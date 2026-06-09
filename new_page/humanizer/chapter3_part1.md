# Chapter 3 Methodology

## 3.1 Research Design and Methodological Overview

This thesis applies an executable mixed-method research design for analyzing automatic ESG disclosures in Indonesian sustainability reports. As explained in chapter 2, the methodological core of this workflow transforms report contents into machine-readable evidence through LLM extraction, validates outputs using ClimateBERT-style and ABSA-style processes, and then aligns validated outputs to ontology. From a technical perspective, this workflow is computational: its fundamental operations involve document ingestion, PDF-to-text extraction, structured ESG extraction, aspect-polarity-tone classification, and evaluation of ontology alignment and model prompt stability. However, it is also interpretive in that the workflow retains page-level provenance, offers manual audit pages, and considers annotation and disagreement analysis as methodological tools rather than just data-processing steps.

In this approach, the fundamental methodological strategy is implemented as a staged pipeline. The stages of the pipeline begin with PDF ingestion and OCR and continue with page-aware LLM extraction, followed by validation, representation, and finally thesis-ready evidence artifact production. As a part of the current repository, the pipeline accepts PDF sustainability reports and annual reports, associated page markdown, prompt definitions, and ontology as input resources and generates structured ESG records, stage-specific benchmark files, ontology coverage tables, and stability summaries as thesis-ready outputs. The resulting structured ESG evidence can then be visualized as JSON, CSV, JSONL, or dashboards.

The methodological design is characterized by combining multiple methodological logics into one pipeline. First, it includes heuristic and weak supervision components, specifically lexicographic rules and ontology mappings, due to the lack of a labeled corpus for Indonesian ESG disclosures. Second, it involves LLM extraction and multiple prompt templates because output performance is affected by both model type and prompt style. Third, it includes ClimateBERT labeling as an external semantic comparator, not an internal classifier for disclosing tone. This distinction is key because climate topic detection and disclosure tone detection are different phenomena.

This particular methodological strategy is appropriate for solving the identified research problem because ESG disclosures are long-form, potentially bilingual, inconsistent, and usually contain metrics, commitments, actions, outcomes, and forward-looking information. A simple single-stage classifier would obscure the difference between various types of disclosures. On the contrary, a methodological pipeline that focuses on evidence traceability, modularity, and verification will help to identify and understand various types of ESG disclosures.

Alternative methodologies were implicit in the implemented solution. A simple keyword search system would be deterministic but fragile under bilingual disclosures. A single prompt extractor would simplify the process but obscure prompt effects and schema drifts. A ClimateBERT-only strategy would allow for climate-topic labeling but fail to account for disclosure tone or commitment, action, outcome distinctions.

This particular methodology addresses four linked objectives: converting PDF disclosures into structured ESG records, specifying and validating an aspect-pillar-sentiment-tone schema, comparing ESG tone with ClimateBERT labels, and analyzing instability and/or failure modes in models and prompts. Provenance and reproducibility are assumed as supporting factors of those four objectives, but they are not treated as independent research questions. Thus, the methodology chapter describes a holistic research approach rather than a classifier in isolation.

### 3.1.1 System Architecture

The pipeline in the current repository has a well-defined operational architecture, described by documentation in pages. In short, it can be visualized as follows:

The OCR stage processes each report into page-level markdown and OCR JSON and stores those artifacts under data/thesis_dataset/<document>. The extraction stage takes prompts from prompt/ folder and writes structured and raw extraction outputs under results/esg_records.json and results/background_llm_jobs/ respectively. The ground truth stage generates resumable JSONL output under results/t1_results.jsonl and results/t2_results.jsonl. The analysis stage generates ontology coverage tables, failure mode tables, prompt and model stability summary, greenwashing-oriented summary, and other evidence outputs under results/revision_analysis/ and results/thesis_workflow_dashboard/.

This architecture is further reflected in the Streamlit UI: pages/Bulk_OCR.py handles report ingestion, pages/llm_processing.py launches a combined T1-T2-T3 extraction pipeline, pages/ground_truth.py manages benchmark outputs and their resumption, pages/1_4_ClimateBERT_Record_Batch.py manages ClimateBERT comparison preparation, pages/1_6_Ontology_Path_Viewer.py analyzes ontology paths, and pages/1_0_Revision_Analytics.py manages diagnostic outputs. Hence, the overall methodology can be understood both conceptually and as an executable research pipeline.

### 3.1.2 Design Principles

The following five principles drive the workflow design.

