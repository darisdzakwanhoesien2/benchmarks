import json
import re
from pathlib import Path
from typing import Dict, Any

import altair as alt
import pandas as pd
import streamlit as st

# ---------- parser ----------
def _is_number_like(v) -> bool:
    try:
        float(v)
        return True
    except Exception:
        return False

def parse_prediction_str(s: str) -> Dict[str, Any]:
    if not s or not str(s).strip():
        return {"raw": ""}
    s = str(s).strip()

    # Try JSON
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

    # strip common prefix
    s2 = re.sub(r"^Predictions for[\s\S]*?:\s*", "", s, flags=re.IGNORECASE).strip()

    # label: score pairs
    pairs = re.findall(r"([^\n:]+?)\s*:\s*([0-9]*\.?[0-9]+)", s2)
    if pairs:
        out = {lab.strip(): float(sc) for lab, sc in pairs}
        top = max(out.items(), key=lambda x: x[1])
        return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}

    # label \\n score pairs
    lines = [ln.strip() for ln in s2.splitlines() if ln.strip()]
    out = {}
    for i in range(len(lines) - 1):
        if re.fullmatch(r"[0-9]*\.?[0-9]+", lines[i + 1]):
            out[lines[i]] = float(lines[i + 1])
    if out:
        top = max(out.items(), key=lambda x: x[1])
        return {"labels_scores": out, "top_label": top[0], "top_score": top[1]}

    # trailing numeric -> preceding text is label
    m = re.search(r"([0-9]*\.?[0-9]+)\s*$", s2)
    if m:
        score = float(m.group(1))
        label = s2[:m.start()].strip().rstrip(":").strip()
        if label:
            return {"labels_scores": {label: score}, "top_label": label, "top_score": score}

    return {"raw": s}

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Parse T1 Results", layout="wide")
st.title("🔎 Parse T1 (ClimateBERT) Results")
st.caption("Load t1_results.jsonl and extract label/score pairs from free-text predictions.")

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
default_path = RESULTS_DIR / "t1_results.jsonl"

path_input = st.text_input("Path to JSONL (one JSON object per line)", value=str(default_path))
jf = Path(path_input)

if not jf.exists():
    st.error(f"File not found: {jf}")
    st.stop()

rows = []
with jf.open("r", encoding="utf-8") as fh:
    for i, line in enumerate(fh):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception as e:
            rows.append({"idx": i, "error": f"json-parse-error: {e}", "raw_line": line})
            continue
        # extract prediction text from common shapes
        pred = ""
        if isinstance(entry.get("result"), dict):
            pred = entry["result"].get("prediction") or entry["result"].get("result") or entry.get("raw_output") or ""
        else:
            pred = entry.get("result") or entry.get("prediction") or entry.get("raw_output") or ""
        text = entry.get("text") or entry.get("label") or entry.get("input_text") or ""
        model = entry.get("model") or entry.get("model_id") or "<no-model>"
        parsed = parse_prediction_str(pred or "")
        rows.append({
            "idx": i,
            "timestamp": entry.get("timestamp"),
            "model": model,
            "label": entry.get("label"),
            "text": text,
            "raw_prediction": pred or "",
            "top_label": parsed.get("top_label"),
            "top_score": parsed.get("top_score"),
            "labels_scores": parsed.get("labels_scores") or parsed.get("raw_json") or parsed.get("raw") or {},
            "parsed": parsed,
        })

if not rows:
    st.warning("No rows parsed.")
    st.stop()

df = pd.DataFrame(rows)

# ensure numeric top_score and string labels
df["top_score"] = pd.to_numeric(df["top_score"], errors="coerce")
df["top_label"] = df["top_label"].astype(str).replace("None", "")

st.sidebar.markdown("### Visualization controls")
model_choices = ["<all>"] + sorted({r["model"] for r in rows if r.get("model")})
sel_model = st.sidebar.selectbox("Model", model_choices, index=0)
label_limit = st.sidebar.number_input("Max labels to show (bar chart)", min_value=5, max_value=100, value=25, step=1)

# subset for selected model
if sel_model != "<all>":
    viz_df = df[df["model"] == sel_model].copy()
else:
    viz_df = df.copy()

