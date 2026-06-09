# Master Revision Tracker

Use this file as the working execution tracker for thesis revision. Update each item's status as work progresses.

Status key:

- `[ ]` not started
- `[-]` in progress
- `[x]` completed
- `[!]` blocked or needs decision

## 1. Submission-Blocking Items

- [ ] Complete `abstract.md`.
- [ ] Complete `tiivistelma.md`.
- [x] Complete `appendices.md`.
- [ ] Fix the truncated numerical statement in `summary.md`.
- [!] Decide whether to add real ablation studies or remove ablation claims.
- [x] Verify that the thesis consistently uses exactly four research questions.
- [x] Add an explicit limitation statement that the thesis is not yet a full gold-standard benchmark study.

## 2. Ablation Study Resolution

- [!] Choose Route A or Route B.
- [ ] If Route A: define one fixed evaluation subset for ablation.
- [ ] If Route A: define one fixed metric set for ablation.
- [ ] If Route A: run generic prompt versus tone-specific prompt comparison under fixed conditions.
- [ ] If Route A: run strongest schema-following model versus weaker model comparison under fixed conditions.
- [ ] If Route A: test with versus without ontology enhancement if feasible.
- [ ] If Route A: test with versus without non-ESG filtering if feasible.
- [ ] If Route A: test single-page versus page-batch context if feasible.
- [ ] If Route A: write one formal ablation subsection with controlled conditions.
- [ ] If Route B: remove or narrow all text implying formal ablation studies were completed.
- [ ] If Route B: rename the current ablation-related section to `Comparative Component Analysis` or equivalent.
- [ ] If Route B: add a clarifying sentence that current comparisons are diagnostic rather than formal ablations.

## 3. Research Design and Methodology

- [x] State the study type explicitly in Chapter 3.
- [x] Add document inclusion criteria.
- [x] Add document exclusion criteria.
- [x] Add text-unit inclusion criteria.
- [x] Add text-unit exclusion criteria.
- [x] Distinguish full raw PDF inventory from OCR-processed inventory.
- [x] Distinguish OCR-processed inventory from active thesis subset.
- [x] Distinguish active thesis subset from pilot annotation subset.
- [x] Distinguish pilot annotation subset from final evaluated subset per experiment.
- [ ] Add one data-subset summary table with counts and purposes.
- [x] Clarify the unit of analysis at each pipeline stage.
- [x] Add a threats-to-validity subsection.
- [x] Add internal validity discussion.
- [x] Add construct validity discussion.
- [x] Add external validity discussion.
- [x] Add reproducibility discussion.

## 4. Ground Truth and Annotation

- [ ] Replace overly strong uses of `ground truth` where only weak labels exist.
- [ ] Replace overly strong uses of `ground truth` where only pilot labels exist.
- [ ] Describe the annotation pipeline step by step.
- [ ] State who annotated the data.
- [ ] State annotator expertise.
- [ ] State whether annotation instructions existed.
- [ ] Add or reference annotation instructions.
- [ ] Report inter-annotator agreement if available.
- [ ] If no inter-annotator agreement exists, state that explicitly as a limitation.
- [ ] Add definitions for commitment, action, outcome, none, ambiguous, and needs review.
- [ ] Add a difficult-cases table.
- [ ] Include commitment versus action boundary examples.
- [ ] Include governance boilerplate examples.
- [ ] Include hedged-language examples.
- [ ] Include accounting-policy text examples.
- [ ] Include bilingual phrasing problems.
- [ ] If feasible, add a small second-pass reliability check.

## 5. Experiments and Evaluation

- [x] Rewrite the Chapter 4 opening around explicit experiment blocks.
- [x] For each experiment, state objective.
- [x] For each experiment, state input subset.
- [x] For each experiment, state model or prompt condition.
- [x] For each experiment, state output.
- [x] For each experiment, state metric.
- [x] For each experiment, state interpretation boundary.
- [ ] Add sample-size provenance to every major table.
- [x] Separate extraction diagnostics from tone-label comparison.
- [x] Separate tone-label comparison from ontology coverage.
- [x] Separate ontology coverage from robustness or stability checks.
- [x] Separate robustness or stability checks from qualitative failure analysis.
- [x] Add a subsection stating whether this is or is not a conventional supervised benchmark.
- [x] Add a metric-justification subsection.
- [x] Justify parse success as a metric.
- [x] Justify missing-tone rate as a metric.
- [x] Justify schema drift as a metric.
- [x] Justify agreement as a metric.
- [x] Justify ontology coverage as a metric.
- [ ] Add class-level reporting where possible.
- [x] Add uncertainty language where no statistical testing exists.
- [x] Replace non-statistical uses of `significant`.
- [ ] Verify all denominators in percentages.
- [ ] Verify all denominators in agreement calculations.
- [ ] Verify all denominators in missing-tone counts.
- [ ] Verify all denominators in schema-drift counts.
- [x] Add one failure-mode table with counts.
- [ ] Add representative failure examples to the failure-mode table.

