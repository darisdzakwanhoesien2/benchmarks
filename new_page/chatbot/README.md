codex resume 019e7864-fe32-7441-8277-968f1ea0c529
# Chatbot Review Paper App

This Streamlit app renders `chatbot/review_paper.md` and grounds it with current sustainability-report artifacts.

## Run

```bash
streamlit run chatbot/app.py
```

## Includes

- Evidence snapshot from current repo artifacts
- Saved thesis workflow dashboard visuals
- Full rendered review paper from `chatbot/review_paper.md`
- Repo context for future `results/chatbot/` work

## Data source priority

1. `results/thesis_workflow_dashboard/`
2. `results/revision_analysis/` (fallback)

## Main grounded artifacts

- `dashboard_metrics.json`
- `pilot_ground_truth_seed.csv` or `pilot_ground_truth_annotations.csv`
- `llm_statement_page_verifier_compiled.csv`
- `failure_mode_counts.csv` or `failure_modes.csv`
- `ontology_coverage.csv`
- `prompt_stability_summary.csv`
- `model_stability_summary.csv`
- `llm_background_jobs.csv`
