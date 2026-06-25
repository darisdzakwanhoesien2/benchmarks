from __future__ import annotations

from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Phase 2 Resolver", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from dataset_phase_utils import (  # noqa: E402
    ANNOTATION_PATH,
    CORE_GT_COLS,
    OPTIONAL_QA_COLS,
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
    "completion_status",
    "missing_core_fields",
    "missing_qa_fields",
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


def distribution_chart(df: pd.DataFrame, category_col: str) -> alt.Chart:
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


def original_file(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "<missing>"
    return text.split("/batch_", 1)[0]


st.title("Phase 2 Resolver")
st.caption("Resolve editing/backfill rows, then promote complete records into the Phase 1 completed dataset pool.")

view = phase_view()
phase2 = view[view["phase"].eq("Phase 2")].copy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Phase 2 rows", f"{len(phase2):,}")
c2.metric("Missing tone", f"{int((~phase2['has_ground_truth_tone'].astype(bool)).sum()):,}" if not phase2.empty else "0")
c3.metric("Missing ESG", f"{int((~phase2['has_ground_truth_esg'].astype(bool)).sum()):,}" if not phase2.empty else "0")
c4.metric("Missing aspect", f"{int((~phase2['has_ground_truth_aspect'].astype(bool)).sum()):,}" if not phase2.empty else "0")

if phase2.empty:
    st.success("No Phase 2 rows remain.")
    st.stop()

st.subheader("Phase 2 Distributions")
d1, d2, d3 = st.columns(3)

phase2_dist = add_pdf_metadata(phase2, "target")
pdf_dist = (
    phase2_dist.groupby(["original_file", "company_name", "report_year"], dropna=False)
    .size()
    .reset_index(name="records")
    .sort_values(["records", "original_file"], ascending=[False, True])
    .head(15)
    .reset_index(drop=True)
)
model_dist = distribution_table(phase2, "model", "model")
prompt_dist = distribution_table(phase2, "prompt", "prompt")

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

with st.sidebar:
    st.header("Filters")
    missing_options = ["Any missing field", *CORE_GT_COLS, *OPTIONAL_QA_COLS]
    missing_filter = st.selectbox("Missing field", missing_options)
    query = st.text_input("Search record/company/text", value="")
    max_rows = st.number_input("Max rows", min_value=10, max_value=2000, value=300, step=25)

filtered = phase2.copy()
if missing_filter != "Any missing field":
    filtered = filtered[
        filtered["missing_core_fields"].astype(str).str.contains(missing_filter, regex=False)
        | filtered["missing_qa_fields"].astype(str).str.contains(missing_filter, regex=False)
    ]
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

st.subheader("Phase 2 Editing Table")
st.caption(f"Saving edits writes to `{ANNOTATION_PATH.relative_to(ROOT)}`. Promotion only updates the phase registry.")
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
        "missing_core_fields",
        "missing_qa_fields",
        "company",
        "model",
        "prompt",
        "target",
        "text",
    ],
    key="phase2_editor",
)

checkbox_selected_ids = edited.loc[edited["select"], "record_id"].astype(str).tolist() if "select" in edited.columns else []
selected_ids = sorted(set(checkbox_selected_ids + manual_selected_ids))
edited_for_save = edited.drop(columns=["select"], errors="ignore").copy()
complete_visible_ids = complete_record_ids(edited_for_save)
complete_selected_ids = [record_id for record_id in selected_ids if record_id in set(complete_visible_ids)]

s1, s2, s3, s4 = st.columns(4)
if s1.button("Save visible edits", type="primary", use_container_width=True):
    changed = save_annotation_updates(edited_for_save)
    st.success(f"Saved {changed:,} visible row(s).")
    st.rerun()

if s2.button(
    f"Save and move selected to Phase 1 ({len(selected_ids):,})",
    use_container_width=True,
    disabled=not selected_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(selected_ids)])
    moved = move_records(selected_ids, "Phase 1", "Resolved in Phase 2 resolver", "phase2_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if s3.button(
    f"Save and promote complete selected ({len(complete_selected_ids):,})",
    use_container_width=True,
    disabled=not complete_selected_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(complete_selected_ids)])
    moved = move_records(complete_selected_ids, "Phase 1", "Resolved complete selection in Phase 2 resolver", "phase2_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if s4.button(
    f"Promote all complete visible ({len(complete_visible_ids):,})",
    use_container_width=True,
    disabled=not complete_visible_ids,
):
    changed = save_annotation_updates(edited_for_save[edited_for_save["record_id"].isin(complete_visible_ids)])
    moved = move_records(complete_visible_ids, "Phase 1", "Bulk resolved in Phase 2 resolver", "phase2_resolver")
    st.success(f"Saved {changed:,} row(s) and moved {moved:,} record(s) to Phase 1.")
    st.rerun()

st.subheader("Download")
st.download_button(
    "Download visible Phase 2 rows",
    edited_for_save.to_csv(index=False).encode("utf-8"),
    "phase2_resolver_visible_rows.csv",
    "text/csv",
    use_container_width=True,
)
