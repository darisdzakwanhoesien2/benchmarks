from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_4_SECTIONS,
    CHAPTER_5_SECTIONS,
    CHAPTER_6_SECTIONS,
    EXISTING_DATA_PATH,
    LABELED_COMPLETE_WORKFLOW_MERMAID,
    PREDICTION_OUTPUT_DIR,
    RQ_PAGE_MAP,
    RQ_WORKFLOWS,
    STREAMLIT_PAGE_CATALOG,
    build_filtered_workflow_mermaid,
    filter_workflow_graph,
    page_link_grid,
    parse_workflow_mermaid,
    render_mermaid,
)


st.set_page_config(page_title="Streamlit Page Workflow", layout="wide")
st.title("Streamlit Page Workflow")
st.caption("Navigation hub for every Streamlit page, every RQ workflow, and the thesis evidence trail.")

st.caption(f"Existing data: `{EXISTING_DATA_PATH}`")
st.caption(f"Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")


def page_catalog_df() -> pd.DataFrame:
    return pd.DataFrame(STREAMLIT_PAGE_CATALOG)


def workflow_df() -> pd.DataFrame:
    rows = []
    for rq, steps in RQ_WORKFLOWS.items():
        for idx, step in enumerate(steps, start=1):
            rows.append(
                {
                    "rq": rq,
                    "step": idx,
                    "action": step["step"],
                    "page": step["page"],
                    "why": step["why"],
                    "expected_output": step["expected_output"],
                }
            )
    return pd.DataFrame(rows)


overview, pages_tab, rq_tab, pipeline_tab, chapters_tab, docs_tab = st.tabs(
    ["Overview", "Every Page", "RQ Workflows", "Complete Workflow", "Chapter Usage", "Documentation"]
)

with overview:
    st.subheader("How to use this page")
    st.write(
        "Start here when you are deciding which dashboard page to open. The workflow tells you what each page does, "
        "which RQ it supports, and how evidence flows into Chapter 4, Chapter 5, and Chapter 6."
    )

    df = page_catalog_df()
    wf = workflow_df()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered pages", len(df))
    c2.metric("RQ workflows", len(RQ_WORKFLOWS))
    c3.metric("Workflow steps", len(wf))
    c4.metric("Thesis chapters", "4-6")

    st.subheader("Fast path")
    fast_path = pd.DataFrame(
        [
            {
                "task": "Start from existing parsed data",
                "start page": "Parsed ESG JSON",
                "then open": "Parsed ESG Review, Data File Visualizer, Research Questions Visualizer",
            },
            {
                "task": "Answer RQ1",
                "start page": "Parsed ESG JSON",
                "then open": "Parsed ESG Review, Data File Visualizer, Research Questions Visualizer",
            },
            {
                "task": "Answer RQ2",
                "start page": "Parsed ESG JSON",
                "then open": "Aspect, Tone Distribution, Sankey, Sample Size Reasoning",
            },
            {
                "task": "Answer RQ3",
                "start page": "ClimateBERT Dataset Processor",
                "then open": "ClimateBERT Result Visualizer, Benchmark Model, Research Questions Visualizer",
            },
            {
                "task": "Answer RQ4",
                "start page": "Parsed ESG Review",
                "then open": "Metric Analysis, Parsed ESG JSON, Research Questions Visualizer",
            },
            {
                "task": "Answer RQ5",
                "start page": "Research Questions Dashboard",
                "then open": "Research Questions Visualizer, Data File Visualizer, chapter pages",
            },
            {
                "task": "Answer RQ6",
                "start page": "Metric Analysis",
                "then open": "Parsed ESG JSON, Sample Size Reasoning, Benchmark Model",
            },
            {
                "task": "Write thesis chapters",
                "start page": "Chapter 4 Results",
                "then open": "Chapter 5 Discussion, Chapter 6 Conclusion",
            },
        ]
    )
    st.dataframe(fast_path, use_container_width=True, hide_index=True)

with pages_tab:
    st.subheader("Every Streamlit page and what it is for")
    df = page_catalog_df()
    st.dataframe(
        df[["page", "file", "purpose", "use_when", "outputs", "supports"]],
        use_container_width=True,
        height=560,
        hide_index=True,
    )

    st.subheader("Open a page")
    selected_page = st.selectbox("Choose page", df["page"].tolist())
    row = df[df["page"] == selected_page].iloc[0]
    c1, c2 = st.columns([1, 2])
    with c1:
        st.link_button(f"Open {row['page']}", row["route"], use_container_width=True)
        st.caption(f"`{row['file']}`")
        st.caption(f"Supports: {row['supports']}")
    with c2:
        st.markdown(f"**Purpose:** {row['purpose']}")
        st.markdown(f"**Use when:** {row['use_when']}")
        st.markdown(f"**Outputs:** {row['outputs']}")

with rq_tab:
    st.subheader("RQ-by-RQ workflow")
    selected_rq = st.radio("Choose an RQ", list(RQ_WORKFLOWS.keys()), horizontal=True)
    workflow = RQ_WORKFLOWS[selected_rq]
    rq_info = next((item for item in RQ_PAGE_MAP if item["rq"] == selected_rq), None)

    if rq_info:
        st.markdown(f"### {selected_rq}: {rq_info['question']}")
        st.info(f"Goal: {rq_info['chapter_4_use']}")
        st.caption(f"Chapter 5: {rq_info['chapter_5_use']}")
        st.caption(f"Chapter 6: {rq_info['chapter_6_use']}")

    for idx, step in enumerate(workflow, start=1):
        with st.container(border=True):
            cols = st.columns([0.5, 1.4, 4.2, 1.3])
            cols[0].metric("Step", idx)
            cols[1].markdown(f"**{step['page']}**")
            cols[2].markdown(f"**{step['step']}**")
            cols[2].write(step["why"])
            cols[2].caption(f"Expected output: {step['expected_output']}")
            cols[3].link_button("Open page", step["route"], use_container_width=True)

    st.subheader("Workflow table")
    st.dataframe(workflow_df()[workflow_df()["rq"] == selected_rq], use_container_width=True, hide_index=True)

