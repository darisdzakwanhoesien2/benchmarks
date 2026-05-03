# ==========================================================
# 📊 Tone Distribution Explorer (Ontology-Aware, Path-Fixed)
# ==========================================================

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(page_title="Tone Distribution Explorer", layout="wide")

st.title("📊 Tone Distribution Explorer")
add_page_explanation(__file__)
st.write(
    "Ontology-normalized tone distribution computed directly from "
    "`output_in_csv.csv`."
)

# ----------------------------------------------------------
# PATH RESOLUTION (FIXED)
# ----------------------------------------------------------


# --- Dataset selection from config/dataset.json ---
dataset_config_path = Path(__file__).resolve().parents[1] / "config" / "dataset.json"
datasets = []
if dataset_config_path.exists():
    with open(dataset_config_path) as f:
        config = json.load(f)
        datasets = config.get("datasets", [])

dataset_names = [d["name"] for d in datasets]
dataset_choice = None
selected_file = None

if dataset_names:
    dataset_choice = st.sidebar.selectbox("Select a dataset", ["(Upload your own)"] + dataset_names)
    if dataset_choice != "(Upload your own)":
        selected = next((d for d in datasets if d["name"] == dataset_choice), None)
        if selected:
            selected_file = selected["filepath"]

uploaded_file = st.sidebar.file_uploader("Or upload your CSV file", type=["csv"])

# -------------------------
# RESOLVE MASTER_PATH (with fallbacks)
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

if uploaded_file is not None:
    # UploadedFile (file-like) is accepted by pd.read_csv
    MASTER_PATH = uploaded_file
elif selected_file:
    p = Path(selected_file)
    if not p.exists():
        # Try resolving relative to project root if the path in config is relative
        p = (PROJECT_ROOT / selected_file).resolve()
    MASTER_PATH = p
else:
    # Candidate locations (project-level data, benchmarks/data, repo root data, cwd)
    candidates = [
        DATA_DIR / "output_in_csv.csv",
        Path(__file__).resolve().parents[1] / "data" / "output_in_csv.csv",  # benchmarks/data
        Path(__file__).resolve().parents[3] / "data" / "output_in_csv.csv",  # alternative layout
        Path.cwd() / "data" / "output_in_csv.csv",
    ]
    # pick first existing candidate, otherwise use the primary project DATA_DIR path
    MASTER_PATH = next((c for c in candidates if c.exists()), candidates[0])

# ----------------------------------------------------------
# LOAD ONTOLOGIES (robust: try multiple locations, fallback)
# ----------------------------------------------------------
def load_json_from_candidates(filename, project_root):
    candidates = [
        project_root / "data" / filename,                                # project data
        Path(__file__).resolve().parents[1] / "data" / filename,        # benchmarks/data
        project_root.parents[0] / "data" / filename,                    # repo parent data (if layout differs)
        Path.cwd() / "data" / filename,                                 # current working dir /data
        Path(filename).resolve()                                        # absolute / provided path
    ]
    tried = []
    for p in candidates:
        tried.append(str(p))
        try:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f), tried
        except Exception:
            # ignore read errors and continue trying other locations
            continue
    return None, tried

# try to load each ontology, collecting attempted paths for helpful error messages
ASPECT_ONTOLOGY, tried_aspect = load_json_from_candidates("aspect_category_ontology.json", PROJECT_ROOT)
SENTIMENT_ONTOLOGY, tried_sent = load_json_from_candidates("sentiment_ontology.json", PROJECT_ROOT)
TONE_ONTOLOGY, tried_tone = load_json_from_candidates("tone_ontology.json", PROJECT_ROOT)

missing_files = []
if ASPECT_ONTOLOGY is None:
    missing_files.append(("aspect_category_ontology.json", tried_aspect))
if SENTIMENT_ONTOLOGY is None:
    missing_files.append(("sentiment_ontology.json", tried_sent))
if TONE_ONTOLOGY is None:
    missing_files.append(("tone_ontology.json", tried_tone))

