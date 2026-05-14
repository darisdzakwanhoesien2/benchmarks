from __future__ import annotations

from datetime import datetime
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


st.set_page_config(page_title="OCR Company Metadata Labeler", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data" / "thesis_dataset"
LABEL_PATH = ROOT / "data" / "ocr_company_metadata.json"

METADATA_FIELDS = [
    "company_name",
    "ticker",
    "sector",
    "subsector",
    "industry",
    "subindustry",
    "report_year",
    "country",
    "exchange",
    "notes",
]

DEFAULT_COMPANY_EXAMPLES = {
    "PT Aspirasi Hidup Indonesia Tbk.": {
        "company_name": "PT Aspirasi Hidup Indonesia Tbk.",
        "ticker": "",
        "sector": "Barang Konsumen Non-Primer",
        "subsector": "Perdagangan Ritel",
        "industry": "Ritel Khusus",
        "subindustry": "Ritel Barang Rumah Tangga",
        "country": "Indonesia",
        "exchange": "IDX",
        "notes": "",
    }
}


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def empty_store() -> dict[str, Any]:
    return {
        "version": 1,
        "description": "OCR document folder to company metadata labels.",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "documents": {},
        "companies": DEFAULT_COMPANY_EXAMPLES,
    }


def load_store() -> dict[str, Any]:
    store = read_json(LABEL_PATH, empty_store())
    if not isinstance(store, dict):
        store = empty_store()
    store.setdefault("version", 1)
    store.setdefault("description", "OCR document folder to company metadata labels.")
    store.setdefault("created_at", now_iso())
    store.setdefault("updated_at", now_iso())
    store.setdefault("documents", {})
    store.setdefault("companies", {})
    for name, meta in DEFAULT_COMPANY_EXAMPLES.items():
        store["companies"].setdefault(name, meta)
    return store


def save_store(store: dict[str, Any]) -> None:
    store["updated_at"] = now_iso()
    write_json(LABEL_PATH, store)


def document_folders() -> list[Path]:
    if not DATASET_DIR.exists():
        return []
    return sorted([path for path in DATASET_DIR.iterdir() if path.is_dir() and (path / "pages").exists()])


def page_count(doc_path: Path) -> int:
    return len(list((doc_path / "pages").glob("*.md"))) if (doc_path / "pages").exists() else 0


def image_count(doc_path: Path) -> int:
    if not (doc_path / "images").exists():
        return 0
    return len([p for p in (doc_path / "images").iterdir() if p.is_file()])


def suggest_company_name(folder_name: str) -> str:
    text = folder_name
    text = re.sub(r"_pdf$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[_-]+", " ", text)
    text = re.sub(r"\b(sustainability|sustainable|annual|integrated|report|laporan|berkelanjutan|sr|ar|pdf|final|compressed|lowres|lores|eng|id)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(20\d{2}|19\d{2})\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" -_")
    return text or folder_name


def infer_year(folder_name: str) -> str:
    matches = re.findall(r"(20\d{2}|19\d{2})", folder_name)
    return matches[-1] if matches else ""


def company_options(store: dict[str, Any]) -> list[str]:
    names = sorted([name for name in store.get("companies", {}) if name])
    return [""] + names


def metadata_from_company(store: dict[str, Any], company_name: str) -> dict[str, Any]:
    meta = store.get("companies", {}).get(company_name, {})
    return {field: meta.get(field, "") for field in METADATA_FIELDS}


def document_summary(store: dict[str, Any]) -> pd.DataFrame:
    docs = document_folders()
    rows: list[dict[str, Any]] = []
    labels = store.get("documents", {})
    for doc in docs:
        label = labels.get(doc.name, {})
        rows.append(
            {
                "document_folder": doc.name,
                "company_name": label.get("company_name", ""),
                "ticker": label.get("ticker", ""),
                "sector": label.get("sector", ""),
                "subsector": label.get("subsector", ""),
                "industry": label.get("industry", ""),
                "subindustry": label.get("subindustry", ""),
                "report_year": label.get("report_year", infer_year(doc.name)),
                "page_count": page_count(doc),
                "image_count": image_count(doc),
                "status": "labeled" if label.get("company_name") else "unlabeled",
                "updated_at": label.get("updated_at", ""),
            }
        )
    return pd.DataFrame(rows)


def preview_page_text(doc_name: str) -> str:
    pages_dir = DATASET_DIR / doc_name / "pages"
    if not pages_dir.exists():
        return ""
    pages = sorted(pages_dir.glob("*.md"))
    if not pages:
        return ""
    try:
        return pages[0].read_text(encoding="utf-8", errors="ignore")[:3000]
    except Exception:
        return ""


st.title("OCR Company Metadata Labeler")
st.caption("Assign company labels and IDX-style sector metadata to every OCR document folder.")

store = load_store()
summary = document_summary(store)

if summary.empty:
    st.warning(f"No OCR document folders with `pages/` were found in `{DATASET_DIR}`.")
    st.stop()

metric_cols = st.columns(5)
metric_cols[0].metric("OCR folders", f"{len(summary):,}")
metric_cols[1].metric("Labeled", f"{int(summary['status'].eq('labeled').sum()):,}")
metric_cols[2].metric("Unlabeled", f"{int(summary['status'].eq('unlabeled').sum()):,}")
metric_cols[3].metric("Known companies", f"{len(store.get('companies', {})):,}")
metric_cols[4].metric("Total pages", f"{int(summary['page_count'].sum()):,}")

st.progress(
    float(summary["status"].eq("labeled").mean()),
    text=f"{int(summary['status'].eq('labeled').sum())}/{len(summary)} OCR folders labeled",
)

label_tab, company_tab, overview_tab, json_tab = st.tabs(
    ["Label OCR Folder", "Company Metadata Library", "Overview", "JSON Export"]
)

with label_tab:
    left, right = st.columns([1.1, 1])
    with left:
        status_filter = st.radio("Folder filter", ["All", "Unlabeled", "Labeled"], horizontal=True)
        view = summary.copy()
        if status_filter == "Unlabeled":
            view = view[view["status"].eq("unlabeled")]
        elif status_filter == "Labeled":
            view = view[view["status"].eq("labeled")]
        if view.empty:
            st.info(f"No OCR folders match the `{status_filter}` filter.")
            view = summary.copy()
        selected_doc = st.selectbox(
            "OCR document folder",
            view["document_folder"].tolist(),
            format_func=lambda name: f"{name} ({store.get('documents', {}).get(name, {}).get('company_name', 'unlabeled') or 'unlabeled'})",
        )
        existing = store.get("documents", {}).get(selected_doc, {})
        selected_company_option = st.selectbox(
            "Use existing company metadata",
            company_options(store),
            index=company_options(store).index(existing.get("company_name", "")) if existing.get("company_name", "") in company_options(store) else 0,
            help="Choose a known company to prefill metadata, or leave blank and type metadata manually.",
        )
        prefill = metadata_from_company(store, selected_company_option) if selected_company_option else {}
        suggested_name = suggest_company_name(selected_doc)

        with st.form("document_label_form"):
            st.markdown("**Company label**")
            company_name = st.text_input(
                "Company name",
                value=existing.get("company_name") or prefill.get("company_name") or suggested_name,
                placeholder="PT Aspirasi Hidup Indonesia Tbk.",
            )
            ticker = st.text_input("Ticker", value=existing.get("ticker") or prefill.get("ticker", ""))
            c1, c2 = st.columns(2)
            with c1:
                sector = st.text_input("Sektor", value=existing.get("sector") or prefill.get("sector", ""))
                industry = st.text_input("Industri", value=existing.get("industry") or prefill.get("industry", ""))
                report_year = st.text_input("Report year", value=str(existing.get("report_year") or infer_year(selected_doc)))
                country = st.text_input("Country", value=existing.get("country") or prefill.get("country", "Indonesia"))
            with c2:
                subsector = st.text_input("Subsektor", value=existing.get("subsector") or prefill.get("subsector", ""))
                subindustry = st.text_input("Subindustri", value=existing.get("subindustry") or prefill.get("subindustry", ""))
                exchange = st.text_input("Exchange", value=existing.get("exchange") or prefill.get("exchange", "IDX"))
                notes = st.text_input("Notes", value=existing.get("notes") or prefill.get("notes", ""))

            save_to_library = st.checkbox("Save/update this company in metadata library", value=True)
            submitted = st.form_submit_button("Save document label", type="primary")

        if submitted:
            doc_path = DATASET_DIR / selected_doc
            label = {
                "document_folder": selected_doc,
                "company_name": company_name.strip(),
                "ticker": ticker.strip(),
                "sector": sector.strip(),
                "subsector": subsector.strip(),
                "industry": industry.strip(),
                "subindustry": subindustry.strip(),
                "report_year": report_year.strip(),
                "country": country.strip(),
                "exchange": exchange.strip(),
                "notes": notes.strip(),
                "page_count": page_count(doc_path),
                "image_count": image_count(doc_path),
                "updated_at": now_iso(),
            }
            store["documents"][selected_doc] = label
            if save_to_library and company_name.strip():
                store["companies"][company_name.strip()] = {
                    field: label.get(field, "")
                    for field in METADATA_FIELDS
                    if field != "report_year"
                }
            save_store(store)
            st.success(f"Saved label for `{selected_doc}`")
            st.rerun()

    with right:
        st.markdown("**OCR folder preview**")
        selected_row = summary[summary["document_folder"].eq(selected_doc)]
        if not selected_row.empty:
            st.dataframe(selected_row, use_container_width=True, hide_index=True)
        st.text_area("First OCR page preview", preview_page_text(selected_doc), height=420)

with company_tab:
    st.subheader("Company metadata library")
    st.caption("Use this to create reusable company metadata, then apply it to multiple OCR folders.")
    company_names = company_options(store)
    selected_company = st.selectbox("Company", company_names, index=0)
    existing_company = metadata_from_company(store, selected_company) if selected_company else {}
    with st.form("company_library_form"):
        name = st.text_input("Company name", value=existing_company.get("company_name", selected_company))
        ticker = st.text_input("Ticker", value=existing_company.get("ticker", ""))
        c1, c2 = st.columns(2)
        with c1:
            sector = st.text_input("Sektor", value=existing_company.get("sector", ""))
            industry = st.text_input("Industri", value=existing_company.get("industry", ""))
            country = st.text_input("Country", value=existing_company.get("country", "Indonesia"))
        with c2:
            subsector = st.text_input("Subsektor", value=existing_company.get("subsector", ""))
            subindustry = st.text_input("Subindustri", value=existing_company.get("subindustry", ""))
            exchange = st.text_input("Exchange", value=existing_company.get("exchange", "IDX"))
        notes = st.text_area("Notes", value=existing_company.get("notes", ""), height=100)
        save_company = st.form_submit_button("Save company metadata", type="primary")
    if save_company and name.strip():
        store["companies"][name.strip()] = {
            "company_name": name.strip(),
            "ticker": ticker.strip(),
            "sector": sector.strip(),
            "subsector": subsector.strip(),
            "industry": industry.strip(),
            "subindustry": subindustry.strip(),
            "country": country.strip(),
            "exchange": exchange.strip(),
            "notes": notes.strip(),
        }
        save_store(store)
        st.success(f"Saved company metadata for `{name.strip()}`")
        st.rerun()

    companies_df = pd.DataFrame(store.get("companies", {}).values())
    if not companies_df.empty:
        st.dataframe(companies_df, use_container_width=True, hide_index=True)

with overview_tab:
    st.subheader("OCR folder label overview")
    filters = st.columns(4)
    with filters[0]:
        selected_statuses = st.multiselect("Status", sorted(summary["status"].unique()), default=[])
    with filters[1]:
        selected_sectors = st.multiselect("Sektor", sorted(v for v in summary["sector"].unique() if v), default=[])
    with filters[2]:
        selected_years = st.multiselect("Report year", sorted(v for v in summary["report_year"].astype(str).unique() if v), default=[])
    with filters[3]:
        text_search = st.text_input("Search", "")

    view = summary.copy()
    if selected_statuses:
        view = view[view["status"].isin(selected_statuses)]
    if selected_sectors:
        view = view[view["sector"].isin(selected_sectors)]
    if selected_years:
        view = view[view["report_year"].astype(str).isin(selected_years)]
    if text_search.strip():
        needle = text_search.lower().strip()
        view = view[
            view["document_folder"].str.lower().str.contains(needle, regex=False)
            | view["company_name"].str.lower().str.contains(needle, regex=False)
        ]

    st.dataframe(view, use_container_width=True, hide_index=True, height=520)

    c1, c2 = st.columns(2)
    with c1:
        sector_counts = summary["sector"].replace("", "missing").value_counts()
        st.bar_chart(sector_counts)
    with c2:
        year_counts = summary["report_year"].astype(str).replace("", "missing").value_counts().sort_index()
        st.bar_chart(year_counts)

with json_tab:
    st.subheader("Saved JSON")
    st.caption(f"Path: `{LABEL_PATH}`")
    if st.button("Save current JSON snapshot"):
        save_store(store)
        st.success(f"Saved `{LABEL_PATH.name}`")
    st.download_button(
        "Download OCR company metadata JSON",
        json.dumps(store, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="ocr_company_metadata.json",
        mime="application/json",
    )
    st.code(json.dumps(store, ensure_ascii=False, indent=2), language="json")
