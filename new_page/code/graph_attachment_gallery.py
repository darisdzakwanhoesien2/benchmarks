from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
VIS = RESULTS / "visualizations"
REV = RESULTS / "revision_analysis"
WORKFLOW = RESULTS / "thesis_workflow_dashboard"
GRAPH_DIR = RESULTS / "docx_graph_attachments"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def page_slug(page: str) -> str:
    stem = Path(page).stem
    parts = stem.split("_", 1)
    if len(parts) == 2 and parts[0].isdigit():
        stem = parts[1]
    return f"/{stem}"


def redirect_button(label: str, page: str) -> None:
    st.link_button(label, page_slug(page), use_container_width=True)


def show_image(path: Path, caption: str | None = None) -> None:
    try:
        st.image(str(path), caption=caption, width="stretch")
    except TypeError:
        st.image(str(path), caption=caption, use_column_width=True)


def graph_attachment_manifest() -> pd.DataFrame:
    rows = [
        ("A.1", "Tone distribution", VIS / "tone_distribution.png", "Chapter 4", "RQ2", "tone_records_flat.csv", "pages/6_1_Chapter_4_Implementation_Results.py"),
        ("A.2", "ESG by tone", VIS / "esg_by_tone.png", "Chapter 4", "RQ2", "tone_esg_crosstab.csv", "pages/6_1_Chapter_4_Implementation_Results.py"),
        ("A.3", "Aspect by tone heatmap", VIS / "aspect_by_tone_heatmap.png", "Chapter 4", "RQ2", "aspect_tone_crosstab.csv", "pages/6_1_Chapter_4_Implementation_Results.py"),
        ("A.4", "Tone by ClimateBERT label", VIS / "climatebert_label_by_tone.png", "Chapter 4 / 5", "RQ3", "tone_climatebert_label_crosstab.csv", "pages/6_2_Chapter_5_Discussion.py"),
        ("A.5", "Top-scoring ClimateBERT records", VIS / "climatebert_remote_top_scores.png", "Chapter 5", "RQ3", "climatebert_remote_flat.csv", "pages/6_2_Chapter_5_Discussion.py"),
        ("A.6", "Streamlit overview", VIS / "streamlit_outputs" / "01_overview.png", "Chapter 6", "RQ5", "DOCX evidence summary", "pages/6_4_ch4-6.py"),
        ("A.7", "Per-RQ evidence", VIS / "streamlit_outputs" / "02_per_rq_evidence.png", "Chapter 4 / 6", "RQ1-RQ6", "chapter-to-RQ mapping", "pages/6_4_ch4-6.py"),
        ("A.8", "Benchmark plan", VIS / "streamlit_outputs" / "04_benchmarks.png", "Chapter 4 / 6", "RQ6", "benchmark checklist", "pages/6_4_ch4-6.py"),
        ("A.9", "Evidence matrix", VIS / "streamlit_outputs" / "07_evidence_matrix.png", "Chapter 6", "RQ5", "graph manifest", "pages/6_4_ch4-6.py"),
        ("A.10", "Model parse success benchmark", GRAPH_DIR / "docx_model_parse_success.png", "Chapter 4 / 6", "RQ6", "model_stability_summary.csv", "pages/6_3_Chapter_6_Conclusion.py"),
        ("A.11", "Prompt missing-tone benchmark", GRAPH_DIR / "docx_prompt_missing_tone_rate.png", "Chapter 5 / 6", "RQ6", "prompt_stability_summary.csv", "pages/6_2_Chapter_5_Discussion.py"),
        ("A.12", "Ontology mapped vs novel aspects", GRAPH_DIR / "docx_ontology_mapped_vs_unmapped.png", "Chapter 5 / 6", "RQ4", "ontology_coverage.csv", "pages/6_2_Chapter_5_Discussion.py"),
        ("A.13", "Human annotation agreement", GRAPH_DIR / "docx_human_annotation_agreement.png", "Chapter 5 / 6", "RQ2", "pilot_ground_truth_seed.csv + silver_tone_ground_truth.csv", "pages/1_1_Ground_Truth_Workbench.py"),
        ("A.14", "Repeated LLM runs", GRAPH_DIR / "docx_repeated_llm_runs.png", "Chapter 4 / 6", "RQ6", "model_stability_summary.csv + prompt_stability_summary.csv", "pages/2_3_LLM_Background_Run_Monitor.py"),
        ("A.15", "ClimateBERT baseline", GRAPH_DIR / "docx_climatebert_baseline.png", "Chapter 5 / 6", "RQ3", "climatebert_proxy_agreement_summary.csv + climatebert_proxy_agreement_records.csv", "pages/1_4_ClimateBERT_Record_Batch.py"),
        ("A.16", "Ontology extension", GRAPH_DIR / "docx_ontology_extension_candidates.png", "Chapter 5 / 6", "RQ4", "ontology_coverage.csv", "pages/1_6_Ontology_Path_Viewer.py"),
        ("A.17", "Ground truth scaffold coverage", GRAPH_DIR / "docx_ground_truth_scaffold_coverage.png", "Chapter 4", "RQ2", "tone_records_flat.csv + silver_tone_ground_truth.csv", "pages/1_8_Ground_Truth_Output_Visualizer.py"),
        ("A.18", "Pilot annotation completion", GRAPH_DIR / "docx_pilot_annotation_completion.png", "Chapter 4 / 5", "RQ2", "pilot_ground_truth_seed.csv + pilot_ground_truth_annotations.csv", "pages/1_1_Ground_Truth_Workbench.py"),
        ("A.19", "Ground truth tone comparison", GRAPH_DIR / "docx_ground_truth_tone_comparison.png", "Chapter 4 / 5", "RQ2", "silver_tone_ground_truth.csv + pilot_ground_truth_annotations.csv", "pages/1_3_Ground_Truth_Metrics.py"),
        ("A.20", "ground_truth.py T2 tone outputs", GRAPH_DIR / "docx_ground_truth_t2_outputs.png", "Chapter 4", "RQ2", "t2_flat_outputs.csv + t2_results.jsonl", "pages/1_9_Ground_Truth_Pipeline_Output_Visualizer.py"),
        ("A.21", "PDF x prompt processing matrix", GRAPH_DIR / "docx_pdf_prompt_matrix.png", "Chapter 4 / 6", "RQ1 / RQ6", "esg_records.json + tone_records_flat.csv", "pages/3_0_Thesis_Action_Plan.py"),
    ]
    df = pd.DataFrame(rows, columns=["figure", "title", "path", "chapter", "rq", "source table", "source page"])
    df["exists"] = df["path"].map(lambda path: Path(path).exists())
    df["path"] = df["path"].astype(str)
    return df


