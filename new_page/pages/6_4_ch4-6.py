from __future__ import annotations

from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_ROOT = ROOT.parent
SOURCE_DOCX = BENCHMARKS_ROOT / "pages" / "thesis_ch4_6_structure_benchmarks.docx"
UPDATED_DOCX = BENCHMARKS_ROOT / "pages" / "thesis_ch4_6_structure_benchmarks_streamlit_graphs.docx"
GRAPH_DIR = ROOT / "results" / "docx_graph_attachments"
VIS = ROOT / "results" / "visualizations"
TOOLS = ROOT / "tools"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(TOOLS))

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
    workflow_coverage_chart,
)


st.set_page_config(page_title="Ch4-6 Benchmarks + DOCX Graphs", layout="wide")


def read_docx_paragraphs(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame([{"paragraph": 0, "text": f"Missing DOCX: {path}", "section": "missing"}])
    try:
        with ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
    except Exception as exc:
        return pd.DataFrame([{"paragraph": 0, "text": f"Could not read DOCX: {exc}", "section": "error"}])

    rows = []
    current = "Front matter"
    for idx, para in enumerate(root.findall(f".//{W_NS}p"), start=1):
        text = "".join(t.text or "" for t in para.findall(f".//{W_NS}t")).strip()
        if not text:
            continue
        if (
            text.startswith(("IV.", "V.", "VI.", "A."))
            or text.startswith(("4.", "5.", "6."))
            or "Appendix" in text
        ):
            current = text
        rows.append({"paragraph": idx, "section": current, "text": text})
    return pd.DataFrame(rows)


def media_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with ZipFile(path) as zf:
            return len([name for name in zf.namelist() if name.startswith("word/media/")])
    except Exception:
        return 0


def graph_manifest() -> pd.DataFrame:
    rows = [
        {"figure": "A.1", "title": "Tone distribution", "path": VIS / "tone_distribution.png", "chapter": "Chapter 4", "rq": "RQ2"},
        {"figure": "A.2", "title": "ESG by tone", "path": VIS / "esg_by_tone.png", "chapter": "Chapter 4", "rq": "RQ2"},
        {"figure": "A.3", "title": "Aspect by tone heatmap", "path": VIS / "aspect_by_tone_heatmap.png", "chapter": "Chapter 4", "rq": "RQ2"},
        {"figure": "A.4", "title": "Tone by ClimateBERT label", "path": VIS / "climatebert_label_by_tone.png", "chapter": "Chapter 4 / 5", "rq": "RQ3"},
        {"figure": "A.5", "title": "Top-scoring ClimateBERT records", "path": VIS / "climatebert_remote_top_scores.png", "chapter": "Chapter 5", "rq": "RQ3"},
        {"figure": "A.6", "title": "Streamlit overview", "path": VIS / "streamlit_outputs" / "01_overview.png", "chapter": "Chapter 6", "rq": "RQ5"},
        {"figure": "A.7", "title": "Per-RQ evidence", "path": VIS / "streamlit_outputs" / "02_per_rq_evidence.png", "chapter": "Chapter 4 / 6", "rq": "RQ1-RQ6"},
        {"figure": "A.8", "title": "Benchmark plan", "path": VIS / "streamlit_outputs" / "04_benchmarks.png", "chapter": "Chapter 4 / 6", "rq": "RQ6"},
        {"figure": "A.9", "title": "Evidence matrix", "path": VIS / "streamlit_outputs" / "07_evidence_matrix.png", "chapter": "Chapter 6", "rq": "RQ5"},
        {"figure": "A.10", "title": "Model parse success benchmark", "path": GRAPH_DIR / "docx_model_parse_success.png", "chapter": "Chapter 4 / 6", "rq": "RQ6"},
        {"figure": "A.11", "title": "Prompt missing-tone benchmark", "path": GRAPH_DIR / "docx_prompt_missing_tone_rate.png", "chapter": "Chapter 5 / 6", "rq": "RQ6"},
        {"figure": "A.12", "title": "Ontology mapped vs novel aspects", "path": GRAPH_DIR / "docx_ontology_mapped_vs_unmapped.png", "chapter": "Chapter 5 / 6", "rq": "RQ4"},
    ]
    df = pd.DataFrame(rows)
    df["exists"] = df["path"].map(lambda p: Path(p).exists())
    df["path"] = df["path"].astype(str)
    return df


def regenerate_docx() -> Path:
    from update_ch4_6_docx_graphs import update_document

    return update_document()


bundle = data_bundle()

st.title("Ch4-6 Structure Benchmarks and Graph Attachments")
st.caption(
    "Streamlit reader for `thesis_ch4_6_structure_benchmarks.docx`, the updated graph-attached DOCX, "
    "and the live evidence used by pages/6_1, pages/6_2, and pages/6_3."
)
metric_row(bundle)

st.divider()

doc_cols = st.columns([2, 2, 1, 1])
doc_cols[0].markdown(f"**Source DOCX:** `{SOURCE_DOCX}`")
doc_cols[1].markdown(f"**Updated DOCX:** `{UPDATED_DOCX}`")
doc_cols[2].metric("Embedded graphs", media_count(UPDATED_DOCX))
doc_cols[3].metric("Graph files", int(graph_manifest()["exists"].sum()))

action_cols = st.columns([1, 1, 2])
with action_cols[0]:
    if st.button("Regenerate updated DOCX", type="primary", use_container_width=True):
        try:
            out = regenerate_docx()
            st.success(f"Updated DOCX generated: {out}")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not regenerate DOCX: {exc}")
with action_cols[1]:
    if UPDATED_DOCX.exists():
        st.download_button(
            "Download updated DOCX",
            UPDATED_DOCX.read_bytes(),
            UPDATED_DOCX.name,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    else:
        st.info("Generate the updated DOCX first.")
with action_cols[2]:
    st.info(
        "This page mirrors the Word appendix: Chapter 4 receives empirical result graphs, "
        "Chapter 5 receives validation/diagnostic graphs, and Chapter 6 receives benchmark and contribution evidence."
    )

tab_summary, tab_docx, tab_graphs, tab_chapters, tab_live = st.tabs(
    ["DOCX Summary", "DOCX Structure", "Graph Attachments", "Chapter 4-6 Mapping", "Live Charts"]
)

with tab_summary:
    st.header("DOCX Evidence Summary")
    summary_rows = [
        {"item": "Source document", "value": str(SOURCE_DOCX), "status": "found" if SOURCE_DOCX.exists() else "missing"},
        {"item": "Updated document", "value": str(UPDATED_DOCX), "status": "found" if UPDATED_DOCX.exists() else "missing"},
        {"item": "Embedded media", "value": media_count(UPDATED_DOCX), "status": "expected: 12"},
        {"item": "Generated benchmark graph folder", "value": str(GRAPH_DIR), "status": "found" if GRAPH_DIR.exists() else "missing"},
    ]
    st.dataframe(pd.DataFrame(summary_rows).astype(str), use_container_width=True, hide_index=True, height=180)

    st.subheader("What the DOCX update adds")
    st.markdown(
        """
        - **Appendix A.1** live evidence snapshot from the shared result bundle.
        - **Appendix A.2** mapping from Streamlit pages `6_1`, `6_2`, and `6_3` to thesis chapter roles.
        - **Appendix A.3** attached graph register with 12 graph images.
        - **Appendix A.4** chapter-level insertion notes.
        - **Appendix A.5** benchmark checklist still needed for stronger thesis claims.
        """
    )

with tab_docx:
    st.header("DOCX Structure Reader")
    selected_doc = st.radio(
        "Document to inspect",
        ["Updated graph-attached DOCX", "Original source DOCX"],
        horizontal=True,
    )
    doc_path = UPDATED_DOCX if selected_doc.startswith("Updated") else SOURCE_DOCX
    doc_df = read_docx_paragraphs(doc_path)
    search = st.text_input("Search DOCX text", placeholder="Example: RQ3, ClimateBERT, Appendix, benchmark")
    display = doc_df.copy()
    if search.strip():
        display = display[display.astype(str).apply(lambda col: col.str.contains(search.strip(), case=False, regex=False)).any(axis=1)]
    st.dataframe(display, use_container_width=True, hide_index=True, height=560)

with tab_graphs:
    st.header("Graph Attachments")
    manifest = graph_manifest()
    c1, c2, c3 = st.columns(3)
    chapter_filter = c1.selectbox("Chapter", ["All"] + sorted(manifest["chapter"].unique().tolist()))
    rq_filter = c2.selectbox("RQ", ["All"] + sorted(manifest["rq"].unique().tolist()))
    only_existing = c3.toggle("Only existing files", value=True)
    filtered = manifest.copy()
    if chapter_filter != "All":
        filtered = filtered[filtered["chapter"].eq(chapter_filter)]
    if rq_filter != "All":
        filtered = filtered[filtered["rq"].eq(rq_filter)]
    if only_existing:
        filtered = filtered[filtered["exists"]]
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=260)

    cols = st.columns(2)
    for idx, row in filtered.iterrows():
        path = Path(row["path"])
        with cols[idx % 2]:
            st.subheader(f"{row['figure']} - {row['title']}")
            st.caption(f"{row['chapter']} | {row['rq']} | `{path}`")
            if path.exists():
                st.image(str(path), use_container_width=True)
            else:
                st.warning("Missing graph file.")

with tab_chapters:
    st.header("Chapter 4-6 Mapping")
    mapping = pd.DataFrame(
        [
            {
                "chapter": "Chapter 4 - Implementation and Results",
                "streamlit page": "pages/6_1_Chapter_4_Implementation_Results.py",
                "primary evidence": "tone records, PDF x prompt matrix, tone/ESG distributions, ClimateBERT crosstab, artifact/model/prompt stability",
                "figures": "A.1, A.2, A.3, A.4, A.7, A.8, A.10",
            },
            {
                "chapter": "Chapter 5 - Discussion",
                "streamlit page": "pages/6_2_Chapter_5_Discussion.py",
                "primary evidence": "agreement metrics, ontology coverage, failure modes, prompt/model sensitivity",
                "figures": "A.4, A.5, A.11, A.12",
            },
            {
                "chapter": "Chapter 6 - Conclusion",
                "streamlit page": "pages/6_3_Chapter_6_Conclusion.py",
                "primary evidence": "contribution summary, RQ answers, artifact inventory, future-work benchmark checklist",
                "figures": "A.6, A.7, A.8, A.9, A.10, A.11, A.12",
            },
        ]
    )
    st.dataframe(mapping, use_container_width=True, hide_index=True, height=260)

    st.subheader("Benchmark checklist still needed")
    checklist = pd.DataFrame(
        [
            {"benchmark": "OCR quality", "why needed": "CER/WER is not yet measured.", "target artifact": "ocr_quality_by_page.csv"},
            {"benchmark": "Human annotation agreement", "why needed": "Single-annotator labels need reliability evidence.", "target artifact": "human_agreement_summary.csv"},
            {"benchmark": "Repeated LLM runs", "why needed": "Model/prompt stability needs confidence intervals.", "target artifact": "model_prompt_repeated_run_ci.csv"},
            {"benchmark": "ClimateBERT baseline", "why needed": "Compare tone-vs-ClimateBERT to majority and human-labelled baselines.", "target artifact": "climatebert_baseline_comparison.csv"},
            {"benchmark": "Ontology extension", "why needed": "Formalise unmapped Indonesian ESG aspects.", "target artifact": "indonesian_esg_ontology_extension.csv"},
        ]
    )
    st.dataframe(checklist, use_container_width=True, hide_index=True, height=240)

with tab_live:
    st.header("Live Charts from the Chapter Pages")
    live_tabs = st.tabs(["Chapter 4", "Chapter 5", "Chapter 6"])
    with live_tabs[0]:
        st.subheader("Chapter 4 result evidence")
        c1, c2 = st.columns(2)
        with c1:
            count_chart(bundle["tone_records"], "tone", "Tone distribution")
        with c2:
            count_chart(bundle["tone_records"], "esg", "ESG pillar distribution")
        heatmap_from_table(bundle["tone_esg"], "tone", "Tone x ESG pillar")
    with live_tabs[1]:
        st.subheader("Chapter 5 discussion evidence")
        c1, c2 = st.columns(2)
        with c1:
            agreement_chart(bundle["agreement"])
        with c2:
            ontology_chart(bundle["ontology"])
        prompt_stability_chart(bundle["prompt_stability"])
    with live_tabs[2]:
        st.subheader("Chapter 6 conclusion evidence")
        workflow_coverage_chart()
        c1, c2 = st.columns(2)
        with c1:
            artifact_chart(bundle["inventory"])
        with c2:
            model_stability_chart(bundle["model_stability"])
