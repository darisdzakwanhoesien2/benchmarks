from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "results" / "revision_analysis"
DATA = ROOT / "data"

SILVER_PATH = REV / "silver_tone_ground_truth.csv"
ANNOTATION_PATH = REV / "pilot_ground_truth_annotations.csv"
PHASE_REGISTRY_PATH = REV / "dataset_phase_registry.csv"
TICKER_UNIVERSE_PATH = DATA / "indonesia_tickers.csv"

PHASES = ["Phase 1", "Phase 2", "Phase 3"]
PDF_METADATA_OVERRIDES = {
    "alfamart_sustainability_2025_pdf": {"company_name": "Alfamart", "report_year": "2025", "ticker": "AMRT"},
    "wika_beton_SR-WTON-2025_pdf": {"company_name": "WIKA Beton", "report_year": "2025", "ticker": "WTON"},
    "SR-Bank-Aladin-Syariah-2025_pdf": {"company_name": "Bank Aladin Syariah", "report_year": "2025", "ticker": "BANK"},
    "ABM_2025_ABMM_SR_2025_pdf": {"company_name": "ABM Investama / ABMM", "report_year": "2025", "ticker": "ABMM"},
    "ARCI-SR-2025-E-reporting_pdf": {"company_name": "ARCI", "report_year": "2025", "ticker": "ARCI"},
    "waskita_karya_SR2025_pdf": {"company_name": "Waskita Karya", "report_year": "2025", "ticker": "WSKT"},
}


def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "nat"} else text


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def stable_id(prefix: str, *parts) -> str:
    digest = hashlib.sha1("|".join(clean(part) for part in parts).encode("utf-8", errors="ignore")).hexdigest()
    return f"{prefix}_{digest[:12]}"


