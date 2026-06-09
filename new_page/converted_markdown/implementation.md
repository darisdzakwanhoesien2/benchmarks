# Chapter 3 Methodology

## 3.1 Research Design and Methodological Overview

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_01_overview}
\end{center}
\caption{High-level methodological flow adapted from the existing thesis workflow Mermaid diagrams in the repository.}
\alt{High-level workflow diagram showing the thesis methodology from source reports through OCR, extraction, validation, and thesis-ready evidence outputs.}
\label{fig:methodological_overview}
\end{figure}

![High-level methodological flow adapted from the existing thesis workflow Mermaid diagrams in the repository](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_01_overview.png)

This study adopts an executable mixed-method research design for automated ESG disclosure analysis over Indonesian sustainability and annual reports. The methodology is computational because the core workflow converts report PDFs into machine-readable evidence, extracts structured ESG records, classifies aspect-sentiment-tone signals, aligns outputs to an ontology, and evaluates stability across models and prompts. At the same time, it remains interpretive because the workflow preserves page-level provenance, supports manual review through Streamlit audit pages, and treats annotation, disagreement analysis, and failure inspection as part of the research method rather than only a post-processing step.

The central methodological strategy is a staged pipeline implemented in this repository. The pipeline begins with PDF ingestion and OCR, continues with page-aware LLM extraction, adds validation and representation layers through ClimateBERT-style comparison and ABSA-style processing, then produces thesis-ready evidence artifacts such as CSV summaries, JSONL benchmark files, visualizations, and audit tables. In this design, the main inputs are sustainability and annual report PDFs together with associated page markdown, OCR metadata, prompts, and ontology resources. The main outputs are structured ESG records in results/esg_records.json, stage-specific benchmark outputs such as results/t1_results.jsonl and results/t2_results.jsonl, ontology coverage tables, stability summaries, and dashboard exports under results/thesis_workflow_dashboard/ and results/revision_analysis/.

The design intentionally combines more than one methodological logic. First, it uses heuristic and weakly supervised components, including lexicon rules and ontology mappings, because a fully labeled Indonesian ESG corpus is not yet available. Second, it uses multiple LLMs and prompt templates as a comparative extraction strategy, since output quality depends not only on model family but also on prompt format and schema constraints. Third, it uses ClimateBERT-style labeling as an external semantic comparison layer rather than as a direct replacement for disclosure-tone analysis. This separation is important because climate-topic detection and disclosure maturity are related but not identical constructs.

This methodological direction is suitable for the research problem because ESG reports are long, bilingual or code-switched, structurally inconsistent, and often mix narrative claims with metrics, tables, governance boilerplate, and forward-looking commitments. A simple single-model classifier would hide those differences and make source auditing difficult. The proposed workflow instead prioritizes traceability, modularity, and cross-checking. Each page, run, record, and downstream artifact can be traced back to document folders in data/thesis_dataset/, page markdown files, and logged run metadata. This directly supports the thesis objective of building a tone-aware, ontology-aligned ESG analysis framework for Indonesian reports.

Traditional or simpler alternatives were considered implicitly in the implementation. A pure keyword system would be more deterministic but too brittle for bilingual reporting language. A single LLM prompt would be easier to run but would hide prompt sensitivity and schema drift. A ClimateBERT-only approach would provide climate-topic labels but would not distinguish commitment, action, and outcome tones. The implemented methodology therefore uses comparative prompts, multiple model families, rule-based baselines, classical machine learning, and a lightweight hybrid model as complementary components rather than mutually exclusive replacements.

At the level of research questions, the methodology addresses four linked goals: transforming PDFs into structured ESG evidence, defining aspect-pillar-sentiment-tone schema, comparing tone with ClimateBERT-style labels, and diagnosing instability or failure modes across prompts and models. Reproducibility and provenance are treated as thesis-wide support conditions for those four goals rather than as standalone research questions. Chapter 3 therefore focuses not on a single classifier in isolation, but on a complete methodological system that turns raw disclosures into auditable research evidence.

### 3.1.1 System Architecture

