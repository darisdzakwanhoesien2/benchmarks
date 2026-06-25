from __future__ import annotations

import math
from pathlib import Path
import sys
from typing import Callable

import altair as alt
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from dataset_phase_utils import add_pdf_metadata  # noqa: E402
from dataset_phase_utils import phase_view  # noqa: E402

WORKFLOW = ROOT / "results" / "thesis_workflow_dashboard"
REVISION = ROOT / "results" / "revision_analysis"

TONE_ORDER = ["commitment", "action", "outcome", "none", "missing"]
PILLAR_ORDER = ["e", "s", "g", "none", "missing"]


def clean(value: object, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip().replace("\xa0", " ")
    return text if text else default


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def load_workflow_csv(name: str) -> pd.DataFrame:
    return load_csv(WORKFLOW / name)


def info_if_empty(df: pd.DataFrame, message: str = "No data available.") -> bool:
    if df.empty:
        st.info(message)
        return True
    return False


def chart_title(text: str, caption: str, sources: str | list[str] | None = None, note: str | None = None) -> None:
    st.subheader(text)
    st.caption(caption)
    if sources:
        paths = [sources] if isinstance(sources, str) else sources
        st.caption("Source data: " + " | ".join(f"`{path}`" for path in paths))
    if note:
        st.caption(note)


def parse_label_list(value: object) -> list[str]:
    text = clean(value)
    if not text:
        return []
    stripped = text.strip("[]")
    parts = []
    for raw in stripped.split(","):
        token = raw.strip().strip("'").strip('"')
        if token:
            parts.append(token)
    return parts


def normalize_provider(model_name: str) -> str:
    text = clean(model_name, "missing")
    if "/" in text:
        return text.split("/", 1)[0]
    return text.split(":", 1)[0]


def enrich_tone_records(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    plot = df.copy()
    if "target" not in plot.columns and "target_doc" in plot.columns:
        plot["target"] = plot["target_doc"].astype(str) + "_pdf"
    plot = add_pdf_metadata(plot, "target")
    plot["tone"] = plot.get("tone", "").map(lambda v: clean(v, "missing"))
    plot["aspect"] = plot.get("aspect", "").map(lambda v: clean(v, "missing"))
    plot["esg"] = plot.get("esg", "").map(lambda v: clean(v, "missing"))
    plot["text"] = plot.get("text", "").map(clean)
    plot["text_len_words"] = plot["text"].map(lambda v: len(v.split()))
    plot["ticker_sector"] = plot.get("ticker_sector", "").map(lambda v: clean(v, "Unmapped"))
    plot["report_year"] = plot.get("report_year", "").map(lambda v: clean(v, "Unknown"))
    plot["document_type"] = plot.get("original_file", "").map(infer_document_type)
    plot["record_key"] = (
        plot.get("target_doc", "").astype(str)
        + "::"
        + plot["text"].astype(str)
        + "::"
        + plot.get("aspect", "").astype(str)
        + "::"
        + plot.get("tone", "").astype(str)
    )
    return plot


def infer_document_type(value: object) -> str:
    text = clean(value).lower()
    if "annual" in text or re_search_any(text, ["_ar_", " annual ", "annual-report", "annual_and_sustainable"]):
        return "Annual / financial filing"
    if "sustain" in text or "keberlanjutan" in text or "-sr" in text or "_sr_" in text:
        return "Sustainability report"
    return "Other report"


def re_search_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def status_stacked_bar(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `ocr_processing_summary.csv`."):
        return
    plot = df.copy()
    plot["status"] = plot["status"].map(lambda v: clean(v, "missing"))
    counts = plot.groupby("status").size().reset_index(name="files")
    counts["stage"] = "Source + OCR preparation"
    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("stage:N", title=None),
            y=alt.Y("files:Q", title="Files"),
            color=alt.Color("status:N", title="Status", scale=alt.Scale(scheme="tableau20")),
            tooltip=["status", "files"],
            order=alt.Order("files:Q", sort="descending"),
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def page_count_distribution(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `ocr_processing_summary.csv`."):
        return
    plot = df.copy()
    plot["pages"] = pd.to_numeric(plot.get("pages"), errors="coerce")
    plot = plot.dropna(subset=["pages"])
    if info_if_empty(plot, "No usable `pages` values found."):
        return
    chart = (
        alt.Chart(plot)
        .mark_bar(color="#2f6f73")
        .encode(
            x=alt.X("pages:Q", bin=alt.Bin(maxbins=20), title="Page count"),
            y=alt.Y("count():Q", title="Reports"),
            tooltip=[alt.Tooltip("count():Q", title="Reports")],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def top_aspects_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `tone_records_flat.csv`."):
        return
    plot = df.copy()
    plot["aspect"] = plot["aspect"].map(lambda v: clean(v, "missing"))
    counts = plot.groupby("aspect").size().reset_index(name="records").sort_values("records", ascending=False).head(20)
    chart = (
        alt.Chart(counts)
        .mark_bar(color="#0f766e")
        .encode(
            x=alt.X("records:Q", title="Records"),
            y=alt.Y("aspect:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320)),
            tooltip=["aspect", "records"],
        )
        .properties(height=560)
    )
    st.altair_chart(chart, use_container_width=True)


def pillar_tone_heatmap(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `tone_esg_crosstab.csv`."):
        return
    row_col = "tone"
    if row_col not in df.columns:
        st.info("Expected a `tone` column in `tone_esg_crosstab.csv`.")
        return
    melted = df.melt(id_vars=[row_col], var_name="pillar", value_name="count")
    melted["count"] = pd.to_numeric(melted["count"], errors="coerce").fillna(0)
    melted["tone"] = pd.Categorical(melted["tone"], categories=TONE_ORDER, ordered=True)
    melted["pillar"] = pd.Categorical(melted["pillar"], categories=PILLAR_ORDER, ordered=True)
    chart = alt.Chart(melted).mark_rect().encode(
        x=alt.X("tone:N", title="Tone"),
        y=alt.Y("pillar:N", title="ESG Pillar"),
        color=alt.Color("count:Q", title="Records", scale=alt.Scale(scheme="tealblues")),
        tooltip=["pillar", "tone", "count"],
    )
    text = alt.Chart(melted).mark_text(fontSize=12).encode(
        x="tone:N",
        y="pillar:N",
        text=alt.Text("count:Q", format=".0f"),
        color=alt.condition(alt.datum.count > float(melted["count"].max()) * 0.55, alt.value("white"), alt.value("#111827")),
    )
    st.altair_chart((chart + text).properties(height=320), use_container_width=True)


def tone_donut(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `tone_records_flat.csv`."):
        return
    plot = df.copy()
    plot["tone"] = plot["tone"].map(lambda v: clean(v, "missing"))
    counts = plot.groupby("tone").size().reset_index(name="records").sort_values("records", ascending=False)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["tone"],
                values=counts["records"],
                hole=0.56,
                textinfo="label+percent",
                hovertemplate="%{label}: %{value} records (%{percent})<extra></extra>",
            )
        ]
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def agreement_bar_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `climatebert_proxy_agreement_summary.csv`."):
        return
    row = df.iloc[0]
    metrics = pd.DataFrame(
        [
            {"metric": "Accuracy / Percent Agreement", "value": pd.to_numeric(row.get("percent_agreement"), errors="coerce")},
            {"metric": "F1 Proxy (Cohen's Kappa)", "value": pd.to_numeric(row.get("cohen_kappa"), errors="coerce")},
        ]
    ).dropna()
    chart = (
        alt.Chart(metrics)
        .mark_bar(color="#395b91")
        .encode(
            x=alt.X("metric:N", title=None),
            y=alt.Y("value:Q", title="Score", scale=alt.Scale(domain=[0, 1])),
            tooltip=["metric", alt.Tooltip("value:Q", format=".3f")],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def sankey_label_mapping(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `tone_climatebert_label_crosstab.csv`."):
        return
    if "tone" not in df.columns:
        st.info("Expected a `tone` column in `tone_climatebert_label_crosstab.csv`.")
        return
    melted = df.melt(id_vars=["tone"], var_name="climatebert_label", value_name="count")
    melted["count"] = pd.to_numeric(melted["count"], errors="coerce").fillna(0)
    melted = melted[melted["count"] > 0].copy()
    if info_if_empty(melted, "No non-zero label mappings available."):
        return
    melted = melted.sort_values("count", ascending=False).reset_index(drop=True)

    left_nodes = [f"LLM Tone: {tone}" for tone in melted["tone"].astype(str).unique()]
    right_nodes = [f"ClimateBERT: {label}" for label in melted["climatebert_label"].astype(str).unique()]
    labels = left_nodes + right_nodes
    index = {label: idx for idx, label in enumerate(labels)}

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=18,
                    thickness=18,
                    line=dict(color="rgba(30,41,59,0.35)", width=0.5),
                    label=labels,
                    color=["#2f6f73"] * len(left_nodes) + ["#64748b"] * len(right_nodes),
                ),
                link=dict(
                    source=[index[f"LLM Tone: {row.tone}"] for row in melted.itertuples()],
                    target=[index[f"ClimateBERT: {row.climatebert_label}"] for row in melted.itertuples()],
                    value=melted["count"].tolist(),
                    color=["rgba(47,111,115,0.28)"] * len(melted),
                    customdata=[
                        [row.tone, row.climatebert_label, int(row.count)]
                        for row in melted.itertuples()
                    ],
                    hovertemplate=(
                        "LLM Tone: %{customdata[0]}<br>"
                        "ClimateBERT: %{customdata[1]}<br>"
                        "Records: %{customdata[2]}<extra></extra>"
                    ),
                ),
            )
        ]
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Hover over each flow to see the exact record count.")
    st.dataframe(
        melted.rename(
            columns={
                "tone": "llm_tone",
                "climatebert_label": "climatebert_label",
                "count": "records",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def pareto_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `failure_mode_counts.csv`."):
        return
    plot = df.copy()
    plot["mode"] = plot["mode"].map(lambda v: clean(v, "missing"))
    plot["count"] = pd.to_numeric(plot["count"], errors="coerce").fillna(0)
    plot = plot.groupby("mode", as_index=False)["count"].sum().sort_values("count", ascending=False)
    if info_if_empty(plot, "No failure counts available."):
        return
    plot["cumulative_pct"] = plot["count"].cumsum() / plot["count"].sum()

    bars = alt.Chart(plot).mark_bar(color="#b45309").encode(
        x=alt.X("mode:N", sort=None, title=None, axis=alt.Axis(labelAngle=-30, labelLimit=220)),
        y=alt.Y("count:Q", title="Failure count"),
        tooltip=["mode", "count", alt.Tooltip("cumulative_pct:Q", format=".1%")],
    )
    line = alt.Chart(plot).mark_line(color="#1d4ed8", point=True).encode(
        x=alt.X("mode:N", sort=None),
        y=alt.Y("cumulative_pct:Q", title="Cumulative share", axis=alt.Axis(format="%")),
    )
    rule = alt.Chart(pd.DataFrame({"threshold": [0.8]})).mark_rule(color="#dc2626", strokeDash=[6, 4]).encode(y="threshold:Q")

    st.altair_chart(alt.layer(bars, line, rule).resolve_scale(y="independent").properties(height=420), use_container_width=True)


def standards_venn(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `ontology_coverage.csv`."):
        return
    plot = df.copy()
    plot["records"] = pd.to_numeric(plot.get("records"), errors="coerce").fillna(0)
    plot["suggested_path"] = plot.get("suggested_path", "").astype(str)
    plot["has_gri"] = plot["suggested_path"].str.contains(r"\bGRI\b", case=False, na=False)
    plot["has_sasb"] = plot["suggested_path"].str.contains(r"\bSASB\b", case=False, na=False)

    gri_only = int(plot.loc[plot["has_gri"] & ~plot["has_sasb"], "records"].sum())
    sasb_only = int(plot.loc[plot["has_sasb"] & ~plot["has_gri"], "records"].sum())
    overlap = int(plot.loc[plot["has_gri"] & plot["has_sasb"], "records"].sum())
    unique_local = int(plot.loc[~plot["has_gri"] & ~plot["has_sasb"], "records"].sum())

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.add_patch(Circle((0.43, 0.5), 0.24, color="#0f766e", alpha=0.38))
    ax.add_patch(Circle((0.60, 0.5), 0.24, color="#1d4ed8", alpha=0.32))
    ax.text(0.32, 0.78, "GRI", fontsize=14, weight="bold", ha="center")
    ax.text(0.71, 0.78, "SASB", fontsize=14, weight="bold", ha="center")
    ax.text(0.30, 0.50, f"{gri_only}", fontsize=20, ha="center", va="center")
    ax.text(0.515, 0.50, f"{overlap}", fontsize=20, ha="center", va="center")
    ax.text(0.73, 0.50, f"{sasb_only}", fontsize=20, ha="center", va="center")
    ax.text(0.86, 0.18, f"Unique Indonesian\nvocabulary: {unique_local}", fontsize=12, ha="center", va="center")
    ax.set_xlim(0.05, 0.98)
    ax.set_ylim(0.05, 0.95)
    ax.axis("off")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.dataframe(
        pd.DataFrame(
            [
                {"segment": "GRI only", "records": gri_only},
                {"segment": "GRI and SASB", "records": overlap},
                {"segment": "SASB only", "records": sasb_only},
                {"segment": "Outside GRI/SASB", "records": unique_local},
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )


def provider_success_line(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `model_stability_summary.csv`."):
        return
    plot = df.copy()
    plot["json_parse_success_rate"] = pd.to_numeric(plot.get("json_parse_success_rate"), errors="coerce")
    plot["runs"] = pd.to_numeric(plot.get("runs"), errors="coerce").fillna(0)
    plot["provider"] = plot["model"].map(normalize_provider)
    plot = plot.dropna(subset=["json_parse_success_rate"])
    if info_if_empty(plot, "No parse success values available."):
        return
    provider_df = (
        plot.groupby("provider", as_index=False)
        .agg(success_rate=("json_parse_success_rate", "mean"), runs=("runs", "sum"))
        .sort_values("success_rate", ascending=False)
    )
    chart = (
        alt.Chart(provider_df)
        .mark_line(point=True, strokeWidth=3, color="#0f766e")
        .encode(
            x=alt.X("provider:N", sort="-y", title="Model provider"),
            y=alt.Y("success_rate:Q", title="Success Rate %", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            tooltip=["provider", alt.Tooltip("success_rate:Q", format=".1%"), "runs"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)
    st.dataframe(
        plot[["model", "provider", "runs", "json_parse_success_rate", "avg_records", "missing_tone_rate", "schema_drift_rate"]]
        .sort_values(["provider", "json_parse_success_rate"], ascending=[True, False]),
        use_container_width=True,
        hide_index=True,
    )


def prompt_variance_boxplot(summary_df: pd.DataFrame, run_df: pd.DataFrame) -> None:
    source = "prompt_stability_summary.csv"
    if not run_df.empty and {"prompt", "record_count"}.issubset(run_df.columns):
        plot = run_df.copy()
        plot["record_count"] = pd.to_numeric(plot["record_count"], errors="coerce")
        plot = plot.dropna(subset=["record_count"])
        if not plot.empty:
            chart = (
                alt.Chart(plot)
                .mark_boxplot(extent="min-max", color="#395b91")
                .encode(
                    x=alt.X("prompt:N", title="Prompt template", axis=alt.Axis(labelAngle=-30, labelLimit=260)),
                    y=alt.Y("record_count:Q", title="Records extracted"),
                    tooltip=["prompt", "record_count", "model", "company"],
                )
                .properties(height=420)
            )
            st.altair_chart(chart, use_container_width=True)
            st.caption("Box plot built from per-run prompt records in `results/revision_analysis/prompt_stability_by_run.csv` because `prompt_stability_summary.csv` is already aggregated.")
            return

    if info_if_empty(summary_df, f"Missing `{source}`."):
        return
    fallback = summary_df.copy()
    fallback["avg_records"] = pd.to_numeric(fallback.get("avg_records"), errors="coerce")
    chart = (
        alt.Chart(fallback)
        .mark_bar(color="#395b91")
        .encode(
            x=alt.X("prompt:N", title="Prompt template", axis=alt.Axis(labelAngle=-30, labelLimit=260)),
            y=alt.Y("avg_records:Q", title="Average records extracted"),
            tooltip=["prompt", "runs", "avg_records", "json_parse_success_rate", "field_completion_rate"],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption("Fallback view: only aggregated prompt stability data was available, so the page shows average extracted records instead of a true variance box plot.")


def sectoral_pillar_split(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for sector analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[
        deduped["ticker_sector"].ne("Unmapped")
        & deduped["esg"].isin(["e", "s", "g"])
    ].copy()
    if info_if_empty(deduped, "No sector-mapped ESG records available."):
        return
    top_sectors = deduped["ticker_sector"].value_counts().head(6).index.tolist()
    plot = deduped[deduped["ticker_sector"].isin(top_sectors)].copy()
    chart = (
        alt.Chart(plot)
        .mark_bar()
        .encode(
            x=alt.X("count():Q", title="Records"),
            y=alt.Y("ticker_sector:N", title="Industry", sort="-x"),
            color=alt.Color("esg:N", title="ESG Pillar", scale=alt.Scale(domain=["e", "s", "g"], range=["#0f766e", "#c97b2a", "#395b91"])),
            column=alt.Column("tone:N", title="Tone"),
            tooltip=["ticker_sector", "tone", "esg", alt.Tooltip("count():Q", title="Records")],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def greenwashing_gap_scatter(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `greenwashing_index_by_company.csv`."):
        return
    plot = df.copy()
    for col in ["commitment", "outcome", "greenwashing_index", "records"]:
        plot[col] = pd.to_numeric(plot.get(col), errors="coerce").fillna(0)
    chart = (
        alt.Chart(plot)
        .mark_circle(opacity=0.8, stroke="#1f2937", strokeWidth=0.5)
        .encode(
            x=alt.X("outcome:Q", title="Achievement / Outcome Count"),
            y=alt.Y("commitment:Q", title="Commitment Count"),
            size=alt.Size("records:Q", title="Records"),
            color=alt.Color("greenwashing_index:Q", title="PRGS / Gap Score", scale=alt.Scale(scheme="orangered")),
            tooltip=["company", "records", "commitment", "outcome", alt.Tooltip("greenwashing_index:Q", format=".3f")],
        )
        .properties(height=420)
    )
    diagonal = alt.Chart(
        pd.DataFrame(
            [
                {"x": 0, "y": 0},
                {"x": float(plot["outcome"].max()), "y": float(plot["outcome"].max())},
            ]
        )
    ).mark_line(color="#64748b", strokeDash=[6, 4]).encode(x="x:Q", y="y:Q")
    st.altair_chart(chart + diagonal, use_container_width=True)


def temporal_topic_bump(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for temporal analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[
        deduped["report_year"].str.fullmatch(r"(19|20)\d{2}")
        & deduped["aspect"].ne("missing")
        & deduped["aspect"].ne("none")
    ].copy()
    if info_if_empty(deduped, "No year-resolved aspect records available."):
        return
    counts = (
        deduped.groupby(["report_year", "aspect"], as_index=False)
        .size()
        .rename(columns={"size": "records"})
    )
    top_aspects = counts.groupby("aspect", as_index=False)["records"].sum().sort_values("records", ascending=False).head(8)["aspect"].tolist()
    counts = counts[counts["aspect"].isin(top_aspects)].copy()
    counts["rank"] = counts.groupby("report_year")["records"].rank(method="dense", ascending=False)
    chart = (
        alt.Chart(counts)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("report_year:O", title="Report Year"),
            y=alt.Y("rank:Q", title="Topic Rank", scale=alt.Scale(reverse=True)),
            color=alt.Color("aspect:N", title="Aspect"),
            tooltip=["report_year", "aspect", "records", "rank"],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)


def information_density_boxplot(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for information-density analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[(deduped["text_len_words"] > 0) & deduped["tone"].isin(TONE_ORDER)].copy()
    if info_if_empty(deduped, "No usable record text lengths available."):
        return
    chart = (
        alt.Chart(deduped)
        .mark_boxplot(extent="min-max", color="#2f6f73")
        .encode(
            x=alt.X("tone:N", title="Tone", sort=TONE_ORDER),
            y=alt.Y("text_len_words:Q", title="Word Count per Record"),
            tooltip=["tone", "target_doc", "aspect", "text_len_words"],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)


def aspect_cooccurrence_network(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for co-occurrence analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    edges: dict[tuple[str, str], int] = {}
    for row in deduped.itertuples():
        primary = clean(row.aspect, "missing")
        label_nodes = [label for label in parse_label_list(getattr(row, "labels", "")) if label and label != primary]
        nodes = [primary] + label_nodes[:4]
        unique_nodes = [node for idx, node in enumerate(nodes) if node and node not in nodes[:idx]]
        if len(unique_nodes) < 2:
            continue
        for i in range(len(unique_nodes)):
            for j in range(i + 1, len(unique_nodes)):
                edge = tuple(sorted((unique_nodes[i], unique_nodes[j])))
                edges[edge] = edges.get(edge, 0) + 1
    if not edges:
        st.info("No multi-label aspect co-occurrence edges could be derived from the current record structure.")
        return
    edge_df = (
        pd.DataFrame(
            [{"source": src, "target": tgt, "weight": weight} for (src, tgt), weight in edges.items()]
        )
        .sort_values("weight", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    nodes = pd.unique(edge_df[["source", "target"]].values.ravel("K")).tolist()
    node_index = {node: idx for idx, node in enumerate(nodes)}
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=18,
                    thickness=18,
                    label=nodes,
                    color=["#2f6f73"] * len(nodes),
                ),
                link=dict(
                    source=edge_df["source"].map(node_index).tolist(),
                    target=edge_df["target"].map(node_index).tolist(),
                    value=edge_df["weight"].tolist(),
                    color=["rgba(47,111,115,0.24)"] * len(edge_df),
                    hovertemplate=(
                        "%{source.label} ↔ %{target.label}<br>"
                        "Co-occurrence weight: %{value}<extra></extra>"
                    ),
                ),
            )
        ]
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Current artifact limitation: each flat record stores one primary aspect, so this network approximates semantic co-occurrence by linking the primary aspect to additional labels extracted in the same record.")
    st.dataframe(edge_df, use_container_width=True, hide_index=True)


def esg_pillar_distribution(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for ESG pillar distribution."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[deduped["esg"].isin(["e", "s", "g"])].copy()
    counts = deduped.groupby("esg", as_index=False).size().rename(columns={"size": "records"})
    fig = go.Figure(
        data=[go.Pie(labels=counts["esg"], values=counts["records"], hole=0.45, textinfo="label+percent")]
    )
    fig.update_layout(height=360, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def sector_composition(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No metadata-enriched records available for sector composition."):
        return
    docs = df[["original_file", "ticker_sector"]].drop_duplicates().copy()
    docs["ticker_sector"] = docs["ticker_sector"].replace("", "Unmapped")
    counts = docs.groupby("ticker_sector", as_index=False).size().rename(columns={"size": "documents"}).sort_values("documents", ascending=False)
    chart = (
        alt.Chart(counts)
        .mark_bar(color="#395b91")
        .encode(
            x=alt.X("documents:Q", title="Documents"),
            y=alt.Y("ticker_sector:N", sort="-x", title="Industry"),
            tooltip=["ticker_sector", "documents"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def record_token_distribution(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for token distribution."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    chart = (
        alt.Chart(deduped)
        .mark_bar(color="#0f766e")
        .encode(
            x=alt.X("text_len_words:Q", bin=alt.Bin(maxbins=25), title="Words per extracted record"),
            y=alt.Y("count():Q", title="Records"),
            tooltip=[alt.Tooltip("count():Q", title="Records")],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def binary_commitment_confusion(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `climatebert_proxy_agreement_records.csv`."):
        return
    plot = df.copy()
    plot["llm_commitment"] = plot["tone_pred"].astype(str).str.strip().str.lower().eq("commitment")
    plot["climate_commitment"] = plot["has_climate_commitment"].astype(str).str.strip().str.lower().eq("true")
    matrix = (
        plot.groupby(["llm_commitment", "climate_commitment"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    matrix["llm_commitment"] = matrix["llm_commitment"].map({True: "LLM: commitment", False: "LLM: non-commitment"})
    matrix["climate_commitment"] = matrix["climate_commitment"].map({True: "ClimateBERT: commitment", False: "ClimateBERT: non-commitment"})
    base = alt.Chart(matrix).mark_rect().encode(
        x=alt.X("climate_commitment:N", title=None),
        y=alt.Y("llm_commitment:N", title=None),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=["llm_commitment", "climate_commitment", "count"],
    )
    text = alt.Chart(matrix).mark_text(fontSize=13).encode(
        x="climate_commitment:N",
        y="llm_commitment:N",
        text="count:Q",
        color=alt.condition(alt.datum.count > float(matrix["count"].max()) * 0.55, alt.value("white"), alt.value("#111827")),
    )
    st.altair_chart((base + text).properties(height=220), use_container_width=True)


def ablation_prompt_trends(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `prompt_stability_summary.csv`."):
        return
    plot = df.copy()
    plot["avg_records"] = pd.to_numeric(plot.get("avg_records"), errors="coerce").fillna(0)
    plot["json_parse_success_rate"] = pd.to_numeric(plot.get("json_parse_success_rate"), errors="coerce").fillna(0)
    plot["prompt_family"] = plot["prompt"].astype(str).str.replace(".md", "", regex=False)
    melted = plot.melt(
        id_vars=["prompt_family"],
        value_vars=["avg_records", "json_parse_success_rate", "field_completion_rate"],
        var_name="metric",
        value_name="value",
    )
    melted["value"] = pd.to_numeric(melted["value"], errors="coerce").fillna(0)
    chart = (
        alt.Chart(melted)
        .mark_bar()
        .encode(
            x=alt.X("prompt_family:N", title="Prompt strategy", axis=alt.Axis(labelAngle=-30, labelLimit=240)),
            y=alt.Y("value:Q", title="Value"),
            color=alt.Color("metric:N", title="Metric"),
            column=alt.Column("metric:N", title=None),
            tooltip=["prompt_family", "metric", "value"],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def sentiment_by_pillar(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for sentiment analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[deduped["esg"].isin(["e", "s", "g"])].copy()
    deduped["sentiment"] = deduped.get("sentiment", "").map(lambda v: clean(v, "missing"))
    chart = (
        alt.Chart(deduped)
        .mark_bar()
        .encode(
            x=alt.X("count():Q", stack="normalize", title="Share of sentiment"),
            y=alt.Y("esg:N", title="ESG Pillar", sort=["e", "s", "g"]),
            color=alt.Color("sentiment:N", title="Sentiment"),
            tooltip=["esg", "sentiment", alt.Tooltip("count():Q", title="Records")],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def aspect_action_linkage(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for aspect-action linkage."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    top_aspects = deduped["aspect"].value_counts().head(10).index.tolist()
    plot = deduped[deduped["aspect"].isin(top_aspects) & deduped["tone"].isin(["commitment", "action", "outcome"])].copy()
    flow = plot.groupby(["aspect", "tone"], as_index=False).size().rename(columns={"size": "count"})
    left_nodes = [f"Aspect: {v}" for v in flow["aspect"].unique()]
    right_nodes = [f"Disclosure: {v}" for v in ["commitment", "action", "outcome"] if v in flow["tone"].unique()]
    labels = left_nodes + right_nodes
    idx = {label: i for i, label in enumerate(labels)}
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(label=labels, pad=18, thickness=18, color=["#2f6f73"] * len(left_nodes) + ["#64748b"] * len(right_nodes)),
                link=dict(
                    source=[idx[f"Aspect: {row.aspect}"] for row in flow.itertuples()],
                    target=[idx[f"Disclosure: {row.tone}"] for row in flow.itertuples()],
                    value=flow["count"].tolist(),
                    color=["rgba(47,111,115,0.25)"] * len(flow),
                    hovertemplate="%{source.label}<br>%{target.label}<br>Records: %{value}<extra></extra>",
                ),
            )
        ]
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def error_distribution_pie(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `failure_mode_counts.csv`."):
        return
    plot = df.copy()
    plot["count"] = pd.to_numeric(plot.get("count"), errors="coerce").fillna(0)
    grouped = plot.groupby("mode", as_index=False)["count"].sum().sort_values("count", ascending=False)
    fig = go.Figure(data=[go.Pie(labels=grouped["mode"], values=grouped["count"], textinfo="label+percent")])
    fig.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def agreement_availability_note(df: pd.DataFrame) -> None:
    annotator_count = int(df.get("annotator", pd.Series(dtype=str)).astype(str).str.strip().replace("", pd.NA).dropna().nunique()) if not df.empty else 0
    reviewed = int(df.get("review_status", pd.Series(dtype=str)).astype(str).str.strip().replace("", pd.NA).dropna().shape[0]) if not df.empty else 0
    st.info(
        f"Inter-annotator agreement heatmap is not implementable from the current artifacts. "
        f"`pilot_ground_truth_annotations.csv` has {annotator_count} populated annotator IDs and {reviewed} non-empty review-status rows, so there is no multi-annotator matrix to compare yet."
    )


def cost_performance_note() -> None:
    st.info(
        "Inference cost vs performance trade-off is not implementable from the current result artifacts because no per-model cost table or stable latency benchmark is stored alongside the evaluation summary."
    )


def _macro_prf(df: pd.DataFrame, truth_col: str, pred_col: str) -> tuple[float, float, float, float]:
    labels = sorted(set(df[truth_col].astype(str)).union(set(df[pred_col].astype(str))))
    labels = [label for label in labels if clean(label)]
    if not labels:
        return 0.0, 0.0, 0.0, 0.0
    precision_scores = []
    recall_scores = []
    f1_scores = []
    total = len(df)
    correct = int((df[truth_col].astype(str) == df[pred_col].astype(str)).sum())
    for label in labels:
        truth = df[truth_col].astype(str) == label
        pred = df[pred_col].astype(str) == label
        tp = int((truth & pred).sum())
        fp = int((~truth & pred).sum())
        fn = int((truth & ~pred).sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        precision_scores.append(precision)
        recall_scores.append(recall)
        f1_scores.append(f1)
    return (
        correct / total if total else 0.0,
        sum(precision_scores) / len(precision_scores),
        sum(recall_scores) / len(recall_scores),
        sum(f1_scores) / len(f1_scores),
    )


def prompt_strategy_bar(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing silver ground-truth records for prompt strategy analysis."):
        return
    plot = df.copy()
    plot = plot[
        plot["silver_tone_ground_truth"].astype(str).str.strip().ne("")
        & plot["tone_pred"].astype(str).str.strip().ne("")
        & plot["prompt"].astype(str).str.strip().ne("")
    ].copy()
    if info_if_empty(plot, "No prompt rows contain both prediction and silver ground truth."):
        return
    rows = []
    for prompt, subset in plot.groupby("prompt"):
        acc, prec, rec, f1 = _macro_prf(subset, "silver_tone_ground_truth", "tone_pred")
        rows.extend(
            [
                {"prompt": prompt, "metric": "accuracy", "value": acc},
                {"prompt": prompt, "metric": "precision", "value": prec},
                {"prompt": prompt, "metric": "recall", "value": rec},
                {"prompt": prompt, "metric": "f1", "value": f1},
            ]
        )
    metric_df = pd.DataFrame(rows)
    chart = (
        alt.Chart(metric_df)
        .mark_bar()
        .encode(
            x=alt.X("prompt:N", title="Prompt strategy", axis=alt.Axis(labelAngle=-30, labelLimit=260)),
            y=alt.Y("value:Q", title="Score", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("metric:N", title="Metric"),
            column=alt.Column("metric:N", title=None),
            tooltip=["prompt", "metric", alt.Tooltip("value:Q", format=".3f")],
        )
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def token_window_accuracy(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing silver ground-truth records for token-window analysis."):
        return
    plot = df.copy()
    plot = plot[
        plot["silver_tone_ground_truth"].astype(str).str.strip().ne("")
        & plot["tone_pred"].astype(str).str.strip().ne("")
    ].copy()
    if info_if_empty(plot, "No labeled rows available for accuracy-by-length analysis."):
        return
    plot["text_len_words"] = pd.to_numeric(plot.get("text_len_words"), errors="coerce")
    plot = plot.dropna(subset=["text_len_words"])
    if plot.empty:
        st.info("No text length values available.")
        return
    plot["length_bin"] = pd.cut(plot["text_len_words"], bins=[0, 20, 40, 60, 100, 200, 1000], include_lowest=True)
    plot["correct"] = plot["tone_pred"].astype(str) == plot["silver_tone_ground_truth"].astype(str)
    summary = (
        plot.groupby("length_bin", observed=False)
        .agg(avg_words=("text_len_words", "mean"), accuracy=("correct", "mean"), records=("correct", "size"))
        .reset_index()
    )
    summary = summary[summary["records"] > 0].copy()
    chart = (
        alt.Chart(summary)
        .mark_line(point=True, strokeWidth=3, color="#395b91")
        .encode(
            x=alt.X("avg_words:Q", title="Average words in record-length bin"),
            y=alt.Y("accuracy:Q", title="Accuracy", scale=alt.Scale(domain=[0, 1])),
            tooltip=["length_bin", alt.Tooltip("avg_words:Q", format=".1f"), alt.Tooltip("accuracy:Q", format=".1%"), "records"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def aspect_action_sentiment_sankey(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for aspect-action-sentiment analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[
        deduped["aspect"].ne("missing")
        & deduped["aspect"].ne("none")
        & deduped["tone"].isin(["commitment", "action", "outcome"])
        & deduped["sentiment"].astype(str).str.strip().ne("")
    ].copy()
    top_aspects = deduped["aspect"].value_counts().head(8).index.tolist()
    deduped = deduped[deduped["aspect"].isin(top_aspects)].copy()
    flow = deduped.groupby(["aspect", "tone", "sentiment"], as_index=False).size().rename(columns={"size": "count"})
    aspect_nodes = [f"Aspect: {v}" for v in flow["aspect"].unique()]
    tone_nodes = [f"Action Mode: {v}" for v in flow["tone"].unique()]
    sentiment_nodes = [f"Sentiment: {v}" for v in flow["sentiment"].unique()]
    labels = aspect_nodes + tone_nodes + sentiment_nodes
    idx = {label: i for i, label in enumerate(labels)}
    left_links = (
        flow.groupby(["aspect", "tone"], as_index=False)["count"].sum()
    )
    right_links = (
        flow.groupby(["tone", "sentiment"], as_index=False)["count"].sum()
    )
    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(label=labels, pad=16, thickness=18),
                link=dict(
                    source=[idx[f"Aspect: {row.aspect}"] for row in left_links.itertuples()] + [idx[f"Action Mode: {row.tone}"] for row in right_links.itertuples()],
                    target=[idx[f"Action Mode: {row.tone}"] for row in left_links.itertuples()] + [idx[f"Sentiment: {row.sentiment}"] for row in right_links.itertuples()],
                    value=left_links["count"].tolist() + right_links["count"].tolist(),
                    color=["rgba(47,111,115,0.25)"] * (len(left_links) + len(right_links)),
                    hovertemplate="%{source.label}<br>%{target.label}<br>Records: %{value}<extra></extra>",
                ),
            )
        ]
    )
    fig.update_layout(height=560, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def sentiment_density_plot(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for sentiment density analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped["sentiment_score"] = pd.to_numeric(deduped.get("sentiment_score"), errors="coerce")
    deduped = deduped.dropna(subset=["sentiment_score"])
    deduped = deduped[deduped["tone"].isin(["commitment", "action", "outcome", "none"])]
    if info_if_empty(deduped, "No numeric sentiment scores available."):
        return
    chart = (
        alt.Chart(deduped)
        .transform_density(
            density="sentiment_score",
            groupby=["tone"],
            as_=["sentiment_score", "density"],
        )
        .mark_area(opacity=0.35)
        .encode(
            x=alt.X("sentiment_score:Q", title="Sentiment score"),
            y=alt.Y("density:Q", title="Density"),
            color=alt.Color("tone:N", title="Tone"),
            tooltip=["tone", alt.Tooltip("sentiment_score:Q", format=".2f"), alt.Tooltip("density:Q", format=".3f")],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def error_taxonomy_sunburst(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `failure_modes.csv`."):
        return
    category_map = {
        "missing_tone": "Classification Error",
        "schema_drift": "Extraction Error",
        "hedged_or_modal_language": "Language Ambiguity",
        "passive_voice": "Language Ambiguity",
        "bilingual_or_code_switched": "Input Noise",
        "regulatory_or_indonesian_domain_terms": "Domain Terminology",
    }
    rows = []
    for raw in df.get("failure_modes", pd.Series(dtype=str)).astype(str):
        labels = [item.strip() for item in raw.split("|") if item.strip()]
        for label in labels:
            rows.append({"category": category_map.get(label, "Other"), "subtype": label, "count": 1})
    tax = pd.DataFrame(rows)
    if info_if_empty(tax, "No failure-mode taxonomy rows available."):
        return
    grouped = tax.groupby(["category", "subtype"], as_index=False)["count"].sum()
    fig = go.Figure(
        go.Sunburst(
            labels=grouped["subtype"].tolist() + grouped["category"].drop_duplicates().tolist(),
            parents=grouped["category"].tolist() + [""] * grouped["category"].nunique(),
            values=grouped["count"].tolist() + grouped.groupby("category")["count"].sum().tolist(),
            branchvalues="total",
        )
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


def confidence_calibration_plot(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing silver ground-truth records for calibration analysis."):
        return
    plot = df.copy()
    plot = plot[
        plot["silver_tone_ground_truth"].astype(str).str.strip().ne("")
        & plot["tone_pred"].astype(str).str.strip().ne("")
    ].copy()
    plot["sentiment_score"] = pd.to_numeric(plot.get("sentiment_score"), errors="coerce").fillna(0)
    plot["confidence_proxy"] = plot["sentiment_score"].abs().clip(0, 1)
    plot["correct"] = plot["tone_pred"].astype(str) == plot["silver_tone_ground_truth"].astype(str)
    plot["conf_bin"] = pd.cut(plot["confidence_proxy"], bins=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], include_lowest=True)
    summary = (
        plot.groupby("conf_bin", observed=False)
        .agg(confidence=("confidence_proxy", "mean"), accuracy=("correct", "mean"), records=("correct", "size"))
        .reset_index()
    )
    summary = summary[summary["records"] > 0].copy()
    bars = alt.Chart(summary).mark_bar(color="#c97b2a", opacity=0.6).encode(
        x=alt.X("confidence:Q", title="Confidence proxy (|sentiment_score|)"),
        y=alt.Y("accuracy:Q", title="Observed accuracy", scale=alt.Scale(domain=[0, 1])),
        tooltip=["conf_bin", alt.Tooltip("confidence:Q", format=".2f"), alt.Tooltip("accuracy:Q", format=".2f"), "records"],
    )
    line = alt.Chart(summary).mark_line(color="#1d4ed8", point=True).encode(
        x=alt.X("confidence:Q"),
        y=alt.Y("confidence:Q"),
    )
    st.altair_chart((bars + line).properties(height=360), use_container_width=True)


def model_cost_accuracy_pareto() -> None:
    try:
        view = phase_view()
    except Exception as exc:
        st.info(f"Could not load runtime phase view for cost/performance trade-off: {exc}")
        return
    if view.empty:
        st.info("No phase-view rows available for runtime trade-off analysis.")
        return
    plot = view.copy()
    for col in ["success_event_seconds", "text_len_words"]:
        if col in plot.columns:
            plot[col] = pd.to_numeric(plot[col], errors="coerce")
    if "silver_tone_ground_truth" not in plot.columns or "tone_pred" not in plot.columns:
        st.info("Phase-view rows do not contain the required prediction and ground-truth columns.")
        return
    plot = plot[
        plot["silver_tone_ground_truth"].astype(str).str.strip().ne("")
        & plot["tone_pred"].astype(str).str.strip().ne("")
        & plot["model"].astype(str).str.strip().ne("")
    ].copy()
    if plot.empty:
        st.info("No labeled model rows available for the trade-off frontier.")
        return
    plot["correct"] = plot["tone_pred"].astype(str) == plot["silver_tone_ground_truth"].astype(str)
    summary = (
        plot.groupby("model", as_index=False)
        .agg(
            accuracy=("correct", "mean"),
            avg_seconds=("success_event_seconds", "mean"),
            records=("correct", "size"),
        )
    )
    summary["avg_seconds"] = summary["avg_seconds"].fillna(0)
    chart = (
        alt.Chart(summary)
        .mark_circle(size=140, opacity=0.85)
        .encode(
            x=alt.X("avg_seconds:Q", title="Average processing seconds per event"),
            y=alt.Y("accuracy:Q", title="Accuracy", scale=alt.Scale(domain=[0, 1])),
            size=alt.Size("records:Q", title="Labeled records"),
            color=alt.Color("model:N", legend=None),
            tooltip=["model", alt.Tooltip("avg_seconds:Q", format=".2f"), alt.Tooltip("accuracy:Q", format=".2%"), "records"],
        )
        .properties(height=420)
    )
    text = alt.Chart(summary).mark_text(dx=8, dy=-8, align="left", fontSize=11).encode(
        x="avg_seconds:Q",
        y="accuracy:Q",
        text="model:N",
    )
    st.altair_chart(chart + text, use_container_width=True)


def sector_absa_heatmap(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for sectoral ABSA heatmap."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    deduped = deduped[deduped["ticker_sector"].ne("Unmapped") & deduped["aspect"].ne("missing") & deduped["aspect"].ne("none")].copy()
    top_sectors = deduped["ticker_sector"].value_counts().head(6).index.tolist()
    top_aspects = deduped["aspect"].value_counts().head(8).index.tolist()
    plot = deduped[deduped["ticker_sector"].isin(top_sectors) & deduped["aspect"].isin(top_aspects)].copy()
    counts = plot.groupby(["ticker_sector", "aspect"], as_index=False).size().rename(columns={"size": "count"})
    base = alt.Chart(counts).mark_rect().encode(
        x=alt.X("aspect:N", title="ABSA dimension / aspect", axis=alt.Axis(labelAngle=-30, labelLimit=220)),
        y=alt.Y("ticker_sector:N", title="Industry"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=["ticker_sector", "aspect", "count"],
    )
    text = alt.Chart(counts).mark_text(fontSize=11).encode(
        x="aspect:N",
        y="ticker_sector:N",
        text="count:Q",
        color=alt.condition(alt.datum.count > float(counts["count"].max()) * 0.55, alt.value("white"), alt.value("#111827")),
    )
    st.altair_chart((base + text).properties(height=320), use_container_width=True)


def thesis_overview_funnel(ocr_df: pd.DataFrame, artifact_df: pd.DataFrame, tone_df: pd.DataFrame) -> None:
    source_docs = int(len(ocr_df))
    artifacts = int(len(artifact_df))
    llm_jobs = 156
    successful_runs = 110
    structured_records = int(len(tone_df))
    plot = pd.DataFrame(
        [
            {"stage": "Source reports", "count": source_docs},
            {"stage": "Documented LLM jobs", "count": llm_jobs},
            {"stage": "Successful extraction runs", "count": successful_runs},
            {"stage": "Structured ESG records", "count": structured_records},
            {"stage": "Research artifacts", "count": artifacts},
        ]
    )
    chart = (
        alt.Chart(plot)
        .mark_bar(color="#2f6f73")
        .encode(
            x=alt.X("count:Q", title="Count"),
            y=alt.Y("stage:N", sort=None, title=None),
            tooltip=["stage", "count"],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)


def bilingual_context_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No silver-dataset rows available for language analysis."):
        return
    plot = df.copy()
    plot["language"] = plot.get("language", "").map(lambda v: clean(v, "unknown"))
    counts = plot.groupby("language", as_index=False).size().rename(columns={"size": "records"}).sort_values("records", ascending=False)
    chart = (
        alt.Chart(counts)
        .mark_bar(color="#395b91")
        .encode(
            x=alt.X("records:Q", title="Labeled records"),
            y=alt.Y("language:N", title="Language"),
            tooltip=["language", "records"],
        )
        .properties(height=220)
    )
    st.altair_chart(chart, use_container_width=True)


def model_tradeoff_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `model_stability_summary.csv`."):
        return
    plot = df.copy()
    for col in ["json_parse_success_rate", "avg_records", "runs"]:
        plot[col] = pd.to_numeric(plot.get(col), errors="coerce").fillna(0)
    chart = (
        alt.Chart(plot)
        .mark_circle(size=180, opacity=0.85)
        .encode(
            x=alt.X("json_parse_success_rate:Q", title="Parse success rate", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("avg_records:Q", title="Average records per run"),
            size=alt.Size("runs:Q", title="Runs"),
            color=alt.Color("model:N", legend=None),
            tooltip=["model", alt.Tooltip("json_parse_success_rate:Q", format=".3f"), alt.Tooltip("avg_records:Q", format=".2f"), "runs"],
        )
        .properties(height=360)
    )
    labels = alt.Chart(plot).mark_text(dx=8, dy=-8, align="left", fontSize=11).encode(
        x="json_parse_success_rate:Q",
        y="avg_records:Q",
        text="model:N",
    )
    st.altair_chart(chart + labels, use_container_width=True)


def commitment_outcome_ratio_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for tone-ratio analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    counts = deduped["tone"].value_counts().rename_axis("tone").reset_index(name="records")
    counts["share"] = counts["records"] / counts["records"].sum()
    chart = (
        alt.Chart(counts)
        .mark_bar(color="#0f766e")
        .encode(
            x=alt.X("tone:N", title="Tone", sort=TONE_ORDER),
            y=alt.Y("share:Q", title="Share of records", axis=alt.Axis(format="%")),
            tooltip=["tone", "records", alt.Tooltip("share:Q", format=".1%")],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)
    commitment = float(counts.loc[counts["tone"].eq("commitment"), "share"].iloc[0]) if (counts["tone"] == "commitment").any() else 0.0
    outcome = float(counts.loc[counts["tone"].eq("outcome"), "share"].iloc[0]) if (counts["tone"] == "outcome").any() else 0.0
    ratio = (commitment / outcome) if outcome else 0.0
    st.caption(f"Observed commitment share: {commitment:.1%}; outcome share: {outcome:.1%}; ratio: {ratio:.2f}:1.")


def silver_dataset_overview(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `silver_tone_ground_truth.csv`."):
        return
    rows = [
        {"metric": "Silver dataset rows", "value": len(df)},
        {"metric": "Unique models", "value": df.get("model", pd.Series(dtype=str)).astype(str).nunique()},
        {"metric": "Unique prompts", "value": df.get("prompt", pd.Series(dtype=str)).astype(str).nunique()},
        {"metric": "Rows with silver tone", "value": int(df.get("silver_tone_ground_truth", pd.Series(dtype=str)).astype(str).str.strip().ne("").sum())},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def human_llm_agreement_summary(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `silver_tone_ground_truth.csv`."):
        return
    plot = df.copy()
    plot = plot[
        plot["silver_tone_ground_truth"].astype(str).str.strip().ne("")
        & plot["tone_pred"].astype(str).str.strip().ne("")
    ].copy()
    if info_if_empty(plot, "No silver-vs-prediction rows available."):
        return
    acc, prec, rec, f1 = _macro_prf(plot, "silver_tone_ground_truth", "tone_pred")
    metrics = pd.DataFrame(
        [
            {"metric": "Accuracy", "value": acc},
            {"metric": "Precision", "value": prec},
            {"metric": "Recall", "value": rec},
            {"metric": "F1", "value": f1},
            {"metric": "Reported tone kappa claim", "value": 0.788},
        ]
    )
    chart = (
        alt.Chart(metrics)
        .mark_bar(color="#395b91")
        .encode(
            x=alt.X("metric:N", title=None, axis=alt.Axis(labelAngle=-25, labelLimit=220)),
            y=alt.Y("value:Q", title="Score", scale=alt.Scale(domain=[0, 1])),
            tooltip=["metric", alt.Tooltip("value:Q", format=".3f")],
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption("The `0.788` value is rendered as the thesis-reported human-vs-LLM tone kappa claim; the other bars are directly recomputed from the silver dataset rows present in this repo.")


def climatebert_divergence_summary() -> None:
    metrics = pd.DataFrame(
        [
            {"metric": "Proxy kappa (stored summary)", "value": 0.645},
            {"metric": "Real kappa claim", "value": 0.079},
        ]
    )
    chart = (
        alt.Chart(metrics)
        .mark_bar(color="#b45309")
        .encode(
            x=alt.X("metric:N", title=None),
            y=alt.Y("value:Q", title="Kappa", scale=alt.Scale(domain=[0, 1])),
            tooltip=["metric", alt.Tooltip("value:Q", format=".3f")],
        )
        .properties(height=260)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption("The `0.645` proxy kappa is backed by `climatebert_proxy_agreement_summary.csv`. The `0.079` real-kappa claim appears in the thesis narrative and related batch-import artifacts, but not as a single finalized summary CSV in the current workflow bundle.")


def ontology_novelty_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "Missing `ontology_novel_aspect_review.csv`."):
        return
    plot = df.copy()
    placeholders = {"missing", "none", "unknown", "e", "s", "g", "general", "social", "environmental", "environmental-claims", "disclosure", "strategy", "business"}
    plot["is_placeholder"] = plot["aspect"].astype(str).str.lower().isin(placeholders)
    plot["has_path"] = plot.get("ontology_path", "").astype(str).str.strip().ne("")
    plot["bucket"] = plot.apply(
        lambda row: "Placeholder / review artifact"
        if row["is_placeholder"]
        else ("Mapped / canonicalized" if row["has_path"] else "Novel / unresolved"),
        axis=1,
    )
    counts = plot.groupby("bucket", as_index=False).size().rename(columns={"size": "aspects"})
    chart = (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("bucket:N", title=None),
            y=alt.Y("aspects:Q", title="Aspect count"),
            color=alt.Color("bucket:N", legend=None),
            tooltip=["bucket", "aspects"],
        )
        .properties(height=260)
    )
    st.altair_chart(chart, use_container_width=True)


def publication_gaps_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "gap": "Real F1 / precision / recall benchmark tables per model/prompt",
                "current status": "Proxy bars exist; no finalized per-model gold benchmark artifact",
                "needed artifact": "evaluation_summary_by_model_prompt.csv",
                "candidate sources": "results/revision_analysis/silver_tone_ground_truth.csv + ground-truth label tables",
            },
            {
                "gap": "Explicit token-window metadata per run",
                "current status": "Only text-length proxy available",
                "needed artifact": "prompt_runtime_window_audit.csv",
                "candidate sources": "background job configs / prompt execution logs",
            },
            {
                "gap": "Calibrated model confidence outputs",
                "current status": "Only sentiment_score proxy available",
                "needed artifact": "prediction_confidence_summary.csv",
                "candidate sources": "LLM raw outputs or classifier probabilities",
            },
            {
                "gap": "Actual cost or token-usage logs",
                "current status": "Runtime seconds proxy available; no monetary cost table",
                "needed artifact": "model_cost_usage_log.csv",
                "candidate sources": "provider billing exports / token accounting middleware",
            },
            {
                "gap": "Multi-annotator IDs for true inter-annotator agreement",
                "current status": "Annotations exist but annotator column is empty",
                "needed artifact": "human_annotation_rounds.csv",
                "candidate sources": "results/revision_analysis/pilot_ground_truth_annotations.csv",
            },
            {
                "gap": "Paragraph-level multi-aspect structure",
                "current status": "Only single primary aspect per flat record",
                "needed artifact": "paragraph_aspect_spans.jsonl",
                "candidate sources": "page-level Markdown + extraction schema extension",
            },
        ]
    )


SOFT_VERBS = {
    "aim",
    "aimed",
    "commit",
    "committed",
    "consider",
    "considered",
    "continue",
    "continued",
    "explore",
    "exploring",
    "intend",
    "intends",
    "plan",
    "planned",
    "planning",
    "seek",
    "seeks",
    "support",
    "supports",
    "will",
    "target",
    "targets",
    "berkomitmen",
    "komitmen",
    "mendukung",
    "akan",
    "rencana",
    "menjajaki",
    "eksplorasi",
}

CONCRETE_VERBS = {
    "achieved",
    "built",
    "completed",
    "decreased",
    "implemented",
    "installed",
    "measured",
    "reduced",
    "reported",
    "retained",
    "signed",
    "tested",
    "trained",
    "adopted",
    "menurunkan",
    "menerapkan",
    "mengurangi",
    "menandatangani",
    "membangun",
    "melakukan",
    "mencapai",
    "mengadopsi",
    "uji",
}


def vagueness_score(text: str) -> tuple[float, int, int]:
    tokens = [token.strip(".,;:!?()[]{}\"'").lower() for token in clean(text).split()]
    tokens = [token for token in tokens if token]
    soft = sum(1 for token in tokens if token in SOFT_VERBS)
    concrete = sum(1 for token in tokens if token in CONCRETE_VERBS)
    total = soft + concrete
    if total == 0:
        return 0.5, soft, concrete
    return soft / total, soft, concrete


def add_vagueness(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    plot = df.copy()
    scores = plot["text"].map(vagueness_score)
    plot["vagueness_score"] = scores.map(lambda v: v[0])
    plot["soft_verb_hits"] = scores.map(lambda v: v[1])
    plot["concrete_verb_hits"] = scores.map(lambda v: v[2])
    return plot


def soft_language_ratio_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for vagueness analysis."):
        return
    deduped = add_vagueness(df.drop_duplicates("record_key")).copy()
    deduped = deduped[deduped["tone"].isin(["commitment", "action", "outcome"])].copy()
    chart = (
        alt.Chart(deduped)
        .mark_boxplot(extent="min-max", color="#b45309")
        .encode(
            x=alt.X("tone:N", title="Tone"),
            y=alt.Y("vagueness_score:Q", title="Vagueness score (soft / [soft + concrete])", scale=alt.Scale(domain=[0, 1])),
            tooltip=["tone", "target_doc", "aspect", "vagueness_score", "soft_verb_hits", "concrete_verb_hits"],
        )
        .properties(height=360)
    )
    st.altair_chart(chart, use_container_width=True)


def cross_document_discrepancy_matrix(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No enriched records available for cross-document consistency analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    paired = deduped[deduped["document_type"].isin(["Annual / financial filing", "Sustainability report"])].copy()
    if paired.empty:
        st.info("No paired annual-vs-sustainability records are available in the current extracted corpus.")
        return
    group_cols = ["company_name", "report_year", "document_type", "tone"]
    counts = paired.groupby(group_cols, as_index=False).size().rename(columns={"size": "records"})
    pivot = counts.pivot_table(index=["company_name", "report_year", "tone"], columns="document_type", values="records", fill_value=0).reset_index()
    if "Sustainability report" not in pivot.columns or "Annual / financial filing" not in pivot.columns:
        st.info("The current corpus does not include enough paired document types per company-year to form a discrepancy matrix.")
        return
    pivot["gap"] = pivot["Sustainability report"] - pivot["Annual / financial filing"]
    pivot["pair"] = pivot["company_name"].astype(str) + " (" + pivot["report_year"].astype(str) + ")"
    view = pivot[["pair", "tone", "gap"]].copy()
    if view.empty:
        st.info("No paired company-year discrepancy rows available.")
        return
    base = alt.Chart(view).mark_rect().encode(
        x=alt.X("tone:N", title="Tone"),
        y=alt.Y("pair:N", title="Company-year pair"),
        color=alt.Color("gap:Q", title="Sustainability - Financial gap", scale=alt.Scale(scheme="redblue")),
        tooltip=["pair", "tone", "gap"],
    )
    text = alt.Chart(view).mark_text(fontSize=11).encode(
        x="tone:N",
        y="pair:N",
        text="gap:Q",
        color=alt.condition("abs(datum.gap) > 2", alt.value("white"), alt.value("#111827")),
    )
    st.altair_chart((base + text).properties(height=300), use_container_width=True)
    st.caption("Positive gaps mean the sustainability report contains more of that tone than the paired annual/financial filing for the same inferred company-year.")


def regulatory_alignment_proxy_chart(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for regulatory-alignment analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    corpus = (
        deduped.get("text", "").astype(str)
        + " "
        + deduped.get("aspect", "").astype(str)
        + " "
        + deduped.get("labels", "").astype(str)
    ).str.lower()
    proxy_rows = []
    dimensions = {
        "governance": ["board", "governance", "komite", "dewan", "ethic", "anti-korupsi", "anti bribery"],
        "strategy": ["strategy", "strategi", "roadmap", "komitmen", "target", "rencana"],
        "risk management": ["risk", "risiko", "mitigasi", "resilience", "ketahanan"],
        "metrics & targets": ["scope", "emission", "emisi", "kpi", "metric", "target", "%", "ton", "mwh", "gj"],
    }
    frameworks = {
        "POJK 51 proxy": ["pojk", "ojk", "seojk", "keuangan berkelanjutan"],
        "IFRS S1/S2 proxy": ["ifrs", "issb", "s1", "s2", "sasb", "tcfd", "climate", "iklim"],
    }
    for framework, markers in frameworks.items():
        framework_mask = corpus.map(lambda text: any(marker in text for marker in markers))
        subset = deduped[framework_mask].copy()
        if subset.empty:
            continue
        subset_text = corpus[framework_mask]
        for dimension, keywords in dimensions.items():
            hits = int(subset_text.map(lambda text: any(keyword in text for keyword in keywords)).sum())
            proxy_rows.append({"framework": framework, "dimension": dimension, "records": hits})
    plot = pd.DataFrame(proxy_rows)
    if info_if_empty(plot, "No framework-reference proxy rows could be derived from the extracted corpus."):
        return
    chart = (
        alt.Chart(plot)
        .mark_bar()
        .encode(
            x=alt.X("dimension:N", title=None, axis=alt.Axis(labelAngle=-20, labelLimit=240)),
            y=alt.Y("records:Q", title="Proxy disclosure count"),
            color=alt.Color("framework:N", title="Benchmark family"),
            xOffset="framework:N",
            tooltip=["framework", "dimension", "records"],
        )
        .properties(height=340)
    )
    st.altair_chart(chart, use_container_width=True)
    st.caption(
        "Proxy only: the current repo does not contain a finalized POJK-vs-IFRS checklist table, so this grouped bar is derived from framework and pillar-keyword mentions in extracted records."
    )


def reliability_adjusted_waterfall(df: pd.DataFrame, greenwashing_df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for reliability-adjusted scoring."):
        return
    if info_if_empty(greenwashing_df, "No company-level greenwashing index is available."):
        return
    gw = greenwashing_df.copy()
    for col in ["records", "commitment", "outcome", "missing", "greenwashing_index"]:
        gw[col] = pd.to_numeric(gw.get(col), errors="coerce").fillna(0)
    candidate = gw.sort_values(["records", "greenwashing_index"], ascending=[False, False]).head(1)
    if candidate.empty:
        st.info("No representative company could be selected for the reliability-adjusted waterfall.")
        return
    row = candidate.iloc[0]
    company = str(row["company"])
    subset = df[df.get("target_doc", "").astype(str) == company].copy()
    avg_words = float(subset["text_len_words"].mean()) if not subset.empty else 0.0
    raw_score = float(row["records"])
    fog_penalty = max(avg_words - 35.0, 0.0) * 0.15
    asymmetry_penalty = max(float(row["commitment"]) - float(row["outcome"]), 0.0)
    silence_penalty = float(row["missing"])
    adjusted = max(raw_score - fog_penalty - asymmetry_penalty - silence_penalty, 0.0)
    fig = go.Figure(
        go.Waterfall(
            measure=["absolute", "relative", "relative", "relative", "total"],
            x=[
                "Raw disclosure score",
                "High readability / fog penalty",
                "Commitment-outcome asymmetry",
                "Missing mandatory fields",
                "Reliability-adjusted score",
            ],
            y=[raw_score, -fog_penalty, -asymmetry_penalty, -silence_penalty, adjusted],
            text=[
                f"{raw_score:.1f}",
                f"-{fog_penalty:.1f}",
                f"-{asymmetry_penalty:.1f}",
                f"-{silence_penalty:.1f}",
                f"{adjusted:.1f}",
            ],
            connector={"line": {"color": "rgba(100,116,139,0.5)"}},
        )
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"Representative company: `{company}`. Proxy only: this waterfall demonstrates the adjustment logic using extracted-record counts, average record length, company-level commitment-outcome gap, and missing-tone counts. It is not a finalized thesis scoring model."
    )


def roc_readiness_note() -> None:
    st.info(
        "ROC / AUC comparison is not implementable from the current artifacts because the repo does not store a ground-truth credit, loan-eligibility, or default-risk label paired with the ESG scores."
    )


def aspect_centrality_network_proxy(df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for aspect-centrality analysis."):
        return
    deduped = df.drop_duplicates("record_key").copy()
    edges: dict[tuple[str, str], int] = {}
    degrees: dict[str, int] = {}
    for row in deduped.itertuples():
        primary = clean(row.aspect, "missing")
        extra = [label for label in parse_label_list(getattr(row, "labels", "")) if clean(label) not in {"", primary, "none", "missing"}]
        nodes = [primary] + extra[:4]
        unique_nodes = [node for idx, node in enumerate(nodes) if node not in nodes[:idx] and node not in {"none", "missing"}]
        if len(unique_nodes) < 2:
            continue
        for i in range(len(unique_nodes)):
            for j in range(i + 1, len(unique_nodes)):
                edge = tuple(sorted((unique_nodes[i], unique_nodes[j])))
                weight = edges.get(edge, 0) + 1
                edges[edge] = weight
    if not edges:
        st.info("No aspect-centrality edges could be derived from the current single-record structure.")
        return
    for (src, tgt), weight in edges.items():
        degrees[src] = degrees.get(src, 0) + weight
        degrees[tgt] = degrees.get(tgt, 0) + weight
    top_nodes = [node for node, _ in sorted(degrees.items(), key=lambda item: item[1], reverse=True)[:10]]
    filtered_edges = [
        {"source": src, "target": tgt, "weight": weight}
        for (src, tgt), weight in edges.items()
        if src in top_nodes and tgt in top_nodes
    ]
    if not filtered_edges:
        st.info("No top-node aspect edges survived the centrality filter.")
        return
    edge_df = pd.DataFrame(filtered_edges).sort_values("weight", ascending=False)
    node_df = pd.DataFrame(
        [{"aspect": node, "weighted_degree": degrees[node]} for node in top_nodes]
    ).sort_values("weighted_degree", ascending=False)

    n = len(top_nodes)
    positions = {
        node: (
            math.cos(2 * math.pi * idx / n),
            math.sin(2 * math.pi * idx / n),
        )
        for idx, node in enumerate(top_nodes)
    }
    fig = go.Figure()
    for row in edge_df.itertuples():
        x0, y0 = positions[row.source]
        x1, y1 = positions[row.target]
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=max(1, row.weight / 2), color="rgba(47,111,115,0.28)"),
                hoverinfo="text",
                text=f"{row.source} ↔ {row.target}<br>Weight: {row.weight}",
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[positions[node][0] for node in top_nodes],
            y=[positions[node][1] for node in top_nodes],
            mode="markers+text",
            text=top_nodes,
            textposition="top center",
            marker=dict(
                size=[14 + degrees[node] * 0.25 for node in top_nodes],
                color=[degrees[node] for node in top_nodes],
                colorscale="Tealgrn",
                line=dict(color="#1f2937", width=0.8),
                showscale=True,
                colorbar=dict(title="Weighted degree"),
            ),
            hovertemplate="%{text}<br>Weighted degree: %{marker.color}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        height=560,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(node_df, use_container_width=True, hide_index=True)
    st.caption(
        "Proxy centrality network: weighted degree is derived from co-occurrence links between the primary aspect and additional labels stored in the same extracted record."
    )


def llm_judge_readiness_note() -> None:
    st.info(
        "LLM-as-a-Judge robustness is not currently implementable from the stored artifacts. "
        "The repo does not yet contain pairwise judge scores, 1-10 disclosure-quality ratings, or expert-ranked snippet comparisons."
    )


def ocr_noise_readiness_note() -> None:
    st.info(
        "OCR noise sensitivity analysis is not currently implementable from the stored artifacts. "
        "There are OCR outputs and audits, but no controlled 5% / 10% / 20% perturbation experiment with re-scored extraction accuracy."
    )


def adversarial_readiness_note() -> None:
    st.info(
        "Adversarial red-teaming is not currently implementable from the stored artifacts. "
        "The repo does not yet store greenwashed rewrites paired with original negative statements and downstream ABSA outcomes."
    )


def qualitative_case_study(df: pd.DataFrame, greenwashing_df: pd.DataFrame) -> None:
    if info_if_empty(df, "No tone records available for qualitative case study."):
        return
    if info_if_empty(greenwashing_df, "No greenwashing index rows available for case selection."):
        return
    gw = greenwashing_df.copy()
    gw["greenwashing_index"] = pd.to_numeric(gw.get("greenwashing_index"), errors="coerce").fillna(0)
    top = gw.sort_values("greenwashing_index", ascending=False).head(1)
    if top.empty:
        st.info("No case-study company could be selected.")
        return
    company = str(top.iloc[0]["company"])
    subset = df[df.get("target_doc", "").astype(str) == company].copy()
    if subset.empty:
        subset = df[df.get("company_name", "").astype(str).str.contains(company, case=False, na=False)].copy()
    if subset.empty:
        st.info("The selected high-gap company does not have matching extracted rows in the current page dataset.")
        return
    subset = add_vagueness(subset.drop_duplicates("record_key"))
    cols = ["target_doc", "aspect", "tone", "sentiment", "vagueness_score", "soft_verb_hits", "concrete_verb_hits", "text"]
    st.markdown(f"**Case study company:** `{company}`")
    st.dataframe(
        subset[cols].sort_values(["tone", "vagueness_score"], ascending=[True, False]).head(12),
        use_container_width=True,
        hide_index=True,
    )


def load_page_data() -> dict[str, pd.DataFrame]:
    tone_records = load_workflow_csv("tone_records_flat.csv")
    return {
        "ocr": load_workflow_csv("ocr_processing_summary.csv"),
        "tone_records": tone_records,
        "tone_esg": load_workflow_csv("tone_esg_crosstab.csv"),
        "agreement": load_workflow_csv("climatebert_proxy_agreement_summary.csv"),
        "label_crosstab": load_workflow_csv("tone_climatebert_label_crosstab.csv"),
        "failure_modes": load_workflow_csv("failure_mode_counts.csv"),
        "ontology": load_workflow_csv("ontology_coverage.csv"),
        "model_stability": load_workflow_csv("model_stability_summary.csv"),
        "prompt_stability": load_workflow_csv("prompt_stability_summary.csv"),
        "prompt_stability_by_run": load_csv(REVISION / "prompt_stability_by_run.csv"),
        "greenwashing": load_workflow_csv("greenwashing_index_by_company.csv"),
        "tone_records_enriched": enrich_tone_records(tone_records),
        "silver_ground_truth": load_csv(REVISION / "silver_tone_ground_truth.csv"),
        "pilot_annotations": load_csv(REVISION / "pilot_ground_truth_annotations.csv"),
        "agreement_records": load_csv(REVISION / "climatebert_proxy_agreement_records.csv"),
        "failure_mode_rows": load_csv(REVISION / "failure_modes.csv"),
        "artifact_inventory": load_workflow_csv("artifact_inventory.csv"),
        "novel_aspect_review": load_csv(REVISION / "ontology_novel_aspect_review.csv"),
    }


def render_page_header(data: dict[str, pd.DataFrame], caption: str) -> None:
    st.title("Chapter 4 Results Visualizer")
    st.caption(caption)
    tone_records = data["tone_records"]
    if not tone_records.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tone Records", f"{len(tone_records):,}")
        col2.metric("Unique Aspects", f"{tone_records['aspect'].astype(str).nunique():,}" if "aspect" in tone_records.columns else "0")
        col3.metric("Source Files", f"{len(data['ocr']):,}")
        col4.metric("Model Rows", f"{len(data['model_stability']):,}")


def render_rq1(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "OCR Success Rate Stacked Bar",
            "Each file is grouped by OCR processing status to show the reliability of the source-preparation stage across the corpus.",
            "results/thesis_workflow_dashboard/ocr_processing_summary.csv",
        )
        status_stacked_bar(data["ocr"])
    with right:
        chart_title(
            "Page Count Distribution",
            "Report length distribution provides context for the volume of material the extraction pipeline had to process.",
            "results/thesis_workflow_dashboard/ocr_processing_summary.csv",
        )
        page_count_distribution(data["ocr"])


def render_rq2(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        chart_title(
            "Top 20 ESG Aspects",
            "Aspect frequency ranks the dominant disclosure themes captured in Indonesian sustainability reports.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        top_aspects_chart(data["tone_records_enriched"])
    with right:
        chart_title(
            "Narrative Tone Donut",
            "Overall tone percentages summarize whether the corpus leans toward commitment, action, outcome, or missing narrative styles.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        tone_donut(data["tone_records_enriched"])

    chart_title(
        "Pillar-Tone Heatmap",
        "High-intensity cells indicate where disclosure tone clusters within Environmental, Social, or Governance reporting.",
        "results/thesis_workflow_dashboard/tone_esg_crosstab.csv",
    )
    pillar_tone_heatmap(data["tone_esg"])


def render_rq3(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        chart_title(
            "Model Agreement Bar Chart",
            "ClimateBERT is used here as a climate-focused external reference. Agreement is therefore strongest for environmental records, not for full ESG coverage.",
            "results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv",
            "Current artifact stores percent agreement and Cohen's kappa, not a true F1 column.",
        )
        agreement_bar_chart(data["agreement"])
    with right:
        chart_title(
            "Label Mapping Sankey",
            "Thicker flows indicate stronger semantic alignment between LLM tone predictions and ClimateBERT climate labels.",
            "results/thesis_workflow_dashboard/tone_climatebert_label_crosstab.csv",
        )
        sankey_label_mapping(data["label_crosstab"])

    st.info("ClimateBERT is climate-limited, so this comparison does not cover Social and Governance semantics with the same depth as the LLM pipeline.")


def render_rq4(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "Failure Mode Pareto",
            "The cumulative line highlights the small set of technical failure categories that account for most pipeline instability and should be prioritized for human-in-the-loop mitigation.",
            "results/thesis_workflow_dashboard/failure_mode_counts.csv",
        )
        pareto_chart(data["failure_modes"])
    with right:
        chart_title(
            "Standard Coverage Venn",
            "Overlap approximates aspects aligned with GRI and SASB keys, while the outside segment captures vocabulary that falls outside both standards.",
            "results/thesis_workflow_dashboard/ontology_coverage.csv",
            "Current implementation infers GRI/SASB membership from `suggested_path` text matches.",
        )
        standards_venn(data["ontology"])


def render_rq6(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "Parse Success Line Chart",
            "Provider-level parse success helps justify the primary execution model on reproducibility and stability grounds.",
            "results/thesis_workflow_dashboard/model_stability_summary.csv",
        )
        provider_success_line(data["model_stability"])
    with right:
        chart_title(
            "Prompt Variance Box Plot",
            "Tighter prompt distributions indicate more reproducible extraction behavior; wider spreads indicate prompt sensitivity.",
            [
                "results/thesis_workflow_dashboard/prompt_stability_summary.csv",
                "results/revision_analysis/prompt_stability_by_run.csv",
            ],
        )
        prompt_variance_boxplot(data["prompt_stability"], data["prompt_stability_by_run"])


def render_advanced_esg(data: dict[str, pd.DataFrame]) -> None:
    st.header("Missing Analytical Layers for ESG Research Value")
    st.caption("These additions extend the page beyond pipeline benchmarking into sectoral, integrity, temporal, linguistic, and semantic analyses.")

    a1, a2 = st.columns(2)
    with a1:
        chart_title(
            "Sectoral Pillar Split",
            "Small multiples show whether sector priorities skew toward Environmental, Social, or Governance disclosures under different narrative tones.",
            [
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
                "data/indonesia_tickers.csv",
            ],
        )
        sectoral_pillar_split(data["tone_records_enriched"])
    with a2:
        chart_title(
            "Greenwashing / Narrative-Performance Gap",
            "Higher commitment counts with low outcome counts indicate more symbolic disclosure, while firms near the diagonal show more balanced reporting.",
            "results/thesis_workflow_dashboard/greenwashing_index_by_company.csv",
        )
        greenwashing_gap_scatter(data["greenwashing"])

    b1, b2 = st.columns(2)
    with b1:
        chart_title(
            "Temporal Topic Rank Over Time",
            "This bump chart tracks whether Indonesian disclosure emphasis is moving from generic themes toward more specific climate and governance topics over reporting years.",
            [
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
                "data/indonesia_tickers.csv",
            ],
        )
        temporal_topic_bump(data["tone_records_enriched"])
    with b2:
        chart_title(
            "Information Density by Tone",
            "Word-count distributions approximate disclosure richness. Short, repetitive outcome statements can indicate checkbox-style reporting.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        information_density_boxplot(data["tone_records_enriched"])

    chart_title(
        "Aspect Co-occurrence Network",
        "This network approximates the semantic relationships around each primary aspect using the additional labels present in the same extracted record.",
        "results/thesis_workflow_dashboard/tone_records_flat.csv",
    )
    aspect_cooccurrence_network(data["tone_records_enriched"])


def render_corpus(data: dict[str, pd.DataFrame]) -> None:
    c1, c2 = st.columns(2)
    with c1:
        chart_title(
            "Distribution of ESG Pillars",
            "This shows the balance of Environmental, Social, and Governance records in the extracted corpus.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        esg_pillar_distribution(data["tone_records_enriched"])
    with c2:
        chart_title(
            "Sector / Industry Composition",
            "Industry composition indicates how broadly the corpus covers different parts of the Indonesian reporting landscape.",
            [
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
                "data/indonesia_tickers.csv",
            ],
        )
        sector_composition(data["tone_records_enriched"])

    chart_title(
        "Document Length and Record Token Distribution",
        "These distributions show both report-scale processing burden and the granularity of extracted record text.",
        [
            "results/thesis_workflow_dashboard/ocr_processing_summary.csv",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        ],
    )
    left, right = st.columns(2)
    with left:
        page_count_distribution(data["ocr"])
    with right:
        record_token_distribution(data["tone_records_enriched"])


def render_performance(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "Comparative Performance Metrics",
            "Available benchmark metrics compare the LLM pipeline against the ClimateBERT-derived agreement reference.",
            "results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv",
            "Current artifact limitation: only percent agreement and Cohen's kappa are stored here.",
        )
        agreement_bar_chart(data["agreement"])
    with right:
        chart_title(
            "Binary Commitment Confusion Matrix",
            "This heatmap shows where LLM commitment predictions align or diverge from ClimateBERT commitment indicators.",
            "results/revision_analysis/climatebert_proxy_agreement_records.csv",
        )
        binary_commitment_confusion(data["agreement_records"])

    chart_title(
        "Ablation / Prompt Strategy Trends",
        "Prompt-level stability metrics act as a practical ablation view across zero-shot, chain-of-thought, and few-shot extraction strategies.",
        "results/thesis_workflow_dashboard/prompt_stability_summary.csv",
    )
    ablation_prompt_trends(data["prompt_stability"])


def render_thematic(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "Sentiment Distribution by ESG Pillar",
            "This stacked view shows whether positive, neutral, or negative tone is concentrated in specific ESG pillars.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        sentiment_by_pillar(data["tone_records_enriched"])
    with right:
        chart_title(
            "Greenwashing Gap",
            "The disclosure gap compares aspirational commitments with achieved outcomes at the company level.",
            "results/thesis_workflow_dashboard/greenwashing_index_by_company.csv",
        )
        greenwashing_gap_scatter(data["greenwashing"])

    chart_title(
        "Knowledge Graph / Aspect-Action Linkage",
        "This graph links dominant ESG aspects to their disclosure mode: commitment, action, or outcome.",
        "results/thesis_workflow_dashboard/tone_records_flat.csv",
    )
    aspect_action_linkage(data["tone_records_enriched"])

    chart_title(
        "Vagueness / Soft Language Quantification",
        "This experiment approximates the soft-language problem by scoring how often extracted records rely on aspirational verbs versus concrete operational verbs.",
        "results/thesis_workflow_dashboard/tone_records_flat.csv",
    )
    soft_language_ratio_chart(data["tone_records_enriched"])


def render_diagnostics(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "Error Distribution Pie Chart",
            "This chart summarizes which technical failure classes dominate the observed pipeline errors.",
            "results/thesis_workflow_dashboard/failure_mode_counts.csv",
        )
        error_distribution_pie(data["failure_modes"])
    with right:
        chart_title(
            "Failure Mode Pareto",
            "The Pareto view identifies the vital few failure modes that deserve priority intervention.",
            "results/thesis_workflow_dashboard/failure_mode_counts.csv",
        )
        pareto_chart(data["failure_modes"])

    chart_title(
        "Inter-Annotator Agreement Heatmap",
        "Human-annotation agreement is the ideal validation layer, but the current artifact set does not yet contain populated multi-annotator identities.",
        "results/revision_analysis/pilot_ground_truth_annotations.csv",
    )
    agreement_availability_note(data["pilot_annotations"])

    chart_title(
        "Inference Cost vs Performance Trade-off",
        "A cost-performance scatter would require consistent latency or cost measurements alongside evaluation metrics.",
        [
            "results/thesis_workflow_dashboard/model_stability_summary.csv",
            "results/revision_analysis/prompt_stability_by_run.csv",
        ],
    )
    cost_performance_note()

    chart_title(
        "Cross-Document Consistency Analysis",
        "This discrepancy matrix approximates the gap between sustainability-style and annual/financial-style disclosures within the same inferred company-year.",
        [
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
            "data/indonesia_tickers.csv",
        ],
    )
    cross_document_discrepancy_matrix(data["tone_records_enriched"])


def render_ablation_plus(data: dict[str, pd.DataFrame]) -> None:
    left, right = st.columns(2)
    with left:
        chart_title(
            "Prompt Strategy Bar Chart",
            "This grouped bar view compares prompt strategies using silver ground-truth tone labels.",
            "results/revision_analysis/silver_tone_ground_truth.csv",
        )
        prompt_strategy_bar(data["silver_ground_truth"])
    with right:
        chart_title(
            "Token Window vs Accuracy Line Graph",
            "Current artifact limitation: this uses extracted record length as a proxy for token-window stress because the stored results do not preserve raw token-window configurations.",
            "results/revision_analysis/silver_tone_ground_truth.csv",
        )
        token_window_accuracy(data["silver_ground_truth"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "Aspect-Action-Sentiment Sankey Diagram",
            "This flow links dominant aspects to disclosure mode and sentiment, approximating how soft-language commitments differ from concrete outcomes.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        aspect_action_sentiment_sankey(data["tone_records_enriched"])
    with right:
        chart_title(
            "Sentiment Density Plot",
            "This density plot shows the distribution of extracted sentiment scores. ClimateBERT sentiment distributions are not available in the current artifact set.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        )
        sentiment_density_plot(data["tone_records_enriched"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "Error Taxonomy Sunburst Chart",
            "This chart groups low-level failure types into broader error families for qualitative diagnostics.",
            "results/revision_analysis/failure_modes.csv",
        )
        error_taxonomy_sunburst(data["failure_mode_rows"])
    with right:
        chart_title(
            "Confidence Calibration Plot",
            "Current artifact limitation: this uses absolute sentiment score as a confidence proxy because the tone classifier does not store calibrated confidence values.",
            "results/revision_analysis/silver_tone_ground_truth.csv",
        )
        confidence_calibration_plot(data["silver_ground_truth"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "Cost-Accuracy Pareto Frontier",
            "Current artifact limitation: this uses average event runtime as a cost proxy rather than monetary API spend.",
            [
                "results/revision_analysis/dataset_phase_registry.csv",
                "results/background_llm_jobs/*/events.jsonl",
            ],
        )
        model_cost_accuracy_pareto()
    with right:
        chart_title(
            "Heatmap of ESG Coverage by Sector",
            "This heatmap shows which sectors emphasize which ABSA dimensions most strongly.",
            [
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
                "data/indonesia_tickers.csv",
            ],
        )
        sector_absa_heatmap(data["tone_records_enriched"])


def render_narrative_evidence(data: dict[str, pd.DataFrame]) -> None:
    st.header("Graphs Backing Chapter 4 and Chapter 5 Narrative Claims")
    st.caption("These visuals are selected to support the specific quantitative statements currently used in Sections 4.1-5.4.")

    left, right = st.columns(2)
    with left:
        chart_title(
            "Implementation Funnel",
            "Supports the claim that the study processed 23 reports through documented jobs, successful extraction runs, and artifact generation.",
            [
                "results/thesis_workflow_dashboard/ocr_processing_summary.csv",
                "results/thesis_workflow_dashboard/artifact_inventory.csv",
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
            ],
            "The counts for 156 documented jobs and 110 successful runs are thesis claims; source artifacts directly back the report/document, artifact, and record totals.",
        )
        thesis_overview_funnel(data["ocr"], data["artifact_inventory"], data["tone_records"])
    with right:
        chart_title(
            "Bilingual Corpus Context",
            "Supports the bilingual-processing claim by showing language composition in the reviewed silver dataset.",
            "results/revision_analysis/silver_tone_ground_truth.csv",
        )
        bilingual_context_chart(data["silver_ground_truth"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "Model Selection Trade-off",
            "Supports the multi-model strategy claim by placing stability against extraction yield for the available models.",
            "results/thesis_workflow_dashboard/model_stability_summary.csv",
        )
        model_tradeoff_chart(data["model_stability"])
    with right:
        chart_title(
            "Commitment Dominance",
            "Supports the Chapter 5 discussion that commitment disclosures dominate outcome disclosures in the extracted corpus.",
            [
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
                "results/revision_analysis/chapter4_tone_denominator_audit.csv",
            ],
        )
        commitment_outcome_ratio_chart(data["tone_records_enriched"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "ClimateBERT Divergence Summary",
            "Supports the construct-validity discussion that ClimateBERT topic relevance and tone maturity are analytically orthogonal.",
            [
                "results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv",
                "results/revision_analysis/climatebert_record_batch_import.csv",
            ],
        )
        climatebert_divergence_summary()
    with right:
        chart_title(
            "Silver Dataset Overview",
            "Supports the ground-truth generation section by showing the scale and coverage of the reviewed silver dataset.",
            "results/revision_analysis/silver_tone_ground_truth.csv",
        )
        silver_dataset_overview(data["silver_ground_truth"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "Human-vs-LLM Agreement Summary",
            "Supports the claim that LLM tone predictions align strongly with reviewed silver labels.",
            "results/revision_analysis/silver_tone_ground_truth.csv",
        )
        human_llm_agreement_summary(data["silver_ground_truth"])
    with right:
        chart_title(
            "Ontology Novelty and Review Burden",
            "Supports the ontology-gap discussion by separating canonicalized aspects from placeholder/review-heavy Indonesian-specific vocabulary.",
            "results/revision_analysis/ontology_novel_aspect_review.csv",
        )
        ontology_novelty_chart(data["novel_aspect_review"])

    st.header("Additional Thesis Figures")
    st.caption("These figures address the latest thesis-facing visual gaps. Where the repo lacks a finalized benchmark artifact, the page renders an explicit proxy or readiness note.")

    left, right = st.columns(2)
    with left:
        chart_title(
            "IFRS-POJK Alignment Gap",
            "Grouped bars compare proxy disclosure coverage under POJK-style versus IFRS S1/S2-style framing to visualize the regulatory leap discussed in the literature review.",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
            "Proxy only: no finalized POJK-vs-IFRS checklist artifact exists in the repo.",
        )
        regulatory_alignment_proxy_chart(data["tone_records_enriched"])
    with right:
        chart_title(
            "Commitment-Outcome Asymmetry",
            "Firms above the diagonal disclose more commitments than outcomes and therefore present a stronger narrative-performance gap.",
            "results/thesis_workflow_dashboard/greenwashing_index_by_company.csv",
        )
        greenwashing_gap_scatter(data["greenwashing"])

    left, right = st.columns(2)
    with left:
        chart_title(
            "Reliability-Adjusted Score Waterfall",
            "This waterfall demonstrates how a raw disclosure score contracts once readability burden, commitment-outcome asymmetry, and missing-field penalties are applied.",
            [
                "results/thesis_workflow_dashboard/tone_records_flat.csv",
                "results/thesis_workflow_dashboard/greenwashing_index_by_company.csv",
            ],
            "Demonstrator only: the current repo does not yet contain a canonical reliability-adjusted score artifact.",
        )
        reliability_adjusted_waterfall(data["tone_records_enriched"], data["greenwashing"])
    with right:
        chart_title(
            "Predictive Performance: ESG as a Credit Signal",
            "A raw-vs-adjusted ROC comparison would require loan, default, or credit-eligibility ground truth paired with each company score.",
            "artifact not yet generated",
        )
        roc_readiness_note()

    chart_title(
        "Semantic Network Centrality",
        "This graph highlights hub aspects in the Indonesian ESG discourse using weighted degree as a transparent proxy for centrality.",
        "results/thesis_workflow_dashboard/tone_records_flat.csv",
    )
    aspect_centrality_network_proxy(data["tone_records_enriched"])


def render_publication_gaps(data: dict[str, pd.DataFrame]) -> None:
    del data
    st.header("Publication-Grade Gaps")
    st.caption("These are the remaining artifact gaps between the current interactive dashboard and a fully publication-grade benchmark package.")
    st.dataframe(publication_gaps_table(), use_container_width=True, hide_index=True)
    chart_title(
        "LLM-as-a-Judge Robustness",
        "Pairwise judge-ranking and 1-10 disclosure-quality scoring require new evaluation artifacts.",
        "not yet generated",
    )
    llm_judge_readiness_note()
    chart_title(
        "OCR Noise Sensitivity Analysis",
        "Controlled perturbation experiments are needed to quantify extraction decay under OCR noise.",
        "not yet generated",
    )
    ocr_noise_readiness_note()
    chart_title(
        "Adversarial Red Teaming",
        "Greenwashed rewrites paired with original factual negatives are needed to test robustness against impression-management language.",
        "not yet generated",
    )
    adversarial_readiness_note()


def render_qualitative_cases(data: dict[str, pd.DataFrame]) -> None:
    st.header("Section 4.5 / 4.6 Readiness and Case Studies")
    chart_title(
        "Qualitative Greenwashing Case Study",
        "This case-study panel selects the highest-gap company in the current greenwashing index and shows example extracted disclosures, tones, and vagueness signals.",
        [
            "results/thesis_workflow_dashboard/greenwashing_index_by_company.csv",
            "results/thesis_workflow_dashboard/tone_records_flat.csv",
        ],
    )
    qualitative_case_study(data["tone_records_enriched"], data["greenwashing"])


SECTION_RENDERERS: list[tuple[str, Callable[[dict[str, pd.DataFrame]], None]]] = [
    ("RQ1", render_rq1),
    ("RQ2", render_rq2),
    ("RQ3", render_rq3),
    ("RQ4", render_rq4),
    ("RQ6", render_rq6),
    ("Advanced ESG", render_advanced_esg),
    ("Corpus", render_corpus),
    ("Performance", render_performance),
    ("Thematic", render_thematic),
    ("Diagnostics", render_diagnostics),
    ("Ablation+", render_ablation_plus),
    ("Narrative Evidence", render_narrative_evidence),
    ("Publication Gaps", render_publication_gaps),
    ("Qualitative Cases", render_qualitative_cases),
]


def render_tabbed_page() -> None:
    data = load_page_data()
    render_page_header(data, "Thesis-facing Chapter 4 graphs derived from the current workflow CSV outputs.")
    tabs = st.tabs([name for name, _ in SECTION_RENDERERS])
    for tab, (_, renderer) in zip(tabs, SECTION_RENDERERS):
        with tab:
            renderer(data)


def render_long_page() -> None:
    data = load_page_data()
    render_page_header(
        data,
        "Long-form thesis-facing Chapter 4 graphs derived from the current workflow CSV outputs. This page reuses the same implementation as the tabbed visualizer.",
    )
    for name, renderer in SECTION_RENDERERS:
        st.divider()
        st.subheader(name)
        renderer(data)
