# Repository Code Documentation

This document is the repository-wide reference for the workspace at `/home/ubuntu/apps/benchmarks/new_page`.

It complements, rather than replaces:

- `documentation.md` for the main Streamlit page set
- `code_documentation/high_level_pseudocode.md` for file-by-file pseudocode
- `documentation_*.md` for research-track writeups
- `documentation_data_inventory.md` for the data layer
- `documentation_apps_inventory.md` for runnable apps
- `documentation_pages_inventory.md` for the full `pages/` surface
- `documentation_code_inventory.md` for the full `code/` module inventory
- `documentation_results_inventory.md` for the `results/` inventory and schemas
- `complete_documentation_master.md` for the polished master overview

The goal here is broader coverage: data, apps, pages, results, background-job artifacts, shared code, and supporting tooling.

## 1. Repository Purpose

This repository is an executable research workspace for Indonesian ESG sustainability-report analysis. The main workflow is:

1. Collect PDF sustainability and annual reports.
2. OCR them into page-level markdown and extracted images.
3. Run LLM-based extraction and tone / ESG / aspect analysis.
4. Run ClimateBERT-style validation or comparison models.
5. Build human-annotation and ground-truth layers.
6. Export metrics, visualizations, semantic graph artifacts, and thesis-ready chapter evidence.
7. Use Streamlit dashboards to inspect the pipeline, diagnose errors, and assemble thesis outputs.

The codebase is not a single app. It is a collection of:

- a multi-page thesis dashboard
- several standalone Streamlit research apps
- lightweight APIs and utilities
- large data and result stores
- thesis-writing and documentation assets

## 2. Top-Level Structure

### Core entrypoints

- `app.py`
  - Main Streamlit hub for the thesis dashboard.
  - Uses `st.page_link(...)` to point into the important pages under `pages/`.
  - This is the correct file to launch when you want Streamlit to discover sibling pages.

- `_page_runtime_controls.py`
  - Shared runtime helper for page-level freeze / refresh behavior.
  - Intended to reduce unnecessary reruns for heavy dashboards.

- `Makefile`
  - Run-management entrypoint for reproducible output folders and manifests.
  - Delegates to scripts in `scripts/`.

- `requirements.txt`
  - Python dependency list for Streamlit, analysis, visualization, and model tooling.

### Major directories

- `pages/`
  - Main multi-page Streamlit thesis application.
- `code/`
  - Shared Python logic reused by pages and workers.
- `data/`
  - Source datasets, OCR corpora, spreadsheets, snapshots, and auxiliary inputs.
- `results/`
  - Derived artifacts, model outputs, charts, audits, and background-job state.
- `api/`
  - Lightweight HTTP utilities, including a documentation API and ClimateBERT client.
- `chatbot/`, `fact_checking/`, `fine_tuning/`, `llm_as_a_judge/`, `social_network_analysis/`, `summarization/`, `topic_modelling/`, `transfer_learning/`
  - Standalone research-track apps and experiment packages.
- `documentation/`, `docs/`, `code_documentation/`
  - Human-readable project and thesis documentation.
- `scripts/`, `tools/`, `templates/`
  - Reproducibility and artifact-generation tooling.

## 3. Data Layer

The data layer is large and heterogeneous. It includes both human-curated tables and machine-generated OCR corpora.

### 3.1 `data/thesis_pdf/`

- Primary PDF corpus for the thesis workflow.
- Contains `193` PDF files at the time of inspection.
- These are the original report-level source documents.
- Filenames typically encode company name, year, and whether the source is an annual report, sustainability report, or integrated report.

Typical usage:

- Input to bulk OCR workflows.
- Reference source for researcher and inventory dashboards.
- Canonical raw source when tracing a result back to the document level.

### 3.2 `data/thesis_dataset/`

- OCR-expanded corpus derived from the PDF set.
- Contains `189` document folders at the time of inspection.
- Each folder represents one OCR-processed report.

Typical folder layout:

- `ocr_result.json`
  - Main OCR payload for the document.
  - Contains a `pages` array with fields such as:
    - `index`
    - `markdown`
    - `images`
    - `tables`
    - `hyperlinks`
    - `dimensions`
    - `confidence_scores`
- `pages/`
  - Page-level markdown files such as `page_0001.md`.
  - These are used by page verifiers, OCR audits, and batching logic.
