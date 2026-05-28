import json
import gc
import re
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


VPS_MODEL_ROOT = Path("/home/ubuntu/apps/benchmarks/model_download/models")
VPS_MODEL_BIN = VPS_MODEL_ROOT / "distilroberta-base-climate-detector" / "pytorch_model.bin"
LOCAL_MODEL_DIR = Path(__file__).resolve().parents[3] / "model_download" / "models"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "data" / "climatebert_predictions"
MODEL_WEIGHT_NAMES = {"pytorch_model.bin", "model.safetensors"}
HEAVY_SOURCE_COLUMNS = {
    "text",
    "markdown_full",
    "cleaned_markdown",
    "original",
    "pa",
}
SAVED_RESULT_COLUMNS = [
    "sentence",
    "label",
    "score",
    "aspect_category",
    "filename",
    "climatebert_model_dir",
    "climatebert_model_name",
    "worker_count",
    "worker_index",
]


def get_query_int(name: str, default: int) -> int:
    try:
        raw = st.query_params.get(name, default)
    except Exception:
        raw = st.experimental_get_query_params().get(name, [default])[0]
    if isinstance(raw, list):
        raw = raw[0] if raw else default
    try:
        return max(1, int(raw))
    except Exception:
        return default


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "model"


def normalize_model_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.name in MODEL_WEIGHT_NAMES:
        return path.parent
    return path


def default_model_root() -> str:
    if VPS_MODEL_ROOT.exists():
        return str(VPS_MODEL_ROOT)
    if LOCAL_MODEL_DIR.exists():
        return str(LOCAL_MODEL_DIR)
    return str(VPS_MODEL_ROOT)


@st.cache_data(show_spinner=False)
def discover_model_dirs(root_path: str) -> list[dict]:
    root = Path(root_path).expanduser()
    if not root.exists():
        return []

    rows = []
    seen = set()
    for weight in sorted(root.rglob("*")):
        if not weight.is_file() or weight.name not in MODEL_WEIGHT_NAMES:
            continue
        model_dir = weight.parent
        if model_dir in seen:
            continue
        seen.add(model_dir)

        try:
            rel = model_dir.relative_to(root)
        except ValueError:
            rel = model_dir

        top_name = rel.parts[0] if rel.parts else model_dir.name
        missing = [
            name for name in ["config.json", "tokenizer_config.json"]
            if not (model_dir / name).exists()
        ]
        rows.append({
            "label": str(rel),
            "model_name": top_name,
            "model_dir": str(model_dir),
            "weight_file": str(weight),
            "weight_type": weight.name,
            "ready": not missing,
            "missing": ", ".join(missing),
        })
    return rows


def default_model_selection(models: list[dict]) -> str:
    preferred = [
        "distilroberta-base-climate-detector",
        "distilroberta-base-climate-d",
        "distilroberta-base-climate-sentiment",
        "distilroberta-base-climate-commitment",
    ]
    for name in preferred:
        for row in models:
            if name in row["label"]:
                return row["label"]
    return models[0]["label"] if models else str(VPS_MODEL_BIN)


@st.cache_data(show_spinner=False)
def load_parsed_dataset() -> pd.DataFrame:
    df = load_and_parse()
    df = df.drop(columns=[col for col in HEAVY_SOURCE_COLUMNS if col in df.columns])
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


