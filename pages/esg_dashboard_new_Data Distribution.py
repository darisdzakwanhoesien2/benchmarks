import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.io as pio
import json
from pathlib import Path

# ------------------------------------------------
# 🎨 Plotly Theme
# ------------------------------------------------
pio.templates.default = "plotly_white"

# ------------------------------------------------
# 📌 Page Title
# ------------------------------------------------
st.title("🔍 Aspect & Ontology Visualization Dashboard")
add_page_explanation(__file__)
st.write(
    "Ontology-driven analysis of aspect categories, ontology URIs, "
    "sentiment, and tone at sentence level."
)

# ------------------------------------------------
# 📥 Sidebar — File Upload
# ------------------------------------------------
from pathlib import Path
import json

# --- Dataset selection from config/dataset.json ---
dataset_config_path = Path(__file__).resolve().parents[1] / "config" / "dataset.json"
datasets = []
if dataset_config_path.exists():
    with open(dataset_config_path) as f:
        config = json.load(f)
        datasets = config.get("datasets", [])

dataset_names = [d["name"] for d in datasets]
dataset_choice = None
selected_file = None

if dataset_names:
    dataset_choice = st.sidebar.selectbox("Select a dataset", ["(Upload your own)"] + dataset_names, key="dataset_selectbox")
    if dataset_choice != "(Upload your own)":
        selected = next((d for d in datasets if d["name"] == dataset_choice), None)
        if selected:
            selected_file = selected["filepath"]

uploaded_file = st.sidebar.file_uploader("Or upload ESG CSV", type=["csv"], key="aspect_file_data_dist")

if selected_file:
    df = pd.read_csv(selected_file)
    st.sidebar.success(f"Loaded dataset: {selected_file}")
elif uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Loaded uploaded file")
else:
    st.info("⬅️ Please select a dataset or upload a CSV file to begin.")
    st.stop()

# --- Dataset selection from config/dataset.json ---
from pathlib import Path
import json

dataset_config_path = Path(__file__).resolve().parents[1] / "config" / "dataset.json"
datasets = []
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

uploaded_file = st.sidebar.file_uploader("Or upload ESG CSV", type=["csv"], key="aspect_file")

if selected_file:
    df = pd.read_csv(selected_file)
    st.sidebar.success(f"Loaded dataset: {selected_file}")
elif uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Loaded uploaded file")
else:
    st.info("⬅️ Please select a dataset or upload a CSV file to begin.")
    st.stop()

# ------------------------------------------------
# 🔐 Normalize Column Names
# ------------------------------------------------
df.columns = df.columns.str.strip().str.lower()

REQUIRED_COLS = {
    "aspect",
    "aspect_category",
    "ontology_uri",
    "sentiment",
    "tone",
    "sentence",
}

missing = REQUIRED_COLS - set(df.columns)
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

st.success("✅ File loaded successfully")
# --- ADDED: show dataset size / row count ---
row_count = len(df)
unique_sentences = df["sentence"].nunique() if "sentence" in df.columns else row_count
col_a, col_b = st.columns([1, 3])
col_a.metric("Rows", row_count)
col_b.caption(f"Unique sentences: {unique_sentences}")

st.dataframe(df.head(), use_container_width=True)

# =================================================
# 📚 LOAD ONTOLOGIES
# =================================================
BASE_DATA_PATH = Path(__file__).resolve().parents[1] / "data"

# -----------------------------
# Aspect Ontology
# -----------------------------
with open(BASE_DATA_PATH / "aspect_category_ontology.json") as f:
    ASPECT_ONTOLOGY = json.load(f)

ASPECT_ALIAS_MAP = {
    str(alias).strip().upper(): canonical
    for canonical, meta in ASPECT_ONTOLOGY.items()
    for alias in meta.get("aliases", [])
    if alias is not None
}

def normalize_aspect_category(value):
    if pd.isna(value):
        return "OTHER"
    return ASPECT_ALIAS_MAP.get(str(value).strip().upper(), "OTHER")

def aspect_label(canonical):
    return ASPECT_ONTOLOGY.get(canonical, {}).get("label", canonical)

# -----------------------------
# Sentiment Ontology
# -----------------------------
with open(BASE_DATA_PATH / "sentiment_ontology.json") as f:
    SENTIMENT_ONTOLOGY = json.load(f)

