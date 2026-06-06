# Chapter 3: Methodology

## 3.1 Overview of the Methodology

This study adopts an executable, mixed-method methodology for ESG aspect-based sentiment analysis (ABSA) in Indonesian sustainability reporting. The core premise is that ESG disclosure analysis is not only a classification problem. It is also a document-engineering problem, a provenance problem, and a validation problem. Sustainability reports are distributed as heterogeneous PDFs, often bilingual, structurally inconsistent, and rhetorically uneven. A defensible methodology must therefore explain how raw reports are transformed into analyzable records, how those records are validated, and how uncertainty is documented.

The research design is exploratory rather than purely confirmatory. The current workspace already contains a functioning OCR-to-record pipeline, prompt-driven extraction runs, ClimateBERT comparison outputs, ontology mappings, dashboards, and review artifacts. However, it does not yet contain a full expert-labeled benchmark suitable for definitive supervised claims. For that reason, the methodology treats model outputs, proxy labels, diagnostic artifacts, and human review interfaces as triangulated evidence. This is appropriate for a thesis whose contribution is the design of an auditable research system as much as the reporting of a final model score.

The methodological unit of analysis is the ESG disclosure record. Instead of assigning a single score to an entire sustainability report, the system extracts record-level evidence units that can preserve text span, page provenance, ESG pillar, aspect, sentiment, tone, prompt template, model source, and downstream validation state. This record-centered design is necessary because a single report may contain future-facing commitments, operational actions, realized outcomes, and neutral governance descriptions in close proximity. Treating the report as one undifferentiated item would erase these distinctions.

The methodology is implemented as a dual-validation pipeline. The primary analytical stream is an LLM-driven extraction layer that converts OCR-derived text into structured ESG records. The secondary stream is a comparative audit layer using ClimateBERT-style climate labels and related ABSA outputs as external semantic reference points. The purpose of the second stream is not to claim that climate labels and ESG tone are identical. Rather, it is to test whether the extracted records exhibit plausible alignment with domain-relevant climate semantics while preserving a broader ESG disclosure taxonomy.

At the current implementation stage, the empirical snapshot contains 23 OCR documents, 332 structured ESG records, 2,074 T2 rows, 110 successful extraction runs, 7 prompt templates, and 2 model backends. These figures are used in this chapter as evidence of feasibility and methodological maturity, not as final population-level claims. The methodology therefore supports three thesis goals simultaneously: transforming reports into structured evidence, exposing weaknesses in that transformation, and preparing the ground for stronger benchmark evaluation in later work.

## 3.2 Data Sources

The study relies on a layered corpus architecture composed of source documents, intermediate preprocessing outputs, extraction artifacts, validation-oriented datasets, and reproducibility documentation. This structure reflects the fact that the thesis investigates the full path from corporate disclosure PDF to structured ESG evidence.

At the source level, the main empirical material consists of sustainability reports, annual reports, and related ESG disclosure documents associated with Indonesian companies. These are the natural language artifacts through which companies communicate environmental, social, and governance commitments, actions, and outcomes. The use of these reports is methodologically necessary because the thesis is concerned with how disclosures are written, not only with external scores derived from them.

At the preprocessing level, the operational text corpus is produced through OCR and page-level markdown conversion. In the repository, this layer is visible through per-document `ocr_result.json` files and page markdown under `data/thesis_dataset/<document>/pages/`. This page-aware representation is important because downstream extraction does not operate on raw PDF binaries. It operates on textual artifacts that preserve document segmentation and source traceability.

At the extraction level, the central artifact is the structured ESG record store represented by `results/esg_records.json` and the flattened analytical tables derived from it. These records provide the main evidence base for tone distribution, ESG pillar analysis, prompt-stability inspection, and ClimateBERT proxy comparison. Current thesis-facing summaries report 332 structured ESG records and 2,074 T2 rows, indicating that the system has moved beyond a small proof-of-concept into a reusable analytical workspace.

At the validation level, the study uses silver-label tables, review queues, and human-editable outputs. These include revision-analysis artifacts, ground-truth workbench tables, disagreement views, and numeric summaries. Their role is methodological rather than decorative. They make it possible to measure missing fields, schema drift, disagreement patterns, and annotation readiness without pretending that a fully mature benchmark already exists.

