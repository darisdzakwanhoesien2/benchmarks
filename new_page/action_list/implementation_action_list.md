# Action List for `implementation.md`

Source file: `converted_markdown/implementation.md`

## Priority Actions

1. Add explicit inclusion and exclusion criteria for documents, pages, and extracted records.
2. State the sampling pathway clearly: total available PDFs, OCR-processed subset, thesis-facing subset, and pilot-annotated subset, with reasons for each reduction.
3. Describe the annotation and reference-construction procedure step by step, including who annotated, what instructions they used, and how disagreements were handled.
4. Separate weak labels, pilot human labels, and external comparison labels into clearly different evidence tiers.
5. Add a formal subsection on threats to validity covering internal, external, and construct validity.

## B2-Specific Gaps to Address

- Research design: explain why this pipeline-plus-review design is methodologically suitable.
- Datasets and sampling: justify representativeness of Indonesian sustainability reports and state what populations are not covered.
- Inclusion/exclusion: define rules for unusable OCR pages, duplicated pages, non-ESG text, tables, and accounting-policy text.
- Annotation rigor: report annotator expertise, annotation guide, adjudication process, and inter-annotator agreement if available; if unavailable, state it as a limitation and action item.
- Label imbalance: explain how imbalance across ESG pillars and tone classes is measured and handled.
- Data leakage: state how prompt engineering, ontology building, and review files were prevented from using test observations improperly.
- Reproducibility: list artifact locations, prompt files, model backends, run metadata, and resume logic in a single consolidated reproducibility table.
- Development vs. evaluation separation: clarify which artifacts shaped the method and which artifacts are reserved for evaluation.

## ML and LLM Procedure Actions

- State whether preprocessing decisions were fitted only on development data or influenced by broad inspection of final evaluation outputs.
- Document whether prompts changed after examining extracted outputs, and if so, how those comparisons are isolated analytically.
- Report randomness controls: seeds, model versions, API dates, decoding settings, retry behavior, and repeated-run policy.
- Explain whether ClimateBERT comparison uses exactly the same text units and conditions as the tone-evaluation outputs.

## Checks Before Finalizing

- Ensure the methodology can be reproduced from this chapter without relying on hidden implementation assumptions.
- Ensure every claimed artifact path corresponds to a real repository artifact.
- Ensure limitations are method-specific, not only general future-work statements.
