import streamlit as st
import pandas as pd

from utils.metrics import compute_metrics
from utils.alignment import align_by_sentence
from utils.validation import validate_columns

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Metric Analysis",
    layout="wide"
)

st.title("📊 Metric Analysis — Ground Truth vs Prediction")
st.caption(
    "Sentence-level alignment with minimum-count matching "
    "(robust for ESG / NLP pipelines)"
)
st.markdown(
    """
This page evaluates prediction quality against a ground-truth file.

**What this page does**
- aligns sentences across a reference dataset and a prediction dataset
- computes accuracy, precision, recall, and F1 for aspect category, sentiment, and tone
- surfaces mismatches so you can inspect error patterns directly

**What this page expects**
- two CSV files with at least `sentence`, `aspect_category`, `sentiment`, and `tone`

**How to use it**
- upload the ground-truth file on the left and the prediction file on the right
- review alignment coverage before trusting the metrics
- inspect the error table to find systematic label confusion
"""
)

# --------------------------------------------------
# REQUIRED COLUMNS
# --------------------------------------------------
REQUIRED_COLS = [
    "sentence",
    "aspect_category",
    "sentiment",
    "tone"
]

TARGETS = ["aspect_category", "sentiment", "tone"]

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
st.header("1️⃣ Upload Data")

col1, col2 = st.columns(2)

with col1:
    gt_file = st.file_uploader(
        "📥 Ground Truth CSV",
        type=["csv"]
    )

with col2:
    pred_file = st.file_uploader(
        "📤 Prediction CSV",
        type=["csv"]
    )

if not gt_file or not pred_file:
    st.info("Please upload both Ground Truth and Prediction CSV files.")
    st.stop()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
gt_df = pd.read_csv(gt_file)
pred_df = pd.read_csv(pred_file)

gt_df.columns = gt_df.columns.str.lower().str.strip()
pred_df.columns = pred_df.columns.str.lower().str.strip()

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------
missing_gt = validate_columns(gt_df, REQUIRED_COLS)
missing_pred = validate_columns(pred_df, REQUIRED_COLS)

if missing_gt or missing_pred:
    st.error(
        f"""
❌ Missing required columns

Ground Truth missing: {missing_gt}
Prediction missing: {missing_pred}
        """
    )
    st.stop()

st.success(
    f"Loaded {len(gt_df)} GT rows and {len(pred_df)} Prediction rows"
)

# --------------------------------------------------
# SENTENCE ALIGNMENT
# --------------------------------------------------
st.header("2️⃣ Sentence Alignment")

aligned_df = align_by_sentence(gt_df, pred_df)

if aligned_df.empty:
    st.error(
        "❌ No overlapping sentences found between Ground Truth and Prediction."
    )
    st.stop()

coverage_gt = len(aligned_df) / len(gt_df) * 100
coverage_pred = len(aligned_df) / len(pred_df) * 100

st.success(
    f"Aligned {len(aligned_df)} rows "
    f"({coverage_gt:.1f}% of GT, {coverage_pred:.1f}% of Predictions)"
)

with st.expander("🔍 Preview aligned data"):
    st.dataframe(
        aligned_df[
            [
                "sentence",
                "aspect_category_gt",
                "aspect_category_pred",
                "sentiment_gt",
                "sentiment_pred",
                "tone_gt",
                "tone_pred",
            ]
        ].head(20),
        use_container_width=True
    )

# --------------------------------------------------
# METRIC COMPUTATION
# --------------------------------------------------
st.header("3️⃣ Evaluation Metrics")

metric_results = {}

for target in TARGETS:
    metrics = compute_metrics(
        aligned_df[f"{target}_gt"],
        aligned_df[f"{target}_pred"]
    )
    metric_results[target] = metrics

# --------------------------------------------------
# DISPLAY METRICS
# --------------------------------------------------
tabs = st.tabs(
    [
        "Aspect Category",
        "Sentiment",
        "Tone"
    ]
)

for tab, target in zip(tabs, TARGETS):
    with tab:
        st.subheader(f"🎯 {target.replace('_', ' ').title()}")

        m = metric_results[target]

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Accuracy", f"{m['accuracy']:.4f}")
        col2.metric("Precision", f"{m['precision']:.4f}")
        col3.metric("Recall", f"{m['recall']:.4f}")
        col4.metric("F1 Score", f"{m['f1']:.4f}")
        col5.metric("Dropped Rows", m["dropped_rows"])

# --------------------------------------------------
# ERROR ANALYSIS
# --------------------------------------------------
st.header("4️⃣ Error Analysis")

selected_target = st.selectbox(
    "Select target for error inspection",
    TARGETS
)

errors = aligned_df[
    aligned_df[f"{selected_target}_gt"]
    != aligned_df[f"{selected_target}_pred"]
].copy()

errors.rename(
    columns={
        f"{selected_target}_gt": "actual",
        f"{selected_target}_pred": "predicted"
    },
    inplace=True
)

st.write(f"❌ Total errors: {len(errors)}")

if errors.empty:
    st.success("No errors found 🎉")
else:
    st.dataframe(
        errors[
            [
                "sentence",
                "actual",
                "predicted"
            ]
        ],
        use_container_width=True
    )

# --------------------------------------------------
# CONFIDENCE ANALYSIS (OPTIONAL)
# --------------------------------------------------
if "confidence_pred" in aligned_df.columns:
    st.header("5️⃣ Confidence vs Errors")

    err_conf = aligned_df.copy()
    err_conf["is_error"] = (
        err_conf[f"{selected_target}_gt"]
        != err_conf[f"{selected_target}_pred"]
    )

    st.scatter_chart(
        err_conf[["confidence_pred", "is_error"]],
        height=300
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.caption(
    "✔ Sentence-level matching | "
    "✔ Min-count alignment | "
    "✔ Safe categorical evaluation | "
    "✔ Audit-ready metrics"
)
