import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.app_state import app_state

st.title("App State Demo")
st.write("Current App State:")
st.json(dict(app_state))

if st.button("Add Example State"):
    app_state["example"] = "This is a test value."
    st.success("Added example state!")
    st.experimental_rerun()