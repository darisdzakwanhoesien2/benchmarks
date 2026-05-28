from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import uuid

import pandas as pd
import streamlit as st


st.set_page_config(page_title="ClimateBERT Multi-Model Runner", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
JOBS = RESULTS / "climatebert_background_jobs"
ROOT_MODELS_DIR = ROOT.parent.parent / "model_download"

sys.path.insert(0, str(ROOT))
from climatebert_background_worker import read_json as _read_json  # noqa: E402


DEFAULT_SILVER_PATH = RESULTS / "revision_analysis" / "silver_tone_ground_truth.csv"
DEFAULT_GLOBAL_IMPORTED = RESULTS / "revision_analysis" / "climatebert_record_batch_import.csv"
FALLBACK_SILVER_PATH = ROOT / "data" / "data" / "data_output.txt"
FALLBACK_GLOBAL_IMPORTED = ROOT / "data" / "data" / "climatebert_record_batch_import.csv"

SILVER_PATH = DEFAULT_SILVER_PATH if DEFAULT_SILVER_PATH.exists() else FALLBACK_SILVER_PATH
GLOBAL_IMPORTED = DEFAULT_GLOBAL_IMPORTED if DEFAULT_GLOBAL_IMPORTED.exists() else FALLBACK_GLOBAL_IMPORTED


def utc_now_id() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def list_local_model_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    # Heuristic: treat any directory with config.json as a model folder.
    candidates = []
    for path in root.rglob("config.json"):
        if path.is_file():
            candidates.append(path.parent)
    # Also include top-level folders (some models may not have config.json in this export).
    for child in root.iterdir() if root.exists() else []:
        if child.is_dir() and child not in candidates:
            candidates.append(child)
    uniq = sorted({p.resolve() for p in candidates})
    return uniq


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        if path.suffix.lower() == ".txt":
            return pd.read_csv(path, sep="\t", engine="python").fillna("")
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def processed_ids_for_model(imported_df: pd.DataFrame, model_id: str) -> set[str]:
    if imported_df.empty or "record_id" not in imported_df.columns:
        return set()
    view = imported_df.copy()
    if "climatebert_model" in view.columns:
        view = view[view["climatebert_model"].astype(str).eq(str(model_id))]
    # Treat as processed if a label exists or an error exists.
    processed = set()
    label_series = view.get("climatebert_label", pd.Series(dtype=str)).astype(str).str.strip()
    error_series = view.get("climatebert_error", pd.Series(dtype=str)).astype(str).str.strip()
    ok_mask = label_series.ne("") | error_series.ne("")
    processed.update(view.loc[ok_mask, "record_id"].astype(str))
    return processed


def processed_ids_for_model_across_jobs(model_id: str, job_root: Path, base_imported: pd.DataFrame) -> set[str]:
    """
    Resume helper: considers both the global imported CSV and any per-job imported outputs.
    """
    processed = set(processed_ids_for_model(base_imported, model_id))
    for job_dir in job_root.iterdir() if job_root.exists() else []:
        if not job_dir.is_dir():
            continue
        job_file = job_dir / "climatebert_record_batch_import.csv"
        df = load_csv(job_file)
        if df.empty:
            continue
        processed |= processed_ids_for_model(df, model_id)
    return processed


def start_job(
    *,
    model_id: str,
    backend: str,
    local_model_path: str,
    record_ids: list[str],
    limit: int,
    max_chars: int,
    skip_existing: bool,
    dry_run: bool,
) -> str:
    job_id = f"climatebert_multi_{utc_now_id()}_{uuid.uuid4().hex[:6]}"
    job_dir = JOBS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "model_backend": backend,
        "model_id": model_id,
        "local_model_path": local_model_path,
        "record_col": "record_id",
        "text_col": "text",
        "record_ids": record_ids,
        "limit": limit,
        "max_chars": max_chars,
        "skip_existing": skip_existing,
        # IMPORTANT: skip_existing should not skip records from other models. Default True in worker.
        "skip_existing_global": True,
        "dry_run": dry_run,
        # per-job outputs to avoid concurrency races
        "script_output_path": str(job_dir / "climatebert_output.csv"),
        "imported_output_path": str(job_dir / "climatebert_record_batch_import.csv"),
    }
    (job_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (job_dir / "control.json").write_text(json.dumps({"stop_requested": False}, indent=2), encoding="utf-8")

    out_log = job_dir / "worker.out.log"
    err_log = job_dir / "worker.err.log"
    cmd = [
        "python3",
        str(ROOT / "climatebert_background_worker.py"),
        job_id,
    ]
    # Use Popen instead of nohup to get immediate feedback and a PID for debugging.
    out_log.parent.mkdir(parents=True, exist_ok=True)
    out_fh = out_log.open("ab")
    err_fh = err_log.open("ab")
    proc = subprocess.Popen(cmd, stdout=out_fh, stderr=err_fh, start_new_session=True)
    (job_dir / "pid.txt").write_text(str(proc.pid) + "\n", encoding="utf-8")
    return job_id


def merge_job_imports_into_global(job_ids: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for job_id in job_ids:
        job_path = JOBS / job_id / "climatebert_record_batch_import.csv"
        df = load_csv(job_path)
        if not df.empty:
            frames.append(df)
    if not frames:
        return load_csv(GLOBAL_IMPORTED)
    merged = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    if GLOBAL_IMPORTED.exists():
        base = load_csv(GLOBAL_IMPORTED)
        if not base.empty:
            merged = pd.concat([base, merged], ignore_index=True, sort=False).fillna("")
    # De-duplicate on (record_id, climatebert_model) keeping last
    if {"record_id", "climatebert_model"}.issubset(merged.columns):
        merged["_k"] = merged["record_id"].astype(str) + "||" + merged["climatebert_model"].astype(str)
        merged = merged.drop_duplicates("_k", keep="last").drop(columns=["_k"])
    merged.to_csv(GLOBAL_IMPORTED, index=False)
    return merged


def load_all_job_imports(job_root: Path, limit_jobs: int = 200) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not job_root.exists():
        return pd.DataFrame()
    job_dirs = sorted([p for p in job_root.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)[:limit_jobs]
    for job_dir in job_dirs:
        df = load_csv(job_dir / "climatebert_record_batch_import.csv")
        if df.empty:
            continue
        df = df.copy()
        df["__job_id"] = job_dir.name
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False).fillna("")


def per_model_result_summary(
    *,
    silver_df: pd.DataFrame,
    global_imported_df: pd.DataFrame,
    job_imports_df: pd.DataFrame,
    models: list[str],
) -> pd.DataFrame:
    all_ids = set(silver_df["record_id"].astype(str)) if not silver_df.empty and "record_id" in silver_df.columns else set()
    rows: list[dict[str, object]] = []
    for model_id in models:
        global_done = processed_ids_for_model(global_imported_df, model_id)
        job_done = processed_ids_for_model(job_imports_df, model_id) if not job_imports_df.empty else set()
        combined = set(global_done) | set(job_done)
        rows.append(
            {
                "model": model_id,
                "processed_global": len(global_done),
                "processed_jobs": len(job_done),
                "processed_total": len(combined),
                "missing": max(len(all_ids) - len(combined), 0),
            }
        )
    return pd.DataFrame(rows).sort_values(["missing", "processed_total"], ascending=[False, True]).fillna(0)


st.title("ClimateBERT Multi-Model Runner")
st.caption("Select existing local models, run the same dataset across them in parallel, resume missing rows, and merge results.")
st.caption(f"Dataset: `{SILVER_PATH}`")
st.caption(f"Global imported: `{GLOBAL_IMPORTED}`")

JOBS.mkdir(parents=True, exist_ok=True)

if not SILVER_PATH.exists():
    st.error(f"Missing input: `{SILVER_PATH}`")
    st.stop()

silver = load_csv(SILVER_PATH)
global_imported = load_csv(GLOBAL_IMPORTED)
job_imports = load_all_job_imports(JOBS)

# Normalize input schema so this page can run against either the revision-analysis
# "silver" dataset or the existing parsed data output used elsewhere in the app.
if not silver.empty:
    if "record_id" not in silver.columns:
        silver = silver.reset_index(drop=False).rename(columns={"index": "record_id"})
    silver["record_id"] = silver["record_id"].astype(str)
    if "text" not in silver.columns:
        if "sentence" in silver.columns:
            silver["text"] = silver["sentence"].astype(str)
        else:
            silver["text"] = ""
local_models = list_local_model_dirs(ROOT_MODELS_DIR)
model_choices = [str(p.relative_to(ROOT_MODELS_DIR)) for p in local_models] if local_models else []

left, right = st.columns([1.05, 1], gap="large")
with left:
    st.subheader("1) Choose models")
    if not model_choices:
        st.warning(f"No local model folders found under `{ROOT_MODELS_DIR}`.")
    selected = st.multiselect("Local models to run (text-classification)", model_choices, default=model_choices[:2])

    st.subheader("2) Choose dataset rows")
    mode = st.radio(
        "Row selection",
        ["All rows", "Resume missing per model"],
        horizontal=True,
        help="Resume mode runs only record_ids that are not present yet for each selected model.",
    )
    limit = st.number_input("Limit rows (0 = all)", min_value=0, max_value=max(1, len(silver)), value=0, step=50)
    max_chars = st.number_input("Max chars per text", min_value=256, max_value=4000, value=1200, step=128)
    dry_run = st.checkbox("Dry run (no model inference)", value=False)
    skip_existing = st.checkbox("Skip existing IDs inside each job output", value=True)
    parallel_jobs = st.number_input("Max parallel jobs to start now", min_value=1, max_value=12, value=4, step=1)

    if st.button("Start runs", type="primary", use_container_width=True, disabled=not selected):
        record_ids_all = silver["record_id"].astype(str).tolist() if "record_id" in silver.columns else []
        if not record_ids_all:
            st.error("No `record_id` column found in silver input; cannot start runs.")
            st.stop()
        started: list[str] = []
        errors: list[str] = []
        for idx, model_rel in enumerate(selected):
            if idx >= int(parallel_jobs):
                break
            try:
                model_id = model_rel
                local_path = str((ROOT_MODELS_DIR / model_rel).resolve())
                record_ids = record_ids_all
                if mode == "Resume missing per model" and record_ids_all:
                    have = processed_ids_for_model_across_jobs(model_id, JOBS, global_imported)
                    record_ids = [rid for rid in record_ids_all if rid not in have]
                if limit and limit > 0:
                    record_ids = record_ids[: int(limit)]
                if not record_ids:
                    errors.append(f"{model_id}: 0 records to run (resume mode has nothing missing).")
                    continue
                job_id = start_job(
                    model_id=model_id,
                    backend="Local model",
                    local_model_path=local_path,
                    record_ids=record_ids,
                    limit=0,  # record_ids already limited
                    max_chars=int(max_chars),
                    skip_existing=bool(skip_existing),
                    dry_run=bool(dry_run),
                )
                started.append(job_id)
            except Exception as exc:
                errors.append(f"{model_rel}: {exc}")
        if started:
            st.success(f"Started {len(started)} job(s): {', '.join(started)}")
        if errors:
            st.warning("Some jobs were not started:")
            st.code("\n".join(errors), language="text")
        st.rerun()

with right:
    st.subheader("Current progress")
    st.metric("Silver rows", f"{len(silver):,}")
    st.metric("Global imported rows", f"{len(global_imported):,}")
    st.metric("Job imported rows (unmerged)", f"{len(job_imports):,}")
    if not selected:
        st.info("Select one or more models to see per-model missing counts.")
    else:
        st.markdown("**Existing results by model (global + job outputs)**")
        summary = per_model_result_summary(
            silver_df=silver,
            global_imported_df=global_imported,
            job_imports_df=job_imports,
            models=selected,
        )
        st.dataframe(summary, use_container_width=True, hide_index=True, height=240)

st.divider()
st.subheader("Background jobs")

job_dirs = sorted([p for p in JOBS.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
latest = job_dirs[:30]
job_rows = []
for path in latest:
    status = _read_json(path / "status.json", {})
    job_rows.append(
        {
            "job_id": path.name,
            "status": status.get("status", "unknown"),
            "completed": int(status.get("completed") or 0),
            "total": int(status.get("total") or 0),
            "model_id": status.get("model_id") or status.get("model"),
            "updated_at": status.get("updated_at", ""),
            "imported_output_path": status.get("imported_output_path", ""),
        }
    )
jobs_df = pd.DataFrame(job_rows).fillna("")
job_id_options = jobs_df["job_id"].astype(str).tolist() if "job_id" in jobs_df.columns else []
st.dataframe(jobs_df, use_container_width=True, hide_index=True, height=320)

st.divider()
st.subheader("Visualize job outputs (unmerged)")

if job_imports.empty:
    st.info("No per-job imported outputs found yet.")
else:
    st.markdown("### Grouped by model_id (unmerged)")
    if "climatebert_model" not in job_imports.columns:
        st.info("No `climatebert_model` column found in job outputs yet.")
    else:
        all_ids = set(silver["record_id"].astype(str)) if not silver.empty and "record_id" in silver.columns else set()
        group_rows: list[dict[str, object]] = []
        for model_id in sorted(job_imports["climatebert_model"].astype(str).unique().tolist()):
            model_view = job_imports[job_imports["climatebert_model"].astype(str).eq(model_id)].copy()
            processed = processed_ids_for_model(model_view, model_id)
            err_series = model_view.get("climatebert_error", pd.Series(dtype=str)).astype(str).str.strip()
            group_rows.append(
                {
                    "model_id": model_id,
                    "job_rows": len(model_view),
                    "unique_record_ids": int(model_view["record_id"].astype(str).nunique()) if "record_id" in model_view.columns else 0,
                    "processed_record_ids": len(processed),
                    "missing_vs_silver": max(len(all_ids) - len(processed), 0) if all_ids else 0,
                    "error_rows": int(err_series.ne("").sum()) if not err_series.empty else 0,
                    "latest_job_id": max(model_view["__job_id"].astype(str)) if "__job_id" in model_view.columns and len(model_view) else "",
                }
            )
        grouped = pd.DataFrame(group_rows).sort_values(["missing_vs_silver", "processed_record_ids"], ascending=[False, True]).fillna("")
        st.dataframe(grouped, use_container_width=True, hide_index=True, height=260)

        with st.expander("Preview one model_id (unmerged)", expanded=False):
            choice = st.selectbox("model_id", grouped["model_id"].astype(str).tolist(), index=0, key="unmerged_model_preview")
            model_view = job_imports[job_imports["climatebert_model"].astype(str).eq(str(choice))].copy()
            show_cols = [
                c
                for c in [
                    "__job_id",
                    "record_id",
                    "company",
                    "prompt",
                    "model",
                    "tone_pred",
                    "climatebert_model",
                    "climatebert_label",
                    "climatebert_score",
                    "climatebert_error",
                ]
                if c in model_view.columns
            ]
            st.dataframe(model_view[show_cols].head(500).astype(str), use_container_width=True, hide_index=True, height=360)

    st.markdown("### Grouped by job_id (unmerged)")
    job_choices = sorted(job_imports["__job_id"].astype(str).unique().tolist(), reverse=True)
    sel_job = st.selectbox("Job id", job_choices, index=0, key="job_output_selected")
    job_view = job_imports[job_imports["__job_id"].astype(str).eq(str(sel_job))].copy()
    st.caption(f"Rows in selected job: {len(job_view):,}")
    show_cols = [
        c
        for c in [
            "__job_id",
            "record_id",
            "company",
            "prompt",
            "model",
            "tone_pred",
            "climatebert_model",
            "climatebert_label",
            "climatebert_score",
            "climatebert_error",
        ]
        if c in job_view.columns
    ]
    st.dataframe(job_view[show_cols].head(500).astype(str), use_container_width=True, hide_index=True, height=380)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**ClimateBERT label counts**")
        if "climatebert_label" in job_view.columns:
            counts = (
                job_view["climatebert_label"]
                .astype(str)
                .str.strip()
                .replace("", "missing")
                .value_counts()
                .head(20)
            )
            st.dataframe(
                counts.rename_axis("label").reset_index(name="count"),
                use_container_width=True,
                hide_index=True,
                height=320,
            )
        else:
            st.info("No climatebert_label column.")
    with c2:
        st.markdown("**Tone counts (tone_pred)**")
        if "tone_pred" in job_view.columns:
            counts = (
                job_view["tone_pred"]
                .astype(str)
                .str.strip()
                .replace("", "missing")
                .value_counts()
            )
            st.dataframe(
                counts.rename_axis("tone_pred").reset_index(name="count"),
                use_container_width=True,
                hide_index=True,
                height=320,
            )
        else:
            st.info("No tone_pred column.")
    with c3:
        st.markdown("**Errors**")
        if "climatebert_error" in job_view.columns:
            err = job_view["climatebert_error"].astype(str).str.strip()
            err_nonempty = job_view[err.ne("")].copy()
            st.metric("Error rows", f"{len(err_nonempty):,}")
            if not err_nonempty.empty:
                st.dataframe(err_nonempty[show_cols].head(200).astype(str), use_container_width=True, hide_index=True, height=260)
        else:
            st.info("No climatebert_error column.")

st.markdown("### Simplified progress (running only)")
if jobs_df.empty:
    st.info("No jobs found yet.")
else:
    view = jobs_df.copy()
    view["completed"] = pd.to_numeric(view["completed"], errors="coerce").fillna(0)
    view["total"] = pd.to_numeric(view["total"], errors="coerce").fillna(0)
    view["progress_pct"] = view.apply(lambda r: (r["completed"] / r["total"] * 100) if r["total"] else 0.0, axis=1)
    running = view[view["status"].astype(str).isin(["running"])].copy()
    if running.empty:
        st.info("No running jobs right now.")
    else:
        st.dataframe(
            running[["job_id", "model_id", "completed", "total", "progress_pct", "updated_at"]],
            use_container_width=True,
            hide_index=True,
            height=220,
        )

merge_cols = st.columns([2, 1, 1])
with merge_cols[0]:
    merge_selected = st.multiselect("Jobs to merge into global imported file", job_id_options)
with merge_cols[1]:
    if st.button("Merge selected", use_container_width=True, disabled=not merge_selected):
        merged = merge_job_imports_into_global(merge_selected)
        st.success(f"Merged -> `{GLOBAL_IMPORTED}` ({len(merged):,} rows)")
        st.rerun()
with merge_cols[2]:
    if st.button("Refresh", use_container_width=True):
        st.rerun()