- `images/`
  - Extracted page-region image assets such as `img-0.jpeg`.

This directory is the most important machine-readable corpus in the repository. Many pages and workers assume that a document can be addressed via:

- a document folder
- page markdown files
- OCR JSON
- extracted images

### 3.3 `data/idx_data.csv`

- Structured IDX-oriented source table.
- Used by cataloging and metadata pages.
- Likely acts as a bridge between public market entities and report-level assets.

### 3.4 `data/ESG Score.xlsx`

- Spreadsheet-style ESG reference artifact.
- Exposed in the researcher tools as a tabular source.
- Used as a supporting benchmark or lookup source rather than a pipeline-native artifact.

### 3.5 `data/stock_info/`

- HTML snapshots organized by market sector.
- Example sector folders include:
  - `carisaham.com_emiten_sektor_energi`
  - `carisaham.com_emiten_sektor_keuangan`
  - `carisaham.com_emiten_sektor_teknologi`
- Each sector folder contains a `rendered.html` snapshot.

Probable role:

- Company metadata enrichment.
- Sector classification support.
- External market context for mapping report issuers.

### 3.6 `data/extra_data/`

- Small auxiliary inputs and image assets.
- Includes:
  - `data/extra_data/youtube_idx.csv`
  - supporting JPEG assets under `general_image/` and `images/`

### 3.7 `data/raw/` and `data/processed/`

- Present but effectively empty in the inspected state.
- These look like reserved directories for a cleaner raw/processed separation, but the current workflow stores most real corpus data under `data/thesis_pdf/` and `data/thesis_dataset/`.

### 3.8 Data scale note

The `data/` tree contains tens of thousands of structured and semi-structured files because each OCR document expands into many page markdown and image files. The `pages/0_11_Source_Data_Catalog.py` page is the best interactive way to browse that inventory.

## 4. Results Layer

The `results/` directory is the operational evidence layer of the repository. It stores model runs, structured outputs, dashboard tables, visualizations, and reproducibility state.

### 4.1 Core structured result files

- `results/esg_records.json`
  - Main LLM extraction output store.
  - JSON list of run objects.
  - A run object typically contains:
    - `timestamp`
    - `model`
    - `target`
    - `target_pages`
    - `prompt`
    - `ok`
    - `records`
    - `error`
    - `error_type`
    - `raw_output`
    - `background_job_id`
  - When `ok` is true, `records` contains extracted ESG items with fields like:
    - `text`
    - `aspect`
    - `labels`
    - `esg`
    - `tone`
    - `sentiment`
    - `sentiment_score`
    - `reasoning`

- `results/ground_truth.json`
  - Ground-truth / validation oriented output list.
  - Contains timestamped model executions against manually supplied or curated text units.
  - Example payloads include `model`, `source`, `text`, and a nested `result`.

- `results/t1_results.json`, `results/t1_results.jsonl`
  - T1 result outputs, likely aligned with first-stage model classification.

- `results/t2_results.json`, `results/t2_results.jsonl`
  - T2 result outputs, likely aligned with second-stage ABSA / tone / aspect processing.

- `results/absa_results.json`
  - ABSA-oriented output bundle.

- `results/absa_results_ground_truth.json`
  - Ground-truth counterpart for ABSA outputs.

- `results/climatebert_results.json`
  - ClimateBERT prediction output store.

### 4.2 `results/revision_analysis/`

- Main curated analysis directory for thesis revision and synthesis work.
- This is the most reused secondary dataset across the standalone apps.

Representative files:

- `pilot_ground_truth_annotations.csv`
- `pilot_ground_truth_seed.csv`
- `silver_tone_ground_truth.csv`
- `climatebert_output.csv`
- `climatebert_record_batch_import.csv`
- `climatebert_proxy_agreement_summary.csv`
- `model_stability_summary.csv`
- `prompt_stability_summary.csv`
- `failure_modes.csv`
- `failure_mode_counts.csv`
- `ocr_processing_summary.csv`
- `ontology_coverage.csv`
- `ontology_coverage_full.csv`
- `ontology.json`
- `llm_statement_page_verifier_compiled.csv`
- `greenwashing_index_by_company.csv`

Role:

- thesis dashboard inputs
- research-track grounding datasets
- reviewer-response evidence
- export layer for tables that are already compact enough to analyze directly

