# Chapter 3: Methodology

## 3.1. Overview of the Methodology

This study adopts an executable, artifact-centered methodology for building and evaluating an ESG aspect-based sentiment analysis (ABSA) pipeline for Indonesian sustainability disclosures. In the language of the broader thesis draft, the system functions as an executable research workspace rather than a single-purpose classifier. The methodological design is not limited to model training or one-off text classification. Instead, it treats the research process as a sequence of linked computational stages that begin with source-document acquisition and end with thesis-ready analytical outputs. The core motivation for this design is that ESG disclosure analysis in practice is constrained by heterogeneous file formats, bilingual reporting, inconsistent document structure, varying disclosure quality, and the absence of a large expert-labeled benchmark tailored to Indonesian corporate reporting. A defensible methodology therefore must manage both the data-engineering problem and the analytical-validation problem.

The pipeline implemented in this repository reflects that requirement. Source PDF reports are first collected and converted into page-level textual artifacts through OCR and document-structure-aware processing. The resulting text units are then passed through extraction and normalization stages that aim to identify ESG-relevant statements, assign structured fields, and preserve provenance back to the original source document and page. Downstream layers use these records for ground-truth annotation, ClimateBERT comparison, ontology alignment, diagnostics, and thesis synthesis. The research workflow is therefore cumulative: each stage produces artifacts that can be inspected, reused, audited, and extended by later stages.

Methodologically, the unit of analysis is the ESG disclosure record rather than the full report. This decision is central to the thesis. A document-level ESG score is too coarse to distinguish between qualitatively different disclosure behaviors. A company may express an intention, describe an operational action, report a realized outcome, or provide neutral descriptive background within the same report. The thesis therefore treats each extracted record as a distinct evidence unit with attributes such as text span, page provenance, ESG pillar, aspect, sentiment, tone, prompt template, and model source. This record-level design enables fine-grained analysis of disclosure language, including commitment-action-outcome distinctions that are necessary for greenwashing-sensitive interpretation.

The methodology is also layered. It combines:

- source-document ingestion and OCR,
- LLM-based structured extraction,
- ABSA-oriented field normalization,
- model-comparison and proxy-validation workflows,
- ontology-grounded interpretation,
- and reproducibility-oriented documentation.

This layered design is intentional. OCR is necessary because the study corpus contains PDF documents with potentially complex layouts, tables, headers, and multilingual text. LLM extraction is necessary because many ESG disclosures are semantically rich but structurally inconsistent, making fixed-rule extraction too brittle. Ground-truth and comparison layers are necessary because extracted outputs alone do not provide sufficient evidence of validity. Ontology alignment is necessary because ESG interpretation must move beyond generic sentiment and connect statements to recognizable sustainability concepts and frameworks. Documentation and reproducibility layers are necessary because a thesis contribution must remain auditable after the experiments are completed.

The current repository already operationalizes this methodology through a set of Streamlit pages and persisted artifacts. For Chapter 3, the most relevant workflow anchors are:

- `pages/Bulk_OCR.py` for PDF-to-text conversion,
- `pages/llm_processing.py` for ESG record extraction,
- `pages/ground_truth.py` and `pages/1_1_Ground_Truth_Workbench.py` for annotation workflows,
- `pages/1_4_ClimateBERT_Record_Batch.py` and `pages/0_9_Tone_ClimateBERT_Visualization.py` for model comparison,
- `pages/1_6_Ontology_Path_Viewer.py` for ontology interpretation,
- `pages/2_1_LLM_Error_Parse_Audit.py` and `pages/2_4_PDF_Page_Processing_Audit.py` for diagnostics,
- and `pages/0_0_Streamlit_Page_Workflow.py` for thesis-facing workflow integration.

The methodology is therefore best understood as a reproducible research-data system and executable research workspace rather than a single classifier. It supports the thesis claim that ESG ABSA for Indonesian disclosures requires a controlled end-to-end pipeline capable of preserving provenance, handling bilingual and semi-structured data, comparing alternative extraction strategies, and surfacing limitations explicitly. This chapter focuses on three major methodological foundations: the data sources, the reasoning behind corpus and artifact selection, and the preprocessing pipeline that turns raw source material into structured, auditable analytical inputs.

## 3.2. Data Sources

The data sources used in this study are heterogeneous by design. They include raw source documents, intermediate preprocessing outputs, extraction artifacts, and validation-oriented derivative datasets. This is necessary because the thesis investigates not only final ESG labels but also the transformation process by which unstructured sustainability reports are converted into structured evidence. The data strategy is therefore multi-layered: each source category corresponds to a different stage in the pipeline and serves a different methodological role.

At the source-document level, the primary corpus consists of sustainability reports, annual reports, and related ESG disclosure PDFs associated with Indonesian companies. These reports are the empirical basis of the study because they contain the natural-language statements from which ESG aspect, sentiment, and tone evidence must be extracted. The source documents are stored as report-level files and then transformed into page-level markdown and OCR artifacts for downstream use. In the project inventory, this source layer is represented by folders such as `data/thesis_pdf/` and `data/thesis_dataset/`, as documented in the repository’s data inventory notes.

At the preprocessing layer, OCR-derived text and page-level artifacts serve as the effective textual corpus for extraction. The repository documentation describes artifacts such as:

- `ocr_result.json` per document,
- markdown page files under `data/thesis_dataset/<doc>/pages/`,
- image and table references,
- and page audit outputs.

These artifacts are important because the extraction system does not operate directly on raw PDFs. Instead, it operates on OCR-transformed, page-aware text units that preserve layout traceability and make audit sampling possible.

At the extraction layer, the study uses structured ESG outputs generated by the LLM pipeline. The central role is played by record-level outputs such as `results/esg_records.json` and flattened dashboard tables derived from that file. The existing thesis-facing summary in `thesis_paper_esg_absa.md` notes currently tracked evidence including:

- 23 OCR documents,
- 332 structured ESG tone records,
- 2,074 T2 rows,
- 40 tracked artifacts in the workflow dashboard,
- prompt-stability and model-stability summaries,
- ontology coverage tables,
- ClimateBERT comparison outputs,
- and ground-truth plus silver-label tables.

These numbers should be treated as the current state of the working corpus rather than a final benchmark claim. Methodologically, they show that the system already contains enough variation to study extraction behavior, label distributions, and failure modes, even though the gold-standard annotation layer is still incomplete.

At the validation layer, the data sources include silver-labeled and human-editable files used for auditing and comparison. These include artifacts such as:

