import streamlit as st
from pathlib import Path
from typing import List, Optional, Tuple
import traceback
import json
from datetime import datetime

st.set_page_config(page_title="Local Model Inference", layout="wide")

ROOT_MODELS_DIR = Path(__file__).parent.parent / "models"

# after the declaration of ROOT_MODELS_DIR and before UI, ensure results dir exists
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

st.title("🔬 Local Model Inference")
st.markdown(
    "Run inference with locally downloaded Hugging Face models saved under benchmarks/models. "
    "This page now auto-discovers folders that actually contain model files (config.json / pytorch_model.bin / model.safetensors)."
)

def looks_like_model_dir(p: Path) -> bool:
    return any((p / fn).exists() for fn in ("config.json", "pytorch_model.bin", "model.safetensors"))

def find_all_model_dirs(root: Path) -> List[Path]:
    """Return a sorted list of directories (under root) that contain HF model files."""
    if not root.exists():
        return []
    found = set()
    # include top-level if it looks like a model folder
    for child in root.iterdir():
        if child.is_dir() and looks_like_model_dir(child):
            found.add(child.resolve())
    # depth-first search for nested model dirs
    for p in root.rglob("*"):
        if p.is_dir() and looks_like_model_dir(p):
            found.add(p.resolve())
    # sort by path for stable order
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

# Discover candidate model folders
candidates = find_all_model_dirs(ROOT_MODELS_DIR)
if not candidates:
    st.warning(f"No valid model folders found under `{ROOT_MODELS_DIR}`. Make sure each model folder contains config.json and model weights.")
    st.stop()

# Build readable labels and allow manual override
labels = [str(p.relative_to(ROOT_MODELS_DIR)) for p in candidates]
selected_label = st.selectbox("Select model folder (detected valid model directories)", labels)
selected_resolved = candidates[labels.index(selected_label)]
st.markdown(f"**Resolved model folder:** `{selected_resolved}`")

# Show detected files
files = sorted([p.name for p in selected_resolved.iterdir() if p.is_file()])
st.markdown("**Files in resolved folder:**")
st.write(files)

# Try load tokenizer to detect mask token
tok, tok_err = load_tokenizer_safe(str(selected_resolved))
mask_token = getattr(tok, "mask_token", None) if tok else None

# Task and input
st.subheader("Task and Input")
task = st.selectbox("Task", ["fill-mask", "text-classification"])
if task == "fill-mask" and not mask_token:
    st.warning("Tokenizer has no mask token configured — fill-mask may fail.")

if task == "fill-mask":
    default_text = f"The company's sustainability claim was {mask_token} about emissions." if mask_token else "The company's sustainability claim was <mask> about emissions."
else:
    default_text = "The company's sustainability report shows strong governance and low climate risk."

input_text = st.text_area("Input text", value=default_text, height=140)
top_k = st.number_input("Top K (for fill-mask)", value=5, min_value=1, max_value=20, step=1) if task == "fill-mask" else None

st.divider()
run_button = st.button("Run inference")
if run_button:
    if not selected_resolved.exists():
        st.error("Selected folder does not exist. Choose another folder or re-download the model.")
    else:
        with st.spinner("Loading model and running inference..."):
            try:
                pipe, load_err = load_pipeline_safe(task, str(selected_resolved))
                if load_err:
                    st.error("Failed to load pipeline for task. See details below.")
                    st.code(load_err)
                    st.info("Ensure the selected folder contains a full HF repo snapshot (config.json and weights). Use the downloader page to snapshot_download the repo if needed.")
                else:
                    if task == "fill-mask":
                        # ensure mask token placeholder present
                        if (tok and tok.mask_token) and (tok.mask_token not in input_text):
                            st.info(f"Inserted mask token `{tok.mask_token}` automatically.")
                            input_text = input_text + f" {tok.mask_token}"
                        results = pipe(input_text, top_k=int(top_k))
                        st.success("Inference completed")
                        st.subheader("Results")
                        for i, r in enumerate(results):
                            if isinstance(r, dict):
                                score = r.get("score") or r.get("probability", None)
                                token_str = r.get("token_str") or r.get("token", "")
                                sequence = r.get("sequence") or ""
                                st.markdown(f"{i+1}. **{token_str.strip()}** — score: {score:.4f}")
                                st.caption(sequence)
                            else:
                                st.write(r)
                    else:  # text-classification
                        results = pipe(input_text)
                        st.success("Inference completed")
                        st.subheader("Results")
                        # pipeline returns list of dicts
                        if isinstance(results, list):
                            for r in results:
                                label = r.get("label", r.get("entity_group", "LABEL"))
                                score = r.get("score", None)
                                st.markdown(f"**{label}** — {score:.4f}" if score else f"**{label}**")
                        else:
                            st.write(results)

                    # ---- Save results to JSON and offer download ----
                    try:
                        out = {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "resolved_folder": str(selected_resolved),
                            "task": task,
                            "input_text": input_text,
                            "params": {"top_k": int(top_k) if top_k is not None else None},
                            "results": results,
                        }
                        fname = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{selected_resolved.name}-{task}.json"
                        out_path = RESULTS_DIR / fname
                        with out_path.open("w", encoding="utf8") as f:
                            json.dump(out, f, ensure_ascii=False, indent=2)
                        st.success(f"Saved inference results → `{out_path}`")
                        # provide download button
                        with out_path.open("rb") as f:
                            st.download_button("Download results (JSON)", data=f, file_name=fname, mime="application/json")
                    except Exception as e:
                        st.error(f"Failed to save results: {e}")
            except Exception:
                st.error("Inference failed. See traceback:")
                st.code(traceback.format_exc())

st.divider()
st.caption("If a repo folder (e.g. climatebert--distilroberta-base-climate-f) does not contain model files, re-run snapshot_download for that repo or point to the valid nested folder (this page auto-discovers nested model folders).")