### 4.3 `results/thesis_workflow_dashboard/`

- Canonical output set for the thesis systematic workflow dashboard.
- Includes compact, report-ready tables and images.

Representative files:

- `dashboard_metrics.json`
  - Includes fields such as `workflow_rqs`, `tone_records`, `t2_rows`, `pilot_labels`, `ocr_docs`, `artifacts`, `llm_jobs`, and ClimateBERT agreement metrics.
- `artifact_inventory.csv`
- `workflow_rq_coverage.csv`
- `rq_report_sections.json`
- `tone_records_flat.csv`
- `t2_flat_outputs.csv`
- `prompt_stability_summary.csv`
- `model_stability_summary.csv`
- `ontology_coverage.csv`
- `climatebert_proxy_agreement_summary.csv`
- image outputs like `aspect_by_tone_heatmap.png`, `tone_distribution.png`, `climatebert_label_by_tone.png`

Role:

- stable dashboard-facing data contracts
- downstream source for research apps such as `summarization/app.py`
- thesis-ready compact evidence bundle

### 4.4 `results/visualizations/`

- Visualization-oriented export directory.
- Contains charts and flattened tables used by comparison dashboards.

Representative files:

- `tone_records_flat.csv`
- `aspect_tone_crosstab.csv`
- `tone_esg_crosstab.csv`
- `climatebert_remote_flat.csv`
- `climatebert_remote_top_labels.csv`
- `tone_climatebert_label_crosstab.csv`
- `tone_climatebert_label_crosstab_full.csv`
- model-specific A.4 exports and manifests
- `streamlit_outputs/` dashboard images and manifest files

### 4.5 `results/docx_graph_attachments/`

- Exported graph and chart images intended for DOCX and thesis chapter integration.
- Used by chapter pages and attachment galleries.

### 4.6 `results/semantic_exports/`

- Semantic / graph export products generated from ABSA and ontology data.

Includes:

- `esg_thesis_graph.ttl`
- `esg_thesis_ontology.owl`
- `neo4j_nodes.csv`
- `neo4j_relationships.csv`
- `neo4j_load.cypher`
- `esg_semantic_exports.zip`

### 4.7 `results/transfer_learning/`

- Derived training dataset and summary for the transfer-learning track.

Includes:

- `dataset.jsonl`
- `dataset_summary.json`

### 4.8 `results/fine_tuning/`

- Fine-tuning validation artifacts.
- Currently includes `test_climatebert_logic.csv`.

### 4.9 Background-job state

#### `results/background_llm_jobs/`

- Stores background execution state for long-running LLM processing jobs.
- Contains `157` job directories at the time of inspection.

Typical job folder contents:

- `config.json`
- `control.json`
- `events.jsonl`
- `status.json`
- `worker.log`
- `worker.err.log`

Role:

- resumability
- monitoring
- provenance of model / prompt / document combinations

#### `results/climatebert_background_jobs/`

- Stores background execution state for ClimateBERT multi-model and step-based jobs.
- Contains `80` job directories at the time of inspection.

Typical job folder contents:

- `config.json`
- `control.json`
- `events.jsonl`
- `status.json`
- `worker.out.log`
- `worker.err.log`
- `climatebert_output.csv`
- `climatebert_record_batch_import.csv`

### 4.10 Frozen and legacy result areas

- `results/ch4_6_frozen_analysis/`
  - frozen chapter-analysis bundle and graph set
- `results_old/`
  - older snapshots such as previous ESG record files and predictions

## 5. Main Streamlit Thesis App

### 5.1 App launcher

- `app.py`
  - Small hub page titled "Thesis Dashboard Hub".
  - Links to:
    - `pages/0_0_Streamlit_Page_Workflow.py`
    - `pages/3_0_Thesis_Action_Plan.py`
    - `pages/5_Thesis_Systematic_Workflow_dashboard.py`
    - utility pages such as `0_10`, `3_3`, and `1_14`

### 5.2 Main page inventory

There are `45` Python files directly under `pages/`, though not all are first-class narrative pages. The major page groups are:

#### Navigation and catalog pages

- `pages/0_0_Streamlit_Page_Workflow.py`
  - Main map of the page ecosystem and thesis flow.
- `pages/0_10_Live_Numbers_Lineage.py`
  - Live metrics plus lineage calculations.
