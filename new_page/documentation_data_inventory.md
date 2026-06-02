# Data Inventory Documentation

This document describes the data assets under `data/` and the result-facing datasets that the applications use most often.

For the repository-wide overview, see [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md).

## 1. Scope

This file focuses on:

- source datasets under `data/`
- OCR corpus layout
- spreadsheet and HTML snapshot inputs
- the compact result datasets most apps actually read

It does not try to replace the page-level documentation in `documentation.md`.

## 2. `data/` Overview

Top-level directories:

- `data/copilot_notes/`
- `data/extra_data/`
- `data/processed/`
- `data/raw/`
- `data/stock_info/`
- `data/thesis_dataset/`
- `data/thesis_pdf/`

Top-level files:

- `data/ESG Score.xlsx`
- `data/idx_data.csv`

## 3. Primary Source Corpus

### 3.1 `data/thesis_pdf/`

This is the raw report corpus.

- Contains PDF source documents for annual reports, sustainability reports, and integrated reports.
- The inspected state contains `193` PDFs.
- Filenames encode company identity and year, often with OCR-safe suffix variations.

Typical use:

- input to OCR
- reference source for inventory pages
- canonical raw artifact when tracing a result back to the original document

### 3.2 `data/thesis_dataset/`

This is the OCR-expanded version of the thesis corpus.

- The inspected state contains `189` document folders.
- Each folder corresponds to one OCR-processed report.

Typical folder pattern:

- `<document_name>_pdf/ocr_result.json`
- `<document_name>_pdf/pages/page_0000.md`
- `<document_name>_pdf/pages/page_0001.md`
- `<document_name>_pdf/images/img-0.jpeg`

Typical structure:

- `ocr_result.json`
  - primary OCR payload
  - includes a `pages` array
  - each page may include:
    - `index`
    - `markdown`
    - `images`
    - `tables`
    - `hyperlinks`
    - `header`
    - `footer`
    - `dimensions`
    - `confidence_scores`
- `pages/`
  - page-level markdown artifacts used by:
    - `pages/2_2_LLM_Statement_Page_Verifier.py`
    - `pages/2_4_PDF_Page_Processing_Audit.py`
    - OCR inspection flows
    - batching logic
- `images/`
  - extracted page image snippets referenced from OCR JSON

This folder is the operational corpus for most of the thesis app.

## 4. Supporting Source Tables

### 4.1 `data/idx_data.csv`

- A structured IDX-related source table.
- Used by inventory and metadata pages.
- Likely contains issuer-level and download-link-oriented fields.

### 4.2 `data/ESG Score.xlsx`

- Spreadsheet-based ESG reference dataset.
- Available through the researcher explorer.
- Used as a lookup or comparison table rather than as a pipeline-native output.

## 5. External Snapshot Data

### 5.1 `data/stock_info/`

This directory contains HTML snapshots grouped by sector.

Examples:

- `data/stock_info/carisaham.com_emiten_sektor_energi/rendered.html`
- `data/stock_info/carisaham.com_emiten_sektor_keuangan/rendered.html`
- `data/stock_info/carisaham.com_emiten_sektor_teknologi/rendered.html`

Purpose:

- sector metadata enrichment
- issuer classification support
- preserved external context without depending on live scraping

### 5.2 `data/extra_data/`

Small auxiliary data area.

Includes:

- `data/extra_data/youtube_idx.csv`
- image assets in:
  - `data/extra_data/general_image/`
  - `data/extra_data/images/`

## 6. Reserved Raw/Processed Areas

### 6.1 `data/raw/`

- Present but effectively empty in the inspected state.
- Appears reserved for cleaner ingestion-stage storage.

### 6.2 `data/processed/`

- Present but effectively empty in the inspected state.
- Appears reserved for explicitly transformed inputs, but current practice stores most usable artifacts in `data/thesis_dataset/`.

## 7. Result Datasets Commonly Read by Apps

Although these live under `results/`, many apps treat them as stable data inputs.

### 7.1 `results/revision_analysis/`

This is the most important compact evidence directory.

High-value files:

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
- `chapter4_tone_denominator_audit.csv`
- `chapter6_benchmark_gap_positioning.csv`

Apps that read from here include:

- `chatbot/app.py`
- `fact_checking/app.py`
- `fine_tuning/app.py`
- `pages/annotator/app.py`
- `pages/0_10_Live_Numbers_Lineage.py`
- `pages/1_0_Revision_Analytics.py`
- `pages/1_15_Thesis_Gap_Closure_Dashboard.py`

### 7.2 `results/thesis_workflow_dashboard/`

Compact dashboard-facing data contract layer.

Important files:

- `dashboard_metrics.json`
- `artifact_inventory.csv`
- `workflow_rq_coverage.csv`
- `rq_report_sections.json`
- `tone_records_flat.csv`
- `t2_flat_outputs.csv`
- `prompt_stability_summary.csv`
- `model_stability_summary.csv`
- `ontology_coverage.csv`
- `climatebert_proxy_agreement_summary.csv`

Also includes thesis-ready PNG exports.

Used heavily by:

- `pages/5_Thesis_Systematic_Workflow_dashboard.py`
- `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`
- `summarization/app.py`

### 7.3 `results/visualizations/`

Flattened comparison tables and rendered charts.

Important files:

- `tone_records_flat.csv`
- `aspect_tone_crosstab.csv`
- `tone_esg_crosstab.csv`
- `climatebert_remote_flat.csv`
- `climatebert_remote_top_labels.csv`
- `tone_climatebert_label_crosstab.csv`
- `tone_climatebert_label_crosstab_full.csv`

Used by comparison and A.4 pages.

## 8. Background Job Datasets

### 8.1 `results/background_llm_jobs/`

Each job folder is a mini dataset containing execution state.

Typical contents:

- `config.json`
- `control.json`
- `events.jsonl`
- `status.json`
- `worker.log`
- `worker.err.log`

### 8.2 `results/climatebert_background_jobs/`

Each job folder includes both execution state and output tables.

Typical contents:

- `config.json`
- `control.json`
- `events.jsonl`
- `status.json`
- `worker.out.log`
- `worker.err.log`
- `climatebert_output.csv`
- `climatebert_record_batch_import.csv`

## 9. Best Interactive Entry Points

If you want to inspect data without reading code, use:

- `pages/0_11_Source_Data_Catalog.py`
- `pages/researcher/app.py`
- `pages/backend/app.py`
- `pages/2_2_LLM_Statement_Page_Verifier.py`

## 10. Summary

The most important data assets in this repository are:

- `data/thesis_pdf/` as the raw corpus
- `data/thesis_dataset/` as the OCR-expanded corpus
- `results/revision_analysis/` as the compact analysis layer
- `results/thesis_workflow_dashboard/` as the dashboard contract layer
- `results/background_llm_jobs/` and `results/climatebert_background_jobs/` as execution-state datasets
