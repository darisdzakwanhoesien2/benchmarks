from __future__ import annotations

from pathlib import Path
import hashlib
import json

import pandas as pd
import streamlit.components.v1 as components


PAGE_DIR = Path(__file__).resolve().parent
BENCHMARK_ROOT = PAGE_DIR.parent
IMAGE_MANIFEST_PATH = BENCHMARK_ROOT / "results" / "image_outputs_archive" / "image_outputs_explanations.json"


RESEARCH_QUESTIONS = [
    {
        "rq": "RQ1",
        "theme": "Pipeline feasibility",
        "question": "How can sustainability reports be transformed into sentence-level ESG records that are traceable enough for ABSA?",
        "short_answer": "The current dashboards support a feasibility claim: parsed records can be inspected, filtered, and traced through the dashboard workflow, but OCR and segmentation quality still need manual measurement.",
        "evidence_status": "Partial",
        "chapter4_result": "A working PDF/markdown-to-structured-record workflow exists, with dashboard pages for parsed ESG records, provenance review, model/prompt coverage, and record-level inspection.",
        "chapter5_discussion": "RQ1 should be worded as a pipeline feasibility result rather than a fully validated extraction-accuracy result. The strongest current contribution is auditability: the workflow makes extraction outputs visible and reviewable.",
        "conclusion": "The project demonstrates a usable and auditable ESG extraction pipeline, while final OCR and segmentation accuracy remain future validation work.",
        "supporting_pages": [
            "esg_dashboard_new_0_new.py",
            "esg_dashboard_new_8_new.py",
            "04_Research_Questions_Visualizer.py",
        ],
        "supporting_images": ["Interface evidence"],
        "available_evidence": [
            "Parsed ESG records can be loaded into Streamlit dashboards.",
            "Dashboard filters expose document, page, model, prompt, and extracted-field coverage.",
            "Existing page inventory separates empirical analysis pages from utility/demo pages.",
        ],
        "partial_evidence": [
            "Provenance is visible in dashboard views, but not yet formalized as an extraction-quality score.",
        ],
        "needed_evidence": [
            "Manual OCR reference pages for CER/WER.",
            "Sentence-boundary precision/recall.",
            "Table and figure extraction accuracy checks.",
        ],
    },
    {
        "rq": "RQ2",
        "theme": "ESG categorization",
        "question": "How should ESG aspects, pillars, sentiment, and tone be categorized for bilingual ABSA?",
        "short_answer": "The current results show useful descriptive category structure, especially for tone, aspect, pillar, and sentiment distributions, but these labels should be described as weak/model-assisted until expert annotation is complete.",
        "evidence_status": "Partial",
        "chapter4_result": "Aspect, sentiment, tone, pillar, and Sankey dashboards show the distributional structure of ESG disclosures and reveal sparse Social-pillar evidence and non-standard aspect labels.",
        "chapter5_discussion": "RQ2 is currently strongest as a descriptive taxonomy and imbalance analysis. It can support discussion of category design and data coverage, but precision/recall/F1 claims require expert labels and bilingual ontology normalization.",
        "conclusion": "The thesis can conclude that the dashboard identifies a workable ESG ABSA categorization structure, while validated classification quality requires a gold-standard annotation layer.",
        "supporting_pages": [
            "esg_dashboard_new_Data Distribution.py",
            "esg_dashboard_new_Data_New_Distribution.py",
            "esg_dashboard_new_Tone_Distribution.py",
            "esg_dashboard_new_Sankey.py",
            "esg_dashboard_new_01_Aspects_Raw.py",
            "esg_dashboard_new_02_Aspects_Clustered.py",
            "esg_dashboard_new_03_Aspect_Comparison.py",
            "zz_aspect_clusters.py",
            "absa_metrics_visualization.py",
        ],
        "supporting_images": [
            "ABSA distribution",
            "Aspect and tone analysis",
            "Taxonomy evidence",
        ],
        "available_evidence": [
            "Tone, sentiment, aspect, and pillar distributions are visualized.",
            "Aspect clustering pages show before/after taxonomy normalization needs.",
            "Sankey-style views make aspect-to-sentiment-to-tone flows interpretable.",
        ],
        "partial_evidence": [
            "ABSA metrics exist, but label-space alignment and gold labels are incomplete.",
        ],
        "needed_evidence": [
            "30-50 record expert-annotated stratified sample.",
            "Inter-annotator agreement, ideally Cohen kappa >= 0.70.",
            "Bilingual aspect ontology mapping.",
        ],
    },
    {
        "rq": "RQ3",
        "theme": "ClimateBERT comparison",
        "question": "How do tone-based ABSA outputs compare with ClimateBERT-style climate classifications?",
        "short_answer": "The current evidence is exploratory: ClimateBERT integration and metric pages exist, but full local inference and explicit label mapping are needed before agreement metrics can be treated as final.",
        "evidence_status": "Needed",
        "chapter4_result": "ClimateBERT pages and ABSA integration pages provide the machinery for batch inference, confidence review, label distributions, confusion matrices, and ABSA-to-ClimateBERT comparison.",
        "chapter5_discussion": "Low or zero scores should be interpreted carefully. They may reflect incompatible label spaces or incomplete prediction coverage rather than simple model failure.",
        "conclusion": "ClimateBERT comparison is a central next validation layer; it is not yet a closed result unless local predictions cover all valid sentences with documented mappings.",
        "supporting_pages": [
            "0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py",
            "0_0_ClimateBERT_4_Model_Analysis.py",
            "0_0_ClimateBERT_5_Model_Deep_Explorer.py",
            "0_0_ClimateBERT_6_Model_Overview_All.py",
            "0_0_ClimateBERT_7_Full_Model_Visualization.py",
            "0_ClimateBERT_Commitment_Distribution.py",
            "1_ABSA_Integration.py",
            "absa_metrics_visualization.py",
        ],
        "supporting_images": [
            "ClimateBERT comparison",
            "Model metric evidence",
        ],
        "available_evidence": [
            "ClimateBERT processing and visualization pages are present.",
            "ABSA metrics visualization can display saved model results.",
            "Local ClimateControversyBert path is now supported in the metrics workflow.",
        ],
        "partial_evidence": [
            "Some comparison artifacts exist, but coverage and label mapping still need review.",
        ],
        "needed_evidence": [
            "Run local ClimateBERT models over every valid sentence.",
            "Define label mapping rules before kappa/F1 calculation.",
            "Join predictions back to sentence-level ABSA rows.",
        ],
    },
    {
        "rq": "RQ4",
        "theme": "Diagnostics",
        "question": "What weaknesses arise in ABSA extraction outputs, and how can they be detected and quantified?",
        "short_answer": "The dashboard already supports diagnostic review through confusion matrices, missing-label checks, taxonomy gaps, and error-oriented tables, but manual error typing is still needed.",
        "evidence_status": "Partial",
        "chapter4_result": "Metric pages, confusion matrices, and taxonomy pages expose where predictions fail, where labels are missing, and where aspect vocabularies drift.",
        "chapter5_discussion": "The diagnostic contribution is practical: it separates schema drift, taxonomy mismatch, missing labels, class imbalance, and evaluation mismatch instead of treating errors as one generic failure.",
        "conclusion": "The thesis can claim a useful diagnostic framework, while quantified error rates require manual error labels.",
        "supporting_pages": [
            "absa_metrics_comparison.py",
            "absa_metrics_comparison_mac.py",
            "absa_metrics_visualization.py",
            "esg_dashboard_new_0_Metric_Analysis.py",
            "test_models.py",
            "zz_aspect_clusters.py",
        ],
        "supporting_images": [
            "Model metric evidence",
            "Taxonomy evidence",
        ],
        "available_evidence": [
            "Confusion matrices and metric dashboards expose label-level failures.",
            "Aspect-cluster pages expose uncontrolled taxonomy drift.",
            "Metrics pages separate category, sentiment, and tone behavior.",
        ],
        "partial_evidence": [
            "Diagnostic categories are visible, but not all errors have manual labels.",
        ],
        "needed_evidence": [
            "Manual `error_type` labels on sampled records.",
            "Error summaries by model, prompt, document, language, pillar, and page.",
        ],
    },
    {
        "rq": "RQ5",
        "theme": "Reproducibility",
        "question": "How can documentation and visualization practices improve reproducibility and auditability of ESG ABSA experiments?",
        "short_answer": "The current implementation strongly supports reproducibility through shared RQ pages, archived images, JSON/Markdown explanations, and explicit page-to-RQ mapping.",
        "evidence_status": "Available",
        "chapter4_result": "The image archive, manifest, Markdown explanations, page inventory, and thesis dashboard pages create a traceable evidence layer for the project.",
        "chapter5_discussion": "RQ5 is one of the strongest current claims because outputs now have stable paths, explanations, RQ links, and thesis-use notes.",
        "conclusion": "The project contributes an auditable Streamlit-based documentation workflow for ESG ABSA research.",
        "supporting_pages": [
            "Research_Questions_Dashboard.py",
            "04_Research_Questions_Visualizer.py",
            "06_Chapter_4_Results.py",
            "07_Chapter_5_Discussion.py",
            "10_Chapter_6_Conclusion.py",
            "_rq_thesis_content.py",
        ],
        "supporting_images": [
            "Interface evidence",
            "Documentation evidence",
        ],
        "available_evidence": [
            "Image outputs are archived with JSON and Markdown explanations.",
            "Pages are mapped to research questions and chapter roles.",
            "Chapter result, discussion, and conclusion pages use shared content.",
        ],
        "partial_evidence": [
            "A final rerun checklist and dependency/version capture would make replication stronger.",
        ],
        "needed_evidence": [
            "Formal replication protocol.",
            "Environment and model-version capture for final thesis submission.",
        ],
    },
    {
        "rq": "RQ6",
        "theme": "Stability",
        "question": "How stable are ABSA outputs across models and prompts, and what ensemble strategies improve reliability?",
        "short_answer": "The current system can inspect model/prompt variation and ensemble-style outputs, but balanced model-by-prompt-by-document coverage is still required for strong stability claims.",
        "evidence_status": "Partial",
        "chapter4_result": "Tone distribution, model comparison, ClimateBERT overview, and ensemble/confusion-matrix artifacts support stability analysis by exposing variation across labels and model settings.",
        "chapter5_discussion": "RQ6 should be framed cautiously until matched runs exist. Current outputs are valuable for identifying instability and designing a balanced comparison matrix.",
        "conclusion": "The project shows how stability can be audited, while final cross-model claims require balanced matched observations.",
        "supporting_pages": [
            "esg_dashboard_new_Tone_Distribution.py",
            "esg_dashboard_new_Sankey.py",
            "ABSA_Model_Comparison.py",
            "0_0_ClimateBERT_6_Model_Overview_All.py",
            "0_0_ClimateBERT_7_Full_Model_Visualization.py",
            "05_Sample_Size_Reasoning.py",
        ],
        "supporting_images": [
            "Model metric evidence",
            "ABSA distribution",
            "ClimateBERT comparison",
        ],
        "available_evidence": [
            "Model and prompt comparison pages exist.",
            "Sample-size page defines matched-cell requirements.",
            "Archived confusion matrices and distribution images support stability discussion.",
        ],
        "partial_evidence": [
            "Current runs are not fully balanced across model, prompt, and document.",
        ],
        "needed_evidence": [
            "Balanced model x prompt x document matrix.",
            "Cross-model agreement metrics.",
            "Majority-vote or ensemble stability simulation on matched cells.",
        ],
    },
]