- `results/revision_analysis/silver_tone_ground_truth.csv`,
- pilot annotation CSVs,
- `results/t1_results.jsonl`,
- `results/t2_results.jsonl`,
- coverage tables,
- disagreement views,
- and review queues.

These are not just convenience files. They are methodological instruments for assessing the completeness, consistency, and interpretability of the extracted records.

At the ontology and semantic layer, the data sources include mapping files and graph exports used to relate extracted records to ESG concepts and regulatory anchors. Examples documented in the repository include:

- `results/semantic_exports/esg_thesis_graph.ttl`,
- `results/semantic_exports/esg_thesis_ontology.owl`,
- `results/semantic_exports/neo4j_nodes.csv`,
- `results/semantic_exports/neo4j_relationships.csv`,
- ontology coverage tables,
- and JSON-based ontology maps.

These artifacts support the thesis objective of moving from isolated labels toward structured ESG knowledge representation.

Finally, the study also uses auxiliary metadata sources, including company information, workflow dashboards, and API-derived reference data. The repository documentation highlights sources such as:

- `data/stock_info`,
- `data/ESG Score.xlsx`,
- `results/api_reader/` snapshots,
- and the Streamlit workflow documentation under `documentation/streamlit_pages/`.

These auxiliary sources support contextualization, reproducibility, and future extension, even when they are not directly used as model inputs.

Taken together, the study’s data sources form a layered corpus architecture:

1. Raw disclosure PDFs as empirical source material.
2. OCR and page-level markdown as extraction-ready text.
3. Structured ESG records as the core analytical dataset.
4. Ground-truth, silver-label, and benchmark artifacts as the validation dataset.
5. Ontology and semantic exports as the interpretation and explainability dataset.
6. Workflow and metadata artifacts as the reproducibility dataset.

This structure is methodologically appropriate because the thesis is concerned with the full transformation path from report document to auditable ESG evidence, not only the final prediction result.

### 3.2.1. Dataset Characteristics

The dataset is best described as a bilingual, document-derived, multi-artifact ESG disclosure corpus. It is not a conventional single-table benchmark prepared in advance. Instead, it is a working research corpus generated progressively through the pipeline. Several characteristics define its methodological profile.

First, the corpus is document-centered at intake but record-centered at analysis. The raw input units are PDF reports, yet the analytical outputs are record-level ESG statements extracted from those reports. This means that the dataset contains a hierarchical structure:

- document level,
- page level,
- batch or run level,
- and record level.

This hierarchy is useful because it preserves the link between a final ESG statement and the document context from which it came. Provenance is particularly important when analyzing sustainability reports because similar wording can have different implications depending on section placement, reporting scope, or neighboring text.

Second, the corpus is bilingual and mixed-language. The project notes and methodology references consistently describe the thesis as targeting Indonesian and English disclosures, including reports where both languages may appear within the same document or across different sections. This affects preprocessing, model prompting, and interpretation. Bilingual handling is not a superficial translation issue; it changes how aspect terms, regulatory references, and sentiment cues must be normalized. For this reason, the dataset should be understood as multilingual at the text level, not just multinational at the company level.

Third, the corpus is semi-structured. Sustainability reports combine narrative prose, tables, bullet lists, headings, captions, and page artifacts. OCR output may therefore contain layout noise, broken sentences, duplicated headers, fragmented tables, or page-number text. The dataset is consequently not a clean natural-language corpus in the usual NLP sense. It is a transformed corporate-report corpus with known layout-related risks. This characteristic justifies the emphasis on page-level audit and preprocessing controls.

Fourth, the corpus is weakly supervised in its current state. Some records have silver labels, some have human-editable annotation fields, and some participate in proxy comparison workflows such as ClimateBERT alignment. However, the repository documentation also makes clear that the full expert-labeled benchmark does not yet exist. Therefore, the dataset should not be framed as a finalized gold-standard corpus. It is more accurately described as a staged benchmark-construction dataset that already supports exploratory evaluation, diagnostics, and thesis reporting, while still requiring further annotation for stronger inferential claims.

Fifth, the corpus is artifact-rich. It includes not only text and labels but also multiple derivative tables and exports. Current tracked examples include:

- `tone_records_flat.csv`,
- `tone_esg_crosstab.csv`,
- `tone_climatebert_label_crosstab.csv`,
- `model_stability_summary.csv`,
- `prompt_stability_summary.csv`,
- `ontology_coverage.csv`,
- annotation CSVs,
- and semantic graph exports.

This means the dataset is not only used for predictive modeling but also for methodological introspection. The same corpus can be viewed through distributional, validation, ontology, and reproducibility lenses.

Sixth, the current dataset scale is pilot-to-intermediate rather than large-scale industrial. The tracked 23 OCR documents and 332 structured ESG tone records provide a meaningful empirical basis for a thesis prototype, especially because the focus is on methodology, pipeline design, and auditability. However, these counts also indicate that the current corpus is still better suited for exploratory evaluation and controlled discussion than for broad population-level generalization. This limitation does not weaken the methodological contribution; rather, it clarifies the scope of the present chapter.

Seventh, the dataset is version-sensitive. Because records are generated through OCR, prompts, models, and downstream normalization, the corpus can change when any stage changes. Different prompt templates, providers, parser revisions, or preprocessing rules may produce different numbers of records or different field completeness profiles. This is why the project stores run-specific logs, stability summaries, and structured artifacts. The dataset is therefore dynamic by construction and must be documented with reproducibility controls.

Overall, the dataset characteristics align closely with the research goals of the thesis. The corpus is suitable for studying how ESG evidence can be extracted from long-form disclosure documents, how tone differs from generic sentiment, how climate-specific model outputs align or diverge from an ESG tone taxonomy, and how reproducibility can be preserved in a multi-stage extraction environment.

### 3.2.2. Rationale

The rationale for the selected data sources and corpus design follows directly from the research problem. ESG disclosure analysis for Indonesian reporting contexts requires data that are realistic, naturally occurring, bilingual, and rich enough to support record-level interpretation. Pre-built sentiment datasets or generic ESG score tables would not satisfy that need because they typically abstract away the original wording, the document structure, and the distinction between narrative commitment and demonstrated outcome.

The decision to use sustainability and annual report PDFs as primary sources is therefore methodological rather than merely practical. These reports are the public artifacts through which companies communicate ESG commitments, actions, and outcomes to investors, regulators, and stakeholders. They contain the narrative patterns that the thesis is designed to analyze. If the study used only tabular ESG scores or manually curated excerpts, it would not be able to test the pipeline’s ability to move from raw disclosure documents to structured, auditable evidence.

