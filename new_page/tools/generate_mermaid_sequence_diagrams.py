from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "pages"
OUT_DIR = ROOT / "documentation" / "streamlit_pages" / "mermaid_sequence_diagram"


def extract_title(page_path: Path) -> str:
    text = page_path.read_text(encoding="utf-8", errors="ignore")
    patterns = [
        r"st\.set_page_config\(page_title=([\"'])(.*?)\1",
        r"st\.title\(([\"'])(.*?)\1\)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(2)
    return page_path.stem


def relative_page_path(page_path: Path) -> str:
    return str(page_path.relative_to(ROOT))


def slug_for(page_path: Path) -> str:
    return page_path.stem


def category_for(page_name: str) -> str:
    if page_name in {"Bulk_OCR.py", "0_3_OCR_Company_Metadata_Labeler.py", "0_11_Source_Data_Catalog.py"}:
        return "ingestion"
    if page_name in {"ground_truth.py", "1_1_Ground_Truth_Workbench.py", "1_2_OCR_Quality_Workbench.py", "1_3_Ground_Truth_Metrics.py", "1_8_Ground_Truth_Output_Visualizer.py", "1_9_Ground_Truth_Pipeline_Output_Visualizer.py", "1_10_Ground_Truth_Run_Coverage.py", "1_11_Ground_Truth_Record_Audit.py", "1_12_Ground_Truth_Step_By_Step_Visualizer.py"}:
        return "ground_truth"
    if page_name in {"llm_processing.py", "2_0_LLM_Processing_Result_Visualizer.py", "2_1_LLM_Error_Parse_Audit.py", "2_2_LLM_Statement_Page_Verifier.py", "2_3_LLM_Background_Run_Monitor.py", "2_4_PDF_Page_Processing_Audit.py", "2_5_LLM_Model_Catalog_Visualizer.py", "1_4_ClimateBERT_Record_Batch.py", "1_14_ClimateBERT_Multi_Model_Runner.py", "0_9_Tone_ClimateBERT_Visualization.py"}:
        return "llm"
    if page_name in {"0_0_Streamlit_Page_Workflow.py", "1_7_Research_Questions_Dashboard.py", "3_0_Thesis_Action_Plan.py", "5_Thesis_Systematic_Workflow_dashboard.py", "5_1_Thesis_Systematic_Workflow_dashboard_generated.py", "6_0_Thesis_Draft_Chapter_Integration_Mermaid.py", "6_1_Chapter_4_Implementation_Results.py", "6_2_Chapter_5_Discussion.py", "6_3_Chapter_6_Conclusion.py", "6_4_ch4-6.py", "0_5_Thesis_Systematic_Workflow.py", "1_15_Thesis_Gap_Closure_Dashboard.py"}:
        return "thesis"
    return "analysis"


def purpose_for(category: str) -> str:
    mapping = {
        "ingestion": "Collect source documents, enrich provenance, and persist reusable dataset artifacts.",
        "ground_truth": "Inspect or curate labeled data, then compute validation and audit outputs.",
        "llm": "Run or inspect model outputs, parse results, and surface diagnostics for review.",
        "thesis": "Aggregate evidence into workflow, dashboard, and chapter-ready thesis views.",
        "analysis": "Load prepared artifacts and turn them into filtered analytical views.",
    }
    return mapping[category]


def primary_inputs_for(category: str) -> str:
    mapping = {
        "ingestion": "PDFs, page images, OCR payloads, metadata forms",
        "ground_truth": "annotated records, audit tables, validation datasets",
        "llm": "OCR text, model outputs, background job files, parser results",
        "thesis": "research artifacts, charts, notes, chapter evidence tables",
        "analysis": "CSV, JSON, cached tables, visualization inputs",
    }
    return mapping[category]


def primary_outputs_for(category: str) -> str:
    mapping = {
        "ingestion": "OCR markdown, JSON, images, catalog entries",
        "ground_truth": "coverage tables, audit reports, metrics, record views",
        "llm": "parsed records, diagnostics, model comparisons, run status views",
        "thesis": "chapter summaries, Mermaid maps, narrative guidance, evidence matrices",
        "analysis": "charts, filtered tables, lineage views, exportable summaries",
    }
    return mapping[category]


def diagram_for(page_path: Path, title: str, category: str) -> tuple[str, str]:
    user_node = "User"
    page_node = "page"
    runtime_node = "runtime"
    data_node = "data"
    compute_node = "compute"
    out_node = "output"
    file_note = page_path.name
    relative_note = relative_page_path(page_path)

    if category == "ingestion":
        lines = [
            "sequenceDiagram",
            f"    actor User as User",
            f"    participant {page_node} as {file_note}",
            f"    participant {runtime_node} as Streamlit runtime",
            f"    participant {data_node} as PDFs / source files",
            f"    participant {compute_node} as OCR / metadata logic",
            f"    participant {out_node} as Dataset artifacts",
            f"    Note over {page_node}: {relative_note}",
            f"    User->>{page_node}: open page and provide source inputs",
            f"    {page_node}->>{runtime_node}: initialize controls and session state",
            f"    {page_node}->>{compute_node}: validate files, options, and metadata fields",
            f"    {compute_node}->>{data_node}: read document bytes and source content",
            f"    {compute_node}->>{compute_node}: run OCR or metadata enrichment steps",
            f"    {compute_node}->>{out_node}: persist markdown, JSON, images, and catalogs",
            f"    {out_node}-->>{page_node}: return saved paths and processing status",
            f"    {page_node}->>{user_node}: display progress, results, and next actions",
        ]
        summary = "Ingestion and provenance capture."
    elif category == "ground_truth":
        lines = [
            "sequenceDiagram",
            f"    actor User as Annotator / Analyst",
            f"    participant {page_node} as {file_note}",
            f"    participant {runtime_node} as Streamlit runtime",
            f"    participant {data_node} as Ground-truth records",
            f"    participant {compute_node} as Validation / metrics logic",
            f"    participant {out_node} as Audit outputs",
            f"    Note over {page_node}: {relative_note}",
            f"    User->>{page_node}: select records, labels, or audit scope",
            f"    {page_node}->>{runtime_node}: apply widget state and filters",
            f"    {page_node}->>{data_node}: load annotations, runs, and record context",
            f"    {page_node}->>{compute_node}: compute coverage, agreement, metrics, or audit diffs",
            f"    {compute_node}->>{compute_node}: validate labels and trace record lineage",
            f"    {compute_node}->>{out_node}: produce metrics tables, audit views, and summaries",
            f"    {out_node}-->>{page_node}: return derived findings",
            f"    {page_node}->>{user_node}: render validation status and unresolved issues",
        ]
        summary = "Annotation and audit workflow."
    elif category == "llm":
        lines = [
            "sequenceDiagram",
            f"    actor User as Analyst",
            f"    participant {page_node} as {file_note}",
            f"    participant {runtime_node} as Streamlit runtime",
            f"    participant {data_node} as OCR text / run outputs",
            f"    participant {compute_node} as LLM / parser / benchmark logic",
            f"    participant {out_node} as Results and diagnostics",
            f"    Note over {page_node}: {relative_note}",
            f"    User->>{page_node}: choose model, run, prompt, or audit target",
            f"    {page_node}->>{runtime_node}: initialize page state and controls",
            f"    {page_node}->>{data_node}: load OCR text, cached jobs, or parsed outputs",
            f"    {page_node}->>{compute_node}: parse outputs, compare models, or monitor execution",
            f"    alt background or batch run exists",
            f"        {compute_node}->>{out_node}: update job status, diagnostics, and result tables",
            f"    else direct analysis view",
            f"        {compute_node}->>{out_node}: build charts, audits, and comparison summaries",
            f"    end",
            f"    {out_node}-->>{page_node}: return diagnostics and visual artifacts",
            f"    {page_node}->>{user_node}: show model quality, failures, and next steps",
        ]
        summary = "LLM extraction and diagnostics."
    elif category == "thesis":
        lines = [
            "sequenceDiagram",
            f"    actor User as Thesis author",
            f"    participant {page_node} as {file_note}",
            f"    participant {runtime_node} as Streamlit runtime",
            f"    participant {data_node} as Research artifacts",
            f"    participant {compute_node} as Synthesis / chapter logic",
            f"    participant {out_node} as Chapter-ready output",
            f"    Note over {page_node}: {relative_note}",
            f"    User->>{page_node}: open workflow, dashboard, or chapter assembly view",
            f"    {page_node}->>{runtime_node}: initialize layout, tabs, and filters",
            f"    {page_node}->>{data_node}: gather evidence tables, charts, notes, and artifacts",
            f"    {page_node}->>{compute_node}: map findings to claims, sections, or chapter structure",
            f"    {compute_node}->>{compute_node}: consolidate narrative logic and evidence links",
            f"    {compute_node}->>{out_node}: render summaries, Mermaid maps, and chapter-ready guidance",
            f"    {out_node}-->>{page_node}: return composed thesis-facing views",
            f"    {page_node}->>{user_node}: display evidence paths and writing guidance",
        ]
        summary = "Thesis synthesis and navigation."
    else:
        lines = [
            "sequenceDiagram",
            f"    actor User as Analyst",
            f"    participant {page_node} as {file_note}",
            f"    participant {runtime_node} as Streamlit runtime",
            f"    participant {data_node} as Input artifacts",
            f"    participant {compute_node} as Page logic",
            f"    participant {out_node} as Visual output",
            f"    Note over {page_node}: {relative_note}",
            f"    User->>{page_node}: adjust filters and inspect page content",
            f"    {page_node}->>{runtime_node}: initialize widgets and local state",
            f"    {page_node}->>{data_node}: load source artifacts for the current view",
            f"    {page_node}->>{compute_node}: transform, aggregate, and filter data",
            f"    {compute_node}->>{out_node}: generate charts, tables, exports, or maps",
            f"    {out_node}-->>{page_node}: return rendered analytical assets",
            f"    {page_node}->>{user_node}: present results and interpretation cues",
        ]
        summary = "Analysis and visualization flow."

    return "\n".join(lines), summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pages = [p for p in sorted(PAGES_DIR.glob("*.py")) if not p.name.startswith("_")]
    index_lines = [
        "# Mermaid Sequence Diagrams",
        "",
        "One file per active Streamlit page.",
        "",
    ]

    for page_path in pages:
        title = extract_title(page_path)
        category = category_for(page_path.name)
        diagram, summary = diagram_for(page_path, title, category)
        out_path = OUT_DIR / f"{page_path.stem}.md"
        out_path.write_text(
            "\n".join(
                [
                    f"# {title}",
                    "",
                    f"- Filename: `{page_path.name}`",
                    f"- Source path: `{relative_page_path(page_path)}`",
                    f"- Diagram file: `{out_path.relative_to(ROOT)}`",
                    f"- Page slug: `{slug_for(page_path)}`",
                    f"- Category: `{category}`",
                    f"- Purpose: {purpose_for(category)}",
                    f"- Primary inputs: {primary_inputs_for(category)}",
                    f"- Primary outputs: {primary_outputs_for(category)}",
                    f"- Summary: {summary}",
                    "",
                    "## Detailed Sequence",
                    "",
                    "```mermaid",
                    diagram,
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        index_lines.append(f"- [`{page_path.stem}.md`](./{page_path.stem}.md) - {title}")

    (OUT_DIR / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
