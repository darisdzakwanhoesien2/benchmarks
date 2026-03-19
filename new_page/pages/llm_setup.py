"""
OpenRouter client helper to run the ESG prompt and return structured JSON.

Usage:
  export OPENROUTER_API_KEY="sk_..."
  from llm_setup import generate_esg_structured
  records = generate_esg_structured("Your input text here")

This is a lightweight, dependency-only-on-requests implementation.
"""
import os
import re
import time
import json
from typing import List, Dict, Any, Optional
import requests
from pathlib import Path
from requests.adapters import HTTPAdapter, Retry

# Config
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"  # adjust if you have a preferred model name on OpenRouter
PROMPT_TEMPLATE_PATH = Path(__file__).parent / "prompt" / "data.md"
API_KEY_ENV = "OPENROUTER_API_KEY"


def _load_prompt_template() -> str:
    if PROMPT_TEMPLATE_PATH.exists():
        return PROMPT_TEMPLATE_PATH.read_text(encoding="utf8")
    # fallback: small inline prompt if file missing
    return (
        "You are an ESG text analysis expert.\n\n"
        "For each meaningful sentence or segment in the text:\n"
        "Output JSON list of {text, labels, esg, sentiment}.\n\n"
        "Now analyze the following text:\n\n{{INPUT_TEXT}}"
    )


def _extract_first_json(text: str) -> Optional[str]:
    # try to find first JSON code block or first top-level JSON array/object
    # common patterns: ```json ... ``` or just starting with [ or {
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
    return s


def parse_json_from_model(text: str) -> Any:
    """
    Try to parse model output into JSON. Use robust fallbacks.
    """
    # direct parse
    try:
        return json.loads(text)
    except Exception:
        # extract first JSON-like block
        js = _extract_first_json(text)
        if js:
            try:
                return json.loads(js)
            except Exception:
                # last resort: use ast.literal_eval
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
    """
    Send the ESG prompt to OpenRouter and return parsed JSON records (list of dicts).
    Raises on unrecoverable errors.
    """
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
        # "top_p": 1.0,
        # "n": 1,
    }

    s = _requests_session_with_retries(retries=retries)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = s.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            # OpenRouter response shape is like OpenAI chat completions; get assistant content
            # try a few known paths
            content = None
            if isinstance(data, dict):
                # choices -> message -> content
                choices = data.get("choices") or data.get("output") or []
                if choices and isinstance(choices, list):
                    # pick first
                    first = choices[0]
                    # openrouter sometimes: {message: {content: {...}}}
                    if isinstance(first, dict):
                        msg = first.get("message") or first.get("delta") or first.get("content")
                        if isinstance(msg, dict):
                            content = msg.get("content") or msg.get("text") or None
                        else:
                            # first might have 'content' directly
                            content = first.get("content") or first.get("text") or None
                    elif isinstance(first, str):
                        content = first
                # fallback to data.get("data") or data.get("response")
                if content is None:
                    # try common fields
                    content = data.get("response") or data.get("text") or None
            if content is None:
                # fallback: raw text of response
                content = resp.text

            # parse JSON from content
            parsed = parse_json_from_model(content)
            if not isinstance(parsed, list):
                # expected a list of records; if dict, wrap
                if isinstance(parsed, dict):
                    parsed = [parsed]
            return parsed
        except Exception as e:
            last_exc = e
            wait = min(10, 2 ** attempt)
            time.sleep(wait)
            continue

    raise RuntimeError(f"OpenRouter request failed after {retries} attempts: {last_exc}")


# -----------------------
# Streamlit page UI below
# -----------------------
if __name__ == "__main__" or True:
    import streamlit as st

    st.set_page_config(page_title="ESG LLM Extractor", layout="wide")
    st.title("ESG Structured Extraction (OpenRouter)")

    input_text = st.text_area("Input text to analyze", height=240)

    with st.expander("Advanced settings", expanded=False):
        api_key_input = st.text_input("OpenRouter API Key (optional — set env OPENROUTER_API_KEY otherwise)", type="password")
        model_input = st.text_input("Model", value=DEFAULT_MODEL)
        temperature_input = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
        max_tokens_input = st.number_input("Max tokens", value=1500, min_value=64, step=1)
        retries_input = st.number_input("Retries", value=3, min_value=0, step=1)

        # new: option to save the API key for this Streamlit session (not written to disk)
        save_key_session = st.checkbox("Save API key for this session (process env)", value=False)
        if api_key_input and save_key_session:
            # store in process env and session_state so subsequent runs use it
            os.environ[API_KEY_ENV] = api_key_input.strip()
            st.session_state[API_KEY_ENV] = api_key_input.strip()
            st.success("API key stored for this session (not saved to disk).")

    run_button = st.button("Generate structured ESG JSON")

    if run_button:
        if not input_text.strip():
            st.warning("Enter text to analyze.")
        else:
            # prefer explicit input, then session_state, then environment variable
            api_key_to_use = (
                api_key_input.strip()
                if api_key_input and api_key_input.strip()
                else st.session_state.get(API_KEY_ENV)
                if API_KEY_ENV in st.session_state
                else os.getenv(API_KEY_ENV)
            )

            if not api_key_to_use:
                st.error("OpenRouter API key not provided. Set it in Advanced settings, save for session, or set env OPENROUTER_API_KEY.")
            else:
                try:
                    with st.spinner("Contacting OpenRouter and parsing results..."):
                        records = generate_esg_structured(
                            input_text,
                            api_key=api_key_to_use,
                            model=model_input,
                            temperature=temperature_input,
                            max_tokens=int(max_tokens_input),
                            retries=int(retries_input),
                        )
                    st.success(f"Parsed {len(records)} record(s)")
                    st.json(records)

                    # Save option
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
                                elif isinstance(loaded, dict):
                                    existing = [loaded]
                            except Exception:
                                existing = []

                        # append and save
                        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        to_append = {"timestamp": timestamp, "model": model_input, "records": records}
                        existing.append(to_append)
                        with fname.open("w", encoding="utf-8") as f:
                            json.dump(existing, f, ensure_ascii=False, indent=2)

                        st.success(f"Appended {len(records)} records to {fname}")
                        st.download_button(
                            "Download last results (JSON)",
                            json.dumps(to_append, ensure_ascii=False, indent=2),
                            file_name=f"esg_records_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json",
                            mime="application/json",
                        )

                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    traceback.print_exc()