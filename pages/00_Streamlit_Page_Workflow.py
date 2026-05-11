from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

try:
    import _rq_thesis_content as rq_content

    CHAPTER_FLOW_MERMAID = getattr(
        rq_content,
        "CHAPTER_FLOW_MERMAID",
        """
flowchart LR
  RQ["Research Questions"] --> C4["Chapter 4 Results"]
  C4 --> C5["Chapter 5 Discussion"]
  C5 --> C6["Chapter 6 Conclusion"]
""".strip(),
    )
    render_mermaid = getattr(rq_content, "render_mermaid")
    mermaid_download_section = getattr(rq_content, "mermaid_download_section", None)

    def research_questions_df() -> pd.DataFrame:
        if hasattr(rq_content, "research_questions_df"):
            return rq_content.research_questions_df()
        if hasattr(rq_content, "RESEARCH_QUESTIONS"):
            return pd.DataFrame(rq_content.RESEARCH_QUESTIONS)
        if hasattr(rq_content, "RQ_PAGE_MAP"):
            rows = []
            for item in rq_content.RQ_PAGE_MAP:
                rows.append(
                    {
                        "rq": item.get("rq", ""),
                        "theme": item.get("theme", ""),
                        "question": item.get("question", ""),
                        "short_answer": item.get("chapter_6_use", item.get("needed_completion", "")),
                    }
                )
            return pd.DataFrame(rows)
        return pd.DataFrame()
except Exception:  # pragma: no cover - this page should still be useful if helper imports fail.
    CHAPTER_FLOW_MERMAID = """
flowchart LR
  RQ["Research Questions"] --> C4["Chapter 4 Results"]
  C4 --> C5["Chapter 5 Discussion"]
  C5 --> C6["Chapter 6 Conclusion"]
""".strip()

    def render_mermaid(code: str, height: int = 520) -> None:
        st.code(code, language="mermaid")

    mermaid_download_section = None

    def research_questions_df() -> pd.DataFrame:
        return pd.DataFrame()


st.set_page_config(page_title="Streamlit Page Workflow", layout="wide")
st.title("Streamlit Page Workflow")
st.caption("A navigation map for every Streamlit page, with RQ-specific workflows and direct page redirects.")


