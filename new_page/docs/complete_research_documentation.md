# Complete Research Documentation: ESG Disclosure Tone Analysis and ClimateBERT Comparison

https://claude.ai/chat/fcd4ed44-4c2a-4311-8679-c0094e508a53

## 1. Executive Summary

This research project builds an end-to-end ESG disclosure analysis pipeline for sustainability reports. It converts PDF reports into analyzable text, extracts structured ESG records, classifies ESG aspect, sentiment, and disclosure tone, and compares the extracted tone patterns with ClimateBERT-style climate labels.

The core research problem is that sustainability reports often contain many positive ESG statements, but not all statements have the same evidentiary value. A company may state a future target, describe an ongoing action, or report a measurable outcome. These are materially different disclosure types. This project therefore focuses on tone categories:

- `commitment`: promise, plan, target, intent, or future-oriented claim.
- `action`: activity, implementation, program, policy, control, or process being performed.
- `outcome`: achieved result, measured performance, reduction, completion, or reported impact.
- `none`: no meaningful ESG disclosure tone.
- `missing`: blank or unparsed tone output that needs cleanup.

ClimateBERT is used as a comparison lens. It does not directly replace the tone classifier, because ClimateBERT models usually classify climate relevance, climate commitment, environmental claims, specificity, TCFD category, sentiment, or related climate tasks. In this project, ClimateBERT-style labels help validate whether extracted tone categories are semantically plausible.

## 2. Research Aim

The aim of this research is to design and evaluate a reproducible pipeline for identifying ESG statements in sustainability reports and interpreting their disclosure posture. The pipeline asks not only "what ESG topic is being discussed?" but also "is the company making a promise, describing an action, or reporting an outcome?"

## 3. Research Questions

RQ1. How can sustainability reports be transformed from PDF or scanned document format into structured ESG evidence?

RQ2. How can ESG statements be categorized by aspect, ESG pillar, sentiment, and disclosure tone?

RQ3. How do the existing tone extraction results compare with ClimateBERT-style climate labels?

RQ4. Can the comparison reveal possible weaknesses in the extraction output, such as missing tones, generic labels, or mismatches between climate relevance and disclosure tone?

RQ5. What documentation and visualization tools are needed to make the research auditable and reproducible?

## 4. Research Contribution

This project contributes:

1. An end-to-end ESG report processing workflow from source documents to structured ESG records.
2. A tone-aware ESG disclosure taxonomy that separates commitments, actions, and outcomes.
3. A comparison method that uses ClimateBERT-style labels as external semantic evidence.
4. Interactive Streamlit visualizations for exploring tone distributions, ESG pillars, aspects, and ClimateBERT outputs.
5. Reproducible artifacts in JSON, CSV, PNG, and markdown form.
6. A foundation for later formal benchmarking using manually labeled ground truth.

## 5. Data Sources

The workspace contains sustainability reports and OCR-derived datasets under:

- `data/thesis_pdf/`
- `data/thesis_dataset/`

The analyzed result files are:

| File | Role |
|---|---|
| `results/esg_records.json` | Main extracted ESG record dataset. |
| `results/climatebert_results.json` | Raw remote ClimateBERT sample outputs. |
| `results/visualizations/tone_records_flat.csv` | Flattened extracted ESG records. |
| `results/visualizations/climatebert_remote_flat.csv` | Flattened ClimateBERT remote outputs. |
| `results/visualizations/tone_climatebert_label_crosstab.csv` | Cross-tabulation between tone and ClimateBERT-style label families. |
| `docs/tone_climatebert_comparison.md` | Focused documentation for the tone and ClimateBERT comparison. |

Current analyzed data snapshot:

| Metric | Value |
|---|---:|
| ESG extraction runs | 110 |
| Successful ESG extraction runs | 110 |
| Extracted ESG records | 332 |
| Source targets represented in extracted records | 40 |
| Prompt templates used | 7 |
| LLM models used | 2 |
| Remote ClimateBERT runs | 3 |
| Parsed ClimateBERT model-level rows | 48 |
| ClimateBERT model error rows | 9 |

The main extracted ESG records come from `results/esg_records.json`. The raw ClimateBERT sample is much smaller, so it should not be described as a full ground-truth benchmark. It is currently best interpreted as a validation sample.

## 6. System Architecture

