# -*- coding: utf-8 -*-
"""
core/hybrid_model.py
Hierarchical encoder + MTL Hybrid model (Hybrid++) for ESG ABSA.

This module is CPU-friendly and robust:
 - Uses a small transformer (DistilBERT) when available for sentence encoding.
 - Falls back to deterministic embeddings when transformers are not available.
 - Provides HierarchicalEncoder, MTLHybrid, and a run_hierarchical_hybrid() function
   which returns CSV, dataframe, matplotlib figures, and metrics.
 - Persists artifacts into core.app_state.app_state["hybrid"] for explainability.
"""

import os
import tempfile
from collections import defaultdict
from typing import List, Tuple, Optional
import regex as re
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from .utils import parse_document, safe_plot
from .lexicons import ASPECT_LEX, CANON_PATHS, any_match
from .app_state import app_state
from .rule_based import polarity_basic, tone_basic

# Try to import transformers (distilbert) if available
try:
    from transformers import AutoTokenizer, AutoModel
    _TRANSFORMERS_AVAILABLE = True
except Exception:
    _TRANSFORMERS_AVAILABLE = False

# default small encoder
HF_SMALL = "distilbert-base-multilingual-cased"
DEVICE = torch.device("cpu")


# -------------------------
# Encoder util (small)
# -------------------------
_tokenizer_small = None
_model_small = None
_hidden_size = 768

if _TRANSFORMERS_AVAILABLE:
    try:
        _tokenizer_small = AutoTokenizer.from_pretrained(HF_SMALL)
        _model_small = AutoModel.from_pretrained(HF_SMALL)
        _model_small.to(DEVICE)
        _model_small.eval()
        _hidden_size = getattr(_model_small.config, "hidden_size", _hidden_size)
        # freeze weights by default for fast training
        for p in _model_small.parameters():
            p.requires_grad = False
    except Exception:
        _tokenizer_small = None
        _model_small = None
        _hidden_size = 768


def encode_texts_small(texts: List[str], max_len: int = 96, batch: int = 8) -> torch.Tensor:
    """
    Encode a list of sentences to sentence vectors (N x hidden).
    Uses _model_small if available (DistilBERT); otherwise fallback deterministic vectors.
    """
    if _model_small is not None and _tokenizer_small is not None:
        embs = []
        with torch.no_grad():
            for i in range(0, len(texts), batch):
                chunk = texts[i:i + batch]
                enc = _tokenizer_small(chunk, truncation=True, padding=True, max_length=max_len, return_tensors="pt")
                enc = {k: v.to(DEVICE) for k, v in enc.items()}
                out = _model_small(**enc)
                # use mean pooling of last_hidden_state w.r.t attention mask
                last = out.last_hidden_state  # (B, seq, hidden)
                mask = enc["attention_mask"].unsqueeze(-1)  # (B, seq, 1)
                pooled = (last * mask).sum(1) / mask.sum(1).clamp(min=1)
                embs.append(pooled.cpu())
        if embs:
            return torch.cat(embs, dim=0)
        else:
            return torch.zeros(0, _hidden_size)
    else:
        # deterministic fallback: use simple char-based embedding
        embs = []
        for t in texts:
            arr = np.frombuffer(t.encode("utf-8", errors="ignore")[:max_len].ljust(max_len, b"\0"), dtype=np.uint8).astype(np.float32)
            # project to hidden size (repeat/truncate)
            if arr.size < _hidden_size:
                rep = np.pad(arr, (0, _hidden_size - arr.size))
            else:
                rep = arr[:_hidden_size]
            # simple scaling
            rep = (rep - rep.mean()) / (rep.std() + 1e-6)
            embs.append(rep)
        if embs:
            return torch.tensor(np.vstack(embs), dtype=torch.float32)
        else:
            return torch.zeros(0, _hidden_size)


# -------------------------
# Ontology nodes
# -------------------------
ONTO_NODES_FULL = sorted(set(ASPECT_LEX.keys()))


