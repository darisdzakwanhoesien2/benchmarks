from pathlib import Path
from html import escape
import json
import re

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Sample Size Reasoning", layout="wide")
st.title("Sample Size Reasoning")
st.caption("Interactive thesis sample-size reasoning for ESG ABSA claims.")


PAGE_DIR = Path(__file__).resolve().parent
BENCHMARKS_DIR = Path(__file__).resolve().parents[3]
SOURCE_HTML_CANDIDATES = [
    PAGE_DIR / "sample_size_reasoning.html",
    BENCHMARKS_DIR / "pages" / "sample_size_reasoning.html",
]
SOURCE_HTML = next(
    (path for path in SOURCE_HTML_CANDIDATES if path.exists()),
    SOURCE_HTML_CANDIDATES[0],
)
ABSA_METRICS_CANDIDATES = [
    PAGE_DIR / "absa_metrics_results.json",
    PAGE_DIR.parent / "absa_metrics_results.json",
    BENCHMARKS_DIR / "absa_metrics_results.json",
]
ABSA_METRICS_PATH = next(
    (path for path in ABSA_METRICS_CANDIDATES if path.exists()),
    ABSA_METRICS_CANDIDATES[0],
)
LOCAL_ABSA_METRICS_PATH = PAGE_DIR.parent / "absa_metrics_results_local_climate_controversy.json"


LADDER = pd.DataFrame([
    [272, "Pipeline feasibility prototype", "Current", "Supports descriptive tone distributions and pipeline feasibility; not enough for F1, full subgroups, or generalizable greenwashing claims."],
    [384, "Standard academic MoE threshold", "Minimum", "Reaches the conventional +/-5 percentage-point worst-case margin of error."],
    [500, "Balanced prompt comparison", "Minimum for RQ6", "About 100 records per prompt template across 5 templates; fixes the few-shot n=14 power issue."],
    [720, "Full bilingual subgroup analysis", "Recommended", "Covers pillar x language x tone matrix with about 30 records per cell."],
    [1000, "Literature-comparable extraction study", "Strong target", "Makes the greenwashing index a credible distributional metric and reaches accepted exploratory ESG NLP scale."],
    [1500, "Expert annotation enables F1 reporting", "Evaluation target", "Allows 1,000 extracted records plus about 500 expert-annotated records for train/test evaluation."],
    [2000, "Fine-tuning bilingual ABSA", "Out of scope", "Required for supervised mBERT/XLM-R style model training with enough records per language/class."],
], columns=["n", "claim_level", "status", "interpretation"])

MOE = pd.DataFrame([
    [272, 5.9, "Current"],
    [384, 5.0, "MoE threshold"],
    [500, 4.4, "Prompt comparison"],
    [600, 4.0, "Improved descriptive"],
    [720, 3.6, "Recommended"],
    [1000, 3.1, "Strong target"],
    [1500, 2.5, "Evaluation target"],
], columns=["n", "worst_case_moe_pp", "status"])

POWER = pd.DataFrame([
    ["ID vs EN outcome rate", "n=200 total", 0.789, "Below threshold"],
    ["ID vs EN outcome rate", "n=272 total", 0.897, "Sufficient"],
    ["ID vs EN outcome rate", "n=400 total", 0.974, "Strong"],
    ["Prompt comparison", "n=14 per template", 0.434, "Too low"],
    ["Prompt comparison", "n=30 per template", 0.747, "Marginal"],
    ["Prompt comparison", "n=40 per template", 0.858, "Acceptable"],
    ["Prompt comparison", "n=55 per template", 0.945, "Good"],
    ["Prompt comparison", "n=100 per template", 0.998, "Excellent"],
], columns=["test", "sample_condition", "power", "verdict"])

SUBGROUPS = pd.DataFrame([
    ["Tone categories only", "5 tones x 30", 150, "Met at n=272"],
    ["Language x tone", "2 languages x 4 tones x 30", 240, "Met at n=272"],
    ["Document x tone, relaxed", "6 docs x 4 tones x 10", 240, "Met at n=272"],
    ["ESG pillar x tone", "3 pillars x 4 tones x 30", 360, "Need 88 more"],
    ["Prompt template x tone", "5 prompts x 4 tones x 20", 400, "Need 128 more"],
    ["Pillar x language x tone", "3 pillars x 2 languages x 4 tones x 30", 720, "Recommended target"],
], columns=["subgroup_claim", "formula", "required_n", "status"])

