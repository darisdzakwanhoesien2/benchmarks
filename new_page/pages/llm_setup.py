"""
Streamlit page wrapper for the OpenRouter ESG extractor.
"""
import os
import re
import time
import json
import socket
from typing import List, Dict, Any, Optional
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urlparse

import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────
OPENROUTER_API_URL    = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODELS_PATH = os.getenv("OPENROUTER_MODELS_URL", "https://openrouter.ai/api/v1/models")
DEFAULT_MODEL         = "gpt-4o-mini"
FREE_MODELS = [
    "stepfun/step-3.5-flash:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompt" / "data.md"
API_KEY_ENV          = "OPENROUTER_API_KEY"
MODELS_CACHE         = Path(__file__).parent / "models_cache.json"
OCR_OUTPUT_DIR       = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"


# ── Core helpers ──────────────────────────────────────────────────────────────
def _load_prompt_template() -> str:
    if PROMPT_TEMPLATE_PATH.exists():
        return PROMPT_TEMPLATE_PATH.read_text(encoding="utf8")
    return (
        "You are an ESG text analysis expert.\n\n"
        "For each meaningful sentence or segment in the text:\n"
        "Output JSON list of {text, labels, esg, sentiment}.\n\n"
        "Now analyze the following text:\n\n{{INPUT_TEXT}}"
    )


def _extract_first_json(text: str) -> Optional[str]:
    m = re.search(r"```json\s*(\{[\s\S]*?\}|\[[\s\S]*?\])\s*```", text, re.IGNORECASE)
    if m:
        return m.group(1)
    m2 = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if m2:
        return m2.group(1)
    return None


def _requests_session_with_retries(retries: int = 3, backoff_factor: float = 0.6) -> requests.Session:
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff_factor,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=["POST", "GET"])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://",  HTTPAdapter(max_retries=retry))
    return s


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


def generate_esg_structured(
    input_text: str,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    max_tokens: int = 1500,
    timeout: int = 60,
    retries: int = 3,
) -> List[Dict[str, Any]]:
    if not api_key:
        api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"OpenRouter API key required in env {API_KEY_ENV} or passed via api_key")

    prompt = _load_prompt_template().replace("{{INPUT_TEXT}}", input_text)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
            {"role": "user",   "content": prompt},
        ],
        "temperature": float(temperature),
        "max_tokens":  int(max_tokens),
    }

    s       = _requests_session_with_retries(retries=retries)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last_exc = None

    for attempt in range(1, retries + 1):
        try:
            resp = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data    = resp.json()
            content = None
            if isinstance(data, dict):
                choices = data.get("choices") or data.get("output") or []
                if choices and isinstance(choices, list):
                    first = choices[0]
                    if isinstance(first, dict):
                        msg = first.get("message") or first.get("delta") or first.get("content")
                        if isinstance(msg, dict):
                            content = msg.get("content") or msg.get("text") or None
                        else:
                            content = first.get("content") or first.get("text") or None
                    elif isinstance(first, str):
                        content = first
                if content is None:
                    content = data.get("response") or data.get("text") or None
            if content is None:
                content = resp.text

            parsed = parse_json_from_model(content)
            if not isinstance(parsed, list):
                parsed = [parsed] if isinstance(parsed, dict) else parsed
            return parsed
        except Exception as e:
            last_exc = e
            time.sleep(min(10, 2 ** attempt))

    raise RuntimeError(f"OpenRouter request failed after {retries} attempts: {last_exc}")


# ── Model fetcher + cache ─────────────────────────────────────────────────────
def _models_cache_age_seconds() -> float:
    try:
        return time.time() - MODELS_CACHE.stat().st_mtime
    except Exception:
        return float("inf")


