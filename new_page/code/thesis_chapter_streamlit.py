from __future__ import annotations

from pathlib import Path
import json
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
    return f"""
    <div class="mermaid">
    {escaped}
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{
        startOnLoad: true,
        securityLevel: 'loose',
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
    PDFS["Sustainability report PDFs"] --> OCR["Bulk OCR<br/>pages + markdown"]
    OCR --> PAGES["thesis_dataset/*/pages/page_XXXX.md"]
    PAGES --> PROMPTS["Seven prompt templates<br/>zero-shot, few-shot, CoT<br/>English + Indonesian"]
    PROMPTS --> LLM["LLM extraction jobs<br/>OpenRouter / LM Studio / Ollama"]
    LLM --> JSON["esg_records.json / JSONL runs"]
    JSON --> FLAT["tone_records_flat.csv<br/>332 evidence records"]
    FLAT --> ABSA["ABSA dimensions<br/>aspect, ESG, sentiment, tone"]
    FLAT --> CBERTR["ClimateBERT comparison<br/>proxy + real labels"]
    FLAT --> ONTO["Ontology mapping<br/>GRI/SASB path + Indonesian-specific aspects"]
    FLAT --> DIAG["Diagnostics<br/>missing tone, schema drift, failure modes"]
    ABSA --> CH4["Chapter IV results graphs"]
    CBERTR --> CH4
    ONTO --> CH4
    DIAG --> CH5["Chapter V discussion"]
    CH4 --> CH6["Chapter VI contributions and future work"]
    """


def validation_mermaid() -> str:
    return """flowchart TD
    EXTRACT["LLM extracted records"] --> SILVER["Silver dataset<br/>silver_tone_ground_truth.csv"]
    SILVER --> HUMAN["Pilot human annotation<br/>tone, ESG, aspect, status"]
    SILVER --> CLIMATE["ClimateBERT run<br/>resume unprocessed records"]
    HUMAN --> KAPPA["Agreement metrics<br/>human vs LLM"]
    CLIMATE --> CKB["ClimateBERT kappa<br/>tone vs climate commitment"]
    EXTRACT --> STABILITY["Prompt/model stability<br/>parse success, missing tone, schema drift"]
    EXTRACT --> FAIL["Failure mode audit"]
    KAPPA --> VALIDITY["Construct validity argument"]
    CKB --> VALIDITY
    STABILITY --> RELIABILITY["Reliability and reproducibility"]
    FAIL --> LIMITS["Limitations and future work"]
    VALIDITY --> CH5["Chapter V"]
    RELIABILITY --> CH6["Chapter VI"]
    LIMITS --> CH6
    """


def artifact_mermaid() -> str:
    return """flowchart LR
    DOCX["thesis_chapters_4_5_6.docx"] --> PAGES["Streamlit chapter pages<br/>6_1, 6_2, 6_3"]
    PDF["thesis_draft_1.pdf"] --> MAP["Integrated thesis map page"]
    REV["results/revision_analysis/*.csv"] --> PAGES
    VIS["results/visualizations/*.csv + *.png"] --> PAGES
    JOBS["background job folders<br/>status.json + events.jsonl"] --> MAP
    PAGES --> DASH["Interactive evidence dashboard"]
    MAP --> DASH
    DASH --> THESIS["Thesis defense narrative<br/>RQs -> evidence -> interpretation -> contributions"]
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


def data_bundle() -> dict[str, pd.DataFrame]:
    return {
        "tone_records": load_csv(VIS / "tone_records_flat.csv"),
        "tone_esg": load_csv(VIS / "tone_esg_crosstab.csv"),
        "tone_climatebert": load_csv(VIS / "tone_climatebert_label_crosstab.csv"),
        "model_stability": load_csv(REVISION / "model_stability_summary.csv"),
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
