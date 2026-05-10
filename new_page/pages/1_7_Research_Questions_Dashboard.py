from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


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


def render_mermaid(source: str, height: int = 620):
    components.html(
        f"""
        <div class="mermaid">
        {source}
        </div>
        <script type="module">
          import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
          mermaid.initialize({{
            startOnLoad: true,
            theme: "dark",
            flowchart: {{ curve: "basis", htmlLabels: true }}
          }});
        </script>
        """,
        height=height,
        scrolling=True,
    )


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

rq_page_map = pd.DataFrame(
    [
        {
            "RQ": "RQ1",
            "thesis need": "Show how PDF sustainability reports become traceable structured ESG evidence.",
            "primary pages": "Bulk_OCR.py; llm_processing.py; 1_9_Ground_Truth_Pipeline_Output_Visualizer.py",
            "supporting pages": "1_2_OCR_Quality_Workbench.py; 2_0_LLM_Processing_Result_Visualizer.py",
            "evidence to cite": "OCR markdown/pages, JSON records, provenance fields, parse success, source-document counts.",
            "remaining gap": "CER/WER and table/figure extraction accuracy still need manual reference samples.",
        },
        {
            "RQ": "RQ2",
            "thesis need": "Explain how ESG statements are categorized by aspect, pillar, tone, language, and sentiment.",
            "primary pages": "0_9_Tone_ClimateBERT_Visualization.py; 1_6_Ontology_Path_Viewer.py; 1_8_Ground_Truth_Output_Visualizer.py",
            "supporting pages": "1_1_Ground_Truth_Workbench.py; 1_3_Ground_Truth_Metrics.py; 1_7_Research_Questions_Dashboard.py",
            "evidence to cite": "Tone distribution, ESG-by-tone, aspect-by-tone heatmap, ontology coverage, language x tone split.",
            "remaining gap": "Expert labels and inter-annotator agreement are required before final F1 claims.",
        },
        {
            "RQ": "RQ3",
            "thesis need": "Compare ABSA tone outputs with ClimateBERT-style climate disclosure labels.",
            "primary pages": "1_4_ClimateBERT_Record_Batch.py; 0_9_Tone_ClimateBERT_Visualization.py",
            "supporting pages": "1_0_Revision_Analytics.py; 1_7_Research_Questions_Dashboard.py",
            "evidence to cite": "Proxy agreement, Cohen's kappa, ClimateBERT label-by-tone, remote score sanity checks.",
            "remaining gap": "Current comparison is proxy-based; run real ClimateBERT across all valid records for final validation.",
        },
        {
            "RQ": "RQ4",
            "thesis need": "Detect, quantify, and explain weaknesses in extraction outputs.",
            "primary pages": "2_1_LLM_Error_Parse_Audit.py; 1_0_Revision_Analytics.py; 1_8_Ground_Truth_Output_Visualizer.py",
            "supporting pages": "1_3_Ground_Truth_Metrics.py; 1_6_Ontology_Path_Viewer.py",
            "evidence to cite": "Missing-tone counts, schema drift, raw-output parse failures, failure modes, ontology gaps.",
            "remaining gap": "Manual error labels would turn diagnostics into measured error rates.",
        },
        {
            "RQ": "RQ5",
            "thesis need": "Demonstrate reproducibility, auditability, and documentation of the ESG ABSA workflow.",
            "primary pages": "1_7_Research_Questions_Dashboard.py; 1_7_Research_Questions_Dashboard_outputs.md; README.md",
            "supporting pages": "All Streamlit pages; results/visualizations; results/revision_analysis",
            "evidence to cite": "Page inventory, image catalog, generated artifacts, CSV/JSON outputs, documented workflow.",
            "remaining gap": "Add a formal reproducibility checklist with model versions, prompt hashes, and rerun settings.",
        },
        {
            "RQ": "RQ6",
            "thesis need": "Evaluate prompt/model stability and define ensemble or verification strategies.",
            "primary pages": "1_0_Revision_Analytics.py; 1_7_Research_Questions_Dashboard.py; 2_0_LLM_Processing_Result_Visualizer.py",
            "supporting pages": "2_1_LLM_Error_Parse_Audit.py; 1_4_ClimateBERT_Record_Batch.py",
            "evidence to cite": "Prompt stability summary, missing-tone rate, schema drift rate, CoT vs zero-shot differences.",
            "remaining gap": "Cross-model kappa needs matched Arcee/GPT-oss runs on the same documents and prompts.",
        },
    ]
)

