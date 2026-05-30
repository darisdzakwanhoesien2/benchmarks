# Research Plan: LLM-as-a-Judge for ESG ABSA Extraction Benchmark

This research plan builds directly on the existing benchmark artifacts produced by the ESG pipeline and stored in this repository—especially `results/esg_records.json` (T3 extraction outputs with run metadata and nested extracted records).

## 1) Research Gap

The current evaluation layer in the repository is primarily oriented around:

- **Syntactic validity** (e.g., JSON parse success, missing fields, error types),
- **Proxy agreement checks** (e.g., label overlap and tone vs ClimateBERT-style proxies), and
- **Limited human/pilot anchoring** (small-scale manual checks and dashboards).

What is missing is a **structured semantic evaluation layer** that can score whether each extracted ESG record is:

- **Faithful** to the source statement,
- **Complete** (key fields are present and meaningfully filled),
- **Consistent** with the benchmark’s ontology/labels/tone constructs, and
- **Justified** with auditable, record-level diagnostics.

In short: the pipeline can produce extraction records at scale, but it lacks a reproducible **LLM-as-a-judge** framework that evaluates *semantic quality* beyond “did it parse?” and “did the label match a proxy?”.

## 2) Research Questions

RQ1. **Judge validity**: Can an LLM judge reliably score ESG extraction record quality (faithfulness, completeness, schema adherence, and evidence grounding) using only existing run artifacts?

RQ2. **Judge reliability**: How stable are judge scores across:

- judge model choice,
- prompt/rubric wording,
- reruns (self-consistency),
- document context (targets/pages)?

RQ3. **Convergent validity**: To what extent do judge scores correlate with currently available anchors:

- parse-success/error categories,
- proxy tone/label signals (e.g., ClimateBERT-style comparisons),
- any existing pilot/human-labeled subsets?

RQ4. **Actionability**: Do judge-generated tags and rationales produce a more actionable failure taxonomy than parse-only diagnostics (e.g., hallucination vs weak evidence vs wrong aspect vs tone mismatch)?

## 3) Research Objectives

O1. Define a rubric-based judge schema for record-level evaluation of `results/esg_records.json` outputs.

O2. Produce **reproducible judge artifacts** (JSONL/CSV) linked to run metadata:

- run timestamp, model, prompt,
- target and target_pages,
- record index (run_idx, record_idx),
- judge config (judge model, rubric version, temperature, etc.).

O3. Benchmark multiple judge configurations:

- single-judge scoring,
- multi-judge ensemble agreement,
- self-consistency reruns (same judge, repeated).

O4. Quantitatively assess reliability/validity:

- inter-judge agreement (e.g., Krippendorff’s alpha / weighted kappa where applicable),
- rerun variance,
- correlations with available anchors (parse success, proxy label/tone constructs).

O5. Integrate judge outputs into the existing Streamlit analytics workflow so results are visible, filterable, and exportable for thesis Chapters 4–6.

## 4) Research Contributions

This work contributes:

1. A **domain-specific LLM-as-a-judge protocol** for ESG ABSA extraction on bilingual sustainability-report data.
2. A **reproducible, auditable judging pipeline**: judge outputs stored as first-class artifacts with clear lineage back to runs and record IDs.
3. A **multi-dimensional semantic quality signal** (faithfulness, completeness, ontology alignment, tone validity) that complements parse success.
4. A bridge between weak proxies and expensive annotation: judge outputs can prioritize where human review yields the most value.
5. A refined, record-level **error taxonomy** separating syntactic failures from semantic failures.

## 5) Topics for Literature Review

Focus the literature review around:

1. **LLM-as-a-judge** frameworks: rubric-based scoring, pairwise ranking, and self-consistency evaluation.
2. **Faithfulness / hallucination evaluation**: groundedness, citation/evidence attribution, and source-backed scoring.
3. **Meta-evaluation and judge biases**: position bias, verbosity bias, self-preference, prompt sensitivity, and calibration strategies.
4. **Reliability measurement**: inter-rater agreement metrics and experimental designs for judge consistency.
5. **ESG NLP + ABSA evaluation**: domain adaptation, bilingual challenges, label/ontology design, and evaluation scarcity.

