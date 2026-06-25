from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Researcher App", layout="wide")

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"
DATA_DIR = ROOT / "data"
THESIS_PDF_DIR = DATA_DIR / "thesis_pdf"


def parse_json_records(path: Path) -> pd.DataFrame:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, list):
        return pd.json_normalize(payload)
    if isinstance(payload, dict):
        if "records" in payload and isinstance(payload["records"], list):
            return pd.json_normalize(payload["records"])
        return pd.json_normalize([payload])
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_table(path: str) -> pd.DataFrame:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(p, low_memory=False)
    if suffix == ".json":
        return parse_json_records(p)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(p)
    return pd.DataFrame()


def discover_tables() -> list[Path]:
    candidates = [
        RESULTS_DIR / "visualizations" / "tone_records_flat.csv",
        RESULTS_DIR / "thesis_workflow_dashboard" / "artifact_inventory.csv",
        RESULTS_DIR / "thesis_workflow_dashboard" / "dashboard_metrics.json",
        RESULTS_DIR / "esg_records.json",
        RESULTS_DIR / "revision_analysis" / "pilot_ground_truth_annotations.csv",
        RESULTS_DIR / "revision_analysis" / "pilot_ground_truth_seed.csv",
        DATA_DIR / "ESG Score.xlsx",
    ]
    candidates.extend(sorted((RESULTS_DIR / "revision_analysis").glob("*.csv")))
    existing = []
    seen = set()
    for p in candidates:
        if p.exists() and p not in seen:
            seen.add(p)
            existing.append(p)
    return existing


def summarize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "non_null": int(s.notna().sum()),
                "nulls": int(s.isna().sum()),
                "unique": int(s.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    mask = pd.Series(True, index=df.index)

    query = st.sidebar.text_input("Global text contains", "")
    if query:
        text_cols = [
            c for c in df.columns if df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c].dtype)
        ]
        if text_cols:
            contains = pd.Series(False, index=df.index)
            for c in text_cols:
                contains |= df[c].fillna("").astype(str).str.contains(query, case=False, na=False)
            mask &= contains

    candidate_cats = []
    for col in df.columns:
        if col.lower() in {"company", "model", "tone", "tone_pred", "esg", "ground_truth_tone", "review_status"}:
            candidate_cats.append(col)
    for col in candidate_cats[:4]:
        values = sorted({str(v) for v in df[col].dropna().astype(str) if str(v).strip()})
        selected = st.sidebar.multiselect(f"{col}", values, default=[])
        if selected:
            mask &= df[col].astype(str).isin(selected)

    max_rows = st.sidebar.number_input("Rows to show", min_value=20, max_value=20000, value=500, step=20)
    return df.loc[mask].head(int(max_rows)).copy()


def render_pdf_inventory() -> None:
    st.subheader("PDF Inventory")
    if not THESIS_PDF_DIR.exists():
        st.info(f"`{THESIS_PDF_DIR}` not found.")
        return
    pdfs = sorted(THESIS_PDF_DIR.glob("*.pdf"))
    query = st.text_input("Find PDF name", "")
    if query:
        pdfs = [p for p in pdfs if query.lower() in p.name.lower()]
    if not pdfs:
        st.info("No PDF matches.")
        return

    rows = []
    for p in pdfs[:2000]:
        rows.append(
            {
                "name": p.name,
                "size_mb": round(p.stat().st_size / (1024 * 1024), 2),
                "modified": pd.to_datetime(p.stat().st_mtime, unit="s"),
            }
        )
    df = pd.DataFrame(rows).sort_values("modified", ascending=False)
    st.caption(f"PDF files matched: {len(pdfs):,}")
    st.dataframe(df, use_container_width=True, hide_index=True)


def main() -> None:
    st.title("Research Explorer")
    st.caption(f"Project root: `{ROOT}`")

    tabs = st.tabs(["Table Explorer", "PDF Inventory"])

    with tabs[0]:
        tables = discover_tables()
        if not tables:
            st.error("No known table files found in `results/` or `data/`.")
            return

        selected = st.selectbox(
            "Data source",
            options=tables,
            format_func=lambda p: str(p.relative_to(ROOT)),
        )
        df = load_table(str(selected))
        if df.empty:
            st.warning("Selected source produced an empty table.")
            return

        filtered = apply_filters(df)

        m1, m2, m3 = st.columns(3)
        m1.metric("Rows (raw)", f"{len(df):,}")
        m2.metric("Rows (filtered)", f"{len(filtered):,}")
        m3.metric("Columns", f"{len(df.columns):,}")

        if "tone" in filtered.columns:
            counts = filtered["tone"].fillna("(missing)").astype(str).value_counts().head(10)
            st.subheader("Tone Distribution")
            st.bar_chart(counts)
        elif "tone_pred" in filtered.columns:
            counts = filtered["tone_pred"].fillna("(missing)").astype(str).value_counts().head(10)
            st.subheader("Predicted Tone Distribution")
            st.bar_chart(counts)

        st.subheader("Filtered Data")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.subheader("Column Summary")
        st.dataframe(summarize_columns(df), use_container_width=True, hide_index=True)

    with tabs[1]:
        render_pdf_inventory()


if __name__ == "__main__":
    main()