The repository documentation defines the workflow as an end-to-end research-data pipeline. Its operational architecture can be summarized as follows.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_01_01_system_architecture}
\end{center}
\caption{Executable system architecture of the repository, rewritten from the repository's Mermaid workflow documentation into a LaTeX-safe diagram.
  \copyrightstring\ \href{https://creativecommons.org/licenses/by/4.0/}{CC BY 4.0}.}
\alt{System architecture diagram showing the OCR layer, extraction layer, benchmarking layer, and analysis layer connected through repository artifacts and Streamlit pages.}
\label{fig:system_architecture}
\end{figure}

![Executable system architecture of the repository, rewritten from the repository's Mermaid workflow documentation into a LaTeX-safe diagram. CC BY 4.0](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_01_01_system_architecture.png)

The OCR layer creates page-level markdown and OCR JSON under data/thesis_dataset/<document>/. The extraction layer uses prompts stored in prompt/ and writes structured outputs and raw responses into results/esg_records.json and results/background_llm_jobs/. The ground-truth and benchmark layer writes resumable JSONL outputs to results/t1_results.jsonl and results/t2_results.jsonl. The analysis layer then produces ontology coverage, failure modes, prompt stability, model stability, and greenwashing-oriented summaries in results/revision_analysis/ and results/thesis_workflow_dashboard/.

This architecture is also reflected in the Streamlit surface. pages/Bulk_OCR.py manages ingestion, pages/llm_processing.py runs the combined T1-T2-T3 pipeline, pages/ground_truth.py manages resumable benchmark generation, pages/1_4_ClimateBERT_Record_Batch.py prepares one-to-one ClimateBERT comparison inputs, pages/1_6_Ontology_Path_Viewer.py inspects ontology assignments, and pages/1_0_Revision_Analytics.py consolidates diagnostics and stability evidence. The methodology chapter therefore describes a system that is both conceptual and executable.

### 3.1.2 Design Principles

Five design principles guide the methodology.

First, provenance is preserved at page and record level. Extracted outputs are always linked back to OCR-expanded documents and page markdown, and dedicated verifier pages exist to map structured statements back to their source pages.

Second, the system favors modular comparison over single-model dependence. Prompt families, model families, rule-based logic, classical ML, and hybrid transformer-based components are all retained so disagreement can be inspected rather than hidden.

Third, the pipeline is designed for bilingual robustness. Indonesian and English text may coexist within the same report or even the same segment, so the method uses multilingual preprocessing, bilingual prompts, and ontology resources that reduce cross-language drift.

Fourth, the method prioritizes interpretability together with automation. Lexical triggers, ontology paths, record-level reasoning fields, and audit tables are kept because the thesis is not only measuring output counts but also evaluating whether the outputs are credible and explainable.

Fifth, the workflow is reproducibility-oriented. Background jobs store status files and event logs, prompts are versioned as standalone markdown files, and dashboard outputs are exported into persistent result folders. This principle matters because the thesis relies on repeated reruns, prompt comparisons, and artifact regeneration rather than a single static experiment.

These principles lead directly to later technical decisions: page batching instead of isolated page inference, JSONL resumability for benchmark runs, ontology alignment after extraction, and separate treatment of topic labels, tone labels, and sentiment polarity.

## 3.2 Data Sources

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_02_data_sources}
\end{center}
\caption{Section-level diagram for the data-source stack used by the workflow.}
\alt{Data-source diagram showing raw PDF reports, OCR-expanded folders, metadata tables, ontology resources, and downstream analytical artifacts used by the workflow.}
\label{fig:data_source_stack}
\end{figure}

![Section-level diagram for the data-source stack used by the workflow](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_02_data_sources.png)

The primary data source is a corpus of sustainability and annual report PDFs stored in data/thesis_pdf/. According to the repository-wide inspection documented in code_documentation.md, this directory contained 193 PDF files at the time of inspection. These files form the raw document-level source for the thesis workflow. They are complemented by a machine-expanded corpus in data/thesis_dataset/, which contained 189 OCR-processed document folders at inspection time. Each processed folder typically includes ocr_result.json, a pages/ directory with page-level markdown such as page_0001.md, and an images/ directory with extracted image crops.

This dataset is appropriate for the research problem because the thesis studies how sustainability disclosures can be transformed into structured ESG evidence rather than how short isolated sentences can be classified in a clean benchmark setting. The corpus captures the real reporting environment: long reports, mixed Indonesian and English text, varied layout structure, numeric tables, narrative commitments, governance descriptions, and different sectoral vocabularies. That diversity is necessary for evaluating whether an ESG ABSA pipeline remains useful under realistic disclosure conditions.

The dataset also supports the research questions directly. For RQ1, it provides raw PDFs and OCR-expanded page units. For RQ2 and RQ3, it provides disclosure text that can be converted into aspect, pillar, sentiment, tone, and ClimateBERT-style comparison labels. For RQ4, it provides enough variability to observe schema drift, missing labels, ontology gaps, and model/prompt instability.

The repository includes additional structured support data. data/idx_data.csv and data/stock_info/ provide company and sector context. data/ESG Score.xlsx functions as an external benchmark or lookup source rather than as a native pipeline artifact. The main ontology and analysis-side derived resources are stored under results/revision_analysis/, including ontology.json, ontology coverage tables, prompt stability summaries, failure-mode tables, and pilot annotation files. These resources are not raw data in the same sense as the PDFs, but they are methodological inputs because later stages depend on them for mapping, validation, and evaluation.

### 3.2.1 Technical Characteristics and Sampling

The raw source data is document-based, but the effective unit of downstream computation changes by stage. OCR produces document folders and page markdown. LLM extraction operates on page batches or page-level contextual chunks. Ground-truth and benchmark stages operate on text units derived from extracted records. Ontology mapping operates on extracted aspects and record-level texts. This multi-level structure is necessary because no single unit is sufficient for all tasks.

The current workflow evidence snapshot  reports 23 completed OCR documents covering about 5,512 pages, 332 extracted tone records, 2,074 T2 rows, 70 pilot labels, and 1,220 result artifacts. These numbers should be interpreted as the active experimental evidence layer used by the thesis dashboard, not as the total raw corpus size. In other words, the repository contains a larger raw and OCR-expanded inventory, while the dashboard snapshot represents the currently processed and thesis-integrated subset.

Selection is therefore partly corpus-driven and partly workflow-driven. Reports are collected because they are relevant to Indonesian ESG disclosure analysis, but the final processed subset is also shaped by practical constraints such as OCR completion, page-batch processing, background job success, and the availability of downstream annotation and validation capacity. This is consistent with the repository design, which stores both large-scale source inventory and smaller thesis-ready evidence layers.

### 3.2.2 Inclusion, Exclusion, and Evidence-Layer Boundaries

The study uses different inclusion and exclusion logic at different stages, and these boundaries need to be stated explicitly because later evaluation claims depend on them. At document level, the broad inclusion target is Indonesian sustainability or annual reporting material available as machine-processable PDF files in the thesis corpus. Documents are excluded from the active experimental subset when OCR expansion is incomplete, page structure is too unstable for downstream use, or later extraction and audit stages have not yet produced reusable artifacts.

At page and text-unit level, inclusion is based on usability for provenance-preserving extraction rather than on an assumption that every page contains ESG evidence. Pages may still enter OCR storage even if they later prove non-informative. In contrast, extracted-record evaluation excludes malformed outputs, explicit missing-tone failures for some downstream denominators, and records that cannot be aligned reliably enough for the specific comparison being reported. This means that the thesis uses several evidence layers rather than a single monolithic dataset: the raw PDF inventory, the OCR-expanded inventory, the active thesis-facing subset, and the smaller reviewed or comparison-ready subset used in specific tables.

The purpose of these boundaries is methodological transparency rather than aggressive filtering. The thesis does not claim that the current active subset is a statistically representative sample of all sustainability reports. Instead, it claims that this subset is sufficient to evaluate whether the implemented workflow can operate on long, noisy, bilingual reports and reveal its main strengths and weaknesses.

### 3.2.3 Ethics, Bias, and Data Limitations

The corpus is based on corporate reports rather than private personal data, so the main ethical concerns are not individual privacy but rather licensing boundaries, faithful source tracing, and fair interpretation of corporate disclosures. The methodology mitigates evidential misuse by retaining provenance links from structured outputs back to report pages. This reduces the risk that generated records are discussed without access to their source context.

Several biases remain. First, the corpus is biased toward firms that produce machine-accessible reports and toward sectors with stronger reporting practices. Second, environmental and governance language appears more strongly represented than social disclosures in the current evidence snapshot, which may affect downstream tone and aspect distributions. Third, bilingual and code-switched language can produce uneven extraction quality because the same disclosure function may be expressed differently across Indonesian and English segments. Fourth, prompt-dependent extraction can introduce representation bias if one template systematically omits certain fields.

Data quality limitations are explicitly acknowledged in the repository. OCR noise, inconsistent formatting, page duplication, table fragmentation, and missing or unstable JSON fields can all affect downstream outputs. The thesis dashboard also notes a current need for stronger OCR baselines and formal manual validation. These limitations do not invalidate the workflow, but they do affect generalizability and motivate the use of diagnostics, review queues, and pilot annotation rather than overclaiming final benchmark performance.

## 3.3 Data Collection and Preprocessing Pipeline

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_02_02}
\end{center}
\caption{Mermaid-derived preprocessing sequence from PDF ingestion to auditable ESG-ready text units.}
\alt{Preprocessing sequence diagram showing PDF ingestion, OCR expansion, page-level markdown generation, storage, and conversion into extraction-ready text units.}
\label{fig:preprocessing_sequence}
\end{figure}

![Mermaid-derived preprocessing sequence from PDF ingestion to auditable ESG-ready text units](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_02_02.png)

The preprocessing pipeline converts raw PDFs into analyzable page units and then into extraction-ready text batches. This stage is methodologically important because every later classifier or ontology mapper depends on the quality and structure of these intermediate artifacts.

### 3.3.1 OCR Expansion and First-Stage Extraction

The first transformation is document OCR and structural extraction. The repository documents this stage through pages/Bulk_OCR.py, pages/1_2_OCR_Quality_Workbench.py, and the OCR-expanded folders in data/thesis_dataset/. Each processed report yields an ocr_result.json file containing page arrays and fields such as markdown text, images, tables, hyperlinks, dimensions, and confidence-related metadata. In parallel, the system writes page-level markdown files under pages/, which are the most commonly reused unit in downstream page audits and page-batch inference.

The unit of analysis at this point is the page. This choice is appropriate because later provenance checks require the workflow to map structured ESG statements back to specific page files, and page-level markdown provides a stable and auditable representation of the original report. At the same time, the system does not restrict itself to single-page inference; page-level files can be grouped into page batches when additional context is needed.

### 3.3.2 Standardization, Storage, and Tooling

The preprocessing outputs are standardized around a reproducible directory structure. Raw source PDFs remain in data/thesis_pdf/. OCR-expanded artifacts are stored in data/thesis_dataset/<document>/ocr_result.json, data/thesis_dataset/<document>/pages/, and data/thesis_dataset/<document>/images/. This structure allows downstream workers to resolve a document folder, inspect its pages, and trace extraction failures to specific files.

The methodological logic is also standardized in code. pages/llm_processing.py defines repository constants for the prompt directory, OCR output directory, results directory, and background-job directory. Background jobs are launched through code/llm_background_worker.py, while run state is preserved through status.json, control.json, and JSONL-like event logs under results/background_llm_jobs/. This storage logic is not incidental implementation detail; it is part of the reproducibility design because it ensures that extraction can be resumed, audited, and compared across runs.

### 3.3.3 Conversion into Structured ESG Records

After OCR, the next conversion is from page text into structured ESG records. In pages/llm_processing.py, the T3 extraction stage sends contextualized text to LLM backends and appends results to results/esg_records.json. Each run object can store metadata such as timestamp, model, target pages, prompt, success status, parsed records, raw output, and error information. When successful, record-level fields may include text, aspect, labels, esg, tone, sentiment, sentiment_score, and reasoning.

This conversion stage is central to the methodology because it creates the canonical evidence layer used by the rest of the system. Instead of treating extracted text as an unstructured blob, the workflow transforms it into schema-bearing records that can later be benchmarked, filtered, aligned to ontology paths, or compared against ClimateBERT outputs.

### 3.3.4 Alignment and Synchronization

The workflow combines several data layers that must be aligned after extraction. First, extracted records must remain linked to their source document and source pages. Second, T1 and T2 benchmark outputs must be aligned back to the record texts or labels they were derived from. Third, ontology mapping must connect extracted aspects to canonical ontology paths. Fourth, external comparison labels such as ClimateBERT-style outputs must preserve stable record identifiers for later agreement analysis.

This alignment logic is visible in multiple parts of the repository. pages/2_2_LLM_Statement_Page_Verifier.py maps extracted statements back to OCR page markdown. pages/1_4_ClimateBERT_Record_Batch.py explicitly preserves record_id for one-to-one ClimateBERT comparison runs. code/data_alignment.py implements matching utilities for aligning reference labels, ABSA outputs, and benchmark outputs by text or related identifiers. The alignment unit therefore varies by task, but the underlying principle is stable: every derived label should remain recoverable to a concrete upstream artifact.

### 3.3.5 Preprocessing Quality Checks

The repository includes both manual and automated quality checks. Automated checks appear in OCR processing summaries, page processing audits, parse-success tables, and missing-field diagnostics. Manual checks are supported through Streamlit inspection pages such as the OCR quality workbench, page-level processing audit, statement-to-page verifier, and ground-truth review visualizers.

The dashboard report indicates that OCR ingestion is operationally complete for the active subset, but it also notes the need for stronger semantic baselines such as page-count parity checks and small manually reviewed OCR samples. This is methodologically important: preprocessing quality is treated as a measured risk rather than an invisible assumption. The final preprocessed dataset is therefore not just the collection of OCR files, but the subset that passes through enough audit steps to be usable for extraction and benchmarking.

## 3.4 Feature Extraction and Representation Learning

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_04}
\end{center}
\caption{Section-level diagram summarizing how explicit, sparse, contextual, and ontology-aware features are combined.}
\alt{Feature-extraction diagram showing lexical rules, TF-IDF features, contextual embeddings, and ontology-aware representations feeding into the ESG analysis workflow.}
\label{fig:feature_strategy}
\end{figure}