First, provenance is preserved at page and record levels in this method. All generated extraction outputs are always linked back to expanded pages and page-level markdown documents, and page-level audit pages are developed to facilitate manual review of each record.

Second, this pipeline prefers modular comparison over reliance on a single classifier model. Multiple prompt types, multiple model types, classical ML models, and hybrids can be used simultaneously to ensure disagreement analysis capability.

Third, the pipeline accounts for the bilingual nature of disclosures. Bilingual reports, multilingual transformers, bilingual prompts, and ontology-based linguistic resources are included to ensure consistency.

Fourth, this methodology strives for interpretability in addition to automation. Lexical triggers, ontological paths, and reasoning fields in each record are included so that generated records can be easily traced back to their meanings.

Fifth, reproducibility is an essential design consideration for this methodology. Status updates, event logs, and prompts are stored separately and benchmark output artifacts are exported so that the pipeline can be rerun, prompted differently, and revised.

These principles imply a number of technical decisions: batch processing over inference per page, JSONL resumable benchmarking, ontology alignment after extraction, and separate treatment of topic labels, tone labels, and sentiment polarity.

## 3.2 Data Sources

The primary data source in the repository is a corpus of PDF documents in data/thesis_pdf/. As of today, according to the inventory provided in code_documentation.md, this folder contains 193 PDF files. These files represent the raw document-level dataset for the thesis methodology. In addition to this, there exists a machine-expanded dataset in data/thesis_dataset/ that contains 189 folders with processed OCR output at the inspection date. Each folder typically contains ocr_result.json, a pages/ folder with OCR-generated markdown, and images/ folder with OCR-generated image crops.

The dataset is appropriate for solving the research problem because the thesis aims to transform disclosures in PDFs into structured records, rather than simply classify isolated sentences. Moreover, the dataset contains long PDFs in Indonesian and English language, mixed text and numeric tables, various structures, and varying vocabularies in the same report. This dataset is necessary to evaluate whether ESG_ABSA can be used as-is on actual disclosure text.

This dataset answers the research questions in the following way. For the purposes of RQ1, the thesis requires document-level and page-level disclosures, which are available in the dataset. For the purposes of RQ2 and RQ3, this dataset provides text that can be classified in the desired manner. For RQ4, the dataset has enough variance in disclosures to demonstrate drifts, ontology gaps, schema inconsistencies, and instability.

In addition to the raw dataset, the repository contains a number of supplementary structured datasets: data/idx_data.csv, data/stock_info/, data/ESG Score.xlsx, and data/ontology_paths.json/. While they cannot be considered raw data, they represent methodological inputs because they are used by later stages to annotate extracted outputs.

### 3.2.1 Technical Characteristics and Sampling

As mentioned previously, the primary data source is at the document level, but the extraction process works in multiple layers. At the OCR stage, document is broken down into pages. At the extraction stage, pages are grouped into batches or contextualized as text units. At ground-truth and benchmark stages, extracted disclosures are analyzed and mapped to topics and tones. Finally, aspects extracted at the extraction stage are used for ontology mapping.

According to the latest evidence snapshot, there are 23 processed and extracted documents with a total of about 5,512 pages. The current dataset includes 332 extracted tone records, 2,074 T2 records, 70 pilot labels, and 1,220 evidence artifacts. These numbers are meant to be understood as a snapshot of the processed subset of the thesis corpus, not the total size of the thesis corpus.

Since the processed subset is selected not randomly but selectively, the sampling process consists of three steps. First, reports are gathered in the initial source dataset based on their relevance to ESG disclosure analysis. Second, documents are selectively extracted from the source dataset because the pipeline depends on the success of OCR extraction, page processing, batch processing, and audit capabilities. Finally, records are selected based on their informativeness and the ability to analyze disagreements.

### 3.2.2 Inclusion, Exclusion, and Evidence-Layer Boundaries

It is necessary to explicitly define the inclusion and exclusion criteria because they determine later evaluation claims. Documents are generally expected to include Indonesian sustainability reports and annual reports in a PDF format. Those documents are generally excluded from further analysis when OCR extraction fails or the pages generated by OCR cannot be used for downstream processing.

Text units (such as a sentence or page chunk) are included for processing by downstream systems based on their relevance for page-based extraction rather than any assumed informative content. Page extraction does not assume informative content, and thus it accepts all pages, even if no meaningful disclosure is present in the page. Once extracted disclosures become the subject of evaluation, malformed records are excluded, missing-tone records are excluded from downstream denominators, and unreliable disclosures are excluded because they are impossible to map.