The decision to use OCR-derived page markdown as the operational corpus is also well justified. Sustainability reports are usually distributed as PDFs, not as clean machine-readable corpora. OCR and page extraction bridge that gap by turning a static document into processable text units. The page-aware representation is particularly important because:

- it preserves provenance,
- it supports page-level error checking,
- it reduces context-window pressure for downstream LLM runs,
- and it makes it possible to revisit problematic records in their original local context.

Without page-level preprocessing, the study would risk treating the PDF as an opaque blob, which would make both debugging and methodological reporting much weaker.

The decision to generate structured ESG records rather than only summary labels follows from the ABSA orientation of the study. Aspect-based sentiment analysis is fundamentally concerned with fine-grained text units and their associated targets or aspects. In this thesis, that logic is extended to an ESG-specific schema that includes tone and provenance. This enables the study to ask questions such as whether a specific statement is a commitment, an action, or an outcome, and whether that statement aligns with a climate-relevance label or an ontology path. A coarser dataset would not support these questions.

The use of silver labels and human-editable annotation artifacts is justified by the current absence of a full expert-labeled benchmark. Rather than ignoring this limitation, the methodology incorporates it into the research design. The staged labeling strategy allows the project to proceed with exploratory evaluation while also making the limitations explicit. Silver labels serve as a provisional scaffold for auditing, prioritization, and workbench design, not as a substitute for full gold-standard validation. This is a pragmatic and transparent choice for a research pipeline that is still undergoing benchmark construction.

The inclusion of ClimateBERT and other comparison artifacts is justified because the thesis is not only extracting ESG records but also evaluating the meaning and reliability of those records. ClimateBERT outputs provide an external climate-focused comparison signal. Even when the labels are not conceptually identical to the ESG tone taxonomy, agreement and disagreement patterns can still reveal whether the extracted records capture semantically plausible disclosure signals. This strengthens the interpretive dimension of the methodology.

The inclusion of ontology maps and semantic exports is justified by the explainability goals of the thesis. ESG analysis becomes more valuable when extracted statements can be positioned within structured conceptual frameworks such as ESG pillars, aspects, and regulatory anchors. A purely flat record table is useful, but it does not fully support interpretability, graph export, or future knowledge-system integration. Ontology-aware artifacts therefore extend the usefulness of the dataset beyond classification alone.

Finally, the inclusion of workflow documentation, run logs, and stability summaries is justified by the reproducibility objective. Because the dataset is dynamically generated through multiple computational steps, methodological rigor requires more than code availability. It requires traceable artifacts, run settings, output summaries, and page-level documentation that make the research process inspectable after the fact. This is especially important in LLM-mediated workflows, where outputs may vary by model, prompt, or parser behavior.

In summary, the dataset design is justified by six intertwined needs:

1. realism, because the source material must reflect actual corporate ESG reporting;
2. granularity, because record-level ABSA requires statement-level evidence;
3. provenance, because every extracted record should remain traceable to source context;
4. bilingual flexibility, because the target reporting environment is Indonesian-English;
5. validation support, because the benchmark is still under construction;
6. reproducibility, because the methodology itself is a research contribution.

For these reasons, the selected data sources are not incidental. They are the minimum viable structure needed to make the thesis both empirically grounded and methodologically auditable.

### 3.2.3. Data Accessibility and Ethical Considerations

The data accessibility profile of this study is shaped by the nature of the source documents and by the repository’s reproducibility goals. The primary source reports are corporate disclosure documents that are generally intended for public or semi-public stakeholder communication. This makes them appropriate for document analysis research, provided that storage, redistribution, and quotation practices remain proportionate and respect any licensing or access constraints associated with the original publishers.

From a practical perspective, the study does not rely on a single externally hosted benchmark that can simply be downloaded and redistributed as-is. Instead, the accessible research package is composed of locally generated artifacts, including OCR outputs, extracted records, review tables, and documentation. This creates an important distinction between:

- source-document accessibility,
- and derivative-artifact accessibility.

Source documents may be publicly available from company or regulatory websites, but the precise redistribution rights may vary. Derivative artifacts generated by the research pipeline, on the other hand, are generally easier to share internally because they are produced by the research system itself. The methodology should therefore recommend sharing derivative datasets, schemas, run logs, and summaries wherever permissible, while documenting the retrieval process for source PDFs rather than assuming unrestricted republication of every original report.

Ethically, the project deals with organizational disclosure text rather than private personal data. This substantially lowers privacy risk relative to many NLP settings. However, low personal-data risk does not eliminate all ethical concerns. Several issues still matter.

First, extraction error can create interpretive distortion. If OCR fails, if the parser fragments a sentence incorrectly, or if a model assigns an inaccurate aspect or tone label, the resulting structured record may misrepresent the meaning of the original disclosure. Because the thesis concerns potentially sensitive themes such as sustainability performance and greenwashing risk, methodological transparency about such errors is ethically necessary. This is one reason the pipeline includes audit pages, parse-error tracking, and review queues.

Second, model outputs may inherit biases from training data or prompt design. A bilingual ESG pipeline may perform differently across Indonesian and English statements, across environmental and governance disclosures, or across documents with different formatting quality. The methodology should therefore avoid overclaiming universality and should treat performance variation as a substantive research concern. Ethical handling in this context means exposing model instability and label ambiguity rather than concealing them behind single summary scores.

Third, the absence of a fully expert-labeled ground truth places ethical pressure on interpretation. When a dataset is only partially annotated or relies on silver-label scaffolding, the researcher must distinguish exploratory findings from definitive evaluative claims. This chapter therefore positions the current dataset as a benchmark-construction and exploratory-validation corpus, not as a final authoritative dataset for ranking firms or making regulatory determinations.

Fourth, provenance preservation is an ethical requirement as well as a technical one. If a structured ESG record cannot be traced back to document, page, or context, then it becomes difficult to challenge or verify the interpretation. The page-aware preprocessing design directly addresses this issue by preserving links between source documents and downstream records.

Fifth, documentation accessibility matters for reproducibility ethics. A thesis that depends on opaque transformations would be difficult for other researchers to audit or replicate. By storing workflow documents, Mermaid diagrams, artifact descriptions, and page-level dashboards, the repository improves methodological transparency. This does not make the system perfect, but it reduces the gap between reported findings and executable evidence.