- `pages/0_11_Source_Data_Catalog.py`
  - Interactive file inventory for `data/`.
- `pages/0_2_JSON_Ontology_Usage_Map.py`
  - Governance view for ontology JSON usage.
- `pages/0_3_OCR_Company_Metadata_Labeler.py`
  - Labeling page for report-level company metadata.
- `pages/0_4_Sustainable_Framework_API_Reader.py`
  - Reader for external framework API endpoints.
- `pages/0_5_Thesis_Systematic_Workflow.py`
  - Executable workflow narrative for the thesis.

#### OCR and input-processing pages

- `pages/Bulk_OCR.py`
  - Bulk OCR driver / controller.
- `pages/1_2_OCR_Quality_Workbench.py`
  - OCR quality and sampling dashboard.
- `pages/2_4_PDF_Page_Processing_Audit.py`
  - Page-level processing audit.

#### LLM processing pages

- `pages/llm_processing.py`
  - Interactive LLM processing pipeline page.
- `pages/2_0_LLM_Processing_Result_Visualizer.py`
  - Visualizer for LLM output bundles.
- `pages/2_1_LLM_Error_Parse_Audit.py`
  - Parse and schema-drift audit page.
- `pages/2_2_LLM_Statement_Page_Verifier.py`
  - Statement-to-page verification using OCR page text.
- `pages/2_3_LLM_Background_Run_Monitor.py`
  - Monitor for `results/background_llm_jobs/`.
- `pages/2_5_LLM_Model_Catalog_Visualizer.py`
  - Model workbook visualizer.

#### Ground-truth and annotation pages

- `pages/ground_truth.py`
  - Ground-truth oriented execution page.
- `pages/1_1_Ground_Truth_Workbench.py`
  - Human annotation workbench.
- `pages/1_3_Ground_Truth_Metrics.py`
  - Metrics and comparison page.
- `pages/1_8_Ground_Truth_Output_Visualizer.py`
  - Output visualizer for annotated results.
- `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`
  - Visualizer for pipeline-generated ground-truth artifacts.
- `pages/1_10_Ground_Truth_Run_Coverage.py`
  - Coverage tracker for ground-truth processing.
- `pages/1_11_Ground_Truth_Record_Audit.py`
  - Record-level audit page.
- `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`
  - Most detailed step-wise trace page.

#### ClimateBERT and tone comparison pages

- `pages/0_9_Tone_ClimateBERT_Visualization.py`
  - Tone vs ClimateBERT comparison dashboard.
- `pages/1_4_ClimateBERT_Record_Batch.py`
  - ClimateBERT record import / validation page.
- `pages/1_14_ClimateBERT_Multi_Model_Runner.py`
  - Starts and aggregates multi-model ClimateBERT jobs.

#### Ontology, flow, and semantic graph pages

- `pages/1_5_ESG_Flow_Sankey.py`
  - Flow chart across ESG / tone / aspect dimensions.
- `pages/1_6_Ontology_Path_Viewer.py`
  - Path explorer and unmapped-aspect analysis.
- `pages/1_13_Semantic_Graph_Exporter.py`
  - Exports graph formats such as Turtle, OWL, and Neo4j CSV.

#### Thesis planning and synthesis pages

- `pages/1_0_Revision_Analytics.py`
  - Revision-oriented evidence dashboard.
- `pages/1_7_Research_Questions_Dashboard.py`
  - RQ-to-evidence mapping page.
- `pages/1_15_Thesis_Gap_Closure_Dashboard.py`
  - Gap-closing and evidence-strength dashboard.
- `pages/3_0_Thesis_Action_Plan.py`
  - Operational command center for thesis progress.
- `pages/5_Thesis_Systematic_Workflow_dashboard.py`
  - Manually curated workflow dashboard.
- `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`
  - Generated workflow dashboard.

#### A.4 per-model support pages

- `pages/3_1_A4_Per_Model_Background_Run.py`
  - Starts a background script for full A.4 crosstab generation.
- `pages/3_2_A4_Per_Model_Dashboard.py`
  - Visualizes model-specific A.4 outputs.
- `pages/3_3_A4_Regenerate_Fix_Grouping.py`
  - Regenerates tone-by-ClimateBERT crosstabs with normalization fixes.

