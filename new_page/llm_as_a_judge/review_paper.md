# Review Paper: LLM-as-a-Judge for ESG ABSA Extraction Evaluation

Date: 2026-05-30  
Scope: This review is written to support the `llm_as_a_judge/` track in this repository. It focuses on **LLM-as-a-judge** as an evaluation layer for **record-level ESG ABSA-style extraction outputs** (aspect/labels/pillar/tone/sentiment), using the repo’s artifact style (run lineage + structured records).

---

## Abstract

Evaluation is a central bottleneck for information extraction pipelines, especially in ESG settings where outputs must be faithful to source text, consistent with an ontology, and actionable for downstream analysis. Traditional evaluation relies on gold labels, which are expensive and slow to produce, while proxy checks (e.g., parsing success, basic overlap metrics) miss semantic failure modes such as hallucination and subtle misalignment of tone or aspect. “LLM-as-a-judge” has emerged as a practical approach for scalable semantic assessment: a separate large language model is prompted with a rubric to score and diagnose model outputs. This review synthesizes design patterns, failure modes, and experimental protocols for using LLM judges to evaluate ESG ABSA extraction records. It proposes a judge taxonomy tailored to ESG disclosures (faithfulness, completeness, ontology alignment, tone validity, and explanation quality), outlines reliability/validity measurement strategies (self-consistency, inter-judge agreement, calibration with small human subsets), and describes artifact and reporting standards for reproducible, audit-friendly benchmarking. The review concludes with concrete recommendations and a roadmap for implementing judge generation and analysis artifacts compatible with this repository’s existing dataset explorer.

---

## Keywords

LLM-as-a-judge; evaluation; ESG disclosures; aspect-based sentiment analysis (ABSA); information extraction; faithfulness; hallucination; rubric-based scoring; reliability; calibration; error taxonomy; Indonesian sustainability reports.

---

## 1. Introduction

ESG disclosure analysis pipelines increasingly rely on LLMs to extract structured statements from sustainability reports. In this repository, the extraction layer outputs record-level objects that include a statement `text` and derived fields such as `aspect`, `labels`, `esg`, `tone`, `sentiment`, and (sometimes) `reasoning`. The evaluation problem is to determine whether these extracted records are **correct and useful**.

However, evaluation in ESG extraction is difficult for three reasons:

1. **Semantics matter more than syntax.** A record can be valid JSON and still be wrong (e.g., fabricated actions, incorrect tone, wrong label).
2. **Gold annotation is expensive.** High-quality record-level labeling requires domain familiarity and careful reading of source context.
3. **ESG constructs are nuanced.** Tone constructs like *commitment/action/outcome* and multi-label taxonomies require interpretive judgment.

LLM-as-a-judge offers a middle path: use one (or more) LLMs to **score** and **diagnose** extracted records under a structured rubric, producing artifacts that can (i) triage failures, (ii) compare models/prompts, and (iii) prioritize limited human review.

This review paper is organized to be directly actionable for implementing a judge layer in this repo: we review judge styles, judge reliability risks, rubric design, and experiment/reporting standards.

---

## 2. Background: What Does “LLM-as-a-Judge” Mean?

In this paper, “LLM-as-a-judge” refers to a design where:

- The *system under evaluation* (SUE) produces an output `ŷ` for an input `x`.
- A *judge model* consumes `(x, ŷ, rubric)` and returns:
  - structured scores (numeric or ordinal),
  - a decision (accept/revise/reject),
  - and diagnostics (tags + evidence quote + short rationale).

The judge is not assumed to be perfectly correct. Instead, it is treated as a **rater** whose behavior must be measured, calibrated, and constrained.

Two fundamental judge paradigms are common:

1. **Rubric scoring:** judge assigns dimension scores according to a rubric.
2. **Pairwise comparison / ranking:** judge compares two outputs and chooses the better one (sometimes with a margin score).

