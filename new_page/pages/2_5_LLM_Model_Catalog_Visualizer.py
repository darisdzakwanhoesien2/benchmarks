from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="LLM Model Catalog Visualizer", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_CANDIDATES = [
    ROOT / "data" / "LLM model.xlsx",
    ROOT / "data" / "LLM Model.xlsx",
    ROOT.parent / "data" / "LLM model.xlsx",
    ROOT.parent / "data" / "LLM Model.xlsx",
]

KNOWN_HEADER_WORDS = {
    "url",
    "model",
    "model name",
    "name",
    "description",
    "tags",
    "downloads",
    "downloads/pulls",
    "stars",
    "updated",
    "organization",
    "provider",
    "parameters",
    "context",
    "license",
    "architecture",
    "total score",
    "general",
    "scientific",
    "coding",
    "agents",
}


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    text = str(value).replace("\xa0", " ").strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return re.sub(r"\s+", " ", text)


def workbook_path() -> Path | None:
    for path in WORKBOOK_CANDIDATES:
        if path.exists():
            return path
    return None


def excel_col_index(cell_ref: str) -> int:
    letters = re.sub(r"[^A-Z]", "", cell_ref.upper())
    out = 0
    for char in letters:
        out = out * 26 + (ord(char) - ord("A") + 1)
    return max(out - 1, 0)


def xml_text(node: ET.Element) -> str:
    return "".join(node.itertext()).strip()


def read_xlsx_without_openpyxl(path: Path) -> dict[str, pd.DataFrame]:
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_ns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    with ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = [xml_text(si) for si in root.findall(".//m:si", ns)]

        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_by_id = {
            rel.attrib.get("Id"): rel.attrib.get("Target", "")
            for rel in rels.findall("r:Relationship", rel_ns)
        }

        sheets: dict[str, pd.DataFrame] = {}
        for sheet in workbook.findall(".//m:sheet", ns):
            name = sheet.attrib.get("name", "Sheet")
            rel_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = rel_by_id.get(rel_id, "")
            if not target:
                continue
            sheet_path = f"xl/{target.lstrip('/')}"
            if sheet_path not in zf.namelist():
                sheet_path = f"xl/worksheets/{Path(target).name}"
            if sheet_path not in zf.namelist():
                continue

            sheet_root = ET.fromstring(zf.read(sheet_path))
            rows: list[list[str]] = []
            max_col = 0
            for row in sheet_root.findall(".//m:sheetData/m:row", ns):
                values: dict[int, str] = {}
                for cell in row.findall("m:c", ns):
                    idx = excel_col_index(cell.attrib.get("r", "A1"))
                    max_col = max(max_col, idx)
                    cell_type = cell.attrib.get("t", "")
                    if cell_type == "inlineStr":
                        value = xml_text(cell)
                    else:
                        value_node = cell.find("m:v", ns)
                        value = value_node.text if value_node is not None and value_node.text is not None else ""
                        if cell_type == "s" and value:
                            try:
                                value = shared[int(value)]
                            except Exception:
                                pass
                    values[idx] = clean(value)
                if values:
                    rows.append([values.get(i, "") for i in range(max_col + 1)])
            width = max((len(row) for row in rows), default=0)
            rows = [row + [""] * (width - len(row)) for row in rows]
            sheets[name] = pd.DataFrame(rows)
    return sheets


@st.cache_data(show_spinner=False)
def load_raw_sheets(path_text: str) -> dict[str, pd.DataFrame]:
    path = Path(path_text)
    try:
        xl = pd.ExcelFile(path)
        return {sheet: pd.read_excel(path, sheet_name=sheet, header=None).fillna("") for sheet in xl.sheet_names}
    except Exception:
        return read_xlsx_without_openpyxl(path)


def trim_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy().fillna("")
    out = out.loc[:, out.astype(str).apply(lambda col: col.map(clean).ne("").any())]
    out = out.loc[out.astype(str).apply(lambda row: row.map(clean).ne("").any(), axis=1)]
    return out.reset_index(drop=True)


def make_unique(columns: list[str]) -> list[str]:
    counts: Counter[str] = Counter()
    out: list[str] = []
    for idx, col in enumerate(columns):
        base = clean(col) or f"column_{idx + 1}"
        counts[base] += 1
        out.append(base if counts[base] == 1 else f"{base} {counts[base]}")
    return out


def header_score(values: list[str]) -> int:
    lowered = [clean(v).lower() for v in values if clean(v)]
    known = sum(1 for value in lowered if value in KNOWN_HEADER_WORDS or any(word in value for word in ["model", "description", "download", "updated", "provider", "organization"]))
    return known * 4 + min(len(lowered), 8)


def normalize_sheet(df: pd.DataFrame) -> pd.DataFrame:
    trimmed = trim_frame(df)
    if trimmed.empty:
        return trimmed
    candidate_count = min(10, len(trimmed))
    scores = [(header_score([clean(v) for v in trimmed.iloc[i].tolist()]), i) for i in range(candidate_count)]
    _, header_idx = max(scores, key=lambda pair: pair[0])
    headers = make_unique([clean(v) for v in trimmed.iloc[header_idx].tolist()])
    out = trimmed.iloc[header_idx + 1 :].copy()
    out.columns = headers[: len(out.columns)]
    out = trim_frame(out)
    return out