chapter_plan = pd.DataFrame(
    [
        {
            "chapter": "Chapter 4 - Results",
            "section": "4.1 Pipeline output and corpus construction",
            "main pages": "Bulk_OCR.py; llm_processing.py; 1_9_Ground_Truth_Pipeline_Output_Visualizer.py",
            "figures/tables": "Record counts, document list, provenance, parse success, OCR sample status.",
            "message": "The system successfully turns report-derived text into structured ESG evidence records.",
        },
        {
            "chapter": "Chapter 4 - Results",
            "section": "4.2 ESG ABSA descriptive results",
            "main pages": "0_9_Tone_ClimateBERT_Visualization.py; 1_6_Ontology_Path_Viewer.py",
            "figures/tables": "Tone distribution, ESG-by-tone, aspect-by-tone heatmap, ontology coverage.",
            "message": "The extracted corpus supports descriptive tone, pillar, aspect, and language analysis.",
        },
        {
            "chapter": "Chapter 4 - Results",
            "section": "4.3 ClimateBERT proxy comparison",
            "main pages": "1_4_ClimateBERT_Record_Batch.py; 0_9_Tone_ClimateBERT_Visualization.py",
            "figures/tables": "Proxy agreement, kappa, ClimateBERT label-by-tone, remote top scores.",
            "message": "ClimateBERT-style labels partially align with tone extraction but remain proxy evidence.",
        },
        {
            "chapter": "Chapter 4 - Results",
            "section": "4.4 Diagnostics, failures, and stability",
            "main pages": "1_0_Revision_Analytics.py; 2_1_LLM_Error_Parse_Audit.py",
            "figures/tables": "Failure modes, missing labels, schema drift, prompt stability summary.",
            "message": "Prompt design and model configuration materially affect output quality.",
        },
        {
            "chapter": "Chapter 5 - Discussion",
            "section": "5.1 Meaning of the bilingual ESG ABSA findings",
            "main pages": "1_7_Research_Questions_Dashboard.py; 0_9_Tone_ClimateBERT_Visualization.py",
            "figures/tables": "Language x tone distribution, Indonesian vs English outcome asymmetry.",
            "message": "The bilingual asymmetry is the strongest descriptive finding but should be framed as feasibility evidence.",
        },
        {
            "chapter": "Chapter 5 - Discussion",
            "section": "5.2 Greenwashing signal and construct validity",
            "main pages": "1_7_Research_Questions_Dashboard.py; 1_0_Revision_Analytics.py",
            "figures/tables": "Greenwashing index table, commitment vs outcome ratio, document-level risk.",
            "message": "The index is useful as a prototype signal, but document coverage is too small for general claims.",
        },
        {
            "chapter": "Chapter 5 - Discussion",
            "section": "5.3 Reliability, validity, and limitations",
            "main pages": "1_8_Ground_Truth_Output_Visualizer.py; 1_3_Ground_Truth_Metrics.py; 1_2_OCR_Quality_Workbench.py",
            "figures/tables": "Annotation coverage, disagreement views, OCR quality gaps, sample-size ladder.",
            "message": "The main threats are missing expert labels, limited sample size, sparse Social-pillar records, and unmatched model comparisons.",
        },
        {
            "chapter": "Chapter 6 - Conclusion",
            "section": "6.1 Answers to research questions",
            "main pages": "1_7_Research_Questions_Dashboard.py",
            "figures/tables": "Evidence matrix and RQ-to-page map.",
            "message": "Summarize each RQ as implemented, partly validated, or requiring follow-up evidence.",
        },
        {
            "chapter": "Chapter 6 - Conclusion",
            "section": "6.2 Contributions",
            "main pages": "1_7_Research_Questions_Dashboard.py; 1_5_ESG_Flow_Sankey.py; 1_6_Ontology_Path_Viewer.py",
            "figures/tables": "Workflow map, ontology path, dashboard outputs, reproducibility artifacts.",
            "message": "The contribution is an auditable bilingual ESG ABSA prototype, not a fully supervised benchmark model.",
        },
        {
            "chapter": "Chapter 6 - Conclusion",
            "section": "6.3 Future work",
            "main pages": "1_7_Research_Questions_Dashboard.py; 1_4_ClimateBERT_Record_Batch.py; 1_1_Ground_Truth_Workbench.py",
            "figures/tables": "Prioritized analysis plan, sample-size target, annotation plan.",
            "message": "The next work is targeted collection, real ClimateBERT scoring, expert annotation, and matched cross-model reruns.",
        },
    ]
)

