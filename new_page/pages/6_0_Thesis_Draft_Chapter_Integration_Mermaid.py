from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from thesis_chapter_streamlit import (  # noqa: E402
    DOCX_PATH,
    PDF_PATH,
    agreement_chart,
    artifact_mermaid,
    artifact_chart,
    citation_table,
    chapter_outline,
    data_bundle,
    evidence_metrics,
    metric_row,
    model_stability_chart,
    ontology_chart,
    pdf_outline,
    pipeline_mermaid,
    prompt_stability_chart,
    render_mermaid,
    rq_evidence_mermaid,
    thesis_spine_mermaid,
    validation_mermaid,
)


st.set_page_config(page_title="Thesis Draft + Chapters Mermaid Integration", layout="wide")

bundle = data_bundle()
metrics = evidence_metrics(bundle)


def chapter_breakdown_rows() -> list[dict[str, str]]:
    return [
        {
            "chapter section": "Chapter 1.1 Research Context",
            "meaning": "Explains why ESG disclosure needs computational evidence rather than manual-only reading.",
            "rq link": "RQ1, RQ5",
            "pipeline link": "Source documents and OCR scope",
            "artifact link": "thesis_draft_1.pdf; ocr_processing_summary.csv",
            "streamlit page": "6_0 Integration; 6_1 Chapter 4",
        },
        {
            "chapter section": "Chapter 1.2 Problem Statement",
            "meaning": "Defines the gap between unstructured sustainability reports and auditable ESG evidence.",
            "rq link": "RQ1, RQ2",
            "pipeline link": "PDF to page text to structured record",
            "artifact link": "tone_records_flat.csv; esg_records.json",
            "streamlit page": "6_1 Chapter 4",
        },
        {
            "chapter section": "Chapter 1.3 Research Questions",
            "meaning": "Turns the thesis into six executable questions that can be tested with artifacts.",
            "rq link": "RQ1 to RQ6",
            "pipeline link": "All layers",
            "artifact link": "workflow_rq_coverage; citation table",
            "streamlit page": "6_0 Integration",
        },
        {
            "chapter section": "Chapter 2.1 ESG Disclosure Literature",
            "meaning": "Provides the conceptual basis for environmental, social, governance, aspect, and tone labels.",
            "rq link": "RQ2",
            "pipeline link": "ABSA evidence layer",
            "artifact link": "tone_esg_crosstab.csv; ontology_coverage.csv",
            "streamlit page": "6_1 Chapter 4; 6_2 Chapter 5",
        },
        {
            "chapter section": "Chapter 2.2 Climate NLP and ClimateBERT",
            "meaning": "Positions ClimateBERT as a benchmark construct, not as a replacement for tone analysis.",
            "rq link": "RQ3",
            "pipeline link": "Validation layer",
            "artifact link": "climatebert_proxy_agreement_summary.csv",
            "streamlit page": "6_2 Chapter 5",
        },
        {
            "chapter section": "Chapter 2.3 Research Gap",
            "meaning": "Frames the novelty as fine-grained Indonesian ESG extraction plus reproducible diagnostics.",
            "rq link": "RQ4, RQ5, RQ6",
            "pipeline link": "Diagnostics and reproducibility layers",
            "artifact link": "failure_mode_counts.csv; model_stability_summary.csv",
            "streamlit page": "6_2 Chapter 5; 6_3 Chapter 6",
        },
        {
            "chapter section": "Chapter 3.1 Data and Corpus",
            "meaning": "Defines what documents enter the pipeline and how document/page provenance is preserved.",
            "rq link": "RQ1",
            "pipeline link": "Source and OCR layers",
            "artifact link": "ocr_processing_summary.csv; target_doc fields",
            "streamlit page": "6_1 Chapter 4",
        },
        {
            "chapter section": "Chapter 3.2 Methodology Pipeline",
            "meaning": "Specifies OCR, prompting, LLM extraction, flattening, validation, and visualization.",
            "rq link": "RQ1, RQ5",
            "pipeline link": "End-to-end method-to-result flow",
            "artifact link": "esg_records.json; background job folders",
            "streamlit page": "3_0 Action Plan; 6_0 Integration",
        },
        {
            "chapter section": "Chapter 3.3 Annotation and Validation",
            "meaning": "Defines human labels, ClimateBERT comparison, reliability checks, and diagnostics.",
            "rq link": "RQ2, RQ3, RQ4, RQ6",
            "pipeline link": "Validation and reliability loop",
            "artifact link": "silver_tone_ground_truth.csv; agreement summary; failure modes",
            "streamlit page": "6_2 Chapter 5",
        },
        {
            "chapter section": "Chapter 4.1 Implementation Results",
            "meaning": "Reports what the pipeline actually produced from the current live result files.",
            "rq link": "RQ1, RQ2",
            "pipeline link": "Structured ESG evidence layer",
            "artifact link": "tone_records_flat.csv; tone_esg_crosstab.csv",
            "streamlit page": "6_1 Chapter 4",
        },
        {
            "chapter section": "Chapter 4.2 Benchmark Results",
            "meaning": "Compares models, prompts, ClimateBERT/proxy agreement, ontology coverage, and artifact completeness.",
            "rq link": "RQ3, RQ6",
            "pipeline link": "Benchmark and validation layers",
            "artifact link": "model_stability_summary.csv; prompt_stability_summary.csv; agreement summary",
            "streamlit page": "6_1 Chapter 4; 6_2 Chapter 5",
        },
        {
            "chapter section": "Chapter 5.1 Discussion",
            "meaning": "Interprets why tone, climate commitment, ontology coverage, and failure modes matter theoretically.",
            "rq link": "RQ3, RQ4",
            "pipeline link": "Validation to interpretation",
            "artifact link": "tone_climatebert_label_crosstab.csv; ontology_coverage.csv",
            "streamlit page": "6_2 Chapter 5",
        },
        {
            "chapter section": "Chapter 6.1 Contributions",
            "meaning": "Closes the thesis by turning artifacts into reproducible contributions and future work.",
            "rq link": "RQ5, RQ6",
            "pipeline link": "Artifact lineage to thesis contribution",
            "artifact link": "artifact inventory; Streamlit pages 6_0 to 6_3",
            "streamlit page": "6_3 Chapter 6",
        },
    ]