with pipeline_tab:
    st.subheader("Complete workflow from source PDF to thesis conclusion")
    st.markdown(
        "Each Mermaid edge is labeled with the RQ(s) it supports. You can filter by a single RQ, such as "
        "`RQ1`, or by multiple RQs, such as `RQ1, RQ5`. Multi-RQ edge labels are treated as belonging to every RQ in the label."
    )

    workflow_nodes, workflow_edges = parse_workflow_mermaid(LABELED_COMPLETE_WORKFLOW_MERMAID)
    rq_options = [f"RQ{i}" for i in range(1, 7)]

    filter_col1, filter_col2, filter_col3 = st.columns([2, 1.4, 1.1])
    with filter_col1:
        selected_rqs = st.multiselect(
            "Filter workflow by RQ",
            rq_options,
            default=rq_options,
            help="Select one RQ for a focused graph, or multiple RQs for shared paths.",
        )
    with filter_col2:
        match_mode = st.radio(
            "Filter mode",
            ["Match any selected RQ", "Match all selected RQs"],
            horizontal=False,
        )
    with filter_col3:
        include_unlabeled = st.checkbox("Include unlabeled edges", value=False)

    display_col1, display_col2, display_col3 = st.columns([1.2, 1.1, 1.3])
    with display_col1:
        compact_labels = st.toggle("Compact node labels", value=True)
    with display_col2:
        direction_label = st.radio("Direction", ["Top-down", "Left-right"], horizontal=False)
        diagram_direction = "TD" if direction_label == "Top-down" else "LR"
    with display_col3:
        show_edge_table = st.toggle("Show visible edge table", value=True)

    filtered_nodes, filtered_edges = filter_workflow_graph(
        workflow_nodes,
        workflow_edges,
        selected_rqs,
        match_mode,
        include_unlabeled,
    )
    filtered_mermaid = build_filtered_workflow_mermaid(
        filtered_nodes,
        filtered_edges,
        direction=diagram_direction,
        compact_labels=compact_labels,
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Visible nodes", len(filtered_nodes))
    metric_col2.metric("Visible edges", len(filtered_edges))
    metric_col3.metric("Selected RQs", ", ".join(selected_rqs) if selected_rqs else "None")

    if filtered_mermaid:
        render_mermaid(filtered_mermaid, height=760)
    else:
        st.info("No workflow edges match the current RQ filter.")

    if show_edge_table:
        st.subheader("Visible workflow edges")
        edge_table = pd.DataFrame(
            [
                {
                    "source": workflow_nodes.get(str(edge["source_id"]), str(edge["source_id"])),
                    "edge label": edge.get("label", ""),
                    "RQs": ", ".join(edge.get("rqs", [])),
                    "target": workflow_nodes.get(str(edge["target_id"]), str(edge["target_id"])),
                }
                for edge in filtered_edges
            ]
        )
        st.dataframe(edge_table, use_container_width=True, hide_index=True)

    st.subheader("Filtered Mermaid source")
    st.code(filtered_mermaid or LABELED_COMPLETE_WORKFLOW_MERMAID, language="mermaid")

with chapters_tab:
    st.subheader("Chapter usage")
    c4, c5, c6 = st.tabs(["Chapter 4 Results", "Chapter 5 Discussion", "Chapter 6 Conclusion"])
    with c4:
        st.write("Use Chapter 4 to present what the dashboard produced and measured.")
        st.dataframe(pd.DataFrame(CHAPTER_4_SECTIONS), use_container_width=True, hide_index=True)
        page_link_grid([("Open Chapter 4 Results", "/Chapter_4_Results")], columns=1)
    with c5:
        st.write("Use Chapter 5 to interpret what the results mean and how limitations affect claims.")
        st.dataframe(pd.DataFrame(CHAPTER_5_SECTIONS), use_container_width=True, hide_index=True)
        page_link_grid([("Open Chapter 5 Discussion", "/Chapter_5_Discussion")], columns=1)
    with c6:
        st.write("Use Chapter 6 to close the research questions, contributions, limitations, and future work.")
        st.dataframe(pd.DataFrame(CHAPTER_6_SECTIONS), use_container_width=True, hide_index=True)
        page_link_grid([("Open Chapter 6 Conclusion", "/Chapter_6_Conclusion")], columns=1)

with docs_tab:
    st.subheader("Documentation and evidence trail")
    st.write(
        "Use this section as a checklist for thesis auditability. The project should preserve the source dataset, "
        "prediction CSV outputs, generated image artifacts, JSON explanations, Markdown report, and chapter pages."
    )
    st.markdown(f"- Existing data: `{EXISTING_DATA_PATH}`")
    st.markdown(f"- Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")
    st.markdown("- Generated artifacts: `research_question_artifacts/`")
    st.markdown("- RQ synthesis: `Research_Questions_Dashboard.py` and `04_Research_Questions_Visualizer.py`")

    st.subheader("Open documentation-related pages")
    page_link_grid(
        [
            ("Research Questions Dashboard", "/Research_Questions_Dashboard"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
            ("Data File Visualizer", "/Data_File_Visualizer"),
            ("Chapter 4 Results", "/Chapter_4_Results"),
            ("Chapter 5 Discussion", "/Chapter_5_Discussion"),
            ("Chapter 6 Conclusion", "/Chapter_6_Conclusion"),
        ],
        columns=3,
    )
