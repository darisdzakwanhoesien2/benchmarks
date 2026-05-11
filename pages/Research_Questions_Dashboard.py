from pathlib import Path
import sys

import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_FLOW_MERMAID,
    IMAGE_MANIFEST_PATH,
    evidence_rows_df,
    image_evidence_by_rq,
    images_for_rq,
    load_image_manifest,
    mermaid_download_section,
    page_mapping_df,
    render_mermaid,
    research_questions_df,
)


st.set_page_config(page_title="Research Questions Dashboard", layout="wide")
st.title("Research Questions Dashboard")
st.caption("Thesis control room for RQ1-RQ6, evidence status, supporting pages, and archived visual results.")


rq_df = research_questions_df()
evidence_df = evidence_rows_df()
mapping_df = page_mapping_df()
image_manifest, image_df = load_image_manifest()

available_count = int((evidence_df["status"] == "Available").sum())
partial_count = int((evidence_df["status"] == "Partial").sum())
needed_count = int((evidence_df["status"] == "Needed").sum())

metric_cols = st.columns(5)
metric_cols[0].metric("Research questions", len(rq_df))
metric_cols[1].metric("Available evidence", available_count)
metric_cols[2].metric("Partial evidence", partial_count)
metric_cols[3].metric("Needed evidence", needed_count)
metric_cols[4].metric("Archived images", int(image_manifest.get("image_count", len(image_df))))

tab_overview, tab_rq, tab_pages, tab_images, tab_flow = st.tabs(
    ["Overview", "RQ Details", "Page Mapping", "Image Evidence", "Chapter Flow"]
)

with tab_overview:
    st.subheader("Research Question Readiness")
    overview_cols = [
        "rq",
        "theme",
        "evidence_status",
        "short_answer",
    ]
    st.dataframe(rq_df[overview_cols], use_container_width=True, hide_index=True)

    status_counts = rq_df["evidence_status"].value_counts().rename_axis("status").reset_index(name="count")
    st.bar_chart(status_counts, x="status", y="count", use_container_width=True)

    st.subheader("How to Read the Status")
    st.markdown(
        """
        - `Available`: enough implementation evidence exists for a cautious thesis claim.
        - `Partial`: the dashboard supports discussion, but the claim needs another validation layer.
        - `Needed`: the implementation path exists, but the result should not be claimed as complete yet.
        """
    )

with tab_rq:
    selected_rq = st.selectbox("Select research question", rq_df["rq"].tolist())
    row = rq_df.loc[rq_df["rq"] == selected_rq].iloc[0]

    st.subheader(f"{row['rq']} - {row['theme']}")
    st.write(row["question"])
    st.info(row["short_answer"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Evidence status", row["evidence_status"])
    c2.metric("Supporting pages", len(row["supporting_pages"]))
    c3.metric("Needed items", len(row["needed_evidence"]))

    st.subheader("Evidence Checklist")
    st.dataframe(
        evidence_df.loc[evidence_df["rq"] == selected_rq],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Chapter Use")
    st.markdown(f"**Chapter 4 result:** {row['chapter4_result']}")
    st.markdown(f"**Chapter 5 discussion:** {row['chapter5_discussion']}")
    st.markdown(f"**Chapter 6 conclusion:** {row['conclusion']}")

with tab_pages:
    st.subheader("RQ-to-Page Mapping")
    st.dataframe(mapping_df, use_container_width=True, hide_index=True)

    page_counts = mapping_df.groupby("rq", as_index=False)["page"].count().rename(columns={"page": "supporting_page_count"})
    st.bar_chart(page_counts, x="rq", y="supporting_page_count", use_container_width=True)

with tab_images:
    st.subheader("Archived Image Evidence")
    st.caption(f"Manifest: `{IMAGE_MANIFEST_PATH}`")

    if image_df.empty:
        st.warning("No archived image manifest was found yet.")
    else:
        rq_image_counts = image_evidence_by_rq(image_df)
        st.bar_chart(rq_image_counts, x="rq", y="image_count", use_container_width=True)

        selected_image_rq = st.selectbox("Filter images by RQ", rq_df["rq"].tolist(), key="image_rq_filter")
        linked = images_for_rq(image_df, selected_image_rq)

        if linked.empty:
            st.info("No archived images are directly linked to this RQ yet.")
        else:
            st.dataframe(
                linked[
                    [
                        "id",
                        "title",
                        "category",
                        "research_question_links_text",
                        "source_path",
                        "archived_path",
                        "explanation",
                        "thesis_use",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            image_id = st.selectbox("Open image", linked["id"].tolist())
            image_row = linked.loc[linked["id"] == image_id].iloc[0]
            st.image(image_row["archived_absolute_path"], caption=image_row["title"], use_container_width=True)
            st.markdown(f"**Implementation result:** {image_row['explanation']}")
            st.markdown(f"**Thesis use:** {image_row['thesis_use']}")

with tab_flow:
    st.subheader("Research Questions to Thesis Chapters")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=460)
    mermaid_download_section(CHAPTER_FLOW_MERMAID, "research_questions_to_thesis_chapters")
