# Code Module Inventory Documentation

This document describes the shared Python modules in `code/`.

For the repository-wide context, see [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md). For page-level coverage, see [documentation_pages_inventory.md](/home/ubuntu/apps/benchmarks/new_page/documentation_pages_inventory.md).

## 1. Purpose of `code/`

The `code/` directory is the shared logic layer behind the thesis dashboards and background workers. It contains:

- worker implementations
- analysis helpers
- graph and export utilities
- multiple modeling baselines
- thesis-chapter rendering helpers

## 2. Module-by-Module Inventory

### `code/__init__.py`

- Purpose: package marker for the shared module directory.

### `code/app_state.py`

- Main type:
  - `AppState`
- Purpose:
  - lightweight dict-style state container
  - shared utility for app-local state patterns

### `code/utils.py`

- Main types and functions:
  - `Sentence`
  - `detect_lang`
  - `parse_document`
  - `safe_plot`
- Purpose:
  - low-level text parsing and language detection
  - split raw text into sentence-like units
  - safe plotting wrapper behavior

### `code/lexicons.py`

- Main functions:
  - `any_match`
- Purpose:
  - lexical pattern / trigger matching support
  - likely reused by rule-based or heuristic pipelines

### `code/rule_based.py`

- Main functions:
  - `collect_aspects`
  - `polarity_basic`
  - `tone_basic`
  - `rq1_sentence_only`
  - `rq1_hierarchical`
  - `rq2_tone_and_sentiment`
  - `rq3_ontology`
  - `explain_rule_based_sentence`
  - `run_rule_based`
- Purpose:
  - rule-based baseline for aspect collection, sentiment, tone, and ontology mapping
  - generates explainable baseline outputs without heavy model dependencies

### `code/classical_ml.py`

- Main types and functions:
  - `Featureizer`
  - `_safe_fit_classifier`
  - `coef_table_binary_safe`
  - `coef_table_aspect`
  - `local_explain`
  - `build_ml_df`
  - `run_classical_ml`
  - `explain_classical_sentence`
- Purpose:
  - classical ML baseline pipeline
  - feature engineering, fitting, explanation, and coefficient reporting

### `code/deep_model.py`

- Main types and functions:
  - `SimpleDLModel`
  - `DLDataset`
  - `labels_for_dl`
  - `run_deep_learning`
  - `explain_deep_sentence`
  - `plot_attention_plotly`
- Purpose:
  - deep-learning baseline for sentence-level ESG analysis
  - produces predictions and attention-like explainability outputs

### `code/deep_model_v2.py`

- Main types and functions:
  - `SimpleDLModel`
  - `DLDataset`
  - `labels_for_dl`
  - `run_deep_learning`
  - `explain_deep_sentence`
  - `plot_attention_plotly`
- Purpose:
  - alternate deep-learning implementation or refinement over `deep_model.py`

### `code/hybrid_model.py`

- Main types and functions:
  - `HierarchicalEncoder`
  - `MTLHybrid`
  - `encode_texts_small`
  - `make_ontology_vectors`
  - `run_hierarchical_hybrid`
  - `explain_hybrid_sentence`
  - `plot_ontology_scatter`
- Purpose:
  - multi-task hybrid model for sentiment, tone, and ontology alignment
  - likely central to T2-style hybrid outputs used in ground-truth artifacts

### `code/explainability.py`

- Main functions:
  - `_get_df_safe`
  - `compare_explain`
  - `explain_sentence_across_models`
  - `plot_consistency_summary`
- Purpose:
  - compare and explain predictions across multiple model families
  - support diagnostic views rather than production inference

### `code/data_alignment.py`

- Main functions:
  - `load_json`
  - `safe_get_absa_df`
  - `normalize_col_candidates`
  - `fuzzy_ratio`
  - `match_absa_rows_by_text`
  - `extract_absa_sentiment`
  - `extract_absa_aspect`
  - `majority_vote`
  - `build_benchmark_map`
  - `save_confusion_matrix`
  - `align_and_evaluate`
