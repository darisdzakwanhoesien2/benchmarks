from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


BENCHMARKS_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCHMARKS_ROOT / "new_page"
DASHBOARD_DIR = BENCHMARKS_ROOT / "esg_dashboard_new-main" / "dashboard"
DASHBOARD_DATA_DIR = DASHBOARD_DIR / "data" / "data"
DASHBOARD_ONTOLOGY_DIR = DASHBOARD_DIR / "data"
SOURCE_DOCX = BENCHMARKS_ROOT / "pages" / "thesis_ch4_6_structure_benchmarks.docx"
UPDATED_DOCX = BENCHMARKS_ROOT / "pages" / "thesis_ch4_6_structure_benchmarks_streamlit_graphs.docx"
GRAPH_DIR = ROOT / "results" / "docx_graph_attachments"
VIS = ROOT / "results" / "visualizations"
TOOLS = ROOT / "tools"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REV = ROOT / "results" / "revision_analysis"
WORKFLOW = ROOT / "results" / "thesis_workflow_dashboard"

sys.path.insert(0, str(ROOT / "code"))
sys.path.insert(0, str(TOOLS))

from thesis_chapter_streamlit import (  # noqa: E402
    agreement_chart,
    artifact_chart,
    count_chart,
    data_bundle,
    heatmap_from_table,
    metric_row,
    model_stability_chart,
    ontology_chart,
    prompt_stability_chart,
    workflow_coverage_chart,
)


st.set_page_config(page_title="Ch4-6 Benchmarks + DOCX Graphs", layout="wide")


