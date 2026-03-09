import streamlit as st
import pandas as pd
import torch
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.deep_model import SimpleDLModel

st.title("Deep Model (mBERT) Demo")

st.write("This demo loads a minimal mBERT-based model for ESG ABSA.")

try:
    model = SimpleDLModel()
    st.write("Model loaded:", model)
    st.success("Model initialized!")
except Exception as e:
    st.error(f"Failed to load model: {e}")