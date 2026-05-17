from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Ground Truth Step-by-Step Visualizer", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
DEFAULT_SOURCE = RESULTS_DIR / "esg_records.json"
DEFAULT_T1 = RESULTS_DIR / "t1_results.jsonl"
DEFAULT_T2 = RESULTS_DIR / "t2_results.jsonl"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def load_json(path: Path) -> Any:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def records_to_frame(data: Any) -> pd.DataFrame:
    if isinstance(data, list):
        rows = [row for row in data if isinstance(row, dict)]
    elif isinstance(data, dict):
        rows = data.get("records") if isinstance(data.get("records"), list) else [data]
        rows = [row for row in rows if isinstance(row, dict)]
    else:
        rows = []
    return pd.DataFrame(rows)


def extract_text_units(data: Any) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    source_rows = data if isinstance(data, list) else []
    for index, item in enumerate(source_rows):
        if isinstance(item, str) and item.strip():
            rows.append(
                {
                    "source_index": index,
                    "label": f"row_{index}",
                    "text": item.strip(),
                    "source_type": "string row",
                    "chars": len(item.strip()),
                }
            )
            continue
        if not isinstance(item, dict):
            continue

        base_label = clean(item.get("target") or item.get("label") or f"row_{index}")
        if clean(item.get("text")):
            text = clean(item.get("text"))
            rows.append(
                {
                    "source_index": index,
                    "label": base_label,
                    "text": text,
                    "source_type": "top-level text",
                    "chars": len(text),
                }
            )
            continue

        nested = item.get("records")
        if isinstance(nested, list):
            for rec_index, rec in enumerate(nested, start=1):
                if isinstance(rec, dict) and clean(rec.get("text")):
                    text = clean(rec.get("text"))
                    rows.append(
                        {
                            "source_index": index,
                            "label": f"{base_label}/rec_{rec_index}",
                            "text": text,
                            "source_type": "nested records",
                            "chars": len(text),
                        }
                    )
            continue

        raw_output = item.get("raw_output")
        if raw_output:
            try:
                parsed = json.loads(raw_output)
            except Exception:
                parsed = []
            if isinstance(parsed, list):
                for rec_index, rec in enumerate(parsed, start=1):
                    if isinstance(rec, dict) and clean(rec.get("text")):
                        text = clean(rec.get("text"))
                        rows.append(
                            {
                                "source_index": index,
                                "label": f"{base_label}/raw_{rec_index}",
                                "text": text,
                                "source_type": "raw_output JSON",
                                "chars": len(text),
                            }
                        )
    return pd.DataFrame(rows)


def parse_prediction_text(value: Any) -> tuple[str, float | None]:
    text = clean(value)
    if not text:
        return "", None
    if text.lower().startswith("error:"):
        return "error", None
    matches = re.findall(r"([A-Za-z][A-Za-z0-9_\- ]{0,60}):\s*([0-9]*\.?[0-9]+)", text)
    if not matches:
        return text.splitlines()[0][:80], None
    label, score = matches[-1]
    try:
        return label.strip(), float(score)
    except ValueError:
        return label.strip(), None


