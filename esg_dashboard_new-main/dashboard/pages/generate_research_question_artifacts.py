from __future__ import annotations

import ast
import json
import math
import textwrap
from datetime import datetime
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PAGE_DIR = Path(__file__).resolve().parent
SOURCE_PAGE = PAGE_DIR / "04_Research_Questions_Visualizer.py"
ARTIFACT_DIR = PAGE_DIR / "research_question_artifacts"
IMAGE_DIR = ARTIFACT_DIR / "images"
MERMAID_DIR = ARTIFACT_DIR / "mermaid"
JSON_PATH = ARTIFACT_DIR / "research_question_artifacts.json"
MARKDOWN_PATH = ARTIFACT_DIR / "research_question_artifacts.md"

EXISTING_DATA_PATH = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/data_output.txt"
PREDICTION_OUTPUT_DIR = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/climatebert_predictions"

COLORS = {
    "ink": "#273043",
    "muted": "#6b7280",
    "grid": "#d9dee7",
    "panel": "#f8fafc",
    "available": "#22c55e",
    "partial": "#f59e0b",
    "needed": "#ef4444",
    "blue": "#2563eb",
    "teal": "#0f766e",
    "purple": "#7c3aed",
    "gray": "#64748b",
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = load_font(34, bold=True)
FONT_SUBTITLE = load_font(19)
FONT_LABEL = load_font(18, bold=True)
FONT_TEXT = load_font(16)
FONT_SMALL = load_font(13)
FONT_TINY = load_font(11)


def extract_rq_data() -> list[dict]:
    tree = ast.parse(SOURCE_PAGE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RQ_DATA":
                    return ast.literal_eval(node.value)
    raise RuntimeError("RQ_DATA was not found in 04_Research_Questions_Visualizer.py")


def status_frame(rq_data: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rq": row["rq"],
                "theme": row["theme"],
                "available": len(row["have"]),
                "partial": len(row["partial"]),
                "needed": len(row["need"]),
                "priority": row["priority"],
            }
            for row in rq_data
        ]
    )


def wrap_lines(text: str, width: int) -> list[str]:
    return textwrap.wrap(str(text), width=width, break_long_words=False) or [""]


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    width: int,
    line_gap: int = 5,
) -> int:
    x, y = xy
    for line in wrap_lines(text, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap if hasattr(font, "size") else 18
    return y


def new_canvas(width: int, height: int, title: str, subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 96), fill="#f8fafc")
    draw.text((44, 26), title, font=FONT_TITLE, fill=COLORS["ink"])
    if subtitle:
        draw.text((46, 68), subtitle, font=FONT_SUBTITLE, fill=COLORS["muted"])
    return img, draw


def save_image(img: Image.Image, filename: str) -> str:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGE_DIR / filename
    img.save(path)
    return str(path.relative_to(ARTIFACT_DIR))


