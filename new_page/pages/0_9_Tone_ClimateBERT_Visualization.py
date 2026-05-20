import json
import re
from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Tone vs ClimateBERT", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
RESULTS_DIR = ROOT / "results"
ESG_RECORDS = RESULTS_DIR / "esg_records.json"
CLIMATEBERT_RESULTS = RESULTS_DIR / "climatebert_results.json"
DOC_PATH = ROOT / "docs" / "tone_climatebert_comparison.md"

TONE_ORDER = ["commitment", "action", "outcome", "none", "unknown", "missing"]
PILLAR_ORDER = ["e", "s", "g", "none", "missing"]

from graph_attachment_gallery import render_attachment_cards  # noqa: E402


def clean_label(value, default="missing"):
    text = "" if value is None else str(value).strip().lower()
    return text or default


def normalize_tone(value):
    text = clean_label(value)
    aliases = {
        "commitment": "commitment",
        "action": "action",
        "outcome": "outcome",
        "none": "none",
        "unknown": "unknown",
        "missing": "missing",
    }
    return aliases.get(text, text)


def short_text(value, limit=180):
    text = "" if value is None else str(value).strip().replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "..."


def climatebert_label_family(label):
    text = clean_label(label)
    if text.startswith("climate-"):
        return text
    if text in {"environmental-claims", "netzero-reduction", "renewable"}:
        return text
    if text in {"governance", "social", "employee", "community"}:
        return text
    if text == "none":
        return "none"
    return "other"


@st.cache_data(show_spinner=False)
def load_tone_records():
    if not ESG_RECORDS.exists():
        return pd.DataFrame()

    raw = json.loads(ESG_RECORDS.read_text(encoding="utf-8") or "[]")
    rows = []
    for run_idx, run in enumerate(raw):
        for record_idx, record in enumerate(run.get("records") or []):
            labels = record.get("labels")
            if not isinstance(labels, list):
                labels = []
            target = run.get("target") or ""
            rows.append(
                {
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": run.get("timestamp"),
                    "model": run.get("model") or "missing",
                    "target": target,
                    "target_doc": re.sub(r"_pdf/batch_\d+$", "", target),
                    "prompt": run.get("prompt") or "missing",
                    "text": record.get("text") or "",
                    "text_short": short_text(record.get("text")),
                    "aspect": clean_label(record.get("aspect")),
                    "esg": clean_label(record.get("esg")),
                    "tone": normalize_tone(record.get("tone")),
                    "sentiment": clean_label(record.get("sentiment")),
                    "sentiment_score": record.get("sentiment_score"),
                    "labels": labels,
                    "labels_joined": ", ".join(labels),
                    "reasoning": record.get("reasoning") or "",
                }
            )
    return pd.DataFrame(rows)


def parse_climatebert_response(raw):
    if raw is None:
        return []

    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
    models = []
    current = None
    bullet_re = re.compile(r"^[•\-\*\u2022]\s*(.+)$")
    label_val_re = re.compile(r"^(.+?)\s*[:\-]\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")

    for line in [line.strip() for line in text.splitlines()]:
        if not line:
            continue
        if line.startswith("###"):
            if current is not None:
                models.append(current)
            current = {"model": line[3:].strip(), "status": "ok", "scores": {}, "error": ""}
            continue
        if current is None:
            continue
        if "❌" in line or line.lower().startswith("error:") or "unrecognized model" in line.lower():
            msg = line.replace("❌", "").strip()
            current["status"] = "error"
            current["error"] = re.sub(r"^error:\s*", "", msg, flags=re.I)
            continue

        bullet = bullet_re.match(line)
        candidate = bullet.group(1).strip() if bullet else line
        pair = label_val_re.match(candidate)
        if pair:
            current["scores"][pair.group(1).strip()] = float(pair.group(2))

    if current is not None:
        models.append(current)
    return models


@st.cache_data(show_spinner=False)
def load_climatebert_rows():
    if not CLIMATEBERT_RESULTS.exists():
        return pd.DataFrame()

    raw = json.loads(CLIMATEBERT_RESULTS.read_text(encoding="utf-8") or "[]")
    rows = []
    for run_idx, run in enumerate(raw):
        models = None
        parsed = run.get("response_parsed")
        if isinstance(parsed, dict):
            models = parsed.get("models")
        if not models:
            models = parse_climatebert_response(run.get("response_raw"))

        for model in models:
            scores = model.get("scores") or {}
            if scores:
                for label, score in scores.items():
                    rows.append(
                        {
                            "run_idx": run_idx,
                            "timestamp": run.get("timestamp"),
                            "input_text": run.get("input_text") or "",
                            "input_short": short_text(run.get("input_text")),
                            "model": model.get("model") or model.get("name"),
                            "status": model.get("status"),
                            "label": label,
                            "score": score,
                            "error": model.get("error") or "",
                        }
                    )
            else:
                rows.append(
                    {
                        "run_idx": run_idx,
                        "timestamp": run.get("timestamp"),
                        "input_text": run.get("input_text") or "",
                        "input_short": short_text(run.get("input_text")),
                        "model": model.get("model") or model.get("name"),
                        "status": model.get("status"),
                        "label": "",
                        "score": None,
                        "error": model.get("error") or "",
                    }
                )
    df = pd.DataFrame(rows)
    if not df.empty:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
    return df


