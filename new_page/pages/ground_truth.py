import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Set, Tuple, List, Dict, Optional
import time
import traceback
import sys

import streamlit as st

# ───────────────────────────────────────────────────────────────
# OPTIONAL: ClimateBERT
# ───────────────────────────────────────────────────────────────
ClimateBERTClient = None
_climatebert_error = ""

try:
    from api.climatebert_client import ClimateBERTClient as _CB
    ClimateBERTClient = _CB
except Exception as e:
    _climatebert_error = str(e)

# ───────────────────────────────────────────────────────────────
# PATHS
# ───────────────────────────────────────────────────────────────
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "code"))
DATA_PATH = ROOT / "results" / "esg_records.json"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

T1_FILE = RESULTS_DIR / "t1_results.jsonl"
T2_FILE = RESULTS_DIR / "t2_results.jsonl"

from graph_attachment_gallery import render_attachment_cards  # noqa: E402

# ───────────────────────────────────────────────────────────────
# MODEL CACHE / FALLBACK
# ───────────────────────────────────────────────────────────────
MODELS_CACHE_PATH = Path(__file__).parent / "models_cache.json"
_cached_models: List[str] = []
if MODELS_CACHE_PATH.exists():
    try:
        _cached_models = json.loads(MODELS_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        _cached_models = []

# ───────────────────────────────────────────────────────────────
# STREAMLIT CONFIG
# ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ESG Pipeline", layout="wide")
st.title("🌿 ESG Pipeline (Resumable)")
st.caption("Now supports resume from cutoff 🚀")

with st.expander("📊 Visualize existing ground_truth.py outputs", expanded=False):
    st.caption("Graph-card view of saved T1/T2 outputs with original graph attachments and backing tables.")
    render_attachment_cards(
        "ground_truth.py Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        rq_default="RQ2",
        figures=["A.22", "A.23", "A.24", "A.25", "A.26", "A.27", "A.28", "A.29"],
        show_filters=False,
    )

if _climatebert_error:
    st.warning(f"⚠️ ClimateBERT not available: {_climatebert_error}")

# ───────────────────────────────────────────────────────────────
# HELPERS
# ───────────────────────────────────────────────────────────────
def serialize(obj):
    try:
        import numpy as np
        import torch
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, torch.Tensor):
            return obj.detach().cpu().numpy().tolist()
    except:
        pass

    if isinstance(obj, (list, tuple)):
        return [serialize(o) for o in obj]
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj


class JSONLWriter:
    def __init__(self, path: Path):
        self.f = open(path, "a", encoding="utf-8")

    def write(self, record: dict):
        self.f.write(json.dumps(serialize(record), ensure_ascii=False) + "\n")
        self.f.flush()

    def close(self):
        self.f.close()


# 🔥 LOAD PROCESSED KEYS (RESUME CORE)
def load_processed_t1(path: Path) -> Set[Tuple[str, str]]:
    done = set()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    done.add((d.get("label"), d.get("model")))
                except:
                    pass
    return done


def load_processed_t2(path: Path) -> Set[str]:
    done = set()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    done.add(d.get("label"))
                except:
                    pass
    return done


# ───────────────────────────────────────────────────────────────
# LOCAL MODEL HELPERS (reuse bulk inference patterns)
# ───────────────────────────────────────────────────────────────

# Fix: point to the actual model_download/models directory
ROOT_MODELS_DIR = Path(__file__).parents[2] / "model_download" / "models"

def looks_like_model_dir(p: Path) -> bool:
    return any((p / fn).exists() for fn in ("config.json", "pytorch_model.bin", "model.safetensors"))

def find_all_model_dirs(root: Path) -> List[Path]:
    """
    Recursively find directories that contain HF model files.
    Returns the directory that *directly* contains config.json / weights.
    """
    if not root.exists():
        return []
    found = set()
    # primary: find by config.json presence (most reliable)
    for f in root.rglob("config.json"):
        if f.is_file():
            found.add(f.parent.resolve())
    # secondary: find by weight files if no config found
    for name in ("pytorch_model.bin", "model.safetensors", "tf_model.h5"):
        for f in root.rglob(name):
            if f.is_file():
                found.add(f.parent.resolve())
    return sorted(found)

@st.cache_resource(show_spinner=False)
def load_pipeline_safe(task: str, local_path: str):
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


# ───────────────────────────────────────────────────────────────
# LOAD DATA
# ───────────────────────────────────────────────────────────────
if not DATA_PATH.exists():
    st.error("❌ Missing example.json")
    st.stop()

data = json.loads(DATA_PATH.read_text())
st.success(f"✅ Loaded {len(data)} records")

# ───────────────────────────────────────────────────────────────
# TEXT EXTRACTION (robust)
# ───────────────────────────────────────────────────────────────
texts = []
missing_text_count = 0

