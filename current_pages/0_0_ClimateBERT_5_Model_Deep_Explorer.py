import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.climatebert_analysis import merge_ground_truth


st.title("ClimateBERT Model Deep Explorer")

# Load merged dataset
df = merge_ground_truth()

if df.empty:

    st.warning("No ClimateBERT parsed data found")
    st.stop()


# =============================
# Select model
# =============================

models = sorted(df.model.unique())

selected_model = st.selectbox(
    "Select ClimateBERT Model",
    models
)

model_df = df[df.model == selected_model]


# =============================
# Overview
# =============================

st.header("Model Overview")

total = len(model_df)

success_df = model_df[model_df.status == "success"]

success = len(success_df)

coverage = success / total if total else 0

correct = (
    success_df.predicted_label ==
    success_df.true_sentiment
).sum()

accuracy = correct / success if success else 0

avg_conf = success_df.confidence.mean() if success else 0


col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", total)
col2.metric("Coverage", f"{coverage:.2%}")
col3.metric("Accuracy", f"{accuracy:.2%}")
col4.metric("Avg Confidence", f"{avg_conf:.2f}")


# =============================
# Label Distribution
# =============================

st.header("Predicted Label Distribution")

label_counts = success_df.predicted_label.value_counts()

fig = px.bar(
    x=label_counts.index,
    y=label_counts.values,
    labels={"x": "Label", "y": "Count"},
    title=f"{selected_model} Label Distribution"
)

st.plotly_chart(fig, use_container_width=True)


# =============================
# Confidence Histogram
# =============================

st.header("Confidence Distribution")

fig2 = px.histogram(
    success_df,
    x="confidence",
    nbins=30,
    title=f"{selected_model} Confidence Histogram"
)

st.plotly_chart(fig2, use_container_width=True)


# =============================
# Confidence vs Accuracy Scatter
# =============================

st.header("Confidence vs Prediction")

success_df["correct"] = (
    success_df.predicted_label ==
    success_df.true_sentiment
)

fig3 = px.scatter(
    success_df,
    x="confidence",
    y="correct",
    title=f"{selected_model} Confidence vs Correctness",
    color="correct"
)

st.plotly_chart(fig3, use_container_width=True)


# =============================
# Confusion Matrix
# =============================

st.header("Confusion Matrix")

cm = pd.crosstab(
    success_df.true_sentiment,
    success_df.predicted_label
)

fig4 = px.imshow(
    cm,
    text_auto=True,
    color_continuous_scale="Blues",
    title=f"{selected_model} Confusion Matrix"
)

st.plotly_chart(fig4)


# =============================
# Prediction Table
# =============================

st.header("Prediction Explorer")

show_errors = st.checkbox("Show only incorrect predictions")

table_df = success_df.copy()

if show_errors:

    table_df = table_df[
        table_df.predicted_label != table_df.true_sentiment
    ]


st.dataframe(
    table_df[[
        "text",
        "true_sentiment",
        "predicted_label",
        "confidence"
    ]],
    height=400
)


# =============================
# Confidence Box Plot
# =============================

st.header("Confidence by Label")

fig5 = px.box(
    success_df,
    x="predicted_label",
    y="confidence",
    title=f"{selected_model} Confidence by Label"
)

st.plotly_chart(fig5)


# =============================
# Error Analysis
# =============================

st.header("Error Analysis")

errors = model_df[model_df.status == "error"]

if len(errors) > 0:

    st.dataframe(errors)

else:

    st.success("No runtime errors for this model")


# =============================
# Export
# =============================

st.header("Export")

st.download_button(
    "Download Model CSV",
    success_df.to_csv(index=False),
    f"{selected_model}_predictions.csv"
)


# =============================
# Advanced Metrics
# =============================

st.header("Advanced Metrics")

precision = {}
recall = {}

labels = success_df.true_sentiment.unique()

for label in labels:

    tp = len(success_df[
        (success_df.predicted_label == label) &
        (success_df.true_sentiment == label)
    ])

    fp = len(success_df[
        (success_df.predicted_label == label) &
        (success_df.true_sentiment != label)
    ])

    fn = len(success_df[
        (success_df.predicted_label != label) &
        (success_df.true_sentiment == label)
    ])

    precision[label] = tp / (tp + fp) if tp + fp else 0
    recall[label] = tp / (tp + fn) if tp + fn else 0


metric_df = pd.DataFrame({

    "Label": labels,
    "Precision": [precision[l] for l in labels],
    "Recall": [recall[l] for l in labels]

})

st.dataframe(metric_df)