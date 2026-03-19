# -*- coding: utf-8 -*-
"""
core/deep_model.py
Deep learning module (mBERT) for ESG ABSA:
 - Light-weight training loop for demo / explainability
 - Extracts attention-based token importances (simple first-layer/head averaging)
 - Returns CSV, DataFrame, matplotlib figure and an interpretability head table
 - Safe fallbacks if Transformers models cannot be loaded (e.g., offline or CPU-only)
"""

import os
import tempfile
from typing import Optional, Tuple, Dict, Any, List
import regex as re
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from .utils import parse_document, safe_plot
from .app_state import app_state

# Use transformers if available; otherwise provide graceful fallback
try:
    from transformers import BertTokenizer, BertModel
    _TRANSFORMERS_AVAILABLE = True
except Exception:
    _TRANSFORMERS_AVAILABLE = False

# Default model names
BERT_BASE = "bert-base-multilingual-cased"

DEVICE = torch.device("cpu")


# -------------------------
# Lightweight mBERT wrapper
# -------------------------
class SimpleDLModel(nn.Module):
    """
    Minimal mBERT-based model:
      - pooled BERT representation -> dropout -> two heads (sentiment, tone)
      - returns attentions if underlying model provides them
    """
    def __init__(self, base_model_name: str = BERT_BASE, hidden_dim: int = 768, tone_n: int = 4, sent_n: int = 3):
        super().__init__()
        self.base_model_name = base_model_name
        self.bert = None
        self.hidden_dim = hidden_dim
        # We'll load BertModel lazily (inside `init_base`), to allow graceful fallback
        if _TRANSFORMERS_AVAILABLE:
            try:
                self.bert = BertModel.from_pretrained(base_model_name, output_attentions=True)
                # if model has different hidden size, update hidden_dim accordingly
                self.hidden_dim = getattr(self.bert.config, "hidden_size", self.hidden_dim)
            except Exception as e:
                # fallback to None; we will use random embeddings if Bert unavailable
                self.bert = None

        # heads
        self.drop = nn.Dropout(0.2)
        self.sent_head = nn.Linear(self.hidden_dim, sent_n)
        self.tone_head = nn.Linear(self.hidden_dim, tone_n)

    def forward(self, ids: Optional[torch.Tensor], mask: Optional[torch.Tensor]):
        """
        If self.bert is available, run it and return (sent_logits, tone_logits, attentions).
        Otherwise, generate random embeddings for demo mode.
        """
        if self.bert is not None and ids is not None and mask is not None:
            out = self.bert(ids, attention_mask=mask, output_attentions=True, return_dict=True)
            pooled = out.pooler_output  # (B, hidden)
            pooled = self.drop(pooled)
            s = self.sent_head(pooled)
            t = self.tone_head(pooled)
            atts = out.attentions if hasattr(out, "attentions") else None
            return s, t, atts
        else:
            # demo / fallback: create deterministic "embeddings" from ids sum if possible
            if ids is None:
                # produce zeros
                B = 1
                pooled = torch.zeros(B, self.hidden_dim)
            else:
                B = ids.size(0)
                # simple embedding: sum of ids -> expand to hidden_dim with sin transform
                sums = ids.to(torch.float32).sum(dim=1).unsqueeze(1)  # (B,1)
                pooled = torch.sin(sums * (torch.arange(1, self.hidden_dim + 1, dtype=torch.float32).unsqueeze(0) * 0.01))
            pooled = self.drop(pooled)
            s = self.sent_head(pooled)
            t = self.tone_head(pooled)
            return s, t, None


# -------------------------
# Dataset helper
# -------------------------
class DLDataset(Dataset):
    def __init__(self, texts: List[str], sent_labels: List[int], tone_labels: List[int], tokenizer=None, max_len=64):
        self.texts = texts
        self.sent = sent_labels
        self.tone = tone_labels
        self.tok = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        t = self.texts[idx]
        if self.tok is not None:
            enc = self.tok(t, truncation=True, padding="max_length", max_length=self.max_len, return_tensors="pt")
            input_ids = enc["input_ids"].squeeze(0)
            att_mask = enc["attention_mask"].squeeze(0)
        else:
            # fallback: create numeric tokens from character ordinals
            toks = [ord(c) % 30522 for c in t[:self.max_len]]
            padding = [0] * (self.max_len - len(toks))
            input_ids = torch.tensor(toks + padding, dtype=torch.long)
            att_mask = torch.tensor([1] * len(toks) + [0] * len(padding), dtype=torch.long)
        return {
            "ids": input_ids,
            "mask": att_mask,
            "y_sent": torch.tensor(self.sent[idx], dtype=torch.long),
            "y_tone": torch.tensor(self.tone[idx], dtype=torch.long),
            "text": t
        }


