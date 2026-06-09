# Master Revision Plan for Thesis Improvement

This master plan consolidates the highest-priority actions needed to improve the thesis, with special attention to the current gap around ablation studies, methodological rigor, evaluation boundaries, and submission readiness.

## 1. Immediate Submission-Blocking Actions

1. Complete the missing front matter.
   Files affected: `abstract.md`, `tiivistelma.md`, and `appendices.md`.
   Reason: these are still placeholders and make the thesis structurally incomplete.

2. Fix the truncated conclusion value in `summary.md`.
   Reason: the sentence ending at `83.7` is visibly incomplete and damages credibility.

3. Resolve the ablation-study claim.
   Reason: the thesis currently implies ablation studies, but Chapter 4 does not yet present formal controlled ablation experiments.

4. Verify research-question consistency across all chapters.
   Reason: the introduction defines four research questions, and later chapters must not silently expand or renumber them.

5. Add a direct limitation statement that the thesis is not yet a full gold-standard benchmark study.
   Reason: this prevents overclaiming.

## 2. Ablation Study Decision Plan

1. Decide between two routes immediately.
   Route A: add real, minimal controlled ablation experiments.
   Route B: remove or narrow all claims that imply ablation studies were completed.

2. If Route A is chosen, keep the ablation section minimal and controlled.
   Use one fixed dataset slice, one fixed evaluation rule, and change only one component at a time.

3. Recommended minimal ablation dimensions:
   - generic prompt versus tone-specific prompt;
   - strongest schema-following model versus weaker model;
   - with ontology enhancement versus without ontology enhancement;
   - with non-ESG filtering versus without filtering;
   - single-page context versus page-batch context.

4. For each ablation, report:
   - what stayed constant;
   - what changed;
   - sample size;
   - metrics used;
   - observed difference;
   - whether the difference is descriptive only or statistically supported.

5. If Route B is chosen, rename the current ablation-related section.
   Recommended title: `Comparative Component Analysis` or `Controlled Configuration Comparisons`.

6. Add an explicit clarification sentence if formal ablations are not added.
   Recommended meaning: these analyses are comparative diagnostics rather than formal ablation studies because not all conditions were held constant.

## 3. Research Design and Methodology Actions

1. State the study type explicitly in Chapter 3.
   Recommended framing: executable pipeline study with comparative diagnostics, weak labels, and pilot human annotation.

2. Add explicit inclusion criteria for documents.
   Examples: Indonesian sustainability and annual reports, machine-processable PDFs, corpus boundaries, time period if relevant.

3. Add explicit exclusion criteria for documents and text units.
   Examples: failed OCR files, duplicate reports, unusable pages, non-ESG accounting-policy text, broken table fragments.

4. Separate all data layers clearly.
   Required distinctions:
   - full raw PDF inventory;
   - OCR-processed inventory;
   - active thesis subset;
   - pilot annotation subset;
   - final evaluated subset per experiment.

5. Add one data-subset summary table.
   Include report count, page count, record count, annotation count, and purpose of each subset.

6. Clarify the unit of analysis at each stage.
   Examples: report, page, page batch, extracted record, benchmark item, annotated item.

7. Add a threats-to-validity subsection.
   Required headings:
   - internal validity;
   - construct validity;
   - external validity;
   - reproducibility.

## 4. Ground Truth and Annotation Actions

1. Stop using `ground truth` broadly for weakly supervised outputs.
   Prefer:
   - weak reference;
   - pilot annotation;
   - external comparison label;
   - provisional benchmark layer.

2. Describe the annotation pipeline step by step.
   Include what was annotated, by whom, using what instructions, and how final labels were decided.

3. State annotator expertise explicitly.
   If only one annotator exists, say so directly.

4. Report inter-annotator agreement if it exists.
   If it does not exist, report that absence as a limitation.

5. Add an annotation-guideline appendix.
   Define at minimum: commitment, action, outcome, none, ambiguous, needs review.

6. Add a difficult-cases table.
   Include cases such as:
   - commitment versus action boundary cases;
   - governance boilerplate;
   - hedged language;
   - accounting-policy text;
   - bilingual phrasing problems.

