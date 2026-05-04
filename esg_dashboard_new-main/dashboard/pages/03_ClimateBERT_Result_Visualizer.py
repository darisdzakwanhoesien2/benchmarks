from pathlib import Path
import re

import pandas as pd
import streamlit as st

from utils.data_loader import (
    format_display_value,
    parse_esg_json,
    resolve_data_path,
    sorted_unique_values,
)


st.set_page_config(page_title="ClimateBERT Result Visualizer", layout="wide")
st.title("ClimateBERT Result Visualizer")
st.caption("Visualize parsed ESG records together with saved ClimateBERT shard outputs.")


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "data" / "climatebert_predictions"
PARSED_USECOLS = {
    "text",
    "filename",
    "model",
    "page_number",
    "filename_index",
}
PREDICTION_BASE_COLUMNS = {
    "sentence",
    "label",
    "score",
    "aspect",
    "aspect_category",
    "sentiment",
    "tone",
    "filename",
    "model",
    "climatebert_model_name",
    "climatebert_model_dir",
    "worker_count",
    "worker_index",
    "result_file",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "model"


def load_parsed_records(path: str) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0)
    usecols = [col for col in PARSED_USECOLS if col in header.columns]
    raw_df = pd.read_csv(path, usecols=usecols)
    if "text" not in raw_df.columns:
        return pd.DataFrame()

    raw_df["parsed"] = raw_df["text"].apply(parse_esg_json)
    exploded = raw_df.explode("parsed", ignore_index=True)
    parsed_df = pd.json_normalize(exploded["parsed"])
    meta_cols = [col for col in raw_df.columns if col not in {"text", "parsed"}]
    df = pd.concat([exploded[meta_cols].reset_index(drop=True), parsed_df], axis=1)

    for col in df.columns:
        if col in {"filename", "model", "sentence", "aspect", "aspect_category", "sentiment", "tone"}:
            df[col] = df[col].map(format_display_value)
    if "sentence" in df.columns:
        df = df[df["sentence"] != ""].reset_index(drop=True)
    return df


def load_prediction_files(output_dir: str, include_class_scores: bool) -> pd.DataFrame:
    root = Path(output_dir).expanduser()
    if not root.exists():
        return pd.DataFrame()

    frames = []
    for path in sorted(root.glob("*.csv")):
        try:
            header = pd.read_csv(path, nrows=0)
            allowed = set(PREDICTION_BASE_COLUMNS)
            if include_class_scores:
                allowed.update(col for col in header.columns if col.startswith("score_"))
            usecols = [col for col in header.columns if col in allowed]
            df = pd.read_csv(path, usecols=usecols)
        except Exception:
            continue
        df["result_file"] = path.name
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    if "climatebert_model_name" not in combined.columns and "result_file" in combined.columns:
        combined["climatebert_model_name"] = (
            combined["result_file"]
            .map(format_display_value)
            .str.replace(r"^climatebert_", "", regex=True)
            .str.replace(r"_workers\d+_worker\d+\.csv$", "", regex=True)
        )
    return combined


def confidence_bins(series: pd.Series, bins: int = 10) -> pd.DataFrame:
    scores = pd.to_numeric(series, errors="coerce").dropna()
    if scores.empty:
        return pd.DataFrame(columns=["confidence_range", "count"])
    counts = pd.cut(scores, bins=bins).value_counts().sort_index()
    return pd.DataFrame({
        "confidence_range": [str(idx) for idx in counts.index],
        "count": counts.to_numpy(),
    })


def apply_multiselect_filter(df: pd.DataFrame, col: str, label: str) -> pd.DataFrame:
    if col not in df.columns:
        return df
    values = sorted_unique_values(df[col])
    selected = st.sidebar.multiselect(label, values)
    if not selected:
        return df
    return df[df[col].map(format_display_value).isin(selected)]


def coverage_by_model(base_df: pd.DataFrame, pred_df: pd.DataFrame) -> pd.DataFrame:
    if "sentence" not in base_df.columns or pred_df.empty or "sentence" not in pred_df.columns:
        return pd.DataFrame(columns=["model", "processed", "not_processed", "total", "coverage_pct"])

    base_sentences = set(base_df["sentence"].map(format_display_value))
    total = len(base_sentences)
    model_col = "climatebert_model_name" if "climatebert_model_name" in pred_df.columns else "result_file"

    rows = []
    for model, part in pred_df.groupby(model_col):
        processed_sentences = set(part["sentence"].map(format_display_value))
        processed = len(base_sentences & processed_sentences)
        rows.append({
            "model": format_display_value(model),
            "processed": processed,
            "not_processed": max(total - processed, 0),
            "total": total,
            "coverage_pct": round((processed / total) * 100, 2) if total else 0.0,
        })
    return pd.DataFrame(rows).sort_values(["coverage_pct", "processed"], ascending=False)


