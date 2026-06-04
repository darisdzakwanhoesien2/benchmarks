# JSON Ontology Usage Map

- Filename: `0_2_JSON_Ontology_Usage_Map.py`
- Source path: `pages/0_2_JSON_Ontology_Usage_Map.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/0_2_JSON_Ontology_Usage_Map.md`
- Page slug: `0_2_JSON_Ontology_Usage_Map`
- Category: `analysis`
- Purpose: Load prepared artifacts and turn them into filtered analytical views.
- Primary inputs: CSV, JSON, cached tables, visualization inputs
- Primary outputs: charts, filtered tables, lineage views, exportable summaries
- Summary: Analysis and visualization flow.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as Analyst
    participant page as 0_2_JSON_Ontology_Usage_Map.py
    participant runtime as Streamlit runtime
    participant data as Input artifacts
    participant compute as Page logic
    participant output as Visual output
    Note over page: pages/0_2_JSON_Ontology_Usage_Map.py
    User->>page: adjust filters and inspect page content
    page->>runtime: initialize widgets and local state
    page->>data: load source artifacts for the current view
    page->>compute: transform, aggregate, and filter data
    compute->>output: generate charts, tables, exports, or maps
    output-->>page: return rendered analytical assets
    page->>User: present results and interpretation cues
```
