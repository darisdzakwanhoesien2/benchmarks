# Results Artifact Inventory Documentation

This document describes the `results/` directory by subfolder and by common schema.

For the repository-wide overview, see [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md). For data-layer discussion, see [documentation_data_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_data_inventory.md).

## 1. Purpose of `results/`

`results/` is the evidence layer of the repository. It stores:

- raw and semi-structured model outputs
- compact CSV and JSON datasets used by dashboards
- background-job state
- exported charts
- semantic graph products
- training-ready derived datasets

## 2. Root-Level Result Files

### `results/esg_records.json`

- Primary T3-style LLM extraction store.
- Schema pattern:
  - list of run objects
  - each run usually has:
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
- Successful `records` entries typically contain:
  - `text`
  - `aspect`
  - `labels`
  - `esg`
  - `tone`
  - `sentiment`
  - `sentiment_score`
  - `reasoning`

### `results/ground_truth.json`

- Ground-truth / validation run list.
- Schema pattern:
  - list of items with:
    - `timestamp`
    - `model`
    - `source`
    - `text`
    - `result`

### `results/t1_results.json`, `results/t1_results.jsonl`

- T1 results stored as JSON and JSONL.
- JSONL rows typically include:
  - `timestamp`
  - `label`
  - `model`
  - `text`
  - `result`

### `results/t2_results.json`, `results/t2_results.jsonl`

- T2 outputs stored as JSON and JSONL.
- JSONL rows typically include:
  - `timestamp`
  - `label`
  - `text`
  - `rule_based`
  - `hybrid`

The `hybrid` block commonly includes:

- `predictions`
  - rows with sentence IDs, tone/sentiment predictions, ontology alignment, and ontology path
- `metrics`
  - rows such as:
    - `Ontology Consistency`
    - `Greenwashing Index`
    - `N Sentences`
    - `Sections`

### Other root files

- `results/absa_results.json`
- `results/absa_results_ground_truth.json`
- `results/climatebert_results.json`
- `results/predictions.json`
- `results/example.json`
- `results/example copy.json`

These appear to be legacy, intermediate, or alternate-export result bundles.

## 3. `results/revision_analysis/`

This is the most important compact analysis subfolder.

### Main artifact classes

- human-annotation datasets
- ClimateBERT comparison datasets
- stability summaries
- ontology review tables
- failure-mode diagnostics
- thesis-resolution planning tables

### High-value files and likely schemas

- `pilot_ground_truth_annotations.csv`
  - manual annotation table
  - often includes fields like:
    - `record_id`
    - `ground_truth_tone`
    - `ground_truth_esg`
    - `ground_truth_aspect`
    - `annotator`
    - `review_status`
    - `review_notes`

- `pilot_ground_truth_seed.csv`
  - seed annotation scaffold

- `silver_tone_ground_truth.csv`
  - silver-label reference dataset

- `climatebert_output.csv`
  - raw or merged ClimateBERT output rows

- `climatebert_record_batch_import.csv`
  - import-ready comparison dataset for ClimateBERT record batch pages

- `climatebert_proxy_agreement_summary.csv`
  - compact agreement summary dataset

- `climatebert_proxy_agreement_records.csv`
  - record-level agreement rows

- `model_stability_summary.csv`
  - one row per model with run counts and parse-success or missing-field rates

- `prompt_stability_summary.csv`
  - one row per prompt with stability / field-completion metrics

- `prompt_stability_by_run.csv`
  - finer-grained repeated-run dataset

- `failure_modes.csv`
  - detailed failure categorization rows

- `failure_mode_counts.csv`
  - compact counts per failure mode

- `ocr_processing_summary.csv`
  - OCR workflow summary table

- `ontology_coverage.csv`
  - aspect coverage and mapped/unmapped ontology paths

- `ontology_coverage_full.csv`
  - expanded ontology coverage table

- `ontology.json`
  - ontology structure artifact used by exporters and viewers

