import os
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="EconBERT / ClimateBERT — Model tester", page_icon="🤖", layout="wide")
st.title("EconBERT / ClimateBERT — Model tester")
st.markdown("Quickly load a Hugging Face model (tokenizer + AutoModel) and inspect tokens / embeddings. "
            "Warning: downloading large models may take time and use disk/ram.")

MODEL_DEFAULT = "YourUsername/EconBERT"
model_name = st.text_input("Model repo (HF)", value=os.getenv("HF_MODEL", MODEL_DEFAULT))
hf_token = st.text_input("HF token (optional, leave blank for public models)", value=os.getenv("HF_TOKEN", ""), type="password")

st.checkbox("Use fast tokenizer", value=True, key="use_fast")
st.checkbox("Use auth token from env HF_TOKEN if empty above", value=True, key="use_env_token")

if st.session_state.get("use_env_token") and not hf_token:
    hf_token = os.getenv("HF_TOKEN", "") or hf_token

st.markdown("## Controls")
col1, col2 = st.columns([2, 1])
with col1:
    load_model = st.button("Load tokenizer & model")
with col2:
    clear_cache = st.button("Clear cached model")

if clear_cache:
    try:
        st.cache_resource.clear()
        st.success("Cleared cached resources")
    except Exception as e:
        st.error(f"Clear cache failed: {e}")

@st.cache_resource(show_spinner=False)
def _load(model_name: str, use_fast: bool, token: str | None):
    # lazy import to avoid heavy deps at top-level
    try:
        from transformers import AutoTokenizer, AutoModel
    except Exception as e:
        raise RuntimeError(f"transformers import failed: {e}")
    kwargs = {}
    if token:
        # transformers historically accepts use_auth_token
        kwargs["use_auth_token"] = token
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=use_fast, **kwargs)
    model = AutoModel.from_pretrained(model_name, **kwargs)
    return tokenizer, model

tokenizer = None
model = None
if load_model:
    st.info(f"Loading {model_name} — this may take time")
    try:
        tokenizer, model = _load(model_name, st.session_state.get("use_fast", True), hf_token or None)
        st.success("Model & tokenizer loaded")
        st.write("Tokenizer:", type(tokenizer), "Model:", type(model))
    except Exception as e:
        st.exception(e)
        st.stop()
else:
    # try to reuse cached resource if already loaded in this session
    try:
        tokenizer, model = _load(model_name, st.session_state.get("use_fast", True), hf_token or None)
    except Exception:
        tokenizer = None
        model = None

if tokenizer is None or model is None:
    st.warning("Tokenizer / model not loaded. Click 'Load tokenizer & model' to initialize.")
    st.stop()

st.markdown("## Inference / Inspection")
text = st.text_area("Input text", "The Federal Reserve increased interest rates by 25 basis points.", height=160)
max_len = st.slider("Max tokens / truncate", min_value=32, max_value=2048, value=512, step=32)

if st.button("Run tokenizer + model"):
    try:
        import torch
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_len,
            padding="longest",
        )
        st.write("Token ids:", inputs.get("input_ids").shape, inputs.get("input_ids").tolist())
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].tolist())
        # show tokenized text in a compact table
        st.write({"tokens (first 200 chars)": " ".join(tokens[:min(100, len(tokens))])})
        with st.spinner("Running model (forward)..."):
            outputs = model(**inputs)
        # try to extract pooled output or mean-pooled embedding
        last_hidden = getattr(outputs, "last_hidden_state", None)
        pooled = getattr(outputs, "pooler_output", None)
        if last_hidden is None:
            st.warning("Model did not return last_hidden_state; inspect raw outputs.")
            st.write(outputs)
        else:
            st.write("last_hidden_state shape:", tuple(last_hidden.shape))
            if pooled is None:
                # mean pool
                emb = last_hidden.mean(dim=1)
                st.write("Pooled embedding (mean) shape:", tuple(emb.shape))
                arr = emb.detach().cpu().numpy().tolist()
            else:
                st.write("pooler_output shape:", tuple(pooled.shape))
                arr = pooled.detach().cpu().numpy().tolist()
            # show first 3 values for brevity
            st.write("Embedding (first 3 dims):", [row[:3] for row in arr])
            # allow download of full embedding
            import json, io
            b = io.BytesIO(json.dumps(arr, ensure_ascii=False).encode("utf-8"))
            st.download_button("Download embedding (JSON)", b, file_name="embedding.json", mime="application/json")
    except Exception as e:
        st.exception(e)

st.markdown("## Notes")
st.markdown(
    "- Model downloads can be large. Prefer to run on a machine with sufficient disk/RAM and a stable network.\n"
    "- If the model repo is private, provide an HF token with access (set HF_TOKEN env or paste above).\n"
    "- For production use, consider using smaller distilled models or a hosted inference endpoint.\n"
)