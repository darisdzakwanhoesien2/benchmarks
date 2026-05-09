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


PAGE_DIR = Path(__file__).resolve().parent
BENCHMARKS_DIR = Path(__file__).resolve().parents[3]
SOURCE_HTML_CANDIDATES = [
    PAGE_DIR / "thesis_data_analysis_benchmarks.html",
    BENCHMARKS_DIR / "pages" / "thesis_data_analysis_benchmarks.html",
]
SOURCE_HTML = next(
    (path for path in SOURCE_HTML_CANDIDATES if path.exists()),
    SOURCE_HTML_CANDIDATES[0],
)
ABSA_METRICS_CANDIDATES = [
    PAGE_DIR / "absa_metrics_results.json",
    PAGE_DIR.parent / "absa_metrics_results.json",
    BENCHMARKS_DIR / "absa_metrics_results.json",
]
ABSA_METRICS_PATH = next(
    (path for path in ABSA_METRICS_CANDIDATES if path.exists()),
    ABSA_METRICS_CANDIDATES[0],
)
LOCAL_ABSA_METRICS_PATH = PAGE_DIR.parent / "absa_metrics_results_local_climate_controversy.json"
IMAGE_EXPLANATIONS_PATH = PAGE_DIR.parent / "results" / "image_outputs_archive" / "image_outputs_explanations.json"
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

PAGE_ANALYSIS_INVENTORY = pd.DataFrame([
    [
        "Parsed ESG sentence dashboards",
        "esg_dashboard_new_0_new.py; esg_dashboard_new_8_new.py",
        "Parsed JSON inspection, filters, model comparison, grounded markdown review, model coverage by PDF/page.",
        "RQ1, RQ2, RQ4, RQ5, RQ6",
        "Direct thesis evidence",
        "Use these as the main source for parseability, provenance, field coverage, tone/aspect distributions, model/prompt coverage, and auditability.",
    ],
    [
        "Aspect and ontology distribution dashboards",
        "esg_dashboard_new_Data Distribution.py; esg_dashboard_new_Data_New_Distribution.py; esg_dashboard_new_01_Aspects_Raw.py; esg_dashboard_new_02_Aspects_Clustered.py; esg_dashboard_new_03_Aspect_Comparison.py; zz_aspect_clusters.py",
        "Aspect category distributions, raw-to-cluster mappings, ontology URI distributions, waterfall filtering, multi-rule filtering, and unclustered aspect review.",
        "RQ2, RQ4, RQ5",
        "Direct thesis evidence",
        "Use these to support taxonomy normalization, ontology coverage, non-standard aspect detection, and bilingual comparability claims.",
    ],
    [
        "Tone, sentiment, Sankey, and document distribution dashboards",
        "esg_dashboard_new_Tone_Distribution.py; esg_dashboard_new_Sankey.py; esg_dashboard_new_Distribution Document.py",
        "Tone distribution, tone balancing, sentiment/tone per document, aspect x sentiment/tone heatmaps, Sankey flows, and correlation summaries.",
        "RQ2, RQ4, RQ6",
        "Direct thesis evidence",
        "Use these for tone imbalance, subgroup coverage, document-level variation, and prompt/model stability framing.",
    ],
    [
        "ABSA metrics and ground-truth comparison",
        "absa_metrics_comparison.py; absa_metrics_comparison_mac.py; absa_metrics_comparison copy.py; absa_metrics_visualization.py; esg_dashboard_new_0_Metric_Analysis.py; test_models.py",
        "Ground truth vs prediction metrics, confusion matrices, TP/FP/FN tables, saved metrics JSON, confidence/error views, and rule/classical/deep/hybrid metric summaries.",
        "RQ2, RQ3, RQ4, RQ6",
        "Direct thesis evidence",
        "Use these only when label spaces and sample alignment are explicit; current low ClimateBERT-style scores are stronger evidence of mapping/evaluation mismatch than final model quality.",
    ],
    [
        "ClimateBERT processing and result exploration",
        "0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py; 0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py; 0_0_ClimateBERT_4_Model_Analysis.py; 0_0_ClimateBERT_5_Model_Deep_Explorer.py; 0_0_ClimateBERT_6_Model_Overview_All.py; 0_0_ClimateBERT_7_Full_Model_Visualization.py; 0_ClimateBERT_Commitment_Distribution.py; 1_ABSA_Integration.py",
        "Batch inference, per-model accuracy/coverage/confidence, leaderboards, confusion matrices, prediction explorers, and ABSA-to-ClimateBERT integration.",
        "RQ3, RQ5, RQ6",
        "Direct thesis evidence",
        "Use these to close the actual ClimateBERT comparison gap: prediction coverage, confidence distribution, label agreement, and cross-model stability.",
    ],
    [
        "Interactive model demos and benchmark testers",
        "0_0_1_Single_Prediction.py; 0_0_1_multiple_Prediction.py; 0_0_2_Batch_Prediction.py; 0_0_3_Model_Explorer.py; esg_dashboard_new_Benchmark_Model.py; ABSA_Model_Comparison.py; 1_Analyze.py",
        "Manual text input, multi-model prediction, batch prediction, model metadata exploration, and interactive comparison across ABSA modules.",
        "RQ5, RQ6",
        "Supporting evidence",
        "Useful for reproducibility demonstrations and qualitative sanity checks; not enough by itself for thesis claims without saved datasets and metrics.",
    ],
    [
        "ABSA ontology/model prototype pages",
        "2_ABSA_Rule_Based.py; 3_ABSA_Classical.py; 5_ABSA_Deep_Learning.py; absa_ontology_3_deep_model.py; absa_ontology_all.py; absa_ontology_all_new_notes.py",
        "Rule-based, classical ML, deep/mBERT, hybrid, and explainability prototypes for ABSA modeling.",
        "RQ2, RQ4, RQ6",
        "Supporting evidence",
        "Use these as methodological prototypes and error-analysis tools, not as production results unless their training/evaluation data are documented.",
    ],
    [
        "Baselines, documentation, and scaffolding",
        "scrambled_absa_mapping_baseline.py; scrambled_absa_mapping_baseline_mac.py; parse_documentation_json.py; _page_explanations.py; _shared/page_explanations.py; _shared/__init__.py; 0_0_0_1.py; 0_0_0_code.py",
        "Scrambled baselines, documentation parsing, page explanations, shared helper scaffolding, and empty placeholder pages.",
        "RQ5",
        "Other / utility",
        "These support dashboard documentation and baseline generation. Empty placeholders and helper modules should be documented as non-analytic utilities.",
    ],
], columns=[
    "analysis_group",
    "pages",
    "what_the_existing_pages_do",
    "research_question_links",
    "evidence_role",
    "how_to_use_in_thesis",
])

