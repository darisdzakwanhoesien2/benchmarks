from task_data import get_tasks_for_phase
from ui import render_phase_page, render_research_frame

render_phase_page(
    "Part 2 - Community and Correlation Analysis",
    "Detect discourse communities and quantify metric correlations in network context.",
    get_tasks_for_phase([6, 7, 8]),
)

render_research_frame(
    gap=(
        "Few studies jointly analyze community structure and sentiment/complexity correlations to explain how ESG "
        "narratives cluster and diverge across firms and sectors."
    ),
    questions=[
        "What discourse communities emerge in ESG co-entity networks?",
        "How do sentiment, complexity, and metric density vary across communities?",
        "Which correlation patterns are consistent with potential greenwashing behavior?",
    ],
    objective=(
        "To detect ESG discourse communities and test statistical relationships between sentiment, evidence density, "
        "and structural position."
    ),
    contribution=[
        "Community-level interpretation layer that complements node-level centrality.",
        "Correlation evidence connecting language style with quantitative disclosure.",
        "A clearer separation between topical concentration and credibility signals.",
    ],
    expected_results=[
        "Community labels and size profiles for major discourse blocks.",
        "Correlation matrices linking tone, complexity, and network metrics.",
        "Ranked community-level risk hypotheses for manual validation.",
    ],
)
