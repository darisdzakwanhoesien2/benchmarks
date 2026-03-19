import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.explainability import compare_explain

st.title("Explainability Dashboard")

if st.button("Compare Models"):
    df, fig, scatter = compare_explain()
    st.write("Comparison DataFrame:")
    st.dataframe(df)
    if fig:
        st.pyplot(fig)
    if scatter is not None:
        st.plotly_chart(scatter)
else:
    st.info("Click 'Compare Models' to run the explainability comparison.")