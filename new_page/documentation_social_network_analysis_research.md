# Complete Research Write-up: Social Network Analysis (SNA) for Indonesian ESG Disclosure Networks

This document turns the existing `social_network_analysis/` implementation into a defensible thesis-style research chapter structure: research gap, questions, objectives, contribution, literature review, methodology, results plan, discussion, and conclusion.

It is written to match what currently exists in this repository:

- OCR dataset under `data/thesis_dataset/*/ocr_result.json`
- Existing Streamlit SNA prototype: `social_network_analysis/app.py`
- Task design + phase framing: `social_network_analysis/task_data.py` and `social_network_analysis/pages/*`
- Broader ESG ABSA pipeline docs: `research_documentation.md`, `documentation_social_network_analysis.md`

If you want this chapter to be “results-complete” (with numbers/tables), run the SNA scan successfully and copy key summary outputs into the Results section. Right now, the code is present but environment constraints may prevent execution unless dependencies are installed.

---

## 1. Background and Problem Statement

Indonesian sustainability reporting is expanding in volume and regulatory importance, but the practical challenge remains: **narratives are easy to write and hard to audit**. Traditional sentiment analysis, or even aspect-based sentiment analysis (ABSA), largely treats disclosures as independent records (sentences/pages). This is informative but incomplete: ESG reporting is also a *relational phenomenon*—themes co-occur, entities recur, and disclosure sections form repeatable templates. These relational patterns can be studied as graphs.

This repository already builds a strong pipeline for extracting ESG text evidence (OCR → ABSA/LLM extraction → dashboards). The missing layer is a rigorous **social network analysis (SNA)** methodology that converts those textual artifacts into networks and uses graph metrics (centrality, community structure, bridging) to detect disclosure structure, narrative concentration, and potential “credibility gaps” where persuasive language is not matched by quantitative evidence.

---

## 2. Research Gap

Even with the existing end-to-end ESG text pipeline in this repo, there are identifiable research gaps:

1. **Relational structure is under-modeled.** Current ABSA-style outputs are record-level and do not consistently quantify *how* disclosures connect across reports, years, and firms.
2. **SNA is often used in social media, but less in section-level ESG disclosure networks.** Many network studies focus on actors and interactions; ESG disclosures require different graph units (section/topic/entity) and careful validity constraints.
3. **Interpretability lacks a structural audit heuristic.** Existing sentiment/tone approaches can be gamed by verbosity and positive language. A graph layer can prioritize which disclosure sections sit on bridges and hubs (high influence), then evaluate them for evidence density.
4. **Indonesia-specific ESG phrasing and bilingual structure need explicit handling.** The corpus is multilingual and domain-specific; network construction must be robust to Indonesian/English templates and OCR artifacts.

These gaps are exactly what the existing `social_network_analysis/app.py` begins to address, but a complete research narrative (and evaluation boundaries) must be made explicit.

---

## 3. Research Questions

**RQ1 (Feasibility / Representation):**  
Can the ESG disclosure outputs in this repository be transformed into meaningful *section-level social-semantic networks* for Indonesian sustainability reports?

**RQ2 (Design / Validity):**  
Which node and edge design is most defensible and interpretable for ESG disclosures (e.g., section-section co-entity links, aspect-aspect co-occurrence, company-aspect bipartite graphs, aspect-tone graphs)?

**RQ3 (Structure / Findings):**  
What network patterns (hubs, bridges, communities, density, assortativity) characterize Indonesian ESG reporting, and do they differ by year and ESG pillar?

**RQ4 (Added Value / Audit Heuristic):**  
Do SNA-derived metrics provide explanatory value beyond ABSA label counts—specifically for prioritizing narrative-risk candidates where positive language is not matched by quantitative evidence density?

---

## 4. Research Objectives

1. **Build a reproducible SNA layer** that reuses the existing OCR dataset and pipeline artifacts in this repository.
2. **Define and compare multiple graph schemas** (at minimum: section co-entity networks; optionally: aspect networks and bipartite graphs).
3. **Compute and interpret standard network measures** (degree/bridging/communities; density; clustering; connected components).
4. **Connect network structure to disclosure quality signals** already present or computable from text (positivity cues vs metric/evidence cues).
5. **Integrate results into thesis narrative** (RQ framing → method → results tables/figures → defensible limitations).

---

## 5. Research Contribution

This project contributes:

1. **A practical graph-based extension** to an existing Indonesian ESG ABSA pipeline.
2. **A reproducible transformation protocol** from OCR report sections into networks with explicit node/edge definitions and thresholds.
3. **A combined structural + evidence diagnostic** (bridge/hub detection + positivity-vs-metric density heuristic) for narrative-risk prioritization.
4. **Corpus-wide and longitudinal network artifacts** suitable for downstream knowledge graph / GraphRAG work.
5. **A thesis-ready interpretation boundary**, clarifying when network signals are informative vs. when they are likely artifacts of OCR or template language.

---

## 6. Literature Review (Targeted)

This thesis chapter should ground itself in five literature streams (citations to be inserted based on your preferred bibliography workflow):

1. **SNA fundamentals and centrality**
   - Definitions and interpretations of degree, betweenness, closeness, eigenvector centrality.
2. **Community detection**
   - Modularity-based community detection; robustness and resolution issues; practical algorithms.
3. **Text-to-network transformation**
   - Co-occurrence networks; semantic networks; entity networks; pitfalls in token/entity extraction and threshold selection.