def metric_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)


def count_bar(df, x, y, title, color=None, sort="-x", height=340):
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=2, cornerRadiusBottomRight=2)
        .encode(
            x=alt.X(f"{x}:Q", title="Count"),
            y=alt.Y(f"{y}:N", sort=sort, title=None),
            color=color or alt.value("#2f6f73"),
            tooltip=[alt.Tooltip(f"{y}:N"), alt.Tooltip(f"{x}:Q", title="Count")],
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def heatmap(df, x, y, value, title, height=360):
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(f"{x}:N", title=None),
            y=alt.Y(f"{y}:N", title=None),
            color=alt.Color(f"{value}:Q", title="Count", scale=alt.Scale(scheme="tealblues")),
            tooltip=[
                alt.Tooltip(f"{y}:N"),
                alt.Tooltip(f"{x}:N"),
                alt.Tooltip(f"{value}:Q", title="Count"),
            ],
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
            color=alt.condition(alt.datum[value] > df[value].max() * 0.55, alt.value("white"), alt.value("#17202a")),
        )
    )
    st.altair_chart(chart + text, use_container_width=True)


st.title("Tone vs ClimateBERT Visualization")
st.caption("Explore the existing ESG tone extraction results and compare them with ClimateBERT-style labels.")

tone_df = load_tone_records()
climate_df = load_climatebert_rows()

if tone_df.empty:
    st.error(f"No ESG tone records found at {ESG_RECORDS}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    tone_choices = [tone for tone in TONE_ORDER if tone in set(tone_df["tone"])] + sorted(
        set(tone_df["tone"]) - set(TONE_ORDER)
    )
    selected_tones = st.multiselect("Tone", tone_choices, default=tone_choices)

    esg_choices = [pillar for pillar in PILLAR_ORDER if pillar in set(tone_df["esg"])] + sorted(
        set(tone_df["esg"]) - set(PILLAR_ORDER)
    )
    selected_esg = st.multiselect("ESG pillar", esg_choices, default=esg_choices)

    prompt_choices = sorted(tone_df["prompt"].dropna().unique().tolist())
    selected_prompts = st.multiselect("Prompt", prompt_choices, default=prompt_choices)

    target_choices = sorted(tone_df["target_doc"].dropna().unique().tolist())
    selected_targets = st.multiselect("Source document", target_choices, default=target_choices)

    min_label_count = st.slider("Minimum label count", 1, 25, 2)

filtered = tone_df[
    tone_df["tone"].isin(selected_tones)
    & tone_df["esg"].isin(selected_esg)
    & tone_df["prompt"].isin(selected_prompts)
    & tone_df["target_doc"].isin(selected_targets)
].copy()

tab_overview, tab_comparison, tab_climatebert, tab_records, tab_docs, tab_cards = st.tabs(
    ["Overview", "Tone Comparison", "ClimateBERT Runs", "Records", "Documentation", "Attachment Cards"]
)

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Filtered records", f"{len(filtered):,}")
    with c2:
        metric_card("Source targets", f"{filtered['target'].nunique():,}")
    with c3:
        metric_card("Runs", f"{filtered['run_idx'].nunique():,}")
    with c4:
        missing_tone = int((filtered["tone"] == "missing").sum())
        metric_card("Missing tone", f"{missing_tone:,}")

    left, right = st.columns([1, 1])
    with left:
        tone_counts = filtered["tone"].value_counts().rename_axis("tone").reset_index(name="count")
        count_bar(tone_counts, "count", "tone", "Tone Distribution", height=320)
    with right:
        esg_counts = filtered["esg"].value_counts().rename_axis("esg").reset_index(name="count")
        count_bar(esg_counts, "count", "esg", "ESG Pillar Distribution", color=alt.Color("esg:N", legend=None), height=320)

    st.subheader("Tone by ESG Pillar")
    tone_esg = filtered.groupby(["tone", "esg"]).size().reset_index(name="count")
    stacked = (
        alt.Chart(tone_esg)
        .mark_bar()
        .encode(
            x=alt.X("tone:N", sort=TONE_ORDER, title=None),
            y=alt.Y("count:Q", title="Record count"),
            color=alt.Color("esg:N", title="ESG"),
            tooltip=["tone", "esg", "count"],
        )
        .properties(height=360)
    )
    st.altair_chart(stacked, use_container_width=True)