![Section-level diagram summarizing how explicit, sparse, contextual, and ontology-aware features are combined](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_04.png)

Feature extraction in this study is multi-layered. Some features are explicit and interpretable, such as lexical triggers, aspect keywords, and ontology paths. Others are learned or semi-learned, such as TF-IDF vectors, transformer embeddings, and hybrid fused representations. The repository does not rely on one single feature philosophy; instead, it combines surface features and contextual features because ESG report language contains both formulaic disclosure patterns and semantically nuanced claims.

### 3.4.1 Overall Feature Strategy

The extracted feature groups can be divided into four categories. The first group contains lexical and rule-based indicators used for aspect, polarity, and tone heuristics. The second group contains classical sparse text representations built from word and character n-gram TF-IDF. The third group contains contextual multilingual sentence embeddings and section-aware representations. The fourth group contains metadata-like supporting features such as ontology paths, source section labels, page linkage, and comparison labels from ClimateBERT-style inference.

These feature groups are connected directly to the research objective. Lexical features improve interpretability and provide a transparent baseline. Sparse features support classical machine learning comparisons. Contextual embeddings capture semantic variation across Indonesian, English, and mixed disclosures. Ontology and metadata features connect extracted outputs to ESG-specific interpretive structure and later evaluation tasks.

### 3.4.2 Rule-Based Lexical Features

