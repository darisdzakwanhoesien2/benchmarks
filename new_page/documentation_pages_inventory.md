# Pages Inventory Documentation

This document is the exhaustive reference for the `pages/` directory.

It complements:

- [documentation.md](/home/ubuntu/apps/benchmarks/new_page/documentation.md) for page grouping and thesis alignment
- [code_documentation.md](/home/ubuntu/apps/benchmarks/new_page/code_documentation.md) for repository-wide context

## 1. Purpose of `pages/`

`pages/` is the main Streamlit multi-page thesis workspace. It contains:

- pipeline execution pages
- visualization pages
- audit pages
- chapter-writing pages
- helper apps
- support assets used by those pages

## 2. Core Python Pages

### Navigation and setup

- `pages/0_0_Streamlit_Page_Workflow.py`
  - Title: `Streamlit Page Workflow`
  - Purpose: master navigation hub and workflow graph for the thesis app

- `pages/_page_runtime_controls.py`
  - Helper module, not a standalone dashboard
  - Purpose: runtime freeze / refresh controls for heavy pages

### Source data and ingestion

- `pages/0_2_JSON_Ontology_Usage_Map.py`
  - Title: `JSON Ontology Usage Map`
  - Purpose: track ontology, category, grouping, and mapping JSON usage across pages

- `pages/0_3_OCR_Company_Metadata_Labeler.py`
  - Title: `OCR Company Metadata Labeler`
  - Purpose: assign company labels and sector metadata to OCR document folders

- `pages/0_4_Sustainable_Framework_API_Reader.py`
  - Title: `Sustainable Framework API Reader`
  - Purpose: browse external API datasets and export snapshots

- `pages/0_5_Thesis_Systematic_Workflow.py`
  - Title: `Thesis Systematic Workflow`
  - Purpose: executable thesis workflow derived from the draft PDF

- `pages/0_10_Live_Numbers_Lineage.py`
  - Title: `Live Numbers + Lineage`
  - Purpose: compute live metrics and show which artifacts they come from

- `pages/0_11_Source_Data_Catalog.py`
  - Title: `Source Data Catalog`
  - Purpose: inventory and preview files under `data/`

### OCR and PDF preparation

- `pages/Bulk_OCR.py`
  - Title: `Bulk OCR Pipeline — Mistral`
  - Purpose: bulk OCR processing pipeline

- `pages/1_2_OCR_Quality_Workbench.py`
  - Title: `OCR Quality Workbench`
  - Purpose: CER/WER-style quality measurement for OCR text

- `pages/2_4_PDF_Page_Processing_Audit.py`
  - Title: `PDF Page Processing Audit`
  - Purpose: page-level checklist for OCR and LLM processing coverage

### Main pipeline and result visualization

- `pages/llm_processing.py`
  - Title: `ESG Combined Pipeline`
  - Purpose: combined T1 ClimateBERT, T2 ABSA, and T3 LLM extraction page

- `pages/2_0_LLM_Processing_Result_Visualizer.py`
  - Title: `LLM Processing Result Visualizer`
  - Purpose: inspect T1, T2, and T3 outputs together

- `pages/2_1_LLM_Error_Parse_Audit.py`
  - Title: `LLM Error & Parse Audit`
  - Purpose: separate successful parses, raw-only outputs, and failed cases in `results/esg_records.json`

- `pages/2_2_LLM_Statement_Page_Verifier.py`
  - Title: `LLM Statement Page Verifier`
  - Purpose: match extracted statements back to OCR page text

- `pages/2_3_LLM_Background_Run_Monitor.py`
  - Title: `LLM Background Run Monitor`
  - Purpose: launch and inspect background T3 extraction jobs

- `pages/2_5_LLM_Model_Catalog_Visualizer.py`
  - Title: `LLM Model Catalog`
  - Purpose: inspect workbook-based model catalog metadata

### Ground truth and validation

- `pages/ground_truth.py`
  - Title: `ESG Pipeline (Resumable)`
  - Purpose: ground-truth oriented processing page with resumable execution

