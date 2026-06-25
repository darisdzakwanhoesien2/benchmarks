from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Mermaid Sequence Filter Studio", layout="wide")


APP_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = APP_ROOT / "documentation" / "streamlit_pages" / "mermaid_sequence_diagram"
sys.path.insert(0, str(APP_ROOT / "code"))

from thesis_chapter_streamlit import render_mermaid  # noqa: E402


MERMAID_BLOCK_RE = re.compile(r"```mermaid\n(?P<body>[\s\S]*?)\n```")
METADATA_RE = re.compile(r"^- (?P<key>[^:]+):\s*`(?P<value>.*?)`\s*$")
ACTOR_RE = re.compile(r"^\s*actor\s+(?P<id>\w+)(?:\s+as\s+(?P<label>.+))?\s*$")
PARTICIPANT_RE = re.compile(r"^\s*participant\s+(?P<id>\w+)(?:\s+as\s+(?P<label>.+))?\s*$")
MESSAGE_RE = re.compile(
    r"^\s*(?P<source>\w+)\s*(?P<arrow>-{1,2}>{1,2}|<{1,2}-{1,2}|-{1,2}x>{1,2}|<{1,2}x-{1,2})\s*(?P<target>\w+)\s*:\s*(?P<label>.+)\s*$"
)
NOTE_RE = re.compile(r"^\s*Note\s+over\s+(?P<targets>[^:]+)\s*:\s*(?P<label>.+)\s*$")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


