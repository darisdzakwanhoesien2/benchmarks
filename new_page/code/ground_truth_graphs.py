from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
WORKFLOW = RESULTS / "thesis_workflow_dashboard"
GRAPH_DIR = RESULTS / "docx_graph_attachments"

T1_JSONL = RESULTS / "t1_results.jsonl"
T1_JSON = RESULTS / "t1_results.json"
T2_JSONL = RESULTS / "t2_results.jsonl"
T2_JSON = RESULTS / "t2_results.json"
T2_FLAT = WORKFLOW / "t2_flat_outputs.csv"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def load_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
        return rows
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    if isinstance(obj, list):
        return [row for row in obj if isinstance(row, dict)]
    if isinstance(obj, dict) and isinstance(obj.get("records"), list):
        return [row for row in obj["records"] if isinstance(row, dict)]
    return [obj] if isinstance(obj, dict) else []


def parse_prediction_text(value: Any) -> tuple[str, float | None]:
    text = clean(value)
    if not text:
        return "", None
    if text.lower().startswith("error:"):
        return "error", None
    matches = re.findall(r"([A-Za-z][A-Za-z0-9_ -]{0,60}):\s*([0-9]*\.?[0-9]+)", text)
    if not matches:
        return text.splitlines()[0][:80], None
    label, score = matches[-1]
    try:
        return label.strip(), float(score)
    except ValueError:
        return label.strip(), None


