import streamlit as st


def safe_api_call(func, *args, **kwargs):

    try:

        return func(*args, **kwargs)

    except Exception as e:

        st.error("API call failed")

        st.exception(e)

        return None
