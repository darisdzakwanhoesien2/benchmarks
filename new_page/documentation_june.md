# Repository File Guide (June 2026)

This document is a **high-level map of what the main files and folders are for** in this workspace (`/home/ubuntu/apps/benchmarks/new_page`).

- Where possible, descriptions are based on directly reading the file.
- For large artifacts (PDF/DOCX/ZIP) and some helper scripts, descriptions are **best-effort based on filename and surrounding repo structure**.

---

## Top-level entrypoints

- `app.py` — Main Streamlit “hub” app. It sets the page config and provides navigation links to key pages under `pages/` (Streamlit multi-page discovery works best when launching Streamlit from this file).
- `_page_runtime_controls.py` — Sidebar “Runtime Controls” helper (Freeze/Refresh) intended to be imported by Streamlit pages to avoid rerunning heavy work unless the user clicks refresh.
- `Makefile` — Run orchestration for reproducible “runs”: create run folders, generate run manifests (`run.json`), compare runs, publish runs to a remote location, and optionally track outputs with DVC.
- `requirements.txt` — Python dependency pins for Streamlit + data/ML stack used across pages and tooling.

---

## Streamlit pages (`pages/`)

`pages/` contains the primary multi-page Streamlit app. Each file is a page unless it is a helper module.

### Core navigation pages

- `pages/0_0_Streamlit_Page_Workflow.py` — “Streamlit Page Workflow”: explains how to navigate and how the pages relate to the thesis pipeline.
- `pages/3_0_Thesis_Action_Plan.py` — “Thesis Action Plan”: large dashboard/checklist-style page for tracking thesis workflow progress.
- `pages/5_Thesis_Systematic_Workflow_dashboard.py` — “Thesis Systematic Workflow Dashboard”: thesis workflow dashboard (manually curated).
- `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py` — “Thesis Systematic Workflow Dashboard”: generated version of the workflow dashboard.

### Data lineage, catalogs, and auditing

- `pages/0_10_Live_Numbers_Lineage.py` — “Live Numbers + Lineage”: summarizes key metrics and connects them to artifacts/lineage.
- `pages/0_11_Source_Data_Catalog.py` — “Source Data Catalog”: catalog of available source datasets/artifacts.
- `pages/1_0_Revision_Analytics.py` — “Revision Analytics”: analyzes revision/iteration results across runs.
- `pages/2_4_PDF_Page_Processing_Audit.py` — “PDF Page Processing Audit”: audits how PDF pages were processed (OCR/extraction step visibility).

### OCR + preparation

- `pages/Bulk_OCR.py` — “Bulk OCR — Mistral”: bulk OCR driver/visualization for turning PDFs into text/page-level outputs.
- `pages/0_3_OCR_Company_Metadata_Labeler.py` — “OCR Company Metadata Labeler”: assigns/edits company metadata for OCR’d documents.
- `pages/1_2_OCR_Quality_Workbench.py` — “OCR Quality Workbench”: spot-checks OCR quality and failure modes.

### Ontology / mapping / semantics

- `pages/0_2_JSON_Ontology_Usage_Map.py` — “JSON Ontology Usage Map”: shows how ontology labels/aspects are used in JSON artifacts.
- `pages/1_6_Ontology_Path_Viewer.py` — “Ontology Path Viewer”: explores paths/relationships within the ontology.
- `pages/1_13_Semantic_Graph_Exporter.py` — “Semantic Graph Exporter”: exports a semantic/knowledge graph representation from artifacts.

### Ground truth (labeling + evaluation)

