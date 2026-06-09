from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st

from _page_runtime_controls import apply_page_runtime_controls


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_MD = ROOT / "converted_markdown" / "implementation.md"
IMPLEMENTATION_TEX = (
    ROOT
    / "report_standardized"
    / "Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_"
    / "Chapters"
    / "implementation.tex"
)
IMPLEMENTATION_PAGE = ROOT / "pages" / "7_3_Implementation_Markdown.py"
CH4_MARKDOWN_PAGE = ROOT / "pages" / "4_0_Chapter_4_Markdown_Results.py"
CH4_LIVE_PAGE = ROOT / "pages" / "6_1_Chapter_4_Implementation_Results.py"
CH4_VISUALIZER_PAGES = [
    ROOT / "pages" / "6_5_Chapter_4_Results_Visualizer.py",
    ROOT / "pages" / "6_6_Chapter_4_Results_Visualizer.py",
]
CH4_DRAFTS = [
    ROOT / "chapter4.md",
    ROOT / "chapter4_v2.md",
    ROOT / "chapter4_v3.md",
    ROOT / "chapter4_v4.md",
]

ASSET_DESCRIPTIONS = {
    "implementation.md": "Converted markdown implementation chapter intended for direct reading in Streamlit.",
    "implementation.tex": "Standardized thesis-grade LaTeX implementation chapter with final formatting intent.",
    "7_3_Implementation_Markdown.py": "Minimal Streamlit wrapper that renders the implementation markdown chapter.",
    "4_0_Chapter_4_Markdown_Results.py": "Executable Chapter 4 markdown-results page tied to live repository evidence.",
    "6_1_Chapter_4_Implementation_Results.py": "Full live Chapter 4 implementation-and-results page driven by current artifacts and graph attachments.",
    "chapter4.md": "Early Chapter 4 draft.",
    "chapter4_v2.md": "Condensed Chapter 4 draft variant.",
    "chapter4_v3.md": "Intermediate Chapter 4 draft variant.",
    "chapter4_v4.md": "Current primary Chapter 4 markdown source used by the markdown-results page.",
    "6_5_Chapter_4_Results_Visualizer.py": "Supporting Chapter 4 results visualizer page.",
    "6_6_Chapter_4_Results_Visualizer.py": "Supporting Chapter 4 results visualizer page variant.",
}

ASSET_CLASS = {
    "implementation.md": "Converted markdown",
    "implementation.tex": "Standardized LaTeX",
    "7_3_Implementation_Markdown.py": "Executable wrapper page",
    "4_0_Chapter_4_Markdown_Results.py": "Executable chapter page",
    "6_1_Chapter_4_Implementation_Results.py": "Executable live chapter page",
    "chapter4.md": "Chapter draft",
    "chapter4_v2.md": "Chapter draft",
    "chapter4_v3.md": "Chapter draft",
    "chapter4_v4.md": "Chapter draft",
    "6_5_Chapter_4_Results_Visualizer.py": "Visualizer page",
    "6_6_Chapter_4_Results_Visualizer.py": "Visualizer page",
}


st.set_page_config(page_title="Implementation Documentation And Comparison", layout="wide")
apply_page_runtime_controls(__file__)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+", stripped):
            headings.append(re.sub(r"^#{1,6}\s+", "", stripped))
        elif re.match(r"^\\(section|subsection|subsubsection)\{", stripped):
            headings.append(re.sub(r"^\\(section|subsection|subsubsection)\{(.*)\}$", r"\2", stripped))
    return headings


def asset_metrics(path: Path) -> dict[str, object]:
    text = load_text(path)
    headings = extract_headings(text)
    mermaid_blocks = len(re.findall(r"```mermaid|render_mermaid\(", text))
    tabs = len(re.findall(r"\bst\.tabs\(", text))
    charts = len(re.findall(r"_chart\(|heatmap|image_or_info|render_attachment_cards", text))
    citations = len(re.findall(r"@\w+|\\parencite|\\cite", text))
    return {
        "asset": path.name,
        "path": str(path.relative_to(ROOT)),
        "type": ASSET_CLASS.get(path.name, "Implementation source"),
        "words": len(re.findall(r"\b\w+\b", text)),
        "lines": len(text.splitlines()),
        "headings": len(headings),
        "mermaid_or_render_refs": mermaid_blocks,
        "tabs": tabs,
        "chart_refs": charts,
        "citations": citations,
        "empty": not text.strip(),
        "description": ASSET_DESCRIPTIONS.get(path.name, "Implementation-related source."),
    }


