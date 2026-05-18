from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Thesis Systematic Workflow Dashboard", layout="wide")

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
VIS = RESULTS / "visualizations"
REVISION = RESULTS / "revision_analysis"
WORKFLOW_PATH = ROOT / "documentation" / "thesis_systematic_workflow.md"
OUTPUT_DIR = RESULTS / "thesis_workflow_dashboard"


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(file_path)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_json(path: str) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return None
    try:
        return json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_jsonl(path: str, limit: int | None = None) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if limit is not None and len(rows) >= limit:
            break
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def workflow_rq_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rq": "RQ1",
                "stage": "PDF-to-structured ESG",
                "implemented_modules": 4,
                "artifact_groups": 5,
                "status": "active",
            },
            {
                "rq": "RQ2",
                "stage": "Aspect/pillar/sentiment/tone schema",
                "implemented_modules": 3,
                "artifact_groups": 4,
                "status": "active",
            },
            {
                "rq": "RQ3",
                "stage": "Tone vs ClimateBERT",
                "implemented_modules": 3,
                "artifact_groups": 3,
                "status": "active",
            },
            {
                "rq": "RQ4",
                "stage": "Diagnostics",
                "implemented_modules": 3,
                "artifact_groups": 4,
                "status": "active",
            },
            {
                "rq": "RQ5",
                "stage": "Reproducibility",
                "implemented_modules": 3,
                "artifact_groups": 4,
                "status": "active",
            },
            {
                "rq": "RQ6",
                "stage": "Stability",
                "implemented_modules": 3,
                "artifact_groups": 3,
                "status": "active",
            },
        ]
    )


def artifact_inventory() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in RESULTS.rglob("*"):
        if not path.is_file() or path.name == ".DS_Store":
            continue
        rel = path.relative_to(ROOT)
        if "background_llm_jobs" in rel.parts:
            group = "LLM background jobs"
        elif "ground_truth_background_jobs" in rel.parts:
            group = "Ground-truth background jobs"
        elif "revision_analysis" in rel.parts:
            group = "Revision analysis"
        elif "visualizations" in rel.parts:
            group = "Visualizations"
        elif "api_reader" in rel.parts:
            group = "API snapshots"
        else:
            group = "Core results"
        rows.append(
            {
                "path": str(rel),
                "group": group,
                "extension": path.suffix.lower().lstrip(".") or "none",
                "size_kb": round(path.stat().st_size / 1024, 2),
                "modified": pd.to_datetime(path.stat().st_mtime, unit="s"),
            }
        )
    return pd.DataFrame(rows)


def job_status_frame(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return pd.DataFrame()
    for job_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        status = load_json(str(job_dir / "status.json"))
        config = load_json(str(job_dir / "config.json"))
        if not isinstance(status, dict):
            status = {}
        if not isinstance(config, dict):
            config = {}
        total = int(status.get("total") or 0)
        completed = int(status.get("completed") or 0)
        rows.append(
            {
                "job_id": job_dir.name,
                "status": clean(status.get("status") or "unknown"),
                "completed": completed,
                "total": total,
                "failed": int(status.get("failed") or 0),
                "skipped": int(status.get("skipped") or 0),
                "progress_pct": round(completed / total * 100, 1) if total else 0.0,
                "document": clean(status.get("document") or config.get("document")),
                "updated_at": clean(status.get("updated_at")),
            }
        )
    return pd.DataFrame(rows)


def t2_flat_frame() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in load_jsonl(str(RESULTS / "t2_results.jsonl")):
        hybrid = record.get("hybrid") if isinstance(record.get("hybrid"), dict) else {}
        rule = record.get("rule_based") if isinstance(record.get("rule_based"), dict) else {}
        predictions = hybrid.get("predictions") if isinstance(hybrid.get("predictions"), list) else []
        metrics = hybrid.get("metrics") if isinstance(hybrid.get("metrics"), list) else []
        metric_map = {
            clean(item.get("Metric")): item.get("Value")
            for item in metrics
            if isinstance(item, dict)
        }
        if not predictions:
            rows.append(
                {
                    "label": clean(record.get("label")),
                    "rule_tone": clean(rule.get("tone")),
                    "hybrid_error": clean(hybrid.get("error")),
                    "tone_pred": "",
                    "sentiment_pred": "",
                    "ontology_alignment": None,
                    "greenwashing_index": pd.to_numeric(metric_map.get("Greenwashing Index"), errors="coerce"),
                }
            )
            continue
        for pred in predictions:
            if not isinstance(pred, dict):
                continue
            rows.append(
                {
                    "label": clean(record.get("label")),
                    "rule_tone": clean(rule.get("tone")),
                    "hybrid_error": clean(hybrid.get("error")),
                    "tone_pred": clean(pred.get("Tone_Pred")),
                    "sentiment_pred": clean(pred.get("Sentiment_Pred")),
                    "ontology_alignment": pd.to_numeric(pred.get("Ontology_Alignment"), errors="coerce"),
                    "greenwashing_index": pd.to_numeric(metric_map.get("Greenwashing Index"), errors="coerce"),
                    "ontology_path": clean(pred.get("Ontology_Path")),
                }
            )
    return pd.DataFrame(rows)


def count_df(df: pd.DataFrame, col: str, top_n: int | None = None) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[col, "count"])
    out = df[col].map(clean).replace("", "missing").value_counts().rename_axis(col).reset_index(name="count")
    return out.head(top_n) if top_n else out


