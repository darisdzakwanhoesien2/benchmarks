from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd
import streamlit as st

from task_data import BADGES, PHASES, get_tasks_for_phase

st.set_page_config(
    page_title="ESG Report Network Analysis",
    page_icon="🕸️",
    layout="wide",
)

st.title("ESG Report Network Analysis - Adapted Framework")
st.caption(
    "Mapping social/news graph analytics to ESG report co-entity and co-aspect networks."
)

cols = st.columns(len(BADGES))
for col, badge in zip(cols, BADGES):
    col.markdown(f"`{badge}`")

st.divider()
st.subheader("Framework Overview")
for phase in PHASES:
    tasks_text = ", ".join(str(tid) for tid in phase["tasks"])
    st.markdown(f"- **{phase['title']}**: Tasks {tasks_text}")

st.divider()
st.subheader("Task Quick View")
for phase in PHASES:
    with st.container(border=True):
        st.markdown(f"### {phase['title']}")
        for task in get_tasks_for_phase(phase["tasks"]):
            st.markdown(f"- **Task {task['id']}**: {task['title']}")
            st.caption(task["subtitle"])

st.divider()
st.subheader("Dataset-Wide Graph Scan (All data/)")

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
THESIS_DATASET_DIR = DATA_DIR / "thesis_dataset"

YEAR_RE = re.compile(r"(20\d{2})")
TOKEN_RE = re.compile(r"\b[a-z]{2,}\b")
NUM_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "our",
    "their",
    "will",
    "shall",
    "can",
    "may",
    "also",
    "not",
    "dan",
    "yang",
    "untuk",
    "dengan",
    "dari",
    "pada",
    "kami",
    "akan",
    "atau",
    "adalah",
    "dalam",
    "sebagai",
    "tahun",
    "perseroan",
    "perusahaan",
    "sustainability",
    "report",
    "laporan",
    "berkelanjutan",
}

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
        "corruption",
        "governansi",
        "dewan",
        "kepatuhan",
        "kebijakan",
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


def _extract_year(name: str) -> str | None:
    years = YEAR_RE.findall(name)
    return years[-1] if years else None


def _split_sections(text: str) -> list[str]:
    chunks = re.split(r"\n{2,}", text)
    out = []
    for c in chunks:
        c = c.strip()
        if len(c) >= 220:
            out.append(c)
    return out


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _entities_for_section(section_text: str, max_entities: int = 40) -> set[str]:
    toks = [t for t in _tokens(section_text) if t not in STOPWORDS and len(t) > 3]
    counts = Counter(toks)
    ranked = [w for w, c in counts.most_common(max_entities) if c >= 2]
    return set(ranked)


def _pillar_for_text(text: str) -> str:
    t = text.lower()
    scores = {p: sum(t.count(k) for k in keys) for p, keys in PILLAR_KEYWORDS.items()}
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "Mixed"


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


