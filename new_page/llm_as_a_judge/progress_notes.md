codex resume 019e7866-c154-7050-a32c-50ac69a0e6b1
# Progress Notes — LLM-as-a-Judge (ESG ABSA Extraction Evaluation)

Date: 2026-05-30

This file tracks what has been completed for the `llm_as_a_judge/` research track and what to do next. It is intentionally execution-first: every item should be traceable to a file path in the repo.

---

## What has been done

- Confirmed the LLM-as-a-judge workspace exists and is runnable as a Streamlit explorer:
  - `llm_as_a_judge/app.py` loads `results/esg_records.json`, flattens run/record tables, and supports record browsing.
- Confirmed a baseline research plan exists for this track:
  - `llm_as_a_judge/research_plan.md` defines the research gap, RQs, objectives, contributions, rubric outline, methodology, and planned interpretation.
- Verified the primary extraction artifact exists and is non-trivial:
  - `results/esg_records.json` contains 1,012 runs and 5,112 extracted records (across runs with records), with diverse tone/label/aspect distributions.
- Added a complete thesis-style research write-up document for this track:
  - `documentation_llm_as_a_judge_research.md` consolidates gap → RQs → objectives → contributions → literature review → methodology → results/readiness evidence → discussion → conclusion.

---

## Current blockers / risks

- Judge artifacts are not yet generated:
  - `results/llm_judge/judge_records.jsonl` and `results/llm_judge/judge_summary.csv` do not exist by default, so there are no judge-based reliability/validity results yet.
- A judge execution pipeline is not implemented in this folder:
  - The current deliverable is an explorer + research framing, not an end-to-end judge generator.

---

## What we need to do next (recommended order)

1. Implement an offline judge runner:
   - Create a script (e.g., `llm_as_a_judge/run_judging.py`) that reads `results/esg_records.json` and writes `results/llm_judge/*`.
2. Define and version the judge rubric prompt:
   - Store prompt templates under `prompt/` or `llm_as_a_judge/` with explicit rubric versioning.
3. Add reliability experiments:
   - Self-consistency reruns (same judge, N repeats) and (optional) multi-judge comparisons.
4. Add analysis + exports:
   - Produce `judge_summary.csv` and (optional) `judge_disagreement.csv` for high-disagreement cases.
5. Add a small human evaluation set:
   - Label faithfulness/completeness/tone validity for a stratified sample, then calibrate judge thresholds.

