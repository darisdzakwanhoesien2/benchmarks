from __future__ import annotations

import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
IMPORTED_PATH = ROOT / "results" / "revision_analysis" / "climatebert_record_batch_import.csv"
VIS = ROOT / "results" / "visualizations"


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unknown"


def crosstab_for_group(group_key: str, group_df: pd.DataFrame) -> tuple[str, int, Path]:
    view = group_df.copy()
    view["tone"] = view["tone_pred"].astype(str).str.strip().replace("", "missing")
    view["climatebert_label"] = view["climatebert_label"].astype(str).str.strip().replace("", "missing")
    pivot = pd.crosstab(view["tone"], view["climatebert_label"]).reset_index()

    out_name = f"tone_climatebert_label_crosstab_full__{slugify(group_key)}.csv"
    out_path = VIS / out_name
    pivot.to_csv(out_path, index=False)
    return group_key, len(group_df), out_path


def main() -> int:
    VIS.mkdir(parents=True, exist_ok=True)
    if not IMPORTED_PATH.exists():
        raise FileNotFoundError(f"Missing input: {IMPORTED_PATH}")

    df = pd.read_csv(IMPORTED_PATH).fillna("")
    required = {"tone_pred", "climatebert_label", "climatebert_model"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")

    groups = []
    for model_name, g in df.groupby("climatebert_model", dropna=False):
        model_name = str(model_name).strip() or "unknown_model"
        groups.append((model_name, g.copy()))

    summary_rows = []
    with ProcessPoolExecutor(max_workers=min(8, max(1, len(groups)))) as ex:
        futures = [ex.submit(crosstab_for_group, model_name, g) for model_name, g in groups]
        for fut in as_completed(futures):
            model_name, records, out_path = fut.result()
            print(f"[ok] {model_name} -> {out_path.name} ({records} rows)")
            summary_rows.append({"climatebert_model": model_name, "rows": records, "file": out_path.name})

    summary = pd.DataFrame(summary_rows).sort_values("rows", ascending=False)
    summary_path = VIS / "tone_climatebert_label_crosstab_full__by_model_manifest.csv"
    summary.to_csv(summary_path, index=False)
    print(f"[ok] manifest -> {summary_path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