def version_strengths(name: str) -> str:
    mapping = {
        "implementation.md": "Best for straightforward Streamlit reading of the implementation chapter.",
        "implementation.tex": "Best for thesis-grade formatting and the publication-oriented implementation chapter.",
        "7_3_Implementation_Markdown.py": "Best as the simplest delivery layer for the implementation chapter.",
        "4_0_Chapter_4_Markdown_Results.py": "Best for linking the `chapter4_v4.md` narrative to live metrics, charts, and artifact evidence.",
        "6_1_Chapter_4_Implementation_Results.py": "Best for the richest live Chapter 4 surface, including generated narrative, figures, and attachment cards.",
        "chapter4.md": "Useful as an early implementation/results draft for historical comparison.",
        "chapter4_v2.md": "Useful as a shorter, more condensed Chapter 4 variant.",
        "chapter4_v3.md": "Useful as an intermediate Chapter 4 formulation before v4.",
        "chapter4_v4.md": "Best current markdown draft for Chapter 4 and the main source for the markdown-results page.",
        "6_5_Chapter_4_Results_Visualizer.py": "Useful as a focused results-visualization surface.",
        "6_6_Chapter_4_Results_Visualizer.py": "Useful as a focused results-visualization surface variant.",
    }
    return mapping.get(name, "Supporting implementation source.")


def version_gaps(name: str) -> str:
    mapping = {
        "implementation.md": "Less format-rich than the LaTeX version and detached from the live evidence widgets.",
        "implementation.tex": "Harder to browse interactively and not directly tied to live repository widgets.",
        "7_3_Implementation_Markdown.py": "Only a wrapper page; it does not itself contain the implementation content.",
        "4_0_Chapter_4_Markdown_Results.py": "Depends on `chapter4_v4.md` and live result tables rather than being a standalone chapter source.",
        "6_1_Chapter_4_Implementation_Results.py": "Stronger on live evidence than on direct chapter-source simplicity.",
        "chapter4.md": "Older and less polished than the later Chapter 4 variants.",
        "chapter4_v2.md": "Too condensed to serve as the strongest final Chapter 4 narrative.",
        "chapter4_v3.md": "Intermediate state; superseded by v4 as the main markdown source.",
        "chapter4_v4.md": "Still separate from the standardized LaTeX chapter and the live docx-translated page.",
        "6_5_Chapter_4_Results_Visualizer.py": "Focused view, not a full implementation chapter.",
        "6_6_Chapter_4_Results_Visualizer.py": "Focused view, not a full implementation chapter.",
    }
    return mapping.get(name, "Needs pairing with other implementation assets.")


main_assets = [
    IMPLEMENTATION_MD,
    IMPLEMENTATION_TEX,
    IMPLEMENTATION_PAGE,
    CH4_MARKDOWN_PAGE,
    CH4_LIVE_PAGE,
    *CH4_DRAFTS,
    *CH4_VISUALIZER_PAGES,
]
assets_df = pd.DataFrame([asset_metrics(path) for path in main_assets])

st.title("Implementation Documentation And Comparison")
st.caption(
    "Repository documentation page for implementation assets: markdown and LaTeX chapters, Chapter 4 draft variants, and live implementation/results pages."
)

st.write(
    "The implementation material in this repo is not a single file. It is split across a converted implementation chapter, a standardized LaTeX chapter, "
    "multiple Chapter 4 markdown drafts, and live Streamlit pages that render current repository evidence."
)

tab_overview, tab_compare, tab_ch4, tab_reader = st.tabs(
    ["Overview", "Version Comparison", "Chapter 4 Drafts", "Source Reader"]
)

