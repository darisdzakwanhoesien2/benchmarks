import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import json
import os
import re

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(page_title="Parsed ESG JSON Dashboard", layout="wide")
st.title("📊 ESG Parsed Sentence-Level Dashboard")
add_page_explanation(__file__)

# -------------------------------------------------------
# Load CSV
# -------------------------------------------------------
st.caption(f"Using data: `{DATA_PATH}`")

# --- Dataset selection from config/dataset.json ---
from pathlib import Path
dataset_config_path = Path(__file__).resolve().parents[1] / "config" / "dataset.json"
datasets = []
import json
if dataset_config_path.exists():
    with open(dataset_config_path) as f:
        config = json.load(f)
        datasets = config.get("datasets", [])

dataset_names = [d["name"] for d in datasets]
dataset_choice = None
selected_file = None

if dataset_names:
    dataset_choice = st.sidebar.selectbox("Select a dataset", ["(Upload your own)"] + dataset_names)
    if dataset_choice != "(Upload your own)":
        selected = next((d for d in datasets if d["name"] == dataset_choice), None)
        if selected:
            selected_file = selected["filepath"]

uploaded_file = st.sidebar.file_uploader("Or upload your CSV file", type=["csv"])

if selected_file:
    raw_df = pd.read_csv(selected_file)
    st.sidebar.success(f"Loaded dataset: {selected_file}")
elif uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    st.sidebar.success("Loaded uploaded file")
else:
    st.info("Please select a dataset or upload a CSV file.")
    st.stop()

# =======================================================
# ROBUST JSON PARSING (NEW)
# =======================================================

def extract_json_block(text):
    """
    Extract the first JSON array or object from messy LLM output.
    """
    if not isinstance(text, str):
        return None

    match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(1))
    except Exception:
        return None


def normalize_json(obj):
    """
    Normalize JSON into flat list of dicts.
    Handles dicts, lists, nested lists.
    """
    if obj is None:
        return []

    if isinstance(obj, dict):
        return [obj]

    if isinstance(obj, list):
        flat = []
        for item in obj:
            flat.extend(normalize_json(item))
        return flat

    return []


def is_valid_esg_object(d):
    """
    Minimal ESG validation.
    """
    return (
        isinstance(d, dict)
        and "sentence" in d
        and "aspect" in d
    )


def parse_esg_json(text):
    """
    End-to-end robust ESG JSON parser.
    """
    raw = extract_json_block(text)
    normalized = normalize_json(raw)
    validated = [x for x in normalized if is_valid_esg_object(x)]
    return validated


# -------------------------------------------------------
# Parse JSON annotations (UPDATED)
# -------------------------------------------------------
@st.cache_data
def parse_annotations(df):
    df = df.copy()
    df["parsed"] = df["text"].apply(parse_esg_json)

    exploded = df.explode("parsed", ignore_index=True)
    parsed_df = pd.json_normalize(exploded["parsed"])

    meta_cols = [c for c in df.columns if c != "parsed"]
    meta = exploded[meta_cols].reset_index(drop=True)

    full = pd.concat([meta, parsed_df], axis=1)
    return full


df = parse_annotations(raw_df)

st.success(f"Parsed **{len(df)}** ESG sentence records")

# -------------------------------------------------------
# Helper: Parse provider
# -------------------------------------------------------
def parse_provider(m):
    if isinstance(m, str) and "/" in m:
        return m.split("/")[0]
    return "unknown"

df["provider"] = df["model"].apply(parse_provider)

# -------------------------------------------------------
# Helper: Ensure pivot contains ALL models
# -------------------------------------------------------
def ensure_all_models(reference_df, pivot):
    all_models = sorted(reference_df["model"].dropna().unique())
    for m in all_models:
        if m not in pivot.columns:
            pivot[m] = None
    return pivot[all_models]

