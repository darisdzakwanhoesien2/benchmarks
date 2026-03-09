import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.rule_based import collect_aspects, polarity_basic, tone_basic

st.title("Rule-Based Model Demo")

text = st.text_area("Enter a sentence:")
if text:
    aspects = collect_aspects(text)
    polarity = polarity_basic(text)
    tone = tone_basic(text)
    st.write(f"Aspects: {aspects}")
    st.write(f"Polarity: {polarity}")
    st.write(f"Tone: {tone}")
else:
    st.info("Enter a sentence to see rule-based predictions.")