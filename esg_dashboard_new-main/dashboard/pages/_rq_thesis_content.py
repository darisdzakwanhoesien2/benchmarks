from __future__ import annotations

import hashlib
import json
import re
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
  C4["Chapter 4 Results"]
  C5["Chapter 5 Discussion"]
  C6["Chapter 6 Conclusion"]

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


STREAMLIT_PAGE_CATALOG = [
    {
        "page": "Metric Analysis",
        "route": "/Metric_Analysis",
        "file": "0_Metric_Analysis.py",
        "purpose": "Compare ground truth and prediction-style metrics when evaluation labels are available.",
        "use_when": "Use for RQ4 and RQ6 when you need performance, agreement, drift, or stability summaries.",
        "outputs": "Metric tables, comparison summaries, and evaluation diagnostics.",
        "supports": "RQ4, RQ6",
    },
    {
        "page": "Parsed ESG JSON",
        "route": "/Parsed_ESG_JSON",
        "file": "00_Parsed_ESG_JSON.py",
        "purpose": "Load and inspect the existing parsed ESG sentence dataset from data_output.txt.",
        "use_when": "Use first for RQ1, RQ2, RQ4, and RQ6 to inspect the source dataset, filters, records, and distributions.",
        "outputs": "Parsed sentence table, raw aspect/tone/pillar distributions, source-data checks.",
        "supports": "RQ1, RQ2, RQ4, RQ6",
    },
    {
        "page": "Aspect",
        "route": "/Aspect",
        "file": "01_Aspect.py",
        "purpose": "Explore ESG aspect labels and taxonomy behavior.",
        "use_when": "Use for RQ2 when checking aspect diversity, ontology normalization needs, and non-standard labels.",
        "outputs": "Aspect tables, aspect distribution views, taxonomy clues.",
        "supports": "RQ2",
    },
    {
        "page": "ClimateBERT Dataset Processor",
        "route": "/ClimateBERT_Dataset_Processor",
        "file": "02_ClimateBERT_Dataset_Processor.py",
        "purpose": "Run local ClimateBERT/ESGBERT models on parsed sentence shards and save prediction CSVs incrementally.",
        "use_when": "Use for RQ3 whenever predictions are missing, incomplete, or need to continue from leftover rows.",
        "outputs": "Saved prediction CSV shards under climatebert_predictions.",
        "supports": "RQ3, RQ5",
    },
    {
        "page": "ClimateBERT Result Visualizer",
        "route": "/ClimateBERT_Result_Visualizer",
        "file": "03_ClimateBERT_Result_Visualizer.py",
        "purpose": "Review all saved ClimateBERT prediction outputs with low-RAM summaries.",
        "use_when": "Use after page 02 to verify coverage, label distributions, confidence scores, and unprocessed rows.",
        "outputs": "Prediction coverage, model-label distribution, processed/not-processed status, confidence summaries.",
        "supports": "RQ3, RQ5",
    },
    {
        "page": "Research Questions Visualizer",
        "route": "/Research_Questions_Visualizer",
        "file": "04_Research_Questions_Visualizer.py",
        "purpose": "Map RQ evidence into Available, Partial, and Needed rows with explanations and diagrams.",
        "use_when": "Use when turning dashboard outputs into thesis evidence and deciding what is still missing.",
        "outputs": "RQ evidence matrix, Mermaid diagrams, image-result explanations, RQ discussion, conclusion notes.",
        "supports": "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6",
    },
    {
        "page": "Sample Size Reasoning",
        "route": "/Sample_Size_Reasoning",
        "file": "05_Sample_Size_Reasoning.py",
        "purpose": "Explain sample-size choices, validation sample needs, and subgroup coverage limits.",
        "use_when": "Use for RQ2 and RQ6 when defending annotation size, subgroup comparison, and margin-of-error logic.",
        "outputs": "Sample-size rationale, margin-of-error explanation, subgroup coverage reasoning.",
        "supports": "RQ2, RQ6",
    },
    {
        "page": "Chapter 4 Results",
        "route": "/Chapter_4_Results",
        "file": "06_Chapter_4_Results.py",
        "purpose": "Translate dashboard outputs into Chapter 4 result sections.",
        "use_when": "Use when writing or checking the Results chapter.",
        "outputs": "Chapter 4 section plan, RQ result mapping, image artifact references.",
        "supports": "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6",
    },
    {
        "page": "Chapter 5 Discussion",
        "route": "/Chapter_5_Discussion",
        "file": "07_Chapter_5_Discussion.py",
        "purpose": "Translate results into interpretation, limitations, and claim-strength language.",
        "use_when": "Use when writing the Discussion chapter or deciding how cautious each claim should be.",
        "outputs": "Discussion sections, RQ interpretation map, claim wording guide.",
        "supports": "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6",
    },
    {
        "page": "Parsed ESG Review",
        "route": "/Parsed_ESG_Review",
        "file": "08_Parsed_ESG_Review.py",
        "purpose": "Review parsed sentence-level ESG records in a more dashboard-like analysis workspace.",
        "use_when": "Use for RQ1 and RQ4 when checking data quality, record-level issues, and diagnostics.",
        "outputs": "Record review tables, filterable evidence checks, quality review workspace.",
        "supports": "RQ1, RQ4",
    },
    {
        "page": "Data File Visualizer",
        "route": "/Data_File_Visualizer",
        "file": "09_Data_File_Visualizer.py",
        "purpose": "Inspect source data files and output files without jumping into model-specific views.",
        "use_when": "Use for RQ1 and RQ5 to verify files, paths, schemas, and artifacts.",
        "outputs": "File previews, schema checks, artifact/source inspection.",
        "supports": "RQ1, RQ5",
    },
    {
        "page": "Chapter 6 Conclusion",
        "route": "/Chapter_6_Conclusion",
        "file": "10_Chapter_6_Conclusion.py",
        "purpose": "Summarize final RQ answers, contributions, limitations, and future work.",
        "use_when": "Use when drafting final conclusion language.",
        "outputs": "Concise RQ answers, contribution summary, limitations, final thesis statement.",
        "supports": "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6",
    },
    {
        "page": "Research Questions Dashboard",
        "route": "/Research_Questions_Dashboard",
        "file": "Research_Questions_Dashboard.py",
        "purpose": "Central navigation map from RQs to pages and Chapters 4-6.",
        "use_when": "Use as the main thesis control panel before writing or completing missing RQ work.",
        "outputs": "RQ page map, chapter flow diagrams, artifact previews.",
        "supports": "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6",
    },
    {
        "page": "Benchmark Model",
        "route": "/Benchmark_Model",
        "file": "Benchmark_Model.py",
        "purpose": "Test ESG and climate NLP models on selected text or benchmark examples.",
        "use_when": "Use for RQ3 and RQ6 when comparing model behavior before or alongside full dataset processing.",
        "outputs": "Model test outputs and benchmark predictions.",
        "supports": "RQ3, RQ6",
    },
    {
        "page": "Data Distribution",
        "route": "/Data_Distribution",
        "file": "Data Distribution.py",
        "purpose": "Visualize aspect and ontology distributions in the parsed ESG data.",
        "use_when": "Use for RQ2 when explaining category imbalance and ontology coverage.",
        "outputs": "Aspect and ontology distribution charts.",
        "supports": "RQ2",
    },
    {
        "page": "Data New Distribution",
        "route": "/Data_New_Distribution",
        "file": "Data_New_Distribution.py",
        "purpose": "Explore updated ESG distribution and Sankey-style filtering views.",
        "use_when": "Use for RQ2 when comparing newer distribution logic or filtered category flows.",
        "outputs": "Filtered distribution and flow visualizations.",
        "supports": "RQ2",
    },
    {
        "page": "Distribution Document",
        "route": "/Distribution_Document",
        "file": "Distribution Document.py",
        "purpose": "Analyze sentiment and tone at document level.",
        "use_when": "Use for RQ2 and RQ6 when comparing documents instead of individual sentences.",
        "outputs": "Document-level tone and sentiment summaries.",
        "supports": "RQ2, RQ6",
    },
    {
        "page": "Sankey",
        "route": "/Sankey",
        "file": "Sankey.py",
        "purpose": "Visualize flows between tone, pillar, aspect, language, or other ESG categories.",
        "use_when": "Use for RQ2 when explaining how ESG categories connect.",
        "outputs": "Sankey flow charts and category balance views.",
        "supports": "RQ2",
    },
    {
        "page": "Tone Distribution",
        "route": "/Tone_Distribution",
        "file": "Tone_Distribution.py",
        "purpose": "Explore tone distribution across the parsed ESG dataset.",
        "use_when": "Use for RQ2 and RQ6 when explaining commitment/action/outcome/other tone patterns.",
        "outputs": "Tone count charts, tone filters, and distribution summaries.",
        "supports": "RQ2, RQ6",
    },
]


