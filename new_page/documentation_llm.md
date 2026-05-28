Below is supported by Codex and this is supported by Claude: https://claude.ai/chat/4f065781-dbab-4d7e-a6b5-0dff6ef9ab9e


# Documentation: Feasibility of LLM-as-a-Judge in This ESG Benchmark

## 1. Research Gap

This repository already implements an end-to-end ESG pipeline (OCR -> T1/T2/T3 -> audits -> ground-truth metrics), but the current evaluation layer is still dominated by:

1. schema-level validity checks (parse success, missing fields, error categories),
2. model-output agreement checks (tone vs ClimateBERT proxy), and
3. limited human-labeled pilot metrics.

The missing layer is a structured **LLM-as-a-judge** mechanism that can evaluate extraction quality beyond JSON parseability and simple label overlap. In other words, we can generate records at scale, but we still lack an automated semantic judge that consistently scores whether each extracted record is faithful, complete, and justified by source evidence.

## 2. Research Questions

The following research questions are suitable for this codebase:

1. Can an LLM judge reliably score T3 ESG extraction quality (faithfulness, completeness, schema adherence, and evidence grounding) from existing artifacts?
2. How consistent are judge scores across models, prompts, reruns, and document contexts?
3. To what extent do LLM judge scores correlate with available human pilot annotations and existing ground-truth metrics?
4. Can judge-generated diagnostics improve failure-mode taxonomy and prioritization (e.g., parse errors vs semantic hallucination vs weak evidence alignment)?

## 3. Research Objectives

1. Design and implement a judge rubric for ESG extraction outputs stored in `results/esg_records.json`.
2. Add judge outputs as reproducible artifacts (JSON/CSV) linked to run metadata (model, prompt, target page/document, timestamp).
3. Benchmark multiple judge settings (single judge, pairwise judges, and self-consistency reruns).
4. Validate judge behavior against existing pilot annotations and confusion-matrix outputs.
5. Integrate judge evidence into Chapter 4-6 dashboards and revision analytics.

## 4. Research Contribution

This study can contribute:

1. A practical LLM-as-a-judge protocol for ESG ABSA extraction in bilingual sustainability-report data.
2. A reproducible judge pipeline integrated with existing background job and audit infrastructure.
3. A multi-dimensional quality signal beyond parse success: factual grounding, ontology consistency, tone maturity alignment, and explanation sufficiency.
4. A bridge between weak supervision (proxy labels) and expensive human annotation through calibrated judge scoring.
5. A structured error taxonomy that separates syntactic validity from semantic validity.

## 5. Literature Review (Focused)

The relevant body of work to position this research includes:

1. **LLM-as-a-judge evaluation frameworks**: work on using LLMs to evaluate generated outputs with rubric-based scoring, pairwise ranking, and self-consistency checks.
2. **Faithfulness and hallucination evaluation**: methods emphasizing source-groundedness and evidence attribution rather than fluency-only scoring.
3. **ABSA and ESG NLP evaluation**: literature on aspect-level sentiment and ESG disclosure analysis, including domain adaptation challenges.
4. **Meta-evaluation and judge bias**: studies showing position bias, verbosity bias, self-preference bias, and prompt sensitivity in LLM judges.
5. **Human-in-the-loop reliability**: frameworks that calibrate automated judges with small high-quality human gold sets.

For this project, the key theoretical claim is: a judge is useful only if it is auditable, repeatable, and aligned with human-labeled constructs already tracked in the repository.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

The repository already provides most required building blocks:

1. **Generation and metadata capture**
   - `code/llm_background_worker.py`
   - `pages/2_3_LLM_Background_Run_Monitor.py`
2. **Extraction result source**
   - `results/esg_records.json`
3. **Parse/failure diagnostics**
   - `pages/2_1_LLM_Error_Parse_Audit.py`
   - `results/revision_analysis/failure_modes.csv`
