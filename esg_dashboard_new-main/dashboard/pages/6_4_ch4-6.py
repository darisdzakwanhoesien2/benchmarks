from __future__ import annotations

from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd
import plotly.express as px
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_4_SECTIONS,
    CHAPTER_5_SECTIONS,
    CHAPTER_6_SECTIONS,
    CHAPTER_FLOW_MERMAID,
    RQ_PAGE_MAP,
    RQ_TO_CHAPTER_MERMAID,
    mermaid_download_section,
    page_link_grid,
    render_mermaid,
)
from utils.data_loader import read_dataset, resolve_data_path

_BENCHMARKS_DIR = PAGE_DIR.parents[2]  # esg_dashboard_new-main/ -> benchmarks/
SOURCE_DOCX = _BENCHMARKS_DIR / "pages" / "thesis_ch4_6_structure_benchmarks.docx"
UPDATED_DOCX = _BENCHMARKS_DIR / "pages" / "thesis_ch4_6_structure_benchmarks_streamlit_graphs.docx"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

st.set_page_config(page_title="Ch4-6 Thesis Overview", layout="wide")
st.title("Ch4-6 Thesis Overview")
st.caption(
    "Chapter 4 → 5 → 6 evidence bridge: live charts from the parsed ESG dataset, "
    "chapter structure, RQ mapping, and benchmark checklist."
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = read_dataset("output_in_csv")
    df.columns = df.columns.str.lower().str.strip()
    return df


def _esg_pillar(raw: str) -> str:
    key = str(raw).strip().lower()[:1]
    return {"e": "Environmental", "s": "Social", "g": "Governance"}.get(key, "Other")


def _sentiment_norm(raw: str) -> str:
    key = str(raw).strip().lower()
    return {"positive": "Positive", "neutral": "Neutral", "negative": "Negative"}.get(key, "Other")


try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

if not df.empty:
    if "aspect_category" in df.columns:
        df["esg_pillar"] = df["aspect_category"].apply(_esg_pillar)
    if "sentiment" in df.columns:
        df["sentiment_norm"] = df["sentiment"].apply(_sentiment_norm)
    if "tone" in df.columns:
        df["tone"] = df["tone"].astype(str).str.strip().replace("", "Other")
    if "aspect" in df.columns:
        df["aspect"] = df["aspect"].astype(str).str.strip().replace("", "Unknown")


if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Parsed Records", f"{len(df):,}")
    m2.metric("Unique Tones", int(df["tone"].nunique()) if "tone" in df.columns else "n/a")
    m3.metric("ESG Pillars", int(df["esg_pillar"].nunique()) if "esg_pillar" in df.columns else "n/a")
    m4.metric("Unique Aspects", int(df["aspect"].nunique()) if "aspect" in df.columns else "n/a")

st.divider()


def bar_v(col: pd.Series, title: str) -> None:
    counts = col.value_counts().reset_index()
    counts.columns = [col.name, "count"]
    fig = px.bar(counts, x=col.name, y="count", title=title, color=col.name)
    fig.update_layout(showlegend=False, margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def bar_h(col: pd.Series, title: str, top_n: int = 15) -> None:
    counts = col.value_counts().head(top_n).reset_index()
    counts.columns = [col.name, "count"]
    fig = px.bar(counts, x="count", y=col.name, orientation="h", title=title, color=col.name)
    fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"), margin=dict(t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def pie_chart(col: pd.Series, title: str) -> None:
    counts = col.value_counts().reset_index()
    counts.columns = [col.name, "count"]
    fig = px.pie(counts, names=col.name, values="count", title=title, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)


def heatmap_pivot(source: pd.DataFrame, row_col: str, col_col: str, title: str) -> None:
    if row_col not in source.columns or col_col not in source.columns:
        st.info(f"Columns not found: {row_col}, {col_col}")
        return
    pivot = (
        source.groupby([row_col, col_col])
        .size()
        .reset_index(name="count")
        .pivot(index=row_col, columns=col_col, values="count")
        .fillna(0)
        .astype(int)
    )
    fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Teal", title=title)
    st.plotly_chart(fig, use_container_width=True)


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
            return len([n for n in zf.namelist() if n.startswith("word/media/")])
    except Exception:
        return 0


tab_live, tab_ch4, tab_ch5, tab_ch6, tab_rq, tab_docx = st.tabs([
    "Live Charts", "Chapter 4", "Chapter 5", "Chapter 6", "RQ Mapping", "DOCX Structure",
])

with tab_live:
    st.header("Live Evidence Charts")
    try:
        data_path = resolve_data_path("output_in_csv")
        st.caption(f"Source: `{data_path}`  ·  {len(df):,} records")
    except Exception:
        pass

    if df.empty:
        st.warning("Dataset is empty or could not be loaded.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            if "tone" in df.columns:
                bar_v(df["tone"], "Tone Distribution")
        with c2:
            if "esg_pillar" in df.columns:
                pie_chart(df["esg_pillar"], "ESG Pillar Distribution")

        c3, c4 = st.columns(2)
        with c3:
            if "sentiment_norm" in df.columns:
                bar_v(df["sentiment_norm"], "Sentiment Distribution")
        with c4:
            if "aspect" in df.columns:
                bar_h(df["aspect"], "Top 15 Aspects", top_n=15)

        if "esg_pillar" in df.columns and "tone" in df.columns:
            st.subheader("Tone × ESG Pillar")
            valid = df[df["esg_pillar"].ne("Other")]
            if not valid.empty:
                heatmap_pivot(valid, "esg_pillar", "tone", "Tone × ESG Pillar Heatmap")

        if "esg_pillar" in df.columns and "sentiment_norm" in df.columns:
            st.subheader("Sentiment × ESG Pillar")
            valid = df[df["esg_pillar"].ne("Other")]
            if not valid.empty:
                heatmap_pivot(valid, "esg_pillar", "sentiment_norm", "Sentiment × ESG Pillar Heatmap")

        st.divider()
        st.download_button(
            "Download ESG records CSV",
            df.to_csv(index=False).encode("utf-8"),
            "esg_records.csv",
            "text/csv",
            use_container_width=True,
        )

with tab_ch4:
    st.header("Chapter 4: Results")
    st.write(
        "What was implemented, measured, and stored — presented without over-interpretation."
    )
    render_mermaid(CHAPTER_FLOW_MERMAID, height=420)
    mermaid_download_section(CHAPTER_FLOW_MERMAID, "chapter_4_to_6_flow")

    st.subheader("Chapter 4 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_4_SECTIONS), use_container_width=True, hide_index=True)
    for section in CHAPTER_4_SECTIONS:
        with st.expander(section["section"]):
            st.markdown(f"**Supports:** {section['supports']}")
            st.write(section["results"])
            st.markdown(f"**Pages to use:** {', '.join(section['pages'])}")

with tab_ch5:
    st.header("Chapter 5: Discussion")
    st.write(
        "What the results mean — within the limits of available evidence."
    )
    render_mermaid(RQ_TO_CHAPTER_MERMAID, height=680)
    mermaid_download_section(RQ_TO_CHAPTER_MERMAID, "rq_to_discussion_flow")

    st.subheader("Chapter 5 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_5_SECTIONS), use_container_width=True, hide_index=True)
    for section in CHAPTER_5_SECTIONS:
        with st.expander(section["section"]):
            st.markdown(f"**Supports:** {section['supports']}")
            st.write(section["discussion"])

with tab_ch6:
    st.header("Chapter 6: Conclusion")
    st.write(
        "Concise answers, contributions, limitations, and future work. No new analysis."
    )

    st.subheader("Chapter 6 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_6_SECTIONS), use_container_width=True, hide_index=True)
    for section in CHAPTER_6_SECTIONS:
        with st.expander(section["section"]):
            st.write(section["conclusion"])

    st.subheader("Benchmark Checklist Still Needed")
    checklist = pd.DataFrame([
        {
            "benchmark": "OCR quality",
            "why needed": "CER/WER not yet measured.",
            "target artifact": "ocr_quality_by_page.csv",
            "redirect page": "/Parsed_ESG_Review",
        },
        {
            "benchmark": "Human annotation agreement",
            "why needed": "Single-annotator labels need reliability evidence.",
            "target artifact": "human_agreement_summary.csv",
            "redirect page": "/Metric_Analysis",
        },
        {
            "benchmark": "Repeated LLM runs",
            "why needed": "Model/prompt stability needs confidence intervals.",
            "target artifact": "model_prompt_repeated_run_ci.csv",
            "redirect page": "/Benchmark_Model",
        },
        {
            "benchmark": "ClimateBERT baseline",
            "why needed": "Compare tone-vs-ClimateBERT to majority and human-labelled baselines.",
            "target artifact": "climatebert_baseline_comparison.csv",
            "redirect page": "/ClimateBERT_Result_Visualizer",
        },
        {
            "benchmark": "Ontology extension",
            "why needed": "Formalise unmapped ESG aspects.",
            "target artifact": "indonesian_esg_ontology_extension.csv",
            "redirect page": "/Aspect",
        },
    ])
    st.dataframe(checklist, use_container_width=True, hide_index=True)

with tab_rq:
    st.header("RQ → Chapter 4-6 Mapping")

    mapping_rows = [
        {
            "rq": rq["rq"],
            "theme": rq["theme"],
            "chapter 4 result": rq["chapter_4_use"],
            "chapter 5 discussion": rq["chapter_5_use"],
            "chapter 6 conclusion": rq["chapter_6_use"],
        }
        for rq in RQ_PAGE_MAP
    ]
    st.dataframe(pd.DataFrame(mapping_rows), use_container_width=True, hide_index=True, height=280)

    selected_rq = st.selectbox("Open RQ detail", [rq["rq"] for rq in RQ_PAGE_MAP])
    rq = next(r for r in RQ_PAGE_MAP if r["rq"] == selected_rq)

    st.markdown(f"### {rq['rq']} · {rq['theme']}")
    st.write(rq["question"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Chapter 4 result**")
        st.info(rq["chapter_4_use"])
    with c2:
        st.markdown("**Chapter 5 discussion**")
        st.info(rq["chapter_5_use"])
    with c3:
        st.markdown("**Chapter 6 conclusion**")
        st.info(rq["chapter_6_use"])

    st.warning(f"**Still needed:** {rq['needed_completion']}")
    st.subheader("Primary pages")
    page_link_grid(rq["primary_pages"], columns=3)

with tab_docx:
    st.header("DOCX Structure Reader")

    doc_cols = st.columns([2, 2, 1, 1])
    doc_cols[0].markdown(f"**Source DOCX:** `{SOURCE_DOCX.name}`")
    doc_cols[1].markdown(f"**Updated DOCX:** `{UPDATED_DOCX.name}`")
    doc_cols[2].metric("Source found", "yes" if SOURCE_DOCX.exists() else "no")
    doc_cols[3].metric("Embedded graphs", media_count(UPDATED_DOCX))

    selected_doc = st.radio(
        "Document to inspect",
        ["Updated graph-attached DOCX", "Original source DOCX"],
        horizontal=True,
    )
    doc_path = UPDATED_DOCX if selected_doc.startswith("Updated") else SOURCE_DOCX
    doc_df = read_docx_paragraphs(doc_path)

    search = st.text_input("Search DOCX text", placeholder="e.g. RQ3, benchmark, Appendix")
    display = doc_df.copy()
    if search.strip():
        display = display[
            display.astype(str)
            .apply(lambda col: col.str.contains(search.strip(), case=False, regex=False))
            .any(axis=1)
        ]
    st.dataframe(display, use_container_width=True, hide_index=True, height=480)

    if UPDATED_DOCX.exists():
        st.download_button(
            "Download updated DOCX",
            UPDATED_DOCX.read_bytes(),
            UPDATED_DOCX.name,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
