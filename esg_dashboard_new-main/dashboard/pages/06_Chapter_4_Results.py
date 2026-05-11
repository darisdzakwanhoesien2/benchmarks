from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_4_SECTIONS,
    CHAPTER_FLOW_MERMAID,
    EXISTING_DATA_PATH,
    PREDICTION_OUTPUT_DIR,
    RQ_PAGE_MAP,
    load_artifact_report,
    mermaid_download_section,
    page_link_grid,
    render_mermaid,
)


st.set_page_config(page_title="Chapter 4 Results", layout="wide")
st.title("Chapter 4: Results")
st.caption("Result implementation chapter: what was produced, measured, visualized, and stored.")

st.caption(f"Existing parsed dataset: `{EXISTING_DATA_PATH}`")
st.caption(f"ClimateBERT prediction outputs: `{PREDICTION_OUTPUT_DIR}`")

st.subheader("Chapter 4 Purpose")
st.write(
    "Chapter 4 should present the implemented outputs without over-interpreting them. It answers: what data exists, "
    "what the dashboard generated, what model outputs were saved, and which result tables or images support each RQ."
)

st.subheader("Chapter 4 to 6 Flow")
render_mermaid(CHAPTER_FLOW_MERMAID, height=420)
mermaid_download_section(CHAPTER_FLOW_MERMAID, "chapter_4_to_6_flow")

tab_sections, tab_rq, tab_images = st.tabs(["Result Sections", "RQ Result Mapping", "Saved Images"])

with tab_sections:
    st.subheader("Recommended Chapter 4 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_4_SECTIONS), use_container_width=True, height=420)

    for section in CHAPTER_4_SECTIONS:
        st.markdown(f"### {section['section']}")
        st.markdown(f"**Supports:** {section['supports']}")
        st.write(section["results"])
        st.markdown("**Pages to use:**")
        st.write(", ".join(section["pages"]))

with tab_rq:
    st.subheader("How Each RQ Appears in Chapter 4")
    rows = []
    for rq in RQ_PAGE_MAP:
        rows.append(
            {
                "rq": rq["rq"],
                "theme": rq["theme"],
                "chapter_4_results": rq["chapter_4_use"],
                "pages_to_open": ", ".join(label for label, _ in rq["primary_pages"]),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=420)

    selected_rq = st.selectbox("Open pages for RQ", [rq["rq"] for rq in RQ_PAGE_MAP])
    selected = next(rq for rq in RQ_PAGE_MAP if rq["rq"] == selected_rq)
    page_link_grid(selected["primary_pages"], columns=3)

with tab_images:
    st.subheader("Images to Include in Chapter 4")
    report = load_artifact_report()
    images = report.get("images", [])
    if not images:
        st.warning("No saved artifact images found. Run `python3 generate_research_question_artifacts.py` first.")
    else:
        for entry in images:
            st.markdown(f"### {entry['title']}")
            path = Path(__file__).resolve().parent / "research_question_artifacts" / entry["path"]
            if path.exists():
                st.image(str(path), use_container_width=True)
            st.write(entry["what_it_shows"])
            st.markdown(f"**Chapter 4 use:** Present this as a result artifact. {entry['interpretation']}")
