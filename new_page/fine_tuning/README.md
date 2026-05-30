codex resume 019e7867-63cf-7a61-9ff6-8e76e47745df

# Fine-Tuning Research Plan App

This Streamlit app converts `documentation_fine_tuning.md` into a structured research plan and grounds it with live evidence from existing datasets under `results/revision_analysis/`.

For the complete thesis-style fine-tuning research write-up, see `documentation_fine_tuning_research.md` (repo root). For execution tracking, see:

- Track-local: `fine_tuning/progress_notes.md`
- Global cross-track: `progress_notes.md` (repo root)

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
