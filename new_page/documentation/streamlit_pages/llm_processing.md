# LLM Processing

## Purpose

This page is the main extraction pipeline. It processes selected report text through LLM prompts and model backends, then stores structured ESG records.

## Data Used

Inputs:

- manual text,
- OCR-derived markdown pages,
- prompt templates in `prompt/`,
- selected LLM backend and model.

Outputs:

- `results/esg_records.json`,
- possible T1/T2/T3 result files depending on selected pipeline steps.

## Workflow Steps

1. Select input mode.
2. Choose source document or manual input.
3. Select page ranges or page batches.
4. Choose model backend.
5. Choose one or more prompt templates.
6. Run extraction.
7. Parse JSON output.
8. Save raw and parsed outputs.

## Important Output Fields

Each ESG record may contain:

- `text`,
- `aspect`,
- `labels`,
- `esg`,
- `tone`,
- `sentiment`,
- `sentiment_score`,
- `reasoning`.

## Interpretation

This page creates the central artifact for most analysis: `results/esg_records.json`.

Because LLMs can produce schema drift, all outputs should be validated through revision analytics, ground-truth annotation, and metrics pages.

## Thesis Use

- Chapter III: T3 LLM extraction method.
- Chapter IV: extraction success and prompt comparison.
- Chapter V: prompt sensitivity and schema drift discussion.

