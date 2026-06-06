# Chapter 5: Discussion

## 5.1 Comparison with Existing Methods

The results in Chapter 4 suggest that the proposed system should not be understood as a narrow classifier. It is better viewed as an integrated ESG evidence-construction environment. For that reason, the most appropriate comparison is not only with a single benchmark model, but with four common alternatives: manual ESG review, pure LLM extraction, ClimateBERT-only approaches, and rule-based taxonomies.

Manual ESG review remains the most context-sensitive approach. Human analysts can resolve ambiguity, recognize disclosure nuance, and distinguish intention from performance more carefully than a prototype system. However, manual review is expensive, difficult to scale, and often weak in structured artifact generation. The present system adds value by converting long reports into comparable record-level evidence while preserving provenance for later human inspection.

Pure LLM extraction is faster than manual review, but it often hides instability. If a workflow only keeps successful JSON outputs and ignores parse failures, empty runs, or field drift, it risks overstating reliability. The current system improves on this by treating prompt sensitivity, schema drift, missing fields, and disagreement as research evidence rather than as invisible implementation noise.

ClimateBERT-only approaches are a useful third comparison point. They are strong for climate-focused semantics, but they do not directly model the broader ESG scope or the distinction between commitment, action, and outcome. The current proxy agreement results show that ClimateBERT-style labels are valuable as an external reference signal, but they do not replace a tone-aware ESG schema.

Rule-based ESG taxonomies provide transparency and low computational cost, but they struggle with bilingual, context-dependent, and rhetorically varied disclosure language. The current system is more flexible because it combines semantic extraction with downstream interpretability layers such as ontology mapping and dashboard review.

Across these alternatives, the main value added by the thesis system is integration. It scales beyond manual reading, is more auditable than pure prompting, is broader than ClimateBERT-only classification, and is more adaptable than deterministic lexicons.

## 5.2 Interpretation of Key Findings

Three findings are especially important for interpretation: the dominance of commitment tone, the alignment between commitment and climate-commitment labels, and the fragility of governance-oriented tone assignment.

### 5.2.1 Commitment Tone Dominance

The most visible empirical pattern is the dominance of commitment tone. Out of 332 records, 115 are classified as `commitment`, compared with 58 `action` records and 50 `outcome` records. This suggests that the sampled disclosure environment is more future-facing than results-focused. Companies often describe plans, intentions, or targets rather than only reporting completed achievements.

This finding is important because it supports the thesis argument that disclosure posture is analytically distinct from sentiment polarity. A statement may sound positive while still representing only a promise. Without the tone dimension, this difference would be difficult to operationalize.

### 5.2.2 Alignment with Climate-Commitment Labels

The second key finding is the strong overlap between `commitment` tone and `climate-commitment` labels. The current project summary reports 91 such co-occurrences, alongside 83.7% proxy agreement and kappa of 0.645. This is a useful validation signal because it suggests that the commitment category is not purely an artifact of prompt wording. It often corresponds to recognizable climate-oriented forward-looking disclosure.

At the same time, the overlap should not be overstated. Climate labels and ESG tone are related constructs, not identical ones. The comparison therefore strengthens plausibility, but it does not eliminate the need for human evaluation.

### 5.2.3 Governance Fragility and Missing Tone

The third major finding concerns the 61 missing-tone records and the broader difficulty of classifying governance-oriented text. Governance language is often procedural, compliance-heavy, and descriptively formal. Such statements may not fit neatly into the commitment-action-outcome taxonomy that works more naturally for environmental reporting.

This is one of the most informative weaknesses in the system. It suggests that some extraction problems are not only model failures; they may also indicate conceptual tension between the taxonomy and the linguistic style of governance disclosure. The pipeline is valuable precisely because it surfaces this problem instead of masking it.

## 5.3 Theoretical Implications

The findings can be interpreted through four main theoretical lenses: legitimacy theory, stakeholder theory, ABSA theory, and greenwashing-oriented disclosure theory.

Legitimacy theory helps explain why commitment language dominates. Organizations often use sustainability disclosure to signal alignment with expected norms and future responsibility. A commitment-heavy corpus is consistent with such signaling behavior, even when outcome reporting is less frequent.

Stakeholder theory helps explain the pillar distribution. The current results show strong environmental and governance presence but very sparse social coverage. This may reflect the kinds of issues companies perceive as most salient to investors, regulators, and formal reporting audiences.

ABSA theory is extended by the thesis because polarity alone is not enough for ESG reporting. The distinction between commitment, action, and outcome shows that the meaning of a disclosure depends not only on what topic is mentioned and whether the wording is positive or negative, but also on what kind of claim is being made.

Greenwashing-oriented theory is relevant because the commitment-to-outcome imbalance creates a computationally tractable signal of rhetorical asymmetry. The thesis does not claim to solve greenwashing detection conclusively, but it does show how tone-aware extraction can support that research direction more directly than sentiment-only analysis.

## 5.4 Limitations

The most important limitation is the absence of a full expert-labeled ground truth. The current 332 records support exploratory analysis and benchmark construction, but they do not yet justify final supervised performance claims.

The second limitation is weak external validation. ClimateBERT proxy comparison is useful, but it is not equivalent to a full one-to-one benchmark across the complete corpus. Silver labels similarly support review, not final truth.

The third limitation is OCR uncertainty. OCR quality is clearly important, yet it has not been quantified with formal CER or WER reporting across representative page types. Some downstream extraction failures may therefore originate upstream.

The fourth limitation is prompt and model sensitivity. Seven prompt templates and multiple backends make the system experimentally rich, but they also introduce instability. Some cross-model comparisons remain confounded because not all models processed the same documents under the same conditions.

The fifth limitation is that the greenwashing index is heuristic. It is analytically useful for screening rhetoric-to-results imbalance, but it has not yet been validated against external outcomes or known controversy benchmarks.

The sixth limitation concerns ontology scope and social-pillar sparsity. The current ontology and extraction logic may not fully capture Indonesian-specific disclosure language, and the very low number of social records limits broad S-pillar conclusions.

Taken together, these limitations set a clear boundary. The current system is strong as an executable prototype, a record-level disclosure framework, and a benchmark-construction environment. It is weaker as a finished supervised benchmark or a definitive greenwashing detector. That distinction is not a defect in the thesis argument; it is part of its methodological honesty.
