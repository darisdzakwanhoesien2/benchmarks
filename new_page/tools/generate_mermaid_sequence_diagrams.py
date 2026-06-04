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


def input_filename_examples_for(category: str) -> list[str]:
    mapping = {
        "ingestion": [
            "`<source_report>.pdf`",
            "`<page_image>.png`",
            "`<ocr_request>.json`",
            "`<document_manifest>.csv`",
        ],
        "ground_truth": [
            "`<ground_truth_seed>.csv`",
            "`<annotation_export>.csv`",
            "`<record_audit>.json`",
            "`<benchmark_rows>.jsonl`",
        ],
        "llm": [
            "`<ocr_text>.md`",
            "`<llm_result>.json`",
            "`<background_run>.jsonl`",
            "`<parsed_records>.csv`",
        ],
        "thesis": [
            "`<chapter_notes>.md`",
            "`<evidence_table>.csv`",
            "`<workflow_map>.json`",
            "`<results_snapshot>.xlsx`",
        ],
        "analysis": [
            "`<dataset>.csv`",
            "`<mapping>.json`",
            "`<events>.jsonl`",
            "`<summary_table>.xlsx`",
        ],
    }
    return mapping[category]


def output_filename_examples_for(category: str) -> list[str]:
    mapping = {
        "ingestion": [
            "`<ocr_output>.md`",
            "`<ocr_output>.json`",
            "`<page_preview>.png`",
            "`<catalog_export>.csv`",
        ],
        "ground_truth": [
            "`<coverage_report>.csv`",
            "`<metrics_summary>.json`",
            "`<audit_queue>.csv`",
            "`<annotation_backup>.jsonl`",
        ],
        "llm": [
            "`<parsed_output>.json`",
            "`<diagnostics>.csv`",
            "`<run_status>.jsonl`",
            "`<comparison_export>.xlsx`",
        ],
        "thesis": [
            "`<chapter_summary>.md`",
            "`<figure_export>.png`",
            "`<evidence_matrix>.csv`",
            "`<chapter_bundle>.json`",
        ],
        "analysis": [
            "`<filtered_output>.csv`",
            "`<chart_spec>.json`",
            "`<dashboard_export>.png`",
            "`<summary_export>.xlsx`",
        ],
    }
    return mapping[category]


def filename_guidance_for(category: str) -> list[str]:
    mapping = {
        "ingestion": [
            "Use the original document stem when possible so OCR outputs stay traceable back to the PDF.",
            "Keep page or batch numbers in the filename when one source document produces multiple artifacts.",
        ],
        "ground_truth": [
            "Use filenames that distinguish seed data, human labels, and audit exports so evaluation stages do not get mixed.",
            "Prefer stable suffixes such as `_ground_truth`, `_review_queue`, or `_metrics` for downstream joins.",
        ],
        "llm": [
            "Include model, prompt, or run identifiers when one text source can produce multiple LLM outputs.",
            "Separate raw outputs from parsed outputs in the filename to avoid schema-confusion during audits.",
        ],
        "thesis": [
            "Use filenames that encode chapter or section ownership so exported artifacts stay citation-ready.",
            "Keep evidence snapshots and narrative drafts separate to avoid mixing analytical data with prose outputs.",
        ],
        "analysis": [
            "Prefer filenames that describe both content and grain, for example `record_level`, `page_level`, or `summary`.",
            "If the page accepts multiple formats, reuse the same stem across `CSV`, `JSON`, and `XLSX` variants when they describe the same dataset.",
        ],
    }
    return mapping[category]


def family_heading(category: str) -> str:
    mapping = {
        "ingestion": "Ingestion Pages",
        "ground_truth": "Ground-Truth Pages",
        "llm": "LLM Pages",
        "thesis": "Thesis Pages",
        "analysis": "Analysis Pages",
    }
    return mapping[category]