LITERATURE = pd.DataFrame([
    ["FinBERT", "Financial sentiment", 10000],
    ["ESG-BERT", "ESG category", 2400],
    ["ClimateBERT-NetZero", "Net-zero target detection", 3000],
    ["Gorovaia & Makrominas 2024", "Greenwashing in CSR", 1200],
    ["Moreno & Caminero 2020", "Climate text mining", 800],
    ["Garrido-Merchan 2023", "Disclosure risk", 500],
    ["Current study", "ESG ABSA bilingual extraction", 272],
    ["Recommended thesis target", "ESG ABSA bilingual evaluation", 1000],
], columns=["study", "scope", "scale"])

TABLE_GUIDE = pd.DataFrame([
    [
        "Claim Ladder",
        "Maps record counts to the strongest thesis claim each sample size can support.",
        "Use this as the framing guardrail: the current n can support feasibility, while higher targets unlock subgroup and benchmark claims.",
        "A target is defensible when its claim level matches the analyses actually performed.",
        "If the thesis claim is stronger than the ladder level, the conclusion should be softened or the sample expanded.",
    ],
    [
        "Margin of Error",
        "Shows worst-case uncertainty for simple proportions using p=0.50.",
        "It is a descriptive precision check, not a substitute for annotation quality or subgroup balance.",
        "Lower MoE means aggregate percentages can be described with more confidence.",
        "A good aggregate MoE can still hide weak subgroup cells.",
    ],
    [
        "Power",
        "Summarizes whether planned comparisons have enough observations to detect expected effects.",
        "Read power below 0.80 as underpowered, around 0.80 as acceptable, and above 0.90 as strong.",
        "The ID vs EN outcome-rate comparison is already plausible at n=272.",
        "Few-shot and prompt comparisons remain weak until each prompt template has enough rows.",
    ],
    [
        "Subgroups",
        "Converts matrix claims into required record counts.",
        "Use this to decide whether the thesis can discuss tone, language, pillar, document, or prompt-level comparisons.",
        "A subgroup claim is stronger when every important cell has roughly the chosen minimum cell n.",
        "Tiny or empty cells should be reported as gaps rather than substantive findings.",
    ],
    [
        "Literature",
        "Places the current and target sample sizes beside related ESG/NLP studies.",
        "Use this for thesis positioning, not as a strict requirement.",
        "n=720-1,000 is more credible for exploratory ESG NLP than n=272 alone.",
        "Large literature scales do not automatically make a study better if labels or provenance are weak.",
    ],
], columns=[
    "table_name",
    "what_it_does",
    "how_to_read_it",
    "if_yes_or_good",
    "if_underperforming",
])

