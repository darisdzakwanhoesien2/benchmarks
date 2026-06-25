from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Dataset Phase Manager", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "results" / "revision_analysis"
RESULTS = ROOT / "results"
ANNOTATION_PATH = REV / "pilot_ground_truth_annotations.csv"
SILVER_PATH = REV / "silver_tone_ground_truth.csv"
ESG_RECORDS_PATH = RESULTS / "esg_records.json"
LLM_JOBS_DIR = RESULTS / "background_llm_jobs"
PHASE_REGISTRY_PATH = REV / "dataset_phase_registry.csv"

PHASES = ["Phase 1", "Phase 2", "Phase 3"]
CORE_GT_COLS = ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect"]
OPTIONAL_QA_COLS = ["review_status", "annotator", "review_notes"]
DISPLAY_COLS = [
    "select",
    "phase",
    "record_id",
    "completion_status",
    "phase1_ready",
    "has_ground_truth_tone",
    "has_ground_truth_esg",
    "has_ground_truth_aspect",
    "missing_core_fields",
    "review_status",
    "annotator",
    "company",
    "source_dataset",
    "model",
    "prompt",
    "target",
    "ground_truth_tone",
    "ground_truth_esg",
    "ground_truth_aspect",
    "text",
    "phase_reason",
    "updated_at",
]


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


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(p).fillna("")
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
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


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


def registry_created_at() -> str:
    if not PHASE_REGISTRY_PATH.exists():
        return ""
    try:
        registry = pd.read_csv(PHASE_REGISTRY_PATH).fillna("")
    except Exception:
        return ""
    if registry.empty or "first_seen_at" not in registry.columns:
        return ""
    values = [clean(value) for value in registry["first_seen_at"].tolist() if clean(value)]
    return min(values) if values else ""


