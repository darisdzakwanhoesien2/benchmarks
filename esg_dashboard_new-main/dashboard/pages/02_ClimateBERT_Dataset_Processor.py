import json
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.data_loader import (
    format_display_value,
    load_and_parse,
    resolve_data_path,
    sorted_unique_values,
)


st.set_page_config(page_title="ClimateBERT Dataset Processor", layout="wide")
st.title("ClimateBERT Dataset Processor")
st.caption("Run a local ClimateBERT text-classification model over parsed ESG sentences.")


VPS_MODEL_BIN = Path(
    "/home/ubuntu/apps/benchmarks/model_download/models/"
    "distilroberta-base-climate-detector/pytorch_model.bin"
)
LOCAL_MODEL_DIR = Path(__file__).resolve().parents[3] / "model_download" / "models"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "data" / "climatebert_predictions.csv"


def default_model_path() -> str:
    if VPS_MODEL_BIN.exists():
        return str(VPS_MODEL_BIN)

    candidates = [
        LOCAL_MODEL_DIR / "distilroberta-base-climate-detector",
        LOCAL_MODEL_DIR / "distilroberta-base-climate-sentiment",
        LOCAL_MODEL_DIR / "distilroberta-base-climate-commitment",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(VPS_MODEL_BIN)


def normalize_model_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.name in {"pytorch_model.bin", "model.safetensors"}:
        return path.parent
    return path


@st.cache_data(show_spinner=False)
def load_parsed_dataset() -> pd.DataFrame:
    df = load_and_parse()
    for col in ["filename", "model", "aspect", "aspect_category", "sentiment", "tone"]:
        if col in df.columns:
            df[col] = df[col].map(format_display_value)
    if "sentence" in df.columns:
        df["sentence"] = df["sentence"].map(format_display_value)
        df = df[df["sentence"] != ""].reset_index(drop=True)
    return df


@st.cache_resource(show_spinner=False)
def load_local_classifier(model_dir: str, device: int):
    from transformers import pipeline

    return pipeline(
        task="text-classification",
        model=model_dir,
        tokenizer=model_dir,
        top_k=None,
        device=device,
        truncation=True,
    )


def flatten_prediction(prediction):
    if isinstance(prediction, list) and len(prediction) == 1 and isinstance(prediction[0], list):
        prediction = prediction[0]
    if isinstance(prediction, dict):
        prediction = [prediction]
    if not isinstance(prediction, list):
        return {"label": "UNKNOWN", "score": None, "raw_prediction": json.dumps(prediction)}

    scored = [
        item for item in prediction
        if isinstance(item, dict) and "label" in item and "score" in item
    ]
    if not scored:
        return {"label": "UNKNOWN", "score": None, "raw_prediction": json.dumps(prediction)}

    best = max(scored, key=lambda item: float(item.get("score") or 0.0))
    row = {
        "label": best.get("label"),
        "score": float(best.get("score") or 0.0),
        "raw_prediction": json.dumps(scored, ensure_ascii=False),
    }
    for item in scored:
        label = str(item.get("label", "")).strip().lower().replace(" ", "_")
        if label:
            row[f"score_{label}"] = float(item.get("score") or 0.0)
    return row


def run_batches(classifier, sentences: list[str], batch_size: int) -> list[dict]:
    rows = []
    progress = st.progress(0)
    status = st.empty()
    total = len(sentences)

    for start in range(0, total, batch_size):
        batch = sentences[start:start + batch_size]
        outputs = classifier(batch, batch_size=batch_size, truncation=True)
        if isinstance(outputs, dict):
            outputs = [outputs]
        rows.extend(flatten_prediction(output) for output in outputs)
        done = min(start + len(batch), total)
        progress.progress(done / total)
        status.caption(f"Processed {done:,} / {total:,} sentences")

    status.empty()
    progress.empty()
    return rows


try:
    source_path = resolve_data_path("data_output")
    df = load_parsed_dataset()
except Exception as exc:
    st.error(f"Failed to load parsed `data_output` dataset.\n\n{exc}")
    st.stop()

st.caption(f"Using data: `{source_path}`")
st.success(f"Loaded {len(df):,} parsed ESG sentence records")

if "sentence" not in df.columns:
    st.error("The parsed dataset does not contain a `sentence` column.")
    st.stop()

with st.sidebar:
    st.header("Model")
    model_path_input = st.text_input(
        "Local model path",
        value=default_model_path(),
        help="Use the model directory or the pytorch_model.bin/model.safetensors path.",
    )
    model_dir = normalize_model_path(model_path_input)
    st.caption(f"Resolved model directory: `{model_dir}`")

    device_label = st.radio("Device", ["CPU", "CUDA 0"], horizontal=True)
    device = 0 if device_label == "CUDA 0" else -1

    st.header("Dataset")
    dedupe = st.checkbox("Deduplicate repeated sentences", value=True)
    max_rows = st.number_input("Maximum sentences", min_value=1, value=1000, step=500)
    batch_size = st.number_input("Batch size", min_value=1, value=16, step=8)

    st.header("Filters")
    selected = {}
    for col in ["filename", "model", "aspect_category", "sentiment", "tone"]:
        if col in df.columns:
            values = sorted_unique_values(df[col])
            selected[col] = st.multiselect(col.replace("_", " ").title(), values)


filtered = df.copy()
for col, values in selected.items():
    if values:
        filtered = filtered[filtered[col].map(format_display_value).isin(values)]

if dedupe:
    filtered = filtered.drop_duplicates(subset=["sentence"]).reset_index(drop=True)

filtered = filtered.head(int(max_rows)).reset_index(drop=True)

left, mid, right = st.columns(3)
left.metric("Ready for inference", f"{len(filtered):,}")
mid.metric("Unique sentences", f"{filtered['sentence'].nunique():,}")
right.metric("Batch size", int(batch_size))

preview_cols = [
    col for col in [
        "sentence", "aspect", "aspect_category", "sentiment", "tone", "filename", "model"
    ]
    if col in filtered.columns
]
st.dataframe(filtered[preview_cols].head(100), use_container_width=True, height=360)

run = st.button("Run ClimateBERT on Selected Sentences", type="primary", disabled=filtered.empty)

if run:
    if not model_dir.exists():
        st.error(f"Model directory does not exist: `{model_dir}`")
        st.stop()

    required_tokenizer_files = ["config.json", "tokenizer_config.json"]
    missing = [name for name in required_tokenizer_files if not (model_dir / name).exists()]
    if missing:
        st.warning(
            "This model directory may be incomplete. Missing: "
            + ", ".join(f"`{name}`" for name in missing)
        )

    try:
        with st.spinner(f"Loading ClimateBERT from `{model_dir}`..."):
            classifier = load_local_classifier(str(model_dir), device)

        sentences = filtered["sentence"].astype(str).tolist()
        with st.spinner("Running ClimateBERT inference..."):
            prediction_rows = run_batches(classifier, sentences, int(batch_size))

        prediction_df = pd.DataFrame(prediction_rows)
        result = pd.concat([filtered.reset_index(drop=True), prediction_df], axis=1)
        st.session_state["climatebert_result"] = result
        st.success(f"Generated ClimateBERT predictions for {len(result):,} sentences")
    except Exception as exc:
        st.error(f"ClimateBERT inference failed:\n\n{exc}")


result = st.session_state.get("climatebert_result")
if isinstance(result, pd.DataFrame) and not result.empty:
    tab_table, tab_summary, tab_export = st.tabs(["Predictions", "Summary", "Export"])

    with tab_table:
        display_cols = [
            col for col in [
                "sentence", "label", "score", "aspect", "aspect_category",
                "sentiment", "tone", "filename", "model"
            ]
            if col in result.columns
        ]
        st.dataframe(result[display_cols], use_container_width=True, height=520)

    with tab_summary:
        st.subheader("Prediction Labels")
        st.bar_chart(result["label"].value_counts())

        score_cols = [col for col in result.columns if col.startswith("score_")]
        if score_cols:
            st.subheader("Average Class Scores")
            st.bar_chart(result[score_cols].mean().sort_values(ascending=False))

        if "aspect_category" in result.columns:
            st.subheader("Labels by Aspect Category")
            pivot = pd.crosstab(result["aspect_category"], result["label"])
            st.dataframe(pivot, use_container_width=True)

    with tab_export:
        csv_bytes = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="climatebert_predictions.csv",
            mime="text/csv",
            use_container_width=True,
        )

        output_path = st.text_input("Optional server output path", value=str(DEFAULT_OUTPUT))
        if st.button("Save CSV on Server", use_container_width=True):
            try:
                target = Path(output_path).expanduser()
                target.parent.mkdir(parents=True, exist_ok=True)
                result.to_csv(target, index=False)
                st.success(f"Saved predictions to `{target}`")
            except Exception as exc:
                st.error(f"Could not save CSV: {exc}")