# -------------------------------------------------------
# Helper: completeness scoring
# -------------------------------------------------------
def model_completeness(df_pdf, df_page):
    expected = sorted(df_pdf["model"].dropna().unique())
    present = sorted(df_page["model"].dropna().unique())
    missing = set(expected) - set(present)

    score = len(present) / len(expected) if expected else 1.0

    return {
        "expected": expected,
        "present": present,
        "missing": sorted(missing),
        "missing_count": len(missing),
        "present_count": len(present),
        "total": len(expected),
        "score": score
    }

# -------------------------------------------------------
# Sidebar Filters
# -------------------------------------------------------
st.sidebar.header("🔍 Filters")

def make_multiselect(label, col):
    if col not in df.columns:
        return None
    vals = sorted(df[col].dropna().unique())
    return st.sidebar.multiselect(label, vals, default=vals)

aspect_cats = make_multiselect("Aspect Category", "aspect_category")
sentiments = make_multiselect("Sentiment", "sentiment")
tones = make_multiselect("Tone", "tone")
materialities = make_multiselect("Materiality", "materiality")
stakeholders = make_multiselect("Stakeholder", "stakeholder")
value_chain_stage = make_multiselect("Value Chain Stage", "value_chain_stage")
time_horizon = make_multiselect("Time Horizon", "time_horizon")

if "confidence" in df.columns:
    conf_range = st.sidebar.slider(
        "Confidence Range",
        0.0, 1.0,
        (float(df["confidence"].min()), float(df["confidence"].max())),
        0.01,
    )
else:
    conf_range = None

filtered = df.copy()

def apply_filter(col, values):
    global filtered
    if values and col in filtered.columns:
        filtered = filtered[filtered[col].isin(values)]

apply_filter("aspect_category", aspect_cats)
apply_filter("sentiment", sentiments)
apply_filter("tone", tones)
apply_filter("materiality", materialities)
apply_filter("stakeholder", stakeholders)
apply_filter("value_chain_stage", value_chain_stage)
apply_filter("time_horizon", time_horizon)

if conf_range:
    lo, hi = conf_range
    filtered = filtered[(filtered["confidence"] >= lo) & (filtered["confidence"] <= hi)]

st.caption(f"Showing **{len(filtered)}** sentences after filtering.")

# -------------------------------------------------------
# Tabs
# -------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Distributions",
    "📌 Aspects",
    "📄 Sentence Table",
    "🤖 Model Comparison",
    "LLM Breakdown",
    "🧮 Model Coverage",
    "📦 Raw JSON View",
    "📊 Grounding Audit"
])


# -------------------------------------------------------
# TAB 1 — Distributions
# -------------------------------------------------------
with tab1:
    st.subheader("Sentiment Distribution")
    add_section_explanation("Sentiment Distribution")
    st.bar_chart(filtered["sentiment"].value_counts())

    st.subheader("Aspect Category Distribution")
    add_section_explanation("Aspect Category Distribution")
    st.bar_chart(filtered["aspect_category"].value_counts())

# -------------------------------------------------------
# TAB 2 — Aspects
# -------------------------------------------------------
with tab2:
    st.subheader("Top Aspects")
    add_section_explanation("Top Aspects")
    if "aspect" in filtered:
        n = st.slider("Show Top N", 3, 30, 10)
        topA = filtered["aspect"].value_counts().head(n)
        st.bar_chart(topA)
        st.dataframe(topA.rename("count"))

# -------------------------------------------------------
# TAB 3 — Sentence Table
# -------------------------------------------------------
with tab3:
    st.subheader("Full Sentence Table")
    add_section_explanation("Full Sentence Table")
    wanted = [
        "sentence","aspect","aspect_category","sentiment","sentiment_score",
        "tone","materiality","stakeholder","impact_level","time_horizon",
        "filename","page_number","model"
    ]
    show_cols = [c for c in wanted if c in filtered.columns]
    st.dataframe(filtered[show_cols], use_container_width=True)

