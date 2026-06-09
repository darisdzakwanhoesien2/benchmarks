"""Generate tone-vs-ClimateBERT visualizations and documentation.

This script uses the existing result artifacts:
- results/esg_records.json: LLM extracted ESG records with tone/aspect/labels.
- results/climatebert_results.json: raw ClimateBERT remote-space responses.

Outputs are written to:
- results/visualizations/
- docs/tone_climatebert_comparison.md
"""

from __future__ import annotations

import json
import re
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
OUT_DIR = RESULTS_DIR / "visualizations"
DOC_PATH = ROOT / "docs" / "tone_climatebert_comparison.md"
WORKFLOW_DIR = RESULTS_DIR / "thesis_workflow_dashboard"
REVISION_DIR = RESULTS_DIR / "revision_analysis"


def clean_label(value: object, default: str = "missing") -> str:
    text = "" if value is None else str(value).strip().lower()
    if not text:
        return default
    return text


def normalize_tone(value: object) -> str:
    text = clean_label(value, "missing")
    mapping = {
        "commitment": "commitment",
        "action": "action",
        "outcome": "outcome",
        "none": "none",
        "unknown": "unknown",
        "missing": "missing",
    }
    return mapping.get(text, text)


def load_esg_records() -> pd.DataFrame:
    path = RESULTS_DIR / "esg_records.json"
    runs = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []

    for run_idx, run in enumerate(runs):
        for rec_idx, record in enumerate(run.get("records") or []):
            labels = record.get("labels")
            if not isinstance(labels, list):
                labels = []
            rows.append(
                {
                    "run_idx": run_idx,
                    "record_idx": rec_idx,
                    "timestamp": run.get("timestamp"),
                    "model": run.get("model"),
                    "target": run.get("target"),
                    "prompt": run.get("prompt"),
                    "text": record.get("text", ""),
                    "aspect": clean_label(record.get("aspect")),
                    "esg": clean_label(record.get("esg")),
                    "tone": normalize_tone(record.get("tone")),
                    "sentiment": clean_label(record.get("sentiment")),
                    "sentiment_score": record.get("sentiment_score"),
                    "labels": labels,
                    "reasoning": record.get("reasoning", ""),
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty:
        df["target_doc"] = df["target"].fillna("").str.replace(r"_pdf/batch_\d+$", "", regex=True)
        df["text_len_words"] = df["text"].fillna("").map(lambda value: len(str(value).split()))
    return df


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def parse_climatebert_response(raw: object) -> list[dict[str, object]]:
    if raw is None:
        return []
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
    lines = [line.strip() for line in text.splitlines()]
    models: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    bullet_re = re.compile(r"^[•\-\*\u2022]\s*(.+)$")
    label_val_re = re.compile(r"^(.+?)\s*[:\-]\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")

    for line in lines:
        if not line:
            continue
        if line.startswith("###"):
            if current is not None:
                models.append(current)
            current = {"model": line[3:].strip(), "status": "ok", "scores": {}, "error": ""}
            continue
        if current is None:
            continue
        if "❌" in line or line.lower().startswith("error:") or "unrecognized model" in line.lower():
            msg = line.replace("❌", "").strip()
            msg = re.sub(r"^error:\s*", "", msg, flags=re.I)
            current["status"] = "error"
            current["error"] = msg
            continue

        candidate_match = bullet_re.match(line)
        candidate = candidate_match.group(1).strip() if candidate_match else line
        pair = label_val_re.match(candidate)
        if pair:
            scores = current.setdefault("scores", {})
            assert isinstance(scores, dict)
            scores[pair.group(1).strip()] = float(pair.group(2))

    if current is not None:
        models.append(current)
    return models


def load_climatebert_rows() -> pd.DataFrame:
    path = RESULTS_DIR / "climatebert_results.json"
    rows: list[dict[str, object]] = []
    if not path.exists():
        return pd.DataFrame()

    records = json.loads(path.read_text(encoding="utf-8"))
    for run_idx, run in enumerate(records):
        models = run.get("response_parsed", {}).get("models") if isinstance(run.get("response_parsed"), dict) else None
        if not models:
            models = parse_climatebert_response(run.get("response_raw"))
        for model in models:
            scores = model.get("scores") if isinstance(model, dict) else {}
            if scores:
                for label, score in scores.items():
                    rows.append(
                        {
                            "run_idx": run_idx,
                            "timestamp": run.get("timestamp"),
                            "input_text": run.get("input_text", ""),
                            "model": model.get("model") or model.get("name"),
                            "status": model.get("status"),
                            "label": label,
                            "score": score,
                            "error": model.get("error", ""),
                        }
                    )
            else:
                rows.append(
                    {
                        "run_idx": run_idx,
                        "timestamp": run.get("timestamp"),
                        "input_text": run.get("input_text", ""),
                        "model": model.get("model") or model.get("name"),
                        "status": model.get("status"),
                        "label": "",
                        "score": None,
                        "error": model.get("error", ""),
                    }
                )
    return pd.DataFrame(rows)


def save_bar(data: pd.Series, title: str, xlabel: str, ylabel: str, path: Path, color: str = "#2f6f73") -> None:
    fig_height = max(4.2, min(9, 0.45 * len(data) + 1.5))
    fig, ax = plt.subplots(figsize=(9.5, fig_height))
    data.sort_values().plot(kind="barh", ax=ax, color=color)
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_stacked_tone_esg(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    table = pd.crosstab(df["tone"], df["esg"])
    keep_cols = [col for col in ["e", "s", "g", "none", "missing"] if col in table.columns]
    table = table[keep_cols + [col for col in table.columns if col not in keep_cols]]

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    table.plot(kind="bar", stacked=True, ax=ax, colormap="Set2")
    ax.set_title("Tone Distribution by ESG Pillar", fontsize=14, pad=12)
    ax.set_xlabel("Tone")
    ax.set_ylabel("Record count")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="ESG", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return table


def save_heatmap(table: pd.DataFrame, title: str, path: Path, figsize: tuple[float, float] = (11, 6)) -> None:
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(table, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.4, ax=ax)
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel(table.columns.name or "")
    ax.set_ylabel(table.index.name or "")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_failure_pareto(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df.copy()
    plot["count"] = pd.to_numeric(plot.get("count"), errors="coerce").fillna(0)
    plot = plot.groupby("mode", as_index=False)["count"].sum().sort_values("count", ascending=False)
    plot["cumulative_pct"] = plot["count"].cumsum() / plot["count"].sum()

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax1.bar(plot["mode"], plot["count"], color="#b45309")
    ax1.set_ylabel("Failure count")
    ax1.set_xlabel("Failure mode")
    ax1.set_title("Failure-Mode Pareto Summary", fontsize=14, pad=12)
    ax1.tick_params(axis="x", rotation=30)
    ax1.grid(axis="y", alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(plot["mode"], plot["cumulative_pct"], color="#1d4ed8", marker="o")
    ax2.set_ylabel("Cumulative share")
    ax2.set_ylim(0, 1.05)
    ax2.axhline(0.8, color="#dc2626", linestyle="--", linewidth=1)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))

    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_failure_pie(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df.copy()
    plot["count"] = pd.to_numeric(plot.get("count"), errors="coerce").fillna(0)
    grouped = plot.groupby("mode", as_index=False)["count"].sum().sort_values("count", ascending=False)
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.pie(grouped["count"], labels=grouped["mode"], autopct="%1.1f%%", startangle=90, counterclock=False)
    ax.set_title("Failure-Mode Composition", fontsize=14, pad=12)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_model_tradeoff(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df.copy()
    for col in ["json_parse_success_rate", "avg_records", "runs"]:
        plot[col] = pd.to_numeric(plot.get(col), errors="coerce").fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        plot["json_parse_success_rate"],
        plot["avg_records"],
        s=40 + plot["runs"] * 2,
        c=plot["runs"],
        cmap="viridis",
        alpha=0.85,
        edgecolors="black",
        linewidths=0.4,
    )
    for _, row in plot.iterrows():
        ax.annotate(str(row["model"]), (row["json_parse_success_rate"], row["avg_records"]), xytext=(6, 4), textcoords="offset points", fontsize=9)
    ax.set_xlabel("Parse success rate")
    ax.set_ylabel("Average records per run")
    ax.set_title("Model Trade-off: Parse Success vs Extraction Yield", fontsize=14, pad=12)
    ax.set_xlim(-0.02, 1.02)
    ax.grid(alpha=0.25)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Runs")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_prompt_strategy(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df.copy()
    plot["avg_records"] = pd.to_numeric(plot.get("avg_records"), errors="coerce").fillna(0)
    plot["json_parse_success_rate"] = pd.to_numeric(plot.get("json_parse_success_rate"), errors="coerce").fillna(0)
    plot["field_completion_rate"] = pd.to_numeric(plot.get("field_completion_rate"), errors="coerce").fillna(0)

    metrics = [
        ("avg_records", "Average records", "#0f766e"),
        ("json_parse_success_rate", "Parse success", "#395b91"),
        ("field_completion_rate", "Field completion", "#b45309"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4))
    for ax, (col, title, color) in zip(axes, metrics):
        ordered = plot.sort_values(col, ascending=False)
        ax.bar(ordered["prompt"], ordered[col], color=color)
        ax.set_title(title, fontsize=12)
        ax.tick_params(axis="x", rotation=35, labelsize=8)
        ax.grid(axis="y", alpha=0.25)
        if col != "avg_records":
            ax.set_ylim(0, 1.05)
    fig.suptitle("Prompt Strategy Comparison", fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


SOFT_VERBS = {
    "aim", "aimed", "commit", "committed", "consider", "continue", "continued",
    "explore", "exploring", "intend", "intends", "plan", "planned", "planning",
    "seek", "seeks", "support", "supports", "will", "target", "targets",
    "berkomitmen", "komitmen", "mendukung", "akan", "rencana", "menjajaki", "eksplorasi",
}
CONCRETE_VERBS = {
    "achieved", "built", "completed", "decreased", "implemented", "installed",
    "measured", "reduced", "reported", "retained", "signed", "tested", "trained",
    "adopted", "menurunkan", "menerapkan", "mengurangi", "menandatangani",
    "membangun", "melakukan", "mencapai", "mengadopsi", "uji",
}


def vagueness_score(text: str) -> float:
    tokens = [token.strip(".,;:!?()[]{}\"'").lower() for token in str(text).split()]
    tokens = [token for token in tokens if token]
    soft = sum(1 for token in tokens if token in SOFT_VERBS)
    concrete = sum(1 for token in tokens if token in CONCRETE_VERBS)
    total = soft + concrete
    return 0.5 if total == 0 else soft / total


def save_information_density(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df[df["tone"].isin(["commitment", "action", "outcome", "none"])].copy()
    if plot.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.boxplot(data=plot, x="tone", y="text_len_words", order=["commitment", "action", "outcome", "none"], ax=ax, palette="Set2")
    ax.set_title("Information Density by Tone", fontsize=14, pad=12)
    ax.set_xlabel("Tone")
    ax.set_ylabel("Words per record")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_soft_language_ratio(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df[df["tone"].isin(["commitment", "action", "outcome"])].copy()
    if plot.empty:
        return
    plot["vagueness_score"] = plot["text"].map(vagueness_score)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.boxplot(data=plot, x="tone", y="vagueness_score", order=["commitment", "action", "outcome"], ax=ax, palette="YlOrBr")
    ax.set_title("Soft-Language Ratio by Tone", fontsize=14, pad=12)
    ax.set_xlabel("Tone")
    ax.set_ylabel("Soft / (Soft + Concrete) verb ratio")
    ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_greenwashing_gap(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    plot = df.copy()
    for col in ["commitment", "outcome", "records", "greenwashing_index"]:
        plot[col] = pd.to_numeric(plot.get(col), errors="coerce").fillna(0)
    fig, ax = plt.subplots(figsize=(9.5, 6))
    scatter = ax.scatter(
        plot["outcome"],
        plot["commitment"],
        s=50 + plot["records"] * 4,
        c=plot["greenwashing_index"],
        cmap="OrRd",
        alpha=0.8,
        edgecolors="black",
        linewidths=0.4,
    )
    for _, row in plot.head(10).iterrows():
        ax.annotate(str(row["company"]), (row["outcome"], row["commitment"]), xytext=(5, 4), textcoords="offset points", fontsize=8)
    limit = max(float(plot["outcome"].max()), float(plot["commitment"].max()), 1.0)
    ax.plot([0, limit], [0, limit], linestyle="--", color="#64748b", linewidth=1)
    ax.set_xlabel("Outcome count")
    ax.set_ylabel("Commitment count")
    ax.set_title("Commitment-Outcome Gap by Company", fontsize=14, pad=12)
    ax.grid(alpha=0.25)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Greenwashing index")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def save_commitment_outcome_ratio(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    counts = df["tone"].value_counts().rename_axis("tone").reset_index(name="records")
    counts["share"] = counts["records"] / counts["records"].sum()
    order = ["commitment", "action", "outcome", "none", "missing", "unknown"]
    counts["tone"] = pd.Categorical(counts["tone"], categories=order, ordered=True)
    counts = counts.sort_values("tone")
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(counts["tone"].astype(str), counts["share"], color="#0f766e")
    ax.set_title("Tone Share Across Extracted Records", fontsize=14, pad=12)
    ax.set_xlabel("Tone")
    ax.set_ylabel("Share of records")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def climatebert_label_family(label: str) -> str:
    text = clean_label(label, "missing")
    if text.startswith("climate-"):
        return text
    if text in {"environmental-claims", "netzero-reduction", "renewable"}:
        return text
    if text in {"governance", "social", "employee", "community"}:
        return text
    if text == "none":
        return "none"
    return "other"


def write_doc(
    df: pd.DataFrame,
    cb_df: pd.DataFrame,
    label_tone: pd.DataFrame,
    tone_esg: pd.DataFrame,
    climate_top: pd.DataFrame,
) -> None:
    total_records = len(df)
    total_runs = df["run_idx"].nunique()
    total_targets = df["target"].nunique()
    tone_counts = df["tone"].value_counts()
    esg_counts = df["esg"].value_counts()
    missing_tone = int(tone_counts.get("missing", 0))
    non_empty_tones = tone_counts.drop(labels=["missing"], errors="ignore")
    dominant_tone = non_empty_tones.idxmax() if not non_empty_tones.empty else "n/a"
    dominant_tone_count = int(non_empty_tones.max()) if not non_empty_tones.empty else 0

    cb_runs = cb_df["run_idx"].nunique() if not cb_df.empty else 0
    cb_models = cb_df["model"].nunique() if not cb_df.empty else 0
    cb_errors = int((cb_df["status"] == "error").sum()) if not cb_df.empty else 0
    cb_ok = cb_df[cb_df["status"] == "ok"] if not cb_df.empty else pd.DataFrame()

    top_labels = (
        df.explode("labels")["labels"]
        .dropna()
        .map(lambda value: clean_label(value))
        .value_counts()
        .head(10)
    )
    tone_label_notes = []
    for tone in ["commitment", "action", "outcome", "none", "missing"]:
        if tone not in label_tone.index:
            continue
        top_for_tone = label_tone.loc[tone].sort_values(ascending=False).head(3)
        formatted = ", ".join(f"`{label}`={int(count)}" for label, count in top_for_tone.items())
        tone_label_notes.append(f"- `{tone}` most often appears with {formatted}.")

    chart_links = [
        "results/visualizations/tone_distribution.png",
        "results/visualizations/esg_by_tone.png",
        "results/visualizations/climatebert_label_by_tone.png",
        "results/visualizations/aspect_by_tone_heatmap.png",
        "results/visualizations/climatebert_remote_top_scores.png",
        "results/visualizations/failure_mode_pareto.png",
        "results/visualizations/failure_mode_pie.png",
        "results/visualizations/model_tradeoff_scatter.png",
        "results/visualizations/prompt_strategy_comparison.png",
        "results/visualizations/information_density_by_tone.png",
        "results/visualizations/soft_language_ratio_by_tone.png",
        "results/visualizations/greenwashing_gap_scatter.png",
        "results/visualizations/commitment_outcome_ratio.png",
    ]

    lines = [
        "# Tone and ClimateBERT Comparison",
        "",
        "## Scope",
        "",
        f"This analysis uses `{RESULTS_DIR / 'esg_records.json'}` as the existing tone-result dataset. It contains {total_records} extracted records from {total_runs} runs across {total_targets} source targets.",
        "",
        f"The raw ClimateBERT comparison file, `{RESULTS_DIR / 'climatebert_results.json'}`, contains {cb_runs} remote ClimateBERT runs. That is much smaller than the tone-result dataset, so it should be treated as a sanity-check sample rather than a full ground-truth evaluation.",
        "",
        "## What The Fields Mean",
        "",
        "- `tone` describes the disclosure posture: `commitment` is a promise or future intent, `action` is an activity being performed, `outcome` is an achieved/measured result, and `none` means no meaningful ESG tone was found.",
        "- `aspect` is the ESG topic assigned by the extraction step, such as `climate-detection`, `governance`, or `environmental-claims`.",
        "- `labels` are ClimateBERT-style task labels attached to the extracted record. They are useful for checking whether the text looks climate-related, specific, a commitment, an environmental claim, or a governance/social item.",
        "- ClimateBERT itself is not a direct tone classifier. It is better interpreted as external evidence about climate relevance, specificity, environmental claims, TCFD category, sentiment, commitment, and related climate tasks.",
        "",
        "## Main Findings",
        "",
        f"- The dominant non-missing tone is `{dominant_tone}` with {dominant_tone_count} records.",
        f"- Missing/blank tone values appear in {missing_tone} records, which means part of the extraction output still needs cleanup before it can support strong accuracy claims.",
        f"- ESG pillar distribution is: {', '.join(f'`{k}`={v}' for k, v in esg_counts.items())}.",
        f"- The most frequent ClimateBERT-style labels in the extracted records are: {', '.join(f'`{k}`={v}' for k, v in top_labels.items())}.",
        "",
        "## Comparison Interpretation",
        "",
        "The practical comparison is: does the tone assigned by the extraction layer make sense given the ClimateBERT-style climate labels?",
        "",
        "- `commitment` should often co-occur with labels such as `climate-commitment`, `netzero-reduction`, `climate-action`, or `environmental-claims` when the text describes targets, plans, or pledges.",
        "- `action` should often co-occur with operational or governance labels when the text describes concrete programs, controls, training, implementation, procurement, or financing activity.",
        "- `outcome` should be strongest when the text contains result language, metrics, reductions, achievements, or reported performance.",
        "- `none` should mainly pair with non-climate, generic, or empty labels. If `none` frequently co-occurs with climate-specific labels, that is a likely false negative in tone extraction.",
        "",
        "In the current data:",
        "",
        *tone_label_notes,
        "",
        "Because the available ClimateBERT remote-run file has only three inputs, it cannot establish full ground truth. For a thesis or benchmark section, describe it as a validation lens unless you manually label the same records and use those labels as ground truth.",
        "",
        "A stricter ground-truth workflow would require one row per text with: `text`, `tone_pred`, `tone_ground_truth`, and the ClimateBERT model outputs for that exact same text. The current files are close to that workflow, but they are not yet a full one-to-one benchmark.",
        "",
        "## ClimateBERT Remote Run Notes",
        "",
        f"The parsed ClimateBERT remote sample contains {len(cb_df)} model-level rows from {cb_models} models. {cb_errors} rows are model errors, mostly from models whose Hugging Face configs were not recognized in the remote space.",
    ]

    if not climate_top.empty:
        lines.extend(
            [
                "",
                "Top labels from successful ClimateBERT sample runs:",
                "",
            ]
        )
        for _, row in climate_top.head(12).iterrows():
            lines.append(f"- `{row['model']}` -> `{row['top_label']}` ({row['top_score']:.2f})")

    lines.extend(
        [
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for chart in chart_links:
        lines.append(f"- `{chart}`")
    lines.extend(
        [
            "- `results/visualizations/tone_records_flat.csv`",
            "- `results/visualizations/climatebert_remote_flat.csv`",
            "- `results/visualizations/tone_climatebert_label_crosstab.csv`",
            "",
            "## Recommended Next Step",
            "",
            "For a true accuracy comparison, run ClimateBERT over the same `text` records in `esg_records.json`, then add a manual ground-truth tone column for a stratified sample. After that, compute a confusion matrix for `tone_pred` versus `tone_ground_truth` and use ClimateBERT labels as explanatory variables for disagreements.",
            "",
        ]
    )

    DOC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    df = load_esg_records()
    cb_df = load_climatebert_rows()

    df.to_csv(OUT_DIR / "tone_records_flat.csv", index=False)
    cb_df.to_csv(OUT_DIR / "climatebert_remote_flat.csv", index=False)

    tone_counts = df["tone"].value_counts()
    save_bar(
        tone_counts,
        "Existing Tone Results",
        "Record count",
        "Tone",
        OUT_DIR / "tone_distribution.png",
        "#2f6f73",
    )

    tone_esg = save_stacked_tone_esg(df, OUT_DIR / "esg_by_tone.png")
    tone_esg.to_csv(OUT_DIR / "tone_esg_crosstab.csv")

    exploded = df.explode("labels").copy()
    exploded["label_family"] = exploded["labels"].map(climatebert_label_family)
    label_tone = pd.crosstab(exploded["tone"], exploded["label_family"])
    label_tone.to_csv(OUT_DIR / "tone_climatebert_label_crosstab.csv")
    keep = label_tone.sum().sort_values(ascending=False).head(12).index.tolist()
    save_heatmap(
        label_tone[keep],
        "Tone vs ClimateBERT-Style Labels",
        OUT_DIR / "climatebert_label_by_tone.png",
        figsize=(12, 5.8),
    )

    top_aspects = df["aspect"].value_counts().head(12).index.tolist()
    aspect_tone = pd.crosstab(df[df["aspect"].isin(top_aspects)]["aspect"], df["tone"])
    aspect_tone.to_csv(OUT_DIR / "aspect_tone_crosstab.csv")
    save_heatmap(
        aspect_tone,
        "Top Aspects by Tone",
        OUT_DIR / "aspect_by_tone_heatmap.png",
        figsize=(9.5, 7),
    )

    failure_counts = load_csv(WORKFLOW_DIR / "failure_mode_counts.csv")
    if failure_counts.empty:
        failure_counts = load_csv(REVISION_DIR / "failure_mode_counts.csv")
    save_failure_pareto(failure_counts, OUT_DIR / "failure_mode_pareto.png")
    save_failure_pie(failure_counts, OUT_DIR / "failure_mode_pie.png")

    model_stability = load_csv(WORKFLOW_DIR / "model_stability_summary.csv")
    save_model_tradeoff(model_stability, OUT_DIR / "model_tradeoff_scatter.png")

    prompt_stability = load_csv(WORKFLOW_DIR / "prompt_stability_summary.csv")
    save_prompt_strategy(prompt_stability, OUT_DIR / "prompt_strategy_comparison.png")

    save_information_density(df, OUT_DIR / "information_density_by_tone.png")
    save_soft_language_ratio(df, OUT_DIR / "soft_language_ratio_by_tone.png")

    greenwashing = load_csv(WORKFLOW_DIR / "greenwashing_index_by_company.csv")
    save_greenwashing_gap(greenwashing, OUT_DIR / "greenwashing_gap_scatter.png")
    save_commitment_outcome_ratio(df, OUT_DIR / "commitment_outcome_ratio.png")

    climate_top = pd.DataFrame()
    if not cb_df.empty and cb_df["score"].notna().any():
        climate_scored = cb_df.dropna(subset=["score"]).copy()
        climate_scored["score"] = pd.to_numeric(climate_scored["score"], errors="coerce")
        climate_top = (
            climate_scored.sort_values(["run_idx", "model", "score"], ascending=[True, True, False])
            .groupby(["run_idx", "model"], as_index=False)
            .first()
            .rename(columns={"label": "top_label", "score": "top_score"})
        )
        climate_top.to_csv(OUT_DIR / "climatebert_remote_top_labels.csv", index=False)
        pivot = climate_top.pivot_table(index="model", columns="top_label", values="top_score", aggfunc="mean")
        save_heatmap(
            pivot.fillna(0),
            "ClimateBERT Remote Sample: Top Scores",
            OUT_DIR / "climatebert_remote_top_scores.png",
            figsize=(12, 7),
        )

    write_doc(df, cb_df, label_tone, tone_esg, climate_top)

    summary = {
        "tone_records": len(df),
        "tone_runs": int(df["run_idx"].nunique()),
        "tone_targets": int(df["target"].nunique()),
        "climatebert_runs": int(cb_df["run_idx"].nunique()) if not cb_df.empty else 0,
        "outputs": sorted(path.name for path in OUT_DIR.iterdir()),
        "doc": str(DOC_PATH.relative_to(ROOT)),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
