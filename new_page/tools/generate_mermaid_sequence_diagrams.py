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


def diagram_for(page_name: str, title: str, category: str) -> tuple[str, str]:
    user_node = "User"
    page_node = "page"
    data_node = "data"
    compute_node = "compute"
    out_node = "output"

    if category == "ingestion":
        lines = [
            "sequenceDiagram",
            f"    actor User as User",
            f"    participant {page_node} as Streamlit page",
            f"    participant {data_node} as PDFs / source files",
            f"    participant {compute_node} as OCR / metadata logic",
            f"    participant {out_node} as Dataset artifacts",
            f"    User->>{page_node}: upload, select, or label inputs",
            f"    {page_node}->>{compute_node}: validate files and derive metadata",
            f"    {compute_node}->>{data_node}: read source document content",
            f"    {compute_node}->>{out_node}: write OCR pages, JSON, images, or catalogs",
            f"    {page_node}->>{user_node}: confirm progress and saved artifacts",
        ]
        summary = "Ingestion and provenance capture."
    elif category == "ground_truth":
        lines = [
            "sequenceDiagram",
            f"    actor User as Annotator / Analyst",
            f"    participant {page_node} as Streamlit page",
            f"    participant {data_node} as Ground-truth records",
            f"    participant {compute_node} as Validation / metrics logic",
            f"    participant {out_node} as Audit outputs",
            f"    User->>{page_node}: review samples, labels, or coverage",
            f"    {page_node}->>{data_node}: load annotations and records",
            f"    {page_node}->>{compute_node}: compute coverage, agreement, or step-by-step checks",
            f"    {compute_node}->>{out_node}: emit metrics, audits, and visual summaries",
            f"    {page_node}->>{user_node}: display validation status and findings",
        ]
        summary = "Annotation and audit workflow."
    elif category == "llm":
        lines = [
            "sequenceDiagram",
            f"    actor User as Analyst",
            f"    participant {page_node} as Streamlit page",
            f"    participant {data_node} as OCR text / run outputs",
            f"    participant {compute_node} as LLM / parser / benchmark logic",
            f"    participant {out_node} as Results and diagnostics",
            f"    User->>{page_node}: inspect runs, errors, or catalogs",
            f"    {page_node}->>{data_node}: fetch prompt/model outputs or cached jobs",
            f"    {page_node}->>{compute_node}: parse, compare, or monitor status",
            f"    {compute_node}->>{out_node}: generate tables, charts, and audit traces",
            f"    {page_node}->>{user_node}: surface model quality and failure modes",
        ]
        summary = "LLM extraction and diagnostics."
    elif category == "thesis":
        lines = [
            "sequenceDiagram",
            f"    actor User as Thesis author",
            f"    participant {page_node} as Streamlit page",
            f"    participant {data_node} as Research artifacts",
            f"    participant {compute_node} as Synthesis / chapter logic",
            f"    participant {out_node} as Chapter-ready output",
            f"    User->>{page_node}: open workflow, dashboard, or chapter page",
            f"    {page_node}->>{data_node}: gather evidence, charts, and notes",
            f"    {page_node}->>{compute_node}: map results to claims or chapter structure",
            f"    {compute_node}->>{out_node}: render summaries, Mermaid maps, or narrative aids",
            f"    {page_node}->>{user_node}: show thesis-facing guidance",
        ]
        summary = "Thesis synthesis and navigation."
    else:
        lines = [
            "sequenceDiagram",
            f"    actor User as Analyst",
            f"    participant {page_node} as Streamlit page",
            f"    participant {data_node} as Input artifacts",
            f"    participant {compute_node} as Page logic",
            f"    participant {out_node} as Visual output",
            f"    User->>{page_node}: interact with controls",
            f"    {page_node}->>{data_node}: load source data",
            f"    {page_node}->>{compute_node}: transform and filter",
            f"    {compute_node}->>{out_node}: render charts, tables, or maps",
            f"    {page_node}->>{user_node}: present results",
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
        diagram, summary = diagram_for(page_path.name, title, category)
        out_path = OUT_DIR / f"{page_path.stem}.md"
        out_path.write_text(
            "\n".join(
                [
                    f"# {title}",
                    "",
                    f"- Source page: `{page_path.name}`",
                    f"- Category: `{category}`",
                    f"- Summary: {summary}",
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