# -------------------------------------------------------
# TAB 4 — Model Comparison (ORIGINAL vs HIGHLIGHTED MARKDOWN)
# -------------------------------------------------------
with tab4:
    st.subheader("🤖 LLM Model Comparison (Grounded & Auditable)")
    add_section_explanation("🤖 LLM Model Comparison (Grounded & Auditable)")

    # ---------------------------------------------------
    # File & Page Selection
    # ---------------------------------------------------
    filenames = sorted(filtered["filename"].unique())
    selected_file = st.selectbox("Filename", filenames, key="mc_file")

    pages = sorted(
        filtered[filtered["filename"] == selected_file]["page_number"].unique()
    )
    selected_page = st.selectbox("Page Number", pages, key="mc_page")

    subset = filtered[
        (filtered["filename"] == selected_file) &
        (filtered["page_number"] == selected_page)
    ]

    if subset.empty:
        st.warning("No data for this file & page.")
        st.stop()

    # ---------------------------------------------------
    # Model Completeness
    # ---------------------------------------------------
    df_pdf = filtered[filtered["filename"] == selected_file]
    comp = model_completeness(df_pdf, subset)

    st.metric(
        "Model Completeness",
        f"{comp['score']*100:.1f}%",
        help=f"Present: {comp['present_count']} / {comp['total']}"
    )

    if comp["missing_count"] > 0:
        st.warning(f"Missing models: {', '.join(comp['missing'])}")

    # ---------------------------------------------------
    # Sentence Index (GLOBAL FOR THIS PAGE)
    # ---------------------------------------------------
    sentences = list(dict.fromkeys(subset["sentence"].dropna().tolist()))
    sentence_index = {s: i + 1 for i, s in enumerate(sentences)}

    # ---------------------------------------------------
    # Highlight Helper
    # ---------------------------------------------------
    def highlight_sentences(text, sentence_index):
        if not isinstance(text, str):
            return ""

        highlighted = text
        for sentence, idx in sentence_index.items():
            if sentence in highlighted:
                highlighted = highlighted.replace(
                    sentence,
                    f"<span style='background-color:#fff59d; padding:2px; "
                    f"border-radius:4px; font-weight:500;'>"
                    f"[{idx}] {sentence}"
                    f"</span>"
                )
        return highlighted

    # ---------------------------------------------------
    # Extract Page-Level Markdown (same for all models)
    # ---------------------------------------------------
    row0 = subset.iloc[0]

    md_full = row0.get("markdown_full", "")
    md_clean = row0.get("cleaned_markdown", "")

    # ---------------------------------------------------
    # MARKDOWN VISUALIZATION
    # ---------------------------------------------------
    st.markdown("## 📄 Source Text vs Highlighted ESG Sentences")
    add_section_explanation("## 📄 Source Text vs Highlighted ESG Sentences")

    # ---- markdown_full ----
    st.markdown("### 🧾 markdown_full")
    add_section_explanation("### 🧾 markdown_full")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original**")
        st.markdown(md_full if md_full else "_No markdown_full_", unsafe_allow_html=True)

    with col2:
        st.markdown("**Highlighted**")
        st.markdown(
            highlight_sentences(md_full, sentence_index),
            unsafe_allow_html=True
        )

    # ---- cleaned_markdown ----
    st.markdown("### ✂️ cleaned_markdown")
    add_section_explanation("### ✂️ cleaned_markdown")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Original**")
        st.markdown(md_clean if md_clean else "_No cleaned_markdown_", unsafe_allow_html=True)

    with col4:
        st.markdown("**Highlighted**")
        st.markdown(
            highlight_sentences(md_clean, sentence_index),
            unsafe_allow_html=True
        )

    # ---------------------------------------------------
    # Sentence Legend
    # ---------------------------------------------------
    st.markdown("## 🏷 Sentence Index (Reference)")
    add_section_explanation("## 🏷 Sentence Index (Reference)")

    legend_df = pd.DataFrame({
        "Index": [sentence_index[s] for s in sentences],
        "Sentence": sentences
    })

    st.dataframe(legend_df, use_container_width=True)

    # ---------------------------------------------------
    # Sentence-Level Model Comparison
    # ---------------------------------------------------
    st.markdown("## 🔍 Sentence-Level Model Comparison")
    add_section_explanation("## 🔍 Sentence-Level Model Comparison")

    pivot = subset.pivot_table(
        index="sentence",
        columns="model",
        values="sentiment",
        aggfunc="first"
    )

    pivot = ensure_all_models(df_pdf, pivot)
    st.dataframe(pivot, use_container_width=True)

    # ---------------------------------------------------
    # Presence Validation
    # ---------------------------------------------------
    st.markdown("## ✅ Sentence Grounding Check")
    add_section_explanation("## ✅ Sentence Grounding Check")

    presence_rows = []
    for s in sentences:
        presence_rows.append({
            "index": sentence_index[s],
            "sentence": s,
            "in_markdown_full": s in str(md_full),
            "in_cleaned_markdown": s in str(md_clean)
        })

    presence_df = pd.DataFrame(presence_rows)
    presence_df["found_anywhere"] = (
        presence_df["in_markdown_full"] |
        presence_df["in_cleaned_markdown"]
    )

    st.dataframe(presence_df, use_container_width=True)

    missing = presence_df[~presence_df["found_anywhere"]]
    if not missing.empty:
        st.warning(
            f"⚠️ {len(missing)} sentences are NOT grounded in the source markdown."
        )
        st.dataframe(
            missing[["index", "sentence"]],
            use_container_width=True
        )
    else:
        st.success("✅ All ESG sentences are grounded in the source text.")

