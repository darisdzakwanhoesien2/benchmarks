from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


st.set_page_config(page_title="Ground Truth Metrics", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
ARTIFACTS = ROOT / "results" / "revision_analysis"
ANNOTATION_PATH = ARTIFACTS / "pilot_ground_truth_annotations.csv"
SEED_PATH = ARTIFACTS / "pilot_ground_truth_seed.csv"
SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"

from graph_attachment_gallery import render_attachment_cards  # noqa: E402


def load_annotations():
    path = ANNOTATION_PATH if ANNOTATION_PATH.exists() else SEED_PATH
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


def cohen_kappa(y_true, y_pred):
    pairs = [(str(a), str(b)) for a, b in zip(y_true, y_pred) if str(a).strip() and str(b).strip()]
    if not pairs:
        return None
    labels = sorted(set([a for a, _ in pairs] + [b for _, b in pairs]))
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    pe = 0.0
    for label in labels:
        pe += (sum(1 for a, _ in pairs if a == label) / n) * (sum(1 for _, b in pairs if b == label) / n)
    return (po - pe) / (1 - pe) if (1 - pe) else 0.0


def normalize_tone_label(value):
    text = str(value or "").strip().lower()
    if text in {"", "missing", "none", "nan", "null", "unknown", "no tone", "not_applicable", "n/a"}:
        return "none"
    return text


def metric_table(df, truth_col, pred_col, label):
    missing = [col for col in [truth_col, pred_col] if col not in df.columns]
    if missing:
        return pd.DataFrame(
            [
                {
                    "target": label,
                    "n": 0,
                    "status": f"Skipped: missing column(s) {', '.join(missing)}",
                }
            ]
        ), pd.DataFrame()
    valid = df[df[truth_col].astype(str).str.strip().ne("") & df[pred_col].astype(str).str.strip().ne("")].copy()
    if valid.empty:
        return pd.DataFrame(), valid
    if "tone" in label.lower():
        y_true = valid[truth_col].map(normalize_tone_label)
        y_pred = valid[pred_col].map(normalize_tone_label)
    else:
        y_true = valid[truth_col].astype(str)
        y_pred = valid[pred_col].astype(str)
    out = pd.DataFrame(
        [
            {
                "target": label,
                "n": len(valid),
                "accuracy": accuracy_score(y_true, y_pred),
                "precision_weighted": precision_score(y_true, y_pred, average="weighted", zero_division=0),
                "recall_weighted": recall_score(y_true, y_pred, average="weighted", zero_division=0),
                "f1_weighted": f1_score(y_true, y_pred, average="weighted", zero_division=0),
                "cohen_kappa": cohen_kappa(y_true, y_pred),
            }
        ]
    )
    return out, valid


def show_confusion(df, truth_col, pred_col, title):
    if df.empty:
        st.info("No labeled rows available for this confusion matrix.")
        return
    if "tone" in title.lower():
        actual = df[truth_col].map(normalize_tone_label)
        predicted = df[pred_col].map(normalize_tone_label)
    else:
        actual = df[truth_col].astype(str)
        predicted = df[pred_col].astype(str)
    labels = sorted(set(actual) | set(predicted))
    cm = confusion_matrix(actual, predicted, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels).reset_index().melt(id_vars="index", var_name="predicted", value_name="count")
    cm_df = cm_df.rename(columns={"index": "actual"})
    chart = (
        alt.Chart(cm_df)
        .mark_rect()
        .encode(
            x=alt.X("predicted:N", title="Predicted"),
            y=alt.Y("actual:N", title="Ground truth"),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=["actual", "predicted", "count"],
        )
        .properties(title=title, height=360)
    )
    text = alt.Chart(cm_df).mark_text().encode(
        x="predicted:N",
        y="actual:N",
        text="count:Q",
        color=alt.condition(alt.datum.count > cm_df["count"].max() * 0.55, alt.value("white"), alt.value("#17202a")),
    )
    st.altair_chart(chart + text, use_container_width=True)


st.title("Ground Truth Metrics")
st.caption("Formal evaluation once pilot human labels are filled. This page turns the annotation workbench into accuracy, F1, kappa, confusion matrices, and error tables.")

df = load_annotations()
if df.empty:
    st.error("No annotation seed or saved annotation file was found.")
    st.stop()

tabs = st.tabs(["Overview", "Tone Metrics", "ESG Metrics", "Aspect Metrics", "Errors", "Exports", "Attachment Cards"])

with tabs[0]:
    labeled_tone = df["ground_truth_tone"].astype(str).str.strip().ne("").sum()
    labeled_esg = df["ground_truth_esg"].astype(str).str.strip().ne("").sum() if "ground_truth_esg" in df else 0
    labeled_aspect = df["ground_truth_aspect"].astype(str).str.strip().ne("").sum() if "ground_truth_aspect" in df else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pilot rows", f"{len(df):,}")
    c2.metric("Tone labels", f"{labeled_tone:,}")
    c3.metric("ESG labels", f"{labeled_esg:,}")
    c4.metric("Aspect labels", f"{labeled_aspect:,}")

    st.info("If the label counts are zero, open `1_1_Ground_Truth_Workbench.py`, fill the ground-truth columns, and save annotations.")
    st.dataframe(df.head(100), use_container_width=True)

tone_metrics, tone_valid = metric_table(df, "ground_truth_tone", "tone_pred", "tone")
esg_metrics, esg_valid = metric_table(df, "ground_truth_esg", "esg", "esg")
aspect_metrics, aspect_valid = metric_table(df, "ground_truth_aspect", "aspect", "aspect")

with tabs[1]:
    st.subheader("Tone Classification Metrics")
    st.dataframe(tone_metrics, use_container_width=True)
    show_confusion(tone_valid, "ground_truth_tone", "tone_pred", "Tone Confusion Matrix")

with tabs[2]:
    st.subheader("ESG Pillar Metrics")
    st.dataframe(esg_metrics, use_container_width=True)
    show_confusion(esg_valid, "ground_truth_esg", "esg", "ESG Pillar Confusion Matrix")

with tabs[3]:
    st.subheader("Aspect Metrics")
    st.dataframe(aspect_metrics, use_container_width=True)
    show_confusion(aspect_valid, "ground_truth_aspect", "aspect", "Aspect Confusion Matrix")

with tabs[4]:
    st.subheader("Disagreement Tables")
    if not tone_valid.empty:
        st.markdown("**Tone disagreements**")
        st.dataframe(tone_valid[tone_valid["ground_truth_tone"].astype(str) != tone_valid["tone_pred"].astype(str)], use_container_width=True, height=320)
    if not esg_valid.empty:
        st.markdown("**ESG disagreements**")
        st.dataframe(esg_valid[esg_valid["ground_truth_esg"].astype(str) != esg_valid["esg"].astype(str)], use_container_width=True, height=320)
    if not aspect_valid.empty:
        st.markdown("**Aspect disagreements**")
        st.dataframe(aspect_valid[aspect_valid["ground_truth_aspect"].astype(str) != aspect_valid["aspect"].astype(str)], use_container_width=True, height=320)

with tabs[5]:
    metrics_all = pd.concat([tone_metrics, esg_metrics, aspect_metrics], ignore_index=True)
    st.download_button("Download metrics CSV", metrics_all.to_csv(index=False).encode("utf-8"), "ground_truth_metrics.csv", "text/csv")
    st.download_button("Download annotation table CSV", df.to_csv(index=False).encode("utf-8"), "pilot_ground_truth_annotations.csv", "text/csv")
    if SILVER_PATH.exists():
        silver = pd.read_csv(SILVER_PATH)
        st.download_button("Download full silver scaffold CSV", silver.to_csv(index=False).encode("utf-8"), "silver_tone_ground_truth.csv", "text/csv")

with tabs[6]:
    render_attachment_cards(
        "Ground Truth Metrics Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        rq_default="RQ2",
        figures=["A.13", "A.17", "A.18", "A.19", "A.20"],
    )
