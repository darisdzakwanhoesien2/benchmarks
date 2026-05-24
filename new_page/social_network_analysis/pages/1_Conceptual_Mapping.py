from task_data import get_tasks_for_phase
from ui import render_phase_page, render_research_frame

render_phase_page(
    "Conceptual Mapping",
    "Translate the original tweet/network project structure into ESG report graph units.",
    get_tasks_for_phase([0]),
)

render_research_frame(
    gap=(
        "Graph methods are well-established in social media but are under-adapted for section-level ESG disclosure "
        "analysis in Indonesian sustainability reports."
    ),
    questions=[
        "What is the correct graph unit for ESG disclosure analysis: report, section, or entity node?",
        "How should social-network concepts (engagement, influence, diffusion) be mapped into ESG text networks?",
        "Which node and edge definitions best preserve interpretable ESG discourse structure?",
    ],
    objective=(
        "To define a defensible ESG graph schema that maps social graph concepts to report-section co-entity networks."
    ),
    contribution=[
        "A conceptual bridge from social graph analytics to ESG disclosure networks.",
        "A section-level node and shared-entity edge specification for empirical analysis.",
        "A clear rationale for downstream centrality, community, and diffusion tasks.",
    ],
    expected_results=[
        "A validated graph schema for ESG reports.",
        "Operational definitions for influence and connectivity in disclosure text.",
        "A consistent foundation for Parts 1-3 analysis.",
    ],
)
