import hashlib
import json
from pathlib import Path
import sys

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    COMPLETE_WORKFLOW_MERMAID,
    EXISTING_DATA_PATH,
    PREDICTION_OUTPUT_DIR,
    RQ_WORKFLOWS,
    STREAMLIT_PAGE_CATALOG,
    page_link_grid,
    render_mermaid,
)


st.set_page_config(page_title="Streamlit Page Workflow Guide", layout="wide")
st.title("Streamlit Page Workflow Guide")
st.caption("A practical guide for what every Streamlit page does, which RQ it supports, and where to go next.")

st.caption(f"Existing data: `{EXISTING_DATA_PATH}`")
st.caption(f"Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")


def render_safe_mermaid(code: str, height: int = 520) -> None:
    container_id = "workflow_guide_mermaid_" + hashlib.md5(code.encode("utf-8")).hexdigest()
    code_json = json.dumps(code)
    html = f"""
    <div id="{container_id}_wrapper" class="diagram-shell">
      <div id="{container_id}"></div>
      <div id="{container_id}_error" class="diagram-error"></div>
    </div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.5/dist/mermaid.esm.min.mjs";
      const initMermaid = (flowchartOpts) => mermaid.initialize({{
        startOnLoad: false,
        securityLevel: "loose",
        theme: "base",
        flowchart: flowchartOpts,
        themeVariables: {{
          background: "#ffffff",
          mainBkg: "#f8fafc",
          primaryColor: "#f8fafc",
          primaryTextColor: "#111827",
          primaryBorderColor: "#64748b",
          lineColor: "#475569",
          textColor: "#111827",
          fontFamily: "Inter, Arial, sans-serif"
        }}
      }});
      const code = {code_json};
      const target = document.getElementById("{container_id}");
      const errorTarget = document.getElementById("{container_id}_error");
      try {{
        initMermaid({{
          htmlLabels: false,
          curve: "basis",
          padding: 18,
          useMaxWidth: true
        }});
        const rendered = await mermaid.render("{container_id}_svg", code);
        target.innerHTML = rendered.svg;
        const svg = target.querySelector("svg");
        if (svg) {{
          svg.style.width = "100%";
          svg.style.maxWidth = "100%";
          svg.style.height = "auto";
          svg.style.display = "block";
          svg.style.margin = "0 auto";
          svg.querySelectorAll("text").forEach((node) => {{
            node.style.fill = "#111827";
            node.style.fontWeight = "600";
          }});
        }}
        if (rendered.bindFunctions) {{
          rendered.bindFunctions(target);
        }}
      }} catch (err) {{
        try {{
          initMermaid({{
            htmlLabels: false,
            curve: "linear",
            padding: 18,
            useMaxWidth: true
          }});
          const renderedSafe = await mermaid.render("{container_id}_svg_safe", code);
          target.innerHTML = renderedSafe.svg;
          const svgSafe = target.querySelector("svg");
          if (svgSafe) {{
            svgSafe.style.width = "100%";
            svgSafe.style.maxWidth = "100%";
            svgSafe.style.height = "auto";
            svgSafe.style.display = "block";
            svgSafe.style.margin = "0 auto";
          }}
          if (renderedSafe.bindFunctions) {{
            renderedSafe.bindFunctions(target);
          }}
        }} catch (retryErr) {{
          errorTarget.style.display = "block";
          errorTarget.textContent = "Mermaid render error: " + err.message + "\\nRetry error: " + retryErr.message;
        }}
      }}
    </script>
    <style>
      #{container_id}_wrapper {{
        background: #ffffff;
        border: 1px solid #d4dbe5;
        border-radius: 8px;
        min-height: {height}px;
        overflow: auto;
        padding: 18px;
      }}
      #{container_id} svg {{
        width: 100% !important;
        max-width: 100% !important;
        height: auto;
      }}
      #{container_id}_error {{
        color: #991b1b;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        display: none;
        margin-top: 12px;
        padding: 12px;
        white-space: pre-wrap;
      }}
    </style>
    """
    components.html(html, height=height + 80, scrolling=True)


page_df = pd.DataFrame(STREAMLIT_PAGE_CATALOG)
workflow_rows = []
for rq, steps in RQ_WORKFLOWS.items():
    for idx, step in enumerate(steps, start=1):
        workflow_rows.append(
            {
                "rq": rq,
                "step_no": idx,
                "step": step["step"],
                "page": step["page"],
                "route": step["route"],
                "why": step["why"],
                "expected_output": step["expected_output"],
            }
        )
workflow_df = pd.DataFrame(workflow_rows)


tab_pages, tab_rq, tab_complete, tab_quick = st.tabs([
    "All Pages",
    "RQ Workflows",
    "Complete Workflow",
    "Quick Redirects",
])

