# Research Documentation: ESG OCR, ABSA, and LLM Extraction Pipeline

https://claude.ai/chat/498fbdb6-973a-476e-91dd-fbb148e77b28

## 1. Code-to-Research Relationship

The code in the `pages` folder implements a research prototype for extracting, classifying, and evaluating ESG-related statements from sustainability reports. The system is organized as a pipeline that transforms unstructured report documents into structured ESG records and then evaluates those records through multiple analytical methods.

The main relationships are:

| Code artifact | Research role | Main output |
|---|---|---|
| `pages/Bulk_OCR.py` | Data acquisition and preprocessing layer | OCR markdown pages, extracted images, complete OCR JSON, processing log |
| `pages/llm_processing.py` | Main experimental pipeline | T1 ClimateBERT predictions, T2 ABSA results, T3 LLM ESG structured extraction |
| `pages/ground_truth.py` | Resumable benchmark/evaluation layer | JSONL records for model comparison over extracted ESG records |
| `pages/data_001_001.json` | Seed/illustrative annotated data | Example ESG text, aspect, labels, ESG pillar, sentiment, reasoning |
| `pages/models_cache.json` | Model availability cache | Candidate model list for benchmarking |
| `pages/source.md` | Data source note | Sustainability report and ESG score sources |

The broader modules referenced by these pages define the analytical logic:

| Referenced module | Analytical function |
|---|---|
| `code/rule_based.py` | Lexicon-based aspect, polarity, tone, and ontology mapping |
| `code/classical_ml.py` | TF-IDF and logistic-regression baseline for aspect, sentiment, and tone |
| `code/hybrid_model.py` | Hierarchical transformer/ontology-aware hybrid ABSA model |
| `code/explainability.py` | Cross-model comparison, disagreement analysis, and explanation views |
| `code/utils.py` | Sentence parsing, section detection, and language detection |
| `code/lexicons.py` | ESG aspect lexicon, polarity markers, tone markers, and ontology paths |

Together, these files support a research workflow for ESG disclosure analysis from document ingestion to model comparison.

## 2. Research Background

ESG disclosure is increasingly important for companies, investors, regulators, and stakeholders. Sustainability reports contain information about environmental, social, governance, economic, operational, and strategic activities. However, these reports are usually long, semi-structured, multilingual, and filled with narrative statements that are difficult to compare automatically.

Traditional ESG analysis often depends on manual reading, checklist-based scoring, or high-level ESG ratings. These approaches are useful but limited when the goal is to analyze sentence-level evidence, identify specific ESG aspects, distinguish promises from realized outcomes, and detect differences between environmental claims, social initiatives, governance commitments, and operational sustainability actions.

This project addresses that problem by combining:

- OCR for converting PDFs and scanned reports into analyzable text.
- Rule-based ESG lexicons for transparent baseline classification.
- Classical machine learning for interpretable text classification.
- Transformer and ClimateBERT-style models for climate/ESG classification.
- LLM-based extraction for structured ESG record generation.
- Hybrid ontology-aware ABSA for section-sensitive and aspect-sensitive analysis.
- Cross-model explainability for comparison and disagreement analysis.

The implementation is especially relevant for sustainability reports in Indonesian and English, because the code includes bilingual lexical cues and parses Indonesian ESG report structures such as `KINERJA LINGKUNGAN`, `KINERJA SOSIAL`, `TATA KELOLA`, and `STRATEGI KEBERLANJUTAN`.

## 3. Research Gap

The implemented system responds to several gaps in existing ESG text-analysis practice:

1. Document-level ESG ratings do not explain sentence-level evidence.
   Many ESG scoring systems produce final scores without showing which textual claims support the score. This code extracts sentence-level records with aspect, sentiment, tone, and reasoning.

2. Generic sentiment analysis does not distinguish ESG disclosure tone.
   ESG reports contain commitments, actions, and outcomes. A positive-sounding commitment is not the same as a verified outcome. The code explicitly models tone categories such as `Commitment`, `Action`, `Outcome`, and `Unknown`.

