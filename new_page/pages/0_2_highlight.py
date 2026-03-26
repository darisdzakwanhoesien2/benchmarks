import json
import os
import sys
import re
from pathlib import Path
from typing import Optional

import streamlit as st

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ESG Highlight Viewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 ESG Detection Highlight Viewer")
st.markdown("Match extracted ESG records back to the original source text.")
st.markdown("---")

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
RESULTS_DIR      = Path(__file__).resolve().parents[1] / "results"
DATASET_DIR      = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"
PREDICTIONS_FILE = RESULTS_DIR / "predictions.json"
ABSA_FILE        = RESULTS_DIR / "absa_results.json"
ESG_RECORDS_FILE = RESULTS_DIR / "esg_records.json"

# ─────────────────────────────────────────────
# Colour Palettes
# ─────────────────────────────────────────────
ESG_COLORS = {
    "Environmental": "#d4edda",
    "Social":        "#cce5ff",
    "Governance":    "#fff3cd",
    "Unknown":       "#f8f9fa",
}
SENTIMENT_COLORS = {
    "Positive": "#28a745",
    "Negative": "#dc3545",
    "Neutral":  "#6c757d",
}

# ─────────────────────────────────────────────
# Helpers — load JSON safely
# ─────────────────────────────────────────────
def load_json(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else [data]
    except Exception as e:
        st.warning(f"⚠️ Could not load `{path.name}`: {e}")
        return []


# ─────────────────────────────────────────────
# Helpers — normalise stored df formats
# ─────────────────────────────────────────────
def normalise_df(raw) -> list[dict]:
    """
    Accepts three formats saved in JSON:
      1. list of dicts  → [{"col": val}, ...]           (ideal)
      2. dict of dicts  → {"col": {"0": val, "1": val}} (pandas to_dict() default)
      3. None / "None" / empty                          → []
    Always returns a list of row-dicts.
    """
    if not raw or raw == "None":
        return []
    if isinstance(raw, list):
        return [r for r in raw if isinstance(r, dict)]
    if isinstance(raw, dict):
        if not raw:
            return []
        cols = list(raw.keys())
        if not all(isinstance(raw[c], dict) for c in cols):
            return []
        indices = list(raw[cols[0]].keys())
        return [{c: raw[c].get(idx) for c in cols} for idx in indices]
    return []


def extract_pred_label(prediction: str) -> tuple[str, float]:
    """Return (label, score) from a prediction string like 'yes (0.92)'."""
    if not prediction:
        return ("—", 0.0)
    m = re.search(r"([\w\s]+)\s*\(([\d.]+)\)", str(prediction))
    if m:
        return (m.group(1).strip(), float(m.group(2)))
    return (str(prediction).strip(), 0.0)


# ─────────────────────────────────────────────
# Load result files
# ─────────────────────────────────────────────
pred_records = load_json(PREDICTIONS_FILE)
absa_records = load_json(ABSA_FILE)
esg_records  = load_json(ESG_RECORDS_FILE)

# ─────────────────────────────────────────────
# Build source → records index
# ─────────────────────────────────────────────

# T1: predictions — always has single "source" field
pred_by_source: dict[str, list] = {}
for r in pred_records:
    src = r.get("source", "")
    if not src:
        continue
    label, score = extract_pred_label(
        (r.get("result") or {}).get("prediction", "")
    )
    pred_by_source.setdefault(src, []).append({
        "model": r.get("model", ""),
        "label": label,
        "score": score,
        "text":  r.get("text", ""),
    })

# T2: absa — always has single "source" field
# normalise hybrid_model.out_df regardless of pandas serialisation format
absa_by_source: dict[str, list] = {}
for r in absa_records:
    src = r.get("source", "")
    if not src:
        continue
    sentences  = normalise_df((r.get("hybrid_model") or {}).get("out_df"))
    rule_based = r.get("rule_based", {}) or {}
    absa_by_source.setdefault(src, []).append({
        "sentences":     sentences,
        "rule_polarity": rule_based.get("polarity", ""),
    })

# T3: esg_records — TWO formats must be handled:
#
#   OLD (llm_setup_with_context.py — per-page calls):
#     { "source": "SCM_2023_sr-scma_pdf/page_0025.md", "records": [...] }
#
#   NEW (0_3_combined_features.py — per-model call, multi-page context):
#     { "targeted_pages": ["SCM_.../page_0025.md", "SCM_.../page_0026.md"], "records": [...] }
#
# We fan-out each record to every page it covers so the page selector works.
esg_by_source: dict[str, list] = {}
for r in esg_records:
    entry = {
        "prompt":  r.get("prompt", ""),
        "model":   r.get("model", ""),
        "records": r.get("records", []),
    }

    # ── NEW format: targeted_pages list ───────────────────────────────────
    targeted = r.get("targeted_pages")
    if isinstance(targeted, list) and targeted:
        for page_src in targeted:
            if page_src:
                esg_by_source.setdefault(page_src, []).append(entry)
        continue

    # ── OLD format: single source string ──────────────────────────────────
    src = r.get("source", "")
    if src:
        esg_by_source.setdefault(src, []).append(entry)

# Union of all known sources
all_sources = sorted(
    set(list(pred_by_source) + list(absa_by_source) + list(esg_by_source))
)

# ─────────────────────────────────────────────
# Sidebar — Source Selector
# ─────────────────────────────────────────────
st.sidebar.header("📄 Source Selector")

if not all_sources:
    st.error(
        "No sources found in any result file. "
        "Run the pipeline first (T1 / T2 / T3)."
    )
    st.stop()

# Group by document (first path component)
doc_map: dict[str, list] = {}
for s in all_sources:
    doc = s.split("/")[0]
    doc_map.setdefault(doc, []).append(s)

# ── Document-level badge showing which pipelines ran ──────────────────────────
def doc_badges(doc: str) -> str:
    pages = doc_map[doc]
    parts = []
    if any(p in pred_by_source for p in pages): parts.append("T1")
    if any(p in absa_by_source for p in pages): parts.append("T2")
    if any(p in esg_by_source  for p in pages): parts.append("T3")
    # FIX: use "/" as a variable, not inside the f-string quotes
    sep = "/"
    return f"[{sep.join(parts)}]" if parts else "[no data]"

doc_options = sorted(doc_map.keys())
doc_labels  = [f"{d}  {doc_badges(d)}" for d in doc_options]

selected_doc_label = st.sidebar.selectbox(
    "Document", doc_labels, key="doc_selectbox"
)
selected_doc = doc_options[doc_labels.index(selected_doc_label)]

# ── Page-level badge showing record counts per pipeline ───────────────────────
def page_badges(page: str) -> str:
    parts = []
    if page in pred_by_source:
        parts.append(f"T1:{len(pred_by_source[page])}")
    if page in absa_by_source:
        parts.append(f"T2:{len(absa_by_source[page])}")
    if page in esg_by_source:
        parts.append(f"T3:{len(esg_by_source[page])}")
    sep = ", "
    return f" [{sep.join(parts)}]" if parts else " [—]"

page_options = doc_map[selected_doc]
page_labels  = [
    f"{p.split('/')[-1]}{page_badges(p)}" for p in page_options
]

selected_page_label = st.sidebar.selectbox(
    "Page", page_labels, key="page_selectbox"
)
selected_page = page_options[page_labels.index(selected_page_label)]

# ── Data availability summary for selected page ───────────────────────────────
with st.sidebar:
    st.divider()
    n_pred = len(pred_by_source.get(selected_page, []))
    n_absa = len(absa_by_source.get(selected_page, []))
    n_esg  = len(esg_by_source.get(selected_page, []))
    st.markdown(
        f"**Data for `{selected_page.split('/')[-1]}`**\n\n"
        f"- 📊 T1 predictions: **{n_pred}**\n"
        f"- 🧠 T2 ABSA runs:   **{n_absa}**\n"
        f"- 🌿 T3 ESG runs:    **{n_esg}**"
    )
    if n_pred == 0 and n_absa == 0 and n_esg == 0:
        st.warning("⚠️ No pipeline results for this page yet.")

# ─────────────────────────────────────────────
# Load original source text
# ─────────────────────────────────────────────
source_text = ""
parts       = selected_page.split("/")
if len(parts) == 2:
    doc_name, page_file = parts
    page_path = DATASET_DIR / doc_name / "pages" / page_file
    if page_path.exists():
        source_text = page_path.read_text(encoding="utf-8")
    else:
        st.warning(f"⚠️ Source file not found: `{page_path}`")

# ─────────────────────────────────────────────
# Main — T1 Predictions
# ─────────────────────────────────────────────
st.subheader("📊 T1 · ClimateBERT Predictions")
t1_data = pred_by_source.get(selected_page, [])
if not t1_data:
    st.info("No T1 predictions for this page.")
else:
    for row in t1_data:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"`{row['model']}`")
        col2.markdown(f"**{row['label']}**")
        col3.markdown(f"`{row['score']:.2f}`")

