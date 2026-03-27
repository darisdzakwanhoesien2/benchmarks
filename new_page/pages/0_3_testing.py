import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any

import streamlit as st

# ───────────────────────────────────────────────────────────────
# OPTIONAL: ClimateBERT (safe import)
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
DATA_PATH = ROOT / "results" / "example.json"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ───────────────────────────────────────────────────────────────
# STREAMLIT CONFIG
# ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ESG T1 + T2 Pipeline", layout="wide")
st.title("🌿 ESG Pipeline (T1 + T2 only)")
st.caption("Using example.json as input (no OCR)")

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


# 🔥 NEW: JSONL STREAM WRITER
class JSONLWriter:
    def __init__(self, path: Path):
        self.path = path
        self.f = open(path, "a", encoding="utf-8")

    def write(self, record: dict):
        line = json.dumps(serialize(record), ensure_ascii=False)
        self.f.write(line + "\n")
        self.f.flush()  # ✅ immediate save

    def close(self):
        self.f.close()


# ───────────────────────────────────────────────────────────────
# LOAD DATA
# ───────────────────────────────────────────────────────────────
if not DATA_PATH.exists():
    st.error(f"❌ Missing example.json at {DATA_PATH}")
    st.stop()

data = json.loads(DATA_PATH.read_text())
st.success(f"✅ Loaded {len(data)} records from example.json")

with st.expander("📄 Preview Data"):
    st.json(data[:3])

# ───────────────────────────────────────────────────────────────
# ROBUST TEXT EXTRACTION
# ───────────────────────────────────────────────────────────────
texts = []
missing_text_count = 0

for i, d in enumerate(data):
    if isinstance(d, dict):

        if d.get("text"):
            lbl = d.get("label") or d.get("target") or f"row_{i}"
            texts.append({"label": lbl, "text": str(d["text"]).strip()})
            continue

        if isinstance(d.get("records"), list):
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

        if d.get("raw_output"):
            try:
                parsed = json.loads(d["raw_output"])
                if isinstance(parsed, list):
                    for j, rec in enumerate(parsed):
                        if isinstance(rec, dict) and rec.get("text"):
                            base_label = d.get("target") or f"row_{i}"
                            texts.append({
                                "label": f"{base_label}/raw_{j+1}",
                                "text": str(rec["text"]).strip()
                            })
                        else:
                            missing_text_count += 1
                    continue
            except:
                pass

        missing_text_count += 1

    elif isinstance(d, str) and d.strip():
        texts.append({"label": f"row_{i}", "text": d.strip()})
    else:
        missing_text_count += 1

if not texts:
    st.error("❌ No usable text found")
    st.stop()

if missing_text_count:
    st.warning(f"⚠️ Skipped {missing_text_count} items")

# ───────────────────────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    run_t1 = st.checkbox("Run T1 (ClimateBERT)", True)
    run_t2 = st.checkbox("Run T2 (ABSA)", True)

    save_t1 = st.checkbox("Save T1", True)
    save_t2 = st.checkbox("Save T2", True)

    run_deep = st.checkbox("Run Deep Model (slow)", False)

# ───────────────────────────────────────────────────────────────
# RUN PIPELINE
# ───────────────────────────────────────────────────────────────
if st.button("🚀 Run Pipeline", use_container_width=True):

    # 🔥 INIT STREAM WRITERS
    t1_writer = JSONLWriter(RESULTS_DIR / "t1_results.jsonl") if save_t1 else None
    t2_writer = JSONLWriter(RESULTS_DIR / "t2_results.jsonl") if save_t2 else None

    # ============================================================
    # T1 — CLIMATEBERT
    # ============================================================
    if run_t1:
        st.subheader("📊 T1 · ClimateBERT")

        if ClimateBERTClient is None:
            st.error("ClimateBERT not available")
        else:
            api = ClimateBERTClient()
            models = getattr(api, "available_models", [])

            progress = st.progress(0)
            total = len(texts) * max(len(models), 1)
            step = 0

            for item in texts:
                for m in models:
                    try:
                        res = api.predict(item["text"], model_key=m)
                    except Exception as e:
                        res = {"error": str(e)}

                    record = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "label": item["label"],
                        "model": m,
                        "text": item["text"],
                        "result": res,
                    }

                    if t1_writer:
                        t1_writer.write(record)

                    st.write(f"{item['label']} × {m} ✅")

                    step += 1
                    progress.progress(step / total)

            st.success("T1 done")

    # ============================================================
    # T2 — ABSA
    # ============================================================
    if run_t2:
        st.subheader("🧠 T2 · ABSA")

        try:
            from code.rule_based import collect_aspects, polarity_basic, tone_basic
            from code.hybrid_model import run_hierarchical_hybrid
        except Exception as e:
            st.error(f"Import error: {e}")
            st.stop()

        progress = st.progress(0)

        for i, item in enumerate(texts):
            st.markdown(f"### 📄 {item['label']}")
            text = item["text"]

            # RULE BASED
            try:
                rb = {
                    "aspects": collect_aspects(text),
                    "polarity": polarity_basic(text),
                    "tone": tone_basic(text),
                }
                st.write("Rule-based:", rb)
            except Exception as e:
                rb = {"error": str(e)}

            # HYBRID
            try:
                _, df, _, _, _, metrics = run_hierarchical_hybrid(text)
                hybrid = {
                    "predictions": df.to_dict("records"),
                    "metrics": metrics.to_dict("records"),
                }
                st.dataframe(df)
            except Exception as e:
                hybrid = {"error": str(e)}

            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "label": item["label"],
                "text": text,
                "rule_based": rb,
                "hybrid": hybrid,
            }

            if t2_writer:
                t2_writer.write(record)

            progress.progress((i + 1) / len(texts))

        st.success("T2 done")

    # 🔥 CLOSE WRITERS
    if t1_writer:
        t1_writer.close()
    if t2_writer:
        t2_writer.close()

    st.success("🎉 Pipeline finished")