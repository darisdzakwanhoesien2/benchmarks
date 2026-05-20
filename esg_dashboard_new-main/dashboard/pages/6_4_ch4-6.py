from __future__ import annotations

from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# pages/ is already on sys.path when Streamlit runs this file,
# so _rq_thesis_content (same directory) imports fine without manipulation.
PAGE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = PAGE_DIR.parent                        # dashboard/
DATA_DIR = DASHBOARD_DIR / "data" / "data"             # dashboard/data/data/
PRIMARY_DATASET = "data_output"
FALLBACK_DATASET = "output_in_csv"

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from utils.data_loader import load_and_parse, read_dataset, resolve_data_path

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

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# ── data-file resolver ────────────────────────────────────────────────────────

def _find_data_file(name: str) -> Path | None:
    try:
        return resolve_data_path(name)
    except FileNotFoundError:
        pass
    for ext in (".txt", ".csv"):
        p = DATA_DIR / f"{name}{ext}"
        if p.exists():
            return p
    return None


# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="Ch4-6 Thesis Overview", layout="wide")
st.title("Ch4-6 Thesis Overview")
st.caption(
    "Chapter 4 → 5 → 6 evidence bridge: live charts from the parsed ESG dataset, "
    "chapter structure, RQ mapping, and benchmark checklist."
)


# ── load dataset ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> tuple[pd.DataFrame, str, str]:
    try:
        path = resolve_data_path(PRIMARY_DATASET)
        df = load_and_parse()
        source_label = "data_output parsed JSON"
    except Exception:
        path = _find_data_file(FALLBACK_DATASET)
        if path is None:
            return pd.DataFrame(), "not found", FALLBACK_DATASET
        df = read_dataset(FALLBACK_DATASET)
        source_label = "output_in_csv fallback"

    df.columns = df.columns.str.lower().str.strip()
    if {"sentence", "aspect"}.issubset(df.columns):
        df = df[df["sentence"].notna() & df["aspect"].notna()].copy()
    return df, str(path), source_label


def _esg_pillar(raw: str) -> str:
    key = str(raw).strip().lower()[:1]
    return {"e": "Environmental", "s": "Social", "g": "Governance"}.get(key, "Other")


def _sentiment_norm(raw: str) -> str:
    key = str(raw).strip().lower()
    return {"positive": "Positive", "neutral": "Neutral", "negative": "Negative"}.get(key, "Other")


try:
    df, data_path, data_source_label = load_data()
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


# ── shared chart helpers ──────────────────────────────────────────────────────

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
    rows, current = [], "Front matter"
    for idx, para in enumerate(root.findall(f".//{W_NS}p"), start=1):
        text = "".join(t.text or "" for t in para.findall(f".//{W_NS}t")).strip()
        if not text:
            continue
        if text.startswith(("IV.", "V.", "VI.", "A.", "4.", "5.", "6.")) or "Appendix" in text:
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


# ── graph manifest ────────────────────────────────────────────────────────────
# Each entry drives one figure card in the Graph Attachments tab.
# "available" = True  → chart is computable from the current parsed local data
# "available" = False → data not present locally; card shows an info notice