chapter_flow = """
flowchart LR
  subgraph C4["Chapter 4 - Results"]
    C41["4.1 Pipeline output\\nPDF/OCR -> structured ESG records"]
    C42["4.2 ESG ABSA results\\nTone, pillar, aspect, language"]
    C43["4.3 ClimateBERT proxy comparison\\nAgreement and label alignment"]
    C44["4.4 Diagnostics and stability\\nFailures, schema drift, prompt effects"]
  end

  subgraph C5["Chapter 5 - Discussion"]
    C51["5.1 Interpret bilingual ESG tone patterns"]
    C52["5.2 Discuss greenwashing signal validity"]
    C53["5.3 Explain limitations and reliability threats"]
  end

  subgraph C6["Chapter 6 - Conclusion"]
    C61["6.1 Answer each RQ"]
    C62["6.2 State contributions"]
    C63["6.3 Recommend future work"]
  end

  C41 --> C51
  C42 --> C51
  C42 --> C52
  C43 --> C53
  C44 --> C53
  C51 --> C61
  C52 --> C62
  C53 --> C63

  RQ1["RQ1 Pipeline"] --> C41
  RQ2["RQ2 Categorization"] --> C42
  RQ3["RQ3 ClimateBERT"] --> C43
  RQ4["RQ4 Diagnostics"] --> C44
  RQ5["RQ5 Auditability"] --> C62
  RQ6["RQ6 Stability"] --> C44

  Pages["Streamlit pages and artifacts"] --> C41
  Pages --> C42
  Pages --> C43
  Pages --> C44
"""

