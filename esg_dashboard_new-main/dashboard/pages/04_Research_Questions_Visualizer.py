from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Research Questions Visualizer", layout="wide")
st.title("Research Questions Visualizer")
st.caption("Interactive view of thesis RQs, available evidence, analysis gaps, and next steps.")


SOURCE_HTML = Path(__file__).resolve().parent / "thesis_data_analysis_benchmarks.html"


RQ_DATA = [
    {
        "rq": "RQ1",
        "theme": "Pipeline",
        "question": "How can a PDF-to-structured ESG transformation pipeline convert Indonesian/English sustainability reports into a governance-aligned, sentence-level representation that supports ABSA?",
        "have": [
            "PDF sustainability reports: 6 docs available; BEST, VKTR, GTRA, PTBA, ICR, Indonet",
            "Markdown page outputs from OCR pipeline with source-page traceability",
            "Records-per-run throughput: mean 8.5 records/run; Arcee 14.3 records/run",
            "Field completion: 100% aspect/ESG/tone; 81.3% sentiment_score",
        ],
        "partial": ["JSON extraction records with provenance: 332 records"],
        "need": [
            "Reference text for CER computation",
            "Table/figure extraction accuracy labels",
            "Sentence boundary precision/recall",
            "ESG topic alignment accuracy from manual verification",
        ],
        "metrics": [
            ("JSON parse success", "100%", "332/332 records parseable"),
            ("Records extracted", "332", "from 6 docs and 39 unique runs"),
            ("OCR quality CER", "missing", "critical gap"),
        ],
        "priority": "Important",
    },
    {
        "rq": "RQ2",
        "theme": "Categorization",
        "question": "How should ESG be categorized by aspect/pillar, sentiment, and tone in bilingual disclosures to enable fine-grained ABSA while preserving cross-language comparability?",
        "have": [
            "Tone x ESG pillar cross-tabulation: E commitment=91, G commitment=24, S commitment=0",
            "Bilingual tone asymmetry: Indonesian outcome 7.9% vs English 21.8%",
            "Sentiment score distribution by tone: outcome mean=0.60 vs commitment mean=0.03",
        ],
        "partial": [
            "LLM labels: 332 records; commitment=115, action=58, outcome=50",
            "Language-tagged records: Indonesian=127, English=205",
        ],
        "need": [
            "Expert-annotated ground truth corpus: 30-50 records, 2 annotators",
            "Bilingual taxonomy mapping",
            "Aspect precision/recall/F1 vs gold labels",
            "Inter-annotator agreement, target Cohen kappa >= 0.70",
            "Ontology normalization for 41 non-standard aspects",
        ],
        "metrics": [
            ("Tone: commitment", "34.6%", "115/332, dominant category"),
            ("E/G/S split", "54/36/1%", "S severely underrepresented"),
            ("Non-standard aspects", "41", "ontology gap"),
        ],
        "priority": "Critical",
    },
    {
        "rq": "RQ3",
        "theme": "ClimateBERT",
        "question": "Do tone-based ABSA outputs differ meaningfully from ClimateBERT-style label classifications, and what is the relationship between detected tone and climate-specific targets?",
        "have": [
            "LLM-assigned ClimateBERT-style label families: 16 label families",
            "Co-occurrence frequency: commitment + climate-commitment = 91",
        ],
        "partial": [
            "Tone x ClimateBERT label crosstab exists, but labels are LLM-assigned",
            "Missing tone vs CB label analysis identifies possible false negatives",
        ],
        "need": [
            "ClimateBERT scores for all valid records from local runs",
            "Row-wise agreement between tone and ClimateBERT labels",
            "Cohen kappa between LLM tone and ClimateBERT classification",
        ],
        "metrics": [
            ("CB alignment commitment", "34.3%", "91/265 commitment records carry climate-commitment"),
            ("CB remote inputs", "3", "far too few; must run locally"),
            ("CB models available", "13", "detection, netzero, TCFD, sentiment, specificity"),
        ],
        "priority": "Critical",
    },
    {
        "rq": "RQ4",
        "theme": "Diagnostics",
        "question": "What weaknesses arise in ABSA extraction outputs, and how can a diagnostics framework detect and quantify extraction errors to inform model improvement?",
        "have": [
            "Complete extraction log per run",
            "Schema drift records: 18 records from data.md + GPT-oss-120b",
            "Missing tone records with context: 61 records",
            "Root cause attribution by model x prompt",
            "Schema drift rate by prompt template",
        ],
        "partial": [
            "Non-standard aspect labels: 41 unique free-text Indonesian labels",
            "Ontology failure rate: 41/332 = 12.3%",
            "Tone none analysis by prompt/pillar",
        ],
        "need": [
            "Manual error labels per record",
            "Formal error taxonomy: wrong-aspect, wrong-tone, wrong-pillar, schema-failure, OCR-noise",
        ],
        "metrics": [
            ("Missing tone, Arcee only", "0.4%", "1/272"),
            ("Schema drift rate", "30%", "18/60 records from data.md"),
            ("Ontology gap", "41", "all Indonesian free-text"),
        ],
        "priority": "Critical",
    },
    {
        "rq": "RQ5",
        "theme": "Reproducibility",
        "question": "How can documentation and visualization practices be designed to maximize reproducibility and auditability of ESG ABSA experiments?",
        "have": [
            "JSON extraction artifacts with full metadata",
            "Static visualization outputs: 5 PNG charts",
            "Streamlit dashboard with filterable tabs",
            "Artifact inventory and completeness audit",
        ],
        "partial": ["Prompt template version registry: 6 templates documented"],
        "need": [
            "Independent replication study log",
            "Formal reproducibility checklist",
            "Schema stability regression test",
            "Dashboard usability evaluation",
        ],
        "metrics": [
            ("Artifacts available", "5+5+1", "5 CSVs, 5 PNGs, 1 Streamlit app"),
            ("Prompt templates logged", "6", "zero-shot, few-shot, CoT, EN/ID variants"),
            ("Replication study", "0", "not yet conducted"),
        ],
        "priority": "Medium",
    },
    {
        "rq": "RQ6",
        "theme": "Stability",
        "question": "What is the stability of ABSA outputs across cross-model and cross-prompt configurations, and what ensemble or verification strategies yield the most reliable results?",
        "have": [
            "Prompt family effect: CoT +55% commitment, zero-shot +21-24%, few-shot +36%",
            "Coefficient of variation across prompts: 38.2%",
            "Language x prompt interaction",
        ],
        "partial": [
            "Per-prompt tone distributions, Arcee only",
            "Per-document commitment rate by prompt",
            "Per-document commitment variance: BEST-SR CoT=100% vs ZS=43%",
        ],
        "need": [
            "Balanced model x prompt x document matrix",
            "Few-shot template with n >= 30",
            "Cross-model Cohen kappa",
            "Ensemble majority-vote simulation",
        ],
        "metrics": [
            ("Prompt instability CV", "38.2%", "high variation across 5 prompts"),
            ("CoT vs zero-shot gap", "+31pp", "55% vs 23% commitment"),
            ("Cross-model kappa", "missing", "imbalanced runs"),
        ],
        "priority": "High",
    },
]