def ensure_record_id(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out = df.copy()
    if "record_id" not in out.columns:
        out.insert(0, "record_id", [f"{prefix}_{idx:06d}" for idx in range(len(out))])
    out["record_id"] = out["record_id"].map(clean)
    out = out[out["record_id"].ne("")].copy()
    return out.drop_duplicates("record_id", keep="last")


def load_live_llm_records() -> pd.DataFrame:
    runs = read_json(ESG_RECORDS_PATH, [])
    if not isinstance(runs, list):
        return pd.DataFrame()

    rows: list[dict] = []
    for run_idx, run in enumerate(runs):
        if not isinstance(run, dict):
            continue
        records = run.get("records") if isinstance(run.get("records"), list) else []
        target = clean(run.get("target"))
        company = target.split("/", 1)[0].replace("_pdf", "").replace("_PDF", "")
        for record_idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            text = record_value(record, "text", "sentence", "statement", "disclosure", "evidence")
            record_id = stable_id(
                "llm",
                run.get("background_job_id", ""),
                run.get("model", ""),
                target,
                run.get("prompt", ""),
                record_idx,
                text[:200],
            )
            tone = record_value(record, "tone", "tone_pred", "disclosure_tone").lower()
            esg = normalise_esg_value(record_value(record, "esg", "pillar", "ground_truth_esg"))
            aspect = record_value(record, "aspect", "topic", "esg_aspect")
            rows.append(
                {
                    "record_id": record_id,
                    "source_dataset": "live_llm_reprocess",
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": clean(run.get("timestamp")),
                    "model": clean(run.get("model")),
                    "prompt": clean(run.get("prompt")),
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
                    "background_job_id": clean(run.get("background_job_id")),
                }
            )
    return pd.DataFrame(rows)


def load_background_llm_event_rows() -> pd.DataFrame:
    if not LLM_JOBS_DIR.exists():
        return pd.DataFrame()
    cutoff = registry_created_at()
    if not cutoff:
        return pd.DataFrame()

    rows: list[dict] = []
    for events_path in sorted(LLM_JOBS_DIR.glob("*/events.jsonl")):
        job_id = events_path.parent.name
        for event_idx, event in enumerate(read_jsonl(events_path)):
            event_name = clean(event.get("event"))
            if event_name not in {"completed", "failed"}:
                continue
            event_time = clean(event.get("time"))
            if not event_time or event_time < cutoff:
                continue
            target = clean(event.get("target"))
            prompt = clean(event.get("prompt"))
            model = clean(event.get("model"))
            pages = clean(event.get("pages"))
            record_count = clean(event.get("records"))
            record_id = stable_id("llm_event", job_id, event_idx, event_name, target, prompt, model, pages)
            rows.append(
                {
                    "record_id": record_id,
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
                }
            )
    return pd.DataFrame(rows)


def build_source_records() -> pd.DataFrame:
    annot = ensure_record_id(load_csv(str(ANNOTATION_PATH)), "annot")
    silver = ensure_record_id(load_csv(str(SILVER_PATH)), "silver")
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

    for col in CORE_GT_COLS + OPTIONAL_QA_COLS + ["company", "model", "prompt", "target", "source_dataset", "text"]:
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

    missing_core: list[str] = []
    phase1_ready: list[bool] = []
    has_tone: list[bool] = []
    has_esg: list[bool] = []
    has_aspect: list[bool] = []
    qa_missing: list[str] = []
    status: list[str] = []

    for _, row in out.iterrows():
        missing = [col for col in CORE_GT_COLS if not clean(row.get(col))]
        missing_qa = [col for col in OPTIONAL_QA_COLS if not clean(row.get(col))]
        ready = not missing
        has_tone.append(bool(clean(row.get("ground_truth_tone"))))
        has_esg.append(bool(clean(row.get("ground_truth_esg"))))
        has_aspect.append(bool(clean(row.get("ground_truth_aspect"))))
        missing_core.append(", ".join(missing))
        qa_missing.append(", ".join(missing_qa))
        phase1_ready.append(ready)
        if ready and not missing_qa:
            status.append("complete_with_qa")
        elif ready:
            status.append("ground_truth_complete")
        else:
            status.append("needs_editing")

    out["missing_core_fields"] = missing_core
    out["missing_qa_fields"] = qa_missing
    out["phase1_ready"] = phase1_ready
    out["has_ground_truth_tone"] = has_tone
    out["has_ground_truth_esg"] = has_esg
    out["has_ground_truth_aspect"] = has_aspect
    out["completion_status"] = status
    return out


def infer_initial_phase(row: pd.Series) -> str:
    if clean(row.get("source_dataset")) in {"live_llm_reprocess", "background_llm_event"}:
        return "Phase 3"
    return "Phase 1" if bool(row.get("phase1_ready")) else "Phase 2"


def load_or_create_registry(source: pd.DataFrame) -> pd.DataFrame:
    source = completion_flags(source)
    now = utc_now()

    if PHASE_REGISTRY_PATH.exists():
        registry = load_csv(str(PHASE_REGISTRY_PATH))
    else:
        registry = pd.DataFrame()

    required = ["record_id", "phase", "phase_reason", "first_seen_at", "updated_at", "updated_by"]
    for col in required:
        if col not in registry.columns:
            registry[col] = ""

    existing_ids = set(registry["record_id"].map(clean))
    rows = []
    created_registry = registry.empty
    for _, row in source.iterrows():
        record_id = clean(row.get("record_id"))
        if not record_id or record_id in existing_ids:
            continue
        if created_registry:
            phase = infer_initial_phase(row)
            reason = "Initial registry inference from current ground-truth completeness"
        else:
            phase = "Phase 3"
            reason = "New record detected after phase registry was created"
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
        st.cache_data.clear()

    registry = registry[required].copy()
    registry["record_id"] = registry["record_id"].map(clean)
    registry["phase"] = registry["phase"].where(registry["phase"].isin(PHASES), "Phase 3")
    return registry.drop_duplicates("record_id", keep="last")


def save_registry(registry: pd.DataFrame) -> None:
    PHASE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = registry.copy()
    for col in ["record_id", "phase", "phase_reason", "first_seen_at", "updated_at", "updated_by"]:
        if col not in out.columns:
            out[col] = ""
    out = out[["record_id", "phase", "phase_reason", "first_seen_at", "updated_at", "updated_by"]]
    out.to_csv(PHASE_REGISTRY_PATH, index=False)


def joined_phase_view(source: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    source = completion_flags(source)
    view = source.merge(registry, on="record_id", how="left")
    view["phase"] = view["phase"].where(view["phase"].isin(PHASES), "Phase 3")
    view["text"] = view["text"].map(lambda value: clean(value)[:500])
    view.insert(0, "select", False)
    for col in DISPLAY_COLS:
        if col not in view.columns:
            view[col] = ""
    return view


def move_records(registry: pd.DataFrame, record_ids: list[str], target_phase: str, reason: str) -> int:
    if not record_ids or target_phase not in PHASES:
        return 0
    now = utc_now()
    out = registry.copy()
    mask = out["record_id"].isin(record_ids)
    out.loc[mask, "phase"] = target_phase
    out.loc[mask, "phase_reason"] = reason.strip() or f"Moved to {target_phase}"
    out.loc[mask, "updated_at"] = now
    out.loc[mask, "updated_by"] = "phase_manager"
    save_registry(out)
    st.cache_data.clear()
    return int(mask.sum())


def phase_summary(view: pd.DataFrame) -> pd.DataFrame:
    if view.empty:
        return pd.DataFrame(columns=["phase", "records", "phase1_ready", "needs_editing", "complete_with_qa"])
    grouped = (
        view.groupby("phase", dropna=False)
        .agg(
            records=("record_id", "size"),
            phase1_ready=("phase1_ready", "sum"),
            needs_editing=("completion_status", lambda s: int((s == "needs_editing").sum())),
            complete_with_qa=("completion_status", lambda s: int((s == "complete_with_qa").sum())),
            ground_truth_tone=("has_ground_truth_tone", "sum"),
            missing_ground_truth_tone=("has_ground_truth_tone", lambda s: int((~s.astype(bool)).sum())),
            ground_truth_esg=("has_ground_truth_esg", "sum"),
            missing_ground_truth_esg=("has_ground_truth_esg", lambda s: int((~s.astype(bool)).sum())),
            ground_truth_aspect=("has_ground_truth_aspect", "sum"),
            missing_ground_truth_aspect=("has_ground_truth_aspect", lambda s: int((~s.astype(bool)).sum())),
        )
        .reset_index()
    )
    return grouped.sort_values("phase")


st.title("Dataset Phase Manager")
st.caption("Manage the completed dataset pool, editing backlog, and new incoming records.")

source_records = build_source_records()
if source_records.empty:
    st.warning("No source records found in the annotation or silver datasets.")
    st.stop()

registry = load_or_create_registry(source_records)
view = joined_phase_view(source_records, registry)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Phase 1 completed pool", f"{int((view['phase'] == 'Phase 1').sum()):,}")
c2.metric("Phase 2 editing pool", f"{int((view['phase'] == 'Phase 2').sum()):,}")
c3.metric("Phase 3 new intake", f"{int((view['phase'] == 'Phase 3').sum()):,}")
c4.metric("Phase 1 ready rows", f"{int(view['phase1_ready'].sum()):,}")

summary = phase_summary(view)
chart = alt.Chart(summary).mark_bar().encode(
    x=alt.X("phase:N", title=None),
    y=alt.Y("records:Q", title="records"),
    color=alt.Color("phase:N", legend=None),
    tooltip=["phase", "records", "phase1_ready", "needs_editing", "complete_with_qa"],
).properties(height=220)
st.altair_chart(chart, use_container_width=True)
st.dataframe(summary, use_container_width=True, hide_index=True)

with st.expander("Phase definitions", expanded=True):
    phase_description = pd.DataFrame(
        [
            {
                "phase": "Phase 1",
                "table description": "Completed dataset pool.",
                "what is missing": "Nothing required for core dataset completeness. Rows are ready to support final analysis denominators.",
                "next action": "Keep locked unless a quality issue is found.",
            },
            {
                "phase": "Phase 2",
                "table description": "Editing and backfill pool.",
                "what is missing": (
                    "One or more required completion items: ground-truth labels, review status, annotator metadata, "
                    "review notes, OCR ground truth, model outputs, provenance, or documented exclusion."
                ),
                "next action": "Edit/backfill the missing fields, then promote complete rows to Phase 1.",
            },
            {
                "phase": "Phase 3",
                "table description": "New incoming data from now onward.",
                "what is missing": (
                    "Triage decision. These rows have not yet been accepted into the completed dataset or assigned "
                    "to the editing/backfill queue."
                ),
                "next action": "Move complete rows directly to Phase 1; move incomplete rows to Phase 2 for editing.",
            },
        ]
    )
    st.dataframe(phase_description, use_container_width=True, hide_index=True)
    st.markdown(
        """
| Phase | Meaning | Can move when |
|---|---|---|
| Phase 1 | Completed dataset pool used for final analysis claims. | A row has usable ground-truth tone, ESG, and aspect labels, or has a documented exclusion. |
| Phase 2 | Editing and backfill pool. | A row needs missing labels, review status, annotator metadata, notes, OCR truth, model output, or provenance work. |
| Phase 3 | New intake from now onward. | New rows wait here until reviewed; complete rows can move directly to Phase 1, incomplete rows move to Phase 2. |
"""
    )

with st.sidebar:
    st.header("Filters")
    phase_filter = st.multiselect("Phase", PHASES, default=PHASES)
    status_options = sorted(view["completion_status"].dropna().unique().tolist())
    status_filter = st.multiselect("Completion status", status_options, default=status_options)
    ready_only = st.checkbox("Phase 1 ready only", value=False)
    query = st.text_input("Search text / company / record_id", value="")
    max_rows = st.number_input("Max visible rows", min_value=50, max_value=5000, value=500, step=50)

filtered = view[view["phase"].isin(phase_filter) & view["completion_status"].isin(status_filter)].copy()
if ready_only:
    filtered = filtered[filtered["phase1_ready"]]
if query.strip():
    q = query.strip().lower()
    haystack = (
        filtered["record_id"].astype(str)
        + " "
        + filtered["company"].astype(str)
        + " "
        + filtered["text"].astype(str)
    ).str.lower()
    filtered = filtered[haystack.str.contains(q, na=False)]

filtered = filtered.sort_values(["phase", "completion_status", "record_id"]).head(int(max_rows)).reset_index(drop=True)

st.subheader("Record Phase Editor")
st.caption(f"Showing {len(filtered):,} row(s). Phase moves update `{PHASE_REGISTRY_PATH.relative_to(ROOT)}`.")

edited = st.data_editor(
    filtered[[col for col in DISPLAY_COLS if col in filtered.columns]],
    use_container_width=True,
    hide_index=True,
    height=520,
    column_config={
        "select": st.column_config.CheckboxColumn("select"),
        "phase": st.column_config.SelectboxColumn("phase", options=PHASES),
        "phase1_ready": st.column_config.CheckboxColumn("phase1_ready"),
        "has_ground_truth_tone": st.column_config.CheckboxColumn("has_ground_truth_tone"),
        "has_ground_truth_esg": st.column_config.CheckboxColumn("has_ground_truth_esg"),
        "has_ground_truth_aspect": st.column_config.CheckboxColumn("has_ground_truth_aspect"),
        "text": st.column_config.TextColumn("text", width="large"),
        "phase_reason": st.column_config.TextColumn("phase_reason", width="large"),
    },
    disabled=[col for col in DISPLAY_COLS if col != "select" and col in filtered.columns],
    key="phase_record_editor",
)

selected_ids = edited.loc[edited["select"], "record_id"].map(clean).tolist() if "select" in edited.columns else []

st.subheader("Move Selected Records")
reason = st.text_input("Move reason", value="")
a1, a2, a3, a4 = st.columns(4)
if a1.button("Move selected to Phase 1", type="primary", use_container_width=True, disabled=not selected_ids):
    moved = move_records(registry, selected_ids, "Phase 1", reason or "Marked complete for Phase 1 dataset pool")
    st.success(f"Moved {moved:,} record(s) to Phase 1.")
    st.rerun()
if a2.button("Move selected to Phase 2", use_container_width=True, disabled=not selected_ids):
    moved = move_records(registry, selected_ids, "Phase 2", reason or "Moved to editing/backfill pool")
    st.success(f"Moved {moved:,} record(s) to Phase 2.")
    st.rerun()
if a3.button("Move selected to Phase 3", use_container_width=True, disabled=not selected_ids):
    moved = move_records(registry, selected_ids, "Phase 3", reason or "Moved to new intake pool")
    st.success(f"Moved {moved:,} record(s) to Phase 3.")
    st.rerun()

selected_complete_ids = edited.loc[
    edited["select"] & edited["phase1_ready"], "record_id"
].map(clean).tolist() if {"select", "phase1_ready", "record_id"}.issubset(edited.columns) else []
if a4.button("Promote complete selection", use_container_width=True, disabled=not selected_complete_ids):
    moved = move_records(registry, selected_complete_ids, "Phase 1", reason or "Promoted after completion check")
    st.success(f"Promoted {moved:,} complete record(s) to Phase 1.")
    st.rerun()

st.subheader("Bulk Phase Operations")
b1, b2, b3 = st.columns(3)
phase2_complete_ids = view.loc[(view["phase"] == "Phase 2") & view["phase1_ready"], "record_id"].map(clean).tolist()
phase3_complete_ids = view.loc[(view["phase"] == "Phase 3") & view["phase1_ready"], "record_id"].map(clean).tolist()
phase3_incomplete_ids = view.loc[(view["phase"] == "Phase 3") & (~view["phase1_ready"]), "record_id"].map(clean).tolist()

if b1.button(
    f"Promote complete Phase 2 to Phase 1 ({len(phase2_complete_ids):,})",
    use_container_width=True,
    disabled=not phase2_complete_ids,
):
    moved = move_records(registry, phase2_complete_ids, "Phase 1", "Bulk promoted completed Phase 2 records")
    st.success(f"Moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if b2.button(
    f"Promote complete Phase 3 to Phase 1 ({len(phase3_complete_ids):,})",
    use_container_width=True,
    disabled=not phase3_complete_ids,
):
    moved = move_records(registry, phase3_complete_ids, "Phase 1", "Bulk promoted completed Phase 3 records")
    st.success(f"Moved {moved:,} record(s) to Phase 1.")
    st.rerun()

if b3.button(
    f"Move incomplete Phase 3 to Phase 2 ({len(phase3_incomplete_ids):,})",
    use_container_width=True,
    disabled=not phase3_incomplete_ids,
):
    moved = move_records(registry, phase3_incomplete_ids, "Phase 2", "Bulk moved incomplete Phase 3 records to editing")
    st.success(f"Moved {moved:,} record(s) to Phase 2.")
    st.rerun()

st.subheader("Exports")
e1, e2 = st.columns(2)
e1.download_button(
    "Download phase registry",
    registry.to_csv(index=False).encode("utf-8"),
    file_name="dataset_phase_registry.csv",
    mime="text/csv",
    use_container_width=True,
)
e2.download_button(
    "Download current phase view",
    view.to_csv(index=False).encode("utf-8"),
    file_name="dataset_phase_view.csv",
    mime="text/csv",
    use_container_width=True,
)
