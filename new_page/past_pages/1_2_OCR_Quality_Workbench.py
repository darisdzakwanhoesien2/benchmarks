from pathlib import Path
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="OCR Quality Workbench", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "results" / "revision_analysis"
SAMPLES_PATH = ARTIFACTS / "ocr_quality_samples.csv"
SUMMARY_PATH = ARTIFACTS / "ocr_processing_summary.csv"


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(
                min(
                    prev[j] + 1,
                    curr[j - 1] + 1,
                    prev[j - 1] + (ca != cb),
                )
            )
        prev = curr
    return prev[-1]


def cer(reference, hypothesis):
    reference = reference or ""
    hypothesis = hypothesis or ""
    if not reference:
        return None
    return edit_distance(reference, hypothesis) / len(reference)


def wer(reference, hypothesis):
    ref_words = (reference or "").split()
    hyp_words = (hypothesis or "").split()
    if not ref_words:
        return None
    return edit_distance(ref_words, hyp_words) / len(ref_words)


def load_samples():
    if SAMPLES_PATH.exists():
        return pd.read_csv(SAMPLES_PATH).fillna("")
    return pd.DataFrame(
        columns=[
            "timestamp",
            "document",
            "page",
            "layout_type",
            "language",
            "reference_text",
            "ocr_text",
            "cer",
            "wer",
            "notes",
        ]
    )


st.title("OCR Quality Workbench")
st.caption("Measure Character Error Rate and Word Error Rate for sampled OCR text. This directly addresses the revision feedback about quantifying OCR fidelity.")

samples = load_samples()
summary = pd.read_csv(SUMMARY_PATH).fillna("") if SUMMARY_PATH.exists() else pd.DataFrame()

overview, add_sample, saved = st.tabs(["Overview", "Add CER/WER Sample", "Saved Samples"])

with overview:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Saved OCR samples", f"{len(samples):,}")
    with c2:
        avg_cer = pd.to_numeric(samples["cer"], errors="coerce").mean() if len(samples) else None
        st.metric("Average CER", "n/a" if pd.isna(avg_cer) else f"{avg_cer:.3f}")
    with c3:
        avg_wer = pd.to_numeric(samples["wer"], errors="coerce").mean() if len(samples) else None
        st.metric("Average WER", "n/a" if pd.isna(avg_wer) else f"{avg_wer:.3f}")

    st.subheader("OCR Processing Log Summary")
    st.dataframe(summary, use_container_width=True)

    if len(samples):
        chart_data = samples.copy()
        chart_data["cer"] = pd.to_numeric(chart_data["cer"], errors="coerce")
        chart_data["wer"] = pd.to_numeric(chart_data["wer"], errors="coerce")
        melted = chart_data.melt(id_vars=["document", "page", "layout_type", "language"], value_vars=["cer", "wer"], var_name="metric", value_name="value")
        chart = (
            alt.Chart(melted)
            .mark_bar()
            .encode(
                x=alt.X("document:N", title=None),
                y=alt.Y("value:Q", title="Error rate"),
                color="metric:N",
                column=alt.Column("layout_type:N", title="Layout type"),
                tooltip=["document", "page", "layout_type", "language", "metric", alt.Tooltip("value:Q", format=".3f")],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)

with add_sample:
    st.subheader("Add Reference/OCR Pair")
    st.write("Paste the manually corrected reference text and the OCR markdown/text for the same page or paragraph.")

    with st.form("ocr_sample_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            document = st.text_input("Document/source", "")
        with c2:
            page = st.text_input("Page/batch", "")
        with c3:
            layout_type = st.selectbox("Layout type", ["narrative", "table", "bilingual_columns", "infographic", "mixed", "unknown"])

        language = st.selectbox("Language", ["id", "en", "mixed", "unknown"])
        reference_text = st.text_area("Reference text", height=220)
        ocr_text = st.text_area("OCR text", height=220)
        notes = st.text_area("Notes", height=100)
        submitted = st.form_submit_button("Compute and save", type="primary")

    if submitted:
        cer_val = cer(reference_text, ocr_text)
        wer_val = wer(reference_text, ocr_text)
        row = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "document": document,
            "page": page,
            "layout_type": layout_type,
            "language": language,
            "reference_text": reference_text,
            "ocr_text": ocr_text,
            "cer": "" if cer_val is None else cer_val,
            "wer": "" if wer_val is None else wer_val,
            "notes": notes,
        }
        updated = pd.concat([samples, pd.DataFrame([row])], ignore_index=True)
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        updated.to_csv(SAMPLES_PATH, index=False)
        st.success(f"Saved OCR sample. CER={cer_val:.3f} WER={wer_val:.3f}" if cer_val is not None and wer_val is not None else "Saved OCR sample.")

with saved:
    st.subheader("Saved CER/WER Samples")
    st.dataframe(samples, use_container_width=True, height=560)
    st.download_button(
        "Download OCR quality samples",
        samples.to_csv(index=False).encode("utf-8"),
        file_name="ocr_quality_samples.csv",
        mime="text/csv",
    )