def not_processed_table(base_df: pd.DataFrame, pred_df: pd.DataFrame, model: str) -> pd.DataFrame:
    if "sentence" not in base_df.columns or "sentence" not in pred_df.columns:
        return base_df.head(0)
    model_col = "climatebert_model_name" if "climatebert_model_name" in pred_df.columns else "result_file"
    processed = set(
        pred_df[pred_df[model_col].map(format_display_value) == model]["sentence"].map(format_display_value)
    )
    return base_df[~base_df["sentence"].map(format_display_value).isin(processed)].reset_index(drop=True)


try:
    data_path = resolve_data_path("data_output")
except Exception as exc:
    st.error(f"Could not resolve `data_output` records.\n\n{exc}")
    st.stop()


with st.sidebar:
    st.header("Data")
    output_dir_input = st.text_input("Prediction output directory", value=str(DEFAULT_OUTPUT_DIR))
    include_class_scores = st.checkbox(
        "Load per-class score columns",
        value=False,
        help="Turn this off to reduce RAM. Overall label and confidence charts still work.",
    )
    table_limit = st.number_input("Table preview row limit", min_value=100, value=3000, step=500)
    build_merged_table = st.checkbox(
        "Build merged prediction + source table",
        value=False,
        help="This can use much more RAM. Enable only when you need the merged table/download.",
    )
    if st.button("Refresh saved outputs", use_container_width=True):
        st.rerun()


parsed = load_parsed_records(str(data_path))
predictions = load_prediction_files(output_dir_input, include_class_scores)

st.caption(f"Existing data: `{data_path}`")
st.caption(f"Prediction outputs: `{output_dir_input}`")

overview_cols = st.columns(4)
overview_cols[0].metric("Parsed ESG records", f"{len(parsed):,}")
overview_cols[1].metric("Parsed unique sentences", f"{parsed['sentence'].nunique():,}" if "sentence" in parsed.columns else "0")
overview_cols[2].metric("Prediction rows", f"{len(predictions):,}")
overview_cols[3].metric("Prediction files", f"{predictions['result_file'].nunique():,}" if "result_file" in predictions.columns else "0")


if predictions.empty:
    st.warning("No saved ClimateBERT prediction CSV files found yet.")
    st.dataframe(parsed.head(int(table_limit)), use_container_width=True, height=520)
    st.stop()


with st.sidebar:
    st.header("Prediction Filters")
    filtered_predictions = predictions.copy()
    for col, label in [
        ("climatebert_model_name", "ClimateBERT Model"),
        ("label", "Prediction Label"),
        ("result_file", "Result File"),
        ("worker_index", "Worker"),
    ]:
        filtered_predictions = apply_multiselect_filter(filtered_predictions, col, label)

    st.header("Parsed Data Filters")
    filtered_parsed = parsed.copy()
    for col, label in [
        ("filename", "Source Filename"),
        ("model", "Original LLM Model"),
        ("aspect_category", "Aspect Category"),
        ("sentiment", "Existing Sentiment"),
        ("tone", "Existing Tone"),
    ]:
        filtered_parsed = apply_multiselect_filter(filtered_parsed, col, label)


merged = pd.DataFrame()
if build_merged_table:
    if "sentence" in filtered_predictions.columns and "sentence" in filtered_parsed.columns:
        merged = filtered_predictions.merge(
            filtered_parsed.drop_duplicates(subset=["sentence"]),
            on="sentence",
            how="left",
            suffixes=("", "_parsed"),
        )
    else:
        merged = filtered_predictions.copy()


coverage = coverage_by_model(filtered_parsed, filtered_predictions)


tab_summary, tab_coverage, tab_models, tab_files, tab_merged, tab_existing = st.tabs([
    "Summary",
    "Coverage",
    "Models",
    "Files & Workers",
    "Merged Table",
    "Existing Data",
])


