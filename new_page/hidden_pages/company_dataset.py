import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Company ESG Dataset",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Company ESG Dataset")
st.markdown("---")

# ─────────────────────────────────────────────
# Load Excel Data
# ─────────────────────────────────────────────
@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """Load Excel data from the given filepath."""
    try:
        df = pd.read_excel(filepath)
        return df
    except FileNotFoundError:
        st.error(f"❌ File not found: `{filepath}`")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
# Sidebar — File Upload / Path Input
# ─────────────────────────────────────────────
st.sidebar.header("📁 Data Source")

upload_mode = st.sidebar.radio(
    "Select Input Mode",
    ["Upload File", "Enter File Path"]
)

df = pd.DataFrame()

if upload_mode == "Upload File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel File", type=["xlsx", "xls"]
    )
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.sidebar.success("✅ File loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

elif upload_mode == "Enter File Path":
    default_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "esg_data.xlsx"
    )
    file_path = st.sidebar.text_input("Excel File Path", value=default_path)
    if st.sidebar.button("Load Data"):
        df = load_data(file_path)
        if not df.empty:
            st.sidebar.success("✅ File loaded successfully!")

# ─────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────
if df.empty:
    st.info("📂 Please upload an Excel file or provide a valid file path to get started.")
    st.stop()

# ─────────────────────────────────────────────
# Dataset Overview
# ─────────────────────────────────────────────
st.subheader("🗂️ Dataset Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Rows", f"{df.shape[0]:,}")
col2.metric("Total Columns", df.shape[1])
col3.metric("Missing Values", f"{df.isnull().sum().sum():,}")

with st.expander("📋 View Raw Data", expanded=False):
    st.dataframe(df, use_container_width=True)

with st.expander("📐 Data Types & Summary Statistics", expanded=False):
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("**Data Types**")
        st.dataframe(
            df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Type"}),
            use_container_width=True
        )
    with col_right:
        st.markdown("**Summary Statistics**")
        st.dataframe(df.describe(), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Sidebar — Column Selectors for Visualization
# ─────────────────────────────────────────────
st.sidebar.header("🎨 Visualization Settings")

numeric_cols  = df.select_dtypes(include="number").columns.tolist()
category_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
all_cols      = df.columns.tolist()

# ─────────────────────────────────────────────
# Section 1 — ESG Score Distribution
# ─────────────────────────────────────────────
st.subheader("📈 Score Distribution")

if numeric_cols:
    selected_score_col = st.sidebar.selectbox(
        "Select Score Column (Histogram)", numeric_cols, index=0
    )

    fig_hist = px.histogram(
        df,
        x=selected_score_col,
        nbins=30,
        title=f"Distribution of {selected_score_col}",
        color_discrete_sequence=["#2E86AB"],
        template="plotly_white"
    )
    fig_hist.update_layout(
        xaxis_title=selected_score_col,
        yaxis_title="Count",
        bargap=0.05
    )
    st.plotly_chart(fig_hist, use_container_width=True)
else:
    st.warning("⚠️ No numeric columns found for histogram.")

st.markdown("---")

# ─────────────────────────────────────────────
# Section 2 — Comparison by Category
# ─────────────────────────────────────────────
st.subheader("🏷️ Score Comparison by Category")

if category_cols and numeric_cols:
    col_cat, col_val = st.columns(2)
    with col_cat:
        selected_cat = st.selectbox("Select Category Column", category_cols)
    with col_val:
        selected_val = st.selectbox("Select Value Column", numeric_cols)

    top_n = st.slider("Show Top N Categories", min_value=5, max_value=50, value=15)

    grouped = (
        df.groupby(selected_cat)[selected_val]
        .mean()
        .reset_index()
        .sort_values(selected_val, ascending=False)
        .head(top_n)
    )

    fig_bar = px.bar(
        grouped,
        x=selected_cat,
        y=selected_val,
        title=f"Average {selected_val} by {selected_cat} (Top {top_n})",
        color=selected_val,
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("⚠️ Need at least one category column and one numeric column.")

st.markdown("---")

# ─────────────────────────────────────────────
# Section 3 — Scatter Plot (Two Metrics)
# ─────────────────────────────────────────────
st.subheader("🔵 Scatter Plot — Two Metric Comparison")

if len(numeric_cols) >= 2:
    sc_col1, sc_col2, sc_col3 = st.columns(3)
    with sc_col1:
        x_axis = st.selectbox("X-Axis", numeric_cols, index=0, key="scatter_x")
    with sc_col2:
        y_axis = st.selectbox("Y-Axis", numeric_cols, index=1, key="scatter_y")
    with sc_col3:
        color_col = st.selectbox(
            "Color By (optional)",
            ["None"] + category_cols,
            key="scatter_color"
        )

    fig_scatter = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color=None if color_col == "None" else color_col,
        title=f"{x_axis} vs {y_axis}",
        template="plotly_white",
        opacity=0.7
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("⚠️ Need at least two numeric columns for scatter plot.")

st.markdown("---")

# ─────────────────────────────────────────────
# Section 4 — Correlation Heatmap
# ─────────────────────────────────────────────
st.subheader("🌡️ Correlation Heatmap")

if len(numeric_cols) >= 2:
    corr = df[numeric_cols].corr()

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=corr.round(2).values,
            texttemplate="%{text}",
            showscale=True
        )
    )
    fig_heatmap.update_layout(
        title="Correlation Matrix",
        template="plotly_white",
        height=500
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.warning("⚠️ Need at least two numeric columns for correlation heatmap.")

st.markdown("---")

# ─────────────────────────────────────────────
# Section 5 — Box Plot
# ─────────────────────────────────────────────
st.subheader("📦 Box Plot — Score Spread by Category")

if category_cols and numeric_cols:
    bp_cat = st.selectbox("Category Column", category_cols, key="box_cat")
    bp_val = st.selectbox("Value Column",    numeric_cols,  key="box_val")

    top_cats = (
        df[bp_cat]
        .value_counts()
        .head(15)
        .index.tolist()
    )
    df_box = df[df[bp_cat].isin(top_cats)]

    fig_box = px.box(
        df_box,
        x=bp_cat,
        y=bp_val,
        title=f"Distribution of {bp_val} by {bp_cat}",
        color=bp_cat,
        template="plotly_white"
    )
    fig_box.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.warning("⚠️ Need at least one category column and one numeric column.")

st.markdown("---")

# ─────────────────────────────────────────────
# Section 6 — Missing Values Analysis
# ─────────────────────────────────────────────
st.subheader("🔍 Missing Values Analysis")

missing = (
    df.isnull()
    .sum()
    .reset_index()
    .rename(columns={"index": "Column", 0: "Missing Count"})
)
missing["Missing %"] = (missing["Missing Count"] / len(df) * 100).round(2)
missing = missing[missing["Missing Count"] > 0].sort_values("Missing Count", ascending=False)

if missing.empty:
    st.success("✅ No missing values found in the dataset!")
else:
    fig_missing = px.bar(
        missing,
        x="Column",
        y="Missing %",
        title="Missing Values per Column (%)",
        color="Missing %",
        color_continuous_scale="Reds",
        template="plotly_white"
    )
    st.plotly_chart(fig_missing, use_container_width=True)
    st.dataframe(missing, use_container_width=True)

st.markdown("---")
st.caption("ESG Dataset Dashboard — Powered by Streamlit & Plotly")