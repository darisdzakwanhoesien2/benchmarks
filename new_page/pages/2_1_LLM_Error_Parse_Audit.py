from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="LLM Error & Parse Audit", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
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


def categorize_error(error: str, raw_output: str = "") -> str:
    text = f"{clean(error)}\n{clean(raw_output)}".lower()
    if not text.strip():
        return "none"
    if "empty response" in text:
        return "empty_response"
    if "could not parse json" in text or "parse error" in text:
        return "json_parse_error"
    if "read timed out" in text or "timeout" in text:
        return "timeout"
    if "requires more system memory" in text or "out of memory" in text or "oom" in text:
        return "memory_error"
    if "http 500" in text or "too many 500" in text or "bad gateway" in text:
        return "server_500"
    if "http 413" in text or "request entity too large" in text:
        return "upload_too_large"
    if "connection refused" in text or "failed to establish a new connection" in text:
        return "connection_error"
    if "rate limit" in text or "429" in text:
        return "rate_limit"
    return "other_error"


def raw_json_signal(raw_output: str) -> str:
    raw = clean(raw_output)
    if not raw:
        return "no_raw_output"
    if raw.strip() in {"[]", "{}"}:
        return "empty_json"
    if raw.lstrip().startswith("[") or raw.lstrip().startswith("{"):
        if raw.rstrip().endswith("]") or raw.rstrip().endswith("}"):
            return "json_like_complete"
        return "json_like_truncated_or_malformed"
    if "```" in raw:
        return "markdown_wrapped"
    return "text_not_json"


def flatten_t3_runs(rows: list[dict[str, Any]]) -> pd.DataFrame:
    out = []
    for run_idx, row in enumerate(rows):
        records = row.get("records") if isinstance(row.get("records"), list) else []
        target = clean(row.get("target"))
        company = target.split("/")[0] if target else ""
        error = clean(row.get("error"))
        raw_output = clean(row.get("raw_output"))
        ok = bool(row.get("ok"))
        n_records = len(records)

        if ok and n_records > 0:
            status = "parsed_records"
        elif ok and n_records == 0:
            status = "ok_empty"
        elif not ok and raw_output:
            status = "failed_with_raw_output"
        else:
            status = "failed_no_raw_output"

        out.append(
            {
                "run_idx": run_idx,
                "timestamp": clean(row.get("timestamp")),
                "model": clean(row.get("model")),
                "target": target,
                "company": company,
                "prompt": clean(row.get("prompt")),
                "ok": ok,
                "status": status,
                "n_records": n_records,
                "error": error,
                "error_category": categorize_error(error, raw_output),
                "raw_output_signal": raw_json_signal(raw_output),
                "raw_output_len_chars": len(raw_output),
                "raw_output_preview": raw_output[:4000],
            }
        )
    return pd.DataFrame(out)


def flatten_t3_records(rows: list[dict[str, Any]]) -> pd.DataFrame:
    out = []
    for run_idx, row in enumerate(rows):
        records = row.get("records") if isinstance(row.get("records"), list) else []
        target = clean(row.get("target"))
        company = target.split("/")[0] if target else ""
        for record_idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                continue
            out.append(
                {
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": clean(row.get("timestamp")),
                    "model": clean(row.get("model")),
                    "target": target,
                    "company": company,
                    "prompt": clean(row.get("prompt")),
                    "text": clean(rec.get("text")),
                    "aspect": clean(rec.get("aspect")),
                    "esg": clean(rec.get("esg")).upper(),
                    "tone": clean(rec.get("tone")).lower(),
                    "sentiment": clean(rec.get("sentiment")).lower(),
                    "reasoning": clean(rec.get("reasoning")),
                }
            )
    return pd.DataFrame(out)


def values(df: pd.DataFrame, col: str) -> list[str]:
    if df.empty or col not in df.columns:
        return []
    return sorted(v for v in df[col].map(clean).unique() if v)


def sidebar_filter(df: pd.DataFrame, col: str, label: str) -> pd.DataFrame:
    opts = values(df, col)
    selected = st.sidebar.multiselect(label, opts, key=f"filter_{col}")
    if not selected:
        return df
    return df[df[col].map(clean).isin(selected)]


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


