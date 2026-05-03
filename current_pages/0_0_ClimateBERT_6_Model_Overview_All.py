import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.climatebert_analysis import merge_ground_truth


st.title("ClimateBERT All Models Visualization")

# Load merged dataset
df = merge_ground_truth()

if df.empty:

    st.warning("No ClimateBERT parsed data found")
    st.stop()


# =====================================================
# GLOBAL LEADERBOARD
# =====================================================

st.header("Model Leaderboard")

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

fig_acc = px.bar(
    metrics_df,
    x="model",
    y="accuracy",
    color="accuracy",
    title="Accuracy by Model"
)

st.plotly_chart(fig_acc, use_container_width=True)


# =====================================================
# GLOBAL CONFIDENCE DISTRIBUTION
# =====================================================

st.header("Confidence Distribution (All Models)")

fig_conf = px.box(
    success_df,
    x="model",
    y="confidence",
    title="Confidence Distribution Across Models"
)

st.plotly_chart(fig_conf, use_container_width=True)


# =====================================================
# GLOBAL LABEL DISTRIBUTION
# =====================================================

st.header("Label Distribution by Model")

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

st.plotly_chart(fig_label, use_container_width=True)

st.header("Label Distribution by Sentiment")

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

st.plotly_chart(fig_label, use_container_width=True)



# =====================================================
# PER MODEL TABS
# =====================================================

st.header("Per-Model Deep Dive")

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

        correct = (
            model_df.predicted_label ==
            model_df.true_sentiment
        ).sum()

        accuracy = correct / success if success else 0

        avg_conf = model_df.confidence.mean()

        col1, col2, col3 = st.columns(3)

        col1.metric("Accuracy", f"{accuracy:.2%}")
        col2.metric("Predictions", success)
        col3.metric("Avg Confidence", f"{avg_conf:.2f}")

        # Raw data
        st.subheader("Predictions Table")

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

        fig_hist = px.histogram(
            model_df,
            x="confidence",
            nbins=30
        )

        st.plotly_chart(fig_hist, use_container_width=True)


        # Confusion Matrix
        st.subheader("Confusion Matrix")

        cm = pd.crosstab(
            model_df.true_sentiment,
            model_df.predicted_label
        )

        fig_cm = px.imshow(
            cm,
            text_auto=True,
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig_cm)


        # Label Distribution
        st.subheader("Label Distribution")

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

        st.plotly_chart(fig_bar, use_container_width=True)





# =====================================================
# EXPORT ALL
# =====================================================

st.header("Export")

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