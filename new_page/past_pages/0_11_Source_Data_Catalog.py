from pathlib import Path
import csv

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Source Data Catalog", layout="wide")
apply_page_runtime_controls(__file__)
st.title("Source Data Catalog")
st.caption("Inventory and preview source datasets used by the Streamlit thesis workflow.")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@st.cache_data(show_spinner=False)
def discover_data_files(base_dir: str):
    base = Path(base_dir)
    patterns = ["*.csv", "*.json", "*.jsonl", "*.xlsx", "*.parquet", "*.txt", "*.md", "*.html"]
    files = []
    for pattern in patterns:
        files.extend(base.rglob(pattern))

    rows = []
    for path in files:
        try:
            stat = path.stat()
        except OSError:
            continue
        rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "name": path.name,
                "ext": path.suffix.lower(),
                "size_mb": round(stat.st_size / (1024 * 1024), 3),
                "modified": pd.to_datetime(stat.st_mtime, unit="s"),
                "abs_path": str(path),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["path", "name", "ext", "size_mb", "modified", "abs_path"])
    return pd.DataFrame(rows).sort_values(["ext", "size_mb"], ascending=[True, False]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def csv_schema(csv_path: str):
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
        return header
    except Exception:
        return []


@st.cache_data(show_spinner=False)
def csv_preview(csv_path: str, nrows: int = 100):
    return pd.read_csv(csv_path, nrows=nrows)


if not DATA_DIR.exists():
    st.error(f"Data directory not found: {DATA_DIR}")
    st.stop()

catalog = discover_data_files(str(DATA_DIR))
if catalog.empty:
    st.warning("No source data files found under `data/`.")
    st.stop()

with st.sidebar:
    st.header("Catalog Filters")
    ext_options = sorted(catalog["ext"].dropna().unique().tolist())
    selected_ext = st.multiselect("File extensions", ext_options, default=ext_options)
    min_size = st.number_input("Min size (MB)", min_value=0.0, value=0.0, step=0.1)
    name_query = st.text_input("Path contains", value="")

filtered = catalog[catalog["ext"].isin(selected_ext)].copy()
filtered = filtered[filtered["size_mb"] >= min_size]
if name_query.strip():
    filtered = filtered[filtered["path"].str.contains(name_query.strip(), case=False, na=False)]

c1, c2, c3 = st.columns(3)
c1.metric("Files in data/", f"{len(catalog):,}")
c2.metric("Files after filters", f"{len(filtered):,}")
c3.metric("Total size after filters", f"{filtered['size_mb'].sum():,.2f} MB")

st.subheader("Dataset Inventory")
st.dataframe(
    filtered[["path", "ext", "size_mb", "modified"]],
    use_container_width=True,
    height=420,
)

st.subheader("Open File")
if filtered.empty:
    st.info("No files match current filters.")
    st.stop()

selected_path = st.selectbox("Select a file", filtered["path"].tolist(), index=0)
selected_row = filtered[filtered["path"] == selected_path].iloc[0]
selected_abs = selected_row["abs_path"]

st.write(f"`{selected_path}`")
st.write(f"Size: **{selected_row['size_mb']:.3f} MB**")

ext = selected_row["ext"]

if ext == ".csv":
    header = csv_schema(selected_abs)
    st.write(f"Columns detected: **{len(header)}**")
    if header:
        st.code("\n".join(header[:80]), language="text")

    preview_rows = st.slider("CSV preview rows", min_value=20, max_value=500, value=100, step=20)
    try:
        preview_df = csv_preview(selected_abs, nrows=preview_rows)
        st.dataframe(preview_df, use_container_width=True, height=360)
    except Exception as exc:
        st.error(f"Failed to read CSV preview: {exc}")

elif ext in {".json", ".jsonl"}:
    try:
        text = Path(selected_abs).read_text(encoding="utf-8", errors="ignore")
        st.code(text[:12000], language="json")
        if len(text) > 12000:
            st.caption("Preview truncated to first 12,000 characters.")
    except Exception as exc:
        st.error(f"Failed to read JSON file: {exc}")

elif ext in {".txt", ".md", ".html"}:
    try:
        text = Path(selected_abs).read_text(encoding="utf-8", errors="ignore")
        st.code(text[:12000], language="text")
        if len(text) > 12000:
            st.caption("Preview truncated to first 12,000 characters.")
    except Exception as exc:
        st.error(f"Failed to read text file: {exc}")

elif ext == ".xlsx":
    try:
        xls = pd.ExcelFile(selected_abs)
        st.write("Sheets:", xls.sheet_names)
        if xls.sheet_names:
            sheet = st.selectbox("Sheet", xls.sheet_names)
            df_sheet = pd.read_excel(selected_abs, sheet_name=sheet, nrows=200)
            st.dataframe(df_sheet, use_container_width=True, height=360)
    except Exception as exc:
        st.error(f"Failed to read Excel file: {exc}")

elif ext == ".parquet":
    try:
        df_parquet = pd.read_parquet(selected_abs)
        st.dataframe(df_parquet.head(200), use_container_width=True, height=360)
    except Exception as exc:
        st.error(f"Failed to read Parquet file: {exc}")

else:
    st.info("Preview is not implemented for this file type.")

st.divider()
st.subheader("IDX Source Snapshot")
idx_path = DATA_DIR / "idx_data.csv"
if not idx_path.exists():
    st.warning("`data/idx_data.csv` not found.")
else:
    try:
        idx_df = pd.read_csv(idx_path)
        st.write(f"Rows: **{len(idx_df):,}** | Columns: **{len(idx_df.columns):,}**")
        ticker_col = "f-20" if "f-20" in idx_df.columns else None
        name_col = "full-width" if "full-width" in idx_df.columns else None
        if ticker_col:
            st.write(f"Unique tickers: **{idx_df[ticker_col].astype(str).str.strip().replace('', pd.NA).dropna().nunique():,}**")
        if name_col:
            st.write(f"Unique issuers: **{idx_df[name_col].astype(str).str.strip().replace('', pd.NA).dropna().nunique():,}**")

        cols_to_show = [c for c in ["f-20", "box-title", "full-width", "table", "link-download href"] if c in idx_df.columns]
        st.dataframe(idx_df[cols_to_show].head(50), use_container_width=True, height=320)
    except Exception as exc:
        st.error(f"Failed to load IDX snapshot: {exc}")
