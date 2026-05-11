# 2.2 LLM Statement Page Verifier

## Purpose

This page maps parsed LLM ESG statements from `results/esg_records.json` back to OCR markdown pages in `data/thesis_dataset`. It checks whether each extracted statement is grounded in the source report page text.

## Main Features

- Filter extracted LLM statements by document, target batch, model, prompt, ESG pillar, tone, sentiment, and aspect.
- Search the OCR pages for the selected extracted statement.
- Classify page evidence as `exact`, `likely`, `possible`, or `not found`.
- Show the best matching OCR page, token coverage, match score, and highlighted evidence snippet.
- Download the top page-match results as CSV.

## Thesis Use

- RQ1: demonstrates traceability from structured LLM record back to OCR source text.
- RQ4: identifies potential hallucinations, weak grounding, or OCR mismatch cases.
- RQ5: strengthens auditability by linking records, pages, and evidence snippets.
- RQ6: compares whether different model/prompt outputs are equally grounded in source pages.

## Inputs

- `new_page/results/esg_records.json`
- `new_page/data/thesis_dataset/<document>/pages/page_*.md`

## Outputs

- Interactive evidence checks in Streamlit.
- Downloadable CSV of page-match candidates for the selected statement.