def integrated_map_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rq": "RQ1",
                "chapter 4 evidence": "OCR documents, page audit, flattened ESG records",
                "execution artifact": "ocr_processing_summary.csv; esg_records.json; tone_records_flat.csv",
                "validation artifact": "OCR errors and record provenance",
                "streamlit page": "6_1 Chapter 4",
                "benchmark needed": "OCR page coverage, empty-page rate, document completion rate",
                "thesis meaning": "Shows that raw PDF disclosures can become structured ESG evidence.",
            },
            {
                "rq": "RQ2",
                "chapter 4 evidence": "Aspect, ESG pillar, sentiment, and tone distributions",
                "execution artifact": "tone_esg_crosstab.csv; aspect_tone_crosstab.csv",
                "validation artifact": "silver_tone_ground_truth.csv; annotation workbench",
                "streamlit page": "6_1 Chapter 4; 6_2 Chapter 5",
                "benchmark needed": "Human annotation agreement and label completion rate",
                "thesis meaning": "Tests whether the ABSA schema is operational and annotatable.",
            },
            {
                "rq": "RQ3",
                "chapter 4 evidence": "Tone by ClimateBERT crosstab and agreement metrics",
                "execution artifact": "climatebert_proxy_agreement_summary.csv",
                "validation artifact": "ClimateBERT local output and proxy comparison",
                "streamlit page": "6_2 Chapter 5",
                "benchmark needed": "ClimateBERT baseline, majority-class baseline, human-labelled benchmark",
                "thesis meaning": "Shows whether disclosure tone is distinct from climate commitment.",
            },
            {
                "rq": "RQ4",
                "chapter 4 evidence": "Failure modes, missing fields, ontology gaps",
                "execution artifact": "failure_mode_counts.csv; ontology_coverage.csv",
                "validation artifact": "Failure audit and unmapped aspect clusters",
                "streamlit page": "6_2 Chapter 5",
                "benchmark needed": "Before/after schema validation and retry-loop comparison",
                "thesis meaning": "Turns errors into a diagnostic and methodological contribution.",
            },
            {
                "rq": "RQ5",
                "chapter 4 evidence": "Artifact inventory, run provenance, dashboard pages",
                "execution artifact": "background job folders; artifact inventory",
                "validation artifact": "rerunnable configs and citation table",
                "streamlit page": "6_0 Integration; 6_3 Chapter 6",
                "benchmark needed": "Reproducibility checklist, artifact completeness, rerun success",
                "thesis meaning": "Shows the work is an executable thesis pipeline.",
            },
            {
                "rq": "RQ6",
                "chapter 4 evidence": "Model and prompt stability tables",
                "execution artifact": "model_stability_summary.csv; prompt_stability_summary.csv",
                "validation artifact": "parse success, missing-tone rate, schema drift rate",
                "streamlit page": "6_1 Chapter 4; 6_3 Chapter 6",
                "benchmark needed": "Repeated runs per prompt/model, confidence intervals, lower-bound model",
                "thesis meaning": "Quantifies how stable the LLM extraction pipeline is.",
            },
        ]
    )


