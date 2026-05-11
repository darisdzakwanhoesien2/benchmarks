from pathlib import Path
import sys

import streamlit as st

PAGE_DIR = Path(__file__).resolve().parent
if str(PAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PAGE_DIR))

from _rq_thesis_content import (
    CHAPTER_FLOW_MERMAID,
    chapter4_results_df,
    image_evidence_by_rq,
    images_for_rq,
    load_image_manifest,
    render_mermaid,
    research_questions_df,
)


st.set_page_config(page_title="Chapter 4 Results", layout="wide")
st.title("Chapter 4 Results")
st.caption("Results implementation page: what to present, which dashboard pages support it, and which archived images can be cited.")


rq_df = research_questions_df()
results_df = chapter4_results_df()
_, image_df = load_image_manifest()

tab_results, tab_by_rq, tab_images, tab_diagram = st.tabs(
    ["Results Sections", "Results by RQ", "Supporting Images", "Diagram"]
)

with tab_results:
    st.subheader("Chapter 4 Results Structure")
    st.dataframe(results_df, use_container_width=True, hide_index=True)

    selected_section = st.selectbox("Open result section", results_df["section"].tolist())
    section = results_df.loc[results_df["section"] == selected_section].iloc[0]
    st.markdown(f"**Linked RQ:** {section['rq']}")
    st.markdown(f"**Result to present:** {section['result']}")
    st.markdown(f"**Supporting pages:** `{section['supporting_pages']}`")
    st.markdown(f"**How to write it in Chapter 4:** {section['use_in_results']}")

with tab_by_rq:
    st.subheader("Research-Question Results")
    selected_rq = st.selectbox("Select RQ", rq_df["rq"].tolist(), key="chapter4_rq")
    row = rq_df.loc[rq_df["rq"] == selected_rq].iloc[0]

    st.info(row["chapter4_result"])
    st.markdown(f"**Evidence status:** {row['evidence_status']}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Available Evidence")
        for item in row["available_evidence"]:
            st.markdown(f"- {item}")
    with c2:
        st.subheader("Pages to Use")
        for page in row["supporting_pages"]:
            st.markdown(f"- `{page}`")

    st.subheader("Partial or Needed Evidence")
    for item in row["partial_evidence"]:
        st.markdown(f"- Partial: {item}")
    for item in row["needed_evidence"]:
        st.markdown(f"- Needed: {item}")

with tab_images:
    st.subheader("Image Outputs That Support Chapter 4")

    if image_df.empty:
        st.warning("No image archive found yet.")
    else:
        counts = image_evidence_by_rq(image_df)
        st.bar_chart(counts, x="rq", y="image_count", use_container_width=True)

        selected_rq = st.selectbox("Select RQ image evidence", rq_df["rq"].tolist(), key="chapter4_image_rq")
        linked = images_for_rq(image_df, selected_rq)

        if linked.empty:
            st.info("No images are currently linked to this RQ.")
        else:
            for _, image_row in linked.iterrows():
                with st.expander(f"{image_row['id']} - {image_row['title']}", expanded=False):
                    st.image(image_row["archived_absolute_path"], caption=image_row["title"], use_container_width=True)
                    st.markdown(f"**Category:** {image_row['category']}")
                    st.markdown(f"**Result explanation:** {image_row['explanation']}")
                    st.markdown(f"**Use in Chapter 4:** {image_row['thesis_use']}")
                    st.caption(f"Source: `{image_row['source_path']}`")

with tab_diagram:
    st.subheader("Chapter 4 Position in Thesis Flow")
    render_mermaid(CHAPTER_FLOW_MERMAID, height=460)
