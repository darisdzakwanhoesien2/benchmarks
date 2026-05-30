https://scite.ai/assistant/absa-aware-evidence-grounded-esg-summarization-in-indonesian-dis-ePY1a6
# Prompts for Generating Each Section of `review_paper.md`

Date: 2026-05-30

Purpose: These prompts are designed to (re)generate each section of the review paper in a consistent academic style. Use them with an LLM to produce sections that are: (i) domain-specific to Indonesian ESG disclosures, (ii) evidence/faithfulness aware, and (iii) aligned with ABSA-aware summarization framing.

**Global instructions (apply to every prompt)**
- Write in an academic review-paper tone.
- Keep claims calibrated; avoid unsupported statements and avoid inventing citations.
- Use clear headings and short paragraphs; prefer bullets only where they help.
- Emphasize ESG constraints: auditability, provenance, ABSA signal preservation, OCR noise, faithfulness.
- When mentioning canonical methods/metrics (e.g., ROUGE, TextRank, BART, PEGASUS, factuality checks), describe them at a high level without fabricating numeric results.
- Do not add repo-specific numbers unless explicitly provided as inputs.

---

## Prompt: Abstract
- 150–220 words.

Write the **Abstract** for a review paper titled:
“A Review of Summarization Methods and Evaluation for Indonesian ESG Disclosures: Toward ABSA-Aware, Evidence-Grounded Summaries”.

Requirements:

- State the problem: ESG summarization under OCR noise and trust requirements.
- Summarize what is reviewed: extractive → abstractive methods; evaluation with emphasis on factual consistency.
- State the proposed framing: ABSA-aware, evidence-grounded summarization.
- End with 2–3 key open challenges/future directions.

Output only the abstract text (no keywords list).

---

## Prompt: 1. Introduction

Write Section **1. Introduction** for the review paper.

Cover:
- What summarization is and why it matters in operational contexts.
- Why ESG disclosures (Indonesian sustainability reports) are a special case (mixed narrative + numeric KPIs + compliance language).
- Why common benchmark assumptions (news datasets, reference summaries) do not transfer cleanly.
- Preview the structure of the paper (methods → datasets/domain → evaluation → faithfulness → ABSA-aware framing → implementation blueprint → gaps).

Length: ~3–6 paragraphs.

---

## Prompt: 2. Background: Summarization Task Definitions

Write Section **2. Background: Summarization Task Definitions**.

Include the following subsections and explain them clearly with ESG examples:
- **2.1 Extractive vs. Abstractive Summarization**
- **2.2 Single-Document vs. Multi-Document Summarization**
- **2.3 Query-Focused and Structured Summarization**
- **2.4 Query-Focused Multi-Document Summarization**


Constraints:
- Tie each definition to ESG reporting needs (pillar-structured summaries, evidence traceability).
- Keep it conceptual; do not cite specific datasets unless necessary.

---

## Prompt: 3. A Taxonomy of Summarization Methods

Write Section **3. A Taxonomy of Summarization Methods** with the subsections below.

Subsections:
- **3.1 Heuristic Extractive Baselines** (lead, frequency; strengths/limits in ESG)
- **3.2 Graph-Based Extractive Ranking (TextRank Family)** (high-level mechanism, why it’s used)
- **3.3 Classical Supervised Summarization** (extractive ranking; early encoder–decoder)
- **3.4 Neural Abstractive Summarization with Pretraining** (seq2seq, transfer; mention BART/PEGASUS at a high level)
- **3.5 Long-Document Summarization** (hierarchical, retrieval-augmented, chunking)
- **3.6 Constrained / Controlled Summarization** (content plans, citations, validation)

Requirements:
- For each subsection, include: (a) what it is, (b) strengths, (c) failure modes in ESG/OCR settings.
- Keep it review-style, not a tutorial.

---

## Prompt: 4. Datasets and Domain Considerations

Write Section **4. Datasets and Domain Considerations** with these subsections:
- **4.1 Canonical Summarization Datasets (and Why ESG Differs)**
- **4.2 Multilingual and Low-Resource Constraints (Indonesian)**
- **4.3 OCR and Table-to-Text Noise**

