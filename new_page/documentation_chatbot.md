# Documentation: Feasibility of Chatbot for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

This repository already has strong ESG ABSA infrastructure (OCR ingestion, structured extraction, ABSA outputs, ontology mapping, validation dashboards). However, there is still a gap in delivering these capabilities through an interactive **chatbot interface** for Indonesian-language users.

Main gaps are:

1. Current workflows are page/dashboard oriented, not conversational and query-driven.
2. ESG ABSA outputs exist, but they are not yet packaged as context-aware responses to natural-language user questions.
3. Evidence traceability is available in artifacts, but not consistently exposed in answer citations during interactive use.
4. There is no formal benchmark for chatbot quality in Indonesian ESG ABSA tasks (accuracy, faithfulness, relevance, safety, and consistency).

## 2. Research Questions

1. Can a chatbot built on existing repository artifacts answer Indonesian ESG ABSA questions accurately and with source-grounded evidence?
2. Which chatbot architecture is most effective in this project: direct prompt-over-records, retrieval-augmented generation (RAG), or workflow-guided hybrid?
3. How well can the chatbot preserve ABSA semantics (aspect, ESG pillar, sentiment, tone) in conversational responses?
4. What are the primary failure modes in Indonesian ESG chatbot responses, and how can they be mitigated?

## 3. Research Objectives

1. Build a reproducible chatbot layer on top of current ESG ABSA outputs.
2. Support Indonesian-language queries about company disclosures, ESG aspects, sentiment/tone, and ontology relations.
3. Ensure responses include evidence links/citations to existing records and source pages.
4. Evaluate chatbot quality with task-specific metrics and failure-mode analysis.
5. Integrate chatbot outputs into existing thesis dashboards and discussion chapters.

## 4. Research Contribution

This study can contribute:

1. A practical Indonesian ESG ABSA chatbot architecture built from existing benchmark components.
2. A grounded conversational interface that translates structured ABSA artifacts into user-facing insights.
3. A reproducible evaluation framework for chatbot faithfulness and ABSA consistency.
4. A taxonomy of chatbot failure modes specific to ESG disclosure analysis.
5. Reusable conversational analytics artifacts for future ESG decision-support tools.

## 5. Literature Review (Focused)

Relevant literature streams:

1. **Task-oriented and retrieval-augmented chatbots**: methods for domain-specific QA with external knowledge grounding.
2. **Conversational AI faithfulness**: hallucination risks and citation-grounding strategies.
3. **Financial/ESG NLP assistants**: domain adaptation and compliance/interpretability requirements.
4. **Multilingual chatbot design**: handling non-English inputs, code-switching, and domain terminology.
5. **Evaluation frameworks**: response relevance, factuality, consistency, helpfulness, and user trust.

For this repository, literature should justify that chatbot quality must be tied to auditable ESG ABSA evidence rather than free-form generative fluency.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Core reusable components:

1. Data and extraction pipeline
   - `pages/Bulk_OCR.py`
   - `pages/llm_processing.py`
   - `results/esg_records.json`
2. Validation/audit tools
   - `pages/2_1_LLM_Error_Parse_Audit.py`
   - `pages/2_2_LLM_Statement_Page_Verifier.py`
   - `pages/1_3_Ground_Truth_Metrics.py`
3. Ontology and graph support
   - `pages/1_6_Ontology_Path_Viewer.py`
   - `pages/1_13_Semantic_Graph_Exporter.py`
4. Job and model orchestration
   - `code/llm_background_worker.py`
   - model catalog and monitoring pages

### 6.2 Chatbot Architecture Options

1. **Direct ABSA-context chatbot**
   - feed selected ESG ABSA records into prompt context.
2. **RAG chatbot**
   - retrieve relevant records/pages first, then generate response with citations.
3. **Hybrid workflow chatbot**
   - route question type (aspect query, sentiment trend, ontology query, company summary) to specialized handlers.

### 6.3 Indonesian Language Handling

1. Normalize user queries (spelling variants, mixed English/Indonesian terms).
2. Map Indonesian ESG terminology to ontology/aspect labels.
3. Preserve bilingual evidence quotes when needed while answering in Indonesian.
4. Add fallback clarification prompts for ambiguous intent.

### 6.4 Evaluation Framework

1. Response quality:
   - relevance,
   - factuality,
   - completeness,
   - clarity.
2. ABSA consistency:
   - correct aspect/ESG pillar/tone references,
   - alignment with stored records.
3. Evidence grounding:
   - citation presence rate,
   - citation correctness.
4. Robustness:
   - repeated-query consistency,
   - adversarial/ambiguous query behavior,
   - out-of-scope detection.

### 6.5 Integration Plan in This Repository

1. Add chatbot service module (e.g., `code/chatbot_esg_absa.py`).
2. Store chat evaluation artifacts under `results/chatbot/`:
   - query logs,
   - response records,
   - grounding checks,
   - failure-mode tables.
3. Add Streamlit chatbot page (e.g., `pages/2_7_Chatbot_ESG_ABSA.py`) with evidence panel.
4. Link metrics to research-question dashboard and chapter pages.

## 7. Expected Results

With current assets, expected outcomes are:

1. The chatbot can answer common Indonesian ESG ABSA questions with usable accuracy when grounded on retrieved records.
2. RAG/hybrid architectures outperform direct prompting in faithfulness and citation quality.
3. Conversational summaries improve user accessibility of ABSA findings.
4. Failure modes will concentrate on ambiguous phrasing, cross-document aggregation errors, and unsupported inference.
5. Grounding and verifier checks significantly reduce hallucination risk.

## 8. Discussion

Key discussion points:

1. **Practical value**: chatbot interaction lowers access barriers to complex ESG ABSA outputs.
2. **Reliability challenge**: conversational fluency can mask factual errors without strict grounding controls.
3. **Method tradeoff**: stronger grounding may increase latency and reduce response brevity.
4. **Data dependency**: OCR and extraction quality directly influence chatbot response quality.
5. **Research implication**: chatbot + ABSA can convert static benchmark artifacts into interactive analytic support.

## 9. Conclusion

Building an Indonesian-language chatbot for ESG ABSA is feasible in this repository using existing extraction, verification, and dashboard infrastructure. The key requirement is to formalize a grounding-first architecture and evaluation protocol so conversational outputs remain accurate, auditable, and thesis-grade. The expected contribution is a robust interface layer that makes ESG ABSA evidence more accessible while preserving methodological rigor.

---

## Suggested Next Implementation Steps

1. Implement `code/chatbot_esg_absa.py` with retrieval and citation support.
2. Create `results/chatbot/` evaluation schema for grounded QA benchmarking.
3. Add Streamlit chatbot page with source-evidence side panel.
4. Integrate chatbot quality metrics into RQ/chapter dashboards.
