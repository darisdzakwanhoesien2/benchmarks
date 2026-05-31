https://scite.ai/assistant/topic-modelling-for-bilingual-ocr-d-esg-reports-a-structured-rev-9bjN52
https://app.litmaps.com/tag/3a874b1b-15c8-46c4-b878-7b8002ea7aaf
t
# Prompts for Generating Each Section of `review_paper.md`

Date: 2026-05-30

Use these prompts to (re)generate each section of `review_paper.md` consistently. Each prompt is designed to be pasted into an LLM as-is.

**Global instructions (apply to every section):**

- Write in an academic “review paper” tone, but implementation-oriented.
- Domain: bilingual (Indonesian–English), OCR-derived Indonesian ESG sustainability reports.
- Emphasize reproducibility, unit-of-analysis design, evaluation beyond coherence, and alignment to supervised taxonomies (ABSA aspects/pillars).
- Avoid invented citations. If you mention literature, describe it by category unless you have verified references.
- Prefer structured subsections, bullet lists where appropriate, and clear claims + limitations.

---

## Prompt — Abstract

- 150–220 words.

Write the **Abstract** for a review paper titled:

“Topic Modelling for Bilingual, OCR-Derived Indonesian ESG Sustainability Reports: A Structured Review and Implementation-Oriented Synthesis”.

Requirements:


- State the problem setting (OCR noise, long documents, bilingual mixing).
- State why topic modelling is hard in this setting and why it matters for ESG.
- Summarize what the review contributes (method families, preprocessing, evaluation, integration with ABSA/taxonomy, implementation roadmap).
- End with 5–10 keywords on a separate line, formatted as: `**Keywords:** ...`

---

## Prompt — 1. Introduction

Write Section **1. Introduction** for the same review paper.

Must include:

- A clear motivation: ESG sustainability reports are important and large-scale reading is infeasible.
- Why topic modelling is attractive but commonly misused in ESG contexts.
- A statement of the review’s unique focus: Indonesian sustainability-report setting + bilingual OCR + implementation-first, evaluation-first design.
- Two subsections:
  - **1.1 Scope and objectives of this review**: list 4 objectives as numbered items.
  - **1.2 Target corpus characteristics (Indonesian ESG disclosures)**: bullet list of corpus properties (OCR noise, bilingual mix, long documents, boilerplate, heterogeneous structure) and why they matter.

Constraints:

- Keep it grounded; do not claim “state of the art” without evidence.
- 600–900 words total for Section 1.

---

## Prompt — 2. Background: What Topic Modelling Is (and Isn’t)

Write Section **2. Background: What Topic Modelling Is (and Isn’t)**.

Must include:

- A short definition of topic modelling and what a “topic” means in both bag-of-words and embedding-based paradigms.
- Subsection **2.1 Why “topics” can be misleading in ESG disclosure corpora**:
  - Provide 4–6 bullet points of common “junk topic” sources (boilerplate, section headings, OCR artifacts, proper nouns).
  - Explain why external validation is needed (pillars/aspects).
- Subsection **2.2 Unit of analysis: the defining choice**:
  - List possible units (report/section/page/chunk/statement).
  - Explain trade-offs for each unit in ESG reports (topic granularity, noise sensitivity, interpretability).
  - End with a recommendation paragraph that motivates using both statement-level and OCR-chunk corpora.

Length: 700–1,000 words.

---

## Prompt — 3. Families of Topic Modelling Methods

Write Section **3. Families of Topic Modelling Methods** with the following subsections:

- **3.1 Probabilistic topic models (LDA-style)**
- **3.2 Matrix factorization (NMF on TF-IDF)**
- **3.3 Embedding-based topic modelling (clustering + topic representation)**
- **3.4 Neural topic models and hybrids**

For each subsection, include:

- `Core idea:` 1–2 sentences.
- `Strengths:` 3–5 bullets tailored to bilingual OCR ESG corpora.
- `Weaknesses:` 3–5 bullets tailored to bilingual OCR ESG corpora.
- `When to use:` 2–4 sentences that position the method in an evaluation pipeline (baselines first, then more complex).

Constraints:

- Avoid naming specific papers unless you can cite them; speak in method families.
- Use ESG-specific framing (template language, drift, sector comparison, ABSA alignment).

Length: 1,100–1,600 words.

---

## Prompt — 4. Preprocessing for OCR and Bilingual Sustainability Reports

Write Section **4. Preprocessing for OCR and Bilingual Sustainability Reports**.

Subsections and requirements:

### 4.1 OCR-specific cleaning
- Provide a numbered list of 4–7 concrete cleaning steps.
- Explain why each step matters for topic modelling.

