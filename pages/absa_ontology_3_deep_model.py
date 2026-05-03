import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import torch
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.deep_model import SimpleDLModel

st.title("Deep Model (mBERT) Demo")
add_page_explanation(__file__)

st.write("This demo loads a minimal mBERT-based model for ESG ABSA.")

try:
    model = SimpleDLModel()
    st.write("Model loaded:", model)
    st.success("Model initialized!")
except Exception as e:
    st.error(f"Failed to load model: {e}")