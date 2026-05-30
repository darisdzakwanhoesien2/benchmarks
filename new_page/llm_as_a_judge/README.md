# LLM-as-a-Judge (Streamlit app)
codex resume 019e7851-6d89-73b3-b80b-19e10da445b4

This folder contains:

- `research_plan.md`: research plan based on existing benchmark artifacts.
- `app.py`: a Streamlit app that explores `results/esg_records.json` and (optionally) judge outputs under `results/llm_judge/`.

## Run

From the repository root:

```bash
streamlit run llm_as_a_judge/app.py
```

## Expected inputs

- T3 extraction dataset: `results/esg_records.json`
- (Optional) judge outputs directory: `results/llm_judge/`
  - `judge_records.jsonl`
  - `judge_summary.csv`