with tab_comparison:
    st.subheader("Tone vs ClimateBERT-Style Labels")
    exploded = filtered.explode("labels").copy()
    exploded["label_family"] = exploded["labels"].map(climatebert_label_family)
    label_counts = (
        exploded.groupby(["tone", "label_family"])
        .size()
        .reset_index(name="count")
        .query("count >= @min_label_count")
    )
    if label_counts.empty:
        st.info("No label combinations match the current filters.")
    else:
        top_labels = (
            label_counts.groupby("label_family")["count"]
            .sum()
            .sort_values(ascending=False)
            .head(16)
            .index
        )
        label_counts = label_counts[label_counts["label_family"].isin(top_labels)]
        heatmap(label_counts, "label_family", "tone", "count", "Tone vs ClimateBERT-Style Label Family", height=420)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Top Aspects")
        aspect_counts = filtered["aspect"].value_counts().head(18).rename_axis("aspect").reset_index(name="count")
        count_bar(aspect_counts, "count", "aspect", "Aspect Frequency", height=520)
    with right:
        st.subheader("Aspect by Tone")
        top_aspects = aspect_counts["aspect"].tolist()
        aspect_tone = (
            filtered[filtered["aspect"].isin(top_aspects[:12])]
            .groupby(["aspect", "tone"])
            .size()
            .reset_index(name="count")
        )
        if aspect_tone.empty:
            st.info("No aspect/tone rows for the current filters.")
        else:
            heatmap(aspect_tone, "tone", "aspect", "count", "Top Aspects Split by Tone", height=520)

    st.subheader("Interpretation Guide")
    st.markdown(
        """
        - `commitment` should usually align with `climate-commitment`, `netzero-reduction`, or `environmental-claims`.
        - `action` should usually align with concrete operational, governance, or implementation labels.
        - `outcome` should be strongest where the text reports results, metrics, reductions, or achieved performance.
        - `none` should mostly align with non-climate or generic labels; climate-specific labels under `none` are useful review candidates.
        """
    )

with tab_climatebert:
    st.subheader("Remote ClimateBERT Sample")
    if climate_df.empty:
        st.warning(f"No ClimateBERT result rows found at {CLIMATEBERT_RESULTS}")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Remote runs", f"{climate_df['run_idx'].nunique():,}")
        with c2:
            metric_card("Models", f"{climate_df['model'].nunique():,}")
        with c3:
            metric_card("Model rows", f"{len(climate_df):,}")
        with c4:
            metric_card("Errors", f"{int((climate_df['status'] == 'error').sum()):,}")

        ok_df = climate_df[climate_df["status"] == "ok"].dropna(subset=["score"]).copy()
        if not ok_df.empty:
            top_per_model = (
                ok_df.sort_values(["run_idx", "model", "score"], ascending=[True, True, False])
                .groupby(["run_idx", "model"], as_index=False)
                .first()
                .rename(columns={"label": "top_label", "score": "top_score"})
            )
            chart = (
                alt.Chart(top_per_model)
                .mark_circle(size=95, opacity=0.82)
                .encode(
                    x=alt.X("top_score:Q", title="Top score", scale=alt.Scale(domain=[0, 1])),
                    y=alt.Y("model:N", sort="x", title=None),
                    color=alt.Color("top_label:N", title="Top label"),
                    tooltip=["run_idx", "model", "top_label", "top_score", "input_short"],
                )
                .properties(title="Top ClimateBERT Label per Model and Run", height=520)
            )
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(top_per_model, use_container_width=True)

        with st.expander("All parsed ClimateBERT rows"):
            st.dataframe(climate_df, use_container_width=True)

        errors = climate_df[climate_df["status"] == "error"][["run_idx", "model", "error"]].drop_duplicates()
        if not errors.empty:
            with st.expander("Model errors"):
                st.dataframe(errors, use_container_width=True)

with tab_records:
    st.subheader("Filtered Tone Records")
    visible_cols = [
        "timestamp",
        "target",
        "prompt",
        "tone",
        "esg",
        "aspect",
        "sentiment",
        "labels_joined",
        "text",
        "reasoning",
    ]
    st.dataframe(filtered[visible_cols], use_container_width=True, height=560)
    st.download_button(
        "Download filtered records CSV",
        filtered[visible_cols].to_csv(index=False).encode("utf-8"),
        file_name="tone_climatebert_filtered_records.csv",
        mime="text/csv",
    )

with tab_docs:
    st.subheader("Documentation")
    if DOC_PATH.exists():
        st.markdown(DOC_PATH.read_text(encoding="utf-8"))
    else:
        st.info("No generated documentation found yet. Run code/visualize_tone_climatebert.py to create it.")

with tab_cards:
    render_attachment_cards(
        "Tone vs ClimateBERT Graph + Table Attachment Cards",
        chapter_default="Chapter 5",
        rq_default="RQ3",
        figures=["A.4", "A.5", "A.15"],
    )
