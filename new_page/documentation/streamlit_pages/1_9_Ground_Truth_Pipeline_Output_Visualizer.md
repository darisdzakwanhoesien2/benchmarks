# 1_9_Ground_Truth_Pipeline_Output_Visualizer.py

## Purpose

This page visualizes the saved output from the `ground_truth.py` pipeline page. The pipeline page shows a live checklist while it runs, but the checklist is difficult to interpret once many records, models, and prompts are involved. This visualizer turns those outputs into charts, tables, failure audits, and exportable CSV files.

It is designed for the output shown during the ground-truth run:

- T1 model execution status;
- successful and failed local model runs;
- ClimateBERT or local model prediction labels;
- T2 rule-based and hybrid ESG predictions;
- ontology alignment;
- greenwashing index;
- rule-based vs hybrid tone agreement.

## Data Used

The page reads the saved result files in `results/`:

- `results/t1_results.jsonl` when available;
- `results/t1_results.json` as a fallback;
- `results/t2_results.jsonl` when available;
- `results/t2_results.json` as a fallback.

The JSONL files are produced by the resumable pipeline. The JSON files are older combined outputs. The visualizer supports both formats.

## T1 Output Meaning

T1 is the model-classification layer. In the current pipeline, T1 can use either the ClimateBERT API or local Hugging Face model folders. Each row represents one text record multiplied by one selected model.

Important fields:

- `label`: the source record identifier, usually report/batch/record.
- `model`: the ClimateBERT or local model name.
- `backend`: whether the run used API models or local models.
- `success`: whether the model produced a usable prediction.
- `error`: model-load, inference, or compatibility error.
- `prediction_label`: normalized label extracted from the model output.
- `prediction_score`: confidence score when available.
- `text`: the evidence text that was classified.

The screenshot shows a common T1 use case: many local models run successfully, while some model folders fail because the checkpoint cannot be loaded as a text-classification model. The T1 failure tab makes those failures countable and auditable.

## T2 Output Meaning

T2 is the ESG interpretation layer. It combines rule-based analysis and the hybrid ESG model.

Important fields:

- `rule_aspects`: aspects detected by the rule-based system.
- `rule_polarity`: rule-based sentiment or polarity.
- `rule_tone`: rule-based tone.
- `tone_pred`: hybrid tone prediction.
- `sentiment_pred`: hybrid sentiment prediction.
- `tone_score`: hybrid tone confidence score.
- `ontology_alignment`: how well the sentence aligns with the ESG ontology.
- `ontology_path`: the ontology path assigned to the text.
- `greenwashing_index`: a proxy signal for commitment-heavy or weakly evidenced sustainability language.
- `ontology_consistency`: whether the assigned aspect and ontology path are structurally consistent.

## Workflow

1. Run the ground-truth pipeline page.
2. Wait for the pipeline to write `t1_results` and/or `t2_results` files.
3. Open this visualizer page.
4. Confirm the file paths in the sidebar.
5. Use filters for T1 model, backend, prediction label, status, T2 tone, sentiment, section, and ontology path.
6. Inspect T1 status and failure charts.
7. Inspect T2 tone, sentiment, ontology, and greenwashing charts.
8. Use the comparisons tab to identify rule-based vs hybrid disagreements.
9. Export filtered T1 or T2 CSV files for documentation and further analysis.

## Tabs

### T1 Model Results

This tab shows:

- T1 success vs failure counts;
- prediction-label distribution;
- success/failure by model;
- prediction-score distribution.

Use it to answer whether the selected ClimateBERT/local models are producing usable outputs and whether their label distributions are sensible.

### T1 Failures

This tab isolates failed T1 rows. It groups failures by model and by error message.

This is important for methodological transparency. If a model cannot load, it should not silently disappear from the experiment. The report can state which models were attempted, which succeeded, and which were excluded because of loading or compatibility failures.

### T2 Hybrid Results

This tab visualizes:

- rule-based tone distribution;
- hybrid tone distribution;
- hybrid sentiment distribution;
- hybrid tone confidence.

It helps compare the simpler rule-based layer with the richer hybrid layer.

### Ontology & Greenwashing

This tab visualizes:

- ontology alignment distribution;
- greenwashing-index distribution;
- most common ontology paths;
- rows with the highest greenwashing index.

This supports the research discussion about whether ESG statements are specific, ontology-aligned, and evidence-backed, or whether they lean toward broad commitment language.

### Comparisons

This tab compares rule-based tone against hybrid tone. It reports comparable rows, agreement percentage, disagreement count, and a confusion matrix.

This is not the final human-ground-truth evaluation. Instead, it is an internal pipeline-consistency check. Large disagreement between rule and hybrid tone indicates rows that may need manual review before being used in final metrics.

### Records & Exports

This tab displays the filtered T1 and T2 records and provides CSV downloads.

Use these exports when preparing:

- manual annotation batches;
- appendix tables;
- failure-mode analysis;
- comparison with ClimateBERT outputs;
- documentation of excluded model runs.

## Interpretation for the Research

This page explains what happened during the ground-truth pipeline run. It answers operational and methodological questions:

- Which models ran successfully?
- Which models failed and why?
- What labels did the models produce?
- How do rule-based and hybrid ESG interpretations differ?
- Which ontology paths are most common?
- Which records have high greenwashing risk?
- Which records should be reviewed manually before final evaluation?

Together with `1_8_Ground_Truth_Output_Visualizer.py`, this page separates two research layers:

- pipeline execution analysis: whether the models and hybrid system produced outputs correctly;
- ground-truth evaluation analysis: whether those outputs agree with silver or human labels.

This distinction is important for thesis reporting because a failed model run is an implementation issue, while a disagreement with ground truth is an evaluation finding.