The rule-based component is implemented in code/rule_based.py with supporting lexicons in code/lexicons.py. The method matches disclosure text against predefined aspect lexicons and tone/polarity trigger lists. collect_aspects() assigns one or more aspect labels by matching regular-expression patterns. polarity_basic() uses positive and negative word lists to assign a simple polarity label. tone_basic() uses ordered lexical cues to assign disclosure tone, prioritizing Outcome over Action over Commitment, and returning Unknown when no strong cue is found.

This feature group is highly interpretable because every decision can be tied to a lexical trigger. The helper explain_rule_based_sentence() returns matched aspect, sentiment, and tone triggers for a sentence, which is useful for explainability outputs in later chapters. The limitation is that rule-based matching can be brittle, especially under bilingual phrasing, code-switching, implicit claims, or complex sentence structure.

### 3.4.3 Classical Sparse Text Features

The classical ML component is implemented in code/classical_ml.py. It builds a Featureizer that combines word n-gram TF-IDF with character n-gram TF-IDF. Word n-grams capture lexical and short-phrase disclosure patterns, while character n-grams add robustness to spelling variation, morphology, and OCR noise. After vectorization, the method trains one-vs-rest logistic regression for multi-label aspects and logistic regression or dummy fallbacks for sentiment and tone.

Formally, if a sentence \(x\) is transformed into a sparse vector \(v(x)\),
the linear classifier computes scores of the form