CHAPTER4_RESULTS = [
    {
        "section": "4.1 Pipeline and evidence infrastructure",
        "rq": "RQ1, RQ5",
        "result": "The project now has an auditable evidence infrastructure: parsed ESG dashboards, image archive, page inventory, and chapter-specific Streamlit pages.",
        "supporting_pages": "esg_dashboard_new_0_new.py; 04_Research_Questions_Visualizer.py; Research_Questions_Dashboard.py",
        "use_in_results": "Present this as the foundation for all later ABSA analysis.",
    },
    {
        "section": "4.2 ESG category and tone distributions",
        "rq": "RQ2",
        "result": "Distribution pages reveal tone, sentiment, aspect, and pillar patterns that make ESG ABSA behavior inspectable.",
        "supporting_pages": "esg_dashboard_new_Data Distribution.py; esg_dashboard_new_Tone_Distribution.py; esg_dashboard_new_Sankey.py",
        "use_in_results": "Report descriptive distribution patterns and identify sparse categories.",
    },
    {
        "section": "4.3 ClimateBERT and ABSA model comparison",
        "rq": "RQ3, RQ6",
        "result": "ClimateBERT and ABSA metric pages provide comparison artifacts, but final agreement claims need complete local inference and label mapping.",
        "supporting_pages": "absa_metrics_visualization.py; 1_ABSA_Integration.py; 0_0_ClimateBERT_7_Full_Model_Visualization.py",
        "use_in_results": "Present current metrics as exploratory comparison and validation-readiness evidence.",
    },
    {
        "section": "4.4 Error diagnostics and taxonomy gaps",
        "rq": "RQ4",
        "result": "Metric, confusion-matrix, and taxonomy pages show where the pipeline can detect missing labels, confusion, schema drift, and non-standard aspects.",
        "supporting_pages": "absa_metrics_comparison.py; zz_aspect_clusters.py; esg_dashboard_new_0_Metric_Analysis.py",
        "use_in_results": "Report diagnostic categories and remaining manual labeling requirements.",
    },
    {
        "section": "4.5 Sample-size and claim readiness",
        "rq": "RQ2, RQ3, RQ6",
        "result": "The sample-size reasoning page defines which claims are supported by current data and which require larger or better-balanced samples.",
        "supporting_pages": "05_Sample_Size_Reasoning.py",
        "use_in_results": "Use this to prevent over-claiming and to justify future-data targets.",
    },
]


