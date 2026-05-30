from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


@dataclass(frozen=True)
class LabelVocab:
    aspect2id: Dict[str, int]
    sentiment2id: Dict[str, int]
    tone2id: Optional[Dict[str, int]] = None

    @property
    def id2aspect(self) -> Dict[int, str]:
        return {v: k for k, v in self.aspect2id.items()}

    @property
    def id2sentiment(self) -> Dict[int, str]:
        return {v: k for k, v in self.sentiment2id.items()}

    @property
    def id2tone(self) -> Dict[int, str]:
        if not self.tone2id:
            return {}
        return {v: k for k, v in self.tone2id.items()}


class MultiHeadAbsaModel(nn.Module):
    """
    Simple multi-task classifier:
      - shared transformer encoder
      - heads for aspect & sentiment
      - optional head for tone
    """

    def __init__(
        self,
        base_model_name: str,
        n_aspects: int,
        n_sentiments: int,
        n_tones: int = 0,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.base_model_name = base_model_name
        self.encoder = AutoModel.from_pretrained(base_model_name)
        hidden = getattr(self.encoder.config, "hidden_size", None)
        if hidden is None:
            raise ValueError("Encoder config has no hidden_size")

        self.dropout = nn.Dropout(dropout)
        self.aspect_head = nn.Linear(hidden, n_aspects)
        self.sentiment_head = nn.Linear(hidden, n_sentiments)
        self.tone_head = nn.Linear(hidden, n_tones) if n_tones > 0 else None

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Dict[str, torch.Tensor]:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # Use [CLS] pooler if present, else first token.
        pooled = getattr(out, "pooler_output", None)
        if pooled is None:
            pooled = out.last_hidden_state[:, 0, :]
        pooled = self.dropout(pooled)
        logits = {
            "aspect": self.aspect_head(pooled),
            "sentiment": self.sentiment_head(pooled),
        }
        if self.tone_head is not None:
            logits["tone"] = self.tone_head(pooled)
        return logits


def load_tokenizer(model_name: str):
    return AutoTokenizer.from_pretrained(model_name, use_fast=True)

