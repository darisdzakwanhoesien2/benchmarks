from pathlib import Path

import pandas as pd
import streamlit as st

from utils.data_loader import (
    format_display_value,
    load_and_parse,
    resolve_data_path,
    sorted_unique_values,
)


st.set_page_config(page_title="ClimateBERT Result Visualizer", layout="wide")
st.title("ClimateBERT Result Visualizer")
st.caption("Visualize parsed ESG records together with saved ClimateBERT shard outputs.")


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "data" / "climatebert_predictions"


@st.cache_data(show_spinner=False)
def load_parsed_records() -> pd.DataFrame:
    df = load_and_parse()
    for col in df.columns:
        if col in {"filename", "model", "sentence", "aspect", "aspect_category", "sentiment", "tone"}:
            df[col] = df[col].map(format_display_value)
    if "sentence" in df.columns:
        df = df[df["sentence"] != ""].reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_prediction_files(output_dir: str) -> pd.DataFrame:
    root = Path(output_dir).expanduser()
    if not root.exists():
        return pd.DataFrame()

    frames = []
    for path in sorted(root.glob("*.csv")):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        df["result_file"] = path.name
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


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


try:
    data_path = resolve_data_path("data_output")
    parsed = load_parsed_records()
except Exception as exc:
    st.error(f"Could not load parsed `data_output` records.\n\n{exc}")
    st.stop()


with st.sidebar:
    st.header("Data")
    output_dir_input = st.text_input("Prediction output directory", value=str(DEFAULT_OUTPUT_DIR))
    if st.button("Refresh saved outputs", use_container_width=True):
        load_prediction_files.clear()
        st.rerun()


predictions = load_prediction_files(output_dir_input)

st.caption(f"Existing data: `{data_path}`")
st.caption(f"Prediction outputs: `{output_dir_input}`")

overview_cols = st.columns(4)
overview_cols[0].metric("Parsed ESG records", f"{len(parsed):,}")
overview_cols[1].metric("Parsed unique sentences", f"{parsed['sentence'].nunique():,}" if "sentence" in parsed.columns else "0")
overview_cols[2].metric("Prediction rows", f"{len(predictions):,}")
overview_cols[3].metric("Prediction files", f"{predictions['result_file'].nunique():,}" if "result_file" in predictions.columns else "0")


if predictions.empty:
    st.warning("No saved ClimateBERT prediction CSV files found yet.")
    st.dataframe(parsed.head(5000), use_container_width=True, height=520)
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


if "sentence" in filtered_predictions.columns and "sentence" in filtered_parsed.columns:
    merged = filtered_predictions.merge(
        filtered_parsed.drop_duplicates(subset=["sentence"]),
        on="sentence",
        how="left",
        suffixes=("", "_parsed"),
    )
else:
    merged = filtered_predictions.copy()


tab_summary, tab_models, tab_files, tab_merged, tab_existing = st.tabs([
    "Summary",
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

    if {"aspect_category", "label"}.issubset(merged.columns):
        st.subheader("Climate Labels by Existing Aspect Category")
        st.dataframe(pd.crosstab(merged["aspect_category"], merged["label"]), use_container_width=True)


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

    if {"filename", "label"}.issubset(merged.columns):
        st.subheader("Top Source Files by Climate Label")
        file_pivot = pd.crosstab(merged["filename"], merged["label"])
        file_pivot["total"] = file_pivot.sum(axis=1)
        file_pivot = file_pivot.sort_values("total", ascending=False).drop(columns=["total"]).head(50)
        st.dataframe(file_pivot, use_container_width=True)


with tab_merged:
    st.dataframe(merged.head(10000), use_container_width=True, height=620)
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
    st.dataframe(filtered_parsed.head(10000), use_container_width=True, height=620)
