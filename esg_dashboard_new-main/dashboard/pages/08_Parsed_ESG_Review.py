import streamlit as st
import pandas as pd
import json
import os
import re
from utils.data_loader import (
    format_display_value,
    read_dataset,
    resolve_data_path,
    sorted_unique_values,
    value_matches,
)

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(page_title="Parsed ESG Review Workspace", layout="wide")
st.title("📊 ESG Parsed Sentence-Level Dashboard")
st.markdown(
    """
This page provides a second parsed-record workspace for reviewing sentence-level ESG annotations.

**What this page does**
- extracts JSON arrays or objects from raw LLM output
- normalizes records into a flat analytical dataframe
- prepares the parsed data for model, aspect, and distribution analysis

**What this page expects**
- the resolved `data_output` dataset with ESG JSON embedded in the `text` field

**How to use it**
- use this page when validating parser behavior against messy raw responses
- compare the parsed outputs with the source data path shown below
- treat this page as a debugging surface before downstream ontology analysis
"""
)

# -------------------------------------------------------
# Load CSV
# -------------------------------------------------------
DATA_PATH = str(resolve_data_path("data_output"))

st.caption(f"Using data: `{DATA_PATH}`")

@st.cache_data
def load_data(path):
    return read_dataset("data_output")

try:
    raw_df = load_data(DATA_PATH)
except Exception as e:
    st.error(f"❌ Failed to load dataset at: {DATA_PATH}\n\n{e}")
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
    df["source_row_id"] = df.index
    df["parsed"] = df["text"].apply(parse_esg_json)
    df["parsed_object_count"] = df["parsed"].apply(len)
    df["source_row_parsed"] = df["parsed_object_count"] > 0

    parsed_sources = df[df["source_row_parsed"]].copy()
    if parsed_sources.empty:
        return pd.DataFrame(columns=[c for c in df.columns if c != "parsed"])

    exploded = parsed_sources.explode("parsed", ignore_index=True)
    parsed_df = pd.json_normalize(exploded["parsed"])

    meta_cols = [c for c in df.columns if c != "parsed"]
    meta = exploded[meta_cols].reset_index(drop=True)

    full = pd.concat([meta, parsed_df], axis=1)
    full["parsed_record"] = True
    return full


df = parse_annotations(raw_df)
if "confidence" in df.columns:
    df["confidence_numeric"] = pd.to_numeric(df["confidence"], errors="coerce")


@st.cache_data
def build_source_parse_audit(source_df):
    audited = source_df.copy()
    audited["source_row_id"] = audited.index
    audited["parsed"] = audited["text"].apply(parse_esg_json) if "text" in audited.columns else [[] for _ in range(len(audited))]
    audited["parsed_object_count"] = audited["parsed"].apply(len)
    audited["source_row_parsed"] = audited["parsed_object_count"] > 0
    audited["parse_status"] = audited["source_row_parsed"].map({True: "parsed", False: "not parsed"})
    return audited.drop(columns=["parsed"])


source_audit_df = build_source_parse_audit(raw_df)

st.success(f"Parsed **{len(df)}** ESG sentence records")

# -------------------------------------------------------
# Helper: Safe filter labels for scalar/list/dict values
# -------------------------------------------------------
def format_filter_value(value):
    return format_display_value(value)


def sorted_unique_filter_values(series):
    return sorted_unique_values(series)


def page_sort_key(value):
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.notna(numeric):
        return (0, float(numeric))
    return (1, format_display_value(value))


def section_note(title, rqs, usage):
    st.info(f"**{title}** · Supports **{rqs}**. {usage}")


