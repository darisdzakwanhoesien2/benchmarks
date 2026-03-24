import streamlit as st
import json
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
RESULTS_DIR      = Path(__file__).resolve().parents[1] / "results"
DATASET_DIR      = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"
PREDICTIONS_FILE = RESULTS_DIR / "predictions.json"
ABSA_FILE        = RESULTS_DIR / "absa_results.json"
ESG_RECORDS_FILE = RESULTS_DIR / "esg_records.json"

# ─────────────────────────────────────────────
# Table identity colours  ← NEW
# ─────────────────────────────────────────────
TABLE_META = {
    "T1": {"label": "T1 · Predictions", "bg": "#343a40", "fg": "#ffffff", "icon": "📊"},
    "T2": {"label": "T2 · ABSA",        "bg": "#0d6efd", "fg": "#ffffff", "icon": "🧠"},
    "T3": {"label": "T3 · ESG Records", "bg": "#198754", "fg": "#ffffff", "icon": "🌿"},
}

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
    parts = source.split("/")
    if len(parts) < 2:
        return ""
    path = DATASET_DIR / parts[0] / "pages" / parts[1]
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _badge(text: str, bg: str, fg: str, bold: bool = False) -> str:
    fw = "700" if bold else "600"
    return (
        f'<span style="background:{bg};color:{fg};padding:1px 7px;'
        f'border-radius:4px;font-size:11px;font-weight:{fw};'
        f'white-space:nowrap;display:inline-block;">'
        f'{html.escape(str(text))}</span>'
    )


def _table_badge(table_id: str) -> str:
    """Render a bold table-source badge e.g. 📊 T1."""
    m = TABLE_META[table_id]
    return _badge(f'{m["icon"]} {table_id}', m["bg"], m["fg"], bold=True)


def highlight_text_html(original: str, matches: list[dict]) -> str:
    """
    Highlight matched spans in the original text.
    Each match: {text, bg, fg, badges: [html_str]}
    Longer matches win over shorter overlapping ones.
    """
    result_html = html.escape(original)
    sorted_matches = sorted(matches, key=lambda m: len(m["text"]), reverse=True)

    for m in sorted_matches:
        needle = m["text"].strip()
        if not needle or len(needle) < 4:
            continue
        escaped_needle = html.escape(needle)
        if escaped_needle not in result_html:
            continue

        badge_html = "&nbsp;".join(m.get("badges", []))
        replacement = (
            f'<mark style="background:{m["bg"]};color:{m["fg"]};'
            f'padding:2px 5px;border-radius:3px;font-weight:500;">'
            f'{escaped_needle}'
            f'</mark>'
            f'<sup style="margin-left:3px;vertical-align:top;">{badge_html}</sup>'
        )
        result_html = result_html.replace(escaped_needle, replacement, 1)

    return result_html.replace("\n", "<br>")


def extract_pred_label(prediction_str: str) -> tuple[str, float | None]:
    if not isinstance(prediction_str, str):
        return "", None
    for line in reversed(prediction_str.strip().splitlines()):
        if ":" in line:
            parts = line.rsplit(":", 1)
            try:
                return parts[0].strip(), round(float(parts[1].strip()), 3)
            except ValueError:
                pass
    return "", None


# ─────────────────────────────────────────────
# Load Data
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
pred_by_source: dict[str, list] = {}
for r in pred_records:
    src = r.get("source", "")
    label, score = extract_pred_label((r.get("result") or {}).get("prediction", ""))
    pred_by_source.setdefault(src, []).append({
        "model": r.get("model", ""),
        "label": label,
        "score": score,
        "text":  r.get("text", ""),
    })

absa_by_source: dict[str, list] = {}
for r in absa_records:
    src = r.get("source", "")
    sentences  = (r.get("hybrid_model") or {}).get("out_df", []) or []
    rule_based = r.get("rule_based", {}) or {}
    absa_by_source.setdefault(src, []).append({
        "sentences":     sentences,
        "rule_polarity": rule_based.get("polarity", ""),
    })

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
# Sidebar
# ─────────────────────────────────────────────
st.sidebar.header("📄 Source Selector")

