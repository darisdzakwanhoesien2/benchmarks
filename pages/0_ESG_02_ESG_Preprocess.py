import streamlit as st
from api.esgdata_client import preprocess


st.title("ESG Preprocessing")

input_path = st.text_input("Input CSV path")

output_path = st.text_input("Output CSV path", "processed.csv")


if st.button("Run Preprocessing"):

    result = preprocess(input_path, output_path)

    st.success("Preprocessing complete")

    st.json(result)