import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.lexicons import ASPECT_LEX, CANON_PATHS

st.title("Lexicons & Ontology Viewer")

st.header("Aspect Lexicon")
st.json(ASPECT_LEX)

st.header("Canonical Ontology Paths")
st.json(CANON_PATHS)