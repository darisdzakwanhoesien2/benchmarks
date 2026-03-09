import streamlit as st
from api.esgdata_client import run_evaluation
from utils.file_handler import render_hf_image


st.title("ESG Evaluation")

space_url = st.text_input(
    "Hugging Face Space URL (optional)",
    value="",
    help="If set, this will override the default HF Space URL / environment variable.",
)

if st.button("Run Evaluation"):

    chart, log = run_evaluation(space_url=space_url or None)

    st.subheader("Coverage Chart")
    render_hf_image(chart)

    st.subheader("Evaluation Log")
    st.text(log)