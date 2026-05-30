import streamlit as st
import requests
import json
from pathlib import Path
from datetime import datetime
import os
import time
import socket
from requests.exceptions import RequestException
from urllib.parse import urlparse

STORE_PATH = Path(__file__).resolve().parents[1] / "chat_history.json"  # stores JSON in benchmarks/new_page
OPENROUTER_DEFAULT_URL = os.getenv("OPENROUTER_API_URL", "https://api.openrouter.ai/v1/chat/completions")

def init_store():
    if not STORE_PATH.exists():
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORE_PATH.write_text("[]", encoding="utf-8")

def save_message(role: str, content: str, model: str | None = None):
    init_store()
    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = []
    entry = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "ts": datetime.utcnow().isoformat(),
        "role": role,
        "content": content,
        "model": model,
    }
    data.append(entry)
    STORE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_history(limit: int = 100):
    init_store()
    try:
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    # return last `limit` messages in chronological order
    return data[-limit:] if len(data) > 0 else []

def clear_store():
    init_store()
    STORE_PATH.write_text("[]", encoding="utf-8")

def diagnose_endpoint(url: str) -> list[str]:
    """Perform quick DNS/connectivity checks and return human-friendly lines."""
    out = []
    try:
        p = urlparse(url)
        host = p.hostname or url
        out.append(f"Endpoint: {url}")
        out.append(f"Resolved host: {host}")
        try:
            addrinfo = socket.getaddrinfo(host, p.port or 443)
            addrs = sorted({ai[4][0] for ai in addrinfo})
            out.append(f"DNS resolution OK — addresses: {', '.join(addrs)}")
        except socket.gaierror as ge:
            out.append(f"DNS resolution failed: {ge}")
        # quick HTTP HEAD/GET test (respect proxies in env)
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            out.append(f"HTTP HEAD status: {r.status_code}")
        except Exception as e:
            out.append(f"HTTP HEAD failed: {e}")
        # try simple GET for full path if HEAD fails
        return out
    except Exception as e:
        return [f"Diagnosis error: {e}"]

def call_openrouter(api_key: str, model: str, messages: list[dict], endpoint: str | None = None, max_tokens: int = 512, temperature: float = 0.2):
    url = endpoint or OPENROUTER_DEFAULT_URL
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_exc = None
    # simple retry/backoff
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # Typical openrouter return similarly structured to OpenAI: choices[0].message.content
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if content is None:
                # fallback to text or first choice
                content = data.get("choices", [{}])[0].get("text") or str(data)
            return content
        except RequestException as e:
            last_exc = e
            cause = getattr(e, "__cause__", None)
            # if underlying socket error is name resolution, raise with clearer guidance
            if isinstance(cause, socket.gaierror) or "Failed to resolve" in str(e) or "NameResolution" in str(e):
                raise RuntimeError(
                    f"Network/DNS error contacting {url}: {e}. "
                    "Check your internet connection, DNS, firewall, or set OPENROUTER_API_URL to a reachable endpoint."
                ) from e
            # brief backoff then retry
            time.sleep(1 * (attempt + 1))
    raise RuntimeError(f"Failed to call OpenRouter after retries: {last_exc}")

# Streamlit UI
st.set_page_config(page_title="OpenRouter LLM Chat", layout="centered")
st.title("OpenRouter LLM Chat")

init_store()

# add an offline/mock option for local testing when network/API is unavailable
use_mock = st.checkbox("Use mock responses (offline testing)", value=False)

# API key input (optionally persisted in session only)
if "openrouter_key" not in st.session_state:
    st.session_state.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

key = st.text_input("OpenRouter API key", value=st.session_state.openrouter_key, type="password")
if key and key != st.session_state.openrouter_key:
    st.session_state.openrouter_key = key

# Allow overriding the endpoint in the UI (helps when DNS blocked or using a proxy)
if "openrouter_url" not in st.session_state:
    st.session_state.openrouter_url = os.getenv("OPENROUTER_API_URL", OPENROUTER_DEFAULT_URL)
endpoint = st.text_input("OpenRouter API URL (override)", value=st.session_state.openrouter_url, help="Set a reachable endpoint, or leave default.")
if endpoint and endpoint != st.session_state.openrouter_url:
    st.session_state.openrouter_url = endpoint

model = st.text_input("Model (OpenRouter model name)", value="gpt-4o-mini", help="Enter the OpenRouter model identifier you want to use.")

with st.form("chat_form", clear_on_submit=False):
    user_input = st.text_area("Your message", height=120)
    submitted = st.form_submit_button("Send")

diagnose = st.button("Run connectivity diagnostics")

if diagnose:
    st.info("Running quick diagnostics...")
    diag_lines = diagnose_endpoint(st.session_state.openrouter_url)
    for line in diag_lines:
        st.write(line)
    st.write("- To override, set 'OpenRouter API URL (override)' above.")
    st.write("- You can enable 'Use mock responses' to test UI without network.")

if "history" not in st.session_state:
    # history is a list of message dicts: {ts, role, content, model}
    st.session_state.history = get_history(200)

# sending
if submitted and user_input:
    if use_mock:
        assistant_text = f"(mock) Echo: {user_input}"
        st.session_state.history.append({"role": "user", "content": user_input, "ts": datetime.utcnow().isoformat(), "model": model})
        save_message("user", user_input, model)
        st.session_state.history.append({"role": "assistant", "content": assistant_text, "ts": datetime.utcnow().isoformat(), "model": model})
        save_message("assistant", assistant_text, model)
    else:
        if not st.session_state.openrouter_key:
            st.error("Provide your OpenRouter API key above.")
        else:
            # append user message to UI history and JSON store
            st.session_state.history.append({"role": "user", "content": user_input, "ts": datetime.utcnow().isoformat(), "model": model})
            save_message("user", user_input, model)
            try:
                # prepare conversation messages if you want context; here we send only the latest user message
                messages_payload = [{"role": "user", "content": user_input}]
                assistant_text = call_openrouter(st.session_state.openrouter_key, model, messages_payload, endpoint=st.session_state.openrouter_url)
                st.session_state.history.append({"role": "assistant", "content": assistant_text, "ts": datetime.utcnow().isoformat(), "model": model})
                save_message("assistant", assistant_text, model)
            except Exception as e:
                st.error(f"API error: {e}")
                with st.expander("Troubleshooting"):
                    st.write("- Check your internet connection and DNS.")
                    st.write("- If you're behind a proxy or firewall, ensure this process can reach the endpoint.")
                    st.write("- You can set OPENROUTER_API_URL env var or override the endpoint above.")
                    st.write("- Enable 'Use mock responses' to test the UI without network access.")
                    st.write("- Click 'Run connectivity diagnostics' to get DNS/connectivity hints.")

# render chat
for msg in st.session_state.history:
    role = msg.get("role", "user")
    content = msg.get("content", "")
    ts = msg.get("ts", "")
    if role == "assistant":
        st.markdown(f"**Assistant** · {ts}\n\n{content}")
    else:
        st.markdown(f"**You** · {ts}\n\n{content}")

st.markdown("---")
if st.button("Clear history (UI only)"):
    st.session_state.history = []

if st.button("Delete stored messages (JSON)"):
    clear_store()
    st.success("Stored messages deleted.")