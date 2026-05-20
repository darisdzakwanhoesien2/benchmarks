from __future__ import annotations

from pathlib import Path
import json
import uuid
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import altair as alt
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
RESULTS = ROOT / "results"
VIS = RESULTS / "visualizations"
REVISION = RESULTS / "revision_analysis"
WORKFLOW = RESULTS / "thesis_workflow_dashboard"
DOCX_PATH = PAGES / "thesis_chapters_4_5_6.docx"
PDF_PATH = PAGES / "thesis_draft_1.pdf"

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).replace("\xa0", " ").strip()


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    if df.empty or col not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col], errors="coerce")


def fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def fmt_rate(value: Any) -> str:
    try:
        number = float(value)
    except Exception:
        return "n/a"
    if pd.isna(number):
        return "n/a"
    return f"{number:.3f}"


def fmt_pct(value: Any) -> str:
    try:
        number = float(value)
    except Exception:
        return "n/a"
    if pd.isna(number):
        return "n/a"
    return f"{number:.1%}"


def style_map(zf: ZipFile) -> dict[str, str]:
    if "word/styles.xml" not in zf.namelist():
        return {}
    root = ET.fromstring(zf.read("word/styles.xml"))
    styles: dict[str, str] = {}
    for style in root.findall(f".//{W_NS}style"):
        style_id = style.attrib.get(f"{W_NS}styleId", "")
        name_el = style.find(f"{W_NS}name")
        name = name_el.attrib.get(f"{W_NS}val", "") if name_el is not None else ""
        if style_id:
            styles[style_id] = name or style_id
    return styles


@st.cache_data(show_spinner=False)
def read_chapter_docx(path_text: str = str(DOCX_PATH)) -> dict[str, list[dict[str, str]]]:
    path = Path(path_text)
    if not path.exists():
        return {}
    with ZipFile(path) as zf:
        styles = style_map(zf)
        root = ET.fromstring(zf.read("word/document.xml"))
    chapters: dict[str, list[dict[str, str]]] = {}
    current = ""
    for para in root.findall(f".//{W_NS}p"):
        texts = [node.text or "" for node in para.findall(f".//{W_NS}t")]
        text = clean("".join(texts))
        if not text:
            continue
        p_style = ""
        p_style_el = para.find(f"./{W_NS}pPr/{W_NS}pStyle")
        if p_style_el is not None:
            p_style = styles.get(p_style_el.attrib.get(f"{W_NS}val", ""), "")
        if p_style == "Heading 1" or text.startswith(("IV.", "V.", "VI.")):
            current = text
            chapters.setdefault(current, [])
            continue
        if current:
            chapters[current].append({"style": p_style, "text": text})
    return chapters


def chapter_key(number: int) -> str:
    prefix = {4: "IV.", 5: "V.", 6: "VI."}.get(number, "")
    chapters = read_chapter_docx()
    for title in chapters:
        if title.startswith(prefix):
            return title
    return ""


def chapter_blocks(number: int) -> list[dict[str, str]]:
    key = chapter_key(number)
    return read_chapter_docx().get(key, [])


def chapter_outline() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for chapter, blocks in read_chapter_docx().items():
        rows.append({"source": "DOCX chapters 4-6", "level": "chapter", "heading": chapter})
        for block in blocks:
            if block["style"] in {"Heading 2", "Heading 3"}:
                rows.append(
                    {
                        "source": "DOCX chapters 4-6",
                        "level": block["style"].lower().replace(" ", "_"),
                        "heading": block["text"],
                    }
                )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def read_pdf_text(path_text: str = str(PDF_PATH), max_pages: int | None = None) -> tuple[str, str]:
    path = Path(path_text)
    if not path.exists():
        return "", f"Missing PDF: {path}"
    try:
        from pypdf import PdfReader
    except Exception as exc:
        return "", f"`pypdf` is not installed in this runtime: {exc}"
    try:
        reader = PdfReader(str(path))
        pages = reader.pages[:max_pages] if max_pages else reader.pages
        text = "\n".join(page.extract_text() or "" for page in pages)
        return text, ""
    except Exception as exc:
        return "", f"Could not read PDF: {exc}"


def pdf_outline(max_lines: int = 140) -> pd.DataFrame:
    text, error = read_pdf_text()
    if error or not text:
        return pd.DataFrame([{"source": "PDF thesis draft", "level": "error", "heading": error or "No text extracted."}])
    rows: list[dict[str, str]] = []
    for raw in text.splitlines():
        line = clean(raw)
        if not line or len(line) > 180:
            continue
        is_heading = (
            line.startswith(("I.", "II", "III", "IV", "V.", "VI", "CHAPTER"))
            or any(line.startswith(prefix) for prefix in ["I-", "II-", "III-", "IV-", "V-", "VI-"])
            or any(token in line.lower() for token in ["research questions", "literature review", "methodology", "implementation and results", "discussion", "conclusion"])
        )
        if is_heading:
            rows.append({"source": "PDF thesis draft", "level": "outline", "heading": line})
        if len(rows) >= max_lines:
            break
    return pd.DataFrame(rows)


