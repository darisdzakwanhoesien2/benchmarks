from __future__ import annotations

from datetime import datetime
import json
import os
import re
from pathlib import Path
import subprocess
import sys
from typing import Any
import uuid

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Ground Truth Step-by-Step Visualizer", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
DEFAULT_SOURCE = RESULTS_DIR / "esg_records.json"
DEFAULT_T1 = RESULTS_DIR / "t1_results.jsonl"
DEFAULT_T2 = RESULTS_DIR / "t2_results.jsonl"
GT_JOBS_DIR = RESULTS_DIR / "ground_truth_background_jobs"
GT_WORKER_PATH = ROOT / "code" / "ground_truth_background_worker.py"
MODELS_CACHE_PATH = Path(__file__).parent / "models_cache.json"


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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


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


def build_processing_coverage(text_units: pd.DataFrame, t1_df: pd.DataFrame, t2_raw: list[dict[str, Any]]) -> pd.DataFrame:
    columns = [
        "source_index",
        "label",
        "source_type",
        "chars",
        "t1_attempts",
        "t1_successes",
        "t1_failures",
        "t1_models",
        "t2_attempts",
        "t2_successes",
        "t2_failures",
        "processing_status",
        "text",
    ]
    if text_units.empty:
        return pd.DataFrame(columns=columns)

    coverage = text_units.copy()
    coverage["label"] = coverage["label"].map(clean)

    if not t1_df.empty and "label" in t1_df.columns:
        t1_status = t1_df.copy()
        t1_status["label"] = t1_status["label"].map(clean)
        if "success" not in t1_status.columns:
            t1_status["success"] = False
        if "model" not in t1_status.columns:
            t1_status["model"] = ""
        t1_summary = (
            t1_status.groupby("label", dropna=False)
            .agg(
                t1_attempts=("label", "size"),
                t1_successes=("success", lambda values: int(pd.Series(values).fillna(False).astype(bool).sum())),
                t1_models=("model", lambda values: ", ".join(sorted(set(clean(v) for v in values if clean(v))))),
            )
            .reset_index()
        )
    else:
        t1_summary = pd.DataFrame(columns=["label", "t1_attempts", "t1_successes", "t1_models"])

    t2_rows: list[dict[str, Any]] = []
    for record in t2_raw:
        if not isinstance(record, dict):
            continue
        hybrid = record.get("hybrid") if isinstance(record.get("hybrid"), dict) else {}
        t2_rows.append(
            {
                "label": clean(record.get("label")),
                "t2_success": not bool(clean(hybrid.get("error"))),
            }
        )
    t2_status = pd.DataFrame(t2_rows)
    if not t2_status.empty and "label" in t2_status.columns:
        t2_summary = (
            t2_status.groupby("label", dropna=False)
            .agg(
                t2_attempts=("label", "size"),
                t2_successes=("t2_success", lambda values: int(pd.Series(values).fillna(False).astype(bool).sum())),
            )
            .reset_index()
        )
    else:
        t2_summary = pd.DataFrame(columns=["label", "t2_attempts", "t2_successes"])

    coverage = coverage.merge(t1_summary, on="label", how="left").merge(t2_summary, on="label", how="left")
    for col in ["t1_attempts", "t1_successes", "t2_attempts", "t2_successes"]:
        coverage[col] = pd.to_numeric(coverage[col], errors="coerce").fillna(0).astype(int)
    coverage["t1_failures"] = (coverage["t1_attempts"] - coverage["t1_successes"]).clip(lower=0)
    coverage["t2_failures"] = (coverage["t2_attempts"] - coverage["t2_successes"]).clip(lower=0)
    coverage["t1_models"] = coverage["t1_models"].fillna("")

    def status(row: pd.Series) -> str:
        has_t1 = int(row["t1_attempts"]) > 0
        has_t2 = int(row["t2_attempts"]) > 0
        if has_t1 and has_t2:
            return "processed_t1_t2"
        if has_t1:
            return "processed_t1_only"
        if has_t2:
            return "processed_t2_only"
        return "not_processed"

    coverage["processing_status"] = coverage.apply(status, axis=1)
    return coverage[columns]


