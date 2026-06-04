from io import StringIO
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from urllib.parse import urlparse

import altair as alt
import pandas as pd
import requests
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls

st.set_page_config(page_title="Thesis Action Plan", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
PAGES_DIR = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
VIS = RESULTS / "visualizations"
ARTIFACTS = ROOT / "results" / "revision_analysis"
REVISION = ARTIFACTS
CLIMATEBERT_JOBS = ROOT / "results" / "climatebert_background_jobs"
CLIMATEBERT_WORKER = ROOT / "code" / "climatebert_background_worker.py"
ROOT_MODELS_DIR = ROOT.parent / "model_download" / "models"
DATASET_DIR = ROOT / "data" / "thesis_dataset"
PROMPT_DIR = ROOT / "prompt"
LLM_JOBS_DIR = ROOT / "results" / "background_llm_jobs"
LLM_WORKER = ROOT / "code" / "llm_background_worker.py"
MODELS_CACHE_PATH = PAGES_DIR / "models_cache.json"
DASHBOARD_SOURCE_PAGE = PAGES_DIR / "5_Thesis_Systematic_Workflow_dashboard.py"

SILVER_PATH       = ARTIFACTS / "silver_tone_ground_truth.csv"
ANNOTATION_PATH   = ARTIFACTS / "pilot_ground_truth_annotations.csv"
SEED_PATH         = ARTIFACTS / "pilot_ground_truth_seed.csv"
PROXY_PATH        = ARTIFACTS / "climatebert_proxy_agreement_records.csv"
CLIMATEBERT_OUTPUT_PATH = ARTIFACTS / "climatebert_output.csv"
IMPORTED_PATH     = ARTIFACTS / "climatebert_record_batch_import.csv"
ONTOLOGY_PATH     = ARTIFACTS / "ontology_coverage.csv"
PROMPT_STAB_PATH  = ARTIFACTS / "prompt_stability_summary.csv"
MODEL_STAB_PATH   = ARTIFACTS / "model_stability_summary.csv"
OCR_PATH          = ARTIFACTS / "ocr_processing_summary.csv"
FAILURE_PATH      = ARTIFACTS / "failure_modes.csv"
FAIL_CNT_PATH     = ARTIFACTS / "failure_mode_counts.csv"
GAP_AUDIT_PATH    = ARTIFACTS / "gap_audit_snapshot.csv"
PHASE_REGISTRY_PATH = ARTIFACTS / "dataset_phase_registry.csv"
CLUSTER_PATH           = ARTIFACTS / "aspect_clusters.csv"
ONTOLOGY_MISSING_LABELS_PATH = ARTIFACTS / "ontology_missing_aspect_labels.csv"
NOVEL_ASPECT_REVIEW_PATH = ARTIFACTS / "ontology_novel_aspect_review.csv"
A28_GENERAL_MISC_REVIEW_PATH = ARTIFACTS / "ground_truth_a28_general_misc_review.csv"
T2_TONE_SENTIMENT_REVIEW_PATH = ARTIFACTS / "ground_truth_t2_tone_sentiment_review.csv"
T2_UNMAPPED_TOPIC_SUGGESTIONS_PATH = ARTIFACTS / "ground_truth_t2_unmapped_topic_suggestions.csv"
T2_UNMAPPED_MAPPING_CANDIDATES_PATH = ARTIFACTS / "ground_truth_t2_unmapped_mapping_candidates.csv"
PROMPT_BY_RUN_PATH     = ARTIFACTS / "prompt_stability_by_run.csv"
CHAPTER_RESOLUTION_PATH = ARTIFACTS / "chapter_4_6_resolution_decisions.json"
CHAPTER_RESOLUTION_EXPORT_PATH = ARTIFACTS / "chapter_4_6_resolution_board.csv"
CHAPTER_TONE_DENOMINATOR_PATH = ARTIFACTS / "chapter4_tone_denominator_audit.csv"
CHAPTER_ONTOLOGY_TOP_UNMAPPED_PATH = ARTIFACTS / "chapter6_top_unmapped_ontology_candidates.csv"
CHAPTER_BENCHMARK_GAP_PATH = ARTIFACTS / "chapter6_benchmark_gap_positioning.csv"
CH46_PAGE_PATH = PAGES_DIR / "6_4_ch4-6.py"
NOTES_PATH             = PAGES_DIR / "notes.md"
ANNOTATION_TARGET = 250

THESIS_TONE_TOTAL_RECORDS = 5444
THESIS_TONE_COMPLETED_RECORDS = 4853
THESIS_TONE_MISSING_RECORDS = 591
CLIMATEBERT_MAJORITY_BASELINE = 0.654

CH46_INTEGRATION_ARTIFACTS = {
    "Chapter 4-6 resolution board": CHAPTER_RESOLUTION_EXPORT_PATH,
    "Tone denominator audit": CHAPTER_TONE_DENOMINATOR_PATH,
    "Top unmapped ontology candidates": CHAPTER_ONTOLOGY_TOP_UNMAPPED_PATH,
    "Benchmark gap positioning": CHAPTER_BENCHMARK_GAP_PATH,
}

TONE_OPTS   = ["", "commitment", "action", "outcome", "none", "unknown"]
ESG_OPTS    = ["", "e", "s", "g", "e-s", "e-g", "s-g", "e-s-g", "none", "unknown"]
STATUS_OPTS = ["needs_review", "reviewed", "uncertain", "discard"]
NOVEL_ASPECT_STATUS_OPTS = [
    "needs_review",
    "confirmed_novel",
    "mapped_existing",
    "placeholder",
    "not_esg",
    "merge_duplicate",
    "discard",
]
A28_REVIEW_STATUS_OPTS = [
    "needs_review",
    "relabelled",
    "confirmed_general_misc",
    "not_esg",
    "insufficient_context",
    "discard",
]
T2_REVIEW_STATUS_OPTS = [
    "needs_review",
    "relabelled",
    "confirmed",
    "not_esg",
    "insufficient_context",
    "discard",
]
T2_TONE_OPTS = ["", "Commitment", "Action", "Outcome", "Unknown", "Unclassified / Unknown"]
T2_SENTIMENT_OPTS = ["", "Neutral", "Positive", "Negative", "Unclassified / Unknown"]

FAILURE_MODES = [
    "Bilingual code-switching", "Hedged modal verb", "Table / numeric data loss",
    "Scanned page / low OCR quality", "Generic boilerplate statement", "Diacritics error",
    "Missing required schema field", "Schema drift", "Empty / truncated text",
    "Multiple aspects merged into one",
]

CLUSTER_NAMES = [
    "Community Relations",
    "Regulatory Compliance",
    "Supply Chain",
    "Human Capital",
    "Energy & Climate",
    "Waste & Pollution",
    "Governance & Ethics",
    "Financial Sustainability",
    "Digital & Data",
    "Biodiversity & Land",
    "Other",
]

COL_ALIASES = {
    "tone": "ground_truth_tone", "ground_truth_tone": "ground_truth_tone",
    "esg": "ground_truth_esg", "pillar": "ground_truth_esg", "ground_truth_esg": "ground_truth_esg",
    "aspect": "ground_truth_aspect", "ground_truth_aspect": "ground_truth_aspect",
    "status": "review_status", "review_status": "review_status",
    "annotator": "annotator", "notes": "review_notes", "review_notes": "review_notes",
}

CLIMATEBERT_SCRIPT = '''\
# Run this on your laptop or in Google Colab (free GPU).
# Install once: pip install transformers pandas torch

from transformers import pipeline
import pandas as pd

df = pd.read_csv("climatebert_332_record_batch_input.csv")

classifier = pipeline(
    "text-classification",
    model="climatebert/distilroberta-base-climate-commitment",
)

results = []
for _, row in df.iterrows():
    text = str(row["text"])[:512]   # model max length
    out  = classifier(text)[0]
    results.append({
        "record_id":           row["record_id"],
        "label":               out["label"],
        "score":               round(out["score"], 4),
        "climate_commitment":  out["label"].lower() in ("yes", "1", "commitment"),
    })

pd.DataFrame(results).to_csv("climatebert_output.csv", index=False)
print("Done — upload climatebert_output.csv back to this page.")
'''


def load(p):
    p = Path(p)
    return pd.read_csv(p).fillna("") if p.exists() else pd.DataFrame()


def load_gap_audit(default_rows):
    saved = load(GAP_AUDIT_PATH)
    if saved.empty:
        return default_rows.copy()
    base = default_rows.copy()
    if "gap_id" not in saved.columns or "gap_id" not in base.columns:
        return saved
    base = base.set_index("gap_id", drop=False)
    saved = saved.set_index("gap_id", drop=False)
    shared = base.index.intersection(saved.index)
    for col in saved.columns:
        if col in base.columns:
            incoming = saved.loc[shared, col].astype(str).fillna("")
            use_mask = incoming.str.strip().ne("")
            if use_mask.any():
                base.loc[shared[use_mask], col] = incoming[use_mask]
    missing = saved.loc[~saved.index.isin(base.index)].copy()
    out = pd.concat([base, missing], axis=0, ignore_index=True)
    return out.fillna("")


def utc_now_id():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def read_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def read_events(path):
    path = Path(path)
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return pd.DataFrame(rows)


def climatebert_jobs():
    if not CLIMATEBERT_JOBS.exists():
        return []
    return sorted([p.name for p in CLIMATEBERT_JOBS.iterdir() if p.is_dir()], reverse=True)


def is_alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def launch_climatebert_job(job_id):
    job_dir = CLIMATEBERT_JOBS / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    with (job_dir / "worker.log").open("ab") as stdout, (job_dir / "worker.err.log").open("ab") as stderr:
        proc = subprocess.Popen(
            [sys.executable, str(CLIMATEBERT_WORKER), job_id],
            cwd=str(ROOT),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    status = read_json(job_dir / "status.json", {})
    status.update({"job_id": job_id, "pid": proc.pid, "status": "running", "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"})
    write_json(job_dir / "status.json", status)


def request_climatebert_stop(job_id):
    control_path = CLIMATEBERT_JOBS / job_id / "control.json"
    control = read_json(control_path, {})
    control["stop_requested"] = True
    control["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    write_json(control_path, control)


def list_documents():
    if not DATASET_DIR.exists():
        return []
    return sorted(path.name for path in DATASET_DIR.iterdir() if (path / "pages").exists())


def list_pages(document):
    pages_dir = DATASET_DIR / document / "pages"
    if not pages_dir.exists():
        return []
    return [path.name for path in sorted(pages_dir.glob("*.md"))]


def list_prompts():
    if not PROMPT_DIR.exists():
        return []
    return [path.name for path in sorted(PROMPT_DIR.glob("*.md"))]


def fallback_llm_models():
    cached = read_json(MODELS_CACHE_PATH, [])
    if isinstance(cached, list) and cached:
        return [str(model).strip() for model in cached if str(model).strip()]
    return [
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-3-27b-it:free",
        "openai/gpt-4o-mini",
    ]


def normalize_openai_base_url(url):
    url = (url or "").strip().rstrip("/")
    if not url:
        return "http://127.0.0.1:1234/v1"
    for suffix in ("/models", "/chat/completions", "/completions", "/responses", "/embeddings"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc and not parsed.path:
        url = f"{url}/v1"
    return url.rstrip("/")


def normalize_ollama_base_url(url):
    url = (url or "").strip().rstrip("/")
    if not url:
        return "http://127.0.0.1:11434"
    for suffix in ("/api/tags", "/api/chat", "/api/generate", "/api/show", "/api/ps"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url.rstrip("/")


def bearer_headers(api_key=""):
    headers = {"Content-Type": "application/json"}
    if str(api_key).strip():
        headers["Authorization"] = f"Bearer {str(api_key).strip()}"
    return headers


@st.cache_data(ttl=300, show_spinner=False)
def fetch_lmstudio_models(base_url, api_key=""):
    try:
        base = normalize_openai_base_url(base_url)
        resp = requests.get(f"{base}/models", headers=bearer_headers(api_key), timeout=8)
        resp.raise_for_status()
        return [str(row.get("id")) for row in resp.json().get("data", []) if row.get("id")]
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ollama_models(base_url, api_key=""):
    try:
        base = normalize_ollama_base_url(base_url)
        resp = requests.get(f"{base}/api/tags", headers=bearer_headers(api_key), timeout=8)
        resp.raise_for_status()
        return sorted(
            str(row.get("name") or row.get("model"))
            for row in resp.json().get("models", [])
            if row.get("name") or row.get("model")
        )
    except Exception:
        return []


def selectable_models_for_backend(backend, lmstudio_url="", lmstudio_api_key="", ollama_url="", ollama_api_key=""):
    if backend == "Mock":
        return ["mock-model"]
    if backend == "LM Studio / OpenAI-compatible":
        return fetch_lmstudio_models(lmstudio_url, lmstudio_api_key)
    if backend == "Ollama":
        return fetch_ollama_models(ollama_url, ollama_api_key)
    return fallback_llm_models()


def launch_llm_job(job_id):
    job_dir = LLM_JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    with (job_dir / "worker.log").open("ab") as stdout, (job_dir / "worker.err.log").open("ab") as stderr:
        proc = subprocess.Popen(
            [sys.executable, str(LLM_WORKER), job_id],
            cwd=str(ROOT),
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    status = read_json(job_dir / "status.json", {})
    status.update({"job_id": job_id, "pid": proc.pid, "status": "running", "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"})
    write_json(job_dir / "status.json", status)


def llm_jobs():
    if not LLM_JOBS_DIR.exists():
        return []
    return sorted([path.name for path in LLM_JOBS_DIR.iterdir() if path.is_dir()], reverse=True)


def load_llm_records():
    rows = []
    esg_path = ROOT / "results" / "esg_records.json"
    if esg_path.exists():
        data = read_json(esg_path, [])
        if isinstance(data, list):
            for row in data:
                if isinstance(row, dict):
                    records = row.get("records") if isinstance(row.get("records"), list) else []
                    rows.append(
                        {
                            "target_doc": str(row.get("target", "")).split("/")[0],
                            "target": row.get("target", ""),
                            "prompt": row.get("prompt", ""),
                            "model": row.get("model", ""),
                            "ok": bool(row.get("ok")),
                            "records_count": len(records),
                            "background_job_id": row.get("background_job_id", ""),
                        }
                    )
    flat_path = ROOT / "results" / "visualizations" / "tone_records_flat.csv"
    if flat_path.exists():
        try:
            flat = pd.read_csv(flat_path).fillna("")
            if not flat.empty:
                group_cols = [c for c in ["target_doc", "target", "prompt", "model"] if c in flat.columns]
                if group_cols:
                    grouped = flat.groupby(group_cols).size().reset_index(name="records_count")
                    grouped["ok"] = True
                    grouped["background_job_id"] = "tone_records_flat"
                    rows.extend(grouped.to_dict("records"))
        except Exception:
            pass
    return pd.DataFrame(rows)


def load_esg_record_runs():
    data = read_json(ROOT / "results" / "esg_records.json", [])
    return data if isinstance(data, list) else []


def record_value(record, *keys):
    if not isinstance(record, dict):
        return ""
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            value = "|".join(str(item) for item in value if str(item).strip())
        if str(value or "").strip():
            return value
    return ""


def llm_runs_to_silver_rows():
    rows = []
    for run_idx, run in enumerate(load_esg_record_runs()):
        if not isinstance(run, dict):
            continue
        records = run.get("records") if isinstance(run.get("records"), list) else []
        target = str(run.get("target", "") or "")
        company = target.split("/", 1)[0].replace("_pdf", "").replace("_PDF", "")
        for record_idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            text = str(record_value(record, "text", "sentence", "statement", "disclosure", "evidence") or "")
            digest_src = "|".join(
                [
                    str(run.get("background_job_id", "")),
                    str(run.get("model", "")),
                    target,
                    str(run.get("prompt", "")),
                    str(record_idx),
                    text[:200],
                ]
            )
            record_id = "llm_" + hashlib.sha1(digest_src.encode("utf-8", errors="ignore")).hexdigest()[:12]
            labels = record_value(record, "labels", "label", "categories")
            tone = record_value(record, "tone", "tone_pred", "disclosure_tone")
            esg = normalise_esg_value(record_value(record, "esg", "pillar", "ground_truth_esg"))
            aspect = record_value(record, "aspect", "topic", "esg_aspect")
            sentiment = record_value(record, "sentiment", "polarity")
            score = pd.to_numeric(record_value(record, "sentiment_score", "score", "confidence"), errors="coerce")
            rows.append(
                {
                    "record_id": record_id,
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": run.get("timestamp", ""),
                    "model": run.get("model", ""),
                    "prompt": run.get("prompt", ""),
                    "target": target,
                    "company": company,
                    "ok": bool(run.get("ok")),
                    "text": text,
                    "text_len_chars": len(text),
                    "text_len_words": len(text.split()),
                    "language": "",
                    "aspect": aspect,
                    "esg": esg,
                    "tone_pred": str(tone).strip().lower(),
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "labels": labels,
                    "reasoning": record_value(record, "reasoning", "rationale", "explanation"),
                    "suggested_tone": str(tone).strip().lower(),
                    "suggestion_source": "llm_reprocess",
                    "silver_tone_ground_truth": str(tone).strip().lower(),
                    "needs_human_review": True,
                    "schema_drift": False,
                    "has_climate_commitment": "climate" in str(labels).lower() or "commitment" in str(tone).lower(),
                    "has_environmental_claims": "environment" in str(labels).lower() or esg == "e",
                    "has_climate_d": "climate-d" in str(labels).lower(),
                    "background_job_id": run.get("background_job_id", ""),
                    "target_pages": run.get("target_pages", ""),
                }
            )
    return pd.DataFrame(rows)


def append_new_rows(base_df, new_df):
    if new_df.empty:
        return base_df.copy()
    if base_df.empty:
        return new_df.copy()
    out = base_df.copy()
    for col in new_df.columns:
        if col not in out.columns:
            out[col] = ""
    for col in out.columns:
        if col not in new_df.columns:
            new_df[col] = ""
    if "record_id" in out.columns and "record_id" in new_df.columns:
        new_df = new_df[~new_df["record_id"].astype(str).isin(out["record_id"].astype(str))]
    return pd.concat([out, new_df[out.columns]], ignore_index=True)


def derive_model_stability_from_llm_runs():
    rows = []
    for run in load_esg_record_runs():
        if not isinstance(run, dict):
            continue
        records = run.get("records") if isinstance(run.get("records"), list) else []
        rows.append(
            {
                "model": run.get("model", ""),
                "ok": bool(run.get("ok")),
                "records_count": len(records),
                "missing_tone_count": sum(
                    1
                    for record in records
                    if isinstance(record, dict) and not str(record_value(record, "tone", "tone_pred", "disclosure_tone")).strip()
                ),
                "schema_drift": any(
                    isinstance(record, dict) and not str(record_value(record, "text", "sentence", "statement", "disclosure", "evidence")).strip()
                    for record in records
                ),
            }
        )
    df = pd.DataFrame(rows)
    if df.empty or "model" not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.groupby("model", dropna=False)
        .agg(
            runs=("model", "size"),
            json_parse_success_rate=("ok", "mean"),
            avg_records=("records_count", "mean"),
            missing_tone_count=("missing_tone_count", "sum"),
            record_total=("records_count", "sum"),
            schema_drift_rate=("schema_drift", "mean"),
        )
        .reset_index()
    )
    grouped["missing_tone_rate"] = grouped.apply(
        lambda row: (row["missing_tone_count"] / row["record_total"]) if row["record_total"] else 0,
        axis=1,
    )
    grouped["source"] = "live_reprocess"
    return grouped[["model", "runs", "json_parse_success_rate", "avg_records", "missing_tone_rate", "schema_drift_rate", "source"]]


def combine_model_stability(static_df, live_df):
    frames = []
    if not static_df.empty:
        static = static_df.copy()
        static["source"] = static.get("source", "revision_analysis")
        frames.append(static)
    if not live_df.empty:
        live = live_df.copy()
        if not static_df.empty and "source" in static_df.columns and "model" in static_df.columns:
            migrated_models = set(
                static_df.loc[
                    static_df["source"].astype(str).eq("live_reprocess"),
                    "model",
                ].astype(str)
            )
            if migrated_models and "model" in live.columns:
                live = live[~live["model"].astype(str).isin(migrated_models)]
        if not live.empty:
            frames.append(live)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    numeric_cols = ["runs", "json_parse_success_rate", "avg_records", "missing_tone_rate", "schema_drift_rate"]
    for col in numeric_cols:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")
    return combined


def migrate_live_reprocess_outputs(silver_df, live_silver_df, model_static_df, model_live_df):
    migrated = {"silver_rows": 0, "model_rows": 0}
    if not live_silver_df.empty:
        merged_silver = append_new_rows(silver_df, live_silver_df)
        SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
        merged_silver.to_csv(SILVER_PATH, index=False)
        migrated["silver_rows"] = len(merged_silver) - len(silver_df)

    if not model_live_df.empty:
        static = model_static_df.copy()
        if not static.empty:
            static["source"] = static.get("source", "revision_analysis")
            static = static[
                ~(
                    static["source"].astype(str).eq("live_reprocess")
                    & static["model"].astype(str).isin(model_live_df["model"].astype(str))
                )
            ]
        merged_models = pd.concat([static, model_live_df], ignore_index=True, sort=False).fillna("")
        MODEL_STAB_PATH.parent.mkdir(parents=True, exist_ok=True)
        merged_models.to_csv(MODEL_STAB_PATH, index=False)
        migrated["model_rows"] = len(model_live_df)

    return migrated


@st.cache_data(show_spinner=False)
def load_ground_truth_t2_outputs_for_a28():
    try:
        from ground_truth_graphs import load_t2_outputs

        return load_t2_outputs().fillna("")
    except Exception:
        return pd.DataFrame()


def normalize_ontology_path_text(value):
    return str(value or "").strip().replace("→", "->").replace("  ", " ").lower()


def stable_review_id(*parts):
    digest = hashlib.sha1(
        "|".join(str(part or "") for part in parts).encode("utf-8", errors="ignore")
    ).hexdigest()
    return f"a28_{digest[:12]}"


def a28_general_misc_candidates(t2_df):
    if t2_df.empty or "ontology_path" not in t2_df.columns:
        return pd.DataFrame()
    df = t2_df.copy()
    normalized_path = df["ontology_path"].map(normalize_ontology_path_text)
    view = df[normalized_path.str.contains("general -> misc", regex=False, na=False)].copy()
    if view.empty:
        return pd.DataFrame()
    if "review_id" not in view.columns:
        view["review_id"] = [
            stable_review_id(
                row.get("label", ""),
                row.get("timestamp", ""),
                row.get("sentence_text", row.get("text", "")),
                idx,
            )
            for idx, row in view.iterrows()
        ]
    view["current_ontology_path"] = view["ontology_path"].astype(str)
    text_source = first_nonempty_series(view, ["sentence_text", "text", "input_text"])
    view["text_for_review"] = text_source
    view["suggested_aspect"] = first_nonempty_series(view, ["rule_aspects", "section", "section_type"]).str.replace("|", " / ", regex=False)
    view["corrected_ontology_path"] = ""
    view["corrected_aspect"] = ""
    view["review_status"] = "needs_review"
    view["review_notes"] = ""
    keep = [
        "review_id",
        "label",
        "timestamp",
        "section",
        "section_type",
        "rule_aspects",
        "tone_pred",
        "sentiment_pred",
        "ontology_alignment",
        "current_ontology_path",
        "suggested_aspect",
        "corrected_aspect",
        "corrected_ontology_path",
        "review_status",
        "review_notes",
        "text_for_review",
    ]
    return view[[col for col in keep if col in view.columns]]


def t2_tone_sentiment_review_candidates(t2_df):
    if t2_df.empty:
        return pd.DataFrame()
    df = t2_df.copy()
    if "review_id" not in df.columns:
        df["review_id"] = [
            stable_review_id(
                row.get("label", ""),
                row.get("timestamp", ""),
                row.get("sentence_text", row.get("text", "")),
                idx,
            )
            for idx, row in df.iterrows()
        ]
    text_source = first_nonempty_series(df, ["sentence_text", "text", "input_text"])
    df["text_for_review"] = text_source
    if "ontology_path" not in df.columns:
        df["ontology_path"] = ""
    for col in ["rule_tone", "tone_pred", "sentiment_pred"]:
        if col not in df.columns:
            df[col] = ""
    df["corrected_rule_tone"] = ""
    df["corrected_hybrid_tone"] = ""
    df["corrected_sentiment"] = ""
    df["review_status"] = "needs_review"
    df["review_notes"] = ""
    tone_values = (
        df[["rule_tone", "tone_pred"]]
        .astype(str)
        .apply(lambda col: col.str.strip().str.lower())
    )
    sentiment_values = df["sentiment_pred"].astype(str).str.strip().str.lower()
    priority = (
        tone_values["rule_tone"].isin(["", "unknown", "unclassified / unknown", "none", "nan", "null"])
        | tone_values["tone_pred"].isin(["", "unknown", "unclassified / unknown", "none", "nan", "null"])
        | sentiment_values.isin(["", "neutral", "unclassified / unknown", "none", "nan", "null"])
        | tone_values["rule_tone"].ne(tone_values["tone_pred"])
    )
    df["review_priority"] = priority.map({True: "high", False: "normal"})
    keep = [
        "review_id",
        "label",
        "timestamp",
        "rule_tone",
        "tone_pred",
        "sentiment_pred",
        "corrected_rule_tone",
        "corrected_hybrid_tone",
        "corrected_sentiment",
        "review_status",
        "review_priority",
        "ontology_path",
        "ontology_alignment",
        "greenwashing_index",
        "review_notes",
        "text_for_review",
    ]
    return df[[col for col in keep if col in df.columns]]


def t2_unmapped_rows(t2_df):
    if t2_df.empty:
        return pd.DataFrame()
    df = t2_df.copy()
    if "ontology_path" not in df.columns:
        df["ontology_path"] = ""
    path_norm = df["ontology_path"].astype(str).str.strip().str.lower().str.replace("→", "->", regex=False)
    unmapped_mask = (
        path_norm.eq("")
        | path_norm.str.contains("general -> misc", regex=False, na=False)
        | path_norm.str.contains("misc", regex=False, na=False)
    )
    out = df[unmapped_mask].copy()
    if out.empty:
        return pd.DataFrame()
    out["text_for_topic"] = first_nonempty_series(out, ["sentence_text", "text", "input_text"]).astype(str)
    out["review_id"] = [
        stable_review_id(
            row.get("label", ""),
            row.get("timestamp", ""),
            row.get("text_for_topic", ""),
            idx,
        )
        for idx, row in out.iterrows()
    ]
    return out


def t2_recover_text_for_unmapped(unmapped_df):
    if unmapped_df.empty:
        return unmapped_df
    out = unmapped_df.copy()
    if "text_for_topic" in out.columns and out["text_for_topic"].astype(str).str.strip().ne("").any():
        return out
    try:
        raw = pd.read_json(ROOT / "results" / "t2_results.jsonl", lines=True).fillna("")
    except Exception:
        return out
    if raw.empty:
        return out
    raw["label_key"] = raw.get("label", "").astype(str).str.strip()
    raw["text_recovered"] = first_nonempty_series(raw, ["text", "sentence_text", "input_text"]).astype(str)
    out["label_key"] = out.get("label", "").astype(str).str.strip()
    join_cols = ["label_key", "text_recovered"]
    merged = out.merge(raw[join_cols].drop_duplicates("label_key", keep="last"), on="label_key", how="left")
    base_text = merged.get("text_for_topic", pd.Series([""] * len(merged))).astype(str)
    recovered = merged.get("text_recovered", pd.Series([""] * len(merged))).astype(str)
    merged["text_for_topic"] = base_text.where(base_text.str.strip().ne(""), recovered)
    return merged.drop(columns=[c for c in ["label_key", "text_recovered"] if c in merged.columns])


def t2_rule_based_mapping_candidates(unmapped_df):
    if unmapped_df.empty:
        return pd.DataFrame()
    out = unmapped_df.copy()
    txt = out.get("text_for_topic", pd.Series([""] * len(out))).astype(str).str.lower()
    sec = out.get("section", pd.Series([""] * len(out))).astype(str).str.lower()
    sec_type = out.get("section_type", pd.Series([""] * len(out))).astype(str).str.lower()
    aspects = out.get("rule_aspects", pd.Series([""] * len(out))).astype(str).str.lower()

    def map_path(i):
        t = txt.iloc[i]
        s = sec.iloc[i]
        st = sec_type.iloc[i]
        a = aspects.iloc[i]
        if any(k in t for k in ["emission", "carbon", "co2", "energy", "waste", "water"]) or "environment" in s:
            return "Environmental -> Climate and Emissions"
        if any(k in t for k in ["employee", "karyawan", "safety", "health", "community", "training"]) or "social" in s:
            return "Social -> Workforce and Community"
        if any(k in t for k in ["governance", "board", "audit", "compliance", "ethic", "corruption"]) or "governance" in s:
            return "Governance -> Ethics and Compliance"
        if "general" in a or "general" in st:
            return "General -> Corporate Sustainability Narrative"
        return ""

    out["pattern_path"] = [map_path(i) for i in range(len(out))]
    out["pattern_label"] = out["pattern_path"].astype(str).str.split("->").str[-1].str.strip()
    out["pattern_confidence"] = out["pattern_path"].astype(str).str.strip().ne("").map({True: 0.72, False: 0.0})
    return out


def t2_embedding_mapping_candidates(unmapped_df, ontology_df):
    if unmapped_df.empty:
        return pd.DataFrame()
    if ontology_df.empty or "aspect" not in ontology_df.columns:
        out = unmapped_df.copy()
        out["embed_path"] = ""
        out["embed_label"] = ""
        out["embed_similarity"] = 0.0
        return out
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except Exception:
        out = unmapped_df.copy()
        out["embed_path"] = ""
        out["embed_label"] = ""
        out["embed_similarity"] = 0.0
        return out

    candidates = ontology_df.copy()
    candidates["aspect"] = candidates["aspect"].astype(str).str.strip()
    candidates = candidates[~is_missing_aspect_series(candidates["aspect"])].copy()
    if candidates.empty:
        out = unmapped_df.copy()
        out["embed_path"] = ""
        out["embed_label"] = ""
        out["embed_similarity"] = 0.0
        return out
    candidates["cand_text"] = candidates["aspect"].astype(str)
    if "suggested_path" in candidates.columns:
        candidates["cand_text"] = candidates["cand_text"] + " " + candidates["suggested_path"].astype(str)

    out = unmapped_df.copy()
    out["text_for_topic"] = out.get("text_for_topic", "").astype(str)
    docs = out["text_for_topic"].fillna("").astype(str).tolist()
    refs = candidates["cand_text"].fillna("").astype(str).tolist()
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1, max_df=0.95)
    X = vec.fit_transform(docs + refs)
    dmat = X[: len(docs)]
    rmat = X[len(docs) :]
    sim = cosine_similarity(dmat, rmat)
    best_idx = sim.argmax(axis=1)
    best_sim = sim.max(axis=1)
    cand_aspect = candidates["aspect"].reset_index(drop=True)
    cand_path = candidates["suggested_path"].reset_index(drop=True) if "suggested_path" in candidates.columns else pd.Series([""] * len(candidates))
    out["embed_label"] = [str(cand_aspect.iloc[i]) for i in best_idx]
    out["embed_path"] = [str(cand_path.iloc[i]) for i in best_idx]
    out["embed_similarity"] = best_sim
    return out


def t2_reassess_tone_sentiment_suggestions(df):
    out = df.copy()
    text = out.get("text_for_topic", pd.Series([""] * len(out))).astype(str).str.lower()
    pos_kw = ["improve", "increase", "berhasil", "meningkat", "strong", "komitmen", "sustainab"]
    neg_kw = ["risk", "penalty", "fine", "incident", "kecelakaan", "gagal", "complaint", "violation"]
    commitment_kw = ["commit", "target", "akan", "will", "plan", "berkomitmen"]
    action_kw = ["implemented", "melakukan", "dilakukan", "program", "training", "audit"]
    outcome_kw = ["achieved", "reduced", "menurun", "hasil", "tercapai", "decreased"]

    def contains_any(t, keys):
        return any(k in t for k in keys)

    rule_s, hybrid_s, sent_s = [], [], []
    for t in text.tolist():
        if contains_any(t, outcome_kw):
            tone = "Outcome"
        elif contains_any(t, action_kw):
            tone = "Action"
        elif contains_any(t, commitment_kw):
            tone = "Commitment"
        else:
            tone = "Unknown"
        rule_s.append(tone)
        hybrid_s.append(tone)
        if contains_any(t, neg_kw):
            sent = "Negative"
        elif contains_any(t, pos_kw):
            sent = "Positive"
        else:
            sent = "Neutral"
        sent_s.append(sent)
    out["suggested_rule_tone"] = rule_s
    out["suggested_hybrid_tone"] = hybrid_s
    out["suggested_sentiment"] = sent_s
    return out


def t2_unmapped_mapping_pipeline(t2_df, ontology_df):
    base = t2_unmapped_rows(t2_df)
    base = t2_recover_text_for_unmapped(base)
    pattern = t2_rule_based_mapping_candidates(base)
    embed = t2_embedding_mapping_candidates(pattern, ontology_df)
    final = t2_reassess_tone_sentiment_suggestions(embed)
    if final.empty:
        return final
    final["proposed_ontology_path"] = final["pattern_path"].astype(str)
    use_embed = final["proposed_ontology_path"].astype(str).str.strip().eq("") & (pd.to_numeric(final["embed_similarity"], errors="coerce").fillna(0) >= 0.18)
    final.loc[use_embed, "proposed_ontology_path"] = final.loc[use_embed, "embed_path"].astype(str)
    final["proposed_t2_label"] = final["proposed_ontology_path"].astype(str).str.split("->").str[-1].str.strip()
    final.loc[final["proposed_t2_label"].eq(""), "proposed_t2_label"] = final.loc[final["proposed_t2_label"].eq(""), "embed_label"].astype(str)
    final["mapping_method"] = "pattern"
    final.loc[use_embed, "mapping_method"] = "embedding_fallback"
    final["mapping_confidence"] = final["pattern_confidence"]
    final.loc[use_embed, "mapping_confidence"] = final.loc[use_embed, "embed_similarity"].clip(0, 1)
    final["review_status"] = "needs_review"
    final["review_notes"] = ""
    return final
def t2_topic_mining(unmapped_df, n_topics=8, top_terms=12, min_df=5):
    if unmapped_df.empty or "text_for_topic" not in unmapped_df.columns:
        return pd.DataFrame(), pd.DataFrame(), "No unmapped rows available for topic mining."
    try:
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import CountVectorizer
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), "scikit-learn is not available in this environment."

    texts = unmapped_df["text_for_topic"].astype(str).str.strip()
    texts = texts[texts.ne("")]
    if len(texts) < 5:
        return pd.DataFrame(), pd.DataFrame(), f"Not enough non-empty unmapped text rows for topic mining (found {len(texts)})."

    effective_min_df = max(2, int(min_df))
    if len(texts) < effective_min_df:
        effective_min_df = 2 if len(texts) >= 2 else 1

    vectorizer = CountVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=effective_min_df,
        max_df=0.9,
    )
    X = vectorizer.fit_transform(texts)
    if X.shape[1] == 0:
        return pd.DataFrame(), pd.DataFrame(), "No usable vocabulary after preprocessing."

    n_topics_eff = min(
        max(2, int(n_topics)),
        max(2, min(12, X.shape[0] // 20 + 1)),
        max(2, min(20, X.shape[1])),
    )
    lda = LatentDirichletAllocation(n_components=n_topics_eff, random_state=42, learning_method="batch")
    doc_topic = lda.fit_transform(X)
    vocab = vectorizer.get_feature_names_out()

    topic_rows = []
    for topic_id, comp in enumerate(lda.components_):
        top_idx = comp.argsort()[::-1][: int(top_terms)]
        terms = [vocab[i] for i in top_idx]
        topic_rows.append(
            {
                "topic_id": topic_id,
                "top_terms": ", ".join(terms),
                "support_docs": int((doc_topic.argmax(axis=1) == topic_id).sum()),
                "proposed_t2_label": "",
                "proposed_keywords_csv": ", ".join(terms[:8]),
                "review_status": "needs_review",
                "review_notes": "",
            }
        )

    topic_df = pd.DataFrame(topic_rows).sort_values("support_docs", ascending=False).reset_index(drop=True)

    texts_df = unmapped_df.loc[texts.index].copy()
    dominant = doc_topic.argmax(axis=1)
    confidence = doc_topic.max(axis=1)
    texts_df = texts_df.reset_index(drop=True)
    texts_df["topic_id"] = dominant
    texts_df["topic_confidence"] = confidence
    text_cols = [c for c in ["review_id", "label", "timestamp", "tone_pred", "sentiment_pred", "ontology_path"] if c in texts_df.columns]
    text_cols += ["topic_id", "topic_confidence", "text_for_topic"]
    return topic_df, texts_df[text_cols], ""


def merge_a28_general_misc_review(candidates, saved):
    if candidates.empty:
        return candidates
    out = candidates.copy()
    if saved.empty or "review_id" not in saved.columns:
        return out
    saved_latest = saved.drop_duplicates("review_id", keep="last").set_index("review_id")
    out = out.set_index("review_id", drop=False)
    shared = out.index.intersection(saved_latest.index)
    editable_cols = [
        "corrected_aspect",
        "corrected_ontology_path",
        "review_status",
        "review_notes",
        "suggested_aspect",
    ]
    for col in editable_cols:
        if col in saved_latest.columns and col in out.columns:
            incoming = saved_latest.loc[shared, col].astype(str)
            if col == "review_status":
                valid = incoming.isin(A28_REVIEW_STATUS_OPTS)
                out.loc[valid[valid].index, col] = incoming.loc[valid]
            else:
                use = incoming.str.strip().ne("")
                out.loc[use[use].index, col] = incoming.loc[use]
    return out.reset_index(drop=True)


def merge_t2_tone_sentiment_review(candidates, saved):
    if candidates.empty:
        return candidates
    out = candidates.copy()
    if saved.empty or "review_id" not in saved.columns:
        return out
    saved_latest = saved.drop_duplicates("review_id", keep="last").set_index("review_id")
    out = out.set_index("review_id", drop=False)
    shared = out.index.intersection(saved_latest.index)
    editable_cols = [
        "corrected_rule_tone",
        "corrected_hybrid_tone",
        "corrected_sentiment",
        "review_status",
        "review_notes",
    ]
    for col in editable_cols:
        if col in saved_latest.columns and col in out.columns:
            incoming = saved_latest.loc[shared, col].astype(str)
            if col == "review_status":
                valid = incoming.isin(T2_REVIEW_STATUS_OPTS)
                out.loc[valid[valid].index, col] = incoming.loc[valid]
            else:
                use = incoming.str.strip().ne("")
                out.loc[use[use].index, col] = incoming.loc[use]
    return out.reset_index(drop=True)


def apply_t2_review_corrections(t2_df, review_df):
    if t2_df.empty or review_df.empty or "review_id" not in review_df.columns:
        return t2_df.copy()
    df = t2_tone_sentiment_review_candidates(t2_df).copy()
    saved = review_df.drop_duplicates("review_id", keep="last").set_index("review_id")
    df = df.set_index("review_id", drop=False)
    shared = df.index.intersection(saved.index)
    mapping = {
        "corrected_rule_tone": "rule_tone",
        "corrected_hybrid_tone": "tone_pred",
        "corrected_sentiment": "sentiment_pred",
    }
    for src, dst in mapping.items():
        if src in saved.columns and dst in df.columns:
            incoming = saved.loc[shared, src].astype(str).str.strip()
            use = incoming.ne("")
            df.loc[use[use].index, dst] = incoming.loc[use]
    return df.reset_index(drop=True)


def a28_review_summary(review_df):
    if review_df.empty:
        return pd.DataFrame()
    rows = []
    if "review_status" in review_df.columns:
        rows.extend(
            {"metric": f"status: {status}", "records": int(count)}
            for status, count in review_df["review_status"].astype(str).replace("", "needs_review").value_counts().items()
        )
    if "corrected_ontology_path" in review_df.columns:
        rows.append(
            {
                "metric": "corrected path filled",
                "records": int(review_df["corrected_ontology_path"].astype(str).str.strip().ne("").sum()),
            }
        )
    if "corrected_aspect" in review_df.columns:
        rows.append(
            {
                "metric": "corrected aspect filled",
                "records": int(review_df["corrected_aspect"].astype(str).str.strip().ne("").sum()),
            }
        )
    return pd.DataFrame(rows)


def t2_review_summary(review_df):
    if review_df.empty:
        return pd.DataFrame()
    rows = []
    if "review_status" in review_df.columns:
        rows.extend(
            {"metric": f"status: {status}", "records": int(count)}
            for status, count in review_df["review_status"].astype(str).replace("", "needs_review").value_counts().items()
        )
    for col in ["corrected_rule_tone", "corrected_hybrid_tone", "corrected_sentiment"]:
        if col in review_df.columns:
            rows.append(
                {
                    "metric": f"{col} filled",
                    "records": int(review_df[col].astype(str).str.strip().ne("").sum()),
                }
            )
    return pd.DataFrame(rows)


def safe_streamlit_page_name(raw_name):
    name = str(raw_name or "").strip()
    if not name:
        name = "5_1_Thesis_Systematic_Workflow_dashboard_generated.py"
    name = name.replace("/", "_").replace("\\", "_")
    if not name.endswith(".py"):
        name = f"{name}.py"
    safe = []
    for char in name:
        safe.append(char if char.isalnum() or char in {"_", "-", "."} else "_")
    return "".join(safe)


def dashboard_fallback_template(page_title):
    return f'''from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="{page_title}", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REVISION = RESULTS / "revision_analysis"
VIS = RESULTS / "visualizations"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


st.title("{page_title}")
st.caption("Generated from Thesis Action Plan. It reads current revision-analysis and visualization outputs.")

tone_records = load_csv(VIS / "tone_records_flat.csv")
model_stability = load_csv(REVISION / "model_stability_summary.csv")
prompt_stability = load_csv(REVISION / "prompt_stability_summary.csv")
ontology = load_csv(REVISION / "ontology_coverage.csv")
failure = load_csv(REVISION / "failure_mode_counts.csv")

cols = st.columns(5)
cols[0].metric("Tone records", f"{{len(tone_records):,}}")
cols[1].metric("Models", f"{{model_stability['model'].nunique() if 'model' in model_stability.columns else 0:,}}")
cols[2].metric("Prompts", f"{{len(prompt_stability):,}}")
cols[3].metric("Ontology rows", f"{{len(ontology):,}}")
cols[4].metric("Failure rows", f"{{len(failure):,}}")

tab1, tab2, tab3 = st.tabs(["Tone Records", "Model Stability", "Prompt Stability"])

with tab1:
    if tone_records.empty:
        st.info("No tone records found.")
    else:
        st.dataframe(tone_records, use_container_width=True, height=360)
        if "tone" in tone_records.columns:
            counts = tone_records["tone"].astype(str).replace("", "missing").value_counts().reset_index()
            counts.columns = ["tone", "count"]
            chart = alt.Chart(counts).mark_bar().encode(
                x=alt.X("count:Q"),
                y=alt.Y("tone:N", sort="-x"),
                tooltip=["tone", "count"],
            )
            st.altair_chart(chart, use_container_width=True)

with tab2:
    st.dataframe(model_stability, use_container_width=True, height=360)

with tab3:
    st.dataframe(prompt_stability, use_container_width=True, height=360)
'''


def create_workflow_dashboard_page(raw_name, overwrite=False):
    page_name = safe_streamlit_page_name(raw_name)
    target = PAGES_DIR / page_name
    if target.exists() and not overwrite:
        return target, False, "exists"
    if DASHBOARD_SOURCE_PAGE.exists():
        source = DASHBOARD_SOURCE_PAGE.read_text(encoding="utf-8", errors="ignore")
        header = (
            "# Generated from 3_0_Thesis_Action_Plan.py.\n"
            "# Source template: 5_Thesis_Systematic_Workflow_dashboard.py\n\n"
        )
        target.write_text(header + source, encoding="utf-8")
    else:
        title = page_name.replace(".py", "").replace("_", " ")
        target.write_text(dashboard_fallback_template(title), encoding="utf-8")
    return target, True, "created"


def looks_like_model_dir(p: Path) -> bool:
    return any((p / fn).exists() for fn in ("config.json", "pytorch_model.bin", "model.safetensors", "tf_model.h5"))


def find_all_model_dirs(root: Path):
    if not root.exists():
        return []
    found = set()
    for f in root.rglob("config.json"):
        if f.is_file():
            found.add(f.parent.resolve())
    for name in ("pytorch_model.bin", "model.safetensors", "tf_model.h5"):
        for f in root.rglob(name):
            if f.is_file():
                found.add(f.parent.resolve())
    return sorted(path for path in found if looks_like_model_dir(path))


def climatebert_family_from_model_name(model_name):
    text = str(model_name or "").lower()
    if "climatecontroversybert_classification" in text or "model_classification" in text:
        return "Climate controversy multiclass"
    if "climatecontroversybert" in text or "model_controversy" in text:
        return "Climate controversy binary"
    if "commitment" in text:
        return "Climate commitment binary"
    if "detector" in text:
        return "Climate detector binary"
    if "specificity" in text:
        return "Climate specificity binary"
    if "tcfd" in text:
        return "TCFD recommendation multiclass"
    if "environmental-claims" in text:
        return "Environmental claims binary"
    if "netzero" in text or "netzero-reduction" in text:
        return "Net-zero / reduction multiclass"
    if "transition-physical" in text:
        return "Transition / physical risk classifier"
    if "renewable" in text:
        return "Renewable-energy classifier"
    if "environmental" in text or "envroberta" in text:
        return "Environmental ESG binary"
    if "governance" in text or "govroberta" in text:
        return "Governance ESG binary"
    if "social" in text or "socroberta" in text:
        return "Social ESG binary"
    if any(token in text for token in ["climate-d", "climate-f", "climate-s"]):
        return "ClimateBERT base / masked language model"
    return "Other local transformer"


def climatebert_label_usage(model_name, label):
    family = climatebert_family_from_model_name(model_name)
    label_text = str(label or "").strip()
    label_l = label_text.lower()
    if label_text == "No classification labels in local config":
        return "Do not combine with A.4 label analysis unless a classification label map is added."
    if family == "Climate commitment binary":
        if label_l == "yes":
            return "Positive climate commitment/action class; compare only with commitment-style tone evidence."
        if label_l == "no":
            return "Negative commitment class; not equivalent to controversy, risk, or ESG pillar labels."
    if family == "Climate detector binary":
        if label_l == "yes":
            return "Climate-related text class; use as a filtering/detection step, not a commitment label."
        if label_l == "no":
            return "Non-climate text class; use only for climate relevance filtering."
    if family == "Environmental claims binary":
        if label_l == "yes":
            return "Environmental-claim class; use as environmental claim evidence, not commitment agreement."
        if label_l == "no":
            return "No environmental claim detected."
    if family == "Climate specificity binary":
        if label_l == "spec":
            return "Specific climate disclosure class."
        if label_l == "non":
            return "Non-specific climate disclosure class."
    if family == "TCFD recommendation multiclass":
        return "TCFD category label; use for climate-disclosure topic routing, not tone agreement."
    if family == "Climate controversy multiclass":
        return "Controversy subtype label; keep separate from binary commitment yes/no."
    if family == "Climate controversy binary":
        return "Binary controversy label; use as a controversy signal, not a commitment label."
    if family in {"Environmental ESG binary", "Governance ESG binary", "Social ESG binary"}:
        if label_l == "none":
            return "Negative class for this ESG pillar detector."
        return "Positive ESG pillar detector label."
    if family == "Net-zero / reduction multiclass":
        if label_l == "none":
            return "No net-zero or emissions-reduction target detected."
        return "Target subtype label for net-zero or emissions-reduction detection."
    if label_l.startswith("label_"):
        return "Generic config label; semantic mapping is not stored in the local model config and needs manual documentation before use."
    return "Local model label; inspect the model family before combining with A.4."


def climatebert_model_label_inventory(root: Path = ROOT_MODELS_DIR):
    rows = []
    if not root.exists():
        return pd.DataFrame(
            columns=["model", "model_path", "model family", "architecture", "model_type", "label_id", "label", "label source", "A.4 use guidance"]
        )
    for config_path in sorted(root.rglob("config.json")):
        if not config_path.is_file():
            continue
        try:
            config = json.loads(config_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            config = {}
        model_path = config_path.parent
        model_name = str(model_path.relative_to(root))
        architecture = ", ".join(config.get("architectures") or [])
        model_type = str(config.get("model_type") or "")
        id2label = config.get("id2label") if isinstance(config.get("id2label"), dict) else {}
        if id2label:
            for label_id, label in sorted(id2label.items(), key=lambda item: str(item[0])):
                rows.append(
                    {
                        "model": model_name,
                        "model_path": str(model_path),
                        "model family": climatebert_family_from_model_name(model_name),
                        "architecture": architecture,
                        "model_type": model_type,
                        "label_id": str(label_id),
                        "label": str(label),
                        "label source": "config.id2label",
                        "A.4 use guidance": climatebert_label_usage(model_name, label),
                    }
                )
            continue
        label2id = config.get("label2id") if isinstance(config.get("label2id"), dict) else {}
        if label2id:
            for label, label_id in sorted(label2id.items(), key=lambda item: str(item[1])):
                rows.append(
                    {
                        "model": model_name,
                        "model_path": str(model_path),
                        "model family": climatebert_family_from_model_name(model_name),
                        "architecture": architecture,
                        "model_type": model_type,
                        "label_id": str(label_id),
                        "label": str(label),
                        "label source": "config.label2id",
                        "A.4 use guidance": climatebert_label_usage(model_name, label),
                    }
                )
            continue
        rows.append(
            {
                "model": model_name,
                "model_path": str(model_path),
                "model family": climatebert_family_from_model_name(model_name),
                "architecture": architecture,
                "model_type": model_type,
                "label_id": "",
                "label": "No classification labels in local config",
                "label source": "config has no id2label/label2id",
                "A.4 use guidance": "Do not combine with A.4 label analysis unless a classification label map is added.",
            }
        )
    return pd.DataFrame(rows)


def cohen_kappa(a, b):
    pairs = [(str(x), str(y)) for x, y in zip(a, b) if str(x).strip() and str(y).strip()]
    if len(pairs) < 2:
        return None, 0
    n = len(pairs)
    labels = sorted({v for p in pairs for v in p})
    po = sum(1 for x, y in pairs if x == y) / n
    pe = sum(
        (sum(1 for x, _ in pairs if x == l) / n) *
        (sum(1 for _, y in pairs if y == l) / n)
        for l in labels
    )
    return (round((po - pe) / (1 - pe), 3) if (1 - pe) else 0.0), n


def kappa_label(k):
    if k is None: return "n/a"
    if k >= 0.80: return f"κ = {k:.3f} — strong ✅"
    if k >= 0.60: return f"κ = {k:.3f} — moderate 🟡"
    if k >= 0.40: return f"κ = {k:.3f} — fair 🟠"
    return f"κ = {k:.3f} — poor 🔴"


def pct(value):
    try:
        return f"{float(value):.1%}"
    except Exception:
        return "n/a"


def numeric_scalar(value, default=0.0):
    try:
        parsed = pd.to_numeric(value, errors="coerce")
        if pd.isna(parsed):
            return default
        return float(parsed)
    except Exception:
        return default


def tone_denominator_summary(total=THESIS_TONE_TOTAL_RECORDS, completed=THESIS_TONE_COMPLETED_RECORDS):
    missing = max(int(total) - int(completed), 0)
    return {
        "total": int(total),
        "completed": int(completed),
        "missing": missing,
        "completion_rate": float(completed / total) if total else 0.0,
        "missing_rate": float(missing / total) if total else 0.0,
    }


def _count_non_empty_csv_column(path: Path, column: str) -> tuple[int, int]:
    """Return (total_rows, non_empty_rows) for a CSV column, streaming rows to avoid pandas dependency at runtime."""
    import csv

    path = Path(path)
    if not path.exists():
        return (0, 0)
    total = 0
    non_empty = 0
    with path.open(newline="", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or column not in set(reader.fieldnames):
            return (0, 0)
        for row in reader:
            total += 1
            value = (row.get(column) or "").strip()
            if value:
                non_empty += 1
    return (total, non_empty)


def live_tone_denominator_summary() -> dict:
    """
    Prefer live counts from `pilot_ground_truth_annotations.csv` when available.
    Falls back to the thesis constants when the file is missing or schema changed.
    """
    total, completed = _count_non_empty_csv_column(ANNOTATION_PATH, "ground_truth_tone")
    if total:
        return tone_denominator_summary(total=total, completed=completed)
    return tone_denominator_summary()


def tone_denominator_policy_options(total=THESIS_TONE_TOTAL_RECORDS, completed=THESIS_TONE_COMPLETED_RECORDS):
    summary = tone_denominator_summary(total, completed)
    return pd.DataFrame(
        [
            {
                "decision": "exclude_from_agreement",
                "agreement denominator": summary["completed"],
                "tone distribution denominator": summary["completed"],
                "methodology implication": "Report missingness separately and compute tone agreement only on records with usable tone labels.",
                "recommended": True,
            },
            {
                "decision": "recode_as_none",
                "agreement denominator": summary["total"],
                "tone distribution denominator": summary["total"],
                "methodology implication": "Treat extraction failure as substantive absence of disclosure tone, which can inflate the none class.",
                "recommended": False,
            },
            {
                "decision": "separate_unclassifiable",
                "agreement denominator": summary["total"],
                "tone distribution denominator": summary["total"],
                "methodology implication": "Preserve failed tone extraction as an explicit quality category, not a disclosure tone.",
                "recommended": False,
            },
        ]
    )


def methodology_paragraph_for_missing_tone(policy, total=THESIS_TONE_TOTAL_RECORDS, completed=THESIS_TONE_COMPLETED_RECORDS):
    summary = live_tone_denominator_summary() if (total == THESIS_TONE_TOTAL_RECORDS and completed == THESIS_TONE_COMPLETED_RECORDS) else tone_denominator_summary(total, completed)
    if policy == "recode_as_none":
        return (
            f"Tone analysis used all {summary['total']:,} extracted records after recoding the "
            f"{summary['missing']:,} records without a returned tone label as `none`. This choice treats absent tone output "
            "as evidence that the statement did not contain a classifyable commitment, action, or outcome signal. "
            "Because this can increase the `none` category, all agreement and distribution tables report the recoding decision explicitly."
        )
    if policy == "separate_unclassifiable":
        return (
            f"Tone analysis retained all {summary['total']:,} extracted records and coded the "
            f"{summary['missing']:,} records without a returned tone label as `unclassifiable`. This separates model or schema failure "
            "from the substantive `none` tone category, allowing missingness to be audited without dropping evidence from denominator checks. "
            "Agreement statistics are reported both with and without the unclassifiable category where applicable."
        )
    return (
        f"Tone agreement and tone-distribution statistics were computed on the {summary['completed']:,} records with a valid tone label, "
        f"excluding the {summary['missing']:,} records ({summary['missing_rate']:.1%}) where the pipeline returned no tone value. "
        "The excluded records are reported as a data-quality outcome rather than recoded as `none`, because absence of a model output is not "
        "equivalent to a substantive no-tone disclosure. Therefore, Chapter 4 tables and figures that analyze tone use "
        f"{summary['completed']:,} as the effective tone-analysis denominator, while corpus coverage tables retain "
        f"{summary['total']:,} as the extraction denominator."
    )


def build_tone_denominator_audit(policy):
    summary = live_tone_denominator_summary()
    denominator = summary["completed"] if policy == "exclude_from_agreement" else summary["total"]
    return pd.DataFrame(
        [
            {"chapter element": "Corpus extraction coverage", "denominator": summary["total"], "included": summary["total"], "excluded": 0, "note": "Use for total extracted-record coverage."},
            {"chapter element": "Tone distribution", "denominator": denominator, "included": denominator, "excluded": summary["missing"] if policy == "exclude_from_agreement" else 0, "note": "Use this denominator in Chapter 4 tone tables and figures."},
            {"chapter element": "Tone agreement / kappa", "denominator": denominator, "included": denominator, "excluded": summary["missing"] if policy == "exclude_from_agreement" else 0, "note": "Do not compute agreement over missing tone outputs unless using an explicit unclassifiable class."},
            {"chapter element": "Missing-tone quality audit", "denominator": summary["total"], "included": summary["missing"], "excluded": summary["completed"], "note": "Report missingness as its own pipeline-quality result."},
        ]
    )


def proxy_agreement_summary(proxy_summary_df):
    if not proxy_summary_df.empty:
        row = proxy_summary_df.iloc[0]
        return {
            "n": int(numeric_scalar(row.get("n", 0), 0)),
            "percent_agreement": numeric_scalar(row.get("percent_agreement", 0), 0),
            "cohen_kappa": numeric_scalar(row.get("cohen_kappa", 0), 0),
            "tone_commitment_rate": numeric_scalar(row.get("tone_commitment_rate", 0), 0),
            "climate_commitment_label_rate": numeric_scalar(row.get("climate_commitment_label_rate", 0), 0),
        }
    return {
        "n": 332,
        "percent_agreement": 0.8373493975903614,
        "cohen_kappa": 0.6451446894422231,
        "tone_commitment_rate": 0.3463855421686747,
        "climate_commitment_label_rate": 0.3644578313253012,
    }


def climatebert_baseline_table(proxy_summary_df):
    summary = proxy_agreement_summary(proxy_summary_df)
    return pd.DataFrame(
        [
            {"metric": "Percent agreement", "value": summary["percent_agreement"], "display": pct(summary["percent_agreement"]), "interpretation": "Observed binary match rate between ABSA commitment-tone proxy and ClimateBERT climate-commitment label."},
            {"metric": "Cohen kappa", "value": summary["cohen_kappa"], "display": f"{summary['cohen_kappa']:.3f}", "interpretation": "Chance-adjusted agreement; this is model-framework agreement, not human inter-rater reliability."},
            {"metric": "Majority baseline", "value": CLIMATEBERT_MAJORITY_BASELINE, "display": pct(CLIMATEBERT_MAJORITY_BASELINE), "interpretation": "Naive always-commitment baseline supplied for A.15 framing."},
            {"metric": "Agreement lift over majority baseline", "value": summary["percent_agreement"] - CLIMATEBERT_MAJORITY_BASELINE, "display": f"{(summary['percent_agreement'] - CLIMATEBERT_MAJORITY_BASELINE) * 100:.1f} pp", "interpretation": "Pipeline improves over the naive baseline, but the comparison should be framed as adjacent-construct agreement."},
        ]
    )


def prompt_outlier_table(prompt_df):
    if prompt_df.empty or "prompt" not in prompt_df.columns:
        return pd.DataFrame(
            [{"prompt": "data.md", "missing_tone_rate": 1.0, "recommended decision": "retain_as_failed_experiment", "chapter use": "Evidence that prompt design affects output validity."}]
        )
    out = prompt_df.copy()
    if "missing_tone_rate" in out.columns:
        out["missing_tone_rate"] = pd.to_numeric(out["missing_tone_rate"], errors="coerce").fillna(0)
        out["is_failed_prompt"] = out["missing_tone_rate"].ge(1.0)
    else:
        out["missing_tone_rate"] = 0.0
        out["is_failed_prompt"] = False
    out["recommended decision"] = out["is_failed_prompt"].map({True: "retain_as_failed_experiment", False: "include_in_stability_summary"})
    out["chapter use"] = out["is_failed_prompt"].map(
        {
            True: "Treat as a failed prompt condition and discuss separately before any stability claim.",
            False: "Use in prompt stability comparison.",
        }
    )
    return out.sort_values(["is_failed_prompt", "missing_tone_rate"], ascending=[False, False])


def greenwashing_summary_table(greenwashing_df):
    if greenwashing_df.empty or "greenwashing_index" not in greenwashing_df.columns:
        return pd.DataFrame(
            [
                {"metric": "records", "value": 2071, "display": "2,071", "interpretation": "A.29 record count supplied for thesis framing."},
                {"metric": "mean", "value": 3380.0, "display": "3,380", "interpretation": "Mean is driven by extreme outliers."},
                {"metric": "median", "value": 0.0, "display": "0.0", "interpretation": "Median better represents the typical record."},
            ]
        )
    values = pd.to_numeric(greenwashing_df["greenwashing_index"], errors="coerce").dropna()
    if values.empty:
        return pd.DataFrame()
    rows = [
        {"metric": "records", "value": int(values.count()), "display": f"{int(values.count()):,}", "interpretation": "Rows with a numeric greenwashing index."},
        {"metric": "mean", "value": float(values.mean()), "display": f"{float(values.mean()):,.3g}", "interpretation": "Sensitive to extreme outliers."},
        {"metric": "median", "value": float(values.median()), "display": f"{float(values.median()):,.3g}", "interpretation": "Recommended primary statistic for skewed prototype metric."},
        {"metric": "max", "value": float(values.max()), "display": f"{float(values.max()):,.3g}", "interpretation": "Use to show tail heaviness."},
    ]
    if (values >= 0).all():
        import math

        rows.append(
            {
                "metric": "mean_log1p",
                "value": float(values.apply(lambda x: math.log1p(x)).mean()),
                "display": f"{float(values.apply(lambda x: math.log1p(x)).mean()):,.3g}",
                "interpretation": "Use log+1 transformation when charting the distribution.",
            }
        )
    return pd.DataFrame(rows)


def a19_confusion_narrative():
    return (
        "A.19 shows the largest substantive confusion around the boundary between realized outcomes and weaker disclosure tones. "
        "Outcome rows include 934 correct classifications but 101 cases assigned as action, indicating that the model sometimes "
        "reads implemented or measured results as activity language. The `none` row includes 1,781 correct classifications but "
        "223 cases assigned as commitment, showing a tendency to over-read generic sustainability language as forward-looking commitment. "
        "This should be interpreted as a claim-maturity boundary problem rather than a simple accuracy failure."
    )


def ontology_top_unmapped_table(full_ontology_df, novel_review_df, top_n=15):
    if full_ontology_df.empty:
        return pd.DataFrame()
    base = full_ontology_df.copy()
    mapped = ontology_bool(base["mapped_to_ontology"]) if "mapped_to_ontology" in base.columns else pd.Series([False] * len(base))
    base = base[~mapped].copy()
    if "aspect" in base.columns:
        base = base[~is_missing_aspect_series(base["aspect"])].copy()
    if "records" in base.columns:
        base["records"] = pd.to_numeric(base["records"], errors="coerce").fillna(0).astype(int)
    base["suggested_cluster"] = base["aspect"].map(suggest_aspect_cluster)
    base["suggested_gri_sasb_tcfd_node"] = base["aspect"].map(suggest_ontology_path)
    if not novel_review_df.empty and {"aspect", "ontology_path"}.issubset(novel_review_df.columns):
        reviewed_paths = (
            novel_review_df.drop_duplicates("aspect", keep="last")
            .set_index("aspect")["ontology_path"]
            .astype(str)
            .to_dict()
        )
        base["reviewed_ontology_path"] = base["aspect"].map(reviewed_paths).fillna("")
    keep = ["aspect", "records", "suggested_cluster", "suggested_gri_sasb_tcfd_node", "reviewed_ontology_path"]
    return base[[col for col in keep if col in base.columns]].sort_values("records", ascending=False).head(top_n)


def benchmark_gap_table():
    return pd.DataFrame(
        [
            {"benchmark": "FinBERT", "reported metric": "F1=97.3%", "handles finance/ESG language": "yes", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no", "positioning": "Strong domain classifier, but not the thesis niche."},
            {"benchmark": "ESG-BERT", "reported metric": "F1=88%", "handles finance/ESG language": "yes", "Indonesian": "no", "multi-aspect": "limited", "tone-labeled disclosure maturity": "no", "positioning": "Relevant ESG baseline without Indonesian multi-aspect tone coverage."},
            {"benchmark": "SpanEval", "reported metric": "F1=75.42%", "handles finance/ESG language": "partial", "Indonesian": "no", "multi-aspect": "yes", "tone-labeled disclosure maturity": "no", "positioning": "Useful extraction benchmark, but not a sustainability disclosure tone system."},
            {"benchmark": "ClimateBERT", "reported metric": "F1=1.16", "handles finance/ESG language": "climate-specific", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no", "positioning": "Adjacent climate NLP baseline; measures climate commitment, not ABSA tone maturity."},
            {"benchmark": "GH-ABSA", "reported metric": "accuracy=4.71", "handles finance/ESG language": "no", "Indonesian": "no", "multi-aspect": "yes", "tone-labeled disclosure maturity": "no", "positioning": "ABSA reference point, but not designed for Indonesian sustainability disclosures."},
            {"benchmark": "This thesis", "reported metric": "prototype system", "handles finance/ESG language": "yes", "Indonesian": "yes", "multi-aspect": "yes", "tone-labeled disclosure maturity": "yes", "positioning": "Niche contribution: Indonesian-language, multi-aspect, tone-labeled sustainability disclosure analysis."},
        ]
    )


def ch46_page_uses_artifact(filename):
    if not CH46_PAGE_PATH.exists():
        return False
    try:
        source = CH46_PAGE_PATH.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    constant_markers = {
        "chapter_4_6_resolution_board.csv": "CHAPTER_RESOLUTION_PATH",
        "chapter4_tone_denominator_audit.csv": "TONE_DENOMINATOR_AUDIT_PATH",
        "chapter6_top_unmapped_ontology_candidates.csv": "TOP_UNMAPPED_ONTOLOGY_PATH",
        "chapter6_benchmark_gap_positioning.csv": "BENCHMARK_GAP_PATH",
    }
    return filename in source or constant_markers.get(filename, "") in source


def ch46_integration_status_rows():
    rows = []
    for label, path in CH46_INTEGRATION_ARTIFACTS.items():
        rows.append(
            {
                "integration item": label,
                "artifact": str(path.relative_to(ROOT)),
                "artifact exists": path.exists(),
                "6_4_ch4-6.py consumes it": ch46_page_uses_artifact(path.name),
                "status": "Done" if path.exists() and ch46_page_uses_artifact(path.name) else "Needed",
            }
        )
    return pd.DataFrame(rows)


def normalise_cols(df):
    renamed = df.rename(columns={
        c: COL_ALIASES[c.lower().strip()]
        for c in df.columns if c.lower().strip() in COL_ALIASES
    })
    if renamed.columns.duplicated().any():
        merged = pd.DataFrame(index=renamed.index)
        for col in dict.fromkeys(renamed.columns):
            same = renamed.loc[:, renamed.columns == col]
            if same.shape[1] == 1:
                merged[col] = same.iloc[:, 0]
            else:
                merged[col] = same.bfill(axis=1).iloc[:, 0]
        renamed = merged
    if "ground_truth_esg" in renamed.columns:
        renamed["ground_truth_esg"] = renamed["ground_truth_esg"].map(normalise_esg_value)
    return renamed


def normalise_esg_value(value):
    raw = str(value or "").strip().lower()
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


def normalise_annotation_values(df):
    if df.empty:
        return df
    out = normalise_cols(df.copy())
    if "ground_truth_tone" in out.columns:
        out["ground_truth_tone"] = out["ground_truth_tone"].astype(str).str.strip().str.lower()
    if "review_status" in out.columns:
        out["review_status"] = out["review_status"].astype(str).str.strip().str.lower()
    return out


def build_annotation_table(silver_df, seed_df, annotation_df):
    if not silver_df.empty:
        base = silver_df.copy()
    elif not seed_df.empty:
        base = seed_df.copy()
    else:
        return pd.DataFrame()

    annotation_cols = [
        "record_id",
        "ground_truth_tone",
        "ground_truth_esg",
        "ground_truth_aspect",
        "annotator",
        "review_notes",
        "review_status",
    ]
    for col in annotation_cols:
        if col not in base.columns:
            base[col] = ""

    overlays = []
    if not seed_df.empty:
        overlays.append(seed_df)
    if not annotation_df.empty:
        overlays.append(annotation_df)

    if overlays and "record_id" in base.columns:
        base = base.set_index("record_id", drop=False)
        for overlay in overlays:
            overlay = normalise_annotation_values(overlay.copy())
            if "record_id" not in overlay.columns:
                continue
            overlay = overlay.set_index("record_id", drop=False)
            shared = base.index.intersection(overlay.index)
            for col in annotation_cols:
                if col in overlay.columns and col in base.columns:
                    incoming = overlay.loc[shared, col].astype(str).str.strip()
                    use_mask = incoming.ne("")
                    base.loc[shared[use_mask], col] = incoming[use_mask]
        base = base.reset_index(drop=True)

    return normalise_annotation_values(base)


def ann_n(df, col):
    if df.empty or col not in df.columns: return 0
    series = df[col]
    if isinstance(series, pd.DataFrame):
        series = series.bfill(axis=1).iloc[:, 0]
    values = series.astype(str).str.strip()
    return int(values.ne("").sum())


def column_series(df, col):
    if df.empty or col not in df.columns:
        return pd.Series(dtype=str)
    series = df[col]
    if isinstance(series, pd.DataFrame):
        series = series.bfill(axis=1).iloc[:, 0]
    return series


def nonempty_count(df, col):
    series = column_series(df, col)
    if series.empty:
        return 0
    return int(series.astype(str).str.strip().ne("").sum())


def climatebert_processed_record_ids(imported_df):
    ids = set()
    if not imported_df.empty and {"record_id", "climatebert_commitment_pred"}.issubset(imported_df.columns):
        pred = column_series(imported_df, "climatebert_commitment_pred").astype(str).str.strip()
        ids.update(imported_df.loc[pred.ne(""), "record_id"].astype(str))
    if CLIMATEBERT_OUTPUT_PATH.exists():
        try:
            bg = pd.read_csv(CLIMATEBERT_OUTPUT_PATH).fillna("")
            if "record_id" in bg.columns:
                label_cols = [c for c in ["climate_commitment", "label", "top_label", "climate_commitment_label"] if c in bg.columns]
                if label_cols:
                    mask = bg[label_cols].astype(str).apply(lambda row: row.str.strip().ne("").any(), axis=1)
                    ids.update(bg.loc[mask, "record_id"].astype(str))
                else:
                    ids.update(bg["record_id"].astype(str))
        except Exception:
            pass
    return ids


def missing_annotation_mask(df):
    if df.empty:
        return pd.Series(dtype=bool)
    mask = pd.Series(False, index=df.index)
    for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect"]:
        if col in df.columns:
            mask = mask | column_series(df, col).astype(str).str.strip().eq("")
        else:
            mask = pd.Series(True, index=df.index)
    return mask


def import_climatebert_output(df_up, label_col):
    df_up = df_up.copy().fillna("")
    df_up["climatebert_commitment_pred"] = df_up[label_col].astype(str).str.lower().isin(
        ["yes", "true", "1", "commitment", "climate-commitment"]
    )
    if not silver.empty:
        keep_cols = ["record_id", "climatebert_commitment_pred", label_col]
        optional_cols = [c for c in ["score", "climatebert_model", "climatebert_model_backend", "climatebert_job_id"] if c in df_up.columns]
        merged = silver.merge(df_up[keep_cols + optional_cols], on="record_id", how="left")
    else:
        merged = df_up
    merged.to_csv(IMPORTED_PATH, index=False)
    return merged


def climatebert_a4_legacy_summary():
    legacy = load(VIS / "tone_climatebert_label_crosstab.csv")
    if legacy.empty:
        return {"rows": 0, "columns": 0, "label_assignments": 0}
    numeric = legacy.select_dtypes(include="number")
    return {
        "rows": len(legacy),
        "columns": max(len(legacy.columns) - 1, 0),
        "label_assignments": int(numeric.to_numpy().sum()) if not numeric.empty else 0,
    }


def climatebert_label_column(df):
    for col in ["climatebert_label", "label", "top_label", "climate_commitment_label"]:
        if col in df.columns and column_series(df, col).astype(str).str.strip().ne("").any():
            return col
    return ""


def normalize_climatebert_label(value):
    text = str(value or "").strip()
    if not text:
        return "missing"
    low = text.lower()
    if low in {"nan", "none", "null", "n/a", "na", "undefined"}:
        return "missing"
    return text


def normalize_tone_value(value):
    text = str(value or "").strip().lower()
    if not text or text in {"nan", "none", "null", "n/a", "na", "undefined"}:
        return "missing"
    if text in {"commitment", "action", "outcome", "none", "unknown", "missing"}:
        return text
    if "," in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if "commitment" in parts:
            return "commitment"
        if "action" in parts:
            return "action"
        if "outcome" in parts:
            return "outcome"
    return text


def climatebert_tone_crosstab(df):
    if df.empty or "tone_pred" not in df.columns:
        return pd.DataFrame()
    label_col = climatebert_label_column(df)
    if not label_col:
        return pd.DataFrame()
    view = df.copy()
    view["tone"] = column_series(view, "tone_pred").map(normalize_tone_value)
    view["climatebert_label"] = column_series(view, label_col).map(normalize_climatebert_label)
    pivot = pd.crosstab(view["tone"], view["climatebert_label"])
    tone_order = ["commitment", "action", "outcome", "none", "unknown", "missing"]
    existing_tones = [t for t in tone_order if t in pivot.index]
    extra_tones = [t for t in pivot.index.tolist() if t not in existing_tones]
    if existing_tones:
        pivot = pivot.reindex(existing_tones + extra_tones, fill_value=0)
    pivot.index.name = "tone"
    pivot.columns.name = None
    return pivot.reset_index()


def climatebert_commitment_crosstab(df):
    if df.empty or "tone_pred" not in df.columns or "climatebert_commitment_pred" not in df.columns:
        return pd.DataFrame()
    view = df.copy()
    view["tone"] = column_series(view, "tone_pred").astype(str).str.strip().replace("", "missing")
    view["climatebert_commitment"] = (
        column_series(view, "climatebert_commitment_pred")
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
        .map({True: "commitment", False: "not commitment"})
    )
    pivot = pd.crosstab(view["tone"], view["climatebert_commitment"])
    pivot.index.name = "tone"
    pivot.columns.name = None
    return pivot.reset_index()


def climatebert_model_summary(df):
    if df.empty or "climatebert_model" not in df.columns:
        return pd.DataFrame()
    group_cols = [col for col in ["climatebert_model", "climatebert_model_backend", "climatebert_job_id"] if col in df.columns]
    summary = df.groupby(group_cols, dropna=False).size().reset_index(name="records")
    return summary.sort_values("records", ascending=False)


def save_a4_primary_artifacts(full_a4: pd.DataFrame) -> list[str]:
    saved: list[str] = []
    if full_a4.empty:
        return saved
    VIS.mkdir(parents=True, exist_ok=True)
    full_csv = VIS / "tone_climatebert_label_crosstab_full.csv"
    full_a4.to_csv(full_csv, index=False)
    saved.append(full_csv.name)

    primary_csv = VIS / "tone_climatebert_label_crosstab.csv"
    full_a4.to_csv(primary_csv, index=False)
    saved.append(primary_csv.name)

    try:
        import matplotlib.pyplot as plt

        table = full_a4.set_index("tone")
        fig_w = max(9, min(16, 1.2 + 0.55 * len(table.columns)))
        fig_h = max(4.6, min(11.0, 2.4 + 0.5 * len(table.index)))
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        table.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
        ax.set_title("Tone by ClimateBERT Label (A.4 regenerated)", fontsize=13, pad=10)
        ax.set_xlabel("Tone")
        ax.set_ylabel("Record count")
        ax.grid(axis="y", alpha=0.25)
        ax.legend(title="ClimateBERT label", bbox_to_anchor=(1.02, 1), loc="upper left")
        fig.tight_layout()
        png_path = VIS / "climatebert_label_by_tone.png"
        fig.savefig(png_path, dpi=180)
        plt.close(fig)
        saved.append(png_path.name)
    except Exception:
        pass

    return saved


def climatebert_label_definitions(labels=None):
    definitions = {
        "yes": {
            "model family": "distilroberta-base-climate-commitment",
            "dashboard meaning": "The ClimateBERT commitment classifier marked the text as a climate-commitment statement.",
            "how to use": "Use for binary commitment agreement against `tone_pred == commitment`.",
        },
        "no": {
            "model family": "distilroberta-base-climate-commitment",
            "dashboard meaning": "The ClimateBERT commitment classifier did not mark the text as a climate-commitment statement.",
            "how to use": "Use as the negative class in binary commitment agreement.",
        },
        "Brown Projects": {
            "model family": "ClimateControversyBERT_classification",
            "dashboard meaning": "A controversy-classification label for climate-related project content that the model associates with brown or carbon-intensive project framing.",
            "how to use": "Do not treat as `not commitment` by itself; interpret as a separate controversy/project label.",
        },
        "Misinformation": {
            "model family": "ClimateControversyBERT_classification",
            "dashboard meaning": "A controversy-classification label for climate claims the model associates with misleading, questionable, or unsupported framing.",
            "how to use": "Use as a diagnostic controversy label, not as a binary commitment label.",
        },
        "Ambiguous Actions": {
            "model family": "ClimateControversyBERT_classification",
            "dashboard meaning": "A controversy-classification label for action claims that are vague, unclear, or insufficiently specific.",
            "how to use": "Use to identify weakly specified action language; keep separate from commitment yes/no.",
        },
        "missing": {
            "model family": "Data quality",
            "dashboard meaning": "No usable ClimateBERT label was available for that record.",
            "how to use": "Exclude from agreement metrics unless missingness itself is being audited.",
        },
    }
    rows = []
    wanted = sorted({str(label) for label in labels if str(label).strip()}) if labels is not None else sorted(definitions)
    for label in wanted:
        rows.append(
            {
                "ClimateBERT label": label,
                **definitions.get(
                    label,
                    {
                        "model family": "ClimateBERT / ESG auxiliary classifier",
                        "dashboard meaning": "Label emitted by the selected ClimateBERT-style model or inherited from earlier ClimateBERT-style proxy labels.",
                        "how to use": "Inspect the model/job source before interpreting this label as commitment, controversy, or ESG-topic evidence.",
                    },
                ),
            }
        )
    return pd.DataFrame(rows)


def climatebert_a4_logic_rows(label_col):
    return pd.DataFrame(
        [
            {
                "step": "Choose label column",
                "logic": f"The page uses `{label_col or 'no label column found'}` as the multiclass ClimateBERT label column.",
            },
            {
                "step": "Full label table",
                "logic": "Rows are `tone_pred`; columns are ClimateBERT labels; cells are record counts from `pd.crosstab(tone_pred, climatebert_label)`.",
            },
            {
                "step": "Binary commitment table",
                "logic": "`climatebert_commitment_pred` is converted to commitment/not commitment and crosstabbed against `tone_pred`.",
            },
            {
                "step": "Important separation",
                "logic": "`yes/no` labels come from the commitment model; `Brown Projects`, `Misinformation`, and `Ambiguous Actions` come from the controversy classifier, so they should not be collapsed into the binary commitment metric.",
            },
            {
                "step": "Thesis interpretation",
                "logic": "Use the binary table for RQ3 commitment agreement, and use controversy labels only as a diagnostic lens for weak, ambiguous, or problematic climate disclosure language.",
            },
        ]
    )


def climatebert_a4_work_items(silver_df, imported_df):
    legacy = climatebert_a4_legacy_summary()
    real_rows = len(imported_df)
    label_col = climatebert_label_column(imported_df)
    processed = nonempty_count(imported_df, "climatebert_commitment_pred") if not imported_df.empty else 0
    expected = len(silver_df) if not silver_df.empty else 0
    models = climatebert_model_summary(imported_df)
    model_names = models["climatebert_model"].astype(str).str.lower().tolist() if not models.empty and "climatebert_model" in models.columns else []
    commitment_model_rows = sum("commitment" in name for name in model_names)
    return pd.DataFrame(
        [
            {
                "work item": "Explain A.4 denominator",
                "current evidence": f"{legacy['label_assignments']:,} exploded label assignments from {legacy['rows']} tone rows and {legacy['columns']} label columns",
                "next action": "Treat legacy A.4 as the compact 332-record visualization, not the full Action Plan corpus.",
                "status": "done" if legacy["label_assignments"] else "needed",
            },
            {
                "work item": "Build full-corpus ClimateBERT x tone table",
                "current evidence": f"{real_rows:,} imported rows; {processed:,}/{expected:,} rows have commitment predictions",
                "next action": "Use the full imported table to continue A.4 analysis for all silver/action-plan records.",
                "status": "done" if expected and processed >= expected else "needed",
            },
            {
                "work item": "Verify ClimateBERT model family",
                "current evidence": f"{len(models):,} model/job group(s); label column = {label_col or 'missing'}",
                "next action": "Confirm whether outputs came from the commitment model or from another ClimateBERT classifier before interpreting labels.",
                "status": "review" if commitment_model_rows != len(model_names) else "done",
            },
            {
                "work item": "Separate binary commitment from multiclass labels",
                "current evidence": "Imported file contains both `climatebert_commitment_pred` and model labels when available.",
                "next action": "Report commitment agreement separately from multiclass/controversy label distribution.",
                "status": "needed",
            },
            {
                "work item": "Regenerate thesis figure/table after review",
                "current evidence": "Legacy A.4 PNG/CSV still lives in results/visualizations.",
                "next action": "After model verification, promote the full-corpus continuation table into the Chapter 4-6 graph attachments.",
                "status": "needed",
            },
        ]
    )


def suggest_aspect_cluster(aspect):
    text = str(aspect or "").lower()
    rules = [
        ("Governance & Ethics", ["korupsi", "antikorupsi", "anti korupsi", "etik", "governance", "tata kelola", "komisaris", "direksi", "kepatuhan", "compliance", "gratifikasi", "conflict", "konflik kepentingan", "pengendalian internal", "manajemen risiko", "pengelolaan risiko"]),
        ("Energy & Climate", ["climate", "karbon", "emisi", "netzero", "net zero", "energi", "energy", "scope", "ghg", "iklim", "renewable", "rendah emisi"]),
        ("Waste & Pollution", ["limbah", "waste", "pollution", "polusi", "air limbah", "b3", "sampah", "emission", "water", "air", "lingkungan", "ramah lingkungan"]),
        ("Human Capital", ["karyawan", "employee", "pelatihan", "training", "keselamatan", "k3", "human", "tenaga kerja", "labor", "pekerja", "hak asasi manusia", "ham"]),
        ("Community Relations", ["masyarakat", "community", "komunitas", "sosial", "csr", "pemberdayaan", "pendidikan", "donasi", "stakeholder"]),
        ("Supply Chain", ["vendor", "supplier", "rantai pasok", "supply", "procurement", "pemasok"]),
        ("Financial Sustainability", ["financial", "keuangan", "investasi", "economic", "ekonomi", "profit", "revenue", "kinerja esg"]),
        ("Digital & Data", ["digital", "data", "cyber", "teknologi", "technology", "privacy"]),
        ("Biodiversity & Land", ["biodiversity", "keanekaragaman", "lahan", "land", "hutan", "forest", "habitat"]),
    ]
    for cluster, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return cluster
    if text in {"missing", "none", "nan", ""}:
        return "Other"
    return "Other"


def suggest_ontology_path(aspect):
    cluster = suggest_aspect_cluster(aspect)
    text = str(aspect or "").strip()
    lowered = text.lower()
    if any(token in lowered for token in ["keberlanjutan", "sustainability", "pengungkapan", "pelaporan", "prospektif"]):
        return f"GRI 2 General Disclosures / GRI 3 Material Topics -> {text}"
    if cluster == "Energy & Climate":
        return f"GRI 305 Emissions / TCFD Climate -> {text}"
    if cluster == "Waste & Pollution":
        return f"GRI 306 Waste / GRI 303 Water -> {text}"
    if cluster == "Human Capital":
        return f"GRI 401-404 Employment and Training -> {text}"
    if cluster == "Community Relations":
        return f"GRI 413 Local Communities -> {text}"
    if cluster == "Supply Chain":
        return f"GRI 308/414 Supplier Assessment -> {text}"
    if cluster == "Governance & Ethics":
        return f"GRI 205 Anti-corruption / GRI 2 Governance -> {text}"
    if cluster == "Financial Sustainability":
        return f"GRI 201 Economic Performance -> {text}"
    if cluster == "Biodiversity & Land":
        return f"GRI 304 Biodiversity -> {text}"
    if cluster == "Digital & Data":
        return f"Governance / Data and Technology -> {text}"
    return ""


def first_nonempty_series(df, columns):
    candidates = []
    for col in columns:
        if col in df.columns:
            candidates.append(column_series(df, col).astype(str).str.strip())
    if not candidates:
        return pd.Series([""] * len(df), index=df.index, dtype=str)
    combined = pd.concat(candidates, axis=1)
    return combined.replace("", pd.NA).bfill(axis=1).iloc[:, 0].fillna("").astype(str)


def ontology_bool(series):
    return pd.Series(series).astype(str).str.lower().isin(["true", "1", "yes"])


MISSING_ASPECT_VALUES = {"", "missing", "none", "nan", "null", "unknown", "n/a", "not_applicable"}


def is_missing_aspect_series(series):
    return pd.Series(series).astype(str).str.strip().str.lower().isin(MISSING_ASPECT_VALUES)


def build_full_ontology_coverage(source_df):
    if source_df.empty:
        return pd.DataFrame()
    aspects = first_nonempty_series(source_df, ["ground_truth_aspect", "aspect"])
    view = pd.DataFrame({"aspect": aspects.str.lower().str.strip()})
    view["aspect"] = view["aspect"].replace("", "missing")
    counts = view["aspect"].value_counts().rename_axis("aspect").reset_index(name="records")
    counts["suggested_path"] = counts["aspect"].map(suggest_ontology_path)
    counts["mapped_to_ontology"] = counts["suggested_path"].astype(str).str.strip().ne("")
    counts.loc[counts["aspect"].isin(["missing", "none", "nan"]), "mapped_to_ontology"] = False
    return counts[["aspect", "records", "mapped_to_ontology", "suggested_path"]]


def ontology_missing_aspect_records(source_df):
    if source_df.empty:
        return pd.DataFrame()
    df = source_df.copy()
    if "record_id" not in df.columns:
        df["record_id"] = [f"row_{idx}" for idx in range(len(df))]

    has_ground_truth = "ground_truth_aspect" in df.columns
    has_pipeline = "aspect" in df.columns
    ground_truth = column_series(df, "ground_truth_aspect").astype(str).str.strip() if has_ground_truth else pd.Series([""] * len(df), index=df.index)
    pipeline = column_series(df, "aspect").astype(str).str.strip() if has_pipeline else pd.Series([""] * len(df), index=df.index)
    needs_label = is_missing_aspect_series(ground_truth) if has_ground_truth else is_missing_aspect_series(pipeline)
    out = df.loc[needs_label].copy()
    if out.empty:
        return pd.DataFrame()

    out["current_ground_truth_aspect"] = ground_truth.loc[out.index].values
    out["pipeline_aspect"] = pipeline.loc[out.index].values
    out["suggested_aspect_label"] = out["pipeline_aspect"].where(~is_missing_aspect_series(out["pipeline_aspect"]), "")
    out["suggested_cluster"] = out["suggested_aspect_label"].map(suggest_aspect_cluster)
    out["suggested_ontology_path"] = out["suggested_aspect_label"].map(suggest_ontology_path)
    if has_ground_truth:
        out["missing_reason"] = "missing ground_truth_aspect"
    else:
        out["missing_reason"] = "placeholder pipeline aspect"
    out["corrected_aspect_label"] = ""
    out["ontology_extension_status"] = "needs_review"
    out["review_notes"] = ""
    keep = [
        "record_id",
        "company",
        "target",
        "prompt",
        "tone_pred",
        "ground_truth_esg",
        "esg",
        "current_ground_truth_aspect",
        "pipeline_aspect",
        "suggested_aspect_label",
        "corrected_aspect_label",
        "suggested_cluster",
        "suggested_ontology_path",
        "ontology_extension_status",
        "missing_reason",
        "review_notes",
        "text",
    ]
    return out[[col for col in keep if col in out.columns]]


def merge_saved_missing_aspect_labels(candidates, saved):
    if candidates.empty or saved.empty or "record_id" not in saved.columns:
        return candidates
    out = candidates.copy()
    saved_latest = saved.drop_duplicates("record_id", keep="last").set_index("record_id")
    out = out.set_index("record_id", drop=False)
    for col in ["corrected_aspect_label", "ontology_extension_status", "review_notes", "suggested_ontology_path", "suggested_cluster"]:
        if col in saved_latest.columns and col in out.columns:
            incoming = saved_latest[col].astype(str)
            shared = out.index.intersection(incoming.index)
            use = incoming.loc[shared].str.strip().ne("")
            update_index = use[use].index
            out.loc[update_index, col] = incoming.loc[update_index]
    return out.reset_index(drop=True)


def build_novel_aspect_review_table(unmapped_df, saved_review):
    if unmapped_df.empty:
        return pd.DataFrame()
    review = unmapped_df.copy()
    if "aspect" not in review.columns:
        return pd.DataFrame()
    review["aspect"] = review["aspect"].astype(str).str.strip()
    review = review[review["aspect"].ne("")].copy()
    if review.empty:
        return pd.DataFrame()
    if "records" in review.columns:
        review["records"] = pd.to_numeric(review["records"], errors="coerce").fillna(0).astype(int)
    else:
        review["records"] = 0
    if "suggested_path" not in review.columns:
        review["suggested_path"] = ""
    review["suggested_cluster"] = review["aspect"].map(suggest_aspect_cluster)
    review["review_status"] = "needs_review"
    review["canonical_aspect"] = review["aspect"].where(~is_missing_aspect_series(review["aspect"]), "")
    review["reviewed_cluster"] = review["suggested_cluster"]
    review["ontology_path"] = review["suggested_path"]
    review["thesis_note"] = ""

    editable_cols = [
        "review_status",
        "canonical_aspect",
        "reviewed_cluster",
        "ontology_path",
        "thesis_note",
    ]
    if not saved_review.empty and "aspect" in saved_review.columns:
        saved_latest = saved_review.drop_duplicates("aspect", keep="last").set_index("aspect")
        review = review.set_index("aspect", drop=False)
        shared = review.index.intersection(saved_latest.index)
        for col in editable_cols:
            if col in saved_latest.columns:
                incoming = saved_latest.loc[shared, col].astype(str)
                if col == "review_status":
                    valid = incoming.isin(NOVEL_ASPECT_STATUS_OPTS)
                    update_index = valid[valid].index
                else:
                    valid = incoming.str.strip().ne("")
                    update_index = valid[valid].index
                review.loc[update_index, col] = incoming.loc[update_index]
        review = review.reset_index(drop=True)

    keep = [
        "aspect",
        "records",
        "review_status",
        "canonical_aspect",
        "suggested_cluster",
        "reviewed_cluster",
        "suggested_path",
        "ontology_path",
        "thesis_note",
    ]
    return review[[col for col in keep if col in review.columns]].sort_values("records", ascending=False)


def ontology_a12_summary(legacy_df, full_df, corpus_rows):
    legacy_records = int(pd.to_numeric(legacy_df.get("records", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not legacy_df.empty else 0
    full_records = int(pd.to_numeric(full_df.get("records", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not full_df.empty else 0
    legacy_mapped = int(ontology_bool(legacy_df["mapped_to_ontology"]).sum()) if not legacy_df.empty and "mapped_to_ontology" in legacy_df.columns else 0
    full_mapped = int(ontology_bool(full_df["mapped_to_ontology"]).sum()) if not full_df.empty and "mapped_to_ontology" in full_df.columns else 0
    return {
        "legacy_aspects": len(legacy_df),
        "legacy_records": legacy_records,
        "legacy_mapped": legacy_mapped,
        "full_aspects": len(full_df),
        "full_records": full_records,
        "full_mapped": full_mapped,
        "corpus_rows": int(corpus_rows),
    }


def ontology_a12_breakdown(full_df):
    if full_df.empty:
        return {
            "mapped_aspects": 0,
            "mapped_records": 0,
            "placeholder_aspects": 0,
            "placeholder_records": 0,
            "substantive_novel_aspects": 0,
            "substantive_novel_records": 0,
        }
    work = full_df.copy()
    work["records"] = pd.to_numeric(work.get("records", 0), errors="coerce").fillna(0).astype(int)
    mapped_mask = ontology_bool(work["mapped_to_ontology"]) if "mapped_to_ontology" in work.columns else pd.Series([False] * len(work))
    placeholder_mask = is_missing_aspect_series(work["aspect"]) if "aspect" in work.columns else pd.Series([False] * len(work))
    substantive_novel_mask = (~mapped_mask) & (~placeholder_mask)
    return {
        "mapped_aspects": int(mapped_mask.sum()),
        "mapped_records": int(work.loc[mapped_mask, "records"].sum()),
        "placeholder_aspects": int(placeholder_mask.sum()),
        "placeholder_records": int(work.loc[placeholder_mask, "records"].sum()),
        "substantive_novel_aspects": int(substantive_novel_mask.sum()),
        "substantive_novel_records": int(work.loc[substantive_novel_mask, "records"].sum()),
    }


def ontology_a12_work_items(legacy_df, full_df, corpus_rows):
    summary = ontology_a12_summary(legacy_df, full_df, corpus_rows)
    return pd.DataFrame(
        [
            {
                "work item": "Explain A.12 denominator",
                "current evidence": f"Legacy ontology file covers {summary['legacy_records']:,} record assignments across {summary['legacy_aspects']:,} unique aspect rows.",
                "next action": "Describe A.12 as compact 332-record ontology coverage, not full-corpus coverage.",
                "status": "done" if summary["legacy_records"] else "needed",
            },
            {
                "work item": "Build full-corpus ontology coverage",
                "current evidence": f"Continuation table covers {summary['full_records']:,}/{summary['corpus_rows']:,} Action Plan rows across {summary['full_aspects']:,} unique aspects.",
                "next action": "Use the current silver/annotation table to extend A.12 beyond the legacy visualization snapshot.",
                "status": "done" if summary["corpus_rows"] and summary["full_records"] >= summary["corpus_rows"] else "review",
            },
            {
                "work item": "Review mapped vs novel labels",
                "current evidence": f"Legacy mapped rows: {summary['legacy_mapped']:,}/{summary['legacy_aspects']:,}; full mapped rows: {summary['full_mapped']:,}/{summary['full_aspects']:,}.",
                "next action": "Manually review high-frequency unmapped aspects before claiming Indonesian ESG vocabulary extension.",
                "status": "needed",
            },
            {
                "work item": "Separate placeholders from real novel aspects",
                "current evidence": "`missing`, `none`, and blank-derived aspects can dominate coverage if they remain in the aspect column.",
                "next action": "Report placeholder coverage separately from substantive novel ESG vocabulary.",
                "status": "needed",
            },
            {
                "work item": "Promote full A.12 after review",
                "current evidence": "Legacy A.12 PNG/CSV still points to the compact ontology snapshot.",
                "next action": "After mapping review, save the full ontology continuation table and use it in Chapter 4-6 graph attachments.",
                "status": "needed",
            },
        ]
    )


# ── Load data ─────────────────────────────────────────────────────────────────
silver_base = load(SILVER_PATH)
llm_silver  = llm_runs_to_silver_rows()
silver     = append_new_rows(silver_base, llm_silver)
seed       = load(SEED_PATH)
annot_file = load(ANNOTATION_PATH)
annot      = build_annotation_table(silver, seed, annot_file)
proxy      = load(PROXY_PATH)
imported   = load(IMPORTED_PATH)
ontology   = load(ONTOLOGY_PATH)
prompt_stab = load(PROMPT_STAB_PATH)
model_stab_static = load(MODEL_STAB_PATH)
model_stab_live = derive_model_stability_from_llm_runs()
model_stab  = combine_model_stability(model_stab_static, model_stab_live)
ocr_df      = load(OCR_PATH)
fail_df     = load(FAILURE_PATH)
fail_cnt    = load(FAIL_CNT_PATH)
phase_registry = load(PHASE_REGISTRY_PATH)

tone_done    = ann_n(annot, "ground_truth_tone")
esg_done     = ann_n(annot, "ground_truth_esg")
aspect_done  = ann_n(annot, "ground_truth_aspect")
annotator_done = ann_n(annot, "annotator")
review_notes_done = ann_n(annot, "review_notes")
tone_missing = max(len(annot) - tone_done, 0)
tone_usable_denominator = tone_done
cb_real      = nonempty_count(imported, "climatebert_commitment_pred") if not imported.empty else 0
n_models     = model_stab["model"].astype(str).nunique() if not model_stab.empty and "model" in model_stab.columns else 0
cb_target_total = len(silver) if not silver.empty else 332
cb_processed_ids = climatebert_processed_record_ids(imported)
cb_unprocessed_ids = []
if not silver.empty and "record_id" in silver.columns:
    cb_unprocessed_ids = [
        str(record_id)
        for record_id in silver["record_id"].astype(str).tolist()
        if str(record_id) not in cb_processed_ids
    ]
ground_truth_missing_mask = missing_annotation_mask(annot) if not annot.empty else pd.Series(dtype=bool)
ground_truth_complete_rows = int((~ground_truth_missing_mask).sum()) if not annot.empty else 0
ground_truth_missing_rows = int(ground_truth_missing_mask.sum()) if not annot.empty else 0
phase2_missing_status_rows = (
    int(column_series(annot, "review_status").astype(str).str.strip().eq("").sum())
    if not annot.empty and "review_status" in annot.columns
    else len(annot)
)
phase2_missing_annotator_rows = (
    int(column_series(annot, "annotator").astype(str).str.strip().eq("").sum())
    if not annot.empty and "annotator" in annot.columns
    else len(annot)
)
ocr_done_rows = (
    int(ocr_df["status"].astype(str).str.lower().eq("done").sum())
    if not ocr_df.empty and "status" in ocr_df.columns
    else len(ocr_df)
)
phase3_registry_rows = (
    int(phase_registry["phase"].astype(str).eq("Phase 3").sum())
    if not phase_registry.empty and "phase" in phase_registry.columns
    else 0
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Show / hide steps")
    show = {i: st.checkbox(lbl, value=True) for i, lbl in {
        1: "Step 1 — ClimateBERT run",
        2: "Step 2 — Annotation",
        3: "Step 3 — OCR ground truth",
        4: "Step 4 — Model stability",
        5: "Step 5 — Failure mode tagging",
        6: "Step 6 — Aspect clustering",
        "matrix": "📊 PDF × Prompt matrix",
    }.items()}
    st.divider()
    with st.expander("📋 Research Notes", expanded=False):
        if NOTES_PATH.exists():
            st.markdown(NOTES_PATH.read_text(encoding="utf-8"))
        else:
            st.info(f"notes.md not found at {NOTES_PATH}")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Thesis Action Plan — Steps 1 to 6")
st.caption(
    "All thesis completion tasks in one place. Toggle steps on/off in the sidebar. "
    "Each step shows live results on the right. Research notes are in the sidebar."
)

legacy_live_rows = 0
if not llm_silver.empty and "record_id" in llm_silver.columns:
    base_ids = set(silver_base["record_id"].astype(str)) if not silver_base.empty and "record_id" in silver_base.columns else set()
    legacy_live_rows = int((~llm_silver["record_id"].astype(str).isin(base_ids)).sum())
live_model_rows = len(model_stab_live) if not model_stab_live.empty else 0

with st.expander("Refresh / migrate reprocess outputs", expanded=bool(legacy_live_rows or live_model_rows)):
    st.caption(
        "Use this after running `Reprocess existing OCR pages with selected LLM and prompt`, especially for outputs created "
        "before this page knew how to include live reprocess results in Step 2 and model stability."
    )
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Live extracted rows", f"{len(llm_silver):,}")
    r2.metric("Not yet in silver CSV", f"{legacy_live_rows:,}")
    r3.metric("Live model summaries", f"{live_model_rows:,}")
    r4.metric("ESG run records", f"{len(load_esg_record_runs()):,}")
    c1, c2 = st.columns(2)
    if c1.button("Refresh live reprocess data", use_container_width=True, key="refresh_live_reprocess_data"):
        st.cache_data.clear()
        st.rerun()
    migrate_disabled = not (legacy_live_rows or live_model_rows)
    if c2.button(
        "Migrate live outputs into Step 2 + model results",
        type="primary",
        use_container_width=True,
        disabled=migrate_disabled,
        key="migrate_live_reprocess_outputs",
    ):
        migrated = migrate_live_reprocess_outputs(silver_base, llm_silver, model_stab_static, model_stab_live)
        st.success(
            f"Migrated {migrated['silver_rows']:,} Step 2 row(s) and "
            f"{migrated['model_rows']:,} model summary row(s)."
        )
        st.rerun()
    if migrate_disabled:
        st.info("No unmigrated live reprocess outputs were detected right now.")

with st.expander("Create Streamlit workflow dashboard page", expanded=False):
    st.caption(
        "Create a new page based on `5_Thesis_Systematic_Workflow_dashboard.py`. "
        "The generated page will appear in the Streamlit sidebar after refresh."
    )
    page_name_input = st.text_input(
        "New dashboard page filename",
        value="5_1_Thesis_Systematic_Workflow_dashboard_generated.py",
        key="workflow_dashboard_page_name",
    )
    overwrite_dashboard_page = st.checkbox(
        "Overwrite if this page already exists",
        value=False,
        key="workflow_dashboard_overwrite",
    )
    preview_page_name = safe_streamlit_page_name(page_name_input)
    st.caption(f"Target: `{PAGES_DIR / preview_page_name}`")
    if st.button("Create workflow dashboard Streamlit page", type="primary", use_container_width=True, key="create_workflow_dashboard_page"):
        target, created, status = create_workflow_dashboard_page(page_name_input, overwrite_dashboard_page)
        if created:
            st.success(f"Created dashboard page: `{target.name}`. Refresh Streamlit/sidebar to open it.")
        elif status == "exists":
            st.warning(f"`{target.name}` already exists. Enable overwrite if you want to replace it.")
        else:
            st.info(f"No change for `{target.name}`.")

for col, (label, val, ok) in zip(st.columns(6), [
    ("ClimateBERT real",  f"{cb_real}/{cb_target_total}",    cb_real >= cb_target_total),
    ("Tone labels",       f"{tone_done}/{len(annot) if len(annot) else ANNOTATION_TARGET}",   tone_done >= ANNOTATION_TARGET),
    ("ESG labels",        f"{esg_done}/{ANNOTATION_TARGET}",    esg_done >= ANNOTATION_TARGET),
    ("Aspect labels",     f"{aspect_done}/{ANNOTATION_TARGET}", aspect_done >= ANNOTATION_TARGET),
    ("OCR pages sampled", "0/100",              False),
    ("Models tested",     f"{n_models}/3+",     n_models >= 3),
]):
    col.metric(label, val, delta="✓ Done" if ok else "Needed",
               delta_color="normal" if ok else "inverse")

with st.expander("Phase split — completed, editing, and new intake pools", expanded=True):
    st.caption(
        "Phase 1 is the completed dataset pool. Phase 2 is the editing/backfill pool. "
        "Phase 3 is the intake pool for data added from now onward."
    )
    phase_rows = pd.DataFrame(
        [
            {
                "phase": "Phase 1",
                "scope": "Completed dataset pool",
                "current evidence": f"{ground_truth_complete_rows:,}/{len(annot):,} rows have tone, ESG, and aspect ground truth"
                if len(annot)
                else "No annotation table loaded",
                "complete means": (
                    "Included rows have stable record_id, non-empty ground_truth_tone/esg/aspect "
                    "or an explicit exclusion, review_status set, denominators documented, and dependent artifacts refreshed."
                ),
                "status": "complete" if len(annot) and ground_truth_missing_rows == 0 and phase2_missing_status_rows == 0 else "usable with QA/backfill remaining",
            },
            {
                "phase": "Phase 2",
                "scope": "Editing and backfill pool",
                "current evidence": (
                    f"{ground_truth_missing_rows:,} rows missing one or more core ground-truth fields; "
                    f"{phase2_missing_status_rows:,} rows missing review_status; "
                    f"{phase2_missing_annotator_rows:,} rows missing annotator; "
                    f"{max(cb_target_total - cb_real, 0):,} ClimateBERT records remaining; "
                    f"{ocr_done_rows:,}/{len(ocr_df):,} OCR summary rows marked done; "
                    f"{len(fail_df):,} failure-mode rows"
                ),
                "complete means": (
                    "Each gap has a saved artifact, a documented exclusion decision, or a limitation/future-work statement "
                    "that names the affected claim and denominator."
                ),
                "status": "open",
            },
            {
                "phase": "Phase 3",
                "scope": "New data from now onward",
                "current evidence": (
                    f"{phase3_registry_rows:,} row(s) currently in Phase 3"
                    if PHASE_REGISTRY_PATH.exists()
                    else "Open `1_16_Dataset_Phase_Manager.py` to initialize the phase registry"
                ),
                "complete means": (
                    "Every new record has been triaged: complete rows move to Phase 1, incomplete rows move to Phase 2."
                ),
                "status": "intake",
            },
        ]
    )
    st.dataframe(phase_rows, use_container_width=True, hide_index=True)
    st.markdown(
        "- Use **Phase 1** for completed dataset claims.\n"
        "- Use **Phase 2** for rows that need editing/backfill before they can become complete.\n"
        "- Use **Phase 3** for new incoming data until it is triaged into Phase 1 or Phase 2.\n"
        "- Manage movement between phases in `1_16_Dataset_Phase_Manager.py`.\n"
        f"- Current Phase 1-ready denominator for all three core ground-truth fields is **{ground_truth_complete_rows:,}** row(s)."
    )

with st.expander("A.18 / A.8 gap audit snapshot", expanded=True):
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Missing ground_truth_tone", f"{tone_missing:,}/{len(annot):,}" if len(annot) else "n/a")
    g2.metric("Usable tone denominator", f"{tone_usable_denominator:,}")
    g3.metric("annotator completed", f"{annotator_done:,}/{len(annot):,}" if len(annot) else "n/a")
    g4.metric("review_notes completed", f"{review_notes_done:,}/{len(annot):,}" if len(annot) else "n/a")
    st.caption(
        f"Reviewer note: if total rows are {len(annot):,}, then {tone_missing:,} missing tone means usable tone denominator is {tone_usable_denominator:,} (A.37 split). "
        "Current κ claims should be presented together with annotator provenance and completion coverage."
    )
    st.markdown(
        "- A.8 benchmark gaps: OCR CER/WER not measured; repeated LLM runs are still concentrated in only a few models; ClimateBERT baseline is proxy-only (κ=0.645) without formal label-match F1.\n"
        "- A.4 scope issue: tone-by-ClimateBERT visual may collapse to one `undefined` bar due to grouping/render bug; verify crosstab categories before using the chart in thesis text."
    )
    st.markdown("#### Editable gap tracker")
    default_gap_rows = pd.DataFrame([
        {"gap_id": "A18_TONE_MISSING", "gap_area": "A.18 annotation coverage", "metric": "Missing ground_truth_tone", "current_value": str(tone_missing), "target_value": "0", "status": "open", "owner": "", "due_date": "", "evidence_path": str(ANNOTATION_PATH), "notes": "Base expectation: 591 missing out of 5,444; usable denominator 4,853 (A.37)."},
        {"gap_id": "A18_ANNOTATOR", "gap_area": "A.18 annotation provenance", "metric": "annotator completed", "current_value": str(annotator_done), "target_value": str(len(annot)), "status": "open", "owner": "", "due_date": "", "evidence_path": str(ANNOTATION_PATH), "notes": "Backfill who annotated each row to support reliability claims."},
        {"gap_id": "A18_REVIEW_NOTES", "gap_area": "A.18 qualitative review", "metric": "review_notes completed", "current_value": str(review_notes_done), "target_value": str(len(annot)), "status": "open", "owner": "", "due_date": "", "evidence_path": str(ANNOTATION_PATH), "notes": "Backfill qualitative notes for disagreement and QA traceability."},
        {"gap_id": "A8_OCR_CER_WER", "gap_area": "A.8 benchmark", "metric": "OCR quality measured (CER/WER)", "current_value": "not_measured", "target_value": "measured", "status": "open", "owner": "", "due_date": "", "evidence_path": str(OCR_PATH), "notes": "Run Step 3 and produce page-level CER/WER outputs."},
        {"gap_id": "A8_REPEATED_RUNS", "gap_area": "A.8 benchmark", "metric": "Repeated LLM runs coverage", "current_value": "partial", "target_value": "all core models/prompts with CI", "status": "open", "owner": "", "due_date": "", "evidence_path": str(MODEL_STAB_PATH), "notes": "Currently concentrated in arcee-ai/trinity-large-preview and openai/gpt-oss-120b."},
        {"gap_id": "A8_CLIMATEBERT_F1", "gap_area": "A.8 benchmark", "metric": "ClimateBERT formal label-match F1", "current_value": "proxy_kappa_0.645", "target_value": "real_label_match_f1", "status": "open", "owner": "", "due_date": "", "evidence_path": str(IMPORTED_PATH), "notes": "Replace proxy-only baseline with formal F1 against human labels."},
        {"gap_id": "A4_SCOPE_CHART", "gap_area": "A.4 scope chart", "metric": "Tone-by-ClimateBERT label chart integrity", "current_value": "collapsed_to_undefined", "target_value": "all_labels_visible", "status": "open", "owner": "", "due_date": "", "evidence_path": str(ARTIFACTS / 'tone_climatebert_label_crosstab.csv'), "notes": "Fix rendering/grouping bug before final chapter export."},
    ])
    gap_df = load_gap_audit(default_gap_rows)
    editable_cols = ["gap_id", "gap_area", "metric", "current_value", "target_value", "status", "owner", "due_date", "evidence_path", "notes"]
    edited_gap_df = st.data_editor(
        gap_df[editable_cols],
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        disabled=["gap_id", "gap_area", "metric"],
        key="gap_audit_editor",
        height=320,
        column_config={
            "status": st.column_config.SelectboxColumn("status", options=["open", "in_progress", "blocked", "done"], required=True),
            "notes": st.column_config.TextColumn("notes", width="large"),
            "evidence_path": st.column_config.TextColumn("evidence_path", width="large"),
        },
    )
    c1, c2 = st.columns(2)
    if c1.button("Save gap tracker", type="primary", use_container_width=True, key="save_gap_tracker"):
        out = edited_gap_df.fillna("").copy()
        GAP_AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(GAP_AUDIT_PATH, index=False)
        st.success(f"Saved gap tracker -> {GAP_AUDIT_PATH.name}")
        st.rerun()
    c2.download_button(
        "Download gap tracker CSV",
        edited_gap_df.fillna("").to_csv(index=False).encode("utf-8"),
        file_name="gap_audit_snapshot.csv",
        mime="text/csv",
        use_container_width=True,
    )
    done_rows = edited_gap_df[edited_gap_df["status"].astype(str).str.lower().eq("done")]
    st.caption(f"Resolved gaps: {len(done_rows)}/{len(edited_gap_df)}")

chapter_decisions = read_json(
    CHAPTER_RESOLUTION_PATH,
    {
        "missing_tone_policy": "exclude_from_agreement",
        "data_md_policy": "retain_as_failed_experiment",
        "greenwashing_policy": "median_primary_log1p_sensitivity",
        "ontology_top_n": 15,
    },
)
proxy_summary_file = load(ARTIFACTS / "climatebert_proxy_agreement_summary.csv")
greenwashing_file = load(ARTIFACTS / "greenwashing_index_by_company.csv")

with st.expander("Chapter 4-6 resolution board — decisions, denominators, and thesis text", expanded=True):
    st.caption(
        "This board turns the current thesis-review issues into explicit methodology decisions, Chapter 4/5 interpretation text, "
        "and exportable Chapter 6 contribution tables."
    )
    integration_status = ch46_integration_status_rows()
    with st.expander("Integration with `pages/6_4_ch4-6.py`", expanded=False):
        st.caption(
            "This verifies that the Chapter 4-6 DOCX/graph page is consuming the same saved artifacts that this Action Plan exports."
        )
        st.dataframe(integration_status.astype(str), use_container_width=True, hide_index=True, height=180)
        if integration_status["status"].eq("Done").all():
            st.success("All Chapter 4-6 resolution artifacts exist and are wired into `6_4_ch4-6.py`.")
        else:
            st.warning("Some artifacts are missing or not yet referenced by `6_4_ch4-6.py`. Save artifacts here, then refresh the Ch4-6 page snapshot.")

    policy_options = tone_denominator_policy_options()
    policy_keys = policy_options["decision"].tolist()
    current_policy = chapter_decisions.get("missing_tone_policy", "exclude_from_agreement")
    if current_policy not in policy_keys:
        current_policy = "exclude_from_agreement"
    prompt_policy_options = ["retain_as_failed_experiment", "exclude_from_stability_analysis"]
    current_prompt_policy = chapter_decisions.get("data_md_policy", "retain_as_failed_experiment")
    if current_prompt_policy not in prompt_policy_options:
        current_prompt_policy = "retain_as_failed_experiment"
    greenwashing_policy_options = ["median_primary_log1p_sensitivity", "prototype_metric_acknowledgement", "raw_mean_with_outlier_warning"]
    current_greenwashing_policy = chapter_decisions.get("greenwashing_policy", "median_primary_log1p_sensitivity")
    if current_greenwashing_policy not in greenwashing_policy_options:
        current_greenwashing_policy = "median_primary_log1p_sensitivity"

    decision_cols = st.columns([2, 2, 2, 1])
    with decision_cols[0]:
        missing_tone_policy = st.selectbox(
            "591 missing tone records",
            policy_keys,
            index=policy_keys.index(current_policy),
            format_func=lambda value: {
                "exclude_from_agreement": "Exclude from agreement (recommended)",
                "recode_as_none": "Recode as none",
                "separate_unclassifiable": "Separate unclassifiable category",
            }.get(value, value),
            key="ch46_missing_tone_policy",
        )
    with decision_cols[1]:
        data_md_policy = st.selectbox(
            "data.md prompt outlier",
            prompt_policy_options,
            index=prompt_policy_options.index(current_prompt_policy),
            format_func=lambda value: {
                "retain_as_failed_experiment": "Keep as failed experiment (recommended)",
                "exclude_from_stability_analysis": "Exclude from stability analysis",
            }.get(value, value),
            key="ch46_data_md_policy",
        )
    with decision_cols[2]:
        greenwashing_policy = st.selectbox(
            "Greenwashing index framing",
            greenwashing_policy_options,
            index=greenwashing_policy_options.index(current_greenwashing_policy),
            format_func=lambda value: {
                "median_primary_log1p_sensitivity": "Median primary + log1p sensitivity",
                "prototype_metric_acknowledgement": "Prototype metric acknowledgement",
                "raw_mean_with_outlier_warning": "Raw mean with explicit outlier warning",
            }.get(value, value),
            key="ch46_greenwashing_policy",
        )
    with decision_cols[3]:
        ontology_top_n = st.number_input(
            "Top unmapped",
            min_value=10,
            max_value=25,
            value=int(chapter_decisions.get("ontology_top_n", 15) or 15),
            step=1,
            key="ch46_ontology_top_n",
        )

    tone_summary = tone_denominator_summary()
    tone_audit = build_tone_denominator_audit(missing_tone_policy)
    baseline_df = climatebert_baseline_table(proxy_summary_file)
    prompt_outliers = prompt_outlier_table(prompt_stab)
    greenwashing_summary = greenwashing_summary_table(greenwashing_file)
    top_unmapped_export = ontology_top_unmapped_table(
        load(ARTIFACTS / "ontology_coverage_full.csv"),
        load(NOVEL_ASPECT_REVIEW_PATH),
        int(ontology_top_n),
    )
    benchmark_df = benchmark_gap_table()

    summary_cols = st.columns(6)
    summary_cols[0].metric("Tone corpus", f"{tone_summary['total']:,}")
    summary_cols[1].metric("Tone usable", f"{tone_summary['completed']:,}", f"{tone_summary['completion_rate']:.1%}")
    summary_cols[2].metric("Tone missing", f"{tone_summary['missing']:,}", f"{tone_summary['missing_rate']:.1%}", delta_color="inverse")
    proxy_stats = proxy_agreement_summary(proxy_summary_file)
    summary_cols[3].metric("Proxy agreement", pct(proxy_stats["percent_agreement"]))
    summary_cols[4].metric("Proxy kappa", f"{proxy_stats['cohen_kappa']:.3f}")
    summary_cols[5].metric("Majority baseline", pct(CLIMATEBERT_MAJORITY_BASELINE))

    tab_ch4, tab_ch5, tab_ch6, tab_export = st.tabs(["Chapter 4", "Chapter 5", "Chapter 6", "Save / export"])

    with tab_ch4:
        st.markdown("#### Missing-tone denominator decision")
        st.dataframe(policy_options, use_container_width=True, hide_index=True, height=150)
        st.dataframe(tone_audit, use_container_width=True, hide_index=True, height=180)
        st.markdown("**Methodology paragraph**")
        st.write(methodology_paragraph_for_missing_tone(missing_tone_policy))

        st.markdown("#### ClimateBERT proxy kappa interpretation")
        st.write(
            "The 0.645 kappa should be described as agreement between ABSA-derived tone commitment and ClimateBERT climate-commitment labels, "
            "not as human inter-rater reliability. It is a construct-validity result: the two tools weakly to moderately align because they "
            "measure adjacent but different properties. ClimateBERT identifies climate-commitment classification, while the ABSA layer asks "
            "whether a disclosure claim is a commitment, action, outcome, or none. The disagreement is therefore a Chapter 4/5 finding, not just an error."
        )

        st.markdown("#### A.19 confusion matrix narrative")
        st.write(a19_confusion_narrative())
        st.dataframe(
            pd.DataFrame(
                [
                    {"confusion boundary": "outcome -> action", "correct cell": 934, "misclassified cell": 101, "interpretation": "Measured or realized outcomes are sometimes read as activity language."},
                    {"confusion boundary": "none -> commitment", "correct cell": 1781, "misclassified cell": 223, "interpretation": "Generic sustainability language is sometimes over-read as forward-looking commitment."},
                ]
            ),
            use_container_width=True,
            hide_index=True,
            height=120,
        )

    with tab_ch5:
        st.markdown("#### data.md prompt outlier")
        st.dataframe(prompt_outliers, use_container_width=True, hide_index=True, height=240)
        if data_md_policy == "retain_as_failed_experiment":
            st.write(
                "`data.md` should remain in the Chapter 5 validation section as a failed prompt condition. Its 1.000 missing-tone rate shows "
                "that the evaluation pipeline detected a complete field-level failure, which strengthens the prompt-engineering argument. "
                "State stability claims on the remaining successful prompt family separately."
            )
        else:
            st.write(
                "`data.md` should be excluded from the main prompt-stability aggregate and documented as a failed pilot prompt. "
                "The stability claim must state that it applies after removing this failed condition."
            )

        st.markdown("#### A.15 ClimateBERT baseline framing")
        st.dataframe(baseline_df, use_container_width=True, hide_index=True, height=180)
        st.write(
            "The honest A.15 framing is that the ABSA pipeline beats the naive majority baseline but not by enough to claim that it simply "
            "replaces ClimateBERT. The stronger thesis claim is construct complementarity: ClimateBERT and tone-labeled ABSA measure adjacent "
            "but distinct disclosure properties."
        )

        st.markdown("#### A.29 greenwashing index")
        st.dataframe(greenwashing_summary, use_container_width=True, hide_index=True, height=180)
        st.write(
            "Report the median as the primary statistic and use a log+1 transformed chart or sensitivity paragraph for the mean. "
            "A mean around 3,380 against a median of 0.0 across 2,071 records means the prototype index is dominated by extreme outliers, "
            "so raw bar charts need explicit caveats."
        )

    with tab_ch6:
        st.markdown("#### Ontology contribution table")
        if top_unmapped_export.empty:
            st.info("No top-unmapped ontology candidate table is available yet. Save A.12 continuation tables first, then return here.")
        else:
            st.dataframe(top_unmapped_export, use_container_width=True, hide_index=True, height=360)
            st.caption(
                "Use this as the missing A.16 backing table: top unmapped or reviewed aspects with suggested GRI/SASB/TCFD placement."
            )

        st.markdown("#### Benchmark gap positioning")
        st.dataframe(benchmark_df, use_container_width=True, hide_index=True, height=260)
        st.write(
            "Chapter 6 should position the contribution as the combination these benchmarks do not cover simultaneously: Indonesian-language, "
            "multi-aspect, tone-labeled sustainability disclosure text. Incomplete benchmark checklist items such as OCR quality, a second "
            "annotator, and ontology formalization should be framed as concrete future research directions."
        )

    with tab_export:
        resolution_rows = pd.DataFrame(
            [
                {"chapter": "4", "issue": "591 missing tone records", "decision": missing_tone_policy, "evidence": f"{tone_summary['completed']:,}/{tone_summary['total']:,} usable tone records", "writeup": methodology_paragraph_for_missing_tone(missing_tone_policy)},
                {"chapter": "4", "issue": "Proxy kappa 0.645", "decision": "frame_as_tone_vs_climatebert_construct_agreement", "evidence": f"agreement={pct(proxy_stats['percent_agreement'])}; kappa={proxy_stats['cohen_kappa']:.3f}", "writeup": "Do not describe as human inter-rater agreement; interpret as ABSA tone vs ClimateBERT climate-commitment agreement."},
                {"chapter": "4", "issue": "A.19 commitment/action/outcome/none confusion", "decision": "add_narrative_interpretation", "evidence": "outcome correct=934, outcome->action=101, none correct=1,781, none->commitment=223", "writeup": a19_confusion_narrative()},
                {"chapter": "5", "issue": "data.md missing-tone outlier", "decision": data_md_policy, "evidence": "data.md missing_tone_rate=1.000", "writeup": "Use the outlier as validation evidence for prompt sensitivity, or exclude it only after documenting it as a failed experiment."},
                {"chapter": "5", "issue": "A.15 ClimateBERT baseline", "decision": "frame_as_adjacent_constructs", "evidence": f"percent agreement={pct(proxy_stats['percent_agreement'])}; kappa={proxy_stats['cohen_kappa']:.3f}; majority baseline={pct(CLIMATEBERT_MAJORITY_BASELINE)}", "writeup": "The pipeline beats the majority baseline but should be argued as complementary to ClimateBERT, not as a replacement."},
                {"chapter": "5", "issue": "A.29 greenwashing index", "decision": greenwashing_policy, "evidence": "mean=3,380; median=0.0; n=2,071", "writeup": "Use median primary and log+1 sensitivity, or explicitly label the index as a prototype metric dominated by outliers."},
                {"chapter": "6", "issue": "Ontology contribution", "decision": "add_top_unmapped_mapping_table", "evidence": "52/52 aspects mapped in compact table; 138 novel/unmapped and 194 mapped reported in thesis notes", "writeup": "Use the top 10-15 unmapped aspects table with suggested GRI/SASB/TCFD nodes as A.16 backing evidence."},
                {"chapter": "6", "issue": "Benchmark gap framing", "decision": "claim_combined_indonesian_multi_aspect_tone_niche", "evidence": "FinBERT, ESG-BERT, SpanEval, ClimateBERT, and GH-ABSA do not cover all target pillars simultaneously.", "writeup": "Frame incomplete benchmark checklist items as future work: OCR quality, second annotator, and ontology formalization."},
            ]
        )
        st.dataframe(resolution_rows, use_container_width=True, hide_index=True, height=320)
        save_decisions = st.button("Save Chapter 4-6 resolution artifacts", type="primary", use_container_width=True, key="save_ch46_resolution_artifacts")
        if save_decisions:
            write_json(
                CHAPTER_RESOLUTION_PATH,
                {
                    "missing_tone_policy": missing_tone_policy,
                    "data_md_policy": data_md_policy,
                    "greenwashing_policy": greenwashing_policy,
                    "ontology_top_n": int(ontology_top_n),
                    "updated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                },
            )
            resolution_rows.to_csv(CHAPTER_RESOLUTION_EXPORT_PATH, index=False)
            tone_audit.to_csv(CHAPTER_TONE_DENOMINATOR_PATH, index=False)
            if not top_unmapped_export.empty:
                top_unmapped_export.to_csv(CHAPTER_ONTOLOGY_TOP_UNMAPPED_PATH, index=False)
            benchmark_df.to_csv(CHAPTER_BENCHMARK_GAP_PATH, index=False)
            st.success(
                "Saved chapter resolution artifacts to `results/revision_analysis`: "
                "`chapter_4_6_resolution_board.csv`, `chapter4_tone_denominator_audit.csv`, "
                "`chapter6_top_unmapped_ontology_candidates.csv`, and `chapter6_benchmark_gap_positioning.csv`."
            )
        st.download_button(
            "Download resolution board CSV",
            resolution_rows.to_csv(index=False).encode("utf-8"),
            "chapter_4_6_resolution_board.csv",
            "text/csv",
            use_container_width=True,
        )

t2_outputs_for_review = load_ground_truth_t2_outputs_for_a28()
a28_candidates = a28_general_misc_candidates(t2_outputs_for_review)
saved_a28_review = load(A28_GENERAL_MISC_REVIEW_PATH)
a28_review = merge_a28_general_misc_review(a28_candidates, saved_a28_review)
t2_review_candidates = t2_tone_sentiment_review_candidates(t2_outputs_for_review)
saved_t2_review = load(T2_TONE_SENTIMENT_REVIEW_PATH)
t2_tone_sentiment_review = merge_t2_tone_sentiment_review(t2_review_candidates, saved_t2_review)

with st.expander(
    "A.24-A.28 continuation — Reassess ground_truth.py T2 tone, sentiment, and General -> Misc ontology paths",
    expanded=not a28_review.empty or not t2_tone_sentiment_review.empty,
):
    st.caption(
        "This panel reads `ground_truth.py` T2 outputs and saves human reassessment rows without overwriting the raw T2 JSON/CSV. "
        "Saved corrections are stored in `results/revision_analysis` and can be used by refreshed graph attachments."
    )
    summary_cols = st.columns(6)
    summary_cols[0].metric("T2 rows", f"{len(t2_outputs_for_review):,}")
    summary_cols[1].metric("A.28 General -> Misc rows", f"{len(a28_review):,}")
    summary_cols[2].metric("A.28 saved reviews", f"{len(saved_a28_review):,}")
    high_priority_count = (
        int(t2_tone_sentiment_review["review_priority"].astype(str).eq("high").sum())
        if not t2_tone_sentiment_review.empty and "review_priority" in t2_tone_sentiment_review.columns
        else 0
    )
    summary_cols[3].metric("Tone/sentiment rows", f"{len(t2_tone_sentiment_review):,}")
    summary_cols[4].metric("High-priority reassessment", f"{high_priority_count:,}")
    summary_cols[5].metric("Tone/sentiment saved", f"{len(saved_t2_review):,}")

    tab_tone_sentiment, tab_general_misc, tab_unmapped_topic_mining, tab_corrected_summary = st.tabs(
        ["Tone + sentiment reassessment", "A.28 General -> Misc relabel", "Unmapped topic mining", "Corrected summaries"]
    )

    with tab_tone_sentiment:
        if t2_tone_sentiment_review.empty:
            st.info("No T2 tone/sentiment rows were found.")
        else:
            filter_cols = st.columns([1, 1, 1, 1])
            with filter_cols[0]:
                t2_priority_filter = st.multiselect(
                    "Priority",
                    ["high", "normal"],
                    default=["high"],
                    key="t2_reassess_priority_filter",
                )
            with filter_cols[1]:
                t2_status_filter = st.multiselect(
                    "Review status",
                    T2_REVIEW_STATUS_OPTS,
                    default=["needs_review"],
                    key="t2_reassess_status_filter",
                )
            with filter_cols[2]:
                t2_current_tone_filter = st.multiselect(
                    "Current hybrid tone",
                    sorted(t2_tone_sentiment_review["tone_pred"].astype(str).replace("", "missing").unique().tolist()),
                    default=[],
                    key="t2_reassess_tone_filter",
                )
            with filter_cols[3]:
                t2_limit = st.number_input(
                    "Rows",
                    min_value=25,
                    max_value=1000,
                    value=200,
                    step=25,
                    key="t2_reassess_limit",
                )

            t2_visible = t2_tone_sentiment_review.copy()
            if t2_priority_filter and "review_priority" in t2_visible.columns:
                t2_visible = t2_visible[t2_visible["review_priority"].isin(t2_priority_filter)].copy()
            if t2_status_filter and "review_status" in t2_visible.columns:
                t2_visible = t2_visible[t2_visible["review_status"].isin(t2_status_filter)].copy()
            if t2_current_tone_filter and "tone_pred" in t2_visible.columns:
                tone_lookup = t2_visible["tone_pred"].astype(str).replace("", "missing")
                t2_visible = t2_visible[tone_lookup.isin(t2_current_tone_filter)].copy()
            sort_cols = [col for col in ["review_priority", "tone_pred", "sentiment_pred"] if col in t2_visible.columns]
            if sort_cols:
                t2_visible = t2_visible.sort_values(sort_cols, ascending=True)
            t2_visible = t2_visible.head(int(t2_limit))
            st.caption(
                "Use `corrected_rule_tone` and `corrected_hybrid_tone` for Commitment, Action, Outcome, or Unknown. "
                "Use `corrected_sentiment` for Neutral, Positive, or Negative. Leave correction cells blank when the current label is acceptable."
            )
            edited_t2_review = st.data_editor(
                t2_visible,
                column_config={
                    "review_id": st.column_config.TextColumn("review_id", disabled=True, width="small"),
                    "label": st.column_config.TextColumn("label", disabled=True, width="medium"),
                    "timestamp": st.column_config.TextColumn("timestamp", disabled=True, width="small"),
                    "rule_tone": st.column_config.TextColumn("rule tone", disabled=True, width="small"),
                    "tone_pred": st.column_config.TextColumn("hybrid tone", disabled=True, width="small"),
                    "sentiment_pred": st.column_config.TextColumn("sentiment", disabled=True, width="small"),
                    "corrected_rule_tone": st.column_config.SelectboxColumn("corrected rule tone", options=T2_TONE_OPTS, width="medium"),
                    "corrected_hybrid_tone": st.column_config.SelectboxColumn("corrected hybrid tone", options=T2_TONE_OPTS, width="medium"),
                    "corrected_sentiment": st.column_config.SelectboxColumn("corrected sentiment", options=T2_SENTIMENT_OPTS, width="medium"),
                    "review_status": st.column_config.SelectboxColumn("status", options=T2_REVIEW_STATUS_OPTS, width="medium"),
                    "review_priority": st.column_config.TextColumn("priority", disabled=True, width="small"),
                    "ontology_path": st.column_config.TextColumn("ontology path", disabled=True, width="large"),
                    "ontology_alignment": st.column_config.NumberColumn("ontology alignment", disabled=True, width="small"),
                    "greenwashing_index": st.column_config.NumberColumn("greenwashing", disabled=True, width="small"),
                    "review_notes": st.column_config.TextColumn("notes", width="large"),
                    "text_for_review": st.column_config.TextColumn("text", disabled=True, width="large"),
                },
                hide_index=True,
                use_container_width=True,
                height=560,
                key="t2_tone_sentiment_reassessment_editor",
            )
            tone_save_cols = st.columns(3)
            if tone_save_cols[0].button("Save visible T2 tone/sentiment edits", type="primary", use_container_width=True, key="save_t2_tone_sentiment_review"):
                existing = load(T2_TONE_SENTIMENT_REVIEW_PATH)
                combined = pd.concat([existing, edited_t2_review], ignore_index=True, sort=False)
                if "review_id" in combined.columns:
                    combined = combined.drop_duplicates("review_id", keep="last")
                combined.to_csv(T2_TONE_SENTIMENT_REVIEW_PATH, index=False)
                st.success(f"Saved {len(edited_t2_review):,} T2 reassessment row(s) -> {T2_TONE_SENTIMENT_REVIEW_PATH.name}")
                st.rerun()
            if tone_save_cols[1].button("Save all high-priority rows", use_container_width=True, key="save_t2_high_priority_defaults"):
                high_priority = t2_tone_sentiment_review[
                    t2_tone_sentiment_review["review_priority"].astype(str).eq("high")
                ].copy()
                existing = load(T2_TONE_SENTIMENT_REVIEW_PATH)
                combined = pd.concat([existing, high_priority], ignore_index=True, sort=False)
                if "review_id" in combined.columns:
                    combined = combined.drop_duplicates("review_id", keep="last")
                combined.to_csv(T2_TONE_SENTIMENT_REVIEW_PATH, index=False)
                st.success(f"Saved {len(high_priority):,} high-priority T2 reassessment row(s).")
                st.rerun()
            tone_save_cols[2].download_button(
                "Download T2 reassessment",
                edited_t2_review.to_csv(index=False).encode("utf-8"),
                "ground_truth_t2_tone_sentiment_review.csv",
                "text/csv",
                use_container_width=True,
            )

    with tab_general_misc:
        if a28_review.empty:
            st.info("No exact `General -> Misc` rows were found in the current T2 ontology paths.")
        else:
            a28_filter_cols = st.columns([1, 1, 1])
            with a28_filter_cols[0]:
                a28_status_filter = st.multiselect(
                    "Review status",
                    A28_REVIEW_STATUS_OPTS,
                    default=["needs_review"],
                    key="a28_general_misc_status_filter",
                )
            with a28_filter_cols[1]:
                a28_show_filled = st.radio(
                    "Correction state",
                    ["Needs path", "Has path", "All"],
                    horizontal=True,
                    key="a28_general_misc_correction_state",
                )
            with a28_filter_cols[2]:
                a28_limit = st.number_input(
                    "Rows",
                    min_value=25,
                    max_value=1000,
                    value=200,
                    step=25,
                    key="a28_general_misc_limit",
                )
            a28_visible = a28_review.copy()
            if a28_status_filter and "review_status" in a28_visible.columns:
                a28_visible = a28_visible[a28_visible["review_status"].isin(a28_status_filter)].copy()
            has_corrected_path = a28_visible["corrected_ontology_path"].astype(str).str.strip().ne("")
            if a28_show_filled == "Needs path":
                a28_visible = a28_visible[~has_corrected_path].copy()
            elif a28_show_filled == "Has path":
                a28_visible = a28_visible[has_corrected_path].copy()
            a28_visible = a28_visible.head(int(a28_limit))
            st.caption(
                "Relabel rows where `General -> Misc` is too coarse. Use GRI/SASB/TCFD-style paths or a clear thesis ontology path."
            )
            edited_a28 = st.data_editor(
                a28_visible,
                column_config={
                    "review_id": st.column_config.TextColumn("review_id", disabled=True, width="small"),
                    "label": st.column_config.TextColumn("label", disabled=True, width="medium"),
                    "timestamp": st.column_config.TextColumn("timestamp", disabled=True, width="small"),
                    "section": st.column_config.TextColumn("section", disabled=True, width="small"),
                    "section_type": st.column_config.TextColumn("section type", disabled=True, width="small"),
                    "rule_aspects": st.column_config.TextColumn("rule aspects", disabled=True, width="medium"),
                    "tone_pred": st.column_config.TextColumn("tone", disabled=True, width="small"),
                    "sentiment_pred": st.column_config.TextColumn("sentiment", disabled=True, width="small"),
                    "ontology_alignment": st.column_config.NumberColumn("alignment", disabled=True, width="small"),
                    "current_ontology_path": st.column_config.TextColumn("current ontology path", disabled=True, width="large"),
                    "suggested_aspect": st.column_config.TextColumn("suggested aspect", width="medium"),
                    "corrected_aspect": st.column_config.TextColumn("corrected aspect", width="medium"),
                    "corrected_ontology_path": st.column_config.TextColumn("corrected ontology path", width="large"),
                    "review_status": st.column_config.SelectboxColumn("status", options=A28_REVIEW_STATUS_OPTS, width="medium"),
                    "review_notes": st.column_config.TextColumn("notes", width="large"),
                    "text_for_review": st.column_config.TextColumn("text", disabled=True, width="large"),
                },
                hide_index=True,
                use_container_width=True,
                height=560,
                key="a28_general_misc_relabel_editor",
            )
            a28_save_cols = st.columns(3)
            if a28_save_cols[0].button("Save visible A.28 relabels", type="primary", use_container_width=True, key="save_a28_general_misc_review"):
                existing = load(A28_GENERAL_MISC_REVIEW_PATH)
                combined = pd.concat([existing, edited_a28], ignore_index=True, sort=False)
                if "review_id" in combined.columns:
                    combined = combined.drop_duplicates("review_id", keep="last")
                combined.to_csv(A28_GENERAL_MISC_REVIEW_PATH, index=False)
                st.success(f"Saved {len(edited_a28):,} A.28 relabel row(s) -> {A28_GENERAL_MISC_REVIEW_PATH.name}")
                st.rerun()
            a28_save_cols[1].download_button(
                "Download A.28 relabels",
                edited_a28.to_csv(index=False).encode("utf-8"),
                "ground_truth_a28_general_misc_review.csv",
                "text/csv",
                use_container_width=True,
            )
            if a28_save_cols[2].button("Save all A.28 candidates", use_container_width=True, key="save_a28_all_candidates"):
                existing = load(A28_GENERAL_MISC_REVIEW_PATH)
                combined = pd.concat([existing, a28_review], ignore_index=True, sort=False)
                if "review_id" in combined.columns:
                    combined = combined.drop_duplicates("review_id", keep="last")
                combined.to_csv(A28_GENERAL_MISC_REVIEW_PATH, index=False)
                st.success(f"Saved {len(a28_review):,} A.28 candidate row(s).")
                st.rerun()

    with tab_unmapped_topic_mining:
        t2_unmapped = t2_unmapped_rows(t2_outputs_for_review)
        mapped_candidates = t2_unmapped_mapping_pipeline(t2_outputs_for_review, full_ontology if 'full_ontology' in locals() else pd.DataFrame())
        st.caption(
            "Topic-model unmapped T2 rows to discover vocabulary gaps, then propose add/edit actions for T2 keyword labels."
        )
        tm_cols = st.columns([1, 1, 1, 3])
        with tm_cols[0]:
            n_topics = st.number_input("Topics", min_value=3, max_value=25, value=8, step=1, key="t2_unmapped_topics_n")
        with tm_cols[1]:
            top_terms = st.number_input("Top terms", min_value=5, max_value=30, value=12, step=1, key="t2_unmapped_topics_terms")
        with tm_cols[2]:
            min_df = st.number_input("Min DF", min_value=2, max_value=50, value=5, step=1, key="t2_unmapped_topics_min_df")

        st.metric("Unmapped T2 rows", f"{len(t2_unmapped):,}")
        if not mapped_candidates.empty:
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Recovered text rows", f"{int(mapped_candidates['text_for_topic'].astype(str).str.strip().ne('').sum()):,}")
            mc2.metric("With ontology proposal", f"{int(mapped_candidates['proposed_ontology_path'].astype(str).str.strip().ne('').sum()):,}")
            mc3.metric("Pattern method", f"{int(mapped_candidates['mapping_method'].astype(str).eq('pattern').sum()):,}")
            mc4.metric("Embedding fallback", f"{int(mapped_candidates['mapping_method'].astype(str).eq('embedding_fallback').sum()):,}")

        topic_df, topic_rows_df, topic_msg = t2_topic_mining(
            mapped_candidates if not mapped_candidates.empty else t2_unmapped,
            n_topics=int(n_topics),
            top_terms=int(top_terms),
            min_df=int(min_df),
        )
        if topic_msg:
            st.info(topic_msg)
        elif topic_df.empty:
            st.info("No topic output generated.")
        else:
            saved_topic_suggestions = load(T2_UNMAPPED_TOPIC_SUGGESTIONS_PATH)
            if not saved_topic_suggestions.empty and "topic_id" in saved_topic_suggestions.columns:
                topic_df = topic_df.set_index("topic_id", drop=False)
                saved_latest = saved_topic_suggestions.drop_duplicates("topic_id", keep="last").set_index("topic_id")
                shared = topic_df.index.intersection(saved_latest.index)
                for col in ["proposed_t2_label", "proposed_keywords_csv", "review_status", "review_notes"]:
                    if col in saved_latest.columns and col in topic_df.columns:
                        incoming = saved_latest.loc[shared, col].astype(str)
                        use = incoming.str.strip().ne("")
                        topic_df.loc[use[use].index, col] = incoming.loc[use]
                topic_df = topic_df.reset_index(drop=True)

            st.markdown("**Topic summary -> proposed T2 updates**")
            edited_topics = st.data_editor(
                topic_df,
                column_config={
                    "topic_id": st.column_config.NumberColumn("topic", disabled=True, width="small"),
                    "support_docs": st.column_config.NumberColumn("support docs", disabled=True, width="small"),
                    "top_terms": st.column_config.TextColumn("top terms", disabled=True, width="large"),
                    "proposed_t2_label": st.column_config.TextColumn("proposed T2 label", width="medium"),
                    "proposed_keywords_csv": st.column_config.TextColumn("proposed keywords (csv)", width="large"),
                    "review_status": st.column_config.SelectboxColumn(
                        "status",
                        options=["needs_review", "candidate", "approved_add", "approved_edit", "reject"],
                        width="small",
                    ),
                    "review_notes": st.column_config.TextColumn("notes", width="large"),
                },
                hide_index=True,
                use_container_width=True,
                height=360,
                key="t2_unmapped_topic_editor",
            )
            save_topic_cols = st.columns(3)
            if save_topic_cols[0].button(
                "Save topic suggestions",
                type="primary",
                use_container_width=True,
                key="save_t2_unmapped_topic_suggestions",
            ):
                existing = load(T2_UNMAPPED_TOPIC_SUGGESTIONS_PATH)
                combined = pd.concat([existing, edited_topics], ignore_index=True, sort=False)
                if "topic_id" in combined.columns:
                    combined = combined.drop_duplicates("topic_id", keep="last")
                combined.to_csv(T2_UNMAPPED_TOPIC_SUGGESTIONS_PATH, index=False)
                st.success(
                    f"Saved {len(edited_topics):,} topic suggestion row(s) -> {T2_UNMAPPED_TOPIC_SUGGESTIONS_PATH.name}"
                )
            save_topic_cols[1].download_button(
                "Download topic suggestions",
                edited_topics.to_csv(index=False).encode("utf-8"),
                "ground_truth_t2_unmapped_topic_suggestions.csv",
                "text/csv",
                use_container_width=True,
            )
            save_topic_cols[2].download_button(
                "Download topic-assigned rows",
                topic_rows_df.to_csv(index=False).encode("utf-8"),
                "ground_truth_t2_unmapped_topic_rows.csv",
                "text/csv",
                use_container_width=True,
            )
            st.markdown("**Topic-assigned unmapped rows (sample)**")
            st.dataframe(
                topic_rows_df.sort_values(["topic_id", "topic_confidence"], ascending=[True, False]).head(300),
                use_container_width=True,
                hide_index=True,
                height=360,
            )
            st.warning(
                "Use approved topic suggestions to update T2 keyword dictionaries manually, then rerun T2 and compare unmapped rates before/after."
            )
        st.markdown("**Auto-suggested reassessment candidates (ontology + tone + sentiment)**")
        if mapped_candidates.empty:
            st.info("No unmapped mapping candidates available.")
        else:
            saved_map = load(T2_UNMAPPED_MAPPING_CANDIDATES_PATH)
            table = mapped_candidates.copy()
            if not saved_map.empty and "review_id" in saved_map.columns:
                latest = saved_map.drop_duplicates("review_id", keep="last").set_index("review_id")
                table = table.set_index("review_id", drop=False)
                shared = table.index.intersection(latest.index)
                for col in [
                    "proposed_ontology_path",
                    "proposed_t2_label",
                    "suggested_rule_tone",
                    "suggested_hybrid_tone",
                    "suggested_sentiment",
                    "review_status",
                    "review_notes",
                ]:
                    if col in latest.columns and col in table.columns:
                        incoming = latest.loc[shared, col].astype(str)
                        use = incoming.str.strip().ne("")
                        table.loc[use[use].index, col] = incoming.loc[use]
                table = table.reset_index(drop=True)
            table = table.sort_values(["mapping_confidence"], ascending=False)
            edit_cols = [
                c
                for c in [
                    "review_id",
                    "label",
                    "timestamp",
                    "tone_pred",
                    "sentiment_pred",
                    "ontology_path",
                    "mapping_method",
                    "mapping_confidence",
                    "proposed_ontology_path",
                    "proposed_t2_label",
                    "suggested_rule_tone",
                    "suggested_hybrid_tone",
                    "suggested_sentiment",
                    "review_status",
                    "review_notes",
                    "text_for_topic",
                ]
                if c in table.columns
            ]
            edited_map = st.data_editor(
                table[edit_cols].head(600),
                column_config={
                    "review_id": st.column_config.TextColumn("review_id", disabled=True, width="small"),
                    "label": st.column_config.TextColumn("label", disabled=True, width="medium"),
                    "tone_pred": st.column_config.TextColumn("current hybrid tone", disabled=True, width="small"),
                    "sentiment_pred": st.column_config.TextColumn("current sentiment", disabled=True, width="small"),
                    "ontology_path": st.column_config.TextColumn("current ontology path", disabled=True, width="large"),
                    "mapping_method": st.column_config.TextColumn("mapping method", disabled=True, width="small"),
                    "mapping_confidence": st.column_config.NumberColumn("confidence", disabled=True, width="small"),
                    "proposed_ontology_path": st.column_config.TextColumn("proposed ontology path", width="large"),
                    "proposed_t2_label": st.column_config.TextColumn("proposed T2 label", width="medium"),
                    "suggested_rule_tone": st.column_config.SelectboxColumn("suggested rule tone", options=T2_TONE_OPTS, width="small"),
                    "suggested_hybrid_tone": st.column_config.SelectboxColumn("suggested hybrid tone", options=T2_TONE_OPTS, width="small"),
                    "suggested_sentiment": st.column_config.SelectboxColumn("suggested sentiment", options=T2_SENTIMENT_OPTS, width="small"),
                    "review_status": st.column_config.SelectboxColumn(
                        "status",
                        options=["needs_review", "candidate", "approved", "rejected"],
                        width="small",
                    ),
                    "review_notes": st.column_config.TextColumn("notes", width="large"),
                    "text_for_topic": st.column_config.TextColumn("text", disabled=True, width="large"),
                },
                hide_index=True,
                use_container_width=True,
                height=520,
                key="t2_unmapped_mapping_editor",
            )
            map_save_cols = st.columns(3)
            if map_save_cols[0].button(
                "Save reassessment candidates",
                type="primary",
                use_container_width=True,
                key="save_t2_unmapped_mapping_candidates",
            ):
                existing = load(T2_UNMAPPED_MAPPING_CANDIDATES_PATH)
                combined = pd.concat([existing, edited_map], ignore_index=True, sort=False)
                if "review_id" in combined.columns:
                    combined = combined.drop_duplicates("review_id", keep="last")
                combined.to_csv(T2_UNMAPPED_MAPPING_CANDIDATES_PATH, index=False)
                st.success(
                    f"Saved {len(edited_map):,} reassessment candidate row(s) -> {T2_UNMAPPED_MAPPING_CANDIDATES_PATH.name}"
                )
            map_save_cols[1].download_button(
                "Download reassessment candidates",
                edited_map.to_csv(index=False).encode("utf-8"),
                "ground_truth_t2_unmapped_mapping_candidates.csv",
                "text/csv",
                use_container_width=True,
            )
            approved = edited_map[
                edited_map["review_status"].astype(str).isin(["approved"])
            ].copy() if "review_status" in edited_map.columns else pd.DataFrame()
            map_save_cols[2].download_button(
                "Download approved-only",
                approved.to_csv(index=False).encode("utf-8"),
                "ground_truth_t2_unmapped_mapping_candidates_approved.csv",
                "text/csv",
                use_container_width=True,
            )

    with tab_corrected_summary:
        corrected_t2 = apply_t2_review_corrections(t2_outputs_for_review, load(T2_TONE_SENTIMENT_REVIEW_PATH))
        summary_left, summary_right = st.columns(2)
        with summary_left:
            st.markdown("**Saved T2 reassessment summary**")
            st.dataframe(t2_review_summary(load(T2_TONE_SENTIMENT_REVIEW_PATH)), use_container_width=True, hide_index=True, height=220)
            if not corrected_t2.empty:
                for col, title in [
                    ("rule_tone", "Corrected rule tone"),
                    ("tone_pred", "Corrected hybrid tone"),
                    ("sentiment_pred", "Corrected sentiment"),
                ]:
                    if col in corrected_t2.columns:
                        counts = corrected_t2[col].astype(str).replace("", "Unclassified / Unknown").value_counts().rename_axis(title).reset_index(name="records")
                        st.dataframe(counts, use_container_width=True, hide_index=True, height=180)
        with summary_right:
            st.markdown("**Saved A.28 relabel summary**")
            st.dataframe(a28_review_summary(load(A28_GENERAL_MISC_REVIEW_PATH)), use_container_width=True, hide_index=True, height=220)
            if not load(A28_GENERAL_MISC_REVIEW_PATH).empty:
                corrected_paths = load(A28_GENERAL_MISC_REVIEW_PATH)
                path_col = "corrected_ontology_path"
                if path_col in corrected_paths.columns:
                    path_counts = (
                        corrected_paths[path_col]
                        .astype(str)
                        .str.strip()
                        .replace("", "not corrected")
                        .value_counts()
                        .rename_axis("corrected ontology path")
                        .reset_index(name="records")
                        .head(30)
                    )
                    st.dataframe(path_counts, use_container_width=True, hide_index=True, height=360)
        st.info(
            "After saving corrections, refresh the Chapter 4-6 graph attachments or rerun the graph page to regenerate A.24, A.25, A.26, and A.28 from the corrected review artifacts."
        )

legacy_a4 = climatebert_a4_legacy_summary()
full_a4 = climatebert_tone_crosstab(imported)
binary_a4 = climatebert_commitment_crosstab(imported)
a4_work = climatebert_a4_work_items(silver, imported)
a4_model_summary = climatebert_model_summary(imported)
a4_label_col = climatebert_label_column(imported)
a4_model_label_inventory = climatebert_model_label_inventory()
a4_labels = []
if a4_label_col and a4_label_col in imported.columns:
    a4_labels = sorted(imported[a4_label_col].astype(str).str.strip().replace("", pd.NA).dropna().unique().tolist())

with st.expander("A.4 continuation — Tone by ClimateBERT label", expanded=legacy_a4["label_assignments"] < cb_real):
    st.caption(
        "A.4 currently points to the older `results/visualizations/tone_climatebert_label_crosstab.csv`. "
        "That file is based on the compact visualization snapshot and counts exploded label assignments, "
        "so its total can be larger than 332 but smaller than the full Action Plan corpus."
    )
    a4_cols = st.columns(4)
    a4_cols[0].metric("Legacy A.4 exploded label-cell count", f"{legacy_a4['label_assignments']:,}")
    a4_cols[1].metric("Legacy compact tone rows", f"{legacy_a4['rows']:,}")
    a4_cols[2].metric("Full corpus rows (Action Plan)", f"{cb_target_total:,}")
    a4_cols[3].metric("Current ClimateBERT predictions", f"{cb_real:,}/{cb_target_total:,}")
    st.warning(
        "A.4 denominator clarification: `Legacy A.4 exploded label-cell count` and `Full corpus rows` are different units and must not be compared directly."
    )
    local_label_count = int(a4_model_label_inventory["label"].nunique()) if not a4_model_label_inventory.empty and "label" in a4_model_label_inventory.columns else 0
    st.caption(
        f"Local model inventory: `{ROOT_MODELS_DIR}` contains "
        f"{a4_model_label_inventory['model'].nunique() if not a4_model_label_inventory.empty and 'model' in a4_model_label_inventory.columns else 0:,} "
        f"config-backed model folder(s) and {local_label_count:,} distinct documented label value(s)."
    )

    with st.expander("Definitions and table logic", expanded=True):
        st.caption(
            "A.4 currently combines labels from different ClimateBERT-style model families. "
            "The first table defines observed A.4 labels; the local inventory below documents every label map found in `model_download/models`."
        )
        st.dataframe(
            climatebert_label_definitions(a4_labels),
            use_container_width=True,
            hide_index=True,
            height=240,
        )
        if a4_model_label_inventory.empty:
            st.info(f"No local model labels found at `{ROOT_MODELS_DIR}`.")
        else:
            st.markdown("**Local `model_download/models` label inventory**")
            st.dataframe(
                a4_model_label_inventory,
                use_container_width=True,
                hide_index=True,
                height=360,
            )
            generic = a4_model_label_inventory[
                a4_model_label_inventory["label"].astype(str).str.startswith("LABEL_")
                | a4_model_label_inventory["label"].astype(str).eq("No classification labels in local config")
            ]
            if not generic.empty:
                st.warning(
                    "Some local models expose generic `LABEL_*` values or no classification label map in `config.json`. "
                    "Keep those out of A.4 interpretation until their semantic mapping is manually confirmed."
                )
        st.markdown("**How A.4 is computed**")
        st.dataframe(
            climatebert_a4_logic_rows(a4_label_col),
            use_container_width=True,
            hide_index=True,
            height=220,
        )
        st.warning(
            "Do not read `Brown Projects`, `Misinformation`, or `Ambiguous Actions` as the negative side of the commitment model. "
            "They come from a controversy classifier, while `yes/no` comes from the binary commitment classifier."
        )

    st.markdown("**Work to continue**")
    st.dataframe(a4_work, use_container_width=True, hide_index=True, height=220)

    tab_full, tab_binary, tab_models, tab_inventory = st.tabs(["Full label table", "Binary commitment table", "Model/job check", "Local label inventory"])
    with tab_full:
        if full_a4.empty:
            st.info("No full ClimateBERT label table can be built yet. Import ClimateBERT outputs with a label column first.")
        else:
            st.dataframe(full_a4, use_container_width=True, hide_index=True, height=260)
            label_cols = [c for c in full_a4.columns if c != "tone"]
            long_full = full_a4.melt("tone", value_vars=label_cols, var_name="climatebert_label", value_name="records")
            chart = (
                alt.Chart(long_full)
                .mark_rect()
                .encode(
                    x=alt.X("climatebert_label:N", title="ClimateBERT label"),
                    y=alt.Y("tone:N", title="Tone"),
                    color=alt.Color("records:Q", scale=alt.Scale(scheme="tealblues")),
                    tooltip=["tone", "climatebert_label", "records"],
                )
                .properties(height=260)
            )
            labels = alt.Chart(long_full).mark_text(fontSize=11).encode(
                x="climatebert_label:N",
                y="tone:N",
                text="records:Q",
                color=alt.condition(alt.datum.records > long_full["records"].max() * 0.55, alt.value("white"), alt.value("#1f2937")),
            )
            st.altair_chart(chart + labels, use_container_width=True)
    with tab_binary:
        if binary_a4.empty:
            st.info("No binary commitment crosstab can be built yet.")
        else:
            st.dataframe(binary_a4, use_container_width=True, hide_index=True, height=220)
            bin_cols = [c for c in binary_a4.columns if c != "tone"]
            long_binary = binary_a4.melt("tone", value_vars=bin_cols, var_name="climatebert_commitment", value_name="records")
            bar = (
                alt.Chart(long_binary)
                .mark_bar()
                .encode(
                    x=alt.X("records:Q", title="Records"),
                    y=alt.Y("tone:N", title="Tone", sort="-x"),
                    color=alt.Color("climatebert_commitment:N", title="ClimateBERT"),
                    tooltip=["tone", "climatebert_commitment", "records"],
                )
                .properties(height=260)
            )
            st.altair_chart(bar, use_container_width=True)
    with tab_models:
        if a4_model_summary.empty:
            st.info("No ClimateBERT model metadata found in the imported output.")
        else:
            st.dataframe(a4_model_summary, use_container_width=True, hide_index=True, height=260)
            st.warning(
                "Review this before promoting the full table to the thesis figure. "
                "Some current rows may come from non-commitment ClimateBERT classifiers, so their labels should not be mixed with binary commitment agreement."
            )
    with tab_inventory:
        if a4_model_label_inventory.empty:
            st.info(f"No local model labels found at `{ROOT_MODELS_DIR}`.")
        else:
            family_counts = (
                a4_model_label_inventory.groupby(["model family"], dropna=False)
                .agg(models=("model", "nunique"), label_rows=("label", "size"), labels=("label", lambda s: ", ".join(sorted({str(v) for v in s})[:12])))
                .reset_index()
                .sort_values(["models", "label_rows"], ascending=False)
            )
            st.dataframe(family_counts, use_container_width=True, hide_index=True, height=260)
            st.dataframe(a4_model_label_inventory, use_container_width=True, hide_index=True, height=360)
            st.download_button(
                "Download local ClimateBERT-style label inventory",
                a4_model_label_inventory.to_csv(index=False).encode("utf-8"),
                "climatebert_model_download_label_inventory.csv",
                "text/csv",
                use_container_width=True,
            )

    save_cols = st.columns(3)
    if save_cols[0].button("Save A.4 continuation tables", type="primary", use_container_width=True, key="save_a4_continuation"):
        saved_primary = save_a4_primary_artifacts(full_a4)
        if not binary_a4.empty:
            binary_a4.to_csv(VIS / "tone_climatebert_commitment_crosstab_full.csv", index=False)
        a4_work.to_csv(ARTIFACTS / "climatebert_a4_continuation_worklist.csv", index=False)
        if not a4_model_label_inventory.empty:
            a4_model_label_inventory.to_csv(ARTIFACTS / "climatebert_model_download_label_inventory.csv", index=False)
        saved_text = ", ".join(f"`{name}`" for name in saved_primary) if saved_primary else "(no A.4 label table saved)"
        st.success(
            "Saved A.4 continuation artifacts: "
            f"{saved_text}, "
            "`tone_climatebert_commitment_crosstab_full.csv`, and "
            "`climatebert_a4_continuation_worklist.csv`. "
            "The local model label inventory is saved as `climatebert_model_download_label_inventory.csv` when labels are found."
        )
    save_cols[1].download_button(
        "Download worklist CSV",
        a4_work.to_csv(index=False).encode("utf-8"),
        "climatebert_a4_continuation_worklist.csv",
        "text/csv",
        use_container_width=True,
    )
    if not full_a4.empty:
        save_cols[2].download_button(
            "Download full A.4 table",
            full_a4.to_csv(index=False).encode("utf-8"),
            "tone_climatebert_label_crosstab_full.csv",
            "text/csv",
            use_container_width=True,
        )

full_ontology = build_full_ontology_coverage(annot if not annot.empty else silver)
a12_summary = ontology_a12_summary(ontology, full_ontology, len(annot if not annot.empty else silver))
a12_breakdown = ontology_a12_breakdown(full_ontology)
a12_work = ontology_a12_work_items(ontology, full_ontology, len(annot if not annot.empty else silver))

with st.expander("A.12 continuation — Ontology mapped vs novel aspects", expanded=a12_summary["legacy_records"] < a12_summary["corpus_rows"]):
    st.caption(
        "A.12 currently uses `results/revision_analysis/ontology_coverage.csv`. "
        "That file is a unique-aspect coverage table from the compact legacy evidence snapshot: "
        "its `records` values sum to the old denominator, not the current Action Plan corpus."
    )
    a12_cols = st.columns(4)
    a12_cols[0].metric("Legacy covered records", f"{a12_summary['legacy_records']:,}")
    a12_cols[1].metric("Legacy aspect rows", f"{a12_summary['legacy_aspects']:,}")
    a12_cols[2].metric("Full covered records", f"{a12_summary['full_records']:,}/{a12_summary['corpus_rows']:,}")
    a12_cols[3].metric("Full unique aspects", f"{a12_summary['full_aspects']:,}")
    st.warning(
        "A.12 clarification: placeholders (`missing`, `none`, `unknown`, etc.) are tracked separately from substantive novel aspects."
    )
    b1, b2, b3 = st.columns(3)
    b1.metric(
        "Mapped (full)",
        f"{a12_breakdown['mapped_aspects']:,} aspects",
        delta=f"{a12_breakdown['mapped_records']:,} records",
    )
    b2.metric(
        "Substantive novel (full)",
        f"{a12_breakdown['substantive_novel_aspects']:,} aspects",
        delta=f"{a12_breakdown['substantive_novel_records']:,} records",
    )
    b3.metric(
        "Placeholders (full)",
        f"{a12_breakdown['placeholder_aspects']:,} aspects",
        delta=f"{a12_breakdown['placeholder_records']:,} records",
    )

    st.markdown("**Work to continue**")
    st.dataframe(a12_work, use_container_width=True, hide_index=True, height=220)

    tab_full_ontology, tab_unmapped, tab_legacy_ontology = st.tabs(["Full ontology table", "High-frequency novel aspects", "Legacy A.12 table"])
    with tab_full_ontology:
        if full_ontology.empty:
            st.info("No full ontology continuation table can be built yet.")
        else:
            st.dataframe(full_ontology, use_container_width=True, hide_index=True, height=300)
            plot = full_ontology.copy()
            plot["mapped"] = "substantive novel / needs review"
            mapped_mask = ontology_bool(plot["mapped_to_ontology"])
            placeholder_mask = is_missing_aspect_series(plot["aspect"])
            plot.loc[mapped_mask, "mapped"] = "mapped"
            plot.loc[placeholder_mask, "mapped"] = "placeholder / missing label"
            summary_plot = plot.groupby("mapped", dropna=False)["records"].sum().reset_index()
            chart = (
                alt.Chart(summary_plot)
                .mark_bar()
                .encode(
                    x=alt.X("records:Q", title="Record assignments"),
                    y=alt.Y("mapped:N", title=None),
                    color=alt.Color("mapped:N", legend=None),
                    tooltip=["mapped", "records"],
                )
                .properties(height=160)
            )
            st.altair_chart(chart, use_container_width=True)
    with tab_unmapped:
        if full_ontology.empty:
            st.info("No unmapped aspect table available yet.")
        else:
            unmapped_full = full_ontology[~ontology_bool(full_ontology["mapped_to_ontology"])].copy()
            saved_novel_review = load(NOVEL_ASPECT_REVIEW_PATH)
            novel_review = build_novel_aspect_review_table(unmapped_full, saved_novel_review)
            st.caption(
                "These are candidates for ontology extension. Review high-frequency rows first, and keep placeholders like `missing` separate from real ESG concepts."
            )
            if novel_review.empty:
                st.info("No novel aspect rows are available for editing.")
            else:
                review_counts = novel_review["review_status"].value_counts().to_dict() if "review_status" in novel_review.columns else {}
                cluster_filled = int(novel_review["reviewed_cluster"].astype(str).str.strip().ne("").sum()) if "reviewed_cluster" in novel_review.columns else 0
                path_filled = int(novel_review["ontology_path"].astype(str).str.strip().ne("").sum()) if "ontology_path" in novel_review.columns else 0
                notes_filled = int(novel_review["thesis_note"].astype(str).str.strip().ne("").sum()) if "thesis_note" in novel_review.columns else 0
                novel_cols = st.columns(7)
                novel_cols[0].metric("Novel rows", f"{len(novel_review):,}")
                novel_cols[1].metric("Confirmed", f"{review_counts.get('confirmed_novel', 0):,}")
                novel_cols[2].metric("Mapped existing", f"{review_counts.get('mapped_existing', 0):,}")
                novel_cols[3].metric("Still needs review", f"{review_counts.get('needs_review', 0):,}")
                novel_cols[4].metric("Cluster filled", f"{cluster_filled:,}")
                novel_cols[5].metric("Path filled", f"{path_filled:,}")
                novel_cols[6].metric("Notes filled", f"{notes_filled:,}")
                st.caption(
                    "`Confirmed` and `Mapped existing` count only rows where `review_status` is set to "
                    "`confirmed_novel` or `mapped_existing`. Cluster, ontology path, and thesis notes are tracked separately."
                )

                filter_left, filter_mid, filter_right = st.columns([2, 1, 1])
                with filter_left:
                    status_filter = st.multiselect(
                        "Review status",
                        NOVEL_ASPECT_STATUS_OPTS,
                        default=["needs_review", "confirmed_novel"],
                        key="a12_novel_status_filter",
                    )
                with filter_mid:
                    table_scope = st.radio(
                        "Table rows",
                        ["Top N", "All"],
                        horizontal=True,
                        key="a12_novel_table_scope",
                    )
                with filter_right:
                    top_novel_rows = st.number_input(
                        "Top N",
                        min_value=10,
                        max_value=500,
                        value=100,
                        step=10,
                        disabled=table_scope == "All",
                        key="a12_novel_rows_limit",
                    )

                visible_novel = novel_review.copy()
                if status_filter and "review_status" in visible_novel.columns:
                    visible_novel = visible_novel[visible_novel["review_status"].isin(status_filter)].copy()
                visible_novel = visible_novel.sort_values("records", ascending=False)
                if table_scope == "Top N":
                    visible_novel = visible_novel.head(int(top_novel_rows))
                st.caption(f"Showing {len(visible_novel):,} of {len(novel_review):,} novel aspect row(s) in the editable table.")
                st.caption("Reviewed cluster options: " + ", ".join(CLUSTER_NAMES))

                edited_novel = st.data_editor(
                    visible_novel,
                    column_config={
                        "aspect": st.column_config.TextColumn("aspect", disabled=True, width="large"),
                        "records": st.column_config.NumberColumn("records", disabled=True, width="small"),
                        "review_status": st.column_config.SelectboxColumn("status", options=NOVEL_ASPECT_STATUS_OPTS, width="medium"),
                        "canonical_aspect": st.column_config.TextColumn("canonical aspect", width="large"),
                        "suggested_cluster": st.column_config.TextColumn("suggested cluster", disabled=True, width="medium"),
                        "reviewed_cluster": st.column_config.SelectboxColumn("reviewed cluster", options=[""] + CLUSTER_NAMES, width="medium"),
                        "suggested_path": st.column_config.TextColumn("suggested path", disabled=True, width="large"),
                        "ontology_path": st.column_config.TextColumn("ontology path", width="large"),
                        "thesis_note": st.column_config.TextColumn("thesis note", width="large"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=700 if table_scope == "All" else 420,
                    key="a12_high_frequency_novel_aspect_editor",
                )

                edit_actions = st.columns(3)
                if edit_actions[0].button("Save visible novel aspect edits", type="primary", use_container_width=True, key="save_a12_novel_aspects"):
                    existing = load(NOVEL_ASPECT_REVIEW_PATH)
                    combined = pd.concat([existing, edited_novel], ignore_index=True, sort=False)
                    if "aspect" in combined.columns:
                        combined = combined.drop_duplicates("aspect", keep="last")
                    combined.to_csv(NOVEL_ASPECT_REVIEW_PATH, index=False)
                    st.success(f"Saved {len(edited_novel):,} novel aspect review row(s) -> {NOVEL_ASPECT_REVIEW_PATH.name}")
                    st.rerun()
                if edit_actions[1].button("Save all auto-suggestions", use_container_width=True, key="save_a12_all_novel_auto"):
                    auto = novel_review.copy()
                    existing = load(NOVEL_ASPECT_REVIEW_PATH)
                    combined = pd.concat([existing, auto], ignore_index=True, sort=False)
                    if "aspect" in combined.columns:
                        combined = combined.drop_duplicates("aspect", keep="last")
                    combined.to_csv(NOVEL_ASPECT_REVIEW_PATH, index=False)
                    st.success(f"Saved {len(auto):,} auto-filled novel aspect review row(s) -> {NOVEL_ASPECT_REVIEW_PATH.name}")
                    st.rerun()
                edit_actions[2].download_button(
                    "Download edited novel aspects",
                    edited_novel.to_csv(index=False).encode("utf-8"),
                    "ontology_novel_aspect_review.csv",
                    "text/csv",
                    use_container_width=True,
                )

                chart_left, chart_right = st.columns([1, 1])
                with chart_left:
                    chart_scope = st.radio(
                        "Chart rows",
                        ["Top 20", "All visible table rows"],
                        horizontal=True,
                        key="a12_novel_chart_scope",
                    )
                with chart_right:
                    color_by_status = st.checkbox(
                        "Color by status",
                        value=True,
                        key="a12_novel_chart_color_status",
                    )

                chart_source = edited_novel.copy()
                if "canonical_aspect" in chart_source.columns:
                    chart_source["display_aspect"] = chart_source["canonical_aspect"].astype(str).str.strip()
                    chart_source.loc[chart_source["display_aspect"].eq(""), "display_aspect"] = chart_source["aspect"]
                else:
                    chart_source["display_aspect"] = chart_source["aspect"]
                top = chart_source.sort_values("records", ascending=False)
                if chart_scope == "Top 20":
                    top = top.head(20)
                chart_encoding = {
                    "x": alt.X("records:Q", title="Records"),
                    "y": alt.Y("display_aspect:N", sort="-x", title=None),
                    "tooltip": [
                        alt.Tooltip("aspect:N", title="original aspect"),
                        alt.Tooltip("display_aspect:N", title="canonical aspect"),
                        alt.Tooltip("records:Q"),
                        alt.Tooltip("review_status:N", title="status"),
                        alt.Tooltip("ontology_path:N", title="ontology path"),
                    ],
                }
                if color_by_status:
                    chart_encoding["color"] = alt.Color("review_status:N", title="Status")
                    bar = alt.Chart(top).mark_bar().encode(**chart_encoding)
                else:
                    bar = alt.Chart(top).mark_bar(color="#2f6f73").encode(**chart_encoding)
                bar = bar.properties(height=min(1200, max(180, len(top) * 24)))
                st.altair_chart(bar, use_container_width=True)
    with tab_legacy_ontology:
        if ontology.empty:
            st.info("No legacy ontology coverage table found.")
        else:
            st.dataframe(ontology, use_container_width=True, hide_index=True, height=300)

    save_a12_cols = st.columns(3)
    if save_a12_cols[0].button("Save A.12 continuation tables", type="primary", use_container_width=True, key="save_a12_continuation"):
        if not full_ontology.empty:
            full_ontology.to_csv(ARTIFACTS / "ontology_coverage_full.csv", index=False)
            unmapped_full = full_ontology[~ontology_bool(full_ontology["mapped_to_ontology"])].copy()
            novel_review = build_novel_aspect_review_table(unmapped_full, load(NOVEL_ASPECT_REVIEW_PATH))
            if not novel_review.empty:
                novel_review.to_csv(NOVEL_ASPECT_REVIEW_PATH, index=False)
        a12_work.to_csv(ARTIFACTS / "ontology_a12_continuation_worklist.csv", index=False)
        st.success(
            "Saved A.12 continuation artifacts: "
            "`ontology_coverage_full.csv`, `ontology_novel_aspect_review.csv`, "
            "and `ontology_a12_continuation_worklist.csv`."
        )
    save_a12_cols[1].download_button(
        "Download A.12 worklist",
        a12_work.to_csv(index=False).encode("utf-8"),
        "ontology_a12_continuation_worklist.csv",
        "text/csv",
        use_container_width=True,
    )
    if not full_ontology.empty:
        save_a12_cols[2].download_button(
            "Download full ontology table",
            full_ontology.to_csv(index=False).encode("utf-8"),
            "ontology_coverage_full.csv",
            "text/csv",
            use_container_width=True,
        )

missing_aspect_candidates = ontology_missing_aspect_records(annot if not annot.empty else silver)
saved_missing_labels = load(ONTOLOGY_MISSING_LABELS_PATH)
missing_aspect_review = merge_saved_missing_aspect_labels(missing_aspect_candidates, saved_missing_labels)
missing_label_done = (
    int(missing_aspect_review["corrected_aspect_label"].astype(str).str.strip().ne("").sum())
    if not missing_aspect_review.empty and "corrected_aspect_label" in missing_aspect_review.columns
    else 0
)

with st.expander("A.16 continuation — Label missing ontology-extension data", expanded=not missing_aspect_review.empty and missing_label_done < len(missing_aspect_review)):
    st.caption(
        "A.16 should describe ontology-extension candidates, not placeholder values. "
        "Use this panel to label records where the aspect is blank, `missing`, `none`, or otherwise not a substantive ESG concept."
    )
    a16_cols = st.columns(4)
    a16_cols[0].metric("Rows needing aspect review", f"{len(missing_aspect_review):,}")
    a16_cols[1].metric("Corrected labels saved", f"{missing_label_done:,}")
    a16_cols[2].metric("Saved label file rows", f"{len(saved_missing_labels):,}")
    a16_cols[3].metric("Remaining", f"{max(len(missing_aspect_review) - missing_label_done, 0):,}")

    if missing_aspect_review.empty:
        st.success("No missing or placeholder aspect rows were detected in the current annotation/silver table.")
    else:
        row_view = st.radio(
            "Rows to show",
            ["Needs label", "Labelled", "All"],
            horizontal=True,
            key="a16_missing_rows_view",
        )
        review_table = missing_aspect_review.copy()
        has_label = review_table["corrected_aspect_label"].astype(str).str.strip().ne("")
        if row_view == "Needs label":
            review_table = review_table[~has_label].copy()
        elif row_view == "Labelled":
            review_table = review_table[has_label].copy()
        review_table = review_table.head(250)

        edit_cols = [
            "record_id",
            "company",
            "tone_pred",
            "ground_truth_esg",
            "esg",
            "current_ground_truth_aspect",
            "pipeline_aspect",
            "suggested_aspect_label",
            "corrected_aspect_label",
            "suggested_cluster",
            "suggested_ontology_path",
            "ontology_extension_status",
            "missing_reason",
            "review_notes",
            "text",
        ]
        st.caption(
            f"Showing {len(review_table):,} row(s). Fill `corrected_aspect_label`; set status to `labelled` when ready."
        )
        edited_missing = st.data_editor(
            review_table[[col for col in edit_cols if col in review_table.columns]],
            column_config={
                "record_id": st.column_config.TextColumn("record_id", disabled=True, width="small"),
                "company": st.column_config.TextColumn("company", disabled=True, width="small"),
                "tone_pred": st.column_config.TextColumn("tone", disabled=True, width="small"),
                "ground_truth_esg": st.column_config.TextColumn("GT ESG", disabled=True, width="small"),
                "esg": st.column_config.TextColumn("pipeline ESG", disabled=True, width="small"),
                "current_ground_truth_aspect": st.column_config.TextColumn("current GT aspect", disabled=True, width="medium"),
                "pipeline_aspect": st.column_config.TextColumn("pipeline aspect", disabled=True, width="medium"),
                "suggested_aspect_label": st.column_config.TextColumn("suggested aspect", disabled=True, width="medium"),
                "corrected_aspect_label": st.column_config.TextColumn("corrected aspect", width="large"),
                "suggested_cluster": st.column_config.SelectboxColumn("cluster", options=[""] + CLUSTER_NAMES, width="medium"),
                "suggested_ontology_path": st.column_config.TextColumn("ontology path", width="large"),
                "ontology_extension_status": st.column_config.SelectboxColumn(
                    "status",
                    options=["needs_review", "labelled", "not_esg", "insufficient_context", "discard"],
                    width="medium",
                ),
                "missing_reason": st.column_config.TextColumn("reason", disabled=True, width="medium"),
                "review_notes": st.column_config.TextColumn("notes", width="large"),
                "text": st.column_config.TextColumn("text", disabled=True, width="large"),
            },
            hide_index=True,
            use_container_width=True,
            height=420,
            key="a16_missing_aspect_editor",
        )

        a16_save_cols = st.columns(3)
        if a16_save_cols[0].button("Save visible A.16 labels", type="primary", use_container_width=True, key="save_a16_missing_labels"):
            existing = load(ONTOLOGY_MISSING_LABELS_PATH)
            combined = pd.concat([existing, edited_missing], ignore_index=True, sort=False)
            if "record_id" in combined.columns:
                combined = combined.drop_duplicates("record_id", keep="last")
            combined.to_csv(ONTOLOGY_MISSING_LABELS_PATH, index=False)
            st.success(f"Saved {len(edited_missing):,} visible label row(s) -> {ONTOLOGY_MISSING_LABELS_PATH.name}")
            st.rerun()

        valid_updates = edited_missing[
            edited_missing["corrected_aspect_label"].astype(str).str.strip().ne("")
        ].copy() if "corrected_aspect_label" in edited_missing.columns else pd.DataFrame()
        apply_disabled = valid_updates.empty or annot.empty or "record_id" not in annot.columns
        if a16_save_cols[1].button(
            "Apply labels to annotation file",
            use_container_width=True,
            disabled=apply_disabled,
            key="apply_a16_missing_labels",
        ):
            base = annot.copy().set_index("record_id", drop=False)
            updates = valid_updates.set_index("record_id", drop=False)
            shared = base.index.intersection(updates.index)
            base.loc[shared, "ground_truth_aspect"] = updates.loc[shared, "corrected_aspect_label"].astype(str)
            base.reset_index(drop=True).to_csv(ANNOTATION_PATH, index=False)
            st.success(f"Applied {len(shared):,} corrected aspect label(s) -> {ANNOTATION_PATH.name}")
            st.rerun()

        a16_save_cols[2].download_button(
            "Download A.16 labels",
            merge_saved_missing_aspect_labels(missing_aspect_candidates, edited_missing).to_csv(index=False).encode("utf-8"),
            "ontology_missing_aspect_labels.csv",
            "text/csv",
            use_container_width=True,
        )

        with st.expander("A.16 labelling guidance", expanded=False):
            st.markdown(
                """
                - Use a concrete ESG topic for `corrected_aspect_label`, not `missing` or `none`.
                - Mark `not_esg` when the record is not actually ESG evidence.
                - Mark `insufficient_context` when the text is too fragmentary to infer a defensible aspect.
                - Keep placeholders separate from novel ontology terms when writing the A.16 interpretation.
                """
            )

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 1 — ClimateBERT
# ═════════════════════════════════════════════════════════════════════════════
if show[1]:
    badge = "✅" if cb_real >= cb_target_total else ("🟡" if cb_real > 0 else "🔴")
    with st.expander(
        f"{badge} Step 1 — Run ClimateBERT on all {cb_target_total:,} records",
        expanded=cb_real < cb_target_total,
    ):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.markdown("#### What is ClimateBERT and what does 'run' mean?")
            st.info(
                "**ClimateBERT** is a pre-trained AI model (a fine-tuned RoBERTa) that reads a "
                "sentence and answers one question: *is this a climate-commitment statement or not?*\n\n"
                "Right now your κ = 0.645 is based on **proxy labels** — labels your own LLM pipeline "
                "generated as a stand-in. To make RQ3 publication-ready, you need to run the real "
                "ClimateBERT model on the current analysis records and import those outputs here.\n\n"
                f"The current Action Plan corpus has **{cb_target_total:,}** records; older A.4 visualizations used the compact 332-record snapshot.\n\n"
                "**Runtime depends on the selected model and whether you resume only missing records.**"
            )

            st.markdown("#### Step-by-step")
            st.markdown(
                f"1. **Download** the {cb_target_total:,}-record batch input CSV below.\n"
                "2. **Run the script** — paste it into a `.py` file or Google Colab cell.\n"
                "3. The script produces `climatebert_output.csv`.\n"
                "4. **Upload** that CSV in the import section below — the Agreement panel updates automatically."
            )

            st.markdown("#### Python script to run ClimateBERT")
            st.code(CLIMATEBERT_SCRIPT, language="python")

            st.markdown("#### 1a. Download batch input")
            if not silver.empty:
                batch_cols = [c for c in ["record_id", "company", "prompt", "model", "language", "tone_pred", "text"] if c in silver.columns]
                st.download_button(
                    "⬇ Download climatebert_332_record_batch_input.csv",
                    silver[batch_cols].to_csv(index=False).encode("utf-8"),
                    file_name="climatebert_332_record_batch_input.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.warning(f"silver_tone_ground_truth.csv not found at {SILVER_PATH}")

            st.markdown("#### 1b. Upload real ClimateBERT outputs")
            st.markdown("#### 1b-alt. Run Step 1 in the background")
            st.caption(
                "This creates `results/revision_analysis/climatebert_output.csv`, the same file shape as the copy-paste script. "
                "The upload/import section below can then import that background-produced file."
            )
            CLIMATEBERT_JOBS.mkdir(parents=True, exist_ok=True)
            cb_jobs = climatebert_jobs()
            latest_cb_job = cb_jobs[0] if cb_jobs else None
            cb_model_backend = st.radio(
                "ClimateBERT source",
                ["Local model", "Hugging Face model id"],
                horizontal=True,
                key="cb_bg_model_backend",
                help="Local model discovery follows the same pattern as ground_truth.py.",
            )
            local_candidates = find_all_model_dirs(ROOT_MODELS_DIR)
            local_map = {str(path.relative_to(ROOT_MODELS_DIR)): path for path in local_candidates}
            cb_model_id = "climatebert/distilroberta-base-climate-commitment"
            cb_local_label = ""
            cb_local_path = ""
            if cb_model_backend == "Local model":
                st.caption(f"Scanning local models at `{ROOT_MODELS_DIR}`")
                if local_map:
                    cb_local_label = st.selectbox(
                        "Local ClimateBERT / text-classification model folder",
                        sorted(local_map),
                        index=0,
                        key="cb_bg_local_model",
                    )
                    cb_local_path = str(local_map[cb_local_label])
                    cb_model_id = cb_local_label
                else:
                    st.warning("No local model folders found. Check `model_download/models`.")
                    with st.expander("Debug local model discovery", expanded=False):
                        st.write("Exists:", ROOT_MODELS_DIR.exists())
                        if ROOT_MODELS_DIR.exists():
                            st.write([str(p.relative_to(ROOT_MODELS_DIR)) for p in ROOT_MODELS_DIR.rglob("*") if p.is_dir()][:50])
            else:
                cb_model_id = st.text_input(
                    "Hugging Face ClimateBERT model id",
                    value="climatebert/distilroberta-base-climate-commitment",
                    key="cb_bg_model_id",
                )

            bg_cols = st.columns([1, 1, 1])
            cb_limit = bg_cols[0].number_input(
                "Run rows",
                min_value=0,
                max_value=max(1, len(silver)),
                value=0,
                help="0 means all rows. Use a small number to test first.",
                key="cb_bg_limit",
            )
            cb_max_chars = bg_cols[1].number_input("Max chars/text", 256, 4000, 1200, 128, key="cb_bg_max_chars")
            cb_dry_run = bg_cols[2].checkbox("Dry run", value=False, key="cb_bg_dry_run")
            cb_skip_existing = st.checkbox("Skip record IDs already present in imported ClimateBERT CSV", value=True, key="cb_bg_skip_existing")
            cb_resume_missing = st.checkbox(
                "Continue only unprocessed records",
                value=True,
                key="cb_bg_resume_missing",
                help="Build this background job from the record IDs missing in imported/background ClimateBERT output, instead of scanning all rows.",
            )
            cb_resume_ids = cb_unprocessed_ids if cb_resume_missing else []
            if cb_resume_missing:
                st.caption(
                    f"Resume mode will process **{len(cb_resume_ids):,}** unprocessed record(s) "
                    f"and skip **{len(cb_processed_ids):,}** already processed record ID(s)."
                )
            if st.button("Start Step 1 ClimateBERT background run", type="primary", use_container_width=True, key="start_cb_bg"):
                job_id = f"climatebert_step1_{utc_now_id()}_{uuid.uuid4().hex[:6]}"
                job_dir = CLIMATEBERT_JOBS / job_id
                effective_total = len(cb_resume_ids) if cb_resume_missing else (int(cb_limit) if int(cb_limit) else len(silver))
                config = {
                    "job_id": job_id,
                    "model_backend": cb_model_backend,
                    "model_id": cb_model_id,
                    "local_model_path": cb_local_path,
                    "limit": int(cb_limit),
                    "record_ids": cb_resume_ids,
                    "max_chars": int(cb_max_chars),
                    "skip_existing": bool(cb_skip_existing),
                    "dry_run": bool(cb_dry_run),
                    "text_col": "text",
                    "record_col": "record_id",
                    "resume_missing_only": bool(cb_resume_missing),
                    "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                }
                write_json(job_dir / "config.json", config)
                write_json(job_dir / "control.json", {"stop_requested": False})
                write_json(
                    job_dir / "status.json",
                    {
                        "job_id": job_id,
                        "status": "queued",
                        "total": effective_total,
                        "completed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "current": "Queued missing-only resume" if cb_resume_missing else "Queued",
                        "created_at": config["created_at"],
                    },
                )
                launch_climatebert_job(job_id)
                st.success(f"Started `{job_id}`")
                st.rerun()

            cb_jobs = climatebert_jobs()
            if cb_jobs:
                selected_cb_job = st.selectbox("ClimateBERT background job", cb_jobs, index=0, key="selected_cb_bg_job")
                cb_job_dir = CLIMATEBERT_JOBS / selected_cb_job
                cb_status = read_json(cb_job_dir / "status.json", {})
                cb_events = read_events(cb_job_dir / "events.jsonl")
                cb_total = int(cb_status.get("total") or 0)
                cb_completed = int(cb_status.get("completed") or 0)
                st.progress((cb_completed / cb_total) if cb_total else 0.0, text=f"{cb_completed}/{cb_total} records complete")
                if st.button("Refresh selected ClimateBERT job progress", use_container_width=True, key="refresh_selected_cb_progress"):
                    st.rerun()
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Status", cb_status.get("status", "unknown"))
                s2.metric("Failed", int(cb_status.get("failed") or 0))
                s3.metric("Skipped", int(cb_status.get("skipped") or 0))
                s4.metric("PID", cb_status.get("pid") or "None", delta="alive" if is_alive(cb_status.get("pid")) else "not running")
                if cb_status.get("script_output_path"):
                    st.caption(f"Background script-compatible output: `{cb_status.get('script_output_path')}`")
                if st.button("Stop selected ClimateBERT job after current row", use_container_width=True, key="stop_cb_bg"):
                    request_climatebert_stop(selected_cb_job)
                    st.rerun()
                with st.expander("ClimateBERT background events/logs", expanded=False):
                    if cb_events.empty:
                        st.info("No events yet.")
                    else:
                        st.dataframe(cb_events.tail(100).iloc[::-1], use_container_width=True, hide_index=True)
                    st.markdown("**stderr**")
                    st.code((cb_job_dir / "worker.err.log").read_text(encoding="utf-8", errors="ignore")[-5000:] if (cb_job_dir / "worker.err.log").exists() else "")

            uploaded = st.file_uploader(
                "Upload the `climatebert_output.csv` produced by the script",
                type=["csv"], key="cb_upload"
            )
            if CLIMATEBERT_OUTPUT_PATH.exists():
                st.info(f"Background output found: `{CLIMATEBERT_OUTPUT_PATH}`")
                bg_df = pd.read_csv(CLIMATEBERT_OUTPUT_PATH).fillna("")
                st.dataframe(bg_df.tail(20), use_container_width=True, height=180)
                st.download_button(
                    "Download background climatebert_output.csv",
                    bg_df.to_csv(index=False).encode("utf-8"),
                    "climatebert_output.csv",
                    "text/csv",
                    use_container_width=True,
                )
                bg_possible = [c for c in ["climate_commitment", "label", "top_label", "climate_commitment_label"] if c in bg_df.columns]
                if bg_possible:
                    bg_lcol = st.selectbox("Background output commitment label column", bg_possible, key="cb_bg_lcol")
                    if st.button("Import background climatebert_output.csv into real ClimateBERT outputs", type="primary", use_container_width=True):
                        imported = import_climatebert_output(bg_df, bg_lcol)
                        st.success(f"Imported {len(imported)} records from background `climatebert_output.csv` → {IMPORTED_PATH.name}")
                        st.rerun()
                else:
                    st.warning("Background `climatebert_output.csv` is missing a commitment label column.")

            if uploaded:
                df_up = pd.read_csv(uploaded).fillna("")
                if "record_id" not in df_up.columns:
                    st.error("CSV must contain a `record_id` column.")
                else:
                    possible = [c for c in ["climate_commitment", "label", "top_label", "climate_commitment_label"] if c in df_up.columns]
                    if not possible:
                        st.error("No commitment output column found. Need one of: climate_commitment, label, top_label.")
                    else:
                        lcol = st.selectbox("Which column holds the climate-commitment label?", possible, key="cb_lcol")
                        merged = import_climatebert_output(df_up, lcol)
                        st.success(f"Saved {len(merged)} records → {IMPORTED_PATH.name}")
                        imported = merged

        with right:
            st.markdown("#### Current status")
            st.metric("Real ClimateBERT records", f"{cb_real} / {cb_target_total}", delta="✓ Done" if cb_real >= cb_target_total else "Not yet")
            st.progress(
                min(cb_real / cb_target_total, 1.0) if cb_target_total else 0.0,
                text=f"Imported ClimateBERT output progress: {cb_real}/{cb_target_total} records",
            )
            st.caption(
                f"Detected processed record IDs across imported/background output: **{len(cb_processed_ids):,}**. "
                f"Remaining unprocessed records: **{len(cb_unprocessed_ids):,}**."
            )
            if cb_unprocessed_ids:
                with st.expander("Preview unprocessed ClimateBERT records", expanded=False):
                    preview_cols = [c for c in ["record_id", "company", "prompt", "model", "tone_pred", "text"] if c in silver.columns]
                    preview = silver[silver["record_id"].astype(str).isin(cb_unprocessed_ids)][preview_cols].head(50)
                    st.dataframe(preview, use_container_width=True, hide_index=True, height=220)

            cb_jobs_for_status = climatebert_jobs()
            if cb_jobs_for_status:
                latest_status = read_json(CLIMATEBERT_JOBS / cb_jobs_for_status[0] / "status.json", {})
                latest_total = int(latest_status.get("total") or 0)
                latest_completed = int(latest_status.get("completed") or 0)
                latest_cols = st.columns([3, 1])
                latest_cols[0].caption(f"Latest background job: `{cb_jobs_for_status[0]}`")
                if latest_cols[1].button("Refresh progress", use_container_width=True, key="refresh_latest_cb_progress"):
                    st.rerun()
                st.progress(
                    min(latest_completed / latest_total, 1.0) if latest_total else 0.0,
                    text=f"Latest job progress: {latest_completed}/{latest_total} records · {latest_status.get('status', 'unknown')}",
                )

            if not proxy.empty and "tone_pred" in proxy.columns and "has_climate_commitment" in proxy.columns:
                st.markdown("**Proxy agreement (already reportable)**")
                truth = proxy["tone_pred"].astype(str).eq("commitment")
                pred  = proxy["has_climate_commitment"].astype(bool)
                agree = (truth == pred).mean()
                k, n  = cohen_kappa(truth.astype(str), pred.astype(str))
                cc1, cc2 = st.columns(2)
                cc1.metric("Agreement", f"{agree:.1%}")
                cc2.metric(kappa_label(k), "")
                st.caption("This is your PROXY κ (already in your thesis). Once you upload real ClimateBERT outputs, the real κ will appear here.")

            if not imported.empty and "climatebert_commitment_pred" in imported.columns and "tone_pred" in imported.columns:
                st.markdown("**Real ClimateBERT agreement**")
                cb_pred_series = column_series(imported, "climatebert_commitment_pred").astype(str).str.strip()
                valid = imported[cb_pred_series.ne("")]
                truth_r = column_series(valid, "tone_pred").astype(str).eq("commitment")
                pred_r  = column_series(valid, "climatebert_commitment_pred").astype(str).str.lower().isin(["true", "1", "yes"])
                agree_r = (truth_r == pred_r).mean()
                k_r, n_r = cohen_kappa(truth_r.astype(str), pred_r.astype(str))
                rc1, rc2 = st.columns(2)
                rc1.metric("Real agreement", f"{agree_r:.1%}")
                rc2.metric(kappa_label(k_r), f"n={n_r}")

    st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 2 — Annotation
# ═════════════════════════════════════════════════════════════════════════════
if show[2]:
    all_done = tone_done >= ANNOTATION_TARGET and esg_done >= ANNOTATION_TARGET and aspect_done >= ANNOTATION_TARGET
    badge = "✅" if all_done else ("🟡" if tone_done > 0 else "🔴")
    with st.expander(f"{badge} Step 2 — Complete pilot annotation to {ANNOTATION_TARGET} records  ·  ~1 week", expanded=not all_done):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.markdown("#### What you need to annotate")
            st.info(
                f"The editor now starts from the full **{len(annot):,}-row annotation dataset** "
                f"(**{len(silver_base):,}** original silver rows"
                f"{f' + **{len(llm_silver):,}** live LLM reprocess rows' if not llm_silver.empty else ''}). "
                f"Complete at least **{ANNOTATION_TARGET} records** by filling in **4 fields**:\n\n"
                "| Field | Values | What it means |\n"
                "|---|---|---|\n"
                "| `ground_truth_tone` | commitment / action / outcome / none / unknown | The disclosure maturity level |\n"
                "| `ground_truth_esg` | e / s / g / e-s / e-g / s-g / e-s-g / none / unknown | One or more ESG pillars |\n"
                "| `ground_truth_aspect` | free text | The specific ESG topic (e.g. *carbon emissions*, *water usage*) |\n"
                "| `review_status` | reviewed / uncertain / discard | Your confidence in this row |\n\n"
                f"**Also needed for κ:** A second annotator labels the same {ANNOTATION_TARGET} records independently. "
                "You then compute Cohen's κ between the two sets."
            )

            st.caption("Multi-pillar ESG values are accepted. You can paste `e-s`, `e/g`, `E, S`, `environmental-social`, or `e-s-g`; they are normalized to `e-s`, `e-g`, `s-g`, or `e-s-g`.")
            if not llm_silver.empty:
                st.success(
                    f"Live reprocess output detected: **{len(llm_silver):,}** extracted LLM records are now included below "
                    "with `record_id` values starting with `llm_`."
                )
                if st.button("Persist live LLM rows into silver_tone_ground_truth.csv", key="persist_llm_silver"):
                    migrated = migrate_live_reprocess_outputs(silver_base, llm_silver, model_stab_static, pd.DataFrame())
                    st.success(f"Saved {migrated['silver_rows']:,} live row(s) -> {SILVER_PATH.name}")
                    st.rerun()

            st.markdown("#### Bulk paste from Google Sheets")
            st.markdown(
                "Set up a Google Sheet with these columns, fill in your labels, "
                "then copy 50 rows (include the header row) and paste below."
            )

            tpl_cols = ["record_id", "ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "review_status", "annotator", "review_notes"]
            if not annot.empty:
                sample = annot.head(3)[[c for c in tpl_cols if c in annot.columns]]
                st.caption("Google Sheets template (columns to use):")
                st.dataframe(sample, use_container_width=True, height=120)

            pasted = st.text_area(
                "Paste here (Ctrl+V from Google Sheets)",
                height=180,
                placeholder="record_id\tground_truth_tone\tground_truth_esg\t...\nr000_000\tcommitment\te-s\t...",
                key="paste_area",
            )

            if pasted.strip():
                try:
                    df_paste = pd.read_csv(StringIO(pasted.strip()), sep="\t").fillna("")
                    df_paste = normalise_annotation_values(df_paste)
                    if "record_id" not in df_paste.columns:
                        st.error("Pasted data must have a `record_id` column (first column) to match records.")
                    else:
                        target_cols = [c for c in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect",
                                                    "review_status", "annotator", "review_notes"] if c in df_paste.columns]
                        if not target_cols:
                            st.error(f"No annotation columns detected. Found columns: {list(df_paste.columns)}")
                        else:
                            st.success(f"Parsed {len(df_paste)} rows  ·  columns: {target_cols}")
                            st.dataframe(df_paste.head(10), use_container_width=True, height=200)

                            if st.button("✅ Apply paste → save to annotation file", type="primary", key="apply_paste"):
                                base = annot.copy()
                                base = base.set_index("record_id")
                                upd  = df_paste.set_index("record_id")
                                for col in target_cols:
                                    if col in upd.columns:
                                        base.loc[base.index.isin(upd.index), col] = upd.loc[upd.index.isin(base.index), col]
                                if "ground_truth_esg" in base.columns:
                                    base["ground_truth_esg"] = base["ground_truth_esg"].map(normalise_esg_value)
                                base.reset_index().to_csv(ANNOTATION_PATH, index=False)
                                st.success(f"Saved {len(df_paste)} updates → {ANNOTATION_PATH.name}")
                                st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")

            st.markdown("#### Or edit directly in the table")
            if not annot.empty:
                missing_mask = missing_annotation_mask(annot)
                editor_view = st.radio(
                    "Rows to show",
                    ["Not annotated yet", "Live LLM reprocess rows", "All data"],
                    horizontal=True,
                    key="annotation_editor_view",
                    help="Not annotated yet shows rows missing tone, ESG, or aspect ground-truth fields.",
                )
                if editor_view == "Not annotated yet":
                    annot_editor_df = annot[missing_mask].copy()
                elif editor_view == "Live LLM reprocess rows":
                    if "record_id" in annot.columns:
                        annot_editor_df = annot[annot["record_id"].astype(str).str.startswith("llm_")].copy()
                    else:
                        annot_editor_df = annot.iloc[0:0].copy()
                else:
                    annot_editor_df = annot.copy()
                st.caption(f"Showing {len(annot_editor_df):,} of {len(annot):,} rows. Missing/incomplete rows: {int(missing_mask.sum()):,}.")
                edit_cols = [c for c in ["record_id", "text", "tone_pred", "ground_truth_tone",
                                         "ground_truth_esg", "ground_truth_aspect", "review_status",
                                         "annotator", "review_notes"] if c in annot.columns]
                col_cfg = {
                    "ground_truth_tone":   st.column_config.SelectboxColumn("ground_truth_tone",   options=TONE_OPTS),
                    "ground_truth_esg":    st.column_config.SelectboxColumn("ground_truth_esg",    options=ESG_OPTS),
                    "review_status":       st.column_config.SelectboxColumn("review_status",       options=STATUS_OPTS),
                    "text":                st.column_config.TextColumn("text", width="large"),
                }
                edited = st.data_editor(annot_editor_df[edit_cols], use_container_width=True, height=380,
                                        column_config=col_cfg,
                                        disabled=["record_id", "text", "tone_pred"], key="annot_editor")
                if st.button("Save direct edits", key="save_direct"):
                    try:
                        base = annot.set_index("record_id", drop=False)
                        upd = normalise_annotation_values(edited).set_index("record_id", drop=False)
                        shared = base.index.intersection(upd.index)
                        if shared.empty:
                            st.warning("No matching record_id values found to save.")
                        else:
                            for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect",
                                        "review_status", "annotator", "review_notes"]:
                                if col in upd.columns and col in base.columns:
                                    base.loc[shared, col] = upd.loc[shared, col]
                            if "ground_truth_esg" in base.columns:
                                base["ground_truth_esg"] = base["ground_truth_esg"].map(normalise_esg_value)
                            base.reset_index(drop=True).to_csv(ANNOTATION_PATH, index=False)
                            st.success(f"Saved → {ANNOTATION_PATH.name} ({len(shared):,} row(s) updated)")
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Save failed: {exc}")
                        st.stop()

        with right:
            st.markdown("#### Annotation progress")
            for label, done, total in [
                ("Tone labels (ground_truth_tone)",     tone_done,   ANNOTATION_TARGET),
                ("ESG labels (ground_truth_esg)",       esg_done,    ANNOTATION_TARGET),
                ("Aspect labels (ground_truth_aspect)", aspect_done, ANNOTATION_TARGET),
            ]:
                pct = min(done / total, 1.0)
                st.markdown(f"**{label}** — {done}/{total}")
                st.progress(pct)

            st.divider()
            st.markdown("#### Agreement with LLM predictions")
            if not annot.empty and "ground_truth_tone" in annot.columns and "tone_pred" in annot.columns:
                labelled = annot[annot["ground_truth_tone"].astype(str).str.strip().ne("")]
                if len(labelled) >= 2:
                    k, n = cohen_kappa(labelled["tone_pred"], labelled["ground_truth_tone"])
                    st.metric("Tone κ (human vs LLM)", kappa_label(k), f"n={n}")
                    st.caption("Target: κ ≥ 0.60 before thesis submission.")
                    if k is not None and k < 0.6:
                        st.warning("κ < 0.60 — review disagreements and refine tone definitions.")
                else:
                    st.info(f"{tone_done} tone labels so far — κ computed once ≥ 2 rows labelled.")

            st.divider()
            st.markdown("#### Tone distribution (predicted)")
            if not annot.empty and "tone_pred" in annot.columns:
                tc = annot["tone_pred"].value_counts().reset_index()
                tc.columns = ["tone", "count"]
                chart = alt.Chart(tc).mark_bar(color="#2f6f73").encode(
                    x=alt.X("count:Q", title=None),
                    y=alt.Y("tone:N", sort="-x", title=None),
                    tooltip=["tone", "count"],
                ).properties(height=160)
                st.altair_chart(chart, use_container_width=True)

            st.markdown("#### Ground-truth ESG combination distribution")
            if not annot.empty and "ground_truth_esg" in annot.columns:
                esg_counts = (
                    annot["ground_truth_esg"]
                    .map(normalise_esg_value)
                    .replace("", "missing")
                    .value_counts()
                    .reset_index()
                )
                esg_counts.columns = ["ground_truth_esg", "count"]
                esg_chart = alt.Chart(esg_counts).mark_bar(color="#395b91").encode(
                    x=alt.X("count:Q", title=None),
                    y=alt.Y("ground_truth_esg:N", sort="-x", title=None),
                    tooltip=["ground_truth_esg", "count"],
                ).properties(height=190)
                st.altair_chart(esg_chart, use_container_width=True)

    st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 3 — OCR Ground Truth
# ═════════════════════════════════════════════════════════════════════════════
if show[3]:
    with st.expander("🔴 Step 3 — OCR ground truth sample  ·  ~4 h", expanded=False):
        left, right = st.columns([3, 2], gap="large")

        with left:
            st.info(
                "**What you're doing:** Pick 50–100 pages from your 23 PDFs, type (or verify) "
                "the correct text for each page, then load them into the OCR Quality Workbench. "
                "That page computes CER/WER automatically.\n\n"
                "While doing this, tag each page with a failure mode — "
                "this simultaneously fills the RQ4 failure rate gap (Step 5)."
            )
            st.markdown("#### Pages you've processed")
            if not ocr_df.empty:
                st.dataframe(ocr_df, use_container_width=True, height=300)
                done_docs = ocr_df[ocr_df["status"].astype(str).eq("done")] if "status" in ocr_df.columns else ocr_df
                st.metric("Documents processed", f"{len(done_docs)} / {len(ocr_df)}")
            else:
                st.info("No OCR processing summary found.")

            st.markdown("#### Open OCR Quality Workbench")
            st.markdown("Open `1_2_OCR_Quality_Workbench.py` from the Streamlit sidebar.")

        with right:
            st.markdown("#### Progress")
            st.metric("Manual CER/WER sample", "0 / 100 pages", delta="Needed", delta_color="inverse")
            st.metric("Failure mode tags", "0 / 10 modes", delta="Needed", delta_color="inverse")
            st.markdown("#### Failure mode categories to tag")
            for fm in FAILURE_MODES:
                st.markdown(f"- {fm}")

    st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# REPROCESS EXISTING OCR PAGES WITH LLM
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("🧪 Reprocess existing OCR pages with selected LLM and prompt", expanded=False):
    st.info(
        "Use this to rerun existing OCR markdown pages through the background LLM worker. "
        "Choose a PDF, page subset, prompt, and LLM model; the job writes to `results/background_llm_jobs` "
        "and appends successful outputs to `results/esg_records.json`."
    )

    left, right = st.columns([3, 2], gap="large")
    with left:
        docs = list_documents()
        selected_doc = st.selectbox("PDF / OCR document", docs, index=0 if docs else None, key="action_llm_doc")
        page_names = list_pages(selected_doc) if selected_doc else []
        page_mode = st.radio("Pages to reprocess", ["First N pages", "Page range", "Specific pages", "All pages"], horizontal=True, key="action_llm_page_mode")
        if page_mode == "First N pages":
            page_n = st.number_input("N pages", min_value=1, max_value=max(1, len(page_names)), value=min(5, max(1, len(page_names))), key="action_llm_page_n")
            selected_pages = page_names[: int(page_n)]
        elif page_mode == "Page range":
            max_page = max(1, len(page_names))
            page_range = st.slider("Page range", 1, max_page, (1, min(5, max_page)), key="action_llm_page_range")
            selected_pages = page_names[page_range[0] - 1 : page_range[1]]
        elif page_mode == "All pages":
            selected_pages = page_names
        else:
            selected_pages = st.multiselect("Specific OCR pages", page_names, default=page_names[:3], key="action_llm_specific_pages")

        prompts = list_prompts()
        selected_prompt = st.selectbox("Prompt", prompts, index=0 if prompts else None, key="action_llm_prompt")
        backend = st.selectbox("LLM provider", ["Mock", "OpenRouter", "LM Studio / OpenAI-compatible", "Ollama"], key="action_llm_backend")
        openrouter_api_key = st.text_input(
            "OpenRouter API key",
            value=os.getenv("OPENROUTER_API_KEY", ""),
            type="password",
            key="action_llm_openrouter_key",
            help="Used only when the provider is OpenRouter.",
        )
        lmstudio_url = st.text_input("LM Studio URL", value="http://127.0.0.1:1234/v1", key="action_llm_lms_url")
        lmstudio_api_key = st.text_input("LM Studio API key", value=os.getenv("LMSTUDIO_API_KEY", ""), type="password", key="action_llm_lms_key")
        ollama_url = st.text_input("Ollama URL", value="http://127.0.0.1:11434", key="action_llm_ollama_url")
        ollama_api_key = st.text_input("Ollama API key", value=os.getenv("OLLAMA_API_KEY", ""), type="password", key="action_llm_ollama_key")

        model_options = selectable_models_for_backend(backend, lmstudio_url, lmstudio_api_key, ollama_url, ollama_api_key)
        model_search = st.text_input("Search model", "", key="action_llm_model_search")
        visible_models = [m for m in model_options if model_search.lower() in m.lower()] if model_search.strip() else model_options
        selected_models = st.multiselect(
            f"LLM model(s) ({len(visible_models)} available)",
            visible_models,
            default=visible_models[:1],
            key="action_llm_models",
        )
        manual_models = st.text_area("Manual model ids, one per line", "", height=70, key="action_llm_manual_models")
        selected_models = list(dict.fromkeys(selected_models + [line.strip() for line in manual_models.splitlines() if line.strip()]))

        c1, c2, c3 = st.columns(3)
        batch_size = c1.number_input("Batch size", 1, max(1, len(selected_pages)), 1, key="action_llm_batch_size")
        context_length = c2.number_input("Context chars", 500, 100000, 10000, 500, key="action_llm_context")
        max_tokens = c3.number_input("Max tokens", 64, 8192, 1500, 64, key="action_llm_max_tokens")
        temperature = st.number_input("Temperature", 0.0, 2.0, 0.0, 0.1, key="action_llm_temperature")
        skip_existing = st.checkbox("Skip already successful model/target/prompt triples", value=False, key="action_llm_skip_existing")

        can_reprocess = bool(selected_doc and selected_pages and selected_prompt and selected_models)
        if st.button("Start LLM reprocess background job", type="primary", disabled=not can_reprocess, use_container_width=True):
            job_id = f"llm_bg_action_{utc_now_id()}_{uuid.uuid4().hex[:6]}"
            job_dir = LLM_JOBS_DIR / job_id
            total = len(selected_models) * ((len(selected_pages) + int(batch_size) - 1) // int(batch_size))
            config = {
                "job_id": job_id,
                "document": selected_doc,
                "page_names": selected_pages,
                "batch_size": int(batch_size),
                "prompt_names": [selected_prompt],
                "prompt_override": "",
                "backend": backend,
                "mock_mode": backend == "Mock",
                "models": selected_models,
                "openrouter_api_key": openrouter_api_key,
                "lmstudio_url": lmstudio_url,
                "lmstudio_api_key": lmstudio_api_key,
                "ollama_url": ollama_url,
                "ollama_api_key": ollama_api_key,
                "ollama_num_ctx": 2048,
                "context_length": int(context_length),
                "max_tokens": int(max_tokens),
                "temperature": float(temperature),
                "retries": 2,
                "sample_error_retries": 2,
                "auto_reduce_context_on_error": True,
                "context_retry_floor": 1200,
                "target_retry_floor": 2000,
                "skip_existing": bool(skip_existing),
                "save_results": True,
                "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
            write_json(job_dir / "config.json", config)
            write_json(job_dir / "control.json", {"pause_requested": False, "stop_requested": False})
            write_json(
                job_dir / "status.json",
                {
                    "job_id": job_id,
                    "status": "queued",
                    "document": selected_doc,
                    "total": total,
                    "completed": 0,
                    "failed": 0,
                    "skipped": 0,
                    "current": "Queued from Action Plan",
                    "created_at": config["created_at"],
                },
            )
            launch_llm_job(job_id)
            st.success(f"Started `{job_id}`")
            st.rerun()

    with right:
        st.markdown("#### Latest reprocess jobs")
        jobs = llm_jobs()
        if not jobs:
            st.info("No LLM background jobs found yet.")
        else:
            job_rows = []
            for job_id in jobs[:10]:
                status = read_json(LLM_JOBS_DIR / job_id / "status.json", {})
                config = read_json(LLM_JOBS_DIR / job_id / "config.json", {})
                total = int(status.get("total") or 0)
                completed = int(status.get("completed") or 0)
                job_rows.append(
                    {
                        "job_id": job_id,
                        "status": status.get("status", "unknown"),
                        "progress_pct": round(completed / total * 100, 1) if total else 0,
                        "completed": completed,
                        "total": total,
                        "failed": int(status.get("failed") or 0),
                        "document": status.get("document") or config.get("document", ""),
                        "prompt": ", ".join(config.get("prompt_names", [])) if isinstance(config.get("prompt_names"), list) else "",
                        "models": ", ".join(config.get("models", [])[:2]) if isinstance(config.get("models"), list) else "",
                    }
                )
            jobs_df = pd.DataFrame(job_rows)
            st.dataframe(jobs_df, use_container_width=True, hide_index=True, height=260)
            latest = job_rows[0]
            st.progress(latest["progress_pct"] / 100 if latest["total"] else 0, text=f"Latest job: {latest['completed']}/{latest['total']} · {latest['status']}")

    st.markdown("#### Data visualization by PDF and prompt")
    llm_records = load_llm_records()
    if llm_records.empty:
        st.info("No LLM extraction records found yet. Start a background reprocess job or generate `tone_records_flat.csv`.")
    else:
        docs_available = sorted(llm_records["target_doc"].astype(str).replace("", "unknown").unique())
        prompts_available = sorted(llm_records["prompt"].astype(str).replace("", "unknown").unique())
        default_viz_docs = [selected_doc] if selected_doc in docs_available else docs_available[:5]
        default_viz_prompts = [selected_prompt] if selected_prompt in prompts_available else prompts_available[:3]
        f1, f2 = st.columns(2)
        selected_docs_viz = f1.multiselect("PDF filter", docs_available, default=default_viz_docs, key="action_viz_docs")
        selected_prompts_viz = f2.multiselect("Prompt filter", prompts_available, default=default_viz_prompts, key="action_viz_prompts")
        viz_df = llm_records.copy()
        if selected_docs_viz:
            viz_df = viz_df[viz_df["target_doc"].astype(str).isin(selected_docs_viz)]
        if selected_prompts_viz:
            viz_df = viz_df[viz_df["prompt"].astype(str).isin(selected_prompts_viz)]
        summary = (
            viz_df.groupby(["target_doc", "prompt"], dropna=False)
            .agg(samples=("records_count", "size"), extracted_records=("records_count", "sum"))
            .reset_index()
        )
        if summary.empty:
            st.info("No records match the current PDF/prompt filters.")
        else:
            total_records = int(summary["extracted_records"].sum())
            total_samples = int(summary["samples"].sum())
            zero_outputs = int(summary["extracted_records"].eq(0).sum())
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("PDFs shown", f"{summary['target_doc'].nunique():,}")
            m2.metric("Prompts shown", f"{summary['prompt'].nunique():,}")
            m3.metric("Extracted records", f"{total_records:,}")
            m4.metric("Zero-output PDF/prompt pairs", f"{zero_outputs:,}")

            pdf_totals = (
                summary.groupby("target_doc", dropna=False)
                .agg(extracted_records=("extracted_records", "sum"), samples=("samples", "sum"))
                .reset_index()
                .sort_values("extracted_records", ascending=False)
            )
            prompt_totals = (
                summary.groupby("prompt", dropna=False)
                .agg(extracted_records=("extracted_records", "sum"), samples=("samples", "sum"))
                .reset_index()
                .sort_values("extracted_records", ascending=False)
            )

            tab_pdf, tab_prompt, tab_heatmap, tab_table = st.tabs(
                ["PDF results", "Prompt results", "PDF × prompt heatmap", "Result table"]
            )

            with tab_pdf:
                chart = alt.Chart(pdf_totals).mark_bar(color="#3f7c85").encode(
                    x=alt.X("extracted_records:Q", title="Extracted records"),
                    y=alt.Y("target_doc:N", sort="-x", title="PDF / processed document", axis=alt.Axis(labelLimit=320)),
                    tooltip=["target_doc", "samples", "extracted_records"],
                ).properties(height=min(520, max(240, 42 * len(pdf_totals))))
                st.altair_chart(chart, use_container_width=True)
                if len(pdf_totals):
                    top_pdf = pdf_totals.iloc[0]
                    st.success(
                        f"Highest extracted output: **{top_pdf['target_doc']}** "
                        f"with **{int(top_pdf['extracted_records']):,}** records from **{int(top_pdf['samples']):,}** run/batch samples."
                    )

            with tab_prompt:
                prompt_chart = alt.Chart(prompt_totals).mark_bar(color="#6f8f45").encode(
                    x=alt.X("extracted_records:Q", title="Extracted records"),
                    y=alt.Y("prompt:N", sort="-x", title="Prompt", axis=alt.Axis(labelLimit=320)),
                    tooltip=["prompt", "samples", "extracted_records"],
                ).properties(height=min(420, max(220, 42 * len(prompt_totals))))
                st.altair_chart(prompt_chart, use_container_width=True)

                stacked = alt.Chart(summary).mark_bar().encode(
                    x=alt.X("extracted_records:Q", title="Extracted records"),
                    y=alt.Y("prompt:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320)),
                    color=alt.Color("target_doc:N", title="PDF"),
                    tooltip=["target_doc", "prompt", "samples", "extracted_records"],
                ).properties(height=min(420, max(220, 42 * summary["prompt"].nunique())))
                st.altair_chart(stacked, use_container_width=True)

            with tab_heatmap:
                heatmap = alt.Chart(summary).mark_rect().encode(
                    x=alt.X("prompt:N", title="Prompt", axis=alt.Axis(labelAngle=-35, labelLimit=220)),
                    y=alt.Y("target_doc:N", title="PDF / processed document", sort="-x", axis=alt.Axis(labelLimit=300)),
                    color=alt.Color("extracted_records:Q", title="Extracted records", scale=alt.Scale(scheme="tealblues")),
                    tooltip=["target_doc", "prompt", "samples", "extracted_records"],
                ).properties(height=min(520, max(260, 34 * summary["target_doc"].nunique())))
                st.altair_chart(heatmap, use_container_width=True)

            with tab_table:
                zero_df = summary[summary["extracted_records"].eq(0)].sort_values(["target_doc", "prompt"])
                if not zero_df.empty:
                    st.warning(f"{len(zero_df):,} PDF/prompt pair(s) produced zero extracted records.")
                    st.dataframe(zero_df, use_container_width=True, hide_index=True, height=160)
                st.dataframe(
                    summary.sort_values("extracted_records", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    height=300,
                )
                st.download_button(
                    "Download action result summary CSV",
                    summary.sort_values("extracted_records", ascending=False).to_csv(index=False).encode("utf-8"),
                    "action_result_by_pdf_prompt.csv",
                    "text/csv",
                    use_container_width=True,
                )

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 4 — Model stability
# ═════════════════════════════════════════════════════════════════════════════
if show[4]:
    n_m = model_stab["model"].astype(str).nunique() if not model_stab.empty and "model" in model_stab.columns else 0
    badge = "✅" if n_m >= 3 else ("🟡" if n_m == 2 else "🔴")
    with st.expander(f"{badge} Step 4 — Add 3rd model + repeated runs at temperature=0  ·  ~3 h", expanded=n_m < 3):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.info(
                "**Why this matters:** You currently have 2 models. Academic cross-model claims "
                "require ≥ 3 to be credible (otherwise one model is always 'better' by construction).\n\n"
                "**What to do:**\n"
                "1. Add one smaller open-weight model (e.g. a 7B model) as a lower bound.\n"
                "2. For each of 7 prompts × 3 models: run **3 times** at `temperature=0`.\n"
                "3. This gives you mean ± SD parse success per prompt — the core RQ6 stability table.\n\n"
                "**LLM Background Run Monitor** already tracks job state:\n"
            )
            st.markdown("Open `2_3_LLM_Background_Run_Monitor.py` or `2_0_LLM_Processing_Result_Visualizer.py` from the Streamlit sidebar.")

            st.markdown("#### Current models in results")
            if not model_stab.empty:
                st.dataframe(model_stab, use_container_width=True, height=180)
                if not model_stab_live.empty:
                    st.success(
                        f"Live reprocess model summary detected: **{len(model_stab_live):,}** model row(s) "
                        "from `results/esg_records.json` are included above."
                    )
                    if st.button("Persist live model summary into model_stability_summary.csv", key="persist_live_model_stability"):
                        migrated = migrate_live_reprocess_outputs(silver_base, pd.DataFrame(), model_stab_static, model_stab_live)
                        st.success(f"Saved {migrated['model_rows']:,} model summary row(s) -> {MODEL_STAB_PATH.name}")
                        st.rerun()
            else:
                st.info("No model stability summary found.")

        with right:
            st.markdown("#### Prompt stability (existing data)")
            if not prompt_stab.empty:
                show_cols = [c for c in ["prompt", "runs", "json_parse_success_rate", "missing_tone_rate", "schema_drift_rate"] if c in prompt_stab.columns]
                st.dataframe(prompt_stab[show_cols], use_container_width=True, height=300)
                if "missing_tone_rate" in prompt_stab.columns:
                    worst = prompt_stab.loc[prompt_stab["missing_tone_rate"].idxmax()]
                    st.warning(f"Highest missing-tone rate: **{worst['prompt']}** ({float(worst['missing_tone_rate']):.1%})")
            else:
                st.info("No prompt stability summary found.")

        st.markdown("#### PDF × prompt processing matrix")
        prompt_pdf_records = load_llm_records()
        if prompt_pdf_records.empty or not {"target_doc", "prompt", "records_count"}.issubset(prompt_pdf_records.columns):
            st.info("No PDF × prompt processing records found yet. Run LLM processing or generate `results/visualizations/tone_records_flat.csv`.")
        else:
            matrix_metric = st.radio(
                "Cell value",
                ["Extracted records", "Runs / batches", "Successful runs"],
                horizontal=True,
                key="prompt_pdf_matrix_metric",
            )
            matrix_df = prompt_pdf_records.copy()
            matrix_df["target_doc"] = matrix_df["target_doc"].astype(str).replace("", "unknown")
            matrix_df["prompt"] = matrix_df["prompt"].astype(str).replace("", "unknown")
            matrix_df["ok"] = matrix_df["ok"].fillna(False).astype(bool) if "ok" in matrix_df.columns else True

            if matrix_metric == "Runs / batches":
                grouped = matrix_df.groupby(["target_doc", "prompt"], dropna=False).size().reset_index(name="value")
            elif matrix_metric == "Successful runs":
                grouped = (
                    matrix_df[matrix_df["ok"]]
                    .groupby(["target_doc", "prompt"], dropna=False)
                    .size()
                    .reset_index(name="value")
                )
            else:
                grouped = (
                    matrix_df.groupby(["target_doc", "prompt"], dropna=False)["records_count"]
                    .sum()
                    .reset_index(name="value")
                )

            if grouped.empty:
                st.info("No matching PDF × prompt rows after filtering successful records.")
            else:
                pivot = (
                    grouped.pivot_table(index="target_doc", columns="prompt", values="value", aggfunc="sum", fill_value=0)
                    .sort_index()
                    .astype(int)
                )
                pivot.insert(0, "total", pivot.sum(axis=1))
                st.dataframe(pivot, use_container_width=True, height=360)
                st.download_button(
                    "Download PDF × prompt matrix CSV",
                    pivot.reset_index().to_csv(index=False).encode("utf-8"),
                    "pdf_prompt_processing_matrix.csv",
                    "text/csv",
                    use_container_width=True,
                )

                heatmap = alt.Chart(grouped).mark_rect().encode(
                    x=alt.X("prompt:N", title="Prompt", axis=alt.Axis(labelAngle=-35, labelLimit=220)),
                    y=alt.Y("target_doc:N", title="PDF / processed document", sort="-x", axis=alt.Axis(labelLimit=260)),
                    color=alt.Color("value:Q", title=matrix_metric, scale=alt.Scale(scheme="tealblues")),
                    tooltip=["target_doc", "prompt", "value"],
                ).properties(height=min(520, max(260, 24 * grouped["target_doc"].nunique())))
                st.altair_chart(heatmap, use_container_width=True)

    st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 5 — Failure mode tagging
# ═════════════════════════════════════════════════════════════════════════════
if show[5]:
    modes_quantified = len(fail_cnt["mode"].unique()) if not fail_cnt.empty and "mode" in fail_cnt.columns else 0
    badge = "✅" if modes_quantified >= 10 else ("🟡" if modes_quantified > 0 else "🔴")
    with st.expander(f"{badge} Step 5 — Quantify failure rates on 100-record sample  ·  ~2 h", expanded=modes_quantified < 10):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.info(
                "**The taxonomy is done (10 modes).** You just need counts.\n\n"
                "Pick a fixed 100-record sample, tag each record with which failure mode(s) apply, "
                "and this produces the quantitative table for Section 4.4.2."
            )
            st.markdown("#### Tag failure modes on a record")
            if not silver.empty:
                record_ids = silver["record_id"].tolist() if "record_id" in silver.columns else []
                sel_id = st.selectbox("Pick a record to tag", record_ids, key="fm_record_sel")
                if sel_id:
                    row = silver[silver["record_id"] == sel_id].iloc[0]
                    if "text" in row:
                        st.text_area("Text", value=str(row["text"]), height=120, disabled=True, key="fm_text")
                    if "tone_pred" in row:
                        st.caption(f"LLM tone: **{row['tone_pred']}** · company: {row.get('company', '')} · lang: {row.get('language', '')}")

                    selected_modes = st.multiselect("Failure modes present in this record", FAILURE_MODES, key="fm_modes")
                    notes_val = st.text_input("Optional note", key="fm_notes")
                    if st.button("Save failure mode tag", type="primary", key="fm_save"):
                        new_row = {"record_id": sel_id, "failure_modes": "|".join(selected_modes), "notes": notes_val}
                        existing = load(FAILURE_PATH)
                        if not existing.empty and sel_id in existing["record_id"].values:
                            existing.loc[existing["record_id"] == sel_id, "failure_modes"] = "|".join(selected_modes)
                        else:
                            existing = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
                        existing.to_csv(FAILURE_PATH, index=False)
                        st.success(f"Saved failure tag for {sel_id}")
                        st.rerun()

        with right:
            st.markdown("#### Failure mode counts (existing)")
            if not fail_cnt.empty:
                st.dataframe(fail_cnt, use_container_width=True, height=260)
                if "mode" in fail_cnt.columns and "count" in fail_cnt.columns:
                    agg = fail_cnt.groupby("mode")["count"].sum().reset_index().sort_values("count", ascending=False)
                    bar = alt.Chart(agg).mark_bar(color="#BA7517").encode(
                        x=alt.X("count:Q", title="Count"),
                        y=alt.Y("mode:N", sort="-x", title=None),
                        tooltip=["mode", "count"],
                    ).properties(height=220)
                    st.altair_chart(bar, use_container_width=True)
            else:
                st.info("No failure mode counts yet. Tag records on the left to build this table.")
            st.metric("Modes quantified", f"{modes_quantified} / 10")

            st.markdown("#### Records already tagged")
            tagged = load(FAILURE_PATH)
            if not tagged.empty and "failure_modes" in tagged.columns:
                n_tagged = tagged["failure_modes"].astype(str).str.strip().ne("").sum()
                st.metric("Records tagged", f"{n_tagged} / 100 target")
            else:
                st.metric("Records tagged", "0 / 100 target")

    st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 6 — Aspect clustering
# ═════════════════════════════════════════════════════════════════════════════
if show[6]:
    clusters_saved = load(CLUSTER_PATH)
    n_clustered = len(clusters_saved) if not clusters_saved.empty else 0
    n_unmapped   = len(ontology[~ontology["mapped_to_ontology"].astype(str).str.lower().isin(["true", "1", "yes"])]) if not ontology.empty and "mapped_to_ontology" in ontology.columns else 46
    badge = "✅" if n_clustered >= n_unmapped else ("🟡" if n_clustered > 0 else "🔴")

    with st.expander(f"{badge} Step 6 — Map 46 unmapped aspects to semantic clusters  ·  ~2 h", expanded=n_clustered < n_unmapped):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.info(
                "**Reframe a gap as a contribution.** The 46 aspects not in GRI/SASB ontology are not a "
                "failure — they are Indonesian-specific ESG vocabulary your pipeline discovered.\n\n"
                "Group them into 5–8 semantic clusters (e.g. *Community Relations*, "
                "*Regulatory Compliance*, *Supply Chain*). This becomes a novel contribution in Section 4.4.3."
            )
            if not ontology.empty:
                st.markdown("#### Map ontology coverage")
                ontology_review = ontology.copy()
                if "suggested_path" not in ontology_review.columns:
                    ontology_review["suggested_path"] = ""
                if "mapped_to_ontology" not in ontology_review.columns:
                    ontology_review["mapped_to_ontology"] = False
                ontology_review["auto_suggested_path"] = ontology_review["aspect"].map(suggest_ontology_path)
                map_view = st.radio(
                    "Ontology rows to show",
                    ["Unmapped only", "All ontology rows"],
                    horizontal=True,
                    key="ontology_mapping_view",
                )
                mapped_bool = ontology_review["mapped_to_ontology"].astype(str).str.lower().isin(["true", "1", "yes"])
                ontology_visible = ontology_review[~mapped_bool].copy() if map_view == "Unmapped only" else ontology_review.copy()
                st.caption(
                    "Set `mapped_to_ontology` to true and fill `suggested_path`. "
                    "`auto_suggested_path` is a starting point for GRI/SASB-style mapping."
                )
                ontology_edit_cols = [c for c in ["aspect", "records", "mapped_to_ontology", "suggested_path", "auto_suggested_path"] if c in ontology_visible.columns]
                edited_ontology = st.data_editor(
                    ontology_visible[ontology_edit_cols],
                    column_config={
                        "aspect": st.column_config.TextColumn("aspect", disabled=True, width="large"),
                        "records": st.column_config.NumberColumn("records", disabled=True, width="small"),
                        "mapped_to_ontology": st.column_config.CheckboxColumn("mapped_to_ontology"),
                        "suggested_path": st.column_config.TextColumn("suggested_path", width="large"),
                        "auto_suggested_path": st.column_config.TextColumn("auto_suggested_path", disabled=True, width="large"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=320,
                    key="ontology_mapping_editor",
                )
                map_cols = st.columns(2)
                with map_cols[0]:
                    if st.button("Save ontology mapping edits", type="primary", use_container_width=True, key="save_ontology_mapping"):
                        base = ontology.copy()
                        base = base.set_index("aspect", drop=False)
                        upd = edited_ontology.set_index("aspect", drop=False)
                        shared = base.index.intersection(upd.index)
                        for col in ["mapped_to_ontology", "suggested_path"]:
                            if col in upd.columns:
                                base.loc[shared, col] = upd.loc[shared, col]
                        base.reset_index(drop=True).to_csv(ONTOLOGY_PATH, index=False)
                        st.success(f"Saved ontology mapping edits → {ONTOLOGY_PATH.name}")
                        st.rerun()
                with map_cols[1]:
                    if st.button("Auto-map rows with suggested paths", use_container_width=True, key="auto_map_ontology"):
                        base = ontology_review.copy()
                        base["suggested_path"] = base["suggested_path"].astype(str)
                        empty_path = base["suggested_path"].str.strip().eq("")
                        base.loc[empty_path, "suggested_path"] = base.loc[empty_path, "auto_suggested_path"]
                        has_path = base["suggested_path"].astype(str).str.strip().ne("")
                        base.loc[has_path, "mapped_to_ontology"] = True
                        base[[c for c in ["aspect", "records", "mapped_to_ontology", "suggested_path"] if c in base.columns]].to_csv(ONTOLOGY_PATH, index=False)
                        st.success("Auto-mapped rows with suggested ontology paths.")
                        st.rerun()

                unmapped_mask = ~ontology["mapped_to_ontology"].astype(str).str.lower().isin(["true", "1", "yes"]) if "mapped_to_ontology" in ontology.columns else pd.Series([True] * len(ontology))
                unmapped = ontology[unmapped_mask].copy()
                st.markdown(f"#### {len(unmapped)} unmapped aspects — assign clusters")
                if not unmapped.empty:
                    display_cols = [c for c in ["aspect", "records", "suggested_path"] if c in unmapped.columns]
                    review = unmapped[display_cols].copy()
                    review["suggested_cluster"] = review["aspect"].map(suggest_aspect_cluster)
                    if not clusters_saved.empty and "aspect" in clusters_saved.columns and "cluster" in clusters_saved.columns:
                        saved_map = clusters_saved.drop_duplicates("aspect", keep="last").set_index("aspect")["cluster"].to_dict()
                        review["cluster"] = review["aspect"].map(saved_map).fillna(review["suggested_cluster"])
                    else:
                        review["cluster"] = review["suggested_cluster"]
                    cluster_view = st.radio(
                        "Rows to show",
                        ["Needs review", "All unmapped aspects", "Auto-suggested only"],
                        horizontal=True,
                        key="cluster_rows_to_show",
                    )
                    if cluster_view == "Needs review":
                        visible_clusters = review[
                            review["cluster"].astype(str).str.strip().eq("")
                            | review["cluster"].eq("Other")
                            | review["aspect"].astype(str).str.lower().isin(["missing", "none"])
                        ].copy()
                    elif cluster_view == "Auto-suggested only":
                        visible_clusters = review[review["cluster"].eq(review["suggested_cluster"])].copy()
                    else:
                        visible_clusters = review.copy()
                    st.caption(
                        f"Showing {len(visible_clusters):,} of {len(review):,} unmapped aspects. "
                        "Use `suggested_cluster` as a starting point, then adjust `cluster` where needed."
                    )
                    edited_clusters = st.data_editor(
                        visible_clusters,
                        column_config={
                            "cluster": st.column_config.SelectboxColumn("cluster", options=[""] + CLUSTER_NAMES, width="medium"),
                            "suggested_cluster": st.column_config.TextColumn("suggested_cluster", disabled=True, width="medium"),
                            "aspect": st.column_config.TextColumn("aspect", disabled=True, width="large"),
                            "records": st.column_config.NumberColumn("records", disabled=True, width="small"),
                            "suggested_path": st.column_config.TextColumn("suggested_path", disabled=True, width="medium"),
                        },
                        use_container_width=True,
                        hide_index=True,
                        height=430,
                        key="cluster_editor",
                    )
                    csave1, csave2 = st.columns(2)
                    with csave1:
                        save_clicked = st.button("Save visible cluster assignments", type="primary", key="save_clusters", use_container_width=True)
                    with csave2:
                        auto_save_clicked = st.button("Auto-save suggested clusters for all unmapped", key="auto_save_clusters", use_container_width=True)
                    if save_clicked:
                        assigned = edited_clusters[edited_clusters["cluster"].astype(str).str.strip().ne("")]
                        existing_c = load(CLUSTER_PATH)
                        combined = pd.concat([existing_c, assigned], ignore_index=True).drop_duplicates(subset=["aspect"], keep="last")
                        combined.to_csv(CLUSTER_PATH, index=False)
                        st.success(f"Saved {len(assigned)} cluster assignments → {CLUSTER_PATH.name}")
                        st.rerun()
                    if auto_save_clicked:
                        assigned = review.copy()
                        assigned["cluster"] = assigned["suggested_cluster"]
                        existing_c = load(CLUSTER_PATH)
                        combined = pd.concat([existing_c, assigned], ignore_index=True).drop_duplicates(subset=["aspect"], keep="last")
                        combined.to_csv(CLUSTER_PATH, index=False)
                        st.success(f"Auto-saved {len(assigned)} suggested cluster assignments → {CLUSTER_PATH.name}")
                        st.rerun()
            else:
                st.info(f"ontology_coverage.csv not found at {ONTOLOGY_PATH}")
                st.markdown("Open `1_6_Ontology_Path_Viewer.py` from the Streamlit sidebar.")

        with right:
            st.markdown("#### Ontology coverage")
            if not ontology.empty and "mapped_to_ontology" in ontology.columns:
                mapped_n = ontology["mapped_to_ontology"].astype(str).str.lower().isin(["true", "1", "yes"]).sum()
                total_n  = len(ontology)
                st.metric("Mapped to GRI/SASB", f"{mapped_n} / {total_n}")
                st.progress(mapped_n / total_n if total_n else 0)
                st.metric("Novel (unmapped) aspects", f"{total_n - mapped_n}")
                st.caption("These novel aspects are your contribution — frame them as the Indonesian ESG vocabulary extension.")

            st.metric("Clusters assigned so far", f"{n_clustered} / {n_unmapped}")
            if n_clustered > 0 and not clusters_saved.empty and "cluster" in clusters_saved.columns:
                cc = clusters_saved["cluster"].value_counts().reset_index()
                cc.columns = ["cluster", "count"]
                bar2 = alt.Chart(cc).mark_bar(color="#1D9E75").encode(
                    x=alt.X("count:Q", title="Aspects"),
                    y=alt.Y("cluster:N", sort="-x", title=None),
                    tooltip=["cluster", "count"],
                ).properties(height=220)
                st.altair_chart(bar2, use_container_width=True)
                top_share = float(cc["count"].max() / cc["count"].sum()) if cc["count"].sum() else 0.0
                if top_share > 0.65 and len(cc) > 1:
                    st.warning(
                        "One cluster dominates the assignments. Review Step 6 with the suggested clusters so the vocabulary extension is more defensible."
                    )
                elif len(cc) == 1 and n_clustered > 5:
                    st.warning(
                        "All assignments are in one cluster. Use the auto-suggested clusters or split them into 5-8 semantic groups before using this in the thesis."
                    )
            else:
                st.info("Cluster assignments will appear here once you save some.")

            if not ontology.empty:
                st.markdown("#### All aspects overview")
                st.dataframe(ontology[[c for c in ["aspect", "records", "mapped_to_ontology"] if c in ontology.columns]],
                             use_container_width=True, height=260)

# ═════════════════════════════════════════════════════════════════════════════
# PDF × PROMPT PROCESSING MATRIX
# ═════════════════════════════════════════════════════════════════════════════
if show.get("matrix", True):
    st.divider()

    METRIC_CONFIG = {
        "record_count":        ("Records extracted",      "YlGn",    False, "{:.0f}"),
        "field_completion_rate": ("Field completion rate", "YlGn",    False, "{:.1%}"),
        "missing_tone_rate":   ("Missing tone rate",       "RdYlGn_r", True,  "{:.1%}"),
        "schema_drift_rate":   ("Schema drift rate",       "RdYlGn_r", True,  "{:.1%}"),
    }

    df_run = load(PROMPT_BY_RUN_PATH)

    run_badge = "✅" if not df_run.empty else "🔴"
    with st.expander(
        f"{run_badge} PDF × Prompt Processing Matrix — LLM output coverage",
        expanded=not df_run.empty,
    ):
        if df_run.empty:
            st.warning(
                f"No data found at `{PROMPT_BY_RUN_PATH.name}`. "
                "Run the LLM processing pipeline to populate this table."
            )
        else:
            # ── controls ────────────────────────────────────────────────────
            ctrl_left, ctrl_right = st.columns([2, 2])
            with ctrl_left:
                sel_metric = st.selectbox(
                    "Metric shown in each cell",
                    list(METRIC_CONFIG.keys()),
                    format_func=lambda k: METRIC_CONFIG[k][0],
                    key="ppm_metric",
                )
            with ctrl_right:
                row_col_choice = st.radio(
                    "Row identifier",
                    ["company", "target"],
                    horizontal=True,
                    key="ppm_row_col",
                    help="'company' is shorter; 'target' shows the exact batch path.",
                )
                row_col = row_col_choice if row_col_choice in df_run.columns else (
                    "company" if "company" in df_run.columns else "target"
                )

            metric_label, cmap, lower_is_better, fmt_str = METRIC_CONFIG[sel_metric]
            is_count = sel_metric == "record_count"
            is_rate  = sel_metric in ("field_completion_rate", "missing_tone_rate", "schema_drift_rate")

            # ── build pivot ─────────────────────────────────────────────────
            agg = (
                df_run.groupby([row_col, "prompt"])[sel_metric]
                .mean()
                .reset_index(name=sel_metric)
            )
            pivot = (
                agg.pivot(index=row_col, columns="prompt", values=sel_metric)
                .fillna(0)
            )
            # Shorten prompt names
            pivot.columns = [
                str(c).replace(".md", "").replace("tone_", "")
                for c in pivot.columns
            ]
            pivot.columns.name = None
            pivot.index.name = row_col

            if is_count:
                pivot = pivot.round(0).astype(int)
                summary_col = "TOTAL"
                pivot[summary_col] = pivot.sum(axis=1)
                pivot = pivot.sort_values(summary_col, ascending=False)
            else:
                pivot = pivot.round(4)
                summary_col = "AVG"
                pivot[summary_col] = pivot.mean(axis=1).round(4)
                pivot = pivot.sort_values(summary_col, ascending=lower_is_better)

            df_pivot = pivot.reset_index()
            val_cols = list(df_pivot.columns[1:])          # all except row label
            prompt_cols = [c for c in val_cols if c != summary_col]

            # ── layout: table left, stats right ─────────────────────────────
            tbl_col, stat_col = st.columns([3, 1], gap="large")

            with tbl_col:
                st.markdown(f"**{metric_label}** per PDF × prompt template")
                try:
                    fmt_map = {c: fmt_str for c in val_cols}
                    styled = (
                        df_pivot.style
                        .background_gradient(subset=val_cols, cmap=cmap)
                        .format(fmt_map)
                        .set_properties(**{"font-size": "12px"})
                    )
                    tbl_height = min(max(300, len(df_pivot) * 38 + 60), 700)
                    st.dataframe(styled, use_container_width=True, hide_index=True, height=tbl_height)
                except Exception:
                    st.dataframe(df_pivot.astype(str), use_container_width=True, hide_index=True)

                st.caption(
                    f"{len(df_pivot)} PDFs/companies  ·  "
                    f"{len(prompt_cols)} prompt templates  ·  "
                    f"Metric: **{metric_label}**  ·  "
                    f"{'Higher = more records' if is_count else ('Higher = better' if not lower_is_better else 'Lower = better')}  ·  "
                    f"Source: `{PROMPT_BY_RUN_PATH.name}`"
                )
                st.download_button(
                    f"⬇ Download PDF × Prompt {metric_label} CSV",
                    df_pivot.to_csv(index=False).encode("utf-8"),
                    f"pdf_prompt_{sel_metric}_matrix.csv",
                    "text/csv",
                    use_container_width=True,
                    key="ppm_download",
                )

            with stat_col:
                st.markdown("**Coverage summary**")

                # Overall coverage: how many (PDF, prompt) cells have data
                total_cells = len(df_pivot) * len(prompt_cols)
                filled_cells = sum(
                    (pd.to_numeric(df_pivot[c], errors="coerce").fillna(0) > 0).sum()
                    for c in prompt_cols
                )
                coverage_pct = filled_cells / total_cells if total_cells else 0
                st.metric("Cells with data", f"{filled_cells} / {total_cells}")
                st.progress(coverage_pct)

                st.divider()

                # Per-prompt averages
                st.markdown("**By prompt** (avg across PDFs)")
                prompt_avgs = []
                for pc in prompt_cols:
                    col_vals = pd.to_numeric(df_pivot[pc], errors="coerce").fillna(0)
                    prompt_avgs.append({
                        "prompt": pc,
                        "avg": round(float(col_vals.mean()), 4),
                        "nonzero": int((col_vals > 0).sum()),
                    })
                df_pavg = pd.DataFrame(prompt_avgs).sort_values(
                    "avg", ascending=lower_is_better
                )
                bar_prompt = (
                    alt.Chart(df_pavg)
                    .mark_bar()
                    .encode(
                        x=alt.X("avg:Q", title=metric_label),
                        y=alt.Y("prompt:N", sort=None, title=None),
                        color=alt.Color(
                            "avg:Q",
                            scale=alt.Scale(scheme="tealblues"),
                            legend=None,
                        ),
                        tooltip=[
                            alt.Tooltip("prompt:N"),
                            alt.Tooltip("avg:Q", format=".3f", title=metric_label),
                            alt.Tooltip("nonzero:Q", title="PDFs with data"),
                        ],
                    )
                    .properties(height=max(160, len(df_pavg) * 28))
                )
                st.altair_chart(bar_prompt, use_container_width=True)

                st.divider()
                st.markdown("**By PDF** (avg across prompts)")
                pdf_avgs = df_pivot[[row_col, summary_col]].copy()
                pdf_avgs[summary_col] = pd.to_numeric(pdf_avgs[summary_col], errors="coerce").fillna(0)
                bar_pdf = (
                    alt.Chart(pdf_avgs)
                    .mark_bar(color="#2f6f73")
                    .encode(
                        x=alt.X(f"{summary_col}:Q", title=summary_col),
                        y=alt.Y(f"{row_col}:N", sort="-x", title=None),
                        tooltip=[row_col, summary_col],
                    )
                    .properties(height=max(160, len(pdf_avgs) * 26))
                )
                st.altair_chart(bar_pdf, use_container_width=True)

            # ── raw data drill-down ──────────────────────────────────────────
            with st.expander("Raw run-level data (prompt_stability_by_run.csv)", expanded=False):
                filter_cols = [c for c in [row_col, "prompt", "model", "run_idx",
                                           "record_count", "field_completion_rate",
                                           "missing_tone_rate", "schema_drift_rate", "ok"]
                               if c in df_run.columns]
                company_filter = st.multiselect(
                    "Filter by PDF/company",
                    sorted(df_run[row_col].dropna().unique().tolist()),
                    key="ppm_company_filter",
                )
                prompt_filter = st.multiselect(
                    "Filter by prompt",
                    sorted(df_run["prompt"].dropna().unique().tolist()) if "prompt" in df_run.columns else [],
                    key="ppm_prompt_filter",
                )
                raw_view = df_run[filter_cols].copy()
                if company_filter:
                    raw_view = raw_view[raw_view[row_col].isin(company_filter)]
                if prompt_filter:
                    raw_view = raw_view[raw_view["prompt"].isin(prompt_filter)]
                st.dataframe(raw_view, use_container_width=True, hide_index=True, height=320)
                st.download_button(
                    "⬇ Download filtered raw runs CSV",
                    raw_view.to_csv(index=False).encode("utf-8"),
                    "pdf_prompt_raw_runs.csv",
                    "text/csv",
                    use_container_width=True,
                    key="ppm_raw_download",
                )
