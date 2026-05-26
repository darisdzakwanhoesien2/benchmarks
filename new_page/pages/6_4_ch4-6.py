from __future__ import annotations

from datetime import datetime
import json
import pickle
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_ROOT = ROOT.parent
SOURCE_DOCX = BENCHMARKS_ROOT / "pages" / "thesis_ch4_6_structure_benchmarks.docx"
UPDATED_DOCX = BENCHMARKS_ROOT / "pages" / "thesis_ch4_6_structure_benchmarks_streamlit_graphs.docx"
GRAPH_DIR = ROOT / "results" / "docx_graph_attachments"
VIS = ROOT / "results" / "visualizations"
TOOLS = ROOT / "tools"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
REV = ROOT / "results" / "revision_analysis"
WORKFLOW = ROOT / "results" / "thesis_workflow_dashboard"
SNAPSHOT_DIR = ROOT / "results" / "ch4_6_frozen_analysis"
SNAPSHOT_GRAPH_DIR = SNAPSHOT_DIR / "graphs"
SNAPSHOT_PATH = SNAPSHOT_DIR / "analysis_snapshot.pkl"
SNAPSHOT_SCHEMA_VERSION = 3
CHAPTER_RESOLUTION_PATH = REV / "chapter_4_6_resolution_board.csv"
CHAPTER_DECISIONS_PATH = REV / "chapter_4_6_resolution_decisions.json"
TONE_DENOMINATOR_AUDIT_PATH = REV / "chapter4_tone_denominator_audit.csv"
TOP_UNMAPPED_ONTOLOGY_PATH = REV / "chapter6_top_unmapped_ontology_candidates.csv"
BENCHMARK_GAP_PATH = REV / "chapter6_benchmark_gap_positioning.csv"

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
    render_mermaid,
    workflow_coverage_chart,
)
from action_plan_status import (  # noqa: E402
    ANNOTATION_PATH,
    SEED_PATH,
    SILVER_PATH,
    action_plan_status_rows,
    build_annotation_table,
    load_csv as action_load_csv,
)
from ground_truth_graphs import (  # noqa: E402
    ensure_ground_truth_graphs,
    ground_truth_attachment_rows,
    ground_truth_source_dataframe,
    t2_consolidated_output_rows,
)


st.set_page_config(page_title="Ch4-6 Benchmarks + DOCX Graphs", layout="wide")


def show_image(path: Path, caption: str | None = None) -> None:
    try:
        st.image(str(path), caption=caption, width="stretch")
    except TypeError:
        st.image(str(path), caption=caption, use_column_width=True)


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
    annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
    seed = load_csv(REV / "pilot_ground_truth_seed.csv")
    silver = load_csv(REV / "silver_tone_ground_truth.csv")
    df = annotation if not annotation.empty else seed
    source = "pilot_ground_truth_annotations.csv" if not annotation.empty else "pilot_ground_truth_seed.csv"
    rows = [
        {"metric": "counted annotation rows", "records": len(df), "source": source},
        {"metric": "saved human annotation rows", "records": len(annotation), "source": "pilot_ground_truth_annotations.csv"},
        {"metric": "pilot seed rows", "records": len(seed), "source": "pilot_ground_truth_seed.csv"},
        {"metric": "silver dataset rows", "records": len(silver), "source": "silver_tone_ground_truth.csv"},
    ]
    for field in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "annotator", "review_notes"]:
        completed = int(df[field].astype(str).str.strip().ne("").sum()) if not df.empty and field in df.columns else 0
        rows.append({"metric": f"{field} completed", "records": completed, "source": source})
    if not df.empty and "ground_truth_tone" in df.columns:
        missing_tone = int(df["ground_truth_tone"].astype(str).str.strip().eq("").sum())
        rows.append({"metric": "ground_truth_tone missing", "records": missing_tone, "source": source})
    if not df.empty and "review_status" in df.columns:
        status_values = df["review_status"].astype(str).str.strip().replace("", "missing")
        for status, count in status_values.value_counts().items():
            rows.append({"metric": f"review_status: {status}", "records": int(count), "source": source})
    return pd.DataFrame(rows)


def repeated_llm_run_rows() -> pd.DataFrame:
    by_run = load_csv(REV / "prompt_stability_by_run.csv")
    if not by_run.empty and {"model", "prompt"}.issubset(by_run.columns):
        view = by_run.copy()
        view["model"] = view["model"].astype(str).str.strip().replace("", "unknown")
        view["prompt"] = (
            view["prompt"]
            .astype(str)
            .str.strip()
            .replace("", "unknown")
            .str.replace(".md", "", regex=False)
            .str.replace("tone_", "", regex=False)
        )
        pivot = (
            view.assign(runs=1)
            .pivot_table(index="model", columns="prompt", values="runs", aggfunc="sum", fill_value=0)
            .astype(int)
        )
        pivot.columns.name = None
        pivot.insert(0, "total", pivot.sum(axis=1))
        return pivot.sort_values("total", ascending=False).reset_index()

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


def chapter_resolution_rows() -> pd.DataFrame:
    rows = load_csv(CHAPTER_RESOLUTION_PATH)
    if not rows.empty:
        return rows
    return pd.DataFrame(
        [
            {
                "chapter": "4",
                "issue": "591 missing tone records",
                "decision": "exclude_from_agreement",
                "evidence": "4,853/5,444 usable tone records",
                "writeup": "Tone agreement and tone-distribution statistics use 4,853 as the effective denominator; the 591 missing tone outputs are reported as data-quality missingness.",
            },
            {
                "chapter": "5",
                "issue": "A.15 ClimateBERT baseline",
                "decision": "frame_as_adjacent_constructs",
                "evidence": "83.7% agreement, kappa=0.645, majority baseline=65.4%",
                "writeup": "Use ClimateBERT as an adjacent construct comparison, not a replacement benchmark.",
            },
            {
                "chapter": "6",
                "issue": "Benchmark gap framing",
                "decision": "claim_combined_indonesian_multi_aspect_tone_niche",
                "evidence": "Existing benchmarks do not cover Indonesian + multi-aspect + tone maturity together.",
                "writeup": "Use benchmark gaps as the contribution claim and future-work structure.",
            },
        ]
    )


def tone_denominator_audit_rows() -> pd.DataFrame:
    rows = load_csv(TONE_DENOMINATOR_AUDIT_PATH)
    if not rows.empty:
        return rows
    return pd.DataFrame(
        [
            {"chapter element": "Corpus extraction coverage", "denominator": 5444, "included": 5444, "excluded": 0, "note": "Use for total extracted-record coverage."},
            {"chapter element": "Tone distribution", "denominator": 4853, "included": 4853, "excluded": 591, "note": "Use this denominator in Chapter 4 tone tables and figures."},
            {"chapter element": "Tone agreement / kappa", "denominator": 4853, "included": 4853, "excluded": 591, "note": "Do not compute agreement over missing tone outputs."},
        ]
    )


def top_unmapped_ontology_rows() -> pd.DataFrame:
    rows = load_csv(TOP_UNMAPPED_ONTOLOGY_PATH)
    if not rows.empty:
        return rows
    return ontology_extension_rows()


