from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import pandas as pd
import streamlit as st

from task_data import BADGES, PHASES, get_tasks_for_phase

st.set_page_config(
    page_title="ESG Sustainability Report Analysis Framework",
    page_icon="📊",
    layout="wide",
)

st.title("ESG Sustainability Report Analysis - Complete Task Framework")
st.caption(
    "Adapted from parliamentary speech analysis for Indonesian listed company sustainability reports."
)

badge_cols = st.columns(len(BADGES))
for col, badge in zip(badge_cols, BADGES):
    col.markdown(f"`{badge}`")

st.divider()

st.subheader("Phase Overview")
for phase in PHASES:
    task_list = ", ".join(str(i) for i in phase["tasks"])
    st.markdown(f"- **{phase['title']}**: Tasks {task_list}")

st.divider()
st.subheader("Task Quick View")

for phase in PHASES:
    with st.container(border=True):
        st.markdown(f"### {phase['title']}")
        tasks = get_tasks_for_phase(phase["tasks"])
        for task in tasks:
            st.markdown(f"- **Task {task['id']}**: {task['title']}")
            st.caption(task["subtitle"])

st.divider()
st.subheader("Dataset-Wide Scan (All data/)")

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
THESIS_DATASET_DIR = DATA_DIR / "thesis_dataset"

PILLAR_KEYWORDS = {
    "E": {
        "emission",
        "co2",
        "carbon",
        "energy",
        "renewable",
        "waste",
        "water",
        "climate",
        "pollution",
        "biodiversity",
        "efisiensi",
        "lingkungan",
        "sampah",
        "air",
    },
    "S": {
        "employee",
        "training",
        "community",
        "health",
        "safety",
        "diversity",
        "labor",
        "inclusion",
        "human",
        "karyawan",
        "pelatihan",
        "masyarakat",
        "kesehatan",
        "keselamatan",
        "sosial",
    },
    "G": {
        "governance",
        "board",
        "audit",
        "risk",
        "compliance",
        "ethics",
        "policy",
        "anti",
        "corruption",
        "governansi",
        "dewan",
        "kepatuhan",
        "kebijakan",
        "pemegang",
    },
}

POSITIVE_CUES = {
    "improve",
    "improvement",
    "strong",
    "commitment",
    "sustainable",
    "success",
    "positive",
    "enhanced",
    "increased",
    "berkelanjutan",
    "komitmen",
    "peningkatan",
    "keberhasilan",
    "positif",
}

METRIC_CUES = {
    "ton",
    "tons",
    "%",
    "percent",
    "kwh",
    "mw",
    "gj",
    "tco2e",
    "m3",
    "mwh",
    "kg",
    "idr",
    "rp",
    "target",
    "baseline",
    "scope",
}

TOKEN_RE = re.compile(r"[A-Za-z]{2,}|")
YEAR_RE = re.compile(r"(20\d{2})")
NUM_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")
WORD_RE = re.compile(r"\b[a-z]{2,}\b")


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def _extract_year(name: str) -> str | None:
    years = YEAR_RE.findall(name)
    return years[-1] if years else None


def _dataset_signature(thesis_dataset_dir: Path) -> str:
    paths = sorted(thesis_dataset_dir.glob("*/ocr_result.json"))
    parts = []
    for p in paths:
        try:
            stat = p.stat()
            parts.append(f"{p.parent.name}:{stat.st_size}:{int(stat.st_mtime)}")
        except OSError:
            continue
    return "|".join(parts)


def _get_scan_state_key(prefix: str) -> str:
    return f"{prefix}_scan_state"


@st.cache_data(show_spinner=True)
def scan_all_data(data_dir: Path, signature: str) -> dict[str, object]:
    _ = signature
    ocr_paths = sorted(data_dir.glob("thesis_dataset/*/ocr_result.json"))

    rows = []
    sector_counts = Counter()
    year_counts = Counter()
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
        tokens = _tokenize(full_text)

        token_count = len(tokens)
        numeric_count = len(NUM_RE.findall(full_text))

        pillar_hits = {}
        for pillar, words in PILLAR_KEYWORDS.items():
            hits = sum(text_lower.count(w) for w in words)
            pillar_hits[pillar] = hits
            pillar_signal_counter[pillar] += hits

        pos_hits = sum(text_lower.count(w) for w in POSITIVE_CUES)
        metric_hits = sum(text_lower.count(w) for w in METRIC_CUES) + numeric_count

        if year:
            year_counts[year] += 1

        # Very lightweight heuristic sector extraction from folder name.
        dn = doc_name.lower()
        if any(k in dn for k in ("bank", "bni", "bri", "danamon", "permata", "aladin", "neo")):
            sector = "Financials"
        elif any(k in dn for k in ("waskita", "abm", "precast", "beton", "petrosea", "intraco")):
            sector = "Infrastructure/Industrial"
        elif any(k in dn for k in ("goto", "digital", "teknologi", "blibli", "superbank")):
            sector = "Technology/Digital"
        elif any(k in dn for k in ("health", "medik", "soho", "bmhs")):
            sector = "Healthcare"
        else:
            sector = "Other/Unmapped"
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

    df = pd.DataFrame(rows)
    if not df.empty:
        df["metric_per_1k_tokens"] = (df["metric_cues_total"] / df["tokens"].clip(lower=1)) * 1000
        df["positive_per_1k_tokens"] = (df["positive_cues_total"] / df["tokens"].clip(lower=1)) * 1000

    return {
        "ocr_paths": ocr_paths,
        "doc_df": df,
        "year_counts": dict(sorted(year_counts.items())),
        "sector_counts": dict(sector_counts),
        "top_tokens": top_tokens.most_common(30),
        "pillar_signals": dict(pillar_signal_counter),
    }


