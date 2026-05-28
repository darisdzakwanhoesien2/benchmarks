# Documentation: Feasibility of Fine-Tuning for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

The current repository already provides OCR, LLM extraction, ABSA-related modeling, diagnostics, and pilot evaluation. However, a dedicated **fine-tuning track** for Indonesian ESG ABSA is still not formalized as a core experimental path.

Main gaps are:

1. Existing outputs come from mixed pipelines (rule-based, classical ML, hybrid/deep, LLM extraction), but there is no standardized supervised fine-tuning benchmark focused on Indonesian ESG ABSA labels.
2. Pilot annotations exist, yet they are not fully operationalized into a clean train/validation/test corpus for controlled fine-tuning experiments.
3. Current evaluations emphasize parse reliability and workflow stability; they are less centered on parameter-update strategies and their impact on aspect-level sentiment quality.
4. There is no consolidated comparison between full fine-tuning and parameter-efficient alternatives within this project’s Indonesian ESG context.

## 2. Research Questions

1. Can supervised fine-tuning of pretrained language models improve Indonesian ESG ABSA performance compared to current baseline methods in this repository?
2. Which fine-tuning strategy is most suitable for this pipeline: full-parameter fine-tuning or parameter-efficient fine-tuning (e.g., adapter/LoRA-style)?
3. How stable are fine-tuned models across ESG pillars, aspect groups, and disclosure-tone subtypes?
4. What data scale and label quality threshold are needed for fine-tuning to produce reliable gains in Indonesian ESG ABSA?

## 3. Research Objectives

1. Build a reproducible fine-tuning workflow using existing project artifacts and evaluation pages.
2. Prepare a standardized Indonesian ESG ABSA labeled dataset from current extraction and annotation outputs.
3. Fine-tune one or more pretrained models for ESG aspect and sentiment classification.
4. Compare fine-tuned models against existing baselines and current pipeline outputs.
5. Produce thesis-ready evidence on performance gains, limitations, and deployment tradeoffs.

## 4. Research Contribution

This study can contribute:

1. A practical fine-tuning blueprint for Indonesian ESG ABSA inside an operational thesis system.
2. Empirical evidence on whether in-domain supervised adaptation improves aspect-sentiment quality for ESG disclosures.
3. A reproducible evaluation package combining aggregate metrics, subgroup diagnostics, and error taxonomies.
4. A clear engineering tradeoff analysis between accuracy, compute cost, and maintainability for fine-tuned ESG models.
5. Reusable artifacts for future Indonesian ESG NLP benchmarking and thesis extensions.

## 5. Literature Review (Focused)

Relevant literature themes:

1. **Pretraining and supervised fine-tuning**: adapting large pretrained encoders to task-specific labels.
2. **ABSA in domain-specific text**: aspect-level polarity classification in specialized corpora with heterogeneous label distributions.
3. **Fine-tuning in low-resource settings**: overfitting risks, class imbalance, and label-noise impacts.
4. **Parameter-efficient fine-tuning**: adapters and low-rank updates as cost-effective alternatives to full updates.
5. **Evaluation methodology**: per-class metrics, cross-domain robustness, calibration, and error analysis beyond top-line F1.

For this repository, literature should support one key thesis: fine-tuning must be evaluated as a complete research protocol (data curation + training + robust diagnostics), not only as a model replacement.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

The repository already includes key building blocks:

1. Data ingestion and preprocessing
   - `pages/Bulk_OCR.py`
   - OCR outputs in `data/thesis_dataset/`
2. ESG extraction and ABSA signal generation
   - `pages/llm_processing.py`
   - `results/esg_records.json`
   - T2/T3 outputs in `results/`
3. Baseline modeling modules
   - `code/rule_based.py`
   - `code/classical_ml.py`
   - `code/hybrid_model.py`
   - `code/deep_model.py`
4. Human-label and metric infrastructure
   - `pages/1_1_Ground_Truth_Workbench.py`
   - `pages/1_3_Ground_Truth_Metrics.py`
   - supporting files in `results/revision_analysis/`