def benchmarking_rows(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = evidence_metrics(bundle)
    model_df = bundle["model_stability"]
    prompt_df = bundle["prompt_stability"]
    best_model = "n/a"
    best_model_score = "n/a"
    if not model_df.empty and {"model", "json_parse_success_rate"}.issubset(model_df.columns):
        ranked = model_df.copy()
        ranked["json_parse_success_rate"] = pd.to_numeric(ranked["json_parse_success_rate"], errors="coerce")
        ranked = ranked.sort_values("json_parse_success_rate", ascending=False)
        if not ranked.empty:
            best_model = str(ranked.iloc[0]["model"])
            best_model_score = f"{ranked.iloc[0]['json_parse_success_rate']:.3f}"
    best_prompt = "n/a"
    best_prompt_score = "n/a"
    if not prompt_df.empty and {"prompt", "missing_tone_rate"}.issubset(prompt_df.columns):
        ranked = prompt_df.copy()
        ranked["missing_tone_rate"] = pd.to_numeric(ranked["missing_tone_rate"], errors="coerce")
        ranked = ranked.sort_values("missing_tone_rate", ascending=True)
        if not ranked.empty:
            best_prompt = str(ranked.iloc[0]["prompt"])
            best_prompt_score = f"{ranked.iloc[0]['missing_tone_rate']:.3f}"
    return pd.DataFrame(
        [
            {
                "benchmark": "LLM model parse reliability",
                "current result": f"Best parse success: {best_model} ({best_model_score})",
                "baseline needed": "At least three models with repeated temperature-zero runs",
                "artifact": "model_stability_summary.csv plus esg_records.json",
                "chapter use": "Chapter 4 result; Chapter 6 reproducibility",
            },
            {
                "benchmark": "Prompt robustness",
                "current result": f"Lowest missing-tone prompt: {best_prompt} ({best_prompt_score})",
                "baseline needed": "Zero-shot vs few-shot vs chain-of-thought in both languages",
                "artifact": "prompt_stability_summary.csv",
                "chapter use": "RQ6 stability discussion",
            },
            {
                "benchmark": "ClimateBERT construct comparison",
                "current result": f"Agreement {m['percent_agreement']:.1%}; kappa {m['kappa']:.3f}",
                "baseline needed": "Majority-label baseline and human-labelled ClimateBERT comparison",
                "artifact": "climatebert_proxy_agreement_summary.csv",
                "chapter use": "RQ3 discussion",
            },
            {
                "benchmark": "Ontology coverage",
                "current result": f"{m['ontology_mapped']:,}/{m['ontology_total']:,} mapped aspect rows",
                "baseline needed": "GRI/SASB-only mapping vs Indonesian-specific extension",
                "artifact": "ontology_coverage.csv",
                "chapter use": "RQ4 and contribution framing",
            },
            {
                "benchmark": "Reproducibility completeness",
                "current result": f"{m['artifacts']:,} discoverable result artifacts",
                "baseline needed": "Artifact checklist: inputs, configs, logs, outputs, charts, chapter pages",
                "artifact": "results/* inventory",
                "chapter use": "RQ5 and Chapter 6",
            },
        ]
    )


def integrated_thesis_mermaid() -> str:
    return """flowchart TD
    subgraph C123["Chapters 1 to 3: Thesis Foundation"]
      C11["Chapter 1.1 Context<br/>Why ESG disclosure needs executable evidence"]
      C12["Chapter 1.2 Problem<br/>Unstructured reports to auditable ESG records"]
      C13["Chapter 1.3 Research Questions<br/>RQ1 to RQ6 become executable tasks"]
      C21["Chapter 2.1 ESG Literature<br/>Aspect, pillar, sentiment, tone"]
      C22["Chapter 2.2 Climate NLP<br/>ClimateBERT as benchmark construct"]
      C31["Chapter 3.1 Corpus<br/>PDF reports and page provenance"]
      C32["Chapter 3.2 Pipeline Method<br/>OCR, prompts, LLM, ABSA, validation"]
      C33["Chapter 3.3 Validation Method<br/>annotation, benchmarks, reliability"]
    end

    subgraph CH4["Chapter 4: Evidence and Results"]
      RQ1["RQ1 Structured ESG records<br/>OCR scope and record extraction"]
      RQ2["RQ2 ABSA schema<br/>aspect, ESG, sentiment, tone"]
      RQ3["RQ3 ClimateBERT comparison<br/>agreement and divergence"]
      RQ4["RQ4 Error diagnostics<br/>failure modes and ontology gaps"]
      RQ5["RQ5 Reproducibility<br/>artifacts, jobs, dashboards"]
      RQ6["RQ6 Stability<br/>model and prompt benchmarking"]
    end

    subgraph ART["Execution Artifacts and Streamlit Pages"]
      OCR["ocr_processing_summary csv"]
      ESG["esg_records json"]
      FLAT["tone_records_flat csv"]
      CB["climatebert agreement csv"]
      ONTO["ontology coverage csv"]
      FAIL["failure mode csv"]
      STAB["model and prompt stability csv"]
      JOBS["background job configs and events"]
      P60["6_0 integrated map"]
      P61["6_1 chapter 4 page"]
      P62["6_2 chapter 5 page"]
      P63["6_3 chapter 6 page"]
    end

    subgraph VAL["Validation and Reliability"]
      HUMAN["Human annotation<br/>silver ground truth"]
      CLIMATE["ClimateBERT local benchmark"]
      BENCH["Benchmarking<br/>models, prompts, ontology, reproducibility"]
      REL["Reliability claims<br/>repeatability and provenance"]
      LIMITS["Limitations<br/>OCR quality, schema drift, label scale"]
    end

    subgraph C56["Chapters 5 and 6: Interpretation and Closure"]
      DISC["Chapter 5 Discussion<br/>construct validity and limitations"]
      CONC["Chapter 6 Conclusion<br/>answers, contributions, future work"]
      CONTRIB["Thesis contribution<br/>Indonesian ESG executable evidence workflow"]
    end

    C11 --> C12 --> C13
    C21 --> RQ2
    C22 --> RQ3
    C31 --> RQ1
    C32 --> RQ1
    C32 --> RQ5
    C33 --> RQ3
    C33 --> RQ6
    C13 --> RQ1
    C13 --> RQ2
    C13 --> RQ3
    C13 --> RQ4
    C13 --> RQ5
    C13 --> RQ6
    RQ1 --> OCR
    RQ1 --> ESG
    RQ2 --> FLAT
    RQ3 --> CB
    RQ4 --> FAIL
    RQ4 --> ONTO
    RQ5 --> JOBS
    RQ5 --> P60
    RQ6 --> STAB
    OCR --> P61
    ESG --> P61
    FLAT --> P61
    CB --> P62
    FAIL --> P62
    ONTO --> P62
    STAB --> P63
    JOBS --> P60
    FLAT --> HUMAN
    CB --> CLIMATE
    STAB --> BENCH
    ONTO --> BENCH
    JOBS --> REL
    FAIL --> LIMITS
    HUMAN --> DISC
    CLIMATE --> DISC
    BENCH --> DISC
    REL --> CONC
    LIMITS --> DISC
    LIMITS --> CONC
    DISC --> CONC
    CONC --> CONTRIB
    """


def filter_df(df: pd.DataFrame, chapter_filter: str, rq_filter: str, layer_filter: str) -> pd.DataFrame:
    out = df.copy()
    if chapter_filter != "All":
        mask = out.astype(str).apply(lambda col: col.str.contains(chapter_filter, case=False, regex=False)).any(axis=1)
        out = out[mask]
    if rq_filter != "All":
        mask = out.astype(str).apply(lambda col: col.str.contains(rq_filter, case=False, regex=False)).any(axis=1)
        out = out[mask]
    if layer_filter != "All":
        mask = out.astype(str).apply(lambda col: col.str.contains(layer_filter, case=False, regex=False)).any(axis=1)
        out = out[mask]
    return out

st.title("Thesis Draft + Chapters 4-6 Integration Map")
st.caption(
    "In-depth Mermaid maps that connect `thesis_draft_1.pdf` with "
    "`thesis_chapters_4_5_6.docx`, current result artifacts, and Streamlit evidence pages."
)
metric_row(bundle)

st.divider()

source_cols = st.columns(2)
source_cols[0].markdown(f"**PDF thesis draft:** `{PDF_PATH}`")
source_cols[1].markdown(f"**DOCX chapters 4-6:** `{DOCX_PATH}`")

tab_integrated, tab_map, tab_rq, tab_pipeline, tab_validation, tab_artifacts, tab_outline, tab_evidence = st.tabs(
    [
        "Integrated Navigator",
        "Thesis Spine",
        "RQ Evidence",
        "Pipeline",
        "Validation",
        "Artifact Lineage",
        "Source Outlines",
        "Evidence Tables",
    ]
)

with tab_integrated:
    st.header("Integrated Thesis Evidence Navigator")
    st.write(
        "This section combines the thesis spine, research-question evidence, method pipeline, validation loop, "
        "benchmarking, and artifact lineage into one filtered view. Use it as the master map from Chapter 1 to "
        "Chapter 6: each thesis section explains a claim, each RQ produces Chapter 4 evidence, and each claim is "
        "tied to execution artifacts, validation artifacts, and Streamlit pages."
    )

    f1, f2, f3 = st.columns(3)
    chapter_filter = f1.selectbox(
        "Chapter / subsection filter",
        [
            "All",
            "Chapter 1",
            "Chapter 1.1",
            "Chapter 1.2",
            "Chapter 1.3",
            "Chapter 2",
            "Chapter 2.1",
            "Chapter 2.2",
            "Chapter 3",
            "Chapter 3.1",
            "Chapter 3.2",
            "Chapter 3.3",
            "Chapter 4",
            "Chapter 5",
            "Chapter 6",
        ],
    )
    rq_filter = f2.selectbox("Research question filter", ["All", "RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"])
    layer_filter = f3.selectbox(
        "Evidence layer filter",
        [
            "All",
            "Source",
            "OCR",
            "Pipeline",
            "ABSA",
            "ClimateBERT",
            "Ontology",
            "Failure",
            "Benchmark",
            "Reproducibility",
            "Streamlit",
        ],
    )

    render_mermaid(integrated_thesis_mermaid(), height=1120)

    st.subheader("1. Chapter Breakdown and Meaning")
    breakdown = pd.DataFrame(chapter_breakdown_rows())
    st.dataframe(
        filter_df(breakdown, chapter_filter, rq_filter, layer_filter),
        use_container_width=True,
        hide_index=True,
        height=360,
    )

    st.subheader("2. Integrated RQ, Chapter 4 Evidence, Execution Artifacts, and Streamlit Pages")
    integrated = integrated_map_rows()
    st.dataframe(
        filter_df(integrated, chapter_filter, rq_filter, layer_filter),
        use_container_width=True,
        hide_index=True,
        height=330,
    )

    st.subheader("3. Benchmarking")
    st.write(
        "These are the benchmark layers needed for thesis defense: model reliability, prompt robustness, "
        "ClimateBERT comparison, ontology coverage, and reproducibility completeness."
    )
    benchmarks = benchmarking_rows(bundle)
    st.dataframe(
        filter_df(benchmarks, chapter_filter, rq_filter, layer_filter),
        use_container_width=True,
        hide_index=True,
        height=250,
    )
    b1, b2 = st.columns(2)
    with b1:
        model_stability_chart(bundle["model_stability"])
    with b2:
        prompt_stability_chart(bundle["prompt_stability"])

    st.subheader("4. Validation and Artifact Lineage Integration")
    validation_lineage = pd.DataFrame(
        [
            {
                "validation claim": "Human annotation checks whether ABSA labels are meaningful.",
                "artifact lineage": "tone_records_flat.csv -> silver_tone_ground_truth.csv -> Chapter 5 discussion",
                "streamlit page": "6_2 Chapter 5",
                "benchmark needed": "Inter-annotator agreement and completion rate",
            },
            {
                "validation claim": "ClimateBERT comparison checks construct divergence.",
                "artifact lineage": "ClimateBERT outputs -> agreement summary -> tone by ClimateBERT crosstab",
                "streamlit page": "6_2 Chapter 5",
                "benchmark needed": "Majority baseline and manually labelled comparison set",
            },
            {
                "validation claim": "Model/prompt stability checks extraction repeatability.",
                "artifact lineage": "background jobs -> esg_records.json -> model and prompt stability summaries",
                "streamlit page": "3_0 Action Plan; 6_3 Chapter 6",
                "benchmark needed": "Repeated runs across at least three models and seven prompts",
            },
            {
                "validation claim": "Ontology coverage checks whether known standards cover Indonesian ESG vocabulary.",
                "artifact lineage": "aspect fields -> ontology_coverage.csv -> unmapped aspect clusters",
                "streamlit page": "6_2 Chapter 5; 6_3 Chapter 6",
                "benchmark needed": "GRI/SASB-only map compared with Indonesian extension",
            },
            {
                "validation claim": "Failure auditing checks where the pipeline needs redesign.",
                "artifact lineage": "raw run outputs -> failure_modes.csv -> Chapter 5 limitations",
                "streamlit page": "6_2 Chapter 5",
                "benchmark needed": "Before/after retry and schema-validation comparison",
            },
        ]
    )
    st.dataframe(
        filter_df(validation_lineage, chapter_filter, rq_filter, layer_filter),
        use_container_width=True,
        hide_index=True,
        height=260,
    )

    st.subheader("5. Citation-Ready Live Evidence")
    st.dataframe(citation_table(bundle), use_container_width=True, hide_index=True, height=260)

with tab_map:
    st.header("Full Thesis Spine: Draft PDF to Chapters 4-6")
    st.write(
        "This diagram treats the PDF as the full thesis spine and the DOCX as the focused implementation, "
        "discussion, and conclusion package. The arrows show how the early chapters feed the evidence and claims."
    )
    render_mermaid(thesis_spine_mermaid(), height=680)

with tab_rq:
    st.header("Research Questions to Evidence, Interpretation, and Conclusion")
    st.write(
        "This map connects the draft's problem/literature/methodology chapters to Chapter IV evidence, "
        "Chapter V interpretation, and Chapter VI contribution closure."
    )
    render_mermaid(rq_evidence_mermaid(), height=780)

with tab_pipeline:
    st.header("Method-to-Result Pipeline")
    st.write(
        "This diagram turns the methodology and implementation chapters into a reproducible dataflow: "
        "PDF inputs, OCR pages, prompt templates, LLM extraction, ABSA dimensions, validation, diagnostics, and thesis graphs."
    )
    render_mermaid(pipeline_mermaid(), height=980)

    st.subheader("Detailed Pipeline Breakdown")
    pipeline_rows = [
        {
            "layer": "A. Source",
            "thesis role": "Connects the draft methodology to the empirical corpus.",
            "live evidence": f"{metrics['ocr_documents']:,} OCR documents; {metrics['ocr_pages']:.0f} OCR pages.",
            "main artifact": "results/revision_analysis/ocr_processing_summary.csv",
            "chapter use": "Chapter 4 describes the data source and processing scope.",
        },
        {
            "layer": "B. OCR",
            "thesis role": "Turns report PDFs into page-level text units for extraction.",
            "live evidence": "OCR status, page counts, and error fields.",
            "main artifact": "thesis_dataset/*/pages/page_XXXX.md",
            "chapter use": "Chapter 4 implementation evidence; Chapter 5 OCR limitation discussion.",
        },
        {
            "layer": "C. Prompt and LLM",
            "thesis role": "Runs extraction prompts through selectable LLM backends.",
            "live evidence": f"{metrics['live_runs']:,} run objects; {metrics['live_extracted_rows']:,} live extracted records.",
            "main artifact": "results/esg_records.json",
            "chapter use": "Chapter 4 results and Chapter 6 reproducibility contribution.",
        },
        {
            "layer": "D. ABSA evidence",
            "thesis role": "Creates record-level aspect, ESG, sentiment, and tone labels.",
            "live evidence": f"{metrics['tone_records']:,} flattened records across {metrics['documents']:,} documents.",
            "main artifact": "results/visualizations/tone_records_flat.csv",
            "chapter use": "Chapter 4 core empirical table and visualizations.",
        },
        {
            "layer": "E. Validation",
            "thesis role": "Tests whether labels are stable, interpretable, and traceable.",
            "live evidence": f"{metrics['models']:,} model configurations; kappa {metrics['kappa']:.3f}.",
            "main artifact": "results/revision_analysis/*.csv",
            "chapter use": "Chapter 5 discussion and Chapter 6 future work.",
        },
        {
            "layer": "F. Thesis output",
            "thesis role": "Converts artifacts into figures, cited claims, and editable interpretation.",
            "live evidence": f"{metrics['artifacts']:,} discoverable result artifacts.",
            "main artifact": "Streamlit pages 6_0 to 6_3",
            "chapter use": "Defense-ready narrative and updateable thesis sections.",
        },
    ]
    st.dataframe(pd.DataFrame(pipeline_rows), use_container_width=True, hide_index=True, height=310)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Prompt Stability Evidence")
        prompt_stability_chart(bundle["prompt_stability"])
    with c2:
        st.subheader("Model Stability Evidence")
        model_stability_chart(bundle["model_stability"])

with tab_validation:
    st.header("Validation and Reliability Loop")
    st.write(
        "This map shows how the ground-truth workbench, ClimateBERT comparison, model/prompt stability, and failure audits "
        "support construct validity, reliability, limitations, and future work."
    )
    render_mermaid(validation_mermaid(), height=980)
    st.subheader("Detailed Validation Breakdown")
    validation_rows = [
        {
            "validation layer": "Human annotation",
            "what it checks": "Whether extracted records can be judged by tone, ESG pillar, aspect, and review status.",
            "expected output": "silver_tone_ground_truth.csv with completed human labels.",
            "thesis claim supported": "RQ2 schema validity and RQ5 reproducibility.",
        },
        {
            "validation layer": "ClimateBERT comparison",
            "what it checks": "Whether disclosure tone is the same construct as climate commitment.",
            "expected output": "Agreement table, crosstab, Cohen kappa.",
            "thesis claim supported": "RQ3 construct divergence between tone and ClimateBERT labels.",
        },
        {
            "validation layer": "Prompt stability",
            "what it checks": "Whether prompt design changes parse success, missing tone, and field completion.",
            "expected output": "prompt_stability_summary.csv.",
            "thesis claim supported": "RQ6 prompt sensitivity and repeatability.",
        },
        {
            "validation layer": "Model stability",
            "what it checks": "Whether backend/model choice changes extraction reliability.",
            "expected output": "model_stability_summary.csv plus live esg_records.json-derived rows.",
            "thesis claim supported": "RQ6 model sensitivity and reproducibility boundaries.",
        },
        {
            "validation layer": "Failure audit",
            "what it checks": "Where the extraction pipeline fails or drifts.",
            "expected output": "failure_mode_counts.csv and failure_modes.csv.",
            "thesis claim supported": "Chapter 5 limitations and Chapter 6 future work.",
        },
        {
            "validation layer": "Ontology coverage",
            "what it checks": "Which aspects map to GRI/SASB and which remain Indonesian-specific.",
            "expected output": "ontology_coverage.csv.",
            "thesis claim supported": "Novel Indonesian ESG vocabulary contribution.",
        },
    ]
    st.dataframe(pd.DataFrame(validation_rows), use_container_width=True, hide_index=True, height=300)

    st.subheader("ClimateBERT / Proxy Agreement Evidence")
    c1, c2 = st.columns(2)
    with c1:
        agreement_chart(bundle["agreement"])
    with c2:
        ontology_chart(bundle["ontology"])

with tab_artifacts:
    st.header("Artifact Lineage and Streamlit Page Integration")
    st.write(
        "This diagram connects the source thesis documents to generated chapter pages and result artifacts, "
        "so the Streamlit application becomes an evidence layer for the thesis narrative."
    )
    render_mermaid(artifact_mermaid(), height=1020)

    st.subheader("Detailed Artifact Lineage")
    artifact_rows = [
        {
            "artifact family": "Source documents",
            "examples": "thesis_draft_1.pdf, thesis_chapters_4_5_6.docx, sustainability report PDFs",
            "owner page": "6_0 integration map",
            "why it matters": "Keeps thesis structure and empirical data connected.",
        },
        {
            "artifact family": "Execution artifacts",
            "examples": "results/esg_records.json, background job status.json, events.jsonl",
            "owner page": "3_0 Thesis Action Plan and LLM monitor",
            "why it matters": "Preserves run provenance and supports reruns.",
        },
        {
            "artifact family": "Analysis tables",
            "examples": "tone_records_flat.csv, model_stability_summary.csv, prompt_stability_summary.csv",
            "owner page": "6_1 Chapter 4 and 6_3 Chapter 6",
            "why it matters": "Provides the numeric basis for figures and claims.",
        },
        {
            "artifact family": "Validation tables",
            "examples": "climatebert_proxy_agreement_summary.csv, ontology_coverage.csv, failure_mode_counts.csv",
            "owner page": "6_2 Chapter 5",
            "why it matters": "Supports interpretation, limitations, and construct-validity discussion.",
        },
        {
            "artifact family": "Editable thesis claims",
            "examples": "generated cited paragraphs plus empty analysis boxes",
            "owner page": "6_1, 6_2, 6_3",
            "why it matters": "Lets the written analysis change without losing the live evidence source.",
        },
    ]
    st.dataframe(pd.DataFrame(artifact_rows), use_container_width=True, hide_index=True, height=285)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Artifact Inventory Chart")
        artifact_chart(bundle["inventory"])
    with c2:
        st.subheader("Citation-Ready Result Claims")
        st.dataframe(citation_table(bundle), use_container_width=True, hide_index=True, height=360)

with tab_outline:
    st.header("Source Outlines")
    pdf_df = pdf_outline()
    docx_df = chapter_outline()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("PDF Draft Outline")
        st.dataframe(pdf_df, use_container_width=True, hide_index=True, height=520)
    with c2:
        st.subheader("DOCX Chapter 4-6 Outline")
        st.dataframe(docx_df, use_container_width=True, hide_index=True, height=520)

    merged = pd.concat([pdf_df, docx_df], ignore_index=True, sort=False)
    st.download_button(
        "Download integrated outline CSV",
        merged.to_csv(index=False).encode("utf-8"),
        "thesis_draft_docx_integrated_outline.csv",
        "text/csv",
        use_container_width=True,
    )

with tab_evidence:
    st.header("Evidence Tables Used by the Integration")
    st.write(
        "These are the live result tables behind the Mermaid claims. Use this tab to verify that each narrative link "
        "has a concrete artifact behind it."
    )
    table_choice = st.selectbox(
        "Evidence table",
        [
            "tone_records",
            "tone_esg",
            "tone_climatebert",
            "model_stability",
            "prompt_stability",
            "failure_counts",
            "ontology",
            "agreement",
            "ocr",
            "greenwashing",
            "inventory",
        ],
    )
    df = bundle.get(table_choice, pd.DataFrame())
    display_df = df.astype(str) if not df.empty else df
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=520)
    if not df.empty:
        st.download_button(
            f"Download {table_choice}.csv",
            df.to_csv(index=False).encode("utf-8"),
            f"{table_choice}.csv",
            "text/csv",
            use_container_width=True,
        )
