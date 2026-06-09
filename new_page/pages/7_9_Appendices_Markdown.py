from __future__ import annotations

import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls
from _converted_markdown_page import render_converted_markdown_page


st.set_page_config(page_title="Converted Markdown - Appendices", layout="wide")
apply_page_runtime_controls(__file__)

render_converted_markdown_page(
    default_filename="appendices.md",
    page_title="Converted Markdown - Appendices",
    page_caption="Browse the converted markdown files with `appendices.md` selected by default.",
)