def build_source_row_coverage(processing_coverage: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "source_index",
        "text_units",
        "processed_t1_t2",
        "processed_t1_only",
        "processed_t2_only",
        "not_processed",
        "source_processing_status",
    ]
    if processing_coverage.empty:
        return pd.DataFrame(columns=columns)
    summary = (
        processing_coverage.groupby("source_index", dropna=False)["processing_status"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["processed_t1_t2", "processed_t1_only", "processed_t2_only", "not_processed"]:
        if col not in summary.columns:
            summary[col] = 0
    summary["text_units"] = summary[["processed_t1_t2", "processed_t1_only", "processed_t2_only", "not_processed"]].sum(axis=1)

    def status(row: pd.Series) -> str:
        if int(row["not_processed"]) == int(row["text_units"]):
            return "not_processed"
        if int(row["processed_t1_t2"]) == int(row["text_units"]):
            return "processed_t1_t2"
        return "partially_processed"

    summary["source_processing_status"] = summary.apply(status, axis=1)
    return summary[columns]


def utc_now_id() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def is_process_alive(pid: Any) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def list_ground_truth_jobs() -> list[str]:
    if not GT_JOBS_DIR.exists():
        return []
    return sorted([path.name for path in GT_JOBS_DIR.iterdir() if path.is_dir()], reverse=True)


def ground_truth_jobs_frame() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for job_id in list_ground_truth_jobs():
        job_dir = GT_JOBS_DIR / job_id
        status = load_json(job_dir / "status.json")
        config = load_json(job_dir / "config.json")
        if not isinstance(status, dict):
            status = {}
        if not isinstance(config, dict):
            config = {}
        total = int(status.get("total") or 0)
        completed = int(status.get("completed") or 0)
        rows.append(
            {
                "job_id": job_id,
                "status": clean(status.get("status") or "unknown"),
                "alive": is_process_alive(status.get("pid")),
                "pid": status.get("pid"),
                "progress_pct": round((completed / total * 100), 1) if total else 0.0,
                "completed": completed,
                "total": total,
                "failed": int(status.get("failed") or 0),
                "skipped": int(status.get("skipped") or 0),
                "items": len(config.get("items", [])) if isinstance(config.get("items"), list) else 0,
                "run_t1": bool(config.get("run_t1")),
                "run_t2": bool(config.get("run_t2")),
                "current": clean(status.get("current")),
                "updated_at": clean(status.get("updated_at")),
            }
        )
    return pd.DataFrame(rows)


def chunk_records(records: list[dict[str, Any]], n_chunks: int) -> list[list[dict[str, Any]]]:
    n_chunks = max(1, min(int(n_chunks), max(1, len(records))))
    chunks: list[list[dict[str, Any]]] = [[] for _ in range(n_chunks)]
    for index, record in enumerate(records):
        chunks[index % n_chunks].append(record)
    return [chunk for chunk in chunks if chunk]


def launch_ground_truth_job(job_id: str) -> None:
    job_dir = GT_JOBS_DIR / job_id
    log_path = job_dir / "worker.log"
    err_path = job_dir / "worker.err.log"
    job_dir.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as stdout, err_path.open("ab") as stderr:
        process = subprocess.Popen(
            [sys.executable, str(GT_WORKER_PATH), job_id],
            cwd=str(ROOT),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    status = load_json(job_dir / "status.json")
    if not isinstance(status, dict):
        status = {}
    status.update(
        {
            "job_id": job_id,
            "pid": process.pid,
            "status": "running",
            "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
    )
    write_json(job_dir / "status.json", status)


def model_cache_options() -> list[str]:
    data = load_json(MODELS_CACHE_PATH)
    if isinstance(data, list):
        return [clean(item) for item in data if clean(item)]
    return []


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
processing_coverage = build_processing_coverage(text_units, t1_df, t2_raw)
all_processing_coverage = processing_coverage.copy()
source_coverage = build_source_row_coverage(processing_coverage)

if search.strip():
    needle = search.strip().lower()
    for name, df in [("text_units", text_units), ("t1_df", t1_df), ("t2_df", t2_df), ("processing_coverage", processing_coverage)]:
        if df.empty:
            continue
        mask = pd.Series(False, index=df.index)
        for column in [col for col in ["label", "text", "sentence_text"] if col in df.columns]:
            mask = mask | df[column].map(lambda value: needle in clean(value).lower())
        if name == "text_units":
            text_units = df[mask]
        elif name == "t1_df":
            t1_df = df[mask]
        elif name == "t2_df":
            t2_df = df[mask]
        else:
            processing_coverage = df[mask]
            source_coverage = build_source_row_coverage(processing_coverage)

with st.sidebar:
    st.header("Processing Coverage")
    status_options = [
        "processed_t1_t2",
        "processed_t1_only",
        "processed_t2_only",
        "not_processed",
    ]
    selected_statuses = st.multiselect("Text-unit processing status", status_options, default=[])
    if selected_statuses and not processing_coverage.empty:
        processing_coverage = processing_coverage[processing_coverage["processing_status"].isin(selected_statuses)]
        source_coverage = build_source_row_coverage(processing_coverage)

metric_cols = st.columns(8)
metric_cols[0].metric("Source rows", f"{len(source_df):,}")
metric_cols[1].metric("Extracted text units", f"{len(text_units):,}")
metric_cols[2].metric("T1 raw rows", f"{len(t1_raw):,}")
metric_cols[3].metric("T1 success", f"{(t1_df['success'].mean() * 100):.1f}%" if not t1_df.empty and "success" in t1_df else "0.0%")
metric_cols[4].metric("T2 raw rows", f"{len(t2_raw):,}")
metric_cols[5].metric("T2 visual rows", f"{len(t2_df):,}")
metric_cols[6].metric("Processed T1+T2", f"{int((processing_coverage['processing_status'] == 'processed_t1_t2').sum()):,}" if not processing_coverage.empty else "0")
metric_cols[7].metric("Not processed", f"{int((processing_coverage['processing_status'] == 'not_processed').sum()):,}" if not processing_coverage.empty else "0")

st.caption(f"Source: `{source_path}`")
st.caption(f"T1: `{t1_path}`")
st.caption(f"T2: `{t2_path}`")

tabs = st.tabs(
    [
        "1 Source Records",
        "2 Extracted Text Units",
        "3 Processing Coverage",
        "4 T1 Raw Output",
        "5 T1 Predictions",
        "6 T2 Raw Output",
        "7 T2 Hybrid Output",
        "8 Audit & Exports",
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
    st.markdown("This compares every extracted source text unit against the saved T1 and T2 output files. `ground_truth.py` resumes by label, so rows with no matching label are the ones not processed yet.")
    if processing_coverage.empty:
        st.warning("No extracted text units are available for processing coverage.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            bar(count_frame(processing_coverage, "processing_status"), "processing_status", "Text-Unit Processing Status")
        with c2:
            bar(count_frame(source_coverage, "source_processing_status"), "source_processing_status", "Source Row Processing Status", color="#2563eb")

        st.subheader("Source row coverage")
        st.dataframe(source_coverage.head(int(preview_limit)), use_container_width=True, height=300)
        st.download_button(
            "Download source row coverage CSV",
            source_coverage.to_csv(index=False).encode("utf-8"),
            "ground_truth_source_row_processing_coverage.csv",
            "text/csv",
        )

        st.subheader("Text-unit coverage")
        st.dataframe(processing_coverage.head(int(preview_limit)), use_container_width=True, height=460)
        st.download_button(
            "Download text-unit coverage CSV",
            processing_coverage.to_csv(index=False).encode("utf-8"),
            "ground_truth_text_unit_processing_coverage.csv",
            "text/csv",
        )

        st.subheader("Background processing for missing rows")
        st.markdown("Queue unprocessed text units into independent background chunks. The workers write to the same `t1_results.jsonl` and `t2_results.jsonl` files as `ground_truth.py`, so the run can continue even when the browser page is not visible.")

        bg_left, bg_right = st.columns([1, 1])
        with bg_left:
            bg_statuses = st.multiselect(
                "Rows to queue",
                ["not_processed", "processed_t1_only", "processed_t2_only"],
                default=["not_processed"],
                help="Use `not_processed` for new rows. Use the partial statuses to finish only the missing side of an interrupted run.",
            )
            run_t2_background = st.checkbox("Run T2 rule/hybrid processing", value=True)
            run_t1_background = st.checkbox("Run T1 ClimateBERT processing", value=False)
            n_chunks = st.number_input("Split into N background chunks", min_value=1, max_value=50, value=4, step=1)
        with bg_right:
            model_options = model_cache_options()
            free_models = [model for model in model_options if ":free" in model or "free" in model.lower()]
            default_models = free_models[:1] or model_options[:1]
            selected_models = st.multiselect(
                "T1 ClimateBERT model ids",
                options=model_options,
                default=default_models if run_t1_background else [],
                disabled=not run_t1_background,
            )
            extra_models_text = st.text_area(
                "Additional T1 model ids, one per line",
                value="",
                height=90,
                disabled=not run_t1_background,
            )
            include_current_filter = st.checkbox(
                "Use current search/status filtered table",
                value=False,
                help="Off means queue from the full source coverage table. On means queue only rows currently visible after search/status filters.",
            )

        candidate_source = processing_coverage if include_current_filter else all_processing_coverage
        if bg_statuses and not candidate_source.empty:
            bg_candidates = candidate_source[candidate_source["processing_status"].isin(bg_statuses)].copy()
        else:
            bg_candidates = pd.DataFrame(columns=candidate_source.columns)

        bg_models = [clean(model) for model in selected_models if clean(model)]
        bg_models.extend([line.strip() for line in extra_models_text.splitlines() if line.strip()])
        bg_models = sorted(set(bg_models))
        bg_total_tasks = (len(bg_candidates) if run_t2_background else 0) + (len(bg_candidates) * len(bg_models) if run_t1_background else 0)

        summary_cols = st.columns(4)
        summary_cols[0].metric("Candidate text units", f"{len(bg_candidates):,}")
        summary_cols[1].metric("Chunks to start", f"{min(int(n_chunks), max(1, len(bg_candidates))) if len(bg_candidates) else 0:,}")
        summary_cols[2].metric("Queued T1 models", f"{len(bg_models):,}" if run_t1_background else "0")
        summary_cols[3].metric("Total operations", f"{bg_total_tasks:,}")

        can_start_background = (
            len(bg_candidates) > 0
            and (run_t1_background or run_t2_background)
            and (not run_t1_background or bool(bg_models))
        )
        if run_t1_background and not bg_models:
            st.warning("Select or type at least one T1 model id before starting T1 background processing.")

        if st.button("Start background processing chunks", disabled=not can_start_background, use_container_width=True):
            GT_JOBS_DIR.mkdir(parents=True, exist_ok=True)
            batch_id = f"gt_bg_{utc_now_id()}_{uuid.uuid4().hex[:6]}"
            queued_records = bg_candidates[["source_index", "label", "source_type", "chars", "text"]].to_dict("records")
            chunks = chunk_records(queued_records, int(n_chunks))
            started_ids: list[str] = []
            created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            for part_index, chunk in enumerate(chunks, start=1):
                job_id = f"{batch_id}_part_{part_index:03d}"
                job_dir = GT_JOBS_DIR / job_id
                config = {
                    "job_id": job_id,
                    "batch_id": batch_id,
                    "part": part_index,
                    "parts": len(chunks),
                    "items": chunk,
                    "run_t1": bool(run_t1_background),
                    "run_t2": bool(run_t2_background),
                    "t1_backend": "ClimateBERT API",
                    "models": bg_models,
                    "created_at": created_at,
                }
                total = (len(chunk) * len(bg_models) if run_t1_background else 0) + (len(chunk) if run_t2_background else 0)
                write_json(job_dir / "config.json", config)
                write_json(
                    job_dir / "status.json",
                    {
                        "job_id": job_id,
                        "batch_id": batch_id,
                        "status": "queued",
                        "total": total,
                        "completed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "current": "Queued",
                        "created_at": created_at,
                        "updated_at": created_at,
                    },
                )
                launch_ground_truth_job(job_id)
                started_ids.append(job_id)
            st.success(f"Started {len(started_ids)} background job(s) for batch `{batch_id}`.")
            st.rerun()

        jobs_df = ground_truth_jobs_frame()
        st.subheader("Background job monitor")
        if jobs_df.empty:
            st.info("No ground-truth background jobs have been started yet.")
        else:
            live_cols = st.columns(5)
            live_cols[0].metric("Jobs", f"{len(jobs_df):,}")
            live_cols[1].metric("Running", f"{int(jobs_df['alive'].sum()):,}")
            live_cols[2].metric("Completed ops", f"{int(jobs_df['completed'].sum()):,}")
            live_cols[3].metric("Failed ops", f"{int(jobs_df['failed'].sum()):,}")
            live_cols[4].metric("Skipped ops", f"{int(jobs_df['skipped'].sum()):,}")
            st.dataframe(jobs_df.head(int(preview_limit)), use_container_width=True, height=360)

with tabs[3]:
    st.markdown("T1 appends one JSONL row per `label x model` classification into `results/t1_results.jsonl`.")
    if not t1_raw:
        st.warning("No T1 raw rows found.")
    else:
        st.json(t1_raw[: min(5, int(preview_limit))], expanded=False)

with tabs[4]:
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

with tabs[5]:
    st.markdown("T2 appends one JSONL row per text label into `results/t2_results.jsonl`, including rule-based and hybrid outputs.")
    if not t2_raw:
        st.warning("No T2 raw rows found.")
    else:
        st.json(t2_raw[: min(5, int(preview_limit))], expanded=False)

with tabs[6]:
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

with tabs[7]:
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
