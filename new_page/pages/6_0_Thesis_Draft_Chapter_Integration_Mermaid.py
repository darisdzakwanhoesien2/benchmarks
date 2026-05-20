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
    artifact_chart,
    citation_table,
    chapter_outline,
    data_bundle,
    evidence_metrics,
    metric_row,
    model_stability_chart,
    ontology_chart,
    pdf_outline,
    pipeline_mermaid,
    prompt_stability_chart,
    render_mermaid,
    rq_evidence_mermaid,
    thesis_spine_mermaid,
    validation_mermaid,
)


st.set_page_config(page_title="Thesis Draft + Chapters Mermaid Integration", layout="wide")

bundle = data_bundle()
metrics = evidence_metrics(bundle)

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
    render_mermaid(pipeline_mermaid(), height=980)

    st.subheader("Detailed Pipeline Breakdown")
    pipeline_rows = [
        {
            "layer": "A. Source",
            "thesis role": "Connects the draft methodology to the empirical corpus.",
            "live evidence": f"{metrics['ocr_documents']:,} OCR documents; {metrics['ocr_pages']:.0f} OCR pages.",
            "main artifact": "results/revision_analysis/ocr_processing_summary.csv",
            "chapter use": "Chapter 4 describes the data source and processing scope.",
        },
        {
            "layer": "B. OCR",
            "thesis role": "Turns report PDFs into page-level text units for extraction.",
            "live evidence": "OCR status, page counts, and error fields.",
            "main artifact": "thesis_dataset/*/pages/page_XXXX.md",
            "chapter use": "Chapter 4 implementation evidence; Chapter 5 OCR limitation discussion.",
        },
        {
            "layer": "C. Prompt and LLM",
            "thesis role": "Runs extraction prompts through selectable LLM backends.",
            "live evidence": f"{metrics['live_runs']:,} run objects; {metrics['live_extracted_rows']:,} live extracted records.",
            "main artifact": "results/esg_records.json",
            "chapter use": "Chapter 4 results and Chapter 6 reproducibility contribution.",
        },
        {
            "layer": "D. ABSA evidence",
            "thesis role": "Creates record-level aspect, ESG, sentiment, and tone labels.",
            "live evidence": f"{metrics['tone_records']:,} flattened records across {metrics['documents']:,} documents.",
            "main artifact": "results/visualizations/tone_records_flat.csv",
            "chapter use": "Chapter 4 core empirical table and visualizations.",
        },
        {
            "layer": "E. Validation",
            "thesis role": "Tests whether labels are stable, interpretable, and traceable.",
            "live evidence": f"{metrics['models']:,} model configurations; kappa {metrics['kappa']:.3f}.",
            "main artifact": "results/revision_analysis/*.csv",
            "chapter use": "Chapter 5 discussion and Chapter 6 future work.",
        },
        {
            "layer": "F. Thesis output",
            "thesis role": "Converts artifacts into figures, cited claims, and editable interpretation.",
            "live evidence": f"{metrics['artifacts']:,} discoverable result artifacts.",
            "main artifact": "Streamlit pages 6_0 to 6_3",
            "chapter use": "Defense-ready narrative and updateable thesis sections.",
        },
    ]
    st.dataframe(pd.DataFrame(pipeline_rows), use_container_width=True, hide_index=True, height=310)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Prompt Stability Evidence")
        prompt_stability_chart(bundle["prompt_stability"])
    with c2:
        st.subheader("Model Stability Evidence")
        model_stability_chart(bundle["model_stability"])

