import streamlit as st
from _page_explanations import add_page_explanation, add_section_explanation
from api.climatebert_client import ClimateBERTClient

st.title("🧠 Model Explorer")
add_page_explanation(__file__)

api = ClimateBERTClient()

st.write("Available models:")

for model in api.available_models:

    st.markdown(f"• **{model}**")

st.info(f"Total models: {len(api.available_models)}")