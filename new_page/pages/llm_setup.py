"""
Streamlit page wrapper for the OpenRouter ESG extractor.

Drop this file into a Streamlit `pages/` folder (already located there) and run:
  streamlit run path/to/your/app

This file preserves the OpenRouter helper functions and exposes a Streamlit UI:
- fetch model list from https://openrouter.ai/api/v1/models (cached)
- run structured ESG extraction via generate_esg_structured(...)
- save/download results
- optional mock mode for offline testing
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

# Config
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_MODELS_PATH = os.getenv("OPENROUTER_MODELS_URL", "https://openrouter.ai/api/v1/models")
DEFAULT_MODEL = "gpt-4o-mini"
# curated free models (can be expanded)
FREE_MODELS = [
    "stepfun/step-3.5-flash:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
]
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompt" / "data.md"
API_KEY_ENV = "OPENROUTER_API_KEY"
MODELS_CACHE = Path(__file__).parent / "models_cache.json"


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
    s.mount("http://", HTTPAdapter(max_retries=retry))
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

    prompt_template = _load_prompt_template()
    prompt = prompt_template.replace("{{INPUT_TEXT}}", input_text)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }

    s = _requests_session_with_retries(retries=retries)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
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
                if isinstance(parsed, dict):
                    parsed = [parsed]
            return parsed
        except Exception as e:
            last_exc = e
            wait = min(10, 2 ** attempt)
            time.sleep(wait)
            continue

    raise RuntimeError(f"OpenRouter request failed after {retries} attempts: {last_exc}")


# Model fetcher + cache
def _models_cache_age_seconds() -> float:
    try:
        return time.time() - MODELS_CACHE.stat().st_mtime
    except Exception:
        return float("inf")


def fetch_openrouter_models(api_key: Optional[str] = None, cache_seconds: int = 3600) -> List[str]:
    # determine base models URL
    url = OPENROUTER_MODELS_PATH
    # use cache when fresh
    if MODELS_CACHE.exists() and _models_cache_age_seconds() < cache_seconds:
        try:
            cached = json.loads(MODELS_CACHE.read_text(encoding="utf-8"))
            if isinstance(cached, list):
                return cached
        except Exception:
            pass

    s = _requests_session_with_retries()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    resp = s.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    models_list: List[str] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                models_list.append(item.get("id") or item.get("name") or item.get("model") or str(item))
            else:
                models_list.append(str(item))
    elif isinstance(data, dict):
        candidates = data.get("models") or data.get("data") or data.get("result") or []
        if isinstance(candidates, list) and candidates:
            for item in candidates:
                if isinstance(item, dict):
                    models_list.append(item.get("id") or item.get("name") or item.get("model") or str(item))
                else:
                    models_list.append(str(item))
    models_list = [m for m in models_list if m]
    if not models_list:
        models_list = [DEFAULT_MODEL]
    try:
        MODELS_CACHE.write_text(json.dumps(models_list, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return models_list


# Streamlit UI
st.set_page_config(page_title="ESG LLM Extractor (OpenRouter)", layout="wide")
st.title("ESG Structured Extraction (OpenRouter)")

# store/load API key in session state optionally
if "openrouter_key" not in st.session_state:
    st.session_state.openrouter_key = os.getenv(API_KEY_ENV, "")

with st.sidebar:
    st.header("Connection")
    api_key_input = st.text_input("OpenRouter API Key", value=st.session_state.openrouter_key, type="password")
    if api_key_input:
        st.session_state.openrouter_key = api_key_input.strip()
    endpoint_input = st.text_input("API URL override", value=os.getenv("OPENROUTER_API_URL", OPENROUTER_API_URL))
    models_base_override = st.text_input("Models endpoint override", value=os.getenv("OPENROUTER_MODELS_URL", OPENROUTER_MODELS_PATH))
    use_mock = st.checkbox("Use mock responses (offline)", value=False)
    if st.button("Run connectivity check"):
        try:
            host = urlparse(endpoint_input).hostname or endpoint_input
            addr = socket.getaddrinfo(host, 443)
            st.success(f"DNS OK: {', '.join({ai[4][0] for ai in addr})}")
        except Exception as e:
            st.error(f"Connectivity/DNS issue: {e}")
    st.markdown("---")

# Main UI
input_text = st.text_area("Input text to analyze", height=240)

with st.expander("Advanced settings", expanded=False):
    st.write("Model selection")
    refresh_models = st.button("Refresh model list")
    # determine API key to fetch models (prefer explicit)
    api_for_models = api_key_input.strip() if api_key_input else st.session_state.openrouter_key or None
    # allow override of models endpoint
    if models_base_override:
        OPENROUTER_MODELS_PATH = models_base_override  # local override used by fetcher

    try:
        # when user requests refresh, bypass cache
        if refresh_models:
            models = fetch_openrouter_models(api_key=api_for_models, cache_seconds=0)
        else:
            models = fetch_openrouter_models(api_key=api_for_models)
    except Exception as e:
        st.warning(f"Could not fetch models: {e}")
        models = [DEFAULT_MODEL]

    # free models filtering / inclusion UI
    include_curated_free = st.checkbox("Include curated free models", value=False, help="Add curated list of known free models")
    free_only = st.checkbox("Show only ':free' models", value=False, help="Filter models to entries containing ':free'")

    # merge / filter models list based on options
    merged_models = []
    seen = set()
    # start with fetched models
    for m in models:
        if m not in seen:
            merged_models.append(m)
            seen.add(m)
    # optionally add curated free models
    if include_curated_free:
        for m in FREE_MODELS:
            if m not in seen:
                merged_models.append(m)
                seen.add(m)

    if free_only:
        filtered = [m for m in merged_models if ":free" in m]
        # fallback to curated free models if filter returns empty
        if not filtered:
            filtered = FREE_MODELS.copy()
        final_models = filtered
    else:
        final_models = merged_models

    if final_models:
        # allow selecting multiple models; default to DEFAULT_MODEL if present
        default_choice = DEFAULT_MODEL if DEFAULT_MODEL in final_models else final_models[0]
        model_inputs = st.multiselect(
            "Models (select one or more)",
            options=final_models,
            default=[default_choice],
            help="Choose one or more models to run the analysis with."
        )
        if not model_inputs:
            # ensure at least one model is selected
            st.warning(f"No models selected — defaulting to {default_choice}")
            model_inputs = [default_choice]
    else:
        model_inputs = [st.text_input("Model", value=DEFAULT_MODEL)]


    temperature_input = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    max_tokens_input = st.number_input("Max tokens", value=1500, min_value=64, step=1)
    retries_input = st.number_input("Retries", value=3, min_value=0, step=1)
    save_key_session = st.checkbox("Save API key to session (not disk)", value=False)
    if save_key_session and api_key_input:
        st.session_state[API_KEY_ENV] = api_key_input.strip()
        os.environ[API_KEY_ENV] = api_key_input.strip()

run_button = st.button("Generate structured ESG JSON")

if run_button:
    if not input_text.strip():
        st.warning("Enter text to analyze.")
    else:
        api_key_to_use = (
            api_key_input.strip()
            if api_key_input and api_key_input.strip()
            else st.session_state.get(API_KEY_ENV)
            if API_KEY_ENV in st.session_state
            else os.getenv(API_KEY_ENV)
        )

        if use_mock:
            # simple mock response
            assistant_text = f"(mock) Echo: {input_text[:200]}"
            parsed = [{"text": input_text, "esg": [], "labels": [], "sentiment": "neutral", "note": assistant_text}]
            st.success(f"Parsed {len(parsed)} mock record(s)")
            st.json(parsed)
        else:
            if not api_key_to_use:
                st.error("OpenRouter API key not provided. Set it in sidebar or env OPENROUTER_API_KEY.")
            else:
                try:
                    with st.spinner("Contacting OpenRouter and parsing results..."):
                        # run the analysis for each selected model and collect results
                        all_results = {}
                        for model in model_inputs:
                            try:
                                recs = generate_esg_structured(
                                    input_text,
                                    api_key=api_key_to_use,
                                    model=model,
                                    temperature=temperature_input,
                                    max_tokens=int(max_tokens_input),
                                    retries=int(retries_input),
                                )
                                all_results[model] = {"ok": True, "count": len(recs), "records": recs}
                            except Exception as me:
                                all_results[model] = {"ok": False, "error": str(me), "records": []}

                    # show results per model
                    total_parsed = sum(v.get("count", 0) for v in all_results.values() if v.get("ok"))
                    st.success(f"Parsed {total_parsed} record(s) across {len(all_results)} model(s)")
                    for model, info in all_results.items():
                        with st.expander(f"Model: {model} — {'OK' if info.get('ok') else 'ERROR'}"):
                            if info.get("ok"):
                                st.write(f"Records: {info.get('count')}")
                                st.json(info.get("records"))
                            else:
                                st.error(f"Error for model {model}: {info.get('error')}")

                    # save combined results (append) with per-model entries
                    save_results = st.checkbox("Save results to results/esg_records.json (append)", value=True)
                    if save_results:
                        base_dir = Path(__file__).resolve().parents[1]
                        results_dir = base_dir / "results"
                        results_dir.mkdir(parents=True, exist_ok=True)
                        fname = results_dir / "esg_records.json"

                        existing = []
                        if fname.exists():
                            try:
                                with fname.open("r", encoding="utf-8") as f:
                                    loaded = json.load(f)
                                if isinstance(loaded, list):
                                    existing = loaded
                            except Exception:
                                existing = []

                        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        to_append = {"timestamp": timestamp, "models": all_results}
                        existing.append(to_append)
                        with fname.open("w", encoding="utf-8") as f:
                            json.dump(existing, f, ensure_ascii=False, indent=2)

                        st.success(f"Appended results for {len(all_results)} model(s) to {fname}")
                        st.download_button(
                            "Download combined results (JSON)",
                            json.dumps(to_append, ensure_ascii=False, indent=2),
                            file_name=f"esg_models_results_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json",
                            mime="application/json",
                        )

                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    traceback.print_exc()