# A Review of Summarization Methods and Evaluation for Indonesian ESG Disclosures: Toward ABSA-Aware, Evidence-Grounded Summaries

Date: 2026-05-30

## Abstract
Automatic text summarization has evolved from heuristic extractive approaches to large-scale pretrained sequence-to-sequence models capable of fluent abstractive generation. Despite these advances, applying summarization to Environmental, Social, and Governance (ESG) disclosures—especially Indonesian sustainability reports processed via OCR—introduces distinct constraints: (i) traceability to evidence, (ii) preservation of structured ESG signals (aspects, pillars, tone/sentiment), (iii) robustness to OCR and table-extraction noise, and (iv) strong faithfulness guarantees to mitigate hallucinated claims. This review synthesizes classical and modern summarization paradigms and emphasizes evaluation practices, with particular focus on factual consistency. We propose a practical framing for **ABSA-aware, evidence-grounded summarization**, where summaries are generated from and audited against structured ABSA records and provenance pointers to source pages. We conclude with a research agenda for integrating summarization into an executable ESG document intelligence benchmark, highlighting open challenges in multilingual/domain adaptation, reference-free evaluation, and end-to-end reliability.

**Keywords:** summarization, extractive, abstractive, factual consistency, faithfulness, ESG, sustainability reports, Indonesian, OCR, ABSA

---

## 1. Introduction
Summarization aims to produce concise representations of longer texts while preserving salient information. In operational settings—policy, finance, compliance, and sustainability—summaries must do more than compress content: they must be *accurate*, *auditable*, and *useful* for decisions. ESG disclosures are a canonical example. Sustainability reports mix narrative claims, KPI tables, forward-looking statements, and boilerplate legal language. Summaries that invent values, misattribute actions, or omit key pillars can harm stakeholders and degrade trust.

Most summarization research is developed and evaluated on news-style corpora with short reference summaries and overlap-based automatic metrics (e.g., ROUGE). ESG summarization differs in three core ways:
1. **Evidence traceability:** decision users need “why” and “where” (page/section provenance), not just “what.”
2. **Structured signal preservation:** ESG reading is often performed through analytic frames (E/S/G pillars, topics/aspects, positive/negative tone, commitments and targets).
3. **Faithfulness under noise:** OCR and table-to-text conversion can distort inputs; abstractive models can “smooth” missing facts into fluent but unsupported statements.

This paper reviews summarization approaches and evaluation methods, then narrows to a domain framing for Indonesian ESG disclosures in an OCR → extraction → ABSA pipeline.

---

## 2. Background: Summarization Task Definitions

### 2.1 Extractive vs. Abstractive Summarization
- **Extractive summarization** selects spans (typically sentences) from the source. It is often more auditable and can be more faithful by construction, but may be redundant and less coherent.
- **Abstractive summarization** generates new text, potentially paraphrasing and synthesizing information across the source. It can improve readability and compression but increases risk of hallucination and factual errors.

### 2.2 Single-Document vs. Multi-Document Summarization
- **Single-document summarization** (most ESG use-cases): summarize a report or a section.
- **Multi-document summarization**: synthesize across companies, sectors, or years; useful for comparative ESG analysis.

### 2.3 Query-Focused and Structured Summarization
Many practical systems require:
- **Query-focused summaries** (e.g., “climate risk management,” “occupational safety,” “anti-corruption”).
- **Structured summaries** (e.g., per ESG pillar; per risk category; per material topic).

---

## 3. A Taxonomy of Summarization Methods

### 3.1 Heuristic Extractive Baselines
Baselines remain essential as a reliability floor and for debugging.

**Lead baseline** selects the first *k* sentences. It is strong for news where important information often appears early, but can be weak for long corporate reports where introductions contain generic language.

**Frequency-based selection** scores sentences using term frequencies. It is simple and fast but vulnerable to repetition, boilerplate dominance, and OCR tokenization noise.

### 3.2 Graph-Based Extractive Ranking (TextRank Family)
TextRank is a classic unsupervised extractive approach: sentences are nodes, similarities form edges, and an iterative ranking (PageRank-like) selects salient sentences (Mihalcea & Tarau, 2004).

**Strengths:** no training data required; interpretable; competitive baseline.  
**Weaknesses:** similarity function sensitivity; redundancy; limited discourse modeling.

### 3.3 Classical Supervised Summarization
Before large pretrained transformers, supervised summarization commonly relied on:
- sentence classification/ranking (extractive)
- encoder–decoder models trained on parallel document–summary datasets (abstractive)

These approaches showed that data quality, domain match, and evaluation choice strongly influence observed performance.

### 3.4 Neural Abstractive Summarization with Pretraining
Modern summarization frequently uses pretrained seq2seq transformer models fine-tuned for summarization:
- **Pointer-generator** style approaches improved copying and reduced OOV issues by mixing generation and copying.
- **Denoising pretraining** (e.g., BART) showed strong transfer across generation tasks.
- **Summarization-aligned pretraining** (e.g., PEGASUS) optimized objectives related to sentence “gap” prediction.

