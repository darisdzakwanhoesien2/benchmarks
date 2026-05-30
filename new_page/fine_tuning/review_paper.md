# Fine-Tuning for Indonesian ESG Aspect-Based Sentiment Analysis (ABSA): A Repository-Grounded Review and Research Agenda

Date: 2026-05-30

## Abstract

Fine-tuning pretrained language models has become the dominant paradigm for improving task-specific NLP performance, but applied research often under-specifies the end-to-end protocol needed to produce trustworthy, reproducible gains—especially in low-resource settings and domain-specific corpora. This review paper synthesizes the fine-tuning landscape through the lens of **Indonesian ESG Aspect-Based Sentiment Analysis (ABSA)** for sustainability-report analysis. The paper is grounded in an operational benchmark repository that already contains (i) OCR-to-text ingestion, (ii) ESG extraction and ABSA-relevant labels, (iii) multiple baseline model families, and (iv) stability diagnostics. We organize prior work into a practical taxonomy (data, objectives, training strategies, parameter-efficient methods, and evaluation rigor), identify key methodological failure modes (template leakage, label noise, and long-tail imbalance), and propose a repository-integrated research agenda for benchmarking **full fine-tuning vs parameter-efficient fine-tuning (PEFT)** under leakage-aware splits with subgroup and stability reporting. The review concludes with a reproducible implementation blueprint tailored to Indonesian ESG disclosures and the constraints of thesis-grade applied research.

## Keywords

Fine-tuning; parameter-efficient fine-tuning; LoRA; adapters; ABSA; sentiment analysis; ESG; sustainability reports; Indonesian NLP; low-resource NLP; evaluation; robustness.

---

## 1. Introduction

Environmental, Social, and Governance (ESG) reporting has expanded rapidly, creating demand for automated methods that can extract, structure, and evaluate sustainability-related disclosures at scale. However, ESG narratives in annual or sustainability reports are linguistically complex: they contain templated boilerplate, mixed claims and commitments, dense policy language, and frequent code-switching. These properties make naive sentiment classification unreliable and motivate **Aspect-Based Sentiment Analysis (ABSA)**: identifying *what* is being discussed (aspect/pillar) and *how* it is framed (sentiment and tone).

Pretrained language models (PLMs), especially multilingual encoders, offer a strong starting point for Indonesian ABSA. Yet the central applied question remains: **does supervised fine-tuning on in-domain ESG labels produce robust gains**—and what protocol is required to ensure those gains are real (not leakage), stable (not seed-sensitive), and useful (not only for frequent labels)?

This review paper addresses that question by synthesizing the fine-tuning literature and translating it into a practical, repository-integrated research agenda for Indonesian ESG ABSA.

---

## 2. Scope and Definitions

### 2.1 Task Scope: Indonesian ESG ABSA

We focus on supervised learning tasks commonly used in ESG ABSA pipelines:

1. **Aspect classification**: assign an aspect label (e.g., emissions, workforce, governance practices) to a text span or statement.
2. **Sentiment classification**: classify sentiment as {positive, neutral, negative} with respect to the identified aspect or disclosure.
3. **(Optional) ESG pillar classification**: map disclosures to E/S/G.
4. **(Optional) Tone classification**: classify disclosure tone (e.g., action, commitment, outcome, none) when label availability supports it.

### 2.2 Fine-Tuning

In this paper, “fine-tuning” refers to updating model parameters using labeled in-domain data. We distinguish:

- **Full fine-tuning**: update all or most pretrained weights plus task head.
- **Parameter-efficient fine-tuning (PEFT)**: freeze the base model and train small additional modules (e.g., adapters/LoRA) plus task head.

### 2.3 Why Sustainability Reports Are Not Standard ABSA Corpora

ESG disclosures differ from product review ABSA settings:

- Longer-form passages with context dependence.
- Repeated templates and boilerplate across years/companies.
- Mixed evidence vs promises (e.g., “will implement”, “committed to”).
- Code-switching (Indonesian + English terms, acronyms).
- Label ambiguity (sentiment toward the *company* vs sentiment toward the *topic*).

These differences drive the need for careful dataset construction and evaluation.

---

## 3. Review Methodology (Narrative, Repository-Grounded)

