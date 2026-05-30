# A Review of Evidence-Grounded Chatbots for Indonesian ESG Aspect-Based Sentiment Analysis (ABSA): Architectures, Evaluation, and Research Gaps

Date: 2026-05-30

---

## Abstract

Interactive chatbots are increasingly used to surface insights from complex document collections, but their adoption in high-stakes domains such as Environmental, Social, and Governance (ESG) reporting requires strong guarantees of **faithfulness**, **auditability**, and **semantic consistency**. This review synthesizes research directions and best practices for building an **evidence-grounded Indonesian-language chatbot** on top of structured ESG Aspect-Based Sentiment Analysis (ABSA) artifacts. We organize the literature around (i) retrieval-augmented generation and non-parametric memory, (ii) dense and sparse retrieval, (iii) hallucination and factuality control, (iv) ABSA-aligned conversational summarization and aggregation, and (v) evaluation frameworks emphasizing citation correctness and stability. We then map these insights to a concrete benchmark setting: an ESG ABSA repository with OCR ingestion, structured extraction, ontology coverage tracking, verifier outputs, prompt/model stability summaries, and failure-mode datasets. The paper concludes with a research agenda and reproducible artifact schema for future empirical studies, including query sets, run logs, claim-level faithfulness labeling, and dialogue-specific failure taxonomies.

---

## Keywords

Retrieval-augmented generation (RAG); ESG; Indonesian NLP; aspect-based sentiment analysis (ABSA); faithfulness; hallucination; citation grounding; evaluation; OCR pipelines; conversational analytics

---

## 1. Introduction

ESG disclosures contain heterogeneous evidence (narrative text, tables, metrics, and policy statements) that stakeholders often need to query interactively. While dashboards can expose aggregate statistics, many real-world information needs are conversational: “What are the main environmental issues for Company X?”, “Show the evidence page”, “Compare tone across companies”, or “Which aspects are most negative?”.

However, open-ended generation is prone to *hallucinations*—fluent but unsupported claims—especially when the source corpus is noisy (e.g., OCR artifacts) and when questions require aggregation and multi-step reasoning. For ESG ABSA chatbots, the central research problem is therefore:

> How can we build a chatbot that is **useful and interactive** while remaining **evidence-grounded, auditable, and ABSA-consistent**?

This review focuses on the methods and evaluation lenses most relevant to that goal and highlights the research gaps that remain open for Indonesian-language ESG ABSA conversational systems.

---

## 2. Problem Setting and Requirements

### 2.1 ESG ABSA conversational tasks

In an ESG ABSA pipeline, systems typically output structured records such as:
- entity/company
- aspect (e.g., emissions, waste, labor, governance)
- ESG pillar (E/S/G)
- sentiment/tone/commitment labels
- evidence pointers (document/page/snippet)

A chatbot built on top of these artifacts must support task families such as:

1. **Evidence lookup**: “Apa buktinya?” (show supporting source).
2. **Explanation**: why a label is assigned (e.g., tone/commitment).
3. **Aggregation**: summarize across pages, sections, time, or companies.
4. **Comparison**: contrast companies or aspects.
5. **Ontology-aware queries**: map terms to ESG taxonomy (aspects → pillar).
6. **Out-of-scope handling**: refuse or ask for clarification when evidence is missing.

### 2.2 Non-negotiable constraints in high-stakes domains

For ESG chatbots, “helpful” is not sufficient. Systems should satisfy:
- **Faithfulness**: claims are supported by retrieved evidence.
- **Citation correctness**: cited sources actually support the claims they are attached to.
- **ABSA semantic integrity**: aspect/pillar/tone labels do not drift across turns.
- **Robustness/stability**: answers are stable under paraphrase and repeated queries.
- **Transparency**: uncertainty and missing evidence are explicitly stated.

---

## 3. Retrieval-Augmented Generation (RAG) as a Foundation

RAG methods combine a parametric generator with a non-parametric evidence store, retrieving relevant passages/documents at inference time. The RAG framing was popularized by work that couples retrieval with sequence-to-sequence generation for knowledge-intensive tasks (Lewis et al., 2020). citeturn0search15

### 3.1 Why retrieval matters for ESG ABSA chatbots

Retrieval is central because:
- ESG corpora are too large and dynamic to “bake into” model weights reliably.
- evidence must be inspectable; retrieving source snippets enables “show evidence”.
- grounding reduces hallucination pressure by constraining generation to retrieved items.

### 3.2 Pretraining-time vs inference-time retrieval

Retrieval can be introduced at:
- **pretraining-time** (retrieval-augmented language model pretraining, e.g., REALM) citeturn1academia12
- **inference-time** (retrieve then generate; RAG-style systems)

For applied benchmarks, inference-time retrieval is usually the practical entry point because it can be attached to existing corpora without retraining the base model.

---

## 4. Retrieval Methods for Evidence Selection

### 4.1 Sparse retrieval (BM25) as a strong baseline

