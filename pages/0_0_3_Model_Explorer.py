import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
from api.climatebert_client import ClimateBERTClient

st.title("🧠 Model Explorer")
add_page_explanation(__file__)

api = ClimateBERTClient()
if not api.is_connected():
    st.error(
        "ClimateBERT service is currently unavailable. "
        "Please try again shortly.\n\n"
        f"Details: {api.get_connection_error() or 'connection failed'}"
    )
    st.stop()

st.write("Available models:")

for model in api.available_models:

    st.markdown(f"• **{model}**")

st.info(f"Total models: {len(api.available_models)}")
