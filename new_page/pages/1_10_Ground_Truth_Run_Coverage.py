from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Ground Truth Run Coverage", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
RESULTS_DIR = ROOT / "results"
DEFAULT_SOURCE_PATH = RESULTS_DIR / "esg_records.json"
DEFAULT_T1_JSONL = RESULTS_DIR / "t1_results.jsonl"
DEFAULT_T2_JSONL = RESULTS_DIR / "t2_results.jsonl"

from graph_attachment_gallery import render_attachment_cards  # noqa: E402


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


def load_t1_records(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []

    if path.suffix == ".jsonl":
        records: list[dict[str, Any]] = []
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
        models = sorted({clean(row.get("model")) for row in records if clean(row.get("model"))})
        return records, models

    obj = load_json(path)
    if isinstance(obj, dict):
        records = [row for row in obj.get("records", []) if isinstance(row, dict)]
        models = [clean(row) for row in obj.get("models", []) if clean(row)]
        if not models:
            models = sorted({clean(row.get("model")) for row in records if clean(row.get("model"))})
        return records, models
    if isinstance(obj, list):
        records = [row for row in obj if isinstance(row, dict)]
        models = sorted({clean(row.get("model")) for row in records if clean(row.get("model"))})
        return records, models
    return [], []


def load_t2_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
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


def extract_source_items(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    data = load_json(path)
    if not isinstance(data, list):
        return []

    items: list[dict[str, str]] = []
    for idx, row in enumerate(data):
        if isinstance(row, dict):
            if row.get("text"):
                items.append(
                    {
                        "label": clean(row.get("label") or row.get("target") or f"row_{idx}"),
                        "text": clean(row.get("text")),
                    }
                )
                continue

            records = row.get("records")
            if isinstance(records, list) and records:
                base = clean(row.get("target") or row.get("label") or f"row_{idx}")
                for rec_idx, rec in enumerate(records, start=1):
                    if isinstance(rec, dict) and clean(rec.get("text")):
                        items.append(
                            {
                                "label": f"{base}/rec_{rec_idx}",
                                "text": clean(rec.get("text")),
                            }
                        )
                continue

            raw_output = row.get("raw_output")
            if raw_output:
                try:
                    parsed = json.loads(raw_output)
                except Exception:
                    parsed = None
                if isinstance(parsed, list):
                    base = clean(row.get("target") or row.get("label") or f"row_{idx}")
                    for rec_idx, rec in enumerate(parsed, start=1):
                        if isinstance(rec, dict) and clean(rec.get("text")):
                            items.append(
                                {
                                    "label": f"{base}/raw_{rec_idx}",
                                    "text": clean(rec.get("text")),
                                }
                            )
        elif isinstance(row, str) and row.strip():
            items.append({"label": f"row_{idx}", "text": row.strip()})
    return items


def flatten_t1(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(
            {
                "timestamp": clean(record.get("timestamp")),
                "label": clean(record.get("label")),
                "model": clean(record.get("model")),
                "backend": clean(record.get("backend")),
                "text": clean(record.get("text")),
                "success": bool(record.get("success")),
                "error": clean(record.get("error")),
            }
        )
    return pd.DataFrame(rows)


def flatten_t2(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in records:
        hybrid = record.get("hybrid") if isinstance(record.get("hybrid"), dict) else {}
        rows.append(
            {
                "timestamp": clean(record.get("timestamp")),
                "label": clean(record.get("label")),
                "text": clean(record.get("text")),
                "has_hybrid_error": bool(clean(hybrid.get("error"))),
                "hybrid_error": clean(hybrid.get("error")),
                "prediction_rows": len(hybrid.get("predictions", [])) if isinstance(hybrid.get("predictions"), list) else 0,
            }
        )
    return pd.DataFrame(rows)


def first_non_empty(series: pd.Series) -> str:
    for value in series:
        value = clean(value)
        if value:
            return value
    return ""


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


st.title("Ground Truth Run Coverage")
st.caption(
    "Track what the resumable `ground_truth.py` pipeline has already processed, which `label x model` tasks are still missing, and whether T2 has covered each source label."
)

available_t1_json = sorted(RESULTS_DIR.glob("t1_run_*.json"))
default_t1_path = DEFAULT_T1_JSONL if DEFAULT_T1_JSONL.exists() else (available_t1_json[-1] if available_t1_json else DEFAULT_T1_JSONL)

with st.sidebar:
    st.header("Files")
    source_path_input = st.text_input("Source input JSON", str(DEFAULT_SOURCE_PATH))
    t1_path_input = st.text_input("T1 output path", str(default_t1_path))
    t2_path_input = st.text_input("T2 output path", str(DEFAULT_T2_JSONL))
    expected_models_raw = st.text_area(
        "Expected T1 models",
        value="",
        help="Optional. Enter one model per line or comma-separated if you want coverage against a specific intended model set.",
    )
    label_limit = st.number_input("Missing-label preview limit", min_value=25, value=200, step=25)
    if st.button("Refresh coverage", use_container_width=True):
        st.rerun()

source_path = Path(source_path_input).expanduser()
t1_path = Path(t1_path_input).expanduser()
t2_path = Path(t2_path_input).expanduser()

source_items = extract_source_items(source_path)
t1_records_raw, t1_models_from_file = load_t1_records(t1_path)
t2_records_raw = load_t2_records(t2_path)

t1 = flatten_t1(t1_records_raw)
t2 = flatten_t2(t2_records_raw)

expected_models = [clean(v) for chunk in expected_models_raw.splitlines() for v in chunk.split(",") if clean(v)]
if not expected_models:
    expected_models = t1_models_from_file

source_df = pd.DataFrame(source_items)
if source_df.empty:
    inferred_labels = sorted(
        {
            *{clean(v) for v in t1.get("label", pd.Series(dtype=str)).tolist() if clean(v)},
            *{clean(v) for v in t2.get("label", pd.Series(dtype=str)).tolist() if clean(v)},
        }
    )
    source_df = pd.DataFrame({"label": inferred_labels, "text": [""] * len(inferred_labels)})
    source_caption = "source file missing; label universe inferred from outputs"
else:
    source_caption = f"source labels reconstructed from `{source_path}`"

source_labels = sorted(source_df["label"].map(clean).unique().tolist()) if not source_df.empty else []

t1_unique = pd.DataFrame(columns=["label", "model", "success", "error", "backend", "attempts"])
if not t1.empty:
    t1_unique = (
        t1.groupby(["label", "model"], dropna=False)
        .agg(
            success=("success", "max"),
            error=("error", first_non_empty),
            backend=("backend", first_non_empty),
            attempts=("label", "size"),
        )
        .reset_index()
    )

t2_unique = pd.DataFrame(columns=["label", "prediction_rows", "has_hybrid_error", "hybrid_error", "attempts"])
if not t2.empty:
    t2_unique = (
        t2.groupby("label", dropna=False)
        .agg(
            prediction_rows=("prediction_rows", "max"),
            has_hybrid_error=("has_hybrid_error", "max"),
            hybrid_error=("hybrid_error", first_non_empty),
            attempts=("label", "size"),
        )
        .reset_index()
    )

t1_done_pairs = set(zip(t1_unique["label"], t1_unique["model"])) if not t1_unique.empty else set()
t2_done_labels = set(t2_unique["label"]) if not t2_unique.empty else set()

expected_pair_rows: list[dict[str, Any]] = []
if source_labels and expected_models:
    for label in source_labels:
        for model in expected_models:
            expected_pair_rows.append({"label": label, "model": model})

expected_pairs_df = pd.DataFrame(expected_pair_rows)
if not expected_pairs_df.empty:
    t1_coverage = expected_pairs_df.merge(t1_unique, on=["label", "model"], how="left")
    t1_coverage["done"] = t1_coverage["success"].notna()
    t1_coverage["status"] = t1_coverage["done"].map({True: "done", False: "missing"})
else:
    t1_coverage = t1_unique.copy()
    if not t1_coverage.empty:
        t1_coverage["done"] = True
        t1_coverage["status"] = "done"

t2_coverage = source_df[["label"]].drop_duplicates().copy() if not source_df.empty else pd.DataFrame(columns=["label"])
if not t2_coverage.empty:
    t2_coverage = t2_coverage.merge(t2_unique, on="label", how="left")
    t2_coverage["done"] = t2_coverage["prediction_rows"].notna() | t2_coverage["has_hybrid_error"].notna()
    t2_coverage["status"] = t2_coverage["done"].map({True: "done", False: "missing"})

top = st.columns(6)
top[0].metric("Source labels", f"{len(source_labels):,}")
top[1].metric("Expected T1 models", f"{len(expected_models):,}")
top[2].metric("Expected T1 tasks", f"{len(expected_pairs_df):,}" if not expected_pairs_df.empty else "n/a")
top[3].metric("Completed T1 tasks", f"{int(t1_coverage['done'].sum()):,}" if not t1_coverage.empty and "done" in t1_coverage else "0")
top[4].metric("Completed T2 labels", f"{int(t2_coverage['done'].sum()):,}" if not t2_coverage.empty and "done" in t2_coverage else f"{len(t2_done_labels):,}")
top[5].metric("T1 duplicate attempts", f"{int((t1_unique['attempts'] > 1).sum()):,}" if not t1_unique.empty else "0")

st.caption(f"Coverage basis: {source_caption}")
st.caption(f"T1 output: `{t1_path}`")
st.caption(f"T2 output: `{t2_path}`")

tabs = st.tabs(["Overview", "T1 Matrix", "T2 Coverage", "Missing Work", "Raw Tables", "Attachment Cards"])

with tabs[0]:
    st.markdown(
        "Use this page to answer whether the saved outputs are complete enough to resume safely. "
        "T1 coverage is tracked at `label x model` granularity because the resumable checkpoint logic keys on both fields."
    )

    c1, c2 = st.columns(2)
    with c1:
        if not t1_coverage.empty:
            model_summary = (
                t1_coverage.groupby("model", dropna=False)["done"]
                .agg(total="size", completed="sum")
                .reset_index()
            )
            model_summary["completion_pct"] = (model_summary["completed"] / model_summary["total"] * 100).round(2)
            bar(model_summary, "model", "completion_pct", title="T1 Completion Rate by Model")
            st.dataframe(model_summary.sort_values(["completion_pct", "model"], ascending=[False, True]), use_container_width=True, height=320)
        else:
            st.info("No T1 model coverage could be constructed.")

    with c2:
        if not t2_coverage.empty:
            t2_status_counts = t2_coverage["status"].value_counts().rename_axis("status").reset_index(name="count")
            bar(t2_status_counts, "status", "count", title="T2 Label Coverage")
            t2_errors = t2_coverage[t2_coverage["has_hybrid_error"] == True]
            st.metric("T2 labels with hybrid error", f"{len(t2_errors):,}")
            if not t2_errors.empty:
                st.dataframe(t2_errors[["label", "hybrid_error", "attempts"]].head(int(label_limit)), use_container_width=True, height=260)
        else:
            st.info("No T2 coverage could be constructed.")

with tabs[1]:
    st.markdown(
        "This matrix shows the exact resumable unit for T1. A missing cell means `ground_truth.py` would still schedule that `label x model` task on the next run."
    )
    if t1_coverage.empty or "done" not in t1_coverage:
        st.warning("No T1 coverage matrix is available. Provide a source file and expected model list, or load a T1 output file.")
    else:
        model_order = expected_models or sorted(t1_coverage["model"].map(clean).unique().tolist())
        label_order = source_labels or sorted(t1_coverage["label"].map(clean).unique().tolist())
        matrix_df = t1_coverage.copy()
        matrix_df["status_text"] = matrix_df["status"].fillna("missing")
        heatmap = (
            alt.Chart(matrix_df)
            .mark_rect()
            .encode(
                x=alt.X("model:N", sort=model_order, title="Model"),
                y=alt.Y("label:N", sort=label_order, title="Label"),
                color=alt.Color(
                    "status_text:N",
                    scale=alt.Scale(domain=["done", "missing"], range=["#217c7e", "#d9d9d9"]),
                    legend=alt.Legend(title="Status"),
                ),
                tooltip=["label", "model", "status_text", "success", "attempts", "error"],
            )
            .properties(height=min(800, 24 * max(len(label_order), 8)), title="T1 Label x Model Completion Matrix")
        )
        st.altair_chart(heatmap, use_container_width=True)

        duplicates = t1_unique[t1_unique["attempts"] > 1].sort_values(["attempts", "label", "model"], ascending=[False, True, True])
        if not duplicates.empty:
            st.markdown("**Repeated T1 attempts**")
            st.dataframe(duplicates.head(int(label_limit)), use_container_width=True, height=260)

with tabs[2]:
    st.markdown(
        "T2 resume state is simpler because it keys only on `label`. This table highlights which source labels never reached a saved T2 record."
    )
    if t2_coverage.empty:
        st.warning("No T2 coverage table is available.")
    else:
        summary = (
            t2_coverage.assign(has_predictions=t2_coverage["prediction_rows"].fillna(0).gt(0))
            [["label", "status", "prediction_rows", "has_predictions", "has_hybrid_error", "attempts", "hybrid_error"]]
            .sort_values(["status", "label"], ascending=[True, True])
        )
        st.dataframe(summary.head(int(label_limit)), use_container_width=True, height=520)

with tabs[3]:
    st.markdown(
        "These exports are the fastest way to decide what a resumed run still needs to process."
    )
    c1, c2 = st.columns(2)
    with c1:
        if not t1_coverage.empty and "done" in t1_coverage:
            missing_t1 = t1_coverage[~t1_coverage["done"]].copy()
        else:
            missing_t1 = pd.DataFrame(columns=["label", "model"])
        st.subheader("Missing T1 tasks")
        st.dataframe(missing_t1.head(int(label_limit)), use_container_width=True, height=440)
        st.download_button(
            "Download missing T1 tasks",
            missing_t1.to_csv(index=False).encode("utf-8"),
            "ground_truth_missing_t1_tasks.csv",
            "text/csv",
        )

    with c2:
        if not t2_coverage.empty and "done" in t2_coverage:
            missing_t2 = t2_coverage[~t2_coverage["done"]].copy()
        else:
            missing_t2 = pd.DataFrame(columns=["label"])
        st.subheader("Missing T2 labels")
        st.dataframe(missing_t2.head(int(label_limit)), use_container_width=True, height=440)
        st.download_button(
            "Download missing T2 labels",
            missing_t2.to_csv(index=False).encode("utf-8"),
            "ground_truth_missing_t2_labels.csv",
            "text/csv",
        )

with tabs[4]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Source labels")
        st.dataframe(source_df.head(int(label_limit)), use_container_width=True, height=500)
    with c2:
        st.subheader("T1 unique tasks")
        st.dataframe(t1_unique.head(int(label_limit)), use_container_width=True, height=500)
    with c3:
        st.subheader("T2 unique labels")
        st.dataframe(t2_unique.head(int(label_limit)), use_container_width=True, height=500)

with tabs[5]:
    render_attachment_cards(
        "Ground Truth Run Coverage Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        rq_default="RQ2",
        figures=["A.13", "A.17", "A.18", "A.19", "A.20"],
    )