def ensure_record_id(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    if "record_id" not in out.columns:
        out.insert(0, "record_id", [stable_id(prefix, idx, row.get("target", ""), row.get("text", "")) for idx, row in out.iterrows()])
    out["record_id"] = out["record_id"].map(clean)
    return out[out["record_id"].ne("")].drop_duplicates("record_id", keep="last").reset_index(drop=True)


def original_file(value: str) -> str:
    text = clean(value)
    if not text:
        return "<missing>"
    return text.split("/batch_", 1)[0]


def normalize_lookup_text(value: str) -> str:
    text = clean(value).lower()
    text = re.sub(r"\b(pt|tbk|persero)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_aliases(value) -> list[str]:
    text = clean(value)
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [clean(item) for item in parsed if clean(item)]
    except Exception:
        pass
    return [part.strip() for part in re.split(r"[|,]", text) if part.strip()]


@lru_cache(maxsize=1)
def load_ticker_universe() -> dict[str, dict[str, str | list[str]]]:
    tickers = load_csv(TICKER_UNIVERSE_PATH)
    out: dict[str, dict[str, str | list[str]]] = {}
    for _, row in tickers.iterrows():
        ticker = clean(row.get("ticker")).upper()
        if not ticker:
            continue
        company_name = clean(row.get("company_name"))
        aliases = [ticker, company_name, *parse_aliases(row.get("aliases"))]
        out[ticker] = {
            "ticker": ticker,
            "company_name": company_name,
            "sector": clean(row.get("sector")),
            "aliases": [alias for alias in aliases if clean(alias)],
        }
    return out


def infer_ticker(original_file_name: str) -> str:
    text = clean(original_file_name)
    override = PDF_METADATA_OVERRIDES.get(text, {})
    if clean(override.get("ticker")):
        return clean(override.get("ticker")).upper()
    tickers = load_ticker_universe()
    tokens = set(re.findall(r"[A-Z][A-Z0-9]{2,5}", text.upper()))
    for ticker in sorted(tokens):
        if ticker in tickers and ticker not in {"BANK"}:
            return ticker
    lookup_text = normalize_lookup_text(text)
    for ticker, meta in tickers.items():
        for alias in meta.get("aliases", []):
            alias_text = normalize_lookup_text(str(alias))
            if len(alias_text) >= 4 and alias_text in lookup_text:
                return ticker
    return ""


def infer_report_year(original_file_name: str) -> str:
    text = clean(original_file_name)
    if text in PDF_METADATA_OVERRIDES:
        return PDF_METADATA_OVERRIDES[text]["report_year"]
    matches = re.findall(r"(20\d{2}|19\d{2})", text)
    return matches[-1] if matches else ""


def infer_company_name(original_file_name: str) -> str:
    text = clean(original_file_name)
    if text in PDF_METADATA_OVERRIDES:
        return PDF_METADATA_OVERRIDES[text]["company_name"]
    company = re.sub(r"_pdf$|\.pdf$", "", text, flags=re.IGNORECASE)
    company = re.sub(r"[_-]+", " ", company)
    company = re.sub(r"\b(20\d{2}|19\d{2})\b", " ", company)
    company = re.sub(
        r"\b(sustainability|sustainable|annual|integrated|report|laporan|berkelanjutan|sr|ar|pdf|final|compressed|lowres|lores|hires|eng|id|submit|submission|e reporting|website)\b",
        " ",
        company,
        flags=re.IGNORECASE,
    )
    company = re.sub(r"\s+", " ", company).strip(" -_")
    return company or text


def add_pdf_metadata(df: pd.DataFrame, source_col: str = "target") -> pd.DataFrame:
    out = df.copy()
    if source_col in out.columns:
        out["original_file"] = out[source_col].map(original_file)
    elif "original_file" not in out.columns:
        out["original_file"] = "<missing>"
    out["company_name"] = out["original_file"].map(infer_company_name)
    out["report_year"] = out["original_file"].map(infer_report_year)
    out["ticker"] = out["original_file"].map(infer_ticker)
    tickers = load_ticker_universe()
    out["ticker_company_name"] = out["ticker"].map(lambda ticker: clean(tickers.get(clean(ticker).upper(), {}).get("company_name")))
    out["ticker_sector"] = out["ticker"].map(lambda ticker: clean(tickers.get(clean(ticker).upper(), {}).get("sector")))
    out["metadata_source"] = out["ticker"].map(lambda ticker: "ticker_universe" if clean(ticker) else "filename_inference")
    return out


def _coalesce(row: pd.Series, *cols: str) -> str:
    for col in cols:
        value = clean(row.get(col))
        if value:
            return value
    return ""


def build_source_records() -> pd.DataFrame:
    annotation = ensure_record_id(load_csv(ANNOTATION_PATH), "annot")
    silver = ensure_record_id(load_csv(SILVER_PATH), "silver")
    if not annotation.empty:
        base = annotation.copy()
        base["source_dataset"] = ANNOTATION_PATH.name
        if not silver.empty:
            incoming = silver[~silver["record_id"].isin(base["record_id"])].copy()
            incoming["source_dataset"] = SILVER_PATH.name
            base = pd.concat([base, incoming], ignore_index=True, sort=False)
    else:
        base = silver.copy()
        if not base.empty:
            base["source_dataset"] = SILVER_PATH.name
    if base.empty:
        return pd.DataFrame(columns=["record_id", "target", "phase"])
    for col in ["target", "company", "model", "prompt", "text", "ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "silver_tone_ground_truth", "esg", "aspect"]:
        if col not in base.columns:
            base[col] = ""
    for col in base.columns:
        if base[col].dtype == object:
            base[col] = base[col].map(clean)
    return base.drop_duplicates("record_id", keep="last").reset_index(drop=True)


def completion_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ground_truth_tone_complete"] = out.apply(lambda row: bool(_coalesce(row, "ground_truth_tone", "silver_tone_ground_truth", "suggested_tone")), axis=1)
    out["ground_truth_esg_complete"] = out.apply(lambda row: bool(_coalesce(row, "ground_truth_esg", "esg")), axis=1)
    out["ground_truth_aspect_complete"] = out.apply(lambda row: bool(_coalesce(row, "ground_truth_aspect", "aspect")), axis=1)
    out["phase1_ready"] = out["ground_truth_tone_complete"] & out["ground_truth_esg_complete"] & out["ground_truth_aspect_complete"]
    out["missing_core_fields"] = out.apply(
        lambda row: ", ".join(
            label
            for label, ok in [
                ("ground_truth_tone", row["ground_truth_tone_complete"]),
                ("ground_truth_esg", row["ground_truth_esg_complete"]),
                ("ground_truth_aspect", row["ground_truth_aspect_complete"]),
            ]
            if not ok
        ),
        axis=1,
    )
    return out


def phase_view() -> pd.DataFrame:
    source = completion_flags(build_source_records())
    if source.empty:
        return source
    source["phase"] = source["phase1_ready"].map(lambda ready: "Phase 1" if ready else "Phase 2")
    registry = load_csv(PHASE_REGISTRY_PATH)
    if not registry.empty and {"record_id", "phase"}.issubset(registry.columns):
        registry = registry[["record_id", "phase"]].copy()
        registry["phase"] = registry["phase"].where(registry["phase"].isin(PHASES), "")
        source = source.drop(columns=["phase"], errors="ignore").merge(registry, on="record_id", how="left")
        source["phase"] = source["phase"].where(source["phase"].isin(PHASES), source["phase1_ready"].map(lambda ready: "Phase 1" if ready else "Phase 2"))
    return source
