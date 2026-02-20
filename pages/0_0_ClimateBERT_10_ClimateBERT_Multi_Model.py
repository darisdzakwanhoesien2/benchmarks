import streamlit as st
import pandas as pd

from api.climatebert_client_combined import predict_all_models
from utils.json_logger import save_result, load_results
from utils.error_logger import log_error


st.title("ClimateBERT Multi-Model Inference")

text = st.text_area(
    "Enter ESG or Climate Text",
    height=200
)


col1, col2 = st.columns(2)

run_button = col1.button("Run ClimateBERT")

clear_button = col2.button("Clear")


if clear_button:
    st.rerun()


# Run inference
if run_button:

    if not text.strip():

        st.warning("Please enter text")

        st.stop()

    with st.spinner("Running ClimateBERT models..."):

        try:

            result = predict_all_models(text)

            save_result(text, result)

            st.success("Inference complete")

            st.subheader("Model Output")

            st.markdown(result)

        except Exception as e:

            log_error(e, text)

            st.error("Inference failed")

            st.exception(e)


# History viewer
st.divider()

st.subheader("Inference History")

history = load_results()

if history:

    df = pd.DataFrame(history)

    st.dataframe(df[["timestamp", "text"]])

    selected = st.selectbox(
        "View Result",
        range(len(history)),
        format_func=lambda i: history[i]["timestamp"]
    )

    st.markdown(history[selected]["result"])

else:

    st.info("No previous results")