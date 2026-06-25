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
    image_or_info,
    metric_row,
    model_stability_chart,
    ontology_chart,
    pdf_prompt_heatmap,
    prompt_stability_chart,
    render_mermaid,
    workflow_coverage_chart,
    VIS,
)


CHAPTER_PATH = ROOT / "chapter4_v4.md"


st.set_page_config(page_title="Chapter 4 - Markdown Results", layout="wide")
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


def chapter4_summary(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tone = bundle["tone_records"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    inventory = bundle["inventory"]
    prompt = bundle["prompt_stability"]
    models = bundle["model_stability"]

    agreement_n = ""
    if not agreement.empty and "n" in agreement.columns:
        agreement_n = str(agreement.iloc[0]["n"])

    rows = [
        {
            "result area": "Structured tone evidence",
            "evidence": f"{len(tone):,} extracted tone records",
            "artifact": "results/visualizations/tone_records_flat.csv",
        },
        {
            "result area": "Prompt stability",
            "evidence": f"{len(prompt):,} prompt rows in stability summary",
            "artifact": "results/revision_analysis/prompt_stability_summary.csv",
        },
        {
            "result area": "Model stability",
            "evidence": f"{models['model'].nunique() if 'model' in models.columns else 0:,} visible model configurations",
            "artifact": "results/revision_analysis/model_stability_summary.csv + results/esg_records.json",
        },
        {
            "result area": "ClimateBERT comparison",
            "evidence": f"{agreement_n or 'n/a'} records in the agreement summary",
            "artifact": "results/revision_analysis/climatebert_proxy_agreement_summary.csv",
        },
        {
            "result area": "Ontology coverage",
            "evidence": f"{len(ontology):,} ontology coverage rows",
            "artifact": "results/revision_analysis/ontology_coverage.csv",
        },
        {
            "result area": "Reproducibility store",
            "evidence": f"{len(inventory):,} result artifacts discovered",
            "artifact": "results/**/*",
        },
    ]
    return pd.DataFrame(rows)


bundle = data_bundle()

st.title("Chapter 4 - Implementation, Results, and Evaluation")
st.caption("Interactive Streamlit page for `chapter4_v4.md`, with markdown chapter text and live result evidence.")
metric_row(bundle)

tab_text, tab_rq12, tab_rq34, tab_rq56, tab_figures = st.tabs(
    ["Chapter Text", "RQ1-RQ2", "RQ3-RQ4", "RQ5-RQ6", "Figure Gallery"]
)

with tab_text:
    source_label("chapter4_v4.md")
    render_markdown_chapter(CHAPTER_PATH)

with tab_rq12:
    st.header("RQ1-RQ2: PDF-to-Structured ESG Evidence and Tone-Aware Schema")
    st.dataframe(chapter4_summary(bundle), use_container_width=True, hide_index=True, height=260)
    source_label("code/thesis_chapter_streamlit.py::workflow_rq_df()")
    workflow_coverage_chart()

    source_label("results/visualizations/tone_records_flat.csv")
    pdf_prompt_heatmap(bundle["tone_records"])

    c1, c2 = st.columns(2)
    with c1:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "tone", "Tone distribution")
    with c2:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "esg", "ESG pillar distribution")

with tab_rq34:
    st.header("RQ3-RQ4: ClimateBERT Comparison, Diagnostics, and Failure Modes")
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/visualizations/tone_climatebert_label_crosstab.csv")
        heatmap_from_table(bundle["tone_climatebert"], "tone", "Tone x ClimateBERT/proxy label")
    with c2:
        source_label("results/revision_analysis/climatebert_proxy_agreement_summary.csv")
        agreement_chart(bundle["agreement"])

    c3, c4 = st.columns(2)
    with c3:
        source_label("results/revision_analysis/failure_mode_counts.csv")
        count_chart(bundle["failure_counts"], "mode", "Failure mode frequency")
    with c4:
        source_label("results/revision_analysis/ontology_coverage.csv")
        ontology_chart(bundle["ontology"])

with tab_rq56:
    st.header("RQ5-RQ6: Reproducibility, Visualization, and Stability")
    c1, c2 = st.columns(2)
    with c1:
        source_label(
            "results/revision_analysis/model_stability_summary.csv",
            "results/esg_records.json",
        )
        model_stability_chart(bundle["model_stability"])
    with c2:
        source_label("results/revision_analysis/prompt_stability_summary.csv")
        prompt_stability_chart(bundle["prompt_stability"])

    source_label("results/**/*")
    artifact_chart(bundle["inventory"])

with tab_figures:
    st.header("Saved Graph Attachments")
    images = [
        ("tone_distribution.png", "Tone distribution", "results/visualizations/tone_distribution.png"),
        ("esg_by_tone.png", "ESG by tone", "results/visualizations/esg_by_tone.png"),
        ("aspect_by_tone_heatmap.png", "Aspect by tone heatmap", "results/visualizations/aspect_by_tone_heatmap.png"),
        ("climatebert_label_by_tone.png", "ClimateBERT label by tone", "results/visualizations/climatebert_label_by_tone.png"),
        ("climatebert_remote_top_scores.png", "ClimateBERT top scores", "results/visualizations/climatebert_remote_top_scores.png"),
    ]
    cols = st.columns(2)
    for idx, (name, caption, source_path) in enumerate(images):
        with cols[idx % 2]:
            source_label(source_path)
            image_or_info(VIS / name, caption)