#### Thesis chapter integration pages

- `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`
  - System-level thesis integration map.
- `pages/6_1_Chapter_4_Implementation_Results.py`
  - Interactive Chapter 4 evidence page.
- `pages/6_2_Chapter_5_Discussion.py`
  - Interactive Chapter 5 discussion page.
- `pages/6_3_Chapter_6_Conclusion.py`
  - Interactive Chapter 6 conclusion page.
- `pages/6_4_ch4-6.py`
  - Appendix-style page for graph attachments and benchmarks.

### 5.3 Page-adjacent assets

The `pages/` directory also includes support assets:

- `pages/models_cache.json`
  - cached model catalog data
- `pages/output/`
  - markdown outputs generated by page workflows
- `pages/thesis_draft/`
  - bibliography, CSV, and DOCX draft assets
- HTML, PNG, DOCX, and PDF files used for visualization or thesis support

### 5.4 Embedded helper apps under `pages/`

- `pages/annotator/app.py`
  - CSV annotation workspace for revision-analysis tables.
  - Supports in-place editing with backup creation.

- `pages/researcher/app.py`
  - Research explorer for tables and PDF inventory.
  - Useful for browsing result tables and source PDFs without touching code.

- `pages/backend/app.py`
  - Backend monitor for background jobs, logs, and core artifact sizes.

## 6. Standalone Apps and Research Tracks

These directories are not just notes. Most of them contain runnable Streamlit applications or executable experiment flows.

### 6.1 `api/`

- `api/documentation_api.py`
  - Lightweight HTTP server for project markdown documentation.
  - Indexes:
    - root `documentation*.md`
    - `research_documentation.md`
    - `docs/*.md`
    - `documentation/**/*.md`
  - Exposes endpoints:
    - `GET /health`
    - `GET /docs`
    - `GET /docs/{doc_id}`
    - `GET /docs/{doc_id}/raw`
    - `GET /docs/content?path=...`

- `api/climatebert_client.py`
  - Wrapper client for ClimateBERT-style remote prediction calls.

- `api/README.md`
  - Run instructions and endpoint summary.

### 6.2 `chatbot/`

- `chatbot/app.py`
  - Streamlit app that turns `documentation_chatbot.md` into a grounded research plan.
  - Reads compact evidence from `results/revision_analysis/`.

- `chatbot/README.md`
  - Documents run command and grounding datasets.

Purpose:

- feasibility study for a chatbot layer over ESG ABSA evidence
- research-plan presentation rather than production inference system

### 6.3 `fact_checking/`

- `fact_checking/app.py`
  - Streamlit app for multimodal fact-checking research planning.
  - Grounds its narrative with revision-analysis datasets and OCR processing summaries.

- `fact_checking/README.md`
  - Track description and output reference.

### 6.4 `fine_tuning/`

- `fine_tuning/app.py`
  - Streamlit research-plan app for fine-tuning feasibility.
- `fine_tuning/call_climatebert_logic.py`
  - Utility for calling / normalizing ClimateBERT-like logic.
- `fine_tuning/README.md`
  - Documents evidence sources and related outputs.

### 6.5 `llm_as_a_judge/`

- `llm_as_a_judge/app.py`
  - Streamlit explorer for:
    - `results/esg_records.json`
    - optional judge outputs under `results/llm_judge/`
  - Includes run flattening, categorical summaries, and optional charting.

- `llm_as_a_judge/research_plan.md`
  - Local track research plan.

### 6.6 `summarization/`

- `summarization/app.py`
  - Standalone summarization research dashboard.
  - Loads source locations from `summarization/data/data_sources.json`.
  - Contains simple lead, frequency-based, and TextRank-like summarization utilities plus ROUGE-style scoring.

- `summarization/data/`
  - sample datasets and a path-config file for real dashboard inputs

Purpose:

- evaluate whether existing thesis outputs can support summarization tasks
- provide lightweight algorithmic baselines without external model dependencies

### 6.7 `topic_modelling/`

- `topic_modelling/app.py`
  - Task-framework dashboard plus dataset-wide corpus scan over `data/thesis_dataset/`.
  - Uses keyword heuristics to estimate ESG pillar signals and other corpus properties.

- `topic_modelling/task_data.py`
  - Task and phase definitions for the track.

