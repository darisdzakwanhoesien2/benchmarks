
import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.classical_ml import Featureizer
from code.deep_model import SimpleDLModel
from code.explainability import compare_explain
from code.hybrid_model import run_hierarchical_hybrid
from code.lexicons import ASPECT_LEX, CANON_PATHS
from code.rule_based import collect_aspects, polarity_basic, tone_basic
from code.utils import detect_lang, Sentence
import pandas as pd
import torch

st.set_page_config(page_title="ABSA Ontology Modules", layout="wide")
st.title("ABSA Ontology Modules")

text_input = st.text_area("Enter text to process with modules:")


if text_input:
    st.header("Rule-Based Model Demo")
    aspects = collect_aspects(text_input)
    polarity = polarity_basic(text_input)
    tone = tone_basic(text_input)
    st.write(f"Aspects: {aspects}")
    st.write(f"Polarity: {polarity}")
    st.write(f"Tone: {tone}")


    # Classical ML
    st.header("Classical ML Pipeline Demo")
    from code.classical_ml import run_classical_ml
    out_csv, out_df, fig, coef_sent, coef_aspect = run_classical_ml(text_input)
    st.write("Classical ML Output DataFrame:")
    st.dataframe(out_df)
    st.write("Sentiment Coefficients:")
    st.dataframe(coef_sent)
    st.write("Aspect Coefficients:")
    st.dataframe(coef_aspect)

    # Deep Model
    st.header("Deep Model (mBERT) Demo")
    from code.deep_model import run_deep_learning
    out_csv, out_df, fig, interp_df = run_deep_learning(text_input)
    st.write("Deep Model Output DataFrame:")
    st.dataframe(out_df)
    st.write("Interpretability (Top Tokens):")
    st.dataframe(interp_df)

    # Hybrid Model
    st.header("Hybrid Model (Hierarchical + MTL) Demo")
    from code.hybrid_model import run_hierarchical_hybrid
    _, df, fig1, _, _, metrics = run_hierarchical_hybrid(text_input)
    st.write("Output DataFrame:")
    st.dataframe(df)
    st.write("Metrics:", metrics)

    # Explainability Comparison
    st.header("Explainability Dashboard")
    from code.explainability import compare_explain
    df, fig, scatter = compare_explain()
    st.write("Comparison DataFrame:")
    st.dataframe(df)
    if fig:
        st.pyplot(fig)
    if scatter is not None:
        st.plotly_chart(scatter)