\[
z_k = w_k^ v(x) + b_k
\]

for class \(k\), where \(w_k\) is the learned coefficient vector and \(b_k\)
is the intercept. The predicted class is derived from the highest or thresholded score depending on the task. This representation is appropriate because it provides a strong, reproducible baseline and makes coefficient-based explanations possible. The code also includes local explanation logic that multiplies active feature values by model coefficients to show which terms contributed most strongly to a prediction.

### 3.4.4 Contextual and Hybrid Representations

The contextual representation layer is implemented in code/hybrid_model.py. This module uses a small multilingual transformer encoder, defaulting to distilbert-base-multilingual-cased when available, and falling back to deterministic embeddings if the transformer cannot be loaded. Sentence embeddings are pooled from transformer outputs, then passed into a HierarchicalEncoder that incorporates section-type embeddings and cross-section attention. This allows the method to capture not only the local sentence meaning but also document-structure context.

The hybrid model then fuses four information sources: sentence vectors,
contextual section vectors, ontology vectors, and a document vector. In the
 class, the fused representation is formed by concatenation
followed by a nonlinear projection:

\[
h_i = f([s_i ; c_i ; o_i ; d])
\]

where \(s_i\) is the sentence vector, \(c_i\) is the contextual section vector,
\(o_i\) is the ontology vector, \(d\) is the document-level vector, and
\(f()\) is the learned fusion network. Separate output heads then predict
sentiment and tone. This representation is appropriate because ESG disclosure
meaning is often shaped by both local phrasing and broader section context,
for example when a metric appears inside a target-setting section or a
governance compliance section.

