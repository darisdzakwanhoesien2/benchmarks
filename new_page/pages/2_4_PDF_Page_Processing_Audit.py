from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="PDF Page Processing Audit", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data" / "thesis_dataset"
RESULTS_DIR = ROOT / "results"
JOBS_DIR = RESULTS_DIR / "background_llm_jobs"
T3_PATH = RESULTS_DIR / "esg_records.json"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "none", "null"} else text


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def document_pages() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not DATASET_DIR.exists():
        return pd.DataFrame(rows)
    for doc_dir in sorted(path for path in DATASET_DIR.iterdir() if path.is_dir()):
        pages_dir = doc_dir / "pages"
        if not pages_dir.exists():
            continue
        for idx, page_path in enumerate(sorted(pages_dir.glob("*.md")), start=1):
            rows.append(
                {
                    "document": doc_dir.name,
                    "page_name": page_path.name,
                    "page_index": idx,
                    "page_path": str(page_path),
                    "page_chars": len(page_path.read_text(encoding="utf-8", errors="ignore")),
                }
            )
    return pd.DataFrame(rows)


def parse_target_pages(value: Any) -> list[str]:
    text = clean(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r",|\n|\|", text) if part.strip()]


def t3_run_rows() -> pd.DataFrame:
    rows = read_json(T3_PATH, [])
    if not isinstance(rows, list):
        rows = [rows]

    out: list[dict[str, Any]] = []
    for run_idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        target = clean(row.get("target"))
        document = target.split("/")[0] if "/" in target else clean(row.get("document"))
        records = row.get("records") if isinstance(row.get("records"), list) else []
        pages = parse_target_pages(row.get("target_pages"))
        if not pages and target:
            pages = re.findall(r"page[_-]\d+\.md", target)
        for page_name in pages or [""]:
            out.append(
                {
                    "run_idx": run_idx,
                    "document": document,
                    "page_name": page_name,
                    "target": target,
                    "timestamp": clean(row.get("timestamp")),
                    "model": clean(row.get("model")),
                    "prompt": clean(row.get("prompt")),
                    "ok": bool(row.get("ok")),
                    "n_records": len(records),
                    "error": clean(row.get("error")),
                    "error_type": clean(row.get("error_type")),
                    "background_job_id": clean(row.get("background_job_id")),
                    "raw_output": clean(row.get("raw_output")),
                }
            )
    return pd.DataFrame(out)


def t3_record_rows() -> pd.DataFrame:
    rows = read_json(T3_PATH, [])
    if not isinstance(rows, list):
        rows = [rows]

    out: list[dict[str, Any]] = []
    for run_idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        target = clean(row.get("target"))
        document = target.split("/")[0] if "/" in target else clean(row.get("document"))
        pages = parse_target_pages(row.get("target_pages"))
        records = row.get("records") if isinstance(row.get("records"), list) else []
        for record_idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            for page_name in pages or [""]:
                out.append(
                    {
                        "run_idx": run_idx,
                        "record_idx": record_idx,
                        "document": document,
                        "page_name": page_name,
                        "model": clean(row.get("model")),
                        "prompt": clean(row.get("prompt")),
                        "text": clean(record.get("text")),
                        "aspect": clean(record.get("aspect")),
                        "esg": clean(record.get("esg")).upper(),
                        "tone": clean(record.get("tone")).lower(),
                        "sentiment": clean(record.get("sentiment")).lower(),
                        "reasoning": clean(record.get("reasoning")),
                    }
                )
    return pd.DataFrame(out)


def job_rows() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not JOBS_DIR.exists():
        return pd.DataFrame(rows)
    for job_dir in sorted([path for path in JOBS_DIR.iterdir() if path.is_dir()], reverse=True):
        config = read_json(job_dir / "config.json", {})
        status = read_json(job_dir / "status.json", {})
        if not isinstance(config, dict):
            config = {}
        if not isinstance(status, dict):
            status = {}
        document = clean(config.get("document") or status.get("document"))
        page_names = config.get("page_names") if isinstance(config.get("page_names"), list) else []
        prompt_names = config.get("prompt_names") if isinstance(config.get("prompt_names"), list) else []
        models = config.get("models") if isinstance(config.get("models"), list) else []
        for page_name in page_names or [""]:
            rows.append(
                {
                    "job_id": job_dir.name,
                    "document": document,
                    "page_name": clean(page_name),
                    "status": clean(status.get("status", "unknown")),
                    "completed": int(status.get("completed") or 0),
                    "failed": int(status.get("failed") or 0),
                    "total": int(status.get("total") or 0),
                    "backend": clean(config.get("backend")),
                    "models": ", ".join(clean(v) for v in models if clean(v)),
                    "prompts": ", ".join(clean(v) for v in prompt_names if clean(v)) or ("override" if clean(config.get("prompt_override")) else ""),
                    "batch_size": config.get("batch_size", ""),
                    "updated_at": clean(status.get("updated_at")),
                }
            )
    return pd.DataFrame(rows)


