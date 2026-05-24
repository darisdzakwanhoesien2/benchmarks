from task_data import get_tasks_for_phase
from ui import render_phase_page, render_research_frame

render_phase_page(
    "Part 3 - Simulation",
    "Run BFS-based ESG distance analysis and discourse diffusion simulation.",
    get_tasks_for_phase([9]),
)

render_research_frame(
    gap=(
        "ESG disclosure research rarely tests dynamic propagation mechanisms, leaving open how narrative patterns "
        "could spread across structurally connected report sections."
    ),
    questions=[
        "How far are sections from dominant ESG hubs in the graph?",
        "What diffusion behavior appears when vague or commitment-heavy language is simulated?",
        "Which sectors or pillars are most exposed to propagated narrative framing?",
    ],
    objective=(
        "To model ESG narrative propagation using distance and diffusion simulations on the section-level network."
    ),
    contribution=[
        "A dynamic extension beyond static centrality/community analysis.",
        "Distance-based influence interpretation for ESG discourse networks.",
        "Simulation evidence for isomorphic mimicry and narrative spillover hypotheses.",
    ],
    expected_results=[
        "BFS distance distributions from identified hub sections.",
        "Diffusion curves under different propagation assumptions.",
        "A map of potentially vulnerable network regions for policy scrutiny.",
    ],
)
