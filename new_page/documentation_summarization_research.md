# Summarization Research Track — Indonesian ESG ABSA (Repo-Integrated Study)
codex resume 019e785d-b5b7-79e3-82a1-f8d76b89d25b

Date: 2026-05-30

This document turns the existing summarization workspace in this repository into a complete, thesis-style **summarization research track**. It is written to be executable and auditable against the current code and artifacts already present in the repo.

**Repo anchors**
- Summarization UI + baselines: `summarization/app.py`
- Summarization framing (existing): `documentation_summarization.md`
- Available evidence metrics snapshot: `results/thesis_workflow_dashboard/dashboard_metrics.json`
- Agreement summary (tone vs ClimateBERT proxy): `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv`

---

## 1) Research Gap

General summarization research provides strong baselines (extractive ranking, neural abstractive models) and standard overlap metrics (ROUGE). However, **Indonesian ESG disclosure summarization** in this repo has additional requirements that are not fully addressed by generic summarization setups:

1. **Auditability / traceability**: summaries must remain linkable to source pages and structured ESG evidence records (ABSA fields), not only to raw text.
2. **Faithfulness under OCR noise**: OCR errors and table extraction artifacts create conditions where abstractive summarizers can hallucinate or “smooth over” missing facts; factual consistency evaluation becomes central (Maynez et al., 2020). citeturn0search1
3. **ABSA-aligned content coverage**: ESG summaries must preserve aspects, ESG pillars, and tone/sentiment signals, not merely salient sentences.
4. **Reproducibility in an applied benchmark**: the repo currently emphasizes stability/diagnostics for extraction and labeling; summarization needs similarly rigorous, repeatable outputs and quality checks.

In short, the gap is not “we need a summarizer,” but “we need a summarization layer that is **ABSA-aware, evidence-grounded, and evaluation-driven** for Indonesian sustainability-report narratives.”

---

## 2) Research Questions

RQ1. **Feasibility**: Can the existing ABSA/extraction artifacts in this repository support faithful, usable ESG summaries at record-, company-, and chapter-level granularity?

RQ2. **Strategy tradeoffs**: How do extractive baselines (Lead, frequency, TextRank-like) compare to constrained/hybrid summarization for ESG narrative utility and evidence traceability?

RQ3. **Faithfulness**: What is the hallucination / unfaithfulness risk for ESG summarization in an OCR-to-LLM pipeline, and which automatic checks correlate best with human judgments of factuality? citeturn0search1turn1academia12turn2search12turn2search0

RQ4. **ABSA alignment**: To what extent do generated summaries preserve (a) key aspects, (b) ESG pillar coverage, and (c) tone/commitment signals from the structured records?

RQ5. **Downstream value**: Does a summarization layer improve interpretability and reporting efficiency beyond record-level tables (e.g., for thesis chapters and stakeholder narratives), without sacrificing auditability?

---

## 3) Research Objectives

O1. **Build** a reproducible summarization pipeline that consumes existing repo artifacts (OCR text, extracted ESG records, tone/ABSA tables) and exports standardized summary outputs.

O2. **Compare** summarization strategies:
- Extractive baselines (already implemented in `summarization/app.py`)
- Abstractive (LLM-based) constrained by ABSA/evidence inputs (to be implemented)
- Hybrid: extractive evidence scaffold + abstractive rewrite with validation checks (to be implemented)

O3. **Evaluate** with a multi-dimensional framework:
- overlap/coverage (ROUGE, aspect coverage rates)
- faithfulness/factual consistency (automatic + human audits)
- usability/readability (human preference + task-based utility)

O4. **Integrate** outputs into thesis/dashboard artifacts under `results/` and link summaries back to evidence sources.

---

## 4) Expected Research Contributions

1. **ABSA-aware summarization protocol** for Indonesian ESG disclosures: summary units explicitly linked to aspect/pillar/tone distributions.
2. **Evidence-grounded summary representation** that preserves traceability to source pages/records.
3. **Evaluation harness** that treats faithfulness as a first-class requirement, using established factual-consistency research to guide design. citeturn0search1turn1academia12turn2search12turn2search0turn0search17
4. **Practical artifact set**: standardized summary exports (CSV/JSON) + audit tables for thesis writing and reproducible reporting.

---

## 5) Literature Review (Focused)

### 5.1 Extractive Summarization Baselines

- **Lead baseline** (take the first sentences) is a strong, simple benchmark in news-style text; in ESG reports it serves as a sanity check for “early-page bias.”
- **Graph-based ranking (TextRank)** ranks sentences via a PageRank-style algorithm on a similarity graph, often used as an unsupervised extractive baseline. citeturn0search14

