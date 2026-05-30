# Complete Research Write-up: LLM-as-a-Judge for ESG ABSA Extraction Quality

This document turns the existing `llm_as_a_judge/` Streamlit explorer and the repository’s current extraction artifacts into a defensible thesis-style chapter structure: **research gap, research questions, research objectives, research contribution, literature review, methodology, results, discussion, and conclusion**.

It is written to match what currently exists in this repository today (as of **2026-05-30**):

- Streamlit dataset explorer + optional judge viewer: `llm_as_a_judge/app.py`
- Judge research plan baseline: `llm_as_a_judge/research_plan.md`
- Primary extraction artifact (T3): `results/esg_records.json`
- Optional judge artifact location (not yet present by default): `results/llm_judge/`

If you want this chapter to become “implementation-complete” (end-to-end judge generation + reliability/validity results), follow the “Next Steps” at the end and in `progress_notes.md` and `llm_as_a_judge/progress_notes.md`.

---

## 1. Background and Problem Statement

The repository already implements an OCR → extraction → ABSA-style structuring workflow that produces record-level ESG disclosures with fields such as:

- `text` (the extracted statement),
- `aspect`,
- `labels` (multi-label tags),
- `esg` (pillar mapping),
- `tone` (e.g., `commitment`, `action`, `outcome`, or `none`),
- `sentiment` and `sentiment_score`,
- `reasoning` (model explanation, if provided).

These outputs are stored in `results/esg_records.json` and support analysis of *what companies say* and *how they frame it*.

However, research-grade benchmarking of extraction systems requires more than “did it parse?” or “did it produce output?”. The critical missing layer is a **semantic quality evaluation framework** that can answer questions such as:

- Is each extracted record **faithful** to the statement text (no fabrication / hallucination)?
- Is it **complete** and meaningfully filled (vs. vague boilerplate)?
- Is it **consistent** with the benchmark ontology (aspect, label sets, pillar mapping, tone constructs)?
- Does it include **auditable diagnostics** that help improve upstream extraction prompts and pipelines?

This is where **LLM-as-a-judge** becomes a practical methodology: use a separate rubric-driven model (or multiple) to score and tag extraction records at scale.

---

## 2. Research Gap

The evaluation layer implied by the current repository artifacts emphasizes:

1. **Syntactic success** (e.g., parse success, error types like `connection`/`parse`),
2. **Proxy signals** (e.g., label overlap, tone comparisons, or heuristic dashboards), and
3. **Ad-hoc manual checks** (through interactive browsing).

What is missing for a complete benchmark is a reproducible, record-level **semantic evaluation layer** that is:

- **Rubric-based** (clear definitions per score dimension),
- **Auditable** (structured diagnostics and evidence quoting),
- **Reproducible** (stored artifacts with run lineage), and
- **Measurable** (agreement/stability metrics and correlations with existing anchors).

In short: the repo can produce extraction records at scale, but lacks a scalable method to evaluate *semantic correctness* and to prioritize which records require human review.

---

## 3. Research Questions

**RQ1 (Judge Validity):**  
Can an LLM judge reliably score ESG extraction record quality (faithfulness, completeness, ontology alignment, tone validity) using only existing run artifacts?

**RQ2 (Judge Reliability):**  
How stable are judge scores across:

- judge model choice,
- rubric wording / prompt template,
- reruns (self-consistency under the same judge),
- document context constraints (target and page range)?

**RQ3 (Convergent Validity):**  
To what extent do judge scores correlate with available anchors already present in the repo outputs (e.g., run-level `ok`, error types, record metadata, tone/label distributions)?

**RQ4 (Actionability):**  
Do judge-generated failure tags and rationales produce a more actionable error taxonomy than syntactic diagnostics alone (e.g., separating `hallucination` from `wrong_aspect` from `tone_mismatch`)?

---

## 4. Research Objectives

1. Define a **judge rubric** and schema for record-level evaluation of `results/esg_records.json`.
2. Produce **reproducible judge artifacts** linked to run lineage:
   - `run_idx`, `record_idx`, `timestamp`, `model`, `prompt`, `target`, `target_pages`,
   - judge model/config, rubric version, temperature/seed where applicable.
3. Benchmark multiple judge configurations:
   - single-judge baseline,
   - multi-judge (2–3) agreement/ensemble,
   - self-consistency reruns (same judge, repeated N times).
4. Quantitatively assess reliability and stability:
   - agreement metrics where applicable (e.g., weighted kappa / Krippendorff’s alpha),
   - rerun variance and disagreement clustering by prompt/model/aspect/tone.
5. Integrate judge results into the existing Streamlit workflow so judge outcomes are visible, filterable, and exportable.

