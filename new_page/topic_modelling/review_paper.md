# Topic Modelling for Bilingual, OCR-Derived Indonesian ESG Sustainability Reports: A Structured Review and Implementation-Oriented Synthesis

Date: 2026-05-30

## Abstract

Topic modelling is widely used to discover latent themes in large text corpora, but sustainability reporting presents distinctive challenges: documents are long, templated, and often noisy due to OCR; disclosure language is frequently bilingual (Indonesian–English); and real-world usefulness depends on whether topics can be aligned to decision-relevant taxonomies (e.g., ESG pillars, aspect labels) rather than evaluated only by intrinsic metrics. This review synthesizes topic-modelling approaches through the lens of Indonesian sustainability reports, emphasizing design choices that matter in practice: unit of analysis, preprocessing for OCR noise, bilingual representations, evaluation beyond coherence, and integration with supervised labels such as aspect-based sentiment analysis (ABSA). We conclude with an implementation-oriented roadmap grounded in an existing benchmark repository: how to build reproducible corpora from OCR and statement-level extractions, compare probabilistic and embedding-based topic models, and export standardized artifacts for dashboards and thesis reporting.

**Keywords:** topic modelling, sustainability reports, ESG, Indonesian, OCR, bilingual NLP, LDA, NMF, BERTopic, evaluation, interpretability

---

## 1. Introduction

Sustainability reports are a central disclosure channel through which firms communicate environmental, social, and governance (ESG) commitments, performance, and risk management. At scale, these reports form a corpus suitable for computational analysis; however, manual reading is infeasible due to length and volume. Topic modelling provides a natural tool to summarize and characterize thematic structure across companies, years, and sectors.

Despite its popularity, topic modelling in ESG disclosure analysis is often reported as a qualitative artifact (e.g., a word list or visualization) without a clear methodology for (i) handling OCR noise and bilingual text, (ii) deciding the correct unit of analysis, (iii) validating topics against external labels, or (iv) making results reproducible and reusable for downstream analytics.

This review addresses those gaps by focusing on the Indonesian sustainability-report setting and by organizing the literature around actionable design decisions for building an end-to-end research track.

### 1.1 Scope and objectives of this review

This review aims to:

1. Summarize major topic modelling families (probabilistic, factorization, embedding-based, hybrid).
2. Explain why sustainability-report corpora require specialized preprocessing and modelling choices.
3. Propose evaluation practices that go beyond intrinsic coherence to include stability and alignment to supervised taxonomies (e.g., ABSA aspects/pillars).
4. Provide an implementation-oriented synthesis suitable for a benchmark repository where OCR and ABSA artifacts already exist.

### 1.2 Target corpus characteristics (Indonesian ESG disclosures)

Indonesian sustainability-report corpora commonly exhibit:

- **OCR-derived noise** (broken tokens, page artifacts, duplicated headers/footers, table extraction remnants).
- **Bilingual mix** (Indonesian and English within the same document and sometimes within the same paragraph).
- **Long-document regime** (reports can be tens of thousands of tokens).
- **Template language and boilerplate** (regulatory and corporate templates repeat across years).
- **Heterogeneous structure** (different report layouts, section naming, and disclosure emphasis).

These properties increase the importance of data profiling, unit-of-analysis design, and robust evaluation.

---

## 2. Background: What Topic Modelling Is (and Isn’t)

Topic modelling refers to a family of methods that infer latent thematic structure from text. A “topic” is typically represented as:

- A distribution over words/terms (bag-of-words models), and/or
- A cluster of semantically similar documents/sentences (embedding-based models), plus a representation (keywords/exemplars).

### 2.1 Why “topics” can be misleading in ESG disclosure corpora

In sustainability-report corpora, naive topic models can produce topics dominated by:

- Boilerplate and generic governance language,
- Repeated section headings,
- OCR artifacts and formatting tokens,
- Company-specific proper nouns.

Therefore, topic modelling requires careful preprocessing and, importantly, external validation: whether topics correspond to meaningful constructs (pillars/aspects) and whether they help explain differences across time and organizations.

### 2.2 Unit of analysis: the defining choice

The “document” in topic modelling may be:

- An entire report,
- A section or chapter,
- A page (OCR page),
- A paragraph/chunk,
- A sentence/statement (e.g., extracted by an ABSA pipeline).

This choice strongly affects interpretability, topic granularity, and evaluation. ESG reports are long and multi-theme; treating each report as a single unit often yields overly broad topics. Conversely, statement-level units may lose global context but enable cleaner topic-to-label alignment.

---

## 3. Families of Topic Modelling Methods

This section reviews the method families most relevant to bilingual, OCR-derived ESG corpora.

### 3.1 Probabilistic topic models (LDA-style)

**Core idea:** each document is a mixture of topics; each topic is a distribution over words.

**Strengths:**

- Interpretable topic-word distributions.
- Document-topic mixtures support downstream analysis (time/sector comparisons).
- Mature tooling and clear baselines.

**Weaknesses in ESG/OCR/bilingual settings:**

