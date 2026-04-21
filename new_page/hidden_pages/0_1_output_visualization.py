import streamlit as st
import json
import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ESG Prediction Results",
    page_icon="📋",
    layout="wide"
)

st.title("📋 ESG Prediction Results Viewer")
st.markdown("---")

# ─────────────────────────────────────────────
# File Paths
# ─────────────────────────────────────────────
RESULTS_DIR      = Path(__file__).resolve().parents[1] / "results"
PREDICTIONS_FILE = RESULTS_DIR / "predictions.json"
ABSA_FILE        = RESULTS_DIR / "absa_results.json"
ESG_RECORDS_FILE = RESULTS_DIR / "esg_records.json"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
@st.cache_data
def load_json(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def safe_str(val, maxlen: int = 0) -> str:
    s = str(val) if val is not None else ""
    return s[:maxlen] if maxlen else s


def extract_label_score(prediction_str: str) -> tuple[str, float | None]:
    if not isinstance(prediction_str, str):
        return safe_str(prediction_str), None
    if prediction_str.startswith("Error:"):
        return "❌ " + prediction_str.split("\n")[0].replace("Error: ", "")[:80], None
    lines = prediction_str.strip().splitlines()
    for line in reversed(lines):
        if ":" in line:
            parts = line.rsplit(":", 1)
            label = parts[0].strip()
            try:
                score = round(float(parts[1].strip()), 4)
                return label, score
            except ValueError:
                pass
    return prediction_str[:80], None


# ── normalise ESG field ────────────────────────────────────────────────────────
ESG_NORM: dict[str, str] = {
    # full words
    "environmental": "Environmental",
    "social":        "Social",
    "governance":    "Governance",
    # single-letter codes produced by few-shot prompt
    "e": "Environmental",
    "s": "Social",
    "g": "Governance",
    "n": "Not ESG",
    # boolean / none
    "none": "Not ESG",
    "true": "ESG-Related",
    "false": "Not ESG",
}

def normalise_esg(raw) -> str:
    if isinstance(raw, bool):
        return "ESG-Related" if raw else "Not ESG"
    key = safe_str(raw).strip().lower()
    return ESG_NORM.get(key, safe_str(raw).capitalize() if raw else "Not ESG")


def normalise_sentiment(raw) -> str:
    s = safe_str(raw).strip().lower()
    if s in ("none", "", "n/a"):
        return "None"
    return s.capitalize()


# ── builders ───────────────────────────────────────────────────────────────────
def build_predictions_df(records: list) -> pd.DataFrame:
    rows = []
    for r in records:
        if not isinstance(r, dict):
            continue
        prediction_raw = r.get("result", {}).get("prediction", "")
        label, score   = extract_label_score(prediction_raw)
        is_error       = label.startswith("❌")
        parts          = r.get("source", "/").split("/")
        doc            = parts[0] if len(parts) > 0 else ""
        page           = parts[1] if len(parts) > 1 else ""
        rows.append({
            "Timestamp": safe_str(r.get("timestamp", ""))[:19].replace("T", " "),
            "Document":  doc,
            "Page":      page,
            "Model":     r.get("model", ""),
            "Label":     label,
            "Score":     score,
            "Status":    "❌ Error" if is_error else "✅ OK",
        })
    return pd.DataFrame(rows)


def build_absa_df(records: list) -> pd.DataFrame:
    rows = []
    for r in records:
        if not isinstance(r, dict):
            continue
        parts     = r.get("source", "/").split("/")
        doc       = parts[0] if len(parts) > 0 else ""
        page      = parts[1] if len(parts) > 1 else ""
        timestamp = safe_str(r.get("timestamp", ""))[:19].replace("T", " ")
        rule_based = r.get("rule_based", {}) or {}
        hybrid_df  = (r.get("hybrid_model") or {}).get("out_df", []) or []
        raw_metrics = (r.get("hybrid_model") or {}).get("metrics", []) or []
        metrics = {}
        for m in raw_metrics:
            if isinstance(m, dict) and "Metric" in m:
                metrics[m["Metric"]] = m.get("Value", "")

        for sent in hybrid_df:
            if not isinstance(sent, dict):
                continue
            rows.append({
                "Timestamp":          timestamp,
                "Document":           doc,
                "Page":               page,
                "Sentence":           safe_str(sent.get("Sentence_Text", ""), 120),
                "Section":            sent.get("Section", ""),
                "Ontology Path":      sent.get("Ontology_Path", ""),
                "Sentiment (Hybrid)": sent.get("Sentiment_Pred", ""),
                "Tone (Hybrid)":      sent.get("Tone_Pred", ""),
                "Sentiment Score":    round(float(sent.get("sentiment_score") or 0), 4),
                "Tone Score":         round(float(sent.get("tone_score") or 0), 4),
                "Ontology Align":     round(float(sent.get("Ontology_Alignment") or 0), 4),
                "Rule Polarity":      rule_based.get("polarity", ""),
                "Rule Tone":          rule_based.get("tone", ""),
                "Greenwashing Idx":   metrics.get("Greenwashing Index", ""),
                "Ontology Consist.":  metrics.get("Ontology Consistency", ""),
            })
    return pd.DataFrame(rows)


def build_esg_records_df(records: list) -> pd.DataFrame:
    """
    Flatten esg_records.json → one row per sentence-record.
    Handles both prompt variants:
      • data.md       → {text, labels, esg, sentiment}
      • few_shot / zero_shot → {text, aspect, labels, esg, sentiment,
                                sentiment_score, reasoning}
    """
    rows = []
    for r in records:
        if not isinstance(r, dict):
            continue

        parts     = r.get("source", "/").split("/")
        doc       = parts[0] if len(parts) > 0 else ""
        page      = parts[1] if len(parts) > 1 else ""
        timestamp = safe_str(r.get("timestamp", ""))[:19].replace("T", " ")
        model     = r.get("model", "")
        backend   = r.get("backend", "")
        prompt    = r.get("prompt", "")
        ok        = r.get("ok", False)

        inner = r.get("records", [])
        if not isinstance(inner, list) or len(inner) == 0:
            # Surface the error even when records is empty
            rows.append({
                "Timestamp":       timestamp,
                "Document":        doc,
                "Page":            page,
                "Model":           model,
                "Backend":         backend,
                "Prompt":          prompt,
                "Run OK":          "✅ Yes" if ok else "❌ No",
                "Text":            r.get("error", "(no records returned)"),
                "Aspect":          "",
                "Labels":          "",
                "ESG":             "",
                "Sentiment":       "",
                "Sentiment Score": None,
                "Reasoning":       "",
            })
            continue

        for rec in inner:
            if not isinstance(rec, dict):
                continue

            # labels — list or missing
            raw_labels = rec.get("labels", [])
            if isinstance(raw_labels, list):
                label_str = ", ".join(str(l) for l in raw_labels if str(l).lower() != "none")
            else:
                label_str = safe_str(raw_labels)
            label_str = label_str or "—"

            # sentiment score — may be missing in data.md variant
            raw_score = rec.get("sentiment_score")
            try:
                sent_score = round(float(raw_score), 4) if raw_score is not None else None
            except (ValueError, TypeError):
                sent_score = None

            rows.append({
                "Timestamp":       timestamp,
                "Document":        doc,
                "Page":            page,
                "Model":           model,
                "Backend":         backend,
                "Prompt":          prompt,
                "Run OK":          "✅ Yes" if ok else "❌ No",
                "Text":            safe_str(rec.get("text", ""), 160),
                "Aspect":          safe_str(rec.get("aspect", "")).capitalize(),
                "Labels":          label_str,
                "ESG":             normalise_esg(rec.get("esg")),
                "Sentiment":       normalise_sentiment(rec.get("sentiment")),
                "Sentiment Score": sent_score,
                "Reasoning":       safe_str(rec.get("reasoning", ""), 200),
            })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────
pred_records, absa_records, esg_raw_records = [], [], []

try:
    pred_records = load_json(PREDICTIONS_FILE)
except FileNotFoundError:
    st.warning(f"⚠️ `predictions.json` not found at `{PREDICTIONS_FILE}`")
except Exception as e:
    st.error(f"❌ Failed to load predictions.json: {e}")

try:
    absa_records = load_json(ABSA_FILE)
except FileNotFoundError:
    st.warning(f"⚠️ `absa_results.json` not found at `{ABSA_FILE}`")
except Exception as e:
    st.error(f"❌ Failed to load absa_results.json: {e}")

try:
    esg_raw_records = load_json(ESG_RECORDS_FILE)
except FileNotFoundError:
    st.warning(f"⚠️ `esg_records.json` not found at `{ESG_RECORDS_FILE}`")
except Exception as e:
    st.error(f"❌ Failed to load esg_records.json: {e}")

pred_df        = build_predictions_df(pred_records)     if pred_records     else pd.DataFrame()
absa_df        = build_absa_df(absa_records)            if absa_records     else pd.DataFrame()
esg_records_df = build_esg_records_df(esg_raw_records)  if esg_raw_records  else pd.DataFrame()

# ─────────────────────────────────────────────
# Colour helpers  (defined before styling below)
# ─────────────────────────────────────────────
ESG_COLOURS = {
    "Environmental": "background-color: #d4edda; color: #155724;",
    "Social":        "background-color: #cce5ff; color: #004085;",
    "Governance":    "background-color: #fff3cd; color: #856404;",
    "ESG-Related":   "background-color: #e2d9f3; color: #4a235a;",
    "Not ESG":       "background-color: #f8d7da; color: #721c24;",
    "None":          "",
}
SENT_COLOURS = {
    "Positive": "background-color: #d4edda; color: #155724;",
    "Negative": "background-color: #f8d7da; color: #721c24;",
    "Neutral":  "background-color: #fff3cd; color: #856404;",
    "None":     "",
}
STATUS_COLOURS = {
    "✅ OK":  "background-color: #d4edda; color: #155724;",
    "✅ Yes": "background-color: #d4edda; color: #155724;",
    "❌ Error": "background-color: #f8d7da; color: #721c24;",
    "❌ No":    "background-color: #f8d7da; color: #721c24;",
}

def style_status(val):    return STATUS_COLOURS.get(val, "")
def style_esg(val):       return ESG_COLOURS.get(val, "")
def style_sentiment(val): return SENT_COLOURS.get(val, "")

# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

# ── Predictions ───────────────────────────────
st.sidebar.subheader("Table 1 · Predictions")
if not pred_df.empty:
    sel_docs_pred   = st.sidebar.multiselect("Document",  sorted(pred_df["Document"].unique()), default=sorted(pred_df["Document"].unique()), key="p_doc")
    sel_models_pred = st.sidebar.multiselect("Model",     sorted(pred_df["Model"].unique()),    default=sorted(pred_df["Model"].unique()),    key="p_model")
    sel_status_pred = st.sidebar.multiselect("Status",    sorted(pred_df["Status"].unique()),   default=sorted(pred_df["Status"].unique()),   key="p_status")
    filtered_pred   = pred_df[
        pred_df["Document"].isin(sel_docs_pred) &
        pred_df["Model"].isin(sel_models_pred)  &
        pred_df["Status"].isin(sel_status_pred)
    ].reset_index(drop=True)
else:
    filtered_pred = pred_df

# ── ABSA ──────────────────────────────────────
st.sidebar.subheader("Table 2 · ABSA")
if not absa_df.empty:
    sel_docs_absa = st.sidebar.multiselect("Document",  sorted(absa_df["Document"].unique()),            default=sorted(absa_df["Document"].unique()),            key="a_doc")
    sel_sent_absa = st.sidebar.multiselect("Sentiment", sorted(absa_df["Sentiment (Hybrid)"].unique()),  default=sorted(absa_df["Sentiment (Hybrid)"].unique()),  key="a_sent")
    filtered_absa = absa_df[
        absa_df["Document"].isin(sel_docs_absa) &
        absa_df["Sentiment (Hybrid)"].isin(sel_sent_absa)
    ].reset_index(drop=True)
else:
    filtered_absa = absa_df

# ── ESG Records ───────────────────────────────
st.sidebar.subheader("Table 3 · ESG Records")
if not esg_records_df.empty:
    all_docs_esg  = sorted(esg_records_df["Document"].unique())
    all_prompts   = sorted(esg_records_df["Prompt"].unique())
    all_esg_cats  = sorted(esg_records_df["ESG"].unique())
    all_sent_esg  = sorted(esg_records_df["Sentiment"].unique())

    sel_docs_esg  = st.sidebar.multiselect("Document",     all_docs_esg,  default=all_docs_esg,  key="e_doc")
    sel_prompts   = st.sidebar.multiselect("Prompt",       all_prompts,   default=all_prompts,   key="e_prompt")
    sel_esg_cats  = st.sidebar.multiselect("ESG Category", all_esg_cats,  default=all_esg_cats,  key="e_esg")
    sel_sent_esg  = st.sidebar.multiselect("Sentiment",    all_sent_esg,  default=all_sent_esg,  key="e_sent")

    filtered_esg = esg_records_df[
        esg_records_df["Document"].isin(sel_docs_esg) &
        esg_records_df["Prompt"].isin(sel_prompts)    &
        esg_records_df["ESG"].isin(sel_esg_cats)      &
        esg_records_df["Sentiment"].isin(sel_sent_esg)
    ].reset_index(drop=True)
else:
    filtered_esg = esg_records_df

# ─────────────────────────────────────────────
# TABLE 1 — Predictions
# ─────────────────────────────────────────────
st.subheader("📊 Table 1 · Model Predictions")

if filtered_pred.empty:
    st.info("No prediction records to display.")
else:
    total   = len(filtered_pred)
    ok_n    = (filtered_pred["Status"] == "✅ OK").sum()
    err_n   = (filtered_pred["Status"] == "❌ Error").sum()
    success = round(ok_n / total * 100, 1) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",  f"{total:,}")
    c2.metric("✅ Successful",  f"{ok_n:,}")
    c3.metric("❌ Errors",      f"{err_n:,}")
    c4.metric("Success Rate",   f"{success}%")

    styled_pred = (
        filtered_pred.style
        .applymap(style_status, subset=["Status"])
        .format({"Score": lambda v: f"{v:.4f}" if pd.notna(v) and v is not None else "—"})
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled_pred, use_container_width=True, height=420)
    st.download_button("⬇️ Download Predictions CSV",
                       filtered_pred.to_csv(index=False),
                       file_name="predictions_table.csv", mime="text/csv")

st.markdown("---")

# ─────────────────────────────────────────────
# TABLE 2 — ABSA Results
# ─────────────────────────────────────────────
st.subheader("🧠 Table 2 · ABSA Results (Sentence-Level)")

if filtered_absa.empty:
    st.info("No ABSA records to display.")
else:
    avg_sent_sc = filtered_absa["Sentiment Score"].mean()
    gw_vals     = pd.to_numeric(
        filtered_absa["Greenwashing Idx"].replace("", pd.NA), errors="coerce"
    ).dropna()
    avg_gw = gw_vals.mean() if not gw_vals.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sentences",      f"{len(filtered_absa):,}")
    c2.metric("Pages Covered",        filtered_absa["Page"].nunique())
    c3.metric("Avg Sentiment Score",  f"{avg_sent_sc:.4f}")
    c4.metric("Avg Greenwashing Idx", f"{avg_gw:.4f}")

    display_cols_absa = [
        "Timestamp", "Document", "Page", "Sentence",
        "Section", "Ontology Path",
        "Sentiment (Hybrid)", "Tone (Hybrid)",
        "Sentiment Score", "Tone Score", "Ontology Align",
        "Rule Polarity", "Rule Tone",
        "Greenwashing Idx", "Ontology Consist.",
    ]
    # Only keep columns that exist (guards against empty hybrid_model)
    display_cols_absa = [c for c in display_cols_absa if c in filtered_absa.columns]

    styled_absa = (
        filtered_absa[display_cols_absa].style
        .applymap(style_sentiment, subset=["Sentiment (Hybrid)"])
        .applymap(style_sentiment, subset=["Rule Polarity"])
        .format({
            "Sentiment Score": "{:.4f}",
            "Tone Score":      "{:.4f}",
            "Ontology Align":  "{:.4f}",
        })
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled_absa, use_container_width=True, height=480)
    st.download_button("⬇️ Download ABSA CSV",
                       filtered_absa[display_cols_absa].to_csv(index=False),
                       file_name="absa_table.csv", mime="text/csv")

st.markdown("---")

# ─────────────────────────────────────────────
# TABLE 3 — ESG Records
# ─────────────────────────────────────────────
st.subheader("🌿 Table 3 · ESG Extracted Records")

if filtered_esg.empty:
    st.info("No ESG records to display.")
else:
    total_recs   = len(filtered_esg)
    esg_counts   = filtered_esg["ESG"].value_counts()
    sent_counts  = filtered_esg["Sentiment"].value_counts()
    prompt_counts = filtered_esg["Prompt"].value_counts()

    # ── Summary metrics ───────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",   f"{total_recs:,}")
    c2.metric("Pages Covered",   filtered_esg["Page"].nunique())
    c3.metric("ESG Categories",  filtered_esg["ESG"].nunique())
    c4.metric("Prompts Used",    filtered_esg["Prompt"].nunique())

    # ── Breakdown panels ──────────────────────
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        st.markdown("**ESG Category Breakdown**")
        st.dataframe(
            esg_counts.reset_index().rename(columns={"index": "ESG", "ESG": "Count"}),
            use_container_width=True, hide_index=True,
        )
    with bc2:
        st.markdown("**Sentiment Breakdown**")
        st.dataframe(
            sent_counts.reset_index().rename(columns={"index": "Sentiment", "Sentiment": "Count"}),
            use_container_width=True, hide_index=True,
        )
    with bc3:
        st.markdown("**Prompt Breakdown**")
        st.dataframe(
            prompt_counts.reset_index().rename(columns={"index": "Prompt", "Prompt": "Count"}),
            use_container_width=True, hide_index=True,
        )

    # ── Main table ────────────────────────────
    esg_display_cols = [
        "Timestamp", "Document", "Page",
        "Model", "Backend", "Prompt",
        "Run OK", "Text", "Aspect", "Labels",
        "ESG", "Sentiment", "Sentiment Score", "Reasoning",
    ]
    # Guard: only show columns that actually exist
    esg_display_cols = [c for c in esg_display_cols if c in filtered_esg.columns]

    fmt = {}
    if "Sentiment Score" in filtered_esg.columns:
        fmt["Sentiment Score"] = lambda v: f"{v:.4f}" if pd.notna(v) and v is not None else "—"

    styled_esg = (
        filtered_esg[esg_display_cols].style
        .applymap(style_esg,       subset=["ESG"]       if "ESG"       in esg_display_cols else [])
        .applymap(style_sentiment, subset=["Sentiment"] if "Sentiment" in esg_display_cols else [])
        .applymap(style_status,    subset=["Run OK"]    if "Run OK"    in esg_display_cols else [])
        .format(fmt)
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled_esg, use_container_width=True, height=520)
    st.download_button(
        "⬇️ Download ESG Records CSV",
        filtered_esg[esg_display_cols].to_csv(index=False),
        file_name="esg_records_table.csv", mime="text/csv",
    )

    # ── Reasoning viewer (full text, no truncation) ───────────────────────────
    if "Reasoning" in filtered_esg.columns:
        with st.expander("🔍 Full Reasoning Viewer", expanded=False):
            sel_idx = st.number_input(
                "Row index (0-based)", min_value=0,
                max_value=max(0, total_recs - 1), value=0, step=1,
            )
            row = filtered_esg.iloc[int(sel_idx)]
            st.markdown(f"**Text:** {row.get('Text', '')}")
            st.markdown(f"**ESG:** `{row.get('ESG', '')}` | **Sentiment:** `{row.get('Sentiment', '')}`")
            st.markdown(f"**Labels:** {row.get('Labels', '')}")
            st.markdown(f"**Reasoning:**\n\n{row.get('Reasoning', '(none)')}")

st.markdown("---")
st.caption("ESG Results Viewer — predictions.json · absa_results.json · esg_records.json")