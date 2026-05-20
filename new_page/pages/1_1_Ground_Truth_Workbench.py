from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Ground Truth Workbench", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
ARTIFACTS = ROOT / "results" / "revision_analysis"
SEED_PATH = ARTIFACTS / "pilot_ground_truth_seed.csv"
ANNOTATION_PATH = ARTIFACTS / "pilot_ground_truth_annotations.csv"
SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"

TONE_OPTIONS = ["", "commitment", "action", "outcome", "none", "unknown"]
ESG_OPTIONS = ["", "e", "s", "g", "none", "unknown"]
STATUS_OPTIONS = ["needs_review", "reviewed", "uncertain", "discard"]

from graph_attachment_gallery import render_attachment_cards  # noqa: E402


def load_table():
    path = ANNOTATION_PATH if ANNOTATION_PATH.exists() else SEED_PATH
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


def cohen_kappa(a, b):
    pairs = [(str(x), str(y)) for x, y in zip(a, b) if str(x).strip() and str(y).strip()]
    if not pairs:
        return None, 0, None
    labels = sorted(set([x for x, _ in pairs] + [y for _, y in pairs]))
    n = len(pairs)
    po = sum(1 for x, y in pairs if x == y) / n
    pe = 0
    for label in labels:
        pa = sum(1 for x, _ in pairs if x == label) / n
        pb = sum(1 for _, y in pairs if y == label) / n
        pe += pa * pb
    kappa = (po - pe) / (1 - pe) if (1 - pe) else 0
    return kappa, n, po


st.title("Ground Truth Workbench")
st.caption("Pilot human annotation scaffold for tone, ESG pillar, and aspect validation. This page creates the missing ground-truth layer requested in the feedback.")

df = load_table()
if df.empty:
    st.error(f"No pilot ground truth seed found at {SEED_PATH}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    status_filter = st.multiselect("Review status", STATUS_OPTIONS, default=STATUS_OPTIONS)
    tone_filter = st.multiselect("Predicted tone", sorted(df["tone_pred"].dropna().unique().tolist()), default=sorted(df["tone_pred"].dropna().unique().tolist()))
    lang_filter = st.multiselect("Language", sorted(df["language"].dropna().unique().tolist()), default=sorted(df["language"].dropna().unique().tolist()))

view = df[
    df["review_status"].isin(status_filter)
    & df["tone_pred"].isin(tone_filter)
    & df["language"].isin(lang_filter)
].copy()

overview, annotate, agreement, export, attachment_cards = st.tabs(["Overview", "Annotate", "Agreement", "Export", "Attachment Cards"])

with overview:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Pilot records", f"{len(df):,}")
    with c2:
        st.metric("Visible records", f"{len(view):,}")
    with c3:
        completed = int(df["ground_truth_tone"].astype(str).str.strip().ne("").sum())
        st.metric("Tone labels filled", f"{completed:,}")
    with c4:
        reviewed = int(df["review_status"].eq("reviewed").sum())
        st.metric("Reviewed", f"{reviewed:,}")

    tone_counts = df["tone_pred"].value_counts().rename_axis("tone_pred").reset_index(name="count")
    chart = (
        alt.Chart(tone_counts)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title=None),
            y=alt.Y("tone_pred:N", sort="-x", title=None),
            tooltip=["tone_pred", "count"],
            color=alt.value("#2f6f73"),
        )
        .properties(title="Pilot Sample by Predicted Tone", height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Annotation Protocol")
    st.markdown(
        """
        Use `ground_truth_tone` as the human label. The model label remains in `tone_pred`, and the weak/silver recommendation remains in `suggested_tone`.

        - `commitment`: promise, target, intent, future plan, or pledge.
        - `action`: activity, implementation, program, procedure, or control.
        - `outcome`: achieved result, measurable performance, reduction, completion, or certified output.
        - `none`: no meaningful ESG tone.
        - `unknown`: annotator cannot decide from the provided text.
        """
    )

with annotate:
    st.subheader("Editable Pilot Annotation Table")
    st.write("Edit the ground-truth columns and click save. The file is saved to `results/revision_analysis/pilot_ground_truth_annotations.csv`.")

    editable_cols = [
        "record_id",
        "company",
        "language",
        "prompt",
        "model",
        "tone_pred",
        "suggested_tone",
        "ground_truth_tone",
        "esg",
        "ground_truth_esg",
        "aspect",
        "ground_truth_aspect",
        "review_status",
        "annotator",
        "review_notes",
        "text",
    ]
    edited = st.data_editor(
        view[editable_cols],
        use_container_width=True,
        height=620,
        column_config={
            "ground_truth_tone": st.column_config.SelectboxColumn("ground_truth_tone", options=TONE_OPTIONS),
            "ground_truth_esg": st.column_config.SelectboxColumn("ground_truth_esg", options=ESG_OPTIONS),
            "review_status": st.column_config.SelectboxColumn("review_status", options=STATUS_OPTIONS),
            "text": st.column_config.TextColumn("text", width="large"),
        },
        disabled=["record_id", "company", "language", "prompt", "model", "tone_pred", "suggested_tone", "esg", "aspect", "text"],
    )

    if st.button("Save annotations", type="primary"):
        merged = df.set_index("record_id").copy()
        update = edited.set_index("record_id")
        for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "review_status", "annotator", "review_notes"]:
            merged.loc[update.index, col] = update[col]
        merged.reset_index().to_csv(ANNOTATION_PATH, index=False)
        st.success(f"Saved annotations to {ANNOTATION_PATH}")

