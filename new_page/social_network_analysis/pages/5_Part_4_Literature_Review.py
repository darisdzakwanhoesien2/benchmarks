from task_data import get_tasks_for_phase
from ui import render_phase_page, render_research_frame

render_phase_page(
    "Part 4 - Literature Review",
    "Contextualize graph and ESG NLP findings with core academic literature.",
    get_tasks_for_phase([10]),
)

render_research_frame(
    gap=(
        "There is limited integrated synthesis combining ESG ABSA, graph analytics, and Indonesian regulatory context "
        "into one coherent methodological argument."
    ),
    questions=[
        "How do graph-based ESG methods compare with conventional sentiment-only pipelines?",
        "Which theories best explain centrality, clustering, and diffusion findings in ESG disclosure?",
        "How do Indonesian regulations shape interpretation of observed reporting patterns?",
    ],
    objective=(
        "To position empirical findings in graph-NLP, greenwashing, and Indonesian regulatory literature and identify "
        "methodological limits and future research directions."
    ),
    contribution=[
        "A unified theoretical framing across ABSA, network science, and governance context.",
        "A transparent mapping from method choice to empirical claim strength.",
        "A future agenda for dynamic and cross-market ESG graph analysis.",
    ],
    expected_results=[
        "A curated literature-to-method matrix tied to this pipeline.",
        "A defensible interpretation boundary for current findings.",
        "Clear recommendations for next-phase research and validation design.",
    ],
)
