# Benchmarks Repository Documentation

_Generated on 2026-05-25 17:19:49_

## Scope

- This file documents all Python code files in this repository (excluding `venv/`, `.git/`, and cache folders).
- Total Python files documented: **349**.
- Focus is practical: entry points, module purpose, and file-by-file inventory.

## High-Level Architecture

- **Root app and scripts**: lightweight Streamlit entry (`app.py`) plus helper scripts for metrics/extraction/export.
- **`api/`**: wrappers for ABSA, ClimateBERT, ESG-data, and Space URL resolution.
- **`code/`**: core ABSA and alignment engine (rule/classical/deep/hybrid/explainability + parsers).
- **`pages/` + `current_pages/` + `old_pages/`**: Streamlit page suites (legacy/current/archived).
- **`utils/` / `services/` / `ui/` / `config/`**: shared helpers, inference loader, UI components, and registries.
- **`esg_dashboard_new-main/`**: packaged dashboard variant with its own pages/utils/services.
- **`new_page/`**: thesis workflow workspace (OCR, LLM, ground-truth, chapter integration, background jobs, graph export).
- **`model_download/`**: local model download/inference sandbox pages.

## Repository Stats

### Files by Area

- `.`: 13 files
- `api`: 5 files
- `code`: 12 files
- `config`: 1 files
- `services`: 2 files
- `ui`: 3 files
- `utils`: 29 files
- `pages`: 55 files
- `current_pages`: 43 files
- `old_pages`: 14 files
- `model_download`: 6 files
- `esg_dashboard_new-main`: 47 files
- `new_page`: 119 files

### Files by Category

- `streamlit_page`: 179
- `module`: 48
- `utility`: 40
- `core_module`: 32
- `page_script`: 12
- `api_client`: 7
- `ops_script`: 7
- `script`: 7
- `ui_component`: 6
- `streamlit_app`: 5
- `service`: 4
- `config`: 2

## Primary Entrypoints

| File | Type | Summary |
|---|---|---|
| `app.py` | app entry | Streamlit app for "🌱 ESG Scoring Dashboard". |
| `code/data_alignment.py` | main-guard script | Defines functions: load_json, safe_get_absa_df, normalize_col_candidates. |
| `code/streamlit_app.py` | app entry | Module related to "ESG Alignment & Evaluation (interactive)". |
| `esg_dashboard_new-main/dashboard/app.py` | app entry | Streamlit app for "📊 ESG Sentence-Level Analytics Dashboard". |
| `esg_dashboard_new-main/dashboard/pages/generate_research_question_artifacts.py` | main-guard script | Defines functions: load_font, extract_rq_data, status_frame. |
| `esg_dashboard_new-main/structure_code.py` | main-guard script | Defines functions: build_tree_html, save_tree_to_markdown. |
| `export_image_outputs.py` | main-guard script | Defines functions: slugify, file_sha256, png_dimensions. |
| `model_download/app.py` | app entry | Application entry point. |
| `new_page/app.py` | app entry | Application entry point. |
| `new_page/code/climatebert_background_worker.py` | main-guard script | Defines functions: utc_now, read_json, write_json. |
| `new_page/code/data_alignment.py` | main-guard script | Defines functions: load_json, safe_get_absa_df, normalize_col_candidates. |
| `new_page/code/ground_truth_background_worker.py` | main-guard script | Defines functions: utc_now, serialize, read_json. |
| `new_page/code/llm_background_worker.py` | main-guard script | Defines functions: utc_now, read_json, write_json. |
| `new_page/code/visualize_tone_climatebert.py` | main-guard script | Generate tone-vs-ClimateBERT visualizations and documentation. |
| `new_page/hidden_pages/0_0_0_0_1_master_thesis_prompt.py` | main-guard script | Module related to "ESG Prompt - Quick Viewer". |
| `new_page/hidden_pages/0_0_0_0_2_combined_master_thesis_prompt.py` | main-guard script | Module related to "Combined ESG Prompt Viewer". |
| `new_page/hidden_pages/0_0_0_0_3_combined_master_thesis_prompt_notes.py` | main-guard script | Module related to "Combined ESG Prompt Viewer". |
| `new_page/hidden_pages/0_0_0_1_esg_matching_evaluation.py` | main-guard script | Module related to "🌍 ESG Matching & Evaluation Dashboard". |
| `new_page/past_pages/streamlit_app.py` | app entry | Module related to "ESG Alignment & Evaluation (interactive)". |
| `new_page/scripts/compare_runs.py` | main-guard script | Defines functions: load_manifest, index_files, resolve_manifest. |
| `new_page/scripts/generate_manifest.py` | main-guard script | Defines functions: now_utc_iso, git_commit, sha256_file. |
| `new_page/scripts/start_run.py` | main-guard script | Defines functions: git_commit, main. |
| `new_page/social_network_analysis/app.py` | app entry | Streamlit app for "ESG Report Network Analysis - Adapted Framework". |
| `new_page/summarization/app.py` | main-guard script | Streamlit app for "ESG ABSA Summarization Workspace". |
| `new_page/tools/build_coherent_thesis_docx.py` | main-guard script | Defines functions: set_cell_shading, set_cell_text, add_table. |
| `new_page/tools/climatebert_a4/generate_a4_per_model.py` | main-guard script | Defines functions: slugify, crosstab_for_group, main. |
| `new_page/tools/generate_chapter_resolution_artifacts.py` | main-guard script | Defines functions: read_csv, write_csv, pct. |
| `new_page/tools/update_ch4_6_docx_graphs.py` | main-guard script | Defines functions: load_csv, font, wrap_text. |
| `new_page/topic_modelling/app.py` | app entry | Streamlit app for "ESG Sustainability Report Analysis - Complete Task Framework". |
| `structure_code.py` | main-guard script | Defines functions: build_tree_html, save_tree_to_markdown. |
| `utils/merge_climatebert_absa.py` | main-guard script | Defines functions: merge. |
| `utils/parse_climatebert_results.py` | main-guard script | Parsing utility for model/data outputs. |
| `utils/save_climatebert_results.py` | main-guard script | Defines functions: save_climatebert_results. |

## Complete File Inventory

Legend: `Category` = functional role inferred from path/content. `Key Symbols` lists top-level classes/functions when available.

### `.` (13 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `6_4_ch4-6.py` | `module` | Module related to "Ch4-6 Structure Benchmarks and Graph Attachments". | read_docx_paragraphs, media_count, chart_font, wrap_label |
| `api_client.py` | `api_client` | Client wrapper for external model/API calls. | get_client, predict_esg |
| `app.py` | `streamlit_app` | Streamlit app for "🌱 ESG Scoring Dashboard". |  |
| `batch_predict.py` | `module` | Batch processing script/module. |  |
| `calc_absa_metrics.py` | `module` | Metrics computation/visualization utility. | safe_report |
| `export_image_outputs.py` | `script` | Defines functions: slugify, file_sha256, png_dimensions. | slugify, file_sha256, png_dimensions, image_paths |
| `extract_absa_mapping_all_sentiment_category_tone.py` | `module` | No module docstring; utility/support code. |  |
| `extract_absa_mapping_simple.py` | `module` | No module docstring; utility/support code. |  |
| `finbert_model.py` | `module` | Defines classes: MultiTaskFinBERT. | MultiTaskFinBERT |
| `model_utils.py` | `module` | Defines functions: torch_available, get_hf_inference_client, make_hf_api_prediction. | torch_available, get_hf_inference_client, make_hf_api_prediction, get_multitask_model_class |
| `structure_code.py` | `script` | Defines functions: build_tree_html, save_tree_to_markdown. | build_tree_html, save_tree_to_markdown |
| `test.py` | `module` | No module docstring; utility/support code. |  |
| `test_api.py` | `module` | No module docstring; utility/support code. |  |

### `api` (5 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `api/_space_url.py` | `api_client` | Utility helpers for resolving a Gradio Space URL. | resolve_space_url |
| `api/absa_client.py` | `api_client` | Client wrapper for external model/API calls. | _get_client, run_rule, run_classical, run_classical_alt |
| `api/climatebert_client.py` | `api_client` | Client wrapper for external model/API calls. | ClimateBERTClient |
| `api/climatebert_client_combined.py` | `api_client` | Client wrapper for external model/API calls. | _get_space_url, predict_all_models |
| `api/esgdata_client.py` | `api_client` | Client wrapper for external model/API calls. | _get_space_url, _get_client, preprocess, run_training |

