# ClimateBERT Multi-Model Runner

- Filename: `1_14_ClimateBERT_Multi_Model_Runner.py`
- Source path: `pages/1_14_ClimateBERT_Multi_Model_Runner.py`
- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/1_14_ClimateBERT_Multi_Model_Runner.md`
- Page slug: `1_14_ClimateBERT_Multi_Model_Runner`
- Category: `llm`
- Purpose: Run or inspect model outputs, parse results, and surface diagnostics for review.
- Primary inputs: OCR text, model outputs, background job files, parser results
- Primary outputs: parsed records, diagnostics, model comparisons, run status views
- Summary: LLM extraction and diagnostics.

## Detailed Sequence

```mermaid
sequenceDiagram
    actor User as Analyst
    participant page as 1_14_ClimateBERT_Multi_Model_Runner.py
    participant runtime as Streamlit runtime
    participant data as OCR text / run outputs
    participant compute as LLM / parser / benchmark logic
    participant output as Results and diagnostics
    Note over page: pages/1_14_ClimateBERT_Multi_Model_Runner.py
    User->>page: choose model, run, prompt, or audit target
    page->>runtime: initialize page state and controls
    page->>data: load OCR text, cached jobs, or parsed outputs
    page->>compute: parse outputs, compare models, or monitor execution
    alt background or batch run exists
        compute->>output: update job status, diagnostics, and result tables
    else direct analysis view
        compute->>output: build charts, audits, and comparison summaries
    end
    output-->>page: return diagnostics and visual artifacts
    page->>User: show model quality, failures, and next steps
```