def benchmark_gap_positioning_rows() -> pd.DataFrame:
    rows = load_csv(BENCHMARK_GAP_PATH)
    if not rows.empty:
        return rows
    return pd.DataFrame(
        [
            {"benchmark": "FinBERT", "reported metric": "F1=97.3%", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no"},
            {"benchmark": "ESG-BERT", "reported metric": "F1=88%", "Indonesian": "no", "multi-aspect": "limited", "tone-labeled disclosure maturity": "no"},
            {"benchmark": "ClimateBERT", "reported metric": "F1=1.16", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no"},
            {"benchmark": "OCR quality audit", "reported metric": "CER/WER missing", "Indonesian": "pending", "multi-aspect": "n/a", "tone-labeled disclosure maturity": "n/a"},
            {"benchmark": "Repeated LLM runs", "reported metric": "partial coverage", "Indonesian": "partial", "multi-aspect": "partial", "tone-labeled disclosure maturity": "partial"},
            {"benchmark": "ClimateBERT formal label-match F1", "reported metric": "not computed (proxy kappa=0.645)", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no"},
            {"benchmark": "This thesis", "reported metric": "prototype system", "Indonesian": "yes", "multi-aspect": "yes", "tone-labeled disclosure maturity": "yes"},
        ]
    )


def benchmark_gap_chart_rows() -> pd.DataFrame:
    df = benchmark_gap_positioning_rows()
    if df.empty:
        return df
    out = df.copy()
    coverage_cols = [
        "handles finance/ESG language",
        "Indonesian",
        "multi-aspect",
        "tone-labeled disclosure maturity",
    ]
    available = [col for col in coverage_cols if col in out.columns]
    for col in available:
        out[col] = out[col].astype(str).str.lower().map({"yes": 1.0, "limited": 0.5, "partial": 0.5}).fillna(0.0)
    out["combined_capability_score"] = out[available].sum(axis=1) if available else 0
    return out


def action_plan_integration_rows() -> pd.DataFrame:
    checks = [
        {
            "integration item": "Chapter 4-6 resolution board",
            "required in Action Plan": str(CHAPTER_RESOLUTION_PATH.relative_to(ROOT)),
            "used by 6_4 page": "chapter_resolution_rows()",
            "status": "Done" if CHAPTER_RESOLUTION_PATH.exists() else "Needed",
            "next action": "Open Action Plan resolution board and save artifacts.",
        },
        {
            "integration item": "Tone denominator audit",
            "required in Action Plan": str(TONE_DENOMINATOR_AUDIT_PATH.relative_to(ROOT)),
            "used by 6_4 page": "tone_denominator_audit_rows()",
            "status": "Done" if TONE_DENOMINATOR_AUDIT_PATH.exists() else "Needed",
            "next action": "Save Chapter 4 denominator decision in Action Plan.",
        },
        {
            "integration item": "Top unmapped ontology candidates",
            "required in Action Plan": str(TOP_UNMAPPED_ONTOLOGY_PATH.relative_to(ROOT)),
            "used by 6_4 page": "A.16 backing table",
            "status": "Done" if TOP_UNMAPPED_ONTOLOGY_PATH.exists() else "Needed",
            "next action": "Save A.12/A.16 ontology continuation and resolution artifacts.",
        },
        {
            "integration item": "Benchmark gap positioning",
            "required in Action Plan": str(BENCHMARK_GAP_PATH.relative_to(ROOT)),
            "used by 6_4 page": "Chapter 6 contribution table",
            "status": "Done" if BENCHMARK_GAP_PATH.exists() else "Needed",
            "next action": "Save Chapter 6 benchmark gap table from Action Plan.",
        },
    ]
    return pd.DataFrame(checks)


def ontology_extension_rows() -> pd.DataFrame:
    top_unmapped = load_csv(TOP_UNMAPPED_ONTOLOGY_PATH)
    if not top_unmapped.empty:
        out = top_unmapped.copy()
        if "records" in out.columns:
            out["records"] = pd.to_numeric(out["records"], errors="coerce").fillna(0)
        return out.sort_values("records", ascending=False).head(20)
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
    source = "pilot_ground_truth_annotations.csv" if not annotation.empty else "pilot_ground_truth_seed.csv"
    if df.empty:
        return pd.DataFrame()
    rows = []
    for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "annotator", "review_notes"]:
        if col in df.columns:
            done = int(df[col].astype(str).str.strip().ne("").sum())
            rows.append({"field": col, "completed": done, "missing": len(df) - done, "total": len(df), "source": source})
    if "review_status" in df.columns:
        status_values = df["review_status"].astype(str).str.strip().replace("", "missing")
        for status, count in status_values.value_counts().items():
            rows.append({"field": f"review_status: {status}", "completed": int(count), "missing": 0, "total": len(df), "source": source})
    return pd.DataFrame(rows)


def normalize_tone_label(value) -> str:
    text = str(value or "").strip().lower()
    if text in {"", "missing", "none", "nan", "null", "unknown", "no tone", "not_applicable", "n/a"}:
        return "none"
    return text


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
    view = df.assign(
        truth=df[truth_col].map(normalize_tone_label),
        prediction=df[pred_col].map(normalize_tone_label),
    )
    pivot = pd.crosstab(view["truth"], view["prediction"])
    order = [label for label in ["action", "commitment", "outcome", "none"] if label in set(pivot.index) | set(pivot.columns)]
    if order:
        pivot = pivot.reindex(index=order, columns=order, fill_value=0)
    pivot.index.name = "truth"
    pivot.columns.name = None
    pivot["total"] = pivot.sum(axis=1)
    return pivot.reset_index()


def ground_truth_t2_output_rows() -> pd.DataFrame:
    return t2_consolidated_output_rows()


def ground_truth_t2_output_chart_rows() -> pd.DataFrame:
    rows = ground_truth_t2_output_rows()
    if rows.empty:
        return rows
    required = ["rule_tone", "tone_pred", "sentiment_pred"]
    if not set(required).issubset(rows.columns):
        return rows
    out = rows.copy()
    out["output_group"] = (
        "Rule: "
        + out["rule_tone"].astype(str)
        + " | Hybrid: "
        + out["tone_pred"].astype(str)
        + " | Sentiment: "
        + out["sentiment_pred"].astype(str)
    )
    return out


def coalesce_text_columns(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    candidates = []
    for col in columns:
        if col in df.columns:
            candidates.append(df[col].astype(str).str.strip())
    if not candidates:
        return pd.Series([""] * len(df), index=df.index, dtype=str)
    stacked = pd.concat(candidates, axis=1)
    return stacked.replace("", pd.NA).bfill(axis=1).iloc[:, 0].fillna("").astype(str)


def full_action_plan_records() -> pd.DataFrame:
    """Use the same full annotation/silver source family as the Action Plan counters."""
    silver = action_load_csv(SILVER_PATH)
    seed = action_load_csv(SEED_PATH)
    annotations = action_load_csv(ANNOTATION_PATH)
    full = build_annotation_table(silver, seed, annotations)
    if full.empty:
        full = load_csv(VIS / "tone_records_flat.csv")
    if full.empty:
        return pd.DataFrame()
    out = full.copy()
    out["tone_label"] = coalesce_text_columns(out, ["ground_truth_tone", "silver_tone_ground_truth", "tone_pred", "tone"])
    out["esg_label"] = coalesce_text_columns(out, ["ground_truth_esg", "esg"])
    out["aspect_label"] = coalesce_text_columns(out, ["ground_truth_aspect", "aspect"])
    return out


def full_tone_distribution_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty:
        return pd.DataFrame()
    tone = df["tone_label"].astype(str).str.strip()
    tone = tone[tone.ne("")]
    return tone.value_counts().rename_axis("tone").reset_index(name="records")


def full_tone_esg_crosstab_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty:
        return pd.DataFrame()
    view = df[(df["tone_label"].astype(str).str.strip().ne("")) & (df["esg_label"].astype(str).str.strip().ne(""))]
    if view.empty:
        return pd.DataFrame()
    pivot = pd.crosstab(view["tone_label"], view["esg_label"])
    pivot.index.name = "tone"
    pivot.columns.name = None
    return pivot.reset_index()


def full_aspect_tone_crosstab_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty:
        return pd.DataFrame()
    view = df[(df["aspect_label"].astype(str).str.strip().ne("")) & (df["tone_label"].astype(str).str.strip().ne(""))]
    if view.empty:
        return pd.DataFrame()
    pivot = pd.crosstab(view["aspect_label"], view["tone_label"])
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False).drop(columns=["total"])
    pivot.index.name = "aspect"
    pivot.columns.name = None
    return pivot.reset_index()


def aspect_cooccurrence_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty or "aspect_label" not in df.columns:
        return pd.DataFrame()
    group_col = "target" if "target" in df.columns else ("company" if "company" in df.columns else "")
    if not group_col:
        return pd.DataFrame()
    rows = []
    for group, sub in df.groupby(group_col, dropna=False):
        aspects = sorted({str(v).strip().lower() for v in sub["aspect_label"] if str(v).strip()})
        for i, left in enumerate(aspects):
            for right in aspects[i + 1 :]:
                rows.append({"aspect_a": left, "aspect_b": right, "records": 1})
    if not rows:
        return pd.DataFrame()
    return (
        pd.DataFrame(rows)
        .groupby(["aspect_a", "aspect_b"], dropna=False)["records"]
        .sum()
        .reset_index()
        .sort_values("records", ascending=False)
        .head(40)
    )


def aspect_centrality_rows() -> pd.DataFrame:
    edges = aspect_cooccurrence_rows()
    freq = full_action_plan_records()
    if edges.empty:
        return pd.DataFrame()
    degree = {}
    for _, row in edges.iterrows():
        weight = float(row["records"])
        degree[row["aspect_a"]] = degree.get(row["aspect_a"], 0.0) + weight
        degree[row["aspect_b"]] = degree.get(row["aspect_b"], 0.0) + weight
    out = pd.DataFrame([{"aspect": aspect, "weighted_degree": weight} for aspect, weight in degree.items()])
    if not freq.empty and "aspect_label" in freq.columns:
        counts = freq["aspect_label"].astype(str).str.lower().str.strip().value_counts().rename_axis("aspect").reset_index(name="frequency")
        out = out.merge(counts, on="aspect", how="left")
    out["frequency"] = pd.to_numeric(out.get("frequency", 0), errors="coerce").fillna(0)
    out["centrality_score"] = out["weighted_degree"] + out["frequency"]
    return out.sort_values("centrality_score", ascending=False).head(30)


def aspect_importance_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty:
        return pd.DataFrame()
    view = df[df["aspect_label"].astype(str).str.strip().ne("")].copy()
    if view.empty:
        return pd.DataFrame()
    view["tone_norm"] = view["tone_label"].map(normalize_tone_label)
    summary = (
        view.groupby("aspect_label", dropna=False)
        .agg(
            records=("aspect_label", "size"),
            commitment=("tone_norm", lambda s: int(s.eq("commitment").sum())),
            action=("tone_norm", lambda s: int(s.eq("action").sum())),
            outcome=("tone_norm", lambda s: int(s.eq("outcome").sum())),
            none=("tone_norm", lambda s: int(s.eq("none").sum())),
        )
        .reset_index()
        .rename(columns={"aspect_label": "aspect"})
    )
    centrality = aspect_centrality_rows()[["aspect", "weighted_degree"]] if not aspect_centrality_rows().empty else pd.DataFrame(columns=["aspect", "weighted_degree"])
    summary["aspect"] = summary["aspect"].astype(str).str.lower().str.strip()
    summary = summary.merge(centrality, on="aspect", how="left")
    summary["weighted_degree"] = pd.to_numeric(summary["weighted_degree"], errors="coerce").fillna(0)
    summary["non_outcome_intensity"] = (summary["commitment"] + summary["action"] + summary["none"]) / summary["records"].clip(lower=1)
    summary["importance_score"] = (summary["records"] * (1 + summary["non_outcome_intensity"]) + summary["weighted_degree"]).round(3)
    return summary.sort_values("importance_score", ascending=False).head(30)


def aspect_tone_dynamics_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty:
        return pd.DataFrame()
    view = df[df["aspect_label"].astype(str).str.strip().ne("")].copy()
    if view.empty:
        return pd.DataFrame()
    view["aspect"] = view["aspect_label"].astype(str).str.lower().str.strip()
    view["tone_norm"] = view["tone_label"].map(normalize_tone_label)
    rows = []
    for aspect, sub in view.groupby("aspect"):
        counts = sub["tone_norm"].value_counts()
        total = int(counts.sum())
        dominant = str(counts.index[0]) if total else ""
        dominant_share = float(counts.iloc[0] / total) if total else 0
        rows.append(
            {
                "aspect": aspect,
                "records": total,
                "dominant_tone": dominant,
                "dominant_share": round(dominant_share, 4),
                "polarization": round(1 - dominant_share, 4),
                "tone_diversity": int(counts.size),
            }
        )
    return pd.DataFrame(rows).sort_values(["polarization", "records"], ascending=False).head(30)


def aspect_entity_comparison_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty or "company" not in df.columns:
        return pd.DataFrame()
    view = df[df["aspect_label"].astype(str).str.strip().ne("")].copy()
    if view.empty:
        return pd.DataFrame()
    top_aspects = view["aspect_label"].astype(str).str.lower().str.strip().value_counts().head(10).index.tolist()
    view["aspect"] = view["aspect_label"].astype(str).str.lower().str.strip()
    view = view[view["aspect"].isin(top_aspects)]
    pivot = pd.crosstab(view["company"].astype(str).str[:42], view["aspect"])
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False).head(20).drop(columns=["total"])
    pivot.index.name = "company"
    pivot.columns.name = None
    return pivot.reset_index()


def aspect_temporal_evolution_rows() -> pd.DataFrame:
    df = full_action_plan_records()
    if df.empty:
        return pd.DataFrame()
    view = df[df["aspect_label"].astype(str).str.strip().ne("")].copy()
    if view.empty:
        return pd.DataFrame()
    timestamp = pd.to_datetime(view.get("timestamp", ""), errors="coerce")
    view["year"] = timestamp.dt.year
    if view["year"].isna().all():
        extracted = view.get("target", pd.Series([""] * len(view))).astype(str).str.extract(r"(20\d{2})")[0]
        view["year"] = pd.to_numeric(extracted, errors="coerce")
    view["year"] = view["year"].fillna(0).astype(int).astype(str).replace("0", "unknown")
    top_aspects = view["aspect_label"].astype(str).str.lower().str.strip().value_counts().head(10).index.tolist()
    view["aspect"] = view["aspect_label"].astype(str).str.lower().str.strip()
    view = view[view["aspect"].isin(top_aspects)]
    pivot = pd.crosstab(view["year"], view["aspect"])
    pivot.index.name = "year"
    pivot.columns.name = None
    return pivot.reset_index()


def aspect_ontology_matrix_rows() -> pd.DataFrame:
    ontology = load_csv(REV / "ontology_coverage.csv")
    if ontology.empty:
        return pd.DataFrame()
    df = ontology.copy()
    df["mapped"] = df.get("mapped_to_ontology", False).astype(str).str.lower().isin(["true", "1", "yes"]).map({True: "mapped", False: "novel"})
    return (
        df.groupby(["mapped", "suggested_path"], dropna=False)["records"]
        .sum()
        .reset_index()
        .sort_values("records", ascending=False)
        .head(30)
    )


def load_action_plan_llm_records() -> pd.DataFrame:
    """Mirror the Action Plan PDF x prompt matrix source without importing the page."""
    rows: list[dict[str, object]] = []
    esg_path = ROOT / "results" / "esg_records.json"
    if esg_path.exists():
        try:
            data = json.loads(esg_path.read_text(encoding="utf-8"))
        except Exception:
            data = []
        if isinstance(data, list):
            for run in data:
                if not isinstance(run, dict):
                    continue
                records = run.get("records") if isinstance(run.get("records"), list) else []
                target = str(run.get("target", "") or "")
                rows.append(
                    {
                        "target_doc": target.split("/")[0] or "unknown",
                        "target": target,
                        "prompt": str(run.get("prompt", "") or "unknown"),
                        "model": str(run.get("model", "") or ""),
                        "ok": bool(run.get("ok")),
                        "records_count": len(records),
                    }
                )

    flat = load_csv(VIS / "tone_records_flat.csv")
    if not flat.empty and "prompt" in flat.columns:
        if "target_doc" not in flat.columns:
            flat["target_doc"] = flat.get("target", pd.Series(["unknown"] * len(flat))).astype(str).str.split("/").str[0]
        group_cols = [col for col in ["target_doc", "target", "prompt", "model"] if col in flat.columns]
        if group_cols:
            grouped = flat.groupby(group_cols, dropna=False).size().reset_index(name="records_count")
            grouped["ok"] = grouped["records_count"].gt(0)
            rows.extend(grouped.to_dict("records"))
    return pd.DataFrame(rows)


def pdf_prompt_matrix_rows(metric: str = "Extracted records") -> pd.DataFrame:
    """Pivot table from Action Plan logic: rows = PDF, columns = prompts."""
    records = load_action_plan_llm_records()
    required = {"target_doc", "prompt", "records_count"}
    if records.empty or not required.issubset(records.columns):
        return pd.DataFrame()
    records = records.copy()
    records["target_doc"] = records["target_doc"].astype(str).str.strip().replace("", "unknown")
    records["prompt"] = records["prompt"].astype(str).str.strip().replace("", "unknown")
    records["ok"] = records["ok"].fillna(False).astype(bool) if "ok" in records.columns else True
    records["records_count"] = pd.to_numeric(records["records_count"], errors="coerce").fillna(0).astype(int)

    if metric == "Runs / batches":
        grouped = records.groupby(["target_doc", "prompt"], dropna=False).size().reset_index(name="value")
    elif metric == "Successful runs":
        grouped = records[records["ok"]].groupby(["target_doc", "prompt"], dropna=False).size().reset_index(name="value")
    else:
        grouped = records.groupby(["target_doc", "prompt"], dropna=False)["records_count"].sum().reset_index(name="value")
    if grouped.empty:
        return pd.DataFrame()

    pivot = grouped.pivot_table(index="target_doc", columns="prompt", values="value", aggfunc="sum", fill_value=0).astype(int)
    pivot.columns = [str(c).replace(".md", "").replace("tone_", "") for c in pivot.columns]
    pivot.columns.name = None
    pivot.index.name = "target_doc"
    pivot.insert(0, "total", pivot.sum(axis=1))
    pivot = pivot.sort_values("total", ascending=False)
    return pivot.reset_index()


def ensure_extra_graph_attachments() -> None:
    ensure_ground_truth_graphs()
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_full_tone_distribution.png",
        "Full Tone Distribution",
        full_tone_distribution_rows(),
        "tone",
        "records",
        "Uses Action Plan full silver/annotation labels, not the older 332-row visualization snapshot",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "docx_full_esg_by_tone.png",
        "Full ESG × Tone Matrix",
        full_tone_esg_crosstab_rows(),
        "Rows are tone labels; columns are ESG labels from the full Action Plan evidence table",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "docx_full_aspect_by_tone_heatmap.png",
        "Full Aspect × Tone Matrix",
        full_aspect_tone_crosstab_rows(),
        "Top rows by total aspect frequency from the full Action Plan evidence table",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_human_annotation_agreement.png",
        "Human Annotation Agreement Readiness",
        human_annotation_agreement_rows(),
        "metric",
        "records",
        "Current ground-truth completion and pilot review status",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "docx_repeated_llm_runs.png",
        "Repeated LLM Runs Grid",
        repeated_llm_run_rows(),
        "Rows are models; columns are prompt templates; cells are run/batch counts",
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
        "Top unmapped Indonesian ESG aspects from the Action Plan Chapter 6 resolution artifact",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_chapter4_tone_denominator_audit.png",
        "Chapter 4 Tone Denominator Audit",
        tone_denominator_audit_rows(),
        "chapter element",
        "denominator",
        "Action Plan decision: tone agreement/distribution uses the effective denominator, not the extraction denominator",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_chapter6_benchmark_gap_positioning.png",
        "Chapter 6 Benchmark Gap Positioning",
        benchmark_gap_chart_rows(),
        "benchmark",
        "combined_capability_score",
        "Which benchmarks cover the combined Indonesian multi-aspect tone-labelling niche",
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
    draw_docx_table_heatmap(
        GRAPH_DIR / "docx_ground_truth_tone_comparison.png",
        "Ground Truth Tone Truth × Prediction",
        ground_truth_tone_comparison_rows(),
        "missing, blank, unknown, and none are normalized to none",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "docx_ground_truth_t2_outputs.png",
        "ground_truth.py T2 Tone Outputs",
        ground_truth_t2_output_chart_rows(),
        "output_group",
        "records",
        "Flattened T2 output with blank/unknown labels consolidated as Unclassified / Unknown",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "docx_pdf_prompt_matrix.png",
        "PDF × Prompt Coverage Matrix",
        pdf_prompt_matrix_rows("Extracted records"),
        "Records extracted per source PDF × prompt template combination",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "aspect_cooccurrence_edges.png",
        "Aspect Co-occurrence Graph Edges",
        aspect_cooccurrence_rows().assign(edge=lambda d: d["aspect_a"].astype(str) + " + " + d["aspect_b"].astype(str)) if not aspect_cooccurrence_rows().empty else pd.DataFrame(),
        "edge",
        "records",
        "Aspect pairs that appear in the same document/source target",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "aspect_network_centrality.png",
        "Aspect Network Centrality",
        aspect_centrality_rows(),
        "aspect",
        "centrality_score",
        "Frequency plus weighted co-occurrence degree",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "aspect_importance_scores.png",
        "Aspect Importance Scores",
        aspect_importance_rows(),
        "aspect",
        "importance_score",
        "Frequency, non-outcome intensity, and graph connectivity",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "aspect_tone_dynamics.png",
        "Aspect-Tone Dynamics",
        aspect_tone_dynamics_rows(),
        "aspect",
        "polarization",
        "Higher values mean tone is more mixed across the aspect",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "aspect_entity_comparison.png",
        "Cross-Entity Aspect Comparison",
        aspect_entity_comparison_rows(),
        "Companies compared by their dominant aspect profiles",
    )
    draw_docx_table_heatmap(
        GRAPH_DIR / "aspect_temporal_evolution.png",
        "Temporal Aspect Evolution",
        aspect_temporal_evolution_rows(),
        "Top aspects by detected year from timestamp/source target",
    )
    draw_docx_bar_chart(
        GRAPH_DIR / "aspect_ontology_coverage_paths.png",
        "Aspect Ontology Coverage",
        aspect_ontology_matrix_rows(),
        "suggested_path",
        "records",
        "Mapped versus novel ESG vocabulary paths",
    )


def graph_manifest() -> pd.DataFrame:
    rows = [
        {
            "figure": "A.1",
            "title": "Full tone distribution",
            "path": GRAPH_DIR / "docx_full_tone_distribution.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv",
            "source page": "pages/3_0_Thesis_Action_Plan.py",
        },
        {
            "figure": "A.2",
            "title": "Full ESG by tone",
            "path": GRAPH_DIR / "docx_full_esg_by_tone.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv",
            "source page": "pages/3_0_Thesis_Action_Plan.py",
        },
        {
            "figure": "A.3",
            "title": "Full aspect by tone heatmap",
            "path": GRAPH_DIR / "docx_full_aspect_by_tone_heatmap.png",
            "chapter": "Chapter 4",
            "rq": "RQ2",
            "source table": "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv",
            "source page": "pages/3_0_Thesis_Action_Plan.py",
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
            "source table": "prompt_stability_by_run.csv",
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
            "source table": "chapter6_top_unmapped_ontology_candidates.csv",
            "source page": "pages/3_0_Thesis_Action_Plan.py",
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
            "rq": "RQ1 / RQ6",
            "source table": "esg_records.json + tone_records_flat.csv",
            "source page": "pages/3_0_Thesis_Action_Plan.py",
        },
    ]
    rows.extend(
        {
            "figure": figure,
            "title": title,
            "path": path,
            "chapter": chapter,
            "rq": rq,
            "source table": source_table,
            "source page": source_page,
        }
        for figure, title, path, chapter, rq, source_table, source_page in ground_truth_attachment_rows()
    )
    rows.extend(
        [
            {
                "figure": "A.30",
                "title": "Aspect co-occurrence graph",
                "path": GRAPH_DIR / "aspect_cooccurrence_edges.png",
                "chapter": "Chapter 4 / 5",
                "rq": "RQ2 / RQ4",
                "source table": "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv",
                "source page": "pages/6_4_ch4-6.py",
            },
            {
                "figure": "A.31",
                "title": "Aspect network centrality",
                "path": GRAPH_DIR / "aspect_network_centrality.png",
                "chapter": "Chapter 5",
                "rq": "RQ4",
                "source table": "aspect co-occurrence edge list",
                "source page": "pages/6_4_ch4-6.py",
            },
            {
                "figure": "A.32",
                "title": "Aspect importance scoring",
                "path": GRAPH_DIR / "aspect_importance_scores.png",
                "chapter": "Chapter 4 / 5",
                "rq": "RQ2 / RQ4",
                "source table": "full Action Plan evidence table",
                "source page": "pages/6_4_ch4-6.py",
            },
            {
                "figure": "A.33",
                "title": "Aspect-tone dynamics",
                "path": GRAPH_DIR / "aspect_tone_dynamics.png",
                "chapter": "Chapter 5",
                "rq": "RQ4",
                "source table": "full Action Plan evidence table",
                "source page": "pages/6_4_ch4-6.py",
            },
            {
                "figure": "A.34",
                "title": "Cross-entity aspect comparison",
                "path": GRAPH_DIR / "aspect_entity_comparison.png",
                "chapter": "Chapter 4 / 5",
                "rq": "RQ2 / RQ4",
                "source table": "full Action Plan evidence table",
                "source page": "pages/6_4_ch4-6.py",
            },
            {
                "figure": "A.35",
                "title": "Temporal aspect evolution",
                "path": GRAPH_DIR / "aspect_temporal_evolution.png",
                "chapter": "Chapter 5",
                "rq": "RQ4",
                "source table": "full Action Plan evidence table",
                "source page": "pages/6_4_ch4-6.py",
            },
            {
                "figure": "A.36",
                "title": "Aspect ontology coverage paths",
                "path": GRAPH_DIR / "aspect_ontology_coverage_paths.png",
                "chapter": "Chapter 5 / 6",
                "rq": "RQ4",
                "source table": "ontology_coverage.csv",
                "source page": "pages/1_6_Ontology_Path_Viewer.py",
            },
            {
                "figure": "A.37",
                "title": "Chapter 4 tone denominator audit",
                "path": GRAPH_DIR / "docx_chapter4_tone_denominator_audit.png",
                "chapter": "Chapter 4",
                "rq": "RQ2 / RQ3",
                "source table": "chapter4_tone_denominator_audit.csv",
                "source page": "pages/3_0_Thesis_Action_Plan.py",
            },
            {
                "figure": "A.38",
                "title": "Chapter 6 benchmark gap positioning",
                "path": GRAPH_DIR / "docx_chapter6_benchmark_gap_positioning.png",
                "chapter": "Chapter 6",
                "rq": "RQ6",
                "source table": "chapter6_benchmark_gap_positioning.csv",
                "source page": "pages/3_0_Thesis_Action_Plan.py",
            },
        ]
    )
    df = pd.DataFrame(rows)
    df["exists"] = df["path"].map(lambda p: Path(p).exists())
    df["path"] = df["path"].astype(str)
    return add_source_table_descriptions(df)


def describe_source_table(source_table: object) -> str:
    text = str(source_table or "").strip()
    normalized = text.lower()
    descriptions = {
        "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv": (
            "Merged full evidence table combining silver tone labels with any saved pilot human annotations; "
            "used for tone, ESG, aspect, and aspect-network summaries."
        ),
        "tone_climatebert_label_crosstab.csv": (
            "Crosstab of ABSA tone predictions against ClimateBERT climate label outputs; "
            "used to inspect proxy agreement patterns."
        ),
        "climatebert_remote_flat.csv": (
            "Flattened ClimateBERT remote-run outputs with record-level scores and labels; "
            "used for top-scoring ClimateBERT examples."
        ),
        "DOCX evidence summary": (
            "Derived summary of the source and graph-attached DOCX files, embedded media count, "
            "and key evidence snapshot metrics."
        ),
        "chapter-to-RQ mapping": (
            "Hand-curated mapping from thesis chapters and Streamlit pages to research questions and figure usage."
        ),
        "benchmark checklist": (
            "Checklist of remaining benchmark evidence needed for stronger thesis claims, including OCR quality, "
            "human agreement, repeated runs, ClimateBERT baseline, and ontology extension."
        ),
        "graph manifest": (
            "Attachment register listing each figure, title, chapter, RQ, backing source table, source page, "
            "file path, and file-existence status."
        ),
        "model_stability_summary.csv": (
            "Model-level run summary with parse success and stability metrics used for model benchmark figures."
        ),
        "prompt_stability_summary.csv": (
            "Prompt-template stability summary, including missing-tone and related prompt sensitivity metrics."
        ),
        "ontology_coverage.csv": (
            "Aspect ontology coverage table showing mapped versus unmapped ESG vocabulary and suggested paths."
        ),
        "chapter_4_6_resolution_board.csv": (
            "Action Plan resolution board that records the Chapter 4-6 decisions, evidence, and ready-to-use thesis write-up text."
        ),
        "chapter4_tone_denominator_audit.csv": (
            "Action Plan denominator audit showing where to use 5,444 extraction records versus 4,853 usable tone records."
        ),
        "chapter6_top_unmapped_ontology_candidates.csv": (
            "Action Plan A.16/Chapter 6 backing table for high-frequency unmapped aspects and suggested GRI/SASB/TCFD placement."
        ),
        "chapter6_benchmark_gap_positioning.csv": (
            "Action Plan benchmark gap table positioning this thesis against FinBERT, ESG-BERT, SpanEval, ClimateBERT, and GH-ABSA."
        ),
        "pilot_ground_truth_seed.csv + silver_tone_ground_truth.csv": (
            "Pilot annotation seed joined with silver labels to summarize ground-truth readiness and agreement coverage."
        ),
        "model_stability_summary.csv + prompt_stability_summary.csv": (
            "Combined model and prompt run summaries used to count repeated LLM benchmark coverage."
        ),
        "prompt_stability_by_run.csv": (
            "Run-level LLM processing table; A.14 pivots it into a model-by-prompt grid where each cell counts runs or batches."
        ),
        "climatebert_proxy_agreement_summary.csv + climatebert_proxy_agreement_records.csv": (
            "ClimateBERT proxy comparison artifacts: aggregate agreement metrics plus record-level agreement evidence."
        ),
        "tone_records_flat.csv + silver_tone_ground_truth.csv": (
            "Flattened ABSA tone records combined with silver labels to show ground-truth scaffold coverage."
        ),
        "pilot_ground_truth_seed.csv + pilot_ground_truth_annotations.csv": (
            "Pilot annotation seed and saved annotation file used to measure completion of human-labelled fields."
        ),
        "t2_flat_outputs.csv + t2_results.jsonl": (
            "Flattened and raw T2 ground_truth.py outputs used to summarize rule, hybrid, and sentiment tone results."
        ),
        "esg_records.json + tone_records_flat.csv": (
            "Raw ESG extraction runs plus flattened tone records used to build the PDF by prompt coverage matrix."
        ),
        "aspect co-occurrence edge list": (
            "Derived edge table where each row links two aspects that appear in the same document or source target."
        ),
        "full Action Plan evidence table": (
            "Derived full evidence table from the Action Plan annotation pipeline, used for aspect importance, "
            "entity comparison, temporal evolution, and tone dynamics."
        ),
    }
    if text in descriptions:
        return descriptions[text]
    if "ground_truth" in normalized:
        return "Ground-truth source artifact used for human-label coverage, prediction comparison, or validation tables."
    if "tone" in normalized:
        return "Tone-analysis artifact used for ABSA label distributions, crosstabs, or flattened record evidence."
    if "climatebert" in normalized:
        return "ClimateBERT comparison artifact used for climate-label baseline, agreement, or score inspection."
    if "ontology" in normalized:
        return "Ontology artifact used to evaluate mapped and novel ESG aspect vocabulary."
    if "model" in normalized or "prompt" in normalized:
        return "Stability benchmark artifact used to evaluate model or prompt-level processing behavior."
    return "Backing source artifact used to reproduce or inspect this graph attachment."


def add_source_table_descriptions(manifest_df: pd.DataFrame) -> pd.DataFrame:
    out = manifest_df.copy()
    if "source table" in out.columns:
        out["source table description"] = out["source table"].map(describe_source_table)
    return out


def mermaid_label(value: object, max_len: int = 58) -> str:
    text = str(value or "").replace("\n", " ").strip()
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return (
        text.replace("\\", "\\\\")
        .replace('"', "'")
        .replace("[", "(")
        .replace("]", ")")
        .replace("{", "(")
        .replace("}", ")")
    )


def mermaid_node_id(prefix: str, value: object, index: int | None = None) -> str:
    import re

    base = re.sub(r"[^A-Za-z0-9_]+", "_", str(value or "").strip()).strip("_")
    if not base:
        base = "unknown"
    if base[0].isdigit():
        base = f"n_{base}"
    suffix = f"_{index}" if index is not None else ""
    return f"{prefix}_{base[:44]}{suffix}"


def graph_attachment_cluster_mermaid(rows: pd.DataFrame) -> str:
    """Build a 5-cluster Mermaid map from graph attachment metadata.

    Clusters:
    1. figure-title node, e.g. A.1 - Full tone distribution
    2. chapter
    3. RQ
    4. source table
    5. source page
    """
    if rows.empty:
        return "flowchart LR\n  EMPTY[\"No selected graph attachments\"]"

    plot = rows[["figure", "title", "chapter", "rq", "source table", "source page"]].drop_duplicates().reset_index(drop=True)
    lines = [
        "flowchart LR",
        '  subgraph FIGS["1. Figure - title"]',
    ]
    figure_ids: list[str] = []
    class_nodes: dict[str, list[str]] = {"figure": [], "chapter": [], "rq": [], "table": [], "page": []}
    for idx, row in plot.iterrows():
        node_id = mermaid_node_id("FIG", row["figure"], idx)
        figure_ids.append(node_id)
        class_nodes["figure"].append(node_id)
        lines.append(f'    {node_id}["{mermaid_label(row["figure"])} - {mermaid_label(row["title"], 70)}"]')
    lines.append("  end")

    cluster_specs = [
        ("CH", "2. Chapter", "chapter"),
        ("RQ", "3. Research question", "rq"),
        ("SRC_TABLE", "4. Source table", "source table"),
        ("SRC_PAGE", "5. Source page", "source page"),
    ]
    value_to_id: dict[tuple[str, str], str] = {}
    for prefix, title, column in cluster_specs:
        lines.append(f'  subgraph {prefix}S["{title}"]')
        values = sorted({str(v) for v in plot[column].fillna("").astype(str).tolist() if str(v).strip()})
        for idx, value in enumerate(values):
            node_id = mermaid_node_id(prefix, value, idx)
            value_to_id[(column, value)] = node_id
            if column == "chapter":
                class_nodes["chapter"].append(node_id)
            elif column == "rq":
                class_nodes["rq"].append(node_id)
            elif column == "source table":
                class_nodes["table"].append(node_id)
            elif column == "source page":
                class_nodes["page"].append(node_id)
            lines.append(f'    {node_id}["{mermaid_label(value, 72)}"]')
        lines.append("  end")

    for idx, row in plot.iterrows():
        fig_id = figure_ids[idx]
        for column, label in [
            ("chapter", "chapter"),
            ("rq", "rq"),
            ("source table", "table"),
            ("source page", "page"),
        ]:
            value = str(row[column])
            target = value_to_id.get((column, value))
            if target:
                lines.append(f'  {fig_id} -- "{label}" --> {target}')

    lines.extend(
        [
            "  classDef figure fill:#eef6f4,stroke:#2f6f73,stroke-width:1px,color:#173f42;",
            "  classDef chapter fill:#fff7e6,stroke:#b7791f,color:#4a2f00;",
            "  classDef rq fill:#eef2ff,stroke:#4f46e5,color:#1e1b4b;",
            "  classDef table fill:#f0fdf4,stroke:#16a34a,color:#052e16;",
            "  classDef page fill:#fdf2f8,stroke:#db2777,color:#500724;",
        ]
    )
    for class_name, nodes in class_nodes.items():
        if nodes:
            lines.append(f"  class {','.join(nodes)} {class_name};")
    return "\n".join(lines)


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def source_dataframe_for_figure(row: pd.Series, bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    figure = str(row["figure"])
    if figure == "A.1":
        return full_tone_distribution_rows()
    if figure == "A.2":
        return full_tone_esg_crosstab_rows()
    if figure == "A.3":
        return full_aspect_tone_crosstab_rows()
    if figure == "A.4":
        full_a4 = load_csv(VIS / "tone_climatebert_label_crosstab_full.csv")
        if not full_a4.empty:
            return full_a4
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
        columns = ["figure", "title", "chapter", "rq", "source table", "source table description", "source page", "exists"]
        return graph_manifest()[columns]
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
    if figure in {f"A.{idx}" for idx in range(22, 30)}:
        return ground_truth_source_dataframe(figure)
    if figure == "A.30":
        return aspect_cooccurrence_rows()
    if figure == "A.31":
        return aspect_centrality_rows()
    if figure == "A.32":
        return aspect_importance_rows()
    if figure == "A.33":
        return aspect_tone_dynamics_rows()
    if figure == "A.34":
        return aspect_entity_comparison_rows()
    if figure == "A.35":
        return aspect_temporal_evolution_rows()
    if figure == "A.36":
        return aspect_ontology_matrix_rows()
    if figure == "A.37":
        return tone_denominator_audit_rows()
    if figure == "A.38":
        return benchmark_gap_positioning_rows()
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
            {
                "metric": "Tone denominator decision",
                "value": "4,853 / 5,444",
                "existing data": "chapter4_tone_denominator_audit.csv",
                "redirect page": "pages/3_0_Thesis_Action_Plan.py",
            },
            {
                "metric": "Chapter resolution rows",
                "value": f"{len(chapter_resolution_rows()):,}",
                "existing data": "chapter_4_6_resolution_board.csv",
                "redirect page": "pages/3_0_Thesis_Action_Plan.py",
            },
        ]
    )


