from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Ground Truth Record Audit", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
DEFAULT_T1_JSONL = RESULTS_DIR / "t1_results.jsonl"
DEFAULT_T2_JSONL = RESULTS_DIR / "t2_results.jsonl"


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

    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []

    if isinstance(obj, dict) and isinstance(obj.get("records"), list):
        return [row for row in obj["records"] if isinstance(row, dict)]
    if isinstance(obj, list):
        return [row for row in obj if isinstance(row, dict)]
    if isinstance(obj, dict):
        return [obj]
    return []


def parse_prediction_text(value: Any) -> tuple[str, float | None]:
    text = clean(value)
    if not text:
        return "", None
    if text.lower().startswith("error:"):
        return "error", None
    matches = re.findall(r"([A-Za-z][A-Za-z0-9_\\- ]{0,60}):\\s*([0-9]*\\.?[0-9]+)", text)
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
        prediction_label = ""
        prediction_score = None
        result_raw = ""
        result_error = ""

        if isinstance(result, list) and result:
            first = result[0] if isinstance(result[0], dict) else {}
            prediction_label = clean(first.get("label"))
            prediction_score = first.get("score")
            result_raw = json.dumps(result, ensure_ascii=False)
        elif isinstance(result, dict):
            result_error = clean(result.get("error"))
            prediction_label, prediction_score = parse_prediction_text(result.get("prediction", result.get("label", "")))
            result_raw = json.dumps(result, ensure_ascii=False)
        else:
            prediction_label, prediction_score = parse_prediction_text(result)
            result_raw = clean(result)

        error = clean(record.get("error")) or result_error
        success = record.get("success")
        if success is None:
            success = not bool(error)

        rows.append(
            {
                "timestamp": clean(record.get("timestamp")),
                "label": clean(record.get("label")),
                "model": clean(record.get("model")),
                "backend": clean(record.get("backend")),
                "text": clean(record.get("text")),
                "success": bool(success),
                "error": error,
                "prediction_label": prediction_label,
                "prediction_score": pd.to_numeric(prediction_score, errors="coerce"),
                "result_raw": result_raw,
            }
        )
    return pd.DataFrame(rows)


def metric_value(metrics: list[dict[str, Any]], metric_name: str) -> float | None:
    for row in metrics:
        if clean(row.get("Metric")).lower() == metric_name.lower():
            return pd.to_numeric(row.get("Value"), errors="coerce")
    return None