def flatten_t1(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in records:
        result = record.get("result")
        result_label = ""
        result_score = None
        result_raw = ""
        result_error = ""

        if isinstance(result, list) and result:
            first = result[0] if isinstance(result[0], dict) else {}
            result_label = clean(first.get("label"))
            result_score = first.get("score")
            result_raw = json.dumps(result, ensure_ascii=False)
        elif isinstance(result, dict):
            result_error = clean(result.get("error"))
            result_label, result_score = parse_prediction_text(result.get("prediction", result.get("label", "")))
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
    rows: list[dict[str, Any]] = []
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
        for prediction in predictions:
            rows.append(
                {
                    **base,
                    "section": clean(prediction.get("Section")),
                    "section_type": clean(prediction.get("Section_Type")),
                    "sentence_text": clean(prediction.get("Sentence_Text")) or clean(record.get("text")),
                    "sentiment_pred": clean(prediction.get("Sentiment_Pred")),
                    "tone_pred": clean(prediction.get("Tone_Pred")),
                    "ontology_alignment": pd.to_numeric(prediction.get("Ontology_Alignment"), errors="coerce"),
                    "ontology_path": clean(prediction.get("Ontology_Path")),
                    "sentiment_score": pd.to_numeric(prediction.get("sentiment_score"), errors="coerce"),
                    "tone_score": pd.to_numeric(prediction.get("tone_score"), errors="coerce"),
                }
            )
    return pd.DataFrame(rows)


def count_frame(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return pd.DataFrame(columns=[column, "count"])
    return df[column].map(clean).replace("", "missing").value_counts().rename_axis(column).reset_index(name="count")


def bar(df: pd.DataFrame, x: str, title: str, color: str = "#217c7e") -> None:
    if df.empty:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{x}:N", sort="-y", title=None),
            y=alt.Y("count:Q", title="Rows"),
            color=alt.value(color),
            tooltip=list(df.columns),
        )
        .properties(height=280, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def histogram(df: pd.DataFrame, column: str, title: str) -> None:
    if df.empty or column not in df.columns or df[column].dropna().empty:
        st.info("No numeric values available for this chart.")
        return
    chart = (
        alt.Chart(df.dropna(subset=[column]))
        .mark_bar()
        .encode(
            x=alt.X(f"{column}:Q", bin=alt.Bin(maxbins=30), title=column.replace("_", " ").title()),
            y=alt.Y("count():Q", title="Rows"),
            tooltip=[alt.Tooltip(f"{column}:Q", bin=True), alt.Tooltip("count():Q")],
        )
        .properties(height=280, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


st.title("Ground Truth Step-by-Step Visualizer")
st.caption("Follow the exact files produced by `ground_truth.py`: source ESG records, extracted text units, T1 model classifications, and T2 rule/hybrid outputs.")

with st.sidebar:
    st.header("Files")
    source_path = Path(st.text_input("Source records", str(DEFAULT_SOURCE))).expanduser()
    t1_path = Path(st.text_input("T1 JSONL", str(DEFAULT_T1))).expanduser()
    t2_path = Path(st.text_input("T2 JSONL", str(DEFAULT_T2))).expanduser()
    preview_limit = st.number_input("Preview row limit", min_value=25, max_value=5000, value=250, step=25)
    search = st.text_input("Search label/text", "")
    if st.button("Refresh", use_container_width=True):
        st.rerun()

source_data = load_json(source_path)
source_df = records_to_frame(source_data)
text_units = extract_text_units(source_data)
t1_raw = load_jsonl(t1_path)
t1_df = flatten_t1(t1_raw)
t2_raw = load_jsonl(t2_path)
t2_df = flatten_t2(t2_raw)

if search.strip():
    needle = search.strip().lower()
    for name, df in [("text_units", text_units), ("t1_df", t1_df), ("t2_df", t2_df)]:
        if df.empty:
            continue
        mask = pd.Series(False, index=df.index)
        for column in [col for col in ["label", "text", "sentence_text"] if col in df.columns]:
            mask = mask | df[column].map(lambda value: needle in clean(value).lower())
        if name == "text_units":
            text_units = df[mask]
        elif name == "t1_df":
            t1_df = df[mask]
        else:
            t2_df = df[mask]

metric_cols = st.columns(6)
metric_cols[0].metric("Source rows", f"{len(source_df):,}")
metric_cols[1].metric("Extracted text units", f"{len(text_units):,}")
metric_cols[2].metric("T1 raw rows", f"{len(t1_raw):,}")
metric_cols[3].metric("T1 success", f"{(t1_df['success'].mean() * 100):.1f}%" if not t1_df.empty and "success" in t1_df else "0.0%")
metric_cols[4].metric("T2 raw rows", f"{len(t2_raw):,}")
metric_cols[5].metric("T2 visual rows", f"{len(t2_df):,}")

st.caption(f"Source: `{source_path}`")
st.caption(f"T1: `{t1_path}`")
st.caption(f"T2: `{t2_path}`")

tabs = st.tabs(
    [
        "1 Source Records",
        "2 Extracted Text Units",
        "3 T1 Raw Output",
        "4 T1 Predictions",
        "5 T2 Raw Output",
        "6 T2 Hybrid Output",
        "7 Audit & Exports",
    ]
)

with tabs[0]:
    st.markdown("`ground_truth.py` starts by reading `results/esg_records.json`. Records can contain top-level `text`, nested `records[*].text`, or JSON stored in `raw_output`.")
    if source_df.empty:
        st.warning("No source rows found.")
    else:
        st.dataframe(source_df.head(int(preview_limit)), use_container_width=True, height=520)

with tabs[1]:
    st.markdown("This is the text list that `ground_truth.py` builds before running T1/T2.")
    if text_units.empty:
        st.warning("No usable text units were extracted from the source file.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            bar(count_frame(text_units, "source_type"), "source_type", "Text Units by Source Type")
        with c2:
            histogram(text_units, "chars", "Text Length Distribution")
        st.dataframe(text_units.head(int(preview_limit)), use_container_width=True, height=420)

with tabs[2]:
    st.markdown("T1 appends one JSONL row per `label x model` classification into `results/t1_results.jsonl`.")
    if not t1_raw:
        st.warning("No T1 raw rows found.")
    else:
        st.json(t1_raw[: min(5, int(preview_limit))], expanded=False)

with tabs[3]:
    st.markdown("This flattened view makes T1 model status, prediction labels, scores, and errors easier to compare.")
    if t1_df.empty:
        st.warning("No T1 rows found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            status_df = t1_df.assign(status=t1_df["success"].map({True: "success", False: "failed"}))
            bar(count_frame(status_df, "status"), "status", "T1 Status")
        with c2:
            bar(count_frame(t1_df, "prediction_label"), "prediction_label", "T1 Prediction Labels")
        histogram(t1_df, "prediction_score", "T1 Score Distribution")
        st.dataframe(t1_df.head(int(preview_limit)), use_container_width=True, height=460)

with tabs[4]:
    st.markdown("T2 appends one JSONL row per text label into `results/t2_results.jsonl`, including rule-based and hybrid outputs.")
    if not t2_raw:
        st.warning("No T2 raw rows found.")
    else:
        st.json(t2_raw[: min(5, int(preview_limit))], expanded=False)

with tabs[5]:
    st.markdown("This flattened view expands T2 hybrid sentence predictions, ontology paths, tone scores, and greenwashing metrics.")
    if t2_df.empty:
        st.warning("No T2 rows found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            bar(count_frame(t2_df, "rule_tone"), "rule_tone", "Rule-Based Tone")
        with c2:
            bar(count_frame(t2_df, "tone_pred"), "tone_pred", "Hybrid Tone")
        c3, c4 = st.columns(2)
        with c3:
            histogram(t2_df, "ontology_alignment", "Ontology Alignment")
        with c4:
            histogram(t2_df, "greenwashing_index", "Greenwashing Index")
        st.dataframe(t2_df.head(int(preview_limit)), use_container_width=True, height=460)

with tabs[6]:
    st.markdown("Use this tab to inspect failure rows and export filtered tables for reporting or manual review.")
    t1_failures = t1_df[(~t1_df["success"]) | t1_df["error"].map(clean).ne("")] if not t1_df.empty and "success" in t1_df else pd.DataFrame()
    t2_failures = t2_df[t2_df["hybrid_error"].map(clean).ne("")] if not t2_df.empty and "hybrid_error" in t2_df else pd.DataFrame()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("T1 failures")
        st.dataframe(t1_failures.head(int(preview_limit)), use_container_width=True, height=360)
        st.download_button("Download T1 flattened CSV", t1_df.to_csv(index=False).encode("utf-8"), "ground_truth_t1_flattened.csv", "text/csv")
    with c2:
        st.subheader("T2 hybrid errors")
        st.dataframe(t2_failures.head(int(preview_limit)), use_container_width=True, height=360)
        st.download_button("Download T2 flattened CSV", t2_df.to_csv(index=False).encode("utf-8"), "ground_truth_t2_flattened.csv", "text/csv")