def chapter_mapping_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "chapter": "Chapter 4 - Implementation and Results",
                "streamlit page": "pages/6_1_Chapter_4_Implementation_Results.py",
                "primary evidence": "tone records, PDF x prompt matrix, tone/ESG distributions, denominator audit, ClimateBERT crosstab, artifact/model/prompt stability",
                "figures": "A.1, A.2, A.3, A.4, A.7, A.8, A.10, A.19, A.37",
            },
            {
                "chapter": "Chapter 5 - Discussion",
                "streamlit page": "pages/6_2_Chapter_5_Discussion.py",
                "primary evidence": "agreement metrics, ontology coverage, failure modes, prompt/model sensitivity, greenwashing caveat, data.md failed prompt framing",
                "figures": "A.4, A.5, A.11, A.12, A.15, A.29",
            },
            {
                "chapter": "Chapter 6 - Conclusion",
                "streamlit page": "pages/6_3_Chapter_6_Conclusion.py",
                "primary evidence": "contribution summary, RQ answers, artifact inventory, top unmapped ontology candidates, benchmark gap positioning, future-work checklist",
                "figures": "A.6, A.7, A.8, A.9, A.10, A.11, A.12, A.16, A.38",
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


def snapshot_source_paths() -> list[Path]:
    paths = [
        ROOT / "results",
        VIS,
        REV,
        WORKFLOW,
        SOURCE_DOCX,
        UPDATED_DOCX,
        ROOT / "results" / "esg_records.json",
        ROOT / "results" / "t1_results.jsonl",
        ROOT / "results" / "t1_results.json",
        ROOT / "results" / "t2_results.jsonl",
        ROOT / "results" / "t2_results.json",
        VIS / "tone_records_flat.csv",
        VIS / "tone_esg_crosstab.csv",
        VIS / "tone_climatebert_label_crosstab.csv",
        VIS / "climatebert_remote_flat.csv",
        REV / "model_stability_summary.csv",
        REV / "prompt_stability_summary.csv",
        REV / "prompt_stability_by_run.csv",
        REV / "failure_mode_counts.csv",
        REV / "ontology_coverage.csv",
        REV / "climatebert_proxy_agreement_summary.csv",
        REV / "climatebert_proxy_agreement_records.csv",
        REV / "ocr_processing_summary.csv",
        REV / "greenwashing_index_by_company.csv",
        REV / "silver_tone_ground_truth.csv",
        REV / "pilot_ground_truth_seed.csv",
        REV / "pilot_ground_truth_annotations.csv",
        REV / "climatebert_record_batch_import.csv",
        REV / "climatebert_output.csv",
        CHAPTER_RESOLUTION_PATH,
        CHAPTER_DECISIONS_PATH,
        TONE_DENOMINATOR_AUDIT_PATH,
        TOP_UNMAPPED_ONTOLOGY_PATH,
        BENCHMARK_GAP_PATH,
        WORKFLOW / "t2_flat_outputs.csv",
    ]
    return sorted({path.resolve() for path in paths}, key=str)


def source_fingerprint() -> dict[str, dict[str, int | bool]]:
    fingerprint: dict[str, dict[str, int | bool]] = {}
    for path in snapshot_source_paths():
        try:
            stat = path.stat()
        except FileNotFoundError:
            fingerprint[str(path)] = {"exists": False, "mtime_ns": 0, "size": 0}
            continue
        fingerprint[str(path)] = {
            "exists": True,
            "mtime_ns": int(stat.st_mtime_ns),
            "size": int(stat.st_size),
        }
    return fingerprint


def fingerprint_changed(snapshot: dict, current: dict[str, dict[str, int | bool]]) -> bool:
    return snapshot.get("source_fingerprint", {}) != current


def changed_source_count(snapshot: dict, current: dict[str, dict[str, int | bool]]) -> int:
    previous = snapshot.get("source_fingerprint", {})
    return sum(1 for key in set(previous) | set(current) if previous.get(key) != current.get(key))


def format_snapshot_time(snapshot: dict) -> str:
    created_at = str(snapshot.get("created_at", ""))
    if not created_at:
        return "unknown time"
    try:
        return datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return created_at


def load_analysis_snapshot() -> dict | None:
    if not SNAPSHOT_PATH.exists():
        return None
    try:
        with SNAPSHOT_PATH.open("rb") as handle:
            snapshot = pickle.load(handle)
    except Exception:
        return None
    if snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        return None
    required = {"bundle", "manifest", "action_status", "source_tables", "source_fingerprint"}
    return snapshot if required.issubset(snapshot) else None


def save_analysis_snapshot(snapshot: dict) -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    with SNAPSHOT_PATH.open("wb") as handle:
        pickle.dump(snapshot, handle, protocol=pickle.HIGHEST_PROTOCOL)


def freeze_manifest_graph_files(manifest: pd.DataFrame) -> pd.DataFrame:
    frozen = manifest.copy()
    SNAPSHOT_GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    for idx, row in frozen.iterrows():
        source = Path(row["path"])
        target_name = f"{str(row['figure']).replace('.', '_')}_{source.name}"
        target = SNAPSHOT_GRAPH_DIR / target_name
        if source.exists():
            try:
                target.write_bytes(source.read_bytes())
                frozen.at[idx, "path"] = str(target)
                frozen.at[idx, "exists"] = True
            except Exception:
                frozen.at[idx, "exists"] = False
        else:
            frozen.at[idx, "exists"] = False
    return frozen


def build_analysis_snapshot() -> dict:
    frozen_bundle = data_bundle()
    ensure_extra_graph_attachments()
    live_manifest = graph_manifest()
    frozen_manifest = freeze_manifest_graph_files(live_manifest)
    frozen_tables: dict[str, pd.DataFrame] = {}
    for _, row in live_manifest.iterrows():
        frozen_tables[str(row["figure"])] = source_dataframe_for_figure(row, frozen_bundle)
    if not frozen_manifest.empty:
        columns = ["figure", "title", "chapter", "rq", "source table", "source table description", "source page", "exists"]
        frozen_tables["A.9"] = add_source_table_descriptions(frozen_manifest)[columns]
    frozen_tables["chapter_resolution"] = chapter_resolution_rows()
    frozen_tables["action_plan_integration"] = action_plan_integration_rows()
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_fingerprint": source_fingerprint(),
        "bundle": frozen_bundle,
        "manifest": frozen_manifest,
        "action_status": action_plan_status_rows(),
        "source_tables": frozen_tables,
    }


