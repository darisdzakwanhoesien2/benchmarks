# -*- coding: utf-8 -*-
"""
core/rule_based.py
Rule-based RQ1–RQ3 pipeline for ESG ABSA.
Uses lexicons and utils to parse text, extract aspects, tone, polarity,
map to ontology paths, save CSV outputs, and produce a safe plot.
"""

import os
import regex as re
import tempfile
from collections import defaultdict
from typing import List, Dict

import pandas as pd

from .utils import parse_document, safe_plot
from .lexicons import ASPECT_LEX, CANON_PATHS, POS_WORDS, NEG_WORDS, COMMITMENT_MARK, ACTION_MARK, OUTCOME_MARK, any_match
from .app_state import app_state


# -------------------------
# Basic helpers (rule-based)
# -------------------------
def collect_aspects(text: str) -> List[str]:
    """Return list of aspect labels that match the sentence (uses ASPECT_LEX)."""
    labs = [label for label, pats in ASPECT_LEX.items() if any_match(pats, text)]
    return labs or ["General"]


def polarity_basic(text: str) -> str:
    """Simple polarity heuristic using POS_WORDS and NEG_WORDS."""
    pos = any_match(POS_WORDS, text)
    neg = any_match(NEG_WORDS, text)
    if pos and not neg:
        return "Positive"
    if neg and not pos:
        return "Negative"
    return "Neutral"


def tone_basic(text: str) -> str:
    """Simple tone categorization: Outcome > Action > Commitment > Unknown."""
    if any_match(OUTCOME_MARK, text):
        return "Outcome"
    if any_match(ACTION_MARK, text):
        return "Action"
    if any_match(COMMITMENT_MARK, text):
        return "Commitment"
    return "Unknown"


# -------------------------
# RQ-specific rule wrappers
# -------------------------
def rq1_sentence_only(sents: List) -> Dict[int, Dict]:
    out = {}
    for s in sents:
        out[s.idx] = {"aspect": collect_aspects(s.text), "sentiment": polarity_basic(s.text)}
    return out


def rq1_hierarchical(sents: List) -> Dict[int, Dict]:
    """Apply a simple section-aware correction (e.g., challenge sections may neutralize positive claims)."""
    out = {}
    by_sec = defaultdict(list)
    for s in sents:
        by_sec[s.section].append(s)
    for sec, group in by_sec.items():
        for s in group:
            base_sent = polarity_basic(s.text)
            # domain-specific correction example
            if "TANTANGAN" in sec.upper() and base_sent == "Positive":
                base_sent = "Neutral"
            out[s.idx] = {"aspect": collect_aspects(s.text), "sentiment": base_sent}
    return out


def rq2_tone_and_sentiment(sents: List) -> Dict[int, Dict]:
    out = {}
    for s in sents:
        t = tone_basic(s.text)
        sent = polarity_basic(s.text)
        # simple rules to combine tone + sentiment
        if t == "Commitment" and sent == "Positive":
            sent = "Neutral"
        elif t == "Action" and sent == "Neutral":
            sent = "Positive"
        out[s.idx] = {"aspect": collect_aspects(s.text), "sentiment": sent, "tone": t}
    return out


def rq3_ontology(preds: Dict[int, Dict], sents: List) -> Dict[int, Dict]:
    out = {}
    for s in sents:
        p = preds[s.idx]
        paths = [CANON_PATHS.get(a, "General → Misc") for a in p.get("aspect", [])]
        # copy and attach ontology paths
        entry = {"aspect": p.get("aspect", []), "sentiment": p.get("sentiment"), "tone": p.get("tone")}
        entry["ontology_paths"] = paths
        out[s.idx] = entry
    return out


# -------------------------
# Explain helper
# -------------------------
def explain_rule_based_sentence(sentence_text: str) -> List[str]:
    """
    Return a list of lexical triggers (short strings) that explain why the rule-based system
    picked certain aspects, tones, or polarity for the given sentence.
    """
    expl = []
    # aspects
    for aspect, pats in ASPECT_LEX.items():
        for p in pats:
            try:
                if re.search(p, sentence_text, re.I):
                    expl.append(f"Aspect '{aspect}' matched /{p}/")
            except re.error:
                # skip invalid regex pattern
                continue

    # polarity triggers
    for p in POS_WORDS:
        if re.search(p, sentence_text, re.I):
            expl.append(f"Positive trigger /{p}/")
    for p in NEG_WORDS:
        if re.search(p, sentence_text, re.I):
            expl.append(f"Negative trigger /{p}/")

    # tone triggers
    for p in COMMITMENT_MARK:
        if re.search(p, sentence_text, re.I):
            expl.append(f"Commitment trigger /{p}/")
    for p in ACTION_MARK:
        if re.search(p, sentence_text, re.I):
            expl.append(f"Action trigger /{p}/")
    for p in OUTCOME_MARK:
        if re.search(p, sentence_text, re.I):
            expl.append(f"Outcome trigger /{p}/")

    return expl or ["No explicit lexical triggers found."]


# -------------------------
# Main runner
# -------------------------
def run_rule_based(raw_text: str):
    """
    Run the full rule-based pipeline, persist CSV to temp folder, store artifacts in app_state,
    and return (csv_path, dataframe, matplotlib_figure).
    """
    sents = parse_document(raw_text)
    # RQ1 baseline / hierarchical
    pb = rq1_sentence_only(sents)
    ph = rq1_hierarchical(sents)
    pt = rq2_tone_and_sentiment(sents)
    po = rq3_ontology(ph, sents)

    rows = []
    for s in sents:
        b = pb.get(s.idx, {})
        h = ph.get(s.idx, {})
        t = pt.get(s.idx, {})
        o = po.get(s.idx, {})
        rows.append({
            "Sentence_ID": s.idx,
            "Section": s.section,
            "Section_Type": s.section_type,
            "Language": s.lang,
            "Sentence_Text": s.text,
            "RQ1_Baseline_Aspect": ", ".join(b.get("aspect", [])),
            "RQ1_Baseline_Sentiment": b.get("sentiment", ""),
            "RQ1_Hierarchical_Aspect": ", ".join(h.get("aspect", [])),
            "RQ1_Hierarchical_Sentiment": h.get("sentiment", ""),
            "RQ2_Tone": t.get("tone", ""),
            "RQ2_Sentiment": t.get("sentiment", ""),
            "RQ3_Ontology_Aspect": ", ".join(o.get("aspect", [])),
            "RQ3_Ontology_Path": "; ".join(o.get("ontology_paths", [])),
        })

    df = pd.DataFrame(rows)

    def _plot(ax):
        if df.empty:
            ax.text(0.5, 0.5, "No data", ha="center")
            ax.axis("off")
            return
        # compare baseline vs hierarchical sentiments
        melt = df.melt(value_vars=["RQ1_Baseline_Sentiment", "RQ1_Hierarchical_Sentiment"],
                       var_name="Model", value_name="Sentiment")
        (melt.groupby(["Model", "Sentiment"]).size()
             .unstack(fill_value=0).plot(kind="bar", ax=ax))
        ax.set_ylabel("Count")

    fig = safe_plot(_plot, "RQ1: Baseline vs Hierarchical (counts)")

    out_csv = os.path.join(tempfile.gettempdir(), "esg_rule_based_outputs.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # persist for explainability dashboard
    app_state["rule"] = {"df": df, "csv": out_csv}

    return out_csv, df, fig