def heatmap(df: pd.DataFrame, x: str, y: str, color_col: str, title: str):
    if df.empty:
        st.info("No rows available for this heatmap.")
        return
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(f"{x}:N", title=x.replace("_", " ").title()),
            y=alt.Y(f"{y}:N", title=y.replace("_", " ").title()),
            color=alt.Color(f"{color_col}:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=360)
    )
    text = alt.Chart(df).mark_text().encode(
        x=f"{x}:N",
        y=f"{y}:N",
        text=f"{color_col}:Q",
        color=alt.condition(
            alt.datum[color_col] > df[color_col].max() * 0.55,
            alt.value("white"),
            alt.value("#17202a"),
        ),
    )
    st.altair_chart(chart + text, use_container_width=True)


st.title("LLM Error & Parse Audit")
st.caption("Count what was parsed, what was saved only as raw output, what failed, and what remains unresolved in `results/esg_records.json`.")

raw_rows = load_json(T3_PATH)
runs = flatten_t3_runs(raw_rows)
records = flatten_t3_records(raw_rows)

with st.sidebar:
    st.header("Data")
    st.caption(f"T3 source: `{T3_PATH}`")
    table_limit = st.number_input("Table preview row limit", min_value=50, value=500, step=50)
    if st.button("Refresh audit", use_container_width=True):
        st.rerun()

    st.header("Filters")
    filtered = runs.copy()
    for col, label in [
        ("model", "Model"),
        ("company", "Company"),
        ("target", "Target"),
        ("prompt", "Prompt"),
        ("status", "Run Status"),
        ("error_category", "Error Category"),
        ("raw_output_signal", "Raw Output Signal"),
    ]:
        filtered = sidebar_filter(filtered, col, label)

filtered_run_ids = set(filtered["run_idx"]) if not filtered.empty else set()
filtered_records = records[records["run_idx"].isin(filtered_run_ids)] if not records.empty else records

total_runs = len(filtered)
parsed_runs = int(filtered["status"].eq("parsed_records").sum()) if not filtered.empty else 0
ok_empty_runs = int(filtered["status"].eq("ok_empty").sum()) if not filtered.empty else 0
failed_runs = int(filtered["status"].isin(["failed_with_raw_output", "failed_no_raw_output"]).sum()) if not filtered.empty else 0
raw_failed_runs = int(filtered["status"].eq("failed_with_raw_output").sum()) if not filtered.empty else 0
parsed_records = len(filtered_records)
parse_rate = (parsed_runs / total_runs * 100) if total_runs else 0.0

cols = st.columns(6)
cols[0].metric("Total T3 runs", f"{total_runs:,}")
cols[1].metric("Parsed runs", f"{parsed_runs:,}", f"{parse_rate:.1f}%")
cols[2].metric("Parsed records", f"{parsed_records:,}")
cols[3].metric("OK but empty", f"{ok_empty_runs:,}")
cols[4].metric("Failed runs", f"{failed_runs:,}")
cols[5].metric("Failed with raw output", f"{raw_failed_runs:,}")

