from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="LLM Processing Result Visualizer", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
T1_PATH = RESULTS_DIR / "predictions.json"
T2_PATH = RESULTS_DIR / "absa_results.json"
T3_PATH = RESULTS_DIR / "esg_records.json"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in {"nan", "none", "null"}:
        return ""
    return value


def load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    if isinstance(obj, list):
        return [row for row in obj if isinstance(row, dict)]
    if isinstance(obj, dict):
        return [obj]
    return []


def parse_prediction(value: Any) -> tuple[str, float | None, bool]:
    text = clean(value)
    if not text:
        return "", None, False
    if text.lower().startswith("error:"):
        return "error", None, True
    matches = re.findall(r"([A-Za-z][A-Za-z0-9_\- ]{0,80}):\s*([0-9]*\.?[0-9]+)", text)
    if matches:
        label, score = matches[-1]
        try:
            return label.strip(), float(score), False
        except ValueError:
            return label.strip(), None, False
    return text.splitlines()[0][:120], None, "error" in text.lower()


def dict_table(value: Any) -> pd.DataFrame:
    if isinstance(value, list):
        return pd.DataFrame(value)
    if isinstance(value, dict):
        try:
            return pd.DataFrame(value)
        except Exception:
            return pd.json_normalize(value)
    return pd.DataFrame()


def flatten_t1(rows: list[dict[str, Any]]) -> pd.DataFrame:
    out = []
    for row in rows:
        result = row.get("result") if isinstance(row.get("result"), dict) else {}
        pred_label, pred_score, is_error = parse_prediction(result.get("prediction", result.get("error", "")))
        error = clean(result.get("error")) or (clean(result.get("prediction")) if is_error else "")
        out.append(
            {
                "timestamp": clean(row.get("timestamp")),
                "model": clean(row.get("model") or result.get("model")),
                "source": clean(row.get("source")),
                "prediction_label": pred_label,
                "prediction_score": pred_score,
                "is_error": bool(is_error or error),
                "error": error,
                "text": clean(row.get("text") or result.get("text")),
                "text_len_chars": len(clean(row.get("text") or result.get("text"))),
            }
        )
    return pd.DataFrame(out)


