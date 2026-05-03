# ==============================================================
# 🪢 Sankey + Waterfall + Multi-Rule ESG Explorer (ONTOLOGY-AWARE)
# ==============================================================
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import plotly.graph_objects as go
import json
import os
import sys
from pathlib import Path

# --------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------
st.set_page_config(page_title="ESG Sankey & Filters", layout="wide")
st.header("🔎 ESG Sankey · Waterfall · Multi-Rule Explorer")
add_page_explanation(__file__)

# --------------------------------------------------------------
# PATHS
# --------------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_DIR.parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "output_in_csv.csv"
ONTOLOGY_DIR = PROJECT_ROOT / "data"

# --------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------
@st.cache_data
def load_dataset():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.lower().str.strip()
    return df

df = load_dataset()

# --------------------------------------------------------------
# VALIDATION
# --------------------------------------------------------------
required_cols = {"aspect_category", "sentiment", "tone"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

# --------------------------------------------------------------
# LOAD ONTOLOGIES
# --------------------------------------------------------------
def load_ontology(name):
    with open(ONTOLOGY_DIR / name) as f:
        return json.load(f)

ASPECT_ONTOLOGY = load_ontology("aspect_category_ontology.json")
SENTIMENT_ONTOLOGY = load_ontology("sentiment_ontology.json")
TONE_ONTOLOGY = load_ontology("tone_ontology.json")

# --------------------------------------------------------------
# BUILD ALIAS MAPS
# --------------------------------------------------------------
def build_alias_map(ontology):
    m = {}
    for canonical, meta in ontology.items():
        for alias in meta.get("aliases", []):
            if alias is None:
                continue
            m[str(alias).strip().lower()] = canonical
    return m

ASPECT_MAP = build_alias_map(ASPECT_ONTOLOGY)
SENTIMENT_MAP = build_alias_map(SENTIMENT_ONTOLOGY)
TONE_MAP = build_alias_map(TONE_ONTOLOGY)

def normalize(val, mapping):
    if pd.isna(val):
        return "OTHER"
    return mapping.get(str(val).strip().lower(), "OTHER")

# --------------------------------------------------------------
# APPLY ONTOLOGY NORMALIZATION
# --------------------------------------------------------------
df["aspect_n"] = df["aspect_category"].apply(lambda x: normalize(x, ASPECT_MAP))
df["sentiment_n"] = df["sentiment"].apply(lambda x: normalize(x, SENTIMENT_MAP))
df["tone_n"] = df["tone"].apply(lambda x: normalize(x, TONE_MAP))

# ==============================================================
# 🪢 GLOBAL SANKEY (SORTED + NAMESPACED)
# ==============================================================
st.markdown("## 🪢 Sankey: Aspect → Sentiment → Tone (Ontology Normalized)")
add_section_explanation("## 🪢 Sankey: Aspect → Sentiment → Tone (Ontology Normalized)")

flow = (
    df.groupby(["aspect_n", "sentiment_n", "tone_n"])
      .size()
      .reset_index(name="count")
)

aspect_order = flow.groupby("aspect_n")["count"].sum().sort_values(ascending=False).index.tolist()
sentiment_order = flow.groupby("sentiment_n")["count"].sum().sort_values(ascending=False).index.tolist()
tone_order = flow.groupby("tone_n")["count"].sum().sort_values(ascending=False).index.tolist()

A = [f"A:{a}" for a in aspect_order]
S = [f"S:{s}" for s in sentiment_order]
T = [f"T:{t}" for t in tone_order]

nodes = A + S + T
idx = {n: i for i, n in enumerate(nodes)}

links = {"source": [], "target": [], "value": []}

for _, r in flow.iterrows():
    a, s, t, c = r["aspect_n"], r["sentiment_n"], r["tone_n"], r["count"]
    if c <= 0:
        continue
    links["source"] += [idx[f"A:{a}"], idx[f"S:{s}"]]
    links["target"] += [idx[f"S:{s}"], idx[f"T:{t}"]]
    links["value"] += [c, c]

labels = (
    [f"Aspect: {ASPECT_ONTOLOGY.get(a, {}).get('label', a)}" for a in aspect_order] +
    [f"Sentiment: {SENTIMENT_ONTOLOGY.get(s, {}).get('label', s)}" for s in sentiment_order] +
    [f"Tone: {TONE_ONTOLOGY.get(t, {}).get('label', t)}" for t in tone_order]
)

fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(label=labels, pad=18, thickness=18),
    link=links
)])

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# 📋 POST-SANKEY CATEGORY INSPECTION
# ==============================================================
st.markdown("---")
st.subheader("📋 Detected Categories (Ontology vs Data)")
add_section_explanation("📋 Detected Categories (Ontology vs Data)")

