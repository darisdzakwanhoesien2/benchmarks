from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import (  # noqa: E402
    VIS,
    agreement_chart,
    artifact_chart,
    count_chart,
    data_bundle,
    generated_chapter4_paragraph,
    heatmap_from_table,
    image_or_info,
    metric_row,
    model_results_table,
    model_stability_chart,
    ontology_chart,
    pdf_prompt_heatmap,
    prompt_stability_chart,
    render_citation_panel,
    render_chapter_text,
    render_generated_claim_box,
    workflow_coverage_chart,
)
from graph_attachment_gallery import render_attachment_cards  # noqa: E402


st.set_page_config(page_title="Chapter 4 - Implementation and Results", layout="wide")

bundle = data_bundle()

st.title("Chapter 4 - Implementation and Results")
st.caption("Interactive Streamlit translation of `thesis_chapters_4_5_6.docx`, with live graphs from current result artifacts.")
metric_row(bundle)

tab_text, tab_live, tab_rq12, tab_rq34, tab_rq56, tab_figures, tab_cards = st.tabs(
    ["Chapter Text", "Live Action Plan Evidence", "RQ1-RQ2", "RQ3-RQ4", "RQ5-RQ6", "Figure Gallery", "Attachment Cards"]
)

with tab_text:
    render_chapter_text(4)

with tab_live:
    st.header("Chapter 4 Live Result Narrative")
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        render_generated_claim_box(
            "chapter4_live_analysis_note",
            generated_chapter4_paragraph(bundle),
            "Implementation result paragraph with live citations",
        )
        render_citation_panel(bundle)
    with right:
        st.markdown("#### Current models in results")
        models = model_results_table(bundle)
        if models.empty:
            st.info("No model-stability rows are available yet.")
        else:
            st.dataframe(models, use_container_width=True, hide_index=True, height=260)

        st.markdown("#### PDF x prompt processing matrix")
        pdf_prompt_heatmap(bundle["tone_records"])

with tab_rq12:
    st.header("RQ1-RQ2: Structured ESG Records and Tone-Aware Schema")
    st.subheader("Figure 4.1 - System architecture and RQ implementation coverage")
    workflow_coverage_chart()

    st.subheader("Figure 4.2 - PDF x prompt processing matrix")
    pdf_prompt_heatmap(bundle["tone_records"])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Figure 4.3 - Tone distribution")
        count_chart(bundle["tone_records"], "tone", "Tone distribution - extracted ESG records")
    with c2:
        st.subheader("Figure 4.4 - ESG pillar distribution")
        count_chart(bundle["tone_records"], "esg", "ESG pillar distribution")

    st.subheader("Figure 4.5 - Tone x ESG pillar heatmap")
    heatmap_from_table(bundle["tone_esg"], "tone", "Tone x ESG pillar")

with tab_rq34:
    st.header("RQ3-RQ4: ClimateBERT Comparison and Diagnostics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Figure 4.6 - Tone x ClimateBERT/proxy label crosstab")
        heatmap_from_table(bundle["tone_climatebert"], "tone", "Tone x ClimateBERT/proxy label")
    with c2:
        st.subheader("Figure 4.7 - Agreement metrics")
        agreement_chart(bundle["agreement"])

    st.subheader("Figure 4.8 - Failure mode frequency by tone category")
    failure = bundle["failure_counts"]
    if not failure.empty and {"mode", "count"}.issubset(failure.columns):
        count_col = "mode"
        count_chart(failure.loc[failure.index.repeat(failure["count"].astype(int).clip(lower=0))], count_col, "Failure mode frequency")
    else:
        st.dataframe(failure, use_container_width=True, height=260)

    st.subheader("Figure 4.9 - Ontology coverage by aspect")
    ontology_chart(bundle["ontology"])

with tab_rq56:
    st.header("RQ5-RQ6: Reproducibility, Visualisation, and Stability")
    st.subheader("Figure 4.10 - Artifact inventory")
    artifact_chart(bundle["inventory"])

    st.subheader("Figure 4.11 - Model stability comparison")
    model_stability_chart(bundle["model_stability"])

    st.subheader("Figure 4.12 - Prompt template stability")
    prompt_stability_chart(bundle["prompt_stability"])

    st.subheader("Figure 4.13 - Top-scoring ClimateBERT records")
    image_or_info(VIS / "climatebert_remote_top_scores.png", "Top-scoring ClimateBERT records")

with tab_figures:
    st.header("Saved Graph Attachments")
    cols = st.columns(2)
    images = [
        ("tone_distribution.png", "Tone distribution"),
        ("esg_by_tone.png", "ESG by tone"),
        ("aspect_by_tone_heatmap.png", "Aspect by tone heatmap"),
        ("climatebert_label_by_tone.png", "ClimateBERT label by tone"),
        ("climatebert_remote_top_scores.png", "ClimateBERT top scores"),
    ]
    for idx, (name, caption) in enumerate(images):
        with cols[idx % 2]:
            image_or_info(VIS / name, caption)

with tab_cards:
    render_attachment_cards(
        "Chapter 4 Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        figures=["A.1", "A.2", "A.3", "A.4", "A.7", "A.8", "A.10", "A.14", "A.17", "A.18", "A.19", "A.20"],
    )