PAGE_DESCRIPTIONS = {
    "00_Streamlit_Page_Workflow.py": ("Workflow navigator", "RQ1-RQ6", "Start here. It explains all pages and gives RQ-by-RQ navigation steps."),
    "04_Research_Questions_Visualizer.py": ("Research question evidence dashboard", "RQ1-RQ6", "Use to inspect available, partial, and needed evidence, missing work, image outputs, discussions, and conclusions."),
    "05_Sample_Size_Reasoning.py": ("Sample-size and claim-readiness reasoning", "RQ2, RQ3, RQ6", "Use to decide what current n can support and what larger/balanced samples are required."),
    "06_Chapter_4_Results.py": ("Chapter 4 results builder", "RQ1-RQ6", "Use to convert dashboard outputs into thesis results sections."),
    "07_Chapter_5_Discussion.py": ("Chapter 5 discussion builder", "RQ1-RQ6", "Use to interpret results, discuss limitations, and word Available/Partial/Needed evidence carefully."),
    "10_Chapter_6_Conclusion.py": ("Chapter 6 conclusion builder", "RQ1-RQ6", "Use to write concise RQ answers, contributions, limitations, future work, and final conclusion."),
    "Research_Questions_Dashboard.py": ("RQ control dashboard", "RQ1-RQ6", "Use to see RQ status, supporting pages, image evidence, and thesis flow."),
    "esg_dashboard_new_0_new.py": ("Parsed ESG JSON dashboard", "RQ1, RQ2, RQ4, RQ5, RQ6", "Use for extracted records, source grounding, filters, model/prompt coverage, and provenance review."),
    "esg_dashboard_new_8_new.py": ("Alternative parsed ESG dashboard", "RQ1, RQ2, RQ4, RQ5, RQ6", "Use as an alternate parsed-data view when dataset.json/data_output paths differ."),
    "esg_dashboard_new_Data Distribution.py": ("ESG data distribution dashboard", "RQ2, RQ4, RQ5", "Use for aspect, ontology, sentiment, tone, feature, and heatmap distributions."),
    "esg_dashboard_new_Data_New_Distribution.py": ("ESG distribution and rule explorer", "RQ2, RQ4, RQ6", "Use for Sankey, waterfall filtering, and multi-rule ESG label exploration."),
    "esg_dashboard_new_Distribution Document.py": ("Document-level distribution dashboard", "RQ2, RQ4, RQ6", "Use for document-level sentiment, tone, and correlation patterns."),
    "esg_dashboard_new_Tone_Distribution.py": ("Tone distribution dashboard", "RQ2, RQ6", "Use for tone imbalance, tone balancing, and prompt/model tone behavior."),
    "esg_dashboard_new_Sankey.py": ("Sankey flow dashboard", "RQ2, RQ6", "Use for aspect-to-sentiment-to-tone flow interpretation and balancing."),
    "esg_dashboard_new_01_Aspects_Raw.py": ("Raw aspect explorer", "RQ2, RQ4", "Use to inspect uncontrolled aspect vocabulary before clustering or ontology cleanup."),
    "esg_dashboard_new_02_Aspects_Clustered.py": ("Clustered aspect explorer", "RQ2, RQ4", "Use to inspect normalized aspect clusters and unmapped aspect labels."),
    "esg_dashboard_new_03_Aspect_Comparison.py": ("Aspect mapping comparison", "RQ2, RQ4", "Use to compare before/after aspect normalization."),
    "zz_aspect_clusters.py": ("Aspect cluster explorer", "RQ2, RQ4", "Use for top cluster members, taxonomy coverage, and ontology-gap review."),
    "absa_metrics_visualization.py": ("ABSA metrics visualization", "RQ2, RQ3, RQ4, RQ6", "Use for saved metrics, zero/non-zero model results, confusion matrices, and local ClimateBERT comparison outputs."),
    "absa_metrics_comparison.py": ("ABSA ground-truth comparison", "RQ2, RQ3, RQ4, RQ6", "Use for category, sentiment, and tone precision/recall/F1 against mapped ground truth."),
    "absa_metrics_comparison_mac.py": ("ABSA ground-truth comparison, Mac/root paths", "RQ2, RQ3, RQ4, RQ6", "Use when benchmark-root paths are required."),
    "absa_metrics_comparison copy.py": ("Older ABSA metric comparison", "RQ2, RQ4", "Use only as a backup/legacy comparison page."),
    "esg_dashboard_new_0_Metric_Analysis.py": ("Upload metric-analysis page", "RQ2, RQ4, RQ6", "Use for aligned sentence metrics, errors, confidence, and metric diagnostics."),
    "test_models.py": ("Model tester", "RQ2, RQ4, RQ6", "Use to compare rule, classical, deep, and hybrid prototypes when outputs are saved."),
    "0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py": ("ClimateBERT batch ground-truth processor", "RQ3, RQ5", "Use to run local ClimateBERT predictions on ground-truth data."),
    "0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py": ("ClimateBERT batch processor, Windows paths", "RQ3, RQ5", "Use as path-specific alternative for ClimateBERT batch inference."),
    "0_0_ClimateBERT_4_Model_Analysis.py": ("ClimateBERT model analysis", "RQ3, RQ4, RQ6", "Use for model accuracy, coverage, confidence, and error diagnostics."),
    "0_0_ClimateBERT_5_Model_Deep_Explorer.py": ("ClimateBERT deep explorer", "RQ3, RQ4", "Use for per-model label distributions, confidence, confusion matrix, and prediction inspection."),
    "0_0_ClimateBERT_6_Model_Overview_All.py": ("ClimateBERT all-model overview", "RQ3, RQ6", "Use for cross-model overview, leaderboard, and stability checks."),
    "0_0_ClimateBERT_7_Full_Model_Visualization.py": ("Full ClimateBERT visualization", "RQ3, RQ5, RQ6", "Use for dataset info, leaderboard, confusion matrix, exports, and coverage diagnostics."),
    "0_ClimateBERT_Commitment_Distribution.py": ("Climate commitment distribution", "RQ3, RQ6", "Use for climate-commitment labels, confidence, and true-vs-predicted comparisons."),
    "1_ABSA_Integration.py": ("ABSA and ClimateBERT integration", "RQ2, RQ3", "Use to connect ABSA majority labels with ClimateBERT parsed outputs."),
    "ABSA_Model_Comparison.py": ("Interactive ABSA model comparison", "RQ2, RQ6", "Use for qualitative comparison across rule-based, classical, deep, and hybrid modules."),
    "2_ABSA_Rule_Based.py": ("Rule-based ABSA demo", "RQ2, RQ4", "Use for explainable ontology/rule diagnostics."),
    "3_ABSA_Classical.py": ("Classical ML ABSA demo", "RQ2, RQ6", "Use for classical predictions, coefficients, and qualitative model behavior."),
    "5_ABSA_Deep_Learning.py": ("Deep-learning ABSA demo", "RQ2, RQ6", "Use for deep ABSA predictions and token/model inspection."),
    "absa_ontology_3_deep_model.py": ("mBERT/deep model ontology demo", "RQ2, RQ6", "Use as a small deep-model ABSA prototype."),
    "absa_ontology_all.py": ("ABSA ontology module demos", "RQ2, RQ4, RQ6", "Use for rule, classical, deep, hybrid, and explainability prototypes."),
    "absa_ontology_all_new_notes.py": ("ABSA ontology demos with notes", "RQ2, RQ4, RQ5, RQ6", "Use when note persistence/explainability documentation matters."),
    "0_0_1_Single_Prediction.py": ("Single prediction demo", "RQ5, RQ6", "Use for manual sanity checks, not final empirical evidence unless outputs are saved."),
    "0_0_1_multiple_Prediction.py": ("Multiple prediction demo", "RQ5, RQ6", "Use for qualitative multi-model comparisons when outputs are retained."),
    "0_0_2_Batch_Prediction.py": ("Batch prediction page", "RQ5, RQ6", "Use to generate batch prediction artifacts from uploads."),
    "0_0_3_Model_Explorer.py": ("Model explorer", "Utility", "Use to inspect available model metadata."),
    "esg_dashboard_new_Benchmark_Model.py": ("ESG/climate benchmark model tester", "RQ3, RQ6", "Use for interactive ESG and climate model testing."),
    "1_Analyze.py": ("Interactive ESG analyzer", "Utility", "Use for manual one-off text analysis."),
    "scrambled_absa_mapping_baseline.py": ("Scrambled baseline", "RQ4, RQ6", "Use as a negative-control baseline."),
    "scrambled_absa_mapping_baseline_mac.py": ("Scrambled baseline, Mac/root paths", "RQ4, RQ6", "Use as path-specific negative-control baseline."),
    "parse_documentation_json.py": ("Documentation JSON viewer", "RQ5 / Utility", "Use to inspect parsed documentation JSON."),
    "_page_explanations.py": ("Page explanation helper", "Utility", "Shared metadata helper, not a dashboard result page."),
    "_shared/page_explanations.py": ("Shared page explanation helper", "Utility", "Shared helper module, not a dashboard result page."),
    "_rq_thesis_content.py": ("Shared RQ thesis content", "Utility", "Shared helper for RQ/chapter pages, not an end-user analysis page."),
    "0_0_0_1.py": ("Placeholder", "Utility", "No substantive analysis."),
    "0_0_0_code.py": ("Placeholder", "Utility", "No substantive analysis."),
}