def flatten_t2(rows: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    run_rows = []
    pred_rows = []
    metric_rows = []
    for row in rows:
        source = clean(row.get("source"))
        timestamp = clean(row.get("timestamp"))
        input_text = clean(row.get("input_text"))
        rule = row.get("rule_based") if isinstance(row.get("rule_based"), dict) else {}
        hybrid = row.get("hybrid_model") if isinstance(row.get("hybrid_model"), dict) else {}
        if not hybrid and isinstance(row.get("hybrid"), dict):
            hybrid = row.get("hybrid")

        hybrid_df = dict_table(hybrid.get("out_df", hybrid.get("predictions", [])))
        metrics_df = dict_table(hybrid.get("metrics", []))
        hybrid_error = clean(hybrid.get("error"))

        run_rows.append(
            {
                "timestamp": timestamp,
                "source": source,
                "rule_aspects": " | ".join(clean(v) for v in rule.get("aspects", []) if clean(v)),
                "rule_polarity": clean(rule.get("polarity")),
                "rule_tone": clean(rule.get("tone")),
                "hybrid_rows": len(hybrid_df),
                "hybrid_error": hybrid_error,
                "input_text_len_chars": len(input_text),
                "input_text": input_text,
            }
        )

        if not hybrid_df.empty:
            for _, pred in hybrid_df.iterrows():
                pred_rows.append(
                    {
                        "timestamp": timestamp,
                        "source": source,
                        "rule_polarity": clean(rule.get("polarity")),
                        "rule_tone": clean(rule.get("tone")),
                        "sentence_id": clean(pred.get("Sentence_ID")),
                        "section": clean(pred.get("Section")),
                        "section_type": clean(pred.get("Section_Type")),
                        "sentence_text": clean(pred.get("Sentence_Text")),
                        "sentiment_pred": clean(pred.get("Sentiment_Pred")),
                        "tone_pred": clean(pred.get("Tone_Pred")),
                        "ontology_alignment": pd.to_numeric(pred.get("Ontology_Alignment"), errors="coerce"),
                        "ontology_path": clean(pred.get("Ontology_Path")),
                        "sentiment_score": pd.to_numeric(pred.get("sentiment_score"), errors="coerce"),
                        "tone_score": pd.to_numeric(pred.get("tone_score"), errors="coerce"),
                    }
                )

        if not metrics_df.empty:
            for _, metric in metrics_df.iterrows():
                metric_rows.append(
                    {
                        "timestamp": timestamp,
                        "source": source,
                        "metric": clean(metric.get("Metric")),
                        "value": pd.to_numeric(metric.get("Value"), errors="coerce"),
                    }
                )

    return pd.DataFrame(run_rows), pd.DataFrame(pred_rows), pd.DataFrame(metric_rows)


def flatten_t3(rows: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    run_rows = []
    record_rows = []
    for run_idx, row in enumerate(rows):
        records = row.get("records") if isinstance(row.get("records"), list) else []
        target = clean(row.get("target"))
        company = target.split("/")[0] if target else ""
        run_rows.append(
            {
                "run_idx": run_idx,
                "timestamp": clean(row.get("timestamp")),
                "model": clean(row.get("model")),
                "target": target,
                "company": company,
                "prompt": clean(row.get("prompt")),
                "ok": bool(row.get("ok")),
                "n_records": len(records),
                "error": clean(row.get("error")),
                "raw_output_len_chars": len(clean(row.get("raw_output"))),
            }
        )
        for record_idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                continue
            labels = rec.get("labels", [])
            if isinstance(labels, list):
                labels_text = " | ".join(clean(v) for v in labels if clean(v))
            else:
                labels_text = clean(labels)
            text = clean(rec.get("text"))
            record_rows.append(
                {
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": clean(row.get("timestamp")),
                    "model": clean(row.get("model")),
                    "target": target,
                    "company": company,
                    "prompt": clean(row.get("prompt")),
                    "text": text,
                    "text_len_chars": len(text),
                    "aspect": clean(rec.get("aspect")),
                    "labels": labels_text,
                    "esg": clean(rec.get("esg")).upper(),
                    "tone": clean(rec.get("tone")).lower(),
                    "sentiment": clean(rec.get("sentiment")).lower(),
                    "sentiment_score": pd.to_numeric(rec.get("sentiment_score"), errors="coerce"),
                    "reasoning": clean(rec.get("reasoning")),
                }
            )
    return pd.DataFrame(run_rows), pd.DataFrame(record_rows)


def values(df: pd.DataFrame, col: str) -> list[str]:
    if df.empty or col not in df.columns:
        return []
    return sorted(v for v in df[col].map(clean).unique() if v)


def sidebar_filter(df: pd.DataFrame, col: str, label: str, key: str) -> pd.DataFrame:
    opts = values(df, col)
    selected = st.sidebar.multiselect(label, opts, key=key)
    if not selected:
        return df
    return df[df[col].map(clean).isin(selected)]


def paired_filter(left: pd.DataFrame, right: pd.DataFrame, col: str, label: str, key: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    opts = sorted(set(values(left, col)) | set(values(right, col)))
    selected = st.sidebar.multiselect(label, opts, key=key)
    if not selected:
        return left, right
    if col in left.columns:
        left = left[left[col].map(clean).isin(selected)]
    if col in right.columns:
        right = right[right[col].map(clean).isin(selected)]
    return left, right


def count_df(df: pd.DataFrame, col: str, label: str | None = None) -> pd.DataFrame:
    label = label or col
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[label, "count", "pct"])
    out = (
        df[col]
        .map(clean)
        .replace("", "missing")
        .value_counts()
        .rename_axis(label)
        .reset_index(name="count")
    )
    total = out["count"].sum()
    out["pct"] = (out["count"] / total * 100).round(2) if total else 0.0
    return out


def bar(df: pd.DataFrame, x: str, y: str = "count", color: str | None = None, title: str = ""):
    if df.empty:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{x}:N", sort="-y", title=x.replace("_", " ").title()),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ").title()),
            color=alt.Color(f"{color}:N") if color else alt.value("#217c7e"),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=330)
    )
    st.altair_chart(chart, use_container_width=True)


