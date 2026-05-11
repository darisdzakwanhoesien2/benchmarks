from pathlib import Path
import json
import sys

import pandas as pd
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import render_mermaid


st.set_page_config(page_title="JSON Ontology Usage Map", layout="wide")
st.title("JSON Ontology Usage Map")
st.caption("Maps ontology, category, cluster, and mapping JSON files to the Streamlit pages that use or reference them.")

BENCHMARKS_ROOT = Path("/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks")
CURRENT_PAGES_DIR = BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "pages"
NEW_PAGE_PAGES_DIR = BENCHMARKS_ROOT / "new_page" / "pages"

JSON_PATHS = [
    BENCHMARKS_ROOT / "data" / "aspect_cluster.json",
    BENCHMARKS_ROOT / "data" / "aspect_category_ontology.json",
    BENCHMARKS_ROOT / "data" / "sentiment_ontology.json",
    BENCHMARKS_ROOT / "data" / "tone_ontology.json",
    BENCHMARKS_ROOT / "data" / "mapping_category.json",
    BENCHMARKS_ROOT / "data" / "sentiment_category.json",
    BENCHMARKS_ROOT / "data" / "tone_category.json",
    BENCHMARKS_ROOT / "new_page" / "results" / "revision_analysis" / "ontology.json",
    BENCHMARKS_ROOT / "new_page" / "results" / "data" / "mapping.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "aspect_category_ontology.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "sentiment_ontology.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "tone_ontology.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "aspect_category_group_mapping.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "aspect_groupings.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "custom_aspect_groupings.json",
    BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard" / "data" / "reporting_framework_aspects.json",
]

PAGE_ROUTE_OVERRIDES = {
    "00_Parsed_ESG_JSON.py": "/Parsed_ESG_JSON",
    "01_Aspect.py": "/Aspect",
    "02_ClimateBERT_Dataset_Processor.py": "/ClimateBERT_Dataset_Processor",
    "03_ClimateBERT_Result_Visualizer.py": "/ClimateBERT_Result_Visualizer",
    "04_Research_Questions_Visualizer.py": "/Research_Questions_Visualizer",
    "05_Sample_Size_Reasoning.py": "/Sample_Size_Reasoning",
    "06_Chapter_4_Results.py": "/Chapter_4_Results",
    "07_Chapter_5_Discussion.py": "/Chapter_5_Discussion",
    "08_Parsed_ESG_Review.py": "/Parsed_ESG_Review",
    "09_Data_File_Visualizer.py": "/Data_File_Visualizer",
    "10_Chapter_6_Conclusion.py": "/Chapter_6_Conclusion",
    "11_Streamlit_Page_Workflow_Guide.py": "/Streamlit_Page_Workflow_Guide",
    "12_JSON_Ontology_Usage_Map.py": "/JSON_Ontology_Usage_Map",
    "0_0_Streamlit_Page_Workflow.py": "/0_Streamlit_Page_Workflow",
    "Benchmark_Model.py": "/Benchmark_Model",
    "Data Distribution.py": "/Data_Distribution",
    "Data_New_Distribution.py": "/Data_New_Distribution",
    "Distribution Document.py": "/Distribution_Document",
    "Research_Questions_Dashboard.py": "/Research_Questions_Dashboard",
    "Sankey.py": "/Sankey",
    "Tone_Distribution.py": "/Tone_Distribution",
}


def page_route(page_path: Path) -> str:
    if page_path.name in PAGE_ROUTE_OVERRIDES:
        return PAGE_ROUTE_OVERRIDES[page_path.name]
    stem = page_path.stem
    parts = stem.split("_", 1)
    if parts and parts[0].isdigit() and len(parts) > 1:
        stem = parts[1]
    return "/" + stem.replace(" ", "_")


def load_json_summary(path: Path) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "type": "missing",
            "top_level_keys": "",
            "top_level_count": 0,
            "preview": None,
            "error": "File does not exist",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "exists": True,
            "type": "invalid",
            "top_level_keys": "",
            "top_level_count": 0,
            "preview": None,
            "error": str(exc),
        }

    if isinstance(data, dict):
        keys = list(data.keys())
        preview = {key: data[key] for key in keys[:5]}
        return {
            "exists": True,
            "type": "dict",
            "top_level_keys": ", ".join(map(str, keys[:12])),
            "top_level_count": len(keys),
            "preview": preview,
            "error": "",
        }
    if isinstance(data, list):
        return {
            "exists": True,
            "type": "list",
            "top_level_keys": "",
            "top_level_count": len(data),
            "preview": data[:5],
            "error": "",
        }
    return {
        "exists": True,
        "type": type(data).__name__,
        "top_level_keys": "",
        "top_level_count": 1,
        "preview": data,
        "error": "",
    }


@st.cache_data
def scan_page_usage(json_paths_as_str):
    json_paths = [Path(path) for path in json_paths_as_str]
    page_dirs = [CURRENT_PAGES_DIR, NEW_PAGE_PAGES_DIR]
    pages = []
    for page_dir in page_dirs:
        if page_dir.exists():
            pages.extend(sorted(page_dir.glob("*.py")))

    rows = []
    for json_path in json_paths:
        basename = json_path.name
        absolute = str(json_path)
        for page in pages:
            try:
                source = page.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            basename_hit = basename in source
            absolute_hit = absolute in source
            parent_hit = str(json_path.parent) in source and basename_hit
            if basename_hit or absolute_hit or parent_hit:
                rows.append(
                    {
                        "json_file": basename,
                        "json_path": absolute,
                        "streamlit_page": page.name,
                        "page_path": str(page),
                        "route": page_route(page),
                        "match_type": "absolute path" if absolute_hit else "basename",
                    }
                )
    return pd.DataFrame(rows)


