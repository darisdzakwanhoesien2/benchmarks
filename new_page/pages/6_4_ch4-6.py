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
        {
            "figure": "A.1",
            "title": "Tone distribution",
            "path": VIS / "tone_distribution.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "tone_records_flat.csv",
            "source page": "pages/6_1_Chapter_4_Implementation_Results.py",
        },
        {
            "figure": "A.2",
            "title": "ESG by tone",
            "path": VIS / "esg_by_tone.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "tone_esg_crosstab.csv",
            "source page": "pages/6_1_Chapter_4_Implementation_Results.py",
        },
        {
            "figure": "A.3",
            "title": "Aspect by tone heatmap",
            "path": VIS / "aspect_by_tone_heatmap.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "aspect_tone_crosstab.csv",
            "source page": "pages/6_1_Chapter_4_Implementation_Results.py",
        },
        {
            "figure": "A.4",
            "title": "Tone by ClimateBERT label",
            "path": VIS / "climatebert_label_by_tone.png",
            "chapter": "Chapter 4 / 5",
            "rq": "RQ3",
            "source table": "tone_climatebert_label_crosstab.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.5",
            "title": "Top-scoring ClimateBERT records",
            "path": VIS / "climatebert_remote_top_scores.png",
            "chapter": "Chapter 5",
            "rq": "RQ3",
            "source table": "climatebert_remote_flat.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.6",
            "title": "Streamlit overview",
            "path": VIS / "streamlit_outputs" / "01_overview.png",
            "chapter": "Chapter 6",
            "rq": "RQ5",
            "source table": "DOCX evidence summary",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.7",
            "title": "Per-RQ evidence",
            "path": VIS / "streamlit_outputs" / "02_per_rq_evidence.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ1-RQ6",
            "source table": "chapter-to-RQ mapping",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.8",
            "title": "Benchmark plan",
            "path": VIS / "streamlit_outputs" / "04_benchmarks.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ6",
            "source table": "benchmark checklist",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.9",
            "title": "Evidence matrix",
            "path": VIS / "streamlit_outputs" / "07_evidence_matrix.png",
            "chapter": "Chapter 6",
            "rq": "RQ5",
            "source table": "graph manifest",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.10",
            "title": "Model parse success benchmark",
            "path": GRAPH_DIR / "docx_model_parse_success.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ6",
            "source table": "model_stability_summary.csv",
            "source page": "pages/6_3_Chapter_6_Conclusion.py",
        },
        {
            "figure": "A.11",
            "title": "Prompt missing-tone benchmark",
            "path": GRAPH_DIR / "docx_prompt_missing_tone_rate.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ6",
            "source table": "prompt_stability_summary.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.12",
            "title": "Ontology mapped vs novel aspects",
            "path": GRAPH_DIR / "docx_ontology_mapped_vs_unmapped.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ4",
            "source table": "ontology_coverage.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
    ]
    df = pd.DataFrame(rows)
    df["exists"] = df["path"].map(lambda p: Path(p).exists())
    df["path"] = df["path"].astype(str)
    return df


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def source_dataframe_for_figure(row: pd.Series, bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    figure = str(row["figure"])
    if figure == "A.1":
        df = bundle["tone_records"]
        if df.empty or "tone" not in df.columns:
            return pd.DataFrame()
        return df["tone"].astype(str).replace("", "missing").value_counts().rename_axis("tone").reset_index(name="records")
    if figure == "A.2":
        return load_csv(VIS / "tone_esg_crosstab.csv")
    if figure == "A.3":
        return load_csv(VIS / "aspect_tone_crosstab.csv")
    if figure == "A.4":
        return load_csv(VIS / "tone_climatebert_label_crosstab.csv")
    if figure == "A.5":
        df = load_csv(VIS / "climatebert_remote_flat.csv")
        return df.head(30) if not df.empty else df
    if figure == "A.6":
        return docx_snapshot_rows(bundle)
    if figure == "A.7":
        return chapter_mapping_rows()
    if figure == "A.8":
        return benchmark_checklist_rows()
    if figure == "A.9":
        return graph_manifest()[["figure", "title", "chapter", "rq", "source table", "source page", "exists"]]
    if figure == "A.10":
        return load_csv(ROOT / "results" / "revision_analysis" / "model_stability_summary.csv")
    if figure == "A.11":
        return load_csv(ROOT / "results" / "revision_analysis" / "prompt_stability_summary.csv")
    if figure == "A.12":
        return load_csv(ROOT / "results" / "revision_analysis" / "ontology_coverage.csv")
    return pd.DataFrame()


def docx_snapshot_rows(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tone = bundle["tone_records"]
    ocr = bundle["ocr"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    model = bundle["model_stability"]
    prompt = bundle["prompt_stability"]
    pages = pd.to_numeric(ocr.get("pages", pd.Series(dtype=float)), errors="coerce").sum() if not ocr.empty else 0
    mapped = int(ontology.get("mapped_to_ontology", pd.Series(dtype=bool)).astype(bool).sum()) if not ontology.empty and "mapped_to_ontology" in ontology.columns else 0
    kappa = pd.to_numeric(agreement.get("cohen_kappa", pd.Series(dtype=float)), errors="coerce")
    pct = pd.to_numeric(agreement.get("percent_agreement", pd.Series(dtype=float)), errors="coerce")
    return pd.DataFrame(
        [
            {
                "metric": "Tone records",
                "value": f"{len(tone):,}",
                "existing data": "tone_records_flat.csv",
                "redirect page": "pages/6_1_Chapter_4_Implementation_Results.py",
            },
            {
                "metric": "Source documents",
                "value": f"{max(tone['target_doc'].nunique() if not tone.empty and 'target_doc' in tone.columns else 0, len(ocr)):,}",
                "existing data": "ocr_processing_summary.csv",
                "redirect page": "pages/6_1_Chapter_4_Implementation_Results.py",
            },
            {
                "metric": "OCR pages",
                "value": f"{int(pages):,}",
                "existing data": "ocr_processing_summary.csv",
                "redirect page": "pages/2_4_PDF_Page_Processing_Audit.py",
            },
            {
                "metric": "Prompt templates",
                "value": f"{max(tone['prompt'].nunique() if not tone.empty and 'prompt' in tone.columns else 0, len(prompt)):,}",
                "existing data": "prompt_stability_summary.csv",
                "redirect page": "pages/6_3_Chapter_6_Conclusion.py",
            },
            {
                "metric": "Model rows",
                "value": f"{len(model):,}",
                "existing data": "model_stability_summary.csv",
                "redirect page": "pages/6_3_Chapter_6_Conclusion.py",
            },
            {
                "metric": "ClimateBERT/proxy agreement",
                "value": f"{pct.iloc[0]:.1%}" if not pct.empty and pd.notna(pct.iloc[0]) else "n/a",
                "existing data": "climatebert_proxy_agreement_summary.csv",
                "redirect page": "pages/6_2_Chapter_5_Discussion.py",
            },
            {
                "metric": "Cohen kappa",
                "value": f"{kappa.iloc[0]:.3f}" if not kappa.empty and pd.notna(kappa.iloc[0]) else "n/a",
                "existing data": "climatebert_proxy_agreement_summary.csv",
                "redirect page": "pages/6_2_Chapter_5_Discussion.py",
            },
            {
                "metric": "Ontology mapped rows",
                "value": f"{mapped}/{len(ontology):,}" if len(ontology) else "n/a",
                "existing data": "ontology_coverage.csv",
                "redirect page": "pages/6_2_Chapter_5_Discussion.py",
            },
        ]
    )


def chapter_mapping_rows() -> pd.DataFrame:
    return pd.DataFrame(
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


def benchmark_checklist_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"benchmark": "OCR quality", "why needed": "CER/WER is not yet measured.", "target artifact": "ocr_quality_by_page.csv", "redirect page": "pages/1_2_OCR_Quality_Workbench.py"},
            {"benchmark": "Human annotation agreement", "why needed": "Single-annotator labels need reliability evidence.", "target artifact": "human_agreement_summary.csv", "redirect page": "pages/1_1_Ground_Truth_Workbench.py"},
            {"benchmark": "Repeated LLM runs", "why needed": "Model/prompt stability needs confidence intervals.", "target artifact": "model_prompt_repeated_run_ci.csv", "redirect page": "pages/2_3_LLM_Background_Run_Monitor.py"},
            {"benchmark": "ClimateBERT baseline", "why needed": "Compare tone-vs-ClimateBERT to majority and human-labelled baselines.", "target artifact": "climatebert_baseline_comparison.csv", "redirect page": "pages/1_4_ClimateBERT_Record_Batch.py"},
            {"benchmark": "Ontology extension", "why needed": "Formalise unmapped Indonesian ESG aspects.", "target artifact": "indonesian_esg_ontology_extension.csv", "redirect page": "pages/1_6_Ontology_Path_Viewer.py"},
        ]
    )


def page_slug(page: str) -> str:
    stem = Path(page).stem
    parts = stem.split("_", 1)
    if len(parts) == 2 and parts[0].isdigit():
        stem = parts[1]
    return f"/{stem}"


def redirect_button(label: str, page: str) -> None:
    st.link_button(label, page_slug(page), use_container_width=True)


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
    summary_rows = pd.DataFrame(
        [
            {"item": "Source document", "value": str(SOURCE_DOCX), "status": "found" if SOURCE_DOCX.exists() else "missing", "redirect page": "DOCX file"},
            {"item": "Updated document", "value": str(UPDATED_DOCX), "status": "found" if UPDATED_DOCX.exists() else "missing", "redirect page": "DOCX file"},
            {"item": "Embedded media", "value": media_count(UPDATED_DOCX), "status": "expected: 12", "redirect page": "Graph Attachments tab"},
            {"item": "Generated benchmark graph folder", "value": str(GRAPH_DIR), "status": "found" if GRAPH_DIR.exists() else "missing", "redirect page": "Graph Attachments tab"},
        ]
    )
    st.dataframe(summary_rows.astype(str), use_container_width=True, hide_index=True, height=180)

    st.subheader("Snapshot with Existing Data and Redirects")
    snapshot = docx_snapshot_rows(bundle)
    st.dataframe(snapshot, use_container_width=True, hide_index=True, height=300)
    redirect_cols = st.columns(4)
    redirects = [
        ("Chapter 4 results", "pages/6_1_Chapter_4_Implementation_Results.py"),
        ("Chapter 5 discussion", "pages/6_2_Chapter_5_Discussion.py"),
        ("Chapter 6 conclusion", "pages/6_3_Chapter_6_Conclusion.py"),
        ("PDF audit", "pages/2_4_PDF_Page_Processing_Audit.py"),
    ]
    for idx, (label, page) in enumerate(redirects):
        with redirect_cols[idx]:
            redirect_button(label, page)

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
    c1, c2, c3, c4 = st.columns(4)
    chapter_filter = c1.selectbox("Chapter", ["All"] + sorted(manifest["chapter"].unique().tolist()))
    rq_filter = c2.selectbox("RQ", ["All"] + sorted(manifest["rq"].unique().tolist()))
    view_mode = c3.selectbox("View", ["Graph + original table", "Graph only", "Original table only"])
    only_existing = c4.toggle("Only existing files", value=True)
    filtered = manifest.copy()
    if chapter_filter != "All":
        filtered = filtered[filtered["chapter"].eq(chapter_filter)]
    if rq_filter != "All":
        filtered = filtered[filtered["rq"].eq(rq_filter)]
    if only_existing:
        filtered = filtered[filtered["exists"]]
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=260)

    for _, row in filtered.iterrows():
        path = Path(row["path"])
        st.divider()
        st.subheader(f"{row['figure']} - {row['title']}")
        meta_cols = st.columns([2, 2, 2, 1])
        meta_cols[0].caption(f"{row['chapter']} | {row['rq']}")
        meta_cols[1].caption(f"Graph: `{path}`")
        meta_cols[2].caption(f"Original table: `{row['source table']}`")
        with meta_cols[3]:
            redirect_button("Open page", str(row["source page"]))

        graph_col, table_col = st.columns([1.05, 1], gap="large")
        if view_mode in {"Graph + original table", "Graph only"}:
            with graph_col:
                st.markdown("**Original graph attachment**")
                st.caption("This is the graph image embedded into the updated DOCX appendix.")
                if path.exists():
                    st.image(str(path), use_container_width=True)
                else:
                    st.warning("Missing graph file.")
        if view_mode in {"Graph + original table", "Original table only"}:
            with table_col:
                st.markdown("**Original / backing table**")
                source_df = source_dataframe_for_figure(row, bundle)
                if source_df.empty:
                    st.info("No backing table is available for this attachment yet.")
                else:
                    st.dataframe(source_df.astype(str), use_container_width=True, hide_index=True, height=360)
                    st.download_button(
                        f"Download {row['figure']} backing table",
                        source_df.to_csv(index=False).encode("utf-8"),
                        f"{row['figure'].replace('.', '_')}_{str(row['source table']).replace('/', '_')}.csv",
                        "text/csv",
                        use_container_width=True,
                        key=f"download_{row['figure']}",
                    )

with tab_chapters:
    st.header("Chapter 4-6 Mapping")
    mapping = chapter_mapping_rows()
    st.dataframe(mapping, use_container_width=True, hide_index=True, height=260)
    page_cols = st.columns(3)
    with page_cols[0]:
        redirect_button("Open Chapter 4 page", "pages/6_1_Chapter_4_Implementation_Results.py")
    with page_cols[1]:
        redirect_button("Open Chapter 5 page", "pages/6_2_Chapter_5_Discussion.py")
    with page_cols[2]:
        redirect_button("Open Chapter 6 page", "pages/6_3_Chapter_6_Conclusion.py")

    st.subheader("Benchmark checklist still needed")
    checklist = benchmark_checklist_rows()
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
