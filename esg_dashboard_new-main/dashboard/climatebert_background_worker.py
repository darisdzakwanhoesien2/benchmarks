from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

import pandas as pd

from services.inference import run_inference
from utils.data_loader import format_display_value, load_and_parse


def read_json(path: str | Path, default):
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: str | Path, data) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stop_requested(job_dir: Path) -> bool:
    control = read_json(job_dir / "control.json", {})
    return bool(control.get("stop_requested", False))


def normalize_prediction(outputs) -> tuple[str, float | None, str]:
    if outputs is None:
        return "", None, ""
    if isinstance(outputs, dict):
        outputs = [outputs]
    if isinstance(outputs, list) and len(outputs) == 1 and isinstance(outputs[0], list):
        outputs = outputs[0]
    if not isinstance(outputs, list):
        return "", None, json.dumps(outputs, ensure_ascii=False)

    scored = [
        item for item in outputs
        if isinstance(item, dict) and "label" in item and "score" in item
    ]
    if not scored:
        return "", None, json.dumps(outputs, ensure_ascii=False)
    best = max(scored, key=lambda item: float(item.get("score") or 0.0))
    label = format_display_value(best.get("label"))
    score = None
    try:
        score = float(best.get("score") or 0.0)
    except Exception:
        score = None
    return label, score, json.dumps(scored, ensure_ascii=False)


def load_dataset(record_col: str, text_col: str, record_ids: list[str] | None) -> pd.DataFrame:
    df = load_and_parse()
    if record_col not in df.columns:
        df = df.reset_index(drop=False).rename(columns={"index": record_col})
    if text_col not in df.columns and "sentence" in df.columns:
        df[text_col] = df["sentence"]
    df[record_col] = df[record_col].astype(str)
    if record_ids:
        want = set(str(x) for x in record_ids)
        df = df[df[record_col].astype(str).isin(want)].copy()
    return df.reset_index(drop=True)


def ensure_imported_schema(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    for col in ["record_id", "text", "climatebert_model", "climatebert_label", "climatebert_score", "climatebert_error"]:
        if col not in df.columns:
            df[col] = ""
    return df


def append_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    df.to_csv(path, mode="a", header=write_header, index=False)


def run_job(job_id: str) -> int:
    project_root = Path(__file__).resolve().parents[0]
    results_root = project_root / "results" / "climatebert_background_jobs"
    job_dir = results_root / job_id
    config = read_json(job_dir / "config.json", {})

    model_id = str(config.get("model_id") or "")
    model_backend = str(config.get("model_backend") or "Local model")
    local_model_path = str(config.get("local_model_path") or "")
    record_col = str(config.get("record_col") or "record_id")
    text_col = str(config.get("text_col") or "text")
    record_ids = config.get("record_ids") or []
    limit = int(config.get("limit") or 0)
    max_chars = int(config.get("max_chars") or 1200)
    skip_existing = bool(config.get("skip_existing", True))
    skip_existing_global = bool(config.get("skip_existing_global", True))
    dry_run = bool(config.get("dry_run", False))

    script_output_path = Path(str(config.get("script_output_path") or (job_dir / "climatebert_output.csv")))
    imported_output_path = Path(str(config.get("imported_output_path") or (job_dir / "climatebert_record_batch_import.csv")))

    imported_df = pd.DataFrame()
    if skip_existing and imported_output_path.exists():
        try:
            imported_df = pd.read_csv(imported_output_path).fillna("")
        except Exception:
            imported_df = pd.DataFrame()

    already_done: set[str] = set()
    if skip_existing and not imported_df.empty and record_col in imported_df.columns:
        view = imported_df.copy()
        if skip_existing_global and "climatebert_model" in view.columns:
            view = view[view["climatebert_model"].astype(str).eq(model_id)]
        label_series = view.get("climatebert_label", pd.Series(dtype=str)).astype(str).str.strip()
        error_series = view.get("climatebert_error", pd.Series(dtype=str)).astype(str).str.strip()
        ok_mask = label_series.ne("") | error_series.ne("")
        already_done = set(view.loc[ok_mask, record_col].astype(str))

    status = {
        "status": "starting",
        "job_id": job_id,
        "model_id": model_id,
        "model_backend": model_backend,
        "imported_output_path": str(imported_output_path),
        "script_output_path": str(script_output_path),
        "total": 0,
        "completed": 0,
        "updated_at": utc_now_iso(),
    }
    write_json(job_dir / "status.json", status)

    base_df = load_dataset(record_col, text_col, record_ids)
    if limit and limit > 0:
        base_df = base_df.head(limit).copy()

    total = int(len(base_df))
    status.update({"status": "running", "total": total, "updated_at": utc_now_iso()})
    write_json(job_dir / "status.json", status)

    clf = None
    if not dry_run:
        from transformers import pipeline

        clf = pipeline(
            task="text-classification",
            model=local_model_path,
            tokenizer=local_model_path,
            top_k=None,
            truncation=True,
        )

    completed = 0
    for _, row in base_df.iterrows():
        if stop_requested(job_dir):
            status.update({"status": "stopped", "completed": completed, "updated_at": utc_now_iso()})
            write_json(job_dir / "status.json", status)
            return 0

        record_id = format_display_value(row.get(record_col))
        if skip_existing and record_id in already_done:
            completed += 1
            status.update({"completed": completed, "updated_at": utc_now_iso()})
            write_json(job_dir / "status.json", status)
            continue

        text = format_display_value(row.get(text_col))
        if max_chars and isinstance(text, str) and len(text) > max_chars:
            text = text[:max_chars]

        label = ""
        score = None
        err = ""
        raw = ""
        if not dry_run:
            outputs, err = run_inference(clf, text)
            if not err:
                label, score, raw = normalize_prediction(outputs)

        result_row = pd.DataFrame([{
            "record_id": record_id,
            "text": text,
            "climatebert_model": model_id,
            "climatebert_label": label,
            "climatebert_score": score if score is not None else "",
            "climatebert_error": err or "",
            "raw_prediction": raw,
        }])
        append_csv(result_row, script_output_path)
        append_csv(ensure_imported_schema(result_row.drop(columns=["raw_prediction"])), imported_output_path)

        completed += 1
        status.update({"completed": completed, "updated_at": utc_now_iso()})
        write_json(job_dir / "status.json", status)
        time.sleep(0.01)

    status.update({"status": "completed", "completed": completed, "updated_at": utc_now_iso()})
    write_json(job_dir / "status.json", status)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python3 climatebert_background_worker.py <job_id>", file=sys.stderr)
        return 2
    return run_job(argv[1])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