### 4.2 Boilerplate and template language handling
- Provide 3–6 strategies (deduplication, stoplists, downweighting, chunking).
- Include a short paragraph explaining how boilerplate distorts topics and evaluation.

### 4.3 Bilingual tokenization and normalization
- Provide practical guidance on stopwords, light normalization, and multilingual embeddings.
- Discuss the risk of “language topics” and mitigations.

### 4.4 Defining canonical metadata
- Provide a table-like bullet list of recommended metadata fields (`company`, `year`, `sector`, `source_type`, optional labels).
- Explain how to version corpora (manifest + signature) for reproducibility.

Length: 900–1,300 words.

---

## Prompt — 5. Evaluation: Beyond Coherence

Write Section **5. Evaluation: Beyond Coherence**.

Subsections and requirements:

### 5.1 Intrinsic evaluation
- Explain coherence/diversity/overlap and why they can fail in ESG OCR corpora.

### 5.2 Stability and robustness
- Provide a reproducible stability protocol: seeds, resampling, topic overlap measures, reporting format.

### 5.3 Extrinsic evaluation using supervised labels (ABSA alignment)
- Explain how to compute topic-to-pillar/aspect distributions and how to interpret them.
- Include at least one simple quantitative alignment metric idea (e.g., entropy/concentration) and caveats.

### 5.4 Human interpretability protocol
- Provide a step-by-step protocol for human labeling of topics (keywords + exemplars).
- Include a short section on inter-annotator disagreement and what it implies.

Length: 1,000–1,400 words.

---

## Prompt — 6. Topic Modelling in ESG Disclosure Analysis: What Works in Practice

Write Section **6. Topic Modelling in ESG Disclosure Analysis: What Works in Practice**.

Must include:

- **6.1 Typical research uses**: bullet list with brief expansions (comparisons, concentration, evolution, auditing/triage).
- **6.2 Common failure modes**: bullet list + 1 paragraph tying failure modes to earlier sections.
- **6.3 Recommended best practices (for Indonesian ESG OCR corpora)**:
  - Provide a numbered checklist of 6–10 best practices.
  - Each best practice should reference either preprocessing, unit-of-analysis, evaluation, or artifact export.

Length: 700–1,000 words.

---

## Prompt — 7. Implementation-Oriented Synthesis (Repository-Ready)

Write Section **7. Implementation-Oriented Synthesis (Repository-Ready)** that translates the review into a concrete pipeline design.

Must include:

### 7.1 Recommended corpora
- Describe two corpora: statement-level (ABSA-extracted) and OCR-chunk.
- For each corpus: advantages, risks, and recommended unit size.

### 7.2 Minimal artifact standard (what to export)
- Specify an export folder (e.g., `results/topic_modelling/`).
- List exact artifact filenames and what columns/fields they contain.

### 7.3 Model comparison design
- Recommend the baseline set (LDA, NMF, embedding clustering).
- Explain how to compare across corpora and how to report results.

### 7.4 Thesis-ready result formats
- Provide a concise list of tables/figures to produce (model comparison table, topic panels, temporal charts, sector charts).

Constraints:

- Write so that an engineer can implement it directly.
- Prefer explicit filenames and structured outputs.

Length: 900–1,200 words.

---

## Prompt — 8. Research Gaps and Future Directions

Write Section **8. Research Gaps and Future Directions**.

Requirements:

- Provide 5–8 clearly numbered gaps/future directions.
- Each item should include:
  - the gap,
  - why it matters in Indonesian ESG OCR topic modelling,
  - what a concrete next study/experiment would do.

Length: 500–800 words.

---

## Prompt — 9. Conclusion

Write Section **9. Conclusion**.

Requirements:

- 250–400 words.
- Restate the main thesis: topic modelling is useful only if reproducible and evaluated beyond coherence.
- Summarize the recommended path: unit-of-analysis, baselines + embedding model, stability + alignment evaluation, standardized artifact export.
- End with one sentence describing the expected impact on ESG disclosure analysis (interpretability, auditing, temporal/sector insights).

---

## Prompt — Acknowledgements

Write a short **Acknowledgements** section (60–120 words).

Requirements:

- State that the paper is implementation-driven and focused on reproducibility and artifact export for benchmarking/thesis workflows.
- Do not name specific people unless explicitly provided.

---

## Prompt — References

Write a **References** section as a structured placeholder (not a fake bibliography).

Requirements:

- Explain that references must be populated via a proper citation workflow (Zotero/BibTeX/manual) and must match in-text claims.
- Provide a categorized checklist of what to include (LDA foundations, coherence metrics, NMF text factorization, embedding-based topic modelling, multilingual topic modelling, ESG text mining, OCR noise mitigation).

