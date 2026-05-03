# 1.0 Revision Analytics

## Purpose

This page directly responds to the revision feedback. It turns the critique into measurable evidence by computing prompt stability, schema drift, ClimateBERT proxy agreement, greenwashing index, failure modes, lexical triggers, ontology coverage, and OCR scaffolding.

It is the central dashboard for improving the thesis from a prototype description into a quantitatively evaluated research system.

## Data Used

Primary artifact folder:

- `results/revision_analysis/`

Main files:

- `silver_tone_ground_truth.csv`
- `prompt_stability_summary.csv`
- `prompt_stability_by_run.csv`
- `model_stability_summary.csv`
- `greenwashing_index_by_company.csv`
- `climatebert_proxy_agreement_summary.csv`
- `climatebert_proxy_agreement_records.csv`
- `failure_modes.csv`
- `failure_mode_counts.csv`
- `lexical_triggers.csv`
- `lexical_trigger_counts.csv`
- `ontology_coverage.csv`
- `ocr_processing_summary.csv`

These artifacts are generated from `results/esg_records.json`.

## Workflow Steps

1. Load the silver record table.
2. Filter records by company/source, predicted tone, and language.
3. Compute or display prompt-level stability metrics.
4. Display ClimateBERT proxy agreement statistics.
5. Plot company-level greenwashing index.
6. Diagnose missing tone and schema drift records.
7. Quantify lexical triggers for commitment, action, outcome, passive voice, hedging, and regulatory terms.
8. Display ontology coverage and OCR processing scaffolding.

## Tabs

### Overview

Shows:

- total filtered records,
- records needing review,
- missing tone count,
- schema drift count,
- tone distribution,
- language distribution,
- review candidate table.

### Prompt Stability

Shows:

- JSON parse success rate,
- average records per run,
- missing tone rate,
- schema drift rate,
- field completion rate.

This answers the feedback asking for statistical comparison across seven prompt templates.

### Agreement

Compares:

- `tone_pred == commitment`,
- presence of the `climate-commitment` label.

Outputs:

- percent agreement,
- Cohen's kappa,
- discordant cases.

This is a proxy agreement analysis, not a final ClimateBERT benchmark.

### Greenwashing Index

Shows company/source-level rhetoric-to-results ratio:

```text
greenwashing_index = (commitment + 0.5) / (outcome + 0.5)
```

A high value means the source has more commitment language than outcome language. It is a screening signal, not proof of greenwashing.

### Failure Modes

Categorizes review candidates by:

- missing tone,
- schema drift,
- hedged/modal language,
- passive voice,
- regulatory Indonesian terms,
- table/numeric layout,
- bilingual/code-switched text,
- long complex sentence.

### Language Triggers

Quantifies lexical markers such as:

- commitment markers: `will`, `target`, `akan`, `berkomitmen`,
- action markers: `implemented`, `melakukan`, `menerapkan`,
- outcome markers: `achieved`, `telah`, `berhasil`,
- passive and regulatory markers.

### Ontology and OCR

Shows ontology coverage and OCR processing logs. Formal CER/WER must be added through the OCR workbench.

## How To Interpret

This page gives the thesis evidence for:

- prompt stability,
- schema drift,
- linguistic failure modes,
- company-level greenwashing index,
- ontology coverage,
- ClimateBERT proxy agreement.

It should be used heavily in Chapter IV and Chapter V.

