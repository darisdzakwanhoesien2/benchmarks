from __future__ import annotations

import json
from pathlib import Path
import re

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls
import streamlit.components.v1 as components


st.set_page_config(page_title="Thesis Systematic Workflow", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "documentation" / "thesis_systematic_workflow.md"
DASHBOARD_OUTPUT_DIR = ROOT / "results" / "thesis_workflow_dashboard"
DASHBOARD_REPORT_PATH = DASHBOARD_OUTPUT_DIR / "thesis_dashboard_report.md"
DASHBOARD_SECTIONS_PATH = DASHBOARD_OUTPUT_DIR / "rq_report_sections.json"
DASHBOARD_METRICS_PATH = DASHBOARD_OUTPUT_DIR / "dashboard_metrics.json"
DASHBOARD_IMAGE_MANIFEST_PATH = DASHBOARD_OUTPUT_DIR / "dashboard_image_manifest.json"


def read_workflow() -> str:
    if not WORKFLOW_PATH.exists():
        return ""
    return WORKFLOW_PATH.read_text(encoding="utf-8", errors="ignore")


def render_mermaid(source: str, height: int = 620) -> None:
    components.html(
        f"""
        <div class="mermaid">
        {source}
        </div>
        <script type="module">
          import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
          mermaid.initialize({{
            startOnLoad: true,
            theme: "default",
            flowchart: {{ curve: "basis", htmlLabels: true }}
          }});
        </script>
        """,
        height=height,
        scrolling=True,
    )


def extract_mermaid(markdown: str) -> str:
    match = re.search(r"```mermaid\n(?P<body>[\s\S]*?)\n```", markdown)
    return match.group("body") if match else ""


def extract_section(markdown: str, heading: str) -> str:
    pattern = rf"(^## {re.escape(heading)}[\s\S]*?)(?=^## |\Z)"
    match = re.search(pattern, markdown, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def strip_mermaid(markdown: str) -> str:
    return re.sub(r"```mermaid\n[\s\S]*?\n```", "", markdown)


def read_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


st.title("Thesis Systematic Workflow")
st.caption("Executable workflow derived from `thesis_draft_1.pdf`: generated data, integration points, and execution order.")

markdown = read_workflow()
if not markdown:
    st.error(f"Missing workflow file: `{WORKFLOW_PATH}`")
    st.stop()

with st.sidebar:
    st.header("Sections")
    view = st.radio(
        "View",
        [
            "Overview",
            "Generated Data",
            "Integration Architecture",
            "Execution Order",
            "Schema",
            "Dashboard Report",
            "Full Document",
        ],
    )
    st.markdown(f"Source: `{WORKFLOW_PATH}`")
    st.markdown(f"Dashboard report: `{DASHBOARD_REPORT_PATH}`")

if view == "Overview":
    mermaid = extract_mermaid(markdown)
    if mermaid:
        render_mermaid(mermaid)
    st.markdown(extract_section(markdown, "1. Research Workflow Overview").split("```mermaid")[0])
    st.markdown(extract_section(markdown, "2. Research Questions to Executable Modules"))
elif view == "Generated Data":
    st.markdown(extract_section(markdown, "3. Data That Can Be Generated"))
elif view == "Integration Architecture":
    st.markdown(extract_section(markdown, "4. Integration Architecture"))
    st.markdown(extract_section(markdown, "8. Streamlit Page Map"))
    st.markdown(extract_section(markdown, "9. Integration Priorities"))
elif view == "Execution Order":
    st.markdown(extract_section(markdown, "5. Recommended Execution Order"))
    st.markdown(extract_section(markdown, "6. Minimum Viable Thesis Dataset"))
elif view == "Schema":
    st.markdown(extract_section(markdown, "7. Practical Data Schema"))
    st.markdown(extract_section(markdown, "10. Final Target"))
elif view == "Dashboard Report":
    st.subheader("Dashboard Output Integration")
    if not DASHBOARD_REPORT_PATH.exists():
        st.warning("No saved dashboard report found yet. Open `5_Thesis_Systematic_Workflow_dashboard.py` once to generate it.")
        st.stop()

    metrics = read_json(DASHBOARD_METRICS_PATH)
    sections = read_json(DASHBOARD_SECTIONS_PATH)
    image_manifest = read_json(DASHBOARD_IMAGE_MANIFEST_PATH)

    if isinstance(metrics, dict):
        m = st.columns(5)
        m[0].metric("Tone records", f"{int(metrics.get('tone_records', 0)):,}")
        m[1].metric("T2 rows", f"{int(metrics.get('t2_rows', 0)):,}")
        m[2].metric("Pilot labels", f"{int(metrics.get('pilot_labels', 0)):,}")
        m[3].metric("Artifacts", f"{int(metrics.get('artifacts', 0)):,}")
        kappa = pd.to_numeric(metrics.get("climatebert_cohen_kappa"), errors="coerce")
        m[4].metric("RQ3 kappa", f"{kappa:.3f}" if pd.notna(kappa) else "n/a")

    st.caption(f"Saved Markdown report: `{DASHBOARD_REPORT_PATH}`")
    st.caption(f"Structured RQ sections: `{DASHBOARD_SECTIONS_PATH}`")

    if isinstance(sections, list) and sections:
        labels = [f"{item.get('rq', '')} - {item.get('title', '')}" for item in sections]
        selected = st.selectbox("Research question report section", labels)
        section = sections[labels.index(selected)]
        st.markdown(f"### {section.get('rq')} results")
        st.write(section.get("results", ""))
        st.markdown(f"### {section.get('rq')} graph")
        st.write(section.get("graph", ""))
        st.markdown(f"### {section.get('rq')} interpretation analysis")
        st.write(section.get("interpretation", ""))
        st.markdown(f"### {section.get('rq')} baseline needed")
        st.info(section.get("baseline", ""))
        st.markdown(f"### {section.get('rq')} discussion")
        st.write(section.get("discussion", ""))
        st.markdown(f"### {section.get('rq')} conclusion")
        st.success(section.get("conclusion", ""))

    if isinstance(image_manifest, list) and image_manifest:
        st.subheader("Attached graph files")
        cols = st.columns(2)
        for index, row in enumerate(image_manifest):
            saved = row.get("saved_to")
            if not saved:
                continue
            image_path = ROOT / saved
            with cols[index % 2]:
                if image_path.exists():
                    st.image(str(image_path), caption=row.get("name", image_path.name), use_column_width=True)

    with st.expander("Full saved Markdown report", expanded=False):
        st.markdown(DASHBOARD_REPORT_PATH.read_text(encoding="utf-8", errors="ignore"))
else:
    st.markdown(strip_mermaid(markdown))
