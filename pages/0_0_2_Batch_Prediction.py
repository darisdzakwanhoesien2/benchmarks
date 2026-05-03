import streamlit as st
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
from api.climatebert_client import ClimateBERTClient

st.title("📊 Batch Prediction")
add_page_explanation(__file__)

api = ClimateBERTClient()

model = st.selectbox(
    "Select Model",
    api.available_models
)

uploaded_file = st.file_uploader(
    "Upload CSV with 'text' column",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.write("Preview:")
    st.dataframe(df.head())

    if st.button("Run Batch Prediction"):

        with st.spinner("Processing..."):

            results = api.batch_predict(
                df["text"].tolist(),
                model
            )

        df["prediction"] = [r["prediction"] for r in results]

        st.success("Done!")

        st.dataframe(df)

        csv = df.to_csv(index=False)

        st.download_button(
            "Download Results",
            csv,
            "results.csv",
            "text/csv"
        )