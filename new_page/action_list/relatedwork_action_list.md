# Action List for `relatedwork.md`

Source file: `converted_markdown/relatedwork.md`

## Priority Actions

1. Reorganize the chapter so it does more than survey tools; it should extract methodological lessons directly relevant to dataset design, annotation, evaluation, and validity threats.
2. Add a clearer comparison of prior work on sampling, benchmark construction, annotator expertise, and inter-annotator agreement rather than focusing mainly on model families.
3. Expand the critique of existing studies to show where they fail on reproducibility, external validity, prompt transparency, or weak evaluation design.
4. Use the literature review to justify your own evaluation choices: why record-level units, why tone labels, why ontology alignment, why ClimateBERT comparison, and why partial human review.
5. Replace placeholder table captions with substantive table purposes tied to methodological rigor.

## B2-Specific Gaps to Address

- Summarize how prior studies construct ground truth and whether they use expert annotation, weak labels, or external proxies.
- Identify how existing papers handle class imbalance, uncertainty analysis, error analysis, and qualitative examples.
- Explicitly compare whether prior LLM studies disclose prompt versions, model versions, decoding settings, and rerun consistency.
- Highlight whether prior work uses proper train/validation/test separation or instead relies on ad hoc case studies.
- Extract lessons on representativeness and external validity, especially when datasets are narrow, sector-specific, or English-only.

## Checks Before Finalizing

- Every major subsection should end with a direct implication for your Chapter 3 or Chapter 4 design.
- Avoid descriptive literature listing without methodological synthesis.
- Ensure claims about "state of the art" are supported by concrete evaluation practices, not just newer model names.