- Purpose:
  - align benchmark or ABSA outputs across inconsistent schemas
  - fuzzy text matching between result tables
  - evaluation support once rows are aligned

### `code/action_plan_status.py`

- Main functions:
  - `load_csv`
  - `load_json`
  - `column_series`
  - `nonempty_count`
  - `normalise_cols`
  - `normalise_annotation_values`
  - `build_annotation_table`
  - `ann_n`
  - `climatebert_processed_record_ids`
  - `record_value`
  - `load_esg_record_runs`
  - `derive_model_stability_from_llm_runs`
  - `combine_model_stability`
  - `action_plan_status_rows`
- Purpose:
  - derive progress-tracking tables for the Thesis Action Plan
  - consolidate live and static metrics from revision-analysis files and `results/esg_records.json`

### `code/graph_attachment_gallery.py`

- Main functions:
  - `graph_attachment_manifest`
  - `source_dataframe_for_attachment`
  - `filter_manifest`
  - `render_attachment_cards`
  - plus helpers for counts, completion rows, repeated-run grids, and agreement summaries
- Purpose:
  - maintain the gallery of chart attachments used across chapter pages
  - connect each figure to its source data and source page

### `code/ground_truth_graphs.py`

- Main functions:
  - `load_json_or_jsonl`
  - `flatten_t1`
  - `flatten_t2`
  - `load_t1_outputs`
  - `load_t2_outputs`
  - `attach_t2_review_ids`
  - `apply_t2_review_corrections`
  - `apply_a28_ontology_corrections`
  - `consolidated_t2_outputs`
  - `t1_status_rows`
  - `t1_prediction_rows`
  - `t2_rule_tone_rows`
  - `t2_hybrid_tone_rows`
  - `t2_sentiment_rows`
  - `t2_ontology_path_rows`
  - `t2_numeric_summary_rows`
  - `draw_bar`
  - `draw_heatmap`
  - `ensure_ground_truth_graphs`
  - `ground_truth_attachment_rows`
  - `ground_truth_source_dataframe`
- Purpose:
  - flatten and normalize ground-truth outputs
  - produce chart data and exported graph images for the ground-truth attachment gallery

### `code/visualize_tone_climatebert.py`

- Main functions:
  - `clean_label`
  - `normalize_tone`
  - `load_esg_records`
  - `parse_climatebert_response`
  - `load_climatebert_rows`
  - `save_bar`
  - `save_stacked_tone_esg`
  - `save_heatmap`
  - `climatebert_label_family`
  - `write_doc`
  - `main`
- Purpose:
  - transform ESG extraction and ClimateBERT outputs into comparison tables and charts
  - likely the core generator for the tone-vs-ClimateBERT visual artifacts

### `code/semantic_exporter.py`

- Main types and functions:
  - `SemanticBundle`
  - `load_semantic_bundle`
  - `canonical_records`
  - `ontology_rows`
  - `build_turtle`
  - `build_owl_xml`
  - `build_neo4j_files`
  - `export_all`
  - `write_exports`
  - `zip_bytes`
- Purpose:
  - convert ESG evidence tables and ontology coverage into semantic web and graph-database exports

Input assumptions:

- `results/visualizations/tone_records_flat.csv`
- `results/revision_analysis/silver_tone_ground_truth.csv`
- `results/revision_analysis/ontology_coverage.csv`
- `results/revision_analysis/ontology.json`

### `code/llm_background_worker.py`

- Main functions:
  - JSON read/write helpers
  - JSONL append helpers
  - URL normalization for OpenAI-style and Ollama backends
  - `apply_prompt`
  - `parse_json_from_model`
  - `classify_error`
  - retry-budget and context-slicing helpers
  - backend call functions:
    - `call_openrouter`
    - `call_lmstudio`
    - `call_ollama`
  - orchestration helpers:
    - `call_llm`
    - `build_batches`
    - `build_context_prompt`
    - `load_prompts`
    - `processed_successes`
    - `update_status`
    - `main`