3. Climate-only models may miss broader ESG dimensions.
   ClimateBERT-style models are useful for climate statements, but ESG reports also include social, governance, operational, and economic topics. The system adds ABSA, ontology mapping, and LLM extraction to cover broader ESG categories.

4. LLM extraction alone can be unstable and hard to evaluate.
   The pipeline stores raw outputs, parsed JSON, prompt labels, model names, errors, and resumable records. This supports comparison across prompts, models, and target pages.

5. OCR and multimodal report structure are often neglected.
   `Bulk_OCR.py` preserves page-level markdown, images, full OCR JSON, and processing logs. This is important because ESG reports often contain tables, charts, graphics, and scanned text.

6. Existing theory often separates disclosure analysis, sentiment analysis, and greenwashing detection.
   The hybrid model links sentiment, tone, ontology alignment, section context, and a greenwashing-style index in one experimental framework.

## 4. Research Questions

The codebase supports the following research questions:

RQ1. How can sustainability reports be converted into structured ESG evidence at sentence or page-batch level?

The OCR pipeline and LLM extraction pipeline address this by converting reports into markdown pages and then extracting JSON ESG records.

RQ2. How accurately and consistently can different model families classify ESG aspects, sentiment, and tone?

The rule-based, classical ML, ClimateBERT/API, local transformer, deep model, hybrid model, and LLM outputs can be compared across the same text units.

RQ3. Does adding section context and ontology mapping improve ESG aspect-based sentiment analysis?

The hybrid model uses sentence vectors, section vectors, document vectors, and ontology vectors, while the rule-based model includes section-aware correction.

RQ4. Can the system distinguish ESG commitments from actions and outcomes?

Tone markers and hybrid tone prediction define whether statements are commitments, actions, outcomes, or unknown claims.

RQ5. Can model disagreement reveal uncertain, ambiguous, or potentially greenwashing-related ESG statements?

The explainability module compares predictions across models and calculates sentiment disagreement and consistency.

RQ6. How do prompt strategy, model choice, and document context affect LLM-based ESG extraction?

`llm_processing.py` supports multiple prompt templates, multiple LLMs, context-length control, full-document context, targeted page batches, retries, mock mode, and resumable result storage.

## 5. Research Objectives

The objectives of the implemented research prototype are:

1. Build an end-to-end ESG text-processing pipeline from PDF/image reports to structured ESG records.
2. Extract ESG statements with fields such as text, aspect, ESG pillar, sentiment, sentiment score, labels, model, prompt, and reasoning.
3. Compare rule-based, classical ML, transformer, ClimateBERT, hybrid, and LLM methods for ESG analysis.
4. Support reproducible and resumable experiments through JSON/JSONL result persistence.
5. Provide interpretable outputs using lexical triggers, coefficient explanations, ontology paths, section metadata, and model-disagreement views.
6. Define metrics that measure not only classification output but also ontology consistency, tone-sentiment patterns, and potential disclosure gaps.
7. Establish a foundation for benchmark construction using OCR-derived sustainability report data and manually or semi-automatically labeled ESG records.

## 6. Research Contribution

This code contributes a practical ESG research framework with the following contributions:

1. End-to-end ESG document pipeline.
   The system starts from raw sustainability reports and produces structured ESG analysis outputs.

2. Page-aware and context-aware LLM extraction.
   The T3 pipeline sends full-document context while focusing extraction on selected pages or page batches.

3. Multi-method ESG classification benchmark.
   The system allows comparison between rules, classical ML, deep learning, hybrid models, ClimateBERT, local models, and remote LLMs.

4. ESG ABSA ontology integration.
   ESG aspects are mapped to canonical ontology paths such as environmental emission reduction, social welfare, governance transparency, and economic operational efficiency.

5. Tone-aware ESG disclosure analysis.
   The code separates commitment, action, and outcome, which is important for evaluating whether reports describe actual performance or only future intent.

6. Explainable model comparison.
   The framework exposes lexical triggers, TF-IDF coefficients, ontology alignment, section influence, and cross-model disagreement.