# -------------------------------------------------------
# TAB 5 — Breakdown by Provider
# -------------------------------------------------------
with tab5:
    st.subheader("LLM Breakdown by Provider")
    add_section_explanation("LLM Breakdown by Provider")

    filenames = sorted(filtered["filename"].unique())
    selected_file = st.selectbox("Select Report Filename", filenames, key="file_tab5")

    pages = sorted(filtered[filtered["filename"] == selected_file]["page_number"].unique())
    selected_page = st.selectbox("Select Page Number", pages, key="page_tab5")

    subset = filtered[
        (filtered["filename"] == selected_file) &
        (filtered["page_number"] == selected_page)
    ].copy()

    providers = sorted(subset["provider"].unique())
    selected_provider = st.selectbox("Select Provider", providers, key="provider_tab5")

    provider_subset = subset[subset["provider"] == selected_provider]

    st.write("Models under provider:", sorted(provider_subset["model"].unique()))

    # --- COMPLETENESS FOR PROVIDER ---
    df_pdf = filtered[filtered["filename"] == selected_file]
    comp = model_completeness(df_pdf[df_pdf["provider"] == selected_provider], provider_subset)

    st.metric("Provider Completeness", f"{comp['score']*100:.1f}%")
    if comp["missing_count"] > 0:
        st.warning(
            f"Missing {comp['missing_count']} provider models: {', '.join(comp['missing'])}"
        )

    # Cleaned Markdown
    st.subheader("📖 Cleaned Markdown")
    add_section_explanation("📖 Cleaned Markdown")
    if "cleaned_markdown" in subset.columns:
        st.markdown(subset["cleaned_markdown"].dropna().iloc[0])

    # Sentence comparison
    pivot_sent = provider_subset.pivot_table(
        index="sentence",
        columns="model",
        values="sentiment",
        aggfunc=lambda x: x.iloc[0] if len(x) else None
    )
    pivot_sent = ensure_all_models(df_pdf[df_pdf["provider"] == selected_provider], pivot_sent)
    st.dataframe(pivot_sent, use_container_width=True)

