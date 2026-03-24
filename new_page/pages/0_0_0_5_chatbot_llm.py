import streamlit as st
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pear AI Chatbot",
    page_icon="🤖",
    layout="wide",
)

# ── Constants ──────────────────────────────────────────────────────────────────
DATA_DIR         = Path(__file__).parent.parent / "data"
CHAT_HISTORY_DIR = DATA_DIR / "chat_history"
CHAT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_API_URL   = "https://openrouter.ai/api/v1/chat/completions"
LMSTUDIO_DEFAULT_URL = "http://localhost:1234/v1"
CHUNK_PREVIEW_LEN    = 300

# Context budget constants
CHARS_PER_TOKEN      = 4
SYSTEM_PROMPT_TOKENS = 800
HISTORY_TOKENS       = 1024
CONTEXT_TOKEN_RATIO  = 0.5
DEFAULT_CTX_TOKENS   = 4096

# Chunking defaults
CHUNK_SIZE_DEFAULT    = 512
CHUNK_OVERLAP_DEFAULT = 50

# Context thresholds for auto-chunking decision
CHUNKING_REQUIRED_CTX   = 8_192    # ctx ≤ this → chunking ON by default
CHUNKING_OPTIONAL_CTX   = 32_768   # ctx ≤ this → chunking optional (user decides)
                                    # ctx >  this → chunking OFF by default

# Chunking strategies
CHUNK_STRATEGY_TOKEN     = "Token"
CHUNK_STRATEGY_SENTENCE  = "Sentence"
CHUNK_STRATEGY_PARAGRAPH = "Paragraph"
CHUNK_STRATEGIES         = [CHUNK_STRATEGY_TOKEN, CHUNK_STRATEGY_SENTENCE, CHUNK_STRATEGY_PARAGRAPH]


# ── Backend enum ───────────────────────────────────────────────────────────────
BACKEND_OPENROUTER = "OpenRouter"
BACKEND_LMSTUDIO   = "LM Studio (Local)"


# ══════════════════════════════════════════════════════════════════════════════
# API KEY
# ══════════════════════════════════════════════════════════════════════════════

def _get_api_key() -> str:
    # 1. Session state (user typed it in)
    if st.session_state.get("api_key", "").strip():
        return st.session_state["api_key"].strip()
    # 2. Env / .env fallback
    try:
        from config.settings import settings
        for attr in ("OPENROUTER_API_KEY", "openrouter_api_key", "api_key"):
            val = getattr(settings, attr, None)
            if val and str(val).strip():
                return str(val).strip()
    except Exception:
        pass
    return os.getenv("OPENROUTER_API_KEY", "")


# ══════════════════════════════════════════════════════════════════════════════
# OPENROUTER MODEL FETCHER  (ported from grading_lab.py)
# ══════════════════════════════════════════════════════════════════════════════

def _FALLBACK_MODELS() -> list[dict]:
    return [
        {"id": "meta-llama/llama-3.1-8b-instruct:free",   "label": "Llama 3.1 8B",       "free": True,  "notes": "free · 131,072 ctx", "ctx": 131072},
        {"id": "meta-llama/llama-3.3-70b-instruct:free",   "label": "Llama 3.3 70B",       "free": True,  "notes": "free · 131,072 ctx", "ctx": 131072},
        {"id": "mistralai/mistral-7b-instruct:free",       "label": "Mistral 7B",           "free": True,  "notes": "free · 32,768 ctx",  "ctx": 32768},
        {"id": "google/gemma-3-27b-it:free",               "label": "Gemma 3 27B",          "free": True,  "notes": "free · 131,072 ctx", "ctx": 131072},
        {"id": "deepseek/deepseek-r1:free",                "label": "DeepSeek R1",          "free": True,  "notes": "free · 65,536 ctx",  "ctx": 65536},
        {"id": "openai/gpt-4o-mini",                       "label": "GPT-4o Mini",          "free": False, "notes": "$0.150/1M · 128,000 ctx", "ctx": 128000},
        {"id": "openai/gpt-4o",                            "label": "GPT-4o",               "free": False, "notes": "$2.500/1M · 128,000 ctx", "ctx": 128000},
        {"id": "anthropic/claude-3.5-sonnet",              "label": "Claude 3.5 Sonnet",    "free": False, "notes": "$3.000/1M · 200,000 ctx", "ctx": 200000},
        {"id": "anthropic/claude-3.5-haiku",               "label": "Claude 3.5 Haiku",     "free": False, "notes": "$0.800/1M · 200,000 ctx", "ctx": 200000},
        {"id": "google/gemini-flash-1.5",                  "label": "Gemini 1.5 Flash",     "free": False, "notes": "$0.075/1M · 1,000,000 ctx", "ctx": 1000000},
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_openrouter_models() -> list[dict]:
    api_key = _get_api_key()
    if not api_key:
        return _FALLBACK_MODELS()
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer":  "https://pear-edtech.app",
                "X-Title":       "Pear EdTech Chatbot",
            },
            timeout=10,
        )
        resp.raise_for_status()
        raw = resp.json().get("data", [])

        models = []
        for m in raw:
            mid     = m.get("id", "")
            name    = m.get("name", mid)
            ctx     = m.get("context_length", 0)
            pricing = m.get("pricing", {})
            try:
                p_cost  = float(pricing.get("prompt",     1))
                c_cost  = float(pricing.get("completion", 1))
                is_free = p_cost == 0.0 and c_cost == 0.0
            except (ValueError, TypeError):
                is_free = str(pricing.get("prompt", "1")) == "0"

            if is_free:
                cost_str = "free"
            else:
                try:
                    cost_str = f"${float(pricing.get('prompt', 0)) * 1_000_000:.3f}/1M"
                except Exception:
                    cost_str = "paid"

            ctx_str = f"{ctx:,} ctx" if ctx else ""
            notes   = " · ".join(filter(None, [cost_str, ctx_str]))
            models.append({"id": mid, "label": name, "free": is_free, "notes": notes, "ctx": ctx})

        models.sort(key=lambda x: (not x["free"], x["label"].lower()))
        return models if models else _FALLBACK_MODELS()

    except Exception:
        return _FALLBACK_MODELS()


