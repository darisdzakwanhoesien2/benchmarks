"""Task definitions for ESG graph network Streamlit app."""

from __future__ import annotations

from typing import Dict, List

BADGES = [
    "Graph construction",
    "Network centrality",
    "Community detection",
    "ESG ABSA",
    "Greenwashing signals",
]

PHASES = [
    {"id": "concept", "title": "Conceptual Mapping", "tasks": [0]},
    {"id": "part1", "title": "Part 1 - Graph Construction and Analysis", "tasks": [1, 2, 3, 4, 5]},
    {"id": "part2", "title": "Part 2 - Community and Correlation Analysis", "tasks": [6, 7, 8]},
    {"id": "part3", "title": "Part 3 - Simulation", "tasks": [9]},
    {"id": "part4", "title": "Part 4 - Literature Review", "tasks": [10]},
]

TASKS: Dict[int, Dict[str, object]] = {
    0: {
        "title": "Original to ESG adaptation key",
        "subtitle": "Map social graph concepts to ESG report network entities",
        "summary": "Set section-level nodes and shared-entity edges as the core adaptation from tweet networks.",
        "steps": [
            "Define report section (company x year x pillar) as node granularity.",
            "Define shared ESG entities/aspects as edge criterion.",
            "Use sentiment/aspect/entity metrics as engagement analogs.",
            "Retain year as temporal axis for later simulation and drift analysis.",
        ],
        "outputs": [
            "Node-edge mapping schema",
            "Attribute dictionary for graph construction",
        ],
        "notes": [
            "Section-level nodes provide richer structure than full-report nodes.",
        ],
    },
    1: {
        "title": "ESG entity graph construction using NER",
        "subtitle": "Build co-entity network from sustainability report sections",
        "summary": "Extract entities, build bipartite graph, project to section-section graph with weighted edges.",
        "steps": [
            "Extract ORG, ENV, POLICY, METRIC, CERT entities using spaCy plus ESG ruler.",
            "Build bipartite graph: section nodes and entity nodes.",
            "Project onto section graph where edge weight = shared entity count.",
            "Apply edge threshold (>=2 shared entities) to reduce noise.",
            "Export NetworkX object and graphml for Gephi.",
        ],
        "outputs": [
            "NetworkX graph",
            "Entity count histograms by type",
            "Gephi-ready .graphml file",
        ],
        "notes": [
            "Produce separate E/S/G subgraphs and compare structure.",
        ],
    },
    2: {
        "title": "Degree distribution and centrality summary",
        "subtitle": "Identify the most connected ESG sections in the network",
        "summary": "Compute core connectivity metrics and inspect high-degree hub sections.",
        "steps": [
            "Compute max/min/avg degree, density, and average path length.",
            "Compute degree centrality and save node-level CSV.",
            "Plot degree histogram (log-log) with top hubs annotated.",
            "Review sector/pillar composition of top-degree nodes.",
        ],
        "outputs": [
            "Degree and graph summary table",
            "Degree centrality CSV",
            "Annotated log-log histogram",
        ],
        "notes": [
            "Reuse degree centrality outputs in Task 5 correlation analysis.",
        ],
    },
    3: {
        "title": "Betweenness and closeness centrality analysis",
        "subtitle": "Find sections that bridge ESG discourse communities",
        "summary": "Locate bridge nodes and globally reachable hubs using path-based centrality.",
        "steps": [
            "Compute betweenness and closeness centralities.",
            "Plot top-20 nodes for each metric.",
            "Save complete centrality table with node metadata.",
            "Inspect text/aspects of top betweenness and top closeness nodes.",
        ],
        "outputs": [
            "Centrality score CSV",
            "Top-node centrality visualizations",
            "Bridge-node content interpretation notes",
        ],
        "notes": [
            "High closeness + low METRIC density can indicate templated positive disclosure.",
        ],
    },
    4: {
        "title": "Clustering coefficients and local structure analysis",
        "subtitle": "Measure how tightly ESG sections cluster around shared entities",
        "summary": "Quantify local transitivity and compare against random null structure.",
        "steps": [
            "Compute node-level clustering coefficients and global average.",
            "Plot 10-bin coefficient histogram.",
            "Generate Erdos-Renyi null graph with same n and m.",
            "Compare observed vs null clustering statistics by sector.",
        ],
        "outputs": [
            "Clustering coefficient CSV",
            "Histogram plot",
            "Observed-vs-random comparison",
        ],
        "notes": [
            "Near-zero clustering with nontrivial degree often marks bridge-like nodes.",
        ],
    },
    5: {
        "title": "Sentiment-centrality correlation and token analysis",
        "subtitle": "Correlate network influence proxies with ESG sentiment credibility",
        "summary": "Replace social engagement metrics with ESG influence metrics and test centrality correlations.",
        "steps": [
            "Define section metrics: sentiment, aspect frequency, entity density, metric density.",
            "Compare top and bottom nodes by centrality for lexical/entity patterns.",
            "Compute Pearson correlations between centrality and sentiment/credibility metrics.",
            "Flag high-centrality but low-metric-density sections as risk signals.",
        ],
        "outputs": [
            "Correlation table",
            "Top-vs-bottom token/entity comparison",
            "Greenwashing signal candidates",
        ],
        "notes": [
            "Centrality-driven positivity without quantitative detail is a novel signal.",
        ],
    },
    6: {
        "title": "Community detection and ESG discourse cluster profiling",
        "subtitle": "Louvain clustering plus Gephi and word-cloud profiling",
        "summary": "Detect communities, visualize them, and map each to ESG aspects and sentiment profiles.",
        "steps": [
            "Run Louvain partitioning with resolution tuning.",
            "Export graph with node attributes for Gephi ForceAtlas2 layout.",
            "Build word clouds for three largest communities.",
            "Profile each community by sector, pillar, sentiment, and top entities.",
        ],
        "outputs": [
            "Community labels for each node",
            "Gephi community visualization",
            "Community profile table and word clouds",
        ],
        "notes": [
            "Align communities against 46-aspect ESG taxonomy and LDA outputs.",
        ],
    },
    7: {
        "title": "Attribute correlation (1): sentiment metric cross-correlations",
        "subtitle": "Statistical alignment between sentiment systems and network context",
        "summary": "Estimate pairwise sentiment-metric correlations with significance testing.",
        "steps": [
            "Compute Pearson r and p-value for core sentiment metric pairs.",
            "Add sentiment vs centrality and entity-density vs metric-density pairs.",
            "Visualize full matrix with heatmap and significant scatter plots.",
            "Interpret low-agreement pairs as model/domain mismatch evidence.",
        ],
        "outputs": [
            "Correlation matrix and p-value table",
            "Heatmap and regression scatter plots",
            "Pairwise interpretation notes",
        ],
        "notes": [
            "LLM vs ClimateBERT mismatch should be reported explicitly.",
        ],
    },
    8: {
        "title": "Attribute correlation (2): sentiment vs complexity and entity count",
        "subtitle": "Relate text complexity, hedging, and quantitative detail to sentiment",
        "summary": "Test whether verbosity and hedging inflate sentiment independently of evidence density.",
        "steps": [
            "Correlate token/entity counts with sentiment and centrality.",
            "Correlate metric density with sentiment to test credibility linkage.",
            "Add hedging phrase count and future-tense ratio correlations.",
            "Summarize effect sizes and significance for greenwashing inference.",
        ],
        "outputs": [
            "Complexity-sentiment correlation results",
            "Hedging/future-tense diagnostic plots",
            "Greenwashing inference summary",
        ],
        "notes": [
            "Sentiment up + metric density down is a key warning pattern.",
        ],
    },
    9: {
        "title": "ESG influence propagation simulation (Erdos number analog)",
        "subtitle": "BFS distance from network hub and diffusion of discourse signals",
        "summary": "Compute ESG distance from hub and simulate phrase diffusion across network neighborhoods.",
        "steps": [
            "Select highest-degree node as ESG hub.",
            "Compute BFS shortest-path distances and export scores.",
            "Plot distance distribution and isolate far sectors/pillars.",
            "Run SIR-style adoption simulation for targeted vague phrase propagation.",
        ],
        "outputs": [
            "ESG distance CSV",
            "BFS distance histogram",
            "Diffusion adoption curve",
        ],
        "notes": [
            "This simulation supports isomorphic mimicry hypotheses in discourse diffusion.",
        ],
    },
    10: {
        "title": "Literature review: graph-based ESG analysis and entity network methods",
        "subtitle": "Position methods and findings in ESG NLP and graph analytics scholarship",
        "summary": "Ground network analyses with graph-NLP, ESG diffusion, and Indonesian regulatory literature.",
        "steps": [
            "Review graph-based NLP and entity network studies in disclosures.",
            "Cover community detection and network methods papers (e.g., Louvain).",
            "Connect findings to greenwashing/isomorphism theory.",
            "Discuss Indonesian context: OJK POJK 51/2017, PROPER, BUMN-private differences.",
        ],
        "outputs": [
            "Curated literature matrix",
            "Methods-to-findings synthesis narrative",
            "Limitations and future dynamic-graph directions",
        ],
        "notes": [
            "Discuss complementarity of ABSA local sentiment and graph-level relational structure.",
        ],
    },
}


def get_tasks_for_phase(task_ids: List[int]) -> List[Dict[str, object]]:
    return [{"id": task_id, **TASKS[task_id]} for task_id in task_ids]
