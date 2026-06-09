# Chapter 7 Appendices

This appendix chapter consolidates supplementary material that supports the methodological and reproducibility claims in the main thesis. The appendices are intended to document materials that are important for transparency but too detailed to place in the core chapter narrative.

## 7.1 Appendix Contents

The appendices should contain, at minimum, the following materials:

1. prompt templates used in the main thesis-facing comparisons;
1. model identifiers, providers, and decoding settings where available;
1. benchmark and comparison artifact paths;
1. annotation instructions and tone-label definitions;
1. additional difficult examples and disagreement cases;
1. supplementary failure-mode tables;
1. extended reproducibility notes for rerunning stored analyses.

## 7.2 Tone-Label Definitions

The pilot annotation and review process should use the following working definitions:

1. **Commitment:** forward-looking promises, targets, intentions, or policy declarations that do not yet demonstrate completed implementation or realized outcome.
1. **Action:** concrete activities, agreements, programs, investments, or operational steps that are being undertaken or have been initiated.
1. **Outcome:** realized, completed, or demonstrably achieved results, milestones, or measured performance changes.
1. **Needs review:** records whose language is too ambiguous, mixed, or incomplete for stable tone assignment without additional human interpretation.

## 7.3 Reproducibility Notes

The main reproducibility artifacts referenced in the thesis include:

1. OCR-expanded document folders under `data/thesis_dataset/`;
1. extracted ESG records under `results/esg_records.json`;
1. resumable benchmark outputs under `results/t1_results.jsonl` and `results/t2_results.jsonl`;
1. prompt and model stability summaries under `results/revision_analysis/`;
1. dashboard-ready figures and tables under `results/thesis_workflow_dashboard/`.

These artifacts support rerunning, auditing, and extending the workflow even where exact third-party LLM outputs may vary across time.