7. Resumable experimentation.
   Long-running OCR and model runs can be resumed or skipped using saved logs, JSON arrays, JSONL files, and processed-key checks.

## 7. Theoretical Foundation

### 7.1 ESG Disclosure Theory

The pipeline is grounded in ESG disclosure theory, where companies communicate environmental, social, and governance performance to stakeholders. The code operationalizes disclosure as analyzable text units: sentences, pages, and page batches.

Relevant implementation:

- `Bulk_OCR.py` collects disclosure text from reports.
- `llm_processing.py` extracts ESG records.
- `data_001_001.json` represents annotated ESG disclosure examples.

### 7.2 Stakeholder Theory

Stakeholder theory argues that companies disclose sustainability information to address the concerns of investors, communities, employees, regulators, and society. The code reflects this through social, governance, environmental, and economic aspect categories.

Relevant implementation:

- `ASPECT_LEX` includes community welfare, education support, worker safety, local partnership, governance/transparency, compliance, and environmental preservation.

### 7.3 Legitimacy Theory

Legitimacy theory explains sustainability reporting as a way for companies to justify their social and environmental role. The distinction between commitment, action, and outcome is important because legitimacy-oriented disclosures may emphasize promises or broad claims rather than measurable outcomes.

Relevant implementation:

- `tone_basic()` identifies commitment, action, and outcome markers.
- `run_hierarchical_hybrid()` predicts tone and compares it with sentiment.
- The greenwashing index compares commitment sentiment against outcome sentiment.

### 7.4 Aspect-Based Sentiment Analysis

ABSA analyzes sentiment toward specific aspects rather than whole documents. This is central to ESG because one report can contain positive governance claims, negative climate-risk statements, and neutral operational descriptions.

Relevant implementation:

- `collect_aspects()` identifies aspect labels.
- `polarity_basic()` estimates positive, negative, or neutral polarity.
- `run_classical_ml()` and `run_hierarchical_hybrid()` predict aspect, sentiment, and tone.

### 7.5 Ontology-Based Information Extraction

Ontology-based extraction maps text into structured knowledge categories. The project defines canonical ESG paths to organize extracted claims.

Relevant implementation:

- `CANON_PATHS` maps aspects to paths such as `Environmental -> Emission Reduction`.
- `Ontology_Alignment` measures semantic consistency between sentence embeddings and ontology vectors.

### 7.6 Human-AI and Explainable AI Theory

Because ESG analysis can influence decision-making, model transparency matters. The project uses rule explanations, coefficient explanations, ontology alignment, and cross-model comparisons to support interpretability.

Relevant implementation:

- `explain_rule_based_sentence()`
- `coef_table_binary_safe()`
- `explain_hybrid_sentence()`
- `compare_explain()`
- `plot_consistency_summary()`

## 8. Analytical Framework

The analytical workflow can be defined as:

1. Input acquisition
   - Upload PDFs or images.
   - Store raw documents in `data/thesis_pdf`.
   - Run Mistral OCR.

2. OCR transformation
   - Save page markdown to `data/thesis_dataset/<document>/pages`.
   - Save extracted images to `data/thesis_dataset/<document>/images`.
   - Save full OCR JSON as `ocr_result.json`.
   - Save resume log to `logs/bulk_ocr_log.json`.

3. Text selection
   - Use manual text or OCR document mode.
   - Select all pages, specific pages, or page ranges.
   - Batch pages for processing.
   - Send full document as context and target pages as extraction focus.

4. T1: ClimateBERT or local text-classification
   - Predict climate/ESG labels using available ClimateBERT API models or local Hugging Face models.
   - Save predictions to `results/predictions.json` or `results/t1_results.jsonl`.

5. T2: ABSA analysis
   - Run rule-based aspect, polarity, and tone extraction.
   - Run classical ML baseline.
   - Optionally run deep model.
   - Run hybrid ontology-aware model.
   - Save outputs to `results/absa_results.json` or `results/t2_results.jsonl`.

