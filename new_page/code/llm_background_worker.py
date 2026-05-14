from __future__ import annotations

import ast
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter, Retry


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
DATASET_DIR = ROOT / "data" / "thesis_dataset"
PROMPT_DIR = ROOT / "prompt"
JOBS_DIR = RESULTS_DIR / "background_llm_jobs"
ESG_RECORDS_PATH = RESULTS_DIR / "esg_records.json"

OPENROUTER_API_URL = os.getenv(
    "OPENROUTER_API_URL",
    "https://openrouter.ai/api/v1/chat/completions",
)
LMSTUDIO_DEFAULT_URL = "http://127.0.0.1:1234/v1"
OLLAMA_DEFAULT_URL = "http://127.0.0.1:11434"


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(data, ensure_ascii=False) + "\n")


def append_record(record: dict[str, Any], path: Path = ESG_RECORDS_PATH) -> None:
    existing = read_json(path, [])
    if not isinstance(existing, list):
        existing = [existing]
    existing.append(record)
    write_json(path, existing)


def normalize_openai_base_url(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if not url:
        return LMSTUDIO_DEFAULT_URL
    for suffix in ("/models", "/chat/completions", "/completions", "/responses", "/embeddings"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc and not parsed.path:
        url = f"{url}/v1"
    return url.rstrip("/")


def normalize_ollama_base_url(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if not url:
        return OLLAMA_DEFAULT_URL
    for suffix in ("/api/tags", "/api/chat", "/api/generate", "/api/show", "/api/ps"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url.rstrip("/")


def bearer_headers(api_key: str = "") -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    return headers


def request_session(retries: int = 3, backoff: float = 0.6) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["POST", "GET"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


def apply_prompt(template: str, input_text: str) -> str:
    if "{{INPUT_TEXT}}" in template:
        return template.replace("{{INPUT_TEXT}}", input_text)
    return template.strip() + f"\n\n---\n\nText to analyze:\n{input_text}"


def parse_json_from_model(text: str) -> Any:
    if not text or not text.strip():
        raise ValueError("Empty response from model.")
    text = re.sub(r"<think>[\s\S]*?</think>", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip("` \n")
    try:
        return json.loads(text)
    except Exception:
        pass
    matches = re.findall(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    for match in sorted(matches, key=len, reverse=True):
        try:
            return json.loads(match)
        except Exception:
            try:
                return ast.literal_eval(match)
            except Exception:
                continue
    raise ValueError(f"Could not parse JSON from model output: {text[:500]}")


def classify_error(exc: Exception) -> str:
    message = str(exc).lower()
    context_markers = [
        "context length",
        "context window",
        "context size",
        "context_length_exceeded",
        "maximum context",
        "max context",
        "too many tokens",
        "token limit",
        "tokens exceed",
        "exceeds the context",
        "prompt is too long",
        "request too large",
        "input too large",
        "num_ctx",
        "maximum sequence length",
    ]
    if any(marker in message for marker in context_markers):
        return "context_too_large"
    if isinstance(exc, requests.Timeout) or "timed out" in message or "timeout" in message:
        return "timeout"
    if "connection" in message or "connection refused" in message or "remote end closed" in message:
        return "connection"
    if "could not parse json" in message or "empty response" in message:
        return "parse"
    if "rate limit" in message or "429" in message:
        return "rate_limit"
    return "unknown"


def context_retry_budgets(config: dict[str, Any], full_doc: str) -> list[int]:
    initial = int(config.get("context_length", 10000) or len(full_doc))
    initial = max(0, min(initial, len(full_doc)))
    floor = int(config.get("context_retry_floor", 1200) or 1200)
    budgets = [
        initial,
        int(initial * 0.75),
        int(initial * 0.5),
        int(initial * 0.25),
        int(initial * 0.1),
        floor,
        0,
    ]
    cleaned: list[int] = []
    for budget in budgets:
        budget = max(0, min(int(budget), len(full_doc)))
        if budget not in cleaned:
            cleaned.append(budget)
    return cleaned


def make_context_slice(full_doc: str, budget: int) -> str:
    if budget <= 0:
        return ""
    if len(full_doc) <= budget:
        return full_doc
    head = max(0, int(budget * 0.7))
    tail = max(0, budget - head)
    if tail <= 0:
        return full_doc[:budget]
    return (
        full_doc[:head]
        + "\n\n[...document context truncated for retry...]\n\n"
        + full_doc[-tail:]
    )


def retry_budgets_for_text(text: str, floor: int) -> list[int]:
    initial = len(text or "")
    budgets = [
        initial,
        int(initial * 0.75),
        int(initial * 0.5),
        int(initial * 0.25),
        int(initial * 0.1),
        floor,
    ]
    cleaned: list[int] = []
    for budget in budgets:
        budget = max(0, min(int(budget), initial))
        if budget not in cleaned:
            cleaned.append(budget)
    return cleaned or [0]


def make_target_slice(target: dict[str, str], budget: int) -> dict[str, str]:
    text = target.get("text", "")
    if budget <= 0 or len(text) <= budget:
        return target
    sliced = dict(target)
    sliced["text"] = text[:budget] + "\n\n[...target page text truncated for retry...]"
    return sliced


def call_llm_with_context_recovery(
    config: dict[str, Any],
    full_doc: str,
    target: dict[str, str],
    template: str,
    model: str,
    events_path: Path,
) -> tuple[str, Any, dict[str, Any]]:
    auto_reduce_context = bool(config.get("auto_reduce_context_on_error", True))
    max_sample_attempts = max(1, int(config.get("sample_error_retries", 2) or 2))
    budgets = context_retry_budgets(config, full_doc) if auto_reduce_context else [int(config.get("context_length", 10000) or len(full_doc))]
    target_budgets = retry_budgets_for_text(target.get("text", ""), int(config.get("target_retry_floor", 2000) or 2000))
    attempts: list[dict[str, Any]] = []
    last_exc: Exception | None = None
    retry_after_context_error = False

    for attempt_idx, budget in enumerate(budgets, start=1):
        prompt_full_doc = make_context_slice(full_doc, budget)
        target_budget_candidates = target_budgets if budget == 0 and auto_reduce_context else [len(target.get("text", ""))]
        for target_budget in target_budget_candidates:
            prompt_target = make_target_slice(target, target_budget)
            final_prompt = build_context_prompt(prompt_full_doc, prompt_target, template)
            for sample_attempt in range(1, max_sample_attempts + 1):
                try:
                    raw_output = call_llm(config, final_prompt, model)
                    parsed = parse_json_from_model(raw_output)
                    if isinstance(parsed, dict):
                        parsed = [parsed]
                    elif not isinstance(parsed, list):
                        parsed = []
                    meta = {
                        "attempts": attempts
                        + [
                            {
                                "attempt": attempt_idx,
                                "sample_attempt": sample_attempt,
                                "context_chars": len(prompt_full_doc),
                                "target_chars": len(prompt_target.get("text", "")),
                                "prompt_chars": len(final_prompt),
                                "status": "ok",
                            }
                        ],
                        "context_chars": len(prompt_full_doc),
                        "target_chars": len(prompt_target.get("text", "")),
                        "prompt_chars": len(final_prompt),
                        "auto_reduced_context": retry_after_context_error,
                        "auto_reduced_target": len(prompt_target.get("text", "")) < len(target.get("text", "")),
                    }
                    return raw_output, parsed, meta
                except Exception as exc:
                    last_exc = exc
                    error_type = classify_error(exc)
                    attempt_meta = {
                        "attempt": attempt_idx,
                        "sample_attempt": sample_attempt,
                        "context_chars": len(prompt_full_doc),
                        "target_chars": len(prompt_target.get("text", "")),
                        "prompt_chars": len(final_prompt),
                        "status": "failed",
                        "error_type": error_type,
                        "error": str(exc)[:1200],
                    }
                    attempts.append(attempt_meta)
                    append_jsonl(
                        events_path,
                        {
                            "time": utc_now(),
                            "event": "sample_attempt_failed",
                            **attempt_meta,
                        },
                    )
                    if error_type == "context_too_large" and auto_reduce_context:
                        retry_after_context_error = True
                        break
                    if error_type not in {"timeout", "connection", "rate_limit"}:
                        raise
                    if sample_attempt >= max_sample_attempts:
                        raise
                    time.sleep(min(8, sample_attempt * 2))

    if last_exc:
        raise RuntimeError(
            f"Failed after {len(attempts)} attempt(s); last error type={classify_error(last_exc)}; "
            f"last error={last_exc}"
        )
    raise RuntimeError("LLM call failed without a captured exception.")


def call_openrouter(prompt: str, model: str, api_key: str, temperature: float, max_tokens: int, retries: int) -> str:
    if not api_key:
        raise RuntimeError("OpenRouter API key is required unless mock mode is enabled.")
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON generator. Return ONLY valid JSON. If unsure, return [].",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    response = request_session(retries).post(
        OPENROUTER_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://esg-project.app",
            "X-Title": "ESG Background Extractor",
        },
        json=payload,
        timeout=120,
    )
    if 400 <= response.status_code < 500:
        raise RuntimeError(f"OpenRouter returned HTTP {response.status_code}: {response.text[:1200]}")
    response.raise_for_status()
    choices = response.json().get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return response.text


def call_lmstudio(prompt: str, model: str, base_url: str, api_key: str, temperature: float, max_tokens: int, retries: int) -> str:
    base_url = normalize_openai_base_url(base_url)
    if not model:
        raise RuntimeError("LM Studio/OpenAI-compatible model id is required.")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator. Return ONLY valid JSON. If unsure, return []."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    response = request_session(retries).post(
        f"{base_url}/chat/completions",
        headers=bearer_headers(api_key),
        json=payload,
        timeout=240,
    )
    if 400 <= response.status_code < 500:
        raise RuntimeError(f"LM Studio/OpenAI-compatible endpoint returned HTTP {response.status_code}: {response.text[:1200]}")
    response.raise_for_status()
    choices = response.json().get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return response.text


def call_ollama(prompt: str, model: str, base_url: str, api_key: str, temperature: float, max_tokens: int, retries: int, num_ctx: int) -> str:
    base_url = normalize_ollama_base_url(base_url)
    if not model:
        raise RuntimeError("Ollama model id is required.")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator. Return ONLY valid JSON. If unsure, return []."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx": num_ctx,
        },
        "keep_alive": "0s",
    }
    response = request_session(retries).post(
        f"{base_url}/api/chat",
        headers=bearer_headers(api_key),
        json=payload,
        timeout=300,
    )
    if 400 <= response.status_code:
        raise RuntimeError(f"Ollama returned HTTP {response.status_code}: {response.text[:1200]}")
    response.raise_for_status()
    data = response.json()
    if isinstance(data.get("message"), dict):
        return data["message"].get("content", "")
    return data.get("response") or response.text


def call_llm(config: dict[str, Any], prompt: str, model: str) -> str:
    if config.get("mock_mode"):
        return json.dumps(
            [
                {
                    "text": "mock ESG extraction generated by background runner",
                    "aspect": "background-runner-test",
                    "labels": ["mock", "background-runner"],
                    "esg": "E",
                    "tone": "commitment",
                    "sentiment": "neutral",
                    "sentiment_score": 0,
                    "reasoning": "Mock mode validates progress tracking without calling an LLM backend.",
                }
            ]
        )

    backend = config.get("backend", "OpenRouter")
    temperature = float(config.get("temperature", 0.0))
    max_tokens = int(config.get("max_tokens", 1500))
    retries = int(config.get("retries", 2))
    if backend == "LM Studio / OpenAI-compatible":
        return call_lmstudio(
            prompt,
            model,
            config.get("lmstudio_url") or LMSTUDIO_DEFAULT_URL,
            config.get("lmstudio_api_key", ""),
            temperature,
            max_tokens,
            retries,
        )
    if backend == "Ollama":
        return call_ollama(
            prompt,
            model,
            config.get("ollama_url") or OLLAMA_DEFAULT_URL,
            config.get("ollama_api_key", ""),
            temperature,
            max_tokens,
            retries,
            int(config.get("ollama_num_ctx", 2048)),
        )
    return call_openrouter(
        prompt,
        model,
        config.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY", ""),
        temperature,
        max_tokens,
        retries,
    )


def build_batches(config: dict[str, Any]) -> tuple[str, list[dict[str, str]], str]:
    document = config["document"]
    pages_dir = DATASET_DIR / document / "pages"
    page_names = config.get("page_names") or []
    page_paths = [pages_dir / name for name in page_names if (pages_dir / name).exists()]
    if not page_paths:
        raise RuntimeError(f"No selected OCR markdown pages found in {pages_dir}")

    full_doc = "\n\n".join(path.read_text(encoding="utf-8", errors="ignore").strip() for path in sorted(pages_dir.glob("*.md")))
    context_length = int(config.get("context_length", 10000))
    full_doc = full_doc[:context_length] if context_length else full_doc

    batch_size = max(1, int(config.get("batch_size", 1)))
    batches: list[dict[str, str]] = []
    for idx in range(0, len(page_paths), batch_size):
        batch = page_paths[idx : idx + batch_size]
        text = "\n\n".join(path.read_text(encoding="utf-8", errors="ignore").strip() for path in batch)
        label = f"{document}/batch_{idx // batch_size + 1}"
        batches.append({"label": label, "pages": ", ".join(path.name for path in batch), "text": text})
    return document, batches, full_doc


def build_context_prompt(full_doc: str, target: dict[str, str], template: str) -> str:
    combined = (
        f"FULL DOCUMENT:\n{full_doc}\n\n"
        f"TARGET PAGES:\n[PAGE: {target['label']}]\n{target['text']}\n\n"
        f"Return JSON array of ESG records."
    )
    return apply_prompt(template, combined)


def load_prompts(config: dict[str, Any]) -> list[tuple[str, str]]:
    override = (config.get("prompt_override") or "").strip()
    if override:
        return [("override", override)]
    prompts = []
    for name in config.get("prompt_names", []):
        path = PROMPT_DIR / name
        if path.exists():
            prompts.append((name, path.read_text(encoding="utf-8", errors="ignore")))
    if prompts:
        return prompts
    return [("default_fallback", "You are an ESG expert. Analyze:\n{{INPUT_TEXT}}\nOutput a JSON list of ESG records.")]


def processed_successes() -> set[tuple[str, str, str]]:
    rows = read_json(ESG_RECORDS_PATH, [])
    if not isinstance(rows, list):
        return set()
    return {
        (row.get("model", ""), row.get("target", ""), row.get("prompt", ""))
        for row in rows
        if isinstance(row, dict) and row.get("ok")
    }


def update_status(status_path: Path, **updates: Any) -> dict[str, Any]:
    status = read_json(status_path, {})
    status.update(updates)
    status["updated_at"] = utc_now()
    write_json(status_path, status)
    return status


def main(job_id: str) -> int:
    job_dir = JOBS_DIR / job_id
    config_path = job_dir / "config.json"
    status_path = job_dir / "status.json"
    events_path = job_dir / "events.jsonl"
    control_path = job_dir / "control.json"
    config = read_json(config_path, {})
    if not config:
        raise RuntimeError(f"Missing job config: {config_path}")

    document, batches, full_doc = build_batches(config)
    prompts = load_prompts(config)
    models = config.get("models") or ["mock-model"]
    total = len(models) * len(batches) * len(prompts)
    successes = processed_successes() if config.get("skip_existing", True) else set()

    status = update_status(
        status_path,
        job_id=job_id,
        pid=os.getpid(),
        status="running",
        document=document,
        total=total,
        completed=int(read_json(status_path, {}).get("completed", 0)),
        failed=int(read_json(status_path, {}).get("failed", 0)),
        skipped=int(read_json(status_path, {}).get("skipped", 0)),
        started_at=read_json(status_path, {}).get("started_at") or utc_now(),
    )
    append_jsonl(events_path, {"time": utc_now(), "event": "started", "total": total, "pid": os.getpid()})

    completed = int(status.get("completed", 0))
    failed = int(status.get("failed", 0))
    skipped = int(status.get("skipped", 0))

    for model in models:
        for target in batches:
            for prompt_label, template in prompts:
                control = read_json(control_path, {})
                if control.get("stop_requested"):
                    update_status(status_path, status="stopped", current="Stopped before next sample")
                    append_jsonl(events_path, {"time": utc_now(), "event": "stopped"})
                    return 0
                if control.get("pause_requested"):
                    update_status(status_path, status="paused", current="Paused before next sample")
                    append_jsonl(events_path, {"time": utc_now(), "event": "paused"})
                    return 0

                key = (model, target["label"], prompt_label)
                current = f"{target['label']} · {prompt_label} · {model}"
                update_status(status_path, status="running", current=current)

                if key in successes:
                    skipped += 1
                    completed += 1
                    update_status(status_path, completed=completed, skipped=skipped, current=f"Skipped existing {current}")
                    append_jsonl(events_path, {"time": utc_now(), "event": "skipped", "target": target["label"], "prompt": prompt_label, "model": model})
                    continue

                started = time.time()
                try:
                    raw_output, parsed, recovery_meta = call_llm_with_context_recovery(
                        config,
                        full_doc,
                        target,
                        template,
                        model,
                        events_path,
                    )
                    record = {
                        "timestamp": utc_now(),
                        "model": model,
                        "target": target["label"],
                        "target_pages": target["pages"],
                        "prompt": prompt_label,
                        "ok": True,
                        "records": parsed,
                        "raw_output": raw_output[:10000],
                        "background_job_id": job_id,
                        "recovery": recovery_meta,
                    }
                    if config.get("save_results", True):
                        append_record(record)
                    completed += 1
                    append_jsonl(
                        events_path,
                        {
                            "time": utc_now(),
                            "event": "completed",
                            "target": target["label"],
                            "pages": target["pages"],
                            "prompt": prompt_label,
                            "model": model,
                            "records": len(parsed),
                            "auto_reduced_context": recovery_meta.get("auto_reduced_context", False),
                            "context_chars": recovery_meta.get("context_chars"),
                            "prompt_chars": recovery_meta.get("prompt_chars"),
                            "seconds": round(time.time() - started, 2),
                        },
                    )
                except Exception as exc:
                    error_type = classify_error(exc)
                    failed += 1
                    completed += 1
                    record = {
                        "timestamp": utc_now(),
                        "model": model,
                        "target": target["label"],
                        "target_pages": target["pages"],
                        "prompt": prompt_label,
                        "ok": False,
                        "records": [],
                        "error": str(exc),
                        "error_type": error_type,
                        "raw_output": "",
                        "background_job_id": job_id,
                    }
                    if config.get("save_results", True):
                        append_record(record)
                    append_jsonl(
                        events_path,
                        {
                            "time": utc_now(),
                            "event": "failed",
                            "target": target["label"],
                            "pages": target["pages"],
                            "prompt": prompt_label,
                            "model": model,
                            "error_type": error_type,
                            "error": str(exc)[:1200],
                            "seconds": round(time.time() - started, 2),
                        },
                    )
                update_status(status_path, completed=completed, failed=failed, skipped=skipped)

    update_status(status_path, status="completed", current="All samples completed", finished_at=utc_now())
    append_jsonl(events_path, {"time": utc_now(), "event": "completed_job", "completed": completed, "failed": failed, "skipped": skipped})
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python llm_background_worker.py <job_id>", file=sys.stderr)
        raise SystemExit(2)
    try:
        raise SystemExit(main(sys.argv[1]))
    except Exception as exc:
        if len(sys.argv) == 2:
            job_dir = JOBS_DIR / sys.argv[1]
            update_status(job_dir / "status.json", status="failed", error=str(exc), finished_at=utc_now())
            append_jsonl(job_dir / "events.jsonl", {"time": utc_now(), "event": "worker_crashed", "error": str(exc)})
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