@st.cache_data(show_spinner=False)
def load_sequence_docs() -> list[dict[str, object]]:
    docs: list[dict[str, object]] = []
    if not DOCS_ROOT.exists():
        return docs

    for path in sorted(DOCS_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = MERMAID_BLOCK_RE.search(text)
        if not match:
            continue

        metadata: dict[str, str] = {}
        for line in text.splitlines():
            md_match = METADATA_RE.match(line.strip())
            if md_match:
                metadata[clean_text(md_match.group("key")).lower()] = clean_text(md_match.group("value"))

        title = clean_text(text.splitlines()[0].lstrip("#")) if text.splitlines() else path.stem
        mermaid = match.group("body").strip()
        participants = parse_sequence_participants(mermaid)
        docs.append(
            {
                "path": path,
                "filename": path.name,
                "title": title or path.stem,
                "page_slug": metadata.get("page slug", path.stem),
                "category": metadata.get("category", "uncategorized"),
                "purpose": metadata.get("purpose", ""),
                "summary": metadata.get("summary", ""),
                "source_path": metadata.get("source path", ""),
                "mermaid": mermaid,
                "participants": participants,
                "participant_ids": [item["id"] for item in participants],
            }
        )

    return docs


def parse_sequence_participants(mermaid_text: str) -> list[dict[str, str]]:
    participants: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_line in mermaid_text.splitlines():
        line = raw_line.strip()
        match = ACTOR_RE.match(line) or PARTICIPANT_RE.match(line)
        if not match:
            continue
        participant_id = match.group("id")
        if participant_id in seen:
            continue
        seen.add(participant_id)
        label = clean_text(match.group("label") or participant_id)
        kind = "actor" if line.startswith("actor ") else "participant"
        participants.append({"id": participant_id, "label": label, "kind": kind})
    return participants


def filter_docs(
    docs: list[dict[str, object]],
    categories: list[str],
    query: str,
) -> list[dict[str, object]]:
    selected_categories = set(categories)
    query_text = clean_text(query).lower()
    filtered: list[dict[str, object]] = []

    for doc in docs:
        if selected_categories and str(doc["category"]) not in selected_categories:
            continue
        haystack = " ".join(
            [
                str(doc["title"]),
                str(doc["filename"]),
                str(doc["page_slug"]),
                str(doc["purpose"]),
                str(doc["summary"]),
            ]
        ).lower()
        if query_text and query_text not in haystack:
            continue
        filtered.append(doc)

    return filtered


def build_doc_rows(docs: list[dict[str, object]]) -> pd.DataFrame:
    rows = []
    for doc in docs:
        rows.append(
            {
                "title": str(doc["title"]),
                "filename": str(doc["filename"]),
                "page slug": str(doc["page_slug"]),
                "category": str(doc["category"]),
                "participants": len(doc["participants"]),
                "purpose": str(doc["purpose"]),
                "summary": str(doc["summary"]),
            }
        )
    return pd.DataFrame(rows)


def build_participant_label_map(participants: list[dict[str, str]]) -> dict[str, str]:
    return {item["id"]: f'{item["label"]} ({item["id"]})' for item in participants}


def filter_sequence_mermaid(
    mermaid_text: str,
    selected_participants: list[str],
    filter_mode: str,
) -> str:
    if not clean_text(mermaid_text):
        return ""

    selected = set(selected_participants)
    visible_ids: set[str] = set()
    kept_lines: list[str] = ["sequenceDiagram"]
    declaration_lines: list[str] = []
    body_lines: list[str] = []

    for raw_line in mermaid_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped == "sequenceDiagram":
            continue

        actor_match = ACTOR_RE.match(stripped)
        participant_match = PARTICIPANT_RE.match(stripped)
        if actor_match or participant_match:
            declaration_lines.append(stripped)
            continue

        message_match = MESSAGE_RE.match(stripped)
        if message_match:
            source = message_match.group("source")
            target = message_match.group("target")
            if not selected:
                visible_ids.update([source, target])
                body_lines.append(stripped)
                continue

            if filter_mode == "Only selected participants":
                if source in selected and target in selected:
                    visible_ids.update([source, target])
                    body_lines.append(stripped)
            else:
                if source in selected or target in selected:
                    visible_ids.update([source, target])
                    body_lines.append(stripped)
            continue

        note_match = NOTE_RE.match(stripped)
        if note_match:
            note_targets = [clean_text(item) for item in note_match.group("targets").split(",")]
            target_set = {item for item in note_targets if item}
            if not selected:
                visible_ids.update(target_set)
                body_lines.append(stripped)
                continue

            if filter_mode == "Only selected participants":
                if target_set and target_set.issubset(selected):
                    visible_ids.update(target_set)
                    body_lines.append(stripped)
            else:
                if not target_set or target_set & selected:
                    visible_ids.update(target_set)
                    body_lines.append(stripped)
            continue

        body_lines.append(stripped)

    if selected:
        visible_ids.update(selected)

    for declaration in declaration_lines:
        match = ACTOR_RE.match(declaration) or PARTICIPANT_RE.match(declaration)
        if not match:
            continue
        if match.group("id") in visible_ids:
            kept_lines.append(f"    {declaration}")

    for body_line in body_lines:
        kept_lines.append(f"    {body_line}")

    return "\n".join(kept_lines)


docs = load_sequence_docs()

st.title("Mermaid Sequence Filter Studio")
st.markdown(
    "Browse Mermaid `sequenceDiagram` blocks from `documentation/streamlit_pages/mermaid_sequence_diagram`, then filter interactions by page, category, and participant."
)

if not docs:
    st.error(f"No Mermaid sequence markdown files found in `{DOCS_ROOT}`.")
    st.stop()

all_categories = sorted({str(doc["category"]) for doc in docs})
sidebar = st.sidebar
sidebar.header("Filters")
selected_categories = sidebar.multiselect("Categories", all_categories, default=all_categories)
query = sidebar.text_input("Search pages", placeholder="title, slug, purpose")

filtered_docs = filter_docs(docs, selected_categories, query)

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Markdown files", len(filtered_docs))
metric_col2.metric("Categories", len({str(doc["category"]) for doc in filtered_docs}))
metric_col3.metric("Sequence diagrams", len(filtered_docs))

if not filtered_docs:
    st.info("No markdown pages match the current filters.")
    st.stop()

st.subheader("Available Markdown Sequence Diagrams")
st.dataframe(build_doc_rows(filtered_docs), use_container_width=True, hide_index=True)

doc_options = {f'{doc["title"]} [{doc["filename"]}]': doc for doc in filtered_docs}
selected_label = st.selectbox("Choose a markdown diagram", list(doc_options.keys()))
selected_doc = doc_options[selected_label]

participants = list(selected_doc["participants"])
participant_labels = build_participant_label_map(participants)
default_participants = [item["id"] for item in participants]

info_col1, info_col2 = st.columns([2, 1])
with info_col1:
    st.markdown(f'**Purpose**: {selected_doc["purpose"] or "n/a"}')
    st.markdown(f'**Summary**: {selected_doc["summary"] or "n/a"}')
    st.markdown(f'**Source**: `{selected_doc["source_path"] or selected_doc["filename"]}`')
with info_col2:
    st.markdown(f'**Category**: `{selected_doc["category"]}`')
    st.markdown(f'**Page slug**: `{selected_doc["page_slug"]}`')
    st.markdown(f'**Markdown**: `{selected_doc["filename"]}`')

filter_mode = st.radio(
    "Participant filter mode",
    ["Include linked participants", "Only selected participants"],
    horizontal=True,
)
selected_participants = st.multiselect(
    "Participants to show",
    options=[item["id"] for item in participants],
    default=default_participants,
    format_func=lambda item: participant_labels.get(item, item),
)

filtered_mermaid = filter_sequence_mermaid(
    str(selected_doc["mermaid"]),
    selected_participants,
    filter_mode,
)

preview_height = max(520, min(1400, 240 + len(filtered_mermaid.splitlines()) * 26))
st.subheader("Filtered Sequence Diagram")
render_mermaid(filtered_mermaid, height=preview_height)

with st.expander("Participant Inventory", expanded=False):
    st.dataframe(
        pd.DataFrame(participants).rename(columns={"id": "participant id", "label": "label", "kind": "kind"}),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Markdown Source", expanded=False):
    st.code(Path(selected_doc["path"]).read_text(encoding="utf-8"), language="markdown")
