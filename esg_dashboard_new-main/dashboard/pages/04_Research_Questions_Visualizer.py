from pathlib import Path
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Research Questions Visualizer", layout="wide")
st.title("Research Questions Visualizer")
st.caption("Interactive view of thesis RQs, available evidence, analysis gaps, and next steps.")


SOURCE_HTML = Path(__file__).resolve().parent / "thesis_data_analysis_benchmarks.html"
EXISTING_DATA_PATH = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/data_output.txt"
PREDICTION_OUTPUT_DIR = "/home/ubuntu/apps/benchmarks/esg_dashboard_new-main/dashboard/data/data/climatebert_predictions"


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

MISSING_WORK = pd.DataFrame([
    [
        "RQ1",
        "OCR and segmentation quality",
        "Sample pages from data_output provenance, manually transcribe reference text, compute CER/WER and sentence-boundary precision.",
        EXISTING_DATA_PATH,
        "CER, WER, sentence precision/recall, table extraction accuracy",
    ],
    [
        "RQ2",
        "Gold taxonomy validation",
        "Draw 30-50 stratified records from parsed ESG sentences, have two annotators label aspect/pillar/tone/sentiment, compute agreement and F1.",
        EXISTING_DATA_PATH,
        "Cohen kappa, precision, recall, F1, ontology mapping coverage",
    ],
    [
        "RQ3",
        "Actual ClimateBERT comparison",
        "Run local ClimateBERT/ESGBERT models on every parsed sentence, then compare predicted labels with LLM tone/aspect fields.",
        PREDICTION_OUTPUT_DIR,
        "Tone x ClimateBERT crosstab, agreement rate, Cohen kappa",
    ],
    [
        "RQ4",
        "Diagnostics and error taxonomy",
        "Use parsed output plus manual spot checks to label schema drift, missing tone, wrong aspect, wrong pillar, and OCR-noise errors.",
        EXISTING_DATA_PATH,
        "Error rate by model, prompt, document, language, and pillar",
    ],
    [
        "RQ5",
        "Reproducibility evidence",
        "Connect saved artifacts, exact prompts, model versions, Streamlit pages, and regenerated outputs into an audit trail.",
        f"{EXISTING_DATA_PATH} + {PREDICTION_OUTPUT_DIR}",
        "Artifact inventory, rerun checklist, dashboard traceability",
    ],
    [
        "RQ6",
        "Stability and ensemble analysis",
        "Balance model x prompt x document coverage, then compare prompt variance and majority-vote/ensemble stability.",
        EXISTING_DATA_PATH,
        "Coefficient of variation, cross-model kappa, ensemble stability gain",
    ],
], columns=["rq", "missing_piece", "process", "primary_source", "output_metric"])