def _load_dashboard_data_loader():
    module_path = DASHBOARD_DIR / "utils" / "data_loader.py"
    spec = importlib.util.spec_from_file_location("dashboard_page_data_loader", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load dashboard data loader from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_dashboard_loader = _load_dashboard_data_loader()
format_display_value = _dashboard_loader.format_display_value
load_and_parse = _dashboard_loader.load_and_parse
read_dashboard_dataset = _dashboard_loader.read_dataset
resolve_dashboard_data_path = _dashboard_loader.resolve_data_path


def _load_ontology(name: str) -> dict[str, Any]:
    path = DASHBOARD_ONTOLOGY_DIR / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _ontology_alias_map(ontology: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for key, meta in ontology.items():
        label = meta.get("label", key) if isinstance(meta, dict) else key
        values = [key, label]
        if isinstance(meta, dict):
            values.extend(meta.get("aliases", []))
        for value in values:
            if value is not None:
                mapping[str(value).strip().lower()] = str(label).strip()
    return mapping


TONE_MAP = _ontology_alias_map(_load_ontology("tone_ontology.json"))
SENTIMENT_MAP = _ontology_alias_map(_load_ontology("sentiment_ontology.json"))
ASPECT_CATEGORY_MAP = _ontology_alias_map(_load_ontology("aspect_category_ontology.json"))
HEAVY_SOURCE_COLUMNS = {"text", "markdown_full", "cleaned_markdown", "original", "pa"}


def read_docx_paragraphs(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame([{"paragraph": 0, "text": f"Missing DOCX: {path}", "section": "missing"}])
    try:
        with ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
    except Exception as exc:
        return pd.DataFrame([{"paragraph": 0, "text": f"Could not read DOCX: {exc}", "section": "error"}])

    rows = []
    current = "Front matter"
    for idx, para in enumerate(root.findall(f".//{W_NS}p"), start=1):
        text = "".join(t.text or "" for t in para.findall(f".//{W_NS}t")).strip()
        if not text:
            continue
        if (
            text.startswith(("IV.", "V.", "VI.", "A."))
            or text.startswith(("4.", "5.", "6."))
            or "Appendix" in text
        ):
            current = text
        rows.append({"paragraph": idx, "section": current, "text": text})
    return pd.DataFrame(rows)


def media_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with ZipFile(path) as zf:
            return len([name for name in zf.namelist() if name.startswith("word/media/")])
    except Exception:
        return 0


def chart_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_label(draw: ImageDraw.ImageDraw, text: str, max_width: int, font: ImageFont.ImageFont) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_docx_bar_chart(path: Path, title: str, rows: pd.DataFrame, label_col: str, value_col: str, subtitle: str = "") -> None:
    if rows.empty or label_col not in rows.columns or value_col not in rows.columns:
        return
    plot = rows[[label_col, value_col]].copy()
    plot[value_col] = pd.to_numeric(plot[value_col], errors="coerce").fillna(0)
    plot = plot.sort_values(value_col, ascending=False).head(14)
    width, height = 1800, max(720, 180 + len(plot) * 78)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = chart_font(46, True)
    subtitle_font = chart_font(25)
    label_font = chart_font(25)
    value_font = chart_font(23)
    draw.rectangle((0, 0, width, 104), fill="#eef6f4")
    draw.text((52, 28), title, fill="#173f42", font=title_font)
    if subtitle:
        draw.text((54, 116), subtitle, fill="#5b6472", font=subtitle_font)
    max_value = max(float(plot[value_col].max()), 1)
    x0, x1 = 560, width - 180
    y = 190
    for _, row in plot.iterrows():
        label = str(row[label_col])
        value = float(row[value_col])
        for idx, line in enumerate(wrap_label(draw, label, 470, label_font)[:2]):
            draw.text((54, y - 4 + idx * 28), line, fill="#1f2937", font=label_font)
        bar_width = int((x1 - x0) * value / max_value)
        draw.rounded_rectangle((x0, y, x0 + bar_width, y + 38), radius=8, fill="#2f6f73")
        draw.line((x0, y + 50, x1, y + 50), fill="#e5e7eb", width=2)
        value_text = f"{value:.3f}" if value <= 1 else f"{value:,.0f}"
        draw.text((x0 + bar_width + 18, y + 3), value_text, fill="#111827", font=value_font)
        y += 78
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def draw_docx_table_heatmap(path: Path, title: str, df: pd.DataFrame, subtitle: str = "") -> None:
    """Render a pivot table as a colour-scaled PNG for DOCX embedding."""
    if df.empty:
        return
    row_label_col = df.columns[0]
    value_cols = [c for c in df.columns if c != row_label_col]
    if not value_cols:
        return

    n_rows = min(len(df), 25)
    n_cols = len(value_cols)
    ROW_LABEL_W = 340
    COL_W = max(90, min(160, 1560 // max(n_cols, 1)))
    ROW_H = 42
    TITLE_H = 110
    WIDTH = ROW_LABEL_W + COL_W * n_cols + 50
    HEIGHT = TITLE_H + ROW_H + n_rows * ROW_H + 50

    image = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    title_font  = chart_font(38, True)
    sub_font    = chart_font(22)
    cell_font   = chart_font(19)
    header_font = chart_font(19, True)

    draw.rectangle((0, 0, WIDTH, TITLE_H - 12), fill="#eef6f4")
    draw.text((30, 20), title, fill="#173f42", font=title_font)
    if subtitle:
        draw.text((30, TITLE_H - 32), subtitle, fill="#5b6472", font=sub_font)

    num_df = df[value_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    max_val = float(max(num_df.values.max(), 1))

    def cell_bg(val: float) -> tuple:
        if val <= 0:
            return (238, 238, 238)
        t = min(val / max_val, 1.0)
        return (int(225 * (1 - t) + 47 * t), int(240 * (1 - t) + 111 * t), int(235 * (1 - t) + 115 * t))

    def txt_fg(val: float) -> str:
        return "#ffffff" if val / max_val > 0.62 else "#111827"

    # column header row
    y_hdr = TITLE_H
    draw.rectangle((0, y_hdr, WIDTH, y_hdr + ROW_H - 1), fill="#173f42")
    draw.text((14, y_hdr + 11), str(row_label_col)[:26], fill="white", font=header_font)
    for i, col in enumerate(value_cols):
        x = ROW_LABEL_W + i * COL_W
        draw.text((x + 5, y_hdr + 11), str(col)[:13], fill="white", font=header_font)

    # data rows
    for r_idx, (_, row) in enumerate(df.head(n_rows).iterrows()):
        y = y_hdr + (r_idx + 1) * ROW_H
        draw.rectangle((0, y, WIDTH, y + ROW_H - 1), fill=(248, 252, 251) if r_idx % 2 == 0 else (255, 255, 255))
        draw.text((14, y + 11), str(row[row_label_col])[:36], fill="#1f2937", font=cell_font)
        for c_idx, col in enumerate(value_cols):
            x = ROW_LABEL_W + c_idx * COL_W
            raw = pd.to_numeric(row[col], errors="coerce")
            val = float(raw) if pd.notna(raw) else 0.0
            draw.rectangle((x + 2, y + 2, x + COL_W - 2, y + ROW_H - 3), fill=cell_bg(val))
            txt = str(int(val)) if val > 0 else "—"
            draw.text((x + COL_W // 2 - 8, y + 11), txt, fill=txt_fg(val), font=cell_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def human_annotation_agreement_rows() -> pd.DataFrame:
    seed = load_csv(REV / "pilot_ground_truth_seed.csv")
    silver = load_csv(REV / "silver_tone_ground_truth.csv")
    rows = []
    for field in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect"]:
        completed = int(seed[field].astype(str).str.strip().ne("").sum()) if not seed.empty and field in seed.columns else 0
        rows.append({"metric": f"{field} completed", "records": completed})
    if not seed.empty and "review_status" in seed.columns:
        for status, count in seed["review_status"].astype(str).replace("", "missing").value_counts().items():
            rows.append({"metric": f"review_status: {status}", "records": int(count)})
    rows.append({"metric": "silver dataset rows", "records": len(silver)})
    rows.append({"metric": "pilot seed rows", "records": len(seed)})
    return pd.DataFrame(rows)


def repeated_llm_run_rows() -> pd.DataFrame:
    model = load_csv(REV / "model_stability_summary.csv")
    prompt = load_csv(REV / "prompt_stability_summary.csv")
    rows = []
    if not model.empty and {"model", "runs"}.issubset(model.columns):
        for _, row in model.iterrows():
            rows.append({"benchmark unit": f"model: {row['model']}", "runs": pd.to_numeric(row["runs"], errors="coerce")})
    if not prompt.empty and {"prompt", "runs"}.issubset(prompt.columns):
        for _, row in prompt.iterrows():
            rows.append({"benchmark unit": f"prompt: {row['prompt']}", "runs": pd.to_numeric(row["runs"], errors="coerce")})
    return pd.DataFrame(rows).fillna(0)


def climatebert_baseline_rows() -> pd.DataFrame:
    agreement = load_csv(REV / "climatebert_proxy_agreement_summary.csv")
    records = load_csv(REV / "climatebert_proxy_agreement_records.csv")
    rows = []
    if not agreement.empty:
        row = agreement.iloc[0]
        for metric in ["percent_agreement", "cohen_kappa", "tone_commitment_rate", "climate_commitment_label_rate"]:
            if metric in agreement.columns:
                rows.append({"metric": metric, "value": pd.to_numeric(row[metric], errors="coerce")})
    if not records.empty and "agreement_commitment" in records.columns:
        agree_rate = records["agreement_commitment"].astype(str).str.lower().isin(["true", "1"]).mean()
        rows.append({"metric": "record_level_agreement_rate", "value": agree_rate})
    if not records.empty and "tone_pred" in records.columns:
        commitment_rate = records["tone_pred"].astype(str).str.lower().eq("commitment").mean()
        rows.append({"metric": "majority_baseline_commitment_binary", "value": max(commitment_rate, 1 - commitment_rate)})
    return pd.DataFrame(rows)


def ontology_extension_rows() -> pd.DataFrame:
    ontology = load_csv(REV / "ontology_coverage.csv")
    if ontology.empty:
        return pd.DataFrame()
    df = ontology.copy()
    df["records"] = pd.to_numeric(df.get("records", 0), errors="coerce").fillna(0)
    if "mapped_to_ontology" in df.columns:
        df = df[~df["mapped_to_ontology"].astype(str).str.lower().isin(["true", "1", "yes"])]
    return df.sort_values("records", ascending=False).head(20)


def ground_truth_scaffold_rows() -> pd.DataFrame:
    tone = load_csv(VIS / "tone_records_flat.csv")
    silver = load_csv(REV / "silver_tone_ground_truth.csv")
    seed = load_csv(REV / "pilot_ground_truth_seed.csv")
    annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
    rows = [
        {"metric": "tone_records_flat rows", "records": len(tone)},
        {"metric": "silver_tone_ground_truth rows", "records": len(silver)},
        {"metric": "pilot seed rows", "records": len(seed)},
        {"metric": "saved human annotation rows", "records": len(annotation)},
    ]
    if not silver.empty:
        for col in ["tone_pred", "silver_tone_ground_truth", "esg", "aspect"]:
            if col in silver.columns:
                rows.append({"metric": f"{col} non-empty", "records": int(silver[col].astype(str).str.strip().ne("").sum())})
    return pd.DataFrame(rows)


def pilot_annotation_completion_rows() -> pd.DataFrame:
    annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
    seed = load_csv(REV / "pilot_ground_truth_seed.csv")
    df = annotation if not annotation.empty else seed
    if df.empty:
        return pd.DataFrame()
    rows = []
    for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "annotator", "review_notes"]:
        if col in df.columns:
            done = int(df[col].astype(str).str.strip().ne("").sum())
            rows.append({"field": col, "completed": done, "missing": len(df) - done, "total": len(df)})
    if "review_status" in df.columns:
        for status, count in df["review_status"].astype(str).replace("", "missing").value_counts().items():
            rows.append({"field": f"review_status: {status}", "completed": int(count), "missing": 0, "total": len(df)})
    return pd.DataFrame(rows)


def ground_truth_tone_comparison_rows() -> pd.DataFrame:
    annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
    seed = load_csv(REV / "pilot_ground_truth_seed.csv")
    silver = load_csv(REV / "silver_tone_ground_truth.csv")
    df = annotation if not annotation.empty else seed
    if df.empty:
        df = silver
    if df.empty:
        return pd.DataFrame()
    truth_col = "ground_truth_tone" if "ground_truth_tone" in df.columns and df["ground_truth_tone"].astype(str).str.strip().ne("").any() else "silver_tone_ground_truth"
    pred_col = "tone_pred" if "tone_pred" in df.columns else "tone"
    if truth_col not in df.columns or pred_col not in df.columns:
        return pd.DataFrame()
    out = (
        df.assign(
            truth=df[truth_col].astype(str).str.strip().replace("", "missing"),
            prediction=df[pred_col].astype(str).str.strip().replace("", "missing"),
        )
        .groupby(["truth", "prediction"], dropna=False)
        .size()
        .reset_index(name="records")
        .sort_values("records", ascending=False)
    )
    out["truth_source"] = truth_col
    return out


def ground_truth_t2_output_rows() -> pd.DataFrame:
    t2 = load_csv(WORKFLOW / "t2_flat_outputs.csv")
    if t2.empty:
        return pd.DataFrame()
    group_cols = [col for col in ["rule_tone", "tone_pred", "sentiment_pred"] if col in t2.columns]
    if not group_cols:
        return t2.head(30)
    return (
        t2.assign(records=1)
        .groupby(group_cols, dropna=False)["records"]
        .sum()
        .reset_index()
        .sort_values("records", ascending=False)
    )


def pdf_prompt_matrix_rows() -> pd.DataFrame:
    """Pivot table: rows = PDF/company, columns = prompt templates, values = record count."""
    silver = load_csv(REV / "silver_tone_ground_truth.csv")
    if silver.empty or "prompt" not in silver.columns:
        return pd.DataFrame()
    row_col = "company" if "company" in silver.columns else "target"
    pivot = (
        silver.groupby([row_col, "prompt"])
        .size()
        .reset_index(name="records")
        .pivot(index=row_col, columns="prompt", values="records")
        .fillna(0)
        .astype(int)
    )
    # Shorten prompt column names: strip .md and leading "tone_"
    pivot.columns = [str(c).replace(".md", "").replace("tone_", "") for c in pivot.columns]
    pivot.columns.name = None
    pivot.index.name = "PDF / Company"
    pivot["TOTAL"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=False)
    return pivot.reset_index()


def ensure_extra_graph_attachments() -> None:
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_human_annotation_agreement.png",
        "Human Annotation Agreement Readiness",
        human_annotation_agreement_rows(),
        "metric",
        "records",
        "Current ground-truth completion and pilot review status",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_repeated_llm_runs.png",
        "Repeated LLM Runs Coverage",
        repeated_llm_run_rows(),
        "benchmark unit",
        "runs",
        "Current run counts by model and prompt; confidence intervals still need repeated runs",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_climatebert_baseline.png",
        "ClimateBERT Baseline Comparison",
        climatebert_baseline_rows(),
        "metric",
        "value",
        "Agreement, kappa, label rates, and majority baseline",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_ontology_extension_candidates.png",
        "Ontology Extension Candidates",
        ontology_extension_rows(),
        "aspect",
        "records",
        "Top unmapped Indonesian ESG aspects for ontology extension",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_ground_truth_scaffold_coverage.png",
        "Ground Truth Scaffold Coverage",
        ground_truth_scaffold_rows(),
        "metric",
        "records",
        "ground_truth.py evidence layer from tone_records_flat into silver and pilot annotation files",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_pilot_annotation_completion.png",
        "Pilot Annotation Completion",
        pilot_annotation_completion_rows(),
        "field",
        "completed",
        "Ground-truth fields completed in the pilot annotation table",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_ground_truth_tone_comparison.png",
        "Ground Truth Tone Comparison",
        ground_truth_tone_comparison_rows(),
        "truth",
        "records",
        "Human or silver ground-truth tone compared with model tone output",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_ground_truth_t2_outputs.png",
        "ground_truth.py T2 Tone Outputs",
        ground_truth_t2_output_rows(),
        "tone_pred",
        "records",
        "Flattened T2 hybrid/rule output from the resumable ground_truth.py pipeline",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "docx_pdf_prompt_matrix.png",
        "PDF × Prompt Coverage Matrix",
        pdf_prompt_matrix_rows(),
        "Records extracted per company × prompt template combination",
    )


def graph_manifest() -> pd.DataFrame:
    rows = [
        {
            "figure": "A.1",
            "title": "Tone distribution",
            "path": VIS / "tone_distribution.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "tone_records_flat.csv",
            "source page": "pages/6_1_Chapter_4_Implementation_Results.py",
        },
        {
            "figure": "A.2",
            "title": "ESG by tone",
            "path": VIS / "esg_by_tone.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "tone_esg_crosstab.csv",
            "source page": "pages/6_1_Chapter_4_Implementation_Results.py",
        },
        {
            "figure": "A.3",
            "title": "Aspect by tone heatmap",
            "path": VIS / "aspect_by_tone_heatmap.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "aspect_tone_crosstab.csv",
            "source page": "pages/6_1_Chapter_4_Implementation_Results.py",
        },
        {
            "figure": "A.4",
            "title": "Tone by ClimateBERT label",
            "path": VIS / "climatebert_label_by_tone.png",
            "chapter": "Chapter 4 / 5",
            "rq": "RQ3",
            "source table": "tone_climatebert_label_crosstab.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.5",
            "title": "Top-scoring ClimateBERT records",
            "path": VIS / "climatebert_remote_top_scores.png",
            "chapter": "Chapter 5",
            "rq": "RQ3",
            "source table": "climatebert_remote_flat.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.6",
            "title": "Streamlit overview",
            "path": VIS / "streamlit_outputs" / "01_overview.png",
            "chapter": "Chapter 6",
            "rq": "RQ5",
            "source table": "DOCX evidence summary",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.7",
            "title": "Per-RQ evidence",
            "path": VIS / "streamlit_outputs" / "02_per_rq_evidence.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ1-RQ6",
            "source table": "chapter-to-RQ mapping",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.8",
            "title": "Benchmark plan",
            "path": VIS / "streamlit_outputs" / "04_benchmarks.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ6",
            "source table": "benchmark checklist",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.9",
            "title": "Evidence matrix",
            "path": VIS / "streamlit_outputs" / "07_evidence_matrix.png",
            "chapter": "Chapter 6",
            "rq": "RQ5",
            "source table": "graph manifest",
            "source page": "pages/6_4_ch4-6.py",
        },
        {
            "figure": "A.10",
            "title": "Model parse success benchmark",
            "path": GRAPH_DIR / "docx_model_parse_success.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ6",
            "source table": "model_stability_summary.csv",
            "source page": "pages/6_3_Chapter_6_Conclusion.py",
        },
        {
            "figure": "A.11",
            "title": "Prompt missing-tone benchmark",
            "path": GRAPH_DIR / "docx_prompt_missing_tone_rate.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ6",
            "source table": "prompt_stability_summary.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.12",
            "title": "Ontology mapped vs novel aspects",
            "path": GRAPH_DIR / "docx_ontology_mapped_vs_unmapped.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ4",
            "source table": "ontology_coverage.csv",
            "source page": "pages/6_2_Chapter_5_Discussion.py",
        },
        {
            "figure": "A.13",
            "title": "Human annotation agreement",
            "path": GRAPH_DIR / "docx_human_annotation_agreement.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ2",
            "source table": "pilot_ground_truth_seed.csv + silver_tone_ground_truth.csv",
            "source page": "pages/1_1_Ground_Truth_Workbench.py",
        },
        {
            "figure": "A.14",
            "title": "Repeated LLM runs",
            "path": GRAPH_DIR / "docx_repeated_llm_runs.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ6",
            "source table": "model_stability_summary.csv + prompt_stability_summary.csv",
            "source page": "pages/2_3_LLM_Background_Run_Monitor.py",
        },
        {
            "figure": "A.15",
            "title": "ClimateBERT baseline",
            "path": GRAPH_DIR / "docx_climatebert_baseline.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ3",
            "source table": "climatebert_proxy_agreement_summary.csv + climatebert_proxy_agreement_records.csv",
            "source page": "pages/1_4_ClimateBERT_Record_Batch.py",
        },
        {
            "figure": "A.16",
            "title": "Ontology extension",
            "path": GRAPH_DIR / "docx_ontology_extension_candidates.png",
            "chapter": "Chapter 5 / 6",
            "rq": "RQ4",
            "source table": "ontology_coverage.csv",
            "source page": "pages/1_6_Ontology_Path_Viewer.py",
        },
        {
            "figure": "A.17",
            "title": "Ground truth scaffold coverage",
            "path": GRAPH_DIR / "docx_ground_truth_scaffold_coverage.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "tone_records_flat.csv + silver_tone_ground_truth.csv",
            "source page": "pages/1_8_Ground_Truth_Output_Visualizer.py",
        },
        {
            "figure": "A.18",
            "title": "Pilot annotation completion",
            "path": GRAPH_DIR / "docx_pilot_annotation_completion.png",
            "chapter": "Chapter 4 / 5",
            "rq": "RQ2",
            "source table": "pilot_ground_truth_seed.csv + pilot_ground_truth_annotations.csv",
            "source page": "pages/1_1_Ground_Truth_Workbench.py",
        },
        {
            "figure": "A.19",
            "title": "Ground truth tone comparison",
            "path": GRAPH_DIR / "docx_ground_truth_tone_comparison.png",
            "chapter": "Chapter 4 / 5",
            "rq": "RQ2",
            "source table": "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv",
            "source page": "pages/1_3_Ground_Truth_Metrics.py",
        },
        {
            "figure": "A.20",
            "title": "ground_truth.py T2 tone outputs",
            "path": GRAPH_DIR / "docx_ground_truth_t2_outputs.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "t2_flat_outputs.csv + t2_results.jsonl",
            "source page": "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py",
        },
        {
            "figure": "A.21",
            "title": "PDF × Prompt coverage matrix",
            "path": GRAPH_DIR / "docx_pdf_prompt_matrix.png",
            "chapter": "Chapter 4 / 6",
            "rq": "RQ6",
            "source table": "silver_tone_ground_truth.csv",
            "source page": "pages/6_4_ch4-6.py",
        },
    ]
    df = pd.DataFrame(rows)
    df["exists"] = df["path"].map(lambda p: Path(p).exists())
    df["path"] = df["path"].astype(str)
    return df


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def _normalize_from_map(value: Any, mapping: dict[str, str], fallback: str = "Other / Unclassified") -> str:
    text = format_display_value(value)
    if not text:
        return fallback
    return mapping.get(text.lower(), fallback)


def _find_dashboard_data_file(name: str) -> Path | None:
    try:
        return resolve_dashboard_data_path(name)
    except FileNotFoundError:
        pass
    for ext in (".csv", ".txt"):
        path = DASHBOARD_DATA_DIR / f"{name}{ext}"
        if path.exists():
            return path
    return None


@st.cache_data
def load_dashboard_records() -> tuple[pd.DataFrame, str, str]:
    try:
        path = resolve_dashboard_data_path("data_output")
        df = load_and_parse()
        source_label = "dashboard/data/data/data_output parsed JSON"
    except Exception:
        path = _find_dashboard_data_file("output_in_csv")
        if path is None:
            return pd.DataFrame(), "not found", "dashboard data not found"
        df = read_dashboard_dataset("output_in_csv")
        source_label = "dashboard/data/data/output_in_csv fallback"

    df.columns = df.columns.str.lower().str.strip()
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df = df.drop(columns=[col for col in HEAVY_SOURCE_COLUMNS if col in df.columns])
    if {"sentence", "aspect"}.issubset(df.columns):
        df = df[df["sentence"].notna() & df["aspect"].notna()].copy()
    for col in ["filename", "model", "sentence", "aspect", "aspect_category", "sentiment", "tone"]:
        if col in df.columns:
            df[col] = df[col].map(format_display_value)
    if "sentence" in df.columns:
        df = df[df["sentence"] != ""].reset_index(drop=True)

    if "aspect_category" in df.columns:
        df["aspect_category_raw"] = df["aspect_category"]
        df["aspect_category"] = df["aspect_category"].apply(lambda value: _normalize_from_map(value, ASPECT_CATEGORY_MAP))
        df["esg_pillar"] = df["aspect_category"]
    if "sentiment" in df.columns:
        df["sentiment_raw"] = df["sentiment"]
        df["sentiment_norm"] = df["sentiment"].apply(lambda value: _normalize_from_map(value, SENTIMENT_MAP))
    if "tone" in df.columns:
        df["tone_raw"] = df["tone"]
        df["tone"] = df["tone"].apply(lambda value: _normalize_from_map(value, TONE_MAP))
    if "aspect" in df.columns:
        df["aspect"] = df["aspect"].replace("", "Unknown")
    if "filename" in df.columns:
        df["filename"] = df["filename"].replace("", "Unknown source")
    return df, str(path), source_label


def live_graph_manifest() -> pd.DataFrame:
    rows = [
        ("A.1", "Tone distribution", "Chapter 4", "RQ2", "data_output parsed JSON -> tone", "Tone_Distribution", True),
        ("A.2", "ESG by tone", "Chapter 4", "RQ2", "data_output parsed JSON -> tone x aspect_category", "Data_File_Visualizer", True),
        ("A.3", "Aspect by tone heatmap", "Chapter 4", "RQ2", "data_output parsed JSON -> aspect x tone", "Aspect", True),
        ("A.4", "Sentiment distribution", "Chapter 4", "RQ2", "data_output parsed JSON -> sentiment", "Tone_Distribution", True),
        ("A.5", "ESG pillar distribution", "Chapter 4", "RQ1", "data_output parsed JSON -> aspect_category", "Data_File_Visualizer", True),
        ("A.6", "Records per source document", "Chapter 4", "RQ1", "data_output parsed JSON -> filename", "Parsed_ESG_Review", True),
        ("A.7", "Tone x ESG pillar heatmap", "Chapter 4", "RQ2", "data_output parsed JSON -> tone x esg_pillar", "Data_File_Visualizer", True),
        ("A.8", "Top 20 aspects by record count", "Chapter 4", "RQ4", "data_output parsed JSON -> aspect", "Aspect", True),
        ("A.9", "Ontology URI coverage", "Chapter 5", "RQ4", "data_output parsed JSON -> ontology_uri", "JSON_Ontology_Usage_Map", True),
        ("A.10", "Aspect x sentiment heatmap", "Chapter 5", "RQ2", "data_output parsed JSON -> aspect x sentiment_norm", "Tone_Distribution", True),
        ("A.11", "Confidence score distribution", "Chapter 4", "RQ6", "data_output parsed JSON -> confidence", "Benchmark_Model", True),
        ("A.12", "Per-RQ evidence mapping", "Chapter 4 / 6", "RQ1-RQ6", "chapter-to-RQ mapping", "Research_Questions_Dashboard", True),
    ]
    return pd.DataFrame(rows, columns=["figure", "title", "chapter", "rq", "source table", "source page", "available"])


def live_figure_data(figure: str, data: pd.DataFrame) -> tuple[go.Figure | None, pd.DataFrame]:
    if data.empty:
        return None, pd.DataFrame()

    def has_columns(*cols: str) -> bool:
        return all(col in data.columns for col in cols)

    def uri_status(value: Any) -> str:
        try:
            if pd.isna(value):
                return "No URI"
        except Exception:
            pass
        text = str(value).strip()
        return "Has URI" if text and text.lower() not in {"nan", "none", "<na>"} else "No URI"

    if figure == "A.1" and has_columns("tone"):
        tbl = data["tone"].value_counts().reset_index()
        tbl.columns = ["tone", "records"]
        fig = px.bar(tbl, x="tone", y="records", color="tone", title="Tone Distribution")
        fig.update_layout(showlegend=False)
        return fig, tbl
    if figure == "A.2" and has_columns("tone", "aspect_category"):
        tbl = data.groupby(["tone", "aspect_category"]).size().reset_index(name="records")
        fig = px.bar(tbl, x="tone", y="records", color="aspect_category", barmode="stack", title="ESG by Tone")
        pivot = tbl.pivot(index="tone", columns="aspect_category", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        return fig, pivot.reset_index()
    if figure == "A.3" and has_columns("aspect", "tone"):
        top = data["aspect"].value_counts().head(15).index
        tbl = data[data["aspect"].isin(top)].groupby(["aspect", "tone"]).size().reset_index(name="records")
        pivot = tbl.pivot(index="aspect", columns="tone", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Blues", title="Aspect by Tone Heatmap", height=520)
        return fig, pivot.reset_index()
    if figure == "A.4" and has_columns("sentiment_norm"):
        tbl = data["sentiment_norm"].value_counts().reset_index()
        tbl.columns = ["sentiment", "records"]
        fig = px.bar(tbl, x="sentiment", y="records", color="sentiment", title="Sentiment Distribution")
        fig.update_layout(showlegend=False)
        return fig, tbl
    if figure == "A.5" and has_columns("esg_pillar"):
        tbl = data["esg_pillar"].value_counts().reset_index()
        tbl.columns = ["esg_pillar", "records"]
        fig = px.pie(tbl, names="esg_pillar", values="records", hole=0.4, title="ESG Pillar Distribution")
        return fig, tbl
    if figure == "A.6" and has_columns("filename"):
        tbl = data.groupby("filename").size().reset_index(name="records").sort_values("records", ascending=False)
        fig = px.bar(tbl, x="records", y="filename", orientation="h", title="Records per Source Document")
        fig.update_layout(showlegend=False, height=max(380, 28 * len(tbl)), yaxis={"categoryorder": "total ascending"})
        return fig, tbl
    if figure == "A.7" and has_columns("esg_pillar", "tone"):
        valid = data[data["esg_pillar"] != "Other / Unclassified"]
        tbl = valid.groupby(["esg_pillar", "tone"]).size().reset_index(name="records")
        pivot = tbl.pivot(index="esg_pillar", columns="tone", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Teal", title="Tone x ESG Pillar Heatmap")
        return fig, pivot.reset_index()
    if figure == "A.8" and has_columns("aspect"):
        tbl = data[data["aspect"] != "Unknown"]["aspect"].value_counts().head(20).reset_index()
        tbl.columns = ["aspect", "records"]
        fig = px.bar(tbl, x="records", y="aspect", orientation="h", title="Top 20 Aspects by Record Count")
        fig.update_layout(showlegend=False, height=560, yaxis={"categoryorder": "total ascending"})
        return fig, tbl
    if figure == "A.9" and "ontology_uri" in data.columns:
        status = data["ontology_uri"].map(uri_status)
        tbl = status.value_counts().reset_index()
        tbl.columns = ["ontology_uri_status", "records"]
        fig = px.pie(tbl, names="ontology_uri_status", values="records", hole=0.4, title="Ontology URI Coverage")
        return fig, tbl
    if figure == "A.10" and has_columns("aspect", "sentiment_norm"):
        top = data["aspect"].value_counts().head(12).index
        tbl = data[data["aspect"].isin(top)].groupby(["aspect", "sentiment_norm"]).size().reset_index(name="records")
        pivot = tbl.pivot(index="aspect", columns="sentiment_norm", values="records").fillna(0).astype(int)
        pivot.columns.name = None
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="RdYlGn", title="Aspect x Sentiment Heatmap", height=480)
        return fig, pivot.reset_index()
    if figure == "A.11" and "confidence" in data.columns:
        conf = pd.to_numeric(data["confidence"], errors="coerce").dropna()
        tbl = conf.describe().reset_index()
        tbl.columns = ["statistic", "value"]
        fig = px.histogram(conf, nbins=30, title="Confidence Score Distribution")
        fig.update_layout(showlegend=False)
        return fig, tbl
    if figure == "A.12":
        tbl = chapter_mapping_rows()
        counts = tbl[["chapter"]].copy()
        counts["evidence_items"] = 1
        counts = counts.groupby("chapter", as_index=False)["evidence_items"].sum()
        fig = px.bar(counts, x="chapter", y="evidence_items", color="chapter", title="Chapter Evidence Items")
        fig.update_layout(showlegend=False)
        return fig, tbl
    return None, pd.DataFrame()


def dashboard_result_bundle(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tone_records = data.copy()
    if "filename" in tone_records.columns and "target_doc" not in tone_records.columns:
        tone_records["target_doc"] = tone_records["filename"]
    if "esg_pillar" in tone_records.columns and "esg" not in tone_records.columns:
        tone_records["esg"] = tone_records["esg_pillar"]
    if {"tone", "esg"}.issubset(tone_records.columns):
        tone_esg = (
            tone_records.groupby(["tone", "esg"])
            .size()
            .reset_index(name="records")
            .pivot(index="tone", columns="esg", values="records")
            .fillna(0)
            .astype(int)
            .reset_index()
        )
    else:
        tone_esg = pd.DataFrame()
    return {
        "tone_records": tone_records,
        "tone_esg": tone_esg,
        "ocr": pd.DataFrame(),
        "agreement": pd.DataFrame(),
        "ontology": pd.DataFrame(),
        "model_stability": pd.DataFrame(),
        "prompt_stability": pd.DataFrame(),
        "inventory": pd.DataFrame(),
    }


def source_dataframe_for_figure(row: pd.Series, bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    figure = str(row["figure"])
    if figure == "A.1":
        df = bundle["tone_records"]
        if df.empty or "tone" not in df.columns:
            return pd.DataFrame()
        return df["tone"].astype(str).replace("", "missing").value_counts().rename_axis("tone").reset_index(name="records")
    if figure == "A.2":
        return load_csv(VIS / "tone_esg_crosstab.csv")
    if figure == "A.3":
        return load_csv(VIS / "aspect_tone_crosstab.csv")
    if figure == "A.4":
        return load_csv(VIS / "tone_climatebert_label_crosstab.csv")
    if figure == "A.5":
        df = load_csv(VIS / "climatebert_remote_flat.csv")
        return df.head(30) if not df.empty else df
    if figure == "A.6":
        return docx_snapshot_rows(bundle)
    if figure == "A.7":
        return chapter_mapping_rows()
    if figure == "A.8":
        return benchmark_checklist_rows()
    if figure == "A.9":
        return graph_manifest()[["figure", "title", "chapter", "rq", "source table", "source page", "exists"]]
    if figure == "A.10":
        return load_csv(ROOT / "results" / "revision_analysis" / "model_stability_summary.csv")
    if figure == "A.11":
        return load_csv(ROOT / "results" / "revision_analysis" / "prompt_stability_summary.csv")
    if figure == "A.12":
        return load_csv(ROOT / "results" / "revision_analysis" / "ontology_coverage.csv")
    if figure == "A.13":
        return human_annotation_agreement_rows()
    if figure == "A.14":
        return repeated_llm_run_rows()
    if figure == "A.15":
        return climatebert_baseline_rows()
    if figure == "A.16":
        return ontology_extension_rows()
    if figure == "A.17":
        return ground_truth_scaffold_rows()
    if figure == "A.18":
        return pilot_annotation_completion_rows()
    if figure == "A.19":
        return ground_truth_tone_comparison_rows()
    if figure == "A.20":
        return ground_truth_t2_output_rows()
    if figure == "A.21":
        return pdf_prompt_matrix_rows()
    return pd.DataFrame()


def docx_snapshot_rows(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tone = bundle["tone_records"]
    ocr = bundle["ocr"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    model = bundle["model_stability"]
    prompt = bundle["prompt_stability"]
    pages = pd.to_numeric(ocr.get("pages", pd.Series(dtype=float)), errors="coerce").sum() if not ocr.empty else 0
    mapped = int(ontology.get("mapped_to_ontology", pd.Series(dtype=bool)).astype(bool).sum()) if not ontology.empty and "mapped_to_ontology" in ontology.columns else 0
    kappa = pd.to_numeric(agreement.get("cohen_kappa", pd.Series(dtype=float)), errors="coerce")
    pct = pd.to_numeric(agreement.get("percent_agreement", pd.Series(dtype=float)), errors="coerce")
    return pd.DataFrame(
        [
            {
                "metric": "Tone records",
                "value": f"{len(tone):,}",
                "existing data": "tone_records_flat.csv",
                "redirect page": "pages/6_1_Chapter_4_Implementation_Results.py",
            },
            {
                "metric": "Source documents",
                "value": f"{max(tone['target_doc'].nunique() if not tone.empty and 'target_doc' in tone.columns else 0, len(ocr)):,}",
                "existing data": "ocr_processing_summary.csv",
                "redirect page": "pages/6_1_Chapter_4_Implementation_Results.py",
            },
            {
                "metric": "OCR pages",
                "value": f"{int(pages):,}",
                "existing data": "ocr_processing_summary.csv",
                "redirect page": "pages/2_4_PDF_Page_Processing_Audit.py",
            },
            {
                "metric": "Prompt templates",
                "value": f"{max(tone['prompt'].nunique() if not tone.empty and 'prompt' in tone.columns else 0, len(prompt)):,}",
                "existing data": "prompt_stability_summary.csv",
                "redirect page": "pages/6_3_Chapter_6_Conclusion.py",
            },
            {
                "metric": "Model rows",
                "value": f"{len(model):,}",
                "existing data": "model_stability_summary.csv",
                "redirect page": "pages/6_3_Chapter_6_Conclusion.py",
            },
            {
                "metric": "ClimateBERT/proxy agreement",
                "value": f"{pct.iloc[0]:.1%}" if not pct.empty and pd.notna(pct.iloc[0]) else "n/a",
                "existing data": "climatebert_proxy_agreement_summary.csv",
                "redirect page": "pages/6_2_Chapter_5_Discussion.py",
            },
            {
                "metric": "Cohen kappa",
                "value": f"{kappa.iloc[0]:.3f}" if not kappa.empty and pd.notna(kappa.iloc[0]) else "n/a",
                "existing data": "climatebert_proxy_agreement_summary.csv",
                "redirect page": "pages/6_2_Chapter_5_Discussion.py",
            },
            {
                "metric": "Ontology mapped rows",
                "value": f"{mapped}/{len(ontology):,}" if len(ontology) else "n/a",
                "existing data": "ontology_coverage.csv",
                "redirect page": "pages/6_2_Chapter_5_Discussion.py",
            },
        ]
    )


def chapter_mapping_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "chapter": "Chapter 4 - Implementation and Results",
                "streamlit page": "pages/6_1_Chapter_4_Implementation_Results.py",
                "primary evidence": "tone records, PDF x prompt matrix, tone/ESG distributions, ClimateBERT crosstab, artifact/model/prompt stability",
                "figures": "A.1, A.2, A.3, A.4, A.7, A.8, A.10",
            },
            {
                "chapter": "Chapter 5 - Discussion",
                "streamlit page": "pages/6_2_Chapter_5_Discussion.py",
                "primary evidence": "agreement metrics, ontology coverage, failure modes, prompt/model sensitivity",
                "figures": "A.4, A.5, A.11, A.12",
            },
            {
                "chapter": "Chapter 6 - Conclusion",
                "streamlit page": "pages/6_3_Chapter_6_Conclusion.py",
                "primary evidence": "contribution summary, RQ answers, artifact inventory, future-work benchmark checklist",
                "figures": "A.6, A.7, A.8, A.9, A.10, A.11, A.12",
            },
        ]
    )


def benchmark_checklist_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"benchmark": "OCR quality", "why needed": "CER/WER is not yet measured.", "target artifact": "ocr_quality_by_page.csv", "redirect page": "pages/1_2_OCR_Quality_Workbench.py"},
            {"benchmark": "Human annotation agreement", "why needed": "Single-annotator labels need reliability evidence.", "target artifact": "human_agreement_summary.csv", "redirect page": "pages/1_1_Ground_Truth_Workbench.py"},
            {"benchmark": "Repeated LLM runs", "why needed": "Model/prompt stability needs confidence intervals.", "target artifact": "model_prompt_repeated_run_ci.csv", "redirect page": "pages/2_3_LLM_Background_Run_Monitor.py"},
            {"benchmark": "ClimateBERT baseline", "why needed": "Compare tone-vs-ClimateBERT to majority and human-labelled baselines.", "target artifact": "climatebert_baseline_comparison.csv", "redirect page": "pages/1_4_ClimateBERT_Record_Batch.py"},
            {"benchmark": "Ontology extension", "why needed": "Formalise unmapped Indonesian ESG aspects.", "target artifact": "indonesian_esg_ontology_extension.csv", "redirect page": "pages/1_6_Ontology_Path_Viewer.py"},
        ]
    )


def page_slug(page: str) -> str:
    stem = Path(page).stem
    parts = stem.split("_", 1)
    if len(parts) == 2 and parts[0].isdigit():
        stem = parts[1]
    return f"/{stem}"


def redirect_button(label: str, page: str) -> None:
    st.link_button(label, page_slug(page), use_container_width=True)


def regenerate_docx() -> Path:
    from update_ch4_6_docx_graphs import update_document

    return update_document()


dashboard_df, dashboard_data_path, dashboard_source_label = load_dashboard_records()
bundle = dashboard_result_bundle(dashboard_df)

st.title("Ch4-6 Structure Benchmarks and Graph Attachments")
st.caption(
    "Streamlit reader for `thesis_ch4_6_structure_benchmarks.docx`, the updated graph-attached DOCX, "
    "and live figures recomputed from the dashboard dataset instead of `new_page/results` artifacts."
)
metric_row(bundle)

st.divider()

doc_cols = st.columns([2, 2, 1, 1])
doc_cols[0].markdown(f"**Source DOCX:** `{SOURCE_DOCX}`")
doc_cols[1].markdown(f"**Updated DOCX:** `{UPDATED_DOCX}`")
doc_cols[2].metric("Embedded graphs", media_count(UPDATED_DOCX))
doc_cols[3].metric("Graph files", int(graph_manifest()["exists"].sum()))

action_cols = st.columns([1, 1, 2])
with action_cols[0]:
    if st.button("Regenerate updated DOCX", type="primary", use_container_width=True):
        try:
            out = regenerate_docx()
            st.success(f"Updated DOCX generated: {out}")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not regenerate DOCX: {exc}")
with action_cols[1]:
    if UPDATED_DOCX.exists():
        st.download_button(
            "Download updated DOCX",
            UPDATED_DOCX.read_bytes(),
            UPDATED_DOCX.name,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    else:
        st.info("Generate the updated DOCX first.")
with action_cols[2]:
    st.info(
        "This page mirrors the Word appendix: Chapter 4 receives empirical result graphs, "
        "Chapter 5 receives validation/diagnostic graphs, and Chapter 6 receives benchmark and contribution evidence."
    )

tab_summary, tab_docx, tab_graphs, tab_chapters, tab_live = st.tabs(
    ["DOCX Summary", "DOCX Structure", "Graph Attachments", "Chapter 4-6 Mapping", "Live Charts"]
)

with tab_summary:
    st.header("DOCX Evidence Summary")
    summary_rows = pd.DataFrame(
        [
            {"item": "Source document", "value": str(SOURCE_DOCX), "status": "found" if SOURCE_DOCX.exists() else "missing", "redirect page": "DOCX file"},
            {"item": "Updated document", "value": str(UPDATED_DOCX), "status": "found" if UPDATED_DOCX.exists() else "missing", "redirect page": "DOCX file"},
            {"item": "Embedded media", "value": media_count(UPDATED_DOCX), "status": "expected: 12", "redirect page": "Graph Attachments tab"},
            {"item": "Generated benchmark graph folder", "value": str(GRAPH_DIR), "status": "found" if GRAPH_DIR.exists() else "missing", "redirect page": "Graph Attachments tab"},
        ]
    )
    st.dataframe(summary_rows.astype(str), use_container_width=True, hide_index=True, height=180)

    st.subheader("Snapshot with Existing Data and Redirects")
    snapshot = docx_snapshot_rows(bundle)
    st.dataframe(snapshot, use_container_width=True, hide_index=True, height=300)
    redirect_cols = st.columns(4)
    redirects = [
        ("Chapter 4 results", "pages/6_1_Chapter_4_Implementation_Results.py"),
        ("Chapter 5 discussion", "pages/6_2_Chapter_5_Discussion.py"),
        ("Chapter 6 conclusion", "pages/6_3_Chapter_6_Conclusion.py"),
        ("PDF audit", "pages/2_4_PDF_Page_Processing_Audit.py"),
    ]
    for idx, (label, page) in enumerate(redirects):
        with redirect_cols[idx]:
            redirect_button(label, page)

    st.subheader("What the DOCX update adds")
    st.markdown(
        """
        - **Appendix A.1** live evidence snapshot from the shared result bundle.
        - **Appendix A.2** mapping from Streamlit pages `6_1`, `6_2`, and `6_3` to thesis chapter roles.
        - **Appendix A.3** attached graph register with 12 graph images.
        - **Appendix A.4** chapter-level insertion notes.
        - **Appendix A.5** benchmark checklist still needed for stronger thesis claims.
        """
    )

with tab_docx:
    st.header("DOCX Structure Reader")
    selected_doc = st.radio(
        "Document to inspect",
        ["Updated graph-attached DOCX", "Original source DOCX"],
        horizontal=True,
    )
    doc_path = UPDATED_DOCX if selected_doc.startswith("Updated") else SOURCE_DOCX
    doc_df = read_docx_paragraphs(doc_path)
    search = st.text_input("Search DOCX text", placeholder="Example: RQ3, ClimateBERT, Appendix, benchmark")
    display = doc_df.copy()
    if search.strip():
        display = display[display.astype(str).apply(lambda col: col.str.contains(search.strip(), case=False, regex=False)).any(axis=1)]
    st.dataframe(display, use_container_width=True, hide_index=True, height=560)

with tab_graphs:
    st.header("Live Figure Tables")
    st.caption(
        f"Computed from `{dashboard_data_path}` ({dashboard_source_label}); "
        "`new_page/results` PNG and CSV artifacts are intentionally not used in this tab."
    )
    manifest = live_graph_manifest()
    c1, c2, c3, c4 = st.columns(4)
    chapter_filter = c1.selectbox("Chapter", ["All"] + sorted(manifest["chapter"].unique().tolist()))
    rq_filter = c2.selectbox("RQ", ["All"] + sorted(manifest["rq"].unique().tolist()))
    view_mode = c3.selectbox("View", ["Chart + table", "Chart only", "Table only"])
    only_available = c4.toggle("Only available figures", value=True)
    filtered = manifest.copy()
    if chapter_filter != "All":
        filtered = filtered[filtered["chapter"].eq(chapter_filter)]
    if rq_filter != "All":
        filtered = filtered[filtered["rq"].eq(rq_filter)]
    if only_available:
        filtered = filtered[filtered["available"]]
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=260)

    for _, row in filtered.iterrows():
        st.divider()
        st.subheader(f"{row['figure']} - {row['title']}")
        meta_cols = st.columns([2, 2, 2, 1])
        meta_cols[0].caption(f"{row['chapter']} | {row['rq']}")
        meta_cols[1].caption(f"Source data: `{row['source table']}`")
        meta_cols[2].caption(f"Source page: `/{row['source page']}`")
        with meta_cols[3]:
            redirect_button("Open page", str(row["source page"]))

        fig_obj, source_df = live_figure_data(str(row["figure"]), dashboard_df)
        graph_col, table_col = st.columns([1.05, 1], gap="large")
        if view_mode in {"Chart + table", "Chart only"}:
            with graph_col:
                st.markdown("**Live chart**")
                if fig_obj is not None:
                    st.plotly_chart(fig_obj, use_container_width=True)
                else:
                    st.info("Chart could not be generated from the dashboard dataset.")
        if view_mode in {"Chart + table", "Table only"}:
            with table_col:
                st.markdown("**Computed backing table**")
                if source_df.empty:
                    st.info("No backing table is available from the dashboard dataset.")
                else:
                    if str(row["figure"]) == "A.21" and len(source_df.columns) > 2:
                        # Pivot table: apply colour gradient on numeric columns
                        value_cols = list(source_df.columns[1:])
                        num_df = source_df.copy()
                        for c in value_cols:
                            num_df[c] = pd.to_numeric(num_df[c], errors="coerce").fillna(0)
                        try:
                            styled = (
                                num_df.style
                                .background_gradient(subset=value_cols, cmap="YlGn")
                                .format({c: "{:.0f}" for c in value_cols})
                                .set_properties(**{"font-size": "12px"})
                            )
                            st.dataframe(styled, use_container_width=True, hide_index=True, height=420)
                        except Exception:
                            st.dataframe(source_df.astype(str), use_container_width=True, hide_index=True, height=420)
                        st.caption(
                            f"Rows = {len(source_df)} companies/PDFs  ·  "
                            f"Columns = {len(value_cols) - 1} prompt templates + TOTAL  ·  "
                            "Cell value = record count"
                        )
                    else:
                        st.dataframe(source_df.astype(str), use_container_width=True, hide_index=True, height=360)
                    st.download_button(
                        f"Download {row['figure']} computed table",
                        source_df.to_csv(index=False).encode("utf-8"),
                        f"{row['figure'].replace('.', '_')}_{str(row['source table']).replace('/', '_')}.csv",
                        "text/csv",
                        use_container_width=True,
                        key=f"download_{row['figure']}",
                    )

with tab_chapters:
    st.header("Chapter 4-6 Mapping")
    mapping = chapter_mapping_rows()
    st.dataframe(mapping, use_container_width=True, hide_index=True, height=260)
    page_cols = st.columns(3)
    with page_cols[0]:
        redirect_button("Open Chapter 4 page", "pages/6_1_Chapter_4_Implementation_Results.py")
    with page_cols[1]:
        redirect_button("Open Chapter 5 page", "pages/6_2_Chapter_5_Discussion.py")
    with page_cols[2]:
        redirect_button("Open Chapter 6 page", "pages/6_3_Chapter_6_Conclusion.py")

    st.subheader("Benchmark checklist still needed")
    checklist = benchmark_checklist_rows()
    st.dataframe(checklist, use_container_width=True, hide_index=True, height=240)

with tab_live:
    st.header("Live Charts from Dashboard Data")
    st.caption(
        f"Source: `{dashboard_data_path}` ({len(dashboard_df):,} parsed ESG records). "
        "This view avoids `new_page/results` data sources."
    )
    if dashboard_df.empty:
        st.warning("Dashboard dataset is empty or could not be loaded.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Parsed Records", f"{len(dashboard_df):,}")
        c2.metric("Unique Tones", int(dashboard_df["tone"].nunique()) if "tone" in dashboard_df.columns else "n/a")
        c3.metric("Source Documents", int(dashboard_df["filename"].nunique()) if "filename" in dashboard_df.columns else "n/a")
        c4.metric("Unique Aspects", int(dashboard_df["aspect"].nunique()) if "aspect" in dashboard_df.columns else "n/a")

        live_tabs = st.tabs(["Distribution", "Cross Tabs", "Data Preview"])
        with live_tabs[0]:
            left, right = st.columns(2)
            with left:
                fig_obj, _ = live_figure_data("A.1", dashboard_df)
                if fig_obj is not None:
                    st.plotly_chart(fig_obj, use_container_width=True)
            with right:
                fig_obj, _ = live_figure_data("A.5", dashboard_df)
                if fig_obj is not None:
                    st.plotly_chart(fig_obj, use_container_width=True)
            left, right = st.columns(2)
            with left:
                fig_obj, _ = live_figure_data("A.4", dashboard_df)
                if fig_obj is not None:
                    st.plotly_chart(fig_obj, use_container_width=True)
            with right:
                fig_obj, _ = live_figure_data("A.8", dashboard_df)
                if fig_obj is not None:
                    st.plotly_chart(fig_obj, use_container_width=True)
        with live_tabs[1]:
            fig_obj, _ = live_figure_data("A.7", dashboard_df)
            if fig_obj is not None:
                st.plotly_chart(fig_obj, use_container_width=True)
            fig_obj, _ = live_figure_data("A.10", dashboard_df)
            if fig_obj is not None:
                st.plotly_chart(fig_obj, use_container_width=True)
        with live_tabs[2]:
            st.dataframe(dashboard_df.head(500).astype(str), use_container_width=True, hide_index=True, height=520)
