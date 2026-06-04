from __future__ import annotations

from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Phase 1 Completed Dataset", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from dataset_phase_utils import (  # noqa: E402
    ANNOTATION_PATH,
    add_pdf_metadata,
    move_records,
    phase_view,
    save_annotation_updates,
)


EDIT_COLS = [
    "select",
    "record_id",
    "source_dataset",
    "completion_status",
    "review_status",
    "annotator",
    "review_notes",
    "ground_truth_tone",
    "ground_truth_esg",
    "ground_truth_aspect",
    "company",
    "model",
    "prompt",
    "target",
    "text",
]


def distribution_table(df: pd.DataFrame, column: str, label: str, top_n: int = 15) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return pd.DataFrame(columns=[label, "records"])
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


def distribution_chart(df: pd.DataFrame, category_col: str, height: int = 280) -> alt.Chart:
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
        .properties(height=height)
    )


def original_file(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "<missing>"
    return text.split("/batch_", 1)[0]


st.title("Phase 1 Completed Dataset")
st.caption("Inspect the completed dataset pool used for final analysis claims, and move rows back to Phase 2 or Phase 3 if review finds a problem.")

view = phase_view()
phase1 = view[view["phase"].eq("Phase 1")].copy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Phase 1 rows", f"{len(phase1):,}")
c2.metric("Ground-truth tone", f"{int(phase1['has_ground_truth_tone'].sum()):,}" if not phase1.empty else "0")
c3.metric("Ground-truth ESG", f"{int(phase1['has_ground_truth_esg'].sum()):,}" if not phase1.empty else "0")
c4.metric("Ground-truth aspect", f"{int(phase1['has_ground_truth_aspect'].sum()):,}" if not phase1.empty else "0")

if phase1.empty:
    st.info("No Phase 1 rows are currently available.")
    st.stop()

st.subheader("Phase 1 Distributions")
d1, d2, d3 = st.columns(3)

phase1_dist = add_pdf_metadata(phase1, "target")
pdf_dist = (
    phase1_dist.groupby(["original_file", "company_name", "report_year"], dropna=False)
    .size()
    .reset_index(name="records")
    .sort_values(["records", "original_file"], ascending=[False, True])
    .head(15)
    .reset_index(drop=True)
)
model_dist = distribution_table(phase1, "model", "model")
prompt_dist = distribution_table(phase1, "prompt", "prompt")

with d1:
    st.caption("PDF / file distribution (original)")
    st.dataframe(pdf_dist, use_container_width=True, hide_index=True, height=280)
    if not pdf_dist.empty:
        st.altair_chart(distribution_chart(pdf_dist, "original_file"), use_container_width=True)
with d2:
    st.caption("LLM model distribution")
    st.dataframe(model_dist, use_container_width=True, hide_index=True, height=280)
    if not model_dist.empty:
        st.altair_chart(distribution_chart(model_dist, "model"), use_container_width=True)
with d3:
    st.caption("Prompt distribution")
    st.dataframe(prompt_dist, use_container_width=True, hide_index=True, height=280)
    if not prompt_dist.empty:
        st.altair_chart(distribution_chart(prompt_dist, "prompt"), use_container_width=True)

st.subheader("Ground-Truth Label Distributions")
l1, l2, l3 = st.columns(3)

tone_dist = distribution_table(phase1, "ground_truth_tone", "ground_truth_tone")
esg_dist = distribution_table(phase1, "ground_truth_esg", "ground_truth_esg")
aspect_dist = distribution_table(phase1, "ground_truth_aspect", "ground_truth_aspect")

with l1:
    st.caption("Ground-truth tone")
    st.dataframe(tone_dist, use_container_width=True, hide_index=True, height=280)
    if not tone_dist.empty:
        st.altair_chart(distribution_chart(tone_dist, "ground_truth_tone"), use_container_width=True)
with l2:
    st.caption("Ground-truth ESG")
    st.dataframe(esg_dist, use_container_width=True, hide_index=True, height=280)
    if not esg_dist.empty:
        st.altair_chart(distribution_chart(esg_dist, "ground_truth_esg"), use_container_width=True)
with l3:
    st.caption("Ground-truth aspect")
    st.dataframe(aspect_dist, use_container_width=True, hide_index=True, height=280)
    if not aspect_dist.empty:
        st.altair_chart(distribution_chart(aspect_dist, "ground_truth_aspect"), use_container_width=True)

with st.sidebar:
    st.header("Filters")
    query = st.text_input("Search record/company/text", value="")
    status_options = sorted(phase1["review_status"].astype(str).replace("", "<missing>").unique().tolist())
    selected_statuses = st.multiselect("Review status", status_options, default=status_options)
    max_rows = st.number_input("Max rows", min_value=10, max_value=5000, value=300, step=25)

filtered = phase1.copy()
filtered_status = filtered["review_status"].astype(str).replace("", "<missing>")
filtered = filtered[filtered_status.isin(selected_statuses)]
if query.strip():
    q = query.strip().lower()
    haystack = (
        filtered["record_id"].astype(str)
        + " "
        + filtered["company"].astype(str)
        + " "
        + filtered["text"].astype(str)
    ).str.lower()
    filtered = filtered[haystack.str.contains(q, na=False)]

filtered = filtered.head(int(max_rows)).copy()
filtered.insert(0, "select", False)

st.subheader("Phase 1 Record Table")
st.caption(
    "Saving edits writes to "
    f"`{ANNOTATION_PATH.relative_to(ROOT)}`. Moving rows out of Phase 1 updates only the phase registry."
)
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
        "completion_status",
        "company",
        "model",
        "prompt",
        "target",
        "text",
    ],
    key="phase1_editor",
)

checkbox_selected_ids = edited.loc[edited["select"], "record_id"].astype(str).tolist() if "select" in edited.columns else []
selected_ids = sorted(set(checkbox_selected_ids + manual_selected_ids))
edited_for_save = edited.drop(columns=["select"], errors="ignore").copy()

a1, a2, a3 = st.columns(3)
if a1.button("Save visible edits", type="primary", use_container_width=True):
    changed = save_annotation_updates(edited_for_save)
    st.success(f"Saved {changed:,} visible row(s).")
    st.rerun()

if a2.button(
    f"Save and move selected to Phase 2 ({len(selected_ids):,})",
    use_container_width=True,
    disabled=not selected_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(selected_ids)])
    moved = move_records(selected_ids, "Phase 2", "Returned from Phase 1 for editing", "phase1_page")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 2.")
    st.rerun()

if a3.button(
    f"Move selected to Phase 3 ({len(selected_ids):,})",
    use_container_width=True,
    disabled=not selected_ids,
):
    moved = move_records(selected_ids, "Phase 3", "Returned from Phase 1 to intake triage", "phase1_page")
    st.success(f"Moved {moved:,} record(s) to Phase 3.")
    st.rerun()

st.subheader("Download")
st.download_button(
    "Download visible Phase 1 rows",
    edited_for_save.to_csv(index=False).encode("utf-8"),
    "phase1_completed_dataset_visible_rows.csv",
    "text/csv",
    use_container_width=True,
)
