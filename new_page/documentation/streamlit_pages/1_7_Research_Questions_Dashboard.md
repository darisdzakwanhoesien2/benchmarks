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

