https://scite.ai/assistant/evidence-grounded-indonesian-esg-absa-chatbots-a-review-d3z9nd
# Prompts for Generating Each Section of `review_paper.md`

Date: 2026-05-30

Use these prompts to (re)generate each section of the review paper in a consistent, thesis-ready style. Each prompt is designed to be copy/pasted into an LLM with minimal edits.

**Global instructions (prepend to every prompt)**
- Audience: graduate thesis / review paper readers.
- Tone: formal, technical, concise.
- Writing rules:
  - No hallucinated citations. If you cannot cite, write “[citation needed]”.
  - Keep claims grounded to well-known literature; do not invent datasets or results.
  - Use consistent terminology: *evidence-grounded*, *faithfulness*, *citation correctness*, *ABSA semantic consistency*, *robustness/stability*.
  - Default language: English (include Indonesian example queries where requested).
- Output format:
  - Start with the exact section heading (e.g., `## 1. Introduction`).
  - Use short paragraphs and bullet lists where helpful.
  - Do not include other sections.

---

## Prompt: Title

Write the full paper title for a review paper on evidence-grounded chatbots for Indonesian ESG ABSA. Keep it informative and specific. Output only the `# ...` title line.

---

## Prompt: Abstract

Write `## Abstract` for a review paper on **evidence-grounded Indonesian ESG ABSA chatbots**.

Include:
- motivation (why conversational ESG analytics needs grounding)
- scope (what this paper reviews: RAG, retrieval, hallucination control, ABSA conversational issues, evaluation)
- contributions (how the review is organized and what it offers: mapping to a benchmark repo, gaps, agenda)
- 150–220 words, one paragraph

Avoid:
- reporting new experiments
- over-claiming (“state of the art”) without support

---

## Prompt: Keywords

Write `## Keywords` with 8–12 keywords/phrases relevant to the paper. Prefer standard terms (RAG, DPR, BM25, faithfulness, ABSA, Indonesian NLP, OCR, evaluation).

---

## Prompt: 1. Introduction

Write `## 1. Introduction` for a review paper on evidence-grounded chatbots for Indonesian ESG ABSA.

Cover:
- what ESG disclosures are and why stakeholders need interactive access
- why dashboards are insufficient for query-driven information needs
- why hallucinations/citation errors are especially risky in ESG contexts
- define the central research problem in one clear sentence
- preview the structure of the review (what sections follow)

Include 2–4 example Indonesian user queries (short, natural).

---

## Prompt: 2. Problem Setting and Requirements

Write `## 2. Problem Setting and Requirements`.

Subsections to include:
### 2.1 ESG ABSA conversational tasks
- define the structured ABSA record fields (company/entity, aspect, pillar, sentiment/tone, evidence pointers)
- list 6–8 chatbot task families (evidence lookup, explanation, aggregation, comparison, ontology-aware, out-of-scope)

### 2.2 Non-negotiable constraints in high-stakes domains
- define and distinguish: faithfulness vs citation correctness vs ABSA semantic integrity vs robustness/stability vs transparency
- provide 1–2 concrete examples of what can go wrong (e.g., invented metrics; wrong company attribution)

Write in a “requirements spec” style: clear bullets, testable statements.

---

## Prompt: 3. Retrieval-Augmented Generation (RAG) as a Foundation

Write `## 3. Retrieval-Augmented Generation (RAG) as a Foundation`.

Include:
- definition of RAG (generator + retrieval from external store)
- why retrieval helps for auditability and reducing hallucination pressure
- distinguish inference-time retrieval vs pretraining-time retrieval (e.g., REALM-like)
- explain why inference-time retrieval is the practical choice for applied repo benchmarks

Add 2–3 citations placeholders like “(Lewis et al., 2020)” and “(Guu et al., 2020)” without fabricating details.

---

## Prompt: 4. Retrieval Methods for Evidence Selection

Write `## 4. Retrieval Methods for Evidence Selection`.

Cover:
### 4.1 Sparse retrieval (BM25)
- what it is and why it remains strong
- why it matters for Indonesian (lexical variation) and for OCR (noise)

### 4.2 Dense retrieval and dual encoders
- what dense retrieval is
- DPR as an exemplar and why semantic matching helps

### 4.3 Evaluation benchmarks for retrievers
- why we need explicit retrieval evaluation
- mention heterogeneous benchmark principles (e.g., BEIR-like)

### 4.4 Practical evidence units for ESG ABSA
- compare indexing units: page chunks vs statement records vs hybrid
- give criteria for choosing units (auditability, granularity, context limits)

End with a short “Review takeaway” paragraph summarizing recommended practice.

---

## Prompt: 5. Hallucination, Faithfulness, and Factuality Control

