from io import StringIO
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Thesis Action Plan", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
PAGES_DIR = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "results" / "revision_analysis"
CLIMATEBERT_JOBS = ROOT / "results" / "climatebert_background_jobs"
CLIMATEBERT_WORKER = ROOT / "code" / "climatebert_background_worker.py"
ROOT_MODELS_DIR = ROOT.parent / "model_download" / "models"

SILVER_PATH       = ARTIFACTS / "silver_tone_ground_truth.csv"
ANNOTATION_PATH   = ARTIFACTS / "pilot_ground_truth_annotations.csv"
SEED_PATH         = ARTIFACTS / "pilot_ground_truth_seed.csv"
PROXY_PATH        = ARTIFACTS / "climatebert_proxy_agreement_records.csv"
IMPORTED_PATH     = ARTIFACTS / "climatebert_record_batch_import.csv"
ONTOLOGY_PATH     = ARTIFACTS / "ontology_coverage.csv"
PROMPT_STAB_PATH  = ARTIFACTS / "prompt_stability_summary.csv"
MODEL_STAB_PATH   = ARTIFACTS / "model_stability_summary.csv"
OCR_PATH          = ARTIFACTS / "ocr_processing_summary.csv"
FAILURE_PATH      = ARTIFACTS / "failure_modes.csv"
FAIL_CNT_PATH     = ARTIFACTS / "failure_mode_counts.csv"
CLUSTER_PATH      = ARTIFACTS / "aspect_clusters.csv"
NOTES_PATH        = PAGES_DIR / "notes.md"

TONE_OPTS   = ["", "commitment", "action", "outcome", "none", "unknown"]
ESG_OPTS    = ["", "e", "s", "g", "e-s", "e-g", "s-g", "e-s-g", "none", "unknown"]
STATUS_OPTS = ["needs_review", "reviewed", "uncertain", "discard"]