SENTIMENT_ALIAS_MAP = {
    str(alias).strip().lower(): canonical
    for canonical, meta in SENTIMENT_ONTOLOGY.items()
    for alias in meta.get("aliases", [])
    if alias is not None
}

def normalize_sentiment(value):
    if pd.isna(value):
        return "OTHER"
    return SENTIMENT_ALIAS_MAP.get(str(value).strip().lower(), "OTHER")

def sentiment_label(canonical):
    return SENTIMENT_ONTOLOGY.get(canonical, {}).get("label", canonical)

# -----------------------------
# Tone Ontology  ✅ NEW
# -----------------------------
with open(BASE_DATA_PATH / "tone_ontology.json") as f:
    TONE_ONTOLOGY = json.load(f)

TONE_ALIAS_MAP = {
    str(alias).strip().lower(): canonical
    for canonical, meta in TONE_ONTOLOGY.items()
    for alias in meta.get("aliases", [])
    if alias is not None
}

def normalize_tone(value):
    if pd.isna(value):
        return "OTHER"
    return TONE_ALIAS_MAP.get(str(value).strip().lower(), "OTHER")

def tone_label(canonical):
    return TONE_ONTOLOGY.get(canonical, {}).get("label", canonical)

# =================================================
# 🧹 APPLY NORMALIZATION
# =================================================
df["aspect_category_raw"] = df["aspect_category"]
df["aspect_category_norm"] = df["aspect_category"].apply(normalize_aspect_category)
df["aspect_category_label"] = df["aspect_category_norm"].apply(aspect_label)

df["sentiment_raw"] = df["sentiment"]
df["sentiment_norm"] = df["sentiment"].apply(normalize_sentiment)
df["sentiment_label"] = df["sentiment_norm"].apply(sentiment_label)

df["tone_raw"] = df["tone"]
df["tone_norm"] = df["tone"].apply(normalize_tone)
df["tone_label"] = df["tone_norm"].apply(tone_label)

ESG_ORDER = ["E", "S", "G", "E-S", "E-G", "S-G", "E-S-G", "OTHER"]
SENTIMENT_ORDER = ["POSITIVE", "NEUTRAL", "NEGATIVE", "OTHER"]
TONE_ORDER = ["OUTCOME", "ACTION", "COMMITMENT", "OTHER"]

# =================================================
# 1️⃣ Aspect Category Distribution
# =================================================
st.subheader("1️⃣ Aspect Category Distribution")
add_section_explanation("1️⃣ Aspect Category Distribution")

# show totals / unique aspects
unique_aspects = df["aspect"].nunique()
col1, col2 = st.columns([1, 2])
col1.metric("Rows", row_count)
col2.metric("Unique aspects", unique_aspects)

# allow switching between normalized category view and raw aspect view
view = st.radio(
    "View",
    ("Normalized Category (canonical)", "Raw Aspect (distinct)"),
    horizontal=True,
)

if view == "Normalized Category (canonical)":
    # normalized category counts (keeps ESG_ORDER first, includes others)
    counts = df["aspect_category_norm"].value_counts()
    ordered_index = [c for c in ESG_ORDER if c in counts.index] + [c for c in counts.index if c not in ESG_ORDER]
    fig1_data = counts.reindex(ordered_index).fillna(0).reset_index()
    fig1_data.columns = ["aspect_category_norm", "count"]
    fig1_data["label"] = fig1_data["aspect_category_norm"].apply(aspect_label)

    fig1 = px.bar(
        fig1_data,
        x="label",
        y="count",
        text="count",
        title="Aspect Category Frequency (normalized)",
    )
    fig1.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig1, use_container_width=True)

    # --- ADDED: table for the chart ---
    st.dataframe(fig1_data, use_container_width=True)

