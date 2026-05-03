import streamlit as st
import pandas as pd
from datetime import datetime

from api_client import predict_esg
from utils.logger import save_history, load_history
from utils.formatter import format_result

st.title("🌱 ESG Text Analyzer")

text_input = st.text_area(
    "Enter company report, news, or ESG-related text:",
    height=200
)

col1, col2 = st.columns([1, 1])

with col1:
    analyze_button = st.button("Analyze ESG")

with col2:
    clear_button = st.button("Clear")

if clear_button:
    st.rerun()

if analyze_button and text_input.strip():

    with st.spinner("Analyzing ESG..."):

        result = predict_esg(text_input)
        formatted = format_result(result)

        timestamp = datetime.now().isoformat()

        entry = {
            "timestamp": timestamp,
            "text": text_input,
            "result": result
        }

        save_history(entry)

    st.success("Analysis Complete")

    st.subheader("Formatted Result")
    st.json(formatted)


# ----------------------
# History Section
# ----------------------

st.divider()
st.subheader("History")

history = load_history()

if history:

    df = pd.DataFrame(history)
    st.dataframe(df[["timestamp", "text"]])

    selected = st.selectbox(
        "View detailed result:",
        range(len(history)),
        format_func=lambda i: history[i]["timestamp"]
    )

    st.json(history[selected]["result"])

else:
    st.info("No history yet.")