with tab_pages:
    st.subheader("Every Streamlit Page and What It Does")
    st.write(
        "This table is the operating manual for the dashboard. Use it when you are unsure which page produces the evidence "
        "needed for a research question or thesis chapter."
    )
    st.dataframe(
        page_df[["page", "file", "route", "purpose", "use_when", "outputs", "supports"]],
        use_container_width=True,
        height=620,
    )

    selected_page = st.selectbox("Open one page description", page_df["page"].tolist())
    page = page_df[page_df["page"] == selected_page].iloc[0]
    st.markdown(f"### {page['page']}")
    st.markdown(f"**File:** `{page['file']}`")
    st.markdown(f"**Supports:** {page['supports']}")
    st.markdown(f"**Purpose:** {page['purpose']}")
    st.markdown(f"**Use when:** {page['use_when']}")
    st.markdown(f"**Expected outputs:** {page['outputs']}")
    st.link_button(f"Open {page['page']}", page["route"], use_container_width=True)

with tab_rq:
    st.subheader("Step-by-Step Workflow for Each RQ")
    selected_rq = st.selectbox("Choose research question", list(RQ_WORKFLOWS.keys()))
    steps = RQ_WORKFLOWS[selected_rq]

    st.dataframe(
        workflow_df[workflow_df["rq"] == selected_rq][["step_no", "step", "page", "why", "expected_output"]],
        use_container_width=True,
        height=360,
        hide_index=True,
    )

    st.markdown("### Action Buttons")
    for idx, step in enumerate(steps, start=1):
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"#### Step {idx}: {step['step']}")
                st.write(step["why"])
                st.caption(f"Expected output: {step['expected_output']}")
            with c2:
                st.link_button(step["page"], step["route"], use_container_width=True)

    st.markdown("### What To Do After Finishing This RQ")
    st.write(
        "After completing the workflow, return to `Research Questions Visualizer` to update the evidence status, then use "
        "`Chapter 4 Results`, `Chapter 5 Discussion`, and `Chapter 6 Conclusion` to turn the output into thesis writing."
    )
    page_link_grid(
        [
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
            ("Chapter 4 Results", "/Chapter_4_Results"),
            ("Chapter 5 Discussion", "/Chapter_5_Discussion"),
            ("Chapter 6 Conclusion", "/Chapter_6_Conclusion"),
        ],
        columns=4,
    )

with tab_complete:
    st.subheader("Complete Dashboard Workflow")
    st.write(
        "This diagram shows the whole dashboard logic. Each RQ starts from a different operational path, but all paths "
        "return to the RQ evidence page and then flow into Chapters 4, 5, and 6."
    )
    render_safe_mermaid(COMPLETE_WORKFLOW_MERMAID, height=760)
    st.code(COMPLETE_WORKFLOW_MERMAID, language="mermaid")

    st.subheader("Complete Workflow Table")
    st.dataframe(workflow_df, use_container_width=True, height=620)

with tab_quick:
    st.subheader("Quick Redirects by Task")
    redirect_groups = {
        "Start with existing parsed dataset": [
            ("Parsed ESG JSON", "/Parsed_ESG_JSON"),
            ("Parsed ESG Review", "/Parsed_ESG_Review"),
            ("Data File Visualizer", "/Data_File_Visualizer"),
        ],
        "Run and verify ClimateBERT": [
            ("ClimateBERT Dataset Processor", "/ClimateBERT_Dataset_Processor"),
            ("ClimateBERT Result Visualizer", "/ClimateBERT_Result_Visualizer"),
            ("Benchmark Model", "/Benchmark_Model"),
        ],
        "Analyze ESG categories": [
            ("Aspect", "/Aspect"),
            ("Tone Distribution", "/Tone_Distribution"),
            ("Data Distribution", "/Data_Distribution"),
            ("Sankey", "/Sankey"),
            ("Distribution Document", "/Distribution_Document"),
        ],
        "Validate sample size and stability": [
            ("Sample Size Reasoning", "/Sample_Size_Reasoning"),
            ("Metric Analysis", "/Metric_Analysis"),
            ("Benchmark Model", "/Benchmark_Model"),
        ],
        "Turn results into thesis chapters": [
            ("Research Questions Dashboard", "/Research_Questions_Dashboard"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
            ("Chapter 4 Results", "/Chapter_4_Results"),
            ("Chapter 5 Discussion", "/Chapter_5_Discussion"),
            ("Chapter 6 Conclusion", "/Chapter_6_Conclusion"),
        ],
    }

    for group, links in redirect_groups.items():
        st.markdown(f"### {group}")
        page_link_grid(links, columns=3)
