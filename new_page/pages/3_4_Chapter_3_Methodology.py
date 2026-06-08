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
    artifact_chart,
    count_chart,
    data_bundle,
    metric_row,
    model_stability_chart,
    ontology_chart,
    prompt_stability_chart,
    render_mermaid,
    workflow_coverage_chart,
)


CHAPTER_PATH = ROOT / "chapter3_v4.md"


st.set_page_config(page_title="Chapter 3 - Methodology", layout="wide")
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


def methodology_summary(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tone = bundle["tone_records"]
    ocr = bundle["ocr"]
    prompt = bundle["prompt_stability"]
    ontology = bundle["ontology"]
    inventory = bundle["inventory"]

    rows = [
        {
            "component": "OCR-expanded corpus",
            "evidence": f"{len(ocr):,} OCR documents in the processing summary",
            "artifact": "results/revision_analysis/ocr_processing_summary.csv",
        },
        {
            "component": "Structured ESG records",
            "evidence": f"{len(tone):,} extracted tone records",
            "artifact": "results/visualizations/tone_records_flat.csv",
        },
        {
            "component": "Prompt comparison layer",
            "evidence": f"{prompt['prompt'].nunique() if 'prompt' in prompt.columns else 0:,} prompts in stability tables",
            "artifact": "results/revision_analysis/prompt_stability_summary.csv",
        },
        {
            "component": "Ontology alignment layer",
            "evidence": f"{len(ontology):,} ontology coverage rows",
            "artifact": "results/revision_analysis/ontology_coverage.csv",
        },
        {
            "component": "Reproducibility store",
            "evidence": f"{len(inventory):,} result artifacts discovered",
            "artifact": "results/*",
        },
    ]
    return pd.DataFrame(rows)


bundle = data_bundle()

st.title("Chapter 3 - Methodology")
st.caption("Interactive Streamlit page for `chapter3_v4.md`, with markdown chapter text and live repository evidence.")
metric_row(bundle)

tab_text, tab_design, tab_data, tab_features, tab_repro = st.tabs(
    ["Chapter Text", "Research Design", "Data Sources", "Feature and Framework", "Reproducibility"]
)

with tab_text:
    source_label("chapter3_v4.md")
    render_markdown_chapter(CHAPTER_PATH)

with tab_design:
    st.header("Research Design and Pipeline Logic")
    st.write(
        "This view ties the methodology narrative to executable repository evidence: staged processing, "
        "comparative prompts, ontology alignment, and result persistence."
    )
    source_label("code/thesis_chapter_streamlit.py::workflow_rq_df()")
    workflow_coverage_chart()
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "prompt", "Prompt usage across extracted records", top_n=12)
    with c2:
        source_label(
            "results/revision_analysis/model_stability_summary.csv",
            "results/esg_records.json",
        )
        model_stability_chart(bundle["model_stability"])

with tab_data:
    st.header("Data Sources and Corpus Evidence")
    st.dataframe(methodology_summary(bundle), use_container_width=True, hide_index=True, height=220)
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "target_doc", "Top source documents by extracted records", top_n=15)
    with c2:
        source_label("results/visualizations/tone_records_flat.csv")
        count_chart(bundle["tone_records"], "esg", "ESG pillar distribution in extracted records")

with tab_features:
    st.header("Feature Extraction and Proposed Framework")
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/revision_analysis/ontology_coverage.csv")
        ontology_chart(bundle["ontology"])
    with c2:
        source_label("results/revision_analysis/prompt_stability_summary.csv")
        prompt_stability_chart(bundle["prompt_stability"])

    st.subheader("Methodological framing")
    st.info(
        "Chapter 3 describes a mixed executable methodology: OCR expansion, page-aware LLM extraction, "
        "weak-label benchmarking, ontology alignment, and iterative audit through Streamlit tooling."
    )

with tab_repro:
    st.header("Reproducibility and Artifact Persistence")
    source_label("results/**/*")
    artifact_chart(bundle["inventory"])
    st.subheader("Current artifact inventory")
    if bundle["inventory"].empty:
        st.info("No result artifacts found.")
    else:
        st.dataframe(
            bundle["inventory"].sort_values(["group", "extension", "path"]).head(200),
            use_container_width=True,
            hide_index=True,
            height=360,
        )
