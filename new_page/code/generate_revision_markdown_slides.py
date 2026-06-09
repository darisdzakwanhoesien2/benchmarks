from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION_ROOT = ROOT / "report_standardized" / "revision"
MARP_DIR = REVISION_ROOT / "Marp"
QUARTO_DIR = REVISION_ROOT / "Quarto"

FIG_RESULTS = "../../../results/visualizations"
FIG_THESIS = "../../Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures"


SLIDES = [
    {
        "title": "Toward an Executable ESG Aspect-Based Sentiment Analysis Framework",
        "subtitle": "Revision Presentation Based on the Standardized Thesis Chapters\n\nDaris Dzakwan Hoesien\n\nUniversity of Oulu",
    },
    {
        "title": "Presentation Scope",
        "bullets": [
            "Research framing",
            "Methodology and data flow",
            "Experiments and empirical findings",
            "Discussion, limitations, and future work",
            "Appendix and reproducibility",
        ],
    },
    {
        "section": "Research Framing",
        "title": "Problem Context",
        "bullets": [
            "Indonesian sustainability reports are long, bilingual, and structurally heterogeneous.",
            "Document-level ESG scoring is too coarse for distinguishing promises, actions, and realized outcomes.",
            "The thesis reframes ESG analysis as record-level evidence extraction with aspect, ESG pillar, sentiment, and disclosure tone.",
            "The target is not only prediction quality, but also provenance, auditability, ontology alignment, and reproducible workflow structure.",
        ],
    },
    {
        "title": "Research Questions",
        "bullets": [
            "**RQ1. ESG ABSA Schema:** How can ESG disclosures be represented using a record-level schema integrating aspect, pillar, sentiment, and tone?",
            "**RQ2. Tone vs. Climate-Specific Models:** How do LLM-generated tone labels compare with ClimateBERT-style outputs?",
            "**RQ3. Pipeline Diagnostics:** What failure modes characterize automated ESG extraction?",
            "**RQ4. Stability and Reproducibility:** How stable are outputs across prompts, models, and providers?",
        ],
    },
    {
        "title": "Main Contributions",
        "bullets": [
            "An executable OCR-to-ESG workflow implemented as a multi-page Streamlit research system.",
            "A record-level ESG schema that separates commitment, action, and outcome from generic positive sentiment.",
            "A layered evaluation design combining prompt diagnostics, model diagnostics, ontology mapping, ClimateBERT comparison, and pilot review.",
            "A reproducible artifact stack covering OCR folders, ESG extraction logs, benchmark JSONL files, revision analytics, and dashboard visualizations.",
        ],
    },
    {
        "section": "Methodology",
        "title": "Methodological Overview",
        "image": f"{FIG_THESIS}/03_01_overview.png",
        "bullets": [
            "The pipeline moves from raw PDF reports to OCR-expanded pages, structured ESG records, benchmark layers, and thesis-ready analytics.",
            "The design is mixed-method and executable: automated extraction is paired with provenance and review surfaces.",
        ],
    },
    {
        "title": "System Architecture",
        "image": f"{FIG_THESIS}/03_01_01_system_architecture.png",
    },
    {
        "title": "Data Sources and Corpus Shape",
        "image": f"{FIG_THESIS}/03_02_data_sources.png",
        "bullets": [
            "Raw source layer: sustainability and annual report PDFs in `data/thesis_pdf/`.",
            "OCR-expanded layer: document folders in `data/thesis_dataset/` with `ocr_result.json`, page markdown, and images.",
            "Active thesis-facing subset: 23 processed reports, about 5,512 pages, 332 tone-bearing records, and 2,074 T2 rows.",
            "Support data includes ontology resources, pilot annotations, benchmark artifacts, and dashboard exports.",
        ],
    },
    {
        "title": "Preprocessing and Provenance Design",
        "image": f"{FIG_THESIS}/03_02_02.png",
        "bullets": [
            "Page-level OCR artifacts are the core provenance unit.",
            "Later extraction and validation stages preserve links back to document folders and page markdown.",
        ],
    },
    {
        "title": "Feature and Representation Strategy",
        "image": f"{FIG_THESIS}/03_04.png",
        "bullets": [
            "The workflow combines rule-based lexical cues, TF-IDF baselines, contextual hybrid embeddings, and ontology-aware representations.",
        ],
    },
    {
        "title": "Framework Split",
        "image": f"{FIG_THESIS}/03_05.png",
        "bullets": [
            "**Framework 1:** page-aware LLM extraction into structured ESG records.",
            "**Framework 2:** benchmarking, comparison, ontology mapping, and evidence scoring.",
            "The thesis contribution is the end-to-end orchestration, not one isolated model.",
        ],
    },
    {
        "title": "Reference Construction",
        "image": f"{FIG_THESIS}/03_06.png",
        "bullets": [
            "No full expert gold corpus exists yet.",
            "The thesis uses a layered reference design: extracted ESG records, ClimateBERT-style comparison labels, T1 and T2 JSONL artifacts, and pilot human annotations.",
            "This supports exploratory evaluation while keeping weak points visible.",
        ],
    },
    {
        "title": "Methodology Summary",
        "image": f"{FIG_THESIS}/03_07_summary.png",
    },
    {
        "section": "Experiments",
        "title": "Experimental Scope",
        "bullets": [
            "The experiments evaluate a full workflow: OCR, T3 extraction, T1 ClimateBERT comparison, T2 ABSA-style processing, ontology mapping, and revision analytics.",
            "Prompt families include zero-shot, few-shot, and chain-of-thought variants in English and Indonesian.",
            "Backend families include OpenRouter, LM Studio or OpenAI-compatible endpoints, and Ollama-style local inference.",
            "The key evaluation focus is usable structured extraction, not parseability alone.",
        ],
    },
    {
        "title": "Evaluation Metrics",
        "bullets": [
            "OCR completion at document and page level.",
            "Parse success, average extracted records, field completion, missing-tone rate, and schema-drift rate.",
            "Percent agreement and Cohen's kappa for tone versus ClimateBERT-style comparison.",
            "Ontology coverage and company-level commitment-outcome ratios for interpretive analysis.",
            "Failure-mode counts and denominator audits for pipeline diagnostics.",
        ],
    },
    {
        "title": "RQ1: Operational Schema Results",
        "bullets": [
            "23 OCR-processed documents were completed across approximately 5,512 pages.",
            "The active evidence layer contains 332 tone-bearing ESG records and 2,074 T2 rows.",
            "The schema supports simultaneous storage of text, aspect, ESG pillar, tone, sentiment, reasoning, and provenance.",
            "Ontology mapping covers all 52 tracked aspects in the thesis-facing subset.",
        ],
    },
    {"title": "Tone Distribution", "image": f"{FIG_RESULTS}/tone_distribution.png"},
    {"title": "ESG Distribution by Tone", "image": f"{FIG_RESULTS}/esg_by_tone.png"},
    {"title": "Aspect-by-Tone Structure", "image": f"{FIG_RESULTS}/aspect_by_tone_heatmap.png"},
    {
        "title": "Prompt-Level Extraction Results",
        "table": {
            "headers": ["Prompt", "Parse success", "Avg. records", "Missing tone"],
            "rows": [
                ["`data.md`", "100.0%", "3.00", "100.0%"],
                ["`tone_cot_en`", "100.0%", "6.25", "0.0%"],
                ["`tone_cot_id`", "100.0%", "4.07", "0.3%"],
                ["`tone_few_shot_en`", "100.0%", "0.00", "0.0%"],
                ["`tone_few_shot_id`", "100.0%", "1.00", "0.0%"],
                ["`tone_zero_shot_en`", "100.0%", "3.93", "0.0%"],
                ["`tone_zero_shot_id`", "100.0%", "2.62", "0.0%"],
            ],
        },
        "bullets": [
            "Parse validity is insufficient as a sole metric.",
            "Tone-aware chain-of-thought prompting is the strongest thesis-facing family.",
        ],
    },
    {
        "title": "RQ2: Tone vs. ClimateBERT",
        "bullets": [
            "Tone commitment versus ClimateBERT-style commitment was evaluated over 332 records.",
            "The saved comparison reports 83.7% agreement and Cohen's kappa of 0.645.",
            "The overlap is strong enough to support construct relevance, but not full label equivalence.",
            "ClimateBERT captures climate-topic or climate-commitment relevance; the tone taxonomy captures disclosure maturity.",
        ],
    },
    {"title": "Tone and ClimateBERT Cross-Distribution", "image": f"{FIG_RESULTS}/climatebert_label_by_tone.png"},
    {
        "title": "RQ3: Failure-Mode Diagnostics",
        "table": {
            "headers": ["Failure mode", "Count", "Interpretation"],
            "rows": [
                ["Missing tone", "61", "Core output field omitted despite otherwise parseable extraction"],
                ["Schema drift", "20", "Values placed in the wrong field or schema semantics shifted"],
                ["Hedged or modal language", "10", "Commitment-action boundary blurred by future-oriented phrasing"],
                ["Regulatory or Indonesian domain terms", "3", "Domain-specific wording weakens cue consistency"],
                ["Table or numeric layout", "3", "Tabular formatting disrupts semantic extraction"],
                ["Passive voice", "3", "Outcome versus action distinction becomes unstable"],
                ["Bilingual or code-switched", "1", "Mixed language complicates interpretation"],
            ],
        },
    },
    {"title": "Failure-Mode Pareto", "image": f"{FIG_RESULTS}/failure_mode_pareto.png"},
    {"title": "Failure-Mode Composition", "image": f"{FIG_RESULTS}/failure_mode_pie.png"},
    {
        "title": "RQ4: Model Stability Trade-Off",
        "table": {
            "headers": ["Model", "Parse success", "Avg. records", "Short reading"],
            "rows": [
                ["`trinity-large-preview`", "100.0%", "3.02", "Best stable thesis-facing baseline"],
                ["`gpt-oss-120b`", "100.0%", "3.00", "Parseable but unusable for tone"],
                ["`trinity-large-thinking`", "89.9%", "12.52", "High yield, weaker formal stability"],
                ["`minimax-m2.5`", "56.6%", "4.94", "High-volume use, weak parse reliability"],
                ["`gpt-oss-20b`", "95.9%", "1.13", "Stable but low yield"],
            ],
        },
        "text": "The decisive factor is schema-following behavior, not nominal model scale.",
    },
    {"title": "Model Trade-Off Scatter", "image": f"{FIG_RESULTS}/model_tradeoff_scatter.png"},
    {"title": "Prompt Strategy Comparison", "image": f"{FIG_RESULTS}/prompt_strategy_comparison.png"},
    {
        "title": "Explainability-Oriented Graphs",
        "images": [
            f"{FIG_RESULTS}/information_density_by_tone.png",
            f"{FIG_RESULTS}/soft_language_ratio_by_tone.png",
        ],
        "bullets": [
            "These charts help explain why commitment-heavy and soft-language segments create boundary failures.",
        ],
    },
    {
        "section": "Discussion",
        "title": "Discussion Synthesis",
        "bullets": [
            "The thesis shows that ESG disclosure analysis becomes more informative when tone is modeled as a separate field from generic sentiment.",
            "The dominant evidence pattern is commitment-heavy environmental disclosure rather than outcome-heavy reporting.",
            "The strongest configuration is a tone-aware prompt paired with a schema-obedient model.",
            "Ontology coverage is comparatively robust; the main bottleneck is tone stability.",
        ],
    },
    {
        "title": "Research Question Resolution Summary",
        "table": {
            "headers": ["Research question", "Core evidence", "Status"],
            "rows": [
                ["RQ1", "OCR-complete subset, structured records, ontology mapping", "Answered positively"],
                ["RQ2", "83.7% agreement, kappa 0.645, meaningful divergence", "Answered positively with qualification"],
                ["RQ3", "Missing tone, schema drift, ambiguity-rich failures", "Answered diagnostically"],
                ["RQ4", "Stored artifacts, prompt and model trade-offs, rerunnable outputs", "Answered positively with stability caveat"],
            ],
        },
    },
    {"title": "Commitment-Outcome Screening Gap", "image": f"{FIG_RESULTS}/greenwashing_gap_scatter.png"},
    {"title": "Tone Share Ratio", "image": f"{FIG_RESULTS}/commitment_outcome_ratio.png"},
    {
        "title": "Limitations",
        "bullets": [
            "The evaluation layer is still partly weakly supervised and not yet a complete expert-coded gold benchmark.",
            "The active evidence subset is domain-concentrated and environmentally skewed.",
            "Prompt and model sensitivity remain material; backend substitution is not safe by default.",
            "Greenwashing-style ratios are heuristic screening aids, not final adjudicative scores.",
        ],
    },
    {
        "title": "Future Work",
        "bullets": [
            "Expand pilot review into a stratified expert benchmark with inter-annotator agreement.",
            "Tighten tone-specific prompting and schema validation with targeted rerun logic.",
            "Add OCR quality baselines so upstream noise can be separated from downstream extraction failure.",
            "Complete one-to-one ClimateBERT benchmarking over the full extracted record layer.",
            "Extend the framework toward analyst-facing review tools and graph-based retrieval workflows.",
        ],
    },
    {
        "section": "Appendix and Reproducibility",
        "title": "Operational User Workflow",
        "bullets": [
            "Bulk OCR accepts uploaded or server-side PDFs and stores OCR-expanded artifacts under `data/thesis_dataset/`.",
            "LLM Processing loads one OCR-expanded document, allows page-range selection, and sends batches to one of three provider families.",
            "Structured ESG records are stored in `results/esg_records.json`.",
            "ClimateBERT or local comparison models operate downstream as the T1 comparison layer.",
        ],
    },
    {
        "title": "Appendix Workflow Figure",
        "image": f"{FIG_THESIS}/03_01_overview.png",
        "bullets": [
            "The appendix adds procedural detail on page-range processing, provider choice, and downstream comparison artifacts.",
        ],
    },
    {
        "title": "Repository JSON Artifact Families",
        "bullets": [
            "`ocr_result.json`: page-level OCR outputs and image metadata.",
            "`results/esg_records.json`: structured T3 extraction runs and records.",
            "`results/t1_results.jsonl` and `results/t2_results.jsonl`: resumable benchmark layers.",
            "`results/revision_analysis/ontology.json`: ontology paths and mapped ESG concepts.",
            "Dashboard and workflow JSON files support narrative reporting, transfer summaries, and Streamlit page relationships.",
        ],
    },
    {
        "title": "Reproducibility Strengths",
        "bullets": [
            "The revision workflow indexes 1,220 stored result artifacts and 184 background jobs.",
            "Prompt templates, logs, JSONL files, visualizations, and chapter-ready outputs are persisted on disk.",
            "The strongest reproducibility claim is workflow and artifact persistence.",
            "Exact third-party LLM semantic outputs may still vary across time, providers, and model updates.",
        ],
    },
    {
        "section": "Conclusion",
        "title": "Closing Takeaways",
        "bullets": [
            "The thesis demonstrates a viable end-to-end framework for converting Indonesian sustainability reports into auditable ESG evidence.",
            "The most important substantive insight is that commitment-heavy disclosure dominates the current extracted layer.",
            "The most important technical insight is that prompt design and schema obedience determine practical extraction quality.",
            "The framework is already useful for structured analysis and diagnostics, but broader benchmarking still requires stronger expert reference data.",
        ],
    },
    {
        "title": "Thank You",
        "text": "Questions and discussion",
    },
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_table(table: dict[str, list[list[str]]]) -> str:
    headers = table["headers"]
    rows = table["rows"]
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [
        "| " + " | ".join(headers) + " |",
        sep,
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_marp_slide(slide: dict[str, object]) -> str:
    parts: list[str] = []
    if slide.get("section"):
        parts.append(f"<!-- _header: {slide['section']} -->")
    parts.append(f"## {slide['title']}")
    if slide.get("subtitle"):
        parts.append(str(slide["subtitle"]))
    if slide.get("text"):
        parts.append(str(slide["text"]))
    if slide.get("image"):
        parts.append(f"![bg right:42% contain]({slide['image']})")
    if slide.get("images"):
        images = slide["images"]
        parts.append(
            '<div class="two-up">\n'
            f'  <img src="{images[0]}" alt="slide image 1" />\n'
            f'  <img src="{images[1]}" alt="slide image 2" />\n'
            "</div>"
        )
    if slide.get("bullets"):
        parts.append("\n".join(f"- {item}" for item in slide["bullets"]))
    if slide.get("table"):
        parts.append(render_table(slide["table"]))
    return "\n\n".join(parts)


def generate_marp() -> str:
    blocks = [
        "---",
        "marp: true",
        "theme: default",
        "paginate: true",
        "size: 16:9",
        "title: Toward an Executable ESG Aspect-Based Sentiment Analysis Framework",
        "style: |",
        "  section { font-size: 28px; }",
        "  h1, h2 { color: #143642; }",
        "  img { max-width: 100%; max-height: 440px; }",
        "  .two-up { display: flex; gap: 16px; align-items: center; justify-content: center; }",
        "  .two-up img { width: 48%; max-height: 360px; object-fit: contain; }",
        "---",
    ]
    for slide in SLIDES:
        blocks.append(render_marp_slide(slide))
        blocks.append("---")
    return "\n".join(blocks)


def render_quarto_slide(slide: dict[str, object]) -> str:
    parts: list[str] = [f"## {slide['title']}"]
    if slide.get("subtitle"):
        parts.append(str(slide["subtitle"]))
    if slide.get("text"):
        parts.append(str(slide["text"]))
    if slide.get("image"):
        parts.append(f"![]({slide['image']}){{fig-align=\"center\" width=\"88%\"}}")
    if slide.get("images"):
        images = slide["images"]
        parts.append(
            "::: columns\n"
            "::: {.column width=\"50%\"}\n"
            f"![]({images[0]}){{fig-align=\"center\" width=\"100%\"}}\n"
            ":::\n"
            "::: {.column width=\"50%\"}\n"
            f"![]({images[1]}){{fig-align=\"center\" width=\"100%\"}}\n"
            ":::\n"
            ":::"
        )
    if slide.get("bullets"):
        parts.append("\n".join(f"- {item}" for item in slide["bullets"]))
    if slide.get("table"):
        parts.append(render_table(slide["table"]))
    return "\n\n".join(parts)


def generate_quarto() -> str:
    blocks = [
        "---",
        'title: "Toward an Executable ESG Aspect-Based Sentiment Analysis Framework"',
        'subtitle: "Revision Presentation Based on the Standardized Thesis Chapters"',
        'author: "Daris Dzakwan Hoesien"',
        'format:',
        '  revealjs:',
        '    theme: default',
        '    slide-number: true',
        '    chalkboard: false',
        '    incremental: false',
        '    width: 1600',
        '    height: 900',
        "execute:",
        "  echo: false",
        "---",
        "",
        "## Presentation Scope",
        "",
        "- Research framing",
        "- Methodology and data flow",
        "- Experiments and empirical findings",
        "- Discussion, limitations, and future work",
        "- Appendix and reproducibility",
        "",
    ]
    current_section = None
    for slide in SLIDES[2:]:
        if slide.get("section") and slide["section"] != current_section:
            current_section = slide["section"]
            blocks.append(f"# {current_section}")
            blocks.append("")
        blocks.append(render_quarto_slide(slide))
        blocks.append("")
    return "\n".join(blocks)


def main() -> None:
    write(MARP_DIR / "revision_presentation.md", generate_marp())
    write(QUARTO_DIR / "revision_presentation.qmd", generate_quarto())
    print(f"Wrote {MARP_DIR / 'revision_presentation.md'}")
    print(f"Wrote {QUARTO_DIR / 'revision_presentation.qmd'}")


if __name__ == "__main__":
    main()
