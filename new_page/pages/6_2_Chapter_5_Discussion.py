from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import (  # noqa: E402
    agreement_chart,
    count_chart,
    data_bundle,
    heatmap_from_table,
    metric_row,
    model_stability_chart,
    ontology_chart,
    prompt_stability_chart,
    render_chapter_text,
)


st.set_page_config(page_title="Chapter 5 - Discussion", layout="wide")

bundle = data_bundle()

st.title("Chapter 5 - Discussion")
st.caption("Discussion chapter translated into an interactive page with the supporting result graphs beside the interpretation.")
metric_row(bundle)

tab_text, tab_findings, tab_limitations = st.tabs(["Chapter Text", "Key Findings", "Limitations and Diagnostics"])

with tab_text:
    render_chapter_text(5)

with tab_findings:
    st.header("Interpretation of Key Findings")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Commitment dominance")
        st.write(
            "The chapter frames commitment as the largest disclosure tone and reads this as a legitimacy signal: "
            "companies often state strategic intent before reporting measurable outcomes."
        )
        count_chart(bundle["tone_records"], "tone", "Tone distribution")
    with c2:
        st.subheader("Environmental and governance concentration")
        st.write(
            "The ESG distribution is not balanced. Environmental and governance claims dominate the extracted record set, "
            "while social disclosures are underrepresented."
        )
        count_chart(bundle["tone_records"], "esg", "ESG pillar distribution")

    st.subheader("Tone x ESG matrix")
    heatmap_from_table(bundle["tone_esg"], "tone", "Tone x ESG pillar")

    st.subheader("ClimateBERT kappa divergence")
    st.write(
        "The discussion treats low real ClimateBERT kappa as a positive construct-validity finding: tone labels and "
        "climate-commitment labels are related but not interchangeable."
    )
    agreement_chart(bundle["agreement"])

with tab_limitations:
    st.header("Limitations and Diagnostic Evidence")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Prompt and model sensitivity")
        prompt_stability_chart(bundle["prompt_stability"])
        model_stability_chart(bundle["model_stability"])
    with c2:
        st.subheader("Ontology scope for Indonesian disclosure")
        ontology_chart(bundle["ontology"])

    st.subheader("Failure-mode evidence")
    failure = bundle["failure_counts"]
    if not failure.empty:
        st.dataframe(failure, use_container_width=True, height=260)
    else:
        st.info("No failure-mode count table found.")

    st.subheader("Discussion-ready diagnostic notes")
    st.info(
        "Use this section to connect evidence to the chapter limitations: human-label scale, social-pillar sparsity, "
        "unmeasured OCR quality, prompt sensitivity, ClimateBERT construct mismatch, and ontology coverage gaps."
    )
