from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "results" / "revision_analysis"
VIS = ROOT / "results" / "visualizations"
SRC = ART / "climatebert_record_batch_import.csv"


def normalize_label(v: object) -> str:
    t = str(v or "").strip()
    if not t:
        return "missing"
    if t.lower() in {"nan", "none", "null", "n/a", "na", "undefined"}:
        return "missing"
    return t


def normalize_tone(v: object) -> str:
    t = str(v or "").strip().lower()
    if not t or t in {"nan", "none", "null", "n/a", "na", "undefined"}:
        return "missing"
    if t in {"commitment", "action", "outcome", "none", "unknown", "missing"}:
        return t
    if "," in t:
        parts = [p.strip() for p in t.split(",") if p.strip()]
        for k in ["commitment", "action", "outcome"]:
            if k in parts:
                return k
    return t


def pick_label_col(df: pd.DataFrame) -> str:
    for c in ["climatebert_label", "label", "top_label", "climate_commitment_label"]:
        if c in df.columns and df[c].astype(str).str.strip().ne("").any():
            return c
    return ""


def main() -> int:
    if not SRC.exists():
        print(f"Missing source CSV: {SRC}")
        return 1
    df = pd.read_csv(SRC).fillna("")
    if "tone_pred" not in df.columns:
        print("Missing tone_pred column")
        return 1
    label_col = pick_label_col(df)
    if not label_col:
        print("No usable ClimateBERT label column found")
        return 1

    view = pd.DataFrame({
        "tone": df["tone_pred"].map(normalize_tone),
        "climatebert_label": df[label_col].map(normalize_label),
    })
    pivot = pd.crosstab(view["tone"], view["climatebert_label"])
    tone_order = ["commitment", "action", "outcome", "none", "unknown", "missing"]
    existing = [t for t in tone_order if t in pivot.index]
    extra = [t for t in pivot.index.tolist() if t not in existing]
    if existing:
        pivot = pivot.reindex(existing + extra, fill_value=0)
    out = pivot.reset_index()

    VIS.mkdir(parents=True, exist_ok=True)
    out.to_csv(VIS / "tone_climatebert_label_crosstab.csv", index=False)
    out.to_csv(VIS / "tone_climatebert_label_crosstab_full.csv", index=False)

    import matplotlib.pyplot as plt

    table = out.set_index("tone")
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
    fig.savefig(VIS / "climatebert_label_by_tone.png", dpi=180)
    plt.close(fig)

    print(f"Rows: {len(df)}")
    print(f"Tone x label matrix: {pivot.shape[0]} x {pivot.shape[1]}")
    print("Top labels:")
    print(view["climatebert_label"].value_counts().head(10).to_string())
    print("Saved:")
    print(VIS / "tone_climatebert_label_crosstab.csv")
    print(VIS / "tone_climatebert_label_crosstab_full.csv")
    print(VIS / "climatebert_label_by_tone.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