def flatten_t1(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for record in records:
        result = record.get("result")
        result_error = ""
        result_label = ""
        result_score = None
        result_raw = ""
        if isinstance(result, list) and result:
            first = result[0] if isinstance(result[0], dict) else {}
            result_label = clean(first.get("label"))
            result_score = first.get("score")
            result_raw = json.dumps(result, ensure_ascii=False)
        elif isinstance(result, dict):
            result_error = clean(result.get("error"))
            prediction = result.get("prediction", result.get("label", ""))
            result_label, result_score = parse_prediction_text(prediction)
            result_raw = json.dumps(result, ensure_ascii=False)
        else:
            result_label, result_score = parse_prediction_text(result)
            result_raw = clean(result)
        error = clean(record.get("error")) or result_error
        success = record.get("success")
        if success is None:
            success = not bool(error or result_label.lower() == "error")
        rows.append(
            {
                "timestamp": clean(record.get("timestamp")),
                "label": clean(record.get("label")),
                "model": clean(record.get("model")),
                "backend": clean(record.get("backend")),
                "text": clean(record.get("text")),
                "success": bool(success),
                "error": error,
                "prediction_label": result_label,
                "prediction_score": pd.to_numeric(result_score, errors="coerce"),
                "result_raw": result_raw,
            }
        )
    return pd.DataFrame(rows)


def metric_value(metrics: list[dict[str, Any]], metric_name: str) -> float | None:
    for item in metrics:
        if clean(item.get("Metric")).lower() == metric_name.lower():
            return pd.to_numeric(item.get("Value"), errors="coerce")
    return None


def flatten_t2(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for record in records:
        rule = record.get("rule_based") if isinstance(record.get("rule_based"), dict) else {}
        hybrid = record.get("hybrid") if isinstance(record.get("hybrid"), dict) else {}
        predictions = hybrid.get("predictions") if isinstance(hybrid.get("predictions"), list) else []
        metrics = hybrid.get("metrics") if isinstance(hybrid.get("metrics"), list) else []
        base = {
            "timestamp": clean(record.get("timestamp")),
            "label": clean(record.get("label")),
            "text": clean(record.get("text")),
            "rule_aspects": " | ".join(clean(v) for v in rule.get("aspects", []) if clean(v)),
            "rule_polarity": clean(rule.get("polarity")),
            "rule_tone": clean(rule.get("tone")),
            "hybrid_error": clean(hybrid.get("error")),
            "ontology_consistency": metric_value(metrics, "Ontology Consistency"),
            "greenwashing_index": metric_value(metrics, "Greenwashing Index"),
            "n_sentences": metric_value(metrics, "N Sentences"),
            "sections": metric_value(metrics, "Sections"),
        }
        if not predictions:
            rows.append(base)
            continue
        for pred in predictions:
            rows.append(
                {
                    **base,
                    "section": clean(pred.get("Section")),
                    "section_type": clean(pred.get("Section_Type")),
                    "sentence_text": clean(pred.get("Sentence_Text")) or clean(record.get("text")),
                    "sentiment_pred": clean(pred.get("Sentiment_Pred")),
                    "tone_pred": clean(pred.get("Tone_Pred")),
                    "ontology_alignment": pd.to_numeric(pred.get("Ontology_Alignment"), errors="coerce"),
                    "ontology_path": clean(pred.get("Ontology_Path")),
                    "sentiment_score": pd.to_numeric(pred.get("sentiment_score"), errors="coerce"),
                    "tone_score": pd.to_numeric(pred.get("tone_score"), errors="coerce"),
                }
            )
    return pd.DataFrame(rows)


def load_t1_outputs() -> pd.DataFrame:
    path = T1_JSONL if T1_JSONL.exists() else T1_JSON
    return flatten_t1(load_json_or_jsonl(path))


def load_t2_outputs() -> pd.DataFrame:
    if T2_FLAT.exists():
        try:
            return pd.read_csv(T2_FLAT).fillna("")
        except Exception:
            pass
    path = T2_JSONL if T2_JSONL.exists() else T2_JSON
    return flatten_t2(load_json_or_jsonl(path))


def count_rows(df: pd.DataFrame, col: str, label: str | None = None) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[label or col, "records"])
    out = (
        df[col]
        .map(clean)
        .replace("", "missing")
        .value_counts()
        .rename_axis(label or col)
        .reset_index(name="records")
    )
    return out


def t1_status_rows() -> pd.DataFrame:
    df = load_t1_outputs()
    if df.empty or "success" not in df.columns:
        return pd.DataFrame(columns=["status", "records"])
    status = df["success"].map({True: "success", False: "failed"}).fillna("unknown")
    return status.value_counts().rename_axis("status").reset_index(name="records")


def t1_prediction_rows() -> pd.DataFrame:
    return count_rows(load_t1_outputs(), "prediction_label", "prediction_label")


def t2_rule_tone_rows() -> pd.DataFrame:
    return count_rows(load_t2_outputs(), "rule_tone", "rule_tone")


def t2_hybrid_tone_rows() -> pd.DataFrame:
    return count_rows(load_t2_outputs(), "tone_pred", "tone_pred")


def t2_sentiment_rows() -> pd.DataFrame:
    return count_rows(load_t2_outputs(), "sentiment_pred", "sentiment_pred")


def t2_rule_hybrid_tone_matrix_rows() -> pd.DataFrame:
    df = load_t2_outputs()
    if df.empty or not {"rule_tone", "tone_pred"}.issubset(df.columns):
        return pd.DataFrame()
    view = df[df["rule_tone"].map(clean).ne("") & df["tone_pred"].map(clean).ne("")].copy()
    if view.empty:
        return pd.DataFrame()
    view["rule_tone"] = view["rule_tone"].astype(str).str.lower()
    view["tone_pred"] = view["tone_pred"].astype(str).str.lower()
    pivot = pd.crosstab(view["rule_tone"], view["tone_pred"])
    pivot.index.name = "rule_tone"
    pivot.columns.name = None
    return pivot.reset_index()


def t2_ontology_path_rows() -> pd.DataFrame:
    return count_rows(load_t2_outputs(), "ontology_path", "ontology_path").head(30)


def t2_numeric_summary_rows() -> pd.DataFrame:
    df = load_t2_outputs()
    rows = []
    for col in ["ontology_alignment", "greenwashing_index", "tone_score", "sentiment_score"]:
        if df.empty or col not in df.columns:
            continue
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        if values.empty:
            continue
        rows.append(
            {
                "metric": col,
                "records": int(values.count()),
                "mean": round(float(values.mean()), 4),
                "median": round(float(values.median()), 4),
                "min": round(float(values.min()), 4),
                "max": round(float(values.max()), 4),
            }
        )
    return pd.DataFrame(rows)


def chart_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_bar(path: Path, title: str, rows: pd.DataFrame, label_col: str, value_col: str = "records", subtitle: str = "") -> None:
    if rows.empty or label_col not in rows.columns or value_col not in rows.columns:
        return
    plot = rows[[label_col, value_col]].copy()
    plot[value_col] = pd.to_numeric(plot[value_col], errors="coerce").fillna(0)
    plot = plot.sort_values(value_col, ascending=False).head(18)
    width, height = 1800, max(700, 180 + len(plot) * 70)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    title_font = chart_font(46, True)
    sub_font = chart_font(24)
    label_font = chart_font(24)
    value_font = chart_font(22)
    draw.rectangle((0, 0, width, 120), fill="#eef6f4")
    draw.text((40, 26), title, fill="#173f42", font=title_font)
    if subtitle:
        draw.text((42, 84), subtitle, fill="#5b6472", font=sub_font)
    x0, x1 = 560, width - 120
    y = 160
    max_value = max(float(plot[value_col].max()), 1)
    for _, row in plot.iterrows():
        label = str(row[label_col])[:42]
        value = float(row[value_col])
        draw.text((45, y + 4), label, fill="#1f2937", font=label_font)
        bar_width = int((x1 - x0) * value / max_value)
        draw.rounded_rectangle((x0, y, x0 + bar_width, y + 36), radius=8, fill="#2f6f73")
        draw.text((x0 + bar_width + 18, y + 4), f"{value:,.0f}", fill="#111827", font=value_font)
        y += 70
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def draw_heatmap(path: Path, title: str, df: pd.DataFrame, subtitle: str = "") -> None:
    if df.empty:
        return
    row_col = df.columns[0]
    value_cols = [col for col in df.columns if col != row_col]
    if not value_cols:
        return
    n_rows = min(len(df), 24)
    n_cols = len(value_cols)
    row_w = 360
    col_w = max(100, min(170, 1420 // max(n_cols, 1)))
    row_h = 44
    title_h = 120
    width = row_w + col_w * n_cols + 60
    height = title_h + row_h + n_rows * row_h + 60
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, title_h - 10), fill="#eef6f4")
    draw.text((32, 24), title, fill="#173f42", font=chart_font(42, True))
    if subtitle:
        draw.text((34, 84), subtitle, fill="#5b6472", font=chart_font(22))
    num_df = df[value_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    max_val = float(max(num_df.values.max(), 1))
    y0 = title_h
    draw.rectangle((0, y0, width, y0 + row_h), fill="#173f42")
    draw.text((14, y0 + 12), str(row_col)[:28], fill="white", font=chart_font(20, True))
    for idx, col in enumerate(value_cols):
        x = row_w + idx * col_w
        draw.text((x + 8, y0 + 12), str(col)[:14], fill="white", font=chart_font(18, True))
    for r_idx, (_, row) in enumerate(df.head(n_rows).iterrows()):
        y = y0 + (r_idx + 1) * row_h
        draw.rectangle((0, y, width, y + row_h - 1), fill=(249, 252, 251) if r_idx % 2 == 0 else (255, 255, 255))
        draw.text((14, y + 12), str(row[row_col])[:34], fill="#1f2937", font=chart_font(19))
        for c_idx, col in enumerate(value_cols):
            x = row_w + c_idx * col_w
            val = float(pd.to_numeric(row[col], errors="coerce") or 0)
            t = min(val / max_val, 1.0)
            fill = (int(229 * (1 - t) + 42 * t), int(242 * (1 - t) + 111 * t), int(238 * (1 - t) + 115 * t))
            draw.rectangle((x + 2, y + 2, x + col_w - 2, y + row_h - 3), fill=fill)
            text_color = "white" if t > 0.62 else "#111827"
            draw.text((x + col_w // 2 - 10, y + 12), f"{int(val)}", fill=text_color, font=chart_font(18))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def ensure_ground_truth_graphs() -> None:
    draw_bar(GRAPH_DIR / "ground_truth_t1_status.png", "ground_truth.py T1 Status", t1_status_rows(), "status", subtitle="Success/failure rows from T1 model outputs")
    draw_bar(GRAPH_DIR / "ground_truth_t1_prediction_labels.png", "ground_truth.py T1 Prediction Labels", t1_prediction_rows(), "prediction_label", subtitle="ClimateBERT/local classifier labels")
    draw_bar(GRAPH_DIR / "ground_truth_t2_rule_tone.png", "ground_truth.py T2 Rule-Based Tone", t2_rule_tone_rows(), "rule_tone", subtitle="Rule-based tone outputs")
    draw_bar(GRAPH_DIR / "ground_truth_t2_hybrid_tone.png", "ground_truth.py T2 Hybrid Tone", t2_hybrid_tone_rows(), "tone_pred", subtitle="Hybrid ABSA tone outputs")
    draw_bar(GRAPH_DIR / "ground_truth_t2_sentiment.png", "ground_truth.py T2 Sentiment", t2_sentiment_rows(), "sentiment_pred", subtitle="Hybrid ABSA sentiment outputs")
    draw_heatmap(GRAPH_DIR / "ground_truth_rule_vs_hybrid_tone.png", "ground_truth.py Rule × Hybrid Tone", t2_rule_hybrid_tone_matrix_rows(), "Rule-based tone compared with hybrid tone")
    draw_bar(GRAPH_DIR / "ground_truth_ontology_paths.png", "ground_truth.py Ontology Paths", t2_ontology_path_rows(), "ontology_path", subtitle="Top ontology paths from T2")
    draw_bar(GRAPH_DIR / "ground_truth_numeric_summary.png", "ground_truth.py Numeric Metrics", t2_numeric_summary_rows(), "metric", "mean", "Mean values for ontology, greenwashing, tone, and sentiment scores")


def ground_truth_attachment_rows() -> list[tuple[str, str, Path, str, str, str, str]]:
    return [
        ("A.22", "ground_truth.py T1 status", GRAPH_DIR / "ground_truth_t1_status.png", "Chapter 4", "RQ2", "t1_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.23", "ground_truth.py T1 prediction labels", GRAPH_DIR / "ground_truth_t1_prediction_labels.png", "Chapter 4", "RQ2", "t1_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.24", "ground_truth.py T2 rule tone", GRAPH_DIR / "ground_truth_t2_rule_tone.png", "Chapter 4", "RQ2", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.25", "ground_truth.py T2 hybrid tone", GRAPH_DIR / "ground_truth_t2_hybrid_tone.png", "Chapter 4", "RQ2", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.26", "ground_truth.py T2 sentiment", GRAPH_DIR / "ground_truth_t2_sentiment.png", "Chapter 4", "RQ2", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.27", "ground_truth.py rule vs hybrid tone", GRAPH_DIR / "ground_truth_rule_vs_hybrid_tone.png", "Chapter 4 / 5", "RQ2", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.28", "ground_truth.py ontology paths", GRAPH_DIR / "ground_truth_ontology_paths.png", "Chapter 5", "RQ4", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.29", "ground_truth.py numeric metrics", GRAPH_DIR / "ground_truth_numeric_summary.png", "Chapter 5", "RQ4", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
    ]


def ground_truth_source_dataframe(figure: str) -> pd.DataFrame:
    mapping = {
        "A.22": t1_status_rows,
        "A.23": t1_prediction_rows,
        "A.24": t2_rule_tone_rows,
        "A.25": t2_hybrid_tone_rows,
        "A.26": t2_sentiment_rows,
        "A.27": t2_rule_hybrid_tone_matrix_rows,
        "A.28": t2_ontology_path_rows,
        "A.29": t2_numeric_summary_rows,
    }
    fn = mapping.get(figure)
    return fn() if fn else pd.DataFrame()
