from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import streamlit as st

from _page_runtime_controls import apply_page_runtime_controls


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import render_mermaid  # noqa: E402


st.set_page_config(page_title="Methodology Documentation And Comparison", layout="wide")
apply_page_runtime_controls(__file__)

METHODOLOGY_DOC = ROOT / "methodology_pipeline_mermaid.md"
CHAPTER_PAGE = ROOT / "pages" / "3_4_Chapter_3_Methodology.py"
CHAPTER_VERSIONS = [
    ROOT / "chapter3_v2.md",
    ROOT / "chapter3_v3.md",
    ROOT / "chapter3_v4.md",
]
P1_DIR = ROOT / "documentation" / "p1_thesis_app"
P1_METHOD_FILES = sorted(P1_DIR.glob("03_*.tex"))

ASSET_DESCRIPTIONS = {
    "chapter3_v2.md": "Narrative methodology draft focused on the executable pipeline, dataset layers, preprocessing, extraction, and validation limits.",
    "chapter3_v3.md": "Page-by-page checklist template that documents how a methodology chapter should be structured rather than reporting this project's final method directly.",
    "chapter3_v4.md": "Expanded methodology draft with stronger chapter-ready prose and thesis framing, currently used by the executable Chapter 3 page.",
    "methodology_pipeline_mermaid.md": "Visual specification of the methodology spine, execution pipeline, research-question map, and validation loop.",
    "3_4_Chapter_3_Methodology.py": "Streamlit implementation that renders the methodology chapter and ties it to live repository evidence.",
}

ASSET_CLASS = {
    "chapter3_v2.md": "Narrative draft",
    "chapter3_v3.md": "Structure template",
    "chapter3_v4.md": "Narrative draft",
    "methodology_pipeline_mermaid.md": "Diagram spec",
    "3_4_Chapter_3_Methodology.py": "Executable page",
}


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def heading_lines(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+", stripped):
            headings.append(re.sub(r"^#{1,6}\s+", "", stripped))
        elif re.match(r"^\d+\.\d+(\.\d+)?\s+", stripped):
            headings.append(stripped)
    return headings


def mermaid_blocks(text: str) -> list[str]:
    matches = re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL)
    return [match.strip() for match in matches]


def asset_metrics(path: Path) -> dict[str, object]:
    text = load_text(path)
    words = len(re.findall(r"\b\w+\b", text))
    lines = len(text.splitlines())
    headings = heading_lines(text)
    mermaids = mermaid_blocks(text)
    checklist_items = len(re.findall(r"^\* \[ \]", text, re.MULTILINE))
    return {
        "asset": path.name,
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "type": ASSET_CLASS.get(path.name, "Chapter scaffold" if path.suffix == ".tex" else "Other"),
        "words": words,
        "lines": lines,
        "headings": len(headings),
        "mermaid_blocks": len(mermaids),
        "checklist_items": checklist_items,
        "empty": not text.strip(),
        "description": ASSET_DESCRIPTIONS.get(path.name, "Reserved methodology scaffold file."),
    }


def chapter_versions_table() -> pd.DataFrame:
    rows = []
    for path in [*CHAPTER_VERSIONS, METHODOLOGY_DOC, CHAPTER_PAGE]:
        rows.append(asset_metrics(path))
    return pd.DataFrame(rows)


def p1_methodology_table() -> pd.DataFrame:
    rows = []
    for path in P1_METHOD_FILES:
        metrics = asset_metrics(path)
        metrics["section_slot"] = path.stem
        rows.append(metrics)
    return pd.DataFrame(rows)


def version_strengths(name: str) -> str:
    mapping = {
        "chapter3_v2.md": "Best as the concise research-method narrative. It explains the unit of analysis, weak-label posture, preprocessing logic, and current validation limits clearly.",
        "chapter3_v3.md": "Best as a structural rubric. It is useful for completeness checking because it spells out what each methodology page should contain.",
        "chapter3_v4.md": "Best as the current thesis-facing narrative. It is fuller than v2 and aligned with the live methodology page already in `pages/3_4_Chapter_3_Methodology.py`.",
        "methodology_pipeline_mermaid.md": "Best as the visual architecture source. It contains the highest-signal diagrams for the methodology spine, execution flow, and validation loop.",
        "3_4_Chapter_3_Methodology.py": "Best as the executable evidence surface. It connects chapter text to data bundles, charts, and artifact inventory.",
    }
    return mapping.get(name, "Reserved scaffold file.")


