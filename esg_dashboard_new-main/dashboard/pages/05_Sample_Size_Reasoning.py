from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Sample Size Reasoning", layout="wide")
st.title("Sample Size Reasoning")
st.caption("Interactive thesis sample-size reasoning for ESG ABSA claims.")


SOURCE_HTML = Path(__file__).resolve().parent / "sample_size_reasoning.html"


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


with st.sidebar:
    st.header("Scenario")
    current_n = st.number_input("Current records", min_value=1, value=272, step=10)
    target_n = st.number_input("Target records", min_value=1, value=720, step=10)
    min_cell_n = st.number_input("Minimum subgroup cell n", min_value=5, value=30, step=5)


remaining = max(target_n - current_n, 0)
cols = st.columns(4)
cols[0].metric("Current n", f"{current_n:,}")
cols[1].metric("Target n", f"{target_n:,}")
cols[2].metric("Records to add", f"{remaining:,}")
cols[3].metric("Worst-case MoE now", f"{(1.96 * (0.25 / current_n) ** 0.5 * 100):.1f}pp")

tab_ladder, tab_moe, tab_power, tab_subgroups, tab_literature, tab_verdict = st.tabs([
    "Claim Ladder",
    "Margin of Error",
    "Power",
    "Subgroups",
    "Literature",
    "Verdict",
])

with tab_ladder:
    st.subheader("What Each Sample Size Supports")
    ladder = LADDER.copy()
    ladder["records_gap_from_current"] = ladder["n"] - current_n
    st.dataframe(ladder, use_container_width=True)
    chart_df = ladder.set_index("claim_level")[["n"]]
    st.bar_chart(chart_df)

with tab_moe:
    st.subheader("Worst-Case Margin of Error")
    moe = MOE.copy()
    scenario_moe = 1.96 * (0.25 / current_n) ** 0.5 * 100
    target_moe = 1.96 * (0.25 / target_n) ** 0.5 * 100
    st.write(f"Current scenario MoE: **+/-{scenario_moe:.2f} percentage points**")
    st.write(f"Target scenario MoE: **+/-{target_moe:.2f} percentage points**")
    st.line_chart(moe.set_index("n")["worst_case_moe_pp"])
    st.dataframe(moe, use_container_width=True)

with tab_power:
    st.subheader("Statistical Power Reference")
    st.dataframe(POWER, use_container_width=True)
    pivot = POWER.pivot(index="sample_condition", columns="test", values="power").fillna(0)
    st.bar_chart(pivot)

with tab_subgroups:
    st.subheader("Subgroup Requirements")
    dynamic = SUBGROUPS.copy()
    dynamic["met_by_current"] = dynamic["required_n"] <= current_n
    dynamic["records_needed_from_current"] = (dynamic["required_n"] - current_n).clip(lower=0)
    st.dataframe(dynamic, use_container_width=True)
    st.bar_chart(dynamic.set_index("subgroup_claim")[["required_n"]])

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
    st.caption(f"Source: `{SOURCE_HTML}`")