def draw_stacked_bar(df: pd.DataFrame) -> dict:
    img, draw = new_canvas(
        1500,
        860,
        "Evidence Readiness by Research Question",
        "Available, partial, and needed evidence items from the RQ details table.",
    )
    left, top, bar_w, bar_h, gap = 230, 165, 980, 48, 52
    max_total = max((df[["available", "partial", "needed"]].sum(axis=1)).max(), 1)
    statuses = [("available", "Available"), ("partial", "Partial"), ("needed", "Needed")]

    for i, row in df.iterrows():
        y = top + i * (bar_h + gap)
        draw.text((55, y + 3), f"{row.rq}", font=FONT_LABEL, fill=COLORS["ink"])
        draw.text((105, y + 5), row.theme, font=FONT_TEXT, fill=COLORS["muted"])
        x = left
        total = int(row.available + row.partial + row.needed)
        for key, _ in statuses:
            value = int(row[key])
            segment_w = round(bar_w * value / max_total)
            if value:
                draw.rounded_rectangle((x, y, x + segment_w, y + bar_h), radius=8, fill=COLORS[key])
                draw.text((x + 10, y + 13), str(value), font=FONT_TEXT, fill="white")
            x += segment_w
        draw.text((left + bar_w + 30, y + 12), f"{total} items", font=FONT_TEXT, fill=COLORS["ink"])

    legend_x = 55
    for key, label in statuses:
        draw.rounded_rectangle((legend_x, 780, legend_x + 28, 808), radius=6, fill=COLORS[key])
        draw.text((legend_x + 38, 782), label, font=FONT_TEXT, fill=COLORS["ink"])
        legend_x += 180

    return {
        "id": "evidence_readiness_by_rq",
        "path": save_image(img, "evidence_readiness_by_rq.png"),
        "title": "Evidence Readiness by Research Question",
        "what_it_shows": "A stacked count of available, partial, and needed evidence for each research question.",
        "expected_metrics": "Each RQ should move toward more Available items and fewer Needed/Partial items before the thesis makes strong claims.",
        "interpretation": "RQ2 and RQ3 are critical because their missing validation and ClimateBERT comparison work directly determine whether the ABSA results are defensible.",
        "if_underperforming": "If a row remains dominated by Needed or Partial evidence, the RQ should be presented as preliminary or narrowed until the missing metric is computed.",
    }


def draw_status_totals(df: pd.DataFrame) -> dict:
    totals = df[["available", "partial", "needed"]].sum()
    img, draw = new_canvas(
        1200,
        720,
        "Overall Evidence Status Totals",
        "Project-level readiness across all thesis research questions.",
    )
    x, y, max_w = 120, 185, 850
    max_value = int(totals.max())
    for key, label in [("available", "Available"), ("partial", "Partial"), ("needed", "Needed")]:
        value = int(totals[key])
        width = int(max_w * value / max_value)
        draw.text((x, y + 9), label, font=FONT_LABEL, fill=COLORS["ink"])
        draw.rounded_rectangle((x + 170, y, x + 170 + width, y + 48), radius=8, fill=COLORS[key])
        draw.text((x + 180 + width, y + 12), f" {value}", font=FONT_LABEL, fill=COLORS["ink"])
        y += 95

    note = (
        "Available evidence can be visualized and interpreted now. Partial evidence needs validation or coverage checks. "
        "Needed evidence is work that should link to a completion page or process."
    )
    draw_wrapped(draw, (120, 540), note, FONT_TEXT, COLORS["muted"], 108)
    return {
        "id": "overall_evidence_status_totals",
        "path": save_image(img, "overall_evidence_status_totals.png"),
        "title": "Overall Evidence Status Totals",
        "what_it_shows": "The total count of evidence rows by status across the whole RQ evidence matrix.",
        "expected_metrics": "A mature thesis evidence set should have most rows Available, with only low-priority items remaining Partial or Needed.",
        "interpretation": "This chart is a readiness check, not a statistical test. It tells you how much of the evidence pipeline has been completed.",
        "if_underperforming": "Large Partial/Needed counts mean the dashboard should redirect users to processing, annotation, or validation workflows.",
    }


