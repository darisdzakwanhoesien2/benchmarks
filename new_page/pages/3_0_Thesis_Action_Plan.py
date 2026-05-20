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

st.set_page_config(page_title="Thesis Action Plan", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "results" / "revision_analysis"
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
CLUSTER_PATH           = ARTIFACTS / "aspect_clusters.csv"
PROMPT_BY_RUN_PATH     = ARTIFACTS / "prompt_stability_by_run.csv"
NOTES_PATH             = PAGES_DIR / "notes.md"
ANNOTATION_TARGET = 250

TONE_OPTS   = ["", "commitment", "action", "outcome", "none", "unknown"]
ESG_OPTS    = ["", "e", "s", "g", "e-s", "e-g", "s-g", "e-s-g", "none", "unknown"]
STATUS_OPTS = ["needs_review", "reviewed", "uncertain", "discard"]

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


def suggest_aspect_cluster(aspect):
    text = str(aspect or "").lower()
    rules = [
        ("Governance & Ethics", ["korupsi", "antikorupsi", "anti korupsi", "etik", "governance", "komisaris", "direksi", "kepatuhan", "compliance", "gratifikasi", "conflict", "konflik kepentingan"]),
        ("Energy & Climate", ["climate", "karbon", "emisi", "netzero", "net zero", "energi", "energy", "scope", "ghg", "iklim", "renewable"]),
        ("Waste & Pollution", ["limbah", "waste", "pollution", "polusi", "air limbah", "b3", "sampah", "emission", "water", "air"]),
        ("Human Capital", ["karyawan", "employee", "pelatihan", "training", "keselamatan", "k3", "human", "tenaga kerja", "labor", "pekerja"]),
        ("Community Relations", ["masyarakat", "community", "komunitas", "sosial", "csr", "pemberdayaan", "pendidikan", "donasi", "stakeholder"]),
        ("Supply Chain", ["vendor", "supplier", "rantai pasok", "supply", "procurement", "pemasok"]),
        ("Financial Sustainability", ["financial", "keuangan", "investasi", "economic", "ekonomi", "profit", "revenue"]),
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

tone_done    = ann_n(annot, "ground_truth_tone")
esg_done     = ann_n(annot, "ground_truth_esg")
aspect_done  = ann_n(annot, "ground_truth_aspect")
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
    ("Tone labels",       f"{tone_done}/{ANNOTATION_TARGET}",   tone_done >= ANNOTATION_TARGET),
    ("ESG labels",        f"{esg_done}/{ANNOTATION_TARGET}",    esg_done >= ANNOTATION_TARGET),
    ("Aspect labels",     f"{aspect_done}/{ANNOTATION_TARGET}", aspect_done >= ANNOTATION_TARGET),
    ("OCR pages sampled", "0/100",              False),
    ("Models tested",     f"{n_models}/3+",     n_models >= 3),
]):
    col.metric(label, val, delta="✓ Done" if ok else "Needed",
               delta_color="normal" if ok else "inverse")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# STEP 1 — ClimateBERT
# ═════════════════════════════════════════════════════════════════════════════
if show[1]:
    badge = "✅" if cb_real == 332 else ("🟡" if cb_real > 0 else "🔴")
    with st.expander(f"{badge} Step 1 — Run ClimateBERT on all 332 records  ·  ~2 h", expanded=cb_real < 332):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.markdown("#### What is ClimateBERT and what does 'run' mean?")
            st.info(
                "**ClimateBERT** is a pre-trained AI model (a fine-tuned RoBERTa) that reads a "
                "sentence and answers one question: *is this a climate-commitment statement or not?*\n\n"
                "Right now your κ = 0.645 is based on **proxy labels** — labels your own LLM pipeline "
                "generated as a stand-in. To make RQ3 publication-ready, you need to run the real "
                "ClimateBERT model on all 332 records and import those outputs here.\n\n"
                "**It takes about 10 minutes on a laptop CPU or 2 minutes on free Google Colab GPU.**"
            )

            st.markdown("#### Step-by-step")
            st.markdown(
                "1. **Download** the 332-record batch input CSV below.\n"
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
                    base = annot.set_index("record_id")
                    upd  = normalise_annotation_values(edited).set_index("record_id")
                    for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect",
                                "review_status", "annotator", "review_notes"]:
                        if col in upd.columns:
                            base.loc[upd.index, col] = upd[col]
                    if "ground_truth_esg" in base.columns:
                        base["ground_truth_esg"] = base["ground_truth_esg"].map(normalise_esg_value)
                    base.reset_index().to_csv(ANNOTATION_PATH, index=False)
                    st.success(f"Saved → {ANNOTATION_PATH.name}")
                    st.rerun()

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
            pivot.index.name = "PDF / Company"

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