def build_page_coverage(audit_df):
    required = {"filename", "page_number"}
    if not required.issubset(audit_df.columns):
        return pd.DataFrame(), pd.DataFrame()

    working = audit_df.copy()
    working["filename_label"] = working["filename"].map(format_display_value)
    working["page_label"] = working["page_number"].map(format_display_value)
    working["page_numeric"] = pd.to_numeric(working["page_number"], errors="coerce")

    coverage = (
        working.groupby(["filename_label", "page_label"], dropna=False)
        .agg(
            source_rows=("source_row_id", "size"),
            parsed_source_rows=("source_row_parsed", "sum"),
            parsed_objects=("parsed_object_count", "sum"),
            models=("model", lambda values: ", ".join(sorted(set(filter(None, values.map(format_display_value))))[:10]) if "model" in working.columns else ""),
        )
        .reset_index()
    )
    coverage["not_parsed_source_rows"] = coverage["source_rows"] - coverage["parsed_source_rows"]
    coverage["page_status"] = coverage["parsed_objects"].gt(0).map({True: "processed", False: "not parsed"})

    missing_rows = []
    numeric_pages = working.dropna(subset=["page_numeric"])
    for filename, group in numeric_pages.groupby("filename_label"):
        if group.empty:
            continue
        min_page = int(group["page_numeric"].min())
        max_page = int(group["page_numeric"].max())
        present_pages = set(group["page_numeric"].astype(int).tolist())
        processed_pages = set(
            group[group["source_row_parsed"]]["page_numeric"].dropna().astype(int).tolist()
        )
        for page in range(min_page, max_page + 1):
            if page not in present_pages:
                status = "missing from source rows"
            elif page not in processed_pages:
                status = "source row exists but not parsed"
            else:
                continue
            missing_rows.append({"filename": filename, "page_number": page, "status": status})

    return coverage.sort_values(["filename_label", "page_label"], key=lambda s: s.map(format_display_value)), pd.DataFrame(missing_rows)

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
    all_models = sorted_unique_values(reference_df["model"])
    for m in all_models:
        if m not in pivot.columns:
            pivot[m] = None
    return pivot[all_models]

# -------------------------------------------------------
# Helper: completeness scoring
# -------------------------------------------------------
def model_completeness(df_pdf, df_page):
    expected = sorted_unique_values(df_pdf["model"])
    present = sorted_unique_values(df_page["model"])
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
    vals = sorted_unique_filter_values(df[col])
    return st.sidebar.multiselect(label, vals, default=vals)

aspect_cats = make_multiselect("Aspect Category", "aspect_category")
sentiments = make_multiselect("Sentiment", "sentiment")
tones = make_multiselect("Tone", "tone")
materialities = make_multiselect("Materiality", "materiality")
stakeholders = make_multiselect("Stakeholder", "stakeholder")
value_chain_stage = make_multiselect("Value Chain Stage", "value_chain_stage")
time_horizon = make_multiselect("Time Horizon", "time_horizon")

if "confidence" in df.columns:
    confidence_values = pd.to_numeric(df["confidence"], errors="coerce")
    confidence_values = confidence_values.dropna()
    if confidence_values.empty:
        st.sidebar.caption("Confidence filter unavailable: no numeric confidence values.")
        conf_range = None
    else:
        conf_min = max(0.0, float(confidence_values.min()))
        conf_max = min(1.0, float(confidence_values.max()))
        if conf_min == conf_max:
            st.sidebar.caption(f"Confidence filter fixed at {conf_min:.2f}.")
            conf_range = (conf_min, conf_max)
        else:
            conf_range = st.sidebar.slider(
                "Confidence Range",
                0.0, 1.0,
                (conf_min, conf_max),
                0.01,
            )
else:
    conf_range = None

filtered = df.copy()

def apply_filter(col, values):
    global filtered
    if values and col in filtered.columns:
        normalized = filtered[col].map(format_filter_value)
        filtered = filtered[normalized.isin(values)]

apply_filter("aspect_category", aspect_cats)
apply_filter("sentiment", sentiments)
apply_filter("tone", tones)
apply_filter("materiality", materialities)
apply_filter("stakeholder", stakeholders)
apply_filter("value_chain_stage", value_chain_stage)
apply_filter("time_horizon", time_horizon)

if conf_range:
    lo, hi = conf_range
    filtered = filtered[
        (filtered["confidence_numeric"] >= lo)
        & (filtered["confidence_numeric"] <= hi)
    ]

