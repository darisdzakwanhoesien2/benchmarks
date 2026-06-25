from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="ESG Flow Sankey", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
SILVER_PATH = ROOT / "results" / "revision_analysis" / "silver_tone_ground_truth.csv"


def load_data():
    if not SILVER_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(SILVER_PATH).fillna("missing")


def sankey(df, cols, value_col="count", title="Sankey"):
    if df.empty:
        st.info("No data for Sankey.")
        return
    flows = df.groupby(cols).size().reset_index(name=value_col)
    labels = []
    label_to_idx = {}

    def node(label):
        if label not in label_to_idx:
            label_to_idx[label] = len(labels)
            labels.append(label)
        return label_to_idx[label]

    sources, targets, values = [], [], []
    for _, row in flows.iterrows():
        for i in range(len(cols) - 1):
            src = f"{cols[i]}: {row[cols[i]]}"
            tgt = f"{cols[i+1]}: {row[cols[i+1]]}"
            sources.append(node(src))
            targets.append(node(tgt))
            values.append(row[value_col])

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(label=labels, pad=16, thickness=16),
                link=dict(source=sources, target=targets, value=values),
            )
        ]
    )
    fig.update_layout(title_text=title, height=650, font_size=11)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(flows.sort_values(value_col, ascending=False), use_container_width=True, height=320)


st.title("ESG Flow Sankey")
st.caption("Visual flow analysis adapted from the legacy Sankey dashboard: company/source, ESG pillar, aspect, tone, prompt, and review issues.")

df = load_data()
if df.empty:
    st.error(f"Missing {SILVER_PATH}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    companies = sorted(df["company"].unique().tolist())
    selected_companies = st.multiselect("Company/source", companies, default=companies)
    tones = sorted(df["tone_pred"].unique().tolist())
    selected_tones = st.multiselect("Tone", tones, default=tones)
    min_records = st.slider("Minimum company/source records", 1, 30, 1)

counts = df["company"].value_counts()
eligible_companies = counts[counts >= min_records].index
view = df[df["company"].isin(selected_companies) & df["company"].isin(eligible_companies) & df["tone_pred"].isin(selected_tones)].copy()
view["review_issue"] = view.apply(
    lambda r: "schema_drift" if bool(r.get("schema_drift")) else ("needs_review" if bool(r.get("needs_human_review")) else "clean"),
    axis=1,
)

tabs = st.tabs(["Company → ESG → Tone", "ESG → Aspect → Tone", "Prompt → Tone → Issue", "Raw Flow Data"])

with tabs[0]:
    sankey(view, ["company", "esg", "tone_pred"], title="Company/Source → ESG Pillar → Tone")

with tabs[1]:
    top_aspects = view["aspect"].value_counts().head(20).index
    sankey(view[view["aspect"].isin(top_aspects)], ["esg", "aspect", "tone_pred"], title="ESG Pillar → Aspect → Tone")

with tabs[2]:
    sankey(view, ["prompt", "tone_pred", "review_issue"], title="Prompt → Tone → Review Issue")

with tabs[3]:
    st.dataframe(view, use_container_width=True, height=620)
    st.download_button("Download filtered Sankey data", view.to_csv(index=False).encode("utf-8"), "esg_flow_sankey_data.csv", "text/csv")
