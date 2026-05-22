# Streamlit Page Documentation

This document explains what each Streamlit page in this workspace talks about, how it fits into the ESG thesis workflow, and how the page contributes to the evidence layer used in Chapters 4-6.

Reference read-through used for documentation style:

- `research_references/nbnfioulu-202506124422.pdf`
- Title: *Towards Behaviour-Aware Multimodal Video Summarization: Integrating Visual, Audio, and Textual Cues for Human-Centric Content Analysis*
- Author: Md Moinul Islam, University of Oulu, June 2025

The reference thesis is useful as a documentation model because it presents a full computational research pipeline: motivation, research questions, related work, methodology, data preparation, feature extraction, pseudo-ground truth generation, experiments, ablation studies, discussion, limitations, and conclusions. The ESG thesis application follows a similar structure, but for sustainability-report processing: OCR, LLM extraction, ClimateBERT validation, ground-truth annotation, ontology mapping, artifact lineage, dashboards, and thesis chapter integration.

## How To Read This App

The Streamlit app is organized as an executable thesis workspace. It is not only a dashboard collection. Each page either generates evidence, audits evidence, visualizes evidence, maps evidence to research questions, or translates evidence into thesis chapters.

The pages can be read in this order:

1. Navigation and workflow pages explain the whole thesis system.
2. OCR and source metadata pages prepare sustainability-report inputs.
3. LLM processing pages generate structured ESG records.
4. Ground-truth and ClimateBERT pages validate the extracted records.
5. Ontology and graph-export pages turn ABSA outputs into semantic artifacts.
6. Research question pages connect outputs to thesis claims.
7. Chapter pages translate live results into Chapter 4, Chapter 5, and Chapter 6 material.

## Source Reference PDF Summary

The reference PDF proposes a behaviour-aware multimodal video summarization framework. Its core idea is that summaries improve when text, audio, and visual behaviour are aligned rather than processed independently. It uses visual signals, prosodic audio cues, and transcript text, then combines them through heuristic and transformer-based approaches. It also uses LLM-generated pseudo-ground truth to address limited human annotation data.

Important ideas that transfer to this ESG Streamlit project:

- Pipeline documentation should show how raw data becomes structured evidence.
- Each research question should be linked to a concrete artifact and evaluation method.
- Generated outputs should be auditable, not only displayed.
- Pseudo-ground truth and human annotation should be clearly separated.
- Model comparison should include ablation, stability, and reliability checks.
- Limitations should be grounded in observed artifacts such as missing fields, parsing failures, OCR quality, or annotation gaps.

## Page Groups

### Navigation, Catalogs, And Thesis Planning

#### `pages/0_0_Streamlit_Page_Workflow.py`

This page is the main navigation and documentation hub for the Streamlit application. It explains the workflow across all pages, maps pages to research questions, and provides a high-level route through the thesis evidence system. It is useful when you need to understand which page supports which RQ, chapter, artifact, or dashboard.

#### `pages/0_2_JSON_Ontology_Usage_Map.py`

This page explains how JSON ontology, category, grouping, and mapping files are used across the app. It helps identify which ontology files are active, which pages consume them, and where the same mapping logic should be reused. It is mainly a governance page for taxonomy and ontology consistency.

#### `pages/0_3_OCR_Company_Metadata_Labeler.py`

This page assigns company labels and IDX-style sector metadata to OCR document folders. It bridges raw report folders and analysis-ready company metadata. Its output supports company-level filtering, sector comparisons, and later ESG profile analysis.

#### `pages/0_4_Sustainable_Framework_API_Reader.py`

This page reads the live Sustainable Framework API catalog and endpoint responses. It provides a dropdown-driven API reader for datasets such as planning, patent analysis, research groups, and other shortcut endpoints exposed by the API. It is useful for inspecting external structured reference data and exporting API snapshots.

#### `pages/0_5_Thesis_Systematic_Workflow.py`

This page translates the thesis draft into an executable workflow. It explains what data can be generated, which scripts or pages generate it, and how the outputs integrate into the research questions and chapters. It works as the planning bridge between the written thesis and the running Streamlit system.