Pretraining improves fluency and salience modeling but does not eliminate hallucination; domain adaptation and factuality controls remain necessary for ESG.

### 3.5 Long-Document Summarization
Sustainability reports can exceed typical transformer context windows. Long-document summarization methods include:
- hierarchical summarization (summarize sections then aggregate)
- retrieval-augmented summarization (select evidence segments then summarize)
- chunking with cross-chunk planning and deduplication

For ESG, hierarchical+retrieval approaches naturally align with evidence traceability.

### 3.6 Constrained / Controlled Summarization
To reduce hallucination and improve consistency, systems can:
- generate from a structured content plan (aspects/pillars)
- enforce citation-style evidence links (span/page IDs)
- restrict to extractive evidence paraphrases unless support is found
- validate claims post-hoc via entailment/QA consistency checks

This theme is central for ESG settings and motivates ABSA-aware summarization.

---

## 4. Datasets and Domain Considerations

### 4.1 Canonical Summarization Datasets (and Why ESG Differs)
Summarization benchmarks are commonly news-centric (e.g., CNN/DailyMail; XSum) with short summaries and strong lead bias. ESG disclosures differ:
- narrative structure: long sections, repeated boilerplate, and mixed modalities (tables, figures)
- factual density: many numeric targets, scope definitions, and compliance statements
- evidence needs: a summary must remain auditable to original pages and tables

### 4.2 Multilingual and Low-Resource Constraints (Indonesian)
Indonesian summarization adds challenges:
- fewer high-quality parallel document–summary datasets compared to English
- domain vocabulary (regulatory terms, sector jargon, Indonesian/English mixing)
- named entity transliteration and OCR character noise

Multilingual pretraining (e.g., mBART-style) improves transfer, but evaluation and domain grounding remain hard.

### 4.3 OCR and Table-to-Text Noise
OCR pipelines introduce:
- token fragmentation (“emisi” → “emi si”)
- incorrect numerals and units
- table cell reordering
- page header/footer contamination

Summarization must therefore include robustness measures (cleaning, confidence scoring, or evidence retrieval constrained to high-confidence spans).

---

## 5. Evaluation of Summarization

### 5.1 Overlap-Based Metrics (ROUGE)
ROUGE (Lin, 2004) remains widely used for automatic evaluation, especially ROUGE-1/2/L. Its benefits are simplicity and comparability, but limitations include:
- dependence on reference summaries (often unavailable for ESG)
- weak sensitivity to factual errors (a fluent but wrong summary can still score well)
- brittleness under paraphrase and multilingual variation

ROUGE is useful as a baseline but insufficient as the primary metric for ESG.

### 5.2 Semantic Similarity Metrics
Semantic similarity metrics (embedding-based or learned) aim to measure meaning similarity beyond surface overlap. They can better handle paraphrases and multilingual variation, but can still miss factual contradictions—particularly numeric, temporal, and attribution errors that are common in ESG reporting.

### 5.3 Faithfulness and Factual Consistency Evaluation
Factual consistency is central for abstractive summarization. Common approaches include:
- **Entailment/NLI-based checks:** whether the source entails each summary sentence.
- **QA-based checks:** generate questions from the summary and answer them from the source; compare answers for consistency.
- **Classifier-based consistency models:** train detectors using synthetic perturbations or labeled inconsistency datasets.

Empirical work has shown that neural abstractive summarizers can generate unsupported content (“hallucinations”), motivating explicit evaluation and mitigation.

### 5.4 Human Evaluation
Human evaluation remains necessary when:
- references do not exist,
- the task is domain-specific,
- factuality and utility matter most.

Recommended axes for ESG:
- **faithfulness:** supported / unsupported / contradicted
- **coverage:** capture key pillars and material topics
- **usefulness:** enables action or writing without re-reading the full document
- **auditability:** each claim traceable to a page/table/quote

### 5.5 Evaluation Under a Benchmark Mindset
For repo-integrated research, evaluation should be reproducible:
- fixed sampling protocols and (if applicable) splits
- stored outputs with configuration metadata (model/prompt/version)
- automated comparison tables and dashboards across strategies

---

## 6. Faithfulness: Sources of Errors and Mitigation Strategies

### 6.1 Common Error Modes in Abstractive Summaries
High-impact error types for ESG include:
- **entity errors:** wrong company, location, or initiative attribution
- **numeric errors:** incorrect target values, units, or years
- **scope errors:** conflating scope 1/2/3 emissions, or mixing initiatives across pillars
- **causal overreach:** asserting outcomes not supported by the report
- **temporal errors:** converting planned initiatives into completed claims

### 6.2 Practical Mitigations
Mitigations can be layered:
1. **Evidence-first generation:** retrieve evidence spans, then summarize from them.
2. **Structured content planning:** require pillar/aspect structure.
3. **Citation requirements:** every claim must cite a span/page ID.
4. **Post-hoc validation:** NLI/QA checks and numeric consistency checks.
5. **Human-in-the-loop audits:** sample-based review with an error taxonomy.