6. T3: LLM structured ESG extraction
   - Select OpenRouter or LM Studio backend.
   - Select one or more LLM models.
   - Select one or more prompt templates.
   - Parse strict JSON output.
   - Save success and failure records to `results/esg_records.json`.

7. Benchmark and ground-truth processing
   - Load extracted records from `results/esg_records.json`.
   - Re-run T1/T2 analysis with resume support.
   - Store JSONL outputs for reproducible comparison.

8. Explainability and comparison
   - Compare model sentiment and tone.
   - Calculate disagreement.
   - Visualize ontology alignment and section distribution.

## 9. Metrics Defined by the Code

### 9.1 OCR Metrics

These are not fully formalized in the code yet, but can be derived from `Bulk_OCR.py` outputs:

| Metric | Definition | Source |
|---|---|---|
| OCR completion rate | Processed documents / uploaded documents | `bulk_ocr_log.json` |
| OCR page count | Number of pages extracted per document | `ocr_result.json`, log field `pages` |
| Image extraction count | Number of extracted images per document | `images` directory |
| OCR failure rate | Failed documents / uploaded documents | `bulk_ocr_log.json` |
| Resume skip count | Documents skipped because status is `done` | Streamlit status/log |

### 9.2 Extraction Metrics

| Metric | Definition | Source |
|---|---|---|
| LLM extraction success rate | Successful T3 runs / total T3 runs | `ok` field in `esg_records.json` |
| Parsed record count | Number of ESG records returned per model/prompt/target | `records` length |
| JSON parse failure rate | Parse failures / total T3 runs | `error` field |
| Prompt sensitivity | Variation in extracted records across prompt templates | `prompt` field |
| Model sensitivity | Variation in extracted records across selected LLM models | `model` field |
| Context sensitivity | Variation under different context-length values | `context_length` setting and outputs |

### 9.3 ABSA Metrics

| Metric | Definition | Source |
|---|---|---|
| Aspect frequency | Count of extracted aspects | Rule-based, classical, hybrid outputs |
| Sentiment distribution | Count of positive, neutral, negative predictions | T2 outputs |
| Tone distribution | Count of commitment, action, outcome, unknown | T2 outputs |
| Section-tone distribution | Tone counts by report section | Hybrid plot `Tone Distribution by Section` |
| Tone-sentiment distribution | Cross-tabulation of tone and sentiment | Hybrid plot `Tone x Sentiment` |
| Sentiment confidence | Maximum softmax score for hybrid sentiment prediction | `sentiment_score` |
| Tone confidence | Maximum softmax score for hybrid tone prediction | `tone_score` |

### 9.4 Ontology and Greenwashing Metrics

| Metric | Definition | Code basis |
|---|---|---|
| Ontology alignment | Cosine similarity between sentence vector and ontology vector | `Ontology_Alignment` |
| Ontology consistency | Share of sentences mapped to non-general ontology paths | `Ontology Consistency` metric |
| Greenwashing index | Average commitment sentiment divided by average outcome sentiment | `Greenwashing Index` metric |
| Section influence | Average vector norm by section for hybrid explanations | `explain_hybrid_sentence()` |

The greenwashing index is exploratory. A high commitment-to-outcome imbalance may indicate that disclosures emphasize promises more than demonstrated outcomes, but this should be validated with human labels before being treated as a definitive greenwashing measure.

### 9.5 Cross-Model Evaluation Metrics

| Metric | Definition | Source |
|---|---|---|
| Sentiment disagreement | Number of unique sentiment labels across models for the same sentence | `compare_explain()` |
| Pairwise consistency | Agreement ratio between model pairs | `plot_consistency_summary()` |
| Rule-vs-hybrid difference | Difference between lexicon baseline and contextual hybrid output | Rule and hybrid outputs |
| Explainability coverage | Availability of explanations per model | Explainability module |

## 10. Comparison With Existing Theory and Methods

### 10.1 Compared With Manual ESG Scoring

