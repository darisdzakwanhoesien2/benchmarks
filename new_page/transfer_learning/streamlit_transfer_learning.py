from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def cm_to_df(cm: List[List[int]], labels: Dict[str, str] | Dict[int, str]) -> pd.DataFrame:
    # labels may be {id: label} as strings after json serialization
    id2label: Dict[int, str] = {}
    for k, v in labels.items():
        try:
            idx = int(k)
        except Exception:
            continue
        id2label[idx] = str(v)

    df = pd.DataFrame(cm)
    df.index = [id2label.get(i, str(i)) for i in range(df.shape[0])]
    df.columns = [id2label.get(i, str(i)) for i in range(df.shape[1])]
    return df


def section_metrics(title: str, block: Dict[str, Any]) -> None:
    st.subheader(title)
    st.write({"accuracy": block.get("accuracy"), "macro_f1": block.get("macro_f1"), "n_labels": len(block.get("labels", {}))})
    cm = block.get("confusion_matrix")
    labels = block.get("labels", {})
    if cm:
        st.dataframe(cm_to_df(cm, labels))


st.set_page_config(page_title="Transfer Learning — ESG ABSA", layout="wide")

st.title("Transfer Learning — ESG ABSA (Bahasa Indonesia)")
st.caption("Viewer untuk hasil training/evaluasi di `results/transfer_learning/`.")

root = Path(".").resolve()
default_metrics = root / "results" / "transfer_learning"

metrics_path_str = st.text_input(
    "Path ke `metrics.json`",
    value=str(default_metrics / "run_001" / "metrics" / "metrics.json"),
)

metrics_path = Path(metrics_path_str)
if not metrics_path.exists():
    st.warning("metrics.json tidak ditemukan. Jalankan data_builder.py → train.py → evaluate.py terlebih dahulu.")
    st.stop()

metrics = read_json(metrics_path)

st.write({"n_rows": metrics.get("n"), "metrics_file": str(metrics_path)})

cols = st.columns(3)
with cols[0]:
    section_metrics("Aspect", metrics.get("aspect", {}))
with cols[1]:
    section_metrics("Sentiment", metrics.get("sentiment", {}))
with cols[2]:
    if "tone" in metrics:
        section_metrics("Tone", metrics.get("tone", {}))
    else:
        st.subheader("Tone")
        st.info("Tone tidak dievaluasi (run ini `include_tone` = false).")