RQ_TABLE_GUIDE = pd.DataFrame([
    [
        "RQ1",
        "Pipeline",
        "Shows whether the PDF-to-Markdown-to-JSON pipeline is technically reliable enough to be used as the foundation for ABSA.",
        "JSON parse success, records per run, field completion, OCR CER/WER, sentence-boundary precision/recall, table extraction accuracy.",
        "JSON parse success near 100%; required fields complete; CER low enough that sentence meaning is preserved; segmentation errors rare; records trace back to page/source.",
        "If CER/WER is high, source text may be noisy and all downstream ESG labels become less trustworthy. If segmentation is poor, ABSA may classify fragments or merged sentences. If provenance is missing, auditability fails.",
        "Use data_output.txt for parsed records and provenance. Add manual OCR references for a small page sample to compute CER/WER.",
    ],
    [
        "RQ2",
        "Categorization",
        "Checks whether aspect, pillar, sentiment, and tone labels are valid and comparable across Indonesian and English disclosures.",
        "Expert-label agreement, Cohen kappa, precision/recall/F1 per tone/aspect/pillar, ontology coverage, bilingual label consistency.",
        "Kappa >= 0.70 for acceptable annotation agreement; F1 high enough per category, ideally >= 0.65 for each tone; non-standard aspect labels mapped into a stable taxonomy.",
        "Underperformance means the LLM labels are weak descriptive labels rather than validated ABSA labels. S-pillar underrepresentation means Social conclusions are not defensible yet.",
        "Draw a stratified sample from data_output.txt by tone, language, and pillar. Two annotators label the same records, then compare model labels with gold labels.",
    ],
    [
        "RQ3",
        "ClimateBERT",
        "Compares thesis tone-based ABSA against local ClimateBERT or ESGBERT model classifications.",
        "Coverage of ClimateBERT predictions, tone x ClimateBERT crosstab, agreement rate, Cohen kappa, model confidence distribution.",
        "Every valid sentence has predictions for selected models; agreement patterns are explainable; ClimateBERT adds a distinct climate-specific signal beyond LLM tone.",
        "If only a few rows have predictions, RQ3 remains incomplete. If agreement is very low, either mappings are wrong, ClimateBERT label space is incompatible, or LLM tone is measuring a different construct.",
        "Use climatebert_predictions as the primary source. Join predictions back to data_output.txt by sentence and compare labels to tone/aspect.",
    ],
    [
        "RQ4",
        "Diagnostics",
        "Quantifies where extraction fails and whether failures are caused by prompt design, model choice, OCR noise, schema drift, or ontology mismatch.",
        "Missing-tone rate, schema-drift rate, wrong-aspect rate, wrong-pillar rate, ontology failure rate, error rate by model/prompt/document/language.",
        "Low schema drift outside known bad prompts; missing tone near zero for stable models; error categories explainable and reducible through prompt/schema fixes.",
        "If drift clusters around one prompt/model, that prompt/model is unsafe. If errors are spread evenly, the taxonomy or source data may be underspecified.",
        "Use data_output.txt plus manual spot checks. Add an error_type column for sampled records and summarize by model/prompt/document.",
    ],
    [
        "RQ5",
        "Reproducibility",
        "Shows whether another person can trace, rerun, audit, and verify the ESG ABSA pipeline and its outputs.",
        "Artifact inventory, exact prompt registry, model version list, rerun checklist, saved outputs, dashboard traceability, replication log.",
        "Every chart/table links back to a dataset, prompt, model, and code path; outputs are reproducible or deviations are documented.",
        "If prompts, model versions, or output files are missing, the result may be visually persuasive but not auditable. This weakens thesis credibility even if metrics look good.",
        "Use both data_output.txt and climatebert_predictions, plus Streamlit pages and prompt files, to build an artifact checklist.",
    ],
    [
        "RQ6",
        "Stability",
        "Measures whether ABSA outputs are stable across model and prompt choices, and whether ensemble strategies improve reliability.",
        "Coefficient of variation across prompts, cross-model Cohen kappa, prompt-family effect size, majority-vote agreement, per-document variance.",
        "Balanced model x prompt x document coverage; lower variance after ensemble/majority voting; prompt differences are quantified rather than anecdotal.",
        "If one prompt has too few records or one model covers different documents, comparisons are confounded. High CV means results depend strongly on prompt design.",
        "Use data_output.txt to create a balanced comparison matrix. Target few-shot n >= 30 and matched documents across models/prompts.",
    ],
], columns=[
    "rq",
    "table_area",
    "what_this_table_does",
    "expected_metrics",
    "if_performing_well",
    "if_underperforming",
    "how_to_process",
])

TABLE_EXPLANATIONS = pd.DataFrame([
    [
        "Overview readiness chart",
        "Counts the number of available, partial, and needed evidence items for each RQ.",
        "It is not a statistical result. It is a project-management/readiness view.",
        "High available count and low needed count means an RQ is close to being defensible.",
        "High needed count means the RQ still needs data collection, annotation, or model runs before it can be claimed strongly.",
    ],
    [
        "RQ Details - Matrix",
        "Expands every RQ into individual evidence rows with status: Available, Partial, or Needed.",
        "Use it as the checklist of what evidence you already have and what is missing.",
        "Available rows can be cited as current evidence if the source is traceable.",
        "Needed rows are thesis risks; partial rows should be upgraded before strong claims.",
    ],
    [
        "RQ Details - Metrics",
        "Shows the headline metrics currently attached to each RQ.",
        "These are the thesis-facing indicators that should appear in results/discussion.",
        "A metric with a concrete value and clear denominator is stronger than a vague qualitative statement.",
        "A missing metric means the RQ is currently argued conceptually rather than empirically.",
    ],
    [
        "Missing Work Process",
        "Turns each missing RQ requirement into an action: source, process, and expected output metric.",
        "This table tells you exactly what to run or annotate next.",
        "A row is complete when the output metric can be computed and added back to the RQ metric table.",
        "If the source is unavailable or the metric cannot be computed, the RQ scope must be narrowed.",
    ],
    [
        "Analysis Plan",
        "Prioritizes the remaining analyses by urgency, effort, and which RQs they answer.",
        "It is the execution roadmap for closing thesis evidence gaps.",
        "Critical/High items should be handled before lower-priority documentation polish.",
        "If critical items remain undone, the thesis should avoid strong claims for those RQs.",
    ],
], columns=[
    "table_name",
    "what_it_does",
    "how_to_read_it",
    "if_yes_or_good",
    "if_underperforming_or_missing",
])


