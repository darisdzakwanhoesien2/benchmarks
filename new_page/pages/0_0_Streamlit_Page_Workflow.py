from __future__ import annotations

from pathlib import Path

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
            ("Inspect LLM outputs", "2_0_LLM_Processing_Result_Visualizer.py", "Check parsed records, prompts, model names, source targets, and run success."),
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
            ("Inspect raw LLM runs", "2_0_LLM_Processing_Result_Visualizer.py", "Compare model, prompt, target, and record counts."),
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
  A["Bulk_OCR.py\\nPDFs -> OCR markdown/images"] --> B["llm_processing.py\\nLLM ESG ABSA extraction"]
  B --> C["2_0_LLM_Processing_Result_Visualizer.py\\nInspect parsed outputs"]
  B --> D["2_1_LLM_Error_Parse_Audit.py\\nAudit failures"]
  C --> E["0_9_Tone_ClimateBERT_Visualization.py\\nTone, ESG, aspect, ClimateBERT proxy"]
  C --> F["1_0_Revision_Analytics.py\\nRevision metrics and stability"]
  C --> G["1_9_Ground_Truth_Pipeline_Output_Visualizer.py\\nTraceability"]
  E --> H["1_6_Ontology_Path_Viewer.py\\nTaxonomy coverage"]
  G --> I["1_1_Ground_Truth_Workbench.py\\nHuman annotation"]
  I --> J["1_3_Ground_Truth_Metrics.py\\nKappa/F1/disagreement"]
  C --> K["1_4_ClimateBERT_Record_Batch.py\\nReal ClimateBERT validation"]
  A --> L["1_2_OCR_Quality_Workbench.py\\nCER/WER"]
  E --> M["1_5_ESG_Flow_Sankey.py\\nFlow visualization"]
  D --> N["1_8_Ground_Truth_Output_Visualizer.py\\nReview coverage"]
  E --> O["1_7_Research_Questions_Dashboard.py\\nRQ + Chapter 4-6 synthesis"]
  F --> O
  H --> O
  J --> O
  K --> O
  L --> O
  O --> P["0_0_Streamlit_Page_Workflow.py\\nNavigation and complete workflow"]
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
    render_mermaid(WORKFLOW_MERMAID)
    st.subheader("Mermaid source")
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
