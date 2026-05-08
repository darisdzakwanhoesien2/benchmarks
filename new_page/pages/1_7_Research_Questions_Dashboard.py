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


def pct(value):
    return f"{value:.1%}"


silver = load("silver_tone_ground_truth.csv")
prompt = load("prompt_stability_summary.csv")
green = load("greenwashing_index_by_company.csv")
agreement = load("climatebert_proxy_agreement_summary.csv")
failures = load("failure_mode_counts.csv")
ontology = load("ontology_coverage.csv")
ocr = load("ocr_quality_samples.csv")

st.title("Research Questions Dashboard")
st.caption(
    "Thesis-facing evidence, benchmarks, sample-size reasoning, and next analyses for the bilingual ESG ABSA study."
)

if silver.empty:
    st.error("No revision analysis data found.")
    st.stop()

valid_arcee = silver[
    (silver["model"].astype(str).str.contains("arcee", case=False, na=False))
    & (silver["tone_pred"].astype(str) != "missing")
]

sample_size_ladder = pd.DataFrame(
    [
        {
            "n": "272",
            "claim level": "Pipeline feasibility prototype",
            "what it supports": "Extraction pipeline demonstration, descriptive tone distributions, and the bilingual outcome-rate asymmetry.",
            "limitation": "No defensible F1, full subgroup matrix, or generalizable greenwashing conclusion.",
            "status": "current",
        },
        {
            "n": "384",
            "claim level": "Standard academic MoE threshold",
            "what it supports": "Worst-case 95% margin of error reaches +/-5.0 percentage points.",
            "limitation": "Still thin for prompt and pillar subgroup comparisons.",
            "status": "minimum",
        },
        {
            "n": "500",
            "claim level": "Balanced prompt comparison",
            "what it supports": "About 100 records per five prompt templates and >=80% power for medium prompt effects.",
            "limitation": "Full pillar x language x tone matrix remains incomplete.",
            "status": "minimum for RQ6",
        },
        {
            "n": "720",
            "claim level": "Full bilingual subgroup analysis",
            "what it supports": "3 pillars x 2 languages x 4 tones x 30 records per cell.",
            "limitation": "Still best framed as a thesis-scale descriptive study.",
            "status": "recommended target",
        },
        {
            "n": "1,000",
            "claim level": "Literature-comparable extraction study",
            "what it supports": "Lower-end comparability with exploratory ESG NLP literature and +/-3.1pp MoE.",
            "limitation": "Needs at least 15 source documents for stable document-level GW claims.",
            "status": "strong target",
        },
        {
            "n": "1,500",
            "claim level": "Expert annotation enables F1 reporting",
            "what it supports": "1,000 extracted records plus about 500 expert-annotated examples for precision, recall, and F1.",
            "limitation": "Requires substantial human annotation effort.",
            "status": "evaluation target",
        },
        {
            "n": "2,000+",
            "claim level": "Fine-tuning a bilingual ABSA model",
            "what it supports": "Supervised mBERT/XLM-R-style model training and published-baseline comparisons.",
            "limitation": "Out of scope for a master's prototype.",
            "status": "out of scope",
        },
    ]
)

moe_rows = pd.DataFrame(
    [
        {"n": 272, "worst_case_moe_pp": 5.9, "outcome_class_moe_pp": 4.6},
        {"n": 384, "worst_case_moe_pp": 5.0, "outcome_class_moe_pp": None},
        {"n": 500, "worst_case_moe_pp": 4.4, "outcome_class_moe_pp": None},
        {"n": 600, "worst_case_moe_pp": 4.0, "outcome_class_moe_pp": 3.1},
        {"n": 720, "worst_case_moe_pp": 3.6, "outcome_class_moe_pp": None},
        {"n": 1000, "worst_case_moe_pp": 3.1, "outcome_class_moe_pp": 2.4},
        {"n": 1500, "worst_case_moe_pp": 2.5, "outcome_class_moe_pp": None},
    ]
)

power_rows = pd.DataFrame(
    [
        {"test": "ID 7.9% vs EN 21.8% outcome rate", "n_basis": "272 total / 136 per language", "power": 0.897, "verdict": "sufficient"},
        {"test": "Few-shot vs other prompt templates", "n_basis": "14 few-shot records", "power": 0.434, "verdict": "underpowered"},
        {"test": "Prompt comparison minimum", "n_basis": "40 records per template", "power": 0.858, "verdict": "minimum acceptable"},
        {"test": "Zero-shot Indonesian", "n_basis": "42 records", "power": 0.872, "verdict": "acceptable"},
        {"test": "Zero-shot English", "n_basis": "55 records", "power": 0.945, "verdict": "good"},
        {"test": "CoT English", "n_basis": "100 records", "power": 0.998, "verdict": "excellent"},
    ]
)

