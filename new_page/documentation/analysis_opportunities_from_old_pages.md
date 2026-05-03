# Analysis Opportunities From Legacy Benchmark Pages

This note maps the older Streamlit pages in `benchmarks/pages` to the current thesis documentation and revision feedback in `new_page/documentation`. The goal is to identify which analyses can be pulled into the current `new_page/pages` app and which thesis claims they support.

## 1. Ground-Truth Evaluation and Model Metrics

Legacy pages:

- `esg_dashboard_new_0_Metric_Analysis.py`
- `absa_metrics_comparison.py`
- `absa_metrics_comparison_mac.py`
- `ABSA_Model_Comparison.py`

Analysis to pull:

- Sentence-level alignment between ground truth and predictions.
- Accuracy, precision, recall, and weighted F1 for aspect, sentiment, and tone.
- Confusion matrices for tone and aspect errors.
- Dropped-row and alignment-coverage analysis.
- Error tables showing actual vs predicted labels.

Why it matters:

- Directly addresses the feedback that the thesis needs quantitative performance metrics.
- Supports Chapter 3.6, Benchmark and Ground Truth Design.
- Supports Chapter 4.2 and 4.3, RQ1-RQ4 results.
- Supports Aspect 5 and Aspect 6 by providing proof of achievement rather than descriptive counts.

Recommended new-page implementation:

- Extend `pages/1_1_Ground_Truth_Workbench.py` into a full evaluator once human annotations are filled.
- Add a dedicated page: `1_3_Ground_Truth_Metrics.py`.

## 2. ClimateBERT Model Validation

Legacy pages:

- `0_ClimateBERT_Commitment_Distribution.py`
- `0_0_ClimateBERT_4_Model_Analysis.py`
- `0_0_ClimateBERT_5_Model_Deep_Explorer.py`
- `0_0_ClimateBERT_6_Model_Overview_All.py`
- `0_0_ClimateBERT_7_Full_Model_Visualization.py`
- `0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py`

Analysis to pull:

- Predicted label distribution by ClimateBERT model.
- Confidence histogram and confidence box plots.
- True vs predicted comparisons if ground truth exists.
- Confusion matrix for ClimateBERT outputs.
- Global label distribution across models.
- Commitment distribution and confidence per model.
- Batch ClimateBERT validation against ground-truth records.

Why it matters:

- Directly responds to feedback that the ClimateBERT comparison is currently too descriptive.
- Enables percentage agreement and Cohen's kappa between LLM tone and ClimateBERT labels.
- Supports the need to run ClimateBERT over all 332 records, not only three remote inputs.

Recommended new-page implementation:

- Keep `pages/1_0_Revision_Analytics.py` for current proxy agreement.
- Add a future batch runner page: `1_4_ClimateBERT_Record_Batch.py`, which takes `silver_tone_ground_truth.csv` and calls ClimateBERT for every record.

## 3. Prompt Stability and Schema Drift Analysis

Legacy pages:

- `0_0_1_multiple_Prediction.py`
- `0_0_2_Batch_Prediction.py`
- `0_0_3_Model_Explorer.py`
- `0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py`

Analysis to pull:

- Per-prompt run count.
- JSON parse success rate.
- Record count per prompt.
- Missing tone rate per prompt.
- Schema drift rate per prompt.
- Field completion rate per prompt.
- Model-level stability comparison.

Why it matters:

- Directly responds to feedback about seven prompt templates needing statistical comparison.
- Supports Chapter 4.4, RQ5-RQ6.
- Helps justify whether zero-shot, few-shot, or chain-of-thought prompts are more stable.

Current status:

- Implemented in `pages/1_0_Revision_Analytics.py`.
- Artifacts generated in `results/revision_analysis/prompt_stability_summary.csv`.

Recommended next step:

- Add a significance test or bootstrap confidence intervals for prompt differences if record volume is sufficient.

## 4. Tone, Aspect, and Sentiment Distribution

Legacy pages:

- `esg_dashboard_new_Tone_Distribution.py`
- `esg_dashboard_new_Data Distribution.py`
- `esg_dashboard_new_Data_New_Distribution.py`
- `esg_dashboard_new_Distribution Document.py`
- `esg_dashboard_new_01_Aspects_Raw.py`
- `esg_dashboard_new_02_Aspects_Clustered.py`
- `esg_dashboard_new_03_Aspect_Comparison.py`

Analysis to pull:

- Tone distribution overall and by source document.
- Aspect distribution before and after clustering.
- Sentiment distribution.
- Aspect-sentiment-tone cross-tabulation.
- Document-level ESG disclosure profile.
- Minimum-tone or underrepresented-tone analysis.

Why it matters:

- Supports Chapter 4 empirical results.
- Supports feedback about improving the outline with actual data rather than repeated methodology scaffolding.
- Provides evidence for the dominance of commitment tone and the underrepresentation of social disclosures.

Current status:

- Partly implemented in `pages/0_9_Tone_ClimateBERT_Visualization.py`.
- Partly implemented in `pages/1_0_Revision_Analytics.py`.

Recommended next step:

- Add document-level distribution charts that compare companies, not only global counts.

## 5. Sankey Flow and Disclosure Path Analysis

Legacy pages:

- `esg_dashboard_new_Sankey.py`

