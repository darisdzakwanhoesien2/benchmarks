import streamlit as st
import pandas as pd
import plotly.express as px

from utils.climatebert_analysis import merge_ground_truth


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ClimateBERT Full Visualization",
    layout="wide"
)

st.title("ClimateBERT Full Model Visualization")


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = merge_ground_truth()

    df = df[df["status"] == "success"]

    df["confidence"] = pd.to_numeric(
        df["confidence"],
        errors="coerce"
    )

    df = df.dropna(subset=["confidence"])

    return df


df = load_data()


if df.empty:

    st.error("No ClimateBERT data found.")
    st.stop()


# =========================================================
# SIDEBAR DEBUG INFO
# =========================================================

st.sidebar.header("Dataset Info")

st.sidebar.write("Total rows:", len(df))
st.sidebar.write("Unique texts:", df["text"].nunique())
st.sidebar.write("Models:", df["model"].nunique())


# =========================================================
# LEADERBOARD
# =========================================================

st.header("Leaderboard")


metrics = (

    df.groupby("model")

    .agg(
        total_predictions=("text", "count"),
        avg_confidence=("confidence", "mean")
    )

    .reset_index()

)


metrics = metrics.sort_values(
    "total_predictions",
    ascending=False
)


st.dataframe(
    metrics,
    use_container_width=True
)


# =========================================================
# GLOBAL DISTRIBUTIONS
# =========================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader("Predicted Label Distribution")

    pred_dist = (

        df.groupby(["model", "predicted_label"])
        .size()
        .reset_index(name="count")

    )

    fig = px.bar(
        pred_dist,
        x="model",
        y="count",
        color="predicted_label",
        barmode="stack",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    st.subheader("True Sentiment Distribution")

    true_dist = (

        df.groupby(["model", "true_sentiment"])
        .size()
        .reset_index(name="count")

    )

    fig = px.bar(
        true_dist,
        x="model",
        y="count",
        color="true_sentiment",
        barmode="stack",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# CONFIDENCE DISTRIBUTION
# =========================================================

st.subheader("Confidence Distribution Across Models")

fig = px.box(
    df,
    x="model",
    y="confidence",
    height=600
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# MODEL SELECTION
# =========================================================

st.header("Per-Model Deep Dive")

models = sorted(df["model"].unique())

selected_model = st.selectbox(
    "Select Model",
    models
)

model_df = df[df["model"] == selected_model]


# =========================================================
# MODEL METRICS
# =========================================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Predictions",
    len(model_df)
)

col2.metric(
    "Avg Confidence",
    round(model_df["confidence"].mean(), 3)
)

col3.metric(
    "Unique texts",
    model_df["text"].nunique()
)


# =========================================================
# CONFIDENCE HISTOGRAM
# =========================================================

st.subheader("Confidence Histogram")

fig = px.histogram(
    model_df,
    x="confidence",
    nbins=50,
    height=400
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# CONFUSION MATRIX
# =========================================================

st.subheader("Confusion Matrix")

cm = pd.crosstab(
    model_df["true_sentiment"],
    model_df["predicted_label"]
)

fig = px.imshow(
    cm,
    text_auto=True,
    height=500
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# LABEL DISTRIBUTION
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Predicted Label Distribution")

    fig = px.bar(
        model_df["predicted_label"]
        .value_counts()
        .reset_index(),
        x="index",
        y="predicted_label",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    st.subheader("True Label Distribution")

    fig = px.bar(
        model_df["true_sentiment"]
        .value_counts()
        .reset_index(),
        x="index",
        y="true_sentiment",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# DATA TABLE
# =========================================================

st.subheader("Prediction Explorer")

st.dataframe(
    model_df[
        [
            "text",
            "true_sentiment",
            "predicted_label",
            "confidence"
        ]
    ],
    height=500
)


# =========================================================
# EXPORT
# =========================================================

st.header("Export")

st.download_button(
    "Download Model CSV",
    model_df.to_csv(index=False),
    f"{selected_model}_predictions.csv"
)

st.download_button(
    "Download All CSV",
    df.to_csv(index=False),
    "climatebert_all_predictions.csv"
)