def draw_priority_matrix(df: pd.DataFrame) -> dict:
    img, draw = new_canvas(
        1500,
        900,
        "RQ Priority and Evidence Gap Matrix",
        "Combines evidence status counts with thesis priority.",
    )
    headers = ["RQ", "Theme", "Priority", "Available", "Partial", "Needed", "Risk Signal"]
    widths = [105, 210, 150, 150, 130, 130, 560]
    x0, y0, row_h = 50, 150, 90
    x = x0
    for header, width in zip(headers, widths):
        draw.rectangle((x, y0, x + width, y0 + 48), fill="#eef2f7", outline=COLORS["grid"])
        draw.text((x + 12, y0 + 14), header, font=FONT_TEXT, fill=COLORS["ink"])
        x += width

    for i, row in df.iterrows():
        y = y0 + 48 + i * row_h
        needed = int(row.needed)
        partial = int(row.partial)
        risk = "Strong base; mostly interpretation work."
        if row.priority in {"Critical", "High"} and needed:
            risk = "High thesis risk until missing metrics are completed."
        elif partial:
            risk = "Promising evidence, but validation/coverage remains incomplete."
        cells = [row.rq, row.theme, row.priority, row.available, row.partial, row.needed, risk]
        x = x0
        for value, width in zip(cells, widths):
            fill = "white" if i % 2 == 0 else "#fbfdff"
            draw.rectangle((x, y, x + width, y + row_h), fill=fill, outline=COLORS["grid"])
            if width > 250:
                draw_wrapped(draw, (x + 12, y + 16), str(value), FONT_SMALL, COLORS["ink"], 66)
            else:
                draw.text((x + 12, y + 30), str(value), font=FONT_TEXT, fill=COLORS["ink"])
            x += width

    return {
        "id": "rq_priority_gap_matrix",
        "path": save_image(img, "rq_priority_gap_matrix.png"),
        "title": "RQ Priority and Evidence Gap Matrix",
        "what_it_shows": "A compact table image linking RQ priority to the amount of available, partial, and needed evidence.",
        "expected_metrics": "Critical and High RQs should have direct metrics, traceable sources, and low unclosed Needed counts.",
        "interpretation": "The most important risk is not simply the number of gaps; it is whether a gap belongs to a Critical RQ.",
        "if_underperforming": "If a Critical RQ has Needed rows, the page should route the user to the processor, result visualizer, annotation plan, or parsed-data page.",
    }


def draw_sample_ladder() -> dict:
    rows = [
        ("Minimum pilot annotation", 30, "Use only for early feasibility checks"),
        ("Defensible manual validation", 50, "Better for Cohen kappa and error taxonomy"),
        ("Subgroup comparison floor", 100, "Needed for language/pillar split checks"),
        ("Current Arcee valid rows", 272, "Enough for descriptive charts, still watch subgroup balance"),
        ("Larger thesis target", 500, "More stable for per-model/prompt comparisons"),
        ("Robust subgroup target", 1000, "Supports narrower slices with less variance"),
    ]
    img, draw = new_canvas(
        1400,
        840,
        "Sample Size Reasoning Ladder",
        "How row counts change the defensibility of analysis claims.",
    )
    left, top, max_w = 360, 160, 820
    max_n = max(n for _, n, _ in rows)
    for i, (label, n, note) in enumerate(rows):
        y = top + i * 92
        w = int(max_w * n / max_n)
        draw.text((65, y + 8), label, font=FONT_LABEL, fill=COLORS["ink"])
        draw.rounded_rectangle((left, y, left + w, y + 38), radius=8, fill=COLORS["blue"])
        draw.text((left + w + 16, y + 7), f"n={n}", font=FONT_LABEL, fill=COLORS["ink"])
        draw_wrapped(draw, (left, y + 45), note, FONT_SMALL, COLORS["muted"], 88)
    return {
        "id": "sample_size_reasoning_ladder",
        "path": save_image(img, "sample_size_reasoning_ladder.png"),
        "title": "Sample Size Reasoning Ladder",
        "what_it_shows": "A practical ladder of sample sizes and what each size can support in the thesis.",
        "expected_metrics": "Manual validation usually needs at least 30-50 records; subgroup comparisons need substantially more balanced rows.",
        "interpretation": "Current row counts can support descriptive analysis, but smaller slices by language, pillar, prompt, or model may still be fragile.",
        "if_underperforming": "If a subgroup has too few rows, report it as exploratory and avoid strong comparative claims.",
    }


