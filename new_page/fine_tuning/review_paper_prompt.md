https://scite.ai/assistant/fine-tuning-indonesian-esg-absa-repository-grounded-review-and-a-kZG1AE
# Prompts for Generating Each Section of `review_paper.md`

Date: 2026-05-30

Purpose: This file provides **copy/paste prompts** to (re)generate each section of `review_paper.md` consistently. Each prompt is written to keep the paper **repository-grounded** and aligned with the fine-tuning track described by:

- `fine_tuning/app.py`
- `documentation_fine_tuning.md`
- `documentation_fine_tuning_research.md`
- `results/revision_analysis/*`
- Baselines in `code/` (rule-based, classical ML, hybrid/deep)

Guidelines for every prompt:

- Write in an academic “review paper” style, but keep it implementation-actionable.
- Avoid claiming measured improvements unless explicitly labeled as “expected” or “hypothesized”.
- Keep references to the repository concrete by including relevant file paths.
- Prefer clear definitions, taxonomies, and failure modes over broad marketing language.
- Keep section content consistent with the scope: **Indonesian ESG ABSA** and **fine-tuning vs PEFT** under leakage-aware evaluation.

---

## Prompt 0 — Global Style + Constraints (use with all sections)

You are writing a thesis-style review paper section for an applied NLP project. The paper is about **fine-tuning for Indonesian ESG ABSA** in a repository that already contains labeled artifacts and baseline models, but does not yet contain full fine-tuning benchmark results.

Constraints:
- Do not fabricate citations or pretend to have performed a systematic literature search.
- Do not claim any new experimental results unless clearly marked as “not yet implemented”.
- Make all repo references explicit via file paths.
- Emphasize methodological rigor: leakage-aware splits, harmonized labels, long-tail reporting, stability across seeds.

Output:
- Return only the section text, using the section heading exactly as provided in the prompt.

---

## Prompt 1 — Title

Write a concise, informative academic title for a review paper on **fine-tuning for Indonesian ESG ABSA** grounded in an operational benchmark repository. The title must reflect:

- Fine-tuning and parameter-efficient fine-tuning (PEFT)
- ESG aspect-based sentiment analysis in Indonesian sustainability reports
- A repository-integrated perspective (data + baselines + diagnostics)

Output only the title line (no subtitle unless necessary).

---

## Prompt 2 — Abstract

Write the **Abstract** for a review paper titled “Fine-Tuning for Indonesian ESG Aspect-Based Sentiment Analysis (ABSA): A Repository-Grounded Review and Research Agenda”.

Include:
- Problem context: ESG disclosure analysis; Indonesian; ABSA
- Why fine-tuning matters and why it is often under-specified (data + protocol issues)
- Key themes: full FT vs PEFT; leakage risk; label noise; long-tail imbalance; stability reporting
- What the repository already provides (planner UI, labeled artifacts, baselines, diagnostics)
- What is missing (canonical dataset packaging, training runner, exported benchmark artifacts)
- A brief statement of contributions: taxonomy + gaps + blueprint

Keep it ~150–250 words.

---

## Prompt 3 — Keywords

Write a **Keywords** line (comma-separated) for the review paper. Include terms covering:
- fine-tuning, PEFT (LoRA/adapters)
- ABSA/sentiment analysis
- ESG/sustainability reports
- Indonesian NLP and robustness/evaluation

---

## Prompt 4 — 1. Introduction

Write section **“1. Introduction”** for the review paper.

