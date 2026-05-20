from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import (  # noqa: E402
    DOCX_PATH,
    PDF_PATH,
    agreement_chart,
    artifact_mermaid,
    chapter_outline,
    data_bundle,
    metric_row,
    pdf_outline,
    pipeline_mermaid,
    render_mermaid,
    rq_evidence_mermaid,
    thesis_spine_mermaid,
    validation_mermaid,
)


st.set_page_config(page_title="Thesis Draft + Chapters Mermaid Integration", layout="wide")

bundle = data_bundle()

st.title("Thesis Draft + Chapters 4-6 Integration Map")
st.caption(
    "In-depth Mermaid maps that connect `thesis_draft_1.pdf` with "
    "`thesis_chapters_4_5_6.docx`, current result artifacts, and Streamlit evidence pages."
)
metric_row(bundle)

st.divider()

source_cols = st.columns(2)
source_cols[0].markdown(f"**PDF thesis draft:** `{PDF_PATH}`")
source_cols[1].markdown(f"**DOCX chapters 4-6:** `{DOCX_PATH}`")

tab_map, tab_rq, tab_pipeline, tab_validation, tab_artifacts, tab_outline, tab_evidence = st.tabs(
    [
        "Thesis Spine",
        "RQ Evidence",
        "Pipeline",
        "Validation",
        "Artifact Lineage",
        "Source Outlines",
        "Evidence Tables",
    ]
)

with tab_map:
    st.header("Full Thesis Spine: Draft PDF to Chapters 4-6")
    st.write(
        "This diagram treats the PDF as the full thesis spine and the DOCX as the focused implementation, "
        "discussion, and conclusion package. The arrows show how the early chapters feed the evidence and claims."
    )
    render_mermaid(thesis_spine_mermaid(), height=680)

with tab_rq:
    st.header("Research Questions to Evidence, Interpretation, and Conclusion")
    st.write(
        "This map connects the draft's problem/literature/methodology chapters to Chapter IV evidence, "
        "Chapter V interpretation, and Chapter VI contribution closure."
    )
    render_mermaid(rq_evidence_mermaid(), height=780)

with tab_pipeline:
    st.header("Method-to-Result Pipeline")
    st.write(
        "This diagram turns the methodology and implementation chapters into a reproducible dataflow: "
        "PDF inputs, OCR pages, prompt templates, LLM extraction, ABSA dimensions, validation, diagnostics, and thesis graphs."
    )
    render_mermaid(pipeline_mermaid(), height=720)

with tab_validation:
    st.header("Validation and Reliability Loop")
    st.write(
        "This map shows how the ground-truth workbench, ClimateBERT comparison, model/prompt stability, and failure audits "
        "support construct validity, reliability, limitations, and future work."
    )
    render_mermaid(validation_mermaid(), height=680)
    st.subheader("ClimateBERT / Proxy Agreement Evidence")
    agreement_chart(bundle["agreement"])

with tab_artifacts:
    st.header("Artifact Lineage and Streamlit Page Integration")
    st.write(
        "This diagram connects the source thesis documents to generated chapter pages and result artifacts, "
        "so the Streamlit application becomes an evidence layer for the thesis narrative."
    )
    render_mermaid(artifact_mermaid(), height=620)

with tab_outline:
    st.header("Source Outlines")
    pdf_df = pdf_outline()
    docx_df = chapter_outline()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("PDF Draft Outline")
        st.dataframe(pdf_df, use_container_width=True, hide_index=True, height=520)
    with c2:
        st.subheader("DOCX Chapter 4-6 Outline")
        st.dataframe(docx_df, use_container_width=True, hide_index=True, height=520)

    merged = pd.concat([pdf_df, docx_df], ignore_index=True, sort=False)
    st.download_button(
        "Download integrated outline CSV",
        merged.to_csv(index=False).encode("utf-8"),
        "thesis_draft_docx_integrated_outline.csv",
        "text/csv",
        use_container_width=True,
    )

with tab_evidence:
    st.header("Evidence Tables Used by the Integration")
    st.write(
        "These are the live result tables behind the Mermaid claims. Use this tab to verify that each narrative link "
        "has a concrete artifact behind it."
    )
    table_choice = st.selectbox(
        "Evidence table",
        [
            "tone_records",
            "tone_esg",
            "tone_climatebert",
            "model_stability",
            "prompt_stability",
            "failure_counts",
            "ontology",
            "agreement",
            "ocr",
            "greenwashing",
            "inventory",
        ],
    )
    df = bundle.get(table_choice, pd.DataFrame())
    display_df = df.astype(str) if not df.empty else df
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=520)
    if not df.empty:
        st.download_button(
            f"Download {table_choice}.csv",
            df.to_csv(index=False).encode("utf-8"),
            f"{table_choice}.csv",
            "text/csv",
            use_container_width=True,
        )
