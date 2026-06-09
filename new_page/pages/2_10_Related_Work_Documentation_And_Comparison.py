from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st

from _page_runtime_controls import apply_page_runtime_controls


ROOT = Path(__file__).resolve().parents[1]
RELATED_MD = ROOT / "converted_markdown" / "relatedwork.md"
RELATED_PAGE = ROOT / "pages" / "7_2_Related_Work_Markdown.py"
RELATED_TEX = (
    ROOT
    / "report_standardized"
    / "Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_"
    / "Chapters"
    / "relatedwork.tex"
)
P1_DIR = ROOT / "documentation" / "p1_thesis_app"
P1_RELATED_FILES = sorted(P1_DIR.glob("02_*.tex"))

ASSET_DESCRIPTIONS = {
    "relatedwork.md": "Converted markdown version of the Related Work chapter, organized into Chapter 2 topic sections and intended for browsing in Streamlit.",
    "7_2_Related_Work_Markdown.py": "Minimal Streamlit wrapper that renders the converted Related Work markdown page.",
    "relatedwork.tex": "Standardized LaTeX chapter file with richer formatting, tables, citations, and publication-oriented structure.",
}

ASSET_CLASS = {
    "relatedwork.md": "Converted markdown",
    "7_2_Related_Work_Markdown.py": "Executable page",
    "relatedwork.tex": "Standardized LaTeX",
}


st.set_page_config(page_title="Related Work Documentation And Comparison", layout="wide")
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


def chapter2_sections(text: str) -> list[str]:
    sections = []
    for heading in extract_headings(text):
        if re.match(r"^2(\.\d+)?", heading) or "Chapter 2" in heading or "Related Work" in heading:
            sections.append(heading)
    return sections


def asset_metrics(path: Path) -> dict[str, object]:
    text = load_text(path)
    headings = extract_headings(text)
    table_count = len(re.findall(r"Table:|\\begin\{table\}", text))
    cite_count = len(re.findall(r"@\w+|\\parencite|\\cite", text))
    return {
        "asset": path.name,
        "path": str(path.relative_to(ROOT)),
        "type": ASSET_CLASS.get(path.name, "Chapter 2 source"),
        "words": len(re.findall(r"\b\w+\b", text)),
        "lines": len(text.splitlines()),
        "headings": len(headings),
        "chapter2_sections": len(chapter2_sections(text)),
        "tables": table_count,
        "citations": cite_count,
        "empty": not text.strip(),
        "description": ASSET_DESCRIPTIONS.get(path.name, "Chapter 2 related-work source fragment."),
    }


def version_strengths(name: str) -> str:
    mapping = {
        "relatedwork.md": "Best for fast reading in Streamlit. It gives the clearest readable chapter flow and preserves the thematic Chapter 2 section structure.",
        "relatedwork.tex": "Best for thesis-grade formatting. It contains richer LaTeX structure, larger table content, and publication-style citation formatting.",
        "7_2_Related_Work_Markdown.py": "Best as the executable delivery layer. It exposes the converted markdown in the multipage app with minimal maintenance cost.",
    }
    if name.startswith("02_"):
        return "Best as Chapter 2 source scaffolding. These files break the literature review into smaller thematic source units."
    return mapping.get(name, "Supporting related-work source.")


def version_gaps(name: str) -> str:
    mapping = {
        "relatedwork.md": "Weaker on formatting fidelity, citation control, and table layout than the LaTeX version.",
        "relatedwork.tex": "Harder to browse quickly in Streamlit and less convenient for interactive reading than markdown.",
        "7_2_Related_Work_Markdown.py": "Only a wrapper page. It does not itself contain the literature content.",
    }
    if name.startswith("02_"):
        return "Useful as source fragments, but fragmented by design and not a standalone Related Work chapter."
    return mapping.get(name, "Needs contextual pairing with other assets.")


def p1_related_table() -> pd.DataFrame:
    rows = []
    for path in P1_RELATED_FILES:
        metrics = asset_metrics(path)
        metrics["section_slot"] = path.stem
        rows.append(metrics)
    return pd.DataFrame(rows)


main_assets = [RELATED_MD, RELATED_TEX, RELATED_PAGE]
main_df = pd.DataFrame([asset_metrics(path) for path in main_assets])
p1_df = p1_related_table()