PAGE_ANALYSIS_INVENTORY = pd.DataFrame([
    [
        "Parsed ESG sentence dashboards",
        "esg_dashboard_new_0_new.py; esg_dashboard_new_8_new.py",
        "Parsed JSON inspection, grounded markdown review, model comparison, and model coverage by PDF/page.",
        "RQ1, RQ2, RQ4, RQ5, RQ6",
        "Direct thesis evidence",
        "Defines the actual extracted-record population; use it to decide whether n is records, sentences, documents, runs, or model/prompt cells.",
    ],
    [
        "Aspect and ontology distribution dashboards",
        "esg_dashboard_new_Data Distribution.py; esg_dashboard_new_Data_New_Distribution.py; esg_dashboard_new_01_Aspects_Raw.py; esg_dashboard_new_02_Aspects_Clustered.py; esg_dashboard_new_03_Aspect_Comparison.py; zz_aspect_clusters.py",
        "Aspect distributions, raw-to-cluster mappings, ontology coverage, waterfall filtering, and unclustered aspect review.",
        "RQ2, RQ4, RQ5",
        "Direct thesis evidence",
        "Adds taxonomy cells to the sample-size problem: enough rows are needed per canonical aspect/pillar, not just in total.",
    ],
    [
        "Tone, sentiment, Sankey, and document distribution dashboards",
        "esg_dashboard_new_Tone_Distribution.py; esg_dashboard_new_Sankey.py; esg_dashboard_new_Distribution Document.py",
        "Tone balancing, sentiment/tone per document, Sankey flows, heatmaps, and document-level summaries.",
        "RQ2, RQ4, RQ6",
        "Direct thesis evidence",
        "Turns sample size into subgroup coverage: tone x language x pillar x document/prompt cells need enough observations.",
    ],
    [
        "ABSA metrics and ground-truth comparison",
        "absa_metrics_comparison.py; absa_metrics_comparison_mac.py; absa_metrics_comparison copy.py; absa_metrics_visualization.py; esg_dashboard_new_0_Metric_Analysis.py; test_models.py",
        "Ground truth vs prediction metrics, confusion matrices, TP/FP/FN, confidence/error views, and saved metrics JSON.",
        "RQ2, RQ3, RQ4, RQ6",
        "Direct thesis evidence",
        "F1/precision/recall require expert labels and aligned label spaces; low current scores argue for annotation expansion before strong evaluation claims.",
    ],
    [
        "ClimateBERT processing and result exploration",
        "0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth.py; 0_0_ClimateBERT_12_ClimateBERT_Batch_GroundTruth_Windows.py; 0_0_ClimateBERT_4_Model_Analysis.py; 0_0_ClimateBERT_5_Model_Deep_Explorer.py; 0_0_ClimateBERT_6_Model_Overview_All.py; 0_0_ClimateBERT_7_Full_Model_Visualization.py; 0_ClimateBERT_Commitment_Distribution.py; 1_ABSA_Integration.py",
        "Batch inference, coverage, confidence, label distributions, leaderboards, and ABSA-to-ClimateBERT integration.",
        "RQ3, RQ5, RQ6",
        "Direct thesis evidence",
        "Requires coverage across all valid sentences and matched comparison cells before agreement or kappa can be interpreted.",
    ],
    [
        "Interactive demos, prototypes, utilities, and scaffolding",
        "0_0_1_Single_Prediction.py; 0_0_1_multiple_Prediction.py; 0_0_2_Batch_Prediction.py; 0_0_3_Model_Explorer.py; esg_dashboard_new_Benchmark_Model.py; ABSA_Model_Comparison.py; 1_Analyze.py; 2_ABSA_Rule_Based.py; 3_ABSA_Classical.py; 5_ABSA_Deep_Learning.py; absa_ontology_3_deep_model.py; absa_ontology_all.py; absa_ontology_all_new_notes.py; scrambled_absa_mapping_baseline.py; scrambled_absa_mapping_baseline_mac.py; parse_documentation_json.py; _page_explanations.py; _shared/page_explanations.py; _shared/__init__.py; 0_0_0_1.py; 0_0_0_code.py",
        "Manual prediction demos, model prototypes, baselines, documentation helpers, and placeholder/support files.",
        "RQ5, RQ6 where outputs are saved; otherwise not directly RQ-bound",
        "Other / utility",
        "Do not count these as empirical sample-size evidence unless they produce saved records, predictions, or metrics tied to the thesis dataset.",
    ],
], columns=[
    "analysis_group",
    "pages",
    "what_the_existing_pages_do",
    "research_question_links",
    "evidence_role",
    "sample_size_implication",
])