def flatten_t2(records: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    label_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []

    for record in records:
        rule = record.get("rule_based") if isinstance(record.get("rule_based"), dict) else {}
        hybrid = record.get("hybrid") if isinstance(record.get("hybrid"), dict) else {}
        metrics = hybrid.get("metrics") if isinstance(hybrid.get("metrics"), list) else []
        predictions = hybrid.get("predictions") if isinstance(hybrid.get("predictions"), list) else []

        label_rows.append(
            {
                "timestamp": clean(record.get("timestamp")),
                "label": clean(record.get("label")),
                "text": clean(record.get("text")),
                "rule_aspects": " | ".join(clean(v) for v in rule.get("aspects", []) if clean(v)),
                "rule_polarity": clean(rule.get("polarity")),
                "rule_tone": clean(rule.get("tone")),
                "hybrid_error": clean(hybrid.get("error")),
                "prediction_count": len(predictions),
                "ontology_consistency": metric_value(metrics, "Ontology Consistency"),
                "greenwashing_index": metric_value(metrics, "Greenwashing Index"),
                "n_sentences": metric_value(metrics, "N Sentences"),
                "sections": metric_value(metrics, "Sections"),
            }
        )

        for pred in predictions:
            prediction_rows.append(
                {
                    "label": clean(record.get("label")),
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

    return pd.DataFrame(label_rows), pd.DataFrame(prediction_rows)


def summarize_label_t1(t1: pd.DataFrame) -> pd.DataFrame:
    if t1.empty:
        return pd.DataFrame(columns=["label"])

    summary = (
        t1.groupby("label", dropna=False)
        .agg(
            text=("text", "first"),
            t1_models=("model", lambda s: ", ".join(sorted({clean(v) for v in s if clean(v)}))),
            t1_success_count=("success", "sum"),
            t1_total_runs=("label", "size"),
            t1_failure_count=("success", lambda s: int((~s).sum())),
            t1_prediction_labels=("prediction_label", lambda s: ", ".join(sorted({clean(v) for v in s if clean(v)}))),
            t1_error_excerpt=("error", lambda s: next((clean(v)[:160] for v in s if clean(v)), "")),
            avg_prediction_score=("prediction_score", "mean"),
        )
        .reset_index()
    )
    return summary


def summarize_label_t2(t2_labels: pd.DataFrame, t2_predictions: pd.DataFrame) -> pd.DataFrame:
    if t2_labels.empty:
        return pd.DataFrame(columns=["label"])

    summary = t2_labels.copy()
    if t2_predictions.empty:
        summary["hybrid_tones"] = ""
        summary["hybrid_sentiments"] = ""
        summary["ontology_paths"] = ""
        summary["avg_ontology_alignment"] = pd.NA
        summary["avg_tone_score"] = pd.NA
        return summary

    pred_summary = (
        t2_predictions.groupby("label", dropna=False)
        .agg(
            hybrid_tones=("tone_pred", lambda s: ", ".join(sorted({clean(v) for v in s if clean(v)}))),
            hybrid_sentiments=("sentiment_pred", lambda s: ", ".join(sorted({clean(v) for v in s if clean(v)}))),
            ontology_paths=("ontology_path", lambda s: " | ".join(sorted({clean(v) for v in s if clean(v)}))),
            avg_ontology_alignment=("ontology_alignment", "mean"),
            avg_tone_score=("tone_score", "mean"),
        )
        .reset_index()
    )
    return summary.merge(pred_summary, on="label", how="left")


def bar(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = ""):
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
        .properties(height=340, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


st.title("Ground Truth Record Audit")
st.caption(
    "Audit saved `ground_truth.py` outputs per source label. This page joins T1 classification results with T2 rule-based and hybrid outputs so each record can be inspected end to end."
)

with st.sidebar:
    st.header("Files")
    t1_path_input = st.text_input("T1 output path", str(DEFAULT_T1_JSONL))
    t2_path_input = st.text_input("T2 output path", str(DEFAULT_T2_JSONL))
    preview_limit = st.number_input("Table preview row limit", min_value=50, value=300, step=50)
    if st.button("Refresh audit", use_container_width=True):
        st.rerun()

t1_path = Path(t1_path_input).expanduser()
t2_path = Path(t2_path_input).expanduser()

t1 = flatten_t1(load_json_or_jsonl(t1_path))
t2_labels, t2_predictions = flatten_t2(load_json_or_jsonl(t2_path))
t1_summary = summarize_label_t1(t1)
t2_summary = summarize_label_t2(t2_labels, t2_predictions)

labels = sorted(
    {
        *{clean(v) for v in t1_summary.get("label", pd.Series(dtype=str)).tolist() if clean(v)},
        *{clean(v) for v in t2_summary.get("label", pd.Series(dtype=str)).tolist() if clean(v)},
    }
)

joined = pd.DataFrame({"label": labels})
if not joined.empty:
    joined = joined.merge(t1_summary, on="label", how="left")
    joined = joined.merge(t2_summary, on="label", how="left", suffixes=("_t1", "_t2"))
    joined["text_joined"] = joined["text_t1"].where(joined["text_t1"].map(clean).ne(""), joined["text_t2"])
    joined["has_t1"] = joined["t1_total_runs"].fillna(0).gt(0)
    joined["has_t2"] = joined["prediction_count"].fillna(0).gt(0) | joined["hybrid_error"].map(clean).ne("")
    joined["pipeline_status"] = "t1+t2"
    joined.loc[joined["has_t1"] & ~joined["has_t2"], "pipeline_status"] = "t1_only"
    joined.loc[~joined["has_t1"] & joined["has_t2"], "pipeline_status"] = "t2_only"
    joined.loc[~joined["has_t1"] & ~joined["has_t2"], "pipeline_status"] = "missing"
else:
    joined = pd.DataFrame(columns=["label"])

with st.sidebar:
    st.header("Filters")
    status_filter = st.multiselect(
        "Pipeline status",
        ["t1+t2", "t1_only", "t2_only", "missing"],
        default=["t1+t2", "t1_only", "t2_only"],
    )
    tone_filter = st.multiselect(
        "T2 hybrid tone",
        sorted({clean(v) for v in joined.get("hybrid_tones", pd.Series(dtype=str)).tolist() if clean(v)}),
    )
    rule_tone_filter = st.multiselect(
        "T2 rule tone",
        sorted({clean(v) for v in joined.get("rule_tone", pd.Series(dtype=str)).tolist() if clean(v)}),
    )
    model_filter = st.multiselect(
        "T1 model list",
        sorted({clean(v) for v in joined.get("t1_models", pd.Series(dtype=str)).tolist() if clean(v)}),
    )

filtered = joined.copy()
if not filtered.empty:
    filtered = filtered[filtered["pipeline_status"].isin(status_filter)]
    if tone_filter:
        filtered = filtered[filtered["hybrid_tones"].map(clean).isin(tone_filter)]
    if rule_tone_filter:
        filtered = filtered[filtered["rule_tone"].map(clean).isin(rule_tone_filter)]
    if model_filter:
        filtered = filtered[filtered["t1_models"].map(clean).isin(model_filter)]

top = st.columns(6)
top[0].metric("Joined labels", f"{len(filtered):,}")
top[1].metric("Labels with T1", f"{int(filtered['has_t1'].sum()):,}" if not filtered.empty else "0")
top[2].metric("Labels with T2", f"{int(filtered['has_t2'].sum()):,}" if not filtered.empty else "0")
top[3].metric("T1 failed labels", f"{int(filtered['t1_failure_count'].fillna(0).gt(0).sum()):,}" if not filtered.empty else "0")
top[4].metric("T2 hybrid errors", f"{int(filtered['hybrid_error'].map(clean).ne('').sum()):,}" if not filtered.empty else "0")
top[5].metric("Joined complete", f"{int(filtered['pipeline_status'].eq('t1+t2').sum()):,}" if not filtered.empty else "0")

st.caption(f"T1 output: `{t1_path}`")
st.caption(f"T2 output: `{t2_path}`")

tabs = st.tabs(["Overview", "Label Audit", "T1 Records", "T2 Predictions", "Exports"])

with tabs[0]:
    st.markdown(
        "This overview helps you spot records that only reached one stage of the pipeline, records with T1 failures, and records whose T2 outputs look weak or incomplete."
    )
    c1, c2 = st.columns(2)
    with c1:
        if not filtered.empty:
            status_counts = filtered["pipeline_status"].value_counts().rename_axis("pipeline_status").reset_index(name="count")
            bar(status_counts, "pipeline_status", "count", title="Pipeline Status by Label")
        else:
            st.info("No joined labels are available.")
    with c2:
        if not filtered.empty:
            rule_counts = filtered["rule_tone"].map(lambda v: clean(v) or "missing").value_counts().rename_axis("rule_tone").reset_index(name="count")
            bar(rule_counts, "rule_tone", "count", title="T2 Rule Tone Distribution")
        else:
            st.info("No T2 rule tones are available.")

    if not filtered.empty:
        risk = filtered[
            filtered["pipeline_status"].ne("t1+t2")
            | filtered["t1_failure_count"].fillna(0).gt(0)
            | filtered["hybrid_error"].map(clean).ne("")
        ].copy()
        st.markdown("**Priority audit queue**")
        st.dataframe(
            risk[
                [
                    "label",
                    "pipeline_status",
                    "t1_models",
                    "t1_failure_count",
                    "t1_prediction_labels",
                    "rule_tone",
                    "hybrid_tones",
                    "hybrid_error",
                ]
            ].head(int(preview_limit)),
            use_container_width=True,
            height=360,
        )

with tabs[1]:
    if filtered.empty:
        st.warning("No labels are available for inspection.")
    else:
        label_choice = st.selectbox("Select label", filtered["label"].tolist())
        selected_row = filtered[filtered["label"] == label_choice].iloc[0]
        selected_t1 = t1[t1["label"] == label_choice].copy()
        selected_t2_label = t2_labels[t2_labels["label"] == label_choice].copy()
        selected_t2_predictions = t2_predictions[t2_predictions["label"] == label_choice].copy()

        st.markdown("**Source text**")
        st.text_area("text", value=clean(selected_row.get("text_joined")), height=220, disabled=True, label_visibility="collapsed")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("T1 runs", f"{int(selected_row.get('t1_total_runs') or 0):,}")
        c2.metric("T1 failures", f"{int(selected_row.get('t1_failure_count') or 0):,}")
        c3.metric("T2 predictions", f"{int(selected_row.get('prediction_count') or 0):,}")
        c4.metric("Greenwashing index", f"{float(selected_row.get('greenwashing_index')):.3f}" if pd.notna(selected_row.get("greenwashing_index")) else "n/a")

        st.markdown("**Joined label summary**")
        summary_cols = [
            "label",
            "pipeline_status",
            "t1_models",
            "t1_prediction_labels",
            "avg_prediction_score",
            "rule_aspects",
            "rule_polarity",
            "rule_tone",
            "hybrid_tones",
            "hybrid_sentiments",
            "ontology_consistency",
            "avg_ontology_alignment",
            "avg_tone_score",
            "greenwashing_index",
            "hybrid_error",
        ]
        st.dataframe(pd.DataFrame([selected_row[summary_cols].to_dict()]), use_container_width=True, height=220)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**T1 runs for label**")
            st.dataframe(selected_t1.head(int(preview_limit)), use_container_width=True, height=320)
        with c2:
            st.markdown("**T2 sentence predictions for label**")
            st.dataframe(selected_t2_predictions.head(int(preview_limit)), use_container_width=True, height=320)

        if not selected_t2_label.empty:
            st.markdown("**T2 label-level metrics**")
            st.dataframe(selected_t2_label.head(int(preview_limit)), use_container_width=True, height=220)

with tabs[2]:
    if t1.empty:
        st.warning("No T1 records were found.")
    else:
        failure_only = st.checkbox("Show only failed T1 rows", value=False)
        t1_view = t1[~t1["success"]] if failure_only else t1
        st.dataframe(t1_view.head(int(preview_limit)), use_container_width=True, height=560)

with tabs[3]:
    if t2_predictions.empty and t2_labels.empty:
        st.warning("No T2 records were found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("T2 label-level outputs")
            st.dataframe(t2_labels.head(int(preview_limit)), use_container_width=True, height=520)
        with c2:
            st.subheader("T2 sentence-level predictions")
            st.dataframe(t2_predictions.head(int(preview_limit)), use_container_width=True, height=520)

with tabs[4]:
    st.download_button(
        "Download joined label audit CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        "ground_truth_joined_label_audit.csv",
        "text/csv",
    )
    st.download_button(
        "Download T1 flattened CSV",
        t1.to_csv(index=False).encode("utf-8"),
        "ground_truth_t1_flattened.csv",
        "text/csv",
    )
    st.download_button(
        "Download T2 sentence predictions CSV",
        t2_predictions.to_csv(index=False).encode("utf-8"),
        "ground_truth_t2_sentence_predictions.csv",
        "text/csv",
    )