This paper is a **narrative review** intended to be implementation-actionable. It is grounded in the structure and artifacts of an operational benchmark repository (see “Repository Anchors” below). The review does **not** claim to be an exhaustive systematic review with a reproducible database search protocol; instead, it synthesizes widely accepted themes from fine-tuning and ABSA research and maps them onto the concrete risks and opportunities that appear in ESG-report pipelines.

### Repository Anchors (for traceability)

The repository already provides the following relevant anchors for the fine-tuning track:

- Fine-tuning planner UI: `fine_tuning/app.py`
- Fine-tuning feasibility framing: `documentation_fine_tuning.md`
- Full fine-tuning research track write-up: `documentation_fine_tuning_research.md` (repo root)
- Baseline modules:
  - `code/rule_based.py`
  - `code/classical_ml.py`
  - `code/hybrid_model.py`
  - `code/deep_model.py`, `code/deep_model_v2.py`
- Labeled / diagnostic artifacts for grounding:
  - `results/revision_analysis/pilot_ground_truth_annotations.csv`
  - `results/revision_analysis/silver_tone_ground_truth.csv`
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
  - `results/revision_analysis/model_stability_summary.csv`
  - `results/revision_analysis/prompt_stability_summary.csv`
- Climate proxy validation hooks:
  - `fine_tuning/call_climatebert_logic.py`
  - `results/fine_tuning/*` outputs produced by the above

---

## 4. Fine-Tuning in Domain-Specific ABSA: What the Literature Emphasizes

### 4.1 Pretraining vs In-Domain Supervision

The common finding across modern NLP is that pretrained multilingual encoders provide strong representations, but **domain shift** can degrade performance. In ESG reports, domain shift emerges from:

- specialized vocabulary (e.g., regulatory terms, ESG frameworks),
- long narrative structures rather than short opinion sentences,
- stylistic uniformity due to templates.

Fine-tuning helps align representations to task labels, but only when the labeled dataset is sufficiently clean and the evaluation protocol prevents leakage.

### 4.2 Low-Resource Fine-Tuning: The Typical Failure Modes

In low-resource settings (common for Indonesian ESG ABSA), fine-tuning is sensitive to:

- **label noise** (human disagreement, LLM-generated weak labels, inconsistent taxonomy),
- **class imbalance** (neutral dominates; negative rare),
- **overfitting** due to repeated templates,
- **instability** across random seeds and hyperparameters.

These issues often invalidate “single-run, single-metric” claims.

### 4.3 PEFT as an Engineering and Scientific Strategy

PEFT (e.g., LoRA/adapters) is frequently motivated by lower compute and storage, but it also supports **reproducibility**:

- smaller update set,
- faster iteration for ablations,
- easier checkpoint management,
- potential to share task adapters without distributing full model weights.

For thesis workflows, PEFT can be a pragmatic default for controlled comparisons.

### 4.4 Multi-Task Learning

ABSA naturally decomposes into multiple labels (aspect, sentiment, pillar, tone). Multi-task fine-tuning can:

- improve sample efficiency,
- regularize the model,
- align representations across related labels.

However, multi-task training can also harm performance if auxiliary labels are noisy or missing; therefore, multi-task should be treated as an **ablation**, not a default.

---

## 5. A Taxonomy of Fine-Tuning Approaches for Indonesian ESG ABSA

This section provides a practical taxonomy that can be mapped directly to experiment design.

### 5.1 Data Axis

1. **Human-labeled gold**: highest reliability, expensive.
2. **Silver / weak labels**: scalable but noisy (e.g., derived from heuristics or LLM pipelines).
3. **Pseudo-labeling / self-training**: can expand data but risks reinforcing model biases.
4. **Hybrid**: gold for evaluation and calibration; silver for pretraining/auxiliary tasks.

### 5.2 Objective Axis (Task Formulation)

1. Single-label classification (aspect OR sentiment).
2. Multi-head classification (aspect + sentiment).
3. Hierarchical objectives:
   - predict pillar first, then aspect within pillar.
4. Sequence labeling (if aspects map to spans).

For this repository’s current artifacts, classification objectives are the most immediate fit.

### 5.3 Parameter Update Axis

1. Full fine-tuning.
2. PEFT:
   - LoRA-style low-rank updates,
   - adapters inserted between layers,
   - bias-only or head-only baselines.

### 5.4 Training Control Axis

1. Standard fine-tuning with early stopping.
2. Class-imbalance mitigation:
   - class weights,
   - focal loss,
   - balanced sampling.
