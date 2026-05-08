from pathlib import Path
from html import escape
import hashlib
import json
import re

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Research Questions Visualizer", layout="wide")
st.title("Research Questions Visualizer")
st.caption("Interactive view of thesis RQs, available evidence, analysis gaps, and next steps.")


SOURCE_HTML = Path(__file__).resolve().parent / "thesis_data_analysis_benchmarks.html"
EXISTING_DATA_PATH = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/data_output.txt"
PREDICTION_OUTPUT_DIR = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/climatebert_predictions"


RQ_DATA = [
    {
        "rq": "RQ1",
        "theme": "Pipeline",
        "question": "How can a PDF-to-structured ESG transformation pipeline convert Indonesian/English sustainability reports into a governance-aligned, sentence-level representation that supports ABSA?",
        "have": [
            "PDF sustainability reports: 6 docs available; BEST, VKTR, GTRA, PTBA, ICR, Indonet",
            "Markdown page outputs from OCR pipeline with source-page traceability",
            "Records-per-run throughput: mean 8.5 records/run; Arcee 14.3 records/run",
            "Field completion: 100% aspect/ESG/tone; 81.3% sentiment_score",
        ],
        "partial": ["JSON extraction records with provenance: 332 records"],
        "need": [
            "Reference text for CER computation",
            "Table/figure extraction accuracy labels",
            "Sentence boundary precision/recall",
            "ESG topic alignment accuracy from manual verification",
        ],
        "metrics": [
            ("JSON parse success", "100%", "332/332 records parseable"),
            ("Records extracted", "332", "from 6 docs and 39 unique runs"),
            ("OCR quality CER", "missing", "critical gap"),
        ],
        "priority": "Important",
    },
    {
        "rq": "RQ2",
        "theme": "Categorization",
        "question": "How should ESG be categorized by aspect/pillar, sentiment, and tone in bilingual disclosures to enable fine-grained ABSA while preserving cross-language comparability?",
        "have": [
            "Tone x ESG pillar cross-tabulation: E commitment=91, G commitment=24, S commitment=0",
            "Bilingual tone asymmetry: Indonesian outcome 7.9% vs English 21.8%",
            "Sentiment score distribution by tone: outcome mean=0.60 vs commitment mean=0.03",
        ],
        "partial": [
            "LLM labels: 332 records; commitment=115, action=58, outcome=50",
            "Language-tagged records: Indonesian=127, English=205",
        ],
        "need": [
            "Expert-annotated ground truth corpus: 30-50 records, 2 annotators",
            "Bilingual taxonomy mapping",
            "Aspect precision/recall/F1 vs gold labels",
            "Inter-annotator agreement, target Cohen kappa >= 0.70",
            "Ontology normalization for 41 non-standard aspects",
        ],
        "metrics": [
            ("Tone: commitment", "34.6%", "115/332, dominant category"),
            ("E/G/S split", "54/36/1%", "S severely underrepresented"),
            ("Non-standard aspects", "41", "ontology gap"),
        ],
        "priority": "Critical",
    },
    {
        "rq": "RQ3",
        "theme": "ClimateBERT",
        "question": "Do tone-based ABSA outputs differ meaningfully from ClimateBERT-style label classifications, and what is the relationship between detected tone and climate-specific targets?",
        "have": [
            "LLM-assigned ClimateBERT-style label families: 16 label families",
            "Co-occurrence frequency: commitment + climate-commitment = 91",
        ],
        "partial": [
            "Tone x ClimateBERT label crosstab exists, but labels are LLM-assigned",
            "Missing tone vs CB label analysis identifies possible false negatives",
        ],
        "need": [
            "ClimateBERT scores for all valid records from local runs",
            "Row-wise agreement between tone and ClimateBERT labels",
            "Cohen kappa between LLM tone and ClimateBERT classification",
        ],
        "metrics": [
            ("CB alignment commitment", "34.3%", "91/265 commitment records carry climate-commitment"),
            ("CB remote inputs", "3", "far too few; must run locally"),
            ("CB models available", "13", "detection, netzero, TCFD, sentiment, specificity"),
        ],
        "priority": "Critical",
    },
    {
        "rq": "RQ4",
        "theme": "Diagnostics",
        "question": "What weaknesses arise in ABSA extraction outputs, and how can a diagnostics framework detect and quantify extraction errors to inform model improvement?",
        "have": [
            "Complete extraction log per run",
            "Schema drift records: 18 records from data.md + GPT-oss-120b",
            "Missing tone records with context: 61 records",
            "Root cause attribution by model x prompt",
            "Schema drift rate by prompt template",
        ],
        "partial": [
            "Non-standard aspect labels: 41 unique free-text Indonesian labels",
            "Ontology failure rate: 41/332 = 12.3%",
            "Tone none analysis by prompt/pillar",
        ],
        "need": [
            "Manual error labels per record",
            "Formal error taxonomy: wrong-aspect, wrong-tone, wrong-pillar, schema-failure, OCR-noise",
        ],
        "metrics": [
            ("Missing tone, Arcee only", "0.4%", "1/272"),
            ("Schema drift rate", "30%", "18/60 records from data.md"),
            ("Ontology gap", "41", "all Indonesian free-text"),
        ],
        "priority": "Critical",
    },
    {
        "rq": "RQ5",
        "theme": "Reproducibility",
        "question": "How can documentation and visualization practices be designed to maximize reproducibility and auditability of ESG ABSA experiments?",
        "have": [
            "JSON extraction artifacts with full metadata",
            "Static visualization outputs: 5 PNG charts",
            "Streamlit dashboard with filterable tabs",
            "Artifact inventory and completeness audit",
        ],
        "partial": ["Prompt template version registry: 6 templates documented"],
        "need": [
            "Independent replication study log",
            "Formal reproducibility checklist",
            "Schema stability regression test",
            "Dashboard usability evaluation",
        ],
        "metrics": [
            ("Artifacts available", "5+5+1", "5 CSVs, 5 PNGs, 1 Streamlit app"),
            ("Prompt templates logged", "6", "zero-shot, few-shot, CoT, EN/ID variants"),
            ("Replication study", "0", "not yet conducted"),
        ],
        "priority": "Medium",
    },
    {
        "rq": "RQ6",
        "theme": "Stability",
        "question": "What is the stability of ABSA outputs across cross-model and cross-prompt configurations, and what ensemble or verification strategies yield the most reliable results?",
        "have": [
            "Prompt family effect: CoT +55% commitment, zero-shot +21-24%, few-shot +36%",
            "Coefficient of variation across prompts: 38.2%",
            "Language x prompt interaction",
        ],
        "partial": [
            "Per-prompt tone distributions, Arcee only",
            "Per-document commitment rate by prompt",
            "Per-document commitment variance: BEST-SR CoT=100% vs ZS=43%",
        ],
        "need": [
            "Balanced model x prompt x document matrix",
            "Few-shot template with n >= 30",
            "Cross-model Cohen kappa",
            "Ensemble majority-vote simulation",
        ],
        "metrics": [
            ("Prompt instability CV", "38.2%", "high variation across 5 prompts"),
            ("CoT vs zero-shot gap", "+31pp", "55% vs 23% commitment"),
            ("Cross-model kappa", "missing", "imbalanced runs"),
        ],
        "priority": "High",
    },
]


