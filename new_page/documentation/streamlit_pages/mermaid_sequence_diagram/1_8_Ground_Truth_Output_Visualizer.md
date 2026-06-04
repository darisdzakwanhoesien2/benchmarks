# Ground Truth Output Visualizer

- Filename: `1_8_Ground_Truth_Output_Visualizer.py`
- Source path: `pages/1_8_Ground_Truth_Output_Visualizer.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/1_8_Ground_Truth_Output_Visualizer.md`
- Page slug: `1_8_Ground_Truth_Output_Visualizer`
- Category: `ground_truth`
- Purpose: Inspect or curate labeled data, then compute validation and audit outputs.
- Primary inputs: annotated records, audit tables, validation datasets
- Primary outputs: coverage tables, audit reports, metrics, record views
- Summary: Annotation and audit workflow.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as Annotator / Analyst
    participant page as 1_8_Ground_Truth_Output_Visualizer.py
    participant runtime as Streamlit runtime
    participant data as Ground-truth records
    participant compute as Validation / metrics logic
    participant output as Audit outputs
    Note over page: pages/1_8_Ground_Truth_Output_Visualizer.py
    User->>page: select records, labels, or audit scope
    page->>runtime: apply widget state and filters
    page->>data: load annotations, runs, and record context
    page->>compute: compute coverage, agreement, metrics, or audit diffs
    compute->>compute: validate labels and trace record lineage
    compute->>output: produce metrics tables, audit views, and summaries
    output-->>page: return derived findings
    page->>User: render validation status and unresolved issues
```
