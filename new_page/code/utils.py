# -*- coding: utf-8 -*-
"""
core/utils.py
Utility functions and shared data structures for the ESG ABSA framework.
Includes text parsing, language detection, and safe plotting helpers.
"""

import regex as re
import os
from dataclasses import dataclass
from typing import List
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ======================
# Data Structure
# ======================

@dataclass
class Sentence:
    """Represents a parsed sentence with metadata."""
    text: str
    idx: int
    section: str
    section_type: str
    lang: str


# ======================
# Section Mapping
# ======================

SECTION_MAP = {
    "TANTANGAN DAN RESPONS TERHADAP ISU KEBERLANJUTAN": "General",
    "KINERJA EKONOMI": "Economic",
    "KINERJA LINGKUNGAN": "Environmental",
    "KINERJA SOSIAL": "Social",
    "TATA KELOLA": "Governance",
    "STRATEGI KEBERLANJUTAN": "Strategy",
}


# ======================
# Item Marker Handling
# ======================

ITEM_MARKER_PATTERN = r"(?:\(?\d{1,3}\)|\([A-Za-z]\)|[A-Za-z]\))"
ITEM_BOUNDARY_RE = re.compile(
    rf"(?m)(?:(?<=^)|(?<=[\n;:]))\s*{ITEM_MARKER_PATTERN}\s+"
)
LEADING_ITEM_MARKER_RE = re.compile(rf"^\s*{ITEM_MARKER_PATTERN}\s+")


# ======================
# Language Detection
# ======================

def detect_lang(s: str) -> str:
    """
    Detects whether the sentence is more likely Indonesian ('id') or English ('en')
    using basic lexical cues.
    """
    if re.search(r"\b(we|our|the|and|of|to|in|a|on)\b", s.lower()):
        if re.search(r"\b(kami|yang|untuk|dan|dengan|pada|di|ke)\b", s.lower()):
            return "id"
        return "en"
    return "id"


# ======================
# Parsing Logic
# ======================

def parse_document(raw: str) -> List[Sentence]:
    """
    Parses a raw ESG report text into structured sentence objects.

    Each sentence is tagged with:
      - section title (from '## ' headers if available)
      - section type (Economic, Social, etc.)
      - detected language ('en' or 'id')
    """
    blocks = re.split(r"\n(?=## )", raw.strip()) if "## " in raw else [raw]
    sentences = []
    sid = 0

    for block in blocks:
        if "## " in block:
            m = re.match(r"## ([^\n]+)\n?(.*)", block, flags=re.S)
            if m:
                header = m.group(1).strip()
                body = (m.group(2) or "").strip()
            else:
                header, body = "General", block
        else:
            header, body = "General", block

        section_type = SECTION_MAP.get(header.upper(), "General")

        # Split into sentences and itemized fragments.
        # Supports markers such as 1), (1), a), and (a) at item boundaries.
        body = ITEM_BOUNDARY_RE.sub("\n", body)
        parts = re.split(r"(?<=[\.\?!])\s+(?=[A-ZÀ-ÿK])|[\n•\-;]", body)
        for part in parts:
            text = LEADING_ITEM_MARKER_RE.sub("", (part or "").strip()).strip()
            if len(text) < 4:
                continue
            sentences.append(Sentence(text, sid, header, section_type, detect_lang(text)))
            sid += 1

    return sentences


# ======================
# Safe Plotting
# ======================

def safe_plot(plot_fn, title: str):
    """
    Safely generates matplotlib figures, even if the plotting function fails.

    Args:
        plot_fn (callable): A function that takes one argument (the matplotlib axis)
        title (str): The title for the figure

    Returns:
        matplotlib.figure.Figure
    """
    try:
        fig = plt.figure(figsize=(6, 4))
        ax = plt.gca()
        plot_fn(ax)
        plt.title(title)
        plt.tight_layout()
        return fig
    except Exception as e:
        fig = plt.figure(figsize=(4, 2))
        plt.text(0.5, 0.5, f"Plot error: {e}", ha="center", va="center")
        plt.axis("off")
        return fig
