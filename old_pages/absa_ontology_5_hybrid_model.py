import streamlit as st
import torch
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.hybrid_model import run_hierarchical_hybrid

st.title("Hybrid Model (Hierarchical + MTL) Demo")

st.write("This demo runs the hybrid model for ESG ABSA.")

if st.button("Run Hybrid Model"):
    try:
        df, fig, metrics = run_hierarchical_hybrid()
        st.write("Output DataFrame:")
        st.dataframe(df)
        if fig:
            st.pyplot(fig)
        st.write("Metrics:", metrics)
        st.success("Hybrid model run complete!")
    except Exception as e:
        st.error(f"Failed to run hybrid model: {e}")
else:
    st.info("Click 'Run Hybrid Model' to execute.")