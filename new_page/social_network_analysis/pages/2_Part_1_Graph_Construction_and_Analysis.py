from task_data import get_tasks_for_phase
from ui import render_phase_page, render_research_frame

render_phase_page(
    "Part 1 - Graph Construction and Analysis",
    "Construct ESG co-entity graphs and compute core network structure metrics.",
    get_tasks_for_phase([1, 2, 3, 4, 5]),
)

render_research_frame(
    gap=(
        "Prior ESG sentiment studies often ignore relational structure between disclosures and therefore miss "
        "which sections act as hubs, bridges, or structurally influential narratives."
    ),
    questions=[
        "Which ESG report sections are most central in co-entity networks?",
        "Do bridge sections differ from hub sections in tone and evidence density?",
        "Can centrality linked with low quantitative evidence indicate potential narrative-risk patterns?",
    ],
    objective=(
        "To build co-entity ESG graphs from all OCR reports and quantify structural influence using degree, "
        "betweenness, closeness, and clustering metrics."
    ),
    contribution=[
        "A reproducible graph construction pipeline from OCR markdown sections.",
        "Joint structural and sentiment-evidence diagnostics at node level.",
        "An operational shortlist of high-impact sections for targeted audit.",
    ],
    expected_results=[
        "Node-level centrality tables with document and pillar metadata.",
        "Identification of hubs and bridge disclosures across corpus.",
        "Risk candidates where persuasive tone outpaces metric disclosure.",
    ],
)
