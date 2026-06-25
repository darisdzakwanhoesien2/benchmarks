from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import uuid

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="ClimateBERT Multi-Model Runner", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REV = RESULTS / "revision_analysis"
JOBS = RESULTS / "climatebert_background_jobs"
ROOT_MODELS_DIR = ROOT.parent / "model_download" / "models"
CLIMATEBERT_LOGIC_DIR = RESULTS / "fine_tuning"

sys.path.insert(0, str(ROOT / "code"))
from climatebert_background_worker import read_json as _read_json  # noqa: E402


SILVER_PATH = REV / "silver_tone_ground_truth.csv"
GLOBAL_IMPORTED = REV / "climatebert_record_batch_import.csv"


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
        str(ROOT / "code" / "climatebert_background_worker.py"),
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


def normalize_result_view(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    view = df.copy().fillna("")
    if "__job_id" not in view.columns and "climatebert_job_id" in view.columns:
        view["__job_id"] = view["climatebert_job_id"].astype(str)
    if "__source" not in view.columns:
        view["__source"] = "results"
    return view


def summarize_grouped(view: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    cols = [c for c in group_cols if c in view.columns]
    if view.empty or not cols:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    for keys, grp in view.groupby(cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {col: key for col, key in zip(cols, keys)}
        err = grp.get("climatebert_error", pd.Series(dtype=str)).astype(str).str.strip()
        row.update(
            {
                "rows": len(grp),
                "record_ids": int(grp["record_id"].astype(str).nunique()) if "record_id" in grp.columns else 0,
                "companies": int(grp["company"].astype(str).nunique()) if "company" in grp.columns else 0,
                "prompts": int(grp["prompt"].astype(str).nunique()) if "prompt" in grp.columns else 0,
                "models": int(grp["model"].astype(str).nunique()) if "model" in grp.columns else 0,
                "labels": int(grp["climatebert_label"].astype(str).nunique()) if "climatebert_label" in grp.columns else 0,
                "errors": int(err.ne("").sum()),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["rows"], ascending=False).fillna("")


def counts_for_chart(view: pd.DataFrame, field: str) -> pd.DataFrame:
    if view.empty or field not in view.columns:
        return pd.DataFrame(columns=[field, "count"])
    return (
        view[field]
        .astype(str)
        .replace("", "missing")
        .value_counts()
        .rename_axis(field)
        .reset_index(name="count")
    )


def describe_explorer(group_by: list[str], chart_field: str) -> str:
    parts: list[str] = []
    if "company" in group_by and "prompt" in group_by:
        parts.append("Compare how the same company behaves under different prompts.")
    elif "company" in group_by:
        parts.append("See which companies produce the most rows, labels, or errors.")
    if "prompt" in group_by:
        parts.append("Check whether prompt wording changes the label mix or error rate.")
    if "model" in group_by or "climatebert_model" in group_by:
        parts.append("Compare model-level agreement, label distribution, and failure patterns.")
    if "climatebert_label" in group_by:
        parts.append("Inspect which predicted labels dominate each slice.")
    if "chart_field" in group_by:
        parts.append("Use the chart to spot long tails or concentrated categories.")
    if chart_field == "company":
        parts.append("The chart highlights the most active companies.")
    elif chart_field == "prompt":
        parts.append("The chart shows which prompt variants dominate the selected rows.")
    elif chart_field in {"model", "climatebert_model"}:
        parts.append("The chart compares outputs across models.")
    elif chart_field == "climatebert_label":
        parts.append("The chart shows the label distribution across the selected subset.")
    return " ".join(parts) or "Group rows to compare counts, labels, and errors across any slice of the results."


st.title("ClimateBERT Multi-Model Runner")
st.caption("Select existing local models, run the same dataset across them in parallel, resume missing rows, and merge results.")

if not SILVER_PATH.exists():
    st.error(f"Missing input: `{SILVER_PATH}`")
    st.stop()

silver = load_csv(SILVER_PATH)
global_imported = load_csv(GLOBAL_IMPORTED)
job_imports = load_all_job_imports(JOBS)

JOBS.mkdir(parents=True, exist_ok=True)
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

st.divider()
st.subheader("Interactive results explorer")

source = st.radio(
    "Source",
    ["Merged results", "All job outputs", "Selected job"],
    horizontal=True,
    key="results_source",
)

if source == "Merged results":
    explorer = global_imported.copy()
elif source == "Selected job":
    if job_imports.empty or "__job_id" not in job_imports.columns:
        explorer = pd.DataFrame()
    else:
        job_ids = sorted(job_imports["__job_id"].astype(str).unique().tolist(), reverse=True)
        selected_job = st.selectbox("Job", job_ids, index=0, key="results_job")
        explorer = job_imports[job_imports["__job_id"].astype(str).eq(str(selected_job))].copy()
else:
    explorer = job_imports.copy()

explorer = normalize_result_view(explorer)

if explorer.empty:
    st.info("No rows available for the selected source.")
else:
    with st.expander("Filters", expanded=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            company_vals = sorted(explorer["company"].astype(str).replace("", "missing").unique().tolist()) if "company" in explorer.columns else []
            selected_companies = st.multiselect("Company", company_vals, default=company_vals, key="filter_company")
        with f2:
            prompt_vals = sorted(explorer["prompt"].astype(str).replace("", "missing").unique().tolist()) if "prompt" in explorer.columns else []
            selected_prompts = st.multiselect("Prompt", prompt_vals, default=prompt_vals, key="filter_prompt")
        with f3:
            model_vals = sorted(explorer["climatebert_model"].astype(str).replace("", "missing").unique().tolist()) if "climatebert_model" in explorer.columns else []
            selected_models = st.multiselect("ClimateBERT model", model_vals, default=model_vals, key="filter_model")

        if selected_companies and "company" in explorer.columns:
            explorer = explorer[explorer["company"].astype(str).replace("", "missing").isin(selected_companies)]
        if selected_prompts and "prompt" in explorer.columns:
            explorer = explorer[explorer["prompt"].astype(str).replace("", "missing").isin(selected_prompts)]
        if selected_models and "climatebert_model" in explorer.columns:
            explorer = explorer[explorer["climatebert_model"].astype(str).replace("", "missing").isin(selected_models)]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{len(explorer):,}")
    m2.metric("Record IDs", f"{explorer['record_id'].astype(str).nunique():,}" if "record_id" in explorer.columns else "0")
    m3.metric("Companies", f"{explorer['company'].astype(str).nunique():,}" if "company" in explorer.columns else "0")
    m4.metric("Errors", f"{explorer.get('climatebert_error', pd.Series(dtype=str)).astype(str).str.strip().ne('').sum():,}")

    group_options = [c for c in ["company", "prompt", "model", "climatebert_model", "climatebert_label", "__job_id", "__source"] if c in explorer.columns]
    default_group = [c for c in ["company", "prompt", "model"] if c in group_options]
    group_by = st.multiselect("Group by", group_options, default=default_group, key="group_by")
    sort_col = st.selectbox("Sort summary by", ["rows", "record_ids", "companies", "prompts", "models", "labels", "errors"], index=0, key="sort_summary")

    chart_field = st.selectbox(
        "Chart field",
        [c for c in ["company", "prompt", "model", "climatebert_model", "climatebert_label", "__job_id"] if c in explorer.columns],
        index=0 if "company" in explorer.columns else 0,
        key="chart_field",
    )
    st.info(describe_explorer(group_by, chart_field))

    summary = summarize_grouped(explorer, group_by)
    if not summary.empty:
        st.dataframe(summary.sort_values(sort_col, ascending=False), use_container_width=True, hide_index=True, height=320)
    else:
        st.info("Choose one or more grouping columns.")

    chart_df = counts_for_chart(explorer, chart_field)
    if not chart_df.empty:
        chart = (
            alt.Chart(chart_df)
            .mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3)
            .encode(
                x=alt.X("count:Q", title="Count"),
                y=alt.Y(f"{chart_field}:N", sort="-x", title=None),
                tooltip=[alt.Tooltip(f"{chart_field}:N"), alt.Tooltip("count:Q")],
                color=alt.value("#2f6f73"),
            )
            .properties(height=min(420, max(240, 18 * len(chart_df))))
        )
        st.altair_chart(chart, use_container_width=True)

    preview_cols = [c for c in ["record_id", "company", "prompt", "model", "tone_pred", "climatebert_model", "climatebert_label", "climatebert_score", "climatebert_error", "__job_id"] if c in explorer.columns]
    st.dataframe(explorer[preview_cols].astype(str).head(500), use_container_width=True, hide_index=True, height=420)

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
    merge_selected = st.multiselect("Jobs to merge into global imported file", jobs_df["job_id"].astype(str).tolist())
with merge_cols[1]:
    if st.button("Merge selected", use_container_width=True, disabled=not merge_selected):
        merged = merge_job_imports_into_global(merge_selected)
        st.success(f"Merged -> `{GLOBAL_IMPORTED}` ({len(merged):,} rows)")
        st.rerun()
with merge_cols[2]:
    if st.button("Refresh", use_container_width=True):
        st.rerun()

st.divider()
st.subheader("ClimateBERT Logic API by Source Model")
st.caption("Integrates `fine_tuning/call_climatebert_logic.py` and visualizes API behavior across original extraction models.")

CLIMATEBERT_LOGIC_DIR.mkdir(parents=True, exist_ok=True)

api_cols = st.columns([1.1, 1, 1.2])
with api_cols[0]:
    logic_limit = st.number_input("API sample limit", min_value=1, max_value=5000, value=300, step=50, key="logic_limit")
with api_cols[1]:
    logic_sleep = st.number_input("API sleep (sec)", min_value=0.0, max_value=2.0, value=0.05, step=0.05, key="logic_sleep")
with api_cols[2]:
    logic_api_key = st.text_input("x-api-key (optional)", value="", type="password", key="logic_api_key")

default_logic_out = f"climatebert_logic_{utc_now_id()}.csv"
logic_out_name = st.text_input("Output file name", value=default_logic_out, key="logic_out_name")

if st.button("Run ClimateBERT Logic from Ground Truth", key="run_climatebert_logic"):
    out_path = CLIMATEBERT_LOGIC_DIR / logic_out_name
    cmd = [
        "python3",
        str(ROOT / "fine_tuning" / "call_climatebert_logic.py"),
        "--input",
        str(REV / "pilot_ground_truth_annotations.csv"),
        "--output",
        str(out_path),
        "--limit",
        str(int(logic_limit)),
        "--sleep",
        str(float(logic_sleep)),
    ]
    if logic_api_key.strip():
        cmd += ["--api-key", logic_api_key.strip()]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            st.success(f"Run complete: `{out_path}`")
        else:
            st.error("ClimateBERT logic run failed.")
            st.code(proc.stderr or proc.stdout, language="text")
    except Exception as exc:
        st.error(f"Failed to run script: {exc}")
    st.rerun()

logic_files = sorted(CLIMATEBERT_LOGIC_DIR.glob("*climatebert_logic*.csv"))
if not logic_files:
    st.info("No logic outputs found yet. Run the API block above to generate one.")
else:
    rel_options = [str(p.relative_to(ROOT)) for p in logic_files]
    selected_logic = st.selectbox("Logic output file", rel_options, index=len(rel_options) - 1, key="logic_file")
    logic_df = load_csv(ROOT / selected_logic)

    if logic_df.empty:
        st.warning("Selected file is empty.")
    else:
        def _extract_from_api_response(raw: str) -> dict:
            try:
                return json.loads(str(raw)) if str(raw).strip() else {}
            except Exception:
                return {}

        parsed = logic_df.get("api_response", pd.Series(dtype=str)).astype(str).apply(_extract_from_api_response)
        logic_df = logic_df.copy()
        logic_df["api_label"] = parsed.apply(
            lambda d: d.get("label")
            or d.get("prediction")
            or d.get("predicted_label")
            or d.get("class")
            or d.get("result")
            or ""
        )
        logic_df["api_climate_sentiment"] = parsed.apply(lambda d: str(d.get("climate_sentiment", "")).strip().lower())
        logic_df["api_error_flag"] = logic_df.get("api_error", pd.Series(dtype=str)).astype(str).str.strip().ne("")
        logic_df["source_model"] = logic_df.get("model", pd.Series(dtype=str)).astype(str).replace("", "missing_model")
        logic_df["sentiment"] = logic_df.get("sentiment", pd.Series(dtype=str)).astype(str).str.strip().str.lower()
        logic_df["sentiment_match"] = logic_df["api_climate_sentiment"].eq(logic_df["sentiment"]) & logic_df["api_climate_sentiment"].ne("")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{len(logic_df):,}")
        m2.metric("Source models", f"{logic_df['source_model'].nunique():,}")
        m3.metric("API errors", f"{int(logic_df['api_error_flag'].sum()):,}")
        m4.metric("Sentiment match", f"{logic_df['sentiment_match'].mean() * 100:.1f}%")

        per_model = (
            logic_df.groupby("source_model", dropna=False)
            .agg(
                rows=("record_id", "count"),
                api_errors=("api_error_flag", "sum"),
                sentiment_match_rate=("sentiment_match", "mean"),
                distinct_api_labels=("api_label", lambda s: s.astype(str).replace("", "missing").nunique()),
            )
            .reset_index()
        )
        per_model["sentiment_match_rate"] = per_model["sentiment_match_rate"] * 100.0

        st.markdown("**Per-source-model summary**")
        st.dataframe(per_model.sort_values("rows", ascending=False), use_container_width=True, hide_index=True, height=280)

        chart = (
            alt.Chart(per_model)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("rows:Q", title="Rows"),
                y=alt.Y("source_model:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("source_model:N", title="Source model"),
                    alt.Tooltip("rows:Q"),
                    alt.Tooltip("api_errors:Q"),
                    alt.Tooltip("sentiment_match_rate:Q", format=".2f"),
                ],
                color=alt.value("#355070"),
            )
            .properties(height=min(420, max(220, 28 * len(per_model))))
        )
        st.altair_chart(chart, use_container_width=True)

        label_dist = (
            logic_df.assign(api_label=logic_df["api_label"].astype(str).replace("", "missing"))
            .groupby(["source_model", "api_label"], dropna=False)
            .size()
            .reset_index(name="count")
            .sort_values(["source_model", "count"], ascending=[True, False])
        )
        st.markdown("**API label distribution by source model**")
        st.dataframe(label_dist, use_container_width=True, hide_index=True, height=320)

        preview_cols = [c for c in ["record_id", "company", "source_model", "prompt", "sentiment", "api_climate_sentiment", "sentiment_match", "api_label", "api_error"] if c in logic_df.columns]
        st.markdown("**Preview**")
        st.dataframe(logic_df[preview_cols].head(500), use_container_width=True, hide_index=True, height=360)