- `topic_modelling/ui.py`
  - Shared task-rendering helpers.

Purpose:

- topic-modelling feasibility and framework adaptation from another domain into ESG reports

### 6.8 `social_network_analysis/`

- `social_network_analysis/app.py`
  - Builds co-entity / co-aspect networks from OCR corpus sections.
  - Uses `networkx` and simple text heuristics to generate graph-level summaries.

- `social_network_analysis/task_data.py`, `ui.py`
  - Track-specific task and rendering helpers.

Purpose:

- adapt graph/network analysis ideas to ESG report corpora

### 6.9 `transfer_learning/`

This directory is the most end-to-end ML package in the repository.

Key files:

- `transfer_learning/schemas.py`
  - Label normalization and example schema definitions.
- `transfer_learning/data_builder.py`
  - Builds a training dataset from `results/esg_records.json`.
- `transfer_learning/modeling.py`
  - Multi-head transformer model definitions.
- `transfer_learning/train.py`
  - Training loop.
- `transfer_learning/evaluate.py`
  - Metrics and confusion-matrix export.
- `transfer_learning/streamlit_transfer_learning.py`
  - Viewer for metrics and errors.
- `transfer_learning/README.md`
  - Full quickstart in Indonesian.

Purpose:

- transform pseudo-labeled or human-labeled ESG ABSA outputs into a trainable supervised dataset

## 7. Shared Code in `code/`

The `code/` directory is the shared logic layer behind the thesis app.

### Core app and state helpers

- `code/app_state.py`
  - shared UI or state utilities
- `code/utils.py`
  - sentence parsing, language detection, plotting wrappers

### Pipeline and worker logic

- `code/llm_background_worker.py`
  - main background LLM worker
  - includes:
    - prompt application
    - JSON parsing from model output
    - provider-specific call logic
    - retry and context-recovery logic
    - job status updates

- `code/ground_truth_background_worker.py`
  - background support for ground-truth jobs

- `code/climatebert_background_worker.py`
  - background support for ClimateBERT jobs

### Analysis and export helpers

- `code/action_plan_status.py`
  - derives action-plan rows and stability summaries
- `code/graph_attachment_gallery.py`
  - assembles graph attachment cards and source tables
- `code/ground_truth_graphs.py`
  - graph-generation support for ground-truth artifacts
- `code/semantic_exporter.py`
  - produces Turtle, OWL, Neo4j CSV, zip exports
- `code/visualize_tone_climatebert.py`
  - creates charts and docs for tone-vs-ClimateBERT comparisons
- `code/data_alignment.py`
  - alignment and normalization helpers across artifact sets

### Modeling variants

- `code/rule_based.py`
  - rule-based baseline logic
- `code/classical_ml.py`
  - classical ML baseline logic
- `code/deep_model.py`
  - deep-learning baseline
- `code/deep_model_v2.py`
  - alternate deep-learning variant
- `code/hybrid_model.py`
  - hierarchical / hybrid model logic
- `code/explainability.py`
  - explainability utilities across models
- `code/lexicons.py`
  - lexical matching / term-list helpers

### Thesis rendering support

- `code/thesis_chapter_streamlit.py`
  - helper functions for chapter-oriented Streamlit pages

## 8. Scripts, Tools, and Templates

### 8.1 `scripts/`

- `scripts/start_run.py`
  - creates a new run folder
- `scripts/generate_manifest.py`
  - generates a run manifest
- `scripts/compare_runs.py`
  - compares two runs
- `scripts/publish_run.sh`
  - publishes run outputs
- `scripts/bootstrap_dvc.sh`
  - DVC bootstrap helper

These are referenced by `Makefile` and `ops/DATA_OPS.md`.

### 8.2 `tools/`

Artifact-generation and thesis-integration scripts.

- `tools/build_coherent_thesis_docx.py`
- `tools/generate_chapter_resolution_artifacts.py`
- `tools/regenerate_a4_chart.py`
- `tools/update_ch4_6_docx_graphs.py`
- `tools/climatebert_a4/generate_a4_per_model.py`

These tools bridge result tables and thesis-ready artifacts.

### 8.3 `templates/`

- Contains reusable page templates and documentation templates.
- Important for cloning dashboard patterns without rewriting large Streamlit blocks.

## 9. Documentation and Writing Assets

### Main documentation files