Sparse term-based retrieval (e.g., BM25) remains a competitive baseline and is frequently used for first-stage retrieval and as a diagnostic comparator. The probabilistic relevance framework and BM25 family are well established in IR literature (Robertson & Zaragoza, 2009). citeturn2search7

### 4.2 Dense retrieval and dual encoders

Dense retrieval learns vector representations for queries and passages, enabling semantic matching beyond lexical overlap. Dense Passage Retrieval (DPR) is a foundational dual-encoder approach in open-domain QA (Karpukhin et al., 2020). citeturn0academia13

### 4.3 Evaluation benchmarks for retrievers

Although ESG corpora are domain-specific, general evaluation suites (e.g., BEIR) highlight that retriever performance can vary across domains and tasks; they also encourage explicit reporting of retrieval quality rather than assuming retrieval “just works” (Thakur et al., 2021). citeturn2academia13

### 4.4 Practical evidence units for ESG ABSA

In an ESG ABSA chatbot, the best indexing unit is an open design choice:
- page-level chunks (aligned to OCR pages)
- statement-level records (aligned to extraction output)
- hybrid (page chunk + statement pointers + ontology tags)

Review takeaway: the evidence unit should match the evaluation target. If the chatbot is graded on claim-level citation correctness, statement-level indexing often makes auditing easier than broad page chunks.

---

## 5. Hallucination, Faithfulness, and Factuality Control

### 5.1 Hallucination as a central risk

Neural generation systems can hallucinate unsupported content; large-scale human evaluations in summarization demonstrate that hallucinations are common even when models appear fluent (Maynez et al., 2020). citeturn0search16

For ESG ABSA chatbots, hallucinations often appear as:
- invented metrics (“emissions increased by X%”) not present in evidence
- incorrect attributions (mixing companies or years)
- “smoothing” OCR noise into plausible but false narratives

### 5.2 NLI-based inconsistency detection as a tool family

A major family of faithfulness checks uses natural language inference (NLI) to detect inconsistencies between a candidate output and the source. SummaC revisits NLI-based inconsistency detection for summarization at document granularity (Laban et al., 2022). citeturn1search0

Even if ESG chatbots are not “summarization” systems, the methodological insight transfers: **inconsistency detection must match the granularity of the task** (claim-level vs document-level vs dialogue-level).

### 5.3 Self-critique and reflective RAG variants

Recent work explores adding critique/reflection loops to improve retrieval and factuality. Self-RAG explicitly integrates retrieval, generation, and critique through self-reflection (Asai et al., 2023). citeturn1academia16

Review takeaway: reflective loops can improve citation accuracy but increase latency and complexity; they should be evaluated as distinct architectures, not as “prompt tweaks”.

---

## 6. ABSA-Specific Challenges in Conversational Systems

### 6.1 Semantic drift across turns

Multi-turn dialogue introduces drift risks:
- aspect drift (switching from “emissions” to “waste” without notice)
- pillar drift (mixing E/S/G categories)
- tone drift (confusing sentiment polarity vs commitment tone)

ABSA chatbots should treat aspect/pillar/tone as **explicit state variables** and carry them through the dialogue, rather than re-inferring them every turn from scratch.

### 6.2 Aggregation and comparison pitfalls

Aggregation queries (“overall environmental performance”) trigger common failure modes:
- over-generalization beyond evidence
- mixing incomparable evidence (different years, different report sections)
- conflating qualitative and quantitative statements

Review takeaway: comparisons require explicit aggregation rules and traceable evidence groupings, not only “generate a comparison paragraph.”

---

## 7. Multilingual and Indonesian-Specific Considerations

Indonesian ESG chatbots face additional constraints:
- **code-switching**: ESG terms may appear in English (“emissions”, “net zero”, “governance”)
- **terminology mismatch**: user phrasing differs from ontology/aspect labels used in extraction outputs
- **morphology and spelling variation**: impacts sparse retrieval recall

Recommended design pattern:
- maintain a bilingual synonym/alias table aligned with internal aspect + ontology labels
- retrieval uses both original query and normalized/expanded query forms
- answer language defaults to Indonesian, but evidence can be quoted verbatim

---

## 8. Evaluation: What Should Be Measured

### 8.1 Decompose evaluation into retrieval and generation

Review consensus: evaluate separately:

1. **Retrieval quality**
   - recall of gold evidence (if available)
   - top-k evidence precision
   - robustness under paraphrase

2. **Answer quality**
   - relevance and completeness
   - clarity and usefulness for stakeholders

3. **Faithfulness and citations**
   - citation presence rate
   - citation correctness rate (does the cited evidence actually support the claim?)
   - claim-level supported/unsupported/contradicted labels (recommended)

4. **ABSA semantic consistency**
   - aspect/pillar/tone correctness
   - consistency across turns (state stability)

5. **Stability and robustness**
   - repeated-query consistency (same question, same config)
   - paraphrase consistency
   - sensitivity to prompt/model changes

### 8.2 Why “benchmarking” matters