7. If feasible, add a small second-pass reliability check.
   Even a small doubly reviewed sample materially improves rigor.

## 5. Evaluation and Experiment Actions

1. Rewrite the Chapter 4 introduction so every experiment states:
   - objective;
   - input subset;
   - model or prompt condition;
   - output;
   - metric;
   - interpretation boundary.

2. Add a provenance note for every table.
   Each table should state exact sample size and subset.

3. Separate experiment types clearly.
   Required categories:
   - extraction performance diagnostics;
   - tone-label comparison;
   - ontology coverage;
   - robustness or stability checks;
   - qualitative failure analysis.

4. Do not imply conventional supervised evaluation if train/validation/test splits do not exist.
   State clearly when the thesis is not a standard supervised benchmark.

5. Add a metric-justification subsection.
   Explain why parse success, missing-tone rate, schema drift, agreement, and ontology coverage are meaningful.

6. Add class-level reporting.
   Aggregate reporting can conceal weak minority-class performance.

7. Add uncertainty language.
   If no statistical testing is performed, describe results as descriptive rather than statistically confirmed.

8. Reserve the word `significant` for statistical significance only.
   Otherwise use `notable`, `large`, or `substantial`.

9. Verify every denominator used in percentages and agreement claims.
   Check record totals, missing-tone counts, schema-drift counts, agreement percentages, and reported improvements.

10. Add one failure-mode table with counts and examples.
   Include:
   - missing tone;
   - schema drift;
   - hedged language failures;
   - OCR corruption;
   - table-layout confusion;
   - non-ESG contamination.

## 6. Reproducibility Actions

1. Add a reproducibility table in Chapter 3 or 4.
   Include:
   - prompt file names;
   - model identifiers;
   - provider;
   - date range;
   - decoding settings;
   - retry policy;
   - parsing rules;
   - artifact paths.

2. State whether seeds exist and whether they are controllable.
   If API models do not expose deterministic seeds, say so.

3. State whether prompts changed after output inspection.
   If yes, distinguish development-stage tuning from final comparison claims.

4. State whether repeated runs were performed.
   If not, say that outputs may reflect single-run stochasticity.

5. Add explicit artifact path references.
   Point to prompts, JSONL outputs, extracted records, dashboard outputs, and benchmark files.

6. Add a subsection on resumability and logging.
   This is a genuine strength and should be formalized.

## 7. Data Leakage and Comparison Fairness Actions

1. State whether final prompt selection was influenced by final evaluation output inspection.
   If yes, narrow claims accordingly.

2. Explain how ClimateBERT comparison was aligned.
   Required details:
   - same text unit;
   - same record ID;
   - same subset;
   - same evaluation condition.

3. Clarify whether ontology updates were influenced by difficult evaluation cases.
   If yes, state that this may inflate apparent coverage.

4. Separate development artifacts from evaluation artifacts where possible.
   Even conceptual separation is better than silence.

5. Add a caution sentence on iterative workspace effects.
   Recommended meaning: because prompt refinement and evaluation occurred in the same evolving workspace, results should be interpreted as iterative research diagnostics rather than leakage-free benchmark estimates.

## 8. Discussion and Interpretation Actions

1. Reduce overclaiming around validation.
   Safest strong claim: the framework is operational, auditable, and diagnostically informative.

2. Reduce overclaiming around ClimateBERT comparison.
   State clearly that tone labels and ClimateBERT-style commitment labels are related but not interchangeable.

3. Add alternative explanations for failures.
   Include prompt sensitivity, OCR quality, bilingual phrasing, governance boilerplate, and annotation scarcity.

4. Reframe the strongest contribution.
   It is likely the integrated auditable workflow plus diagnostic transparency, not benchmark-leading accuracy.

5. Add a paragraph on what cannot be concluded.
   Examples:
   - not final benchmark superiority;
   - not universal generalization;
   - not validated greenwashing adjudication.

6. Tighten future work priorities.
   Put annotation rigor, OCR evaluation, controlled comparisons, and broader validation ahead of extra system features.

## 9. Chapter-by-Chapter Revision Checklist

