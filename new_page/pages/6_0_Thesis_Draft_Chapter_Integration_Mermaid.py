from __future__ import annotations

from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
NARRATIVE_PATH = ROOT / "pages" / "Thesis_Complete_Narrative.docx"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

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
from graph_attachment_gallery import render_attachment_cards  # noqa: E402


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


EDGE_RE = re.compile(r"^(\s*)([A-Za-z][A-Za-z0-9_]*)\s+-->\s+([A-Za-z][A-Za-z0-9_]*)(\s*)$")
NODE_RE = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*)\["(.+?)"\]\s*$')
NARRATIVE_EDGE_GROUP_RE = re.compile(r"\((\d{3}(?:\s*,\s*\d{3})*)\)")


def _clean_node_label(label: str) -> str:
    return re.sub(r"<br\s*/?>", " - ", label).replace('"', "").strip()


def _integrated_node_labels(mermaid: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    for line in mermaid.splitlines():
        match = NODE_RE.match(line)
        if match:
            labels[match.group(1)] = _clean_node_label(match.group(2))
    return labels


def _integrated_edges(mermaid: str) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for line in mermaid.splitlines():
        match = EDGE_RE.match(line)
        if match:
            edges.append((match.group(2), match.group(3)))
    return edges


def _edge_explanation(source_label: str, target_label: str) -> str:
    return (
        f"`{source_label}` is connected to `{target_label}` because the source either feeds data into, "
        "justifies, validates, or operationalizes the target in the thesis workflow. Read this edge as a "
        "traceability link: it shows how a concept, research question, artifact, validation result, or page "
        "supports the next thesis claim."
    )


def label_mermaid_edges(mermaid: str) -> str:
    edge_id = 1
    labelled_lines: list[str] = []
    for line in mermaid.splitlines():
        match = EDGE_RE.match(line)
        if not match:
            labelled_lines.append(line)
            continue
        indent, source, target, trailing = match.groups()
        labelled_lines.append(f"{indent}{source} -- ({edge_id:03d}) --> {target}{trailing}")
        edge_id += 1
    return "\n".join(labelled_lines)


def integrated_edge_explanation_rows() -> pd.DataFrame:
    raw = integrated_thesis_mermaid_raw()
    labels = _integrated_node_labels(raw)
    rows = []
    for idx, (source, target) in enumerate(_integrated_edges(raw), start=1):
        source_label = labels.get(source, source)
        target_label = labels.get(target, target)
        rows.append(
            {
                "edge": f"({idx:03d})",
                "source node": source,
                "source meaning": source_label,
                "target node": target,
                "target meaning": target_label,
                "explanation": _edge_explanation(source_label, target_label),
            }
        )
    return pd.DataFrame(rows)


def focused_edge_mermaid(edge_df: pd.DataFrame, selected_edges: list[str]) -> str:
    selected = edge_df[edge_df["edge"].astype(str).isin(selected_edges)].copy()
    if selected.empty:
        return integrated_thesis_mermaid()

    node_labels: dict[str, str] = {}
    for _, row in selected.iterrows():
        node_labels[str(row["source node"])] = str(row["source meaning"])
        node_labels[str(row["target node"])] = str(row["target meaning"])

    lines = [
        "flowchart LR",
        '    SELECTED["Selected Mermaid edge focus"]',
    ]
    for node_id, label in sorted(node_labels.items()):
        clean_label = label.replace('"', "'")
        lines.append(f'    {node_id}["{clean_label}"]')
    for _, row in selected.iterrows():
        lines.append(
            f'    {row["source node"]} -- {row["edge"]} --> {row["target node"]}'
        )
    for node_id in sorted(node_labels):
        lines.append(f"    SELECTED -. includes .-> {node_id}")
    return "\n".join(lines)


@st.cache_data(show_spinner=False)
def read_complete_narrative_docx(path_text: str = str(NARRATIVE_PATH)) -> pd.DataFrame:
    path = Path(path_text)
    if not path.exists():
        return pd.DataFrame(
            [
                {
                    "paragraph": 0,
                    "text": "",
                    "status": f"Missing narrative document: {path}",
                }
            ]
        )
    try:
        with ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
    except Exception as exc:
        return pd.DataFrame([{"paragraph": 0, "text": "", "status": f"Could not read DOCX: {exc}"}])

    rows: list[dict[str, object]] = []
    for idx, para in enumerate(root.findall(f".//{W_NS}p"), start=1):
        text = "".join(node.text or "" for node in para.findall(f".//{W_NS}t")).strip()
        if text:
            rows.append({"paragraph": idx, "text": text, "status": "ok"})
    return pd.DataFrame(rows)


def narrative_reference_rows(edge_df: pd.DataFrame) -> pd.DataFrame:
    narrative = read_complete_narrative_docx()
    if narrative.empty or "text" not in narrative.columns:
        return pd.DataFrame()

    edge_lookup = {
        str(row["edge"]): row
        for _, row in edge_df.iterrows()
        if str(row.get("edge", "")).strip()
    }
    rows: list[dict[str, object]] = []
    for _, paragraph in narrative.iterrows():
        text = str(paragraph.get("text", ""))
        for match in NARRATIVE_EDGE_GROUP_RE.finditer(text):
            group_text = f"({match.group(1)})"
            numbers = re.findall(r"\d{3}", match.group(1))
            for position, number in enumerate(numbers, start=1):
                edge_id = f"({number})"
                edge = edge_lookup.get(edge_id)
                paragraph_text = text.replace("\n", " ")
                rows.append(
                    {
                        "paragraph": int(paragraph.get("paragraph", 0)),
                        "reference group": group_text,
                        "group size": len(numbers),
                        "item": position,
                        "edge": edge_id,
                        "source node": edge.get("source node", "") if edge is not None else "",
                        "source meaning": edge.get("source meaning", "") if edge is not None else "",
                        "target node": edge.get("target node", "") if edge is not None else "",
                        "target meaning": edge.get("target meaning", "") if edge is not None else "",
                        "edge explanation": edge.get("explanation", "No matching Integrated Mermaid edge label found.") if edge is not None else "No matching Integrated Mermaid edge label found.",
                        "paragraph excerpt": paragraph_text[:900],
                    }
                )
    return pd.DataFrame(rows)


def integrated_thesis_mermaid() -> str:
    return label_mermaid_edges(integrated_thesis_mermaid_raw())


def integrated_thesis_mermaid_raw() -> str:
    return """flowchart TD
    subgraph DRAFT_FOUNDATION["PDF Draft Foundation"]
      I["Chapter I<br/>problem, motivation, objectives, RQs"]
      II["Chapter II<br/>literature gaps, ESG disclosure, Climate NLP"]
      III["Chapter III<br/>methodology, corpus, validation design"]
      DRAFT["thesis_draft_1.pdf<br/>full thesis spine"]
      C456["thesis_chapters_4_5_6.docx<br/>implementation, discussion, conclusion"]
      DRAFT --> I
      DRAFT --> II
      DRAFT --> III
      DRAFT --> C456
    end

    subgraph CHAPTER_BREAKDOWN["Detailed Chapter Breakdown"]
      C11["Chapter 1.1 Context<br/>why ESG disclosure needs executable evidence"]
      C12["Chapter 1.2 Problem<br/>unstructured reports to auditable ESG records"]
      C13["Chapter 1.3 Research Questions<br/>RQ1 to RQ6 become executable tasks"]
      C21["Chapter 2.1 ESG disclosure literature<br/>aspect, pillar, sentiment, tone"]
      C22["Chapter 2.2 Climate NLP and ClimateBERT<br/>benchmark construct"]
      C23["Chapter 2.3 Research gap<br/>Indonesian ESG ABSA and reproducibility"]
      C31["Chapter 3.1 Data and corpus<br/>report PDFs and page provenance"]
      C32["Chapter 3.2 Methodology pipeline<br/>OCR, prompts, LLM, ABSA, validation"]
      C33["Chapter 3.3 Annotation and validation<br/>ground truth, benchmarks, reliability"]
    end

    subgraph RESULTS["Chapter IV Evidence"]
      RQ1["RQ1 PDF to structured ESG<br/>OCR pages, JSON records, provenance"]
      RQ2["RQ2 ABSA schema<br/>aspect, ESG, sentiment, tone"]
      RQ3["RQ3 ClimateBERT comparison<br/>agreement, kappa, crosstab"]
      RQ4["RQ4 Diagnostics<br/>failure modes, schema drift, ontology gaps"]
      RQ5["RQ5 Reproducibility<br/>artifact inventory, dashboards, logs"]
      RQ6["RQ6 Stability<br/>model and prompt metrics"]
    end

    subgraph DISCUSSION["Chapter V Interpretation"]
      V1["Commitment dominance"]
      V2["ClimateBERT divergence<br/>construct validity"]
      V3["Schema drift as diagnostic signal"]
      V4["Indonesian ESG vocabulary contribution"]
      V5["Limitations"]
    end

    subgraph CONCLUSION["Chapter VI Closure"]
      C1["Contribution summary"]
      C2["Answers to RQs"]
      C3["Practical implications"]
      C4["Future work"]
    end

    subgraph S0["A. Source and OCR Preparation"]
      PDFS["Sustainability report PDFs<br/>Indonesian disclosure corpus"]
      OCR["Bulk OCR process<br/>PDF pages become text and markdown"]
      PAGE_MD["Page markdown files<br/>thesis dataset pages page_XXXX md"]
      OCR_AUDIT["OCR processing audit<br/>document status, pages, errors"]
    end

    subgraph S2["C. Prompt and LLM Execution"]
      PROMPTS["Prompt templates<br/>zero-shot, few-shot, chain-of-thought, English, Indonesian"]
      PROVIDERS["Provider options<br/>OpenRouter, LM Studio, Ollama"]
      JOBS["Background job runner<br/>job id, status, progress, events"]
      RAW_RUNS["Raw LLM run records<br/>results esg_records json"]
    end

    subgraph S3["D. Structured ESG Evidence"]
      FLAT["Flattened evidence table<br/>tone_records_flat csv"]
      ABSA["ABSA dimensions<br/>aspect, ESG pillar, sentiment, tone"]
      PROVENANCE["Provenance fields<br/>target document, prompt, model, timestamp, record index"]
      PDF_PROMPT["PDF by prompt matrix<br/>which prompt processed which source"]
    end

    subgraph S4["E. Validation and Diagnostics"]
      CLIMATE["ClimateBERT comparison<br/>proxy and real commitment labels"]
      ONTO["Ontology mapping<br/>GRI and SASB coverage plus novel aspects"]
      FAIL["Failure mode audit<br/>missing tone, schema drift, OCR loss, bilingual issues"]
      STABILITY["Model and prompt stability<br/>parse success, missing-tone rate, field completion"]
    end

    subgraph S5["F. Thesis Outputs"]
      CH4["Chapter 4<br/>implementation results and figures"]
      CH5["Chapter 5<br/>discussion, limitations, construct validity"]
      CH6["Chapter 6<br/>answers, contributions, future work"]
      DASH["Streamlit dashboard<br/>interactive evidence layer"]
    end

    subgraph INPUTS["Validation Inputs"]
      EXTRACT["LLM extracted ESG records<br/>records from esg_records json and tone_records_flat csv"]
      SILVER["Silver dataset<br/>silver_tone_ground_truth csv"]
      IMPORTED["Imported model outputs<br/>ClimateBERT output csv and manual uploads"]
    end

    subgraph HUMAN["Human and Pilot Annotation"]
      SAMPLE["Pilot annotation target<br/>150 to 250 records or full silver set"]
      TONE_GT["Ground-truth tone<br/>commitment, action, outcome, missing, other"]
      ESG_GT["Ground-truth ESG<br/>E, S, G, E-S, E-G, S-G, E-S-G"]
      ASPECT_GT["Ground-truth aspect<br/>domain-specific ESG vocabulary"]
      REVIEW["Needs-review status<br/>unannotated rows remain visible"]
    end

    subgraph MODEL["Model Comparison"]
      CLIMATE_LOCAL["ClimateBERT local run<br/>continue from unprocessed text"]
      PROXY["Proxy climate labels<br/>derived from tone and label fields"]
      CROSSTAB["Tone by ClimateBERT crosstab<br/>agreement and divergence"]
      KAPPA["Agreement metrics<br/>percent agreement and Cohen kappa"]
    end

    subgraph RELIABILITY["Reliability Checks"]
      PROMPT_STAB["Prompt stability<br/>runs, missing-tone rate, schema drift"]
      MODEL_STAB["Model stability<br/>parse success, average records, provider differences"]
      FAILURE["Failure-mode audit<br/>bilingual text, numeric loss, schema field missing"]
      ONTO_VAL["Ontology coverage<br/>mapped and unmapped aspects"]
    end

    subgraph CLAIMS["Thesis Claims"]
      CONSTRUCT["Construct validity<br/>tone is not identical to climate commitment"]
      REPRO["Reproducibility<br/>job logs, artifacts, run configs, dashboards"]
      LIMIT["Limitations<br/>OCR quality, prompt sensitivity, annotation scale"]
      CONTRIBUTION["Contribution<br/>Indonesian ESG vocabulary and executable thesis pipeline"]
    end

    subgraph SOURCE["Source Documents"]
      PDF["thesis_draft_1.pdf<br/>problem, literature, method, thesis spine"]
      DOCX["thesis_chapters_4_5_6.docx<br/>implementation, discussion, conclusion draft"]
      REPORTS["raw sustainability reports<br/>PDF disclosure corpus"]
    end

    subgraph RUNS["Execution Artifacts"]
      OCR_SUM["ocr_processing_summary csv<br/>document and page audit"]
      ESG_JSON["esg_records json<br/>LLM runs and extracted records"]
      JOB_DIRS["background job folders<br/>config, status, control, events"]
      CLIMATE_OUT["climatebert outputs<br/>local model predictions and resume progress"]
    end

    subgraph ANALYSIS["Analysis Tables"]
      TONE_FLAT["tone_records_flat csv<br/>record-level ABSA table"]
      TONE_ESG["tone_esg_crosstab csv<br/>tone by ESG pillar"]
      TONE_CB["tone_climatebert_label_crosstab csv<br/>tone by climate label"]
      MODEL_STAB_ART["model_stability_summary csv<br/>provider and model performance"]
      PROMPT_STAB_ART["prompt_stability_summary csv<br/>prompt reliability"]
      FAILURE_ART["failure_mode_counts csv<br/>diagnostic categories"]
      ONTO_ART["ontology_coverage csv<br/>mapped and novel aspects"]
      AGREEMENT["climatebert_proxy_agreement_summary csv<br/>agreement and kappa"]
    end

    subgraph PAGES["Streamlit Pages"]
      INTEGRATION["6_0 Integration Mermaid<br/>thesis map and lineage"]
      PAGE_CH4["6_1 Chapter 4<br/>live implementation results"]
      PAGE_CH5["6_2 Chapter 5<br/>live discussion claims"]
      PAGE_CH6["6_3 Chapter 6<br/>live conclusion claims"]
      ACTION["3_0 Thesis Action Plan<br/>processing, migration, annotation"]
    end

    subgraph THESIS["Thesis Outputs"]
      FIGURES["figures and tables<br/>dashboard-ready charts"]
      CLAIM_TEXT["citation-backed paragraphs<br/>AP evidence references"]
      NOTES["empty analysis boxes<br/>manual interpretation updates"]
      DEFENSE["defense narrative<br/>RQ evidence, limitation, contribution"]
    end

    I --> C11
    I --> C12
    I --> C13
    II --> C21
    II --> C22
    II --> C23
    III --> C31
    III --> C32
    III --> C33
    C11 --> C12
    C12 --> C13
    C13 --> RQ1
    C13 --> RQ2
    C13 --> RQ3
    C13 --> RQ4
    C13 --> RQ5
    C13 --> RQ6
    C21 --> RQ2
    C22 --> RQ3
    C23 --> RQ4
    C23 --> RQ5
    C23 --> RQ6
    C31 --> RQ1
    C32 --> RQ1
    C32 --> RQ5
    C33 --> RQ2
    C33 --> RQ3
    C33 --> RQ6

    I --> RQ1
    I --> RQ2
    I --> RQ3
    I --> RQ4
    I --> RQ5
    I --> RQ6
    II --> V1
    II --> V2
    II --> V3
    II --> V4
    III --> RQ1
    III --> RQ5
    RQ1 --> C2
    RQ2 --> V1
    RQ3 --> V2
    RQ4 --> V3
    RQ4 --> V4
    RQ5 --> C1
    RQ6 --> V5
    V1 --> C1
    V2 --> C2
    V3 --> C4
    V4 --> C1
    V5 --> C4
    C1 --> CH6
    C2 --> CH6
    C3 --> CH6
    C4 --> CH6

    DRAFT --> PROMPTS
    DRAFT --> C456
    PDFS --> OCR
    OCR --> PAGE_MD
    OCR --> OCR_AUDIT
    PAGE_MD --> PROMPTS
    PROMPTS --> PROVIDERS
    PROVIDERS --> JOBS
    JOBS --> RAW_RUNS
    RAW_RUNS --> FLAT
    FLAT --> ABSA
    FLAT --> PROVENANCE
    FLAT --> PDF_PROMPT
    ABSA --> CLIMATE
    ABSA --> ONTO
    RAW_RUNS --> FAIL
    RAW_RUNS --> STABILITY
    OCR_AUDIT --> CH4
    PDF_PROMPT --> CH4
    CLIMATE --> CH4
    ONTO --> CH4
    FAIL --> CH5
    STABILITY --> CH5
    CH4 --> CH5
    CH5 --> CH6
    CH4 --> DASH
    CH5 --> DASH
    CH6 --> DASH

    EXTRACT --> SILVER
    IMPORTED --> CLIMATE_LOCAL
    SILVER --> SAMPLE
    SAMPLE --> TONE_GT
    SAMPLE --> ESG_GT
    SAMPLE --> ASPECT_GT
    SAMPLE --> REVIEW
    TONE_GT --> CROSSTAB
    ESG_GT --> ONTO_VAL
    ASPECT_GT --> ONTO_VAL
    CLIMATE_LOCAL --> CROSSTAB
    PROXY --> CROSSTAB
    CROSSTAB --> KAPPA
    EXTRACT --> PROMPT_STAB
    EXTRACT --> MODEL_STAB
    EXTRACT --> FAILURE
    ONTO_VAL --> LIMIT
    PROMPT_STAB --> REPRO
    MODEL_STAB --> REPRO
    FAILURE --> LIMIT
    KAPPA --> CONSTRUCT
    ONTO_VAL --> CONTRIBUTION
    CONSTRUCT --> PAGE_CH5
    REPRO --> PAGE_CH6
    LIMIT --> PAGE_CH5
    LIMIT --> PAGE_CH6
    CONTRIBUTION --> PAGE_CH6

    PDF --> INTEGRATION
    DOCX --> INTEGRATION
    REPORTS --> OCR_SUM
    REPORTS --> ESG_JSON
    OCR_SUM --> TONE_FLAT
    ESG_JSON --> TONE_FLAT
    JOB_DIRS --> MODEL_STAB_ART
    ESG_JSON --> MODEL_STAB_ART
    CLIMATE_OUT --> AGREEMENT
    CLIMATE_OUT --> TONE_CB
    TONE_FLAT --> TONE_ESG
    TONE_FLAT --> FAILURE_ART
    TONE_FLAT --> ONTO_ART
    TONE_FLAT --> PROMPT_STAB_ART
    TONE_FLAT --> ACTION
    MODEL_STAB_ART --> ACTION
    PROMPT_STAB_ART --> ACTION
    TONE_ESG --> PAGE_CH4
    TONE_CB --> PAGE_CH4
    AGREEMENT --> PAGE_CH5
    FAILURE_ART --> PAGE_CH5
    ONTO_ART --> PAGE_CH5
    MODEL_STAB_ART --> PAGE_CH6
    PROMPT_STAB_ART --> PAGE_CH6
    PAGE_CH4 --> FIGURES
    PAGE_CH5 --> CLAIM_TEXT
    PAGE_CH6 --> CLAIM_TEXT
    ACTION --> NOTES
    INTEGRATION --> DEFENSE
    FIGURES --> DEFENSE
    CLAIM_TEXT --> DEFENSE
    NOTES --> DEFENSE

    RQ1 --> OCR_SUM
    RQ1 --> ESG_JSON
    RQ2 --> TONE_FLAT
    RQ2 --> TONE_ESG
    RQ3 --> AGREEMENT
    RQ3 --> TONE_CB
    RQ4 --> FAILURE_ART
    RQ4 --> ONTO_ART
    RQ5 --> JOB_DIRS
    RQ5 --> INTEGRATION
    RQ6 --> MODEL_STAB_ART
    RQ6 --> PROMPT_STAB_ART
    FLAT --> EXTRACT
    CLIMATE --> CLIMATE_OUT
    ONTO --> ONTO_ART
    FAIL --> FAILURE_ART
    STABILITY --> MODEL_STAB_ART
    STABILITY --> PROMPT_STAB_ART
    DASH --> INTEGRATION
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

source_cols = st.columns(3)
source_cols[0].markdown(f"**PDF thesis draft:** `{PDF_PATH}`")
source_cols[1].markdown(f"**DOCX chapters 4-6:** `{DOCX_PATH}`")
source_cols[2].markdown(f"**Complete narrative:** `{NARRATIVE_PATH}`")

tab_integrated, tab_map, tab_rq, tab_pipeline, tab_validation, tab_artifacts, tab_cards, tab_outline, tab_evidence = st.tabs(
    [
        "Integrated Navigator",
        "Thesis Spine",
        "RQ Evidence",
        "Pipeline",
        "Validation",
        "Artifact Lineage",
        "Attachment Cards",
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
    st.info(
        "The integrated Mermaid canvas is intentionally large: it combines Thesis Spine, RQ Evidence, Pipeline, "
        "Validation, and Artifact Lineage in one graph. Use the diagram toolbar or scroll inside the frame to inspect details."
    )

    edge_df = integrated_edge_explanation_rows()

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

    edge_options = edge_df["edge"].astype(str).tolist()
    selected_edges = st.multiselect(
        "Select specific Mermaid edge labels",
        edge_options,
        default=[],
        placeholder="Choose one or more edges, for example (001), (002), (005)",
        key="integrated_selected_edges",
        help="When one or more labels are selected, the diagram and tables below focus on those exact arrows.",
    )
    if selected_edges:
        st.caption(f"Focused view: {len(selected_edges):,} selected connection(s). Clear the selector to return to the full integrated navigator.")
        render_mermaid(focused_edge_mermaid(edge_df, selected_edges), height=720)
    else:
        render_mermaid(integrated_thesis_mermaid(), height=1600)

    st.subheader("0. Arrow / Connection Explanations")
    edge_filter = st.text_input(
        "Search edge explanations",
        value="",
        placeholder="Example: (005), RQ5, JOB_DIRS, ClimateBERT, Chapter 5",
        key="integrated_edge_explanation_search",
    )
    edge_display = filter_df(edge_df, chapter_filter, rq_filter, layer_filter)
    if selected_edges:
        edge_display = edge_display[edge_display["edge"].astype(str).isin(selected_edges)]
    if edge_filter.strip():
        needle = edge_filter.strip()
        edge_display = edge_display[
            edge_display.astype(str).apply(
                lambda col: col.str.contains(needle, case=False, regex=False)
            ).any(axis=1)
        ]
    st.dataframe(edge_display, use_container_width=True, hide_index=True, height=420)
    st.download_button(
        "Download connection explanation CSV",
        edge_display.to_csv(index=False).encode("utf-8"),
        "integrated_navigator_connection_explanations.csv",
        "text/csv",
        use_container_width=True,
    )

    st.subheader("0b. Thesis_Complete_Narrative.docx Edge Reference Parser")
    st.write(
        "This parser reads `Thesis_Complete_Narrative.docx`, finds edge citations such as `(080, 081, 082)`, "
        "splits them into separate references, and joins each reference to the matching Integrated Mermaid edge explanation."
    )
    narrative_df = read_complete_narrative_docx()
    narrative_refs = narrative_reference_rows(edge_df)
    n_paragraphs = len(narrative_df[narrative_df.get("status", pd.Series(dtype=str)).astype(str).eq("ok")]) if not narrative_df.empty and "status" in narrative_df.columns else 0
    n_groups = narrative_refs["reference group"].nunique() if not narrative_refs.empty else 0
    n_edges = narrative_refs["edge"].nunique() if not narrative_refs.empty else 0
    c_ref1, c_ref2, c_ref3 = st.columns(3)
    c_ref1.metric("Narrative paragraphs", f"{n_paragraphs:,}")
    c_ref2.metric("Reference groups", f"{n_groups:,}")
    c_ref3.metric("Expanded edge refs", f"{len(narrative_refs):,}")

    if narrative_refs.empty:
        st.info("No `(000)` or `(000, 001, 002)` style edge references were found in the narrative document.")
    else:
        group_options = ["All"] + sorted(narrative_refs["reference group"].astype(str).unique().tolist())
        ref_col1, ref_col2 = st.columns([1, 2])
        selected_group = ref_col1.selectbox("Reference group", group_options)
        ref_search = ref_col2.text_input(
            "Search narrative references",
            value="",
            placeholder="Example: (080), RQ5, Chapter 5, ClimateBERT, provenance",
            key="narrative_reference_search",
        )
        ref_display = filter_df(narrative_refs, chapter_filter, rq_filter, layer_filter)
        if selected_group != "All":
            ref_display = ref_display[ref_display["reference group"].astype(str).eq(selected_group)]
        if selected_edges:
            ref_display = ref_display[ref_display["edge"].astype(str).isin(selected_edges)]
        if ref_search.strip():
            needle = ref_search.strip()
            ref_display = ref_display[
                ref_display.astype(str).apply(
                    lambda col: col.str.contains(needle, case=False, regex=False)
                ).any(axis=1)
            ]

        show_cols = [
            "paragraph",
            "reference group",
            "group size",
            "item",
            "edge",
            "source node",
            "target node",
            "source meaning",
            "target meaning",
            "edge explanation",
            "paragraph excerpt",
        ]
        st.dataframe(ref_display[show_cols], use_container_width=True, hide_index=True, height=520)
        st.download_button(
            "Download narrative reference mapping CSV",
            ref_display.to_csv(index=False).encode("utf-8"),
            "thesis_complete_narrative_edge_reference_mapping.csv",
            "text/csv",
            use_container_width=True,
        )

        multi_ref = narrative_refs[narrative_refs["group size"].astype(int).gt(1)]
        if not multi_ref.empty:
            with st.expander("Example: multi-edge bracket split", expanded=True):
                example_group = multi_ref["reference group"].astype(str).iloc[0]
                st.write(
                    f"`{example_group}` is parsed into "
                    f"{int(multi_ref[multi_ref['reference group'].astype(str).eq(example_group)]['group size'].iloc[0])} "
                    "separate edge explanation rows."
                )
                st.dataframe(
                    multi_ref[multi_ref["reference group"].astype(str).eq(example_group)][show_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=220,
                )

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

with tab_cards:
    render_attachment_cards("Integrated Graph + Table Attachment Cards")

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
