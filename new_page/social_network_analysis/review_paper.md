# Social Network Analysis for Indonesian ESG Disclosures: A Review and an Evidence-Ready Research Blueprint

## Abstract

Environmental, Social, and Governance (ESG) reporting has expanded rapidly in Indonesia, creating both opportunities for transparency and risks of narrative-driven disclosure that is difficult to audit at scale. Most automated approaches to ESG text analysis emphasize document-level ratings or record-level sentiment/aspect labels. While valuable, these methods often under-model *relational structure*: how disclosures connect across sections, themes, entities, and time. Social Network Analysis (SNA)—originally developed for actor–relation networks—offers a complementary lens for ESG discourse by quantifying connectivity, influence, bridging, and community structure within networks derived from text. This review synthesizes (i) core SNA concepts relevant to disclosure networks, (ii) text-to-network construction strategies and validity pitfalls, (iii) ESG discourse and greenwashing-oriented motivations for structural analysis, and (iv) practical methodological guidance for building defensible section-level disclosure graphs. It concludes with an implementation-ready blueprint aligned to an existing end-to-end OCR→ESG extraction benchmark repository, where OCR report sections become nodes and shared entities/terms create weighted edges. The proposed blueprint emphasizes transparency, robustness checks (threshold sensitivity, alternative extraction), and an “audit prioritization” framing that treats graph signals as *screening heuristics* rather than definitive greenwashing classifiers.

## Keywords

Social network analysis; ESG disclosure; sustainability reporting; Indonesia; text-to-network; semantic networks; community detection; centrality; audit prioritization; greenwashing risk.

---

## 1. Introduction

ESG reporting is increasingly central to how firms communicate risk management, compliance, and sustainability strategies to stakeholders. In Indonesia, sustainability reporting requirements and market expectations have increased the quantity and visibility of corporate ESG disclosures. However, the practical problem remains: **narrative is easy to produce and hard to verify**. Long reports can contain thousands of sentences with mixed languages (Indonesian and English), varied structures, and uneven evidence quality. Manual audit is expensive, and automated scoring systems often lack sentence-level traceability.

Natural Language Processing (NLP) approaches such as sentiment analysis and Aspect-Based Sentiment Analysis (ABSA) help by extracting structured labels from unstructured text, producing traceable records. Yet ESG disclosure is not only a collection of independent statements—disclosure is also *structural*. Firms reuse templates, repeat entities, and connect governance language to environmental commitments or social initiatives. These relationships can be represented as graphs and studied with Social Network Analysis (SNA).

This review paper focuses on **SNA as a method for ESG disclosure networks**, particularly suited to Indonesian report corpora where OCR outputs and bilingual text complicate conventional pipelines. The paper also provides an **evidence-ready blueprint** for building and validating disclosure networks, designed to integrate with an existing benchmark codebase that already contains OCR outputs and ESG extraction artifacts.

---

## 2. Scope and Research Framing

### 2.1 What “social network” means in this context

In classic SNA, nodes are social actors (people, organizations) and edges are social relations (communication, friendship, collaboration). In ESG disclosure analysis, the “social” dimension is different: the network often represents **discourse units and semantic relations**, not direct social ties. This review uses the term **social-semantic disclosure networks** to emphasize that:

- nodes may be disclosure sections, aspects, entities, or documents, and
- edges represent co-occurrence, association, similarity, or citation-like linkage within textual evidence.

### 2.2 Intended use: interpretability and audit prioritization

The primary value proposition of SNA in ESG disclosure is **interpretability at scale**:

- **Hubs**: sections/themes that dominate the disclosure network.
- **Bridges**: sections/themes that connect otherwise separate clusters, potentially shaping narrative flow.
- **Communities**: groups of sections/themes that form recurring discourse modules (e.g., governance-compliance modules, climate-target modules).

Importantly, network indicators should generally be framed as **screening signals** for audit prioritization. They can help analysts decide *where to read first* and *what to compare*, rather than directly labeling content as misleading.

