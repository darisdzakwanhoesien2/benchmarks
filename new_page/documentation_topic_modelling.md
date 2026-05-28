# Documentation: Feasibility of Topic Modelling for Indonesian ESG ABSA in This Benchmark

## 1. Research Gap

This repository already supports OCR, ESG extraction, ABSA labeling, ontology mapping, and multiple dashboard analyses. It also has a dedicated `topic_modelling/` workspace. However, a formal **topic modelling research track** connected to Indonesian ESG ABSA is still not fully integrated.

Main gaps are:

1. Existing ABSA outputs focus on predefined aspect/tone labels, while latent topic structure in Indonesian ESG narratives is not consistently modeled.
2. Topic modelling artifacts are present, but links between discovered topics and ABSA labels (aspect, sentiment, tone, ESG pillar) are not yet systematically benchmarked.
3. Cross-sector and cross-document topic dynamics are not yet a central evaluation axis.
4. Current thesis evidence emphasizes extraction and validation; topic coherence, interpretability, and drift analysis are not yet fully operationalized.

## 2. Research Questions

1. Can topic modelling uncover meaningful latent ESG themes in Indonesian sustainability-report text beyond predefined ABSA categories?
2. How well do discovered topics align with existing ESG ABSA aspect and pillar taxonomies in this repository?
3. Which topic-modelling approach is most effective for this corpus: probabilistic models, embedding-based clustering, or hybrid methods?
4. Can topic distributions improve interpretation of sentiment/tone patterns and disclosure emphasis across sectors and companies?

## 3. Research Objectives

1. Build a reproducible topic modelling workflow using existing ESG text artifacts.
2. Compare multiple topic-modelling strategies for Indonesian ESG text.
3. Measure topic quality, stability, and alignment with ABSA/ontology structures.
4. Integrate topic outputs into existing dashboards and thesis chapter evidence.
5. Demonstrate how topic-level insights complement ABSA metrics for richer ESG analysis.

## 4. Research Contribution

This study can contribute:

1. A practical topic-modelling extension for Indonesian ESG ABSA within an end-to-end thesis system.
2. Empirical evidence on latent ESG narrative structure across companies and sectors.
3. A mapping framework between unsupervised topics and supervised ABSA labels.
4. A complementary interpretation layer for identifying disclosure concentration, emerging themes, and under-covered ESG areas.
5. Reusable topic artifacts to support downstream SNA/graph analytics and decision-support dashboards.

## 5. Literature Review (Focused)

Relevant literature streams:

1. **Classical topic models**: LDA and related probabilistic frameworks for latent theme discovery.
2. **Neural/embedding-based topic modelling**: contextual embedding clustering and topic representation methods.
3. **Topic modelling in low-resource/multilingual settings**: preprocessing and representation challenges for non-English corpora.
4. **ESG and sustainability text mining**: use of topic structures to analyze corporate disclosure priorities.
5. **Topic quality evaluation**: coherence, diversity, stability, and human interpretability.

For this repository, literature should support a practical position: topic models are valuable when validated against existing ABSA labels and ontology paths, not only by unsupervised scores.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Key assets available now:

1. Topic modelling workspace
   - `topic_modelling/` (`app.py`, `ui.py`, task/data helpers)
2. ESG extraction and ABSA outputs
   - `results/esg_records.json`
   - T2/T3 outputs under `results/`
3. Ontology/ABSA context
   - `code/lexicons.py`
   - `pages/1_6_Ontology_Path_Viewer.py`
4. Validation and dashboards
   - `pages/1_3_Ground_Truth_Metrics.py`
   - `pages/1_7_Research_Questions_Dashboard.py`
   - Chapter integration pages under `pages/6_x_*.py`

### 6.2 Corpus Preparation

1. Aggregate Indonesian and bilingual ESG statements from extracted records and OCR text.
2. Normalize text (case, punctuation, OCR artifacts, repeated boilerplate).
3. Apply Indonesian-aware preprocessing (tokenization, stopword strategy, optional stemming/lemmatization).
4. Build alternate corpora:
   - full statement corpus,
   - aspect-filtered corpus,
   - sector-specific corpora.

### 6.3 Topic-Modelling Strategies

Candidate approaches:

1. **Probabilistic topic modelling**
   - LDA-style baselines on cleaned bag-of-words.
2. **Embedding-based topic modelling**
   - sentence/document embeddings + clustering + topic term extraction.
3. **Hybrid strategy**
   - combine probabilistic topic distributions with ABSA/ontology constraints.

### 6.4 Evaluation Framework

1. Intrinsic topic quality:
   - coherence,
   - diversity,
   - topic redundancy,
   - run-to-run stability.
2. Extrinsic alignment:
   - mapping topics to ABSA aspects,
   - mapping topics to ESG pillars,
   - relationship between topic presence and sentiment/tone distributions.
3. Human interpretability:
   - manual review of top terms and representative statements per topic.
4. Comparative analysis:
   - by sector,
   - by company,
   - by model/prompt subsets where relevant.

### 6.5 Integration Plan in This Repository

1. Extend `topic_modelling/` scripts to export standardized outputs under `results/topic_modelling/`.
2. Save:
   - topic-word tables,
   - document-topic distributions,
   - coherence/stability metrics,
   - topic-to-ABSA mapping tables.
3. Add/extend Streamlit topic dashboard page for filtering and comparison.
4. Link topic evidence into RQ dashboard and Chapter 4-6 discussion/conclusion pages.

## 7. Expected Results

With current assets, expected outcomes are:

1. Topic modelling identifies latent ESG themes not fully captured by predefined ABSA labels.
2. Many topics will align with existing ESG pillars, while some expose cross-pillar or emerging disclosure patterns.
3. Embedding-based methods are likely to improve semantic coherence for Indonesian bilingual corporate language.
4. Topic distributions will reveal sector-level narrative differences and disclosure concentration effects.
5. Topic outputs will complement ABSA classification by explaining thematic context behind sentiment and tone labels.

## 8. Discussion

Key discussion points:

1. **Added value**: topic models provide macro thematic structure, while ABSA provides micro aspect-sentiment labeling.
2. **Method sensitivity**: results depend on preprocessing, topic count, and model choice; transparent ablation is needed.
3. **Data quality dependency**: OCR noise and extraction inconsistency can degrade topic coherence.
4. **Interpretability challenge**: unsupervised topics require careful mapping to ESG ontology to avoid over-interpretation.
5. **Thesis implication**: integrating topic modelling with ABSA strengthens evidence for narrative-level ESG analysis in Indonesian reports.

## 9. Conclusion

Topic modelling for Indonesian ESG ABSA is feasible in this repository and can be implemented using existing code, outputs, and dashboards. The primary task is to formalize corpus preparation, model comparison, and ABSA-alignment evaluation so topic findings become reproducible thesis evidence. The expected contribution is a robust thematic layer that complements ABSA and improves interpretation of ESG disclosure behavior.

---

## Suggested Next Implementation Steps

1. Consolidate Indonesian ESG text corpus from `results/esg_records.json` and selected OCR artifacts.
2. Extend `topic_modelling/` pipeline to produce `results/topic_modelling/` standardized outputs.
3. Add topic-to-aspect and topic-to-pillar mapping diagnostics.
4. Integrate topic evidence into RQ and chapter dashboards for thesis reporting.