3. Regularization:
   - dropout,
   - weight decay,
   - freezing lower layers.
4. Robustness:
   - multiple seeds,
   - hyperparameter sweeps (small, controlled).

### 5.5 Evaluation Axis

1. Aggregate metrics:
   - macro-F1, weighted-F1, accuracy.
2. Per-class reporting:
   - especially for rare negative sentiment or tail aspects.
3. Subgroup diagnostics:
   - by ESG pillar, tone group, aspect frequency band, and company.
4. Stability reporting:
   - mean ± std across seeds.
5. Error taxonomies:
   - code-switching, hedging, boilerplate, ontology mismatch.

---

## 6. Research Gaps and Open Problems (Indonesian ESG ABSA Fine-Tuning)

Drawing from both the fine-tuning literature and ESG-report realities, the most consequential gaps are:

### 6.1 Leakage-Aware Evaluation Is Under-Implemented

Sustainability reports contain repeated templates. Random row-level splits risk placing near-identical text in train and test. Without leakage-aware splits (company/report-level), gains can be overstated.

### 6.2 Label Taxonomy Drift and Mixed Labels

ESG pillar labels may appear in mixed forms (e.g., multi-pillar tags). Sentiment and tone labels may be missing or inconsistent. Without harmonization rules, fine-tuning becomes non-reproducible and non-comparable.

### 6.3 Long-Tail Aspects

In ABSA, the label space often follows a head/tail distribution. Fine-tuning can improve head aspects while leaving tails unchanged or worse. Many papers report only aggregate scores, masking these failures.

### 6.4 “Better F1” vs “Better Decisions”

For applied ESG analysis, the goal is not only higher F1 but also:

- stable performance across companies/sectors,
- transparent errors (auditable),
- predictable failure modes.

The review highlights the need for evaluation protocols aligned with downstream use.

### 6.5 Full Fine-Tuning vs PEFT Tradeoffs Remain Unclear In-Repo

The repository includes multiple baselines and diagnostic infrastructure, but it does not yet contain a controlled comparison of full fine-tuning vs PEFT under a shared protocol.

---

## 7. Research Questions and Objectives (Review-Informed)

### 7.1 Research Questions

RQ1. Can supervised fine-tuning improve Indonesian ESG ABSA performance compared to existing baseline approaches in the repository?

RQ2. Under the same dataset and protocol, does PEFT approach full fine-tuning performance while improving reproducibility and iteration cost?

RQ3. How stable are fine-tuned models across ESG pillars, aspect groups (head/tail), tone subtypes, and company-level splits?

RQ4. What minimum labeled data scale and label quality are required to obtain reliable gains, rather than noise-fitting?

### 7.2 Research Objectives

O1. Package a canonical labeled dataset and leakage-aware splits.

O2. Implement full fine-tuning and PEFT runners integrated into the repository.

O3. Evaluate using aggregate, per-class, subgroup, and stability reporting.

O4. Produce error analyses and engineering tradeoff summaries suitable for thesis chapters.

---

## 8. Proposed Methodology Blueprint (Repository-Integrated)

This section translates the review into a concrete plan for implementation.

### 8.1 Dataset Construction

Inputs:

- `results/revision_analysis/pilot_ground_truth_annotations.csv` (primary)
- optional supporting artifacts for analysis and filtering:
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
  - `results/revision_analysis/silver_tone_ground_truth.csv`

Processing steps:

1. **Row eligibility checks**:
   - require non-empty text field(s),
   - require non-empty target label(s).
2. **Label harmonization**:
   - map sentiment to {positive, neutral, negative},
   - map tone to a stable set (or drop if too sparse),
   - decide how to handle multi-pillar labels (multi-label vs mapped “mixed”).
3. **Deduplication**:
   - exact duplicates by record_id/text hash,
   - optional near-duplicate removal if feasible.
4. **Split construction**:
   - default split unit: company (and/or report ID),
   - deterministic seed,
   - persist split mapping in `results/fine_tuning/splits.json`.

Outputs:

- `results/fine_tuning/labels_master.csv`
- `results/fine_tuning/splits.json`

### 8.2 Model Families and Training

Recommended approach:

- Start with a multilingual encoder baseline (for stability and interpretability).
- Compare:
  - head-only (frozen encoder) baseline,
  - PEFT (LoRA/adapters),
  - full fine-tuning.