### 6.2 Dataset Preparation for Fine-Tuning

1. Consolidate labels from pilot annotations, ground-truth scaffolds, and validated extraction rows.
2. Harmonize taxonomy for:
   - aspect labels,
   - ESG pillar labels,
   - sentiment labels,
   - optional tone labels.
3. Deduplicate and clean inconsistent rows (missing fields, conflicting labels, low-evidence samples).
4. Split data by document/company to reduce leakage and preserve realistic generalization tests.

### 6.3 Fine-Tuning Strategies

1. **Full fine-tuning**
   - update all model weights on Indonesian ESG ABSA tasks.
2. **Parameter-efficient fine-tuning**
   - apply adapter/LoRA-style lightweight updates where supported.
3. **Multi-task fine-tuning (optional)**
   - jointly train aspect and sentiment heads; optionally add ESG pillar/tone auxiliary targets.

### 6.4 Experimental Protocol

1. Baseline comparisons:
   - rule-based,
   - classical ML,
   - existing hybrid/deep outputs.
2. Core metrics:
   - accuracy,
   - precision/recall/F1 (macro and weighted),
   - Cohen kappa,
   - confusion matrices.
3. Subgroup analysis:
   - by ESG pillar,
   - by aspect frequency band,
   - by tone group,
   - by sector/company.
4. Stability checks:
   - repeated-seed training,
   - early stopping sensitivity,
   - class-weight/imbalance ablation.

### 6.5 Integration Plan in This Codebase

1. Add a dedicated script/module (e.g., `code/fine_tuning_esg_absa.py`) for train/eval/inference.
2. Save outputs in `results/fine_tuning/`:
   - metrics,
   - predictions,
   - confusion matrices,
   - error-analysis tables.
3. Create a Streamlit benchmark page (e.g., `pages/1_16_Fine_Tuning_ESG_ABSA.py`) reusing the existing analytics style.
4. Connect findings to `pages/1_7_Research_Questions_Dashboard.py` and chapter pages.

## 7. Expected Results

Given current project maturity, expected outcomes are:

1. Fine-tuned models improve ABSA aspect/sentiment metrics over rule/classical baselines.
2. Improvements are strongest for high-frequency aspect categories and weaker for sparse labels.
3. Parameter-efficient fine-tuning may approach full fine-tuning performance with lower resource requirements.
4. Remaining errors will concentrate in ambiguous Indonesian phrasing, code-switching, and boilerplate disclosure language.
5. Aggregate gains may conceal subgroup instability, requiring explicit per-group reporting.

## 8. Discussion

Key points to discuss in thesis chapters:

1. **Feasibility**: fine-tuning is practical here because data, outputs, and evaluation tooling already exist.
2. **Data dependency**: model quality is constrained more by label quality/coverage than by architecture choice alone.
3. **Operational tradeoff**: full fine-tuning can maximize performance but increases compute and reproducibility burden.
4. **Methodological rigor**: robust conclusions require subgroup diagnostics and repeated-run evidence, not single-run headline scores.
5. **Pipeline impact**: fine-tuning can strengthen the ABSA core while preserving current OCR/extraction/audit workflow.

## 9. Conclusion

Fine-tuning for Indonesian ESG ABSA is feasible in this repository with the existing code and artifacts. The essential next step is to formalize a high-quality labeled training corpus and run controlled comparisons across fine-tuning strategies against established baselines. The expected contribution is a reproducible, thesis-grade demonstration of how in-domain supervised adaptation improves ESG ABSA quality in Indonesian sustainability-report analysis.

---

## Suggested Next Implementation Steps

1. Build `results/fine_tuning/labels_master.csv` from existing annotation and extraction artifacts.
2. Implement `code/fine_tuning_esg_absa.py` with configurable training strategies.
3. Export benchmark tables/plots aligned with `Ground_Truth_Metrics` conventions.
4. Add a Streamlit page for fine-tuning experiments and chapter-linked reporting.