subgroup_rows = pd.DataFrame(
    [
        {"requirement": "Tone categories only", "formula": "5 tones x 30", "n_needed": 150, "status": "met at n=272"},
        {"requirement": "Language x tone", "formula": "2 languages x 4 tones x 30", "n_needed": 240, "status": "met at n=272"},
        {"requirement": "Document x tone, relaxed", "formula": "6 docs x 4 tones x 10", "n_needed": 240, "status": "met at n=272"},
        {"requirement": "ESG pillar x tone", "formula": "3 pillars x 4 tones x 30", "n_needed": 360, "status": "need 88 more"},
        {"requirement": "Prompt template x tone", "formula": "5 prompts x 4 tones x 20", "n_needed": 400, "status": "need 128 more"},
        {"requirement": "Pillar x language x tone", "formula": "3 x 2 x 4 x 30", "n_needed": 720, "status": "need 448 more"},
    ]
)

benchmark_rows = pd.DataFrame(
    [
        {
            "model / study": "FinBERT (Huang et al. 2023)",
            "task": "Financial sentiment classification",
            "benchmark": "F1 97.0%",
            "thesis relevance": "Upper-bound sentiment reference for financial text.",
        },
        {
            "model / study": "ESG-BERT (Mukherjee et al. 2022)",
            "task": "ESG category classification",
            "benchmark": "F1 about 88%",
            "thesis relevance": "Direct reference for ESG pillar classification once expert labels exist.",
        },
        {
            "model / study": "SemEval ABSA best systems",
            "task": "Aspect extraction + sentiment",
            "benchmark": "F1 75-82%",
            "thesis relevance": "General-domain ABSA baseline; ESG regulatory language is harder.",
        },
        {
            "model / study": "ClimateBERT climate-detector",
            "task": "Climate relevance detection",
            "benchmark": "F1 0.87",
            "thesis relevance": "External validator for climate-related ESG records.",
        },
        {
            "model / study": "ClimateBERT climate-commitment",
            "task": "Commitment statement detection",
            "benchmark": "F1 0.81",
            "thesis relevance": "Closest validator for the commitment tone class.",
        },
        {
            "model / study": "XLM-R / mBERT cross-lingual ABSA",
            "task": "Multilingual target-language transfer",
            "benchmark": "F1 0.55-0.80",
            "thesis relevance": "Context for Indonesian/English extraction asymmetry.",
        },
        {
            "model / study": "Gorovaia & Makrominas 2024",
            "task": "Greenwashing detection in CSR",
            "benchmark": "Accuracy 0.71 / precision 0.68",
            "thesis relevance": "Comparable commitment-vs-outcome greenwashing framing.",
        },
    ]
)

analysis_plan = pd.DataFrame(
    [
        {
            "priority": "P1",
            "analysis": "Run ClimateBERT locally over all valid Arcee records",
            "answers": "RQ3, RQ4",
            "effort": "1-2 days",
            "impact": "critical",
            "expected output": "Record x ClimateBERT-model score matrix and true tone-vs-ClimateBERT agreement.",
        },
        {
            "priority": "P2",
            "analysis": "Expert annotation of 30-50 stratified records",
            "answers": "RQ2, RQ4",
            "effort": "2-3 weeks",
            "impact": "critical",
            "expected output": "Cohen's kappa and per-class precision, recall, F1 for tone/aspect/pillar.",
        },
        {
            "priority": "P3",
            "analysis": "Prompt stability ensemble on PTBA",
            "answers": "RQ6",
            "effort": "1 day",
            "impact": "high",
            "expected output": "Majority-vote prompt ensemble and variance reduction estimate.",
        },
        {
            "priority": "P4",
            "analysis": "Formal bilingual asymmetry test",
            "answers": "RQ2",
            "effort": "2 hours",
            "impact": "high",
            "expected output": "Two-proportion z-test or Fisher exact test for ID vs EN outcome rate.",
        },
        {
            "priority": "P5",
            "analysis": "GW index by document x prompt",
            "answers": "RQ3, RQ5",
            "effort": "1 day",
            "impact": "medium",
            "expected output": "Per-prompt greenwashing stability and domestic/international comparison.",
        },
        {
            "priority": "P6",
            "analysis": "Re-run social-pillar pages and balance GPT-oss",
            "answers": "RQ2, RQ6",
            "effort": "2-3 days",
            "impact": "medium",
            "expected output": "At least 30 S-pillar records and matched cross-model runs for kappa.",
        },
        {
            "priority": "P7",
            "analysis": "OCR quality measurement on a reference document",
            "answers": "RQ1",
            "effort": "1-2 days",
            "impact": "important",
            "expected output": "CER/WER and table extraction accuracy for sampled pages.",
        },
    ]
)

