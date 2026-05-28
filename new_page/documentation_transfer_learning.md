# Documentation: Feasibility of Transfer Learning for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

This repository already supports ESG ABSA through rule-based, classical ML, hybrid/deep modeling, ClimateBERT proxy checks, and LLM-based extraction. However, there is still a clear gap in **targeted transfer learning** for Indonesian ESG ABSA:

1. Existing models and outputs are mixed-purpose (climate/topic/tone/extraction), but not consistently fine-tuned on Indonesian ESG ABSA labels.
2. The evaluation pipeline exists, but labeled Indonesian aspect-level sentiment data is still limited and fragmented across pilot artifacts.
3. Cross-model comparisons are available, but domain adaptation effects (general language model -> Indonesian ESG ABSA) are not yet systematically measured.
4. Current stability diagnostics focus on prompts and parsing; transferability across sectors, report styles, and years is not yet a primary experiment axis.

## 2. Research Questions

1. Can transfer learning from general multilingual/domain-pretrained transformers improve Indonesian ESG ABSA performance over existing rule/classical baselines?
2. Which transfer strategy is most effective in this codebase: full fine-tuning, parameter-efficient tuning, or feature-based adaptation?
3. How robust are transfer-learned Indonesian ESG ABSA models across ESG pillars, aspect categories, and disclosure tone types?
4. How much labeled data is required before transfer learning gives meaningful gains versus current pipeline baselines?

## 3. Research Objectives

1. Build a reproducible transfer-learning experiment path using current data and evaluation modules.
2. Fine-tune one or more pretrained language models for Indonesian ESG aspect and sentiment classification.
3. Compare transfer-learning models with existing baselines (rule-based, classical ML, proxy/hybrid outputs).
4. Measure performance by aspect, ESG pillar, tone subgroup, and failure modes.
5. Produce thesis-ready evidence on when transfer learning is beneficial and where it still fails.

## 4. Research Contribution

This study can contribute:

1. A practical transfer-learning blueprint for Indonesian ESG ABSA using an existing end-to-end thesis pipeline.
2. Empirical evidence on domain adaptation value for low-resource, bilingual ESG reporting contexts.
3. A benchmark protocol connecting extraction outputs, human labels, and fine-tuned ABSA models.
4. Error analysis that distinguishes linguistic challenges (Indonesian morphology, code-switching, boilerplate) from modeling limitations.
5. Reusable artifacts (training/evaluation outputs and diagnostics) for subsequent ESG NLP research.

## 5. Literature Review (Focused)

The relevant literature streams include:

1. **Transfer learning in NLP**: pretrained transformers adapted to downstream tasks with limited labeled data.
2. **ABSA modeling**: aspect extraction/classification and sentiment prediction at aspect level, including joint and pipeline approaches.
3. **Low-resource and multilingual adaptation**: transfer strategies for non-English languages and mixed-language corpora.
4. **Domain adaptation for finance/sustainability text**: adapting general models to ESG/climate disclosure language.
5. **Evaluation reliability**: robustness, calibration, and subgroup error analysis beyond aggregate F1.

Positioning for this repository: transfer learning should be justified not only by higher metrics, but also by improved consistency across ESG aspects and better behavior on real Indonesian sustainability-report language.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Core components already available:

1. OCR and document ingestion
   - `pages/Bulk_OCR.py`
   - dataset artifacts under `data/thesis_dataset/`
2. Extraction and ABSA-related outputs
   - `pages/llm_processing.py`
   - `results/esg_records.json`
   - T2 outputs and related visual artifacts in `results/`
3. Baseline/analysis modules
   - `code/rule_based.py`
   - `code/classical_ml.py`
   - `code/hybrid_model.py`
   - `code/deep_model.py`
4. Evaluation and diagnostics
   - `pages/1_1_Ground_Truth_Workbench.py`
   - `pages/1_3_Ground_Truth_Metrics.py`
   - `pages/2_1_LLM_Error_Parse_Audit.py`
   - revision/stability summaries under `results/revision_analysis/` and `results/thesis_workflow_dashboard/`

