# Improvement Implementation 001

This file documents concrete implementation completed from `improvement_001.md`.

## Scope Applied

Reviewed `pages/` and implemented a new thesis-facing page plus workflow integration to address the strategic gaps listed in the improvement note.

## Implemented Changes

### 1) New Page: Thesis Gap Closure Dashboard

Created:
- `pages/1_15_Thesis_Gap_Closure_Dashboard.py`

Purpose:
- Consolidates strategic thesis risks into one operational dashboard using existing `results/revision_analysis` artifacts.

Sections implemented in the page:
1. Baseline hierarchy (VADER, FinBERT, ClimateBERT, LLM ABSA, LLM+Ontology)
2. Significance layer (bootstrap CI over verifier exact-match rate + stability table context)
3. Formal error taxonomy (from `failure_modes.csv` + canonical categories)
4. Greenwashing validation status (from `greenwashing_index_by_company.csv` with explicit gap callout)
5. Ontology contribution view (from `ontology_coverage_full.csv` sample rows + mapping counts)
6. Bilingual and temporal analysis starter (language distribution + inferred year counters)
7. Threats-to-validity table (internal/construct/external/conclusion validity + mitigations)
8. Ablation plan matrix (LLM-only through full pipeline)

Data sources used by this page:
- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
- `results/revision_analysis/failure_modes.csv`
- `results/revision_analysis/ontology_coverage_full.csv`
- `results/revision_analysis/greenwashing_index_by_company.csv`
- `results/revision_analysis/prompt_stability_summary.csv`
- `results/revision_analysis/model_stability_summary.csv`

### 2) Workflow Hub Integration

Updated:
- `pages/0_0_Streamlit_Page_Workflow.py`

Changes:
- Added `1_15_Thesis_Gap_Closure_Dashboard.py` into `PAGE_REGISTRY` with stage, RQ coverage, purpose, and output description.
- Added a new fast-path row:
  - Task: `Close thesis strategic gaps`
  - Start page: `1_15_Thesis_Gap_Closure_Dashboard.py`
  - Follow-up pages: `1_0, 1_7, 6_4`

## Mapping Back to improvement_001.md

Implemented directly:
- Stronger baseline section: yes (formal hierarchy table)
- Statistical significance/testing layer: partial (bootstrap CI implemented; formal McNemar/chi-square not yet added)
- Error taxonomy: yes (formalized with counts + canonical categories)
- Greenwashing validation: partial (status surfaced; explicit expert-label gap flagged)
- Ontology contribution analysis: partial (coverage and sample contribution rows added; standardized variant table still pending)
- Bilingual analysis: partial (language distribution added)
- Temporal analysis: partial (inferred year proxy added; explicit year metadata still needed)
- Threats-to-validity section: yes (structured table with mitigation)
- Ablation study framing: yes (configuration matrix)

Not implemented in this change set:
- Direct McNemar / chi-square tests across paired prediction outputs
- Expert-labeled greenwashing adjudication module
- Dedicated Indonesian-vs-English model-performance benchmark table
- Full temporal trend charts from explicit report-year metadata

## Validation

- `python3 -m py_compile pages/1_15_Thesis_Gap_Closure_Dashboard.py`
- `python3 -m py_compile pages/0_0_Streamlit_Page_Workflow.py`

Both compile successfully.

## Run

Main workflow hub:
```bash
streamlit run app.py
```

Direct page:
```bash
streamlit run pages/1_15_Thesis_Gap_Closure_Dashboard.py
```