### 3.4.5 Ontology-Based Feature Enhancement

Ontology alignment is used as a feature enhancement and interpretive layer rather than only as a final visualization step. In the rule-based pipeline, canonical ontology paths are attached using CANON_PATHS. In the hybrid pipeline, ontology nodes are embedded and projected into the fused representation. The workflow documentation also describes ontology resources as including pillar, aspect, sub-aspect, synonym, and regulatory-anchor information.

This enhancement improves the representation in two ways. First, it regularizes semantically similar disclosures under common ESG concepts. Second, it makes outputs regulator-readable and more interpretable by mapping extracted aspects to structured paths rather than leaving them as free-text labels only. The main limitation is ontology scope: if an Indonesian-specific disclosure topic is absent from the current ontology resources, the mapping may still be incomplete or overly generic.

## 3.5 Proposed Framework

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_05}
\end{center}
\caption{Conceptual split between record generation and validation-comparison within the proposed framework.}
\alt{Framework diagram separating LLM-centered ESG record generation from the downstream validation, benchmarking, and comparison layers.}
\label{fig:framework_split}
\end{figure}

![Conceptual split between record generation and validation-comparison within the proposed framework](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_05.png)

The proposed framework is not a single standalone classifier but a composite methodological system centered on a structured ESG evidence store. The extracted features described above are used in two main ways: first, to generate structured records from report text; second, to evaluate and refine those records through comparison, benchmarking, and ontology-aware analysis.

### 3.5.1 Framework 1: LLM-Centered ESG Record Generation

The first framework is the page-aware LLM extraction workflow implemented primarily in pages/llm_processing.py and code/llm_background_worker.py. Its purpose is to convert OCR-expanded report text into structured ESG records with fields such as text span, aspect, pillar, tone, sentiment, and reasoning. The framework accepts document or page-batch inputs, combines them with prompt templates, sends requests to configured model backends, and writes normalized outputs into results/esg_records.json.

The implemented prompt inventory shows multiple prompt families, including zero-shot, few-shot, chain-of-thought, and tone-specific variants in both Indonesian and English, plus data-oriented prompt files such as data.md and data_v1.md. This comparative prompt design allows the framework to test whether output quality depends on schema framing, language, or reasoning style.

At a high level, the framework processes a batch
\(B = \{p_1, , p_n\}\) of page texts under prompt template \(q\)
and model \(m\) to produce a structured output set \(R\):

\[
R = F(B, q, m)
\]