if not all_sources:
    st.error("No sources found in any result file.")
    st.stop()

doc_map: dict[str, list] = {}
for s in all_sources:
    doc_map.setdefault(s.split("/")[0], []).append(s)

selected_doc  = st.sidebar.selectbox("Document", sorted(doc_map))
selected_page = st.sidebar.selectbox("Page", doc_map[selected_doc])
source_key    = selected_page

st.sidebar.markdown("---")
st.sidebar.header("👁️ Display Options")

show_predictions = st.sidebar.checkbox("Show Predictions (T1)", value=True)
show_absa        = st.sidebar.checkbox("Show ABSA (T2)",        value=True)
show_esg         = st.sidebar.checkbox("Show ESG Records (T3)", value=True)
highlight_mode   = st.sidebar.radio(
    "Highlight colour by",
    ["ESG Category", "Sentiment", "Table Source"],
    index=2,
)

st.sidebar.markdown("---")
st.sidebar.header("🎨 Table Legend")
for tid, meta in TABLE_META.items():
    st.sidebar.markdown(
        _badge(f'{meta["icon"]} {meta["label"]}', meta["bg"], meta["fg"], bold=True),
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Load source text
# ─────────────────────────────────────────────
original_text = read_page_text(source_key)

# ─────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════
# LEFT — Highlighted Source Text
# ══════════════════════════════════════════════
with left_col:
    st.subheader("📄 Source Text with Highlights")

    if not original_text:
        st.warning(
            f"⚠️ Could not load `{source_key}`.\n\n"
            f"Expected: `{DATASET_DIR / selected_doc / 'pages' / source_key.split('/')[-1]}`"
        )
    else:
        matches: list[dict] = []

        # ── T3 · ESG Records ─────────────────────────────────────────────
        if show_esg and source_key in esg_by_source:
            for run in esg_by_source[source_key]:
                for rec in run.get("records", []):
                    if not isinstance(rec, dict):
                        continue
                    txt  = safe_str(rec.get("text", "")).strip()
                    esg  = normalise_esg(rec.get("esg"))
                    sent = normalise_sentiment(rec.get("sentiment"))
                    if not txt or len(txt) < 4:
                        continue

                    esg_bg,  esg_fg  = ESG_HIGHLIGHT.get(esg,  ESG_HIGHLIGHT["None"])[1:]
                    sent_bg, sent_fg = SENT_HIGHLIGHT.get(sent, SENT_HIGHLIGHT["None"])

                    if highlight_mode == "ESG Category":
                        bg, fg = esg_bg, esg_fg
                    elif highlight_mode == "Sentiment":
                        bg, fg = sent_bg, sent_fg
                    else:  # Table Source
                        bg, fg = TABLE_META["T3"]["bg"], TABLE_META["T3"]["fg"]

                    esg_icon = ESG_HIGHLIGHT.get(esg, ESG_HIGHLIGHT["None"])[0]
                    badges = [
                        _table_badge("T3"),
                        _badge(f"{esg_icon} {esg}", esg_bg, esg_fg),
                        _badge(f"💬 {sent}", sent_bg, sent_fg),
                    ]
                    matches.append({"text": txt, "bg": bg, "fg": fg, "badges": badges})

        # ── T2 · ABSA ────────────────────────────────────────────────────
        if show_absa and source_key in absa_by_source:
            for run in absa_by_source[source_key]:
                for s in run.get("sentences", []):
                    if not isinstance(s, dict):
                        continue
                    txt  = safe_str(s.get("Sentence_Text", "")).strip()
                    sent = s.get("Sentiment_Pred", "Neutral")
                    if not txt or len(txt) < 6:
                        continue

                    sent_bg, sent_fg = SENT_HIGHLIGHT.get(sent, SENT_HIGHLIGHT["None"])
                    score = s.get("sentiment_score", 0)

                    if highlight_mode == "Table Source":
                        bg, fg = TABLE_META["T2"]["bg"], TABLE_META["T2"]["fg"]
                    elif highlight_mode == "Sentiment":
                        bg, fg = sent_bg, sent_fg
                    else:
                        bg, fg = sent_bg, sent_fg

                    badges = [
                        _table_badge("T2"),
                        _badge(f"💬 {sent} ({score:.2f})", sent_bg, sent_fg),
                    ]
                    matches.append({"text": txt, "bg": bg, "fg": fg, "badges": badges})

        # ── T1 · Predictions  (whole-page text, shown as border note) ────
        # Predictions apply to the whole page — we show them as a header
        # bar rather than inline highlights (no sentence-level text spans)
        pred_list = pred_by_source.get(source_key, [])
        if show_predictions and pred_list:
            pred_parts = []
            for p in pred_list:
                lbl       = safe_str(p["label"])
                lbl_lower = lbl.lower()
                lbl_bg, lbl_fg = next(
                    (v for k, v in PRED_LABEL_COLOURS.items() if k in lbl_lower),
                    ("#f8f9fa", "#6c757d"),
                )
                score_str = f" ({p['score']:.3f})" if p["score"] is not None else ""
                pred_parts.append(
                    _table_badge("T1")
                    + "&nbsp;"
                    + _badge(f"{p['model']}", "#6c757d", "#fff")
                    + "&nbsp;"
                    + _badge(f"{lbl}{score_str}", lbl_bg, lbl_fg)
                )
            st.markdown(
                "<div style='margin-bottom:10px;padding:8px 12px;"
                "background:#f8f9fa;border-left:4px solid #343a40;"
                "border-radius:4px;display:flex;flex-wrap:wrap;gap:6px;'>"
                + "<br>".join(pred_parts)
                + "</div>",
                unsafe_allow_html=True,
            )

        # ── Colour legend ────────────────────────────────────────────────
        legend_items = []

        # Table-source legend
        for tid, meta in TABLE_META.items():
            show = (
                (tid == "T1" and show_predictions) or
                (tid == "T2" and show_absa)        or
                (tid == "T3" and show_esg)
            )
            if show:
                legend_items.append(
                    _badge(f'{meta["icon"]} {meta["label"]}', meta["bg"], meta["fg"], bold=True)
                )

        legend_items.append("&nbsp;|&nbsp;")

        # ESG category legend
        for cat, (icon, bg, fg) in ESG_HIGHLIGHT.items():
            if cat not in ("Not ESG", "None"):
                legend_items.append(_badge(f"{icon} {cat}", bg, fg))

        legend_items.append("&nbsp;|&nbsp;")

        # Sentiment legend
        for sent, (bg, fg) in SENT_HIGHLIGHT.items():
            if sent not in ("None", "Unknown"):
                legend_items.append(_badge(f"💬 {sent}", bg, fg))

        st.markdown(
            "<div style='margin-bottom:10px;display:flex;flex-wrap:wrap;"
            "align-items:center;gap:4px;font-size:12px;'>"
            + " ".join(legend_items)
            + "</div>",
            unsafe_allow_html=True,
        )

        # ── Highlighted text block ────────────────────────────────────────
        highlighted_html = highlight_text_html(original_text, matches)

        t2_count = sum(1 for m in matches if m["bg"] == TABLE_META["T2"]["bg"] or
                       any("T2" in b for b in m.get("badges", [])))
        t3_count = sum(1 for m in matches if m["bg"] == TABLE_META["T3"]["bg"] or
                       any("T3" in b for b in m.get("badges", [])))

        st.markdown(
            f"""
            <div style="
                background:#fafafa;border:1px solid #e0e0e0;
                border-radius:8px;padding:16px;
                font-size:13px;line-height:2.0;
                max-height:680px;overflow-y:auto;
                font-family:'Segoe UI',sans-serif;
            ">{highlighted_html}</div>
            """,
            unsafe_allow_html=True,
        )

        # ── Match stats ───────────────────────────────────────────────────
        stat_cols = st.columns(3)
        stat_cols[0].metric("📊 T1 Predictions", len(pred_list))
        stat_cols[1].metric("🧠 T2 ABSA Spans",  t2_count)
        stat_cols[2].metric("🌿 T3 ESG Spans",   t3_count)

# ══════════════════════════════════════════════
# RIGHT — Data Tables
# ══════════════════════════════════════════════
with right_col:

    # ── TABLE 1 · Predictions ─────────────────────────────────────────────
    if show_predictions:
        tm = TABLE_META["T1"]
        st.markdown(
            _badge(f'{tm["icon"]} {tm["label"]}', tm["bg"], tm["fg"], bold=True),
            unsafe_allow_html=True,
        )

        pred_list = pred_by_source.get(source_key, [])
        if not pred_list:
            st.info("No predictions for this page.")
        else:
            pred_rows = [
                {"Model": p["model"], "Label": p["label"], "Score": p["score"]}
                for p in pred_list
            ]
            pred_df = pd.DataFrame(pred_rows)

            def _colour_pred_label(val):
                lv = safe_str(val).lower()
                for k, (bg, fg) in PRED_LABEL_COLOURS.items():
                    if k in lv:
                        return f"background-color:{bg};color:{fg}"
                return ""

            st.dataframe(
                pred_df.style
                .applymap(_colour_pred_label, subset=["Label"])
                .format({"Score": lambda v: f"{v:.4f}" if v is not None else "—"})
                .set_properties(**{"font-size": "12px"}),
                use_container_width=True,
                height=260,
            )
        st.markdown("---")

    # ── TABLE 2 · ABSA ───────────────────────────────────────────────────
    if show_absa:
        tm = TABLE_META["T2"]
        st.markdown(
            _badge(f'{tm["icon"]} {tm["label"]}', tm["bg"], tm["fg"], bold=True),
            unsafe_allow_html=True,
        )

        absa_list = absa_by_source.get(source_key, [])
        if not absa_list:
            st.info("No ABSA results for this page.")
        else:
            absa_rows = []
            for run in absa_list:
                for s in run.get("sentences", []):
                    absa_rows.append({
                        "Sentence":   safe_str(s.get("Sentence_Text", ""), 80),
                        "Sentiment":  s.get("Sentiment_Pred", ""),
                        "Tone":       s.get("Tone_Pred", ""),
                        "Sent Score": round(float(s.get("sentiment_score") or 0), 4),
                        "Ontology":   s.get("Ontology_Path", ""),
                        "Align":      round(float(s.get("Ontology_Alignment") or 0), 4),
                    })
            if absa_rows:
                def _colour_sentiment(val):
                    bg, fg = SENT_HIGHLIGHT.get(val, ("#f8f9fa", "#6c757d"))
                    return f"background-color:{bg};color:{fg}"

                st.dataframe(
                    pd.DataFrame(absa_rows).style
                    .applymap(_colour_sentiment, subset=["Sentiment"])
                    .format({"Sent Score": "{:.4f}", "Align": "{:.4f}"})
                    .set_properties(**{"font-size": "12px"}),
                    use_container_width=True,
                    height=280,
                )
        st.markdown("---")

    # ── TABLE 3 · ESG Records ────────────────────────────────────────────
    if show_esg:
        tm = TABLE_META["T3"]
        st.markdown(
            _badge(f'{tm["icon"]} {tm["label"]}', tm["bg"], tm["fg"], bold=True),
            unsafe_allow_html=True,
        )

        esg_list = esg_by_source.get(source_key, [])
        if not esg_list:
            st.info("No ESG records for this page.")
        else:
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
                    if isinstance(raw_labels, list) else safe_str(raw_labels)
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

                st.dataframe(
                    esg_df.style
                    .applymap(_colour_esg,  subset=["ESG"])
                    .applymap(_colour_sent, subset=["Sentiment"])
                    .format(fmt)
                    .set_properties(**{"font-size": "12px"}),
                    use_container_width=True,
                    height=340,
                )

                with st.expander("🔍 Full Reasoning Viewer", expanded=False):
                    sel = st.number_input("Row", 0, max(0, len(esg_rows) - 1), 0, key="esg_row_sel")
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