## 6) Methodology

### 6.1 Data and Units of Analysis (Existing Dataset)

Primary dataset:

- `results/esg_records.json`: list of T3 runs containing run metadata and nested `records[*]` items.

Unit of analysis:

- **Record-level extraction**: each `records[*]` contains at least `text`, `aspect`, `labels`, `esg`, `tone`, `sentiment`, `sentiment_score`, `reasoning`.

Optional anchors (if present in repo outputs):

- Parse/error diagnostics derived from `ok`, `error`, `error_type`, and raw output fields.
- Any existing stability summaries (model/prompt) and tone-proxy comparisons.

### 6.2 Judge Rubric (Proposed)

For each extracted record, the judge returns:

- `faithfulness_score` (0–4): supported by statement text and not fabricated.
- `completeness_score` (0–4): key fields present and meaningful.
- `ontology_alignment_score` (0–4): aspect/labels/esg mapping coherent.
- `tone_validity_score` (0–4): commitment/action/outcome assignment justified by wording.
- `reasoning_quality_score` (0–4): explanation is specific, concise, non-generic.
- `overall_score` (0–100): weighted composite.

Plus structured diagnostics:

- `verdict_label`: `accept` / `revise` / `reject`
- `failure_tags`: multi-label, e.g. `hallucination`, `weak_evidence`, `wrong_aspect`, `tone_mismatch`, `label_noise`, `overgeneralization`
- `evidence_quote`: a short quote from the record’s `text` used for justification (not the whole page)
- `judge_rationale`: short explanation anchored to the evidence quote

### 6.3 Experimental Design

1. **Sampling**:
   - Stratify by model, prompt, company/target, and outcome (`ok`, error types).
   - Include records with `tone=none` and non-none, and a spread across frequent labels.
2. **Judge conditions**:
   - Single judge model (baseline).
   - Multi-judge ensemble (2–3 judge models).
   - Self-consistency (N reruns per record under same rubric).
3. **Metrics**:
   - Agreement: weighted kappa / alpha (where applicable), disagreement rates.
   - Stability: per-dimension variance across reruns.
   - Validity: correlation with available anchors (parse success, tone proxy, etc.).

### 6.4 Implementation and Artifacts

Outputs to store under `results/llm_judge/`:

- `judge_records.jsonl`: one line per judged record with full lineage fields.
- `judge_summary.csv`: aggregated stats by model/prompt/target/label/tone.
- `judge_disagreement.csv`: high-disagreement cases for review.

Streamlit deliverable:

- A dedicated app in `llm_as_a_judge/` to load `results/esg_records.json`, load judge outputs if present, compute summaries, filter, and export.

## 7) Results Interpretation (Planned)

Interpret results along four axes:

1. **Semantic vs syntactic gap**: cases where parse success is high but faithfulness is low.
2. **Construct boundaries**: when tone proxies and judge tone-validity disagree (e.g., “action” predicted without concrete actions).
3. **Stability**: judge rerun variance and whether instability clusters by prompt/model/target.
4. **Failure-mode taxonomy**: distribution of failure tags and their association with upstream errors.

## 8) Discussion (Planned)

Key thesis discussion points:

- **Utility**: judge as triage to reduce manual review, not a replacement for human labels.
- **Bias and limitations**: prompt sensitivity, judge model preference, verbosity bias.
- **Calibration**: how small human gold sets can calibrate judge thresholds.
- **Engineering implications**: robust pipelines need both parser-level gates and semantic judge gates.

## 9) Conclusion (Planned)

This benchmark is technically ready for LLM-as-a-judge because it already stores:

- structured extraction outputs,
- run metadata and prompts,
- error diagnostics and stability artifacts.

The primary contribution is a calibrated semantic evaluation layer that improves methodological rigor and provides actionable diagnostics for iterative extraction improvements.

