import streamlit as st
import json
import re
import html
import pandas as pd
from pathlib import Path

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
RESULTS_DIR    = Path(__file__).resolve().parents[1] / "results"
DATASET_DIR    = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"
PREDICTIONS_FILE = RESULTS_DIR / "predictions.json"
ABSA_FILE        = RESULTS_DIR / "absa_results.json"
ESG_RECORDS_FILE = RESULTS_DIR / "esg_records.json"

# ─────────────────────────────────────────────
# Colour Palettes
# ─────────────────────────────────────────────
ESG_HIGHLIGHT = {
    "Environmental": ("🟢", "#d4edda", "#155724"),
    "Social":        ("🔵", "#cce5ff", "#004085"),
    "Governance":    ("🟡", "#fff3cd", "#856404"),
    "ESG-Related":   ("🟣", "#e2d9f3", "#4a235a"),
    "Not ESG":       ("⚪", "#f8f9fa", "#6c757d"),
    "None":          ("⚪", "#f8f9fa", "#6c757d"),
}
SENT_HIGHLIGHT = {
    "Positive": ("#d4edda", "#155724"),
    "Negative": ("#f8d7da", "#721c24"),
    "Neutral":  ("#fff3cd", "#856404"),
    "Unknown":  ("#f8f9fa", "#6c757d"),
    "None":     ("#f8f9fa", "#6c757d"),
}
PRED_LABEL_COLOURS = {
    "yes":        ("#d4edda", "#155724"),
    "no":         ("#f8d7da", "#721c24"),
    "neutral":    ("#fff3cd", "#856404"),
    "positive":   ("#d4edda", "#155724"),
    "negative":   ("#f8d7da", "#721c24"),
    "transition": ("#cce5ff", "#004085"),
    "physical":   ("#f8d7da", "#721c24"),
    "specific":   ("#d4edda", "#155724"),
    "vague":      ("#fff3cd", "#856404"),
}

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


ESG_NORM = {
    "environmental": "Environmental", "social": "Social",
    "governance": "Governance", "e": "Environmental",
    "s": "Social", "g": "Governance", "n": "Not ESG",
    "none": "Not ESG", "true": "ESG-Related", "false": "Not ESG",
}

def normalise_esg(raw) -> str:
    if isinstance(raw, bool):
        return "ESG-Related" if raw else "Not ESG"
    key = safe_str(raw).strip().lower()
    return ESG_NORM.get(key, safe_str(raw).capitalize() if raw else "Not ESG")


def normalise_sentiment(raw) -> str:
    s = safe_str(raw).strip().lower()
    return "None" if s in ("none", "", "n/a") else s.capitalize()


def read_page_text(source: str) -> str:
    """Load the original .md page text from thesis_dataset."""
    parts = source.split("/")
    if len(parts) < 2:
        return ""
    doc_folder = DATASET_DIR / parts[0] / "pages" / parts[1]
    if doc_folder.exists():
        return doc_folder.read_text(encoding="utf-8")
    return ""


def _badge(text: str, bg: str, fg: str) -> str:
    return (
        f'<span style="background:{bg};color:{fg};padding:1px 6px;'
        f'border-radius:4px;font-size:11px;font-weight:600;'
        f'white-space:nowrap;">{html.escape(str(text))}</span>'
    )


def highlight_text_html(
    original: str,
    matches: list[dict],          # list of {"text", "bg", "fg", "badges": [...]}
    context_chars: int = 0,
) -> str:
    """
    Build an HTML string where every matched span is highlighted.
    matches: sorted by descending length so longer spans win.
    """
    escaped_original = original

    # Sort longest match first to avoid partial overlaps
    sorted_matches = sorted(matches, key=lambda m: len(m["text"]), reverse=True)

    # Replace each matched text with a highlighted version
    used_ranges: list[tuple[int, int]] = []

    result_html = html.escape(escaped_original)

    for m in sorted_matches:
        needle = m["text"].strip()
        if not needle or len(needle) < 4:
            continue

        escaped_needle = html.escape(needle)
        if escaped_needle not in result_html:
            continue

        badge_html = " ".join(m.get("badges", []))
        replacement = (
            f'<mark style="background:{m["bg"]};color:{m["fg"]};'
            f'padding:2px 4px;border-radius:3px;font-weight:500;">'
            f'{escaped_needle}'
            f'</mark>'
            f'<sup style="margin-left:2px;">{badge_html}</sup>'
        )
        result_html = result_html.replace(escaped_needle, replacement, 1)

    # Preserve newlines
    result_html = result_html.replace("\n", "<br>")
    return result_html


