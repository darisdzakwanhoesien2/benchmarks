import streamlit as st


st.title("ABSA Ground Truth Annotation Guide (Windows)")
st.caption("Reference guide for labels used by `absa_metrics_comparison.py`.")

st.subheader("Core Human-Labeled Elements")
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

st.subheader("Recommended Supporting Metadata")
support_rows = [
    {"field": "annotator_id", "description": "Identifier of the human annotator."},
    {"field": "annotation_timestamp", "description": "When annotation was created/updated."},
    {"field": "guideline_version", "description": "Labeling guideline version used for consistency."},
    {"field": "confidence", "description": "Human confidence score/value for the label."},
    {"field": "adjudicated_label", "description": "Final resolved label after disagreement review."},
    {"field": "notes_rationale", "description": "Short rationale for difficult or ambiguous cases."},
]
st.data_editor(support_rows, num_rows="dynamic", use_container_width=True, key="gt_guide_windows_support")

st.subheader("Annotation Unit Rule")
st.write("Use `sentence_norm + canonical_aspect` as the labeling unit, then assign category, sentiment, and tone consistently.")