RQ_WORKFLOWS = {
    "RQ1": [
        {
            "step": "Inspect parsed dataset and record provenance",
            "page": "Parsed ESG JSON",
            "route": "/Parsed_ESG_JSON",
            "why": "Confirm that data_output.txt loads, records are parseable, and sentence rows have useful fields.",
            "expected_output": "Parsed row count, sentence table, field completion, source/path visibility.",
        },
        {
            "step": "Review sentence-level quality and traceability",
            "page": "Parsed ESG Review",
            "route": "/Parsed_ESG_Review",
            "why": "Check whether extracted rows look coherent enough for ABSA.",
            "expected_output": "Quality review notes and examples of good/bad parsed records.",
        },
        {
            "step": "Inspect source/output files",
            "page": "Data File Visualizer",
            "route": "/Data_File_Visualizer",
            "why": "Verify file paths, data shape, and artifact availability.",
            "expected_output": "Source file preview, schema check, artifact inventory.",
        },
        {
            "step": "Record RQ1 evidence status",
            "page": "Research Questions Visualizer",
            "route": "/Research_Questions_Visualizer",
            "why": "Mark what is Available, Partial, and Needed for the pipeline RQ.",
            "expected_output": "RQ1 evidence explanation and remaining OCR/sentence-boundary tasks.",
        },
        {
            "step": "Write Chapter 4-6 RQ1 narrative",
            "page": "Chapter 4 Results",
            "route": "/Chapter_4_Results",
            "why": "Move the pipeline results into thesis chapter language.",
            "expected_output": "Chapter 4 result statement; Chapter 5/6 pages provide discussion and conclusion wording.",
        },
    ],
    "RQ2": [
        {
            "step": "Start from parsed ESG records",
            "page": "Parsed ESG JSON",
            "route": "/Parsed_ESG_JSON",
            "why": "Filter sentence records by language, pillar, tone, sentiment, and aspect.",
            "expected_output": "Base crosstabs and filtered sentence examples.",
        },
        {
            "step": "Analyze aspects and ontology coverage",
            "page": "Aspect",
            "route": "/Aspect",
            "why": "Find non-standard labels and taxonomy fragmentation.",
            "expected_output": "Aspect distribution and ontology cleanup targets.",
        },
        {
            "step": "Analyze tone distribution",
            "page": "Tone Distribution",
            "route": "/Tone_Distribution",
            "why": "Explain commitment/action/outcome patterns and tone imbalance.",
            "expected_output": "Tone count and proportion charts.",
        },
        {
            "step": "Analyze category flows",
            "page": "Sankey",
            "route": "/Sankey",
            "why": "Show how tone, pillar, language, and aspect categories connect.",
            "expected_output": "Flow visualization for Chapter 4 categorization results.",
        },
        {
            "step": "Check sample-size defensibility",
            "page": "Sample Size Reasoning",
            "route": "/Sample_Size_Reasoning",
            "why": "Defend why some subgroup claims are exploratory and why expert labels need enough rows.",
            "expected_output": "Validation sample-size rationale and subgroup limitation language.",
        },
        {
            "step": "Write categorization result and discussion",
            "page": "Chapter 5 Discussion",
            "route": "/Chapter_5_Discussion",
            "why": "Separate descriptive weak-label findings from validated classification claims.",
            "expected_output": "Chapter 5 RQ2 discussion and claim-strength wording.",
        },
    ],
    "RQ3": [
        {
            "step": "Run or continue local model predictions",
            "page": "ClimateBERT Dataset Processor",
            "route": "/ClimateBERT_Dataset_Processor",
            "why": "Generate saved predictions for selected local ClimateBERT/ESGBERT models.",
            "expected_output": "Prediction CSV shards saved incrementally in climatebert_predictions.",
        },
        {
            "step": "Verify prediction coverage and results",
            "page": "ClimateBERT Result Visualizer",
            "route": "/ClimateBERT_Result_Visualizer",
            "why": "Check processed rows, leftover rows, model labels, and confidence distributions.",
            "expected_output": "Coverage table, label distribution, confidence chart, missing rows.",
        },
        {
            "step": "Test model behavior manually if needed",
            "page": "Benchmark Model",
            "route": "/Benchmark_Model",
            "why": "Probe model behavior on example ESG sentences.",
            "expected_output": "Example predictions that help interpret the full-dataset results.",
        },
        {
            "step": "Link ClimateBERT results to RQ evidence",
            "page": "Research Questions Visualizer",
            "route": "/Research_Questions_Visualizer",
            "why": "Mark whether ClimateBERT comparison evidence is Available, Partial, or Needed.",
            "expected_output": "RQ3 evidence status, interpretation, and remaining agreement/kappa tasks.",
        },
        {
            "step": "Write Chapter 4 result and Chapter 5 interpretation",
            "page": "Chapter 4 Results",
            "route": "/Chapter_4_Results",
            "why": "Present prediction coverage and model output distributions before discussing meaning.",
            "expected_output": "ClimateBERT result section ready for thesis drafting.",
        },
    ],
    "RQ4": [
        {
            "step": "Review extraction quality issues",
            "page": "Parsed ESG Review",
            "route": "/Parsed_ESG_Review",
            "why": "Inspect missing tone, schema drift, suspicious records, and source examples.",
            "expected_output": "Record-level diagnostic examples.",
        },
        {
            "step": "Quantify diagnostic patterns",
            "page": "Metric Analysis",
            "route": "/Metric_Analysis",
            "why": "Summarize errors by model, prompt, document, language, or pillar when labels/fields are available.",
            "expected_output": "Diagnostic metric tables and failure-rate summaries.",
        },
        {
            "step": "Check parsed records behind failures",
            "page": "Parsed ESG JSON",
            "route": "/Parsed_ESG_JSON",
            "why": "Trace failures back to original rows and filters.",
            "expected_output": "Filtered evidence rows for schema drift, missing tone, and ontology issues.",
        },
        {
            "step": "Update RQ4 evidence",
            "page": "Research Questions Visualizer",
            "route": "/Research_Questions_Visualizer",
            "why": "Connect diagnostic results to the RQ4 evidence checklist.",
            "expected_output": "RQ4 Available/Partial/Needed status and formal error-taxonomy task.",
        },
    ],
    "RQ5": [
        {
            "step": "Open central thesis dashboard",
            "page": "Research Questions Dashboard",
            "route": "/Research_Questions_Dashboard",
            "why": "Use the RQ-to-page map and Chapter 4-6 links as the audit trail.",
            "expected_output": "Navigation map showing where every RQ is fulfilled.",
        },
        {
            "step": "Inspect generated artifact explanations",
            "page": "Research Questions Visualizer",
            "route": "/Research_Questions_Visualizer",
            "why": "Review image outputs, JSON/Markdown explanations, and Mermaid diagrams.",
            "expected_output": "Traceable interpretation layer for saved outputs.",
        },
        {
            "step": "Verify files and source paths",
            "page": "Data File Visualizer",
            "route": "/Data_File_Visualizer",
            "why": "Confirm source files, prediction folders, and generated artifacts exist.",
            "expected_output": "Artifact inventory and path checks.",
        },
        {
            "step": "Write reproducibility narrative",
            "page": "Chapter 5 Discussion",
            "route": "/Chapter_5_Discussion",
            "why": "Explain auditability, rerun capability, and remaining replication limitations.",
            "expected_output": "Chapter 5 reproducibility discussion.",
        },
    ],
    "RQ6": [
        {
            "step": "Inspect parsed data by model/prompt/document",
            "page": "Parsed ESG JSON",
            "route": "/Parsed_ESG_JSON",
            "why": "Build the base comparison view before measuring stability.",
            "expected_output": "Matched or unmatched record counts by model, prompt, document, tone, and language.",
        },
        {
            "step": "Run metric comparison",
            "page": "Metric Analysis",
            "route": "/Metric_Analysis",
            "why": "Compute variation, agreement, or performance metrics where possible.",
            "expected_output": "Coefficient of variation, agreement summaries, stability tables.",
        },
        {
            "step": "Check sample-size and subgroup limits",
            "page": "Sample Size Reasoning",
            "route": "/Sample_Size_Reasoning",
            "why": "Avoid overclaiming when model/prompt slices are small or unbalanced.",
            "expected_output": "Sample-size limitation and balanced-comparison requirements.",
        },
        {
            "step": "Compare models manually or with examples",
            "page": "Benchmark Model",
            "route": "/Benchmark_Model",
            "why": "Understand why models/prompts may disagree before writing interpretation.",
            "expected_output": "Model behavior examples.",
        },
        {
            "step": "Write stability discussion and conclusion",
            "page": "Chapter 5 Discussion",
            "route": "/Chapter_5_Discussion",
            "why": "Frame stability as a limitation and future ensemble direction unless the balanced matrix is complete.",
            "expected_output": "RQ6 discussion and Chapter 6 conclusion qualification.",
        },
    ],
}


