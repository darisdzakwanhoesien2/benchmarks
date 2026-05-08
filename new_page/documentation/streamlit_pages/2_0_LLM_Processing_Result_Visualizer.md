# 2_0_LLM_Processing_Result_Visualizer.py

## Purpose

This page visualizes the artifacts produced by `llm_processing.py`. It is the result-inspection page for the combined pipeline after T1, T2, and T3 have run.

The page answers:

- Did the pipeline produce records?
- Which model, prompt, and batch produced them?
- Which ESG pillars, tones, aspects, and sentiments dominate?
- Which runs failed or produced empty outputs?
- What did the T2 hybrid ABSA layer predict?
- What did the T1 ClimateBERT/model layer predict?

## Data Used

The page reads:

- `results/predictions.json` for T1 ClimateBERT/model predictions.
- `results/absa_results.json` for T2 rule-based, classical, and hybrid ABSA outputs.
- `results/esg_records.json` for T3 LLM ESG extraction outputs.

It flattens nested JSON into analysis tables:

- T3 run table: one row per model-target-prompt run.
- T3 record table: one row per extracted ESG evidence record.
- T2 run table: one row per ABSA source/batch.
- T2 prediction table: one row per hybrid sentence-level prediction.
- T1 prediction table: one row per model-level prediction.

## Workflow

1. Run `llm_processing.py`.
2. Open this visualizer page.
3. Use the sidebar filters for model, company, target, prompt, ESG pillar, tone, sentiment, aspect, T2 source, and T1 prediction label.
4. Review Overview for high-level distributions.
5. Review T3 ESG Records for extracted evidence.
6. Review T3 Run Quality for failed or empty runs.
7. Review T2 ABSA for hybrid tone, sentiment, ontology alignment, and metrics.
8. Review T1 ClimateBERT for model labels and errors.
9. Export flattened CSVs from Records & Exports.

## Tabs

### Overview

Shows the main T3 extraction distributions:

- tone;
- ESG pillar;
- sentiment;
- prompt run count.

This is the fastest way to see whether the latest LLM run is producing usable ESG evidence or mostly empty outputs.

### T3 ESG Records

Shows the parsed ESG records from `results/esg_records.json`. Important fields include:

- `model`;
- `target`;
- `prompt`;
- `text`;
- `aspect`;
- `labels`;
- `esg`;
- `tone`;
- `sentiment`;
- `sentiment_score`;
- `reasoning`.

Use this tab for thesis examples and evidence-level interpretation.

### T3 Run Quality

Shows run-level quality:

- successful vs failed runs;
- records per run;
- status by model;
- failed or partial runs.

This tab is important for documenting prompt/model reliability. A run can be technically successful but still produce zero parsed records.

### T2 ABSA

Shows rule-based and hybrid ABSA outputs from `results/absa_results.json`:

- hybrid tone;
- hybrid sentiment;
- ontology alignment;
- tone confidence;
- metrics table.

This tab helps compare the deterministic ABSA layer against the LLM extraction layer.

### T1 ClimateBERT

Shows model-level T1 outputs from `results/predictions.json`:

- prediction labels;
- prediction scores;
- errors by model;
- raw prediction rows.

This is useful for diagnosing ClimateBERT/model compatibility and comparing climate-specific signals against broader ESG extraction.

### Records & Exports

Provides CSV downloads for:

- T3 records;
- T3 runs;
- T2 predictions;
- T2 runs;
- T1 predictions.

These exports can be used for further statistical analysis, thesis tables, and validation against ground truth.

## Interpretation

This page is not a model runner. It is a result audit page. It turns raw JSON artifacts into evidence that can be inspected, filtered, exported, and cited.

For final research claims, use this page together with:

- `1_3_Ground_Truth_Metrics.py` for human-label evaluation;
- `1_8_Ground_Truth_Output_Visualizer.py` for annotation coverage and disagreement review;
- `1_7_Research_Questions_Dashboard.py` for RQ-level synthesis.