with tab_validation:
    st.header("Validation and Reliability Loop")
    st.write(
        "This map shows how the ground-truth workbench, ClimateBERT comparison, model/prompt stability, and failure audits "
        "support construct validity, reliability, limitations, and future work."
    )
    render_mermaid(validation_mermaid(), height=980)
    st.subheader("Detailed Validation Breakdown")
    validation_rows = [
        {
            "validation layer": "Human annotation",
            "what it checks": "Whether extracted records can be judged by tone, ESG pillar, aspect, and review status.",
            "expected output": "silver_tone_ground_truth.csv with completed human labels.",
            "thesis claim supported": "RQ2 schema validity and RQ5 reproducibility.",
        },
        {
            "validation layer": "ClimateBERT comparison",
            "what it checks": "Whether disclosure tone is the same construct as climate commitment.",
            "expected output": "Agreement table, crosstab, Cohen kappa.",
            "thesis claim supported": "RQ3 construct divergence between tone and ClimateBERT labels.",
        },
        {
            "validation layer": "Prompt stability",
            "what it checks": "Whether prompt design changes parse success, missing tone, and field completion.",
            "expected output": "prompt_stability_summary.csv.",
            "thesis claim supported": "RQ6 prompt sensitivity and repeatability.",
        },
        {
            "validation layer": "Model stability",
            "what it checks": "Whether backend/model choice changes extraction reliability.",
            "expected output": "model_stability_summary.csv plus live esg_records.json-derived rows.",
            "thesis claim supported": "RQ6 model sensitivity and reproducibility boundaries.",
        },
        {
            "validation layer": "Failure audit",
            "what it checks": "Where the extraction pipeline fails or drifts.",
            "expected output": "failure_mode_counts.csv and failure_modes.csv.",
            "thesis claim supported": "Chapter 5 limitations and Chapter 6 future work.",
        },
        {
            "validation layer": "Ontology coverage",
            "what it checks": "Which aspects map to GRI/SASB and which remain Indonesian-specific.",
            "expected output": "ontology_coverage.csv.",
            "thesis claim supported": "Novel Indonesian ESG vocabulary contribution.",
        },
    ]
    st.dataframe(pd.DataFrame(validation_rows), use_container_width=True, hide_index=True, height=300)

    st.subheader("ClimateBERT / Proxy Agreement Evidence")
    c1, c2 = st.columns(2)
    with c1:
        agreement_chart(bundle["agreement"])
    with c2:
        ontology_chart(bundle["ontology"])

with tab_artifacts:
    st.header("Artifact Lineage and Streamlit Page Integration")
    st.write(
        "This diagram connects the source thesis documents to generated chapter pages and result artifacts, "
        "so the Streamlit application becomes an evidence layer for the thesis narrative."
    )
    render_mermaid(artifact_mermaid(), height=1020)

    st.subheader("Detailed Artifact Lineage")
    artifact_rows = [
        {
            "artifact family": "Source documents",
            "examples": "thesis_draft_1.pdf, thesis_chapters_4_5_6.docx, sustainability report PDFs",
            "owner page": "6_0 integration map",
            "why it matters": "Keeps thesis structure and empirical data connected.",
        },
        {
            "artifact family": "Execution artifacts",
            "examples": "results/esg_records.json, background job status.json, events.jsonl",
            "owner page": "3_0 Thesis Action Plan and LLM monitor",
            "why it matters": "Preserves run provenance and supports reruns.",
        },
        {
            "artifact family": "Analysis tables",
            "examples": "tone_records_flat.csv, model_stability_summary.csv, prompt_stability_summary.csv",
            "owner page": "6_1 Chapter 4 and 6_3 Chapter 6",
            "why it matters": "Provides the numeric basis for figures and claims.",
        },
        {
            "artifact family": "Validation tables",
            "examples": "climatebert_proxy_agreement_summary.csv, ontology_coverage.csv, failure_mode_counts.csv",
            "owner page": "6_2 Chapter 5",
            "why it matters": "Supports interpretation, limitations, and construct-validity discussion.",
        },
        {
            "artifact family": "Editable thesis claims",
            "examples": "generated cited paragraphs plus empty analysis boxes",
            "owner page": "6_1, 6_2, 6_3",
            "why it matters": "Lets the written analysis change without losing the live evidence source.",
        },
    ]
    st.dataframe(pd.DataFrame(artifact_rows), use_container_width=True, hide_index=True, height=285)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Artifact Inventory Chart")
        artifact_chart(bundle["inventory"])
    with c2:
        st.subheader("Citation-Ready Result Claims")
        st.dataframe(citation_table(bundle), use_container_width=True, hide_index=True, height=360)

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