### Chapter 1: Introduction

1. Remove or soften promises that are not supported later.
2. Make the four research questions precise and measurable.
3. Remove or revise any claim that Chapter 4 contains ablation studies unless real ablations are added.
4. Align the stated contributions with what the thesis actually demonstrates.

### Chapter 2: Related Work

1. Add methodological comparison, not only model history.
2. Explain how prior work handles annotation, benchmark construction, baselines, evaluation splits, and reproducibility.
3. Replace placeholder table captions with real state-of-the-art synthesis tables.
4. Show how the literature justifies record-level ESG extraction and the tone-versus-climate distinction.

### Chapter 3: Implementation / Methodology

1. Add inclusion and exclusion criteria.
2. Add the subset-definition table.
3. Add a formal reference-construction subsection that distinguishes weak labels, pilot labels, and comparison labels.
4. Add threats to validity.
5. Add the reproducibility table.

### Chapter 4: Experiments

1. Rebuild the chapter as a sequence of explicit experiment blocks.
2. Add controlled comparisons or remove ablation claims.
3. Add class-level results where relevant.
4. Add the failure-mode table.
5. Add metrics justification and comparison-fairness notes.
6. Add explicit uncertainty language where statistical support is absent.

### Chapter 5: Discussion

1. Distinguish strong operational evidence from weaker validation evidence.
2. Reframe overstated validation claims.
3. Tie all major findings back to the same four research questions.
4. Make the limitations section more formal under validity-related categories.

### Chapter 6: Conclusion

1. Fix incomplete numerical statements.
2. Keep only evidence-backed claims.
3. State the main limitation explicitly: no full expert gold-standard benchmark and remaining prompt sensitivity.

### Front Matter and Appendices

1. Write `abstract.md` after the main thesis claims are frozen.
2. Write `tiivistelma.md` to match the final abstract exactly in scope and evidence level.
3. Use `appendices.md` to store annotation instructions, reproducibility settings, prompt versions, extended examples, and supplementary tables.
4. Clean `abbreviations.md` so it contains only thesis-relevant abbreviations.
5. Revise `foreword.md` for grammar and keep it free of unsupported scientific claims.

## 10. High-Value Improvements That Can Be Added Quickly

1. Rename or narrow ablation claims.
2. Add one subset-definition table.
3. Add one reproducibility table.
4. Add one threats-to-validity subsection.
5. Add one failure-mode table with examples.
6. Add one annotation-procedure subsection.
7. Add one explicit statement that the work is not yet a finalized benchmark study.
8. Complete the missing front matter and fix the truncated conclusion.

## 11. Best Single Experiment Upgrade If Time Is Limited

1. Choose a fixed sample of around 100 to 150 extracted records.
2. Run the same model under:
   - generic prompt;
   - tone-specific prompt.
3. Keep parsing and evaluation conditions fixed.
4. Compare at minimum:
   - parse success;
   - missing-tone rate;
   - schema drift;
   - tone completion;
   - optional manual spot-check quality on a small reviewed sample.
5. Report this as a real controlled prompt ablation if the setup is properly fixed.

## 12. Safest Final Positioning for the Thesis

1. Present the thesis as an auditable ESG extraction pipeline for Indonesian sustainability reports.
2. Claim operational feasibility, diagnostic transparency, and partial construct validation.
3. Do not claim a finalized gold-standard, leakage-controlled benchmark unless new evidence is added.
4. Present formal ablation and broader validation as future work unless they are added now under controlled conditions.

## 13. Recommended Revision Order

1. Fix front matter and obvious broken text.
2. Resolve the ablation-study claim.
3. Freeze research-question wording and chapter alignment.
4. Add subset definitions, annotation procedure, and reproducibility reporting.
5. Rewrite Chapter 4 into explicit experiment blocks.
6. Add failure analysis, validity discussion, and uncertainty language.
7. Tighten discussion and conclusion claims.
8. Finish appendices and final consistency pass.

## 14. Final Working Principle

When a claim cannot be fully supported with new experiments in time, prefer narrowing the claim over overstating the evidence. This is the lowest-risk way to improve scientific credibility before submission.