else:
    # raw aspect counts (allow showing all or top-N)
    raw_counts_all = (
        df["aspect"].fillna("UNKNOWN")
        .value_counts()
        .reset_index()
    )
    raw_counts_all.columns = ["aspect", "count"]

    show_all = st.checkbox("Show all raw aspects", value=False, help="Display the full aspect distribution (may be large).")
    if show_all:
        viz = raw_counts_all.copy()
    else:
        TOP_N = st.slider("Top N Raw Aspects to show", 5, 500, 50)
        viz = raw_counts_all.head(TOP_N).copy()

    # choose orientation for better readability when many items
    if len(viz) > 40:
        fig1 = px.bar(
            viz,
            x="count",
            y="aspect",
            orientation="h",
            text="count",
            title=f"{'All' if show_all else f'Top {len(viz)}'} Raw Aspects by Frequency",
        )
        fig1.update_layout(height=max(400, len(viz) * 18), yaxis={"automargin": True})
    else:
        fig1 = px.bar(
            viz,
            x="aspect",
            y="count",
            text="count",
            title=f"{'All' if show_all else f'Top {len(viz)}'} Raw Aspects by Frequency",
        )
        fig1.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig1, use_container_width=True)

    # table + download
    st.dataframe(viz.reset_index(drop=True), use_container_width=True)
    csv = viz.to_csv(index=False)
    st.download_button("Download Raw Aspect Distribution CSV", csv, "raw_aspect_distribution.csv")

# --- ADDED: Feature Distributions (ontology_uri / sentiment / tone / confidence) ---
st.subheader("🔎 Feature Distributions")
add_section_explanation("🔎 Feature Distributions")

# allow optional filtering by aspect category
aspect_options = ["All"] + [
    (c, aspect_label(c)) for c in sorted(df["aspect_category_norm"].unique())
]
# build a map for display -> canonical
display_map = {"All": "All"}
for canon, lbl in aspect_options[1:]:
    display_map[f"{lbl} ({canon})"] = canon

selected_aspect_display = st.selectbox(
    "Filter by Aspect Category",
    ["All"] + [f"{lbl} ({canon})" for canon, lbl in aspect_options[1:]],
    help="Limit distributions to a specific aspect category (optional).",
)
selected_aspect = display_map.get(selected_aspect_display, "All")

if selected_aspect == "All":
    feat_df = df.copy()
else:
    feat_df = df[df["aspect_category_norm"] == selected_aspect].copy()

st.caption(f"Rows in selection: {len(feat_df)}")

feature = st.selectbox(
    "Feature",
    ["Ontology URI", "Sentiment (normalized)", "Tone (normalized)", "Confidence"],
    index=0,
)

if feature == "Ontology URI":
    vc = feat_df["ontology_uri"].fillna("UNKNOWN").value_counts()
    top_n = st.slider("Top N URIs to show", 5, 200, 30)
    viz = vc.head(top_n).reset_index()
    viz.columns = ["ontology_uri", "count"]
    viz["percent"] = (viz["count"] / len(feat_df)).round(4)
    fig = px.bar(viz, x="ontology_uri", y="count", text="count", title="Ontology URI Frequency")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(viz, use_container_width=True)

elif feature == "Sentiment (normalized)":
    # use sentiment_label for human readable labels
    vc = feat_df["sentiment_norm"].fillna("OTHER").value_counts()
    viz = vc.reset_index()
    viz.columns = ["sentiment_norm", "count"]
    viz["label"] = viz["sentiment_norm"].apply(sentiment_label)
    viz["percent"] = (viz["count"] / len(feat_df)).round(4)
    # keep SENTIMENT_ORDER if present
    order = [s for s in SENTIMENT_ORDER if s in viz["sentiment_norm"].values] + [s for s in viz["sentiment_norm"].values if s not in SENTIMENT_ORDER]
    viz = viz.set_index("sentiment_norm").reindex(order).reset_index()
    fig = px.bar(viz, x="label", y="count", text="count", title="Sentiment Distribution (normalized)")
    fig.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(viz[["label", "count", "percent"]], use_container_width=True)