## 6. Reproducibility

- [ ] Add one reproducibility table in Chapter 3 or 4.
- [ ] Report prompt file names.
- [ ] Report model identifiers.
- [ ] Report provider names.
- [ ] Report date range or run dates.
- [ ] Report decoding settings.
- [ ] Report retry policy.
- [ ] Report parsing rules.
- [ ] Report artifact paths.
- [ ] State whether seeds exist.
- [ ] State whether seeds are controllable.
- [ ] State whether prompts changed after output inspection.
- [ ] Distinguish development-stage prompt tuning from final comparison claims.
- [ ] State whether repeated runs were performed.
- [ ] If repeated runs were not performed, state stochasticity as a limitation.
- [ ] Add explicit references to prompt files and result artifacts.
- [ ] Add a resumability and logging subsection.

## 7. Data Leakage and Comparison Fairness

- [ ] State whether final prompt selection was influenced by final output inspection.
- [ ] Narrow claims if prompt selection used evaluation observations.
- [x] Explain ClimateBERT alignment by text unit.
- [x] Explain ClimateBERT alignment by record ID.
- [x] Explain ClimateBERT alignment by subset.
- [x] Explain ClimateBERT alignment by evaluation condition.
- [ ] State whether ontology updates were influenced by difficult evaluation cases.
- [ ] Add a caution note if ontology refinement may inflate apparent coverage.
- [ ] Separate development artifacts from evaluation artifacts conceptually or operationally.
- [x] Add the iterative-workspace caution sentence.

## 8. Discussion and Interpretation

- [x] Reduce overclaiming around validation.
- [x] Reframe the strongest supported contribution as workflow plus diagnostic transparency.
- [x] State clearly that tone labels and ClimateBERT-style commitment labels are related but not interchangeable.
- [ ] Add alternative explanations for failures.
- [x] Mention prompt sensitivity as an alternative explanation.
- [x] Mention OCR quality as an alternative explanation.
- [x] Mention bilingual phrasing as an alternative explanation.
- [x] Mention governance boilerplate as an alternative explanation.
- [ ] Mention annotation scarcity as an alternative explanation.
- [x] Add a paragraph on what cannot be concluded.
- [x] State that benchmark superiority cannot yet be concluded.
- [x] State that universal generalization cannot yet be concluded.
- [x] State that greenwashing adjudication cannot yet be concluded.
- [x] Reorder future work so rigor-related improvements come first.

## 9. Chapter 1: Introduction

- [ ] Remove unsupported promises from the introduction.
- [ ] Make the four research questions more precise if needed.
- [ ] Ensure the chapter outline does not promise ablation studies unless they are added.
- [ ] Align stated contributions with actual demonstrated contributions.

## 10. Chapter 2: Related Work

- [ ] Add methodological comparison, not just model chronology.
- [ ] Discuss how prior work handles annotation.
- [ ] Discuss how prior work handles benchmark construction.
- [ ] Discuss how prior work handles baselines.
- [ ] Discuss how prior work handles evaluation splits.
- [ ] Discuss how prior work handles reproducibility.
- [x] Replace placeholder table captions.
- [ ] Add synthesis supporting record-level ESG extraction.
- [ ] Add synthesis supporting the tone-versus-climate distinction.

## 11. Chapter 3: Implementation / Methodology

- [x] Add inclusion criteria.
- [x] Add exclusion criteria.
- [ ] Add subset-definition table.
- [x] Distinguish weak labels from pilot labels and comparison labels.
- [x] Add threats to validity.
- [ ] Add reproducibility table or reproducibility subsection.

