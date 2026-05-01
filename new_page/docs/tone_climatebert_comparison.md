# Tone and ClimateBERT Comparison

## Scope

This analysis uses `/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks/new_page/results/esg_records.json` as the existing tone-result dataset. It contains 332 extracted records from 39 runs across 34 source targets.

The raw ClimateBERT comparison file, `/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks/new_page/results/climatebert_results.json`, contains 3 remote ClimateBERT runs. That is much smaller than the tone-result dataset, so it should be treated as a sanity-check sample rather than a full ground-truth evaluation.

## What The Fields Mean

- `tone` describes the disclosure posture: `commitment` is a promise or future intent, `action` is an activity being performed, `outcome` is an achieved/measured result, and `none` means no meaningful ESG tone was found.
- `aspect` is the ESG topic assigned by the extraction step, such as `climate-detection`, `governance`, or `environmental-claims`.
- `labels` are ClimateBERT-style task labels attached to the extracted record. They are useful for checking whether the text looks climate-related, specific, a commitment, an environmental claim, or a governance/social item.
- ClimateBERT itself is not a direct tone classifier. It is better interpreted as external evidence about climate relevance, specificity, environmental claims, TCFD category, sentiment, commitment, and related climate tasks.

## Main Findings

- The dominant non-missing tone is `commitment` with 115 records.
- Missing/blank tone values appear in 61 records, which means part of the extraction output still needs cleanup before it can support strong accuracy claims.
- ESG pillar distribution is: `e`=179, `g`=121, `none`=27, `s`=4, `missing`=1.
- The most frequent ClimateBERT-style labels in the extracted records are: `climate-commitment`=121, `governance`=111, `climate-d`=101, `environmental-claims`=85, `climate-sentiment`=50, `metrics`=49, `climate-specificity`=46, `strategy`=40, `none`=35, `climate-s`=34.

## Comparison Interpretation

The practical comparison is: does the tone assigned by the extraction layer make sense given the ClimateBERT-style climate labels?

- `commitment` should often co-occur with labels such as `climate-commitment`, `netzero-reduction`, `climate-action`, or `environmental-claims` when the text describes targets, plans, or pledges.
- `action` should often co-occur with operational or governance labels when the text describes concrete programs, controls, training, implementation, procurement, or financing activity.
- `outcome` should be strongest when the text contains result language, metrics, reductions, achievements, or reported performance.
- `none` should mainly pair with non-climate, generic, or empty labels. If `none` frequently co-occurs with climate-specific labels, that is a likely false negative in tone extraction.

In the current data:

- `commitment` most often appears with `climate-commitment`=91, `climate-d`=57, `environmental-claims`=48.
- `action` most often appears with `governance`=25, `climate-d`=23, `other`=22.
- `outcome` most often appears with `other`=36, `governance`=20, `climate-d`=19.
- `none` most often appears with `none`=24, `governance`=21, `climate-d`=2.
- `missing` most often appears with `other`=49, `climate-commitment`=22, `environmental-claims`=21.

Because the available ClimateBERT remote-run file has only three inputs, it cannot establish full ground truth. For a thesis or benchmark section, describe it as a validation lens unless you manually label the same records and use those labels as ground truth.

A stricter ground-truth workflow would require one row per text with: `text`, `tone_pred`, `tone_ground_truth`, and the ClimateBERT model outputs for that exact same text. The current files are close to that workflow, but they are not yet a full one-to-one benchmark.

## ClimateBERT Remote Run Notes

The parsed ClimateBERT remote sample contains 48 model-level rows from 16 models. 9 rows are model errors, mostly from models whose Hugging Face configs were not recognized in the remote space.

Top labels from successful ClimateBERT sample runs:

- `climate-commitment` -> `yes` (0.92)
- `climate-d` -> `LABEL_1` (0.56)
- `climate-d-s` -> `LABEL_0` (0.50)
- `climate-detector` -> `no` (0.99)
- `climate-f` -> `LABEL_1` (0.54)
- `climate-s` -> `LABEL_1` (0.51)
- `climate-sentiment` -> `opportunity` (0.86)
- `climate-specificity` -> `spec` (0.84)
- `climate-tcfd` -> `metrics` (0.77)
- `environmental-claims` -> `no` (1.00)
- `netzero-reduction` -> `none` (1.00)
- `renewable` -> `Not about renewables` (1.00)

## Generated Artifacts

- `results/visualizations/tone_distribution.png`
- `results/visualizations/esg_by_tone.png`
- `results/visualizations/climatebert_label_by_tone.png`
- `results/visualizations/aspect_by_tone_heatmap.png`
- `results/visualizations/climatebert_remote_top_scores.png`
- `results/visualizations/tone_records_flat.csv`
- `results/visualizations/climatebert_remote_flat.csv`
- `results/visualizations/tone_climatebert_label_crosstab.csv`

## Recommended Next Step

For a true accuracy comparison, run ClimateBERT over the same `text` records in `esg_records.json`, then add a manual ground-truth tone column for a stratified sample. After that, compute a confusion matrix for `tone_pred` versus `tone_ground_truth` and use ClimateBERT labels as explanatory variables for disagreements.
