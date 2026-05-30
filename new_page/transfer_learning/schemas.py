from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_SENTIMENTS: Tuple[str, ...] = ("Negative", "Neutral", "Positive")
DEFAULT_TONES: Tuple[str, ...] = ("Commitment", "Action", "Outcome", "Unknown")


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = " ".join(text.split())
    return text.strip()


def normalize_sentiment(label: Any) -> str:
    """
    Normalize sentiment labels found in this repo (LLM outputs, baselines).
    Keeps a 3-class scheme by default: Negative/Neutral/Positive.
    """
    text = _clean_text(label).lower()
    if not text:
        return "Neutral"
    if text in {"neg", "negative", "negatif", "buruk", "down"}:
        return "Negative"
    if text in {"pos", "positive", "positif", "baik", "up"}:
        return "Positive"
    if text in {"neu", "neutral", "netral", "unknown", "na", "n/a"}:
        return "Neutral"
    # fallback: keep Neutral so we don't explode label space
    return "Neutral"


def normalize_tone(label: Any) -> str:
    text = _clean_text(label).lower()
    if not text:
        return "Unknown"
    if text in {"commitment", "komitmen"}:
        return "Commitment"
    if text in {"action", "aksi"}:
        return "Action"
    if text in {"outcome", "hasil", "result"}:
        return "Outcome"
    if text in {"unknown", "na", "n/a", "other"}:
        return "Unknown"
    return "Unknown"


def normalize_esg(label: Any) -> str:
    text = _clean_text(label).upper()
    if text in {"E", "ENV", "ENVIRONMENT", "ENVIRONMENTAL"}:
        return "E"
    if text in {"S", "SOC", "SOCIAL"}:
        return "S"
    if text in {"G", "GOV", "GOVERNANCE"}:
        return "G"
    return ""


@dataclass(frozen=True)
class AbsaExample:
    text: str
    aspect: str
    sentiment: str
    tone: str = "Unknown"
    esg: str = ""
    source: str = ""
    meta: Optional[Dict[str, Any]] = None

    def to_json(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "aspect": self.aspect,
            "sentiment": self.sentiment,
            "tone": self.tone,
            "esg": self.esg,
            "source": self.source,
            "meta": self.meta or {},
        }


def iter_llm_records(esg_records_payload: List[Dict[str, Any]]) -> Iterable[AbsaExample]:
    """
    Extract (text, aspect, sentiment, tone, esg) from `results/esg_records.json`.
    That file stores a list of jobs; each job may contain a `records` list with
    dict items shaped like:
      {'text','aspect','labels','esg','tone','sentiment','sentiment_score','reasoning'}
    """
    for job in esg_records_payload:
        records = job.get("records") or []
        if not isinstance(records, list):
            continue
        for rec in records:
            if not isinstance(rec, dict):
                continue
            text = _clean_text(rec.get("text"))
            aspect = _clean_text(rec.get("aspect"))
            if not text or not aspect:
                continue
            sentiment = normalize_sentiment(rec.get("sentiment"))
            tone = normalize_tone(rec.get("tone"))
            esg = normalize_esg(rec.get("esg"))
            meta = {
                "labels": rec.get("labels"),
                "sentiment_score": rec.get("sentiment_score"),
                "reasoning": rec.get("reasoning"),
                "job_model": job.get("model"),
                "job_target": job.get("target"),
                "job_background_id": job.get("background_job_id"),
            }
            yield AbsaExample(
                text=text,
                aspect=aspect,
                sentiment=sentiment,
                tone=tone,
                esg=esg,
                source="esg_records",
                meta=meta,
            )