# -------------------------
# Labels mapping
# -------------------------
def labels_for_dl(texts: List[str]):
    sent_map = {"Negative": 0, "Neutral": 1, "Positive": 2}
    tone_map = {"Commitment": 0, "Action": 1, "Outcome": 2, "Unknown": 3}
    # The above is intentionally compact but may be hard to read; simpler mapping below:
    sLabs = []
    tLabs = []
    for t in texts:
        # sentiment
        if re.search(r"(meningkat|improv|achiev|berhasil|improve|enhanc|strengthen|boost)", t, re.I):
            sLabs.append(2)
        elif re.search(r"(tantangan|krisis|risiko|turun|penurunan|decline|problem|shortage)", t, re.I):
            sLabs.append(0)
        else:
            sLabs.append(1)
        # tone
        if re.search(r"(telah|achieved|resulted|delivered|successfully|tercapai|mencapai)", t, re.I):
            tLabs.append(2)
        elif re.search(r"(melakukan|implement|adopt|launch|initiated|mengadopsi|menerapkan)", t, re.I):
            tLabs.append(1)
        elif re.search(r"(berkomitmen|commitment|we are committed|menargetkan|target|aim to)", t, re.I):
            tLabs.append(0)
        else:
            tLabs.append(3)
    return sLabs, tLabs