- `pages/ground_truth.py` — “ESG Pipeline”: ground-truth oriented pipeline page (anchors the labeling + evaluation workflow).
- `pages/1_1_Ground_Truth_Workbench.py` — “Ground Truth Workbench”: UI for interacting with ground-truth records.
- `pages/1_3_Ground_Truth_Metrics.py` — “Ground Truth Metrics”: metrics and summaries over ground-truth labels.
- `pages/1_8_Ground_Truth_Output_Visualizer.py` — “Ground Truth Output Visualizer”: visualizes ground-truth outputs.
- `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py` — “Ground Truth Pipeline Output Visualizer”: compares/visualizes outputs from the full pipeline.
- `pages/1_10_Ground_Truth_Run_Coverage.py` — “Ground Truth Run Coverage”: coverage analysis of what got labeled/processed.
- `pages/1_11_Ground_Truth_Record_Audit.py` — “Ground Truth Record Audit”: audits individual records for correctness/completeness.
- `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py` — “Ground Truth Step-by-Step Visualizer”: step-by-step tracing through the ground-truth workflow.

### LLM processing + verification

- `pages/2_0_LLM_Processing_Result_Visualizer.py` — “LLM Processing Result Visualizer”: visualizes structured results produced by LLM processing.
- `pages/2_1_LLM_Error_Parse_Audit.py` — “LLM Error & Parse Audit”: inspects schema drift / parse errors / failure cases.
- `pages/2_2_LLM_Statement_Page_Verifier.py` — “LLM Statement Page Verifier”: verifies LLM statements against page-level sources.
- `pages/2_3_LLM_Background_Run_Monitor.py` — “LLM Background Run Monitor”: monitors background LLM jobs and their progress.
- `pages/2_5_LLM_Model_Catalog_Visualizer.py` — “LLM Model Catalog Visualizer”: shows available models/configurations and compares them.

### ClimateBERT / tone

- `pages/0_9_Tone_ClimateBERT_Visualization.py` — “Tone vs ClimateBERT”: compares tone labels with ClimateBERT-style outputs.
- `pages/1_4_ClimateBERT_Record_Batch.py` — “ClimateBERT Record Batch”: batch scoring of records through ClimateBERT.
- `pages/1_14_ClimateBERT_Multi_Model_Runner.py` — “ClimateBERT Multi-Model Runner”: runs multiple ClimateBERT models and compares predictions.

### ESG flow / Sankey

- `pages/1_5_ESG_Flow_Sankey.py` — “ESG Flow Sankey”: Sankey visualization for ESG/aspect flows through the pipeline.

### Research questions + thesis chapters

- `pages/1_7_Research_Questions_Dashboard.py` — “Research Questions Dashboard”: maps artifacts/metrics back to thesis research questions.
- `pages/1_15_Thesis_Gap_Closure_Dashboard.py` — “Thesis Gap Closure Dashboard”: tracks open gaps and evidence coverage.
- `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py` — “Thesis Draft + Chapters Mermaid Integration”: builds a mermaid-based integration view for thesis chapters and artifacts.
- `pages/6_1_Chapter_4_Implementation_Results.py` — “Chapter 4 - Implementation and Results”: thesis chapter dashboard/content.
- `pages/6_2_Chapter_5_Discussion.py` — “Chapter 5 - Discussion”: thesis chapter dashboard/content.
- `pages/6_3_Chapter_6_Conclusion.py` — “Chapter 6 - Conclusion”: thesis chapter dashboard/content.
- `pages/6_4_ch4-6.py` — “Ch4-6 Benchmarks + DOCX Graphs”: benchmarking/graph export helpers for thesis chapter integration.

### Page utilities and assets

- `pages/_page_runtime_controls.py` — Same concept as top-level `_page_runtime_controls.py`, but scoped for `pages/` imports.
- `pages/models_cache.json` — cached model catalog metadata used by pages.
- `pages/output/` — exported markdown outputs generated by pages.
- `pages/thesis_draft/` — thesis draft assets (e.g., bib, csv, docx).
- `pages/*.html`, `pages/*.png`, `pages/*.docx`, `pages/*.pdf` — supporting artifacts and exports rendered or referenced by the Streamlit pages.

---

## API (`api/`)

This folder contains a small HTTP service for serving markdown documentation.

