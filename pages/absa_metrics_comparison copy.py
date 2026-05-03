import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix

st.title("ABSA Mapping Metrics Comparison")
add_page_explanation(__file__)

# File paths
gt_path = "data/ground_truth_windows/absa_mapping.csv"
baseline_path = "data/ground_truth_windows/absa_mapping_baseline.csv"

# Load data
gt = pd.read_csv(gt_path)
baseline = pd.read_csv(baseline_path)

# Try to align on canonical_aspect (or raw_aspects if needed)
# For demonstration, align on canonical_aspect
merge_col = "canonical_aspect" if "canonical_aspect" in gt.columns and "canonical_aspect" in baseline.columns else "raw_aspects"

merged = pd.merge(gt, baseline, on=merge_col, suffixes=("_gt", "_baseline"), how="inner")

# Choose which columns to compare
cat_gt = merged["majority_category_gt"].astype(str)
cat_baseline = merged["majority_category_baseline"].astype(str)

# Compute metrics
def compute_metrics(y_true, y_pred, label):
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=list(set(y_true) | set(y_pred)))
    st.subheader(f"{label} Metrics")
    st.write(f"F1 Score: {f1:.3f}")
    st.write(f"Precision: {precision:.3f}")
    st.write(f"Recall: {recall:.3f}")
    st.write("Confusion Matrix:")
    st.dataframe(pd.DataFrame(cm, index=list(set(y_true) | set(y_pred)), columns=list(set(y_true) | set(y_pred))))

    # TP, FP, FN (for each class)
    st.write("True Positives, False Positives, False Negatives per class:")
    for i, label in enumerate(list(set(y_true) | set(y_pred))):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        st.write(f"{label}: TP={tp}, FP={fp}, FN={fn}")

compute_metrics(cat_gt, cat_baseline, "Majority Category")

# Optionally, repeat for sentiments and tones if columns exist
if "sentiments_gt" in merged.columns and "sentiments_baseline" in merged.columns:
    compute_metrics(merged["sentiments_gt"].astype(str), merged["sentiments_baseline"].astype(str), "Sentiments")
if "tones_gt" in merged.columns and "tones_baseline" in merged.columns:
    compute_metrics(merged["tones_gt"].astype(str), merged["tones_baseline"].astype(str), "Tones")

st.write("\n---\n")
st.write("Compared on column:", merge_col)
