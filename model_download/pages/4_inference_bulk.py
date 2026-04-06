import streamlit as st
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict
import traceback
import json
from datetime import datetime
import time

st.set_page_config(page_title="Local Model Inference — Bulk", layout="wide")

ROOT_MODELS_DIR = Path(__file__).parent.parent / "models"
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

st.title("🔬 Local Model Inference — Bulk")
st.markdown(
    "Run the same inference across multiple locally downloaded Hugging Face models. "
    "Select one or more valid model folders (containing config.json / model weights)."
)

# ---- helpers ----
def looks_like_model_dir(p: Path) -> bool:
    return any((p / fn).exists() for fn in ("config.json", "pytorch_model.bin", "model.safetensors"))

def find_all_model_dirs(root: Path) -> List[Path]:
    if not root.exists():
        return []
    found = set()
    for child in root.iterdir():
        if child.is_dir() and looks_like_model_dir(child):
            found.add(child.resolve())
    for p in root.rglob("*"):
        if p.is_dir() and looks_like_model_dir(p):
            found.add(p.resolve())
    return sorted(found)

@st.cache_resource(show_spinner=False)
def load_pipeline_safe(task: str, local_path: str) -> Tuple[Optional[object], Optional[str]]:
    try:
        from transformers import pipeline
        pipe = pipeline(task, model=local_path, tokenizer=local_path)
        return pipe, None
    except Exception as e:
        return None, str(e)

@st.cache_resource(show_spinner=False)
def load_tokenizer_safe(local_path: str):
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(local_path, use_fast=True)
        return tok, None
    except Exception as e:
        return None, str(e)

# ---- discover models ----
candidates = find_all_model_dirs(ROOT_MODELS_DIR)
if not candidates:
    st.warning(f"No valid model folders found under `{ROOT_MODELS_DIR}`. Use the downloader to snapshot_download repos.")
    st.stop()

labels = [str(p.relative_to(ROOT_MODELS_DIR)) for p in candidates]
selected_labels = st.multiselect("Select one or more model folders", labels, default=[labels[0]])
selected_paths = [candidates[labels.index(lbl)] for lbl in selected_labels]

st.markdown("**Selected folders:**")
for p in selected_paths:
    st.markdown(f"- `{p}`")

# ---- task & input ----
task = st.selectbox("Task", ["fill-mask", "text-classification"])
st.subheader("Input")
default_example = "The company's sustainability claim was <mask> about emissions." if task == "fill-mask" else "The company's sustainability report shows strong governance and low climate risk."
input_text = st.text_area("Input text (same input will be used for all selected models)", value=default_example, height=140)
top_k = st.number_input("Top K (for fill-mask)", value=5, min_value=1, max_value=20, step=1) if task == "fill-mask" else None

st.divider()
col1, col2 = st.columns([1,3])
with col1:
    run_button = st.button("Run bulk inference")
with col2:
    st.info(f"Will run across {len(selected_paths)} model(s). Results saved to `{RESULTS_DIR}` after completion.")

# ---- run bulk inference ----
if run_button:
    if not selected_paths:
        st.error("No models selected.")
    else:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        combined_results: Dict[str, Any] = {
            "timestamp": timestamp,
            "task": task,
            "input_text": input_text,
            "params": {"top_k": int(top_k) if top_k is not None else None},
            "models": []
        }

        overall_progress = st.progress(0)
        num_models = len(selected_paths)
        for idx, model_path in enumerate(selected_paths, start=1):
            model_entry: Dict[str, Any] = {
                "model_label": str(model_path.relative_to(ROOT_MODELS_DIR)),
                "resolved_path": str(model_path),
                "started_at": datetime.utcnow().isoformat() + "Z",
                "success": False,
                "error": None,
                "results": None,
            }

            with st.container():
                st.markdown(f"### [{idx}/{num_models}] `{model_entry['model_label']}`")
                st.markdown(f"Path: `{model_entry['resolved_path']}`")

                # try tokenizer detection
                tok, tok_err = load_tokenizer_safe(str(model_path))
                mask_token = getattr(tok, "mask_token", None) if tok else None
                if task == "fill-mask" and mask_token:
                    inp = input_text if mask_token in input_text else (input_text + f" {mask_token}")
                else:
                    inp = input_text

                # load pipeline
                with st.spinner(f"Loading pipeline for {model_entry['model_label']}..."):
                    pipe, load_err = load_pipeline_safe(task, str(model_path))
                    if load_err:
                        model_entry["error"] = load_err
                        st.error("Failed to load pipeline:")
                        st.code(load_err)
                    else:
                        # run inference
                        try:
                            with st.spinner("Running inference..."):
                                if task == "fill-mask":
                                    res = pipe(inp, top_k=int(top_k))
                                else:
                                    res = pipe(inp)
                                model_entry["results"] = res
                                model_entry["success"] = True
                                st.success("Inference completed")
                                # brief display
                                st.write(res if isinstance(res, list) and len(res) < 10 else f"Returned {len(res)} items")
                        except Exception as e:
                            model_entry["error"] = str(e)
                            st.error("Inference failed:")
                            st.code(str(e))

            model_entry["finished_at"] = datetime.utcnow().isoformat() + "Z"
            combined_results["models"].append(model_entry)

            # save per-model JSON
            try:
                per_fname = f"{timestamp}-{model_entry['model_label'].replace('/', '_')}-{task}.json"
                per_path = RESULTS_DIR / per_fname
                with per_path.open("w", encoding="utf8") as f:
                    json.dump(model_entry, f, ensure_ascii=False, indent=2)
                st.markdown(f"Saved per-model results → `{per_path}`")
                st.download_button(f"Download per-model JSON ({model_entry['model_label']})", data=per_path.read_bytes(), file_name=per_fname, mime="application/json")
            except Exception as e:
                st.error(f"Failed to save per-model JSON: {e}")

            # update overall progress
            overall_progress.progress(int((idx / num_models) * 100))
            # small sleep so UI updates smoothly
            time.sleep(0.2)

        # save combined JSON
        try:
            combined_fname = f"{timestamp}-bulk-{task}.json"
            combined_path = RESULTS_DIR / combined_fname
            with combined_path.open("w", encoding="utf8") as f:
                json.dump(combined_results, f, ensure_ascii=False, indent=2)
            st.success(f"Saved combined results → `{combined_path}`")
            st.download_button("Download combined JSON", data=combined_path.read_bytes(), file_name=combined_fname, mime="application/json")
        except Exception as e:
            st.error(f"Failed to save combined JSON: {e}")

st.divider()
st.caption("Bulk inference saves per-model and combined JSON files under the `results` folder. Use the downloader page to get full HF repo snapshots (config.json + weights) if needed.")