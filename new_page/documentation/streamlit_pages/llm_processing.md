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
4. Choose model backend: OpenRouter or LM Studio/OpenAI-compatible.
5. Choose one or more prompt templates.
6. Run extraction.
7. Parse JSON output.
8. Save raw and parsed outputs.

## LM Studio / VPS Usage

The page supports LM Studio through its OpenAI-compatible API. In the sidebar, select **LM Studio / OpenAI-compatible** as the T3 backend.

Accepted URL formats:

- `http://127.0.0.1:1234/v1`
- `http://127.0.0.1:1234/v1/models`
- `http://YOUR_VPS_IP:1234/v1`
- a reverse-proxy URL that ends in `/v1`

The page normalizes endpoint URLs automatically. For example, if you paste `http://127.0.0.1:1234/v1/models`, the app uses `http://127.0.0.1:1234/v1` as the base URL and calls:

- `GET /v1/models` to list models;
- `POST /v1/chat/completions` to run T3 extraction.

Important deployment note:

- If Streamlit and LM Studio run on the same VPS, `127.0.0.1` refers to the VPS.
- If Streamlit runs on your local machine and LM Studio runs on the VPS, use an SSH tunnel such as:

```bash
ssh -N -L 1234:127.0.0.1:1234 ubuntu@YOUR_VPS_IP
```

Then keep the Streamlit URL as:

```text
http://127.0.0.1:1234/v1
```

If `/v1/models` is empty, load a model in LM Studio first. The page also provides a **Manual model id** field for cases where the model endpoint is hidden by a proxy or you already know the exact model id.

If your VPS reverse proxy requires authentication, fill the optional API key field. LM Studio itself usually does not need an API key.

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
