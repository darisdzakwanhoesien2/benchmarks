# Thesis Systematic Workflow Dashboard

- Filename: `5_Thesis_Systematic_Workflow_dashboard.py`
- Source path: `pages/5_Thesis_Systematic_Workflow_dashboard.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/5_Thesis_Systematic_Workflow_dashboard.md`
- Page slug: `5_Thesis_Systematic_Workflow_dashboard`
- Category: `thesis`
- Purpose: Aggregate evidence into workflow, dashboard, and chapter-ready thesis views.
- Primary inputs: research artifacts, charts, notes, chapter evidence tables
- Primary outputs: chapter summaries, Mermaid maps, narrative guidance, evidence matrices
- Summary: Thesis synthesis and navigation.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as Thesis author
    participant page as 5_Thesis_Systematic_Workflow_dashboard.py
    participant runtime as Streamlit runtime
    participant data as Research artifacts
    participant compute as Synthesis / chapter logic
    participant output as Chapter-ready output
    Note over page: pages/5_Thesis_Systematic_Workflow_dashboard.py
    User->>page: open workflow, dashboard, or chapter assembly view
    page->>runtime: initialize layout, tabs, and filters
    page->>data: gather evidence tables, charts, notes, and artifacts
    page->>compute: map findings to claims, sections, or chapter structure
    compute->>compute: consolidate narrative logic and evidence links
    compute->>output: render summaries, Mermaid maps, and chapter-ready guidance
    output-->>page: return composed thesis-facing views
    page->>User: display evidence paths and writing guidance
```
