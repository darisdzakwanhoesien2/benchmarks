from pathlib import Path
import sys

import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_FLOW_MERMAID,
    CONTRIBUTIONS,
    FINAL_CONCLUSION,
    LIMITATIONS,
    markdown_conclusion_export,
    mermaid_download_section,
    render_mermaid,
    research_questions_df,
)


st.set_page_config(page_title="Chapter 6 Conclusion", layout="wide")
st.title("Chapter 6 Conclusion")
st.caption("Conclusion implementation page: concise RQ answers, contribution summary, limitations, and final thesis-ready conclusion.")


rq_df = research_questions_df()

tab_answers, tab_contributions, tab_limitations, tab_export, tab_flow = st.tabs(
    ["RQ Answers", "Contributions", "Limitations", "Markdown Draft", "Diagram"]
)

with tab_answers:
    st.subheader("Concise Answers to RQ1-RQ6")
    st.dataframe(
        rq_df[["rq", "theme", "evidence_status", "conclusion"]],
        use_container_width=True,
        hide_index=True,
    )

    selected_rq = st.selectbox("Open RQ conclusion", rq_df["rq"].tolist())
    row = rq_df.loc[rq_df["rq"] == selected_rq].iloc[0]
    st.info(row["conclusion"])
    st.markdown(f"**Claim strength:** {row['evidence_status']}")
    st.markdown(f"**Short answer:** {row['short_answer']}")

with tab_contributions:
    st.subheader("Contribution Summary")
    for contribution in CONTRIBUTIONS:
        st.markdown(f"- {contribution}")

    st.subheader("Overall Conclusion")
    st.success(FINAL_CONCLUSION)

with tab_limitations:
    st.subheader("Limitations to Carry into Chapter 6")
    for limitation in LIMITATIONS:
        st.markdown(f"- {limitation}")

    st.subheader("Future Work")
    st.markdown(
        """
        - Add expert annotation and inter-annotator agreement.
        - Run complete local ClimateBERT inference and map label spaces explicitly.
        - Build a balanced model x prompt x document comparison matrix.
        - Add OCR, segmentation, and table/figure extraction quality metrics.
        """
    )

with tab_export:
    st.subheader("Thesis-Ready Markdown Draft")
    draft = markdown_conclusion_export()
    st.download_button(
        "Download conclusion draft",
        data=draft,
        file_name="chapter_6_conclusion_draft.md",
        mime="text/markdown",
    )
    st.code(draft, language="markdown")

with tab_flow:
    st.subheader("Conclusion Position in Thesis Flow")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=460)
    mermaid_download_section(CHAPTER_FLOW_MERMAID, "chapter_6_conclusion_flow")