def category_table(df, col, title, ontology):
    summary = (
        df[col]
        .value_counts()
        .reset_index()
    )
    summary.columns = [col, "count"]
    total = summary["count"].sum()

    summary["percentage"] = (summary["count"] / total * 100).round(2)
    summary["label"] = summary[col].apply(
        lambda x: ontology.get(x, {}).get("label", "❓ Not in ontology")
    )

    st.markdown(f"### {title}")
    st.dataframe(summary, use_container_width=True)

    flagged = summary[
        (summary[col] == "OTHER") |
        (summary["percentage"] < 1.0)
    ]

    if not flagged.empty:
        st.warning("⚠️ Review low-frequency or fallback categories")
        st.dataframe(flagged, use_container_width=True)

with st.expander("📌 Aspect Categories", expanded=True):
    category_table(df, "aspect_n", "Aspect Categories", ASPECT_ONTOLOGY)

with st.expander("📌 Sentiment Categories", expanded=False):
    category_table(df, "sentiment_n", "Sentiment Categories", SENTIMENT_ONTOLOGY)

with st.expander("📌 Tone Categories", expanded=False):
    category_table(df, "tone_n", "Tone Categories", TONE_ONTOLOGY)

# ==============================================================
# 1️⃣ WATERFALL FILTER
# ==============================================================
st.markdown("---")
st.subheader("1️⃣ Waterfall Filter")
add_section_explanation("1️⃣ Waterfall Filter")

a = st.selectbox("Aspect", ["(All)"] + aspect_order)
s = st.selectbox("Sentiment", ["(All)"] + sentiment_order)
t = st.selectbox("Tone", ["(All)"] + tone_order)

tmp = df.copy()
if a != "(All)": tmp = tmp[tmp["aspect_n"] == a]
if s != "(All)": tmp = tmp[tmp["sentiment_n"] == s]
if t != "(All)": tmp = tmp[tmp["tone_n"] == t]

st.success(f"🎯 Matching rows: {len(tmp)}")
st.dataframe(tmp, use_container_width=True)

# ==============================================================
# 2️⃣ MULTI-RULE BUILDER
# ==============================================================
st.markdown("---")
st.subheader("2️⃣ Multi-Rule Builder")
add_section_explanation("2️⃣ Multi-Rule Builder")

if "rules" not in st.session_state:
    st.session_state.rules = []

if st.button("➕ Add Rule"):
    st.session_state.rules.append({
        "aspect": "(Any)",
        "sentiment": "(Any)",
        "tone": "(Any)",
        "take_n": 10
    })

results = []

for i, rule in enumerate(st.session_state.rules):
    with st.expander(f"Rule #{i+1}", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])

        rule["aspect"] = c1.selectbox("Aspect", ["(Any)"] + aspect_order, key=f"a{i}")
        rule["sentiment"] = c2.selectbox("Sentiment", ["(Any)"] + sentiment_order, key=f"s{i}")
        rule["tone"] = c3.selectbox("Tone", ["(Any)"] + tone_order, key=f"t{i}")

        if c4.button("🗑", key=f"del{i}"):
            st.session_state.rules.pop(i)
            st.experimental_rerun()

        filt = df.copy()
        if rule["aspect"] != "(Any)": filt = filt[filt["aspect_n"] == rule["aspect"]]
        if rule["sentiment"] != "(Any)": filt = filt[filt["sentiment_n"] == rule["sentiment"]]
        if rule["tone"] != "(Any)": filt = filt[filt["tone_n"] == rule["tone"]]

        st.info(f"Matches: {len(filt)}")

        rule["take_n"] = st.number_input(
            "Take N rows",
            min_value=1,
            max_value=max(1, len(filt)),
            value=min(rule["take_n"], max(1, len(filt))),
            key=f"n{i}"
        )

        subset = filt.head(rule["take_n"])
        st.dataframe(subset, use_container_width=True)

        results.append({
            "Rule": i + 1,
            "Aspect": rule["aspect"],
            "Sentiment": rule["sentiment"],
            "Tone": rule["tone"],
            "Count": len(filt),
            "Take N": rule["take_n"]
        })

