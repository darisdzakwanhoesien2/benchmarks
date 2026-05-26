# High-Level Pseudocode Documentation

This document provides per-file high-level pseudocode for `app.py` and all Python files under `pages/`, formatted with LaTeX algorithm blocks.

## `app.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `app.py`}
\Output{Rendered UI state and side effects produced by `app.py`}
1. Load required modules and utilities\;
2. Parse inputs and configuration\;
3. Execute application logic\;
4. Render or persist outputs\;
\caption{High-level pseudocode for `app.py`}
\label{alg:app_py}
\end{algorithm}

## `pages/0_0_Streamlit_Page_Workflow.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/0_0_Streamlit_Page_Workflow.py`}
\Output{Rendered UI state and side effects produced by `pages/0_0_Streamlit_Page_Workflow.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `PAGES_DIR`\;
6. Set runtime variable `DOCS_DIR`\;
7. Define helper `render_mermaid(...)`\;
8. Define helper `page_link(...)`\;
9. Define helper `clean_text(...)`\;
\caption{High-level pseudocode for `pages/0_0_Streamlit_Page_Workflow.py`}
\label{alg:pages_0_0_Streamlit_Page_Workflow_py}
\end{algorithm}

## `pages/0_2_JSON_Ontology_Usage_Map.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/0_2_JSON_Ontology_Usage_Map.py`}
\Output{Rendered UI state and side effects produced by `pages/0_2_JSON_Ontology_Usage_Map.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Initialize `BENCHMARKS_ROOT` using `Path(...)`\;
4. Set runtime variable `NEW_PAGE_ROOT`\;
5. Set runtime variable `NEW_PAGE_PAGES`\;
6. Set runtime variable `DOCS_DIR`\;
7. Set runtime variable `JSON_REGISTRY`\;
8. Define helper `render_mermaid(...)`\;
9. Define helper `safe_load_json(...)`\;
\caption{High-level pseudocode for `pages/0_2_JSON_Ontology_Usage_Map.py`}
\label{alg:pages_0_2_JSON_Ontology_Usage_Map_py}
\end{algorithm}

## `pages/0_3_OCR_Company_Metadata_Labeler.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/0_3_OCR_Company_Metadata_Labeler.py`}
\Output{Rendered UI state and side effects produced by `pages/0_3_OCR_Company_Metadata_Labeler.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `DATASET_DIR`\;
5. Set runtime variable `LABEL_PATH`\;
6. Set runtime variable `METADATA_FIELDS`\;
7. Set runtime variable `DEFAULT_COMPANY_EXAMPLES`\;
8. Define helper `now_iso(...)`\;
9. Define helper `read_json(...)`\;
\caption{High-level pseudocode for `pages/0_3_OCR_Company_Metadata_Labeler.py`}
\label{alg:pages_0_3_OCR_Company_Metadata_Labeler_py}
\end{algorithm}

## `pages/0_4_Sustainable_Framework_API_Reader.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/0_4_Sustainable_Framework_API_Reader.py`}
\Output{Rendered UI state and side effects produced by `pages/0_4_Sustainable_Framework_API_Reader.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `DEFAULT_BASE_URL`\;
4. Set runtime variable `DEFAULT_TIMEOUT`\;
5. Set runtime variable `ROOT`\;
6. Set runtime variable `EXPORT_DIR`\;
7. Define helper `clean(...)`\;
8. Define helper `api_url(...)`\;
9. Define helper `request_json(...)`\;
\caption{High-level pseudocode for `pages/0_4_Sustainable_Framework_API_Reader.py`}
\label{alg:pages_0_4_Sustainable_Framework_API_Reader_py}
\end{algorithm}

## `pages/0_5_Thesis_Systematic_Workflow.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/0_5_Thesis_Systematic_Workflow.py`}
\Output{Rendered UI state and side effects produced by `pages/0_5_Thesis_Systematic_Workflow.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `WORKFLOW_PATH`\;
5. Set runtime variable `DASHBOARD_OUTPUT_DIR`\;
6. Set runtime variable `DASHBOARD_REPORT_PATH`\;
7. Set runtime variable `DASHBOARD_SECTIONS_PATH`\;
8. Set runtime variable `DASHBOARD_METRICS_PATH`\;
9. Set runtime variable `DASHBOARD_IMAGE_MANIFEST_PATH`\;
\caption{High-level pseudocode for `pages/0_5_Thesis_Systematic_Workflow.py`}
\label{alg:pages_0_5_Thesis_Systematic_Workflow_py}
\end{algorithm}

## `pages/0_9_Tone_ClimateBERT_Visualization.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/0_9_Tone_ClimateBERT_Visualization.py`}
\Output{Rendered UI state and side effects produced by `pages/0_9_Tone_ClimateBERT_Visualization.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `ESG_RECORDS`\;
7. Set runtime variable `CLIMATEBERT_RESULTS`\;
8. Set runtime variable `DOC_PATH`\;
9. Set runtime variable `TONE_ORDER`\;
\caption{High-level pseudocode for `pages/0_9_Tone_ClimateBERT_Visualization.py`}
\label{alg:pages_0_9_Tone_ClimateBERT_Visualization_py}
\end{algorithm}

## `pages/1_0_Revision_Analytics.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_0_Revision_Analytics.py`}
\Output{Rendered UI state and side effects produced by `pages/1_0_Revision_Analytics.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `ARTIFACTS`\;
6. Define helper `load_csv(...)`\;
7. Define helper `metric(...)`\;
8. Define helper `bar(...)`\;
9. Define helper `grouped_bar(...)`\;
\caption{High-level pseudocode for `pages/1_0_Revision_Analytics.py`}
\label{alg:pages_1_0_Revision_Analytics_py}
\end{algorithm}

## `pages/1_10_Ground_Truth_Run_Coverage.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_10_Ground_Truth_Run_Coverage.py`}
\Output{Rendered UI state and side effects produced by `pages/1_10_Ground_Truth_Run_Coverage.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `DEFAULT_SOURCE_PATH`\;
7. Set runtime variable `DEFAULT_T1_JSONL`\;
8. Set runtime variable `DEFAULT_T2_JSONL`\;
9. Define helper `clean(...)`\;
\caption{High-level pseudocode for `pages/1_10_Ground_Truth_Run_Coverage.py`}
\label{alg:pages_1_10_Ground_Truth_Run_Coverage_py}
\end{algorithm}

## `pages/1_11_Ground_Truth_Record_Audit.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_11_Ground_Truth_Record_Audit.py`}
\Output{Rendered UI state and side effects produced by `pages/1_11_Ground_Truth_Record_Audit.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `DEFAULT_T1_JSONL`\;
7. Set runtime variable `DEFAULT_T2_JSONL`\;
8. Define helper `clean(...)`\;
9. Define helper `load_json_or_jsonl(...)`\;
\caption{High-level pseudocode for `pages/1_11_Ground_Truth_Record_Audit.py`}
\label{alg:pages_1_11_Ground_Truth_Record_Audit_py}
\end{algorithm}

## `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`}
\Output{Rendered UI state and side effects produced by `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `DEFAULT_SOURCE`\;
7. Set runtime variable `DEFAULT_T1`\;
8. Set runtime variable `DEFAULT_T2`\;
9. Set runtime variable `GT_JOBS_DIR`\;
\caption{High-level pseudocode for `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`}
\label{alg:pages_1_12_Ground_Truth_Step_By_Step_Visualizer_py}
\end{algorithm}

## `pages/1_13_Semantic_Graph_Exporter.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_13_Semantic_Graph_Exporter.py`}
\Output{Rendered UI state and side effects produced by `pages/1_13_Semantic_Graph_Exporter.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ROOT`\;
3. Execute `sys.path.insert(...)`\;
4. Render Streamlit UI via `set_page_config(...)`\;
5. Render Streamlit UI via `title(...)`\;
6. Render Streamlit UI via `caption(...)`\;
7. Initialize `bundle` using `load_semantic_bundle(...)`\;
8. Initialize `records` using `canonical_records(...)`\;
9. Initialize `onto` using `ontology_rows(...)`\;
\caption{High-level pseudocode for `pages/1_13_Semantic_Graph_Exporter.py`}
\label{alg:pages_1_13_Semantic_Graph_Exporter_py}
\end{algorithm}

## `pages/1_1_Ground_Truth_Workbench.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_1_Ground_Truth_Workbench.py`}
\Output{Rendered UI state and side effects produced by `pages/1_1_Ground_Truth_Workbench.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `ARTIFACTS`\;
6. Set runtime variable `SEED_PATH`\;
7. Set runtime variable `ANNOTATION_PATH`\;
8. Set runtime variable `SILVER_PATH`\;
9. Set runtime variable `TONE_OPTIONS`\;
\caption{High-level pseudocode for `pages/1_1_Ground_Truth_Workbench.py`}
\label{alg:pages_1_1_Ground_Truth_Workbench_py}
\end{algorithm}

## `pages/1_2_OCR_Quality_Workbench.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_2_OCR_Quality_Workbench.py`}
\Output{Rendered UI state and side effects produced by `pages/1_2_OCR_Quality_Workbench.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `ARTIFACTS`\;
5. Set runtime variable `SAMPLES_PATH`\;
6. Set runtime variable `SUMMARY_PATH`\;
7. Define helper `edit_distance(...)`\;
8. Define helper `cer(...)`\;
9. Define helper `wer(...)`\;
\caption{High-level pseudocode for `pages/1_2_OCR_Quality_Workbench.py`}
\label{alg:pages_1_2_OCR_Quality_Workbench_py}
\end{algorithm}

## `pages/1_3_Ground_Truth_Metrics.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_3_Ground_Truth_Metrics.py`}
\Output{Rendered UI state and side effects produced by `pages/1_3_Ground_Truth_Metrics.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `ARTIFACTS`\;
6. Set runtime variable `ANNOTATION_PATH`\;
7. Set runtime variable `SEED_PATH`\;
8. Set runtime variable `SILVER_PATH`\;
9. Define helper `load_annotations(...)`\;
\caption{High-level pseudocode for `pages/1_3_Ground_Truth_Metrics.py`}
\label{alg:pages_1_3_Ground_Truth_Metrics_py}
\end{algorithm}

## `pages/1_4_ClimateBERT_Record_Batch.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_4_ClimateBERT_Record_Batch.py`}
\Output{Rendered UI state and side effects produced by `pages/1_4_ClimateBERT_Record_Batch.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `ARTIFACTS`\;
5. Set runtime variable `SILVER_PATH`\;
6. Set runtime variable `PROXY_PATH`\;
7. Set runtime variable `IMPORTED_PATH`\;
8. Define helper `load(...)`\;
9. Define helper `cohen_kappa_bool(...)`\;
\caption{High-level pseudocode for `pages/1_4_ClimateBERT_Record_Batch.py`}
\label{alg:pages_1_4_ClimateBERT_Record_Batch_py}
\end{algorithm}

## `pages/1_5_ESG_Flow_Sankey.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_5_ESG_Flow_Sankey.py`}
\Output{Rendered UI state and side effects produced by `pages/1_5_ESG_Flow_Sankey.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `SILVER_PATH`\;
5. Define helper `load_data(...)`\;
6. Define helper `sankey(...)`\;
7. Render Streamlit UI via `title(...)`\;
8. Render Streamlit UI via `caption(...)`\;
9. Initialize `df` using `load_data(...)`\;
\caption{High-level pseudocode for `pages/1_5_ESG_Flow_Sankey.py`}
\label{alg:pages_1_5_ESG_Flow_Sankey_py}
\end{algorithm}

## `pages/1_6_Ontology_Path_Viewer.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_6_Ontology_Path_Viewer.py`}
\Output{Rendered UI state and side effects produced by `pages/1_6_Ontology_Path_Viewer.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `ARTIFACTS`\;
5. Set runtime variable `ONTOLOGY_PATH`\;
6. Set runtime variable `COVERAGE_PATH`\;
7. Set runtime variable `SILVER_PATH`\;
8. Define helper `load_json(...)`\;
9. Define helper `load_csv(...)`\;
\caption{High-level pseudocode for `pages/1_6_Ontology_Path_Viewer.py`}
\label{alg:pages_1_6_Ontology_Path_Viewer_py}
\end{algorithm}

## `pages/1_7_Research_Questions_Dashboard.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_7_Research_Questions_Dashboard.py`}
\Output{Rendered UI state and side effects produced by `pages/1_7_Research_Questions_Dashboard.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `ARTIFACTS`\;
6. Define helper `load(...)`\;
7. Define helper `pct(...)`\;
8. Define helper `render_mermaid(...)`\;
9. Initialize `silver` using `load(...)`\;
\caption{High-level pseudocode for `pages/1_7_Research_Questions_Dashboard.py`}
\label{alg:pages_1_7_Research_Questions_Dashboard_py}
\end{algorithm}

## `pages/1_8_Ground_Truth_Output_Visualizer.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_8_Ground_Truth_Output_Visualizer.py`}
\Output{Rendered UI state and side effects produced by `pages/1_8_Ground_Truth_Output_Visualizer.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `ARTIFACTS`\;
6. Set runtime variable `ANNOTATION_PATH`\;
7. Set runtime variable `SEED_PATH`\;
8. Set runtime variable `SILVER_PATH`\;
9. Set runtime variable `RAW_GROUND_TRUTH_PATH`\;
\caption{High-level pseudocode for `pages/1_8_Ground_Truth_Output_Visualizer.py`}
\label{alg:pages_1_8_Ground_Truth_Output_Visualizer_py}
\end{algorithm}

## `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`}
\Output{Rendered UI state and side effects produced by `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `DEFAULT_T1_JSONL`\;
7. Set runtime variable `DEFAULT_T1_JSON`\;
8. Set runtime variable `DEFAULT_T2_JSONL`\;
9. Set runtime variable `DEFAULT_T2_JSON`\;
\caption{High-level pseudocode for `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`}
\label{alg:pages_1_9_Ground_Truth_Pipeline_Output_Visualizer_py}
\end{algorithm}

## `pages/2_0_LLM_Processing_Result_Visualizer.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/2_0_LLM_Processing_Result_Visualizer.py`}
\Output{Rendered UI state and side effects produced by `pages/2_0_LLM_Processing_Result_Visualizer.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `T1_PATH`\;
7. Set runtime variable `T2_PATH`\;
8. Set runtime variable `T3_PATH`\;
9. Define helper `clean(...)`\;
\caption{High-level pseudocode for `pages/2_0_LLM_Processing_Result_Visualizer.py`}
\label{alg:pages_2_0_LLM_Processing_Result_Visualizer_py}
\end{algorithm}

## `pages/2_1_LLM_Error_Parse_Audit.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/2_1_LLM_Error_Parse_Audit.py`}
\Output{Rendered UI state and side effects produced by `pages/2_1_LLM_Error_Parse_Audit.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS_DIR`\;
5. Set runtime variable `T3_PATH`\;
6. Define helper `clean(...)`\;
7. Define helper `load_json(...)`\;
8. Define helper `categorize_error(...)`\;
9. Define helper `raw_json_signal(...)`\;
\caption{High-level pseudocode for `pages/2_1_LLM_Error_Parse_Audit.py`}
\label{alg:pages_2_1_LLM_Error_Parse_Audit_py}
\end{algorithm}

## `pages/2_2_LLM_Statement_Page_Verifier.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/2_2_LLM_Statement_Page_Verifier.py`}
\Output{Rendered UI state and side effects produced by `pages/2_2_LLM_Statement_Page_Verifier.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS_DIR`\;
5. Set runtime variable `VIS_DIR`\;
6. Set runtime variable `DATASET_DIR`\;
7. Set runtime variable `T3_PATH`\;
8. Set runtime variable `TONE_FLAT_PATH`\;
9. Set runtime variable `COMPILED_VERIFICATION_PATH`\;
\caption{High-level pseudocode for `pages/2_2_LLM_Statement_Page_Verifier.py`}
\label{alg:pages_2_2_LLM_Statement_Page_Verifier_py}
\end{algorithm}

## `pages/2_3_LLM_Background_Run_Monitor.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/2_3_LLM_Background_Run_Monitor.py`}
\Output{Rendered UI state and side effects produced by `pages/2_3_LLM_Background_Run_Monitor.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `DATASET_DIR`\;
5. Set runtime variable `PROMPT_DIR`\;
6. Set runtime variable `RESULTS_DIR`\;
7. Set runtime variable `JOBS_DIR`\;
8. Set runtime variable `WORKER_PATH`\;
9. Set runtime variable `LLM_PROCESS_DIR`\;
\caption{High-level pseudocode for `pages/2_3_LLM_Background_Run_Monitor.py`}
\label{alg:pages_2_3_LLM_Background_Run_Monitor_py}
\end{algorithm}

## `pages/2_4_PDF_Page_Processing_Audit.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/2_4_PDF_Page_Processing_Audit.py`}
\Output{Rendered UI state and side effects produced by `pages/2_4_PDF_Page_Processing_Audit.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `DATASET_DIR`\;
5. Set runtime variable `RESULTS_DIR`\;
6. Set runtime variable `JOBS_DIR`\;
7. Set runtime variable `T3_PATH`\;
8. Define helper `clean(...)`\;
9. Define helper `read_json(...)`\;
\caption{High-level pseudocode for `pages/2_4_PDF_Page_Processing_Audit.py`}
\label{alg:pages_2_4_PDF_Page_Processing_Audit_py}
\end{algorithm}

## `pages/2_5_LLM_Model_Catalog_Visualizer.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/2_5_LLM_Model_Catalog_Visualizer.py`}
\Output{Rendered UI state and side effects produced by `pages/2_5_LLM_Model_Catalog_Visualizer.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `WORKBOOK_CANDIDATES`\;
5. Set runtime variable `KNOWN_HEADER_WORDS`\;
6. Define helper `clean(...)`\;
7. Define helper `workbook_path(...)`\;
8. Define helper `excel_col_index(...)`\;
9. Define helper `xml_text(...)`\;
\caption{High-level pseudocode for `pages/2_5_LLM_Model_Catalog_Visualizer.py`}
\label{alg:pages_2_5_LLM_Model_Catalog_Visualizer_py}
\end{algorithm}

## `pages/3_0_Thesis_Action_Plan.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/3_0_Thesis_Action_Plan.py`}
\Output{Rendered UI state and side effects produced by `pages/3_0_Thesis_Action_Plan.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Execute `sys.path.insert(...)`\;
5. Set runtime variable `PAGES_DIR`\;
6. Set runtime variable `RESULTS`\;
7. Set runtime variable `VIS`\;
8. Set runtime variable `ARTIFACTS`\;
9. Set runtime variable `REVISION`\;
\caption{High-level pseudocode for `pages/3_0_Thesis_Action_Plan.py`}
\label{alg:pages_3_0_Thesis_Action_Plan_py}
\end{algorithm}

## `pages/3_1_A4_Per_Model_Background_Run.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/3_1_A4_Per_Model_Background_Run.py`}
\Output{Rendered UI state and side effects produced by `pages/3_1_A4_Per_Model_Background_Run.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `SCRIPT_PATH`\;
5. Set runtime variable `LOG_DIR`\;
6. Set runtime variable `LOG_PATH`\;
7. Set runtime variable `PID_PATH`\;
8. Render Streamlit UI via `title(...)`\;
9. Render Streamlit UI via `caption(...)`\;
\caption{High-level pseudocode for `pages/3_1_A4_Per_Model_Background_Run.py`}
\label{alg:pages_3_1_A4_Per_Model_Background_Run_py}
\end{algorithm}

## `pages/3_2_A4_Per_Model_Dashboard.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/3_2_A4_Per_Model_Dashboard.py`}
\Output{Rendered UI state and side effects produced by `pages/3_2_A4_Per_Model_Dashboard.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `VIS`\;
5. Set runtime variable `MANIFEST_PATH`\;
6. Render Streamlit UI via `title(...)`\;
7. Render Streamlit UI via `caption(...)`\;
8. Branch on `not MANIFEST_PATH.exists()`\;
9. Initialize `manifest` using `pd.read_csv.fillna(...)`\;
\caption{High-level pseudocode for `pages/3_2_A4_Per_Model_Dashboard.py`}
\label{alg:pages_3_2_A4_Per_Model_Dashboard_py}
\end{algorithm}

## `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`}
\Output{Rendered UI state and side effects produced by `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS`\;
5. Set runtime variable `VIS`\;
6. Set runtime variable `REVISION`\;
7. Set runtime variable `WORKFLOW_PATH`\;
8. Set runtime variable `OUTPUT_DIR`\;
9. Define helper `clean(...)`\;
\caption{High-level pseudocode for `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`}
\label{alg:pages_5_1_Thesis_Systematic_Workflow_dashboard_generated_py}
\end{algorithm}

## `pages/5_Thesis_Systematic_Workflow_dashboard.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/5_Thesis_Systematic_Workflow_dashboard.py`}
\Output{Rendered UI state and side effects produced by `pages/5_Thesis_Systematic_Workflow_dashboard.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS`\;
5. Set runtime variable `VIS`\;
6. Set runtime variable `REVISION`\;
7. Set runtime variable `WORKFLOW_PATH`\;
8. Set runtime variable `OUTPUT_DIR`\;
9. Define helper `clean(...)`\;
\caption{High-level pseudocode for `pages/5_Thesis_Systematic_Workflow_dashboard.py`}
\label{alg:pages_5_Thesis_Systematic_Workflow_dashboard_py}
\end{algorithm}

## `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`}
\Output{Rendered UI state and side effects produced by `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ROOT`\;
3. Execute `sys.path.insert(...)`\;
4. Set runtime variable `NARRATIVE_PATH`\;
5. Set runtime variable `W_NS`\;
6. Render Streamlit UI via `set_page_config(...)`\;
7. Initialize `bundle` using `data_bundle(...)`\;
8. Initialize `metrics` using `evidence_metrics(...)`\;
9. Define helper `chapter_breakdown_rows(...)`\;
\caption{High-level pseudocode for `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`}
\label{alg:pages_6_0_Thesis_Draft_Chapter_Integration_Mermaid_py}
\end{algorithm}

## `pages/6_1_Chapter_4_Implementation_Results.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/6_1_Chapter_4_Implementation_Results.py`}
\Output{Rendered UI state and side effects produced by `pages/6_1_Chapter_4_Implementation_Results.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ROOT`\;
3. Execute `sys.path.insert(...)`\;
4. Render Streamlit UI via `set_page_config(...)`\;
5. Initialize `bundle` using `data_bundle(...)`\;
6. Render Streamlit UI via `title(...)`\;
7. Render Streamlit UI via `caption(...)`\;
8. Execute `metric_row(...)`\;
9. Set runtime variables\;
\caption{High-level pseudocode for `pages/6_1_Chapter_4_Implementation_Results.py`}
\label{alg:pages_6_1_Chapter_4_Implementation_Results_py}
\end{algorithm}

## `pages/6_2_Chapter_5_Discussion.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/6_2_Chapter_5_Discussion.py`}
\Output{Rendered UI state and side effects produced by `pages/6_2_Chapter_5_Discussion.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ROOT`\;
3. Execute `sys.path.insert(...)`\;
4. Render Streamlit UI via `set_page_config(...)`\;
5. Initialize `bundle` using `data_bundle(...)`\;
6. Render Streamlit UI via `title(...)`\;
7. Render Streamlit UI via `caption(...)`\;
8. Execute `metric_row(...)`\;
9. Set runtime variables\;
\caption{High-level pseudocode for `pages/6_2_Chapter_5_Discussion.py`}
\label{alg:pages_6_2_Chapter_5_Discussion_py}
\end{algorithm}

## `pages/6_3_Chapter_6_Conclusion.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/6_3_Chapter_6_Conclusion.py`}
\Output{Rendered UI state and side effects produced by `pages/6_3_Chapter_6_Conclusion.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ROOT`\;
3. Execute `sys.path.insert(...)`\;
4. Render Streamlit UI via `set_page_config(...)`\;
5. Initialize `bundle` using `data_bundle(...)`\;
6. Render Streamlit UI via `title(...)`\;
7. Render Streamlit UI via `caption(...)`\;
8. Execute `metric_row(...)`\;
9. Set runtime variables\;
\caption{High-level pseudocode for `pages/6_3_Chapter_6_Conclusion.py`}
\label{alg:pages_6_3_Chapter_6_Conclusion_py}
\end{algorithm}

## `pages/6_4_ch4-6.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/6_4_ch4-6.py`}
\Output{Rendered UI state and side effects produced by `pages/6_4_ch4-6.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ROOT`\;
3. Set runtime variable `BENCHMARKS_ROOT`\;
4. Set runtime variable `SOURCE_DOCX`\;
5. Set runtime variable `UPDATED_DOCX`\;
6. Set runtime variable `GRAPH_DIR`\;
7. Set runtime variable `VIS`\;
8. Set runtime variable `TOOLS`\;
9. Set runtime variable `W_NS`\;
\caption{High-level pseudocode for `pages/6_4_ch4-6.py`}
\label{alg:pages_6_4_ch4-6_py}
\end{algorithm}

## `pages/Bulk_OCR.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/Bulk_OCR.py`}
\Output{Rendered UI state and side effects produced by `pages/Bulk_OCR.py`}
1. Load required modules and utilities\;
2. Set runtime variable `BASE_DIR`\;
3. Execute `load_dotenv(...)`\;
4. Initialize `API_KEY` using `os.getenv(...)`\;
5. Branch on `not API_KEY`\;
6. Set runtime variable `BASE`\;
7. Set runtime variable `HEADERS`\;
8. Set runtime variable `TMP_DIR`\;
9. Set runtime variable `OUT_DIR`\;
\caption{High-level pseudocode for `pages/Bulk_OCR.py`}
\label{alg:pages_Bulk_OCR_py}
\end{algorithm}

## `pages/annotator/app.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/annotator/app.py`}
\Output{Rendered UI state and side effects produced by `pages/annotator/app.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS_DIR`\;
5. Set runtime variable `REVISION_DIR`\;
6. Set runtime variable `DEFAULT_DATASETS`\;
7. Set runtime variable `EDITABLE_COLUMNS`\;
8. Set runtime variable `DISPLAY_PRIORITY`\;
9. Define helper `read_csv(...)`\;
\caption{High-level pseudocode for `pages/annotator/app.py`}
\label{alg:pages_annotator_app_py}
\end{algorithm}

## `pages/backend/app.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/backend/app.py`}
\Output{Rendered UI state and side effects produced by `pages/backend/app.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS_DIR`\;
5. Set runtime variable `LOGS_DIR`\;
6. Set runtime variable `BG_DIR`\;
7. Define helper `load_json(...)`\;
8. Define helper `summarize_jobs(...)`\;
9. Define helper `read_events(...)`\;
\caption{High-level pseudocode for `pages/backend/app.py`}
\label{alg:pages_backend_app_py}
\end{algorithm}

## `pages/ground_truth.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/ground_truth.py`}
\Output{Rendered UI state and side effects produced by `pages/ground_truth.py`}
1. Load required modules and utilities\;
2. Set runtime variable `ClimateBERTClient`\;
3. Set runtime variable `_climatebert_error`\;
4. Execute guarded logic with exception handling\;
5. Set runtime variable `ROOT`\;
6. Execute `sys.path.insert(...)`\;
7. Set runtime variable `DATA_PATH`\;
8. Set runtime variable `RESULTS_DIR`\;
9. Execute `RESULTS_DIR.mkdir(...)`\;
\caption{High-level pseudocode for `pages/ground_truth.py`}
\label{alg:pages_ground_truth_py}
\end{algorithm}

## `pages/llm_processing.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/llm_processing.py`}
\Output{Rendered UI state and side effects produced by `pages/llm_processing.py`}
1. Load required modules and utilities\;
2. Set runtime variable `_LOCAL_TMP`\;
3. Execute `_LOCAL_TMP.mkdir(...)`\;
4. Define helper `_ensure_tempdir(...)`\;
5. Execute `_ensure_tempdir(...)`\;
6. Initialize `ROOT` using `os.path.abspath(...)`\;
7. Branch on `ROOT not in sys.path`\;
8. Set runtime variable `ClimateBERTClient`\;
9. Execute application logic block\;
\caption{High-level pseudocode for `pages/llm_processing.py`}
\label{alg:pages_llm_processing_py}
\end{algorithm}

## `pages/researcher/app.py`

\vspace{7mm}
\begin{algorithm}[H]
\SetAlgoLined
\DontPrintSemicolon
\SetKwInOut{Input}{Input}
\SetKwInOut{Output}{Output}
\Input{Runtime context, configuration, and data sources for `pages/researcher/app.py`}
\Output{Rendered UI state and side effects produced by `pages/researcher/app.py`}
1. Load required modules and utilities\;
2. Render Streamlit UI via `set_page_config(...)`\;
3. Set runtime variable `ROOT`\;
4. Set runtime variable `RESULTS_DIR`\;
5. Set runtime variable `DATA_DIR`\;
6. Set runtime variable `THESIS_PDF_DIR`\;
7. Define helper `parse_json_records(...)`\;
8. Define helper `load_table(...)`\;
9. Define helper `discover_tables(...)`\;
\caption{High-level pseudocode for `pages/researcher/app.py`}
\label{alg:pages_researcher_app_py}
\end{algorithm}
