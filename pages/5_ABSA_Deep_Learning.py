import streamlit as st

from api.absa_client import run_deep
from utils.dataframe import hf_to_df
from utils.visualization import render_plot


st.title("ABSA Deep Learning")

text = st.text_area("Enter ESG Text")

epochs = st.slider("Epochs", 1, 10, 1)


if st.button("Run Deep Learning ABSA"):

    result = run_deep(text, epochs)

    csv = result[0]
    predictions = hf_to_df(result[1])
    plot = result[2]
    tokens = hf_to_df(result[3])

    st.dataframe(predictions)

    render_plot(plot)

    st.subheader("Token Interpretability")
    st.dataframe(tokens)

    st.download_button(
        "Download CSV",
        open(csv, "rb"),
        file_name="absa_deep.csv"
    )