with tab_summary:
    cols = st.columns(4)
    cols[0].metric("Filtered predictions", f"{len(filtered_predictions):,}")
    if "sentence" in filtered_predictions.columns:
        cols[1].metric("Filtered unique sentences", f"{filtered_predictions['sentence'].nunique():,}")
    if "climatebert_model_name" in filtered_predictions.columns:
        cols[2].metric("Filtered models", f"{filtered_predictions['climatebert_model_name'].nunique():,}")
    if "label" in filtered_predictions.columns:
        cols[3].metric("Filtered labels", f"{filtered_predictions['label'].nunique():,}")

    if "label" in filtered_predictions.columns:
        left, right = st.columns(2)
        with left:
            st.subheader("Prediction Labels")
            st.bar_chart(filtered_predictions["label"].value_counts())
        with right:
            st.subheader("Confidence Distribution")
            bins = confidence_bins(filtered_predictions.get("score", pd.Series(dtype=float)))
            if bins.empty:
                st.caption("No numeric confidence scores available.")
            else:
                st.bar_chart(bins, x="confidence_range", y="count")

    if {"aspect_category", "label"}.issubset(filtered_predictions.columns):
        st.subheader("Climate Labels by Existing Aspect Category")
        st.dataframe(
            pd.crosstab(filtered_predictions["aspect_category"], filtered_predictions["label"]),
            use_container_width=True,
        )

    st.subheader("Existing Data Distribution")
    dist_cols = st.columns(3)
    for idx, col in enumerate(["aspect_category", "sentiment", "tone"]):
        if col in filtered_parsed.columns:
            with dist_cols[idx]:
                st.bar_chart(filtered_parsed[col].map(format_display_value).value_counts().head(25))


with tab_coverage:
    st.subheader("Processed vs Not Processed")
    if coverage.empty:
        st.caption("No coverage can be computed yet.")
    else:
        st.dataframe(coverage, use_container_width=True)
        st.bar_chart(coverage.set_index("model")[["processed", "not_processed"]])

        model_options = coverage["model"].tolist()
        selected_model = st.selectbox("Show not-processed records for model", model_options)
        leftover = not_processed_table(filtered_parsed, filtered_predictions, selected_model)
        cols = st.columns(3)
        cols[0].metric("Model", selected_model)
        cols[1].metric("Not processed", f"{len(leftover):,}")
        cols[2].metric("Processed", f"{int(coverage[coverage['model'] == selected_model]['processed'].iloc[0]):,}")

        display_cols = [
            col for col in [
                "sentence", "aspect", "aspect_category", "sentiment", "tone", "filename", "model"
            ]
            if col in leftover.columns
        ]
        st.dataframe(leftover[display_cols].head(5000), use_container_width=True, height=520)
        st.download_button(
            "Download not-processed CSV",
            data=leftover.to_csv(index=False).encode("utf-8"),
            file_name=f"not_processed_{slugify(selected_model)}.csv",
            mime="text/csv",
            use_container_width=True,
        )


with tab_models:
    if {"climatebert_model_name", "label"}.issubset(filtered_predictions.columns):
        st.subheader("Labels by ClimateBERT Model")
        model_pivot = pd.crosstab(filtered_predictions["climatebert_model_name"], filtered_predictions["label"])
        st.dataframe(model_pivot, use_container_width=True)
        st.bar_chart(model_pivot)

    score_cols = [col for col in filtered_predictions.columns if col.startswith("score_")]
    if score_cols and "climatebert_model_name" in filtered_predictions.columns:
        st.subheader("Average Class Scores by Model")
        avg_scores = filtered_predictions.groupby("climatebert_model_name")[score_cols].mean(numeric_only=True)
        st.dataframe(avg_scores, use_container_width=True)


with tab_files:
    if "result_file" in filtered_predictions.columns:
        st.subheader("Rows by Result File")
        file_counts = filtered_predictions["result_file"].value_counts().rename_axis("result_file").reset_index(name="rows")
        st.dataframe(file_counts, use_container_width=True)
        st.bar_chart(file_counts, x="result_file", y="rows")

    if "worker_index" in filtered_predictions.columns:
        st.subheader("Rows by Worker")
        worker_counts = filtered_predictions["worker_index"].value_counts().sort_index()
        st.bar_chart(worker_counts)

    if {"filename", "label"}.issubset(filtered_predictions.columns):
        st.subheader("Top Source Files by Climate Label")
        file_pivot = pd.crosstab(filtered_predictions["filename"], filtered_predictions["label"])
        file_pivot["total"] = file_pivot.sum(axis=1)
        file_pivot = file_pivot.sort_values("total", ascending=False).drop(columns=["total"]).head(50)
        st.dataframe(file_pivot, use_container_width=True)


with tab_merged:
    if not build_merged_table:
        st.info("Enable `Build merged prediction + source table` in the sidebar to load this RAM-heavy view.")
    elif merged.empty:
        st.caption("No merged rows available.")
    else:
        st.dataframe(merged.head(int(table_limit)), use_container_width=True, height=620)
        st.download_button(
            "Download filtered merged CSV",
            data=merged.to_csv(index=False).encode("utf-8"),
            file_name="climatebert_merged_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )


with tab_existing:
    st.subheader("Parsed data_output.txt Records")
    if "aspect_category" in filtered_parsed.columns:
        st.bar_chart(filtered_parsed["aspect_category"].value_counts())
    st.dataframe(filtered_parsed.head(int(table_limit)), use_container_width=True, height=620)