As a result of these decisions, the dataset includes several distinct evidence layers: the corpus, the OCR-processed dataset, the actively processed subset, and a subset that was selected specifically for a particular analysis. The purpose of multiple layers is transparency: the thesis is evaluated by the ability to extract meaningful disclosures from Indonesian sustainability reports.

### 3.2.3 Ethics, Bias, and Data Limitations

This dataset is based on corporate disclosures, rather than personal information, and therefore the primary concern here is not individual privacy but data licensing, faithful reporting, and appropriate analysis. The methodology avoids misinterpreting generated records by preserving page-level provenance so that the generated statements can be verified against the source document.

Nevertheless, there are several potential sources of bias in this methodology. First, reports are included based on their availability, thus biasing the sample towards firms that publish and distribute machine-readable reports. Second, this subset of ESG reports may be biased towards some sectors rather than others. Third, the dataset may be biased towards environmental and governance disclosures relative to social disclosures. Fourth, bilingual or code-switched texts may be biased towards certain forms of disclosure language. Fifth, prompt templates may be biased towards certain disclosures rather than others.

In addition to biases, there are explicit limitations regarding the quality of the corpus. As indicated in the documentation of code_documentation.md, current limitations include OCR errors, inconsistent formatting, page duplication, table fragmentation, missing metadata, and OCR artifacts. The documentation also mentions that a more robust OCR and manual validation may be required. This limitation does not invalidate the pipeline; it just affects its generalizability.

## 3.3 Data Collection and Preprocessing Pipeline

Preprocessing pipeline is a critical part of the methodology because each subsequent classifier or ontology mapper depends on the quality and structure of intermediate artifacts.

### 3.3.1 OCR Expansion and First-Stage Extraction

The first preprocessing step is document OCR and page expansion. The system implements this functionality in pages/Bulk_OCR.py, pages/1_2_OCR_Quality_Workbench.py, and the OCR-expanded document folders in data/thesis_dataset/. The results of OCR are saved under ocr_result.json, and the system expands the document into pages. Specifically, ocr_result.json contains page-level array with metadata and markdown field among other fields. Pages themselves are saved in markdown as pages/page_0001.md.

Pages are chosen as a unit of analysis because page-level provenance is necessary for downstream analysis and manual auditing, and the system retains the flexibility to group pages into larger batches. This decision enables later traceability by allowing the system to trace each disclosure back to the original page.

### 3.3.2 Standardization, Storage, and Tooling

Standardization in this pipeline is implemented both as a methodology design principle and a tooling practice. Documents in PDF format are stored in the source folder data/thesis_pdf/. Expanded documents are stored in data/thesis_dataset/<document>/ocr_result.json, data/thesis_dataset/<document>/pages/, and data/thesis_dataset/<document>/images/. This structure enables easy linking of documents to their corresponding extracted artifacts and manual validation pages.

Storage standardization is extended to the repository code, where pages/llm_processing.py defines several constants for prompt location, expanded OCR location, results folder, and background job locations. Job statuses are preserved using control and status files and JSONL-like event logs. Again, storing job statuses is not merely an implementation issue but a methodology design decision, aimed at ensuring reproducibility.

### 3.3.3 Conversion into Structured ESG Records

Once the OCR expansion step is done, the system performs a first conversion step: converting OCR pages into structured disclosures. This is implemented in pages/llm_processing.py as a series of extraction requests sent from T3 and recorded under results/esg_records.json. T3 records typically contain metadata like timestamps, target pages, prompts, success status, parsing errors, and record-level information like text, aspect, labels, esg, tone, sentiment, sentiment score, and reasoning.

Conversion into structured record is the crucial step in this methodology because it generates a record that can later be benchmarked, filtered, mapped to ontology paths, or aligned against ClimateBERT records.

### 3.3.4 Alignment and Synchronization

This preprocessing methodology involves multiple layers of information: page-level markdown, extracted records, benchmark records, ontology nodes, and ClimateBERT-style outputs. After extraction is done, it becomes necessary to synchronize each output and its relationship to another output. First, extracted records should be synchronized back to the source document and page number. Second, benchmark records should be aligned back to the source text. Third, ontology nodes should be matched to the extracted record. Fourth, ClimateBERT outputs should be aligned to the record ID.