ANALYSIS_PLAN = pd.DataFrame([
    ["P1", "Run ClimateBERT on all valid records", "1-2 days", "RQ3", "Critical"],
    ["P2", "Expert annotation 30-50 records + IAA", "2-3 weeks", "RQ2, RQ4", "Critical"],
    ["P3", "Ensemble majority-vote on PTBA", "1 day", "RQ6", "High"],
    ["P4", "Statistical test of bilingual asymmetry", "2 hours", "RQ2", "High"],
    ["P5", "GW index per-doc per-prompt stability", "1 day", "RQ3, RQ5", "Medium"],
    ["P6", "S-pillar extraction + GPT-oss balance", "2-3 days", "RQ2, RQ6", "Medium"],
    ["P7", "OCR quality measurement", "1-2 days", "RQ1", "Important"],
], columns=["priority_id", "task", "effort", "answers", "urgency"])

MISSING_WORK = pd.DataFrame([
    [
        "RQ1",
        "OCR and segmentation quality",
        "Sample pages from data_output provenance, manually transcribe reference text, compute CER/WER and sentence-boundary precision.",
        EXISTING_DATA_PATH,
        "CER, WER, sentence precision/recall, table extraction accuracy",
    ],
    [
        "RQ2",
        "Gold taxonomy validation",
        "Draw 30-50 stratified records from parsed ESG sentences, have two annotators label aspect/pillar/tone/sentiment, compute agreement and F1.",
        EXISTING_DATA_PATH,
        "Cohen kappa, precision, recall, F1, ontology mapping coverage",
    ],
    [
        "RQ3",
        "Actual ClimateBERT comparison",
        "Run local ClimateBERT/ESGBERT models on every parsed sentence, then compare predicted labels with LLM tone/aspect fields.",
        PREDICTION_OUTPUT_DIR,
        "Tone x ClimateBERT crosstab, agreement rate, Cohen kappa",
    ],
    [
        "RQ4",
        "Diagnostics and error taxonomy",
        "Use parsed output plus manual spot checks to label schema drift, missing tone, wrong aspect, wrong pillar, and OCR-noise errors.",
        EXISTING_DATA_PATH,
        "Error rate by model, prompt, document, language, and pillar",
    ],
    [
        "RQ5",
        "Reproducibility evidence",
        "Connect saved artifacts, exact prompts, model versions, Streamlit pages, and regenerated outputs into an audit trail.",
        f"{EXISTING_DATA_PATH} + {PREDICTION_OUTPUT_DIR}",
        "Artifact inventory, rerun checklist, dashboard traceability",
    ],
    [
        "RQ6",
        "Stability and ensemble analysis",
        "Balance model x prompt x document coverage, then compare prompt variance and majority-vote/ensemble stability.",
        EXISTING_DATA_PATH,
        "Coefficient of variation, cross-model kappa, ensemble stability gain",
    ],
], columns=["rq", "missing_piece", "process", "primary_source", "output_metric"])

RQ_TABLE_GUIDE = pd.DataFrame([
    [
        "RQ1",
        "Pipeline",
        "Shows whether the PDF-to-Markdown-to-JSON pipeline is technically reliable enough to be used as the foundation for ABSA.",
        "JSON parse success, records per run, field completion, OCR CER/WER, sentence-boundary precision/recall, table extraction accuracy.",
        "JSON parse success near 100%; required fields complete; CER low enough that sentence meaning is preserved; segmentation errors rare; records trace back to page/source.",
        "If CER/WER is high, source text may be noisy and all downstream ESG labels become less trustworthy. If segmentation is poor, ABSA may classify fragments or merged sentences. If provenance is missing, auditability fails.",
        "Use data_output.txt for parsed records and provenance. Add manual OCR references for a small page sample to compute CER/WER.",
    ],
    [
        "RQ2",
        "Categorization",
        "Checks whether aspect, pillar, sentiment, and tone labels are valid and comparable across Indonesian and English disclosures.",
        "Expert-label agreement, Cohen kappa, precision/recall/F1 per tone/aspect/pillar, ontology coverage, bilingual label consistency.",
        "Kappa >= 0.70 for acceptable annotation agreement; F1 high enough per category, ideally >= 0.65 for each tone; non-standard aspect labels mapped into a stable taxonomy.",
        "Underperformance means the LLM labels are weak descriptive labels rather than validated ABSA labels. S-pillar underrepresentation means Social conclusions are not defensible yet.",
        "Draw a stratified sample from data_output.txt by tone, language, and pillar. Two annotators label the same records, then compare model labels with gold labels.",
    ],
    [
        "RQ3",
        "ClimateBERT",
        "Compares thesis tone-based ABSA against local ClimateBERT or ESGBERT model classifications.",
        "Coverage of ClimateBERT predictions, tone x ClimateBERT crosstab, agreement rate, Cohen kappa, model confidence distribution.",
        "Every valid sentence has predictions for selected models; agreement patterns are explainable; ClimateBERT adds a distinct climate-specific signal beyond LLM tone.",
        "If only a few rows have predictions, RQ3 remains incomplete. If agreement is very low, either mappings are wrong, ClimateBERT label space is incompatible, or LLM tone is measuring a different construct.",
        "Use climatebert_predictions as the primary source. Join predictions back to data_output.txt by sentence and compare labels to tone/aspect.",
    ],
    [
        "RQ4",
        "Diagnostics",
        "Quantifies where extraction fails and whether failures are caused by prompt design, model choice, OCR noise, schema drift, or ontology mismatch.",
        "Missing-tone rate, schema-drift rate, wrong-aspect rate, wrong-pillar rate, ontology failure rate, error rate by model/prompt/document/language.",
        "Low schema drift outside known bad prompts; missing tone near zero for stable models; error categories explainable and reducible through prompt/schema fixes.",
        "If drift clusters around one prompt/model, that prompt/model is unsafe. If errors are spread evenly, the taxonomy or source data may be underspecified.",
        "Use data_output.txt plus manual spot checks. Add an error_type column for sampled records and summarize by model/prompt/document.",
    ],
    [
        "RQ5",
        "Reproducibility",
        "Shows whether another person can trace, rerun, audit, and verify the ESG ABSA pipeline and its outputs.",
        "Artifact inventory, exact prompt registry, model version list, rerun checklist, saved outputs, dashboard traceability, replication log.",
        "Every chart/table links back to a dataset, prompt, model, and code path; outputs are reproducible or deviations are documented.",
        "If prompts, model versions, or output files are missing, the result may be visually persuasive but not auditable. This weakens thesis credibility even if metrics look good.",
        "Use both data_output.txt and climatebert_predictions, plus Streamlit pages and prompt files, to build an artifact checklist.",
    ],
    [
        "RQ6",
        "Stability",
        "Measures whether ABSA outputs are stable across model and prompt choices, and whether ensemble strategies improve reliability.",
        "Coefficient of variation across prompts, cross-model Cohen kappa, prompt-family effect size, majority-vote agreement, per-document variance.",
        "Balanced model x prompt x document coverage; lower variance after ensemble/majority voting; prompt differences are quantified rather than anecdotal.",
        "If one prompt has too few records or one model covers different documents, comparisons are confounded. High CV means results depend strongly on prompt design.",
        "Use data_output.txt to create a balanced comparison matrix. Target few-shot n >= 30 and matched documents across models/prompts.",
    ],
], columns=[
    "rq",
    "table_area",
    "what_this_table_does",
    "expected_metrics",
    "if_performing_well",
    "if_underperforming",
    "how_to_process",
])

