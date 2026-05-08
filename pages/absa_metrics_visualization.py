import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _page_explanations import add_page_explanation, add_section_explanation
import json
import pandas as pd

st.title('ABSA Metrics Results Visualization')
add_page_explanation(__file__)

PAGE_DIR = Path(__file__).resolve().parent
BENCHMARK_ROOT = PAGE_DIR.parent
RESULTS_PATH = BENCHMARK_ROOT / "absa_metrics_results.json"
ABSA_INTEGRATION_PATH = BENCHMARK_ROOT / "data" / "absa_integration.csv"
LOCAL_ZERO_MODEL_DIR = Path("/home/ubuntu/apps/benchmarks/model_download/models/ClimateControversyBert")
LOCAL_ZERO_OUTPUT_PATH = BENCHMARK_ROOT / "data" / "absa_integration_local_climate_controversy.csv"
LOCAL_ZERO_METRICS_PATH = BENCHMARK_ROOT / "absa_metrics_results_local_climate_controversy.json"
MODEL_WEIGHT_NAMES = {"pytorch_model.bin", "model.safetensors"}


def config_has_model_type(model_dir: Path) -> bool:
    config_path = model_dir / "config.json"
    if not config_path.exists():
        return False
    try:
        with config_path.open("r") as f:
            config = json.load(f)
        return bool(config.get("model_type"))
    except Exception:
        return False


def has_model_weight(model_dir: Path) -> bool:
    return any((model_dir / name).exists() for name in MODEL_WEIGHT_NAMES)


def resolve_local_model_dir(root: Path) -> Path | None:
    if config_has_model_type(root) and has_model_weight(root):
        return root
    for config_path in sorted(root.rglob("config.json")) if root.exists() else []:
        candidate = config_path.parent
        if config_has_model_type(candidate) and has_model_weight(candidate):
            return candidate
    return None


def normalize_label(value) -> str:
    value = "" if pd.isna(value) else str(value).strip()
    if not value or value.lower() in {"nan", "none", "null"}:
        return "none"
    return value


def normalize_series(series: pd.Series) -> pd.Series:
    return series.map(normalize_label)


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
        "label": normalize_label(best.get("label")),
        "score": float(best.get("score") or 0.0),
        "raw_prediction": json.dumps(scored, ensure_ascii=False),
    }
    for item in scored:
        label = normalize_label(item.get("label")).lower().replace(" ", "_")
        if label:
            row[f"score_{label}"] = float(item.get("score") or 0.0)
    return row


@st.cache_resource(show_spinner=False)
def load_local_classifier(model_dir: str, device: int):
    from transformers import pipeline

    resolved = resolve_local_model_dir(Path(model_dir))
    if resolved is None:
        raise ValueError(
            "No loadable Hugging Face text-classification model was found under "
            f"`{model_dir}`. The selected directory or one of its subdirectories must "
            "contain a config.json with a `model_type` key plus pytorch_model.bin or model.safetensors."
        )

    return pipeline(
        task="text-classification",
        model=str(resolved),
        tokenizer=str(resolved),
        top_k=None,
        device=device,
        truncation=True,
    )


def run_local_batches(classifier, texts: list[str], batch_size: int) -> pd.DataFrame:
    rows = []
    progress = st.progress(0)
    status = st.empty()
    total = len(texts)
    for start in range(0, total, batch_size):
        batch = texts[start:start + batch_size]
        outputs = classifier(batch, batch_size=batch_size, truncation=True)
        if isinstance(outputs, dict):
            outputs = [outputs]
        rows.extend(flatten_prediction(output) for output in outputs)
        done = min(start + len(batch), total)
        progress.progress(done / total)
        status.caption(f"Processed {done:,} / {total:,} texts with local ClimateControversyBert")
    status.empty()
    progress.empty()
    return pd.DataFrame(rows)


def compute_local_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
    )

    y_true = normalize_series(y_true).reset_index(drop=True)
    y_pred = normalize_series(y_pred).reset_index(drop=True)
    labels = sorted(set(y_true) | set(y_pred))
    return {
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
            output_dict=True,
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "labels": labels,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "support": len(y_true),
    }


def load_results(path=RESULTS_PATH):
    with open(path, 'r') as f:
        return json.load(f)

def is_nonzero(metrics):
    # Check if any main metric is non-zero
    return (
        metrics['accuracy'] > 0 or
        metrics['precision'] > 0 or
        metrics['recall'] > 0 or
        metrics['f1'] > 0
    )

def flatten_report(report):
    # Flatten classification report for display
    rows = []
    for label, scores in report.items():
        if isinstance(scores, dict):
            row = {'label': label}
            row.update(scores)
            rows.append(row)
    return pd.DataFrame(rows)

results = load_results()

nonzero = {k: v for k, v in results.items() if is_nonzero(v)}
zero = {k: v for k, v in results.items() if not is_nonzero(v)}

