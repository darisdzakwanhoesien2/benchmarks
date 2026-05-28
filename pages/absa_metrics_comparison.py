import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix

import json

st.title("ABSA Mapping Metrics Comparison")
add_page_explanation(__file__)

PAGE_DIR = Path(__file__).resolve().parent
BENCHMARK_ROOT = PAGE_DIR.parent

# File paths
gt_path = BENCHMARK_ROOT / "data" / "ground_truth_windows" / "absa_mapping.csv"
baseline_path = BENCHMARK_ROOT / "data" / "ground_truth_windows" / "absa_mapping_baseline.csv"

source_rows = [
    {
        "source_type": "Ground truth input",
        "path": str(gt_path),
        "used_by": "pd.read_csv(gt_path)",
        "notes": "Primary ABSA labels for windows variant.",
    },
    {
        "source_type": "Baseline input",
        "path": str(baseline_path),
        "used_by": "pd.read_csv(baseline_path)",
        "notes": "Predicted/baseline labels compared against ground truth.",
    },
    {
        "source_type": "Category mapping",
        "path": str(BENCHMARK_ROOT / 'data' / 'mapping_category.json'),
        "used_by": "map_to_cluster for majority_category",
        "notes": "Maps raw categories to clustered categories.",
    },
    {
        "source_type": "Sentiment mapping",
        "path": str(BENCHMARK_ROOT / 'data' / 'sentiment_category.json'),
        "used_by": "map_sentiment_cluster for sentiments",
        "notes": "Used only when sentiments columns exist.",
    },
    {
        "source_type": "Tone mapping",
        "path": str(BENCHMARK_ROOT / 'data' / 'tone_category.json'),
        "used_by": "map_tone_cluster for tones",
        "notes": "Used only when tones columns exist.",
    },
    {
        "source_type": "Upstream generator page",
        "path": str(PAGE_DIR / '0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py'),
        "used_by": "Reference only",
        "notes": "Runs batch_process_csv_windows on ground_truth_windows dataset.",
    },
]

st.subheader("Data Sources")
st.caption("Editable provenance table for this page inputs and supporting mappings.")
st.data_editor(
    pd.DataFrame(source_rows),
    num_rows="dynamic",
    use_container_width=True,
    key="absa_metrics_sources_windows_editor",
)

# Load data
gt = pd.read_csv(gt_path)
baseline = pd.read_csv(baseline_path)

# Load mapping for category clustering
with open(BENCHMARK_ROOT / "data" / "mapping_category.json", "r") as f:
    category_mapping = json.load(f)

# Try to align on canonical_aspect (or raw_aspects if needed)
# For demonstration, align on canonical_aspect
merge_col = "canonical_aspect" if "canonical_aspect" in gt.columns and "canonical_aspect" in baseline.columns else "raw_aspects"

merged = pd.merge(gt, baseline, on=merge_col, suffixes=("_gt", "_baseline"), how="inner")

# Choose which columns to compare
def normalize_labels(series: pd.Series) -> pd.Series:
    return (
        series.fillna("none")
        .astype(str)
        .str.strip()
        .replace({"": "none", "nan": "none", "NaN": "none", "None": "none"})
    )


cat_gt = normalize_labels(merged["majority_category_gt"])
cat_baseline = normalize_labels(merged["majority_category_baseline"])

# Compute metrics
def compute_metrics(y_true, y_pred, label):
    y_true = normalize_labels(pd.Series(y_true)).reset_index(drop=True)
    y_pred = normalize_labels(pd.Series(y_pred)).reset_index(drop=True)
    labels = sorted(set(y_true) | set(y_pred))
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    st.subheader(f"{label} Metrics")
    st.write(f"F1 Score: {f1:.3f}")
    st.write(f"Precision: {precision:.3f}")
    st.write(f"Recall: {recall:.3f}")
    st.write("Confusion Matrix:")
    st.dataframe(pd.DataFrame(cm, index=labels, columns=labels))

    # TP, FP, FN (for each class) as table
    tp_fp_fn_data = []
    for i, class_label in enumerate(labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tp_fp_fn_data.append({"Class": class_label, "TP": tp, "FP": fp, "FN": fn})
    tp_fp_fn_df = pd.DataFrame(tp_fp_fn_data)
    st.write("True Positives, False Positives, False Negatives per class:")
    st.dataframe(tp_fp_fn_df)


# Map categories to clusters for majority category
def map_to_cluster(series):
    return normalize_labels(series).apply(lambda x: category_mapping.get(str(x), "none"))

cat_gt_cluster = map_to_cluster(cat_gt)
cat_baseline_cluster = map_to_cluster(cat_baseline)

# Original metrics
compute_metrics(cat_gt, cat_baseline, "Majority Category (Original)")
# Clustered metrics
compute_metrics(cat_gt_cluster, cat_baseline_cluster, "Majority Category (Clustered)")

# Optionally, repeat for sentiments and tones if columns exist
if "sentiments_gt" in merged.columns and "sentiments_baseline" in merged.columns:
    # Load sentiment mapping
    with open(BENCHMARK_ROOT / "data" / "sentiment_category.json", "r") as f:
        sentiment_mapping = json.load(f)

    def map_sentiment_cluster(series):
        return normalize_labels(series).apply(lambda x: sentiment_mapping.get(str(x), "none"))

    sentiments_gt = normalize_labels(merged["sentiments_gt"])
    sentiments_baseline = normalize_labels(merged["sentiments_baseline"])
    # Original metrics
    compute_metrics(sentiments_gt, sentiments_baseline, "Sentiments (Original)")
    # Clustered metrics
    compute_metrics(map_sentiment_cluster(sentiments_gt), map_sentiment_cluster(sentiments_baseline), "Sentiments (Clustered)")
if "tones_gt" in merged.columns and "tones_baseline" in merged.columns:
    # Load tone mapping
    with open(BENCHMARK_ROOT / "data" / "tone_category.json", "r") as f:
        tone_mapping = json.load(f)

    def map_tone_cluster(series):
        return normalize_labels(series).apply(lambda x: tone_mapping.get(str(x), "none"))

    tones_gt = normalize_labels(merged["tones_gt"])
    tones_baseline = normalize_labels(merged["tones_baseline"])
    # Original metrics
    compute_metrics(tones_gt, tones_baseline, "Tones (Original)")
    # Clustered metrics
    compute_metrics(map_tone_cluster(tones_gt), map_tone_cluster(tones_baseline), "Tones (Clustered)")

st.write("\n---\n")
st.write("Compared on column:", merge_col)