def mermaid_html(code: str, height: int = 620) -> str:
    escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    element_id = f"mermaid-{uuid.uuid4().hex}"
    return f"""
    <div id="{element_id}" class="mermaid">
    {escaped}
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: 'loose',
        suppressErrorRendering: false,
        flowchart: {{
          htmlLabels: true,
          curve: 'basis',
          nodeSpacing: 42,
          rankSpacing: 58
        }},
        theme: 'base',
        themeVariables: {{
          primaryColor: '#e8f3f1',
          primaryTextColor: '#1f2937',
          primaryBorderColor: '#2f6f73',
          lineColor: '#4b5563',
          secondaryColor: '#f5f7fa',
          tertiaryColor: '#fff7ed'
        }}
      }});
      await mermaid.run({{ nodes: [document.getElementById('{element_id}')] }});
    </script>
    <style>
      .mermaid {{
        min-height: {height - 24}px;
        overflow: auto;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        background: #ffffff;
      }}
    </style>
    """


def render_mermaid(code: str, height: int = 620) -> None:
    import streamlit.components.v1 as components

    components.html(mermaid_html(code, height), height=height, scrolling=True)
    with st.expander("Mermaid source", expanded=False):
        st.code(code, language="mermaid")


def thesis_spine_mermaid() -> str:
    return """flowchart TD
    DRAFT["thesis_draft_1.pdf<br/>Full thesis spine"] --> C1["Chapter I<br/>Problem, motivation, RQs"]
    DRAFT --> C2["Chapter II<br/>Literature review and gaps"]
    DRAFT --> C3["Chapter III<br/>Methodology"]
    DRAFT --> C456["thesis_chapters_4_5_6.docx<br/>Implementation, Discussion, Conclusion"]

    C1 --> RQ["Six Research Questions"]
    C2 --> GAPS["Gap synthesis<br/>fine-grained ESG ABSA, bilinguality, explainability, reproducibility"]
    C3 --> METHOD["Pipeline method<br/>OCR -> prompts -> ABSA -> validation -> dashboards"]
    C456 --> CH4["Chapter IV<br/>Implementation and Results"]
    C456 --> CH5["Chapter V<br/>Discussion"]
    C456 --> CH6["Chapter VI<br/>Conclusion"]

    RQ --> CH4
    GAPS --> CH5
    METHOD --> CH4
    CH4 --> CH5
    CH5 --> CH6
    CH6 --> CONTRIBUTIONS["Six thesis contributions<br/>pipeline, prompt framework, tone taxonomy, ontology, ClimateBERT comparison, explainability"]
    """


def rq_evidence_mermaid() -> str:
    return """flowchart LR
    subgraph DRAFT["PDF Draft Foundation"]
      I["Chapter I<br/>RQs and objectives"]
      II["Chapter II<br/>Literature gaps"]
      III["Chapter III<br/>Methodology design"]
    end

    subgraph RESULTS["Chapter IV Evidence"]
      RQ1["RQ1 PDF -> structured ESG<br/>OCR pages, JSON records, provenance"]
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
    """


def pipeline_mermaid() -> str:
    return """flowchart TD
    subgraph S0["A. Thesis Source Layer"]
      DRAFT["thesis_draft_1.pdf<br/>Chapters 1 to 3 define problem, gaps, RQs, and methodology"]
      C456["thesis_chapters_4_5_6.docx<br/>Chapters 4 to 6 receive generated evidence and interpretation"]
      PDFS["Sustainability report PDFs<br/>Indonesian listed-company reports"]
    end

    subgraph S1["B. OCR and Page Preparation"]
      OCR["Bulk OCR process<br/>PDF pages become text and markdown"]
      PAGE_MD["Page markdown files<br/>thesis_dataset pages page_XXXX.md"]
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
    """