#### `pages/3_0_Thesis_Action_Plan.py`

This is the operational command center for completing the thesis. It tracks Step 1 through Step 6, including ClimateBERT outputs, pilot annotation, LLM reruns, prompt stability, failure modes, and ontology mapping. It also contains live status counters, refresh/migration controls, PDF-by-prompt processing matrices, and progress views for background jobs.

#### `pages/5_Thesis_Systematic_Workflow_dashboard.py`

This page visualizes the systematic workflow outputs as charts and thesis-ready evidence. It turns the planning workflow into a report-style dashboard with pipeline coverage, diagnostics, stability summaries, ground-truth progress, and artifact images.

### OCR And Input Preparation

#### `pages/Bulk_OCR.py`

This page runs or manages the bulk OCR pipeline for PDF sustainability reports. It is the first major data-generation step because it converts raw PDF documents into OCR text and markdown-like page outputs. These outputs later feed LLM extraction and page-level quality audits.

#### `pages/1_2_OCR_Quality_Workbench.py`

This page measures OCR quality using CER/WER-style sampling. It exists because OCR errors can affect all downstream extraction, tone labels, aspect labels, and validation metrics. Its evidence supports limitations and reliability discussion in Chapter 5.

#### `pages/2_4_PDF_Page_Processing_Audit.py`

This page audits PDF pages at the page level. It shows which pages were selected, processed, failed, or missing LLM output. It helps diagnose whether gaps in ESG extraction come from missing OCR pages, skipped pages, failed jobs, or later parsing problems.

#### `pages/2_2_LLM_Statement_Page_Verifier.py`

This page maps extracted LLM statements back to OCR markdown pages. It checks whether extracted ESG statements are actually present in the source text. This is a provenance and factuality page: it supports evidence traceability from a structured record back to the original page.

### LLM Processing And Background Jobs

#### `pages/llm_processing.py`

This page runs the combined ESG pipeline: T1 ClimateBERT predictions, T2 ABSA analysis, and T3 LLM-based ESG structured extraction. It is an interactive execution page where the user can choose input mode, models, prompts, generation settings, and view outputs/events.

#### `pages/2_0_LLM_Processing_Result_Visualizer.py`

This page visualizes outputs produced by `llm_processing.py`. It shows T1, T2, and T3 records, pipeline waterfalls, run quality, ABSA fields, ClimateBERT labels, and exportable tables. It is the main visual audit page for combined LLM pipeline results.

#### `pages/2_1_LLM_Error_Parse_Audit.py`

This page focuses on parsing and failure diagnostics inside `results/esg_records.json`. It separates parsed records, raw-only outputs, failed outputs, and unresolved cases. It supports the thesis discussion on schema drift, JSON parse reliability, and LLM extraction limitations.

#### `pages/2_3_LLM_Background_Run_Monitor.py`

This page manages long-running LLM extraction jobs in the background. It tracks job IDs, progress, provider/model settings, cloned reruns, logs, events, and configuration files. It is important for reproducibility because each job can be tied to a prompt, provider, model, config, and output artifact.

#### `pages/2_5_LLM_Model_Catalog_Visualizer.py`

This page reads and visualizes the LLM model workbook. It lets the user select models from dropdowns and inspect model descriptions or metadata. It supports model-selection decisions for OpenRouter, Ollama, LM Studio, and other providers.

### Ground Truth, Annotation, And Validation

#### `pages/ground_truth.py`

This page runs the resumable ESG ground-truth pipeline. It supports T1 and T2 processing, resume-from-previous-run behavior, ClimateBERT/local-model options, prompt templates, and saved output visualization. It is the main page for producing and resuming ground-truth-related outputs.

#### `pages/1_1_Ground_Truth_Workbench.py`

This page is the human annotation workbench. It supports pilot annotation for tone, ESG pillar, and aspect labels. It is used to create or update human labels that can later be compared against extracted records, proxy labels, or model outputs.

#### `pages/1_3_Ground_Truth_Metrics.py`