Manual ESG scoring is usually accurate when performed by domain experts but is slow, expensive, and difficult to reproduce. This system improves scalability by extracting sentence-level ESG records automatically. However, it still requires human validation for high-stakes scoring.

### 10.2 Compared With Traditional Sentiment Analysis

Traditional sentiment analysis predicts polarity at document or sentence level. The implemented system extends this by adding aspect labels, ESG ontology paths, section context, tone categories, and model explanations.

### 10.3 Compared With ClimateBERT-Only Classification

ClimateBERT is useful for climate-related classification, especially environmental claims. This project expands beyond climate classification by adding social, governance, economic, operational, and sustainability-strategy aspects.

### 10.4 Compared With Pure LLM Extraction

A pure LLM pipeline can extract rich records but may produce inconsistent JSON, hallucinated categories, or prompt-sensitive outputs. This system reduces that risk by:

- Requiring strict JSON output.
- Parsing and storing raw outputs.
- Saving failures for auditability.
- Comparing multiple prompts and models.
- Running non-LLM baselines for comparison.

### 10.5 Compared With Rule-Based ESG Taxonomies

Rule-based ESG systems are interpretable but brittle. The code uses rules as a transparent baseline, then compares them with ML and hybrid models that can capture broader language patterns.

### 10.6 Compared With Ontology-Only Approaches

Ontology-only methods provide structure but may miss semantic nuance. The hybrid model combines ontology vectors with sentence, section, and document representations, making the ontology a modeling component rather than only a lookup table.

## 11. Limitations

1. Ground truth is still limited.
   `data_001_001.json` contains example labeled records, but a larger manually validated dataset is required for reliable evaluation.

2. Weak labels are used in several models.
   Classical and hybrid models rely partly on rule-derived labels, which may reproduce lexicon bias.

3. OCR quality is not yet quantitatively evaluated.
   The OCR pipeline stores outputs and logs, but character error rate, word error rate, and table fidelity are not yet implemented.

4. LLM outputs may vary by prompt and model.
   The pipeline tracks prompt and model differences, but consistency must be measured over repeated runs.

5. Greenwashing index is exploratory.
   The commitment/outcome ratio is theoretically meaningful but requires empirical validation against expert-labeled greenwashing cases.

6. ESG ontology is handcrafted and limited.
   `ASPECT_LEX` and `CANON_PATHS` cover useful categories but may not represent all industries or reporting standards.

7. Section parsing is simple.
   `parse_document()` recognizes markdown-style headings and known section names, but complex report layouts may need stronger structural parsing.

8. Multilingual handling is basic.
   Indonesian and English cues are included, but robust multilingual classification would require larger multilingual training data.

9. Model comparison is mostly internal.
   The current comparison evaluates consistency and disagreement, but external benchmarks and human adjudication are needed for accuracy claims.

10. Some model paths and APIs depend on local environment.
   ClimateBERT imports, OpenRouter keys, LM Studio, local model folders, and Mistral OCR credentials must be configured correctly.

## 12. Conclusion

The `pages` folder implements an applied research prototype for ESG document intelligence. It converts sustainability reports into OCR-derived markdown, extracts structured ESG records with LLMs, analyzes ESG aspect, sentiment, tone, and ontology alignment, and supports model comparison through resumable benchmark outputs.

The research value of the system is not only in classification, but in its layered design: OCR for document access, LLM extraction for structured records, ABSA for sentence-level interpretation, ontology mapping for theoretical grounding, and explainability tools for comparing model behavior.

The strongest research direction from this code is a benchmark study on ESG disclosure analysis in Indonesian and English sustainability reports. The benchmark can compare rule-based, classical ML, ClimateBERT, hybrid ontology-aware models, and LLM prompting strategies across extraction quality, sentiment/tone consistency, ontology alignment, and commitment-versus-outcome patterns.

Future work should focus on building a larger expert-labeled ground-truth dataset, adding OCR quality metrics, validating the greenwashing index, expanding the ESG ontology, and reporting formal evaluation metrics such as precision, recall, F1-score, agreement rate, and human adjudication accuracy.
