import json
import re
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

# ---------------------
# CONFIG
# ---------------------
st.set_page_config(
    page_title="ClimateBERT — Results Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("ClimateBERT — Results Dashboard")

RESULTS_FPATH = Path(__file__).resolve().parents[1] / "results" / "climatebert_results.json"

if not RESULTS_FPATH.exists():
    st.warning(f"No results file found at {RESULTS_FPATH}")
    st.stop()

# ---------------------
# Parser for response_raw
# ---------------------
def parse_response_raw(raw):
    if raw is None:
        return {"raw": raw, "models": []}

    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
    lines = [ln.strip() for ln in text.splitlines()]

    models = []
    cur = None

    bullet_re = re.compile(r"^[•\-\*\u2022]\s*(.+)$")
    label_val_re = re.compile(r"^(.+?)\s*[:\-]\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")

    for ln in lines:
        if not ln:
            continue

        # New model section
        if ln.startswith("###"):
            if cur is not None:
                models.append(cur)
            cur = {
                "name": ln[3:].strip(),
                "status": "ok",
                "error": None,
                "scores": {}
            }
            continue

        if cur is None:
            continue

        # Error detection
        if "❌" in ln or ln.lower().startswith("error:") or "unrecognized model" in ln.lower():
            msg = ln.replace("❌", "").strip()
            if msg.lower().startswith("error:"):
                msg = msg[6:].strip()

            cur["status"] = "error"
            cur["error"] = (cur["error"] + " | " + msg) if cur.get("error") else msg
            continue

        # Bullet parsing
        m = bullet_re.match(ln)
        candidate = m.group(1).strip() if m else ln

        # Label: value format
        m2 = label_val_re.match(candidate)
        if m2:
            key = m2.group(1).strip()
            try:
                val = float(m2.group(2))
            except Exception:
                val = m2.group(2)

            cur["scores"][key] = val
            continue

        # Fallback parsing
        if m:
            parts = candidate.rsplit(" ", 1)
            if len(parts) == 2:
                key, tail = parts[0].strip(), parts[1].strip()
                try:
                    val = float(tail)
                    cur["scores"][key] = val
                    continue
                except Exception:
                    pass

        # Notes
        cur.setdefault("note", "")
        cur["note"] = (cur["note"] + " | " + ln) if cur["note"] else ln

    if cur is not None:
        models.append(cur)

    return {"raw": text, "models": models}


# ---------------------
# Load data
# ---------------------
with RESULTS_FPATH.open("r", encoding="utf-8") as f:
    raw_list = json.load(f)

expanded_rows = []

for rec in raw_list:
    parsed = rec.get("response_parsed") or parse_response_raw(rec.get("response_raw"))

    ts = rec.get("timestamp")
    try:
        ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
    except Exception:
        ts_dt = None

    base = {
        "timestamp": ts_dt,
        "source_mode": rec.get("mode"),
        "space_url": rec.get("space_url"),
        "input_text": rec.get("input_text"),
    }

    for m in parsed.get("models", []):
        scores = m.get("scores", {}) or {}

        if scores:
            for label, val in scores.items():
                row = dict(base)
                row.update({
                    "model": m.get("name"),
                    "model_status": m.get("status"),
                    "model_error": m.get("error"),
                    "model_note": m.get("note"),
                    "score_label": label,
                    "score_value": val
                })
                expanded_rows.append(row)
        else:
            row = dict(base)
            row.update({
                "model": m.get("name"),
                "model_status": m.get("status"),
                "model_error": m.get("error"),
                "model_note": m.get("note"),
                "score_label": None,
                "score_value": None
            })
            expanded_rows.append(row)

df = pd.DataFrame(expanded_rows)

# Ensure a numeric column exists early so filters and the heatmap use it
df["score_value_numeric"] = pd.to_numeric(df["score_value"], errors="coerce")

if df.empty:
    st.info("No model-level rows found.")
    st.stop()

# ---------------------
# Sidebar filters
# ---------------------
st.sidebar.header("Filters")

models = sorted(df["model"].dropna().unique().tolist())
selected_models = st.sidebar.multiselect("Models", models, default=models)

status_opts = sorted(df["model_status"].dropna().unique().tolist())
selected_status = st.sidebar.multiselect("Status", status_opts, default=status_opts)

# Default min_score to the minimum numeric score (if any) to avoid unintentionally filtering all rows
default_min = float(df["score_value_numeric"].min()) if df["score_value_numeric"].notnull().any() else 0.0
min_score = st.sidebar.number_input("Min score", value=default_min, step=0.01)

date_min = st.sidebar.date_input(
    "From",
    value=df["timestamp"].dropna().min().date() if df["timestamp"].notnull().any() else None
)

date_max = st.sidebar.date_input(
    "To",
    value=df["timestamp"].dropna().max().date() if df["timestamp"].notnull().any() else None
)

apply_filters = st.sidebar.button("Apply filters")


def apply(df0):
    d = df0[df0["model"].isin(selected_models)]
    d = d[d["model_status"].isin(selected_status)]

    if date_min:
        d = d[d["timestamp"].notnull() & (d["timestamp"].dt.date >= date_min)]

    if date_max:
        d = d[d["timestamp"].notnull() & (d["timestamp"].dt.date <= date_max)]

    if min_score is not None:
        # Use the numeric column for comparison
        d = d[
            d["score_value_numeric"].isnull() |
            (d["score_value_numeric"] >= min_score)
        ]

    return d


df_view = apply(df) if apply_filters else df.copy()

st.markdown(f"Found {len(df_view)} rows (from {len(raw_list)} records).")

# ---------------------
# Display
# ---------------------
with st.expander("Raw records"):
    st.write(raw_list)

st.subheader("Model-level table")
st.dataframe(df_view.reset_index(drop=True), use_container_width=True)

# ---------------------
# Explorer
# ---------------------
st.subheader("Record explorer")

for i, rec in enumerate(raw_list[-50:][::-1]):
    parsedrec = rec.get("response_parsed") or parse_response_raw(rec.get("response_raw"))

    label = f"{i+1} — {rec.get('timestamp')} — {rec.get('mode')}"

    with st.expander(label):
        st.markdown("**Input text**")
        st.code(rec.get("input_text", "")[:1000])

        st.markdown("**Parsed models**")
        for m in parsedrec.get("models", []):
            st.markdown(f"- **{m.get('name')}** — `{m.get('status')}`")

            if m.get("error"):
                st.warning(m.get("error"))

            if m.get("scores"):
                st.table(pd.DataFrame(list(m["scores"].items()), columns=["label", "value"]))

# ---------------------
# Heatmap
# ---------------------
st.subheader("Aggregated heatmap")

df_view = df_view.copy()  # already contains score_value_numeric

pivot = df_view.dropna(subset=["score_label", "score_value_numeric"]).pivot_table(
    index="model",
    columns="score_label",
    values="score_value_numeric",
    aggfunc="mean"
)

if pivot.empty:
    st.info("No numeric scores to visualize. (non-numeric score_value entries were ignored or filtered out)")
else:
    try:
        import plotly.express as px
        fig = px.imshow(
            pivot.fillna(0),
            labels=dict(x="label", y="model", color="mean score"),
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.table(pivot.round(3))

# ---------------------
# Export
# ---------------------
st.subheader("Export parsed results")

parsed_export = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "records": raw_list
}

st.download_button(
    "Download JSON",
    data=json.dumps(parsed_export, ensure_ascii=False, indent=2),
    file_name="climatebert_parsed.json",
    mime="application/json"
)