Analysis to pull:

- Sankey flow from aspect to sentiment to tone.
- Sankey flow from ESG pillar to aspect to tone.
- Sankey flow from company to ESG pillar to tone.
- Optional flow from prompt to tone to schema drift.

Why it matters:

- Improves layout and interpretability.
- Provides a visually strong Chapter 4 figure.
- Supports thesis claims about integrated ESG aspect, sentiment, and tone analysis.

Recommended new-page implementation:

- Add Sankey chart to `pages/0_9_Tone_ClimateBERT_Visualization.py` or create `1_5_ESG_Flow_Sankey.py`.

## 6. Aspect Clustering and Ontology Coverage

Legacy pages:

- `zz_aspect_clusters.py`
- `esg_dashboard_new_02_Aspects_Clustered.py`
- `esg_dashboard_new_03_Aspect_Comparison.py`
- `absa_ontology_all.py`
- `absa_ontology_all_new_notes.py`
- `absa_ontology_3_deep_model.py`

Analysis to pull:

- Raw aspect to clustered aspect mapping.
- Aspect cluster frequency.
- Ontology coverage rate.
- Unmapped aspect list.
- Ontology path traversal from raw text to canonical ESG node.
- Cluster-level tone distribution.

Why it matters:

- Directly addresses the feedback that ontology claims need proof.
- Supports Aspect 1 and Aspect 5 by showing machine-readable ontology coverage.
- Supports Chapter 3.4 Model Design and Chapter 4.5 Explainability.

Current status:

- Basic ontology coverage implemented in `pages/1_0_Revision_Analytics.py`.
- Machine-readable ontology artifact generated at `results/revision_analysis/ontology.json`.

Recommended next step:

- Build an ontology-path visualization page with a tree or graph view.

## 7. Greenwashing Index and Rhetoric-to-Results Analysis

Legacy pages:

- No exact old equivalent, but the tone distribution and Sankey pages provide the raw pattern.

Analysis to pull:

- Company-level commitment-to-outcome ratio.
- Commitment share vs outcome share.
- Risk-tier assignment such as low, medium, high rhetoric-to-results imbalance.
- Comparison across sources such as BeFa, VKTR, PTBA, ICR, and GTRA.

Why it matters:

- Directly addresses the strongest revision request: actually compute the greenwashing index.
- Supports Aspect 7, Significance of Results.
- Provides a regulator/investor-facing result.

Current status:

- Implemented in `pages/1_0_Revision_Analytics.py`.
- Artifact: `results/revision_analysis/greenwashing_index_by_company.csv`.

Recommended next step:

- Add external validation with ESG scores or controversy data if available.

## 8. OCR Quality and Layout Error Analysis

Legacy pages:

- Not directly implemented in the old pages, but OCR/document-distribution pages imply document-level traceability.

Analysis to pull/build:

- Character Error Rate (CER).
- Word Error Rate (WER).
- OCR quality by layout type: narrative, table, bilingual columns, infographic, mixed.
- Relationship between OCR quality and missing tone/schema drift.
- Layout-induced extraction error analysis.

Why it matters:

- Directly addresses the feedback that OCR quality must be quantified.
- Supports Contribution 1, PDF-to-structured-ESG pipeline.
- Supports Chapter 3.3 and Chapter 4.2.

Current status:

- Workbench implemented in `pages/1_2_OCR_Quality_Workbench.py`.
- Requires manually corrected reference snippets for true CER/WER.

Recommended next step:

- Annotate 20-30 page snippets across layout types.

## 9. Linguistic Failure-Mode Analysis

Legacy pages:

- The old pages do not explicitly implement this, but ABSA and tone pages supply the necessary predictions.

Analysis to pull/build:

- Missing tone records by language.
- Schema drift by language and prompt.
- Trigger frequency for commitment/action/outcome markers.
- Hedging, passive voice, regulatory Indonesian terms, and long sentence markers.
- Cross-lingual lexical drift between Indonesian and English ESG phrasing.

Why it matters:

- Directly responds to Aspect 9, Language.
- Turns language revision feedback into quantitative analysis.
- Supports a stronger Chapter 5 discussion.

Current status:

- Implemented in `pages/1_0_Revision_Analytics.py`.
- Artifacts: `failure_modes.csv`, `failure_mode_counts.csv`, `lexical_triggers.csv`, `lexical_trigger_counts.csv`.

Recommended next step:

- Add a written interpretation section using the failure-mode table as evidence.

## 10. Recommended Build Priority

Highest impact for revision:

1. `1_3_Ground_Truth_Metrics.py`: formal metrics from human annotations.
2. `1_4_ClimateBERT_Record_Batch.py`: run ClimateBERT over all extracted records.
3. `1_5_ESG_Flow_Sankey.py`: aspect -> sentiment -> tone and company -> ESG -> tone flows.
4. Ontology path viewer: raw sentence -> aspect -> ontology path.
5. OCR sample campaign using `1_2_OCR_Quality_Workbench.py`.

Already implemented in `new_page/pages`:

- `0_9_Tone_ClimateBERT_Visualization.py`
- `1_0_Revision_Analytics.py`
- `1_1_Ground_Truth_Workbench.py`
- `1_2_OCR_Quality_Workbench.py`