---

## 3. Foundations: SNA Concepts Most Relevant to Disclosure Networks

### 3.1 Network representation

A network is typically expressed as a graph \(G=(V,E)\):

- \(V\): nodes (sections, entities, aspects, documents)
- \(E\): edges (co-occurrence links, associations)
- weights: frequency, similarity, or other strength measures

Disclosure networks often benefit from:

- **weighted edges** (strength of association),
- **node attributes** (year, sector, ESG pillar, tone, evidence markers), and
- **multi-layer design** (e.g., bipartite graphs projected to single-mode graphs).

### 3.2 Centrality (influence and structural importance)

Centrality measures quantify structural importance. For ESG discourse networks:

- **Degree centrality**: indicates hubs that connect to many nodes (broadly recurring disclosure content).
- **Betweenness centrality**: identifies bridges that lie on many shortest paths (narrative connectors linking clusters).
- **Closeness centrality**: indicates nodes that are on average near others (globally “reachable” narrative units).
- **Eigenvector centrality**: emphasizes nodes connected to other central nodes (structural reinforcement).

Interpretation note: centrality depends heavily on graph construction choices; therefore results must be accompanied by sensitivity analysis.

### 3.3 Community detection (discourse modules)

Community detection partitions the network into groups with denser internal connections. In disclosure networks, communities often correspond to:

- standardized reporting modules,
- sector-specific ESG emphases,
- repeated regulatory compliance narratives,
- reporting “templates” reused across years.

Because community structure can change with thresholding and weighting, community detection should be treated as exploratory unless stability is demonstrated.

### 3.4 Macro-structure: density, components, clustering, assortativity

Global network properties help describe corpus-level disclosure structure:

- **Density**: overall connectedness (high density may reflect generic boilerplate vocabulary).
- **Connected components**: fragmentation; potential separation of themes or document groups.
- **Clustering coefficient**: triangle density; may indicate repeated co-topic triads.
- **Degree assortativity**: whether high-degree nodes connect to high-degree nodes (structure of narrative hubs).

---

## 4. Text-to-Network Transformation: Design Space and Pitfalls

Transforming text into a network is the core methodological decision in disclosure SNA. This section outlines major options and risks.

### 4.1 Choice of node type (what becomes a node?)

Common node choices:

1. **Section nodes** (recommended for interpretability):
   - pro: preserves local context; supports section-level audit
   - con: depends on segmentation quality (OCR formatting)
2. **Entity nodes**:
   - pro: closer to “actor-like” nodes; supports co-entity networks
   - con: requires robust entity extraction; OCR noise can dominate
3. **Aspect/ontology nodes**:
   - pro: aligns with ABSA and ESG taxonomies
   - con: depends on classifier/ontology validity
4. **Document nodes**:
   - pro: simple and stable
   - con: too coarse; mixes unrelated themes

### 4.2 Choice of edge definition (what becomes an edge?)

Common edge definitions:

- **Co-occurrence**: within section/page/document windows.
- **Shared entities**: link sections that share repeated entities/terms.
- **Similarity**: embedding cosine similarity; more semantic but less transparent.
- **Bipartite association**: e.g., company–aspect, aspect–tone; then projection.

Edge definition is inseparable from interpretation. For example, “shared entities” links imply topical overlap, not causal influence.

### 4.3 Weighting and thresholding

Edge weights can reflect:

- raw frequency counts,
- normalized association (e.g., PMI-like normalization),
- confidence-weighted counts (down-weight OCR low-confidence pages),
- time-weighted links (dynamic networks).

Thresholding is often required to reduce noise but can introduce bias:

- too low: boilerplate dominates; network becomes dense and uninformative
- too high: network fragments; loses bridges and small themes

Therefore, **threshold sensitivity analysis** should be planned from the start.

### 4.4 Validity threats

Disclosure SNA is sensitive to:

- OCR errors (spurious tokens, broken hyphenation, missing whitespace)
- bilingual tokenization issues
- boilerplate/legal disclaimers
- inconsistent section segmentation
- simplistic “entity proxies” (frequent tokens that are not true entities)

A defensible paper must explicitly document these risks and include mitigation steps.

---

## 5. ESG Disclosure Analytics: Why Structure Matters

### 5.1 Beyond label counts

ABSA and related approaches can tell us:

- which aspects are mentioned frequently,
- sentiment toward each aspect,
- tone categories (commitment vs action vs outcome).

But they may miss:

- how themes are bundled (communities),
- which sections connect governance to environmental promises (bridges),
- whether narrative emphasis is structurally concentrated around a few recurring modules (hub dominance),
- how discourse evolves over time (dynamic changes).

### 5.2 Greenwashing and “credibility gaps”

A central motivation is the difference between:

- persuasive, positive claims, and
- measurable, auditable evidence.

Network structure can support credibility analysis by identifying influential sections (bridges/hubs) and then comparing language-based positivity with quantitative evidence markers (numbers, units, targets, baselines). The intended outcome is an *audit shortlist*—high-impact sections where the credibility gap may be largest.

Crucially, this is not a deterministic greenwashing detector; it is a prioritization mechanism that supports manual verification.

---

## 6. Review of Method Families for ESG Disclosure Networks

This section summarizes method families you can position within a review paper. The goal is not exhaustive coverage of every paper, but a coherent map of approaches and trade-offs.

### 6.1 Co-occurrence and semantic networks

Approach:

- tokenize text, extract terms/entities, create co-occurrence edges using windows.

Strengths:

- transparent and reproducible
- minimal dependency footprint

Weaknesses:

- sensitive to preprocessing and thresholds
- “entity proxies” may reflect style rather than substance

### 6.2 Topic-model-based networks

Approach:

- build topic mixtures; connect documents/sections to topics; project into topic networks.

Strengths:

- reduces lexical noise
- interpretable at thematic level

Weaknesses:

- topic instability; requires careful model selection

### 6.3 ABSA/ontology-driven networks

Approach:

- treat aspects/ontology nodes as canonical; connect them via co-mention or inferred relations.

Strengths:

- aligns with ESG frameworks and controlled vocabularies
- more robust across languages if taxonomy mapping is strong

Weaknesses:

- depends on classifier accuracy and ontology completeness

### 6.4 Embedding similarity graphs

Approach:

- represent sections with embeddings; connect by similarity threshold or kNN.

Strengths:

- captures semantic similarity beyond surface tokens

Weaknesses:

- less transparent; similarity thresholds can be arbitrary
- can encode model biases

### 6.5 Dynamic disclosure networks

Approach:

- build year-by-year networks; analyze evolution of structure.

Strengths:

- directly supports longitudinal ESG questions

Weaknesses:

- requires consistent preprocessing; network comparability across time is non-trivial

---

## 7. An Evidence-Ready Blueprint (Aligned to an Existing OCR→ESG Pipeline)

This section proposes a complete methodology that can be implemented in an OCR-based benchmark repository.

### 7.1 Data source and unit of analysis

Data:

- OCR outputs stored as JSON with `pages[*].markdown` fields.

Unit of analysis (baseline):

- **Section** derived from splitting concatenated OCR markdown by blank lines, filtering out short chunks.

Rationale:

- section nodes are audit-friendly and preserve local narrative.

### 7.2 Baseline network design: section-level co-entity graph

Graph:

- nodes: `doc::sec_XXX`
- node metadata: year, pillar (keyword heuristic), token count
- “entity proxy” extraction: frequent tokens excluding stopwords
- edges: connect sections (within a document) if they share ≥2 entities
- edge weight: number of shared entities

### 7.3 Metrics and outputs (minimum reporting set)

Network summary:

- number of documents (coverage)
- nodes, edges
- density, connected components
- average degree, clustering coefficient

Node-level metrics:

- degree, degree centrality
- betweenness (bridges)
- closeness, eigenvector (optional if stable)

Community:

- modularity-based community detection (report top community sizes; interpret via entity inspection)

### 7.4 Narrative positivity vs evidence density (screening heuristic)

Compute per section:

- positivity cue rate (per 1k tokens)
- metric/evidence cue rate (per 1k tokens): numbers + units + target/baseline terms
- heuristic score: ratio of positivity to evidence markers

Use case:

- rank high-betweenness sections by heuristic score to create an audit shortlist.

### 7.5 Robustness and validation

Minimum defensibility checks:

1. Threshold sensitivity:
   - vary shared-entity threshold; compare top bridges/hubs stability.
2. Alternative extraction:
   - compare token-frequency proxies vs stricter entity extraction.
3. Triangulation:
   - compare graph hubs with ABSA aspect frequencies and dashboard insights.
4. Manual audit sampling:
   - read a sample of top-ranked bridge/risk sections and quote representative snippets in the paper.

---

## 8. Expected Results and How to Interpret Them

In ESG disclosure networks, plausible patterns include:

- a small set of hub communities corresponding to standard report templates,
- bridges connecting governance/compliance narratives with environmental/social commitments,
- pillar-dependent clustering (e.g., governance language clustering tightly; environmental metrics forming distinct modules),
- a subset of structurally influential sections with high positivity and low metric density (audit candidates).

Interpretation boundaries:

- a high “risk” heuristic score indicates a *candidate for review*, not confirmed misrepresentation;
- dense networks may indicate boilerplate dominance;
- community labels require qualitative inspection.

---

## 9. Discussion: Implications, Limitations, and Research Agenda

### 9.1 Practical implications

- Regulators and auditors can use SNA outputs to prioritize reading effort.
- Firms can benchmark disclosure structure against peers and identify over-reliance on generic narrative modules.
- Researchers can connect structure to theories of legitimacy, impression management, and disclosure strategy.

### 9.2 Methodological limitations

- OCR noise and bilingual tokenization introduce spurious connectivity.
- Entity proxies are not true entities without dedicated NER.
- Graph conclusions may be unstable without sensitivity analysis.
- Similarity-based graphs reduce transparency.

### 9.3 Future research directions

- Dynamic networks across years with formal change-point analysis.
- Multi-layer graphs combining aspects, entities, firms, and tone categories.
- Causal inference cautions: use graph signals for screening, not causal claims.
- Stronger evidence measures: link disclosures to external data (KPIs, PROPER ratings, enforcement events) when available.

---

## 10. Conclusion

SNA provides a natural complement to ABSA and sentiment-based ESG analytics by modeling disclosure as *structure*, not just isolated labels. For Indonesian ESG reports—often long, multilingual, and template-rich—section-level disclosure graphs can identify hubs, bridges, and discourse communities that matter for interpretability and audit prioritization. A defensible disclosure SNA study requires transparent text-to-network design choices, robustness checks, and careful interpretation boundaries. The blueprint in this review is implementation-ready for OCR-based ESG benchmark repositories, enabling reproducible network artifacts and thesis-ready reporting.

---

## Appendix A. Repository Alignment (Implementation Anchors)

If you are implementing this review’s blueprint in the current codebase, the relevant anchor points are:

- Streamlit SNA prototype and corpus scan: `social_network_analysis/app.py`
- Task framing and method roadmap: `social_network_analysis/task_data.py`
- SNA section pages: `social_network_analysis/pages/`
- OCR corpus: `data/thesis_dataset/*/ocr_result.json`
- Broader ESG pipeline documentation: `research_documentation.md`, `documentation_social_network_analysis.md`

---

## References (to be completed)

Add the final bibliography using your thesis/journal format (APA/IEEE/Chicago). At minimum, include canonical references for:

- SNA centrality foundations
- modularity/community detection
- community detection reviews
- text-to-network / semantic network methods
- ESG disclosure / legitimacy / greenwashing foundations