RQ_WORKFLOWS = [
    {
        "rq": "RQ1",
        "goal": "Prove the PDF/report-to-structured ESG pipeline is usable and auditable.",
        "steps": [
            ("Inspect parsed records and filters", "esg_dashboard_new_0_new.py", "Check document/page/model/prompt coverage, extracted fields, and source grounding."),
            ("Cross-check alternate parsed-data view", "esg_dashboard_new_8_new.py", "Use this if the dataset artifact differs from data_output.csv/txt."),
            ("Review evidence gaps", "04_Research_Questions_Visualizer.py", "Confirm OCR, sentence segmentation, and table/figure extraction gaps."),
            ("Write result", "06_Chapter_4_Results.py", "Use the RQ1 section for Chapter 4 pipeline evidence."),
            ("Discuss limitation", "07_Chapter_5_Discussion.py", "Word this as feasibility unless CER/WER and segmentation metrics are added."),
        ],
    },
    {
        "rq": "RQ2",
        "goal": "Describe and validate ESG aspect, pillar, sentiment, and tone categorization.",
        "steps": [
            ("Inspect distributions", "esg_dashboard_new_Data Distribution.py", "Review aspect, ontology, sentiment, tone, and heatmap distributions."),
            ("Trace flows", "esg_dashboard_new_Sankey.py", "Use aspect/sentiment/tone flows to explain category structure."),
            ("Review aspect normalization", "esg_dashboard_new_03_Aspect_Comparison.py", "Compare raw vs clustered aspects and identify ontology gaps."),
            ("Check metrics", "absa_metrics_visualization.py", "Use metrics only where label spaces and gold labels are aligned."),
            ("Check sample readiness", "05_Sample_Size_Reasoning.py", "Confirm whether subgroup/sample claims are defensible."),
        ],
    },
    {
        "rq": "RQ3",
        "goal": "Compare tone-based ABSA outputs with ClimateBERT-style classifications.",
        "steps": [
            ("Run or inspect batch predictions", "0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py", "Generate local ClimateBERT predictions for valid rows."),
            ("Analyze model coverage", "0_0_ClimateBERT_4_Model_Analysis.py", "Check coverage, confidence, errors, and exports."),
            ("Compare all models", "0_0_ClimateBERT_7_Full_Model_Visualization.py", "Review leaderboards, confusion matrices, and dataset-level visualizations."),
            ("Integrate with ABSA", "1_ABSA_Integration.py", "Join ClimateBERT outputs with ABSA majority category/sentiment/tone fields."),
            ("Visualize metrics", "absa_metrics_visualization.py", "Interpret zero/low scores as label-space or coverage diagnostics until mappings are final."),
        ],
    },
    {
        "rq": "RQ4",
        "goal": "Detect and quantify weaknesses in extraction and ABSA outputs.",
        "steps": [
            ("Start with parsed records", "esg_dashboard_new_0_new.py", "Find missing or inconsistent fields by document, model, prompt, and page."),
            ("Inspect metric errors", "absa_metrics_comparison.py", "Review confusion matrices, TP/FP/FN, and class-level metric failures."),
            ("Inspect taxonomy gaps", "zz_aspect_clusters.py", "Find unclustered or non-standard aspect labels."),
            ("Use upload/aligned metric analysis", "esg_dashboard_new_0_Metric_Analysis.py", "Review aligned sentences, confidence, and error tables."),
            ("Write diagnostics discussion", "07_Chapter_5_Discussion.py", "Separate schema drift, ontology mismatch, missing labels, class imbalance, and evaluation mismatch."),
        ],
    },
    {
        "rq": "RQ5",
        "goal": "Make the workflow reproducible, auditable, and thesis-ready.",
        "steps": [
            ("Open RQ dashboard", "Research_Questions_Dashboard.py", "Check RQ status, image evidence, and thesis flow."),
            ("Open image/RQ visualizer", "04_Research_Questions_Visualizer.py", "Review archived image explanations, discussions, and conclusions."),
            ("Review this workflow navigator", "00_Streamlit_Page_Workflow.py", "Use it as the map of all available Streamlit pages."),
            ("Write Chapter 4 artifacts section", "06_Chapter_4_Results.py", "Describe saved images, JSON/Markdown artifacts, and traceable sources."),
            ("Export conclusion draft", "10_Chapter_6_Conclusion.py", "Use the Markdown draft as the final thesis closure scaffold."),
        ],
    },
    {
        "rq": "RQ6",
        "goal": "Assess stability across models/prompts and plan ensemble or verification strategies.",
        "steps": [
            ("Inspect tone behavior", "esg_dashboard_new_Tone_Distribution.py", "Review tone imbalance and tone behavior by subgroup."),
            ("Compare models qualitatively", "ABSA_Model_Comparison.py", "Compare rule/classical/deep/hybrid behavior."),
            ("Review ClimateBERT model spread", "0_0_ClimateBERT_6_Model_Overview_All.py", "Compare cross-model prediction distributions and leaderboard patterns."),
            ("Check sample balance", "05_Sample_Size_Reasoning.py", "Confirm matched model x prompt x document requirements."),
            ("Discuss stability cautiously", "07_Chapter_5_Discussion.py", "Avoid strong stability claims until matched coverage exists."),
        ],
    },
]