Write `## 5. Hallucination, Faithfulness, and Factuality Control`.

Include:
- what hallucination looks like in ESG chat (invented metrics, wrong attributions, smoothing OCR noise)
- why faithfulness is central and must be measured
- introduce NLI-based inconsistency detection (SummaC-like) as a family of tools
- introduce reflective / self-critique RAG variants (Self-RAG-like)
- discuss tradeoffs: latency vs reliability; complexity vs measurable gains

Provide a short taxonomy table (markdown) listing 5 hallucination/failure types and how grounding mitigates each.

---

## Prompt: 6. ABSA-Specific Challenges in Conversational Systems

Write `## 6. ABSA-Specific Challenges in Conversational Systems`.

Cover:
- semantic drift across turns (aspect/pillar/tone drift) with examples
- why ABSA variables should be treated as explicit dialogue state
- aggregation and comparison pitfalls; propose rules/controls (time range scoping, company scoping, aspect scoping, evidence grouping)

End with a short checklist that an ABSA chatbot should satisfy during multi-turn interactions.

---

## Prompt: 7. Multilingual and Indonesian-Specific Considerations

Write `## 7. Multilingual and Indonesian-Specific Considerations`.

Include:
- code-switching patterns in ESG domain queries
- terminology alignment problem (user phrasing vs ontology labels)
- impacts on sparse vs dense retrieval
- recommended design pattern: bilingual synonym/alias table, query expansion, response language policy (Indonesian answers, verbatim evidence quotes)

Add 3 example mappings in a small table (Indonesian term → English/ontology label).

---

## Prompt: 8. Evaluation: What Should Be Measured

Write `## 8. Evaluation: What Should Be Measured`.

Requirements:
- explicitly separate retrieval evaluation vs answer evaluation vs citation evaluation
- propose concrete metrics for:
  - retrieval: recall@k, precision@k (if gold available), robustness under paraphrase
  - answers: relevance/completeness (human rubric)
  - citations: presence rate + correctness rate (claim-level)
  - ABSA consistency: aspect/pillar/tone alignment
  - stability: repeated-query variance; config sensitivity
- justify why “has citations” is insufficient
- recommend a minimal benchmark artifact set (queries, run logs, labels, metrics)

Write in a prescriptive “evaluation protocol” tone.

---

## Prompt: 9. Mapping the Review to a Concrete Repository Benchmark

Write `## 9. Mapping the Review to a Concrete Repository Benchmark`.

Assume a repo already contains:
- OCR ingestion + processing
- structured ESG statement extraction outputs
- verifier outputs and failure-mode datasets
- prompt/model stability summaries
- ontology coverage tables

Include:
- how these artifacts enable grounding-first chatbots (bullets)
- a minimal reproducibility schema under `results/chatbot/`:
  - `queries.jsonl`, `runs.jsonl`, `labels.csv`, `metrics.csv`
- describe key fields for each file (as bullet lists or mini schemas)

Keep this section implementation-oriented and reproducible.

---

## Prompt: 10. Research Gaps and Open Problems

Write `## 10. Research Gaps and Open Problems`.

List 5–8 high-impact gaps with short explanations. Must include:
- claim-level citation correctness at scale
- ABSA-constrained dialogue state + consistency checking
- robustness under paraphrase and prompt/model drift
- OCR noise and fragmented evidence
- Indonesian ESG terminology alignment

For each gap, add one “testable research question” in one sentence.

---

## Prompt: 11. Future Directions (Actionable Research Agenda)

Write `## 11. Future Directions (Actionable Research Agenda)`.

Provide 5–7 future directions, each with:
- what to implement
- why it matters
- what artifact/metric would validate it

Must include:
- hybrid routing + RAG
- evidence panel UX + “why” explanations
- automatic faithfulness proxies + human-in-the-loop calibration
- dialogue-specific failure taxonomy
- custom retriever evaluation for ESG ABSA

---

## Prompt: 12. Conclusion

Write `## 12. Conclusion`.

Summarize:
- why grounding-first is necessary for ESG ABSA chatbots
- what this review contributed (organization + mapping + gaps)
- what the next empirical step should be (implement + benchmark + report tables)

Keep it 1–2 short paragraphs.

---

## Prompt: References

Write `## References` with a short, curated list (6–12 items) of seminal and representative works spanning:
- RAG / retrieval-augmented generation
- dense retrieval (DPR-like)
- factuality / faithfulness / inconsistency detection (SummaC-like; summarization factuality)
- retriever benchmarking (BEIR-like)
- graph-based ranking baseline (TextRank-like)

Rules:
- Do not invent DOIs or venues if unsure.
- If details are uncertain, include author + year + title only and mark missing details as “[details needed]”.