- `api/documentation_api.py` — Minimal HTTP server that indexes markdown docs in a controlled scope (e.g., `documentation*.md`, `docs/*.md`, `documentation/**/*.md`) and serves them via endpoints like `GET /docs` and `GET /docs/{doc_id}`.
- `api/climatebert_client.py` — Minimal wrapper client around a HuggingFace/Gradio Space for ClimateBERT multi-model predictions (reads `CLIMATEBERT_SPACE_URL` and optional `HF_TOKEN`).
- `api/README.md` — How to run the documentation API and endpoint definitions.

---

## Chatbot research app (`chatbot/`)

- `chatbot/app.py` — Streamlit app that renders a chatbot research plan and “grounds” it with summary counts/tables from CSVs in `results/revision_analysis/`.
- `chatbot/README.md` — Overview of the chatbot research-plan app and which datasets it reads.
- `chatbot/review_paper.md` / `chatbot/review_paper_prompt.md` — Literature review draft + its prompt scaffold for generating/iterating the review.

---

## Shared code library (`code/`)

`code/` is a Python module directory used by multiple pages/tools.

- `code/__init__.py` — module init.
- `code/app_state.py` — small shared state/helpers (lightweight).
- `code/utils.py` — general utility functions used across workflows.
- `code/action_plan_status.py` — helpers for tracking action plan/task state.
- `code/lexicons.py` — lexicons/term lists used for labeling or parsing.
- `code/data_alignment.py` — alignment/normalization utilities between datasets/artifacts.
- `code/semantic_exporter.py` — functions that export semantic graph/structured representations.
- `code/graph_attachment_gallery.py` — builds/serves galleries of graph attachments/exports.
- `code/ground_truth_graphs.py` — graph construction utilities specifically for ground-truth evidence.
- `code/llm_background_worker.py` — background LLM processing worker helpers.
- `code/ground_truth_background_worker.py` — background worker helpers for ground-truth workflows.
- `code/climatebert_background_worker.py` — background worker helpers for ClimateBERT runs.
- `code/classical_ml.py` / `code/deep_model.py` / `code/deep_model_v2.py` / `code/hybrid_model.py` / `code/rule_based.py` — different modeling approaches (classical, deep, hybrid, rule-based) for ESG/ABSA-related tasks.
- `code/explainability.py` — explainability/interpretation utilities for model outputs.
- `code/visualize_tone_climatebert.py` — visualization helpers for tone vs ClimateBERT comparisons.
- `code/thesis_chapter_streamlit.py` — helpers for rendering thesis chapter pages/sections inside Streamlit.

---

## Data, results, and outputs

These folders contain large artifacts and intermediate/final outputs.

- `data/` — raw and processed inputs (e.g., PDFs, stock info, datasets).
  - `data/raw/` — raw inputs.
  - `data/processed/` — transformed inputs.
  - `data/thesis_dataset/`, `data/thesis_pdf/` — the main thesis corpus and PDFs.
  - `data/stock_info/` — scraped/collected stock sector pages (HTML snapshots).
  - `data/idx_data.csv` / `data/ESG Score.xlsx` — key dataset files used by the pipeline.
- `results/` — run products, exports, and derived datasets (often large).
  - includes background job folders, exports, JSON/JSONL results, revision analysis, and visualization assets.
- `outputs/` — standardized per-run output directory (intended target: `outputs/<project>/<run_id>/...`). The repo’s `Makefile` + `scripts/` help create and track these.
- `reports/` — intended place for reports (may be populated by scripts/pages).

---

## Ops + reproducibility (`ops/`, `scripts/`)

- `ops/DATA_OPS.md` — documented workflow for creating run folders, generating `run.json` manifests, comparing runs, publishing runs to remote storage, and (optionally) tracking large outputs with DVC.
- `scripts/start_run.py` — creates a new run directory (used by `make start-run`).
- `scripts/generate_manifest.py` — generates `run.json` manifest for a run directory (used by `make manifest`).
- `scripts/compare_runs.py` — compares two runs (directory or manifest) and reports changes (used by `make compare`).
- `scripts/publish_run.sh` — publishes a run directory to a remote location (used by `make publish`).
- `scripts/bootstrap_dvc.sh` — initializes DVC setup (used by `make dvc-init`).

