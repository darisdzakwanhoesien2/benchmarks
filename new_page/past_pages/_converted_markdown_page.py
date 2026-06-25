from __future__ import annotations

from pathlib import Path
import re

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
CONVERTED_MARKDOWN_DIR = ROOT / "converted_markdown"


def source_label(*paths: str) -> None:
    joined = " | ".join(paths)
    st.caption(f"Source data: `{joined}`")


def discover_converted_markdown_files() -> list[Path]:
    return sorted(
        path for path in CONVERTED_MARKDOWN_DIR.glob("*.md")
        if not path.name.endswith("_v1.md")
    )


def strip_image_content(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)\n?", "", text)
    text = re.sub(r"\*Figure[^*]*\*\n?", "", text)
    text = re.sub(r"\\begin\{figure\}\[ht\].*?\\end\{figure\}\n?", "", text, flags=re.DOTALL)
    return text


def split_markdown_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    last = 0
    for match in pattern.finditer(text):
        if match.start() > last:
            blocks.append(("markdown", text[last:match.start()]))
        blocks.append((match.group(1) or "", match.group(2).strip()))
        last = match.end()
    if last < len(text):
        blocks.append(("markdown", text[last:]))
    return blocks


def render_markdown_file(path: Path) -> None:
    if not path.exists():
        st.error(f"Missing markdown source: `{path}`")
        return

    text = strip_image_content(path.read_text(encoding="utf-8"))

    for kind, content in split_markdown_blocks(text):
        if not content.strip():
            continue
        if kind:
            st.code(content, language=kind)
        else:
            st.markdown(content)


def friendly_label(path: Path) -> str:
    return path.stem.replace("_", " ").title()


def render_converted_markdown_page(default_filename: str, page_title: str, page_caption: str) -> None:
    markdown_files = discover_converted_markdown_files()
    if not markdown_files:
        st.warning("No Markdown files were found in `converted_markdown`.")
        st.stop()

    file_lookup = {path.name: path for path in markdown_files}
    file_names = list(file_lookup)
    default_index = file_names.index(default_filename) if default_filename in file_lookup else 0

    selected_name = st.selectbox(
        "Converted Markdown File",
        file_names,
        index=default_index,
        format_func=lambda name: f"{friendly_label(file_lookup[name])} ({name})",
    )
    selected_path = file_lookup[selected_name]

    st.title(page_title)
    st.caption(page_caption)
    source_label(f"converted_markdown/{selected_name}")

    c1, c2 = st.columns(2)
    c1.metric("Available markdown files", len(markdown_files))
    c2.metric("Selected file size", f"{selected_path.stat().st_size / 1024:.1f} KB")

    st.divider()
    render_markdown_file(selected_path)