elif feature == "Tone (normalized)":
    vc = feat_df["tone_norm"].fillna("OTHER").value_counts()
    viz = vc.reset_index()
    viz.columns = ["tone_norm", "count"]
    viz["label"] = viz["tone_norm"].apply(tone_label)
    viz["percent"] = (viz["count"] / len(feat_df)).round(4)
    order = [t for t in TONE_ORDER if t in viz["tone_norm"].values] + [t for t in viz["tone_norm"].values if t not in TONE_ORDER]
    viz = viz.set_index("tone_norm").reindex(order).reset_index()
    fig = px.bar(viz, x="label", y="count", text="count", title="Tone Distribution (normalized)")
    fig.update_layout(xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(viz[["label", "count", "percent"]], use_container_width=True)

else:  # Confidence
    if "confidence" not in feat_df.columns:
        st.info("No 'confidence' column found in the dataset.")
    else:
        conf = pd.to_numeric(feat_df["confidence"], errors="coerce")
        missing = conf.isna().sum()
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        stats_col1.metric("Mean", f"{conf.mean():.3f}")
        stats_col2.metric("Median", f"{conf.median():.3f}")
        stats_col3.metric("Missing", f"{missing}")

        # histogram
        bins = st.slider("Histogram bins", 10, 200, 30)
        fig_h = px.histogram(feat_df, x="confidence", nbins=bins, title="Confidence Histogram")
        st.plotly_chart(fig_h, use_container_width=True)

        # boxplot grouped
        group_by = st.selectbox("Group confidence by (optional)", ["None", "Sentiment", "Tone", "Aspect Category"])
        if group_by != "None":
            if group_by == "Sentiment":
                col = "sentiment_label"
                feat_df["sentiment_label"] = feat_df["sentiment_norm"].apply(sentiment_label)
                fig_b = px.box(feat_df, x=col, y="confidence", title="Confidence by Sentiment")
            elif group_by == "Tone":
                col = "tone_label"
                feat_df["tone_label"] = feat_df["tone_norm"].apply(tone_label)
                fig_b = px.box(feat_df, x=col, y="confidence", title="Confidence by Tone")
            else:
                col = "aspect_label"
                feat_df["aspect_label"] = feat_df["aspect_category_norm"].apply(aspect_label)
                fig_b = px.box(feat_df, x=col, y="confidence", title="Confidence by Aspect Category")
            fig_b.update_layout(xaxis_tickangle=-25)
            st.plotly_chart(fig_b, use_container_width=True)

# =================================================
# 2️⃣ Ontology URI Distribution
# =================================================
st.subheader("2️⃣ Ontology URI Distribution")
add_section_explanation("2️⃣ Ontology URI Distribution")

fig2_data = (
    df["ontology_uri"]
    .fillna("UNKNOWN")
    .value_counts()
    .head(30)
    .reset_index()
)

fig2_data.columns = ["ontology_uri", "count"]

fig2 = px.bar(
    fig2_data,
    x="ontology_uri",
    y="count",
    title="Top Ontology URI Frequency",
)

fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2, use_container_width=True)

# --- ADDED: show data table for ontology URI chart ---
st.dataframe(fig2_data, use_container_width=True)

# =================================================
# 3️⃣ Sentiment Distribution by Aspect Category
# =================================================
st.subheader("3️⃣ Sentiment Distribution by Aspect Category")
add_section_explanation("3️⃣ Sentiment Distribution by Aspect Category")

sent_aspect = (
    df.groupby(["aspect_category_norm", "sentiment_norm"])
    .size()
    .reset_index(name="count")
)

sent_aspect["aspect_label"] = sent_aspect["aspect_category_norm"].apply(aspect_label)
sent_aspect["sentiment_label"] = sent_aspect["sentiment_norm"].apply(sentiment_label)

fig3 = px.bar(
    sent_aspect,
    x="aspect_label",
    y="count",
    color="sentiment_label",
    barmode="group",
    title="Sentiment Distribution by Aspect Category",
)

fig3.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig3, use_container_width=True)

# --- ADDED: show underlying table for sentiment by aspect ---
st.dataframe(
    sent_aspect.sort_values(["aspect_label", "sentiment_label", "count"], ascending=[True, True, False]).reset_index(drop=True),
    use_container_width=True,
)

# =================================================
# 4️⃣ Tone Distribution by Aspect Category ✅ FIXED
# =================================================
st.subheader("4️⃣ Tone Distribution by Aspect Category")
add_section_explanation("4️⃣ Tone Distribution by Aspect Category")

tone_aspect = (
    df.groupby(["aspect_category_norm", "tone_norm"])
    .size()
    .reset_index(name="count")
)

