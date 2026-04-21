import json
from pathlib import Path

import pandas as pd
import streamlit as st

# load results file
RESULTS = Path(__file__).resolve().parents[1] / "results" / "esg_records.json"

st.set_page_config(page_title="ESG Record Viewer", layout="wide")
st.title("📋 ESG Record Viewer")
st.caption("Select a run entry and inspect its extracted records as a table.")

if not RESULTS.exists():
    st.error(f"Missing results file: {RESULTS}")
    st.stop()

try:
    raw = json.loads(RESULTS.read_text(encoding="utf-8") or "[]")
except Exception as e:
    st.error(f"Failed to read JSON: {e}")
    st.stop()

# build choices for entries that contain records
choices = []
entries = []
for i, entry in enumerate(raw):
    ts = entry.get("timestamp") or entry.get("time") or f"idx_{i}"
    model = entry.get("model", "<no-model>")
    target = entry.get("target", "<no-target>")
    prompt = entry.get("prompt", "<no-prompt>")
    label = f"{ts} | {model} | {target} | {prompt}"
    choices.append(label)
    entries.append(entry)

if not choices:
    st.warning("No entries found in esg_records.json")
    st.stop()

# default to the known timestamp if present
default_label = next((c for c in choices if "2026-03-26T22:03:45.302119Z" in c), choices[0])
sel = st.selectbox("Select run entry", choices, index=choices.index(default_label))

entry = entries[choices.index(sel)]

st.markdown("### Run metadata")
st.write({
    "timestamp": entry.get("timestamp"),
    "model": entry.get("model"),
    "target": entry.get("target"),
    "prompt": entry.get("prompt"),
    "ok": entry.get("ok"),
})

records = entry.get("records") or []

if not records:
    st.info("No parsed records for this run. Raw output (if any) shown below.")
    st.code(entry.get("raw_output", "")[:10000])
else:
    # normalize records to flat table
    def normalize(r):
        return {
            "text": r.get("text"),
            "aspect": r.get("aspect"),
            "labels": ", ".join(r.get("labels", [])) if isinstance(r.get("labels", []), (list,tuple)) else r.get("labels"),
            "esg": r.get("esg"),
            "sentiment": r.get("sentiment"),
            "sentiment_score": r.get("sentiment_score"),
            "reasoning": r.get("reasoning"),
        }

    df = pd.DataFrame([normalize(r) for r in records])
    st.markdown(f"### Parsed records ({len(df)} rows)")
    st.dataframe(df, use_container_width=True)

    # allow download of selected records
    st.download_button(
        "⬇️ Download selected records (JSON)",
        json.dumps(records, ensure_ascii=False, indent=2),
        file_name=f"esg_records_selected_{entry.get('timestamp','run')}.json",
        mime="application/json",
    )
```# filepath: /Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks/new_page/pages/0_7_visualize_esg_record.py
import json
from pathlib import Path

import pandas as pd
import streamlit as st

# load results file
RESULTS = Path(__file__).resolve().parents[1] / "results" / "esg_records.json"

st.set_page_config(page_title="ESG Record Viewer", layout="wide")
st.title("📋 ESG Record Viewer")
st.caption("Select a run entry and inspect its extracted records as a table.")

if not RESULTS.exists():
    st.error(f"Missing results file: {RESULTS}")
    st.stop()

try:
    raw = json.loads(RESULTS.read_text(encoding="utf-8") or "[]")
except Exception as e:
    st.error(f"Failed to read JSON: {e}")
    st.stop()

# build choices for entries that contain records
choices = []
entries = []
for i, entry in enumerate(raw):
    ts = entry.get("timestamp") or entry.get("time") or f"idx_{i}"
    model = entry.get("model", "<no-model>")
    target = entry.get("target", "<no-target>")
    prompt = entry.get("prompt", "<no-prompt>")
    label = f"{ts} | {model} | {target} | {prompt}"
    choices.append(label)
    entries.append(entry)

if not choices:
    st.warning("No entries found in esg_records.json")
    st.stop()

# default to the known timestamp if present
default_label = next((c for c in choices if "2026-03-26T22:03:45.302119Z" in c), choices[0])
sel = st.selectbox("Select run entry", choices, index=choices.index(default_label))

entry = entries[choices.index(sel)]

st.markdown("### Run metadata")
st.write({
    "timestamp": entry.get("timestamp"),
    "model": entry.get("model"),
    "target": entry.get("target"),
    "prompt": entry.get("prompt"),
    "ok": entry.get("ok"),
})

records = entry.get("records") or []

if not records:
    st.info("No parsed records for this run. Raw output (if any) shown below.")
    st.code(entry.get("raw_output", "")[:10000])
else:
    # normalize records to flat table
    def normalize(r):
        return {
            "text": r.get("text"),
            "aspect": r.get("aspect"),
            "labels": ", ".join(r.get("labels", [])) if isinstance(r.get("labels", []), (list,tuple)) else r.get("labels"),
            "esg": r.get("esg"),
            "sentiment": r.get("sentiment"),
            "sentiment_score": r.get("sentiment_score"),
            "reasoning": r.get("reasoning"),
        }

    df = pd.DataFrame([normalize(r) for r in records])
    st.markdown(f"### Parsed records ({len(df)} rows)")
    st.dataframe(df, use_container_width=True)

    # allow download of selected records
    st.download_button(
        "⬇️ Download selected records (JSON)",
        json.dumps(records, ensure_ascii=False, indent=2),
        file_name=f"esg_records_selected_{entry.get('timestamp','run')}.json",