with tab_overview:
    st.header("Implementation Asset Inventory")
    st.dataframe(
        assets_df[["asset", "type", "words", "headings", "tabs", "chart_refs", "citations", "path"]],
        use_container_width=True,
        hide_index=True,
        height=320,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Narrative Sources")
        for name in ["implementation.md", "implementation.tex", "chapter4.md", "chapter4_v2.md", "chapter4_v3.md", "chapter4_v4.md"]:
            row = assets_df[assets_df["asset"] == name].iloc[0]
            st.markdown(f"### {name}")
            st.write(row["description"])
            st.write(f"Primary value: {version_strengths(name)}")
            st.write(f"Current gap: {version_gaps(name)}")
    with c2:
        st.subheader("Executable Pages")
        for name in [
            "7_3_Implementation_Markdown.py",
            "4_0_Chapter_4_Markdown_Results.py",
            "6_1_Chapter_4_Implementation_Results.py",
            "6_5_Chapter_4_Results_Visualizer.py",
            "6_6_Chapter_4_Results_Visualizer.py",
        ]:
            row = assets_df[assets_df["asset"] == name].iloc[0]
            st.markdown(f"### {name}")
            st.write(row["description"])
            st.write(f"Primary value: {version_strengths(name)}")
            st.write(f"Current gap: {version_gaps(name)}")

with tab_compare:
    st.header("Version Comparison")
    compare_df = assets_df.copy()
    compare_df["strength"] = compare_df["asset"].map(version_strengths)
    compare_df["gap"] = compare_df["asset"].map(version_gaps)
    st.dataframe(
        compare_df[["asset", "type", "words", "headings", "tabs", "chart_refs", "citations", "strength", "gap"]],
        use_container_width=True,
        hide_index=True,
        height=360,
    )

    st.subheader("Direct Comparison")
    compare_options = {
        path.name: path
        for path in [
            IMPLEMENTATION_MD,
            IMPLEMENTATION_TEX,
            *CH4_DRAFTS,
            CH4_MARKDOWN_PAGE,
            CH4_LIVE_PAGE,
        ]
    }
    left_col, right_col = st.columns(2)
    with left_col:
        left_asset = st.selectbox("Left asset", list(compare_options.keys()), index=0)
    with right_col:
        right_asset = st.selectbox("Right asset", list(compare_options.keys()), index=1)

    left_text = load_text(compare_options[left_asset])
    right_text = load_text(compare_options[right_asset])
    left_headings = extract_headings(left_text)
    right_headings = extract_headings(right_text)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### {left_asset}")
        st.write(version_strengths(left_asset))
        st.write(version_gaps(left_asset))
        st.code("\n".join(left_headings[:30]) or "No headings found.", language="text")
    with c2:
        st.markdown(f"### {right_asset}")
        st.write(version_strengths(right_asset))
        st.write(version_gaps(right_asset))
        st.code("\n".join(right_headings[:30]) or "No headings found.", language="text")

    shared = sorted(set(left_headings).intersection(right_headings))
    st.subheader("Shared Structure")
    if shared:
        st.code("\n".join(shared[:30]), language="text")
    else:
        st.info("No direct heading overlap detected.")

with tab_ch4:
    st.header("Chapter 4 Draft Progression")
    draft_df = assets_df[assets_df["asset"].isin([path.name for path in CH4_DRAFTS])].copy()
    draft_df["strength"] = draft_df["asset"].map(version_strengths)
    draft_df["gap"] = draft_df["asset"].map(version_gaps)
    st.dataframe(
        draft_df[["asset", "words", "headings", "strength", "gap"]],
        use_container_width=True,
        hide_index=True,
        height=240,
    )

    st.info(
        "Interpretation: `chapter4_v4.md` is the current strongest markdown chapter source. "
        "The older `chapter4.md`, `chapter4_v2.md`, and `chapter4_v3.md` are still useful for tracing how the implementation/results narrative evolved."
    )

    selected_draft = st.selectbox("Inspect Chapter 4 draft", [path.name for path in CH4_DRAFTS], index=3)
    selected_path = ROOT / selected_draft
    selected_text = load_text(selected_path)
    st.code(selected_text[:22000] if selected_text else "# empty", language="markdown")

with tab_reader:
    st.header("Source Reader")
    readable = {path.name: path for path in main_assets}
    selected_asset = st.selectbox("Read source file", list(readable.keys()), index=0)
    selected_path = readable[selected_asset]
    selected_text = load_text(selected_path)

    preview_chars = st.slider("Preview characters", min_value=3000, max_value=40000, value=16000, step=1000)
    language = "python" if selected_path.suffix == ".py" else "markdown" if selected_path.suffix == ".md" else "tex"
    st.code(selected_text[:preview_chars] if selected_text else "% empty file", language=language)
    if len(selected_text) > preview_chars:
        st.caption("Preview truncated.")