tabs = st.tabs(["Audit Overview", "Remaining Errors", "Raw Output Not Parsed", "Parsed Records", "Exports"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        bar(count_df(filtered, "status"), "status", title="T3 Run Status Counts")
    with c2:
        bar(count_df(filtered, "error_category"), "error_category", title="Error Category Counts")

    c3, c4 = st.columns(2)
    with c3:
        bar(count_df(filtered, "raw_output_signal"), "raw_output_signal", title="Raw Output Signal")
    with c4:
        by_prompt = filtered.groupby(["prompt", "status"], dropna=False).size().reset_index(name="count")
        bar(by_prompt, "prompt", color="status", title="Status by Prompt")

    model_status = filtered.groupby(["model", "status"], dropna=False).size().reset_index(name="count")
    heatmap(model_status, "status", "model", "count", "Model by Status Matrix")

with tabs[1]:
    st.markdown("Remaining errors are runs that did not produce parsed records and still need rerun, model change, prompt repair, or manual recovery.")
    remaining = filtered[filtered["status"].isin(["failed_with_raw_output", "failed_no_raw_output", "ok_empty"])].copy()
    st.dataframe(
        remaining[
            [
                "timestamp",
                "model",
                "target",
                "prompt",
                "status",
                "error_category",
                "raw_output_signal",
                "n_records",
                "raw_output_len_chars",
                "error",
            ]
        ].head(int(table_limit)),
        use_container_width=True,
        height=520,
    )

    c1, c2 = st.columns(2)
    with c1:
        by_model = remaining.groupby(["model", "error_category"], dropna=False).size().reset_index(name="count")
        bar(by_model, "model", color="error_category", title="Remaining Error Categories by Model")
    with c2:
        by_target = remaining.groupby(["target", "status"], dropna=False).size().reset_index(name="count").head(40)
        bar(by_target, "target", color="status", title="Remaining Outputs by Target")

with tabs[2]:
    st.markdown(
        "These runs have raw model output saved, but the parser could not turn it into records. "
        "They are the best candidates for prompt/schema repair or manual JSON cleanup."
    )
    raw_not_parsed = filtered[
        filtered["status"].eq("failed_with_raw_output")
        | ((filtered["status"].eq("ok_empty")) & filtered["raw_output_len_chars"].gt(2))
    ].copy()
    st.dataframe(
        raw_not_parsed[
            [
                "timestamp",
                "model",
                "target",
                "prompt",
                "error_category",
                "raw_output_signal",
                "raw_output_len_chars",
                "error",
                "raw_output_preview",
            ]
        ].head(int(table_limit)),
        use_container_width=True,
        height=560,
    )

    selected_idx = None
    if raw_not_parsed.empty:
        st.info("No failed runs with raw output are available under the current filters.")
    else:
        selected_idx = st.selectbox(
            "Inspect one raw-output run",
            raw_not_parsed["run_idx"].tolist(),
            format_func=lambda idx: (
                f"{idx} · "
                f"{raw_not_parsed.loc[raw_not_parsed['run_idx'] == idx, 'model'].iloc[0]} · "
                f"{raw_not_parsed.loc[raw_not_parsed['run_idx'] == idx, 'target'].iloc[0]} · "
                f"{raw_not_parsed.loc[raw_not_parsed['run_idx'] == idx, 'prompt'].iloc[0]}"
            ),
        )
    if selected_idx is not None:
        row = raw_not_parsed[raw_not_parsed["run_idx"] == selected_idx].iloc[0]
        st.markdown("**Error**")
        st.code(row["error"] or "(no explicit error)")
        st.markdown("**Raw output preview**")
        st.code(row["raw_output_preview"] or "(no raw output saved)", language="json")

with tabs[3]:
    st.markdown("Parsed records are runs that successfully produced structured ESG evidence rows.")
    c1, c2 = st.columns(2)
    with c1:
        bar(count_df(filtered_records, "tone"), "tone", title="Parsed Tone Counts")
    with c2:
        bar(count_df(filtered_records, "esg"), "esg", title="Parsed ESG Counts")
    st.dataframe(filtered_records.head(int(table_limit)), use_container_width=True, height=520)

with tabs[4]:
    remaining = filtered[filtered["status"].isin(["failed_with_raw_output", "failed_no_raw_output", "ok_empty"])].copy()
    raw_not_parsed = filtered[
        filtered["status"].eq("failed_with_raw_output")
        | ((filtered["status"].eq("ok_empty")) & filtered["raw_output_len_chars"].gt(2))
    ].copy()
    st.download_button("Download audit runs CSV", filtered.to_csv(index=False).encode("utf-8"), "llm_t3_audit_runs.csv", "text/csv")
    st.download_button("Download remaining errors CSV", remaining.to_csv(index=False).encode("utf-8"), "llm_t3_remaining_errors.csv", "text/csv")
    st.download_button("Download raw-not-parsed CSV", raw_not_parsed.to_csv(index=False).encode("utf-8"), "llm_t3_raw_not_parsed.csv", "text/csv")
    st.download_button("Download parsed records CSV", filtered_records.to_csv(index=False).encode("utf-8"), "llm_t3_parsed_records.csv", "text/csv")