st.caption(f"Showing **{len(filtered)}** sentences after filtering.")

# -------------------------------------------------------
# Tabs
# -------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊 Distributions",
    "📌 Aspects",
    "📄 Sentence Table",
    "🤖 Model Comparison",
    "LLM Breakdown",
    "🧮 Model Coverage",
    "📦 Raw JSON View",
    "📊 Grounding Audit",
    "🧾 Page Coverage & Parse Audit",
])


# -------------------------------------------------------
# TAB 1 — Distributions
# -------------------------------------------------------
with tab1:
    section_note(
        "Distributions",
        "RQ2, RQ6",
        "Use this section to understand tone, sentiment, and aspect-category balance before making categorization or stability claims.",
    )
    st.subheader("Sentiment Distribution")
    st.bar_chart(filtered["sentiment"].value_counts().sort_values(ascending=False))

    st.subheader("Aspect Category Distribution")
    st.bar_chart(filtered["aspect_category"].value_counts().sort_values(ascending=False))

# -------------------------------------------------------
# TAB 2 — Aspects
# -------------------------------------------------------
with tab2:
    section_note(
        "Aspect review",
        "RQ2, RQ4",
        "Use this section to identify dominant aspects and possible ontology drift or over-fragmented free-text labels.",
    )
    st.subheader("Top Aspects")
    if "aspect" in filtered:
        n = st.slider("Show Top N", 3, 30, 10)
        topA = filtered["aspect"].value_counts().head(n)
        st.bar_chart(topA)
        st.dataframe(topA.rename("count"))