- `pages/1_1_Ground_Truth_Workbench.py`
  - Title: `Ground Truth Workbench`
  - Purpose: pilot annotation scaffold for tone, ESG pillar, and aspect labels

- `pages/1_3_Ground_Truth_Metrics.py`
  - Title: `Ground Truth Metrics`
  - Purpose: accuracy, F1, kappa, confusion matrices, and error tables

- `pages/1_8_Ground_Truth_Output_Visualizer.py`
  - Title: `Ground Truth Output Visualizer`
  - Purpose: inspect saved annotation and validation outputs

- `pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py`
  - Title: `Ground Truth Pipeline Output Visualizer`
  - Purpose: inspect saved T1 and T2 ground-truth pipeline outputs

- `pages/1_10_Ground_Truth_Run_Coverage.py`
  - Title: `Ground Truth Run Coverage`
  - Purpose: show what source rows have and have not been processed

- `pages/1_11_Ground_Truth_Record_Audit.py`
  - Title: `Ground Truth Record Audit`
  - Purpose: record-level audit joining T1 and T2 outputs

- `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`
  - Title: `Ground Truth Step-by-Step Visualizer`
  - Purpose: walk the full file-level trail from source to T1 and T2 outputs

### Tone and ClimateBERT

- `pages/0_9_Tone_ClimateBERT_Visualization.py`
  - Title: `Tone vs ClimateBERT Visualization`
  - Purpose: compare extracted tone labels with ClimateBERT-style outputs

- `pages/1_4_ClimateBERT_Record_Batch.py`
  - Title: `ClimateBERT Record Batch`
  - Purpose: prepare and inspect records used for ClimateBERT validation

- `pages/1_14_ClimateBERT_Multi_Model_Runner.py`
  - Title: `ClimateBERT Multi-Model Runner`
  - Purpose: run the same dataset across multiple local models and merge results

### Flow, ontology, and graph export

- `pages/1_5_ESG_Flow_Sankey.py`
  - Title: `ESG Flow Sankey`
  - Purpose: visualize flow across company/source, ESG pillar, aspect, tone, prompt, and review issues

- `pages/1_6_Ontology_Path_Viewer.py`
  - Title: `Ontology Path Viewer`
  - Purpose: trace records to ontology paths and unmapped aspects

- `pages/1_13_Semantic_Graph_Exporter.py`
  - Title: `Semantic Graph Exporter`
  - Purpose: export Turtle, OWL, and Neo4j graph artifacts

### Revision, planning, and action tracking

- `pages/1_0_Revision_Analytics.py`
  - Title: `Revision Analytics Dashboard`
  - Purpose: quantitative checks requested by revision feedback

- `pages/1_7_Research_Questions_Dashboard.py`
  - Title: `Research Questions Dashboard`
  - Purpose: map results and benchmarks to thesis RQ1-RQ6

- `pages/1_15_Thesis_Gap_Closure_Dashboard.py`
  - Title: `Thesis Gap Closure Dashboard`
  - Purpose: implement strategic improvements from `improvement_001.md`

- `pages/3_0_Thesis_Action_Plan.py`
  - Title: `Thesis Action Plan — Steps 1 to 6`
  - Purpose: main operational command center for thesis completion

### A.4 and ClimateBERT table regeneration

- `pages/3_1_A4_Per_Model_Background_Run.py`
  - Title: `A.4 Per-Model Background Run`
  - Purpose: run per-model A.4 crosstab generation in the background

- `pages/3_2_A4_Per_Model_Dashboard.py`
  - Title: `A.4 Per-Model Dashboard`
  - Purpose: visualize per-model full-corpus A.4 outputs

- `pages/3_3_A4_Regenerate_Fix_Grouping.py`
  - Title: `A.4 Regenerate (Tone x ClimateBERT label)`
  - Purpose: regenerate normalized A.4 crosstabs and chart output

### Workflow and chapter dashboards

