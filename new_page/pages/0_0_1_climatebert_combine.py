# https://huggingface.co/spaces/darisdzakwanhoesien/climatebert-multi-model-demo-docker-new

import os
import io
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="ClimateBERT · Combined Demo", page_icon="🌡️", layout="wide")
st.title("🌡️ ClimateBERT — Combined (Remote Space & Local HF Model)")

# --- results storage setup (new) ---
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_FPATH = RESULTS_DIR / "climatebert_results.json"

def _json_default(o):
    try:
        import numpy as _np
        if isinstance(o, _np.ndarray):
            return o.tolist()
        if isinstance(o, (_np.integer, _np.floating)):
            return float(o)
    except Exception:
        pass
    try:
        import torch as _torch
        if isinstance(o, _torch.Tensor):
            return o.cpu().detach().numpy().tolist()
    except Exception:
        pass
    if isinstance(o, (Path,)):
        return str(o)
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)

def append_json_record(path: Path, record: dict) -> None:
    existing = []
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            existing = loaded if isinstance(loaded, list) else [loaded]
        except Exception:
            existing = []
    existing.append(record)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2, default=_json_default)
    tmp.replace(path)

# --- New: improved parser for `response_raw` from ClimateBERT space ----
import re
def parse_response_raw(raw: str) -> dict:
    """
    Parse the text blob returned by /predict_all_models into structured JSON.
    Expected format (examples):
      ### model-name
      ❌ Error: ...
      ### model2
      • label: 0.92
      • other: 0.08

    Returns:
      {"raw": raw, "models": [ {"name": str, "status": "ok"|"error", "error": str|null, "scores": {label: value}} , ... ] }
    """
    if raw is None:
        return {"raw": raw, "models": []}
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
    lines = [ln.strip() for ln in text.splitlines()]
    models = []
    cur = None

    bullet_re = re.compile(r"^[•\-\*\u2022]\s*(.+)$")
    label_val_re = re.compile(r"^(.+?)\s*[:\-]\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")
    # fallback for lines like "• Not about renewables: 1.00" (label contains spaces)
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("###"):
            # new model header
            name = ln[3:].strip()
            if cur is not None:
                models.append(cur)
            cur = {"name": name, "status": "ok", "error": None, "scores": {}}
            continue
        if cur is None:
            # preamble / stray lines -> skip or collect under intro model
            continue
        # detect explicit error marker
        if "❌" in ln or ln.lower().startswith("error:") or "unrecognized model" in ln.lower():
            # collect error message (rest of line)
            msg = ln.replace("❌", "").strip()
            if msg.lower().startswith("error:"):
                msg = msg[6:].strip()
            # append to error field (concatenate if multiple lines)
            if cur.get("error"):
                cur["error"] += " | " + msg
            else:
                cur["error"] = msg
            cur["status"] = "error"
            continue
        # bullets
        m = bullet_re.match(ln)
        candidate = ln
        if m:
            candidate = m.group(1).strip()
        # try label:value numeric
        m2 = label_val_re.match(candidate)
        if m2:
            key = m2.group(1).strip()
            try:
                val = float(m2.group(2))
            except Exception:
                val = m2.group(2)
            cur["scores"][key] = val
            continue
        # lines like "• no: 0.99" handled above; fallback: lines "• key value"
        # attempt split on last space and parse numeric tail
        if m:
            parts = candidate.rsplit(" ", 1)
            if len(parts) == 2:
                key, tail = parts[0].strip(), parts[1].strip()
                try:
                    val = float(tail)
                    cur["scores"][key] = val
                    continue
                except Exception:
                    pass
        # if we reach here, treat line as free-text message (append to error or store under misc)
        if "note" not in cur:
            cur["note"] = ln
        else:
            cur["note"] += " | " + ln

    if cur is not None:
        models.append(cur)

    return {"raw": text, "models": models}

# -------------------------
# Sidebar / options
# -------------------------
st.sidebar.header("Mode")
mode = st.sidebar.selectbox("Run mode", ["Remote Space (gradio)", "Local HF model (transformers)"])

# Common inputs
hf_token_input = st.sidebar.text_input("HF token (optional)", value=os.getenv("HF_TOKEN", ""), type="password")
use_env_token = st.sidebar.checkbox("Use HF_TOKEN from env if input empty", value=True)

if use_env_token and not hf_token_input:
    hf_token = os.getenv("HF_TOKEN", "") or None
