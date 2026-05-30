https://scite.ai/assistant/a-modular-automated-fact-checking-pipeline-for-esg-verification-8gLNkQ
# Prompts for Generating Each Section of `review_paper.md`

Use these prompts to regenerate or refine each section independently while keeping the review paper consistent.  
Assume the paper topic is **“Automated and Multimodal Fact-Checking for Indonesian ESG Claim Verification”** and the target style is **academic review paper** (concise, evidence-grounded, auditability/provenance emphasis).

General constraints (apply to all prompts):

- Write in formal academic style suitable for a thesis review chapter.
- Keep claims scoped to what can be supported by cited work; do not invent datasets, results, or metrics.
- Prefer structured paragraphs with clear topic sentences.
- When mentioning a dataset/paper/method, include an inline citation placeholder like `[CITATION: ...]` using the reference name or URL.
- Keep the Indonesian ESG focus explicit (entity/time alignment, credibility weighting, provenance).
- Do not include “tooling limitations” (e.g., MCP limits) in the paper text.

---

## Prompt: Title Block

Write a paper header for a review paper with:

- Title: “Automated and Multimodal Fact-Checking for Indonesian ESG Claim Verification”
- Date: 2026-05-30

Output only the title line and date line in Markdown.

---

## Prompt: Abstract

Write a 170–230 word abstract that:

- Defines automated fact-checking (AFC) as a modular pipeline (claim identification/normalization, evidence retrieval, claim–evidence reasoning, verdict + provenance).
- Mentions benchmark lineage (e.g., FEVER) and the shift to real-world, multilingual, and multimodal evidence.
- States why ESG disclosure verification (especially Indonesian contexts) is challenging (hedging, temporal dependence, entity ambiguity, heterogeneous sources).
- States the main contributions of the review: synthesis of datasets/methods/evaluation, and a research agenda for provenance-first Indonesian ESG claim verification.
- Emphasizes three principles: separate retrieval vs reasoning evaluation; treat “insufficient evidence” distinct from “false”; measure citation fidelity.

Include 2–4 inline citation placeholders (e.g., `[CITATION: FEVER (Thorne et al., 2018)]`, `[CITATION: Guo et al., 2022 survey]`).

---

## Prompt: Keywords

Produce a single-line keyword list (8–12 items) separated by semicolons, reflecting:

- automated fact-checking, claim verification, evidence retrieval, NLI, multimodal, credibility, ESG, Indonesia, provenance, citation fidelity

---

## Prompt: 1. Introduction
(500–800 words)
Write the Introduction section  that:

- Motivates fact-checking for accountability and ESG disclosure analysis.
- Explains why sentiment/readability/boilerplate signals are insufficient for truth verification in ESG reporting and may only indicate “risk” (greenwashing signals).
- Summarizes what AFC systems do at a high level and why multimodal evidence matters.
- Highlights key representative datasets/surveys (FEVER, LIAR, MultiFC; at least one survey) with citation placeholders.
- States the two goals of this review:
  1) synthesize textual + multimodal AFC methods/benchmarks/evaluations,
  2) translate them into a concrete research plan for Indonesian ESG claim verification.

Close with a paragraph that previews the paper structure.

---

## Prompt: 2. Problem Formulation and Terminology

Write Section 2 (600–900 words) with subsections:

### 2.1 Claim Types and Verifiability
- Define outcome/action/commitment claims.
- Explain how verifiability differs across these claim types.
- Provide 2–3 ESG-style examples and note why commitments require different evaluation rules than outcomes.

### 2.2 Evidence-Based Verdict Labels
- Present supported/refuted/insufficient evidence tri-label scheme.
- Explain what “insufficient evidence” means operationally (missing, ambiguous, conflicting, or temporally mismatched evidence).

### 2.3 Provenance and Citation Fidelity
- Define internal vs external provenance.
- Define citation fidelity and why it matters for auditability in ESG.
- Introduce the idea of evidence bundles with timestamps and excerpts.

Include 3–6 citation placeholders referencing FEVER and at least one AFC survey.

---

## Prompt: 3. Taxonomy of Automated Fact-Checking Pipelines

Write Section 3 (700–1,000 words) that explains the standard AFC pipeline and where errors occur:

### 3.1 Claim Detection and Checkworthiness
- Explain the task and why it is needed.
- Mention shared-task framing (e.g., CheckThat!) and its relevance.

### 3.2 Evidence Retrieval and Ranking
- Contrast closed-corpus vs open-web retrieval.
- Describe retrieval + reranking components and why time/entity filters matter.

### 3.3 Claim–Evidence Reasoning
- Explain NLI-style entailment/contradiction reasoning.
- Mention multi-sentence aggregation and multi-hop evidence cases.

### 3.4 Explanation and Reporting
- Explain why explanations must be constrained to cited evidence.
- Mention that some datasets include explanation generation and why that is helpful but risky if ungrounded.

Include at least 5 citation placeholders (survey + FEVER + CheckThat overview + one multimodal dataset).

---

## Prompt: 4. Key Datasets and Benchmarks

Write Section 4 (800–1,200 words) organized as:

### 4.1 Textual Claim Verification
For each dataset (FEVER, LIAR, MultiFC, SciFact):
- What it contains (claims, evidence type/source, labels).
- What it is useful for (retrieval vs reasoning).
- Key limitations for Indonesian ESG use (domain mismatch, evidence scope).

### 4.2 Shared Tasks: CheckThat!
- Summarize how shared tasks break down the pipeline and support multilingual evaluation.
- Mention typical subtasks (checkworthiness, retrieval, verification).

