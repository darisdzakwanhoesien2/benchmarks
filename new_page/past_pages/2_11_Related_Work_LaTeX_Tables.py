from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st

from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Related Work LaTeX Tables", layout="wide")
apply_page_runtime_controls(__file__)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CANDIDATES = [
    ROOT / "source" / "thesis_related_works" / "thesis_related_works.tex",
    ROOT / "final_revision" / "version_3" / "Chapters" / "relatedwork.tex",
    ROOT / "report_standardized" / "Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_" / "Chapters" / "relatedwork.tex",
]


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def resolve_source() -> Path | None:
    for candidate in SOURCE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def strip_latex_commands(text: str) -> str:
    value = str(text or "")
    value = re.sub(r"%.*$", "", value, flags=re.M)
    value = re.sub(r"\\parencite\*?\{[^}]*\}", "", value)
    value = re.sub(r"\\cite\*?\{[^}]*\}", "", value)
    value = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\emph\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\textit\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\caption\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\label\{([^{}]*)\}", "", value)
    value = re.sub(r"\\renewcommand\{[^}]*\}\{[^}]*\}", "", value)
    value = re.sub(r"\\small\b", "", value)
    value = re.sub(r"\\centering\b", "", value)
    value = value.replace(r"\&", "&")
    value = value.replace(r"\%", "%")
    value = value.replace(r"\$", "$")
    value = value.replace(r"\_", "_")
    value = value.replace(r"\par", " ")
    value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{([^{}]*)\})?", lambda m: m.group(1) or "", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" |")


def split_latex_row(row_text: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    brace_depth = 0
    escape = False
    for char in row_text:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)
        elif char == "&" and brace_depth == 0:
            cells.append(strip_latex_commands("".join(current)))
            current = []
            continue
        current.append(char)
    tail = strip_latex_commands("".join(current))
    if tail or cells:
        cells.append(tail)
    return cells


def parse_tabular_rows(tabular_text: str) -> list[list[str]]:
    body = re.sub(r"\\begin\{tabularx?\}(\{[^}]*\}){1,2}", "", tabular_text, count=1, flags=re.S)
    body = re.sub(r"\\end\{tabularx?\}", "", body, count=1, flags=re.S)
    body = re.sub(r"\\hline", "", body)
    raw_rows = re.split(r"\\\\", body)
    rows: list[list[str]] = []
    for raw_row in raw_rows:
        cleaned = raw_row.strip()
        if not cleaned:
            continue
        row = split_latex_row(cleaned)
        if any(cell for cell in row):
            rows.append(row)
    return rows


def extract_table_title(tex: str, table_start: int, index: int) -> str:
    prefix = tex[:table_start]
    section_matches = list(re.finditer(r"\\subsection\{([^{}]*)\}", prefix))
    if section_matches:
        title = strip_latex_commands(section_matches[-1].group(1))
        if title:
            return title
    return f"Table {index}"


def extract_tables(tex: str) -> list[dict[str, object]]:
    tables: list[dict[str, object]] = []
    pattern = re.compile(r"\\begin\{table\}\[[^\]]*\](.*?)\\end\{table\}", re.S)
    for index, match in enumerate(pattern.finditer(tex), start=1):
        block = match.group(0)
        tabular_match = re.search(r"\\begin\{tabularx?\}.*?\\end\{tabularx?\}", block, re.S)
        if not tabular_match:
            continue
        rows = parse_tabular_rows(tabular_match.group(0))
        if not rows:
            continue
        header = rows[0]
        width = max(len(header), max(len(row) for row in rows))
        normalized_rows = [row + [""] * (width - len(row)) for row in rows[1:]]
        normalized_header = header + [f"Column {i}" for i in range(len(header) + 1, width + 1)]
        frame = pd.DataFrame(normalized_rows, columns=normalized_header)
        tables.append(
            {
                "index": index,
                "title": extract_table_title(tex, match.start(), index),
                "dataframe": frame,
                "rows": len(frame),
                "columns": len(frame.columns),
                "latex": block.strip(),
            }
        )
    return tables


source_path = resolve_source()

st.title("Related Work LaTeX Tables")
st.caption("Extract and render all related-work literature tables directly from the LaTeX source.")

if source_path is None:
    st.error("No related-work LaTeX source was found in the configured candidate paths.")
    st.stop()

source_text = load_text(source_path)
tables = extract_tables(source_text)

st.write(
    "This page reads the LaTeX chapter, extracts every `table` environment, parses the embedded `tabular` or `tabularx` block, and renders the result as Streamlit dataframes."
)
st.info(f"Using source: `{source_path.relative_to(ROOT)}`")

summary_rows = [
    {
        "table_index": table["index"],
        "title": table["title"],
        "rows": table["rows"],
        "columns": table["columns"],
    }
    for table in tables
]

c1, c2 = st.columns(2)
with c1:
    st.metric("Tables extracted", len(tables))
with c2:
    st.metric("Source length", f"{len(source_text.splitlines()):,} lines")

if not tables:
    st.warning("No LaTeX tables were extracted from the selected source.")
    st.stop()

st.subheader("Table Inventory")
st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True, height=260)

selected_title = st.selectbox(
    "Inspect extracted table",
    [f"{table['index']}. {table['title']}" for table in tables],
    index=0,
)
selected_table = tables[[f"{table['index']}. {table['title']}" for table in tables].index(selected_title)]

tab_data, tab_latex = st.tabs(["Parsed Table", "Raw LaTeX"])

with tab_data:
    st.subheader(selected_table["title"])
    st.dataframe(selected_table["dataframe"], use_container_width=True, height=560)

with tab_latex:
    st.code(selected_table["latex"], language="tex")

st.subheader("All Extracted Tables")
for table in tables:
    with st.expander(f"{table['index']}. {table['title']} ({table['rows']} rows)"):
        st.dataframe(table["dataframe"], use_container_width=True, height=min(560, 120 + table["rows"] * 35))
