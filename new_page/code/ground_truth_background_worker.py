from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RESULTS_DIR = ROOT / "results"
JOBS_DIR = RESULTS_DIR / "ground_truth_background_jobs"
T1_FILE = RESULTS_DIR / "t1_results.jsonl"
T2_FILE = RESULTS_DIR / "t2_results.jsonl"


try:
    import fcntl
except Exception:
    fcntl = None


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def serialize(obj: Any) -> Any:
    try:
        import numpy as np
        import torch

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, torch.Tensor):
            return obj.detach().cpu().numpy().tolist()
    except Exception:
        pass
    if isinstance(obj, (list, tuple)):
        return [serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


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


def append_jsonl_locked(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            handle.write(json.dumps(serialize(record), ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_event(job_dir: Path, event: str, **payload: Any) -> None:
    append_jsonl_locked(job_dir / "events.jsonl", {"time": utc_now(), "event": event, **payload})


def update_status(job_dir: Path, **updates: Any) -> dict[str, Any]:
    status_path = job_dir / "status.json"
    status = read_json(status_path, {})
    status.update(updates)
    status["updated_at"] = utc_now()
    write_json(status_path, status)
    return status


def load_processed_t1(path: Path = T1_FILE) -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    if not path.exists():
        return done
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            done.add((str(row.get("label", "")), str(row.get("model", ""))))
    return done


def load_processed_t2(path: Path = T2_FILE) -> set[str]:
    done: set[str] = set()
    if not path.exists():
        return done
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            done.add(str(row.get("label", "")))
    return done


def run_t1_item(job_dir: Path, item: dict[str, Any], model: str, backend: str) -> bool:
    if backend != "ClimateBERT API":
        raise RuntimeError(f"Unsupported background T1 backend: {backend}")
    from api.climatebert_client import ClimateBERTClient

    api = ClimateBERTClient()
    try:
        result = api.predict(str(item["text"]), model_key=model)
        success = True
        error = None
    except Exception as exc:
        result = {"error": str(exc)}
        success = False
        error = str(exc)

    append_jsonl_locked(
        T1_FILE,
        {
            "timestamp": datetime.utcnow().isoformat(),
            "label": item["label"],
            "model": model,
            "text": item["text"],
            "result": result,
            "success": success,
            "error": error,
            "backend": backend,
            "background_job_id": job_dir.name,
        },
    )
    return success


def run_t2_item(item: dict[str, Any]) -> tuple[bool, str | None]:
    from code.rule_based import collect_aspects, polarity_basic, tone_basic
    from code.hybrid_model import run_hierarchical_hybrid

    text = str(item["text"])
    rule_based = {
        "aspects": collect_aspects(text),
        "polarity": polarity_basic(text),
        "tone": tone_basic(text),
    }
    try:
        _, df, _, _, _, metrics = run_hierarchical_hybrid(text)
        hybrid = {
            "predictions": df.to_dict("records"),
            "metrics": metrics.to_dict("records"),
        }
        success = True
        error = None
    except Exception as exc:
        hybrid = {"error": str(exc)}
        success = False
        error = str(exc)

    append_jsonl_locked(
        T2_FILE,
        {
            "timestamp": datetime.utcnow().isoformat(),
            "label": item["label"],
            "text": text,
            "rule_based": rule_based,
            "hybrid": hybrid,
            "background_job_id": item.get("background_job_id"),
        },
    )
    return success, error


def main(job_id: str) -> int:
    job_dir = JOBS_DIR / job_id
    config = read_json(job_dir / "config.json", {})
    if not config:
        raise RuntimeError(f"Missing config for {job_id}")

    items = [item for item in config.get("items", []) if isinstance(item, dict) and item.get("label") and item.get("text")]
    run_t1 = bool(config.get("run_t1"))
    run_t2 = bool(config.get("run_t2"))
    models = [str(model).strip() for model in config.get("models", []) if str(model).strip()]
    backend = str(config.get("t1_backend") or "ClimateBERT API")

    total = (len(items) * len(models) if run_t1 else 0) + (len(items) if run_t2 else 0)
    update_status(
        job_dir,
        job_id=job_id,
        pid=os.getpid(),
        status="running",
        total=total,
        completed=0,
        failed=0,
        skipped=0,
        started_at=read_json(job_dir / "status.json", {}).get("started_at") or utc_now(),
    )
    append_event(job_dir, "started", total=total, items=len(items), pid=os.getpid())

    completed = 0
    failed = 0
    skipped = 0
    processed_t1 = load_processed_t1()
    processed_t2 = load_processed_t2()

    for item in items:
        item = dict(item)
        item["background_job_id"] = job_id
        label = str(item["label"])

        if run_t1:
            for model in models:
                current = f"T1 {label} x {model}"
                update_status(job_dir, current=current)
                if (label, model) in processed_t1:
                    skipped += 1
                    completed += 1
                    update_status(job_dir, completed=completed, skipped=skipped, current=f"Skipped existing {current}")
                    append_event(job_dir, "skipped_t1", label=label, model=model)
                    continue
                ok = run_t1_item(job_dir, item, model, backend)
                completed += 1
                if ok:
                    processed_t1.add((label, model))
                    append_event(job_dir, "completed_t1", label=label, model=model)
                else:
                    failed += 1
                    append_event(job_dir, "failed_t1", label=label, model=model)
                update_status(job_dir, completed=completed, failed=failed, skipped=skipped)

        if run_t2:
            current = f"T2 {label}"
            update_status(job_dir, current=current)
            if label in processed_t2:
                skipped += 1
                completed += 1
                update_status(job_dir, completed=completed, skipped=skipped, current=f"Skipped existing {current}")
                append_event(job_dir, "skipped_t2", label=label)
                continue
            ok, error = run_t2_item(item)
            completed += 1
            if ok:
                processed_t2.add(label)
                append_event(job_dir, "completed_t2", label=label)
            else:
                failed += 1
                append_event(job_dir, "failed_t2", label=label, error=error)
            update_status(job_dir, completed=completed, failed=failed, skipped=skipped)

    update_status(job_dir, status="completed", current="All queued items completed", finished_at=utc_now())
    append_event(job_dir, "completed_job", completed=completed, failed=failed, skipped=skipped)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ground_truth_background_worker.py <job_id>", file=sys.stderr)
        raise SystemExit(2)
    job_id_arg = sys.argv[1]
    try:
        raise SystemExit(main(job_id_arg))
    except Exception as exc:
        job_dir_arg = JOBS_DIR / job_id_arg
        update_status(job_dir_arg, status="failed", error=str(exc), finished_at=utc_now())
        append_event(job_dir_arg, "worker_crashed", error=str(exc))
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
