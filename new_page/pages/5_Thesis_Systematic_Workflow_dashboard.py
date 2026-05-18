from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Thesis Systematic Workflow Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
VIS = RESULTS / "visualizations"
REVISION = RESULTS / "revision_analysis"
WORKFLOW_PATH = ROOT / "documentation" / "thesis_systematic_workflow.md"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_json(path: str) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return None
    try:
        return json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_jsonl(path: str, limit: int | None = None) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if limit is not None and len(rows) >= limit:
            break
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def workflow_rq_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rq": "RQ1",
                "stage": "PDF-to-structured ESG",
                "implemented_modules": 4,
                "artifact_groups": 5,
                "status": "active",
            },
            {
                "rq": "RQ2",
                "stage": "Aspect/pillar/sentiment/tone schema",
                "implemented_modules": 3,
                "artifact_groups": 4,
                "status": "active",
            },
            {
                "rq": "RQ3",
                "stage": "Tone vs ClimateBERT",
                "implemented_modules": 3,
                "artifact_groups": 3,
                "status": "active",
            },
            {
                "rq": "RQ4",
                "stage": "Diagnostics",
                "implemented_modules": 3,
                "artifact_groups": 4,
                "status": "active",
            },
            {
                "rq": "RQ5",
                "stage": "Reproducibility",
                "implemented_modules": 3,
                "artifact_groups": 4,
                "status": "active",
            },
            {
                "rq": "RQ6",
                "stage": "Stability",
                "implemented_modules": 3,
                "artifact_groups": 3,
                "status": "active",
            },
        ]
    )


def artifact_inventory() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in RESULTS.rglob("*"):
        if not path.is_file() or path.name == ".DS_Store":
            continue
        rel = path.relative_to(ROOT)
        if "background_llm_jobs" in rel.parts:
            group = "LLM background jobs"
        elif "ground_truth_background_jobs" in rel.parts:
            group = "Ground-truth background jobs"
        elif "revision_analysis" in rel.parts:
            group = "Revision analysis"
        elif "visualizations" in rel.parts:
            group = "Visualizations"
        elif "api_reader" in rel.parts:
            group = "API snapshots"
        else:
            group = "Core results"
        rows.append(
            {
                "path": str(rel),
                "group": group,
                "extension": path.suffix.lower().lstrip(".") or "none",
                "size_kb": round(path.stat().st_size / 1024, 2),
                "modified": pd.to_datetime(path.stat().st_mtime, unit="s"),
            }
        )
    return pd.DataFrame(rows)


def job_status_frame(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return pd.DataFrame()
    for job_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        status = load_json(str(job_dir / "status.json"))
        config = load_json(str(job_dir / "config.json"))
        if not isinstance(status, dict):
            status = {}
        if not isinstance(config, dict):
            config = {}
        total = int(status.get("total") or 0)
        completed = int(status.get("completed") or 0)
        rows.append(
            {
                "job_id": job_dir.name,
                "status": clean(status.get("status") or "unknown"),
                "completed": completed,
                "total": total,
                "failed": int(status.get("failed") or 0),
                "skipped": int(status.get("skipped") or 0),
                "progress_pct": round(completed / total * 100, 1) if total else 0.0,
                "document": clean(status.get("document") or config.get("document")),
                "updated_at": clean(status.get("updated_at")),
            }
        )
    return pd.DataFrame(rows)


def t2_flat_frame() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in load_jsonl(str(RESULTS / "t2_results.jsonl")):
        hybrid = record.get("hybrid") if isinstance(record.get("hybrid"), dict) else {}
        rule = record.get("rule_based") if isinstance(record.get("rule_based"), dict) else {}
        predictions = hybrid.get("predictions") if isinstance(hybrid.get("predictions"), list) else []
        metrics = hybrid.get("metrics") if isinstance(hybrid.get("metrics"), list) else []
        metric_map = {
            clean(item.get("Metric")): item.get("Value")
            for item in metrics
            if isinstance(item, dict)
        }
        if not predictions:
            rows.append(
                {
                    "label": clean(record.get("label")),
                    "rule_tone": clean(rule.get("tone")),
                    "hybrid_error": clean(hybrid.get("error")),
                    "tone_pred": "",
                    "sentiment_pred": "",
                    "ontology_alignment": None,
                    "greenwashing_index": pd.to_numeric(metric_map.get("Greenwashing Index"), errors="coerce"),
                }
            )
            continue
        for pred in predictions:
            if not isinstance(pred, dict):
                continue
            rows.append(
                {
                    "label": clean(record.get("label")),
                    "rule_tone": clean(rule.get("tone")),
                    "hybrid_error": clean(hybrid.get("error")),
                    "tone_pred": clean(pred.get("Tone_Pred")),
                    "sentiment_pred": clean(pred.get("Sentiment_Pred")),
                    "ontology_alignment": pd.to_numeric(pred.get("Ontology_Alignment"), errors="coerce"),
                    "greenwashing_index": pd.to_numeric(metric_map.get("Greenwashing Index"), errors="coerce"),
                    "ontology_path": clean(pred.get("Ontology_Path")),
                }
            )
    return pd.DataFrame(rows)


def count_df(df: pd.DataFrame, col: str, top_n: int | None = None) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[col, "count"])
    out = df[col].map(clean).replace("", "missing").value_counts().rename_axis(col).reset_index(name="count")
    return out.head(top_n) if top_n else out


