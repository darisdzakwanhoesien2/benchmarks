from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Iterable

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Ground Truth Output Visualizer", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
ARTIFACTS = ROOT / "results" / "revision_analysis"
ANNOTATION_PATH = ARTIFACTS / "pilot_ground_truth_annotations.csv"
SEED_PATH = ARTIFACTS / "pilot_ground_truth_seed.csv"
SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"
RAW_GROUND_TRUTH_PATH = ROOT / "results" / "ground_truth.json"
RAW_ABSA_GROUND_TRUTH_PATH = ROOT / "results" / "absa_results_ground_truth.json"

TONE_ORDER = ["commitment", "action", "outcome", "none", "missing"]
REQUIRED_COLUMNS = [
    "record_id",
    "company",
    "target",
    "model",
    "prompt",
    "language",
    "aspect",
    "esg",
    "tone_pred",
    "silver_tone_ground_truth",
    "ground_truth_tone",
    "ground_truth_esg",
    "ground_truth_aspect",
    "review_status",
    "needs_human_review",
    "schema_drift",
    "text",
    "reasoning",
    "review_notes",
]

from graph_attachment_gallery import render_attachment_cards  # noqa: E402


def clean_label(value: object) -> str:
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in {"nan", "none", "null"}:
        return ""
    return value


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


def load_default_ground_truth() -> tuple[pd.DataFrame, Path | None, str]:
    candidates = [
        (ANNOTATION_PATH, "saved human annotation output"),
        (SEED_PATH, "pilot ground-truth seed"),
        (SILVER_PATH, "full silver-tone scaffold"),
    ]
    for path, label in candidates:
        df = load_csv(path)
        if not df.empty:
            return normalize_ground_truth(df), path, label
    return pd.DataFrame(), None, ""


def normalize_ground_truth(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    for col in [
        "company",
        "target",
        "model",
        "prompt",
        "language",
        "aspect",
        "esg",
        "tone_pred",
        "silver_tone_ground_truth",
        "ground_truth_tone",
        "ground_truth_esg",
        "ground_truth_aspect",
        "review_status",
        "text",
    ]:
        df[col] = df[col].map(clean_label)
    for col in ["needs_human_review", "schema_drift"]:
        df[col] = df[col].astype(str).str.lower().isin({"true", "1", "yes", "y"})
    if "text_len_words" not in df.columns:
        df["text_len_words"] = df["text"].str.split().map(len)
    df["is_annotated_tone"] = df["ground_truth_tone"].str.strip().ne("")
    df["comparison_tone"] = df["ground_truth_tone"].where(
        df["is_annotated_tone"], df["silver_tone_ground_truth"]
    )
    df["comparison_source"] = df["is_annotated_tone"].map(
        {True: "human annotation", False: "silver proxy"}
    )
    df["tone_matches_comparison"] = (
        df["tone_pred"].str.lower().str.strip()
        == df["comparison_tone"].str.lower().str.strip()
    ) & df["comparison_tone"].str.strip().ne("")
    return df


def sorted_values(series: pd.Series) -> list[str]:
    values = sorted(v for v in series.map(clean_label).unique() if v)
    return values


def apply_filter(df: pd.DataFrame, col: str, label: str) -> pd.DataFrame:
    values = sorted_values(df[col]) if col in df.columns else []
    selected = st.sidebar.multiselect(label, values)
    if not selected:
        return df
    return df[df[col].map(clean_label).isin(selected)]


def bar_chart(df: pd.DataFrame, x: str, y: str = "count", color: str | None = None, title: str = ""):
    if df.empty:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{x}:N", sort="-y", title=x.replace("_", " ").title()),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ").title()),
            color=alt.Color(f"{color}:N", legend=alt.Legend(title=color.replace("_", " ").title())) if color else alt.value("#217c7e"),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=330)
    )
    st.altair_chart(chart, use_container_width=True)


def distribution(df: pd.DataFrame, col: str, name: str | None = None) -> pd.DataFrame:
    if col not in df.columns:
        return pd.DataFrame(columns=[name or col, "count", "pct"])
    label = name or col
    out = (
        df[col]
        .map(clean_label)
        .replace("", "missing")
        .value_counts(dropna=False)
        .rename_axis(label)
        .reset_index(name="count")
    )
    total = out["count"].sum()
    out["pct"] = (out["count"] / total * 100).round(2) if total else 0.0
    return out


