from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Annotator App", layout="wide")

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
REVISION_DIR = RESULTS_DIR / "revision_analysis"

DEFAULT_DATASETS = [
    REVISION_DIR / "pilot_ground_truth_annotations.csv",
    REVISION_DIR / "pilot_ground_truth_seed.csv",
]

EDITABLE_COLUMNS = [
    "ground_truth_tone",
    "ground_truth_esg",
    "ground_truth_aspect",
    "annotator",
    "review_notes",
    "review_status",
    "needs_human_review",
]

DISPLAY_PRIORITY = [
    "record_id",
    "run_idx",
    "record_idx",
    "company",
    "model",
    "prompt",
    "target",
    "text",
    "aspect",
    "esg",
    "tone_pred",
    "ground_truth_tone",
    "ground_truth_esg",
    "ground_truth_aspect",
    "annotator",
    "review_status",
    "review_notes",
]


@st.cache_data(show_spinner=False)
def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def list_datasets() -> list[Path]:
    discovered = sorted(REVISION_DIR.glob("*.csv"))
    all_paths = []
    seen = set()
    for p in DEFAULT_DATASETS + discovered:
        if p.exists() and p not in seen:
            seen.add(p)
            all_paths.append(p)
    return all_paths


def get_preferred_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def make_display_columns(df: pd.DataFrame) -> list[str]:
    preferred = [c for c in DISPLAY_PRIORITY if c in df.columns]
    remaining = [c for c in df.columns if c not in preferred]
    return preferred + remaining


def build_filters(df: pd.DataFrame) -> pd.Series:
    mask = pd.Series(True, index=df.index)

    with st.sidebar:
        st.header("Filters")

        search_text = st.text_input("Text contains", "")
        if search_text:
            text_col = get_preferred_column(df, ["text", "reasoning"])
            if text_col:
                mask &= df[text_col].fillna("").astype(str).str.contains(search_text, case=False, na=False)

        for label, candidates in [
            ("Company", ["company"]),
            ("Model", ["model"]),
            ("Review status", ["review_status"]),
            ("Predicted tone", ["tone_pred", "tone"]),
            ("Ground truth tone", ["ground_truth_tone", "silver_tone_ground_truth"]),
        ]:
            col = get_preferred_column(df, candidates)
            if not col:
                continue
            values = sorted({str(v) for v in df[col].dropna().astype(str) if str(v).strip()})
            selected = st.multiselect(label, values, default=[])
            if selected:
                mask &= df[col].astype(str).isin(selected)

        limit = st.number_input("Rows to show", min_value=10, max_value=5000, value=250, step=10)
        st.caption(f"Base rows: {len(df):,}")

    filtered_idx = df[mask].index[: int(limit)]
    final_mask = pd.Series(False, index=df.index)
    final_mask.loc[filtered_idx] = True
    return final_mask


def main() -> None:
    st.title("Annotation Workspace")
    st.caption(f"Project root: `{ROOT}`")

    dataset_paths = list_datasets()
    if not dataset_paths:
        st.error(f"No CSV datasets found in `{REVISION_DIR}`.")
        return

    selected_path = st.selectbox(
        "Dataset",
        options=dataset_paths,
        format_func=lambda p: str(p.relative_to(ROOT)),
    )

    df = read_csv(str(selected_path)).copy()
    if df.empty:
        st.warning("Selected dataset is empty.")
        return

    mask = build_filters(df)
    filtered = df.loc[mask].copy()
    if filtered.empty:
        st.info("No rows match current filters.")
        return

    row_id_col = "_row_id"
    filtered[row_id_col] = filtered.index

    editable_cols = [c for c in EDITABLE_COLUMNS if c in filtered.columns]
    display_cols = make_display_columns(filtered)
    if row_id_col not in display_cols:
        display_cols = [row_id_col] + display_cols

    disabled_cols = [c for c in display_cols if c not in editable_cols]
    if row_id_col in disabled_cols:
        pass
    else:
        disabled_cols.append(row_id_col)

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Editable Rows")
        edited = st.data_editor(
            filtered[display_cols],
            hide_index=True,
            use_container_width=True,
            disabled=disabled_cols,
            num_rows="fixed",
            key=f"editor_{selected_path.name}",
        )

    with right:
        st.subheader("Summary")
        st.metric("Visible rows", f"{len(filtered):,}")
        if "review_status" in filtered.columns:
            review_counts = filtered["review_status"].fillna("(missing)").astype(str).value_counts().head(10)
            st.dataframe(review_counts.rename_axis("review_status").reset_index(name="count"), use_container_width=True)
        if "ground_truth_tone" in filtered.columns:
            tone_counts = filtered["ground_truth_tone"].fillna("(missing)").astype(str).value_counts().head(10)
            st.dataframe(tone_counts.rename_axis("ground_truth_tone").reset_index(name="count"), use_container_width=True)

    st.divider()
    save_col, info_col = st.columns([1, 3])
    with save_col:
        if st.button("Save edits to CSV", type="primary", use_container_width=True):
            result_df = df.copy()
            edited_copy = edited.copy()
            changed = 0
            for _, row in edited_copy.iterrows():
                row_idx = int(row[row_id_col])
                for col in editable_cols:
                    old_val = result_df.at[row_idx, col]
                    new_val = row[col]
                    if (pd.isna(old_val) and pd.isna(new_val)) or old_val == new_val:
                        continue
                    result_df.at[row_idx, col] = new_val
                    changed += 1

            backup_dir = REVISION_DIR / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            backup_path = backup_dir / f"{selected_path.stem}.{ts}.bak.csv"
            selected_path.rename(backup_path)
            result_df.to_csv(selected_path, index=False)
            st.success(
                f"Saved `{selected_path.name}` with {changed} changed cells. "
                f"Backup: `{backup_path.relative_to(ROOT)}`"
            )
            read_csv.clear()
            st.rerun()

    with info_col:
        st.caption(
            "Only editable columns are written back. A timestamped backup is created before save."
        )


if __name__ == "__main__":
    main()