tone_aspect["aspect_label"] = tone_aspect["aspect_category_norm"].apply(aspect_label)
tone_aspect["tone_label"] = tone_aspect["tone_norm"].apply(tone_label)

fig4 = px.bar(
    tone_aspect,
    x="aspect_label",
    y="count",
    color="tone_label",
    barmode="group",
    title="Tone Distribution by Aspect Category",
)

fig4.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig4, use_container_width=True)

# --- ADDED: show underlying table for tone by aspect ---
st.dataframe(
    tone_aspect.sort_values(["aspect_label", "tone_label", "count"], ascending=[True, True, False]).reset_index(drop=True),
    use_container_width=True,
)

# =================================================
# 5️⃣ Heatmaps
# =================================================
st.subheader("5️⃣ Aspect Category × Sentiment / Tone Heatmaps")
add_section_explanation("5️⃣ Aspect Category × Sentiment / Tone Heatmaps")

pivot_sent = pd.pivot_table(
    df,
    values="sentence",
    index="aspect_category_norm",
    columns="sentiment_label",
    aggfunc="count",
    fill_value=0,
).reindex(ESG_ORDER)

pivot_tone = pd.pivot_table(
    df,
    values="sentence",
    index="aspect_category_norm",
    columns="tone_label",
    aggfunc="count",
    fill_value=0,
).reindex(ESG_ORDER)

fig, ax = plt.subplots(1, 2, figsize=(16, 5))

sns.heatmap(pivot_sent, annot=True, cmap="Blues", ax=ax[0])
ax[0].set_title("Sentiment Heatmap")

sns.heatmap(pivot_tone, annot=True, cmap="Greens", ax=ax[1])
ax[1].set_title("Tone Heatmap")

st.pyplot(fig)

# --- ADDED: show pivot tables used for heatmaps side-by-side ---
col_left, col_right = st.columns(2)
col_left.subheader("Pivot: Aspect × Sentiment")
col_left.dataframe(pivot_sent.reset_index(), use_container_width=True)
col_right.subheader("Pivot: Aspect × Tone")
col_right.dataframe(pivot_tone.reset_index(), use_container_width=True)
#
# =================================================
# 📤 JSON EXPORTS
# =================================================
st.subheader("📤 Export Normalized JSON Annotations")
add_section_explanation("📤 Export Normalized JSON Annotations")

# Aspect JSON
aspect_json = (
    df["aspect_category_norm"]
    .value_counts()
    .reindex(ESG_ORDER, fill_value=0)
    .reset_index()
)
aspect_json.columns = ["aspect", "count"]
aspect_json["label"] = aspect_json["aspect"].apply(aspect_label)

st.download_button(
    "Download Aspect Summary (JSON)",
    json.dumps(aspect_json.to_dict(orient="records"), indent=2),
    "aspect_category_summary.json",
    "application/json",
)

# Sentiment JSON
sentiment_json = (
    df["sentiment_norm"]
    .value_counts()
    .reindex(SENTIMENT_ORDER, fill_value=0)
    .reset_index()
)
sentiment_json.columns = ["sentiment", "count"]
sentiment_json["label"] = sentiment_json["sentiment"].apply(sentiment_label)

st.download_button(
    "Download Sentiment Summary (JSON)",
    json.dumps(sentiment_json.to_dict(orient="records"), indent=2),
    "sentiment_summary.json",
    "application/json",
)

# Tone JSON ✅ NEW
tone_json = (
    df["tone_norm"]
    .value_counts()
    .reindex(TONE_ORDER, fill_value=0)
    .reset_index()
)
tone_json.columns = ["tone", "count"]
tone_json["label"] = tone_json["tone"].apply(tone_label)

st.download_button(
    "Download Tone Summary (JSON)",
    json.dumps(tone_json.to_dict(orient="records"), indent=2),
    "tone_summary.json",
    "application/json",
)

# =================================================
# 🧪 DEBUG VIEW
# =================================================
with st.expander("🧪 Debug: Raw vs Normalized Labels"):
    st.dataframe(
        df[
            [
                "aspect_category_raw",
                "aspect_category_norm",
                "sentiment_raw",
                "sentiment_norm",
                "tone_raw",
                "tone_norm",
                "sentence",
            ]
        ].head(30),
        use_container_width=True,
    )
