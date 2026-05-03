from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Research Questions Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "results" / "revision_analysis"


def load(name):
    path = ARTIFACTS / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


silver = load("silver_tone_ground_truth.csv")
prompt = load("prompt_stability_summary.csv")
green = load("greenwashing_index_by_company.csv")
agreement = load("climatebert_proxy_agreement_summary.csv")
failures = load("failure_mode_counts.csv")
ontology = load("ontology_coverage.csv")
ocr = load("ocr_quality_samples.csv")

st.title("Research Questions Dashboard")
st.caption("A single thesis-facing page that answers each RQ with the current evidence, figures, and remaining validation work.")

if silver.empty:
    st.error("No revision analysis data found.")
    st.stop()

rq_tabs = st.tabs(["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6", "Evidence Matrix"])

with rq_tabs[0]:
    st.header("RQ1. How can sustainability reports be transformed into structured ESG evidence?")
    st.markdown(
        """
        The pipeline converted report-derived text into structured ESG records stored in `results/esg_records.json` and normalized into `silver_tone_ground_truth.csv`.
        The current evidence demonstrates document-to-record transformation, but formal OCR quality still requires CER/WER samples.
        """
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Structured records", f"{len(silver):,}")
    c2.metric("Company/source targets", f"{silver['company'].nunique():,}")
    c3.metric("OCR CER/WER samples", f"{len(ocr):,}" if not ocr.empty else "0")
    st.info("Use `1_2_OCR_Quality_Workbench.py` to add manually corrected reference snippets for CER/WER.")

with rq_tabs[1]:
    st.header("RQ2. How can ESG statements be categorized by aspect, ESG pillar, sentiment, and tone?")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Aspects", f"{silver['aspect'].nunique():,}")
    c2.metric("ESG pillars", f"{silver['esg'].nunique():,}")
    c3.metric("Tones", f"{silver['tone_pred'].nunique():,}")
    c4.metric("Sentiments", f"{silver['sentiment'].nunique():,}")
    tone_counts = silver["tone_pred"].value_counts().rename_axis("tone").reset_index(name="count")
    chart = alt.Chart(tone_counts).mark_bar().encode(
        x="count:Q",
        y=alt.Y("tone:N", sort="-x"),
        tooltip=["tone", "count"],
        color=alt.value("#2f6f73"),
    ).properties(title="Tone Distribution", height=320)
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(silver[["record_id", "company", "aspect", "esg", "tone_pred", "sentiment", "text"]], use_container_width=True, height=360)

with rq_tabs[2]:
    st.header("RQ3. How do tone extraction results compare with ClimateBERT-style labels?")
    if agreement.empty:
        st.warning("No agreement summary found.")
    else:
        row = agreement.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Proxy agreement", f"{row['percent_agreement']:.3f}")
        c2.metric("Cohen kappa", f"{row['cohen_kappa']:.3f}")
        c3.metric("N", f"{int(row['n']):,}")
        st.write("This is a proxy comparison using ClimateBERT-style labels already attached to extracted records. For final validation, run real ClimateBERT over all 332 texts using `1_4_ClimateBERT_Record_Batch.py`.")

with rq_tabs[3]:
    st.header("RQ4. Can disagreement and missing labels reveal weaknesses in the extraction pipeline?")
    missing = int((silver["tone_pred"] == "missing").sum())
    drift = int(silver["schema_drift"].sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Missing tone records", f"{missing:,}", f"{missing / len(silver):.1%}")
    c2.metric("Schema drift records", f"{drift:,}", f"{drift / len(silver):.1%}")
    c3.metric("Needs review", f"{int(silver['needs_human_review'].sum()):,}")
    if not failures.empty:
        chart = alt.Chart(failures).mark_bar().encode(
            x=alt.X("count:Q", title="Count"),
            y=alt.Y("mode:N", sort="-x", title=None),
            color="tone_pred:N",
            tooltip=["mode", "tone_pred", "count"],
        ).properties(title="Failure Modes", height=420)
        st.altair_chart(chart, use_container_width=True)
    st.write("Failure-mode analysis converts the 61 missing-tone cases into actionable categories such as missing tone, hedged language, passive voice, regulatory Indonesian terms, and table/numeric layout markers.")

with rq_tabs[4]:
    st.header("RQ5. What documentation and visualization tools make the research auditable?")
    st.markdown(
        """
        The current app now includes pages for tone/ClimateBERT visualization, revision analytics, ground-truth annotation, OCR quality, formal metrics, ClimateBERT batching, Sankey flows, ontology paths, and this RQ dashboard.
        """
    )
    pages = [
        "0_9_Tone_ClimateBERT_Visualization.py",
        "1_0_Revision_Analytics.py",
        "1_1_Ground_Truth_Workbench.py",
        "1_2_OCR_Quality_Workbench.py",
        "1_3_Ground_Truth_Metrics.py",
        "1_4_ClimateBERT_Record_Batch.py",
        "1_5_ESG_Flow_Sankey.py",
        "1_6_Ontology_Path_Viewer.py",
        "1_7_Research_Questions_Dashboard.py",
    ]
    st.dataframe(pd.DataFrame({"Streamlit page": pages}), use_container_width=True)

with rq_tabs[5]:
    st.header("RQ6. How do prompt strategy and model choice affect extraction stability?")
    st.markdown("Prompt stability is evaluated through JSON parse success, average record count, missing tone rate, schema drift rate, and field completion.")
    st.dataframe(prompt, use_container_width=True)
    if not prompt.empty:
        chart = alt.Chart(prompt).mark_bar().encode(
            x=alt.X("missing_tone_rate:Q", title="Missing tone rate"),
            y=alt.Y("prompt:N", sort="-x", title=None),
            color=alt.value("#a6503f"),
            tooltip=["prompt", "runs", "missing_tone_rate", "schema_drift_rate", "field_completion_rate"],
        ).properties(title="Prompt Missing Tone Rate", height=360)
        st.altair_chart(chart, use_container_width=True)

with rq_tabs[6]:
    st.header("Evidence Matrix")
    matrix = pd.DataFrame(
        [
            {"RQ": "RQ1", "Evidence": "332 structured records; OCR workbench for CER/WER", "Status": "Partly validated"},
            {"RQ": "RQ2", "Evidence": "Aspect, ESG, tone, sentiment fields for every extracted record", "Status": "Implemented"},
            {"RQ": "RQ3", "Evidence": "Proxy agreement 0.837 and kappa 0.645", "Status": "Proxy validated"},
            {"RQ": "RQ4", "Evidence": "61 missing tones, schema drift, failure-mode categories", "Status": "Implemented"},
            {"RQ": "RQ5", "Evidence": "Static artifacts plus 9 Streamlit pages", "Status": "Implemented"},
            {"RQ": "RQ6", "Evidence": "Prompt stability table across 7 templates", "Status": "Implemented"},
            {"RQ": "Contribution", "Evidence": "Greenwashing index by company/source", "Status": "Implemented"},
            {"RQ": "Contribution", "Evidence": "Ontology coverage and path viewer", "Status": "Implemented"},
        ]
    )
    st.dataframe(matrix, use_container_width=True)
    if not green.empty:
        st.subheader("Greenwashing Index Evidence")
        st.dataframe(green, use_container_width=True)
    if not ontology.empty:
        st.subheader("Ontology Coverage Evidence")
        st.dataframe(ontology, use_container_width=True)