GENERAL_DISCUSSION = [
    "The strongest current contribution is not a single high metric. It is a complete audit workflow that connects research questions, dashboards, saved visual outputs, metrics, and thesis-ready interpretation.",
    "The results are strongest for feasibility, traceability, descriptive distributions, and diagnostics. They are weaker for final accuracy claims because expert annotation, full local ClimateBERT coverage, and balanced model/prompt runs are still needed.",
    "This means the thesis should frame the system as a reproducible ESG ABSA framework and validation scaffold, with selected exploratory findings, rather than as a final production classifier.",
]


CONTRIBUTIONS = [
    "A bilingual ESG ABSA dashboard workflow that links extracted records to visual, metric, and discussion evidence.",
    "A research-question mapping layer that separates available, partial, and needed evidence for RQ1-RQ6.",
    "An archived image-output manifest with explanations, RQ links, and thesis-use notes.",
    "A chapter structure that turns implementation outputs into Chapter 4 results, Chapter 5 discussion, and Chapter 6 conclusion text.",
]


LIMITATIONS = [
    "Expert annotation and inter-annotator agreement are not yet complete.",
    "ClimateBERT comparison needs full local inference coverage and explicit label-space mapping.",
    "Stability claims require balanced model x prompt x document cells.",
    "OCR and sentence-segmentation quality still need manual validation.",
]


