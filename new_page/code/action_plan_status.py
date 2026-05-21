from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ARTIFACTS = RESULTS / "revision_analysis"

SILVER_PATH = ARTIFACTS / "silver_tone_ground_truth.csv"
ANNOTATION_PATH = ARTIFACTS / "pilot_ground_truth_annotations.csv"
SEED_PATH = ARTIFACTS / "pilot_ground_truth_seed.csv"
IMPORTED_PATH = ARTIFACTS / "climatebert_record_batch_import.csv"
CLIMATEBERT_OUTPUT_PATH = ARTIFACTS / "climatebert_output.csv"
MODEL_STAB_PATH = ARTIFACTS / "model_stability_summary.csv"
ESG_RECORDS_PATH = RESULTS / "esg_records.json"

ANNOTATION_TARGET = 250
OCR_PAGE_TARGET = 100
MODEL_TARGET = 3


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def column_series(df: pd.DataFrame, col: str) -> pd.Series:
    if df.empty or col not in df.columns:
        return pd.Series(dtype=str)
    series = df[col]
    if isinstance(series, pd.DataFrame):
        series = series.bfill(axis=1).iloc[:, 0]
    return series


def nonempty_count(df: pd.DataFrame, col: str) -> int:
    series = column_series(df, col)
    if series.empty:
        return 0
    return int(series.astype(str).str.strip().ne("").sum())


def normalise_cols(df: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "tone": "ground_truth_tone",
        "ground_truth_tone": "ground_truth_tone",
        "esg": "ground_truth_esg",
        "pillar": "ground_truth_esg",
        "ground_truth_esg": "ground_truth_esg",
        "aspect": "ground_truth_aspect",
        "ground_truth_aspect": "ground_truth_aspect",
        "status": "review_status",
        "review_status": "review_status",
        "annotator": "annotator",
        "notes": "review_notes",
        "review_notes": "review_notes",
    }
    out = df.copy()
    rename = {col: aliases[col.strip().lower()] for col in out.columns if col.strip().lower() in aliases}
    out = out.rename(columns=rename)
    if out.columns.duplicated().any():
        collapsed = {}
        for col in out.columns:
            data = out.loc[:, out.columns == col]
            collapsed[col] = data.bfill(axis=1).iloc[:, 0] if isinstance(data, pd.DataFrame) else data
        out = pd.DataFrame(collapsed)
    return out


def normalise_annotation_values(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = normalise_cols(df.copy())
    for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "review_status"]:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip().str.lower()
    return out


def build_annotation_table(silver_df: pd.DataFrame, seed_df: pd.DataFrame, annotation_df: pd.DataFrame) -> pd.DataFrame:
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


def ann_n(df: pd.DataFrame, col: str) -> int:
    return nonempty_count(df, col)


def climatebert_processed_record_ids(imported_df: pd.DataFrame) -> set[str]:
    ids: set[str] = set()
    if not imported_df.empty and {"record_id", "climatebert_commitment_pred"}.issubset(imported_df.columns):
        pred = column_series(imported_df, "climatebert_commitment_pred").astype(str).str.strip()
        ids.update(imported_df.loc[pred.ne(""), "record_id"].astype(str))
    if CLIMATEBERT_OUTPUT_PATH.exists():
        try:
            bg = pd.read_csv(CLIMATEBERT_OUTPUT_PATH).fillna("")
            if "record_id" in bg.columns:
                label_cols = [col for col in ["climate_commitment", "label", "top_label", "climate_commitment_label"] if col in bg.columns]
                if label_cols:
                    mask = bg[label_cols].astype(str).apply(lambda row: row.str.strip().ne("").any(), axis=1)
                    ids.update(bg.loc[mask, "record_id"].astype(str))
                else:
                    ids.update(bg["record_id"].astype(str))
        except Exception:
            pass
    return ids


def record_value(record: dict, *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            value = "|".join(str(item) for item in value if str(item).strip())
        if str(value or "").strip():
            return str(value)
    return ""


def load_esg_record_runs() -> list[dict]:
    data = load_json(ESG_RECORDS_PATH, [])
    return data if isinstance(data, list) else []


def derive_model_stability_from_llm_runs() -> pd.DataFrame:
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
                    if isinstance(record, dict) and not record_value(record, "tone", "tone_pred", "disclosure_tone").strip()
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
        )
        .reset_index()
    )
    grouped["missing_tone_rate"] = grouped.apply(
        lambda row: (row["missing_tone_count"] / row["record_total"]) if row["record_total"] else 0,
        axis=1,
    )
    grouped["source"] = "live_reprocess"
    return grouped[["model", "runs", "json_parse_success_rate", "avg_records", "missing_tone_rate", "source"]]


def combine_model_stability(static_df: pd.DataFrame, live_df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    if not static_df.empty:
        static = static_df.copy()
        static["source"] = static.get("source", "revision_analysis")
        frames.append(static)
    if not live_df.empty:
        frames.append(live_df.copy())
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False).fillna("")


def action_plan_status_rows() -> pd.DataFrame:
    silver = load_csv(SILVER_PATH)
    seed = load_csv(SEED_PATH)
    annotation = load_csv(ANNOTATION_PATH)
    annot = build_annotation_table(silver, seed, annotation)
    imported = load_csv(IMPORTED_PATH)
    model_stab = combine_model_stability(load_csv(MODEL_STAB_PATH), derive_model_stability_from_llm_runs())

    cb_processed_ids = climatebert_processed_record_ids(imported)
    cb_real = len(cb_processed_ids) if cb_processed_ids else nonempty_count(imported, "climatebert_commitment_pred")
    cb_target_total = len(silver) if not silver.empty else max(cb_real, 332)
    tone_done = ann_n(annot, "ground_truth_tone")
    esg_done = ann_n(annot, "ground_truth_esg")
    aspect_done = ann_n(annot, "ground_truth_aspect")
    n_models = model_stab["model"].astype(str).str.strip().replace("", pd.NA).dropna().nunique() if "model" in model_stab.columns else 0

    rows = [
        ("ClimateBERT real", cb_real, cb_target_total, cb_real >= cb_target_total and cb_target_total > 0, "pages/3_0_Thesis_Action_Plan.py"),
        ("Tone labels", tone_done, ANNOTATION_TARGET, tone_done >= ANNOTATION_TARGET, "pages/1_1_Ground_Truth_Workbench.py"),
        ("ESG labels", esg_done, ANNOTATION_TARGET, esg_done >= ANNOTATION_TARGET, "pages/1_1_Ground_Truth_Workbench.py"),
        ("Aspect labels", aspect_done, ANNOTATION_TARGET, aspect_done >= ANNOTATION_TARGET, "pages/1_1_Ground_Truth_Workbench.py"),
        ("OCR pages sampled", 0, OCR_PAGE_TARGET, False, "pages/1_2_OCR_Quality_Workbench.py"),
        ("Models tested", int(n_models), MODEL_TARGET, n_models >= MODEL_TARGET, "pages/2_3_LLM_Background_Run_Monitor.py"),
    ]
    return pd.DataFrame(
        [
            {
                "metric": label,
                "completed": completed,
                "target": f"{target}+" if label == "Models tested" else target,
                "value": f"{completed}/{target}+" if label == "Models tested" else f"{completed}/{target}",
                "status": "Done" if ok else "Needed",
                "ok": ok,
                "source page": page,
            }
            for label, completed, target, ok, page in rows
        ]
    )
