codex resume 019e7863-7ad1-7302-98bc-bbb0a4fb8fab
# Fact-Checking Research Plan App

This Streamlit app builds a full multimodal fact-checking research plan from `documentation_fact_checking.md` and grounds it with current datasets under `results/revision_analysis/`.

## Run

```bash
streamlit run fact_checking/app.py
```

## Includes

- Research gap
- Research questions
- Research objectives
- Research contributions
- Topic of literature review
- Methodology
- Results interpretation
- Discussion
- Conclusion

## Outputs

- Full thesis-style write-up: `documentation_fact_checking_research.md`

## Grounding datasets

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
- `results/revision_analysis/failure_modes.csv`
- `results/revision_analysis/prompt_stability_summary.csv`
- `results/revision_analysis/model_stability_summary.csv`
- `results/revision_analysis/ocr_processing_summary.csv`