# -------------------------------------------------------
# TAB 3 — Sentence Table
# -------------------------------------------------------
with tab3:
    section_note(
        "Sentence table",
        "RQ1, RQ2, RQ4",
        "Use this section to inspect the actual parsed records. Rows here are parsed ESG records; raw rows that failed parsing are listed in the parse audit tab.",
    )
    st.subheader("Full Sentence Table")
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
    section_note(
        "Model comparison",
        "RQ1, RQ3, RQ4, RQ6",
        "Use this section to compare model outputs on the same file/page and verify whether extracted ESG sentences are grounded in the source markdown.",
    )
    st.subheader("🤖 LLM Model Comparison (Grounded & Auditable)")

    # ---------------------------------------------------
    # File & Page Selection
    # ---------------------------------------------------
    filenames = sorted_unique_values(filtered["filename"])
    selected_file = st.selectbox("Filename", filenames, key="mc_file")

    file_mask = value_matches(filtered["filename"], selected_file)
    pages = sorted_unique_values(filtered.loc[file_mask, "page_number"])
    selected_page = st.selectbox("Page Number", pages, key="mc_page")

    subset = filtered[
        file_mask &
        value_matches(filtered["page_number"], selected_page)
    ]

    if subset.empty:
        st.warning("No data for this file & page.")
        st.stop()

    # ---------------------------------------------------
    # Model Completeness
    # ---------------------------------------------------
    df_pdf = filtered[file_mask]
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

    # ---- markdown_full ----
    st.markdown("### 🧾 markdown_full")

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

    legend_df = pd.DataFrame({
        "Index": [sentence_index[s] for s in sentences],
        "Sentence": sentences
    })

    st.dataframe(legend_df, use_container_width=True)

    # ---------------------------------------------------
    # Sentence-Level Model Comparison
    # ---------------------------------------------------
    st.markdown("## 🔍 Sentence-Level Model Comparison")

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
    section_note(
        "LLM breakdown",
        "RQ1, RQ4, RQ6",
        "Use this section to inspect provider/model coverage and identify missing models for a selected file and page.",
    )
    st.subheader("LLM Breakdown by Provider")

    filenames = sorted_unique_values(filtered["filename"])
    selected_file = st.selectbox("Select Report Filename", filenames, key="file_tab5")

    file_mask = value_matches(filtered["filename"], selected_file)
    pages = sorted_unique_values(filtered.loc[file_mask, "page_number"])
    selected_page = st.selectbox("Select Page Number", pages, key="page_tab5")

    subset = filtered[
        file_mask &
        value_matches(filtered["page_number"], selected_page)
    ].copy()

    providers = sorted_unique_values(subset["provider"])
    selected_provider = st.selectbox("Select Provider", providers, key="provider_tab5")

    provider_subset = subset[value_matches(subset["provider"], selected_provider)]

    st.write("Models under provider:", sorted_unique_values(provider_subset["model"]))

    # --- COMPLETENESS FOR PROVIDER ---
    df_pdf = filtered[file_mask]
    comp = model_completeness(
        df_pdf[value_matches(df_pdf["provider"], selected_provider)],
        provider_subset,
    )

    st.metric("Provider Completeness", f"{comp['score']*100:.1f}%")
    if comp["missing_count"] > 0:
        st.warning(
            f"Missing {comp['missing_count']} provider models: {', '.join(comp['missing'])}"
        )

    # Cleaned Markdown
    st.subheader("📖 Cleaned Markdown")
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
    section_note(
        "Model coverage",
        "RQ1, RQ3, RQ6",
        "Use this section to see which pages were processed by which models and where model/page coverage is incomplete.",
    )
    st.subheader("📦 Model Coverage Across PDFs and Pages")

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
        sorted_unique_values(df["filename"]),
        key="cov_file"
    )

    st.subheader("📄 Pages for this File")
    subset = models_per_page[
        value_matches(models_per_page["filename"], selected_file_cov)
    ].sort_values("page_number")
    st.dataframe(subset)

    st.subheader("🧠 Models Used on Each Page")
    model_page_map = (
        df[value_matches(df["filename"], selected_file_cov)]
        .groupby("page_number")["model"]
        .unique()
        .reset_index()
    )
    model_page_map["models"] = model_page_map["model"].apply(
        lambda x: ", ".join(sorted(format_display_value(item) for item in x if format_display_value(item)))
    )
    model_page_map = model_page_map.drop(columns=["model"])
    st.dataframe(model_page_map)

    st.subheader("🔥 Model–Page Heatmap")
    pivot = (
        df[value_matches(df["filename"], selected_file_cov)]
        .pivot_table(
            index="page_number",
            columns="model",
            values="sentence",
            aggfunc="count",
            fill_value=0
        )
    )
    pivot = ensure_all_models(df[value_matches(df["filename"], selected_file_cov)], pivot)
    st.dataframe(pivot.style.background_gradient(cmap="Blues"), use_container_width=True)