for i, d in enumerate(data):
    if isinstance(d, dict):
        # top-level "text"
        if d.get("text"):
            texts.append({
                "label": d.get("label", d.get("target", f"row_{i}")),
                "text": str(d["text"]).strip()
            })
            continue

        # nested "records" (e.g. esg_records-like entries)
        if isinstance(d.get("records"), list) and d["records"]:
            base_label = d.get("target") or d.get("label") or f"row_{i}"
            for j, rec in enumerate(d["records"]):
                if isinstance(rec, dict) and rec.get("text"):
                    texts.append({
                        "label": f"{base_label}/rec_{j+1}",
                        "text": str(rec["text"]).strip()
                    })
                else:
                    missing_text_count += 1
            continue

        # try to parse raw_output (stringified JSON array)
        if d.get("raw_output"):
            try:
                parsed = json.loads(d["raw_output"])
                if isinstance(parsed, list):
                    base_label = d.get("target") or d.get("label") or f"row_{i}"
                    for j, rec in enumerate(parsed):
                        if isinstance(rec, dict) and rec.get("text"):
                            texts.append({
                                "label": f"{base_label}/raw_{j+1}",
                                "text": str(rec["text"]).strip()
                            })
                        else:
                            missing_text_count += 1
                    continue
            except Exception:
                # ignore parse errors, fallthrough to count as missing
                pass

        # nothing usable in this dict entry
        missing_text_count += 1

    elif isinstance(d, str) and d.strip():
        texts.append({"label": f"row_{i}", "text": d.strip()})
    else:
        missing_text_count += 1

if not texts:
    st.error("❌ No valid text")
    st.stop()

if missing_text_count:
    st.warning(f"⚠️ Skipped {missing_text_count} item(s) without usable 'text'")

# preview loaded texts
with st.expander("📄 Preview extracted texts"):
    st.json(texts[:10])


# ───────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    run_t1 = st.checkbox("Run T1", True)
    run_t2 = st.checkbox("Run T2", True)

    resume_mode = st.checkbox("Resume from previous run", True)

    # T1 backend selection
    t1_backend = st.radio("T1 backend", ("ClimateBERT API", "Local models"), index=0)

    # --- ClimateBERT API models ---
    connected = ClimateBERTClient is not None and not _climatebert_error
    available_models: List[str] = []
    if connected:
        try:
            _api_tmp = ClimateBERTClient()
            available_models = getattr(_api_tmp, "available_models", []) or []
        except Exception:
            available_models = []

    model_options = available_models or _cached_models or []
    free_candidates = [m for m in model_options if (":free" in m) or ("free" in m.lower())]
    default_model_selection = free_candidates if free_candidates else (model_options[:6] if model_options else [])

    if t1_backend == "ClimateBERT API":
        selected_models = st.multiselect(
            "ClimateBERT Model(s)",
            options=model_options,
            default=default_model_selection,
        )
        selected_local: List[str] = []
    else:
        selected_models = []
        # Local model discovery
        local_candidates = find_all_model_dirs(ROOT_MODELS_DIR)
        local_map = {str(p.relative_to(ROOT_MODELS_DIR)): p for p in local_candidates}
        local_labels = sorted(local_map.keys())

        # Debug expander so you can see exactly what was found
        with st.expander("🔍 Debug: discovered local model folders", expanded=not bool(local_labels)):
            st.markdown(f"**Scanning:** `{ROOT_MODELS_DIR}`")
            st.markdown(f"**Exists:** `{ROOT_MODELS_DIR.exists()}`")
            if local_labels:
                for lbl in local_labels:
                    st.markdown(f"- `{lbl}`")
            else:
                st.warning("No model dirs found. Check that ROOT_MODELS_DIR is correct.")
                # show what IS in the directory tree for diagnosis
                if ROOT_MODELS_DIR.exists():
                    all_dirs = [str(p.relative_to(ROOT_MODELS_DIR)) for p in ROOT_MODELS_DIR.rglob("*") if p.is_dir()]
                    st.write("All sub-directories found:", all_dirs[:30])
                    all_files = [str(p.relative_to(ROOT_MODELS_DIR)) for p in ROOT_MODELS_DIR.rglob("*") if p.is_file()]
                    st.write("All files found:", all_files[:30])

        selected_local = st.multiselect(
            "Local model folders (for T1 — text-classification)",
            options=local_labels,
            default=local_labels[:1] if local_labels else [],
            help="Folders are discovered from model_download/models/. Each must contain config.json.",
        )

    # --- Prompt templates ---
    PROMPT_TEMPLATES = [
        "tone_chain_of_thought_english",
        "tone_chain_of_thought_indonesian",
        "tone_few_shot_indonesian",
        "tone_few_shot_english",
        "tone_zero_shot_indonesian",
        "tone_zero_shot_english",
    ]
    selected_prompts = st.multiselect(
        "Prompt templates",
        options=PROMPT_TEMPLATES,
        default=PROMPT_TEMPLATES,
    )