Include:
- How ESG differs from news (structure, repetitiveness/boilerplate, numeric density, auditability).
- Challenges from Indonesian + code-switching + domain terms.
- OCR-specific error types and how they propagate into summarization.
- Practical implications for experimental design (sampling, cleaning, evidence selection).

---

## Prompt: 5. Evaluation of Summarization

Write Section **5. Evaluation of Summarization** with these subsections:
- **5.1 Overlap-Based Metrics (ROUGE)** (why used; limitations for ESG)
- **5.2 Semantic Similarity Metrics** (what they add; what they miss)
- **5.3 Faithfulness and Factual Consistency Evaluation** (NLI/QA/classifiers; why critical)
- **5.4 Human Evaluation** (faithfulness/coverage/usefulness/auditability axes)
- **5.5 Evaluation Under a Benchmark Mindset** (reproducible outputs, configs, dashboards)

Requirements:
- Emphasize that ROUGE is not sufficient for ESG.
- Recommend a multi-dimensional evaluation protocol.
- Do not claim any specific metric correlations unless you can justify them.

---

## Prompt: 6. Faithfulness: Sources of Errors and Mitigation Strategies

Write Section **6. Faithfulness: Sources of Errors and Mitigation Strategies** with:
- **6.1 Common Error Modes in Abstractive Summaries** (entity, numeric, scope, temporal, causal overreach)
- **6.2 Practical Mitigations** (evidence-first, content planning, citations, post-hoc validation, human audits; OCR confidence filtering)

Requirements:
- Make the discussion ESG-specific (targets, emissions scopes, time horizons).
- Include a short “why this matters” paragraph (risk and trust implications).

---

## Prompt: 7. ABSA-Aware, Evidence-Grounded Summarization for ESG (Proposed Framing)

Write Section **7. ABSA-Aware, Evidence-Grounded Summarization for ESG (Proposed Framing)** with:
- **7.1 Why ABSA Matters for ESG Summarization**
- **7.2 Summary Unit Design**
- **7.3 Strategy Set for ABSA-Aware Summarization**

Include:
- How ABSA outputs act as a content plan and audit scaffold.
- Define summary units (record-level, company-level, comparative, chapter-ready) and required metadata (provenance, aspect/pillar coverage, tone/commitment distribution).
- Describe the three-strategy set (extractive, constrained abstractive, hybrid) and when to prefer each.

---

## Prompt: 8. Implementation Blueprint for a Repo-Integrated Benchmark

Write Section **8. Implementation Blueprint for a Repo-Integrated Benchmark** with:
- **8.1 Inputs and Artifacts**
- **8.2 Standardized Outputs**
- **8.3 Experiment Tracking**
- **8.4 Integration into Analysis and Writing**

Requirements:
- Provide a concrete but tool-agnostic blueprint: what inputs, what stored outputs, what metadata, what evaluation tables.
- Include example file naming conventions (e.g., `results/summarization/summaries.jsonl`, `faithfulness_audit.csv`) without assuming a specific stack.
- Keep it oriented toward reproducibility.

---

## Prompt: 9. Research Gaps and Future Directions

Write Section **9. Research Gaps and Future Directions**.

Cover (at minimum):
- reference-free evaluation for ESG
- numeric/table faithfulness checks
- multilingual domain adaptation for Indonesian ESG
- end-to-end error attribution across OCR → extraction → summarization
- human-centered utility evaluation

Length: 5–10 bullet points or short paragraphs (choose one style and stay consistent).

---

## Prompt: 10. Conclusion

Write Section **10. Conclusion**.

Requirements:
- Summarize the key takeaways: method landscape, evaluation needs, faithfulness priority, ABSA-aware framing.
- End with a clear thesis: evidence-grounded, auditable summarization is the practical path for ESG.
- Keep it to ~1–2 paragraphs.

---

## Prompt: References (Selected)

Write a **References (Selected)** section suitable for an academic review paper.

Constraints:
- Include only well-known, canonical works that you are confident exist.
- Provide standard citation fields (authors, year, title, venue).
- Do not invent DOIs or URLs.
- Keep the list to ~5–12 references, prioritizing: ROUGE, TextRank, one pretraining-based summarization model (e.g., BART or PEGASUS), and one faithfulness/factuality paper.