def fetch_openrouter_models(api_key: Optional[str] = None, cache_seconds: int = 3600) -> List[str]:
    if MODELS_CACHE.exists() and _models_cache_age_seconds() < cache_seconds:
        try:
            cached = json.loads(MODELS_CACHE.read_text(encoding="utf-8"))
            if isinstance(cached, list):
                return cached
        except Exception:
            pass

    s       = _requests_session_with_retries()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    resp    = s.get(OPENROUTER_MODELS_PATH, headers=headers, timeout=10)
    resp.raise_for_status()
    data    = resp.json()

    models_list: List[str] = []
    candidates = data if isinstance(data, list) else (
        data.get("models") or data.get("data") or data.get("result") or []
    )
    for item in candidates:
        if isinstance(item, dict):
            models_list.append(item.get("id") or item.get("name") or item.get("model") or str(item))
        else:
            models_list.append(str(item))

    models_list = [m for m in models_list if m] or [DEFAULT_MODEL]
    try:
        MODELS_CACHE.write_text(json.dumps(models_list, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return models_list


# ── Immediate-save helper ─────────────────────────────────────────────────────
def append_record(record: dict, fname: Path) -> None:
    """Append one record to fname immediately using an atomic tmp → replace write."""
    existing: list = []
    if fname.exists():
        try:
            with fname.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            existing = loaded if isinstance(loaded, list) else [loaded]
        except Exception:
            existing = []

    existing.append(record)
    tmp = fname.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    tmp.replace(fname)  # atomic replace — safe even if interrupted


# ── Streamlit UI ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="ESG LLM Extractor (OpenRouter)", layout="wide")
st.title("ESG Structured Extraction (OpenRouter)")

if "openrouter_key" not in st.session_state:
    st.session_state.openrouter_key = os.getenv(API_KEY_ENV, "")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Connection")
    api_key_input = st.text_input(
        "OpenRouter API Key", value=st.session_state.openrouter_key, type="password"
    )
    if api_key_input:
        st.session_state.openrouter_key = api_key_input.strip()

    endpoint_input      = st.text_input("API URL override", value=OPENROUTER_API_URL)
    models_base_override = st.text_input("Models endpoint override", value=OPENROUTER_MODELS_PATH)
    use_mock            = st.checkbox("Use mock responses (offline)", value=False)

    if st.button("Run connectivity check"):
        try:
            host = urlparse(endpoint_input).hostname or endpoint_input
            addr = socket.getaddrinfo(host, 443)
            st.success(f"DNS OK: {', '.join({ai[4][0] for ai in addr})}")
        except Exception as e:
            st.error(f"Connectivity/DNS issue: {e}")
    st.markdown("---")

# ── Input source ──────────────────────────────────────────────────────────────
input_mode = st.radio("Input source", ["Manual text", "OCR output file"], horizontal=True)

texts_to_process: list[dict] = []   # {"label": str, "text": str}

if input_mode == "Manual text":
    manual_text = st.text_area("Input text to analyze", height=240)
    if manual_text.strip():
        texts_to_process = [{"label": "manual_input", "text": manual_text.strip()}]

else:
    # ── Discover documents ────────────────────────────────────────────────────
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
                    {"label": f"{selected_doc}/{pf.name}", "text": pf.read_text(encoding="utf-8").strip()}
                    for pf in chosen_pages
                    if pf.read_text(encoding="utf-8").strip()
                ]

# ── Advanced settings ─────────────────────────────────────────────────────────
with st.expander("Advanced settings", expanded=False):
    refresh_models = st.button("Refresh model list")
    api_for_models = api_key_input.strip() if api_key_input else st.session_state.openrouter_key or None
    if models_base_override:
        OPENROUTER_MODELS_PATH = models_base_override

    try:
        models = fetch_openrouter_models(
            api_key=api_for_models, cache_seconds=0 if refresh_models else 3600
        )
    except Exception as e:
        st.warning(f"Could not fetch models: {e}")
        models = [DEFAULT_MODEL]

    include_curated_free = st.checkbox("Include curated free models", value=False)
    free_only            = st.checkbox("Show only ':free' models",     value=False)

    merged, seen = [], set()
    for m in models:
        if m not in seen:
            merged.append(m); seen.add(m)
    if include_curated_free:
        for m in FREE_MODELS:
            if m not in seen:
                merged.append(m); seen.add(m)

    final_models = ([m for m in merged if ":free" in m] or FREE_MODELS.copy()) if free_only else merged

    default_choice = DEFAULT_MODEL if DEFAULT_MODEL in final_models else final_models[0]
    model_inputs   = st.multiselect("Models (select one or more)", final_models, default=[default_choice])
    if not model_inputs:
        st.warning(f"No models selected — defaulting to {default_choice}")
        model_inputs = [default_choice]

    temperature_input = st.slider("Temperature",  min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    max_tokens_input  = st.number_input("Max tokens", value=1500, min_value=64, step=1)
    retries_input     = st.number_input("Retries",    value=3,    min_value=0,  step=1)

    save_key_session = st.checkbox("Save API key to session (not disk)", value=False)
    if save_key_session and api_key_input:
        st.session_state[API_KEY_ENV] = api_key_input.strip()
        os.environ[API_KEY_ENV]       = api_key_input.strip()

# ── Save option ───────────────────────────────────────────────────────────────
save_results = st.checkbox(
    "Save each result immediately to results/esg_records.json", value=True
)

# ── Run ───────────────────────────────────────────────────────────────────────
if st.button("Generate structured ESG JSON"):
    if not texts_to_process:
        st.warning("No text to process. Enter text or select at least one page.")
    else:
        api_key_to_use = (
            api_key_input.strip()
            or st.session_state.get(API_KEY_ENV)
            or os.getenv(API_KEY_ENV)
        )

        if not use_mock and not api_key_to_use:
            st.error("OpenRouter API key not provided. Set it in the sidebar or env OPENROUTER_API_KEY.")
        else:
            results_dir = Path(__file__).resolve().parents[1] / "results"
            results_dir.mkdir(parents=True, exist_ok=True)
            fname = results_dir / "esg_records.json"

            total    = len(texts_to_process) * len(model_inputs)
            step     = 0
            progress = st.progress(0)
            status   = st.empty()
            all_run_records: list = []

            for item in texts_to_process:
                for model in model_inputs:
                    step += 1
                    status.info(
                        f"⏳ [{step}/{total}] `{item['label']}` — `{model}`"
                    )

                    if use_mock:
                        parsed  = [{"text": item["text"][:200], "esg": [],
                                    "labels": [], "sentiment": "neutral", "note": "mock"}]
                        ok, err = True, None
                    else:
                        try:
                            parsed  = generate_esg_structured(
                                item["text"],
                                api_key    = api_key_to_use,
                                model      = model,
                                temperature= temperature_input,
                                max_tokens = int(max_tokens_input),
                                retries    = int(retries_input),
                            )
                            ok, err = True, None
                        except Exception as e:
                            parsed  = []
                            ok, err = False, str(e)

                    # ── Build record ──────────────────────────────────────────
                    record = {
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "source":    item["label"],
                        "model":     model,
                        "input":     item["text"],
                        "ok":        ok,
                        "records":   parsed,
                        **({"error": err} if err else {}),
                    }
                    all_run_records.append(record)

                    # ── Show inline result ────────────────────────────────────
                    if ok:
                        with st.expander(
                            f"✅ `{item['label']}` × `{model}` — {len(parsed)} record(s)"
                        ):
                            st.json(parsed)
                    else:
                        st.error(f"❌ `{item['label']}` × `{model}`: {err}")

                    # ── Save immediately ──────────────────────────────────────
                    if save_results and ok:
                        try:
                            append_record(record, fname)
                            st.toast(f"💾 Saved `{item['label']}` / `{model}`")
                        except Exception as save_err:
                            st.warning(f"Save failed for `{item['label']}`: {save_err}")

                    progress.progress(step / total)

            # ── Final summary ─────────────────────────────────────────────────
            progress.empty()
            status.empty()

            ok_count  = sum(1 for r in all_run_records if r.get("ok"))
            err_count = len(all_run_records) - ok_count
            st.success(f"✅ {ok_count} succeeded — {err_count} failed — {len(all_run_records)} total")

            st.download_button(
                "⬇️ Download all results from this run (JSON)",
                json.dumps(all_run_records, ensure_ascii=False, indent=2),
                file_name=f"esg_results_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json",
                mime="application/json",
            )