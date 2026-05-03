import streamlit as st
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import numpy as np

st.title('Scrambled ABSA Mapping Baseline')
add_page_explanation(__file__)

# Load the CSV
df = pd.read_csv('data/ground_truth_windows/absa_mapping_baseline.csv')

# Columns to scramble
cols = ['raw_aspects', 'aspect_categories', 'majority_category', 'sentiments', 'tones', 'avg_confidence']

# Scramble string columns by shuffling their values
scrambled_df = df.copy()
for col in cols:
    if scrambled_df[col].dtype == object:
        scrambled_df[col] = np.random.permutation(scrambled_df[col].values)
    else:
        # For numerical, generate random values between 0 and 1
        scrambled_df[col] = np.random.rand(len(scrambled_df))

# Show the scrambled columns
display_cols = cols
st.dataframe(scrambled_df[display_cols])

st.write('Note: String columns are shuffled, numerical columns are randomized between 0 and 1.')