def build_json_usage_mermaid(usage_df: pd.DataFrame) -> str:
    if usage_df.empty:
        return 'flowchart LR\n  Empty["No Streamlit page references found"]'

    lines = ["flowchart LR"]
    json_nodes = {}
    page_nodes = {}
    for _, row in usage_df.iterrows():
        json_id = "json_" + str(abs(hash(row["json_path"])))
        page_id = "page_" + str(abs(hash(row["page_path"])))
        json_nodes[json_id] = row["json_file"]
        page_nodes[page_id] = row["streamlit_page"]
        lines.append(f'  {json_id}["{row["json_file"]}"]')
        lines.append(f'  {page_id}["{row["streamlit_page"]}"]')
        lines.append(f"  {json_id} --> {page_id}")

    lines.extend([
        "  classDef json fill:#ecfdf5,stroke:#16a34a,color:#111827;",
        "  classDef page fill:#eef6ff,stroke:#2563eb,color:#111827;",
        f"  class {','.join(json_nodes.keys())} json;",
        f"  class {','.join(page_nodes.keys())} page;",
    ])
    return "\n".join(lines)


def json_purpose(path: Path) -> tuple[str, str]:
    name = path.name
    if "aspect_cluster" in name:
        return "Aspect clustering", "RQ2, RQ4"
    if "aspect_category_ontology" in name:
        return "Aspect category ontology", "RQ2"
    if "sentiment" in name:
        return "Sentiment ontology/category", "RQ2"
    if "tone" in name:
        return "Tone ontology/category", "RQ2, RQ6"
    if "aspect_category_group_mapping" in name:
        return "Aspect category grouping and aliases", "RQ2, RQ4"
    if name in {"aspect_groupings.json", "custom_aspect_groupings.json", "reporting_framework_aspects.json"}:
        return "Aspect taxonomy normalization", "RQ2, RQ4, RQ5"
    if name in {"mapping.json", "mapping_category.json"}:
        return "Category mapping", "RQ2, RQ5"
    if name == "ontology.json":
        return "Generated ontology artifact", "RQ2, RQ4, RQ5"
    return "Reference JSON", "RQ1-RQ6"


json_rows = []
for path in JSON_PATHS:
    summary = load_json_summary(path)
    purpose, rqs = json_purpose(path)
    json_rows.append(
        {
            "file": path.name,
            "path": str(path),
            "exists": summary["exists"],
            "type": summary["type"],
            "top_level_count": summary["top_level_count"],
            "top_level_keys": summary["top_level_keys"],
            "purpose": purpose,
            "supports": rqs,
            "error": summary["error"],
        }
    )

json_df = pd.DataFrame(json_rows)
usage_df = scan_page_usage([str(path) for path in JSON_PATHS])

tab_overview, tab_usage, tab_preview, tab_diagram = st.tabs([
    "Overview",
    "Streamlit Usage",
    "JSON Preview",
    "Usage Diagram",
])

with tab_overview:
    st.subheader("JSON Files Included")
    st.write(
        "This table lists the ontology, category, cluster, and mapping JSON files you provided. "
        "It shows whether each file exists, what it appears to contain, and which RQs it supports."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("JSON files", len(json_df))
    c2.metric("Existing files", int(json_df["exists"].sum()))
    c3.metric("Referenced files", usage_df["json_path"].nunique() if not usage_df.empty else 0)
    st.dataframe(json_df, use_container_width=True, height=520)

with tab_usage:
    st.subheader("Which Streamlit Pages Use Each JSON")
    st.write(
        "This scan searches Streamlit page source code for each JSON basename or absolute path. "
        "If a JSON is not listed here, it may be unused by the current pages or loaded indirectly by a utility module."
    )
    if usage_df.empty:
        st.warning("No direct Streamlit page references were found for the listed JSON files.")
    else:
        st.dataframe(usage_df, use_container_width=True, height=520)
        selected_json = st.selectbox(
            "Filter usage by JSON",
            sorted(usage_df["json_file"].unique()),
        )
        filtered_usage = usage_df[usage_df["json_file"] == selected_json]
        st.dataframe(filtered_usage, use_container_width=True)
        for _, row in filtered_usage.iterrows():
            st.link_button(f"Open {row['streamlit_page']}", row["route"], use_container_width=True)

with tab_preview:
    st.subheader("JSON Structure Preview")
    selected_path = st.selectbox(
        "Choose JSON file",
        [str(path) for path in JSON_PATHS],
        format_func=lambda value: Path(value).name,
    )
    selected = Path(selected_path)
    summary = load_json_summary(selected)
    st.markdown(f"**Path:** `{selected}`")
    st.markdown(f"**Exists:** {summary['exists']}")
    st.markdown(f"**Type:** {summary['type']}")
    st.markdown(f"**Top-level count:** {summary['top_level_count']}")
    if summary["error"]:
        st.error(summary["error"])
    elif summary["preview"] is not None:
        st.json(summary["preview"])

with tab_diagram:
    st.subheader("JSON to Streamlit Page Usage Diagram")
    mermaid = build_json_usage_mermaid(usage_df)
    render_mermaid(mermaid, height=720)
    st.code(mermaid, language="mermaid")