def extract_pred_label(prediction_str: str) -> tuple[str, float | None]:
    if not isinstance(prediction_str, str):
        return "", None
    lines = prediction_str.strip().splitlines()
    for line in reversed(lines):
        if ":" in line:
            parts = line.rsplit(":", 1)
            label = parts[0].strip()
            try:
                score = round(float(parts[1].strip()), 3)
                return label, score
            except ValueError:
                pass
    return "", None


# ─────────────────────────────────────────────
# Load JSON Files
# ─────────────────────────────────────────────
pred_records, absa_records, esg_records = [], [], []

try:
    pred_records = load_json(PREDICTIONS_FILE)
except FileNotFoundError:
    st.warning("⚠️ predictions.json not found")

try:
    absa_records = load_json(ABSA_FILE)
except FileNotFoundError:
    st.warning("⚠️ absa_results.json not found")

try:
    esg_records = load_json(ESG_RECORDS_FILE)
except FileNotFoundError:
    st.warning("⚠️ esg_records.json not found")

# ─────────────────────────────────────────────
# Build source → records index
# ─────────────────────────────────────────────
# predictions: source → list of {model, label, score}
pred_by_source: dict[str, list] = {}
for r in pred_records:
    src = r.get("source", "")
    label, score = extract_pred_label(
        (r.get("result") or {}).get("prediction", "")
    )
    pred_by_source.setdefault(src, []).append({
        "model": r.get("model", ""),
        "label": label,
        "score": score,
        "text":  r.get("text", ""),
    })

# absa: source → list of sentence dicts
absa_by_source: dict[str, list] = {}
for r in absa_records:
    src = r.get("source", "")
    sentences = (r.get("hybrid_model") or {}).get("out_df", []) or []
    rule_based = r.get("rule_based", {}) or {}
    absa_by_source.setdefault(src, []).append({
        "sentences": sentences,
        "rule_polarity": rule_based.get("polarity", ""),
    })

# esg: source → list of {prompt, records[]}
esg_by_source: dict[str, list] = {}
for r in esg_records:
    src = r.get("source", "")
    esg_by_source.setdefault(src, []).append({
        "prompt":  r.get("prompt", ""),
        "model":   r.get("model", ""),
        "records": r.get("records", []),
    })

all_sources = sorted(
    set(list(pred_by_source) + list(absa_by_source) + list(esg_by_source))
)

# ─────────────────────────────────────────────
# Sidebar — Source Selector
# ─────────────────────────────────────────────
st.sidebar.header("📄 Source Selector")

if not all_sources:
    st.error("No sources found in any result file.")
    st.stop()

# Group sources by document
doc_map: dict[str, list] = {}
for s in all_sources:
    doc = s.split("/")[0]
    doc_map.setdefault(doc, []).append(s)

selected_doc  = st.sidebar.selectbox("Document", sorted(doc_map))
selected_page = st.sidebar.selectbox("Page", doc_map[selected_doc])

st.sidebar.markdown("---")
st.sidebar.header("👁️ Display Options")

show_predictions = st.sidebar.checkbox("Show Predictions (Table 1)", value=True)
show_absa        = st.sidebar.checkbox("Show ABSA (Table 2)",        value=True)
show_esg         = st.sidebar.checkbox("Show ESG Records (Table 3)", value=True)
highlight_mode   = st.sidebar.radio(
    "Highlight by",
    ["ESG Category", "Sentiment", "Both"],
    index=2,
)

# ─────────────────────────────────────────────
# Load original page text
# ─────────────────────────────────────────────
original_text = read_page_text(selected_page)
source_key    = selected_page

