from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="A.4 Regenerate (Tone x ClimateBERT)", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "results" / "revision_analysis"
VIS = ROOT / "results" / "visualizations"

SRC = REV / "climatebert_record_batch_import.csv"
OUT_CROSSTAB = VIS / "tone_climatebert_label_crosstab.csv"
OUT_CROSSTAB_FULL = VIS / "tone_climatebert_label_crosstab_full.csv"
OUT_PNG = VIS / "climatebert_label_by_tone.png"


def normalize_label(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return "missing"
    lowered = text.lower()
    if lowered in {"nan", "none", "null", "n/a", "na", "undefined"}:
        return "missing"
    return text


def normalize_tone(value: object) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "missing"
    if text in {"nan", "null", "n/a", "na", "undefined"}:
        return "missing"
    if text in {"commitment", "action", "outcome", "none", "unknown", "missing"}:
        return text
    # Sometimes tones get stored as multi-label strings; pick first substantive one.
    if "," in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        for key in ["commitment", "action", "outcome", "none", "unknown"]:
            if key in parts:
                return key
        return parts[0] if parts else "missing"
    return text


def pick_label_col(df: pd.DataFrame) -> str:
    for col in ["climatebert_label", "label", "top_label", "climate_commitment_label"]:
        if col in df.columns and df[col].astype(str).str.strip().ne("").any():
            return col
    return ""


def regenerate_a4(keep_top_labels: int | None = None) -> dict[str, object]:
    if not SRC.exists():
        raise FileNotFoundError(f"Missing source CSV: {SRC}")
    df = pd.read_csv(SRC).fillna("")
    if "tone_pred" not in df.columns:
        raise ValueError("Missing required column: tone_pred")
    label_col = pick_label_col(df)
    if not label_col:
        raise ValueError("No usable ClimateBERT label column found")

    view = pd.DataFrame(
        {
            "tone": df["tone_pred"].map(normalize_tone),
            "climatebert_label": df[label_col].map(normalize_label),
        }
    )
    pivot = pd.crosstab(view["tone"], view["climatebert_label"])

    tone_order = ["commitment", "action", "outcome", "none", "unknown", "missing"]
    existing = [t for t in tone_order if t in pivot.index]
    extra = [t for t in pivot.index.tolist() if t not in set(existing)]
    pivot = pivot.reindex(existing + extra, fill_value=0) if existing else pivot

    if keep_top_labels is not None and keep_top_labels > 0:
        totals = pivot.sum(axis=0).sort_values(ascending=False)
        keep = totals.head(int(keep_top_labels)).index.tolist()
        pivot = pivot.loc[:, keep]

    out = pivot.reset_index()
    VIS.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CROSSTAB, index=False)
    out.to_csv(OUT_CROSSTAB_FULL, index=False)

    # Generate the PNG using matplotlib (same approach as tools/regenerate_a4_chart.py).
    import matplotlib.pyplot as plt

    table = out.set_index("tone")
    fig_w = max(9, min(18, 1.2 + 0.55 * len(table.columns)))
    fig_h = max(4.6, min(11.5, 2.4 + 0.5 * len(table.index)))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    table.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_title("Tone by ClimateBERT Label (A.4 regenerated)", fontsize=13, pad=10)
    ax.set_xlabel("Tone")
    ax.set_ylabel("Record count")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="ClimateBERT label", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=180)
    plt.close(fig)

    return {
        "rows": len(df),
        "label_col": label_col,
        "tone_levels": int(pivot.shape[0]),
        "label_levels": int(pivot.shape[1]),
        "outputs": [str(OUT_CROSSTAB.relative_to(ROOT)), str(OUT_CROSSTAB_FULL.relative_to(ROOT)), str(OUT_PNG.relative_to(ROOT))],
    }


st.title("A.4 Regenerate (Tone x ClimateBERT label)")
st.caption(
    "Regenerates A.4 artifacts from the current `climatebert_record_batch_import.csv` with corrected label/tone normalization "
    "(prevents charts collapsing into a single `undefined` group)."
)

st.markdown("**Inputs**")
st.code(str(SRC.relative_to(ROOT)), language="text")

st.markdown("**Outputs**")
st.code(
    "\n".join(
        [
            str(OUT_CROSSTAB.relative_to(ROOT)),
            str(OUT_CROSSTAB_FULL.relative_to(ROOT)),
            str(OUT_PNG.relative_to(ROOT)),
        ]
    ),
    language="text",
)

col1, col2 = st.columns([1, 2], gap="large")
with col1:
    keep_top = st.number_input(
        "Keep top-N ClimateBERT labels (0 = keep all)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
        help="Useful if the legend gets too big.",
    )
    run = st.button("Regenerate A.4 now", type="primary", use_container_width=True)
with col2:
    if OUT_PNG.exists():
        st.image(str(OUT_PNG), caption="Current A.4 chart (PNG)", width="stretch")
    else:
        st.info("A.4 PNG not found yet.")

if run:
    try:
        payload = regenerate_a4(keep_top_labels=(None if keep_top == 0 else int(keep_top)))
        st.success(f"Done ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).")
        st.json(payload)
        st.rerun()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

st.divider()
st.subheader("Backing tables (preview)")

tab1, tab2 = st.tabs(["tone_climatebert_label_crosstab.csv", "climatebert_record_batch_import.csv (head)"])
with tab1:
    if OUT_CROSSTAB.exists():
        df = pd.read_csv(OUT_CROSSTAB).fillna("")
        st.dataframe(df.astype(str), use_container_width=True, hide_index=True, height=260)
    else:
        st.info("Crosstab CSV not found yet.")
with tab2:
    if SRC.exists():
        src = pd.read_csv(SRC).fillna("")
        show_cols = [c for c in ["record_id", "tone_pred", "climatebert_label", "climatebert_score", "climatebert_model", "prompt", "target"] if c in src.columns]
        st.dataframe(src[show_cols].head(80).astype(str), use_container_width=True, hide_index=True, height=320)
    else:
        st.info("Source CSV not found.")