def draw_margin_of_error() -> dict:
    img, draw = new_canvas(
        1400,
        820,
        "Approximate Margin of Error by Sample Size",
        "95% worst-case proportion margin of error, useful for tone/category rates.",
    )
    plot = (120, 150, 1260, 660)
    x0, y0, x1, y1 = plot
    draw.rectangle(plot, outline=COLORS["grid"], width=2)
    for pct in [0.05, 0.10, 0.15, 0.20]:
        y = y1 - int((pct - 0.03) / (0.20 - 0.03) * (y1 - y0))
        draw.line((x0, y, x1, y), fill=COLORS["grid"])
        draw.text((58, y - 9), f"{pct:.0%}", font=FONT_SMALL, fill=COLORS["muted"])
    points = []
    for n in range(30, 1001, 10):
        moe = 1.96 * math.sqrt(0.25 / n)
        x = x0 + int((n - 30) / (1000 - 30) * (x1 - x0))
        y = y1 - int((moe - 0.03) / (0.20 - 0.03) * (y1 - y0))
        points.append((x, y))
    draw.line(points, fill=COLORS["teal"], width=5)
    for n in [50, 100, 272, 500, 1000]:
        moe = 1.96 * math.sqrt(0.25 / n)
        x = x0 + int((n - 30) / (1000 - 30) * (x1 - x0))
        y = y1 - int((moe - 0.03) / (0.20 - 0.03) * (y1 - y0))
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=COLORS["needed"] if n < 100 else COLORS["blue"])
        draw.text((x + 10, y - 24), f"n={n}, +/-{moe:.1%}", font=FONT_SMALL, fill=COLORS["ink"])
    draw.text((640, 704), "Sample size", font=FONT_TEXT, fill=COLORS["ink"])
    draw.text((36, 126), "MOE", font=FONT_TEXT, fill=COLORS["ink"])
    return {
        "id": "margin_of_error_by_sample_size",
        "path": save_image(img, "margin_of_error_by_sample_size.png"),
        "title": "Approximate Margin of Error by Sample Size",
        "what_it_shows": "How uncertainty shrinks as the number of validated rows grows.",
        "expected_metrics": "For proportion estimates such as tone rate, more rows reduce uncertainty; n=272 gives roughly +/-5.9 percentage points in the worst case.",
        "interpretation": "The thesis can report descriptive proportions, but subgroup results need enough rows per subgroup, not just a large total row count.",
        "if_underperforming": "If a subgroup is below n=30-50, use it for qualitative diagnostics rather than quantitative claims.",
    }


def draw_subgroup_requirements() -> dict:
    rows = [
        ("Manual gold sample", 50),
        ("Language split", 2 * 50),
        ("E/G/S pillar split", 3 * 50),
        ("Model x prompt slice", 6 * 50),
        ("Current Arcee valid rows", 272),
    ]
    img, draw = new_canvas(
        1400,
        760,
        "Subgroup Coverage Requirement Check",
        "Why balanced analysis needs more than a large headline row count.",
    )
    left, top, max_w = 420, 170, 760
    max_n = max(n for _, n in rows)
    for i, (label, n) in enumerate(rows):
        y = top + i * 90
        color = COLORS["available"] if label == "Current Arcee valid rows" else COLORS["purple"]
        w = int(max_w * n / max_n)
        draw.text((70, y + 8), label, font=FONT_LABEL, fill=COLORS["ink"])
        draw.rounded_rectangle((left, y, left + w, y + 42), radius=8, fill=color)
        draw.text((left + w + 16, y + 9), str(n), font=FONT_LABEL, fill=COLORS["ink"])
    draw_wrapped(
        draw,
        (70, 640),
        "Interpretation: 272 total rows can look large, but a model x prompt x language split can still leave small cells. Balance matters more than the total when comparing categories.",
        FONT_TEXT,
        COLORS["muted"],
        120,
    )
    return {
        "id": "subgroup_coverage_requirement_check",
        "path": save_image(img, "subgroup_coverage_requirement_check.png"),
        "title": "Subgroup Coverage Requirement Check",
        "what_it_shows": "The row counts needed when validation is split by language, pillar, model, or prompt.",
        "expected_metrics": "A useful target is 30-50 validated rows per important subgroup.",
        "interpretation": "This chart explains why some RQ evidence remains Partial even when the dataset already has many rows.",
        "if_underperforming": "If important cells are sparse, add data or collapse categories before claiming subgroup differences.",
    }