st.markdown(f"## Visualizations — {len(viz_df)} rows (model: {sel_model})")

# 1) Top-label counts (bar chart)
label_counts = (
    viz_df.groupby("top_label")
    .size()
    .reset_index(name="count")
    .query("top_label != ''")
    .sort_values("count", ascending=False)
)
if label_counts.empty:
    st.info("No parsed top_label values to visualize.")
else:
    st.markdown("### Top-label distribution")
    top_labels = label_counts.head(label_limit)
    bar = alt.Chart(top_labels).mark_bar().encode(
        x=alt.X("count:Q", title="Count"),
        y=alt.Y("top_label:N", sort="-x", title="Top label"),
        color=alt.Color("top_label:N", legend=None)
    ).properties(height=min(600, 40 * len(top_labels)))
    st.altair_chart(bar, use_container_width=True)

    # table with counts + score stats
    stats = (
        viz_df.loc[viz_df["top_label"] != ""]
        .groupby("top_label")["top_score"]
        .agg(["count", "mean", "std"])
        .reset_index()
        .sort_values("count", ascending=False)
    )
    st.markdown("#### Label stats (count, mean top_score, std)")
    st.dataframe(stats.head(label_limit), use_container_width=True)

# 2) Top_score distribution by model (boxplot)
st.markdown("### Top-score distribution by model")
box_src = df.dropna(subset=["top_score"])
if box_src.empty:
    st.info("No numeric top_score values to visualize.")
else:
    # limit number of models shown for readability
    models_for_box = sorted(box_src["model"].unique())
    if len(models_for_box) > 20:
        models_for_box = models_for_box[:20]
        box_src = box_src[box_src["model"].isin(models_for_box)]
    box = alt.Chart(box_src).mark_boxplot(extent=1.5).encode(
        x=alt.X("model:N", title="Model", sort=models_for_box),
        y=alt.Y("top_score:Q", title="Top score"),
        color=alt.Color("model:N", legend=None)
    ).properties(height=300)
    st.altair_chart(box, use_container_width=True)

# 3) Scatter: top_score vs top_label (for selected model)
st.markdown("### Top-score per model (scatter)")
scatter_src = viz_df.dropna(subset=["top_score"]).copy()
if scatter_src.empty:
    st.info("No numeric top_score values for the selected model.")
else:
    scatter_src["top_label_short"] = scatter_src["top_label"].fillna("").apply(lambda x: x if len(x) < 80 else x[:77] + "…")
    # preserve model order for plotting
    models_order = list(dict.fromkeys(scatter_src["model"].tolist()))
    scatter = alt.Chart(scatter_src).mark_circle(size=80, opacity=0.8).encode(
        x=alt.X("top_score:Q", title="Top score"),
        y=alt.Y("model:N", sort=models_order, title="Model"),
        color=alt.Color("top_label_short:N", title="Top label"),
        tooltip=["idx","timestamp","model","text","top_label","top_score"]
    ).interactive().properties(height=min(800, 40 * len(models_order)))
    st.altair_chart(scatter, use_container_width=True)

# 4) Summary table per model
st.markdown("### Summary per model")
summary = (
    df.groupby("model")
    .agg(rows=("idx", "count"), labels_present=("top_label", lambda s: s.replace("None","").astype(bool).sum()), mean_top_score=("top_score","mean"))
    .reset_index()
    .sort_values("rows", ascending=False)
)
st.dataframe(summary, use_container_width=True)

# allow download of visualization-ready table
if st.button("⬇️ Download viz table (JSON)"):
    out = RESULTS_DIR / f"t1_viz_table_{pd.Timestamp.now().strftime('%Y%m%dT%H%M%S')}.json"
    out.write_text(df.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
    st.success(f"Wrote {out}")
    st.download_button("Download JSON", df.to_json(orient="records", force_ascii=False, indent=2), file_name=out.name, mime="application/json")

if st.button("⬇️ Download parsed results (JSON)"):
    out = RESULTS_DIR / f"t1_parsed_{pd.Timestamp.now().strftime('%Y%m%dT%H%M%S')}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    st.success(f"Wrote {out}")
    st.download_button("Download JSON", json.dumps(rows, ensure_ascii=False, indent=2), file_name=out.name, mime="application/json")