# -------------------------------------------------------
# TAB 6 — Model Coverage
# -------------------------------------------------------
with tab6:
    st.subheader("📦 Model Coverage Across PDFs and Pages")
    add_section_explanation("📦 Model Coverage Across PDFs and Pages")

    models_per_pdf = (
        df.groupby("filename")["model"].nunique()
        .rename("unique_model_count")
        .sort_values(ascending=False)
    )
    st.dataframe(models_per_pdf)

    models_per_page = (
        df.groupby(["filename", "page_number"])["model"]
        .nunique()
        .reset_index()
        .rename(columns={"model": "unique_model_count"})
    )
    st.dataframe(models_per_page)

    selected_file_cov = st.selectbox(
        "Select Report Filename",
        sorted(df["filename"].unique()),
        key="cov_file"
    )

    st.subheader("📄 Pages for this File")
    add_section_explanation("📄 Pages for this File")
    subset = models_per_page[
        models_per_page["filename"] == selected_file_cov
    ].sort_values("page_number")
    st.dataframe(subset)

    st.subheader("🧠 Models Used on Each Page")
    add_section_explanation("🧠 Models Used on Each Page")
    model_page_map = (
        df[df["filename"] == selected_file_cov]
        .groupby("page_number")["model"]
        .unique()
        .reset_index()
    )
    model_page_map["models"] = model_page_map["model"].apply(lambda x: ", ".join(sorted(x)))
    model_page_map = model_page_map.drop(columns=["model"])
    st.dataframe(model_page_map)

    st.subheader("🔥 Model–Page Heatmap")
    add_section_explanation("🔥 Model–Page Heatmap")
    pivot = (
        df[df["filename"] == selected_file_cov]
        .pivot_table(
            index="page_number",
            columns="model",
            values="sentence",
            aggfunc="count",
            fill_value=0
        )
    )
    pivot = ensure_all_models(df[df["filename"] == selected_file_cov], pivot)
    st.dataframe(pivot.style.background_gradient(cmap="Blues"), use_container_width=True)

# -------------------------------------------------------
# TAB 7 — Raw JSON View (FIXED)
# -------------------------------------------------------
with tab7:
    st.subheader("📦 Raw JSON Data Viewer")
    add_section_explanation("📦 Raw JSON Data Viewer")

    filenames = sorted(raw_df["filename"].unique())
    selected_file = st.selectbox("Filename", filenames, key="raw_file")

    pages = sorted(raw_df[raw_df["filename"] == selected_file]["page_number"].unique())
    selected_page = st.selectbox("Page", pages, key="raw_page")

    subset = raw_df[
        (raw_df["filename"] == selected_file) &
        (raw_df["page_number"] == selected_page)
    ]

    for _, row in subset.iterrows():
        st.markdown(f"## 🤖 Model: **{row['model']}**")

        with st.expander("📄 Raw Text"):
            st.code(row["text"], language="json")

        parsed = parse_esg_json(row["text"])
        st.caption(f"Parsed {len(parsed)} ESG objects")

        with st.expander("✅ Parsed JSON"):
            st.json(parsed)

        if parsed:
            with st.expander("📊 Normalized Table"):
                st.dataframe(pd.json_normalize(parsed), use_container_width=True)

