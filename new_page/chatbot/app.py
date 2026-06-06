from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
REVIEW_PATH = Path(__file__).resolve().with_name("review_paper.md")
THESIS_DASHBOARD_DIR = ROOT_DIR / "results" / "thesis_workflow_dashboard"
REVISION_ANALYSIS_DIR = ROOT_DIR / "results" / "revision_analysis"


st.set_page_config(page_title="Chatbot Review Paper", page_icon="💬", layout="wide")


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _top(rows: list[dict[str, str]], key: str, n: int = 8) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = (row.get(key) or "").strip()
        counter[value if value else "<BLANK>"] += 1
    return counter.most_common(n)


def _table(items: list[tuple[str, int]], key_name: str, count_name: str = "count") -> str:
    if not items:
        return "No data available."
    lines = [f"| {key_name} | {count_name} |", "|---|---:|"]
    for key, value in items:
        lines.append(f"| {key} | {value:,} |")
    return "\n".join(lines)


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _pick_data_dir() -> Path:
    if THESIS_DASHBOARD_DIR.exists():
        return THESIS_DASHBOARD_DIR
    return REVISION_ANALYSIS_DIR


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, Any]:
    data_dir = _pick_data_dir()
    dashboard_metrics = _load_json(data_dir / "dashboard_metrics.json")

    pilot = _load_csv(data_dir / "pilot_ground_truth_seed.csv")
    if not pilot:
        pilot = _load_csv(data_dir / "pilot_ground_truth_annotations.csv")

    verifier = _load_csv(data_dir / "llm_statement_page_verifier_compiled.csv")
    failure = _load_csv(data_dir / "failure_mode_counts.csv")
    if not failure:
        failure = _load_csv(data_dir / "failure_modes.csv")

    ontology = _load_csv(data_dir / "ontology_coverage.csv")
    prompt_stability = _load_csv(data_dir / "prompt_stability_summary.csv")
    model_stability = _load_csv(data_dir / "model_stability_summary.csv")
    llm_jobs = _load_csv(data_dir / "llm_background_jobs.csv")
    workflow_report = data_dir / "thesis_dashboard_report.md"

    return {
        "data_dir": data_dir,
        "dashboard_metrics": dashboard_metrics,
        "pilot": pilot,
        "verifier": verifier,
        "failure": failure,
        "ontology": ontology,
        "prompt_stability": prompt_stability,
        "model_stability": model_stability,
        "llm_jobs": llm_jobs,
        "workflow_report": workflow_report,
    }


def render_header(data: dict[str, Any]) -> None:
    data_dir = data["data_dir"]
    source_label = "thesis_workflow_dashboard" if data_dir == THESIS_DASHBOARD_DIR else "revision_analysis"

    st.title("Evidence-Grounded Chatbots Review")
    st.caption(
        "Renders `chatbot/review_paper.md` and grounds it with current sustainability-report artifacts "
        f"from `results/{source_label}/`."
    )


def render_evidence_snapshot(data: dict[str, Any]) -> None:
    metrics = data["dashboard_metrics"]
    pilot = data["pilot"]
    verifier = data["verifier"]
    failure = data["failure"]
    ontology = data["ontology"]
    prompt_stability = data["prompt_stability"]
    model_stability = data["model_stability"]
    llm_jobs = data["llm_jobs"]

    st.subheader("Current Sustainable Report Evidence")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OCR docs", f"{_to_int(metrics.get('ocr_docs', len(llm_jobs))):,}")
    c2.metric("Tone records", f"{_to_int(metrics.get('tone_records', len(verifier))):,}")
    c3.metric("Pilot labels", f"{_to_int(metrics.get('pilot_labels', len(pilot))):,}")
    c4.metric("Artifacts", f"{_to_int(metrics.get('artifacts')):,}")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Prompt configs", f"{len(prompt_stability):,}")
    s2.metric("Model configs", f"{len(model_stability):,}")
    s3.metric("Ontology aspects", f"{len(ontology):,}")
    s4.metric("LLM jobs", f"{_to_int(metrics.get('llm_jobs', len(llm_jobs))):,}")

    if "climatebert_percent_agreement" in metrics or "climatebert_cohen_kappa" in metrics:
        a1, a2 = st.columns(2)
        a1.metric(
            "Climate proxy agreement",
            f"{_to_float(metrics.get('climatebert_percent_agreement')) * 100:.1f}%",
        )
        a2.metric(
            "Cohen kappa",
            f"{_to_float(metrics.get('climatebert_cohen_kappa')):.3f}",
        )

    left, right = st.columns(2)
    with left:
        if pilot:
            st.markdown("**Pilot distribution**")
            pilot_key = "ground_truth_esg" if "ground_truth_esg" in pilot[0] else "company"
            st.markdown(_table(_top(pilot, pilot_key), pilot_key))
        if ontology:
            st.markdown("**Ontology coverage**")
            aspect_key = "aspect" if "aspect" in ontology[0] else next(iter(ontology[0].keys()), "aspect")
            st.markdown(_table(_top(ontology, aspect_key), aspect_key))

    with right:
        if verifier:
            st.markdown("**Verifier / extraction status**")
            status_key = "best_status" if "best_status" in verifier[0] else "status"
            st.markdown(_table(_top(verifier, status_key), status_key))
        if failure:
            st.markdown("**Failure modes**")
            failure_key = "mode" if "mode" in failure[0] else "failure_modes"
            st.markdown(_table(_top(failure, failure_key), failure_key))


def render_charts(data: dict[str, Any]) -> None:
    chart_dir = data["data_dir"]
    chart_paths = [
        chart_dir / "tone_distribution.png",
        chart_dir / "esg_by_tone.png",
        chart_dir / "aspect_by_tone_heatmap.png",
        chart_dir / "climatebert_label_by_tone.png",
    ]
    existing = [path for path in chart_paths if path.exists()]
    if not existing:
        return

    st.subheader("Saved Dashboard Visuals")
    for idx in range(0, len(existing), 2):
        cols = st.columns(2)
        for col, path in zip(cols, existing[idx: idx + 2]):
            with col:
                st.image(str(path), caption=path.name, use_container_width=True)


def render_repo_context(data: dict[str, Any]) -> None:
    workflow_report = data["workflow_report"]
    st.subheader("Repo Context")
    st.markdown(
        f"""
- Active evidence directory: `{data["data_dir"].relative_to(ROOT_DIR)}`
- Review paper source: `chatbot/review_paper.md`
- Recommended output target for future experiments: `results/chatbot/`
"""
    )

    if workflow_report.exists():
        with st.expander("Workflow dashboard report excerpt"):
            st.markdown(workflow_report.read_text(encoding="utf-8"))


def render_review_paper() -> None:
    st.subheader("Review Paper")
    if not REVIEW_PATH.exists():
        st.error("Missing `chatbot/review_paper.md`.")
        return
    st.markdown(REVIEW_PATH.read_text(encoding="utf-8"))


def main() -> None:
    data = load_data()
    render_header(data)

    overview_tab, paper_tab = st.tabs(["Evidence Snapshot", "Review Paper"])

    with overview_tab:
        render_evidence_snapshot(data)
        st.divider()
        render_charts(data)
        st.divider()
        render_repo_context(data)

    with paper_tab:
        render_review_paper()


if __name__ == "__main__":
    main()
