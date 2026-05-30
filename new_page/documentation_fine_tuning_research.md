# Fine-Tuning Research Track — Indonesian ESG ABSA (Repo-Integrated Study)

Date: 2026-05-30

This document turns the existing fine-tuning feasibility framing in `documentation_fine_tuning.md` into a complete, thesis-style **fine-tuning research track** that is auditable against the code and artifacts already present in this repository.

**Repo anchors**

- Fine-tuning planner UI (gap/RQs/objectives/method skeleton + evidence snapshots): `fine_tuning/app.py`
- Fine-tuning framing (existing): `documentation_fine_tuning.md`
- ClimateBERT-logic API validation (CLI + UI): `fine_tuning/call_climatebert_logic.py`, `fine_tuning/app.py`
- Baseline modules referenced by the fine-tuning plan:
  - `code/rule_based.py`
  - `code/classical_ml.py`
  - `code/hybrid_model.py`
  - `code/deep_model.py`, `code/deep_model_v2.py`
- Existing labeled / evaluation artifacts used as evidence sources:
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` (5,444 rows; 34 columns)
  - `results/revision_analysis/silver_tone_ground_truth.csv` (5,444 rows; 30 columns)
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv` (332 rows; 25 columns)
  - `results/revision_analysis/climatebert_output.csv` (5,112 rows; 7 columns)
  - `results/revision_analysis/model_stability_summary.csv` (6 rows; 7 columns)
  - `results/revision_analysis/prompt_stability_summary.csv` (7 rows; 7 columns)

---

## 1) Background and Problem Statement

This repository operationalizes an end-to-end workflow for Indonesian sustainability-report analysis: OCR ingestion, ESG record extraction, ABSA-style labeling (aspect / pillar / sentiment / tone), and stability diagnostics. In practice, the system already produces a non-trivial labeled corpus and multiple baseline model families.

The missing piece is a **standardized, reproducible supervised fine-tuning benchmark** that answers: *If we allow model weights to update using in-repo labels, do we materially improve Indonesian ESG ABSA quality and stability—and under what constraints (label noise, imbalance, compute limits, and leakage risk)?*

This track focuses on supervised fine-tuning for **Indonesian ESG ABSA** with thesis-grade experimental rigor: data curation, controlled training, leakage-aware splits, subgroup/stability diagnostics, and engineering tradeoff reporting.

---

## 2) Research Gap

Despite strong pipeline coverage in the repository, several fine-tuning-specific gaps remain:

1. **No standardized supervised fine-tuning benchmark for Indonesian ESG ABSA.** Current outputs span rule-based, classical ML, hybrid/deep models, and LLM-driven extraction/labeling; however, the repo does not yet define a single, consistent fine-tuning benchmark dataset and protocol that integrates those artifacts into train/dev/test splits.
2. **Pilot annotations are not yet operationalized into a clean, leakage-controlled corpus.** Labeled rows exist (`results/revision_analysis/pilot_ground_truth_annotations.csv`), but they are not packaged as a canonical dataset with deduplication rules, label harmonization, and company/document-level splitting.
3. **Evaluation emphasis currently leans toward stability and parsing reliability, not parameter-update strategy comparisons.** Existing stability summaries (`model_stability_summary.csv`, `prompt_stability_summary.csv`) are valuable context, but there is not yet an in-repo comparison of full fine-tuning vs PEFT (e.g., LoRA) under consistent metrics.
4. **Robustness and subgroup evidence are not yet organized as fine-tuning outcomes.** The labeled corpus supports subgroup analysis (pillar/aspect/tone/company), but there is no dedicated fine-tuning results package with subgroup diagnostics and repeated-seed stability.

In short: the project has *the ingredients* (data + baselines + diagnostics), but not yet the *benchmark-quality fine-tuning track*.

---

## 3) Research Questions

RQ1. **Effectiveness:** Can supervised fine-tuning improve Indonesian ESG ABSA performance over existing baseline approaches already present in this repository?

