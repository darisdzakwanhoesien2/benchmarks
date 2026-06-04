from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys

import altair as alt
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Phase 3 Resolver", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
JOBS_DIR = ROOT / "results" / "background_llm_jobs"
WORKER_PATH = ROOT / "code" / "llm_background_worker.py"
sys.path.insert(0, str(ROOT / "code"))

from dataset_phase_utils import (  # noqa: E402
    ANNOTATION_PATH,
    add_pdf_metadata,
    complete_record_ids,
    move_records,
    phase_view,
    save_annotation_updates,
)


EDIT_COLS = [
    "select",
    "record_id",
    "source_dataset",
    "timestamp",
    "success_event_timestamp",
    "success_event_records",
    "success_event_seconds",
    "event",
    "event_records",
    "target_pages",
    "background_job_id",
    "phase_reason",
    "tone_pred",
    "esg",
    "aspect",
    "ground_truth_tone",
    "ground_truth_esg",
    "ground_truth_aspect",
    "review_status",
    "annotator",
    "review_notes",
    "company",
    "model",
    "prompt",
    "target",
    "text",
]


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def request_job_control(job_id: str, **updates) -> None:
    control_path = JOBS_DIR / job_id / "control.json"
    control = read_json(control_path, {})
    control.update(updates)
    control["updated_at"] = utc_now()
    write_json(control_path, control)


def launch_job(job_id: str) -> None:
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    with (job_dir / "worker.log").open("ab") as stdout, (job_dir / "worker.err.log").open("ab") as stderr:
        process = subprocess.Popen(
            [sys.executable, str(WORKER_PATH), job_id],
            cwd=str(ROOT),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    status = read_json(job_dir / "status.json", {})
    status.update(
        {
            "job_id": job_id,
            "pid": process.pid,
            "status": "running",
            "updated_at": utc_now(),
            "started_at": status.get("started_at") or utc_now(),
        }
    )
    write_json(job_dir / "status.json", status)


def job_control_rows(df):
    if df.empty or "background_job_id" not in df.columns:
        return []
    cols = [
        "background_job_id",
        "job_status",
        "job_completion_progress",
        "job_llm_call_progress",
        "job_elapsed_seconds",
        "job_completed_targets",
        "job_failed_targets",
        "job_total_targets",
    ]
    available_cols = [col for col in cols if col in df.columns]
    jobs = df[available_cols].drop_duplicates("background_job_id").copy()
    rows = []
    for _, row in jobs.iterrows():
        job_id = str(row.get("background_job_id", "")).strip()
        if not job_id:
            continue
        status = read_json(JOBS_DIR / job_id / "status.json", {})
        control = read_json(JOBS_DIR / job_id / "control.json", {})
        rows.append(
            {
                "background_job_id": job_id,
                "derived_job_status": row.get("job_status", ""),
                "worker_status": status.get("status", ""),
                "current": status.get("current", ""),
                "control_pause_requested": bool(control.get("pause_requested")),
                "control_stop_requested": bool(control.get("stop_requested")),
                "job_completion_progress": row.get("job_completion_progress", ""),
                "job_llm_call_progress": row.get("job_llm_call_progress", ""),
                "job_elapsed_seconds": row.get("job_elapsed_seconds", ""),
                "status_updated_at": status.get("updated_at", ""),
            }
        )
    return rows


def distribution_table(df, column: str, label: str, top_n: int = 15):
    if df.empty or column not in df.columns:
        return []
    counts = (
        df[column]
        .astype(str)
        .str.strip()
        .replace("", "<missing>")
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    counts.columns = [label, "records"]
    return counts


def distribution_chart(df, category_col: str) -> alt.Chart:
    tooltip = [category_col, "records"]
    if "company_name" in df.columns:
        tooltip.insert(1, "company_name")
    if "report_year" in df.columns:
        tooltip.insert(2, "report_year")
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("records:Q", title="records"),
            y=alt.Y(f"{category_col}:N", sort="-x", title=None),
            tooltip=tooltip,
        )
        .properties(height=280)
    )


def count_pages(value) -> int:
    text = str(value or "").strip()
    if not text:
        return 0
    return len([part for part in text.split(",") if part.strip()])