def available_pages() -> list[str]:
    return sorted(path.name for path in PAGE_DIR.glob("*.py"))


def page_route(file_name: str) -> str:
    return f"pages/{file_name}"


def page_exists(file_name: str) -> bool:
    return (PAGE_DIR / file_name).exists()


def render_page_button(file_name: str, label: str | None = None) -> None:
    label = label or file_name
    if page_exists(file_name):
        try:
            st.page_link(page_route(file_name), label=label, use_container_width=True)
        except Exception:
            st.code(file_name)
    else:
        st.button(f"{label} (missing)", disabled=True, use_container_width=True)


def page_catalog_df() -> pd.DataFrame:
    rows = []
    for file_name in available_pages():
        title, rq_links, description = PAGE_DESCRIPTIONS.get(
            file_name,
            ("Uncatalogued Streamlit page", "Unmapped", "This page exists in the folder but has not been manually classified yet."),
        )
        rows.append(
            {
                "file": file_name,
                "title": title,
                "rq_links": rq_links,
                "description": description,
                "route": page_route(file_name),
            }
        )
    return pd.DataFrame(rows)


def workflow_rows_df() -> pd.DataFrame:
    rows = []
    for workflow in RQ_WORKFLOWS:
        for idx, (action, page, detail) in enumerate(workflow["steps"], start=1):
            rows.append(
                {
                    "rq": workflow["rq"],
                    "step": idx,
                    "action": action,
                    "page": page,
                    "detail": detail,
                    "exists": page_exists(page),
                }
            )
    return pd.DataFrame(rows)


