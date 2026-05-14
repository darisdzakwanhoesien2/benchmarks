from __future__ import annotations

from pathlib import Path
import re

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Streamlit Page Workflow", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "pages"
DOCS_DIR = ROOT / "documentation" / "streamlit_pages"


def render_mermaid(source: str, height: int = 720):
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


def page_link(page_file: str, label: str | None = None):
    label = label or page_file
    candidates = [f"pages/{page_file}", page_file, str(PAGES_DIR / page_file)]
    for candidate in candidates:
        try:
            st.page_link(candidate, label=label)
            return
        except Exception:
            continue
    st.code(page_file, language=None)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def mermaid_label(value: str) -> str:
    return str(value or "").replace('"', '\\"')


def parse_edge_rqs(label: str) -> list[str]:
    return sorted(set(re.findall(r"RQ[1-6]", label or "")))


def parse_workflow_mermaid(mermaid_text: str) -> tuple[dict[str, str], list[dict[str, object]]]:
    nodes: dict[str, str] = {}
    edges: list[dict[str, object]] = []
    node_pattern = re.compile(r'^(?P<node_id>\S+)\s*\["(?P<label>.*)"\]\s*$')
    labeled_edge_pattern = re.compile(
        r'^(?P<source>\S+)\s*--\s*"(?P<label>.*?)"\s*-->\s*(?P<target>\S+)\s*$'
    )
    plain_edge_pattern = re.compile(r"^(?P<source>\S+)\s*-->\s*(?P<target>\S+)\s*$")

    for raw_line in (mermaid_text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("flowchart") or line.startswith("subgraph ") or line == "end":
            continue

        node_match = node_pattern.match(line)
        if node_match:
            nodes[node_match.group("node_id")] = clean_text(node_match.group("label")).replace("\\n", " | ")
            continue

        labeled_edge_match = labeled_edge_pattern.match(line)
        if labeled_edge_match:
            label = clean_text(labeled_edge_match.group("label"))
            edges.append(
                {
                    "source_id": labeled_edge_match.group("source"),
                    "target_id": labeled_edge_match.group("target"),
                    "label": label,
                    "rqs": parse_edge_rqs(label),
                }
            )
            continue

        plain_edge_match = plain_edge_pattern.match(line)
        if plain_edge_match:
            edges.append(
                {
                    "source_id": plain_edge_match.group("source"),
                    "target_id": plain_edge_match.group("target"),
                    "label": "",
                    "rqs": [],
                }
            )

    return nodes, edges


def filter_workflow_graph(
    nodes: dict[str, str],
    edges: list[dict[str, object]],
    selected_rqs: list[str],
    match_mode: str,
    include_unlabeled_edges: bool,
) -> tuple[dict[str, str], list[dict[str, object]]]:
    selected_set = set(selected_rqs)
    filtered_edges: list[dict[str, object]] = []

    for edge in edges:
        edge_rqs = set(edge.get("rqs", []))
        if not selected_set:
            keep = True
        elif match_mode == "Match all selected RQs":
            keep = selected_set.issubset(edge_rqs)
        else:
            keep = bool(selected_set & edge_rqs)

        if not edge_rqs and include_unlabeled_edges:
            keep = True

        if keep:
            filtered_edges.append(edge)

    visible_node_ids: list[str] = []
    for edge in filtered_edges:
        for key in ("source_id", "target_id"):
            node_id = str(edge[key])
            if node_id not in visible_node_ids:
                visible_node_ids.append(node_id)

    return {node_id: nodes[node_id] for node_id in visible_node_ids if node_id in nodes}, filtered_edges


def compact_node_label(label: str) -> str:
    parts = [part.strip() for part in str(label or "").split("|")]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}\\n{parts[1]}"


def build_filtered_workflow_mermaid(
    nodes: dict[str, str],
    edges: list[dict[str, object]],
    direction: str = "TD",
    compact_labels: bool = True,
) -> str:
    if not nodes or not edges:
        return ""

    lines = [f"flowchart {direction}"]
    for node_id, label in nodes.items():
        display_label = compact_node_label(label) if compact_labels else label
        lines.append(f'  {node_id}["{mermaid_label(display_label)}"]')

    for edge in edges:
        label = str(edge.get("label", ""))
        if label:
            lines.append(
                f'  {edge["source_id"]} -- "{mermaid_label(label)}" --> {edge["target_id"]}'
            )
        else:
            lines.append(f'  {edge["source_id"]} --> {edge["target_id"]}')

    return "\n".join(lines)


WORKFLOW_STAGE_ORDER = [
    "Input and Extraction",
    "Analysis and Validation",
    "Synthesis and Thesis Writing",
]


