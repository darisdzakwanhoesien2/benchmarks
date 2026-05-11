# 0.2 JSON Ontology Usage Map

## Purpose

This page inventories the ontology, category, grouping, and mapping JSON artifacts used across the ESG ABSA benchmark dashboards. It answers a practical maintenance question: which Streamlit pages use each JSON file, and which pages should use it semantically.

## Data Used

The page covers JSON files from:

- `benchmarks/data/`
- `benchmarks/new_page/results/revision_analysis/`
- `benchmarks/new_page/results/data/`
- `benchmarks/esg_dashboard_new-main/dashboard/data/`

## Main Features

- Inventory table with file status, JSON type, top-level keys, and file role.
- Usage matrix showing direct code references and recommended Streamlit pages.
- JSON inspector for one artifact at a time.
- Raw reference scan across Python, Markdown, TOML, and JSON files under `benchmarks/`.
- Mermaid diagram grouping JSON artifacts by ontology/mapping family.

## Thesis Use

- Chapter III: taxonomy and artifact-management methodology.
- Chapter IV: evidence that ontology and category mappings are auditable.
- Chapter V: discussion of taxonomy drift, duplicate ontology copies, and maintenance risks.
- Chapter VI: future work for consolidating ontology artifacts into a single canonical source.
