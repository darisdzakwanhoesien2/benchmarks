# Ground Truth

## Purpose

This page supports ground-truth or benchmark processing for extracted ESG records. It is part of the validation layer of the app.

## Data Used

Possible inputs:

- extracted records from `results/esg_records.json`,
- manual input records,
- model prediction outputs,
- ground-truth JSON/CSV files.

Possible outputs:

- `results/ground_truth.json`,
- JSONL benchmark records,
- model comparison records.

## Workflow Steps

1. Load extracted ESG records or manual input.
2. Select model or benchmark mode.
3. Generate prediction or comparison records.
4. Save outputs for later evaluation.

## Relationship To New Ground-Truth Pages

The newer ground-truth workflow is:

1. `1_1_Ground_Truth_Workbench.py` for human annotation.
2. `1_3_Ground_Truth_Metrics.py` for metrics and confusion matrices.
3. `1_4_ClimateBERT_Record_Batch.py` for external ClimateBERT validation.

## Thesis Use

- Chapter III: benchmark design.
- Chapter IV: validation and model comparison.
- Chapter V: limitations of weak labels and need for expert annotation.

