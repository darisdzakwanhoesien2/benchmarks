import json
import math
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
THESIS_DATASET_DIR = ROOT_DIR / "data" / "thesis_dataset"
NOTES_PATH = APP_DIR / "notes.md"
RESEARCH_PATH = APP_DIR / "research.md"
TOPIC_MODELLING_RESEARCH_PATH = APP_DIR / "topic_modelling_research.md"
SOURCES_PATH = DATA_DIR / "data_sources.json"
RESULTS_DIR = ROOT_DIR / "results"
ESG_RECORDS_PATH = RESULTS_DIR / "esg_records.json"
SUMMARIZATION_RESULTS_DIR = RESULTS_DIR / "summarization"
JUDGE_RESULTS_DIR = SUMMARIZATION_RESULTS_DIR / "llm_judge"
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is",
    "it", "its", "of", "on", "or", "that", "the", "their", "this", "to", "was", "were",
    "will", "with", "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "adalah",
    "ini", "itu", "dalam", "sebagai", "akan", "atau", "juga", "karena", "agar", "lebih",
    "telah", "menjadi", "kami", "kita", "mereka", "oleh", "serta", "antara", "tidak",
}
PILLAR_KEYWORDS = {
    "E": {
        "emission", "co2", "carbon", "energy", "renewable", "waste", "water", "climate",
        "pollution", "biodiversity", "efisiensi", "lingkungan", "sampah", "air",
    },
    "S": {
        "employee", "training", "community", "health", "safety", "diversity", "labor",
        "inclusion", "human", "karyawan", "pelatihan", "masyarakat", "kesehatan",
        "keselamatan", "sosial",
    },
    "G": {
        "governance", "board", "audit", "risk", "compliance", "ethics", "policy", "anti",
        "corruption", "governansi", "dewan", "kepatuhan", "kebijakan", "pemegang",
    },
}
POSITIVE_CUES = {
    "improve", "improvement", "strong", "commitment", "sustainable", "success", "positive",
    "enhanced", "increased", "berkelanjutan", "komitmen", "peningkatan", "keberhasilan",
    "positif",
}
METRIC_CUES = {
    "ton", "tons", "%", "percent", "kwh", "mw", "gj", "tco2e", "m3", "mwh", "kg", "idr",
    "rp", "target", "baseline", "scope",
}
YEAR_RE = re.compile(r"(20\d{2})")
NUM_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")


st.set_page_config(
    page_title="ESG ABSA Research Dashboard",
    page_icon="📘",
    layout="wide",
)


def _read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _read_json(path: Path) -> list | dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    return slug.strip("._-") or "artifact"


def _write_json(path: Path, payload: object) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_sources_config() -> dict:
    if not SOURCES_PATH.exists():
        return {}
    try:
        payload = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _extract_year(name: str) -> str | None:
    years = YEAR_RE.findall(name)
    return years[-1] if years else None


def _sector_proxy(doc_name: str) -> str:
    dn = doc_name.lower()
    if any(k in dn for k in ("bank", "bni", "bri", "danamon", "permata", "aladin", "neo")):
        return "Financials"
    if any(k in dn for k in ("waskita", "abm", "precast", "beton", "petrosea", "intraco")):
        return "Infrastructure/Industrial"
    if any(k in dn for k in ("goto", "digital", "teknologi", "blibli", "superbank")):
        return "Technology/Digital"
    if any(k in dn for k in ("health", "medik", "soho", "bmhs")):
        return "Healthcare"
    return "Other/Unmapped"


@st.cache_data(show_spinner=False)
def scan_topic_modelling_corpus(dataset_dir: Path) -> dict[str, object]:
    if not dataset_dir.exists():
        return {
            "doc_df": pd.DataFrame(),
            "year_counts": {},
            "sector_counts": {},
            "pillar_signals": {},
            "top_tokens": [],
            "ocr_paths": [],
        }

    ocr_paths = sorted(dataset_dir.glob("*/ocr_result.json"))
    rows = []
    year_counts = Counter()
    sector_counts = Counter()
    top_tokens = Counter()
    pillar_signal_counter = Counter()

    for path in ocr_paths:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        pages = obj.get("pages") or []
        doc_name = path.parent.name
        year = _extract_year(doc_name)
        full_text = "\n".join((p.get("markdown") or "") for p in pages if isinstance(p, dict))
        text_lower = full_text.lower()
        tokens = content_tokens(full_text)
        token_count = len(tokens)
        numeric_count = len(NUM_RE.findall(full_text))

        pillar_hits = {}
        for pillar, words in PILLAR_KEYWORDS.items():
            hits = sum(text_lower.count(word) for word in words)
            pillar_hits[pillar] = hits
            pillar_signal_counter[pillar] += hits

        pos_hits = sum(text_lower.count(word) for word in POSITIVE_CUES)
        metric_hits = sum(text_lower.count(word) for word in METRIC_CUES) + numeric_count
        sector = _sector_proxy(doc_name)

        if year:
            year_counts[year] += 1
        sector_counts[sector] += 1
        top_tokens.update(tokens)

        rows.append(
            {
                "document": doc_name,
                "year": year or "Unknown",
                "sector_proxy": sector,
                "pages": len(pages),
                "tokens": token_count,
                "numeric_mentions": numeric_count,
                "metric_cues_total": metric_hits,
                "positive_cues_total": pos_hits,
                "E_signal": pillar_hits["E"],
                "S_signal": pillar_hits["S"],
                "G_signal": pillar_hits["G"],
            }
        )

    doc_df = pd.DataFrame(rows)
    if not doc_df.empty:
        doc_df["metric_per_1k_tokens"] = (doc_df["metric_cues_total"] / doc_df["tokens"].clip(lower=1)) * 1000
        doc_df["positive_per_1k_tokens"] = (doc_df["positive_cues_total"] / doc_df["tokens"].clip(lower=1)) * 1000
        doc_df["risk_score"] = (doc_df["positive_per_1k_tokens"] + 1.0) / (doc_df["metric_per_1k_tokens"] + 1.0)

    return {
        "doc_df": doc_df,
        "year_counts": dict(sorted(year_counts.items())),
        "sector_counts": dict(sector_counts),
        "pillar_signals": dict(pillar_signal_counter),
        "top_tokens": top_tokens.most_common(30),
        "ocr_paths": [str(p) for p in ocr_paths],
    }
    try:
        return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def load_datasets() -> tuple[dict, list[str]]:
    config = _load_sources_config()
    datasets = {}
    logs = []

    real_keys = [
        "tone_records_flat",
        "t2_flat_outputs",
        "climatebert_proxy_agreement_summary",
        "model_stability_summary",
        "prompt_stability_summary",
        "ontology_coverage",
    ]

    for key in real_keys:
        rel = config.get(key)
        df = pd.DataFrame()
        if rel:
            p = ROOT_DIR / rel
            if p.exists():
                df = _read_csv(p)
                logs.append(f"Loaded real dataset for `{key}` from `{p}`")
            else:
                logs.append(f"Missing real dataset for `{key}` expected at `{p}`")
        else:
            logs.append(f"No configured path for `{key}` in data_sources.json")

        if df.empty:
            sample_name = f"sample_{key}.csv"
            sample_path = DATA_DIR / sample_name
            if sample_path.exists():
                df = _read_csv(sample_path)
                logs.append(f"Loaded fallback sample for `{key}` from `{sample_path}`")
            else:
                logs.append(f"No fallback sample found for `{key}`")

        datasets[key] = df

    return datasets, logs


def metric_int(value) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return "N/A"


