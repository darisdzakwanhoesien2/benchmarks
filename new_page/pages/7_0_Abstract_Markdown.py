from __future__ import annotations

import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls
from _converted_markdown_page import render_converted_markdown_page


st.set_page_config(page_title="Converted Markdown - Abstract", layout="wide")
apply_page_runtime_controls(__file__)

render_converted_markdown_page(
    default_filename="abstract.md",
    page_title="Converted Markdown - Abstract",
    page_caption="Browse the converted markdown files with `abstract.md` selected by default.",
)
