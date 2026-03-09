import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.classical_ml import Featureizer

st.title("Classical ML Pipeline Demo")

uploaded_file = st.file_uploader("Upload CSV for Training", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Sample Data:", df.head())
    feat = Featureizer().fit(df)
    X = feat.transform(df)
    st.write(f"Feature matrix shape: {X.shape}")
    st.write("Feature names:", feat.feature_names() if hasattr(feat, 'feature_names') else "N/A")
    st.success("Featureizer fitted and transformed!")
else:
    st.info("Please upload a CSV file with a 'Sentence_Text' column.")