### 5.2 Abstractive Summarization Models and Pretraining

Modern summarization is frequently improved by sequence-to-sequence pretraining:
- **BART**: denoising seq2seq pretraining that transfers well to summarization tasks. citeturn1search1
- **PEGASUS**: pretraining objective based on predicting “gap sentences,” designed to match summarization. citeturn1academia13

For multilingual settings (relevant to Indonesian):
- **mBART** demonstrates multilingual denoising pretraining for seq2seq transfer. citeturn3search0

### 5.3 Faithfulness, Hallucination, and Factual Consistency

Abstractive summarization systems can hallucinate content not supported by the source; human studies show this can be substantial. citeturn0search1

Representative approaches and metrics:
- **FactCC** trains a classifier to detect factual consistency issues and provides span-level evidence for checking. citeturn2search3
- **QAGS** evaluates factual consistency via automatically generated questions/answers from summaries and source documents. citeturn2search12
- **SummaC** revisits NLI-based inconsistency detection for summaries. citeturn2search0

### 5.4 Evaluation Benchmarks and Limitations of Single Metrics

- **ROUGE** is a classic overlap-based metric widely used for summarization evaluation and is implemented (in simplified form) in this repo’s summarization workspace. citeturn1search16
- Large-scale studies show that automatic metrics capture different dimensions unevenly; evaluation should not collapse to a single number (e.g., ROUGE-only). citeturn0search17

### 5.5 Task/Dataset Context (for positioning)

Canonical summarization datasets (e.g., XSum) are designed for news articles and short abstractive targets; ESG disclosures differ in structure and evidence requirements. XSum is an example of “extreme summarization” encouraging abstractive behavior. citeturn4search0

---

## 6) Methodology

### 6.1 Study Design Overview

This is a **repo-integrated, applied NLP study**:
- Treat the existing OCR → extraction → ABSA pipeline as the upstream generator of evidence.
- Add a summarization layer that produces narrative summaries at multiple granularities.
- Evaluate summaries for **coverage, faithfulness, and utility**, emphasizing auditability.

### 6.2 Inputs (Existing Artifacts to Reuse)

Primary reusable artifacts (already referenced in `summarization/data/data_sources.json`):
- `results/thesis_workflow_dashboard/tone_records_flat.csv` (record-level statements/fields)
- `results/thesis_workflow_dashboard/t2_flat_outputs.csv` (flattened extraction outputs)
- stability/diagnostics tables:
  - `results/thesis_workflow_dashboard/model_stability_summary.csv`
  - `results/thesis_workflow_dashboard/prompt_stability_summary.csv`
  - `results/thesis_workflow_dashboard/ontology_coverage.csv`
- agreement summary:
  - `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv`

### 6.3 Summary Units (Granularity)

Define summary “units” (each stored with metadata):
1. **Record-level micro-summary**: short rewrite/label explanation per extracted ESG record.
2. **Company-level ESG summary**: per report, grouped by ESG pillars and top aspects.
3. **Comparative summary**: cross-company, cross-sector contrasts.
4. **Chapter-ready thesis summary**: narrative synthesis + contribution/future-work framing.

For each unit store:
- provenance pointers (document/page IDs or record IDs)
- ABSA distributions (tone/sentiment/aspect/pillar)
- summarization strategy + configuration (baseline/extractive/LLM/hybrid)
- evaluation results (metrics + human audit flags)

### 6.4 Summarization Strategies (Implementation Plan)

**S1: Extractive baselines (implemented)**
- Lead baseline: `summarize_lead()`
- Frequency-based sentence scoring: `summarize_frequency()`
- TextRank-like iterative ranking: `summarize_textrank_like()` citeturn0search14

**S2: Abstractive (to implement)**
- LLM summary generation constrained by:
  - ABSA fields (aspect/pillar/tone/sentiment)
  - retrieved evidence sentences (extractive scaffold)
  - explicit “no new facts” instructions + citation requirements

**S3: Hybrid ABSA-guided (to implement)**
- Select evidence sentences per aspect/pillar (extractive scaffold).
- Produce concise narrative paragraphs per pillar/aspect group.
- Run factuality checks (FactCC/QAGS/SummaC-style or simplified proxies) and flag risky claims. citeturn2search3turn2search12turn2search0

### 6.5 Evaluation Framework

