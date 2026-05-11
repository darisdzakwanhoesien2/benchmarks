from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="JSON Ontology Usage Map", layout="wide")

BENCHMARKS_ROOT = Path("/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks")
NEW_PAGE_ROOT = BENCHMARKS_ROOT / "new_page"
NEW_PAGE_PAGES = NEW_PAGE_ROOT / "pages"
DOCS_DIR = NEW_PAGE_ROOT / "documentation" / "streamlit_pages"


JSON_REGISTRY = [
    {
        "id": "bench_aspect_cluster",
        "path": BENCHMARKS_ROOT / "data" / "aspect_cluster.json",
        "family": "Aspect clustering",
        "role": "Maps raw/free-text aspects into generated aspect clusters.",
        "recommended pages": "zz_aspect_clusters.py; esg_dashboard_new_02_Aspects_Clustered.py; esg_dashboard_new_03_Aspect_Comparison.py",
    },
    {
        "id": "bench_aspect_category_ontology",
        "path": BENCHMARKS_ROOT / "data" / "aspect_category_ontology.json",
        "family": "Aspect ontology",
        "role": "Canonical aspect-category ontology for Sankey, distribution, and tone pages.",
        "recommended pages": "Sankey.py; Tone_Distribution.py; Data Distribution.py; Data_New_Distribution.py",
    },
    {
        "id": "bench_sentiment_ontology",
        "path": BENCHMARKS_ROOT / "data" / "sentiment_ontology.json",
        "family": "Sentiment ontology",
        "role": "Canonical sentiment label ontology and display mapping.",
        "recommended pages": "Sankey.py; Tone_Distribution.py; Distribution Document.py; Data Distribution.py; Data_New_Distribution.py",
    },
    {
        "id": "bench_tone_ontology",
        "path": BENCHMARKS_ROOT / "data" / "tone_ontology.json",
        "family": "Tone ontology",
        "role": "Canonical ESG tone ontology for commitment/action/outcome/neutral-style views.",
        "recommended pages": "Sankey.py; Tone_Distribution.py; Distribution Document.py; Data Distribution.py; Data_New_Distribution.py",
    },
    {
        "id": "bench_mapping_category",
        "path": BENCHMARKS_ROOT / "data" / "mapping_category.json",
        "family": "Evaluation mapping",
        "role": "Maps aspect/category labels into grouped evaluation categories.",
        "recommended pages": "absa_metrics_comparison.py; absa_metrics_comparison_mac.py",
    },
    {
        "id": "bench_sentiment_category",
        "path": BENCHMARKS_ROOT / "data" / "sentiment_category.json",
        "family": "Evaluation mapping",
        "role": "Maps sentiment labels into grouped evaluation categories.",
        "recommended pages": "absa_metrics_comparison.py; absa_metrics_comparison_mac.py",
    },
    {
        "id": "bench_tone_category",
        "path": BENCHMARKS_ROOT / "data" / "tone_category.json",
        "family": "Evaluation mapping",
        "role": "Maps tone labels into grouped evaluation categories.",
        "recommended pages": "absa_metrics_comparison.py; absa_metrics_comparison_mac.py",
    },
    {
        "id": "new_revision_ontology",
        "path": NEW_PAGE_ROOT / "results" / "revision_analysis" / "ontology.json",
        "family": "Revision ontology",
        "role": "New-page ontology artifact used by the ontology path viewer.",
        "recommended pages": "1_6_Ontology_Path_Viewer.py; 1_7_Research_Questions_Dashboard.py",
    },
    {
        "id": "new_mapping",
        "path": NEW_PAGE_ROOT / "results" / "data" / "mapping.json",
        "family": "Evaluation mapping",
        "role": "New-page mapping artifact for ESG/prediction grouping and matching evaluation.",
        "recommended pages": "0_0_0_1_esg_matching_evaluation.py; future metrics pages",
    },
    {
        "id": "dash_aspect_category_ontology",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "aspect_category_ontology.json",
        "family": "Aspect ontology",
        "role": "Dashboard-local copy of the aspect-category ontology.",
        "recommended pages": "Sankey.py; Tone_Distribution.py; Data Distribution.py; Data_New_Distribution.py",
    },
    {
        "id": "dash_sentiment_ontology",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "sentiment_ontology.json",
        "family": "Sentiment ontology",
        "role": "Dashboard-local copy of the sentiment ontology.",
        "recommended pages": "Sankey.py; Tone_Distribution.py; Distribution Document.py; Data Distribution.py; Data_New_Distribution.py",
    },
    {
        "id": "dash_tone_ontology",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "tone_ontology.json",
        "family": "Tone ontology",
        "role": "Dashboard-local copy of the tone ontology.",
        "recommended pages": "Sankey.py; Tone_Distribution.py; Distribution Document.py; Data Distribution.py; Data_New_Distribution.py",
    },
    {
        "id": "dash_aspect_category_group_mapping",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "aspect_category_group_mapping.json",
        "family": "Aspect grouping",
        "role": "Alias and group mapping used to normalize aspect-category groups.",
        "recommended pages": "09_Data_File_Visualizer.py",
    },
    {
        "id": "dash_aspect_groupings",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "aspect_groupings.json",
        "family": "Aspect grouping",
        "role": "Base aspect grouping taxonomy used for grouped aspect analysis.",
        "recommended pages": "09_Data_File_Visualizer.py",
    },
    {
        "id": "dash_custom_aspect_groupings",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "custom_aspect_groupings.json",
        "family": "Aspect grouping",
        "role": "User-custom aspect grouping overrides and additions.",
        "recommended pages": "09_Data_File_Visualizer.py",
    },
    {
        "id": "dash_reporting_framework_aspects",
        "path": BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "reporting_framework_aspects.json",
        "family": "Reporting framework",
        "role": "Reporting-framework aspect taxonomy for mapping ESG aspects to disclosure frameworks.",
        "recommended pages": "09_Data_File_Visualizer.py",
    },
]


