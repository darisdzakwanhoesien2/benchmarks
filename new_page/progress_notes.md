# Progress Notes — Research Tracks (ESG ABSA Benchmark)

Date: 2026-05-30

This file tracks what has been completed in the repo across research tracks and what to do next. It is intentionally “execution-first”: each item should be traceable to a file path in the repo.

---

## Track: Summarization (Indonesian ESG ABSA)

### What has been done

- Confirmed a working summarization workspace exists:
  - `summarization/app.py` implements three extractive baselines (Lead, frequency, TextRank-like) and optional ROUGE-1/2/L evaluation (when a reference summary is provided).
- Confirmed formal “summarization track” framing existed but was not consolidated as a thesis-style write-up:
  - `documentation_summarization.md` contains an initial gap/questions/objectives/method outline.
- Added a complete research write-up document for summarization:
  - `documentation_summarization_research.md` consolidates research gap, RQs, objectives, contribution, literature review, methodology, results/discussion/conclusion, repo anchors, and next steps.
- Verified available upstream evidence metrics that summarization can build on:
  - `results/thesis_workflow_dashboard/dashboard_metrics.json` (e.g., OCR docs=23, tone records=332, T2 rows=2074).
  - `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv` (percent agreement=0.8373; kappa=0.6451).

### Current blockers / risks

- Local Python environment is missing dependencies required to run the Streamlit summarization app locally (e.g., `pandas`), so we cannot compute additional stats in this environment without installing packages.
- The scite MCP literature tool is unavailable (monthly limit reached), so citations were collected via web sources instead of full-text MCP excerpts.

### What we need to do next (recommended order)

1. Standardize summarization outputs:
   - Create `results/summarization/` and export summary units + metadata (JSONL/CSV).
2. Implement ABSA-guided summarization:
   - Build “evidence scaffold” per aspect/pillar before any abstractive step.
3. Add faithfulness evaluation:
   - Start with evidence-span support checks; then integrate stronger factuality methods (e.g., FactCC/QAGS/SummaC-style approaches).
4. Add a small human evaluation set:
   - Label faithfulness + utility for a sample of summaries; store labels under `results/summarization/`.
5. Integrate into dashboards:
   - Extend the Streamlit UI to read and audit `results/summarization/*` outputs.

---

## Track: Social Network Analysis (ESG Disclosure Networks)

### What has been done

- Identified existing SNA codebase under `social_network_analysis/`:
  - `social_network_analysis/app.py` implements a corpus-wide section-level graph scan over `data/thesis_dataset/*/ocr_result.json`.
  - The graph design is: **nodes = report sections**, **edges = shared high-frequency entities/terms**, edge weight = shared entity count.
  - Computes core metrics and artifacts in-memory: degree centrality, betweenness (sampled), greedy modularity communities, density, average degree, pillar composition, and a “risk_score” heuristic (positivity vs metric density).
- Confirmed the OCR dataset exists and is non-trivial:
  - `data/thesis_dataset/` contains 189 documents with `ocr_result.json` pages including `markdown`, `tables`, and `images`.
- Confirmed research framing already exists in the repo:
  - `documentation_social_network_analysis.md` contains initial gap/questions/objectives/method discussion.
  - `social_network_analysis/task_data.py` lists tasks, including a literature-review task.
- Added a complete thesis-style research write-up document:
  - `documentation_social_network_analysis_research.md` consolidates research gap, RQs, objectives, contribution, literature review plan, methodology, results plan, discussion, conclusion, and repo anchors.
- Added an offline (non-Streamlit) runner to export SNA artifacts:
  - `social_network_analysis/run_corpus_scan.py` writes `results/social_network_analysis/` outputs (CSV/JSON/GEXF).
  - Note: execution currently fails due to missing `networkx`/`pandas` in the system python environment.

---

### Current blockers / risks

- Python dependencies are not installed in the base system environment:
  - Running `python3 social_network_analysis/run_corpus_scan.py ...` fails with `ModuleNotFoundError: networkx`.
- Creating a full `.venv` using `requirements.txt` failed due to **disk space** constraints (root filesystem ~99% full). Installing the whole requirements set also pulls very large CUDA/Torch packages.
- scite MCP literature tool is unavailable (monthly limit reached), so peer-reviewed citations could not be imported directly through the MCP tool.

---

### What we need to do next (recommended order)

1. Get a minimal Python environment working for SNA export:
   - Create a small venv that installs only: `networkx`, `pandas` (and optionally `pyarrow`).
   - Avoid `requirements.txt` because it includes heavy GPU/CUDA stacks.
2. Run the corpus scan and generate results artifacts:
   - `python3 social_network_analysis/run_corpus_scan.py --thesis-dataset-dir data/thesis_dataset --output-dir results/social_network_analysis`
   - Confirm `results/social_network_analysis/summary.json`, `nodes.csv`, `edges.csv` exist.