def bar_chart(df: pd.DataFrame, x: str, y: str = "count", color: str | None = None, title: str = "", height: int = 320) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(f"{x}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-25, labelLimit=180)),
            y=alt.Y(f"{y}:Q", title=y.replace("_", " ").title()),
            color=alt.Color(f"{color}:N") if color else alt.value("#217c7e"),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def hbar_chart(df: pd.DataFrame, y: str, x: str = "count", color: str | None = None, title: str = "", height: int = 360) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No rows available for this chart.")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=2, cornerRadiusBottomRight=2)
        .encode(
            x=alt.X(f"{x}:Q", title=x.replace("_", " ").title()),
            y=alt.Y(f"{y}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=280)),
            color=alt.Color(f"{color}:N") if color else alt.value("#2563eb"),
            tooltip=list(df.columns),
        )
        .properties(title=title, height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def heatmap_from_crosstab(df: pd.DataFrame, row_col: str, title: str) -> None:
    if df.empty or row_col not in df.columns:
        st.info("No crosstab data available.")
        return
    melted = df.melt(id_vars=[row_col], var_name="column", value_name="count")
    chart = (
        alt.Chart(melted)
        .mark_rect()
        .encode(
            x=alt.X("column:N", title=None, axis=alt.Axis(labelAngle=-35, labelLimit=160)),
            y=alt.Y(f"{row_col}:N", title=None),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
            tooltip=[row_col, "column", "count"],
        )
        .properties(title=title, height=320)
    )
    text = alt.Chart(melted).mark_text(fontSize=11).encode(
        x="column:N",
        y=f"{row_col}:N",
        text="count:Q",
        color=alt.condition(alt.datum.count > melted["count"].max() * 0.55, alt.value("white"), alt.value("#17202a")),
    )
    st.altair_chart(chart + text, use_container_width=True)


def numeric_hist(df: pd.DataFrame, col: str, title: str) -> None:
    if df.empty or col not in df.columns or df[col].dropna().empty:
        st.info("No numeric values available.")
        return
    chart = (
        alt.Chart(df.dropna(subset=[col]))
        .mark_bar()
        .encode(
            x=alt.X(f"{col}:Q", bin=alt.Bin(maxbins=30), title=col.replace("_", " ").title()),
            y=alt.Y("count():Q", title="Rows"),
            tooltip=[alt.Tooltip(f"{col}:Q", bin=True), alt.Tooltip("count():Q")],
        )
        .properties(title=title, height=300)
    )
    st.altair_chart(chart, use_container_width=True)


def show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_column_width=True)
    else:
        st.info(f"Missing image: `{path.relative_to(ROOT)}`")


def pct(value: Any) -> str:
    number = pd.to_numeric(value, errors="coerce")
    if pd.isna(number):
        return "n/a"
    return f"{number * 100:.1f}%"


def num(value: Any, digits: int = 2) -> str:
    number = pd.to_numeric(value, errors="coerce")
    if pd.isna(number):
        return "n/a"
    return f"{number:.{digits}f}"


def top_value(df: pd.DataFrame, col: str) -> str:
    counts = count_df(df, col, 1)
    if counts.empty:
        return "n/a"
    return f"{counts.iloc[0][col]} ({int(counts.iloc[0]['count'])})"


def first_metric(df: pd.DataFrame, col: str) -> Any:
    if df.empty or col not in df.columns:
        return None
    return df.iloc[0][col]


def df_to_markdown(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "_No rows available._"
    return df.head(max_rows).to_markdown(index=False)


def copy_existing_images() -> list[dict[str, str]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for source in [
        VIS / "tone_distribution.png",
        VIS / "esg_by_tone.png",
        VIS / "aspect_by_tone_heatmap.png",
        VIS / "climatebert_label_by_tone.png",
        VIS / "climatebert_remote_top_scores.png",
    ]:
        if not source.exists():
            continue
        target = OUTPUT_DIR / source.name
        target.write_bytes(source.read_bytes())
        rows.append({"name": source.name, "source": str(source.relative_to(ROOT)), "saved_to": str(target.relative_to(ROOT))})
    return rows


def rq_report_sections(
    tone_records: pd.DataFrame,
    tone_esg: pd.DataFrame,
    tone_climatebert: pd.DataFrame,
    model_stability: pd.DataFrame,
    prompt_stability: pd.DataFrame,
    failure_counts: pd.DataFrame,
    ocr_summary: pd.DataFrame,
    ontology_coverage: pd.DataFrame,
    greenwashing: pd.DataFrame,
    agreement: pd.DataFrame,
    seed: pd.DataFrame,
    t2_flat: pd.DataFrame,
    inventory: pd.DataFrame,
    llm_jobs: pd.DataFrame,
    gt_jobs: pd.DataFrame,
) -> list[dict[str, Any]]:
    done_ocr = int((ocr_summary["status"].map(clean) == "done").sum()) if "status" in ocr_summary.columns else 0
    total_pages = int(pd.to_numeric(ocr_summary.get("pages", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()) if not ocr_summary.empty else 0
    mapped_aspects = int(ontology_coverage["mapped_to_ontology"].fillna(False).astype(bool).sum()) if "mapped_to_ontology" in ontology_coverage.columns else 0
    climate_n = first_metric(agreement, "n")
    best_model = ""
    if not model_stability.empty and "json_parse_success_rate" in model_stability.columns:
        best_model = clean(model_stability.sort_values(["json_parse_success_rate", "schema_drift_rate"], ascending=[False, True]).iloc[0].get("model"))
    worst_prompt = ""
    if not prompt_stability.empty and "missing_tone_rate" in prompt_stability.columns:
        worst_prompt = clean(prompt_stability.sort_values("missing_tone_rate", ascending=False).iloc[0].get("prompt"))

    return [
        {
            "rq": "RQ1",
            "title": "PDF-to-structured ESG evidence",
            "graph": "OCR processing status and largest documents by page count",
            "results": f"{done_ocr}/{len(ocr_summary)} OCR documents are marked done, covering about {total_pages:,} pages. The artifact inventory and background job tables show whether PDF-to-record processing is reproducible outside the visible browser session.",
            "interpretation": "This supports the ingestion layer of the thesis: sustainability reports can be converted into auditable intermediate artifacts before ABSA or ClimateBERT comparison begins.",
            "baseline": "Needed baseline: document-level OCR completeness from a trusted extractor such as PyMuPDF/pdfplumber, page-count parity against the original PDFs, and a small manually checked sample of page text quality.",
            "discussion": "The current evidence is operational rather than semantic. It proves that the pipeline can process large reports, but the thesis should still report OCR error categories such as scanned pages, table loss, missing Indonesian characters, and duplicated headers.",
            "conclusion": "RQ1 is implementation-ready; the next validation gap is a page/text quality baseline, not another dashboard.",
        },
        {
            "rq": "RQ2",
            "title": "Aspect, ESG pillar, sentiment, and tone schema",
            "graph": "Tone distribution, ESG pillar distribution, tone x ESG heatmap, and T2 hybrid outputs",
            "results": f"The flat tone table contains {len(tone_records):,} extracted records. The most common tone is {top_value(tone_records, 'tone')}; the most common ESG pillar is {top_value(tone_records, 'esg')}. T2 contains {len(t2_flat):,} parsed hybrid prediction rows.",
            "interpretation": "The generated schema separates topic, ESG pillar, sentiment polarity, and disclosure tone, which is useful because ESG text can be positive in sentiment while still being only a promise or commitment.",
            "baseline": "Needed baseline: a human-coded annotation set for aspect, ESG pillar, sentiment, and tone; inter-annotator agreement; and a simple keyword/rule baseline for commitment/action/outcome labels.",
            "discussion": "The current schema is broad enough for thesis experiments, but the human label loop should decide where 'commitment' ends and 'action' begins, especially for Indonesian modal verbs and sustainability boilerplate.",
            "conclusion": "RQ2 has usable model outputs and a pilot seed, but formal claims need human validation and agreement statistics.",
        },
        {
            "rq": "RQ3",
            "title": "Tone vs ClimateBERT/proxy labels",
            "graph": "Tone x ClimateBERT/proxy label crosstab and ClimateBERT agreement metrics",
            "results": f"The agreement table covers {int(climate_n) if climate_n else 'n/a'} records. Tone commitment vs climate-commitment proxy agreement is {pct(first_metric(agreement, 'percent_agreement'))}, with Cohen kappa {num(first_metric(agreement, 'cohen_kappa'), 3)}. Tone commitment rate is {pct(first_metric(agreement, 'tone_commitment_rate'))}; climate commitment label rate is {pct(first_metric(agreement, 'climate_commitment_label_rate'))}.",
            "interpretation": "The relatively high agreement suggests that disclosure tone and climate label signals overlap, but they are not identical constructs. That distinction is valuable for the thesis because ClimateBERT-style labels identify climate content while tone labels describe claim maturity.",
            "baseline": "Needed baseline: the original ClimateBERT classifier outputs on the same records, a majority-class baseline, a keyword climate-commitment baseline, and a confusion matrix against manually reviewed climate/tone labels.",
            "discussion": "The key thesis discussion is construct validity. A climate-commitment label can coexist with commitment tone, action tone, or outcome tone; disagreement cases should be inspected as evidence of why ABSA tone adds value beyond climate-topic classification.",
            "conclusion": "RQ3 already has publishable-shaped evidence, but it needs an explicit baseline table and disagreement examples before being treated as final experimental evidence.",
        },
        {
            "rq": "RQ4",
            "title": "Diagnostics and extraction weaknesses",
            "graph": "Failure-mode counts and ontology coverage by aspect",
            "results": f"The failure-mode table contains {len(failure_counts):,} mode-tone rows. Ontology coverage tracks {len(ontology_coverage):,} aspects, with {mapped_aspects:,} mapped to ontology paths.",
            "interpretation": "Diagnostics expose where the pipeline is weak: bilingual/code-switched text, hedged claims, missing tone fields, ontology gaps, and schema drift.",
            "baseline": "Needed baseline: an error taxonomy coded on a fixed sample, expected failure rates for a rule-only extractor, and an ontology gold map for the most frequent ESG aspects.",
            "discussion": "This section should turn model failure into thesis contribution: every recurring failure mode can become either a schema refinement, a prompt revision, or a human-review rule.",
            "conclusion": "RQ4 is strong as an audit chapter if the dashboard examples are paired with manually inspected representative errors.",
        },
        {
            "rq": "RQ5",
            "title": "Reproducibility, documentation, and visualization",
            "graph": "Artifact inventory, background job status, and exported dashboard report files",
            "results": f"The dashboard currently indexes {len(inventory):,} result artifacts, {len(llm_jobs):,} LLM background jobs, and {len(gt_jobs):,} ground-truth background jobs.",
            "interpretation": "The workflow is no longer only an interactive Streamlit view; it now has saved report artifacts that can be attached to the thesis workflow page and regenerated as results change.",
            "baseline": "Needed baseline: a manifest of expected output files for each pipeline stage, checksums or timestamps, and a reproduce-from-clean-run checklist.",
            "discussion": "Reproducibility depends on stable file paths, cached API/model metadata, and background execution logs. The report should distinguish generated evidence from manually edited thesis interpretation.",
            "conclusion": "RQ5 is supported by the saved dashboard output and workflow integration; the remaining work is formal run provenance.",
        },
        {
            "rq": "RQ6",
            "title": "Cross-model and cross-prompt stability",
            "graph": "Model parse success, schema drift, prompt field completion, and missing-tone rate",
            "results": f"Model stability covers {len(model_stability):,} models and prompt stability covers {len(prompt_stability):,} prompts. The currently strongest parse-success model is {best_model or 'n/a'}; the highest missing-tone prompt is {worst_prompt or 'n/a'}.",
            "interpretation": "The stability results show that output validity is not only a model-quality problem; prompt format and field requirements strongly affect whether the pipeline produces thesis-usable records.",
            "baseline": "Needed baseline: deterministic rule extraction, repeated runs with fixed seeds/temperature, a smaller local model baseline, and per-field agreement rates across prompts.",
            "discussion": "The thesis can frame stability as an engineering and research validity condition. A high-performing model is not enough if it drifts schema or omits tone under a different prompt.",
            "conclusion": "RQ6 has the clearest dashboard evidence for model/prompt comparison; it should be extended with repeated-run confidence intervals and field-level agreement.",
        },
    ]


def save_dashboard_outputs(
    sections: list[dict[str, Any]],
    tables: dict[str, pd.DataFrame],
    metrics_summary: dict[str, Any],
) -> tuple[Path, Path, Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        if not df.empty:
            df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
    image_rows = copy_existing_images()
    (OUTPUT_DIR / "dashboard_metrics.json").write_text(json.dumps(metrics_summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    (OUTPUT_DIR / "dashboard_image_manifest.json").write_text(json.dumps(image_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    report_lines = [
        "# Thesis Systematic Workflow Dashboard Report",
        "",
        f"- Results root: `{RESULTS}`",
        f"- Saved output root: `{OUTPUT_DIR}`",
        f"- Tone records: {metrics_summary.get('tone_records', 0):,}",
        f"- T2 rows: {metrics_summary.get('t2_rows', 0):,}",
        f"- Pilot labels: {metrics_summary.get('pilot_labels', 0):,}",
        f"- Result artifacts: {metrics_summary.get('artifacts', 0):,}",
        "",
        "## Saved Graph Attachments",
        "",
    ]
    if image_rows:
        for row in image_rows:
            report_lines.append(f"- `{row['name']}`: `{row['saved_to']}`")
    else:
        report_lines.append("_No existing PNG graph attachments were found._")
    report_lines.append("")

    for section in sections:
        report_lines.extend(
            [
                f"## {section['rq']} {section['title']}",
                "",
                f"**{section['rq']} results.** {section['results']}",
                "",
                f"**{section['rq']} graph.** {section['graph']}",
                "",
                f"**{section['rq']} interpretation analysis.** {section['interpretation']}",
                "",
                f"**{section['rq']} baseline needed.** {section['baseline']}",
                "",
                f"**{section['rq']} discussion.** {section['discussion']}",
                "",
                f"**{section['rq']} conclusion.** {section['conclusion']}",
                "",
            ]
        )

    report_path = OUTPUT_DIR / "thesis_dashboard_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    sections_path = OUTPUT_DIR / "rq_report_sections.json"
    sections_path.write_text(json.dumps(sections, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return report_path, sections_path, OUTPUT_DIR / "dashboard_metrics.json"


def render_report_section(section: dict[str, Any]) -> None:
    st.markdown(f"### {section['rq']} results")
    st.write(section["results"])
    st.markdown(f"### {section['rq']} graph")
    st.write(section["graph"])
    st.markdown(f"### {section['rq']} interpretation analysis")
    st.write(section["interpretation"])
    st.markdown(f"### {section['rq']} baseline needed")
    st.info(section["baseline"])
    st.markdown(f"### {section['rq']} discussion")
    st.write(section["discussion"])
    st.markdown(f"### {section['rq']} conclusion")
    st.success(section["conclusion"])


st.title("Thesis Systematic Workflow Dashboard")
st.caption("Graphs generated from the current thesis workflow outputs, revision analysis files, visualizations, JSONL runs, and background job status.")

tone_records = load_csv(str(VIS / "tone_records_flat.csv"))
tone_esg = load_csv(str(VIS / "tone_esg_crosstab.csv"))
tone_climatebert = load_csv(str(VIS / "tone_climatebert_label_crosstab.csv"))
model_stability = load_csv(str(REVISION / "model_stability_summary.csv"))
prompt_stability = load_csv(str(REVISION / "prompt_stability_summary.csv"))
failure_counts = load_csv(str(REVISION / "failure_mode_counts.csv"))
ocr_summary = load_csv(str(REVISION / "ocr_processing_summary.csv"))
ontology_coverage = load_csv(str(REVISION / "ontology_coverage.csv"))
greenwashing = load_csv(str(REVISION / "greenwashing_index_by_company.csv"))
agreement = load_csv(str(REVISION / "climatebert_proxy_agreement_summary.csv"))
seed = load_csv(str(REVISION / "pilot_ground_truth_seed.csv"))
t2_flat = t2_flat_frame()
inventory = artifact_inventory()
llm_jobs = job_status_frame(RESULTS / "background_llm_jobs")
gt_jobs = job_status_frame(RESULTS / "ground_truth_background_jobs")
rq_df = workflow_rq_df()
rq_sections = rq_report_sections(
    tone_records,
    tone_esg,
    tone_climatebert,
    model_stability,
    prompt_stability,
    failure_counts,
    ocr_summary,
    ontology_coverage,
    greenwashing,
    agreement,
    seed,
    t2_flat,
    inventory,
    llm_jobs,
    gt_jobs,
)
metrics_summary = {
    "workflow_rqs": len(rq_df),
    "tone_records": len(tone_records),
    "t2_rows": len(t2_flat),
    "pilot_labels": len(seed),
    "ocr_docs": len(ocr_summary),
    "artifacts": len(inventory),
    "llm_jobs": len(llm_jobs),
    "ground_truth_jobs": len(gt_jobs),
    "climatebert_percent_agreement": first_metric(agreement, "percent_agreement"),
    "climatebert_cohen_kappa": first_metric(agreement, "cohen_kappa"),
}
report_path, sections_path, metrics_path = save_dashboard_outputs(
    rq_sections,
    {
        "workflow_rq_coverage": rq_df,
        "artifact_inventory": inventory,
        "tone_records_flat": tone_records,
        "tone_esg_crosstab": tone_esg,
        "tone_climatebert_label_crosstab": tone_climatebert,
        "t2_flat_outputs": t2_flat,
        "model_stability_summary": model_stability,
        "prompt_stability_summary": prompt_stability,
        "failure_mode_counts": failure_counts,
        "ocr_processing_summary": ocr_summary,
        "ontology_coverage": ontology_coverage,
        "greenwashing_index_by_company": greenwashing,
        "climatebert_proxy_agreement_summary": agreement,
        "pilot_ground_truth_seed": seed,
        "llm_background_jobs": llm_jobs,
        "ground_truth_background_jobs": gt_jobs,
    },
    metrics_summary,
)

with st.sidebar:
    st.header("Dashboard")
    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"Workflow: `{WORKFLOW_PATH}`")
    st.markdown(f"Results: `{RESULTS}`")
    st.markdown(f"Saved report: `{report_path}`")

metrics = st.columns(8)
metrics[0].metric("Workflow RQs", f"{len(rq_df):,}")
metrics[1].metric("Tone records", f"{len(tone_records):,}")
metrics[2].metric("T2 rows", f"{len(t2_flat):,}")
metrics[3].metric("Pilot labels", f"{len(seed):,}")
metrics[4].metric("OCR docs", f"{len(ocr_summary):,}")
metrics[5].metric("Artifacts", f"{len(inventory):,}")
metrics[6].metric("LLM jobs", f"{len(llm_jobs):,}")
metrics[7].metric("GT jobs", f"{len(gt_jobs):,}")

tabs = st.tabs(
    [
        "Workflow Coverage",
        "Thesis Report",
        "Pipeline Outputs",
        "Diagnostics",
        "Stability",
        "Ground Truth",
        "Artifacts & Images",
    ]
)

with tabs[0]:
    st.subheader("Research-question implementation coverage")
    c1, c2 = st.columns(2)
    with c1:
        hbar_chart(rq_df, "stage", "implemented_modules", color="rq", title="Implemented modules per thesis workflow stage")
    with c2:
        hbar_chart(rq_df, "stage", "artifact_groups", color="rq", title="Generated artifact groups per stage")
    st.dataframe(rq_df, use_container_width=True, hide_index=True)

    st.subheader("Current artifact inventory")
    if inventory.empty:
        st.warning("No result artifacts found.")
    else:
        c3, c4 = st.columns(2)
        with c3:
            bar_chart(count_df(inventory, "group"), "group", title="Artifacts by result group")
        with c4:
            bar_chart(count_df(inventory, "extension"), "extension", title="Artifacts by file type")

with tabs[1]:
    st.subheader("Saved thesis dashboard output")
    st.success(f"Dashboard report saved to `{report_path}`")
    st.caption(f"Structured RQ sections: `{sections_path}`")
    st.caption(f"Metrics summary: `{metrics_path}`")
    report_text = report_path.read_text(encoding="utf-8", errors="ignore") if report_path.exists() else ""
    st.download_button(
        "Download thesis dashboard report Markdown",
        report_text.encode("utf-8"),
        "thesis_dashboard_report.md",
        "text/markdown",
        use_container_width=True,
    )

    selected_rq = st.selectbox(
        "Research question",
        [f"{section['rq']} - {section['title']}" for section in rq_sections],
        key="thesis_report_rq_selector",
    )
    section = rq_sections[[f"{item['rq']} - {item['title']}" for item in rq_sections].index(selected_rq)]
    render_report_section(section)

    st.divider()
    st.subheader("Graphs attached to the report")
    if section["rq"] == "RQ1":
        c1, c2 = st.columns(2)
        with c1:
            bar_chart(count_df(ocr_summary, "status"), "status", title="RQ1 OCR processing status")
        with c2:
            if not ocr_summary.empty and "pages" in ocr_summary.columns:
                hbar_chart(ocr_summary.sort_values("pages", ascending=False).head(10), "document", "pages", title="RQ1 largest processed reports")
    elif section["rq"] == "RQ2":
        c1, c2 = st.columns(2)
        with c1:
            bar_chart(count_df(tone_records, "tone"), "tone", title="RQ2 tone distribution")
        with c2:
            bar_chart(count_df(tone_records, "esg"), "esg", title="RQ2 ESG pillar distribution")
        heatmap_from_crosstab(tone_esg, "tone", "RQ2 tone x ESG pillar")
    elif section["rq"] == "RQ3":
        heatmap_from_crosstab(tone_climatebert, "tone", "RQ3 tone x ClimateBERT/proxy label")
        if not agreement.empty:
            agree_long = agreement.melt(id_vars=["comparison"], var_name="metric", value_name="value")
            numeric = agree_long[pd.to_numeric(agree_long["value"], errors="coerce").notna()].copy()
            numeric["value"] = pd.to_numeric(numeric["value"], errors="coerce")
            bar_chart(numeric[numeric["metric"].ne("n")], "metric", "value", title="RQ3 agreement metrics")
    elif section["rq"] == "RQ4":
        c1, c2 = st.columns(2)
        with c1:
            failure_view = failure_counts.copy()
            if not failure_view.empty:
                failure_view["mode_tone"] = failure_view["mode"].map(clean) + " | " + failure_view["tone_pred"].map(clean)
            hbar_chart(failure_view.sort_values("count", ascending=False).head(20), "mode_tone", "count", title="RQ4 failure modes")
        with c2:
            hbar_chart(ontology_coverage.sort_values("records", ascending=False).head(20), "aspect", "records", color="mapped_to_ontology", title="RQ4 ontology coverage")
    elif section["rq"] == "RQ5":
        c1, c2 = st.columns(2)
        with c1:
            bar_chart(count_df(inventory, "group"), "group", title="RQ5 saved artifacts by group")
        with c2:
            bar_chart(count_df(llm_jobs, "status"), "status", title="RQ5 LLM background jobs")
    elif section["rq"] == "RQ6":
        c1, c2 = st.columns(2)
        with c1:
            hbar_chart(model_stability, "model", "schema_drift_rate", title="RQ6 schema drift by model")
        with c2:
            hbar_chart(prompt_stability, "prompt", "missing_tone_rate", title="RQ6 missing tone by prompt")

with tabs[2]:
    st.subheader("Tone-aware ESG extraction results")
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(count_df(tone_records, "tone"), "tone", title="Extracted tone distribution")
    with c2:
        bar_chart(count_df(tone_records, "esg"), "esg", title="Extracted ESG pillar distribution")
    heatmap_from_crosstab(tone_esg, "tone", "Tone x ESG pillar crosstab")
    heatmap_from_crosstab(tone_climatebert, "tone", "Tone x ClimateBERT/proxy label crosstab")

    st.subheader("T2 rule/hybrid outputs")
    c3, c4 = st.columns(2)
    with c3:
        bar_chart(count_df(t2_flat, "tone_pred"), "tone_pred", title="T2 hybrid tone predictions")
    with c4:
        bar_chart(count_df(t2_flat, "sentiment_pred"), "sentiment_pred", title="T2 hybrid sentiment predictions")
    numeric_hist(t2_flat, "ontology_alignment", "T2 ontology alignment distribution")

with tabs[3]:
    st.subheader("OCR and extraction diagnostics")
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(count_df(ocr_summary, "status"), "status", title="OCR processing status")
    with c2:
        if not ocr_summary.empty and "pages" in ocr_summary.columns:
            top_pages = ocr_summary.sort_values("pages", ascending=False).head(15)
            hbar_chart(top_pages, "document", "pages", title="Largest OCR documents by page count")
        else:
            st.info("No OCR page counts available.")

    st.subheader("Failure modes and ontology coverage")
    c3, c4 = st.columns(2)
    with c3:
        if not failure_counts.empty:
            failure_view = failure_counts.copy()
            failure_view["mode_tone"] = failure_view["mode"].map(clean) + " | " + failure_view["tone_pred"].map(clean)
            hbar_chart(failure_view.sort_values("count", ascending=False).head(20), "mode_tone", "count", title="Top failure modes")
        else:
            st.info("No failure mode counts available.")
    with c4:
        if not ontology_coverage.empty:
            ontology_view = ontology_coverage.sort_values("records", ascending=False).head(20)
            hbar_chart(ontology_view, "aspect", "records", color="mapped_to_ontology", title="Ontology coverage by aspect")
        else:
            st.info("No ontology coverage file available.")

    st.subheader("Greenwashing index")
    if not greenwashing.empty:
        hbar_chart(greenwashing.sort_values("greenwashing_index", ascending=False), "company", "greenwashing_index", title="Greenwashing index by company", height=360)
        st.dataframe(greenwashing, use_container_width=True, hide_index=True)
    else:
        st.info("No greenwashing index file available.")

with tabs[4]:
    st.subheader("Model stability")
    c1, c2 = st.columns(2)
    with c1:
        hbar_chart(model_stability, "model", "json_parse_success_rate", title="JSON parse success by model")
    with c2:
        hbar_chart(model_stability, "model", "schema_drift_rate", title="Schema drift by model")

    st.subheader("Prompt stability")
    c3, c4 = st.columns(2)
    with c3:
        hbar_chart(prompt_stability, "prompt", "field_completion_rate", title="Field completion by prompt")
    with c4:
        hbar_chart(prompt_stability, "prompt", "missing_tone_rate", title="Missing tone rate by prompt")

    st.subheader("ClimateBERT proxy agreement")
    if not agreement.empty:
        agree_long = agreement.melt(id_vars=["comparison"], var_name="metric", value_name="value")
        numeric = agree_long[pd.to_numeric(agree_long["value"], errors="coerce").notna()].copy()
        numeric["value"] = pd.to_numeric(numeric["value"], errors="coerce")
        bar_chart(numeric[numeric["metric"].ne("n")], "metric", "value", title="Agreement metrics", height=300)
        st.dataframe(agreement, use_container_width=True, hide_index=True)
    else:
        st.info("No ClimateBERT proxy agreement summary available.")

with tabs[5]:
    st.subheader("Pilot ground-truth seed")
    c1, c2 = st.columns(2)
    with c1:
        bar_chart(count_df(seed, "review_status"), "review_status", title="Review status")
    with c2:
        bar_chart(count_df(seed, "language"), "language", title="Language distribution")
    c3, c4 = st.columns(2)
    with c3:
        bar_chart(count_df(seed, "tone_pred"), "tone_pred", title="Predicted tone in annotation seed")
    with c4:
        bar_chart(count_df(seed, "silver_tone_ground_truth"), "silver_tone_ground_truth", title="Silver tone labels")
    if not seed.empty:
        flags = []
        for col in ["needs_human_review", "schema_drift", "has_climate_commitment", "has_environmental_claims", "has_climate_d"]:
            if col in seed.columns:
                flags.append({"flag": col, "count": int(seed[col].fillna(False).astype(bool).sum())})
        bar_chart(pd.DataFrame(flags), "flag", title="Annotation seed review flags")
        st.dataframe(seed.head(300), use_container_width=True, hide_index=True, height=420)

    st.subheader("Background job status")
    c5, c6 = st.columns(2)
    with c5:
        st.markdown("**LLM background jobs**")
        bar_chart(count_df(llm_jobs, "status"), "status", title="LLM job status")
        st.dataframe(llm_jobs, use_container_width=True, hide_index=True)
    with c6:
        st.markdown("**Ground-truth background jobs**")
        bar_chart(count_df(gt_jobs, "status"), "status", title="Ground-truth job status")
        st.dataframe(gt_jobs, use_container_width=True, hide_index=True)

with tabs[6]:
    st.subheader("Existing visualization artifacts")
    image_paths = [
        VIS / "tone_distribution.png",
        VIS / "esg_by_tone.png",
        VIS / "aspect_by_tone_heatmap.png",
        VIS / "climatebert_label_by_tone.png",
        VIS / "climatebert_remote_top_scores.png",
    ]
    cols = st.columns(2)
    for index, path in enumerate(image_paths):
        with cols[index % 2]:
            show_image(path, path.name)

    st.subheader("Dashboard image catalog")
    catalog_path = VIS / "streamlit_outputs" / "dashboard_image_catalog.json"
    catalog = load_json(str(catalog_path))
    if isinstance(catalog, list):
        st.dataframe(pd.DataFrame(catalog), use_container_width=True, hide_index=True)
    elif isinstance(catalog, dict):
        st.json(catalog, expanded=False)

    st.subheader("Result artifact table")
    if inventory.empty:
        st.warning("No artifacts found.")
    else:
        st.dataframe(inventory.sort_values("modified", ascending=False), use_container_width=True, hide_index=True, height=520)
