from __future__ import annotations

from pathlib import Path
import csv
import shutil

import pandas as pd
import streamlit as st

from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Page Archive Mover", layout="wide")
apply_page_runtime_controls(__file__)
st.title("Page Archive Mover")
st.caption("Scan `pages/`, choose a file from a dropdown, and move it into `past_pages/`.")

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = ROOT / "pages"
ARCHIVE_DIR = ROOT / "past_pages"
CURRENT_PAGE = Path(__file__).resolve()
SCAN_PATTERNS = [
    "*.py",
    "*.md",
    "*.txt",
    "*.json",
    "*.jsonl",
    "*.csv",
    "*.html",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.pdf",
    "*.docx",
    "*.bib",
]


@st.cache_data(show_spinner=False)
def discover_code_files(base_dir: str) -> pd.DataFrame:
    base = Path(base_dir)
    rows: list[dict[str, object]] = []
    seen: set[Path] = set()
    for pattern in SCAN_PATTERNS:
        for path in sorted(base.rglob(pattern)):
            resolved = path.resolve()
            if resolved == CURRENT_PAGE or resolved in seen:
                continue
            seen.add(resolved)
            stat = path.stat()
            rows.append(
                {
                    "module": path.stem,
                    "filename": path.name,
                    "path": str(path.relative_to(ROOT)),
                    "abs_path": str(path),
                    "ext": path.suffix.lower(),
                    "size_kb": round(stat.st_size / 1024, 2),
                    "modified": pd.to_datetime(stat.st_mtime, unit="s"),
                }
            )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def load_text(path_str: str) -> str:
    return Path(path_str).read_text(encoding="utf-8", errors="ignore")


@st.cache_data(show_spinner=False)
def load_csv_preview(path_str: str, nrows: int = 100) -> pd.DataFrame:
    return pd.read_csv(path_str, nrows=nrows)


@st.cache_data(show_spinner=False)
def csv_schema(path_str: str) -> list[str]:
    try:
        with open(path_str, newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            return next(reader)
    except Exception:
        return []


if not PAGES_DIR.exists():
    st.error(f"Pages directory not found: {PAGES_DIR}")
    st.stop()

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

catalog = discover_code_files(str(PAGES_DIR))
if catalog.empty:
    st.warning("No movable files found under `pages/`.")
    st.stop()

with st.sidebar:
    st.header("Code Filters")
    search = st.text_input("Filename contains", value="")
    ext_options = sorted(catalog["ext"].dropna().unique().tolist())
    selected_ext = st.multiselect("Extensions", ext_options, default=ext_options)

filtered = catalog.copy()
if search.strip():
    filtered = filtered[filtered["module"].str.contains(search.strip(), case=False, na=False)]
filtered = filtered[filtered["ext"].isin(selected_ext)]

c1, c2 = st.columns(2)
c1.metric("Files", f"{len(catalog):,}")
c2.metric("Filtered", f"{len(filtered):,}")

st.subheader("Page Inventory")
st.dataframe(
    filtered[["module", "filename", "ext", "size_kb", "modified"]],
    use_container_width=True,
    height=280,
)

if filtered.empty:
    st.info("No files match the current filter.")
    st.stop()

options = filtered["path"].tolist()
selected_module = st.selectbox("Choose a file to move into past_pages", options, index=0)
selected_row = filtered[filtered["path"] == selected_module].iloc[0]
selected_path = selected_row["abs_path"]
target_path = ARCHIVE_DIR / selected_row["filename"]

left, right = st.columns([1, 2])
with left:
    st.subheader("Selected Page")

    overwrite = st.checkbox(
        "Overwrite existing file in past_pages",
        value=False,
        help="Enable this only if you want to replace a same-named archived file.",
    )

    if target_path.exists() and not overwrite:
        st.warning("A file with the same name already exists in `past_pages/`.")

    move_disabled = target_path.exists() and not overwrite
    if st.button("Move to past_pages", type="primary", disabled=move_disabled, use_container_width=True):
        if target_path.exists() and overwrite:
            target_path.unlink()
        shutil.move(selected_path, target_path)
        st.cache_data.clear()
        st.success(f"Moved `{selected_row['filename']}` to `past_pages/`.")
        st.rerun()

    st.write(f"Module: `{selected_row['module']}`")
    st.write(f"From: `{selected_row['path']}`")
    st.write(f"To: `{target_path.relative_to(ROOT)}`")
    st.write(f"Type: `{selected_row['ext']}`")
    st.write(f"Size: **{selected_row['size_kb']:.2f} KB**")
    st.write(f"Modified: **{selected_row['modified']}**")

with right:
    st.subheader("Source Preview")
    ext = str(selected_row["ext"])

    if ext in {".py", ".md", ".txt", ".html", ".bib"}:
        selected_text = load_text(selected_path)
        preview_limit = st.slider("Preview characters", min_value=2000, max_value=30000, value=12000, step=1000)
        language = "python" if ext == ".py" else "text"
        st.code(selected_text[:preview_limit], language=language)
        if len(selected_text) > preview_limit:
            st.caption("Preview truncated. Increase the slider to view more of the file.")
    elif ext in {".json", ".jsonl"}:
        selected_text = load_text(selected_path)
        preview_limit = st.slider("Preview characters", min_value=2000, max_value=30000, value=12000, step=1000)
        st.code(selected_text[:preview_limit], language="json")
        if len(selected_text) > preview_limit:
            st.caption("Preview truncated. Increase the slider to view more of the file.")
    elif ext == ".csv":
        header = csv_schema(selected_path)
        if header:
            st.caption(f"Columns detected: {len(header)}")
            st.code("\n".join(header[:80]), language="text")
        preview_rows = st.slider("CSV preview rows", min_value=20, max_value=500, value=100, step=20)
        try:
            preview_df = load_csv_preview(selected_path, nrows=preview_rows)
            st.dataframe(preview_df, use_container_width=True, height=360)
        except Exception as exc:
            st.error(f"Failed to preview CSV: {exc}")
    elif ext in {".png", ".jpg", ".jpeg"}:
        st.image(selected_path, use_container_width=True)
    elif ext in {".pdf", ".docx"}:
        st.info("Binary document selected. Preview is not rendered here, but the file can still be moved to `past_pages/`.")
    else:
        st.info("Preview is not implemented for this file type.")