---

## Prompts (`prompt/`)

Reusable prompt templates used for extraction, classification, and experiments.

- `prompt/zero_shot_english.md`, `prompt/few_shot_english.md`, `prompt/chain_of_thought_english.md` — English prompt variants.
- `prompt/zero_shot_indonesian.md`, `prompt/few_shot_indonesian.md`, `prompt/chain_of_thought_indonesian.md` — Indonesian prompt variants.
- `prompt/tone_*` — tone-focused prompt variants (zero-shot, few-shot, chain-of-thought) in English/Indonesian.
- `prompt/data.md`, `prompt/data_v1.md` — dataset/payload formatting guidance for prompts.

---

## Tooling helpers (`tools/`)

Small scripts that generate or update thesis artifacts and charts.

- `tools/build_coherent_thesis_docx.py` — builds a more coherent thesis DOCX from parts/inputs.
- `tools/generate_chapter_resolution_artifacts.py` — generates chapter resolution artifacts for reporting.
- `tools/update_ch4_6_docx_graphs.py` — updates graphs for Chapter 4–6 DOCX outputs.
- `tools/regenerate_a4_chart.py` — regenerates A.4 charts/plots for dashboards/chapters.
- `tools/climatebert_a4/generate_a4_per_model.py` — generates A.4 per-model artifacts for ClimateBERT comparisons.

---

## Documentation and writing artifacts (top-level `*.md`, `docs/`, `documentation/`)

This repo is documentation-heavy; many markdown files are thesis notes, research plans, and module documentation.

- `documentation.md` — primary “Streamlit Page Documentation” (explains how pages map into the thesis workflow).
- `complete_documentation.md` — consolidated documentation snapshot (project-wide).
- `research_documentation.md` — research-oriented documentation entrypoint.
- `docs/complete_research_documentation.md`, `docs/tone_climatebert_comparison.md` — additional research documentation files.
- `documentation_*.md` — topic-specific documentation tracks (LLM, chatbot, fine-tuning, summarization, topic modeling, social network analysis, transfer learning, fact checking, etc.).
- `methodology_pipeline_mermaid.md`, `mermaid_workflow_and_insights.md` — mermaid diagrams and workflow write-ups.
- `progress_notes.md`, `notes.md`, `vps_notes.md`, `job/notes.md` — working notes, ops notes, and log-style updates.
- `thesis_paper_esg_absa.md` and related `*.docx` — thesis manuscript and export formats.

---

## “Hidden” / legacy work (`hidden_pages/`, `past_pages/`, `pages_non_ocr/`, `results_old/`)

These folders generally contain older prototypes, experimental pages, and previous result snapshots.

- `hidden_pages/` — prototypes/experiments that are not part of the main Streamlit navigation.
- `past_pages/`, `pages_non_ocr/` — older Streamlit page sets.
- `results_old/` — older result snapshots kept for reference.

---

## Large binary artifacts (selected)

These are not “code”, but are important project outputs/inputs.

- `bulk_ocr_outputs.zip` — bulk OCR output archive (large).
- `thesis_draft_1.pdf` — thesis draft PDF.
- `thesis_draft_1.pdf` (also appears under `pages/`) — a copy referenced by Streamlit pages.
- Various `*.docx`, `*.pdf`, `*.png`, `*.html` under `pages/`, `documentation/`, and `research_references/` — supporting figures, drafts, and research notes.

---

## Notes on scope

If you need a **per-file line-by-line summary** of every Python module (including `hidden_pages/` and all subprojects like `topic_modelling/`), say so and I can generate a second document that walks each file with: purpose, key functions, inputs/outputs, and where it is imported/used.

