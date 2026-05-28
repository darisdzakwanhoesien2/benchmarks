# Documentation: Feasibility of Social Network Analysis for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

This repository already provides ESG extraction, ABSA labels, ontology mapping, and visualization artifacts. However, there is still a gap in using these outputs as a formal **Social Network Analysis (SNA)** layer for Indonesian ESG discourse.

Main gaps are:

1. Current analyses focus on classification and dashboards, but not on graph-theoretic modeling of relationships among ESG aspects, entities, tones, and disclosures.
2. Co-occurrence and linkage information exists in outputs, yet network structure (centrality, modularity, bridges, communities) is not consistently quantified as a core experiment.
3. Indonesian ESG language patterns (sector terms, governance phrasing, environmental claims) are not yet systematically examined through network topology.
4. Existing evaluation mostly targets prediction quality; it does not deeply assess whether network structures reveal narrative concentration, disclosure fragmentation, or greenwashing risk signals.

## 2. Research Questions

1. Can ESG ABSA outputs in this repository be transformed into meaningful social-semantic networks for Indonesian sustainability disclosures?
2. Which node/edge design best captures ESG relationships: aspect-aspect, company-aspect, aspect-tone, or aspect-ontology-path networks?
3. What network patterns (central nodes, communities, bridge nodes) characterize Indonesian ESG reporting across sectors?
4. Can SNA-derived metrics provide additional explanatory value beyond standard ABSA metrics for identifying disclosure emphasis and potential risk patterns?

## 3. Research Objectives

1. Build a reproducible SNA pipeline from existing ESG ABSA artifacts.
2. Define multiple network construction schemas and compare their interpretability.
3. Quantify structural properties of Indonesian ESG disclosure networks using centrality and community metrics.
4. Integrate SNA outputs into existing dashboards and chapter evidence.
5. Evaluate whether SNA findings enrich ESG ABSA interpretation and thesis conclusions.

## 4. Research Contribution

This study can contribute:

1. A practical graph-based extension of Indonesian ESG ABSA within an existing end-to-end thesis system.
2. A network analytics protocol linking textual ABSA outputs to structural disclosure insights.
3. Empirical evidence on dominant ESG themes and cross-theme bridges in Indonesian reports.
4. A complementary interpretability layer that augments label-level evaluation with relational structure.
5. Reusable network artifacts for future GraphRAG/knowledge-graph and ESG monitoring work.

## 5. Literature Review (Focused)

Relevant literature streams:

1. **Social Network Analysis fundamentals**: centrality, density, clustering, assortativity, and community detection.
2. **Text-to-network transformation**: constructing networks from co-occurrence, semantic relations, and document metadata.
3. **ESG and sustainability discourse networks**: graph-based analysis for stakeholder communication and topic diffusion.
4. **ABSA and relational semantics**: moving from per-instance labels to relationship-aware interpretability.
5. **Network robustness and validity**: sensitivity of results to thresholding, edge weighting, and preprocessing choices.

For this repository, literature should justify that network evidence is valuable when grounded in auditable ABSA records and not treated as a purely exploratory visualization.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Key assets already present:

1. ESG extraction and ABSA outputs
   - `pages/llm_processing.py`
   - `results/esg_records.json`
   - T2/T3 derived outputs under `results/`
2. Ontology and relational mapping support
   - `pages/1_6_Ontology_Path_Viewer.py`
   - ontology coverage files in `results/revision_analysis/`
3. Graph-oriented and export tools
   - `pages/1_13_Semantic_Graph_Exporter.py`
   - `code/semantic_exporter.py`
4. Existing SNA workspace
   - `social_network_analysis/`
5. Thesis dashboards and chapter integration pages
   - `pages/1_7_Research_Questions_Dashboard.py`
   - Chapter 4-6 pages under `pages/6_x_*.py`

### 6.2 Network Construction Design

Potential node types:

1. aspect nodes,
2. ESG pillar nodes,
3. tone nodes,
4. company/document nodes,
5. ontology-path nodes.

Potential edge definitions:

1. aspect-aspect co-occurrence within record/page/document,
2. company-aspect mention links,
3. aspect-tone association links,
4. aspect-ontology path mapping links,
5. sentiment transition links across sections/documents.

Edge weights can use frequency, normalized PMI-like scores, or confidence-weighted counts.

### 6.3 Analytical Procedures

1. Build multiple graph variants (bipartite and projected graphs).
2. Compute structural metrics:
   - degree, betweenness, closeness, eigenvector centrality,
   - density and clustering coefficient,
   - connected components,
   - modularity-based communities.
3. Compare network structure across:
   - sectors,
   - ESG pillars,
   - tone categories,
   - prompt/model subsets.
4. Link network anomalies to known failure modes and ontology gaps.

### 6.4 Validation Strategy

1. Internal validity:
   - sensitivity tests on edge thresholds,
   - repeated construction with alternate preprocessing.
2. Cross-reference validity:
   - compare central nodes with high-frequency ABSA outputs,
   - compare bridge nodes with disagreement/failure-mode cases.
3. Expert interpretability checks:
   - manually inspect top central/bridge nodes and representative source statements.

### 6.5 Integration Plan in This Codebase

1. Add/extend SNA processing module (e.g., `social_network_analysis/` scripts or `code/sna_esg_absa.py`).
2. Save outputs under `results/social_network_analysis/`:
   - node/edge tables,
   - centrality rankings,
   - community assignments,
   - network figures.
3. Add Streamlit page (e.g., `pages/1_17_SNA_ESG_ABSA.py`) with filters and download support.
4. Link selected figures/tables into RQ dashboard and Chapter 4-6 narrative.

## 7. Expected Results

With current repository assets, expected outcomes are:

1. Clear hub aspects will emerge (e.g., frequent governance/environmental anchors).
2. Bridge nodes will reveal cross-pillar disclosure connections (for example governance-language linked to environmental commitments).
3. Community structures will differentiate sector-specific ESG narratives.
4. Network-based diagnostics will highlight concentration patterns and under-represented aspects not obvious in flat ABSA tables.
5. SNA insights will complement, not replace, standard ABSA performance metrics.

## 8. Discussion

Key discussion points:

1. **Added value**: SNA provides relational interpretability beyond isolated label counts.
2. **Method sensitivity**: network conclusions depend on edge-definition and threshold choices, requiring transparent reporting.
3. **Data quality dependency**: extraction errors and ontology inconsistencies propagate into graph structure.
4. **Practical implication**: SNA can guide ontology refinement, annotation focus, and risk-oriented ESG review priorities.
5. **Research implication**: combining ABSA + SNA strengthens narrative analysis for Indonesian sustainability disclosures.

## 9. Conclusion

Social Network Analysis for Indonesian ESG ABSA is feasible in this repository using existing extraction outputs, ontology mappings, and graph-export infrastructure. The main work is to formalize network-construction protocols, validate structural findings, and integrate them into thesis evidence pages. The expected contribution is a robust relational layer that deepens ESG ABSA interpretation and supports more defensible analytical conclusions.

---

## Suggested Next Implementation Steps

1. Build canonical node/edge schemas from `results/esg_records.json` and ontology outputs.
2. Implement `results/social_network_analysis/` artifact generation (centrality, communities, and graph tables).
3. Add a dedicated Streamlit SNA page for filtering, visualization, and export.
4. Map key SNA findings to research questions and chapter-level discussion outputs.
