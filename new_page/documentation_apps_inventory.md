# Apps Inventory Documentation

This document lists the runnable app surfaces in the repository outside the core explanation-only markdown assets.

For the repository-wide overview, see [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md).

## 1. Main Thesis App

### `app.py`

- Type: Streamlit launcher / hub
- Title: `Thesis Dashboard Hub`
- Purpose:
  - launch point for the main thesis multi-page dashboard
  - links into the key `pages/` modules

This is the primary entrypoint when you want Streamlit to discover the full thesis page set.

## 2. Embedded Helper Apps Under `pages/`

### `pages/annotator/app.py`

- Type: Streamlit app
- Title: `Annotation Workspace`
- Purpose:
  - edit revision-analysis CSV datasets directly
  - filter rows by text, company, model, tone, and review status
  - save edits back to CSV with timestamped backups

Primary inputs:

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/pilot_ground_truth_seed.csv`
- other CSVs discovered in `results/revision_analysis/`

### `pages/researcher/app.py`

- Type: Streamlit app
- Title: `Research Explorer`
- Purpose:
  - browse key result tables and spreadsheet inputs
  - inspect PDF inventory in `data/thesis_pdf/`
  - summarize columns and filter table data

Primary inputs:

- `results/visualizations/tone_records_flat.csv`
- `results/thesis_workflow_dashboard/artifact_inventory.csv`
- `results/thesis_workflow_dashboard/dashboard_metrics.json`
- `results/esg_records.json`
- `results/revision_analysis/*.csv`
- `data/ESG Score.xlsx`
- `data/thesis_pdf/*.pdf`

### `pages/backend/app.py`

- Type: Streamlit app
- Title: `Backend Monitor`
- Purpose:
  - inspect background job folders
  - read log files
  - summarize core artifact sizes

Primary inputs:

- `results/background_llm_jobs/`
- `logs/`
- selected files in `results/`

## 3. Lightweight API Surfaces

### `api/documentation_api.py`

- Type: HTTP server
- Purpose:
  - expose repository documentation files through simple endpoints

Endpoints documented in `api/README.md`:

- `GET /health`
- `GET /docs`
- `GET /docs/{doc_id}`
- `GET /docs/{doc_id}/raw`
- `GET /docs/content?path=...`

### `api/climatebert_client.py`

- Type: API client helper
- Purpose:
  - call remote ClimateBERT-style inference endpoints

This is not a server by itself, but it is an integration surface used by app code.

## 4. Research-Track Streamlit Apps

### `chatbot/app.py`

- Title: `Chatbot Research Planner`
- Purpose:
  - convert `documentation_chatbot.md` into a grounded research-plan dashboard

Grounding data:

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
- `results/revision_analysis/failure_modes.csv`
- `results/revision_analysis/prompt_stability_summary.csv`
- `results/revision_analysis/model_stability_summary.csv`
- `results/revision_analysis/ontology_coverage.csv`

### `fact_checking/app.py`

- Title: `Fact-Checking Research Planner`
- Purpose:
  - present a multimodal fact-checking research plan grounded in current evidence

Grounding data:

- revision-analysis tables
- OCR processing summaries

### `fine_tuning/app.py`

- Title: `Fine-Tuning Research Planner`
- Purpose:
  - present a fine-tuning research plan
  - validate climatebert-logic API behavior against sample rows

Grounding data:

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/silver_tone_ground_truth.csv`
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
- `results/revision_analysis/climatebert_output.csv`
- `results/revision_analysis/model_stability_summary.csv`
- `results/revision_analysis/prompt_stability_summary.csv`

### `llm_as_a_judge/app.py`

- Title: `LLM-as-a-Judge (Dataset Explorer + Research Plan)`
- Purpose:
  - explore `results/esg_records.json`
  - optionally inspect judge outputs
  - summarize extraction records and judge summaries

Primary inputs:

- `results/esg_records.json`
- optional `results/llm_judge/judge_records.jsonl`
- optional `results/llm_judge/judge_summary.csv`

### `summarization/app.py`

- Title: `ESG ABSA Summarization Workspace`
- Purpose:
  - summarization workspace over compact ESG evidence tables
  - includes simple extractive baselines and ROUGE-style evaluation

Primary config:

- `summarization/data/data_sources.json`

Typical resolved datasets:

- `results/thesis_workflow_dashboard/tone_records_flat.csv`
- `results/thesis_workflow_dashboard/t2_flat_outputs.csv`
- `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv`
- `results/thesis_workflow_dashboard/model_stability_summary.csv`
- `results/thesis_workflow_dashboard/prompt_stability_summary.csv`
- `results/thesis_workflow_dashboard/ontology_coverage.csv`

### `topic_modelling/app.py`

- Title: `ESG Sustainability Report Analysis - Complete Task Framework`
- Purpose:
  - task-framework dashboard
  - dataset-wide OCR corpus scan using lightweight heuristics

Primary corpus:

- `data/thesis_dataset/`

### `social_network_analysis/app.py`

- Title: `ESG Report Network Analysis - Adapted Framework`
- Purpose:
  - build co-entity / co-aspect graph summaries from OCR text sections

Primary corpus:

- `data/thesis_dataset/`

### `transfer_learning/streamlit_transfer_learning.py`

- Title: `Transfer Learning — ESG ABSA (Bahasa Indonesia)`
- Purpose:
  - view training and evaluation outputs from the transfer-learning pipeline

Primary inputs:

- `results/transfer_learning/`

## 5. Experiment Pipelines That Are Not Primarily UI Apps

### `transfer_learning/data_builder.py`

- Type: CLI-style data preparation script
- Purpose:
  - build training rows from `results/esg_records.json`

### `transfer_learning/train.py`

- Type: training script
- Purpose:
  - train multi-head transformer model for ESG ABSA tasks

### `transfer_learning/evaluate.py`

- Type: evaluation script
- Purpose:
  - compute metrics and confusion matrices

### `fine_tuning/call_climatebert_logic.py`

- Type: API exercise / helper script
- Purpose:
  - call and normalize ClimateBERT-style classification responses

## 6. Best Entry Points by Task

- Want the main thesis workspace:
  - `app.py`
- Want to edit annotations:
  - `pages/annotator/app.py`
- Want to inspect tables and PDFs:
  - `pages/researcher/app.py`
- Want to monitor jobs:
  - `pages/backend/app.py`
- Want research-plan dashboards:
  - `chatbot/app.py`
  - `fact_checking/app.py`
  - `fine_tuning/app.py`
- Want experimental analysis tracks:
  - `summarization/app.py`
  - `topic_modelling/app.py`
  - `social_network_analysis/app.py`
- Want supervised ML experimentation:
  - `transfer_learning/data_builder.py`
  - `transfer_learning/train.py`
  - `transfer_learning/evaluate.py`
  - `transfer_learning/streamlit_transfer_learning.py`
