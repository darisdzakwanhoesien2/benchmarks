# Topic Modelling Research Track (Indonesian ESG Sustainability Reports)

Date: 2026-05-30

This document is a thesis-style research write-up for the **Topic Modelling** track in this repository. It is anchored to existing code and datasets already present in the repo, and it is written to be executable: every key claim or step is traceable to a concrete file path.

> Scope note: this track is part of a broader ESG ABSA benchmark system. Topic modelling here is not treated as a standalone NLP demo; it is designed to **complement** the existing ABSA outputs and ontology/taxonomy artifacts in `results/` and `pages/`.

---

## 1) Research Gap

Indonesian sustainability-report NLP work typically faces three practical constraints: (1) the documents are long and heterogeneous, (2) the text is often **bilingual (Indonesian–English)** and **OCR-derived**, and (3) “topic modelling” is often reported as an isolated qualitative visualization without integration into a validated downstream task.

In this repository, the infrastructure to process and evaluate Indonesian ESG text exists (OCR ingestion, ABSA-like extraction, dashboards), and there is a dedicated `topic_modelling/` workspace. However, a complete topic-modelling research track is not yet fully operationalized end-to-end.

**Concrete gaps in this repo (what is missing / incomplete):**

1. **Topic modelling artifacts are not exported as standardized results.**
   - There is no `results/topic_modelling/` (or equivalent) containing reproducible topic tables, document-topic distributions, coherence/stability metrics, or topic-to-taxonomy mapping outputs.
2. **Topic-to-ABSA/ontology alignment is not implemented as a measurable evaluation step.**
   - ABSA outputs exist under `results/` (e.g., `results/esg_records.json`), but topic model outputs are not systematically compared against ABSA aspects/pillars/tone.
3. **Temporal topic dynamics (policy breakpoint framing) is planned but not executed.**
   - Task definitions call for pre/post comparisons around Indonesian sustainable finance policy timing (see `topic_modelling/task_data.py`), but no dynamic topic results are persisted yet.
4. **Bilingual/OCR-specific preprocessing is described but not built as a reusable corpus builder.**
   - Phase framing exists, but there is no canonical “topic modelling corpus” builder that outputs a single, versioned dataset for modelling.

---

## 2) Research Questions

RQ1. **Latent themes beyond ABSA**  
Can topic modelling uncover coherent, interpretable ESG themes in Indonesian sustainability-report text that are not captured by the repository’s predefined ABSA labels (aspect, ESG pillar, tone)?

RQ2. **Alignment with existing labels and taxonomy**  
To what extent do discovered topics align with existing ABSA outputs (aspect, pillar, sentiment, tone) and any ontology/taxonomy structures already used in the thesis workflow?

RQ3. **Method suitability for this corpus**  
Which topic-modelling approach is most effective for this data regime (bilingual + OCR + very long documents): classical probabilistic models (e.g., LDA), embedding-based models (e.g., BERTopic-like clustering), or hybrid constrained approaches?

RQ4. **Temporal and sectoral narrative shifts**  
How do topic prevalence, diversity, and drift change over time and across sector proxies, and can these dynamics improve interpretation of disclosure emphasis and potential greenwashing patterns?

---

## 3) Research Objectives

O1. Build a **reproducible topic-modelling corpus** from existing repo artifacts (OCR pages and/or ABSA records) with consistent metadata (company/year/sector/pillar).

O2. Implement at least two contrasting topic-modelling families and compare them:

- A bag-of-words probabilistic baseline (LDA/NMF).
- An embedding-based topic modelling approach (BERTopic-style clustering + topic representation).

O3. Define and compute an evaluation bundle that includes both intrinsic and extrinsic metrics:

- Intrinsic: topic coherence, redundancy/diversity, stability.
- Extrinsic: alignment to ABSA aspect/pillar labels; utility for interpreting sentiment/tone patterns.

O4. Persist standardized outputs to `results/topic_modelling/` so dashboards and thesis chapters can reuse them without re-running heavy computation.

O5. Produce thesis-ready evidence: figures, tables, and narrative interpretation for results/discussion/conclusion.

---

## 4) Research Contribution

This topic-modelling track contributes:

1. **A versioned “topic modelling corpus” layer** for Indonesian ESG reporting derived from OCR/ABSA artifacts, with reproducible preprocessing choices.
2. **Method comparison evidence** (probabilistic vs embedding-based) for bilingual/OCR ESG disclosures.
3. **A topic-to-ABSA/taxonomy mapping framework** that evaluates interpretability and external validity (topics should map meaningfully to existing ESG aspects/pillars).
4. **Temporal and sectoral narrative diagnostics** (topic concentration, emergence, drift) designed to complement existing disclosure-quality and greenwashing heuristics.
5. **Reusable topic artefacts** (topic word lists, representative texts, doc-topic matrices) that can be integrated into other repo tracks (dashboards, SNA, fact-checking, summarization).

---

## 5) Literature Review (Focused, Thesis-Oriented)

This literature review is organized as *streams of methods* and *streams of application*. It is intentionally focused on what is needed to justify methodological choices in this repo (not a generic survey).

### 5.1 Classical topic models (probabilistic / matrix factorization)

- **LDA-style models** provide interpretable topic-word distributions and document-topic mixtures, serving as a baseline for interpretability.
- **NMF** is a useful baseline alternative that sometimes yields sharper topics on TF-IDF representations, especially when documents are long and vocabularies are large.

Relevance to this repo: provides a baseline for comparing against embedding-based approaches, and supports coherent topic count selection via coherence or stability.

### 5.2 Embedding-based topic modelling

- Embedding-based methods cluster sentence/document embeddings and then derive topic representations (keywords and exemplars). They often perform better on multilingual or semantically nuanced corpora than pure bag-of-words.

Relevance to this repo: bilingual sustainability-report language (Indonesian + English, formal corporate phrasing, OCR artifacts) is expected to benefit from semantic representations.

### 5.3 Topic modelling under OCR noise and long-document regimes

- OCR artifacts, boilerplate, duplicated sections, and inconsistent formatting can degrade both coherence and interpretability unless preprocessing explicitly targets these issues.
- Long documents can overwhelm topic models if treated as a single unit; splitting into smaller “analysis units” (section/pillar/statement) is often necessary.

Relevance: this repo already uses OCR-derived pages (`data/thesis_dataset/*/ocr_result.json`) and extracted statement records (`results/esg_records.json`). Topic modelling must explicitly define the unit of analysis.

### 5.4 ESG/sustainability disclosure text mining

- ESG disclosures are prone to template language and regulatory boilerplate, making thematic differentiation a challenge.
- Topic modelling is useful when the output is tied to interpretable constructs (pillars, aspects) and when it supports comparative analysis (sector, year, company).

Relevance: the core value in this repo is *alignment* with ABSA labels and the ability to produce thesis evidence about disclosure structure.

### 5.5 Topic evaluation and interpretability

- Intrinsic measures (coherence, diversity) are not enough on their own; topic evaluation should include **stability** and **human interpretability** checks.
- When supervised labels exist (ABSA aspects/pillars), they can be used as an extrinsic validation lens.

Relevance: this repo already has structured labels; the topic modelling track should use them.

> Citation note: this repo currently cannot use the scite MCP tool (monthly limit reached). Add peer-reviewed citations later via your bibliography workflow; the evaluation structure and method choices here are written so that they can be cited straightforwardly.

---

## 6) Methodology

### 6.1 Data sources (existing repo assets)

Two complementary corpora are available and should be treated as separate modelling datasets:

1. **OCR corpus (document-page text)**
   - Source: `data/thesis_dataset/*/ocr_result.json`
   - Access path example: `data/thesis_dataset/<doc_folder>/ocr_result.json`
   - Text field: `pages[*].markdown` (plus tables/images metadata)
   - Strength: full report coverage.
   - Risk: heavy boilerplate, OCR noise, very long documents.

2. **ABSA-like extracted statement corpus (record-level)**
   - Source: `results/esg_records.json`
   - Structure: list of background-job runs; each run includes `records[*]` with:
     - `text`, `aspect`, `labels`, `esg`, `tone`, `sentiment`, `sentiment_score`, `reasoning`
   - Strength: already segmented into smaller units; already labeled.
   - Risk: depends on extraction quality and coverage; may not represent full document content.

### 6.2 Unit of analysis (critical design choice)

Topic modelling results are only interpretable if the modelling unit is consistent.

Recommended units:

- **Statement-level topics** using `results/esg_records.json` as the primary corpus for ABSA-alignment evaluation.
- **Document-level topics** using OCR text for broad disclosure structure and temporal/sector comparisons.
- Optional: **pillar-level units** derived from OCR using keyword gating (E/S/G signal proxy) to reduce topic mixing.

### 6.3 Preprocessing and normalization

The repository already frames preprocessing and profiling in the topic-modelling UI, especially Phase 1:

- `topic_modelling/pages/1_Phase_1_Data_Preparation.py`
- `topic_modelling/app.py` includes a full-corpus scan and proxy diagnostics.

Minimum preprocessing steps for modelling:

1. Remove OCR boilerplate / page artifacts (page numbers, headers/footers, duplicated section titles).
2. Normalize whitespace, punctuation, and common OCR errors.
3. Stopword strategy: combine Indonesian + English stopwords, plus an ESG domain stoplist.
4. Tokenization consistent across corpora.
5. Optional: language-aware lemmatization (English) + stemming/normalization (Indonesian) if the environment supports it.

### 6.4 Models to compare (planned implementations)

**Baseline A: LDA (bag-of-words)**

- Input: tokenized documents (statement-level or chunked OCR units).
- Hyperparameters: topic count `K` selected via coherence and stability.
- Output: topic-word distributions; document-topic distributions.

**Baseline B: NMF (TF-IDF factorization)**

- Input: TF-IDF vectors.
- Output: topic-term weights; document-topic weights.

**Model C: Embedding-based topic modelling (BERTopic-style)**

- Input: sentence/document embeddings (multilingual).
- Steps: embedding → clustering → c-TF-IDF or equivalent representation.
- Output: topic labels, keywords, exemplars, outlier cluster.

> Implementation note: model execution should be done via an offline runner that exports to `results/topic_modelling/`, then read by Streamlit pages. This avoids recomputation and makes results reproducible.

### 6.5 Evaluation framework

**Intrinsic evaluation**

- Topic coherence (per model and per unit-of-analysis).
- Topic diversity / redundancy checks.
- Stability across seeds / resampling (topic overlap consistency).

**Extrinsic evaluation (ABSA alignment)**

Using the statement corpus:

- Topic → ABSA aspect distribution (does a topic concentrate on a small set of aspects?).
- Topic → ESG pillar distribution (E/S/G separation or cross-pillar mixing).
- Topic → sentiment/tone profiles (do topics systematically differ in tone composition?).

**Human interpretability**

- For each topic: top keywords + top representative statements.
- Manual mapping to a small set of thesis-relevant ESG dimensions (pillars, common aspects).

### 6.6 Outputs and reproducibility (to be added)

Standardize exports under:

- `results/topic_modelling/`

Recommended artifacts:

- `corpus_manifest.json` (corpus version, preprocessing flags, signature hash).
- `topics_lda.csv`, `doc_topics_lda.parquet` (or CSV).
- `topics_nmf.csv`, `doc_topics_nmf.parquet`.
- `topics_embedding.csv`, `doc_topics_embedding.parquet`.
- `topic_alignment_aspect.csv`, `topic_alignment_pillar.csv`.
- `metrics.json` (coherence/diversity/stability summaries).

---

## 7) Results (Current Evidence From Existing Code/Datasets)

This section reports **what is already measurable today** in the repository, without adding new dependencies or training new models.

### 7.1 OCR corpus scale and coverage (document-level)

From the OCR dataset under `data/thesis_dataset/`:

- OCR documents: **189** (`data/thesis_dataset/*/ocr_result.json`)
- Total pages across OCR documents: **33,722** (avg **178.42** pages per doc)
- Total tokens (simple word regex): **11,724,429** (avg **62,034** tokens per doc)
- Numeric mentions (simple regex proxy): **1,079,710** (avg **5,712** numeric mentions per doc)

Coverage concentration by year (top observed counts from folder names):

- 2024: **41** documents
- 2023: **27** documents
- 2025: **21** documents
- 2022: **16** documents
- 2021: **15** documents
- 2019: **9** documents
- 2020: **9** documents

**Interpretation:** the OCR corpus is sufficiently large for robust topic modelling, but temporal modelling should explicitly account for year imbalance (e.g., avoid over-claiming trends for sparse years).

### 7.2 ABSA-extracted statement corpus scale (statement-level)

From `results/esg_records.json`:

- Successful extraction jobs with records: **544**
- Total extracted records: **5,112**
- Records with non-empty `text`: **5,110**
- Average statement length: ~**171 characters** (proxy)

Label distributions (as present in the records):

- ESG pillar label counts:
  - E: **2,409**
  - G: **1,228**
  - S: **828**
  - plus mixed/other labels (various strings) and `none`
- Tone label counts:
  - none: **1,806**
  - action: **1,452**
  - outcome: **973**
  - commitment: **878**
