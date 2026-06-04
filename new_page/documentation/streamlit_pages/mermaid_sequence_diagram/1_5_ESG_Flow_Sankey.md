# ESG Flow Sankey

- Filename: `1_5_ESG_Flow_Sankey.py`
- Source path: `pages/1_5_ESG_Flow_Sankey.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/1_5_ESG_Flow_Sankey.md`
- Page slug: `1_5_ESG_Flow_Sankey`
- Category: `analysis`
- Purpose: Load prepared artifacts and turn them into filtered analytical views.
- Primary inputs: CSV, JSON, cached tables, visualization inputs
- Primary outputs: charts, filtered tables, lineage views, exportable summaries
- Summary: Analysis and visualization flow.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as Analyst
    participant page as 1_5_ESG_Flow_Sankey.py
    participant runtime as Streamlit runtime
    participant data as Input artifacts
    participant compute as Page logic
    participant output as Visual output
    Note over page: pages/1_5_ESG_Flow_Sankey.py
    User->>page: adjust filters and inspect page content
    page->>runtime: initialize widgets and local state
    page->>data: load source artifacts for the current view
    page->>compute: transform, aggregate, and filter data
    compute->>output: generate charts, tables, exports, or maps
    output-->>page: return rendered analytical assets
    page->>User: present results and interpretation cues
```
