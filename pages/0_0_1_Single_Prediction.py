import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
from api.climatebert_client import ClimateBERTClient

st.title("🔎 Single Prediction")
add_page_explanation(__file__)

api = ClimateBERTClient()

model = st.selectbox(
    "Select Model",
    api.available_models
)

text = st.text_area(
    "Enter text",
    height=150
)

if st.button("Predict"):

    if not text.strip():
        st.warning("Enter text first")
    else:

        with st.spinner("Running inference..."):

            result = api.predict(
                text=text,
                model_key=model
            )

        st.success("Prediction complete")

        st.json(result)