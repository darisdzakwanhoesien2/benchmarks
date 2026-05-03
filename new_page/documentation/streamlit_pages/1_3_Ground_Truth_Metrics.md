# 1.3 Ground Truth Metrics

## Purpose

This page computes formal evaluation metrics after human labels have been added in the Ground Truth Workbench. It is designed to answer the revision feedback requiring accuracy, precision, recall, F1, Cohen's kappa, confusion matrices, and error analysis.

## Data Used

Preferred input:

- `results/revision_analysis/pilot_ground_truth_annotations.csv`

Fallback input:

- `results/revision_analysis/pilot_ground_truth_seed.csv`

Optional export:

- `results/revision_analysis/silver_tone_ground_truth.csv`

## Workflow Steps

1. Load annotation table.
2. Count filled human labels.
3. For tone:
   - compare `ground_truth_tone` to `tone_pred`.
4. For ESG:
   - compare `ground_truth_esg` to `esg`.
5. For aspect:
   - compare `ground_truth_aspect` to `aspect`.
6. Compute:
   - accuracy,
   - weighted precision,
   - weighted recall,
   - weighted F1,
   - Cohen's kappa.
7. Display confusion matrices.
8. Display disagreement tables.

## Interpretation

Accuracy shows exact agreement. Weighted F1 is better when class imbalance exists. Cohen's kappa adjusts for agreement expected by chance and is more defensible for a thesis evaluation.

If no labels are filled, the page will show that metrics cannot yet be computed. This is intentional: the page separates model outputs from human validation.

## Thesis Use

- Chapter IV: evaluation metrics.
- Chapter V: reliability discussion.
- Aspect 5 and 6 revision response: proof that aims were evaluated quantitatively.

