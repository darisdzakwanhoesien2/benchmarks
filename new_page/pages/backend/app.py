from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Backend App", layout="wide")

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
LOGS_DIR = ROOT / "logs"
BG_DIR = RESULTS_DIR / "background_llm_jobs"


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def summarize_jobs() -> pd.DataFrame:
    rows = []
    if not BG_DIR.exists():
        return pd.DataFrame(rows)

    for job_dir in sorted(BG_DIR.iterdir(), reverse=True):
        if not job_dir.is_dir():
            continue
        status = load_json(job_dir / "status.json")
        cfg = load_json(job_dir / "config.json")
        rows.append(
            {
                "job_id": status.get("job_id", job_dir.name),
                "status": status.get("status", "unknown"),
                "document": status.get("document", cfg.get("document", "")),
                "model_count": len(cfg.get("models", [])) if isinstance(cfg.get("models"), list) else None,
                "prompts": ", ".join(cfg.get("prompt_names", [])) if isinstance(cfg.get("prompt_names"), list) else "",
                "total": status.get("total"),
                "completed": status.get("completed"),
                "failed": status.get("failed"),
                "skipped": status.get("skipped"),
                "created_at": status.get("created_at", cfg.get("created_at")),
                "updated_at": status.get("updated_at"),
                "path": str(job_dir),
            }
        )
    return pd.DataFrame(rows)


def read_events(job_path: Path, max_lines: int = 5000) -> pd.DataFrame:
    events_path = job_path / "events.jsonl"
    if not events_path.exists():
        return pd.DataFrame()

    rows = []
    with events_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= max_lines:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"event": "malformed_json", "raw": line})
    return pd.DataFrame(rows)


def read_text(path: Path, max_chars: int = 30000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n... [truncated]"
    return text


def render_jobs() -> None:
    st.subheader("Background LLM Jobs")
    jobs = summarize_jobs()
    if jobs.empty:
        st.info(f"No job folders found in `{BG_DIR}`.")
        return

    status_options = sorted({str(v) for v in jobs["status"].dropna().astype(str)})
    selected_status = st.multiselect("Filter by status", status_options, default=[])
    if selected_status:
        jobs = jobs[jobs["status"].astype(str).isin(selected_status)]

    max_rows = st.number_input("Jobs to show", min_value=10, max_value=5000, value=200, step=10)
    jobs_view = jobs.head(int(max_rows)).copy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jobs shown", f"{len(jobs_view):,}")
    c2.metric("Completed", f"{(jobs_view['status'].astype(str) == 'completed').sum():,}")
    c3.metric("Failed", f"{(jobs_view['status'].astype(str) == 'failed').sum():,}")
    c4.metric("Running", f"{(jobs_view['status'].astype(str) == 'running').sum():,}")

    st.dataframe(
        jobs_view[
            ["job_id", "status", "document", "total", "completed", "failed", "skipped", "created_at", "updated_at"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    selected_job = st.selectbox("Inspect job", jobs_view["job_id"].tolist())
    row = jobs[jobs["job_id"] == selected_job].head(1)
    if row.empty:
        return
    job_path = Path(row.iloc[0]["path"])

    st.markdown(f"Job path: `{job_path}`")
    st.markdown("Config")
    st.json(load_json(job_path / "config.json"))

    st.markdown("Status")
    st.json(load_json(job_path / "status.json"))

    events = read_events(job_path)
    if events.empty:
        st.info("No events loaded.")
    else:
        st.markdown("Events")
        st.dataframe(events, use_container_width=True, hide_index=True)
        if "event" in events.columns:
            counts = events["event"].fillna("(missing)").astype(str).value_counts().head(12)
            st.bar_chart(counts)


def render_logs() -> None:
    st.subheader("Logs")
    log_candidates = sorted(LOGS_DIR.glob("*"))
    if not log_candidates:
        st.info(f"No log files in `{LOGS_DIR}`.")
        return

    selected = st.selectbox("Choose log file", log_candidates, format_func=lambda p: p.name, key="log_file")
    if selected.suffix.lower() == ".json":
        data = load_json(selected)
        st.json(data)
        if isinstance(data, dict):
            st.caption(f"Entries: {len(data):,}")
    else:
        text = read_text(selected)
        if not text:
            st.info("Log is empty.")
        else:
            st.code(text)


def render_core_artifacts() -> None:
    st.subheader("Core Artifact Sizes")
    files = [
        RESULTS_DIR / "esg_records.json",
        RESULTS_DIR / "t1_results.jsonl",
        RESULTS_DIR / "t2_results.jsonl",
        ROOT / "data" / "thesis_pdf",
        RESULTS_DIR / "revision_analysis" / "pilot_ground_truth_annotations.csv",
    ]
    rows = []
    for p in files:
        if p.exists():
            if p.is_file():
                size = p.stat().st_size
                rows.append(
                    {
                        "path": str(p.relative_to(ROOT)),
                        "type": "file",
                        "size_mb": round(size / (1024 * 1024), 2),
                        "modified": pd.to_datetime(p.stat().st_mtime, unit="s"),
                    }
                )
            elif p.is_dir():
                count = sum(1 for _ in p.glob("*"))
                rows.append(
                    {
                        "path": str(p.relative_to(ROOT)),
                        "type": "dir",
                        "size_mb": None,
                        "modified": pd.to_datetime(p.stat().st_mtime, unit="s"),
                        "entries": count,
                    }
                )
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No core artifacts found.")


def main() -> None:
    st.title("Backend Monitor")
    st.caption(f"Project root: `{ROOT}`")

    t1, t2, t3 = st.tabs(["Jobs", "Logs", "Artifacts"])
    with t1:
        render_jobs()
    with t2:
        render_logs()
    with t3:
        render_core_artifacts()


if __name__ == "__main__":
    main()