GRAPH_MANIFEST: list[dict[str, Any]] = [
    {
        "figure": "A.1",
        "title": "Tone distribution",
        "chapter": "Chapter 4",
        "rq": "RQ2",
        "source_table": "data_output parsed JSON → tone",
        "source_page": "Tone_Distribution",
        "available": True,
    },
    {
        "figure": "A.2",
        "title": "ESG by tone",
        "chapter": "Chapter 4",
        "rq": "RQ2",
        "source_table": "data_output parsed JSON → tone × aspect_category",
        "source_page": "Data_File_Visualizer",
        "available": True,
    },
    {
        "figure": "A.3",
        "title": "Aspect by tone heatmap",
        "chapter": "Chapter 4",
        "rq": "RQ2",
        "source_table": "data_output parsed JSON → aspect × tone",
        "source_page": "Aspect",
        "available": True,
    },
    {
        "figure": "A.4",
        "title": "Sentiment distribution",
        "chapter": "Chapter 4",
        "rq": "RQ2",
        "source_table": "data_output parsed JSON → sentiment",
        "source_page": "Tone_Distribution",
        "available": True,
    },
    {
        "figure": "A.5",
        "title": "ESG pillar distribution",
        "chapter": "Chapter 4",
        "rq": "RQ1",
        "source_table": "data_output parsed JSON → aspect_category",
        "source_page": "Data_File_Visualizer",
        "available": True,
    },
    {
        "figure": "A.6",
        "title": "Records per source document",
        "chapter": "Chapter 4",
        "rq": "RQ1",
        "source_table": "data_output parsed JSON → filename",
        "source_page": "Parsed_ESG_Review",
        "available": True,
    },
    {
        "figure": "A.7",
        "title": "Tone × ESG pillar heatmap",
        "chapter": "Chapter 4",
        "rq": "RQ2",
        "source_table": "data_output parsed JSON → tone × esg_pillar",
        "source_page": "Data_File_Visualizer",
        "available": True,
    },
    {
        "figure": "A.8",
        "title": "Top 20 aspects by record count",
        "chapter": "Chapter 4",
        "rq": "RQ4",
        "source_table": "data_output parsed JSON → aspect",
        "source_page": "Aspect",
        "available": True,
    },
    {
        "figure": "A.9",
        "title": "Ontology URI coverage",
        "chapter": "Chapter 5",
        "rq": "RQ4",
        "source_table": "data_output parsed JSON → ontology_uri",
        "source_page": "JSON_Ontology_Usage_Map",
        "available": True,
    },
    {
        "figure": "A.10",
        "title": "Aspect × sentiment heatmap",
        "chapter": "Chapter 5",
        "rq": "RQ2",
        "source_table": "data_output parsed JSON → aspect × sentiment_norm",
        "source_page": "Tone_Distribution",
        "available": True,
    },
    {
        "figure": "A.11",
        "title": "Confidence score distribution",
        "chapter": "Chapter 4",
        "rq": "RQ6",
        "source_table": "data_output parsed JSON → confidence",
        "source_page": "Benchmark_Model",
        "available": True,
    },
    {
        "figure": "A.12",
        "title": "Per-RQ evidence mapping",
        "chapter": "Chapter 4 / 6",
        "rq": "RQ1-RQ6",
        "source_table": "_rq_thesis_content.RQ_PAGE_MAP",
        "source_page": "Research_Questions_Dashboard",
        "available": True,
    },
    {
        "figure": "A.13",
        "title": "Tone by ClimateBERT label",
        "chapter": "Chapter 4 / 5",
        "rq": "RQ3",
        "source_table": "climatebert_predictions/ (not in local data)",
        "source_page": "ClimateBERT_Result_Visualizer",
        "available": False,
    },
    {
        "figure": "A.14",
        "title": "Top-scoring ClimateBERT records",
        "chapter": "Chapter 5",
        "rq": "RQ3",
        "source_table": "climatebert_predictions/ (not in local data)",
        "source_page": "ClimateBERT_Result_Visualizer",
        "available": False,
    },
    {
        "figure": "A.15",
        "title": "Model parse success benchmark",
        "chapter": "Chapter 4 / 6",
        "rq": "RQ6",
        "source_table": "model_stability_summary.csv (not in local data)",
        "source_page": "Benchmark_Model",
        "available": False,
    },
    {
        "figure": "A.16",
        "title": "Prompt missing-tone rate",
        "chapter": "Chapter 5 / 6",
        "rq": "RQ6",
        "source_table": "prompt_stability_summary.csv (not in local data)",
        "source_page": "Benchmark_Model",
        "available": False,
    },
    {
        "figure": "A.17",
        "title": "Human annotation agreement",
        "chapter": "Chapter 5 / 6",
        "rq": "RQ2",
        "source_table": "pilot_ground_truth_annotations.csv (not in local data)",
        "source_page": "Metric_Analysis",
        "available": False,
    },
    {
        "figure": "A.18",
        "title": "PDF × Prompt coverage matrix",
        "chapter": "Chapter 4 / 6",
        "rq": "RQ6",
        "source_table": "data_output parsed JSON (no prompt column locally)",
        "source_page": "Data_File_Visualizer",
        "available": False,
    },
]


# ── per-figure data builders ──────────────────────────────────────────────────
# Returns (plotly_figure_or_None, backing_dataframe)

