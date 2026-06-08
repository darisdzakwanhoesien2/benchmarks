from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import (  # noqa: E402
    agreement_chart,
    artifact_chart,
    count_chart,
    data_bundle,
    heatmap_from_table,
    metric_row,
    model_stability_chart,
    ontology_chart,
    prompt_stability_chart,
    render_mermaid,
)


CHAPTER_PATH = ROOT / "chapter5_v4.md"


st.set_page_config(page_title="Chapter 5 - Markdown Discussion", layout="wide")
apply_page_runtime_controls(__file__)


def source_label(*paths: str) -> None:
    joined = " | ".join(paths)
    st.caption(f"Source data: `{joined}`")


def split_markdown_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    last = 0
    for match in pattern.finditer(text):
        if match.start() > last:
            blocks.append(("markdown", text[last:match.start()]))
        blocks.append((match.group(1) or "", match.group(2).strip()))
        last = match.end()
    if last < len(text):
        blocks.append(("markdown", text[last:]))
    return blocks


def render_markdown_chapter(path: Path) -> None:
    if not path.exists():
        st.error(f"Missing chapter source: `{path}`")
        return

    for kind, content in split_markdown_blocks(path.read_text(encoding="utf-8")):
        if not content.strip():
            continue
        if kind == "mermaid":
            render_mermaid(content, height=520)
        elif kind:
            st.code(content, language=kind)
        else:
            st.markdown(content)


def chapter5_summary(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tone = bundle["tone_records"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    inventory = bundle["inventory"]
    failure = bundle["failure_counts"]

    rows = [
        {
            "discussion area": "Tone-bearing evidence",
            "evidence": f"{len(tone):,} extracted tone records in the discussion subset",
            "artifact": "results/visualizations/tone_records_flat.csv",
        },
        {
            "discussion area": "ClimateBERT overlap",
            "evidence": f"{agreement.iloc[0]['cohen_kappa'] if not agreement.empty and 'cohen_kappa' in agreement.columns else 'n/a'} Cohen's kappa in agreement summary",
            "artifact": "results/revision_analysis/climatebert_proxy_agreement_summary.csv",
        },
        {
            "discussion area": "Ontology coverage",
            "evidence": f"{len(ontology):,} ontology coverage rows",
            "artifact": "results/revision_analysis/ontology_coverage.csv",
        },
        {
            "discussion area": "Failure concentration",
            "evidence": f"{len(failure):,} failure-mode summary rows",
            "artifact": "results/revision_analysis/failure_mode_counts.csv",
        },
        {
            "discussion area": "Artifact reproducibility",
            "evidence": f"{len(inventory):,} result artifacts discovered",
            "artifact": "results/**/*",
        },
    ]
    return pd.DataFrame(rows)


bundle = data_bundle()

st.title("Chapter 5 - Discussion")
st.caption("Interactive Streamlit page for `chapter5_v4.md`, with markdown chapter text and live discussion evidence.")
metric_row(bundle)

tab_text, tab_findings, tab_rqs, tab_limits, tab_future = st.tabs(
    ["Chapter Text", "Key Findings", "RQ Resolution", "Limitations", "Future Work and Impact"]
)

with tab_text:
    source_label("chapter5_v4.md")
    render_markdown_chapter(CHAPTER_PATH)

with tab_findings:
    st.header("Key Findings and Synthesis")
    st.dataframe(chapter5_summary(bundle), use_container_width=True, hide_index=True, height=230)
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "tone", "Tone distribution in discussion evidence")
    with c2:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "esg", "ESG pillar distribution in discussion evidence")

    source_label("results/visualizations/tone_esg_crosstab.csv")
    heatmap_from_table(bundle["tone_esg"], "tone", "Tone x ESG pillar")

with tab_rqs:
    st.header("Research Question Resolution")
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/revision_analysis/climatebert_proxy_agreement_summary.csv")
        agreement_chart(bundle["agreement"])
    with c2:
        source_label("results/revision_analysis/ontology_coverage.csv")
        ontology_chart(bundle["ontology"])

    c3, c4 = st.columns(2)
    with c3:
        source_label(
            "results/revision_analysis/model_stability_summary.csv",
            "results/esg_records.json",
        )
        model_stability_chart(bundle["model_stability"])
    with c4:
        source_label("results/revision_analysis/prompt_stability_summary.csv")
        prompt_stability_chart(bundle["prompt_stability"])

with tab_limits:
    st.header("Limitations and Diagnostic Concentration")
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/revision_analysis/failure_mode_counts.csv")
        count_chart(bundle["failure_counts"], "mode", "Failure mode frequency")
    with c2:
        source_label("results/revision_analysis/ontology_coverage.csv")
        ontology_chart(bundle["ontology"])

    st.info(
        "This chapter frames the current system as strong enough for executable ESG evidence extraction, "
        "but still limited by weak-label reference construction, prompt/model sensitivity, and tone instability."
    )

with tab_future:
    st.header("Future Work, Reproducibility, and Broader Impact")
    source_label("results/**/*")
    artifact_chart(bundle["inventory"])
    st.subheader("Discussion-ready interpretation")
    st.write(
        "The current evidence supports future work on stronger human annotation, stricter tone-schema validation, "
        "direct OCR quality benchmarking, one-to-one ClimateBERT comparison, and more cautious deployment of "
        "greenwashing-style indicators."
    )