COMPLETE_WORKFLOW_MERMAID = """
flowchart TB
  Start["Start: choose research question"]
  RQ1["RQ1 Pipeline"]
  RQ2["RQ2 Categorization"]
  RQ3["RQ3 ClimateBERT"]
  RQ4["RQ4 Diagnostics"]
  RQ5["RQ5 Reproducibility"]
  RQ6["RQ6 Stability"]

  Parsed["Parsed ESG JSON"]
  Review["Parsed ESG Review"]
  Files["Data File Visualizer"]
  Aspect["Aspect"]
  Tone["Tone Distribution"]
  SankeyPage["Sankey"]
  Sample["Sample Size Reasoning"]
  Processor["ClimateBERT Dataset Processor"]
  Results["ClimateBERT Result Visualizer"]
  Metric["Metric Analysis"]
  Benchmark["Benchmark Model"]
  RQViz["Research Questions Visualizer"]
  RQDash["Research Questions Dashboard"]
  C4["Chapter 4 Results"]
  C5["Chapter 5 Discussion"]
  C6["Chapter 6 Conclusion"]

  Start --> RQ1
  Start --> RQ2
  Start --> RQ3
  Start --> RQ4
  Start --> RQ5
  Start --> RQ6

  RQ1 --> Parsed --> Review --> Files --> RQViz
  RQ2 --> Parsed --> Aspect --> Tone --> SankeyPage --> Sample --> RQViz
  RQ3 --> Processor --> Results --> Benchmark --> RQViz
  RQ4 --> Review --> Metric --> Parsed --> RQViz
  RQ5 --> RQDash --> RQViz --> Files
  RQ6 --> Parsed --> Metric --> Sample --> Benchmark --> RQViz

  RQViz --> C4
  C4 --> C5
  C5 --> C6
""".strip()