Without standardized artifacts (query sets, run logs, labels, metrics), chatbot iterations are difficult to compare and regression-test. Evaluation should therefore be treated as a *first-class deliverable* alongside the chatbot implementation.

---

## 9. Mapping the Review to a Concrete Repository Benchmark

This section summarizes how the reviewed methods connect to an ESG ABSA benchmark repo that includes:
- OCR ingestion and processing
- structured ESG statement extraction
- verifier outputs and failure mode analysis
- prompt/model stability summaries
- ontology coverage tables

### 9.1 Existing evidence/diagnostics that enable grounding-first chatbots

Key artifact types:
- labeled pilot data for quick distribution checks
- verifier datasets for evidence matching outcomes
- failure-mode datasets for taxonomy bootstrapping
- stability summaries for robustness stress testing

### 9.2 Recommended reproducibility schema for chatbot research artifacts

Minimal set of outputs to enable scientific comparison:

- `results/chatbot/queries.jsonl`
  - `query_id`, `text_id`, `lang`, `intent`, `expected_aspects`, `company`
- `results/chatbot/runs.jsonl`
  - `run_id`, `query_id`, `architecture`, `retriever`, `k`, `model`, `prompt_hash`
  - `retrieved_evidence` (IDs + snippets)
  - `answer_text`, `citations` (structured)
- `results/chatbot/labels.csv`
  - `run_id`, `claim_id`, `faithfulness_label`, `citation_correct`, `absa_consistent`
- `results/chatbot/metrics.csv`
  - aggregated metrics by architecture/config

---

## 10. Research Gaps and Open Problems

Based on the literature and the benchmark requirements, the highest-impact research gaps are:

1. **Claim-level citation correctness at scale**
   - Most systems report “has citations”; fewer validate that each citation supports each claim.

2. **ABSA-constrained dialogue state**
   - Few chatbot designs treat aspect/pillar/tone as explicit state variables with consistency checks.

3. **Robustness under paraphrase and configuration drift**
   - Stability is often ignored, despite known sensitivity to prompts and models.

4. **OCR-driven noise and evidence fragmentation**
   - ESG evidence is frequently spread across tables and noisy text; retrieval and citation must handle partial evidence and uncertain parsing.

5. **Indonesian ESG terminology alignment**
   - Query normalization and ontology mapping for Indonesian ESG remains under-tested in benchmarked chatbot settings.

---

## 11. Future Directions (Actionable Research Agenda)

1. **Hybrid routing + RAG**
   - intent classification routes to ABSA-safe handlers; retrieval supplies evidence; generation summarizes with strict citation templates.

2. **Evidence panel UX + “why” explanations**
   - expose evidence snippets and allow interactive drills (show more context, show all evidence for an aspect).

3. **Automatic faithfulness proxies with human-in-the-loop sampling**
   - run NLI/consistency checks automatically; sample for human labeling to calibrate thresholds.

4. **Dialogue-specific failure taxonomy**
   - extend static failure modes with dialogue failures: follow-up drift, cross-turn contradiction, citation mismatch, unsupported aggregation.

5. **Retriever evaluation customized to ESG ABSA**
   - create a small gold set mapping Indonesian queries to evidence pages/records; track recall@k across retrievers.

---

## 12. Conclusion

Evidence-grounded Indonesian ESG ABSA chatbots sit at the intersection of retrieval-augmented generation, factuality control, multilingual query handling, and ABSA-consistent aggregation. The literature strongly suggests that a successful system must be evaluated not only by response fluency but by retrieval quality, claim-level faithfulness, citation correctness, ABSA semantic integrity, and stability under perturbation. For benchmark repositories that already contain structured extraction outputs, verifiers, stability summaries, and failure-mode datasets, the most impactful next step is to formalize a reproducible chatbot evaluation harness and artifact schema so that architectural choices (direct prompting vs RAG vs hybrid routing) can be compared scientifically.

---

## References

- Asai, A., et al. (2023). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*. arXiv:2310.11511. citeturn1academia16
- Karpukhin, V., Oğuz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., & Yih, W.-t. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. arXiv:2004.04906. citeturn0academia13
- Laban, P., Schnarr, K., Barbosa, A., & Hearst, M. (2022). *SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization*. TACL. citeturn1search0
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W.-t., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS. citeturn0search15
- Maynez, J., Narayan, S., Bohnet, B., & McDonald, R. (2020). *On Faithfulness and Factuality in Abstractive Summarization*. ACL. citeturn0search16
- Mihalcea, R., & Tarau, P. (2004). *TextRank: Bringing Order into Texts*. EMNLP Workshop. citeturn2search0
- Robertson, S., & Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval. citeturn2search7
- Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., & Gurevych, I. (2021). *BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*. arXiv:2104.08663. citeturn2academia13
- Guu, K., Lee, K., Tung, Z., Pasupat, P., & Chang, M.-W. (2020). *REALM: Retrieval-Augmented Language Model Pre-Training*. arXiv:2002.08909. citeturn1academia12

