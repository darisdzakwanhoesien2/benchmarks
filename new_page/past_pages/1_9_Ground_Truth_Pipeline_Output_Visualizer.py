from __future__ import annotations

import json
import re
from pathlib import Path
import sys
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Ground Truth Pipeline Output Visualizer", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
RESULTS_DIR = ROOT / "results"
DEFAULT_T1_JSONL = RESULTS_DIR / "t1_results.jsonl"
DEFAULT_T1_JSON = RESULTS_DIR / "t1_results.json"
DEFAULT_T2_JSONL = RESULTS_DIR / "t2_results.jsonl"
DEFAULT_T2_JSON = RESULTS_DIR / "t2_results.json"

from graph_attachment_gallery import render_attachment_cards  # noqa: E402


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def load_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    if path.suffix == ".jsonl":
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                records.append(obj)
        return records
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    if isinstance(obj, list):
        return [row for row in obj if isinstance(row, dict)]
    if isinstance(obj, dict):
        if isinstance(obj.get("records"), list):
            return [row for row in obj["records"] if isinstance(row, dict)]
        return [obj]
    return []


def selected_existing_path(primary: Path, fallback: Path) -> Path:
    return primary if primary.exists() else fallback


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
        if not error and result_label.lower() == "error":
            error = result_raw
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


def values(df: pd.DataFrame, col: str) -> list[str]:
    if col not in df.columns:
        return []
    return sorted(v for v in df[col].map(clean).unique() if v)


def sidebar_filter(df: pd.DataFrame, col: str, label: str, key: str) -> pd.DataFrame:
    opts = values(df, col)
    selected = st.sidebar.multiselect(label, opts, key=key)
    if not selected:
        return df
    return df[df[col].map(clean).isin(selected)]


