from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Thesis Systematic Workflow", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "documentation" / "thesis_systematic_workflow.md"


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
            "Full Document",
        ],
    )
    st.markdown(f"Source: `{WORKFLOW_PATH}`")

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
else:
    st.markdown(strip_mermaid(markdown))
