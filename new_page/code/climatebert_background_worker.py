from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "results" / "revision_analysis"
JOBS_DIR = ROOT / "results" / "climatebert_background_jobs"
SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"
SCRIPT_OUTPUT_PATH = ARTIFACTS / "climatebert_output.csv"
IMPORTED_PATH = ARTIFACTS / "climatebert_record_batch_import.csv"
ROOT_MODELS_DIR = ROOT.parent / "model_download" / "models"


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(data, ensure_ascii=False) + "\n")


def update_status(status_path: Path, **updates: Any) -> dict[str, Any]:
    status = read_json(status_path, {})
    status.update(updates)
    status["updated_at"] = utc_now()
    write_json(status_path, status)
    return status


def is_commitment_label(label: Any) -> bool:
    value = str(label or "").lower().strip()
    return value in {"yes", "true", "1", "commitment", "climate-commitment", "label_1"}


def load_existing_outputs(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def load_pipeline_safe(task: str, local_path: str):
    try:
        from transformers import pipeline

        pipe = pipeline(task, model=local_path, tokenizer=local_path)
        return pipe, None
    except Exception as exc:
        return None, str(exc)


def main(job_id: str) -> int:
    job_dir = JOBS_DIR / job_id
    config = read_json(job_dir / "config.json", {})
    status_path = job_dir / "status.json"
    events_path = job_dir / "events.jsonl"
    control_path = job_dir / "control.json"
    if not config:
        raise RuntimeError(f"Missing config for ClimateBERT job: {job_dir / 'config.json'}")
    if not SILVER_PATH.exists():
        raise RuntimeError(f"Missing input file: {SILVER_PATH}")

    silver = pd.read_csv(SILVER_PATH).fillna("")
    record_col = str(config.get("record_col") or "record_id")
    record_ids = [str(value) for value in config.get("record_ids", []) if str(value).strip()]
    if record_ids and record_col in silver.columns:
        silver = silver[silver[record_col].astype(str).isin(set(record_ids))].copy()
    limit = int(config.get("limit") or 0)
    if limit > 0:
        silver = silver.head(limit)

    model_backend = str(config.get("model_backend") or "Local model")
    model_id = str(config.get("model_id") or "climatebert/distilroberta-base-climate-commitment")
    local_model_path = str(config.get("local_model_path") or "")
    text_col = str(config.get("text_col") or "text")
    max_chars = int(config.get("max_chars") or 1200)
    skip_existing = bool(config.get("skip_existing", True))
    dry_run = bool(config.get("dry_run", False))
    total = len(silver)

    update_status(
        status_path,
        job_id=job_id,
        pid=os.getpid(),
        status="running",
        model_backend=model_backend,
        model_id=model_id,
        total=total,
        completed=0,
        failed=0,
        skipped=0,
        current="Loading model" if not dry_run else "Starting dry run",
        started_at=read_json(status_path, {}).get("started_at") or utc_now(),
    )
    append_jsonl(
        events_path,
        {
            "time": utc_now(),
            "event": "started",
            "model_backend": model_backend,
            "model_id": model_id,
            "local_model_path": local_model_path,
            "total": total,
            "dry_run": dry_run,
        },
    )

    skip_existing_global = bool(config.get("skip_existing_global", True))
    classifier = None
    resolved = Path(model_id)
    if not dry_run:
        if model_backend == "Local model":
            resolved = Path(local_model_path or model_id)
            if not resolved.is_absolute():
                resolved = ROOT_MODELS_DIR / resolved
            classifier, load_error = load_pipeline_safe("text-classification", str(resolved))
            if load_error:
                update_status(status_path, status="failed", current="local model load failed", error=load_error)
                append_jsonl(events_path, {"time": utc_now(), "event": "failed", "error": load_error, "local_model_path": str(resolved)})
                return 1
        else:
            try:
                from transformers import pipeline
            except Exception as exc:
                update_status(status_path, status="failed", current="transformers import failed", error=str(exc))
                append_jsonl(events_path, {"time": utc_now(), "event": "failed", "error": str(exc)})
                return 1
            classifier = pipeline("text-classification", model=model_id)

    # IMPORTANT: multiple background jobs can run in parallel. To avoid output-file races,
    # each job writes its own output files by default, then the UI can merge them.
    job_script_output_path = Path(config.get("script_output_path") or (job_dir / "climatebert_output.csv"))
    job_imported_output_path = Path(config.get("imported_output_path") or (job_dir / "climatebert_record_batch_import.csv"))
    imported_existing = load_existing_outputs(job_imported_output_path)
    script_existing = load_existing_outputs(job_script_output_path)

    existing_ids: set[str] = set()
    if skip_existing and record_col in imported_existing.columns:
        existing_ids.update(imported_existing[record_col].astype(str))

    if skip_existing and skip_existing_global:
        global_existing = load_existing_outputs(IMPORTED_PATH)
        # Default: only skip records already processed for the SAME model_id.
        if not global_existing.empty and {"record_id", "climatebert_model"}.issubset(global_existing.columns):
            same_model = global_existing[global_existing["climatebert_model"].astype(str).eq(model_id)]
            existing_ids.update(same_model["record_id"].astype(str))
    if skip_existing and record_col in script_existing.columns:
        existing_ids.update(script_existing[record_col].astype(str))

    output_rows: list[dict[str, Any]] = imported_existing.to_dict("records") if not imported_existing.empty else []
    script_rows = script_existing.to_dict("records") if not script_existing.empty else []
    completed = 0
    failed = 0
    skipped = 0

    for _, row in silver.iterrows():
        control = read_json(control_path, {})
        if control.get("stop_requested"):
            update_status(status_path, status="stopped", current="Stopped by user", completed=completed, failed=failed, skipped=skipped)
            append_jsonl(events_path, {"time": utc_now(), "event": "stopped"})
            break

        record_id = str(row.get(record_col, ""))
        if skip_existing and record_id in existing_ids:
            skipped += 1
            completed += 1
            update_status(status_path, completed=completed, skipped=skipped, current=f"Skipped {record_id}")
            append_jsonl(events_path, {"time": utc_now(), "event": "skipped", "record_id": record_id})
            continue

        text = str(row.get(text_col, ""))[:max_chars]
        update_status(status_path, current=f"Running {record_id}", completed=completed, failed=failed, skipped=skipped)
        started = time.time()
        try:
            if dry_run:
                label = "commitment" if "commit" in text.lower() or "target" in text.lower() else "not_commitment"
                score = 0.5
            else:
                assert classifier is not None
                result = classifier(text[:512])[0]
                label = result.get("label", "")
                score = result.get("score", 0)

            out = row.to_dict()
            out.update(
                {
                    "climatebert_model": model_id,
                    "climatebert_model_path": str(resolved) if model_backend == "Local model" else "",
                    "climatebert_model_backend": model_backend,
                    "climatebert_label": label,
                    "climatebert_score": round(float(score), 6),
                    "climatebert_commitment_pred": is_commitment_label(label),
                    "climatebert_job_id": job_id,
                    "climatebert_elapsed_sec": round(time.time() - started, 3),
                }
            )
            script_rows.append(
                {
                    "record_id": record_id,
                    "label": label,
                    "score": round(float(score), 6),
                    "climate_commitment": is_commitment_label(label),
                    "climatebert_model": model_id,
                    "climatebert_model_backend": model_backend,
                    "climatebert_job_id": job_id,
                }
            )
            output_rows.append(out)
            completed += 1
            append_jsonl(events_path, {"time": utc_now(), "event": "record_completed", "record_id": record_id, "label": label})
        except Exception as exc:
            failed += 1
            completed += 1
            out = row.to_dict()
            out.update(
                {
                    "climatebert_model": model_id,
                    "climatebert_model_backend": model_backend,
                    "climatebert_label": "",
                    "climatebert_score": "",
                    "climatebert_commitment_pred": "",
                    "climatebert_job_id": job_id,
                    "climatebert_error": str(exc)[:1200],
                }
            )
            output_rows.append(out)
            append_jsonl(events_path, {"time": utc_now(), "event": "record_failed", "record_id": record_id, "error": str(exc)[:1200]})

        pd.DataFrame(script_rows).to_csv(job_script_output_path, index=False)
        pd.DataFrame(output_rows).to_csv(job_imported_output_path, index=False)
        update_status(
            status_path,
            completed=completed,
            failed=failed,
            skipped=skipped,
            script_output_path=str(job_script_output_path),
            imported_output_path=str(job_imported_output_path),
        )

    pd.DataFrame(script_rows).to_csv(job_script_output_path, index=False)
    pd.DataFrame(output_rows).to_csv(job_imported_output_path, index=False)
    final_status = "completed_with_errors" if failed else "completed"
    update_status(
        status_path,
        status=final_status,
        completed=completed,
        failed=failed,
        skipped=skipped,
        current="Finished",
        finished_at=utc_now(),
        script_output_path=str(job_script_output_path),
        imported_output_path=str(job_imported_output_path),
    )
    append_jsonl(events_path, {"time": utc_now(), "event": final_status, "completed": completed, "failed": failed, "skipped": skipped})
    return 0 if not failed else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: climatebert_background_worker.py <job_id>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