if missing_files:
    # show which files / paths were attempted
    msg_lines = []
    for fname, tried in missing_files:
        msg_lines.append(f"- {fname} (checked {len(tried)} locations, examples:\n    {tried[:3]})")
    st.warning(
        "Some ontology files were not found. Checked several locations.\n\n"
        + "\n".join(msg_lines)
        + "\n\nPlace the JSON files under the project data directory "
        f"({PROJECT_ROOT / 'data'}) or the benchmarks/data folder."
    )
    # fallback: minimal ontologies so UI can still run
    if ASPECT_ONTOLOGY is None:
        ASPECT_ONTOLOGY = {
            "OTHER": {"aliases": ["other", None]},
            "SERVICE": {"aliases": ["service", "customer service"]},
            "PRODUCT": {"aliases": ["product", "item"]}
        }
    if SENTIMENT_ONTOLOGY is None:
        SENTIMENT_ONTOLOGY = {
            "OTHER": {"aliases": ["other", None]},
            "POSITIVE": {"aliases": ["positive", "pos", "good"]},
            "NEGATIVE": {"aliases": ["negative", "neg", "bad"]}
        }
    if TONE_ONTOLOGY is None:
        TONE_ONTOLOGY = {
            "OTHER": {"aliases": ["other", None]},
            "FORMAL": {"aliases": ["formal"]},
            "INFORMAL": {"aliases": ["informal"]},
            "NEUTRAL": {"aliases": ["neutral"]}
        }


def build_alias_map(ontology):
    mapping = {}
    for canonical, meta in ontology.items():
        for alias in meta.get("aliases", []):
            if alias is not None:
                mapping[str(alias).strip().lower()] = canonical
    return mapping


ASPECT_MAP = build_alias_map(ASPECT_ONTOLOGY)
SENTIMENT_MAP = build_alias_map(SENTIMENT_ONTOLOGY)
TONE_MAP = build_alias_map(TONE_ONTOLOGY)


def normalize(value, mapping):
    if pd.isna(value):
        return "OTHER"
    return mapping.get(str(value).strip().lower(), "OTHER")


# ----------------------------------------------------------
# LOAD MASTER DATASET
# ----------------------------------------------------------
@st.cache_data
def load_master():
    df = pd.read_csv(MASTER_PATH)
    df.columns = df.columns.str.lower().str.strip()
    return df


try:
    raw = load_master()
except Exception as e:
    st.error(f"❌ Failed to load dataset {MASTER_PATH}:\n{e}")
    st.stop()

st.success(f"✅ Loaded {len(raw)} rows from output_in_csv.csv")

# ----------------------------------------------------------
# VALIDATE REQUIRED COLUMNS
# ----------------------------------------------------------
required_cols = {"aspect_category", "sentiment", "tone"}
missing = required_cols - set(raw.columns)
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# ----------------------------------------------------------
# NORMALIZE USING ONTOLOGIES
# ----------------------------------------------------------
raw["aspect_norm"] = raw["aspect_category"].apply(lambda x: normalize(x, ASPECT_MAP))
raw["sentiment_norm"] = raw["sentiment"].apply(lambda x: normalize(x, SENTIMENT_MAP))
raw["tone_norm"] = raw["tone"].apply(lambda x: normalize(x, TONE_MAP))

# ----------------------------------------------------------
# COMPUTE TONE DISTRIBUTION (CORRECT MINIMUM LOGIC)
# ----------------------------------------------------------
@st.cache_data
def compute_tone_distribution(df):
    rows = []

    for (aspect, sentiment), g in df.groupby(["aspect_norm", "sentiment_norm"]):
        counts = g["tone_norm"].value_counts()

        if counts.empty:
            continue

        rows.append({
            "aspect_category": aspect,
            "sentiment": sentiment,
            "minimum_tone": counts.idxmin(),
            "minimum_amount": int(counts.min()),
            "group_size": len(g)
        })

    return (
        pd.DataFrame(rows)
        .sort_values(["aspect_category", "sentiment"])
        .reset_index(drop=True)
    )


tone_df = compute_tone_distribution(raw)

st.subheader("Auto-Generated Tone Distribution")
add_section_explanation("Auto-Generated Tone Distribution")
st.dataframe(tone_df, use_container_width=True)

# ----------------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------------
st.sidebar.header("Filters")

f_aspects = st.sidebar.multiselect(
    "Aspect Category",
    sorted(tone_df["aspect_category"].unique()),
    default=sorted(tone_df["aspect_category"].unique())
)

f_sentiments = st.sidebar.multiselect(
    "Sentiment",
    sorted(tone_df["sentiment"].unique()),
    default=sorted(tone_df["sentiment"].unique())
)