def render_mermaid(code: str, height: int = 520) -> None:
    html = f"""
    <div id="mermaid-wrapper">
      <pre class="mermaid">{escape(code)}</pre>
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{
        startOnLoad: true,
        securityLevel: 'loose',
        theme: 'base',
        flowchart: {{ curve: 'basis', htmlLabels: true }},
        themeVariables: {{
          primaryColor: '#f8fafc',
          primaryTextColor: '#111827',
          primaryBorderColor: '#64748b',
          lineColor: '#475569',
          clusterBkg: '#eef6f4',
          clusterBorder: '#0f766e',
          edgeLabelBackground: '#ffffff'
        }}
      }});
    </script>
    <style>
      #mermaid-wrapper {{
        background: #ffffff;
        border: 1px solid #d4dbe5;
        border-radius: 8px;
        min-height: {height}px;
        overflow: auto;
        padding: 18px;
      }}
      .mermaid {{
        display: flex;
        justify-content: center;
        min-width: 980px;
      }}
      svg {{
        max-width: none !important;
        height: auto;
      }}
    </style>
    """
    components.html(html, height=height + 70, scrolling=True)


PIPELINE_MERMAID = f"""
flowchart LR
  PDFs["Sustainability reports - PDF source pages"]
  OCR["OCR and markdown extraction"]
  LLM["LLM ESG JSON extraction"]
  DataOutput["data_output.txt - sentence ESG records"]
  Parsed["Parsed ESG table - sentence aspect tone sentiment"]
  CBRun["Local ClimateBERT processor - page 02"]
  CBOut["climatebert_predictions - saved shard CSVs"]
  Viz["Result visualizer - page 03"]
  RQ["Research question evidence - page 04"]

  PDFs --> OCR --> LLM --> DataOutput --> Parsed
  Parsed --> CBRun --> CBOut --> Viz
  Parsed --> RQ
  CBOut --> RQ
""".strip()

RQ_MERMAID = """
flowchart TB
  RQ1["RQ1 Pipeline quality - needs CER WER segmentation"]
  RQ2["RQ2 Categorization - needs expert labels and taxonomy"]
  RQ3["RQ3 ClimateBERT comparison - needs full local outputs"]
  RQ4["RQ4 Diagnostics - needs manual error taxonomy"]
  RQ5["RQ5 Reproducibility - needs audit checklist and rerun log"]
  RQ6["RQ6 Stability - needs balanced model prompt matrix"]

  Data["data_output.txt"]
  Pred["climatebert_predictions"]
  Gold["Expert annotation sample"]
  Audit["Artifact registry / dashboard"]

  Data --> RQ1
  Data --> RQ2
  Data --> RQ4
  Data --> RQ6
  Pred --> RQ3
  Pred --> RQ5
  Gold --> RQ2
  Gold --> RQ4
  Audit --> RQ5
  RQ3 --> RQ6
""".strip()