def save_progress_csv(new_rows: pd.DataFrame, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    write_header = not target.exists() or target.stat().st_size == 0
    new_rows.to_csv(target, mode="a", header=write_header, index=False)


def run_batches_with_checkpoints(
    classifier,
    input_df: pd.DataFrame,
    batch_size: int,
    metadata: dict,
    save_path: Path | None = None,
) -> pd.DataFrame:
    rows = []
    progress = st.progress(0)
    status = st.empty()
    total = len(input_df)

    for start in range(0, total, batch_size):
        batch_df = input_df.iloc[start:start + batch_size].reset_index(drop=True)
        sentences = batch_df["sentence"].astype(str).tolist()
        outputs = classifier(sentences, batch_size=batch_size, truncation=True)
        if isinstance(outputs, dict):
            outputs = [outputs]

        prediction_df = pd.DataFrame(flatten_prediction(output) for output in outputs)
        batch_result = pd.concat([batch_df, prediction_df], axis=1)
        for key, value in metadata.items():
            batch_result[key] = value

        rows.append(batch_result)

        if save_path is not None:
            save_progress_csv(batch_result, save_path)

        done = min(start + len(batch_df), total)
        progress.progress(done / total)
        saved_note = f" Saved checkpoint to `{save_path}`." if save_path is not None else ""
        status.caption(f"Processed {done:,} / {total:,} sentences.{saved_note}")

    status.empty()
    progress.empty()
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def shard_dataframe(df: pd.DataFrame, worker_count: int, worker_index: int) -> pd.DataFrame:
    worker_index = min(max(worker_index, 1), worker_count)
    sharded = df.iloc[(worker_index - 1)::worker_count].copy()
    return sharded.reset_index(drop=True)


def make_output_path(output_dir: Path, model_dir: Path, worker_count: int, worker_index: int) -> Path:
    model_slug = slugify(str(model_dir).split("/models/")[-1] if "/models/" in str(model_dir) else model_dir.name)
    return output_dir / f"climatebert_{model_slug}_workers{worker_count}_worker{worker_index}.csv"


def model_name_from_dir(model_dir: Path) -> str:
    model_dir_str = str(model_dir)
    return model_dir_str.split("/models/")[-1] if "/models/" in model_dir_str else model_dir.name


def confidence_bins(series: pd.Series, bins: int = 10) -> pd.DataFrame:
    scores = pd.to_numeric(series, errors="coerce").dropna()
    if scores.empty:
        return pd.DataFrame(columns=["confidence_range", "count"])
    counts = pd.cut(scores, bins=bins).value_counts().sort_index()
    return pd.DataFrame({
        "confidence_range": [str(idx) for idx in counts.index],
        "count": counts.to_numpy(),
    })


@st.cache_data(show_spinner=False)
def read_saved_results(output_dir: str) -> pd.DataFrame:
    root = Path(output_dir).expanduser()
    if not root.exists():
        return pd.DataFrame()

    frames = []
    for path in sorted(root.glob("*.csv")):
        try:
            header = pd.read_csv(path, nrows=0)
            usecols = [col for col in SAVED_RESULT_COLUMNS if col in header.columns]
            part = pd.read_csv(path, usecols=usecols) if usecols else pd.DataFrame()
            part["result_file"] = path.name
            frames.append(part)
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data(show_spinner=False)
def list_saved_result_files(output_dir: str) -> list[dict]:
    root = Path(output_dir).expanduser()
    if not root.exists():
        return []
    rows = []
    for path in sorted(root.glob("*.csv")):
        try:
            stat = path.stat()
            rows.append({
                "file": path.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": pd.Timestamp(stat.st_mtime, unit="s"),
            })
        except Exception:
            continue
    return rows


def processed_sentence_set(saved_df: pd.DataFrame, model_dir: Path) -> set[str]:
    if saved_df.empty or "sentence" not in saved_df.columns:
        return set()

    scoped = saved_df
    model_name = model_name_from_dir(model_dir)
    if "climatebert_model_dir" in scoped.columns:
        scoped = scoped[scoped["climatebert_model_dir"].map(format_display_value) == str(model_dir)]
    elif "climatebert_model_name" in scoped.columns:
        scoped = scoped[scoped["climatebert_model_name"].map(format_display_value) == model_name]
    else:
        model_slug = slugify(model_name)
        if "result_file" in scoped.columns:
            scoped = scoped[scoped["result_file"].map(format_display_value).str.contains(model_slug, na=False)]

    return set(scoped["sentence"].map(format_display_value))


def coverage_rows(base_df: pd.DataFrame, saved_df: pd.DataFrame, model_dirs: list[Path]) -> pd.DataFrame:
    rows = []
    sentences = set(base_df["sentence"].map(format_display_value)) if "sentence" in base_df.columns else set()
    total = len(sentences)
    for model_dir in model_dirs:
        done = processed_sentence_set(saved_df, model_dir)
        processed = len(sentences & done)
        rows.append({
            "model": model_name_from_dir(model_dir),
            "processed": processed,
            "leftover": max(total - processed, 0),
            "total": total,
            "coverage_pct": round((processed / total) * 100, 2) if total else 0.0,
        })
    return pd.DataFrame(rows)


def unload_model_from_memory(model_dir: Path, device: int) -> None:
    load_local_classifier.clear(str(model_dir), device)
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


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
    model_root_input = st.text_input(
        "Model root",
        value=default_model_root(),
        help="The page scans recursively for pytorch_model.bin and model.safetensors.",
    )

    refresh_cols = st.columns(2)
    with refresh_cols[0]:
        if st.button("Refresh Models", use_container_width=True):
            discover_model_dirs.clear()
            st.rerun()
    with refresh_cols[1]:
        if st.button("Clear Loaded", use_container_width=True):
            load_local_classifier.clear()
            st.success("Cleared loaded model cache.")

    discovered_models = discover_model_dirs(model_root_input)

    if discovered_models:
        model_labels = [row["label"] for row in discovered_models]
        default_label = default_model_selection(discovered_models)
        selected_labels = st.multiselect(
            "Discovered models",
            options=model_labels,
            default=[default_label],
            format_func=lambda label: label,
        )
        selected_models = [row for row in discovered_models if row["label"] in selected_labels]
        for selected_model in selected_models[:5]:
            st.caption(f"{selected_model['label']} weight: `{selected_model['weight_file']}`")
            if not selected_model["ready"]:
                st.warning(
                    f"`{selected_model['label']}` may be incomplete. "
                    f"Missing: {selected_model['missing']}"
                )
    else:
        st.warning("No local model weights found under this root.")
        model_path_input = st.text_input(
            "Manual model path",
            value=str(VPS_MODEL_BIN),
            help="Use the model directory or the pytorch_model.bin/model.safetensors path.",
        )
        selected_models = [{
            "label": Path(model_path_input).name,
            "model_dir": str(normalize_model_path(model_path_input)),
            "weight_file": model_path_input,
            "ready": True,
            "missing": "",
        }]

    manual_override = st.text_input(
        "Manual override",
        value="",
        help="Optional. Paste a specific model directory or weight path to override the dropdown.",
    )
    if manual_override.strip():
        override_dir = normalize_model_path(manual_override.strip())
        selected_models = [{
            "label": override_dir.name,
            "model_dir": str(override_dir),
            "weight_file": manual_override.strip(),
            "ready": True,
            "missing": "",
        }]

    model_dirs = [Path(row["model_dir"]) for row in selected_models]
    st.caption(f"Selected model count: **{len(model_dirs)}**")

    device_label = st.radio("Device", ["CPU", "CUDA 0"], horizontal=True)
    device = 0 if device_label == "CUDA 0" else -1
    unload_after_model = st.checkbox(
        "Unload model after each run",
        value=False,
        help="Use this when RAM is tight. It frees memory after each selected model, but reruns must reload the model.",
    )

    st.header("Dataset")
    dedupe = st.checkbox("Deduplicate repeated sentences", value=True)
    max_rows = st.number_input("Maximum sentences before sharding", min_value=1, value=10000, step=1000)
    batch_size = st.number_input("Batch size", min_value=1, value=16, step=8)

    st.header("Parallel Windows")
    query_workers = get_query_int("workers", 1)
    query_worker = get_query_int("worker", 1)
    worker_count = st.number_input("Total windows/workers", min_value=1, value=query_workers, step=1)
    worker_index = st.number_input(
        "This window worker number",
        min_value=1,
        max_value=int(worker_count),
        value=min(query_worker, int(worker_count)),
        step=1,
    )
    st.caption("Example URLs: `?workers=5&worker=1` through `?workers=5&worker=5`.")

    st.header("Output")
    output_dir_input = st.text_input("Output directory", value=str(DEFAULT_OUTPUT_DIR))
    auto_save = st.checkbox("Auto-save this worker CSV after inference", value=True)
    st.caption("When auto-save is enabled, every completed batch is checkpointed to CSV immediately.")
    continue_leftover_only = st.checkbox(
        "Continue from leftover only",
        value=True,
        help="Skip sentences already found in saved CSV outputs for each selected model.",
    )
    st.markdown("**Saved data snapshot**")
    freeze_saved_view = st.checkbox(
        "Freeze current saved-data view",
        value=bool(st.session_state.get("cb_saved_freeze", False)),
        help="When enabled, coverage and leftover checks use a frozen snapshot of current saved CSV data.",
    )
    st.session_state["cb_saved_freeze"] = bool(freeze_saved_view)
    snapshot_cols = st.columns(2)
    with snapshot_cols[0]:
        if st.button("Capture Snapshot", use_container_width=True):
            snapshot_df = read_saved_results(output_dir_input).copy()
            st.session_state["cb_saved_snapshot_df"] = snapshot_df
            st.session_state["cb_saved_snapshot_at"] = pd.Timestamp.utcnow().isoformat()
            st.success(f"Snapshot captured ({len(snapshot_df):,} rows).")
    with snapshot_cols[1]:
        if st.button("Refresh Saved Data", use_container_width=True):
            read_saved_results.clear()
            list_saved_result_files.clear()
            st.session_state.pop("cb_saved_snapshot_df", None)
            st.session_state.pop("cb_saved_snapshot_at", None)
            st.success("Live saved-data view refreshed.")
            st.rerun()

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
worker_df = shard_dataframe(filtered, int(worker_count), int(worker_index))
output_dir = Path(output_dir_input).expanduser()
live_saved_before_run = read_saved_results(str(output_dir))
snapshot_df = st.session_state.get("cb_saved_snapshot_df")
use_snapshot = bool(st.session_state.get("cb_saved_freeze", False)) and isinstance(snapshot_df, pd.DataFrame)
saved_before_run = snapshot_df.copy() if use_snapshot else live_saved_before_run
saved_snapshot_at = st.session_state.get("cb_saved_snapshot_at", "")
saved_files = list_saved_result_files(str(output_dir))
preview_output_paths = [
    make_output_path(output_dir, model_dir, int(worker_count), int(worker_index))
    for model_dir in model_dirs
]
coverage = coverage_rows(filtered, saved_before_run, model_dirs)
worker_coverage = coverage_rows(worker_df, saved_before_run, model_dirs)

metric_cols = st.columns(5)
metric_cols[0].metric("Filtered rows", f"{len(filtered):,}")
metric_cols[1].metric("This worker rows", f"{len(worker_df):,}")
metric_cols[2].metric("Unique sentences", f"{filtered['sentence'].nunique():,}")
metric_cols[3].metric("Workers", int(worker_count))
metric_cols[4].metric("Batch size", int(batch_size))
if use_snapshot:
    st.warning(
        f"Using frozen saved-data snapshot ({len(saved_before_run):,} rows)"
        + (f" captured at `{saved_snapshot_at}`." if saved_snapshot_at else ".")
    )
else:
    st.caption("Using live saved-data view (updates when new CSV files are written).")

st.info(
    f"This window is worker **{int(worker_index)} of {int(worker_count)}**. "
    f"It will process every {int(worker_count)}th row from the filtered dataset for "
    f"**{len(model_dirs)}** selected model(s)."
)
if preview_output_paths:
    st.caption("Output files:")
    for path in preview_output_paths[:10]:
        st.caption(f"`{path}`")

dist_tab, coverage_tab, preview_tab = st.tabs([
    "Data Distribution",
    "Processing Coverage",
    "Worker Preview",
])

with dist_tab:
    chart_cols = st.columns(2)
    for idx, col in enumerate(["aspect_category", "sentiment", "tone", "model"]):
        if col in filtered.columns:
            with chart_cols[idx % 2]:
                st.subheader(col.replace("_", " ").title())
                st.bar_chart(filtered[col].map(format_display_value).value_counts().head(30))

    if "filename" in filtered.columns:
        st.subheader("Top Source Files")
        file_counts = filtered["filename"].map(format_display_value).value_counts().head(30)
        st.bar_chart(file_counts)

with coverage_tab:
    left, right = st.columns(2)
    with left:
        st.subheader("Filtered Dataset Coverage")
        st.dataframe(coverage, use_container_width=True)
    with right:
        st.subheader("This Worker Coverage")
        st.dataframe(worker_coverage, use_container_width=True)

    if not coverage.empty:
        st.subheader("Leftover by Selected Model")
        st.bar_chart(coverage.set_index("model")[["processed", "leftover"]])

    if continue_leftover_only:
        st.caption("Runs will skip already processed sentences separately for each selected model.")

preview_cols = [
    col for col in [
        "sentence", "aspect", "aspect_category", "sentiment", "tone", "filename", "model"
    ]
    if col in filtered.columns
]
with preview_tab:
    st.dataframe(worker_df[preview_cols].head(100), use_container_width=True, height=360)

run = st.button("Run ClimateBERT on This Worker Shard", type="primary", disabled=worker_df.empty)

if run:
    if not model_dirs:
        st.error("Select at least one model.")
        st.stop()

    try:
        all_results = []
        for model_dir in model_dirs:
            if not model_dir.exists():
                st.error(f"Model directory does not exist: `{model_dir}`")
                continue

            required_tokenizer_files = ["config.json", "tokenizer_config.json"]
            missing = [name for name in required_tokenizer_files if not (model_dir / name).exists()]
            if missing:
                st.warning(
                    f"`{model_dir}` may be incomplete. Missing: "
                    + ", ".join(f"`{name}`" for name in missing)
                )

            with st.spinner(f"Loading model from `{model_dir}`..."):
                classifier = load_local_classifier(str(model_dir), device)

            model_worker_df = worker_df
            if continue_leftover_only:
                done_sentences = processed_sentence_set(saved_before_run, model_dir)
                model_worker_df = worker_df[
                    ~worker_df["sentence"].map(format_display_value).isin(done_sentences)
                ].reset_index(drop=True)

            if model_worker_df.empty:
                st.info(f"`{model_name_from_dir(model_dir)}` has no leftover rows for this worker.")
                continue

            worker_output_path = make_output_path(output_dir, model_dir, int(worker_count), int(worker_index))
            metadata = {
                "climatebert_model_dir": str(model_dir),
                "climatebert_model_name": model_name_from_dir(model_dir),
                "worker_count": int(worker_count),
                "worker_index": int(worker_index),
            }
            if auto_save:
                output_dir.mkdir(parents=True, exist_ok=True)

            with st.spinner(f"Running inference with `{model_dir.name}`..."):
                model_result = run_batches_with_checkpoints(
                    classifier=classifier,
                    input_df=model_worker_df,
                    batch_size=int(batch_size),
                    metadata=metadata,
                    save_path=worker_output_path if auto_save else None,
                )

            all_results.append(model_result)

            if auto_save:
                st.success(f"Checkpointed latest worker result to `{worker_output_path}`")

            if unload_after_model:
                del classifier
                unload_model_from_memory(model_dir, device)

        if all_results:
            result = pd.concat(all_results, ignore_index=True)
            st.session_state["climatebert_result"] = result
            read_saved_results.clear()
            st.success(f"Generated ClimateBERT predictions for {len(result):,} model-sentence rows")
    except Exception as exc:
        st.error(f"ClimateBERT inference failed:\n\n{exc}")


result = st.session_state.get("climatebert_result")
if isinstance(result, pd.DataFrame) and not result.empty:
    tab_table, tab_summary, tab_cross, tab_export = st.tabs([
        "Predictions",
        "Visual Summary",
        "Cross Tabs",
        "Export",
    ])

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
        left, right = st.columns(2)
        with left:
            st.subheader("Prediction Labels")
            st.bar_chart(result["label"].value_counts())
        with right:
            st.subheader("Confidence Distribution")
            scores = pd.to_numeric(result["score"], errors="coerce").dropna()
            if scores.empty:
                st.caption("No numeric confidence scores available.")
            else:
                st.bar_chart(confidence_bins(scores), x="confidence_range", y="count")

        score_cols = [col for col in result.columns if col.startswith("score_")]
        if score_cols:
            st.subheader("Average Class Scores")
            st.bar_chart(result[score_cols].mean().sort_values(ascending=False))

    with tab_cross:
        if "aspect_category" in result.columns:
            st.subheader("Labels by Aspect Category")
            pivot = pd.crosstab(result["aspect_category"], result["label"])
            st.dataframe(pivot, use_container_width=True)
            st.bar_chart(pivot)

        if "sentiment" in result.columns:
            st.subheader("Labels by Existing Sentiment")
            pivot = pd.crosstab(result["sentiment"], result["label"])
            st.dataframe(pivot, use_container_width=True)

        if "filename" in result.columns:
            st.subheader("Top Files by Climate Label")
            file_pivot = pd.crosstab(result["filename"], result["label"])
            file_pivot["total"] = file_pivot.sum(axis=1)
            file_pivot = file_pivot.sort_values("total", ascending=False).drop(columns=["total"]).head(25)
            st.dataframe(file_pivot, use_container_width=True)

    with tab_export:
        csv_bytes = result.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name="climatebert_predictions.csv",
            mime="text/csv",
            use_container_width=True,
        )

        default_export_path = (
            preview_output_paths[0]
            if preview_output_paths
            else output_dir / "climatebert_predictions.csv"
        )
        output_path = st.text_input("Optional server output path", value=str(default_export_path))
        if st.button("Save CSV on Server", use_container_width=True):
            try:
                target = Path(output_path).expanduser()
                target.parent.mkdir(parents=True, exist_ok=True)
                result.to_csv(target, index=False)
                read_saved_results.clear()
                st.success(f"Saved predictions to `{target}`")
            except Exception as exc:
                st.error(f"Could not save CSV: {exc}")