tabs = st.tabs(
    [
        "Overview",
        "Per-RQ Evidence",
        "Sample Size",
        "Benchmarks",
        "Existing Results",
        "Analysis Plan",
        "Evidence Matrix",
    ]
)

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Structured records", f"{len(silver):,}")
    c2.metric("Valid Arcee records", f"{len(valid_arcee):,}")
    c3.metric("Documents / companies", f"{silver['company'].nunique():,}")
    c4.metric("Prompt templates", f"{silver['prompt'].nunique():,}")

    st.subheader("Main thesis read")
    st.markdown(
        """
        The current dataset is credible as a feasibility study and already supports several descriptive findings:
        structured PDF-to-record transformation, tone distributions, prompt instability, diagnostics, and the
        Indonesian/English outcome-rate asymmetry. The statistical ceiling is narrower: n=272 does not support
        full subgroup claims, few-shot prompt comparison, F1 reporting, or generalizable document-level greenwashing claims.
        """
    )

    highlights = pd.DataFrame(
        [
            {"finding": "Bilingual outcome asymmetry", "evidence": "ID outcome 7.9% vs EN outcome 21.8%", "claim strength": "powered at n=272"},
            {"finding": "Prompt instability", "evidence": "CoT commitment about 55% vs zero-shot about 22-24%", "claim strength": "strong, but few-shot is thin"},
            {"finding": "S-pillar gap", "evidence": "Only 4 S-pillar records", "claim strength": "cannot analyze Social yet"},
            {"finding": "Greenwashing index", "evidence": "5 working documents, domestic vs international gap +0.500", "claim strength": "case-study signal only"},
            {"finding": "Cross-model comparison", "evidence": "No matched Arcee/GPT-oss inputs", "claim strength": "not computable yet"},
        ]
    )
    st.dataframe(highlights, use_container_width=True, hide_index=True)