def parsed_attempt_trace(df, top_n: int = 100):
    if df.empty or "source_dataset" not in df.columns:
        return []
    parsed = df[df["source_dataset"].astype(str).eq("live_llm_reprocess")].copy()
    if parsed.empty:
        return []
    group_cols = [
        "target",
        "background_job_id",
        "timestamp",
        "success_event_timestamp",
        "success_event_records",
        "success_event_pages",
        "success_event_seconds",
        "job_status",
        "job_completion_progress",
        "job_llm_call_progress",
        "job_elapsed_seconds",
        "job_sum_target_seconds",
        "job_completed_targets",
        "job_failed_targets",
        "job_total_targets",
        "model",
        "prompt",
    ]
    available_cols = [col for col in group_cols if col in parsed.columns]
    trace = (
        parsed.groupby(available_cols, dropna=False)
        .size()
        .reset_index(name="parsed_llm_rows")
        .sort_values(["success_event_timestamp", "timestamp", "target"], ascending=[False, False, True])
        .head(top_n)
        .reset_index(drop=True)
    )
    if "success_event_pages" in trace.columns:
        trace["success_event_page_count"] = trace["success_event_pages"].map(count_pages)
    if "model" in trace.columns:
        trace["llm_called"] = trace["model"]
    ordered_cols = [
        "target",
        "background_job_id",
        "timestamp",
        "success_event_timestamp",
        "success_event_page_count",
        "success_event_pages",
        "success_event_records",
        "success_event_seconds",
        "job_status",
        "job_completion_progress",
        "job_llm_call_progress",
        "job_elapsed_seconds",
        "job_sum_target_seconds",
        "llm_called",
        "model",
        "prompt",
        "parsed_llm_rows",
    ]
    trace = trace[[col for col in ordered_cols if col in trace.columns]]
    return trace


def parsed_llm_rows_detail(df, top_n: int = 300):
    if df.empty or "source_dataset" not in df.columns:
        return []
    parsed = df[df["source_dataset"].astype(str).eq("live_llm_reprocess")].copy()
    if parsed.empty:
        return []
    parsed = add_pdf_metadata(parsed, "target")
    if "success_event_pages" in parsed.columns:
        parsed["success_event_page_count"] = parsed["success_event_pages"].map(count_pages)
    if "model" in parsed.columns:
        parsed["llm_called"] = parsed["model"]
    detail_cols = [
        "record_id",
        "timestamp",
        "success_event_timestamp",
        "success_event_page_count",
        "success_event_pages",
        "success_event_records",
        "success_event_seconds",
        "job_status",
        "job_completion_progress",
        "job_llm_call_progress",
        "job_elapsed_seconds",
        "job_sum_target_seconds",
        "job_completed_targets",
        "job_failed_targets",
        "job_total_targets",
        "llm_called",
        "background_job_id",
        "target",
        "original_file",
        "ticker",
        "ticker_company_name",
        "company_name",
        "report_year",
        "model",
        "prompt",
        "run_idx",
        "record_idx",
        "tone_pred",
        "esg",
        "aspect",
        "text",
    ]
    available_cols = [col for col in detail_cols if col in parsed.columns]
    sort_cols = [col for col in ["target", "background_job_id", "timestamp", "record_idx"] if col in parsed.columns]
    if sort_cols:
        parsed = parsed.sort_values(sort_cols, ascending=[True] * len(sort_cols))
    return parsed[available_cols].head(top_n).reset_index(drop=True)