def render_mermaid(code: str, height: int = 520) -> None:
    escaped_code = escape(code)
    html = f"""
    <div class="diagram-shell">
      <pre class="mermaid">{escaped_code}</pre>
      <div id="mermaid-error" class="diagram-error"></div>
    </div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.5/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: "loose",
        theme: "base",
        flowchart: {{
          htmlLabels: false,
          curve: "basis",
          padding: 18,
          useMaxWidth: true
        }},
        themeVariables: {{
          background: "#ffffff",
          mainBkg: "#f8fafc",
          primaryColor: "#f8fafc",
          primaryTextColor: "#111827",
          primaryBorderColor: "#64748b",
          lineColor: "#475569",
          clusterBkg: "#eef6f4",
          clusterBorder: "#0f766e",
          edgeLabelBackground: "#ffffff",
          textColor: "#111827",
          fontFamily: "Inter, Arial, sans-serif"
        }}
      }});
      try {{
        await mermaid.run({{ querySelector: ".mermaid" }});
        document.querySelectorAll(".diagram-shell svg").forEach((svg) => {{
          svg.style.width = "100%";
          svg.style.maxWidth = "100%";
          svg.style.height = "auto";
          svg.style.display = "block";
          svg.style.margin = "0 auto";
          svg.querySelectorAll("text").forEach((node) => {{
            node.style.fill = "#111827";
            node.style.fontWeight = "600";
          }});
        }});
      }} catch (err) {{
        const target = document.getElementById("mermaid-error");
        target.style.display = "block";
        target.textContent = "Mermaid render error: " + err.message;
      }}
    </script>
    <style>
      .diagram-shell {{
        background: #ffffff;
        border: 1px solid #d4dbe5;
        border-radius: 8px;
        min-height: {height}px;
        overflow: auto;
        padding: 18px;
      }}
      .diagram-shell .mermaid {{
        background: #ffffff;
        color: #111827;
        display: block;
        margin: 0;
        text-align: center;
      }}
      .diagram-shell svg {{
        background: #ffffff !important;
        width: 100% !important;
        max-width: 100% !important;
        height: auto;
      }}
      .diagram-error {{
        color: #991b1b;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        display: none;
        margin-top: 12px;
        padding: 12px;
        white-space: pre-wrap;
      }}
    </style>
    """
    components.html(html, height=height + 80, scrolling=True)


