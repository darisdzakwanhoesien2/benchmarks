import json
import os
import html
from pathlib import Path
from typing import List, Tuple, Any, Dict
import streamlit as st

HERE = Path(__file__).resolve()
RESULTS_DIR = HERE.parents[1] / "results"
GT_FILE = str(RESULTS_DIR / "esg_records.json")
ABSA_FILE = str(RESULTS_DIR / "absa_results.json")
BENCH_FILE = str(RESULTS_DIR / "predictions.json")

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
        return None
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def normalize_dataset(data) -> Tuple[dict, List[str]]:
    out = {}
    if not data:
        return out, []
    if isinstance(data, dict) and "models" in data:
        for m, info in data["models"].items():
            out[m] = (info.get("records") if isinstance(info, dict) else []) or []
        return out, list(out.keys())
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            # per-entry model + records
            if "model" in item and "records" in item:
                out.setdefault(item["model"], [])
                out[item["model"]].extend(item.get("records") or [])
            # combined models block
            elif "models" in item and isinstance(item["models"], dict):
                for m, info in item["models"].items():
                    out.setdefault(m, [])
                    if isinstance(info, dict):
                        out[m].extend(info.get("records") or [])
            # single record with model present
            elif "model" in item and ("text" in item or "result" in item):
                out.setdefault(item["model"], [])
                out[item["model"]].append(item)
            else:
                out.setdefault("_anon", [])
                out["_anon"].append(item)
    return out, list(out.keys())

def map_esg_tag(raw) -> str:
    if raw is None:
        return "unknown"
    if isinstance(raw, list) and raw:
        raw = raw[0]
    tag = str(raw).lower()
    if tag in ("e", "environmental", "environment", "env"):
        return "E"
    if tag in ("s", "social"):
        return "S"
    if tag in ("g", "governance", "govern", "governance"):
        return "G"
    # keywords
    if "env" in tag or "climate" in tag or "natural" in tag:
        return "E"
    if "social" in tag or "community" in tag or "welfare" in tag:
        return "S"
    if "govern" in tag or "risk" in tag or "strategy" in tag or "corporate" in tag:
        return "G"
    return "unknown"

def extract_segments_from_record(rec: dict) -> List[Tuple[str, Any]]:
    segments = []
    if not rec:
        return segments
    # 'result' list of segments
    if isinstance(rec.get("result"), list):
        for s in rec["result"]:
            if isinstance(s, dict):
                text = s.get("text") or s.get("segment") or ""
                segments.append((text, s))
    # nested 'records' list
    elif isinstance(rec.get("records"), list):
        for s in rec["records"]:
            if isinstance(s, dict):
                text = s.get("text") or ""
                segments.append((text, s))
    # simple record with 'text'
    elif isinstance(rec.get("text"), str):
        segments.append((rec.get("text"), rec))
    else:
        # pick first long string field
        if isinstance(rec, dict):
            for k, v in rec.items():
                if isinstance(v, str) and len(v) > 20:
                    segments.append((v, rec))
                    break
    return segments

def render_segment_html(text: str, esg_tag: str) -> str:
    color = ESG_COLOR.get(esg_tag) or ESG_COLOR["unknown"]
    safe = html.escape(text or "")
    return f'<div style="padding:10px;margin:6px 0;background:{color};border-radius:6px;">{safe}</div>'