At the semantic interpretation level, the project also uses ontology-oriented artifacts and graph exports, including coverage tables and semantic export files intended for RDF, OWL, and Neo4j-style reuse. These support the thesis claim that extracted ESG records should not remain isolated rows only; they should also be connectable to structured sustainability concepts.

### 3.2.1 Dataset Characteristics

The dataset is best described as a bilingual, document-derived, record-centered ESG disclosure corpus. Its input units are long-form PDF reports, but its analytical units are extracted records. This creates a hierarchy spanning document level, page level, run level, and record level. Such a hierarchy is important because later interpretations of tone or greenwashing-oriented imbalance remain meaningful only if each record can be traced back to its source context.

The corpus is also semi-structured and noise-prone. Sustainability reports mix prose, tables, captions, boilerplate, page headers, and legal disclaimers. OCR output may therefore contain broken sentences, duplicate headings, page numbers, and fragmented table text. The methodology explicitly treats these artifacts as part of the research problem rather than as invisible preprocessing residue.

The current dataset should be described as weakly supervised. Some fields have silver labels, some are exposed for human correction, and some are compared against ClimateBERT-style outputs. However, the project does not yet have a complete expert-annotated benchmark covering all records and all target labels. This distinction matters. The dataset is already suitable for exploratory evaluation, diagnostic analysis, and thesis reporting, but not yet for strong final claims about generalizable classification accuracy.

Finally, the dataset is dynamic by construction. Outputs may change when prompt templates, model providers, parser logic, or preprocessing steps change. That is why the repository stores run-specific artifacts, prompt summaries, model summaries, and static dashboard exports. Reproducibility in this context requires artifact lineage, not just code availability.

### 3.2.2 Rationale for Data Selection

The choice of sustainability-report PDFs as the primary source material follows directly from the research problem. If the thesis aims to analyze the rhetorical structure of ESG disclosure, then the dataset must preserve the wording, location, and contextual framing of those disclosures. Prebuilt ESG score tables or heavily curated excerpts would not satisfy this requirement.

The Indonesian context further strengthens this rationale. Reports are often bilingual or mixed-language, disclosure quality varies, and readability is not uniform. These conditions make generic English-only sentiment datasets methodologically inadequate. A document-derived corpus is necessary because the pipeline must handle the same kinds of ambiguity and heterogeneity that analysts face in real reporting environments.

The use of page-level OCR outputs is also intentional. It reduces context-window pressure for downstream LLM extraction, preserves provenance, and enables targeted review when extraction fails. Similarly, the use of structured record outputs rather than document-level labels supports ABSA-style analysis by allowing the system to separate commitments from actions and outcomes.

The inclusion of ClimateBERT comparison artifacts, silver labels, and ontology coverage tables is justified because the thesis investigates validity and interpretability as well as extraction. These layers do not eliminate uncertainty, but they make uncertainty measurable and discussable.

### 3.2.3 Data Accessibility and Ethical Considerations

The primary source reports are corporate disclosures intended for public or semi-public stakeholder communication. This makes them appropriate for research use, but it does not automatically imply unrestricted redistribution. The methodology therefore distinguishes between source-document accessibility and derivative-artifact accessibility. In practice, the most reproducible research package is likely to consist of derived artifacts, schemas, run logs, and extraction summaries, while documenting the retrieval path for the original PDFs.

The project does not primarily process private personal data, so privacy risk is relatively low. The more important ethical issues concern interpretive distortion and overclaiming. OCR errors, extraction failures, schema drift, or prompt instability can misrepresent the meaning of a disclosure if not surfaced clearly. This is especially important because ESG analysis may influence judgments about transparency, legitimacy, or greenwashing risk.

For that reason, the methodology treats traceability and error visibility as ethical as well as technical requirements. Page-aware provenance, stored raw outputs, parse-audit views, and disagreement tables all help ensure that extracted claims can be challenged and reviewed. The current weak-label state of the benchmark also requires restraint: exploratory signals should not be presented as definitive firm-level verdicts.

## 3.3 Preprocessing Pipeline

The preprocessing pipeline is the bridge between raw sustainability reports and structured ESG records. In this thesis, preprocessing is not limited to text cleaning. It is a multi-stage transformation process that establishes traceability, removes obvious non-semantic noise, prepares text for extraction, and creates the intermediate artifacts required for validation.

The first stage is source intake and inventory preparation. Reports are gathered as PDFs and associated with document-level identifiers and metadata such as company, reporting year, language context, and file path. Even when metadata coverage is incomplete, the system assumes that each source document should have a stable identity so that OCR outputs, extracted records, review rows, and dashboard summaries can be linked consistently.