FINAL_CONCLUSION = (
    "This project demonstrates a defensible, auditable ESG ABSA research workflow. "
    "It can support thesis claims about pipeline feasibility, evidence traceability, descriptive ESG category patterns, diagnostics, and sample-size reasoning. "
    "Stronger claims about classification accuracy, ClimateBERT agreement, and generalizable stability should be reserved for the next validation layer: expert-labeled records, complete local model predictions, and balanced cross-model/cross-prompt experiments."
)


CHAPTER_FLOW_MERMAID = """
flowchart LR
  RQ["Research Questions<br/>RQ1-RQ6"] --> C4["Chapter 4<br/>Results"]
  C4 --> C5["Chapter 5<br/>Discussion"]
  C5 --> C6["Chapter 6<br/>Conclusion"]

  RQ1["RQ1 Pipeline"] --> C4
  RQ2["RQ2 Categorization"] --> C4
  RQ3["RQ3 ClimateBERT"] --> C4
  RQ4["RQ4 Diagnostics"] --> C4
  RQ5["RQ5 Reproducibility"] --> C4
  RQ6["RQ6 Stability"] --> C4

  C4 --> EVID["Pages, metrics,<br/>images, tables"]
  EVID --> C5
  C5 --> CLAIMS["Claim strength:<br/>Available / Partial / Needed"]
  CLAIMS --> C6
"""