# -------------------------------------------------------
# TAB 7 — Raw JSON View (FIXED)
# -------------------------------------------------------
with tab7:
    section_note(
        "Raw JSON view",
        "RQ1, RQ4",
        "Use this section to compare raw LLM output against the parsed JSON objects and diagnose failed parsing.",
    )
    st.subheader("📦 Raw JSON Data Viewer")

    filenames = sorted_unique_values(raw_df["filename"])
    selected_file = st.selectbox("Filename", filenames, key="raw_file")

    raw_file_mask = value_matches(raw_df["filename"], selected_file)
    pages = sorted_unique_values(raw_df.loc[raw_file_mask, "page_number"])
    selected_page = st.selectbox("Page", pages, key="raw_page")

    subset = raw_df[
        raw_file_mask &
        value_matches(raw_df["page_number"], selected_page)
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
    section_note(
        "Grounding audit",
        "RQ1, RQ4",
        "Use this section to test whether parsed ESG sentences actually appear in the source markdown, which helps detect hallucinated or ungrounded outputs.",
    )
    st.subheader("📊 Cross-Document Grounding Audit")

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
    llm_models = sorted_unique_values(filtered["model"])

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
    st.dataframe(page_level_df, use_container_width=True)

    # ---------------------------------------------------
    # PAGE SELECTION FOR DRILL-DOWN
    # ---------------------------------------------------
    st.markdown("## 🔍 Drill-Down: Sentence-Level Audit")

    sel_file = st.selectbox(
        "Select Filename",
        sorted_unique_values(page_level_df["filename"]),
        key="audit_file"
    )

    audit_file_mask = value_matches(page_level_df["filename"], sel_file)
    sel_pages = sorted_unique_values(page_level_df.loc[audit_file_mask, "page_number"])

    sel_page = st.selectbox(
        "Select Page",
        sel_pages,
        key="audit_page"
    )

    page_subset = filtered[
        value_matches(filtered["filename"], sel_file) &
        value_matches(filtered["page_number"], sel_page)
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

    if not_grounded_df.empty:
        st.success("🎉 No hallucinated sentences detected on this page.")
    else:
        st.dataframe(
            not_grounded_df.drop(columns=["grounded"]),
            use_container_width=True
        )

with tab9:
    section_note(
        "Page coverage and parse audit",
        "RQ1, RQ4, RQ5",
        "Use this section to answer which file/page rows were parsed, which raw rows failed parsing, and where there may be missing pages or source rows with no parsed ESG objects.",
    )

    st.subheader("Parse Status Summary")
    total_source_rows = len(source_audit_df)
    parsed_source_rows = int(source_audit_df["source_row_parsed"].sum()) if not source_audit_df.empty else 0
    not_parsed_source_rows = total_source_rows - parsed_source_rows
    parsed_objects = int(source_audit_df["parsed_object_count"].sum()) if not source_audit_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Source rows", f"{total_source_rows:,}")
    c2.metric("Parsed source rows", f"{parsed_source_rows:,}")
    c3.metric("Not parsed source rows", f"{not_parsed_source_rows:,}")
    c4.metric("Parsed ESG objects", f"{parsed_objects:,}")

    st.subheader("Pages Processed by Filename")
    coverage_df, missing_pages_df = build_page_coverage(source_audit_df)
    if coverage_df.empty:
        st.info("Filename/page_number columns are not available for page coverage.")
    else:
        st.write(
            "A page is marked `processed` when at least one source row on that file/page produced parsed ESG objects. "
            "`not parsed` means the source row exists, but the parser did not extract any valid ESG sentence objects."
        )
        st.dataframe(coverage_df, use_container_width=True, height=420)

        status_counts = (
            coverage_df["page_status"]
            .value_counts()
            .rename_axis("page_status")
            .reset_index(name="pages")
        )
        st.bar_chart(status_counts.set_index("page_status")["pages"])

        selected_cov_file = st.selectbox(
            "Drill into filename",
            sorted_unique_values(coverage_df["filename_label"]),
            key="parse_audit_file",
        )
        file_coverage = coverage_df[value_matches(coverage_df["filename_label"], selected_cov_file)]
        st.dataframe(file_coverage, use_container_width=True)

    st.subheader("Missing or Unprocessed Pages")
    if missing_pages_df.empty:
        st.success("No numeric page gaps or unparsed source pages were detected in the current source data.")
    else:
        st.write(
            "This table has two meanings: `missing from source rows` means the page number is absent between the minimum "
            "and maximum observed page for the file; `source row exists but not parsed` means the raw row exists but produced no valid ESG objects."
        )
        st.dataframe(missing_pages_df, use_container_width=True, height=360)

    st.subheader("Parsed vs Not Parsed Source Rows")
    parse_status = st.radio(
        "Rows to list",
        ["not parsed", "parsed", "all"],
        horizontal=True,
        key="parse_status_rows",
    )
    row_view = source_audit_df.copy()
    if parse_status != "all":
        row_view = row_view[row_view["parse_status"] == parse_status]

    audit_cols = [
        col for col in [
            "source_row_id",
            "parse_status",
            "parsed_object_count",
            "filename",
            "page_number",
            "model",
            "metadata_check",
            "check",
            "text",
        ]
        if col in row_view.columns
    ]
    st.dataframe(row_view[audit_cols], use_container_width=True, height=520)
