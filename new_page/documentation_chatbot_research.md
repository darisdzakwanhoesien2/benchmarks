# Chatbot Research Track — Indonesian ESG ABSA (Repo-Integrated Study)

Date: 2026-05-30

This document turns the existing **chatbot feasibility plan** in this repository into a complete, thesis-style **chatbot research track**. It is written to be executable and auditable against code and artifacts already present in the repo.

**Repo anchors (what exists today)**
- Chatbot research-plan Streamlit app (planner + dataset evidence): `chatbot/app.py`
- Chatbot feasibility framing (existing): `documentation_chatbot.md`
- Revision-analysis datasets (used for grounding/evidence metrics in the planner):
  - `results/revision_analysis/pilot_ground_truth_annotations.csv`
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv`
  - `results/revision_analysis/failure_modes.csv`
  - `results/revision_analysis/prompt_stability_summary.csv`
  - `results/revision_analysis/model_stability_summary.csv`
  - `results/revision_analysis/ontology_coverage.csv`
- Upstream pipeline modules referenced in the feasibility doc:
  - OCR + processing: `pages/Bulk_OCR.py`, `pages/llm_processing.py`
  - Validation: `pages/2_2_LLM_Statement_Page_Verifier.py`, `pages/1_3_Ground_Truth_Metrics.py`
  - Ontology/graph: `pages/1_6_Ontology_Path_Viewer.py`, `pages/1_13_Semantic_Graph_Exporter.py`

---

## 1) Research Gap

This repository already provides a strong “evidence layer” for Indonesian ESG ABSA:
- OCR ingestion and text/table extraction
- structured record generation for ESG statements
- ontology coverage / mapping
- audit and verification pages + failure-mode tracking

However, there is a clear gap between **structured analysis artifacts** and an **interactive conversational interface**:

1. **Non-conversational delivery**: current workflows are page/dashboard oriented rather than query-driven conversation.
2. **Weak real-time grounding exposure**: even when evidence exists (verifier rows, failure modes), users cannot consistently see citations/evidence while interacting.
3. **No chatbot benchmark harness in-repo**: there is no standard evaluation protocol for a chatbot answering Indonesian ESG ABSA questions (faithfulness, ABSA consistency, safety, repeated-query stability).
4. **ABSA semantics under dialogue is under-specified**: preserving aspect/pillar/sentiment/tone across follow-up questions, clarifications, and aggregation is not yet implemented or evaluated.

In short, the gap is not “add a chat UI,” but “add a chatbot layer that is **grounding-first**, **ABSA-consistent**, and **benchmarkable** using the repo’s existing verification and stability artifacts.”

---

## 2) Research Questions

RQ1 (Feasibility). Can a chatbot built on existing repository artifacts answer Indonesian ESG ABSA questions accurately, with verifiable evidence, under realistic user queries?

RQ2 (Architecture). Which architecture performs best given the repo’s artifacts and constraints: (a) direct prompt-over-records, (b) retrieval-augmented generation (RAG) over statements/pages, or (c) a workflow-guided hybrid router?

RQ3 (ABSA semantics). How reliably can the chatbot preserve ABSA semantics in conversation (aspect, ESG pillar, sentiment, tone/commitment) across multi-turn dialogue and aggregation requests?

RQ4 (Failure modes & mitigation). What are the dominant failure modes in Indonesian ESG ABSA chatbot outputs, and which controls mitigate them without degrading usability?

RQ5 (Stability). How stable are chatbot answers under repeated prompts, minor paraphrases, and model/prompt configuration changes, using the repo’s existing stability summaries as diagnostic signals?

---

## 3) Research Objectives

O1. Build a reproducible chatbot layer over existing ESG ABSA outputs and revision-analysis artifacts.

O2. Support Indonesian-language queries for:
- company summaries and comparisons
- aspect/pillar-level evidence retrieval
- tone/commitment and sentiment interpretation
- ontology-aware explanations (“why is this aspect under E/S/G?”)

O3. Require source-grounded responses:
- each substantive claim is backed by retrieved evidence (record/page/snippet)
- responses expose citations and allow “show evidence” expansions

O4. Evaluate chatbot quality with a task-specific protocol:
- relevance and completeness
- factuality / faithfulness to evidence
- ABSA semantic consistency
- citation presence and citation correctness
- robustness (repeated-query stability, ambiguity handling, out-of-scope behavior)

O5. Integrate outputs into thesis/dashboard reporting:
- export logs and evaluation tables under `results/chatbot/`
- summarize findings for thesis chapters (methods + evaluation + error analysis)

---

## 4) Expected Research Contributions

1. **Evidence-grounded Indonesian ESG ABSA chatbot architecture** that reuses repo artifacts (records, verifier outputs, ontology coverage).
2. **ABSA-to-dialogue translation method**: converting structured ABSA evidence into conversational answers while preserving aspect/pillar/tone constraints.
3. **Chatbot evaluation harness** emphasizing faithfulness + auditability, not just fluency.
4. **Failure-mode taxonomy for conversational ESG analytics**, aligned with existing `failure_modes.csv` but extended for dialogue-specific errors (follow-up drift, aggregation hallucinations, citation mismatch).
5. **Reusable research artifacts** (`results/chatbot/*`) for future work, including query sets, logs, labels, and regression tests.

---

## 5) Literature Review (Focused)

This literature review is written as a *targeted map* for thesis grounding and implementation decisions. It is organized by questions this repo must answer rather than by an exhaustive survey.

### 5.1 Retrieval-Augmented and Tool-Using Chatbots (Domain QA)

Key ideas to cover:
- why retrieval and external evidence reduce hallucination risk
- design choices: chunking, indexing units (pages vs statements), reranking, and evidence selection
- how “citation-first” prompting changes answer behavior and evaluation

Relevance to this repo:
- the repo already has statement/page-level structures and verifiers; RAG can retrieve “candidate evidence” for chatbot answers rather than asking the model to infer.

### 5.2 Faithfulness, Hallucination, and Citation-Grounded Generation

Key ideas to cover:
- known hallucination failure modes in generative models
- factuality metrics and evidence-backed evaluation paradigms
- how to design prompts that (a) refuse unsupported claims and (b) surface uncertainty

Relevance to this repo:
- the revision-analysis datasets already capture failure modes and verifier outcomes; the chatbot should reuse that discipline at interaction time.

### 5.3 Aspect-Based Sentiment Analysis (ABSA) Under Interaction

Key ideas to cover:
- preserving aspect and sentiment labels during summarization/explanation
- aggregation pitfalls (averaging across companies/time periods, mixing aspects)
- interpretability expectations for sentiment/tone in applied settings

Relevance to this repo:
- users will ask “why is this negative?” or “compare companies,” which require aggregation logic that respects ABSA constraints.

### 5.4 Multilingual/Indonesian Conversational NLP + Domain Terminology

Key ideas to cover:
- handling Indonesian queries, code-switching, and domain-specific ESG vocabulary
- query normalization, synonym mapping, and ontology-aligned terminology

Relevance to this repo:
- Indonesian ESG queries can include English ESG terms; the chatbot must normalize and map to internal aspect/ontology labels.

### 5.5 Evaluation Frameworks for Conversational Systems

Key ideas to cover:
- why “helpfulness” is insufficient without faithfulness
- evaluation decomposition: retrieval quality, answer quality, citation quality, safety/refusals
- human evaluation design for domain QA (supported/unsupported/contradicted)

Relevance to this repo:
- evaluation can be grounded in existing verifier rows and failure mode analysis patterns; the key is to formalize the benchmark protocol and exports.

---

## 6) Methodology

### 6.1 Data and Evidence Sources (Already in Repo)

This track treats the repo as a benchmark and uses existing artifacts as evidence sources:
- `results/revision_analysis/pilot_ground_truth_annotations.csv` for labeled snapshots (e.g., tone/sentiment labels and company-level coverage)
- `results/revision_analysis/llm_statement_page_verifier_compiled.csv` for evidence matching and “status” distributions
- `results/revision_analysis/failure_modes.csv` for error taxonomy bootstrapping
- `results/revision_analysis/ontology_coverage.csv` for aspect/pillar mapping coverage and gaps
- `results/revision_analysis/prompt_stability_summary.csv` and `results/revision_analysis/model_stability_summary.csv` for robustness diagnostics

### 6.2 System Designs to Compare (Three Architectures)

**A1: Direct prompt-over-records**
- Select a subset of structured records based on the user query and pass them to the model.
- Pros: fast to prototype.
- Risks: context overflow, weak citation correctness, fragile under aggregation.

**A2: RAG over statements/pages**
- Retrieve top-k evidence items (statements/pages/snippets) via lexical + semantic search.
- Force the answer to only use retrieved evidence and cite it.
- Pros: stronger traceability.
- Risks: retrieval errors become dominant; requires careful indexing and chunking.

**A3: Hybrid workflow-guided router**
- Classify intent (e.g., “company summary,” “tone justification,” “ontology explanation,” “comparison,” “out-of-scope”).
- Route to specialized handlers with constrained output formats.
- Pros: best for ABSA consistency and safe aggregation.
- Risks: engineering complexity, more components to evaluate.

### 6.3 Indonesian Query Handling

Minimum viable language pipeline:
1. Normalize query (typos, casing, punctuation).
2. Detect/translate key ESG terms (code-switching) using a synonym table aligned with ontology/aspect labels.
3. Clarify ambiguity (company, time range, aspect scope) via short follow-up questions.
4. Enforce response language policy (default Indonesian, but quote evidence verbatim if needed).

### 6.4 Evaluation Protocol (Offline + In-App)

This track evaluates **both** the retrieval layer and the generation layer.

**Offline benchmark set**
- Build a query set representative of Indonesian ESG ABSA use cases:
  - company-specific: “Apa isu lingkungan terbesar untuk Perusahaan X?”
  - aspect justification: “Buktinya apa?”
  - comparisons: “Bandingkan X vs Y pada aspek emisi.”
  - robustness: paraphrases, repeated questions, out-of-scope prompts

**Metrics**
- Relevance/utility (human or rubric-based)
- Faithfulness:
  - “supported / unsupported / contradicted” labels at claim level (recommended)
  - citation presence rate
  - citation correctness rate (does cited item actually support the claim?)
- ABSA semantic consistency:
  - aspect/pillar preservation
  - tone/sentiment alignment with evidence
- Robustness:
  - repeated-query consistency
  - prompt/model configuration sensitivity (reuse existing stability summaries)

### 6.5 Reproducibility Outputs (Where to Save)

Create and standardize exports under `results/chatbot/`:
- `queries.jsonl` (query set + metadata)
- `runs.jsonl` (model/prompt config + retrieved evidence IDs + answer text + citations)
- `labels.csv` (human or rubric labels)
- `metrics.csv` (aggregated metrics by architecture/config)
- `failure_modes_chatbot.csv` (dialogue-specific failure taxonomy aligned with `results/revision_analysis/failure_modes.csv`)

---

## 7) Results (Current Repo State — What We Can Claim Today)

### 7.1 Implemented Components

As of 2026-05-30, the repo contains:
- a Streamlit research planner at `chatbot/app.py` that:
  - loads the revision-analysis datasets (if present)
  - displays dataset evidence snapshots
  - renders a structured research plan (gap → conclusion) for the chatbot track
- a feasibility write-up in `documentation_chatbot.md` that lists:
  - reusable infrastructure
  - candidate architectures
  - evaluation dimensions
  - integration plan

### 7.2 Available Evidence and Diagnostics (Not Yet a Chatbot Result)

The revision-analysis datasets provide:
- ground-truth labeling snapshots (pilot)
- statement-page verification outcomes (verifier)
- failure-mode patterns
- prompt/model stability summaries
- ontology coverage tables

These artifacts are necessary prerequisites for an auditable chatbot benchmark, but they are **not** yet equivalent to chatbot performance results because there is not yet:
- an implemented chatbot module
- a `results/chatbot/` run log
- architecture comparisons with metrics
- human evaluation labels for faithfulness and usefulness

### 7.3 Missing Results (Research To Be Completed)

To complete the research track, the repo still needs:
- an actual chatbot implementation (at least one architecture)
- a reproducible query set and evaluation harness
- quantitative metrics and tables
- an error analysis section based on observed chatbot failures (not only pipeline failures)

---

## 8) Discussion (What This Track Will Likely Reveal)

This section frames the thesis discussion once results exist.

1. **Interactivity vs. auditability tradeoff**: conversational answers increase accessibility, but also raise the bar for evidence traceability (citations must be correct at claim level).
2. **Retrieval as the critical bottleneck**: even strong generators cannot be faithful if evidence retrieval fails; retrieval evaluation must be first-class.
3. **ABSA aggregation is fragile**: “compare companies” and “summarize trends” queries can induce unsupported generalizations; hybrid routing with explicit aggregation rules will likely be necessary.
4. **Stability matters**: the repo already emphasizes prompt/model stability; chatbot answers should be assessed for variance under paraphrase and config changes.
5. **Upstream data quality remains limiting**: OCR and extraction errors propagate; chatbot should expose uncertainty and provide evidence panels rather than hiding imperfections.

---

## 9) Conclusion

An Indonesian ESG ABSA chatbot is feasible in this repository because the evidence and diagnostic layers already exist (records, verifiers, stability summaries, failure modes, ontology coverage). The research contribution becomes thesis-grade when the repo adds (1) an implemented grounding-first chatbot, (2) a benchmark query set with repeatable runs, and (3) evaluation tables and failure analysis demonstrating faithfulness and ABSA consistency under real interaction.

---

## Next Implementation Steps (Recommended Order)

1. Implement a minimal chatbot module (start with RAG + citations):
   - `code/chatbot_esg_absa.py` (retrieval + answer formatting + citation schema)
2. Create `results/chatbot/` and the run-log schema (`queries.jsonl`, `runs.jsonl`).
3. Add a Streamlit chat UI page with evidence panel:
   - e.g., `pages/2_7_Chatbot_ESG_ABSA.py` (or similar page numbering pattern)
4. Add evaluation scripts:
   - automatic checks (citation presence/correctness proxies, ABSA label consistency)
   - small human label set for faithfulness
5. Populate “Results” with real numbers and tables in this document and in thesis chapters.