def render_mermaid(source: str, height: int = 680):
    components.html(
        f"""
        <div class="mermaid">
        {source}
        </div>
        <script type="module">
          import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
          mermaid.initialize({{
            startOnLoad: true,
            theme: "dark",
            flowchart: {{ curve: "basis", htmlLabels: true }}
          }});
        </script>
        """,
        height=height,
        scrolling=True,
    )


def safe_load_json(path: Path) -> tuple[Any | None, str]:
    if not path.exists():
        return None, "missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), "ok"
    except Exception as exc:
        return None, f"error: {exc}"


def summarize_json(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {"json type": "missing", "top-level count": 0, "top-level keys": "", "preview": ""}
    if isinstance(obj, dict):
        keys = list(obj.keys())
        preview_obj = {key: obj[key] for key in keys[:3]}
        return {
            "json type": "dict",
            "top-level count": len(keys),
            "top-level keys": ", ".join(map(str, keys[:12])),
            "preview": json.dumps(preview_obj, ensure_ascii=False)[:600],
        }
    if isinstance(obj, list):
        preview_obj = obj[:3]
        return {
            "json type": "list",
            "top-level count": len(obj),
            "top-level keys": "",
            "preview": json.dumps(preview_obj, ensure_ascii=False)[:600],
        }
    return {
        "json type": type(obj).__name__,
        "top-level count": 1,
        "top-level keys": "",
        "preview": str(obj)[:600],
    }


@st.cache_data(show_spinner=False)
def scan_references(file_names: tuple[str, ...]) -> pd.DataFrame:
    searchable_exts = {".py", ".md", ".json", ".toml"}
    rows = []
    skip_parts = {"__pycache__", ".git", "node_modules", ".venv", "venv"}
    for path in BENCHMARKS_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in searchable_exts:
            continue
        if any(part in skip_parts for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for file_name in file_names:
            if file_name in text:
                rows.append(
                    {
                        "json file": file_name,
                        "referencing file": str(path.relative_to(BENCHMARKS_ROOT)),
                        "kind": path.suffix.lstrip("."),
                    }
                )
    return pd.DataFrame(rows).drop_duplicates() if rows else pd.DataFrame(columns=["json file", "referencing file", "kind"])


def build_inventory() -> pd.DataFrame:
    rows = []
    for item in JSON_REGISTRY:
        obj, status = safe_load_json(item["path"])
        summary = summarize_json(obj)
        rows.append(
            {
                "id": item["id"],
                "file": item["path"].name,
                "family": item["family"],
                "status": status,
                "role": item["role"],
                "recommended pages": item["recommended pages"],
                "path": str(item["path"]),
                **summary,
            }
        )
    return pd.DataFrame(rows)


def build_usage_matrix(inventory: pd.DataFrame, references: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for item in JSON_REGISTRY:
        file_name = item["path"].name
        refs = references[references["json file"].eq(file_name)] if not references.empty else pd.DataFrame()
        streamlit_refs = []
        other_refs = []
        for ref in refs["referencing file"].tolist() if not refs.empty else []:
            if "/pages/" in ref or ref.startswith("pages/") or ref.startswith("new_page/pages/") or ref.endswith(".py"):
                streamlit_refs.append(ref)
            else:
                other_refs.append(ref)
        rows.append(
            {
                "json id": item["id"],
                "json file": file_name,
                "family": item["family"],
                "currently referenced by": "\n".join(sorted(streamlit_refs)) or "No direct reference found",
                "other references": "\n".join(sorted(other_refs[:8])),
                "recommended pages": item["recommended pages"],
                "status": inventory.loc[inventory["id"].eq(item["id"]), "status"].iloc[0],
            }
        )
    return pd.DataFrame(rows)


def file_tree_mermaid(inventory: pd.DataFrame) -> str:
    lines = ["flowchart LR"]
    families = sorted(inventory["family"].unique())
    for idx, family in enumerate(families, start=1):
        family_id = f"fam_{idx}"
        lines.append(f'  {family_id}["{family}"]')
        subset = inventory[inventory["family"].eq(family)]
        for j, row in enumerate(subset.to_dict("records"), start=1):
            node_id = f"{family_id}_{j}"
            label = f"{row['file']}<br/>{row['status']}"
            lines.append(f'  {node_id}["{label}"]')
            lines.append(f"  {family_id} --> {node_id}")
    return "\n".join(lines)


inventory_df = build_inventory()
references_df = scan_references(tuple(sorted({Path(item["path"]).name for item in JSON_REGISTRY})))
usage_df = build_usage_matrix(inventory_df, references_df)

st.title("JSON Ontology Usage Map")
st.caption("Map ontology, category, grouping, and mapping JSON files to the Streamlit pages that use or should use them.")

overview_tab, usage_tab, inspector_tab, refs_tab, diagram_tab = st.tabs(
    ["Overview", "Usage Matrix", "JSON Inspector", "Reference Scan", "Diagram"]
)

with overview_tab:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("JSON files", len(inventory_df))
    c2.metric("Found", int(inventory_df["status"].eq("ok").sum()))
    c3.metric("Families", inventory_df["family"].nunique())
    c4.metric("Direct reference rows", len(references_df))

    st.subheader("Inventory")
    st.dataframe(
        inventory_df[
            [
                "id",
                "file",
                "family",
                "status",
                "json type",
                "top-level count",
                "top-level keys",
                "role",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with usage_tab:
    st.subheader("Which Streamlit pages use each JSON")
    family_filter = st.multiselect(
        "Filter by family",
        sorted(usage_df["family"].unique()),
        default=sorted(usage_df["family"].unique()),
    )
    view = usage_df[usage_df["family"].isin(family_filter)].copy()
    st.dataframe(view, use_container_width=True, hide_index=True)

    st.info(
        "`currently referenced by` is based on a code/text scan for the JSON filename. "
        "`recommended pages` is the intended page-level use based on each JSON's semantic role."
    )

with inspector_tab:
    st.subheader("Inspect one JSON file")
    selected_id = st.selectbox("JSON artifact", inventory_df["id"].tolist())
    selected = next(item for item in JSON_REGISTRY if item["id"] == selected_id)
    obj, status = safe_load_json(selected["path"])
    st.write(f"Path: `{selected['path']}`")
    st.write(f"Status: `{status}`")
    st.write(f"Role: {selected['role']}")
    summary = summarize_json(obj)
    st.json(summary)
    with st.expander("Raw JSON preview", expanded=False):
        st.json(obj if obj is not None else {})

with refs_tab:
    st.subheader("Raw reference scan")
    st.dataframe(references_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download reference scan CSV",
        references_df.to_csv(index=False).encode("utf-8"),
        "json_ontology_reference_scan.csv",
        "text/csv",
    )

with diagram_tab:
    st.subheader("JSON families and artifacts")
    render_mermaid(file_tree_mermaid(inventory_df))
    st.subheader("Mermaid source")
    st.code(file_tree_mermaid(inventory_df), language="mermaid")
