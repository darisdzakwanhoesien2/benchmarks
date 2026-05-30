https://scite.ai/assistant/llm-basedjudges-for-esg-absa-evaluation-NMgWe9
# Prompts for Writing Each Section of `review_paper.md`

Use these prompts to (re)generate each section of the review paper in a consistent style. Each prompt is designed to be fed to an LLM along with any repo context you want to reference (e.g., `llm_as_a_judge/app.py`, `llm_as_a_judge/research_plan.md`, `results/esg_records.json` stats).

Global writing constraints (apply to all sections):

- Audience: thesis/research readership; formal but practical.
- Style: concrete, repo-grounded where possible; avoid hype.
- Do not invent citations. If you mention “prior work”, phrase it generally unless you can cite a real source.
- Keep claims scoped: if not experimentally measured in this repo, label as “planned”, “recommended”, or “hypothesized”.
- Prefer structured lists, explicit definitions, and artifact names/paths.

---

## Prompt 0 — Paper Metadata (title/date/scope)

Write the opening metadata block for a review paper titled **“LLM-as-a-Judge for ESG ABSA Extraction Evaluation”**.

Include:

- Date: 2026-05-30
- Scope: This review supports the repo module `llm_as_a_judge/` and focuses on LLM judges for evaluating record-level ESG ABSA extraction outputs.

Constraints:

- Keep to 3–6 lines.
- Mention that the artifact style is “run lineage + structured records”.

---

## Prompt 1 — Abstract

Write the **Abstract** for a review paper on LLM-as-a-judge for ESG ABSA extraction evaluation.

Must include:

- Problem: semantic evaluation bottleneck; proxy checks miss hallucination and misalignment.
- Why judges: scalable semantic assessment with structured rubric outputs.
- What the paper provides: judge taxonomy for ESG records, reliability/validity protocols, artifact standards.
- Closing: actionable roadmap for implementing in this repository (compatible with `llm_as_a_judge/app.py` and `results/esg_records.json`).

Constraints:

- 150–220 words.
- No citations.
- Avoid absolute claims like “solves evaluation”; use cautious language.

---

## Prompt 2 — Keywords

Generate a **Keywords** list (10–16 items) for this review paper.

Constraints:

- Include ESG disclosures, ABSA, information extraction, faithfulness/hallucination, rubric scoring, reliability, calibration, Indonesian reports.
- Use semicolon-separated terms.

---

## Prompt 3 — Introduction

Write **Section 1: Introduction**.

Must include:

- Repo-grounded framing: the extraction output schema includes `text`, `aspect`, `labels`, `esg`, `tone`, `sentiment`, `sentiment_score`, and possibly `reasoning`.
- Why evaluation is hard in ESG: semantics > syntax, expensive gold labels, nuanced constructs (commitment/action/outcome).
- Position LLM-as-a-judge as a triage + diagnostics layer (not a replacement for humans).
- End with a clear “paper organization” paragraph listing the upcoming sections.

Constraints:

- 450–700 words.
- Do not mention any judge results as already completed.

---

## Prompt 4 — Background / Definition of LLM-as-a-Judge

Write **Section 2: Background** explaining what “LLM-as-a-judge” means in this paper.

Must include:

- Formal description of `(x, ŷ, rubric) -> {scores, verdict, diagnostics}`.
- Distinguish rubric scoring vs pairwise ranking paradigms.
- Explain why rubric scoring fits record-level ESG diagnostics in this repo.
- Note that judges are fallible “raters” requiring measurement and calibration.

Constraints:

- 400–650 words.
- Include 1 small boxed list or table-like bullet list describing the two paradigms.

---

## Prompt 5 — Why ESG ABSA Extraction Needs a Judge Layer

Write **Section 3** explaining why ESG ABSA extraction needs LLM judging.

Must include:

- A list of semantic failure modes relevant to ESG extraction (hallucination, wrong aspect, label noise, tone mismatch, pillar mismatch, vague output).
- A short subsection on bilingual/Indonesian report challenges (OCR artifacts, mixed language, reporting style variance).
- Explain why simple proxies (parse success, basic overlap) cannot catch these.

Constraints:

- 450–700 words.
- Use at least two bullet lists (failure modes; bilingual challenges).

---

## Prompt 6 — Judge Output Taxonomy (Rubric + Tags)

Write **Section 4: Judge Output Taxonomy for ESG ABSA Records**.

Must include:

- Unit of evaluation: one extraction record + lineage fields (`run_idx`, `record_idx`, `model`, `prompt`, `target`, `target_pages`, etc.).
- Define each rubric dimension with 1–2 sentences:
  - faithfulness, completeness, ontology alignment, tone validity, explanation quality.