## 12. Chapter 4: Experiments

- [x] Rebuild the chapter into explicit experiment blocks.
- [ ] Add controlled comparisons or remove ablation claims.
- [ ] Add class-level results where feasible.
- [x] Add failure-mode table.
- [x] Add metric justification.
- [x] Add comparison-fairness notes.
- [x] Add uncertainty language.

## 13. Chapter 5: Discussion

- [x] Distinguish strong operational evidence from weaker validation evidence.
- [x] Reframe overstated validation claims.
- [x] Tie all major findings back to the same four research questions.
- [x] Group limitations under validity-related categories where possible.

## 14. Chapter 6: Conclusion

- [ ] Fix incomplete numerical statements.
- [ ] Keep only evidence-backed claims.
- [ ] State the main limitation explicitly.

## 15. Front Matter and Appendices

- [ ] Write `abstract.md` after body claims are frozen.
- [ ] Write `tiivistelma.md` to match the final abstract in scope and evidence level.
- [x] Use `appendices.md` for annotation instructions.
- [x] Use `appendices.md` for reproducibility settings.
- [x] Use `appendices.md` for prompt versions.
- [x] Use `appendices.md` for extended examples.
- [x] Use `appendices.md` for supplementary tables.
- [ ] Clean `abbreviations.md` to contain only thesis-relevant abbreviations.
- [ ] Revise `foreword.md` for grammar and formality.
- [ ] Remove unsupported scientific claims from `foreword.md`.

## 16. Quick Wins

- [ ] Rename or narrow ablation claims.
- [ ] Add one subset-definition table.
- [ ] Add one reproducibility table.
- [x] Add one threats-to-validity subsection.
- [x] Add one failure-mode table.
- [ ] Add one annotation-procedure subsection.
- [ ] Add one explicit benchmark-boundary statement.
- [ ] Complete the missing front matter.
- [ ] Fix the broken conclusion sentence.

## 17. Best Single Experiment Upgrade If Time Is Limited

- [ ] Select a fixed sample of about 100 to 150 extracted records.
- [ ] Run the same model with a generic prompt.
- [ ] Run the same model with a tone-specific prompt.
- [ ] Keep parsing conditions fixed across the comparison.
- [ ] Keep evaluation conditions fixed across the comparison.
- [ ] Compare parse success.
- [ ] Compare missing-tone rate.
- [ ] Compare schema drift.
- [ ] Compare tone completion.
- [ ] If feasible, add a small manual spot-check quality review.
- [ ] Write the result as a formal controlled prompt ablation if conditions are truly fixed.

## 18. Final Positioning Check

- [x] Present the thesis as an auditable ESG extraction pipeline.
- [x] Claim operational feasibility.
- [x] Claim diagnostic transparency.
- [x] Claim partial construct validation only if the evidence supports it.
- [ ] Avoid claiming finalized gold-standard benchmark status unless new evidence is added.
- [ ] Present formal ablation and broader validation as future work unless actually completed.

## 20. LaTeX and Presentation

- [x] Remove duplicate LaTeX labels that caused multiply-defined reference warnings.
- [x] Replace placeholder table labels in Chapter 2 with unique semantic labels.
- [x] Replace placeholder table captions in Chapter 4 and appendices.
- [x] Fix appendix figure label collision with discussion figures.
- [x] Constrain oversized full-page figures in Chapters 3 to 5 and appendices to fit the thesis page height more reliably.
- [ ] Reduce or restructure oversized landscape tables in Chapter 2 that still trigger float-too-large warnings.
- [ ] Reduce overfull `\texttt{}` table cells in Chapter 4.

## 19. Recommended Revision Order

- [ ] Step 1: fix front matter and broken text.
- [ ] Step 2: resolve the ablation-study claim.
- [ ] Step 3: freeze research-question wording and chapter alignment.
- [ ] Step 4: add subset definitions, annotation procedure, and reproducibility reporting.
- [ ] Step 5: rewrite Chapter 4 into explicit experiment blocks.
- [ ] Step 6: add failure analysis, validity discussion, and uncertainty language.
- [ ] Step 7: tighten discussion and conclusion claims.
- [ ] Step 8: finish appendices and run a final consistency pass.

## 20. Final Principle

- [ ] When full experimental support is not feasible in time, narrow the claim instead of overstating the evidence.