def bar_chart(df: pd.DataFrame, x: str, y: str = "count", color: str | None = None, title: str = "", height: int = 320) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{x}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-25, labelLimit=180)),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ").title()),
            color=alt.Color(f"{color}:N") if color else alt.value("#217c7e"),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def hbar_chart(df: pd.DataFrame, y: str, x: str = "count", color: str | None = None, title: str = "", height: int = 360) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=2, cornerRadiusBottomRight=2)
        .encode(
            x=alt.X(f"{x}:Q", title=x.replace("_", " ").title()),
            y=alt.Y(f"{y}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=280)),
            color=alt.Color(f"{color}:N") if color else alt.value("#2563eb"),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def heatmap_from_crosstab(df: pd.DataFrame, row_col: str, title: str) -> None:
    if df.empty or row_col not in df.columns:
        st.info("No crosstab data available.")
        return
    melted = df.melt(id_vars=[row_col], var_name="column", value_name="count")
    chart = (
        alt.Chart(melted)
        .mark_rect()
        .encode(
            x=alt.X("column:N", title=None, axis=alt.Axis(labelAngle=-35, labelLimit=160)),
            y=alt.Y(f"{row_col}:N", title=None),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=[row_col, "column", "count"],
        )
        .properties(title=title, height=320)
    )
    text = alt.Chart(melted).mark_text(fontSize=11).encode(
        x="column:N",
        y=f"{row_col}:N",
        text="count:Q",
        color=alt.condition(alt.datum.count > melted["count"].max() * 0.55, alt.value("white"), alt.value("#17202a")),
    )
    st.altair_chart(chart + text, use_container_width=True)


def numeric_hist(df: pd.DataFrame, col: str, title: str) -> None:
    if df.empty or col not in df.columns or df[col].dropna().empty:
        st.info("No numeric values available.")
        return
    chart = (
        alt.Chart(df.dropna(subset=[col]))
        .mark_bar()
        .encode(
            x=alt.X(f"{col}:Q", bin=alt.Bin(maxbins=30), title=col.replace("_", " ").title()),
            y=alt.Y("count():Q", title="Rows"),
            tooltip=[alt.Tooltip(f"{col}:Q", bin=True), alt.Tooltip("count():Q")],
        )
        .properties(title=title, height=300)
    )
    st.altair_chart(chart, use_container_width=True)


def show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_column_width=True)
    else:
        st.info(f"Missing image: `{path.relative_to(ROOT)}`")


st.title("Thesis Systematic Workflow Dashboard")
st.caption("Graphs generated from the current thesis workflow outputs, revision analysis files, visualizations, JSONL runs, and background job status.")

tone_records = load_csv(str(VIS / "tone_records_flat.csv"))
tone_esg = load_csv(str(VIS / "tone_esg_crosstab.csv"))
tone_climatebert = load_csv(str(VIS / "tone_climatebert_label_crosstab.csv"))
model_stability = load_csv(str(REVISION / "model_stability_summary.csv"))
prompt_stability = load_csv(str(REVISION / "prompt_stability_summary.csv"))
failure_counts = load_csv(str(REVISION / "failure_mode_counts.csv"))
ocr_summary = load_csv(str(REVISION / "ocr_processing_summary.csv"))
ontology_coverage = load_csv(str(REVISION / "ontology_coverage.csv"))
greenwashing = load_csv(str(REVISION / "greenwashing_index_by_company.csv"))
agreement = load_csv(str(REVISION / "climatebert_proxy_agreement_summary.csv"))
seed = load_csv(str(REVISION / "pilot_ground_truth_seed.csv"))
t2_flat = t2_flat_frame()
inventory = artifact_inventory()
llm_jobs = job_status_frame(RESULTS / "background_llm_jobs")
gt_jobs = job_status_frame(RESULTS / "ground_truth_background_jobs")
rq_df = workflow_rq_df()

with st.sidebar:
    st.header("Dashboard")
    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"Workflow: `{WORKFLOW_PATH}`")
    st.markdown(f"Results: `{RESULTS}`")