with tabs[1]:
    rq_tabs = st.tabs(["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"])

    with rq_tabs[0]:
        st.header("RQ1. PDF-to-structured ESG transformation")
        c1, c2, c3 = st.columns(3)
        c1.metric("Structured records", f"{len(silver):,}")
        c2.metric("Company/source targets", f"{silver['company'].nunique():,}")
        c3.metric("OCR CER/WER samples", f"{len(ocr):,}" if not ocr.empty else "0")
        st.info("Evidence exists for document-to-record transformation. Formal OCR quality still needs manual reference snippets and CER/WER measurement.")

    with rq_tabs[1]:
        st.header("RQ2. Aspect, pillar, sentiment, and tone categorization")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aspects", f"{silver['aspect'].nunique():,}")
        c2.metric("ESG pillars", f"{silver['esg'].nunique():,}")
        c3.metric("Tones", f"{silver['tone_pred'].nunique():,}")
        c4.metric("Languages", f"{silver['language'].nunique():,}")
        tone_counts = silver["tone_pred"].value_counts().rename_axis("tone").reset_index(name="count")
        chart = alt.Chart(tone_counts).mark_bar().encode(
            x="count:Q",
            y=alt.Y("tone:N", sort="-x"),
            tooltip=["tone", "count"],
            color=alt.value("#a78bfa"),
        ).properties(title="Tone distribution", height=320)
        st.altair_chart(chart, use_container_width=True)
        st.warning("Expert labels are still required before reporting precision, recall, F1, or taxonomy validity.")

    with rq_tabs[2]:
        st.header("RQ3. Tone vs ClimateBERT-style labels")
        if agreement.empty:
            st.warning("No agreement summary found.")
        else:
            row = agreement.iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Proxy agreement", f"{row['percent_agreement']:.3f}")
            c2.metric("Cohen kappa", f"{row['cohen_kappa']:.3f}")
            c3.metric("N", f"{int(row['n']):,}")
        st.info("Current agreement is a proxy from LLM-assigned ClimateBERT-style labels. Final validation needs actual ClimateBERT runs over all valid texts.")

    with rq_tabs[3]:
        st.header("RQ4. Diagnostics and extraction weaknesses")
        missing = int((silver["tone_pred"] == "missing").sum())
        drift = int(pd.to_numeric(silver["schema_drift"], errors="coerce").fillna(0).sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("Missing tone records", f"{missing:,}", pct(missing / len(silver)))
        c2.metric("Schema drift records", f"{drift:,}", pct(drift / len(silver)))
        c3.metric("Needs human review", f"{int(pd.to_numeric(silver['needs_human_review'], errors='coerce').fillna(0).sum()):,}")
        if not failures.empty:
            chart = alt.Chart(failures).mark_bar().encode(
                x=alt.X("count:Q", title="Count"),
                y=alt.Y("mode:N", sort="-x", title=None),
                color="tone_pred:N",
                tooltip=["mode", "tone_pred", "count"],
            ).properties(title="Failure modes", height=420)
            st.altair_chart(chart, use_container_width=True)

    with rq_tabs[4]:
        st.header("RQ5. Reproducibility and auditability")
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
            "1_8_Ground_Truth_Output_Visualizer.py",
            "1_9_Ground_Truth_Pipeline_Output_Visualizer.py",
            "2_0_LLM_Processing_Result_Visualizer.py",
            "2_1_LLM_Error_Parse_Audit.py",
        ]
        st.dataframe(pd.DataFrame({"Streamlit page": pages}), use_container_width=True, hide_index=True)
        st.info("The next reproducibility gap is a formal checklist: model version, prompt exact text, decoding config, input hashes, and rerun similarity.")

    with rq_tabs[5]:
        st.header("RQ6. Prompt and model stability")
        st.dataframe(prompt, use_container_width=True, hide_index=True)
        if not prompt.empty:
            chart = alt.Chart(prompt).mark_bar().encode(
                x=alt.X("missing_tone_rate:Q", title="Missing tone rate"),
                y=alt.Y("prompt:N", sort="-x", title=None),
                color=alt.value("#fbbf24"),
                tooltip=["prompt", "runs", "missing_tone_rate", "schema_drift_rate", "field_completion_rate"],
            ).properties(title="Prompt missing-tone rate", height=360)
            st.altair_chart(chart, use_container_width=True)
        st.warning("Cross-model kappa is not computable until GPT-oss is rerun on matched documents and prompts.")

with tabs[2]:
    st.header("Sample-size reasoning")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current n", "272", "+112 to MoE minimum")
    c2.metric("MoE minimum", "384", "+128 to prompt minimum")
    c3.metric("Recommended n", "720", "full subgroup matrix")
    c4.metric("Strong target", "1,000", "15+ documents")

    st.subheader("Claim ladder")
    st.dataframe(sample_size_ladder, use_container_width=True, hide_index=True)

    st.subheader("Margin of error")
    moe_long = moe_rows.melt("n", var_name="metric", value_name="moe_pp").dropna()
    chart = alt.Chart(moe_long).mark_line(point=True).encode(
        x=alt.X("n:O", title="Sample size"),
        y=alt.Y("moe_pp:Q", title="MoE, percentage points"),
        color="metric:N",
        tooltip=["n", "metric", "moe_pp"],
    ).properties(height=320)
    threshold = alt.Chart(pd.DataFrame({"y": [5.0]})).mark_rule(color="#f87171", strokeDash=[6, 4]).encode(y="y:Q")
    st.altair_chart(chart + threshold, use_container_width=True)

    st.subheader("Power and subgroup needs")
    left, right = st.columns(2)
    with left:
        st.dataframe(power_rows, use_container_width=True, hide_index=True)
    with right:
        st.dataframe(subgroup_rows, use_container_width=True, hide_index=True)

    st.success(
        "Bottom line: n=272 is adequate for a feasibility frame. For a defensible thesis-scale descriptive study, target n=720-1,000, with targeted additions for few-shot prompts, S-pillar pages, and 15+ documents."
    )

with tabs[3]:
    st.header("Benchmark reference")
    st.dataframe(benchmark_rows, use_container_width=True, hide_index=True)
    st.markdown(
        """
        Benchmark implication: this thesis should not claim supervised ABSA model performance until expert labels exist.
        It can currently claim a structured extraction pipeline, descriptive bilingual ABSA findings, diagnostics, and a
        prototype greenwashing signal. F1/precision/recall belong after P2 expert annotation.
        """
    )