def histogram(df: pd.DataFrame, col: str, title: str):
    if df.empty or col not in df.columns or df[col].dropna().empty:
        st.info("No numeric values available for this chart.")
        return
    chart = (
        alt.Chart(df.dropna(subset=[col]))
        .mark_bar()
        .encode(
            x=alt.X(f"{col}:Q", bin=alt.Bin(maxbins=30), title=col.replace("_", " ").title()),
            y=alt.Y("count():Q", title="Count"),
            tooltip=[alt.Tooltip(f"{col}:Q", bin=True), alt.Tooltip("count():Q")],
        )
        .properties(title=title, height=330)
    )
    st.altair_chart(chart, use_container_width=True)


st.title("LLM Processing Result Visualizer")
st.caption("Visualize T1 ClimateBERT predictions, T2 ABSA outputs, and T3 LLM ESG extraction records produced by `llm_processing.py`.")

t1_df = flatten_t1(load_json(T1_PATH))
t2_runs, t2_preds, t2_metrics = flatten_t2(load_json(T2_PATH))
t3_runs, t3_records = flatten_t3(load_json(T3_PATH))

with st.sidebar:
    st.header("Files")
    st.caption(f"T1: `{T1_PATH}`")
    st.caption(f"T2: `{T2_PATH}`")
    st.caption(f"T3: `{T3_PATH}`")
    table_limit = st.number_input("Table preview row limit", min_value=50, value=500, step=50)
    if st.button("Refresh result files", use_container_width=True):
        st.rerun()

    st.header("T3 Filters")
    filtered_t3_runs = t3_runs.copy()
    filtered_t3_records = t3_records.copy()
    for col, label in [
        ("model", "T3 Model"),
        ("company", "Company"),
        ("target", "Target"),
        ("prompt", "Prompt"),
    ]:
        filtered_t3_runs, filtered_t3_records = paired_filter(filtered_t3_runs, filtered_t3_records, col, label, f"t3_{col}")
    for col, label in [("esg", "ESG"), ("tone", "Tone"), ("sentiment", "Sentiment"), ("aspect", "Aspect")]:
        filtered_t3_records = sidebar_filter(filtered_t3_records, col, label, f"t3rec_{col}")

    st.header("T2 Filters")
    filtered_t2_runs = t2_runs.copy()
    filtered_t2_preds = t2_preds.copy()
    for col, label in [("source", "T2 Source"), ("rule_tone", "Rule Tone"), ("tone_pred", "Hybrid Tone"), ("sentiment_pred", "Hybrid Sentiment")]:
        filtered_t2_runs, filtered_t2_preds = paired_filter(filtered_t2_runs, filtered_t2_preds, col, label, f"t2_{col}")

    st.header("T1 Filters")
    filtered_t1 = t1_df.copy()
    for col, label in [("model", "T1 Model"), ("source", "T1 Source"), ("prediction_label", "Prediction Label")]:
        filtered_t1 = sidebar_filter(filtered_t1, col, label, f"t1_{col}")

overview = st.columns(6)
overview[0].metric("T3 runs", f"{len(filtered_t3_runs):,}")
overview[1].metric("T3 records", f"{len(filtered_t3_records):,}")
overview[2].metric("T3 failed runs", f"{int(filtered_t3_runs['ok'].eq(False).sum()):,}" if "ok" in filtered_t3_runs else "0")
overview[3].metric("T2 runs", f"{len(filtered_t2_runs):,}")
overview[4].metric("T2 predictions", f"{len(filtered_t2_preds):,}")
overview[5].metric("T1 rows", f"{len(filtered_t1):,}")