- `llm_statement_page_verifier_compiled.csv`
  - compiled best-match evidence between extracted statements and OCR pages

- `greenwashing_index_by_company.csv`
  - company-level greenwashing metrics

- `chapter_4_6_resolution_board.csv`
  - thesis resolution planning board

- `chapter_4_6_resolution_decisions.json`
  - structured decisions for resolution workflow

- `chapter6_top_unmapped_ontology_candidates.csv`
- `ontology_novel_aspect_review.csv`
- `ground_truth_t2_unmapped_mapping_candidates.csv`
- `ground_truth_t2_unmapped_topic_suggestions.csv`
  - ontology extension and aspect-review tables

## 4. `results/thesis_workflow_dashboard/`

This is the dashboard contract layer: compact, report-ready, and repeatedly reused.

### Main files

- `dashboard_metrics.json`
  - compact metric summary
  - observed keys include:
    - `workflow_rqs`
    - `tone_records`
    - `t2_rows`
    - `pilot_labels`
    - `ocr_docs`
    - `artifacts`
    - `llm_jobs`
    - `ground_truth_jobs`
    - `climatebert_percent_agreement`
    - `climatebert_cohen_kappa`

- `rq_report_sections.json`
  - list of RQ sections
  - each object typically includes:
    - `rq`
    - `title`
    - `graph`
    - `results`
    - `interpretation`
    - `baseline`
    - `discussion`
    - `conclusion`

- `artifact_inventory.csv`
  - catalog of output artifacts used by the workflow dashboard

- `workflow_rq_coverage.csv`
  - table linking artifacts or measures to RQ coverage

- `tone_records_flat.csv`
  - flattened extraction dataset used by many visualizations

- `t2_flat_outputs.csv`
  - flattened T2 output table

- `climatebert_proxy_agreement_summary.csv`
- `model_stability_summary.csv`
- `prompt_stability_summary.csv`
- `ontology_coverage.csv`
- `failure_mode_counts.csv`
- `ocr_processing_summary.csv`
- `greenwashing_index_by_company.csv`

- `thesis_dashboard_report.md`
  - markdown report version of the workflow dashboard

- `dashboard_image_manifest.json`
  - maps chart filenames from `results/visualizations/` into their saved dashboard copies

### Image outputs

- `tone_distribution.png`
- `esg_by_tone.png`
- `aspect_by_tone_heatmap.png`
- `climatebert_label_by_tone.png`
- `climatebert_remote_top_scores.png`

## 5. `results/visualizations/`

This subfolder contains visual and flattened comparison outputs.

### Core tables

- `tone_records_flat.csv`
- `aspect_tone_crosstab.csv`
- `tone_esg_crosstab.csv`
- `climatebert_remote_flat.csv`
- `climatebert_remote_top_labels.csv`
- `tone_climatebert_label_crosstab.csv`
- `tone_climatebert_label_crosstab_full.csv`
- `tone_climatebert_commitment_crosstab_full.csv`
- model-specific crosstab files with long descriptive filenames

### Core images

- `tone_distribution.png`
- `esg_by_tone.png`
- `aspect_by_tone_heatmap.png`
- `climatebert_label_by_tone.png`
- `climatebert_remote_top_scores.png`

### `results/visualizations/streamlit_outputs/`

Saved image outputs and catalogs from Streamlit dashboard snapshots.

Representative files:

- `01_overview.png`
- `02_per_rq_evidence.png`
- `03_sample_size.png`
- `04_benchmarks.png`
- `05_existing_results.png`
- `06_analysis_plan.png`
- `07_evidence_matrix.png`
- `dashboard_image_catalog.json`

`dashboard_image_catalog.json` schema typically includes:

- `generated_at`
- `root`
- `purpose`
- `image_count`
- `images`
  - each image object includes:
    - `id`
    - `title`
    - `path`
    - `source`
    - `type`
    - `explanation`
    - `thesis_use`
    - `relative_path`
    - `file_size_bytes`

