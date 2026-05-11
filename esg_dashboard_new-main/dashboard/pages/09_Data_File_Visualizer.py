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
ASPECT_GROUPINGS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "aspect_groupings.json"
)
CUSTOM_ASPECT_GROUPINGS_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "custom_aspect_groupings.json"
)
REPORTING_FRAMEWORK_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "reporting_framework_aspects.json"
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


@st.cache_data
def load_aspect_groupings():
    with open(ASPECT_GROUPINGS_PATH) as f:
        mapping_config = json.load(f)
    return mapping_config


@st.cache_data
def load_custom_aspect_groupings():
    if not CUSTOM_ASPECT_GROUPINGS_PATH.exists():
        return {"aspect_groupings": {}}
    with open(CUSTOM_ASPECT_GROUPINGS_PATH) as f:
        return json.load(f)


@st.cache_data
def load_reporting_framework_aspects():
    with open(REPORTING_FRAMEWORK_PATH) as f:
        mapping_config = json.load(f)
    return mapping_config


def normalize_aspect_category_group(value, alias_map):
    key = format_display_value(value).lower()
    if not key:
        return ""
    return alias_map.get(key, "Others")


def merge_aspect_groupings(*configs):
    merged = {"aspect_groupings": {}}
    for config in configs:
        for major_group, subgroups in config.get("aspect_groupings", {}).items():
            merged_major = merged["aspect_groupings"].setdefault(major_group, {})
            for sub_group, keywords in subgroups.items():
                merged_keywords = merged_major.setdefault(sub_group, [])
                existing = {normalize_text(keyword) for keyword in merged_keywords}
                for keyword in keywords:
                    normalized = normalize_text(keyword)
                    if normalized and normalized not in existing:
                        merged_keywords.append(keyword)
                        existing.add(normalized)
    return merged