- `documentation.md`
  - page-focused documentation for the thesis Streamlit app
- `complete_documentation.md`
  - high-level project or thesis-status writeup
- `research_documentation.md`
  - research-focused umbrella documentation
- `code_documentation/high_level_pseudocode.md`
  - pseudocode view for `app.py` and `pages/*.py`

### Topic-track documentation

- `documentation_chatbot.md`
- `documentation_fact_checking.md`
- `documentation_fine_tuning.md`
- `documentation_graphrag.md`
- `documentation_social_network_analysis.md`
- `documentation_summarization.md`
- `documentation_topic_modelling.md`
- `documentation_transfer_learning.md`

These are feasibility / research-plan documents for each extension track.

### Documentation subdirectories

- `docs/`
  - secondary top-level docs such as `complete_research_documentation.md`
- `documentation/streamlit_pages/`
  - per-page markdown docs
- `documentation/section_reports/`
  - thesis section reports
- `documentation/p1_thesis_app/`
  - LaTeX assets for thesis writing

### Manuscript assets

- `thesis_paper_esg_absa.md`
- `thesis_paper_esg_absa_combined.md.docx`
- `thesis_paper_esg_absa_combined_coherent.docx`
- `thesis_draft_1.pdf`
- additional page-local thesis DOCX files under `pages/`

## 10. Operations and Reproducibility

- `ops/DATA_OPS.md`
  - explains run folders, manifests, publishing, and DVC-related workflow
- `outputs/`
  - intended run-output target directory
- `reports/`
  - reserved report directory
- `logs/`
  - runtime log store, especially for background workflows

The repository favors artifact preservation over aggressive cleanup. That is why many results remain stored alongside dashboards and thesis assets.

## 11. Legacy and Experimental Areas

- `hidden_pages/`
  - older or hidden prototypes not part of the main Streamlit navigation
- `pages_non_ocr/`
  - alternate or historical page set
- `past_pages/`
  - older page variants
- `results_old/`
  - older result snapshots

These should be treated as reference material unless a current page explicitly depends on them.

## 12. How To Navigate the Repo Efficiently

If you are new to this workspace, the fastest route is:

1. Read `app.py` and `documentation.md`.
2. Open `pages/0_0_Streamlit_Page_Workflow.py`.
3. Inspect `pages/3_0_Thesis_Action_Plan.py` and `pages/5_Thesis_Systematic_Workflow_dashboard.py`.
4. Treat `data/thesis_dataset/` as the main corpus and `results/revision_analysis/` as the main compact evidence layer.
5. Use `pages/0_11_Source_Data_Catalog.py`, `pages/researcher/app.py`, and `pages/backend/app.py` to inspect data and runs interactively.
6. Use the track folders only when you are working on a specific extension such as summarization, topic modelling, or transfer learning.

## 13. Quick Mapping by Need

- Need the main dashboard:
  - `app.py`
- Need the corpus:
  - `data/thesis_pdf/`, `data/thesis_dataset/`
- Need the main extracted records:
  - `results/esg_records.json`
- Need compact thesis evidence:
  - `results/revision_analysis/`, `results/thesis_workflow_dashboard/`
- Need background-job provenance:
  - `results/background_llm_jobs/`, `results/climatebert_background_jobs/`
- Need semantic exports:
  - `results/semantic_exports/`
- Need supervised ML experimentation:
  - `transfer_learning/`
- Need page-by-page docs:
  - `documentation/streamlit_pages/`
- Need file-by-file pseudocode:
  - `code_documentation/high_level_pseudocode.md`

## 14. Summary

This repository is best understood as a thesis operating system rather than a narrow application. The main assets are:

- a document corpus expanded into OCR page datasets
- a structured evidence layer built from LLM and ClimateBERT processing
- multiple dashboards for audit, validation, and chapter writing
- research-track sandboxes for future extensions

The most important directories operationally are:

- `pages/`
- `code/`
- `data/thesis_dataset/`
- `results/revision_analysis/`
- `results/thesis_workflow_dashboard/`
- `results/background_llm_jobs/`

The most important documents for orientation are:

- `documentation.md`
- `code_documentation/high_level_pseudocode.md`
- `documentation_data_inventory.md`
- `documentation_apps_inventory.md`
- `documentation_pages_inventory.md`
- this file, `code_documentation.md`