def get_frozen_source_table(row: pd.Series, snapshot: dict, frozen_bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    figure = str(row["figure"])
    if figure in {"A.13", "A.14", "A.18", "A.23"}:
        return add_source_table_descriptions(source_dataframe_for_figure(row, frozen_bundle))
    table = snapshot.get("source_tables", {}).get(figure)
    if isinstance(table, pd.DataFrame):
        return add_source_table_descriptions(table)
    return add_source_table_descriptions(source_dataframe_for_figure(row, frozen_bundle))


snapshot = load_analysis_snapshot()
current_fingerprint = source_fingerprint()

st.title("Ch4-6 Structure Benchmarks and Graph Attachments")
st.caption(
    "Streamlit reader for `thesis_ch4_6_structure_benchmarks.docx`, the updated graph-attached DOCX, "
    "and the frozen evidence used by pages/6_1, pages/6_2, and pages/6_3."
)

refresh_cols = st.columns([1.1, 1.2, 2.7])
refresh_requested = refresh_cols[0].button("Refresh frozen analysis", type="primary", use_container_width=True)
if snapshot is None:
    refresh_cols[1].warning("No frozen snapshot yet.")
elif fingerprint_changed(snapshot, current_fingerprint):
    refresh_cols[1].warning(f"New source data detected in {changed_source_count(snapshot, current_fingerprint)} file(s).")
else:
    refresh_cols[1].success("Frozen data is current.")

if snapshot is None or refresh_requested:
    with st.spinner("Building and saving frozen Ch4-6 analysis snapshot..."):
        snapshot = build_analysis_snapshot()
        save_analysis_snapshot(snapshot)
    st.success(f"Frozen analysis saved to `{SNAPSHOT_PATH}`.")
    current_fingerprint = snapshot["source_fingerprint"]

if snapshot is None:
    st.error("Could not create or load the frozen analysis snapshot.")
    st.stop()

bundle = snapshot["bundle"]
manifest = add_source_table_descriptions(snapshot["manifest"])
action_status = snapshot["action_status"]

refresh_cols[2].caption(
    f"Using snapshot from {format_snapshot_time(snapshot)}. "
    "The page stays on this stored analysis until you press refresh."
)
metric_row(bundle)

st.divider()

doc_cols = st.columns([2, 2, 1, 1])
doc_cols[0].markdown(f"**Source DOCX:** `{SOURCE_DOCX}`")
doc_cols[1].markdown(f"**Updated DOCX:** `{UPDATED_DOCX}`")
doc_cols[2].metric("Embedded graphs", media_count(UPDATED_DOCX))
doc_cols[3].metric("Graph files", int(manifest["exists"].sum()) if "exists" in manifest.columns else 0)

st.subheader("Thesis Action Plan Frozen Status")
status_cols = st.columns(len(action_status) if not action_status.empty else 1)
for idx, (_, row) in enumerate(action_status.iterrows()):
    with status_cols[idx]:
        st.metric(
            str(row["metric"]),
            str(row["value"]),
            delta="✓ Done" if bool(row["ok"]) else "Needed",
            delta_color="normal" if bool(row["ok"]) else "inverse",
        )
        try:
            completed = float(row["completed"])
            target = float(str(row["target"]).replace("+", ""))
            st.progress(min(completed / target, 1.0) if target else 0.0)
        except Exception:
            pass
st.caption("These counters are frozen from the completion block in `pages/3_0_Thesis_Action_Plan.py`.")

legacy_a4_df = load_csv(VIS / "tone_climatebert_label_crosstab.csv")
full_a4_df = load_csv(VIS / "tone_climatebert_label_crosstab_full.csv")
legacy_a4_numeric = legacy_a4_df.select_dtypes(include="number")
legacy_a4_label_assignments = int(legacy_a4_numeric.to_numpy().sum()) if not legacy_a4_numeric.empty else 0
legacy_a4_rows = int(len(legacy_a4_df))
full_a4_numeric = full_a4_df.select_dtypes(include="number")
full_a4_label_assignments = int(full_a4_numeric.to_numpy().sum()) if not full_a4_numeric.empty else 0

st.subheader("A.4 Denominator Clarification")
a4_cols = st.columns(4)
a4_cols[0].metric("Legacy A.4 exploded label-cell count", f"{legacy_a4_label_assignments:,}")
a4_cols[1].metric("Legacy compact tone rows", f"{legacy_a4_rows:,}")
a4_cols[2].metric("Full corpus rows (Action Plan)", "5,444")
a4_cols[3].metric(
    "Full A.4 exploded label-cell count",
    f"{full_a4_label_assignments:,}" if full_a4_label_assignments else "not generated",
)
st.warning(
    "Do not compare exploded label-cell counts with row counts directly. "
    "Legacy A.4 comes from the compact snapshot; full-corpus A.4 uses the continuation table when available."
)
viz_df = pd.DataFrame(
    [
        {"A.4 scope": "Legacy compact tone rows", "count": legacy_a4_rows, "unit": "rows"},
        {"A.4 scope": "Legacy exploded label-cell count", "count": legacy_a4_label_assignments, "unit": "label-cell assignments"},
        {"A.4 scope": "Full corpus rows (Action Plan)", "count": 5444, "unit": "rows"},
        {
            "A.4 scope": "Full exploded label-cell count",
            "count": full_a4_label_assignments if full_a4_label_assignments else 0,
            "unit": "label-cell assignments",
        },
    ]
)
st.markdown("**A.4 Scope Comparison (visual)**")
st.bar_chart(viz_df.set_index("A.4 scope")["count"])
st.dataframe(viz_df, use_container_width=True, hide_index=True)

st.markdown("**Full A.4 - Tone by ClimateBERT label**")
if full_a4_df.empty:
    st.info(
        "Full A.4 crosstab is not available yet. Generate/save `tone_climatebert_label_crosstab_full.csv` "
        "from `pages/3_0_Thesis_Action_Plan.py` first."
    )
else:
    tone_col = "tone" if "tone" in full_a4_df.columns else full_a4_df.columns[0]
    a4_matrix = full_a4_df.copy()
    value_cols = [c for c in a4_matrix.columns if c != tone_col]
    for col in value_cols:
        a4_matrix[col] = pd.to_numeric(a4_matrix[col], errors="coerce").fillna(0)
    st.caption("Heatmap-style matrix of tone rows vs ClimateBERT labels using the full Action Plan corpus.")
    st.dataframe(a4_matrix, use_container_width=True, hide_index=True, height=280)
    st.bar_chart(a4_matrix.set_index(tone_col))

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
    ["DOCX Summary", "DOCX Structure", "Graph Attachments", "Chapter 4-6 Mapping", "Frozen Charts"]
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
    snapshot_rows = docx_snapshot_rows(bundle)
    st.dataframe(snapshot_rows, use_container_width=True, hide_index=True, height=300)
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

    st.subheader("Action Plan Completion Evidence")
    st.dataframe(
        action_status[["metric", "value", "status", "source page"]].astype(str),
        use_container_width=True,
        hide_index=True,
        height=260,
    )
    st.subheader("Action Plan -> Chapter 4-6 Integration")
    integration = snapshot.get("source_tables", {}).get("action_plan_integration")
    if not isinstance(integration, pd.DataFrame):
        integration = action_plan_integration_rows()
    st.dataframe(integration.astype(str), use_container_width=True, hide_index=True, height=220)
    resolution = snapshot.get("source_tables", {}).get("chapter_resolution")
    if not isinstance(resolution, pd.DataFrame):
        resolution = chapter_resolution_rows()
    with st.expander("Saved Chapter 4-6 resolution board", expanded=False):
        st.dataframe(resolution.astype(str), use_container_width=True, hide_index=True, height=300)
    st.download_button(
        "Download Action Plan status CSV",
        action_status.to_csv(index=False).encode("utf-8"),
        "action_plan_frozen_status.csv",
        "text/csv",
        use_container_width=True,
    )

    st.subheader("What the DOCX update adds")
    st.markdown(
        """
        - **Appendix A.1** frozen evidence snapshot from the shared result bundle.
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
    st.header("Graph Attachments")
    c1, c2, c3, c4 = st.columns(4)
    chapter_filter = c1.selectbox("Chapter", ["All"] + sorted(manifest["chapter"].unique().tolist()))
    rq_filter = c2.selectbox("RQ", ["All"] + sorted(manifest["rq"].unique().tolist()))
    view_mode = c3.selectbox("View", ["Graph + original table", "Graph only", "Original table only"])
    only_existing = c4.toggle("Only existing files", value=True)
    filtered = manifest.copy()
    filtered["_figure_title"] = filtered["figure"].astype(str) + " - " + filtered["title"].astype(str)
    if chapter_filter != "All":
        filtered = filtered[filtered["chapter"].eq(chapter_filter)]
    if rq_filter != "All":
        filtered = filtered[filtered["rq"].eq(rq_filter)]
    if only_existing:
        filtered = filtered[filtered["exists"]]
    c5, c6 = st.columns(2)
    figure_title_options = ["All"] + sorted(filtered["_figure_title"].dropna().astype(str).unique().tolist())
    source_page_options = ["All"] + sorted(filtered["source page"].dropna().astype(str).unique().tolist())
    figure_title_filter = c5.selectbox("Figure - Title", figure_title_options)
    source_page_filter = c6.selectbox("Source Page", source_page_options)
    if figure_title_filter != "All":
        filtered = filtered[filtered["_figure_title"].eq(figure_title_filter)]
    if source_page_filter != "All":
        filtered = filtered[filtered["source page"].astype(str).eq(source_page_filter)]
    st.dataframe(filtered.drop(columns=["_figure_title"]), use_container_width=True, hide_index=True, height=260)
    with st.expander("Source table descriptions", expanded=False):
        source_table_guide = (
            add_source_table_descriptions(manifest)[["source table", "source table description"]]
            .drop_duplicates()
            .sort_values("source table")
        )
        st.dataframe(source_table_guide, use_container_width=True, hide_index=True, height=320)

    st.subheader("5-cluster Mermaid map")
    st.caption(
        "Maps each graph attachment into five clusters: figure-title, chapter, RQ, source table, and source page."
    )
    figure_options = filtered["figure"].astype(str).tolist()
    default_figures = figure_options[: min(8, len(figure_options))]
    selected_figures = st.multiselect(
        "Figures to map",
        figure_options,
        default=default_figures,
        help="Select fewer figures if the diagram becomes too dense.",
        key="graph_attachment_mermaid_figures",
    )
    mermaid_rows = filtered[filtered["figure"].astype(str).isin(selected_figures)] if selected_figures else filtered.head(0)
    mermaid_code = graph_attachment_cluster_mermaid(mermaid_rows)
    render_mermaid(mermaid_code, height=max(520, min(1200, 260 + len(mermaid_rows) * 70)))
    with st.expander("Mermaid source code"):
        st.code(mermaid_code, language="mermaid")
        st.download_button(
            "Download Mermaid map",
            mermaid_code.encode("utf-8"),
            "graph_attachment_5_cluster_map.mmd",
            "text/plain",
            use_container_width=True,
        )

    for _, row in filtered.iterrows():
        path = Path(row["path"])
        st.divider()
        st.subheader(f"{row['figure']} - {row['title']}")
        meta_cols = st.columns([2, 2, 2, 1])
        meta_cols[0].caption(f"{row['chapter']} | {row['rq']}")
        meta_cols[1].caption(f"Graph: `{path}`")
        meta_cols[2].caption(f"Original table: `{row['source table']}`")
        with meta_cols[3]:
            redirect_button("Open page", str(row["source page"]))
        if str(row.get("source table description", "")).strip():
            st.caption(f"Source table description: {row['source table description']}")

        graph_col, table_col = st.columns([1.05, 1], gap="large")
        if view_mode in {"Graph + original table", "Graph only"}:
            with graph_col:
                st.markdown("**Original graph attachment**")
                st.caption("This is the graph image embedded into the updated DOCX appendix.")
                if path.exists():
                    show_image(path)
                else:
                    st.warning("Missing graph file.")
        if view_mode in {"Graph + original table", "Original table only"}:
            with table_col:
                st.markdown("**Original / backing table**")
                source_df = get_frozen_source_table(row, snapshot, bundle)
                if source_df.empty:
                    st.info("No backing table is available for this attachment yet.")
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
                        f"Download {row['figure']} backing table",
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

    st.subheader("Resolved Action Plan items now integrated")
    resolution = snapshot.get("source_tables", {}).get("chapter_resolution")
    if not isinstance(resolution, pd.DataFrame):
        resolution = chapter_resolution_rows()
    st.dataframe(resolution.astype(str), use_container_width=True, hide_index=True, height=320)

    st.subheader("Chapter 4 denominator audit")
    st.dataframe(tone_denominator_audit_rows().astype(str), use_container_width=True, hide_index=True, height=180)

with tab_live:
    st.header("Frozen Charts from the Chapter Pages")
    live_tabs = st.tabs(["Chapter 4", "Chapter 5", "Chapter 6"])
    with live_tabs[0]:
        st.subheader("Chapter 4 result evidence")
        c1, c2 = st.columns(2)
        with c1:
            count_chart(bundle["tone_records"], "tone", "Tone distribution")
        with c2:
            count_chart(bundle["tone_records"], "esg", "ESG pillar distribution")
        heatmap_from_table(bundle["tone_esg"], "tone", "Tone x ESG pillar")
    with live_tabs[1]:
        st.subheader("Chapter 5 discussion evidence")
        c1, c2 = st.columns(2)
        with c1:
            agreement_chart(bundle["agreement"])
        with c2:
            ontology_chart(bundle["ontology"])
        prompt_stability_chart(bundle["prompt_stability"])
    with live_tabs[2]:
        st.subheader("Chapter 6 conclusion evidence")
        workflow_coverage_chart()
        c1, c2 = st.columns(2)
        with c1:
            artifact_chart(bundle["inventory"])
        with c2:
            model_stability_chart(bundle["model_stability"])
