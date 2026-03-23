import json
import os
from pathlib import Path
from typing import Tuple
import streamlit as st

# --- configuration: locate result files relative to this script ---
HERE = Path(__file__).resolve()
RESULTS_DIR = HERE.parents[1] / "results"  # new_page/results
gt_file = str(RESULTS_DIR / "esg_records.json")
absa_file = str(RESULTS_DIR / "absa_results.json")
bench_file = str(RESULTS_DIR / "predictions.json")

# --- Highlight viewer utilities ---
ESG_COLOR = {
    "E": "#c6f6d5",        # green-ish
    "Environmental": "#c6f6d5",
    "S": "#bee3f8",        # blue-ish
    "Social": "#bee3f8",
    "G": "#fed7aa",        # orange-ish
    "Governance": "#fed7aa",
    "unknown": "#f0f0f0"
}

def safe_load_json(path: str):
    if not path:
        st.warning("No path provided.")
        return None
    if not os.path.exists(path):
        st.warning(f"File not found: {path}")
        return None
    try:
        with open(path, "r", encoding="utf8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Could not load JSON '{path}': {e}")
        return None

def normalize_dataset(data) -> Tuple[dict, list]:
    """
    Normalize common shapes into a mapping:
      model -> list of record dicts (each having at least 'text' and optional 'esg'/'labels'/'sentiment')
    Accepts:
      - list of top-level entries (each may have 'model' and 'records')
      - a single object where 'models' maps to per-model entries (like combined results)
    """
    out = {}
    if not data:
        return out, []

    if isinstance(data, dict) and "models" in data:
        # unexpected top-level, but handle
        for m, info in data["models"].items():
            recs = info.get("records") if isinstance(info, dict) else []
            out[m] = recs or []
        return out, list(out.keys())

    if isinstance(data, list):
        for item in data:
            # item may be {"model": "...", "records": [...] } or {'models': {...}} or bare records
            if isinstance(item, dict):
                if "models" in item and isinstance(item["models"], dict):
                    for m, info in item["models"].items():
                        out.setdefault(m, [])
                        if isinstance(info, dict):
                            recs = info.get("records") or []
                            out[m].extend(recs)
                elif "model" in item and "records" in item:
                    out.setdefault(item["model"], [])
                    out[item["model"]].extend(item.get("records") or [])
                elif "model" in item and ("text" in item or "result" in item):
                    out.setdefault(item["model"], [])
                    out[item["model"]].append(item)
                else:
                    # guess: list of records without model -> put under "_anon"
                    out.setdefault("_anon", [])
                    out["_anon"].append(item)
            else:
                # skip non-dict entries
                continue
    return out, list(out.keys())

def get_texts_from_record(rec) -> list:
    """
    Return list of (segment_text, meta_dict) pairs from a record.
    Supports various shapes: 'text', 'result' (list of segments), 'records' nested, or whole record as text.
    """
    segments = []
    if not rec:
        return segments
    # some outputs use 'result' as list of segments
    if isinstance(rec, dict):
        if "result" in rec and isinstance(rec["result"], list):
            for seg in rec["result"]:
                if isinstance(seg, dict):
                    text = seg.get("text") or seg.get("segment") or ""
                    segments.append((text, seg))
        elif "text" in rec and isinstance(rec.get("text"), str):
            segments.append((rec.get("text"), rec))
        elif "records" in rec and isinstance(rec["records"], list):
            for seg in rec["records"]:
                if isinstance(seg, dict) and "text" in seg:
                    segments.append((seg.get("text"), seg))
        else:
            # try to grab any string fields
            for k, v in rec.items():
                if isinstance(v, str) and len(v) > 20:
                    segments.append((v, rec))
                    break
    elif isinstance(rec, str):
        segments.append((rec, {}))
    return segments

def render_highlight_html(text: str, esg_tag) -> str:
    color = ESG_COLOR.get(esg_tag) or ESG_COLOR.get(str(esg_tag)) or ESG_COLOR["unknown"]
    safe = (text or "").replace("<", "&lt;").replace(">", "&gt;")
    return f'<div style="padding:8px;margin:6px 0;background:{color};border-radius:6px;">{safe}</div>'

# --- UI: Highlights viewer ---
st.set_page_config(page_title="ESG Highlights viewer", layout="wide")
st.title("ESG Highlights viewer")

