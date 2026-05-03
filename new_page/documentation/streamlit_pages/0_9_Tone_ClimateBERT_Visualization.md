# 0.9 Tone ClimateBERT Visualization

## Purpose

This page visualizes the relationship between extracted ESG disclosure tone and ClimateBERT-style labels. It is the first analytical dashboard for answering whether the current tone taxonomy is coherent with external climate-oriented labels.

The page supports the thesis argument that ESG disclosure should not be analyzed only by sentiment. It separates `commitment`, `action`, `outcome`, `none`, and `missing`, then compares those tones with ESG pillars, aspects, labels, and ClimateBERT remote outputs.

## Data Used

Primary input files:

- `results/esg_records.json`
- `results/climatebert_results.json`
- `docs/tone_climatebert_comparison.md`

Derived data shown by the page:

- Flattened ESG records built from every run and every record in `esg_records.json`.
- Parsed ClimateBERT remote rows from `climatebert_results.json`.

Important fields:

- `text`: extracted ESG disclosure sentence or paragraph.
- `tone`: LLM-assigned disclosure posture.
- `aspect`: ESG topic or ClimateBERT-style aspect.
- `esg`: environmental, social, governance, none, or missing.
- `labels`: ClimateBERT-style labels attached to the extracted record.
- `sentiment`: LLM-assigned sentiment.

## Workflow Steps

1. Load `esg_records.json`.
2. Flatten nested runs into a record-level table.
3. Normalize empty tone values as `missing`.
4. Extract source document names from target paths.
5. Load `climatebert_results.json`.
6. Parse ClimateBERT raw response text into model, label, score, and error rows.
7. Apply sidebar filters for tone, ESG pillar, prompt, and source document.
8. Render overview charts, comparison heatmaps, raw record tables, and documentation.

## Tabs

### Overview

Shows:

- filtered record count,
- number of source targets,
- number of runs,
- missing tone count,
- tone distribution,
- ESG pillar distribution,
- stacked tone-by-ESG chart.

Use this tab to describe the overall shape of the dataset.

### Tone Comparison

Shows:

- tone vs ClimateBERT-style label family heatmap,
- top aspect frequency,
- aspect-by-tone heatmap,
- interpretation guide.

Use this tab to support RQ3: comparison between existing tone results and ClimateBERT-style labels.

### ClimateBERT Runs

Shows parsed remote ClimateBERT outputs:

- number of runs,
- model count,
- model row count,
- error count,
- top labels and scores.

Important limitation: the raw remote ClimateBERT file currently contains only three inputs, so this tab is illustrative rather than a full benchmark.

### Records

Shows filtered record-level evidence. This is useful for auditability and qualitative inspection.

### Documentation

Renders `docs/tone_climatebert_comparison.md` inside the app.

## How To Interpret

Strong evidence:

- `commitment` often aligns with `climate-commitment`, `climate-d`, and `environmental-claims`.
- This supports the claim that the tone taxonomy has semantic validity.

Weaknesses:

- `missing` tone records still co-occur with climate-relevant labels.
- ClimateBERT remote runs are too few to claim full external validation.

## Thesis Use

- Chapter IV: tone distribution and ClimateBERT comparison results.
- Chapter V: interpretation of commitment dominance and missing-tone failures.
- Revision Aspect 6: moves the evaluation beyond purely descriptive narrative.

