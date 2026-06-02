# Complete Documentation Master

This file is the polished master reference for the repository at `/home/ubuntu/apps/benchmarks/new_page`.

It consolidates the documentation effort across:

- [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md)
- [documentation_data_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_data_inventory.md)
- [documentation_apps_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_apps_inventory.md)
- [documentation_pages_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_pages_inventory.md)
- [documentation_code_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_code_inventory.md)
- [documentation_results_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_results_inventory.md)
- [documentation.md](/home/ubuntu/apps/benchmarks/new_page/documentation.md)

## Quick Navigation

Use this file when you want the single polished overview.

Use the focused inventories when you need depth:

- [documentation_data_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_data_inventory.md) for `data/`
- [documentation_apps_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_apps_inventory.md) for runnable apps
- [documentation_pages_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_pages_inventory.md) for the `pages/` surface
- [documentation_code_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_code_inventory.md) for the `code/` modules
- [documentation_results_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_results_inventory.md) for `results/` artifacts and schemas

## 1. What This Repository Is

This repository is an executable thesis workspace for Indonesian ESG sustainability-report analysis.

It is not just:

- a dashboard
- a model benchmark
- a data folder
- or a manuscript archive

It is all of those at once.

The core workflow is:

1. collect report PDFs
2. OCR them into page-level text and image artifacts
3. run LLM extraction and ABSA-oriented processing
4. compare or validate with ClimateBERT-style models
5. build human-annotation and ground-truth evidence
6. generate charts, tables, semantic exports, and chapter-ready artifacts
7. translate those outputs into interactive thesis chapter pages

## 2. The Repository at a Glance

### Main launch point

- `app.py`
  - main Streamlit hub for the thesis dashboard

### Most important directories

- `pages/`
  - main multi-page Streamlit thesis app
- `code/`
  - shared implementation logic
- `data/`
  - source corpora and auxiliary input datasets
- `results/`
  - extracted outputs, analysis tables, visualizations, and job state
- `api/`
  - documentation API and ClimateBERT client
- research-track apps:
  - `chatbot/`
  - `fact_checking/`
  - `fine_tuning/`
  - `llm_as_a_judge/`
  - `summarization/`
  - `topic_modelling/`
  - `social_network_analysis/`
  - `transfer_learning/`
- documentation and manuscript assets:
  - `documentation/`
  - `docs/`
  - `code_documentation/`

## 3. Source Data Layer

### Raw report corpus

- `data/thesis_pdf/`
  - raw PDF corpus
  - `193` PDFs in the inspected state

### OCR-expanded corpus

- `data/thesis_dataset/`
  - OCR-expanded corpus
  - `189` document folders in the inspected state
  - each folder typically contains:
    - `ocr_result.json`
    - `pages/*.md`
    - `images/*.jpeg`

### Structured lookup and metadata inputs

- `data/idx_data.csv`
- `data/ESG Score.xlsx`
- `data/stock_info/*/rendered.html`
- `data/extra_data/`

### Important note

Even though `data/raw/` and `data/processed/` exist, the current operational corpus lives mainly in:

- `data/thesis_pdf/`
- `data/thesis_dataset/`

## 4. Results and Evidence Layer

### Primary result stores

- `results/esg_records.json`
  - main T3 LLM extraction record store
- `results/t1_results.jsonl`
  - T1 result rows
- `results/t2_results.jsonl`
  - T2 result rows
- `results/ground_truth.json`
  - ground-truth execution record store
- `results/climatebert_results.json`
  - ClimateBERT output store

### Most important compact analysis areas

- `results/revision_analysis/`
  - curated compact analysis tables
- `results/thesis_workflow_dashboard/`
  - dashboard contract layer
- `results/visualizations/`
  - comparison tables and rendered charts

### Export-oriented areas

- `results/docx_graph_attachments/`
- `results/semantic_exports/`
- `results/transfer_learning/`

### Reproducibility and provenance areas

- `results/background_llm_jobs/`
- `results/climatebert_background_jobs/`

These hold per-job `config.json`, `status.json`, `events.jsonl`, logs, and sometimes direct output tables.

## 5. Main Application Surface

### The thesis dashboard

Launch:

- `streamlit run app.py`

Key pages:

- `pages/0_0_Streamlit_Page_Workflow.py`
- `pages/3_0_Thesis_Action_Plan.py`
- `pages/5_Thesis_Systematic_Workflow_dashboard.py`
- `pages/llm_processing.py`
- `pages/ground_truth.py`
- `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`

### What the pages do

The `pages/` directory includes:

- navigation and catalog pages
- OCR and PDF audit pages
- LLM extraction pages
- ground-truth and validation pages
- ClimateBERT comparison pages
- ontology and semantic export pages
- thesis revision and gap-closure dashboards
- chapter-writing and chapter-integration pages
- helper apps for annotation, research browsing, and backend monitoring

## 6. Standalone Apps and Research Tracks

Outside the main thesis app, the repository includes several focused apps:

- `chatbot/app.py`
  - chatbot research planner
- `fact_checking/app.py`
  - multimodal fact-checking research planner
- `fine_tuning/app.py`
  - fine-tuning research planner plus API validation
- `llm_as_a_judge/app.py`
  - dataset explorer and judge research-plan app
- `summarization/app.py`
  - ESG summarization workspace
- `topic_modelling/app.py`
  - task framework plus corpus scan
- `social_network_analysis/app.py`
  - graph/network analysis workspace
- `transfer_learning/streamlit_transfer_learning.py`
  - training/evaluation result viewer

## 7. Shared Implementation Layer