- Bag-of-words assumptions are sensitive to noisy tokens and boilerplate.
- Multilingual mixing can fragment topics or create language-separated topics (English vs Indonesian) rather than semantic themes.
- Topic count selection is non-trivial and often tuned without robust stability checks.

**When to use:** as a baseline and when interpretability + reproducibility matter more than semantic nuance.

### 3.2 Matrix factorization (NMF on TF-IDF)

**Core idea:** factorize a document-term matrix into topic-term and document-topic weights.

**Strengths:**

- Often yields sharper topics than LDA on TF-IDF.
- Works well as a strong baseline with good preprocessing.

**Weaknesses:**

- Still depends on bag-of-words; shares vulnerabilities to OCR noise and bilingual token fragmentation.

**When to use:** as a baseline complementary to LDA; useful in ablation studies.

### 3.3 Embedding-based topic modelling (clustering + topic representation)

**Core idea:** embed documents/sentences using contextual models (ideally multilingual), cluster embeddings, then build a topic representation (keywords/exemplars).

**Strengths:**

- Better semantic grouping for bilingual corpora than bag-of-words approaches.
- Can represent topics with exemplars (representative statements), aiding interpretability.

**Weaknesses:**

- Heavier dependencies and compute cost (embedding models).
- Sensitive to clustering choices and hyperparameters.
- Reproducibility can degrade if embeddings/clustering are not versioned and seeded.

**When to use:** when bilingual semantics and nuanced thematic clustering are important and infrastructure supports embedding computation.

### 3.4 Neural topic models and hybrids

This family includes neural variational topic models and hybrids combining:

- Probabilistic topic distributions with embeddings,
- Constraint-based topic shaping (seed words, taxonomies),
- Semi-supervised alignment to labels (aspects/pillars).

**Strengths:**

- Potentially better semantic coherence and label-alignment.

**Weaknesses:**

- Complexity, sensitivity, and weaker transparency.

**When to use:** after establishing strong baselines, when additional complexity is justified by measurable gains.

---

## 4. Preprocessing for OCR and Bilingual Sustainability Reports

### 4.1 OCR-specific cleaning

Recommended steps:

1. Remove page artifacts: page numbers, repeated headers/footers, line breaks that split words.
2. Normalize whitespace and punctuation.
3. Remove or normalize tables and list artifacts if they dominate token space.
4. Optional de-duplication of repeated boilerplate segments across documents/years.

**Why it matters:** OCR artifacts introduce high-frequency noise that topic models interpret as thematic structure.

### 4.2 Boilerplate and template language handling

Template language is pervasive in corporate reporting. Practical strategies:

- Remove standard disclaimers or repeated section titles.
- Downweight boilerplate via TF-IDF, de-duplication, or stoplists.
- Model at smaller units (sections/statements) rather than full reports to reduce multi-theme mixing.

### 4.3 Bilingual tokenization and normalization

For Indonesian–English mixed text:

- Use a combined stopword list (Indonesian + English) plus domain stopwords (e.g., “sustainability”, “laporan”, “company”, “perseroan”).
- Consider light stemming/lemmatization, but avoid aggressive stemming that harms interpretability.
- Prefer multilingual embeddings for semantic topic modelling when possible.

### 4.4 Defining canonical metadata

To support analysis and evaluation, each unit should carry:

- `company` (or proxy identifier),
- `year`,
- `sector` (true sector if available; otherwise an explicit proxy),
- `source_type` (OCR vs ABSA extraction),
- optional `pillar` (E/S/G), `aspect`, `tone`, `sentiment` if labels exist.

Reproducibility requires that corpus-building decisions be versioned (manifest + signature).

---

## 5. Evaluation: Beyond Coherence

### 5.1 Intrinsic evaluation

Common intrinsic metrics:

- Topic coherence (multiple variants),
- Topic diversity (redundancy checks),
- Topic distinctiveness / overlap.

**Limitations:** Intrinsic metrics alone can reward boilerplate separation or language separation rather than meaningful ESG themes.

### 5.2 Stability and robustness

Stability is critical for thesis-level claims:

- Re-run with different random seeds,
- Re-sample documents,
- Measure topic overlap consistency across runs,
- Check whether “top topics” remain consistent across variations.

### 5.3 Extrinsic evaluation using supervised labels (ABSA alignment)

If statement-level extractions include labels (pillar/aspect/tone/sentiment), topic model evaluation should include:

- Topic → pillar concentration (does a topic correspond to E/S/G?),
- Topic → aspect concentration (does it map to interpretable aspect clusters?),
- Topic → sentiment/tone profile (does it explain patterns in disclosure tone?).

This shifts topic modelling from a purely exploratory tool to a validated interpretability layer.

### 5.4 Human interpretability protocol

A minimal protocol:

- For each topic: top keywords + top exemplars (statements or chunks).
- Human assigns a short topic label and mapping to (pillar/aspect) where applicable.
- Record disagreements and unclear topics; use them as evidence of model limitations.

---

## 6. Topic Modelling in ESG Disclosure Analysis: What Works in Practice

### 6.1 Typical research uses

Topic modelling is most useful when tied to:

