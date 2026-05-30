# Complete Research Write-up: Multimodal Fact-Checking for Indonesian ESG ABSA

This document turns the existing `fact_checking/` prototype and the repo’s current revision-analysis artifacts into a defensible thesis-style research chapter structure: **research gap, research questions, research objectives, research contribution, literature review, methodology, results, discussion, and conclusion**.

It is written to match what currently exists in this repository today (as of **2026-05-30**):

- Streamlit research-plan + dataset-evidence prototype: `fact_checking/app.py`
- Research framing baseline: `documentation_fact_checking.md`
- Grounding datasets (revision analysis): `results/revision_analysis/*.csv`

If you want this chapter to become “implementation-complete” (end-to-end external evidence retrieval + adjudicated verdict evaluation), follow the “Next Steps” at the end and in `progress_notes.md`.

---

## 1. Background and Problem Statement

ESG disclosure analysis in this repository already supports OCR extraction, ABSA-style labeling (aspect, tone, sentiment), ontology mapping, and several quality-control dashboards. These components answer: *What did companies say and how is it framed?*

However, ESG analysis for accountability also requires answering: **Is the disclosure supported by external evidence, contradicted by credible sources, or unverifiable with available information?** This is the domain of automated fact-checking and claim verification.

For Indonesian sustainability reports, the evidence landscape is multimodal:

- Textual evidence (news, press releases, regulator announcements, NGO reports)
- Social media text (coverage, but noisy and credibility-varying)
- Visual evidence (infographics, photos, scanned tables, charts)
- Video evidence (documentaries, interviews, hearings) via transcripts and frames

The existing repo is therefore well-positioned to extend from extraction/classification into **provenance-aware multimodal claim verification**.

---

## 2. Research Gap

Even with the existing ABSA and validation pages, there are clear gaps that prevent full fact-checking:

1. **No claim-truthfulness layer.** Current outputs primarily characterize internal disclosures (aspect/tone/sentiment), but do not verify whether claims match external reality.
2. **Validation focuses on parsing/label correctness, not verdict correctness.** The repo contains strong diagnostics for OCR and label stability, but limited measurement for claim-level supported/contradicted judgments.
3. **External evidence is not integrated.** News/social/video/image evidence is not yet retrieved, filtered, ranked, and attached to claims in a unified workflow.
4. **Multimodal reasoning is not operationalized.** There is no implemented fusion step that uses text+image+video to determine support vs contradiction.
5. **No benchmark protocol for verdict quality and citation fidelity.** Without a canonical claim unit and ground-truth labels, it is hard to evaluate or compare approaches.

These gaps motivate a structured fact-checking module that is compatible with Indonesian ESG contexts and the repo’s existing provenance style.

---

## 3. Research Questions

**RQ1 (Feasibility):**  
Can ESG claims extracted from Indonesian sustainability reports be automatically verified against external Indonesian multimodal evidence?

**RQ2 (Evidence Utility):**  
Which evidence type contributes most to verification quality—news text, social media text, documentary/video transcripts, images, or a multimodal fusion?

**RQ3 (Verdict Reliability):**  
How reliably can the system classify each claim as `supported`, `contradicted`, or `insufficient_evidence` under a provenance requirement?

**RQ4 (Multimodal Value):**  
Does multimodal aggregation improve reliability over text-only verification for ESG claims?

**RQ5 (Failure Modes):**  
What dominant failure modes appear in Indonesian ESG fact-checking (entity mismatch, temporal drift/mismatch, sentiment-claim confusion, visual ambiguity, and credibility noise)?

---

## 4. Research Objectives

1. Define a **canonical claim unit schema** derived from existing ABSA outputs and report provenance.
2. Build a reproducible pipeline that connects internal claims to external evidence across **text, image, and video**.
3. Produce `supported` / `contradicted` / `insufficient_evidence` verdicts with a **citation bundle** (URLs/metadata + timestamp).
4. Evaluate (i) retrieval quality and (ii) verdict accuracy separately to identify bottlenecks.
5. Integrate fact-checking artifacts into the repo’s dashboards and thesis chapter workflows.

---

## 5. Research Contributions

This work contributes to the repository (and to Indonesian ESG analysis) by delivering:

1. **A provenance-aware multimodal fact-checking architecture** layered on top of the existing ABSA/OCR pipeline.
2. **A claim-centric benchmark design** that links internal disclosure claims to external evidence trails.
3. **A reproducible evaluation protocol** for verdict quality *and* citation fidelity, including multimodal ablations.
4. **A disclosure reliability layer** that expands analysis beyond sentiment/tone into factual accountability.
5. Reusable artifacts for greenwashing and ESG misinformation risk analysis in low-resource multilingual settings.

---

