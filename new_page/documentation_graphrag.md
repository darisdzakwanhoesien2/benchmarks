# Documentation: Feasibility of GraphRAG for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

This repository already contains ESG ABSA extraction, ontology mapping, and semantic graph export capabilities. However, there is still a gap in operationalizing these assets into a full **GraphRAG (Graph-based Retrieval-Augmented Generation)** workflow for Indonesian ESG analysis.

Main gaps are:

1. Existing retrieval and analysis workflows are mostly table/dashboard driven, not graph-native retrieval pipelines.
2. Graph artifacts exist, but they are not yet systematically used for grounded conversational or analytical generation.
3. Indonesian ESG semantic relationships (aspect-entity-tone-ontology) are modeled, but not fully exploited for multi-hop question answering.
4. There is no dedicated benchmark for GraphRAG quality in this ESG ABSA context (grounding accuracy, retrieval fidelity, answer faithfulness, and robustness).

## 2. Research Questions

1. Can existing ESG ABSA and ontology outputs be transformed into an effective GraphRAG knowledge layer for Indonesian ESG queries?
2. Does graph-based retrieval improve answer quality over non-graph retrieval baselines for ESG ABSA tasks?
3. Which graph schema and retrieval strategy best supports Indonesian ESG reasoning (entity-centric, aspect-centric, or ontology-path-centric)?
4. What failure modes arise in GraphRAG responses, and how can they be mitigated with validation and provenance controls?

## 3. Research Objectives

1. Build a reproducible GraphRAG pipeline from current repository artifacts.
2. Define a graph schema that captures ESG ABSA semantics, provenance, and ontology alignment.
3. Implement graph-based retrieval and generation for Indonesian-language ESG questions.
4. Evaluate GraphRAG outputs for faithfulness, relevance, and evidence traceability.
5. Integrate GraphRAG findings into existing thesis dashboards and chapter narratives.

## 4. Research Contribution

This study can contribute:

1. A practical GraphRAG architecture for Indonesian ESG ABSA based on an existing end-to-end benchmark.
2. A graph-grounded retrieval protocol linking ABSA records, ontology paths, and source evidence.
3. Empirical comparison between graph-based and conventional retrieval for ESG analysis tasks.
4. A reproducible evaluation framework for grounded ESG answer generation.
5. Reusable graph and QA artifacts for future semantic search, chatbot, and policy-analytics extensions.

## 5. Literature Review (Focused)

Relevant literature streams:

1. **RAG systems**: retrieval-augmented generation for reducing hallucinations and improving factual grounding.
2. **Knowledge graph QA and GraphRAG**: graph-structured retrieval, path reasoning, and multi-hop evidence aggregation.
3. **ESG/financial information extraction**: domain-specific ontology and explainability requirements.
4. **Multilingual and low-resource retrieval**: challenges in Indonesian and mixed-language enterprise texts.
5. **Evaluation of grounded generation**: metrics for retrieval relevance, citation faithfulness, and response correctness.

For this repository, literature should support a core principle: generative answers must be auditable through explicit graph provenance to be valid for thesis-grade ESG analysis.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Key components already available:

1. ESG extraction and ABSA outputs
   - `results/esg_records.json`
   - T2/T3 outputs under `results/`
2. Ontology and graph support
   - `pages/1_6_Ontology_Path_Viewer.py`
   - `pages/1_13_Semantic_Graph_Exporter.py`
   - `code/semantic_exporter.py`
3. Validation and provenance tools
   - `pages/2_2_LLM_Statement_Page_Verifier.py`
   - `pages/2_1_LLM_Error_Parse_Audit.py`
4. Monitoring and thesis integration
   - `pages/1_7_Research_Questions_Dashboard.py`
   - Chapter pages under `pages/6_x_*.py`

### 6.2 Graph Schema Design

Define graph entities (nodes):

1. company,
2. document/page,
3. ESG statement,
4. aspect,
5. ESG pillar,
6. tone,
7. ontology path,
8. model/prompt metadata.

Define relationships (edges):

1. `company -> has_document -> page`,
2. `page -> contains_statement -> statement`,
3. `statement -> has_aspect -> aspect`,
4. `statement -> has_sentiment/tone -> label`,
5. `aspect -> mapped_to -> ontology_path`,
6. `statement -> produced_by -> model/prompt`,
7. provenance links back to source text spans.

### 6.3 GraphRAG Pipeline

1. Build/refresh graph from ABSA and ontology artifacts.
2. Index graph nodes/edges and optional text embeddings.
3. Retrieve candidate subgraphs for a user query (entity match + semantic match + relation expansion).
4. Construct grounded context from retrieved subgraph and evidence spans.
5. Generate Indonesian response constrained by retrieved evidence and citations.

### 6.4 Evaluation Framework

1. Retrieval quality:
   - node/edge relevance,
   - subgraph coverage for target question.
2. Generation quality:
   - answer correctness,
   - faithfulness,
   - completeness.
3. Grounding/provenance:
   - citation presence,
   - citation correctness,
   - traceability to source pages/statements.
4. Comparative benchmarking:
   - GraphRAG vs non-graph RAG,
   - performance by query type (aspect, trend, cross-pillar, company comparison).

### 6.5 Integration Plan in This Repository

1. Add GraphRAG module (e.g., `code/graphrag_esg_absa.py`) for indexing, retrieval, and answer generation.
2. Save artifacts in `results/graphrag/`:
   - graph indices,
   - query/retrieval logs,
   - answer records,
   - grounding metrics.
3. Add Streamlit page (e.g., `pages/2_8_GraphRAG_ESG_ABSA.py`) with query UI and evidence graph view.
4. Connect GraphRAG metrics to RQ dashboard and chapter discussions.

## 7. Expected Results

With current code assets, expected outcomes are:

1. GraphRAG improves multi-hop ESG reasoning and cross-entity query handling.
2. Graph-based provenance reduces unsupported claims compared to unconstrained generation.
3. Ontology-aware retrieval improves consistency of aspect and pillar interpretation.
4. Query performance varies by graph completeness and extraction quality.
5. GraphRAG outputs provide more explainable evidence trails for thesis conclusions.

## 8. Discussion

Key discussion points:

1. **Added value**: GraphRAG combines structured ESG semantics with generative usability.
2. **Constraint benefit**: graph-grounded context can reduce hallucination and improve auditability.
3. **Dependency risk**: weak extraction or ontology mapping errors propagate into graph retrieval quality.
4. **Complexity tradeoff**: GraphRAG adds engineering overhead (schema maintenance, indexing, retrieval tuning).
5. **Research implication**: GraphRAG can shift ESG ABSA from static outputs to explainable, queryable intelligence.

## 9. Conclusion

GraphRAG for Indonesian ESG ABSA is feasible in this repository because the required foundations already exist: structured extraction outputs, ontology mapping, semantic graph export, and validation pages. The key next step is to formalize graph schema and retrieval-generation evaluation so GraphRAG results are reproducible and thesis-ready. The expected contribution is a grounded, explainable QA layer that strengthens ESG analysis quality and accessibility.

---

## Suggested Next Implementation Steps

1. Build canonical GraphRAG schema from existing ABSA and ontology artifacts.
2. Implement `code/graphrag_esg_absa.py` with graph retrieval + grounded answer generation.
3. Create `results/graphrag/` benchmark outputs for retrieval and faithfulness metrics.
4. Add Streamlit GraphRAG page with query interface, retrieved subgraph panel, and citation audit.