def draw_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str, color: str) -> None:
    draw.rounded_rectangle(box, radius=10, fill="#ffffff", outline=color, width=3)
    x0, y0, x1, _ = box
    draw_wrapped(draw, (x0 + 14, y0 + 15), label, FONT_TEXT, COLORS["ink"], max(18, (x1 - x0) // 9))


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = "#64748b") -> None:
    draw.line((start, end), fill=color, width=3)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    for offset in (2.6, -2.6):
        p = (end[0] - 14 * math.cos(angle + offset), end[1] - 14 * math.sin(angle + offset))
        draw.line((end, p), fill=color, width=3)


def draw_workflow_diagram() -> dict:
    img, draw = new_canvas(
        1600,
        900,
        "Workflow Diagram",
        "End-to-end path from sustainability reports to RQ evidence.",
    )
    nodes = [
        ("PDF reports", (70, 180, 260, 260), COLORS["blue"]),
        ("OCR markdown", (330, 180, 540, 260), COLORS["blue"]),
        ("LLM JSON extraction", (610, 180, 850, 260), COLORS["teal"]),
        ("data_output.txt", (920, 180, 1150, 260), COLORS["available"]),
        ("Parsed ESG records", (1230, 180, 1510, 260), COLORS["available"]),
        ("ClimateBERT processor page 02", (360, 430, 640, 520), COLORS["purple"]),
        ("Prediction CSV shards", (720, 430, 980, 520), COLORS["purple"]),
        ("Result visualizer page 03", (1060, 430, 1320, 520), COLORS["purple"]),
        ("RQ evidence page 04", (720, 650, 980, 740), COLORS["needed"]),
    ]
    for label, box, color in nodes:
        draw_box(draw, box, label, color)
    arrows = [
        ((260, 220), (330, 220)),
        ((540, 220), (610, 220)),
        ((850, 220), (920, 220)),
        ((1150, 220), (1230, 220)),
        ((1370, 260), (500, 430)),
        ((640, 475), (720, 475)),
        ((980, 475), (1060, 475)),
        ((850, 520), (850, 650)),
        ((1370, 260), (980, 650)),
    ]
    for start, end in arrows:
        draw_arrow(draw, start, end)
    return {
        "id": "workflow_diagram",
        "path": save_image(img, "workflow_diagram.png"),
        "title": "Workflow Diagram",
        "what_it_shows": "The operational pipeline connecting source reports, parsed records, ClimateBERT processing, prediction outputs, and the RQ evidence page.",
        "expected_metrics": "Every output should be traceable back to data_output.txt or climatebert_predictions, with page-level or row-level provenance where possible.",
        "interpretation": "The dashboard should treat page 02 as the production step, page 03 as the prediction review step, and page 04 as the thesis-evidence interpretation layer.",
        "if_underperforming": "If any handoff is missing, the downstream chart may still render but it will be hard to audit or continue after interruption.",
    }


def draw_missing_process_diagram() -> dict:
    img, draw = new_canvas(
        1600,
        900,
        "Missing Evidence Process",
        "How Needed and Partial evidence rows become completed thesis metrics.",
    )
    nodes = [
        ("Missing or partial RQ evidence", (70, 190, 320, 280), COLORS["needed"]),
        ("Identify the missing metric", (390, 190, 650, 280), COLORS["teal"]),
        ("Choose source: data_output or predictions", (720, 190, 1020, 280), COLORS["blue"]),
        ("Create targeted sample", (1090, 190, 1360, 280), COLORS["blue"]),
        ("Run analysis or annotation", (250, 460, 540, 550), COLORS["purple"]),
        ("Compute metric", (620, 460, 850, 550), COLORS["purple"]),
        ("Update RQ table and report", (930, 460, 1230, 550), COLORS["available"]),
        ("Redirect targets: page 02, page 03, Parsed ESG JSON, Sample Size Reasoning", (430, 680, 1160, 760), COLORS["gray"]),
    ]
    for label, box, color in nodes:
        draw_box(draw, box, label, color)
    arrows = [
        ((320, 235), (390, 235)),
        ((650, 235), (720, 235)),
        ((1020, 235), (1090, 235)),
        ((1225, 280), (395, 460)),
        ((540, 505), (620, 505)),
        ((850, 505), (930, 505)),
        ((1080, 550), (795, 680)),
    ]
    for start, end in arrows:
        draw_arrow(draw, start, end)
    return {
        "id": "missing_evidence_process",
        "path": save_image(img, "missing_evidence_process.png"),
        "title": "Missing Evidence Process",
        "what_it_shows": "The completion workflow for rows marked Needed or Partial in the RQ details table.",
        "expected_metrics": "Each missing item should name a source, a process, and a metric that can be computed and added back to the evidence table.",
        "interpretation": "Needed rows are not errors. They are explicit thesis work items with a destination page and completion metric.",
        "if_underperforming": "If a Needed row has no route or metric, it should be rewritten until the next action is executable.",
    }


def draw_full_rq_map(df: pd.DataFrame) -> dict:
    img, draw = new_canvas(
        1700,
        980,
        "Full Research Question Evidence Map",
        "Source-to-RQ links plus evidence status counts.",
    )
    sources = [
        ("data_output.txt", (90, 150, 360, 230), COLORS["blue"]),
        ("climatebert_predictions", (490, 150, 810, 230), COLORS["purple"]),
        ("expert annotation", (940, 150, 1220, 230), COLORS["needed"]),
        ("artifact registry", (1350, 150, 1600, 230), COLORS["teal"]),
    ]
    for label, box, color in sources:
        draw_box(draw, box, label, color)
    positions = {
        "RQ1": (80, 410, 310, 505),
        "RQ2": (360, 410, 590, 505),
        "RQ3": (640, 410, 870, 505),
        "RQ4": (920, 410, 1150, 505),
        "RQ5": (1200, 410, 1430, 505),
        "RQ6": (680, 650, 930, 745),
    }
    for _, row in df.iterrows():
        counts = f"A:{row.available} P:{row.partial} N:{row.needed}"
        draw_box(draw, positions[row.rq], f"{row.rq} {row.theme}\n{counts}", COLORS["gray"])
    links = [
        ((225, 230), (195, 410)),
        ((225, 230), (475, 410)),
        ((650, 230), (755, 410)),
        ((225, 230), (1035, 410)),
        ((650, 230), (1315, 410)),
        ((225, 230), (805, 650)),
        ((1080, 230), (475, 410)),
        ((1080, 230), (1035, 410)),
        ((1475, 230), (1315, 410)),
        ((755, 505), (805, 650)),
    ]
    for start, end in links:
        draw_arrow(draw, start, end)
    return {
        "id": "full_research_question_evidence_map",
        "path": save_image(img, "full_research_question_evidence_map.png"),
        "title": "Full Research Question Evidence Map",
        "what_it_shows": "A high-level lineage map from source artifacts to the six research questions.",
        "expected_metrics": "Each RQ should be linked to the data source that supports it and the status counts that indicate readiness.",
        "interpretation": "RQ3 depends most directly on prediction outputs, while RQ2 and RQ4 also need expert annotation to become fully defensible.",
        "if_underperforming": "If a source-to-RQ link is weak or missing, the RQ should not be presented as fully supported yet.",
    }


def write_mermaid_files(df: pd.DataFrame) -> list[dict]:
    MERMAID_DIR.mkdir(parents=True, exist_ok=True)
    diagrams = {
        "workflow_diagram.mmd": """flowchart LR
  PDF["PDF reports"] --> OCR["OCR markdown"]
  OCR --> LLM["LLM JSON extraction"]
  LLM --> DATA["data_output.txt"]
  DATA --> PARSED["Parsed ESG records"]
  PARSED --> RUN["ClimateBERT processor page 02"]
  RUN --> PRED["Prediction CSV shards"]
  PRED --> VIZ["Result visualizer page 03"]
  PARSED --> RQ["RQ evidence page 04"]
  PRED --> RQ
""",
        "missing_evidence_process.mmd": """flowchart LR
  GAP["Missing or partial evidence"] --> IDENTIFY["Identify metric"]
  IDENTIFY --> SOURCE["Choose source"]
  SOURCE --> SAMPLE["Create targeted sample"]
  SAMPLE --> RUN["Run analysis or annotation"]
  RUN --> METRIC["Compute metric"]
  METRIC --> UPDATE["Update RQ table"]
""",
    }
    lines = [
        "flowchart TB",
        '  DATA["data_output.txt"]',
        '  PRED["climatebert_predictions"]',
        '  GOLD["expert annotation"]',
        '  AUDIT["artifact registry"]',
    ]
    for _, row in df.iterrows():
        lines.append(f'  {row.rq}["{row.rq} {row.theme}: A{row.available} P{row.partial} N{row.needed}"]')
    lines.extend(
        [
            "  DATA --> RQ1",
            "  DATA --> RQ2",
            "  PRED --> RQ3",
            "  DATA --> RQ4",
            "  AUDIT --> RQ5",
            "  DATA --> RQ6",
            "  GOLD --> RQ2",
            "  GOLD --> RQ4",
            "  RQ3 --> RQ6",
        ]
    )
    diagrams["full_research_question_evidence_map.mmd"] = "\n".join(lines) + "\n"

    outputs = []
    for filename, code in diagrams.items():
        path = MERMAID_DIR / filename
        path.write_text(code, encoding="utf-8")
        outputs.append(
            {
                "id": filename.removesuffix(".mmd"),
                "path": str(path.relative_to(ARTIFACT_DIR)),
                "title": filename.removesuffix(".mmd").replace("_", " ").title(),
                "description": "Mermaid source for the corresponding dashboard diagram.",
            }
        )
    return outputs


def build_rq_explanations(rq_data: list[dict]) -> list[dict]:
    explanations = []
    for row in rq_data:
        available = len(row["have"])
        partial = len(row["partial"])
        needed = len(row["need"])
        if row["rq"] == "RQ1":
            interp = "Pipeline evidence is strong for parsing and traceability, but OCR and sentence-boundary quality still need direct measurement."
        elif row["rq"] == "RQ2":
            interp = "Categorization has useful descriptive distributions, but gold labels and inter-annotator agreement are required before treating labels as validated ABSA."
        elif row["rq"] == "RQ3":
            interp = "ClimateBERT comparison becomes defensible only when local model prediction CSVs cover all valid records and can be joined back to the parsed dataset."
        elif row["rq"] == "RQ4":
            interp = "Diagnostics are already useful for identifying schema drift and missing tone, but manual error labels are needed for a formal error taxonomy."
        elif row["rq"] == "RQ5":
            interp = "Reproducibility has several artifacts in place; the remaining work is a formal rerun checklist and independent replication log."
        else:
            interp = "Stability analysis shows prompt sensitivity; balanced model x prompt x document coverage is needed before ensemble claims are strong."
        explanations.append(
            {
                "rq": row["rq"],
                "theme": row["theme"],
                "question": row["question"],
                "priority": row["priority"],
                "status_counts": {
                    "available": available,
                    "partial": partial,
                    "needed": needed,
                },
                "available_evidence": row["have"],
                "partial_evidence": row["partial"],
                "needed_evidence": row["need"],
                "metrics": [
                    {"metric": metric, "value": value, "note": note}
                    for metric, value, note in row["metrics"]
                ],
                "interpretation": interp,
                "redirect_guidance": {
                    "available": "Visualize and cite with source traceability.",
                    "partial": "Open the linked page, compute the missing validation/coverage metric, then upgrade the row.",
                    "needed": "Treat as an executable task and route to processing, annotation, parsed data, or sample-size reasoning.",
                },
            }
        )
    return explanations


def write_json_report(image_entries: list[dict], mermaid_entries: list[dict], rq_explanations: list[dict]) -> None:
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_files": {
            "research_questions_page": str(SOURCE_PAGE),
            "existing_data": EXISTING_DATA_PATH,
            "prediction_outputs": PREDICTION_OUTPUT_DIR,
        },
        "images": image_entries,
        "mermaid_sources": mermaid_entries,
        "research_question_explanations": rq_explanations,
        "usage_notes": [
            "Use Available rows as current evidence only when the source path and denominator are clear.",
            "Use Partial rows as promising but not fully defensible evidence.",
            "Use Needed rows as direct completion tasks routed back into the dashboard workflow.",
        ],
    }
    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_markdown_report(image_entries: list[dict], mermaid_entries: list[dict], rq_explanations: list[dict]) -> None:
    lines = [
        "# Research Question Artifact Export",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Sources",
        "",
        f"- Existing data: `{EXISTING_DATA_PATH}`",
        f"- Prediction outputs: `{PREDICTION_OUTPUT_DIR}`",
        f"- Streamlit RQ page: `{SOURCE_PAGE}`",
        "",
        "## Image Outputs and Explanations",
        "",
    ]
    for entry in image_entries:
        lines.extend(
            [
                f"### {entry['title']}",
                "",
                f"![{entry['title']}]({entry['path']})",
                "",
                f"**What it shows:** {entry['what_it_shows']}",
                "",
                f"**Expected metrics:** {entry['expected_metrics']}",
                "",
                f"**Interpretation:** {entry['interpretation']}",
                "",
                f"**If underperforming:** {entry['if_underperforming']}",
                "",
            ]
        )

    lines.extend(["## Research Question Details", ""])
    for rq in rq_explanations:
        lines.extend(
            [
                f"### {rq['rq']} - {rq['theme']}",
                "",
                rq["question"],
                "",
                f"Priority: **{rq['priority']}**",
                "",
                (
                    "Status counts: "
                    f"Available={rq['status_counts']['available']}, "
                    f"Partial={rq['status_counts']['partial']}, "
                    f"Needed={rq['status_counts']['needed']}."
                ),
                "",
                f"Interpretation: {rq['interpretation']}",
                "",
                "Key metrics:",
                "",
            ]
        )
        for metric in rq["metrics"]:
            lines.append(f"- `{metric['metric']}`: {metric['value']} ({metric['note']})")
        lines.extend(["", "Needed/partial completion logic:", ""])
        lines.append("- Available: visualize and cite with traceability.")
        lines.append("- Partial: compute the missing validation or coverage metric before strong claims.")
        lines.append("- Needed: redirect to the relevant dashboard/process page and complete the metric.")
        lines.append("")

    lines.extend(["## Mermaid Sources", ""])
    for entry in mermaid_entries:
        lines.append(f"- [{entry['title']}]({entry['path']}): {entry['description']}")
    lines.append("")
    MARKDOWN_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    MERMAID_DIR.mkdir(parents=True, exist_ok=True)

    rq_data = extract_rq_data()
    df = status_frame(rq_data)
    image_entries = [
        draw_stacked_bar(df),
        draw_status_totals(df),
        draw_priority_matrix(df),
        draw_sample_ladder(),
        draw_margin_of_error(),
        draw_subgroup_requirements(),
        draw_workflow_diagram(),
        draw_missing_process_diagram(),
        draw_full_rq_map(df),
    ]
    mermaid_entries = write_mermaid_files(df)
    rq_explanations = build_rq_explanations(rq_data)
    write_json_report(image_entries, mermaid_entries, rq_explanations)
    write_markdown_report(image_entries, mermaid_entries, rq_explanations)

    print(f"Saved {len(image_entries)} PNG images")
    print(f"Saved JSON: {JSON_PATH}")
    print(f"Saved Markdown: {MARKDOWN_PATH}")


if __name__ == "__main__":
    main()