def first_column(columns: list[str], predicates: list[str], *, exact: set[str] | None = None) -> str:
    exact = exact or set()
    for col in columns:
        label = col.lower()
        if label in exact:
            return col
    for col in columns:
        label = col.lower()
        if any(token in label for token in predicates):
            return col
    return ""


def url_values(row: pd.Series) -> list[str]:
    links: list[str] = []
    for col, value in row.items():
        text = clean(value)
        if not text:
            continue
        if "http://" in text or "https://" in text or any(token in col.lower() for token in ["url", "link", "href"]):
            links.extend(re.findall(r"https?://[^\s,;]+", text) or ([text] if text.startswith("http") else []))
    return list(dict.fromkeys(links))


def best_description(row: pd.Series) -> str:
    candidates: list[str] = []
    for col, value in row.items():
        label = col.lower()
        text = clean(value)
        if not text:
            continue
        if any(token in label for token in ["description", "text-muted", "mb-4"]) or label in {"#n/a"}:
            candidates.append(text)
    return max(candidates, key=len) if candidates else ""


def build_catalog(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for sheet, raw_df in sheets.items():
        df = normalize_sheet(raw_df)
        if df.empty:
            continue
        cols = list(df.columns)
        model_col = first_column(cols, ["model name", "model", "mb-2", "text-lg"], exact={"model", "model name", "name"})
        if not model_col:
            continue
        org_col = first_column(cols, ["organization", "provider"], exact={"organization", "provider", "#n/a"})
        tags_col = first_column(cols, ["tag"], exact={"tags", "tag"})
        downloads_col = first_column(cols, ["download", "pull"], exact={"downloads", "downloads/pulls"})
        updated_col = first_column(cols, ["updated"], exact={"updated"})
        params_col = first_column(cols, ["parameter", "param"], exact={"parameters"})
        context_col = first_column(cols, ["context"], exact={"context"})
        license_col = first_column(cols, ["license"], exact={"license"})
        score_col = first_column(cols, ["total score"], exact={"total score"})

        for _, row in df.iterrows():
            model = clean(row.get(model_col))
            if not model or model.lower() in {"model", "model name", "name", "url"}:
                continue
            description = best_description(row)
            links = url_values(row)
            rows.append(
                {
                    "model": model,
                    "source_sheet": sheet,
                    "organization": clean(row.get(org_col)) if org_col else "",
                    "tags": clean(row.get(tags_col)) if tags_col else "",
                    "downloads": clean(row.get(downloads_col)) if downloads_col else "",
                    "updated": clean(row.get(updated_col)) if updated_col else "",
                    "parameters": clean(row.get(params_col)) if params_col else "",
                    "context": clean(row.get(context_col)) if context_col else "",
                    "license": clean(row.get(license_col)) if license_col else "",
                    "total_score": pd.to_numeric(row.get(score_col), errors="coerce") if score_col else pd.NA,
                    "description": description,
                    "links": " | ".join(links),
                    "raw_fields": {str(k): clean(v) for k, v in row.items() if clean(v)},
                }
            )
    catalog = pd.DataFrame(rows)
    if catalog.empty:
        return catalog
    catalog["model_key"] = catalog["model"].astype(str).str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()
    catalog["has_description"] = catalog["description"].astype(str).str.strip().ne("")
    return catalog.sort_values(["model_key", "source_sheet"]).reset_index(drop=True)


def short_text(text: str, limit: int = 260) -> str:
    text = clean(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


path = workbook_path()

st.title("LLM Model Catalog")
st.caption("Explore the workbook model lists, choose a model, and read its available descriptions and metadata.")

if path is None:
    st.error("Could not find `data/LLM model.xlsx` or `data/LLM Model.xlsx` in the app or parent benchmark data folders.")
    st.stop()

st.caption(f"Workbook: `{path}`")
raw_sheets = load_raw_sheets(str(path))
normalised_sheets = {name: normalize_sheet(df) for name, df in raw_sheets.items()}
catalog = build_catalog(raw_sheets)

if catalog.empty:
    st.warning("The workbook loaded, but no model-like rows could be detected.")
    st.stop()

top = st.columns(4)
top[0].metric("Workbook sheets", len(raw_sheets))
top[1].metric("Catalog rows", f"{len(catalog):,}")
top[2].metric("Unique models", f"{catalog['model_key'].nunique():,}")
top[3].metric("Rows with descriptions", f"{int(catalog['has_description'].sum()):,}")

st.divider()

left, right = st.columns([1.1, 2], gap="large")

with left:
    st.subheader("Select Model")
    sheet_filter = st.multiselect(
        "Source sheets",
        sorted(catalog["source_sheet"].dropna().unique()),
        default=sorted(catalog["source_sheet"].dropna().unique())[:6],
    )
    filtered = catalog[catalog["source_sheet"].isin(sheet_filter)].copy() if sheet_filter else catalog.copy()
    query = st.text_input("Search model / organization / tag", "")
    if query.strip():
        needle = query.lower()
        haystack = (
            filtered["model"].astype(str)
            + " "
            + filtered["organization"].astype(str)
            + " "
            + filtered["tags"].astype(str)
            + " "
            + filtered["description"].astype(str)
        ).str.lower()
        filtered = filtered[haystack.str.contains(re.escape(needle), na=False)]

    labels = (
        filtered.assign(label=lambda df: df["model"] + " — " + df["source_sheet"])
        .sort_values("label")["label"]
        .tolist()
    )
    if not labels:
        st.info("No models match the current filters.")
        st.stop()
    selected_label = st.selectbox("Model", labels)
    selected_model = selected_label.rsplit(" — ", 1)[0]
    selected_key = clean(selected_model).lower()
    selected_rows = catalog[catalog["model"].astype(str).str.lower().eq(selected_key)].copy()
    if selected_rows.empty:
        selected_rows = catalog[catalog["model"].eq(selected_model)].copy()

with right:
    st.subheader(selected_model)
    sources = ", ".join(sorted(selected_rows["source_sheet"].unique()))
    orgs = [value for value in sorted(selected_rows["organization"].dropna().astype(str).unique()) if clean(value)]
    st.caption(f"Found in: {sources}")
    if orgs:
        st.markdown(f"**Organization / provider:** {', '.join(orgs[:6])}")

    descriptions = [clean(value) for value in selected_rows["description"].tolist() if clean(value)]
    if descriptions:
        st.markdown("#### Description")
        st.write(max(descriptions, key=len))
    else:
        st.info("No long description is available for this model in the workbook.")

    meta_cols = ["source_sheet", "organization", "tags", "downloads", "updated", "parameters", "context", "license", "total_score", "links"]
    visible_meta = selected_rows[[c for c in meta_cols if c in selected_rows.columns]].copy()
    st.markdown("#### Workbook Records For This Model")
    st.dataframe(visible_meta, use_container_width=True, hide_index=True, height=220)

    link_text = " | ".join(v for v in selected_rows["links"].dropna().astype(str).tolist() if clean(v))
    links = list(dict.fromkeys(re.findall(r"https?://[^\s|]+", link_text)))
    if links:
        st.markdown("#### Links")
        for url in links[:12]:
            st.markdown(f"- [{url}]({url})")

st.divider()

st.subheader("Catalog Overview")
overview_left, overview_right = st.columns([1, 1], gap="large")

with overview_left:
    by_sheet = catalog.groupby("source_sheet", dropna=False).size().reset_index(name="models")
    chart = alt.Chart(by_sheet).mark_bar(color="#3f7c85").encode(
        x=alt.X("models:Q", title="Rows detected"),
        y=alt.Y("source_sheet:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
        tooltip=["source_sheet", "models"],
    ).properties(height=360)
    st.altair_chart(chart, use_container_width=True)

with overview_right:
    org_df = catalog[catalog["organization"].astype(str).str.strip().ne("")]
    if not org_df.empty:
        top_orgs = org_df.groupby("organization").size().reset_index(name="models").sort_values("models", ascending=False).head(20)
        chart = alt.Chart(top_orgs).mark_bar(color="#6f8f45").encode(
            x=alt.X("models:Q", title="Rows detected"),
            y=alt.Y("organization:N", sort="-x", title=None, axis=alt.Axis(labelLimit=220)),
            tooltip=["organization", "models"],
        ).properties(height=360)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No organization/provider column was detected in the normalized catalog.")

summary_cols = ["model", "source_sheet", "organization", "tags", "downloads", "updated", "parameters", "context", "description"]
summary = catalog[[c for c in summary_cols if c in catalog.columns]].copy()
if "description" in summary.columns:
    summary["description"] = summary["description"].map(lambda value: short_text(value, 180))
st.dataframe(summary, use_container_width=True, hide_index=True, height=420)
st.download_button(
    "Download normalized LLM catalog CSV",
    summary.to_csv(index=False).encode("utf-8"),
    "llm_model_catalog.csv",
    "text/csv",
    use_container_width=True,
)

st.divider()

st.subheader("Raw Workbook Sheets")
sheet_name = st.selectbox("Sheet", list(raw_sheets.keys()))
sheet_df = normalised_sheets.get(sheet_name, pd.DataFrame())
if sheet_df.empty:
    st.info("This sheet has no visible rows after trimming.")
else:
    st.caption(f"{sheet_name}: {len(sheet_df):,} rows x {len(sheet_df.columns):,} columns after header normalization")
    st.dataframe(sheet_df, use_container_width=True, height=420)
    st.download_button(
        f"Download {sheet_name} CSV",
        sheet_df.to_csv(index=False).encode("utf-8"),
        f"{sheet_name.replace(' ', '_').lower()}.csv",
        "text/csv",
        use_container_width=True,
    )