# ══════════════════════════════════════════════════════════════════════════════
# CONVERSATION PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════

def _session_path(session_id: str) -> Path:
    return CHAT_HISTORY_DIR / f"{session_id}.json"


def save_conversation(session_id: str, messages: list[dict], metadata: dict) -> None:
    data = {
        "session_id":  session_id,
        "metadata":    metadata,
        "updated_at":  datetime.now().isoformat(),
        "messages":    messages,
    }
    _session_path(session_id).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_conversation(session_id: str) -> dict | None:
    p = _session_path(session_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def list_conversations() -> list[dict]:
    """Return saved sessions sorted newest-first."""
    sessions = []
    for fp in sorted(CHAT_HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            sessions.append({
                "session_id":  data.get("session_id", fp.stem),
                "title":       data.get("metadata", {}).get("title", fp.stem),
                "model":       data.get("metadata", {}).get("model", ""),
                "updated_at":  data.get("updated_at", ""),
                "msg_count":   len(data.get("messages", [])),
            })
        except Exception:
            continue
    return sessions


def delete_conversation(session_id: str) -> None:
    p = _session_path(session_id)
    if p.exists():
        p.unlink()


def new_session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def derive_title(messages: list[dict]) -> str:
    """Use the first user message as the conversation title."""
    for m in messages:
        if m.get("role") == "user":
            text = m["content"].strip().replace("\n", " ")
            return text[:60] + "…" if len(text) > 60 else text
    return "Untitled conversation"


# ══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE LOADING
# ══════════════════════════════════════════════════════════════════════════════

def load_json_file(filepath: Path) -> dict | list | None:
    try:
        return json.loads(filepath.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_html_file(filepath: Path) -> str:
    try:
        soup = BeautifulSoup(filepath.read_text(encoding="utf-8"), "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return ""


def flatten_json(obj, prefix="") -> str:
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            lines.append(flatten_json(v, f"{prefix}{k} > " if prefix else f"{k} > "))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            lines.append(flatten_json(v, f"{prefix}[{i}] "))
    else:
        lines.append(f"{prefix.rstrip(' > ')}: {obj}")
    return "\n".join(lines)


def extract_text_from_file(filepath: Path) -> str:
    ext = filepath.suffix.lower()
    if ext == ".json":
        data = load_json_file(filepath)
        return flatten_json(data) if data is not None else ""
    elif ext in (".html", ".htm"):
        return load_html_file(filepath)
    elif ext == ".txt":
        try:
            return filepath.read_text(encoding="utf-8")
        except Exception:
            return ""
    elif ext == ".tex":
        try:
            text = filepath.read_text(encoding="utf-8")
            text = re.sub(r"\\[a-zA-Z]+\*?(\[.*?\])*\{(.*?)\}", r"\2", text)
            text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
            text = re.sub(r"[{}]", " ", text)
            text = re.sub(r"%.*", "", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        except Exception:
            return ""
    elif ext == ".bib":
        try:
            text = filepath.read_text(encoding="utf-8")
            text = re.sub(r"@\w+\{", "", text)
            text = re.sub(r"[{}]", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text
        except Exception:
            return ""
    elif ext == ".csv":
        try:
            df   = pd.read_csv(filepath, on_bad_lines="skip")
            # Keep only text-like columns, drop empty
            text_cols = [c for c in df.columns if df[c].dtype == object]
            if not text_cols:
                return ""
            rows = []
            for _, row in df[text_cols].iterrows():
                parts = [f"{col}: {str(val).strip()}" for col, val in row.items() if str(val).strip() not in ("", "nan")]
                if parts:
                    rows.append(" | ".join(parts))
            return "\n".join(rows)
        except Exception:
            return ""
    return ""


def friendly_label(fp: Path) -> str:
    """Return a human-readable label relative to DATA_DIR."""
    try:
        return str(fp.relative_to(DATA_DIR))
    except ValueError:
        return fp.name


def get_category_hierarchy(fp: Path) -> tuple[str, str, str]:
    """
    Return (category, subcategory, display_path) for a file.

    category    → top-level folder   e.g. 'litmap_references'
    subcategory → second-level folder e.g. 'Video Uniderstanding'
    display_path → full relative path  e.g. 'litmap_references/Video Uniderstanding/untitled.bib'
    """
    try:
        rel_parts = fp.relative_to(DATA_DIR).parts
    except ValueError:
        return "general", "", fp.name

    category    = rel_parts[0] if len(rel_parts) > 1 else "general"
    subcategory = rel_parts[1] if len(rel_parts) > 2 else ""
    display_path = str(fp.relative_to(DATA_DIR))
    return category, subcategory, display_path


@st.cache_data(show_spinner="Loading knowledge base…")
def load_all_documents() -> list[dict]:
    docs, seen = [], set()
    for pattern in [
        "**/*.json",
        "**/*.html",
        "**/*.htm",
        "**/*.txt",
        "**/*.tex",
        "**/*.bib",
        "**/*.csv",       # ← added
    ]:
        for fp in sorted(DATA_DIR.glob(pattern)):
            if CHAT_HISTORY_DIR in fp.parents:
                continue
            if fp in seen:
                continue
            seen.add(fp)
            text = extract_text_from_file(fp).strip()
            if not text:
                continue
            category, subcategory, display_path = get_category_hierarchy(fp)
            docs.append({
                "label":       friendly_label(fp),
                "path":        str(fp),
                "text":        text,
                "category":    category,
                "subcategory": subcategory,
                "filename":    fp.name,
            })
    return docs


# ══════════════════════════════════════════════════════════════════════════════
# CHUNKING
# ══════════════════════════════════════════════════════════════════════════════

def should_chunk_by_default(model_ctx: int) -> bool:
    """Return True if model context is small enough to require chunking."""
    return model_ctx <= CHUNKING_REQUIRED_CTX


def chunk_text_by_token(
    text: str,
    chunk_size_tokens: int = CHUNK_SIZE_DEFAULT,
    overlap_tokens: int    = CHUNK_OVERLAP_DEFAULT,
) -> list[str]:
    """Split text into overlapping token-based chunks."""
    chunk_size_chars = chunk_size_tokens * CHARS_PER_TOKEN
    overlap_chars    = overlap_tokens    * CHARS_PER_TOKEN

    if len(text) <= chunk_size_chars:
        return [text]

    chunks, start = [], 0
    while start < len(text):
        end = start + chunk_size_chars
        chunks.append(text[start:end])
        start += chunk_size_chars - overlap_chars
        if start >= len(text):
            break
    return chunks


def chunk_text_by_sentence(
    text: str,
    chunk_size_tokens: int = CHUNK_SIZE_DEFAULT,
    overlap_tokens: int    = CHUNK_OVERLAP_DEFAULT,
) -> list[str]:
    """
    Split text into chunks at sentence boundaries.
    Groups sentences until chunk_size is reached, then starts a new chunk.
    Overlap carries the last N chars from the previous chunk.
    """
    chunk_size_chars = chunk_size_tokens * CHARS_PER_TOKEN
    overlap_chars    = overlap_tokens    * CHARS_PER_TOKEN

    # Split on sentence-ending punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [text]

    chunks, current, current_len = [], [], 0
    for sent in sentences:
        sent_len = len(sent)
        if current_len + sent_len > chunk_size_chars and current:
            chunk_text_str = " ".join(current)
            chunks.append(chunk_text_str)
            # Overlap: keep tail of previous chunk
            overlap_text = chunk_text_str[-overlap_chars:] if overlap_chars else ""
            current      = [overlap_text, sent] if overlap_text else [sent]
            current_len  = len(overlap_text) + sent_len
        else:
            current.append(sent)
            current_len += sent_len

    if current:
        chunks.append(" ".join(current))

    return chunks if chunks else [text]


def chunk_text_by_paragraph(
    text: str,
    chunk_size_tokens: int = CHUNK_SIZE_DEFAULT,
    overlap_tokens: int    = CHUNK_OVERLAP_DEFAULT,
) -> list[str]:
    """
    Split text at paragraph boundaries (double newline).
    Groups paragraphs until chunk_size is reached.
    """
    chunk_size_chars = chunk_size_tokens * CHARS_PER_TOKEN
    overlap_chars    = overlap_tokens    * CHARS_PER_TOKEN

    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]

    if not paragraphs:
        return [text]

    chunks, current, current_len = [], [], 0
    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > chunk_size_chars and current:
            chunk_text_str = "\n\n".join(current)
            chunks.append(chunk_text_str)
            overlap_text = chunk_text_str[-overlap_chars:] if overlap_chars else ""
            current      = [overlap_text, para] if overlap_text else [para]
            current_len  = len(overlap_text) + para_len
        else:
            current.append(para)
            current_len += para_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks if chunks else [text]


def chunk_text(
    text: str,
    strategy: str          = CHUNK_STRATEGY_TOKEN,
    chunk_size_tokens: int = CHUNK_SIZE_DEFAULT,
    overlap_tokens: int    = CHUNK_OVERLAP_DEFAULT,
) -> list[str]:
    """Dispatch to the correct chunking strategy."""
    if strategy == CHUNK_STRATEGY_SENTENCE:
        return chunk_text_by_sentence(text, chunk_size_tokens, overlap_tokens)
    elif strategy == CHUNK_STRATEGY_PARAGRAPH:
        return chunk_text_by_paragraph(text, chunk_size_tokens, overlap_tokens)
    else:
        return chunk_text_by_token(text, chunk_size_tokens, overlap_tokens)


def chunk_documents(
    docs: list[dict],
    chunk_size_tokens: int = CHUNK_SIZE_DEFAULT,
    overlap_tokens: int    = CHUNK_OVERLAP_DEFAULT,
    strategy: str          = CHUNK_STRATEGY_TOKEN,
) -> list[dict]:
    """Explode each document into chunk-docs using the selected strategy."""
    chunked = []
    for doc in docs:
        pieces = chunk_text(doc["text"], strategy, chunk_size_tokens, overlap_tokens)
        for i, piece in enumerate(pieces):
            chunk_label = f"{doc['label']}#chunk{i+1}" if len(pieces) > 1 else doc["label"]
            chunked.append({
                **doc,
                "text":         piece,
                "label":        chunk_label,
                "parent_label": doc["label"],
                "chunk_index":  i + 1,
                "chunk_total":  len(pieces),
            })
    return chunked


# ══════════════════════════════════════════════════════════════════════════════
# RETRIEVAL
# ══════════════════════════════════════════════════════════════════════════════

def simple_keyword_score(query: str, text: str) -> float:
    tokens = re.findall(r"\w+", query.lower())
    if not tokens:
        return 0.0
    text_lower = text.lower()
    return sum(text_lower.count(t) for t in tokens) / len(tokens)


def retrieve_top_docs(query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
    scored = [(simple_keyword_score(query, d["text"]), d) for d in docs]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for score, d in scored[:top_k] if score > 0]


def estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 characters."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def get_context_budget(active_m: dict | None, backend: str) -> int:
    """
    Calculate max characters available for KB context,
    accounting for model ctx limit, system prompt, and chat history.
    """
    if active_m and active_m.get("ctx", 0) > 0:
        ctx_tokens = active_m["ctx"]
    else:
        ctx_tokens = DEFAULT_CTX_TOKENS

    # Reserve tokens for system prompt template + chat history + safety margin
    reserved   = SYSTEM_PROMPT_TOKENS + HISTORY_TOKENS + 256
    available  = max(512, ctx_tokens - reserved)
    budget_tokens = int(available * CONTEXT_TOKEN_RATIO)
    return budget_tokens * CHARS_PER_TOKEN   # return as chars


def build_context(retrieved: list[dict], max_chars: int) -> str:
    """Build context string within the given character budget."""
    parts, budget = [], max_chars
    for d in retrieved:
        header  = f"--- Reference: {d['label']} ---\n"
        snippet = d["text"][: max(100, budget - len(header))]
        block   = header + snippet
        if budget - len(block) < 0:
            # Still include a truncated version if there's room for the header
            if budget > len(header) + 100:
                block = header + d["text"][: budget - len(header)]
                parts.append(block)
            break
        parts.append(block)
        budget -= len(block)
    return "\n\n".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# RENDERING
# ══════════════════════════════════════════════════════════════════════════════

def render_message_with_citations(content: str, docs_index: dict) -> None:
    """
    Render assistant message with [REF: label] citations highlighted.
    Citations are replaced with clickable superscript-style badges,
    and a footnote list is appended at the bottom.
    """
    # Find all unique citations in order of appearance
    all_citations = re.findall(r"\[REF:\s*(.+?)\]", content)
    unique_citations = list(dict.fromkeys(all_citations))  # preserve order, dedupe

    if not unique_citations:
        st.markdown(content)
        return

    # Build citation index: label → number
    citation_map = {label: i + 1 for i, label in enumerate(unique_citations)}

    # Replace [REF: label] with inline badge ¹ ² ³ …
    def replace_ref(match):
        label = match.group(1).strip()
        num   = citation_map.get(label, "?")
        return f" `[{num}]`"

    rendered = re.sub(r"\[REF:\s*(.+?)\]", replace_ref, content)
    st.markdown(rendered)

    # Render footnotes
    st.markdown("---")
    st.markdown("**References:**")
    for label, num in citation_map.items():
        doc = docs_index.get(label)
        if doc:
            preview = doc["text"][:120].replace("\n", " ")
            st.markdown(f"`[{num}]` **{label}**  \n> _{preview}…_")
        else:
            st.markdown(f"`[{num}]` **{label}**")


# ══════════════════════════════════════════════════════════════════════════════
# OPENROUTER CALL
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_TEMPLATE = """\
You are Pear, a knowledgeable and helpful AI assistant.
You answer questions accurately and concisely based on the provided knowledge base.

You have access to a set of reference documents. Relevant excerpts are provided below.

INSTRUCTIONS:
1. Base your answer **primarily on the provided references**. Do not fabricate information.
2. You MUST cite EVERY reference block you use with this exact inline format: [REF: <label>]
   where <label> is copied EXACTLY from the "Reference: <label>" header of that block.
   Example: [REF: documents/Survey_Paper_IndoNLP/sections/1_introduction.tex]
3. Place the citation immediately after the sentence that uses the information.
4. If multiple references support the same point, cite all of them: [REF: a] [REF: b]
5. If the references do not contain enough information to answer confidently, say so honestly \
and indicate what additional information would be needed.
6. Structure your response clearly:
   - Use bullet points or numbered lists for multi-part answers.
   - Use headers (##) for long answers with distinct sections.
   - Keep answers concise unless depth is explicitly requested.
7. Maintain a neutral, professional tone. Do not speculate beyond what the references support.

KNOWLEDGE BASE:
{context}
"""


def call_openrouter(
    messages: list[dict],
    model: str,
    api_key: str,
    temperature: float = 0.3,
) -> tuple[str, list[str]]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://pear-edtech.app",
        "X-Title":       "Pear EdTech Chatbot",
    }
    payload = {"model": model, "messages": messages, "temperature": temperature}
    resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    reply = resp.json()["choices"][0]["message"]["content"]
    cited = re.findall(r"\[REF:\s*(.+?)\]", reply)
    return reply, cited


# ══════════════════════════════════════════════════════════════════════════════
# LM STUDIO HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def fetch_lmstudio_models(base_url: str) -> list[dict]:
    """Fetch locally loaded models from LM Studio's OpenAI-compatible /v1/models endpoint."""
    try:
        resp = requests.get(
            f"{base_url.rstrip('/')}/models",
            timeout=5,
        )
        resp.raise_for_status()
        raw = resp.json().get("data", [])
        models = []
        for m in raw:
            mid = m.get("id", "")
            models.append({
                "id":    mid,
                "label": mid,          # LM Studio uses filename/path as id
                "free":  True,         # local = free
                "notes": "local · LM Studio",
                "ctx":   m.get("context_length", 0),
            })
        return models if models else []
    except requests.ConnectionError:
        return []
    except Exception:
        return []


def call_lmstudio(
    messages: list[dict],
    model: str,
    base_url: str,
    temperature: float = 0.3,
) -> tuple[str, list[str]]:
    """Call LM Studio via its OpenAI-compatible chat completions endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"

    # LM Studio ignores the model field but still requires a valid payload.
    # Some versions reject unknown model IDs with 400 — omit it to be safe.
    payload: dict = {
        "messages":    messages,
        "temperature": temperature,
        "stream":      False,
    }
    # Only include model if it looks like a local path/filename LM Studio knows
    if model and "/" not in model:
        payload["model"] = model

    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.HTTPError as e:
        # Surface the actual LM Studio error body for easier debugging
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise requests.HTTPError(
            f"{e} — LM Studio response: {detail}", response=resp
        ) from e

    reply = resp.json()["choices"][0]["message"]["content"]
    cited = re.findall(r"\[REF:\s*(.+?)\]", reply)
    return reply, cited


# ══════════════════════════════════════════════════════════════════════════════
# UNIFIED LLM CALL
# ══════════════════════════════════════════════════════════════════════════════

def call_llm(
    messages: list[dict],
    model: str,
    backend: str,
    api_key: str = "",
    lmstudio_url: str = LMSTUDIO_DEFAULT_URL,
    temperature: float = 0.3,
) -> tuple[str, list[str]]:
    if backend == BACKEND_LMSTUDIO:
        return call_lmstudio(messages, model, lmstudio_url, temperature)
    else:
        return call_openrouter(messages, model, api_key, temperature)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT  (add new keys)
# ══════════════════════════════════════════════════════════════════════════════

_DEFAULTS = {
    "api_key":           "",
    "messages":          [],
    "session_id":        new_session_id(),
    "active_model_id":   "meta-llama/llama-3.1-8b-instruct:free",
    "backend":           BACKEND_OPENROUTER,
    "lmstudio_url":      LMSTUDIO_DEFAULT_URL,
    "lmstudio_model_id": "",
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.title("🤖 Pear AI Chatbot")
    st.caption("Ask anything — powered by OpenRouter or LM Studio with local knowledge base.")

    # ── Load OpenRouter models ─────────────────────────────────────────────────
    with st.spinner("🔄 Loading models from OpenRouter…"):
        all_or_models = fetch_openrouter_models()

    free_models = [m for m in all_or_models if     m["free"]]
    paid_models = [m for m in all_or_models if not m["free"]]
    id_to_model = {m["id"]: m for m in all_or_models}

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:

        # ── Backend selector ───────────────────────────────────────────────────
        st.header("🖥️ Backend")
        backend = st.radio(
            "LLM Backend",
            [BACKEND_OPENROUTER, BACKEND_LMSTUDIO],
            index=0 if st.session_state.backend == BACKEND_OPENROUTER else 1,
            horizontal=True,
        )
        st.session_state.backend = backend

        # ── API Key (OpenRouter only) ──────────────────────────────────────────
        if backend == BACKEND_OPENROUTER:
            st.subheader("🔑 API Key")
            api_key_input = st.text_input(
                "OpenRouter API Key",
                type="password",
                value=st.session_state.get("api_key", ""),
                help="Get your key at https://openrouter.ai/keys",
            )
            if api_key_input:
                st.session_state["api_key"] = api_key_input

            effective_key = _get_api_key()
            if effective_key:
                st.success("✅ API key set")
            else:
                st.error("❌ API key missing")

            if st.button("🔄 Refresh Model List", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

            st.caption(
                f"**{len(all_or_models)}** models · "
                f"{len(free_models)} 🆓 free · {len(paid_models)} 💳 paid"
            )
        else:
            effective_key = ""

        # ── LM Studio config ───────────────────────────────────────────────────
        if backend == BACKEND_LMSTUDIO:
            st.subheader("🏠 LM Studio")
            lmstudio_url = st.text_input(
                "Server URL",
                value=st.session_state.lmstudio_url,
                help="Default: http://localhost:1234/v1",
            )
            st.session_state.lmstudio_url = lmstudio_url

            lms_models = fetch_lmstudio_models(lmstudio_url)
            if lms_models:
                st.success(f"✅ Connected · {len(lms_models)} model(s) loaded")
                id_to_model.update({m["id"]: m for m in lms_models})
            else:
                st.error("❌ Cannot reach LM Studio — is it running?")
                st.caption("Enable: LM Studio → Local Server → Start Server")

        st.divider()

        # ── Model selector ─────────────────────────────────────────────────────
        st.header("🤖 Model")

        if backend == BACKEND_LMSTUDIO:
            lms_models = fetch_lmstudio_models(st.session_state.lmstudio_url)
            if lms_models:
                lms_labels  = [m["label"] for m in lms_models]
                current_lms = st.session_state.lmstudio_model_id
                default_idx = lms_labels.index(current_lms) if current_lms in lms_labels else 0
                selected_lms_label = st.selectbox(
                    f"Local model ({len(lms_models)} loaded)",
                    options=lms_labels,
                    index=default_idx,
                )
                selected_lms = next((m for m in lms_models if m["label"] == selected_lms_label), None)
                if selected_lms:
                    st.session_state.lmstudio_model_id = selected_lms["id"]
                    st.caption(f"🏠 Local · `{selected_lms['id']}`")
                active_model_id = st.session_state.lmstudio_model_id
                active_m        = id_to_model.get(active_model_id)
            else:
                st.warning("No models found — load a model in LM Studio first.")
                active_model_id = ""
                active_m        = None
        else:
            tier = st.radio("Show:", ["🆓 Free Only", "💳 Paid Only", "🔀 All"], horizontal=True)
            visible = (
                free_models if tier == "🆓 Free Only" else
                paid_models if tier == "💳 Paid Only" else
                all_or_models
            )

            search = st.text_input("🔍 Search", placeholder="llama, claude, mistral…")
            if search.strip():
                visible = [m for m in visible if search.lower() in m["label"].lower() or search.lower() in m["id"].lower()]

            visible_labels = [m["label"] for m in visible]
            current_label  = id_to_model.get(st.session_state.active_model_id, {}).get("label", "")
            default_idx    = visible_labels.index(current_label) if current_label in visible_labels else 0

            selected_label = st.selectbox(
                f"Select model ({len(visible)} shown)",
                options=visible_labels,
                index=default_idx,
                key="model_selectbox",
            )
            selected_model = next((m for m in all_or_models if m["label"] == selected_label), None)
            if selected_model:
                st.session_state.active_model_id = selected_model["id"]
                tier_badge = "🆓 Free" if selected_model["free"] else "💳 Paid"
                st.caption(
                    f"{tier_badge} · {selected_model['notes']}\n\n"
                    f"`{selected_model['id']}`"
                )
            active_model_id = st.session_state.active_model_id
            active_m        = id_to_model.get(active_model_id)

        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
        top_k       = st.slider("Top K references", 1, 10, 5)

        # ── Context budget info ────────────────────────────────────────────────
        ctx_budget_chars = get_context_budget(active_m, backend)
        ctx_tokens_shown = ctx_budget_chars // CHARS_PER_TOKEN
        model_ctx        = active_m["ctx"] if active_m and active_m.get("ctx") else DEFAULT_CTX_TOKENS

        # ── Chunking settings ──────────────────────────────────────────────────
        st.divider()
        st.header("✂️ Chunking")

        # Auto-decide default based on model context
        auto_chunk = should_chunk_by_default(model_ctx)
        if model_ctx <= CHUNKING_REQUIRED_CTX:
            chunk_hint = f"⚠️ Small context ({model_ctx:,} tokens) — chunking recommended."
            hint_color = "warning"
        elif model_ctx <= CHUNKING_OPTIONAL_CTX:
            chunk_hint = f"ℹ️ Medium context ({model_ctx:,} tokens) — chunking optional."
            hint_color = "info"
        else:
            chunk_hint = f"✅ Large context ({model_ctx:,} tokens) — chunking not needed."
            hint_color = "success"

        # Show hint
        getattr(st, hint_color)(chunk_hint)

        # Manual override toggle
        enable_chunking = st.toggle(
            "Enable chunking",
            value=auto_chunk,
            help=(
                "**Auto-set** based on model context window:\n\n"
                f"• ≤ {CHUNKING_REQUIRED_CTX:,} tokens → ON\n"
                f"• {CHUNKING_REQUIRED_CTX+1:,}–{CHUNKING_OPTIONAL_CTX:,} → optional\n"
                f"• > {CHUNKING_OPTIONAL_CTX:,} tokens → OFF\n\n"
                "You can always override manually."
            ),
        )

        if enable_chunking:
            chunk_strategy = st.selectbox(
                "Chunking strategy",
                options=CHUNK_STRATEGIES,
                index=0,
                help=(
                    "**Token** — fixed-size character windows. Fast, language-agnostic.\n\n"
                    "**Sentence** — splits at `.`, `!`, `?`. Preserves sentence meaning. "
                    "Good for prose and NLP papers.\n\n"
                    "**Paragraph** — splits at blank lines. Best for structured docs "
                    "like LaTeX sections and `.bib` entries."
                ),
            )

            chunk_size = st.select_slider(
                "Chunk size (tokens)",
                options=[128, 256, 512, 1024, 2048],
                value=min(
                    CHUNK_SIZE_DEFAULT,
                    256 if model_ctx <= 4096 else
                    512 if model_ctx <= 8192 else
                    1024
                ),
                help=(
                    "• **128–256** → fine-grained, fits small context models (≤4K)\n"
                    "• **512** → balanced\n"
                    "• **1024–2048** → broad, for large context models"
                ),
            )
            chunk_overlap = st.select_slider(
                "Chunk overlap (tokens)",
                options=[0, 25, 50, 100, 200],
                value=CHUNK_OVERLAP_DEFAULT,
                help="Tokens repeated at the start of each new chunk to avoid cutting mid-thought.",
            )

            # Suggest based on model ctx
            suggested = (
                256  if model_ctx <= 4096  else
                512  if model_ctx <= 8192  else
                1024 if model_ctx <= 32768 else
                2048
            )
            if chunk_size != suggested:
                st.caption(f"💡 Suggested chunk size for this model: **{suggested} tokens**")
        else:
            # No chunking — use full document text as-is
            chunk_strategy = CHUNK_STRATEGY_TOKEN   # irrelevant but needed for reference
            chunk_size     = 0
            chunk_overlap  = 0
            st.caption("📄 Full documents will be passed to the model (trimmed to context budget if needed).")

        max_chunks_fit = max(1, ctx_budget_chars // (chunk_size * CHARS_PER_TOKEN)) if chunk_size else "N/A"
        with st.expander("⚙️ Context Budget", expanded=False):
            st.caption(
                f"**Model context:** {model_ctx:,} tokens\n\n"
                f"**KB budget:** ~{ctx_tokens_shown:,} tokens ({ctx_budget_chars:,} chars)\n\n"
                + (
                    f"**Strategy:** {chunk_strategy}\n\n"
                    f"**Chunk size:** {chunk_size} tokens (~{chunk_size * CHARS_PER_TOKEN:,} chars)\n\n"
                    f"**Max chunks that fit:** ~{max_chunks_fit}\n\n"
                    if enable_chunking else
                    f"**Mode:** Full documents (no chunking)\n\n"
                ) +
                f"_System + history reserve: ~{SYSTEM_PROMPT_TOKENS + HISTORY_TOKENS} tokens_"
            )

        st.divider()

        # ── Knowledge base ─────────────────────────────────────────────────────
        st.header("📂 Knowledge Base")
        docs     = load_all_documents()
        all_cats = sorted({d["category"] for d in docs})

        selected_cats = st.multiselect("Filter by top-level folder", all_cats, default=all_cats)
        cat_filtered  = [d for d in docs if d["category"] in selected_cats]

        all_subcats = sorted({d["subcategory"] for d in cat_filtered if d["subcategory"]})
        if all_subcats:
            selected_subcats = st.multiselect(
                "Filter by subfolder",
                all_subcats,
                default=all_subcats,
            )
            filtered_docs = [
                d for d in cat_filtered
                if d["subcategory"] in selected_subcats or d["subcategory"] == ""
            ]
        else:
            filtered_docs = cat_filtered

        # Chunk or use full docs based on toggle
        if enable_chunking:
            chunked_docs = chunk_documents(filtered_docs, chunk_size, chunk_overlap, chunk_strategy)
        else:
            # Add parent_label / chunk metadata so downstream code stays consistent
            chunked_docs = [
                {**d, "parent_label": d["label"], "chunk_index": 1, "chunk_total": 1}
                for d in filtered_docs
            ]

        st.metric("Documents loaded", len(filtered_docs))
        st.metric("Total chunks", len(chunked_docs) if enable_chunking else "—")

        with st.expander("📁 Browse documents", expanded=False):
            from collections import defaultdict
            tree = defaultdict(lambda: defaultdict(list))
            for d in filtered_docs:
                tree[d["category"]][d["subcategory"] or "_root"].append(d)

            for cat in sorted(tree.keys()):
                st.markdown(f"**📂 {cat}**")
                for subcat in sorted(tree[cat].keys()):
                    files = tree[cat][subcat]
                    if subcat == "_root":
                        for d in files:
                            if enable_chunking:
                                n = len(chunk_text(d["text"], chunk_strategy, chunk_size, chunk_overlap))
                                st.text(f"    • {d['filename']}  [{n} chunk{'s' if n>1 else ''}]")
                            else:
                                st.text(f"    • {d['filename']}  [full doc]")
                    else:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;📁 *{subcat}*")
                        for d in files:
                            if enable_chunking:
                                n = len(chunk_text(d["text"], chunk_strategy, chunk_size, chunk_overlap))
                                st.text(f"        • {d['filename']}  [{n} chunk{'s' if n>1 else ''}]")
                            else:
                                st.text(f"        • {d['filename']}  [full doc]")

        st.divider()

        # ── Conversation history ───────────────────────────────────────────────
        st.header("💬 Conversations")

        if st.button("➕ New Conversation", use_container_width=True):
            if st.session_state.messages:
                save_conversation(
                    st.session_state.session_id,
                    st.session_state.messages,
                    {
                        "title":   derive_title(st.session_state.messages),
                        "model":   active_model_id,
                        "backend": backend,
                    },
                )
            st.session_state.messages   = []
            st.session_state.session_id = new_session_id()
            st.rerun()

        saved = list_conversations()
        if saved:
            with st.expander(f"📁 Saved ({len(saved)})", expanded=True):
                for s in saved:
                    col_a, col_b = st.columns([5, 1])
                    is_active    = s["session_id"] == st.session_state.session_id
                    label        = f"{'▶ ' if is_active else ''}{s['title']}"
                    col_a.caption(f"**{label}**\n\n_{s['msg_count']} msgs · {s['updated_at'][:16]}_")
                    if col_a.button("Load", key=f"load_{s['session_id']}", use_container_width=True):
                        if st.session_state.messages:
                            save_conversation(
                                st.session_state.session_id,
                                st.session_state.messages,
                                {
                                    "title":   derive_title(st.session_state.messages),
                                    "model":   active_model_id,
                                    "backend": backend,
                                },
                            )
                        conv = load_conversation(s["session_id"])
                        if conv:
                            st.session_state.messages   = conv["messages"]
                            st.session_state.session_id = s["session_id"]
                            saved_backend = conv.get("metadata", {}).get("backend", BACKEND_OPENROUTER)
                            saved_model   = conv.get("metadata", {}).get("model", "")
                            st.session_state.backend = saved_backend
                            if saved_backend == BACKEND_LMSTUDIO:
                                st.session_state.lmstudio_model_id = saved_model
                            else:
                                st.session_state.active_model_id = saved_model
                        st.rerun()
                    if col_b.button("🗑", key=f"del_{s['session_id']}"):
                        delete_conversation(s["session_id"])
                        if s["session_id"] == st.session_state.session_id:
                            st.session_state.messages   = []
                            st.session_state.session_id = new_session_id()
                        st.rerun()
        else:
            st.caption("No saved conversations yet.")

    # ── Chat area ──────────────────────────────────────────────────────────────
    docs_index = {d["label"]: d for d in filtered_docs}

    # Active model banner
    if active_m:
        backend_icon = "🏠" if backend == BACKEND_LMSTUDIO else "🆓"
        st.caption(f"{backend_icon} **{active_m['label']}** · `{active_m['id']}` · {active_m['notes']}")
    elif backend == BACKEND_LMSTUDIO:
        st.caption("🏠 LM Studio — no model loaded")

    # Render existing messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                render_message_with_citations(msg["content"], docs_index)

                cited_refs     = msg.get("references_cited", msg.get("references", []))
                retrieved_refs = msg.get("references_retrieved", [])

                if retrieved_refs:
                    with st.expander(f"🔍 {len(retrieved_refs)} reference(s) used as context", expanded=False):
                        for lbl in retrieved_refs:
                            doc         = docs_index.get(lbl)
                            cited_badge = "✅ cited" if lbl in cited_refs else "📄 retrieved"
                            st.markdown(f"**{cited_badge} · {lbl}**")
                            if doc:
                                st.code(doc["text"][:CHUNK_PREVIEW_LEN] + "…", language=None)

                if cited_refs:
                    st.caption(f"📎 LLM cited: {', '.join(cited_refs)}")

                if msg.get("model_id"):
                    m_info  = id_to_model.get(msg["model_id"])
                    m_label = m_info["label"] if m_info else msg["model_id"]
                    backend_tag = f" · 🏠 {msg.get('backend', '')}" if msg.get("backend") == BACKEND_LMSTUDIO else ""
                    st.caption(f"🤖 `{m_label}`{backend_tag} · ⏱ {msg.get('elapsed_s', '?')}s")
            else:
                st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Ask anything…"):
        # Guard: API key required for OpenRouter
        if backend == BACKEND_OPENROUTER and not effective_key:
            st.error("⚠️ Please enter your OpenRouter API key in the sidebar.")
            st.stop()

        # Guard: model must be selected
        if not active_model_id:
            st.error("⚠️ No model selected. Load a model in LM Studio first." if backend == BACKEND_LMSTUDIO else "⚠️ No model selected.")
            st.stop()

        if not filtered_docs:
            st.warning("⚠️ No documents loaded.")
            st.stop()

        # Append + show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Retrieve from CHUNKS (not raw docs)
        retrieved     = retrieve_top_docs(prompt, chunked_docs, top_k=top_k)
        ctx_budget    = get_context_budget(active_m, backend)
        context       = build_context(retrieved, max_chars=ctx_budget)

        # Warn if trimmed
        total_text = sum(len(d["text"]) for d in retrieved)
        if total_text > ctx_budget * 1.5:
            st.toast(
                f"⚠️ Retrieved content ({total_text:,} chars) trimmed to fit "
                f"model context (~{ctx_budget:,} chars). "
                f"Try reducing chunk size or Top K.",
                icon="⚠️",
            )

        # Build API messages
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)
        api_messages  = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.messages[-10:]:
            api_messages.append({"role": m["role"], "content": m["content"]})

        # Call LLM (unified)
        model_label = active_m["label"] if active_m else active_model_id
        with st.chat_message("assistant"):
            with st.spinner(f"Thinking with {model_label} via {backend}…"):
                t0 = time.time()
                try:
                    reply, cited = call_llm(
                        api_messages,
                        model       = active_model_id,
                        backend     = backend,
                        api_key     = effective_key,
                        lmstudio_url= st.session_state.lmstudio_url,
                        temperature = temperature,
                    )
                    elapsed = round(time.time() - t0, 1)
                except requests.ConnectionError:
                    st.error("❌ Cannot connect to LM Studio. Is the local server running?")
                    st.stop()
                except requests.HTTPError as e:
                    st.error(f"API error: {e}")
                    st.stop()
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
                    st.stop()

            render_message_with_citations(reply, docs_index)

            # Display retrieved chunks
            retrieved_labels = [d["label"] for d in retrieved]
            with st.expander(f"🔍 Retrieved {len(retrieved)} chunk(s) from knowledge base", expanded=False):
                for d in retrieved:
                    cited_badge  = "✅ cited" if d["label"] in cited else "📄 retrieved"
                    chunk_info   = f"chunk {d['chunk_index']}/{d['chunk_total']}" if d.get("chunk_total", 1) > 1 else "full doc"
                    parent_label = d.get("parent_label", d["label"])
                    st.markdown(
                        f"**{cited_badge}** · `{parent_label}` "
                        f"_{chunk_info}_ · _(category: {d['category']})_"
                    )
                    st.code(d["text"][:CHUNK_PREVIEW_LEN] + "…", language=None)

            if cited:
                st.caption(f"📎 LLM cited: {', '.join(cited)}")
            else:
                st.caption("⚠️ LLM did not emit explicit citations — see retrieved references above.")

            backend_icon = "🏠" if backend == BACKEND_LMSTUDIO else "🤖"
            st.caption(f"{backend_icon} `{model_label}` · ⏱ {elapsed}s")

        # Save assistant message
        assistant_msg = {
            "role":                  "assistant",
            "content":               reply,
            "references_cited":      cited,
            "references_retrieved":  retrieved_labels,
            "model_id":              active_model_id,
            "backend":               backend,
            "elapsed_s":             elapsed,
            "timestamp":             datetime.now().isoformat(),
        }
        assistant_msg["references"] = list(dict.fromkeys(cited + retrieved_labels))
        st.session_state.messages.append(assistant_msg)

        save_conversation(
            st.session_state.session_id,
            st.session_state.messages,
            {
                "title":   derive_title(st.session_state.messages),
                "model":   active_model_id,
                "backend": backend,
            },
        )


if __name__ == "__main__":
    main()