def coverage_table(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if group_col not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.assign(annotation_status=df["is_annotated_tone"].map({True: "annotated", False: "not annotated"}))
        .groupby([group_col, "annotation_status"], dropna=False)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["annotated", "not annotated"]:
        if col not in grouped.columns:
            grouped[col] = 0
    grouped["total"] = grouped["annotated"] + grouped["not annotated"]
    grouped["coverage_pct"] = (grouped["annotated"] / grouped["total"] * 100).round(2)
    return grouped.sort_values(["coverage_pct", "total"], ascending=[True, False])


def cohen_kappa(y_true: Iterable[str], y_pred: Iterable[str]) -> float | None:
    pairs = [(clean_label(a).lower(), clean_label(b).lower()) for a, b in zip(y_true, y_pred)]
    pairs = [(a, b) for a, b in pairs if a and b]
    if not pairs:
        return None
    labels = sorted(set(a for a, _ in pairs) | set(b for _, b in pairs))
    n = len(pairs)
    observed = sum(1 for a, b in pairs if a == b) / n
    expected = 0.0
    for label in labels:
        expected += (
            sum(1 for a, _ in pairs if a == label) / n
            * sum(1 for _, b in pairs if b == label) / n
        )
    return (observed - expected) / (1 - expected) if (1 - expected) else 0.0


def agreement_summary(df: pd.DataFrame, truth_col: str, pred_col: str, label: str) -> pd.DataFrame:
    valid = df[df[truth_col].map(clean_label).ne("") & df[pred_col].map(clean_label).ne("")].copy()
    if valid.empty:
        return pd.DataFrame(), valid
    y_true = valid[truth_col].map(clean_label).str.lower()
    y_pred = valid[pred_col].map(clean_label).str.lower()
    matches = y_true == y_pred
    summary = pd.DataFrame(
        [{
            "target": label,
            "n": len(valid),
            "agreement_pct": round(matches.mean() * 100, 2),
            "cohen_kappa": round(cohen_kappa(y_true, y_pred) or 0.0, 4),
            "disagreements": int((~matches).sum()),
        }]
    )
    valid["_truth"] = y_true
    valid["_prediction"] = y_pred
    valid["_matches"] = matches
    return summary, valid


def confusion_heatmap(valid: pd.DataFrame, truth_col: str, pred_col: str, title: str):
    if valid.empty:
        st.info("No paired labels are available for this confusion matrix.")
        return
    cm = (
        valid.assign(
            actual=valid[truth_col].map(clean_label).str.lower(),
            predicted=valid[pred_col].map(clean_label).str.lower(),
        )
        .groupby(["actual", "predicted"])
        .size()
        .reset_index(name="count")
    )
    chart = (
        alt.Chart(cm)
        .mark_rect()
        .encode(
            x=alt.X("predicted:N", title="Predicted"),
            y=alt.Y("actual:N", title="Ground truth or proxy"),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=["actual", "predicted", "count"],
        )
        .properties(title=title, height=360)
    )
    text = (
        alt.Chart(cm)
        .mark_text()
        .encode(
            x="predicted:N",
            y="actual:N",
            text="count:Q",
            color=alt.condition(
                alt.datum.count > cm["count"].max() * 0.55,
                alt.value("white"),
                alt.value("#17202a"),
            ),
        )
    )
    st.altair_chart(chart + text, use_container_width=True)


def read_json_records(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return pd.DataFrame()
    if isinstance(data, list):
        return pd.json_normalize(data)
    if isinstance(data, dict):
        return pd.json_normalize(data)
    return pd.DataFrame({"value": [str(data)]})


st.title("Ground Truth Output Visualizer")
st.caption(
    "Inspect the pilot ground-truth output, annotation coverage, silver-label comparisons, and records that still need human review."
)

default_df, default_path, default_label = load_default_ground_truth()

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Optional ground-truth CSV", type=["csv"])
    table_limit = st.number_input("Table preview row limit", min_value=50, value=500, step=50)
    use_silver_comparison = st.checkbox(
        "Use silver tone where human tone is blank",
        value=True,
        help="This lets the visualizer show proxy agreement before manual annotation is complete.",
    )
    if st.button("Refresh ground-truth outputs", use_container_width=True):
        st.rerun()

if uploaded is not None:
    df = normalize_ground_truth(pd.read_csv(uploaded).fillna(""))
    source_caption = "uploaded CSV"
else:
    df = default_df
    source_caption = f"{default_label}: `{default_path}`" if default_path else "no default file found"

if df.empty:
    st.error("No ground-truth output was found. Expected a seed, annotation, or silver CSV in `results/revision_analysis`.")
    st.stop()

if not use_silver_comparison:
    df["comparison_tone"] = df["ground_truth_tone"]
    df["comparison_source"] = "human annotation only"
    df["tone_matches_comparison"] = (
        df["tone_pred"].str.lower().str.strip()
        == df["comparison_tone"].str.lower().str.strip()
    ) & df["comparison_tone"].str.strip().ne("")

st.caption(f"Loaded from {source_caption}")

filtered = df.copy()
with st.sidebar:
    st.header("Filters")
    for col, label in [
        ("company", "Company"),
        ("target", "Source Target"),
        ("model", "LLM Model"),
        ("prompt", "Prompt"),
        ("language", "Language"),
        ("esg", "ESG Pillar"),
        ("tone_pred", "Predicted Tone"),
        ("silver_tone_ground_truth", "Silver Tone"),
        ("ground_truth_tone", "Human Tone"),
        ("review_status", "Review Status"),
    ]:
        filtered = apply_filter(filtered, col, label)
    review_only = st.checkbox("Show only review-needed rows", value=False)
    drift_only = st.checkbox("Show only schema-drift rows", value=False)
    if review_only:
        filtered = filtered[filtered["needs_human_review"]]
    if drift_only:
        filtered = filtered[filtered["schema_drift"]]

annotated_count = int(filtered["is_annotated_tone"].sum())
comparison_count = int(filtered["comparison_tone"].map(clean_label).ne("").sum())
agreement_count = int(filtered["tone_matches_comparison"].sum())

top_cols = st.columns(5)
top_cols[0].metric("Rows", f"{len(filtered):,}")
top_cols[1].metric("Human tone labels", f"{annotated_count:,}")
top_cols[2].metric("Comparable tone rows", f"{comparison_count:,}")
top_cols[3].metric("Tone agreement", f"{(agreement_count / comparison_count * 100):.1f}%" if comparison_count else "0.0%")
top_cols[4].metric("Needs review", f"{int(filtered['needs_human_review'].sum()):,}")

tabs = st.tabs([
    "Summary",
    "Coverage",
    "Agreement",
    "Review Queue",
    "Records",
    "Raw Outputs",
    "Attachment Cards",
])

with tabs[0]:
    st.markdown(
        "This tab shows what the ground-truth output contains before and after annotation. "
        "Predicted tone is the LLM/ABSA tone, silver tone is the automatic scaffold, and human tone is the final evaluation label when filled."
    )
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(distribution(filtered, "tone_pred", "tone"), "tone", title="Predicted Tone Distribution")
    with c2:
        comparison_dist = distribution(filtered, "comparison_tone", "tone")
        bar_chart(comparison_dist, "tone", title="Human or Silver Tone Distribution")

    c3, c4 = st.columns(2)
    with c3:
        bar_chart(distribution(filtered, "language", "language"), "language", title="Language Distribution")
    with c4:
        bar_chart(distribution(filtered, "esg", "esg"), "esg", title="ESG Pillar Distribution")

    source_dist = distribution(filtered, "comparison_source", "comparison_source")
    st.dataframe(source_dist, use_container_width=True)

with tabs[1]:
    st.markdown(
        "Coverage answers whether the pilot sample has enough human labels across companies, prompts, models, and predicted tones. "
        "Low coverage groups are priority candidates for annotation before reporting final accuracy or kappa."
    )
    group_col = st.selectbox(
        "Coverage grouping",
        ["company", "prompt", "model", "tone_pred", "language", "esg", "target"],
        index=0,
    )
    cov = coverage_table(filtered, group_col)
    st.dataframe(cov, use_container_width=True, height=360)
    if not cov.empty:
        chart_data = cov.melt(
            id_vars=[group_col, "total", "coverage_pct"],
            value_vars=["annotated", "not annotated"],
            var_name="status",
            value_name="rows",
        )
        chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                x=alt.X(f"{group_col}:N", sort="-y", title=group_col.replace("_", " ").title()),
                y=alt.Y("rows:Q", stack="zero"),
                color=alt.Color("status:N", scale=alt.Scale(range=["#217c7e", "#d9a441"])),
                tooltip=[group_col, "status", "rows", "coverage_pct", "total"],
            )
            .properties(height=360)
        )
        st.altair_chart(chart, use_container_width=True)

    not_annotated = filtered[~filtered["is_annotated_tone"]]
    st.download_button(
        "Download not-annotated rows",
        not_annotated.to_csv(index=False).encode("utf-8"),
        "ground_truth_not_annotated_rows.csv",
        "text/csv",
    )

