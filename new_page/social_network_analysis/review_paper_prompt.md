https://scite.ai/assistant/indonesian-esg-reporting-sna-based-insight-QyjYwQ
https://app.litmaps.com/tag/837d90b2-7318-4863-ac19-f971a3ae8844

# Prompts for Generating Each Section of `review_paper.md`

Use the prompts below to (re)generate each section of the review paper. Each prompt is designed to produce content that matches the scope and style of `review_paper.md` and stays aligned with an Indonesian ESG disclosure-network context (OCR-based corpora, ABSA/ontology compatibility, and an audit-prioritization framing).

General guidance for all prompts:

- Write in an academic review-paper tone, concise but comprehensive.
- Avoid claiming empirical results unless explicitly instructed to produce “expected results” only.
- Treat SNA indicators as *screening* signals, not definitive greenwashing detectors.
- Keep the writing self-contained: define terms at first use.
- Keep placeholders where citations should go (e.g., `[CITE: centrality foundations]`).

---

## 0. Title + Metadata

**Prompt**

Write a title page section for a review paper on Social Network Analysis (SNA) for Indonesian ESG disclosures. Include:

- Title: “Social Network Analysis for Indonesian ESG Disclosures: A Review and an Evidence-Ready Research Blueprint”
- 1–2 sentence positioning statement (why this review matters now)
- Keywords list (8–12 items)

Constraints:

- No citations required here.
- Keep it compact and professional.

---

## 1. Abstract

**Prompt**

Write the Abstract for the review paper. Cover:

- The problem: Indonesian ESG reporting growth + audit difficulty + narrative risk
- Limits of sentiment/ABSA-only approaches (record-level, under-model relational structure)
- Why SNA is relevant (centrality, bridging, communities, structure)
- What this paper contributes (review + methodological guidance + implementation blueprint)
- Clear interpretation boundary: graph signals are screening heuristics

Constraints:

- 150–250 words.
- Do not claim new empirical findings.
- Include 3–5 inline citation placeholders like `[CITE: disclosure theory]`.

---

## 2. Introduction

**Prompt**

Write Section 1 “Introduction” for the review paper. Include:

- Indonesian ESG disclosure context (bilingual, long reports, template reuse, OCR realities)
- Why manual audit is hard and why traceability matters
- How NLP/ABSA helps, and where it falls short for relational structure
- Why SNA complements ABSA (structure, hubs, bridges, communities, longitudinal patterns)
- Outline of the paper structure in 4–6 sentences

Constraints:

- 700–1,000 words.
- Use subheadings only if needed.
- Add citation placeholders where appropriate.

---

## 3. Scope and Research Framing

### 3.1 What “social network” means here

**Prompt**

Write Section 2.1 explaining what “social network” means in ESG disclosure analysis. Clarify:

- Difference from actor-interaction networks
- Definition of “social-semantic disclosure networks”
- Typical node/edge choices (sections, entities, aspects, documents; co-occurrence, shared entities, similarity)
- Why terminology matters for validity and interpretation

Constraints:

- 350–600 words.
- Include 2–4 citation placeholders.

### 3.2 Intended use: interpretability and audit prioritization

**Prompt**

Write Section 2.2 explaining the intended use of disclosure SNA. Cover:

- Interpretability at scale: hubs, bridges, communities
- Audit prioritization use case (where to read first)
- Why not to overclaim causality or misrepresentation
- How this aligns with regulator/auditor workflows

Constraints:

- 350–600 words.
- Include 2–4 citation placeholders.

---

## 4. Foundations: SNA Concepts Relevant to Disclosure Networks

### 4.1 Network representation

**Prompt**

Write Section 3.1 describing network representation for disclosure networks:

- Graph definition \(G=(V,E)\)
- Weighted vs unweighted edges
- Node attributes and metadata (year, pillar, sector, tone, evidence markers)
- Multi-layer and bipartite representations

Constraints:

- 300–500 words.
- Include 2–3 citation placeholders.

### 4.2 Centrality

**Prompt**

Write Section 3.2 on centrality for disclosure networks. Explain:

- Degree, betweenness, closeness, eigenvector centrality
- What each can mean in disclosure networks (hubs vs bridges)
- Key pitfalls (construction dependence, threshold sensitivity)
- Reporting recommendations (don’t interpret as “influence” without caveats)

Constraints:

- 500–800 words.
- Include 4–6 citation placeholders, including one for centrality foundations.

### 4.3 Community detection

**Prompt**

Write Section 3.3 on community detection. Cover:

- Modularity intuition and what communities represent in disclosure networks
- Practical algorithms (modularity-based, greedy methods)
- Stability concerns and resolution limits
- How to interpret communities with qualitative inspection

Constraints:

- 450–700 words.
- Include 4–6 citation placeholders.

### 4.4 Macro-structure metrics

**Prompt**

Write Section 3.4 on global network structure metrics. Discuss:

- Density, connected components, clustering coefficient, assortativity
- How each metric can be interpreted for ESG disclosure structure
- Common failure modes (boilerplate inflation, OCR noise)

Constraints:

- 450–700 words.
- Include 3–5 citation placeholders.

---

## 5. Text-to-Network Transformation: Design Space and Pitfalls

**Prompt**

Write Section 4, structured with subheadings:

1. Node-type choice
2. Edge-definition choice
3. Weighting and thresholding
4. Validity threats and mitigation

For each, include:

- Options and trade-offs
- Specific to Indonesian ESG + OCR corpora (bilingual, template language)
- Concrete mitigation steps (stopwords, section segmentation, robustness checks)

Constraints:

- 1,000–1,500 words.
- Include 6–10 citation placeholders.
- Include a short bullet list of “minimum defensibility checks” at the end.

---

## 6. ESG Disclosure Analytics: Why Structure Matters

### 6.1 Beyond label counts

**Prompt**

Write Section 5.1 explaining why ABSA/sentiment alone is insufficient. Include:

- What ABSA provides
- What structural analysis adds (bundling, bridges, template communities)
- Examples of how structure changes interpretability

Constraints:

- 450–700 words.
- Include 3–5 citation placeholders.

### 6.2 Greenwashing and “credibility gaps”

**Prompt**

Write Section 5.2 discussing credibility gaps and narrative risk. Cover:

- Why positive narrative may diverge from evidence
- What “evidence markers” can mean in text (numbers, units, targets, baselines)
- How networks help prioritize influential sections
- Strong boundary statement: screening heuristic, manual verification required

Constraints:

- 450–750 words.
- Include 4–6 citation placeholders.

---

## 7. Review of Method Families for ESG Disclosure Networks

**Prompt**

Write Section 6 as a method-family review with subheadings:

- Co-occurrence / semantic networks
- Topic-model-based networks
- ABSA/ontology-driven networks
- Embedding similarity graphs
- Dynamic disclosure networks

For each family: escribing the approach, listing strengths/weaknesses and suitability for Indonesian ESG OCR corpora


- 1 paragraph describing the approach
- 1 paragraph listing strengths/weaknesses
- 1–2 notes on suitability for Indonesian ESG OCR corpora

Constraints:

- 1,200–1,800 words.
- Include 8–12 citation placeholders.

---

## 8. Evidence-Ready Blueprint (Implementation-Oriented)

**Prompt**

Write Section 7 as an implementation-ready blueprint aligned to an OCR→ESG pipeline repository. Include:

- Data assumptions (`ocr_result.json` with `pages[*].markdown`)
- Section segmentation approach and rationale
- Baseline graph design: section-level co-entity network
- Metrics to compute and artifacts to export (summary JSON, nodes/edges CSV, top bridges/hubs, community sizes)
- Narrative positivity vs evidence density heuristic and how to report it
- Robustness and validation checklist (threshold sensitivity, alternative extraction, triangulation with ABSA, manual sampling)

Constraints:

- 1,000–1,400 words.
- Include a numbered checklist at the end.
- Keep it actionable and reproducible.

---

## 9. Expected Results and Interpretation

**Prompt**

Write Section 8 “Expected Results and How to Interpret Them”. Include:

- Plausible network patterns (hubs, bridge sections, communities, pillar clustering)
- How to interpret dense graphs vs fragmented graphs
- Interpretation boundaries and cautions (no causal claims; heuristic not classifier)
- A short paragraph on what would count as “useful” vs “artifact-driven” results

Constraints:

- 450–700 words.
- No new data; only expected patterns.
- Include 2–4 citation placeholders.

---

## 10. Discussion: Implications, Limitations, Research Agenda

**Prompt**

Write Section 9 with three subheadings:

1. Practical implications (regulators/auditors/firms/researchers)
2. Methodological limitations (OCR noise, bilingual issues, entity proxies, threshold sensitivity)
3. Future research directions (dynamic graphs, multi-layer networks, stronger evidence linkage, external validation)

Constraints:

- 900–1,300 words.
- Include 6–10 citation placeholders.
- End with a short bullet list of “recommended next experiments”.

---

## 11. Conclusion

**Prompt**

Write Section 10 “Conclusion”. Summarize:

- Why SNA complements ABSA for Indonesian ESG disclosures
- What a defensible study requires (transparent construction + robustness + boundaries)
- What the blueprint enables (reproducible artifacts + thesis-ready reporting)

Constraints:

- 250–400 words.
- No citations required.

---

## 12. Appendix A: Repository Alignment (Implementation Anchors)

**Prompt**

Write Appendix A listing concrete repository anchor points (as bullet points) that would support implementing the blueprint in code. Include:

- SNA Streamlit prototype path
- Task framing/data definitions path
- OCR corpus path
- Related pipeline documentation paths

Constraints:

- 120–200 words.
- Keep it as a practical pointer list.

---

## 13. References (Placeholder)

**Prompt**

Write a “References” section placeholder for the paper:

- Briefly state that references will be inserted in the final draft.
- Provide a categorized list of what must be cited (centrality, community detection, semantic/text networks, ESG disclosure theory, greenwashing/legitimacy theory, Indonesian reporting context).

Constraints:

- 120–250 words.
- Do not fabricate full citations.

