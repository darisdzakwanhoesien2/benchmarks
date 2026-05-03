# 1.1 Ground Truth Workbench

## Purpose

This page creates the human annotation layer required by the revision feedback. It allows a reviewer to label a pilot sample of records with true tone, ESG pillar, and aspect values.

The page is important because current model outputs are not enough to claim formal accuracy. Human annotation is needed before reporting precision, recall, F1, or final Cohen's kappa.

## Data Used

Input seed:

- `results/revision_analysis/pilot_ground_truth_seed.csv`

Saved annotation output:

- `results/revision_analysis/pilot_ground_truth_annotations.csv`

Optional full scaffold:

- `results/revision_analysis/silver_tone_ground_truth.csv`

## Workflow Steps

1. Load saved annotations if they exist.
2. Otherwise load the pilot seed file.
3. Filter by review status, predicted tone, and language.
4. Edit ground-truth fields in the annotation table.
5. Save annotations to CSV.
6. Compute preliminary agreement when human labels exist.

## Annotation Fields

Main human fields:

- `ground_truth_tone`
- `ground_truth_esg`
- `ground_truth_aspect`
- `annotator`
- `review_notes`
- `review_status`

Model fields are shown but locked:

- `tone_pred`
- `suggested_tone`
- `esg`
- `aspect`
- `text`

## Annotation Protocol

Use `ground_truth_tone` as the human label:

- `commitment`: target, plan, pledge, intention, or future-oriented disclosure.
- `action`: policy, program, implementation, procedure, or activity.
- `outcome`: measured result, achieved target, completed activity, reduction, or certification.
- `none`: no meaningful ESG tone.
- `unknown`: insufficient context.

## Outputs

The saved file `pilot_ground_truth_annotations.csv` becomes input to:

- `1_3_Ground_Truth_Metrics.py`

## Thesis Use

- Chapter III: benchmark and ground-truth design.
- Chapter IV: pilot human validation results.
- Chapter V: limitations and reliability discussion.

