from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls

st.set_page_config(page_title="A.4 Per-Model Background Run", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "tools" / "climatebert_a4" / "generate_a4_per_model.py"
LOG_DIR = ROOT / "logs"
LOG_PATH = LOG_DIR / "a4_per_model.log"
PID_PATH = LOG_DIR / "a4_per_model.pid"

st.title("A.4 Per-Model Background Run")
st.caption("Run per-model full A.4 crosstab generation in background and monitor job state.")


def read_pid() -> int | None:
    if not PID_PATH.exists():
        return None
    try:
        return int(PID_PATH.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def is_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        subprocess.run(["kill", "-0", str(pid)], check=True, capture_output=True, text=True)
        return True
    except Exception:
        return False


def tail_log(path: Path, max_lines: int = 80) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[-max_lines:])


pid = read_pid()
running = is_running(pid)

m1, m2, m3 = st.columns(3)
m1.metric("Script", "ready" if SCRIPT_PATH.exists() else "missing")
m2.metric("Background PID", str(pid) if pid else "none")
m3.metric("Status", "running" if running else "idle")

controls = st.columns([1, 1, 1, 3])
with controls[0]:
    if st.button("Start Background Run", type="primary", use_container_width=True):
        if not SCRIPT_PATH.exists():
            st.error(f"Missing script: {SCRIPT_PATH}")
        else:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            cmd = f"nohup python3 {SCRIPT_PATH} > {LOG_PATH} 2>&1 & echo $!"
            out = subprocess.check_output(cmd, shell=True, text=True).strip()
            PID_PATH.write_text(out + "\n", encoding="utf-8")
            st.success(f"Started background run PID {out}")
            st.rerun()

with controls[1]:
    if st.button("Refresh Status", use_container_width=True):
        st.rerun()

with controls[2]:
    if st.button("Stop Run", use_container_width=True):
        if running and pid:
            try:
                subprocess.run(["kill", str(pid)], check=True)
                st.warning(f"Stopped PID {pid}")
            except Exception as exc:
                st.error(f"Failed to stop PID {pid}: {exc}")
        else:
            st.info("No running PID to stop.")
        st.rerun()

st.divider()
st.subheader("Run Log")
last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.caption(f"Last refresh: {last_update}")
log_text = tail_log(LOG_PATH)
if log_text:
    st.code(log_text, language="text")
else:
    st.info("No log output yet.")

st.subheader("Quick Output Check")
vis_dir = ROOT / "results" / "visualizations"
manifest_path = vis_dir / "tone_climatebert_label_crosstab_full__by_model_manifest.csv"
if manifest_path.exists():
    try:
        manifest = pd.read_csv(manifest_path)
        st.dataframe(manifest, use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"Could not read manifest: {exc}")
else:
    st.info("Manifest not found yet. Start a run first.")