def workflow_stage_for_node(node_id: str) -> str:
    if node_id.startswith("node_I_"):
        return "Input and Extraction"
    if node_id.startswith("node_II_"):
        return "Analysis and Validation"
    if node_id.startswith("node_V_"):
        return "Synthesis and Thesis Writing"
    return "Other"


def build_workflow_funnel_df(
    nodes: dict[str, str],
    edges: list[dict[str, object]],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for step, stage in enumerate(WORKFLOW_STAGE_ORDER, start=1):
        stage_node_ids = [
            node_id for node_id in nodes if workflow_stage_for_node(node_id) == stage
        ]
        stage_edges = [
            edge
            for edge in edges
            if workflow_stage_for_node(str(edge["source_id"])) == stage
            or workflow_stage_for_node(str(edge["target_id"])) == stage
        ]
        page_labels = [
            compact_node_label(nodes[node_id]).replace("\\n", " | ")
            for node_id in stage_node_ids
        ]
        rows.append(
            {
                "step": step,
                "stage": stage,
                "visible pages": len(stage_node_ids),
                "visible edges touching stage": len(stage_edges),
                "pages": ", ".join(page_labels),
            }
        )
    return pd.DataFrame(rows)


def render_workflow_funnel(funnel_df: pd.DataFrame):
    if funnel_df.empty or int(funnel_df["visible pages"].sum()) == 0:
        st.info("No funnel stages are visible for the current RQ filter.")
        return

    chart_df = funnel_df.copy()
    max_visible = max(int(chart_df["visible pages"].max()), 1)
    chart_df["bar_start"] = (max_visible - chart_df["visible pages"]) / 2
    chart_df["bar_end"] = chart_df["bar_start"] + chart_df["visible pages"]
    chart_df["bar_mid"] = chart_df["bar_start"] + (chart_df["visible pages"] / 2)
    chart_df["stage label"] = chart_df.apply(
        lambda row: f"{row['step']}. {row['stage']} ({row['visible pages']} pages)",
        axis=1,
    )

    base = alt.Chart(chart_df).encode(
        y=alt.Y(
            "stage:N",
            sort=WORKFLOW_STAGE_ORDER,
            title=None,
            axis=alt.Axis(labelFontSize=13, labelLimit=260),
        )
    )
    bars = base.mark_bar(height=46, cornerRadius=7).encode(
        x=alt.X("bar_start:Q", axis=None, title=None),
        x2=alt.X2("bar_end:Q"),
        color=alt.Color(
            "stage:N",
            legend=None,
            scale=alt.Scale(range=["#2563eb", "#0f766e", "#b45309"]),
        ),
        tooltip=[
            alt.Tooltip("stage:N", title="Stage"),
            alt.Tooltip("visible pages:Q", title="Visible pages"),
            alt.Tooltip(
                "visible edges touching stage:Q",
                title="Visible edges touching stage",
            ),
            alt.Tooltip("pages:N", title="Pages"),
        ],
    )
    labels = base.mark_text(
        color="white",
        fontWeight="bold",
        fontSize=13,
        limit=520,
    ).encode(
        x=alt.X("bar_mid:Q", axis=None, title=None),
        text=alt.Text("stage label:N"),
    )
    st.altair_chart((bars + labels).properties(height=230), use_container_width=True)


PAGE_REGISTRY = [
    {
        "page": "Bulk_OCR.py",
        "label": "Bulk OCR",
        "stage": "Data ingestion",
        "primary RQs": "RQ1, RQ5",
        "purpose": "Upload or select sustainability reports and convert them into OCR markdown, page artifacts, images, and source JSON.",
        "use when": "You need source text, OCR outputs, provenance, or evidence that report PDFs were converted into usable text.",
        "outputs": "data/thesis_dataset/*, OCR markdown, OCR JSON, extracted page images.",
    },
    {
        "page": "0_3_OCR_Company_Metadata_Labeler.py",
        "label": "OCR Company Metadata Labeler",
        "stage": "Metadata labeling",
        "primary RQs": "RQ1, RQ5",
        "purpose": "Assign company names and sector/subsector/industry/subindustry metadata to OCR document folders.",
        "use when": "You need document-to-company provenance before extraction, visualization, or company-level analysis.",
        "outputs": "data/ocr_company_metadata.json.",
    },
    {
        "page": "llm_processing.py",
        "label": "LLM Processing",
        "stage": "Extraction",
        "primary RQs": "RQ1, RQ2, RQ6",
        "purpose": "Run prompt/model extraction over OCR text to produce ESG ABSA records.",
        "use when": "You need to generate or expand records, rebalance prompts, rerun social-pillar pages, or add matched model runs.",
        "outputs": "results/esg_records.json, run metadata, raw outputs.",
    },
    {
        "page": "ground_truth.py",
        "label": "Ground Truth",
        "stage": "Annotation",
        "primary RQs": "RQ2, RQ4",
        "purpose": "Manage or create human-labeled ground-truth data for validation.",
        "use when": "You need expert labels, annotation samples, or data for precision/recall/F1.",
        "outputs": "results/ground_truth.json, results/absa_results_ground_truth.json.",
    },
    {
        "page": "0_9_Tone_ClimateBERT_Visualization.py",
        "label": "Tone + ClimateBERT Visualization",
        "stage": "Results",
        "primary RQs": "RQ2, RQ3, RQ5",
        "purpose": "Visualize tone distribution, ESG-by-tone, aspect-by-tone, and ClimateBERT-style label alignment.",
        "use when": "You are writing Chapter 4 descriptive results or explaining ABSA/ClimateBERT relationships.",
        "outputs": "results/visualizations/*.png and crosstab CSVs.",
    },
    {
        "page": "1_0_Revision_Analytics.py",
        "label": "Revision Analytics",
        "stage": "Results and diagnostics",
        "primary RQs": "RQ2, RQ3, RQ4, RQ6",
        "purpose": "Summarize revision evidence: tone distributions, proxy agreement, greenwashing, prompt stability, and failure modes.",
        "use when": "You need thesis-ready analytics for Chapter 4 and Chapter 5.",
        "outputs": "results/revision_analysis/*.csv.",
    },
    {
        "page": "1_1_Ground_Truth_Workbench.py",
        "label": "Ground Truth Workbench",
        "stage": "Annotation",
        "primary RQs": "RQ2, RQ4",
        "purpose": "Review and annotate sampled records for tone, ESG pillar, aspect, and sentiment.",
        "use when": "You need to create the expert labels required for final metrics.",
        "outputs": "Pilot labels and saved annotation outputs.",
    },
    {
        "page": "1_2_OCR_Quality_Workbench.py",
        "label": "OCR Quality Workbench",
        "stage": "Validation",
        "primary RQs": "RQ1, RQ4",
        "purpose": "Compute CER/WER from manually corrected OCR reference snippets.",
        "use when": "You need to close the OCR-quality limitation in methodology and results.",
        "outputs": "results/revision_analysis/ocr_quality_samples.csv.",
    },
    {
        "page": "1_3_Ground_Truth_Metrics.py",
        "label": "Ground Truth Metrics",
        "stage": "Validation",
        "primary RQs": "RQ2, RQ4",
        "purpose": "Compute agreement and quality metrics from human labels and model predictions.",
        "use when": "You need Cohen's kappa, precision, recall, F1, or disagreement tables.",
        "outputs": "Metric tables and disagreement views.",
    },
    {
        "page": "1_4_ClimateBERT_Record_Batch.py",
        "label": "ClimateBERT Record Batch",
        "stage": "External validation",
        "primary RQs": "RQ3, RQ4",
        "purpose": "Prepare record-level inputs for real ClimateBERT validation and import batch outputs.",
        "use when": "You need to turn proxy ClimateBERT evidence into actual model-output evidence.",
        "outputs": "ClimateBERT input/output CSVs and merged validation data.",
    },
    {
        "page": "1_5_ESG_Flow_Sankey.py",
        "label": "ESG Flow Sankey",
        "stage": "Results",
        "primary RQs": "RQ2, RQ5",
        "purpose": "Visualize the flow from source/company to ESG pillar, aspect, tone, and sentiment.",
        "use when": "You need a thesis or defense figure showing the whole ABSA pipeline result structure.",
        "outputs": "Interactive Sankey view.",
    },
    {
        "page": "1_6_Ontology_Path_Viewer.py",
        "label": "Ontology Path Viewer",
        "stage": "Taxonomy",
        "primary RQs": "RQ2, RQ4, RQ5",
        "purpose": "Inspect aspect normalization, ontology coverage, and ESG category paths.",
        "use when": "You need to explain taxonomy design or diagnose non-standard aspect labels.",
        "outputs": "Ontology coverage views and aspect path evidence.",
    },
    {
        "page": "1_7_Research_Questions_Dashboard.py",
        "label": "Research Questions Dashboard",
        "stage": "Synthesis",
        "primary RQs": "RQ1-RQ6",
        "purpose": "Synthesize RQ evidence, sample-size reasoning, benchmarks, chapter plans, and thesis conclusions.",
        "use when": "You need the master evidence map for Chapter 4, 5, 6, or defense preparation.",
        "outputs": "RQ map, sample-size ladder, chapter 4-6 Mermaid flow, evidence matrix.",
    },
    {
        "page": "1_8_Ground_Truth_Output_Visualizer.py",
        "label": "Ground Truth Output Visualizer",
        "stage": "Validation",
        "primary RQs": "RQ2, RQ4",
        "purpose": "Inspect ground-truth seed records, review coverage, disagreement, and records needing human review.",
        "use when": "You need to explain current validation coverage and what still needs annotation.",
        "outputs": "Annotation coverage tables and review-priority views.",
    },
    {
        "page": "1_9_Ground_Truth_Pipeline_Output_Visualizer.py",
        "label": "Ground Truth Pipeline Output Visualizer",
        "stage": "Pipeline evidence",
        "primary RQs": "RQ1, RQ2, RQ4",
        "purpose": "Inspect the pipeline output that feeds ground truth and validation work.",
        "use when": "You need record-level traceability between extraction, labels, and validation.",
        "outputs": "Pipeline output tables and record inspection views.",
    },
    {
        "page": "2_0_LLM_Processing_Result_Visualizer.py",
        "label": "LLM Processing Result Visualizer",
        "stage": "Extraction audit",
        "primary RQs": "RQ1, RQ2, RQ6",
        "purpose": "Inspect T1/T2/T3 LLM outputs, parsed records, model/prompt metadata, and extraction runs.",
        "use when": "You need to audit what the LLM pipeline produced before downstream analysis.",
        "outputs": "Run summaries, record tables, prediction/ABSA/ESG output views.",
    },
    {
        "page": "2_2_LLM_Statement_Page_Verifier.py",
        "label": "LLM Statement Page Verifier",
        "stage": "Source verification",
        "primary RQs": "RQ1, RQ4, RQ5, RQ6",
        "purpose": "Map extracted LLM ESG statements back to OCR markdown pages and verify whether the statement appears in the source report pages.",
        "use when": "You need page-level provenance, hallucination checks, or evidence that an extracted statement is grounded in the OCR source.",
        "outputs": "Exact/likely/possible/not-found page matches, evidence snippets, and downloadable verification CSVs.",
    },
    {
        "page": "2_3_LLM_Background_Run_Monitor.py",
        "label": "LLM Background Run Monitor",
        "stage": "Extraction runner",
        "primary RQs": "RQ1, RQ4, RQ5, RQ6",
        "purpose": "Launch T3-style LLM extraction as a background job and visualize live progress.",
        "use when": "You want long LLM runs to continue behind the scenes while monitoring status, current sample, completed counts, failures, and logs.",
        "outputs": "background_llm_jobs/* status/events/logs plus appended T3-style records in results/esg_records.json.",
    },
    {
        "page": "2_1_LLM_Error_Parse_Audit.py",
        "label": "LLM Error Parse Audit",
        "stage": "Failure audit",
        "primary RQs": "RQ4, RQ6",
        "purpose": "Audit failed, empty, raw-output, and parse-error LLM runs.",
        "use when": "You need concrete evidence for extraction failure modes and prompt/model weaknesses.",
        "outputs": "Error categories, raw-output signals, failure tables.",
    },
]

RQ_WORKFLOWS = {
    "RQ1": {
        "question": "How can sustainability reports be transformed into structured ESG evidence?",
        "goal": "Prove the PDF/OCR-to-structured-record pipeline works and is traceable.",
        "steps": [
            ("Collect and OCR reports", "Bulk_OCR.py", "Upload/select PDFs, run OCR, save markdown, images, and OCR JSON."),
            ("Run extraction", "llm_processing.py", "Use OCR text batches and run ESG ABSA prompts/models."),
            ("Run long extraction in background", "2_3_LLM_Background_Run_Monitor.py", "Launch selected document/page/model/prompt batches and monitor progress."),
            ("Inspect LLM outputs", "2_0_LLM_Processing_Result_Visualizer.py", "Check parsed records, prompts, model names, source targets, and run success."),
            ("Verify statement grounding", "2_2_LLM_Statement_Page_Verifier.py", "Confirm extracted statements can be found in the OCR markdown pages."),
            ("Inspect pipeline outputs", "1_9_Ground_Truth_Pipeline_Output_Visualizer.py", "Show record-level traceability and structured fields."),
            ("Measure OCR quality", "1_2_OCR_Quality_Workbench.py", "Add manual reference snippets and compute CER/WER."),
            ("Synthesize evidence", "1_7_Research_Questions_Dashboard.py", "Use RQ1 and Chapter 4 tabs to write the results."),
        ],
        "chapter use": "Chapter 4.1 pipeline output; Chapter 5 limitations for OCR quality.",
    },
    "RQ2": {
        "question": "How should ESG be categorized by aspect, pillar, sentiment, and tone?",
        "goal": "Show the ABSA taxonomy and descriptive distributions, then validate with expert labels.",
        "steps": [
            ("Inspect tone and pillar distributions", "0_9_Tone_ClimateBERT_Visualization.py", "Use tone distribution, ESG-by-tone, and aspect heatmaps."),
            ("Inspect ontology coverage", "1_6_Ontology_Path_Viewer.py", "Check standard vs non-standard aspect labels and ontology paths."),
            ("Review ground-truth coverage", "1_8_Ground_Truth_Output_Visualizer.py", "Find records needing human review and coverage gaps."),
            ("Annotate records", "1_1_Ground_Truth_Workbench.py", "Create human labels for tone, pillar, aspect, and sentiment."),
            ("Compute validation metrics", "1_3_Ground_Truth_Metrics.py", "Calculate kappa, precision, recall, F1, and disagreement tables."),
            ("Synthesize evidence", "1_7_Research_Questions_Dashboard.py", "Use RQ2 and Chapter 4/5 tabs for writing."),
        ],
        "chapter use": "Chapter 4.2 descriptive ABSA results; Chapter 5 validity discussion.",
    },
    "RQ3": {
        "question": "Do ABSA tone outputs differ from ClimateBERT-style classification?",
        "goal": "Compare tone extraction against ClimateBERT-style labels and later actual ClimateBERT outputs.",
        "steps": [
            ("Review proxy label alignment", "0_9_Tone_ClimateBERT_Visualization.py", "Use ClimateBERT label-by-tone and remote score visualizations."),
            ("Prepare full ClimateBERT batch", "1_4_ClimateBERT_Record_Batch.py", "Export all valid records for ClimateBERT and preserve record IDs."),
            ("Import real ClimateBERT outputs", "1_4_ClimateBERT_Record_Batch.py", "Merge actual model outputs back into the record table."),
            ("Analyze agreement", "1_0_Revision_Analytics.py", "Use agreement/kappa and false-negative discussion."),
            ("Synthesize evidence", "1_7_Research_Questions_Dashboard.py", "Use RQ3, Benchmarks, and Chapter 5 tabs."),
        ],
        "chapter use": "Chapter 4.3 proxy/external comparison; Chapter 5 construct-validity caution.",
    },
    "RQ4": {
        "question": "What weaknesses arise in ABSA extraction outputs?",
        "goal": "Turn errors, missing labels, schema drift, and ontology gaps into a diagnostics framework.",
        "steps": [
            ("Audit parse failures", "2_1_LLM_Error_Parse_Audit.py", "Review failed runs, raw outputs, and JSON parse signals."),
            ("Monitor failed background items", "2_3_LLM_Background_Run_Monitor.py", "Use failed counts, logs, and events to locate unstable model/prompt runs."),
            ("Check source grounding", "2_2_LLM_Statement_Page_Verifier.py", "Find extracted statements that are not exact or likely matches in the OCR pages."),
            ("Review revision diagnostics", "1_0_Revision_Analytics.py", "Use failure-mode counts, missing-tone counts, and schema drift."),
            ("Inspect human-review queue", "1_8_Ground_Truth_Output_Visualizer.py", "Identify records needing annotation or correction."),
            ("Compute validation metrics", "1_3_Ground_Truth_Metrics.py", "Quantify disagreements once labels exist."),
            ("Inspect ontology failures", "1_6_Ontology_Path_Viewer.py", "Explain non-standard aspects and taxonomy gaps."),
            ("Synthesize evidence", "1_7_Research_Questions_Dashboard.py", "Use RQ4 and Chapter 5 limitations sections."),
        ],
        "chapter use": "Chapter 4.4 diagnostics; Chapter 5 reliability threats.",
    },
    "RQ5": {
        "question": "How can documentation and visualization maximize auditability?",
        "goal": "Show the workflow is reproducible through pages, artifacts, screenshots, JSON, CSV, and documentation.",
        "steps": [
            ("Start from the workflow hub", "0_0_Streamlit_Page_Workflow.py", "Use this page as the navigation and audit map."),
            ("Use the RQ dashboard", "1_7_Research_Questions_Dashboard.py", "Show evidence matrix, chapter map, and Mermaid flow."),
            ("Use saved image outputs", "1_7_Research_Questions_Dashboard_outputs.md", "Cite saved screenshots and image explanations."),
            ("Show page-level provenance", "2_2_LLM_Statement_Page_Verifier.py", "Use source page matches and evidence snippets to demonstrate auditability."),
            ("Show live run provenance", "2_3_LLM_Background_Run_Monitor.py", "Use job status, events, and logs to document how long extraction runs were produced."),
            ("Open specific evidence pages", "0_9_Tone_ClimateBERT_Visualization.py", "Show concrete figures backing each RQ."),
            ("Inspect generated artifacts", "results/visualizations", "Use PNG/CSV/JSON outputs for reproducibility evidence."),
            ("Maintain docs index", "README.md", "Keep page documentation synchronized with active Streamlit pages."),
        ],
        "chapter use": "Chapter 3 methodology support; Chapter 6 contribution and reproducibility claim.",
    },
    "RQ6": {
        "question": "How do prompt strategy and model choice affect extraction stability?",
        "goal": "Measure prompt/model instability and decide what reruns or ensemble checks are required.",
        "steps": [
            ("Inspect prompt stability", "1_0_Revision_Analytics.py", "Use missing-tone rate, schema drift, and field-completion summary."),
            ("Run matched reruns in background", "2_3_LLM_Background_Run_Monitor.py", "Queue comparable model/prompt jobs and watch progress until complete."),
            ("Inspect raw LLM runs", "2_0_LLM_Processing_Result_Visualizer.py", "Compare model, prompt, target, and record counts."),
            ("Verify extracted statements", "2_2_LLM_Statement_Page_Verifier.py", "Compare grounding quality across model/prompt outputs."),
            ("Audit errors", "2_1_LLM_Error_Parse_Audit.py", "Explain broken prompts and raw-output failures."),
            ("Plan matched reruns", "llm_processing.py", "Run GPT-oss and Arcee on the same documents/prompts."),
            ("Validate with external labels", "1_4_ClimateBERT_Record_Batch.py", "Use real ClimateBERT output for verification if available."),
            ("Synthesize evidence", "1_7_Research_Questions_Dashboard.py", "Use RQ6, Analysis Plan, and Chapter 5 tabs."),
        ],
        "chapter use": "Chapter 4.4 stability results; Chapter 5 reliability discussion; Chapter 6 future work.",
    },
}

WORKFLOW_MERMAID = """
flowchart TD
  subgraph node_I["Input and Extraction"]
    node_I_A_1["Bulk_OCR.py\\nPDFs -> OCR markdown/images"]
    node_I_A_6["0_3_OCR_Company_Metadata_Labeler.py\\nCompany + sector metadata"]
    node_I_A_2["llm_processing.py\\nLLM ESG ABSA extraction"]
    node_I_A_5["2_3_LLM_Background_Run_Monitor.py\\nBackground extraction runner"]
    node_I_A_3["2_0_LLM_Processing_Result_Visualizer.py\\nInspect parsed outputs"]
    node_I_A_4["2_1_LLM_Error_Parse_Audit.py\\nAudit failures"]
  end

  subgraph node_II["Analysis and Validation"]
    node_II_B_1["0_9_Tone_ClimateBERT_Visualization.py\\nTone, ESG, aspect, ClimateBERT proxy"]
    node_II_B_2["1_0_Revision_Analytics.py\\nRevision metrics and stability"]
    node_II_B_3["1_9_Ground_Truth_Pipeline_Output_Visualizer.py\\nTraceability"]
    node_II_B_4["1_6_Ontology_Path_Viewer.py\\nTaxonomy coverage"]
    node_II_B_5["1_1_Ground_Truth_Workbench.py\\nHuman annotation"]
    node_II_B_6["1_3_Ground_Truth_Metrics.py\\nKappa/F1/disagreement"]
    node_II_B_7["1_4_ClimateBERT_Record_Batch.py\\nReal ClimateBERT validation"]
    node_II_B_8["1_2_OCR_Quality_Workbench.py\\nCER/WER"]
    node_II_B_9["1_5_ESG_Flow_Sankey.py\\nFlow visualization"]
    node_II_B_10["1_8_Ground_Truth_Output_Visualizer.py\\nReview coverage"]
    node_II_B_11["2_2_LLM_Statement_Page_Verifier.py\\nStatement-to-page grounding"]
  end

  subgraph node_V["Synthesis and Thesis Writing"]
    node_V_C_1["1_7_Research_Questions_Dashboard.py\\nRQ + Chapter 4-6 synthesis"]
    node_V_C_2["0_0_Streamlit_Page_Workflow.py\\nNavigation and complete workflow"]
    node_V_C_3["Documentation + saved image catalog\\nMarkdown, PNG, JSON evidence"]
  end

  node_I_A_1 -- "RQ1, RQ5" --> node_I_A_6
  node_I_A_6 -- "RQ1, RQ5" --> node_I_A_2
  node_I_A_1 -- "RQ1, RQ5" --> node_I_A_2
  node_I_A_2 -- "RQ1, RQ4, RQ5, RQ6" --> node_I_A_5
  node_I_A_5 -- "RQ1, RQ2, RQ6" --> node_I_A_3
  node_I_A_2 -- "RQ1, RQ2, RQ6" --> node_I_A_3
  node_I_A_2 -- "RQ4, RQ6" --> node_I_A_4
  node_I_A_3 -- "RQ2, RQ3, RQ5" --> node_II_B_1
  node_I_A_3 -- "RQ2, RQ3, RQ4, RQ6" --> node_II_B_2
  node_I_A_3 -- "RQ1, RQ2, RQ4" --> node_II_B_3
  node_I_A_3 -- "RQ1, RQ4, RQ5, RQ6" --> node_II_B_11
  node_II_B_1 -- "RQ2, RQ4, RQ5" --> node_II_B_4
  node_II_B_3 -- "RQ2, RQ4" --> node_II_B_5
  node_II_B_5 -- "RQ2, RQ4" --> node_II_B_6
  node_I_A_3 -- "RQ3, RQ4" --> node_II_B_7
  node_I_A_1 -- "RQ1, RQ4" --> node_II_B_8
  node_II_B_1 -- "RQ2, RQ5" --> node_II_B_9
  node_I_A_4 -- "RQ4, RQ6" --> node_II_B_10
  node_II_B_1 -- "RQ2, RQ3, RQ5" --> node_V_C_1
  node_II_B_2 -- "RQ2, RQ3, RQ4, RQ6" --> node_V_C_1
  node_II_B_4 -- "RQ2, RQ4, RQ5" --> node_V_C_1
  node_II_B_6 -- "RQ2, RQ4" --> node_V_C_1
  node_II_B_7 -- "RQ3, RQ4" --> node_V_C_1
  node_II_B_8 -- "RQ1, RQ4" --> node_V_C_1
  node_II_B_11 -- "RQ1, RQ4, RQ5, RQ6" --> node_V_C_1
  node_V_C_1 -- "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6" --> node_V_C_2
  node_V_C_1 -- "RQ5" --> node_V_C_3
"""


def page_df() -> pd.DataFrame:
    return pd.DataFrame(PAGE_REGISTRY)


st.title("Streamlit Page Workflow")
st.caption("Navigation hub for every Streamlit page, every RQ workflow, and the thesis evidence trail.")

overview, pages_tab, rq_tab, pipeline_tab, chapters_tab, docs_tab = st.tabs(
    ["Overview", "Every Page", "RQ Workflows", "Complete Workflow", "Chapter Usage", "Documentation"]
)

with overview:
    st.subheader("How to use this page")
    st.markdown(
        """
        Start here when you are writing, validating, or defending the thesis. The app has many pages,
        so this workflow page tells you which one to open, what it proves, and how it contributes to each RQ.
        """
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered pages", f"{len(PAGE_REGISTRY):,}")
    c2.metric("Research workflows", f"{len(RQ_WORKFLOWS):,}")
    c3.metric("Major stages", f"{page_df()['stage'].nunique():,}")
    c4.metric("Thesis chapters", "4-6")

    st.subheader("Fast path")
    fast_path = pd.DataFrame(
        [
            {"task": "Write Chapter 4 results", "start page": "1_7_Research_Questions_Dashboard.py", "then open": "0_9, 1_0, 1_9, 2_1"},
            {"task": "Answer RQ1", "start page": "Bulk_OCR.py", "then open": "llm_processing, 2_0, 1_9, 1_2"},
            {"task": "Answer RQ2", "start page": "0_9_Tone_ClimateBERT_Visualization.py", "then open": "1_6, 1_8, 1_1, 1_3"},
            {"task": "Answer RQ3", "start page": "1_4_ClimateBERT_Record_Batch.py", "then open": "0_9, 1_0"},
            {"task": "Answer RQ4", "start page": "2_1_LLM_Error_Parse_Audit.py", "then open": "1_0, 1_8, 1_3"},
            {"task": "Answer RQ5", "start page": "1_7_Research_Questions_Dashboard.py", "then open": "docs README and saved image outputs"},
            {"task": "Answer RQ6", "start page": "1_0_Revision_Analytics.py", "then open": "2_0, 2_1, llm_processing"},
        ]
    )
    st.dataframe(fast_path, use_container_width=True, hide_index=True)

with pages_tab:
    st.subheader("Every Streamlit page and what it is for")
    st.dataframe(page_df(), use_container_width=True, hide_index=True)

    st.subheader("Open a page")
    grouped = page_df().groupby("stage", sort=False)
    for stage, rows in grouped:
        with st.expander(stage, expanded=stage in {"Synthesis", "Data ingestion", "Results"}):
            for _, row in rows.iterrows():
                cols = st.columns([1.2, 2.8, 1.2])
                with cols[0]:
                    page_link(row["page"], row["label"])
                with cols[1]:
                    st.write(row["purpose"])
                with cols[2]:
                    st.caption(row["primary RQs"])

with rq_tab:
    st.subheader("RQ-by-RQ workflow")
    selected_rq = st.radio("Choose an RQ", list(RQ_WORKFLOWS.keys()), horizontal=True)
    workflow = RQ_WORKFLOWS[selected_rq]
    st.markdown(f"### {selected_rq}: {workflow['question']}")
    st.info(workflow["goal"])
    st.caption(workflow["chapter use"])

    for idx, (step, page, action) in enumerate(workflow["steps"], start=1):
        with st.container(border=True):
            cols = st.columns([0.6, 1.8, 4.2])
            cols[0].metric("Step", idx)
            with cols[1]:
                page_link(page, page)
            with cols[2]:
                st.markdown(f"**{step}**")
                st.write(action)

    st.subheader("Workflow table")
    st.dataframe(
        pd.DataFrame(
            [
                {"step": idx, "action": step, "page": page, "what to do": action}
                for idx, (step, page, action) in enumerate(workflow["steps"], start=1)
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

with pipeline_tab:
    st.subheader("Complete workflow from source PDF to thesis conclusion")
    st.markdown(
        """
        Each Mermaid edge is labeled with the RQ(s) it supports. You can filter by a single RQ, such as
        `RQ1`, or by multiple RQs, such as `RQ1, RQ5`. Multi-RQ edge labels are treated as belonging to
        every RQ in the label.
        """
    )

    workflow_nodes, workflow_edges = parse_workflow_mermaid(WORKFLOW_MERMAID)
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
        show_funnel = st.toggle("Show funnel view", value=True)
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
    st.caption(
        "Tip: keep all RQs selected for the complete map, or choose one RQ to reveal only that research path. "
        "Edges labeled `RQ1, RQ5` appear when either RQ is selected in match-any mode."
    )

    if show_funnel:
        st.subheader("RQ-filtered workflow funnel")
        st.caption(
            "The funnel summarizes the same filtered Mermaid graph by thesis workflow stage, so selecting "
            "RQ1, RQ5, or any multi-RQ path changes both the diagram and the funnel together."
        )
        funnel_df = build_workflow_funnel_df(filtered_nodes, filtered_edges)
        render_workflow_funnel(funnel_df)
        st.dataframe(
            funnel_df[
                [
                    "step",
                    "stage",
                    "visible pages",
                    "visible edges touching stage",
                    "pages",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    if filtered_mermaid:
        render_mermaid(filtered_mermaid)
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
    st.code(filtered_mermaid or "", language="mermaid")

    with st.expander("Full unfiltered Mermaid source"):
        st.code(WORKFLOW_MERMAID, language="mermaid")

with chapters_tab:
    st.subheader("Which pages to use by thesis chapter")
    chapter_rows = pd.DataFrame(
        [
            {"chapter": "Chapter 3 Methodology", "use pages": "Bulk_OCR.py; llm_processing.py; ground_truth.py; 1_4; 1_6", "purpose": "Describe pipeline design, extraction prompts, validation plan, taxonomy, and auditability."},
            {"chapter": "Chapter 4 Results", "use pages": "1_7; 0_9; 1_0; 1_9; 2_1; 1_5", "purpose": "Report empirical outputs: records, distributions, proxy agreement, greenwashing signal, diagnostics, and stability."},
            {"chapter": "Chapter 5 Discussion", "use pages": "1_7; 1_0; 1_8; 1_3; 1_2; 2_1", "purpose": "Interpret claim strength, validity, limitations, sample-size risks, and reliability threats."},
            {"chapter": "Chapter 6 Conclusion", "use pages": "1_7; 0_0; documentation/streamlit_pages", "purpose": "Answer each RQ, state contribution, and define future work."},
        ]
    )
    st.dataframe(chapter_rows, use_container_width=True, hide_index=True)

    st.subheader("Chapter writing route")
    for row in chapter_rows.to_dict("records"):
        with st.expander(row["chapter"], expanded=row["chapter"] == "Chapter 4 Results"):
            st.write(row["purpose"])
            st.code(row["use pages"], language=None)

with docs_tab:
    st.subheader("Documentation files")
    doc_files = sorted(DOCS_DIR.glob("*.md"))
    doc_rows = []
    for doc in doc_files:
        doc_rows.append(
            {
                "doc": doc.name,
                "path": str(doc.relative_to(ROOT)),
                "exists": doc.exists(),
            }
        )
    st.dataframe(pd.DataFrame(doc_rows), use_container_width=True, hide_index=True)

    st.subheader("Key docs to keep updated")
    docs = [
        ("Streamlit docs index", DOCS_DIR / "README.md"),
        ("Research Questions Dashboard docs", DOCS_DIR / "1_7_Research_Questions_Dashboard.md"),
        ("Saved image outputs", DOCS_DIR / "1_7_Research_Questions_Dashboard_outputs.md"),
    ]
    for label, path in docs:
        with st.expander(label):
            st.code(str(path.relative_to(ROOT)), language=None)
            if path.exists():
                st.markdown(path.read_text(encoding="utf-8")[:2500])