---

## 5. Research Contributions

This work contributes:

1. A **domain-specific LLM-as-a-judge protocol** for ESG ABSA-style record extraction, explicitly covering tone constructs (`commitment`/`action`/`outcome`) and ontology mapping (aspect/labels/pillar).
2. A **reproducible judging pipeline** that stores judge outputs as first-class artifacts with clear lineage back to each extraction record.
3. A **multi-dimensional semantic quality signal** that complements syntactic success, enabling prioritization and targeted upstream improvements.
4. A refined **failure taxonomy** separating syntactic failures from semantic failures (e.g., faithful-but-incomplete vs. complete-but-unfaithful).
5. A practical bridge between weak proxies and expensive annotation: judge results can select high-value samples for human review.

---

## 6. Literature Review (Focused Topics)

The literature review should be structured around the methodological risks and requirements of LLM judging (rather than generic “LLM eval” surveys):

1. **LLM-as-a-judge frameworks**: rubric-based scoring, pairwise ranking, and evaluator prompting strategies.
2. **Faithfulness / groundedness evaluation**: hallucination detection, evidence-based scoring, and quote-based rationales.
3. **Judge biases and meta-evaluation**: prompt sensitivity, position bias, verbosity bias, self-preference, and calibration.
4. **Reliability measurement**: treating judges as “raters” and using agreement/stability analysis (inter-rater, intra-rater).
5. **ESG NLP + ABSA evaluation**: ontology design, bilingual issues (Indonesian/English), scarcity of gold labels, and evaluation tradeoffs.

Repo-specific requirement for literature alignment:

- The judge must produce **structured outputs** (not only free-text) and must be evaluated on **consistency and actionable diagnostics**, not only correlation with proxies.

---

## 7. Methodology

### 7.1 Data and Units of Analysis (Existing Artifacts)

Primary dataset:

- `results/esg_records.json`: a list of extraction runs containing run metadata and nested `records[*]`.

Unit of analysis:

- **Record-level extraction**: each record includes statement text and structured fields to be evaluated.

Lineage fields already available in `results/esg_records.json`:

- Run-level: `timestamp`, `model`, `prompt`, `target`, `target_pages`, `ok`, `error_type`, `raw_output`, `background_job_id`.
- Record-level: `text`, `aspect`, `labels`, `esg`, `tone`, `sentiment`, `sentiment_score`, `reasoning`.

### 7.2 Judge Rubric and Output Schema (Proposed)

For each extraction record, the judge returns a structured object with:

**Scores (0–4 each):**

- `faithfulness_score`: Is the structured record supported by the record’s `text` without fabrication?
- `completeness_score`: Are key fields present and meaningfully filled?
- `ontology_alignment_score`: Are `aspect`, `labels`, and `esg` coherent and consistent?
- `tone_validity_score`: Is the assigned tone justified by the language in `text`?
- `reasoning_quality_score`: Is the extraction reasoning specific and non-generic (when present)?

**Decision + diagnostics:**

- `verdict`: `accept` / `revise` / `reject`
- `failure_tags`: multi-label set (e.g., `hallucination`, `weak_evidence`, `wrong_aspect`, `tone_mismatch`, `label_noise`, `overgeneralization`)
- `evidence_quote`: short quote from `text` used to justify the score
- `judge_rationale`: concise, evidence-anchored explanation

**Composite:**

- `overall_score` (0–100), computed from weighted rubric dimensions.

### 7.3 Experimental Design (Planned)

1. **Sampling strategy**
   - Stratify by extraction model and prompt.
   - Include a spread across tone classes and frequent label/aspect categories.
   - Include both “OK” and failure modes (e.g., parse failures where records exist vs. missing records).
2. **Judge conditions**
   - Baseline single judge.
   - Multi-judge ensemble (2–3 judges) for agreement analysis.
   - Self-consistency reruns (same judge, N repeats).
3. **Metrics**
   - Agreement: weighted kappa / alpha on discrete score bins or verdict labels.
   - Stability: per-dimension score variance across reruns.
   - Convergent validity: correlation between judge outcomes and available anchors (run `ok`, error categories, tone/label distributions).
   - Actionability: frequency and clustering of failure tags; “top fixable causes”.

### 7.4 Implementation Plan and Artifacts

Judge outputs are stored under `results/llm_judge/`:

- `judge_records.jsonl`: one line per judged record with full lineage and rubric outputs.
- `judge_summary.csv`: aggregated stats by model/prompt/company/label/tone.
- (Optional) `judge_disagreement.csv`: cases with high inter-judge disagreement for manual review.

