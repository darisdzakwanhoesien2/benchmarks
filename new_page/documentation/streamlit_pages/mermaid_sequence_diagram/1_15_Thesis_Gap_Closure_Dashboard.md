# Thesis Gap Closure Dashboard

- Filename: `1_15_Thesis_Gap_Closure_Dashboard.py`
- Source path: `pages/1_15_Thesis_Gap_Closure_Dashboard.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/1_15_Thesis_Gap_Closure_Dashboard.md`
- Page slug: `1_15_Thesis_Gap_Closure_Dashboard`
- Category: `thesis`
- Purpose: Aggregate evidence into workflow, dashboard, and chapter-ready thesis views.
- Primary inputs: research artifacts, charts, notes, chapter evidence tables
- Primary outputs: chapter summaries, Mermaid maps, narrative guidance, evidence matrices
- Summary: Thesis synthesis and navigation.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as Thesis author
    participant page as 1_15_Thesis_Gap_Closure_Dashboard.py
    participant runtime as Streamlit runtime
    participant data as Research artifacts
    participant compute as Synthesis / chapter logic
    participant output as Chapter-ready output
    Note over page: pages/1_15_Thesis_Gap_Closure_Dashboard.py
    User->>page: open workflow, dashboard, or chapter assembly view
    page->>runtime: initialize layout, tabs, and filters
    page->>data: gather evidence tables, charts, notes, and artifacts
    page->>compute: map findings to claims, sections, or chapter structure
    compute->>compute: consolidate narrative logic and evidence links
    compute->>output: render summaries, Mermaid maps, and chapter-ready guidance
    output-->>page: return composed thesis-facing views
    page->>User: display evidence paths and writing guidance
```