# ==============================================================
# 📊 SUMMARY
# ==============================================================
if results:
    st.markdown("### 📊 Rule Summary")
    add_section_explanation("### 📊 Rule Summary")
    st.dataframe(pd.DataFrame(results), use_container_width=True)


# # ==============================================================
# # 🪢 Sankey + Waterfall + Multi-Rule ESG Explorer (FIXED)
# # ==============================================================
# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import os
# import sys

# # --------------------------------------------------------------
# # PAGE CONFIG
# # --------------------------------------------------------------
# st.set_page_config(page_title="ESG Sankey & Filters", layout="wide")
# st.header("🔎 ESG Sankey · Waterfall · Multi-Rule Explorer")

# # --------------------------------------------------------------
# # LOAD DATA
# # --------------------------------------------------------------
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
# sys.path.append(PROJECT_ROOT)

# @st.cache_data
# def load_dataset():
#     path = os.path.join(PROJECT_ROOT, "data/output_in_csv.csv")
#     df = pd.read_csv(path)
#     df.columns = df.columns.str.lower().str.strip()
#     return df

# df = load_dataset()

# # --------------------------------------------------------------
# # VALIDATION
# # --------------------------------------------------------------
# required = {"aspect_category", "sentiment", "tone"}
# missing = required - set(df.columns)
# if missing:
#     st.error(f"Missing columns: {missing}")
#     st.stop()

# # --------------------------------------------------------------
# # 🔧 NORMALIZATION (MINIMAL, SAFE)
# # --------------------------------------------------------------
# def norm(x):
#     if pd.isna(x):
#         return "OTHER"
#     return str(x).strip().upper()

# df["aspect_n"] = df["aspect_category"].apply(norm)
# df["sentiment_n"] = df["sentiment"].apply(norm)
# df["tone_n"] = df["tone"].apply(norm)

# # ==============================================================
# # 🪢 GLOBAL SANKEY (NAMESPACED + SORTED)
# # ==============================================================
# st.markdown("## 🪢 Sankey: Aspect → Sentiment → Tone (Sorted by Frequency)")

# flow = (
#     df.groupby(["aspect_n", "sentiment_n", "tone_n"])
#     .size()
#     .reset_index(name="count")
# )

# # Frequency ordering
# aspect_order = flow.groupby("aspect_n")["count"].sum().sort_values(ascending=False).index.tolist()
# sentiment_order = flow.groupby("sentiment_n")["count"].sum().sort_values(ascending=False).index.tolist()
# tone_order = flow.groupby("tone_n")["count"].sum().sort_values(ascending=False).index.tolist()

# # Namespaced nodes
# A = [f"A:{a}" for a in aspect_order]
# S = [f"S:{s}" for s in sentiment_order]
# T = [f"T:{t}" for t in tone_order]

# nodes = A + S + T
# idx = {n: i for i, n in enumerate(nodes)}

# links = {"source": [], "target": [], "value": []}

# for _, r in flow.iterrows():
#     a, s, t, c = r["aspect_n"], r["sentiment_n"], r["tone_n"], r["count"]
#     if c <= 0:
#         continue

#     links["source"] += [idx[f"A:{a}"], idx[f"S:{s}"]]
#     links["target"] += [idx[f"S:{s}"], idx[f"T:{t}"]]
#     links["value"] += [c, c]

# labels = (
#     [x.replace("A:", "Aspect: ") for x in A] +
#     [x.replace("S:", "Sentiment: ") for x in S] +
#     [x.replace("T:", "Tone: ") for x in T]
# )

# fig = go.Figure(data=[go.Sankey(
#     arrangement="snap",
#     node=dict(
#         pad=18,
#         thickness=18,
#         label=labels
#     ),
#     link=links
# )])

# st.plotly_chart(fig, use_container_width=True)

# # ==============================================================
# # 📋 DETECTED CATEGORIES (POST-SANKEY INSPECTION)
# # ==============================================================

# st.markdown("---")
# st.subheader("📋 Detected Aspect, Sentiment & Tone Categories")

# def category_table(df, col, title):
#     summary = (
#         df[col]
#         .value_counts()
#         .reset_index()
#         .rename(columns={"index": col, col: "count"})
#     )
#     summary["percentage"] = (summary["count"] / summary["count"].sum() * 100).round(2)
#     summary = summary.sort_values("count", ascending=False)

#     st.markdown(f"### {title}")
#     st.dataframe(
#         summary,
#         use_container_width=True
#     )

