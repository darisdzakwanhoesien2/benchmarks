# Action List for `experiments.md`

Source file: `converted_markdown/experiments.md`

## Priority Actions

1. Convert Chapter 4 into a stricter evaluation chapter with explicit experimental protocol, comparison conditions, and evidence boundaries.
2. State exactly which dataset slice each table uses; do not mix full corpus, active subset, pilot annotation subset, and per-model slice without labeling them.
3. Add a reproducible evaluation procedure for each experiment: inputs, models, prompts, outputs, metrics, and acceptance criteria.
4. Distinguish clearly between benchmark-style evaluation, diagnostic analytics, and illustrative case studies.
5. Add a final subsection consolidating uncertainty, error analysis, and robustness findings.

## B2-Specific Gaps to Address

- Baselines: justify why rule-based, classical ML, hybrid, and ClimateBERT comparison are the right baselines and what each can and cannot validate.
- Ablations: make the "ablation-like findings" section explicit about what component changes were isolated and what remained constant.
- Hyperparameters and settings: report prompt template versions, model identifiers, temperature, decoding settings, parsing rules, and batching conditions.
- Metrics: justify why parse success, missing-tone rate, schema drift, agreement, and ontology coverage are appropriate; note what they do not capture.
- Class-level reporting: add per-tone and per-pillar results where aggregate percentages could hide weak minority-class behavior.
- Numerical rigor: verify that all percentages, kappas, improvements, and record totals are calculated correctly and use the same denominators throughout.
- Statistical language: use "significant" only when supported by statistical testing or confidence intervals.
- Error analysis: group failures into recurring categories and quantify them with representative examples.
- Qualitative analysis: ensure selected examples represent typical and difficult cases, not only best-case outputs.
- Robustness: compare results across prompts, models, and repeated runs under consistent conditions.

## ML and LLM Procedure Actions

- State whether train/validation/test splits exist; if not, explicitly say this is not a conventional supervised benchmark and avoid benchmark-style overclaiming.
- Confirm whether preprocessing and prompt selection were finalized before any final evaluation slice was interpreted.
- State whether repeated LLM runs were normalized or whether only single-run outputs are reported.
- Confirm that model comparisons use identical input texts and evaluation rules.

## Checks Before Finalizing

- Each result section should answer a specific research question with named evidence.
- Each table should declare its source files, sample size, and comparison condition.
- Each claim of improvement should identify the baseline and denominator.