- Sentiment label counts:
  - neutral: **2,823**
  - positive: **2,152**
  - negative: **86**

**Interpretation:** the statement corpus is large enough for topic modelling at the statement level, and it is already metadata-rich for topic-to-label alignment evaluation (RQ2).

### 7.3 Existing “data readiness” diagnostics in topic_modelling UI

The Streamlit topic-modelling workspace currently performs a corpus-wide scan and produces exploratory charts/diagnostics:

- Implementation: `topic_modelling/app.py`
- Outputs displayed: year coverage, sector proxy distribution (folder-name heuristic), ESG pillar signal totals, and a “metric evidence vs positive tone” scatter plus “narrative-risk” shortlist.

**Interpretation:** this provides a strong foundation for the thesis: it establishes corpus breadth, identifies imbalance risk, and motivates modelling design choices (unit-of-analysis, stratification, and robustness checks).

> Limitation: these are proxy diagnostics, not topic models. Topic modelling results still need to be implemented and exported.

---

## 8) Discussion

### 8.1 What these results imply for topic modelling feasibility

1. **Feasibility is strong**: the OCR corpus has substantial text mass (11.7M+ tokens) and broad year coverage (though imbalanced).
2. **Bilingual/OCR noise is a first-order concern**: direct document-level LDA on raw OCR is likely to recover boilerplate topics unless strong preprocessing and/or unit segmentation is applied.
3. **The ABSA statement corpus is the most evaluation-friendly starting point**:
   - The units are short and already labeled.
   - Topic-to-aspect/pillar alignment can be computed immediately after modelling.

### 8.2 Risk analysis / threats to validity

- **Imbalance bias**: year/sector imbalance can cause “dominant year topics” to masquerade as trends.
- **Template language**: corporate boilerplate may dominate topics without de-duplication.
- **Extraction bias**: ABSA records may cover only certain types of statements (e.g., those that match prompts), skewing topic distributions.
- **Label noise**: pillar/tone labels include `none` and mixed-string variants; these need normalization before alignment metrics are meaningful.

### 8.3 How to mitigate risks (design choices)

- Build two corpora (OCR + ABSA records) and compare.
- Chunk OCR by sections/pages and optionally gate by pillar keywords to reduce mixing.
- Add de-duplication or boilerplate filtering before modelling.
- Normalize ABSA labels (pillar/tone/sentiment) into canonical values before computing alignment.

---

## 9) Conclusion

Topic modelling is feasible and well-motivated in this repository, primarily as a complementary interpretability layer to the existing ABSA pipeline. The repo already contains:

- a large OCR corpus (`data/thesis_dataset/*/ocr_result.json`),
- a sizeable statement-level ABSA-like record corpus (`results/esg_records.json`),
- and a topic-modelling workspace with Phase framing and corpus-level diagnostics (`topic_modelling/app.py`, `topic_modelling/task_data.py`).

The primary remaining work is to implement and **persist** topic model outputs (LDA/NMF + embedding-based) into standardized result artifacts and then connect them to ABSA/ontology alignment evaluation and temporal/sectoral analysis.

---

## 10) Implementation Plan (Next Steps in This Repo)

Recommended order (to convert this write-up into executable, thesis-ready evidence):

1. **Create an offline exporter for topic modelling**
   - Add `topic_modelling/run_topic_models.py` to build corpora and export `results/topic_modelling/` artifacts.
2. **Normalize ABSA labels**
   - Build a small canonicalization step for pillar/tone/sentiment strings before alignment metrics.
3. **Run baseline topic models**
   - LDA/NMF on statement corpus first; then OCR-chunk corpus.
4. **Compute alignment + stability metrics**
   - Export topic-to-aspect/pillar distributions and stability summaries.
5. **Add Streamlit pages that read exported outputs**
   - Avoid re-training in-app; keep Streamlit for exploration and visualization.
6. **Populate thesis chapter results**
   - Use exported tables/figures to write results/discussion with concrete numbers.

---

## Repo Anchors (Where the relevant code/data lives)

- Topic modelling app scaffold and corpus scan:
  - `topic_modelling/app.py`
  - `topic_modelling/ui.py`
  - `topic_modelling/task_data.py`
  - `topic_modelling/pages/1_Phase_1_Data_Preparation.py`
- OCR corpus:
  - `data/thesis_dataset/*/ocr_result.json`
- ABSA-like extracted statement records:
  - `results/esg_records.json`
- Topic modelling track framing (older, shorter):
  - `documentation_topic_modelling.md`

