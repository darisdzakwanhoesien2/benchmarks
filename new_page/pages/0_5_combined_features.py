import os
import re
import sys
import time
import json
import socket
import tempfile
import matplotlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter, Retry
import streamlit as st

# ── Fix temp directory BEFORE any gradio import ───────────────────────────────
_LOCAL_TMP = Path(__file__).resolve().parents[2] / ".tmp"
_LOCAL_TMP.mkdir(parents=True, exist_ok=True)

def _ensure_tempdir():
    try:
        tempfile.gettempdir()
    except FileNotFoundError:
        os.environ["TMPDIR"]  = str(_LOCAL_TMP)
        os.environ["TEMP"]    = str(_LOCAL_TMP)
        os.environ["TMP"]     = str(_LOCAL_TMP)
        tempfile.tempdir      = str(_LOCAL_TMP)

_ensure_tempdir()

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── ClimateBERT — lazy import ─────────────────────────────────────────────────
ClimateBERTClient = None
_climatebert_import_error: str = ""

try:
    from api.climatebert_client import ClimateBERTClient as _CB
    ClimateBERTClient = _CB
except Exception as _e:
    _climatebert_import_error = str(_e)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
OPENROUTER_API_URL    = os.getenv("OPENROUTER_API_URL",    "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODELS_URL = os.getenv("OPENROUTER_MODELS_URL", "https://openrouter.ai/api/v1/models")
LMSTUDIO_DEFAULT_URL  = "http://localhost:1234/v1"
DEFAULT_MODEL         = "meta-llama/llama-3.1-8b-instruct:free"
API_KEY_ENV           = "OPENROUTER_API_KEY"
BACKEND_OPENROUTER    = "OpenRouter"
BACKEND_LMSTUDIO      = "LM Studio (Local)"

PROMPT_DIR     = Path(__file__).resolve().parents[1] / "prompt"
OCR_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"
RESULTS_DIR    = Path(__file__).resolve().parents[1] / "results"

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE DEFAULTS
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
st.set_page_config(
    page_title="ESG Combined Pipeline",
    page_icon="🌿",
    layout="wide",
)
st.title("🌿 ESG Combined Pipeline")
st.caption(
    "Run ClimateBERT predictions (T1), ABSA analysis (T2), and "
    "LLM-based ESG structured extraction (T3) — with full-document context."
)

# Show import warning in UI (non-fatal)
if _climatebert_import_error:
    st.warning(
        f"⚠️ **ClimateBERT unavailable** — T1 pipeline will be skipped.\n\n"
        f"`{_climatebert_import_error}`\n\n"
        f"**Fix:** Run `mkdir -p /tmp` in your terminal, or restart the app."
    )

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — SERIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
def _serialize(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_serialize(o) for o in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):                return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)): return obj.item()
        if isinstance(obj, np.bool_):                  return bool(obj)
    except ImportError:
        pass
    try:
        import torch
        if isinstance(obj, torch.Tensor):
            return obj.cpu().detach().numpy().tolist()
    except ImportError:
        pass
    if isinstance(obj, Path):     return str(obj)
    if isinstance(obj, datetime): return obj.isoformat()
    if isinstance(obj, matplotlib.figure.Figure): return "<matplotlib.figure.Figure>"
    try:
        import plotly.graph_objs as go
        if isinstance(obj, go.Figure): return obj.to_dict()
    except Exception:
        pass
    if hasattr(obj, "to_dict") and not isinstance(obj, type):
        try:    return obj.to_dict()
        except Exception: pass
    return str(obj)


def make_json_safe(value):
    return _serialize(value)


def append_record(record: dict, fname: Path) -> None:
    """Atomically append one record to a JSON array file."""
    existing: list = []
    if fname.exists():
        try:
            loaded   = json.loads(fname.read_text(encoding="utf-8"))
            existing = loaded if isinstance(loaded, list) else [loaded]
        except Exception:
            existing = []
    existing.append(make_json_safe(record))
    tmp = fname.with_suffix(".tmp")
    tmp.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(fname)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — PROMPT
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
# HELPERS — HTTP / RETRY
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
# HELPERS — MODEL FETCHERS
# ══════════════════════════════════════════════════════════════════════════════
def _fallback_openrouter_models() -> list[dict]:
    return [
        {"id": "meta-llama/llama-3.1-8b-instruct:free",  "label": "Llama 3.1 8B",    "free": True,  "notes": "free · 131k ctx",  "ctx": 131072},
        {"id": "meta-llama/llama-3.3-70b-instruct:free",  "label": "Llama 3.3 70B",    "free": True,  "notes": "free · 131k ctx",  "ctx": 131072},
        {"id": "mistralai/mistral-7b-instruct:free",      "label": "Mistral 7B",        "free": True,  "notes": "free · 32k ctx",   "ctx": 32768},
        {"id": "google/gemma-3-27b-it:free",              "label": "Gemma 3 27B",       "free": True,  "notes": "free · 131k ctx",  "ctx": 131072},
        {"id": "deepseek/deepseek-r1:free",               "label": "DeepSeek R1",       "free": True,  "notes": "free · 65k ctx",   "ctx": 65536},
        {"id": "openai/gpt-4o-mini",                      "label": "GPT-4o Mini",       "free": False, "notes": "$0.15/1M · 128k",  "ctx": 128000},
        {"id": "openai/gpt-4o",                           "label": "GPT-4o",            "free": False, "notes": "$2.50/1M · 128k",  "ctx": 128000},
        {"id": "anthropic/claude-3.5-sonnet",             "label": "Claude 3.5 Sonnet", "free": False, "notes": "$3.00/1M · 200k",  "ctx": 200000},
        {"id": "anthropic/claude-3.5-haiku",              "label": "Claude 3.5 Haiku",  "free": False, "notes": "$0.80/1M · 200k",  "ctx": 200000},
        {"id": "google/gemini-flash-1.5",                 "label": "Gemini 1.5 Flash",  "free": False, "notes": "$0.075/1M · 1M",   "ctx": 1000000},
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
            {"id": m.get("id", ""), "label": m.get("id", ""), "free": True,
             "notes": "local · LM Studio", "ctx": m.get("context_length", 4096)}
            for m in raw if m.get("id")
        ]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — LLM CALLERS