ANALYSIS_PLAN = pd.DataFrame([
    ["P1", "Run ClimateBERT on all valid records", "1-2 days", "RQ3", "Critical"],
    ["P2", "Expert annotation 30-50 records + IAA", "2-3 weeks", "RQ2, RQ4", "Critical"],
    ["P3", "Ensemble majority-vote on PTBA", "1 day", "RQ6", "High"],
    ["P4", "Statistical test of bilingual asymmetry", "2 hours", "RQ2", "High"],
    ["P5", "GW index per-doc per-prompt stability", "1 day", "RQ3, RQ5", "Medium"],
    ["P6", "S-pillar extraction + GPT-oss balance", "2-3 days", "RQ2, RQ6", "Medium"],
    ["P7", "OCR quality measurement", "1-2 days", "RQ1", "Important"],
], columns=["priority_id", "task", "effort", "answers", "urgency"])


def status_counts(rows):
    return pd.DataFrame([
        {
            "rq": item["rq"],
            "theme": item["theme"],
            "available": len(item["have"]),
            "partial": len(item["partial"]),
            "needed": len(item["need"]),
            "priority": item["priority"],
        }
        for item in rows
    ])


with st.sidebar:
    st.header("Filters")
    priority_filter = st.multiselect(
        "Priority",
        ["Critical", "High", "Medium", "Important"],
        default=["Critical", "High", "Medium", "Important"],
    )
    rq_filter = st.multiselect("Research Questions", [item["rq"] for item in RQ_DATA])
    view_mode = st.radio("Detail view", ["Matrix", "Question Cards", "Metrics"], horizontal=False)