metrics = st.columns(8)
metrics[0].metric("Workflow RQs", f"{len(rq_df):,}")
metrics[1].metric("Tone records", f"{len(tone_records):,}")
metrics[2].metric("T2 rows", f"{len(t2_flat):,}")
metrics[3].metric("Pilot labels", f"{len(seed):,}")
metrics[4].metric("OCR docs", f"{len(ocr_summary):,}")
metrics[5].metric("Artifacts", f"{len(inventory):,}")
metrics[6].metric("LLM jobs", f"{len(llm_jobs):,}")
metrics[7].metric("GT jobs", f"{len(gt_jobs):,}")

tabs = st.tabs(
    [
        "Workflow Coverage",
        "Pipeline Outputs",
        "Diagnostics",
        "Stability",
        "Ground Truth",
        "Artifacts & Images",
    ]
)

with tabs[0]:
    st.subheader("Research-question implementation coverage")
    c1, c2 = st.columns(2)
    with c1:
        hbar_chart(rq_df, "stage", "implemented_modules", color="rq", title="Implemented modules per thesis workflow stage")
    with c2:
        hbar_chart(rq_df, "stage", "artifact_groups", color="rq", title="Generated artifact groups per stage")
    st.dataframe(rq_df, use_container_width=True, hide_index=True)

    st.subheader("Current artifact inventory")
    if inventory.empty:
        st.warning("No result artifacts found.")
    else:
        c3, c4 = st.columns(2)
        with c3:
            bar_chart(count_df(inventory, "group"), "group", title="Artifacts by result group")
        with c4:
            bar_chart(count_df(inventory, "extension"), "extension", title="Artifacts by file type")

with tabs[1]:
    st.subheader("Tone-aware ESG extraction results")
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(count_df(tone_records, "tone"), "tone", title="Extracted tone distribution")
    with c2:
        bar_chart(count_df(tone_records, "esg"), "esg", title="Extracted ESG pillar distribution")
    heatmap_from_crosstab(tone_esg, "tone", "Tone x ESG pillar crosstab")
    heatmap_from_crosstab(tone_climatebert, "tone", "Tone x ClimateBERT/proxy label crosstab")

    st.subheader("T2 rule/hybrid outputs")
    c3, c4 = st.columns(2)
    with c3:
        bar_chart(count_df(t2_flat, "tone_pred"), "tone_pred", title="T2 hybrid tone predictions")
    with c4:
        bar_chart(count_df(t2_flat, "sentiment_pred"), "sentiment_pred", title="T2 hybrid sentiment predictions")
    numeric_hist(t2_flat, "ontology_alignment", "T2 ontology alignment distribution")

with tabs[2]:
    st.subheader("OCR and extraction diagnostics")
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(count_df(ocr_summary, "status"), "status", title="OCR processing status")
    with c2:
        if not ocr_summary.empty and "pages" in ocr_summary.columns:
            top_pages = ocr_summary.sort_values("pages", ascending=False).head(15)
            hbar_chart(top_pages, "document", "pages", title="Largest OCR documents by page count")
        else:
            st.info("No OCR page counts available.")

    st.subheader("Failure modes and ontology coverage")
    c3, c4 = st.columns(2)
    with c3:
        if not failure_counts.empty:
            failure_view = failure_counts.copy()
            failure_view["mode_tone"] = failure_view["mode"].map(clean) + " | " + failure_view["tone_pred"].map(clean)
            hbar_chart(failure_view.sort_values("count", ascending=False).head(20), "mode_tone", "count", title="Top failure modes")
        else:
            st.info("No failure mode counts available.")
    with c4:
        if not ontology_coverage.empty:
            ontology_view = ontology_coverage.sort_values("records", ascending=False).head(20)
            hbar_chart(ontology_view, "aspect", "records", color="mapped_to_ontology", title="Ontology coverage by aspect")
        else:
            st.info("No ontology coverage file available.")

    st.subheader("Greenwashing index")
    if not greenwashing.empty:
        hbar_chart(greenwashing.sort_values("greenwashing_index", ascending=False), "company", "greenwashing_index", title="Greenwashing index by company", height=360)
        st.dataframe(greenwashing, use_container_width=True, hide_index=True)
    else:
        st.info("No greenwashing index file available.")