st.title("Related Work Documentation And Comparison")
st.caption(
    "Repository documentation page for the Related Work assets: converted markdown, standardized LaTeX chapter, executable Streamlit page, and Chapter 2 source fragments."
)

st.write(
    "The related-work material in this repo is split across a readable markdown chapter, a richer standardized LaTeX chapter, "
    "a lightweight Streamlit wrapper page, and the `documentation/p1_thesis_app/02_*.tex` source set."
)

tab_overview, tab_compare, tab_sections, tab_reader = st.tabs(
    ["Overview", "Version Comparison", "02_x Source Set", "Source Reader"]
)

with tab_overview:
    st.header("Related Work Asset Inventory")
    st.dataframe(
        main_df[["asset", "type", "words", "headings", "chapter2_sections", "tables", "citations", "path"]],
        use_container_width=True,
        hide_index=True,
        height=220,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("What Each Asset Does")
        for _, row in main_df.iterrows():
            st.markdown(f"### {row['asset']}")
            st.write(row["description"])
            st.write(f"Primary value: {version_strengths(str(row['asset']))}")
            st.write(f"Current gap: {version_gaps(str(row['asset']))}")
    with c2:
        st.subheader("Current Interpretation")
        st.info(
            "The best reading pair is `converted_markdown/relatedwork.md` plus the standardized `relatedwork.tex`. "
            "The markdown version is easiest to navigate, while the LaTeX version is the richer thesis-format source."
        )
        st.write(
            "The `02_*.tex` files are the underlying Chapter 2 source fragments. They are important because they reveal how the literature review is decomposed before standardization."
        )

with tab_compare:
    st.header("Version Comparison")
    compare_df = main_df.copy()
    compare_df["strength"] = compare_df["asset"].map(version_strengths)
    compare_df["gap"] = compare_df["asset"].map(version_gaps)
    st.dataframe(
        compare_df[["asset", "type", "words", "headings", "chapter2_sections", "tables", "citations", "strength", "gap"]],
        use_container_width=True,
        hide_index=True,
        height=260,
    )

    st.subheader("Direct Comparison")
    option_map = {path.name: path for path in [RELATED_MD, RELATED_TEX]}
    left_col, right_col = st.columns(2)
    with left_col:
        left_asset = st.selectbox("Left asset", list(option_map.keys()), index=0)
    with right_col:
        right_asset = st.selectbox("Right asset", list(option_map.keys()), index=1)

    left_text = load_text(option_map[left_asset])
    right_text = load_text(option_map[right_asset])
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

with tab_sections:
    st.header("Chapter 2 Source Fragment Set")
    if p1_df.empty:
        st.info("No `02_*.tex` files found under `documentation/p1_thesis_app`.")
    else:
        view = p1_df.copy()
        view["status"] = view["empty"].map(lambda value: "Empty" if value else "Has content")
        st.dataframe(
            view[["section_slot", "status", "words", "headings", "tables", "citations", "path"]],
            use_container_width=True,
            hide_index=True,
            height=320,
        )

        st.write(
            "Interpretation: the Chapter 2 literature review is already decomposed into nine source fragments (`02_01.tex` to `02_09.tex`). "
            "These are not duplicates; they are the modular source set behind the larger Related Work chapter."
        )

        selected_slot = st.selectbox("Inspect Chapter 2 source file", view["section_slot"].tolist(), index=0)
        selected_path = P1_DIR / f"{selected_slot}.tex"
        selected_text = load_text(selected_path)
        st.code(selected_text[:18000] if selected_text else "% empty file", language="tex")

with tab_reader:
    st.header("Source Reader")
    readable = {path.name: path for path in [RELATED_MD, RELATED_TEX, RELATED_PAGE, *P1_RELATED_FILES]}
    selected_asset = st.selectbox("Read source file", list(readable.keys()), index=0)
    selected_path = readable[selected_asset]
    selected_text = load_text(selected_path)

    preview_chars = st.slider("Preview characters", min_value=3000, max_value=40000, value=16000, step=1000)
    language = "python" if selected_path.suffix == ".py" else "markdown" if selected_path.suffix == ".md" else "tex"
    st.code(selected_text[:preview_chars] if selected_text else "% empty file", language=language)
    if len(selected_text) > preview_chars:
        st.caption("Preview truncated.")
