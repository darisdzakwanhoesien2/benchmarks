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
    data_bundle,
    metric_row,
    model_stability_chart,
    ontology_chart,
    prompt_stability_chart,
    render_mermaid,
)


CHAPTER_PATH = ROOT / "chapter6_v2.md"


st.set_page_config(page_title="Chapter 6 - Markdown Conclusion", layout="wide")
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


def chapter6_summary(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tone = bundle["tone_records"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    inventory = bundle["inventory"]

    rows = [
        {
            "contribution": "Document-to-record pipeline",
            "evidence": f"{len(tone):,} tone-bearing records available for synthesis",
            "artifact": "results/visualizations/tone_records_flat.csv",
        },
        {
            "contribution": "Record-level ESG schema",
            "evidence": f"{bundle['tone_esg'].shape[0]:,} tone x ESG rows in the summary table",
            "artifact": "results/visualizations/tone_esg_crosstab.csv",
        },
        {
            "contribution": "Comparative validation",
            "evidence": f"{agreement.iloc[0]['cohen_kappa'] if not agreement.empty and 'cohen_kappa' in agreement.columns else 'n/a'} Cohen's kappa",
            "artifact": "results/revision_analysis/climatebert_proxy_agreement_summary.csv",
        },
        {
            "contribution": "Ontology-oriented interpretation",
            "evidence": f"{len(ontology):,} ontology coverage rows",
            "artifact": "results/revision_analysis/ontology_coverage.csv",
        },
        {
            "contribution": "Reproducibility",
            "evidence": f"{len(inventory):,} discoverable result artifacts",
            "artifact": "results/**/*",
        },
    ]
    return pd.DataFrame(rows)


bundle = data_bundle()

st.title("Chapter 6 - Conclusion")
st.caption("Interactive Streamlit page for `chapter6_v2.md`, with markdown chapter text and live conclusion evidence.")
metric_row(bundle)

tab_text, tab_summary, tab_rqs, tab_future = st.tabs(
    ["Chapter Text", "Contribution Summary", "RQ Answers", "Future Work"]
)

with tab_text:
    source_label("chapter6_v2.md")
    render_markdown_chapter(CHAPTER_PATH)

with tab_summary:
    st.header("Contribution Summary")
    st.dataframe(chapter6_summary(bundle), use_container_width=True, hide_index=True, height=240)
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/visualizations/tone_records_flat.csv")
        model_stability_chart(bundle["model_stability"])
    with c2:
        source_label("results/revision_analysis/ontology_coverage.csv")
        ontology_chart(bundle["ontology"])

with tab_rqs:
    st.header("Research Question Answers")
    c1, c2 = st.columns(2)
    with c1:
        source_label("results/revision_analysis/climatebert_proxy_agreement_summary.csv")
        agreement_chart(bundle["agreement"])
    with c2:
        source_label("results/revision_analysis/prompt_stability_summary.csv")
        prompt_stability_chart(bundle["prompt_stability"])

    st.info(
        "The conclusion frames the thesis as feasible, useful, and auditable, while still dependent on stronger "
        "benchmark labels and OCR measurement before broader generalization."
    )

with tab_future:
    st.header("Future Work and Impact")
    source_label("results/**/*")
    artifact_chart(bundle["inventory"])
    st.write(
        "Priority follow-ups remain: larger expert-labeled benchmarks, formal OCR quality measurement, "
        "ontology expansion, multilingual model improvement, and full one-to-one ClimateBERT evaluation."
    )
