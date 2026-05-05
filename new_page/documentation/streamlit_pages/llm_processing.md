# LLM Processing

## Purpose

This page is the main extraction pipeline. It processes selected report text through LLM prompts and model backends, then stores structured ESG records.

## Data Used

Inputs:

- manual text,
- OCR-derived markdown pages,
- prompt templates in `prompt/`,
- selected LLM backend and model.

Outputs:

- `results/esg_records.json`,
- possible T1/T2/T3 result files depending on selected pipeline steps.

## Workflow Steps

1. Select input mode.
2. Choose source document or manual input.
3. Select page ranges or page batches.
4. Choose model backend: OpenRouter, LM Studio/OpenAI-compatible, or Ollama.
5. Choose one or more prompt templates.
6. Run extraction.
7. Parse JSON output.
8. Save raw and parsed outputs.

## LM Studio / VPS Usage

The page supports LM Studio through its OpenAI-compatible API. In the sidebar, select **LM Studio / OpenAI-compatible** as the T3 backend.

Accepted URL formats:

- `http://127.0.0.1:1234/v1`
- `http://localhost:1234/v1`
- `http://127.0.0.1:1234/v1/models`
- `http://YOUR_VPS_IP:1234/v1`
- a reverse-proxy URL that ends in `/v1`

The page normalizes endpoint URLs automatically. For example, if you paste `http://127.0.0.1:1234/v1/models`, the app uses `http://127.0.0.1:1234/v1` as the base URL and calls:

- `GET /v1/models` to list models;
- `POST /v1/chat/completions` to run T3 extraction.

Important deployment note:

- If Streamlit and LM Studio run on the same VPS, `127.0.0.1` refers to the VPS.
- If Streamlit runs in the hosted app or VPS and LM Studio runs on your Mac, the browser may reach `127.0.0.1:1234`, but the Streamlit server cannot. In that case, create a reverse tunnel from your Mac to the VPS:

```bash
ssh -N -R 1234:127.0.0.1:1234 ubuntu@YOUR_VPS_IP
```

Then keep the Streamlit URL as:

```text
http://127.0.0.1:1234/v1
```

- If Streamlit runs on your local machine and LM Studio runs on the VPS, use a local forward tunnel:

```bash
ssh -N -L 1234:127.0.0.1:1234 ubuntu@YOUR_VPS_IP
```

Then keep the Streamlit URL as:

```text
http://127.0.0.1:1234/v1
```

If `/v1/models` is empty, load a model in LM Studio first. The page also provides a **Manual model id** field for cases where the model endpoint is hidden by a proxy or you already know the exact model id.

If your VPS reverse proxy requires authentication, fill the optional API key field. LM Studio itself usually does not need an API key.

## Ollama / VPS Usage

The page also supports Ollama through its native API. In the sidebar, select **Ollama** as the T3 backend.

Accepted URL formats:

- `http://127.0.0.1:11434`
- `http://localhost:11434`
- `http://127.0.0.1:11434/api/tags`
- `http://YOUR_VPS_IP:11434`

The page normalizes endpoint URLs automatically. For example, if you paste `http://127.0.0.1:11434/api/tags`, the app uses `http://127.0.0.1:11434` as the base URL and calls:

- `GET /api/tags` to list models;
- `POST /api/chat` to run T3 extraction.

To verify Ollama on the VPS:

```bash
curl http://127.0.0.1:11434/api/tags
```

Example model returned by Ollama:

```text
deepseek-r1:1.5b
```

If Streamlit and Ollama both run on the VPS, keep the app URL as:

```text
http://127.0.0.1:11434
```

If Streamlit runs locally and Ollama runs on the VPS, forward the port:

```bash
ssh -N -L 11434:127.0.0.1:11434 ubuntu@YOUR_VPS_IP
```

If Streamlit runs on the VPS and Ollama runs on your Mac, reverse-forward the port:

```bash
ssh -N -R 11434:127.0.0.1:11434 ubuntu@YOUR_VPS_IP
```

DeepSeek R1 models may produce reasoning text before the final JSON. The parser now strips `<think>...</think>` blocks before trying to parse JSON, which improves compatibility with reasoning-style Ollama models.

### Ollama HTTP 500 Troubleshooting

If a run fails with a message such as:

```text
Ollama failed after 3 attempts at http://127.0.0.1:11434/api/chat
```

the URL is usually correct, but the Ollama server rejected or crashed during generation. Common causes are:

- `num_predict` is too high for the VPS memory/model size;
- the prompt is too large for the model context window;
- the selected model is unloaded, corrupted, or out of memory;
- Ollama is restarting while the request is running.

The page now has an **Ollama num_predict** control and caps Ollama output length separately from the global `Max tokens` setting. Start with:

```text
Ollama num_predict = 1024 or 2048
Ollama num_ctx = 1024 or 2048
Context length = 3000 to 6000 characters
Batch size = 1 page
```

If Ollama reports:

```text
model requires more system memory (7.2 GiB) than is available (5.5 GiB)
```

that is RAM availability, not disk space. `df -h` only shows disk. `htop` can show total memory, but Ollama needs enough available RAM to load model weights plus context/KV cache. A VPS with 7.45 GiB total RAM can still have only about 5.5 GiB available after the OS, Streamlit, Python, Ollama, and other services are running. Reducing `num_ctx` lowers the KV-cache memory, but if the model weights alone are too large, use a smaller/quantized model or a larger VPS.

On the VPS, verify the model directly:

```bash
curl http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma4:e2b","stream":false,"messages":[{"role":"user","content":"Return only JSON: [{\"ok\": true}]"}],"options":{"num_predict":256,"num_ctx":1024},"keep_alive":"0s"}'
```

If that command fails, check the Ollama service logs:

```bash
journalctl -u ollama -n 100 --no-pager
```

## Important Output Fields

Each ESG record may contain:

- `text`,
- `aspect`,
- `labels`,
- `esg`,
- `tone`,
- `sentiment`,
- `sentiment_score`,
- `reasoning`.

## Interpretation

This page creates the central artifact for most analysis: `results/esg_records.json`.

Because LLMs can produce schema drift, all outputs should be validated through revision analytics, ground-truth annotation, and metrics pages.

## Thesis Use

- Chapter III: T3 LLM extraction method.
- Chapter IV: extraction success and prompt comparison.
- Chapter V: prompt sensitivity and schema drift discussion.
