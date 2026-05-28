import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix, classification_report

import json

st.title("ABSA Mapping Metrics Comparison")
add_page_explanation(__file__)

PAGE_DIR = Path(__file__).resolve().parent
BENCHMARK_ROOT = PAGE_DIR.parent

# File paths
gt_path = BENCHMARK_ROOT / "data" / "ground_truth" / "absa_mapping.csv"
baseline_path = BENCHMARK_ROOT / "data" / "ground_truth" / "absa_mapping_baseline.csv"

source_rows = [
    {
        "source_type": "Ground truth input",
        "path": str(gt_path),
        "used_by": "pd.read_csv(gt_path)",
        "notes": "Primary ABSA labels for mac/ground_truth variant.",
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
        "used_by": "map_to_cluster for majority_sentiment",
        "notes": "Used in majority sentiment clustered metrics.",
    },
    {
        "source_type": "Tone mapping",
        "path": str(BENCHMARK_ROOT / 'data' / 'tone_category.json'),
        "used_by": "map_to_cluster for majority_tone",
        "notes": "Used in majority tone clustered metrics.",
    },
    {
        "source_type": "Upstream generator page",
        "path": str(PAGE_DIR / '0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py'),
        "used_by": "Reference only",
        "notes": "Ground truth batch page for data/ground_truth dataset family.",
    },
]

st.subheader("Data Sources")
st.caption("Editable provenance table for this page inputs and supporting mappings.")
st.data_editor(
    pd.DataFrame(source_rows),
    num_rows="dynamic",
    use_container_width=True,
    key="absa_metrics_sources_mac_editor",
)

# Load data
gt = pd.read_csv(gt_path)
baseline = pd.read_csv(baseline_path)

# Load mapping for category clustering
with open(BENCHMARK_ROOT / "data" / "mapping_category.json", "r") as f:
    category_mapping = json.load(f)

def normalize_labels(series: pd.Series) -> pd.Series:
    return (
        series.fillna("none")
        .astype(str)
        .str.strip()
        .replace({"": "none", "nan": "none", "NaN": "none", "None": "none"})
    )

# Helper: Compute metrics and show results
def compute_metrics(y_true, y_pred, label):
    st.subheader(f"{label} Metrics")
    y_true = normalize_labels(pd.Series(y_true)).reset_index(drop=True)
    y_pred = normalize_labels(pd.Series(y_pred)).reset_index(drop=True)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    # Calculate and display F1, Precision, Recall (weighted)
    f1 = report['weighted avg']['f1-score']
    precision = report['weighted avg']['precision']
    recall = report['weighted avg']['recall']
    st.write(f"F1 Score: {f1:.3f}")
    st.write(f"Precision: {precision:.3f}")
    st.write(f"Recall: {recall:.3f}")
    st.write("Classification Report:")
    st.dataframe(pd.DataFrame(report).transpose())
    cm_labels = sorted(list(set(y_true) | set(y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=cm_labels)
    st.write("Confusion Matrix:")
    st.dataframe(pd.DataFrame(cm, index=cm_labels, columns=cm_labels))
    # TP, FP, FN per class
    tp_fp_fn_data = []
    for i, class_label in enumerate(cm_labels):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tp_fp_fn_data.append({"Class": class_label, "TP": tp, "FP": fp, "FN": fn})
    st.write("TP/FP/FN per class:")
    st.dataframe(pd.DataFrame(tp_fp_fn_data))

# Helper: Map categories to clusters for any mapping
def map_to_cluster(series, mapping):
    return normalize_labels(series).apply(lambda x: mapping.get(str(x), "none"))

# Improved: Robust merge, error handling, flexible metrics, and clearer output
def safe_merge(gt, baseline, keys):
    for key in keys:
        if key in gt.columns and key in baseline.columns:
            return pd.merge(gt, baseline, on=key, suffixes=("_gt", "_baseline"), how="inner"), key
    st.error(f"None of the merge keys {keys} found in both files.")
    return None, None

# Use 'sentence_norm' as the merge key and compare category, sentiment, and tone
merge_keys = ["sentence_norm"]
merged, merge_col = safe_merge(gt, baseline, merge_keys)
if merged is None:
    st.stop()

# Compare majority_category
if "majority_category_gt" in merged.columns and "majority_category_baseline" in merged.columns:
    cat_gt = normalize_labels(merged["majority_category_gt"])
    cat_baseline = normalize_labels(merged["majority_category_baseline"])
    cat_gt_cluster = map_to_cluster(cat_gt, category_mapping)
    cat_baseline_cluster = map_to_cluster(cat_baseline, category_mapping)
    compute_metrics(cat_gt, cat_baseline, "Majority Category (Original)")
    compute_metrics(cat_gt_cluster, cat_baseline_cluster, "Majority Category (Clustered)")

# Compare majority_sentiment
if "majority_sentiment_gt" in merged.columns and "majority_sentiment_baseline" in merged.columns:
    with open(BENCHMARK_ROOT / "data" / "sentiment_category.json", "r") as f:
        sentiment_mapping = json.load(f)
    sent_gt = normalize_labels(merged["majority_sentiment_gt"])
    sent_baseline = normalize_labels(merged["majority_sentiment_baseline"])
    compute_metrics(sent_gt, sent_baseline, "Majority Sentiment (Original)")
    compute_metrics(map_to_cluster(sent_gt, sentiment_mapping), map_to_cluster(sent_baseline, sentiment_mapping), "Majority Sentiment (Clustered)")

# Compare majority_tone
if "majority_tone_gt" in merged.columns and "majority_tone_baseline" in merged.columns:
    with open(BENCHMARK_ROOT / "data" / "tone_category.json", "r") as f:
        tone_mapping = json.load(f)
    tone_gt = normalize_labels(merged["majority_tone_gt"])
    tone_baseline = normalize_labels(merged["majority_tone_baseline"])
    compute_metrics(tone_gt, tone_baseline, "Majority Tone (Original)")
    compute_metrics(map_to_cluster(tone_gt, tone_mapping), map_to_cluster(tone_baseline, tone_mapping), "Majority Tone (Clustered)")

st.write("---")
st.write(f"Compared on column: {merge_col}")