Based on these considerations, the study’s ethical stance can be summarized as follows:

- use publicly communicative corporate materials as the empirical base,
- preserve source provenance wherever possible,
- treat OCR and extraction error as reportable methodological risk,
- distinguish exploratory proxy validation from full gold-standard evaluation,
- avoid overstating model certainty in multilingual, semi-structured settings,
- and prioritize the sharing of derivative research artifacts and documentation when direct source redistribution is constrained.

This approach is appropriate for a thesis that aims to balance innovation with auditability. It recognizes that ESG disclosure analysis can influence interpretive judgments about company communication, and therefore requires careful handling of uncertainty, traceability, and transparency.

## 3.3. Preprocessing Pipeline

The preprocessing pipeline is the operational bridge between raw sustainability reports and the structured ESG records analyzed in later chapters. In this thesis, preprocessing is not a narrow text-cleaning step. It is a multi-stage transformation process that establishes provenance, reduces document noise, prepares text for extraction, and creates the intermediate artifacts required for validation and reproducibility.

The pipeline begins with source-document acquisition and inventory preparation. Reports are collected as PDFs and associated with document-level metadata such as company, report year, report type, language context, and file path. Even when the metadata layer is still evolving, the methodological expectation is that each document should be assigned a stable `document_id` so that OCR output, extracted records, annotation rows, and evaluation summaries can all be linked back to the same source.

The next stage is OCR and document decomposition. The repository’s workflow documentation identifies `Bulk_OCR.py` as the main entry point for PDF processing. This stage converts each report into:

- OCR output JSON,
- page-level markdown,
- and, where relevant, image or layout-derived artifacts.

The methodological value of this step lies in converting a visually formatted PDF into computational units that can be processed by later models without discarding provenance. Each page becomes a local evidence container rather than forcing the entire document into one long unstructured string.

After OCR, the pipeline moves into page-aware text preparation. This includes organizing markdown pages, associating them with document and page identifiers, and preparing them for batch processing. The methodology notes in the repository explicitly emphasize page-aware processing because sustainability reports often exceed model context windows and contain noisy formatting. Splitting the corpus into page-level or batch-level text units helps:

- control model input size,
- improve traceability,
- isolate OCR issues,
- and support finer-grained debugging.

The next preprocessing concern is text normalization and noise control. OCR outputs from corporate reports may contain:

- repeated headers and footers,
- page numbers,
- table fragments,
- line breaks inside sentences,
- bullet artifacts,
- and inconsistent spacing or punctuation.

Preprocessing must therefore reduce superficial formatting noise while preserving semantically important cues. The goal is not aggressive cleaning that erases context, but controlled normalization that makes downstream extraction more stable. In this study, that means retaining the evidential wording of disclosure statements while minimizing layout artifacts that could distort model parsing.

Language handling is another core preprocessing function. Because the corpus is bilingual or mixed-language, the pipeline must treat language not as an afterthought but as a structural attribute. At minimum, preprocessing should preserve language tags or language-aware metadata per document, page, or extracted record. This helps in three ways:

- it supports prompt selection for Indonesian or English inputs,
- it helps interpret model errors that may cluster by language,
- and it assists future ontology and lexicon expansion for bilingual ESG terminology.

The preprocessing pipeline also includes batching and contextual segmentation for LLM extraction. The relevant project notes describe page batching as a methodological choice rather than an implementation convenience. Some ESG statements require enough surrounding context to interpret scope, target, or result framing, but overly large contexts can reduce extraction precision or exceed provider limits. The pipeline therefore benefits from batching strategies that preserve local context while keeping input units manageable. These batches, together with prompt identifiers and model settings, become part of the run-level provenance stored in background-job and extraction artifacts.

Once the OCR text is prepared, the pipeline transitions into structured extraction preparation. Here the key objective is schema readiness. The extraction stage expects text segments that can plausibly yield fields such as:

- `text`,
- `aspect`,
- `esg_pillar`,
- `sentiment`,
- `tone`,
- `reasoning`,
- `target_doc`,
- `prompt`,
- and `model`.

Preprocessing supports this by ensuring that the source text units are coherent enough to be interpreted as ESG statements and by preserving the metadata necessary for reconstructing their origin. If a later stage encounters a malformed record, the preprocessing layer should make it possible to determine whether the issue originated in OCR quality, segmentation quality, prompt behavior, or parser normalization.

An important methodological feature of this pipeline is that preprocessing outputs are themselves auditable artifacts. The study does not treat preprocessing as invisible code. Instead, it exposes preprocessing evidence through pages such as:

- `pages/1_2_OCR_Quality_Workbench.py`,
- `pages/2_4_PDF_Page_Processing_Audit.py`,
- and the workflow documentation pages in `documentation/streamlit_pages/`.

This allows the researcher to inspect page completeness, OCR outputs, source paths, and failure patterns. Such visibility is important because preprocessing quality directly affects every subsequent result.

The preprocessing pipeline can be described step by step as follows:

1. Collect and register source PDF reports.
2. Assign document-level identifiers and metadata.
3. Run OCR to create machine-readable text and document decomposition artifacts.
4. Split outputs into page-level markdown or batch-ready text units.
5. Normalize layout noise while retaining disclosure meaning.
6. Preserve provenance metadata such as document ID, page ID, language, and source path.
7. Prepare page or batch text for LLM extraction and downstream parsing.
8. Store preprocessing outputs as reusable artifacts for auditing and reruns.

From a thesis perspective, this pipeline serves several methodological goals simultaneously. It supports reproducibility because each preprocessing stage leaves traceable files. It supports validity because the researcher can inspect whether extraction failures originate in poor OCR or poor modeling. It supports bilingual handling because language information can be preserved from source to record. It supports interpretability because extracted records can be traced to page-level evidence. And it supports future extension because the same preprocessed artifacts can later feed additional modules such as semantic graph export, social-network analysis, or more formal benchmark construction.

The preprocessing pipeline also defines the limits of downstream claims. If OCR quality is uneven, if page segmentation is unstable, or if certain report sections systematically generate noisy records, then those problems are not merely technical inconveniences. They affect what can reasonably be claimed about tone distribution, ontology coverage, model agreement, and greenwashing indicators. This is why preprocessing in this thesis is treated as part of the methodology chapter rather than a minor implementation detail.