## 6. Literature Review (Focused Topics)

The literature review should be structured around the methods required by the pipeline, not generic summaries:

1. **Automated fact-checking pipelines**: claim detection/normalization → evidence retrieval → claim-evidence reasoning → verdict + explanations/citations.
2. **NLI / entailment for verification**: textual entailment and contradiction classification as the reasoning core; calibration/uncertainty.
3. **Multimodal fact-checking**: approaches that combine image/video evidence with text (OCR, captioning, visual entailment, cross-modal consistency).
4. **Source credibility modeling**: weighting evidence by reputation, recency, and document type; handling social media noise.
5. **Low-resource / multilingual verification**: Indonesian language issues, code-switching, NER/entity linking under OCR artifacts.
6. **ESG/greenwashing research**: reliability of voluntary disclosures; triangulation with external accountability signals.

Repo-specific principle for literature alignment:

- The system must output **traceable, timestamped evidence bundles** and be evaluated on **citation correctness**, not only on fluent verdict narratives.

---

## 7. Methodology

### 7.1 Existing Artifacts to Reuse (Grounded Evidence)

The `fact_checking/app.py` prototype already grounds the research plan in `results/revision_analysis/` artifacts:

- `pilot_ground_truth_annotations.csv` (internal label ground truth)
- `llm_statement_page_verifier_compiled.csv` (page-level statement provenance verification)
- `failure_modes.csv` (known failure modes)
- `prompt_stability_summary.csv` and `model_stability_summary.csv` (operational stability)
- `ocr_processing_summary.csv` (OCR processing tracking)

These artifacts justify feasibility: the repo already tracks internal statements, provenance, and quality risks.

### 7.2 Canonical Claim Unit (Proposed)

Define the claim record used for fact-checking:

- `claim_id` (stable identifier)
- `company` (normalized entity)
- `claim_text` (canonical statement)
- `claim_type` (commitment / action / outcome)
- `esg_pillar` (E/S/G/mixed/none)
- `aspect` (ontology or ABSA aspect)
- `time_reference` (explicit year/period, if present)
- `internal_provenance` (document id + page ref + extracted snippet)

Key requirement: **every claim remains linked to internal provenance** (which the repo already emphasizes).

### 7.3 External Evidence Collection (To Implement)

Evidence sources (Indonesia-focused, ESG-relevant):

- News and press releases (text, URL, publish date)
- Government/regulator/stock exchange announcements (authoritative)
- NGO / watchdog reports
- Social media posts (optional, credibility-weighted)
- Video transcripts (YouTube captions, documentary transcripts, hearings)
- Images (figures, photos, infographics) with OCR/caption extraction

Evidence item schema (minimum):

- `evidence_id`, `source_type`, `source_domain`, `publish_date`, `url`
- `evidence_text` (or transcript excerpt)
- `evidence_media_refs` (image/video refs, if applicable)
- `retrieval_score`, `entity_match_score`, `time_match_score`

### 7.4 Fact-Checking Pipeline (Target Architecture)

1. **Claim extraction + normalization**  
   Use existing ABSA/LLM extraction artifacts to produce canonical claim candidates.
2. **Evidence retrieval**  
   Query external sources (text, transcript index, image OCR store) and return top-k evidence.
3. **Filtering and ranking**  
   Apply entity disambiguation, date filtering, and credibility weighting to reduce false contradictions.
4. **Reasoning / verification**  
   - Textual NLI-style support vs contradiction checks
   - Multimodal fusion when visual/video evidence is present (OCR/caption/transcript alignment)
5. **Verdict output**  
   `supported` / `contradicted` / `insufficient_evidence`, plus:
   - confidence + calibration bin
   - citation bundle (evidence excerpts + URLs + timestamps)
   - explanation constrained to evidence (no hallucinated facts)

### 7.5 Evaluation Plan

Evaluate each layer independently (to avoid “black box” failure):

1. **Retrieval quality**: precision@k / recall@k; evidence relevance labeling on a subset.
2. **Verdict quality**: macro-F1 over `supported/contradicted/insufficient_evidence`; confusion analysis by claim type/pillar.
3. **Citation fidelity**: does the cited evidence actually support the verdict? (human adjudication subset)
4. **Ablations**:
   - text-only vs text+image vs text+video vs full fusion
   - with vs without credibility weighting
5. **Robustness checks**:
   temporal drift; sector vocabulary shift; OCR-noise stress tests.

---

## 8. Results (Current Repo Evidence + What It Implies)

This section reports what can be stated *today* from the repository’s existing revision-analysis datasets, and what these results imply for fact-checking readiness. These are not yet “external truth” fact-check results; they are **readiness and reliability diagnostics**.

### 8.1 Dataset Scale (as of 2026-05-30)

