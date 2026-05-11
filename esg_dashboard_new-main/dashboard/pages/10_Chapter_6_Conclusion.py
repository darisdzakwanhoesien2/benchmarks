from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_6_SECTIONS,
    CHAPTER_FLOW_MERMAID,
    RQ_PAGE_MAP,
    page_link_grid,
    render_mermaid,
)


st.set_page_config(page_title="Chapter 6 Conclusion", layout="wide")
st.title("Chapter 6: Conclusion")
st.caption("Conclusion chapter: concise answers, contributions, limitations, future work, and final thesis position.")

st.subheader("Chapter 6 Purpose")
st.write(
    "Chapter 6 should not introduce new analysis. It should close the loop from the research questions to the Chapter 4 "
    "results and Chapter 5 discussion, then state what can be concluded, what the study contributes, and what remains limited."
)

st.subheader("Chapter 4 to 6 Closing Flow")
render_mermaid(CHAPTER_FLOW_MERMAID, height=420)

tab_sections, tab_rq, tab_final = st.tabs(["Conclusion Sections", "RQ Answer Summary", "Final Statement"])

with tab_sections:
    st.subheader("Recommended Chapter 6 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_6_SECTIONS), use_container_width=True, height=360)

    for section in CHAPTER_6_SECTIONS:
        st.markdown(f"### {section['section']}")
        st.write(section["conclusion"])

with tab_rq:
    st.subheader("Concise Answer for Each Research Question")
    for rq in RQ_PAGE_MAP:
        with st.expander(f"{rq['rq']} · {rq['theme']}", expanded=rq["rq"] in {"RQ1", "RQ3"}):
            st.write(rq["question"])
            st.markdown("**Conclusion answer:**")
            st.write(rq["chapter_6_use"])
            st.markdown("**Remaining qualification:**")
            st.warning(rq["needed_completion"])
            page_link_grid(rq["primary_pages"], columns=3)

with tab_final:
    st.subheader("Thesis-Ready Final Conclusion")
    st.success(
        "This study implemented a reproducible ESG ABSA dashboard that connects parsed sustainability-report records, "
        "local ClimateBERT model outputs, result visualization, and research-question evidence tracking. The system is "
        "suitable for presenting descriptive ESG extraction results, diagnosing weaknesses, and organizing thesis evidence."
    )

    st.write(
        "The main conclusion is that the implementation successfully supports a traceable workflow from source reports to "
        "sentence-level ESG evidence and thesis-ready visual artifacts. The dashboard also makes methodological limitations "
        "visible: OCR quality, expert-label validation, local ClimateBERT coverage, manual error taxonomy, and balanced "
        "model/prompt comparisons remain necessary before the study can make strong accuracy or stability claims."
    )

    st.subheader("Contribution Summary")
    st.write("- A PDF-to-structured ESG evidence workflow with source traceability.")
    st.write("- A local ClimateBERT processing and result-visualization workflow that stores partial outputs for continuation.")
    st.write("- A research-question evidence dashboard that links Available, Partial, and Needed evidence to thesis chapters.")
    st.write("- Saved PNG, JSON, Markdown, and Mermaid artifacts for auditability and thesis writing.")

    st.subheader("Final Work Before Submission")
    st.write("- Complete expert annotation and compute agreement/performance metrics.")
    st.write("- Complete ClimateBERT predictions and verify coverage across all selected models.")
    st.write("- Add OCR and sentence-boundary validation metrics.")
    st.write("- Add formal diagnostic error labels.")
    st.write("- Run balanced prompt/model stability and ensemble analysis.")