def page_audit_df(pages_df: pd.DataFrame, runs_df: pd.DataFrame, jobs_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    run_groups = {}
    job_groups = {}
    if not runs_df.empty:
        for key, grp in runs_df.groupby(["document", "page_name"], dropna=False):
            run_groups[key] = grp
    if not jobs_df.empty:
        for key, grp in jobs_df.groupby(["document", "page_name"], dropna=False):
            job_groups[key] = grp

    for _, page in pages_df.iterrows():
        key = (page["document"], page["page_name"])
        runs = run_groups.get(key, pd.DataFrame())
        jobs = job_groups.get(key, pd.DataFrame())
        ok_runs = int(runs["ok"].sum()) if not runs.empty and "ok" in runs else 0
        failed_runs = int((~runs["ok"]).sum()) if not runs.empty and "ok" in runs else 0
        n_records = int(runs["n_records"].sum()) if not runs.empty and "n_records" in runs else 0
        if ok_runs > 0 and n_records > 0:
            processing_status = "processed_with_output"
        elif ok_runs > 0:
            processing_status = "processed_empty_output"
        elif failed_runs > 0:
            processing_status = "processed_failed"
        elif not jobs.empty:
            running_or_queued = jobs["status"].isin(["queued", "running", "paused"]).any()
            processing_status = "queued_or_running" if running_or_queued else "selected_not_output"
        else:
            processing_status = "not_processed"

        rows.append(
            {
                "document": page["document"],
                "page_name": page["page_name"],
                "page_index": int(page["page_index"]),
                "page_chars": int(page["page_chars"]),
                "processing_status": processing_status,
                "job_count": 0 if jobs.empty else int(jobs["job_id"].nunique()),
                "run_count": 0 if runs.empty else len(runs),
                "ok_runs": ok_runs,
                "failed_runs": failed_runs,
                "output_records": n_records,
                "models": "" if runs.empty else ", ".join(sorted(v for v in runs["model"].map(clean).unique() if v)),
                "prompts": "" if runs.empty else ", ".join(sorted(v for v in runs["prompt"].map(clean).unique() if v)),
                "job_ids": "" if runs.empty else ", ".join(sorted(v for v in runs["background_job_id"].map(clean).unique() if v)),
                "latest_error": "" if runs.empty else clean(runs["error"].map(clean).replace("", pd.NA).dropna().iloc[-1]) if runs["error"].map(clean).replace("", pd.NA).dropna().size else "",
            }
        )
    return pd.DataFrame(rows)


def status_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No page audit rows available.")
        return
    counts = df["processing_status"].value_counts().rename_axis("status").reset_index(name="pages")
    chart = (
        alt.Chart(counts)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("status:N", sort="-y", title=None),
            y=alt.Y("pages:Q", title="Pages"),
            color=alt.Color("status:N", legend=None),
            tooltip=["status", "pages"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


st.title("PDF Page Processing Audit")
st.caption("Page-level checklist showing which OCR/PDF pages were selected, processed, failed, or still missing LLM output.")

pages = document_pages()
runs = t3_run_rows()
records = t3_record_rows()
jobs = job_rows()
audit = page_audit_df(pages, runs, jobs) if not pages.empty else pd.DataFrame()

if pages.empty:
    st.warning(f"No OCR page folders were found in `{DATASET_DIR}`.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    documents = sorted(audit["document"].unique())
    selected_doc = st.selectbox("PDF / OCR document", documents, index=0 if documents else None)
    statuses = sorted(audit["processing_status"].unique())
    selected_statuses = st.multiselect("Processing status", statuses, default=[])
    selected_models = st.multiselect("LLM model", sorted(v for v in runs["model"].map(clean).unique() if v) if not runs.empty else [])
    selected_prompts = st.multiselect("Prompt", sorted(v for v in runs["prompt"].map(clean).unique() if v) if not runs.empty else [])
    search = st.text_input("Search page/job/error", "")

view = audit[audit["document"].eq(selected_doc)].copy() if selected_doc else audit.copy()
if selected_statuses:
    view = view[view["processing_status"].isin(selected_statuses)]
if selected_models:
    view = view[view["models"].apply(lambda text: any(model in text for model in selected_models))]
if selected_prompts:
    view = view[view["prompts"].apply(lambda text: any(prompt in text for prompt in selected_prompts))]
if search.strip():
    needle = search.lower().strip()
    view = view[
        view["page_name"].str.lower().str.contains(needle, regex=False)
        | view["job_ids"].str.lower().str.contains(needle, regex=False)
        | view["latest_error"].str.lower().str.contains(needle, regex=False)
    ]

metrics = st.columns(6)
metrics[0].metric("Pages in document", f"{len(audit[audit['document'].eq(selected_doc)]):,}" if selected_doc else f"{len(audit):,}")
metrics[1].metric("Visible pages", f"{len(view):,}")
metrics[2].metric("Processed with output", f"{int(view['processing_status'].eq('processed_with_output').sum()):,}")
metrics[3].metric("Failed pages", f"{int(view['processing_status'].eq('processed_failed').sum()):,}")
metrics[4].metric("Not processed", f"{int(view['processing_status'].eq('not_processed').sum()):,}")
metrics[5].metric("Output records", f"{int(view['output_records'].sum()):,}")

tabs = st.tabs(["Page Audit Table", "LLM Output By Page", "Jobs & Config", "Distribution"])

with tabs[0]:
    st.markdown("Each row is one OCR page from the selected PDF/document.")
    st.dataframe(view, use_container_width=True, hide_index=True, height=620)
    st.download_button(
        "Download visible page audit CSV",
        view.to_csv(index=False).encode("utf-8"),
        file_name="pdf_page_processing_audit.csv",
        mime="text/csv",
    )

with tabs[1]:
    st.markdown("Parsed LLM output records joined back to PDF page names.")
    record_view = records[records["document"].eq(selected_doc)].copy() if selected_doc and not records.empty else records.copy()
    if selected_models and not record_view.empty:
        record_view = record_view[record_view["model"].isin(selected_models)]
    if selected_prompts and not record_view.empty:
        record_view = record_view[record_view["prompt"].isin(selected_prompts)]
    if record_view.empty:
        st.info("No parsed LLM output records found for the current filters.")
    else:
        st.dataframe(record_view, use_container_width=True, hide_index=True, height=620)
        st.download_button(
            "Download visible LLM output CSV",
            record_view.to_csv(index=False).encode("utf-8"),
            file_name="pdf_page_llm_output.csv",
            mime="text/csv",
        )

with tabs[2]:
    st.markdown("Background job selections show which pages were queued even before output exists.")
    job_view = jobs[jobs["document"].eq(selected_doc)].copy() if selected_doc and not jobs.empty else jobs.copy()
    if job_view.empty:
        st.info("No background job config rows found for the selected document.")
    else:
        st.dataframe(job_view, use_container_width=True, hide_index=True, height=420)

    run_view = runs[runs["document"].eq(selected_doc)].copy() if selected_doc and not runs.empty else runs.copy()
    st.markdown("**Run-level output rows**")
    if run_view.empty:
        st.info("No T3 run rows found for the selected document.")
    else:
        st.dataframe(run_view.drop(columns=["raw_output"], errors="ignore"), use_container_width=True, hide_index=True, height=420)

with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Page processing status**")
        status_chart(view)
    with c2:
        st.markdown("**Output records per page**")
        chart_data = view[["page_name", "output_records"]].copy()
        chart = (
            alt.Chart(chart_data)
            .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
            .encode(
                x=alt.X("page_name:N", sort=None, title=None, axis=alt.Axis(labelLimit=80)),
                y=alt.Y("output_records:Q", title="Records"),
                tooltip=["page_name", "output_records"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart, use_container_width=True)

    st.markdown("**Coverage by document**")
    coverage = (
        audit.assign(processed=audit["processing_status"].isin(["processed_with_output", "processed_empty_output"]))
        .groupby("document", dropna=False)
        .agg(total_pages=("page_name", "count"), processed_pages=("processed", "sum"), output_records=("output_records", "sum"))
        .reset_index()
    )
    coverage["coverage_pct"] = (coverage["processed_pages"] / coverage["total_pages"] * 100).round(2)
    st.dataframe(coverage, use_container_width=True, hide_index=True, height=360)