# -------------------------------------------------------
# TAB 8 — Cross-Document Grounding Audit
# -------------------------------------------------------
with tab8:
    st.subheader("📊 Cross-Document Grounding Audit")
    add_section_explanation("📊 Cross-Document Grounding Audit")

    # ---------------------------------------------------
    # Helper: sentence grounding check
    # ---------------------------------------------------
    def is_sentence_grounded(sentence, md_full, md_clean):
        if not isinstance(sentence, str):
            return False
        return (
            sentence in str(md_full)
            or sentence in str(md_clean)
        )

    # ---------------------------------------------------
    # PREPARE PAGE-LEVEL DATA
    # ---------------------------------------------------
    audit_rows = []
    llm_models = sorted(filtered["model"].dropna().unique())

    grouped = filtered.groupby(["filename", "page_number"])

    for (filename, page), group in grouped:
        row0 = group.iloc[0]
        md_full = row0.get("markdown_full", "")
        md_clean = row0.get("cleaned_markdown", "")

        sentences = group["sentence"].dropna().unique().tolist()

        grounded_flags = {
            s: is_sentence_grounded(s, md_full, md_clean)
            for s in sentences
        }

        total_sentences = len(sentences)
        grounded_count = sum(grounded_flags.values())
        not_grounded_count = total_sentences - grounded_count

        num_llms = group["model"].nunique()

        base_row = {
            "filename": filename,
            "page_number": page,
            "num_llms": num_llms,
            "total_sentences": total_sentences,
            "grounded": grounded_count,
            "not_grounded": not_grounded_count,
        }


        # per-LLM counts
        for model in llm_models:
            model_group = group[group["model"] == model]
            model_sentences = model_group["sentence"].dropna().unique().tolist()

            model_grounded = sum(
                is_sentence_grounded(s, md_full, md_clean)
                for s in model_sentences
            )
            model_not = len(model_sentences) - model_grounded

            base_row[f"{model}_grounded"] = model_grounded
            base_row[f"{model}_not_grounded"] = model_not

        audit_rows.append(base_row)

    page_level_df = pd.DataFrame(audit_rows)

    st.markdown("## 🧾 Table 1 — Page-Level Grounding Scorecard")
    add_section_explanation("## 🧾 Table 1 — Page-Level Grounding Scorecard")
    st.dataframe(page_level_df, use_container_width=True)

    # ---------------------------------------------------
    # PAGE SELECTION FOR DRILL-DOWN
    # ---------------------------------------------------
    st.markdown("## 🔍 Drill-Down: Sentence-Level Audit")
    add_section_explanation("## 🔍 Drill-Down: Sentence-Level Audit")

    sel_file = st.selectbox(
        "Select Filename",
        sorted(page_level_df["filename"].unique()),
        key="audit_file"
    )

    sel_pages = sorted(
        page_level_df[page_level_df["filename"] == sel_file]["page_number"].unique()
    )

    sel_page = st.selectbox(
        "Select Page",
        sel_pages,
        key="audit_page"
    )

    page_subset = filtered[
        (filtered["filename"] == sel_file) &
        (filtered["page_number"] == sel_page)
    ]

    if page_subset.empty:
        st.warning("No data for selected file/page.")
        st.stop()

    row0 = page_subset.iloc[0]
    md_full = row0.get("markdown_full", "")
    md_clean = row0.get("cleaned_markdown", "")

    # ---------------------------------------------------
    # BUILD SENTENCE-LEVEL TABLES
    # ---------------------------------------------------
    sentence_rows = []

    for _, r in page_subset.iterrows():
        grounded = is_sentence_grounded(
            r["sentence"], md_full, md_clean
        )

        sentence_rows.append({
            "filename": r["filename"],
            "page_number": r["page_number"],
            "sentence": r["sentence"],
            "aspect": r.get("aspect"),
            "sentiment": r.get("sentiment"),
            "model": r["model"],
            "grounded": grounded
        })

    sentence_df = pd.DataFrame(sentence_rows)

    grounded_df = sentence_df[sentence_df["grounded"]]
    not_grounded_df = sentence_df[~sentence_df["grounded"]]

    # ---------------------------------------------------
    # TABLE 2 — GROUNDED SENTENCES
    # ---------------------------------------------------
    st.markdown("## ✅ Table 2 — Grounded Sentences")
    add_section_explanation("## ✅ Table 2 — Grounded Sentences")

    if grounded_df.empty:
        st.info("No grounded sentences on this page.")
    else:
        st.dataframe(
            grounded_df.drop(columns=["grounded"]),
            use_container_width=True
        )

    # ---------------------------------------------------
    # TABLE 3 — NOT-GROUNDED SENTENCES
    # ---------------------------------------------------
    st.markdown("## 🚨 Table 3 — Not-Grounded Sentences")
    add_section_explanation("## 🚨 Table 3 — Not-Grounded Sentences")

    if not_grounded_df.empty:
        st.success("🎉 No hallucinated sentences detected on this page.")
    else:
        st.dataframe(
            not_grounded_df.drop(columns=["grounded"]),
            use_container_width=True
        )