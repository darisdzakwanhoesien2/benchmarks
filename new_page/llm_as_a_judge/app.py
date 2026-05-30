from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import streamlit as st

try:
    import altair as alt  # type: ignore
except Exception:  # pragma: no cover
    alt = None

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
DEFAULT_ESG_RECORDS_PATH = RESULTS_DIR / "esg_records.json"
DEFAULT_JUDGE_DIR = RESULTS_DIR / "llm_judge"


def _clean(value: Any) -> str:
    if value is None:
        return ""
    if pd is not None and isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


@st.cache_data(show_spinner=False)
def _load_json_list(path: Path) -> list[dict[str, Any]]:
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


@st.cache_data(show_spinner=False)
def _load_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
            if limit is not None and len(rows) >= limit:
                break
    return rows


def _flatten_esg_runs(runs: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    if pd is None:  # pragma: no cover
        raise RuntimeError("pandas is required to flatten ESG runs")
    run_rows: list[dict[str, Any]] = []
    record_rows: list[dict[str, Any]] = []

    for run_idx, run in enumerate(runs):
        records = run.get("records") if isinstance(run.get("records"), list) else []
        target = _clean(run.get("target"))
        company = target.split("/")[0] if target else ""

        run_rows.append(
            {
                "run_idx": run_idx,
                "timestamp": _clean(run.get("timestamp")),
                "model": _clean(run.get("model")),
                "prompt": _clean(run.get("prompt")),
                "target": target,
                "company": company,
                "ok": bool(run.get("ok")),
                "n_records": len(records),
                "error_type": _clean(run.get("error_type")),
                "error": _clean(run.get("error")),
                "background_job_id": _clean(run.get("background_job_id")),
            }
        )

        for record_idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                continue
            labels_val = rec.get("labels", [])
            if isinstance(labels_val, list):
                labels = " | ".join(_clean(v) for v in labels_val if _clean(v))
            else:
                labels = _clean(labels_val)

            text = _clean(rec.get("text"))
            record_rows.append(
                {
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": _clean(run.get("timestamp")),
                    "model": _clean(run.get("model")),
                    "prompt": _clean(run.get("prompt")),
                    "target": target,
                    "company": company,
                    "text": text,
                    "text_len_chars": len(text),
                    "aspect": _clean(rec.get("aspect")),
                    "labels": labels,
                    "esg": _clean(rec.get("esg")).upper(),
                    "tone": _clean(rec.get("tone")).lower(),
                    "sentiment": _clean(rec.get("sentiment")).lower(),
                    "sentiment_score": pd.to_numeric(rec.get("sentiment_score"), errors="coerce"),
                    "reasoning": _clean(rec.get("reasoning")),
                }
            )

    return pd.DataFrame(run_rows), pd.DataFrame(record_rows)


def _count_df(df: pd.DataFrame, col: str, label: str | None = None) -> pd.DataFrame:
    if pd is None:  # pragma: no cover
        return pd.DataFrame()  # type: ignore[return-value]
    label = label or col
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[label, "count", "pct"])
    out = (
        df[col]
        .map(_clean)
        .replace("", "missing")
        .value_counts()
        .rename_axis(label)
        .reset_index(name="count")
    )
    total = int(out["count"].sum())
    out["pct"] = (out["count"] / total * 100).round(2) if total else 0.0
    return out


def _render_bar(df: pd.DataFrame, cat_col: str, title: str, max_rows: int = 30) -> None:
    counts = _count_df(df, cat_col, label="category").head(max_rows)
    st.markdown(f"**{title}**")
    if counts.empty:
        st.caption("No data.")
        return
    if alt is None:
        chart_df = counts.set_index("category")[["count"]]
        st.bar_chart(chart_df, height=max(280, 18 * len(counts)))
        st.dataframe(counts, use_container_width=True, height=240)
        return

    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Count"),
            y=alt.Y("category:N", sort="-x", title=None),
            tooltip=["category:N", "count:Q", "pct:Q"],
        )
        .properties(height=max(280, 18 * len(counts)))
    )
    st.altair_chart(chart, use_container_width=True)


@dataclass(frozen=True)
class JudgeFiles:
    records_jsonl: Path
    summary_csv: Path


def _discover_judge_files(judge_dir: Path) -> JudgeFiles:
    return JudgeFiles(
        records_jsonl=judge_dir / "judge_records.jsonl",
        summary_csv=judge_dir / "judge_summary.csv",
    )