filtered = [
    item for item in RQ_DATA
    if item["priority"] in priority_filter and (not rq_filter or item["rq"] in rq_filter)
]
summary = status_counts(filtered)

cols = st.columns(4)
cols[0].metric("Research questions", len(filtered))
cols[1].metric("Available evidence items", int(summary["available"].sum()) if not summary.empty else 0)
cols[2].metric("Partial evidence items", int(summary["partial"].sum()) if not summary.empty else 0)
cols[3].metric("Open needs", int(summary["needed"].sum()) if not summary.empty else 0)

tab_overview, tab_details, tab_plan, tab_source = st.tabs([
    "Overview",
    "RQ Details",
    "Analysis Plan",
    "Source HTML",
])

with tab_overview:
    if summary.empty:
        st.info("No RQs match the selected filters.")
    else:
        chart_df = summary.set_index("rq")[["available", "partial", "needed"]]
        st.subheader("Evidence Readiness by RQ")
        st.bar_chart(chart_df)
        st.dataframe(summary, use_container_width=True)

with tab_details:
    if view_mode == "Matrix":
        rows = []
        for item in filtered:
            for status, key in [("Available", "have"), ("Partial", "partial"), ("Needed", "need")]:
                for entry in item[key]:
                    rows.append({
                        "rq": item["rq"],
                        "theme": item["theme"],
                        "status": status,
                        "item": entry,
                        "priority": item["priority"],
                    })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=620)

    elif view_mode == "Question Cards":
        for item in filtered:
            st.subheader(f"{item['rq']} · {item['theme']}")
            st.write(item["question"])
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Available**")
                for entry in item["have"]:
                    st.write(f"- {entry}")
            with c2:
                st.markdown("**Partial**")
                for entry in item["partial"]:
                    st.write(f"- {entry}")
            with c3:
                st.markdown("**Needed**")
                for entry in item["need"]:
                    st.write(f"- {entry}")
            st.divider()

    else:
        metric_rows = []
        for item in filtered:
            for name, value, context in item["metrics"]:
                metric_rows.append({
                    "rq": item["rq"],
                    "theme": item["theme"],
                    "metric": name,
                    "value": value,
                    "context": context,
                })
        st.dataframe(pd.DataFrame(metric_rows), use_container_width=True, height=620)

with tab_plan:
    st.subheader("Prioritized Next Analyses")
    plan = ANALYSIS_PLAN[ANALYSIS_PLAN["urgency"].isin(priority_filter)]
    st.dataframe(plan, use_container_width=True)
    if not plan.empty:
        st.bar_chart(plan["answers"].str.get_dummies(sep=", ").sum().sort_values(ascending=False))

with tab_source:
    st.caption(f"Source: `{SOURCE_HTML}`")
    st.info("This Streamlit page is a native visualization distilled from the HTML thesis benchmark artifact.")
