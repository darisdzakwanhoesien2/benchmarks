from __future__ import annotations

from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Phase PDF Distribution", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from dataset_phase_utils import add_pdf_metadata, phase_view  # noqa: E402


PHASES = ["Phase 1", "Phase 2", "Phase 3"]
PDF_GROUP_COLS = [
    "original_file",
    "company_name",
    "ticker",
    "ticker_company_name",
    "ticker_sector",
    "report_year",
]


def ticker_filter_options(df: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    options = ["All tickers"]
    mapping = {"All tickers": "__all__"}
    ticker_cols = ["ticker", "ticker_company_name", "ticker_sector"]
    if not set(ticker_cols).issubset(df.columns):
        return options, mapping

    unique_rows = (
        df[ticker_cols]
        .fillna("")
        .drop_duplicates()
        .sort_values(["ticker", "ticker_company_name", "ticker_sector"], ascending=[True, True, True])
    )
    has_missing = False
    for _, row in unique_rows.iterrows():
        ticker = str(row.get("ticker", "")).strip()
        company = str(row.get("ticker_company_name", "")).strip()
        sector = str(row.get("ticker_sector", "")).strip()
        if not ticker:
            has_missing = True
            continue
        label = " | ".join(part for part in [ticker, company, sector] if part)
        options.append(label)
        mapping[label] = ticker

    if has_missing:
        options.append("Unmapped ticker metadata")
        mapping["Unmapped ticker metadata"] = "__missing__"
    return options, mapping

def phase_pdf_counts(df: pd.DataFrame, phase: str, top_n: int = 25) -> pd.DataFrame:
    subset = df[df["phase"].eq(phase)].copy()
    if subset.empty:
        return pd.DataFrame(columns=[*PDF_GROUP_COLS, "records"])
    counts = (
        subset.groupby(PDF_GROUP_COLS, dropna=False)
        .size()
        .reset_index(name="records")
        .sort_values(["records", "original_file"], ascending=[False, True])
        .head(top_n)
        .reset_index(drop=True)
    )
    return counts


def phase3_intake_summary(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    phase3 = df[df["phase"].eq("Phase 3")].copy()
    if phase3.empty:
        metrics = pd.DataFrame(
            [
                {"metric": "Parsed LLM rows", "value": 0},
                {"metric": "Success event rows", "value": 0},
                {"metric": "Failed event rows", "value": 0},
                {"metric": "Unique background jobs", "value": 0},
            ]
        )
        return metrics, pd.DataFrame()

    parsed_rows = phase3["source_dataset"].eq("live_llm_reprocess").sum() if "source_dataset" in phase3.columns else 0
    success_rows = (
        (phase3["source_dataset"].eq("background_llm_event")) & (phase3["event"].eq("completed"))
    ).sum() if {"source_dataset", "event"}.issubset(phase3.columns) else 0
    failed_rows = (
        (phase3["source_dataset"].eq("background_llm_event")) & (phase3["event"].eq("failed"))
    ).sum() if {"source_dataset", "event"}.issubset(phase3.columns) else 0
    unique_jobs = phase3["background_job_id"].astype(str).str.strip().replace("", pd.NA).dropna().nunique() if "background_job_id" in phase3.columns else 0

    metrics = pd.DataFrame(
        [
            {"metric": "Parsed LLM rows", "value": int(parsed_rows)},
            {"metric": "Success event rows", "value": int(success_rows)},
            {"metric": "Failed event rows", "value": int(failed_rows)},
            {"metric": "Unique background jobs", "value": int(unique_jobs)},
        ]
    )

    detail_cols = [
        "original_file",
        "ticker",
        "ticker_company_name",
        "model",
        "prompt",
        "source_dataset",
        "event",
        "background_job_id",
    ]
    available_cols = [col for col in detail_cols if col in phase3.columns]
    details = (
        phase3.groupby(available_cols, dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["rows", "original_file"], ascending=[False, True])
        .reset_index(drop=True)
    ) if available_cols else pd.DataFrame()
    return metrics, details


def bar_chart(df: pd.DataFrame, color: str) -> alt.Chart:
    tooltip = ["original_file", "records"]
    if "company_name" in df.columns:
        tooltip.insert(1, "company_name")
    if "ticker" in df.columns:
        tooltip.insert(2, "ticker")
    if "ticker_company_name" in df.columns:
        tooltip.insert(3, "ticker_company_name")
    if "ticker_sector" in df.columns:
        tooltip.insert(4, "ticker_sector")
    if "report_year" in df.columns:
        tooltip.append("report_year")
    return (
        alt.Chart(df)
        .mark_bar(color=color)
        .encode(
            x=alt.X("records:Q", title="records"),
            y=alt.Y("original_file:N", sort="-x", title=None),
            tooltip=tooltip,
        )
        .properties(height=420)
    )


st.title("Phase PDF Distribution")
st.caption("Compare original PDF/file distribution across the completed pool, editing pool, and new intake pool.")

view = phase_view()
view = add_pdf_metadata(view, "target")

with st.sidebar:
    st.header("Filters")
    include_missing = st.checkbox("Include <missing> target rows", value=False)
    top_n = st.number_input("Top files per phase", min_value=5, max_value=100, value=25, step=5)
    ticker_options, ticker_map = ticker_filter_options(view)
    selected_ticker_label = st.selectbox("Ticker metadata", ticker_options, index=0)

filtered = view.copy()
if not include_missing:
    filtered = filtered[filtered["original_file"].ne("<missing>")].copy()
selected_ticker = ticker_map.get(selected_ticker_label, "__all__")
if selected_ticker == "__missing__":
    filtered = filtered[filtered["ticker"].fillna("").astype(str).str.strip().eq("")].copy()
elif selected_ticker != "__all__":
    filtered = filtered[filtered["ticker"].eq(selected_ticker)].copy()

if selected_ticker_label != "All tickers":
    st.caption(f"Ticker filter: {selected_ticker_label}")

c1, c2, c3 = st.columns(3)
c1.metric("Phase 1 rows", f"{int(filtered['phase'].eq('Phase 1').sum()):,}")
c2.metric("Phase 2 rows", f"{int(filtered['phase'].eq('Phase 2').sum()):,}")
c3.metric("Phase 3 rows", f"{int(filtered['phase'].eq('Phase 3').sum()):,}")

st.subheader("Phase 3 Intake Summary")
phase3_metrics, phase3_details = phase3_intake_summary(filtered)
m1, m2, m3, m4 = st.columns(4)
metric_values = {row["metric"]: int(row["value"]) for _, row in phase3_metrics.iterrows()}
m1.metric("Parsed LLM rows", f"{metric_values.get('Parsed LLM rows', 0):,}")
m2.metric("Success event rows", f"{metric_values.get('Success event rows', 0):,}")
m3.metric("Failed event rows", f"{metric_values.get('Failed event rows', 0):,}")
m4.metric("Unique background jobs", f"{metric_values.get('Unique background jobs', 0):,}")
if phase3_details.empty:
    st.info("No Phase 3 intake rows for the current filter.")
else:
    st.dataframe(phase3_details.head(int(top_n) * 4), use_container_width=True, hide_index=True, height=260)

st.subheader("Cross-Phase PDF Comparison")
pivot = (
    filtered.groupby([*PDF_GROUP_COLS, "phase"], dropna=False)
    .size()
    .reset_index(name="records")
    .pivot(index=PDF_GROUP_COLS, columns="phase", values="records")
    .fillna(0)
    .reset_index()
)
for phase in PHASES:
    if phase not in pivot.columns:
        pivot[phase] = 0
pivot["total_records"] = pivot[PHASES].sum(axis=1)
pivot = pivot.sort_values(["total_records", "original_file"], ascending=[False, True]).reset_index(drop=True)
st.dataframe(pivot, use_container_width=True, hide_index=True, height=420)

stacked_source = (
    pivot.melt(
        id_vars=[*PDF_GROUP_COLS, "total_records"],
        value_vars=PHASES,
        var_name="phase",
        value_name="records",
    )
    .sort_values(["total_records", "phase"], ascending=[False, True])
)
stacked_chart = (
    alt.Chart(stacked_source.head(int(top_n) * 3))
    .mark_bar()
    .encode(
        x=alt.X("records:Q", title="records"),
        y=alt.Y("original_file:N", sort="-x", title=None),
        color=alt.Color("phase:N", sort=PHASES),
        tooltip=[*PDF_GROUP_COLS, "phase", "records"],
    )
    .properties(height=520)
)
st.altair_chart(stacked_chart, use_container_width=True)

st.subheader("Per-Phase PDF Distribution")
t1, t2, t3 = st.tabs(PHASES)

phase_colors = {
    "Phase 1": "#2f6f73",
    "Phase 2": "#c97b2a",
    "Phase 3": "#7a52c7",
}

for tab, phase in zip([t1, t2, t3], PHASES):
    with tab:
        counts = phase_pdf_counts(filtered, phase, top_n=int(top_n))
        st.caption(f"{phase} original PDF/file distribution")
        st.dataframe(counts, use_container_width=True, hide_index=True, height=420)
        if counts.empty:
            st.info(f"No rows in {phase} for the current filter.")
        else:
            st.altair_chart(bar_chart(counts, phase_colors[phase]), use_container_width=True)