def _safe_read_csv(path: Path) -> pd.DataFrame:
    if pd is None:  # pragma: no cover
        return pd.DataFrame()  # type: ignore[return-value]
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def main() -> None:
    st.set_page_config(page_title="LLM-as-a-Judge", layout="wide")
    st.title("LLM-as-a-Judge (Dataset Explorer + Research Plan)")
    st.caption("Uses existing benchmark artifacts; judge outputs are optional.")

    if pd is None:
        st.error("Missing dependency: `pandas`. Install project requirements to run this app.")
        st.stop()

    with st.expander("Research plan (repo-local)", expanded=False):
        plan_path = Path(__file__).with_name("research_plan.md")
        if plan_path.exists():
            st.markdown(plan_path.read_text(encoding="utf-8", errors="ignore"))
        else:
            st.info("Missing `llm_as_a_judge/research_plan.md`.")

    st.sidebar.header("Data sources")
    esg_path = Path(st.sidebar.text_input("T3 extraction dataset", str(DEFAULT_ESG_RECORDS_PATH)))
    judge_dir = Path(st.sidebar.text_input("Judge outputs dir (optional)", str(DEFAULT_JUDGE_DIR)))

    st.sidebar.markdown("---")
    max_records = int(st.sidebar.number_input("Max records to display", min_value=50, max_value=20000, value=2000, step=50))

    runs = _load_json_list(esg_path)
    if not runs:
        st.error(f"No usable runs loaded from: `{esg_path}`")
        st.stop()

    runs_df, records_df = _flatten_esg_runs(runs)

    st.success(f"Loaded {len(runs_df):,} runs and {len(records_df):,} extracted records from `{esg_path.name}`.")

    st.subheader("Quick dataset snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runs", f"{len(runs_df):,}")
    c2.metric("OK runs", f"{int(runs_df['ok'].sum()):,}")
    c3.metric("Records", f"{len(records_df):,}")
    c4.metric("Unique targets", f"{records_df['target'].nunique():,}" if not records_df.empty else "0")

    with st.expander("Run-level distribution", expanded=True):
        left, right = st.columns(2)
        with left:
            _render_bar(runs_df, "model", "Runs by model", max_rows=25)
        with right:
            _render_bar(runs_df, "ok", "Runs by ok status", max_rows=10)

        left2, right2 = st.columns(2)
        with left2:
            _render_bar(records_df, "tone", "Records by tone", max_rows=10)
        with right2:
            _render_bar(records_df, "esg", "Records by ESG", max_rows=10)

    st.subheader("Record browser")
    st.sidebar.header("Filters")
    filter_model = st.sidebar.multiselect("Model", sorted(v for v in records_df["model"].unique() if _clean(v)))
    filter_company = st.sidebar.multiselect("Company", sorted(v for v in records_df["company"].unique() if _clean(v)))
    filter_tone = st.sidebar.multiselect("Tone", sorted(v for v in records_df["tone"].unique() if _clean(v)))
    filter_esg = st.sidebar.multiselect("ESG", sorted(v for v in records_df["esg"].unique() if _clean(v)))

    filtered = records_df
    if filter_model:
        filtered = filtered[filtered["model"].isin(filter_model)]
    if filter_company:
        filtered = filtered[filtered["company"].isin(filter_company)]
    if filter_tone:
        filtered = filtered[filtered["tone"].isin(filter_tone)]
    if filter_esg:
        filtered = filtered[filtered["esg"].isin(filter_esg)]

    st.caption(f"Filtered records: {len(filtered):,}")

    show_cols = [
        "timestamp",
        "model",
        "company",
        "target",
        "aspect",
        "labels",
        "esg",
        "tone",
        "sentiment",
        "sentiment_score",
        "text_len_chars",
    ]
    show_cols = [c for c in show_cols if c in filtered.columns]
    st.dataframe(filtered[show_cols].head(max_records), use_container_width=True, height=420)

    with st.expander("Inspect a single record (text + reasoning)", expanded=False):
        if filtered.empty:
            st.info("No records available under current filters.")
        else:
            idx = int(st.number_input("Row index (in filtered table)", min_value=0, max_value=max(len(filtered) - 1, 0), value=0))
            row = filtered.iloc[idx].to_dict()
            st.markdown(f"**Target**: `{row.get('target','')}`")
            st.markdown(f"**Aspect**: `{row.get('aspect','')}` | **Labels**: `{row.get('labels','')}`")
            st.markdown(f"**ESG/Tone/Sentiment**: `{row.get('esg','')}` / `{row.get('tone','')}` / `{row.get('sentiment','')}`")
            st.text_area("Text", value=_clean(row.get("text")), height=180)
            st.text_area("Model reasoning (if provided)", value=_clean(row.get("reasoning")), height=160)

    st.subheader("Optional: judge outputs")
    judge_files = _discover_judge_files(judge_dir)
    judge_summary_df = _safe_read_csv(judge_files.summary_csv)
    judge_records = _load_jsonl(judge_files.records_jsonl, limit=10000)

    if judge_summary_df.empty and not judge_records:
        st.info(
            "No judge artifacts found yet. Expected files:\n"
            f"- `{judge_files.records_jsonl}`\n"
            f"- `{judge_files.summary_csv}`\n\n"
            "You can still use this app to explore the existing dataset and refine the judging protocol."
        )
    else:
        if not judge_summary_df.empty:
            st.caption(f"Loaded judge summary: {len(judge_summary_df):,} rows from `{judge_files.summary_csv.name}`.")
            st.dataframe(judge_summary_df.head(200), use_container_width=True, height=360)

        if judge_records:
            judge_df = pd.json_normalize(judge_records)
            st.caption(f"Loaded judge records: {len(judge_df):,} rows from `{judge_files.records_jsonl.name}` (showing first 10k).")
            st.dataframe(judge_df.head(200), use_container_width=True, height=360)

    st.subheader("Export")
    export_records = filtered.copy()
    if not export_records.empty:
        csv_bytes = export_records.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered records CSV", data=csv_bytes, file_name="filtered_esg_records.csv", mime="text/csv")


if __name__ == "__main__":
    main()
