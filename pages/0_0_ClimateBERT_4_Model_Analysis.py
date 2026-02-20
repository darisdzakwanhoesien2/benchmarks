import streamlit as st
import pandas as pd
import plotly.express as px

from utils.climatebert_analysis import (
    merge_ground_truth,
    compute_model_metrics,
    confidence_distribution,
    model_error_analysis
)


st.title("ClimateBERT Model Analysis")

# Load merged dataset
df = merge_ground_truth()

if df.empty:

    st.warning("No parsed ClimateBERT data found")

    st.stop()


# ======================
# Overview metrics
# ======================

st.header("Overview")

total_predictions = len(df)

successful = len(df[df.status == "success"])

coverage = successful / total_predictions if total_predictions else 0

col1, col2, col3 = st.columns(3)

col1.metric("Total Predictions", total_predictions)
col2.metric("Successful Predictions", successful)
col3.metric("Coverage", f"{coverage:.2%}")


# ======================
# Model performance table
# ======================

st.header("Model Performance")

metrics_df = compute_model_metrics(df)

st.dataframe(metrics_df.sort_values("accuracy", ascending=False))


# ======================
# Accuracy bar chart
# ======================

st.subheader("Model Accuracy")

fig = px.bar(
    metrics_df,
    x="model",
    y="accuracy",
    color="accuracy",
    title="Accuracy by Model"
)

st.plotly_chart(fig, use_container_width=True)


# ======================
# Coverage chart
# ======================

st.subheader("Model Coverage")

fig2 = px.bar(
    metrics_df,
    x="model",
    y="coverage",
    color="coverage",
    title="Coverage by Model"
)

st.plotly_chart(fig2, use_container_width=True)


# ======================
# Confidence distribution
# ======================

st.header("Confidence Distribution")

conf_df = confidence_distribution(df)

fig3 = px.box(
    conf_df,
    x="model",
    y="confidence",
    title="Confidence Distribution per Model"
)

st.plotly_chart(fig3, use_container_width=True)


# ======================
# Error analysis
# ======================

st.header("Error Analysis")

errors = model_error_analysis(df)

if not errors.empty:

    st.dataframe(errors)

else:

    st.success("No model errors")


# ======================
# Confusion matrix
# ======================

st.header("Confusion Matrix")

model_choice = st.selectbox(
    "Select Model",
    df.model.unique()
)

subset = df[
    (df.model == model_choice) &
    (df.status == "success")
]

if not subset.empty:

    cm = pd.crosstab(
        subset.true_sentiment,
        subset.predicted_label
    )

    fig4 = px.imshow(
        cm,
        text_auto=True,
        title=f"Confusion Matrix: {model_choice}"
    )

    st.plotly_chart(fig4)

else:

    st.warning("No valid predictions for selected model")


# ======================
# Raw data explorer
# ======================

st.header("Raw Data Explorer")

st.dataframe(df)


# ======================
# Export
# ======================

st.header("Export Results")

st.download_button(
    "Download Metrics CSV",
    metrics_df.to_csv(index=False),
    "climatebert_model_metrics.csv"
)

st.download_button(
    "Download Full Analysis CSV",
    df.to_csv(index=False),
    "climatebert_full_analysis.csv"
)

# import streamlit as st
# import pandas as pd
# import os


# DATA_PATH = "data/ground_truth/climatebert_absa_combined.csv"


# st.title("ClimateBERT Model Analysis")


# if not os.path.exists(DATA_PATH):

#     st.error("Combined dataset not found.")

#     st.stop()


# df = pd.read_csv(DATA_PATH)


# st.subheader("Dataset Preview")

# st.dataframe(df)


# # Detect valid label columns safely
# model_label_cols = []

# for col in df.columns:

#     if col.endswith("_label"):
#         model_label_cols.append(col)


# st.write("Detected model label columns:")

# st.write(model_label_cols)


# if len(model_label_cols) == 0:

#     st.error(
#         "No model label columns found.\n"
#         "Run merge_climatebert_absa.py first."
#     )

#     st.stop()


# selected_model = st.selectbox(
#     "Select model",
#     model_label_cols
# )


# if selected_model:

#     st.subheader("Label Distribution")

#     label_counts = (
#         df[selected_model]
#         .dropna()
#         .value_counts()
#     )

#     st.bar_chart(label_counts)


#     confidence_col = selected_model.replace(
#         "_label",
#         "_confidence"
#     )

#     if confidence_col in df.columns:

#         st.subheader("Confidence Distribution")

#         conf_counts = (
#             df[confidence_col]
#             .dropna()
#             .value_counts()
#         )

#         st.bar_chart(conf_counts)


#     status_col = selected_model.replace(
#         "_label",
#         "_status"
#     )

#     if status_col in df.columns:

#         success_rate = (
#             df[status_col] == "success"
#         ).mean()

#         st.metric(
#             "Success Rate",
#             f"{success_rate:.2%}"
#         )

# import streamlit as st
# import pandas as pd


# DATA_PATH = "data/ground_truth/absa_mapping.csv"


# st.title("ClimateBERT Model Analysis")


# @st.cache_data
# def load_data():
#     return pd.read_csv(DATA_PATH)


# df = load_data()


# # Show dataset
# st.subheader("Dataset preview")

# st.dataframe(df)


# # Show available model columns
# st.subheader("Detected model outputs")

# model_label_cols = [
#     col for col in df.columns
#     if col.endswith("_label")
# ]


# st.write(model_label_cols)


# # Select model
# selected_model = st.selectbox(
#     "Select model",
#     model_label_cols
# )


# # Distribution
# st.subheader("Label distribution")

# label_counts = df[selected_model].value_counts()

# st.bar_chart(label_counts)


# # Confidence distribution
# confidence_col = selected_model.replace("_label", "_confidence")

# if confidence_col in df.columns:

#     st.subheader("Confidence distribution")

#     st.bar_chart(
#         df[confidence_col].value_counts()
#     )


# # Success rate
# status_col = selected_model.replace("_label", "_status")

# if status_col in df.columns:

#     success_rate = (
#         df[status_col] == "success"
#     ).mean()

#     st.metric(
#         "Success Rate",
#         f"{success_rate:.2%}"
#     )

# import streamlit as st
# import pandas as pd


# st.title("ClimateBERT Model Analysis")

# df = pd.read_csv(
#     "data/ground_truth/absa_mapping.csv"
# )

# st.dataframe(df)


# st.subheader("Sentiment distribution")

# sentiment_counts = df["climate-sentiment_label"].value_counts()

# st.bar_chart(sentiment_counts)


# st.subheader("Confidence distribution")

# st.histogram(
#     df["climate-sentiment_confidence"]
# )