In summary, the preprocessing pipeline is a foundational research component. It transforms raw PDF disclosures into structured, page-aware, extraction-ready evidence units while preserving enough metadata and artifact history to make the overall ESG ABSA workflow inspectable and reproducible. The rest of the thesis depends on the quality of this transformation, which is why the preprocessing design must be documented in full methodological detail.

## 3.4. Model Design

The model design of this thesis follows a layered and comparative strategy rather than a single-model strategy. This is a deliberate methodological choice. ESG disclosure analysis in bilingual corporate reports is affected by several simultaneous challenges: terminology variation across industries, differences between narrative commitment and measurable outcome language, inconsistencies introduced by OCR and PDF layout, and limited availability of high-quality labeled training data. No single modeling approach is likely to handle all of these issues equally well. For that reason, the thesis organizes model behavior into multiple complementary components that together form an interpretable analytical stack.

The repository’s methodology notes describe this stack as combining transparent heuristic layers, statistical baselines, external domain-specific comparison models, and LLM-based structured extraction. In practice, the current system operationalizes four modeling components that matter for Chapter 3:

1. a rule-based ESG lexicon and schema-control layer;
2. a classical machine-learning baseline built around TF-IDF and logistic regression logic;
3. a ClimateBERT comparison layer as an external climate-domain validator;
4. an LLM extraction layer that produces structured ESG records from page-aware OCR text.

These components are not identical in purpose. Some are designed for direct prediction, some for comparison, and some for error detection or interpretability. Their value lies in the fact that they expose different kinds of strengths and weaknesses. The methodology therefore treats the modeling architecture as a triangulation framework rather than a winner-take-all competition.

### 3.4.1. Rule-Based ESG Lexicon and Schema Layer

The first modeling component is a rule-oriented layer that captures explicit lexical cues, normalization patterns, and schema expectations. This layer is methodologically important even when its predictive sophistication is limited. Rule-based logic is transparent, inspectable, and easy to align with domain knowledge. In ESG reporting, some features are especially suited to such a layer:

- explicit aspect terms such as emissions, waste, safety, labor, board, audit, or compliance;
- bilingual equivalents and aliases across Indonesian and English usage;
- tone markers such as future-oriented commitment verbs, implementation verbs, and result-reporting expressions;
- and simple structural checks on whether required fields are present in extracted outputs.

This rule-based layer supports two tasks. First, it provides a low-cost interpretive anchor for classifying obvious cases or for proposing initial labels. Second, it acts as a control and repair mechanism around downstream structured outputs. For example, if an LLM returns a malformed field, a rule-based normalizer may still recover common label variants or detect schema drift. This is especially useful when different prompts or providers use slightly different textual conventions for the same conceptual field.

Methodologically, the rule layer is not presented as sufficient on its own. Its weaknesses are clear: it is brittle under paraphrase, weak for implicit meaning, and sensitive to vocabulary drift across sectors and languages. However, it remains valuable for explainability, ontology alignment, and error categorization. In a thesis context, this is important because a purely black-box approach would make it harder to justify how certain labels were stabilized or normalized after extraction.

### 3.4.2. Classical Machine-Learning Baseline

The second modeling component is a classical machine-learning baseline centered on TF-IDF-style sparse text representation combined with logistic-regression-style classification. The methodology notes in the repository explicitly reference this baseline as part of the model-design chapter because it provides a conventional benchmark against which more complex methods can be interpreted.

The rationale for including a classical baseline is threefold.

First, it provides a transparent statistical reference point. If a simpler linear model with weighted lexical features performs competitively on some subtask, then the thesis can avoid overstating the necessity of more expensive or less stable LLM-based extraction for every analytical goal.

Second, TF-IDF and logistic regression expose interpretable coefficients. This is especially useful for Chapter 4 and Chapter 5 because the weights can reveal which lexical items are most associated with commitment, action, outcome, or other ESG categories. In other words, the classical baseline helps convert raw predictive behavior into interpretable evidence about disclosure language.

Third, the baseline is methodologically valuable under limited labeled data conditions. Even when the human-labeled benchmark remains incomplete, classical models can still be useful on pilot annotations, silver-label subsets, or comparison samples. Their simplicity makes them practical for sanity checks and controlled experiments.

In the thesis design, the classical model is not expected to solve the full structured extraction problem. Rather, it serves as a reference classifier for subcomponents such as tone or aspect categorization once labeled examples are available. The limitation is that such models require cleaner feature-target alignment than the raw OCR-to-JSON task provides. They are therefore better suited to downstream benchmarking and explainability than to end-to-end extraction from raw page text.

### 3.4.3. ClimateBERT as External Domain Validator

The third modeling component is ClimateBERT, used here not as a direct replacement for ESG tone classification but as an external climate-domain comparison layer. This distinction is crucial. The repository documentation repeatedly cautions that ClimateBERT labels and the thesis tone taxonomy are not conceptually identical. The role of ClimateBERT in this methodology is therefore comparative and construct-oriented rather than definitive.

The justification for ClimateBERT is straightforward. ClimateBERT is domain-adapted to climate-related text and can therefore provide an independent signal about whether extracted statements align with climate-related disclosure patterns such as commitment framing or climate relevance. This is especially useful when the thesis needs more than internal self-consistency. Agreement with an external domain-tuned model can strengthen the argument that the extracted records are capturing meaningful disclosure semantics rather than random parser artifacts.

The current repository includes dedicated infrastructure for this comparison, especially through `pages/1_4_ClimateBERT_Record_Batch.py` and `pages/0_9_Tone_ClimateBERT_Visualization.py`. The documented workflow indicates that the current project already supports:

- proxy comparison between ESG tone outputs and ClimateBERT-style commitment signals,
- record-preserving batch export for one-to-one external ClimateBERT evaluation,
- confusion-style comparisons,
- percent agreement,
- and Cohen’s kappa.

However, the methodology must also state the present limitation clearly: the proxy comparison is useful for early validation, but it is not the same as a full ClimateBERT run over every extracted record. The documentation notes that only a very small remote validation sample currently exists and that a real thesis-grade result requires record-level ClimateBERT output for the complete dataset. Therefore, ClimateBERT in this chapter should be framed as an external semantic validator whose current implementation is partial but methodologically well defined.

### 3.4.4. LLM-Based Structured ESG Extraction

The fourth and most central modeling component is the LLM extraction layer. This layer is responsible for transforming page-aware OCR text into structured ESG records containing fields such as text, aspect, ESG pillar, sentiment, tone, reasoning, prompt ID, and source metadata. In the current repository, this is implemented primarily through `pages/llm_processing.py` and related background-job and audit pages.