@st.cache_data(show_spinner=True)
def build_network_from_all_data(data_dir: Path, signature: str) -> dict[str, object]:
    _ = signature
    ocr_paths = sorted((data_dir / "thesis_dataset").glob("*/ocr_result.json"))

    G = nx.Graph()
    section_rows = []
    doc_counter_by_year = Counter()

    for path in ocr_paths:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        pages = obj.get("pages") or []
        doc_name = path.parent.name
        year = _extract_year(doc_name) or "Unknown"
        doc_counter_by_year[year] += 1

        full_text = "\n".join((p.get("markdown") or "") for p in pages if isinstance(p, dict))
        sections = _split_sections(full_text)

        local_nodes = []
        for idx, section in enumerate(sections):
            node_id = f"{doc_name}::sec_{idx:03d}"
            ents = _entities_for_section(section)
            if len(ents) < 3:
                continue

            tl = section.lower()
            numeric = len(NUM_RE.findall(section))
            pos_hits = sum(tl.count(w) for w in POSITIVE_CUES)
            metric_hits = sum(tl.count(w) for w in METRIC_CUES) + numeric
            pillar = _pillar_for_text(section)

            G.add_node(
                node_id,
                doc=doc_name,
                year=year,
                pillar=pillar,
                token_count=len(_tokens(section)),
                positive_hits=pos_hits,
                metric_hits=metric_hits,
                entity_count=len(ents),
                entities=sorted(ents),
            )
            local_nodes.append(node_id)

        for u, v in combinations(local_nodes, 2):
            eu = set(G.nodes[u]["entities"])
            ev = set(G.nodes[v]["entities"])
            shared = eu.intersection(ev)
            if len(shared) >= 2:
                G.add_edge(u, v, weight=len(shared))

    if G.number_of_nodes() == 0:
        return {
            "graph": G,
            "ocr_paths": ocr_paths,
            "node_df": pd.DataFrame(),
            "year_counts": dict(doc_counter_by_year),
            "community_sizes": {},
        }

    degree_c = nx.degree_centrality(G)
    bet_c = nx.betweenness_centrality(G, k=min(200, max(20, G.number_of_nodes() // 8)), normalized=True)

    # Greedy modularity keeps deps minimal (no python-louvain install requirement).
    communities = list(nx.algorithms.community.greedy_modularity_communities(G))
    node_to_community = {}
    for i, comm in enumerate(communities):
        for n in comm:
            node_to_community[n] = i

    node_rows = []
    for n, data in G.nodes(data=True):
        tokens = max(int(data.get("token_count", 0)), 1)
        metric_per_1k = float(data.get("metric_hits", 0)) / tokens * 1000.0
        pos_per_1k = float(data.get("positive_hits", 0)) / tokens * 1000.0
        risk_score = (pos_per_1k + 1.0) / (metric_per_1k + 1.0)

        node_rows.append(
            {
                "node": n,
                "doc": data.get("doc", ""),
                "year": data.get("year", "Unknown"),
                "pillar": data.get("pillar", "Mixed"),
                "token_count": tokens,
                "entity_count": int(data.get("entity_count", 0)),
                "degree": int(G.degree(n)),
                "degree_centrality": float(degree_c.get(n, 0.0)),
                "betweenness": float(bet_c.get(n, 0.0)),
                "community": int(node_to_community.get(n, -1)),
                "positive_per_1k_tokens": pos_per_1k,
                "metric_per_1k_tokens": metric_per_1k,
                "risk_score": risk_score,
            }
        )

    node_df = pd.DataFrame(node_rows)
    community_sizes = dict(sorted(Counter(node_df["community"]).items(), key=lambda x: x[1], reverse=True))

    return {
        "graph": G,
        "ocr_paths": ocr_paths,
        "node_df": node_df,
        "year_counts": dict(sorted(doc_counter_by_year.items())),
        "community_sizes": community_sizes,
    }


if THESIS_DATASET_DIR.exists():
    state_key = "social_network_scan_state"
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
        out = scan_state["result"]
        used_sig = scan_state["signature"]
        st.caption("Mode: Frozen snapshot (analysis is pinned until unfreeze).")
    else:
        out = build_network_from_all_data(DATA_DIR, current_sig)
        scan_state["result"] = out
        scan_state["signature"] = current_sig
        used_sig = current_sig
        st.caption("Mode: Auto-refresh on data change (reuses cache when unchanged).")

    st.caption(f"Dataset signature: `{hash(used_sig)}`")
    G: nx.Graph = out["graph"]
    node_df: pd.DataFrame = out["node_df"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("OCR Documents", f"{len(out['ocr_paths']):,}")
    m2.metric("Graph Nodes (sections)", f"{G.number_of_nodes():,}")
    m3.metric("Graph Edges", f"{G.number_of_edges():,}")
    m4.metric("Connected Components", f"{nx.number_connected_components(G):,}" if G.number_of_nodes() else "0")

    if G.number_of_nodes() > 0:
        density = nx.density(G)
        avg_degree = (2.0 * G.number_of_edges() / G.number_of_nodes()) if G.number_of_nodes() else 0.0

        st.markdown("**Core Network Structure**")
        c1, c2 = st.columns(2)
        c1.metric("Graph Density", f"{density:.6f}")
        c2.metric("Average Degree", f"{avg_degree:.2f}")

        st.markdown("**Coverage by Year (document count)**")
        year_df = pd.DataFrame([{"year": k, "documents": v} for k, v in out["year_counts"].items()])
        if not year_df.empty:
            st.bar_chart(year_df.set_index("year"))

        st.markdown("**Pillar Composition of Nodes**")
        pillar_df = node_df.groupby("pillar", as_index=False).size().rename(columns={"size": "nodes"})
        st.bar_chart(pillar_df.set_index("pillar"))

        st.markdown("**Largest Communities (greedy modularity)**")
        comm_df = pd.DataFrame(
            [{"community": k, "nodes": v} for k, v in out["community_sizes"].items()]
        ).head(20)
        if not comm_df.empty:
            st.bar_chart(comm_df.set_index("community"))

        st.markdown("**Centrality: Degree vs Betweenness**")
        st.scatter_chart(node_df, x="degree_centrality", y="betweenness")

        st.markdown("**Potential Bridge + Narrative-Risk Candidates**")
        bridge_risk_df = node_df.sort_values(
            ["betweenness", "risk_score", "degree_centrality"],
            ascending=[False, False, False],
        )
        st.dataframe(
            bridge_risk_df[
                [
                    "doc",
                    "year",
                    "pillar",
                    "community",
                    "degree",
                    "degree_centrality",
                    "betweenness",
                    "positive_per_1k_tokens",
                    "metric_per_1k_tokens",
                    "risk_score",
                ]
            ].head(25),
            use_container_width=True,
        )

        st.markdown("**Reasoning and Insights from All data/**")
        top_comm = comm_df.iloc[0]["nodes"] if not comm_df.empty else 0
        top_year = year_df.sort_values("documents", ascending=False).iloc[0]["year"] if not year_df.empty else "N/A"

        st.markdown(
            f"""
1. **Why this graph design**: each section becomes a node and shared high-frequency entities form weighted edges. This preserves local disclosure structure and is closer to how ESG narratives are actually written than whole-report nodes.
2. **Coverage insight**: the network is built from **{len(out['ocr_paths']):,} OCR documents** across years, with highest document concentration in **{top_year}**. This supports robust longitudinal comparisons.
3. **Structure insight**: with **{G.number_of_nodes():,} nodes** and **{G.number_of_edges():,} edges**, density (**{density:.6f}**) and average degree (**{avg_degree:.2f}**) indicate how interconnected ESG sections are across firms and years.
4. **Community insight**: the largest discovered community has **{int(top_comm):,} nodes**, showing recurring discourse blocks (for example repeated governance, compliance, or climate templates).
5. **Influence insight**: high-betweenness nodes are bridge sections linking otherwise separate clusters; they are important for diffusion of narrative framing.
6. **Risk insight**: when bridge-central sections also have high positivity but low metric density (`risk_score`), they are strong candidates for targeted greenwashing-risk audit.
"""
        )
    else:
        st.warning("No graph could be built from the available OCR files. Check OCR JSON integrity.")
else:
    st.warning("`data/thesis_dataset/` was not found. Place OCR outputs there to run the full graph scan.")

st.info("Use the left sidebar to open detailed pages for each part.")