else:
    hf_token = hf_token_input or None

# --- results auto-save toggle (added) ---
auto_save = st.sidebar.checkbox("Auto-save predictions to results/climatebert_results.json", value=True)
st.sidebar.markdown(f"Results file: `{RESULTS_FPATH}`")

# -------------------------
# Remote Space (gradio_client)
# -------------------------
if mode == "Remote Space (gradio)":
    st.header("Remote Space — call /predict_all_models")
    space_url = st.text_input(
        "Space URL",
        value=os.getenv("CLIMATEBERT_SPACE_URL", "https://darisdzakwanhoesien-climatebert-multi-model-demo-8aae81e.hf.space/"),
        help="HF Space URL (leave default for demo)"
    )
    text = st.text_area("Input text", "Hello world — ESG / climate example", height=200)
    timeout = st.number_input("Timeout (seconds)", value=120, min_value=10, max_value=600, step=10)

    col1, col2 = st.columns([3, 1])
    with col1:
        predict_btn = st.button("Predict (all models)")
    with col2:
        st.markdown("Connection test")
        test_btn = st.button("Test connect")

    def call_space_predict(url: str, txt: str, token: str | None, timeout_sec: int):
        try:
            from gradio_client import Client
        except Exception as e:
            raise RuntimeError(f"gradio-client not installed: {e}")
        kwargs = {}
        if token:
            kwargs["hf_token"] = token
        # instantiate client (do not pass timeout here — gradio_client.Client may not accept it)
        client = Client(url, **kwargs)
        # call using named parameter to match space input
        return client.predict(text=txt, api_name="/predict_all_models")

    if test_btn:
        try:
            st.info("Testing connection…")
            # a lightweight call: instantiate client and optionally call a health endpoint by predict empty text
            from gradio_client import Client  # might raise
            kwargs = {}
            if hf_token:
                kwargs["hf_token"] = hf_token
            # instantiate client (no timeout argument)
            Client(space_url, **kwargs)
            st.success("Client instantiated successfully (no network call performed yet).")
        except Exception as e:
            st.error("Connection test failed")
            st.exception(e)

    if predict_btn:
        if not text.strip():
            st.warning("Enter input text first.")
        else:
            try:
                with st.spinner("Calling remote space…"):
                    resp = call_space_predict(space_url, text, hf_token, int(timeout))
                st.subheader("Raw response")
                # try to pretty-print JSON if possible
                parsed = None
                try:
                    parsed = json.loads(resp) if isinstance(resp, (str, bytes)) else resp
                    st.json(parsed)
                except Exception:
                    st.text(str(resp))

                # --- save remote response (new) ---
                if auto_save or st.button("Save this remote prediction"):
                    rec = {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "mode": "remote_space",
                        "space_url": space_url,
                        "input_text": text,
                        "response_raw": resp,
                        "response_parsed": parsed,
                    }
                    try:
                        append_json_record(RESULTS_FPATH, rec)
                        st.success(f"Saved result to {RESULTS_FPATH.name}")
                    except Exception as e:
                        st.error(f"Save failed: {e}")

            except Exception as e:
                st.error("Prediction failed")
                st.exception(e)

