import streamlit as st
from pathlib import Path
import threading
import time
import shutil
import re
import traceback

# Required packages: pip install -U streamlit huggingface_hub

st.set_page_config(page_title="ESG Model Downloader", layout="wide")

# ── Constants ────────────────────────────────────────────────────────────────
DEFAULT_SAVE_DIR = Path(__file__).parent.parent / "models"   # Adjust if needed

MODELS = {
    "ClimateBERT — distilroberta-base-climate-s": {
        "repo_id": "climatebert/distilroberta-base-climate-s",
        "task": "fill-mask",
        "size": "~82 MB",
        "est_mb": 82,
        "description": "Distilled RoBERTa model fine-tuned on climate-related text. Great for masked language modeling and climate domain adaptation.",
    },
    "ClimateBERT — distilroberta-base-climate-f": {
        "repo_id": "climatebert/distilroberta-base-climate-f",
        "task": "fill-mask",
        "size": "~82 MB",
        "est_mb": 82,
        "description": "ClimateBERT variant focused on climate fact detection.",
    },
    "ClimateBERT — climate-sentiment": {
        "repo_id": "climatebert/distilroberta-base-climate-sentiment",
        "task": "text-classification",
        "size": "~82 MB",
        "est_mb": 82,
        "description": "ClimateBERT fine-tuned for sentiment analysis (opportunity / neutral / risk) on climate text.",
    },
    "ProsusAI — finbert": {
        "repo_id": "ProsusAI/finbert",
        "task": "text-classification",
        "size": "~440 MB",
        "est_mb": 440,
        "description": "BERT model fine-tuned on financial news for sentiment analysis (positive / negative / neutral).",
    },
    "yiyanghkust — finbert-esg": {
        "repo_id": "yiyanghkust/finbert-esg",
        "task": "text-classification",
        "size": "~440 MB",
        "est_mb": 440,
        "description": "FinBERT variant specifically fine-tuned for ESG classification tasks.",
    },
}

# ── Session State Initialization ─────────────────────────────────────────────
for key in ["download_log", "download_done", "download_error", "download_progress", "download_in_progress"]:
    if key not in st.session_state:
        st.session_state[key] = {}

# ── Helper Functions ─────────────────────────────────────────────────────────
def local_dir_for(repo_id: str, base: Path) -> Path:
    slug = repo_id.replace("/", "--")
    return base / slug

def is_already_downloaded(repo_id: str, base: Path) -> bool:
    d = local_dir_for(repo_id, base)
    if not d.exists():
        return False
    # More reliable check: look for config.json (present in all HF models)
    return (d / "config.json").exists()

def folder_size_mb(path: Path) -> float:
    if not path.exists():
        return 0.0
    try:
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)
    except Exception:
        return 0.0

def append_log(repo_id: str, msg: str):
    if repo_id not in st.session_state.download_log:
        st.session_state.download_log[repo_id] = []
    ts = time.strftime("%H:%M:%S")
    st.session_state.download_log[repo_id].append(f"[{ts}] {msg}")

def parse_est_mb(info: dict) -> float:
    return float(info.get("est_mb", 100))

def run_download(repo_id: str, save_dir: Path, info: dict):
    """Background download function"""
    try:
        from huggingface_hub import snapshot_download

        local_dir = local_dir_for(repo_id, save_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        # Initialize state
        st.session_state.download_log[repo_id] = []
        st.session_state.download_done[repo_id] = False
        st.session_state.download_error[repo_id] = None
        st.session_state.download_in_progress[repo_id] = True
        st.session_state.download_progress[repo_id] = 0.0

        append_log(repo_id, f"Starting download of {repo_id}")
        append_log(repo_id, f"Saving to: {local_dir}")

        est_mb = parse_est_mb(info)

        # Actual download (snapshot_download shows tqdm progress in console by default)
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
            # You can add resume_download=True if needed
        )

        actual_mb = folder_size_mb(local_dir)
        append_log(repo_id, f"✅ Download completed! ({actual_mb:.1f} MB)")
        
        st.session_state.download_done[repo_id] = True
        st.session_state.download_error[repo_id] = None
        st.session_state.download_in_progress[repo_id] = False
        st.session_state.download_progress[repo_id] = 1.0

    except Exception as e:
        err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        append_log(repo_id, f"❌ Error: {err_msg}")
        st.session_state.download_done[repo_id] = False
        st.session_state.download_error[repo_id] = str(e)
        st.session_state.download_in_progress[repo_id] = False