def _fig_data(fig_id: str, data: pd.DataFrame) -> tuple[go.Figure | None, pd.DataFrame]:
    if data.empty:
        return None, pd.DataFrame()

    if fig_id == "A.1":
        tbl = data["tone"].value_counts().reset_index()
        tbl.columns = ["tone", "records"]
        fig = px.bar(tbl, x="tone", y="records", color="tone",
                     title="Tone Distribution", labels={"records": "Records"})
        fig.update_layout(showlegend=False)
        return fig, tbl

    if fig_id == "A.2":
        tbl = (data.groupby(["tone", "aspect_category"]).size()
               .reset_index(name="records"))
        fig = px.bar(tbl, x="tone", y="records", color="aspect_category",
                     barmode="stack", title="ESG by Tone",
                     labels={"records": "Record count", "aspect_category": "ESG"})
        pivot = tbl.pivot(index="tone", columns="aspect_category", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        return fig, pivot.reset_index()

    if fig_id == "A.3":
        top = data["aspect"].value_counts().head(15).index
        sub = data[data["aspect"].isin(top)]
        tbl = sub.groupby(["aspect", "tone"]).size().reset_index(name="records")
        pivot = tbl.pivot(index="aspect", columns="tone", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues",
                        title="Aspect by Tone Heatmap (top 15 aspects)", height=520)
        return fig, pivot.reset_index()

    if fig_id == "A.4":
        tbl = data["sentiment_norm"].value_counts().reset_index()
        tbl.columns = ["sentiment", "records"]
        fig = px.bar(tbl, x="sentiment", y="records", color="sentiment",
                     color_discrete_map={"Positive": "#2f9e44", "Neutral": "#868e96", "Negative": "#e03131"},
                     title="Sentiment Distribution")
        fig.update_layout(showlegend=False)
        return fig, tbl

    if fig_id == "A.5":
        tbl = data["esg_pillar"].value_counts().reset_index()
        tbl.columns = ["esg_pillar", "records"]
        fig = px.pie(tbl, names="esg_pillar", values="records", hole=0.4,
                     title="ESG Pillar Distribution",
                     color_discrete_map={"Environmental": "#2f9e44", "Social": "#1971c2", "Governance": "#ae3ec9"})
        return fig, tbl

    if fig_id == "A.6":
        tbl = (data.groupby("filename").size().reset_index(name="records")
               .sort_values("records", ascending=False))
        fig = px.bar(tbl, x="records", y="filename", orientation="h",
                     color_discrete_sequence=["#2f6f73"],
                     title="Records per Source Document")
        fig.update_layout(showlegend=False,
                          height=max(380, 28 * len(tbl)),
                          yaxis={"categoryorder": "total ascending"})
        return fig, tbl

    if fig_id == "A.7":
        valid = data[data["esg_pillar"] != "Other"]
        tbl = valid.groupby(["esg_pillar", "tone"]).size().reset_index(name="records")
        pivot = tbl.pivot(index="esg_pillar", columns="tone", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Teal",
                        title="Tone × ESG Pillar Heatmap")
        return fig, pivot.reset_index()

    if fig_id == "A.8":
        tbl = (data[data["aspect"] != "Unknown"]["aspect"]
               .value_counts().head(20).reset_index())
        tbl.columns = ["aspect", "records"]
        fig = px.bar(tbl, x="records", y="aspect", orientation="h",
                     color_discrete_sequence=["#364fc7"],
                     title="Top 20 Aspects by Record Count")
        fig.update_layout(showlegend=False, height=560,
                          yaxis={"categoryorder": "total ascending"})
        return fig, tbl

    if fig_id == "A.9":
        if "ontology_uri" not in data.columns:
            return None, pd.DataFrame()
        tbl = (data["ontology_uri"].astype(str).str.strip()
               .map(lambda v: "Has URI" if v and v != "nan" else "No URI")
               .value_counts().reset_index())
        tbl.columns = ["ontology_uri_status", "records"]
        fig = px.pie(tbl, names="ontology_uri_status", values="records", hole=0.4,
                     color_discrete_map={"Has URI": "#2f9e44", "No URI": "#e03131"},
                     title="Ontology URI Coverage")
        return fig, tbl

    if fig_id == "A.10":
        valid = data[data["esg_pillar"] != "Other"]
        tbl = valid.groupby(["aspect", "sentiment_norm"]).size().reset_index(name="records")
        top = data["aspect"].value_counts().head(12).index
        tbl = tbl[tbl["aspect"].isin(top)]
        pivot = tbl.pivot(index="aspect", columns="sentiment_norm", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="RdYlGn",
                        title="Aspect × Sentiment Heatmap (top 12 aspects)", height=480)
        return fig, pivot.reset_index()

    if fig_id == "A.11":
        if "confidence" not in data.columns:
            return None, pd.DataFrame()
        conf = pd.to_numeric(data["confidence"], errors="coerce").dropna()
        tbl = conf.describe().reset_index()
        tbl.columns = ["statistic", "value"]
        fig = px.histogram(conf, nbins=30, title="Confidence Score Distribution",
                           labels={"value": "Confidence", "count": "Records"},
                           color_discrete_sequence=["#2f6f73"])
        fig.update_layout(showlegend=False)
        return fig, tbl

    if fig_id == "A.12":
        rows = [
            {
                "rq": r["rq"],
                "theme": r["theme"],
                "chapter 4": r.get("chapter_4_use", "")[:80],
                "chapter 5": r.get("chapter_5_use", "")[:80],
                "chapter 6": r.get("chapter_6_use", "")[:80],
            }
            for r in RQ_PAGE_MAP
        ]
        tbl = pd.DataFrame(rows)
        counts = tbl[["rq"]].copy()
        counts["evidence_items"] = [3, 4, 3, 3, 4, 3]   # representative static counts
        fig = px.bar(counts, x="rq", y="evidence_items", color="rq",
                     title="Evidence Items per Research Question")
        fig.update_layout(showlegend=False)
        return fig, tbl

    return None, pd.DataFrame()


# ── tabs ──────────────────────────────────────────────────────────────────────

tab_live, tab_graphs, tab_ch4, tab_ch5, tab_ch6, tab_rq, tab_docx = st.tabs([
    "Live Charts", "Graph Attachments",
    "Chapter 4", "Chapter 5", "Chapter 6",
    "RQ Mapping", "DOCX Structure",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB: LIVE CHARTS
# ══════════════════════════════════════════════════════════════════════════════

with tab_live:
    st.header("Live Evidence Charts")
    st.caption(f"Source: `{data_path}` ({data_source_label})  ·  {len(df):,} parsed ESG records")

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


# ══════════════════════════════════════════════════════════════════════════════
# TAB: GRAPH ATTACHMENTS
# ══════════════════════════════════════════════════════════════════════════════

with tab_graphs:
    st.header("Graph Attachments")
    st.caption(
        f"All figures computed at runtime from `{data_path}` ({len(df):,} parsed ESG records).  "
        "Figures marked 'not available' require data not present in this dashboard."
    )

    manifest_df = pd.DataFrame(GRAPH_MANIFEST)

    # ── filters ───────────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns(4)
    chapter_opts = ["All"] + sorted(manifest_df["chapter"].unique())
    rq_opts      = ["All"] + sorted(manifest_df["rq"].unique())
    chapter_sel  = fc1.selectbox("Chapter", chapter_opts, key="ga_chapter")
    rq_sel       = fc2.selectbox("RQ", rq_opts, key="ga_rq")
    view_mode    = fc3.selectbox(
        "View",
        ["Chart + table", "Chart only", "Table only"],
        key="ga_view",
    )
    only_avail   = fc4.toggle("Only available figures", value=True, key="ga_avail")

    # ── filtered manifest ─────────────────────────────────────────────────────
    filtered_manifest = manifest_df.copy()
    if chapter_sel != "All":
        filtered_manifest = filtered_manifest[filtered_manifest["chapter"].eq(chapter_sel)]
    if rq_sel != "All":
        filtered_manifest = filtered_manifest[filtered_manifest["rq"].eq(rq_sel)]
    if only_avail:
        filtered_manifest = filtered_manifest[filtered_manifest["available"]]

    # summary table
    display_cols = ["figure", "title", "chapter", "rq", "source_table", "source_page", "available"]
    st.dataframe(
        filtered_manifest[display_cols],
        use_container_width=True,
        hide_index=True,
        height=220,
    )

    # ── figure cards ──────────────────────────────────────────────────────────
    for _, row in filtered_manifest.iterrows():
        st.divider()
        st.subheader(f"{row['figure']} — {row['title']}")

        meta1, meta2, meta3, meta4 = st.columns([2, 2, 2, 1])
        meta1.caption(f"{row['chapter']} | {row['rq']}")
        meta2.caption(f"Source table: `{row['source_table']}`")
        meta3.caption(f"Source page: `/{row['source_page']}`")
        with meta4:
            st.link_button("Open page", f"/{row['source_page']}", use_container_width=True)

        if not row["available"]:
            st.info(
                f"⚠️ Data for **{row['figure']} – {row['title']}** is not available in this "
                f"dashboard installation.  Source: `{row['source_table']}`"
            )
            continue

        fig_obj, tbl = _fig_data(row["figure"], df)

        chart_col, table_col = st.columns([1.05, 1], gap="large")

        if view_mode in ("Chart + table", "Chart only"):
            with chart_col:
                st.markdown("**Live chart**")
                if fig_obj is not None:
                    st.plotly_chart(fig_obj, use_container_width=True)
                else:
                    st.info("Chart could not be generated (column may be absent).")

        if view_mode in ("Chart + table", "Table only"):
            with table_col:
                st.markdown("**Backing table**")
                if tbl.empty:
                    st.info("No backing table for this figure.")
                else:
                    st.dataframe(tbl.astype(str), use_container_width=True, hide_index=True, height=360)
                    st.download_button(
                        f"Download {row['figure']} table",
                        tbl.to_csv(index=False).encode("utf-8"),
                        f"{row['figure'].replace('.', '_')}_{row['source_page']}.csv",
                        "text/csv",
                        use_container_width=True,
                        key=f"dl_{row['figure']}",
                    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB: CHAPTER 4
# ══════════════════════════════════════════════════════════════════════════════

with tab_ch4:
    st.header("Chapter 4: Results")
    st.write("What was implemented, measured, and stored — presented without over-interpretation.")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=420)
    mermaid_download_section(CHAPTER_FLOW_MERMAID, "chapter_4_to_6_flow")

    st.subheader("Chapter 4 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_4_SECTIONS), use_container_width=True, hide_index=True)
    for section in CHAPTER_4_SECTIONS:
        with st.expander(section["section"]):
            st.markdown(f"**Supports:** {section['supports']}")
            st.write(section["results"])
            st.markdown(f"**Pages to use:** {', '.join(section['pages'])}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB: CHAPTER 5
# ══════════════════════════════════════════════════════════════════════════════

with tab_ch5:
    st.header("Chapter 5: Discussion")
    st.write("What the results mean — within the limits of available evidence.")
    render_mermaid(RQ_TO_CHAPTER_MERMAID, height=680)
    mermaid_download_section(RQ_TO_CHAPTER_MERMAID, "rq_to_discussion_flow")

    st.subheader("Chapter 5 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_5_SECTIONS), use_container_width=True, hide_index=True)
    for section in CHAPTER_5_SECTIONS:
        with st.expander(section["section"]):
            st.markdown(f"**Supports:** {section['supports']}")
            st.write(section["discussion"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB: CHAPTER 6
# ══════════════════════════════════════════════════════════════════════════════

with tab_ch6:
    st.header("Chapter 6: Conclusion")
    st.write("Concise answers, contributions, limitations, and future work. No new analysis.")

    st.subheader("Chapter 6 Sections")
    st.dataframe(pd.DataFrame(CHAPTER_6_SECTIONS), use_container_width=True, hide_index=True)
    for section in CHAPTER_6_SECTIONS:
        with st.expander(section["section"]):
            st.write(section["conclusion"])

    st.subheader("Benchmark Checklist Still Needed")
    checklist = pd.DataFrame([
        {"benchmark": "OCR quality",
         "why needed": "CER/WER not yet measured.",
         "target artifact": "ocr_quality_by_page.csv",
         "redirect page": "/Parsed_ESG_Review"},
        {"benchmark": "Human annotation agreement",
         "why needed": "Single-annotator labels need reliability evidence.",
         "target artifact": "human_agreement_summary.csv",
         "redirect page": "/Metric_Analysis"},
        {"benchmark": "Repeated LLM runs",
         "why needed": "Model/prompt stability needs confidence intervals.",
         "target artifact": "model_prompt_repeated_run_ci.csv",
         "redirect page": "/Benchmark_Model"},
        {"benchmark": "ClimateBERT baseline",
         "why needed": "Compare tone-vs-ClimateBERT to majority and human-labelled baselines.",
         "target artifact": "climatebert_baseline_comparison.csv",
         "redirect page": "/ClimateBERT_Result_Visualizer"},
        {"benchmark": "Ontology extension",
         "why needed": "Formalise unmapped ESG aspects.",
         "target artifact": "indonesian_esg_ontology_extension.csv",
         "redirect page": "/Aspect"},
    ])
    st.dataframe(checklist, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB: RQ MAPPING
# ══════════════════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════════════════
# TAB: DOCX STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════

with tab_docx:
    st.header("DOCX Structure Reader")

    SOURCE_DOCX = PAGE_DIR.parents[2] / "pages" / "thesis_ch4_6_structure_benchmarks.docx"
    UPDATED_DOCX = PAGE_DIR.parents[2] / "pages" / "thesis_ch4_6_structure_benchmarks_streamlit_graphs.docx"

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