Training controls:

- consistent epoch/step budgets,
- early stopping on dev macro-F1,
- multiple random seeds (at least 3).

### 8.3 Metrics and Diagnostics

1. Aggregate:
   - macro-F1, weighted-F1, accuracy.
2. Per-class:
   - class-wise F1 and support.
3. Subgroups:
   - pillar, tone, aspect frequency band, company.
4. Stability:
   - mean ± std across seeds,
   - “worst seed” reporting to avoid cherry-picking.
5. Error analysis:
   - sample incorrect predictions by category,
   - identify recurring patterns (boilerplate, hedging, code-switching).

### 8.4 Outputs and Reporting Artifacts

Write all artifacts to `results/fine_tuning/`:

- `metrics_*.json` / `metrics_*.csv`
- `predictions_*.csv`
- `confusion_*.csv` (and/or plots)
- `error_analysis_*.csv`

Add a Streamlit page under `pages/` that reads these artifacts (avoid training inside Streamlit).

---

## 9. Results (Current Status in the Repository)

As of 2026-05-30, the repository supports *planning and feasibility validation* but does not yet contain fine-tuning benchmark results.

### 9.1 What Exists Today

- A fine-tuning research planner UI that presents a structured plan and shows evidence snapshots from in-repo datasets: `fine_tuning/app.py`.
- A ClimateBERT-logic API validation hook (CLI and UI) that can be used for proxy checks and saves outputs under `results/fine_tuning/`:
  - `fine_tuning/call_climatebert_logic.py`
  - `fine_tuning/app.py`
- Labeled artifacts that can seed a supervised fine-tuning benchmark:
  - `results/revision_analysis/pilot_ground_truth_annotations.csv`

### 9.2 What Is Missing (To Turn Review Into Measured Evidence)

- Canonical dataset packaging under `results/fine_tuning/` with deterministic splits.
- A training/evaluation runner under `code/` for full fine-tuning and PEFT.
- Exported metrics, predictions, subgroup tables, and repeated-seed stability summaries.

---

## 10. Discussion

### 10.1 What Would Count as a Strong Fine-Tuning Result?

In this domain, “strong” results should satisfy:

1. **Leakage-aware generalization**: company/report-level splits.
2. **Subgroup robustness**: not only improved aggregate metrics.
3. **Stability**: consistent improvements across random seeds.
4. **Error transparency**: clear failure modes and an auditable error sample.

### 10.2 Expected Tradeoffs: Full Fine-Tuning vs PEFT

Based on common patterns in applied NLP:

- Full fine-tuning may yield the best top-line performance, especially when enough clean labels exist.
- PEFT may deliver near-parity with better:
  - iteration speed,
  - reproducibility,
  - storage efficiency,
  - easier deployment of task-specific adapters.

The correct choice should be justified empirically in this repository’s setting.

### 10.3 Data Quality and Taxonomy Are Likely the Binding Constraint

For Indonesian ESG ABSA, major risks include:

- ambiguous labels (sentiment toward topic vs company),
- mixed pillar tags,
- missing tone fields.

Better label definitions and harmonization rules can unlock larger gains than model architecture changes.

---

## 11. Conclusion

Fine-tuning for Indonesian ESG ABSA is a high-value next research step, but it must be treated as an end-to-end protocol rather than a model swap. The literature emphasizes—and the ESG-report domain amplifies—the importance of leakage-aware splits, label harmonization, long-tail reporting, and stability diagnostics. A repository-integrated benchmark that compares full fine-tuning and PEFT under a single rigorous protocol can produce thesis-grade contributions: both scientific (robustness and data requirements) and engineering (reproducible pipelines and auditable artifacts).

---

## Appendix A. Immediate Next Steps (Implementation Checklist)

1. Create `results/fine_tuning/labels_master.csv` from `results/revision_analysis/pilot_ground_truth_annotations.csv`.
2. Create `results/fine_tuning/splits.json` with deterministic company/report-level splits.
3. Implement `code/fine_tuning_esg_absa.py` for:
   - head-only baseline,
   - PEFT,
   - full fine-tuning,
   - repeated seeds and subgroup metrics export.
4. Export standardized results artifacts under `results/fine_tuning/`.
5. Add a Streamlit page under `pages/` to visualize comparisons from exported artifacts.

