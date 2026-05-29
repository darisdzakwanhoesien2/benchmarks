# Fine-Tuning Research Plan App

This Streamlit app converts `documentation_fine_tuning.md` into a structured research plan and grounds it with live evidence from existing datasets under `results/revision_analysis/`.

## Run

```bash
streamlit run fine_tuning/app.py
```

## Includes

- Research gap
- Research questions
- Research objectives
- Research contributions
- Topic of literature
- Methodology
- Results interpretation plan
- Discussion
- Conclusion

## Evidence Sources

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
- `results/revision_analysis/silver_tone_ground_truth.csv`
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
- `results/revision_analysis/climatebert_output.csv`
- `results/revision_analysis/model_stability_summary.csv`
- `results/revision_analysis/prompt_stability_summary.csv`
