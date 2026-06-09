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
- [ ] Complete `appendices.md`.
- [ ] Fix the truncated numerical statement in `summary.md`.
- [!] Decide whether to add real ablation studies or remove ablation claims.
- [ ] Verify that the thesis consistently uses exactly four research questions.
- [ ] Add an explicit limitation statement that the thesis is not yet a full gold-standard benchmark study.

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

- [ ] State the study type explicitly in Chapter 3.
- [ ] Add document inclusion criteria.
- [ ] Add document exclusion criteria.
- [ ] Add text-unit inclusion criteria.
- [ ] Add text-unit exclusion criteria.
- [ ] Distinguish full raw PDF inventory from OCR-processed inventory.
- [ ] Distinguish OCR-processed inventory from active thesis subset.
- [ ] Distinguish active thesis subset from pilot annotation subset.
- [ ] Distinguish pilot annotation subset from final evaluated subset per experiment.
- [ ] Add one data-subset summary table with counts and purposes.
- [ ] Clarify the unit of analysis at each pipeline stage.
- [ ] Add a threats-to-validity subsection.
- [ ] Add internal validity discussion.
- [ ] Add construct validity discussion.
- [ ] Add external validity discussion.
- [ ] Add reproducibility discussion.

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

- [ ] Rewrite the Chapter 4 opening around explicit experiment blocks.
- [ ] For each experiment, state objective.
- [ ] For each experiment, state input subset.
- [ ] For each experiment, state model or prompt condition.
- [ ] For each experiment, state output.
- [ ] For each experiment, state metric.
- [ ] For each experiment, state interpretation boundary.
- [ ] Add sample-size provenance to every major table.
- [ ] Separate extraction diagnostics from tone-label comparison.
- [ ] Separate tone-label comparison from ontology coverage.
- [ ] Separate ontology coverage from robustness or stability checks.
- [ ] Separate robustness or stability checks from qualitative failure analysis.
- [ ] Add a subsection stating whether this is or is not a conventional supervised benchmark.
- [ ] Add a metric-justification subsection.
- [ ] Justify parse success as a metric.
- [ ] Justify missing-tone rate as a metric.
- [ ] Justify schema drift as a metric.
- [ ] Justify agreement as a metric.
- [ ] Justify ontology coverage as a metric.
- [ ] Add class-level reporting where possible.
- [ ] Add uncertainty language where no statistical testing exists.
- [ ] Replace non-statistical uses of `significant`.
- [ ] Verify all denominators in percentages.
- [ ] Verify all denominators in agreement calculations.
- [ ] Verify all denominators in missing-tone counts.
- [ ] Verify all denominators in schema-drift counts.
- [ ] Add one failure-mode table with counts.
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
- [ ] Explain ClimateBERT alignment by text unit.
- [ ] Explain ClimateBERT alignment by record ID.
- [ ] Explain ClimateBERT alignment by subset.
- [ ] Explain ClimateBERT alignment by evaluation condition.
- [ ] State whether ontology updates were influenced by difficult evaluation cases.
- [ ] Add a caution note if ontology refinement may inflate apparent coverage.
- [ ] Separate development artifacts from evaluation artifacts conceptually or operationally.
- [ ] Add the iterative-workspace caution sentence.

## 8. Discussion and Interpretation

- [ ] Reduce overclaiming around validation.
- [ ] Reframe the strongest supported contribution as workflow plus diagnostic transparency.
- [ ] State clearly that tone labels and ClimateBERT-style commitment labels are related but not interchangeable.
- [ ] Add alternative explanations for failures.
- [ ] Mention prompt sensitivity as an alternative explanation.
- [ ] Mention OCR quality as an alternative explanation.
- [ ] Mention bilingual phrasing as an alternative explanation.
- [ ] Mention governance boilerplate as an alternative explanation.
- [ ] Mention annotation scarcity as an alternative explanation.
- [ ] Add a paragraph on what cannot be concluded.
- [ ] State that benchmark superiority cannot yet be concluded.
- [ ] State that universal generalization cannot yet be concluded.
- [ ] State that greenwashing adjudication cannot yet be concluded.
- [ ] Reorder future work so rigor-related improvements come first.

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
- [ ] Replace placeholder table captions.
- [ ] Add synthesis supporting record-level ESG extraction.
- [ ] Add synthesis supporting the tone-versus-climate distinction.

## 11. Chapter 3: Implementation / Methodology

- [ ] Add inclusion criteria.
- [ ] Add exclusion criteria.
- [ ] Add subset-definition table.
- [ ] Distinguish weak labels from pilot labels and comparison labels.
- [ ] Add threats to validity.
- [ ] Add reproducibility table or reproducibility subsection.

## 12. Chapter 4: Experiments

- [ ] Rebuild the chapter into explicit experiment blocks.
- [ ] Add controlled comparisons or remove ablation claims.
- [ ] Add class-level results where feasible.
- [ ] Add failure-mode table.
- [ ] Add metric justification.
- [ ] Add comparison-fairness notes.
- [ ] Add uncertainty language.

## 13. Chapter 5: Discussion

- [ ] Distinguish strong operational evidence from weaker validation evidence.
- [ ] Reframe overstated validation claims.
- [ ] Tie all major findings back to the same four research questions.
- [ ] Group limitations under validity-related categories where possible.

## 14. Chapter 6: Conclusion

- [ ] Fix incomplete numerical statements.
- [ ] Keep only evidence-backed claims.
- [ ] State the main limitation explicitly.

## 15. Front Matter and Appendices

- [ ] Write `abstract.md` after body claims are frozen.
- [ ] Write `tiivistelma.md` to match the final abstract in scope and evidence level.
- [ ] Use `appendices.md` for annotation instructions.
- [ ] Use `appendices.md` for reproducibility settings.
- [ ] Use `appendices.md` for prompt versions.
- [ ] Use `appendices.md` for extended examples.
- [ ] Use `appendices.md` for supplementary tables.
- [ ] Clean `abbreviations.md` to contain only thesis-relevant abbreviations.
- [ ] Revise `foreword.md` for grammar and formality.
- [ ] Remove unsupported scientific claims from `foreword.md`.

## 16. Quick Wins

- [ ] Rename or narrow ablation claims.
- [ ] Add one subset-definition table.
- [ ] Add one reproducibility table.
- [ ] Add one threats-to-validity subsection.
- [ ] Add one failure-mode table.
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

- [ ] Present the thesis as an auditable ESG extraction pipeline.
- [ ] Claim operational feasibility.
- [ ] Claim diagnostic transparency.
- [ ] Claim partial construct validation only if the evidence supports it.
- [ ] Avoid claiming finalized gold-standard benchmark status unless new evidence is added.
- [ ] Present formal ablation and broader validation as future work unless actually completed.

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
