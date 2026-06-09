# Review Paper Section Prompts (Copy/Paste Pack)

Use the prompts below to generate or refine each section of `review_paper.md`. Each prompt is designed to be sent independently to an LLM.

**Assumed paper title:** *A Practical Review of LLM-Assisted ESG & Climate-Disclosure Analytics Pipelines*

## Global instructions (prepend to every section prompt)
Copy this block into the top of any prompt if you want consistent style across sections:

```
You are writing a review paper section for a practitioner-oriented academic audience.
Style: precise, non-hype, neutral tone, define terms on first use, avoid marketing language.
Output format: Markdown.
Constraints:
- No fabricated citations. If you cite, use placeholders like [CITATION NEEDED] unless you are provided sources.
- Avoid strong causal claims unless qualified.
- Use concrete examples (e.g., “Scope 1/2/3”, “baseline year”, “assurance”) when helpful.
- Keep the section internally consistent with the rest of the paper.
If information is missing, make reasonable assumptions and state them explicitly.
```

---

## Prompt 0 — Paper-wide outline alignment (optional but recommended)
Use when you want the model to “sync” with what already exists and propose edits.

```
Task: Review the following paper draft and propose improvements to structure and section flow.
Deliverable:
1) A revised outline (H2/H3 headings) that preserves the original intent.
2) A bullet list of 8–12 concrete edits to improve clarity, rigor, and auditability.
3) A short list of missing sections (if any) and why they matter.

Draft (paste full `review_paper.md`):
<PASTE HERE>
```

---

## Prompt 1 — Abstract
```
Write an abstract for a review paper on LLM-assisted ESG & climate-disclosure analytics pipelines.
Length: 150–220 words.
Must include:
- Problem framing (why disclosures are hard data)
- Core pipeline components (OCR/layout, retrieval, LLM extraction, evaluation)
- Main contribution (taxonomy + practical recommendations)
- Caution about reliability / evaluation
Output: single Markdown paragraph + 4–8 keywords line.
```

---

## Prompt 2 — Introduction
```
Write the Introduction section.
Length: 600–900 words.
Must include:
- Why ESG/climate disclosures matter (research + decision-making)
- Why document heterogeneity makes analytics hard (PDF, tables, scans, multilingual)
- Why LLMs help and why they create new risks (hallucination, inconsistency)
- Scope and contributions (what this paper covers vs. excludes)
Include 1 short “running example” used throughout the paper (e.g., extracting emissions target + evidence).
Output: Markdown with H2/H3 headings.
```

---

## Prompt 3 — Background: The Disclosure Data Problem
```
Write a background section explaining:
1) document heterogeneity and layout issues,
2) high-context nature of ESG/climate language (targets vs. performance, boundaries, uncertainty),
3) implications for dataset construction.
Length: 500–800 words.
Add a small table (Markdown) with 6–10 common disclosure elements and typical pitfalls.
```

---

## Prompt 4 — Taxonomy of End-to-End Pipelines
```
Write a taxonomy section describing an end-to-end pipeline for ESG/climate disclosure analytics.
Length: 900–1400 words.
Must cover stages:
- ingestion/versioning
- OCR/layout parsing
- segmentation/chunking
- retrieval/indexing
- LLM extraction
- normalization/entity resolution
- knowledge representation/lineage
For each stage provide:
- purpose
- key design choices (2–4 bullets)
- common failure modes (2–4 bullets)
- evaluation hooks (how to measure/monitor that stage)
Output: Markdown with clear subheadings per stage.
```

---

## Prompt 5 — Modeling Approaches (BERT → LLMs → RAG → constraints)
```
Write a modeling approaches section comparing:
- domain-adapted encoders (e.g., BERT variants) for classification/extraction
- instruction-tuned LLMs for schema extraction
- retrieval-augmented generation (RAG) patterns
- tool-augmented / constrained decoding (JSON schema, function calling, validation-retry)
Length: 800–1200 words.
Include:
- a “When to use what” decision matrix (Markdown table) with cost, data needs, reliability, interpretability.
- 3 concrete implementation tips for making LLM extraction robust.
Avoid naming proprietary models unless provided; keep it method-centric.
```

---