def validation_mermaid() -> str:
    return """flowchart TD
    subgraph INPUTS["A. Validation Inputs"]
      EXTRACT["LLM extracted ESG records<br/>records from esg_records json and tone_records_flat csv"]
      SILVER["Silver dataset<br/>silver_tone_ground_truth csv"]
      IMPORTED["Imported model outputs<br/>ClimateBERT output csv and manual uploads"]
    end

    subgraph HUMAN["B. Human and Pilot Annotation"]
      SAMPLE["Pilot annotation target<br/>150 to 250 records or full silver set"]
      TONE_GT["Ground-truth tone<br/>commitment, action, outcome, missing, other"]
      ESG_GT["Ground-truth ESG<br/>E, S, G, E-S, E-G, S-G, E-S-G"]
      ASPECT_GT["Ground-truth aspect<br/>domain-specific ESG vocabulary"]
      REVIEW["Needs-review status<br/>unannotated rows remain visible"]
    end

    subgraph MODEL["C. Model Comparison"]
      CLIMATE["ClimateBERT local run<br/>continue from unprocessed text"]
      PROXY["Proxy climate labels<br/>derived from tone and label fields"]
      CROSSTAB["Tone by ClimateBERT crosstab<br/>agreement and divergence"]
      KAPPA["Agreement metrics<br/>percent agreement and Cohen kappa"]
    end

    subgraph RELIABILITY["D. Reliability Checks"]
      PROMPT_STAB["Prompt stability<br/>runs, missing-tone rate, schema drift"]
      MODEL_STAB["Model stability<br/>parse success, average records, provider differences"]
      FAILURE["Failure-mode audit<br/>bilingual text, numeric loss, schema field missing"]
      ONTO["Ontology coverage<br/>mapped and unmapped aspects"]
    end

    subgraph CLAIMS["E. Thesis Claims"]
      CONSTRUCT["Construct validity<br/>tone is not identical to climate commitment"]
      REPRO["Reproducibility<br/>job logs, artifacts, run configs, dashboards"]
      LIMIT["Limitations<br/>OCR quality, prompt sensitivity, annotation scale"]
      CONTRIBUTION["Contribution<br/>Indonesian ESG vocabulary and executable thesis pipeline"]
    end

    EXTRACT --> SILVER
    IMPORTED --> CLIMATE
    SILVER --> SAMPLE
    SAMPLE --> TONE_GT
    SAMPLE --> ESG_GT
    SAMPLE --> ASPECT_GT
    SAMPLE --> REVIEW
    TONE_GT --> CROSSTAB
    ESG_GT --> ONTO
    ASPECT_GT --> ONTO
    CLIMATE --> CROSSTAB
    PROXY --> CROSSTAB
    CROSSTAB --> KAPPA
    EXTRACT --> PROMPT_STAB
    EXTRACT --> MODEL_STAB
    EXTRACT --> FAILURE
    ONTO --> LIMIT
    PROMPT_STAB --> REPRO
    MODEL_STAB --> REPRO
    FAILURE --> LIMIT
    KAPPA --> CONSTRUCT
    ONTO --> CONTRIBUTION
    CONSTRUCT --> CH5["Chapter 5 Discussion"]
    REPRO --> CH6["Chapter 6 Conclusion"]
    LIMIT --> CH5
    LIMIT --> CH6
    CONTRIBUTION --> CH6
    """


def artifact_mermaid() -> str:
    return """flowchart LR
    subgraph SOURCE["A. Source Documents"]
      PDF["thesis_draft_1.pdf<br/>problem, literature, method, thesis spine"]
      DOCX["thesis_chapters_4_5_6.docx<br/>implementation, discussion, conclusion draft"]
      REPORTS["raw sustainability reports<br/>PDF disclosure corpus"]
    end

    subgraph RUNS["B. Execution Artifacts"]
      OCR_SUM["ocr_processing_summary csv<br/>document and page audit"]
      ESG_JSON["esg_records json<br/>LLM runs and extracted records"]
      JOB_DIRS["background job folders<br/>config, status, control, events"]
      CLIMATE_OUT["climatebert outputs<br/>local model predictions and resume progress"]
    end

    subgraph ANALYSIS["C. Analysis Tables"]
      TONE_FLAT["tone_records_flat csv<br/>record-level ABSA table"]
      TONE_ESG["tone_esg_crosstab csv<br/>tone by ESG pillar"]
      TONE_CB["tone_climatebert_label_crosstab csv<br/>tone by climate label"]
      MODEL_STAB["model_stability_summary csv<br/>provider and model performance"]
      PROMPT_STAB["prompt_stability_summary csv<br/>prompt reliability"]
      FAILURE["failure_mode_counts csv<br/>diagnostic categories"]
      ONTO["ontology_coverage csv<br/>mapped and novel aspects"]
      AGREEMENT["climatebert_proxy_agreement_summary csv<br/>agreement and kappa"]
    end

    subgraph PAGES["D. Streamlit Pages"]
      INTEGRATION["6_0 Integration Mermaid<br/>thesis map and lineage"]
      CH4["6_1 Chapter 4<br/>live implementation results"]
      CH5["6_2 Chapter 5<br/>live discussion claims"]
      CH6["6_3 Chapter 6<br/>live conclusion claims"]
      ACTION["3_0 Thesis Action Plan<br/>processing, migration, annotation"]
    end

    subgraph THESIS["E. Thesis Outputs"]
      FIGURES["figures and tables<br/>dashboard-ready charts"]
      CLAIMS["citation-backed paragraphs<br/>AP evidence references"]
      NOTES["empty analysis boxes<br/>manual interpretation updates"]
      DEFENSE["defense narrative<br/>RQ evidence, limitation, contribution"]
    end

    PDF --> INTEGRATION
    DOCX --> INTEGRATION
    REPORTS --> OCR_SUM
    REPORTS --> ESG_JSON
    OCR_SUM --> TONE_FLAT
    ESG_JSON --> TONE_FLAT
    JOB_DIRS --> MODEL_STAB
    ESG_JSON --> MODEL_STAB
    CLIMATE_OUT --> AGREEMENT
    CLIMATE_OUT --> TONE_CB
    TONE_FLAT --> TONE_ESG
    TONE_FLAT --> FAILURE
    TONE_FLAT --> ONTO
    TONE_FLAT --> PROMPT_STAB
    TONE_FLAT --> ACTION
    MODEL_STAB --> ACTION
    PROMPT_STAB --> ACTION
    TONE_ESG --> CH4
    TONE_CB --> CH4
    AGREEMENT --> CH5
    FAILURE --> CH5
    ONTO --> CH5
    MODEL_STAB --> CH6
    PROMPT_STAB --> CH6
    CH4 --> FIGURES
    CH5 --> CLAIMS
    CH6 --> CLAIMS
    ACTION --> NOTES
    INTEGRATION --> DEFENSE
    FIGURES --> DEFENSE
    CLAIMS --> DEFENSE
    NOTES --> DEFENSE
    """


