import streamlit as st

from _rq_thesis_content import (
    CHAPTER_FLOW_MERMAID,
    GENERAL_DISCUSSION,
    LIMITATIONS,
    evidence_rows_df,
    images_for_rq,
    load_image_manifest,
    render_mermaid,
    research_questions_df,
)


st.set_page_config(page_title="Chapter 5 Discussion", layout="wide")
st.title("Chapter 5 Discussion")
st.caption("Discussion implementation page: interpret each RQ, state limitations clearly, and avoid over-claiming.")


rq_df = research_questions_df()
evidence_df = evidence_rows_df()
_, image_df = load_image_manifest()

tab_discussion, tab_status, tab_images, tab_general, tab_flow = st.tabs(
    ["RQ Discussion", "Evidence Wording", "Image Discussion", "General Discussion", "Diagram"]
)

with tab_discussion:
    selected_rq = st.selectbox("Select research question", rq_df["rq"].tolist())
    row = rq_df.loc[rq_df["rq"] == selected_rq].iloc[0]

    st.subheader(f"{row['rq']} - {row['theme']}")
    st.write(row["question"])
    st.markdown(f"**Interpretation:** {row['chapter5_discussion']}")
    st.markdown(f"**Claim status:** {row['evidence_status']}")

    st.subheader("How to Discuss the Result")
    if row["evidence_status"] == "Available":
        st.success("Available evidence: this RQ can support a cautious thesis claim now.")
    elif row["evidence_status"] == "Partial":
        st.warning("Partial evidence: discuss the result as useful, but keep accuracy/generalization claims cautious.")
    else:
        st.error("Needed evidence: describe the implementation path and gap, not a completed finding.")

    st.subheader("Limitation Paragraph Ingredients")
    for item in row["needed_evidence"]:
        st.markdown(f"- {item}")

with tab_status:
    st.subheader("Available / Partial / Needed Wording")
    st.dataframe(evidence_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
        **Available wording:** "The dashboard demonstrates..." or "The current evidence supports..."

        **Partial wording:** "The current result suggests..." or "The dashboard provides exploratory evidence..."

        **Needed wording:** "A stronger claim requires..." or "This remains a validation gap because..."
        """
    )

with tab_images:
    st.subheader("How to Discuss Archived Images")

    if image_df.empty:
        st.warning("No image archive found yet.")
    else:
        selected_rq = st.selectbox("Select RQ", rq_df["rq"].tolist(), key="discussion_image_rq")
        linked = images_for_rq(image_df, selected_rq)

        if linked.empty:
            st.info("No linked images for this RQ.")
        else:
            for _, image_row in linked.iterrows():
                with st.expander(f"{image_row['title']}"):
                    st.image(image_row["archived_absolute_path"], caption=image_row["title"], use_container_width=True)
                    st.markdown(f"**What this image shows:** {image_row['explanation']}")
                    st.markdown(f"**Discussion use:** {image_row['thesis_use']}")

with tab_general:
    st.subheader("General Discussion")
    for paragraph in GENERAL_DISCUSSION:
        st.write(paragraph)

    st.subheader("Cross-Cutting Limitations")
    for limitation in LIMITATIONS:
        st.markdown(f"- {limitation}")

    st.subheader("Recommended Discussion Framing")
    st.info(
        "Frame the thesis as a reproducible ESG ABSA framework with exploratory empirical outputs. "
        "Reserve strong accuracy, agreement, and generalization claims for the expert-labeled and balanced-model validation layer."
    )

with tab_flow:
    st.subheader("Discussion Position in Thesis Flow")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=460)
