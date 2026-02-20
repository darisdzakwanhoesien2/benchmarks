import streamlit as st
from api.climatebert_client import ClimateBERTClient

st.title("🧠 Model Explorer")

api = ClimateBERTClient()

st.write("Available models:")

for model in api.available_models:

    st.markdown(f"• **{model}**")

st.info(f"Total models: {len(api.available_models)}")