where \(F\) denotes the end-to-end extraction function. In practice,
\(R\) is accepted only if it can be parsed into the expected record
schema. Otherwise, the run is preserved with error metadata for later
audit rather than silently discarded.

### 3.5.2 Framework 2: Benchmarking, Comparison, and Evidence Scoring

The second framework is the validation and comparison layer built around T1 and T2 outputs, ClimateBERT-style comparison, and ontology-aligned diagnostics. pages/ground_truth.py loads extracted texts from results/esg_records.json, derives benchmark text units, and writes resumable outputs to results/t1_results.jsonl and results/t2_results.jsonl. T1 focuses on ClimateBERT or local classification-style outputs, while T2 captures rule-based or hybrid ABSA-oriented labels and related processing.

The design uses JSONL because each processed item can be appended independently and resume logic can skip already complete records. load_processed_t1() and load_processed_t2() use stable keys such as label-model pairs or labels alone to avoid rerunning completed items. This matters methodologically because benchmark generation may be interrupted by model availability, long-running jobs, or partial failures, and the study needs a reproducible way to continue from the last valid state.

Evidence from multiple sources is then combined downstream. The workflow compares tone labels against ClimateBERT-style labels, maps extracted aspects to ontology paths, measures missing-tone and schema-drift rates, and preserves disagreement cases for manual review. The scoring logic is therefore not a single scalar objective but a collection of evidence-quality indicators: parse success, field completion, label agreement, ontology coverage, and failure-mode distribution.

### 3.5.3 Inference and Output Mapping

Inference in the overall system means more than generating a label. It includes mapping model outputs back into actionable thesis artifacts. For T3 extraction, raw outputs are parsed into structured records. For T1 and T2 benchmarking, JSONL outputs are mapped back to labels and record texts. For ontology analysis, extracted aspects are mapped to canonical paths. For provenance checks, statements are mapped back to page markdown. For dashboard reporting, all of these outputs are aggregated into CSV summaries, graphs, and narrative evidence tables.

This mapping step is essential because the thesis aims to produce usable disclosure evidence rather than isolated classification scores. A predicted tone label has limited value if it cannot be tied back to a record, source page, ontology path, and comparison context. The implemented framework therefore treats output mapping as part of the methodological core.

## 3.6 Ground Truth, Weak Labels, and Evaluation Reference

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_06}
\end{center}
\caption{Layered evaluation-reference construction used when a full expert gold corpus is not yet available.}
\alt{Reference-construction diagram showing extracted records, weak labels, pilot human annotations, and ClimateBERT-style comparison signals combined into a layered evaluation framework.}
\label{fig:reference_construction}
\end{figure}

![Layered evaluation-reference construction used when a full expert gold corpus is not yet available](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_06.png)

True expert-labeled reference data does not yet exist for the full corpus. This is one of the central methodological constraints of the study, and the repository is designed around that constraint rather than ignoring it. The workflow therefore uses a layered reference strategy: weak labels from extraction outputs, benchmark outputs in JSONL form, pilot human annotation files, and comparison labels from ClimateBERT-style runs.

### 3.6.1 Why a Special Reference Construction Process Is Needed

Existing outputs are not sufficient to act as final gold labels. The extracted record layer is generated by prompts and models that can drift in schema, omit fields, or disagree across templates. ClimateBERT-style labels are useful as an external comparison signal but do not fully capture disclosure tone. Human annotation is available only in pilot form. As a result, the study requires a special reference-construction process that balances automation with manual oversight.

The dashboard snapshot confirms this limitation. It reports 70 pilot labels and explicitly notes the need for stronger human-coded baselines, disagreement examples, and broader evaluation coverage. The methodology therefore treats reference construction as iterative: weak labels support early experimentation, pilot labels support focused validation, and future expansion can move toward a stronger stratified gold set.

### 3.6.2 Reference Generation Procedure

Reference generation begins with extracted records in results/esg_records.json. pages/ground_truth.py converts top-level text fields, nested record texts, and parseable raw outputs into benchmark text units. These units are then processed by T1 and T2 pipelines, with outputs appended line-by-line into results/t1_results.jsonl and results/t2_results.jsonl. The use of JSONL makes the process resumable and auditable.

