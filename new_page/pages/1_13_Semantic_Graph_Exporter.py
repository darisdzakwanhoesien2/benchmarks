from __future__ import annotations

import io
from pathlib import Path
import sys

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from semantic_exporter import (  # noqa: E402
    EXPORT_DIR,
    build_neo4j_files,
    build_owl_xml,
    build_turtle,
    canonical_records,
    export_all,
    load_semantic_bundle,
    ontology_rows,
    write_exports,
    zip_bytes,
)


st.set_page_config(page_title="Semantic Graph Exporter", layout="wide")

st.title("Semantic Graph Exporter")
st.caption("Export the ESG thesis evidence layer into RDF Turtle, OWL/RDF-XML, and Neo4j import files.")

bundle = load_semantic_bundle()
records = canonical_records(bundle)
onto = ontology_rows(bundle)

metric_cols = st.columns(5)
metric_cols[0].metric("ESG records", f"{len(records):,}")
metric_cols[1].metric("Companies", f"{records['company'].nunique():,}" if "company" in records else "0")
metric_cols[2].metric("Aspects", f"{records['aspect'].nunique():,}" if "aspect" in records else "0")
metric_cols[3].metric("Ontology rows", f"{len(onto):,}")
metric_cols[4].metric("Output folder", EXPORT_DIR.name)

with st.expander("Semantic mapping used in the export", expanded=True):
    st.markdown(
        """
        - `ESGRecord` nodes are created from `silver_tone_ground_truth.csv` when available, otherwise `tone_records_flat.csv`.
        - Each record links to `Company`, `Model`, `Prompt`, `Aspect`, `ESGPillar`, `Tone`, `Sentiment`, and `ClimateLabel`.
        - Ontology rows link `Aspect` to `OntologyPath` using `ontology_coverage.csv` and `ontology.json`.
        - Neo4j export is split into `neo4j_nodes.csv`, `neo4j_relationships.csv`, and `neo4j_load.cypher`.
        """
    )

left, right = st.columns([1, 1], gap="large")
with left:
    limit_mode = st.radio("Export size", ["All records", "Preview subset"], horizontal=True)
with right:
    preview_n = st.number_input("Preview/export subset rows", min_value=10, max_value=max(len(records), 10), value=min(100, max(len(records), 10)), step=10)
limit = None if limit_mode == "All records" else int(preview_n)

tabs = st.tabs(["Preview", "RDF Turtle", "OWL", "Neo4j", "Export Files"])

with tabs[0]:
    st.subheader("Record graph preview")
    st.dataframe(records.head(100).astype(str), use_container_width=True, height=320)
    st.subheader("Ontology path preview")
    st.dataframe(onto.head(100).astype(str), use_container_width=True, height=260)

with tabs[1]:
    ttl = build_turtle(bundle, limit)
    st.subheader("RDF Turtle")
    st.download_button("Download RDF Turtle (.ttl)", ttl.encode("utf-8"), "esg_thesis_graph.ttl", "text/turtle", use_container_width=True)
    st.code(ttl[:12000], language="turtle")
    if len(ttl) > 12000:
        st.caption(f"Preview truncated from {len(ttl):,} characters. Download for full file.")

with tabs[2]:
    owl = build_owl_xml(bundle, limit)
    st.subheader("OWL / RDF-XML")
    st.download_button("Download OWL (.owl)", owl.encode("utf-8"), "esg_thesis_ontology.owl", "application/rdf+xml", use_container_width=True)
    st.code(owl[:12000], language="xml")
    if len(owl) > 12000:
        st.caption(f"Preview truncated from {len(owl):,} characters. Download for full file.")

with tabs[3]:
    neo = build_neo4j_files(bundle, limit)
    st.subheader("Neo4j import package")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Download nodes CSV", neo["neo4j_nodes.csv"], "neo4j_nodes.csv", "text/csv", use_container_width=True)
    c2.download_button("Download relationships CSV", neo["neo4j_relationships.csv"], "neo4j_relationships.csv", "text/csv", use_container_width=True)
    c3.download_button("Download Cypher loader", neo["neo4j_load.cypher"], "neo4j_load.cypher", "text/plain", use_container_width=True)
    node_df = pd.read_csv(io.BytesIO(neo["neo4j_nodes.csv"]))
    rel_df = pd.read_csv(io.BytesIO(neo["neo4j_relationships.csv"]))
    st.markdown("#### Nodes")
    st.dataframe(node_df.head(100).astype(str), use_container_width=True, height=280)
    st.markdown("#### Relationships")
    st.dataframe(rel_df.head(100).astype(str), use_container_width=True, height=280)
    st.markdown("#### Loader")
    st.code(neo["neo4j_load.cypher"].decode("utf-8"), language="cypher")

with tabs[4]:
    st.subheader("Write and download all semantic exports")
    files = export_all(bundle, limit)
    st.download_button(
        "Download RDF + OWL + Neo4j ZIP",
        zip_bytes(files),
        "esg_semantic_exports.zip",
        "application/zip",
        use_container_width=True,
    )
    if st.button("Write exports to results/semantic_exports", type="primary", use_container_width=True):
        paths = write_exports(bundle, limit)
        st.success(f"Wrote {len(paths):,} files to `{EXPORT_DIR}`")
        st.dataframe(
            pd.DataFrame([{"file": name, "path": str(path), "bytes": path.stat().st_size} for name, path in paths.items()]),
            use_container_width=True,
            hide_index=True,
        )