Requirements:
- Motivate ESG report analysis and why ABSA is needed (aspect + sentiment + tone distinctions).
- Explain the gap: PLMs exist but a reproducible fine-tuning benchmark protocol is missing in many applied settings.
- Make it explicitly repository-grounded by mentioning:
  - `fine_tuning/app.py` (planner UI)
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` (existing labels)
  - baseline modules under `code/`
- Close with a clear statement of what the review provides (taxonomy + gaps + repo-integrated agenda).

Target length: ~3–6 paragraphs.

---

## Prompt 5 — 2. Scope and Definitions

Write section **“2. Scope and Definitions”** with the following subsections:

- 2.1 Task Scope: Indonesian ESG ABSA
- 2.2 Fine-Tuning
- 2.3 Why Sustainability Reports Are Not Standard ABSA Corpora

Requirements:
- Define the minimum supervised tasks (aspect, sentiment) and optional tasks (pillar, tone).
- Distinguish full fine-tuning vs PEFT.
- Describe domain properties: templated boilerplate, long-form context, code-switching, commitment vs outcome language.
- Keep the scope constrained to classification-first approaches aligned with current repo artifacts.

Target length: ~500–900 words total.

---

## Prompt 6 — 3. Review Methodology (Narrative, Repository-Grounded)

Write section **“3. Review Methodology (Narrative, Repository-Grounded)”**.

Requirements:
- State this is a narrative review aimed at being implementation-actionable.
- Explicitly disclaim that it is not a systematic review with database search protocol.
- Include a short “Repository Anchors” bullet list with these file paths (verbatim):
  - `fine_tuning/app.py`
  - `documentation_fine_tuning.md`
  - `documentation_fine_tuning_research.md`
  - `code/rule_based.py`
  - `code/classical_ml.py`
  - `code/hybrid_model.py`
  - `code/deep_model.py`
  - `results/revision_analysis/pilot_ground_truth_annotations.csv`
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
  - `results/revision_analysis/model_stability_summary.csv`
  - `results/revision_analysis/prompt_stability_summary.csv`
  - `fine_tuning/call_climatebert_logic.py`
- Explain how these anchors shape the review’s emphasis (leakage, stability, auditable outputs).

---

## Prompt 7 — 4. Fine-Tuning in Domain-Specific ABSA: What the Literature Emphasizes

Write section **“4. Fine-Tuning in Domain-Specific ABSA: What the Literature Emphasizes”** with subsections:

- 4.1 Pretraining vs In-Domain Supervision
- 4.2 Low-Resource Fine-Tuning: The Typical Failure Modes
- 4.3 PEFT as an Engineering and Scientific Strategy
- 4.4 Multi-Task Learning

Requirements:
- Keep it high-level but concrete: mention domain shift, label noise, imbalance, seed instability, leakage.
- Explain why PEFT can help reproducibility/iteration (not just cost).
- Treat multi-task as an ablation unless labels are clean/complete.
- Do not include fake citations; instead, use phrases like “prior work commonly finds…” without naming papers.

Target length: ~900–1400 words.

---

## Prompt 8 — 5. A Taxonomy of Fine-Tuning Approaches for Indonesian ESG ABSA

Write section **“5. A Taxonomy of Fine-Tuning Approaches for Indonesian ESG ABSA”** with subsections:

- 5.1 Data Axis
- 5.2 Objective Axis (Task Formulation)
- 5.3 Parameter Update Axis
- 5.4 Training Control Axis
- 5.5 Evaluation Axis

Requirements:
- Provide a structured taxonomy that could be turned into experiment tables.
- Explicitly relate each axis back to this repository’s likely constraints and artifacts.
- Include practical examples (e.g., head-only baseline vs LoRA vs full FT; class weights; repeated seeds; subgroup breakdown).

Target length: ~900–1400 words.

---

## Prompt 9 — 6. Research Gaps and Open Problems (Indonesian ESG ABSA Fine-Tuning)

Write section **“6. Research Gaps and Open Problems (Indonesian ESG ABSA Fine-Tuning)”**.

Must include these gap headings (verbatim):

- 6.1 Leakage-Aware Evaluation Is Under-Implemented
- 6.2 Label Taxonomy Drift and Mixed Labels
- 6.3 Long-Tail Aspects
- 6.4 “Better F1” vs “Better Decisions”
- 6.5 Full Fine-Tuning vs PEFT Tradeoffs Remain Unclear In-Repo

Requirements:
- Make each gap actionable with a short “what to do” suggestion.
- Tie the gaps to repo signals: company clustering in `pilot_ground_truth_annotations.csv`, existing stability summaries, etc.

Target length: ~700–1100 words.

---

## Prompt 10 — 7. Research Questions and Objectives (Review-Informed)

Write section **“7. Research Questions and Objectives (Review-Informed)”** with:

- 7.1 Research Questions (list RQ1–RQ4)
- 7.2 Research Objectives (list O1–O4)

Requirements:
- Keep them concise, testable, and aligned to repo implementation.
- Ensure RQs mention: effectiveness, full FT vs PEFT, subgroup/stability, data requirements.
- Ensure objectives mention: dataset packaging, training runner, evaluation rigor, thesis-ready reporting.

Target length: ~250–450 words.

---

## Prompt 11 — 8. Proposed Methodology Blueprint (Repository-Integrated)

Write section **“8. Proposed Methodology Blueprint (Repository-Integrated)”** with subsections:

- 8.1 Dataset Construction
- 8.2 Model Families and Training
- 8.3 Metrics and Diagnostics
- 8.4 Outputs and Reporting Artifacts

Requirements:
- Describe inputs from `results/revision_analysis/*` and outputs under `results/fine_tuning/`.
- Include explicit artifact names:
  - `labels_master.csv`
  - `splits.json`
  - `metrics_*.json`
  - `predictions_*.csv`
  - `confusion_*.csv`
  - `error_analysis_*.csv`
- Emphasize company/report-level splits and repeated seeds.
- Recommend adding a `pages/` dashboard that reads exported artifacts rather than training in Streamlit.

Target length: ~900–1400 words.

---

## Prompt 12 — 9. Results (Current Status in the Repository)

Write section **“9. Results (Current Status in the Repository)”**.

Requirements:
- Clearly state that fine-tuning benchmark results are not yet implemented.
- Describe what does exist today:
  - `fine_tuning/app.py` (planner + evidence snapshots)
  - `fine_tuning/call_climatebert_logic.py` and `results/fine_tuning/*` outputs (API validation artifacts)
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` (labels as feasibility evidence)
- Describe what is missing (canonical dataset packaging, training runner, exported benchmark artifacts).

Target length: ~400–700 words.

---

## Prompt 13 — 10. Discussion

Write section **“10. Discussion”** with subsections:

- 10.1 What Would Count as a Strong Fine-Tuning Result?
- 10.2 Expected Tradeoffs: Full Fine-Tuning vs PEFT
- 10.3 Data Quality and Taxonomy Are Likely the Binding Constraint

Requirements:
- Define criteria for strong claims (leakage-aware, subgroup, stability, error transparency).
- Discuss why PEFT can be near-parity and better for iteration/reproducibility in a thesis workflow.
- Argue that data quality/taxonomy harmonization likely dominates model choice.

Target length: ~700–1100 words.

---

## Prompt 14 — 11. Conclusion

Write section **“11. Conclusion”**.

Requirements:
- Summarize the review’s main message: fine-tuning must be an end-to-end protocol.
- Reinforce the core methodological requirements: leakage-aware splits, harmonization, long-tail reporting, stability.
- Close with a concrete statement of the repository-integrated benchmark contribution (full FT vs PEFT, auditable artifacts).

Target length: ~250–450 words.

---

## Prompt 15 — Appendix A. Immediate Next Steps (Implementation Checklist)

Write **“Appendix A. Immediate Next Steps (Implementation Checklist)”** as a numbered checklist (1–5).

Requirements:
- Include these exact action items:
  1) create `results/fine_tuning/labels_master.csv`
  2) create `results/fine_tuning/splits.json`
  3) implement `code/fine_tuning_esg_absa.py` (head-only baseline, PEFT, full FT, repeated seeds)
  4) export standardized artifacts under `results/fine_tuning/`
  5) add a Streamlit page under `pages/` to visualize results

Keep it crisp and repo-operational.