# -------------------------
# Hierarchical Encoder (light)
# -------------------------
class HierarchicalEncoder(nn.Module):
    """
    Simple hierarchical encoder:
      - section-type embeddings
      - for each section compute a pooled representation
      - produce per-sentence contextualized vector and document vector
    """
    def __init__(self, hidden: int = None, sec_types: Optional[List[str]] = None):
        super().__init__()
        h = hidden or _hidden_size
        self.hidden = h
        self.sec_types = sorted(set(sec_types or ["General"]))
        self.sec_type2id = {t: i for i, t in enumerate(self.sec_types)}
        self.sec_type_emb = nn.Embedding(len(self.sec_type2id), h)
        self.proj = nn.Linear(h, h)
        # Use a lightweight MultiheadAttention for section cross-talk
        self.cross = nn.MultiheadAttention(embed_dim=h, num_heads=4, batch_first=True)

    def forward(self, sent_vecs: torch.Tensor, sections: List[str], sec_types: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            sent_vecs: (N, hidden)
            sections: list of N section names (strings)
            sec_types: list of N section type names (strings)
        Returns:
            per_sentence_vectors: (N, hidden)
            doc_vector: (hidden,)
        """
        if sent_vecs.numel() == 0:
            return torch.zeros(0, self.hidden), torch.zeros(self.hidden)

        by_sec = defaultdict(list)
        for i, sec in enumerate(sections):
            by_sec[sec].append(i)

        per_sentence = torch.zeros_like(sent_vecs)
        sec_vecs = []
        for sec, idxs in by_sec.items():
            idxs = list(idxs)
            pool = sent_vecs[idxs].mean(dim=0)  # (hidden,)
            st = sec_types[idxs[0]] if idxs else "General"
            st_id = torch.tensor(self.sec_type2id.get(st, 0), dtype=torch.long)
            st_emb = self.sec_type_emb(st_id).to(sent_vecs.device)
            v = self.proj(pool + st_emb)
            sec_vecs.append(v)
            for i in idxs:
                per_sentence[i] = v

        if sec_vecs:
            m = torch.stack(sec_vecs, dim=0).unsqueeze(0)  # (1, S, hidden)
            attn_out, _ = self.cross(m, m, m)  # (1, S, hidden)
            doc_vec = attn_out.mean(dim=1).squeeze(0)  # (hidden,)
        else:
            doc_vec = torch.zeros(self.hidden)

        return per_sentence, doc_vec


# -------------------------
# MTL Hybrid model
# -------------------------
class MTLHybrid(nn.Module):
    """
    Fuse sentence vector (sv), section vector (cv), ontology vector (ov), doc vector (dv)
    and predict sentiment and tone.
    """
    def __init__(self, hidden: int = None, onto_dim: int = 64):
        super().__init__()
        h = hidden or _hidden_size
        self.hidden = h
        self.onto_emb = nn.Embedding(len(ONTO_NODES_FULL) + 1, onto_dim)
        self.onto_proj = nn.Linear(onto_dim, h)
        self.fuse = nn.Sequential(
            nn.Linear(h * 4, h),
            nn.Tanh(),
            nn.Dropout(0.2)
        )
        self.sent_head = nn.Linear(h, 3)
        self.tone_head = nn.Linear(h, 4)

    def forward(self, sv: torch.Tensor, cv: torch.Tensor, ov: torch.Tensor, dv: torch.Tensor):
        """
        sv: (N, h) sentence vectors
        cv: (N, h) section vectors (per sentence)
        ov: (N, h) ontology projected vectors
        dv: (h,) or (1, h) document vector
        """
        if dv.dim() == 1:
            dv = dv.unsqueeze(0)  # (1, h)
        dv_expanded = dv.repeat(sv.shape[0], 1)
        z = torch.cat([sv, cv, ov, dv_expanded], dim=1)  # (N, h*4)
        hz = self.fuse(z)
        return self.sent_head(hz), self.tone_head(hz), hz


# -------------------------
# Helpers to create ontology vectors
# -------------------------
def make_ontology_vectors(aspect_lists: List[List[str]], model: Optional[MTLHybrid] = None) -> torch.Tensor:
    """
    Given list of aspect lists per sentence, produce projected ontology vectors (N, hidden).
    If an aspect not found -> use the last index (padding id).
    """
    if model is None:
        # create a lightweight projection (random init) to avoid dependency
        temp_model = MTLHybrid(hidden=_hidden_size, onto_dim=64)
    else:
        temp_model = model

    node2id = {n: i for i, n in enumerate(ONTO_NODES_FULL)}
    embeds = []
    for lst in aspect_lists:
        ids = [node2id.get(a, len(ONTO_NODES_FULL)) for a in (lst or ["General"])]
        ids_t = torch.tensor(ids, dtype=torch.long)
        with torch.no_grad():
            e = temp_model.onto_emb(ids_t).mean(dim=0)  # (onto_dim,)
            proj = temp_model.onto_proj(e)  # (hidden,)
        embeds.append(proj)
    if embeds:
        return torch.stack(embeds, dim=0)
    else:
        return torch.zeros(0, _hidden_size)


# -------------------------
# Main runner
# -------------------------
def run_hierarchical_hybrid(raw_text: str, epochs: int = 1, tone_weight: float = 1.5, align_weight: float = 0.2):
    """
    Full pipeline:
      - parse -> sentences, sections
      - encode sentences (encode_texts_small)
      - hierarchical encoder -> section vectors + doc vector
      - make ontology vectors from aspects
      - prepare weak labels (polarity/tone)
      - train MTLHybrid (very light)
      - inference -> build df, metrics, plots
    Returns: out_csv, df, fig1, fig2, fig3, metrics_df
    """
    sents = parse_document(raw_text)
    if not sents:
        empty = pd.DataFrame()
        fig = safe_plot(lambda ax: (ax.text(0.5, 0.5, "No data", ha="center"), ax.axis("off")), "Hybrid++")
        app_state["hybrid"] = None
        return None, empty, fig, fig, fig, empty

    texts = [s.text for s in sents]
    sections = [s.section for s in sents]
    sec_types = [s.section_type for s in sents]
    aspects = []
    for t in texts:
        # collect aspects using ASPECT_LEX (simple helper)
        found = [a for a, pats in ASPECT_LEX.items() if any_match(pats, t)]
        aspects.append(found or ["General"])
    onto_paths = ["; ".join([CANON_PATHS.get(a, "General → Misc") for a in lst]) for lst in aspects]

    # encode
    sent_vecs = encode_texts_small(texts)  # tensor (N, hidden)
    if isinstance(sent_vecs, np.ndarray):
        sent_vecs = torch.tensor(sent_vecs, dtype=torch.float32)
    if sent_vecs.dim() == 1:
        sent_vecs = sent_vecs.unsqueeze(0)

    hier = HierarchicalEncoder(hidden=_hidden_size, sec_types=list(set(sec_types)))
    sec_vecs, doc_vec = hier.forward(sent_vecs, sections, sec_types)  # sec_vecs (N, h), doc_vec (h,)

    model = MTLHybrid(hidden=_hidden_size, onto_dim=64)
    # onto vectors (N, hidden)
    onto_vecs = make_ontology_vectors(aspects, model)

    # prepare targets (weak labeling using simple heuristics)
    sent_map = {"Negative": 0, "Neutral": 1, "Positive": 2}
    tone_map = {"Commitment": 0, "Action": 1, "Outcome": 2, "Unknown": 3}
    sent_y = torch.tensor([sent_map.get(
        ("Positive" if re.search(r"(meningkat|improv|achiev|berhasil|improve|enhanc)", t, re.I) else
         ("Negative" if re.search(r"(tantangan|krisis|risiko|turun|penurunan|decline)", t, re.I) else "Neutral"))
    , None) for t in texts]).long()
    # Above is a compact but safe mapping; simplify below to be clear and robust:
    sent_y = []
    tone_y = []
    for t in texts:
        if re.search(r"(meningkat|improv|achiev|berhasil|improve|enhanc|strengthen|boost)", t, re.I):
            sent_y.append(2)
        elif re.search(r"(tantangan|krisis|risiko|turun|penurunan|decline|problem|shortage)", t, re.I):
            sent_y.append(0)
        else:
            sent_y.append(1)
        if re.search(r"(telah|achieved|resulted|delivered|successfully|tercapai|mencapai)", t, re.I):
            tone_y.append(2)
        elif re.search(r"(melakukan|implement|adopt|launch|initiated|mengadopsi|menerapkan)", t, re.I):
            tone_y.append(1)
        elif re.search(r"(berkomitmen|commitment|we are committed|menargetkan|target|aim to)", t, re.I):
            tone_y.append(0)
        else:
            tone_y.append(3)
    sent_y = torch.tensor(sent_y, dtype=torch.long)
    tone_y = torch.tensor(tone_y, dtype=torch.long)

    # train MTLHybrid (light, CPU-friendly)
    model = model.to(DEVICE)
    ce = nn.CrossEntropyLoss()
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=3e-4)

    model.train()
    for _ in range(max(1, int(epochs))):
        opt.zero_grad()
        sent_pred, tone_pred, _ = model(sent_vecs, sec_vecs, onto_vecs, doc_vec)
        loss = ce(sent_pred, sent_y) + tone_weight * ce(tone_pred, tone_y)
        # alignment loss: cosine between sent_vecs and onto_vecs
        cos = torch.cosine_similarity(sent_vecs, onto_vecs, dim=1)
        loss = loss + align_weight * (1.0 - cos.mean())
        loss.backward()
        opt.step()

    # inference
    model.eval()
    with torch.no_grad():
        sent_pred_final, tone_pred_final, _ = model(sent_vecs, sec_vecs, onto_vecs, doc_vec)
        ps = sent_pred_final.argmax(dim=1).cpu().numpy()
        pt = tone_pred_final.argmax(dim=1).cpu().numpy()
        align_arr = torch.cosine_similarity(sent_vecs, onto_vecs, dim=1).cpu().numpy()

    sent_map_inv = {0: "Negative", 1: "Neutral", 2: "Positive"}
    tone_map_inv = {0: "Commitment", 1: "Action", 2: "Outcome", 3: "Unknown"}

    df = pd.DataFrame({
        "Sentence_ID": [s.idx for s in sents],
        "Section": sections,
        "Section_Type": sec_types,
        "Sentence_Text": texts,
        "Sentiment_Pred": [sent_map_inv.get(int(x), "Neutral") for x in ps],
        "Tone_Pred": [tone_map_inv.get(int(x), "Unknown") for x in pt],
        "Ontology_Alignment": align_arr,
        "Ontology_Path": onto_paths
    })

    # Metrics
    ont_consistency = float((df["Ontology_Path"] != "General → Misc").mean())
    s_map_val = {"Negative": -1, "Neutral": 0, "Positive": 1}
    commit_vals = df[df["Tone_Pred"] == "Commitment"]["Sentiment_Pred"].map(s_map_val).dropna().values
    outcome_vals = df[df["Tone_Pred"] == "Outcome"]["Sentiment_Pred"].map(s_map_val).dropna().values
    commit = float(commit_vals.mean()) if commit_vals.size > 0 else 0.0
    outcome = float(outcome_vals.mean()) if outcome_vals.size > 0 else 1e-6
    gdi = commit / (outcome if abs(outcome) > 1e-6 else 1e-6)

    metrics = pd.DataFrame([
        ["Ontology Consistency", round(ont_consistency, 4)],
        ["Greenwashing Index", round(float(gdi), 4)],
        ["N Sentences", len(df)],
        ["Sections", df["Section"].nunique()]
    ], columns=["Metric", "Value"])

    # prediction scores (softmax confidence)
    with torch.no_grad():
        s_scores = sent_pred_final.softmax(dim=1).max(dim=1).values.cpu().numpy()
        t_scores = tone_pred_final.softmax(dim=1).max(dim=1).values.cpu().numpy()

    df["sentiment_pred"] = ps
    df["sentiment_score"] = s_scores
    df["tone_pred"] = pt
    df["tone_score"] = t_scores

    out_csv = os.path.join(tempfile.gettempdir(), "esg_hier_mtl_hybrid.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # persist artifacts for explainability
    app_state["hybrid"] = {
        "df": df,
        "sent_vecs": sent_vecs.detach().cpu().numpy(),
        "onto_vecs": onto_vecs.detach().cpu().numpy() if isinstance(onto_vecs, torch.Tensor) else onto_vecs,
        "sections": sections,
        "csv": out_csv,
        "model": model
    }

    # Visualizations using safe_plot + plotly for scatter helper
    def plot_tone_sent(ax):
        if df.empty:
            ax.text(0.5, 0.5, "No data", ha="center")
            ax.axis("off")
        else:
            pd.crosstab(df["Tone_Pred"], df["Sentiment_Pred"]).plot(kind="bar", stacked=True, ax=ax)
            ax.set_ylabel("Count")

    def plot_align(ax):
        if df.empty:
            ax.text(0.5, 0.5, "No sentences", ha="center")
            ax.axis("off")
        else:
            ax.hist(df["Ontology_Alignment"], bins=10)
            ax.set_xlabel("Cosine Similarity")

    def plot_sec(ax):
        if df.empty or df["Section"].nunique() == 0:
            ax.text(0.5, 0.5, "No sections", ha="center")
            ax.axis("off")
        else:
            pd.crosstab(df["Section"], df["Tone_Pred"]).plot(kind="bar", ax=ax, rot=45)
            ax.set_ylabel("Count")

    fig1 = safe_plot(plot_tone_sent, "Tone × Sentiment")
    fig2 = safe_plot(plot_align, "Ontology Alignment (cosine)")
    fig3 = safe_plot(plot_sec, "Tone Distribution by Section")

    return out_csv, df, fig1, fig2, fig3, metrics


# -------------------------
# Explain helpers
# -------------------------
def explain_hybrid_sentence(sentence_text: str):
    state = app_state.get("hybrid")
    if not state:
        return {"error": "Hybrid model not run yet."}
    df = state.get("df", pd.DataFrame())
    if df.empty:
        return {"error": "Hybrid model has no sentences."}

    # match by exact text (strip)
    row = df[df["Sentence_Text"].str.strip() == sentence_text.strip()]
    if row.empty:
        row = df.head(1)
    if row.empty:
        return {"error": "Hybrid model has no sentences."}

    align = float(row["Ontology_Alignment"].iloc[0])
    section = row["Section"].iloc[0]
    onto_path = row["Ontology_Path"].iloc[0]

    sections = state.get("sections", [])
    sent_vecs = state.get("sent_vecs", np.zeros((0, _hidden_size)))
    sec_influence = {}
    for i, sec in enumerate(sections):
        sec_influence.setdefault(sec, []).append(float(np.linalg.norm(sent_vecs[i])) if i < len(sent_vecs) else 0.0)
    sec_summary = {k: float(np.mean(v)) for k, v in sec_influence.items()}
    influence_score = sec_summary.get(section, 0.0)

    return {
        "ontology_alignment": align,
        "section_influence": influence_score,
        "section_name": section,
        "ontology_path": onto_path
    }


def plot_ontology_scatter(state: dict):
    """
    Build a Plotly scatter of sentence embeddings (PCA -> 2D) colored by alignment,
    with overlayed ontology node positions.
    """
    try:
        import plotly.express as px
        import plotly.graph_objects as go
    except Exception:
        return None

    df = state.get("df")
    sent_vecs = state.get("sent_vecs")
    onto_vecs = state.get("onto_vecs")
    if df is None or sent_vecs is None or onto_vecs is None:
        return None

    sent_vecs = np.asarray(sent_vecs)
    onto_vecs = np.asarray(onto_vecs)
    # PCA to 2D
    from sklearn.decomposition import PCA
    all_emb = np.vstack([sent_vecs, onto_vecs])
    pca = PCA(n_components=2)
    proj = pca.fit_transform(all_emb)
    sN = sent_vecs.shape[0]
    sent_proj = proj[:sN]
    onto_proj = proj[sN:]

    px_df = pd.DataFrame(sent_proj, columns=["x", "y"])
    px_df["text"] = df["Sentence_Text"].values
    px_df["alignment"] = df["Ontology_Alignment"].values
    fig = px.scatter(px_df, x="x", y="y", color="alignment", hover_data=["text"],
                     title="Sentence embeddings (PCA) colored by ontology alignment")
    # add ontology nodes (limit to first 30 for clarity)
    for i, onto in enumerate(ONTO_NODES_FULL[:min(30, len(ONTO_NODES_FULL))]):
        fig.add_trace(go.Scatter(x=[onto_proj[i, 0]], y=[onto_proj[i, 1]], mode="markers+text",
                                 marker=dict(symbol="x", size=8), text=[onto], textposition="top center", showlegend=False))
    return fig