st.header('Non-zero Results')
add_section_explanation('Non-zero Results')
if nonzero:
    for model, metrics in nonzero.items():
        st.subheader(model)
        st.write(f"Accuracy: {metrics['accuracy']:.4f}")
        st.write(f"Precision: {metrics['precision']:.4f}")
        st.write(f"Recall: {metrics['recall']:.4f}")
        st.write(f"F1: {metrics['f1']:.4f}")
        st.write('Confusion Matrix:')
        st.dataframe(pd.DataFrame(metrics['confusion_matrix']))
        st.write('Classification Report:')
        st.dataframe(flatten_report(metrics['classification_report']))
else:
    st.write('No non-zero results found.')

st.header('Zero Results')
add_section_explanation('Zero Results')
if zero:
    st.write(', '.join(zero.keys()))
    st.subheader("Local rerun for zero-result models")
    st.write(
        "Zero metrics often mean the saved prediction labels are missing, unmapped, or in a "
        "different label space. This rerun path adopts the local batch-processing pattern from "
        "`02_ClimateBERT_Dataset_Processor.py` and runs the local ClimateControversyBert model."
    )
    st.caption(f"Local model directory: `{LOCAL_ZERO_MODEL_DIR}`")
    st.caption(f"ABSA integration data: `{ABSA_INTEGRATION_PATH}`")

    if not LOCAL_ZERO_MODEL_DIR.exists():
        st.warning("The local ClimateControversyBert directory was not found on this machine.")
    elif not ABSA_INTEGRATION_PATH.exists():
        st.warning("`data/absa_integration.csv` was not found, so there is no dataset to rerun.")
    else:
        resolved_model_dir = resolve_local_model_dir(LOCAL_ZERO_MODEL_DIR)
        if resolved_model_dir is None:
            st.error(
                "The ClimateControversyBert folder exists, but no loadable Hugging Face model "
                "was found under it. Check that a subdirectory contains `config.json` with "
                "`model_type` plus `pytorch_model.bin` or `model.safetensors`."
            )
            st.stop()
        st.caption(f"Resolved loadable model directory: `{resolved_model_dir}`")

        integration_df = pd.read_csv(ABSA_INTEGRATION_PATH)
        default_text_col = "sentence_norm" if "sentence_norm" in integration_df.columns else integration_df.columns[0]
        default_gt_col = "majority_sentiment" if "majority_sentiment" in integration_df.columns else integration_df.columns[0]

        text_col = st.selectbox("Text column for local rerun", integration_df.columns.tolist(), index=integration_df.columns.get_loc(default_text_col))
        gt_col = st.selectbox("Ground-truth column for local metric check", integration_df.columns.tolist(), index=integration_df.columns.get_loc(default_gt_col))
        output_col = st.text_input("Output prediction column", value="local_climate_controversy_label")
        score_col = f"{output_col}_score"
        max_rows = st.number_input("Maximum rows to rerun", min_value=1, value=min(500, len(integration_df)), step=100)
        batch_size = st.number_input("Local batch size", min_value=1, value=16, step=8)
        device_label = st.radio("Device", ["CPU", "CUDA 0"], horizontal=True)
        device = 0 if device_label == "CUDA 0" else -1

        if st.button("Run local ClimateControversyBert for zero-results", type="primary"):
            rerun_df = integration_df.dropna(subset=[text_col]).head(int(max_rows)).reset_index(drop=True)
            texts = rerun_df[text_col].map(normalize_label).tolist()
            with st.spinner(f"Loading local model from `{resolved_model_dir}`..."):
                classifier = load_local_classifier(str(resolved_model_dir), device)
            with st.spinner("Running local inference..."):
                predictions = run_local_batches(classifier, texts, int(batch_size))

            rerun_df[output_col] = predictions["label"].values
            rerun_df[score_col] = predictions["score"].values
            for col in predictions.columns:
                if col.startswith("score_"):
                    rerun_df[f"{output_col}_{col}"] = predictions[col].values

            LOCAL_ZERO_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            rerun_df.to_csv(LOCAL_ZERO_OUTPUT_PATH, index=False)

            local_metrics = compute_local_metrics(rerun_df[gt_col], rerun_df[output_col])
            LOCAL_ZERO_METRICS_PATH.write_text(json.dumps({
                output_col: local_metrics,
            }, indent=2))

            st.success(f"Saved local predictions to `{LOCAL_ZERO_OUTPUT_PATH}`")
            st.success(f"Saved local metrics to `{LOCAL_ZERO_METRICS_PATH}`")
            metric_cols = st.columns(4)
            metric_cols[0].metric("Accuracy", f"{local_metrics['accuracy']:.4f}")
            metric_cols[1].metric("Precision", f"{local_metrics['precision']:.4f}")
            metric_cols[2].metric("Recall", f"{local_metrics['recall']:.4f}")
            metric_cols[3].metric("F1", f"{local_metrics['f1']:.4f}")

            st.dataframe(rerun_df[[text_col, gt_col, output_col, score_col]].head(500), use_container_width=True)
            st.subheader("Local Confusion Matrix")
            st.dataframe(pd.DataFrame(
                local_metrics["confusion_matrix"],
                index=local_metrics["labels"],
                columns=local_metrics["labels"],
            ))
            st.subheader("Local Classification Report")
            st.dataframe(flatten_report(local_metrics["classification_report"]))
else:
    st.write('No zero results found.')
