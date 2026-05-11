from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_5_SECTIONS,
    RQ_PAGE_MAP,
    RQ_TO_CHAPTER_MERMAID,
    mermaid_download_section,
    page_link_grid,
    render_mermaid,
)


st.set_page_config(page_title="Chapter 5 Discussion", layout="wide")
st.title("Chapter 5: Discussion")
st.caption("Interpretation chapter: what the results mean, why some evidence underperforms, and how limitations affect the RQs.")

st.subheader("Chapter 5 Purpose")
st.write(
    "Chapter 5 should interpret the Chapter 4 outputs. This is where descriptive findings become research meaning, "
    "but only within the limits of available evidence. Available evidence can support current claims, Partial evidence "
    "should be discussed cautiously, and Needed evidence should be framed as limitation or future work."
)

st.subheader("RQ to Discussion Flow")
render_mermaid(RQ_TO_CHAPTER_MERMAID, height=680)
mermaid_download_section(RQ_TO_CHAPTER_MERMAID, "rq_to_discussion_flow")

tab_sections, tab_rq, tab_claims = st.tabs(["Discussion Sections", "RQ Discussion Map", "Claim Strength"])

with tab_sections:
    st.subheader("Recommended Chapter 5 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_5_SECTIONS), use_container_width=True, height=420)

    for section in CHAPTER_5_SECTIONS:
        st.markdown(f"### {section['section']}")
        st.markdown(f"**Supports:** {section['supports']}")
        st.write(section["discussion"])

with tab_rq:
    st.subheader("How to Discuss Each Research Question")
    selected_rq = st.selectbox("Choose RQ", [item["rq"] for item in RQ_PAGE_MAP])
    rq = next(item for item in RQ_PAGE_MAP if item["rq"] == selected_rq)

    st.markdown(f"### {rq['rq']} · {rq['theme']}")
    st.write(rq["question"])
    st.markdown("#### Result to Interpret")
    st.write(rq["chapter_4_use"])
    st.markdown("#### Discussion Angle")
    st.write(rq["chapter_5_use"])
    st.markdown("#### Limitation or Risk")
    st.warning(rq["needed_completion"])
    st.markdown("#### Pages to Revisit")
    page_link_grid(rq["primary_pages"], columns=3)

with tab_claims:
    st.subheader("How to Word Claims in Chapter 5")
    st.markdown("#### Available Evidence")
    st.success(
        "Use direct wording: the dashboard shows, the dataset contains, the model output indicates, or the distribution suggests. "
        "Still include the source path, denominator, and scope."
    )

    st.markdown("#### Partial Evidence")
    st.info(
        "Use cautious wording: the pattern is promising, exploratory, partially supported, or requires validation. "
        "Explain exactly what is missing, such as expert labels, balanced coverage, or full model prediction coverage."
    )

    st.markdown("#### Needed Evidence")
    st.warning(
        "Use limitation wording: this metric is required before a strong claim can be made. Turn the item into a concrete "
        "future-work step or a pre-submission task."
    )

    st.markdown("#### General Discussion Paragraph")
    st.write(
        "The dashboard results show that the ESG ABSA workflow is operational and traceable, but the strength of each "
        "research answer differs by evidence type. Distributional and workflow evidence can be interpreted descriptively, "
        "whereas classification quality and stability require additional validation through expert annotation, full local "
        "ClimateBERT prediction coverage, and balanced model/prompt comparisons."
    )