def family_description(category: str) -> str:
    mapping = {
        "ingestion": "These pages create source-side artifacts such as OCR text, metadata, images, and catalog records.",
        "ground_truth": "These pages validate labeled records, benchmark coverage, disagreements, and audit status.",
        "llm": "These pages run, parse, compare, and monitor model-driven extraction workflows.",
        "thesis": "These pages assemble evidence, narrative structure, and chapter-ready research outputs.",
        "analysis": "These pages inspect prepared datasets, lineage, mappings, dashboards, and analytical summaries.",
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


def combined_diagram() -> str:
    lines = [
        "sequenceDiagram",
        "    actor User as Researcher / Analyst",
        "    participant ingest as Ingestion Pages",
        "    participant analysis as Analysis Pages",
        "    participant gt as Ground-Truth Pages",
        "    participant llm as LLM Pages",
        "    participant thesis as Thesis Pages",
        "    participant artifacts as Shared Artifacts",
        "    Note over ingest,thesis: Combined overview of the active Streamlit page families",
        "    User->>ingest: upload PDFs, metadata, OCR options, and source catalogs",
        "    ingest->>artifacts: create OCR markdown, JSON, images, and catalog entries",
        "    User->>analysis: inspect mappings, lineage, dashboards, and filtered views",
        "    analysis->>artifacts: read CSV / JSON / JSONL / XLSX artifacts",
        "    analysis->>User: show charts, tables, Sankey flows, and export summaries",
        "    User->>gt: review labels, coverage, audits, and record-level validation",
        "    gt->>artifacts: load annotations, benchmark rows, and audit datasets",
        "    gt->>User: return metrics, disagreements, review queues, and record views",
        "    User->>llm: run models, parse outputs, compare prompts, and monitor jobs",
        "    llm->>artifacts: consume OCR text and write parsed outputs plus diagnostics",
        "    llm->>User: expose failures, comparisons, run status, and benchmark results",
        "    User->>thesis: assemble evidence into chapter views and workflow narratives",
        "    thesis->>artifacts: gather charts, notes, metrics, exports, and evidence tables",
        "    thesis->>User: produce chapter-ready summaries, Mermaid maps, and writing guidance",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pages = [p for p in sorted(PAGES_DIR.glob("*.py")) if not p.name.startswith("_")]
    page_metadata: list[tuple[Path, str, str]] = [
        (page_path, extract_title(page_path), category_for(page_path.name))
        for page_path in pages
    ]
    index_lines = [
        "# Mermaid Sequence Diagrams",
        "",
        "One file per active Streamlit page.",
        "",
        "- [`Combined_Streamlit_Workflow.md`](./Combined_Streamlit_Workflow.md) - Combined overview across ingestion, analysis, ground-truth, LLM, and thesis pages",
        "",
    ]

    family_order = ["ingestion", "analysis", "ground_truth", "llm", "thesis"]
    family_sections: list[str] = []
    for category in family_order:
        family_sections.extend(
            [
                f"### {family_heading(category)}",
                "",
                family_description(category),
                "",
            ]
        )
        members = [(page_path, title) for page_path, title, page_category in page_metadata if page_category == category]
        for page_path, title in members:
            family_sections.append(f"- [`{page_path.stem}.md`](./{page_path.stem}.md) - {title}")
        family_sections.append("")

    combined_path = OUT_DIR / "Combined_Streamlit_Workflow.md"
    combined_path.write_text(
        "\n".join(
            [
                "# Combined Streamlit Workflow",
                "",
                "- Scope: All active Streamlit page families",
                "- Diagram file: `documentation/streamlit_pages/mermaid_sequence_diagram/Combined_Streamlit_Workflow.md`",
                "- Purpose: Show the end-to-end relationship between ingestion, analysis, ground-truth, LLM, and thesis pages.",
                "- Shared artifacts: CSV, JSON, JSONL, XLSX, MD, PNG, PDF",
                "",
                "## What This Diagram Shows",
                "",
                "This combined sequence diagram summarizes how the Streamlit pages work together around shared research artifacts.",
                "It is the high-level entry point for the whole folder: use it first, then drill down into the page-level markdown files for the detailed Mermaid sequence of each Streamlit page.",
                "",
                "## Workflow Explanation",
                "",
                "The workflow starts with ingestion pages, which create the source artifacts that the rest of the application depends on.",
                "Those artifacts are then reused by analysis pages, ground-truth pages, and LLM pages depending on whether the researcher is exploring data, validating labels, or running extraction jobs.",
                "The final stage is the thesis layer, where validated outputs, figures, notes, and metrics are assembled into chapter-ready explanations and research evidence.",
                "",
                "In short, the overall flow is:",
                "",
                "`PDF or source document -> OCR or metadata capture -> analytical inspection -> validation or LLM processing -> thesis synthesis`",
                "",
                "## Page Families",
                "",
                *family_sections,
                "",
                "## How To Use It",
                "",
                "1. Start at `Ingestion Pages` if you are documenting document intake, OCR, or source registration.",
                "2. Move to `Analysis Pages`, `Ground-Truth Pages`, or `LLM Pages` depending on the workflow branch you want to explain.",
                "3. End at `Thesis Pages` when you need chapter-ready outputs, evidence synthesis, or narrative summaries.",
                "4. Replace artifact examples with your actual filenames, such as `esg_records.csv`, `ontology_map.json`, or `background_runs.jsonl`.",
                "",
                "## Shared Artifact Types",
                "",
                "- `CSV`: tabular exports such as record tables, metrics, review queues, and summaries",
                "- `JSON`: structured mappings, metadata, parsed records, and configuration-like files",
                "- `JSONL`: run logs, benchmark rows, event streams, and parser diagnostics",
                "- `XLSX`: review workbooks, spreadsheet deliverables, and manually curated tables",
                "- `MD`: OCR text, notes, chapter drafts, and markdown summaries",
                "- `PNG`: charts, screenshots, figure exports, and page previews",
                "- `PDF`: raw reports, source documents, and exported document outputs",
                "",
                "## Combined Sequence",
                "",
                "```mermaid",
                combined_diagram(),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for page_path, title, category in page_metadata:
        diagram, summary = diagram_for(page_path, title, category)
        out_path = OUT_DIR / f"{page_path.stem}.md"
        input_examples = input_filename_examples_for(category)
        output_examples = output_filename_examples_for(category)
        filename_guidance = filename_guidance_for(category)
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
                    "## What This Page Documents",
                    "",
                    f"This file documents the interaction flow for `{page_path.name}` and gives a reusable filename pattern for the artifacts that this page reads or writes.",
                    "",
                    "## Filename Placeholders",
                    "",
                    "Use these placeholders when you want to substitute your own files such as `CSV`, `JSON`, `JSONL`, `XLSX`, `PNG`, or `PDF` assets.",
                    "",
                    f"- Input examples: {', '.join(input_examples)}",
                    f"- Output examples: {', '.join(output_examples)}",
                    "",
                    "Recommended placeholder format:",
                    "",
                    "- `<name>.csv` for tabular inputs or exports",
                    "- `<name>.json` for structured objects or config-like artifacts",
                    "- `<name>.jsonl` for line-by-line run logs or benchmark rows",
                    "- `<name>.xlsx` for spreadsheet deliverables",
                    "- `<name>.md` for OCR text or narrative output",
                    "- `<name>.png` for figure snapshots or image intermediates",
                    "- `<name>.pdf` for source documents",
                    "",
                    "## Naming Guidance",
                    "",
                    f"- {filename_guidance[0]}",
                    f"- {filename_guidance[1]}",
                    "",
                    "## Customization Steps",
                    "",
                    "1. Choose the file stem that matches your dataset or experiment, for example `esg_records`, `ontology_map`, or `ground_truth_seed`.",
                    "2. Keep the extension aligned with the artifact type, for example `CSV` for tables and `JSON` for nested structures.",
                    "3. If multiple runs exist, append a stable suffix such as `_v2`, `_2026_06`, `_prompt_3`, or `_model_a`.",
                    "4. Update this page documentation if the real source path, output path, or artifact role changes.",
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