def _value_counts(path: Path, column: str, label: str | None = None) -> pd.DataFrame:
    df = load_csv(path)
    if df.empty or column not in df.columns:
        return pd.DataFrame()
    return (
        df[column]
        .astype(str)
        .str.strip()
        .replace("", "missing")
        .value_counts()
        .rename_axis(label or column)
        .reset_index(name="records")
    )


def _completion_rows() -> pd.DataFrame:
    seed = load_csv(REV / "pilot_ground_truth_seed.csv")
    annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
    df = annotation if not annotation.empty else seed
    if df.empty:
        return pd.DataFrame()
    rows = []
    for col in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect", "annotator", "review_notes"]:
        if col in df.columns:
            completed = int(df[col].astype(str).str.strip().ne("").sum())
            rows.append({"field": col, "completed": completed, "missing": len(df) - completed, "total": len(df)})
    return pd.DataFrame(rows)


def _action_plan_llm_records() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    esg_path = RESULTS / "esg_records.json"
    if esg_path.exists():
        try:
            data = json.loads(esg_path.read_text(encoding="utf-8"))
        except Exception:
            data = []
        if isinstance(data, list):
            for run in data:
                if not isinstance(run, dict):
                    continue
                records = run.get("records") if isinstance(run.get("records"), list) else []
                target = str(run.get("target", "") or "")
                rows.append(
                    {
                        "target_doc": target.split("/")[0] or "unknown",
                        "target": target,
                        "prompt": str(run.get("prompt", "") or "unknown"),
                        "model": str(run.get("model", "") or ""),
                        "ok": bool(run.get("ok")),
                        "records_count": len(records),
                    }
                )

    flat = load_csv(VIS / "tone_records_flat.csv")
    if not flat.empty and "prompt" in flat.columns:
        if "target_doc" not in flat.columns:
            flat["target_doc"] = flat.get("target", pd.Series(["unknown"] * len(flat))).astype(str).str.split("/").str[0]
        group_cols = [col for col in ["target_doc", "target", "prompt", "model"] if col in flat.columns]
        if group_cols:
            grouped = flat.groupby(group_cols, dropna=False).size().reset_index(name="records_count")
            grouped["ok"] = grouped["records_count"].gt(0)
            rows.extend(grouped.to_dict("records"))
    return pd.DataFrame(rows)


