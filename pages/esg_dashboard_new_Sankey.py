# ==========================================================
# 📤 Upload-Based Tone Distribution & Balancer (Ontology-Aware)
# ==========================================================

import streamlit as st
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(page_title="Upload-Based Tone Balancer", layout="wide")

st.title("📤 Upload-Based Tone Distribution & Balancer")
add_page_explanation(__file__)
st.write(
    "Upload a dataset and generate ontology-normalized tone distributions, "
    "Sankey graphs, and balanced datasets."
)

def build_alias_map(ontology):
    mapping = {}
    for canonical, meta in ontology.items():
        for alias in meta.get("aliases", []):
            if alias is not None:
                mapping[str(alias).strip().lower()] = canonical
    return mapping
def normalize(value, mapping):
    if pd.isna(value):
        return "OTHER"
    return mapping.get(str(value).strip().lower(), "OTHER")

# ----------------------------------------------------------
# LOAD ONTOLOGIES
# ----------------------------------------------------------
BASE_DATA_PATH = Path(__file__).resolve().parents[1] / "data"
with open(BASE_DATA_PATH / "aspect_category_ontology.json") as f:
    ASPECT_ONTOLOGY = json.load(f)
with open(BASE_DATA_PATH / "sentiment_ontology.json") as f:
    SENTIMENT_ONTOLOGY = json.load(f)
with open(BASE_DATA_PATH / "tone_ontology.json") as f:
    TONE_ONTOLOGY = json.load(f)

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
# FILE UPLOADER & DATASET SELECTION
# ----------------------------------------------------------
st.header("1️⃣ Upload Your Dataset")
add_section_explanation("1️⃣ Upload Your Dataset")
from pathlib import Path
import json

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

uploaded = st.file_uploader("Or upload CSV file", type=["csv"])

if selected_file:
    df = pd.read_csv(selected_file)
    st.sidebar.success(f"Loaded dataset: {selected_file}")
elif uploaded is not None:
    df = pd.read_csv(uploaded)
    st.sidebar.success("Loaded uploaded file")
else:
    st.info("Please select a dataset or upload a CSV file to continue.")
    st.stop()
df.columns = df.columns.str.lower().str.strip()

