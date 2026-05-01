import json
import re

import pandas as pd
import streamlit as st

from utils.data_loader import (
    format_display_value,
    read_dataset,
    resolve_data_path,
    sorted_unique_values,
)


DATASETS = {
    "data_output_2.txt": "data_output_2",
    "data_output.txt": "data_output",
    "Dataset.txt": "Dataset",
    "output.txt": "output",
    "output_in_csv.txt": "output_in_csv",
}


st.set_page_config(page_title="Data File Visualizer", layout="wide")
st.title("Data File Visualizer")


@st.cache_data
def load_named_dataset(base_name):
    return read_dataset(base_name)


def extract_json_block(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except Exception:
        return None


def normalize_json(obj):
    if obj is None:
        return []
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        rows = []
        for item in obj:
            rows.extend(normalize_json(item))
        return rows
    return []


def parse_json_rows(df):
    if "text" not in df.columns:
        return pd.DataFrame()

    rows = []
    meta_cols = [col for col in ["filename", "page_number", "model"] if col in df.columns]
    for _, source_row in df.iterrows():
        parsed_rows = normalize_json(extract_json_block(source_row.get("text")))
        for parsed in parsed_rows:
            if isinstance(parsed, dict):
                row = {col: source_row.get(col) for col in meta_cols}
                row.update(parsed)
                rows.append(row)

    return pd.DataFrame(rows)


def apply_sidebar_filters(df):
    filtered = df.copy()
    st.sidebar.header("Filters")

    for col in ["filename", "page_number", "model", "aspect_category", "sentiment", "tone"]:
        if col not in filtered.columns:
            continue
        options = sorted_unique_values(filtered[col])
        if not options:
            continue
        selected = st.sidebar.multiselect(col.replace("_", " ").title(), options, default=options)
        if selected:
            normalized = filtered[col].map(format_display_value)
            filtered = filtered[normalized.isin(selected)]

    return filtered


def show_value_counts(df, col, limit=25):
    counts = (
        df[col]
        .map(format_display_value)
        .loc[lambda values: values != ""]
        .value_counts()
        .head(limit)
    )
    if counts.empty:
        st.info(f"No values available for {col}.")
        return
    st.bar_chart(counts)
    st.dataframe(counts.rename("count"), use_container_width=True)


selected_label = st.sidebar.selectbox("Dataset", list(DATASETS.keys()))
base_name = DATASETS[selected_label]
data_path = resolve_data_path(base_name)

try:
    df = load_named_dataset(base_name)
except Exception as exc:
    st.error(f"Failed to load {data_path}:\n\n{exc}")
    st.stop()

filtered = apply_sidebar_filters(df)
parsed_df = parse_json_rows(filtered)

st.caption(f"Using data: `{data_path}`")

metric_cols = st.columns(4)
metric_cols[0].metric("Rows", f"{len(filtered):,}")
metric_cols[1].metric("Columns", f"{len(filtered.columns):,}")
metric_cols[2].metric("Missing Cells", f"{int(filtered.isna().sum().sum()):,}")
metric_cols[3].metric("Parsed JSON Rows", f"{len(parsed_df):,}")

overview_tab, distribution_tab, parsed_tab, table_tab = st.tabs(
    ["Overview", "Distributions", "Parsed JSON", "Table"]
)

with overview_tab:
    st.subheader("Schema")
    schema = pd.DataFrame(
        {
            "column": filtered.columns,
            "dtype": [str(filtered[col].dtype) for col in filtered.columns],
            "non_null": [int(filtered[col].notna().sum()) for col in filtered.columns],
            "unique": [int(filtered[col].map(format_display_value).nunique()) for col in filtered.columns],
        }
    )
    st.dataframe(schema, use_container_width=True)

    if {"filename", "page_number"}.issubset(filtered.columns):
        st.subheader("Rows by File and Page")
        page_counts = (
            filtered.assign(
                filename_label=filtered["filename"].map(format_display_value),
                page_label=filtered["page_number"].map(format_display_value),
            )
            .groupby(["filename_label", "page_label"])
            .size()
            .reset_index(name="rows")
            .sort_values("rows", ascending=False)
        )
        st.dataframe(page_counts, use_container_width=True)

with distribution_tab:
    candidate_cols = [
        col
        for col in [
            "filename",
            "page_number",
            "model",
            "aspect",
            "aspect_category",
            "sentiment",
            "tone",
            "ontology_uri",
            "check",
            "metadata_check",
        ]
        if col in filtered.columns
    ]

    if candidate_cols:
        selected_col = st.selectbox("Column", candidate_cols)
        show_value_counts(filtered, selected_col)
    else:
        st.info("No categorical distribution columns found for this dataset.")

    numeric_cols = filtered.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        st.subheader("Numeric Summary")
        st.dataframe(filtered[numeric_cols].describe().T, use_container_width=True)

with parsed_tab:
    if parsed_df.empty:
        st.info("No JSON-like rows were parsed from the selected data.")
    else:
        st.subheader("Parsed Records")
        st.dataframe(parsed_df, use_container_width=True)

        parsed_cols = [
            col for col in ["aspect", "aspect_category", "sentiment", "tone"]
            if col in parsed_df.columns
        ]
        if parsed_cols:
            selected_parsed_col = st.selectbox("Parsed Column", parsed_cols)
            show_value_counts(parsed_df, selected_parsed_col)

with table_tab:
    st.subheader("Filtered Table")
    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered CSV",
        csv,
        file_name=f"{base_name}_filtered.csv",
        mime="text/csv",
    )