with tabs[2]:
    st.markdown(
        "Agreement compares `tone_pred` with human tone when available. "
        "If human tone is still blank and the sidebar option is enabled, the page uses `silver_tone_ground_truth` as a proxy preview."
    )
    summary, valid = agreement_summary(filtered, "comparison_tone", "tone_pred", "tone")
    st.dataframe(summary, use_container_width=True)
    confusion_heatmap(valid, "comparison_tone", "tone_pred", "Tone Confusion Matrix")

    disagreements = valid[~valid["_matches"]].drop(columns=["_truth", "_prediction", "_matches"], errors="ignore")
    st.markdown("**Tone disagreements**")
    st.dataframe(
        disagreements[
            [
                col
                for col in [
                    "record_id",
                    "company",
                    "prompt",
                    "language",
                    "aspect",
                    "tone_pred",
                    "comparison_tone",
                    "comparison_source",
                    "text",
                    "reasoning",
                ]
                if col in disagreements.columns
            ]
        ].head(int(table_limit)),
        use_container_width=True,
        height=420,
    )
    st.download_button(
        "Download tone disagreements",
        disagreements.to_csv(index=False).encode("utf-8"),
        "ground_truth_tone_disagreements.csv",
        "text/csv",
    )

with tabs[3]:
    st.markdown(
        "The review queue isolates rows that are risky for evaluation: missing human labels, schema drift, proxy disagreement, or automatic review flags. "
        "These rows should be resolved before using the metrics as final thesis evidence."
    )
    review_df = filtered[
        filtered["needs_human_review"]
        | filtered["schema_drift"]
        | ~filtered["is_annotated_tone"]
        | (
            filtered["comparison_tone"].map(clean_label).ne("")
            & ~filtered["tone_matches_comparison"]
        )
    ].copy()
    review_df["review_reason"] = ""
    review_df.loc[~review_df["is_annotated_tone"], "review_reason"] += "missing_human_tone;"
    review_df.loc[review_df["needs_human_review"], "review_reason"] += "needs_human_review;"
    review_df.loc[review_df["schema_drift"], "review_reason"] += "schema_drift;"
    review_df.loc[
        review_df["comparison_tone"].map(clean_label).ne("") & ~review_df["tone_matches_comparison"],
        "review_reason",
    ] += "tone_disagreement;"

    reason_counts = (
        review_df["review_reason"]
        .str.split(";")
        .explode()
        .map(clean_label)
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .rename_axis("review_reason")
        .reset_index(name="count")
    )
    bar_chart(reason_counts, "review_reason", title="Review Reason Counts")
    st.dataframe(review_df.head(int(table_limit)), use_container_width=True, height=480)
    st.download_button(
        "Download review queue",
        review_df.to_csv(index=False).encode("utf-8"),
        "ground_truth_review_queue.csv",
        "text/csv",
    )