3. Populate the **Results** section with real numbers:
   - Copy key summary statistics and top tables into `documentation_social_network_analysis_research.md`.
   - Add a small “Results Snapshot” table (nodes, edges, density, top year, pillar distribution).
4. Add robustness checks:
   - Re-run scan at different thresholds (shared entities >= 1/2/3) and compare stability of top hubs/bridges.
5. Optional: Integrate outputs into Streamlit UI:
   - Add a page that reads `results/social_network_analysis/*.csv` rather than recomputing on the fly.
6. Literature citations:
   - Add citations for centrality/community detection/text-as-network methods using your bibliography approach (BibTeX, Zotero, manual list).

---

### Where to look

- SNA research write-up: `documentation_social_network_analysis_research.md`
- SNA implementation: `social_network_analysis/app.py`
- Offline exporter: `social_network_analysis/run_corpus_scan.py`
- OCR corpus: `data/thesis_dataset/`

---

## Track: Topic Modelling (Indonesian ESG Disclosures)

### What has been done

- Confirmed a working topic-modelling workspace exists:
  - `topic_modelling/app.py` performs corpus-wide scan and exploratory diagnostics over `data/thesis_dataset/*/ocr_result.json` (coverage by year, sector proxy, pillar keyword signals, tone-vs-metric proxy scatter, and a narrative-risk shortlist).
  - `topic_modelling/task_data.py` defines the topic-modelling and cluster-interpretation tasks (including LDA/BERTopic and temporal topic evolution tasks).
  - `topic_modelling/pages/1_Phase_1_Data_Preparation.py` includes a formal research frame (gap, RQs, objectives, contributions, expected results).
- Verified upstream labeled text artifacts exist that can be used as a statement-level topic modelling corpus:
  - `results/esg_records.json` contains extracted `records[*].text` plus labels (`aspect`, `esg`, `tone`, `sentiment`).
- Added a complete thesis-style research write-up document for topic modelling:
  - `documentation_topic_modelling_research.md` consolidates research gap, RQs, objectives, contribution, literature review outline, methodology, results snapshot (based on existing corpus counts), discussion, conclusion, repo anchors, and next steps.
- Added local workspace progress notes for the track:
  - `topic_modelling/progress_notes.md`

### Current blockers / risks

- Topic modelling dependencies (e.g., `gensim`, `scikit-learn`, `sentence-transformers`, `bertopic`) may not be installed and may be difficult to install due to disk constraints noted in other tracks.
- scite MCP literature tool is unavailable (monthly limit reached), so peer-reviewed citations are not yet embedded via full-text excerpts.

### What we need to do next (recommended order)

1. Implement an offline topic modelling exporter:
   - Add `topic_modelling/run_topic_models.py` to build corpora (statement-level from `results/esg_records.json`, and optionally chunked OCR) and write standardized outputs to `results/topic_modelling/`.
2. Normalize labels for alignment evaluation:
   - Canonicalize pillar/tone/sentiment strings (handle `none`, mixed labels, nulls) before computing topic-to-label distributions.
3. Run baseline models first:
   - LDA/NMF on the statement corpus to generate interpretable baseline topics.
4. Add alignment + stability metrics:
   - Export topic coherence/diversity + topic-to-aspect/pillar mapping tables.
5. Integrate exported outputs into Streamlit:
   - Add a page under `topic_modelling/pages/` that reads `results/topic_modelling/*` and visualizes topics + alignment heatmaps.

## Track: Fine-Tuning (Indonesian ESG ABSA)

### What has been done

- Confirmed a fine-tuning research planner UI exists and is wired to repo artifacts:
  - `fine_tuning/app.py` renders research gap/RQs/objectives/contribution/literature topics/method outline and reads evidence from `results/revision_analysis/*`.
