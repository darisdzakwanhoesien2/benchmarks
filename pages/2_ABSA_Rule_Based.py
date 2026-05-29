import streamlit as st
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
PAGES_DIR = Path(__file__).resolve().parent
if str(PAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PAGES_DIR))

loaded_utils = sys.modules.get("utils")
if loaded_utils is not None and not hasattr(loaded_utils, "__path__"):
    del sys.modules["utils"]

from _page_explanations import add_page_explanation, add_section_explanation

from api.absa_client import run_rule
from utils.dataframe import hf_to_df
from utils.visualization import render_plot


st.title("ABSA Rule-Based Ontology")
add_page_explanation(__file__)

space_url = st.text_input(
    "Hugging Face Space URL (optional)",
    value="",
    help="If set, this will override the default HF Space URL / environment variable.",
)

text = st.text_area("Enter ESG Text")


if st.button("Run Rule-Based ABSA"):

    result = run_rule(text, space_url=space_url or None)

    csv_path = result[0]
    preview = hf_to_df(result[1])
    plot = result[2]
    explanations = hf_to_df(result[3])

    st.subheader("Preview")
    add_section_explanation("Preview")
    st.dataframe(preview)

    st.subheader("Visualization")
    add_section_explanation("Visualization")
    render_plot(plot)

    st.subheader("Rule Explanations")
    add_section_explanation("Rule Explanations")
    st.dataframe(explanations)

    st.download_button(
        "Download CSV",
        open(csv_path, "rb"),
        file_name="absa_rule.csv"
    )