The `code/` directory is the functional backbone of the repository.

### Most important groups

#### Worker modules

- `code/llm_background_worker.py`
- `code/ground_truth_background_worker.py`
- `code/climatebert_background_worker.py`

#### Evidence and chart modules

- `code/action_plan_status.py`
- `code/graph_attachment_gallery.py`
- `code/ground_truth_graphs.py`
- `code/visualize_tone_climatebert.py`

#### Export and chapter integration modules

- `code/semantic_exporter.py`
- `code/thesis_chapter_streamlit.py`

#### Modeling and baseline modules

- `code/rule_based.py`
- `code/classical_ml.py`
- `code/deep_model.py`
- `code/deep_model_v2.py`
- `code/hybrid_model.py`
- `code/explainability.py`

#### Utility modules

- `code/utils.py`
- `code/lexicons.py`
- `code/data_alignment.py`
- `code/app_state.py`

## 8. How Data Moves Through the System

### Stage 1: source documents

- PDFs live in `data/thesis_pdf/`

### Stage 2: OCR expansion

- OCR outputs live in `data/thesis_dataset/`
- page markdown and image assets become addressable

### Stage 3: LLM and model extraction

- T3 runs populate `results/esg_records.json`
- T1 and T2 processing populate `results/t1_results*.jsonl` and `results/t2_results*.jsonl`
- ClimateBERT jobs populate background-job folders and merged CSV outputs

### Stage 4: compact analysis and dashboards

- data is normalized into `results/revision_analysis/`
- dashboard-facing subsets are written to `results/thesis_workflow_dashboard/`
- charts land in `results/visualizations/` and `results/docx_graph_attachments/`

### Stage 5: export and writing

- semantic artifacts land in `results/semantic_exports/`
- thesis pages render current outputs
- chapter-ready explanations and images become available in Streamlit and markdown outputs

## 9. Most Important Files by Practical Need

### If you need the source corpus

- `data/thesis_pdf/`
- `data/thesis_dataset/`

### If you need the main extracted records

- `results/esg_records.json`

### If you need compact analysis tables

- `results/revision_analysis/`

### If you need stable dashboard inputs

- `results/thesis_workflow_dashboard/`

### If you need comparison charts

- `results/visualizations/`
- `results/docx_graph_attachments/`

### If you need background-job provenance

- `results/background_llm_jobs/`
- `results/climatebert_background_jobs/`

### If you need semantic graph export

- `results/semantic_exports/`

### If you need transfer-learning artifacts

- `results/transfer_learning/`

## 10. Best Entry Points for Different Roles

### For a thesis reader or reviewer

Start with:

1. `documentation.md`
2. `pages/0_0_Streamlit_Page_Workflow.py`
3. `pages/1_7_Research_Questions_Dashboard.py`
4. `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`

### For a developer debugging extraction

Start with:

1. `pages/llm_processing.py`
2. `pages/2_3_LLM_Background_Run_Monitor.py`
3. `code/llm_background_worker.py`
4. `results/esg_records.json`

### For someone validating tone or ClimateBERT

Start with:

1. `pages/0_9_Tone_ClimateBERT_Visualization.py`
2. `pages/1_4_ClimateBERT_Record_Batch.py`
3. `pages/1_14_ClimateBERT_Multi_Model_Runner.py`
4. `results/revision_analysis/climatebert_*`

### For someone working on human validation

Start with:

1. `pages/1_1_Ground_Truth_Workbench.py`
2. `pages/1_3_Ground_Truth_Metrics.py`
3. `pages/annotator/app.py`
4. `results/revision_analysis/pilot_ground_truth_annotations.csv`

### For someone packaging thesis chapters

Start with:

1. `pages/6_1_Chapter_4_Implementation_Results.py`
2. `pages/6_2_Chapter_5_Discussion.py`
3. `pages/6_3_Chapter_6_Conclusion.py`
4. `code/thesis_chapter_streamlit.py`
5. `code/graph_attachment_gallery.py`

## 11. Supporting Operations and Tooling

- `Makefile`
  - top-level run orchestration
- `scripts/`
  - run creation, manifest generation, run comparison, publishing
- `ops/DATA_OPS.md`
  - reproducibility workflow
- `tools/`
  - chart regeneration and DOCX/thesis artifact builders
- `templates/`
  - page and documentation templates

## 12. Documentation Map

Use these documents depending on the level of detail you need:

- [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md)
  - repo-wide overview
- [documentation_data_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_data_inventory.md)
  - data-layer detail
- [documentation_apps_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_apps_inventory.md)
  - runnable app surfaces
- [documentation_pages_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_pages_inventory.md)
  - `pages/` inventory
- [documentation_code_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_code_inventory.md)
  - `code/` module inventory
- [documentation_results_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_results_inventory.md)
  - `results/` subfolders and schemas
- [documentation.md](/home/ubuntu/apps/benchmarks/new_page/documentation.md)
  - existing main Streamlit page narrative

## 13. Final Summary

This repository is best understood as a thesis operating system.

Its critical layers are:

- a raw PDF corpus
- an OCR-expanded corpus
- a structured extraction and validation layer
- a compact analysis layer for dashboards and thesis evidence
- an export layer for charts, semantic artifacts, and chapters
- a documentation layer that explains how all of those pieces connect

If you only remember a few paths, remember these:

- `app.py`
- `pages/`
- `code/`
- `data/thesis_dataset/`
- `results/revision_analysis/`
- `results/thesis_workflow_dashboard/`
- `results/background_llm_jobs/`
- `results/climatebert_background_jobs/`