with tabs[4]:
    st.header("Existing results")
    cards = [
        ("RQ1 Pipeline", f"{len(silver):,}", "records extracted; JSON parseable"),
        ("RQ2 Categorization", "4-dim", "aspect + pillar + tone + sentiment"),
        ("RQ3 ClimateBERT proxy", "0.837", "proxy agreement from existing labels"),
        ("RQ4 Diagnostics", "61", "missing-tone cases identified"),
        ("RQ5 Artifacts", "13", "Streamlit pages in this workspace"),
        ("RQ6 Stability", "38.2%", "CV in commitment rate across prompts"),
    ]
    cols = st.columns(3)
    for idx, (label, value, help_text) in enumerate(cards):
        cols[idx % 3].metric(label, value, help_text)

    st.subheader("Greenwashing index by company")
    st.dataframe(green, use_container_width=True, hide_index=True)

    st.subheader("Language x tone distribution")
    lang_tone = (
        valid_arcee.groupby(["language", "tone_pred"])
        .size()
        .reset_index(name="count")
        .sort_values(["language", "count"], ascending=[True, False])
    )
    if not lang_tone.empty:
        chart = alt.Chart(lang_tone).mark_bar().encode(
            x=alt.X("count:Q", title="Records"),
            y=alt.Y("tone_pred:N", title=None),
            color="language:N",
            row="language:N",
            tooltip=["language", "tone_pred", "count"],
        ).properties(height=150)
        st.altair_chart(chart, use_container_width=True)
        st.dataframe(lang_tone, use_container_width=True, hide_index=True)

with tabs[5]:
    st.header("Prioritized analysis plan")
    st.dataframe(analysis_plan, use_container_width=True, hide_index=True)
    st.subheader("Actionable fixes from sample-size diagnosis")
    fixes = pd.DataFrame(
        [
            {"problem": "Few-shot template underpowered", "current": "n=14 / power=43%", "fix": "Run 2-3 more few-shot batches to add 25-40 records."},
            {"problem": "Greenwashing index document count", "current": "5 working docs", "fix": "Add 9-14 IDX sustainability reports for 15-20 document coverage."},
            {"problem": "S-pillar coverage", "current": "n=4", "fix": "Select social-topic PTBA and VKTR pages; target at least 30 S records."},
            {"problem": "Cross-model comparison confounded", "current": "0 shared inputs", "fix": "Run GPT-oss on matched PTBA/ICR documents and prompts."},
        ]
    )
    st.dataframe(fixes, use_container_width=True, hide_index=True)

with tabs[6]:
    st.header("Evidence matrix")
    matrix = pd.DataFrame(
        [
            {"RQ": "RQ1", "evidence": "332 structured records; OCR workbench exists", "status": "partly validated", "next evidence": "CER/WER sample"},
            {"RQ": "RQ2", "evidence": "Aspect, ESG, tone, sentiment fields for every extracted record", "status": "implemented", "next evidence": "Expert labels + IAA"},
            {"RQ": "RQ3", "evidence": "Proxy agreement 0.837 and kappa 0.645", "status": "proxy validated", "next evidence": "Actual ClimateBERT matrix"},
            {"RQ": "RQ4", "evidence": "Missing tones, schema drift, failure-mode categories", "status": "implemented", "next evidence": "Manual error labels"},
            {"RQ": "RQ5", "evidence": "Static artifacts plus Streamlit pages", "status": "implemented", "next evidence": "Reproducibility checklist"},
            {"RQ": "RQ6", "evidence": "Prompt stability table across templates", "status": "partly validated", "next evidence": "Matched cross-model kappa"},
            {"RQ": "Sample size", "evidence": "n=272 feasibility; target ladder to 720/1,000", "status": "diagnosed", "next evidence": "Targeted collection plan"},
            {"RQ": "Contribution", "evidence": "Greenwashing index by company/source", "status": "case-study signal", "next evidence": "15+ document stability"},
            {"RQ": "Contribution", "evidence": "Ontology coverage and path viewer", "status": "implemented", "next evidence": "Aspect normalization map"},
        ]
    )
    st.dataframe(matrix, use_container_width=True, hide_index=True)
    if not ontology.empty:
        st.subheader("Ontology coverage")
        st.dataframe(ontology, use_container_width=True, hide_index=True)
