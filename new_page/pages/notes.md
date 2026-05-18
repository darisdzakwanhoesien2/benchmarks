Based on the annotation readiness across all 6 RQs, here is a prioritized action plan ordered by what unblocks the most:

---

## Step 1 — Run ClimateBERT on all 332 records (RQ3) `~2 hours`
**This is the highest ROI single action.** RQ3 is already at κ=0.645 with proxy labels. One batch job gives you real ClimateBERT outputs and converts RQ3 from "defensible" to "publication-ready."
- Open `1_4_ClimateBERT_Record_Batch.py` — it's already built for this
- Run inference on the full 332 records
- Compute majority-class and keyword baselines for comparison
- After: code 20–30 disagreement cases qualitatively in `0_9_Tone_ClimateBERT_Visualization.py`

---

## Step 2 — Complete pilot annotation to 150 records + recruit 2nd annotator (RQ2) `~1 week`
**This is the most consequential gap.** Without it, RQ2 can only make descriptive claims, not validity claims. Currently 70/150 done.
- Use `1_1_Ground_Truth_Workbench.py` to finish your own labels to 150
- Recruit a second annotator (supervisor, colleague, or paid annotator) for the same 150 records
- Compute Cohen's κ in `1_3_Ground_Truth_Metrics.py` — target ≥ 0.60
- If κ < 0.60: adjudicate disagreements, refine tone definitions, re-annotate

---

## Step 3 — Manually transcribe 50–100 pages for OCR ground truth (RQ1) `~3–5 hours`
**Unblocks all CER/WER claims.** Right now you have zero quality evidence for RQ1.
- Pick 50–100 pages that represent the range: clean digital, scanned, bilingual, tabular
- Manually type or verify the true text for each page
- Load into `1_2_OCR_Quality_Workbench.py` to compute CER/WER automatically
- While doing this: tag each page with a failure mode category (scanned/table/diacritics/header) — this simultaneously fills the RQ4 failure rate gap

---

## Step 4 — Add a 3rd model and run 3× repeated runs at temperature=0 (RQ6) `~3 hours`
**Without this, RQ6 cross-model claims are not credible with only 2 models.**
- Add one smaller open-weight model as a lower bound (e.g. a 7B model)
- For each of the 7 prompts × 3 models: run 3× at temp=0
- This gives you mean ± SD parse success and field completion — the core RQ6 table
- `2_0_LLM_Processing_Result_Visualizer.py` and `2_1_LLM_Error_Parse_Audit.py` already handle the visualization

---

## Step 5 — Quantify failure rates per mode on a 100-record sample (RQ4) `~2 hours`
**The taxonomy is done (10 modes identified) — you just need counts.**
- Pick a fixed 100-record held-out sample
- For each record: tag which failure mode(s) apply (bilingual code-switch, hedged modal, table loss, etc.)
- This directly produces the "failure rates per 100 records" table for Section 4.4.2
- Code 3–5 text examples per mode for the qualitative section (Section 4.4.4)

---

## Step 6 — Map the 46 unmapped aspects to semantic clusters (RQ4 + RQ2) `~2 hours`
**Reframes a gap as a contribution.** The 46 novel aspects are not a failure — they're a discovery.
- Open `1_6_Ontology_Path_Viewer.py` — the 46 unmapped aspects are already surfaced
- Group them into 5–8 semantic clusters (e.g. "Community Relations", "Regulatory Compliance", "Supply Chain")
- Frame in the thesis as: *novel Indonesian ESG aspect vocabulary not covered by GRI/SASB*

---

## Step 7 — Create a clean-run manifest and provenance links (RQ5) `~1–2 hours`
**The last remaining gap for RQ5.** You have 967 artifacts and 147 job logs — you just need to formally document the chain.
- Create a simple markdown or CSV manifest: `input file → pipeline stage → output file → job ID`
- Even 30–40% coverage (the stages you know) is reportable with honest limitations
- Note that `0_5_Thesis_Systematic_Workflow.py` and `1_7_Research_Questions_Dashboard.py` already serve as the "dashboard-as-documentation" argument

---

## Priority order at a glance

| Step | RQ | Effort | Unblocks |
|---|---|---|---|
| 1 | RQ3 | ~2h | Real ClimateBERT results, disagreement analysis |
| 2 | RQ2 | ~1 week | Validity claims, Cohen's κ, accuracy reporting |
| 3 | RQ1 | ~4h | All CER/WER claims + partially fills RQ4 failure modes |
| 4 | RQ6 | ~3h | Cross-model stability claims |
| 5 | RQ4 | ~2h | Quantitative failure rate table |
| 6 | RQ4+RQ2 | ~2h | Novel aspect contribution framing |
| 7 | RQ5 | ~1h | Reproducibility manifest |

**Start with Step 1 today** — it's a single pipeline run that immediately makes your strongest RQ publication-ready.