- `pages/5_Thesis_Systematic_Workflow_dashboard.py`
  - Title: `Thesis Systematic Workflow Dashboard`
  - Purpose: thesis workflow dashboard built from current artifacts

- `pages/5_1_Thesis_Systematic_Workflow_dashboard_generated.py`
  - Title: `Thesis Systematic Workflow Dashboard`
  - Purpose: generated version of the same workflow dashboard

- `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`
  - Title: `Thesis Draft + Chapters 4-6 Integration Map`
  - Purpose: integrated thesis spine with Mermaid maps and evidence links

- `pages/6_1_Chapter_4_Implementation_Results.py`
  - Title: `Chapter 4 - Implementation and Results`
  - Purpose: interactive chapter page backed by current artifacts

- `pages/6_2_Chapter_5_Discussion.py`
  - Title: `Chapter 5 - Discussion`
  - Purpose: interactive discussion chapter with supporting result graphs

- `pages/6_3_Chapter_6_Conclusion.py`
  - Title: `Chapter 6 - Conclusion`
  - Purpose: interactive conclusion chapter

- `pages/6_4_ch4-6.py`
  - Title: `Ch4-6 Structure Benchmarks and Graph Attachments`
  - Purpose: benchmark tables, attachment cards, and chapter appendix support

## 3. Helper Apps Inside `pages/`

- `pages/annotator/app.py`
  - Title: `Annotation Workspace`
  - Purpose: edit revision-analysis CSVs

- `pages/researcher/app.py`
  - Title: `Research Explorer`
  - Purpose: browse tables and PDF inventory

- `pages/backend/app.py`
  - Title: `Backend Monitor`
  - Purpose: inspect background jobs, logs, and artifact sizes

## 4. Non-Python Support Assets in `pages/`

### JSON and cache assets

- `pages/models_cache.json`
  - cached model catalog data

- `pages/data_001_001.json`
  - page-local JSON support artifact

### Markdown support files

- `pages/review_paper.md`
- `pages/review_paper_prompt.md`
- `pages/review_paper_prompt_without_ocr.md`
- `pages/final_diagram.md`
- `pages/final_notes.md`
- `pages/source.md`
- `pages/notes.md`

These appear to support writing, prompt scaffolding, or page-local reference views.

### Generated markdown outputs

- `pages/output/002.md`
- `pages/output/003.md`
- `pages/output/004.md`
- `pages/output/005.md`
- `pages/output/006.md`
- `pages/output/007.md`
- `pages/output/008.md`
- `pages/output/009.md`
- `pages/output/010.md`
- `pages/output/011.md`

### HTML artifacts

- `pages/sample_size_reasoning.html`
- `pages/chapter4_results_plan_by_rq.html`
- `pages/thesis_data_analysis_benchmarks.html`

### Binary thesis assets

- `pages/Thesis_Complete_Narrative.docx`
- `pages/thesis_chapters_4_5_6.docx`
- `pages/thesis_draft_1.pdf`
- `pages/thesis_draft/toward_an_executable_esg_aspect_based_sentiment_analysis_framework_for_indonesian_sustainability_reports.docx`

### Screenshots

- `pages/Screenshot 2026-03-27 at 16.03.58.png`
- `pages/Screenshot 2026-03-30 at 16.37.27.png`
- `pages/Screenshot 2026-03-30 at 16.37.29.png`

## 5. Recommended Reading Order

If you are trying to understand the page system, this order is practical:

1. `pages/0_0_Streamlit_Page_Workflow.py`
2. `pages/0_5_Thesis_Systematic_Workflow.py`
3. `pages/3_0_Thesis_Action_Plan.py`
4. `pages/llm_processing.py`
5. `pages/ground_truth.py`
6. `pages/5_Thesis_Systematic_Workflow_dashboard.py`
7. `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`

## 6. Summary

The `pages/` directory is the main executable thesis environment. Its most important modules are:

- navigation and catalog pages
- LLM / OCR / ground-truth processing pages
- revision and thesis-planning dashboards
- chapter-integration pages
- helper apps for annotation, research browsing, and backend monitoring
