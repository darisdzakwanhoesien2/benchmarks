from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
import uuid

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="LLM Background Run Monitor", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data" / "thesis_dataset"
PROMPT_DIR = ROOT / "prompt"
RESULTS_DIR = ROOT / "results"
JOBS_DIR = RESULTS_DIR / "background_llm_jobs"
WORKER_PATH = ROOT / "code" / "llm_background_worker.py"


def utc_now_id() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_events(path: Path) -> pd.DataFrame:
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return pd.DataFrame(rows)


def list_documents() -> list[str]:
    if not DATASET_DIR.exists():
        return []
    return sorted(path.name for path in DATASET_DIR.iterdir() if (path / "pages").exists())


def list_pages(document: str) -> list[str]:
    pages_dir = DATASET_DIR / document / "pages"
    if not pages_dir.exists():
        return []
    return [path.name for path in sorted(pages_dir.glob("*.md"))]


def list_prompts() -> list[str]:
    if not PROMPT_DIR.exists():
        return []
    return [path.name for path in sorted(PROMPT_DIR.glob("*.md"))]


def list_jobs() -> list[str]:
    if not JOBS_DIR.exists():
        return []
    return sorted([path.name for path in JOBS_DIR.iterdir() if path.is_dir()], reverse=True)


def is_process_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def launch_job(job_id: str) -> None:
    job_dir = JOBS_DIR / job_id
    log_path = job_dir / "worker.log"
    err_path = job_dir / "worker.err.log"
    job_dir.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as stdout, err_path.open("ab") as stderr:
        process = subprocess.Popen(
            [sys.executable, str(WORKER_PATH), job_id],
            cwd=str(ROOT),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    status = read_json(job_dir / "status.json", {})
    status.update(
        {
            "job_id": job_id,
            "pid": process.pid,
            "status": "running",
            "started_at": status.get("started_at") or datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
    )
    write_json(job_dir / "status.json", status)


def request_control(job_id: str, **updates: Any) -> None:
    control_path = JOBS_DIR / job_id / "control.json"
    control = read_json(control_path, {})
    control.update(updates)
    control["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    write_json(control_path, control)


def progress_chart(status: dict[str, Any]):
    total = int(status.get("total") or 0)
    completed = int(status.get("completed") or 0)
    failed = int(status.get("failed") or 0)
    skipped = int(status.get("skipped") or 0)
    remaining = max(total - completed, 0)
    data = pd.DataFrame(
        [
            {"state": "completed", "samples": max(completed - failed - skipped, 0)},
            {"state": "failed", "samples": failed},
            {"state": "skipped", "samples": skipped},
            {"state": "remaining", "samples": remaining},
        ]
    )
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("state:N", sort=["completed", "failed", "skipped", "remaining"], title=None),
            y=alt.Y("samples:Q", title="Samples"),
            color=alt.Color(
                "state:N",
                legend=None,
                scale=alt.Scale(
                    domain=["completed", "failed", "skipped", "remaining"],
                    range=["#2563eb", "#dc2626", "#a16207", "#94a3b8"],
                ),
            ),
            tooltip=["state", "samples"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def event_chart(events: pd.DataFrame):
    if events.empty or "event" not in events.columns:
        st.info("No event timeline yet.")
        return
    event_counts = events["event"].value_counts().rename_axis("event").reset_index(name="count")
    chart = (
        alt.Chart(event_counts)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("event:N", sort="-y", title=None),
            y=alt.Y("count:Q", title="Events"),
            color=alt.value("#0f766e"),
            tooltip=["event", "count"],
        )
        .properties(height=260)
    )
    st.altair_chart(chart, use_container_width=True)


st.title("LLM Background Run Monitor")
st.caption("Run T3-style LLM ESG extraction behind the scenes and visualize progress without keeping the main `llm_processing.py` page busy.")

JOBS_DIR.mkdir(parents=True, exist_ok=True)

with st.sidebar:
    st.header("Monitor")
    jobs = list_jobs()
    selected_job = st.selectbox("Existing jobs", jobs, index=0 if jobs else None, placeholder="No jobs yet")
    auto_refresh = st.toggle("Auto-refresh while running", value=True)
    refresh_seconds = st.slider("Refresh seconds", 2, 20, 5)
    if st.button("Refresh progress", use_container_width=True):
        st.rerun()

    st.header("New background run")
    documents = list_documents()
    selected_doc = st.selectbox("Document", documents, index=0 if documents else None)
    page_names = list_pages(selected_doc) if selected_doc else []
    page_mode = st.radio("Pages", ["First N pages", "Specific pages", "Page range"], horizontal=False)
    if page_mode == "First N pages":
        page_count = st.number_input("N pages", min_value=1, max_value=max(1, len(page_names)), value=min(3, max(1, len(page_names))))
        selected_pages = page_names[: int(page_count)]
    elif page_mode == "Page range":
        max_page = max(1, len(page_names))
        page_range = st.slider("Page range", min_value=1, max_value=max_page, value=(1, min(3, max_page)))
        selected_pages = page_names[page_range[0] - 1 : page_range[1]]
    else:
        selected_pages = st.multiselect("Select pages", page_names, default=page_names[:1])

    batch_size = st.number_input("Batch size", min_value=1, max_value=max(1, len(selected_pages)), value=1)
    prompts = list_prompts()
    selected_prompts = st.multiselect("Prompts", prompts, default=[prompts[0]] if prompts else [])
    prompt_override = st.text_area("Prompt override", height=100, help="Optional. If filled, this overrides selected prompt files.")

    backend = st.selectbox("Backend", ["Mock", "OpenRouter", "LM Studio / OpenAI-compatible", "Ollama"])
    default_model = "mock-model" if backend == "Mock" else "meta-llama/llama-3.1-8b-instruct:free"
    models_text = st.text_area("Model ids, one per line", value=default_model, height=80)
    mock_mode = backend == "Mock"
    openrouter_api_key = st.text_input("OpenRouter API key", value=os.getenv("OPENROUTER_API_KEY", ""), type="password")
    lmstudio_url = st.text_input("LM Studio/OpenAI-compatible URL", value="http://127.0.0.1:1234/v1")
    lmstudio_api_key = st.text_input("LM Studio/OpenAI-compatible API key", value=os.getenv("LMSTUDIO_API_KEY", ""), type="password")
    ollama_url = st.text_input("Ollama URL", value="http://127.0.0.1:11434")
    ollama_api_key = st.text_input("Ollama API key", value=os.getenv("OLLAMA_API_KEY", ""), type="password")

    context_length = st.number_input("Context length", min_value=500, max_value=100000, value=10000, step=500)
    max_tokens = st.number_input("Max tokens", min_value=64, max_value=8192, value=1500, step=64)
    temperature = st.number_input("Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
    retries = st.number_input("Retries", min_value=1, max_value=5, value=2)
    ollama_num_ctx = st.number_input("Ollama num_ctx", min_value=512, max_value=32768, value=2048, step=512)
    skip_existing = st.checkbox("Skip already successful model/target/prompt triples", value=True)
    save_results = st.checkbox("Append outputs to esg_records.json", value=True)

    can_start = bool(selected_doc and selected_pages and (selected_prompts or prompt_override.strip()) and models_text.strip())
    if st.button("Start background run", disabled=not can_start, use_container_width=True):
        job_id = f"llm_bg_{utc_now_id()}_{uuid.uuid4().hex[:6]}"
        job_dir = JOBS_DIR / job_id
        models = [line.strip() for line in models_text.splitlines() if line.strip()]
        total = len(models) * ((len(selected_pages) + int(batch_size) - 1) // int(batch_size)) * max(1, len(selected_prompts) if not prompt_override.strip() else 1)
        config = {
            "job_id": job_id,
            "document": selected_doc,
            "page_names": selected_pages,
            "batch_size": int(batch_size),
            "prompt_names": selected_prompts,
            "prompt_override": prompt_override,
            "backend": backend,
            "mock_mode": mock_mode,
            "models": models,
            "openrouter_api_key": openrouter_api_key,
            "lmstudio_url": lmstudio_url,
            "lmstudio_api_key": lmstudio_api_key,
            "ollama_url": ollama_url,
            "ollama_api_key": ollama_api_key,
            "ollama_num_ctx": int(ollama_num_ctx),
            "context_length": int(context_length),
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "retries": int(retries),
            "skip_existing": skip_existing,
            "save_results": save_results,
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
        write_json(job_dir / "config.json", config)
        write_json(job_dir / "control.json", {"pause_requested": False, "stop_requested": False})
        write_json(
            job_dir / "status.json",
            {
                "job_id": job_id,
                "status": "queued",
                "document": selected_doc,
                "total": total,
                "completed": 0,
                "failed": 0,
                "skipped": 0,
                "current": "Queued",
                "created_at": config["created_at"],
                "updated_at": config["created_at"],
            },
        )
        launch_job(job_id)
        st.success(f"Started `{job_id}`")
        st.rerun()

if not selected_job:
    st.info("Create a background run from the sidebar to start monitoring progress.")
    st.stop()

job_dir = JOBS_DIR / selected_job
status = read_json(job_dir / "status.json", {})
config = read_json(job_dir / "config.json", {})
control = read_json(job_dir / "control.json", {})
events = read_events(job_dir / "events.jsonl")

pid = status.get("pid")
alive = is_process_alive(pid)
if status.get("status") == "running" and not alive:
    status["status"] = "exited"
    status["current"] = "Worker process is no longer alive. Check logs for details."
    write_json(job_dir / "status.json", status)

total = int(status.get("total") or 0)
completed = int(status.get("completed") or 0)
progress = completed / total if total else 0.0

st.subheader(selected_job)
st.progress(progress, text=f"{completed}/{total} samples complete")

card1, card2, card3, card4 = st.columns(4)
card1.metric("Status", str(status.get("status", "unknown")))
card2.metric("Current", str(status.get("current", ""))[:38] or "None")
card3.metric("Updated", str(status.get("updated_at", ""))[-9:] or "None")
card4.metric("PID", str(pid or "None"), delta="alive" if alive else "not running")

control_cols = st.columns(5)
with control_cols[0]:
    if st.button("Refresh", use_container_width=True):
        st.rerun()
with control_cols[1]:
    if st.button("Pause after current", disabled=status.get("status") != "running", use_container_width=True):
        request_control(selected_job, pause_requested=True)
        st.rerun()
with control_cols[2]:
    if st.button("Resume / keep running", disabled=status.get("status") not in {"paused", "exited", "failed", "stopped"}, use_container_width=True):
        request_control(selected_job, pause_requested=False, stop_requested=False)
        launch_job(selected_job)
        st.rerun()
with control_cols[3]:
    if st.button("Stop after current", disabled=status.get("status") not in {"running", "paused"}, use_container_width=True):
        request_control(selected_job, stop_requested=True)
        st.rerun()
with control_cols[4]:
    st.download_button(
        "Download status",
        json.dumps(status, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"{selected_job}_status.json",
        mime="application/json",
        use_container_width=True,
    )

st.caption(
    "Pause/stop requests are cooperative: the worker finishes the current sample, then pauses or stops before starting the next model-target-prompt item."
)

viz_tab, events_tab, config_tab, logs_tab = st.tabs(["Progress Visualization", "Events", "Config", "Logs"])

with viz_tab:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        progress_chart(status)
    with c2:
        event_chart(events)

with events_tab:
    if events.empty:
        st.info("No worker events have been written yet.")
    else:
        st.dataframe(events.tail(200).iloc[::-1], use_container_width=True, hide_index=True)

with config_tab:
    display_config = dict(config)
    for key in ["openrouter_api_key", "lmstudio_api_key", "ollama_api_key"]:
        if display_config.get(key):
            display_config[key] = "***"
    st.json(display_config)

with logs_tab:
    st.markdown("**Worker stdout**")
    st.code((job_dir / "worker.log").read_text(encoding="utf-8", errors="ignore")[-8000:] if (job_dir / "worker.log").exists() else "")
    st.markdown("**Worker stderr**")
    st.code((job_dir / "worker.err.log").read_text(encoding="utf-8", errors="ignore")[-8000:] if (job_dir / "worker.err.log").exists() else "")

if auto_refresh and status.get("status") == "running":
    components.html(
        f"<script>setTimeout(() => window.parent.location.reload(), {int(refresh_seconds) * 1000});</script>",
        height=0,
    )
