from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import (  # noqa: E402
    agreement_chart,
    artifact_chart,
    data_bundle,
    generated_chapter6_paragraph,
    metric_row,
    model_stability_chart,
    ontology_chart,
    prompt_stability_chart,
    render_citation_panel,
    render_chapter_text,
    render_generated_claim_box,
    workflow_coverage_chart,
)
from graph_attachment_gallery import render_attachment_cards  # noqa: E402


st.set_page_config(page_title="Chapter 6 - Conclusion", layout="wide")

bundle = data_bundle()

st.title("Chapter 6 - Conclusion")
st.caption("Conclusion chapter translated into an interactive evidence summary with contribution and future-work views.")
metric_row(bundle)

tab_text, tab_live, tab_contributions, tab_rqs, tab_future, tab_cards = st.tabs(
    ["Chapter Text", "Live Conclusion Claims", "Contribution Summary", "Research Question Answers", "Future Work", "Attachment Cards"]
)

with tab_text:
    render_chapter_text(6)

with tab_live:
    st.header("Chapter 6 Live Conclusion Narrative")
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        render_generated_claim_box(
            "chapter6_live_analysis_note",
            generated_chapter6_paragraph(bundle),
            "Conclusion paragraph with live citations",
        )
        render_citation_panel(bundle)
    with right:
        st.markdown("#### Reproducibility evidence")
        artifact_chart(bundle["inventory"])
        st.markdown("#### Stability evidence")
        model_stability_chart(bundle["model_stability"])

with tab_contributions:
    st.header("Six Thesis Contributions")
    contribution_rows = [
        {
            "contribution": "C1 OCR-to-record pipeline",
            "deliverable": "PDF OCR, markdown pages, structured JSON records",
            "evidence": f"{len(bundle['tone_records']):,} tone records; {len(bundle['inventory']):,} result artifacts",
            "status": "Implemented",
        },
        {
            "contribution": "C2 Prompt-driven extraction framework",
            "deliverable": "Zero-shot, few-shot, and chain-of-thought prompt templates",
            "evidence": f"{bundle['tone_records']['prompt'].nunique() if 'prompt' in bundle['tone_records'].columns else 0} prompts represented",
            "status": "Implemented",
        },
        {
            "contribution": "C3 Tone-aware ESG taxonomy",
            "deliverable": "Commitment/action/outcome/none/missing tone schema",
            "evidence": "Tone distribution and tone x ESG matrix",
            "status": "Implemented",
        },
        {
            "contribution": "C4 Ontology-based ABSA layer",
            "deliverable": "Aspect-to-ontology mapping",
            "evidence": f"{len(bundle['ontology']):,} aspect rows",
            "status": "Implemented",
        },
        {
            "contribution": "C5 ClimateBERT comparison framework",
            "deliverable": "Proxy/ClimateBERT agreement metrics",
            "evidence": "Agreement and kappa dashboard",
            "status": "Implemented",
        },
        {
            "contribution": "C6 Explainability and reproducibility module",
            "deliverable": "Artifacts, visual dashboards, logs, and stability tables",
            "evidence": "Artifact inventory and model/prompt stability",
            "status": "Implemented",
        },
    ]
    st.dataframe(pd.DataFrame(contribution_rows), use_container_width=True, hide_index=True, height=260)
    workflow_coverage_chart()
    artifact_chart(bundle["inventory"])

with tab_rqs:
    st.header("Answers to Research Questions")
    rq_rows = [
        {"rq": "RQ1", "answer": "Yes. PDF reports are transformed into source-linked structured ESG records.", "graph": "Workflow coverage and PDF x prompt matrix."},
        {"rq": "RQ2", "answer": "The four-dimensional schema separates aspect, ESG pillar, sentiment, and tone.", "graph": "Tone distribution, ESG distribution, and tone x ESG heatmap."},
        {"rq": "RQ3", "answer": "Yes. Tone labels differ meaningfully from ClimateBERT-style labels.", "graph": "Agreement metrics and tone x ClimateBERT crosstab."},
        {"rq": "RQ4", "answer": "The main weaknesses are schema drift, missing tone, OCR/text quality, and ontology gaps.", "graph": "Failure-mode and ontology coverage charts."},
        {"rq": "RQ5", "answer": "Reproducibility is supported through result artifacts, saved reports, job logs, and dashboards.", "graph": "Artifact inventory."},
        {"rq": "RQ6", "answer": "Model and prompt choices materially affect output stability and completeness.", "graph": "Model and prompt stability charts."},
    ]
    st.dataframe(pd.DataFrame(rq_rows), use_container_width=True, hide_index=True, height=260)
    c1, c2 = st.columns(2)
    with c1:
        agreement_chart(bundle["agreement"])
    with c2:
        ontology_chart(bundle["ontology"])

with tab_future:
    st.header("Future Work Evidence Map")
    future_rows = [
        {"priority": 1, "work": "Expand expert-labelled ground truth", "needed_graph": "Human agreement and confusion matrices."},
        {"priority": 2, "work": "Measure OCR quality directly", "needed_graph": "CER/WER by document and page type."},
        {"priority": 3, "work": "Improve social-pillar recall", "needed_graph": "Social aspect coverage and examples."},
        {"priority": 4, "work": "Add schema validation and retry loops", "needed_graph": "Schema drift before/after validation."},
        {"priority": 5, "work": "Broaden model/prompt stability tests", "needed_graph": "Repeated-run confidence intervals."},
        {"priority": 6, "work": "Extend Indonesian ESG ontology", "needed_graph": "Mapped vs unmapped aspect clusters."},
    ]
    st.dataframe(pd.DataFrame(future_rows), use_container_width=True, hide_index=True, height=260)
    model_stability_chart(bundle["model_stability"])
    prompt_stability_chart(bundle["prompt_stability"])

with tab_cards:
    render_attachment_cards(
        "Chapter 6 Graph + Table Attachment Cards",
        chapter_default="Chapter 6",
        figures=["A.6", "A.7", "A.8", "A.9", "A.10", "A.11", "A.12", "A.13", "A.14", "A.15", "A.16"],
    )