### `code` (12 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `code/__init__.py` | `core_module` | No module docstring; utility/support code. |  |
| `code/app_state.py` | `core_module` | Defines classes: AppState. | AppState |
| `code/classical_ml.py` | `core_module` | core/classical_ml.py Classical ML pipeline for ESG ABSA: - TF-IDF (word + char) featureizer - One-vs-Rest logistic regression for multi-label aspects - Logistic regression (or Dum… | Featureizer, _safe_fit_classifier, coef_table_binary_safe, coef_table_aspect, local_explain |
| `code/data_alignment.py` | `core_module` | Defines functions: load_json, safe_get_absa_df, normalize_col_candidates. | load_json, safe_get_absa_df, normalize_col_candidates, fuzzy_ratio |
| `code/deep_model.py` | `core_module` | core/deep_model.py Deep learning module (mBERT) for ESG ABSA: - Light-weight training loop for demo / explainability - Extracts attention-based token importances (simple first-lay… | SimpleDLModel, DLDataset, labels_for_dl, run_deep_learning, explain_deep_sentence, plot_attention_plotly |
| `code/deep_model_v2.py` | `core_module` | core/deep_model.py Deep learning module (mBERT) for ESG ABSA: - Light-weight training loop for demo / explainability - Extracts attention-based token importances (simple first-lay… | SimpleDLModel, DLDataset, labels_for_dl, run_deep_learning, explain_deep_sentence, plot_attention_plotly |
| `code/explainability.py` | `core_module` | core/explainability.py Cross-model explainability and visualization layer for ESG ABSA. | _get_df_safe, compare_explain, explain_sentence_across_models, plot_consistency_summary |
| `code/hybrid_model.py` | `core_module` | core/hybrid_model.py Hierarchical encoder + MTL Hybrid model (Hybrid++) for ESG ABSA. | HierarchicalEncoder, MTLHybrid, encode_texts_small, make_ontology_vectors, run_hierarchical_hybrid, explain_hybrid_sentence |
| `code/lexicons.py` | `core_module` | core/lexicons.py Lexical resources and ontology mappings for ESG ABSA Framework. | any_match |
| `code/rule_based.py` | `core_module` | core/rule_based.py Rule-based RQ1–RQ3 pipeline for ESG ABSA. | collect_aspects, polarity_basic, tone_basic, rq1_sentence_only |
| `code/streamlit_app.py` | `core_module` | Module related to "ESG Alignment & Evaluation (interactive)". |  |
| `code/utils.py` | `core_module` | core/utils.py Utility functions and shared data structures for the ESG ABSA framework. | Sentence, detect_lang, parse_document, safe_plot |

### `config` (1 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `config/model_registry.py` | `config` | No module docstring; utility/support code. |  |

### `services` (2 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `services/hf_loader.py` | `service` | Defines functions: load_pipeline. | load_pipeline |
| `services/inference.py` | `service` | Defines functions: run_inference. | run_inference |

### `ui` (3 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `ui/results.py` | `ui_component` | Defines functions: render_results. | render_results |
| `ui/sidebar.py` | `ui_component` | Defines functions: render_sidebar. | render_sidebar |
| `ui/text_input.py` | `ui_component` | Defines functions: render_text_input. | render_text_input |

### `utils` (29 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `utils/alignment.py` | `utility` | Defines functions: align_by_sentence. | align_by_sentence |
| `utils/api_safe.py` | `utility` | Defines functions: safe_api_call. | safe_api_call |
| `utils/aspect_clustering.py` | `utility` | Defines functions: cluster_aspect. | cluster_aspect |
| `utils/climatebert_analysis.py` | `utility` | Defines functions: load_ground_truth, load_predictions, merge_ground_truth. | load_ground_truth, load_predictions, merge_ground_truth, compute_model_metrics |
| `utils/climatebert_batch.py` | `utility` | Batch processing script/module. | batch_process_csv |
| `utils/climatebert_batch_core.py` | `utility` | Batch processing script/module. | detect_text_column, batch_process_core |
| `utils/climatebert_batch_windows.py` | `utility` | Batch processing script/module. | batch_process_csv_windows |
| `utils/climatebert_groundtruth_storage.py` | `utility` | Defines functions: _ensure_dir, _atomic_write, load_results. | _ensure_dir, _atomic_write, load_results, save_result |
| `utils/climatebert_groundtruth_storage_windows.py` | `utility` | Defines functions: _ensure_dir, _atomic_write, load_results. | _ensure_dir, _atomic_write, load_results, save_result |
| `utils/climatebert_parser.py` | `utility` | Parsing utility for model/data outputs. | parse_climatebert_markdown, flatten_climatebert |
| `utils/climatebert_storage.py` | `utility` | Defines functions: save_parsed_result, load_parsed_results. | save_parsed_result, load_parsed_results |
| `utils/climatebert_storage_windows.py` | `utility` | Defines functions: _ensure_dir, _atomic_write, load_results. | _ensure_dir, _atomic_write, load_results, save_result |
| `utils/compare_logic.py` | `utility` | Defines functions: find_missing. | find_missing |
| `utils/data_loader.py` | `utility` | Defines functions: extract_json_block, normalize_json, parse_esg_json. | extract_json_block, normalize_json, parse_esg_json, load_and_parse |
| `utils/dataframe.py` | `utility` | Defines functions: hf_to_df. | hf_to_df |
| `utils/env.py` | `utility` | Defines functions: get_hf_token. | get_hf_token |
| `utils/error_logger.py` | `utility` | Defines functions: log_error. | log_error |
| `utils/file_handler.py` | `utility` | Defines functions: render_hf_image, render_download. | render_hf_image, render_download |
| `utils/formatter.py` | `utility` | Defines functions: format_result. | format_result |
| `utils/json_logger.py` | `utility` | Defines functions: save_result, load_results. | save_result, load_results |
| `utils/load_hf_file.py` | `utility` | Defines functions: load_csv_from_hf. | load_csv_from_hf |
| `utils/logger.py` | `utility` | Defines functions: load_history, save_history. | load_history, save_history |
| `utils/merge_climatebert_absa.py` | `utility` | Defines functions: merge. | merge |
| `utils/metrics.py` | `utility` | Metrics computation/visualization utility. | normalize_labels, compute_metrics |
| `utils/parse_climatebert_results.py` | `utility` | Parsing utility for model/data outputs. | parse_climatebert_results |
| `utils/save_climatebert_results.py` | `utility` | Defines functions: save_climatebert_results. | save_climatebert_results |
| `utils/validation.py` | `utility` | Defines functions: validate_columns. | validate_columns |
| `utils/visual_utils.py` | `utility` | No module docstring; utility/support code. |  |
| `utils/visualization.py` | `utility` | Defines functions: _decode_base64_image, _render_plotly, _render_matplotlib. | _decode_base64_image, _render_plotly, _render_matplotlib, _render_altair |

### `pages` (55 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `pages/00_Streamlit_Page_Workflow.py` | `streamlit_page` | Streamlit page for "Streamlit Page Workflow". | render_desktop_safe_mermaid, render_workflow_cards, available_pages, page_route |
| `pages/04_Research_Questions_Visualizer.py` | `streamlit_page` | Streamlit page for "Research Questions Visualizer". | render_mermaid, mermaid_download_section, mermaid_label, mermaid_id |
| `pages/05_Sample_Size_Reasoning.py` | `streamlit_page` | Streamlit page for "Sample Size Reasoning". | render_mermaid, mermaid_download_section, mermaid_label, load_absa_metrics |
| `pages/06_Chapter_4_Results.py` | `streamlit_page` | Streamlit page for "Chapter 4 Results". |  |
| `pages/07_Chapter_5_Discussion.py` | `streamlit_page` | Streamlit page for "Chapter 5 Discussion". |  |
| `pages/0_0_0_1.py` | `page_script` | No module docstring; utility/support code. |  |
| `pages/0_0_0_code.py` | `page_script` | No module docstring; utility/support code. |  |
| `pages/0_0_1_Single_Prediction.py` | `streamlit_page` | Streamlit page for "🔎 Single Prediction". |  |
| `pages/0_0_1_multiple_Prediction.py` | `streamlit_page` | Streamlit page for "🔎 Multi-Model Prediction". |  |
| `pages/0_0_2_Batch_Prediction.py` | `streamlit_page` | Streamlit page for "📊 Batch Prediction". |  |
| `pages/0_0_3_Model_Explorer.py` | `streamlit_page` | Streamlit page for "🧠 Model Explorer". |  |
| `pages/0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py` | `streamlit_page` | Streamlit page for "ClimateBERT Batch Processor (Linux)". | update |
| `pages/0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py` | `streamlit_page` | Streamlit page for "ClimateBERT Batch Processor (Windows)". | update |
| `pages/0_0_ClimateBERT_4_Model_Analysis.py` | `streamlit_page` | Streamlit page for "ClimateBERT Model Analysis". |  |
| `pages/0_0_ClimateBERT_5_Model_Deep_Explorer.py` | `streamlit_page` | Streamlit page for "ClimateBERT Model Deep Explorer". |  |
| `pages/0_0_ClimateBERT_6_Model_Overview_All.py` | `streamlit_page` | Streamlit page for "ClimateBERT All Models Visualization". |  |
| `pages/0_0_ClimateBERT_7_Full_Model_Visualization.py` | `streamlit_page` | Streamlit page for "ClimateBERT Full Model Visualization". | load_data |
| `pages/0_ClimateBERT_Commitment_Distribution.py` | `streamlit_page` | Streamlit page for "Climate Commitment Model Analysis". | load_data |
| `pages/10_Chapter_6_Conclusion.py` | `streamlit_page` | Streamlit page for "Chapter 6 Conclusion". |  |
| `pages/1_ABSA_Integration.py` | `streamlit_page` | Streamlit page for "ABSA Mapping with ClimateBERT Results". |  |
| `pages/1_Analyze.py` | `streamlit_page` | Streamlit page for "🌱 ESG Text Analyzer". |  |
| `pages/2_ABSA_Rule_Based.py` | `streamlit_page` | Streamlit page for "ABSA Rule-Based Ontology". |  |
| `pages/3_ABSA_Classical.py` | `streamlit_page` | Streamlit page for "ABSA Classical ML". |  |
| `pages/5_ABSA_Deep_Learning.py` | `streamlit_page` | Streamlit page for "ABSA Deep Learning". |  |
| `pages/6_4_ch4-6.py` | `streamlit_page` | Streamlit page for "Ch4-6 Structure Benchmarks and Graph Attachments". | _load_dashboard_data_loader, _load_ontology, _ontology_alias_map, read_docx_paragraphs |
| `pages/ABSA_Model_Comparison.py` | `streamlit_page` | Streamlit page for "ABSA Model Comparison: Input Text and Compare All Modules". |  |
| `pages/Research_Questions_Dashboard.py` | `streamlit_page` | Streamlit page for "Research Questions Dashboard". |  |
| `pages/_page_explanations.py` | `streamlit_page` | Defines functions: add_page_explanation, add_section_explanation. | add_page_explanation, add_section_explanation |
| `pages/_rq_thesis_content.py` | `streamlit_page` | Defines functions: research_questions_df, chapter4_results_df, evidence_rows_df. | research_questions_df, chapter4_results_df, evidence_rows_df, page_mapping_df |
| `pages/_shared/__init__.py` | `page_script` | No module docstring; utility/support code. |  |
| `pages/_shared/page_explanations.py` | `streamlit_page` | Defines functions: add_page_explanation, add_section_explanation. | add_page_explanation, add_section_explanation |
| `pages/absa_metrics_comparison copy.py` | `streamlit_page` | Streamlit page for "ABSA Mapping Metrics Comparison". | normalize_labels, compute_metrics |
| `pages/absa_metrics_comparison.py` | `streamlit_page` | Streamlit page for "ABSA Mapping Metrics Comparison". | normalize_labels, compute_metrics, map_to_cluster |
| `pages/absa_metrics_comparison_mac.py` | `streamlit_page` | Streamlit page for "ABSA Mapping Metrics Comparison". | normalize_labels, compute_metrics, map_to_cluster, safe_merge |
| `pages/absa_metrics_visualization.py` | `streamlit_page` | Streamlit page for "ABSA Metrics Results Visualization". | config_has_model_type, has_model_weight, resolve_local_model_dir, normalize_label |
| `pages/absa_ontology_3_deep_model.py` | `streamlit_page` | Streamlit page for "Deep Model (mBERT) Demo". |  |
| `pages/absa_ontology_all.py` | `streamlit_page` | Streamlit page for "ABSA Ontology Modules". |  |
| `pages/absa_ontology_all_new_notes.py` | `streamlit_page` | Streamlit page for "ABSA Ontology Modules". |  |
| `pages/esg_dashboard_new_01_Aspects_Raw.py` | `streamlit_page` | Streamlit page for "📌 Aspects — Raw Model Output". |  |
| `pages/esg_dashboard_new_02_Aspects_Clustered.py` | `streamlit_page` | Streamlit page for "🧩 Aspects — After Manual Clustering". |  |
| `pages/esg_dashboard_new_03_Aspect_Comparison.py` | `streamlit_page` | Streamlit page for "🔍 Aspect Mapping — Before vs After". |  |
| `pages/esg_dashboard_new_0_Metric_Analysis.py` | `streamlit_page` | Streamlit page for "📊 Metric Analysis — Ground Truth vs Prediction". |  |
| `pages/esg_dashboard_new_0_new.py` | `streamlit_page` | Streamlit page for "📊 ESG Parsed Sentence-Level Dashboard". | load_data, extract_json_block, normalize_json, is_valid_esg_object |
| `pages/esg_dashboard_new_8_new.py` | `streamlit_page` | Streamlit page for "📊 ESG Parsed Sentence-Level Dashboard". | extract_json_block, normalize_json, is_valid_esg_object, parse_esg_json |
| `pages/esg_dashboard_new_Benchmark_Model.py` | `streamlit_page` | Streamlit page for "🌍 ESG & Climate NLP Model Tester". |  |
| `pages/esg_dashboard_new_Data Distribution.py` | `streamlit_page` | Streamlit page for "🔍 Aspect & Ontology Visualization Dashboard". | normalize_aspect_category, aspect_label, normalize_sentiment, sentiment_label |
| `pages/esg_dashboard_new_Data_New_Distribution.py` | `streamlit_page` | Streamlit page for "ESG Sankey & Filters". | load_dataset, load_ontology, build_alias_map, normalize |
| `pages/esg_dashboard_new_Distribution Document.py` | `streamlit_page` | Streamlit page for "🧠 ESG Sentiment & Tone — Document-Level Analysis". | build_alias_map, normalize_sentiment, normalize_tone |
| `pages/esg_dashboard_new_Sankey.py` | `streamlit_page` | Streamlit page for "📤 Upload-Based Tone Distribution & Balancer". | build_alias_map, normalize, build_alias_map, normalize |
| `pages/esg_dashboard_new_Tone_Distribution.py` | `streamlit_page` | Streamlit page for "📊 Tone Distribution Explorer". | load_json_from_candidates, build_alias_map, normalize, load_master |
| `pages/parse_documentation_json.py` | `streamlit_page` | Streamlit page for "Documentation JSON Table Viewer". |  |
| `pages/scrambled_absa_mapping_baseline.py` | `streamlit_page` | Streamlit page for "Scrambled ABSA Mapping Baseline". |  |
| `pages/scrambled_absa_mapping_baseline_mac.py` | `streamlit_page` | Streamlit page for "Scrambled ABSA Mapping Baseline". |  |
| `pages/test_models.py` | `streamlit_page` | Streamlit page for "ESG ABSA Model Tester". |  |
| `pages/zz_aspect_clusters.py` | `streamlit_page` | Streamlit page for "🔗 Aspect Clusters Explorer". |  |

### `current_pages` (43 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `current_pages/0_0_0_1.py` | `page_script` | No module docstring; utility/support code. |  |
| `current_pages/0_0_0_code.py` | `page_script` | No module docstring; utility/support code. |  |
| `current_pages/0_0_1_Single_Prediction.py` | `streamlit_page` | Streamlit page for "🔎 Single Prediction". |  |
| `current_pages/0_0_1_multiple_Prediction.py` | `streamlit_page` | Streamlit page for "🔎 Multi-Model Prediction". |  |
| `current_pages/0_0_2_Batch_Prediction.py` | `streamlit_page` | Streamlit page for "📊 Batch Prediction". |  |
| `current_pages/0_0_3_Model_Explorer.py` | `streamlit_page` | Streamlit page for "🧠 Model Explorer". |  |
| `current_pages/0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py` | `streamlit_page` | Streamlit page for "ClimateBERT Batch Processor (Linux)". | update |
| `current_pages/0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py` | `streamlit_page` | Streamlit page for "ClimateBERT Batch Processor (Windows)". | update |
| `current_pages/0_0_ClimateBERT_4_Model_Analysis.py` | `streamlit_page` | Streamlit page for "ClimateBERT Model Analysis". |  |
| `current_pages/0_0_ClimateBERT_5_Model_Deep_Explorer.py` | `streamlit_page` | Streamlit page for "ClimateBERT Model Deep Explorer". |  |
| `current_pages/0_0_ClimateBERT_6_Model_Overview_All.py` | `streamlit_page` | Streamlit page for "ClimateBERT All Models Visualization". |  |
| `current_pages/0_0_ClimateBERT_7_Full_Model_Visualization.py` | `streamlit_page` | Streamlit page for "ClimateBERT Full Model Visualization". | load_data |
| `current_pages/0_ClimateBERT_Commitment_Distribution.py` | `streamlit_page` | Streamlit page for "Climate Commitment Model Analysis". | load_data |
| `current_pages/1_ABSA_Integration.py` | `streamlit_page` | Streamlit page for "ABSA Mapping with ClimateBERT Results". |  |
| `current_pages/1_Analyze.py` | `streamlit_page` | Streamlit page for "🌱 ESG Text Analyzer". |  |
| `current_pages/2_ABSA_Rule_Based.py` | `streamlit_page` | Streamlit page for "ABSA Rule-Based Ontology". |  |
| `current_pages/3_ABSA_Classical.py` | `streamlit_page` | Streamlit page for "ABSA Classical ML". |  |
| `current_pages/5_ABSA_Deep_Learning.py` | `streamlit_page` | Streamlit page for "ABSA Deep Learning". |  |
| `current_pages/ABSA_Model_Comparison.py` | `streamlit_page` | Streamlit page for "ABSA Model Comparison: Input Text and Compare All Modules". |  |
| `current_pages/absa_metrics_comparison copy.py` | `streamlit_page` | Streamlit page for "ABSA Mapping Metrics Comparison". | compute_metrics |
| `current_pages/absa_metrics_comparison.py` | `streamlit_page` | Streamlit page for "ABSA Mapping Metrics Comparison". | compute_metrics, map_to_cluster |
| `current_pages/absa_metrics_comparison_mac.py` | `streamlit_page` | Streamlit page for "ABSA Mapping Metrics Comparison". | compute_metrics, map_to_cluster, safe_merge |
| `current_pages/absa_metrics_visualization.py` | `streamlit_page` | Streamlit page for "ABSA Metrics Results Visualization". | load_results, is_nonzero, flatten_report |
| `current_pages/absa_ontology_3_deep_model.py` | `streamlit_page` | Streamlit page for "Deep Model (mBERT) Demo". |  |
| `current_pages/absa_ontology_all.py` | `streamlit_page` | Streamlit page for "ABSA Ontology Modules". |  |
| `current_pages/absa_ontology_all_new_notes.py` | `streamlit_page` | Streamlit page for "ABSA Ontology Modules". |  |
| `current_pages/esg_dashboard_new_01_Aspects_Raw.py` | `streamlit_page` | Streamlit page for "📌 Aspects — Raw Model Output". |  |
| `current_pages/esg_dashboard_new_02_Aspects_Clustered.py` | `streamlit_page` | Streamlit page for "🧩 Aspects — After Manual Clustering". |  |
| `current_pages/esg_dashboard_new_03_Aspect_Comparison.py` | `streamlit_page` | Streamlit page for "🔍 Aspect Mapping — Before vs After". |  |
| `current_pages/esg_dashboard_new_0_Metric_Analysis.py` | `streamlit_page` | Streamlit page for "📊 Metric Analysis — Ground Truth vs Prediction". |  |
| `current_pages/esg_dashboard_new_0_new.py` | `streamlit_page` | Streamlit page for "📊 ESG Parsed Sentence-Level Dashboard". | load_data, extract_json_block, normalize_json, is_valid_esg_object |
| `current_pages/esg_dashboard_new_8_new.py` | `streamlit_page` | Streamlit page for "📊 ESG Parsed Sentence-Level Dashboard". | extract_json_block, normalize_json, is_valid_esg_object, parse_esg_json |
| `current_pages/esg_dashboard_new_Benchmark_Model.py` | `streamlit_page` | Streamlit page for "🌍 ESG & Climate NLP Model Tester". |  |
| `current_pages/esg_dashboard_new_Data Distribution.py` | `streamlit_page` | Streamlit page for "🔍 Aspect & Ontology Visualization Dashboard". | normalize_aspect_category, aspect_label, normalize_sentiment, sentiment_label |
| `current_pages/esg_dashboard_new_Data_New_Distribution.py` | `streamlit_page` | Streamlit page for "ESG Sankey & Filters". | load_dataset, load_ontology, build_alias_map, normalize |
| `current_pages/esg_dashboard_new_Distribution Document.py` | `streamlit_page` | Streamlit page for "🧠 ESG Sentiment & Tone — Document-Level Analysis". | build_alias_map, normalize_sentiment, normalize_tone |
| `current_pages/esg_dashboard_new_Sankey.py` | `streamlit_page` | Streamlit page for "📤 Upload-Based Tone Distribution & Balancer". | build_alias_map, normalize, build_alias_map, normalize |
| `current_pages/esg_dashboard_new_Tone_Distribution.py` | `streamlit_page` | Streamlit page for "📊 Tone Distribution Explorer". | load_json_from_candidates, build_alias_map, normalize, load_master |
| `current_pages/parse_documentation_json.py` | `streamlit_page` | Streamlit page for "Documentation JSON Table Viewer". |  |
| `current_pages/scrambled_absa_mapping_baseline.py` | `streamlit_page` | Streamlit page for "Scrambled ABSA Mapping Baseline". |  |
| `current_pages/scrambled_absa_mapping_baseline_mac.py` | `streamlit_page` | Streamlit page for "Scrambled ABSA Mapping Baseline". |  |
| `current_pages/test_models.py` | `streamlit_page` | Streamlit page for "ESG ABSA Model Tester". |  |
| `current_pages/zz_aspect_clusters.py` | `streamlit_page` | Streamlit page for "🔗 Aspect Clusters Explorer". |  |

### `old_pages` (14 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `old_pages/0_0_ClimateBERT_10_ClimateBERT_Multi_Model.py` | `streamlit_page` | Streamlit page for "ClimateBERT Multi-Model Inference". |  |
| `old_pages/0_0_ClimateBERT_11_ClimateBERT_Parse_JSON.py` | `streamlit_page` | Streamlit page for "ClimateBERT JSON Parser". |  |
| `old_pages/0_ESG_02_ESG_Preprocess.py` | `streamlit_page` | Streamlit page for "ESG Preprocessing". |  |
| `old_pages/0_ESG_03_ESG_Training.py` | `streamlit_page` | Streamlit page for "ESG Preprocessing". |  |
| `old_pages/0_ESG_04_ESG_Evaluation.py` | `streamlit_page` | Streamlit page for "ESG Evaluation". |  |
| `old_pages/0_ESG_05_ESG_XAI.py` | `streamlit_page` | Streamlit page for "ESG Evaluation". |  |
| `old_pages/0_ESG_06_ESG_Compare.py` | `streamlit_page` | Streamlit page for "ESG Evaluation". |  |
| `old_pages/absa_ontology_1_app_state.py` | `streamlit_page` | Streamlit page for "App State Demo". |  |
| `old_pages/absa_ontology_2_classical_ml.py` | `streamlit_page` | Streamlit page for "Classical ML Pipeline Demo". |  |
| `old_pages/absa_ontology_4_explainability.py` | `streamlit_page` | Streamlit page for "Explainability Dashboard". |  |
| `old_pages/absa_ontology_5_hybrid_model.py` | `streamlit_page` | Streamlit page for "Hybrid Model (Hierarchical + MTL) Demo". |  |
| `old_pages/absa_ontology_6_lexicons.py` | `streamlit_page` | Streamlit page for "Lexicons & Ontology Viewer". |  |
| `old_pages/absa_ontology_7_rule_based.py` | `streamlit_page` | Streamlit page for "Rule-Based Model Demo". |  |
| `old_pages/absa_ontology_8_utils.py` | `streamlit_page` | Streamlit page for "Utils Demo". |  |

### `model_download` (6 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `model_download/app.py` | `module` | Application entry point. |  |
| `model_download/models/EnvironmentalBERT-base/llm_processing.py` | `module` | Module related to "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `model_download/pages/1.py` | `streamlit_page` | Streamlit page for "🤖 ESG & Climate Model Downloader". | local_dir_for, is_already_downloaded, folder_size_mb, append_log |
| `model_download/pages/2.py` | `page_script` | No module docstring; utility/support code. |  |
| `model_download/pages/3_inference.py` | `streamlit_page` | Streamlit page for "🔬 Local Model Inference". | looks_like_model_dir, find_all_model_dirs, load_pipeline_safe, load_tokenizer_safe |
| `model_download/pages/4_inference_bulk.py` | `streamlit_page` | Streamlit page for "🔬 Local Model Inference — Bulk". | looks_like_model_dir, find_all_model_dirs, load_pipeline_safe, load_tokenizer_safe |

### `esg_dashboard_new-main` (47 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `esg_dashboard_new-main/dashboard/app.py` | `streamlit_app` | Streamlit app for "📊 ESG Sentence-Level Analytics Dashboard". | page_doc |
| `esg_dashboard_new-main/dashboard/config/model_registry.py` | `config` | No module docstring; utility/support code. |  |
| `esg_dashboard_new-main/dashboard/finbert_model.py` | `module` | Defines classes: MultiTaskFinBERT. | MultiTaskFinBERT |
| `esg_dashboard_new-main/dashboard/model_utils.py` | `module` | Defines functions: torch_available, get_hf_inference_client, make_hf_api_prediction. | torch_available, get_hf_inference_client, make_hf_api_prediction, get_multitask_model_class |
| `esg_dashboard_new-main/dashboard/pages/00_Parsed_ESG_JSON.py` | `streamlit_page` | Streamlit page for "📊 ESG Parsed Sentence-Level Dashboard". | load_data, extract_json_block, normalize_json, is_valid_esg_object |
| `esg_dashboard_new-main/dashboard/pages/00_Streamlit_Page_Workflow.py` | `streamlit_page` | Streamlit page for "Streamlit Page Workflow". | render_desktop_safe_mermaid, render_workflow_cards, available_pages, page_route |
| `esg_dashboard_new-main/dashboard/pages/01_Aspect.py` | `streamlit_page` | Streamlit page for "🧩 Aspect Workspace". | normalize_aspect_level, make_normalized_aspect_summary |
| `esg_dashboard_new-main/dashboard/pages/02_ClimateBERT_Dataset_Processor.py` | `streamlit_page` | Streamlit page for "ClimateBERT Dataset Processor". | get_query_int, slugify, normalize_model_path, default_model_root |
| `esg_dashboard_new-main/dashboard/pages/03_ClimateBERT_Result_Visualizer.py` | `streamlit_page` | Streamlit page for "ClimateBERT Result Visualizer". | slugify, load_parsed_records, load_prediction_files, confidence_bins |
| `esg_dashboard_new-main/dashboard/pages/04_Research_Questions_Visualizer.py` | `streamlit_page` | Streamlit page for "Research Questions Visualizer". | load_artifact_report, render_mermaid, mermaid_download_section, mermaid_label |
| `esg_dashboard_new-main/dashboard/pages/05_Sample_Size_Reasoning.py` | `streamlit_page` | Streamlit page for "Sample Size Reasoning". | render_mermaid, mermaid_download_section, mermaid_label, worst_case_moe |
| `esg_dashboard_new-main/dashboard/pages/06_Chapter_4_Results.py` | `streamlit_page` | Streamlit page for "Chapter 4: Results". |  |
| `esg_dashboard_new-main/dashboard/pages/07_Chapter_5_Discussion.py` | `streamlit_page` | Streamlit page for "Chapter 5: Discussion". |  |
| `esg_dashboard_new-main/dashboard/pages/08_Parsed_ESG_Review.py` | `streamlit_page` | Streamlit page for "📊 ESG Parsed Sentence-Level Dashboard". | load_data, extract_json_block, normalize_json, is_valid_esg_object |
| `esg_dashboard_new-main/dashboard/pages/09_Data_File_Visualizer.py` | `streamlit_page` | Streamlit page for "Data File Visualizer". | load_named_dataset, load_aspect_category_group_mapping, load_aspect_groupings, load_custom_aspect_groupings |
| `esg_dashboard_new-main/dashboard/pages/0_0_Streamlit_Page_Workflow.py` | `streamlit_page` | Streamlit page for "Streamlit Page Workflow". | page_catalog_df, workflow_df |
| `esg_dashboard_new-main/dashboard/pages/0_Metric_Analysis.py` | `streamlit_page` | Streamlit page for "📊 Metric Analysis — Ground Truth vs Prediction". |  |
| `esg_dashboard_new-main/dashboard/pages/10_Chapter_6_Conclusion.py` | `streamlit_page` | Streamlit page for "Chapter 6: Conclusion". |  |
| `esg_dashboard_new-main/dashboard/pages/11_Streamlit_Page_Workflow_Guide.py` | `streamlit_page` | Streamlit page for "Streamlit Page Workflow Guide". |  |
| `esg_dashboard_new-main/dashboard/pages/12_JSON_Ontology_Usage_Map.py` | `streamlit_page` | Streamlit page for "JSON Ontology Usage Map". | page_route, load_json_summary, scan_page_usage, build_json_usage_mermaid |
| `esg_dashboard_new-main/dashboard/pages/6_4_ch4-6.py` | `streamlit_page` | Streamlit page for "Ch4-6 Thesis Overview". | _load_local_data_loader, _find_data_file, _load_ontology, _ontology_alias_map |
| `esg_dashboard_new-main/dashboard/pages/Benchmark_Model.py` | `streamlit_page` | Streamlit page for "🌍 ESG & Climate NLP Model Tester". |  |
| `esg_dashboard_new-main/dashboard/pages/Data Distribution.py` | `streamlit_page` | Streamlit page for "🔍 Aspect & Ontology Visualization Dashboard". | normalize_aspect_category, aspect_label, normalize_sentiment, sentiment_label |
| `esg_dashboard_new-main/dashboard/pages/Data_New_Distribution.py` | `streamlit_page` | Streamlit page for "ESG Sankey & Filters". | load_dataset, load_ontology, build_alias_map, normalize |
| `esg_dashboard_new-main/dashboard/pages/Distribution Document.py` | `streamlit_page` | Streamlit page for "🧠 ESG Sentiment & Tone — Document-Level Analysis". | build_alias_map, normalize_sentiment, normalize_tone |
| `esg_dashboard_new-main/dashboard/pages/Research_Questions_Dashboard.py` | `streamlit_page` | Streamlit page for "Research Questions Dashboard". | rq_rows |
| `esg_dashboard_new-main/dashboard/pages/Sankey.py` | `streamlit_page` | Streamlit page for "📤 Upload-Based Tone Distribution & Balancer". | build_alias_map, normalize, compute_tone_distribution |
| `esg_dashboard_new-main/dashboard/pages/Tone_Distribution.py` | `streamlit_page` | Streamlit page for "📊 Tone Distribution Explorer". | build_alias_map, normalize, load_master, compute_tone_distribution |
| `esg_dashboard_new-main/dashboard/pages/_rq_thesis_content.py` | `streamlit_page` | Defines functions: clean_text, mermaid_label, parse_edge_rqs. | clean_text, mermaid_label, parse_edge_rqs, parse_workflow_mermaid |
| `esg_dashboard_new-main/dashboard/pages/generate_research_question_artifacts.py` | `streamlit_page` | Defines functions: load_font, extract_rq_data, status_frame. | load_font, extract_rq_data, status_frame, wrap_lines |
| `esg_dashboard_new-main/dashboard/services/hf_loader.py` | `service` | Defines functions: load_pipeline. | load_pipeline |
| `esg_dashboard_new-main/dashboard/services/inference.py` | `service` | Defines functions: run_inference. | run_inference |
| `esg_dashboard_new-main/dashboard/ui/results.py` | `ui_component` | Defines functions: render_results. | render_results |
| `esg_dashboard_new-main/dashboard/ui/sidebar.py` | `ui_component` | Defines functions: render_sidebar. | render_sidebar |
| `esg_dashboard_new-main/dashboard/ui/text_input.py` | `ui_component` | Defines functions: render_text_input. | render_text_input |
| `esg_dashboard_new-main/dashboard/utils/__init__.py` | `utility` | No module docstring; utility/support code. |  |
| `esg_dashboard_new-main/dashboard/utils/alignment.py` | `utility` | Defines functions: align_by_sentence. | align_by_sentence |
| `esg_dashboard_new-main/dashboard/utils/aspect_clustering.py` | `utility` | Defines functions: cluster_aspect. | cluster_aspect |
| `esg_dashboard_new-main/dashboard/utils/data_loader.py` | `utility` | Defines functions: resolve_data_path, read_dataset, format_display_value. | resolve_data_path, read_dataset, format_display_value, sorted_unique_values |
| `esg_dashboard_new-main/dashboard/utils/env.py` | `utility` | Defines functions: get_hf_token. | get_hf_token |
| `esg_dashboard_new-main/dashboard/utils/metrics.py` | `utility` | Metrics computation/visualization utility. | normalize_labels, compute_metrics |
| `esg_dashboard_new-main/dashboard/utils/validation.py` | `utility` | Defines functions: validate_columns. | validate_columns |
| `esg_dashboard_new-main/structure_code.py` | `script` | Defines functions: build_tree_html, save_tree_to_markdown. | build_tree_html, save_tree_to_markdown |
| `esg_dashboard_new-main/utils/compare_logic.py` | `utility` | Defines functions: find_missing. | find_missing |
| `esg_dashboard_new-main/utils/data_loader.py` | `utility` | Defines functions: load_csv_uploaded_or_local. | load_csv_uploaded_or_local |
| `esg_dashboard_new-main/utils/load_hf_file.py` | `utility` | Defines functions: load_csv_from_hf. | load_csv_from_hf |
| `esg_dashboard_new-main/utils/visual_utils.py` | `utility` | No module docstring; utility/support code. |  |

### `new_page` (119 files)

| File | Category | Summary | Key Symbols |
|---|---|---|---|
| `new_page/api/climatebert_client.py` | `api_client` | Client wrapper for external model/API calls. | ClimateBERTClient, predict_text |
| `new_page/app.py` | `module` | Application entry point. |  |
| `new_page/code/__init__.py` | `core_module` | No module docstring; utility/support code. |  |
| `new_page/code/action_plan_status.py` | `core_module` | Defines functions: load_csv, load_json, column_series. | load_csv, load_json, column_series, nonempty_count |
| `new_page/code/app_state.py` | `core_module` | Defines classes: AppState. | AppState |
| `new_page/code/classical_ml.py` | `core_module` | core/classical_ml.py Classical ML pipeline for ESG ABSA: - TF-IDF (word + char) featureizer - One-vs-Rest logistic regression for multi-label aspects - Logistic regression (or Dum… | Featureizer, _safe_fit_classifier, coef_table_binary_safe, coef_table_aspect, local_explain |
| `new_page/code/climatebert_background_worker.py` | `core_module` | Defines functions: utc_now, read_json, write_json. | utc_now, read_json, write_json, append_jsonl |
| `new_page/code/data_alignment.py` | `core_module` | Defines functions: load_json, safe_get_absa_df, normalize_col_candidates. | load_json, safe_get_absa_df, normalize_col_candidates, fuzzy_ratio |
| `new_page/code/deep_model.py` | `core_module` | core/deep_model.py Deep learning module (mBERT) for ESG ABSA: - Light-weight training loop for demo / explainability - Extracts attention-based token importances (simple first-lay… | SimpleDLModel, DLDataset, labels_for_dl, run_deep_learning, explain_deep_sentence, plot_attention_plotly |
| `new_page/code/deep_model_v2.py` | `core_module` | core/deep_model.py Deep learning module (mBERT) for ESG ABSA: - Light-weight training loop for demo / explainability - Extracts attention-based token importances (simple first-lay… | SimpleDLModel, DLDataset, labels_for_dl, run_deep_learning, explain_deep_sentence, plot_attention_plotly |
| `new_page/code/explainability.py` | `core_module` | core/explainability.py Cross-model explainability and visualization layer for ESG ABSA. | _get_df_safe, compare_explain, explain_sentence_across_models, plot_consistency_summary |
| `new_page/code/graph_attachment_gallery.py` | `core_module` | Defines functions: load_csv, page_slug, redirect_button. | load_csv, page_slug, redirect_button, show_image |
| `new_page/code/ground_truth_background_worker.py` | `core_module` | Defines functions: utc_now, serialize, read_json. | utc_now, serialize, read_json, write_json |
| `new_page/code/ground_truth_graphs.py` | `core_module` | Defines functions: clean, load_json_or_jsonl, parse_prediction_text. | clean, load_json_or_jsonl, parse_prediction_text, flatten_t1 |
| `new_page/code/hybrid_model.py` | `core_module` | core/hybrid_model.py Hierarchical encoder + MTL Hybrid model (Hybrid++) for ESG ABSA. | HierarchicalEncoder, MTLHybrid, encode_texts_small, make_ontology_vectors, run_hierarchical_hybrid, explain_hybrid_sentence |
| `new_page/code/lexicons.py` | `core_module` | core/lexicons.py Lexical resources and ontology mappings for ESG ABSA Framework. | any_match |
| `new_page/code/llm_background_worker.py` | `core_module` | Defines functions: utc_now, read_json, write_json. | utc_now, read_json, write_json, append_jsonl |
| `new_page/code/rule_based.py` | `core_module` | core/rule_based.py Rule-based RQ1–RQ3 pipeline for ESG ABSA. | collect_aspects, polarity_basic, tone_basic, rq1_sentence_only |
| `new_page/code/semantic_exporter.py` | `core_module` | Defines classes: SemanticBundle; functions: load_csv, load_json, slug. | SemanticBundle, load_csv, load_json, slug, turtle_literal |
| `new_page/code/thesis_chapter_streamlit.py` | `core_module` | Defines functions: clean, load_csv, load_json. | clean, load_csv, load_json, numeric_series |
| `new_page/code/utils.py` | `core_module` | core/utils.py Utility functions and shared data structures for the ESG ABSA framework. | Sentence, detect_lang, parse_document, safe_plot |
| `new_page/code/visualize_tone_climatebert.py` | `core_module` | Generate tone-vs-ClimateBERT visualizations and documentation. | clean_label, normalize_tone, load_esg_records, parse_climatebert_response |
| `new_page/hidden_pages/0_0_0_0_1_master_thesis_prompt.py` | `script` | Module related to "ESG Prompt - Quick Viewer". | list_markdown_files, strip_html_comments, extract_title_from_file, make_latex_skeleton |
| `new_page/hidden_pages/0_0_0_0_2_combined_master_thesis_prompt.py` | `script` | Module related to "Combined ESG Prompt Viewer". | list_markdown_files, strip_html_comments, extract_title_from_file, make_latex_skeleton |
| `new_page/hidden_pages/0_0_0_0_3_combined_master_thesis_prompt_notes.py` | `script` | Module related to "Combined ESG Prompt Viewer". | list_markdown_files, strip_html_comments, extract_title_from_file, make_latex_skeleton |
| `new_page/hidden_pages/0_0_0_1_esg_matching_evaluation.py` | `script` | Module related to "🌍 ESG Matching & Evaluation Dashboard". | safe_load_json, load_jsonl_results, load_mapping, normalize_text |
| `new_page/hidden_pages/0_0_0_2_Bulk_OCR copy.py` | `module` | Module related to "📚 Bulk OCR Pipeline — Mistral OCR". | safe_name, safe_image_name, load_log, save_log |
| `new_page/hidden_pages/0_0_1_climatebert.py` | `module` | Module related to "🌡️ ClimateBERT — Combined (Remote Space & Local HF Model)". | _json_default, append_json_record, parse_response_raw |
| `new_page/hidden_pages/0_0_1_climatebert_combine.py` | `module` | Module related to "🌡️ ClimateBERT — Combined (Remote Space & Local HF Model)". | _json_default, append_json_record, parse_response_raw |
| `new_page/hidden_pages/0_0_1_climatebert_page.py` | `module` | Module related to "EconBERT / ClimateBERT — Model tester". | _load |
| `new_page/hidden_pages/0_0_2.py` | `module` | Defines functions: parse_prediction_str, _is_number_like. | parse_prediction_str, _is_number_like |
| `new_page/hidden_pages/0_0_2_climatebert_dashboard.py` | `module` | Module related to "ClimateBERT — Results Dashboard". | parse_response_raw, apply |
| `new_page/hidden_pages/0_0_3_language_splitter.py` | `module` | Module related to "🌐 Language Splitter — English / Indonesian (Langdetect)". | clean_text, split_paragraphs, split_sentences, detect_lang |
| `new_page/hidden_pages/0_1_output_visualization.py` | `module` | Module related to "📋 ESG Prediction Results Viewer". | load_json, safe_str, extract_label_score, normalise_esg |
| `new_page/hidden_pages/0_2_2_highlight_view.py` | `module` | Module related to "🔍 ESG Detection Highlight Viewer". | load_json, safe_str, normalise_esg, normalise_sentiment |
| `new_page/hidden_pages/0_2_highlight.py` | `module` | Module related to "🔍 ESG Detection Highlight Viewer". | load_json, normalise_df, extract_pred_label, doc_badges |
| `new_page/hidden_pages/0_4_combined_features.py` | `module` | Module related to "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `new_page/hidden_pages/0_5_combined_features.py` | `module` | Module related to "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `new_page/hidden_pages/0_6_combined_features copy.py` | `module` | Module related to "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `new_page/hidden_pages/0_7_combined_features.py` | `module` | Module related to "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `new_page/hidden_pages/0_7_predefined_combined_features.py` | `module` | Module related to "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `new_page/hidden_pages/0_7_visualize_esg_record.py` | `module` | Module related to "📋 ESG Record Viewer". |  |
| `new_page/hidden_pages/0_8_parse_ground_predictions.py` | `module` | Module related to "🔎 Parse T1 (ClimateBERT) Results". | _is_number_like, parse_prediction_str |
| `new_page/hidden_pages/0_8_parse_predictions.py` | `module` | Module related to "🔎 Parse Model Prediction Strings". | _is_number_like, parse_prediction_str |
| `new_page/hidden_pages/0_ocr_multiple_Prediction.py` | `module` | Module related to "🔎 Multi-Model Prediction". |  |
| `new_page/hidden_pages/absa_ontology_all_new_notes.py` | `module` | Defines functions: _serialize, make_json_safe, append_record_absa. | _serialize, make_json_safe, append_record_absa |
| `new_page/hidden_pages/climatebert_demo.py` | `module` | Module related to "🌡️ ClimateBERT — Demo". | connect |
| `new_page/hidden_pages/climatebert_models.py` | `module` | Module related to "🧾 ClimateBERT — Models". | ensure_client |
| `new_page/hidden_pages/company_dataset.py` | `module` | Module related to "📊 Company ESG Dataset". | load_data |
| `new_page/hidden_pages/data_idx.py` | `module` | Module related to "📊 ESG Score Visualization". | load_esg_data, load_html_data |
| `new_page/pages/0_0_Streamlit_Page_Workflow.py` | `streamlit_page` | Streamlit page for "Streamlit Page Workflow". | render_mermaid, page_link, clean_text, mermaid_label |
| `new_page/pages/0_2_JSON_Ontology_Usage_Map.py` | `streamlit_page` | Streamlit page for "JSON Ontology Usage Map". | render_mermaid, safe_load_json, summarize_json, scan_references |
| `new_page/pages/0_3_OCR_Company_Metadata_Labeler.py` | `streamlit_page` | Streamlit page for "OCR Company Metadata Labeler". | now_iso, read_json, write_json, empty_store |
| `new_page/pages/0_4_Sustainable_Framework_API_Reader.py` | `streamlit_page` | Streamlit page for "Sustainable Framework API Reader". | clean, api_url, request_json, cached_catalog |
| `new_page/pages/0_5_Thesis_Systematic_Workflow.py` | `streamlit_page` | Streamlit page for "Thesis Systematic Workflow". | read_workflow, render_mermaid, extract_mermaid, extract_section |
| `new_page/pages/0_9_Tone_ClimateBERT_Visualization.py` | `streamlit_page` | Streamlit page for "Tone vs ClimateBERT Visualization". | clean_label, normalize_tone, short_text, climatebert_label_family |
| `new_page/pages/1_0_Revision_Analytics.py` | `streamlit_page` | Streamlit page for "Revision Analytics Dashboard". | load_csv, metric, bar, grouped_bar |
| `new_page/pages/1_10_Ground_Truth_Run_Coverage.py` | `streamlit_page` | Streamlit page for "Ground Truth Run Coverage". | clean, load_json, load_t1_records, load_t2_records |
| `new_page/pages/1_11_Ground_Truth_Record_Audit.py` | `streamlit_page` | Streamlit page for "Ground Truth Record Audit". | clean, load_json_or_jsonl, parse_prediction_text, flatten_t1 |
| `new_page/pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py` | `streamlit_page` | Streamlit page for "Ground Truth Step-by-Step Visualizer". | clean, load_json, write_json, load_jsonl |
| `new_page/pages/1_13_Semantic_Graph_Exporter.py` | `streamlit_page` | Streamlit page for "Semantic Graph Exporter". |  |
| `new_page/pages/1_1_Ground_Truth_Workbench.py` | `streamlit_page` | Streamlit page for "Ground Truth Workbench". | load_table, cohen_kappa |
| `new_page/pages/1_2_OCR_Quality_Workbench.py` | `streamlit_page` | Streamlit page for "OCR Quality Workbench". | edit_distance, cer, wer, load_samples |
| `new_page/pages/1_3_Ground_Truth_Metrics.py` | `streamlit_page` | Streamlit page for "Ground Truth Metrics". | load_annotations, cohen_kappa, normalize_tone_label, metric_table |
| `new_page/pages/1_4_ClimateBERT_Record_Batch.py` | `streamlit_page` | Streamlit page for "ClimateBERT Record Batch". | load, cohen_kappa_bool, agreement_summary |
| `new_page/pages/1_5_ESG_Flow_Sankey.py` | `streamlit_page` | Streamlit page for "ESG Flow Sankey". | load_data, sankey |
| `new_page/pages/1_6_Ontology_Path_Viewer.py` | `streamlit_page` | Streamlit page for "Ontology Path Viewer". | load_json, load_csv |
| `new_page/pages/1_7_Research_Questions_Dashboard.py` | `streamlit_page` | Streamlit page for "Research Questions Dashboard". | load, pct, render_mermaid |
| `new_page/pages/1_8_Ground_Truth_Output_Visualizer.py` | `streamlit_page` | Streamlit page for "Ground Truth Output Visualizer". | clean_label, load_csv, load_default_ground_truth, normalize_ground_truth |
| `new_page/pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py` | `streamlit_page` | Streamlit page for "Ground Truth Pipeline Output Visualizer". | clean, load_json_or_jsonl, selected_existing_path, parse_prediction_text |
| `new_page/pages/2_0_LLM_Processing_Result_Visualizer.py` | `streamlit_page` | Streamlit page for "LLM Processing Result Visualizer". | clean, load_json, parse_prediction, dict_table |
| `new_page/pages/2_1_LLM_Error_Parse_Audit.py` | `streamlit_page` | Streamlit page for "LLM Error & Parse Audit". | clean, load_json, categorize_error, raw_json_signal |
| `new_page/pages/2_2_LLM_Statement_Page_Verifier.py` | `streamlit_page` | Streamlit page for "LLM Statement Page Verifier". | clean, normalize_text, tokens, load_json |
| `new_page/pages/2_3_LLM_Background_Run_Monitor.py` | `streamlit_page` | Streamlit page for "LLM Background Run Monitor". | utc_now_id, read_json, write_json, append_jsonl |
| `new_page/pages/2_4_PDF_Page_Processing_Audit.py` | `streamlit_page` | Streamlit page for "PDF Page Processing Audit". | clean, read_json, document_pages, parse_target_pages |
| `new_page/pages/2_5_LLM_Model_Catalog_Visualizer.py` | `streamlit_page` | Streamlit page for "LLM Model Catalog". | clean, workbook_path, excel_col_index, xml_text |
| `new_page/pages/3_0_Thesis_Action_Plan.py` | `streamlit_page` | Streamlit page for "{page_title}". | load, utc_now_id, read_json, write_json |
| `new_page/pages/3_1_A4_Per_Model_Background_Run.py` | `streamlit_page` | Streamlit page for "A.4 Per-Model Background Run". | read_pid, is_running, tail_log |
| `new_page/pages/3_2_A4_Per_Model_Dashboard.py` | `streamlit_page` | Streamlit page for "A.4 Per-Model Dashboard". |  |
| `new_page/pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py` | `streamlit_page` | Streamlit page for "Thesis Systematic Workflow Dashboard". | clean, load_csv, load_json, load_jsonl |
| `new_page/pages/5_Thesis_Systematic_Workflow_dashboard.py` | `streamlit_page` | Streamlit page for "Thesis Systematic Workflow Dashboard". | clean, load_csv, load_json, load_jsonl |
| `new_page/pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py` | `streamlit_page` | Streamlit page for "Thesis Draft + Chapters 4-6 Integration Map". | chapter_breakdown_rows, integrated_map_rows, benchmarking_rows, _clean_node_label |
| `new_page/pages/6_1_Chapter_4_Implementation_Results.py` | `streamlit_page` | Streamlit page for "Chapter 4 - Implementation and Results". |  |
| `new_page/pages/6_2_Chapter_5_Discussion.py` | `streamlit_page` | Streamlit page for "Chapter 5 - Discussion". |  |
| `new_page/pages/6_3_Chapter_6_Conclusion.py` | `streamlit_page` | Streamlit page for "Chapter 6 - Conclusion". |  |
| `new_page/pages/6_4_ch4-6.py` | `streamlit_page` | Streamlit page for "Ch4-6 Structure Benchmarks and Graph Attachments". | show_image, read_docx_paragraphs, media_count, chart_font |
| `new_page/pages/Bulk_OCR.py` | `streamlit_page` | Streamlit page for "📚 Bulk OCR Pipeline — Mistral OCR". | safe_name, safe_image_name, load_log, save_log |
| `new_page/pages/ground_truth.py` | `streamlit_page` | Streamlit page for "🌿 ESG Pipeline (Resumable)". | JSONLWriter, serialize, has_usable_t1_label, is_complete_t1_record, load_processed_t1 |
| `new_page/pages/llm_processing.py` | `streamlit_page` | Streamlit page for "🌿 ESG Combined Pipeline". | _ensure_tempdir, _serialize, make_json_safe, append_record |
| `new_page/pages_non_ocr/0_0_1_multiple_Prediction.py` | `streamlit_page` | Streamlit page for "🔎 Multi-Model Prediction". |  |
| `new_page/pages_non_ocr/absa_ontology_all_new_notes.py` | `streamlit_page` | Streamlit page for "ABSA Ontology Modules". |  |
| `new_page/pages_non_ocr/llm_setup.py` | `streamlit_page` | Streamlit page for "ESG Structured Extraction (OpenRouter)". | _load_prompt_template, _extract_first_json, _requests_session_with_retries, parse_json_from_model |
| `new_page/pages_non_ocr/test_llm.py` | `streamlit_page` | Streamlit page for "OpenRouter LLM Chat". | init_store, save_message, get_history, clear_store |
| `new_page/past_pages/0_3_testing_combined_features.py` | `module` | Module related to "🌿 ESG Pipeline (T1 + T2 only)". | serialize, append_json |
| `new_page/past_pages/hallucination.py` | `module` | Module related to "ESG Highlights viewer". | safe_load_json, normalize_dataset, get_texts_from_record, render_highlight_html |
| `new_page/past_pages/llm_setup.py` | `module` | Module related to "🌿 ESG Structured Extraction". | list_prompt_files, load_prompt_file, apply_prompt, _requests_session |
| `new_page/past_pages/llm_setup_with_context.py` | `module` | Module related to "🌿 ESG Structured Extraction". | estimate_tokens, estimate_cost, format_cost, ctx_utilisation_color |
| `new_page/past_pages/streamlit_app.py` | `module` | Module related to "ESG Alignment & Evaluation (interactive)". | load_settings, save_settings |
| `new_page/past_pages/visualizer.py` | `module` | Module related to "ESG Full-text visualizer". | safe_load_json, normalize_dataset, map_esg_tag, extract_segments_from_record |
| `new_page/scripts/compare_runs.py` | `ops_script` | Defines functions: load_manifest, index_files, resolve_manifest. | load_manifest, index_files, resolve_manifest, main |
| `new_page/scripts/generate_manifest.py` | `ops_script` | Defines functions: now_utc_iso, git_commit, sha256_file. | now_utc_iso, git_commit, sha256_file, collect_files |
| `new_page/scripts/start_run.py` | `ops_script` | Defines functions: git_commit, main. | git_commit, main |
| `new_page/social_network_analysis/app.py` | `streamlit_app` | Streamlit app for "ESG Report Network Analysis - Adapted Framework". | _extract_year, _split_sections, _tokens, _entities_for_section |
| `new_page/social_network_analysis/pages/1_Conceptual_Mapping.py` | `page_script` | No module docstring; utility/support code. |  |
| `new_page/social_network_analysis/pages/2_Part_1_Graph_Construction_and_Analysis.py` | `page_script` | No module docstring; utility/support code. |  |
| `new_page/social_network_analysis/pages/3_Part_2_Community_and_Correlation.py` | `page_script` | No module docstring; utility/support code. |  |
| `new_page/social_network_analysis/pages/4_Part_3_Simulation.py` | `page_script` | No module docstring; utility/support code. |  |
| `new_page/social_network_analysis/pages/5_Part_4_Literature_Review.py` | `page_script` | No module docstring; utility/support code. |  |
| `new_page/social_network_analysis/task_data.py` | `module` | Task definitions for ESG graph network Streamlit app. | get_tasks_for_phase |
| `new_page/social_network_analysis/ui.py` | `module` | Defines functions: render_task, render_phase_page, render_research_frame. | render_task, render_phase_page, render_research_frame |
| `new_page/summarization/app.py` | `streamlit_app` | Streamlit app for "ESG ABSA Summarization Workspace". | _read_csv, _load_sources_config, load_datasets, metric_int |
| `new_page/tools/build_coherent_thesis_docx.py` | `ops_script` | Defines functions: set_cell_shading, set_cell_text, add_table. | set_cell_shading, set_cell_text, add_table, add_bullets |
| `new_page/tools/climatebert_a4/generate_a4_per_model.py` | `ops_script` | Defines functions: slugify, crosstab_for_group, main. | slugify, crosstab_for_group, main |
| `new_page/tools/generate_chapter_resolution_artifacts.py` | `ops_script` | Defines functions: read_csv, write_csv, pct. | read_csv, write_csv, pct, float_value |
| `new_page/tools/update_ch4_6_docx_graphs.py` | `ops_script` | Defines functions: load_csv, font, wrap_text. | load_csv, font, wrap_text, draw_bar_chart |
| `new_page/topic_modelling/app.py` | `streamlit_app` | Streamlit app for "ESG Sustainability Report Analysis - Complete Task Framework". | _tokenize, _extract_year, _dataset_signature, _get_scan_state_key |
| `new_page/topic_modelling/pages/1_Phase_1_Data_Preparation.py` | `page_script` | No module docstring; utility/support code. |  |
| `new_page/topic_modelling/task_data.py` | `module` | Task definitions and UI helpers for ESG sustainability report task app. | get_tasks_for_phase |
| `new_page/topic_modelling/ui.py` | `module` | Shared Streamlit rendering helpers. | render_task, render_phase_page, render_research_frame |

## Notes and Maintenance

- This documentation is generated from static code inspection; runtime behavior still depends on local data files, `.env` values, and model/API availability.
- If you add/remove files, regenerate this document to keep the inventory complete.
- Regenerate by rerunning the inventory-generation command/script you use for this repo so the file list and summaries stay current.
