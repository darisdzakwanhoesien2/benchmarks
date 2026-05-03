import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import numpy as np
from collections import OrderedDict

st.title('Scrambled ABSA Mapping Baseline')
add_page_explanation(__file__)

# Load the CSV
df = pd.read_csv('data/ground_truth/absa_mapping.csv')

# Load the CSV (correct path and columns for absa_mapping.csv)
cols = ['sentence_norm', 'canonical_aspect', 'majority_category', 'majority_sentiment', 'majority_tone', 'runs_count']

# Define columns to display and scramble
string_cols = ['raw_aspects', 'aspect_categories', 'majority_category', 'sentiments', 'tones']
numeric_cols = ['avg_confidence']
display_cols = ['sentence_norm', 'canonical_aspect', 'majority_category', 'majority_sentiment', 'majority_tone', 'runs_count'] + string_cols + numeric_cols

# Ensure display_cols has unique column names
display_cols = ['sentence_norm', 'canonical_aspect', 'majority_category', 'majority_sentiment', 'majority_tone', 'runs_count'] + string_cols + numeric_cols
# Remove duplicates while preserving order
unique_display_cols = list(OrderedDict.fromkeys(display_cols))

# Scramble string columns by shuffling their values, randomize numeric columns
shuffle = st.button('Shuffle Data')

scrambled_df = df.copy()
if shuffle:
    random_state = np.random.RandomState()
    for col in string_cols + numeric_cols:
        if col in scrambled_df.columns:
            # Shuffle only within the column, do not cross columns
            scrambled_df.loc[:, col] = random_state.permutation(scrambled_df[col].values)

final_display_cols = [col for col in unique_display_cols if col in scrambled_df.columns]
st.dataframe(scrambled_df[final_display_cols])

st.write('Note: Shuffle only randomizes values within each column, not across columns. Column structure is preserved.')
