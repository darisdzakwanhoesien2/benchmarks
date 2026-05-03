from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Revision Analytics", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "results" / "revision_analysis"


@st.cache_data(show_spinner=False)
def load_csv(name):
    path = ARTIFACTS / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def metric(label, value, help_text=None):
    st.metric(label, value, help=help_text)


def bar(df, x, y, title, color="#2f6f73", height=360, sort="-x"):
    if df.empty:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=2, cornerRadiusBottomRight=2)
        .encode(
            x=alt.X(f"{x}:Q", title=None),
            y=alt.Y(f"{y}:N", sort=sort, title=None),
            color=alt.value(color),
            tooltip=[y, alt.Tooltip(f"{x}:Q", format=".3f")],
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def grouped_bar(df, x, y, color, title, height=420):
    if df.empty:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{x}:N", title=None),
            y=alt.Y(f"{y}:Q", title=None),
            color=alt.Color(f"{color}:N", title=color.replace("_", " ").title()),
            tooltip=[x, color, alt.Tooltip(f"{y}:Q", format=".3f")],
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def heatmap(df, x, y, value, title, height=420):
    if df.empty:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(f"{x}:N", title=None),
            y=alt.Y(f"{y}:N", title=None),
            color=alt.Color(f"{value}:Q", scale=alt.Scale(scheme="tealblues"), title=value.replace("_", " ").title()),
            tooltip=[x, y, alt.Tooltip(f"{value}:Q")],
        )
        .properties(title=title, height=height)
    )
    text = (
        alt.Chart(df)
        .mark_text(fontSize=12)
        .encode(
            x=alt.X(f"{x}:N"),
            y=alt.Y(f"{y}:N"),
            text=alt.Text(f"{value}:Q"),
            color=alt.condition(
                alt.datum[value] > df[value].max() * 0.55,
                alt.value("white"),
                alt.value("#17202a"),
            ),
        )
    )
    st.altair_chart(chart + text, use_container_width=True)


st.title("Revision Analytics Dashboard")
st.caption("Quantitative checks requested by the revision feedback: stability, agreement, greenwashing index, failure modes, language features, ontology coverage, and OCR scaffolding.")

silver = load_csv("silver_tone_ground_truth.csv")
prompt_summary = load_csv("prompt_stability_summary.csv")
run_stability = load_csv("prompt_stability_by_run.csv")
model_summary = load_csv("model_stability_summary.csv")
greenwashing = load_csv("greenwashing_index_by_company.csv")
agreement_summary = load_csv("climatebert_proxy_agreement_summary.csv")
agreement_records = load_csv("climatebert_proxy_agreement_records.csv")
failure_modes = load_csv("failure_modes.csv")
failure_counts = load_csv("failure_mode_counts.csv")
trigger_counts = load_csv("lexical_trigger_counts.csv")
triggers = load_csv("lexical_triggers.csv")
ontology = load_csv("ontology_coverage.csv")
ocr = load_csv("ocr_processing_summary.csv")

if silver.empty:
    st.error(f"No revision artifacts found in {ARTIFACTS}. Run the revision analysis generator first.")
    st.stop()

with st.sidebar:
    st.header("Filters")
    companies = sorted(silver["company"].dropna().unique().tolist())
    selected_companies = st.multiselect("Company/source", companies, default=companies)
    tones = sorted(silver["tone_pred"].dropna().unique().tolist())
    selected_tones = st.multiselect("Predicted tone", tones, default=tones)
    languages = sorted(silver["language"].dropna().unique().tolist())
    selected_languages = st.multiselect("Language", languages, default=languages)

view = silver[
    silver["company"].isin(selected_companies)
    & silver["tone_pred"].isin(selected_tones)
    & silver["language"].isin(selected_languages)
].copy()

tabs = st.tabs(
    [
        "Overview",
        "Prompt Stability",
        "Agreement",
        "Greenwashing Index",
        "Failure Modes",
        "Language Triggers",
        "Ontology and OCR",
        "Artifacts",
    ]
)

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("Records", f"{len(view):,}")
    with c2:
        metric("Needs review", f"{int(view['needs_human_review'].sum()):,}")
    with c3:
        metric("Missing tone", f"{int((view['tone_pred'] == 'missing').sum()):,}")
    with c4:
        drift = int(view["schema_drift"].sum())
        metric("Schema drift", f"{drift:,}", "Sentiment field contains values outside positive/negative/neutral/none.")

    left, right = st.columns(2)
    with left:
        tone_counts = view["tone_pred"].value_counts().rename_axis("tone").reset_index(name="count")
        bar(tone_counts, "count", "tone", "Tone Distribution")
    with right:
        lang_counts = view["language"].value_counts().rename_axis("language").reset_index(name="count")
        bar(lang_counts, "count", "language", "Language Distribution", color="#6b8f3a")

    st.subheader("Review Candidates")
    review_cols = ["record_id", "company", "prompt", "model", "language", "tone_pred", "sentiment", "suggested_tone", "suggestion_source", "text"]
    st.dataframe(view[view["needs_human_review"]][review_cols], use_container_width=True, height=420)