def metric_float(value, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return "N/A"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def split_sentences(text: str) -> list[str]:
    if not text or not isinstance(text, str):
        return []
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []
    normalized = re.sub(r"([.!?])(?=[A-ZÀ-ÿ0-9])", r"\1 ", normalized)
    normalized = re.sub(r"([.!?;:])\s*(?=(?:[A-ZÀ-ÿ]|[0-9]|[A-Za-zÀ-ÿ]{2,}\s+[A-ZÀ-ÿ]))", r"\1 ", normalized)
    parts = re.split(r"(?<=[.!?;:])\s+", normalized)
    return [p.strip() for p in parts if p.strip()]


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['-][A-Za-zÀ-ÿ0-9]+)*", text.lower())


def content_tokens(text: str) -> list[str]:
    return [token for token in tokenize(text) if token not in STOPWORDS and len(token) > 1]


def detect_bilingual_signal(text: str) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    english_markers = {"the", "and", "with", "for", "from", "will", "company", "sustainability", "energy"}
    indonesian_markers = {"dan", "dengan", "untuk", "dari", "akan", "perusahaan", "keberlanjutan", "energi"}
    token_set = set(tokens)
    has_en = any(token in token_set for token in english_markers)
    has_id = any(token in token_set for token in indonesian_markers)
    if has_en and has_id:
        return 1.0
    return 0.5 if has_en or has_id else 0.0


def summarize_lead(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    return " ".join(sentences[:max_sentences])


def summarize_frequency(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""
    tokens = content_tokens(text)
    if not tokens:
        return summarize_lead(text, max_sentences=max_sentences)
    freqs = Counter(tokens)
    scores = []
    for idx, sent in enumerate(sentences):
        sent_tokens = content_tokens(sent)
        if not sent_tokens:
            continue
        score = sum(freqs[t] for t in sent_tokens) / (len(sent_tokens) + 1e-9)
        if re.search(r"[A-Za-zÀ-ÿ]", sent) and re.search(r"\b(?:dan|yang|untuk|dengan|the|and|with|for)\b", sent.lower()):
            score *= 1.05
        scores.append((idx, score))
    if not scores:
        return summarize_lead(text, max_sentences=max_sentences)
    top_idx = [i for i, _ in sorted(scores, key=lambda x: x[1], reverse=True)[:max_sentences]]
    top_idx.sort()
    return " ".join(sentences[i] for i in top_idx)


def _sentence_similarity(a: str, b: str) -> float:
    ta = set(content_tokens(a))
    tb = set(content_tokens(b))
    if not ta or not tb:
        return 0.0
    inter = len(ta.intersection(tb))
    denom = math.sqrt(len(ta) * len(tb))
    if denom == 0:
        return 0.0
    return inter / denom


def summarize_textrank_like(text: str, max_sentences: int = 3, iters: int = 20, d: float = 0.85) -> str:
    sentences = split_sentences(text)
    n = len(sentences)
    if n == 0:
        return ""
    if n <= max_sentences:
        return " ".join(sentences)

    sim = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                sim[i][j] = _sentence_similarity(sentences[i], sentences[j])

    scores = [1.0] * n
    for _ in range(iters):
        new_scores = [1 - d] * n
        for i in range(n):
            s = 0.0
            for j in range(n):
                if i == j:
                    continue
                row_sum = sum(sim[j])
                if row_sum > 0:
                    s += (sim[j][i] / row_sum) * scores[j]
            new_scores[i] += d * s
        scores = new_scores

    top_idx = sorted(range(n), key=lambda i: scores[i], reverse=True)[:max_sentences]
    top_idx.sort()
    return " ".join(sentences[i] for i in top_idx)


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def rouge_n(pred: str, ref: str, n: int) -> dict:
    pt = tokenize(pred)
    rt = tokenize(ref)
    p_ngrams = _ngrams(pt, n)
    r_ngrams = _ngrams(rt, n)
    if not p_ngrams or not r_ngrams:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    pc = Counter(p_ngrams)
    rc = Counter(r_ngrams)
    overlap = sum(min(pc[g], rc[g]) for g in rc)
    precision = overlap / len(p_ngrams)
    recall = overlap / len(r_ngrams)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def _lcs_length(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    dp = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        prev = 0
        for j in range(1, len(b) + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = tmp
    return dp[-1]


def rouge_l(pred: str, ref: str) -> dict:
    pt = tokenize(pred)
    rt = tokenize(ref)
    if not pt or not rt:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    lcs = _lcs_length(pt, rt)
    precision = lcs / len(pt)
    recall = lcs / len(rt)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


@st.cache_data(show_spinner=False)
def load_esg_records() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not ESG_RECORDS_PATH.exists():
        return pd.DataFrame(), pd.DataFrame()

    payload = _read_json(ESG_RECORDS_PATH)
    if not isinstance(payload, list):
        return pd.DataFrame(), pd.DataFrame()

    run_rows = []
    record_rows = []
    for run_idx, run in enumerate(payload):
        if not isinstance(run, dict):
            continue
        records = run.get("records") if isinstance(run.get("records"), list) else []
        run_rows.append(
            {
                "run_idx": run_idx,
                "timestamp": str(run.get("timestamp", "")).strip(),
                "model": str(run.get("model", "")).strip(),
                "target": str(run.get("target", "")).strip(),
                "target_pages": str(run.get("target_pages", "")).strip(),
                "prompt": str(run.get("prompt", "")).strip(),
                "ok": bool(run.get("ok")),
                "error_type": str(run.get("error_type", "")).strip(),
                "n_records": len(records),
            }
        )
        for record_idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                continue
            labels = rec.get("labels", [])
            if isinstance(labels, list):
                labels = ", ".join(str(item).strip() for item in labels if str(item).strip())
            record_rows.append(
                {
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "target": str(run.get("target", "")).strip(),
                    "prompt": str(run.get("prompt", "")).strip(),
                    "model": str(run.get("model", "")).strip(),
                    "text": str(rec.get("text", "")).strip(),
                    "aspect": str(rec.get("aspect", "")).strip(),
                    "esg": str(rec.get("esg", "")).strip(),
                    "tone": str(rec.get("tone", "")).strip(),
                    "sentiment": str(rec.get("sentiment", "")).strip(),
                    "labels": str(labels).strip(),
                    "reasoning": str(rec.get("reasoning", "")).strip(),
                }
            )
    return pd.DataFrame(run_rows), pd.DataFrame(record_rows)


def summarize_system(name: str, text: str, max_sentences: int) -> tuple[str, float]:
    start = time.perf_counter()
    if name == "Lead":
        summary = summarize_lead(text, max_sentences=max_sentences)
    elif name == "Frequency":
        summary = summarize_frequency(text, max_sentences=max_sentences)
    else:
        summary = summarize_textrank_like(text, max_sentences=max_sentences)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return summary, elapsed_ms


def build_document_benchmark_frame(tone_df: pd.DataFrame) -> pd.DataFrame:
    if tone_df.empty:
        return pd.DataFrame()

    doc_col = find_column(tone_df, ["target_doc", "source_doc", "target", "company"])
    text_col = find_column(tone_df, ["text", "statement"])
    ref_col = find_column(tone_df, ["reasoning"])
    tone_col = find_column(tone_df, ["tone"])
    esg_col = find_column(tone_df, ["esg", "esg_pillar"])
    aspect_col = find_column(tone_df, ["aspect"])

    if not doc_col or not text_col:
        return pd.DataFrame()

    working = tone_df.copy()
    working[doc_col] = working[doc_col].fillna("").astype(str)
    working[text_col] = working[text_col].fillna("").astype(str)
    if ref_col:
        working[ref_col] = working[ref_col].fillna("").astype(str)

    rows = []
    for doc_id, group in working.groupby(doc_col):
        texts = [value.strip() for value in group[text_col].tolist() if value.strip()]
        refs = [value.strip() for value in group[ref_col].tolist() if value.strip()] if ref_col else []
        if not texts:
            continue
        rows.append(
            {
                "document": doc_id or "unknown",
                "record_count": len(group),
                "text": " ".join(texts),
                "reference": " ".join(refs[: min(8, len(refs))]),
                "sentence_count": len(split_sentences(" ".join(texts))),
                "tone_diversity": group[tone_col].astype(str).nunique() if tone_col else 0,
                "esg_diversity": group[esg_col].astype(str).nunique() if esg_col else 0,
                "aspect_diversity": group[aspect_col].astype(str).nunique() if aspect_col else 0,
            }
        )
    return pd.DataFrame(rows).sort_values(["record_count", "sentence_count"], ascending=False).reset_index(drop=True)


def run_benchmark(benchmark_df: pd.DataFrame, max_sentences: int) -> pd.DataFrame:
    if benchmark_df.empty:
        return pd.DataFrame()

    systems = ["Lead", "Frequency", "TextRank-like"]
    rows = []

    for _, row in benchmark_df.iterrows():
        text = str(row.get("text", ""))
        reference = str(row.get("reference", "")).strip()
        if not text.strip():
            continue
        for system in systems:
            summary, elapsed_ms = summarize_system(system, text, max_sentences=max_sentences)
            out = {
                "document": row.get("document", ""),
                "system": system,
                "record_count": row.get("record_count", 0),
                "sentence_count": row.get("sentence_count", 0),
                "summary_sentences": len(split_sentences(summary)),
                "summary_chars": len(summary),
                "runtime_ms": round(elapsed_ms, 3),
                "has_reference": bool(reference),
            }
            if reference:
                r1 = rouge_n(summary, reference, 1)
                r2 = rouge_n(summary, reference, 2)
                rl = rouge_l(summary, reference)
                out.update(
                    {
                        "rouge1_f1": round(r1["f1"], 4),
                        "rouge2_f1": round(r2["f1"], 4),
                        "rougel_f1": round(rl["f1"], 4),
                        "rouge1_recall": round(r1["recall"], 4),
                        "rouge2_recall": round(r2["recall"], 4),
                        "rougel_recall": round(rl["recall"], 4),
                    }
                )
            rows.append(out)

    return pd.DataFrame(rows)


def build_pseudo_ground_truth_frame(tone_df: pd.DataFrame, max_sentences: int = 3) -> pd.DataFrame:
    benchmark_df = build_document_benchmark_frame(tone_df)
    if benchmark_df.empty:
        return pd.DataFrame()

    rows = []
    for _, row in benchmark_df.iterrows():
        text = str(row.get("text", ""))
        source_sentences = split_sentences(text)
        reasoning_reference = str(row.get("reference", "")).strip()
        lead_summary = summarize_lead(text, max_sentences=max_sentences)
        frequency_summary = summarize_frequency(text, max_sentences=max_sentences)
        textrank_summary = summarize_textrank_like(text, max_sentences=max_sentences)
        abstractive_proxy = reasoning_reference or textrank_summary

        scored_sentences = []
        for sent in source_sentences:
            sent_score = 0.0
            if abstractive_proxy:
                sent_score += rouge_l(sent, abstractive_proxy)["f1"]
                sent_score += rouge_n(sent, abstractive_proxy, 1)["f1"]
            sent_score += 0.2 * detect_bilingual_signal(sent)
            scored_sentences.append((sent, sent_score))

        top_sentences = [sent for sent, _ in sorted(scored_sentences, key=lambda item: item[1], reverse=True)[:max_sentences]]
        extractive_proxy = " ".join(top_sentences)
        verification_support = rouge_l(extractive_proxy, text)["precision"] if extractive_proxy else 0.0
        semantic_alignment = rouge_l(extractive_proxy, abstractive_proxy)["f1"] if abstractive_proxy else 0.0
        completeness = clamp((len(top_sentences) / max(max_sentences, 1)) * 0.5 + semantic_alignment * 0.5, 0.0, 1.0)
        verification_status = "verified" if semantic_alignment >= 0.30 and verification_support >= 0.95 else "review"

        rows.append(
            {
                "document": row.get("document", ""),
                "record_count": row.get("record_count", 0),
                "abstractive_proxy": abstractive_proxy,
                "lead_summary": lead_summary,
                "frequency_summary": frequency_summary,
                "textrank_summary": textrank_summary,
                "pseudo_ground_truth": extractive_proxy,
                "verification_support": round(verification_support, 4),
                "semantic_alignment": round(semantic_alignment, 4),
                "completeness": round(completeness, 4),
                "verification_status": verification_status,
                "bilingual_signal": round(detect_bilingual_signal(text), 4),
            }
        )
    return pd.DataFrame(rows)


def judge_summary(summary: str, source_text: str, pseudo_ground_truth: str, context_row: dict | None = None) -> dict:
    source_tokens = set(content_tokens(source_text))
    summary_tokens = set(content_tokens(summary))
    pseudo_tokens = set(content_tokens(pseudo_ground_truth))
    overlap_source = len(summary_tokens & source_tokens) / max(len(summary_tokens), 1)
    overlap_pseudo = len(summary_tokens & pseudo_tokens) / max(len(pseudo_tokens), 1) if pseudo_tokens else 0.0
    compression = len(summary) / max(len(source_text), 1)
    bilingual = detect_bilingual_signal(source_text)

    faithfulness = clamp(1 + 4 * overlap_source, 1, 5)
    completeness = clamp(1 + 4 * overlap_pseudo, 1, 5)
    source_sentences = split_sentences(source_text)
    summary_sentences = split_sentences(summary)
    concision = clamp(5 - 8 * compression, 1, 5)
    structure = clamp(1 + 4 * min(len(summary_sentences) / max(len(source_sentences), 1), 1.0), 1, 5)
    bilingual_robustness = clamp(3 + 2 * bilingual if bilingual > 0 else 3.0, 1, 5)
    overall = round((faithfulness * 0.35 + completeness * 0.25 + concision * 0.15 + structure * 0.15 + bilingual_robustness * 0.10) * 20, 1)

    failure_tags = []
    if overlap_source < 0.7:
        failure_tags.append("weak_evidence")
    if overlap_pseudo < 0.25:
        failure_tags.append("low_reference_alignment")
    if compression > 0.6:
        failure_tags.append("undercompressed")
    if not summary_sentences:
        failure_tags.append("empty_summary")

    evidence_quote = source_sentences[0][:220] if source_sentences else ""
    verdict = "accept" if overall >= 75 else "revise" if overall >= 55 else "reject"
    rationale = (
        f"Source overlap={overlap_source:.2f}, pseudo-reference alignment={overlap_pseudo:.2f}, "
        f"compression={compression:.2f}, bilingual_signal={bilingual:.2f}."
    )

    out = {
        "faithfulness_score": round(faithfulness, 2),
        "completeness_score": round(completeness, 2),
        "concision_score": round(concision, 2),
        "structure_score": round(structure, 2),
        "bilingual_robustness_score": round(bilingual_robustness, 2),
        "overall_score": overall,
        "verdict_label": verdict,
        "failure_tags": ", ".join(failure_tags) if failure_tags else "none",
        "evidence_quote": evidence_quote,
        "judge_rationale": rationale,
    }
    if context_row:
        out.update(context_row)
    return out


def judge_run_artifact_name(document: str, summary_budget: int) -> str:
    return f"{_safe_slug(document)}__budget_{summary_budget}"


def save_judge_run(
    document: str,
    summary_budget: int,
    judge_df: pd.DataFrame,
    systems: dict[str, str],
    pseudo_row: dict,
    source_text: str,
) -> tuple[Path, Path]:
    _ensure_dir(JUDGE_RESULTS_DIR)
    stem = judge_run_artifact_name(document, summary_budget)
    csv_path = JUDGE_RESULTS_DIR / f"{stem}.csv"
    json_path = JUDGE_RESULTS_DIR / f"{stem}.json"

    judge_df.to_csv(csv_path, index=False)
    payload = {
        "document": document,
        "summary_budget": summary_budget,
        "systems": systems,
        "pseudo_ground_truth": pseudo_row,
        "source_text": source_text,
        "records": judge_df.to_dict(orient="records"),
    }
    _write_json(json_path, payload)
    return csv_path, json_path


def discover_saved_judge_runs() -> list[Path]:
    if not JUDGE_RESULTS_DIR.exists():
        return []
    return sorted(JUDGE_RESULTS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def load_saved_judge_run(path: Path) -> tuple[pd.DataFrame, dict]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return pd.DataFrame(), {}
    records = payload.get("records")
    if not isinstance(records, list):
        return pd.DataFrame(), payload
    return pd.DataFrame(records), payload


def run_judge_for_document(document: str, summary_budget: int, benchmark_df: pd.DataFrame, pseudo_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], dict, str]:
    doc_row = benchmark_df[benchmark_df["document"] == document].iloc[0]
    pseudo_row = pseudo_df[pseudo_df["document"] == document].iloc[0].to_dict()
    text = str(doc_row["text"])
    systems = {
        "Lead": summarize_lead(text, max_sentences=summary_budget),
        "Frequency": summarize_frequency(text, max_sentences=summary_budget),
        "TextRank-like": summarize_textrank_like(text, max_sentences=summary_budget),
        "Pseudo Ground Truth": str(pseudo_row.get("pseudo_ground_truth", "")),
    }
    judge_rows = []
    for system_name, summary in systems.items():
        judge_rows.append(
            judge_summary(
                summary,
                text,
                str(pseudo_row.get("pseudo_ground_truth", "")),
                context_row={"document": document, "system": system_name, "summary_budget": summary_budget},
            )
        )
    judge_df = pd.DataFrame(judge_rows).sort_values(["overall_score", "faithfulness_score"], ascending=False)
    return judge_df, systems, pseudo_row, text


def save_judge_batch(summary_budget: int, batch_df: pd.DataFrame, batch_meta: dict) -> tuple[Path, Path]:
    _ensure_dir(JUDGE_RESULTS_DIR)
    stem = f"batch__budget_{summary_budget}"
    csv_path = JUDGE_RESULTS_DIR / f"{stem}.csv"
    json_path = JUDGE_RESULTS_DIR / f"{stem}.json"
    batch_df.to_csv(csv_path, index=False)
    payload = {
        "scope": "batch",
        "summary_budget": summary_budget,
        "generated_documents": int(batch_df["document"].nunique()) if not batch_df.empty and "document" in batch_df.columns else 0,
        "records": batch_df.to_dict(orient="records"),
        "meta": batch_meta,
    }
    _write_json(json_path, payload)
    return csv_path, json_path


def discover_saved_judge_batches() -> list[Path]:
    if not JUDGE_RESULTS_DIR.exists():
        return []
    return sorted(JUDGE_RESULTS_DIR.glob("batch__budget_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def dataset_inventory(datasets: dict) -> pd.DataFrame:
    config = _load_sources_config() or {}
    rows = []
    for key, df in datasets.items():
        rel = config.get(key, "")
        path = ROOT_DIR / rel if rel else None
        rows.append(
            {
                "dataset": key,
                "configured_path": rel,
                "path_exists": bool(path and path.exists()),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": ", ".join(df.columns.astype(str).tolist()),
            }
        )
    return pd.DataFrame(rows)


def render_automatic_summarization_analysis(datasets: dict) -> None:
    st.subheader("Automatic Summarization Analysis")
    st.caption("Compare built-in extractive summarizers and optionally evaluate with ROUGE metrics.")
    st.info("Bilingual handling is enabled: sentence splitting and keyword scoring account for mixed Indonesian-English text.")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    source_options = ["Manual input", "From tone_records_flat grouped text"]
    source_choice = st.radio("Input Source", source_options, horizontal=True)

    text_input = ""
    if source_choice == "Manual input":
        text_input = st.text_area(
            "Input Document Text",
            height=220,
            placeholder="Paste a report section, page text, or paragraph to summarize.",
        )
    else:
        if tone_df.empty:
            st.warning("tone_records_flat is empty. Use Manual input.")
            return
        group_col = find_column(tone_df, ["source_doc", "source", "company", "target_doc"])
        text_col = find_column(tone_df, ["text", "statement", "reasoning"])
        if not group_col or not text_col:
            st.warning("Required columns not found for grouped summarization (`source_doc/company` and `text/statement/reasoning`).")
            return
        options = sorted(tone_df[group_col].dropna().astype(str).unique().tolist())
        if not options:
            st.warning("No valid grouping values in dataset.")
            return
        selected = st.selectbox("Select Group", options)
        subset = tone_df[tone_df[group_col].astype(str) == selected]
        text_input = " ".join(subset[text_col].dropna().astype(str).tolist())
        st.caption(f"Built input from {len(subset):,} rows in `{selected}`")

    max_sentences = st.slider("Summary Length (sentences)", min_value=1, max_value=10, value=3, step=1)
    if not text_input.strip():
        st.info("Provide input text to generate summaries.")
        return

    lead_summary, lead_ms = summarize_system("Lead", text_input, max_sentences=max_sentences)
    freq_summary, freq_ms = summarize_system("Frequency", text_input, max_sentences=max_sentences)
    rank_summary, rank_ms = summarize_system("TextRank-like", text_input, max_sentences=max_sentences)

    c1, c2, c3 = st.columns(3)
    c1.markdown("#### Lead Baseline")
    c1.caption(f"{lead_ms:.3f} ms")
    c1.write(lead_summary if lead_summary else "No summary generated.")
    c2.markdown("#### Frequency")
    c2.caption(f"{freq_ms:.3f} ms")
    c2.write(freq_summary if freq_summary else "No summary generated.")
    c3.markdown("#### TextRank-like")
    c3.caption(f"{rank_ms:.3f} ms")
    c3.write(rank_summary if rank_summary else "No summary generated.")

    st.markdown("### ROUGE Evaluation (Optional)")
    ref = st.text_area("Reference (Gold) Summary", height=140, placeholder="Paste a reference summary to compute ROUGE-1/2/L.")
    if ref.strip():
        rows = []
        systems = {
            "Lead": lead_summary,
            "Frequency": freq_summary,
            "TextRank-like": rank_summary,
        }
        for name, pred in systems.items():
            r1 = rouge_n(pred, ref, 1)
            r2 = rouge_n(pred, ref, 2)
            rl = rouge_l(pred, ref)
            rows.append(
                {
                    "system": name,
                    "rouge1_f1": round(r1["f1"], 4),
                    "rouge2_f1": round(r2["f1"], 4),
                    "rougel_f1": round(rl["f1"], 4),
                    "rouge1_recall": round(r1["recall"], 4),
                    "rouge2_recall": round(r2["recall"], 4),
                    "rougel_recall": round(rl["recall"], 4),
                }
            )
        scores_df = pd.DataFrame(rows).sort_values(by=["rouge2_f1", "rougel_f1"], ascending=False)
        st.dataframe(scores_df, use_container_width=True)


def render_overview(datasets: dict) -> None:
    st.subheader("Overview")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    t2_df = datasets.get("t2_flat_outputs", pd.DataFrame())
    climate_df = datasets.get("climatebert_proxy_agreement_summary", pd.DataFrame())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Structured ESG Records", metric_int(len(tone_df)))
    col2.metric("T2 Rows", metric_int(len(t2_df)))

    agreement_val = "N/A"
    kappa_val = "N/A"
    if not climate_df.empty:
        agreement_col = find_column(climate_df, ["agreement", "proxy_agreement", "agreement_rate", "value"])
        kappa_col = find_column(climate_df, ["kappa", "cohen_kappa", "cohens_kappa"])
        if agreement_col:
            try:
                agreement_val = f"{float(climate_df[agreement_col].dropna().iloc[0]):.3f}"
            except Exception:
                pass
        if kappa_col:
            try:
                kappa_val = f"{float(climate_df[kappa_col].dropna().iloc[0]):.3f}"
            except Exception:
                pass

    col3.metric("ClimateBERT Agreement", agreement_val)
    col4.metric("Cohen's Kappa", kappa_val)

    st.markdown("### Tone Distribution")
    if not tone_df.empty:
        tone_col = find_column(tone_df, ["tone", "label_tone"])
        if tone_col:
            dist = tone_df[tone_col].fillna("Unknown").value_counts().rename_axis("tone").reset_index(name="count")
            st.bar_chart(dist.set_index("tone"))
        else:
            st.info("No `tone` column found in tone records.")
    else:
        st.info("No tone records available.")

    st.markdown("### Research Question Anchors")
    rq_rows = [
        {
            "rq": "RQ1",
            "question": "How do lightweight extractive methods perform for ESG disclosure summarization?",
            "database_signal": "Evaluated in Auto Summarization and Benchmark tabs using grouped `tone_records_flat` documents.",
        },
        {
            "rq": "RQ2",
            "question": "Can prior-track outputs serve as standalone summarization inputs?",
            "database_signal": "Uses `tone_records_flat`, `t2_flat_outputs`, stability summaries, and ontology coverage as source evidence.",
        },
        {
            "rq": "Goal",
            "question": "Can we build a resource-constrained summarization research dashboard from existing ESG artifacts?",
            "database_signal": "This app now profiles the local datasets, benchmarks extractive methods, and surfaces proxy evaluation metrics.",
        },
    ]
    st.dataframe(pd.DataFrame(rq_rows), use_container_width=True, hide_index=True)


def render_record_explorer(datasets: dict) -> None:
    st.subheader("Record Explorer")
    tone_df = datasets.get("tone_records_flat", pd.DataFrame())

    if tone_df.empty:
        st.warning("No tone record data available.")
        return

    aspect_col = find_column(tone_df, ["aspect"])
    esg_col = find_column(tone_df, ["esg", "esg_pillar"])
    tone_col = find_column(tone_df, ["tone"])

    f1, f2, f3 = st.columns(3)

    filtered = tone_df.copy()

    if aspect_col:
        aspects = ["All"] + sorted(filtered[aspect_col].dropna().astype(str).unique().tolist())
        aspect_choice = f1.selectbox("Aspect", aspects)
        if aspect_choice != "All":
            filtered = filtered[filtered[aspect_col].astype(str) == aspect_choice]

    if esg_col:
        esgs = ["All"] + sorted(filtered[esg_col].dropna().astype(str).unique().tolist())
        esg_choice = f2.selectbox("ESG Pillar", esgs)
        if esg_choice != "All":
            filtered = filtered[filtered[esg_col].astype(str) == esg_choice]

    if tone_col:
        tones = ["All"] + sorted(filtered[tone_col].dropna().astype(str).unique().tolist())
        tone_choice = f3.selectbox("Tone", tones)
        if tone_choice != "All":
            filtered = filtered[filtered[tone_col].astype(str) == tone_choice]

    st.caption(f"Showing {len(filtered):,} rows")
    st.dataframe(filtered, use_container_width=True, height=420)


def render_stability(datasets: dict) -> None:
    st.subheader("Stability Analysis")

    model_df = datasets.get("model_stability_summary", pd.DataFrame())
    prompt_df = datasets.get("prompt_stability_summary", pd.DataFrame())

    left, right = st.columns(2)

    with left:
        st.markdown("#### Model Stability")
        if model_df.empty:
            st.info("No model stability summary available.")
        else:
            st.dataframe(model_df, use_container_width=True)
            model_col = find_column(model_df, ["model", "model_name"])
            success_col = find_column(model_df, ["parse_success_rate", "success_rate"])
            if model_col and success_col:
                chart_df = model_df[[model_col, success_col]].dropna().set_index(model_col)
                st.bar_chart(chart_df)

    with right:
        st.markdown("#### Prompt Stability")
        if prompt_df.empty:
            st.info("No prompt stability summary available.")
        else:
            st.dataframe(prompt_df, use_container_width=True)
            prompt_col = find_column(prompt_df, ["prompt_name", "prompt"])
            success_col = find_column(prompt_df, ["parse_success_rate", "success_rate"])
            if prompt_col and success_col:
                chart_df = prompt_df[[prompt_col, success_col]].dropna().set_index(prompt_col)
                st.bar_chart(chart_df)


def render_ontology(datasets: dict) -> None:
    st.subheader("Ontology Coverage")

    ont_df = datasets.get("ontology_coverage", pd.DataFrame())
    if ont_df.empty:
        st.info("No ontology coverage data available.")
        return

    st.dataframe(ont_df, use_container_width=True)

    status_col = find_column(ont_df, ["status", "mapping_status", "label"])
    count_col = find_column(ont_df, ["count", "records", "value"])

    if status_col and count_col:
        chart_df = ont_df[[status_col, count_col]].dropna().set_index(status_col)
        st.bar_chart(chart_df)


def render_dataset_profile(datasets: dict) -> None:
    st.subheader("Dataset Profile")
    st.caption("Database-backed inventory for the resources referenced by `summarization/research.md`.")

    inventory = dataset_inventory(datasets)
    st.dataframe(inventory, use_container_width=True, hide_index=True)

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    t2_df = datasets.get("t2_flat_outputs", pd.DataFrame())
    if not tone_df.empty:
        doc_col = find_column(tone_df, ["target_doc", "source_doc", "target", "company"])
        aspect_col = find_column(tone_df, ["aspect"])
        esg_col = find_column(tone_df, ["esg", "esg_pillar"])
        tone_col = find_column(tone_df, ["tone"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Unique Documents", metric_int(tone_df[doc_col].astype(str).nunique() if doc_col else 0))
        c2.metric("Unique Aspects", metric_int(tone_df[aspect_col].astype(str).nunique() if aspect_col else 0))
        c3.metric("Unique ESG Labels", metric_int(tone_df[esg_col].astype(str).nunique() if esg_col else 0))
        c4.metric("Unique Tone Labels", metric_int(tone_df[tone_col].astype(str).nunique() if tone_col else 0))

    if not t2_df.empty:
        st.markdown("### T2 Output Snapshot")
        st.dataframe(t2_df.head(20), use_container_width=True)


def render_database_research_dashboard(datasets: dict) -> None:
    st.subheader("Research Dashboard")
    st.caption("Implements the `research.md` agenda against the current project database rather than static text.")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    climate_df = datasets.get("climatebert_proxy_agreement_summary", pd.DataFrame())
    model_df = datasets.get("model_stability_summary", pd.DataFrame())
    prompt_df = datasets.get("prompt_stability_summary", pd.DataFrame())
    benchmark_df = build_document_benchmark_frame(tone_df)

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Document Groups", metric_int(len(benchmark_df)))
    top2.metric("Benchmarkable Records", metric_int(len(tone_df)))
    if not climate_df.empty:
        agree_col = find_column(climate_df, ["percent_agreement"])
        kappa_col = find_column(climate_df, ["cohen_kappa"])
        top3.metric("Climate Agreement", metric_float(climate_df[agree_col].iloc[0] if agree_col else None))
        top4.metric("Cohen's Kappa", metric_float(climate_df[kappa_col].iloc[0] if kappa_col else None))
    else:
        top3.metric("Climate Agreement", "N/A")
        top4.metric("Cohen's Kappa", "N/A")

    st.markdown("### Methodology Mapping")
    method_rows = [
        {"research_component": "Data sources", "local_evidence": "`tone_records_flat`, `t2_flat_outputs`, stability CSVs, ontology coverage"},
        {"research_component": "Lead-N baseline", "local_evidence": "Implemented in app and benchmarked per grouped document"},
        {"research_component": "Frequency-based baseline", "local_evidence": "Implemented in app and benchmarked per grouped document"},
        {"research_component": "TextRank-like baseline", "local_evidence": "Implemented in app and benchmarked per grouped document"},
        {"research_component": "Evaluation", "local_evidence": "ROUGE-1/2/L with reasoning-derived proxy references when available"},
        {"research_component": "Efficiency", "local_evidence": "Runtime per summarizer measured locally in milliseconds"},
        {"research_component": "Pseudo-ground truth", "local_evidence": "Built from grouped source sentences, reasoning-derived abstractive proxy, and ROUGE-ranked extractive selection"},
        {"research_component": "LLM-as-a-judge", "local_evidence": "Judge-style rubric scores summaries for faithfulness, completeness, concision, and bilingual robustness"},
    ]
    st.dataframe(pd.DataFrame(method_rows), use_container_width=True, hide_index=True)

    if benchmark_df.empty:
        st.warning("Could not build grouped document benchmark from `tone_records_flat`.")
        return

    max_docs = st.slider("Documents to benchmark", min_value=3, max_value=min(30, len(benchmark_df)), value=min(10, len(benchmark_df)))
    max_sentences = st.slider("Benchmark summary length", min_value=1, max_value=8, value=3)
    candidate_docs = benchmark_df.head(max_docs).copy()
    results_df = run_benchmark(candidate_docs, max_sentences=max_sentences)

    st.markdown("### Proxy Benchmark Results")
    st.caption("Reference summaries are derived from grouped `reasoning` fields when available, so ROUGE here is a database-backed proxy rather than a human executive-summary gold set.")
    if results_df.empty:
        st.info("No benchmark results generated.")
    else:
        aggregate = (
            results_df.groupby("system", dropna=False)
            .agg(
                documents=("document", "nunique"),
                avg_runtime_ms=("runtime_ms", "mean"),
                avg_summary_chars=("summary_chars", "mean"),
                avg_rouge1_f1=("rouge1_f1", "mean"),
                avg_rouge2_f1=("rouge2_f1", "mean"),
                avg_rougel_f1=("rougel_f1", "mean"),
            )
            .reset_index()
            .sort_values(["avg_rouge2_f1", "avg_rougel_f1"], ascending=False)
        )
        st.dataframe(aggregate.round(4), use_container_width=True, hide_index=True)
        chart_source = aggregate.set_index("system")[["avg_rouge1_f1", "avg_rouge2_f1", "avg_rougel_f1"]]
        st.bar_chart(chart_source)

        detail_cols = [
            "document",
            "system",
            "record_count",
            "sentence_count",
            "runtime_ms",
            "rouge1_f1",
            "rouge2_f1",
            "rougel_f1",
        ]
        st.dataframe(results_df[detail_cols].round(4), use_container_width=True, hide_index=True, height=320)

    st.markdown("### RQ-Linked Evidence")
    rq1, rq2 = st.columns(2)
    with rq1:
        st.markdown("#### RQ1: Extractive Performance")
        if not results_df.empty:
            best = (
                results_df.groupby("system", dropna=False)[["rouge1_f1", "rouge2_f1", "rougel_f1", "runtime_ms"]]
                .mean()
                .round(4)
                .reset_index()
                .sort_values(["rouge2_f1", "rougel_f1"], ascending=False)
            )
            st.dataframe(best, use_container_width=True, hide_index=True)
        else:
            st.info("Benchmark data unavailable.")

    with rq2:
        st.markdown("#### RQ2: Suitability of Prior Outputs")
        source_rows = [
            {"source": "tone_records_flat", "rows": len(tone_df), "supports": "Document-group summarization input and proxy reference generation"},
            {"source": "t2_flat_outputs", "rows": len(datasets.get("t2_flat_outputs", pd.DataFrame())), "supports": "Downstream output inspection and ontology-path summary context"},
            {"source": "model_stability_summary", "rows": len(model_df), "supports": "Comparison context for lightweight summarization vs prior model-heavy stages"},
            {"source": "prompt_stability_summary", "rows": len(prompt_df), "supports": "Reliability framing for why local summarization baselines matter"},
        ]
        st.dataframe(pd.DataFrame(source_rows), use_container_width=True, hide_index=True)

    st.markdown("### Benchmark Corpus")
    corpus_view = candidate_docs[["document", "record_count", "sentence_count", "tone_diversity", "esg_diversity", "aspect_diversity"]]
    st.dataframe(corpus_view, use_container_width=True, hide_index=True, height=280)


def render_pseudo_ground_truth_lab(datasets: dict) -> None:
    st.subheader("Pseudo-Ground Truth Lab")
    st.caption("Builds proxy reference summaries from existing ESG records when no gold executive summary is available.")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    esg_runs_df, esg_records_df = load_esg_records()
    max_sentences = st.slider("Pseudo-ground-truth sentence budget", min_value=1, max_value=6, value=3, key="pseudo_budget")

    pseudo_df = build_pseudo_ground_truth_frame(tone_df, max_sentences=max_sentences)
    if pseudo_df.empty:
        st.warning("No pseudo-ground-truth candidates could be generated from `tone_records_flat`.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pseudo References", metric_int(len(pseudo_df)))
    c2.metric("Verified Candidates", metric_int((pseudo_df["verification_status"] == "verified").sum()))
    c3.metric("Avg Semantic Alignment", metric_float(pseudo_df["semantic_alignment"].mean()))
    c4.metric("ESG Runs Loaded", metric_int(len(esg_runs_df)))

    st.markdown("### Method Mapping")
    method_rows = [
        {"stage": "Generator proxy", "implementation": "Uses grouped `reasoning` text as an abstractive-like proxy when available."},
        {"stage": "ROUGE ranking", "implementation": "Ranks source sentences against the proxy and selects top extractive evidence."},
        {"stage": "Multi-stage verification", "implementation": "Checks source support, semantic alignment, completeness, and bilingual signal before marking `verified`."},
        {"stage": "Expert-in-the-loop handoff", "implementation": "Rows marked `review` are the priority set for manual validation."},
    ]
    st.dataframe(pd.DataFrame(method_rows), use_container_width=True, hide_index=True)

    st.markdown("### Candidate Table")
    view_cols = [
        "document",
        "record_count",
        "verification_status",
        "semantic_alignment",
        "verification_support",
        "completeness",
        "bilingual_signal",
    ]
    st.dataframe(pseudo_df[view_cols], use_container_width=True, hide_index=True, height=280)

    selected_doc = st.selectbox("Inspect pseudo-ground truth for document", pseudo_df["document"].tolist(), key="pseudo_doc")
    row = pseudo_df[pseudo_df["document"] == selected_doc].iloc[0]
    left, right = st.columns(2)
    with left:
        st.markdown("#### Abstractive Proxy")
        st.write(row["abstractive_proxy"] or "No proxy available.")
        st.markdown("#### Pseudo Ground Truth")
        st.write(row["pseudo_ground_truth"] or "No extractive pseudo ground truth generated.")
    with right:
        st.markdown("#### Baseline Candidates")
        st.write(f"Lead: {row['lead_summary']}")
        st.write(f"Frequency: {row['frequency_summary']}")
        st.write(f"TextRank-like: {row['textrank_summary']}")

    if not esg_records_df.empty:
        st.markdown("### Linked ESG Records Sample")
        target_match = esg_records_df[esg_records_df["target"].astype(str).str.contains(re.escape(selected_doc), case=False, na=False)]
        if target_match.empty:
            target_match = esg_records_df.head(10)
        st.dataframe(target_match.head(15), use_container_width=True, hide_index=True, height=260)


def render_llm_judge_lab(datasets: dict) -> None:
    st.subheader("LLM-as-a-Judge Lab")
    st.caption("Implements a rubric-driven judge layer over summary outputs using current local data and evidence tracing.")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    benchmark_df = build_document_benchmark_frame(tone_df)
    pseudo_df = build_pseudo_ground_truth_frame(tone_df, max_sentences=3)
    if benchmark_df.empty or pseudo_df.empty:
        st.warning("Judge lab requires grouped benchmark documents and pseudo-ground-truth candidates.")
        return

    st.markdown("### Process")
    process_rows = [
        {"step": 1, "action": "Build candidate summaries", "details": "Generate Lead, Frequency, TextRank-like, and pseudo-ground-truth summaries from the grouped ESG document."},
        {"step": 2, "action": "Define pseudo reference", "details": "Use the pseudo-ground-truth summary as the main comparison anchor for completeness scoring."},
        {"step": 3, "action": "Judge with rubric", "details": "Score faithfulness, completeness, concision, structure, and bilingual robustness using traceable local heuristics."},
        {"step": 4, "action": "Produce verdicts", "details": "Assign `accept`, `revise`, or `reject`, plus failure tags and evidence quotes for review."},
        {"step": 5, "action": "Persist artifacts", "details": "Save document-level or batch-level judged outputs to `results/summarization/llm_judge/` so future sessions can load them directly."},
    ]
    st.dataframe(pd.DataFrame(process_rows), use_container_width=True, hide_index=True)

    saved_runs = discover_saved_judge_runs()
    saved_batches = discover_saved_judge_batches()
    mode = st.radio("Judge result source", ["Compute now", "Load saved result", "Process all documents", "Load saved batch"], horizontal=True, key="judge_mode")

    selected_doc = ""
    summary_budget = 3
    text = ""
    systems: dict[str, str] = {}
    judge_df = pd.DataFrame()
    payload: dict = {}
    pseudo_row: dict = {}
    batch_df = pd.DataFrame()

    if mode == "Load saved result":
        if not saved_runs:
            st.info("No saved judge results found yet. Compute a run first, then save it.")
            return
        saved_labels = [path.name for path in saved_runs]
        selected_label = st.selectbox("Saved judge artifact", saved_labels, key="judge_saved_artifact")
        selected_path = saved_runs[saved_labels.index(selected_label)]
        judge_df, payload = load_saved_judge_run(selected_path)
        if judge_df.empty:
            st.warning(f"Saved artifact `{selected_path.name}` could not be loaded.")
            return
        selected_doc = str(payload.get("document", ""))
        summary_budget = int(payload.get("summary_budget", 3))
        text = str(payload.get("source_text", ""))
        systems = payload.get("systems", {}) if isinstance(payload.get("systems"), dict) else {}
        pseudo_row = payload.get("pseudo_ground_truth", {}) if isinstance(payload.get("pseudo_ground_truth"), dict) else {}
        st.caption(f"Loaded `{selected_path.name}` from `{selected_path.parent}`")
    elif mode == "Load saved batch":
        if not saved_batches:
            st.info("No saved batch judge results found yet. Run `Process all documents` first.")
            return
        batch_labels = [path.name for path in saved_batches]
        selected_label = st.selectbox("Saved batch artifact", batch_labels, key="judge_saved_batch")
        selected_path = saved_batches[batch_labels.index(selected_label)]
        batch_df, payload = load_saved_judge_run(selected_path)
        if batch_df.empty:
            st.warning(f"Saved batch artifact `{selected_path.name}` could not be loaded.")
            return
        summary_budget = int(payload.get("summary_budget", 3))
        st.caption(f"Loaded batch artifact `{selected_path.name}` from `{selected_path.parent}`")
    elif mode == "Process all documents":
        summary_budget = st.slider("Batch summary length", min_value=1, max_value=6, value=3, key="judge_batch_budget")
        max_docs = st.slider("Documents to process", min_value=1, max_value=len(benchmark_df), value=len(benchmark_df), key="judge_batch_docs")
        documents = benchmark_df["document"].head(max_docs).tolist()
        if st.button("Run judge for all selected documents", use_container_width=True, key="run_judge_batch"):
            rows = []
            for document in documents:
                per_doc_df, _, _, _ = run_judge_for_document(document, summary_budget, benchmark_df, pseudo_df)
                rows.extend(per_doc_df.to_dict(orient="records"))
            batch_df = pd.DataFrame(rows)
            if batch_df.empty:
                st.warning("Batch judge run did not produce any rows.")
                return
            csv_path, json_path = save_judge_batch(
                summary_budget,
                batch_df,
                {"documents": documents, "mode": "batch", "document_count": len(documents)},
            )
            st.success(f"Saved batch judge outputs to `{csv_path.name}` and `{json_path.name}`")
        else:
            st.info("Select batch settings and run the judge to create a reusable corpus-level artifact.")
            return
    else:
        doc_options = benchmark_df["document"].tolist()
        selected_doc = st.selectbox("Document for judge evaluation", doc_options, key="judge_doc")
        summary_budget = st.slider("Summary length for judged systems", min_value=1, max_value=6, value=3, key="judge_budget")

        judge_df, systems, pseudo_row, text = run_judge_for_document(selected_doc, summary_budget, benchmark_df, pseudo_df)

        action_left, action_right = st.columns([1, 3])
        if action_left.button("Save current judge result", use_container_width=True, key="save_judge_run"):
            csv_path, json_path = save_judge_run(selected_doc, summary_budget, judge_df, systems, pseudo_row, text)
            action_right.success(f"Saved judge outputs to `{csv_path.name}` and `{json_path.name}`")

    if mode in {"Process all documents", "Load saved batch"}:
        st.markdown("### Batch Judge Scores")
        top1, top2, top3, top4 = st.columns(4)
        top1.metric("Judge Rows", metric_int(len(batch_df)))
        top2.metric("Documents", metric_int(batch_df["document"].nunique() if "document" in batch_df.columns else 0))
        top3.metric("Mean Overall Score", metric_float(batch_df["overall_score"].mean(), digits=1))
        top4.metric("Accept Rate", metric_float((batch_df["verdict_label"].eq("accept").mean() * 100) if "verdict_label" in batch_df.columns else None, digits=1))

        aggregate = (
            batch_df.groupby("system", dropna=False)
            .agg(
                documents=("document", "nunique"),
                avg_overall_score=("overall_score", "mean"),
                avg_faithfulness=("faithfulness_score", "mean"),
                avg_completeness=("completeness_score", "mean"),
            )
            .reset_index()
            .sort_values("avg_overall_score", ascending=False)
        )
        st.dataframe(aggregate.round(4), use_container_width=True, hide_index=True)
        st.bar_chart(aggregate.set_index("system")[["avg_overall_score", "avg_faithfulness", "avg_completeness"]])

        st.markdown("### Batch Detail")
        batch_cols = [
            "document",
            "system",
            "overall_score",
            "faithfulness_score",
            "completeness_score",
            "concision_score",
            "structure_score",
            "verdict_label",
            "failure_tags",
        ]
        st.dataframe(batch_df[batch_cols], use_container_width=True, hide_index=True, height=360)
        return

    top1, top2, top3 = st.columns(3)
    top1.metric("Judge Variants", metric_int(len(judge_df)))
    top2.metric("Best Overall Score", metric_float(judge_df["overall_score"].max(), digits=1))
    top3.metric("Avg Faithfulness", metric_float(judge_df["faithfulness_score"].mean(), digits=2))

    st.markdown("### G-Eval Style Rubric")
    rubric_rows = [
        {"dimension": "Faithfulness", "criterion": "Is the summary supported by source ESG evidence?"},
        {"dimension": "Completeness", "criterion": "Does it cover the core claims surfaced by the pseudo reference?"},
        {"dimension": "Concision", "criterion": "Is it compressed enough for dashboard use without repeating source text excessively?"},
        {"dimension": "Structure", "criterion": "Does sentence selection preserve readable summary flow?"},
        {"dimension": "Bilingual Robustness", "criterion": "Does performance remain acceptable on mixed Indonesian-English disclosures?"},
    ]
    st.dataframe(pd.DataFrame(rubric_rows), use_container_width=True, hide_index=True)

    st.markdown("### Judge Scores")
    st.dataframe(
        judge_df[
            [
                "system",
                "overall_score",
                "faithfulness_score",
                "completeness_score",
                "concision_score",
                "structure_score",
                "bilingual_robustness_score",
                "verdict_label",
                "failure_tags",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(judge_df.set_index("system")[["faithfulness_score", "completeness_score", "concision_score", "structure_score"]])

    selected_system = st.selectbox("Inspect judged system", judge_df["system"].tolist(), key="judge_system")
    detail = judge_df[judge_df["system"] == selected_system].iloc[0]
    st.markdown("### Judge Detail")
    st.write(f"Summary: {systems.get(selected_system, '')}")
    st.write(f"Verdict: `{detail['verdict_label']}`")
    st.write(f"Failure tags: `{detail['failure_tags']}`")
    st.write(f"Evidence quote: {detail['evidence_quote']}")
    st.write(f"Rationale: {detail['judge_rationale']}")

    with st.expander("Artifact details", expanded=False):
        st.write(f"Results directory: `{JUDGE_RESULTS_DIR}`")
        st.write(f"Selected document: `{selected_doc}`")
        st.write(f"Summary budget: `{summary_budget}`")
        if mode == "Load saved result" and payload:
            st.json(
                {
                    "document": payload.get("document", ""),
                    "summary_budget": payload.get("summary_budget", ""),
                    "saved_systems": list(systems.keys()),
                }
            )


def render_research_notes() -> None:
    st.subheader("Research Framing")
    if NOTES_PATH.exists():
        st.markdown(NOTES_PATH.read_text(encoding="utf-8"))
    else:
        st.warning("`summarization/notes.md` not found.")


def render_research_plan() -> None:
    st.subheader("Research Plan")
    if RESEARCH_PATH.exists():
        st.markdown(RESEARCH_PATH.read_text(encoding="utf-8"))
    else:
        st.warning("`summarization/research.md` not found.")


def render_topic_modelling_research() -> None:
    st.subheader("Topic Modelling Research")
    st.caption("Integrated thesis notes from `topic_modelling/research_notes.md` for cross-track reference inside the summarization workspace.")
    if TOPIC_MODELLING_RESEARCH_PATH.exists():
        st.markdown(TOPIC_MODELLING_RESEARCH_PATH.read_text(encoding="utf-8"))
    else:
        st.warning("`summarization/topic_modelling_research.md` not found.")


def render_topic_modelling_research_dashboard(datasets: dict) -> None:
    st.subheader("Topic Modelling Research Dashboard")
    st.caption("Implements `topic_modelling/research_notes.md` using the current project database and thesis dataset scan.")

    topic_scan = scan_topic_modelling_corpus(THESIS_DATASET_DIR)
    doc_df = topic_scan["doc_df"]
    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    t2_df = datasets.get("t2_flat_outputs", pd.DataFrame())
    model_df = datasets.get("model_stability_summary", pd.DataFrame())
    prompt_df = datasets.get("prompt_stability_summary", pd.DataFrame())
    ontology_df = datasets.get("ontology_coverage", pd.DataFrame())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OCR Documents", metric_int(len(topic_scan["ocr_paths"])))
    c2.metric("Structured ESG Records", metric_int(len(tone_df)))
    c3.metric("T2 Rows", metric_int(len(t2_df)))
    c4.metric("Ontology Aspects", metric_int(len(ontology_df)))

    st.markdown("### Research Mapping")
    mapping_rows = [
        {"research_component": "Task-framework dashboard", "local_evidence": "Corpus scan over `data/thesis_dataset/*/ocr_result.json` with document-level thematic proxies."},
        {"research_component": "Domain-specific keyword heuristics", "local_evidence": "E/S/G signals estimated with bilingual pillar keyword dictionaries in the app."},
        {"research_component": "Cross-category ESG trends", "local_evidence": "Year, sector proxy, and pillar signal distributions exposed for corpus-wide comparison."},
        {"research_component": "Interactive corpus scanning", "local_evidence": "Database-backed tables and charts summarize pages, token mass, signal density, and narrative-risk patterns."},
        {"research_component": "Heuristic mapping without exhaustive labels", "local_evidence": "Links `tone_records_flat`, `t2_flat_outputs`, and ontology coverage as weak-supervision style evidence."},
    ]
    st.dataframe(pd.DataFrame(mapping_rows), use_container_width=True, hide_index=True)

    if doc_df.empty:
        st.warning("No parseable `data/thesis_dataset/*/ocr_result.json` files were found for topic modelling analysis.")
        return

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Corpus Pages", metric_int(doc_df["pages"].sum()))
    top2.metric("Corpus Tokens", metric_int(doc_df["tokens"].sum()))
    top3.metric("Avg Tokens / Doc", metric_int(round(doc_df["tokens"].mean())))
    top4.metric("Avg Risk Score", metric_float(doc_df["risk_score"].mean()))

    left, right = st.columns(2)
    with left:
        st.markdown("### Coverage by Year")
        year_df = pd.DataFrame([{"year": k, "documents": v} for k, v in topic_scan["year_counts"].items()])
        if not year_df.empty:
            st.bar_chart(year_df.set_index("year"))
        else:
            st.info("No year markers detected in document names.")

        st.markdown("### Sector Proxy Distribution")
        sector_df = pd.DataFrame([{"sector": k, "documents": v} for k, v in topic_scan["sector_counts"].items()]).sort_values("documents", ascending=False)
        st.bar_chart(sector_df.set_index("sector"))

    with right:
        st.markdown("### ESG Pillar Signal Totals")
        pillar_df = pd.DataFrame([{"pillar": k, "hits": v} for k, v in topic_scan["pillar_signals"].items()]).sort_values("hits", ascending=False)
        st.bar_chart(pillar_df.set_index("pillar"))

        st.markdown("### Metric vs Positive Cue Density")
        scatter_df = doc_df[["document", "metric_per_1k_tokens", "positive_per_1k_tokens"]].copy()
        st.scatter_chart(scatter_df, x="positive_per_1k_tokens", y="metric_per_1k_tokens")

    st.markdown("### RQ-Linked Evidence")
    rq1, rq2 = st.columns(2)
    with rq1:
        st.markdown("#### RQ1: Heuristic ESG Signal Detection")
        signal_rows = [
            {"indicator": "Documents scanned", "value": int(len(doc_df)), "interpretation": "Corpus-wide base for unsupervised thematic scanning."},
            {"indicator": "Environment signal", "value": int(doc_df["E_signal"].sum()), "interpretation": "Keyword hit volume for environmental topics."},
            {"indicator": "Social signal", "value": int(doc_df["S_signal"].sum()), "interpretation": "Keyword hit volume for social topics."},
            {"indicator": "Governance signal", "value": int(doc_df["G_signal"].sum()), "interpretation": "Keyword hit volume for governance topics."},
        ]
        st.dataframe(pd.DataFrame(signal_rows), use_container_width=True, hide_index=True)

    with rq2:
        st.markdown("#### RQ2: Adapted Framework Feasibility")
        feasibility_rows = [
            {"evidence": "Structured ESG records", "value": int(len(tone_df)), "why_it_matters": "Shows downstream extraction can complement unsupervised corpus scanning."},
            {"evidence": "Ontology mappings", "value": int(len(ontology_df)), "why_it_matters": "Supports thematic alignment between detected topics and semantic ESG categories."},
            {"evidence": "Model stability rows", "value": int(len(model_df)), "why_it_matters": "Indicates whether the broader pipeline is reliable enough for topic-support workflows."},
            {"evidence": "Prompt stability rows", "value": int(len(prompt_df)), "why_it_matters": "Shows prompt-dependent extraction variance around the same corpus."},
        ]
        st.dataframe(pd.DataFrame(feasibility_rows), use_container_width=True, hide_index=True)

    st.markdown("### Narrative-Risk Shortlist")
    st.caption("High positive language density with lower metric density is treated as a heuristic follow-up signal, not a definitive greenwashing label.")
    risk_view = doc_df.sort_values("risk_score", ascending=False)[
        ["document", "year", "sector_proxy", "positive_per_1k_tokens", "metric_per_1k_tokens", "risk_score", "E_signal", "S_signal", "G_signal"]
    ]
    st.dataframe(risk_view.head(20).round(4), use_container_width=True, hide_index=True, height=320)

    st.markdown("### Top Corpus Tokens")
    token_df = pd.DataFrame(topic_scan["top_tokens"], columns=["token", "count"])
    if not token_df.empty:
        st.dataframe(token_df.head(20), use_container_width=True, hide_index=True)

    st.markdown("### Ontology and T2 Support")
    support_left, support_right = st.columns(2)
    with support_left:
        if not ontology_df.empty:
            st.markdown("#### Ontology Coverage Snapshot")
            st.dataframe(ontology_df.head(15), use_container_width=True, hide_index=True, height=260)
        else:
            st.info("No ontology coverage data available.")
    with support_right:
        if not t2_df.empty:
            st.markdown("#### T2 Output Snapshot")
            st.dataframe(t2_df.head(15), use_container_width=True, hide_index=True, height=260)
        else:
            st.info("No T2 outputs available.")

    top_year = max(topic_scan["year_counts"].items(), key=lambda item: item[1])[0] if topic_scan["year_counts"] else "N/A"
    dominant_pillar = max(topic_scan["pillar_signals"].items(), key=lambda item: item[1])[0] if topic_scan["pillar_signals"] else "N/A"
    st.markdown("### Research Interpretation")
    st.markdown(
        f"""
1. The corpus scan covers **{len(doc_df):,} documents** and **{int(doc_df['pages'].sum()):,} pages**, which is sufficient for a dashboard-oriented topic modelling baseline over `data/thesis_dataset/`.
2. The strongest year concentration is **{top_year}**, which gives a practical anchor for temporal trend comparisons before moving to formal coherence-based topic estimation.
3. The dominant heuristic pillar signal is **{dominant_pillar}**, so any later LDA or BERTopic stage should be checked for pillar imbalance rather than assuming neutral theme distribution.
4. High `risk_score` documents combine stronger positive narrative density with weaker metric density, making them efficient candidates for manual audit, ABSA comparison, and later topic-cluster validation.
5. The combination of corpus heuristics, structured ESG records, ontology mappings, and stability summaries shows the adapted framework is operational now, even before adding formal coherence-score optimization or topic-number search.
"""
    )


def main() -> None:
    st.title("ESG ABSA Summarization Workspace")
    st.caption("Streamlit dashboard for ESG evidence summarization, stability checks, and research framing.")

    datasets, logs = load_datasets()

    with st.expander("Data Loading Log", expanded=False):
        for line in logs:
            st.write(f"- {line}")

    tabs = st.tabs([
        "Overview",
        "Dataset Profile",
        "Research Dashboard",
        "Topic Modelling Dashboard",
        "Pseudo Ground Truth",
        "LLM Judge",
        "Auto Summarization",
        "Record Explorer",
        "Stability",
        "Ontology",
        "Research Plan",
        "Research Notes",
        "Topic Modelling Research",
    ])

    with tabs[0]:
        render_overview(datasets)
    with tabs[1]:
        render_dataset_profile(datasets)
    with tabs[2]:
        render_database_research_dashboard(datasets)
    with tabs[3]:
        render_topic_modelling_research_dashboard(datasets)
    with tabs[4]:
        render_pseudo_ground_truth_lab(datasets)
    with tabs[5]:
        render_llm_judge_lab(datasets)
    with tabs[6]:
        render_automatic_summarization_analysis(datasets)
    with tabs[7]:
        render_record_explorer(datasets)
    with tabs[8]:
        render_stability(datasets)
    with tabs[9]:
        render_ontology(datasets)
    with tabs[10]:
        render_research_plan()
    with tabs[11]:
        render_research_notes()
    with tabs[12]:
        render_topic_modelling_research()


if __name__ == "__main__":
    main()
