# 0.0 Streamlit Page Workflow

## Purpose

This page is the navigation and workflow hub for the ESG ABSA Streamlit app. It explains every active Streamlit page, when to use it, what evidence it produces, and how it supports each research question.

## Main Features

- A registry of every Streamlit page in `new_page/pages`.
- Grouped page redirects using Streamlit page links where available.
- RQ-by-RQ workflow steps for RQ1 through RQ6.
- A complete Mermaid workflow from PDF ingestion to thesis synthesis.
- RQ-filtered Mermaid edges using labels such as `RQ1` or `RQ1, RQ5`.
- Chapter-level guidance for Chapter 3, Chapter 4, Chapter 5, and Chapter 6.
- Documentation index preview for the relevant Markdown files.

## Research Question Workflow

The `RQ Workflows` tab is the most important part of the page. For each RQ, it lists:

- the goal of the RQ,
- the exact Streamlit pages to open,
- the action to perform on each page,
- the thesis chapter where the evidence should be used.

## Filterable Mermaid Workflow

The `Complete Workflow` tab contains a Mermaid workflow whose edges are labeled by research question:

```mermaid
node_I_A_4 -- "RQ1" --> node_V_C_1
node_I_A_4 -- "RQ1, RQ5" --> node_V_C_1
```

The filter treats `RQ1, RQ5` as a multi-RQ path. Selecting `RQ1` shows the edge, selecting `RQ5` also shows the edge, and selecting both can be filtered with either "match any" or "match all" behavior.

This makes the diagram useful as a thesis evidence router: choose an RQ and the visible graph narrows to only the pages and artifacts needed to answer that RQ.

## Thesis Use

- Chapter III: method workflow and reproducibility map.
- Chapter IV: results workflow and figure source map.
- Chapter V: discussion and limitation evidence routing.
- Chapter VI: final RQ answer and future-work routing.
- Defense: live navigation page for answering "where is the evidence for this claim?"

## Related Pages

- `1_7_Research_Questions_Dashboard.py` for RQ synthesis, sample-size reasoning, and Chapter 4-6 planning.
- `0_9_Tone_ClimateBERT_Visualization.py` for core ABSA visual outputs.
- `1_0_Revision_Analytics.py` for revision metrics, greenwashing, stability, and diagnostics.
- `2_1_LLM_Error_Parse_Audit.py` for failure and parse-error evidence.