#     # Highlight potentially problematic values
#     flagged = summary[
#         summary[col].isin(["OTHER", "NONE", "UNKNOWN"])
#         | (summary["percentage"] < 1.0)
#     ]

#     if not flagged.empty:
#         st.warning("⚠️ Low-frequency or fallback categories detected")
#         st.dataframe(flagged, use_container_width=True)


# with st.expander("📌 Aspect Categories", expanded=True):
#     category_table(df, "aspect_n", "Aspect Categories")

# with st.expander("📌 Sentiments", expanded=False):
#     category_table(df, "sentiment_n", "Sentiment Categories")

# with st.expander("📌 Tones", expanded=False):
#     category_table(df, "tone_n", "Tone Categories")


# # ==============================================================
# # 1️⃣ WATERFALL FILTER
# # ==============================================================
# st.markdown("---")
# st.subheader("1️⃣ Waterfall Filter")

# aspect_opts = sorted(df["aspect_n"].unique())
# sentiment_opts = sorted(df["sentiment_n"].unique())
# tone_opts = sorted(df["tone_n"].unique())

# a = st.selectbox("Aspect", ["(All)"] + aspect_opts)
# s = st.selectbox("Sentiment", ["(All)"] + sentiment_opts)
# t = st.selectbox("Tone", ["(All)"] + tone_opts)

# temp = df.copy()
# if a != "(All)": temp = temp[temp["aspect_n"] == a]
# if s != "(All)": temp = temp[temp["sentiment_n"] == s]
# if t != "(All)": temp = temp[temp["tone_n"] == t]

# st.success(f"🎯 Matching rows: {len(temp)}")
# st.dataframe(temp, use_container_width=True)

# # ==============================================================
# # 2️⃣ MULTI-RULE BUILDER
# # ==============================================================
# st.markdown("---")
# st.subheader("2️⃣ Multi-Rule Builder")

# if "rules" not in st.session_state:
#     st.session_state.rules = []

# if st.button("➕ Add Rule"):
#     st.session_state.rules.append({
#         "aspect": "(Any)",
#         "sentiment": "(Any)",
#         "tone": "(Any)",
#         "take_n": 10
#     })

# results = []

# for i, rule in enumerate(st.session_state.rules):
#     with st.expander(f"Rule #{i+1}", expanded=True):
#         c1, c2, c3, c4 = st.columns([2,2,2,1])

#         rule["aspect"] = c1.selectbox(
#             "Aspect", ["(Any)"] + aspect_opts,
#             index=(["(Any)"] + aspect_opts).index(rule["aspect"]),
#             key=f"a{i}"
#         )

#         rule["sentiment"] = c2.selectbox(
#             "Sentiment", ["(Any)"] + sentiment_opts,
#             index=(["(Any)"] + sentiment_opts).index(rule["sentiment"]),
#             key=f"s{i}"
#         )

#         rule["tone"] = c3.selectbox(
#             "Tone", ["(Any)"] + tone_opts,
#             index=(["(Any)"] + tone_opts).index(rule["tone"]),
#             key=f"t{i}"
#         )

#         if c4.button("🗑", key=f"del{i}"):
#             st.session_state.rules.pop(i)
#             st.experimental_rerun()

#         tmp = df.copy()
#         if rule["aspect"] != "(Any)": tmp = tmp[tmp["aspect_n"] == rule["aspect"]]
#         if rule["sentiment"] != "(Any)": tmp = tmp[tmp["sentiment_n"] == rule["sentiment"]]
#         if rule["tone"] != "(Any)": tmp = tmp[tmp["tone_n"] == rule["tone"]]

#         st.info(f"Matches: {len(tmp)}")

#         rule["take_n"] = st.number_input(
#             "Take N rows",
#             min_value=1,
#             max_value=max(1, len(tmp)),
#             value=min(rule["take_n"], max(1, len(tmp))),
#             key=f"n{i}"
#         )

#         subset = tmp.head(rule["take_n"])
#         st.dataframe(subset, use_container_width=True)

#         results.append({
#             "Rule": i+1,
#             "Aspect": rule["aspect"],
#             "Sentiment": rule["sentiment"],
#             "Tone": rule["tone"],
#             "Count": len(tmp),
#             "Take N": rule["take_n"]
#         })

# # ==============================================================
# # SUMMARY
# # ==============================================================
# if results:
#     st.markdown("### 📊 Rule Summary")
#     st.dataframe(pd.DataFrame(results), use_container_width=True)
