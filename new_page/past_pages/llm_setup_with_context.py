"""
ESG Structured Extraction — OpenRouter + LM Studio backends,
with selectable prompt templates from /prompt/*.md
Full-document context + targeted page sentence extraction.
"""
import os
import re
import time
import json
import socket
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urlparse

import requests
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
OPENROUTER_API_URL    = os.getenv("OPENROUTER_API_URL",    "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODELS_URL = os.getenv("OPENROUTER_MODELS_URL", "https://openrouter.ai/api/v1/models")
LMSTUDIO_DEFAULT_URL  = "http://localhost:1234/v1"

DEFAULT_MODEL        = "meta-llama/llama-3.1-8b-instruct:free"
API_KEY_ENV          = "OPENROUTER_API_KEY"
CHARS_PER_TOKEN      = 4
DEFAULT_CTX_TOKENS   = 4096

PROMPT_DIR     = Path(__file__).resolve().parents[1] / "prompt"
OCR_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"
RESULTS_DIR    = Path(__file__).resolve().parents[1] / "results"

BACKEND_OPENROUTER = "OpenRouter"
BACKEND_LMSTUDIO   = "LM Studio (Local)"


# ══════════════════════════════════════════════════════════════════════════════
# TOKEN / COST HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def estimate_tokens(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 characters."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def estimate_cost(prompt_tokens: int, completion_tokens: int, model_info: dict) -> Optional[float]:
    """
    Returns estimated USD cost or None if model is free / pricing unknown.
    model_info keys: prompt_price_per_token, completion_price_per_token (per-token USD).
    """
    p = model_info.get("prompt_price_per_token")
    c = model_info.get("completion_price_per_token")
    if p is None or c is None:
        return None
    return round(prompt_tokens * p + completion_tokens * c, 6)


def format_cost(usd: Optional[float]) -> str:
    if usd is None:
        return "free / unknown"
    if usd == 0.0:
        return "🆓 free"
    if usd < 0.001:
        return f"~${usd * 1000:.4f} m¢"
    return f"~${usd:.4f}"


def ctx_utilisation_color(used: int, limit: int) -> str:
    if limit == 0:
        return "gray"
    ratio = used / limit
    if ratio > 0.9:  return "red"
    if ratio > 0.7:  return "orange"
    return "green"


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def list_prompt_files() -> list[Path]:
    if not PROMPT_DIR.exists():
        return []
    return sorted(PROMPT_DIR.glob("*.md"))


def load_prompt_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def apply_prompt(template: str, input_text: str) -> str:
    if "{{INPUT_TEXT}}" in template:
        return template.replace("{{INPUT_TEXT}}", input_text)
    return template.strip() + f"\n\n---\n\nText to analyze:\n{input_text}"


# ══════════════════════════════════════════════════════════════════════════════
# HTTP / RETRY
# ══════════════════════════════════════════════════════════════════════════════

def _requests_session(retries: int = 3, backoff: float = 0.6) -> requests.Session:
    s = requests.Session()
    r = Retry(
        total=retries, backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["POST", "GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.mount("http://",  HTTPAdapter(max_retries=r))
    return s


# ══════════════════════════════════════════════════════════════════════════════
# MODEL FETCHERS
# ══════════════════════════════════════════════════════════════════════════════

def _fallback_openrouter_models() -> list[dict]:
    """
    Each entry includes prompt_price_per_token and completion_price_per_token
    in USD per token (divide $/1M by 1_000_000).
    """
    return [
        {"id": "meta-llama/llama-3.1-8b-instruct:free",  "label": "Llama 3.1 8B",     "free": True,  "notes": "free · 131k ctx",   "ctx": 131072,   "prompt_price_per_token": 0.0,           "completion_price_per_token": 0.0},
        {"id": "meta-llama/llama-3.3-70b-instruct:free",  "label": "Llama 3.3 70B",    "free": True,  "notes": "free · 131k ctx",   "ctx": 131072,   "prompt_price_per_token": 0.0,           "completion_price_per_token": 0.0},
        {"id": "mistralai/mistral-7b-instruct:free",      "label": "Mistral 7B",        "free": True,  "notes": "free · 32k ctx",    "ctx": 32768,    "prompt_price_per_token": 0.0,           "completion_price_per_token": 0.0},
        {"id": "google/gemma-3-27b-it:free",              "label": "Gemma 3 27B",       "free": True,  "notes": "free · 131k ctx",   "ctx": 131072,   "prompt_price_per_token": 0.0,           "completion_price_per_token": 0.0},
        {"id": "deepseek/deepseek-r1:free",               "label": "DeepSeek R1",       "free": True,  "notes": "free · 65k ctx",    "ctx": 65536,    "prompt_price_per_token": 0.0,           "completion_price_per_token": 0.0},
        {"id": "openai/gpt-4o-mini",                      "label": "GPT-4o Mini",       "free": False, "notes": "$0.150/1M · 128k",  "ctx": 128000,   "prompt_price_per_token": 0.15/1e6,     "completion_price_per_token": 0.60/1e6},
        {"id": "openai/gpt-4o",                           "label": "GPT-4o",            "free": False, "notes": "$2.500/1M · 128k",  "ctx": 128000,   "prompt_price_per_token": 2.50/1e6,     "completion_price_per_token": 10.0/1e6},
        {"id": "anthropic/claude-3.5-sonnet",             "label": "Claude 3.5 Sonnet", "free": False, "notes": "$3.000/1M · 200k",  "ctx": 200000,   "prompt_price_per_token": 3.00/1e6,     "completion_price_per_token": 15.0/1e6},
        {"id": "anthropic/claude-3.5-haiku",              "label": "Claude 3.5 Haiku",  "free": False, "notes": "$0.800/1M · 200k",  "ctx": 200000,   "prompt_price_per_token": 0.80/1e6,     "completion_price_per_token": 4.00/1e6},
        {"id": "google/gemini-flash-1.5",                 "label": "Gemini 1.5 Flash",  "free": False, "notes": "$0.075/1M · 1M ctx","ctx": 1000000,  "prompt_price_per_token": 0.075/1e6,    "completion_price_per_token": 0.30/1e6},
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_openrouter_models(api_key: Optional[str] = None) -> list[dict]:
    if not api_key:
        return _fallback_openrouter_models()
    try:
        resp = requests.get(
            OPENROUTER_MODELS_URL,
            headers={"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://esg-project.app"},
            timeout=10,
        )
        resp.raise_for_status()
        raw    = resp.json().get("data", [])
        models = []
        for m in raw:
            mid     = m.get("id", "")
            name    = m.get("name", mid)
            ctx     = m.get("context_length", 0)
            pricing = m.get("pricing", {})
            try:
                p_raw   = float(pricing.get("prompt",     1))
                c_raw   = float(pricing.get("completion", 1))
                is_free = p_raw == 0.0 and c_raw == 0.0
                # OpenRouter pricing is already per-token (not per-1M)
                p_per_tok = p_raw
                c_per_tok = c_raw
            except (ValueError, TypeError):
                is_free   = str(pricing.get("prompt", "1")) == "0"
                p_per_tok = None
                c_per_tok = None

            cost_str = "free" if is_free else f"${(p_per_tok or 0) * 1_000_000:.3f}/1M"
            ctx_str  = f"{ctx:,} ctx" if ctx else ""
            notes    = " · ".join(filter(None, [cost_str, ctx_str]))
            models.append({
                "id": mid, "label": name, "free": is_free,
                "notes": notes, "ctx": ctx,
                "prompt_price_per_token":     p_per_tok,
                "completion_price_per_token": c_per_tok,
            })

        models.sort(key=lambda x: (not x["free"], x["label"].lower()))
        return models if models else _fallback_openrouter_models()
    except Exception:
        return _fallback_openrouter_models()


def fetch_lmstudio_models(base_url: str) -> list[dict]:
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/models", timeout=5)
        resp.raise_for_status()
        raw = resp.json().get("data", [])
        return [
            {
                "id":    m.get("id", ""),
                "label": m.get("id", ""),
                "free":  True,
                "notes": "local · LM Studio",
                "ctx":   m.get("context_length", DEFAULT_CTX_TOKENS),
                "prompt_price_per_token":     0.0,
                "completion_price_per_token": 0.0,
            }
            for m in raw if m.get("id")
        ]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════════
# JSON PARSING
# ══════════════════════════════════════════════════════════════════════════════

def parse_json_from_model(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"```json\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
        if not m:
            m = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                import ast
                try:    return ast.literal_eval(m.group(1))
                except Exception: pass
    raise ValueError("Could not parse JSON from model output.")


# ══════════════════════════════════════════════════════════════════════════════
# LLM CALLERS
# ══════════════════════════════════════════════════════════════════════════════

def _call_openrouter(prompt: str, model: str, api_key: str,
                     temperature: float = 0.0, max_tokens: int = 1500, retries: int = 3) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
            {"role": "user",   "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens":  max_tokens,
    }
    s       = _requests_session(retries=retries)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://esg-project.app",
        "X-Title":       "ESG Extractor",
    }
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp    = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            choices = resp.json().get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return resp.text
        except Exception as e:
            last_exc = e
            time.sleep(min(10, 2 ** attempt))
    raise RuntimeError(f"OpenRouter failed after {retries} attempts: {last_exc}")


def _call_lmstudio(prompt: str, model: str, base_url: str,
                   temperature: float = 0.0, max_tokens: int = 1500) -> str:
    url     = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
            {"role": "user",   "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens":  max_tokens,
        "stream":      False,
    }
    if model:
        payload["model"] = model
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_llm(prompt: str, model: str, backend: str, api_key: str = "",
             lmstudio_url: str = LMSTUDIO_DEFAULT_URL,
             temperature: float = 0.0, max_tokens: int = 1500, retries: int = 3) -> str:
    if backend == BACKEND_LMSTUDIO:
        return _call_lmstudio(prompt, model, lmstudio_url, temperature, max_tokens)
    return _call_openrouter(prompt, model, api_key, temperature, max_tokens, retries)


# ══════════════════════════════════════════════════════════════════════════════
# IMMEDIATE SAVE
# ══════════════════════════════════════════════════════════════════════════════

def append_record(record: dict, fname: Path) -> None:
    """Atomically append one record to a JSON array file."""
    existing: list = []
    if fname.exists():
        try:
            loaded   = json.loads(fname.read_text(encoding="utf-8"))
            existing = loaded if isinstance(loaded, list) else [loaded]
        except Exception:
            existing = []
    existing.append(record)
    tmp = fname.with_suffix(".tmp")
    tmp.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(fname)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "openrouter_key":    os.getenv(API_KEY_ENV, ""),
    "backend":           BACKEND_OPENROUTER,
    "lmstudio_url":      LMSTUDIO_DEFAULT_URL,
    "active_model_id":   DEFAULT_MODEL,
    "lmstudio_model_id": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="ESG LLM Extractor", page_icon="🌿", layout="wide")
st.title("🌿 ESG Structured Extraction")
st.caption(
    "Select a document as full context, target specific pages for sentence-level "
    "extraction, and track live token usage & estimated cost per call."
)

# ── Load models ───────────────────────────────────────────────────────────────
with st.spinner("🔄 Fetching models from OpenRouter…"):
    all_or_models = fetch_openrouter_models(st.session_state.openrouter_key or None)

free_models = [m for m in all_or_models if     m["free"]]
paid_models = [m for m in all_or_models if not m["free"]]
id_to_model = {m["id"]: m for m in all_or_models}


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Backend ───────────────────────────────────────────────────────────────
    st.header("🖥️ Backend")
    backend = st.radio(
        "LLM Backend",
        [BACKEND_OPENROUTER, BACKEND_LMSTUDIO],
        index=0 if st.session_state.backend == BACKEND_OPENROUTER else 1,
        horizontal=True,
        key="backend_radio",
    )
    st.session_state.backend = backend

    if backend == BACKEND_OPENROUTER:
        st.subheader("🔑 API Key")
        api_key_input = st.text_input(
            "OpenRouter API Key", type="password",
            value=st.session_state.openrouter_key,
            help="https://openrouter.ai/keys",
        )
        if api_key_input.strip():
            st.session_state.openrouter_key = api_key_input.strip()
        if st.session_state.openrouter_key:
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
        if st.button("🔌 Connectivity Check", use_container_width=True):
            try:
                host = urlparse(OPENROUTER_API_URL).hostname
                addr = socket.getaddrinfo(host, 443)
                st.success(f"DNS OK: {', '.join({ai[4][0] for ai in addr})}")
            except Exception as e:
                st.error(f"Connectivity issue: {e}")
    else:
        st.subheader("🏠 LM Studio")
        lmstudio_url = st.text_input(
            "Server URL", value=st.session_state.lmstudio_url,
            help="Default: http://localhost:1234/v1",
        )
        st.session_state.lmstudio_url = lmstudio_url
        lms_models = fetch_lmstudio_models(lmstudio_url)
        if lms_models:
            st.success(f"✅ Connected · {len(lms_models)} model(s)")
            id_to_model.update({m["id"]: m for m in lms_models})
        else:
            st.error("❌ Cannot reach LM Studio")

    st.divider()

    # ── Model Selector ────────────────────────────────────────────────────────
    st.header("🤖 Model")

    if backend == BACKEND_LMSTUDIO:
        lms_models = fetch_lmstudio_models(st.session_state.lmstudio_url)
        if lms_models:
            lms_labels  = [m["label"] for m in lms_models]
            curr_lms    = st.session_state.lmstudio_model_id
            def_idx     = lms_labels.index(curr_lms) if curr_lms in lms_labels else 0
            sel_lms_lbl = st.selectbox(f"Local model ({len(lms_models)} loaded)", lms_labels, index=def_idx)
            sel_lms     = next((m for m in lms_models if m["label"] == sel_lms_lbl), None)
            if sel_lms:
                st.session_state.lmstudio_model_id = sel_lms["id"]
            selected_models = [st.session_state.lmstudio_model_id] if st.session_state.lmstudio_model_id else []
            active_m        = id_to_model.get(st.session_state.lmstudio_model_id)
        else:
            st.warning("No models found — load one in LM Studio first.")
            selected_models = []
            active_m        = None
    else:
        tier = st.radio(
            "Show:", ["🆓 Free Only", "💳 Paid Only", "🔀 All"],
            horizontal=True, key="model_tier",
        )
        visible = (
            free_models if "Free" in tier else
            paid_models if "Paid" in tier else
            all_or_models
        )
        search = st.text_input("🔍 Search model", placeholder="llama, claude, mistral…")
        if search.strip():
            visible = [
                m for m in visible
                if search.lower() in m["label"].lower()
                or search.lower() in m["id"].lower()
            ]
        visible_labels = [m["label"] for m in visible]
        curr_label     = id_to_model.get(st.session_state.active_model_id, {}).get("label", "")
        def_idx        = visible_labels.index(curr_label) if curr_label in visible_labels else 0

        selected_labels = st.multiselect(
            f"Select model(s) ({len(visible)} shown)",
            options=visible_labels,
            default=[visible_labels[def_idx]] if visible_labels else [],
        )
        selected_models = [m["id"] for m in all_or_models if m["label"] in selected_labels]
        if selected_models:
            st.session_state.active_model_id = selected_models[0]
        active_m = id_to_model.get(st.session_state.active_model_id)

        if active_m:
            badge = "🆓 Free" if active_m["free"] else "💳 Paid"
            st.caption(f"{badge} · {active_m['notes']}\n\n`{active_m['id']}`")

    st.divider()

    # ── Generation Settings ───────────────────────────────────────────────────
    st.header("⚙️ Generation")
    temperature_input = st.slider("Temperature",  0.0, 1.0, 0.0, 0.01)
    max_tokens_input  = st.number_input("Max tokens", value=1500, min_value=64, step=100)
    retries_input     = st.number_input("Retries",    value=3,    min_value=0,  step=1)

    st.divider()

    # ── Prompt Selector ───────────────────────────────────────────────────────
    st.header("📝 Prompt Template")
    prompt_files         = list_prompt_files()
    selected_prompt_path = None
    prompt_override      = ""
    if not prompt_files:
        st.warning(f"No .md files in `{PROMPT_DIR}`")
    else:
        prompt_names  = [p.name for p in prompt_files]
        selected_name = st.selectbox(
            "Select prompt", prompt_names,
            index=prompt_names.index("data.md") if "data.md" in prompt_names else 0,
        )
        selected_prompt_path = PROMPT_DIR / selected_name
        with st.expander("👁️ Preview prompt", expanded=False):
            raw_prompt = load_prompt_file(selected_prompt_path)
            st.markdown(raw_prompt[:1500] + ("…" if len(raw_prompt) > 1500 else ""))
        with st.expander("✏️ Override prompt (optional)", expanded=False):
            st.caption("Use `{{INPUT_TEXT}}` as placeholder. Leave blank to use file.")
            prompt_override = st.text_area(
                "Custom prompt", value="", height=200,
                placeholder="Leave blank to use the selected prompt file…",
            )

    st.divider()

    # ── Output ────────────────────────────────────────────────────────────────
    st.header("💾 Output")
    save_results = st.checkbox("Save each result immediately", value=True)
    use_mock     = st.checkbox("Mock responses (offline/testing)", value=False)


# ══════════════════════════════════════════════════════════════════════════════
# INPUT SOURCE — Document + Page Selector
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📥 Input Source")
input_mode = st.radio(
    "Input source", ["Manual text", "OCR document"],
    horizontal=True, key="input_mode_radio",
)

texts_to_process:    list[dict] = []   # pages targeted for sentence extraction
doc_full_text:       str        = ""   # entire document as LLM context
selected_page_texts: list[dict] = []
all_page_files:      list       = []

if input_mode == "Manual text":
    manual_text = st.text_area("Enter text to analyze", height=200, key="manual_text_area")
    if manual_text.strip():
        t = manual_text.strip()
        texts_to_process    = [{"label": "manual_input", "text": t}]
        selected_page_texts = texts_to_process
        doc_full_text       = t

else:
    doc_folders = sorted(
        [d for d in OCR_OUTPUT_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    ) if OCR_OUTPUT_DIR.exists() else []

    if not doc_folders:
        st.warning(f"No document folders found in `{OCR_OUTPUT_DIR}`")
    else:
        doc_names    = [d.name for d in doc_folders]
        selected_doc = st.selectbox("📁 Select document", doc_names, key="doc_select")
        pages_dir    = OCR_OUTPUT_DIR / selected_doc / "pages"
        all_page_files = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []

        if not all_page_files:
            st.warning(f"No `.md` page files in `{pages_dir}`")
        else:
            page_names = [p.name for p in all_page_files]

            # ── Load entire document as context ───────────────────────────────
            doc_full_text = "\n\n".join(
                pf.read_text(encoding="utf-8").strip()
                for pf in all_page_files
                if pf.read_text(encoding="utf-8").strip()
            )
            doc_token_est = estimate_tokens(doc_full_text)

            # Context window info
            ctx_limit  = (active_m or {}).get("ctx", DEFAULT_CTX_TOKENS)
            ctx_color  = ctx_utilisation_color(doc_token_est, ctx_limit)
            ctx_pct    = f"{doc_token_est / ctx_limit * 100:.1f}%" if ctx_limit else "?"

            col_doc1, col_doc2, col_doc3 = st.columns(3)
            col_doc1.metric("📄 Total pages",   len(all_page_files))
            col_doc2.metric("📝 Est. tokens",   f"{doc_token_est:,}")
            col_doc3.metric("🪟 Context used",  ctx_pct,
                            help=f"Model context window: {ctx_limit:,} tokens" if ctx_limit else "Unknown ctx")

            if doc_token_est > ctx_limit * 0.9 and ctx_limit > 0:
                st.warning(
                    f"⚠️ Document (~{doc_token_est:,} tok) is near or over the "
                    f"model's context window ({ctx_limit:,} tok). "
                    "Consider selecting fewer pages or using a larger-context model."
                )

            # ── Target page selector ──────────────────────────────────────────
            st.markdown("#### 🎯 Target Pages for Sentence Extraction")
            st.caption(
                "The **full document** is always sent as background context. "
                "Select which pages the LLM should focus extraction on."
            )

            selection_mode = st.radio(
                "Page selection",
                ["All pages", "Select specific pages"],
                horizontal=True,
                key="page_selection_radio",
            )

            if selection_mode == "All pages":
                chosen_pages = all_page_files
            else:
                chosen_names = st.multiselect(
                    "Select page(s) to target",
                    page_names,
                    default=[page_names[0]],
                    key="page_multiselect",
                )
                chosen_pages = [pages_dir / n for n in chosen_names]

            if chosen_pages:
                selected_page_texts = [
                    {
                        "label": f"{selected_doc}/{pf.name}",
                        "text":  pf.read_text(encoding="utf-8").strip(),
                    }
                    for pf in chosen_pages
                    if pf.read_text(encoding="utf-8").strip()
                ]
                texts_to_process = selected_page_texts

                # ── Page preview ──────────────────────────────────────────────
                with st.expander(
                    f"📄 Preview targeted pages ({len(chosen_pages)})", expanded=False
                ):
                    for pf in chosen_pages[:5]:
                        st.markdown(f"**{pf.name}**")
                        content = pf.read_text(encoding="utf-8")
                        st.text(content[:400] + ("…" if len(content) > 400 else ""))
                    if len(chosen_pages) > 5:
                        st.caption(f"… and {len(chosen_pages) - 5} more page(s)")


# ══════════════════════════════════════════════════════════════════════════════
# CONTEXT BUDGET HELPERS
# ══════════════════════════════════════════════════════════════════════════════

# Reserve tokens for the prompt template + completion
PROMPT_OVERHEAD_TOKENS = 500   # template text, headers, separators
COMPLETION_RESERVE     = 1500  # keep room for the model to respond


def truncate_to_tokens(text: str, max_tokens: int) -> tuple[str, bool]:
    """Truncate text to fit within max_tokens. Returns (truncated_text, was_truncated)."""
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars] + "\n\n[... truncated to fit context window ...]", True


def build_context_prompt(
    full_doc: str,
    page_texts: list[dict],
    template: str,
    ctx_limit: int = DEFAULT_CTX_TOKENS,
    max_completion: int = COMPLETION_RESERVE,
) -> tuple[str, dict]:
    """
    Combines the full document as background context with the targeted pages.
    Intelligently truncates to fit within the model's context window.

    Returns:
        (final_prompt, budget_info dict)
    """
    # Budget: total ctx - completion reserve - overhead
    usable_tokens   = max(512, ctx_limit - max_completion - PROMPT_OVERHEAD_TOKENS)

    # Targeted pages get PRIORITY — allocate up to 60% of budget to them
    page_budget     = int(usable_tokens * 0.60)
    context_budget  = int(usable_tokens * 0.40)

    # Build targeted pages section first (priority content)
    page_section_raw = "\n\n---\n\n".join(
        f"[PAGE: {p['label']}]\n{p['text']}" for p in page_texts
    )
    page_section, page_truncated = truncate_to_tokens(page_section_raw, page_budget)

    # Remaining budget for full-doc context
    full_doc_part, ctx_truncated = truncate_to_tokens(full_doc, context_budget)

    combined = (
        "### FULL DOCUMENT CONTEXT\n"
        "(Background reference only — do NOT extract from here)\n\n"
        f"{full_doc_part}\n\n"
        "### TARGET PAGES\n"
        "(Extract ALL ESG-relevant sentences from these pages)\n\n"
        f"{page_section}"
    )

    final_prompt = apply_prompt(template, combined)

    budget_info = {
        "ctx_limit":          ctx_limit,
        "usable_tokens":      usable_tokens,
        "page_budget":        page_budget,
        "context_budget":     context_budget,
        "page_tok_est":       estimate_tokens(page_section),
        "ctx_tok_est":        estimate_tokens(full_doc_part),
        "prompt_tok_est":     estimate_tokens(final_prompt),
        "page_truncated":     page_truncated,
        "context_truncated":  ctx_truncated,
    }
    return final_prompt, budget_info


# ══════════════════════════════════════════════════════════════════════════════
# PRE-RUN COST / TOKEN ESTIMATE
# ══════════════════════════════════════════════════════════════════════════════
if texts_to_process and selected_models and doc_full_text:
    st.markdown("---")
    st.subheader("💰 Pre-Run Estimate")
    st.caption("Based on ~4 chars/token. Actual billing may differ.")

    if selected_prompt_path:
        base_prompt_preview = prompt_override.strip() or load_prompt_file(selected_prompt_path)
    else:
        base_prompt_preview = "You are an ESG expert. Analyze:\n{{INPUT_TEXT}}\nOutput JSON list."

    est_rows = []
    for model_id in selected_models:
        m_info    = id_to_model.get(model_id, {})
        ctx_limit = m_info.get("ctx", DEFAULT_CTX_TOKENS) or DEFAULT_CTX_TOKENS

        sample_prompt, budget = build_context_prompt(
            doc_full_text,
            selected_page_texts,
            base_prompt_preview,
            ctx_limit     = ctx_limit,
            max_completion= int(max_tokens_input),
        )
        prompt_tok_est     = budget["prompt_tok_est"]
        completion_tok_est = int(max_tokens_input)
        cost               = estimate_cost(prompt_tok_est, completion_tok_est, m_info)

        warnings = []
        if budget["context_truncated"]: warnings.append("⚠️ context truncated")
        if budget["page_truncated"]:    warnings.append("⚠️ pages truncated")
        if prompt_tok_est > ctx_limit * 0.9: warnings.append("🔴 near limit")

        est_rows.append({
            "Model":            m_info.get("label", model_id),
            "Ctx window":       f"{ctx_limit:,}",
            "Prompt tokens":    f"{prompt_tok_est:,}",
            "Ctx used %":       f"{prompt_tok_est / ctx_limit * 100:.1f}%" if ctx_limit else "?",
            "Max completion":   f"{completion_tok_est:,}",
            "Est. cost/call":   format_cost(cost),
            "Warnings":         " ".join(warnings) if warnings else "✅ ok",
        })

    st.dataframe(est_rows, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pages targeted",  len(texts_to_process))
    c2.metric("Models selected", len(selected_models))
    c3.metric("Total API calls", len(selected_models))
    c4.metric("Doc tokens (raw)", f"{estimate_tokens(doc_full_text):,}")

    with st.expander("📋 Run plan + budget breakdown", expanded=False):
        for m in selected_models:
            m_info    = id_to_model.get(m, {})
            ctx_limit = m_info.get("ctx", DEFAULT_CTX_TOKENS) or DEFAULT_CTX_TOKENS
            _, budget = build_context_prompt(
                doc_full_text, selected_page_texts, base_prompt_preview,
                ctx_limit=ctx_limit, max_completion=int(max_tokens_input),
            )
            st.markdown(f"**{m_info.get('label', m)}** · `{m}`")
            st.json(budget)


# ══════════════════════════════════════════════════════════════════════════════
# EXECUTE
# ══════════════════════════════════════════════════════════════════════════════
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if st.button("🚀 Generate Structured ESG JSON", type="primary", use_container_width=True):
    if not texts_to_process:
        st.warning("⚠️ No text to process. Enter text or select at least one page.")
        st.stop()
    if not selected_models:
        st.warning("⚠️ No model selected.")
        st.stop()
    if backend == BACKEND_OPENROUTER and not use_mock and not st.session_state.openrouter_key:
        st.error("❌ OpenRouter API key not provided.")
        st.stop()

    if selected_prompt_path:
        base_prompt  = prompt_override.strip() or load_prompt_file(selected_prompt_path)
        prompt_label = "custom override" if prompt_override.strip() else selected_prompt_path.name
    else:
        base_prompt  = "You are an ESG expert. Analyze:\n{{INPUT_TEXT}}\nOutput a JSON list of ESG records."
        prompt_label = "default fallback"

    st.info(f"📝 Prompt: **{prompt_label}**")

    fname            = RESULTS_DIR / "esg_records.json"
    total            = len(selected_models)
    step             = 0
    saved_count      = 0
    failed_count     = 0
    all_run_records: list = []
    progress         = st.progress(0)
    status_text      = st.empty()

    for model in selected_models:
        step       += 1
        m_info      = id_to_model.get(model, {})
        model_label = m_info.get("label", model)
        ctx_limit   = m_info.get("ctx", DEFAULT_CTX_TOKENS) or DEFAULT_CTX_TOKENS

        # Build prompt WITH per-model context budget enforcement
        final_prompt, budget = build_context_prompt(
            doc_full_text,
            selected_page_texts,
            base_prompt,
            ctx_limit      = ctx_limit,
            max_completion = int(max_tokens_input),
        )
        prompt_tok_act = budget["prompt_tok_est"]

        # Warn if truncation happened
        if budget["context_truncated"] or budget["page_truncated"]:
            st.warning(
                f"⚠️ **{model_label}**: content was truncated to fit "
                f"{ctx_limit:,} token context window. "
                f"(context_truncated={budget['context_truncated']}, "
                f"page_truncated={budget['page_truncated']})"
            )

        status_text.info(
            f"⏳ [{step}/{total}] **{model_label}** · "
            f"prompt ~{prompt_tok_act:,} / {ctx_limit:,} tokens · "
            f"{len(selected_page_texts)} page(s) targeted"
        )

        if use_mock:
            parsed     = [
                {
                    "text":      p["text"][:120],
                    "esg":       "Environmental",
                    "sentiment": "Positive",
                    "labels":    ["mock"],
                    "note":      "mock response",
                    "source":    p["label"],
                }
                for p in selected_page_texts
            ]
            raw_output = ""
            ok, err    = True, None
        else:
            try:
                raw_output = call_llm(
                    prompt       = final_prompt,
                    model        = model,
                    backend      = backend,
                    api_key      = st.session_state.openrouter_key,
                    lmstudio_url = st.session_state.lmstudio_url,
                    temperature  = float(temperature_input),
                    max_tokens   = int(max_tokens_input),
                    retries      = int(retries_input),
                )
                parsed = parse_json_from_model(raw_output)
                if not isinstance(parsed, list):
                    parsed = [parsed] if isinstance(parsed, dict) else []
                ok, err = True, None
            except Exception as e:
                parsed, raw_output = [], ""
                ok, err = False, str(e)

        completion_tok_act = estimate_tokens(raw_output) if raw_output else int(max_tokens_input)
        actual_cost        = estimate_cost(prompt_tok_act, completion_tok_act, m_info)

        record = {
            "timestamp":             datetime.utcnow().strftime("%Y-%m-%dT%H:%M%SZ"),
            "model":                 model,
            "backend":               backend,
            "prompt":                prompt_label,
            "context_pages":         len(all_page_files) if input_mode != "Manual text" else 1,
            "targeted_pages":        [p["label"] for p in selected_page_texts],
            "prompt_tokens_est":     prompt_tok_act,
            "completion_tokens_est": completion_tok_act,
            "estimated_cost_usd":    actual_cost,
            "context_truncated":     budget["context_truncated"],
            "pages_truncated":       budget["page_truncated"],
            "ok":                    ok,
            "records":               parsed,
            **({"error": err} if err else {}),
        }
        all_run_records.append(record)

        if ok:
            cost_str = format_cost(actual_cost)
            with st.expander(
                f"✅ **{model_label}** — {len(parsed)} record(s) · "
                f"{prompt_tok_act:,} / {ctx_limit:,} tok · {cost_str}",
                expanded=True,
            ):
                mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                mc1.metric("Prompt tokens",     f"{prompt_tok_act:,}")
                mc2.metric("Ctx window",        f"{ctx_limit:,}")
                mc3.metric("Ctx used",          f"{prompt_tok_act / ctx_limit * 100:.1f}%")
                mc4.metric("Completion tokens", f"{completion_tok_act:,}")
                mc5.metric("Est. cost",         cost_str)
                if budget["context_truncated"] or budget["page_truncated"]:
                    st.warning("⚠️ Content was truncated to fit this model's context window.")
                st.json(parsed)
        else:
            st.error(f"❌ **{model_label}**: {err}")
            failed_count += 1

        if save_results and ok:
            try:
                append_record(record, fname)
                saved_count += 1
                status_text.success(f"💾 Saved [{saved_count}] **{model_label}** · {format_cost(actual_cost)}")
            except Exception as save_err:
                st.warning(f"⚠️ Save failed for **{model_label}**: {save_err}")

        progress.progress(step / total)

    # ── Final summary ──────────────────────────────────────────────────────────
    progress.empty()
    status_text.empty()

    total_cost_all = sum(
        r["estimated_cost_usd"]
        for r in all_run_records
        if r.get("ok") and r.get("estimated_cost_usd") is not None
    )
    ok_count = sum(1 for r in all_run_records if r.get("ok"))

    st.markdown("---")
    st.subheader("📊 Run Summary")
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Total calls",        total)
    s2.metric("✅ Successful",      ok_count)
    s3.metric("❌ Failed",          failed_count)
    s4.metric("💾 Saved",           saved_count)
    s5.metric("💰 Total est. cost", format_cost(total_cost_all if ok_count else None))

    if save_results and saved_count:
        st.info(f"📁 Records appended live to `{fname}`")

    st.download_button(
        "⬇️ Download all results (JSON)",
        json.dumps(all_run_records, ensure_ascii=False, indent=2),
        file_name=f"esg_results_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
        mime="application/json",
        key="dl_results",
    )