# -------------------------
# Local HF model (transformers)
# -------------------------
else:
    st.header("Local model — Hugging Face transformers")
    st.markdown("Load tokenizer + model locally and run a forward pass. Provide HF repo id or local path.")
    model_repo = st.text_input("Model repo or path", value=os.getenv("HF_MODEL", "climatebert/econbert"))
    use_fast = st.checkbox("Use fast tokenizer", value=True)
    max_len = st.slider("Max tokens", min_value=32, max_value=2048, value=512, step=32)
    text = st.text_area("Input text", "The Federal Reserve increased interest rates by 25 basis points.", height=200)

    col1, col2 = st.columns([2, 1])
    with col1:
        load_btn = st.button("Load tokenizer & model")
        run_btn = st.button("Run tokenizer + model")
    with col2:
        clear_cache = st.button("Clear cached model")

    if clear_cache:
        try:
            st.cache_resource.clear()
            st.success("Cleared cached resources")
        except Exception as e:
            st.error(f"Clear cache failed: {e}")

    @st.cache_resource(show_spinner=False)
    def _load_transformers(repo: str, use_fast_tok: bool, token: str | None):
        try:
            from transformers import AutoTokenizer, AutoModel
        except Exception as e:
            raise RuntimeError(f"transformers not installed: {e}")
        kwargs = {}
        if token:
            kwargs["use_auth_token"] = token
        tokenizer = AutoTokenizer.from_pretrained(repo, use_fast=use_fast_tok, **kwargs)
        model = AutoModel.from_pretrained(repo, **kwargs)
        return tokenizer, model

    tokenizer = None
    model = None
    if load_btn:
        try:
            st.info(f"Loading {model_repo} … this may take time and disk space.")
            tokenizer, model = _load_transformers(model_repo, use_fast, hf_token or None)
            st.success("Model & tokenizer loaded")
            st.write("Tokenizer:", type(tokenizer).__name__, "Model:", type(model).__name__)
        except Exception as e:
            st.error("Load failed")
            st.exception(e)
    else:
        # try reuse cached resources
        try:
            tokenizer, model = _load_transformers(model_repo, use_fast, hf_token or None)
        except Exception:
            tokenizer = None
            model = None

    if tokenizer is None or model is None:
        st.warning("Tokenizer / model not loaded. Click 'Load tokenizer & model' to initialize.")
    else:
        st.markdown("### Tokenizer / inputs")
        if st.button("Show tokenization only"):
            try:
                inputs = tokenizer(text, truncation=True, max_length=max_len)
                token_ids = inputs.get("input_ids", [])
                tokens = tokenizer.convert_ids_to_tokens(token_ids)
                st.write({"tokens_count": len(tokens)})
                st.write(tokens[:200])
            except Exception as e:
                st.exception(e)

        if run_btn:
            try:
                import torch
                inputs = tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=max_len,
                    padding="longest",
                )
                st.write("Input IDs shape:", inputs["input_ids"].shape)
                tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].tolist())
                st.write("Tokens (first 200):", tokens[:200])

                with st.spinner("Running model forward…"):
                    model.eval()
                    with torch.no_grad():
                        outputs = model(**inputs)
                # Handle common outputs
                last_hidden = getattr(outputs, "last_hidden_state", None)
                pooled = getattr(outputs, "pooler_output", None)
                st.subheader("Model outputs")
                if last_hidden is not None:
                    st.write("last_hidden_state shape:", tuple(last_hidden.shape))
                else:
                    st.write("Raw outputs:")
                    st.write(outputs)

                if pooled is None and last_hidden is not None:
                    emb = last_hidden.mean(dim=1)
                    arr = emb.detach().cpu().numpy().tolist()
                    st.write("Pooled embedding (mean) shape:", tuple(emb.shape))
                elif pooled is not None:
                    arr = pooled.detach().cpu().numpy().tolist()
                    st.write("Pooler output shape:", tuple(pooled.shape))
                else:
                    arr = None

                if arr is not None:
                    # show brief preview and allow download
                    st.write("Embedding (first 3 dims):", [row[:3] for row in arr])
                    b = io.BytesIO(json.dumps(arr, ensure_ascii=False).encode("utf-8"))
                    st.download_button("Download embedding (JSON)", b, file_name="embedding.json", mime="application/json")

                    # --- save local run results (new) ---
                    if auto_save or st.button("Save this local run"):
                        rec = {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "mode": "local_model",
                            "model_repo": model_repo,
                            "input_text": text,
                            "embedding_shape": (len(arr), len(arr[0])) if arr else None,
                            "embedding_preview": [row[:3] for row in arr],
                        }
                        try:
                            append_json_record(RESULTS_FPATH, rec)
                            st.success(f"Saved result to {RESULTS_FPATH.name}")
                        except Exception as e:
                            st.error(f"Save failed: {e}")
            except Exception as e:
                st.error("Model run failed")
                st.exception(e)

st.markdown("---")
st.caption("Use Remote Space mode to call the hosted ClimateBERT demo (gradio). Use Local HF model mode to load and run a HF model locally. Ensure dependencies: gradio-client and/or transformers + torch installed in the environment.")

# Add a short sidebar / footer control to download or view stored results
if RESULTS_FPATH.exists():
    with st.sidebar.expander("Stored results"):
        st.write(f"Records: {len(json.loads(RESULTS_FPATH.read_text(encoding='utf-8')))}")
        if st.button("Download stored results"):
            st.download_button("Download results JSON", RESULTS_FPATH.read_bytes(), file_name=RESULTS_FPATH.name, mime="application/json")