This page calculates formal metrics from available ground-truth labels. It covers accuracy, F1, Cohen kappa, confusion matrices, and error tables for tone, ESG, and aspect labels. It supports the validation claims in Chapter 4 and reliability discussion in Chapter 5.

#### `pages/1_4_ClimateBERT_Record_Batch.py`

This page prepares extracted ESG records for ClimateBERT validation and imports real ClimateBERT outputs. It compares proxy labels with model labels and exports agreement data. It is central to RQ3, where tone labels are compared against climate-focused labels.

#### `pages/1_8_Ground_Truth_Output_Visualizer.py`

This page visualizes pilot ground-truth outputs, annotation coverage, silver-label comparisons, and records needing review. It is the main inspection page for seeing whether human labels and model labels are complete enough for evaluation.

#### `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`

This page visualizes saved `ground_truth.py` outputs across T1 model predictions, model-load failures, T2 rule/hybrid labels, ontology alignment, and greenwashing metrics. It connects raw ground-truth outputs to higher-level validation and diagnostic summaries.

#### `pages/1_10_Ground_Truth_Run_Coverage.py`

This page tracks which source records have been processed by `ground_truth.py` and which remain incomplete. It shows T1 matrices, T2 coverage, missing work, raw tables, and graph attachment cards. It is useful when resuming a large batch and avoiding duplicate work.

#### `pages/1_11_Ground_Truth_Record_Audit.py`

This page audits saved ground-truth outputs per source label and joins T1 and T2 results. It helps verify whether each source, label, model, and prediction path has been processed correctly. It is a record-level inspection page for debugging ground-truth outputs.

#### `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`

This page walks through the exact files produced by `ground_truth.py`. It shows source records, extracted text units, processing coverage, T1 raw output, T1 predictions, T2 raw output, T2 hybrid output, audits, exports, and attachment cards. It is the most detailed page for step-by-step ground-truth pipeline understanding.

### ESG Flow, Ontology, And Semantic Graphs

#### `pages/1_5_ESG_Flow_Sankey.py`

This page visualizes ESG flows across company/source, ESG pillar, aspect, tone, prompt, and review issues. It is useful for seeing how extracted records move through the ABSA dimensions and where the dominant paths or bottlenecks are.

#### `pages/1_6_Ontology_Path_Viewer.py`

This page traces records from raw text to predicted aspect and ontology path. It shows coverage, path exploration, ontology JSON files, and unmapped aspects. It supports the thesis contribution around Indonesian ESG vocabulary extension and ontology gaps.

#### `pages/1_13_Semantic_Graph_Exporter.py`

This page exports the ESG evidence layer into semantic graph formats: RDF Turtle, OWL/RDF-XML, and Neo4j import files. It turns ABSA records, ontology mappings, documents, prompts, and extracted evidence into graph-ready artifacts for semantic querying and GraphRAG-style workflows.

### Tone, ClimateBERT, Revision, And Research Question Dashboards

#### `pages/0_9_Tone_ClimateBERT_Visualization.py`

This page compares existing ESG tone extraction results with ClimateBERT-style labels. It provides tone comparison charts, ClimateBERT run views, record tables, documentation, and attachment cards. It is a major visual page for RQ3 and construct validity discussion.

#### `pages/1_0_Revision_Analytics.py`

This page collects analyses requested by revision feedback. It covers prompt stability, agreement, greenwashing index, failure modes, language triggers, ontology coverage, OCR scaffolding, artifacts, and attachment cards. It is a reviewer-facing analytics page that translates feedback into measurable checks.

#### `pages/1_7_Research_Questions_Dashboard.py`

This page maps the thesis research questions to evidence, benchmarks, sample-size reasoning, existing results, planned analyses, and chapter-level conclusions. It is the main RQ dashboard and is useful for explaining what each RQ has already produced and what evidence is still missing.

### Thesis Draft, Integration, And Chapter Pages

#### `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`