def delete_model(repo_id: str, base: Path):
    d = local_dir_for(repo_id, base)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    # Clean session state
    for key in ["download_log", "download_done", "download_error", "download_progress", "download_in_progress"]:
        st.session_state[key].pop(repo_id, None)

def usage_snippet(task: str, local_path: Path) -> str:
    return f"""from transformers import pipeline, AutoTokenizer, AutoModel

# Load from local path (works offline)
pipe = pipeline("{task}", model=r"{local_path}")

# Or manually:
tokenizer = AutoTokenizer.from_pretrained(r"{local_path}")
model = AutoModel.from_pretrained(r"{local_path}")
"""

# ── Main UI ──────────────────────────────────────────────────────────────────
st.title("🤖 ESG & Climate Model Downloader")
st.markdown("Download Hugging Face models for ESG / Climate / Finance analysis. Models are saved locally in your project.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    save_dir_input = st.text_input("Save directory", value=str(DEFAULT_SAVE_DIR))
    save_dir = Path(save_dir_input.strip())
    save_dir.mkdir(parents=True, exist_ok=True)
    st.caption(f"Resolved: `{save_dir.resolve()}`")

    st.divider()
    st.header("💾 Disk Usage")
    total_mb = sum(folder_size_mb(local_dir_for(info["repo_id"], save_dir)) for info in MODELS.values())
    st.metric("Total downloaded", f"{total_mb:.1f} MB")

    st.divider()
    if st.button("⬇️ Download All Models", use_container_width=True):
        for info in MODELS.values():
            rid = info["repo_id"]
            if not is_already_downloaded(rid, save_dir) and not st.session_state.download_in_progress.get(rid, False):
                threading.Thread(
                    target=run_download,
                    args=(rid, save_dir, info),
                    daemon=True
                ).start()
        st.success("Bulk download started in background threads.")

    if st.button("🔄 Refresh All Status", use_container_width=True):
        st.rerun()

    st.divider()
    st.info("💡 Models are also cached by Hugging Face in `~/.cache/huggingface/hub`.")

# CLI tip
with st.expander("🖥️ Quick CLI Alternative"):
    st.code(
        "pip install -U huggingface_hub[cli]\n"
        "huggingface-cli download climatebert/distilroberta-base-climate-s --local-dir ./models/climatebert--distilroberta-base-climate-s",
        language="bash"
    )

st.divider()

# Model Cards
for display_name, info in MODELS.items():
    repo_id = info["repo_id"]
    local_path = local_dir_for(repo_id, save_dir)
    already = is_already_downloaded(repo_id, save_dir)
    in_progress = st.session_state.download_in_progress.get(repo_id, False)
    progress = st.session_state.download_progress.get(repo_id, 0.0)
    error = st.session_state.download_error.get(repo_id)
    log_msgs = st.session_state.download_log.get(repo_id, [])

    status_icon = "✅" if already else ("🔄" if in_progress else "⬜")
    size_label = f"{folder_size_mb(local_path):.1f} MB" if already else info["size"]

    with st.expander(f"{status_icon} {display_name} — {size_label}", expanded=False):
        tab_info, tab_log, tab_usage = st.tabs(["📋 Info", "📜 Download Log", "🐍 Usage"])

        with tab_info:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Repo:** `{repo_id}`")
                st.markdown(f"**Task:** `{info['task']}`")
                st.markdown(f"**Estimated size:** {info['size']}")
                st.markdown(info["description"])
                st.markdown(f"**Local folder:** `{local_path}`")

                if already:
                    st.success(f"Downloaded ({folder_size_mb(local_path):.1f} MB)")
                elif error:
                    st.error(f"Download failed: {error}")
                elif in_progress:
                    st.info("Download in progress...")

            with col2:
                if st.button("⬇️ Download", key=f"dl_{repo_id}", disabled=in_progress, use_container_width=True):
                    threading.Thread(
                        target=run_download,
                        args=(repo_id, save_dir, info),
                        daemon=True
                    ).start()
                    st.toast(f"Download started for {display_name}", icon="⏳")

                if already:
                    if st.button("🗑️ Delete", key=f"del_{repo_id}", use_container_width=True):
                        delete_model(repo_id, save_dir)
                        st.warning(f"Deleted {display_name}")
                        time.sleep(0.5)
                        st.rerun()

                st.link_button("🌐 View on Hugging Face", f"https://huggingface.co/{repo_id}", use_container_width=True)

            # Progress bar
            if in_progress:
                pct = int(progress * 100)
                st.progress(pct, text=f"Downloading... {pct}%")
            elif already:
                st.progress(100, text="Download complete")

        with tab_log:
            if log_msgs:
                st.code("\n".join(log_msgs), language="text")
            else:
                st.info("No logs yet. Start a download to see activity.")

        with tab_usage:
            if already:
                st.code(usage_snippet(info["task"], local_path), language="python")
            else:
                st.warning("Download the model first to use the local path.")
                st.code(usage_snippet(info["task"], local_path), language="python")

st.caption("Tip: Use the **Refresh All Status** button in the sidebar after downloads finish. "
           "Progress is approximate because `snapshot_download` uses internal tqdm bars.")


# import streamlit as st
# from pathlib import Path
# import threading
# import time
# import shutil
# import math
# import re

# st.set_page_config(page_title="Model Downloader", layout="wide")

# # ── constants ────────────────────────────────────────────────────────────────
# DEFAULT_SAVE_DIR = Path(__file__).parents[2] / "models"   # store locally next to benchmarks

# MODELS = {
#     "ClimateBERT — distilroberta-base-climate-s": {
#         "repo_id": "climatebert/distilroberta-base-climate-s",
#         "task":    "fill-mask",
#         "size":    "~82 MB",
#         "est_mb":  82,
#         "description": (
#             "A distilled RoBERTa model fine-tuned on climate-related text. "
#             "Useful for masked language modeling and ClimateBERT-based ESG classification."
#         ),
#     },
#     "ClimateBERT — distilroberta-base-climate-f": {
#         "repo_id": "climatebert/distilroberta-base-climate-f",
#         "task":    "fill-mask",
#         "size":    "~82 MB",
#         "est_mb":  82,
#         "description": (
#             "Fine-tuned variant for climate fact detection tasks."
#         ),
#     },
#     "ClimateBERT — climate-sentiment": {
#         "repo_id": "climatebert/distilroberta-base-climate-sentiment",
#         "task":    "text-classification",
#         "size":    "~82 MB",
#         "est_mb":  82,
#         "description": (
#             "ClimateBERT fine-tuned for climate-related sentiment analysis."
#         ),
#     },
#     "ProsusAI — finbert": {
#         "repo_id": "ProsusAI/finbert",
#         "task":    "text-classification",
#         "size":    "~440 MB",
#         "est_mb":  440,
#         "description": (
#             "BERT fine-tuned on financial news for sentiment analysis. "
#             "Widely used in ESG financial text analysis."
#         ),
#     },
#     "yiyanghkust — finbert-esg": {
#         "repo_id": "yiyanghkust/finbert-esg",
#         "task":    "text-classification",
#         "size":    "~440 MB",
#         "est_mb":  440,
#         "description": (
#             "FinBERT variant fine-tuned specifically for ESG classification tasks."
#         ),
#     },
# }

# # ── session state ─────────────────────────────────────────────────────────────
# if "download_log" not in st.session_state:
#     st.session_state.download_log = {}
# if "download_done" not in st.session_state:
#     st.session_state.download_done = {}
# if "download_error" not in st.session_state:
#     st.session_state.download_error = {}
# if "download_progress" not in st.session_state:
#     st.session_state.download_progress = {}        # repo_id -> float 0..1
# if "download_in_progress" not in st.session_state:
#     st.session_state.download_in_progress = {}    # repo_id -> bool

# # ── helpers ───────────────────────────────────────────────────────────────────
# def local_dir_for(repo_id: str, base: Path) -> Path:
#     slug = repo_id.replace("/", "--")
#     return base / slug

# def is_already_downloaded(repo_id: str, base: Path) -> bool:
#     d = local_dir_for(repo_id, base)
#     return d.exists() and any(d.iterdir())

# def folder_size_mb(path: Path) -> float:
#     if not path.exists():
#         return 0.0
#     try:
#         return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)
#     except Exception:
#         return 0.0

# def append_log(repo_id, msg):
#     if repo_id not in st.session_state.download_log:
#         st.session_state.download_log[repo_id] = []
#     ts = time.strftime("%H:%M:%S")
#     st.session_state.download_log[repo_id].append(f"[{ts}] {msg}")

# def parse_est_mb_from_info(info: dict) -> float:
#     if "est_mb" in info and isinstance(info["est_mb"], (int, float)):
#         return float(info["est_mb"])
#     s = info.get("size", "")
#     m = re.search(r"(\d+)", s)
#     return float(m.group(1)) if m else 100.0

# def monitor_progress(repo_id: str, save_dir: Path, est_mb: float):
#     """Poll local folder size and update download_progress until download_done."""
#     local_dir = local_dir_for(repo_id, save_dir)
#     while True:
#         done = st.session_state.download_done.get(repo_id, False)
#         err = st.session_state.download_error.get(repo_id, None)
#         if done or err:
#             break
#         size_mb = folder_size_mb(local_dir)
#         # Avoid division by zero; cap to 0.99 while in-progress
#         if est_mb > 0:
#             ratio = min(0.99, size_mb / est_mb)
#         else:
#             ratio = 0.0
#         st.session_state.download_progress[repo_id] = ratio
#         time.sleep(0.8)
#     # finalize
#     if st.session_state.download_done.get(repo_id, False):
#         st.session_state.download_progress[repo_id] = 1.0
#     elif st.session_state.download_error.get(repo_id, None):
#         # leave progress as-is or set to 0
#         pass

# def run_download(repo_id: str, save_dir: Path, info: dict):
#     """Run in a background thread so the UI stays responsive."""
#     try:
#         from huggingface_hub import snapshot_download
#         local_dir = local_dir_for(repo_id, save_dir)
#         local_dir.mkdir(parents=True, exist_ok=True)

#         # init state
#         st.session_state.download_log[repo_id] = []
#         st.session_state.download_done[repo_id] = False
#         st.session_state.download_error[repo_id] = None
#         st.session_state.download_in_progress[repo_id] = True
#         st.session_state.download_progress[repo_id] = 0.0

#         append_log(repo_id, f"⏳ Starting download: {repo_id}")
#         append_log(repo_id, f"📁 Saving to: {local_dir}")

#         # start monitor thread
#         est_mb = parse_est_mb_from_info(info)
#         monitor = threading.Thread(target=monitor_progress, args=(repo_id, save_dir, est_mb), daemon=True)
#         monitor.start()

#         # perform download
#         snapshot_download(
#             repo_id=repo_id,
#             local_dir=str(local_dir),
#             local_dir_use_symlinks=False,
#         )

#         mb = folder_size_mb(local_dir)
#         append_log(repo_id, f"✅ Done! {mb:.1f} MB saved to: {local_dir}")
#         st.session_state.download_done[repo_id]  = True
#         st.session_state.download_error[repo_id] = None
#         st.session_state.download_in_progress[repo_id] = False
#         st.session_state.download_progress[repo_id] = 1.0
#     except Exception as e:
#         err = str(e)
#         append_log(repo_id, f"❌ Error: {err}")
#         st.session_state.download_done[repo_id]  = False
#         st.session_state.download_error[repo_id] = err
#         st.session_state.download_in_progress[repo_id] = False

# def delete_model(repo_id: str, base: Path):
#     d = local_dir_for(repo_id, base)
#     if d.exists():
#         shutil.rmtree(d)
#         # reset progress/state
#         st.session_state.download_progress.pop(repo_id, None)
#         st.session_state.download_done.pop(repo_id, None)
#         st.session_state.download_error.pop(repo_id, None)
#         st.session_state.download_in_progress.pop(repo_id, None)
#         st.session_state.download_log.pop(repo_id, None)

# def usage_snippet(task: str, local_path: Path) -> str:
#     return (
#         f"from transformers import pipeline\n\n"
#         f"# Load from local directory (offline-safe)\n"
#         f'pipe = pipeline("{task}", model=r"{local_path}")\n\n'
#         f"# Or using AutoTokenizer + AutoModel\n"
#         f"from transformers import AutoTokenizer, AutoModel\n"
#         f'tokenizer = AutoTokenizer.from_pretrained(r"{local_path}")\n'
#         f'model     = AutoModel.from_pretrained(r"{local_path}")'
#     )

# # ── page ──────────────────────────────────────────────────────────────────────
# st.title("🤖 ESG Model Downloader")
# st.markdown(
#     "Download and manage Hugging Face models for ESG analysis. "
#     "Models are stored **locally inside this project** by default."
# )

# # ── sidebar ───────────────────────────────────────────────────────────────────
# with st.sidebar:
#     st.header("⚙️ Settings")
#     save_dir_input = st.text_input(
#         "Local save directory",
#         value=str(DEFAULT_SAVE_DIR),
#         help="Models will be saved here as sub-folders.",
#     )
#     save_dir = Path(save_dir_input.strip())
#     save_dir.mkdir(parents=True, exist_ok=True)
#     st.caption(f"Resolved path:\n`{save_dir.resolve()}`")

#     st.divider()

#     # ── overall disk usage ────────────────────────────────────────────────────
#     st.header("💾 Disk Usage")
#     total_mb = 0.0
#     for info in MODELS.values():
#         d = local_dir_for(info["repo_id"], save_dir)
#         if d.exists() and any(d.iterdir()):
#             total_mb += folder_size_mb(d)
#     st.metric("Total downloaded", f"{total_mb:.1f} MB")

#     st.divider()
#     st.header("📦 Bulk Actions")
#     if st.button("⬇️ Download all models", use_container_width=True):
#         for info in MODELS.values():
#             rid = info["repo_id"]
#             if not is_already_downloaded(rid, save_dir) and not st.session_state.download_in_progress.get(rid, False):
#                 t = threading.Thread(target=run_download, args=(rid, save_dir, info), daemon=True)
#                 t.start()
#         st.success("Bulk download started in background.")

#     if st.button("🔄 Refresh status", use_container_width=True):
#         st.rerun()

#     st.divider()
#     st.info(
#         "HF also caches to `~/.cache/huggingface/hub/` automatically. "
#         "The directory above is your explicit project-local copy."
#     )

# # ── CLI snippet ───────────────────────────────────────────────────────────────
# with st.expander("🖥️ CLI alternative (no code needed)", expanded=False):
#     st.markdown("Install the Hugging Face CLI and run:")
#     st.code(
#         "pip install -U 'huggingface_hub[cli]'\n"
#         "huggingface-cli download <repo_id> --local-dir ./models/my_model",
#         language="bash",
#     )

# st.divider()

# # ── model cards ───────────────────────────────────────────────────────────────
# for display_name, info in MODELS.items():
#     repo_id  = info["repo_id"]
#     already  = is_already_downloaded(repo_id, save_dir)
#     log_msgs = st.session_state.download_log.get(repo_id, [])
#     done     = st.session_state.download_done.get(repo_id, False)
#     error    = st.session_state.download_error.get(repo_id, None)
#     local_path = local_dir_for(repo_id, save_dir)
#     in_progress = st.session_state.download_in_progress.get(repo_id, False)
#     progress = st.session_state.download_progress.get(repo_id, 0.0)

#     status_icon = "✅" if already else ("🔄" if in_progress else "⬜")
#     disk_label  = f"{folder_size_mb(local_path):.1f} MB on disk" if already else info["size"]

#     with st.expander(f"{status_icon} {display_name}  —  {disk_label}", expanded=False):

#         # ── tabs replace the inner expander (fixes nesting error) ─────────────
#         tab_info, tab_log, tab_usage = st.tabs(["📋 Info", "📜 Download Log", "🐍 Usage Snippet"])

#         with tab_info:
#             col_info, col_action = st.columns([3, 1])

#             with col_info:
#                 st.markdown(f"**Repo ID:** `{repo_id}`")
#                 st.markdown(f"**Task:** `{info['task']}`")
#                 st.markdown(f"**Size:** {info['size']}")
#                 st.markdown(info["description"])
#                 st.markdown(f"**Local path:** `{local_path}`")
#                 if already:
#                     st.success(f"✅ Downloaded ({folder_size_mb(local_path):.1f} MB)")
#                 elif error:
#                     st.error(f"Last download failed: {error}")
#                 elif in_progress:
#                     st.info("Download in progress…")
#                 else:
#                     st.info("Not yet downloaded.")

#             with col_action:
#                 st.markdown(" ")   # spacing

#                 if st.button(
#                     "⬇️ Download" if not in_progress else "⏳ Downloading…",
#                     key=f"dl_{repo_id}",
#                     use_container_width=True,
#                     disabled=in_progress,
#                 ):
#                     # start background download thread
#                     st.session_state.download_log[repo_id]  = []
#                     st.session_state.download_done[repo_id] = False
#                     st.session_state.download_error[repo_id] = None
#                     st.session_state.download_in_progress[repo_id] = True
#                     st.session_state.download_progress[repo_id] = 0.0
#                     t = threading.Thread(target=run_download, args=(repo_id, save_dir, info), daemon=True)
#                     t.start()
#                     # immediate UI update
#                     st.experimental_rerun()

#                 if already:
#                     if st.button("🗑️ Delete", key=f"del_{repo_id}", use_container_width=True):
#                         delete_model(repo_id, save_dir)
#                         st.warning(f"Deleted local copy of {display_name}.")
#                         time.sleep(0.4)
#                         st.experimental_rerun()

#                 st.link_button(
#                     "🌐 HF Hub",
#                     url=f"https://huggingface.co/{repo_id}",
#                     use_container_width=True,
#                 )

#             # show progress UI below action column
#             if in_progress:
#                 pct = int(math.floor(progress * 100))
#                 pct = max(0, min(100, pct))
#                 st.progress(pct)
#                 with st.spinner(f"Downloading {display_name} — {pct}%"):
#                     # small sleep so spinner renders; no blocking of download thread
#                     time.sleep(0.05)
#             elif done:
#                 # ensure progress shows 100% when done
#                 st.progress(100)

#         with tab_log:
#             if log_msgs:
#                 st.code("\n".join(log_msgs), language="text")
#             else:
#                 st.info("No download activity yet for this model.")

#         with tab_usage:
#             if already:
#                 st.code(usage_snippet(info["task"], local_path), language="python")
#             else:
#                 st.warning("Download the model first to see the local path in the snippet.")
#                 st.code(usage_snippet(info["task"], local_path), language="python")

# st.divider()
# st.caption("Tip: Click '🔄 Refresh status' in the sidebar after a download completes to update icons.")