import streamlit as st
import pandas as pd
import numpy as np

st.title('Scrambled ABSA Mapping Baseline')

# Load the CSV
df = pd.read_csv('data/ground_truth/absa_mapping.csv')

# Load the CSV (correct path and columns for absa_mapping.csv)
cols = ['sentence_norm', 'canonical_aspect', 'majority_category', 'majority_sentiment', 'majority_tone', 'runs_count']

# Columns to scramble
cols = ['raw_aspects', 'aspect_categories', 'majority_category', 'sentiments', 'tones', 'avg_confidence']

# Scramble string columns by shuffling their values
scrambled_df = df.copy()
for col in cols:
    if col in scrambled_df.columns:
        if scrambled_df[col].dtype == object:
            scrambled_df[col] = np.random.permutation(scrambled_df[col].values)
        else:
            # For numerical, generate random values between 0 and 1
            scrambled_df[col] = np.random.rand(len(scrambled_df))


# Show only columns that exist in the DataFrame
display_cols = [col for col in cols if col in scrambled_df.columns]
st.dataframe(scrambled_df[display_cols])

st.write('Note: String columns are shuffled, numerical columns are randomized between 0 and 1.')
