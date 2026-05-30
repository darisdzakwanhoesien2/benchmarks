codex resume 019e785d-b5b7-79e3-82a1-f8d76b89d25b
# Adapted Research Notes (ESG ABSA Project)

## 1) Project Focus (Adapted From Generic Summarization Notes)
This project is not a generic text-summarization benchmark (e.g., Sumy/Opinosis/WikiSummary). It is an **executable ESG document intelligence pipeline** for Indonesian sustainability reports.

Core workflow:
1. OCR sustainability reports (PDF/image) into page-level text artifacts.
2. Extract structured ESG statements using LLM prompts.
3. Normalize extracted records into ABSA-style fields (aspect, ESG pillar, sentiment, tone, reasoning, provenance).
4. Compare outputs across model families (rule-based, hybrid ABSA, LLM extraction, ClimateBERT comparison layer).
5. Map aspects to ontology paths and export thesis-ready evidence tables/visuals.

## 2) Current Data/Evidence Snapshot (From Our Existing Outputs)
- OCR documents processed: **23**
- Structured ESG tone records: **332**
- T2 flattened outputs: **2,074 rows**
- ClimateBERT proxy agreement: **0.837 (83.7%)**
- Cohen’s kappa (tone vs ClimateBERT proxy label comparison): **0.645**
- Tracked artifacts: **40**

Primary evidence files include:
- `results/thesis_workflow_dashboard/tone_records_flat.csv`
- `results/thesis_workflow_dashboard/t2_flat_outputs.csv`
- `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv`
- `results/thesis_workflow_dashboard/model_stability_summary.csv`
- `results/thesis_workflow_dashboard/prompt_stability_summary.csv`
- `results/thesis_workflow_dashboard/ontology_coverage.csv`

## 3) Research Gap
Existing literature and tooling provide useful pieces (ABSA methods, climate-domain language models, ESG scoring frameworks, LLM extraction), but there is still a practical gap in a **single reproducible, thesis-executable system** that combines:
1. PDF-to-OCR-to-record transformation with provenance.
2. Record-level ESG ABSA schema (aspect, ESG pillar, sentiment, tone), not only document-level scoring.
3. Climate-specific baseline comparison (ClimateBERT) with explicit construct-separation analysis.
4. Prompt/model stability diagnostics for LLM extraction reliability.
5. Ontology mapping and graph-ready ESG evidence for Indonesian/local vocabulary extension.

## 4) Research Questions
1. How can sustainability-report PDFs be transformed into structured ESG evidence records while preserving traceability to source pages?
2. How should ESG disclosures be represented at record level using aspect, ESG pillar, sentiment, and tone labels?
3. How do ESG tone labels compare with ClimateBERT-style climate labels, and what does agreement/disagreement imply about construct validity?
4. How stable are extracted ESG records across prompt templates, models, and providers?
5. To what extent do current ontology mappings cover extracted aspects, and what unmapped items indicate Indonesian ESG vocabulary extension opportunities?

## 5) Research Objective
General objective:
- Build and validate an executable ESG ABSA framework that transforms sustainability reports into structured, auditable, and analyzable evidence.

Specific objectives:
1. Develop an end-to-end OCR + LLM + ABSA pipeline for ESG disclosure processing.
2. Produce record-level ESG outputs with provenance and reproducible artifacts.
3. Evaluate extraction/classification consistency using agreement and stability metrics.
4. Compare ESG tone outputs with ClimateBERT-style climate predictions.
5. Map extracted aspects to ontology paths and identify coverage gaps for extension.

## 6) Research Contributions
1. **Executable end-to-end pipeline**: from raw report PDFs to structured ESG evidence records.
2. **Record-level ESG ABSA schema**: supports finer interpretation than document-level ESG score summaries.
3. **ClimateBERT comparison layer**: demonstrates related-but-distinct constructs between climate labels and ESG tone.
4. **Reproducibility artifacts**: dashboards, CSV summaries, logs, prompt/model stability outputs, and chapter-ready figures.
5. **Ontology-grounded ESG analysis**: links extracted aspects to semantic paths and highlights local vocabulary extension candidates.

## 7) Method/Thesis Positioning Note
This project is positioned as **ESG ABSA and evidence extraction research**, not classic extractive/abstractive summarization benchmarking. Any summarization-style generation is treated as a supportive NLP utility, while the central thesis contribution is structured ESG evidence construction, validation, and ontology-aware interpretation.
