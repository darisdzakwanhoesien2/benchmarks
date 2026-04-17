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

def merge_existing_per_model_jsons(results_dir: Path, output_name: str = None) -> Optional[Path]:
    """
    Read JSON files in results_dir that look like per-model results and combine into one JSON.
    Returns path to combined JSON or None on failure/none found.
    """
    files = sorted(results_dir.glob("*.json"))
    per_model_files = []
    for f in files:
        try:
            payload = json.loads(f.read_text(encoding="utf8"))
        except Exception:
            continue
        # heuristic: per-model results contain keys like 'model_label' or 'resolved_path'
        if isinstance(payload, dict) and ("model_label" in payload or ("models" in payload and isinstance(payload.get("models"), list))):
            # if payload already a combined bulk, skip
            if payload.get("task") and payload.get("models"):
                # treat as combined -> include its models
                per_model_files.extend(payload.get("models", []))
            elif "model_label" in payload:
                per_model_files.append(payload)
    if not per_model_files:
        return None
    combined = {
        "merged_at": datetime.utcnow().isoformat() + "Z",
        "source_files": [str(f.name) for f in files],
        "models": per_model_files
    }
    if output_name is None:
        output_name = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-merged-results.json"
    out_path = results_dir / output_name
    out_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf8")
    return out_path

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
    st.info(f"Will run across {len(selected_paths)} model(s). A single combined JSON will be saved to `{RESULTS_DIR}` after completion.")

# ---- run bulk inference (save only one combined JSON) ----
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
                                st.write(res if isinstance(res, list) and len(res) < 10 else f"Returned {len(res)} items")
                        except Exception as e:
                            model_entry["error"] = str(e)
                            st.error("Inference failed:")
                            st.code(str(e))

            model_entry["finished_at"] = datetime.utcnow().isoformat() + "Z"
            combined_results["models"].append(model_entry)

            # update overall progress
            overall_progress.progress(int((idx / num_models) * 100))
            time.sleep(0.2)

        # save single combined JSON only
        try:
            combined_fname = f"{timestamp}-bulk-{task}-combined.json"
            combined_path = RESULTS_DIR / combined_fname
            with combined_path.open("w", encoding="utf8") as f:
                json.dump(combined_results, f, ensure_ascii=False, indent=2)
            st.success(f"Saved combined results → `{combined_path}`")
            st.download_button("Download combined JSON", data=combined_path.read_bytes(), file_name=combined_fname, mime="application/json")
        except Exception as e:
            st.error(f"Failed to save combined JSON: {e}")

st.divider()

# ---- utility: merge existing per-model JSONs into one combined JSON ----
with st.expander("Merge existing per-model JSONs into a single combined JSON", expanded=False):
    st.markdown("This will scan the results folder for JSON files that look like per-model outputs and merge them into a single JSON.")
    if st.button("Merge now"):
        merged = merge_existing_per_model_jsons(RESULTS_DIR)
        if merged:
            st.success(f"Merged results saved → `{merged}`")
            st.download_button("Download merged JSON", data=merged.read_bytes(), file_name=merged.name, mime="application/json")
        else:
            st.info("No suitable per-model JSON files found to merge.")

st.caption("Bulk inference saves a single combined JSON file. Use the merge utility to combine older per-model JSON files if needed.")