catalog = page_catalog_df()
workflow_df = workflow_rows_df()
rq_df = research_questions_df()

metrics = st.columns(5)
metrics[0].metric("Streamlit pages", len(catalog))
metrics[1].metric("Mapped pages", int((catalog["rq_links"] != "Unmapped").sum()))
metrics[2].metric("RQ workflows", len(RQ_WORKFLOWS))
metrics[3].metric("Workflow steps", len(workflow_df))
metrics[4].metric("Missing workflow pages", int((~workflow_df["exists"]).sum()))

tab_workflow, tab_catalog, tab_rq, tab_types, tab_diagram = st.tabs(
    ["RQ Workflow", "All Pages", "RQ Details", "Analysis Types", "Diagram"]
)

with tab_workflow:
    st.subheader("Complete RQ Workflow")
    selected_rq = st.selectbox("Select research question", [item["rq"] for item in RQ_WORKFLOWS])
    workflow = next(item for item in RQ_WORKFLOWS if item["rq"] == selected_rq)

    st.info(workflow["goal"])
    if not rq_df.empty and selected_rq in rq_df["rq"].tolist():
        rq_row = rq_df.loc[rq_df["rq"] == selected_rq].iloc[0]
        st.markdown(f"**Research question:** {rq_row.get('question', '')}")
        st.markdown(f"**Current answer:** {rq_row.get('short_answer', '')}")

    for step_number, (action, page, detail) in enumerate(workflow["steps"], start=1):
        left, right = st.columns([0.68, 0.32])
        with left:
            st.markdown(f"**Step {step_number}: {action}**")
            st.write(detail)
            title, _, page_description = PAGE_DESCRIPTIONS.get(page, (page, "", ""))
            st.caption(f"{title}: {page_description}")
        with right:
            render_page_button(page, f"Open {page}")

    st.subheader("Workflow Table")
    st.dataframe(workflow_df.loc[workflow_df["rq"] == selected_rq], use_container_width=True, hide_index=True)

