from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import signal
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
LLM_PROCESS_DIR = RESULTS_DIR / "llm_processing_process"
LLM_PROCESS_STATE = LLM_PROCESS_DIR / "state.json"
LLM_PROCESS_LOG = LLM_PROCESS_DIR / "llm_processing.log"
LLM_PROCESS_ERR = LLM_PROCESS_DIR / "llm_processing.err.log"
LLM_PROCESS_PORT_DEFAULT = 8521


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


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(data, ensure_ascii=False) + "\n")


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


def launch_llm_processing_process(port: int) -> dict[str, Any]:
    LLM_PROCESS_DIR.mkdir(parents=True, exist_ok=True)
    with LLM_PROCESS_LOG.open("ab") as stdout, LLM_PROCESS_ERR.open("ab") as stderr:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(Path(__file__).resolve().parent / "llm_processing.py"),
                "--server.headless",
                "true",
                "--server.port",
                str(port),
            ],
            cwd=str(Path(__file__).resolve().parent),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    state = {
        "pid": process.pid,
        "port": port,
        "status": "running",
        "url": f"http://localhost:{port}",
        "started_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    write_json(LLM_PROCESS_STATE, state)
    return state


def stop_llm_processing_process(pid: int | None) -> dict[str, Any]:
    state = read_json(LLM_PROCESS_STATE, {})
    if pid and is_process_alive(pid):
        try:
            os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
        except Exception:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except Exception:
                pass
    state.update(
        {
            "status": "stopped",
            "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
    )
    write_json(LLM_PROCESS_STATE, state)
    return state


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


def is_restartable_status(status: dict[str, Any], alive: bool = False) -> bool:
    if alive:
        return False
    status_name = str(status.get("status", "")).lower()
    failed_value = status.get("failed") or 0
    failed = 0 if pd.isna(failed_value) else int(failed_value)
    return status_name in {"failed", "exited", "error", "stopped"} or failed > 0


def restart_job(job_id: str, skip_existing_successes: bool = True) -> bool:
    job_dir = JOBS_DIR / job_id
    config_path = job_dir / "config.json"
    status_path = job_dir / "status.json"
    control_path = job_dir / "control.json"
    events_path = job_dir / "events.jsonl"
    config = read_json(config_path, {})
    status = read_json(status_path, {})
    if not config:
        return False
    if is_process_alive(status.get("pid")):
        return False

    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    restarts = config.get("restart_history", [])
    if not isinstance(restarts, list):
        restarts = []
    restarts.append(
        {
            "time": now,
            "previous_status": status.get("status", "unknown"),
            "previous_completed": int(status.get("completed") or 0),
            "previous_failed": int(status.get("failed") or 0),
            "previous_skipped": int(status.get("skipped") or 0),
            "skip_existing_successes": skip_existing_successes,
        }
    )
    config["restart_history"] = restarts
    config["skip_existing"] = bool(skip_existing_successes)
    write_json(config_path, config)

    status.update(
        {
            "status": "queued",
            "pid": None,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "current": "Queued for restart",
            "restarted_at": now,
            "updated_at": now,
        }
    )
    status.pop("error", None)
    status.pop("finished_at", None)
    write_json(status_path, status)
    write_json(control_path, {"pause_requested": False, "stop_requested": False, "updated_at": now})
    append_jsonl(
        events_path,
        {
            "time": now,
            "event": "restart_requested",
            "skip_existing_successes": skip_existing_successes,
        },
    )
    launch_job(job_id)
    return True


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


def discover_llm_processing_processes() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    try:
        result = subprocess.run(
            ["ps", "-ax", "-o", "pid=", "-o", "command="],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return pd.DataFrame(columns=["pid", "kind", "command", "port", "known_state"])

    known_state = read_json(LLM_PROCESS_STATE, {})
    known_pid = str(known_state.get("pid") or "")
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        pid, command = parts
        if "llm_processing.py" not in command:
            continue
        port_match = re.search(r"--server\.port\s+(\d+)", command)
        rows.append(
            {
                "pid": int(pid),
                "kind": "continuous llm_processing.py",
                "port": int(port_match.group(1)) if port_match else None,
                "known_state": "tracked" if pid == known_pid else "discovered",
                "alive": is_process_alive(int(pid)),
                "command": command,
            }
        )
    return pd.DataFrame(rows)


def jobs_overview_df() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for job_id in list_jobs():
        job_dir = JOBS_DIR / job_id
        status = read_json(job_dir / "status.json", {})
        config = read_json(job_dir / "config.json", {})
        pid = status.get("pid")
        total = int(status.get("total") or 0)
        completed = int(status.get("completed") or 0)
        rows.append(
            {
                "job_id": job_id,
                "status": status.get("status", "unknown"),
                "alive": is_process_alive(pid),
                "pid": pid,
                "progress_pct": round((completed / total * 100), 1) if total else 0.0,
                "completed": completed,
                "total": total,
                "failed": int(status.get("failed") or 0),
                "skipped": int(status.get("skipped") or 0),
                "document": status.get("document") or config.get("document", ""),
                "current": status.get("current", ""),
                "updated_at": status.get("updated_at", ""),
            }
        )
    return pd.DataFrame(rows)


st.title("LLM Background Run Monitor")
st.caption("Run T3-style LLM ESG extraction behind the scenes and visualize progress without keeping the main `llm_processing.py` page busy.")

JOBS_DIR.mkdir(parents=True, exist_ok=True)
LLM_PROCESS_DIR.mkdir(parents=True, exist_ok=True)

llm_process_state = read_json(LLM_PROCESS_STATE, {})
llm_process_pid = llm_process_state.get("pid")
llm_process_alive = is_process_alive(llm_process_pid)
if llm_process_state and llm_process_state.get("status") == "running" and not llm_process_alive:
    llm_process_state["status"] = "exited"
    llm_process_state["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    write_json(LLM_PROCESS_STATE, llm_process_state)

with st.expander("Continuous llm_processing.py process", expanded=True):
    st.markdown(
        """
        This section runs the actual `llm_processing.py` Streamlit page as a separate long-lived process.
        Use it when you want the original extraction page to stay alive continuously, then open its URL
        and operate the normal `llm_processing.py` controls there.
        """
    )
    proc_cols = st.columns(4)
    proc_cols[0].metric("Process status", "running" if llm_process_alive else llm_process_state.get("status", "not started"))
    proc_cols[1].metric("PID", str(llm_process_pid or "None"))
    proc_cols[2].metric("Port", str(llm_process_state.get("port") or LLM_PROCESS_PORT_DEFAULT))
    proc_cols[3].metric("Updated", str(llm_process_state.get("updated_at", ""))[-9:] or "None")
    if llm_process_state.get("url"):
        st.markdown(f"[Open running llm_processing.py]({llm_process_state['url']})")
    st.caption(
        "Important: this keeps the original page/server running. It does not auto-click its Run button. "
        "The background job controls below are for queue-style automatic runs."
    )

with st.sidebar:
    st.header("Continuous llm_processing.py")
    process_port = st.number_input(
        "Process port",
        min_value=8501,
        max_value=8999,
        value=int(llm_process_state.get("port") or LLM_PROCESS_PORT_DEFAULT),
    )
    if st.button(
        "Run llm_processing.py continuously",
        disabled=llm_process_alive,
        use_container_width=True,
    ):
        launch_llm_processing_process(int(process_port))
        st.rerun()
    if st.button(
        "Stop llm_processing.py process",
        disabled=not llm_process_alive,
        use_container_width=True,
    ):
        stop_llm_processing_process(llm_process_pid)
        st.rerun()
    if llm_process_state:
        st.caption(f"Status: `{llm_process_state.get('status', 'unknown')}`")
        st.caption(f"URL: `{llm_process_state.get('url', '')}`")

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

st.subheader("All running and known LLM processes")
process_df = discover_llm_processing_processes()
jobs_df = jobs_overview_df()
running_jobs = jobs_df[jobs_df["alive"].eq(True)] if not jobs_df.empty and "alive" in jobs_df else pd.DataFrame()
running_continuous = process_df[process_df["alive"].eq(True)] if not process_df.empty and "alive" in process_df else pd.DataFrame()

overview_cols = st.columns(5)
overview_cols[0].metric("Continuous processes", f"{len(process_df):,}")
overview_cols[1].metric("Running continuous", f"{len(running_continuous):,}")
overview_cols[2].metric("Background jobs", f"{len(jobs_df):,}")
overview_cols[3].metric("Running jobs", f"{len(running_jobs):,}")
overview_cols[4].metric("Failed jobs", f"{int(jobs_df['failed'].sum()):,}" if not jobs_df.empty and "failed" in jobs_df else "0")

overview_tab, process_tab, jobs_tab = st.tabs(["Overview Dashboard", "llm_processing.py Processes", "Background Jobs"])

with overview_tab:
    left, right = st.columns([1, 1])
    with left:
        if jobs_df.empty:
            st.info("No background jobs have been created yet.")
        else:
            status_counts = jobs_df["status"].fillna("unknown").value_counts().rename_axis("status").reset_index(name="count")
            chart = (
                alt.Chart(status_counts)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("status:N", sort="-y", title=None),
                    y=alt.Y("count:Q", title="Jobs"),
                    color=alt.value("#2563eb"),
                    tooltip=["status", "count"],
                )
                .properties(height=260, title="Jobs by status")
            )
            st.altair_chart(chart, use_container_width=True)
    with right:
        if jobs_df.empty:
            st.info("No progress data yet.")
        else:
            progress_chart_df = jobs_df[["job_id", "progress_pct", "status"]].copy().head(20)
            chart = (
                alt.Chart(progress_chart_df)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("progress_pct:Q", title="Progress %"),
                    y=alt.Y("job_id:N", sort="-x", title=None, axis=alt.Axis(labelLimit=220)),
                    color=alt.Color("status:N", legend=None),
                    tooltip=["job_id", "status", "progress_pct"],
                )
                .properties(height=260, title="Latest job progress")
            )
            st.altair_chart(chart, use_container_width=True)

with process_tab:
    if process_df.empty:
        st.info("No running `llm_processing.py` Streamlit process was discovered by `ps -ax`.")
    else:
        st.dataframe(
            process_df[["pid", "kind", "alive", "port", "known_state", "command"]],
            use_container_width=True,
            hide_index=True,
        )

with jobs_tab:
    if jobs_df.empty:
        st.info("No background jobs found in `results/background_llm_jobs`.")
    else:
        status_filter = st.multiselect(
            "Filter job statuses",
            sorted(jobs_df["status"].fillna("unknown").unique()),
            default=[],
        )
        visible_jobs = jobs_df
        if status_filter:
            visible_jobs = visible_jobs[visible_jobs["status"].isin(status_filter)]
        st.dataframe(
            visible_jobs[
                [
                    "job_id",
                    "status",
                    "alive",
                    "pid",
                    "progress_pct",
                    "completed",
                    "total",
                    "failed",
                    "skipped",
                    "document",
                    "current",
                    "updated_at",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
        restartable_jobs = [
            row["job_id"]
            for _, row in visible_jobs.iterrows()
            if is_restartable_status({"status": row.get("status"), "failed": row.get("failed")}, bool(row.get("alive")))
        ]
        st.markdown("**Restart failed/error jobs**")
        st.caption(
            "Restartable jobs include hard failures, exited/stopped workers, and completed jobs with failed samples."
        )
        restart_targets = st.multiselect(
            "Jobs to restart",
            restartable_jobs,
            default=restartable_jobs[:1],
            disabled=not restartable_jobs,
        )
        bulk_skip_successes = st.checkbox(
            "Skip already successful samples during bulk restart",
            value=True,
            help="Uses records already saved in esg_records.json so restart focuses on failed or missing work.",
        )
        if st.button(
            "Restart selected error jobs",
            disabled=not restart_targets,
            type="primary",
            use_container_width=True,
        ):
            restarted = [job_id for job_id in restart_targets if restart_job(job_id, bulk_skip_successes)]
            st.success(f"Restarted {len(restarted)} job(s).")
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

restartable_selected_job = is_restartable_status(status, alive)
restart_skip_successes = st.checkbox(
    "On restart, skip already successful model/target/prompt triples",
    value=True,
    disabled=not restartable_selected_job,
    help="Keeps successful rows in esg_records.json and reruns failed or missing items. Turn this off only if you want to rerun everything.",
)

control_cols = st.columns(6)
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
    if st.button("Restart error run", disabled=not restartable_selected_job, type="primary", use_container_width=True):
        if restart_job(selected_job, restart_skip_successes):
            st.success(f"Restarted `{selected_job}`")
            st.rerun()
        else:
            st.error("Could not restart this job. It may still be running or missing config.json.")
with control_cols[5]:
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