The second stage is OCR and page decomposition. The repository’s workflow centers this in the bulk OCR layer, which converts each report into markdown pages and OCR result files. This stage is necessary because the downstream extraction system cannot operate reliably on opaque PDFs. It needs accessible, page-level text units that preserve source boundaries.

The third stage is page-aware batching. Sustainability reports are too long and too structurally irregular to be passed to an LLM as a single monolithic input. The preprocessing design therefore groups text into bounded, provenance-preserving units. This batching strategy helps retain local context while avoiding uncontrolled prompt length and making it possible to revisit extraction errors at the page level.

The fourth stage is text cleaning and non-semantic artifact suppression. Common noise sources include page numbers, repeated headers, table fragments, legal disclaimers, and OCR-specific corruption. The purpose of cleaning is not to create a perfectly normalized corpus, but to reduce the frequency with which irrelevant layout noise is mistaken for analyzable ESG evidence.

The fifth stage is record preparation for downstream extraction and comparison. Once page batches are available, prompt templates in English and Indonesian are applied to produce structured JSON-like outputs that are later parsed into `esg_records.json`. At this stage, the pipeline also preserves prompt identity, model identity, run status, and parse outcomes so that failures remain visible.

The current implementation shows why this preprocessing design matters. The same corpus that yields 332 usable records also yields 61 missing-tone cases and observable schema drift. These weaknesses do not invalidate preprocessing; they demonstrate that preprocessing and extraction quality are tightly coupled and must be documented together.

## 3.4 Extraction and ABSA Layer

The extraction layer operationalizes the thesis claim that ESG disclosure should be modeled at record level. It combines prompt-driven LLM extraction with ABSA-oriented field design. Each extracted record is expected to contain at least text content, ESG pillar, aspect, sentiment, tone, and supporting metadata.

The tone taxonomy is particularly important. Instead of relying only on positive, negative, and neutral sentiment, the thesis uses commitment, action, outcome, none, and missing as disclosure-posture categories. This choice reflects the fact that corporate sustainability language often communicates intent or implementation status rather than overt opinion. A positive statement about a future target is not equivalent to a statement reporting a measured result.

The extraction design also supports an aspect-action logic that is relevant to greenwashing-oriented interpretation. An extracted statement is more useful when it links a topic or aspect to a concrete disclosure posture. This is why the pipeline aims to preserve both semantic content and structural role.

In the current repository state, the LLM extraction layer is implemented across seven prompt templates spanning zero-shot, few-shot, and chain-of-thought styles in English and Indonesian. This allows prompt formulation itself to become an experimental variable rather than a hidden implementation detail.

## 3.5 Core ABSA Logic and LLM Engine

The system uses a hybrid logic rather than a single-model assumption. Rule-based and ontology-aware components contribute interpretability, LLM extraction contributes semantic flexibility, and comparison layers contribute diagnostic pressure. This architecture is preferable to a single opaque extractor because ESG text is both semantically varied and structurally fragile.

Prompt engineering is treated as part of the methodology. Different prompt families test whether examples, reasoning instructions, or language alignment improve structured extraction. This is necessary because a pipeline that succeeds only under one narrow prompt configuration is methodologically weak.

The LLM engine therefore functions as an information-extraction component embedded within a controlled research workflow. Outputs are not accepted at face value. They are parsed, counted, compared, and exposed to review.

## 3.6 Validation and Silver Dataset

Because a full expert-labeled benchmark does not yet exist, the thesis uses a staged validation design. The first layer is model-generated structured output. The second layer is silver-label scaffolding and revision-analysis tables. The third layer is human-editable annotation infrastructure intended to mature into formal ground truth.

This design makes it possible to proceed with benchmark construction while remaining explicit about current limits. The present workspace already exposes important weaknesses: 61 records have missing tone, some records show schema drift where `commitment` appears in the sentiment field, and the ClimateBERT remote comparison layer is still limited relative to the full corpus. These are not minor implementation issues; they are part of the current methodological boundary.

Overall, the methodology of this thesis is best understood as an executable benchmark-construction framework. It already demonstrates that sustainability-report PDFs can be transformed into structured ESG evidence with meaningful comparative and diagnostic layers. At the same time, it makes clear that stronger evaluation depends on deeper annotation, tighter OCR measurement, and more complete matched-model comparison.