This page integrates `thesis_draft_1.pdf`, `thesis_chapters_4_5_6.docx`, result artifacts, Streamlit pages, Mermaid maps, and edge labels. It provides the thesis spine, RQ evidence map, pipeline map, validation loop, artifact lineage, source outlines, evidence tables, and attachment cards. It is the system-level map of the whole thesis.

#### `pages/6_1_Chapter_4_Implementation_Results.py`

This page translates Chapter 4 into an interactive implementation-and-results page. It shows chapter text beside live action-plan evidence, RQ1-RQ6 result sections, figure galleries, and graph attachment cards. It is used to keep Chapter 4 synchronized with current data.

#### `pages/6_2_Chapter_5_Discussion.py`

This page translates Chapter 5 into an interactive discussion page. It presents live discussion claims, key findings, limitations, diagnostics, and attachment cards. It is where model divergence, schema drift, OCR limitations, ontology gaps, and construct validity are interpreted.

#### `pages/6_3_Chapter_6_Conclusion.py`

This page translates Chapter 6 into an interactive conclusion page. It summarizes contributions, research question answers, future work, and live conclusion claims. It is used to connect empirical results back to thesis answers and forward-looking research directions.

#### `pages/6_4_ch4-6.py`

This page reads `thesis_ch4_6_structure_benchmarks.docx`, the updated graph-attached DOCX, and live evidence used by Chapter 4, Chapter 5, and Chapter 6. It contains DOCX summaries, graph attachments, benchmark checklist outputs, live charts, chapter mapping, and counters mirrored from the Thesis Action Plan. It is the main appendix-style page for graph/table attachments.

## Complete Page Inventory

| Page | Main topic | Thesis role |
|---|---|---|
| `0_0_Streamlit_Page_Workflow.py` | App navigation, page inventory, RQ workflow map | Helps readers understand the whole Streamlit evidence system |
| `0_2_JSON_Ontology_Usage_Map.py` | JSON ontology and mapping-file usage | Keeps taxonomy and ontology references consistent |
| `0_3_OCR_Company_Metadata_Labeler.py` | Company and sector labels for OCR folders | Adds company metadata for later analysis |
| `0_4_Sustainable_Framework_API_Reader.py` | Live API catalog and endpoint reader | Imports and inspects external structured reference data |
| `0_5_Thesis_Systematic_Workflow.py` | Executable thesis workflow | Converts thesis draft into data-generation steps |
| `0_9_Tone_ClimateBERT_Visualization.py` | Tone versus ClimateBERT comparison | Supports RQ3 and construct-validity analysis |
| `1_0_Revision_Analytics.py` | Reviewer-requested analytics | Converts revision feedback into measurable checks |
| `1_1_Ground_Truth_Workbench.py` | Human annotation workbench | Produces pilot labels for validation |
| `1_2_OCR_Quality_Workbench.py` | OCR quality sampling | Supports OCR limitation and reliability claims |
| `1_3_Ground_Truth_Metrics.py` | Accuracy, F1, kappa, confusion matrices | Formal validation metrics |
| `1_4_ClimateBERT_Record_Batch.py` | ClimateBERT batch validation | Compares ESG tone records with climate labels |
| `1_5_ESG_Flow_Sankey.py` | ESG flow paths | Shows how records move through source, ESG, aspect, tone, and prompt |
| `1_6_Ontology_Path_Viewer.py` | Ontology coverage and unmapped aspects | Supports ontology extension contribution |
| `1_7_Research_Questions_Dashboard.py` | RQ evidence and benchmark dashboard | Connects results to RQ1-RQ6 |
| `1_8_Ground_Truth_Output_Visualizer.py` | Ground-truth output inspection | Shows label coverage and review queues |
| `1_9_Ground_Truth_Pipeline_Output_Visualizer.py` | Saved ground-truth pipeline outputs | Audits T1/T2 outputs and ontology/greenwashing fields |
| `1_10_Ground_Truth_Run_Coverage.py` | Ground-truth processing coverage | Tracks completed and missing work |
| `1_11_Ground_Truth_Record_Audit.py` | Record-level T1/T2 audit | Debugs per-record ground-truth outputs |
| `1_12_Ground_Truth_Step_By_Step_Visualizer.py` | Step-by-step ground-truth file visualizer | Explains exactly how `ground_truth.py` outputs are produced |
| `1_13_Semantic_Graph_Exporter.py` | RDF, OWL, Neo4j exports | Converts ESG evidence into graph-ready artifacts |
| `2_0_LLM_Processing_Result_Visualizer.py` | T1/T2/T3 pipeline result visualizer | Audits combined LLM processing outputs |
| `2_1_LLM_Error_Parse_Audit.py` | Parse failures and raw-only outputs | Supports LLM reliability and schema-drift analysis |
| `2_2_LLM_Statement_Page_Verifier.py` | Statement-to-page verification | Checks source provenance for extracted claims |
| `2_3_LLM_Background_Run_Monitor.py` | Background LLM job runner | Provides reproducible job execution and rerun controls |
| `2_4_PDF_Page_Processing_Audit.py` | Page-level processing audit | Explains page-level gaps in LLM outputs |
| `2_5_LLM_Model_Catalog_Visualizer.py` | LLM model workbook reader | Helps choose and describe candidate models |
| `3_0_Thesis_Action_Plan.py` | Thesis completion action plan | Central operational page for running, refreshing, and validating work |
| `5_Thesis_Systematic_Workflow_dashboard.py` | Workflow dashboard | Turns workflow outputs into thesis-style visuals |
| `6_0_Thesis_Draft_Chapter_Integration_Mermaid.py` | Integrated Mermaid thesis map | Shows thesis spine, RQ evidence, pipeline, validation, artifact lineage |
| `6_1_Chapter_4_Implementation_Results.py` | Live Chapter 4 results | Converts current artifacts into Chapter 4 evidence |
| `6_2_Chapter_5_Discussion.py` | Live Chapter 5 discussion | Interprets results, limitations, and construct validity |
| `6_3_Chapter_6_Conclusion.py` | Live Chapter 6 conclusion | Summarizes answers, contributions, and future work |
| `6_4_ch4-6.py` | Ch4-6 graph/table attachment page | Shows graph attachments, backing tables, benchmark checks, and live counters |
| `Bulk_OCR.py` | Bulk OCR execution | Converts PDF reports into text sources |
| `ground_truth.py` | Resumable ESG ground-truth pipeline | Generates T1/T2 validation artifacts |
| `llm_processing.py` | Combined ESG pipeline | Runs ClimateBERT, ABSA, and LLM extraction |