TABLE_EXPLANATIONS = pd.DataFrame([
    [
        "Overview readiness chart",
        "Counts the number of available, partial, and needed evidence items for each RQ.",
        "It is not a statistical result. It is a project-management/readiness view.",
        "High available count and low needed count means an RQ is close to being defensible.",
        "High needed count means the RQ still needs data collection, annotation, or model runs before it can be claimed strongly.",
    ],
    [
        "RQ Details - Matrix",
        "Expands every RQ into individual evidence rows with status: Available, Partial, or Needed.",
        "Use it as the checklist of what evidence you already have and what is missing.",
        "Available rows can be cited as current evidence if the source is traceable.",
        "Needed rows are thesis risks; partial rows should be upgraded before strong claims.",
    ],
    [
        "RQ Details - Metrics",
        "Shows the headline metrics currently attached to each RQ.",
        "These are the thesis-facing indicators that should appear in results/discussion.",
        "A metric with a concrete value and clear denominator is stronger than a vague qualitative statement.",
        "A missing metric means the RQ is currently argued conceptually rather than empirically.",
    ],
    [
        "Missing Work Process",
        "Turns each missing RQ requirement into an action: source, process, and expected output metric.",
        "This table tells you exactly what to run or annotate next.",
        "A row is complete when the output metric can be computed and added back to the RQ metric table.",
        "If the source is unavailable or the metric cannot be computed, the RQ scope must be narrowed.",
    ],
    [
        "Analysis Plan",
        "Prioritizes the remaining analyses by urgency, effort, and which RQs they answer.",
        "It is the execution roadmap for closing thesis evidence gaps.",
        "Critical/High items should be handled before lower-priority documentation polish.",
        "If critical items remain undone, the thesis should avoid strong claims for those RQs.",
    ],
], columns=[
    "table_name",
    "what_it_does",
    "how_to_read_it",
    "if_yes_or_good",
    "if_underperforming_or_missing",
])


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
      #{container_id} {{
        display: flex;
        justify-content: center;
        min-width: 980px;
      }}
      #{container_id} svg {{
        max-width: none !important;
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
    components.html(html, height=height + 70, scrolling=True)


def mermaid_label(value: str, max_len: int = 70) -> str:
    clean = re.sub(r"\s+", " ", str(value)).strip()
    if len(clean) > max_len:
        clean = clean[: max_len - 3].rstrip() + "..."
    return clean.replace('"', "'")


