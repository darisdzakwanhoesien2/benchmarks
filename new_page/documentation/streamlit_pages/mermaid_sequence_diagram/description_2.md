# Combined Streamlit Workflow

* Scope: All active Streamlit page families
* Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/Combined_Streamlit_Workflow.md`
* Purpose: Explain the repository as one connected research system rather than as isolated pages
* Shared artifacts: CSV, JSON, JSONL, XLSX, MD, PNG, PDF

## What This Document Is For

This document is the narrative companion to the combined Mermaid sequence diagram. The diagram shows motion. This file explains meaning.

The repository is easiest to understand when viewed as an artifact-driven research pipeline. The Streamlit pages are only the visible interface. Underneath them is a shared layer of datasets, registries, OCR outputs, annotations, event logs, model results, and thesis-ready summaries. Each page family reads from that layer, reshapes part of it, and returns a more interpretable view to the researcher.

That matters because the system does not behave like a sequence of disconnected dashboards. A source PDF may first appear as a raw document, then as OCR text, then as a catalog entry, then as a row in a validation dataset, then as an LLM processing target, and finally as evidence used in a thesis chapter. The combined workflow exists to make that lifecycle explicit.

## The System as a Research Story

The workflow begins with source materials: company reports, sustainability reports, ESG disclosures, and related files. At that point the system knows very little. It may know a filename, a directory location, or a PDF binary, but it does not yet know whether the document has useful text, whether it has been cataloged, whether it contains ESG evidence, or whether it has been reviewed by a human or model.

The ingestion-oriented pages reduce that uncertainty. They extract OCR text, build page-level assets, register source files, attach metadata, and create the first structured records that other pages can consume. Once those artifacts exist, they stop being tied to a single page. They become shared project assets.

The analysis-oriented pages then act as the system's inspection layer. They do not mainly create new evidence. Instead, they help the researcher see the shape of the data: what exists, what is missing, how records are distributed, how ontology mappings are being used, how phase assignments are changing, and which files or companies dominate a particular slice of the corpus.

Ground-truth pages move the workflow from visibility to reliability. They check whether rows are labeled, whether annotations are complete, whether benchmark outputs are trustworthy, and whether the evidence base is good enough to support comparison and interpretation.

LLM pages extend that process into automated extraction and monitoring. They run prompts, collect model outputs, track background jobs, inspect failures, verify page references, and expose where generated records are usable and where they still need review.

Finally, the thesis pages convert the validated artifact ecosystem into narrative structure. At that stage the goal is no longer only to inspect data. The goal is to connect evidence, methods, figures, claims, and chapter logic into material that can be written into Chapters 4, 5, and 6.

In short, the full movement is:

`source document -> extracted artifact -> inspected dataset -> validated record -> modeled or benchmarked output -> thesis evidence`

## How the Data Structure Actually Works

The most important structural idea in this repository is that the system works at the record level, but each record remains connected to higher-level artifacts such as PDFs, jobs, prompts, and phase registries.

At a high level, the data model has five layers.

### 1. Source Artifact Layer

This is the raw or near-raw project material:

* PDF files
* OCR markdown or text outputs
* source catalogs
* image exports
* metadata files

This layer answers basic provenance questions: what document is this, where did it come from, and what generated artifacts already exist for it?

### 2. Record Layer

This is the core analytical layer used by many pages. A record is usually a row-like unit representing a statement, sentence, disclosure fragment, benchmark row, or parsed model output.

In `code/dataset_phase_utils.py`, records are assembled from several sources:

* `results/revision_analysis/pilot_ground_truth_annotations.csv`
* `results/revision_analysis/silver_tone_ground_truth.csv`
* `results/esg_records.json`
* `results/background_llm_jobs/*/events.jsonl`

These are merged into one normalized view by `build_source_records()`. The function creates or preserves a stable `record_id`, aligns column names, fills missing columns, and appends LLM-derived rows that are not already present in the annotation tables.

Common record-level fields include:

* `record_id`
* `source_dataset`
* `target`
* `text`
* `model`
* `prompt`
* `tone_pred`
* `esg`
* `aspect`
* `ground_truth_tone`
* `ground_truth_esg`
* `ground_truth_aspect`
* `review_status`
* `annotator`
* `review_notes`
* `background_job_id`

This is why many pages can interoperate even when they focus on different tasks. They are often reading different projections of the same normalized record space.

### 3. Completion and Validation Layer

After the raw records are assembled, the system computes whether they are complete enough for downstream use. The function `completion_flags()` derives flags such as:

* whether ground-truth tone exists
* whether ground-truth ESG exists
* whether ground-truth aspect exists
* which core fields are still missing
* whether the record is ready for Phase 1 completion
* whether the record is complete with QA

This layer is important because the repository does not treat every row as equally ready. Some rows are still under review. Some are partially labeled. Some are complete enough for analysis but not for final reporting. Some are automatically generated and still need human verification.

### 4. Phase Registry Layer

The project also keeps a separate registry that tracks where each record sits in the workflow. That registry lives in:

* `results/revision_analysis/dataset_phase_registry.csv`

This is not the same thing as the record dataset itself. The record dataset stores content and labels. The phase registry stores workflow state.

The registry includes fields such as:

* `record_id`
* `phase`
* `phase_reason`
* `first_seen_at`
* `updated_at`
* `updated_by`

The separation is useful. It means a row can keep its analytical content while its workflow status changes independently. A record may move from Phase 3 to Phase 2 or from Phase 2 to Phase 1 without rewriting its entire content payload.

### 5. Enrichment and PDF Metadata Layer

Several pages, especially the phase-distribution pages, enrich record-level data with PDF-level context. In `add_pdf_metadata()`, the repository derives:

* `original_file`
* `company_name`
* `report_year`
* `ticker`
* `ticker_company_name`
* `ticker_sector`
* `metadata_source`

This enrichment is inferred from the `target` path, filename patterns, manual overrides, and the ticker universe file:

* `data/indonesia_tickers.csv`

That step is what allows the repository to move from statement-level analysis back up to company-level and report-level comparison.

## A Concrete Example: Phase-Based Pages

The phase-management pages show this structure clearly.

The page [`1_20_Phase_PDF_Distribution.md`](./1_20_Phase_PDF_Distribution.md) looks simple on the surface because it mostly renders metrics, tables, and bar charts. But underneath that interface is a layered join:

1. `phase_view()` builds a normalized record table.
2. That table merges record content with completion flags and the external phase registry.
3. `add_pdf_metadata()` enriches each row with PDF-level identity such as original file, ticker, sector, and report year.
4. The page groups those rows by `original_file` and phase.
5. The result is presented as cross-phase PDF distribution, per-phase counts, and Phase 3 intake summaries.

This means the page is not just counting files in folders. It is counting workflow rows that are connected back to their source PDFs.

That distinction is important. If one PDF produces many statement-level rows, those rows can appear in different operational states. The page therefore answers a research operations question, not merely a file inventory question:

`How is evidence from each source document distributed across completed, editing, and new-intake workflow stages?`

## How Page Families Relate to the Data Structure

### Ingestion Pages

These pages work closest to the source artifact layer. They create the first reusable project assets: OCR text, metadata, catalogs, image outputs, and document references.

They are the point where raw files become structured inputs for the rest of the system.

### Analysis Pages

These pages work mostly across the record, registry, and enrichment layers. They ask questions such as:

* what does the dataset currently contain
* how are records distributed
* which mappings or ontology paths are dominant
* which PDFs, companies, or sectors are overrepresented
* where are the missing values or incomplete regions

Their role is interpretive and diagnostic.

### Ground-Truth Pages

These pages work heavily on the completion and validation layer. They expose whether labels exist, whether benchmark rows are aligned, and whether the project has enough trustworthy rows to support comparison and reporting.

They help convert raw record volume into reliable evidence.

### LLM Pages

These pages connect the record layer to the background-job layer. They consume prompt configuration, model outputs, and event logs, then turn them into trackable operational records.

This is where fields like `background_job_id`, `event`, `success_event_timestamp`, and job progress metrics become analytically useful rather than just operational logs.

### Thesis Pages

These pages consume the most curated end of the artifact system. They are less concerned with raw record generation and more concerned with synthesizing validated outputs into chapter-level evidence, Mermaid maps, figures, lineage tables, and narrative scaffolding.

They are where the data structure becomes argument structure.

## Why the Combined Workflow Matters

The repository contains many pages, and without a combined explanation it is easy to misunderstand the architecture as a large UI collection. It is not. It is a research workflow with UI entry points.

The combined workflow matters because it makes four relationships visible:

* page-to-artifact relationships
* artifact-to-record relationships
* record-to-phase relationships
* evidence-to-thesis relationships

Once those relationships are clear, individual pages become easier to place. A page is no longer just "another dashboard." It is part of one of the system's major responsibilities: ingestion, inspection, validation, model processing, or synthesis.

## Reading This Diagram in Practice

A practical way to use the combined workflow is:

1. Start here when you need the high-level architecture.
2. Move to a page-family document when you know which stage of the workflow you care about.
3. Move to the page-level Mermaid document when you need the internal logic of one Streamlit page.
4. Check the underlying CSV, JSON, JSONL, or registry file when you need to verify how the page-level output was assembled.

If something looks wrong in the UI, the combined workflow helps you trace the likely failure point:

* missing source artifact
* incomplete normalization
* broken enrichment
* missing phase registry row
* incomplete ground-truth fields
* failed background job
* thesis page expecting an artifact that was never produced

## Summary

This combined workflow is best understood as a narrative of evidence maturation.

The repository begins with documents, converts them into reusable artifacts, assembles those artifacts into normalized records, tracks those records through workflow phases, enriches them with metadata, validates them through annotation and model review, and finally turns them into thesis-ready evidence.

The Mermaid diagram gives the motion. The underlying data structure explains why that motion is coherent.
