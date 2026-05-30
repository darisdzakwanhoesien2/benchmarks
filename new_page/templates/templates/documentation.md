codex-mirbuds resume 019e7858-4964-7223-98c4-650e51d43d81
# Streamlit Templates: Pages, Data, Relationships

This folder (`new_page/templates/`) contains **template Streamlit pages** that are copied into `new_page/pages/` (or used as reference implementations) for thesis-facing dashboards.

The active Streamlit app is launched from `new_page/app.py`, which discovers all pages in `new_page/pages/`.

## What is in this folder

### `templates/3_0_Thesis_Action_Plan.py`

Purpose:
- Operational “control room” for the thesis workflow: shows what is done, what is missing, and what to run next.

Primary data consumed:
- `new_page/results/revision_analysis/*.csv` (silver records, prompt/model stability summaries, ontology coverage, failure modes, OCR summary, gap audits, etc.)
- `new_page/results/background_llm_jobs/*` and `new_page/results/climatebert_background_jobs/*` (status + events for long jobs)
- `new_page/prompt/*` (prompt templates used for extraction)

Primary outputs produced:
- Action-plan exports and “board” artifacts (for example chapter-resolution decisions) under `new_page/results/revision_analysis/`.

Relationship role:
- **Synthesizes** multiple artifact families into a single “what to do next” view.
- **Bridges** analysis pages (revision/metrics/ontology) with chapter-writing pages (6.x).

### `templates/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`

Purpose:
- A thesis “spine” page that connects: thesis draft (PDF), chapter docx, Streamlit pages, Mermaid workflow, and evidence metrics.

Primary data consumed:
- `new_page/thesis_draft_1.pdf`
- `new_page/pages/thesis_chapters_4_5_6.docx`
- `new_page/results/revision_analysis/*`

Primary outputs produced:
- In-page Mermaid graphs and tables intended to be cited directly when writing Chapters 4–6.

Relationship role:
- **Sits above** analysis pages: it does not generate raw extraction data; it assembles and explains it.

### `templates/6_4_ch4-6.py`

Purpose:
- Chapter 4–6 “benchmarks + DOCX graphs” page that loads frozen analysis snapshots and exports DOCX attachments/graphs.

Primary data consumed:
- `new_page/results/ch4_6_frozen_analysis/*`
- `new_page/results/revision_analysis/*`
- `new_page/results/docx_graph_attachments/*`

Primary outputs produced:
- Generated/updated DOCX (benchmark structure + Streamlit graphs embedded)
- Attachment graphs/images in `new_page/results/docx_graph_attachments/` and `new_page/results/visualizations/`

Relationship role:
- **Transforms** analysis artifacts into thesis-appendix-ready documents.

## Data model and relationships (how pages connect)

At the system level, the Streamlit pages form an evidence pipeline:

1. **Inputs** (PDFs, OCR outputs)
2. **Extraction** (LLM runs -> structured records)
3. **Validation & audit** (ground-truth, ontology coverage, error audits, statement grounding)
4. **Synthesis** (RQ dashboard + chapter integration pages)

The key relationship types are:
- `generates`: a page or script produces an artifact file/folder.
- `consumes`: a page reads an artifact file/folder.
- `validates`: a page checks quality/consistency/grounding of upstream artifacts.
- `audits`: a page inspects failures, missing fields, or drift.
- `synthesizes`: a page packages many artifacts into thesis-ready narrative/tables/graphs.

## Embedded JSON registry (canonical mapping)

The canonical, human-editable mapping of **page → RQ → artifacts** lives at:
- `new_page/documentation/streamlit_pages/page_relationships.json`

This JSON is intended to be used as:
- a documentation source of truth (what each page is for and what it reads/writes)
- a registry to keep Streamlit navigation pages synchronized (for example `0_0_Streamlit_Page_Workflow.py`)

If you add a new page:
1. Add it to `page_relationships.json` (page metadata + outputs).
2. Add/update the corresponding markdown page doc under `new_page/documentation/streamlit_pages/`.
3. Optionally add the page to `new_page/app.py` under “Core pages” or “Utilities”.

## Using the registry as templates

If you are building *new* pages, treat the existing pages as templates in this way:
- Copy UI patterns (tabs, `st.dataframe`, Mermaid rendering, artifact loading) from:
  - `new_page/pages/0_0_Streamlit_Page_Workflow.py` (registry-style navigation + Mermaid filtering)
  - `new_page/pages/0_2_JSON_Ontology_Usage_Map.py` (JSON inventory + reference scan)
  - `new_page/pages/1_7_Research_Questions_Dashboard.py` (thesis-facing synthesis + evidence tables)
- Register each new page in `page_relationships.json` so the workflow map and documentation stay consistent.

