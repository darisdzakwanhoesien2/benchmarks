import streamlit as st
import pandas as pd

from utils.aspect_clustering import cluster_aspect
from utils.data_loader import load_and_parse, sorted_unique_values

st.set_page_config(page_title="Aspect Workspace", layout="wide")
st.title("🧩 Aspect Workspace")
st.markdown(
    """
This page combines the full aspect review workflow into one place.

**What this page does**
- shows the most frequent raw extracted aspects
- groups those labels into manual aspect clusters
- compares raw labels against their clustered mapping
- highlights labels that still fall into `Unclustered` or `Undefined`

**What this page expects**
- parsed ESG sentence records from the resolved `data_output` dataset
- an `aspect` field in the parsed annotations
- the manual clustering rules in `utils.aspect_clustering`

**How to use it**
- start in **Raw Aspects** to see the vocabulary your models extracted
- move to **Clustered Aspects** to inspect thematic rollups
- use **Mapping Review** when refining taxonomy rules or QA-ing cluster behavior
"""
)

df = load_and_parse()

if df.empty or "aspect" not in df.columns:
    st.warning("No aspect data available.")
    st.stop()

df = df.copy()
df["aspect"] = df["aspect"].astype(str).str.strip()
df["aspect_cluster"] = df["aspect"].apply(cluster_aspect)

non_empty_df = df[df["aspect"].ne("")]

summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.metric("Parsed Rows", f"{len(df):,}")
summary_col2.metric("Unique Raw Aspects", f"{non_empty_df['aspect'].nunique():,}")
summary_col3.metric(
    "Unique Aspect Clusters",
    f"{non_empty_df['aspect_cluster'].astype(str).nunique():,}"
)

raw_tab, cluster_tab, comparison_tab = st.tabs(
    ["Raw Aspects", "Clustered Aspects", "Mapping Review"]
)

with raw_tab:
    st.markdown(
        """
### Raw Aspect View
Review the original extracted aspect labels before any manual grouping.
This is the best place to spot duplicate phrasing, noisy labels, and ontology gaps.
"""
    )

    raw_n = st.slider("Show Top N Raw Aspects", 3, 50, 15, key="aspect_raw_n")

    top_raw = (
        non_empty_df["aspect"]
        .value_counts()
        .sort_values(ascending=False)
        .head(raw_n)
    )

    raw_df = top_raw.reset_index()
    raw_df.columns = ["aspect", "count"]
    raw_df["aspect"] = pd.Categorical(
        raw_df["aspect"],
        categories=raw_df["aspect"].tolist(),
        ordered=True,
    )

    st.bar_chart(raw_df.set_index("aspect")["count"])
    st.dataframe(raw_df, use_container_width=True)

with cluster_tab:
    st.markdown(
        """
### Clustered Aspect View
This view rolls granular aspect labels into broader, auditable clusters.
Use it when you want a thematic summary instead of label-level detail.
"""
    )

    cluster_n = st.slider(
        "Show Top N Aspect Clusters",
        3,
        30,
        10,
        key="aspect_cluster_n",
    )

    top_clusters = (
        non_empty_df["aspect_cluster"]
        .value_counts()
        .sort_values(ascending=False)
        .head(cluster_n)
    )

    cluster_df = top_clusters.reset_index()
    cluster_df.columns = ["aspect_cluster", "count"]
    cluster_df["aspect_cluster"] = pd.Categorical(
        cluster_df["aspect_cluster"],
        categories=cluster_df["aspect_cluster"].tolist(),
        ordered=True,
    )

    st.bar_chart(cluster_df.set_index("aspect_cluster")["count"])
    st.dataframe(cluster_df, use_container_width=True)

    unclustered_labels = {"Unclustered", "Undefined"}
    unclustered_df = (
        non_empty_df[non_empty_df["aspect_cluster"].isin(unclustered_labels)]
        .groupby("aspect")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    st.subheader("🚨 Unclustered Aspects")
    if unclustered_df.empty:
        st.success("No unclustered aspects found.")
    else:
        st.markdown(
            """
These labels were not confidently assigned into a stable cluster.
They are good candidates for taxonomy cleanup or new cluster rules.
"""
        )
        st.dataframe(unclustered_df, use_container_width=True)

with comparison_tab:
    st.markdown(
        """
### Raw-to-Cluster Mapping Review
This table shows how each raw aspect label is being translated into a cluster.
Use it to audit mapping coverage and verify that high-frequency labels land in the right group.
"""
    )

    mapping_scope = st.radio(
        "Mapping scope",
        ["All data", "Top raw aspects table"],
        horizontal=True,
        help="Use all parsed aspect rows, or limit the mapping review to the same high-frequency labels shown in the raw aspect table.",
    )

    if mapping_scope == "Top raw aspects table":
        review_n = st.slider(
            "Top raw aspects to map",
            3,
            100,
            25,
            key="aspect_mapping_top_n",
        )
        top_aspect_labels = (
            non_empty_df["aspect"]
            .value_counts()
            .head(review_n)
            .index
        )
        mapping_source = non_empty_df[non_empty_df["aspect"].isin(top_aspect_labels)]
    else:
        mapping_source = non_empty_df

    cluster_options = sorted_unique_values(mapping_source["aspect_cluster"])
    selected_clusters = st.multiselect(
        "Filter by aspect cluster",
        cluster_options,
        default=cluster_options,
    )

    comparison = (
        mapping_source[mapping_source["aspect_cluster"].map(str).isin(selected_clusters)][
            ["aspect", "aspect_cluster"]
        ]
        .value_counts()
        .reset_index(name="count")
        .sort_values(["count", "aspect"], ascending=[False, True])
    )

    st.dataframe(comparison, use_container_width=True)