def version_gaps(name: str) -> str:
    mapping = {
        "chapter3_v2.md": "Shorter than v4 and weaker on chapter-polish, figures, and explicit structural checklist coverage.",
        "chapter3_v3.md": "Not a final methodology chapter. It documents how to write one, but does not itself present the final project method.",
        "chapter3_v4.md": "Still separate from the `documentation/p1_thesis_app/03_*.tex` scaffold, so the LaTeX slots remain unpopulated.",
        "methodology_pipeline_mermaid.md": "Strong on diagrams, weaker on chapter prose and direct thesis-ready paragraphs.",
        "3_4_Chapter_3_Methodology.py": "Explains the live chapter surface, but depends on external markdown and result tables rather than standing alone as documentation.",
    }
    return mapping.get(name, "Empty placeholder with no content yet.")


def summary_bullets() -> None:
    st.write("This page documents the methodology assets already present in the repository and compares how they differ in role.")
    st.write(
        "The main methodology set in this repo is not a single file. It is split across narrative chapter drafts, diagram specifications, "
        "an executable Streamlit page, and a still-empty `03_*.tex` publication scaffold."
    )


def render_asset_card(row: pd.Series) -> None:
    st.markdown(f"### {row['asset']}")
    st.write(row["description"])
    st.write(f"Path: `{row['path']}`")
    st.write(f"Type: `{row['type']}`")
    st.write(f"Words: **{int(row['words']):,}** | Headings: **{int(row['headings'])}** | Mermaid blocks: **{int(row['mermaid_blocks'])}**")
    st.write(f"Primary value: {version_strengths(str(row['asset']))}")
    st.write(f"Current gap: {version_gaps(str(row['asset']))}")


st.title("Methodology Documentation And Comparison")
st.caption(
    "Repository documentation page for the methodology assets: chapter drafts, mermaid pipeline spec, executable Streamlit page, and Chapter 3 scaffold files."
)

summary_bullets()

versions_df = chapter_versions_table()
p1_df = p1_methodology_table()

tab_overview, tab_compare, tab_scaffold, tab_mermaid, tab_reader = st.tabs(
    ["Overview", "Version Comparison", "03_x Scaffold", "Mermaid Diagrams", "Source Reader"]
)

