# 2_1_LLM_Error_Parse_Audit.py

## Purpose

This page audits the T3 output from `llm_processing.py` when some model runs do not become parsed ESG records.

It focuses on the gap between:

- runs that produced parsed records;
- runs that completed but returned an empty JSON array;
- runs that failed with no raw output;
- runs that failed but still saved raw output that may be recoverable.

## Data Used

The page reads:

- `results/esg_records.json`

Each row in this file is a T3 model-target-prompt run. The page flattens those runs into an audit table with:

- `model`;
- `target`;
- `company`;
- `prompt`;
- `ok`;
- `status`;
- `n_records`;
- `error`;
- `error_category`;
- `raw_output_signal`;
- `raw_output_len_chars`;
- `raw_output_preview`.

## Status Definitions

- `parsed_records`: the run produced one or more structured ESG records.
- `ok_empty`: the run succeeded but returned zero records, usually `[]`.
- `failed_with_raw_output`: the run failed, but the raw model output was saved.
- `failed_no_raw_output`: the run failed before usable raw output was captured.

## Error Categories

The page groups errors into:

- `json_parse_error`;
- `empty_response`;
- `timeout`;
- `memory_error`;
- `server_500`;
- `upload_too_large`;
- `connection_error`;
- `rate_limit`;
- `other_error`;
- `none`.

This makes it easier to distinguish model-generation problems from parser problems and infrastructure problems.

## Raw Output Signals

The page also labels saved raw output as:

- `no_raw_output`;
- `empty_json`;
- `json_like_complete`;
- `json_like_truncated_or_malformed`;
- `markdown_wrapped`;
- `text_not_json`.

This helps identify outputs that could potentially be repaired or recovered.

## Workflow

1. Run `llm_processing.py`.
2. Open this audit page.
3. Use filters for model, company, target, prompt, status, error category, and raw-output signal.
4. Review the dashboard counts.
5. Open **Remaining Errors** to see unresolved model-target-prompt combinations.
6. Open **Raw Output Not Parsed** to inspect outputs that were saved but could not be parsed.
7. Export CSVs for rerun planning or manual correction.

## Interpretation

This page is useful when a run appears to have happened but does not show up in the normal result charts. A failed T3 run is still stored as a run-level object in `esg_records.json`, but it does not produce record-level ESG rows. That means record-only visualizations can make failed or empty runs look invisible.

For example, a row such as:

```text
google/gemma-4-e2b · batch_2 · tone_few_shot_indonesian.md
```

can fail with a parse error while still saving partial raw output. This page counts that run as unresolved and displays the raw output preview for debugging.

## Research Use

Use this page to report:

- extraction success rate;
- number of parsed ESG records;
- number of empty prompt outputs;
- number of parse failures;
- number of model/server failures;
- remaining model-target-prompt combinations needing rerun or manual repair.

It supports methodology transparency because failed runs are accounted for instead of silently disappearing from the parsed-record tables.