PAGE_FILE_INVENTORY = pd.DataFrame([
    ["04_Research_Questions_Visualizer.py", "RQ synthesis and evidence-gap dashboard", "Related", "RQ1-RQ6", "Meta synthesis", "This page organizes thesis evidence, missing work, RQ links, diagrams, and page inventory."],
    ["05_Sample_Size_Reasoning.py", "Sample-size, subgroup, power, and evaluation-readiness reasoning", "Related", "RQ2, RQ3, RQ6", "Direct thesis evidence", "Supports defensible claim levels, subgroup coverage, power, and why expert annotation is needed."],
    ["esg_dashboard_new_0_new.py", "Parsed ESG JSON dashboard with filters, grounded model comparison, coverage, and sentence table", "Related", "RQ1, RQ2, RQ4, RQ5, RQ6", "Direct thesis evidence", "Core evidence for parseability, provenance, field distributions, model/prompt behavior, and auditability."],
    ["esg_dashboard_new_8_new.py", "Alternative parsed ESG JSON dashboard over dataset.json", "Related", "RQ1, RQ2, RQ4, RQ5, RQ6", "Direct thesis evidence", "Same analytical role as the parsed JSON dashboard, using a different dataset artifact."],
    ["esg_dashboard_new_Data Distribution.py", "Aspect, ontology, sentiment, tone, feature, and heatmap distributions", "Related", "RQ2, RQ4, RQ5", "Direct thesis evidence", "Supports taxonomy coverage, aspect imbalance, sentiment/tone distribution, and ontology diagnostics."],
    ["esg_dashboard_new_Data_New_Distribution.py", "ESG Sankey, waterfall filtering, and multi-rule explorer", "Related", "RQ2, RQ4, RQ6", "Direct thesis evidence", "Supports subgroup filtering, distribution pathways, and rule-based analysis of ESG labels."],
    ["esg_dashboard_new_Distribution Document.py", "Document-level sentiment and tone analysis", "Related", "RQ2, RQ4, RQ6", "Direct thesis evidence", "Supports document-level variation, sentiment/tone composition, and correlation analysis."],
    ["esg_dashboard_new_Tone_Distribution.py", "Tone distribution explorer and tone balancing workflow", "Related", "RQ2, RQ6", "Direct thesis evidence", "Supports tone imbalance, subgroup coverage, and balancing requirements."],
    ["esg_dashboard_new_Sankey.py", "Upload-based tone distribution, balancing, and Sankey flow", "Related", "RQ2, RQ6", "Direct thesis evidence", "Supports aspect-sentiment-tone flow interpretation and balanced sampling design."],
    ["esg_dashboard_new_01_Aspects_Raw.py", "Raw aspect view before manual annotation", "Related", "RQ2, RQ4", "Direct thesis evidence", "Shows uncontrolled aspect vocabulary before taxonomy cleanup."],
    ["esg_dashboard_new_02_Aspects_Clustered.py", "Clustered aspect view and unclustered aspect review", "Related", "RQ2, RQ4", "Direct thesis evidence", "Supports ontology normalization and review of unmapped aspect labels."],
    ["esg_dashboard_new_03_Aspect_Comparison.py", "Before-vs-after aspect mapping comparison", "Related", "RQ2, RQ4", "Direct thesis evidence", "Shows impact of manual clustering on aspect distributions."],
    ["zz_aspect_clusters.py", "Aspect cluster explorer", "Related", "RQ2, RQ4", "Direct thesis evidence", "Supports inspection of aspect clusters, top members, and taxonomy coverage."],
    ["absa_metrics_comparison.py", "Ground truth vs baseline ABSA metric comparison for Windows paths", "Related", "RQ2, RQ3, RQ4, RQ6", "Direct thesis evidence", "Computes precision, recall, F1, confusion matrix, and TP/FP/FN for category, sentiment, and tone."],
    ["absa_metrics_comparison_mac.py", "Ground truth vs baseline ABSA metric comparison for benchmark-root paths", "Related", "RQ2, RQ3, RQ4, RQ6", "Direct thesis evidence", "Same metrics role as the Windows version, with robust path and label normalization."],
    ["absa_metrics_comparison copy.py", "Older or duplicate ABSA metric comparison page", "Partly related", "RQ2, RQ4", "Supporting evidence", "Potentially useful but should not be cited separately unless it differs from the main metric pages."],
    ["absa_metrics_visualization.py", "Saved ABSA metrics JSON visualization", "Related", "RQ2, RQ3, RQ4, RQ6", "Direct thesis evidence", "Displays non-zero and zero model results from absa_metrics_results.json."],
    ["esg_dashboard_new_0_Metric_Analysis.py", "Upload-based metric analysis with sentence alignment, errors, and confidence", "Related", "RQ2, RQ4, RQ6", "Direct thesis evidence", "Supports evaluation workflow and error analysis when inputs are aligned."],
    ["test_models.py", "ESG ABSA model tester with metrics and interpretability", "Partly related", "RQ2, RQ4, RQ6", "Supporting evidence", "Useful for comparing rule/classical/deep/hybrid prototypes, but needs saved evaluation artifacts for thesis claims."],
    ["0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py", "ClimateBERT batch processor for Linux ground-truth data", "Related", "RQ3, RQ5", "Direct thesis evidence", "Produces ClimateBERT predictions needed for dataset-wide comparison."],
    ["0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py", "ClimateBERT batch processor for Windows ground-truth data", "Related", "RQ3, RQ5", "Direct thesis evidence", "Alternative path version for producing ClimateBERT predictions."],
    ["0_0_ClimateBERT_4_Model_Analysis.py", "ClimateBERT model analysis with accuracy, coverage, confidence, errors, and export", "Related", "RQ3, RQ4, RQ6", "Direct thesis evidence", "Supports model performance, coverage, and error diagnostics."],
    ["0_0_ClimateBERT_5_Model_Deep_Explorer.py", "Per-model ClimateBERT deep explorer", "Related", "RQ3, RQ4", "Direct thesis evidence", "Supports label distribution, confidence, confusion matrix, prediction explorer, and advanced metrics."],
    ["0_0_ClimateBERT_6_Model_Overview_All.py", "All-model ClimateBERT visualization and leaderboard", "Related", "RQ3, RQ6", "Direct thesis evidence", "Supports cross-model comparison and stability analysis."],
    ["0_0_ClimateBERT_7_Full_Model_Visualization.py", "Full ClimateBERT visualization with dataset info, leaderboard, confusion matrix, and exports", "Related", "RQ3, RQ5, RQ6", "Direct thesis evidence", "Supports model comparison, reproducible exports, and coverage diagnostics."],
    ["0_ClimateBERT_Commitment_Distribution.py", "Climate commitment model analysis", "Related", "RQ3, RQ6", "Direct thesis evidence", "Supports climate-commitment label distributions, confidence, true-vs-predicted comparison, and global model distributions."],
    ["1_ABSA_Integration.py", "ABSA mapping integrated with ClimateBERT parsed results", "Related", "RQ2, RQ3", "Direct thesis evidence", "Connects ABSA majority category/sentiment/tone fields with climate commitment outputs."],
    ["ABSA_Model_Comparison.py", "Interactive comparison across rule-based, classical, deep, and hybrid ABSA modules", "Partly related", "RQ2, RQ6", "Supporting evidence", "Useful for qualitative model behavior comparison; not enough for quantitative thesis evidence by itself."],
    ["2_ABSA_Rule_Based.py", "Rule-based ontology ABSA demo", "Partly related", "RQ2, RQ4", "Supporting evidence", "Prototype for explainable taxonomy logic and rule diagnostics."],
    ["3_ABSA_Classical.py", "Classical ML ABSA demo", "Partly related", "RQ2, RQ6", "Supporting evidence", "Prototype with predictions, coefficients, and visualization; cite only if evaluated on thesis data."],
    ["5_ABSA_Deep_Learning.py", "Deep learning ABSA demo", "Partly related", "RQ2, RQ6", "Supporting evidence", "Prototype for token interpretability; needs formal evaluation before thesis claims."],
    ["absa_ontology_3_deep_model.py", "Deep model mBERT demo", "Partly related", "RQ2, RQ6", "Supporting evidence", "Small demo page for deep ABSA modeling."],
    ["absa_ontology_all.py", "ABSA ontology module demos", "Partly related", "RQ2, RQ4, RQ6", "Supporting evidence", "Shows rule, classical, deep, hybrid, and explainability modules as methodology prototypes."],
    ["absa_ontology_all_new_notes.py", "ABSA ontology module demos with saved explanation notes", "Partly related", "RQ2, RQ4, RQ5, RQ6", "Supporting evidence", "Adds note persistence and explainability outputs; relevant for documentation if outputs are saved."],
    ["0_0_1_Single_Prediction.py", "Single text prediction demo", "Partly related", "RQ5, RQ6", "Supporting evidence", "Manual sanity-check interface; not empirical evidence unless predictions are saved and evaluated."],
    ["0_0_1_multiple_Prediction.py", "Multi-model prediction demo", "Partly related", "RQ5, RQ6", "Supporting evidence", "Can support reproducibility and qualitative model comparison if saved predictions are retained."],
    ["0_0_2_Batch_Prediction.py", "Batch prediction upload page", "Partly related", "RQ5, RQ6", "Supporting evidence", "Can produce batch result artifacts, but thesis relevance depends on dataset alignment."],
    ["0_0_3_Model_Explorer.py", "Model metadata explorer", "Unrelated / utility", "None directly", "Utility", "Helps inspect available models but does not analyze thesis data."],
    ["esg_dashboard_new_Benchmark_Model.py", "ESG and climate NLP model tester", "Partly related", "RQ3, RQ6", "Supporting evidence", "Interactive benchmark tester; thesis relevance depends on saved outputs and aligned evaluation."],
    ["1_Analyze.py", "Interactive ESG text analyzer", "Unrelated / utility", "None directly", "Demo / utility", "Manual analysis page, not tied to thesis dataset or RQ evidence unless outputs are saved."],
    ["scrambled_absa_mapping_baseline.py", "Scrambled baseline generator/viewer for Windows ground truth", "Partly related", "RQ4, RQ6", "Supporting evidence", "Useful as a negative-control baseline, not a substantive ESG result."],
    ["scrambled_absa_mapping_baseline_mac.py", "Scrambled baseline generator/viewer for Mac/benchmark ground truth", "Partly related", "RQ4, RQ6", "Supporting evidence", "Useful as a negative-control baseline, not a substantive ESG result."],
    ["parse_documentation_json.py", "Documentation JSON table viewer", "Unrelated / utility", "RQ5 only if used for docs", "Utility", "Documentation parsing helper; not empirical ESG evidence."],
    ["_page_explanations.py", "Shared page explanation metadata/helper", "Unrelated / utility", "RQ5 only as documentation support", "Utility", "Supports page documentation but is not an analysis page."],
    ["0_0_0_1.py", "Empty placeholder", "Unrelated / utility", "None", "Empty placeholder", "No analysis code exists in this file."],
    ["0_0_0_code.py", "Empty placeholder", "Unrelated / utility", "None", "Empty placeholder", "No analysis code exists in this file."],
], columns=[
    "file",
    "analysis",
    "relation_to_research_questions",
    "rq_links",
    "evidence_role",
    "why_it_matters_or_not",
])

