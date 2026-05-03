import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import json

st.title("ABSA Mapping with ClimateBERT Results")
add_page_explanation(__file__)

# Load ABSA mapping
absa_df = pd.read_csv('/workspaces/benchmarks/data/ground_truth/absa_mapping.csv')

# Load ClimateBERT parsed results
with open('/workspaces/benchmarks/data/ground_truth/climatebert_parsed.json', 'r') as f:
    climatebert_results = json.load(f)

# Integrate the data
integrated_data = []
for i, row in absa_df.iterrows():
    entry = row.to_dict()
    if i < len(climatebert_results):
        predictions = climatebert_results[i]['models']
        for model, pred in predictions.items():
            if pred['status'] == 'success':
                entry[f"{model}_label"] = pred['label']
                entry[f"{model}_confidence"] = pred['confidence']
            else:
                entry[f"{model}_label"] = 'error'
                entry[f"{model}_confidence"] = None
    integrated_data.append(entry)

integrated_df = pd.DataFrame(integrated_data)

# Display filters
st.sidebar.header("Filters")
category_filter = st.sidebar.multiselect("Filter by Majority Category", options=integrated_df['majority_category'].unique(), default=[])
sentiment_filter = st.sidebar.multiselect("Filter by Majority Sentiment", options=integrated_df['majority_sentiment'].unique(), default=[])

# Apply filters
filtered_df = integrated_df
if category_filter:
    filtered_df = filtered_df[filtered_df['majority_category'].isin(category_filter)]
if sentiment_filter:
    filtered_df = filtered_df[filtered_df['majority_sentiment'].isin(sentiment_filter)]

st.dataframe(filtered_df)

# Data Distribution
st.header("Data Distribution")
add_section_explanation("Data Distribution")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Majority Category Distribution")
    add_section_explanation("Majority Category Distribution")
    category_counts = filtered_df['majority_category'].value_counts()
    st.bar_chart(category_counts)

with col2:
    st.subheader("Majority Sentiment Distribution")
    add_section_explanation("Majority Sentiment Distribution")
    sentiment_counts = filtered_df['majority_sentiment'].value_counts()
    st.bar_chart(sentiment_counts)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Majority Tone Distribution")
    add_section_explanation("Majority Tone Distribution")
    tone_counts = filtered_df['majority_tone'].value_counts()
    st.bar_chart(tone_counts)

with col4:
    st.subheader("Climate Commitment Label Distribution")
    add_section_explanation("Climate Commitment Label Distribution")
    commitment_counts = filtered_df['climate-commitment_label'].value_counts()
    st.bar_chart(commitment_counts)