tabs = st.tabs(["Overview", "T3 ESG Records", "T3 Run Quality", "T2 ABSA", "T1 ClimateBERT", "Records & Exports"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        bar(count_df(filtered_t3_records, "tone"), "tone", title="T3 Tone Distribution")
    with c2:
        bar(count_df(filtered_t3_records, "esg"), "esg", title="T3 ESG Pillar Distribution")
    c3, c4 = st.columns(2)
    with c3:
        bar(count_df(filtered_t3_records, "sentiment"), "sentiment", title="T3 Sentiment Distribution")
    with c4:
        bar(count_df(filtered_t3_runs, "prompt"), "prompt", title="T3 Runs by Prompt")

with tabs[1]:
    st.markdown("T3 records are the parsed ESG evidence records extracted by the selected LLM, target batch, and prompt.")
    c1, c2 = st.columns(2)
    with c1:
        bar(count_df(filtered_t3_records, "aspect").head(25), "aspect", title="Top Extracted Aspects")
    with c2:
        histogram(filtered_t3_records, "sentiment_score", "Sentiment Score Distribution")
    st.dataframe(filtered_t3_records.head(int(table_limit)), use_container_width=True, height=520)

with tabs[2]:
    st.markdown("Run quality shows whether prompts and models produced parsed records, empty arrays, or errors.")
    if not filtered_t3_runs.empty:
        status_df = filtered_t3_runs.assign(status=filtered_t3_runs["ok"].map({True: "ok", False: "failed"}))
        c1, c2 = st.columns(2)
        with c1:
            bar(count_df(status_df, "status"), "status", title="T3 Run Status")
        with c2:
            histogram(filtered_t3_runs, "n_records", "Records per T3 Run")
        by_model = status_df.groupby(["model", "status"], dropna=False).size().reset_index(name="count")
        bar(by_model, "model", color="status", title="T3 Status by Model")
        failed = filtered_t3_runs[filtered_t3_runs["ok"].eq(False) | filtered_t3_runs["error"].map(clean).ne("")]
        st.markdown("**Failed or partial runs**")
        st.dataframe(failed.head(int(table_limit)), use_container_width=True, height=420)

with tabs[3]:
    st.markdown("T2 records come from the rule-based, classical, and hybrid ABSA layer.")
    if filtered_t2_preds.empty:
        st.info("No flattened T2 hybrid predictions found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            bar(count_df(filtered_t2_preds, "tone_pred"), "tone_pred", title="Hybrid Tone")
        with c2:
            bar(count_df(filtered_t2_preds, "sentiment_pred"), "sentiment_pred", title="Hybrid Sentiment")
        c3, c4 = st.columns(2)
        with c3:
            histogram(filtered_t2_preds, "ontology_alignment", "Ontology Alignment")
        with c4:
            histogram(filtered_t2_preds, "tone_score", "Tone Score")
        st.markdown("**T2 metrics**")
        st.dataframe(t2_metrics.head(int(table_limit)), use_container_width=True, height=260)
        st.markdown("**T2 hybrid predictions**")
        st.dataframe(filtered_t2_preds.head(int(table_limit)), use_container_width=True, height=420)

with tabs[4]:
    st.markdown("T1 predictions are ClimateBERT/model-level predictions saved by `llm_processing.py`.")
    if filtered_t1.empty:
        st.info("No T1 predictions found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            bar(count_df(filtered_t1, "prediction_label"), "prediction_label", title="T1 Prediction Labels")
        with c2:
            histogram(filtered_t1, "prediction_score", "T1 Prediction Scores")
        status_df = filtered_t1.assign(status=filtered_t1["is_error"].map({True: "error", False: "ok"}))
        by_model = status_df.groupby(["model", "status"], dropna=False).size().reset_index(name="count")
        bar(by_model, "model", color="status", title="T1 Status by Model")
        st.dataframe(filtered_t1.head(int(table_limit)), use_container_width=True, height=420)

with tabs[5]:
    st.markdown("Download flattened CSVs for analysis, tables, or documentation.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Download T3 records CSV", filtered_t3_records.to_csv(index=False).encode("utf-8"), "llm_t3_records.csv", "text/csv")
        st.download_button("Download T3 runs CSV", filtered_t3_runs.to_csv(index=False).encode("utf-8"), "llm_t3_runs.csv", "text/csv")
    with c2:
        st.download_button("Download T2 predictions CSV", filtered_t2_preds.to_csv(index=False).encode("utf-8"), "llm_t2_predictions.csv", "text/csv")
        st.download_button("Download T2 runs CSV", filtered_t2_runs.to_csv(index=False).encode("utf-8"), "llm_t2_runs.csv", "text/csv")
    with c3:
        st.download_button("Download T1 predictions CSV", filtered_t1.to_csv(index=False).encode("utf-8"), "llm_t1_predictions.csv", "text/csv")

    st.subheader("Raw Run Tables")
    st.markdown("**T3 runs**")
    st.dataframe(filtered_t3_runs.head(int(table_limit)), use_container_width=True, height=300)
    st.markdown("**T2 runs**")
    st.dataframe(filtered_t2_runs.head(int(table_limit)), use_container_width=True, height=300)
    st.markdown("**T1 rows**")
    st.dataframe(filtered_t1.head(int(table_limit)), use_container_width=True, height=300)