RQ2. **Strategy tradeoffs:** Under the same protocol and dataset, which strategy is more suitable for this pipeline: full fine-tuning or parameter-efficient fine-tuning (PEFT; adapter/LoRA-style)?

RQ3. **Stability / robustness:** How stable are fine-tuned models across (a) ESG pillars, (b) aspect groups / frequency bands, (c) tone subtypes, and (d) company sectors (or at minimum, company-level splits)?

RQ4. **Data requirements:** What minimum data scale and label-quality threshold are needed for fine-tuning to produce reliable gains (and not regress due to noise/imbalance)?

---

## 4) Research Objectives

O1. **Build** a reproducible fine-tuning workflow that is integrated with current artifacts and reporting style in the repository (data inputs under `results/`, outputs under `results/fine_tuning/`).

O2. **Construct** a standardized Indonesian ESG ABSA labeled dataset derived from existing annotation/extraction outputs, including leakage-aware split logic and reproducible preprocessing.

O3. **Fine-tune** one or more pretrained language models for (at minimum) aspect and sentiment classification; optionally include auxiliary ESG pillar and/or tone tasks.

O4. **Compare** fine-tuned models against existing baselines with a fixed protocol (metrics, splits, seeds), plus subgroup and error-taxonomy reporting.

O5. **Deliver** thesis-ready evidence on gains, limitations, and operational tradeoffs (accuracy vs compute vs maintainability).

---

## 5) Expected Research Contributions

1. **A repository-native fine-tuning benchmark** for Indonesian ESG ABSA with standardized dataset packaging and evaluation.
2. **Empirical evidence** on whether in-domain supervised adaptation improves aspect/sentiment quality for Indonesian ESG disclosure text under OCR/LLM pipeline constraints.
3. **A reproducible diagnostics package** (aggregate + subgroup + stability + error taxonomy) aligned with the repo’s existing “stability-first” philosophy.
4. **Engineering tradeoff analysis** comparing full fine-tuning vs PEFT in an applied thesis system context.
5. **Reusable artifacts** (master labels CSV/JSONL, train/dev/test splits, evaluation scripts, metrics tables) that enable future extensions (transfer learning, multi-task, continual learning).

---

## 6) Literature Review (Focused)

This thesis track should position fine-tuning as a complete protocol—**data curation + training + evaluation rigor**—rather than a model swap. The literature review should therefore cover:

### 6.1 Pretraining and Supervised Fine-Tuning

- Why pretrained multilingual encoders can be adapted effectively with limited labeled data, and what failure modes appear under domain shift and label noise.

### 6.2 ABSA in Domain-Specific Text

- ABSA in finance/sustainability disclosures differs from product reviews: long-form, templated narratives, boilerplate, and mixed Indonesian/English code-switching.

### 6.3 Low-Resource Fine-Tuning Behavior

- The central methodological risks in this repo’s setting:
  - class imbalance (e.g., neutral vs negative),
  - label noise (LLM-derived or weakly supervised labels),
  - overfitting and leakage across the same company/report templates.

### 6.4 Parameter-Efficient Fine-Tuning (PEFT)

- Adapter/LoRA-style fine-tuning as a compute- and storage-efficient alternative; why PEFT may be preferable for reproducibility and iterative experimentation in a thesis workflow.

### 6.5 Evaluation Rigor Beyond Top-Line Scores

- The need for:
  - subgroup and long-tail label reporting,
  - repeated-seed stability,
  - confusion matrices and calibration,
  - error taxonomy grounded in language/domain phenomena (boilerplate, hedging, policy vs outcomes, code-switching).

Note: This repo currently does not maintain a formal BibTeX/Zotero bibliography in-tree. Treat this section as a structured plan; add citations via your preferred bibliography workflow (Zotero/BibTeX) once you decide the canonical source list.

---

## 7) Methodology

### 7.1 Existing Evidence and Data Sources (In-Repo)

The fine-tuning plan is grounded in existing labeled and diagnostic artifacts:

- `results/revision_analysis/pilot_ground_truth_annotations.csv` (n=5,444 rows)
  - Contains ground-truth fields used for supervised fine-tuning:
    - `ground_truth_aspect`, `ground_truth_esg`, `ground_truth_tone`, `sentiment`, plus provenance fields such as `company`, `model`, and `prompt`.
  - Distribution snapshots (current repo state):
    - `ground_truth_esg` is dominated by `e` then `g` then `s` (with mixed labels present).
    - `sentiment` is dominated by `neutral` and `positive`, with a small `negative` tail.
    - `ground_truth_tone` includes `none`, `action`, `outcome`, `commitment`.
- `results/revision_analysis/silver_tone_ground_truth.csv` (n=5,444 rows)
  - A “silver” file aligned to the pilot rows; currently `ground_truth_tone` may be blank/missing in many rows (needs verification/harmonization if used for training).
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv` (n=332 rows)
  - Validation layer linking statements to page evidence; useful for leakage checks and error inspection.
- `results/revision_analysis/climatebert_output.csv` (n=5,112 rows)
  - Climate proxy signals; useful as auxiliary features, weak labels, or evaluation context (not a replacement for ground truth).
- `results/revision_analysis/model_stability_summary.csv`, `results/revision_analysis/prompt_stability_summary.csv`
  - Stability context: parse success, missing fields, schema drift; can be used to justify robustness emphasis.

### 7.2 Task Formulation

Minimum viable supervised tasks for this repo:

1. **Aspect classification**: predict `ground_truth_aspect` from Indonesian text (and optionally neighboring metadata).
2. **Sentiment classification**: predict `sentiment` (neutral/positive/negative; ensure mapping is consistent).

Optional auxiliary tasks:

3. **ESG pillar classification**: predict `ground_truth_esg`.
4. **Tone classification**: predict `ground_truth_tone` (action/outcome/commitment/none), if label completeness is sufficient.

### 7.3 Data Packaging and Leakage Control

Core dataset-construction rules:

- **Deduplication:** remove exact-duplicate texts and near-duplicate rows (at least by `record_id` + text hash if available).
- **Harmonization:** map label variants to canonical forms:
  - pillars: `e`, `s`, `g`, and `none` (handle mixed labels explicitly: either multi-label or map to “mixed” and report separately).
  - sentiment: map any non-standard tokens to {positive, neutral, negative}.
  - tone: map unknown/missing to `none` or `unknown` consistently (and report missingness).
- **Splitting:** split at the **company/report** level to reduce template leakage:
  - train/dev/test splits ensure that a company’s repeated boilerplate does not appear in both train and test.
- **Versioning:** produce a `labels_master` artifact with a dataset version and deterministic split IDs (seeded).

### 7.4 Model and Training Strategies

Two strategy families to compare:

1. **Full fine-tuning:** update all parameters of a pretrained encoder.
2. **PEFT fine-tuning:** freeze the base model and train adapters/LoRA modules + classifier head.

For each, define consistent training controls:

- same splits, same max steps/epochs budget,
- early stopping on dev macro-F1 (or weighted-F1 if justified),
- class-weighting or focal loss ablation for imbalance,
- repeated seeds (e.g., 3–5) to report stability.

### 7.5 Evaluation Protocol

Report at least:

- Aggregate metrics:
  - accuracy,
  - macro-F1 and weighted-F1,
  - per-class precision/recall/F1,
  - confusion matrix.
- Reliability:
  - repeated-seed variance (mean ± std),
  - calibration diagnostics if feasible.
- Subgroup evaluation:
  - by ESG pillar,
  - by aspect frequency bands (head / torso / tail),
  - by tone groups (if trained/evaluated),
  - by company (as a robustness proxy).

### 7.6 Engineering / Repo Integration

Standardize all fine-tuning outputs under:

- `results/fine_tuning/`
  - `labels_master.csv` (or JSONL)
  - `splits.json` (train/dev/test IDs)
  - `metrics_*.json` and `metrics_*.csv`
  - `predictions_*.csv`
  - `confusion_*.csv` (or PNG)
  - `error_analysis_*.csv`

Then add a dashboard page that reads these outputs rather than re-running training in Streamlit:

- `pages/` (recommended): `pages/1_16_Fine_Tuning_ESG_ABSA.py` (name can be adjusted to match your page numbering conventions)

---

## 8) Results (Current Repo State — What We Can Claim Today)

### 8.1 Existing Fine-Tuning Track Implementation Status

As of 2026-05-30:

- The repo includes a **fine-tuning research planner UI** that already formalizes:
  - research gap, RQs, objectives, contributions, literature topics, methodology outline, results interpretation plan, discussion, and conclusion (`fine_tuning/app.py`).
- The repo includes a **ClimateBERT-logic API validation routine** that can run against sampled ground-truth rows and save outputs to `results/fine_tuning/` (`fine_tuning/app.py`, `fine_tuning/call_climatebert_logic.py`).

### 8.2 Evidence Snapshot from Existing Labeled Data

The labeled corpus currently supports a realistic supervised benchmark:

- `pilot_ground_truth_annotations.csv` has 5,444 labeled rows with multiple labels and metadata fields (company/model/prompt).
- Label distributions suggest:
  - pillar imbalance (E dominates),
  - sentiment imbalance (neutral/positive dominate; negative is rare),
  - tone availability with a meaningful non-`none` population.

These are not fine-tuning outcomes; they justify feasibility and define the main methodological risks (imbalance, noise, leakage).

### 8.3 Missing Results (Not Yet Implemented in Repo)

The repo does not yet provide:

- a canonical `labels_master` dataset + deterministic leakage-aware splits under `results/fine_tuning/`,
- a training/eval script integrated into `code/` that can run full fine-tuning and PEFT in a controlled way,
- a consolidated benchmark report comparing fine-tuning vs baselines with subgroup and stability evidence.

---

## 9) Discussion (How to Interpret Future Outcomes)

When fine-tuning experiments are implemented, interpret results within these boundaries:

1. **Data quality dominates:** improvements will be limited by label reliability and taxonomy consistency more than by architecture choice.
2. **Template leakage is a major threat:** random row-level splits can inflate results; company/report-level splits should be the default.
3. **Aggregate gains can hide regressions:** improvements on frequent aspects may mask worsening performance on tail categories; subgroup reporting is required.
4. **Full fine-tuning vs PEFT is an engineering decision as much as a modeling decision:** PEFT may deliver near-parity while improving reproducibility, iteration speed, and storage cost.
5. **Stability evidence matters:** use repeated seeds and show variance; a single run is not thesis-grade evidence in this pipeline.

---

## 10) Conclusion

Fine-tuning for Indonesian ESG ABSA is feasible in this repository because it already contains:

- labeled ground-truth rows,
- baseline model families,
- stability and validation artifacts,
- a dedicated fine-tuning planning UI.

The immediate next milestone is to formalize a canonical labeled dataset (harmonized + deduplicated + leakage-controlled splits) and implement controlled comparisons of full fine-tuning vs PEFT against established baselines, with subgroup and stability diagnostics exported to `results/fine_tuning/` for thesis-grade reporting.

---

## Appendix A — Immediate Next Implementation Steps (Repo-Traceable)

1. Build `results/fine_tuning/labels_master.csv`:
   - start from `results/revision_analysis/pilot_ground_truth_annotations.csv`
   - harmonize labels, drop unusable rows, add stable IDs and text fields
2. Add deterministic split file `results/fine_tuning/splits.json`:
   - split by `company` (and/or report ID) to reduce leakage
3. Implement a training runner:
   - recommended module: `code/fine_tuning_esg_absa.py` (train/eval for full FT and PEFT)
4. Export benchmark artifacts:
   - predictions + metrics + confusion matrices + subgroup tables under `results/fine_tuning/`
5. Add a Streamlit page to visualize results:
   - read `results/fine_tuning/*` artifacts and display comparisons vs baselines