def original_file(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "<missing>"
    return text.split("/batch_", 1)[0]


st.title("Phase 3 Resolver")
st.caption("Triage new intake rows into the completed dataset pool or the editing/backfill pool.")

view = phase_view()
phase3 = view[view["phase"].eq("Phase 3")].copy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Phase 3 rows", f"{len(phase3):,}")
c2.metric("Parsed LLM rows", f"{int(phase3['source_dataset'].astype(str).eq('live_llm_reprocess').sum()):,}" if not phase3.empty else "0")
c3.metric("Event rows", f"{int(phase3['source_dataset'].astype(str).eq('background_llm_event').sum()):,}" if not phase3.empty else "0")
c4.metric("Already complete", f"{int(phase3['phase1_ready'].sum()):,}" if not phase3.empty else "0")

if phase3.empty:
    st.success("No Phase 3 rows remain.")
    st.stop()

st.subheader("Phase 3 Distributions")
d1, d2, d3 = st.columns(3)

phase3_dist = add_pdf_metadata(phase3, "target")
pdf_dist = (
    phase3_dist.groupby(["original_file", "company_name", "report_year"], dropna=False)
    .size()
    .reset_index(name="records")
    .sort_values(["records", "original_file"], ascending=[False, True])
    .head(15)
    .reset_index(drop=True)
)
model_dist = distribution_table(phase3, "model", "model")
prompt_dist = distribution_table(phase3, "prompt", "prompt")

with d1:
    st.caption("PDF / file distribution (original)")
    st.dataframe(pdf_dist, use_container_width=True, hide_index=True, height=280)
    if len(pdf_dist):
        st.altair_chart(distribution_chart(pdf_dist, "original_file"), use_container_width=True)
with d2:
    st.caption("LLM model distribution")
    st.dataframe(model_dist, use_container_width=True, hide_index=True, height=280)
    if len(model_dist):
        st.altair_chart(distribution_chart(model_dist, "model"), use_container_width=True)
with d3:
    st.caption("Prompt distribution")
    st.dataframe(prompt_dist, use_container_width=True, hide_index=True, height=280)
    if len(prompt_dist):
        st.altair_chart(distribution_chart(prompt_dist, "prompt"), use_container_width=True)

with st.sidebar:
    st.header("Filters")
    source_options = sorted(phase3["source_dataset"].dropna().astype(str).unique().tolist())
    selected_sources = st.multiselect("Source", source_options, default=source_options)
    query = st.text_input("Search record/company/text", value="")
    max_rows = st.number_input("Max rows", min_value=10, max_value=2000, value=300, step=25)
    parsed_rows_limit = st.number_input("Parsed LLM detail rows", min_value=10, max_value=10000, value=1000, step=100)

filtered_all = phase3[phase3["source_dataset"].astype(str).isin(selected_sources)].copy()
if query.strip():
    q = query.strip().lower()
    haystack = (
        filtered_all["record_id"].astype(str)
        + " "
        + filtered_all["company"].astype(str)
        + " "
        + filtered_all["text"].astype(str)
    ).str.lower()
    filtered_all = filtered_all[haystack.str.contains(q, na=False)]

sort_cols = [col for col in ["target", "background_job_id", "timestamp", "success_event_timestamp", "record_idx"] if col in filtered_all.columns]
if sort_cols:
    filtered_all = filtered_all.sort_values(sort_cols, ascending=[True] * len(sort_cols)).copy()
filtered = filtered_all.head(int(max_rows)).copy()
filtered.insert(0, "select", False)

for source_col, target_col in [("tone_pred", "ground_truth_tone"), ("esg", "ground_truth_esg"), ("aspect", "ground_truth_aspect")]:
    if source_col in filtered.columns and target_col in filtered.columns:
        empty_mask = filtered[target_col].astype(str).str.strip().eq("")
        filtered.loc[empty_mask, target_col] = filtered.loc[empty_mask, source_col].astype(str)

st.subheader("Phase 3 Triage Table")
st.caption(
    "Phase 3 rows are not part of final denominators until they are moved. "
    f"Saving annotations writes to `{ANNOTATION_PATH.relative_to(ROOT)}`."
)
visible_parsed_count = int(filtered_all["source_dataset"].astype(str).eq("live_llm_reprocess").sum()) if "source_dataset" in filtered_all.columns else 0
st.caption(
    f"Current filters contain {visible_parsed_count:,} Parsed LLM row(s). "
    f"The editor below is capped separately at {int(max_rows):,} total Phase 3 row(s)."
)

trace = parsed_attempt_trace(filtered_all, top_n=int(parsed_rows_limit))
if len(trace):
    st.caption("Parsed LLM attempt trace")
    st.caption(
        "`success_event_seconds` is the completed-event duration for that target batch/page group. "
        "`job_elapsed_seconds` is the whole background job duration from its started event to the latest completed/failed event."
    )
    st.dataframe(trace, use_container_width=True, hide_index=True, height=240)
else:
    st.info("No parsed LLM rows are visible for the current filter.")

control_rows = job_control_rows(filtered_all)
in_progress_rows = [row for row in control_rows if row.get("derived_job_status") == "in_progress"]
if in_progress_rows:
    st.caption("In-progress background job controls")
    st.dataframe(in_progress_rows, use_container_width=True, hide_index=True, height=180)
    job_options = [row["background_job_id"] for row in in_progress_rows]
    selected_control_job = st.selectbox("Select in-progress job to control", job_options)
    selected_control_status = next((row for row in in_progress_rows if row["background_job_id"] == selected_control_job), {})
    worker_status = str(selected_control_status.get("worker_status", "")).lower()
    jc1, jc2, jc3 = st.columns(3)
    if jc1.button(
        "Pause after current",
        disabled=worker_status != "running",
        use_container_width=True,
        help="Cooperative pause: the worker finishes the current model-target-prompt item first.",
    ):
        request_job_control(selected_control_job, pause_requested=True)
        st.success(f"Pause requested for `{selected_control_job}`.")
        st.rerun()
    if jc2.button(
        "Resume / keep running",
        disabled=worker_status not in {"paused", "exited", "failed", "stopped"},
        use_container_width=True,
        help="Clears pause/stop flags and relaunches the worker for this job.",
    ):
        request_job_control(selected_control_job, pause_requested=False, stop_requested=False)
        launch_job(selected_control_job)
        st.success(f"Resume requested for `{selected_control_job}`.")
        st.rerun()
    if jc3.button("Refresh job status", use_container_width=True):
        st.rerun()
else:
    st.caption("No in-progress background jobs are visible for the current filter.")

parsed_detail = parsed_llm_rows_detail(filtered_all, top_n=int(parsed_rows_limit))
if len(parsed_detail):
    st.caption("Parsed LLM row details")
    st.dataframe(parsed_detail, use_container_width=True, hide_index=True, height=360)

manual_selected_ids = st.multiselect(
    "Selected records fallback",
    filtered["record_id"].astype(str).tolist(),
    default=[],
    help="Use this if checkbox selection in the table does not enable the move buttons.",
)

edited = st.data_editor(
    filtered[[col for col in EDIT_COLS if col in filtered.columns]],
    use_container_width=True,
    hide_index=True,
    height=560,
    column_config={
        "select": st.column_config.CheckboxColumn("select"),
        "ground_truth_tone": st.column_config.SelectboxColumn(
            "ground_truth_tone",
            options=["", "commitment", "action", "outcome", "none", "unknown"],
        ),
        "ground_truth_esg": st.column_config.SelectboxColumn(
            "ground_truth_esg",
            options=["", "e", "s", "g", "e-s", "e-g", "s-g", "e-s-g", "none", "unknown"],
        ),
        "review_status": st.column_config.SelectboxColumn(
            "review_status",
            options=["", "needs_review", "reviewed", "uncertain", "discard", "insufficient_context"],
        ),
        "text": st.column_config.TextColumn("text", width="large"),
        "review_notes": st.column_config.TextColumn("review_notes", width="large"),
    },
    disabled=[
        "record_id",
        "source_dataset",
        "timestamp",
        "success_event_timestamp",
        "success_event_records",
        "success_event_seconds",
        "event",
        "event_records",
        "target_pages",
        "background_job_id",
        "phase_reason",
        "tone_pred",
        "esg",
        "aspect",
        "company",
        "model",
        "prompt",
        "target",
        "text",
    ],
    key="phase3_editor",
)

checkbox_selected_ids = edited.loc[edited["select"], "record_id"].astype(str).tolist() if "select" in edited.columns else []
selected_ids = sorted(set(checkbox_selected_ids + manual_selected_ids))
edited_for_save = edited.drop(columns=["select"], errors="ignore").copy()
complete_visible_ids = complete_record_ids(edited_for_save)
complete_selected_ids = [record_id for record_id in selected_ids if record_id in set(complete_visible_ids)]
incomplete_selected_ids = [record_id for record_id in selected_ids if record_id not in set(complete_visible_ids)]

a1, a2, a3, a4 = st.columns(4)
if a1.button(
    f"Save and move selected to Phase 1 ({len(selected_ids):,})",
    type="primary",
    use_container_width=True,
    disabled=not selected_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(selected_ids)])
    moved = move_records(selected_ids, "Phase 1", "Accepted from Phase 3 resolver", "phase3_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if a2.button(
    f"Save and move selected to Phase 2 ({len(selected_ids):,})",
    use_container_width=True,
    disabled=not selected_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(selected_ids)])
    moved = move_records(selected_ids, "Phase 2", "Needs editing after Phase 3 triage", "phase3_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 2.")
    st.rerun()