MISSING_PROCESS_MERMAID = """
flowchart LR
  Gap["Missing RQ evidence"]
  Identify["Identify missing metric from RQ matrix"]
  Source["Select source - data_output or predictions"]
  Sample["Create targeted sample by RQ weakness"]
  Run["Run analysis or annotation"]
  Metric["Compute metric"]
  Update["Update dashboard evidence"]

  Gap --> Identify --> Source --> Sample --> Run --> Metric --> Update

  Source --> A["data_output.txt - parsed LLM ESG records"]
  Source --> B["climatebert_predictions - local model outputs"]
  Run --> C["manual annotation for RQ2 and RQ4"]
  Run --> D["ClimateBERT comparison for RQ3"]
  Run --> E["prompt model stability for RQ6"]
""".strip()


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
    view_mode = st.radio(
        "Detail view",
        ["Matrix", "Question Cards", "Metrics", "Detailed Explanation"],
        horizontal=False,
    )


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
st.caption(f"Existing data: `{EXISTING_DATA_PATH}`")
st.caption(f"Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")

tab_overview, tab_details, tab_guide, tab_missing, tab_mermaid, tab_plan, tab_source = st.tabs([
    "Overview",
    "RQ Details",
    "Table Guide",
    "Missing Work Process",
    "Mermaid Preview",
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

    elif view_mode == "Metrics":
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

    else:
        guide = RQ_TABLE_GUIDE
        if rq_filter:
            guide = guide[guide["rq"].isin(rq_filter)]
        st.dataframe(guide, use_container_width=True, height=620)

with tab_guide:
    st.subheader("How to Interpret the Tables")
    st.dataframe(TABLE_EXPLANATIONS, use_container_width=True, height=300)

    st.subheader("Expected Metrics and Interpretation by RQ")
    guide = RQ_TABLE_GUIDE.copy()
    if rq_filter:
        guide = guide[guide["rq"].isin(rq_filter)]
    st.dataframe(guide, use_container_width=True, height=620)

    selected_guide_rq = st.selectbox("Detailed explanation for RQ", guide["rq"].tolist())
    guide_row = guide[guide["rq"] == selected_guide_rq].iloc[0]
    st.markdown(f"**What it does:** {guide_row['what_this_table_does']}")
    st.markdown(f"**Expected metrics:** {guide_row['expected_metrics']}")
    st.markdown(f"**If performing well:** {guide_row['if_performing_well']}")
    st.markdown(f"**If underperforming:** {guide_row['if_underperforming']}")
    st.markdown(f"**How to process:** {guide_row['how_to_process']}")

with tab_missing:
    st.subheader("How to Process the Missing Research-Question Evidence")
    st.write(
        "The page treats the existing parsed dataset as the main source of LLM ESG evidence, "
        "and the ClimateBERT prediction folder as the source of local-model comparison evidence."
    )
    st.dataframe(MISSING_WORK, use_container_width=True, height=420)

    selected_missing_rq = st.selectbox("Explain one RQ gap", MISSING_WORK["rq"].tolist())
    row = MISSING_WORK[MISSING_WORK["rq"] == selected_missing_rq].iloc[0]
    st.markdown(f"**Missing piece:** {row['missing_piece']}")
    st.markdown(f"**Process:** {row['process']}")
    st.markdown(f"**Primary source:** `{row['primary_source']}`")
    st.markdown(f"**Output metric:** {row['output_metric']}")

with tab_mermaid:
    st.subheader("Workflow Diagram")
    render_mermaid(PIPELINE_MERMAID, height=430)
    st.code(PIPELINE_MERMAID, language="mermaid")

    st.subheader("Research Question Evidence Map")
    render_mermaid(RQ_MERMAID, height=520)
    st.code(RQ_MERMAID, language="mermaid")

    st.subheader("Missing Evidence Process")
    render_mermaid(MISSING_PROCESS_MERMAID, height=430)
    st.code(MISSING_PROCESS_MERMAID, language="mermaid")

with tab_plan:
    st.subheader("Prioritized Next Analyses")
    plan = ANALYSIS_PLAN[ANALYSIS_PLAN["urgency"].isin(priority_filter)]
    st.dataframe(plan, use_container_width=True)
    if not plan.empty:
        st.bar_chart(plan["answers"].str.get_dummies(sep=", ").sum().sort_values(ascending=False))

with tab_source:
    st.caption(f"Source: `{SOURCE_HTML}`")
    st.info("This Streamlit page is a native visualization distilled from the HTML thesis benchmark artifact.")