For T1, the system can call a ClimateBERT client when available or use local model alternatives discovered from the model cache. For T2, rule-based and hybrid logic provide tone, sentiment, and ontology-related outputs. In addition, pages/1_4_ClimateBERT_Record_Batch.py prepares one-to-one record batches for external ClimateBERT validation, explicitly preserving record_id so imported outputs can be aligned back to the original records.

Human review enters through the pilot annotation files and review-oriented Streamlit pages. results/revision_analysis/pilot_ground_truth_seed.csv provides an annotation scaffold, while pilot_ground_truth_annotations.csv stores reviewed labels. These artifacts do not yet form a complete gold corpus, but they are sufficient to support targeted inspection, early agreement analysis, and the identification of difficult cases.

### 3.6.3 Validation, Constraints, and Current Limitations

Generated references are validated through a combination of structural and semantic checks. Structurally, a record is considered complete only if expected labels are present and no explicit error state is stored. Semantically, agreement pages and review queues inspect whether tone, sentiment, and ClimateBERT-style labels are coherent or contradictory. Provenance pages further constrain the outputs by checking whether extracted statements can be found in the OCR source text.

The current reference layer nevertheless has important limitations. Weak labels remain model-dependent. Prompt sensitivity affects which records are extracted in the first place. OCR quality is operationally tracked but not yet fully benchmarked with formal CER or WER across the active subset. Ontology coverage, while strong in the current dashboard snapshot, still depends on the scope of the existing ontology resources. For these reasons, the study does not claim a finalized gold-standard benchmark. Instead, it claims an auditable and extensible reference-construction process suitable for iterative thesis research.

## 3.7 Threats to Validity and Reproducibility Boundaries

Internal validity is limited by the evolving nature of the research workspace. Prompt refinement, model comparison, ontology expansion, and review-oriented diagnostics were developed iteratively in the same repository. This improves engineering transparency, but it also means the thesis should not be read as a fully frozen benchmark in which development and evaluation were perfectly isolated from the beginning.

Construct validity is limited by the fact that disclosure tone, sentiment polarity, climate-topic labels, and greenwashing-oriented ratios are related but non-identical constructs. The thesis mitigates this by keeping those layers separate analytically, but it cannot eliminate the underlying conceptual overlap entirely. ClimateBERT-style commitment outputs are therefore treated as an external semantic comparison signal rather than as definitive reference truth for tone.

External validity is limited by domain concentration. The active evidence layer is drawn from Indonesian sustainability and annual reports, often with bilingual or mixed-language phrasing and sector-specific reporting conventions. The findings therefore support claims about this setting more strongly than claims about other regulatory, linguistic, or sectoral environments.

Reproducibility is strong at the level of stored artifacts, prompts, logs, and resumable outputs, but weaker at the level of exact semantic reruns for third-party LLMs. Model availability, provider-side updates, and stochastic generation behavior can alter future outputs even when the repository preserves prompt files and artifact paths. For that reason, the thesis claims reproducible workflow structure and reproducible evidence storage more confidently than perfectly identical future outputs.

## 3.8 Chapter Summary

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_07_summary}
\end{center}
\caption{Summary diagram of the chapter's end-to-end methodological contribution.}
\alt{Summary diagram showing the end-to-end methodological contribution from report ingestion through structured ESG evidence generation, validation, and thesis reporting.}
\label{fig:methodology_summary}
\end{figure}

![Summary diagram of the chapter's end-to-end methodological contribution](https://github.com/darisdzakwanhoesien2/benchmarks/blob/main/new_page/report_standardized/Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/03_07_summary.png)

This chapter has described an executable methodology for Indonesian ESG disclosure analysis. The workflow begins with PDF reports, expands them into OCR-based page artifacts, transforms those artifacts into structured ESG records through comparative LLM prompting, enriches the records through rule-based, classical ML, and hybrid contextual representations, aligns them to ontology paths and ClimateBERT-style comparison labels, and preserves the full process in reproducible result stores and dashboard artifacts.

Methodologically, the contribution of this design is not only that it automates extraction, but that it does so in a way that remains auditable, modular, bilingual-aware, and compatible with partial reference data. The next chapter can therefore focus on implementation and results using a clearly defined data flow, model structure, and evaluation reference layer grounded in the code and artifacts of the repository.