def render_chapter_text(number: int, *, max_blocks: int | None = None) -> None:
    key = chapter_key(number)
    blocks = chapter_blocks(number)
    if not key:
        st.warning(f"Could not find Chapter {number} in `{DOCX_PATH}`.")
        return
    st.header(key)
    rendered = 0
    for block in blocks:
        if max_blocks is not None and rendered >= max_blocks:
            break
        text = block["text"]
        style = block["style"]
        if style == "Heading 2":
            st.subheader(text)
        elif style == "Heading 3":
            st.markdown(f"#### {text}")
        elif text.lower().startswith(("figure ", "table ")):
            st.caption(text)
        else:
            st.write(text)
        rendered += 1


def workflow_rq_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"rq": "RQ1", "stage": "PDF-to-structured ESG", "implemented_modules": 4, "artifact_groups": 5},
            {"rq": "RQ2", "stage": "Aspect/pillar/sentiment/tone schema", "implemented_modules": 3, "artifact_groups": 4},
            {"rq": "RQ3", "stage": "Tone vs ClimateBERT", "implemented_modules": 3, "artifact_groups": 3},
            {"rq": "RQ4", "stage": "Diagnostics", "implemented_modules": 3, "artifact_groups": 4},
            {"rq": "RQ5", "stage": "Reproducibility", "implemented_modules": 3, "artifact_groups": 4},
            {"rq": "RQ6", "stage": "Stability", "implemented_modules": 3, "artifact_groups": 3},
        ]
    )


def artifact_inventory() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not RESULTS.exists():
        return pd.DataFrame()
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
        elif "thesis_workflow_dashboard" in rel.parts:
            group = "Workflow dashboard"
        else:
            group = "Core results"
        rows.append({"path": str(rel), "group": group, "extension": path.suffix.lower().lstrip(".") or "none"})
    return pd.DataFrame(rows)


def load_esg_record_runs() -> list[dict[str, Any]]:
    data = load_json(RESULTS / "esg_records.json", [])
    return data if isinstance(data, list) else []


def record_value(record: dict[str, Any], *keys: str) -> str:
    if not isinstance(record, dict):
        return ""
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            value = "|".join(str(item) for item in value if str(item).strip())
        if str(value or "").strip():
            return str(value).strip()
    return ""


def derive_live_model_stability() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
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
                    if isinstance(record, dict)
                    and not record_value(record, "tone", "tone_pred", "disclosure_tone")
                ),
                "schema_drift": any(
                    isinstance(record, dict)
                    and not record_value(record, "text", "sentence", "statement", "disclosure", "evidence")
                    for record in records
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
            schema_drift_rate=("schema_drift", "mean"),
        )
        .reset_index()
    )
    grouped["missing_tone_rate"] = grouped.apply(
        lambda row: (row["missing_tone_count"] / row["record_total"]) if row["record_total"] else 0,
        axis=1,
    )
    grouped["source"] = "results/esg_records.json"
    return grouped[
        [
            "model",
            "runs",
            "json_parse_success_rate",
            "avg_records",
            "missing_tone_rate",
            "schema_drift_rate",
            "source",
        ]
    ]