f_tones = st.sidebar.multiselect(
    "Minimum Tone",
    sorted(tone_df["minimum_tone"].unique()),
    default=sorted(tone_df["minimum_tone"].unique())
)

filtered = tone_df[
    tone_df["aspect_category"].isin(f_aspects) &
    tone_df["sentiment"].isin(f_sentiments) &
    tone_df["minimum_tone"].isin(f_tones)
]

st.write(f"### Filtered Rows: {len(filtered)}")
st.dataframe(filtered, use_container_width=True)

# ----------------------------------------------------------
# PIE — COMBINED MINIMUM TONE
# ----------------------------------------------------------
st.markdown("## 🥧 Combined Minimum Tone Distribution")
add_section_explanation("## 🥧 Combined Minimum Tone Distribution")

if not filtered.empty:
    pie_df = (
        filtered.groupby("minimum_tone")["minimum_amount"]
        .sum()
        .reset_index()
    )

    fig_pie = px.pie(
        pie_df,
        names="minimum_tone",
        values="minimum_amount",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------------------------------------------
# BAR — MINIMUM AMOUNT
# ----------------------------------------------------------
st.markdown("## 📦 Minimum Amount per Tone")
add_section_explanation("## 📦 Minimum Amount per Tone")

fig_bar = px.bar(
    filtered,
    x="minimum_tone",
    y="minimum_amount",
    color="minimum_tone"
)
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------------------------------------
# SANKEY — NAMESPACED (NO COLLISIONS)
# ----------------------------------------------------------
st.markdown("## 🔗 Sankey: Aspect → Sentiment → Minimum Tone")
add_section_explanation("## 🔗 Sankey: Aspect → Sentiment → Minimum Tone")

if not filtered.empty:
    sankey_df = (
        filtered.groupby(["aspect_category", "sentiment", "minimum_tone"])["minimum_amount"]
        .sum()
        .reset_index()
    )

    sankey_df["A"] = sankey_df["aspect_category"].apply(lambda x: f"A:{x}")
    sankey_df["S"] = sankey_df["sentiment"].apply(lambda x: f"S:{x}")
    sankey_df["T"] = sankey_df["minimum_tone"].apply(lambda x: f"T:{x}")

    nodes = pd.unique(sankey_df[["A", "S", "T"]].values.ravel()).tolist()
    idx = {n: i for i, n in enumerate(nodes)}

    source = sankey_df["A"].map(idx).tolist() + sankey_df["S"].map(idx).tolist()
    target = sankey_df["S"].map(idx).tolist() + sankey_df["T"].map(idx).tolist()
    value = sankey_df["minimum_amount"].tolist() * 2

    labels = [
        n.replace("A:", "Aspect: ")
         .replace("S:", "Sentiment: ")
         .replace("T:", "Tone: ")
        for n in nodes
    ]

    fig_sankey = go.Figure(
        data=[go.Sankey(
            node=dict(label=labels, pad=15, thickness=18),
            link=dict(source=source, target=target, value=value)
        )]
    )

    st.plotly_chart(fig_sankey, use_container_width=True)

# ----------------------------------------------------------
# HEATMAP
# ----------------------------------------------------------
st.markdown("## 🔥 Heatmap: Aspect × Sentiment")
add_section_explanation("## 🔥 Heatmap: Aspect × Sentiment")

pivot = filtered.pivot_table(
    index="aspect_category",
    columns="sentiment",
    values="minimum_amount",
    aggfunc="sum",
    fill_value=0
)

fig_heat = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues")
st.plotly_chart(fig_heat, use_container_width=True)

# ----------------------------------------------------------
# EXPORT
# ----------------------------------------------------------
st.markdown("## ⤵ Download Tone Distribution Table")
add_section_explanation("## ⤵ Download Tone Distribution Table")

st.download_button(
    "Download tone_distribution.csv",
    tone_df.to_csv(index=False).encode("utf-8"),
    file_name="tone_distribution.csv",
    mime="text/csv"
)

st.caption("Computed at runtime using dashboard/data ontologies.")


# # ==========================================================
# # 📊 Tone Distribution Explorer (Ontology-Aware, Fixed)
# # ==========================================================

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import json
# from pathlib import Path

# # ----------------------------------------------------------
# # PAGE CONFIG
# # ----------------------------------------------------------
# st.set_page_config(page_title="Tone Distribution Explorer", layout="wide")

# st.title("📊 Tone Distribution Explorer")
# st.write(
#     "Ontology-normalized tone distribution computed directly from "
#     "`output_in_csv.csv`."
# )

# # ----------------------------------------------------------
# # PATHS
# # ----------------------------------------------------------
# CURRENT_DIR = Path(__file__).resolve()
# PROJECT_ROOT = CURRENT_DIR.parents[2]
# DATA_DIR = PROJECT_ROOT / "data"

# MASTER_PATH = DATA_DIR / "output_in_csv.csv"

# # ----------------------------------------------------------
# # LOAD ONTOLOGIES
# # ----------------------------------------------------------
# with open(DATA_DIR / "aspect_category_ontology.json") as f:
#     ASPECT_ONTOLOGY = json.load(f)

# with open(DATA_DIR / "sentiment_ontology.json") as f:
#     SENTIMENT_ONTOLOGY = json.load(f)

# with open(DATA_DIR / "tone_ontology.json") as f:
#     TONE_ONTOLOGY = json.load(f)


# def build_alias_map(ontology):
#     m = {}
#     for canonical, meta in ontology.items():
#         for a in meta.get("aliases", []):
#             if a is not None:
#                 m[str(a).strip().lower()] = canonical
#     return m


# ASPECT_MAP = build_alias_map(ASPECT_ONTOLOGY)
# SENTIMENT_MAP = build_alias_map(SENTIMENT_ONTOLOGY)
# TONE_MAP = build_alias_map(TONE_ONTOLOGY)


# def normalize(val, mapping):
#     if pd.isna(val):
#         return "OTHER"
#     return mapping.get(str(val).strip().lower(), "OTHER")


# # ----------------------------------------------------------
# # LOAD MASTER DATA
# # ----------------------------------------------------------
# @st.cache_data
# def load_master():
#     df = pd.read_csv(MASTER_PATH)
#     df.columns = df.columns.str.lower().str.strip()
#     return df


# try:
#     raw = load_master()
# except Exception as e:
#     st.error(f"Failed to load dataset: {e}")
#     st.stop()

# st.success(f"Loaded {len(raw)} rows from output_in_csv.csv")

# # ----------------------------------------------------------
# # VALIDATE COLUMNS
# # ----------------------------------------------------------
# required_cols = {"aspect_category", "sentiment", "tone"}
# missing = required_cols - set(raw.columns)
# if missing:
#     st.error(f"Missing required columns: {missing}")
#     st.stop()

# # ----------------------------------------------------------
# # NORMALIZE USING ONTOLOGIES
# # ----------------------------------------------------------
# raw["aspect_norm"] = raw["aspect_category"].apply(lambda x: normalize(x, ASPECT_MAP))
# raw["sentiment_norm"] = raw["sentiment"].apply(lambda x: normalize(x, SENTIMENT_MAP))
# raw["tone_norm"] = raw["tone"].apply(lambda x: normalize(x, TONE_MAP))

# # ----------------------------------------------------------
# # COMPUTE TONE DISTRIBUTION (CORRECT MINIMUM)
# # ----------------------------------------------------------
# @st.cache_data
# def compute_tone_distribution(df):
#     rows = []

#     for (a, s), g in df.groupby(["aspect_norm", "sentiment_norm"]):
#         counts = g["tone_norm"].value_counts()

#         if counts.empty:
#             continue

#         min_tone = counts.idxmin()
#         min_amount = int(counts.min())

#         rows.append({
#             "aspect_category": a,
#             "sentiment": s,
#             "minimum_tone": min_tone,
#             "minimum_amount": min_amount,
#             "group_size": len(g)
#         })

#     return (
#         pd.DataFrame(rows)
#         .sort_values(["aspect_category", "sentiment"])
#         .reset_index(drop=True)
#     )


# tone_df = compute_tone_distribution(raw)

# st.subheader("Auto-Generated Tone Distribution")
# st.dataframe(tone_df, use_container_width=True)

# # ----------------------------------------------------------
# # SIDEBAR FILTERS
# # ----------------------------------------------------------
# st.sidebar.header("Filters")

# f_aspects = st.sidebar.multiselect(
#     "Aspect Category",
#     sorted(tone_df["aspect_category"].unique()),
#     default=sorted(tone_df["aspect_category"].unique())
# )

# f_sentiments = st.sidebar.multiselect(
#     "Sentiment",
#     sorted(tone_df["sentiment"].unique()),
#     default=sorted(tone_df["sentiment"].unique())
# )

# f_tones = st.sidebar.multiselect(
#     "Minimum Tone",
#     sorted(tone_df["minimum_tone"].unique()),
#     default=sorted(tone_df["minimum_tone"].unique())
# )

# filtered = tone_df[
#     tone_df["aspect_category"].isin(f_aspects) &
#     tone_df["sentiment"].isin(f_sentiments) &
#     tone_df["minimum_tone"].isin(f_tones)
# ]

# st.write(f"### Filtered Rows: {len(filtered)}")
# st.dataframe(filtered, use_container_width=True)

# # ----------------------------------------------------------
# # PIE — COMBINED MINIMUM TONE
# # ----------------------------------------------------------
# st.markdown("## 🥧 Combined Minimum Tone Distribution")

# if not filtered.empty:
#     pie_df = (
#         filtered.groupby("minimum_tone")["minimum_amount"]
#         .sum()
#         .reset_index()
#     )

#     fig_pie = px.pie(
#         pie_df,
#         names="minimum_tone",
#         values="minimum_amount",
#         hole=0.4
#     )
#     st.plotly_chart(fig_pie, use_container_width=True)

# # ----------------------------------------------------------
# # BAR — MINIMUM AMOUNT
# # ----------------------------------------------------------
# st.markdown("## 📦 Minimum Amount per Tone")

# fig_bar = px.bar(
#     filtered,
#     x="minimum_tone",
#     y="minimum_amount",
#     color="minimum_tone"
# )
# st.plotly_chart(fig_bar, use_container_width=True)

# # ----------------------------------------------------------
# # SANKEY — NAMESPACED (FIXED)
# # ----------------------------------------------------------
# st.markdown("## 🔗 Sankey: Aspect → Sentiment → Minimum Tone")

# if not filtered.empty:
#     sankey_df = (
#         filtered.groupby(["aspect_category", "sentiment", "minimum_tone"])["minimum_amount"]
#         .sum()
#         .reset_index()
#     )

#     sankey_df["A"] = sankey_df["aspect_category"].apply(lambda x: f"A:{x}")
#     sankey_df["S"] = sankey_df["sentiment"].apply(lambda x: f"S:{x}")
#     sankey_df["T"] = sankey_df["minimum_tone"].apply(lambda x: f"T:{x}")

#     nodes = pd.unique(sankey_df[["A", "S", "T"]].values.ravel()).tolist()
#     idx = {n: i for i, n in enumerate(nodes)}

#     src = sankey_df["A"].map(idx).tolist() + sankey_df["S"].map(idx).tolist()
#     tgt = sankey_df["S"].map(idx).tolist() + sankey_df["T"].map(idx).tolist()
#     val = sankey_df["minimum_amount"].tolist() * 2

#     labels = [
#         n.replace("A:", "Aspect: ")
#          .replace("S:", "Sentiment: ")
#          .replace("T:", "Tone: ")
#         for n in nodes
#     ]

#     fig_sankey = go.Figure(
#         data=[go.Sankey(
#             node=dict(label=labels, pad=15, thickness=18),
#             link=dict(source=src, target=tgt, value=val)
#         )]
#     )

#     st.plotly_chart(fig_sankey, use_container_width=True)

# # ----------------------------------------------------------
# # HEATMAP
# # ----------------------------------------------------------
# st.markdown("## 🔥 Heatmap: Aspect × Sentiment")

# pivot = filtered.pivot_table(
#     index="aspect_category",
#     columns="sentiment",
#     values="minimum_amount",
#     aggfunc="sum",
#     fill_value=0
# )

# fig_heat = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues")
# st.plotly_chart(fig_heat, use_container_width=True)

# # ----------------------------------------------------------
# # EXPORT TABLE
# # ----------------------------------------------------------
# st.markdown("## ⤵ Download Tone Distribution Table")

# st.download_button(
#     "Download tone_distribution.csv",
#     tone_df.to_csv(index=False).encode("utf-8"),
#     file_name="tone_distribution.csv",
#     mime="text/csv"
# )

# st.caption("Computed at runtime from output_in_csv.csv using ontologies.")