# ───────────────────────────────────────────────────────────────
# RUN
# ───────────────────────────────────────────────────────────────
if st.button("🚀 Run Pipeline"):

    # 🔥 LOAD CHECKPOINTS
    done_t1 = load_processed_t1(T1_FILE) if resume_mode else set()
    done_t2 = load_processed_t2(T2_FILE) if resume_mode else set()

    st.info(f"T1 already done: {len(done_t1)}")
    st.info(f"T2 already done: {len(done_t2)}")

    t1_writer = JSONLWriter(T1_FILE)
    t2_writer = JSONLWriter(T2_FILE)

    # ============================================================
    # T1
    # ============================================================
    if run_t1:
        st.subheader("📊 T1")

        if t1_backend == "ClimateBERT API":
            if ClimateBERTClient is None:
                st.error("ClimateBERT client missing")
                target_models = []
            else:
                api = ClimateBERTClient()
                client_models = getattr(api, "available_models", []) or []
                target_models = selected_models if selected_models else client_models
            local_map = {}
        else:
            # rebuild local_map inside run block (sidebar may have re-run)
            local_candidates = find_all_model_dirs(ROOT_MODELS_DIR)
            local_map = {str(p.relative_to(ROOT_MODELS_DIR)): p for p in local_candidates}
            target_models = selected_local

        if not target_models:
            st.warning("No models selected for T1.")
        else:
            total_tasks = len(texts) * len(target_models)
            progress = st.progress(0)
            step = 0
            timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            run_records: List[Dict[str, Any]] = []

            for item in texts:
                for m in target_models:
                    key = (item["label"], m)

                    if t1_backend == "ClimateBERT API" and key in done_t1:
                        step += 1
                        progress.progress(step / total_tasks)
                        continue

                    if t1_backend == "ClimateBERT API":
                        try:
                            res = api.predict(item["text"], model_key=m)
                            success, error = True, None
                        except Exception as e:
                            res = {"error": str(e)}
                            success, error = False, str(e)
                    else:
                        model_path = local_map.get(m)
                        if model_path is None:
                            res = {"error": f"Path not found for label: {m}"}
                            success, error = False, res["error"]
                        else:
                            pipe, load_err = load_pipeline_safe("text-classification", str(model_path))
                            if load_err:
                                res = {"error": load_err}
                                success, error = False, load_err
                            else:
                                try:
                                    out = pipe(item["text"])
                                    res = out
                                    success, error = True, None
                                except Exception as e:
                                    res = {"error": str(e)}
                                    success, error = False, str(e)

                    record = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "label": item["label"],
                        "model": m,
                        "text": item["text"],
                        "result": res,
                        "success": success,
                        "error": error,
                        "backend": t1_backend,
                    }
                    try:
                        t1_writer.write(record)
                    except Exception as e:
                        st.error(f"Failed to write T1 record: {e}")

                    run_records.append(record)
                    st.write(f"✅ {item['label']} × {m}" if success else f"❌ {item['label']} × {m} — {error}")

                    step += 1
                    progress.progress(step / total_tasks)

            st.success("T1 run completed")

            try:
                combined_obj = {
                    "run_id": timestamp,
                    "run_at": datetime.utcnow().isoformat() + "Z",
                    "num_records": len(run_records),
                    "backend": t1_backend,
                    "models": target_models,
                    "records": run_records,
                }
                combined_fname = f"t1_run_{timestamp}.json"
                combined_path = RESULTS_DIR / combined_fname
                combined_path.write_text(json.dumps(combined_obj, ensure_ascii=False, indent=2), encoding="utf8")
                st.success(f"Saved combined T1 JSON → `{combined_path}`")
                st.download_button("Download T1 combined JSON", data=combined_path.read_bytes(), file_name=combined_fname, mime="application/json")
            except Exception as e:
                st.error(f"Failed to save combined T1 JSON: {e}")

    # ============================================================
    # T2
    # ============================================================
    if run_t2:
        st.subheader("🧠 T2")

        from code.rule_based import collect_aspects, polarity_basic, tone_basic
        from code.hybrid_model import run_hierarchical_hybrid

        progress = st.progress(0)

        for i, item in enumerate(texts):

            key = item["label"]

            # 🔥 SKIP IF DONE
            if key in done_t2:
                progress.progress((i + 1) / len(texts))
                continue

            text = item["text"]

            rb = {
                "aspects": collect_aspects(text),
                "polarity": polarity_basic(text),
                "tone": tone_basic(text),
            }

            try:
                _, df, _, _, _, metrics = run_hierarchical_hybrid(text)
                hybrid = {
                    "predictions": df.to_dict("records"),
                    "metrics": metrics.to_dict("records"),
                }
            except Exception as e:
                hybrid = {"error": str(e)}

            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "label": item["label"],
                "text": text,
                "rule_based": rb,
                "hybrid": hybrid,
            }

            t2_writer.write(record)

            progress.progress((i + 1) / len(texts))

        st.success("T2 done")

    t1_writer.close()
    t2_writer.close()

    st.success("🎉 Finished (Resumable)")
