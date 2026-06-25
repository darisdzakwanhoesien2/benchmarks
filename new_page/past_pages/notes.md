# Thesis Work Split

This plan separates work by evidence readiness.

- **Phase 1** is for data that already has usable ground-truth labels or equivalent thesis evidence.
- **Phase 2** is for data or evidence that is still missing, incomplete, or not yet defensible for claims.
- **Phase 3** is for new records/data from now onward before they are reviewed into Phase 1 or Phase 2.

## Phase 1 — Ground-Truth-Ready Data

Phase 1 uses the records that already have ground-truth fields available for analysis. These are the rows where the thesis can already run label distributions, agreement checks, ontology summaries, and comparison tables without waiting for new annotation.

### Included data

- `results/revision_analysis/pilot_ground_truth_annotations.csv`
  - Main labelled dataset.
  - Current inspected state: 5,444 rows.
  - `ground_truth_tone`: populated for 5,444 rows.
  - `ground_truth_esg`: populated for 5,444 rows.
  - `ground_truth_aspect`: populated for 5,441 rows; 3 rows still need aspect backfill.
- `results/revision_analysis/pilot_ground_truth_seed.csv`
  - Original pilot seed.
  - Current inspected state: 70 rows with tone, ESG, aspect, review status, annotator, and review notes populated.
- Existing thesis-ready analysis artifacts under `results/revision_analysis/` and `results/thesis_workflow_dashboard/` that are derived from the labelled data.

### Phase 1 work

1. Lock the labelled analysis subset.
2. Use the labelled rows for tone, ESG-pillar, aspect, ontology, and human-vs-model analyses.
3. Refresh all figures/tables that depend only on already-labelled rows.
4. Write Chapter 4/5 claims using the Phase 1 denominator explicitly.
5. Keep missingness visible instead of silently dropping rows.

### What "complete" means for Phase 1

Phase 1 is complete when:

- Every included row has a stable `record_id`.
- Every included row has non-empty `ground_truth_tone`, `ground_truth_esg`, and `ground_truth_aspect`, or is explicitly marked `discard` / `insufficient_context`.
- The final denominator is written down for each claim, for example `n = 5,441` for rows with all three ground-truth fields if the 3 missing-aspect rows remain unresolved.
- `review_status` is set for rows used in final evaluation, at minimum `reviewed`, `uncertain`, or `discard`.
- Any agreement metric states exactly which labels are compared and excludes missing/unclassifiable rows unless those are intentionally modelled as a class.
- All derived artifacts are refreshed after the final Phase 1 dataset is locked.

Phase 1 does not require waiting for missing OCR ground truth, missing model runs, or second-annotator coverage. Those are Phase 2 unless they are needed for the specific claim being made.

## Phase 2 — Missing Or Incomplete Data

Phase 2 covers anything that cannot yet support a final thesis claim because required evidence is missing, partial, or not traceable enough.

### Included gaps

- Missing `ground_truth_aspect` rows in `pilot_ground_truth_annotations.csv`.
- Missing `review_status`, `annotator`, and `review_notes` coverage for the expanded 5,444-row annotation table.
- Missing second-annotator labels for reliability claims.
- Missing or partial real ClimateBERT output coverage.
- Missing OCR page-level ground truth for CER/WER claims.
- Partial failure-mode quantification.
- Partial model-stability coverage across models/prompts/repeated runs.
- Unmapped or placeholder ontology aspects that still need review.
- Clean-run manifest/provenance gaps.

### Phase 2 work

1. Backfill the 3 missing aspect labels or mark them as `discard` / `insufficient_context`.
2. Decide whether final evaluation needs annotator provenance on all 5,444 rows or only on the locked evaluation subset.
3. Add second-annotator labels for the selected reliability subset and compute Cohen's kappa.
4. Complete real ClimateBERT outputs for all required labelled records.
5. Create 50-100 OCR ground-truth pages and compute CER/WER.
6. Finish failure-mode counts on a fixed held-out sample.
7. Run missing model-stability experiments and update prompt/model stability summaries.
8. Review unmapped aspects and separate real novel ESG concepts from placeholders.
9. Build the clean-run manifest linking input files, pipeline stages, outputs, and job IDs.

### What "complete" means for Phase 2

Phase 2 is complete when every open gap has either:

- a saved artifact with the required data,
- a documented exclusion decision,
- or a clearly written limitation that prevents the thesis from overclaiming.

No Phase 2 item should remain as an implicit gap. If it is not finished, it must be named in the limitation/future-work text with the affected claim and denominator.

## Phase 3 — New Data From Now Onward

Phase 3 is the intake pool for any new record that appears after the phase registry is created. New data should not automatically affect final thesis denominators until it has been reviewed.

### Phase 3 movement rules

- Move Phase 3 -> Phase 1 when the row is already complete enough for the final completed dataset pool.
- Move Phase 3 -> Phase 2 when the row needs editing, annotation, provenance, OCR truth, model output, or review notes.
- Keep Phase 3 rows out of final thesis denominators until they are promoted.

### What "complete" means for Phase 3

Phase 3 is complete when every new row has been triaged into either:

- Phase 1, because it is ready for the completed dataset pool,
- or Phase 2, because it needs editing/backfill.

## Priority Order

| Priority | Phase | Work item | Completion target |
|---|---:|---|---|
| 1 | Phase 1 | Lock ground-truth-ready dataset | All included rows have tone, ESG, aspect, status, and denominator notes |
| 2 | Phase 1 | Refresh labelled-data analyses | Figures/tables regenerated from the locked dataset |
| 3 | Phase 3 | Triage new incoming rows | New complete rows go to Phase 1; incomplete rows go to Phase 2 |
| 4 | Phase 2 | Backfill missing aspect rows | 0 blank `ground_truth_aspect` rows, or documented exclusions |
| 5 | Phase 2 | Complete ClimateBERT coverage | Real output exists for every required labelled record |
| 6 | Phase 2 | Add second annotator | Same reliability subset labelled independently; kappa reported |
| 7 | Phase 2 | OCR ground truth | 50-100 manually verified pages with CER/WER |
| 8 | Phase 2 | Failure modes | Fixed sample counted and examples selected |
| 9 | Phase 2 | Model stability | Repeated runs summarized across required models/prompts |
| 10 | Phase 2 | Provenance manifest | Input -> stage -> output -> job ID links saved |