def highlight_input_inline(input_text: str, records: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Try to inline-highlight the original input by locating extracted record texts.
    Returns (html, unmatched_records_list).
    """
    if not input_text:
        return "", records or []

    low = input_text.lower()
    intervals = []
    unmatched = []
    # collect candidate intervals
    for rec in records:
        rec_text = rec.get("text") if isinstance(rec, dict) else (str(rec) if rec else "")
        if not rec_text or len(rec_text.strip()) < 4:
            unmatched.append(rec)
            continue
        rec_low = rec_text.strip().lower()
        idx = low.find(rec_low)
        if idx >= 0:
            intervals.append({"start": idx, "end": idx + len(rec_low), "rec": rec})
        else:
            # try fuzzy find by first 40 chars
            snippet = rec_low[:40]
            idx2 = low.find(snippet) if snippet else -1
            if idx2 >= 0:
                intervals.append({"start": idx2, "end": idx2 + len(rec_low), "rec": rec})
            else:
                unmatched.append(rec)

    # remove overlaps: keep earliest non-overlapping intervals
    intervals = sorted(intervals, key=lambda x: x["start"])
    non_overlap = []
    last_end = -1
    for it in intervals:
        if it["start"] >= last_end:
            non_overlap.append(it)
            last_end = it["end"]
        else:
            # overlapping: skip or shorten (skip for simplicity)
            continue

    # build html by slicing
    parts = []
    pos = 0
    for it in non_overlap:
        start, end, rec = it["start"], it["end"], it["rec"]
        # append text before
        pre = html.escape(input_text[pos:start])
        if pre:
            parts.append(f'<span>{pre}</span>')
        # colored span for matched segment
        esg_tag = map_esg_tag(rec.get("esg") if isinstance(rec, dict) else None)
        color = ESG_COLOR.get(esg_tag) or ESG_COLOR["unknown"]
        matched = html.escape(input_text[start:end])
        parts.append(f'<span style="background:{color};padding:2px 4px;border-radius:4px">{matched}</span>')
        pos = end
    # tail
    tail = html.escape(input_text[pos:])
    if tail:
        parts.append(f'<span>{tail}</span>')

    html_out = "<div style='line-height:1.5;font-size:15px'>" + "".join(parts) + "</div>"
    return html_out, unmatched

st.set_page_config(page_title="ESG Full-text visualizer", layout="wide")
st.title("ESG Full-text visualizer")

with st.expander("Load data and visualize", expanded=True):
    src = st.selectbox(
        "Source JSON",
        [
            ("GT (esg_records.json)", GT_FILE),
            ("ABSA (absa_results.json)", ABSA_FILE),
            ("Benchmark (predictions.json)", BENCH_FILE),
            ("Upload JSON file...", None),
        ],
        format_func=lambda t: t[0] if isinstance(t, tuple) else (t if t else "Upload JSON file...")
    )

    chosen_path = src[1] if isinstance(src, tuple) else None
    data = None
    if chosen_path is None:
        uploaded = st.file_uploader("Upload a JSON file", type=["json"])
        if uploaded:
            try:
                data = json.load(uploaded)
            except Exception as e:
                st.error(f"Invalid JSON upload: {e}")
    else:
        data = safe_load_json(chosen_path)

    if not data:
        st.info("No data loaded. Select a file or upload JSON.")
    else:
        # If top-level is list of saved runs (with 'input' and 'models'), allow selecting run
        run_entries = []
        if isinstance(data, list) and any(isinstance(it, dict) and ("input" in it or "timestamp" in it) for it in data):
            for i, entry in enumerate(data):
                ts = entry.get("timestamp") or f"entry_{i:03d}"
                preview = (entry.get("input") or "")[:120].replace("\n", " ")
                run_entries.append((i, ts, preview, entry))
            sel_run_idx = st.selectbox("Select run", options=list(range(len(run_entries))),
                                       format_func=lambda i: f"{run_entries[i][0]} | {run_entries[i][1]} | {run_entries[i][2]}")
            sel_entry = run_entries[sel_run_idx][3]
            input_text = sel_entry.get("input") or ""
            models_map = sel_entry.get("models") or {}
            model_names = list(models_map.keys())
        else:
            # fallback: normalize dataset as before
            models_map, model_names = normalize_dataset(data)
            input_text = ""

        if not model_names:
            st.info("No models found in file.")
        else:
            model_choice = st.selectbox("Model", ["_all"] + model_names)
            records = []
            # helper: normalize per-model entry to a list of record dicts
            def _records_from_entry(entry):
                if entry is None:
                    return []
                # common case: entry is a dict with a 'records' list
                if isinstance(entry, dict):
                    if "records" in entry and isinstance(entry["records"], list):
                        return entry["records"]
                    # some exporters put the list directly under the model key
                    # or the entry itself can be a mapping of record id -> rec; try to recover lists
                    # fallback: if entry looks like a list disguised as dict values
                    vals = [v for v in entry.values() if isinstance(v, list)]
                    if vals:
                        return vals[0]
                    return []
                # entry might already be a list of records
                if isinstance(entry, list):
                    return entry
                return []

            if model_choice == "_all":
                for m in model_names:
                    entry = models_map.get(m)
                    for rec in _records_from_entry(entry):
                        records.append((m, rec))
            else:
                entry = models_map.get(model_choice)
                for rec in _records_from_entry(entry):
                    records.append((model_choice, rec))

            if not records:
                st.info("No records for selected model.")
            else:
                # if we selected from run entry, records currently are tuples (m, rec)
                # convert to list of record dicts for inline highlighting
                records_dicts = []
                for m, rec in records:
                    # if rec already contains text and esg, keep
                    if isinstance(rec, dict) and "text" in rec:
                        # include model name on record for reference
                        rec_copy = dict(rec)
                        rec_copy["_model"] = m
                        records_dicts.append(rec_copy)
                    else:
                        # normalize segments
                        segments = extract_segments_from_record(rec if isinstance(rec, dict) else {})
                        for text, meta in segments:
                            meta_rec = meta if isinstance(meta, dict) else {}
                            meta_rec["_model"] = m
                            if "text" not in meta_rec:
                                meta_rec["text"] = text
                            records_dicts.append(meta_rec)

                # index selector for record grouping (keep same behavior)
                # Defensive: handle empty records_dicts and changing model choices safely.
                if not records_dicts:
                    st.warning("No extracted record dicts available to select.")
                    st.stop()

                # Build stable display labels and let selectbox return the label.
                preview_labels = [
                    f"{i:03d} | {records_dicts[i].get('_model','')} | {records_dicts[i].get('text','')[:80]}"
                    for i in range(len(records_dicts))
                ]
                sel_label = st.selectbox(
                    "Record index",
                    options=preview_labels,
                    index=0,
                    key=f"record_index_{model_choice}"
                )
                # map selected label back to index safely and clamp
                try:
                    idx = preview_labels.index(sel_label)
                except ValueError:
                    idx = 0
                # clamp to valid range
                idx = max(0, min(idx, len(records_dicts) - 1))
                chosen_record = records_dicts[idx]

                st.markdown("**Model:**")
                st.write(chosen_record.get("_model", model_choice))

                col_left, col_right = st.columns([2, 1])
                with col_left:
                    st.markdown("**Original Input (plain)**")
                    if input_text:
                        st.code(input_text)
                    else:
                        # If no run-level input provided, show concatenated text of all records
                        concat_input = "\n\n".join(r.get("text", "") for r in records_dicts)
                        st.code(concat_input)

                    # Inline-highlight the whole input using all records for the chosen model
                    html_inline, unmatched = highlight_input_inline(input_text or ("\n".join([r.get("text","") for r in records_dicts])), records_dicts)
                    st.markdown("**Inline highlighted input (matched segments highlighted)**")
                    if html_inline:
                        st.markdown(html_inline, unsafe_allow_html=True)
                    else:
                        st.warning("No input available to inline-highlight.")

                    # show unmatched extracted segments as colored blocks
                    if unmatched:
                        st.markdown("**Extracted segments not found inline (shown as blocks)**")
                        for rec in unmatched:
                            txt = rec.get("text") or str(rec)
                            esg_tag = map_esg_tag(rec.get("esg"))
                            st.markdown(render_segment_html(txt, esg_tag), unsafe_allow_html=True)

                with col_right:
                    st.markdown("**Selected record (detailed)**")
                    st.code(json.dumps(chosen_record, ensure_ascii=False, indent=2))
                    st.markdown("**Legend**")
                    for k, v in ESG_COLOR.items():
                        st.markdown(f"<div style='display:flex;align-items:center;margin:4px 0'><div style='width:18px;height:18px;background:{v};border-radius:4px;margin-right:8px'></div><div>{k}</div></div>", unsafe_allow_html=True)

                # allow download of the inline-highlighted HTML and blocks
                if st.button("Download highlighted input + blocks HTML"):
                    fname = f"highlighted_input_{(chosen_record.get('_model') or 'model')}_{idx}.html"
                    blocks_html = ""
                    # inline part
                    blocks_html += f"<h3>Inline highlighted input</h3>\n{html_inline}"
                    # unmatched blocks
                    if unmatched:
                        blocks_html += "<h3>Unmatched extracted segments</h3>\n"
                        for rec in unmatched:
                            esg_tag = map_esg_tag(rec.get("esg"))
                            blocks_html += render_segment_html(rec.get("text") or "", esg_tag)
                    doc = f"<html><head><meta charset='utf-8'><title>{fname}</title></head><body>{blocks_html}</body></html>"
                    st.download_button("Download HTML", data=doc, file_name=fname, mime="text/html")
