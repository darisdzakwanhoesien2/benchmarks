# Bulk OCR

## Purpose

This page performs document ingestion and OCR preprocessing. It converts PDF or image-based sustainability reports into machine-readable markdown pages and extracted artifacts.

## Data Used

Inputs:

- uploaded PDF files,
- sustainability reports stored under `data/thesis_pdf/`.

Outputs:

- page-level markdown under `data/thesis_dataset/<document>/pages/`,
- extracted images under `data/thesis_dataset/<document>/images/`,
- OCR JSON such as `ocr_result.json`,
- processing logs under `logs/bulk_ocr_log.json`.

## Workflow Steps

1. Select or upload reports.
2. Run OCR processing.
3. Save page-level markdown.
4. Save extracted images if available.
5. Update processing logs.
6. Reuse logs to avoid rerunning completed documents.

## Interpretation

The OCR layer is the first stage of the pipeline. Its quality affects every downstream model. No classification result should be interpreted without considering OCR quality, especially for tables, bilingual columns, and infographics.

## Thesis Use

- Chapter III: data preprocessing.
- Chapter IV: PDF-to-structured evidence pipeline.
- OCR quality should be evaluated using `1_2_OCR_Quality_Workbench.py`.