- Define verdict labels (`accept/revise/reject`) and provide a recommended mapping rule (e.g., minimum faithfulness threshold).
- Provide a failure tag list and short definitions.
- Explain and justify the `evidence_quote` requirement.

Constraints:

- 600–900 words.
- Include a compact JSON example *schema* (not real data) showing field names only (no invented values).

---

## Prompt 7 — Judge Design Patterns

Write **Section 5: Judge Design Patterns**.

Must cover:

- Single-judge baseline.
- Self-consistency (reruns) and what it reveals.
- Multi-judge ensembles and how to use disagreement.
- Pairwise judging and why it can be more stable for A/B comparisons.
- Hybrid workflows (rubric + pairwise).

Constraints:

- 500–800 words.
- For each pattern, include: (a) when to use, (b) main risk, (c) artifact to save.

---

## Prompt 8 — Judge Failure Modes and Biases + Mitigations

Write **Section 6** on judge failure modes, biases, and mitigations.

Must include:

- Prompt sensitivity and rubric versioning.
- Leniency/severity drift and calibration.
- Fluent-but-ungrounded rationales and the role of evidence quotes.
- Ontology confusion and the need for definitions/examples.
- Tone ambiguity (commitment/action/outcome) and how to reduce it.

Constraints:

- 600–900 words.
- Use a “Risk → Symptom → Mitigation” structure, preferably as bullets.

---

## Prompt 9 — Experimental Protocol (Evaluation Study)

Write **Section 7: Methodological Protocol** for a judge-based evaluation study for this repo.

Must include:

- Data prep steps from `results/esg_records.json`.
- Stratified sampling plan (by model/prompt/tone/labels/aspects; include failure strata).
- Judge conditions (baseline, self-consistency, multi-judge).
- Metrics:
  - reliability (variance; agreement on verdict/score bins),
  - convergent validity against weak anchors (`ok`, `error_type`, distributions),
  - actionability (failure tag frequencies/co-occurrences).
- Reporting standards: what to report so the study is reproducible.

Constraints:

- 700–1100 words.
- Keep it concrete (bullet checklists are OK).

---

## Prompt 10 — Artifact Design for Reproducible Judging

Write **Section 8: Artifact Design** describing recommended files and fields.

Must include:

- `results/llm_judge/judge_records.jsonl`
- `results/llm_judge/judge_summary.csv`
- Optional `results/llm_judge/judge_disagreement.csv`
- Required lineage and judge config fields.

Constraints:

- 500–800 words.
- Provide 1 example JSONL “record skeleton” with keys only (no values).

---

## Prompt 11 — Relationship to Human Evaluation

Write **Section 9** on how judge evaluation relates to human evaluation.

Must include:

- The “calibration, not replacement” framing.
- A recommended workflow: broad judge → disagreement sampling → human labeling → calibration → iterate.
- What to measure for judge-human alignment (do not claim results).

Constraints:

- 350–600 words.

---

## Prompt 12 — Open Research Challenges (ESG-Specific)

Write **Section 10** listing open research challenges for LLM judging in ESG ABSA extraction.

Must include:

- Gold scarcity/subjectivity.
- Temporal context and tense.
- Cross-sentence context limitations.
- Ontology evolution/versioning.
- Strategic vagueness/boilerplate language.

Constraints:

- 350–600 words.
- End with 3 “research directions” bullets.

---

## Prompt 13 — Practical Recommendations (Implementation-Ready)

Write **Section 11** with practical recommendations for implementing LLM-as-a-judge in this repository.

Must include:

- Enforcing a JSON schema and rejecting non-conforming outputs.
- Evidence quote requirement and rationale length constraints.
- Rubric prompt versioning and storage.
- Stratified sampling first; self-consistency on subset.
- Export disagreement cases for annotation.
- Integrate artifacts into `llm_as_a_judge/app.py`.

Constraints:

- 10–16 bullets, each 1 sentence.
- Every bullet should mention an artifact, metric, or implementation mechanism (not generic advice).

---

## Prompt 14 — Conclusion

Write **Section 12: Conclusion**.

Must include:

- Summary of why judges help and what must be done for rigor (reliability measurement + calibration + artifact lineage).
- Reiterate evidence-anchored diagnostics as key to auditability.
- Close with a forward-looking paragraph about implementing `results/llm_judge/*` and using it to drive iterative extraction improvements.

Constraints:

- 250–450 words.

---

## Prompt 15 — References Placeholder

Write **Section “References (to be finalized)”** as a placeholder.

Must include:

- A statement that citations are intentionally not hard-coded to avoid inventing references.
- A short list of source categories to collect via Zotero/BibTeX/manual bibliography (LLM-as-judge, hallucination/faithfulness, inter-rater reliability, ABSA/ESG NLP, judge bias/meta-evaluation).

Constraints:

- 120–200 words.

