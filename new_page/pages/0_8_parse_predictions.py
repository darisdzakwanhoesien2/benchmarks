import json
import re
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import streamlit as st

# ---------- parser (copied/adapted) ----------
def _is_number_like(v) -> bool:
    try:
        float(v)
        return True
    except Exception:
        return False

def parse_prediction_str(s: str) -> Dict[str, Any]:
    """Parse prediction strings like:
       - 'Label: 1.00'
       - 'Label\\n1.00'
       - 'Predictions for ...:\\nLabel: 1.00'
       - JSON arrays/dicts
    Returns structured dict: {'labels_scores': {...}, 'top_label': ..., 'top_score': ...} or {'raw': s}.
    """
    if not s or not str(s).strip():
        return {"raw": ""}
    s = str(s).strip()

    # Try JSON first
    try:
        j = json.loads(s)
        if isinstance(j, dict):
            out = {k: float(v) for k, v in j.items() if _is_number_like(v)}
            if out:
                top = max(out.items(), key=lambda x: x[1])
                return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}
            return {"raw_json": j}
        if isinstance(j, list):
            out = {}
            for item in j:
                if isinstance(item, dict):
                    label = item.get("label") or item.get("text") or item.get("aspect")
                    score = item.get("score") or item.get("sentiment_score") or item.get("prob") or item.get("confidence")
                    if label and _is_number_like(score):
                        out[str(label)] = float(score)
            if out:
                top = max(out.items(), key=lambda x: x[1])
                return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}
            return {"raw_json": j}
    except Exception:
        pass

    s2 = re.sub(r"^Predictions for[\s\S]*?:\s*", "", s, flags=re.IGNORECASE).strip()

    # 1) label: score pairs
    pairs = re.findall(r"([^\n:]+?)\s*:\s*([0-9]*\.?[0-9]+)", s2)
    if pairs:
        out = {lab.strip(): float(sc) for lab, sc in pairs}
        top = max(out.items(), key=lambda x: x[1])
        return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}

    # 2) label newline score pairs
    lines = [ln.strip() for ln in s2.splitlines() if ln.strip()]
    out = {}
    for i in range(len(lines) - 1):
        if re.fullmatch(r"[0-9]*\.?[0-9]+", lines[i + 1]):
            out[lines[i]] = float(lines[i + 1])
    if out:
        top = max(out.items(), key=lambda x: x[1])
        return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}

    # 3) trailing numeric score -> treat preceding text as label
    m = re.search(r"([0-9]*\.?[0-9]+)\s*$", s2)
    if m:
        score = float(m.group(1))
        label = s2[:m.start()].strip().rstrip(":").strip()
        if label:
            return {"labels_scores": {label: score}, "top_label": label, "top_score": score}

    return {"raw": s}

# ---------- Streamlit page ----------
st.set_page_config(page_title="Parse Predictions", layout="wide")
st.title("🔎 Parse Model Prediction Strings")
st.caption("Load a JSON file of prediction runs and parse free-text prediction outputs into structured labels + scores.")

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
default_path = RESULTS_DIR / "example.json"

json_path = st.text_input("Path to JSON file", value=str(default_path))
jf = Path(json_path)

if not jf.exists():
    st.error(f"File not found: {jf}")
    st.stop()

try:
    raw = json.loads(jf.read_text(encoding="utf-8") or "[]")
except Exception as e:
    st.error(f"Failed to read JSON: {e}")
    st.stop()

# Build rows by extracting likely prediction text from entries
rows = []
for i, entry in enumerate(raw):
    timestamp = entry.get("timestamp") or entry.get("time") or f"idx_{i}"
    model = entry.get("model") or entry.get("model_id") or entry.get("model_name") or "<no-model>"
    # possible prediction sources (common shapes)
    raw_pred = (
        (entry.get("result") or {}).get("prediction")
        if isinstance(entry.get("result"), dict) else None
    ) or entry.get("prediction") or entry.get("raw_output") or entry.get("result") or ""
    # some entries are T1-style: top-level "text"
    text = entry.get("text") or entry.get("input_text") or entry.get("target") or ""
    parsed = parse_prediction_str(raw_pred if raw_pred is not None else "")
    rows.append({
        "idx": i,
        "timestamp": timestamp,
        "model": model,
        "text": text,
        "raw_prediction": raw_pred if raw_pred is not None else "",
        "parsed": parsed,
        "top_label": parsed.get("top_label"),
        "top_score": parsed.get("top_score"),
        "labels_scores": json.dumps(parsed.get("labels_scores") or parsed.get("raw_json") or parsed.get("raw") or {}, ensure_ascii=False),
    })

if not rows:
    st.warning("No entries found in the JSON file.")
    st.stop()

df = pd.DataFrame(rows)

# Filters
models = ["<all>"] + sorted({r["model"] for r in rows})
sel_model = st.selectbox("Model filter", models, index=0)
if sel_model != "<all>":
    df = df[df["model"] == sel_model]

lbls = ["<all>"] + sorted({r["top_label"] for r in rows if r.get("top_label")})
sel_label = st.selectbox("Top-label filter", lbls, index=0)
if sel_label != "<all>":
    df = df[df["top_label"] == sel_label]

st.markdown(f"### Parsed results ({len(df)} rows)")
st.dataframe(df[["timestamp", "model", "text", "top_label", "top_score", "labels_scores"]], use_container_width=True)

# Inspect single row
with st.expander("Inspect a single entry", expanded=False):
    sel_idx = st.number_input("Row index", min_value=0, max_value=len(rows) - 1, value=0, step=1)
    r = rows[sel_idx]
    st.json(r)

# Download parsed output
if st.button("⬇️ Download parsed results (JSON)"):
    out_path = RESULTS_DIR / f"parsed_predictions_{pd.Timestamp.now().strftime('%Y%m%dT%H%M%S')}.json"
    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    st.success(f"Wrote {out_path}")
    st.download_button("Download JSON", json.dumps(rows, ensure_ascii=False, indent=2), file_name=out_path.name, mime="application/json")