with tab_overview:
    st.header("Methodology Asset Inventory")
    st.dataframe(
        versions_df[["asset", "type", "words", "headings", "mermaid_blocks", "checklist_items", "path"]],
        use_container_width=True,
        hide_index=True,
        height=260,
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Current Interpretation")
        st.info(
            "The strongest current methodology pair is `chapter3_v4.md` plus `methodology_pipeline_mermaid.md`. "
            "The first gives thesis-style prose, while the second gives visual architecture and validation logic."
        )
    with right:
        st.subheader("Main Structural Gap")
        empty_slots = int(p1_df["empty"].sum()) if not p1_df.empty else 0
        st.warning(
            f"The `documentation/p1_thesis_app/03_*.tex` scaffold exists, but {empty_slots} methodology section slots are still empty."
        )

    st.subheader("Asset Roles")
    for _, row in versions_df.iterrows():
        render_asset_card(row)

with tab_compare:
    st.header("Version Comparison")
    compare_df = versions_df.copy()
    compare_df["strength"] = compare_df["asset"].map(version_strengths)
    compare_df["gap"] = compare_df["asset"].map(version_gaps)
    st.dataframe(
        compare_df[["asset", "type", "words", "headings", "mermaid_blocks", "checklist_items", "strength", "gap"]],
        use_container_width=True,
        hide_index=True,
        height=320,
    )

    st.subheader("Direct Comparison")
    options = [path.name for path in [*CHAPTER_VERSIONS, METHODOLOGY_DOC]]
    sel_a, sel_b = st.columns(2)
    with sel_a:
        asset_a = st.selectbox("Left asset", options, index=0)
    with sel_b:
        asset_b = st.selectbox("Right asset", options, index=min(2, len(options) - 1))

    asset_lookup = {path.name: path for path in [*CHAPTER_VERSIONS, METHODOLOGY_DOC]}
    a_text = load_text(asset_lookup[asset_a])
    b_text = load_text(asset_lookup[asset_b])
    a_headings = heading_lines(a_text)
    b_headings = heading_lines(b_text)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### {asset_a}")
        st.write(version_strengths(asset_a))
        st.write(version_gaps(asset_a))
        st.write("Headings:")
        st.code("\n".join(a_headings[:20]) or "No headings found.", language="text")
    with c2:
        st.markdown(f"### {asset_b}")
        st.write(version_strengths(asset_b))
        st.write(version_gaps(asset_b))
        st.write("Headings:")
        st.code("\n".join(b_headings[:20]) or "No headings found.", language="text")

    overlap = sorted(set(a_headings).intersection(b_headings))
    st.subheader("Heading Overlap")
    if overlap:
        st.code("\n".join(overlap[:30]), language="text")
    else:
        st.info("No direct heading overlap found between the selected assets.")

with tab_scaffold:
    st.header("Chapter 3 LaTeX Scaffold Status")
    if p1_df.empty:
        st.info("No `03_*.tex` methodology scaffold files were found.")
    else:
        scaffold_view = p1_df.copy()
        scaffold_view["status"] = scaffold_view["empty"].map(lambda value: "Empty placeholder" if value else "Has content")
        st.dataframe(
            scaffold_view[["section_slot", "status", "words", "lines", "path"]],
            use_container_width=True,
            hide_index=True,
            height=320,
        )
        st.write(
            "Interpretation: the repository already has strong methodology prose in markdown and a live Streamlit implementation, "
            "but the publication-oriented `03_*.tex` chapter scaffold is not yet populated."
        )

        selected_slot = st.selectbox("Inspect scaffold file", scaffold_view["section_slot"].tolist(), index=0)
        slot_path = P1_DIR / f"{selected_slot}.tex"
        slot_text = load_text(slot_path)
        st.code(slot_text if slot_text.strip() else "% empty file", language="tex")

with tab_mermaid:
    st.header("Methodology Diagram Documentation")
    mermaid_text = load_text(METHODOLOGY_DOC)
    diagrams = mermaid_blocks(mermaid_text)

    if not diagrams:
        st.info("No mermaid diagrams found in `methodology_pipeline_mermaid.md`.")
    else:
        diagram_titles = re.findall(r"##\s+\d+\.\s+(.*)", mermaid_text)
        title_options = []
        for idx, diagram in enumerate(diagrams):
            label = diagram_titles[idx] if idx < len(diagram_titles) else f"Diagram {idx + 1}"
            title_options.append((label, diagram))

        selected_label = st.selectbox("Choose methodology diagram", [label for label, _ in title_options], index=0)
        selected_diagram = next(diagram for label, diagram in title_options if label == selected_label)
        render_mermaid(selected_diagram, height=640)

        st.subheader("Diagram Interpretation")
        interpretation = {
            "Methodology Spine": "Shows the logic from motivation and research gaps to research questions, method layers, validation, and final thesis claims.",
            "End-To-End Execution Pipeline": "Documents the operational flow from PDF corpus through OCR, extraction, ABSA normalization, evidence tables, and outputs.",
            "Research Question To Artifact Map": "Explains which artifacts and figures answer which research questions.",
            "Validation And Reliability Loop": "Shows that validation is iterative: extraction feeds annotation, diagnostics, ontology checks, and refinement.",
        }
        for prefix, text in interpretation.items():
            if selected_label.startswith(prefix):
                st.info(text)
                break

with tab_reader:
    st.header("Source Reader")
    readable_assets = {
        path.name: path for path in [*CHAPTER_VERSIONS, METHODOLOGY_DOC, CHAPTER_PAGE, *P1_METHOD_FILES]
    }
    selected_asset = st.selectbox("Read source file", list(readable_assets.keys()), index=0)
    selected_path = readable_assets[selected_asset]
    selected_text = load_text(selected_path)

    preview_chars = st.slider("Preview characters", min_value=3000, max_value=40000, value=16000, step=1000)
    language = "python" if selected_path.suffix == ".py" else "markdown" if selected_path.suffix == ".md" else "tex"
    st.code(selected_text[:preview_chars] if selected_text else "% empty file", language=language)
    if len(selected_text) > preview_chars:
        st.caption("Preview truncated.")