def mermaid_id(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", str(value)).strip("_")
    if not clean:
        clean = "node"
    if clean[0].isdigit():
        clean = "n_" + clean
    return clean


def build_rq_evidence_mermaid(rq: str, detail_df: pd.DataFrame) -> str:
    rq_rows = detail_df[detail_df["rq"] == rq].reset_index(drop=True)
    if rq_rows.empty:
        return 'flowchart TB\n  Empty["No RQ detail rows selected"]'

    theme = rq_rows["theme"].iloc[0]
    source_node = "Predictions" if rq == "RQ3" else "DataOutput"
    lines = [
        "flowchart TB",
        '  DataOutput["data_output.txt - parsed ESG records"]',
        '  Predictions["climatebert_predictions - local model outputs"]',
        f'  RQNode["{rq} - {mermaid_label(theme)}"]',
        '  Available["Available evidence"]',
        '  Partial["Partial evidence"]',
        '  Needed["Needed evidence"]',
        f"  {source_node} --> RQNode",
        "  RQNode --> Available",
        "  RQNode --> Partial",
        "  RQNode --> Needed",
    ]

    for idx, row in rq_rows.iterrows():
        node_id = f"{row['status']}_{idx}"
        label = mermaid_label(row["item"], max_len=82)
        lines.append(f'  {node_id}["{label}"]')
        lines.append(f"  {row['status']} --> {node_id}")

    lines.extend([
        "  classDef source fill:#eef6ff,stroke:#2563eb,color:#111827;",
        "  classDef rq fill:#f8fafc,stroke:#334155,color:#111827,stroke-width:2px;",
        "  classDef available fill:#ecfdf5,stroke:#16a34a,color:#111827;",
        "  classDef partial fill:#fffbeb,stroke:#d97706,color:#111827;",
        "  classDef needed fill:#fef2f2,stroke:#dc2626,color:#111827;",
        "  class DataOutput,Predictions source;",
        "  class RQNode rq;",
        "  class Available available;",
        "  class Partial partial;",
        "  class Needed needed;",
    ])
    return "\n".join(lines)


def build_row_detail_mermaid(row: pd.Series) -> str:
    source = "Predictions" if row["rq"] == "RQ3" else "DataOutput"
    status_class = str(row["status"]).lower()
    return f"""
flowchart LR
  DataOutput["data_output.txt"]
  Predictions["climatebert_predictions"]
  RQ["{row['rq']} - {mermaid_label(row['theme'])}"]
  Item["{mermaid_label(row['item'], max_len=90)}"]
  Metric["Expected metric: {mermaid_label(row['expected_metric'], max_len=80)}"]
  Good["If good: {mermaid_label(row['if_yes_or_good'], max_len=80)}"]
  Weak["If weak: {mermaid_label(row['if_underperforming'], max_len=80)}"]
  Action["Next action: {mermaid_label(row['next_action'], max_len=80)}"]

  {source} --> RQ --> Item --> Metric
  Metric --> Good
  Metric --> Weak
  Weak --> Action

  classDef source fill:#eef6ff,stroke:#2563eb,color:#111827;
  classDef rq fill:#f8fafc,stroke:#334155,color:#111827,stroke-width:2px;
  classDef available fill:#ecfdf5,stroke:#16a34a,color:#111827;
  classDef partial fill:#fffbeb,stroke:#d97706,color:#111827;
  classDef needed fill:#fef2f2,stroke:#dc2626,color:#111827;
  class DataOutput,Predictions source;
  class RQ rq;
  class Item {status_class};
""".strip()


PIPELINE_MERMAID = f"""
flowchart LR
  PDFs["Sustainability reports - PDF source pages"]
  OCR["OCR and markdown extraction"]
  LLM["LLM ESG JSON extraction"]
  DataOutput["data_output.txt - sentence ESG records"]
  Parsed["Parsed ESG table - sentence aspect tone sentiment"]
  CBRun["Local ClimateBERT processor - page 02"]
  CBOut["climatebert_predictions - saved shard CSVs"]
  Viz["Result visualizer - page 03"]
  RQ["Research question evidence - page 04"]

  PDFs --> OCR --> LLM --> DataOutput --> Parsed
  Parsed --> CBRun --> CBOut --> Viz
  Parsed --> RQ
  CBOut --> RQ
""".strip()

RQ_MERMAID = """
flowchart TB
  RQ1["RQ1 Pipeline quality - needs CER WER segmentation"]
  RQ2["RQ2 Categorization - needs expert labels and taxonomy"]
  RQ3["RQ3 ClimateBERT comparison - needs full local outputs"]
  RQ4["RQ4 Diagnostics - needs manual error taxonomy"]
  RQ5["RQ5 Reproducibility - needs audit checklist and rerun log"]
  RQ6["RQ6 Stability - needs balanced model prompt matrix"]

  Data["data_output.txt"]
  Pred["climatebert_predictions"]
  Gold["Expert annotation sample"]
  Audit["Artifact registry / dashboard"]

  Data --> RQ1
  Data --> RQ2
  Data --> RQ4
  Data --> RQ6
  Pred --> RQ3
  Pred --> RQ5
  Gold --> RQ2
  Gold --> RQ4
  Audit --> RQ5
  RQ3 --> RQ6
""".strip()

MISSING_PROCESS_MERMAID = """
flowchart LR
  Gap["Missing RQ evidence"]
  Identify["Identify missing metric from RQ matrix"]
  Source["Select source - data_output or predictions"]
  Sample["Create targeted sample by RQ weakness"]
  Run["Run analysis or annotation"]
  Metric["Compute metric"]
  Update["Update dashboard evidence"]

  Gap --> Identify --> Source --> Sample --> Run --> Metric --> Update

  Source --> A["data_output.txt - parsed LLM ESG records"]
  Source --> B["climatebert_predictions - local model outputs"]
  Run --> C["manual annotation for RQ2 and RQ4"]
  Run --> D["ClimateBERT comparison for RQ3"]
  Run --> E["prompt model stability for RQ6"]
""".strip()


def status_counts(rows):
    return pd.DataFrame([
        {
            "rq": item["rq"],
            "theme": item["theme"],
            "available": len(item["have"]),
            "partial": len(item["partial"]),
            "needed": len(item["need"]),
            "priority": item["priority"],
        }
        for item in rows
    ])


def status_interpretation(status: str) -> str:
    if status == "Available":
        return "Evidence already exists and can support the RQ, provided the source is traceable and the denominator is clear."
    if status == "Partial":
        return "Evidence exists, but it is incomplete, weakly validated, imbalanced, or only a proxy for the real metric."
    return "Evidence is missing. This row is a work item that must be completed before the RQ can be claimed strongly."


def detail_for_item(rq: str, theme: str, status: str, item: str) -> dict[str, str]:
    guide = RQ_TABLE_GUIDE[RQ_TABLE_GUIDE["rq"] == rq].iloc[0]
    lower = item.lower()

    detail = {
        "what_it_does": guide["what_this_table_does"],
        "expected_metric": guide["expected_metrics"],
        "if_yes_or_good": guide["if_performing_well"],
        "if_underperforming": guide["if_underperforming"],
        "likely_reason_if_weak": "The evidence is not yet measured with a direct metric, has insufficient coverage, or lacks validation against an independent reference.",
        "next_action": guide["how_to_process"],
    }

    if "pdf sustainability reports" in lower:
        detail.update({
            "what_it_does": "Defines the document base of the thesis pipeline. It shows which source reports the ESG extraction is built from.",
            "expected_metric": "Number of source documents, number of pages, language mix, source-page coverage, and document diversity.",
            "if_yes_or_good": "The document set covers multiple companies, both languages, and enough pages to support report-level and sentence-level analysis.",
            "if_underperforming": "If only a few reports or one sector dominate, the thesis becomes a case study rather than a broadly descriptive ESG analysis.",
            "likely_reason_if_weak": "Document collection may be too narrow, too environmentally focused, or missing social/governance-heavy reports.",
            "next_action": "Add documents strategically, especially reports/pages rich in Social and Governance disclosures.",
        })
    elif "markdown page outputs" in lower:
        detail.update({
            "what_it_does": "Shows that the PDF/OCR stage produced intermediate text that can be traced back to report pages.",
            "expected_metric": "Page-to-record provenance coverage, OCR completion rate, and traceability from sentence back to page.",
            "if_yes_or_good": "Every extracted sentence can be linked back to a source page and inspected manually.",
            "if_underperforming": "If provenance is missing, later ESG labels cannot be audited or corrected confidently.",
            "likely_reason_if_weak": "The OCR/export pipeline may not preserve page metadata or markdown file references consistently.",
            "next_action": "Ensure each parsed record stores filename, page number, and/or markdown source identifier.",
        })
    elif "records-per-run" in lower or "throughput" in lower:
        detail.update({
            "what_it_does": "Measures extraction efficiency: how many usable ESG sentence records each model/prompt run produces.",
            "expected_metric": "Mean, median, and range of records per run by model, prompt, document, and language.",
            "if_yes_or_good": "Throughput is stable enough that additional sample expansion is predictable.",
            "if_underperforming": "Low or unstable throughput means scaling the dataset will take longer and may bias toward prompts/models that over-extract.",
            "likely_reason_if_weak": "Prompt design, document structure, model behavior, or OCR quality may be causing inconsistent extraction counts.",
            "next_action": "Compare throughput by model and prompt; keep high-quality prompts, not merely high-volume prompts.",
        })
    elif "field completion" in lower:
        detail.update({
            "what_it_does": "Checks schema completeness: whether required ABSA fields are populated after JSON parsing.",
            "expected_metric": "Completion percentage for sentence, aspect, ESG pillar/category, tone, sentiment, and confidence/score fields.",
            "if_yes_or_good": "Required fields are near 100% complete and optional score fields are mostly populated.",
            "if_underperforming": "Missing fields weaken downstream charts, crosstabs, and metric computation.",
            "likely_reason_if_weak": "Prompt schema may be ambiguous, model may drift from JSON instructions, or some source sentences may not contain enough signal.",
            "next_action": "Tighten JSON schema instructions and add validation/repair for missing fields.",
        })
    elif "json extraction records" in lower:
        detail.update({
            "what_it_does": "Shows that structured sentence-level records exist, but the evidence is still only partially validated.",
            "expected_metric": "Record count, parse success rate, valid sentence count, duplicate rate, and provenance completeness.",
            "if_yes_or_good": "Records are parseable, deduplicated, traceable, and balanced enough for the intended RQs.",
            "if_underperforming": "A raw record count alone can mislead if duplicates, bad parsing, or imbalanced document coverage are present.",
            "likely_reason_if_weak": "Records may come disproportionately from one model/prompt/document or may include duplicated sentences.",
            "next_action": "Run deduplication, provenance checks, and balance diagnostics before using counts as thesis evidence.",
        })
    elif "reference text" in lower or "cer" in lower:
        detail.update({
            "what_it_does": "Creates a ground-truth reference to measure OCR quality.",
            "expected_metric": "Character error rate, word error rate, and qualitative examples of OCR mistakes.",
            "if_yes_or_good": "CER/WER is low enough that ESG meaning is preserved; extraction errors are unlikely to be OCR-driven.",
            "if_underperforming": "High OCR error means downstream ABSA labels may classify corrupted text rather than original disclosure meaning.",
            "likely_reason_if_weak": "Scanned PDFs, tables, bilingual formatting, or report layout complexity can degrade OCR.",
            "next_action": "Manually transcribe 3-5 representative pages and compute CER/WER against OCR output.",
        })
    elif "table/figure" in lower:
        detail.update({
            "what_it_does": "Tests whether non-prose ESG evidence from tables and figures is captured accurately.",
            "expected_metric": "Table-cell extraction accuracy, figure-caption extraction coverage, and missed-table count.",
            "if_yes_or_good": "Important ESG metrics in tables remain available for downstream interpretation.",
            "if_underperforming": "The pipeline may miss quantitative ESG claims, making the dataset biased toward narrative prose.",
            "likely_reason_if_weak": "Tables often break OCR/markdown structure and may require separate table extraction logic.",
            "next_action": "Select table-heavy pages, label key cells manually, and compare extracted markdown/table outputs.",
        })
    elif "sentence boundary" in lower:
        detail.update({
            "what_it_does": "Checks whether the unit of ABSA analysis, the sentence, is correctly segmented.",
            "expected_metric": "Sentence boundary precision, recall, split error rate, and merge error rate.",
            "if_yes_or_good": "Each ABSA row corresponds to one coherent disclosure sentence.",
            "if_underperforming": "Merged sentences can contain multiple aspects; split fragments can lose context. Both reduce label validity.",
            "likely_reason_if_weak": "Bullet lists, abbreviations, Indonesian punctuation patterns, or OCR line breaks can confuse segmentation.",
            "next_action": "Manually label sentence boundaries for a small page sample and compare to automated segmentation.",
        })
    elif "topic alignment" in lower:
        detail.update({
            "what_it_does": "Validates whether extracted topics/aspects actually match ESG content in the source sentence.",
            "expected_metric": "Manual aspect-alignment accuracy and examples of wrong or overly broad aspect labels.",
            "if_yes_or_good": "Most aspect labels are semantically aligned with the sentence and ESG pillar.",
            "if_underperforming": "Aspect labels become noisy and distribution charts can overstate themes that are not actually present.",
            "likely_reason_if_weak": "Free-text aspect generation may be too unconstrained or the taxonomy may not cover Indonesian expressions.",
            "next_action": "Sample 30-50 records and manually verify aspect-to-sentence alignment.",
        })
    elif "tone x esg pillar" in lower or "tone × esg pillar" in lower:
        detail.update({
            "what_it_does": "Shows how ESG tone categories distribute across Environmental, Social, and Governance pillars.",
            "expected_metric": "Crosstab counts and percentages for pillar by tone, with enough records per cell.",
            "if_yes_or_good": "Each major pillar has enough records to support tone comparisons, ideally at least 30 per important subgroup.",
            "if_underperforming": "A zero or tiny cell means the thesis cannot compare that subgroup reliably.",
            "likely_reason_if_weak": "The dataset may over-sample environmental pages and under-sample social/governance content.",
            "next_action": "Target Social and Governance pages for additional extraction, not just more records in general.",
        })
    elif "bilingual tone asymmetry" in lower:
        detail.update({
            "what_it_does": "Tests whether Indonesian and English disclosures show different tone patterns.",
            "expected_metric": "Tone proportions by language, difference in proportions, confidence interval, and significance test.",
            "if_yes_or_good": "The language difference is large enough and powered enough to be reported as a thesis finding.",
            "if_underperforming": "The observed difference may be sampling noise or caused by different documents rather than language.",
            "likely_reason_if_weak": "Language may be confounded with company, report section, or prompt template.",
            "next_action": "Run a two-proportion test and control/check document and prompt composition.",
        })
    elif "sentiment score distribution" in lower:
        detail.update({
            "what_it_does": "Checks whether sentiment scores behave consistently with tone categories.",
            "expected_metric": "Mean, median, spread, and distribution of sentiment_score by tone.",
            "if_yes_or_good": "Outcome/action/commitment tones show interpretable sentiment differences.",
            "if_underperforming": "Sentiment may not be calibrated, or tone and sentiment may be measuring different constructs.",
            "likely_reason_if_weak": "LLM-generated sentiment scores may not be anchored to a stable rubric.",
            "next_action": "Plot distributions and compare against expert sentiment labels for a small sample.",
        })
    elif "llm labels" in lower:
        detail.update({
            "what_it_does": "Provides weak-label counts from the LLM extraction stage.",
            "expected_metric": "Counts and percentages for tone, aspect, pillar, sentiment, and confidence fields.",
            "if_yes_or_good": "Counts are balanced enough and validated enough to support descriptive ABSA claims.",
            "if_underperforming": "Weak labels may reflect prompt/model bias more than true disclosure patterns.",
            "likely_reason_if_weak": "No expert gold labels yet; distribution may be shaped by prompt wording.",
            "next_action": "Validate a stratified sample against expert labels before reporting strong accuracy claims.",
        })
    elif "language-tagged" in lower:
        detail.update({
            "what_it_does": "Separates records by Indonesian/English language for bilingual comparison.",
            "expected_metric": "Language counts, language proportions, and language x tone/aspect crosstabs.",
            "if_yes_or_good": "Both languages have enough records for comparison and are not fully confounded with one document.",
            "if_underperforming": "Language effects may actually be document, company, or section effects.",
            "likely_reason_if_weak": "Reports may not be evenly bilingual, or one language may dominate specific companies/pages.",
            "next_action": "Check language distribution by filename/document and rebalance if necessary.",
        })
    elif "expert-annotated" in lower or "gold" in lower:
        detail.update({
            "what_it_does": "Creates the independent reference labels needed to evaluate LLM/ABSA quality.",
            "expected_metric": "Cohen kappa between annotators, precision, recall, and F1 against gold labels.",
            "if_yes_or_good": "Annotators agree and model labels reach acceptable F1, making taxonomy claims credible.",
            "if_underperforming": "Low agreement means the taxonomy is unclear; low F1 means the LLM labels are not reliable enough for strong claims.",
            "likely_reason_if_weak": "Tone/aspect definitions may be ambiguous, or annotators may lack a precise codebook.",
            "next_action": "Build a codebook, label 30-50 records with two annotators, adjudicate disagreements, then compute metrics.",
        })
    elif "taxonomy" in lower or "ontology" in lower or "non-standard" in lower:
        detail.update({
            "what_it_does": "Normalizes free-text aspect labels into a stable taxonomy.",
            "expected_metric": "Ontology coverage, number of unmapped labels, mapping accuracy, and before/after aspect counts.",
            "if_yes_or_good": "Most aspect labels map cleanly to canonical ESG categories in both languages.",
            "if_underperforming": "Charts fragment across many near-duplicate labels and bilingual comparison becomes unstable.",
            "likely_reason_if_weak": "The LLM may generate many natural-language aspect variants instead of choosing from a controlled list.",
            "next_action": "Create a canonical aspect dictionary and map free-text aspects to it.",
        })
    elif "precision/recall/f1" in lower:
        detail.update({
            "what_it_does": "Measures how accurately model-generated labels match expert labels.",
            "expected_metric": "Precision, recall, and F1 by class, plus macro-F1 for overall performance.",
            "if_yes_or_good": "Per-class F1 is acceptable and no major category collapses.",
            "if_underperforming": "The model may over-predict common classes, miss rare classes, or confuse similar tones/aspects.",
            "likely_reason_if_weak": "Class imbalance, weak prompt definitions, or ambiguous ESG language can lower F1.",
            "next_action": "Compute F1 after expert annotation; inspect confusion matrix for systematic errors.",
        })
    elif "inter-annotator" in lower or "kappa" in lower:
        detail.update({
            "what_it_does": "Measures whether humans agree on the taxonomy before judging model performance.",
            "expected_metric": "Cohen kappa by aspect, pillar, tone, and sentiment.",
            "if_yes_or_good": "Kappa at or above about 0.70 means the labeling scheme is reasonably reliable.",
            "if_underperforming": "If humans cannot agree, model errors may reflect an unclear taxonomy rather than bad model behavior.",
            "likely_reason_if_weak": "Definitions may overlap, examples may be missing, or labels may be too granular.",
            "next_action": "Revise the annotation codebook and run a second calibration round.",
        })
    elif "climatebert scores" in lower or "full local" in lower:
        detail.update({
            "what_it_does": "Completes the actual local ClimateBERT/ESGBERT comparison instead of relying on a few remote examples.",
            "expected_metric": "Prediction coverage by model, label distribution, confidence distribution, and processed/not-processed counts.",
            "if_yes_or_good": "All valid sentences have saved predictions for selected models in climatebert_predictions.",
            "if_underperforming": "RQ3 remains incomplete because model comparison is not yet dataset-wide.",
            "likely_reason_if_weak": "Runs may be interrupted, model loading may fail, or worker shards may not cover all rows.",
            "next_action": "Use page 02 with auto-save and continue-leftover mode; verify coverage in page 03.",
        })
    elif "row-wise" in lower or "agreement" in lower:
        detail.update({
            "what_it_does": "Tests whether LLM tone labels and ClimateBERT labels agree at the sentence level.",
            "expected_metric": "Agreement percentage, mapped-label crosstab, and Cohen kappa.",
            "if_yes_or_good": "Agreement is interpretable and supports a relationship between ABSA tone and climate classification.",
            "if_underperforming": "The two systems may be measuring different constructs or the mapping may be too crude.",
            "likely_reason_if_weak": "ClimateBERT labels are task-specific while ABSA tone is rhetorical/semantic.",
            "next_action": "Define a transparent mapping from ClimateBERT outputs to tone-relevant categories and compute agreement.",
        })
    elif "cohen" in lower:
        detail.update({
            "what_it_does": "Quantifies agreement beyond chance.",
            "expected_metric": "Cohen kappa, with interpretation bands and confidence intervals if possible.",
            "if_yes_or_good": "Kappa is positive and substantively meaningful, supporting stable agreement.",
            "if_underperforming": "Low kappa means agreement is weak after accounting for base-rate effects.",
            "likely_reason_if_weak": "Class imbalance, incompatible label spaces, or noisy labels can depress kappa.",
            "next_action": "Inspect the confusion matrix and class distribution before interpreting kappa.",
        })
    elif "schema drift" in lower:
        detail.update({
            "what_it_does": "Detects cases where the model outputs values in the wrong field or breaks the expected schema.",
            "expected_metric": "Schema drift count and rate by model, prompt, and document.",
            "if_yes_or_good": "Drift is rare and isolated to known bad configurations.",
            "if_underperforming": "High drift means downstream metrics may be corrupted by invalid fields.",
            "likely_reason_if_weak": "Prompt schema may be underspecified or the model may ignore formatting constraints.",
            "next_action": "Add schema validation and revise prompts that produce drift.",
        })
    elif "missing tone" in lower:
        detail.update({
            "what_it_does": "Finds records where the model failed to assign the key ABSA tone field.",
            "expected_metric": "Missing-tone count/rate by model, prompt, document, language, and pillar.",
            "if_yes_or_good": "Missing tone is near zero for stable configurations.",
            "if_underperforming": "Tone distributions become biased because some sentences disappear from tone analysis.",
            "likely_reason_if_weak": "Prompt ambiguity, governance-heavy text, or model/schema failure may cause missing tone.",
            "next_action": "Trace missing-tone rows to prompt/model combinations and fix the extraction schema.",
        })
    elif "root cause" in lower:
        detail.update({
            "what_it_does": "Attributes failures to specific model, prompt, document, or language conditions.",
            "expected_metric": "Error rate grouped by model x prompt and document x language.",
            "if_yes_or_good": "Failure clusters are identifiable and fixable.",
            "if_underperforming": "If failures are diffuse, the whole pipeline or taxonomy may need redesign.",
            "likely_reason_if_weak": "Multiple failure modes may overlap: OCR noise, prompt design, model limitations, and taxonomy ambiguity.",
            "next_action": "Create grouped error tables and inspect top failing combinations first.",
        })
    elif "artifact" in lower or "streamlit" in lower or "prompt template" in lower or "replication" in lower or "reproducibility" in lower:
        detail.update({
            "what_it_does": "Supports auditability: whether another person can trace and reproduce the thesis outputs.",
            "expected_metric": "Artifact count, prompt version coverage, model version coverage, rerun success, and replication notes.",
            "if_yes_or_good": "Every result links to code, input data, prompt, model, and saved output.",
            "if_underperforming": "The thesis may be hard to verify even if the analysis is technically correct.",
            "likely_reason_if_weak": "Outputs may be scattered, prompt versions undocumented, or model paths not recorded.",
            "next_action": "Create a reproducibility checklist and artifact registry that points to each source file and dashboard page.",
        })
    elif "balanced model" in lower:
        detail.update({
            "what_it_does": "Ensures model/prompt comparisons are fair rather than confounded by different documents or sample sizes.",
            "expected_metric": "Balanced counts by model, prompt, document, language, and tone.",
            "if_yes_or_good": "Each compared model/prompt has matched records from the same documents or comparable strata.",
            "if_underperforming": "Observed differences may reflect sample composition rather than model/prompt behavior.",
            "likely_reason_if_weak": "Some prompts/models may have been run on different documents or with unequal row counts.",
            "next_action": "Build a matched comparison matrix and rerun missing cells.",
        })
    elif "few-shot" in lower:
        detail.update({
            "what_it_does": "Checks whether the few-shot prompt has enough observations for comparison.",
            "expected_metric": "Few-shot row count and power for prompt comparison.",
            "if_yes_or_good": "Few-shot n reaches at least 30, preferably 40+, so comparisons are not severely underpowered.",
            "if_underperforming": "Few-shot performance claims are not statistically defensible.",
            "likely_reason_if_weak": "Few-shot runs may have been limited or produced fewer usable records.",
            "next_action": "Run additional few-shot extractions on matched documents.",
        })
    elif "coefficient of variation" in lower or "prompt family" in lower or "per-document" in lower:
        detail.update({
            "what_it_does": "Measures output stability across prompt families or documents.",
            "expected_metric": "Coefficient of variation, range, standard deviation, and per-document prompt gaps.",
            "if_yes_or_good": "Variation is quantified and either low enough to trust or reducible through ensemble methods.",
            "if_underperforming": "High variation means results depend strongly on prompt choice.",
            "likely_reason_if_weak": "Prompts may emphasize different evidence types or induce different tone interpretations.",
            "next_action": "Compare matched documents across prompts and test majority-vote stabilization.",
        })
    elif "ensemble" in lower or "majority" in lower:
        detail.update({
            "what_it_does": "Tests whether combining prompts/models improves stability.",
            "expected_metric": "Majority-vote agreement, variance reduction, and changed-label rate.",
            "if_yes_or_good": "Ensemble output reduces prompt variance without hiding systematic errors.",
            "if_underperforming": "Ensemble may simply average incompatible outputs and reduce interpretability.",
            "likely_reason_if_weak": "Base models/prompts may disagree for principled reasons, not random noise.",
            "next_action": "Run ensemble simulation on matched PTBA or other multi-prompt documents.",
        })

    return detail


def build_rq_detail_rows(items: list[dict]) -> pd.DataFrame:
    rows = []
    for item in items:
        for status, key in [("Available", "have"), ("Partial", "partial"), ("Needed", "need")]:
            for entry in item[key]:
                detail = detail_for_item(item["rq"], item["theme"], status, entry)
                rows.append({
                    "rq": item["rq"],
                    "theme": item["theme"],
                    "status": status,
                    "status_meaning": status_interpretation(status),
                    "item": entry,
                    "what_it_does": detail["what_it_does"],
                    "expected_metric": detail["expected_metric"],
                    "if_yes_or_good": detail["if_yes_or_good"],
                    "if_underperforming": detail["if_underperforming"],
                    "likely_reason_if_weak": detail["likely_reason_if_weak"],
                    "next_action": detail["next_action"],
                    "priority": item["priority"],
                })
    return pd.DataFrame(rows)


with st.sidebar:
    st.header("Filters")
    priority_filter = st.multiselect(
        "Priority",
        ["Critical", "High", "Medium", "Important"],
        default=["Critical", "High", "Medium", "Important"],
    )
    rq_filter = st.multiselect("Research Questions", [item["rq"] for item in RQ_DATA])
    view_mode = st.radio(
        "Detail view",
        ["Matrix", "Question Cards", "Metrics", "Detailed Explanation"],
        horizontal=False,
    )


filtered = [
    item for item in RQ_DATA
    if item["priority"] in priority_filter and (not rq_filter or item["rq"] in rq_filter)
]
summary = status_counts(filtered)
detail_df = build_rq_detail_rows(filtered)

cols = st.columns(4)
cols[0].metric("Research questions", len(filtered))
cols[1].metric("Available evidence items", int(summary["available"].sum()) if not summary.empty else 0)
cols[2].metric("Partial evidence items", int(summary["partial"].sum()) if not summary.empty else 0)
cols[3].metric("Open needs", int(summary["needed"].sum()) if not summary.empty else 0)
st.caption(f"Existing data: `{EXISTING_DATA_PATH}`")
st.caption(f"Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")

tab_overview, tab_details, tab_guide, tab_missing, tab_mermaid, tab_plan, tab_source = st.tabs([
    "Overview",
    "RQ Details",
    "Table Guide",
    "Missing Work Process",
    "Mermaid Preview",
    "Analysis Plan",
    "Source HTML",
])

with tab_overview:
    if summary.empty:
        st.info("No RQs match the selected filters.")
    else:
        chart_df = summary.set_index("rq")[["available", "partial", "needed"]]
        st.subheader("Evidence Readiness by RQ")
        st.bar_chart(chart_df)
        st.dataframe(summary, use_container_width=True)

with tab_details:
    if view_mode == "Matrix":
        st.write(
            "This table is the operational RQ evidence checklist. Each row is one evidence item. "
            "`Available` means usable evidence exists, `Partial` means the evidence is promising but not fully defensible, "
            "and `Needed` means a missing metric or validation step must be completed."
        )
        st.dataframe(detail_df, use_container_width=True, height=620)

        if not detail_df.empty:
            selected_row = st.selectbox(
                "Explain row",
                detail_df.index,
                format_func=lambda idx: f"{detail_df.loc[idx, 'rq']} · {detail_df.loc[idx, 'status']} · {detail_df.loc[idx, 'item'][:90]}",
            )
            row = detail_df.loc[selected_row]
            st.session_state["linked_rq"] = row["rq"]
            st.session_state["linked_detail_row"] = int(selected_row)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Item:** {row['item']}")
                st.markdown(f"**Status meaning:** {row['status_meaning']}")
                st.markdown(f"**What it does:** {row['what_it_does']}")
                st.markdown(f"**Expected metric:** {row['expected_metric']}")
            with c2:
                st.markdown(f"**If yes / good:** {row['if_yes_or_good']}")
                st.markdown(f"**If underperforming:** {row['if_underperforming']}")
                st.markdown(f"**Likely reason if weak:** {row['likely_reason_if_weak']}")
                st.markdown(f"**Next action:** {row['next_action']}")

            st.subheader("Linked Row Diagram")
            linked_row_code = build_row_detail_mermaid(row)
            render_mermaid(linked_row_code, height=360)
            st.code(linked_row_code, language="mermaid")

    elif view_mode == "Question Cards":
        for item in filtered:
            st.subheader(f"{item['rq']} · {item['theme']}")
            st.write(item["question"])
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Available**")
                for entry in item["have"]:
                    st.write(f"- {entry}")
            with c2:
                st.markdown("**Partial**")
                for entry in item["partial"]:
                    st.write(f"- {entry}")
            with c3:
                st.markdown("**Needed**")
                for entry in item["need"]:
                    st.write(f"- {entry}")
            st.divider()

    elif view_mode == "Metrics":
        metric_rows = []
        for item in filtered:
            for name, value, context in item["metrics"]:
                metric_rows.append({
                    "rq": item["rq"],
                    "theme": item["theme"],
                    "metric": name,
                    "value": value,
                    "context": context,
                })
        st.dataframe(pd.DataFrame(metric_rows), use_container_width=True, height=620)

    else:
        guide = RQ_TABLE_GUIDE
        if rq_filter:
            guide = guide[guide["rq"].isin(rq_filter)]
        st.dataframe(guide, use_container_width=True, height=620)

with tab_guide:
    st.subheader("How to Interpret the Tables")
    st.dataframe(TABLE_EXPLANATIONS, use_container_width=True, height=300)

    st.subheader("Expected Metrics and Interpretation by RQ")
    guide = RQ_TABLE_GUIDE.copy()
    if rq_filter:
        guide = guide[guide["rq"].isin(rq_filter)]
    st.dataframe(guide, use_container_width=True, height=620)

    selected_guide_rq = st.selectbox("Detailed explanation for RQ", guide["rq"].tolist())
    guide_row = guide[guide["rq"] == selected_guide_rq].iloc[0]
    st.markdown(f"**What it does:** {guide_row['what_this_table_does']}")
    st.markdown(f"**Expected metrics:** {guide_row['expected_metrics']}")
    st.markdown(f"**If performing well:** {guide_row['if_performing_well']}")
    st.markdown(f"**If underperforming:** {guide_row['if_underperforming']}")
    st.markdown(f"**How to process:** {guide_row['how_to_process']}")

with tab_missing:
    st.subheader("How to Process the Missing Research-Question Evidence")
    st.write(
        "The page treats the existing parsed dataset as the main source of LLM ESG evidence, "
        "and the ClimateBERT prediction folder as the source of local-model comparison evidence."
    )
    st.dataframe(MISSING_WORK, use_container_width=True, height=420)

    selected_missing_rq = st.selectbox("Explain one RQ gap", MISSING_WORK["rq"].tolist())
    row = MISSING_WORK[MISSING_WORK["rq"] == selected_missing_rq].iloc[0]
    st.markdown(f"**Missing piece:** {row['missing_piece']}")
    st.markdown(f"**Process:** {row['process']}")
    st.markdown(f"**Primary source:** `{row['primary_source']}`")
    st.markdown(f"**Output metric:** {row['output_metric']}")

with tab_mermaid:
    st.subheader("Linked RQ Evidence Diagram")
    rq_options = detail_df["rq"].drop_duplicates().tolist() if not detail_df.empty else [item["rq"] for item in RQ_DATA]
    default_linked_rq = st.session_state.get("linked_rq", rq_options[0] if rq_options else "RQ1")
    default_index = rq_options.index(default_linked_rq) if default_linked_rq in rq_options else 0
    linked_rq = st.selectbox(
        "Choose RQ to diagram from the RQ Details table",
        rq_options,
        index=default_index,
    )
    linked_code = build_rq_evidence_mermaid(linked_rq, detail_df)
    render_mermaid(linked_code, height=520)
    st.code(linked_code, language="mermaid")

    st.subheader("Full Research Question Evidence Map")
    render_mermaid(RQ_MERMAID, height=520)
    st.code(RQ_MERMAID, language="mermaid")

    st.subheader("Workflow Diagram")
    render_mermaid(PIPELINE_MERMAID, height=430)
    st.code(PIPELINE_MERMAID, language="mermaid")

    st.subheader("Missing Evidence Process")
    render_mermaid(MISSING_PROCESS_MERMAID, height=430)
    st.code(MISSING_PROCESS_MERMAID, language="mermaid")

with tab_plan:
    st.subheader("Prioritized Next Analyses")
    plan = ANALYSIS_PLAN[ANALYSIS_PLAN["urgency"].isin(priority_filter)]
    st.dataframe(plan, use_container_width=True)
    if not plan.empty:
        st.bar_chart(plan["answers"].str.get_dummies(sep=", ").sum().sort_values(ascending=False))

with tab_source:
    st.caption(f"Source: `{SOURCE_HTML}`")
    st.info("This Streamlit page is a native visualization distilled from the HTML thesis benchmark artifact.")