RQ_DISCUSSIONS = pd.DataFrame([
    [
        "RQ1",
        "Pipeline",
        "The current evidence supports a working feasibility pipeline: source reports are available, extracted JSON records are parseable, and dashboard pages can trace records back into source-oriented views.",
        "The strongest contribution is auditability and structured transformation from report text into sentence-level ESG records.",
        "OCR character/word error rate, sentence-boundary accuracy, and table/figure extraction quality are still missing, so RQ1 should be framed as pipeline feasibility rather than fully validated extraction accuracy.",
        "Add a small manual OCR reference set and record-level provenance audit before claiming production-grade extraction reliability.",
    ],
    [
        "RQ2",
        "Categorization",
        "The visual outputs show meaningful tone, aspect, pillar, and sentiment structure. Tone distribution, ESG-by-tone, and aspect-by-tone images make category imbalance visible.",
        "The findings are useful for descriptive ABSA: commitment language is prominent, Environmental and Governance evidence are more visible than Social evidence, and aspect/tone cells reveal where the taxonomy is sparse.",
        "Because expert labels and inter-annotator agreement are not complete, the current categories are best treated as LLM-assisted weak labels rather than validated gold ABSA labels.",
        "Create a 30-50 row expert-labeled stratified sample and normalize non-standard aspects into a controlled bilingual ontology.",
    ],
    [
        "RQ3",
        "ClimateBERT",
        "The ClimateBERT label-by-tone and remote-score outputs are useful exploratory evidence, but current metrics show that label-space alignment remains fragile.",
        "The analysis suggests ClimateBERT can add a climate-specific layer beyond tone, especially when compared through crosstabs and confidence distributions.",
        "Zero or near-zero metrics should not be interpreted as model failure alone; they may indicate incompatible label spaces, incomplete local inference, or mapping problems.",
        "Run local ClimateBERT models over every valid sentence, then define explicit mapping rules before computing agreement and Cohen kappa.",
    ],
    [
        "RQ4",
        "Diagnostics",
        "The confusion-matrix images and missing-work tables show that the dashboard can identify where label decisions fail, where classes are confused, and where extraction evidence is incomplete.",
        "The current diagnostic contribution is practical: it separates schema drift, missing labels, taxonomy gaps, class imbalance, and evaluation mismatch rather than treating errors as one generic failure.",
        "Formal manual error labels are still missing, so the diagnostics framework is stronger as an audit design than as a quantified error taxonomy.",
        "Add an `error_type` column for sampled records and summarize errors by model, prompt, document, language, pillar, and page.",
    ],
    [
        "RQ5",
        "Reproducibility",
        "The image archive, JSON manifest, Markdown explanation file, page inventory, and Streamlit pages provide a reproducible audit trail for visual and tabular outputs.",
        "The strongest contribution is traceability: visual outputs now have archived paths, checksums, dimensions, explanations, and thesis-use notes.",
        "The dashboard still needs a final rerun checklist and environment/version capture before claiming independent reproducibility.",
        "Keep the generated image manifest under version control and add a short replication protocol for regenerating data, metrics, and visualizations.",
    ],
    [
        "RQ6",
        "Stability",
        "Tone distribution, ESG-by-tone, aspect-by-tone, ClimateBERT label-by-tone, and ensemble confusion matrices support the stability question by exposing variation across labels, models, and aggregation choices.",
        "The current evidence suggests prompt/model choices and ensemble choices can materially change output distributions and errors.",
        "The model x prompt x document matrix is still imbalanced, so stability claims should remain cautious until matched runs exist.",
        "Build a balanced comparison matrix and run majority-vote or ensemble simulations on matched document/prompt/model cells.",
    ],
], columns=[
    "rq",
    "theme",
    "discussion",
    "results_interpretation",
    "limitation",
    "next_step",
])

