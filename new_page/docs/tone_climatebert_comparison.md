# Tone and ClimateBERT Comparison

## Scope

This analysis uses `/home/ubuntu/apps/benchmarks/new_page/results/esg_records.json` as the existing tone-result dataset. It contains 481 extracted records from 71 runs across 34 source targets.

The raw ClimateBERT comparison file, `/home/ubuntu/apps/benchmarks/new_page/results/climatebert_results.json`, contains 3 remote ClimateBERT runs. That is much smaller than the tone-result dataset, so it should be treated as a sanity-check sample rather than a full ground-truth evaluation.

## What The Fields Mean

- `tone` describes the disclosure posture: `commitment` is a promise or future intent, `action` is an activity being performed, `outcome` is an achieved/measured result, and `none` means no meaningful ESG tone was found.
- `aspect` is the ESG topic assigned by the extraction step, such as `climate-detection`, `governance`, or `environmental-claims`.
- `labels` are ClimateBERT-style task labels attached to the extracted record. They are useful for checking whether the text looks climate-related, specific, a commitment, an environmental claim, or a governance/social item.
- ClimateBERT itself is not a direct tone classifier. It is better interpreted as external evidence about climate relevance, specificity, environmental claims, TCFD category, sentiment, commitment, and related climate tasks.

## Main Findings

- The dominant non-missing tone is `none` with 168 records.
- Missing/blank tone values appear in 0 records, which means part of the extraction output still needs cleanup before it can support strong accuracy claims.
- ESG pillar distribution is: `e`=211, `g`=121, `none`=86, `s`=63.
- The most frequent ClimateBERT-style labels in the extracted records are: `governance`=115, `environmental-claims`=113, `climate-d-s`=89, `none`=72, `strategy`=60, `climate-commitment`=47, `metrics`=36, `risk`=25, `climate-d`=22, `opportunity`=22.

## Comparison Interpretation

The practical comparison is: does the tone assigned by the extraction layer make sense given the ClimateBERT-style climate labels?

- `commitment` should often co-occur with labels such as `climate-commitment`, `netzero-reduction`, `climate-action`, or `environmental-claims` when the text describes targets, plans, or pledges.
- `action` should often co-occur with operational or governance labels when the text describes concrete programs, controls, training, implementation, procurement, or financing activity.
- `outcome` should be strongest when the text contains result language, metrics, reductions, achievements, or reported performance.
- `none` should mainly pair with non-climate, generic, or empty labels. If `none` frequently co-occurs with climate-specific labels, that is a likely false negative in tone extraction.

In the current data:

- `commitment` most often appears with `other`=50, `climate-commitment`=42, `governance`=34.
- `action` most often appears with `other`=51, `environmental-claims`=47, `climate-d-s`=43.
- `outcome` most often appears with `other`=30, `environmental-claims`=19, `climate-d-s`=18.
- `none` most often appears with `governance`=55, `none`=55, `other`=41.

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
- `results/visualizations/failure_mode_pareto.png`
- `results/visualizations/failure_mode_pie.png`
- `results/visualizations/model_tradeoff_scatter.png`
- `results/visualizations/prompt_strategy_comparison.png`
- `results/visualizations/information_density_by_tone.png`
- `results/visualizations/soft_language_ratio_by_tone.png`
- `results/visualizations/greenwashing_gap_scatter.png`
- `results/visualizations/commitment_outcome_ratio.png`
- `results/visualizations/tone_records_flat.csv`
- `results/visualizations/climatebert_remote_flat.csv`
- `results/visualizations/tone_climatebert_label_crosstab.csv`

## Recommended Next Step

For a true accuracy comparison, run ClimateBERT over the same `text` records in `esg_records.json`, then add a manual ground-truth tone column for a stratified sample. After that, compute a confusion matrix for `tone_pred` versus `tone_ground_truth` and use ClimateBERT labels as explanatory variables for disagreements.