if THESIS_DATASET_DIR.exists():
    state_key = _get_scan_state_key("topic_modelling")
    if state_key not in st.session_state:
        st.session_state[state_key] = {"frozen": False, "result": None, "signature": None}
    scan_state: dict[str, Any] = st.session_state[state_key]

    controls = st.columns([1, 1, 1, 4])
    if controls[0].button("Refresh", use_container_width=True):
        st.cache_data.clear()
        scan_state["frozen"] = False
        scan_state["result"] = None
        scan_state["signature"] = None
        st.rerun()
    if controls[1].button("Freeze", use_container_width=True):
        scan_state["frozen"] = True
    if controls[2].button("Unfreeze", use_container_width=True):
        scan_state["frozen"] = False

    current_sig = _dataset_signature(THESIS_DATASET_DIR)
    if scan_state["frozen"] and scan_state["result"] is not None:
        result = scan_state["result"]
        used_sig = scan_state["signature"]
        st.caption("Mode: Frozen snapshot (analysis is pinned until unfreeze).")
    else:
        result = scan_all_data(DATA_DIR, current_sig)
        scan_state["result"] = result
        scan_state["signature"] = current_sig
        used_sig = current_sig
        st.caption("Mode: Auto-refresh on data change (reuses cache when unchanged).")

    st.caption(f"Dataset signature: `{hash(used_sig)}`")
    doc_df: pd.DataFrame = result["doc_df"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OCR Documents", f"{len(result['ocr_paths']):,}")
    c2.metric("Analyzed Documents", f"{len(doc_df):,}")
    c3.metric("Total Tokens", f"{int(doc_df['tokens'].sum()):,}" if not doc_df.empty else "0")
    c4.metric("Total Pages", f"{int(doc_df['pages'].sum()):,}" if not doc_df.empty else "0")

    if not doc_df.empty:
        st.markdown("**Coverage by Year**")
        year_df = pd.DataFrame(
            [{"year": k, "documents": v} for k, v in result["year_counts"].items()]
        )
        if not year_df.empty:
            st.bar_chart(year_df.set_index("year"))

        st.markdown("**Sector Proxy Distribution (folder-name heuristic)**")
        sector_df = pd.DataFrame(
            [{"sector": k, "documents": v} for k, v in result["sector_counts"].items()]
        ).sort_values("documents", ascending=False)
        st.bar_chart(sector_df.set_index("sector"))

        st.markdown("**ESG Pillar Signal Totals**")
        pillar_df = pd.DataFrame(
            [{"pillar": k, "hits": v} for k, v in result["pillar_signals"].items()]
        ).sort_values("hits", ascending=False)
        st.bar_chart(pillar_df.set_index("pillar"))

        st.markdown("**Metric Evidence vs Positive Tone (per 1k tokens)**")
        scatter_df = doc_df[["document", "metric_per_1k_tokens", "positive_per_1k_tokens"]].copy()
        st.scatter_chart(scatter_df, x="positive_per_1k_tokens", y="metric_per_1k_tokens")

        st.markdown("**Top Documents by Potential Narrative-Risk Pattern**")
        # Heuristic: high positive tone, lower metric density.
        risk_df = doc_df.assign(
            risk_score=(doc_df["positive_per_1k_tokens"] + 1.0)
            / (doc_df["metric_per_1k_tokens"] + 1.0)
        ).sort_values("risk_score", ascending=False)
        st.dataframe(
            risk_df[
                [
                    "document",
                    "year",
                    "sector_proxy",
                    "positive_per_1k_tokens",
                    "metric_per_1k_tokens",
                    "risk_score",
                ]
            ].head(20),
            use_container_width=True,
        )

        st.markdown("**Reasoning and Insights from All data/**")

        avg_tokens = int(mean(doc_df["tokens"])) if len(doc_df) else 0
        avg_metric = float(doc_df["metric_per_1k_tokens"].mean()) if len(doc_df) else 0.0
        avg_positive = float(doc_df["positive_per_1k_tokens"].mean()) if len(doc_df) else 0.0
        top_year = max(result["year_counts"].items(), key=lambda x: x[1])[0] if result["year_counts"] else "N/A"

        st.markdown(
            f"""
1. **Corpus reasoning**: we process every `data/thesis_dataset/*/ocr_result.json`, because OCR markdown is the common normalized text layer across documents. This gives a comparable unit for topic and sentiment diagnostics.
2. **Coverage insight**: the corpus is broad (`{len(doc_df):,}` docs, `{int(doc_df['pages'].sum()):,}` pages), with the strongest observed year concentration at **{top_year}**. This helps choose reliable windows for temporal modeling (Task 10).
3. **Text complexity insight**: average document length is about **{avg_tokens:,} tokens**, indicating enough text mass for robust topic models (LDA/BERTopic), while still allowing document-level comparisons.
4. **Pillar emphasis insight**: keyword signal totals across E/S/G reveal which pillar dominates narrative space; this can guide pillar-stratified topic modeling and avoid one-pillar bias.
5. **Credibility-vs-tone insight**: average positive cues are **{avg_positive:.2f} per 1k tokens** versus metric cues **{avg_metric:.2f} per 1k tokens**. Documents with high positive language but lower metric density become candidates for greenwashing-risk follow-up.
6. **Actionable next analysis**: use the top risk-score documents as a shortlist for ABSA + entity-level manual audit, then compare with cluster/topic assignments to test whether risk patterns are systemic (sector-level) or company-specific.
"""
        )

    else:
        st.warning("No parseable `ocr_result.json` files were found under `data/thesis_dataset/`.")
else:
    st.warning("`data/thesis_dataset/` was not found. Place OCR outputs there to run the full scan.")

st.info("Use the left sidebar to open detailed pages for each phase.")