with tabs[3]:
    st.subheader("Model stability")
    c1, c2 = st.columns(2)
    with c1:
        hbar_chart(model_stability, "model", "json_parse_success_rate", title="JSON parse success by model")
    with c2:
        hbar_chart(model_stability, "model", "schema_drift_rate", title="Schema drift by model")

    st.subheader("Prompt stability")
    c3, c4 = st.columns(2)
    with c3:
        hbar_chart(prompt_stability, "prompt", "field_completion_rate", title="Field completion by prompt")
    with c4:
        hbar_chart(prompt_stability, "prompt", "missing_tone_rate", title="Missing tone rate by prompt")

    st.subheader("ClimateBERT proxy agreement")
    if not agreement.empty:
        agree_long = agreement.melt(id_vars=["comparison"], var_name="metric", value_name="value")
        numeric = agree_long[pd.to_numeric(agree_long["value"], errors="coerce").notna()].copy()
        numeric["value"] = pd.to_numeric(numeric["value"], errors="coerce")
        bar_chart(numeric[numeric["metric"].ne("n")], "metric", "value", title="Agreement metrics", height=300)
        st.dataframe(agreement, use_container_width=True, hide_index=True)
    else:
        st.info("No ClimateBERT proxy agreement summary available.")

with tabs[4]:
    st.subheader("Pilot ground-truth seed")
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(count_df(seed, "review_status"), "review_status", title="Review status")
    with c2:
        bar_chart(count_df(seed, "language"), "language", title="Language distribution")
    c3, c4 = st.columns(2)
    with c3:
        bar_chart(count_df(seed, "tone_pred"), "tone_pred", title="Predicted tone in annotation seed")
    with c4:
        bar_chart(count_df(seed, "silver_tone_ground_truth"), "silver_tone_ground_truth", title="Silver tone labels")
    if not seed.empty:
        flags = []
        for col in ["needs_human_review", "schema_drift", "has_climate_commitment", "has_environmental_claims", "has_climate_d"]:
            if col in seed.columns:
                flags.append({"flag": col, "count": int(seed[col].fillna(False).astype(bool).sum())})
        bar_chart(pd.DataFrame(flags), "flag", title="Annotation seed review flags")
        st.dataframe(seed.head(300), use_container_width=True, hide_index=True, height=420)

    st.subheader("Background job status")
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("**LLM background jobs**")
        bar_chart(count_df(llm_jobs, "status"), "status", title="LLM job status")
        st.dataframe(llm_jobs, use_container_width=True, hide_index=True)
    with c6:
        st.markdown("**Ground-truth background jobs**")
        bar_chart(count_df(gt_jobs, "status"), "status", title="Ground-truth job status")
        st.dataframe(gt_jobs, use_container_width=True, hide_index=True)

with tabs[5]:
    st.subheader("Existing visualization artifacts")
    image_paths = [
        VIS / "tone_distribution.png",
        VIS / "esg_by_tone.png",
        VIS / "aspect_by_tone_heatmap.png",
        VIS / "climatebert_label_by_tone.png",
        VIS / "climatebert_remote_top_scores.png",
    ]
    cols = st.columns(2)
    for index, path in enumerate(image_paths):
        with cols[index % 2]:
            show_image(path, path.name)

    st.subheader("Dashboard image catalog")
    catalog_path = VIS / "streamlit_outputs" / "dashboard_image_catalog.json"
    catalog = load_json(str(catalog_path))
    if isinstance(catalog, list):
        st.dataframe(pd.DataFrame(catalog), use_container_width=True, hide_index=True)
    elif isinstance(catalog, dict):
        st.json(catalog, expanded=False)

    st.subheader("Result artifact table")
    if inventory.empty:
        st.warning("No artifacts found.")
    else:
        st.dataframe(inventory.sort_values("modified", ascending=False), use_container_width=True, hide_index=True, height=520)