def combine_model_stability(static_df: pd.DataFrame, live_df: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not static_df.empty:
        static = static_df.copy()
        if "source" not in static.columns:
            static["source"] = "results/revision_analysis/model_stability_summary.csv"
        frames.append(static)
    if not live_df.empty:
        live = live_df.copy()
        if not static_df.empty and {"model", "source"}.issubset(static_df.columns):
            already_migrated = set(
                static_df.loc[
                    static_df["source"].astype(str).eq("live_reprocess"),
                    "model",
                ].astype(str)
            )
            live = live[~live["model"].astype(str).isin(already_migrated)]
        frames.append(live)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    for col in ["runs", "json_parse_success_rate", "avg_records", "missing_tone_rate", "schema_drift_rate"]:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")
    return combined


def data_bundle() -> dict[str, pd.DataFrame]:
    static_model_stability = load_csv(REVISION / "model_stability_summary.csv")
    live_model_stability = derive_live_model_stability()
    return {
        "tone_records": load_csv(VIS / "tone_records_flat.csv"),
        "tone_esg": load_csv(VIS / "tone_esg_crosstab.csv"),
        "tone_climatebert": load_csv(VIS / "tone_climatebert_label_crosstab.csv"),
        "model_stability": combine_model_stability(static_model_stability, live_model_stability),
        "model_stability_static": static_model_stability,
        "model_stability_live": live_model_stability,
        "prompt_stability": load_csv(REVISION / "prompt_stability_summary.csv"),
        "failure_counts": load_csv(REVISION / "failure_mode_counts.csv"),
        "ontology": load_csv(REVISION / "ontology_coverage.csv"),
        "agreement": load_csv(REVISION / "climatebert_proxy_agreement_summary.csv"),
        "ocr": load_csv(REVISION / "ocr_processing_summary.csv"),
        "greenwashing": load_csv(REVISION / "greenwashing_index_by_company.csv"),
        "climatebert_remote": load_csv(VIS / "climatebert_remote_flat.csv"),
        "inventory": artifact_inventory(),
    }


def metric_row(bundle: dict[str, pd.DataFrame]) -> None:
    tone = bundle["tone_records"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    inventory = bundle["inventory"]
    cols = st.columns(6)
    cols[0].metric("Tone records", f"{len(tone):,}")
    cols[1].metric("Documents", f"{tone['target_doc'].nunique() if 'target_doc' in tone.columns else 0:,}")
    cols[2].metric("Prompts", f"{tone['prompt'].nunique() if 'prompt' in tone.columns else 0:,}")
    kappa = pd.to_numeric(agreement.get("cohen_kappa", pd.Series(dtype=float)), errors="coerce")
    cols[3].metric("Proxy kappa", f"{kappa.iloc[0]:.3f}" if not kappa.empty and pd.notna(kappa.iloc[0]) else "n/a")
    mapped = int(ontology.get("mapped_to_ontology", pd.Series(dtype=bool)).astype(bool).sum()) if not ontology.empty and "mapped_to_ontology" in ontology.columns else 0
    cols[4].metric("Ontology mapped", f"{mapped}/{len(ontology):,}" if len(ontology) else "n/a")
    cols[5].metric("Artifacts", f"{len(inventory):,}")


def evidence_metrics(bundle: dict[str, pd.DataFrame]) -> dict[str, Any]:
    tone = bundle["tone_records"]
    ocr = bundle["ocr"]
    agreement = bundle["agreement"]
    ontology = bundle["ontology"]
    inventory = bundle["inventory"]
    model_stability = bundle["model_stability"]
    prompt_stability = bundle["prompt_stability"]
    live_runs = load_esg_record_runs()

    extracted_from_runs = 0
    ok_runs = 0
    for run in live_runs:
        if isinstance(run, dict):
            ok_runs += int(bool(run.get("ok")))
            records = run.get("records") if isinstance(run.get("records"), list) else []
            extracted_from_runs += len(records)

    kappa = numeric_series(agreement, "cohen_kappa")
    percent_agreement = numeric_series(agreement, "percent_agreement")
    mapped = int(ontology.get("mapped_to_ontology", pd.Series(dtype=bool)).astype(bool).sum()) if not ontology.empty and "mapped_to_ontology" in ontology.columns else 0
    pages = numeric_series(ocr, "pages").sum() if not ocr.empty else 0

    return {
        "tone_records": len(tone),
        "documents": tone["target_doc"].nunique() if not tone.empty and "target_doc" in tone.columns else len(ocr),
        "ocr_documents": len(ocr),
        "ocr_pages": pages,
        "prompts": tone["prompt"].nunique() if not tone.empty and "prompt" in tone.columns else 0,
        "models": model_stability["model"].astype(str).nunique() if not model_stability.empty and "model" in model_stability.columns else 0,
        "live_runs": len(live_runs),
        "ok_live_runs": ok_runs,
        "live_extracted_rows": extracted_from_runs,
        "artifacts": len(inventory),
        "ontology_mapped": mapped,
        "ontology_total": len(ontology),
        "kappa": kappa.iloc[0] if not kappa.empty else float("nan"),
        "percent_agreement": percent_agreement.iloc[0] if not percent_agreement.empty else float("nan"),
    }


def citation_table(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    m = evidence_metrics(bundle)
    return pd.DataFrame(
        [
            {
                "citation_id": "[AP-ESG]",
                "source": "results/visualizations/tone_records_flat.csv",
                "claim": f"{fmt_int(m['tone_records'])} structured ESG/tone records across {fmt_int(m['documents'])} documents and {fmt_int(m['prompts'])} prompt templates.",
            },
            {
                "citation_id": "[AP-OCR]",
                "source": "results/revision_analysis/ocr_processing_summary.csv",
                "claim": f"{fmt_int(m['ocr_documents'])} OCR documents and {fmt_int(m['ocr_pages'])} OCR pages are represented in the processing summary.",
            },
            {
                "citation_id": "[AP-RUNS]",
                "source": "results/esg_records.json",
                "claim": f"{fmt_int(m['live_runs'])} live LLM run objects, {fmt_int(m['ok_live_runs'])} successful runs, and {fmt_int(m['live_extracted_rows'])} extracted records are available from Action Plan reprocessing.",
            },
            {
                "citation_id": "[AP-MODEL]",
                "source": "results/revision_analysis/model_stability_summary.csv + results/esg_records.json",
                "claim": f"{fmt_int(m['models'])} model configurations are visible in the combined static/live model-stability table.",
            },
            {
                "citation_id": "[AP-CBERT]",
                "source": "results/revision_analysis/climatebert_proxy_agreement_summary.csv",
                "claim": f"Tone-vs-ClimateBERT proxy agreement is {fmt_pct(m['percent_agreement'])}, with Cohen's kappa of {fmt_rate(m['kappa'])}.",
            },
            {
                "citation_id": "[AP-ONTO]",
                "source": "results/revision_analysis/ontology_coverage.csv",
                "claim": f"{fmt_int(m['ontology_mapped'])} of {fmt_int(m['ontology_total'])} aspect rows are currently mapped to the ontology.",
            },
            {
                "citation_id": "[AP-ART]",
                "source": "results/*",
                "claim": f"{fmt_int(m['artifacts'])} result artifacts are currently discoverable under the results directory.",
            },
        ]
    )


def model_results_table(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df = bundle["model_stability"]
    if df.empty:
        return pd.DataFrame()
    cols = [
        col
        for col in ["model", "runs", "json_parse_success_rate", "avg_records", "missing_tone_rate", "schema_drift_rate", "source"]
        if col in df.columns
    ]
    out = df[cols].copy()
    if "runs" in out.columns:
        out = out.sort_values("runs", ascending=False)
    return out


def generated_chapter4_paragraph(bundle: dict[str, pd.DataFrame]) -> str:
    m = evidence_metrics(bundle)
    return (
        "The current implementation evidence shows that the pipeline has transformed "
        f"{fmt_int(m['ocr_documents'])} OCR documents ({fmt_int(m['ocr_pages'])} OCR pages) into "
        f"{fmt_int(m['tone_records'])} structured ESG/tone records across {fmt_int(m['documents'])} source documents "
        f"and {fmt_int(m['prompts'])} prompt templates [AP-OCR; AP-ESG]. "
        f"The live Action Plan run store contributes {fmt_int(m['live_runs'])} LLM run objects and "
        f"{fmt_int(m['live_extracted_rows'])} extracted records, while the combined model-stability table contains "
        f"{fmt_int(m['models'])} model configurations [AP-RUNS; AP-MODEL]. "
        "These figures support Chapter 4 as an implementation-and-results chapter because each empirical claim can be "
        "traced back to a concrete artifact rather than a manually rewritten summary."
    )


def generated_chapter5_paragraph(bundle: dict[str, pd.DataFrame]) -> str:
    m = evidence_metrics(bundle)
    return (
        "The discussion should interpret the results as a construct-validity comparison rather than a simple accuracy contest. "
        f"The current tone-vs-ClimateBERT proxy table reports {fmt_pct(m['percent_agreement'])} agreement and "
        f"Cohen's kappa of {fmt_rate(m['kappa'])}, which indicates that climate commitment labels and disclosure-tone labels "
        "overlap but are not identical constructs [AP-CBERT]. "
        f"Ontology coverage remains partial, with {fmt_int(m['ontology_mapped'])} of {fmt_int(m['ontology_total'])} aspect rows mapped, "
        "so unmapped Indonesian ESG vocabulary should be discussed as both a limitation and a thesis contribution [AP-ONTO]."
    )


def generated_chapter6_paragraph(bundle: dict[str, pd.DataFrame]) -> str:
    m = evidence_metrics(bundle)
    return (
        "The conclusion can state that the thesis has produced a reproducible empirical workflow, not only a conceptual framework. "
        f"The current artifact inventory contains {fmt_int(m['artifacts'])} result files, while the Action Plan evidence covers "
        f"{fmt_int(m['tone_records'])} structured records, {fmt_int(m['models'])} visible model configurations, and "
        f"{fmt_int(m['prompts'])} prompt templates [AP-ART; AP-ESG; AP-MODEL]. "
        "The strongest future-work claims should therefore focus on expanding expert-labelled ground truth, improving ontology coverage, "
        "and broadening repeated-run model/prompt stability tests."
    )


def render_generated_claim_box(key: str, generated: str, title: str = "Generated thesis claim") -> None:
    st.markdown(f"#### {title}")
    st.markdown(generated)
    note = st.text_area(
        "Your revised interpretation / analysis note",
        value="",
        placeholder="Write your updated thesis interpretation here when the result changes. Leave empty to keep the generated claim above.",
        height=180,
        key=key,
    )
    if note.strip():
        st.success("Custom analysis note captured in this Streamlit session.")
        st.markdown("**Current custom note**")
        st.write(note)


def render_citation_panel(bundle: dict[str, pd.DataFrame], *, height: int = 260) -> None:
    st.markdown("#### Result Citations")
    st.dataframe(citation_table(bundle), use_container_width=True, hide_index=True, height=height)


def hbar(df: pd.DataFrame, y: str, x: str = "count", title: str = "", color: str = "#2f6f73", height: int = 320) -> None:
    if df.empty or y not in df.columns or x not in df.columns:
        st.info("No data available for this chart.")
        return
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{x}:Q", title=x.replace("_", " ").title()),
        y=alt.Y(f"{y}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=300)),
        tooltip=list(df.columns),
        color=alt.value(color),
    ).properties(title=title, height=height)
    st.altair_chart(chart, use_container_width=True)


def count_chart(df: pd.DataFrame, col: str, title: str, top_n: int | None = None) -> None:
    if df.empty or col not in df.columns:
        st.info("No data available for this chart.")
        return
    counts = df[col].map(clean).replace("", "missing").value_counts().rename_axis(col).reset_index(name="count")
    if top_n:
        counts = counts.head(top_n)
    hbar(counts, col, title=title)


def heatmap_from_table(df: pd.DataFrame, row_col: str, title: str) -> None:
    if df.empty or row_col not in df.columns:
        st.info("No data available for this heatmap.")
        return
    melted = df.melt(id_vars=[row_col], var_name="column", value_name="count")
    melted["count"] = pd.to_numeric(melted["count"], errors="coerce").fillna(0)
    chart = alt.Chart(melted).mark_rect().encode(
        x=alt.X("column:N", title=None, axis=alt.Axis(labelAngle=-35)),
        y=alt.Y(f"{row_col}:N", title=None),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=[row_col, "column", "count"],
    ).properties(title=title, height=320)
    text = alt.Chart(melted).mark_text(fontSize=11).encode(
        x="column:N",
        y=f"{row_col}:N",
        text=alt.Text("count:Q", format=".0f"),
        color=alt.condition(alt.datum.count > max(float(melted["count"].max()), 1) * 0.55, alt.value("white"), alt.value("#111827")),
    )
    st.altair_chart(chart + text, use_container_width=True)


def workflow_coverage_chart() -> None:
    df = workflow_rq_df()
    melted = df.melt(id_vars=["rq", "stage"], value_vars=["implemented_modules", "artifact_groups"], var_name="metric", value_name="count")
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X("count:Q", title="Count"),
        y=alt.Y("stage:N", sort=None, title=None, axis=alt.Axis(labelLimit=280)),
        color=alt.Color("metric:N", title="Metric"),
        tooltip=["rq", "stage", "metric", "count"],
        row=alt.Row("metric:N", title=None),
    ).properties(height=170)
    st.altair_chart(chart, use_container_width=True)


def pdf_prompt_heatmap(tone_records: pd.DataFrame) -> None:
    if tone_records.empty or not {"target_doc", "prompt"}.issubset(tone_records.columns):
        st.info("No PDF x prompt records available.")
        return
    grouped = tone_records.groupby(["target_doc", "prompt"], dropna=False).size().reset_index(name="records")
    chart = alt.Chart(grouped).mark_rect().encode(
        x=alt.X("prompt:N", title="Prompt", axis=alt.Axis(labelAngle=-35, labelLimit=180)),
        y=alt.Y("target_doc:N", title="PDF / source document", axis=alt.Axis(labelLimit=260)),
        color=alt.Color("records:Q", scale=alt.Scale(scheme="tealblues")),
        tooltip=["target_doc", "prompt", "records"],
    ).properties(height=min(560, max(260, 26 * grouped["target_doc"].nunique())))
    st.altair_chart(chart, use_container_width=True)


def ontology_chart(df: pd.DataFrame) -> None:
    if df.empty or not {"aspect", "records"}.issubset(df.columns):
        st.info("No ontology coverage data available.")
        return
    plot = df.copy()
    plot["records"] = pd.to_numeric(plot["records"], errors="coerce").fillna(0)
    plot["mapped"] = plot.get("mapped_to_ontology", False).astype(bool).map({True: "Mapped", False: "Unmapped"})
    plot = plot.sort_values("records", ascending=False).head(20)
    chart = alt.Chart(plot).mark_bar().encode(
        x=alt.X("records:Q", title="Records"),
        y=alt.Y("aspect:N", sort="-x", title=None, axis=alt.Axis(labelLimit=280)),
        color=alt.Color("mapped:N", scale=alt.Scale(range=["#3f7c85", "#b45309"])),
        tooltip=["aspect", "records", "mapped", "suggested_path"],
    ).properties(title="Ontology coverage by aspect", height=460)
    st.altair_chart(chart, use_container_width=True)


def model_stability_chart(df: pd.DataFrame) -> None:
    if df.empty or "model" not in df.columns:
        st.info("No model stability data available.")
        return
    cols = [c for c in ["json_parse_success_rate", "avg_records", "missing_tone_rate", "schema_drift_rate"] if c in df.columns]
    plot = df[["model"] + cols].copy()
    for col in cols:
        plot[col] = pd.to_numeric(plot[col], errors="coerce")
    melted = plot.melt(id_vars=["model"], value_vars=cols, var_name="metric", value_name="value")
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X("value:Q", title="Value"),
        y=alt.Y("model:N", title=None, axis=alt.Axis(labelLimit=260)),
        color=alt.Color("metric:N"),
        tooltip=["model", "metric", "value"],
        row=alt.Row("metric:N", title=None),
    ).properties(height=120)
    st.altair_chart(chart, use_container_width=True)


def prompt_stability_chart(df: pd.DataFrame) -> None:
    if df.empty or "prompt" not in df.columns:
        st.info("No prompt stability data available.")
        return
    cols = [c for c in ["runs", "missing_tone_rate", "schema_drift_rate", "field_completion_rate"] if c in df.columns]
    plot = df[["prompt"] + cols].copy()
    for col in cols:
        plot[col] = pd.to_numeric(plot[col], errors="coerce")
    melted = plot.melt(id_vars=["prompt"], value_vars=cols, var_name="metric", value_name="value")
    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X("value:Q", title="Value"),
        y=alt.Y("prompt:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
        color=alt.Color("metric:N"),
        tooltip=["prompt", "metric", "value"],
        row=alt.Row("metric:N", title=None),
    ).properties(height=170)
    st.altair_chart(chart, use_container_width=True)


def artifact_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No artifact inventory available.")
        return
    c1, c2 = st.columns(2)
    with c1:
        count_chart(df, "group", "Artifact count by result group")
    with c2:
        count_chart(df, "extension", "Artifact count by file type")


def agreement_chart(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No ClimateBERT agreement data available.")
        return
    row = df.iloc[0]
    metrics = pd.DataFrame(
        [
            {"metric": "Percent agreement", "value": pd.to_numeric(row.get("percent_agreement"), errors="coerce")},
            {"metric": "Cohen kappa", "value": pd.to_numeric(row.get("cohen_kappa"), errors="coerce")},
            {"metric": "Tone commitment rate", "value": pd.to_numeric(row.get("tone_commitment_rate"), errors="coerce")},
            {"metric": "Climate label rate", "value": pd.to_numeric(row.get("climate_commitment_label_rate"), errors="coerce")},
        ]
    )
    chart = alt.Chart(metrics).mark_bar(color="#395b91").encode(
        x=alt.X("value:Q", title="Value"),
        y=alt.Y("metric:N", sort=None, title=None),
        tooltip=["metric", "value"],
    ).properties(title="ClimateBERT/proxy agreement metrics", height=250)
    st.altair_chart(chart, use_container_width=True)


def image_or_info(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"Missing image: `{path.relative_to(ROOT)}`")
