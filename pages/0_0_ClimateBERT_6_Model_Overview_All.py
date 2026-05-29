import streamlit as st
from pathlib import Path
import sys

PAGE_DIR = Path(__file__).resolve().parent
ROOT = PAGE_DIR.parent
sys.path.insert(0, str(PAGE_DIR))
sys.path.insert(0, str(ROOT / "utils"))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from climatebert_analysis import merge_ground_truth

REVISION_DIR = ROOT / "results" / "revision_analysis"
CLIMATE_COMMITMENT_ANNOTATION_PATH = REVISION_DIR / "climate_commitment_manual_annotations.csv"


def _norm_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()


def load_climate_commitment_annotations() -> pd.DataFrame:
    if not CLIMATE_COMMITMENT_ANNOTATION_PATH.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(CLIMATE_COMMITMENT_ANNOTATION_PATH).fillna("")
    except Exception:
        return pd.DataFrame()
    required = {"text", "human_climate_commitment"}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    out = df.copy()
    out["text"] = _norm_text(out["text"])
    out["human_climate_commitment"] = (
        out["human_climate_commitment"]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    return out


def build_climate_commitment_seed(model_df: pd.DataFrame) -> pd.DataFrame:
    seed = model_df[["text", "predicted_label", "confidence"]].copy()
    seed["text"] = _norm_text(seed["text"])
    seed = seed.drop_duplicates(subset=["text"]).sort_values("text")
    seed["human_climate_commitment"] = ""
    seed["review_notes"] = ""
    return seed[["text", "predicted_label", "confidence", "human_climate_commitment", "review_notes"]]


def compute_metric_context(model_df: pd.DataFrame, model: str) -> dict[str, object]:
    metric = {
        "label": "Accuracy",
        "value": None,
        "help": "Exact match between predicted label and true_sentiment.",
        "usable_rows": len(model_df),
    }
    if model != "climate-commitment":
        correct = (model_df["predicted_label"] == model_df["true_sentiment"]).sum()
        metric["value"] = correct / len(model_df) if len(model_df) else 0.0
        return metric

    annotations = load_climate_commitment_annotations()
    if not annotations.empty:
        merged = model_df.copy()
        merged["text"] = _norm_text(merged["text"])
        merged["predicted_label_norm"] = merged["predicted_label"].astype(str).str.strip().str.lower()
        merged = merged.merge(
            annotations[["text", "human_climate_commitment"]],
            on="text",
            how="left",
        )
        usable = merged[
            merged["human_climate_commitment"].isin(["yes", "no", "true", "false", "1", "0"])
        ].copy()
        if not usable.empty:
            usable["human_climate_commitment"] = usable["human_climate_commitment"].replace(
                {"true": "yes", "1": "yes", "false": "no", "0": "no"}
            )
            metric["label"] = "Manual Accuracy"
            metric["value"] = (
                usable["predicted_label_norm"] == usable["human_climate_commitment"]
            ).mean()
            metric["help"] = (
                "Accuracy against manual binary climate-commitment annotations in "
                f"{CLIMATE_COMMITMENT_ANNOTATION_PATH.name}."
            )
            metric["usable_rows"] = len(usable)
            return metric

    commitment_alignment = (
        (model_df["true_sentiment"].astype(str).str.strip().str.lower() == "commitment")
        & (model_df["predicted_label"].astype(str).str.strip().str.lower() == "yes")
    ).sum()
    commitment_total = (
        model_df["true_sentiment"].astype(str).str.strip().str.lower() == "commitment"
    ).sum()
    metric["label"] = "Commitment Alignment"
    metric["value"] = commitment_alignment / commitment_total if commitment_total else None
    metric["help"] = (
        "Proxy construct-alignment only: share of rows with true_sentiment='commitment' "
        "that the climate-commitment model predicted as 'yes'. This is not human-label accuracy."
    )
    metric["usable_rows"] = int(commitment_total)
    return metric


st.title("ClimateBERT All Models Visualization")
add_page_explanation(__file__)

# Load merged dataset
df = merge_ground_truth()

if df.empty:

    st.warning("No ClimateBERT parsed data found")
    st.stop()


# =====================================================
# GLOBAL LEADERBOARD
# =====================================================

st.header("Model Leaderboard")
add_section_explanation("Model Leaderboard")

success_df = df[df.status == "success"].copy()

metrics = []

for model in sorted(success_df.model.unique()):

    model_df = success_df[success_df.model == model]

    total = len(df[df.model == model])
    success = len(model_df)

    coverage = success / total if total else 0

    correct = (
        model_df.predicted_label ==
        model_df.true_sentiment
    ).sum()

    accuracy = correct / success if success else 0

    avg_conf = model_df.confidence.mean()

    metrics.append({

        "model": model,
        "accuracy": accuracy,
        "coverage": coverage,
        "avg_confidence": avg_conf,
        "total_predictions": total

    })


metrics_df = pd.DataFrame(metrics)

metrics_df = metrics_df.sort_values(
    "accuracy",
    ascending=False
)

st.dataframe(metrics_df, use_container_width=True)


# =====================================================
# GLOBAL ACCURACY BAR
# =====================================================

st.header("Accuracy Comparison")
add_section_explanation("Accuracy Comparison")

fig_acc = px.bar(
    metrics_df,
    x="model",
    y="accuracy",
    color="accuracy",
    title="Accuracy by Model"
)

st.plotly_chart(fig_acc, use_container_width=True, key="accuracy_comparison_chart")


# =====================================================
# GLOBAL CONFIDENCE DISTRIBUTION
# =====================================================

st.header("Confidence Distribution (All Models)")
add_section_explanation("Confidence Distribution (All Models)")

fig_conf = px.box(
    success_df,
    x="model",
    y="confidence",
    title="Confidence Distribution Across Models"
)

st.plotly_chart(fig_conf, use_container_width=True, key="confidence_distribution_all_models_chart")


# =====================================================
# GLOBAL LABEL DISTRIBUTION
# =====================================================

st.header("Label Distribution by Model")
add_section_explanation("Label Distribution by Model")

label_dist = (
    success_df
    .groupby(["model", "predicted_label"])
    .size()
    .reset_index(name="count")
)

fig_label = px.bar(
    label_dist,
    x="model",
    y="count",
    color="predicted_label",
    title="Predicted Label Distribution per Model"
)

st.plotly_chart(fig_label, use_container_width=True, key="predicted_label_distribution_by_model_chart")

st.header("Label Distribution by Sentiment")
add_section_explanation("Label Distribution by Sentiment")

label_dist = (
    success_df
    .groupby(["model", "true_sentiment"])
    .size()
    .reset_index(name="count")
)

fig_label = px.bar(
    label_dist,
    x="model",
    y="count",
    color="true_sentiment",
    title="Predicted Label Distribution per Model"
)

st.plotly_chart(fig_label, use_container_width=True, key="true_sentiment_distribution_by_model_chart")



# =====================================================
# PER MODEL TABS
# =====================================================

st.header("Per-Model Deep Dive")
add_section_explanation("Per-Model Deep Dive")

models = sorted(success_df.model.unique())

tabs = st.tabs(models)


for i, model in enumerate(models):

    with tabs[i]:

        model_df = success_df[
            success_df.model == model
        ].copy()

        st.subheader(f"{model} Overview")

        total = len(df[df.model == model])
        success = len(model_df)

        avg_conf = model_df.confidence.mean()
        metric_context = compute_metric_context(model_df, model)

        col1, col2, col3 = st.columns(3)

        metric_value = metric_context["value"]
        col1.metric(
            metric_context["label"],
            f"{metric_value:.2%}" if metric_value is not None else "N/A"
        )
        col2.metric("Predictions", success)
        col3.metric("Avg Confidence", f"{avg_conf:.2f}")
        st.caption(
            f"{metric_context['help']} Usable rows: {metric_context['usable_rows']:,}."
        )

        if model == "climate-commitment":
            st.info(
                "The climate-commitment model uses a binary yes/no label space, so direct comparison "
                "to tone labels like commitment/action/outcome is invalid. Use manual climate-commitment "
                "annotations to measure real accuracy."
            )
            annotation_seed = build_climate_commitment_seed(model_df)
            st.download_button(
                "Download manual annotation seed",
                annotation_seed.to_csv(index=False),
                file_name="climate_commitment_manual_annotations_seed.csv",
                mime="text/csv",
            )
            st.caption(
                "To enable manual accuracy, save a reviewed CSV at "
                f"`{CLIMATE_COMMITMENT_ANNOTATION_PATH}` with columns "
                "`text` and `human_climate_commitment` using `yes` or `no`."
            )

        # Raw data
        st.subheader("Predictions Table")
        add_section_explanation("Predictions Table")

        st.dataframe(

            model_df[
                [
                    "text",
                    "true_sentiment",
                    "predicted_label",
                    "confidence"
                ]
            ],

            height=300

        )
        # Confidence Histogram
        st.subheader("Confidence Histogram")
        add_section_explanation("Confidence Histogram")

        fig_hist = px.histogram(
            model_df,
            x="confidence",
            nbins=30
        )

        st.plotly_chart(fig_hist, use_container_width=True, key=f"{model}_confidence_histogram_chart")


        # Confusion Matrix
        st.subheader("Confusion Matrix")
        add_section_explanation("Confusion Matrix")

        cm = pd.crosstab(
            model_df.true_sentiment,
            model_df.predicted_label
        )

        fig_cm = px.imshow(
            cm,
            text_auto=True,
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig_cm, use_container_width=True, key=f"{model}_confusion_matrix_chart")


        # Label Distribution
        st.subheader("Label Distribution")
        add_section_explanation("Label Distribution")

        label_counts = (
            model_df.predicted_label
            .value_counts()
            .reset_index()
        )

        label_counts.columns = [
            "label",
            "count"
        ]

        fig_bar = px.bar(
            label_counts,
            x="label",
            y="count"
        )

        st.plotly_chart(fig_bar, use_container_width=True, key=f"{model}_label_distribution_chart")





# =====================================================
# EXPORT ALL
# =====================================================

st.header("Export")
add_section_explanation("Export")

st.download_button(
    "Download All Predictions CSV",
    success_df.to_csv(index=False),
    "climatebert_all_predictions.csv"
)

st.download_button(
    "Download Leaderboard CSV",
    metrics_df.to_csv(index=False),
    "climatebert_leaderboard.csv"
)