There are many places in the current repository where such synchronization occurs. For example, pages/2_2_LLM_Statement_Page_Verifier.py links the extracted record back to the page-level provenance. pages/1_4_ClimateBERT_Record_Batch.py preserves the unique record ID during ClimateBERT inference. code/data_alignment.py implements match_by_ids() and match_by_texts() to facilitate alignment by record ID or record text. The point is that all derived records should retain alignment to a concrete input record.

### 3.3.5 Preprocessing Quality Checks

The current system contains both automated and manual preprocessing checks. In terms of automated checks, pages/1_1_Page_Processing_Audit.py verifies the success of the OCR preprocessing pipeline. pages/2_3_T3_Parse_Success_Rate.py audits parse successes in extracted ESG records. pages/2_4_Missing_Json_Records.py identifies missing record fields. In terms of manual checks, the system provides Streamlit pages to facilitate the process. There is a workbench for auditing OCR preprocessing quality and a page-level processing audit. There is also a record-verifying page that links each statement back to the source page. Finally, there is ground truth annotation visualizer to verify benchmark records.

The dashboard report indicates that this step is operationally complete, but there is currently a recommendation to develop better OCR semantics. Specifically, there should be an estimate of page count per document. It would also be valuable to generate manually checked OCR samples of a few pages.

## 3.4 Feature Extraction and Representation Learning

Feature extraction process in this pipeline is complex because there is more than one class of features. Some features are explicit: lexical and ontological. Other features are latent: learned or semi-learned through transformer-based representation learning. Thus, this repository does not follow a single philosophy of features: it combines explicit features with contextual features.

### 3.4.1 Overall Feature Strategy

Four distinct classes of features are applied in this thesis workflow. First, rule-based features include lexical triggers and heuristics for aspect detection, tone detection, and polarity detection. Second, sparse textual features are used for classification through word- and character- n-gram TF-IDF vectors. Third, contextual transformer-based features are learned in section-aware contexts. Fourth, metadata-like features are applied in the form of section labels, ontology paths, page-level provenance, and ClimateBERT-style outputs.

All four classes of features are linked directly to the research objective. Lexical features enhance interpretability and serve as a solid baseline for classification. Sparse features are useful for implementing and evaluating classical machine learning classifiers. Transformer-based representations are useful for capturing semantic variance across different Indonesian and English disclosures. Metadata features link extracted outputs to ontology and make classification tasks easier.

### 3.4.2 Rule-Based Lexical Features

Rule-based feature extraction is implemented in code/rule_based.py and code/lexicons.py. Specifically, the system includes the following functions for detecting aspects, sentiment, and tone. collect_aspects() detects multiple aspect keywords using regex patterns. polarity_basic() calculates polarity using positive and negative word lists. tone_basic() detects tone using ordered lexical cues, which are preferentially detected in the following order: OUTCOME, ACTION, COMMITMENT, UNK. Each rule-based function produces an output in the form of a list.

Rule-based extraction is highly interpretable: it is possible to trace each output back to specific lexical triggers. The explain_rule_based_sentence() helper function takes text, polarity and tone labels, and provides a list of lexical triggers, which helps explain outputs. However, this method is vulnerable to errors in disclosure language and structure. First, there may be issues in phrasing. Second, there may be errors in bilingual code-switching.

### 3.4.3 Classical Sparse Text Features

Classical feature extraction is implemented in code/classical_ml.py. First, the system implements a Featureizer class, which combines word n-gram and character n-gram vectors through TF-IDF. Then, logistic regression is applied to train the multi-label classifier. Sentiment and tone classifiers implement one-vs-rest logistic regression, while aspect classifiers implement multi-label logistic regression. If the training is unsuccessful, the dummy classifier is applied.

Formally, if a sentence \(x\) is transformed into a sparse vector \(v(x)\),
the linear classifier computes scores of the form

\[
z_k = w_k^ v(x) + b_k
\]

for class \(k\), where \(w_k\) is the learned coefficient vector and \(b_k\)
is the intercept. The predicted class is derived from the highest score
threshold. This representation is appropriate because it gives the method a strong,
reproducible baseline. It also enables explanation of decisions because the
coefficient values and feature values can be multiplied to see which features
contribute the most to the decision.

### 3.4.4 Contextual and Hybrid Representations

The current system uses transformers and section embedding to learn semantic representations of a sentence, and to enrich those representations with contextual information. This is implemented in code/hybrid_model.py. By default, the system loads distilbert-base-multilingual-cased model, although it falls back to deterministic representations when this model fails. The transformer learns a fixed-size dense vector representation for
