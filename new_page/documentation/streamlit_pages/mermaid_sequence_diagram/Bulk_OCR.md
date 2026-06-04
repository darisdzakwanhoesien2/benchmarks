# 📚 Bulk OCR — Mistral

- Filename: `Bulk_OCR.py`
- Source path: `pages/Bulk_OCR.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/Bulk_OCR.md`
- Page slug: `Bulk_OCR`
- Category: `ingestion`
- Purpose: Collect source documents, enrich provenance, and persist reusable dataset artifacts.
- Primary inputs: PDFs, page images, OCR payloads, metadata forms
- Primary outputs: OCR markdown, JSON, images, catalog entries
- Summary: Ingestion and provenance capture.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as User
    participant page as Bulk_OCR.py
    participant runtime as Streamlit runtime
    participant data as PDFs / source files
    participant compute as OCR / metadata logic
    participant output as Dataset artifacts
    Note over page: pages/Bulk_OCR.py
    User->>page: open page and provide source inputs
    page->>runtime: initialize controls and session state
    page->>compute: validate files, options, and metadata fields
    compute->>data: read document bytes and source content
    compute->>compute: run OCR or metadata enrichment steps
    compute->>output: persist markdown, JSON, images, and catalogs
    output-->>page: return saved paths and processing status
    page->>User: display progress, results, and next actions
```