def research_questions_df() -> pd.DataFrame:
    return pd.DataFrame(RESEARCH_QUESTIONS)


def chapter4_results_df() -> pd.DataFrame:
    return pd.DataFrame(CHAPTER4_RESULTS)


def evidence_rows_df() -> pd.DataFrame:
    rows = []
    for rq in RESEARCH_QUESTIONS:
        for status, key in [
            ("Available", "available_evidence"),
            ("Partial", "partial_evidence"),
            ("Needed", "needed_evidence"),
        ]:
            for item in rq[key]:
                rows.append(
                    {
                        "rq": rq["rq"],
                        "theme": rq["theme"],
                        "status": status,
                        "evidence": item,
                    }
                )
    return pd.DataFrame(rows)


def page_mapping_df() -> pd.DataFrame:
    rows = []
    for rq in RESEARCH_QUESTIONS:
        for page in rq["supporting_pages"]:
            rows.append(
                {
                    "rq": rq["rq"],
                    "theme": rq["theme"],
                    "page": page,
                    "evidence_status": rq["evidence_status"],
                }
            )
    return pd.DataFrame(rows)


def load_image_manifest(path: Path = IMAGE_MANIFEST_PATH) -> tuple[dict, pd.DataFrame]:
    if not path.exists():
        return {"images": [], "image_count": 0, "category_counts": {}}, pd.DataFrame()
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("images", [])
    df = pd.DataFrame(rows)
    if df.empty:
        return payload, df
    df["archived_absolute_path"] = df["archived_path"].apply(lambda p: str((BENCHMARK_ROOT / p).resolve()))
    df["research_question_links_text"] = df["research_question_links"].apply(
        lambda values: ", ".join(values) if isinstance(values, list) else str(values)
    )
    return payload, df


def images_for_rq(image_df: pd.DataFrame, rq: str) -> pd.DataFrame:
    if image_df.empty or "research_question_links" not in image_df.columns:
        return pd.DataFrame()
    mask = image_df["research_question_links"].apply(lambda values: rq in values if isinstance(values, list) else False)
    return image_df.loc[mask].copy()


def image_evidence_by_rq(image_df: pd.DataFrame) -> pd.DataFrame:
    if image_df.empty:
        return pd.DataFrame(columns=["rq", "image_count"])
    rows = []
    for rq in [item["rq"] for item in RESEARCH_QUESTIONS]:
        rows.append({"rq": rq, "image_count": len(images_for_rq(image_df, rq))})
    return pd.DataFrame(rows)


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
    </style>
    """
    components.html(html, height=height + 90, scrolling=True)


def markdown_conclusion_export() -> str:
    lines = ["# Thesis RQ Conclusion Draft", ""]
    for rq in RESEARCH_QUESTIONS:
        lines.extend(
            [
                f"## {rq['rq']} - {rq['theme']}",
                "",
                f"**Answer:** {rq['conclusion']}",
                "",
                f"**Evidence status:** {rq['evidence_status']}",
                "",
            ]
        )
    lines.extend(["## Overall conclusion", "", FINAL_CONCLUSION, ""])
    return "\n".join(lines)
