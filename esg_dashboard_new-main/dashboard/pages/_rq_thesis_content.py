from __future__ import annotations

import hashlib
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


PAGE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = PAGE_DIR / "research_question_artifacts"
ARTIFACT_JSON = ARTIFACT_DIR / "research_question_artifacts.json"

EXISTING_DATA_PATH = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/data_output.txt"
PREDICTION_OUTPUT_DIR = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/climatebert_predictions"


RQ_PAGE_MAP = [
    {
        "rq": "RQ1",
        "theme": "Pipeline",
        "question": "How can PDF sustainability reports become structured, sentence-level ESG records for ABSA?",
        "primary_pages": [
            ("Parsed ESG JSON", "/Parsed_ESG_JSON"),
            ("Parsed ESG Review", "/Parsed_ESG_Review"),
            ("Data File Visualizer", "/Data_File_Visualizer"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
        ],
        "chapter_4_use": "Show parsed record counts, schema completion, provenance, document coverage, and extraction throughput.",
        "chapter_5_use": "Discuss extraction reliability, OCR/segmentation limitations, and whether the pipeline is audit-ready.",
        "chapter_6_use": "Conclude whether the pipeline is usable for thesis-scale ESG ABSA and what validation remains.",
        "needed_completion": "Add OCR CER/WER, table extraction accuracy, and sentence-boundary precision/recall.",
    },
    {
        "rq": "RQ2",
        "theme": "Categorization",
        "question": "How should ESG be categorized by aspect, pillar, sentiment, and tone across bilingual disclosures?",
        "primary_pages": [
            ("Parsed ESG JSON", "/Parsed_ESG_JSON"),
            ("Aspect", "/Aspect"),
            ("Tone Distribution", "/Tone_Distribution"),
            ("Data Distribution", "/Data_Distribution"),
            ("Sankey", "/Sankey"),
            ("Sample Size Reasoning", "/Sample_Size_Reasoning"),
        ],
        "chapter_4_use": "Report tone, pillar, language, sentiment, and aspect distributions from the parsed dataset.",
        "chapter_5_use": "Interpret bilingual asymmetry, class imbalance, taxonomy drift, and weak-label limitations.",
        "chapter_6_use": "Conclude which categorization results are descriptive now and which require expert validation.",
        "needed_completion": "Create expert gold labels, compute Cohen kappa, precision, recall, F1, and ontology coverage.",
    },
    {
        "rq": "RQ3",
        "theme": "ClimateBERT",
        "question": "Do tone-based ABSA outputs differ from ClimateBERT-style classifications?",
        "primary_pages": [
            ("ClimateBERT Dataset Processor", "/ClimateBERT_Dataset_Processor"),
            ("ClimateBERT Result Visualizer", "/ClimateBERT_Result_Visualizer"),
            ("Benchmark Model", "/Benchmark_Model"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
        ],
        "chapter_4_use": "Present model coverage, saved prediction CSVs, label distributions, and tone x ClimateBERT crosstabs.",
        "chapter_5_use": "Discuss whether ClimateBERT captures climate-specific signals that differ from rhetorical tone.",
        "chapter_6_use": "Conclude whether local ClimateBERT outputs strengthen the ABSA evidence layer.",
        "needed_completion": "Run all selected local models across all valid rows and compute agreement, confidence, and Cohen kappa.",
    },
    {
        "rq": "RQ4",
        "theme": "Diagnostics",
        "question": "What weaknesses arise in ABSA extraction, and how can diagnostics quantify extraction errors?",
        "primary_pages": [
            ("Parsed ESG Review", "/Parsed_ESG_Review"),
            ("Parsed ESG JSON", "/Parsed_ESG_JSON"),
            ("Metric Analysis", "/Metric_Analysis"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
        ],
        "chapter_4_use": "Show missing tone, schema drift, ontology gaps, and error-prone model/prompt combinations.",
        "chapter_5_use": "Discuss root causes: prompt schema, model behavior, OCR noise, taxonomy ambiguity, and imbalance.",
        "chapter_6_use": "Conclude whether the diagnostic framework can guide model and prompt improvements.",
        "needed_completion": "Manually label error types and summarize error rates by model, prompt, document, language, and pillar.",
    },
    {
        "rq": "RQ5",
        "theme": "Reproducibility",
        "question": "How can documentation and visualization maximize reproducibility and auditability?",
        "primary_pages": [
            ("Research Questions Dashboard", "/Research_Questions_Dashboard"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
            ("Data File Visualizer", "/Data_File_Visualizer"),
            ("Chapter 4 Results", "/Chapter_4_Results"),
            ("Chapter 5 Discussion", "/Chapter_5_Discussion"),
            ("Chapter 6 Conclusion", "/Chapter_6_Conclusion"),
        ],
        "chapter_4_use": "List generated artifacts, saved images, JSON reports, Markdown reports, and traceable data sources.",
        "chapter_5_use": "Discuss auditability, rerun capability, interruption recovery, and limits of reproducibility evidence.",
        "chapter_6_use": "Conclude whether the project is reproducible enough for thesis review and future replication.",
        "needed_completion": "Add an independent replication log, formal checklist, and schema stability regression test.",
    },
    {
        "rq": "RQ6",
        "theme": "Stability",
        "question": "How stable are ABSA outputs across models and prompts, and can ensemble strategies improve reliability?",
        "primary_pages": [
            ("Parsed ESG JSON", "/Parsed_ESG_JSON"),
            ("Metric Analysis", "/Metric_Analysis"),
            ("Benchmark Model", "/Benchmark_Model"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
            ("Sample Size Reasoning", "/Sample_Size_Reasoning"),
        ],
        "chapter_4_use": "Report prompt-family effects, coefficient of variation, per-document variance, and matched coverage gaps.",
        "chapter_5_use": "Discuss why prompt/model instability matters for thesis validity and how ensemble logic may help.",
        "chapter_6_use": "Conclude whether stability has been quantified enough to support final ABSA claims.",
        "needed_completion": "Build balanced model x prompt x document coverage and run majority-vote or ensemble simulations.",
    },
]


CHAPTER_4_SECTIONS = [
    {
        "section": "4.1 Dataset and Parsed ESG Records",
        "supports": "RQ1, RQ2",
        "results": "Describe the existing parsed dataset, document coverage, sentence counts, language mix, ESG pillars, tone labels, and source traceability.",
        "pages": ["Parsed ESG JSON", "Parsed ESG Review", "Data File Visualizer"],
    },
    {
        "section": "4.2 ESG Categorization Outputs",
        "supports": "RQ2",
        "results": "Visualize aspect, pillar, tone, language, and sentiment distributions, including imbalanced Social-pillar evidence and bilingual tone patterns.",
        "pages": ["Aspect", "Tone Distribution", "Data Distribution", "Sankey"],
    },
    {
        "section": "4.3 ClimateBERT Prediction Results",
        "supports": "RQ3",
        "results": "Show local model processing coverage, saved prediction shards, confidence distributions, and label counts by selected model.",
        "pages": ["ClimateBERT Dataset Processor", "ClimateBERT Result Visualizer"],
    },
    {
        "section": "4.4 Diagnostics and Error Signals",
        "supports": "RQ4, RQ6",
        "results": "Report schema drift, missing-tone records, ontology gaps, prompt instability, and model/prompt failure clusters.",
        "pages": ["Parsed ESG Review", "Metric Analysis", "Research Questions Visualizer"],
    },
    {
        "section": "4.5 Reproducibility Artifacts",
        "supports": "RQ5",
        "results": "Show generated PNG images, Mermaid sources, JSON explanations, Markdown report, and dashboard-page lineage.",
        "pages": ["Research Questions Dashboard", "Research Questions Visualizer"],
    },
]


CHAPTER_5_SECTIONS = [
    {
        "section": "5.1 Pipeline Validity",
        "supports": "RQ1",
        "discussion": "Interpret the pipeline as functional and traceable, while clearly marking OCR and segmentation metrics as remaining validation work.",
    },
    {
        "section": "5.2 Meaning of ESG Categorization Patterns",
        "supports": "RQ2",
        "discussion": "Discuss what tone, language, pillar, and sentiment patterns suggest, while separating descriptive weak-label evidence from validated classification performance.",
    },
    {
        "section": "5.3 ClimateBERT vs Tone-Based ABSA",
        "supports": "RQ3",
        "discussion": "Explain whether ClimateBERT labels confirm, complement, or disagree with tone-based ABSA labels once prediction coverage is complete.",
    },
    {
        "section": "5.4 Diagnostic Failure Modes",
        "supports": "RQ4",
        "discussion": "Discuss schema drift, ontology mismatch, missing tone, and prompt/model effects as actionable diagnostic categories.",
    },
    {
        "section": "5.5 Auditability and Reproducibility",
        "supports": "RQ5",
        "discussion": "Evaluate whether saved outputs, page links, generated artifacts, and rerunnable processors make the study auditable.",
    },
    {
        "section": "5.6 Stability and Ensemble Implications",
        "supports": "RQ6",
        "discussion": "Discuss prompt sensitivity, coefficient of variation, and why balanced model/prompt comparisons are required before reliability claims.",
    },
]


CHAPTER_6_SECTIONS = [
    {
        "section": "6.1 Research Answer Summary",
        "conclusion": "The dashboard supports descriptive ESG ABSA findings and makes validation gaps explicit for each RQ.",
    },
    {
        "section": "6.2 Contributions",
        "conclusion": "The project contributes a traceable ESG extraction workflow, local ClimateBERT processing layer, result visualizer, and RQ evidence-management dashboard.",
    },
    {
        "section": "6.3 Limitations",
        "conclusion": "The strongest limitations are missing expert annotation, incomplete ClimateBERT coverage where applicable, OCR validation gaps, and unbalanced model/prompt comparisons.",
    },
    {
        "section": "6.4 Future Work",
        "conclusion": "Future work should complete gold labels, full prediction coverage, formal error taxonomy, reproducibility checklist, and ensemble stability testing.",
    },
    {
        "section": "6.5 Final Statement",
        "conclusion": "The system is thesis-ready as an implementation and evidence-navigation framework, while final performance claims should remain tied to completed validation metrics.",
    },
]


CHAPTER_FLOW_MERMAID = """
flowchart LR
  RQ["Research Questions"]
  C4["Chapter 4: Results"]
  C5["Chapter 5: Discussion"]
  C6["Chapter 6: Conclusion"]

  DATA["data_output.txt"]
  PRED["climatebert_predictions"]
  IMG["saved PNG + JSON + Markdown artifacts"]

  RQ --> C4
  DATA --> C4
  PRED --> C4
  IMG --> C4
  C4 --> C5
  C5 --> C6

  C4 --> R1["What was implemented and measured?"]
  C5 --> R2["What do results mean and where are limits?"]
  C6 --> R3["What can be concluded and what remains?"]
""".strip()


RQ_TO_CHAPTER_MERMAID = """
flowchart TB
  RQ1["RQ1 Pipeline"] --> C41["4.1 Dataset and Parsed ESG Records"]
  RQ2["RQ2 Categorization"] --> C42["4.2 ESG Categorization Outputs"]
  RQ3["RQ3 ClimateBERT"] --> C43["4.3 ClimateBERT Prediction Results"]
  RQ4["RQ4 Diagnostics"] --> C44["4.4 Diagnostics and Error Signals"]
  RQ5["RQ5 Reproducibility"] --> C45["4.5 Reproducibility Artifacts"]
  RQ6["RQ6 Stability"] --> C44

  C41 --> D51["5.1 Pipeline Validity"]
  C42 --> D52["5.2 Meaning of ESG Categorization Patterns"]
  C43 --> D53["5.3 ClimateBERT vs Tone-Based ABSA"]
  C44 --> D54["5.4 Diagnostic Failure Modes"]
  C45 --> D55["5.5 Auditability and Reproducibility"]
  C44 --> D56["5.6 Stability and Ensemble Implications"]

  D51 --> C61["6.1 Research Answer Summary"]
  D52 --> C61
  D53 --> C61
  D54 --> C62["6.2 Contributions and Limitations"]
  D55 --> C62
  D56 --> C63["6.3 Future Work and Final Statement"]
""".strip()


def load_artifact_report() -> dict:
    if not ARTIFACT_JSON.exists():
        return {}
    try:
        return json.loads(ARTIFACT_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def render_mermaid(code: str, height: int = 520) -> None:
    container_id = "mermaid_" + hashlib.md5(code.encode("utf-8")).hexdigest()
    code_json = json.dumps(code)
    html = f"""
    <div id="{container_id}_wrapper">
      <div id="{container_id}"></div>
      <pre id="{container_id}_error" style="display:none;"></pre>
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: 'loose',
        theme: 'base',
        flowchart: {{ curve: 'basis', htmlLabels: true }},
        themeVariables: {{
          primaryColor: '#f8fafc',
          primaryTextColor: '#111827',
          primaryBorderColor: '#64748b',
          lineColor: '#475569',
          clusterBkg: '#eef6f4',
          clusterBorder: '#0f766e',
          edgeLabelBackground: '#ffffff'
        }}
      }});
      const code = {code_json};
      const target = document.getElementById("{container_id}");
      const errorTarget = document.getElementById("{container_id}_error");
      try {{
        const rendered = await mermaid.render("{container_id}_svg", code);
        target.innerHTML = rendered.svg;
        const svg = target.querySelector("svg");
        if (svg) {{
          svg.removeAttribute("height");
          svg.style.width = "100%";
          svg.style.maxWidth = "100%";
          svg.style.height = "auto";
          svg.style.display = "block";
          svg.style.margin = "0 auto";
        }}
        if (rendered.bindFunctions) {{
          rendered.bindFunctions(target);
        }}
      }} catch (err) {{
        errorTarget.style.display = "block";
        errorTarget.textContent = "Mermaid render error:\\n" + err.message + "\\n\\n" + code;
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
        padding: 12px;
        white-space: pre-wrap;
      }}
    </style>
    """
    components.html(html, height=height + 80, scrolling=True)


def page_link_grid(page_pairs: list[tuple[str, str]], columns: int = 3) -> None:
    cols = st.columns(columns)
    for idx, (label, route) in enumerate(page_pairs):
        with cols[idx % columns]:
            st.link_button(label, route, use_container_width=True)
