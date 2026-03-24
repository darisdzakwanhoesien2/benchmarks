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
        return json.load(f)


def extract_label_score(prediction_str: str) -> tuple[str, float | None]:
    if not isinstance(prediction_str, str):
        return str(prediction_str), None
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


def build_predictions_df(records: list) -> pd.DataFrame:
    rows = []
    for r in records:
        prediction_raw = r.get("result", {}).get("prediction", "")
        label, score   = extract_label_score(prediction_raw)
        is_error       = label.startswith("❌")
        doc, page      = (r.get("source", "/").split("/") + [""])[:2]
        rows.append({
            "Timestamp": r.get("timestamp", "")[:19].replace("T", " "),
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
        doc, page  = (r.get("source", "/").split("/") + [""])[:2]
        timestamp  = r.get("timestamp", "")[:19].replace("T", " ")
        rule_based = r.get("rule_based", {})
        hybrid_df  = r.get("hybrid_model", {}).get("out_df", [])
        metrics    = {
            m["Metric"]: m["Value"]
            for m in r.get("hybrid_model", {}).get("metrics", [])
        }
        for sent in hybrid_df:
            rows.append({
                "Timestamp":          timestamp,
                "Document":           doc,
                "Page":               page,
                "Sentence":           sent.get("Sentence_Text", "")[:120],
                "Section":            sent.get("Section", ""),
                "Ontology Path":      sent.get("Ontology_Path", ""),
                "Sentiment (Hybrid)": sent.get("Sentiment_Pred", ""),
                "Tone (Hybrid)":      sent.get("Tone_Pred", ""),
                "Sentiment Score":    round(sent.get("sentiment_score", 0), 4),
                "Tone Score":         round(sent.get("tone_score", 0), 4),
                "Ontology Align":     round(sent.get("Ontology_Alignment", 0), 4),
                "Rule Polarity":      rule_based.get("polarity", ""),
                "Rule Tone":          rule_based.get("tone", ""),
                "Greenwashing Idx":   metrics.get("Greenwashing Index", ""),
                "Ontology Consist.":  metrics.get("Ontology Consistency", ""),
            })
    return pd.DataFrame(rows)


def build_esg_records_df(records: list) -> pd.DataFrame:
    """Flatten esg_records.json → one row per extracted record (sentence)."""
    rows = []
    for r in records:
        doc, page  = (r.get("source", "/").split("/") + [""])[:2]
        timestamp  = r.get("timestamp", "")[:19].replace("T", " ")
        model      = r.get("model", "")
        ok         = r.get("ok", False)

        for rec in r.get("records", []):
            # esg field can be "Governance" / "Social" / "Environmental" / True / False
            esg_raw = rec.get("esg", "")
            if isinstance(esg_raw, bool):
                esg_val = "ESG-Related" if esg_raw else "Not ESG"
            else:
                esg_val = str(esg_raw) if esg_raw else "Not ESG"

            labels = rec.get("labels", [])

            rows.append({
                "Timestamp":  timestamp,
                "Document":   doc,
                "Page":       page,
                "Model":      model,
                "Run OK":     "✅ Yes" if ok else "❌ No",
                "Text":       rec.get("text", "")[:150],
                "Labels":     ", ".join(labels) if labels else "—",
                "ESG":        esg_val,
                "Sentiment":  rec.get("sentiment", "").capitalize(),
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

try:
    absa_records = load_json(ABSA_FILE)
except FileNotFoundError:
    st.warning(f"⚠️ `absa_results.json` not found at `{ABSA_FILE}`")

try:
    esg_raw_records = load_json(ESG_RECORDS_FILE)
except FileNotFoundError:
    st.warning(f"⚠️ `esg_records.json` not found at `{ESG_RECORDS_FILE}`")

pred_df       = build_predictions_df(pred_records)    if pred_records     else pd.DataFrame()
absa_df       = build_absa_df(absa_records)           if absa_records     else pd.DataFrame()
esg_records_df = build_esg_records_df(esg_raw_records) if esg_raw_records else pd.DataFrame()

# ─────────────────────────────────────────────
# Sidebar Filters
# ─────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

# ── Predictions filters ───────────────────────
st.sidebar.subheader("Table 1 · Predictions")
if not pred_df.empty:
    all_docs_pred   = sorted(pred_df["Document"].unique())
    all_models_pred = sorted(pred_df["Model"].unique())
    all_status_pred = sorted(pred_df["Status"].unique())

    sel_docs_pred   = st.sidebar.multiselect("Document",  all_docs_pred,   default=all_docs_pred,   key="p_doc")
    sel_models_pred = st.sidebar.multiselect("Model",     all_models_pred, default=all_models_pred, key="p_model")
    sel_status_pred = st.sidebar.multiselect("Status",    all_status_pred, default=all_status_pred, key="p_status")

    mask_pred = (
        pred_df["Document"].isin(sel_docs_pred) &
        pred_df["Model"].isin(sel_models_pred)  &
        pred_df["Status"].isin(sel_status_pred)
    )
    filtered_pred = pred_df[mask_pred].reset_index(drop=True)
else:
    filtered_pred = pred_df

# ── ABSA filters ──────────────────────────────
st.sidebar.subheader("Table 2 · ABSA")
if not absa_df.empty:
    all_docs_absa = sorted(absa_df["Document"].unique())
    all_sent_absa = sorted(absa_df["Sentiment (Hybrid)"].unique())

    sel_docs_absa = st.sidebar.multiselect("Document",  all_docs_absa, default=all_docs_absa, key="a_doc")
    sel_sent_absa = st.sidebar.multiselect("Sentiment", all_sent_absa, default=all_sent_absa, key="a_sent")

    mask_absa = (
        absa_df["Document"].isin(sel_docs_absa) &
        absa_df["Sentiment (Hybrid)"].isin(sel_sent_absa)
    )
    filtered_absa = absa_df[mask_absa].reset_index(drop=True)
else:
    filtered_absa = absa_df

# ── ESG Records filters ───────────────────────
st.sidebar.subheader("Table 3 · ESG Records")
if not esg_records_df.empty:
    all_docs_esg  = sorted(esg_records_df["Document"].unique())
    all_esg_cats  = sorted(esg_records_df["ESG"].unique())
    all_sent_esg  = sorted(esg_records_df["Sentiment"].unique())

    sel_docs_esg  = st.sidebar.multiselect("Document",  all_docs_esg,  default=all_docs_esg,  key="e_doc")
    sel_esg_cats  = st.sidebar.multiselect("ESG Category", all_esg_cats, default=all_esg_cats, key="e_esg")
    sel_sent_esg  = st.sidebar.multiselect("Sentiment", all_sent_esg,  default=all_sent_esg,  key="e_sent")

    mask_esg = (
        esg_records_df["Document"].isin(sel_docs_esg)  &
        esg_records_df["ESG"].isin(sel_esg_cats)       &
        esg_records_df["Sentiment"].isin(sel_sent_esg)
    )
    filtered_esg = esg_records_df[mask_esg].reset_index(drop=True)
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
    ok      = (filtered_pred["Status"] == "✅ OK").sum()
    errors  = (filtered_pred["Status"] == "❌ Error").sum()
    success = round(ok / total * 100, 1) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",   f"{total:,}")
    c2.metric("✅ Successful",   f"{ok:,}")
    c3.metric("❌ Errors",       f"{errors:,}")
    c4.metric("Success Rate",    f"{success}%")

    def style_status(val):
        if val == "✅ OK":
            return "background-color: #d4edda; color: #155724;"
        elif val == "❌ Error":
            return "background-color: #f8d7da; color: #721c24;"
        return ""

    styled_pred = (
        filtered_pred.style
        .applymap(style_status, subset=["Status"])
        .format({"Score": lambda v: f"{v:.4f}" if v is not None else "—"})
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled_pred, use_container_width=True, height=420)
    st.download_button(
        "⬇️ Download Predictions CSV",
        filtered_pred.to_csv(index=False),
        file_name="predictions_table.csv",
        mime="text/csv",
    )

st.markdown("---")

# ─────────────────────────────────────────────
# TABLE 2 — ABSA Results
# ─────────────────────────────────────────────
st.subheader("🧠 Table 2 · ABSA Results (Sentence-Level)")

if filtered_absa.empty:
    st.info("No ABSA records to display.")
else:
    total_sents  = len(filtered_absa)
    unique_pages = filtered_absa["Page"].nunique()
    avg_sent_sc  = filtered_absa["Sentiment Score"].mean()
    gw_vals      = filtered_absa["Greenwashing Idx"].replace("", pd.NA).dropna()
    avg_gw       = gw_vals.astype(float).mean() if not gw_vals.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sentences",     f"{total_sents:,}")
    c2.metric("Pages Covered",       unique_pages)
    c3.metric("Avg Sentiment Score", f"{avg_sent_sc:.4f}")
    c4.metric("Avg Greenwashing Idx",f"{avg_gw:.4f}")

    SENT_COLOURS = {
        "Positive": "background-color: #d4edda; color: #155724;",
        "Negative": "background-color: #f8d7da; color: #721c24;",
        "Neutral":  "background-color: #fff3cd; color: #856404;",
    }

    def style_sentiment(val):
        return SENT_COLOURS.get(val, "")

    display_cols = [
        "Timestamp", "Document", "Page", "Sentence",
        "Section", "Ontology Path",
        "Sentiment (Hybrid)", "Tone (Hybrid)",
        "Sentiment Score", "Tone Score",
        "Ontology Align", "Rule Polarity", "Rule Tone",
        "Greenwashing Idx", "Ontology Consist.",
    ]

    styled_absa = (
        filtered_absa[display_cols].style
        .applymap(style_sentiment, subset=["Sentiment (Hybrid)", "Rule Polarity"])
        .format({
            "Sentiment Score": "{:.4f}",
            "Tone Score":      "{:.4f}",
            "Ontology Align":  "{:.4f}",
        })
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled_absa, use_container_width=True, height=480)
    st.download_button(
        "⬇️ Download ABSA CSV",
        filtered_absa[display_cols].to_csv(index=False),
        file_name="absa_table.csv",
        mime="text/csv",
    )

st.markdown("---")

# ─────────────────────────────────────────────
# TABLE 3 — ESG Records
# ─────────────────────────────────────────────
st.subheader("🌿 Table 3 · ESG Extracted Records")

if filtered_esg.empty:
    st.info("No ESG records to display.")
else:
    total_recs    = len(filtered_esg)
    unique_pages  = filtered_esg["Page"].nunique()
    esg_counts    = filtered_esg["ESG"].value_counts()
    sent_counts   = filtered_esg["Sentiment"].value_counts()

    # ── Summary metrics ───────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",  f"{total_recs:,}")
    c2.metric("Pages Covered",  unique_pages)
    c3.metric("ESG Categories", filtered_esg["ESG"].nunique())
    c4.metric("Unique Labels",
              filtered_esg["Labels"]
              .str.split(", ").explode()
              .nunique())

    # ── ESG & Sentiment breakdown ─────────────
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown("**ESG Category Breakdown**")
        st.dataframe(
            esg_counts.reset_index().rename(columns={"index": "ESG Category", "ESG": "Count"}),
            use_container_width=True,
            hide_index=True,
        )
    with bc2:
        st.markdown("**Sentiment Breakdown**")
        st.dataframe(
            sent_counts.reset_index().rename(columns={"index": "Sentiment", "Sentiment": "Count"}),
            use_container_width=True,
            hide_index=True,
        )

    # ── ESG colour map ────────────────────────
    ESG_COLOURS = {
        "Environmental": "background-color: #d4edda; color: #155724;",
        "Social":        "background-color: #cce5ff; color: #004085;",
        "Governance":    "background-color: #fff3cd; color: #856404;",
        "ESG-Related":   "background-color: #e2d9f3; color: #4a235a;",
        "Not ESG":       "background-color: #f8d7da; color: #721c24;",
    }

    def style_esg(val):
        return ESG_COLOURS.get(val, "")

    SENTIMENT_COLOURS = {
        "Positive": "background-color: #d4edda; color: #155724;",
        "Negative": "background-color: #f8d7da; color: #721c24;",
        "Neutral":  "background-color: #fff3cd; color: #856404;",
    }

    def style_esg_sentiment(val):
        return SENTIMENT_COLOURS.get(val, "")

    esg_display_cols = [
        "Timestamp", "Document", "Page", "Model",
        "Run OK", "Text", "Labels", "ESG", "Sentiment",
    ]

    styled_esg = (
        filtered_esg[esg_display_cols].style
        .applymap(style_esg,           subset=["ESG"])
        .applymap(style_esg_sentiment, subset=["Sentiment"])
        .applymap(style_status,        subset=["Run OK"])
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled_esg, use_container_width=True, height=480)
    st.download_button(
        "⬇️ Download ESG Records CSV",
        filtered_esg[esg_display_cols].to_csv(index=False),
        file_name="esg_records_table.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption("ESG Results Viewer — predictions.json · absa_results.json · esg_records.json")