The research system is organized into five layers.

### 6.1 Document Ingestion and OCR

Relevant files:

- `pages/Bulk_OCR.py`
- `logs/bulk_ocr_log.json`
- `data/thesis_dataset/<document>/pages/`
- `data/thesis_dataset/<document>/images/`

This layer converts PDF and image-based sustainability reports into markdown pages and extracted image files. The OCR outputs preserve page-level structure so later analysis can trace ESG statements back to report context.

### 6.2 Text Processing and ABSA

Relevant files:

- `code/rule_based.py`
- `code/classical_ml.py`
- `code/hybrid_model.py`
- `code/explainability.py`
- `code/utils.py`
- `code/lexicons.py`

This layer performs aspect-based sentiment analysis and tone prediction. It supports:

- rule-based ESG lexicon classification,
- classical machine learning baselines,
- hybrid ontology-aware classification,
- explainability outputs,
- ontology alignment,
- greenwashing-style exploratory metrics.

### 6.3 LLM-Based ESG Record Extraction

Relevant files:

- `pages/llm_processing.py`
- `prompt/*.md`
- `results/esg_records.json`

The LLM extraction layer produces structured records with fields such as:

- `text`
- `aspect`
- `labels`
- `esg`
- `tone`
- `sentiment`
- `sentiment_score`
- `reasoning`

The prompt templates include zero-shot, few-shot, and chain-of-thought variants in English and Indonesian.

Current prompt distribution in `results/esg_records.json`:

| Prompt | Runs |
|---|---:|
| `data.md` | 20 |
| `tone_zero_shot_indonesian.md` | 16 |
| `tone_chain_of_thought_english.md` | 16 |
| `tone_chain_of_thought_indonesian.md` | 15 |
| `tone_few_shot_english.md` | 15 |
| `tone_zero_shot_english.md` | 14 |
| `tone_few_shot_indonesian.md` | 14 |

Current model distribution:

| Model | Runs |
|---|---:|
| `arcee-ai/trinity-large-preview:free` | 90 |
| `openai/gpt-oss-120b:free` | 20 |

### 6.4 ClimateBERT Comparison

Relevant files:

- `hidden_pages/0_0_1_climatebert_combine.py`
- `hidden_pages/0_0_2_climatebert_dashboard.py`
- `results/climatebert_results.json`
- `results/visualizations/climatebert_remote_flat.csv`

ClimateBERT outputs are parsed into model, label, and score rows. The currently available remote sample includes models/tasks such as:

- `climate-detector`
- `climate-commitment`
- `climate-specificity`
- `climate-sentiment`
- `climate-tcfd`
- `environmental-claims`
- `netzero-reduction`
- `renewable`
- `transition-physical`

Several remote ClimateBERT models returned configuration errors, especially models whose Hugging Face configs were not recognized by the remote space. These errors are preserved as part of the audit trail.

### 6.5 Visualization and Documentation

Relevant files:

- `code/visualize_tone_climatebert.py`
- `pages/0_9_Tone_ClimateBERT_Visualization.py`
- `docs/tone_climatebert_comparison.md`
- `docs/complete_research_documentation.md`
- `results/visualizations/`

The visualization layer provides both static and interactive outputs.

Static outputs:

- `results/visualizations/tone_distribution.png`
- `results/visualizations/esg_by_tone.png`
- `results/visualizations/climatebert_label_by_tone.png`
- `results/visualizations/aspect_by_tone_heatmap.png`
- `results/visualizations/climatebert_remote_top_scores.png`

Interactive Streamlit page:

- `pages/0_9_Tone_ClimateBERT_Visualization.py`

Run with:

```bash
streamlit run app.py --server.port 8590
```

Then open:

```text
http://localhost:8590
```

## 7. Methodology

### 7.1 Preprocessing

Reports are converted into markdown pages. Each page or page batch can then be selected for model processing. The markdown format helps preserve headings, tables, and paragraph boundaries better than raw plain text.

### 7.2 ESG Record Extraction

LLM prompts ask the model to extract structured ESG records. Each record represents a relevant ESG statement or paragraph and includes classification fields. The design is intentionally record-based because sustainability reports often mix environmental, social, governance, and financial statements in the same page.

### 7.3 Tone Classification

Tone is the main analytical construct in this research.