FAILURE_MODES = [
    "Bilingual code-switching", "Hedged modal verb", "Table / numeric data loss",
    "Scanned page / low OCR quality", "Generic boilerplate statement", "Diacritics error",
    "Missing required schema field", "Schema drift", "Empty / truncated text",
    "Multiple aspects merged into one",
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


# ── Load data ─────────────────────────────────────────────────────────────────
silver     = load(SILVER_PATH)
annot_raw  = load(ANNOTATION_PATH) if ANNOTATION_PATH.exists() else load(SEED_PATH)
annot      = normalise_annotation_values(annot_raw.copy())
proxy      = load(PROXY_PATH)
imported   = load(IMPORTED_PATH)
ontology   = load(ONTOLOGY_PATH)
prompt_stab = load(PROMPT_STAB_PATH)
model_stab  = load(MODEL_STAB_PATH)
ocr_df      = load(OCR_PATH)
fail_df     = load(FAILURE_PATH)
fail_cnt    = load(FAIL_CNT_PATH)

tone_done    = ann_n(annot, "ground_truth_tone")
esg_done     = ann_n(annot, "ground_truth_esg")
aspect_done  = ann_n(annot, "ground_truth_aspect")
cb_real      = nonempty_count(imported, "climatebert_commitment_pred") if not imported.empty else 0
n_models     = len(model_stab) if not model_stab.empty else 0
cb_target_total = len(silver) if not silver.empty else 332

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

for col, (label, val, ok) in zip(st.columns(6), [
    ("ClimateBERT real",  f"{cb_real}/{cb_target_total}",    cb_real >= cb_target_total),
    ("Tone labels",       f"{tone_done}/150",   tone_done >= 150),
    ("ESG labels",        f"{esg_done}/150",    esg_done >= 150),
    ("Aspect labels",     f"{aspect_done}/150", aspect_done >= 150),
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
                "This writes directly to `results/revision_analysis/climatebert_record_batch_import.csv`, "
                "so the output is integrated into the same real ClimateBERT result slot as the uploader below."
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
            if st.button("Start Step 1 ClimateBERT background run", type="primary", use_container_width=True, key="start_cb_bg"):
                job_id = f"climatebert_step1_{utc_now_id()}_{uuid.uuid4().hex[:6]}"
                job_dir = CLIMATEBERT_JOBS / job_id
                config = {
                    "job_id": job_id,
                    "model_backend": cb_model_backend,
                    "model_id": cb_model_id,
                    "local_model_path": cb_local_path,
                    "limit": int(cb_limit),
                    "max_chars": int(cb_max_chars),
                    "skip_existing": bool(cb_skip_existing),
                    "dry_run": bool(cb_dry_run),
                    "text_col": "text",
                    "record_col": "record_id",
                    "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                }
                write_json(job_dir / "config.json", config)
                write_json(job_dir / "control.json", {"stop_requested": False})
                write_json(
                    job_dir / "status.json",
                    {
                        "job_id": job_id,
                        "status": "queued",
                        "total": int(cb_limit) if int(cb_limit) else len(silver),
                        "completed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "current": "Queued",
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
                s1, s2, s3, s4 = st.columns(4)
                s1.metric("Status", cb_status.get("status", "unknown"))
                s2.metric("Failed", int(cb_status.get("failed") or 0))
                s3.metric("Skipped", int(cb_status.get("skipped") or 0))
                s4.metric("PID", cb_status.get("pid") or "None", delta="alive" if is_alive(cb_status.get("pid")) else "not running")
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
                        df_up["climatebert_commitment_pred"] = df_up[lcol].astype(str).str.lower().isin(
                            ["yes", "true", "1", "commitment", "climate-commitment"]
                        )
                        if not silver.empty:
                            merged = silver.merge(df_up[["record_id", "climatebert_commitment_pred", lcol]], on="record_id", how="left")
                        else:
                            merged = df_up
                        merged.to_csv(IMPORTED_PATH, index=False)
                        st.success(f"Saved {len(merged)} records → {IMPORTED_PATH.name}")
                        imported = merged

        with right:
            st.markdown("#### Current status")
            st.metric("Real ClimateBERT records", f"{cb_real} / {cb_target_total}", delta="✓ Done" if cb_real >= cb_target_total else "Not yet")
            st.progress(
                min(cb_real / cb_target_total, 1.0) if cb_target_total else 0.0,
                text=f"Imported ClimateBERT output progress: {cb_real}/{cb_target_total} records",
            )

            cb_jobs_for_status = climatebert_jobs()
            if cb_jobs_for_status:
                latest_status = read_json(CLIMATEBERT_JOBS / cb_jobs_for_status[0] / "status.json", {})
                latest_total = int(latest_status.get("total") or 0)
                latest_completed = int(latest_status.get("completed") or 0)
                st.caption(f"Latest background job: `{cb_jobs_for_status[0]}`")
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
    all_done = tone_done >= 150 and esg_done >= 150 and aspect_done >= 150
    badge = "✅" if all_done else ("🟡" if tone_done > 0 else "🔴")
    with st.expander(f"{badge} Step 2 — Complete pilot annotation to 150 records  ·  ~1 week", expanded=not all_done):

        left, right = st.columns([3, 2], gap="large")

        with left:
            st.markdown("#### What you need to annotate")
            st.info(
                "For each of the 150 pilot records, fill in **4 fields**:\n\n"
                "| Field | Values | What it means |\n"
                "|---|---|---|\n"
                "| `ground_truth_tone` | commitment / action / outcome / none / unknown | The disclosure maturity level |\n"
                "| `ground_truth_esg` | e / s / g / e-s / e-g / s-g / e-s-g / none / unknown | One or more ESG pillars |\n"
                "| `ground_truth_aspect` | free text | The specific ESG topic (e.g. *carbon emissions*, *water usage*) |\n"
                "| `review_status` | reviewed / uncertain / discard | Your confidence in this row |\n\n"
                "**Also needed for κ:** A second annotator labels the same 150 records independently. "
                "You then compute Cohen's κ between the two sets."
            )

            st.caption("Multi-pillar ESG values are accepted. You can paste `e-s`, `e/g`, `E, S`, `environmental-social`, or `e-s-g`; they are normalized to `e-s`, `e-g`, `s-g`, or `e-s-g`.")

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
                                save_path = ANNOTATION_PATH if ANNOTATION_PATH.exists() else SEED_PATH
                                base = normalise_annotation_values(pd.read_csv(save_path).fillna("")) if save_path.exists() else annot.copy()
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
                edit_cols = [c for c in ["record_id", "text", "tone_pred", "ground_truth_tone",
                                         "ground_truth_esg", "ground_truth_aspect", "review_status",
                                         "annotator", "review_notes"] if c in annot.columns]
                col_cfg = {
                    "ground_truth_tone":   st.column_config.SelectboxColumn("ground_truth_tone",   options=TONE_OPTS),
                    "ground_truth_esg":    st.column_config.SelectboxColumn("ground_truth_esg",    options=ESG_OPTS),
                    "review_status":       st.column_config.SelectboxColumn("review_status",       options=STATUS_OPTS),
                    "text":                st.column_config.TextColumn("text", width="large"),
                }
                edited = st.data_editor(annot[edit_cols], use_container_width=True, height=380,
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
                ("Tone labels (ground_truth_tone)",     tone_done,   150),
                ("ESG labels (ground_truth_esg)",       esg_done,    150),
                ("Aspect labels (ground_truth_aspect)", aspect_done, 150),
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
# STEP 4 — Model stability
# ═════════════════════════════════════════════════════════════════════════════
if show[4]:
    n_m = len(model_stab) if not model_stab.empty else 0
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
                unmapped_mask = ~ontology["mapped_to_ontology"].astype(str).str.lower().isin(["true", "1", "yes"]) if "mapped_to_ontology" in ontology.columns else pd.Series([True] * len(ontology))
                unmapped = ontology[unmapped_mask].copy()
                st.markdown(f"#### {len(unmapped)} unmapped aspects — assign clusters")
                cluster_names = ["Community Relations", "Regulatory Compliance", "Supply Chain",
                                 "Human Capital", "Energy & Climate", "Waste & Pollution",
                                 "Governance & Ethics", "Financial Sustainability", "Other"]
                if not unmapped.empty:
                    display_cols = [c for c in ["aspect", "records", "suggested_path"] if c in unmapped.columns]
                    edited_clusters = st.data_editor(
                        unmapped[display_cols].assign(cluster=""),
                        column_config={
                            "cluster": st.column_config.SelectboxColumn("cluster", options=[""] + cluster_names, width="medium"),
                            "aspect": st.column_config.TextColumn("aspect", disabled=True),
                        },
                        use_container_width=True, height=360, key="cluster_editor",
                    )
                    if st.button("Save cluster assignments", type="primary", key="save_clusters"):
                        assigned = edited_clusters[edited_clusters["cluster"].astype(str).str.strip().ne("")]
                        existing_c = load(CLUSTER_PATH)
                        combined = pd.concat([existing_c, assigned], ignore_index=True).drop_duplicates(subset=["aspect"], keep="last")
                        combined.to_csv(CLUSTER_PATH, index=False)
                        st.success(f"Saved {len(assigned)} cluster assignments → {CLUSTER_PATH.name}")
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
            else:
                st.info("Cluster assignments will appear here once you save some.")

            if not ontology.empty:
                st.markdown("#### All aspects overview")
                st.dataframe(ontology[[c for c in ["aspect", "records", "mapped_to_ontology"] if c in ontology.columns]],
                             use_container_width=True, height=260)