with tab_catalog:
    st.subheader("Every Streamlit Page")
    rq_filter = st.multiselect(
        "Filter by RQ or role",
        sorted({value.strip() for links in catalog["rq_links"] for value in str(links).split(",")}),
    )
    filtered = catalog.copy()
    if rq_filter:
        filtered = filtered[
            filtered["rq_links"].apply(lambda value: any(item in str(value) for item in rq_filter))
        ]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    selected_page = st.selectbox("Open page description", filtered["file"].tolist() if not filtered.empty else catalog["file"].tolist())
    page_row = catalog.loc[catalog["file"] == selected_page].iloc[0]
    st.markdown(f"**{page_row['title']}**")
    st.write(page_row["description"])
    st.caption(f"RQ links: {page_row['rq_links']}")
    render_page_button(selected_page, f"Open {selected_page}")

with tab_rq:
    st.subheader("RQ-to-Page Matrix")
    st.dataframe(workflow_df, use_container_width=True, hide_index=True)

    st.subheader("Direct RQ Redirects")
    for workflow in RQ_WORKFLOWS:
        with st.expander(f"{workflow['rq']} - {workflow['goal']}"):
            cols = st.columns(2)
            for idx, (action, page, detail) in enumerate(workflow["steps"]):
                with cols[idx % 2]:
                    st.markdown(f"**{action}**")
                    st.caption(detail)
                    render_page_button(page, page)

with tab_types:
    st.subheader("Pages by Analysis Type")
    type_rules = {
        "Thesis/RQ and chapter pages": ["Research_Questions", "Chapter", "Workflow", "04_", "05_"],
        "Parsed ESG and distribution pages": ["esg_dashboard_new"],
        "ABSA metrics and comparison pages": ["absa_metrics", "Metric_Analysis", "test_models"],
        "ClimateBERT pages": ["ClimateBERT", "ABSA_Integration"],
        "ABSA model demo pages": ["ABSA_", "absa_ontology", "Rule_Based", "Classical", "Deep_Learning"],
        "Utilities, baselines, and helpers": ["scrambled", "parse_", "_page", "_shared", "_rq", "0_0_0", "Analyze"],
    }
    for group, markers in type_rules.items():
        group_df = catalog[catalog["file"].apply(lambda value: any(marker in value for marker in markers))]
        with st.expander(f"{group} ({len(group_df)})", expanded=group.startswith("Thesis")):
            st.dataframe(group_df, use_container_width=True, hide_index=True)

with tab_diagram:
    st.subheader("Thesis Workflow Diagram")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=460)
    st.subheader("Download and Edit Mermaid")
    if mermaid_download_section:
        mermaid_download_section(CHAPTER_FLOW_MERMAID, "thesis_workflow")
    else:
        st.download_button(
            "Download Mermaid source",
            data=CHAPTER_FLOW_MERMAID,
            file_name="thesis_workflow.mmd",
            mime="text/plain",
            use_container_width=True,
        )
        st.link_button("Open Mermaid Live Editor", "https://mermaid.ai/live/edit", use_container_width=True)
    st.caption("Open the live editor, then paste the downloaded Mermaid source if the editor does not prefill automatically.")