def save_custom_aspect_groupings(new_mapping):
    existing = load_custom_aspect_groupings()
    merged = merge_aspect_groupings(existing, new_mapping)
    CUSTOM_ASPECT_GROUPINGS_PATH.write_text(
        json.dumps(merged, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    st.cache_data.clear()
    return merged


def normalize_text(value):
    return re.sub(r"\s+", " ", format_display_value(value).lower()).strip()


def map_aspect_group(value, aspect_groupings):
    normalized = normalize_text(value)
    if not normalized:
        return "Other", "other"

    fallback_match = None
    for major_group, subgroups in aspect_groupings.get("aspect_groupings", {}).items():
        for subgroup, keywords in subgroups.items():
            for keyword in keywords:
                normalized_keyword = normalize_text(keyword)
                if normalized_keyword and normalized == normalized_keyword:
                    return major_group, subgroup
                if normalized_keyword and normalized_keyword in normalized:
                    fallback_match = fallback_match or (major_group, subgroup)

    return fallback_match or ("Other", "other")


def flatten_taxonomy(mapping_config, root_key, source_name):
    rows = []
    for major_group, subgroups in mapping_config.get(root_key, {}).items():
        for subgroup, keywords in subgroups.items():
            for keyword in keywords:
                rows.append({
                    "source": source_name,
                    "major_group": major_group,
                    "sub_group": subgroup,
                    "keyword": keyword,
                    "keyword_norm": normalize_text(keyword),
                })
    return rows


def detect_taxonomy_root(mapping_config):
    for root_key in ["aspect_groupings", "reporting_framework_aspects"]:
        if isinstance(mapping_config.get(root_key), dict):
            return root_key
    return None


def flatten_any_taxonomy(mapping_config, source_name):
    root_key = detect_taxonomy_root(mapping_config)
    if not root_key:
        return []
    return flatten_taxonomy(mapping_config, root_key, source_name)


def find_taxonomy_match(value, taxonomy_rows):
    normalized = normalize_text(value)
    if not normalized:
        return None

    fallback_match = None
    for row in taxonomy_rows:
        keyword = row["keyword_norm"]
        if keyword and normalized == keyword:
            return row
        if keyword and keyword in normalized:
            fallback_match = fallback_match or row
    return fallback_match


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
    meta_cols = [col for col in ["source_row_id", "filename", "page_number", "model"] if col in df.columns]
    for _, source_row in df.iterrows():
        parsed_rows = normalize_json(extract_json_block(source_row.get("text")))
        for parsed in parsed_rows:
            if isinstance(parsed, dict):
                row = {col: source_row.get(col) for col in meta_cols}
                row.update(parsed)
                rows.append(row)

    return pd.DataFrame(rows)


def count_parsed_json_objects(text):
    return len(normalize_json(extract_json_block(text)))


def build_source_parse_audit(df):
    audited = df.copy()
    if "source_row_id" not in audited.columns:
        audited["source_row_id"] = audited.index
    if "text" in audited.columns:
        audited["parsed_object_count"] = audited["text"].apply(count_parsed_json_objects)
    else:
        audited["parsed_object_count"] = 0
    audited["source_row_parsed"] = audited["parsed_object_count"] > 0
    audited["parse_status"] = audited["source_row_parsed"].map({True: "parsed", False: "not parsed"})
    return audited


def section_note(title, rqs, usage):
    st.info(f"**{title}** · Supports **{rqs}**. {usage}")


def build_page_coverage(audit_df):
    if not {"filename", "page_number"}.issubset(audit_df.columns):
        return pd.DataFrame(), pd.DataFrame()

    working = audit_df.copy()
    working["filename_label"] = working["filename"].map(format_display_value)
    working["page_label"] = working["page_number"].map(format_display_value)
    working["page_numeric"] = pd.to_numeric(working["page_number"], errors="coerce")

    agg_spec = {
        "source_rows": ("source_row_id", "size"),
        "parsed_source_rows": ("source_row_parsed", "sum"),
        "parsed_objects": ("parsed_object_count", "sum"),
    }
    if "model" in working.columns:
        agg_spec["models"] = (
            "model",
            lambda values: ", ".join(sorted(set(filter(None, values.map(format_display_value))))[:10]),
        )

    coverage = (
        working.groupby(["filename_label", "page_label"], dropna=False)
        .agg(**agg_spec)
        .reset_index()
    )
    coverage["not_parsed_source_rows"] = coverage["source_rows"] - coverage["parsed_source_rows"]
    coverage["page_status"] = coverage["parsed_objects"].gt(0).map({True: "processed", False: "not parsed"})

    missing_rows = []
    numeric_pages = working.dropna(subset=["page_numeric"])
    for filename, group in numeric_pages.groupby("filename_label"):
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

    return coverage.sort_values(["filename_label", "page_label"]), pd.DataFrame(missing_rows)


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


def add_aspect_groups(df, aspect_groupings):
    if "aspect" not in df.columns:
        return df

    mapped = df.copy()
    groups = mapped["aspect"].apply(
        lambda value: map_aspect_group(value, aspect_groupings)
    )
    mapped["aspect_major_group"] = groups.apply(lambda value: value[0])
    mapped["aspect_sub_group"] = groups.apply(lambda value: value[1])
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


def make_other_aspect_counts(df, taxonomy_rows=None):
    required_cols = {"aspect", "aspect_major_group"}
    if not required_cols.issubset(df.columns):
        return pd.DataFrame()

    other_df = df[
        df["aspect_major_group"].map(format_display_value).str.lower().eq("other")
    ].copy()
    if other_df.empty:
        return pd.DataFrame()

    other_df["aspect_label"] = other_df["aspect"].map(format_display_value)
    other_df = other_df[other_df["aspect_label"] != ""]
    if other_df.empty:
        return pd.DataFrame()

    aggregations = {"count": ("aspect_label", "size")}
    for col in ["aspect_category_group", "aspect_category_raw", "sentiment", "tone"]:
        if col in other_df.columns:
            aggregations[col] = (
                col,
                lambda values: ", ".join(sorted(set(filter(None, values.map(format_display_value))))[:8]),
            )

    counts = (
        other_df
        .groupby("aspect_label")
        .agg(**aggregations)
        .reset_index()
        .rename(columns={"aspect_label": "aspect"})
        .sort_values(["count", "aspect"], ascending=[False, True])
    )

    if taxonomy_rows:
        matches = counts["aspect"].apply(lambda value: find_taxonomy_match(value, taxonomy_rows))
        counts["suggested_source"] = matches.apply(lambda match: match["source"] if match else "")
        counts["suggested_major_group"] = matches.apply(lambda match: match["major_group"] if match else "")
        counts["suggested_sub_group"] = matches.apply(lambda match: match["sub_group"] if match else "")
        counts["suggested_keyword"] = matches.apply(lambda match: match["keyword"] if match else "")

    return counts


def build_other_aspect_json_suggestion(other_counts):
    if other_counts.empty:
        return {}
    if {"suggested_major_group", "suggested_sub_group"}.issubset(other_counts.columns):
        suggested = other_counts[
            (other_counts["suggested_major_group"] != "")
            & (other_counts["suggested_sub_group"] != "")
        ]
        if not suggested.empty:
            aspect_groupings = {}
            for _, row in suggested.iterrows():
                major_group = row["suggested_major_group"]
                sub_group = row["suggested_sub_group"]
                aspect_groupings.setdefault(major_group, {}).setdefault(sub_group, [])
                aspect_groupings[major_group][sub_group].append(row["aspect"])
            return {"aspect_groupings": aspect_groupings}

    return {
        "aspect_groupings": {
            "Needs_Mapping": {
                "review_candidates": other_counts["aspect"].tolist()
            }
        }
    }


def default_custom_taxonomy_text():
    return json.dumps({
        "reporting_framework_aspects": {
            "Environmental": {
                "climate_and_energy": [
                    "carbon footprint",
                    "emissions reduction target",
                    "renewable energy"
                ]
            },
            "Social": {
                "community_impact": [
                    "community engagement",
                    "scholarship program"
                ]
            },
            "Operations_and_Strategy": {
                "business_development": [
                    "real estate development",
                    "business strategy"
                ],
                "stakeholder_relations": [
                    "stakeholder engagement",
                    "supplier sustainability"
                ]
            }
        }
    }, indent=2)


selected_label = st.sidebar.selectbox("Dataset", list(DATASETS.keys()))
base_name = DATASETS[selected_label]
data_path = resolve_data_path(base_name)

try:
    df = load_named_dataset(base_name)
except Exception as exc:
    st.error(f"Failed to load {data_path}:\n\n{exc}")
    st.stop()

df = df.copy()
df["source_row_id"] = df.index
mapping_config, aspect_category_alias_map = load_aspect_category_group_mapping()
aspect_groupings_config = load_aspect_groupings()
custom_aspect_groupings_config = load_custom_aspect_groupings()
combined_aspect_groupings_config = merge_aspect_groupings(
    aspect_groupings_config,
    custom_aspect_groupings_config,
)
reporting_framework_config = load_reporting_framework_aspects()
taxonomy_rows = (
    flatten_taxonomy(combined_aspect_groupings_config, "aspect_groupings", "aspect_groupings")
    + flatten_taxonomy(
        reporting_framework_config,
        "reporting_framework_aspects",
        "reporting_framework_aspects",
    )
)
df = add_aspect_category_group(df, aspect_category_alias_map)
df = add_aspect_groups(df, combined_aspect_groupings_config)
source_audit_df = build_source_parse_audit(df)
filtered = apply_sidebar_filters(df)
filtered_source_audit = build_source_parse_audit(filtered)
parsed_df = add_aspect_category_group(
    parse_json_rows(filtered),
    aspect_category_alias_map,
)
parsed_df = add_aspect_groups(parsed_df, combined_aspect_groupings_config)

st.caption(f"Using data: `{data_path}`")

metric_cols = st.columns(4)
metric_cols[0].metric("Rows", f"{len(filtered):,}")
metric_cols[1].metric("Columns", f"{len(filtered.columns):,}")
metric_cols[2].metric("Missing Cells", f"{int(filtered.isna().sum().sum()):,}")
metric_cols[3].metric("Parsed JSON Rows", f"{len(parsed_df):,}")

overview_tab, distribution_tab, parsed_tab, table_tab, coverage_tab = st.tabs(
    ["Overview", "Distributions", "Parsed JSON", "Table", "Page Coverage & Parse Audit"]
)

with overview_tab:
    section_note(
        "Overview",
        "RQ1, RQ5",
        "Use this section to check the source file schema, missing cells, and whether the selected dataset has the columns needed for traceability.",
    )
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
    section_note(
        "Distributions",
        "RQ2, RQ4, RQ6",
        "Use this section to inspect category balance and detect suspicious skews before using distributions in Chapter 4 or stability discussion.",
    )
    candidate_cols = [
        col
        for col in [
            "filename",
            "page_number",
            "model",
            "aspect",
            "aspect_major_group",
            "aspect_sub_group",
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
    section_note(
        "Parsed JSON",
        "RQ1, RQ2, RQ4",
        "Use this section for actual parsed ESG objects extracted from raw text. If this is empty or much smaller than the raw table, inspect the parse audit tab.",
    )
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

            if selected_parsed_col in {"aspect_major_group", "aspect_sub_group"}:
                with st.expander("Aspect Grouping Taxonomy"):
                    grouping_rows = []
                    for major_group, subgroups in combined_aspect_groupings_config.get("aspect_groupings", {}).items():
                        for subgroup, keywords in subgroups.items():
                            for keyword in keywords:
                                grouping_rows.append({
                                    "major_group": major_group,
                                    "sub_group": subgroup,
                                    "keyword": keyword,
                                })
                    st.dataframe(pd.DataFrame(grouping_rows), use_container_width=True)

                other_counts = make_other_aspect_counts(parsed_df, taxonomy_rows)
                st.subheader("Other Aspect Mapping Workbench")
                if other_counts.empty:
                    st.success("No unmapped aspect values in the current filtered data.")
                else:
                    matched_count = 0
                    if "suggested_major_group" in other_counts.columns:
                        matched_count = int(other_counts["suggested_major_group"].ne("").sum())
                    unmapped_total = int(other_counts["count"].sum())
                    st.caption(
                        f"{len(other_counts):,} unique unmapped aspect values across "
                        f"{unmapped_total:,} parsed rows. "
                        f"{matched_count:,} have a suggested taxonomy match."
                    )
                    other_top_n = st.slider(
                        "Unmapped Top Values",
                        5,
                        min(200, max(5, len(other_counts))),
                        min(50, max(5, len(other_counts))),
                        key="other_aspect_top_values",
                    )
                    top_other = other_counts.head(other_top_n)

                    st.bar_chart(top_other.set_index("aspect")["count"])
                    st.dataframe(other_counts, use_container_width=True)

                    st.subheader("Map Other Values From JSON Input")
                    taxonomy_source = st.radio(
                        "Taxonomy Input",
                        ["Paste JSON", "Saved taxonomies"],
                        horizontal=True,
                        key="other_taxonomy_source",
                    )

                    active_taxonomy_rows = taxonomy_rows
                    parsed_custom_taxonomy = None
                    if taxonomy_source == "Paste JSON":
                        custom_taxonomy_text = st.text_area(
                            "Paste taxonomy JSON",
                            value=default_custom_taxonomy_text(),
                            height=320,
                            key="custom_taxonomy_json",
                        )
                        try:
                            parsed_custom_taxonomy = json.loads(custom_taxonomy_text)
                            active_taxonomy_rows = flatten_any_taxonomy(
                                parsed_custom_taxonomy,
                                "pasted_json",
                            )
                            if active_taxonomy_rows:
                                st.success(
                                    f"Parsed {len(active_taxonomy_rows):,} taxonomy keywords from pasted JSON."
                                )
                            else:
                                st.warning(
                                    "JSON parsed, but no supported taxonomy root was found. "
                                    "Use `aspect_groupings` or `reporting_framework_aspects`."
                                )
                        except json.JSONDecodeError as exc:
                            active_taxonomy_rows = []
                            st.error(f"Invalid JSON: {exc}")

                    rematched_other = make_other_aspect_counts(parsed_df, active_taxonomy_rows)
                    matched_other = rematched_other[
                        rematched_other.get("suggested_major_group", pd.Series(dtype=str)).ne("")
                    ]
                    unmatched_after_input = rematched_other[
                        rematched_other.get("suggested_major_group", pd.Series(dtype=str)).eq("")
                    ]

                    st.subheader("Matches From Active JSON")
                    if matched_other.empty:
                        st.info("No unmapped aspect values matched the active taxonomy JSON.")
                    else:
                        st.dataframe(matched_other, use_container_width=True)

                    with st.expander("Still Unmatched After Active JSON"):
                        st.dataframe(unmatched_after_input, use_container_width=True)

                    suggestion = build_other_aspect_json_suggestion(rematched_other)
                    st.download_button(
                        "Download Matched Mapping JSON",
                        json.dumps(suggestion, indent=2).encode("utf-8"),
                        file_name="matched_aspect_mapping.json",
                        mime="application/json",
                    )
                    with st.expander("Generated Mapping JSON"):
                        st.json(suggestion)

                    if st.button(
                        "Save Generated Mapping To Custom Taxonomy",
                        key="save_generated_aspect_mapping",
                        disabled=not bool(suggestion.get("aspect_groupings")),
                    ):
                        saved_mapping = save_custom_aspect_groupings(suggestion)
                        saved_count = sum(
                            len(keywords)
                            for subgroups in saved_mapping.get("aspect_groupings", {}).values()
                            for keywords in subgroups.values()
                        )
                        st.success(
                            f"Saved custom taxonomy with {saved_count:,} total keywords. Rerunning..."
                        )
                        st.rerun()

                    with st.expander("Active Taxonomy Keywords"):
                        if active_taxonomy_rows:
                            st.dataframe(
                                pd.DataFrame(active_taxonomy_rows).drop(columns=["keyword_norm"]),
                                use_container_width=True,
                            )
                        else:
                            st.info("No active taxonomy keywords available.")
        else:
            st.dataframe(parsed_df, use_container_width=True)

with table_tab:
    section_note(
        "Filtered raw table",
        "RQ1, RQ4, RQ5",
        "Use this section to inspect raw source rows after filters. These rows are not necessarily parsed ESG records; use `parse_status` to distinguish parsed and not parsed rows.",
    )
    st.subheader("Filtered Table")
    table_view = filtered_source_audit.copy()
    parse_status_filter = st.radio(
        "Parse status",
        ["all", "parsed", "not parsed"],
        horizontal=True,
        key="data_file_parse_status_filter",
    )
    if parse_status_filter != "all":
        table_view = table_view[table_view["parse_status"] == parse_status_filter]
    priority_cols = [
        col for col in [
            "source_row_id",
            "parse_status",
            "parsed_object_count",
            "filename",
            "page_number",
            "model",
            "text",
        ]
        if col in table_view.columns
    ]
    remaining_cols = [col for col in table_view.columns if col not in priority_cols]
    st.dataframe(table_view[priority_cols + remaining_cols], use_container_width=True)

    csv = table_view.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered CSV",
        csv,
        file_name=f"{base_name}_filtered.csv",
        mime="text/csv",
    )

with coverage_tab:
    section_note(
        "Page coverage and parse audit",
        "RQ1, RQ4, RQ5",
        "Use this section to see which filename/page combinations were processed, which source rows produced JSON objects, and which pages are missing or unparsed.",
    )
    st.subheader("Parse Status Summary")
    total_source_rows = len(filtered_source_audit)
    parsed_source_rows = int(filtered_source_audit["source_row_parsed"].sum()) if not filtered_source_audit.empty else 0
    not_parsed_source_rows = total_source_rows - parsed_source_rows
    parsed_objects = int(filtered_source_audit["parsed_object_count"].sum()) if not filtered_source_audit.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered source rows", f"{total_source_rows:,}")
    c2.metric("Parsed source rows", f"{parsed_source_rows:,}")
    c3.metric("Not parsed source rows", f"{not_parsed_source_rows:,}")
    c4.metric("Parsed JSON objects", f"{parsed_objects:,}")

    coverage_df, missing_pages_df = build_page_coverage(filtered_source_audit)
    st.subheader("Pages Processed by Filename")
    if coverage_df.empty:
        st.info("Filename/page_number columns are not available for coverage analysis.")
    else:
        st.write(
            "`processed` means at least one source row for that file/page produced JSON objects. "
            "`not parsed` means the file/page exists in the filtered source data but produced no JSON objects."
        )
        st.dataframe(coverage_df, use_container_width=True, height=420)
        st.bar_chart(coverage_df["page_status"].value_counts())

    st.subheader("Missing or Unprocessed Pages")
    if missing_pages_df.empty:
        st.success("No numeric page gaps or unprocessed source pages were detected in the filtered data.")
    else:
        st.dataframe(missing_pages_df, use_container_width=True, height=360)

    st.subheader("Rows Parsed or Not Parsed")
    audit_status = st.radio(
        "Rows to list",
        ["not parsed", "parsed", "all"],
        horizontal=True,
        key="data_file_audit_status_rows",
    )
    audit_view = filtered_source_audit.copy()
    if audit_status != "all":
        audit_view = audit_view[audit_view["parse_status"] == audit_status]
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
        if col in audit_view.columns
    ]
    st.dataframe(audit_view[audit_cols], use_container_width=True, height=520)