The LLM layer is necessary because the source texts are long, heterogeneous, bilingual, and often rhetorically complex. A rule-only or sentence-classification-only design would not adequately capture multi-field structured outputs from semi-structured disclosure text. The LLM approach instead treats the task as constrained information extraction: given a page or batch of OCR text, the model is prompted to produce a structured representation of ESG-relevant records.

This modeling choice allows the thesis to operationalize ABSA as a richer record schema instead of a single sentiment score. It also supports prompt engineering across multiple templates. The methodology notes in `documentation/general.md` define the extraction design as using seven prompt templates across at least two model families, including zero-shot, few-shot, and chain-of-thought variants in Indonesian and English. That design is important because prompt structure can affect:

- JSON parse success,
- field completion rate,
- number of extracted records,
- missing tone frequency,
- and schema drift.

The LLM layer therefore has two simultaneous roles:

- extraction of substantive ESG evidence;
- and empirical study of prompt and model stability.

This is why the repository stores run-level objects in `results/esg_records.json`, tracks background-job events, and exposes parse-audit views. The modeling methodology is not satisfied with only the records that parse successfully. It also accounts for empty runs, malformed JSON, failed outputs, and partially recoverable raw generations. This is a major methodological strength because it turns failure into analyzable evidence rather than silently dropping it.

### 3.4.5. Prompt Strategy and Comparative Model Logic

A key part of the model design is that multiple prompt templates are not treated as minor implementation variants. They are an experimental factor. The thesis notes describe seven prompt templates and emphasize the need to compare zero-shot, few-shot, and chain-of-thought strategies in both Indonesian and English settings. This comparative structure reflects the methodological assumption that structured ESG extraction quality is sensitive not only to the underlying model but also to the prompt formulation.

Different prompts operationalize different tradeoffs:

- zero-shot prompts maximize simplicity and minimize setup overhead, but may be weaker in schema compliance;
- few-shot prompts improve structure by demonstrating the expected output pattern, but may bias the model or consume context budget;
- chain-of-thought prompts may improve reasoning or field consistency, but can also create unstable or overly verbose outputs that complicate parsing.

The thesis therefore treats prompt design as part of the model-design problem rather than a pre-model convenience. This is consistent with the repository’s revision-analysis tooling, which already includes prompt-level stability artifacts and summary tables. The model design is thus comparative in two directions: across model families and across prompt families.

### 3.4.6. Overall Design Logic

Taken together, the model architecture can be summarized as a hybrid evidence-extraction design:

- rules provide transparency and schema support;
- classical ML provides a benchmark and interpretable feature weights;
- ClimateBERT provides external climate-domain comparison;
- and LLM prompting provides the flexible structured extraction needed for long-form ESG disclosures.

This architecture is appropriate for the thesis because it avoids both extremes: it is neither a purely hand-engineered system nor an unconstrained generative black box. Instead, it is a controlled hybrid framework in which each modeling layer serves a defined methodological purpose. That design supports not only extraction accuracy but also interpretability, auditability, and future benchmark extension.

## 3.5. Metrics Definition

The metrics framework of this thesis is designed to evaluate not just one predictive task but the integrity of the entire ESG ABSA pipeline. Because the study involves OCR, structured extraction, field normalization, climate-model comparison, and partial human validation, a single metric such as accuracy would be insufficient. The methodological goal is therefore to define a layered measurement system that aligns with the pipeline stages and the maturity of the available benchmark.

The repository notes already specify five major metric families for Chapter 3:

1. OCR quality metrics;
2. extraction and parsing metrics;
3. ABSA evaluation metrics;
4. ontology and alignment metrics;
5. stability and comparative metrics.

Each metric family answers a different methodological question. Together they determine whether the pipeline is producing usable evidence, whether the structured outputs are complete and consistent, and whether the resulting labels are defensible enough for thesis interpretation.

### 3.5.1. OCR Quality Metrics

OCR quality is the first measurable stage because all downstream extraction depends on the fidelity of the text produced from PDFs. If OCR introduces substantial distortion, then even a strong extraction model may fail for reasons unrelated to ESG semantics. For this reason, OCR quality is treated as a methodological risk variable rather than a hidden preprocessing detail.

The repository documentation identifies candidate OCR metrics such as:

- character error rate (CER),
- word error rate (WER),
- table extraction quality,
- and page completeness.

CER measures the proportion of character-level edits required to transform OCR output into a corrected reference snippet. WER performs the same logic at the token level. These metrics are appropriate for sampled manual evaluation when a fully corrected corpus is unavailable. They allow the researcher to quantify whether OCR reliability differs across layout types such as narrative paragraphs, tables, bilingual columns, or infographic-heavy pages.

Page completeness is also important in this thesis because a page can be technically parsed while still missing meaningful segments. A page-level audit therefore complements CER and WER by documenting whether expected content zones were captured. In methodological terms, OCR metrics are not only quality-control statistics. They are explanatory variables for later extraction failure, missing tone, or schema drift.

### 3.5.2. Extraction and Parsing Metrics

The second metric family evaluates the success of the LLM extraction layer as a structured generation system. This is especially important because the pipeline is designed to produce machine-readable JSON-like ESG records rather than only free-form text summaries.

The repository’s audit tooling and revision-analysis notes explicitly identify the following metrics as relevant:

- JSON parse success rate,
- record count per run,
- field completion rate,
- missing tone rate,
- schema drift rate,
- empty-output rate,
- and unresolved failure count.

JSON parse success rate measures the proportion of model runs that produce outputs parsable into structured records. This is one of the most important extraction metrics because an output that looks plausible to a human but cannot be parsed programmatically is methodologically fragile. Record count per run indicates how productive each run is, but it must be interpreted carefully because a higher record count is not automatically better if it comes with low precision or high schema drift.

Field completion rate measures whether required schema fields such as tone, aspect, ESG pillar, or reasoning are consistently populated. Missing tone rate is especially important in this thesis because the tone taxonomy is central to the research questions and greenwashing-sensitive interpretation. Schema drift rate captures cases where the model appears to understand the task semantically but produces structurally inconsistent outputs, for example by placing tone values in sentiment fields or changing expected keys.

The page `2_1_LLM_Error_Parse_Audit.py` also formalizes run-level status definitions and error categories, which can be aggregated into extraction metrics. This makes it possible to distinguish between:

- successful parsed runs,
- successful-but-empty runs,
- failed runs with recoverable raw output,
- and failed runs without usable output.

Methodologically, this is valuable because it prevents extraction performance from being overstated through selective visibility of successful records only.

### 3.5.3. ABSA Evaluation Metrics

The third metric family evaluates the quality of the structured labels once human annotations or reliable comparison labels are available. The repository’s `1_3_Ground_Truth_Metrics.md` documentation defines the core metrics for tone, ESG pillar, and aspect evaluation:

- accuracy,
- weighted precision,
- weighted recall,
- weighted F1,
- Cohen’s kappa,
- confusion matrices,
- and disagreement tables.

Accuracy is useful as a top-line measure of exact match, but on its own it can be misleading under class imbalance. Weighted precision and weighted recall provide more nuanced information about how well the system identifies classes with uneven frequency. Weighted F1 is particularly appropriate because the tone and ESG distributions in this project are not balanced; it summarizes the precision-recall tradeoff while accounting for class support.

Cohen’s kappa is especially important for the thesis because it adjusts for chance agreement. In a setting where some categories may dominate, kappa is more defensible than raw agreement alone. Confusion matrices and disagreement tables then operationalize the errors by showing which categories are being confused, such as whether outcome statements are over-assigned as action or whether governance-related records systematically produce missing tones.

These metrics apply separately to:

- tone prediction versus `ground_truth_tone`,
- ESG pillar prediction versus `ground_truth_esg`,
- and aspect prediction versus `ground_truth_aspect`.

This separation matters because a pipeline can perform differently across these label types. A system may recognize broad ESG pillars reasonably well while still struggling with fine-grained aspect distinctions or tone nuance.

### 3.5.4. ClimateBERT Comparison Metrics

Because ClimateBERT is used as an external comparison layer rather than as gold-standard truth, its metrics require careful interpretation. The repository documentation for the ClimateBERT batch workflow identifies:

- percent agreement,
- Cohen’s kappa,
- confusion heatmaps,
- and raw proxy or merged comparison records.

These metrics are appropriate for construct comparison. They can indicate whether ESG tone labels align in a meaningful way with climate-specific commitment or topical relevance outputs. However, they must not be misreported as direct accuracy metrics against ground truth unless a validated one-to-one benchmark is available. In this chapter, ClimateBERT metrics therefore function as external consistency indicators rather than final performance scores.

### 3.5.5. Ontology and Coverage Metrics

The fourth metric family evaluates how well extracted records align with the project’s ontology and ESG concept structure. The repository notes describe ontology coverage as an important proof layer for explainability claims. Relevant metrics include:

- ontology coverage rate,
- mapped versus unmapped aspect count,
- cluster frequency,
- depth or specificity of ontology path assignment,
- and list size of novel or unresolved aspects.

These metrics matter because a flat aspect label is less analytically useful than one that can be situated within an interpretable conceptual hierarchy. High ontology coverage supports the claim that the system is not only extracting records but also organizing them in a machine-readable ESG framework. Conversely, unmapped or weakly mapped aspects identify where the ontology remains incomplete, especially for Indonesian-specific terminology or organization-specific phrasing.

### 3.5.6. Stability and Comparative Metrics

The fifth metric family measures robustness across models, prompts, and runs. This is necessary because the thesis explicitly studies prompt sensitivity and structured-output stability. The revision-analysis notes identify metrics such as:

- parse success rate by prompt,
- missing tone rate by prompt,
- schema drift rate by prompt,
- field completion rate by prompt,
- run count by model,
- and cross-model stability summaries.

These metrics are methodologically important because a system that performs well only under one fragile prompt configuration is less defensible than one that remains reasonably stable across prompting strategies. Stability metrics therefore support the thesis objective of identifying robust extraction practices rather than merely reporting the best-looking output.

### 3.5.7. Greenwashing-Oriented and Interpretive Metrics

The thesis also proposes interpretive metrics that connect disclosure tone to substantive research meaning. The most important of these is the greenwashing-oriented rhetoric-to-results indicator, operationalized in the repository as a company-level commitment-to-outcome imbalance measure. While not yet a formally validated benchmark metric, it is methodologically useful as a heuristic indicator derived from the tone taxonomy.

This metric typically takes the form of:

- commitment share,
- outcome share,
- commitment-to-outcome ratio,
- and company-level risk tier or imbalance interpretation.

Because it is heuristic, the chapter should present it carefully. Its value lies in framing one possible downstream use of tone-aware ESG extraction rather than claiming that it is already a validated regulatory measure.

### 3.5.8. Overall Measurement Philosophy

The metrics framework of this thesis is intentionally plural. Different stages require different kinds of evidence, and the current benchmark maturity does not justify collapsing them into one overall score. Instead:

- OCR metrics evaluate text fidelity;
- extraction metrics evaluate structured-output reliability;
- ABSA metrics evaluate label quality against human annotation where available;
- ClimateBERT metrics evaluate external construct alignment;
- ontology metrics evaluate explainability and coverage;
- and stability metrics evaluate robustness across prompts and models.

This measurement design is appropriate because the thesis contribution is an end-to-end methodology. The system should therefore be judged not only by whether it can assign a label, but by whether it can generate traceable, consistent, and interpretable ESG evidence from complex disclosure documents.

## 3.6. Benchmark and Ground Truth Design

The benchmark and ground-truth design in this thesis is staged, resumable, and explicitly transitional. It does not begin from a pre-existing gold-standard dataset. Instead, it begins from a document-processing and record-extraction pipeline that generates candidate ESG evidence units, then incrementally converts those units into evaluation-ready benchmark artifacts through annotation, comparison, and audit workflows. This design reflects the reality of the research problem: there is no widely established, bilingual Indonesian ESG ABSA benchmark with record-level tone, aspect, and provenance fields that fits the thesis requirements out of the box.

For that reason, the benchmark design is inseparable from the system design. The benchmark is not a static input to the research; it is one of the outputs of the research infrastructure.

### 3.6.1. Benchmark Unit and Data Format

The benchmark unit in this study is the record-level ESG disclosure statement. Each benchmarkable unit ideally contains:

- the extracted text span,
- document and page provenance,
- predicted ESG pillar,
- predicted aspect,
- predicted tone,
- optional sentiment and reasoning fields,
- model and prompt provenance,
- and human-editable ground-truth columns.

This structure is consistent with the repository’s broader data-model notes and with the current annotation workflows. It ensures that evaluation happens at the same level of granularity as the research questions. A benchmark row should represent a concrete disclosure claim, not an entire document summary.

