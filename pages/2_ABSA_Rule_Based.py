import streamlit as st

from api.absa_client import run_rule
from utils.dataframe import hf_to_df
from utils.visualization import render_plot


st.title("ABSA Rule-Based Ontology")

text = st.text_area("Enter ESG Text")


if st.button("Run Rule-Based ABSA"):

    result = run_rule(text)

    csv_path = result[0]
    preview = hf_to_df(result[1])
    plot = result[2]
    explanations = hf_to_df(result[3])

    st.subheader("Preview")
    st.dataframe(preview)

    st.subheader("Visualization")
    render_plot(plot)

    st.subheader("Rule Explanations")
    st.dataframe(explanations)

    st.download_button(
        "Download CSV",
        open(csv_path, "rb"),
        file_name="absa_rule.csv"
    )
