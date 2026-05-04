# 1_8_Ground_Truth_Output_Visualizer.py

## Purpose

This Streamlit page visualizes the ground-truth output used to evaluate tone classification and compare the existing ESG tone results against a validation target. It is designed to look and behave like the ClimateBERT result visualizer: load a saved output, filter it, inspect distributions, check coverage, review disagreements, and export rows for manual follow-up.

The page is useful at two stages of the research:

1. Before human annotation is complete, it uses `silver_tone_ground_truth` as a proxy label so the researcher can preview likely agreement and identify risky cases.
2. After human annotation is complete, it uses `ground_truth_tone` as the evaluation label and becomes a formal error-analysis dashboard.

## Data Used

The page loads the first available file from this priority order:

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/pilot_ground_truth_seed.csv`
- `results/revision_analysis/silver_tone_ground_truth.csv`

It also reads the older raw files for audit inspection:

- `results/ground_truth.json`
- `results/absa_results_ground_truth.json`

The core columns are:

- `text`: the ESG sentence or evidence passage being evaluated.
- `tone_pred`: the existing tone output from the LLM/ABSA extraction pipeline.
- `silver_tone_ground_truth`: an automatically constructed reference label used as a weak or proxy ground truth.
- `ground_truth_tone`: the human-validated tone label, which should be filled during annotation.
- `ground_truth_esg` and `ground_truth_aspect`: optional human validation fields for ESG pillar and aspect.
- `needs_human_review`: flag for records that should be checked manually.
- `schema_drift`: flag for records where output structure may have changed or become unreliable.
- `review_status`, `review_notes`, and `annotator`: annotation workflow fields.

## Workflow

1. Open the page from the Streamlit sidebar.
2. Leave the default CSV selected, or upload another ground-truth CSV.
3. Use sidebar filters to focus on a company, source report, prompt, model, language, ESG pillar, predicted tone, silver tone, human tone, or review status.
4. Keep **Use silver tone where human tone is blank** enabled for preliminary analysis.
5. Disable that option when reporting final human-labeled metrics.
6. Review the Summary tab to understand the label distribution.
7. Review the Coverage tab to see which groups still need manual annotation.
8. Review the Agreement tab to compare predicted tone against human or silver tone.
9. Review the Review Queue tab to resolve missing labels, schema drift, and disagreements.
10. Export filtered rows, disagreements, or review queues as CSV files when needed.

## Tabs

### Summary

The Summary tab explains what the ground-truth output contains. It visualizes:

- predicted tone distribution;
- human or silver tone distribution;
- language distribution;
- ESG pillar distribution;
- whether the comparison label comes from human annotation or the silver proxy.

This tab answers whether the evaluation sample is balanced or dominated by particular labels, languages, companies, or ESG pillars. If the predicted tone distribution is dominated by `commitment`, for example, the thesis can discuss whether the source reports mostly express future-facing sustainability claims rather than measurable outcomes.

### Coverage

The Coverage tab shows annotation coverage across groups such as company, prompt, model, predicted tone, language, ESG pillar, and source target. It separates rows into:

- `annotated`;
- `not annotated`;
- `coverage_pct`.

This is important because accuracy, F1, and Cohen's kappa are only meaningful if the annotated sample covers the relevant strata of the research. Low coverage for a prompt, company, or tone class means that group should be prioritized before making final claims.

### Agreement

The Agreement tab compares `tone_pred` to the selected comparison label:

- human tone when `ground_truth_tone` exists;
- silver tone when the human label is blank and the proxy option is enabled.

It reports:

- comparable row count;
- percentage agreement;
- Cohen's kappa;
- disagreement count;
- confusion matrix;
- downloadable disagreement table.

The confusion matrix shows where the current pipeline confuses tone categories. For example, if many `outcome` rows are predicted as `action`, that suggests the model recognizes activity but misses measurable result language.

### Review Queue

The Review Queue tab collects records that are risky for final evaluation. A row appears here when it has:

- missing human tone;
- `needs_human_review = True`;
- `schema_drift = True`;
- disagreement between predicted tone and comparison tone.

This tab operationalizes the revision feedback about failure-mode analysis. It turns abstract validity concerns into a concrete annotation queue.

### Records

The Records tab is the audit table. It shows the sentence text, source metadata, model, prompt, predicted tone, silver tone, human tone, ESG labels, review flags, reasoning, and notes.

This table is useful when writing examples in the report because each row preserves the evidence text and the model reasoning that produced the original tone label.

### Raw Outputs

The Raw Outputs tab displays `ground_truth.json` and `absa_results_ground_truth.json`. These files are not the preferred final evaluation format, but they preserve earlier experiment outputs and support auditability.

## Interpretation for the Research Questions

This page supports the research questions by showing whether the extracted ESG tone results can be validated against a ground-truth layer.

- For the tone-comparison question, the Agreement tab shows how often the existing tone result matches a human or proxy label.
- For the ClimateBERT comparison question, the same ground-truth labels can be used as the reference layer when comparing ClimateBERT outputs against the existing LLM/ABSA outputs.
- For the methodology question, the Coverage tab demonstrates whether the validation sample is broad enough across models, prompts, companies, and tone categories.
- For the error-analysis question, the Review Queue tab identifies missing labels, schema drift, and tone disagreements that should be discussed as limitations or corrected in annotation.

## What It Means

The ground-truth output is not just another prediction table. It is the evaluation bridge between the generated ESG tone results and the research claims. The page separates three different label roles:

- `tone_pred` is the system output being evaluated.
- `silver_tone_ground_truth` is an automatically created reference label used for preliminary inspection.
- `ground_truth_tone` is the human-validated label that should be used for final metrics.

When human labels are missing, the page can still reveal likely weak points by comparing against the silver proxy. However, final thesis claims should rely on human-filled `ground_truth_tone` and should report coverage, agreement, Cohen's kappa, and remaining limitations.
