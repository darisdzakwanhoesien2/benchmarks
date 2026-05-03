# 1.5 ESG Flow Sankey

## Purpose

This page visualizes ESG disclosure flows using Sankey diagrams. It adapts the legacy Sankey concept to the current extracted records.

The page helps explain how source documents flow into ESG pillars, aspects, tones, prompts, and review issues.

## Data Used

Input:

- `results/revision_analysis/silver_tone_ground_truth.csv`

Main fields:

- `company`,
- `esg`,
- `aspect`,
- `tone_pred`,
- `prompt`,
- `needs_human_review`,
- `schema_drift`.

## Workflow Steps

1. Load silver records.
2. Filter by company/source, tone, and minimum record count.
3. Build grouped flow tables.
4. Render Sankey diagrams.
5. Display raw grouped flow data and filtered records.

## Sankey Views

### Company -> ESG -> Tone

Shows which companies/sources emphasize environmental, social, governance, none, or missing records, and how those records are distributed by tone.

### ESG -> Aspect -> Tone

Shows how ESG pillars map into aspects and then into disclosure tone.

This is useful for showing whether environmental disclosures are mostly commitments or outcomes.

### Prompt -> Tone -> Issue

Shows whether specific prompt templates are associated with clean records, missing tone, or schema drift.

## Interpretation

This page turns aggregate tables into a visual narrative. It is especially useful for Chapter IV figures and for explaining how disclosure patterns differ by company/source.

## Thesis Use

- Chapter IV: visual results.
- Chapter V: interpretation of company-level and prompt-level patterns.
- Layout improvement: provides professional figure-ready flows.