with agreement:
    st.subheader("Pilot Agreement Metrics")
    annotated = df[df["ground_truth_tone"].astype(str).str.strip().ne("")].copy()
    if annotated.empty:
        st.info("No human tone labels yet. Add `ground_truth_tone` labels in the Annotate tab, save, and return here.")
    else:
        kappa, n, pct = cohen_kappa(annotated["tone_pred"], annotated["ground_truth_tone"])
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Annotated tone rows", f"{n:,}")
        with c2:
            st.metric("Percent agreement", f"{pct:.3f}")
        with c3:
            st.metric("Cohen kappa", f"{kappa:.3f}")

        conf = annotated.groupby(["ground_truth_tone", "tone_pred"]).size().reset_index(name="count")
        heat = (
            alt.Chart(conf)
            .mark_rect()
            .encode(
                x=alt.X("tone_pred:N", title="Predicted tone"),
                y=alt.Y("ground_truth_tone:N", title="Human tone"),
                color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
                tooltip=["ground_truth_tone", "tone_pred", "count"],
            )
            .properties(title="Tone Confusion Matrix", height=360)
        )
        labels = alt.Chart(conf).mark_text().encode(
            x="tone_pred:N",
            y="ground_truth_tone:N",
            text="count:Q",
            color=alt.condition(alt.datum.count > conf["count"].max() * 0.55, alt.value("white"), alt.value("#17202a")),
        )
        st.altair_chart(heat + labels, use_container_width=True)

        st.subheader("Disagreements")
        st.dataframe(annotated[annotated["tone_pred"] != annotated["ground_truth_tone"]], use_container_width=True, height=420)

with export:
    st.subheader("Exports")
    st.download_button(
        "Download current annotation table",
        df.to_csv(index=False).encode("utf-8"),
        file_name="pilot_ground_truth_annotations.csv",
        mime="text/csv",
    )
    if SILVER_PATH.exists():
        silver = pd.read_csv(SILVER_PATH)
        st.download_button(
            "Download full silver ground-truth scaffold",
            silver.to_csv(index=False).encode("utf-8"),
            file_name="silver_tone_ground_truth.csv",
            mime="text/csv",
        )
        st.dataframe(silver.head(100), use_container_width=True, height=420)

with attachment_cards:
    render_attachment_cards(
        "Ground Truth Workbench Graph + Table Attachment Cards",
        chapter_default="Chapter 4",
        rq_default="RQ2",
        figures=["A.13", "A.17", "A.18", "A.19", "A.20"],
    )