# ─────────────────────────────────────────────
# LAYOUT — two columns: highlights left, tables right
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════
# LEFT — Highlighted Source Text
# ══════════════════════════════════════════════
with left_col:
    st.subheader("📄 Source Text with Highlights")

    if not original_text:
        st.warning(
            f"⚠️ Could not load source file for `{source_key}`.\n\n"
            f"Expected path: `{DATASET_DIR / selected_doc / 'pages' / selected_page.split('/')[-1]}`"
        )
    else:
        # ── Build match list from ESG records ────────────────────────────
        matches: list[dict] = []

        if show_esg and source_key in esg_by_source:
            for run in esg_by_source[source_key]:
                for rec in run.get("records", []):
                    if not isinstance(rec, dict):
                        continue
                    txt  = safe_str(rec.get("text", "")).strip()
                    esg  = normalise_esg(rec.get("esg"))
                    sent = normalise_sentiment(rec.get("sentiment"))

                    if not txt or esg == "Not ESG":
                        continue

                    esg_bg  = ESG_HIGHLIGHT.get(esg, ESG_HIGHLIGHT["None"])[1]
                    esg_fg  = ESG_HIGHLIGHT.get(esg, ESG_HIGHLIGHT["None"])[2]
                    sent_bg = SENT_HIGHLIGHT.get(sent, SENT_HIGHLIGHT["None"])[0]
                    sent_fg = SENT_HIGHLIGHT.get(sent, SENT_HIGHLIGHT["None"])[1]

                    if highlight_mode == "ESG Category":
                        bg, fg = esg_bg, esg_fg
                    elif highlight_mode == "Sentiment":
                        bg, fg = sent_bg, sent_fg
                    else:
                        bg, fg = esg_bg, esg_fg  # ESG colour, badges show sentiment

                    esg_icon  = ESG_HIGHLIGHT.get(esg, ESG_HIGHLIGHT["None"])[0]
                    badges    = [
                        _badge(f"{esg_icon} {esg}", esg_bg, esg_fg),
                        _badge(f"💬 {sent}", sent_bg, sent_fg),
                    ]
                    matches.append({"text": txt, "bg": bg, "fg": fg, "badges": badges})

        if show_absa and source_key in absa_by_source:
            for run in absa_by_source[source_key]:
                for sent_row in run.get("sentences", []):
                    if not isinstance(sent_row, dict):
                        continue
                    txt  = safe_str(sent_row.get("Sentence_Text", "")).strip()
                    sent = sent_row.get("Sentiment_Pred", "Neutral")
                    if not txt or len(txt) < 6:
                        continue
                    bg, fg = SENT_HIGHLIGHT.get(sent, SENT_HIGHLIGHT["None"])
                    score  = sent_row.get("sentiment_score", 0)
                    badges = [_badge(f"🧠 {sent} ({score:.2f})", bg, fg)]
                    matches.append({"text": txt, "bg": bg, "fg": fg, "badges": badges})

        highlighted_html = highlight_text_html(original_text, matches)

        # ── Legend ────────────────────────────────────────────────────────
        legend_parts = []
        for cat, (icon, bg, fg) in ESG_HIGHLIGHT.items():
            if cat in ("Not ESG", "None"):
                continue
            legend_parts.append(_badge(f"{icon} {cat}", bg, fg))
        for sent, (bg, fg) in SENT_HIGHLIGHT.items():
            if sent in ("None", "Unknown"):
                continue
            legend_parts.append(_badge(f"💬 {sent}", bg, fg))

        st.markdown(
            "<div style='margin-bottom:8px;display:flex;flex-wrap:wrap;gap:4px;'>"
            + " ".join(legend_parts)
            + "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="
                background:#fafafa;
                border:1px solid #e0e0e0;
                border-radius:8px;
                padding:16px;
                font-size:13px;
                line-height:1.8;
                max-height:700px;
                overflow-y:auto;
                font-family: 'Segoe UI', sans-serif;
            ">
            {highlighted_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"✅ {len([m for m in matches if m['text']])} span(s) matched "
            f"out of original {len(original_text.splitlines())} lines"
        )

# ══════════════════════════════════════════════
# RIGHT — Data Tables
# ══════════════════════════════════════════════
with right_col:

    # ── TABLE 1 · Predictions ─────────────────────────────────────────────
    if show_predictions:
        st.subheader("📊 Table 1 · Model Predictions")

        pred_list = pred_by_source.get(source_key, [])
        if not pred_list:
            st.info("No predictions for this page.")
        else:
            pred_rows = []
            for p in pred_list:
                lbl_lower  = safe_str(p["label"]).lower()
                lbl_colors = next(
                    (v for k, v in PRED_LABEL_COLOURS.items() if k in lbl_lower),
                    ("#f8f9fa", "#6c757d"),
                )
                pred_rows.append({
                    "Model": p["model"],
                    "Label": p["label"],
                    "Score": p["score"],
                })
            pred_df = pd.DataFrame(pred_rows)

            def _colour_pred_label(val):
                lv = safe_str(val).lower()
                for k, (bg, fg) in PRED_LABEL_COLOURS.items():
                    if k in lv:
                        return f"background-color:{bg};color:{fg}"
                return ""

            styled = (
                pred_df.style
                .applymap(_colour_pred_label, subset=["Label"])
                .format({"Score": lambda v: f"{v:.4f}" if v is not None else "—"})
                .set_properties(**{"font-size": "12px"})
            )
            st.dataframe(styled, use_container_width=True, height=300)

        st.markdown("---")

    # ── TABLE 2 · ABSA ───────────────────────────────────────────────────
    if show_absa:
        st.subheader("🧠 Table 2 · ABSA Sentences")

        absa_list = absa_by_source.get(source_key, [])
        if not absa_list:
            st.info("No ABSA results for this page.")
        else:
            absa_rows = []
            for run in absa_list:
                for s in run.get("sentences", []):
                    absa_rows.append({
                        "ID":             s.get("Sentence_ID", ""),
                        "Sentence":       safe_str(s.get("Sentence_Text", ""), 80),
                        "Sentiment":      s.get("Sentiment_Pred", ""),
                        "Tone":           s.get("Tone_Pred", ""),
                        "Sent Score":     round(float(s.get("sentiment_score") or 0), 4),
                        "Ontology":       s.get("Ontology_Path", ""),
                        "Align":          round(float(s.get("Ontology_Alignment") or 0), 4),
                    })
            if absa_rows:
                absa_df = pd.DataFrame(absa_rows)

                def _colour_sentiment(val):
                    bg, fg = SENT_HIGHLIGHT.get(val, ("#f8f9fa", "#6c757d"))
                    return f"background-color:{bg};color:{fg}"

                styled_absa = (
                    absa_df.style
                    .applymap(_colour_sentiment, subset=["Sentiment"])
                    .format({"Sent Score": "{:.4f}", "Align": "{:.4f}"})
                    .set_properties(**{"font-size": "12px"})
                )
                st.dataframe(styled_absa, use_container_width=True, height=300)

        st.markdown("---")

    # ── TABLE 3 · ESG Records ────────────────────────────────────────────
    if show_esg:
        st.subheader("🌿 Table 3 · ESG Extracted Records")

        esg_list = esg_by_source.get(source_key, [])
        if not esg_list:
            st.info("No ESG records for this page.")
        else:
            # Prompt selector
            prompts_available = [run["prompt"] for run in esg_list]
            selected_prompt   = st.selectbox(
                "Prompt variant", prompts_available, key="esg_prompt_sel"
            )
            run_data = next(
                (r for r in esg_list if r["prompt"] == selected_prompt), esg_list[0]
            )

            esg_rows = []
            for rec in run_data.get("records", []):
                if not isinstance(rec, dict):
                    continue
                raw_labels = rec.get("labels", [])
                label_str  = (
                    ", ".join(str(l) for l in raw_labels if str(l).lower() != "none")
                    if isinstance(raw_labels, list)
                    else safe_str(raw_labels)
                ) or "—"

                raw_score = rec.get("sentiment_score")
                try:
                    sent_score = round(float(raw_score), 4) if raw_score is not None else None
                except (ValueError, TypeError):
                    sent_score = None

                esg_rows.append({
                    "Text":      safe_str(rec.get("text", ""), 100),
                    "Aspect":    safe_str(rec.get("aspect", "")).capitalize(),
                    "ESG":       normalise_esg(rec.get("esg")),
                    "Sentiment": normalise_sentiment(rec.get("sentiment")),
                    "Score":     sent_score,
                    "Labels":    label_str,
                    "Reasoning": safe_str(rec.get("reasoning", ""), 120),
                })

            if esg_rows:
                esg_df = pd.DataFrame(esg_rows)

                def _colour_esg(val):
                    info = ESG_HIGHLIGHT.get(val, ("", "#f8f9fa", "#6c757d"))
                    return f"background-color:{info[1]};color:{info[2]}"

                def _colour_sent(val):
                    bg, fg = SENT_HIGHLIGHT.get(val, ("#f8f9fa", "#6c757d"))
                    return f"background-color:{bg};color:{fg}"

                fmt = {}
                if "Score" in esg_df.columns:
                    fmt["Score"] = lambda v: f"{v:.4f}" if pd.notna(v) and v is not None else "—"

                styled_esg = (
                    esg_df.style
                    .applymap(_colour_esg,  subset=["ESG"])
                    .applymap(_colour_sent, subset=["Sentiment"])
                    .format(fmt)
                    .set_properties(**{"font-size": "12px"})
                )
                st.dataframe(styled_esg, use_container_width=True, height=340)

                # ── Reasoning detail viewer ───────────────────────────────
                with st.expander("🔍 Full Reasoning Viewer", expanded=False):
                    sel = st.number_input(
                        "Row", 0, max(0, len(esg_rows) - 1), 0, key="esg_row_sel"
                    )
                    row = esg_df.iloc[int(sel)]
                    esg_info  = ESG_HIGHLIGHT.get(row["ESG"], ("", "#f8f9fa", "#6c757d"))
                    sent_info = SENT_HIGHLIGHT.get(row["Sentiment"], ("#f8f9fa", "#6c757d"))
                    st.markdown(
                        f"**Text:** {row['Text']}\n\n"
                        + " ".join([
                            _badge(f"{esg_info[0]} {row['ESG']}", esg_info[1], esg_info[2]),
                            _badge(f"💬 {row['Sentiment']}", sent_info[0], sent_info[1]),
                        ])
                        + f"\n\n**Labels:** `{row['Labels']}`"
                        + f"\n\n**Reasoning:** {row.get('Reasoning', '(none)')}",
                        unsafe_allow_html=True,
                    )

st.markdown("---")
st.caption("ESG Highlight Viewer — matches extracted records against original source pages")