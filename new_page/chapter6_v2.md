# Chapter 6: Conclusion

## 6.1 Contribution Summary

This thesis set out to build an executable ESG aspect-based sentiment analysis framework for Indonesian sustainability reporting. The central contribution is not only a model, but a full document-to-record research workflow that connects OCR, structured extraction, tone-aware labeling, comparative validation, ontology-oriented interpretation, and reproducible reporting artifacts.

The first contribution is the document-to-record pipeline itself. The current repository demonstrates that sustainability-report PDFs can be transformed into page-aware text artifacts and then into structured ESG records while preserving provenance. This is important because ESG disclosure analysis in practice begins with heterogeneous PDFs, not clean benchmark tables.

The second contribution is the record-level ESG schema. The thesis shows that ESG disclosure can be modeled through records containing aspect, pillar, sentiment, tone, and provenance rather than through document-level sentiment alone. This is necessary for distinguishing promise-like language from implemented action and realized outcomes.

The third contribution is the tone-aware disclosure taxonomy. By operationalizing commitment, action, outcome, none, and missing, the system moves ESG analysis beyond generic polarity and toward disclosure posture.

The fourth contribution is the comparative validation layer. The ClimateBERT proxy comparison does not claim conceptual identity, but it provides useful construct-level evidence. The current results report 83.7% proxy agreement and kappa of 0.645, with 91 co-occurrences between `commitment` and `climate-commitment`.

The fifth contribution is the benchmark-construction environment. The project already includes silver-label workflows, review queues, disagreement tables, metrics pages, and dashboard artifacts that make later human evaluation feasible.

The sixth contribution is reproducibility and interpretability infrastructure. The system preserves prompts, run artifacts, figures, documentation, and semantic outputs so that the research process remains auditable after extraction is complete.

### 6.1.1 Answers to the Research Questions

RQ1 is answered positively at the feasibility level. The pipeline already converts sustainability-report PDFs into OCR-derived pages and then into structured ESG records, supported by 23 OCR documents and 332 extracted records.

RQ2 is also answered positively. The current corpus shows that ESG statements can be represented using a record-level schema including aspect, ESG pillar, sentiment, and tone.

RQ3 is answered cautiously but positively. Tone labels and ClimateBERT-style labels align meaningfully, especially in the 91 `commitment` and `climate-commitment` overlaps, but they are not identical constructs.

RQ4 is answered clearly. The current pipeline reveals its own weaknesses through 61 missing-tone records, schema drift in sentiment fields, and sparse social-pillar coverage.

RQ5 is answered positively. Static charts, review tables, dashboards, and documentation materially improve the auditability of ESG extraction experiments.

RQ6 is answered partially. Prompt and model choices clearly influence extraction stability, but stronger causal comparison requires more tightly matched runs and fuller annotation.

Taken together, the findings show that automated tone-aware ESG disclosure analysis is feasible and analytically useful, but still dependent on stronger validation before broad generalization.

## 6.2 Practical Implications

For ESG analysts, the pipeline reduces the burden of manually searching long reports by surfacing structured evidence records and making commitment-outcome imbalance visible.

For sustainability report authors, the system offers a feedback mechanism on disclosure posture. Reports dominated by commitments rather than actions or outcomes can be identified and revised more deliberately.

For regulators and standards-oriented reviewers, especially in OJK-aligned reporting contexts, the system can support triage rather than autonomous judgment. It can help identify sections where rhetoric is abundant but evidence is weak or structurally unclear.

For investors, the system provides a supplement to abstract ESG ratings. Tone-aware record analysis can reveal whether a sustainability narrative is primarily promissory, operational, or outcome-focused.

## 6.3 Future Work

The first priority for future work is a larger expert-labeled benchmark with inter-annotator agreement. This is the most direct path toward defensible supervised evaluation.

The second priority is formal OCR quality measurement using representative page samples and metrics such as character error rate, word error rate, and table extraction quality.

The third priority is validation of the greenwashing-oriented rhetoric-to-results index against known cases, controversy signals, or external ESG benchmarks.

The fourth priority is ontology expansion, especially for Indonesian-specific governance and social disclosure language.

The fifth priority is multilingual model development through fine-tuning or instruction tuning on Indonesian-English ESG corpora.

The sixth priority is full one-to-one ClimateBERT evaluation over all 332 extracted records so that external comparison becomes more rigorous.

Overall, the thesis demonstrates that the current pipeline is already a meaningful research instrument. Its next stage is not conceptual reinvention, but validation deepening: stronger labels, stronger OCR measurement, stronger matched-model comparison, and broader ontology coverage.