with st.expander("Open highlights / visualizer", expanded=True):
    src = st.selectbox("Source JSON", [
        ("GT (esg_records.json)", gt_file),
        ("ABSA (absa_results.json)", absa_file),
        ("Benchmark (predictions.json)", bench_file),
        ("Upload JSON file...", None)
    ], format_func=lambda t: t[0] if isinstance(t, tuple) else (t if t else "Upload JSON file..."))

    chosen = None
    if isinstance(src, tuple):
        chosen = src[1]
    if chosen is None:
        uploaded = st.file_uploader("Upload a JSON file with records", type=["json"])
        if uploaded:
            try:
                data = json.load(uploaded)
            except Exception as e:
                st.error(f"Invalid JSON upload: {e}")
                data = None
        else:
            data = None
    else:
        data = safe_load_json(chosen)

    if not data:
        st.info("No data loaded. Select a file or upload JSON.")
    else:
        models_map, model_names = normalize_dataset(data)

        if not model_names:
            st.info("No model/records found in selected file.")
        else:
            model_choice = st.selectbox("Model", ["_all"] + model_names)
            records_list = []
            if model_choice == "_all":
                for m in model_names:
                    for rec in models_map.get(m, []):
                        records_list.append((m, rec))
            else:
                for rec in models_map.get(model_choice, []):
                    records_list.append((model_choice, rec))

            if not records_list:
                st.info("No records found for selected model.")
            else:
                # present selector by index and short preview
                preview_options = []
                for i, (m, rec) in enumerate(records_list):
                    txts = get_texts_from_record(rec)
                    preview = (txts[0][0][:140] + "...") if txts else (repr(rec)[:140] + "...")
                    preview_options.append(f"{i:03d} | {m} | {preview}")

                sel_idx = st.selectbox("Record", options=list(range(len(preview_options))), format_func=lambda i: preview_options[i])

                model_name, record = records_list[sel_idx]
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("**Model:**")
                    st.write(model_name)
                    st.markdown("**Raw record**")
                    st.code(json.dumps(record, ensure_ascii=False, indent=2))
                    st.markdown("Legend")
                    st.write(", ".join([f"{k}={v}" for k, v in ESG_COLOR.items() if k != "unknown"]))

                with col2:
                    st.markdown("**Highlighted segments:**")
                    segs = get_texts_from_record(record)
                    if not segs:
                        st.warning("No textual segments found in this record.")
                    html_parts = []
                    for seg_text, meta in segs:
                        # determine esg tag: try meta['esg'], meta['labels'] or meta.get('esg')
                        esg_tag = None
                        if isinstance(meta, dict):
                            esg_tag = meta.get("esg") or meta.get("esg_tags") or meta.get("labels")
                            if isinstance(esg_tag, list) and esg_tag:
                                esg_tag = esg_tag[0]
                        # fallback try to infer from labels
                        if not esg_tag and isinstance(meta, dict):
                            lbls = meta.get("labels") or meta.get("label") or []
                            if isinstance(lbls, list) and lbls:
                                # try map common words
                                l0 = str(lbls[0]).lower()
                                if "env" in l0 or "climate" in l0 or "natural" in l0:
                                    esg_tag = "E"
                                elif "social" in l0 or "community" in l0 or "sharia" in l0 or "msme" in l0:
                                    esg_tag = "S"
                                elif "govern" in l0 or "risk" in l0 or "strategy" in l0:
                                    esg_tag = "G"
                        if not esg_tag:
                            esg_tag = "unknown"
                        html_parts.append(render_highlight_html(seg_text or "", esg_tag))
                        # optionally show metadata
                        if isinstance(meta, dict):
                            md = {}
                            for k in ("labels", "esg", "sentiment"):
                                if k in meta:
                                    md[k] = meta[k]
                            if md:
                                html_parts.append(f"<div style='margin-bottom:8px;font-size:0.9em;color:#444'>meta: {json.dumps(md, ensure_ascii=False)}</div>")

                    html = "\n".join(html_parts)
                    st.markdown(html, unsafe_allow_html=True)

                    # download single record HTML
                    if st.button("Prepare download for this record"):
                        fname = f"highlight_{model_name.replace('/', '_')}_{sel_idx}.html"
                        html_doc = f"<html><head><meta charset='utf-8'><title>{fname}</title></head><body>{html}</body></html>"
                        st.download_button("Download highlighted HTML", data=html_doc, file_name=fname, mime="text/html")