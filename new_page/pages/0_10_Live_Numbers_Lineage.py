from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Live Numbers + Lineage", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REV = RESULTS / "revision_analysis"
VIS = RESULTS / "visualizations"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def nonempty_count(df: pd.DataFrame, col: str) -> int:
    if df.empty or col not in df.columns:
        return 0
    return int(df[col].astype(str).str.strip().ne("").sum())


def tone_denominator_summary(annotation_df: pd.DataFrame) -> dict[str, Any]:
    total = int(len(annotation_df))
    completed = nonempty_count(annotation_df, "ground_truth_tone")
    missing = max(total - completed, 0)
    return {
        "total": total,
        "completed": completed,
        "missing": missing,
        "missing_rate": (missing / total) if total else 0.0,
        "source_file": str((REV / "pilot_ground_truth_annotations.csv").relative_to(ROOT)),
        "source_column": "ground_truth_tone",
    }


def sentence_tone_denominator(summary: dict[str, Any]) -> str:
    return (
        "Tone agreement and tone-distribution statistics were computed on the "
        f"{summary['completed']:,} records with a valid tone label, excluding the "
        f"{summary['missing']:,} records ({summary['missing_rate']:.1%}) where the pipeline returned no tone value."
    )


def st_page_redirect_button(label: str, page_filename: str, key: str) -> None:
    """
    Best-effort page redirect across Streamlit versions.
    Falls back to showing the target page filename when switch_page is unavailable.
    """
    if st.button(label, use_container_width=True, key=key):
        try:
            st.switch_page(page_filename)
        except Exception:
            st.session_state["__codex_live_numbers_target_page__"] = page_filename
            st.info(f"Open this page from the sidebar: `{page_filename}`")


@dataclass(frozen=True)
class LiveMetric:
    metric_id: str
    label: str
    compute: Callable[[], dict[str, Any]]
    pages: list[str]
    narrative: Callable[[dict[str, Any]], str] | None = None