| Tone | Meaning | Typical evidence |
|---|---|---|
| `commitment` | Future intent, pledge, plan, target, aim, or strategy. | "will reduce emissions", "aims to achieve", "committed to". |
| `action` | Concrete activity or implementation. | "implemented", "conducted training", "established policy". |
| `outcome` | Reported achievement or measurable result. | "reduced by 20%", "achieved certification", "completed". |
| `none` | No meaningful ESG tone. | Generic, irrelevant, or non-ESG content. |
| `missing` | Empty or unparsed tone. | Extraction quality issue. |

This distinction is important because a report dominated by commitments may communicate ambition, while a report dominated by outcomes may provide stronger evidence of realized performance.

### 7.4 ClimateBERT-Style Label Comparison

ClimateBERT-style labels are used to interpret whether the extracted tone is semantically plausible.

Examples:

- A `commitment` tone should often align with `climate-commitment`, `netzero-reduction`, or `environmental-claims`.
- An `action` tone should often align with governance, implementation, or climate-action labels.
- An `outcome` tone should ideally align with reported metrics, performance, or concrete result language.
- A `none` tone should mostly align with non-climate or generic labels.

This is not yet a formal accuracy test because the ClimateBERT outputs are not available for every extracted record and do not provide manual ground-truth tone labels.

### 7.5 Visualization

The generated visualizations answer:

- What tones are most common?
- Which ESG pillars dominate each tone?
- Which ClimateBERT-style labels co-occur with each tone?
- Which aspects are associated with commitments, actions, outcomes, and none?
- What do the remote ClimateBERT model outputs look like?

## 8. Current Empirical Results

### 8.1 Tone Distribution

| Tone | Count |
|---|---:|
| `commitment` | 115 |
| `missing` | 61 |
| `action` | 58 |
| `outcome` | 50 |
| `none` | 48 |

Interpretation:

The most common non-missing tone is `commitment`. This suggests many extracted ESG statements describe plans, goals, commitments, or future-oriented sustainability narratives. That is common in sustainability reporting, but it also means the dataset should be evaluated carefully to distinguish ambition from actual performance.

The `missing` count is also material. There are 61 records with blank or missing tone values, so the extraction pipeline needs cleanup before strong quantitative claims are made.

### 8.2 ESG Pillar Distribution

| ESG pillar | Count |
|---|---:|
| `e` | 179 |
| `g` | 121 |
| `none` | 27 |
| `s` | 4 |
| `missing` | 1 |

Interpretation:

The dataset is dominated by environmental and governance records. Social records are underrepresented in the current extracted data. This may reflect the selected pages, prompt behavior, or model bias toward climate and governance topics.

### 8.3 Sentiment Distribution

| Sentiment | Count |
|---|---:|
| `neutral` | 210 |
| `positive` | 67 |
| `none` | 24 |
| `commitment` | 18 |
| `negative` | 11 |
| `missing` | 2 |

Interpretation:

Most records are neutral. This is plausible because ESG disclosures often describe policies, programs, metrics, and governance structures in formal reporting language. The presence of `commitment` in the sentiment field suggests some output schema drift, where the model placed tone-like information into the sentiment field. That should be cleaned in future experiments.

### 8.4 Tone by ESG Pillar

| Tone | E | S | G | None | Missing |
|---|---:|---:|---:|---:|---:|
| `action` | 33 | 0 | 25 | 0 | 0 |
| `commitment` | 91 | 0 | 24 | 0 | 0 |
| `missing` | 23 | 2 | 31 | 4 | 1 |
| `none` | 4 | 0 | 21 | 23 | 0 |
| `outcome` | 28 | 2 | 20 | 0 | 0 |

Interpretation:

Environmental records dominate commitment, action, and outcome categories. Governance appears strongly in action, outcome, none, and missing categories. The concentration of `missing` tone under governance suggests governance disclosures may need clearer prompt instructions or post-processing rules.

### 8.5 Tone vs ClimateBERT-Style Labels

| Tone | Key co-occurring label patterns |
|---|---|
| `commitment` | `climate-commitment` = 91, `climate-d` = 57, `environmental-claims` = 48 |
| `action` | `governance` = 25, `climate-d` = 23, `other` = 22 |
| `outcome` | `other` = 36, `governance` = 20, `climate-d` = 19 |
| `none` | `none` = 24, `governance` = 21, `climate-d` = 2 |
| `missing` | `other` = 49, `climate-commitment` = 22, `environmental-claims` = 21 |

