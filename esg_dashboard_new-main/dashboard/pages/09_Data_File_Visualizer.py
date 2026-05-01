import json
import re
from pathlib import Path

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

MAPPING_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "aspect_category_group_mapping.json"
)


st.set_page_config(page_title="Data File Visualizer", layout="wide")
st.title("Data File Visualizer")


@st.cache_data
def load_named_dataset(base_name):
    return read_dataset(base_name)


@st.cache_data
def load_aspect_category_group_mapping():
    with open(MAPPING_PATH) as f:
        mapping_config = json.load(f)

    aliases = {}
    for group, meta in mapping_config.get("groups", {}).items():
        aliases[group.strip().lower()] = group
        for alias in meta.get("aliases", []):
            aliases[str(alias).strip().lower()] = group
    return mapping_config, aliases


def normalize_aspect_category_group(value, alias_map):
    key = format_display_value(value).lower()
    if not key:
        return ""
    return alias_map.get(key, "Others")


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


def add_aspect_category_group(df, alias_map):
    if "aspect_category" not in df.columns:
        return df

    mapped = df.copy()
    if "aspect_category_raw" not in mapped.columns:
        mapped["aspect_category_raw"] = mapped["aspect_category"]
    mapped["aspect_category_group"] = mapped["aspect_category"].apply(
        lambda value: normalize_aspect_category_group(value, alias_map)
    )
    return mapped


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
    counts = make_value_counts(df, col, limit=limit)
    if counts.empty:
        st.info(f"No values available for {col}.")
        return
    st.bar_chart(counts)
    st.dataframe(counts.rename("count"), use_container_width=True)


def make_value_counts(df, col, limit=25, sort_order="Count descending"):
    counts = (
        df[col]
        .map(format_display_value)
        .loc[lambda values: values != ""]
        .value_counts()
    )
    if sort_order == "Count ascending":
        counts = counts.sort_values(ascending=True)
    elif sort_order == "Label A-Z":
        counts = counts.sort_index(ascending=True)
    elif sort_order == "Label Z-A":
        counts = counts.sort_index(ascending=False)
    else:
        counts = counts.sort_values(ascending=False)
    return counts.head(limit)


def sort_value_counts(counts, sort_order="Count descending"):
    if sort_order == "Count ascending":
        return counts.sort_values(ascending=True)
    if sort_order == "Label A-Z":
        return counts.sort_index(ascending=True)
    if sort_order == "Label Z-A":
        return counts.sort_index(ascending=False)
    return counts.sort_values(ascending=False)


def parsed_dimension_columns(df):
    excluded = {"sentence", "text", "reasoning", "markdown_full", "cleaned_markdown"}
    columns = []
    for col in df.columns:
        if col in excluded:
            continue
        values = df[col].map(format_display_value)
        values = values[values != ""]
        if values.empty:
            continue
        columns.append(col)
    return columns


selected_label = st.sidebar.selectbox("Dataset", list(DATASETS.keys()))
base_name = DATASETS[selected_label]
data_path = resolve_data_path(base_name)

try:
    df = load_named_dataset(base_name)
except Exception as exc:
    st.error(f"Failed to load {data_path}:\n\n{exc}")
    st.stop()

mapping_config, aspect_category_alias_map = load_aspect_category_group_mapping()
df = add_aspect_category_group(df, aspect_category_alias_map)
filtered = apply_sidebar_filters(df)
parsed_df = add_aspect_category_group(
    parse_json_rows(filtered),
    aspect_category_alias_map,
)

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
            "aspect_category_group",
            "aspect_category",
            "aspect_category_raw",
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

        parsed_cols = parsed_dimension_columns(parsed_df)
        if parsed_cols:
            default_col = "aspect_category_group" if "aspect_category_group" in parsed_cols else "aspect"
            default_idx = parsed_cols.index(default_col) if default_col in parsed_cols else 0
            selected_parsed_col = st.selectbox(
                "Parsed Column",
                parsed_cols,
                index=default_idx,
            )
            control_cols = st.columns(3)
            with control_cols[0]:
                top_n = st.slider(
                    "Top Values",
                    5,
                    100,
                    25,
                    key="parsed_top_values",
                )
            with control_cols[1]:
                sort_order = st.selectbox(
                    "Sort",
                    ["Count descending", "Count ascending", "Label A-Z", "Label Z-A"],
                )
            with control_cols[2]:
                table_scope = st.radio(
                    "Table Scope",
                    ["All parsed rows", "Top graph rows"],
                    horizontal=True,
                )

            all_counts = (
                parsed_df[selected_parsed_col]
                .map(format_display_value)
                .loc[lambda values: values != ""]
                .value_counts()
            )
            sorted_counts = sort_value_counts(all_counts, sort_order)
            chart_counts = sorted_counts.head(top_n)
            top_values = set(chart_counts.index)

            if table_scope == "Top graph rows":
                table_df = parsed_df[
                    parsed_df[selected_parsed_col].map(format_display_value).isin(top_values)
                ]
                count_table = chart_counts
            else:
                table_df = parsed_df
                count_table = sorted_counts

            st.subheader("Parsed Row Table")
            st.dataframe(table_df, use_container_width=True)

            if chart_counts.empty:
                st.info(f"No values available for {selected_parsed_col}.")
            else:
                st.subheader("Top Graph")
                st.bar_chart(chart_counts)

                st.subheader("Count Table")
                st.dataframe(count_table.rename("count"), use_container_width=True)

            if selected_parsed_col == "aspect_category_group":
                with st.expander("Aspect Category Group Mapping"):
                    mapping_rows = []
                    for group, meta in mapping_config.get("groups", {}).items():
                        for alias in meta.get("aliases", []):
                            mapping_rows.append({
                                "raw_value": alias,
                                "mapped_group": group,
                                "label": meta.get("label", group),
                            })
                    st.dataframe(pd.DataFrame(mapping_rows), use_container_width=True)
        else:
            st.dataframe(parsed_df, use_container_width=True)

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
