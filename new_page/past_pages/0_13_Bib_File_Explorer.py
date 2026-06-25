from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st

from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Bib File Explorer", layout="wide")
apply_page_runtime_controls(__file__)
st.title("Bib File Explorer")
st.caption("Load BibTeX files, count papers, and convert entries into a table.")

ROOT = Path(__file__).resolve().parents[1]

TABLE_COLUMNS = [
    "entry_type",
    "citation_key",
    "title",
    "author",
    "year",
    "month",
    "journal",
    "booktitle",
    "publisher",
    "pages",
    "doi",
    "url",
    "abstract",
]


@st.cache_data(show_spinner=False)
def discover_bib_files(base_dir: str) -> pd.DataFrame:
    base = Path(base_dir)
    rows: list[dict[str, object]] = []
    for path in sorted(base.rglob("*.bib")):
        try:
            stat = path.stat()
        except OSError:
            continue
        rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "abs_path": str(path),
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": pd.to_datetime(stat.st_mtime, unit="s"),
            }
        )
    return pd.DataFrame(rows)


def _clean_bib_value(value: str) -> str:
    text = (value or "").strip().rstrip(",").strip()
    changed = True
    while changed and len(text) >= 2:
        changed = False
        if text.startswith("{") and text.endswith("}"):
            text = text[1:-1].strip()
            changed = True
        elif text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()
            changed = True
    text = text.replace("\\_", "_")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _find_entry_end(text: str, start_idx: int) -> int:
    brace_depth = 0
    in_quotes = False
    escape = False
    for idx in range(start_idx, len(text)):
        char = text[idx]
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            continue
        if in_quotes:
            continue
        if char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
            if brace_depth == 0:
                return idx
    return len(text) - 1


def _split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    brace_depth = 0
    in_quotes = False
    escape = False

    for char in text:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if char == '"':
            current.append(char)
            in_quotes = not in_quotes
            continue
        if not in_quotes:
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
            elif char == delimiter and brace_depth == 0:
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
                continue
        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def _parse_bibtex_entry(entry_text: str) -> dict[str, str] | None:
    match = re.match(r"@(?P<entry_type>\w+)\s*\{\s*(?P<body>.*)\s*\}\s*$", entry_text.strip(), re.S)
    if not match:
        return None

    entry_type = match.group("entry_type").strip().lower()
    body = match.group("body").strip()
    parts = _split_top_level(body)
    if not parts:
        return None

    citation_key = parts[0].strip()
    record: dict[str, str] = {
        "entry_type": entry_type,
        "citation_key": citation_key,
    }

    for part in parts[1:]:
        if "=" not in part:
            continue
        field_name, raw_value = part.split("=", 1)
        record[field_name.strip().lower()] = _clean_bib_value(raw_value)
    return record


