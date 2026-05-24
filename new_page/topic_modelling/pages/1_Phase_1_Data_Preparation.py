from task_data import get_tasks_for_phase
from ui import render_phase_page, render_research_frame

render_phase_page(
    "Phase 1 - Data Preparation",
    "Prepare, clean, and profile bilingual ESG report corpus data before modeling.",
    get_tasks_for_phase([1, 2]),
)

render_research_frame(
    gap=(
        "Most ESG NLP studies in Indonesian reporting either rely on narrow samples or do not formalize "
        "bilingual preprocessing and metadata coverage diagnostics before modeling."
    ),
    questions=[
        "How can we standardize OCR-derived Indonesian-English ESG text into comparable analytical units?",
        "What corpus imbalances exist across years, sectors, and ESG pillars, and how do they affect downstream validity?",
        "What minimum data quality and coverage thresholds are needed before sentiment/topic modeling?",
    ],
    objective=(
        "To construct a reproducible, metadata-aware preprocessing and corpus profiling layer that supports robust "
        "topic, sentiment, and greenwashing analyses on all available reports."
    ),
    contribution=[
        "A full-corpus bilingual preprocessing design for `data/thesis_dataset/*/ocr_result.json`.",
        "A practical coverage and imbalance diagnostic framework for ESG report corpora.",
        "A validated input layer that reduces noise and bias propagation into later tasks.",
    ],
    expected_results=[
        "Clean, structured text units with company-year-pillar metadata.",
        "Clear identification of sparse years/sectors and pillar imbalance risks.",
        "Documented readiness criteria for topic modeling, sentiment analysis, and clustering.",
    ],
)