GENERAL_DISCUSSION = [
    "Across the dashboard, the strongest current result is not a single model score. It is the construction of an auditable ESG ABSA workflow that turns raw sustainability-report text into inspectable sentence-level evidence, visual distributions, metrics, and documented artifacts.",
    "The visual outputs show useful descriptive patterns: tone classes are imbalanced, ESG pillars are unevenly represented, aspect-tone cells reveal taxonomy sparsity, and ClimateBERT comparison needs careful label mapping.",
    "The main methodological risk is over-claiming. Current labels and metrics are valuable for feasibility, diagnostics, and thesis direction, but expert annotation, OCR quality measurement, and balanced model/prompt coverage are still needed before reporting strong accuracy or generalizable greenwashing claims.",
]

CONCLUSION_TEXT = [
    "The current system is defensible as a research-grade feasibility and diagnostics dashboard for ESG ABSA. It demonstrates that bilingual sustainability reports can be transformed into structured, auditable sentence-level records and connected to visual and metric-based analysis.",
    "The strongest thesis claim should emphasize pipeline feasibility, evidence traceability, taxonomy diagnostics, and sample-size reasoning. Stronger claims about classification accuracy, ClimateBERT agreement, and greenwashing generalization require the next validation layer: expert labels, full local model coverage, and balanced subgroup sampling.",
    "The archived image outputs and their JSON/Markdown explanations improve reproducibility because every major visual artifact now has a stable file path, source path, interpretation, RQ linkage, and thesis-use note.",
]


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
      #{container_id} {{
        width: 100%;
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


def build_full_rq_map_mermaid(detail_df: pd.DataFrame) -> str:
    rows = detail_df.groupby(["rq", "theme", "status"]).size().reset_index(name="count")
    lines = [
        "flowchart TB",
        '  DataOutput["data_output.txt"]',
        '  Predictions["climatebert_predictions"]',
        '  Gold["expert annotation"]',
        '  Audit["artifact registry"]',
    ]

    for rq in sorted(detail_df["rq"].unique()):
        theme = detail_df[detail_df["rq"] == rq]["theme"].iloc[0]
        lines.append(f'  {rq}["{rq} - {mermaid_label(theme)}"]')

    lines.extend([
        "  DataOutput --> RQ1",
        "  DataOutput --> RQ2",
        "  Predictions --> RQ3",
        "  DataOutput --> RQ4",
        "  Audit --> RQ5",
        "  DataOutput --> RQ6",
        "  Gold --> RQ2",
        "  Gold --> RQ4",
        "  Predictions --> RQ5",
        "  RQ3 --> RQ6",
    ])

    for _, row in rows.iterrows():
        node_id = f'{row["rq"]}_{row["status"]}'
        label = f'{row["status"]}: {row["count"]}'
        lines.append(f'  {node_id}["{label}"]')
        lines.append(f'  {row["rq"]} --> {node_id}')

    lines.extend([
        "  classDef source fill:#eef6ff,stroke:#2563eb,color:#111827;",
        "  classDef rq fill:#f8fafc,stroke:#334155,color:#111827,stroke-width:2px;",
        "  classDef available fill:#ecfdf5,stroke:#16a34a,color:#111827;",
        "  classDef partial fill:#fffbeb,stroke:#d97706,color:#111827;",
        "  classDef needed fill:#fef2f2,stroke:#dc2626,color:#111827;",
        "  class DataOutput,Predictions,Gold,Audit source;",
        "  class RQ1,RQ2,RQ3,RQ4,RQ5,RQ6 rq;",
    ])
    for status, class_name in [("Available", "available"), ("Partial", "partial"), ("Needed", "needed")]:
        nodes = [f"{rq}_{status}" for rq in sorted(detail_df["rq"].unique()) if f"{rq}_{status}" in "\n".join(lines)]
        if nodes:
            lines.append(f"  class {','.join(nodes)} {class_name};")
    return "\n".join(lines)


def build_workflow_mermaid() -> str:
    return """
flowchart LR
  PDF["PDF reports"]
  OCR["OCR markdown"]
  LLM["LLM JSON extraction"]
  DATA["data_output.txt"]
  PARSED["parsed ESG records"]
  CB["ClimateBERT processor"]
  PRED["prediction CSV shards"]
  VIZ["result visualizer"]
  RQ["RQ evidence dashboard"]

  PDF --> OCR
  OCR --> LLM
  LLM --> DATA
  DATA --> PARSED
  PARSED --> CB
  CB --> PRED
  PRED --> VIZ
  PARSED --> RQ
  PRED --> RQ

  classDef source fill:#eef6ff,stroke:#2563eb,color:#111827;
  classDef process fill:#f8fafc,stroke:#334155,color:#111827;
  classDef output fill:#ecfdf5,stroke:#16a34a,color:#111827;
  class PDF,DATA,PRED source;
  class OCR,LLM,CB,VIZ,RQ process;
  class PARSED output;
""".strip()


def build_missing_process_mermaid() -> str:
    return """
flowchart TB
  GAP["missing RQ evidence"]
  IDENTIFY["identify metric"]
  SOURCE["choose source"]
  SAMPLE["targeted sample"]
  RUN["run analysis"]
  METRIC["compute metric"]
  UPDATE["update RQ table"]

  DATA["data_output.txt"]
  PRED["climatebert_predictions"]
  ANN["manual annotation"]
  COMP["ClimateBERT comparison"]
  STAB["stability analysis"]

  GAP --> IDENTIFY
  IDENTIFY --> SOURCE
  SOURCE --> SAMPLE
  SAMPLE --> RUN
  RUN --> METRIC
  METRIC --> UPDATE

  SOURCE --> DATA
  SOURCE --> PRED
  RUN --> ANN
  RUN --> COMP
  RUN --> STAB

  classDef source fill:#eef6ff,stroke:#2563eb,color:#111827;
  classDef process fill:#f8fafc,stroke:#334155,color:#111827;
  classDef action fill:#fffbeb,stroke:#d97706,color:#111827;
  class DATA,PRED source;
  class GAP,IDENTIFY,SOURCE,SAMPLE,RUN,METRIC,UPDATE process;
  class ANN,COMP,STAB action;
""".strip()


PIPELINE_MERMAID = """
flowchart LR
  W_PDF[PDF source reports]
  W_OCR[OCR and markdown extraction]
  W_LLM[LLM ESG JSON extraction]
  W_DATA[data output sentence records]
  W_PARSED[Parsed ESG table]
  W_RUN[ClimateBERT processor page 02]
  W_PRED[ClimateBERT prediction CSVs]
  W_VIZ[Result visualizer page 03]
  W_RQ[Research question evidence page 04]

  W_PDF --> W_OCR
  W_OCR --> W_LLM
  W_LLM --> W_DATA
  W_DATA --> W_PARSED
  W_PARSED --> W_RUN
  W_RUN --> W_PRED
  W_PRED --> W_VIZ
  W_PARSED --> W_RQ
  W_PRED --> W_RQ
""".strip()