The Streamlit app `llm_as_a_judge/app.py` is already prepared to load:

- `results/esg_records.json` (required),
- `results/llm_judge/judge_records.jsonl` (optional),
- `results/llm_judge/judge_summary.csv` (optional).

---

## 8. Results (What Exists Today)

This section reports **repo-grounded results and readiness evidence** available as of **2026-05-30**, even before judge generation is implemented.

### 8.1 Dataset Readiness Snapshot (`results/esg_records.json`)

From a repo-local scan of `results/esg_records.json` (recorded on 2026-05-30):

- Total runs: **1,012**
- OK runs (`ok=true`): **658**
- Runs with at least one extracted record: **544**
- Total extracted records across runs with records: **5,112**
- Unique extraction models observed: **4**
- Most common error types among non-OK runs: `connection` (dominant), `unknown`, `parse`, `timeout`

Record distributions show the dataset is semantically diverse and suitable for judge evaluation:

- Tone counts: `none` (1,806), `action` (1,452), `outcome` (973), `commitment` (878)
- ESG counts: `E` (2,409), `G` (1,228), `S` (828), plus small counts of mixed/other labels (`NONE`, `ESG`, etc.)
- Frequent label tags include: `environmental-claims`, `governance`, `strategy`, `metrics`, and `climate-*` variants.

### 8.2 Tooling Readiness (`llm_as_a_judge/app.py`)

The Streamlit app already supports:

- Loading and flattening run-level and record-level tables from `results/esg_records.json`,
- Dataset snapshots and categorical distributions (model, ok status, tone, ESG),
- Record browsing (including `text` and `reasoning`),
- Optional loading of judge artifacts from `results/llm_judge/` when present.

### 8.3 What Is Not Yet Available

The following are **not yet produced** in the repo by default:

- `results/llm_judge/judge_records.jsonl`
- `results/llm_judge/judge_summary.csv`
- Quantitative judge reliability and validity metrics

Therefore, judge-based “accuracy” claims are intentionally deferred to future work; current results are readiness evidence.

---

## 9. Discussion

### 9.1 Why LLM-as-a-Judge Fits This Repo

This repository already stores the key prerequisites for reproducible judging:

- Record-level structured outputs (with text and categorical fields),
- Run metadata (model, prompt, timestamp, target/page range),
- Run outcomes and error modes (`ok`, `error_type`).

These enable judge outputs to be traceable and auditable, avoiding the “black-box eval” problem.

### 9.2 Risks and Limitations (Planned Mitigations)

1. **Prompt sensitivity**
   - Mitigation: rubric versioning and prompt ablations stored in judge artifacts.
2. **Judge instability**
   - Mitigation: self-consistency reruns and variance reporting.
3. **Biases (verbosity, style preference, polarity)**
   - Mitigation: constrain judge output schema; require `evidence_quote`; emphasize record faithfulness over fluency.
4. **No human gold standard yet**
   - Mitigation: build a small adjudicated subset focused on high-disagreement or high-impact cases.

### 9.3 Engineering Implication

In this benchmark, syntactic gates and semantic gates should both exist:

- Syntactic gate: parse success, missing-field checks.
- Semantic gate: judge faithfulness/completeness/tone validity + failure tags.

This combination supports a practical iterative loop: improve extraction prompts/models based on the judge’s actionable failure taxonomy.

---

## 10. Conclusion

The repository is technically ready for a defensible LLM-as-a-judge research chapter because it already contains:

- A large corpus of structured extraction outputs (`results/esg_records.json`) with lineage fields,
- An interactive Streamlit explorer (`llm_as_a_judge/app.py`) designed to ingest both extraction records and judge artifacts,
- A research plan that specifies the intended rubric and experimental design (`llm_as_a_judge/research_plan.md`).

The primary remaining work is to implement the judge generation pipeline, store outputs as reproducible artifacts, and report reliability/validity results with clear limitations.

---

## Next Steps (Implementation Checklist)

1. Implement an offline judge runner (script) that:
   - reads `results/esg_records.json`,
   - samples or iterates records,
   - calls a judge model with the rubric,
   - writes `results/llm_judge/judge_records.jsonl` and `results/llm_judge/judge_summary.csv`.
2. Add agreement/stability analysis:
   - self-consistency reruns,
   - multi-judge comparisons,
   - export disagreement cases for manual review.
3. Add a small human annotation subset:
   - prioritize high-disagreement and high-impact categories,
   - compute judge-human calibration and threshold selection.
4. Extend the Streamlit app to:
   - summarize judge outcomes by model/prompt/tone/label,
   - surface worst-performing categories,
   - filter and export “reject / revise” cases.