tabs = st.tabs(
    [
        "Overview",
        "Per-RQ Evidence",
        "RQ Page Map",
        "Sample Size",
        "Benchmarks",
        "Existing Results",
        "Analysis Plan",
        "Evidence Matrix",
        "Chapter 4 Results",
        "Chapter 5 Discussion",
        "Chapter 6 Conclusion",
        "Ch4-6 Mermaid",
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
    st.header("Which pages fulfill each research question")
    st.markdown(
        """
        Use this as the practical navigation layer for the thesis. Each row tells you which Streamlit pages
        and artifacts should be opened when writing or defending a specific research question.
        """
    )
    st.dataframe(rq_page_map, use_container_width=True, hide_index=True)

    st.subheader("Quick reading order")
    reading_order = pd.DataFrame(
        [
            {"step": "1", "open this first": "1_7_Research_Questions_Dashboard.py", "why": "Orient all RQs, chapter logic, sample-size limits, and evidence status."},
            {"step": "2", "open this first": "0_9_Tone_ClimateBERT_Visualization.py", "why": "Read the core ABSA results: tone, pillar, aspect, language, and ClimateBERT-style labels."},
            {"step": "3", "open this first": "1_0_Revision_Analytics.py", "why": "Use revision metrics, greenwashing evidence, stability, and failure summaries."},
            {"step": "4", "open this first": "1_8_Ground_Truth_Output_Visualizer.py", "why": "Check annotation coverage, review needs, and validation gaps."},
            {"step": "5", "open this first": "2_1_LLM_Error_Parse_Audit.py", "why": "Support the diagnostics and limitations discussion with concrete parse/error evidence."},
            {"step": "6", "open this first": "1_4_ClimateBERT_Record_Batch.py", "why": "Explain how RQ3 becomes fully validated once real ClimateBERT outputs are imported."},
        ]
    )
    st.dataframe(reading_order, use_container_width=True, hide_index=True)

    st.info(
        "Most writing should cite the dashboard for synthesis, then cite the more specific page for the figure/table that proves the point."
    )

with tabs[3]:
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

with tabs[4]:
    st.header("Benchmark reference")
    st.dataframe(benchmark_rows, use_container_width=True, hide_index=True)
    st.markdown(
        """
        Benchmark implication: this thesis should not claim supervised ABSA model performance until expert labels exist.
        It can currently claim a structured extraction pipeline, descriptive bilingual ABSA findings, diagnostics, and a
        prototype greenwashing signal. F1/precision/recall belong after P2 expert annotation.
        """
    )

with tabs[5]:
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

with tabs[6]:
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

with tabs[7]:
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

with tabs[8]:
    st.header("Chapter 4 - Results")
    st.markdown(
        """
        Chapter 4 should report what the system produced and what the results show. Keep this chapter
        evidence-forward: figures, counts, charts, tables, and direct answers to the empirical part of each RQ.
        Interpretation belongs mostly in Chapter 5.
        """
    )
    ch4 = chapter_plan[chapter_plan["chapter"].eq("Chapter 4 - Results")]
    st.dataframe(ch4, use_container_width=True, hide_index=True)

    st.subheader("Recommended Chapter 4 storyline")
    st.markdown(
        """
        1. Start with the pipeline output: reports, OCR-derived text, structured ESG records, and provenance.
        2. Present the core ABSA distributions: tone, ESG pillar, aspect, sentiment, and language.
        3. Present ClimateBERT-style comparison as proxy validation, while clearly labeling it as proxy evidence.
        4. Present diagnostics and prompt stability as results, not as excuses: missing tone, schema drift, and prompt effects are findings.
        5. End with the evidence matrix so the reader sees which RQs are fully supported and which need follow-up validation.
        """
    )

    st.subheader("Chapter 4 figure checklist")
    st.dataframe(
        pd.DataFrame(
            [
                {"figure/table": "Structured records summary", "source page": "1_9_Ground_Truth_Pipeline_Output_Visualizer.py", "use for": "RQ1"},
                {"figure/table": "Tone distribution", "source page": "0_9_Tone_ClimateBERT_Visualization.py", "use for": "RQ2"},
                {"figure/table": "ESG by tone and aspect heatmap", "source page": "0_9_Tone_ClimateBERT_Visualization.py", "use for": "RQ2"},
                {"figure/table": "ClimateBERT label by tone", "source page": "0_9_Tone_ClimateBERT_Visualization.py", "use for": "RQ3"},
                {"figure/table": "Failure modes and schema drift", "source page": "2_1_LLM_Error_Parse_Audit.py", "use for": "RQ4"},
                {"figure/table": "Prompt stability summary", "source page": "1_0_Revision_Analytics.py", "use for": "RQ6"},
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

with tabs[9]:
    st.header("Chapter 5 - Discussion")
    st.markdown(
        """
        Chapter 5 should explain what the Chapter 4 results mean, how strong each claim is, and where
        the thesis must be careful. This is where sample-size reasoning, construct validity, and limitations
        become central.
        """
    )
    ch5 = chapter_plan[chapter_plan["chapter"].eq("Chapter 5 - Discussion")]
    st.dataframe(ch5, use_container_width=True, hide_index=True)

    st.subheader("Recommended Chapter 5 arguments")
    st.markdown(
        """
        1. The bilingual outcome-rate asymmetry is the strongest descriptive insight, but it should be framed as feasibility-level evidence.
        2. The greenwashing index is useful as a prototype construct because it compares commitment-heavy and outcome-rich disclosure, but document coverage is not yet enough for generalization.
        3. Prompt strategy changes the tone distribution, so the system should be discussed as an auditable extraction workflow rather than a single stable classifier.
        4. The Social-pillar shortage is a sampling/design problem, not merely a total-n problem.
        5. The absence of expert labels means the thesis can report descriptive validity and proxy alignment, but not final precision, recall, or F1.
        """
    )

    st.subheader("Discussion claims and cautions")
    st.dataframe(
        pd.DataFrame(
            [
                {"claim": "Pipeline can produce structured ESG records", "strength": "strong", "caution": "OCR quality still needs CER/WER samples."},
                {"claim": "Tone distributions reveal commitment/action/outcome patterns", "strength": "moderate", "caution": "Ground truth is needed for final classification validity."},
                {"claim": "Indonesian and English disclosures differ in outcome/action framing", "strength": "promising", "caution": "Check document-level confounds and expand sample."},
                {"claim": "Greenwashing index separates commitment-heavy from outcome-rich documents", "strength": "prototype", "caution": "Needs 15+ documents and per-prompt stability checks."},
                {"claim": "Prompt strategy affects extraction stability", "strength": "strong within current runs", "caution": "Cross-model comparison is confounded until matched runs exist."},
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

with tabs[10]:
    st.header("Chapter 6 - Conclusion")
    st.markdown(
        """
        Chapter 6 should be concise: answer each RQ, state the contribution, name the main limitations,
        and convert the remaining gaps into a future-work plan.
        """
    )
    ch6 = chapter_plan[chapter_plan["chapter"].eq("Chapter 6 - Conclusion")]
    st.dataframe(ch6, use_container_width=True, hide_index=True)

    st.subheader("RQ answer template")
    st.dataframe(
        pd.DataFrame(
            [
                {"RQ": "RQ1", "answer": "The pipeline converts report-derived text into structured ESG records with provenance.", "status": "Implemented, OCR quality partly validated"},
                {"RQ": "RQ2", "answer": "Records can be categorized by aspect, pillar, tone, sentiment, and language for descriptive ABSA.", "status": "Implemented, expert-label validation pending"},
                {"RQ": "RQ3", "answer": "Tone outputs can be compared with ClimateBERT-style labels as a proxy alignment analysis.", "status": "Proxy validated, real ClimateBERT batch pending"},
                {"RQ": "RQ4", "answer": "Diagnostics reveal missing tones, schema drift, ontology gaps, and prompt/model failure modes.", "status": "Implemented, manual error-rate labels pending"},
                {"RQ": "RQ5", "answer": "The workflow is auditable through Streamlit pages, CSV/JSON artifacts, screenshots, and documentation.", "status": "Implemented, reproducibility checklist pending"},
                {"RQ": "RQ6", "answer": "Prompt strategy materially changes output stability; ensemble and matched reruns are the next reliability step.", "status": "Partly validated, matched cross-model runs pending"},
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Conclusion language")
    st.success(
        "The thesis contribution is an auditable bilingual ESG ABSA prototype with descriptive evidence, diagnostics, and a greenwashing-signal workflow. It should not be framed as a fully supervised benchmark model until expert annotation and larger matched samples are complete."
    )

with tabs[11]:
    st.header("Mermaid flow: Chapter 4 to Chapter 6")
    st.markdown(
        """
        This diagram links empirical results to discussion arguments and final conclusions. Use it as a writing
        guide: every Chapter 5 interpretation should point back to a Chapter 4 result, and every Chapter 6
        conclusion should follow from that evidence chain.
        """
    )
    render_mermaid(chapter_flow, height=760)
    st.subheader("Mermaid source")
    st.code(chapter_flow, language="mermaid")