### 4.3 Multimodal Fact-Checking and Verification
- Distinguish image–text consistency vs end-to-end multimodal fact-checking with web evidence.
- Summarize VERITE, MOCHEG, FACTIFY3M, and MAFT at a high level (what problem they target, what supervision they offer, what they teach us).

Use 8–14 citation placeholders total.

---

## Prompt: 5. Methods: Evidence Retrieval, Reasoning, and Multimodal Fusion

Write Section 5 (800–1,200 words) covering:

### 5.1 Retrieval in Closed vs Open Settings
- Discuss leakage, missing evidence, and the role of time-aware retrieval.

### 5.2 Claim–Evidence Reasoning: From NLI to LLMs
- Explain NLI classifiers and how LLMs can be used carefully.
- Stress hallucination risks and the need for evidence quoting.

### 5.3 Multimodal Fusion Strategies
- Compare early fusion, late fusion, and textualization approaches.
- Argue why textualization is particularly suitable for ESG visuals (tables/figures).

### 5.4 Credibility Modeling and Evidence Weighting
- Propose practical credibility features (source type, domain, corroboration, recency).

Include 6–10 citation placeholders (survey, MAFT, VERITE, MOCHEG, and open-web datasets if discussed).

---

## Prompt: 6. Evaluation Protocols and Metrics

Write Section 6 (600–900 words) including:

### 6.1 Layered Evaluation (Recommended)
- Define retrieval metrics (precision@k/recall@k/MRR).
- Define verdict metrics (macro-F1/accuracy).
- Define citation fidelity evaluation and calibration.
- Explain why separating stages matters for diagnosis.

### 6.2 Preventing Temporal Leakage
- Explain temporal splits and why they matter.
- Translate to ESG: why verifying a past-year claim with future evidence can mislead.

Include 4–8 citation placeholders (CheckThat overview + survey + any temporal-split dataset paper if used).

---

## Prompt: 7. Open Challenges and Research Gaps

Write Section 7 (600–1,000 words) that:

- Lists and explains 7–10 gaps, with Indonesian ESG framing:
  - claim definition/normalization
  - evidence sufficiency
  - entity resolution
  - temporal alignment
  - multimodal bias/shortcut learning
  - citation fidelity
  - ESG domain mismatch
  - multilingual/OCR noise
  - credibility modeling limitations

For each gap, include:
- why it matters,
- what failure looks like in practice,
- one concrete mitigation direction.

Include 5–9 citation placeholders (survey + VERITE for bias + at least one multimodal dataset).

---

## Prompt: 8. Implications for Indonesian ESG Fact-Checking

Write Section 8 (700–1,000 words) with subsections:

### 8.1 Evidence Sources and Credibility
- Propose a tiered source strategy (regulators/exchange → audits → credible news/NGOs → social media).
- Explain why “credibility-first” improves early-stage evaluation.

### 8.2 Multimodality in ESG
- Explain typical ESG multimodal evidence (tables/figures, PDFs, photos) and why OCR/structured extraction matters.
- Connect to multimodal textualization ideas.

### 8.3 Greenwashing vs Fact-Checking
- Explain how greenwashing risk signals complement but do not replace claim verification.
- Propose a combined workflow: risk-prioritization + claim-level verification.

Include 3–7 citation placeholders (greenwashing textual framework + MAFT + a survey).

---

## Prompt: 9. Recommended Research Agenda for This Repository

Write Section 9 (700–1,100 words) as an implementation-ready plan, including:

### 9.1 Canonical Claim Schema (Artifact-First)
- Define required claim fields and internal provenance.
- Recommend storage format and versioning.

### 9.2 External Evidence Indexing (Credibility-First)
- Define evidence schema fields (url/domain/date/excerpt/media refs).
- Recommend how to store/transcribe OCR/captions.

### 9.3 Retrieval + Hard Filters
- Define entity normalization, time-window filtering, credibility weights.
- Explain how these reduce false contradictions.

### 9.4 Reasoning Baselines and Ablations
- Propose baseline progression (text-only → textualized multimodal).
- Define ablations (remove time filter, remove credibility, remove normalization).

### 9.5 Evaluation and Human Adjudication
- Define sampling strategy across claim types/pillars.
- Define what annotators label (evidence relevance, verdict correctness, citation fidelity).
- Define reporting artifacts (tables, confusion matrices, error taxonomy).

No need for many citations here (0–3 placeholders max); focus on concrete artifacts and metrics.

---

## Prompt: 10. Conclusion

Write Section 10 (250–400 words) that:

- Summarizes the field’s trajectory (closed-corpus → open-web → multilingual/multimodal).
- Restates the key methodological requirements for Indonesian ESG verification:
  - provenance-first claim units
  - time-aware and credibility-aware retrieval
  - citation fidelity measurement
- Ends with a concise statement of how the proposed agenda transforms ESG analysis into evidence-grounded accountability.

Include 1–3 citation placeholders (survey + one multimodal benchmark).

---

## Prompt: References (links)

Generate a “References (links)” list in Markdown bullet format that includes (at minimum) entries for:

- Guo et al. (TACL survey)
- Thorne et al. (FEVER)
- Wang (LIAR)
- MultiFC
- SciFact
- CheckThat overview papers (2019, 2020, 2025)
- VERITE
- MOCHEG
- FACTIFY3M
- MAFT
- MDPI fact-checking survey
- Greenwashing textual framework paper

For each entry, include: author(s), year, title (italic), venue (if known), and a URL.