### 6.2 Data Construction for Transfer Learning

1. Use existing extracted records and pilot annotations as seed labels.
2. Normalize labels for:
   - aspect taxonomy,
   - ESG pillar (`E`, `S`, `G`),
   - sentiment classes,
   - optional tone classes (commitment/action/outcome).
3. Build train/validation/test splits with document-level separation to reduce leakage.
4. Create sector-aware split views (energy, finance, etc.) for transfer robustness checks.

### 6.3 Model and Transfer Strategies

Candidate strategies:

1. **Feature-based transfer**
   - freeze encoder, train lightweight classifier heads.
2. **Full fine-tuning**
   - fine-tune all parameters on Indonesian ESG ABSA labels.
3. **Parameter-efficient transfer**
   - adapters/LoRA-style updates where feasible in local setup.

Candidate backbones:

1. multilingual transformers,
2. Indonesian-pretrained language models,
3. climate/ESG-relevant encoders as weak-domain priors.

### 6.4 Experimental Design

1. Baselines:
   - rule-based and classical ML outputs from existing modules,
   - current hybrid/deep pipeline outputs as reference.
2. Main metrics:
   - accuracy, precision, recall, weighted/macro F1,
   - Cohen kappa where applicable,
   - per-class confusion matrices.
3. Subgroup evaluation:
   - by ESG pillar,
   - by aspect family,
   - by tone class,
   - by company/sector.
4. Robustness checks:
   - repeated runs with fixed seeds,
   - label-noise sensitivity,
   - out-of-domain document subsets.

### 6.5 Integration Plan in This Repository

1. Add a training/eval worker in `code/` (e.g., `code/transfer_learning_esg_absa.py`).
2. Save outputs to `results/transfer_learning/`:
   - predictions,
   - metrics tables,
   - confusion matrices,
   - per-subgroup diagnostics.
3. Add a Streamlit audit page (e.g., `pages/1_15_Transfer_Learning_ESG_ABSA.py`) reusing chart/report patterns from existing analytics pages.
4. Link results into RQ dashboard and Chapter 4-6 pages.

## 7. Expected Results

With current pipeline maturity, expected outcomes are:

1. Transfer-learned models outperform rule/classical baselines on aspect and sentiment F1.
2. Gains are larger for frequent aspects and smaller for sparse/ambiguous classes.
3. Indonesian-specific and bilingual expressions remain a major source of residual error.
4. Parameter-efficient tuning may provide near full fine-tuning performance with lower compute cost.
5. Performance improvements in aggregate metrics may still hide instability across sectors or tone classes.

## 8. Discussion

Key discussion points:

1. **Practical value**: transfer learning can raise ABSA quality while keeping current pipeline architecture intact.
2. **Data bottleneck**: annotation quality/coverage is still the limiting factor for reliable generalization claims.
3. **Domain drift**: annual-report style changes and sector vocabulary shifts reduce cross-document stability.
4. **Method tradeoff**: full fine-tuning may improve peak accuracy, while parameter-efficient tuning improves reproducibility and cost.
5. **Research validity**: claims should emphasize per-class/subgroup behavior, not only global averages.

## 9. Conclusion

Transfer learning for Indonesian ESG ABSA is feasible in this repository using existing code, artifacts, and dashboards. The main requirement is to formalize a clean labeled training set and run structured adaptation experiments against established baselines. The expected thesis value is a rigorous, reproducible demonstration of when transfer learning materially improves ESG ABSA in Indonesian sustainability-report contexts, and where limitations persist.

---

## Suggested Next Implementation Steps

1. Build `results/transfer_learning/labels_master.csv` by consolidating pilot/human labels with extraction records.
2. Implement `code/transfer_learning_esg_absa.py` for training, inference, and metric export.
3. Add subgroup and error diagnostics aligned with existing `Ground_Truth_Metrics` outputs.
4. Create a Streamlit page for transfer-learning benchmark tracking and thesis integration.
