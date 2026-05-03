import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.climatebert_analysis import merge_ground_truth


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Climate Commitment Analysis",
    layout="wide"
)

st.title("Climate Commitment Model Analysis")


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = merge_ground_truth()

    if df is None or df.empty:
        return pd.DataFrame()

    df = df[df["status"] == "success"].copy()

    df["confidence"] = pd.to_numeric(
        df["confidence"],
        errors="coerce"
    )

    df = df.dropna(subset=["confidence"])

    return df


df = load_data()

if df.empty:

    st.error("No data found.")
    st.stop()


# =========================================================
# MODEL SELECTOR
# =========================================================

models = sorted(df["model"].unique())

selected_model = st.selectbox(
    "Select ClimateBERT Model",
    models
)

model_df = df[df["model"] == selected_model]


# =========================================================
# BASIC METRICS
# =========================================================

st.header("Overview")

total_predictions = len(model_df)

avg_confidence = model_df["confidence"].mean()

accuracy = (
    model_df["true_sentiment"] == model_df["predicted_label"]
).mean()


col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Predictions",
    total_predictions
)

col2.metric(
    "Avg Confidence",
    f"{avg_confidence:.3f}"
)

col3.metric(
    "Accuracy",
    f"{accuracy:.2%}"
)


# =========================================================
# PREDICTED LABEL DISTRIBUTION
# =========================================================

st.header("Predicted Label Distribution")

label_counts = (
    model_df["predicted_label"]
    .value_counts()
    .rename_axis("predicted_label")
    .reset_index(name="count")
)

label_counts["percentage"] = (
    label_counts["count"] / label_counts["count"].sum() * 100
).round(2)


# Summary Metrics
st.subheader("Prediction Summary")

cols = st.columns(len(label_counts))

for i, row in label_counts.iterrows():

    cols[i].metric(
        row["predicted_label"],
        row["count"],
        f"{row['percentage']}%"
    )


# Charts
col1, col2 = st.columns(2)


with col1:

    st.subheader("Bar Chart")

    fig = px.bar(
        label_counts,
        x="predicted_label",
        y="count",
        color="predicted_label",
        text="count",
        height=400
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


with col2:

    st.subheader("Pie Chart")

    fig = px.pie(
        label_counts,
        names="predicted_label",
        values="count",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)


st.dataframe(label_counts, use_container_width=True)


# =========================================================
# CONFIDENCE DISTRIBUTION
# =========================================================

st.header("Confidence Analysis")

col1, col2 = st.columns(2)


with col1:

    st.subheader("Confidence Histogram")

    fig = px.histogram(
        model_df,
        x="confidence",
        nbins=50,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:

    st.subheader("Confidence Box Plot")

    fig = px.box(
        model_df,
        y="confidence",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# TRUE VS PREDICTED DISTRIBUTION
# =========================================================

st.header("True vs Predicted Comparison")

comparison = (
    model_df.groupby(
        ["true_sentiment", "predicted_label"]
    )
    .size()
    .reset_index(name="count")
)

fig = px.bar(
    comparison,
    x="true_sentiment",
    y="count",
    color="predicted_label",
    barmode="group",
    height=500
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# CONFUSION MATRIX
# =========================================================

st.header("Confusion Matrix")

cm = pd.crosstab(
    model_df["true_sentiment"],
    model_df["predicted_label"]
)

fig = px.imshow(
    cm,
    text_auto=True,
    aspect="auto",
    height=500
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# GLOBAL DISTRIBUTION ACROSS MODELS
# =========================================================

st.header("Global Distribution Across Models")

global_dist = (
    df.groupby(["model", "predicted_label"])
    .size()
    .reset_index(name="count")
)

fig = px.bar(
    global_dist,
    x="model",
    y="count",
    color="predicted_label",
    barmode="stack",
    height=500
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# PREDICTION EXPLORER
# =========================================================

st.header("Prediction Explorer")

search = st.text_input("Search text")


filtered_df = model_df

if search:

    filtered_df = model_df[
        model_df["text"]
        .str.contains(search, case=False, na=False)
    ]


st.dataframe(
    filtered_df[
        [
            "text",
            "true_sentiment",
            "predicted_label",
            "confidence"
        ]
    ],
    height=500,
    use_container_width=True
)


# =========================================================
# EXPORT
# =========================================================

st.header("Export")

st.download_button(
    "Download Model Predictions",
    model_df.to_csv(index=False),
    f"{selected_model}_predictions.csv",
    mime="text/csv"
)

st.download_button(
    "Download All Predictions",
    df.to_csv(index=False),
    "all_climate_predictions.csv",
    mime="text/csv"
)