@st.cache_data(show_spinner=False)
def parse_bibtex_text(text: str) -> tuple[pd.DataFrame, list[str]]:
    entries: list[dict[str, str]] = []
    errors: list[str] = []
    idx = 0

    while idx < len(text):
        at_idx = text.find("@", idx)
        if at_idx == -1:
            break
        open_brace_idx = text.find("{", at_idx)
        if open_brace_idx == -1:
            errors.append(f"Entry starting at character {at_idx} is missing an opening brace.")
            break
        end_idx = _find_entry_end(text, open_brace_idx)
        entry_text = text[at_idx : end_idx + 1]
        parsed = _parse_bibtex_entry(entry_text)
        if parsed is None:
            preview = entry_text[:80].replace("\n", " ")
            errors.append(f"Could not parse entry near: {preview}")
        else:
            entries.append(parsed)
        idx = end_idx + 1

    if not entries:
        return pd.DataFrame(columns=TABLE_COLUMNS), errors

    df = pd.DataFrame(entries)
    for column in TABLE_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    if "author" in df.columns:
        df["author"] = (
            df["author"]
            .fillna("")
            .astype(str)
            .str.replace(r"\s+AND\s+", "; ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    preferred = TABLE_COLUMNS + [col for col in df.columns if col not in TABLE_COLUMNS]
    df = df[preferred].fillna("")
    return df, errors


def render_summary(df: pd.DataFrame) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Papers", f"{len(df):,}")
    c2.metric("Entry types", f"{df['entry_type'].replace('', pd.NA).dropna().nunique():,}")
    c3.metric("Unique years", f"{df['year'].replace('', pd.NA).dropna().nunique():,}")
    doi_count = df["doi"].replace("", pd.NA).dropna().shape[0] if "doi" in df.columns else 0
    c4.metric("Entries with DOI", f"{doi_count:,}")


sources = ["Repository .bib file", "Upload .bib file", "Paste BibTeX text"]

with st.sidebar:
    st.header("Input Source")
    source_mode = st.radio("Choose input mode", sources, index=0)

bib_text = ""
source_label = ""

if source_mode == "Repository .bib file":
    catalog = discover_bib_files(str(ROOT))
    if catalog.empty:
        st.warning("No `.bib` files found in the repository.")
        st.stop()

    st.subheader("Repository BibTeX Files")
    st.dataframe(
        catalog[["path", "size_kb", "modified"]],
        use_container_width=True,
        height=220,
    )
    selected_path = st.selectbox("Select a `.bib` file", catalog["path"].tolist(), index=0)
    selected_row = catalog[catalog["path"] == selected_path].iloc[0]
    bib_text = Path(str(selected_row["abs_path"])).read_text(encoding="utf-8", errors="ignore")
    source_label = selected_path

elif source_mode == "Upload .bib file":
    uploaded = st.file_uploader("Upload a `.bib` file", type=["bib"])
    if uploaded is None:
        st.info("Upload a `.bib` file to parse it.")
        st.stop()
    bib_text = uploaded.getvalue().decode("utf-8", errors="ignore")
    source_label = uploaded.name

else:
    default_text = """@article{mattia_birti_c097e3e8,
  author = {Mattia Birti AND Andrea Maurino AND Francesco Osborne},
  title = {Optimizing Large Language Models for ESG Activity Detection in Financial Texts},
  year = {2025},
  doi = {10.1145/3768292.3770371},
  url = {http://arxiv.org/abs/2502.21112}
}"""
    bib_text = st.text_area("Paste BibTeX text", value=default_text, height=320)
    if not bib_text.strip():
        st.info("Paste BibTeX content to parse it.")
        st.stop()
    source_label = "Pasted BibTeX"

st.subheader("Selected Source")
st.write(f"`{source_label}`")

parsed_df, parse_errors = parse_bibtex_text(bib_text)

if parse_errors:
    with st.expander("Parsing warnings", expanded=False):
        for message in parse_errors:
            st.write(f"- {message}")

if parsed_df.empty:
    st.error("No BibTeX entries could be parsed from the selected input.")
    st.stop()

render_summary(parsed_df)

with st.expander("Column selector", expanded=False):
    default_columns = [col for col in TABLE_COLUMNS if col in parsed_df.columns]
    selected_columns = st.multiselect(
        "Columns to show",
        options=parsed_df.columns.tolist(),
        default=default_columns,
    )

st.subheader("Paper Table")
display_df = parsed_df[selected_columns].copy() if selected_columns else parsed_df.copy()
st.dataframe(display_df, use_container_width=True, height=520)

csv_bytes = parsed_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download table as CSV",
    data=csv_bytes,
    file_name="bib_entries.csv",
    mime="text/csv",
)

with st.expander("Raw BibTeX preview", expanded=False):
    preview_chars = st.slider("Preview characters", min_value=500, max_value=30000, value=6000, step=500)
    st.code(bib_text[:preview_chars], language="text")
    if len(bib_text) > preview_chars:
        st.caption("Preview truncated.")
