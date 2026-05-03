# 1.4 ClimateBERT Record Batch

## Purpose

This page prepares the extracted records for a complete ClimateBERT validation run. The revision feedback notes that only three remote ClimateBERT inputs are not enough. This page creates a one-to-one batch workflow for all extracted records.

## Data Used

Inputs:

- `results/revision_analysis/silver_tone_ground_truth.csv`
- `results/revision_analysis/climatebert_proxy_agreement_records.csv`

Optional imported real ClimateBERT output:

- `results/revision_analysis/climatebert_record_batch_import.csv`

## Workflow Steps

### Batch Input

1. Load all silver records.
2. Display `record_id`, source, prompt, model, language, tone, and text.
3. Export this as ClimateBERT batch input.
4. Preserve `record_id` when running external ClimateBERT.

### Proxy Batch

Uses existing labels from `esg_records.json` as a weak ClimateBERT-style proxy.

It compares:

- `tone_pred == commitment`,
- `has_climate_commitment == True`.

Outputs:

- percent agreement,
- Cohen's kappa,
- confusion heatmap,
- raw proxy records.

### Import Real Outputs

Upload a real ClimateBERT CSV with:

- `record_id`,
- one commitment output column such as `climate_commitment`, `label`, or `top_label`.

The page saves the merged file and computes agreement.

## Interpretation

The proxy batch is useful for early validation but must not be described as final ClimateBERT evaluation. A final thesis result requires real ClimateBERT outputs for every record.

## Thesis Use

- Chapter III: external validation method.
- Chapter IV: ClimateBERT comparison results.
- Chapter V: limitation of proxy validation and plan for full validation.