- **Comparative analysis:** sector/company differences, cross-year shifts.
- **Disclosure concentration:** which themes dominate vs which are underrepresented.
- **Narrative evolution:** emergence and drift of ESG language.
- **Auditing & triage:** identifying documents or sections that exhibit suspicious patterns (e.g., high positivity with low metric density).

### 6.2 Common failure modes

- Topics represent formatting or boilerplate rather than ESG themes.
- Topics separate by language rather than meaning (English vs Indonesian topics).
- Topic number selection is arbitrary and not robust.
- Findings are not reproducible because corpora and model artifacts are not persisted.

### 6.3 Recommended best practices (for Indonesian ESG OCR corpora)

1. Start with statement-level corpora (if available) for cleaner units and better label alignment.
2. Use probabilistic/factorization baselines to establish interpretability and reproducibility.
3. Add embedding-based topic models for bilingual semantic robustness.
4. Evaluate with stability + alignment, not only coherence.
5. Export standardized artifacts for dashboards and thesis reporting.

---

## 7. Implementation-Oriented Synthesis (Repository-Ready)

This section translates the review into an actionable pipeline design for a benchmark repository where OCR and ABSA artifacts already exist.

### 7.1 Recommended corpora

**Corpus A (statement-level):** extracted ESG statements with labels.

- Source: a JSON structure containing records like:
  - `text`, `aspect`, `esg` (pillar), `tone`, `sentiment`, etc.
- Advantages: short units, label alignment available.

**Corpus B (OCR-chunk):** chunked OCR pages or sections.

- Source: OCR JSON containing page markdown.
- Chunking strategy: per page, sliding window, or section heuristics.
- Advantages: full coverage; supports document-level temporal analysis.

### 7.2 Minimal artifact standard (what to export)

Export to a stable folder (e.g., `results/topic_modelling/`):

- `corpus_manifest.json`:
  - corpus name, build time, filtering rules, signature hash
- `units.parquet` or `units.csv`:
  - `unit_id`, `text`, `company`, `year`, `sector`, `source`, optional labels
- For each model:
  - `topics_<model>.csv` (topic_id, keywords, label)
  - `unit_topics_<model>.parquet` (unit_id × topic weights or hard assignments)
  - `metrics_<model>.json` (coherence/diversity/stability summaries)
- Alignment exports (if labels exist):
  - `topic_alignment_pillar_<model>.csv`
  - `topic_alignment_aspect_<model>.csv`
  - `topic_sentiment_tone_profiles_<model>.csv`

### 7.3 Model comparison design

Recommended baseline set:

1. LDA (bag-of-words)
2. NMF (TF-IDF)
3. Embedding + clustering (BERTopic-style)

Run each model on:

- statement-level corpus, then
- OCR-chunk corpus

Report:

- intrinsic metrics, stability, and label alignment.

### 7.4 Thesis-ready result formats

Include:

- A table comparing models (coherence, diversity, stability, alignment score).
- Topic interpretability panels: keywords + exemplars + label mappings.
- Temporal charts: topic prevalence by year (with imbalance caveats).
- Sector comparisons: topic distribution differences with caution around proxies.

---

## 8. Research Gaps and Future Directions

1. **Validated multilingual topic modelling for OCR corpora:** robust, reproducible best practices are under-specified in many ESG studies.
2. **External validity via label alignment:** topic modelling is often evaluated only intrinsically; ESG corpora frequently have usable taxonomies (pillars/aspects) that should be exploited.
3. **Temporal inference with imbalance control:** reporting trends are frequently asserted without careful handling of year/sector coverage imbalance.
4. **Greenwashing-oriented topic diagnostics:** combining topic prevalence with “evidence density” proxies (metrics vs claims) is a promising direction, but must be validated with human audit sets.
5. **Standardized artifact export and reuse:** many studies cannot be replicated because corpora and model outputs are not versioned and shared.

---

## 9. Conclusion

Topic modelling can materially improve sustainability-report analysis when treated as a reproducible, evaluated component—especially in bilingual, OCR-derived Indonesian ESG corpora. The most reliable path is to (i) define robust units of analysis, (ii) implement both probabilistic baselines and embedding-based models, (iii) evaluate with stability and label alignment (not only coherence), and (iv) export standardized artifacts that connect topic modelling to downstream ABSA-based interpretation and thesis reporting.

---

## Acknowledgements

This review paper is designed to support an implementation-driven benchmark workflow. It intentionally emphasizes reproducibility, artifact export, and alignment to supervised ESG taxonomies.

---

## References

This section is intentionally left as a structured placeholder because the current environment cannot retrieve peer-reviewed full-text excerpts via the configured literature tool (monthly limit reached). Populate this section via your citation workflow (Zotero/BibTeX/manual) and ensure every cited claim in Sections 3–5 is properly referenced.

Suggested reference categories to include:

1. Foundational topic modelling (LDA and variants).
2. Topic coherence and evaluation metrics.
3. NMF for topic modelling and text factorization.
4. Embedding-based topic modelling and BERTopic-style methods.
5. Multilingual NLP and topic modelling.
6. ESG/sustainability text mining applications.
7. OCR noise impacts on NLP and mitigation strategies.