if a3.button(
    f"Save and move complete selected to Phase 1 ({len(complete_selected_ids):,})",
    use_container_width=True,
    disabled=not complete_selected_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(complete_selected_ids)])
    moved = move_records(complete_selected_ids, "Phase 1", "Accepted complete selection from Phase 3 resolver", "phase3_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if a4.button(
    f"Save visible edits ({len(edited_for_save):,})",
    use_container_width=True,
):
    changed = save_annotation_updates(edited_for_save)
    st.success(f"Saved {changed:,} visible row(s).")
    st.rerun()

st.subheader("Bulk Triage")
b1, b2 = st.columns(2)
if b1.button(
    f"Move all complete visible to Phase 1 ({len(complete_visible_ids):,})",
    use_container_width=True,
    disabled=not complete_visible_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(complete_visible_ids)])
    moved = move_records(complete_visible_ids, "Phase 1", "Bulk accepted from Phase 3 resolver", "phase3_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if b2.button(
    f"Move all incomplete visible to Phase 2 ({len(edited_for_save) - len(complete_visible_ids):,})",
    use_container_width=True,
    disabled=len(edited_for_save) == len(complete_visible_ids),
):
    incomplete_visible_ids = [record_id for record_id in edited_for_save["record_id"].astype(str).tolist() if record_id not in set(complete_visible_ids)]
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(incomplete_visible_ids)])
    moved = move_records(incomplete_visible_ids, "Phase 2", "Bulk moved to editing from Phase 3 resolver", "phase3_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 2.")
    st.rerun()

st.subheader("Download")
st.download_button(
    "Download visible Phase 3 rows",
    edited_for_save.to_csv(index=False).encode("utf-8"),
    "phase3_resolver_visible_rows.csv",
    "text/csv",
    use_container_width=True,
)
