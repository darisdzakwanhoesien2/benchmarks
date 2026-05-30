codex resume 019e7864-5d4a-7502-b1e7-8770fcd4c7e6
codex resume 019e7867-63cf-7a61-9ff6-8e76e47745df
# Fine-Tuning Track — Progress Notes

Date: 2026-05-30

This file tracks work completed for the **fine-tuning research track** and what to do next. Items are written so you can verify them directly in the repo by opening the referenced paths.

## What has been done (in this repo)

- Fine-tuning research planner Streamlit UI exists and is grounded in existing datasets:
  - `fine_tuning/app.py` renders research gap/RQs/objectives/contributions/literature topics/methodology/results-plan/discussion/conclusion.
  - It loads evidence from `results/revision_analysis/*` and shows label distribution snapshots and stability context.
- ClimateBERT-logic API validation hook exists (CLI + UI) and writes outputs under `results/fine_tuning/`:
  - `fine_tuning/call_climatebert_logic.py` writes `results/fine_tuning/climatebert_logic_from_ground_truth.csv`.
  - `fine_tuning/app.py` can sample ground-truth rows, call `/api/v1/climatebert-logic/classify`, compare fields, and export `results/fine_tuning/climatebert_api_validation_latest.csv`.
- A complete thesis-style research write-up exists and is repo-anchored:
  - `documentation_fine_tuning_research.md` (at repo root) includes research gap, questions, objectives, contributions, literature review plan, methodology, current-results status, discussion, and conclusion.
- Global cross-track execution notes already include a fine-tuning section:
  - `progress_notes.md` (at repo root) contains the fine-tuning “done / blockers / next” list.

## Current blockers / risks

- **Environment constraints:** the base Python environment may lack common dependencies (e.g., `pandas`), which slows dataset packaging and repeatable EDA in scripts.
- **Leakage risk:** row-level splitting is likely invalid because texts are templated and clustered by `company`; splits should be company/report-level.
- **Label harmonization required:** pillar labels can appear in mixed forms (e.g., `e-s-g`, `e-s`), and sentiment/tone may have blanks/non-canonical tokens.
- **No fine-tuning runner yet:** there is no integrated `code/` module that trains/evaluates full fine-tuning and PEFT and exports standardized benchmark artifacts.

## What we need to do next (recommended order)

1. Build canonical dataset artifact:
   - Create `results/fine_tuning/labels_master.csv` derived from `results/revision_analysis/pilot_ground_truth_annotations.csv`.
   - Define stable IDs, text field selection, canonical label mappings, and filtering rules.
2. Add deterministic, leakage-aware splits:
   - Write `results/fine_tuning/splits.json` splitting by `company` (and/or report/document IDs if available).
   - Record split seed + version so results are reproducible.
3. Implement training + evaluation runner:
   - Add `code/fine_tuning_esg_absa.py` to run:
     - baseline(s) (if needed for direct comparison),
     - full fine-tuning,
     - PEFT (LoRA/adapters),
     - repeated seeds and subgroup breakdowns.
   - Export: `metrics_*.json/csv`, `predictions_*.csv`, `confusion_*.csv`, `error_analysis_*.csv` under `results/fine_tuning/`.
4. Add results visualization page:
   - Create a Streamlit page under `pages/` that reads `results/fine_tuning/*` outputs and compares models consistently.
5. Update the research write-up with real results:
   - Replace the “current repo state” Results section with measured metrics and stability/subgroup evidence once (1–4) exist.

