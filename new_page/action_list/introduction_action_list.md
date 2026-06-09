# Action List for `introduction.md`

Source file: `converted_markdown/introduction.md`

## Priority Actions

1. Tighten the research-design framing so the introduction states exactly what kind of study this is: executable mixed-methods, pipeline evaluation, comparative prompt/model study, or benchmark construction work.
2. Add an explicit early statement on the unit of analysis: report, page, page-batch, record, and annotated sample, because later rigor claims depend on that distinction.
3. Refine the problem statement so it separates methodological gaps from engineering gaps: sampling, annotation scarcity, construct validity, reproducibility, and data leakage risk should not be mixed together.
4. Reword the research questions so they can be answered by measurable evidence rather than general narrative claims.
5. Add a short statement previewing the evaluation boundary: the thesis uses partial human annotation and weak-reference layers, not a full gold-standard benchmark.

## B2-Specific Gaps to Address

- Define the suitability of the research design and why it matches the thesis objective better than a single-model classification study.
- Preview dataset scope and sampling logic at a high level, including why Indonesian reports are selected and what that limits.
- State the expected inclusion and exclusion logic for report selection and extracted text units.
- Clarify construct validity early: tone, sentiment, ESG aspect, and ClimateBERT-style labels are related but not interchangeable constructs.
- Add a brief reproducibility claim only if later chapters actually report prompts, model versions, run settings, and data splits consistently.

## Checks Before Finalizing

- Ensure each research question maps to a later chapter section and metric.
- Ensure terms like "validated", "reproducible", or "reliable" are not overstated before the evidence is shown.
- Ensure no causal or generalization claim is made here that later chapters cannot defend empirically.