LABELED_COMPLETE_WORKFLOW_MERMAID = """
flowchart TD
  subgraph INPUT["Input and parsed ESG data"]
    Parsed["Parsed ESG JSON\\nInspect data_output.txt"]
    Review["Parsed ESG Review\\nReview sentence-level quality"]
    Files["Data File Visualizer\\nInspect source and artifacts"]
  end

  subgraph CATEGORY["ESG categorization and distribution"]
    Aspect["Aspect\\nAspect and ontology labels"]
    Tone["Tone Distribution\\nTone counts and proportions"]
    DataDist["Data Distribution\\nAspect and ontology charts"]
    DataNew["Data New Distribution\\nFiltered distribution views"]
    DocDist["Distribution Document\\nDocument-level tone/sentiment"]
    SankeyPage["Sankey\\nESG flow visualization"]
    Sample["Sample Size Reasoning\\nValidation and subgroup logic"]
  end

  subgraph CLIMATE["ClimateBERT and model validation"]
    Processor["ClimateBERT Dataset Processor\\nRun local models"]
    Results["ClimateBERT Result Visualizer\\nReview saved predictions"]
    Benchmark["Benchmark Model\\nTest model behavior"]
    Metric["Metric Analysis\\nCompare metrics and stability"]
  end

  subgraph SYNTHESIS["RQ evidence and thesis writing"]
    RQDash["Research Questions Dashboard\\nRQ to page map"]
    RQViz["Research Questions Visualizer\\nEvidence matrix"]
    Workflow["Streamlit Page Workflow\\nNavigation and complete workflow"]
    C4["Chapter 4 Results\\nWhat was implemented"]
    C5["Chapter 5 Discussion\\nWhat the results mean"]
    C6["Chapter 6 Conclusion\\nFinal answers and limits"]
    Artifacts["Saved PNG + JSON + Markdown\\nEvidence artifacts"]
  end

  Parsed -- "RQ1, RQ2, RQ4, RQ6" --> Review
  Parsed -- "RQ1, RQ5" --> Files
  Parsed -- "RQ2, RQ6" --> Aspect
  Aspect -- "RQ2" --> Tone
  Tone -- "RQ2, RQ6" --> DataDist
  DataDist -- "RQ2" --> DataNew
  DataNew -- "RQ2" --> SankeyPage
  DocDist -- "RQ2, RQ6" --> RQViz
  SankeyPage -- "RQ2, RQ5" --> RQViz
  Sample -- "RQ2, RQ6" --> RQViz

  Processor -- "RQ3, RQ5" --> Results
  Results -- "RQ3" --> Benchmark
  Results -- "RQ3, RQ5" --> RQViz
  Metric -- "RQ4, RQ6" --> RQViz
  Benchmark -- "RQ3, RQ6" --> RQViz
  Review -- "RQ1, RQ4" --> Metric

  RQDash -- "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6" --> Workflow
  RQViz -- "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6" --> RQDash
  RQViz -- "RQ5" --> Artifacts
  Artifacts -- "RQ5" --> C4
  RQViz -- "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6" --> C4
  C4 -- "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6" --> C5
  C5 -- "RQ1, RQ2, RQ3, RQ4, RQ5, RQ6" --> C6
""".strip()


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
            lines.append(f'  {edge["source_id"]} -- "{mermaid_label(label)}" --> {edge["target_id"]}')
        else:
            lines.append(f'  {edge["source_id"]} --> {edge["target_id"]}')

    return "\n".join(lines)


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


def mermaid_download_section(code: str, name: str = "mermaid_diagram") -> None:
    safe_name = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in name).strip("_") or "mermaid_diagram"
    cols = st.columns(3)
    with cols[0]:
        st.download_button(
            "Download Mermaid source",
            data=code,
            file_name=f"{safe_name}.mmd",
            mime="text/plain",
            use_container_width=True,
        )
    with cols[1]:
        st.download_button(
            "Download Markdown block",
            data=f"```mermaid\n{code}\n```\n",
            file_name=f"{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with cols[2]:
        st.link_button(
            "Open Mermaid Live Editor",
            "https://mermaid.ai/live/edit",
            use_container_width=True,
        )


def page_link_grid(page_pairs: list[tuple[str, str]], columns: int = 3) -> None:
    cols = st.columns(columns)
    for idx, (label, route) in enumerate(page_pairs):
        with cols[idx % columns]:
            st.link_button(label, route, use_container_width=True)
