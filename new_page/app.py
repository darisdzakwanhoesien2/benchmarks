from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="Thesis Dashboard Hub", layout="wide")

st.title("Thesis Dashboard Hub")
st.caption(
    "Run Streamlit from this file to enable multi-page navigation (sidebar pages). "
    "If you run Streamlit from a file inside `pages/`, Streamlit will not discover sibling pages correctly."
)

st.markdown("### Core pages")
st.page_link("pages/0_0_Streamlit_Page_Workflow.py", label="0_0 Streamlit Page Workflow (navigation hub)")
st.page_link("pages/3_0_Thesis_Action_Plan.py", label="3_0 Thesis Action Plan")
st.page_link("pages/5_Thesis_Systematic_Workflow_dashboard.py", label="5 Thesis Systematic Workflow Dashboard")

st.markdown("### Utilities")
st.page_link("pages/0_10_Live_Numbers_Lineage.py", label="0_10 Live Numbers + Lineage")
st.page_link("pages/0_13_Bib_File_Explorer.py", label="0_13 Bib File Explorer")
st.page_link("pages/3_3_A4_Regenerate_Fix_Grouping.py", label="3_3 A.4 Regenerate (fix grouping)")
st.page_link("pages/1_14_ClimateBERT_Multi_Model_Runner.py", label="1_14 ClimateBERT Multi-Model Runner")