The repository documentation also emphasizes JSONL-style and row-based experiment formats for resumable runs. This is methodologically useful because each run can be logged as a distinct event or output object rather than being merged invisibly into one opaque result file. In practice, the benchmark ecosystem already includes:

- run-level objects in `results/esg_records.json`,
- T1 and T2 output files such as `results/t1_results.jsonl` and `results/t2_results.jsonl`,
- silver-label tables,
- pilot annotation CSVs,
- and comparison exports.

This design supports restartability, auditability, and partial completion. If one stage fails or one subset is still unlabeled, the rest of the benchmark artifacts remain inspectable and reusable.

### 3.6.2. Silver Labels and Weak Supervision

Given the absence of a complete expert-labeled corpus, the methodology uses silver labels and proxy comparison files as an intermediate validation scaffold. This is a pragmatic but carefully bounded choice. Silver labels are useful for:

- generating annotation seeds,
- prioritizing review queues,
- estimating likely agreement patterns,
- building workbench interfaces,
- and identifying error-prone regions before full manual annotation is complete.

The repository specifically highlights `results/revision_analysis/silver_tone_ground_truth.csv` as a central artifact in this process. Methodologically, this file should not be treated as the final truth source. It is a scaffold that enables the system to function as a benchmark-construction environment while human labeling is still incomplete.

The advantage of this approach is that it accelerates development and allows early quantitative inspection. The disadvantage is that weak labels can propagate systematic biases from the extraction layer into the validation layer. This is why the chapter must distinguish between:

- exploratory proxy evaluation,
- pilot human-labeled evaluation,
- and future full benchmark evaluation.

### 3.6.3. Human Annotation Workflow

The ground-truth design includes a dedicated human annotation workflow through pages such as `ground_truth.py`, `1_1_Ground_Truth_Workbench.py`, and related metric and visualizer pages. The intended annotation logic is to present extracted records together with source context and editable ground-truth fields. At minimum, human annotation should cover:

- `ground_truth_tone`,
- `ground_truth_esg`,
- `ground_truth_aspect`,
- review notes,
- reviewer identity where applicable,
- and status markers such as whether the record requires further human review.

This design is appropriate because the thesis’s most important labels are nuanced and context dependent. For example, distinguishing commitment from action or action from outcome often requires close reading of the statement rather than keyword spotting alone. Human annotation therefore remains necessary even in a highly automated pipeline.

The repository’s metrics page documentation also makes it clear that the annotation workflow is deliberately separated from automatic output generation. If no human labels are filled, the formal evaluation metrics should not be computed as if the benchmark already exists. That separation is a methodological strength because it prevents accidental conflation of model output with validated truth.

### 3.6.4. Coverage, Stratification, and Resumability

The benchmark is not only about labels; it is also about coverage. A useful evaluation corpus should cover meaningful variation across:

- company or source document,
- language,
- prompt family,
- model family,
- ESG pillar,
- tone category,
- and aspect category.

This is why the repository includes coverage-oriented pages such as `1_10_Ground_Truth_Run_Coverage.py` and record-audit tools. The benchmark design should be understood as resumable and stratifiable. Annotation does not need to begin with a fully complete corpus, but it should progressively move toward a stratified sample that covers the major sources of variation in the extracted records.

Resumability is particularly important because the benchmark is assembled from a dynamic pipeline. New extraction runs, prompt variants, or revised normalization logic may create new candidate rows. A resumable design ensures that human annotation effort is not wasted and that benchmark growth can proceed incrementally.

### 3.6.5. Current Ground-Truth Limitations

The methodology chapter must acknowledge the current limitations clearly because they define the inferential scope of the thesis. The repository notes already identify several concrete issues that should be carried into the benchmark discussion.

First, the human-labeled benchmark is incomplete. This means that many current evaluations are proxy or pilot evaluations rather than final performance claims.

Second, the ClimateBERT comparison is still partial. The project documentation explicitly notes that only a very small remote validation subset currently exists and that a full thesis-grade evaluation requires ClimateBERT output for all extracted records.

Third, the extraction layer exhibits schema instability. The revision notes highlight missing tone records, parse errors, empty outputs, and field drift as active methodological concerns. These issues do not invalidate the benchmark effort, but they do mean that benchmark construction must account for dropped rows, partially filled records, and uncertain label provenance.

Fourth, OCR quality has not yet been fully quantified across representative page samples. Because OCR error can cascade into extraction error, the present benchmark should be treated as conditional on the current preprocessing quality.

The planning notes in `documentation/general.md` also identify specific benchmark weaknesses that deserve explicit mention in a full thesis narrative, including:

- missing tone rows,
- limited ClimateBERT comparison coverage,
- and schema drift in sentiment or related fields.

These limitations should not be hidden. They are part of the methodological contribution because the system is designed to surface them and organize future corrective work.

### 3.6.6. Why This Design Is Still Defensible

Although the benchmark is incomplete, the design is still methodologically defensible for a thesis focused on executable pipeline construction and auditability. The defense rests on five points.

First, the benchmark design is transparent about its current maturity level. It does not present silver labels or proxy agreement as a finished gold standard.

Second, the design is operational. The repository already contains the workbench, metrics pages, audit pages, and file structures needed to expand the benchmark systematically.

Third, the benchmark units are well specified. Record-level rows with provenance and editable ground-truth fields provide a strong basis for future formal evaluation.

Fourth, the benchmark is tied directly to the research questions. Tone, ESG pillar, aspect, prompt stability, and ClimateBERT comparison are not arbitrary labels; they correspond to the thesis’s analytical claims.

Fifth, the benchmark design is extensible. Additional human labels, OCR reference snippets, ontology refinements, and full ClimateBERT runs can all be incorporated without redesigning the whole system.

### 3.6.7. Final Position of the Benchmark in the Methodology

The benchmark and ground-truth design should therefore be described as a staged validity framework. It begins with extracted record generation, passes through silver-label and proxy-comparison scaffolds, incorporates human annotation and disagreement review, and ultimately aims toward a stronger gold-standard corpus with wider coverage and higher reliability.

This is appropriate for the present thesis because the central contribution is not merely a final score against a fixed benchmark. The contribution is the construction of a reproducible ESG ABSA environment in which benchmark creation, error analysis, model comparison, and documentation are integrated into one executable system. Under that framing, the current benchmark is both a research instrument and a research outcome.