For this repository’s needs (record-level diagnostics and auditability), rubric scoring is typically the better fit, but pairwise ranking can be useful for prompt/model selection experiments.

---

## 3. Why ESG ABSA Extraction Needs a Judge Layer

### 3.1 Semantic failure modes in ESG records

Extraction pipelines that output structured ESG records face several failure modes that are hard to detect with simple proxies:

- **Hallucination / fabrication:** record asserts an action or result not present in the statement.
- **Over-generalization:** record inflates a narrow statement into a broad sustainability claim.
- **Wrong aspect:** assigns an aspect category that does not match the statement.
- **Label noise:** assigns labels that are plausible in general but unsupported by the statement.
- **Tone misclassification:** labels “action” when only a future intention is stated, or labels “outcome” without measurable achieved results.
- **Incoherent pillar mapping:** assigns `E/S/G` inconsistent with the content.
- **Vague/boilerplate extraction:** output is syntactically valid but semantically empty.

### 3.2 Why judging is especially relevant for bilingual / Indonesian ESG reports

In bilingual contexts (Indonesian with English fragments), LLM outputs can drift due to:

- OCR artifacts and partial translations,
- domain-specific Indonesian phrasing for compliance and commitments,
- mixed reporting styles across companies and years.

A judge that requires **evidence quotes** and provides **failure tags** can expose these issues more effectively than aggregate metrics.

---

## 4. Judge Output Taxonomy for ESG ABSA Records

This section defines what a “complete” judge output should contain when evaluating a record produced by the extraction pipeline.

### 4.1 Unit of evaluation

The unit of evaluation is a **single extracted record**:

- Input to judge:
  - `record.text` (the statement text),
  - `record` fields (`aspect`, `labels`, `esg`, `tone`, `sentiment`, `sentiment_score`, `reasoning`),
  - and lineage metadata (run/model/prompt/target/pages).
- Output from judge:
  - scores + verdict + diagnostics linked to (`run_idx`, `record_idx`).

### 4.2 Recommended rubric dimensions

For ESG ABSA extraction, a practical rubric includes:

1. **Faithfulness (0–4):** Is the structured record supported by the statement text without fabrication?
2. **Completeness (0–4):** Are the fields present and meaningfully filled (not placeholders)?
3. **Ontology alignment (0–4):** Are `aspect` / `labels` / `esg` coherent and consistent with the taxonomy?
4. **Tone validity (0–4):** Is `tone` justified by the language (commitment vs action vs outcome vs none)?
5. **Explanation quality (0–4):** Is `reasoning` (if present) specific and evidence-linked, not generic?

Optionally include:

- **Sentiment validity:** whether sentiment is warranted by the statement tone and wording.
- **Specificity / measurability:** whether “outcome” claims include quantitative evidence.

### 4.3 Verdict and failure tags

To make outputs actionable, judges should produce:

- `verdict`: `accept` / `revise` / `reject`
- `failure_tags`: multi-label set, e.g.:
  - `hallucination`
  - `weak_evidence`
  - `wrong_aspect`
  - `tone_mismatch`
  - `pillar_mismatch`
  - `label_noise`
  - `overgeneralization`
  - `vague_output`
  - `contradictory_fields`

### 4.4 Evidence quoting requirement

A critical guardrail is to require:

- `evidence_quote`: a short excerpt from `text` that supports the judge’s decision.

This improves auditability and reduces “free-form judge hallucination” in rationales.

---

## 5. Judge Design Patterns

### 5.1 Single-judge scoring (baseline)

Use one judge model with a fixed rubric prompt. Advantages: simple and cheap. Risks: idiosyncratic bias and instability.

### 5.2 Self-consistency judging (intra-judge stability)

Run the same judge prompt/model multiple times per record to estimate variance. This exposes:

- sensitivity to sampling,
- borderline cases,
- and dimensions with unstable definitions (often tone validity).

### 5.3 Multi-judge ensembles (inter-judge agreement)

Use multiple judge models (or same model with different system prompts) and:

- compute agreement on verdicts and score bins,
- surface disagreement cases for human review.

The ensemble does not “guarantee truth” but provides uncertainty signals.

### 5.4 Pairwise judging (A/B comparisons)

When comparing extraction prompts or models, pairwise judging can be useful:

- judge chooses which record is better given the same statement text.

Pairwise judgments can be more stable than absolute scoring, but they provide less diagnostic detail unless augmented with tag/rationale extraction.

### 5.5 Hybrid: rubric + pairwise

A practical workflow is:

1. rubric scoring for error taxonomy and analytics,
2. pairwise judging for selecting between candidate extraction prompts/models.

---

## 6. Judge Failure Modes and Biases (and How to Mitigate Them)

Treat judges as fallible raters. Common issues include:

### 6.1 Prompt sensitivity

Small rubric wording changes can shift score distributions.

Mitigation:

- version rubric prompts (`rubric_version`),
- store prompt templates as repo artifacts,
- report score histograms per version.

### 6.2 Leniency/severity drift

Some judges systematically score higher/lower.

Mitigation:

- use calibration sets (small human-labeled subset),
- normalize scores per judge (careful: normalization can hide real differences),
- or use verdict thresholds tuned per judge.

### 6.3 Over-trusting fluent rationales

Judges may produce convincing explanations not grounded in text.

Mitigation:

- enforce `evidence_quote`,
- limit rationale length,
- require that each failure tag is linked to a quote span.

### 6.4 Ontology confusion

Judges may not internalize your label definitions.

Mitigation:

- include concise ontology definitions in the prompt,
- provide positive/negative examples for frequent labels,
- forbid inventing new labels.

### 6.5 Tone construct ambiguity

“Commitment”, “action”, and “outcome” are close but distinct.

Mitigation:

- include crisp definitions + examples,
- add explicit decision rules (e.g., “action requires concrete past/present activities; outcome requires achieved results, ideally measurable”),
- and measure inter-judge disagreement specifically on tone.

---

## 7. Methodological Protocol for a Judge-Based Evaluation Study

This section outlines a defensible protocol suitable for a thesis chapter.

### 7.1 Data preparation

From `results/esg_records.json`:

- flatten run-level and record-level tables,
- add stable IDs (`run_idx`, `record_idx`, and optionally a hash of `text`),
- keep lineage fields: `timestamp`, `model`, `prompt`, `target`, `target_pages`, `ok`, `error_type`.

### 7.2 Sampling design

Avoid judging “everything” first. Use stratified sampling:

- by extraction `model` and `prompt`,
- by `tone` class,
- by frequent `labels` and `aspects`,
- include known failure strata (non-OK runs, long statements, mixed-language statements).

### 7.3 Judge conditions (experiments)

Recommended minimal set:

1. Single judge (baseline rubric v1)
2. Self-consistency on a subset (e.g., N=3 repeats per record)
3. Multi-judge on a smaller subset (2–3 judges)

### 7.4 Metrics and analyses

**Reliability:**

- intra-judge variance across repeats (per dimension),
- inter-judge agreement on verdict and discretized score bins,
- disagreement clustering by tone/aspect/label (where do judges disagree most?).

**Convergent validity (weak anchors):**

- compare judge outcomes vs. run-level `ok` / `error_type`,
- compare distributions across extraction `model` and `prompt`.

**Actionability:**

- top failure tags overall and per model/prompt,
- co-occurrence matrix of failure tags (e.g., `tone_mismatch` often with `overgeneralization`),
- “top fixable categories” (highest count * highest severity).

### 7.5 Reporting standards

A judge-based evaluation paper should report:

- judge model(s), temperature, prompt templates, and rubric versioning,
- sample sizes per stratum,
- agreement/stability metrics with confidence intervals where possible,
- qualitative examples of each major failure tag with evidence quotes.

---

## 8. Artifact Design for Reproducible Judging

