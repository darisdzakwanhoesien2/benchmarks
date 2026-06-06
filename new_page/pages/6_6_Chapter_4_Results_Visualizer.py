from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _chapter4_results_visualizer_shared import render_long_page
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Chapter 4 Results Visualizer Long Page", layout="wide")
apply_page_runtime_controls(__file__)

render_long_page()
