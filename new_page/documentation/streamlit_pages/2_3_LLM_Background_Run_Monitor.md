# 2.3 LLM Background Run Monitor

## Purpose

This page runs T3-style LLM ESG extraction behind the scenes and visualizes progress while the worker continues independently of the main Streamlit interaction.

## Main Features

- Create a background extraction job from OCR markdown pages.
- Choose document, pages, batch size, prompts, backend, model ids, context length, token limit, temperature, and retry count.
- Support OpenRouter, LM Studio/OpenAI-compatible, Ollama, and Mock mode.
- Monitor live status, current sample, updated time, process id, completed samples, failed samples, skipped samples, and remaining work.
- Pause after the current sample, resume a paused job, or stop after the current sample.
- Inspect worker events, redacted config, stdout logs, and stderr logs.
- Optionally run a dry/mock job without appending outputs to `esg_records.json`.

## Inputs

- `new_page/data/thesis_dataset/<document>/pages/page_*.md`
- `new_page/prompt/*.md`

## Outputs

- Job metadata under `new_page/results/background_llm_jobs/<job_id>/`
- Appended T3-style records in `new_page/results/esg_records.json`

## Thesis Use

- RQ1: demonstrates that extraction can be run as a reproducible queue over OCR pages.
- RQ4: exposes failures and unstable items as job events and logs.
- RQ5: improves auditability through job status, events, configuration, and logs.
- RQ6: supports matched reruns across model and prompt combinations.