def mermaid_download_section(code: str, name: str = "mermaid_diagram") -> None:
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "mermaid_diagram"
    cols = st.columns(3)
    with cols[0]:
        st.download_button(
            "Download Mermaid source",
            data=code,
            file_name=f"{safe_name}.mmd",
            mime="text/plain",
            use_container_width=True,
        )
    with cols[1]:
        st.download_button(
            "Download Markdown block",
            data=f"```mermaid\n{code}\n```\n",
            file_name=f"{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with cols[2]:
        st.link_button(
            "Open Mermaid Live Editor",
            "https://mermaid.ai/live/edit",
            use_container_width=True,
        )


def mermaid_label(value: str, max_len: int = 70) -> str:
    clean = re.sub(r"\s+", " ", str(value)).strip()
    if len(clean) > max_len:
        clean = clean[: max_len - 3].rstrip() + "..."
    return clean.replace('"', "'")


def load_absa_metrics(path: Path, extra_path: Path | None = None) -> pd.DataFrame:
    paths = [path]
    if extra_path is not None and extra_path.exists() and extra_path != path:
        paths.append(extra_path)
    if not any(candidate.exists() for candidate in paths):
        return pd.DataFrame(columns=["model", "accuracy", "precision", "recall", "f1", "is_nonzero"])

    rows = []
    for metrics_path in paths:
        if not metrics_path.exists():
            continue
        with metrics_path.open("r") as f:
            results = json.load(f)
        for model, metrics in results.items():
            accuracy = float(metrics.get("accuracy", 0) or 0)
            precision = float(metrics.get("precision", 0) or 0)
            recall = float(metrics.get("recall", 0) or 0)
            f1 = float(metrics.get("f1", 0) or 0)
            rows.append({
                "model": model,
                "metric_source": metrics_path.name,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "is_nonzero": any(value > 0 for value in [accuracy, precision, recall, f1]),
            })
    return pd.DataFrame(rows).sort_values(["f1", "accuracy"], ascending=False)


def worst_case_moe(n: int) -> float:
    return 1.96 * (0.25 / n) ** 0.5 * 100


def claim_level_for_n(n: int) -> pd.Series:
    eligible = LADDER[LADDER["n"] <= n]
    if eligible.empty:
        return LADDER.iloc[0]
    return eligible.sort_values("n").iloc[-1]


def status_for_gap(required_n: int, current_n: int) -> str:
    if current_n >= required_n:
        return "Met"
    gap = required_n - current_n
    if gap <= max(50, required_n * 0.2):
        return "Near"
    return "Open"


def build_scenario_table(current_n: int, target_n: int) -> pd.DataFrame:
    rows = []
    for n in sorted(set(LADDER["n"].tolist() + [current_n, target_n])):
        claim = claim_level_for_n(n)
        rows.append({
            "n": n,
            "claim_level": claim["claim_level"],
            "status": claim["status"],
            "worst_case_moe_pp": round(worst_case_moe(n), 2),
            "gap_from_current": n - current_n,
            "records_to_target": max(target_n - n, 0),
        })
    return pd.DataFrame(rows).sort_values("n")


def build_subgroup_table(current_n: int, min_cell_n: int) -> pd.DataFrame:
    dynamic = SUBGROUPS.copy()
    dynamic["required_n"] = dynamic["required_n"].where(
        dynamic["subgroup_claim"] != "Pillar x language x tone",
        3 * 2 * 4 * min_cell_n,
    )
    dynamic["records_needed_from_current"] = (dynamic["required_n"] - current_n).clip(lower=0)
    dynamic["scenario_status"] = dynamic["required_n"].apply(lambda value: status_for_gap(int(value), current_n))
    return dynamic


def explain_ladder_row(row: pd.Series, current_n: int) -> dict[str, str]:
    n = int(row["n"])
    gap = n - current_n
    if gap <= 0:
        position = "This level is already reached by the current extracted-record count."
    else:
        position = f"This level needs {gap:,} additional records from the current scenario."

    return {
        "position": position,
        "valid_claim": row["interpretation"],
        "risk": "Do not use this level to imply gold-label accuracy, F1, or generalizable greenwashing rates unless the supporting annotation and subgroup design are also completed.",
        "next_action": "Expand records in the weakest design cells first: few-shot prompts, Social-pillar material, and matched prompt/document runs.",
    }


def build_claim_ladder_mermaid(current_n: int, target_n: int) -> str:
    rows = build_scenario_table(current_n, target_n)
    lines = [
        "flowchart LR",
        f'  Current["Current n={current_n:,}"]',
        f'  Target["Target n={target_n:,}"]',
    ]
    previous = "Current"
    for _, row in rows.iterrows():
        if row["n"] in [current_n, target_n]:
            continue
        node_id = f'N{int(row["n"])}'
        label = f'{int(row["n"]):,} - {mermaid_label(row["claim_level"], 42)}'
        lines.append(f'  {node_id}["{label}"]')
        lines.append(f"  {previous} --> {node_id}")
        previous = node_id
    lines.append(f"  {previous} --> Target")
    lines.extend([
        "  classDef current fill:#eef6ff,stroke:#2563eb,color:#111827,stroke-width:2px;",
        "  classDef target fill:#ecfdf5,stroke:#16a34a,color:#111827,stroke-width:2px;",
        "  classDef step fill:#f8fafc,stroke:#64748b,color:#111827;",
        "  class Current current;",
        "  class Target target;",
    ])
    step_nodes = [f'N{int(row["n"])}' for _, row in rows.iterrows() if row["n"] not in [current_n, target_n]]
    if step_nodes:
        lines.append(f"  class {','.join(step_nodes)} step;")
    return "\n".join(lines)


def build_sample_design_mermaid(min_cell_n: int) -> str:
    full_matrix_n = 3 * 2 * 4 * min_cell_n
    return f"""
flowchart TB
  Claim["Full bilingual ESG ABSA subgroup claim"]
  Pillar["3 ESG pillars"]
  Language["2 languages"]
  Tone["4 thesis tone classes"]
  Cell["minimum cell n={min_cell_n}"]
  Required["required records={full_matrix_n}"]
  Thesis["defensible subgroup interpretation"]

  Claim --> Pillar
  Claim --> Language
  Claim --> Tone
  Pillar --> Cell
  Language --> Cell
  Tone --> Cell
  Cell --> Required --> Thesis

  classDef claim fill:#f8fafc,stroke:#334155,color:#111827,stroke-width:2px;
  classDef design fill:#eef6ff,stroke:#2563eb,color:#111827;
  classDef target fill:#ecfdf5,stroke:#16a34a,color:#111827;
  class Claim claim;
  class Pillar,Language,Tone,Cell design;
  class Required,Thesis target;
""".strip()


def build_decision_mermaid(current_n: int, target_n: int) -> str:
    current_claim = mermaid_label(claim_level_for_n(current_n)["claim_level"])
    target_claim = mermaid_label(claim_level_for_n(target_n)["claim_level"])
    return f"""
flowchart LR
  Current["n={current_n:,}: {current_claim}"]
  Gap["targeted expansion"]
  Prompt["balance prompt templates"]
  Social["add Social-pillar records"]
  Match["match model x prompt x document cells"]
  Target["n={target_n:,}: {target_claim}"]
  Claim["stronger thesis claim"]

  Current --> Gap
  Gap --> Prompt
  Gap --> Social
  Gap --> Match
  Prompt --> Target
  Social --> Target
  Match --> Target
  Target --> Claim

  classDef current fill:#eef6ff,stroke:#2563eb,color:#111827,stroke-width:2px;
  classDef action fill:#fffbeb,stroke:#d97706,color:#111827;
  classDef target fill:#ecfdf5,stroke:#16a34a,color:#111827,stroke-width:2px;
  class Current current;
  class Gap,Prompt,Social,Match action;
  class Target,Claim target;
""".strip()


with st.sidebar:
    st.header("Scenario")
    current_n = st.number_input("Current records", min_value=1, value=272, step=10)
    target_n = st.number_input("Target records", min_value=1, value=720, step=10)
    min_cell_n = st.number_input("Minimum subgroup cell n", min_value=5, value=30, step=5)
    status_filter = st.multiselect(
        "Claim status",
        LADDER["status"].drop_duplicates().tolist(),
        default=LADDER["status"].drop_duplicates().tolist(),
    )
    view_mode = st.radio(
        "Detail view",
        ["Table", "Cards", "Detailed Explanation"],
        horizontal=False,
    )


remaining = max(target_n - current_n, 0)
current_claim = claim_level_for_n(current_n)
target_claim = claim_level_for_n(target_n)
absa_metrics_df = load_absa_metrics(ABSA_METRICS_PATH, LOCAL_ABSA_METRICS_PATH)
nonzero_absa_metrics = absa_metrics_df[absa_metrics_df["is_nonzero"]] if not absa_metrics_df.empty else absa_metrics_df

cols = st.columns(4)
cols[0].metric("Current n", f"{current_n:,}", current_claim["status"])
cols[1].metric("Target n", f"{target_n:,}", target_claim["status"])
cols[2].metric("Records to add", f"{remaining:,}")
cols[3].metric("Worst-case MoE now", f"+/-{worst_case_moe(current_n):.1f}pp")

st.caption(f"Source: `{SOURCE_HTML}`")
st.caption(f"ABSA metrics: `{ABSA_METRICS_PATH}`")
if LOCAL_ABSA_METRICS_PATH.exists():
    st.caption(f"Local rerun metrics: `{LOCAL_ABSA_METRICS_PATH}`")

tab_overview, tab_ladder, tab_moe, tab_power, tab_subgroups, tab_literature, tab_page_inventory, tab_absa_metrics, tab_mermaid, tab_guide, tab_verdict = st.tabs([
    "Overview",
    "Claim Ladder",
    "Margin of Error",
    "Power",
    "Subgroups",
    "Literature",
    "Existing Page Analyses",
    "ABSA Metrics",
    "Mermaid Preview",
    "Table Guide",
    "Verdict",
])

with tab_overview:
    scenario = build_scenario_table(current_n, target_n)
    st.subheader("Scenario Readiness")
    st.dataframe(scenario, use_container_width=True, height=360)
    st.bar_chart(scenario.set_index("n")[["worst_case_moe_pp"]])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Current defensible framing:** {current_claim['claim_level']}")
        st.write(current_claim["interpretation"])
    with c2:
        st.markdown(f"**Target defensible framing:** {target_claim['claim_level']}")
        st.write(target_claim["interpretation"])

with tab_ladder:
    ladder = LADDER[LADDER["status"].isin(status_filter)].copy()
    ladder["records_gap_from_current"] = ladder["n"] - current_n
    ladder["worst_case_moe_pp"] = ladder["n"].apply(lambda n: round(worst_case_moe(int(n)), 2))
    st.subheader("What Each Sample Size Supports")

    if view_mode == "Table":
        st.dataframe(ladder, use_container_width=True, height=420)
    elif view_mode == "Cards":
        for _, row in ladder.iterrows():
            st.subheader(f"{int(row['n']):,} records - {row['claim_level']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Status", row["status"])
            c2.metric("MoE", f"+/-{worst_case_moe(int(row['n'])):.1f}pp")
            c3.metric("Gap from current", f"{int(row['records_gap_from_current']):,}")
            st.write(row["interpretation"])
            st.divider()
    else:
        st.dataframe(ladder, use_container_width=True, height=260)

    if not ladder.empty:
        selected_n = st.selectbox(
            "Explain sample-size level",
            ladder["n"].tolist(),
            format_func=lambda value: f"{int(value):,} - {ladder[ladder['n'] == value].iloc[0]['claim_level']}",
        )
        row = ladder[ladder["n"] == selected_n].iloc[0]
        explanation = explain_ladder_row(row, current_n)
        e1, e2 = st.columns(2)
        with e1:
            st.markdown(f"**Position:** {explanation['position']}")
            st.markdown(f"**Valid claim:** {explanation['valid_claim']}")
        with e2:
            st.markdown(f"**Risk:** {explanation['risk']}")
            st.markdown(f"**Next action:** {explanation['next_action']}")

with tab_moe:
    st.subheader("Worst-Case Margin of Error")
    scenario_moe = worst_case_moe(current_n)
    target_moe = worst_case_moe(target_n)
    st.write(f"Current scenario MoE: **+/-{scenario_moe:.2f} percentage points**")
    st.write(f"Target scenario MoE: **+/-{target_moe:.2f} percentage points**")

    moe = MOE.copy()
    moe = pd.concat([
        moe,
        pd.DataFrame([
            [current_n, round(scenario_moe, 2), "Current scenario"],
            [target_n, round(target_moe, 2), "Target scenario"],
        ], columns=moe.columns),
    ]).drop_duplicates(subset=["n", "status"]).sort_values("n")
    st.line_chart(moe.set_index("n")["worst_case_moe_pp"])
    st.dataframe(moe, use_container_width=True)

with tab_power:
    st.subheader("Statistical Power Reference")
    test_filter = st.multiselect(
        "Power tests",
        POWER["test"].drop_duplicates().tolist(),
        default=POWER["test"].drop_duplicates().tolist(),
    )
    power = POWER[POWER["test"].isin(test_filter)]
    st.dataframe(power, use_container_width=True)
    pivot = power.pivot(index="sample_condition", columns="test", values="power").fillna(0)
    st.bar_chart(pivot)

    st.info(
        "Interpretation: the bilingual outcome-rate comparison is already reasonably powered at n=272, "
        "but prompt comparison needs at least about 40 records per template to become acceptable."
    )

with tab_subgroups:
    st.subheader("Subgroup Requirements")
    dynamic = build_subgroup_table(current_n, min_cell_n)
    st.dataframe(dynamic, use_container_width=True)
    st.bar_chart(dynamic.set_index("subgroup_claim")[["required_n", "records_needed_from_current"]])

    full_matrix_n = 3 * 2 * 4 * min_cell_n
    st.info(
        f"With minimum cell n={min_cell_n}, the pillar x language x tone full matrix requires "
        f"**{full_matrix_n:,} records**."
    )

with tab_literature:
    st.subheader("Scale Compared With Related Work")
    literature = LITERATURE.sort_values("scale", ascending=False)
    st.dataframe(literature, use_container_width=True)
    st.bar_chart(literature.set_index("study")["scale"])

with tab_page_inventory:
    st.subheader("Existing Page Analyses and Sample-Size Implications")
    st.write(
        "This section summarizes the existing code in `pages/` and separates pages that create "
        "thesis evidence from demos, prototypes, helper pages, and baselines. Only pages that "
        "produce saved records, predictions, or metrics should be counted as empirical sample-size evidence."
    )
    page_inventory = PAGE_ANALYSIS_INVENTORY.copy()
    role_filter = st.multiselect(
        "Evidence role",
        page_inventory["evidence_role"].drop_duplicates().tolist(),
        default=page_inventory["evidence_role"].drop_duplicates().tolist(),
    )
    if role_filter:
        page_inventory = page_inventory[page_inventory["evidence_role"].isin(role_filter)]
    st.dataframe(page_inventory, use_container_width=True, height=440)

    if not page_inventory.empty:
        role_counts = page_inventory["evidence_role"].value_counts()
        st.bar_chart(role_counts)
        selected_group = st.selectbox("Explain analysis group", page_inventory["analysis_group"].tolist())
        selected = page_inventory[page_inventory["analysis_group"] == selected_group].iloc[0]
        st.markdown(f"**Pages:** {selected['pages']}")
        st.markdown(f"**RQ links:** {selected['research_question_links']}")
        st.markdown(f"**Sample-size implication:** {selected['sample_size_implication']}")

with tab_absa_metrics:
    st.subheader("Evaluation Metrics and Sample-Size Implications")
    if absa_metrics_df.empty:
        st.warning(f"No ABSA metrics JSON found at `{ABSA_METRICS_PATH}`.")
    else:
        best = absa_metrics_df.iloc[0]
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Evaluated outputs", len(absa_metrics_df))
        a2.metric("Non-zero outputs", len(nonzero_absa_metrics))
        a3.metric("Best F1", f"{best['f1']:.4f}", best["model"])
        a4.metric("Zero-output models", len(absa_metrics_df) - len(nonzero_absa_metrics))

        st.write(
            "These metrics come from `absa_metrics_visualization.py`. They show that the current "
            "ABSA/ClimateBERT label comparison is mostly a label-alignment and evaluation-design issue. "
            "That strengthens the recommendation to add expert annotations before reporting F1 as a thesis result."
        )
        st.dataframe(absa_metrics_df, use_container_width=True, height=420)
        st.bar_chart(absa_metrics_df.set_index("model")[["accuracy", "precision", "recall", "f1"]])

        if not nonzero_absa_metrics.empty:
            st.subheader("Non-zero Results")
            st.dataframe(nonzero_absa_metrics, use_container_width=True)

with tab_mermaid:
    st.subheader("Claim Ladder Diagram")
    ladder_code = build_claim_ladder_mermaid(current_n, target_n)
    render_mermaid(ladder_code, height=430)
    mermaid_download_section(ladder_code, "sample_size_claim_ladder")
    st.code(ladder_code, language="mermaid")

    st.subheader("Subgroup Design Diagram")
    design_code = build_sample_design_mermaid(min_cell_n)
    render_mermaid(design_code, height=430)
    mermaid_download_section(design_code, "sample_design_matrix")
    st.code(design_code, language="mermaid")

    st.subheader("Targeted Expansion Decision Flow")
    decision_code = build_decision_mermaid(current_n, target_n)
    render_mermaid(decision_code, height=430)
    mermaid_download_section(decision_code, "sample_size_decision_tree")
    st.code(decision_code, language="mermaid")

with tab_guide:
    st.subheader("How to Interpret the Tables")
    st.dataframe(TABLE_GUIDE, use_container_width=True, height=360)
    selected_table = st.selectbox("Detailed guide", TABLE_GUIDE["table_name"].tolist())
    guide_row = TABLE_GUIDE[TABLE_GUIDE["table_name"] == selected_table].iloc[0]
    st.markdown(f"**What it does:** {guide_row['what_it_does']}")
    st.markdown(f"**How to read it:** {guide_row['how_to_read_it']}")
    st.markdown(f"**If yes / good:** {guide_row['if_yes_or_good']}")
    st.markdown(f"**If underperforming:** {guide_row['if_underperforming']}")

with tab_verdict:
    st.subheader("Thesis Interpretation")
    st.write(
        "n=272 is defensible for a pipeline feasibility prototype, but it should be framed as "
        "a feasibility study rather than a generalizable ESG ABSA benchmark."
    )
    st.write(
        "A practical master's-thesis target is n=720-1,000. n=720 supports the full bilingual "
        "pillar x language x tone matrix, while n=1,000 makes the study more comparable with "
        "published exploratory ESG NLP work."
    )
    st.write(
        "The most efficient fix is targeted expansion: add records where the design is weakest, "
        "especially few-shot prompts, S-pillar material, and documents needed for greenwashing-index reliability."
    )
