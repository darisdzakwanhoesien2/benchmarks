import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.utils import detect_lang, Sentence

st.title("Utils Demo")

text = st.text_input("Enter text for language detection:")
if text:
    lang = detect_lang(text)
    st.write(f"Detected language: {lang}")

st.header("Sentence Data Structure Example")
example = Sentence(text="Example sentence.", idx=0, section="General", section_type="General", lang="en")
st.json(example.__dict__)