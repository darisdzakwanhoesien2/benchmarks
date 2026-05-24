from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="A.4 Per-Model Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
VIS = ROOT / "results" / "visualizations"
MANIFEST_PATH = VIS / "tone_climatebert_label_crosstab_full__by_model_manifest.csv"

st.title("A.4 Per-Model Dashboard")
st.caption("Monitor and visualize full-corpus A.4 (tone by ClimateBERT label) split by model.")

if not MANIFEST_PATH.exists():
    st.warning("Manifest not found. Run `3_1_A4_Per_Model_Background_Run` first.")
    st.stop()

manifest = pd.read_csv(MANIFEST_PATH).fillna("")
if manifest.empty:
    st.warning("Manifest is empty. Run the generator again.")
    st.stop()

st.subheader("Model Output Manifest")
st.dataframe(manifest, use_container_width=True, hide_index=True)

manifest_view = manifest.copy()
manifest_view["rows"] = pd.to_numeric(manifest_view["rows"], errors="coerce").fillna(0)
chart_df = manifest_view[["climatebert_model", "rows"]].set_index("climatebert_model")
st.bar_chart(chart_df)

choices = manifest["file"].astype(str).tolist()
selected_file = st.selectbox("Choose model-specific A.4 crosstab", choices, index=0)
selected_path = VIS / selected_file

st.subheader("Selected A.4 Table")
st.caption(f"File: `{selected_path}`")

if not selected_path.exists():
    st.error("Selected crosstab file does not exist.")
    st.stop()

a4_df = pd.read_csv(selected_path).fillna("")
if a4_df.empty:
    st.warning("Selected table is empty.")
    st.stop()

tone_col = "tone" if "tone" in a4_df.columns else a4_df.columns[0]
value_cols = [c for c in a4_df.columns if c != tone_col]
for c in value_cols:
    a4_df[c] = pd.to_numeric(a4_df[c], errors="coerce").fillna(0)

st.dataframe(a4_df, use_container_width=True, hide_index=True, height=300)
st.markdown("**A.4 Visualization (tone x label)**")
st.bar_chart(a4_df.set_index(tone_col))

long_df = a4_df.melt(id_vars=[tone_col], value_vars=value_cols, var_name="climatebert_label", value_name="records")
st.markdown("**Long-format preview**")
st.dataframe(long_df.sort_values([tone_col, "records"], ascending=[True, False]), use_container_width=True, hide_index=True, height=280)