In OCR pipelines, additional mitigations include confidence-based filtering and table-aware extraction.

---

## 7. ABSA-Aware, Evidence-Grounded Summarization for ESG (Proposed Framing)

### 7.1 Why ABSA Matters for ESG Summarization
Aspect-Based Sentiment Analysis (ABSA) outputs provide a structured view of disclosures:
- aspects/material topics (e.g., emissions, workplace safety, anti-corruption)
- pillar labels (E/S/G)
- tone/sentiment or commitment flags
- provenance fields (document/page/section pointers)

Summarization can leverage ABSA as:
- a **content plan** (what must be covered),
- an **audit scaffold** (which evidence supports which summary claim),
- and a **comparability layer** (consistent structure across companies).

### 7.2 Summary Unit Design
We recommend defining multiple summary “units,” each stored with metadata:
1. **Record-level micro-summaries** (one ABSA record → short paraphrase + evidence)
2. **Company-level structured summaries** (per pillar, include top aspects and commitments)
3. **Comparative summaries** (cross-company; highlight differences with evidence)
4. **Chapter-ready summaries** (thesis narrative; still grounded in evidence)

Each unit should store:
- evidence IDs (page/section/record IDs)
- top aspects/pillars included
- tone/commitment distributions
- strategy configuration and evaluation outputs

### 7.3 Strategy Set for ABSA-Aware Summarization
We propose a three-strategy set:
- **Extractive baseline** (Lead, frequency, TextRank-like)
- **Abstractive constrained** (LLM generation with evidence-only policy + citations)
- **Hybrid** (extractive evidence scaffold + abstractive rewrite + validation)

For Indonesian ESG, the hybrid strategy often offers the best balance between readability and auditability.

---

## 8. Implementation Blueprint for a Repo-Integrated Benchmark

### 8.1 Inputs and Artifacts
A benchmark should explicitly define inputs:
- OCR text segments (with confidence/metadata)
- extracted ESG statements and ABSA fields
- ontology mappings (optional) for semantic grouping

### 8.2 Standardized Outputs
Store outputs under a stable path, for example:
- `results/summarization/summaries.jsonl` (one row per summary unit)
- `results/summarization/coverage_metrics.csv`
- `results/summarization/faithfulness_audit.csv`
- `results/summarization/strategy_comparison.csv`

### 8.3 Experiment Tracking
Each output row should include:
- summarizer strategy name
- model/prompt version (if LLM-based)
- input IDs and timestamps
- evaluation metrics and audit flags

### 8.4 Integration into Analysis and Writing
Finally, connect summaries to downstream artifacts:
- dashboards for filtering/auditing evidence
- export to chapter sections and tables
- sample-based human evaluation logs

---

## 9. Research Gaps and Future Directions

1. **Reference-free evaluation:** ESG often lacks gold summaries; robust reference-free factuality metrics and protocols are needed.
2. **Numeric and table faithfulness:** factuality checks must explicitly handle numerals, units, and table-derived claims.
3. **Multilingual domain adaptation:** Indonesian ESG involves code-switching and domain terminology; better adaptation and evaluation are needed.
4. **End-to-end reliability:** OCR/extraction errors propagate; summarization evaluation must attribute errors to stages.
5. **Human-centered utility:** summary usefulness is task-dependent (analyst vs. policymaker vs. thesis writing); evaluation should reflect target users.

---

## 10. Conclusion
Summarization research provides a rich toolkit of extractive and abstractive methods, but ESG disclosures—especially OCR-derived Indonesian sustainability reports—require stricter guarantees around evidence traceability and factual consistency. An **ABSA-aware, evidence-grounded summarization** framing provides a practical path: use structured ABSA outputs as content plans and audit scaffolds, combine extractive evidence scaffolding with constrained abstractive generation, and evaluate with multi-dimensional metrics and targeted human audits. This approach can transform summarization from a generic NLP feature into a trustworthy layer for ESG reporting and reproducible research.

---

## References (Selected)
- Lin, C.-Y. (2004). ROUGE: A Package for Automatic Evaluation of Summaries. *Workshop on Text Summarization Branches Out (WAS 2004)*.
- Mihalcea, R., & Tarau, P. (2004). TextRank: Bringing Order into Texts. *EMNLP 2004*.
- Maynez, J., Narayan, S., Bohnet, B., & McDonald, R. (2020). On Faithfulness and Factuality in Abstractive Summarization. *ACL 2020*.
- Lewis, M., Liu, Y., Goyal, N., et al. (2020). BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension. *ACL 2020*.
- Zhang, J., Zhao, Y., Saleh, M., & Liu, P. (2020). PEGASUS: Pre-training with Extracted Gap-sentences for Abstractive Summarization. *ICML 2020*.
