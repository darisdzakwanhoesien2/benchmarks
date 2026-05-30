from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd

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
    out: list[str] = []
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) >= 220:
            out.append(chunk)
    return out


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _entities_for_section(section_text: str, max_entities: int = 40) -> set[str]:
    tokens = [t for t in _tokens(section_text) if t not in STOPWORDS and len(t) > 3]
    counts = Counter(tokens)
    ranked = [word for word, count in counts.most_common(max_entities) if count >= 2]
    return set(ranked)


def _pillar_for_text(text: str) -> str:
    t = text.lower()
    scores = {pillar: sum(t.count(k) for k in keys) for pillar, keys in PILLAR_KEYWORDS.items()}
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else "Mixed"


def build_section_coentity_graph(thesis_dataset_dir: Path) -> tuple[nx.Graph, pd.DataFrame, dict[str, int]]:
    ocr_paths = sorted(thesis_dataset_dir.glob("*/ocr_result.json"))
    graph = nx.Graph()
    doc_counter_by_year: Counter[str] = Counter()

    for path in ocr_paths:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        pages = obj.get("pages") or []
        if not isinstance(pages, list):
            continue

        doc_name = path.parent.name
        year = _extract_year(doc_name) or "Unknown"
        doc_counter_by_year[year] += 1

        full_text = "\n".join((p.get("markdown") or "") for p in pages if isinstance(p, dict))
        sections = _split_sections(full_text)

        local_nodes: list[str] = []
        for idx, section in enumerate(sections):
            node_id = f"{doc_name}::sec_{idx:03d}"
            entities = _entities_for_section(section)
            if len(entities) < 3:
                continue

            section_lower = section.lower()
            numeric = len(NUM_RE.findall(section))
            pos_hits = sum(section_lower.count(w) for w in POSITIVE_CUES)
            metric_hits = sum(section_lower.count(w) for w in METRIC_CUES) + numeric
            pillar = _pillar_for_text(section)

            graph.add_node(
                node_id,
                doc=doc_name,
                year=year,
                pillar=pillar,
                token_count=len(_tokens(section)),
                positive_hits=pos_hits,
                metric_hits=metric_hits,
                entity_count=len(entities),
                entities=sorted(entities),
            )
            local_nodes.append(node_id)

        for u, v in combinations(local_nodes, 2):
            eu = set(graph.nodes[u]["entities"])
            ev = set(graph.nodes[v]["entities"])
            shared = eu.intersection(ev)
            if len(shared) >= 2:
                graph.add_edge(u, v, weight=len(shared))

    if graph.number_of_nodes() == 0:
        return graph, pd.DataFrame(), dict(doc_counter_by_year)

    degree_c = nx.degree_centrality(graph)
    bet_c = nx.betweenness_centrality(
        graph, k=min(200, max(20, graph.number_of_nodes() // 8)), normalized=True
    )
    clo_c = nx.closeness_centrality(graph)
    eig_c: dict[str, float] = {}
    try:
        eig_c = nx.eigenvector_centrality(graph, max_iter=2500)
    except Exception:
        eig_c = {}

    communities = list(nx.algorithms.community.greedy_modularity_communities(graph))
    node_to_community: dict[str, int] = {}
    for i, comm in enumerate(communities):
        for n in comm:
            node_to_community[n] = i

    node_rows: list[dict[str, object]] = []
    for node, data in graph.nodes(data=True):
        tokens = max(int(data.get("token_count", 0)), 1)
        metric_per_1k = float(data.get("metric_hits", 0)) / tokens * 1000.0
        pos_per_1k = float(data.get("positive_hits", 0)) / tokens * 1000.0
        risk_score = (pos_per_1k + 1.0) / (metric_per_1k + 1.0)

        node_rows.append(
            {
                "node": node,
                "doc": data.get("doc", ""),
                "year": data.get("year", "Unknown"),
                "pillar": data.get("pillar", "Mixed"),
                "token_count": tokens,
                "entity_count": int(data.get("entity_count", 0)),
                "degree": int(graph.degree(node)),
                "degree_centrality": float(degree_c.get(node, 0.0)),
                "betweenness": float(bet_c.get(node, 0.0)),
                "closeness": float(clo_c.get(node, 0.0)),
                "eigenvector": float(eig_c.get(node, 0.0)),
                "community": int(node_to_community.get(node, -1)),
                "positive_per_1k_tokens": pos_per_1k,
                "metric_per_1k_tokens": metric_per_1k,
                "risk_score": risk_score,
                "entities": "|".join(data.get("entities") or []),
            }
        )

    node_df = pd.DataFrame(node_rows)
    return graph, node_df, dict(doc_counter_by_year)


def _graph_summary(graph: nx.Graph, node_df: pd.DataFrame, year_counts: dict[str, int]) -> dict[str, object]:
    if graph.number_of_nodes() == 0:
        return {
            "documents": int(sum(year_counts.values())),
            "nodes": 0,
            "edges": 0,
            "components": 0,
        }

    density = nx.density(graph)
    avg_degree = (2.0 * graph.number_of_edges() / graph.number_of_nodes()) if graph.number_of_nodes() else 0.0
    components = nx.number_connected_components(graph)
    clustering = nx.average_clustering(graph, weight=None)
    assortativity = None
    try:
        assortativity = nx.degree_assortativity_coefficient(graph)
    except Exception:
        assortativity = None

    top_year = None
    if year_counts:
        top_year = sorted(year_counts.items(), key=lambda x: x[1], reverse=True)[0][0]

    top_pillars: dict[str, int] = {}
    if not node_df.empty:
        top_pillars = node_df["pillar"].value_counts().to_dict()

    return {
        "documents": int(sum(year_counts.values())),
        "nodes": int(graph.number_of_nodes()),
        "edges": int(graph.number_of_edges()),
        "components": int(components),
        "density": float(density),
        "avg_degree": float(avg_degree),
        "avg_clustering": float(clustering),
        "degree_assortativity": None if assortativity is None else float(assortativity),
        "top_year": top_year,
        "year_counts": dict(sorted(year_counts.items())),
        "pillar_counts": top_pillars,
    }


def run(thesis_dataset_dir: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    graph, node_df, year_counts = build_section_coentity_graph(thesis_dataset_dir)

    summary = _graph_summary(graph, node_df, year_counts)
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    node_df.to_csv(output_dir / "nodes.csv", index=False)
    edges = [
        {"source": u, "target": v, "weight": float(d.get("weight", 1.0))}
        for u, v, d in graph.edges(data=True)
    ]
    pd.DataFrame(edges).to_csv(output_dir / "edges.csv", index=False)

    if not node_df.empty:
        node_df.sort_values(["betweenness", "degree_centrality"], ascending=[False, False]).head(50).to_csv(
            output_dir / "top_bridges.csv",
            index=False,
        )
        node_df.sort_values(
            ["risk_score", "betweenness", "degree_centrality"],
            ascending=[False, False, False],
        ).head(50).to_csv(output_dir / "top_risk_candidates.csv", index=False)
        node_df.groupby("community", as_index=False).size().rename(columns={"size": "nodes"}).sort_values(
            "nodes", ascending=False
        ).to_csv(output_dir / "community_sizes.csv", index=False)
        node_df.groupby("year", as_index=False).size().rename(columns={"size": "sections"}).sort_values(
            "sections", ascending=False
        ).to_csv(output_dir / "sections_by_year.csv", index=False)

    try:
        nx.write_gexf(graph, output_dir / "graph.gexf")
    except Exception:
        pass

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run corpus-wide ESG disclosure network scan.")
    parser.add_argument("--thesis-dataset-dir", type=Path, default=Path("data/thesis_dataset"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/social_network_analysis"))
    args = parser.parse_args()

    summary = run(args.thesis_dataset_dir, args.output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