4. **ESG disclosure analysis and greenwashing**
   - Why narratives can be strategically framed; why evidence-based signals matter.
5. **Explainability and validity**
   - Sensitivity analysis, stability under threshold changes, and triangulation against independent evidence.

**Important thesis positioning:** This repository’s SNA is not “social network” in the actor-interaction sense; it is a *social-semantic disclosure network* where nodes represent disclosure units (sections), and edges represent shared entities/terms.

---

## 7. Methodology

### 7.1 Data

**Primary corpus (already in repo):**

- `data/thesis_dataset/*/ocr_result.json`  
  Each document contains a list of pages; each page includes a `markdown` field (plus tables/images metadata).

**Unit of analysis (current implementation):**

- A **section** is defined by splitting concatenated OCR markdown using blank-line boundaries, then filtering out short chunks (`>= 220` chars), as in `social_network_analysis/app.py`.

### 7.2 Network Construction (Current Baseline)

**Baseline graph (implemented in `social_network_analysis/app.py`):**

- Graph type: undirected weighted graph `G = (V, E)`
- Nodes: section nodes `doc::sec_XXX`
- Node attributes:
  - `doc`, `year` (regex-based extraction), `pillar` (keyword heuristic),
  - `token_count`,
  - `positive_hits` (lexicon cues),
  - `metric_hits` (units/numbers cues),
  - `entity_count`, `entities` (token frequency-based “entity proxy”)
- Edges:
  - Edge added between sections in the same document if they share at least 2 extracted entities.
  - Weight = number of shared entities.

**Justification:** A section-level node captures local disclosure context better than whole-report nodes, and shared-entity edges operationalize topical relatedness without requiring full NER models.

### 7.3 Analytical Measures

At minimum, report:

- Graph size and connectivity: `|V|`, `|E|`, connected components, density
- Centrality:
  - Degree centrality (hubs)
  - Betweenness centrality (bridges)
  - (Optional) closeness, eigenvector centrality
- Communities:
  - Greedy modularity communities (already used in `app.py`)
- ESG pillar composition:
  - Node distribution by pillar (E/S/G/Mixed)

### 7.4 Evidence Density vs Narrative Positivity (Heuristic)

The current code implements:

- `positive_per_1k_tokens` and `metric_per_1k_tokens`
- `risk_score = (positive_per_1k + 1) / (metric_per_1k + 1)`

**Interpretation boundary:** This is a *prioritization heuristic*, not a greenwashing classifier. It flags sections that are:

- structurally influential (high betweenness / hub-like), and
- highly positive but low in quantitative evidence markers.

This can support audit prioritization and deeper manual review.

### 7.5 Validation and Robustness

To make the research defensible, include:

1. **Threshold sensitivity tests**
   - Vary the shared-entity threshold (e.g., 1, 2, 3) and entity-frequency threshold.
2. **Alternate entity extraction**
   - Compare simple token-frequency proxies vs. (optional) NER models.
3. **Cross-check with ABSA outputs**
   - Confirm that central nodes correspond to high-frequency or high-impact aspects.
4. **Manual interpretability check**
   - Sample top-bridge and top-risk sections; report representative snippets.

---

## 8. Results (What to Report)

This section should contain *numbers and artifacts* generated from the pipeline. Suggested tables/figures:

1. **Dataset coverage table**
   - number of OCR documents, year counts
2. **Network summary table**
   - nodes, edges, density, components, avg degree, clustering
3. **Top hubs / bridges**
   - top 20 sections by degree centrality and betweenness, with `doc`, `year`, `pillar`
4. **Community structure**
   - top communities by size; optionally interpret themes by inspecting shared entities
5. **Narrative-risk shortlist**
   - top 20 by `risk_score` among high-betweenness nodes, with justification and section excerpts

If execution is blocked, keep Results as an “expected results and reporting plan” and explicitly label it as such in the thesis draft.

---

## 9. Discussion

Recommended discussion structure:

1. **What the network adds beyond ABSA**
   - relational interpretability: hubs/bridges, discourse modules, repeated templates
2. **Interpretation of bridges**
   - bridges as “connectors” between governance compliance language and environmental commitments, etc.
3. **Narrative-risk heuristic implications**
   - why positivity + low metric density matters, and why it must be validated manually
4. **Indonesia-specific implications**
   - bilingual phrasing, sector reporting templates, regulatory reporting incentives
5. **Limitations**
   - token-based “entity proxies” are not true entities; OCR noise; threshold sensitivity; community resolution issues

---

## 10. Conclusion

This repository already contains the essential building blocks for a complete SNA study of Indonesian ESG disclosures: a large OCR corpus, ABSA/LLM extraction infrastructure, and a working Streamlit prototype that constructs section-level co-entity graphs and computes core network metrics.

The research value lies in turning these artifacts into a formal methodology with robust reporting and validation boundaries. The expected outcome is a defensible graph-based interpretability layer that complements ABSA by revealing structural hubs, bridges, and discourse communities, and by prioritizing high-influence sections for deeper audit when persuasive narrative outpaces quantitative evidence.

---

## Appendix A: Implementation Anchors in This Repo

- SNA prototype (corpus-wide scan): `social_network_analysis/app.py`
- Task framing + literature task list: `social_network_analysis/task_data.py`
- SNA mini-pages: `social_network_analysis/pages/`
- Existing SNA feasibility doc: `documentation_social_network_analysis.md`
- Pipeline overview doc: `research_documentation.md`