with tabs[1]:
    st.subheader("Prompt Stability")
    st.write("This table answers the feedback asking for JSON parse rate, field completion, missing tone rate, and schema drift per template.")
    st.dataframe(prompt_summary, use_container_width=True)

    left, right = st.columns(2)
    with left:
        bar(prompt_summary.sort_values("missing_tone_rate", ascending=False), "missing_tone_rate", "prompt", "Missing Tone Rate by Prompt", color="#a6503f", height=420)
    with right:
        bar(prompt_summary.sort_values("schema_drift_rate", ascending=False), "schema_drift_rate", "prompt", "Schema Drift Rate by Prompt", color="#7a5ea8", height=420)

    st.subheader("Model Stability")
    st.dataframe(model_summary, use_container_width=True)

    with st.expander("Run-level stability table"):
        st.dataframe(run_stability, use_container_width=True, height=420)

with tabs[2]:
    st.subheader("ClimateBERT Proxy Agreement")
    st.write("This uses the ClimateBERT-style labels already attached to `esg_records.json`: `tone_pred == commitment` is compared with the presence of `climate-commitment` in the labels. It is a proxy, not a substitute for human ground truth.")
    if not agreement_summary.empty:
        row = agreement_summary.iloc[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            metric("Percent agreement", f"{row['percent_agreement']:.3f}")
        with c2:
            metric("Cohen kappa", f"{row['cohen_kappa']:.3f}")
        with c3:
            metric("N", f"{int(row['n']):,}")

    if not agreement_records.empty:
        conf = (
            agreement_records.assign(tone_commitment=agreement_records["tone_pred"].eq("commitment"))
            .groupby(["tone_commitment", "has_climate_commitment"])
            .size()
            .reset_index(name="count")
        )
        heatmap(conf, "has_climate_commitment", "tone_commitment", "count", "Commitment Tone vs Climate-Commitment Label", height=260)
        st.subheader("Discordant Cases")
        discord = agreement_records[agreement_records["agreement_commitment"] == False]
        st.dataframe(discord, use_container_width=True, height=420)

with tabs[3]:
    st.subheader("Company-Level Greenwashing Index")
    st.write("The index is `(commitment + 0.5) / (outcome + 0.5)`. A high value is a screening signal for rhetoric-to-results imbalance, not a final greenwashing verdict.")
    min_records = st.slider("Minimum records per company/source", 1, 30, 3)
    gw_view = greenwashing[greenwashing["records"] >= min_records].sort_values("greenwashing_index", ascending=False)
    bar(gw_view.head(25), "greenwashing_index", "company", "Greenwashing Index by Company/Source", color="#b75d42", height=620)
    st.dataframe(gw_view, use_container_width=True)

with tabs[4]:
    st.subheader("Failure Mode Analysis")
    st.write("This diagnoses the 61 missing-tone records and schema-drift records by language, length, layout markers, hedging, passive voice, and regulatory Indonesian terms.")
    if not failure_counts.empty:
        heatmap(failure_counts, "tone_pred", "mode", "count", "Failure Mode by Predicted Tone", height=520)
    st.dataframe(failure_modes, use_container_width=True, height=520)

with tabs[5]:
    st.subheader("Lexical Trigger Analysis")
    st.write("This quantifies tone-related lexical markers such as modal/commitment terms, action terms, outcome terms, passive voice, and Indonesian regulatory markers.")
    if not trigger_counts.empty:
        grouped_bar(trigger_counts, "trigger_category", "count", "tone_pred", "Trigger Category by Tone", height=460)
    st.dataframe(triggers, use_container_width=True, height=520)

with tabs[6]:
    st.subheader("Ontology Coverage")
    if not ontology.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            metric("Observed aspects", f"{len(ontology):,}")
        with c2:
            metric("Mapped aspects", f"{int(ontology['mapped_to_ontology'].sum()):,}")
        with c3:
            metric("Coverage", f"{ontology['mapped_to_ontology'].mean():.1%}")
        st.dataframe(ontology, use_container_width=True)
        bar(ontology.sort_values("records", ascending=False).head(20), "records", "aspect", "Observed Aspect Coverage", height=520)

    st.subheader("OCR Quality Scaffolding")
    st.write("The current project logs document-level OCR processing. CER/WER requires human reference text; use the Ground Truth Workbench to add page-level reference snippets for formal OCR quality measurement.")
    st.dataframe(ocr, use_container_width=True)

with tabs[7]:
    st.subheader("Generated Artifacts")
    files = sorted(ARTIFACTS.glob("*"))
    st.dataframe(pd.DataFrame({"artifact": [str(p.relative_to(ROOT)) for p in files]}), use_container_width=True)
    st.download_button(
        "Download filtered revision records CSV",
        view.to_csv(index=False).encode("utf-8"),
        file_name="revision_filtered_records.csv",
        mime="text/csv",
    )