Interpretation:

The strongest positive sign is that `commitment` aligns heavily with `climate-commitment`. This suggests the extraction output is semantically coherent for many commitment records.

The main concern is that `missing` tone still co-occurs with climate-relevant labels such as `climate-commitment` and `environmental-claims`. These are likely review candidates, because climate-relevant statements should usually have a meaningful disclosure tone.

### 8.6 Aspect by Tone

Key patterns from the aspect-tone crosstab:

| Aspect | Main tone pattern |
|---|---|
| `climate-detection` | Mostly `commitment`, followed by `outcome` and `action`. |
| `climate-commitment` | Entirely `commitment` in the current table. |
| `governance` | Spread across `action`, `commitment`, `none`, and `outcome`. |
| `none` | Entirely `none`. |
| `missing` | Entirely `missing`. |
| `environmental-claims` | Mostly `action` and `commitment`, with fewer `outcome`. |

Interpretation:

Climate commitment labels are behaving as expected. Governance is more ambiguous because governance disclosures can be policies, procedures, structures, outcomes, or generic statements. This makes governance a good target for additional manual annotation.

## 9. ClimateBERT Remote Sample Findings

The raw remote ClimateBERT sample contains only three inputs, so findings are illustrative rather than conclusive.

The first sample, which discusses media industry audience share, received:

- `climate-detector`: `no` with 0.99
- `environmental-claims`: `no` with 1.00
- `netzero-reduction`: `none` with 1.00
- `renewable`: `Not about renewables` with 1.00
- `climate-commitment`: `yes` with 0.92

Interpretation:

Most labels correctly identify the text as not strongly environmental or renewable-related. The `climate-commitment` result appears less intuitive for that example, which shows why ClimateBERT outputs should be treated as comparison evidence rather than final ground truth.

Across the three samples, some ClimateBERT tasks returned useful scores and some returned model configuration errors. The system preserves both successes and errors for transparency.

## 10. Dashboard Documentation

The Streamlit dashboard for this research is:

```text
pages/0_9_Tone_ClimateBERT_Visualization.py
```

It contains five tabs.

### 10.1 Overview

Shows:

- filtered record count,
- source target count,
- run count,
- missing tone count,
- tone distribution,
- ESG pillar distribution,
- stacked tone-by-ESG chart.

Use this tab to understand the overall shape of the extracted records.

### 10.2 Tone Comparison

Shows:

- tone vs ClimateBERT-style label family heatmap,
- top aspect frequency,
- aspect-by-tone heatmap,
- interpretation guide.

Use this tab to inspect whether tone assignments make sense given climate and ESG labels.

### 10.3 ClimateBERT Runs

Shows:

- remote ClimateBERT run count,
- model count,
- model row count,
- error count,
- top label per model and run,
- parsed raw rows,
- model errors.

Use this tab to inspect the small ClimateBERT sample and debug remote model behavior.

### 10.4 Records

Shows the filtered ESG records with:

- timestamp,
- source target,
- prompt,
- tone,
- ESG pillar,
- aspect,
- sentiment,
- labels,
- text,
- reasoning.

It also provides CSV download for the current filtered table.

### 10.5 Documentation

Renders:

```text
docs/tone_climatebert_comparison.md
```

Use this tab to read the shorter comparison note inside the app.

## 11. Reproducibility Guide

### 11.1 Regenerate Static Visualizations

Run:

```bash
python3 code/visualize_tone_climatebert.py
```

This writes:

- `results/visualizations/tone_records_flat.csv`
- `results/visualizations/climatebert_remote_flat.csv`
- `results/visualizations/tone_climatebert_label_crosstab.csv`
- `results/visualizations/tone_distribution.png`
- `results/visualizations/esg_by_tone.png`
- `results/visualizations/climatebert_label_by_tone.png`
- `results/visualizations/aspect_by_tone_heatmap.png`
- `results/visualizations/climatebert_remote_top_scores.png`
- `docs/tone_climatebert_comparison.md`

### 11.2 Launch Dashboard

Run:

```bash
streamlit run app.py --server.port 8590
```

Open:

```text
http://localhost:8590
```

Select:

```text
0 9 Tone ClimateBERT Visualization
```

### 11.3 Traceability

The dashboard and generated files trace back to:

```text
results/esg_records.json
results/climatebert_results.json
```

This means the analysis can be rerun whenever those result files change.

## 12. Limitations

1. The ClimateBERT sample is small.
   The current raw ClimateBERT result file contains only three remote inputs, so it cannot support full benchmark claims.

2. ClimateBERT is not a tone-ground-truth model.
   It helps identify climate relevance and related labels, but it does not directly label `commitment`, `action`, and `outcome` as a human annotator would.

3. The extracted tone dataset has missing values.
   There are 61 missing tone records. These must be cleaned or reviewed before formal evaluation.

4. Some schema drift exists.
   Some sentiment fields contain tone-like values, such as `commitment`. This indicates that prompt/schema validation should be strengthened.

5. Social disclosures are underrepresented.
   The current extracted records contain only four `s` records. This limits social-pillar conclusions.

6. LLM extraction may be prompt-sensitive.
   Seven prompts were used, and different prompts can produce different record counts and category choices.

7. No expert-labeled full ground truth exists yet.
   The project has extracted records and model outputs, but not a complete manually adjudicated benchmark table.

## 13. Recommended Ground-Truth Benchmark Design

To convert this from exploratory analysis into a formal evaluation, create a table where each row is one text unit.

Recommended columns:

| Column | Purpose |
|---|---|
| `record_id` | Stable unique identifier. |
| `source_document` | Report/document source. |
| `page_or_batch` | Page or batch reference. |
| `text` | ESG statement text. |
| `aspect_pred` | Model-predicted ESG aspect. |
| `aspect_ground_truth` | Human-labeled aspect. |
| `esg_pred` | Model-predicted ESG pillar. |
| `esg_ground_truth` | Human-labeled ESG pillar. |
| `tone_pred` | Model-predicted tone. |
| `tone_ground_truth` | Human-labeled tone. |
| `sentiment_pred` | Model-predicted sentiment. |
| `sentiment_ground_truth` | Human-labeled sentiment. |
| `climatebert_labels` | ClimateBERT model outputs for the same text. |
| `review_notes` | Human explanation or uncertainty notes. |

Sampling strategy:

1. Stratify records by tone: commitment, action, outcome, none, missing.
2. Stratify records by ESG pillar: E, S, G.
3. Include ambiguous cases where ClimateBERT labels and tone disagree.
4. Include multiple documents and industries.
5. Use at least two annotators for a subset to measure agreement.

Metrics to compute:

- precision, recall, and F1 for tone,
- confusion matrix for `tone_pred` vs `tone_ground_truth`,
- agreement rate by ESG pillar,
- error rate by prompt template,
- error rate by source document,
- ClimateBERT-label correlation with tone,
- inter-annotator agreement for human labels.

## 14. Research Interpretation

The current results suggest that the extraction pipeline can identify meaningful ESG disclosures and that the tone taxonomy is analytically useful. The strongest pattern is the alignment between `commitment` tone and `climate-commitment` labels. This indicates that the model often recognizes future-oriented climate or environmental statements correctly.

However, the results also show areas requiring improvement. Missing tone values are too frequent, governance records are semantically broad, and the ClimateBERT remote sample is too small to function as ground truth. Therefore, the current research stage should be described as exploratory and diagnostic rather than a final validated benchmark.

The main research value is the framework: it separates ESG topic, ESG pillar, sentiment, disclosure tone, and ClimateBERT-style climate evidence. This makes the analysis richer than generic sentiment analysis or document-level ESG scoring.

## 15. Conclusion

This project provides a working research prototype for ESG disclosure analysis in sustainability reports. It supports OCR-based document processing, LLM-based ESG record extraction, ABSA-style interpretation, ClimateBERT comparison, visualization, and documentation.

The current empirical results show that commitment-oriented ESG language is common in the extracted dataset, especially in environmental records. The ClimateBERT-style comparison supports the plausibility of many commitment labels, while also revealing missing-tone and schema-quality issues that should be addressed before formal evaluation.

The next research step is to build a manually labeled ground-truth benchmark and run ClimateBERT over the same exact text records. That would allow the project to move from exploratory visualization to formal model evaluation.