def _pdf_prompt_matrix_rows(metric: str = "Extracted records") -> pd.DataFrame:
    records = _action_plan_llm_records()
    if records.empty or not {"target_doc", "prompt", "records_count"}.issubset(records.columns):
        return pd.DataFrame()
    records = records.copy()
    records["target_doc"] = records["target_doc"].astype(str).str.strip().replace("", "unknown")
    records["prompt"] = records["prompt"].astype(str).str.strip().replace("", "unknown")
    records["ok"] = records["ok"].fillna(False).astype(bool) if "ok" in records.columns else True
    records["records_count"] = pd.to_numeric(records["records_count"], errors="coerce").fillna(0).astype(int)
    if metric == "Runs / batches":
        grouped = records.groupby(["target_doc", "prompt"], dropna=False).size().reset_index(name="value")
    elif metric == "Successful runs":
        grouped = records[records["ok"]].groupby(["target_doc", "prompt"], dropna=False).size().reset_index(name="value")
    else:
        grouped = records.groupby(["target_doc", "prompt"], dropna=False)["records_count"].sum().reset_index(name="value")
    if grouped.empty:
        return pd.DataFrame()
    pivot = grouped.pivot_table(index="target_doc", columns="prompt", values="value", aggfunc="sum", fill_value=0).astype(int)
    pivot.columns = [str(c).replace(".md", "").replace("tone_", "") for c in pivot.columns]
    pivot.columns.name = None
    pivot.insert(0, "total", pivot.sum(axis=1))
    return pivot.sort_values("total", ascending=False).reset_index()


def source_dataframe_for_attachment(row: pd.Series) -> pd.DataFrame:
    figure = str(row["figure"])
    if figure == "A.1":
        return _value_counts(VIS / "tone_records_flat.csv", "tone", "tone")
    if figure == "A.2":
        return load_csv(VIS / "tone_esg_crosstab.csv")
    if figure == "A.3":
        return load_csv(VIS / "aspect_tone_crosstab.csv")
    if figure == "A.4":
        return load_csv(VIS / "tone_climatebert_label_crosstab.csv")
    if figure == "A.5":
        return load_csv(VIS / "climatebert_remote_flat.csv").head(30)
    if figure in {"A.6", "A.7", "A.8", "A.9"}:
        return graph_attachment_manifest()[["figure", "title", "chapter", "rq", "source table", "source page", "exists"]]
    if figure == "A.10":
        return load_csv(REV / "model_stability_summary.csv")
    if figure == "A.11":
        return load_csv(REV / "prompt_stability_summary.csv")
    if figure in {"A.12", "A.16"}:
        return load_csv(REV / "ontology_coverage.csv")
    if figure == "A.13":
        seed = load_csv(REV / "pilot_ground_truth_seed.csv")
        silver = load_csv(REV / "silver_tone_ground_truth.csv")
        rows = [{"metric": "pilot seed rows", "records": len(seed)}, {"metric": "silver dataset rows", "records": len(silver)}]
        for field in ["ground_truth_tone", "ground_truth_esg", "ground_truth_aspect"]:
            if field in seed.columns:
                rows.append({"metric": f"{field} completed", "records": int(seed[field].astype(str).str.strip().ne("").sum())})
        return pd.DataFrame(rows)
    if figure == "A.14":
        model = load_csv(REV / "model_stability_summary.csv")
        prompt = load_csv(REV / "prompt_stability_summary.csv")
        rows = []
        if not model.empty and {"model", "runs"}.issubset(model.columns):
            rows.extend({"unit": f"model: {r['model']}", "runs": r["runs"]} for _, r in model.iterrows())
        if not prompt.empty and {"prompt", "runs"}.issubset(prompt.columns):
            rows.extend({"unit": f"prompt: {r['prompt']}", "runs": r["runs"]} for _, r in prompt.iterrows())
        return pd.DataFrame(rows)
    if figure == "A.15":
        return load_csv(REV / "climatebert_proxy_agreement_summary.csv")
    if figure == "A.17":
        tone = load_csv(VIS / "tone_records_flat.csv")
        silver = load_csv(REV / "silver_tone_ground_truth.csv")
        seed = load_csv(REV / "pilot_ground_truth_seed.csv")
        return pd.DataFrame(
            [
                {"metric": "tone_records_flat rows", "records": len(tone)},
                {"metric": "silver_tone_ground_truth rows", "records": len(silver)},
                {"metric": "pilot ground truth seed rows", "records": len(seed)},
            ]
        )
    if figure == "A.18":
        return _completion_rows()
    if figure == "A.19":
        annotation = load_csv(REV / "pilot_ground_truth_annotations.csv")
        seed = load_csv(REV / "pilot_ground_truth_seed.csv")
        silver = load_csv(REV / "silver_tone_ground_truth.csv")
        df = annotation if not annotation.empty else seed
        if df.empty:
            df = silver
        truth = "ground_truth_tone" if "ground_truth_tone" in df.columns and df["ground_truth_tone"].astype(str).str.strip().ne("").any() else "silver_tone_ground_truth"
        pred = "tone_pred" if "tone_pred" in df.columns else "tone"
        if truth not in df.columns or pred not in df.columns:
            return pd.DataFrame()
        return df.groupby([truth, pred], dropna=False).size().reset_index(name="records")
    if figure == "A.20":
        t2 = load_csv(WORKFLOW / "t2_flat_outputs.csv")
        if t2.empty:
            return t2
        cols = [c for c in ["rule_tone", "tone_pred", "sentiment_pred"] if c in t2.columns]
        return t2.groupby(cols, dropna=False).size().reset_index(name="records") if cols else t2.head(30)
    if figure == "A.21":
        return _pdf_prompt_matrix_rows("Extracted records")
    return pd.DataFrame()