# ══════════════════════════════════════════════════════════════════════════════
# def parse_json_from_model(text: str) -> Any:
#     import json, re
#     # Try direct JSON
#     try:
#         return json.loads(text)
#     except Exception:
#         pass
#     # Try to extract JSON from code block or anywhere in text
#     matches = re.findall(r'(\{[\s\S]*?\}|\[[\s\S]*?\])', text)
#     for m in matches:
#         try:
#             return json.loads(m)
#         except Exception:
#             continue
#     # Try ast.literal_eval as a last resort
#     import ast
#     for m in matches:
#         try:
#             return ast.literal_eval(m)
#         except Exception:
#             continue
#     raise ValueError("Could not parse JSON from model output.")


def parse_json_from_model(text: str) -> Any:
    import json, re, ast

    if not text or not text.strip():
        raise ValueError("Empty response from model.")

    text = text.strip()

    # 🔹 Remove markdown code blocks
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip("` \n")

    # 🔹 Try direct JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # 🔹 Extract largest JSON block
    matches = re.findall(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)

    if matches:
        matches = sorted(matches, key=len, reverse=True)
        for m in matches:
            try:
                return json.loads(m)
            except Exception:
                try:
                    return ast.literal_eval(m)
                except Exception:
                    continue

    raise ValueError(f"Could not parse JSON. Raw output:\n{text[:500]}")

def _call_openrouter(prompt: str, model: str, api_key: str,
                     temperature: float = 0.0, max_tokens: int = 1500, retries: int = 3) -> str:

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. "
                    "Return ONLY valid JSON. "
                    "Do NOT include markdown, explanations, comments, or text outside JSON. "
                    "If unsure, return an empty JSON list []."
                )
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    s = _requests_session(retries=retries)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://esg-project.app",
        "X-Title": "ESG Extractor",
    }

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            choices = resp.json().get("choices", [])

            if choices:
                return choices[0].get("message", {}).get("content", "")

            return resp.text

        except Exception as e:
            last_exc = e
            time.sleep(min(10, 2 ** attempt))

    raise RuntimeError(f"OpenRouter failed after {retries} attempts: {last_exc}")

# def _call_openrouter(prompt: str, model: str, api_key: str,
#                      temperature: float = 0.0, max_tokens: int = 1500, retries: int = 3) -> str:
#     payload = {
#         "model": model,
#         "messages": [
#             {"role": "system", "content": "You are an API. Output only valid JSON. Do not include explanations, markdown, or any extra text."},
#             {"role": "user",   "content": prompt},
#         ],
#         "temperature": temperature,
#         "max_tokens":  max_tokens,
#     }
#     s       = _requests_session(retries=retries)
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type":  "application/json",
#         "HTTP-Referer":  "https://esg-project.app",
#         "X-Title":       "ESG Extractor",
#     }
#     last_exc = None
#     for attempt in range(1, retries + 1):
#         try:
#             resp    = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90)
#             resp.raise_for_status()
#             choices = resp.json().get("choices", [])
#             if choices:
#                 return choices[0].get("message", {}).get("content", "")
#             return resp.text
#         except Exception as e:
#             last_exc = e
#             time.sleep(min(10, 2 ** attempt))
#     raise RuntimeError(f"OpenRouter failed after {retries} attempts: {last_exc}")


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
# LOAD OPENROUTER MODELS
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("🔄 Fetching OpenRouter models…"):
    all_or_models = fetch_openrouter_models(st.session_state.openrouter_key or None)

