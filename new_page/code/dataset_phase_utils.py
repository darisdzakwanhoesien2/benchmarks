from __future__ import annotations

from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "results" / "revision_analysis"
RESULTS = ROOT / "results"
DATA = ROOT / "data"

ANNOTATION_PATH = REV / "pilot_ground_truth_annotations.csv"
SILVER_PATH = REV / "silver_tone_ground_truth.csv"
ESG_RECORDS_PATH = RESULTS / "esg_records.json"
LLM_JOBS_DIR = RESULTS / "background_llm_jobs"
PHASE_REGISTRY_PATH = REV / "dataset_phase_registry.csv"
TICKER_UNIVERSE_PATH = DATA / "indonesia_tickers.csv"

PHASES = ["Phase 1", "Phase 2", "Phase 3"]
CORE_GT_COLS = ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect"]
OPTIONAL_QA_COLS = ["review_status", "annotator", "review_notes"]
REGISTRY_COLS = ["record_id", "phase", "phase_reason", "first_seen_at", "updated_at", "updated_by"]
PDF_METADATA_OVERRIDES = {
    "alfamart_sustainability_2025_pdf": {"company_name": "Alfamart", "report_year": "2025", "ticker": "AMRT"},
    "wika_beton_SR-WTON-2025_pdf": {"company_name": "WIKA Beton", "report_year": "2025", "ticker": "WTON"},
    "SR-Bank-Aladin-Syariah-2025_pdf": {"company_name": "Bank Aladin Syariah", "report_year": "2025", "ticker": "BANK"},
    "ABM_2025_ABMM_SR_2025_pdf": {"company_name": "ABM Investama / ABMM", "report_year": "2025", "ticker": "ABMM"},
    "ARCI-SR-2025-E-reporting_pdf": {"company_name": "ARCI", "report_year": "2025", "ticker": "ARCI"},
    "waskita_karya_SR2025_pdf": {"company_name": "Waskita Karya", "report_year": "2025", "ticker": "WSKT"},
}


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "nat"}:
        return ""
    return text


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def parse_iso_time(value: str) -> datetime | None:
    text = clean(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def seconds_between(start: str, end: str) -> str:
    start_dt = parse_iso_time(start)
    end_dt = parse_iso_time(end)
    if start_dt is None or end_dt is None:
        return ""
    return str(round(max((end_dt - start_dt).total_seconds(), 0), 2))


def clean_int(value) -> int:
    text = clean(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except Exception:
        return 0


def clean_float(value) -> float:
    text = clean(value)
    if not text:
        return 0.0
    try:
        return float(text)
    except Exception:
        return 0.0


@lru_cache(maxsize=1)
def load_job_progress_lookup() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    if not LLM_JOBS_DIR.exists():
        return lookup
    for events_path in sorted(LLM_JOBS_DIR.glob("*/events.jsonl")):
        job_id = events_path.parent.name
        started_at = ""
        latest_terminal_at = ""
        total_targets = 0
        completed_targets = 0
        failed_targets = 0
        target_seconds = 0.0

        for event in read_jsonl(events_path):
            event_name = clean(event.get("event"))
            event_time = clean(event.get("time"))
            if event_name == "started":
                started_at = event_time or started_at
                total_targets = clean_int(event.get("total")) or total_targets
                continue
            if event_name not in {"completed", "failed"}:
                continue
            if event_name == "completed":
                completed_targets += 1
            elif event_name == "failed":
                failed_targets += 1
            target_seconds += clean_float(event.get("seconds"))
            if event_time and (not latest_terminal_at or event_time > latest_terminal_at):
                latest_terminal_at = event_time

        terminal_targets = completed_targets + failed_targets
        total = total_targets or terminal_targets
        if total and terminal_targets >= total:
            job_status = "completed" if failed_targets == 0 else "completed_with_failures"
        elif terminal_targets:
            job_status = "in_progress"
        else:
            job_status = "started" if started_at else "unknown"

        lookup[job_id] = {
            "job_started_at": started_at,
            "job_latest_event_at": latest_terminal_at,
            "job_total_targets": str(total) if total else "",
            "job_completed_targets": str(completed_targets),
            "job_failed_targets": str(failed_targets),
            "job_terminal_targets": str(terminal_targets),
            "job_completion_progress": f"{completed_targets}/{total} completed" if total else "",
            "job_llm_call_progress": f"{terminal_targets}/{total} LLM called" if total else "",
            "job_status": job_status,
            "job_elapsed_seconds": seconds_between(started_at, latest_terminal_at),
            "job_sum_target_seconds": str(round(target_seconds, 2)) if target_seconds else "",
        }
    return lookup


@lru_cache(maxsize=1)
def load_completed_event_lookup() -> dict[tuple[str, str, str, str], dict[str, str]]:
    lookup: dict[tuple[str, str, str, str], dict[str, str]] = {}
    if not LLM_JOBS_DIR.exists():
        return lookup
    for events_path in sorted(LLM_JOBS_DIR.glob("*/events.jsonl")):
        job_id = events_path.parent.name
        for event in read_jsonl(events_path):
            if clean(event.get("event")) != "completed":
                continue
            key = (
                job_id,
                clean(event.get("target")),
                clean(event.get("model")),
                clean(event.get("prompt")),
            )
            lookup[key] = {
                "success_event_timestamp": clean(event.get("time")),
                "success_event_records": clean(event.get("records")),
                "success_event_pages": clean(event.get("pages")),
                "success_event_seconds": clean(event.get("seconds")),
            }
    return lookup


def normalise_esg_value(value) -> str:
    raw = clean(value).lower()
    if not raw or raw in {"nan", "na", "n/a"}:
        return ""
    if raw in {"none", "unknown"}:
        return raw
    raw = (
        raw.replace("environmental", "e")
        .replace("environment", "e")
        .replace("social", "s")
        .replace("governance", "g")
        .replace("&", "-")
        .replace("/", "-")
        .replace(",", "-")
        .replace("+", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )
    parts = [part for part in raw.split("-") if part in {"e", "s", "g"}]
    ordered = [pillar for pillar in ["e", "s", "g"] if pillar in parts]
    return "-".join(ordered) if ordered else raw


def record_value(record: dict, *keys: str) -> str:
    if not isinstance(record, dict):
        return ""
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            value = "|".join(str(item) for item in value if clean(item))
        text = clean(value)
        if text:
            return text
    return ""


def stable_id(prefix: str, *parts) -> str:
    digest = hashlib.sha1("|".join(clean(part) for part in parts).encode("utf-8", errors="ignore")).hexdigest()
    return f"{prefix}_{digest[:12]}"


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
    if isinstance(value, list):
        return [clean(item) for item in value if clean(item)]
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
    if tickers.empty:
        return out
    for _, row in tickers.iterrows():
        ticker = clean(row.get("ticker")).upper()
        if not ticker:
            continue
        company_name = clean(row.get("company_name"))
        aliases = parse_aliases(row.get("aliases"))
        alias_values = [ticker, company_name, *aliases]
        out[ticker] = {
            "ticker": ticker,
            "company_name": company_name,
            "sector": clean(row.get("sector")),
            "aliases": [alias for alias in alias_values if clean(alias)],
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
    if not lookup_text:
        return ""
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
    company = text
    company = re.sub(r"_pdf$", "", company, flags=re.IGNORECASE)
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


def ensure_record_id(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out = df.copy()
    if "record_id" not in out.columns:
        out.insert(0, "record_id", [f"{prefix}_{idx:06d}" for idx in range(len(out))])
    out["record_id"] = out["record_id"].map(clean)
    out = out[out["record_id"].ne("")].copy()
    return out.drop_duplicates("record_id", keep="last")


def registry_created_at() -> str:
    registry = load_csv(PHASE_REGISTRY_PATH)
    if registry.empty or "first_seen_at" not in registry.columns:
        return ""
    values = [clean(value) for value in registry["first_seen_at"].tolist() if clean(value)]
    return min(values) if values else ""


def load_live_llm_records() -> pd.DataFrame:
    runs = read_json(ESG_RECORDS_PATH, [])
    if not isinstance(runs, list):
        return pd.DataFrame()

    completed_events = load_completed_event_lookup()
    job_progress = load_job_progress_lookup()
    rows: list[dict] = []
    for run_idx, run in enumerate(runs):
        if not isinstance(run, dict):
            continue
        records = run.get("records") if isinstance(run.get("records"), list) else []
        target = clean(run.get("target"))
        model = clean(run.get("model"))
        prompt = clean(run.get("prompt"))
        job_id = clean(run.get("background_job_id"))
        completed_meta = completed_events.get((job_id, target, model, prompt), {})
        job_meta = job_progress.get(job_id, {})
        company = target.split("/", 1)[0].replace("_pdf", "").replace("_PDF", "")
        for record_idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            text = record_value(record, "text", "sentence", "statement", "disclosure", "evidence")
            tone = record_value(record, "tone", "tone_pred", "disclosure_tone").lower()
            esg = normalise_esg_value(record_value(record, "esg", "pillar", "ground_truth_esg"))
            aspect = record_value(record, "aspect", "topic", "esg_aspect")
            rows.append(
                {
                    "record_id": stable_id(
                        "llm",
                        job_id,
                        model,
                        target,
                        prompt,
                        record_idx,
                        text[:200],
                    ),
                    "source_dataset": "live_llm_reprocess",
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": clean(run.get("timestamp")),
                    "success_event_timestamp": clean(completed_meta.get("success_event_timestamp")),
                    "success_event_records": clean(completed_meta.get("success_event_records")),
                    "success_event_pages": clean(completed_meta.get("success_event_pages")),
                    "success_event_seconds": clean(completed_meta.get("success_event_seconds")),
                    **job_meta,
                    "model": model,
                    "prompt": prompt,
                    "target": target,
                    "company": company,
                    "text": text,
                    "tone_pred": tone,
                    "suggested_tone": tone,
                    "ground_truth_tone": "",
                    "ground_truth_esg": "",
                    "ground_truth_aspect": "",
                    "esg": esg,
                    "aspect": aspect,
                    "review_status": "",
                    "annotator": "",
                    "review_notes": "",
                    "background_job_id": job_id,
                }
            )
    return pd.DataFrame(rows)


def load_background_llm_event_rows() -> pd.DataFrame:
    cutoff = registry_created_at()
    if not LLM_JOBS_DIR.exists() or not cutoff:
        return pd.DataFrame()

    job_progress = load_job_progress_lookup()
    rows: list[dict] = []
    for events_path in sorted(LLM_JOBS_DIR.glob("*/events.jsonl")):
        job_id = events_path.parent.name
        for event_idx, event in enumerate(read_jsonl(events_path)):
            event_name = clean(event.get("event"))
            event_time = clean(event.get("time"))
            if event_name not in {"completed", "failed"} or not event_time or event_time < cutoff:
                continue
            target = clean(event.get("target"))
            prompt = clean(event.get("prompt"))
            model = clean(event.get("model"))
            pages = clean(event.get("pages"))
            record_count = clean(event.get("records"))
            rows.append(
                {
                    "record_id": stable_id("llm_event", job_id, event_idx, event_name, target, prompt, model, pages),
                    "source_dataset": "background_llm_event",
                    "timestamp": event_time,
                    "model": model,
                    "prompt": prompt,
                    "target": target,
                    "company": target.split("/", 1)[0].replace("_pdf", "").replace("_PDF", ""),
                    "text": clean(event.get("error")) if event_name == "failed" else f"{record_count or '0'} parsed record(s) from {pages}",
                    "ground_truth_tone": "",
                    "ground_truth_esg": "",
                    "ground_truth_aspect": "",
                    "review_status": "",
                    "annotator": "",
                    "review_notes": "",
                    "background_job_id": job_id,
                    "event": event_name,
                    "event_records": record_count,
                    "target_pages": pages,
                    **job_progress.get(job_id, {}),
                }
            )
    return pd.DataFrame(rows)


def build_source_records() -> pd.DataFrame:
    annot = ensure_record_id(load_csv(ANNOTATION_PATH), "annot")
    silver = ensure_record_id(load_csv(SILVER_PATH), "silver")
    live_llm = ensure_record_id(load_live_llm_records(), "llm")
    llm_events = ensure_record_id(load_background_llm_event_rows(), "llm_event")

    if annot.empty and silver.empty:
        base = pd.DataFrame(columns=["record_id"])
    elif annot.empty:
        base = silver.copy()
        base["source_dataset"] = SILVER_PATH.name
    else:
        base = annot.copy()
        base["source_dataset"] = ANNOTATION_PATH.name
        if not silver.empty:
            missing_silver = silver[~silver["record_id"].isin(base["record_id"])].copy()
            if not missing_silver.empty:
                missing_silver["source_dataset"] = SILVER_PATH.name
                base = pd.concat([base, missing_silver], ignore_index=True, sort=False)

    for extra in [live_llm, llm_events]:
        if extra.empty:
            continue
        existing_ids = set(base["record_id"].astype(str)) if "record_id" in base.columns else set()
        incoming = extra[~extra["record_id"].astype(str).isin(existing_ids)].copy()
        if not incoming.empty:
            base = pd.concat([base, incoming], ignore_index=True, sort=False)

    for col in CORE_GT_COLS + OPTIONAL_QA_COLS + ["company", "model", "prompt", "target", "source_dataset", "text", "tone_pred", "esg", "aspect"]:
        if col not in base.columns:
            base[col] = ""

    for col in base.columns:
        if base[col].dtype == object:
            base[col] = base[col].map(clean)

    return base.drop_duplicates("record_id", keep="last").reset_index(drop=True)


def completion_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in CORE_GT_COLS + OPTIONAL_QA_COLS:
        if col not in out.columns:
            out[col] = ""

    out["has_ground_truth_tone"] = out["ground_truth_tone"].map(lambda value: bool(clean(value)))
    out["has_ground_truth_esg"] = out["ground_truth_esg"].map(lambda value: bool(clean(value)))
    out["has_ground_truth_aspect"] = out["ground_truth_aspect"].map(lambda value: bool(clean(value)))
    out["missing_core_fields"] = out.apply(
        lambda row: ", ".join(col for col in CORE_GT_COLS if not clean(row.get(col))),
        axis=1,
    )
    out["missing_qa_fields"] = out.apply(
        lambda row: ", ".join(col for col in OPTIONAL_QA_COLS if not clean(row.get(col))),
        axis=1,
    )
    out["phase1_ready"] = out["missing_core_fields"].map(lambda value: not clean(value))
    out["completion_status"] = out.apply(
        lambda row: "complete_with_qa"
        if row["phase1_ready"] and not clean(row["missing_qa_fields"])
        else ("ground_truth_complete" if row["phase1_ready"] else "needs_editing"),
        axis=1,
    )
    return out


def infer_initial_phase(row: pd.Series) -> str:
    if clean(row.get("source_dataset")) in {"live_llm_reprocess", "background_llm_event"}:
        return "Phase 3"
    return "Phase 1" if bool(row.get("phase1_ready")) else "Phase 2"


def save_registry(registry: pd.DataFrame) -> None:
    PHASE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = registry.copy()
    for col in REGISTRY_COLS:
        if col not in out.columns:
            out[col] = ""
    out[REGISTRY_COLS].to_csv(PHASE_REGISTRY_PATH, index=False)


def load_or_create_registry(source: pd.DataFrame | None = None) -> pd.DataFrame:
    if source is None:
        source = build_source_records()
    source = completion_flags(source)
    registry = load_csv(PHASE_REGISTRY_PATH)
    for col in REGISTRY_COLS:
        if col not in registry.columns:
            registry[col] = ""

    now = utc_now()
    existing_ids = set(registry["record_id"].map(clean))
    created_registry = registry.empty
    rows: list[dict] = []
    for _, row in source.iterrows():
        record_id = clean(row.get("record_id"))
        if not record_id or record_id in existing_ids:
            continue
        phase = infer_initial_phase(row) if created_registry else "Phase 3"
        reason = (
            "Initial registry inference from current ground-truth completeness"
            if created_registry
            else "New record detected after phase registry was created"
        )
        rows.append(
            {
                "record_id": record_id,
                "phase": phase,
                "phase_reason": reason,
                "first_seen_at": now,
                "updated_at": now,
                "updated_by": "phase_manager",
            }
        )

    if rows:
        registry = pd.concat([registry, pd.DataFrame(rows)], ignore_index=True, sort=False)
        save_registry(registry)

    registry = registry[REGISTRY_COLS].copy()
    registry["record_id"] = registry["record_id"].map(clean)
    registry["phase"] = registry["phase"].where(registry["phase"].isin(PHASES), "Phase 3")
    return registry.drop_duplicates("record_id", keep="last")


def phase_view() -> pd.DataFrame:
    source = completion_flags(build_source_records())
    registry = load_or_create_registry(source)
    view = source.merge(registry, on="record_id", how="left")
    view["phase"] = view["phase"].where(view["phase"].isin(PHASES), "Phase 3")
    return completion_flags(view)


def move_records(record_ids: list[str], target_phase: str, reason: str = "", updated_by: str = "phase_resolver") -> int:
    if target_phase not in PHASES or not record_ids:
        return 0
    registry = load_or_create_registry()
    mask = registry["record_id"].isin([clean(record_id) for record_id in record_ids])
    registry.loc[mask, "phase"] = target_phase
    registry.loc[mask, "phase_reason"] = reason or f"Moved to {target_phase}"
    registry.loc[mask, "updated_at"] = utc_now()
    registry.loc[mask, "updated_by"] = updated_by
    save_registry(registry)
    return int(mask.sum())


def complete_record_ids(df: pd.DataFrame) -> list[str]:
    flagged = completion_flags(df)
    return flagged.loc[flagged["phase1_ready"], "record_id"].map(clean).tolist()


def save_annotation_updates(updates: pd.DataFrame) -> int:
    if updates.empty or "record_id" not in updates.columns:
        return 0

    annot = load_csv(ANNOTATION_PATH)
    if annot.empty:
        annot = pd.DataFrame(columns=["record_id"])
    for col in set(annot.columns).union(updates.columns):
        if col not in annot.columns:
            annot[col] = ""
    annot = annot.astype("object")
    mutable_cols = [
        "record_id",
        "run_idx",
        "record_idx",
        "timestamp",
        "model",
        "prompt",
        "target",
        "company",
        "ok",
        "text",
        "tone_pred",
        "esg",
        "aspect",
        "ground_truth_tone",
        "ground_truth_esg",
        "ground_truth_aspect",
        "review_status",
        "annotator",
        "review_notes",
        "source_dataset",
    ]
    for col in mutable_cols:
        if col not in annot.columns:
            annot[col] = ""
        if col not in updates.columns:
            updates[col] = ""

    annot = annot.set_index("record_id", drop=False)
    changed = 0
    for _, row in updates.iterrows():
        record_id = clean(row.get("record_id"))
        if not record_id:
            continue
        if record_id not in annot.index:
            blank_row = {col: "" for col in annot.columns}
            blank_row["record_id"] = record_id
            annot.loc[record_id] = blank_row
        for col in mutable_cols:
            value = clean(row.get(col))
            if col in CORE_GT_COLS + OPTIONAL_QA_COLS + ["text", "company", "model", "prompt", "target", "tone_pred", "esg", "aspect", "source_dataset"]:
                annot.loc[record_id, col] = value
        changed += 1

    if "ground_truth_esg" in annot.columns:
        annot["ground_truth_esg"] = annot["ground_truth_esg"].map(normalise_esg_value)
    ANNOTATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    annot.reset_index(drop=True).to_csv(ANNOTATION_PATH, index=False)
    return changed