def filter_manifest(
    manifest: pd.DataFrame,
    chapter: str = "All",
    rq: str = "All",
    figures: list[str] | None = None,
    only_existing: bool = True,
) -> pd.DataFrame:
    out = manifest.copy()
    if figures:
        out = out[out["figure"].isin(figures)]
    if chapter != "All":
        out = out[out["chapter"].astype(str).str.contains(chapter, case=False, regex=False)]
    if rq != "All":
        out = out[out["rq"].astype(str).str.contains(rq, case=False, regex=False)]
    if only_existing:
        out = out[out["exists"]]
    return out


def render_attachment_cards(
    title: str = "Graph Attachments",
    chapter_default: str = "All",
    rq_default: str = "All",
    figures: list[str] | None = None,
    show_filters: bool = True,
) -> None:
    st.header(title)
    manifest = graph_attachment_manifest()
    chapter = chapter_default
    rq = rq_default
    view_mode = "Graph + original table"
    only_existing = True
    if show_filters:
        c1, c2, c3, c4 = st.columns(4)
        chapter_options = ["All"] + sorted(manifest["chapter"].unique().tolist())
        rq_options = ["All"] + sorted(manifest["rq"].unique().tolist())
        chapter_index = chapter_options.index(chapter_default) if chapter_default in chapter_options else 0
        rq_index = rq_options.index(rq_default) if rq_default in rq_options else 0
        chapter = c1.selectbox("Chapter", chapter_options, index=chapter_index, key=f"{title}_chapter")
        rq = c2.selectbox("RQ", rq_options, index=rq_index, key=f"{title}_rq")
        view_mode = c3.selectbox("View", ["Graph + original table", "Graph only", "Original table only"], key=f"{title}_view")
        only_existing = c4.toggle("Only existing files", value=True, key=f"{title}_existing")

    filtered = filter_manifest(manifest, chapter, rq, figures, only_existing)
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=240)
    for _, row in filtered.iterrows():
        path = Path(str(row["path"]))
        st.divider()
        st.subheader(f"{row['figure']} - {row['title']}")
        meta_cols = st.columns([2, 2, 2, 1])
        meta_cols[0].caption(f"{row['chapter']} | {row['rq']}")
        meta_cols[1].caption(f"Graph: `{path}`")
        meta_cols[2].caption(f"Original table: `{row['source table']}`")
        with meta_cols[3]:
            redirect_button("Open page", str(row["source page"]))
        graph_col, table_col = st.columns([1.05, 1], gap="large")
        if view_mode in {"Graph + original table", "Graph only"}:
            with graph_col:
                st.markdown("**Original graph attachment**")
                if path.exists():
                    show_image(path)
                else:
                    st.warning("Missing graph file.")
        if view_mode in {"Graph + original table", "Original table only"}:
            with table_col:
                st.markdown("**Original / backing table**")
                df = source_dataframe_for_attachment(row)
                if df.empty:
                    st.info("No backing table is available for this attachment yet.")
                else:
                    st.dataframe(df.astype(str), use_container_width=True, hide_index=True, height=360)
                    st.download_button(
                        f"Download {row['figure']} backing table",
                        df.to_csv(index=False).encode("utf-8"),
                        f"{row['figure'].replace('.', '_')}_backing_table.csv",
                        "text/csv",
                        use_container_width=True,
                        key=f"{title}_{row['figure']}_download",
                    )