# ─────────────────────────────────────────────
# Main — T2 ABSA
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🧠 T2 · ABSA Sentences")
t2_data = absa_by_source.get(selected_page, [])
if not t2_data:
    st.info("No T2 ABSA results for this page.")
else:
    for run_idx, run in enumerate(t2_data):
        with st.expander(f"Run {run_idx + 1} · polarity: {run['rule_polarity']}", expanded=run_idx == 0):
            sentences = run.get("sentences", [])
            if not sentences:
                st.info("No sentences extracted.")
            else:
                for s in sentences:
                    tone      = s.get("Tone", s.get("tone", ""))
                    sent_text = s.get("Sentence_Text", s.get("text", str(s)))
                    color     = SENTIMENT_COLORS.get(str(tone).capitalize(), "#6c757d")
                    st.markdown(
                        f'<span style="border-left:4px solid {color};padding-left:8px">'
                        f"{sent_text}</span>",
                        unsafe_allow_html=True,
                    )

# ─────────────────────────────────────────────
# Main — T3 ESG Records
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("🌿 T3 · ESG Extracted Records")
t3_data = esg_by_source.get(selected_page, [])
if not t3_data:
    st.info("No T3 ESG records for this page.")
else:
    for run_idx, run in enumerate(t3_data):
        label = f"Run {run_idx + 1} · {run['model']} · prompt: {run['prompt']}"
        with st.expander(label, expanded=run_idx == 0):
            records = run.get("records", [])
            if not records:
                st.info("No records extracted.")
            else:
                for rec in records:
                    esg_cat   = rec.get("esg",       rec.get("category",   "Unknown"))
                    sentiment = rec.get("sentiment", rec.get("tone",        "Neutral"))
                    text_val  = rec.get("text",      rec.get("sentence",    ""))
                    bg        = ESG_COLORS.get(esg_cat, ESG_COLORS["Unknown"])
                    fg        = SENTIMENT_COLORS.get(
                        str(sentiment).capitalize(), "#6c757d"
                    )
                    st.markdown(
                        f'<div style="background:{bg};border-left:5px solid {fg};'
                        f'padding:8px 12px;margin-bottom:6px;border-radius:4px">'
                        f'<strong>{esg_cat}</strong> · '
                        f'<em style="color:{fg}">{sentiment}</em><br>{text_val}'
                        f"</div>",
                        unsafe_allow_html=True,
                    )

# ─────────────────────────────────────────────
# Main — Original Source Text
# ─────────────────────────────────────────────
st.markdown("---")
st.subheader("📄 Original Source Text")
if source_text:
    with st.expander("View source text", expanded=False):
        st.text(source_text)
else:
    st.info("Source text not available.")