## Research Question Alignment

### RQ1: PDF-to-Structured ESG Transformation

Relevant pages:

- `Bulk_OCR.py`
- `2_4_PDF_Page_Processing_Audit.py`
- `2_0_LLM_Processing_Result_Visualizer.py`
- `2_2_LLM_Statement_Page_Verifier.py`
- `3_0_Thesis_Action_Plan.py`
- `6_1_Chapter_4_Implementation_Results.py`

These pages explain how raw sustainability reports become OCR text, page-level artifacts, extracted ESG records, and provenance-checked statements.

### RQ2: ABSA Schema For ESG Tone, Pillar, And Aspect

Relevant pages:

- `ground_truth.py`
- `1_1_Ground_Truth_Workbench.py`
- `1_3_Ground_Truth_Metrics.py`
- `1_5_ESG_Flow_Sankey.py`
- `1_8_Ground_Truth_Output_Visualizer.py`
- `1_12_Ground_Truth_Step_By_Step_Visualizer.py`
- `6_4_ch4-6.py`

These pages explain how the ESG ABSA labels are created, inspected, validated, and visualized.

### RQ3: Tone Versus ClimateBERT

Relevant pages:

- `0_9_Tone_ClimateBERT_Visualization.py`
- `1_4_ClimateBERT_Record_Batch.py`
- `1_3_Ground_Truth_Metrics.py`
- `3_0_Thesis_Action_Plan.py`
- `6_1_Chapter_4_Implementation_Results.py`
- `6_2_Chapter_5_Discussion.py`

These pages compare ESG tone labels with ClimateBERT-style climate labels and support construct-validity discussion.