with tabs[4]:
    st.markdown(
        "Use this table to inspect individual evidence records. "
        "The text, reasoning, predicted tone, silver tone, and human tone columns are the core audit trail for research reporting."
    )
    display_cols = [
        col
        for col in [
            "record_id",
            "company",
            "target",
            "model",
            "prompt",
            "language",
            "aspect",
            "esg",
            "tone_pred",
            "silver_tone_ground_truth",
            "ground_truth_tone",
            "ground_truth_esg",
            "ground_truth_aspect",
            "review_status",
            "needs_human_review",
            "schema_drift",
            "text",
            "reasoning",
            "review_notes",
        ]
        if col in filtered.columns
    ]
    st.dataframe(filtered[display_cols].head(int(table_limit)), use_container_width=True, height=560)
    st.download_button(
        "Download filtered ground-truth records",
        filtered.to_csv(index=False).encode("utf-8"),
        "filtered_ground_truth_records.csv",
        "text/csv",
    )

with tabs[5]:
    st.markdown(
        "These are the earlier raw ground-truth result files. They are useful for auditability, but the CSV seed/annotation files are the preferred evaluation format."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ground_truth.json")
        raw_gt = read_json_records(RAW_GROUND_TRUTH_PATH)
        st.caption(f"`{RAW_GROUND_TRUTH_PATH}`")
        st.metric("Rows", f"{len(raw_gt):,}")
        st.dataframe(raw_gt.head(int(table_limit)), use_container_width=True, height=420)
    with c2:
        st.subheader("absa_results_ground_truth.json")
        raw_absa = read_json_records(RAW_ABSA_GROUND_TRUTH_PATH)
        st.caption(f"`{RAW_ABSA_GROUND_TRUTH_PATH}`")
        st.metric("Rows", f"{len(raw_absa):,}")
        st.dataframe(raw_absa.head(int(table_limit)), use_container_width=True, height=420)

with tabs[6]:
    render_attachment_cards(
        "Ground Truth Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        rq_default="RQ2",
        figures=["A.13", "A.17", "A.18", "A.19", "A.20"],
    )
