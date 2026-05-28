# Documentation: Feasibility of Summarization for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

This repository already supports OCR, ESG extraction, ABSA labeling, ontology mapping, and dashboard reporting. It also includes a dedicated `summarization/` workspace. However, a formal **summarization research track** for Indonesian ESG ABSA is not yet fully integrated as a core benchmark.

Main gaps are:

1. Existing outputs emphasize structured extraction and classification, but not controlled summarization quality for Indonesian ESG disclosures.
2. Summarization artifacts exist, yet linkage between summaries and ABSA fields (aspect, sentiment, tone, ESG pillar) is not systematically evaluated.
3. Current validation focuses on parse stability and label agreement; summary faithfulness, coverage, and hallucination risk are not central metrics.
4. There is no standardized comparison of summarization strategies (extractive, abstractive, hybrid) on this ESG corpus.

## 2. Research Questions

1. Can summarization methods generate faithful and useful Indonesian ESG summaries from existing ABSA/extraction outputs?
2. Which summarization strategy performs best in this repository: extractive, abstractive, or hybrid ABSA-guided summarization?
3. How well do generated summaries preserve key ESG aspects, sentiment/tone signals, and evidence traceability?
4. Can summary-level evaluation improve interpretability and decision support beyond record-level ABSA outputs?

## 3. Research Objectives

1. Build a reproducible summarization pipeline using existing ESG ABSA artifacts.
2. Compare multiple summarization strategies for Indonesian sustainability-report content.
3. Evaluate summary quality with faithfulness, coverage, and ABSA-alignment metrics.
4. Integrate summarization outputs into existing dashboards and thesis chapters.
5. Demonstrate how summarization complements ABSA for faster and clearer ESG interpretation.

## 4. Research Contribution

This study can contribute:

1. A practical summarization framework for Indonesian ESG ABSA within an operational thesis system.
2. An ABSA-aware summarization protocol that preserves aspect, sentiment, tone, and ESG pillar signals.
3. Empirical evidence on tradeoffs between concise summaries and factual/evidence fidelity.
4. A reproducible evaluation setup for summary faithfulness and ESG coverage.
5. Reusable summary artifacts for stakeholder reporting, chapter writing, and downstream analytics.

## 5. Literature Review (Focused)

Relevant literature streams:

1. **Extractive and abstractive summarization**: methods for selecting or generating concise content from long documents.
2. **Faithfulness and hallucination in summarization**: risk of unsupported claims and methods for evidence-grounded summarization.
3. **Domain-specific summarization**: adaptation challenges for financial/sustainability narrative text.
4. **Multilingual/low-resource summarization**: quality constraints for non-English and bilingual corpora.
5. **Evaluation frameworks**: lexical overlap, semantic similarity, factual consistency, and human utility assessments.

For this repository, literature should support one practical claim: summaries are valuable only when they remain aligned with auditable ABSA evidence and source text.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Available assets include:

1. Summarization workspace
   - `summarization/app.py`
   - `summarization/data/` sample summary and coverage tables
2. ESG extraction and ABSA outputs
   - `results/esg_records.json`
   - T2/T3 outputs under `results/`
3. Validation and diagnostics
   - `pages/2_1_LLM_Error_Parse_Audit.py`
   - `pages/1_3_Ground_Truth_Metrics.py`
   - revision artifacts under `results/revision_analysis/`
4. Thesis integration pages
   - `pages/1_7_Research_Questions_Dashboard.py`
   - Chapter pages under `pages/6_x_*.py`

### 6.2 Summary Unit Design

Define summary granularities:

1. record-level summaries,
2. company-level ESG summaries,
3. sector-level comparative summaries,
4. chapter-ready analytical summaries.

Each summary should carry metadata:

1. source document/page references,
2. dominant aspects and ESG pillars,
3. sentiment/tone distribution,
4. generation model/prompt configuration.

### 6.3 Summarization Strategies

1. **Extractive baseline**
   - sentence selection using ABSA salience and evidence weights.
2. **Abstractive summarization**
   - LLM-based generation constrained by structured ABSA inputs.
3. **Hybrid ABSA-guided summarization**
   - extractive evidence scaffold + abstractive rewrite with validation checks.

### 6.4 Evaluation Framework

1. Faithfulness and factuality:
   - unsupported-claim rate,
   - source-evidence alignment checks.
2. Coverage quality:
   - proportion of key ABSA aspects represented,
   - ESG pillar coverage,
   - tone/sentiment preservation.
3. Utility and readability:
   - concise clarity for thesis/report consumers,
   - consistency across reruns.
4. Comparative benchmarking:
   - by company,
   - by sector,
   - by summarization strategy/model/prompt.

### 6.5 Integration Plan in This Repository

1. Extend summarization pipeline to export standardized outputs under `results/summarization/`.
2. Save:
   - summaries,
   - evidence links,
   - coverage/factuality metrics,
   - strategy comparison tables.
3. Add or extend Streamlit summarization page for filtering, auditing, and export.
4. Link outputs into RQ dashboard and Chapter 4-6 narrative sections.

## 7. Expected Results

With current code and artifacts, expected outcomes are:

1. ABSA-guided summaries improve ESG signal coverage compared with generic summarization.
2. Extractive methods provide stronger evidence traceability, while abstractive methods improve readability.
3. Hybrid approaches achieve better balance between faithfulness and interpretive clarity.
4. Summary quality varies by sector and document style due to vocabulary and disclosure structure differences.
5. Summarization outputs provide a practical bridge from technical ABSA records to decision-ready narrative insights.

## 8. Discussion

Key discussion points:

1. **Added value**: summarization accelerates interpretation of large ESG corpora without discarding ABSA structure.
2. **Risk**: abstractive summaries can introduce hallucination unless constrained by source-evidence checks.
3. **Method tradeoff**: high readability may reduce strict traceability; explicit evidence links are required.
4. **Data dependency**: OCR noise and extraction errors propagate into summary quality.
5. **Thesis implication**: combining ABSA + summarization strengthens reporting clarity and chapter-level synthesis.

## 9. Conclusion

Summarization for Indonesian ESG ABSA is feasible in this repository using existing extraction outputs, summarization workspace components, and dashboard integration. The main work is to formalize ABSA-aware summary generation and robust faithfulness/coverage evaluation. The expected contribution is a reproducible summary layer that improves usability of ESG ABSA results while preserving analytical rigor.

---

## Suggested Next Implementation Steps

1. Consolidate summary input tables from `results/esg_records.json` and ABSA outputs.
2. Extend `summarization/` pipeline to produce `results/summarization/` standardized artifacts.
3. Add factuality and ABSA-coverage audit tables to summary outputs.
4. Integrate summary evidence into research-question and chapter dashboards.