To support auditability and reruns, store outputs as first-class artifacts:

### 8.1 Record-level JSONL (`judge_records.jsonl`)

Each line corresponds to one judged record with:

- lineage: `run_idx`, `record_idx`, `timestamp`, `target`, `target_pages`, extraction `model` and `prompt`,
- judge config: `judge_model`, `rubric_version`, `judge_temperature`, `judge_seed` (if used), `rerun_id`,
- rubric outputs: scores + verdict + tags + evidence quote + rationale,
- optional: raw judge response for debugging.

### 8.2 Aggregate summary CSV (`judge_summary.csv`)

Aggregations by:

- extraction model,
- extraction prompt,
- company/target,
- tone/label/aspect strata,
- and verdict counts / mean scores.

### 8.3 Disagreement export (`judge_disagreement.csv`)

For multi-judge or self-consistency runs, export:

- high variance cases,
- or cases where judges disagree on verdict.

These become the best candidates for human labeling.

---

## 9. Relationship to Human Evaluation (Calibration, Not Replacement)

LLM judges should be positioned as:

- a triage and diagnostics layer,
- a way to scale “semantic checks” cheaply,
- not a replacement for ground truth.

A robust workflow:

1. Judge a broad sample → identify failure hotspots.
2. Human-label a small targeted subset (high disagreement + high impact).
3. Calibrate judge thresholds and measure judge-human alignment.
4. Iterate on extraction prompts/models using judge tags and verified cases.

---

## 10. Open Research Challenges (ESG-Specific)

1. **Gold standard scarcity and subjectivity:** ESG statements can be ambiguous; “correct” tone or label may require context.
2. **Temporal context:** outcomes vs commitments can depend on report year and tense.
3. **Cross-sentence context:** short extracted `text` spans may omit context required for faithful interpretation.
4. **Ontology evolution:** ESG label taxonomies evolve; judges must be versioned with the ontology.
5. **Strategic reporting language:** sustainability reports can be intentionally vague; judges need to detect vagueness and reward specificity.

---

## 11. Practical Recommendations (Implementation-Ready)

For implementing LLM-as-a-judge in this repository:

1. Use a **structured JSON schema** for judge output; reject non-conforming responses.
2. Require `evidence_quote` and keep rationales short.
3. Version rubric prompts (`rubric_v1`, `rubric_v2`) and store them in-repo.
4. Start with stratified sampling rather than full-corpus judging.
5. Add self-consistency repeats on a subset to quantify instability.
6. Export `judge_disagreement.csv` and use it to drive human annotation prioritization.
7. Integrate judge artifacts into `llm_as_a_judge/app.py` so results are inspectable and exportable.

---

## 12. Conclusion

LLM-as-a-judge is a pragmatic evaluation layer for ESG ABSA extraction pipelines because it can detect semantic quality failures that proxies miss, produce actionable diagnostics at scale, and guide efficient human review. For this repository’s extraction artifacts, a judge rubric centered on faithfulness, completeness, ontology alignment, and tone validity provides a defensible framework for benchmarking. The key to rigor is to treat judges as raters: measure reliability (self-consistency and inter-judge agreement), calibrate with targeted human subsets, and store outputs as reproducible artifacts with run lineage and evidence quotes. Implemented carefully, the judge layer becomes both a research contribution (evaluation methodology) and an engineering tool (failure taxonomy and iterative improvement loop).

---

## References (to be finalized)

This review paper is intentionally written without hard-coded bibliographic entries to avoid inventing citations. Populate this section using your preferred thesis workflow (Zotero/BibTeX/manual list) with sources covering:

- LLM-as-a-judge / LLM evaluation frameworks (rubric scoring, pairwise judging),
- hallucination/faithfulness evaluation and groundedness,
- inter-rater reliability (weighted kappa, Krippendorff’s alpha) and experimental design,
- ABSA evaluation and ESG/greenwashing NLP literature,
- judge bias and meta-evaluation studies.

