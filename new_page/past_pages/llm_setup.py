"""
ESG Structured Extraction — OpenRouter + LM Studio backends,
with selectable prompt templates from /prompt/*.md
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

DEFAULT_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
API_KEY_ENV   = "OPENROUTER_API_KEY"

PROMPT_DIR    = Path(__file__).resolve().parents[1] / "prompt"
OCR_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"
MODELS_CACHE  = Path(__file__).parent / "models_cache.json"

BACKEND_OPENROUTER = "OpenRouter"
BACKEND_LMSTUDIO   = "LM Studio (Local)"

CHARS_PER_TOKEN      = 4
DEFAULT_CTX_TOKENS   = 4096

FREE_MODELS_CURATED = [
    "stepfun/step-3.5-flash:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-3-27b-it:free",
    "deepseek/deepseek-r1:free",
]


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT LOADER
# ══════════════════════════════════════════════════════════════════════════════

def list_prompt_files() -> list[Path]:
    """Return all .md prompt files from the /prompt directory."""
    if not PROMPT_DIR.exists():
        return []
    return sorted(PROMPT_DIR.glob("*.md"))


def load_prompt_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def apply_prompt(template: str, input_text: str) -> str:
    """Replace {{INPUT_TEXT}} placeholder in the prompt template."""
    if "{{INPUT_TEXT}}" in template:
        return template.replace("{{INPUT_TEXT}}", input_text)
    # If no placeholder, append text at the end
    return template.strip() + f"\n\n---\n\nText to analyze:\n{input_text}"


# ══════════════════════════════════════════════════════════════════════════════
# SESSION + RETRY HELPERS
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

def _models_cache_age() -> float:
    try:
        return time.time() - MODELS_CACHE.stat().st_mtime
    except Exception:
        return float("inf")


def _fallback_openrouter_models() -> list[dict]:
    return [
        {"id": "meta-llama/llama-3.1-8b-instruct:free",  "label": "Llama 3.1 8B",      "free": True,  "notes": "free · 131,072 ctx", "ctx": 131072},
        {"id": "meta-llama/llama-3.3-70b-instruct:free",  "label": "Llama 3.3 70B",      "free": True,  "notes": "free · 131,072 ctx", "ctx": 131072},
        {"id": "mistralai/mistral-7b-instruct:free",      "label": "Mistral 7B",          "free": True,  "notes": "free · 32,768 ctx",  "ctx": 32768},
        {"id": "google/gemma-3-27b-it:free",              "label": "Gemma 3 27B",         "free": True,  "notes": "free · 131,072 ctx", "ctx": 131072},
        {"id": "deepseek/deepseek-r1:free",               "label": "DeepSeek R1",         "free": True,  "notes": "free · 65,536 ctx",  "ctx": 65536},
        {"id": "stepfun/step-3.5-flash:free",             "label": "Step 3.5 Flash",      "free": True,  "notes": "free",               "ctx": 32768},
        {"id": "openai/gpt-4o-mini",                      "label": "GPT-4o Mini",         "free": False, "notes": "$0.150/1M · 128k ctx","ctx": 128000},
        {"id": "openai/gpt-4o",                           "label": "GPT-4o",              "free": False, "notes": "$2.500/1M · 128k ctx","ctx": 128000},
        {"id": "anthropic/claude-3.5-sonnet",             "label": "Claude 3.5 Sonnet",   "free": False, "notes": "$3.000/1M · 200k ctx","ctx": 200000},
        {"id": "anthropic/claude-3.5-haiku",              "label": "Claude 3.5 Haiku",    "free": False, "notes": "$0.800/1M · 200k ctx","ctx": 200000},
        {"id": "google/gemini-flash-1.5",                 "label": "Gemini 1.5 Flash",    "free": False, "notes": "$0.075/1M · 1M ctx",  "ctx": 1000000},
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_openrouter_models(api_key: Optional[str] = None) -> list[dict]:
    if not api_key:
        return _fallback_openrouter_models()
    try:
        resp = requests.get(
            OPENROUTER_MODELS_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer":  "https://esg-project.app",
                "X-Title":       "ESG Extractor",
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
                p_cost  = float(pricing.get("prompt", 1))
                c_cost  = float(pricing.get("completion", 1))
                is_free = p_cost == 0.0 and c_cost == 0.0
            except (ValueError, TypeError):
                is_free = str(pricing.get("prompt", "1")) == "0"

            cost_str = "free" if is_free else f"${float(pricing.get('prompt', 0)) * 1_000_000:.3f}/1M"
            ctx_str  = f"{ctx:,} ctx" if ctx else ""
            notes    = " · ".join(filter(None, [cost_str, ctx_str]))
            models.append({"id": mid, "label": name, "free": is_free, "notes": notes, "ctx": ctx})

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
            }
            for m in raw if m.get("id")
        ]
    except requests.ConnectionError:
        return []
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════════
# JSON PARSING
# ══════════════════════════════════════════════════════════════════════════════

def _extract_first_json(text: str) -> Optional[str]:
    m = re.search(r"```json\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m2 = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text)
    if m2:
        return m2.group(1)
    return None


def parse_json_from_model(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        js = _extract_first_json(text)
        if js:
            try:
                return json.loads(js)
            except Exception:
                import ast
                try:
                    return ast.literal_eval(js)
                except Exception:
                    pass
    raise ValueError("Could not parse JSON from model output.")


# ══════════════════════════════════════════════════════════════════════════════
# LLM CALLERS
# ══════════════════════════════════════════════════════════════════════════════

def _call_openrouter(
    prompt: str,
    model: str,
    api_key: str,
    temperature: float = 0.0,
    max_tokens: int = 1500,
    retries: int = 3,
) -> str:
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
            resp = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data    = resp.json()
            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                return msg.get("content", "")
            return resp.text
        except Exception as e:
            last_exc = e
            time.sleep(min(10, 2 ** attempt))
    raise RuntimeError(f"OpenRouter failed after {retries} attempts: {last_exc}")


def _call_lmstudio(
    prompt: str,
    model: str,
    base_url: str,
    temperature: float = 0.0,
    max_tokens: int = 1500,
) -> str:
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
    if model and "/" not in model:
        payload["model"] = model
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.HTTPError as e:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise requests.HTTPError(f"{e} — LM Studio: {detail}", response=resp) from e
    return resp.json()["choices"][0]["message"]["content"]


def call_llm(
    prompt: str,
    model: str,
    backend: str,
    api_key: str = "",
    lmstudio_url: str = LMSTUDIO_DEFAULT_URL,
    temperature: float = 0.0,
    max_tokens: int = 1500,
    retries: int = 3,
) -> str:
    if backend == BACKEND_LMSTUDIO:
        return _call_lmstudio(prompt, model, lmstudio_url, temperature, max_tokens)
    return _call_openrouter(prompt, model, api_key, temperature, max_tokens, retries)


# ══════════════════════════════════════════════════════════════════════════════
# IMMEDIATE SAVE
# ══════════════════════════════════════════════════════════════════════════════

def append_record(record: dict, fname: Path) -> None:
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
    tmp.replace(fname)    # atomic replace


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
# PAGE
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="ESG LLM Extractor", page_icon="🌿", layout="wide")
st.title("🌿 ESG Structured Extraction")
st.caption("Extract structured ESG records via OpenRouter or LM Studio with selectable prompt templates.")

# ── Load OpenRouter models ─────────────────────────────────────────────────────
with st.spinner("🔄 Fetching models from OpenRouter…"):
    all_or_models = fetch_openrouter_models(st.session_state.openrouter_key or None)

free_models  = [m for m in all_or_models if     m["free"]]
paid_models  = [m for m in all_or_models if not m["free"]]
id_to_model  = {m["id"]: m for m in all_or_models}

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
    )
    st.session_state.backend = backend

    # ── OpenRouter API Key ────────────────────────────────────────────────────
    if backend == BACKEND_OPENROUTER:
        st.subheader("🔑 API Key")
        api_key_input = st.text_input(
            "OpenRouter API Key",
            type="password",
            value=st.session_state.openrouter_key,
            help="Get your key at https://openrouter.ai/keys",
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

        # Connectivity check
        if st.button("🔌 Run Connectivity Check", use_container_width=True):
            try:
                host = urlparse(OPENROUTER_API_URL).hostname
                addr = socket.getaddrinfo(host, 443)
                st.success(f"DNS OK: {', '.join({ai[4][0] for ai in addr})}")
            except Exception as e:
                st.error(f"Connectivity issue: {e}")

    # ── LM Studio ─────────────────────────────────────────────────────────────
    else:
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
                st.caption(f"🏠 Local · `{sel_lms['id']}`")
            active_model_id = st.session_state.lmstudio_model_id
            active_m        = id_to_model.get(active_model_id)
        else:
            st.warning("No models found — load a model in LM Studio first.")
            active_model_id = ""
            active_m        = None

        # Allow multiple models for batch comparison
        selected_models = [active_model_id] if active_model_id else []

    else:
        tier = st.radio("Show:", ["🆓 Free Only", "💳 Paid Only", "🔀 All"], horizontal=True)
        visible = (
            free_models if tier == "🆓 Free Only" else
            paid_models if tier == "💳 Paid Only" else
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
        selected_models = [
            m["id"] for m in all_or_models if m["label"] in selected_labels
        ]
        if selected_models:
            st.session_state.active_model_id = selected_models[0]
        active_model_id = st.session_state.active_model_id
        active_m        = id_to_model.get(active_model_id)

        if active_m:
            tier_badge = "🆓 Free" if active_m["free"] else "💳 Paid"
            st.caption(f"{tier_badge} · {active_m['notes']}\n\n`{active_m['id']}`")

    st.divider()

    # ── Generation Settings ───────────────────────────────────────────────────
    st.header("⚙️ Generation")
    temperature_input = st.slider("Temperature",  0.0, 1.0, 0.0, 0.01)
    max_tokens_input  = st.number_input("Max tokens", value=1500, min_value=64, step=100)
    retries_input     = st.number_input("Retries",    value=3,    min_value=0,  step=1)

    st.divider()

    # ── Prompt Selector ───────────────────────────────────────────────────────
    st.header("📝 Prompt Template")

    prompt_files = list_prompt_files()
    if not prompt_files:
        st.warning(f"No .md files found in `{PROMPT_DIR}`")
        selected_prompt_path = None
    else:
        prompt_names  = [p.name for p in prompt_files]
        selected_name = st.selectbox(
            "Select prompt",
            prompt_names,
            index=prompt_names.index("data.md") if "data.md" in prompt_names else 0,
            help="Prompt files are loaded from the /prompt directory",
        )
        selected_prompt_path = PROMPT_DIR / selected_name

        # Preview
        with st.expander("👁️ Preview prompt", expanded=False):
            raw_prompt = load_prompt_file(selected_prompt_path)
            st.markdown(raw_prompt[:1500] + ("…" if len(raw_prompt) > 1500 else ""))

        # Manual edit / override
        with st.expander("✏️ Override prompt (optional)", expanded=False):
            st.caption(
                "Edit the prompt below. Use `{{INPUT_TEXT}}` as the placeholder "
                "for the input text. Leave blank to use the file as-is."
            )
            prompt_override = st.text_area(
                "Custom prompt",
                value="",
                height=200,
                placeholder="Leave blank to use the selected prompt file…",
            )

    st.divider()

    # ── Save option ───────────────────────────────────────────────────────────
    st.header("💾 Output")
    save_results = st.checkbox("Save each result immediately to esg_records.json", value=True)
    use_mock     = st.checkbox("Use mock responses (offline/testing)", value=False)


# ══════════════════════════════════════════════════════════════════════════════
# INPUT SOURCE
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📥 Input Source")
input_mode = st.radio("Input source", ["Manual text", "OCR output file"], horizontal=True)

texts_to_process: list[dict] = []

if input_mode == "Manual text":
    manual_text = st.text_area("Enter text to analyze", height=200)
    if manual_text.strip():
        texts_to_process = [{"label": "manual_input", "text": manual_text.strip()}]

else:
    doc_folders = sorted(
        [d for d in OCR_OUTPUT_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    ) if OCR_OUTPUT_DIR.exists() else []

    if not doc_folders:
        st.warning(f"No document folders found in `{OCR_OUTPUT_DIR}`")
    else:
        doc_names    = [d.name for d in doc_folders]
        selected_doc = st.selectbox("Select document", doc_names)
        pages_dir    = OCR_OUTPUT_DIR / selected_doc / "pages"
        page_files   = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []

        if not page_files:
            st.warning(f"No `.md` page files found in `{pages_dir}`")
        else:
            page_names     = [p.name for p in page_files]
            selection_mode = st.radio(
                "Page selection", ["All pages", "Select specific pages"], horizontal=True
            )
            if selection_mode == "All pages":
                chosen_pages = page_files
            else:
                chosen_names = st.multiselect("Select page(s)", page_names, default=[page_names[0]])
                chosen_pages = [pages_dir / n for n in chosen_names]

            if chosen_pages:
                with st.expander(f"📄 Preview ({len(chosen_pages)} page(s) selected)"):
                    for pf in chosen_pages[:5]:
                        st.markdown(f"**{pf.name}**")
                        st.text(
                            pf.read_text(encoding="utf-8")[:500]
                            + ("…" if pf.stat().st_size > 500 else "")
                        )
                    if len(chosen_pages) > 5:
                        st.caption(f"… and {len(chosen_pages) - 5} more page(s)")

                texts_to_process = [
                    {
                        "label": f"{selected_doc}/{pf.name}",
                        "text":  pf.read_text(encoding="utf-8").strip(),
                    }
                    for pf in chosen_pages
                    if pf.read_text(encoding="utf-8").strip()
                ]

# ══════════════════════════════════════════════════════════════════════════════
# RUN SUMMARY BEFORE EXECUTION
# ══════════════════════════════════════════════════════════════════════════════
if texts_to_process and selected_models:
    c1, c2, c3 = st.columns(3)
    c1.metric("Pages to process",  len(texts_to_process))
    c2.metric("Models selected",   len(selected_models))
    c3.metric("Total API calls",   len(texts_to_process) * len(selected_models))

    with st.expander("📋 Run plan", expanded=False):
        for t in texts_to_process:
            for m in selected_models:
                m_info = id_to_model.get(m, {})
                st.markdown(f"- `{t['label']}` → **{m_info.get('label', m)}**")

# ══════════════════════════════════════════════════════════════════════════════
# EXECUTE
# ══════════════════════════════════════════════════════════════════════════════
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

    # ── Resolve prompt template ────────────────────────────────────────────────
    if selected_prompt_path:
        base_prompt = (
            prompt_override.strip()
            if "prompt_override" in dir() and prompt_override.strip()
            else load_prompt_file(selected_prompt_path)
        )
        prompt_label = (
            "custom override"
            if "prompt_override" in dir() and prompt_override.strip()
            else selected_prompt_path.name
        )
    else:
        base_prompt  = "You are an ESG expert. Analyze:\n{{INPUT_TEXT}}\nOutput JSON list."
        prompt_label = "default fallback"

    st.info(f"📝 Using prompt: **{prompt_label}**")

    # ── Prepare output ─────────────────────────────────────────────────────────
    results_dir = Path(__file__).resolve().parents[1] / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    fname = results_dir / "esg_records.json"

    total            = len(texts_to_process) * len(selected_models)
    step             = 0
    saved_count      = 0
    failed_count     = 0
    all_run_records: list = []

    progress    = st.progress(0)
    status_text = st.empty()

    for item in texts_to_process:
        for model in selected_models:
            step += 1
            m_info      = id_to_model.get(model, {})
            model_label = m_info.get("label", model)
            status_text.info(
                f"⏳ [{step}/{total}] `{item['label']}` → **{model_label}**"
                f" ({'🏠 LM Studio' if backend == BACKEND_LMSTUDIO else '☁️ OpenRouter'})"
            )

            # Build final prompt
            final_prompt = apply_prompt(base_prompt, item["text"])

            if use_mock:
                parsed  = [{"text": item["text"][:100], "labels": [], "esg": [], "sentiment": "neutral", "note": "mock"}]
                ok, err = True, None
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
                    parsed  = parse_json_from_model(raw_output)
                    if not isinstance(parsed, list):
                        parsed = [parsed] if isinstance(parsed, dict) else []
                    ok, err = True, None
                except Exception as e:
                    parsed  = []
                    ok, err = False, str(e)

            # Build record
            record = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source":    item["label"],
                "model":     model,
                "backend":   backend,
                "prompt":    prompt_label,
                "input":     item["text"],
                "ok":        ok,
                "records":   parsed,
                **({"error": err} if err else {}),
            }
            all_run_records.append(record)

            # Show inline
            if ok:
                with st.expander(
                    f"✅ `{item['label']}` × **{model_label}** — {len(parsed)} record(s)"
                ):
                    st.json(parsed)
            else:
                st.error(f"❌ `{item['label']}` × **{model_label}**: {err}")
                failed_count += 1

            # ── Save immediately on success ────────────────────────────────────
            if save_results and ok:
                try:
                    append_record(record, fname)
                    saved_count += 1
                    status_text.success(
                        f"✅ Saved [{saved_count}] `{item['label']}` → **{model_label}**"
                    )
                except Exception as save_err:
                    st.warning(f"⚠️ Save failed for `{item['label']}`: {save_err}")

            progress.progress(step / total)

    # ── Final summary ──────────────────────────────────────────────────────────
    progress.empty()
    status_text.empty()

    ok_count = sum(1 for r in all_run_records if r.get("ok"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total",     total)
    c2.metric("✅ OK",     ok_count)
    c3.metric("❌ Failed", failed_count)
    c4.metric("💾 Saved",  saved_count)

    if save_results and saved_count:
        st.info(f"📁 Records saved to `{fname}`")

    st.download_button(
        "⬇️ Download all results from this run (JSON)",
        json.dumps(all_run_records, ensure_ascii=False, indent=2),
        file_name=f"esg_results_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
        mime="application/json",
    )