- Confirmed existing evidence sources and basic corpus readiness:
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` contains 5,444 labeled rows and key targets (`ground_truth_aspect`, `ground_truth_esg`, `ground_truth_tone`, `sentiment`) plus provenance fields (`company`, `model`, `prompt`).
  - `results/revision_analysis/model_stability_summary.csv` and `results/revision_analysis/prompt_stability_summary.csv` provide stability context for reproducibility claims.
- Confirmed an executable validation hook exists for ClimateBERT-logic proxy labeling:
  - CLI runner: `fine_tuning/call_climatebert_logic.py` writes to `results/fine_tuning/climatebert_logic_from_ground_truth.csv`.
  - UI validator: `fine_tuning/app.py` can sample ground-truth rows, call the API, compare fields, and export `results/fine_tuning/climatebert_api_validation_latest.csv`.
- Added a complete thesis-style research write-up for the fine-tuning track:
  - `documentation_fine_tuning_research.md` consolidates research gap, RQs, objectives, contribution, literature review plan, methodology, current results state, discussion, conclusion, and repo-anchored next steps.

### Current blockers / risks

- Python environment is missing common data-science dependencies (e.g., `pandas`), which prevents quick local EDA and makes it harder to package a canonical dataset via scripts in this environment.
- High leakage risk if splits are done at row level:
  - `pilot_ground_truth_annotations.csv` is heavily clustered by `company` and is derived from a pipeline with templated report sections; train/test separation must be company/report-level.
- Label-quality risks that must be explicitly handled:
  - Pillar labels include mixed forms (e.g., `e-s-g`, `e-s`) that require harmonization or multi-label treatment.
  - Sentiment is imbalanced (neutral/positive dominate; negative is rare), requiring careful metrics and class-imbalance controls.

### What we need to do next (recommended order)

1. Build the canonical dataset artifact:
   - Create `results/fine_tuning/labels_master.csv` from `results/revision_analysis/pilot_ground_truth_annotations.csv`.
   - Define stable IDs, canonical label mappings, and basic filtering rules (missing/blank text, unusable labels).
2. Implement leakage-aware deterministic splits:
   - Write `results/fine_tuning/splits.json` that splits by `company` (and/or report ID).
   - Keep the split seed and logic fixed for reproducibility.
3. Implement training + evaluation runner integrated with the repo:
   - Add `code/fine_tuning_esg_absa.py` to run full fine-tuning and PEFT comparisons (configurable).
   - Export predictions + metrics + confusion matrices + subgroup tables under `results/fine_tuning/`.
4. Add a results visualization page:
   - Create a Streamlit page under `pages/` that reads `results/fine_tuning/*` artifacts and displays comparisons vs existing baselines.
5. Populate the Results section with real metrics:
   - Aggregate + per-class + subgroup + repeated-seed stability, and an error taxonomy.

---

## Track: Chatbot (Indonesian ESG ABSA)

### What has been done

- Confirmed a working chatbot research-plan app exists:
  - `chatbot/app.py` renders a structured research plan (gap → conclusion) and grounds it with revision-analysis CSVs when present.
- Confirmed feasibility framing exists and is repo-aligned:
  - `documentation_chatbot.md` defines the gap, RQs, objectives, architecture options, evaluation dimensions, and integration plan.
- Added a complete thesis-style research write-up for the chatbot track:
  - `documentation_chatbot_research.md` consolidates research gap, RQs, objectives, expected contributions, literature review map, methodology, results-status, discussion framing, and next steps.

### Current blockers / risks

- There is not yet an implemented chatbot module (retrieval + answer + citation schema) in `code/`, so the track currently provides *research framing* rather than measurable chatbot performance results.
- The repo does not yet have standardized chatbot evaluation artifacts under `results/chatbot/` (query set, run logs, labels, metrics).
- Python environment constraints may affect running new evaluation scripts (dependency availability); keep initial implementations lightweight and scoped.

### What we need to do next (recommended order)

1. Implement the minimal chatbot core (start with RAG + citations):
   - Add `code/chatbot_esg_absa.py` with retrieval + response formatting + citation structure.
2. Standardize evaluation artifacts:
   - Create `results/chatbot/` and define `queries.jsonl` + `runs.jsonl` schemas.
3. Build a small benchmark query set:
   - Include Indonesian queries for company summary, aspect justification (“buktinya?”), comparisons, and out-of-scope prompts.
4. Add offline evaluation checks:
   - Citation presence + citation correctness proxy checks.
   - ABSA semantic consistency checks (aspect/pillar/tone alignment with evidence).
5. Add a Streamlit chat UI page (optional but recommended):
   - A chat interface with a “show evidence” side panel to inspect retrieved statements/pages.

---

## Track: Fact-Checking (Indonesian ESG ABSA)

### What has been done

- Confirmed existing fact-checking prototype exists:
  - `fact_checking/app.py` is a Streamlit app that renders a structured research plan (gap → RQs → objectives → contributions → literature topics → methodology → results interpretation → discussion → conclusion).
  - It also grounds feasibility using revision-analysis datasets under `results/revision_analysis/`.
- Confirmed baseline feasibility document exists:
  - `documentation_fact_checking.md` defines the research framing and a practical implementation roadmap.
- Verified the available revision-analysis datasets used for grounding are present and non-trivial (as of 2026-05-30):
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` (5,444 rows)
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv` (332 rows; `best_status` mostly `exact`)
  - `results/revision_analysis/failure_modes.csv` (62 rows; dominated by `missing_tone`-related patterns)
  - `results/revision_analysis/prompt_stability_summary.csv` (7 rows)
  - `results/revision_analysis/model_stability_summary.csv` (6 rows)
  - `results/revision_analysis/ocr_processing_summary.csv` (23 rows)
- Added a complete thesis-style fact-checking research write-up:
  - `documentation_fact_checking_research.md` consolidates research gap, RQs, objectives, contribution, literature review focus, methodology, current results/readiness evidence, discussion, conclusion, and repo anchors.

### Current blockers / risks

- External evidence ingestion and retrieval are not implemented yet:
  - Current artifacts validate internal provenance and extraction risks, but do not verify truthfulness against external sources.
- Canonical claim schema is not enforced as an output artifact:
  - There is no `results/fact_checking/claims.csv` with stable `claim_id` + `time_reference` + `internal_provenance`.
- Verdict evaluation is not yet possible:
  - No adjudicated ground-truth verdict set exists for `supported/contradicted/insufficient_evidence`.
- Literature citations are not yet embedded as a formal bibliography:
  - The write-up is structured, but citations need to be added using your standard thesis workflow (Zotero/BibTeX/manual list).

### What we need to do next (recommended order)

1. Define a canonical claim unit schema and export a first `claims.csv`:
   - Derive from existing internal statements/records and enforce:
     - `claim_id`, `company`, `claim_text`, `claim_type`, `time_reference`, `internal_provenance`
   - Save under `results/fact_checking/claims.csv`.
2. Implement external evidence ingestion connectors (start with high-credibility sources):
   - News / regulator / NGO sources first (text + publish date + URL).
   - Add optional social/video/image later with credibility weighting.
3. Implement retrieval + ranking with hard constraints:
   - entity disambiguation (company variants)
   - time-window filtering (avoid cross-year false contradictions)
   - source credibility weights (domain/type)
4. Implement a minimal text-only verifier first:
   - NLI-style verdicting over top-k evidence and strict evidence citation in every verdict.
5. Create an adjudication/evaluation subset:
   - Sample claims across pillars + claim types.
   - Label evidence relevance and verdict ground truth.
   - Compute macro-F1, confusion matrix, and citation fidelity.
6. Extend `fact_checking/app.py` to display real outputs:
   - Read `results/fact_checking/*.csv` to show claim cards, evidence bundles, verdict summaries, and error analysis.
7. Add citations + bibliography:
   - Add citations for fact-checking pipelines, NLI verification, multimodal verification, and credibility modeling.

### Where to look

- Fact-checking app: `fact_checking/app.py`
- Feasibility doc: `documentation_fact_checking.md`
- Full research write-up: `documentation_fact_checking_research.md`
- Grounding datasets: `results/revision_analysis/`

---

## Track: LLM-as-a-Judge (ESG ABSA Extraction Evaluation)

### What has been done

- Confirmed the LLM-as-a-judge workspace exists and is usable as a Streamlit explorer:
  - `llm_as_a_judge/app.py` loads `results/esg_records.json`, flattens run/record tables, shows distributions, and supports record browsing.
- Confirmed a baseline research plan exists:
  - `llm_as_a_judge/research_plan.md` defines the research gap, RQs, objectives, contributions, rubric outline, and methodology.
- Verified the primary dataset is present and non-trivial (as of 2026-05-30):
  - `results/esg_records.json` contains 1,012 runs, 658 OK runs, 544 runs with records, and 5,112 extracted records.
- Added a complete thesis-style research write-up for this track:
  - `documentation_llm_as_a_judge_research.md` consolidates gap → RQs → objectives → contributions → literature focus → methodology → results/readiness evidence → discussion → conclusion.
- Added track-local progress tracking:
  - `llm_as_a_judge/progress_notes.md` (this folder) records what exists and what to implement next.

### Current blockers / risks

- Judge outputs are not generated yet:
  - `results/llm_judge/judge_records.jsonl` and `results/llm_judge/judge_summary.csv` do not exist by default, so no judge reliability/validity results can be reported yet.
- A judge execution pipeline is not implemented in this repo area:
  - Current code is an explorer + research framing; the end-to-end judge runner must be added next.

### What we need to do next (recommended order)

1. Implement an offline judge runner:
   - Add a script (e.g., `llm_as_a_judge/run_judging.py`) that reads `results/esg_records.json` and writes `results/llm_judge/*`.
2. Define and version the judge rubric prompt:
   - Store rubric templates and explicitly version them for ablations (rubric v1/v2).
3. Add reliability experiments:
   - Self-consistency reruns (same judge, N repeats) and (optional) multi-judge comparisons for disagreement analysis.
4. Add analysis exports:
   - Produce `judge_summary.csv` and (optional) `judge_disagreement.csv` for manual review sampling.
5. Add a small human evaluation subset:
   - Stratified sample labeling (faithfulness/completeness/tone validity) to calibrate and validate judge thresholds.
