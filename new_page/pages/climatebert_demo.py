import streamlit as st
from api.climatebert_client import ClimateBERTClient
from pathlib import Path
import os

st.set_page_config(page_title="ClimateBERT · Demo", page_icon="🌡️", layout="wide")
st.title("🌡️ ClimateBERT — Demo")

# Optional override of the space URL
default = os.getenv("CLIMATEBERT_SPACE_URL", "")
space_url = st.text_input("Space URL (leave blank to use default)", value=default, help="e.g. https://...hf.space/")

if "cb_client" not in st.session_state:
    st.session_state.cb_client = None
    st.session_state.cb_connected = False
    st.session_state.last_error = ""

def connect():
    try:
        client = ClimateBERTClient(space_url or None)
        # attempt lazy instantiation only when used; still test by accessing available_models (best-effort)
        _ = client.available_models
        st.session_state.cb_client = client
        st.session_state.cb_connected = True
        st.session_state.last_error = ""
        st.success("✅ Connected to ClimateBERT space")
    except Exception as e:
        st.session_state.cb_client = None
        st.session_state.cb_connected = False
        st.session_state.last_error = str(e)
        st.error(f"Connection failed: {e}")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("Connect to ClimateBERT"):
        connect()
with col2:
    if st.session_state.cb_connected:
        st.metric("Status", "Connected")
    else:
        st.metric("Status", "Disconnected")

st.divider()

text = st.text_area("Input text to classify / predict (T1)", "Hello world — ESG climate example", height=180)

if st.button("Predict (all models)"):
    if not text.strip():
        st.warning("Enter some text first.")
    else:
        client = st.session_state.cb_client or ClimateBERTClient(space_url or None)
        with st.spinner("Calling predict_all_models…"):
            try:
                out = client.predict_all_models(text)
                st.subheader("Results (raw)")
                st.json(out)
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                st.session_state.last_error = str(e)

st.divider()

st.subheader("Quick usage / troubleshooting")
st.write(
    "• Use the Connect button to test the space URL. "
    "• If your space exposes other API names, use the wrapper in api/climatebert_client.py "
    "  (predict / predict_all_models) to call them."
)