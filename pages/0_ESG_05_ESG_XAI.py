import streamlit as st
from api.esgdata_client import run_evaluation
from utils.file_handler import render_hf_image


st.title("ESG Evaluation")

if st.button("Run Evaluation"):

    chart, log = run_evaluation()

    st.subheader("Coverage Chart")
    render_hf_image(chart)

    st.subheader("Evaluation Log")
    st.text(log)