## Prompt 6 — Ground Truth, Evaluation, and Error Analysis
```
Write the evaluation section focused on scientific and deployment-grade validation.
Length: 1200–1800 words.
Must include:
- Ground truth strategies (expert, weak labels, adjudication, model-assisted)
- Metrics beyond accuracy (field-level F1, record exact match, evidence correctness, abstention)
- Error taxonomy by stage (OCR, layout, retrieval, LLM, normalization)
- Reproducibility guidance (versioning, logging prompts, canary sets)
Add:
- A compact rubric for evaluating “evidence-grounded extraction” (3–6 criteria).
- A short paragraph on inter-annotator agreement and disagreement handling.
```

---

## Prompt 7 — System Design Patterns for Reliability
```
Write a systems section with actionable patterns:
- schema-first extraction
- evidence-first extraction and provenance
- human-in-the-loop triage
- monitoring + drift detection
Length: 700–1100 words.
Include:
- 2 short pseudo-workflows (bulleted steps) for “extract metric” and “extract statement”.
- A checklist (10–15 items) suitable for an engineering team.
Avoid generic advice; be specific about what to log/store and why.
```

---

## Prompt 8 — Ethics, Governance, and Security
```
Write an ethics/governance section.
Length: 500–900 words.
Must cover:
- over-interpretation / greenwashing amplification risks
- bias and representativeness across regions/sectors/languages
- privacy/licensing/terms constraints and data retention
Include a short “Do/Don’t” list for responsible deployment (6–10 bullets).
Neutral tone; avoid policy prescriptions beyond practical guidance.
```

---

## Prompt 9 — Open Challenges and Future Directions
```
Write a future work section.
Length: 500–900 words.
Must include at least 6 distinct open challenges, each with:
- why it’s hard
- what progress might look like (measurement/benchmark signal)
Include at least 2 challenges specifically about tables/figures and multilingual alignment.
```

---

## Prompt 10 — Practical Recommendations (Checklist)
```
Write a short recommendations section formatted as:
- a 12–18 item checklist grouped into 3–5 categories (e.g., Data, Modeling, Evaluation, Governance).
- each item must be actionable and testable (i.e., you can verify if it’s done).
Length: 250–450 words total.
```

---

## Prompt 11 — Conclusion
```
Write the conclusion.
Length: 250–450 words.
Must:
- restate the core message (pipeline + evaluation discipline)
- emphasize evidence/provenance and reproducibility
- avoid hype; include one sentence about limitations
```

---

## Prompt 12 — References (two modes)
### Mode A: Placeholder references only
```
Produce a “Selected References” list with 12–20 entries.
Rules:
- Do NOT invent citations you can’t verify.
- If uncertain, use placeholders like: [CITATION NEEDED: OCR survey], [CITATION NEEDED: RAG paper], etc.
Group by topic: OCR/layout, retrieval, extraction, evaluation, ESG/climate disclosure analytics.
Output: Markdown list.
```

### Mode B: Source-grounded references (requires you to provide sources)
```
You will be given a set of sources (DOIs, URLs, or bibtex).
Task: Create a consistent reference list (APA style) and add 1–2 sentences per reference explaining relevance to ESG/climate disclosure pipelines.
Sources:
<PASTE SOURCES HERE>
```

---

## Prompt 13 — “Tighten this section” editor prompt (works on any section)
```
Rewrite the section below to be:
- clearer and more technical
- less repetitive
- more auditability-focused (evidence, provenance, evaluation hooks)
Keep the same headings but improve wording.
Do not add new citations unless marked [CITATION NEEDED].

Section text:
<PASTE SECTION HERE>
```

---

## Prompt 14 — Evidence-first extraction schema design (optional)
Use if you want the model to help you design the JSON schema used by your pipeline.

```
Design a JSON schema (with examples) for extracting climate-related disclosure records from PDFs.
Requirements:
- Support both metric records (value/unit/year/scope/boundary) and statement records (claim/topic/polarity/timeframe/uncertainty).
- Every non-null extracted field must include an evidence pointer (doc_id, page, start/end offsets or block ids).
- Must support “not found” and “insufficient evidence” explicitly.
Deliverables:
1) JSON Schema (draft-07 or newer)
2) 2 example outputs (one metric, one statement)
3) 6 validation rules (plain English) that your post-processor should enforce
```

