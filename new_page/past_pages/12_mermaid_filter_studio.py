from __future__ import annotations

import base64
import json
from pathlib import Path
import re
import sys
import zlib

import streamlit as st


st.set_page_config(page_title="Mermaid Filter Studio", layout="wide")


APP_ROOT = Path(__file__).resolve().parents[1]
SESSION_ROOT = APP_ROOT / "data" / "mermaid_filter_sessions"
sys.path.insert(0, str(APP_ROOT / "code"))

from thesis_chapter_streamlit import render_mermaid  # noqa: E402


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


def ensure_session_dir() -> None:
    SESSION_ROOT.mkdir(parents=True, exist_ok=True)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def extract_chapter_label(node_label: str) -> str:
    match = re.match(r"^([IVXLCDM]+)", clean_text(node_label), flags=re.IGNORECASE)
    if match:
        return f"Chapter {match.group(1).upper()}"
    return "Other"


def roman_to_int(roman: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    roman = roman.upper()
    total = 0
    previous = 0
    for char in reversed(roman):
        value = values.get(char, 0)
        if value < previous:
            total -= value
        else:
            total += value
            previous = value
    return total


def chapter_sort_key(chapter_label: str) -> tuple[int, str]:
    match = re.search(r"Chapter\s+([IVXLCDM]+)", chapter_label, flags=re.IGNORECASE)
    if not match:
        return (10**9, chapter_label)
    return (roman_to_int(match.group(1)), chapter_label)


def mermaid_label(text: str) -> str:
    return text.replace('"', '\\"')


def build_mermaid_live_url(mermaid_code: str, edit_mode: bool = True) -> str:
    if not clean_text(mermaid_code):
        return ""

    payload = {
        "code": mermaid_code,
        "mermaid": {"theme": "default"},
    }
    payload_bytes = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(payload_bytes) + compressor.flush()
    encoded = base64.b64encode(compressed).decode("ascii").replace("+", "-").replace("/", "_")
    mode = "edit" if edit_mode else "view"
    return f"https://mermaid.ai/live/{mode}#pako:{encoded}"


def list_session_files() -> list[str]:
    ensure_session_dir()
    return sorted(path.name for path in SESSION_ROOT.glob("*.json"))


def session_path_from_name(name: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip()).strip("_")
    safe_name = safe_name or "mermaid_session"
    return SESSION_ROOT / f"{safe_name}.json"


def parse_mermaid_source(mermaid_text: str) -> tuple[dict[str, str], list[dict[str, str]]]:
    nodes: dict[str, str] = {}
    edges: list[dict[str, str]] = []

    node_pattern = re.compile(r'^(?P<node_id>\S+)\s*\["(?P<label>.*)"\]\s*$')
    labeled_edge_pattern = re.compile(
        r'^(?P<source>\S+)\s*--\s*"(?P<label>.*?)"\s*-->\s*(?P<target>\S+)\s*$'
    )
    plain_edge_pattern = re.compile(r"^(?P<source>\S+)\s*-->\s*(?P<target>\S+)\s*$")

    for raw_line in (mermaid_text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("flowchart") or line.startswith("subgraph ") or line == "end":
            continue

        node_match = node_pattern.match(line)
        if node_match:
            nodes[node_match.group("node_id")] = clean_text(node_match.group("label"))
            continue

        labeled_edge_match = labeled_edge_pattern.match(line)
        if labeled_edge_match:
            edges.append(
                {
                    "source_id": labeled_edge_match.group("source"),
                    "target_id": labeled_edge_match.group("target"),
                    "explanation": clean_text(labeled_edge_match.group("label")),
                }
            )
            continue

        plain_edge_match = plain_edge_pattern.match(line)
        if plain_edge_match:
            edges.append(
                {
                    "source_id": plain_edge_match.group("source"),
                    "target_id": plain_edge_match.group("target"),
                    "explanation": "",
                }
            )

    return nodes, edges


def parse_mermaid_source_with_subgraphs(
    mermaid_text: str,
) -> tuple[dict[str, str], list[dict[str, str]], dict[str, str], dict[str, str]]:
    nodes, edges = parse_mermaid_source(mermaid_text)
    subgraph_titles: dict[str, str] = {}
    node_to_subgraph: dict[str, str] = {}
    current_subgraph_id = ""

    subgraph_pattern = re.compile(r'^\s*subgraph\s+(?P<subgraph_id>\S+)\s*\["(?P<label>.*)"\]\s*$')
    node_pattern = re.compile(r'^\s*(?P<node_id>\S+)\s*\["(?P<label>.*)"\]\s*$')

    for raw_line in (mermaid_text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("flowchart"):
            continue
        if line == "end":
            current_subgraph_id = ""
            continue

        subgraph_match = subgraph_pattern.match(line)
        if subgraph_match:
            current_subgraph_id = subgraph_match.group("subgraph_id")
            subgraph_titles[current_subgraph_id] = clean_text(subgraph_match.group("label"))
            continue

        node_match = node_pattern.match(line)
        if node_match and current_subgraph_id:
            node_to_subgraph[node_match.group("node_id")] = current_subgraph_id

    return nodes, edges, subgraph_titles, node_to_subgraph


def list_subgraphs(
    subgraph_titles: dict[str, str],
    node_to_subgraph: dict[str, str],
) -> list[str]:
    present_ids = set(node_to_subgraph.values())
    return [
        subgraph_id
        for subgraph_id, _ in sorted(subgraph_titles.items(), key=lambda item: item[1].lower())
        if subgraph_id in present_ids
    ]


def list_notes_from_subgraphs(
    nodes: dict[str, str],
    node_to_subgraph: dict[str, str],
    selected_subgraphs: list[str] | None = None,
) -> list[str]:
    selected_set = set(selected_subgraphs or [])
    labels = []
    for node_id, label in nodes.items():
        subgraph_id = node_to_subgraph.get(node_id, "")
        if not selected_set or subgraph_id in selected_set:
            labels.append(label)
    return sorted(labels)


def list_chapters_from_nodes(nodes: dict[str, str]) -> list[str]:
    return sorted({extract_chapter_label(label) for label in nodes.values()}, key=chapter_sort_key)


def list_notes_from_nodes(nodes: dict[str, str], selected_chapters: list[str] | None = None) -> list[str]:
    selected_set = set(selected_chapters or [])
    labels = []
    for label in nodes.values():
        chapter = extract_chapter_label(label)
        if not selected_set or chapter in selected_set:
            labels.append(label)
    return sorted(labels)


def filter_mermaid_graph(
    nodes: dict[str, str],
    edges: list[dict[str, str]],
    selected_subgraphs: list[str],
    selected_notes: list[str],
    filter_mode: str,
    node_to_subgraph: dict[str, str],
) -> tuple[dict[str, str], list[dict[str, str]]]:
    selected_subgraph_set = set(selected_subgraphs)
    selected_note_set = set(selected_notes)
    filtered_edges = []

    for edge in edges:
        source_label = nodes.get(edge["source_id"], edge["source_id"])
        target_label = nodes.get(edge["target_id"], edge["target_id"])
        source_subgraph = node_to_subgraph.get(edge["source_id"], "")
        target_subgraph = node_to_subgraph.get(edge["target_id"], "")

        if filter_mode == "Only cross-subgraph connections" and source_subgraph == target_subgraph:
            continue

        if selected_subgraph_set:
            if filter_mode == "Only selected subgraphs":
                if source_subgraph not in selected_subgraph_set or target_subgraph not in selected_subgraph_set:
                    continue
            else:
                if source_subgraph not in selected_subgraph_set and target_subgraph not in selected_subgraph_set:
                    continue

        if selected_note_set and (source_label not in selected_note_set or target_label not in selected_note_set):
            continue

        filtered_edges.append(edge)

    visible_node_ids = []
    for edge in filtered_edges:
        if edge["source_id"] not in visible_node_ids:
            visible_node_ids.append(edge["source_id"])
        if edge["target_id"] not in visible_node_ids:
            visible_node_ids.append(edge["target_id"])

    filtered_nodes = {node_id: nodes[node_id] for node_id in visible_node_ids if node_id in nodes}
    return filtered_nodes, filtered_edges


def build_filtered_mermaid(
    nodes: dict[str, str],
    edges: list[dict[str, str]],
    subgraph_titles: dict[str, str],
    node_to_subgraph: dict[str, str],
) -> str:
    if not nodes or not edges:
        return ""

    subgraph_to_nodes: dict[str, list[tuple[str, str]]] = {}
    for node_id, label in nodes.items():
        subgraph_id = node_to_subgraph.get(node_id, "UNGROUPED")
        subgraph_to_nodes.setdefault(subgraph_id, []).append((node_id, label))

    lines = ["flowchart LR"]
    for subgraph_id in sorted(
        subgraph_to_nodes.keys(),
        key=lambda value: subgraph_titles.get(value, value).lower(),
    ):
        subgraph_title = subgraph_titles.get(subgraph_id, subgraph_id)
        lines.append(f'  subgraph {subgraph_id}["{mermaid_label(subgraph_title)}"]')
        for node_id, label in sorted(subgraph_to_nodes[subgraph_id], key=lambda item: item[1]):
            lines.append(f'    {node_id}["{mermaid_label(label)}"]')
        lines.append("  end")

    for edge in edges:
        if edge["explanation"]:
            lines.append(
                f'  {edge["source_id"]} -- "{mermaid_label(edge["explanation"])}" --> {edge["target_id"]}'
            )
        else:
            lines.append(f'  {edge["source_id"]} --> {edge["target_id"]}')

    return "\n".join(lines)


def init_state() -> None:
    if "mermaid_filter_input_text" not in st.session_state:
        st.session_state.mermaid_filter_input_text = integrated_thesis_mermaid_raw()
    if "mermaid_filter_session_name" not in st.session_state:
        st.session_state.mermaid_filter_session_name = "mermaid_workflow"
    if "mermaid_filter_mode" not in st.session_state:
        st.session_state.mermaid_filter_mode = "Include cross-subgraph links"
    if "mermaid_filter_selected_chapters" not in st.session_state:
        st.session_state.mermaid_filter_selected_chapters = []
    if "mermaid_filter_selected_notes" not in st.session_state:
        st.session_state.mermaid_filter_selected_notes = []
    if "mermaid_filter_pending_payload" not in st.session_state:
        st.session_state.mermaid_filter_pending_payload = None
    if "mermaid_filter_flash_message" not in st.session_state:
        st.session_state.mermaid_filter_flash_message = ""


def apply_pending_payload() -> None:
    payload = st.session_state.get("mermaid_filter_pending_payload")
    if not payload:
        return

    st.session_state.mermaid_filter_session_name = str(payload.get("session_name", "loaded_mermaid_session"))
    st.session_state.mermaid_filter_input_text = str(payload.get("mermaid_source", ""))
    st.session_state.mermaid_filter_mode = str(payload.get("filter_mode", "Include cross-chapter links"))
    st.session_state.mermaid_filter_selected_chapters = list(payload.get("selected_chapters", []))
    st.session_state.mermaid_filter_selected_notes = list(payload.get("selected_notes", []))
    st.session_state.mermaid_filter_pending_payload = None


def build_session_payload() -> dict[str, object]:
    return {
        "session_name": st.session_state.mermaid_filter_session_name,
        "mermaid_source": st.session_state.mermaid_filter_input_text,
        "filter_mode": st.session_state.mermaid_filter_mode,
        "selected_chapters": st.session_state.mermaid_filter_selected_chapters,
        "selected_notes": st.session_state.mermaid_filter_selected_notes,
    }


def load_session_payload(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


init_state()
apply_pending_payload()


st.title("Mermaid Filter Studio")
st.markdown(
    "Load or paste Mermaid source, then filter the integrated graph by actual Mermaid subgraphs and notes, regenerate a cleaner Mermaid graph, and open it in Mermaid Live."
)

session_files = list_session_files()
session_col1, session_col2 = st.columns([2, 1])
with session_col1:
    st.text_input("Session name", key="mermaid_filter_session_name")
with session_col2:
    selected_session_file = st.selectbox("Load existing session", [""] + session_files)

session_action_col1, session_action_col2, session_action_col3 = st.columns(3)
with session_action_col1:
    if st.button("New session", use_container_width=True):
        st.session_state.mermaid_filter_input_text = integrated_thesis_mermaid_raw()
        st.session_state.mermaid_filter_selected_chapters = []
        st.session_state.mermaid_filter_selected_notes = []
        st.session_state.mermaid_filter_mode = "Include cross-subgraph links"
        st.rerun()
with session_action_col2:
    if st.button("Load session", use_container_width=True, disabled=not selected_session_file):
        st.session_state.mermaid_filter_pending_payload = load_session_payload(SESSION_ROOT / selected_session_file)
        st.session_state.mermaid_filter_flash_message = f"Loaded `{selected_session_file}`"
        st.rerun()
with session_action_col3:
    if st.button("Save session", use_container_width=True):
        payload = build_session_payload()
        target_path = session_path_from_name(st.session_state.mermaid_filter_session_name)
        ensure_session_dir()
        target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
        st.success(f"Saved `{target_path.name}`")

if st.session_state.mermaid_filter_flash_message:
    st.success(st.session_state.mermaid_filter_flash_message)
    st.session_state.mermaid_filter_flash_message = ""

st.text_area(
    "Mermaid source",
    key="mermaid_filter_input_text",
    height=360,
    placeholder="Paste full Mermaid source here, for example `flowchart LR ...`",
)

source_action_col1, source_action_col2 = st.columns(2)
with source_action_col1:
    if st.button("Load integrated thesis graph", use_container_width=True):
        st.session_state.mermaid_filter_input_text = integrated_thesis_mermaid_raw()
        st.session_state.mermaid_filter_selected_chapters = []
        st.session_state.mermaid_filter_selected_notes = []
        st.rerun()
with source_action_col2:
    if st.button("Clear source", use_container_width=True):
        st.session_state.mermaid_filter_input_text = ""
        st.session_state.mermaid_filter_selected_chapters = []
        st.session_state.mermaid_filter_selected_notes = []
        st.rerun()

nodes, edges, subgraph_titles, node_to_subgraph = parse_mermaid_source_with_subgraphs(
    st.session_state.mermaid_filter_input_text
)

if not nodes and not edges:
    st.info("Paste Mermaid source to begin filtering.")
else:
    subgraph_options = list_subgraphs(subgraph_titles, node_to_subgraph)
    filter_mode = st.radio(
        "Mermaid subgraph filter mode",
        ["Include cross-subgraph links", "Only selected subgraphs", "Only cross-subgraph connections"],
        horizontal=True,
        key="mermaid_filter_mode",
    )
    default_selected_subgraphs = [
        subgraph_id
        for subgraph_id in st.session_state.mermaid_filter_selected_chapters
        if subgraph_id in subgraph_options
    ] or subgraph_options
    subgraph_labels = {subgraph_id: subgraph_titles.get(subgraph_id, subgraph_id) for subgraph_id in subgraph_options}
    selected_subgraphs = st.multiselect(
        "Subgraphs to show in Mermaid",
        subgraph_options,
        default=default_selected_subgraphs,
        format_func=lambda value: subgraph_labels.get(value, value),
        key="mermaid_filter_selected_chapters_widget",
    )
    st.session_state.mermaid_filter_selected_chapters = selected_subgraphs
    note_options = list_notes_from_subgraphs(nodes, node_to_subgraph, selected_subgraphs)
    default_selected_notes = [
        note for note in st.session_state.mermaid_filter_selected_notes if note in note_options
    ] or note_options
    selected_notes = st.multiselect(
        "Notes to show in Mermaid",
        note_options,
        default=default_selected_notes,
        key="mermaid_filter_selected_notes_widget",
    )
    st.session_state.mermaid_filter_selected_notes = selected_notes

    filtered_nodes, filtered_edges = filter_mermaid_graph(
        nodes,
        edges,
        selected_subgraphs,
        selected_notes,
        st.session_state.mermaid_filter_mode,
        node_to_subgraph,
    )
    filtered_mermaid = build_filtered_mermaid(filtered_nodes, filtered_edges, subgraph_titles, node_to_subgraph)

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Nodes", len(filtered_nodes))
    metric_col2.metric("Edges", len(filtered_edges))
    metric_col3.metric("Subgraphs", len({node_to_subgraph.get(node_id, "") for node_id in filtered_nodes}))

    st.subheader("Filtered Mermaid Preview")
    if filtered_mermaid:
        preview_height = max(560, min(1800, 260 + len(filtered_nodes) * 42))
        render_mermaid(filtered_mermaid, height=preview_height)
        live_url = build_mermaid_live_url(filtered_mermaid, edit_mode=True)
        if live_url:
            st.markdown(f"[Open filtered Mermaid in Mermaid Live]({live_url})")
    else:
        st.info("No nodes or edges remain after applying the current filters.")
