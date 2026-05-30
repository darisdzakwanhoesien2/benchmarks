codex resume 019e7865-f984-7d90-9e36-820c899a107b
# Progress Notes — Topic Modelling (local workspace)

Date: 2026-05-30

This file tracks progress specifically inside `topic_modelling/` and links work to concrete repo paths.

---

## What has been done

- Confirmed the topic-modelling workspace exists and is wired for a phase/task UI:
  - `topic_modelling/app.py` (Streamlit entry, corpus scan, dataset-level charts)
  - `topic_modelling/task_data.py` (phase/task definitions; includes topic modelling tasks)
  - `topic_modelling/ui.py` (shared UI helpers)
  - `topic_modelling/pages/1_Phase_1_Data_Preparation.py` (research frame: gap, RQs, objectives, contributions)
- Confirmed the OCR dataset is present and large enough for topic modelling experiments:
  - `data/thesis_dataset/*/ocr_result.json`
- Confirmed ABSA-like extracted statement records exist and are suitable as a smaller “topic modelling unit”:
  - `results/esg_records.json` (contains `records[*].text` + labels like `aspect`, `esg`, `tone`, `sentiment`)
- Added a thesis-style research write-up for this track:
  - `documentation_topic_modelling_research.md`

---

## What we need to do next (recommended order)

1. Build a reproducible topic-modelling corpus exporter (offline runner)
   - Add a script (suggested): `topic_modelling/run_topic_models.py`
   - Inputs:
     - `results/esg_records.json` (statement corpus)
     - optionally `data/thesis_dataset/*/ocr_result.json` (OCR corpus, chunked)
   - Outputs (suggested):
     - `results/topic_modelling/` with corpus manifest + topic tables + doc-topic matrices

2. Normalize and clean labels for alignment evaluation
   - Canonicalize `esg` pillar strings (E/S/G/mixed/none) into stable categories.
   - Canonicalize tone and sentiment values (handle `none`, nulls, and mixed strings).

3. Implement two modelling baselines + one embedding-based model
   - Baselines: LDA and/or NMF on the statement corpus first (fast and interpretable).
   - Embedding-based: BERTopic-style pipeline for bilingual semantics (if deps allow).

4. Implement evaluation exports
   - Intrinsic: coherence, diversity, stability.
   - Extrinsic: topic-to-aspect/pillar distributions; topic sentiment/tone profiles.

5. Integrate results into Streamlit pages (read from exported outputs)
   - Add a page under `topic_modelling/pages/` that loads `results/topic_modelling/*` and visualizes:
     - topic keywords, exemplars
     - topic prevalence by year/sector/pillar
     - alignment heatmaps (topics × aspects/pillars)

---

## Risks / blockers

- Python dependencies for topic modelling may not be installed in the base environment (common issue in this repo due to disk constraints).
- Some models (transformer embeddings) may require large downloads; prefer minimal, staged installs or precomputed embeddings if disk is tight.