4. **Human/pilot evaluation anchors**
   - `pages/1_1_Ground_Truth_Workbench.py`
   - `pages/1_3_Ground_Truth_Metrics.py`
5. **Stability artifacts**
   - `results/thesis_workflow_dashboard/model_stability_summary.csv`
   - `results/thesis_workflow_dashboard/prompt_stability_summary.csv`

### 6.2 Judge Design

Define a rubric with scalar dimensions per extracted record:

1. `faithfulness_score` (0-4): Is the extracted claim supported by source text?
2. `completeness_score` (0-4): Are key fields present and semantically filled?
3. `ontology_alignment_score` (0-4): Is aspect-to-ontology mapping coherent?
4. `tone_validity_score` (0-4): Is commitment/action/outcome assignment justified by wording?
5. `reasoning_quality_score` (0-4): Is the explanation concise, specific, and non-generic?
6. `overall_score` (0-100): weighted composite.

Each judgment should also return:

1. `verdict_label` (`accept`, `revise`, `reject`),
2. `failure_tags` (e.g., `hallucination`, `wrong_aspect`, `weak_evidence`, `tone_mismatch`), and
3. `evidence_span` or page reference used by the judge.

### 6.3 Experimental Setup

1. Sample records across models/prompts from existing outputs.
2. Run judge inference with at least three configurations:
   - single judge,
   - judge ensemble (2-3 models),
   - repeated self-consistency runs per same judge prompt.
3. Compare judge outputs with:
   - parse success categories,
   - ground-truth pilot labels,
   - tone vs ClimateBERT agreement tables.
4. Compute reliability statistics:
   - inter-judge agreement,
   - rerun variance,
   - correlation with human labels.

### 6.4 Integration Plan in Current Codebase

1. Add a judge runner (new module under `code/`, e.g., `code/llm_judge_worker.py`) using patterns from `code/llm_background_worker.py`.
2. Store outputs under `results/llm_judge/` (`judge_records.jsonl`, `judge_summary.csv`, `judge_disagreement.csv`).
3. Add a Streamlit page (e.g., `pages/2_6_LLM_Judge_Audit.py`) mirroring patterns from parse audit and metrics dashboards.
4. Connect summaries to revision and thesis workflow dashboards.

## 7. Expected Results

With current artifacts and pipeline maturity, expected outcomes are:

1. Judge scores will differentiate syntactically valid but semantically weak records.
2. Prompt/model combinations with high parse success may still have lower faithfulness scores.
3. Agreement between tone labels and judge tone-validity scores will be moderate, revealing construct boundaries.
4. Judge failure tags will produce a more actionable error taxonomy than parse-only categories.

## 8. Discussion

Likely discussion points for thesis chapters:

1. **Utility**: LLM-as-a-judge reduces manual review load by triaging low-quality records.
2. **Risk**: judge outputs can inherit model biases and may over-reward verbose reasoning.
3. **Validity**: judge metrics should be treated as complementary, not a replacement for human gold labels.
4. **Engineering implication**: stable extraction pipelines need dual quality gates: parser-level and judge-level.
5. **Research implication**: ESG ABSA evaluation benefits from separating topic detection, tone maturity, and factual grounding.

## 9. Conclusion

It is technically feasible to implement LLM-as-a-judge in this repository **without rebuilding the pipeline**, because core prerequisites already exist: structured outputs, run metadata, diagnostics, pilot labels, and dashboard infrastructure. The main research value is not another extractor, but a calibrated semantic evaluation layer that can quantify extraction quality, expose hidden failure modes, and strengthen methodological rigor in Chapters 4-6.

---

## Suggested Next Implementation Steps

1. Implement `code/llm_judge_worker.py` with rubric scoring and JSONL output.
2. Create `results/llm_judge/` schema and aggregation script.
3. Add `pages/2_6_LLM_Judge_Audit.py` for charts, disagreement tables, and export.
4. Link judge metrics into `pages/1_7_Research_Questions_Dashboard.py` and chapter pages.
