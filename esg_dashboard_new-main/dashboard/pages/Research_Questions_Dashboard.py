import pandas as pd
import streamlit as st

from _rq_thesis_content import (
    ARTIFACT_JSON,
    CHAPTER_4_SECTIONS,
    CHAPTER_5_SECTIONS,
    CHAPTER_6_SECTIONS,
    CHAPTER_FLOW_MERMAID,
    EXISTING_DATA_PATH,
    PREDICTION_OUTPUT_DIR,
    RQ_PAGE_MAP,
    RQ_TO_CHAPTER_MERMAID,
    load_artifact_report,
    page_link_grid,
    render_mermaid,
)


st.set_page_config(page_title="Research Questions Dashboard", layout="wide")
st.title("Research Questions Dashboard")
st.caption("Navigation map from research questions to implementation pages, thesis chapters, evidence outputs, and remaining validation work.")

st.caption(f"Existing data: `{EXISTING_DATA_PATH}`")
st.caption(f"Prediction outputs: `{PREDICTION_OUTPUT_DIR}`")
st.caption(f"Artifact explanation bundle: `{ARTIFACT_JSON}`")


def rq_rows() -> pd.DataFrame:
    rows = []
    for rq in RQ_PAGE_MAP:
        rows.append(
            {
                "rq": rq["rq"],
                "theme": rq["theme"],
                "question": rq["question"],
                "pages_to_use": ", ".join(label for label, _ in rq["primary_pages"]),
                "chapter_4_results": rq["chapter_4_use"],
                "chapter_5_discussion": rq["chapter_5_use"],
                "chapter_6_conclusion": rq["chapter_6_use"],
                "remaining_completion": rq["needed_completion"],
            }
        )
    return pd.DataFrame(rows)


tab_map, tab_rq, tab_chapters, tab_artifacts = st.tabs([
    "RQ Page Map",
    "RQ Detail Navigator",
    "Chapter 4-6 Link",
    "Artifact Outputs",
])

with tab_map:
    st.subheader("Which Dashboard Pages Fulfill Each Research Question")
    st.write(
        "Use this table as the thesis navigation layer. Each RQ points to the Streamlit pages that provide the evidence, "
        "then maps that evidence into Chapter 4 results, Chapter 5 discussion, and Chapter 6 conclusion."
    )
    st.dataframe(rq_rows(), use_container_width=True, height=520)

    st.subheader("Chapter Flow")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=420)
    st.code(CHAPTER_FLOW_MERMAID, language="mermaid")

with tab_rq:
    st.subheader("Research Question Detail Navigator")
    selected_rq = st.selectbox("Choose RQ", [item["rq"] for item in RQ_PAGE_MAP])
    rq = next(item for item in RQ_PAGE_MAP if item["rq"] == selected_rq)

    st.markdown(f"### {rq['rq']} · {rq['theme']}")
    st.write(rq["question"])

    st.markdown("#### Pages To Use")
    page_link_grid(rq["primary_pages"], columns=3)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Chapter 4 Results")
        st.write(rq["chapter_4_use"])
    with c2:
        st.markdown("#### Chapter 5 Discussion")
        st.write(rq["chapter_5_use"])
    with c3:
        st.markdown("#### Chapter 6 Conclusion")
        st.write(rq["chapter_6_use"])

    st.markdown("#### Remaining Completion Task")
    st.warning(rq["needed_completion"])

with tab_chapters:
    st.subheader("Research Questions Linked to Chapter 4, Chapter 5, and Chapter 6")
    render_mermaid(RQ_TO_CHAPTER_MERMAID, height=680)
    st.code(RQ_TO_CHAPTER_MERMAID, language="mermaid")

    st.subheader("Open Chapter Pages")
    page_link_grid(
        [
            ("Chapter 4 Results", "/Chapter_4_Results"),
            ("Chapter 5 Discussion", "/Chapter_5_Discussion"),
            ("Chapter 6 Conclusion", "/Chapter_6_Conclusion"),
            ("Research Questions Visualizer", "/Research_Questions_Visualizer"),
        ],
        columns=4,
    )

    st.markdown("### Chapter Section Summary")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("#### Chapter 4")
        for item in CHAPTER_4_SECTIONS:
            st.write(f"**{item['section']}**")
            st.caption(item["supports"])
    with c5:
        st.markdown("#### Chapter 5")
        for item in CHAPTER_5_SECTIONS:
            st.write(f"**{item['section']}**")
            st.caption(item["supports"])
    with c6:
        st.markdown("#### Chapter 6")
        for item in CHAPTER_6_SECTIONS:
            st.write(f"**{item['section']}**")

with tab_artifacts:
    st.subheader("Generated Result Images and Explanation Bundle")
    report = load_artifact_report()
    if not report:
        st.warning("No artifact report is available yet. Run `python3 generate_research_question_artifacts.py`, then refresh.")
    else:
        st.caption(f"Generated: {report.get('generated_at', 'unknown')}")
        images = report.get("images", [])
        st.dataframe(pd.DataFrame(images), use_container_width=True, height=420)
        if images:
            selected = st.selectbox("Preview image artifact", [entry["title"] for entry in images])
            entry = next(item for item in images if item["title"] == selected)
            image_path = ARTIFACT_JSON.parent / entry["path"]
            if image_path.exists():
                st.image(str(image_path), caption=entry["title"], use_container_width=True)
            st.markdown(f"**What it shows:** {entry['what_it_shows']}")
            st.markdown(f"**Expected metric:** {entry['expected_metrics']}")
            st.markdown(f"**Interpretation:** {entry['interpretation']}")
            st.markdown(f"**If underperforming:** {entry['if_underperforming']}")