- Purpose:
  - main background execution engine for T3-style LLM ESG extraction jobs

### `code/ground_truth_background_worker.py`

- Main functions:
  - serialization and JSON helpers
  - `append_jsonl_locked`
  - `append_event`
  - `update_status`
  - processed-record discovery helpers for T1 and T2
  - local-model discovery and loading
  - `run_t1_item`
  - `run_t2_item`
  - `main`
- Purpose:
  - background executor for ground-truth related jobs
  - orchestrates T1 and T2 processing at record level

### `code/climatebert_background_worker.py`

- Main functions:
  - JSON helpers
  - status/event writing
  - `is_commitment_label`
  - `load_existing_outputs`
  - `load_pipeline_safe`
  - `main`
- Purpose:
  - background executor for ClimateBERT batch jobs and multi-model runs

### `code/thesis_chapter_streamlit.py`

- Main functions:
  - data loading and formatting helpers
  - DOCX and PDF parsing:
    - `read_chapter_docx`
    - `chapter_outline`
    - `read_pdf_text`
    - `pdf_outline`
  - Mermaid rendering:
    - `mermaid_html`
    - `render_mermaid`
    - `thesis_spine_mermaid`
    - `rq_evidence_mermaid`
    - `pipeline_mermaid`
    - `validation_mermaid`
    - `artifact_mermaid`
  - chapter rendering:
    - `render_chapter_text`
    - `generated_chapter4_paragraph`
    - `generated_chapter5_paragraph`
    - `generated_chapter6_paragraph`
  - dashboard bundle helpers:
    - `workflow_rq_df`
    - `artifact_inventory`
    - `derive_live_model_stability`
    - `combine_model_stability`
    - `data_bundle`
  - chart helpers:
    - `workflow_coverage_chart`
    - `pdf_prompt_heatmap`
    - `ontology_chart`
    - `model_stability_chart`
    - `prompt_stability_chart`
    - `artifact_chart`
    - `agreement_chart`
- Purpose:
  - shared rendering and evidence glue for thesis chapter pages
  - bridges document assets, result tables, and generated thesis claims

## 3. Functional Grouping

### Worker and execution modules

- `llm_background_worker.py`
- `ground_truth_background_worker.py`
- `climatebert_background_worker.py`

### Evidence derivation and chart modules

- `action_plan_status.py`
- `graph_attachment_gallery.py`
- `ground_truth_graphs.py`
- `visualize_tone_climatebert.py`

### Export and thesis integration modules

- `semantic_exporter.py`
- `thesis_chapter_streamlit.py`

### Modeling and experimentation modules

- `rule_based.py`
- `classical_ml.py`
- `deep_model.py`
- `deep_model_v2.py`
- `hybrid_model.py`
- `explainability.py`

### Shared utilities

- `app_state.py`
- `utils.py`
- `lexicons.py`
- `data_alignment.py`

## 4. Most Important Modules for Day-to-Day Work

- If you are debugging LLM extraction:
  - `llm_background_worker.py`
- If you are debugging ClimateBERT runs:
  - `climatebert_background_worker.py`
- If you are debugging ground-truth outputs:
  - `ground_truth_background_worker.py`
  - `ground_truth_graphs.py`
- If you are working on thesis chapter pages:
  - `thesis_chapter_streamlit.py`
  - `graph_attachment_gallery.py`
- If you are working on semantic export:
  - `semantic_exporter.py`

## 5. Summary

The `code/` directory is the implementation backbone of the repository. The most central responsibilities are:

- background execution for T1, T2, T3, and ClimateBERT jobs
- normalization of revision-analysis and result datasets
- generation of dashboard tables and graph attachments
- semantic export and thesis chapter integration
- baseline modeling and explainability