required_cols = ["aspect_category", "sentiment", "tone"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

st.success(f"✅ File uploaded successfully. Loaded {len(df)} rows.")

# ----------------------------------------------------------
# NORMALIZE USING ONTOLOGIES
# ----------------------------------------------------------
df["aspect_norm"] = df["aspect_category"].apply(lambda x: normalize(x, ASPECT_MAP))
df["sentiment_norm"] = df["sentiment"].apply(lambda x: normalize(x, SENTIMENT_MAP))
df["tone_norm"] = df["tone"].apply(lambda x: normalize(x, TONE_MAP))

# ----------------------------------------------------------
# COMPUTE TONE DISTRIBUTION TABLE
# ----------------------------------------------------------
@st.cache_data
def compute_tone_distribution(df):
    rows = []

    grouped = df.groupby(["aspect_norm", "sentiment_norm"])

    for (aspect, sentiment), g in grouped:
        tone_counts = g["tone_norm"].value_counts()

        if tone_counts.empty:
            continue

        minimum_tone = tone_counts.idxmin()
        minimum_amount = int(tone_counts.min())

        rows.append({
            "aspect_category": aspect,
            "sentiment": sentiment,
            "minimum_tone": minimum_tone,
            "minimum_amount": minimum_amount,
            "group_count": len(g)
        })

    return (
        pd.DataFrame(rows)
        .sort_values(["aspect_category", "sentiment"])
        .reset_index(drop=True)
    )


tone_df = compute_tone_distribution(df)

st.header("2️⃣ Generated Tone Distribution Table")
add_section_explanation("2️⃣ Generated Tone Distribution Table")
st.dataframe(tone_df, use_container_width=True)

# ----------------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------------
st.sidebar.header("Filters")

selected_aspects = st.sidebar.multiselect(
    "Aspect Category",
    sorted(tone_df["aspect_category"].unique()),
    default=sorted(tone_df["aspect_category"].unique())
)

selected_sentiments = st.sidebar.multiselect(
    "Sentiment",
    sorted(tone_df["sentiment"].unique()),
    default=sorted(tone_df["sentiment"].unique())
)

selected_tones = st.sidebar.multiselect(
    "Minimum Tone",
    sorted(tone_df["minimum_tone"].unique()),
    default=sorted(tone_df["minimum_tone"].unique())
)

filtered = tone_df[
    tone_df["aspect_category"].isin(selected_aspects) &
    tone_df["sentiment"].isin(selected_sentiments) &
    tone_df["minimum_tone"].isin(selected_tones)
]

st.write(f"### Filtered Rows: {len(filtered)}")
st.dataframe(filtered, use_container_width=True)

# ----------------------------------------------------------
# COMBINED TONE DISTRIBUTION PIE
# ----------------------------------------------------------
st.markdown("## 🥧 Combined Minimum-Tone Distribution")
add_section_explanation("## 🥧 Combined Minimum-Tone Distribution")

if not filtered.empty:
    combined = (
        filtered.groupby("minimum_tone")["minimum_amount"]
        .sum()
        .reset_index()
    )

    fig_pie = px.pie(
        combined,
        names="minimum_tone",
        values="minimum_amount",
        hole=0.4,
        title="Combined Minimum-Tone Distribution"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ----------------------------------------------------------
# SANKEY — Aspect → Sentiment → Tone (NAMESPACED)
# ----------------------------------------------------------
st.markdown("## 🔗 Aspect → Sentiment → Tone Sankey")
add_section_explanation("## 🔗 Aspect → Sentiment → Tone Sankey")

if not filtered.empty:
    sankey_data = (
        filtered
        .groupby(["aspect_category", "sentiment", "minimum_tone"])["minimum_amount"]
        .sum()
        .reset_index()
    )

    # Namespace nodes to avoid collisions
    sankey_data["aspect_node"] = sankey_data["aspect_category"].apply(
        lambda x: f"ASPECT_{x}"
    )
    sankey_data["sentiment_node"] = sankey_data["sentiment"].apply(
        lambda x: f"SENTIMENT_{x}"
    )
    sankey_data["tone_node"] = sankey_data["minimum_tone"].apply(
        lambda x: f"TONE_{x}"
    )

    nodes = pd.unique(
        sankey_data[["aspect_node", "sentiment_node", "tone_node"]]
        .values.ravel()
    ).tolist()

    idx = {n: i for i, n in enumerate(nodes)}

    source = (
        sankey_data["aspect_node"].map(idx).tolist() +
        sankey_data["sentiment_node"].map(idx).tolist()
    )
    target = (
        sankey_data["sentiment_node"].map(idx).tolist() +
        sankey_data["tone_node"].map(idx).tolist()
    )
    value = sankey_data["minimum_amount"].tolist() * 2

    # Human-readable labels
    labels = [
        n.replace("ASPECT_", "Aspect: ")
         .replace("SENTIMENT_", "Sentiment: ")
         .replace("TONE_", "Tone: ")
        for n in nodes
    ]

    fig_sankey = go.Figure(
        data=[go.Sankey(
            node=dict(
                label=labels,
                pad=15,
                thickness=18
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            )
        )]
    )

    fig_sankey.update_layout(title_text="Aspect → Sentiment → Tone Flow")
    st.plotly_chart(fig_sankey, use_container_width=True)

# ----------------------------------------------------------
# BALANCED DATASET EXPORT
# ----------------------------------------------------------
st.markdown("## 🎯 Balanced Dataset Export")
add_section_explanation("## 🎯 Balanced Dataset Export")

sample_n = st.number_input(
    "Number of samples per group",
    min_value=1,
    max_value=2000,
    value=50,
    step=1
)

if not filtered.empty:
    balanced_rows = []

    for _, row in filtered.iterrows():
        subset = df[
            (df["aspect_norm"] == row["aspect_category"]) &
            (df["sentiment_norm"] == row["sentiment"]) &
            (df["tone_norm"] == row["minimum_tone"])
        ]

        if subset.empty:
            continue

        sampled = subset.sample(
            sample_n,
            replace=len(subset) < sample_n,
            random_state=42
        )

        sampled = sampled.copy()
        sampled["target_aspect"] = row["aspect_category"]
        sampled["target_sentiment"] = row["sentiment"]
        sampled["target_tone"] = row["minimum_tone"]

        balanced_rows.append(sampled)

    if balanced_rows:
        balanced_df = pd.concat(balanced_rows, ignore_index=True)

        st.success(f"✅ Balanced dataset created with {len(balanced_df)} rows.")
        st.dataframe(balanced_df.head(20), use_container_width=True)

        st.download_button(
            "⬇ Download Balanced Dataset (CSV)",
            balanced_df.to_csv(index=False).encode("utf-8"),
            file_name=f"balanced_dataset_{sample_n}_per_group.csv",
            mime="text/csv"
        )


# # ==========================================================
# # 📤 Upload-Based Tone Distribution & Balancer (Ontology-Aware)
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
# st.set_page_config(page_title="Upload-Based Tone Balancer", layout="wide")

# st.title("📤 Upload-Based Tone Distribution & Balancer")
# st.write(
#     "Upload a dataset and generate ontology-normalized tone distributions, "
#     "Sankey graphs, and balanced datasets."
# )

# # ----------------------------------------------------------
# # LOAD ONTOLOGIES
# # ----------------------------------------------------------
# BASE_DATA_PATH = Path(__file__).resolve().parents[1] / "data"

# with open(BASE_DATA_PATH / "aspect_category_ontology.json") as f:
#     ASPECT_ONTOLOGY = json.load(f)

# with open(BASE_DATA_PATH / "sentiment_ontology.json") as f:
#     SENTIMENT_ONTOLOGY = json.load(f)

# with open(BASE_DATA_PATH / "tone_ontology.json") as f:
#     TONE_ONTOLOGY = json.load(f)


# def build_alias_map(ontology):
#     mapping = {}
#     for canonical, meta in ontology.items():
#         for alias in meta.get("aliases", []):
#             if alias is not None:
#                 mapping[str(alias).strip().lower()] = canonical
#     return mapping


# ASPECT_MAP = build_alias_map(ASPECT_ONTOLOGY)
# SENTIMENT_MAP = build_alias_map(SENTIMENT_ONTOLOGY)
# TONE_MAP = build_alias_map(TONE_ONTOLOGY)


# def normalize(value, mapping):
#     if pd.isna(value):
#         return "OTHER"
#     return mapping.get(str(value).strip().lower(), "OTHER")


# # ----------------------------------------------------------
# # FILE UPLOADER
# # ----------------------------------------------------------
# st.header("1️⃣ Upload Your Dataset")

# uploaded = st.file_uploader("Upload CSV file", type=["csv"])

# if not uploaded:
#     st.info("Please upload a CSV file to continue.")
#     st.stop()

# df = pd.read_csv(uploaded)
# df.columns = df.columns.str.lower().str.strip()

# required_cols = ["aspect_category", "sentiment", "tone"]
# missing = [c for c in required_cols if c not in df.columns]
# if missing:
#     st.error(f"❌ Missing required columns: {missing}")
#     st.stop()

# st.success(f"✅ File uploaded successfully. Loaded {len(df)} rows.")

# # ----------------------------------------------------------
# # NORMALIZE USING ONTOLOGIES (CRITICAL)
# # ----------------------------------------------------------
# df["aspect_norm"] = df["aspect_category"].apply(lambda x: normalize(x, ASPECT_MAP))
# df["sentiment_norm"] = df["sentiment"].apply(lambda x: normalize(x, SENTIMENT_MAP))
# df["tone_norm"] = df["tone"].apply(lambda x: normalize(x, TONE_MAP))

# # ----------------------------------------------------------
# # COMPUTE TONE DISTRIBUTION TABLE
# # ----------------------------------------------------------
# @st.cache_data
# def compute_tone_distribution(df):
#     rows = []

#     grouped = df.groupby(["aspect_norm", "sentiment_norm"])

#     for (aspect, sentiment), g in grouped:
#         tone_counts = g["tone_norm"].value_counts()

#         if tone_counts.empty:
#             continue

#         minimum_tone = tone_counts.idxmin()
#         minimum_amount = int(tone_counts.min())

#         descending_order = ", ".join(tone_counts.index.tolist())
#         data_distribution = ", ".join(str(int(v)) for v in tone_counts.values.tolist())

#         rows.append({
#             "aspect_category": aspect,
#             "sentiment": sentiment,
#             "minimum_tone": minimum_tone,
#             "minimum_amount": minimum_amount,
#             "descending_order": descending_order,
#             "data_distribution": data_distribution,
#             "group_count": len(g)
#         })

#     return (
#         pd.DataFrame(rows)
#         .sort_values(["aspect_category", "sentiment"])
#         .reset_index(drop=True)
#     )


# tone_df = compute_tone_distribution(df)

# st.header("2️⃣ Generated Tone Distribution Table")
# st.dataframe(tone_df, use_container_width=True)

# # ----------------------------------------------------------
# # SIDEBAR FILTERS
# # ----------------------------------------------------------
# st.sidebar.header("Filters")

# selected_aspects = st.sidebar.multiselect(
#     "Aspect Category",
#     sorted(tone_df["aspect_category"].unique()),
#     default=sorted(tone_df["aspect_category"].unique())
# )

# selected_sentiments = st.sidebar.multiselect(
#     "Sentiment",
#     sorted(tone_df["sentiment"].unique()),
#     default=sorted(tone_df["sentiment"].unique())
# )

# selected_tones = st.sidebar.multiselect(
#     "Minimum Tone",
#     sorted(tone_df["minimum_tone"].unique()),
#     default=sorted(tone_df["minimum_tone"].unique())
# )

# filtered = tone_df[
#     tone_df["aspect_category"].isin(selected_aspects) &
#     tone_df["sentiment"].isin(selected_sentiments) &
#     tone_df["minimum_tone"].isin(selected_tones)
# ]

# st.write(f"### Filtered Rows: {len(filtered)}")
# st.dataframe(filtered, use_container_width=True)

# # ----------------------------------------------------------
# # COMBINED TONE DISTRIBUTION PIE
# # ----------------------------------------------------------
# st.markdown("## 🥧 Combined Minimum-Tone Distribution")

# if filtered.empty:
#     st.info("No groups match your filters.")
# else:
#     combined = (
#         filtered.groupby("minimum_tone")["minimum_amount"]
#         .sum()
#         .reset_index()
#     )

#     fig_pie = px.pie(
#         combined,
#         names="minimum_tone",
#         values="minimum_amount",
#         hole=0.4,
#         title="Combined Minimum-Tone Distribution"
#     )
#     st.plotly_chart(fig_pie, use_container_width=True)

# # ----------------------------------------------------------
# # BAR CHART — MINIMUM AMOUNT
# # ----------------------------------------------------------
# st.markdown("## 📦 Minimum Amount by Tone")

# if not filtered.empty:
#     fig_bar = px.bar(
#         filtered,
#         x="minimum_tone",
#         y="minimum_amount",
#         color="minimum_tone",
#         title="Minimum Tone Amount per Group"
#     )
#     st.plotly_chart(fig_bar, use_container_width=True)

# # ----------------------------------------------------------
# # DESCENDING ORDER EXAMPLE
# # ----------------------------------------------------------
# st.markdown("## 📉 Tone Ranking Example")

# if not filtered.empty:
#     first = filtered.iloc[0]
#     ranks = [x.strip() for x in first["descending_order"].split(",")]

#     fig_rank = go.Figure(
#         data=[go.Bar(
#             x=list(range(1, len(ranks) + 1)),
#             y=[1] * len(ranks),
#             text=ranks,
#             textposition="inside"
#         )]
#     )
#     fig_rank.update_layout(
#         xaxis_title="Rank",
#         yaxis=dict(showticklabels=False),
#         title="Example Tone Ranking"
#     )
#     st.plotly_chart(fig_rank, use_container_width=True)

# # ----------------------------------------------------------
# # SANKEY — Aspect → Sentiment → Tone
# # ----------------------------------------------------------
# st.markdown("## 🔗 Aspect → Sentiment → Tone Sankey")

# if not filtered.empty:
#     sankey_data = (
#         filtered
#         .groupby(["aspect_category", "sentiment", "minimum_tone"])["minimum_amount"]
#         .sum()
#         .reset_index()
#     )

#     nodes = list(pd.unique(
#         sankey_data[["aspect_category", "sentiment", "minimum_tone"]].values.ravel()
#     ))
#     idx = {n: i for i, n in enumerate(nodes)}

#     source = (
#         sankey_data["aspect_category"].map(idx).tolist() +
#         sankey_data["sentiment"].map(idx).tolist()
#     )
#     target = (
#         sankey_data["sentiment"].map(idx).tolist() +
#         sankey_data["minimum_tone"].map(idx).tolist()
#     )
#     value = sankey_data["minimum_amount"].tolist() * 2

#     fig_sankey = go.Figure(
#         data=[go.Sankey(
#             node=dict(label=nodes, pad=15, thickness=18),
#             link=dict(source=source, target=target, value=value)
#         )]
#     )

#     fig_sankey.update_layout(title_text="Aspect → Sentiment → Tone Flow")
#     st.plotly_chart(fig_sankey, use_container_width=True)

# # ----------------------------------------------------------
# # BALANCED DATASET EXPORT
# # ----------------------------------------------------------
# st.markdown("## 🎯 Balanced Dataset Export")

# sample_n = st.number_input(
#     "Number of samples per group",
#     min_value=1,
#     max_value=2000,
#     value=50,
#     step=1
# )

# if filtered.empty:
#     st.info("No groups to export.")
# else:
#     balanced_rows = []

#     for _, row in filtered.iterrows():
#         subset = df[
#             (df["aspect_norm"] == row["aspect_category"]) &
#             (df["sentiment_norm"] == row["sentiment"]) &
#             (df["tone_norm"] == row["minimum_tone"])
#         ]

#         if subset.empty:
#             continue

#         sampled = (
#             subset.sample(sample_n, replace=len(subset) < sample_n, random_state=42)
#         )

#         sampled = sampled.copy()
#         sampled["target_aspect"] = row["aspect_category"]
#         sampled["target_sentiment"] = row["sentiment"]
#         sampled["target_tone"] = row["minimum_tone"]

#         balanced_rows.append(sampled)

#     if balanced_rows:
#         balanced_df = pd.concat(balanced_rows, ignore_index=True)

#         st.success(f"✅ Balanced dataset created with {len(balanced_df)} rows.")
#         st.dataframe(balanced_df.head(20), use_container_width=True)

#         st.download_button(
#             "⬇ Download Balanced Dataset (CSV)",
#             balanced_df.to_csv(index=False).encode("utf-8"),
#             file_name=f"balanced_dataset_{sample_n}_per_group.csv",
#             mime="text/csv"
#         )
#     else:
#         st.warning("No matching rows found for sampling.")