From the datasets used by `fact_checking/app.py`:

- Pilot labeled rows: **5,444** (`pilot_ground_truth_annotations.csv`)
- Statement-page verifier rows: **332** (`llm_statement_page_verifier_compiled.csv`)
- Failure-mode rows: **62** (`failure_modes.csv`)
- OCR docs tracked: **23** (`ocr_processing_summary.csv`)
- Prompt stability configs: **7** (`prompt_stability_summary.csv`)
- Model stability configs: **6** (`model_stability_summary.csv`)

Interpretation: the repo already has (i) a meaningful amount of internal labeling ground truth and (ii) a provenance verification dataset that can become the backbone for claim provenance guarantees in fact-checking.

### 8.2 Provenance Verification Signal

In `llm_statement_page_verifier_compiled.csv`, `best_status` counts are:

- `exact`: **311**
- `likely`: **17**
- `possible`: **4**

Interpretation: internal statement → page provenance matching is frequently exact, which is a strong prerequisite for a credible fact-checking layer. Remaining “likely/possible” cases should be audited because claim units must be tied to exact internal sources.

### 8.3 Dominant Failure Modes in Current Extraction/Labeling

Top failure mode patterns (from `failure_modes.csv`) are dominated by missing tone / schema issues:

- `missing_tone` (and combinations with `schema_drift`, `hedged_or_modal_language`, `table_or_numeric_layout`)

Interpretation: the primary bottleneck today is not external evidence retrieval—it is internal statement normalization and consistent claim typing. If “tone” (commitment/action/outcome) is missing or unstable, then fact-check evaluation by claim type will be unreliable until the claim schema stabilizes.

### 8.4 What These Results Enable (and What They Don’t)

Enabled now:

- A validated internal provenance substrate for claims
- A measured list of failure modes to target before building verdict evaluation

Not enabled yet:

- External evidence retrieval performance measurement
- Supported/contradicted/insufficient verdict evaluation against ground truth

---

## 9. Discussion

### 9.1 Why a Fact-Checking Layer Matters for ESG

ABSA and tone/sentiment can characterize how disclosures are framed, but do not address **accountability**. A fact-checking layer converts disclosures into verifiable claims with traceable evidence trails and allows:

- identifying contradictions with regulators/credible news
- flagging unverifiable claims (potential “PR-only” claims)
- prioritizing claims for manual audit based on confidence and evidence quality

### 9.2 Expected Challenges (Indonesia + Multimodality)

1. **Entity mismatch**: company name variants and subsidiaries can drive false contradictions.
2. **Temporal mismatch**: claims may refer to a different year than evidence; time resolution must be explicit.
3. **Hedged language**: commitments (“will”, “aim to”) are not falsifiable in the same way as outcomes; they need different evaluation rules.
4. **Source noise**: social media increases coverage but can reduce reliability; credibility weighting is required.
5. **Visual ambiguity**: images/tables in PDFs and news posts require OCR and careful alignment to the claim being verified.

### 9.3 Interpretation Boundary

This work should explicitly distinguish:

- “**insufficient evidence**” from “false”
- “contradicted” from “different time period / entity”
- internal extraction errors vs external retrieval errors vs reasoning errors

Without this separation, the system can appear worse than it is, or worse, can report confident but ungrounded verdicts.

---

## 10. Conclusion

Multimodal fact-checking for Indonesian ESG ABSA is feasible in this repository because prerequisites already exist: internal claim extraction artifacts, provenance verification evidence, OCR processing tracking, and operational stability summaries.

The major missing component is **external evidence ingestion and retrieval**, followed by rigorous evaluation of **verdict accuracy and citation fidelity**. Implementing this will transform the repository from “what companies say” into “what can be externally supported or contradicted,” enabling stronger ESG accountability analysis.

---

## Appendix A: Implementation Anchors in This Repo

- Fact-checking research-plan prototype: `fact_checking/app.py`
- Feasibility framing baseline: `documentation_fact_checking.md`
- Grounding datasets: `results/revision_analysis/`

## Appendix B: Recommended Next Implementation Steps (Practical Order)

1. Define canonical claim schema derived from existing ABSA outputs (and enforce internal provenance).
2. Build `results/fact_checking/` artifact structure:
   - `claims.csv`, `evidence.csv`, `verdicts.csv`, `eval_summary.json`
3. Implement external evidence ingestion and indexing:
   - news/regulator/NGO sources first (higher credibility), then social/video/image
4. Implement retrieval + filtering (entity/date/credibility)
5. Implement reasoning/verdict module (start text-only; then add multimodal fusion)
6. Add human adjudication subset + evaluation scripts
7. Extend Streamlit UI to display claim cards + evidence bundles + verdict metrics

