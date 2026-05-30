import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Ontology Path Viewer", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "results" / "revision_analysis"
ONTOLOGY_PATH = ARTIFACTS / "ontology.json"
COVERAGE_PATH = ARTIFACTS / "ontology_coverage.csv"
SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"


def load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path):
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


st.title("Ontology Path Viewer")
st.caption("Trace records from raw text to predicted aspect and ontology path. This page provides evidence for the ontology-based ABSA contribution.")

ontology = load_json(ONTOLOGY_PATH)
coverage = load_csv(COVERAGE_PATH)
records = load_csv(SILVER_PATH)

if records.empty:
    st.error("No silver records found.")
    st.stop()

path_lookup = {}
for node in ontology.get("nodes", []):
    path_lookup[str(node.get("aspect", "")).lower()] = node

tabs = st.tabs(["Coverage", "Path Explorer", "Ontology JSON", "Unmapped Aspects"])

with tabs[0]:
    st.subheader("Ontology Coverage")
    if coverage.empty:
        st.warning("No coverage table found.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Observed aspects", f"{len(coverage):,}")
        c2.metric("Mapped aspects", f"{int(coverage['mapped_to_ontology'].sum()):,}")
        c3.metric("Coverage", f"{coverage['mapped_to_ontology'].mean():.1%}")
        chart = (
            alt.Chart(coverage.sort_values("records", ascending=False).head(25))
            .mark_bar()
            .encode(
                x=alt.X("records:Q", title="Records"),
                y=alt.Y("aspect:N", sort="-x", title=None),
                color=alt.Color("mapped_to_ontology:N", title="Mapped"),
                tooltip=["aspect", "records", "mapped_to_ontology", "suggested_path"],
            )
            .properties(height=580, title="Observed Aspects and Ontology Coverage")
        )
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(coverage, use_container_width=True)

with tabs[1]:
    st.subheader("Record-Level Path Explorer")
    aspects = sorted(records["aspect"].dropna().unique().tolist())
    selected_aspect = st.selectbox("Aspect", ["All"] + aspects)
    view = records.copy()
    if selected_aspect != "All":
        view = view[view["aspect"] == selected_aspect]
    selected_id = st.selectbox("Record", view["record_id"].tolist())
    row = view[view["record_id"] == selected_id].iloc[0]
    aspect = str(row["aspect"])
    node = path_lookup.get(aspect.lower())
    cov_row = coverage[coverage["aspect"].astype(str).str.lower() == aspect.lower()] if not coverage.empty else pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    c1.metric("Aspect", aspect)
    c2.metric("Tone", row["tone_pred"])
    c3.metric("ESG", row["esg"])

    st.markdown("**Raw text**")
    st.write(row["text"])
    st.markdown("**Reasoning**")
    st.write(row.get("reasoning", ""))

    st.markdown("**Ontology path**")
    if node:
        st.code(" -> ".join(node.get("path", [])))
        st.markdown("**Keywords**")
        st.write(", ".join(node.get("keywords", [])))
    elif not cov_row.empty and str(cov_row.iloc[0].get("suggested_path", "")).strip():
        st.warning("No canonical ontology node exists yet. Suggested path:")
        st.code(str(cov_row.iloc[0]["suggested_path"]))
    else:
        st.error("This aspect is currently unmapped.")

    st.markdown("**Record metadata**")
    st.json({k: row[k] for k in ["company", "prompt", "model", "language", "labels", "suggested_tone", "suggestion_source"] if k in row})

with tabs[2]:
    st.subheader("Machine-Readable Ontology")
    st.json(ontology)
    st.download_button("Download ontology.json", json.dumps(ontology, indent=2, ensure_ascii=False).encode("utf-8"), "ontology.json", "application/json")

with tabs[3]:
    st.subheader("Unmapped Aspect Candidates")
    if coverage.empty:
        st.info("Coverage table is not available.")
    else:
        unmapped = coverage[coverage["mapped_to_ontology"] == False].sort_values("records", ascending=False)
        st.dataframe(unmapped, use_container_width=True)
        st.download_button("Download unmapped aspects", unmapped.to_csv(index=False).encode("utf-8"), "unmapped_aspects.csv", "text/csv")