# -------------------------
# Main runner
# -------------------------
def run_deep_learning(raw_text: str, epochs: int = 1) -> Tuple[Optional[str], pd.DataFrame, object, pd.DataFrame]:
    """
    Run a light-weight deep learning demo:
      - parse text
      - prepare labels (weak labels)
      - build small DataLoader
      - train for `epochs` (default=1) on CPU
      - collect attention weights (if available)
      - return csv path, dataframe, matplotlib figure, and an interpretability dataframe

    Safe even when Transformers isn't available.
    """
    sents = parse_document(raw_text)
    if not sents:
        empty = pd.DataFrame()
        fig = safe_plot(lambda ax: (ax.text(0.5, 0.5, "No data", ha="center"), ax.axis("off")), "Deep Learning")
        app_state["deep"] = None
        return None, empty, fig, empty

    texts = [s.text for s in sents]
    sLabs, tLabs = labels_for_dl(texts)

    # Load tokenizer if available
    tokenizer = None
    if _TRANSFORMERS_AVAILABLE:
        try:
            tokenizer = BertTokenizer.from_pretrained(BERT_BASE)
        except Exception:
            tokenizer = None

    ds = DLDataset(texts, sLabs, tLabs, tokenizer=tokenizer, max_len=64)
    dl = DataLoader(ds, batch_size=4, shuffle=True)

    # build model
    model = SimpleDLModel(base_model_name=BERT_BASE)
    model = model.to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-5)
    ce = nn.CrossEntropyLoss()

    # train loop (very light)
    model.train()
    for epoch in range(max(1, int(epochs))):
        for batch in dl:
            ids = batch["ids"].to(DEVICE)
            mask = batch["mask"].to(DEVICE)
            ys = batch["y_sent"].to(DEVICE)
            yt = batch["y_tone"].to(DEVICE)
            opt.zero_grad()
            ls, lt, _ = model(ids, mask)
            loss = ce(ls, ys) + 0.5 * ce(lt, yt)
            loss.backward()
            opt.step()

    # inference & attention extraction
    model.eval()
    preds_sent = []
    preds_tone = []
    token_attentions: Dict[int, Dict[str, Any]] = {}
    sample_idx = 0
    with torch.no_grad():
        for batch in DataLoader(ds, batch_size=4, shuffle=False):
            ids = batch["ids"].to(DEVICE)
            mask = batch["mask"].to(DEVICE)
            texts_b = batch["text"]
            ls, lt, atts = model(ids, mask)
            ps = torch.argmax(ls, dim=1).cpu().numpy()
            pt = torch.argmax(lt, dim=1).cpu().numpy()
            preds_sent.extend(ps.tolist())
            preds_tone.extend(pt.tolist())

            # attentions: if provided, average heads & average query positions to get per-token weight
            if atts is not None and len(atts) > 0:
                # atts is tuple(list) of layers: each tensor (B, heads, seq, seq)
                try:
                    layer0 = atts[0].cpu().numpy()  # shape (B, heads, seq, seq)
                    head_avg = layer0.mean(axis=1).mean(axis=1)  # (B, seq)
                except Exception:
                    head_avg = None
            else:
                head_avg = None

            for bi in range(len(texts_b)):
                toks = None
                weights = None
                if tokenizer is not None:
                    # convert ids to tokens
                    raw_ids = ids[bi].cpu().tolist()
                    toks = tokenizer.convert_ids_to_tokens(raw_ids)
                else:
                    # simple char-based tokens
                    toks = list(texts_b[bi])[:64]
                if head_avg is not None:
                    w = head_avg[bi]
                    # mask pads if mask present
                    att_mask = batch["mask"][bi].cpu().numpy()
                    w = w * att_mask
                    if w.sum() > 0:
                        w = w / w.sum()
                    weights = w.tolist()
                else:
                    # fallback: uniform weights on non-pad tokens
                    att_mask = batch["mask"][bi].cpu().numpy()
                    nonzero = att_mask.sum()
                    if nonzero > 0:
                        weights = (att_mask / nonzero).tolist()
                    else:
                        weights = [1.0 / max(1, len(toks))] * len(toks)

                token_attentions[sample_idx] = {"tokens": toks, "weights": weights, "text": texts_b[bi]}
                sample_idx += 1

    # map preds to labels
    sent_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
    tone_map = {0: "Commitment", 1: "Action", 2: "Outcome", 3: "Unknown"}

    sent_labels = [sent_map.get(int(i), "Neutral") for i in preds_sent]
    tone_labels = [tone_map.get(int(i), "Unknown") for i in preds_tone]

    # build result df + CSV
    rows = []
    for i, s in enumerate(sents):
        toks_entry = token_attentions.get(i, {"tokens": [], "weights": []})
        top_tokens = ", ".join([t for t in toks_entry.get("tokens", []) if t not in ["[PAD]", "[CLS]", "[SEP]"]][:8])
        rows.append({
            "Sentence_ID": s.idx,
            "Sentence_Text": s.text,
            "Predicted_Sentiment": sent_labels[i] if i < len(sent_labels) else "Neutral",
            "Predicted_Tone": tone_labels[i] if i < len(tone_labels) else "Unknown",
            "TopTokens_Attention": top_tokens
        })

    df = pd.DataFrame(rows)
    out_csv = os.path.join(tempfile.gettempdir(), "esg_deeplearning_outputs.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # Persist deep artifacts to shared state
    app_state["deep"] = {"df": df, "token_att": token_attentions, "csv": out_csv, "tokenizer": (tokenizer if tokenizer is not None else None), "model": model}

    # quick plot: distribution of predicted sentiments (matplotlib)
    def _plot(ax):
        if df.empty:
            ax.text(0.5, 0.5, "No data", ha="center")
            ax.axis("off")
            return
        df["Predicted_Sentiment"].value_counts().plot(kind="bar", ax=ax)
        ax.set_ylabel("Count")

    fig = safe_plot(_plot, "Deep Learning: Sentiment Predictions")
    interp_df = df[["Sentence_Text", "TopTokens_Attention"]].head(8)

    return out_csv, df, fig, interp_df


# -------------------------
# Explain helper
# -------------------------
def explain_deep_sentence(sentence_text: str, sentence_idx: Optional[int] = None):
    """
    Find the matching sentence in app_state['deep'] token_att (by text or index) and return tokens + weights.
    """
    state = app_state.get("deep")
    if not state:
        return {"error": "Deep model not run yet."}
    token_att = state.get("token_att", {})
    # match by provided index
    if sentence_idx is not None and sentence_idx in token_att:
        return {"tokens": token_att[sentence_idx]["tokens"], "weights": token_att[sentence_idx]["weights"]}

    # match by text
    for k, v in token_att.items():
        if v.get("text") and v["text"].strip() == sentence_text.strip():
            return {"tokens": v["tokens"], "weights": v["weights"]}

    # fallback to first
    if not token_att:
        return {"error": "No token attention available."}
    first_k = next(iter(token_att))
    return {"tokens": token_att[first_k]["tokens"], "weights": token_att[first_k]["weights"]}


# -------------------------
# Plotly helper
# -------------------------
def plot_attention_plotly(tokens: List[str], weights: List[float], title: str = "Attention"):
    """
    Build a small Plotly heatmap-like visual where x = tokens and z = weights.
    Returns a plotly.graph_objects.Figure.
    """
    try:
        import plotly.graph_objects as go
        toks = [t for t in tokens if t not in ["[PAD]"]]
        w = weights[:len(toks)]
        fig = go.Figure(data=go.Heatmap(z=[w], x=toks, y=["attention"], colorscale="Viridis"))
        fig.update_layout(title=title, height=260, margin=dict(l=10, r=10, t=30, b=10))
        return fig
    except Exception as e:
        # if Plotly not available, return None
        return None