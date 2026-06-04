# Source Data Catalog

- Filename: `0_11_Source_Data_Catalog.py`
- Source path: `pages/0_11_Source_Data_Catalog.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/0_11_Source_Data_Catalog.md`
- Page slug: `0_11_Source_Data_Catalog`
- Category: `ingestion`
- Purpose: Collect source documents, enrich provenance, and persist reusable dataset artifacts.
- Primary inputs: PDFs, page images, OCR payloads, metadata forms
- Primary outputs: OCR markdown, JSON, images, catalog entries
- Summary: Ingestion and provenance capture.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as User
    participant page as 0_11_Source_Data_Catalog.py
    participant runtime as Streamlit runtime
    participant data as PDFs / source files
    participant compute as OCR / metadata logic
    participant output as Dataset artifacts
    Note over page: pages/0_11_Source_Data_Catalog.py
    User->>page: open page and provide source inputs
    page->>runtime: initialize controls and session state
    page->>compute: validate files, options, and metadata fields
    compute->>data: read document bytes and source content
    compute->>compute: run OCR or metadata enrichment steps
    compute->>output: persist markdown, JSON, images, and catalogs
    output-->>page: return saved paths and processing status
    page->>User: display progress, results, and next actions
```