def count_table(df: pd.DataFrame, col: str, label: str | None = None) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[label or col, "count", "pct"])
    out = (
        df[col]
        .map(clean)
        .replace("", "missing")
        .value_counts()
        .rename_axis(label or col)
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


st.title("Ground Truth Pipeline Output Visualizer")
st.caption(
    "Visualize the saved outputs produced by the ground-truth pipeline page: T1 model predictions, model-load failures, T2 rule-based labels, hybrid labels, ontology alignment, and greenwashing metrics."
)

with st.sidebar:
    st.header("Output Files")
    t1_path_input = st.text_input("T1 output path", str(selected_existing_path(DEFAULT_T1_JSONL, DEFAULT_T1_JSON)))
    t2_path_input = st.text_input("T2 output path", str(selected_existing_path(DEFAULT_T2_JSONL, DEFAULT_T2_JSON)))
    table_limit = st.number_input("Table preview row limit", min_value=50, value=500, step=50)
    if st.button("Refresh output files", use_container_width=True):
        st.rerun()

t1_path = Path(t1_path_input).expanduser()
t2_path = Path(t2_path_input).expanduser()
t1 = flatten_t1(load_json_or_jsonl(t1_path))
t2 = flatten_t2(load_json_or_jsonl(t2_path))

with st.sidebar:
    st.header("T1 Filters")
    t1_filtered = t1.copy()
    for col, label in [
        ("model", "T1 Model"),
        ("backend", "T1 Backend"),
        ("prediction_label", "T1 Prediction Label"),
    ]:
        t1_filtered = sidebar_filter(t1_filtered, col, label, f"t1_{col}")
    t1_status = st.multiselect("T1 Status", ["success", "failed"], key="t1_status")
    if t1_status:
        desired = {item == "success" for item in t1_status}
        t1_filtered = t1_filtered[t1_filtered["success"].isin(desired)]

    st.header("T2 Filters")
    t2_filtered = t2.copy()
    for col, label in [
        ("rule_tone", "Rule-Based Tone"),
        ("tone_pred", "Hybrid Tone"),
        ("sentiment_pred", "Hybrid Sentiment"),
        ("section", "Section"),
        ("ontology_path", "Ontology Path"),
    ]:
        t2_filtered = sidebar_filter(t2_filtered, col, label, f"t2_{col}")

t1_success_rate = t1_filtered["success"].mean() * 100 if not t1_filtered.empty and "success" in t1_filtered else 0.0
t2_error_count = int(t2_filtered["hybrid_error"].map(clean).ne("").sum()) if "hybrid_error" in t2_filtered else 0

overview = st.columns(5)
overview[0].metric("T1 rows", f"{len(t1_filtered):,}")
overview[1].metric("T1 success rate", f"{t1_success_rate:.1f}%")
overview[2].metric("T1 models", f"{t1_filtered['model'].nunique():,}" if "model" in t1_filtered else "0")
overview[3].metric("T2 rows", f"{len(t2_filtered):,}")
overview[4].metric("T2 hybrid errors", f"{t2_error_count:,}")

st.caption(f"T1 output: `{t1_path}`")
st.caption(f"T2 output: `{t2_path}`")

tabs = st.tabs(["T1 Model Results", "T1 Failures", "T2 Hybrid Results", "Ontology & Greenwashing", "Comparisons", "Records & Exports", "Attachment Cards"])

with tabs[0]:
    st.markdown(
        "T1 is the ClimateBERT/local-model classification layer. This tab shows which models produced outputs, which labels they produced, and how confident those outputs were."
    )
    if t1_filtered.empty:
        st.warning("No T1 rows were found. Run T1 in the pipeline or point this page to a T1 JSON/JSONL output.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            status_counts = count_table(t1_filtered.assign(status=t1_filtered["success"].map({True: "success", False: "failed"})), "status")
            bar(status_counts, "status", title="T1 Run Status")
        with c2:
            bar(count_table(t1_filtered, "prediction_label"), "prediction_label", title="T1 Prediction Labels")

        model_counts = (
            t1_filtered.assign(status=t1_filtered["success"].map({True: "success", False: "failed"}))
            .groupby(["model", "status"], dropna=False)
            .size()
            .reset_index(name="count")
        )
        bar(model_counts, "model", color="status", title="T1 Status by Model")
        histogram(t1_filtered, "prediction_score", "T1 Prediction Score Distribution")

with tabs[1]:
    st.markdown(
        "This tab turns the live checklist-style output into an error audit. It is especially useful for local model folders that fail to load or incompatible ClimateBERT checkpoints."
    )
    if t1_filtered.empty:
        st.warning("No T1 rows were found.")
    else:
        failures = t1_filtered[~t1_filtered["success"] | t1_filtered["error"].map(clean).ne("")].copy()
        c1, c2 = st.columns(2)
        with c1:
            bar(count_table(failures, "model"), "model", title="Failures by Model")
        with c2:
            error_counts = count_table(failures.assign(error_short=failures["error"].map(lambda v: clean(v)[:140])), "error_short")
            bar(error_counts.head(20), "error_short", title="Most Frequent Error Messages")
        st.dataframe(failures.head(int(table_limit)), use_container_width=True, height=460)

with tabs[2]:
    st.markdown(
        "T2 is the rule-based and hybrid ESG interpretation layer. This tab visualizes tone, sentiment, and model confidence from the hybrid output."
    )
    if t2_filtered.empty:
        st.warning("No T2 rows were found. Run T2 in the pipeline or point this page to a T2 JSON/JSONL output.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            bar(count_table(t2_filtered, "rule_tone"), "rule_tone", title="Rule-Based Tone")
        with c2:
            bar(count_table(t2_filtered, "tone_pred"), "tone_pred", title="Hybrid Tone")

        c3, c4 = st.columns(2)
        with c3:
            bar(count_table(t2_filtered, "sentiment_pred"), "sentiment_pred", title="Hybrid Sentiment")
        with c4:
            histogram(t2_filtered, "tone_score", "Hybrid Tone Score Distribution")

with tabs[3]:
    st.markdown(
        "Ontology and greenwashing outputs explain whether the ESG classification is structurally coherent and whether the text looks more like commitment language than measured outcome evidence."
    )
    if t2_filtered.empty:
        st.warning("No T2 rows were found.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            histogram(t2_filtered, "ontology_alignment", "Ontology Alignment Distribution")
        with c2:
            histogram(t2_filtered, "greenwashing_index", "Greenwashing Index Distribution")

        path_counts = count_table(t2_filtered, "ontology_path")
        bar(path_counts.head(25), "ontology_path", title="Top Ontology Paths")
        high_greenwashing = t2_filtered.sort_values("greenwashing_index", ascending=False, na_position="last")
        st.markdown("**Highest greenwashing-index rows**")
        st.dataframe(high_greenwashing.head(int(table_limit)), use_container_width=True, height=420)

with tabs[4]:
    st.markdown(
        "These comparisons show how much the rule-based tone agrees with the hybrid tone and where the pipeline needs manual review."
    )
    if t2_filtered.empty:
        st.warning("No T2 rows were found.")
    else:
        comparable = t2_filtered[t2_filtered["rule_tone"].map(clean).ne("") & t2_filtered["tone_pred"].map(clean).ne("")].copy()
        if comparable.empty:
            st.info("No paired rule/hybrid tone labels are available.")
        else:
            comparable["rule_tone_clean"] = comparable["rule_tone"].str.lower()
            comparable["hybrid_tone_clean"] = comparable["tone_pred"].str.lower()
            comparable["tone_agrees"] = comparable["rule_tone_clean"] == comparable["hybrid_tone_clean"]
            agreement = comparable["tone_agrees"].mean() * 100
            c1, c2, c3 = st.columns(3)
            c1.metric("Comparable rows", f"{len(comparable):,}")
            c2.metric("Rule/hybrid tone agreement", f"{agreement:.1f}%")
            c3.metric("Disagreements", f"{int((~comparable['tone_agrees']).sum()):,}")

            cm = comparable.groupby(["rule_tone_clean", "hybrid_tone_clean"]).size().reset_index(name="count")
            heatmap = (
                alt.Chart(cm)
                .mark_rect()
                .encode(
                    x=alt.X("hybrid_tone_clean:N", title="Hybrid Tone"),
                    y=alt.Y("rule_tone_clean:N", title="Rule-Based Tone"),
                    color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
                    tooltip=["rule_tone_clean", "hybrid_tone_clean", "count"],
                )
                .properties(title="Rule-Based vs Hybrid Tone", height=360)
            )
            text = alt.Chart(cm).mark_text().encode(
                x="hybrid_tone_clean:N",
                y="rule_tone_clean:N",
                text="count:Q",
                color=alt.condition(
                    alt.datum.count > cm["count"].max() * 0.55,
                    alt.value("white"),
                    alt.value("#17202a"),
                ),
            )
            st.altair_chart(heatmap + text, use_container_width=True)

            disagreements = comparable[~comparable["tone_agrees"]]
            st.markdown("**Rule/hybrid tone disagreements**")
            st.dataframe(disagreements.head(int(table_limit)), use_container_width=True, height=420)

with tabs[5]:
    st.markdown(
        "Use these tables to audit individual outputs and export the filtered result sets for documentation or manual annotation."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("T1 records")
        st.dataframe(t1_filtered.head(int(table_limit)), use_container_width=True, height=520)
        st.download_button(
            "Download filtered T1 CSV",
            t1_filtered.to_csv(index=False).encode("utf-8"),
            "filtered_t1_pipeline_outputs.csv",
            "text/csv",
        )
    with c2:
        st.subheader("T2 records")
        st.dataframe(t2_filtered.head(int(table_limit)), use_container_width=True, height=520)
        st.download_button(
            "Download filtered T2 CSV",
            t2_filtered.to_csv(index=False).encode("utf-8"),
            "filtered_t2_pipeline_outputs.csv",
            "text/csv",
        )

with tabs[6]:
    render_attachment_cards(
        "ground_truth.py Pipeline Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        rq_default="RQ2",
        figures=["A.17", "A.18", "A.19", "A.20", "A.22", "A.23", "A.24", "A.25", "A.26", "A.27", "A.28", "A.29"],
    )