st.divider()
st.subheader("Saved Result Visualizer")
saved = read_saved_results(str(output_dir))
if use_snapshot:
    saved = saved_before_run.copy()

if saved.empty:
    st.caption(f"No saved CSV files found in `{output_dir}` yet.")
else:
    st.caption(f"Loaded {len(saved):,} saved prediction rows from `{output_dir}`")
    saved_tabs = st.tabs(["Combined Summary", "Combined Table", "Files"])

    with saved_tabs[0]:
        cols = st.columns(4)
        cols[0].metric("Saved rows", f"{len(saved):,}")
        if "sentence" in saved.columns:
            cols[1].metric("Saved unique sentences", f"{saved['sentence'].nunique():,}")
        if "result_file" in saved.columns:
            cols[2].metric("Shard files", f"{saved['result_file'].nunique():,}")
        if "climatebert_model_dir" in saved.columns:
            cols[3].metric("Models", f"{saved['climatebert_model_dir'].nunique():,}")

        if "label" in saved.columns:
            left, right = st.columns(2)
            with left:
                st.subheader("Combined Labels")
                st.bar_chart(saved["label"].value_counts())
            with right:
                st.subheader("Rows by Worker")
                if {"worker_count", "worker_index"}.issubset(saved.columns):
                    st.bar_chart(saved["worker_index"].value_counts().sort_index())

        if {"aspect_category", "label"}.issubset(saved.columns):
            st.subheader("Combined Labels by Aspect Category")
            st.dataframe(pd.crosstab(saved["aspect_category"], saved["label"]), use_container_width=True)

    with saved_tabs[1]:
        st.dataframe(saved.head(5000), use_container_width=True, height=520)

    with saved_tabs[2]:
        if "result_file" in saved.columns:
            file_counts = saved["result_file"].value_counts().rename_axis("result_file").reset_index(name="rows")
            st.dataframe(file_counts, use_container_width=True)
        if saved_files:
            st.markdown("**Detected CSV files on disk**")
            st.dataframe(pd.DataFrame(saved_files), use_container_width=True, hide_index=True)
