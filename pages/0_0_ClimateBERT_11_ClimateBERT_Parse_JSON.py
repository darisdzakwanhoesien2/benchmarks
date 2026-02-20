import streamlit as st
import pandas as pd

from utils.json_logger import load_results
from utils.climatebert_parser import (
    parse_climatebert_markdown,
    flatten_climatebert
)
from utils.climatebert_storage import (
    save_parsed_result,
    load_parsed_results
)


st.title("ClimateBERT JSON Parser")

raw_results = load_results()

if not raw_results:

    st.warning("No ClimateBERT results found")

    st.stop()


# select result
index = st.selectbox(
    "Select Result",
    range(len(raw_results)),
    format_func=lambda i: raw_results[i]["timestamp"]
)

selected = raw_results[index]

st.subheader("Raw Markdown")

st.markdown(selected["result"])


# parse button
if st.button("Parse to JSON"):

    parsed = parse_climatebert_markdown(selected["result"])

    save_parsed_result(parsed)

    st.success("Parsed successfully")

    st.subheader("Parsed JSON")

    st.json(parsed)

    # table view
    flat = flatten_climatebert(parsed)

    df = pd.DataFrame(flat)

    st.subheader("Table View")

    st.dataframe(df)

    # success summary
    success = df[df.status == "success"].shape[0]
    error = df[df.status == "error"].shape[0]

    st.metric("Successful Models", success)
    st.metric("Failed Models", error)


# history section
st.divider()

st.subheader("Parsed History")

history = load_parsed_results()

if history:

    st.write(f"{len(history)} parsed entries")

    latest = history[-1]

    df = pd.DataFrame(flatten_climatebert(latest))

    st.dataframe(df)