RQ_MERMAID = """
flowchart TB
  E_DATA[data output parsed records]
  E_PRED[ClimateBERT predictions]
  E_GOLD[Expert annotation sample]
  E_AUDIT[Artifact registry and dashboard]

  E_RQ1[RQ1 pipeline quality]
  E_RQ2[RQ2 categorization]
  E_RQ3[RQ3 ClimateBERT comparison]
  E_RQ4[RQ4 diagnostics]
  E_RQ5[RQ5 reproducibility]
  E_RQ6[RQ6 stability]

  E_DATA --> E_RQ1
  E_DATA --> E_RQ2
  E_DATA --> E_RQ4
  E_DATA --> E_RQ6
  E_PRED --> E_RQ3
  E_PRED --> E_RQ5
  E_GOLD --> E_RQ2
  E_GOLD --> E_RQ4
  E_AUDIT --> E_RQ5
  E_RQ3 --> E_RQ6
""".strip()

MISSING_PROCESS_MERMAID = """
flowchart LR
  M_GAP[Missing RQ evidence]
  M_IDENTIFY[Identify missing metric]
  M_SOURCE[Select source data]
  M_SAMPLE[Create targeted sample]
  M_RUN[Run analysis or annotation]
  M_METRIC[Compute metric]
  M_UPDATE[Update dashboard evidence]

  M_DATA[data output records]
  M_PRED[ClimateBERT prediction outputs]
  M_ANNOTATE[Manual annotation for RQ2 and RQ4]
  M_COMPARE[ClimateBERT comparison for RQ3]
  M_STABILITY[Prompt model stability for RQ6]

  M_GAP --> M_IDENTIFY
  M_IDENTIFY --> M_SOURCE
  M_SOURCE --> M_SAMPLE
  M_SAMPLE --> M_RUN
  M_RUN --> M_METRIC
  M_METRIC --> M_UPDATE

  M_SOURCE --> M_DATA
  M_SOURCE --> M_PRED
  M_RUN --> M_ANNOTATE
  M_RUN --> M_COMPARE
  M_RUN --> M_STABILITY
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


def load_absa_metrics(path: Path, extra_path: Path | None = None) -> pd.DataFrame:
    paths = [path]
    if extra_path is not None and extra_path.exists() and extra_path != path:
        paths.append(extra_path)
    if not any(candidate.exists() for candidate in paths):
        return pd.DataFrame(columns=["model", "accuracy", "precision", "recall", "f1", "is_nonzero"])

    rows = []
    for metrics_path in paths:
        if not metrics_path.exists():
            continue
        with metrics_path.open("r") as f:
            results = json.load(f)
        for model, metrics in results.items():
            accuracy = float(metrics.get("accuracy", 0) or 0)
            precision = float(metrics.get("precision", 0) or 0)
            recall = float(metrics.get("recall", 0) or 0)
            f1 = float(metrics.get("f1", 0) or 0)
            rows.append({
                "model": model,
                "metric_source": metrics_path.name,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "is_nonzero": any(value > 0 for value in [accuracy, precision, recall, f1]),
            })
    return pd.DataFrame(rows).sort_values(["f1", "accuracy"], ascending=False)


def load_image_explanations(path: Path) -> tuple[dict, pd.DataFrame]:
    if not path.exists():
        columns = [
            "id",
            "title",
            "category",
            "research_question_links",
            "source_path",
            "archived_path",
            "width",
            "height",
            "explanation",
            "thesis_use",
        ]
        return {}, pd.DataFrame(columns=columns)

    with path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    rows = manifest.get("images", [])
    df = pd.DataFrame(rows)
    return manifest, df


def status_interpretation(status: str) -> str:
    if status == "Available":
        return "Evidence already exists and can support the RQ, provided the source is traceable and the denominator is clear."
    if status == "Partial":
        return "Evidence exists, but it is incomplete, weakly validated, imbalanced, or only a proxy for the real metric."
    return "Evidence is missing. This row is a work item that must be completed before the RQ can be claimed strongly."


def route_for_item(rq: str, item: str) -> tuple[str, str]:
    lower = item.lower()
    if "climatebert" in lower or rq == "RQ3":
        if any(term in lower for term in ["scores", "run", "full local", "prediction"]):
            return "Run/continue ClimateBERT processing", "/ClimateBERT_Dataset_Processor"
        return "Open ClimateBERT result visualizer", "/ClimateBERT_Result_Visualizer"
    if any(term in lower for term in ["parsed", "json", "sentence", "field completion", "provenance", "records"]):
        return "Inspect parsed ESG JSON records", "/Parsed_ESG_JSON"
    if any(term in lower for term in ["sample", "n >=", "few-shot", "subgroup", "power"]):
        return "Open sample size reasoning", "/Sample_Size_Reasoning"
    if any(term in lower for term in ["tone", "pillar", "sentiment", "aspect", "language", "ontology", "taxonomy"]):
        return "Inspect parsed ESG distributions", "/Parsed_ESG_JSON"
    if any(term in lower for term in ["artifact", "dashboard", "replication", "prompt"]):
        return "Open dashboard landing page", "/"
    return "Open parsed ESG records", "/Parsed_ESG_JSON"


def available_result_for_item(rq: str, item: str) -> dict[str, str]:
    lower = item.lower()
    result = {
        "result": "Evidence exists for this row, but the result should be interpreted together with its denominator, source, and remaining validation gaps.",
        "interpretation": "This can support a descriptive claim, not necessarily a fully validated performance claim.",
        "visualization": "Use the RQ detail table, related dashboard page, and source records to inspect the evidence.",
    }

    if "pdf sustainability reports" in lower:
        result.update({
            "result": "6 sustainability reports are available: BEST, VKTR, GTRA, PTBA, ICR, and Indonet.",
            "interpretation": "This supports a pipeline feasibility claim across multiple reports. It is still small for broad generalization.",
            "visualization": "Treat this as the document coverage base. The key chart is document count and record count by filename.",
        })
    elif "markdown page outputs" in lower:
        result.update({
            "result": "OCR/markdown page outputs exist and provide traceability from extracted records back to source pages.",
            "interpretation": "This supports auditability: a reader can inspect where a sentence came from.",
            "visualization": "Use filename/page counts and source-page references in parsed outputs.",
        })
    elif "records-per-run" in lower:
        result.update({
            "result": "Current throughput evidence: mean 8.5 records/run overall and 14.3 records/run for Arcee.",
            "interpretation": "The extraction pipeline is productive enough to scale, but throughput differences may also show model/prompt bias.",
            "visualization": "Plot records per model, prompt, document, and run.",
        })
    elif "field completion" in lower:
        result.update({
            "result": "Core fields are complete for aspect/ESG/tone; sentiment_score is available for about 81.3%.",
            "interpretation": "The schema is mostly stable for core ABSA analysis, but score-based analysis has missingness.",
            "visualization": "Use a field-completion bar chart and missingness table.",
        })
    elif "tone x esg pillar" in lower or "tone × esg pillar" in lower:
        result.update({
            "result": "Current crosstab shows E commitment=91, G commitment=24, and S commitment=0.",
            "interpretation": "Environmental/Governance tone analysis is possible descriptively; Social is underrepresented and should not be generalized.",
            "visualization": "Use pillar x tone crosstab and stacked bar chart.",
        })
    elif "bilingual tone asymmetry" in lower:
        result.update({
            "result": "Observed outcome tone differs by language: Indonesian 7.9% vs English 21.8%.",
            "interpretation": "This is a promising bilingual asymmetry finding. It should be checked for document/prompt confounding.",
            "visualization": "Use language x tone bar chart and a two-proportion comparison.",
        })
    elif "sentiment score distribution" in lower:
        result.update({
            "result": "Outcome sentiment mean is around 0.60, while commitment mean is around 0.03.",
            "interpretation": "Sentiment appears to separate outcome-style evidence from commitment-style language, but calibration needs validation.",
            "visualization": "Use box/violin/histogram by tone and compare means.",
        })
    elif "llm-assigned climatebert" in lower:
        result.update({
            "result": "16 ClimateBERT-style label families are embedded in the LLM extraction JSON.",
            "interpretation": "This is useful as a proxy, but not a substitute for actual local ClimateBERT inference.",
            "visualization": "Use label-family counts and label x tone crosstabs.",
        })
    elif "co-occurrence" in lower:
        result.update({
            "result": "Commitment + climate-commitment co-occurrence appears 91 times.",
            "interpretation": "This suggests overlap between rhetorical commitment tone and climate-commitment labeling.",
            "visualization": "Use tone x climate-label crosstab.",
        })
    elif "complete extraction log" in lower:
        result.update({
            "result": "Run-level metadata exists for model, prompt, target, tone, sentiment, and label fields.",
            "interpretation": "This enables diagnostics by model and prompt rather than only aggregate output review.",
            "visualization": "Use error/missingness rates by model, prompt, and document.",
        })
    elif "schema drift" in lower:
        result.update({
            "result": "Known schema drift appears in 18 records, concentrated in data.md + GPT-oss-120b.",
            "interpretation": "The issue is likely configuration-specific, not a universal pipeline failure.",
            "visualization": "Use schema-drift rate by model x prompt.",
        })
    elif "missing tone" in lower:
        result.update({
            "result": "Missing tone appears in 61 records overall, but only 1/272 for Arcee-only valid records.",
            "interpretation": "Tone missingness is strongly model/prompt dependent.",
            "visualization": "Use missing-tone rate by model, prompt, document, language, and pillar.",
        })
    elif "root cause" in lower:
        result.update({
            "result": "Failures can be grouped by model x prompt; GPT-oss + data.md is a known high-failure configuration.",
            "interpretation": "The diagnostic framework can identify bad configurations rather than treating all extraction failures equally.",
            "visualization": "Use grouped failure-rate heatmaps.",
        })
    elif "json extraction artifacts" in lower or "static visualization" in lower or "streamlit dashboard" in lower or "artifact inventory" in lower:
        result.update({
            "result": "Core artifacts exist: JSON records, CSV/PNG outputs, and Streamlit pages.",
            "interpretation": "This supports reproducibility, but a formal replication checklist is still needed.",
            "visualization": "Use artifact inventory table and source-to-output lineage diagram.",
        })
    elif "prompt family effect" in lower:
        result.update({
            "result": "Prompt family effect is visible: CoT about 55% commitment, zero-shot about 21-24%, few-shot about 36%.",
            "interpretation": "Prompt choice materially affects ABSA tone outputs.",
            "visualization": "Use commitment rate by prompt family.",
        })
    elif "coefficient of variation" in lower:
        result.update({
            "result": "Prompt-level coefficient of variation is about 38.2%.",
            "interpretation": "This indicates high prompt instability and motivates ensemble/verification strategies.",
            "visualization": "Use CV table and per-prompt tone distribution bars.",
        })
    elif "language x prompt" in lower:
        result.update({
            "result": "CoT appears similar across English/Indonesian, while zero-shot English is higher than zero-shot Indonesian.",
            "interpretation": "There may be a language x prompt interaction, but it needs balanced matched data.",
            "visualization": "Use language x prompt x tone interaction chart.",
        })
    return result


def completion_plan_for_row(row: pd.Series) -> dict[str, str]:
    label, route = route_for_item(str(row["rq"]), str(row["item"]))
    if row["status"] == "Partial":
        framing = "Upgrade this partial evidence into defensible evidence."
    else:
        framing = "Complete this missing evidence item before making a strong claim."
    return {
        "framing": framing,
        "target_label": label,
        "target_route": route,
        "step_1": "Open the linked dashboard/data page and filter to the relevant RQ, document, model, prompt, or label family.",
        "step_2": f"Compute or collect the expected metric: {row['expected_metric']}",
        "step_3": "Add the computed metric and interpretation back into the RQ evidence table or thesis results section.",
    }


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
    columns = [
        "rq",
        "theme",
        "status",
        "status_meaning",
        "item",
        "what_it_does",
        "expected_metric",
        "if_yes_or_good",
        "if_underperforming",
        "likely_reason_if_weak",
        "next_action",
        "priority",
    ]
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
    return pd.DataFrame(rows, columns=columns)


with st.sidebar:
    st.header("Filters")
    priority_filter = st.multiselect(
        "Priority",
        ["Critical", "High", "Medium", "Important"],
        default=["Critical", "High", "Medium", "Important"],
    )
    rq_filter = st.multiselect("Research Questions", [item["rq"] for item in RQ_DATA])
    evidence_status_filter = st.multiselect(
        "Evidence status",
        ["Available", "Partial", "Needed"],
        default=["Available", "Partial", "Needed"],
    )
    view_mode = st.radio(
        "Detail view",
        ["Matrix", "Question Cards", "Metrics", "Detailed Explanation"],
        horizontal=False,
    )


selected_evidence_statuses = evidence_status_filter or ["Available", "Partial", "Needed"]
filtered = [
    item for item in RQ_DATA
    if item["priority"] in priority_filter and (not rq_filter or item["rq"] in rq_filter)
]
summary = status_counts(filtered)
detail_df = build_rq_detail_rows(filtered)
detail_df = detail_df[detail_df["status"].isin(selected_evidence_statuses)].reset_index(drop=True)
absa_metrics_df = load_absa_metrics(ABSA_METRICS_PATH, LOCAL_ABSA_METRICS_PATH)
nonzero_absa_metrics = absa_metrics_df[absa_metrics_df["is_nonzero"]] if not absa_metrics_df.empty else absa_metrics_df
image_manifest, image_explanations_df = load_image_explanations(IMAGE_EXPLANATIONS_PATH)

cols = st.columns(5)
cols[0].metric("Research questions", len(filtered))
cols[1].metric("Available evidence items", int(summary["available"].sum()) if not summary.empty else 0)
cols[2].metric("Partial evidence items", int(summary["partial"].sum()) if not summary.empty else 0)
cols[3].metric("Open needs", int(summary["needed"].sum()) if not summary.empty else 0)
cols[4].metric("Visible evidence rows", len(detail_df))
st.caption(f"Existing data: `{EXISTING_DATA_PATH}`")
st.caption(f"Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")
st.caption(f"ABSA metrics: `{ABSA_METRICS_PATH}`")
if LOCAL_ABSA_METRICS_PATH.exists():
    st.caption(f"Local rerun metrics: `{LOCAL_ABSA_METRICS_PATH}`")
st.caption(f"Image output explanations: `{IMAGE_EXPLANATIONS_PATH}`")

tab_overview, tab_details, tab_guide, tab_missing, tab_existing_pages, tab_image_results, tab_discussion, tab_absa_metrics, tab_mermaid, tab_plan, tab_source = st.tabs([
    "Overview",
    "RQ Details",
    "Table Guide",
    "Missing Work Process",
    "Existing Page Analyses",
    "Image Results",
    "Discussion",
    "ABSA Metrics",
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
        if not detail_df.empty:
            visible_chart = (
                detail_df.groupby(["rq", "status"])
                .size()
                .unstack(fill_value=0)
                .reindex(columns=selected_evidence_statuses, fill_value=0)
            )
            st.subheader("Visible Evidence Rows by RQ")
            st.bar_chart(visible_chart)

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

            if row["status"] == "Available":
                st.subheader("Available Result Interpretation")
                result_info = available_result_for_item(row["rq"], row["item"])
                r1, r2, r3 = st.columns(3)
                r1.metric("Status", "Available")
                r2.metric("RQ", row["rq"])
                r3.metric("Priority", row["priority"])
                st.markdown(f"**Current result:** {result_info['result']}")
                st.markdown(f"**Interpretation:** {result_info['interpretation']}")
                st.markdown(f"**How to visualize it:** {result_info['visualization']}")
                target_label, target_route = route_for_item(row["rq"], row["item"])
                st.link_button(target_label, target_route, use_container_width=True)
            else:
                st.subheader("Completion Redirect")
                plan = completion_plan_for_row(row)
                st.warning(plan["framing"])
                st.markdown(f"**Step 1:** {plan['step_1']}")
                st.markdown(f"**Step 2:** {plan['step_2']}")
                st.markdown(f"**Step 3:** {plan['step_3']}")
                st.link_button(plan["target_label"], plan["target_route"], use_container_width=True)

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

with tab_existing_pages:
    st.subheader("What the Existing Pages Already Analyze")
    st.write(
        "This section maps the existing Streamlit pages into thesis evidence. Pages that do not "
        "directly answer RQ1-RQ6 are kept as supporting or utility analyses instead of being forced "
        "into a research-question claim."
    )
    inventory_view = st.radio(
        "Inventory view",
        ["Grouped analyses", "All individual page files"],
        horizontal=True,
    )
    page_inventory = PAGE_ANALYSIS_INVENTORY.copy()
    file_inventory = PAGE_FILE_INVENTORY.copy()

    if inventory_view == "Grouped analyses":
        role_filter = st.multiselect(
            "Evidence role",
            page_inventory["evidence_role"].drop_duplicates().tolist(),
            default=page_inventory["evidence_role"].drop_duplicates().tolist(),
        )
        rq_page_filter = st.multiselect(
            "RQ link in existing pages",
            ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"],
            default=[],
        )
        if role_filter:
            page_inventory = page_inventory[page_inventory["evidence_role"].isin(role_filter)]
        if rq_page_filter:
            page_inventory = page_inventory[
                page_inventory["research_question_links"].apply(
                    lambda value: any(rq in str(value) for rq in rq_page_filter)
                )
            ]

        st.dataframe(page_inventory, use_container_width=True, height=460)
        if not page_inventory.empty:
            role_counts = page_inventory["evidence_role"].value_counts()
            st.bar_chart(role_counts)

            selected_group = st.selectbox("Explain analysis group", page_inventory["analysis_group"].tolist())
            selected = page_inventory[page_inventory["analysis_group"] == selected_group].iloc[0]
            st.markdown(f"**Pages:** {selected['pages']}")
            st.markdown(f"**What these pages do:** {selected['what_the_existing_pages_do']}")
            st.markdown(f"**RQ links:** {selected['research_question_links']}")
            st.markdown(f"**How to use in thesis:** {selected['how_to_use_in_thesis']}")
    else:
        relation_filter = st.multiselect(
            "Relation to RQs",
            file_inventory["relation_to_research_questions"].drop_duplicates().tolist(),
            default=file_inventory["relation_to_research_questions"].drop_duplicates().tolist(),
        )
        role_filter = st.multiselect(
            "Evidence role",
            file_inventory["evidence_role"].drop_duplicates().tolist(),
            default=file_inventory["evidence_role"].drop_duplicates().tolist(),
        )
        rq_page_filter = st.multiselect(
            "RQ link",
            ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"],
            default=[],
        )
        if relation_filter:
            file_inventory = file_inventory[
                file_inventory["relation_to_research_questions"].isin(relation_filter)
            ]
        if role_filter:
            file_inventory = file_inventory[file_inventory["evidence_role"].isin(role_filter)]
        if rq_page_filter:
            file_inventory = file_inventory[
                file_inventory["rq_links"].apply(
                    lambda value: any(rq in str(value) for rq in rq_page_filter)
                )
            ]

        st.dataframe(file_inventory, use_container_width=True, height=560)
        if not file_inventory.empty:
            c1, c2 = st.columns(2)
            c1.bar_chart(file_inventory["relation_to_research_questions"].value_counts())
            c2.bar_chart(file_inventory["evidence_role"].value_counts())

            selected_file = st.selectbox("Explain page file", file_inventory["file"].tolist())
            selected = file_inventory[file_inventory["file"] == selected_file].iloc[0]
            st.markdown(f"**Analysis:** {selected['analysis']}")
            st.markdown(f"**Relation:** {selected['relation_to_research_questions']}")
            st.markdown(f"**RQ links:** {selected['rq_links']}")
            st.markdown(f"**Evidence role:** {selected['evidence_role']}")
            st.markdown(f"**Why it matters or not:** {selected['why_it_matters_or_not']}")

with tab_image_results:
    st.subheader("Implemented Image Results and Explanations")
    if image_explanations_df.empty:
        st.warning(f"No image explanation manifest found at `{IMAGE_EXPLANATIONS_PATH}`.")
    else:
        st.write(
            "These images were archived from generated dashboard/result outputs and documented "
            "in JSON and Markdown. Each image has an implementation result, RQ linkage, source path, "
            "archive path, and thesis-use explanation."
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Archived images", int(image_manifest.get("image_count", len(image_explanations_df))))
        c2.metric("Categories", image_explanations_df["category"].nunique())
        linked_count = image_explanations_df["research_question_links"].apply(lambda value: bool(value)).sum()
        c3.metric("RQ-linked images", int(linked_count))

        category_filter = st.multiselect(
            "Image category",
            sorted(image_explanations_df["category"].dropna().unique()),
            default=sorted(image_explanations_df["category"].dropna().unique()),
        )
        rq_image_filter = st.multiselect(
            "RQ link",
            ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"],
            default=[],
        )
        display_images = image_explanations_df.copy()
        if category_filter:
            display_images = display_images[display_images["category"].isin(category_filter)]
        if rq_image_filter:
            display_images = display_images[
                display_images["research_question_links"].apply(
                    lambda links: any(rq in list(links or []) for rq in rq_image_filter)
                )
            ]

        table_cols = [
            "id", "title", "category", "research_question_links", "source_path",
            "archived_path", "width", "height", "explanation", "thesis_use",
        ]
        st.dataframe(display_images[table_cols], use_container_width=True, height=360)

        if not display_images.empty:
            selected_image_id = st.selectbox(
                "Open image explanation",
                display_images["id"].tolist(),
                format_func=lambda image_id: f"{image_id} - {display_images[display_images['id'] == image_id].iloc[0]['title']}",
            )
            image_row = display_images[display_images["id"] == selected_image_id].iloc[0]
            archived_abs_path = PAGE_DIR.parent / image_row["archived_path"]
            left, right = st.columns([1, 1])
            with left:
                if archived_abs_path.exists():
                    st.image(str(archived_abs_path), caption=image_row["title"], use_container_width=True)
                else:
                    st.warning(f"Archived image not found: `{archived_abs_path}`")
            with right:
                rq_links = ", ".join(image_row["research_question_links"]) or "Not directly linked"
                st.markdown(f"**Category:** {image_row['category']}")
                st.markdown(f"**RQ links:** {rq_links}")
                st.markdown(f"**Source path:** `{image_row['source_path']}`")
                st.markdown(f"**Archived path:** `{image_row['archived_path']}`")
                st.markdown(f"**Implementation result:** {image_row['explanation']}")
                st.markdown(f"**Thesis discussion use:** {image_row['thesis_use']}")

        st.subheader("Image Evidence by Research Question")
        rq_rows = []
        for _, row in image_explanations_df.iterrows():
            for rq in row["research_question_links"] or []:
                rq_rows.append({
                    "rq": rq,
                    "image": row["title"],
                    "category": row["category"],
                    "implementation_result": row["explanation"],
                    "discussion_use": row["thesis_use"],
                })
        if rq_rows:
            rq_image_df = pd.DataFrame(rq_rows)
            st.dataframe(rq_image_df, use_container_width=True, height=300)
            st.bar_chart(rq_image_df["rq"].value_counts().sort_index())
        else:
            st.info("No RQ-linked image evidence found.")

with tab_discussion:
    st.subheader("Research Question Discussion")
    st.write(
        "This discussion synthesizes the current tables, metrics, image outputs, and remaining gaps. "
        "It is written as thesis interpretation rather than page-operation documentation."
    )
    discussion_df = RQ_DISCUSSIONS.copy()
    if rq_filter:
        discussion_df = discussion_df[discussion_df["rq"].isin(rq_filter)]
    st.dataframe(discussion_df, use_container_width=True, height=360)

    if not discussion_df.empty:
        selected_discussion_rq = st.selectbox(
            "Detailed RQ discussion",
            discussion_df["rq"].tolist(),
            format_func=lambda rq: f"{rq} - {discussion_df[discussion_df['rq'] == rq].iloc[0]['theme']}",
        )
        row = discussion_df[discussion_df["rq"] == selected_discussion_rq].iloc[0]
        st.markdown(f"**Discussion:** {row['discussion']}")
        st.markdown(f"**Results interpretation:** {row['results_interpretation']}")
        st.markdown(f"**Limitation:** {row['limitation']}")
        st.markdown(f"**Next step:** {row['next_step']}")

        linked_images = image_explanations_df[
            image_explanations_df["research_question_links"].apply(
                lambda links: selected_discussion_rq in list(links or [])
            )
        ] if not image_explanations_df.empty else pd.DataFrame()
        if not linked_images.empty:
            st.subheader(f"Images Supporting {selected_discussion_rq}")
            for _, image_row in linked_images.iterrows():
                with st.expander(f"{image_row['id']} - {image_row['title']}"):
                    archived_abs_path = PAGE_DIR.parent / image_row["archived_path"]
                    if archived_abs_path.exists():
                        st.image(str(archived_abs_path), caption=image_row["title"], use_container_width=True)
                    st.markdown(f"**Implementation result:** {image_row['explanation']}")
                    st.markdown(f"**Discussion use:** {image_row['thesis_use']}")

    st.subheader("General Discussion")
    for paragraph in GENERAL_DISCUSSION:
        st.write(paragraph)

    st.subheader("Conclusion")
    for paragraph in CONCLUSION_TEXT:
        st.write(paragraph)

with tab_absa_metrics:
    st.subheader("ABSA Metrics Results from the Metrics Visualizer")
    if absa_metrics_df.empty:
        st.warning(f"No ABSA metrics JSON found at `{ABSA_METRICS_PATH}`.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Model outputs", len(absa_metrics_df))
        m2.metric("Non-zero outputs", len(nonzero_absa_metrics))
        best = absa_metrics_df.iloc[0]
        m3.metric("Best F1", f"{best['f1']:.4f}", best["model"])
        m4.metric("Best accuracy", f"{absa_metrics_df['accuracy'].max():.4f}")

        st.write(
            "These are the saved ABSA/ClimateBERT-style alignment metrics used by "
            "`absa_metrics_visualization.py`. Low or zero scores should be interpreted as "
            "label-space mismatch evidence for RQ3, not as a final ABSA model-quality claim."
        )
        st.dataframe(absa_metrics_df, use_container_width=True, height=420)
        st.bar_chart(absa_metrics_df.set_index("model")[["accuracy", "precision", "recall", "f1"]])

        if not nonzero_absa_metrics.empty:
            st.subheader("Non-zero Results")
            st.dataframe(nonzero_absa_metrics, use_container_width=True)
        zero_models = absa_metrics_df.loc[~absa_metrics_df["is_nonzero"], "model"].tolist()
        if zero_models:
            st.subheader("Zero Results")
            st.write(", ".join(zero_models))

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
    full_map_code = build_full_rq_map_mermaid(detail_df)
    render_mermaid(full_map_code, height=520)
    st.code(full_map_code, language="mermaid")

    st.subheader("Workflow Diagram")
    workflow_code = build_workflow_mermaid()
    render_mermaid(workflow_code, height=430)
    st.code(workflow_code, language="mermaid")

    st.subheader("Missing Evidence Process")
    missing_process_code = build_missing_process_mermaid()
    render_mermaid(missing_process_code, height=430)
    st.code(missing_process_code, language="mermaid")

with tab_plan:
    st.subheader("Prioritized Next Analyses")
    plan = ANALYSIS_PLAN[ANALYSIS_PLAN["urgency"].isin(priority_filter)]
    st.dataframe(plan, use_container_width=True)
    if not plan.empty:
        st.bar_chart(plan["answers"].str.get_dummies(sep=", ").sum().sort_values(ascending=False))

with tab_source:
    st.caption(f"Source: `{SOURCE_HTML}`")
    st.info("This Streamlit page is a native visualization distilled from the HTML thesis benchmark artifact.")