**Automatic evaluation**
- ROUGE-1/2/L (overlap) against any available reference summaries (where created). citeturn1search16
- ABSA coverage:
  - aspect coverage rate (share of top-k aspects mentioned)
  - pillar coverage completeness
  - tone/commitment preservation rate
- Faithfulness proxies:
  - extractive support ratio (share of summary claims mapped to evidence spans)
  - contradiction/entailment signals via NLI (if available)

**Human evaluation (recommended)**
- Faithfulness labeling: supported / unsupported / contradicted.
- Utility: “Can the summary replace reading the table for quick understanding?”
- Error taxonomy aligned with factuality studies (entity swaps, incorrect quantities, spurious claims). citeturn0search1

### 6.6 Reproducibility Outputs (Where to Save)

Standardize exports under `results/summarization/` (to implement):
- `summaries.jsonl` (one row per unit; includes metadata/provenance)
- `coverage_metrics.csv` (aspect/pillar/tone coverage)
- `faithfulness_audit.csv` (automatic flags + human labels when available)
- `strategy_comparison.csv` (metrics by strategy/unit)

---

## 7) Results (Current Repo State — What We Can Claim Today)

### 7.1 Implemented Summarization Baselines

The repo already implements a working extractive summarization sandbox in `summarization/app.py`:
- Lead baseline
- frequency-based sentence selection
- TextRank-like graph ranking
- optional ROUGE computation (ROUGE-1/2/L) when a reference summary is provided

This establishes a minimum viable experimental bed for strategy comparison, with a baseline evaluation metric (ROUGE). citeturn1search16turn0search14

### 7.2 Available Evidence-Level Results That Summarization Can Build On

The thesis dashboard metrics indicate the upstream pipeline has produced non-trivial structured outputs (as of `results/thesis_workflow_dashboard/dashboard_metrics.json`):
- OCR documents processed: 23
- Structured tone records: 332
- T2 flattened outputs: 2,074 rows

Additionally, record-level agreement between a “tone commitment” signal and a ClimateBERT-style proxy label is reported:
- percent agreement: 0.8373
- Cohen’s kappa: 0.6451
from `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv`.

These values are **not** summarization-quality results; they justify that the structured evidence layer exists and can be summarized at scale with diagnostic awareness.

### 7.3 Known Missing Results (Not Yet Implemented)

The repo does not yet provide:
- a standardized `results/summarization/` export
- ABSA-aware/hybrid summary generation
- factuality audits (FactCC/QAGS/SummaC-style or equivalent)
- any human evaluation of summary faithfulness/utility (as recommended in the literature) citeturn0search1turn0search17

---

## 8) Discussion

1. **Why extractive baselines matter here**: Extractive summaries are generally easier to audit because content is copied from the source. In OCR-heavy pipelines, this can be a safer default than free-form abstraction.
2. **Why abstractive methods are risky but useful**: Abstractive summaries can produce more readable narrative ESG summaries but increase hallucination risk; the literature consistently highlights faithfulness limitations in neural abstractive summarization. citeturn0search1
3. **ABSA as a constraint mechanism**: Using aspect/pillar/tone distributions as a “content plan” can reduce omissions and make summaries systematically comparable across companies.
4. **Evaluation must be multi-dimensional**: ROUGE is a useful overlap measure but insufficient as a sole metric; benchmark work shows that different metrics align differently with human judgments. citeturn0search17turn1search16
5. **Implication for thesis writing**: A summarization layer can bridge from record-level evidence tables to chapter-ready narrative, but only if provenance and faithfulness checks are enforced.

---

## 9) Conclusion

Summarization is feasible in this repository today as an **extractive baseline + ROUGE evaluation sandbox**. To become a complete research track, the summarization layer must be extended into an ABSA-aware, evidence-grounded pipeline with standardized exports and explicit faithfulness evaluation, guided by established factuality findings in summarization research. citeturn0search1turn2search3turn2search12turn2search0

---

## 10) Next Implementation Steps (Repo Tasks)

1. Add `results/summarization/` exporters (JSONL + CSV) driven from existing `results/thesis_workflow_dashboard/*` inputs.
2. Implement ABSA-guided extractive selection (evidence scaffold per aspect/pillar).
3. Implement constrained LLM abstractive summarization (with citations to evidence spans).
4. Add a factuality audit layer (start with simple evidence-span checks; later integrate FactCC/QAGS/SummaC style methods). citeturn2search3turn2search12turn2search0
5. Add a small human evaluation protocol (faithfulness + utility) and store labels in `results/summarization/faithfulness_audit.csv`.

