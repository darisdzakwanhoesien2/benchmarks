import streamlit as st
from api.climatebert_client import ClimateBERTClient
import os

st.set_page_config(page_title="ClimateBERT · Models", page_icon="🧾", layout="wide")
st.title("🧾 ClimateBERT — Models")

space_url = st.text_input("Space URL (optional)", value=os.getenv("CLIMATEBERT_SPACE_URL", ""))

if "cb_client" not in st.session_state:
    st.session_state.cb_client = None
    st.session_state.cb_connected = False

def ensure_client():
    if st.session_state.cb_client is None:
        try:
            st.session_state.cb_client = ClimateBERTClient(space_url or None)
            st.session_state.cb_connected = True
        except Exception as e:
            st.session_state.cb_client = None
            st.session_state.cb_connected = False
            st.error(f"Client init failed: {e}")

if st.button("Load available models"):
    ensure_client()
    if st.session_state.cb_client:
        try:
            models = st.session_state.cb_client.available_models
            st.success(f"Found {len(models)} model(s)")
            st.session_state.available_models = models
        except Exception as e:
            st.error(f"Could not fetch models: {e}")

models = st.session_state.get("available_models", [])
if models:
    st.subheader("Available models")
    st.dataframe({"model": models})

    sel = st.selectbox("Select model to test", models)
    example_text = st.text_area("Text to send to model", "Example ESG sentence for model", height=140)
    if st.button("Predict selected model"):
        if not example_text.strip():
            st.warning("Enter input text.")
        else:
            client = st.session_state.cb_client or ClimateBERTClient(space_url or None)
            with st.spinner("Calling model endpoint…"):
                try:
                    # many spaces use a generic /predict endpoint that accepts model attr,
                    # wrapper passes kwargs through — adjust if your space uses different API names.
                    resp = client.predict(example_text, api_name="/predict", model=sel)
                    st.subheader("Response")
                    st.json(resp)
                except Exception as e:
                    st.error(f"Call failed: {e}")
else:
    st.info("No models loaded — click 'Load available models' after connecting.")