def metric_table(metrics: list[LiveMetric]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for metric in metrics:
        payload = metric.compute()
        rows.append(
            {
                "metric_id": metric.metric_id,
                "label": metric.label,
                "value": payload.get("value", ""),
                "details": payload.get("details", ""),
                "source_file": payload.get("source_file", ""),
                "source_column": payload.get("source_column", ""),
                "used_in_pages": ", ".join(metric.pages),
            }
        )
    return pd.DataFrame(rows)


st.title("Live Numbers + Lineage")
st.caption(
    "This page computes the key thesis/dashboard numbers live from the current artifacts and shows where each number comes from "
    "(file + column/formula) and where it is displayed."
)

annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
silver = load_csv(REV / "silver_tone_ground_truth.csv")
tone_records = load_csv(VIS / "tone_records_flat.csv")
tone_audit = load_csv(REV / "chapter4_tone_denominator_audit.csv")

tone_denoms = tone_denominator_summary(annotation)

top = st.columns(4)
top[0].metric("Extraction denominator (rows)", f"{tone_denoms['total']:,}")
top[1].metric("Valid tone labels", f"{tone_denoms['completed']:,}")
top[2].metric("Missing tone outputs", f"{tone_denoms['missing']:,}", f"{tone_denoms['missing_rate']:.1%}", delta_color="inverse")
top[3].metric("Tone records (compact)", f"{len(tone_records):,}")

st.markdown("### Tone denominator narrative sentence")
st.code(sentence_tone_denominator(tone_denoms), language="text")
st.caption(f"Source: `{tone_denoms['source_file']}` column `{tone_denoms['source_column']}` (non-empty count).")

st.markdown("### Quick links (where it appears)")
link_cols = st.columns(3)
with link_cols[0]:
    st_page_redirect_button("Open Systematic Workflow Dashboard", "pages/5_Thesis_Systematic_Workflow_dashboard.py", key="goto_workflow_dashboard")
with link_cols[1]:
    st_page_redirect_button("Open Thesis Action Plan", "pages/3_0_Thesis_Action_Plan.py", key="goto_action_plan")
with link_cols[2]:
    st_page_redirect_button("Open Ch4-6 Benchmarks Page", "pages/6_4_ch4-6.py", key="goto_ch46")

st.divider()

st.subheader("Live numbers register (computed now)")

def compute_tone_denominators_payload() -> dict[str, Any]:
    return {
        "value": f"{tone_denoms['completed']:,} usable / {tone_denoms['total']:,} extracted",
        "details": f"missing={tone_denoms['missing']:,} ({tone_denoms['missing_rate']:.1%})",
        "source_file": tone_denoms["source_file"],
        "source_column": tone_denoms["source_column"],
    }


def compute_silver_rows_payload() -> dict[str, Any]:
    return {
        "value": f"{len(silver):,}",
        "details": "Rows in silver scaffold table (tone_pred, esg, aspect, etc).",
        "source_file": str((REV / "silver_tone_ground_truth.csv").relative_to(ROOT)),
        "source_column": "(row count)",
    }


def compute_annotation_rows_payload() -> dict[str, Any]:
    return {
        "value": f"{len(annotation):,}",
        "details": "Rows in annotation table (includes ground_truth_tone/esg/aspect, annotator, notes).",
        "source_file": str((REV / "pilot_ground_truth_annotations.csv").relative_to(ROOT)),
        "source_column": "(row count)",
    }


def compute_compact_tone_records_payload() -> dict[str, Any]:
    return {
        "value": f"{len(tone_records):,}",
        "details": "Compact tone records used by several dashboards (not the full-corpus denominator).",
        "source_file": str((VIS / "tone_records_flat.csv").relative_to(ROOT)),
        "source_column": "(row count)",
    }


METRICS: list[LiveMetric] = [
    LiveMetric(
        metric_id="tone_denominator",
        label="Tone denominator (usable vs extracted)",
        compute=compute_tone_denominators_payload,
        pages=["pages/5_Thesis_Systematic_Workflow_dashboard.py", "pages/3_0_Thesis_Action_Plan.py", "pages/6_4_ch4-6.py"],
        narrative=lambda _: sentence_tone_denominator(tone_denoms),
    ),
    LiveMetric(
        metric_id="silver_rows",
        label="Silver scaffold rows",
        compute=compute_silver_rows_payload,
        pages=["pages/1_8_Ground_Truth_Output_Visualizer.py", "pages/5_Thesis_Systematic_Workflow_dashboard.py"],
    ),
    LiveMetric(
        metric_id="annotation_rows",
        label="Annotation rows",
        compute=compute_annotation_rows_payload,
        pages=["pages/1_1_Ground_Truth_Workbench.py", "pages/5_Thesis_Systematic_Workflow_dashboard.py"],
    ),
    LiveMetric(
        metric_id="tone_records_compact",
        label="Tone records (compact snapshot)",
        compute=compute_compact_tone_records_payload,
        pages=["pages/5_Thesis_Systematic_Workflow_dashboard.py", "pages/6_1_Chapter_4_Implementation_Results.py"],
    ),
]

df = metric_table(METRICS)
st.dataframe(df, use_container_width=True, hide_index=True, height=280)

with st.expander("Show computed narrative snippets", expanded=False):
    for metric in METRICS:
        payload = metric.compute()
        if metric.narrative is None:
            continue
        st.markdown(f"**{metric.label}** (`{metric.metric_id}`)")
        st.code(metric.narrative(payload), language="text")

st.divider()
st.subheader("Raw sources (for traceability)")

src_tabs = st.tabs(
    [
        "pilot_ground_truth_annotations.csv",
        "chapter4_tone_denominator_audit.csv",
        "silver_tone_ground_truth.csv",
        "tone_records_flat.csv",
    ]
)
with src_tabs[0]:
    st.caption(f"`{(REV / 'pilot_ground_truth_annotations.csv').relative_to(ROOT)}`")
    st.dataframe(annotation.head(200), use_container_width=True, height=420)
with src_tabs[1]:
    st.caption(f"`{(REV / 'chapter4_tone_denominator_audit.csv').relative_to(ROOT)}`")
    st.dataframe(tone_audit, use_container_width=True, height=320)
with src_tabs[2]:
    st.caption(f"`{(REV / 'silver_tone_ground_truth.csv').relative_to(ROOT)}`")
    st.dataframe(silver.head(200), use_container_width=True, height=420)
with src_tabs[3]:
    st.caption(f"`{(VIS / 'tone_records_flat.csv').relative_to(ROOT)}`")
    st.dataframe(tone_records.head(200), use_container_width=True, height=420)