free_models = [m for m in all_or_models if     m["free"]]
paid_models = [m for m in all_or_models if not m["free"]]
id_to_model = {m["id"]: m for m in all_or_models}

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ Global Settings")

    st.subheader("🔀 Pipelines")
    _t1_disabled = ClimateBERTClient is None
    run_t1 = st.checkbox(
        "T1 · ClimateBERT Predictions",
        value=not _t1_disabled,
        disabled=_t1_disabled,
        help="Unavailable — ClimateBERT failed to import" if _t1_disabled else "",
    )
    run_t2 = st.checkbox("T2 · ABSA Analysis",      value=True)
    run_t3 = st.checkbox("T3 · LLM ESG Extraction", value=True)

    st.divider()

    st.subheader("🖥️ LLM Backend (T3)")
    backend = st.radio(
        "Backend",
        [BACKEND_OPENROUTER, BACKEND_LMSTUDIO],
        index=0 if st.session_state.backend == BACKEND_OPENROUTER else 1,
        horizontal=True,
        key="backend_radio",
    )
    st.session_state.backend = backend

    if backend == BACKEND_OPENROUTER:
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
            st.warning("⚠️ No API key — only free/mock mode available")
        if st.button("🔄 Refresh Model List", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        if st.button("🔌 Connectivity Check", use_container_width=True):
            try:
                host = urlparse(OPENROUTER_API_URL).hostname
                addr = socket.getaddrinfo(host, 443)
                st.success(f"DNS OK: {', '.join({ai[4][0] for ai in addr})}")
            except Exception as e:
                st.error(f"DNS issue: {e}")
    else:
        lmstudio_url_input = st.text_input(
            "LM Studio URL", value=st.session_state.lmstudio_url,
            help="Default: http://localhost:1234/v1",
        )
        st.session_state.lmstudio_url = lmstudio_url_input
        lms_models = fetch_lmstudio_models(lmstudio_url_input)
        if lms_models:
            st.success(f"✅ {len(lms_models)} model(s) loaded")
            id_to_model.update({m["id"]: m for m in lms_models})
        else:
            st.error("❌ Cannot reach LM Studio")

    st.divider()

    st.subheader("🤖 LLM Model (T3)")
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
            selected_llm_models = [st.session_state.lmstudio_model_id] if st.session_state.lmstudio_model_id else []
        else:
            st.warning("No local models — load one in LM Studio first.")
            selected_llm_models = []
    else:
        tier = st.radio(
            "Filter:", ["🆓 Free Only", "💳 Paid Only", "🔀 All"],
            horizontal=True, key="model_tier",
        )
        visible = (
            free_models if "Free" in tier else
            paid_models if "Paid" in tier else
            all_or_models
        )
        search = st.text_input("🔍 Search model", placeholder="llama, claude, mistral…")
        if search.strip():
            visible = [m for m in visible if search.lower() in m["label"].lower() or search.lower() in m["id"].lower()]

        visible_labels = [m["label"] for m in visible]
        curr_label     = id_to_model.get(st.session_state.active_model_id, {}).get("label", "")
        def_idx        = visible_labels.index(curr_label) if curr_label in visible_labels else 0

        sel_labels = st.multiselect(
            f"Model(s) ({len(visible)} shown)",
            options=visible_labels,
            default=[visible_labels[def_idx]] if visible_labels else [],
        )
        selected_llm_models = [m["id"] for m in all_or_models if m["label"] in sel_labels]
        if selected_llm_models:
            st.session_state.active_model_id = selected_llm_models[0]
            active_m = id_to_model.get(selected_llm_models[0])
            if active_m:
                badge = "🆓 Free" if active_m["free"] else "💳 Paid"
                st.caption(f"{badge} · {active_m['notes']}\n\n`{active_m['id']}`")

    st.divider()

    st.subheader("⚙️ Generation (T3)")
    temperature_input = st.slider("Temperature", 0.0, 1.0, 0.0, 0.01)
    max_tokens_input  = st.number_input("Max tokens", value=1500, min_value=64, step=100)
    retries_input     = st.number_input("Retries", value=3, min_value=0, step=1)

    st.divider()

    st.subheader("📝 Prompt Template (T3)")
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
            prompt_override = st.text_area("Custom prompt", value="", height=150,
                                           placeholder="Leave blank to use the selected file…")

    st.divider()

    st.subheader("💾 Output")
    save_t1     = st.checkbox("Save T1 predictions",       value=True)
    save_t2     = st.checkbox("Save T2 ABSA results",      value=True)
    save_t3     = st.checkbox("Save T3 ESG records",       value=True)
    use_mock_t3 = st.checkbox("Mock T3 (offline testing)", value=False)
    run_deep_model = st.checkbox("Run Deep Model in T2 (slow)", value=False)

    st.divider()
    st.subheader("🛠️ System")
    try:
        _td = tempfile.gettempdir()
        st.success(f"✅ Temp dir: `{_td}`")
    except Exception as _te:
        st.error(f"❌ Temp dir broken: {_te}\n\nFallback: `{_LOCAL_TMP}`")
    if st.button("🔧 Fix temp dir", use_container_width=True):
        _ensure_tempdir()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# INPUT SOURCE
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📥 Input Source")
input_mode = st.radio(
    "Mode", ["Manual text", "OCR document"],
    horizontal=True,
    key="input_mode_radio",
)

texts_to_process:    list[dict] = []
doc_full_text:       str        = ""
selected_page_texts: list[dict] = []
all_page_files:      list       = []

if input_mode == "Manual text":
    manual_text = st.text_area("Enter text to analyze", height=200, key="manual_text_area")
    if manual_text.strip():
        t = manual_text.strip()
        texts_to_process    = [{"label": "manual_input", "text": t}]
        selected_page_texts = texts_to_process
        doc_full_text       = t
        all_page_files      = []

else:
    doc_folders = sorted(
        [d for d in OCR_OUTPUT_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    ) if OCR_OUTPUT_DIR.exists() else []

    if not doc_folders:
        st.warning(f"No document folders found in `{OCR_OUTPUT_DIR}`")
    else:
        doc_names    = [d.name for d in doc_folders]
        selected_doc = st.selectbox("Select document", doc_names, key="doc_select")
        pages_dir    = OCR_OUTPUT_DIR / selected_doc / "pages"
        all_page_files = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []

        if not all_page_files:
            st.warning(f"No `.md` page files in `{pages_dir}`")
        else:
            page_names = [p.name for p in all_page_files]

            doc_full_text = "\n\n".join(
                pf.read_text(encoding="utf-8").strip()
                for pf in all_page_files
                if pf.read_text(encoding="utf-8").strip()
            )

            st.info(
                f"📄 **Full document**: {len(all_page_files)} page(s) · "
                f"~{len(doc_full_text):,} chars loaded as LLM context"
            )

            st.markdown("#### 📑 Select pages for sentence-level extraction")
            st.caption(
                "The **full document** is always sent to the LLM as context. "
                "Use this to focus extraction on specific pages."
            )

            selection_mode = st.radio(
                "Page selection", ["All pages", "Select specific pages"],
                horizontal=True,
                key="page_selection_radio",
            )

            if selection_mode == "All pages":
                chosen_pages = all_page_files
            else:
                chosen_names = st.multiselect(
                    "Select page(s)", page_names,
                    default=[page_names[0]],
                    key="page_multiselect",
                )
                chosen_pages = [pages_dir / n for n in chosen_names]

            if chosen_pages:
                with st.expander(f"📄 Preview ({len(chosen_pages)} page(s))", expanded=False):
                    for pf in chosen_pages[:5]:
                        st.markdown(f"**{pf.name}**")
                        content = pf.read_text(encoding="utf-8")
                        st.text(content[:400] + ("…" if len(content) > 400 else ""))
                    if len(chosen_pages) > 5:
                        st.caption(f"… and {len(chosen_pages) - 5} more page(s)")

                selected_page_texts = [
                    {"label": f"{selected_doc}/{pf.name}", "text": pf.read_text(encoding="utf-8").strip()}
                    for pf in chosen_pages
                    if pf.read_text(encoding="utf-8").strip()
                ]
                texts_to_process = selected_page_texts

# ══════════════════════════════════════════════════════════════════════════════
# RUN SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
if texts_to_process:
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Pages selected",   len(texts_to_process))
    col_b.metric("LLM models (T3)",  len(selected_llm_models))
    col_c.metric("Pipelines active", sum([run_t1, run_t2, run_t3]))

    if run_t3 and selected_llm_models and doc_full_text:
        with st.expander("📋 T3 run plan", expanded=False):
            st.markdown(
                f"**Context:** full document (~{len(doc_full_text):,} chars)\n\n"
                f"**Sentence capture pages:** {len(texts_to_process)}"
            )
            for m in selected_llm_models:
                m_info = id_to_model.get(m, {})
                st.markdown(f"- **{m_info.get('label', m)}** · `{m}`")

# ══════════════════════════════════════════════════════════════════════════════
# EXECUTE BUTTON
# ══════════════════════════════════════════════════════════════════════════════
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

if st.button("🚀 Run Selected Pipelines", type="primary", use_container_width=True):
    if not texts_to_process:
        st.warning("⚠️ No text selected. Enter text or select pages above.")
        st.stop()
    if not any([run_t1, run_t2, run_t3]):
        st.warning("⚠️ No pipelines selected in sidebar.")
        st.stop()

    # ─────────────────────────────────────────────────────────────────────────
    # T1 · ClimateBERT
    # ─────────────────────────────────────────────────────────────────────────
    if run_t1:
        st.markdown("---")
        st.subheader("📊 T1 · ClimateBERT Predictions")

        if ClimateBERTClient is None:
            st.error(
                f"❌ ClimateBERT is not available.\n\n`{_climatebert_import_error}`\n\n"
                "**Quick fix:**\n```bash\nsudo mkdir -p /tmp && sudo chmod 1777 /tmp\n```"
            )
        else:
            try:
                api       = ClimateBERTClient()
                cb_models = api.available_models if hasattr(api, "available_models") else []
            except Exception as e:
                st.error(f"ClimateBERT client init failed: {e}")
                cb_models = []

            if not cb_models:
                st.warning("No ClimateBERT models available.")
            else:
                t1_results  = []
                t1_fname    = RESULTS_DIR / "predictions.json"
                t1_progress = st.progress(0)
                t1_total    = len(texts_to_process) * len(cb_models)
                t1_step     = 0

                for item in texts_to_process:
                    for model_key in cb_models:
                        with st.spinner(f"T1 · [{item['label']}] {model_key}…"):
                            try:
                                res     = api.predict(text=item["text"], model_key=model_key)
                                outcome = "✅ ok"
                            except Exception as e:
                                res     = {"error": str(e)}
                                outcome = f"⚠️ {e}"

                            record = {
                                "timestamp": datetime.utcnow().isoformat() + "Z",
                                "model":     model_key,
                                "source":    item["label"],
                                "text":      item["text"],
                                "result":    res,
                            }
                            t1_results.append(record)

                            # ── immediate save after every single record ──
                            if save_t1:
                                try:
                                    append_record(record, t1_fname)
                                    st.caption(f"💾 saved `{model_key}` / `{item['label']}`")
                                except Exception as save_err:
                                    st.warning(f"⚠️ T1 save failed: {save_err}")

                            st.write(f"`{item['label']}` × `{model_key}` → {outcome}")
                        t1_step += 1
                        t1_progress.progress(t1_step / t1_total)

                t1_progress.empty()
                st.success(f"T1 complete · {len(t1_results)} prediction(s)")

                with st.expander("📊 T1 Results JSON", expanded=False):
                    st.json(t1_results)

                if save_t1:
                    st.info(f"💾 T1 records appended live to `{t1_fname}`")

                st.download_button(
                    "⬇️ Download T1 predictions (JSON)",
                    json.dumps([make_json_safe(r) for r in t1_results], ensure_ascii=False, indent=2),
                    file_name=f"predictions_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
                    mime="application/json",
                    key="dl_t1",
                )

    # ─────────────────────────────────────────────────────────────────────────
    # T2 · ABSA  (saves immediately after each page)
    # ─────────────────────────────────────────────────────────────────────────
    if run_t2:
        st.markdown("---")
        st.subheader("🧠 T2 · ABSA Analysis")
        try:
            from code.rule_based import collect_aspects, polarity_basic, tone_basic
            from code.hybrid_model import run_hierarchical_hybrid
            from code.explainability import compare_explain
            absa_imports_ok = True
        except ImportError as e:
            st.error(f"❌ ABSA import failed: {e}")
            absa_imports_ok = False

        if absa_imports_ok:
            t2_fname       = RESULTS_DIR / "absa_results.json"
            all_t2_records = []
            t2_progress    = st.progress(0)
            t2_total       = len(texts_to_process)

            for idx, item in enumerate(texts_to_process):
                text_input = item["text"]
                label      = item["label"]

                st.divider()
                st.markdown(f"#### 📄 `{label}`")

                rb_out = cml_out = hybrid_out = expl_out = {}
                deep_out = {"ran": run_deep_model}

                with st.expander("🔧 Rule-Based", expanded=False):
                    try:
                        aspects  = collect_aspects(text_input)
                        polarity = polarity_basic(text_input)
                        tone     = tone_basic(text_input)
                        st.write(f"**Aspects:** {aspects}")
                        st.write(f"**Polarity:** {polarity}")
                        st.write(f"**Tone:** {tone}")
                        rb_out = {"aspects": aspects, "polarity": polarity, "tone": tone}
                    except Exception as e:
                        st.error(f"Rule-based error: {e}")
                        rb_out = {"error": str(e)}

                with st.expander("📐 Classical ML", expanded=False):
                    try:
                        from code.classical_ml import run_classical_ml
                        _, out_df, _, coef_sent, coef_aspect = run_classical_ml(text_input)
                        st.dataframe(out_df,      use_container_width=True)
                        st.dataframe(coef_sent,   use_container_width=True)
                        st.dataframe(coef_aspect, use_container_width=True)
                        cml_out = {"out_df": out_df, "coef_sent": coef_sent, "coef_aspect": coef_aspect}
                    except Exception as e:
                        st.error(f"Classical ML error: {e}")
                        cml_out = {"error": str(e)}

                with st.expander("🧬 Deep Model (mBERT)", expanded=False):
                    if run_deep_model:
                        try:
                            from code.deep_model import run_deep_learning
                            _, deep_df, _, interp_df = run_deep_learning(text_input)
                            st.dataframe(deep_df,   use_container_width=True)
                            st.dataframe(interp_df, use_container_width=True)
                            deep_out.update({"out_df": deep_df, "interpretability": interp_df})
                        except Exception as e:
                            st.error(f"Deep model error: {e}")
                            deep_out["error"] = str(e)
                    else:
                        st.info("Skipped — enable 'Run Deep Model' in sidebar.")

                with st.expander("🔀 Hybrid Model", expanded=False):
                    try:
                        _, hybrid_df, _, _, _, metrics = run_hierarchical_hybrid(text_input)
                        st.dataframe(hybrid_df, use_container_width=True)
                        st.write("**Metrics:**", metrics)
                        # ── always store as list-of-dicts so highlight viewer can iterate ──
                        hybrid_out = {
                            "out_df":  hybrid_df.to_dict(orient="records") if hasattr(hybrid_df, "to_dict") else hybrid_df,
                            "metrics": metrics.to_dict(orient="records")   if hasattr(metrics,   "to_dict") else metrics,
                        }
                    except Exception as e:
                        st.error(f"Hybrid model error: {e}")
                        hybrid_out = {"error": str(e)}

                with st.expander("💡 Explainability", expanded=False):
                    try:
                        expl_df, expl_fig, expl_scatter = compare_explain()
                        st.dataframe(expl_df, use_container_width=True)
                        if expl_fig:                  st.pyplot(expl_fig)
                        if expl_scatter is not None:  st.plotly_chart(expl_scatter)
                        expl_out = {"compare_df": expl_df}
                    except Exception as e:
                        st.error(f"Explainability error: {e}")
                        expl_out = {"error": str(e)}

                record = {
                    "timestamp":      datetime.utcnow().isoformat() + "Z",
                    "source":         label,
                    "input_text":     text_input,
                    "rule_based":     rb_out,
                    "classical_ml":   cml_out,
                    "deep_model":     deep_out,
                    "hybrid_model":   hybrid_out,
                    "explainability": expl_out,
                }
                all_t2_records.append(record)

                # ── immediate save after each page ──
                if save_t2:
                    try:
                        append_record(record, t2_fname)
                        st.caption(f"💾 T2 saved `{label}`")
                    except Exception as save_err:
                        st.error(f"T2 save failed for `{label}`: {save_err}")

                t2_progress.progress((idx + 1) / t2_total)

            t2_progress.empty()
            st.success(f"T2 complete · {len(all_t2_records)} document(s) processed")
            if save_t2:
                st.info(f"💾 T2 records appended live to `{t2_fname}`")

            st.download_button(
                "⬇️ Download T2 ABSA results (JSON)",
                json.dumps([make_json_safe(r) for r in all_t2_records], ensure_ascii=False, indent=2),
                file_name=f"absa_results_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
                mime="application/json",
                key="dl_t2",
            )

    # ─────────────────────────────────────────────────────────────────────────
    # T3 · LLM ESG Extraction  (saves immediately after each model)
    # ─────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────
# T3 · LLM ESG Extraction (FIXED VERSION)
# ─────────────────────────────────────────────────────────────────────────
    if run_t3:
        st.markdown("---")
        st.subheader("🌿 T3 · LLM ESG Structured Extraction")

        if not selected_llm_models:
            st.warning("⚠️ No LLM model selected for T3.")
        elif not doc_full_text:
            st.warning("⚠️ No document text available.")
        elif backend == BACKEND_OPENROUTER and not use_mock_t3 and not st.session_state.openrouter_key:
            st.error("❌ OpenRouter API key not set.")
        else:

            if selected_prompt_path:
                base_prompt = prompt_override.strip() or load_prompt_file(selected_prompt_path)
                prompt_label = "custom override" if prompt_override.strip() else selected_prompt_path.name
            else:
                base_prompt = "Extract ESG records as JSON list from:\n{{INPUT_TEXT}}"
                prompt_label = "default fallback"

            st.info(f"📝 Prompt: **{prompt_label}**")

            def build_context_prompt(full_doc: str, page_texts: list[dict], template: str) -> str:
                page_section = "\n\n---\n\n".join(
                    f"[PAGE: {p['label']}]\n{p['text']}" for p in page_texts
                )

                combined = (
                    f"FULL DOCUMENT:\n{full_doc}\n\n"
                    f"TARGET PAGES:\n{page_section}\n\n"
                    f"Return JSON array of ESG records."
                )

                return apply_prompt(template, combined)

            t3_fname = RESULTS_DIR / "esg_records.json"
            all_t3_records = []

            t3_progress = st.progress(0)
            t3_total = len(selected_llm_models)

            for i, model in enumerate(selected_llm_models, 1):

                st.info(f"⏳ Running model: {model} ({i}/{t3_total})")

                final_prompt = build_context_prompt(doc_full_text, selected_page_texts, base_prompt)

                try:
                    if use_mock_t3:
                        raw_output = json.dumps([
                            {"text": "mock", "esg": "Environmental", "sentiment": "Positive"}
                        ])
                    else:
                        raw_output = call_llm(
                            prompt=final_prompt,
                            model=model,
                            backend=backend,
                            api_key=st.session_state.openrouter_key,
                            lmstudio_url=st.session_state.lmstudio_url,
                            temperature=float(temperature_input),
                            max_tokens=int(max_tokens_input),
                            retries=int(retries_input),
                        )

                    # 🔍 DEBUG OUTPUT
                    with st.expander(f"🧪 Raw Output — {model}"):
                        st.code(raw_output)

                    # ✅ SAFE PARSING
                    try:
                        parsed = parse_json_from_model(raw_output)

                        if isinstance(parsed, dict):
                            parsed = [parsed]
                        elif not isinstance(parsed, list):
                            parsed = []

                        ok = True
                        err = None

                    except Exception as parse_err:
                        parsed = []
                        ok = False
                        err = f"Parse error: {parse_err}"

                except Exception as e:
                    parsed = []
                    ok = False
                    err = str(e)
                    raw_output = ""

                record = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "model": model,
                    "ok": ok,
                    "records": parsed,
                    "error": err,
                }

                all_t3_records.append(record)

                if ok:
                    st.success(f"✅ {model} → {len(parsed)} records")
                    st.json(parsed)
                else:
                    st.error(f"❌ {model} failed: {err}")

                # 💾 SAVE IMMEDIATELY
                if save_t3 and ok:
                    try:
                        append_record(record, t3_fname)
                        st.caption(f"💾 Saved: {model}")
                    except Exception as save_err:
                        st.warning(f"Save failed: {save_err}")

                t3_progress.progress(i / t3_total)

            t3_progress.empty()

            st.success("🎉 T3 Completed")

            st.download_button(
                "⬇️ Download T3 JSON",
                json.dumps(all_t3_records, indent=2, ensure_ascii=False),
                file_name="t3_results.json",
                mime="application/json",
            )

    st.markdown("---")
    st.caption("ESG Combined Pipeline · T1 ClimateBERT · T2 ABSA · T3 LLM Extraction")

    # if run_t3:
    #     st.markdown("---")
    #     st.subheader("🌿 T3 · LLM ESG Structured Extraction")

    #     if not selected_llm_models:
    #         st.warning("⚠️ No LLM model selected for T3.")
    #     elif not doc_full_text:
    #         st.warning("⚠️ No document text available.")
    #     elif backend == BACKEND_OPENROUTER and not use_mock_t3 and not st.session_state.openrouter_key:
    #         st.error("❌ OpenRouter API key not set.")
    #     else:
    #         if selected_prompt_path:
    #             base_prompt  = prompt_override.strip() or load_prompt_file(selected_prompt_path)
    #             prompt_label = "custom override" if prompt_override.strip() else selected_prompt_path.name
    #         else:
    #             base_prompt  = "You are an ESG expert. Analyze:\n{{INPUT_TEXT}}\nOutput a JSON list of ESG records."
    #             prompt_label = "default fallback"

    #         st.info(f"📝 Prompt: **{prompt_label}**")

    #         def build_context_prompt(full_doc: str, page_texts: list[dict], template: str) -> str:
    #             page_section = "\n\n---\n\n".join(
    #                 f"[PAGE: {p['label']}]\n{p['text']}" for p in page_texts
    #             )
    #             combined = (
    #                 f"### FULL DOCUMENT CONTEXT (for reference)\n\n{full_doc}\n\n"
    #                 f"### PAGES TO EXTRACT FROM (focus here)\n\n{page_section}"
    #             )
    #             return apply_prompt(template, combined)

    #         t3_fname       = RESULTS_DIR / "esg_records.json"
    #         all_t3_records = []
    #         t3_total       = len(selected_llm_models)
    #         t3_progress    = st.progress(0)
    #         t3_status      = st.empty()

    #         for t3_step, model in enumerate(selected_llm_models, 1):
    #             m_info      = id_to_model.get(model, {})
    #             model_label = m_info.get("label", model)
    #             t3_status.info(
    #                 f"⏳ [{t3_step}/{t3_total}] **{model_label}** · "
    #                 f"context ~{len(doc_full_text):,} chars · "
    #                 f"{len(selected_page_texts)} page(s) targeted"
    #             )

    #             final_prompt = build_context_prompt(doc_full_text, selected_page_texts, base_prompt)

    #             if use_mock_t3:
    #                 parsed  = [
    #                     {"text": p["text"][:120], "esg": "Environmental",
    #                      "sentiment": "Positive", "labels": ["mock"],
    #                      "note": "mock response", "source": p["label"]}
    #                     for p in selected_page_texts
    #                 ]
    #                 ok, err = True, None
    #             else:
    #                 try:
    #                     raw_output = call_llm(
    #                         prompt       = final_prompt,
    #                         model        = model,
    #                         backend      = backend,
    #                         api_key      = st.session_state.openrouter_key,
    #                         lmstudio_url = st.session_state.lmstudio_url,
    #                         temperature  = float(temperature_input),
    #                         max_tokens   = int(max_tokens_input),
    #                         retries      = int(retries_input),
    #                     )
    #                     parsed = parse_json_from_model(raw_output)
    #                     if not isinstance(parsed, list):
    #                         parsed = [parsed] if isinstance(parsed, dict) else []
    #                     ok, err = True, None
    #                 except Exception as e:
    #                     parsed  = []
    #                     ok, err = False, str(e)

    #             record = {
    #                 "timestamp":      datetime.utcnow().strftime("%Y-%m-%dT%H:%M%SZ"),
    #                 "model":          model,
    #                 "backend":        backend,
    #                 "prompt":         prompt_label,
    #                 "context_pages":  len(all_page_files) if input_mode != "Manual text" else 1,
    #                 "targeted_pages": [p["label"] for p in selected_page_texts],
    #                 "ok":             ok,
    #                 "records":        parsed,
    #                 **({"error": err} if err else {}),
    #             }
    #             all_t3_records.append(record)

    #             if ok:
    #                 with st.expander(
    #                     f"✅ **{model_label}** — {len(parsed)} record(s) extracted",
    #                     expanded=True,
    #                 ):
    #                     st.json(parsed)
    #             else:
    #                 st.error(f"❌ **{model_label}**: {err}")

    #             # ── immediate save after each model ──
    #             if save_t3 and ok:
    #                 try:
    #                     append_record(record, t3_fname)
    #                     st.caption(f"💾 T3 saved · **{model_label}**")
    #                 except Exception as save_err:
    #                     st.warning(f"⚠️ T3 save failed: {save_err}")

    #             t3_progress.progress(t3_step / t3_total)

    #         t3_progress.empty()
    #         t3_status.empty()

    #         ok_count = sum(1 for r in all_t3_records if r.get("ok"))
    #         cc1, cc2, cc3 = st.columns(3)
    #         cc1.metric("Models run",    t3_total)
    #         cc2.metric("✅ Successful", ok_count)
    #         cc3.metric("❌ Failed",     t3_total - ok_count)

    #         if save_t3 and ok_count:
    #             st.info(f"📁 T3 records appended live to `{t3_fname}`")

    #         st.download_button(
    #             "⬇️ Download T3 ESG records (JSON)",
    #             json.dumps(all_t3_records, ensure_ascii=False, indent=2),
    #             file_name=f"esg_records_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
    #             mime="application/json",
    #             key="dl_t3",
    #         )

# # https://huggingface.co/spaces/darisdzakwanhoesien/climatebert-multi-model-demo-docker-new

# import os
# import io
# import json
# import streamlit as st
# from pathlib import Path
# from datetime import datetime

# st.set_page_config(page_title="ClimateBERT · Combined Demo", page_icon="🌡️", layout="wide")
# st.title("🌡️ ClimateBERT — Combined (Remote Space & Local HF Model)")

# # --- results storage setup (new) ---
# RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
# RESULTS_DIR.mkdir(parents=True, exist_ok=True)
# RESULTS_FPATH = RESULTS_DIR / "climatebert_results.json"

# def _json_default(o):
#     try:
#         import numpy as _np
#         if isinstance(o, _np.ndarray):
#             return o.tolist()
#         if isinstance(o, (_np.integer, _np.floating)):
#             return float(o)
#     except Exception:
#         pass
#     try:
#         import torch as _torch
#         if isinstance(o, _torch.Tensor):
#             return o.cpu().detach().numpy().tolist()
#     except Exception:
#         pass
#     if isinstance(o, (Path,)):
#         return str(o)
#     if isinstance(o, datetime):
#         return o.isoformat()
#     return str(o)

# def append_json_record(path: Path, record: dict) -> None:
#     existing = []
#     if path.exists():
#         try:
#             with path.open("r", encoding="utf-8") as f:
#                 loaded = json.load(f)
#             existing = loaded if isinstance(loaded, list) else [loaded]
#         except Exception:
#             existing = []
#     existing.append(record)
#     tmp = path.with_suffix(".tmp")
#     with tmp.open("w", encoding="utf-8") as f:
#         json.dump(existing, f, ensure_ascii=False, indent=2, default=_json_default)
#     tmp.replace(path)

# # --- New: improved parser for `response_raw` from ClimateBERT space ----
# import re
# def parse_response_raw(raw: str) -> dict:
#     """
#     Parse the text blob returned by /predict_all_models into structured JSON.
#     Expected format (examples):
#       ### model-name
#       ❌ Error: ...
#       ### model2
#       • label: 0.92
#       • other: 0.08

#     Returns:
#       {"raw": raw, "models": [ {"name": str, "status": "ok"|"error", "error": str|null, "scores": {label: value}} , ... ] }
#     """
#     if raw is None:
#         return {"raw": raw, "models": []}
#     text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
#     lines = [ln.strip() for ln in text.splitlines()]
#     models = []
#     cur = None

#     bullet_re = re.compile(r"^[•\-\*\u2022]\s*(.+)$")
#     label_val_re = re.compile(r"^(.+?)\s*[:\-]\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")
#     # fallback for lines like "• Not about renewables: 1.00" (label contains spaces)
#     for ln in lines:
#         if not ln:
#             continue
#         if ln.startswith("###"):
#             # new model header
#             name = ln[3:].strip()
#             if cur is not None:
#                 models.append(cur)
#             cur = {"name": name, "status": "ok", "error": None, "scores": {}}
#             continue
#         if cur is None:
#             # preamble / stray lines -> skip or collect under intro model
#             continue
#         # detect explicit error marker
#         if "❌" in ln or ln.lower().startswith("error:") or "unrecognized model" in ln.lower():
#             # collect error message (rest of line)
#             msg = ln.replace("❌", "").strip()
#             if msg.lower().startswith("error:"):
#                 msg = msg[6:].strip()
#             # append to error field (concatenate if multiple lines)
#             if cur.get("error"):
#                 cur["error"] += " | " + msg
#             else:
#                 cur["error"] = msg
#             cur["status"] = "error"
#             continue
#         # bullets
#         m = bullet_re.match(ln)
#         candidate = ln
#         if m:
#             candidate = m.group(1).strip()
#         # try label:value numeric
#         m2 = label_val_re.match(candidate)
#         if m2:
#             key = m2.group(1).strip()
#             try:
#                 val = float(m2.group(2))
#             except Exception:
#                 val = m2.group(2)
#             cur["scores"][key] = val
#             continue
#         # lines like "• no: 0.99" handled above; fallback: lines "• key value"
#         # attempt split on last space and parse numeric tail
#         if m:
#             parts = candidate.rsplit(" ", 1)
#             if len(parts) == 2:
#                 key, tail = parts[0].strip(), parts[1].strip()
#                 try:
#                     val = float(tail)
#                     cur["scores"][key] = val
#                     continue
#                 except Exception:
#                     pass
#         # if we reach here, treat line as free-text message (append to error or store under misc)
#         if "note" not in cur:
#             cur["note"] = ln
#         else:
#             cur["note"] += " | " + ln

#     if cur is not None:
#         models.append(cur)

#     return {"raw": text, "models": models}

# # -------------------------
# # Sidebar / options
# # -------------------------
# st.sidebar.header("Mode")
# mode = st.sidebar.selectbox("Run mode", ["Remote Space (gradio)", "Local HF model (transformers)"])

# # Common inputs
# hf_token_input = st.sidebar.text_input("HF token (optional)", value=os.getenv("HF_TOKEN", ""), type="password")
# use_env_token = st.sidebar.checkbox("Use HF_TOKEN from env if input empty", value=True)

# if use_env_token and not hf_token_input:
#     hf_token = os.getenv("HF_TOKEN", "") or None
# else:
#     hf_token = hf_token_input or None

# # --- results auto-save toggle (added) ---
# auto_save = st.sidebar.checkbox("Auto-save predictions to results/climatebert_results.json", value=True)
# st.sidebar.markdown(f"Results file: `{RESULTS_FPATH}`")

# # -------------------------
# # Remote Space (gradio_client)
# # -------------------------
# if mode == "Remote Space (gradio)":
#     st.header("Remote Space — call /predict_all_models")
#     space_url = st.text_input(
#         "Space URL",
#         value=os.getenv("CLIMATEBERT_SPACE_URL", "https://darisdzakwanhoesien-climatebert-multi-model-demo-8aae81e.hf.space/"),
#         help="HF Space URL (leave default for demo)"
#     )
#     text = st.text_area("Input text", "Hello world — ESG / climate example", height=200)
#     timeout = st.number_input("Timeout (seconds)", value=120, min_value=10, max_value=600, step=10)

#     col1, col2 = st.columns([3, 1])
#     with col1:
#         predict_btn = st.button("Predict (all models)")
#     with col2:
#         st.markdown("Connection test")
#         test_btn = st.button("Test connect")

#     def call_space_predict(url: str, txt: str, token: str | None, timeout_sec: int):
#         try:
#             from gradio_client import Client
#         except Exception as e:
#             raise RuntimeError(f"gradio-client not installed: {e}")
#         kwargs = {}
#         if token:
#             kwargs["hf_token"] = token
#         # instantiate client (do not pass timeout here — gradio_client.Client may not accept it)
#         client = Client(url, **kwargs)
#         # call using named parameter to match space input
#         return client.predict(text=txt, api_name="/predict_all_models")

#     if test_btn:
#         try:
#             st.info("Testing connection…")
#             # a lightweight call: instantiate client and optionally call a health endpoint by predict empty text
#             from gradio_client import Client  # might raise
#             kwargs = {}
#             if hf_token:
#                 kwargs["hf_token"] = hf_token
#             # instantiate client (no timeout argument)
#             Client(space_url, **kwargs)
#             st.success("Client instantiated successfully (no network call performed yet).")
#         except Exception as e:
#             st.error("Connection test failed")
#             st.exception(e)

#     if predict_btn:
#         if not text.strip():
#             st.warning("Enter input text first.")
#         else:
#             try:
#                 with st.spinner("Calling remote space…"):
#                     resp = call_space_predict(space_url, text, hf_token, int(timeout))
#                 st.subheader("Raw response")
#                 # try to pretty-print JSON if possible
#                 parsed = None
#                 try:
#                     parsed = json.loads(resp) if isinstance(resp, (str, bytes)) else resp
#                     st.json(parsed)
#                 except Exception:
#                     st.text(str(resp))

#                 # --- save remote response (new) ---
#                 if auto_save or st.button("Save this remote prediction"):
#                     rec = {
#                         "timestamp": datetime.utcnow().isoformat() + "Z",
#                         "mode": "remote_space",
#                         "space_url": space_url,
#                         "input_text": text,
#                         "response_raw": resp,
#                         "response_parsed": parsed,
#                     }
#                     try:
#                         append_json_record(RESULTS_FPATH, rec)
#                         st.success(f"Saved result to {RESULTS_FPATH.name}")
#                     except Exception as e:
#                         st.error(f"Save failed: {e}")

#             except Exception as e:
#                 st.error("Prediction failed")
#                 st.exception(e)

# # -------------------------
# # Local HF model (transformers)
# # -------------------------
# else:
#     st.header("Local model — Hugging Face transformers")
#     st.markdown("Load tokenizer + model locally and run a forward pass. Provide HF repo id or local path.")
#     model_repo = st.text_input("Model repo or path", value=os.getenv("HF_MODEL", "climatebert/econbert"))
#     use_fast = st.checkbox("Use fast tokenizer", value=True)
#     max_len = st.slider("Max tokens", min_value=32, max_value=2048, value=512, step=32)
#     text = st.text_area("Input text", "The Federal Reserve increased interest rates by 25 basis points.", height=200)

#     col1, col2 = st.columns([2, 1])
#     with col1:
#         load_btn = st.button("Load tokenizer & model")
#         run_btn = st.button("Run tokenizer + model")
#     with col2:
#         clear_cache = st.button("Clear cached model")

#     if clear_cache:
#         try:
#             st.cache_resource.clear()
#             st.success("Cleared cached resources")
#         except Exception as e:
#             st.error(f"Clear cache failed: {e}")

#     @st.cache_resource(show_spinner=False)
#     def _load_transformers(repo: str, use_fast_tok: bool, token: str | None):
#         try:
#             from transformers import AutoTokenizer, AutoModel
#         except Exception as e:
#             raise RuntimeError(f"transformers not installed: {e}")
#         kwargs = {}
#         if token:
#             kwargs["use_auth_token"] = token
#         tokenizer = AutoTokenizer.from_pretrained(repo, use_fast=use_fast_tok, **kwargs)
#         model = AutoModel.from_pretrained(repo, **kwargs)
#         return tokenizer, model

#     tokenizer = None
#     model = None
#     if load_btn:
#         try:
#             st.info(f"Loading {model_repo} … this may take time and disk space.")
#             tokenizer, model = _load_transformers(model_repo, use_fast, hf_token or None)
#             st.success("Model & tokenizer loaded")
#             st.write("Tokenizer:", type(tokenizer).__name__, "Model:", type(model).__name__)
#         except Exception as e:
#             st.error("Load failed")
#             st.exception(e)
#     else:
#         # try reuse cached resources
#         try:
#             tokenizer, model = _load_transformers(model_repo, use_fast, hf_token or None)
#         except Exception:
#             tokenizer = None
#             model = None

#     if tokenizer is None or model is None:
#         st.warning("Tokenizer / model not loaded. Click 'Load tokenizer & model' to initialize.")
#     else:
#         st.markdown("### Tokenizer / inputs")
#         if st.button("Show tokenization only"):
#             try:
#                 inputs = tokenizer(text, truncation=True, max_length=max_len)
#                 token_ids = inputs.get("input_ids", [])
#                 tokens = tokenizer.convert_ids_to_tokens(token_ids)
#                 st.write({"tokens_count": len(tokens)})
#                 st.write(tokens[:200])
#             except Exception as e:
#                 st.exception(e)

#         if run_btn:
#             try:
#                 import torch
#                 inputs = tokenizer(
#                     text,
#                     return_tensors="pt",
#                     truncation=True,
#                     max_length=max_len,
#                     padding="longest",
#                 )
#                 st.write("Input IDs shape:", inputs["input_ids"].shape)
#                 tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].tolist())
#                 st.write("Tokens (first 200):", tokens[:200])

#                 with st.spinner("Running model forward…"):
#                     model.eval()
#                     with torch.no_grad():
#                         outputs = model(**inputs)
#                 # Handle common outputs
#                 last_hidden = getattr(outputs, "last_hidden_state", None)
#                 pooled = getattr(outputs, "pooler_output", None)
#                 st.subheader("Model outputs")
#                 if last_hidden is not None:
#                     st.write("last_hidden_state shape:", tuple(last_hidden.shape))
#                 else:
#                     st.write("Raw outputs:")
#                     st.write(outputs)

#                 if pooled is None and last_hidden is not None:
#                     emb = last_hidden.mean(dim=1)
#                     arr = emb.detach().cpu().numpy().tolist()
#                     st.write("Pooled embedding (mean) shape:", tuple(emb.shape))
#                 elif pooled is not None:
#                     arr = pooled.detach().cpu().numpy().tolist()
#                     st.write("Pooler output shape:", tuple(pooled.shape))
#                 else:
#                     arr = None

#                 if arr is not None:
#                     # show brief preview and allow download
#                     st.write("Embedding (first 3 dims):", [row[:3] for row in arr])
#                     b = io.BytesIO(json.dumps(arr, ensure_ascii=False).encode("utf-8"))
#                     st.download_button("Download embedding (JSON)", b, file_name="embedding.json", mime="application/json")

#                     # --- save local run results (new) ---
#                     if auto_save or st.button("Save this local run"):
#                         rec = {
#                             "timestamp": datetime.utcnow().isoformat() + "Z",
#                             "mode": "local_model",
#                             "model_repo": model_repo,
#                             "input_text": text,
#                             "embedding_shape": (len(arr), len(arr[0])) if arr else None,
#                             "embedding_preview": [row[:3] for row in arr],
#                         }
#                         try:
#                             append_json_record(RESULTS_FPATH, rec)
#                             st.success(f"Saved result to {RESULTS_FPATH.name}")
#                         except Exception as e:
#                             st.error(f"Save failed: {e}")
#             except Exception as e:
#                 st.error("Model run failed")
#                 st.exception(e)

# st.markdown("---")
# st.caption("Use Remote Space mode to call the hosted ClimateBERT demo (gradio). Use Local HF model mode to load and run a HF model locally. Ensure dependencies: gradio-client and/or transformers + torch installed in the environment.")

# # Add a short sidebar / footer control to download or view stored results
# if RESULTS_FPATH.exists():
#     with st.sidebar.expander("Stored results"):
#         st.write(f"Records: {len(json.loads(RESULTS_FPATH.read_text(encoding='utf-8')))}")
#         if st.button("Download stored results"):
#             st.download_button("Download results JSON", RESULTS_FPATH.read_bytes(), file_name=RESULTS_FPATH.name, mime="application/json")