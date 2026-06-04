from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA_FILES = DATA / "data"
RESULTS = ROOT / "results"
REV = RESULTS / "revision_analysis"

PHASES = ["Phase 1", "Phase 2", "Phase 3"]
TICKER_UNIVERSE_PATH = DATA / "indonesia_tickers.csv"
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
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    text = str(value).strip()
    return "" if text.lower() in {"nan", "nat"} else text


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def resolve_data_path(base_name: str) -> Path:
    candidates = [
        DATA_FILES / f"{base_name}.csv",
        DATA_FILES / f"{base_name}.txt",
        DATA / f"{base_name}.csv",
        DATA / f"{base_name}.txt",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(base_name)


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


def normalize_lookup_text(value: str) -> str:
    text = clean(value).lower()
    text = re.sub(r"\b(pt|tbk|persero)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def original_file(value: str) -> str:
    text = clean(value)
    if not text:
        return "<missing>"
    return text.split("/batch_", 1)[0]


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


def extract_json_block(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except Exception:
        return None


def normalize_json(obj) -> list[dict]:
    if obj is None:
        return []
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        out: list[dict] = []
        for item in obj:
            out.extend(normalize_json(item))
        return out
    return []


def parse_esg_json(text: str) -> list[dict]:
    return [
        row
        for row in normalize_json(extract_json_block(text))
        if isinstance(row, dict) and clean(row.get("sentence")) and clean(row.get("aspect"))
    ]


def _phase_from_revision_data() -> pd.DataFrame:
    silver = load_csv(REV / "silver_tone_ground_truth.csv")
    if silver.empty:
        return pd.DataFrame()
    if "record_id" not in silver.columns:
        silver.insert(0, "record_id", [f"silver_{idx:06d}" for idx in range(len(silver))])
    for col in ["target", "company", "model", "prompt", "text", "esg", "aspect", "silver_tone_ground_truth"]:
        if col not in silver.columns:
            silver[col] = ""
    silver["phase"] = "Phase 1"
    return silver


def _phase_from_packaged_data() -> pd.DataFrame:
    raw = load_csv(resolve_data_path("data_output"))
    if raw.empty or "text" not in raw.columns:
        return pd.DataFrame()
    raw = raw.copy()
    raw["parsed"] = raw["text"].map(parse_esg_json)
    exploded = raw.explode("parsed", ignore_index=True)
    exploded = exploded[exploded["parsed"].notna()].copy()
    if exploded.empty:
        return pd.DataFrame()
    parsed = pd.json_normalize(exploded["parsed"])
    meta_cols = [col for col in raw.columns if col != "parsed"]
    meta = exploded[meta_cols].reset_index(drop=True)
    df = pd.concat([meta, parsed], axis=1)
    filename_col = "filename" if "filename" in df.columns else ""
    df["target"] = df[filename_col].map(clean) if filename_col else ""
    df["text"] = df["sentence"].map(clean) if "sentence" in df.columns else ""
    df["company"] = df["target"].map(lambda value: infer_company_name(original_file(value)))
    for col in ["model", "prompt", "aspect", "tone", "sentiment", "aspect_category"]:
        if col not in df.columns:
            df[col] = ""
    df["record_id"] = [f"packaged_{idx:06d}" for idx in range(len(df))]
    df["phase"] = "Phase 3"
    df["source_dataset"] = "data_output"
    return df


def phase_view() -> pd.DataFrame:
    df = _phase_from_revision_data()
    if df.empty:
        df = _phase_from_packaged_data()
    if df.empty:
        return pd.DataFrame(columns=["record_id", "target", "phase", "source_dataset"])
    return df.reset_index(drop=True)
