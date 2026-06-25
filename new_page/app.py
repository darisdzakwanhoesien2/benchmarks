from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="Thesis Dashboard Hub", layout="wide")

st.title("Thesis Dashboard Hub")
st.caption(
    "Run Streamlit from this file to enable multi-page navigation (sidebar pages). "
    "If you run Streamlit from a file inside `pages/`, Streamlit will not discover sibling pages correctly."
)

st.markdown("### Core pages (archived → `past_pages/`)")
st.markdown("- `past_pages/0_0_Streamlit_Page_Workflow.py` — navigation hub")
st.markdown("- `past_pages/3_0_Thesis_Action_Plan.py`")
st.markdown("- `past_pages/5_Thesis_Systematic_Workflow_dashboard.py`")

st.markdown("### Utilities (archived → `past_pages/`)")
st.markdown("- `past_pages/0_10_Live_Numbers_Lineage.py`")
st.markdown("- `past_pages/0_13_Bib_File_Explorer.py`")
st.markdown("- `past_pages/3_3_A4_Regenerate_Fix_Grouping.py`")
st.markdown("- `past_pages/1_14_ClimateBERT_Multi_Model_Runner.py`")
