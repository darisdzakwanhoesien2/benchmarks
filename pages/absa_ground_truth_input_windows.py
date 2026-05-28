import streamlit as st
from pathlib import Path
import pandas as pd


st.title("ABSA Ground Truth Input (Windows)")

PAGE_DIR = Path(__file__).resolve().parent
BENCHMARK_ROOT = PAGE_DIR.parent
GROUND_TRUTH_PATH = BENCHMARK_ROOT / "data" / "ground_truth_windows" / "absa_mapping.csv"

st.caption(f"Source used by `absa_metrics_comparison.py`: `{GROUND_TRUTH_PATH}`")

if not GROUND_TRUTH_PATH.exists():
    st.error(f"Missing file: {GROUND_TRUTH_PATH}")
    st.stop()

df = pd.read_csv(GROUND_TRUTH_PATH)
st.write(f"Rows: {len(df):,} | Columns: {len(df.columns)}")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="absa_gt_windows_editor",
)

col1, col2 = st.columns(2)
with col1:
    if st.button("Save Changes", type="primary", use_container_width=True):
        edited_df.to_csv(GROUND_TRUTH_PATH, index=False)
        st.success(f"Saved to {GROUND_TRUTH_PATH}")
with col2:
    st.download_button(
        "Download Edited CSV",
        data=edited_df.to_csv(index=False).encode("utf-8"),
        file_name="absa_mapping_windows_edited.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.subheader("Ground Truth Annotation Guide")

st.markdown("**Core Human-Labeled Elements**")
core_rows = [
    {
        "field": "sentence_norm",
        "description": "Canonical sentence text to label; stable key for merges/comparison.",
    },
    {
        "field": "canonical_aspect",
        "description": "Normalized aspect target in the sentence (what sentiment/tone refers to).",
    },
    {
        "field": "majority_category",
        "description": "Aspect/category class label based on the taxonomy.",
    },
    {
        "field": "majority_sentiment",
        "description": "Sentiment polarity label for that aspect (e.g., positive/neutral/negative).",
    },
    {
        "field": "majority_tone",
        "description": "Tone or intent label based on your schema (e.g., commitment/action/outcome).",
    },
]
st.data_editor(core_rows, num_rows="dynamic", use_container_width=True, key="gt_guide_windows_core")

st.markdown("**Recommended Supporting Metadata**")
support_rows = [
    {"field": "annotator_id", "description": "Identifier of the human annotator."},
    {"field": "annotation_timestamp", "description": "When annotation was created/updated."},
    {"field": "guideline_version", "description": "Labeling guideline version used for consistency."},
    {"field": "confidence", "description": "Human confidence score/value for the label."},
    {"field": "adjudicated_label", "description": "Final resolved label after disagreement review."},
    {"field": "notes_rationale", "description": "Short rationale for difficult or ambiguous cases."},
]
st.data_editor(support_rows, num_rows="dynamic", use_container_width=True, key="gt_guide_windows_support")

st.markdown("**Annotation Unit Rule**")
st.write("Use `sentence_norm + canonical_aspect` as the labeling unit, then assign category, sentiment, and tone consistently.")
