# 1.7 Research Questions Dashboard

## Purpose

This page gives one complete thesis-facing dashboard that answers each research question with current evidence. It is designed to make the relationship between the implementation and the thesis structure explicit.

## Data Used

Inputs from `results/revision_analysis/`:

- `silver_tone_ground_truth.csv`
- `prompt_stability_summary.csv`
- `greenwashing_index_by_company.csv`
- `climatebert_proxy_agreement_summary.csv`
- `failure_mode_counts.csv`
- `ontology_coverage.csv`
- `ocr_quality_samples.csv` if available.

## Research Questions Covered

### RQ1

How can sustainability reports be transformed into structured ESG evidence?

Evidence:

- structured records,
- source count,
- OCR workbench samples.

### RQ2

How can ESG statements be categorized by aspect, ESG pillar, sentiment, and tone?

Evidence:

- aspect count,
- ESG pillar count,
- tone distribution,
- sentiment field.

### RQ3

How do tone results compare with ClimateBERT-style labels?

Evidence:

- proxy agreement,
- Cohen's kappa,
- sample size.

### RQ4

Can disagreement and missing labels reveal weaknesses?

Evidence:

- missing tone records,
- schema drift records,
- failure-mode categories.

### RQ5

What documentation and visualization tools make the research auditable?

Evidence:

- list of Streamlit pages,
- static and dynamic artifacts.

### RQ6

How do prompt strategy and model choice affect extraction stability?

Evidence:

- prompt stability table,
- missing tone rate,
- schema drift rate,
- field completion.

## Interpretation

This page should be used as a final thesis evidence map. It shows which research questions are fully implemented, partly validated, or still awaiting human annotation/OCR reference samples.

## Thesis Use

- Chapter IV: final results overview.
- Chapter VI: contribution summary.
- Defense presentation: one-page map from RQs to evidence.

## RQ Page Map

The dashboard now includes an `RQ Page Map` tab that tells which Streamlit pages should be used to fulfill each research question:

- RQ1: OCR, LLM processing, and pipeline-output pages.
- RQ2: tone/ClimateBERT visualization, ontology path viewer, and ground-truth output pages.
- RQ3: ClimateBERT batch and tone/ClimateBERT comparison pages.
- RQ4: revision analytics, error parse audit, and ground-truth review pages.
- RQ5: dashboard, generated image catalog, documentation index, and artifact folders.
- RQ6: revision analytics, LLM result visualizer, error audit, and ClimateBERT batch page.

Use this tab as the working checklist when writing the thesis so each RQ points to concrete page evidence rather than a generic statement.

## Chapter 4-6 Writing Pages

The dashboard also includes chapter-planning tabs:

- `Chapter 4 Results`: sections, figures, and page sources for reporting empirical results.
- `Chapter 5 Discussion`: interpretation, claim strength, limitations, and validity cautions.
- `Chapter 6 Conclusion`: RQ answer template, contributions, and future-work framing.
- `Ch4-6 Mermaid`: a Mermaid flowchart linking Chapter 4 evidence to Chapter 5 interpretation and Chapter 6 conclusions.

The Mermaid flow is intended as a writing map: Chapter 4 should provide the evidence, Chapter 5 should explain meaning and limitations, and Chapter 6 should answer the RQs and state the contribution.


## Saved Image Outputs

Saved dashboard screenshots and existing visualization outputs are documented in [1_7_Research_Questions_Dashboard_outputs.md](./1_7_Research_Questions_Dashboard_outputs.md). The machine-readable catalog is stored at `results/visualizations/streamlit_outputs/dashboard_image_catalog.json`.