### RQ4: Diagnostics, Failure Modes, And Ontology Gaps

Relevant pages:

- `2_1_LLM_Error_Parse_Audit.py`
- `1_0_Revision_Analytics.py`
- `1_6_Ontology_Path_Viewer.py`
- `1_13_Semantic_Graph_Exporter.py`
- `6_2_Chapter_5_Discussion.py`

These pages explain schema drift, missing fields, OCR loss, bilingual issues, unmapped aspects, and ontology extension opportunities.

### RQ5: Reproducibility And Artifact Lineage

Relevant pages:

- `2_3_LLM_Background_Run_Monitor.py`
- `0_0_Streamlit_Page_Workflow.py`
- `6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`
- `6_4_ch4-6.py`
- `3_0_Thesis_Action_Plan.py`

These pages connect job configs, status files, events, output records, dashboards, figures, and thesis claims into a reproducible evidence trail.

### RQ6: Model And Prompt Stability

Relevant pages:

- `2_3_LLM_Background_Run_Monitor.py`
- `2_5_LLM_Model_Catalog_Visualizer.py`
- `1_0_Revision_Analytics.py`
- `3_0_Thesis_Action_Plan.py`
- `5_Thesis_Systematic_Workflow_dashboard.py`
- `6_3_Chapter_6_Conclusion.py`

These pages support model comparison, repeated runs, prompt stability, parse success, missing-tone rates, and provider/model selection.

## Chapter Alignment

### Chapter 4: Implementation And Results

Primary pages:

- `6_1_Chapter_4_Implementation_Results.py`
- `6_4_ch4-6.py`
- `1_7_Research_Questions_Dashboard.py`
- `3_0_Thesis_Action_Plan.py`

Chapter 4 should use these pages for implementation evidence, result tables, graph attachments, and current run counters.

### Chapter 5: Discussion

Primary pages:

- `6_2_Chapter_5_Discussion.py`
- `1_0_Revision_Analytics.py`
- `2_1_LLM_Error_Parse_Audit.py`
- `1_6_Ontology_Path_Viewer.py`
- `0_9_Tone_ClimateBERT_Visualization.py`

Chapter 5 should use these pages to interpret model disagreement, validation limits, ontology gaps, prompt sensitivity, and extraction failures.

### Chapter 6: Conclusion

Primary pages:

- `6_3_Chapter_6_Conclusion.py`
- `6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`
- `1_13_Semantic_Graph_Exporter.py`
- `5_Thesis_Systematic_Workflow_dashboard.py`

Chapter 6 should use these pages to summarize research contributions, reproducibility, graph-export potential, and future work.

## Core Artifacts Mentioned Across Pages

Common backing files include:

- `results/esg_records.json`
- `results/tone_records_flat.csv`
- `results/tone_esg_crosstab.csv`
- `results/tone_climatebert_label_crosstab.csv`
- `results/model_stability_summary.csv`
- `results/prompt_stability_summary.csv`
- `results/failure_mode_counts.csv`
- `results/ontology_coverage.csv`
- `results/climatebert_proxy_agreement_summary.csv`
- `results/visualizations/*.png`
- background job folders containing config, status, control, event, and log files

These files form the thesis evidence layer. The Streamlit pages should make each artifact inspectable through a graph, a table, a redirect/open-page action, and a connection to the relevant chapter or research question.

## Practical Usage Notes

- Use `3_0_Thesis_Action_Plan.py` first when you want the current state of the thesis pipeline.
- Use `6_4_ch4-6.py` when you need thesis-ready graph attachments and backing tables.
- Use `6_0_Thesis_Draft_Chapter_Integration_Mermaid.py` when you need to explain how source documents, artifacts, pages, and thesis chapters connect.
- Use `1_12_Ground_Truth_Step_By_Step_Visualizer.py` when debugging `ground_truth.py`.
- Use `2_3_LLM_Background_Run_Monitor.py` when launching or auditing long LLM runs.
- Use `1_13_Semantic_Graph_Exporter.py` when exporting the evidence layer to RDF, OWL, or Neo4j.