## 6. `results/docx_graph_attachments/`

This folder stores graph and chart images intended for DOCX chapter integration.

It includes:

- ground-truth charts
- ontology coverage charts
- A.4 and repeated-run charts
- benchmark and chapter summary figures

These files are heavily referenced by:

- `code/graph_attachment_gallery.py`
- `pages/6_1_Chapter_4_Implementation_Results.py`
- `pages/6_2_Chapter_5_Discussion.py`
- `pages/6_3_Chapter_6_Conclusion.py`
- `pages/6_4_ch4-6.py`

## 7. `results/semantic_exports/`

Semantic and graph-oriented export products.

Files:

- `esg_thesis_graph.ttl`
- `esg_thesis_ontology.owl`
- `neo4j_nodes.csv`
- `neo4j_relationships.csv`
- `neo4j_load.cypher`
- `esg_semantic_exports.zip`

These are produced by `code/semantic_exporter.py`.

## 8. `results/transfer_learning/`

Derived supervised-learning dataset outputs.

Files:

- `dataset.jsonl`
  - training-ready JSONL examples
- `dataset_summary.json`
  - summary statistics such as:
    - `n`
    - `unique_aspects`
    - `top_aspects`
    - `sentiments`
    - `tones`
    - `esg`

## 9. `results/fine_tuning/`

Fine-tuning track outputs.

Files:

- `test_climatebert_logic.csv`
  - validation or API test output for climatebert-logic interactions

## 10. `results/background_llm_jobs/`

Background T3 / LLM extraction execution folders.

### Folder schema

Typical files:

- `config.json`
  - job configuration
- `control.json`
  - runtime control or cancellation flags
- `events.jsonl`
  - chronological event log
- `status.json`
  - current summary status
- `worker.log`
- `worker.err.log`

### `status.json` shape

Typical keys:

- `job_id`
- `status`
- `document`
- `total`
- `completed`
- `failed`
- `skipped`
- `current`
- `created_at`
- `updated_at`
- `pid`
- `started_at`
- `finished_at`

## 11. `results/climatebert_background_jobs/`

Background ClimateBERT execution folders.

### Folder schema

Typical files:

- `config.json`
- `control.json`
- `events.jsonl`
- `status.json`
- `worker.out.log`
- `worker.err.log`
- `climatebert_output.csv`
- `climatebert_record_batch_import.csv`

### `events.jsonl` shape

Typical rows include:

- `time`
- `event`
- `model_backend`
- `model_id`
- `local_model_path`
- `total`
- `dry_run`
- `record_id`

This makes the folder both:

- an execution-state bundle
- a result bundle

## 12. `results/ch4_6_frozen_analysis/`

Frozen analysis bundle for chapter work.

Files:

- `analysis_snapshot.pkl`
- `graphs/*.png`

Purpose:

- pin chapter figures and avoid drift while writing or packaging chapters 4-6

## 13. `results/data/`

Currently includes:

- `mapping.json`

Purpose:

- auxiliary mapping artifact for result workflows

## 14. `results/llm_processing_process/`

- Present as a subfolder in the tree.
- Likely reserved for process-state outputs related to `llm_processing.py`.

## 15. Best Interactive Consumers of `results/`

- `pages/backend/app.py`
- `pages/2_3_LLM_Background_Run_Monitor.py`
- `pages/2_0_LLM_Processing_Result_Visualizer.py`
- `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`
- `pages/5_Thesis_Systematic_Workflow_dashboard.py`
- `pages/6_4_ch4-6.py`

## 16. Summary

The most important result areas are:

- `results/esg_records.json` for primary LLM extraction
- `results/revision_analysis/` for compact analysis datasets
- `results/thesis_workflow_dashboard/` for dashboard contracts
- `results/visualizations/` for comparison charts and flat tables
- `results/background_llm_jobs/` and `results/climatebert_background_jobs/` for reproducibility and provenance
- `results/semantic_exports/` and `results/transfer_learning/` for downstream advanced uses
