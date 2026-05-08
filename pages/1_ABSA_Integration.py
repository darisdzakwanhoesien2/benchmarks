import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import json

st.title("ABSA Mapping with ClimateBERT Results")
add_page_explanation(__file__)

PAGE_DIR = Path(__file__).resolve().parent
BENCHMARK_ROOT = PAGE_DIR.parent
ABSA_MAPPING_CANDIDATES = [
    Path("/home/ubuntu/apps/benchmarks/data/ground_truth/absa_mapping.csv"),
    BENCHMARK_ROOT / "data" / "ground_truth" / "absa_mapping.csv",
]
CLIMATEBERT_PARSED_CANDIDATES = [
    Path("/home/ubuntu/apps/benchmarks/data/ground_truth/climatebert_parsed.json"),
    BENCHMARK_ROOT / "data" / "ground_truth" / "climatebert_parsed.json",
]
ABSA_MAPPING_PATH = next(
    (path for path in ABSA_MAPPING_CANDIDATES if path.exists()),
    ABSA_MAPPING_CANDIDATES[0],
)
CLIMATEBERT_PARSED_PATH = next(
    (path for path in CLIMATEBERT_PARSED_CANDIDATES if path.exists()),
    CLIMATEBERT_PARSED_CANDIDATES[0],
)

# Load ABSA mapping
if not ABSA_MAPPING_PATH.exists():
    st.error(f"ABSA mapping CSV not found at `{ABSA_MAPPING_PATH}`.")
    st.stop()
absa_df = pd.read_csv(ABSA_MAPPING_PATH)
st.caption(f"ABSA mapping: `{ABSA_MAPPING_PATH}`")

# Load ClimateBERT parsed results
if CLIMATEBERT_PARSED_PATH.exists():
    with open(CLIMATEBERT_PARSED_PATH, 'r') as f:
        climatebert_results = json.load(f)
    st.caption(f"ClimateBERT parsed results: `{CLIMATEBERT_PARSED_PATH}`")
else:
    climatebert_results = []
    st.warning(
        f"ClimateBERT parsed JSON not found at `{CLIMATEBERT_PARSED_PATH}`. "
        "Showing ABSA mapping without ClimateBERT joined columns."
    )

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
    if 'climate-commitment_label' in filtered_df.columns:
        commitment_counts = filtered_df['climate-commitment_label'].value_counts()
        st.bar_chart(commitment_counts)
    else:
        st.info("No `climate-commitment_label` column is available yet.")
