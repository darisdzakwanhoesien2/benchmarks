from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BEAMER_DIR = ROOT / "report_standardized" / "revision" / "Beamer"
OUTPUT_PATH = BEAMER_DIR / "revision_presentation.tex"


def build_beamer_tex() -> str:
    return r"""\documentclass[aspectratio=169]{beamer}
\usetheme{Madrid}
\usecolortheme{default}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{caption}[numbered]

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{hyperref}

\title{Toward an Executable ESG Aspect-Based Sentiment Analysis Framework}
\subtitle{Revision Presentation Based on the Standardized Thesis Chapters}
\author{Daris Dzakwan Hoesien}
\institute{University of Oulu}
\date{\today}

\graphicspath{
  {../../../results/visualizations/}
  {../../Toward_an_Executable_ESG_Aspect_Based_Sentiment_Analysis_Framework_for_Indonesian_Sustainability_Reports__1_/Figures/}
}

\begin{document}

\begin{frame}
  \titlepage
\end{frame}

\begin{frame}{Presentation Scope}
  \tableofcontents
\end{frame}

\section{Research Framing}

\begin{frame}{Problem Context}
  \begin{itemize}
    \item Indonesian sustainability reports are long, bilingual, and structurally heterogeneous.
    \item Document-level ESG scoring is too coarse for tracing whether a statement is a promise, action, or realized outcome.
    \item The thesis reframes ESG analysis as record-level evidence extraction with four linked fields: aspect, ESG pillar, sentiment, and disclosure tone.
    \item The research target is not only prediction quality, but also provenance, auditability, ontology alignment, and reproducible workflow structure.
  \end{itemize}
\end{frame}

\begin{frame}{Research Questions}
  \begin{itemize}
    \item \textbf{RQ1. ESG ABSA Schema:} How can ESG disclosures be represented using a record-level schema integrating aspect, pillar, sentiment, and tone?
    \item \textbf{RQ2. Tone vs. Climate-Specific Models:} How do LLM-generated tone labels compare with ClimateBERT-style outputs?
    \item \textbf{RQ3. Pipeline Diagnostics:} What failure modes characterize automated ESG extraction?
    \item \textbf{RQ4. Stability and Reproducibility:} How stable are outputs across prompts, models, and providers?
  \end{itemize}
\end{frame}

\begin{frame}{Main Contributions}
  \begin{itemize}
    \item An executable OCR-to-ESG workflow implemented as a multi-page Streamlit research system.
    \item A record-level ESG schema that separates commitment, action, and outcome from generic positive sentiment.
    \item A layered evaluation design combining prompt diagnostics, model diagnostics, ontology mapping, ClimateBERT comparison, and pilot review.
    \item A reproducible artifact stack covering OCR folders, ESG extraction logs, benchmark JSONL files, revision analytics, and dashboard visualizations.
  \end{itemize}
\end{frame}

\section{Methodology}

\begin{frame}{Methodological Overview}
  \begin{figure}
    \centering
    \includegraphics[width=0.88\linewidth]{03_01_overview.png}
  \end{figure}
  \begin{itemize}
    \item The pipeline moves from raw PDF reports to OCR-expanded pages, structured ESG records, benchmark layers, and thesis-ready analytics.
    \item The design is mixed-method and executable: automated extraction is paired with provenance and review surfaces.
  \end{itemize}
\end{frame}

\begin{frame}{System Architecture}
  \begin{figure}
    \centering
    \includegraphics[width=\linewidth]{03_01_01_system_architecture.png}
  \end{figure}
\end{frame}

\begin{frame}{Data Sources and Corpus Shape}
  \begin{columns}[T]
    \begin{column}{0.58\linewidth}
      \begin{itemize}
        \item Raw source layer: sustainability and annual report PDFs in \texttt{data/thesis\_pdf/}.
        \item OCR-expanded layer: document folders in \texttt{data/thesis\_dataset/} with \texttt{ocr\_result.json}, page markdown, and images.
        \item Active thesis-facing subset: 23 processed reports, about 5{,}512 pages, 332 tone-bearing records, and 2{,}074 T2 rows.
        \item Support data includes ontology resources, pilot annotations, benchmark artifacts, and dashboard exports.
      \end{itemize}
    \end{column}
    \begin{column}{0.42\linewidth}
      \begin{figure}
        \centering
        \includegraphics[width=\linewidth]{03_02_data_sources.png}
      \end{figure}
    \end{column}
  \end{columns}
\end{frame}

\begin{frame}{Preprocessing and Provenance Design}
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{03_02_02.png}
  \end{figure}
  \begin{itemize}
    \item Page-level OCR artifacts are the core provenance unit.
    \item Later extraction and validation stages preserve links back to document folders and page markdown.
  \end{itemize}
\end{frame}

\begin{frame}{Feature and Representation Strategy}
  \begin{figure}
    \centering
    \includegraphics[width=0.84\linewidth]{03_04.png}
  \end{figure}
  \begin{itemize}
    \item The workflow combines rule-based lexical cues, TF-IDF baselines, contextual hybrid embeddings, and ontology-aware representations.
  \end{itemize}
\end{frame}

\begin{frame}{Framework Split}
  \begin{columns}[T]
    \begin{column}{0.52\linewidth}
      \begin{figure}
        \centering
        \includegraphics[width=\linewidth]{03_05.png}
      \end{figure}
    \end{column}
    \begin{column}{0.48\linewidth}
      \begin{itemize}
        \item \textbf{Framework 1:} page-aware LLM extraction into structured ESG records.
        \item \textbf{Framework 2:} benchmarking, comparison, ontology mapping, and evidence scoring.
        \item The thesis contribution is the end-to-end orchestration, not one isolated model.
      \end{itemize}
    \end{column}
  \end{columns}
\end{frame}

\begin{frame}{Reference Construction}
  \begin{columns}[T]
    \begin{column}{0.5\linewidth}
      \begin{figure}
        \centering
        \includegraphics[width=\linewidth]{03_06.png}
      \end{figure}
    \end{column}
    \begin{column}{0.5\linewidth}
      \begin{itemize}
        \item No full expert gold corpus exists yet.
        \item The thesis uses a layered reference design:
        \begin{itemize}
          \item extracted ESG records,
          \item ClimateBERT-style comparison labels,
          \item T1 and T2 JSONL artifacts,
          \item pilot human annotations.
        \end{itemize}
        \item This supports exploratory evaluation while keeping weak points visible.
      \end{itemize}
    \end{column}
  \end{columns}
\end{frame}

\begin{frame}{Methodology Summary}
  \begin{figure}
    \centering
    \includegraphics[width=0.82\linewidth]{03_07_summary.png}
  \end{figure}
\end{frame}

\section{Experiments}

\begin{frame}{Experimental Scope}
  \begin{itemize}
    \item The experiments evaluate a full workflow: OCR, T3 extraction, T1 ClimateBERT comparison, T2 ABSA-style processing, ontology mapping, and revision analytics.
    \item Prompt families include zero-shot, few-shot, and chain-of-thought variants in English and Indonesian.
    \item Backend families include OpenRouter, LM Studio or OpenAI-compatible endpoints, and Ollama-style local inference.
    \item The key evaluation focus is usable structured extraction, not parseability alone.
  \end{itemize}
\end{frame}

\begin{frame}{Evaluation Metrics}
  \begin{itemize}
    \item OCR completion at document and page level.
    \item Parse success, average extracted records, field completion, missing-tone rate, and schema-drift rate.
    \item Percent agreement and Cohen's kappa for tone versus ClimateBERT-style comparison.
    \item Ontology coverage and company-level commitment-outcome ratios for interpretive analysis.
    \item Failure-mode counts and denominator audits for pipeline diagnostics.
  \end{itemize}
\end{frame}

\begin{frame}{RQ1: Operational Schema Results}
  \begin{itemize}
    \item 23 OCR-processed documents were completed across approximately 5{,}512 pages.
    \item The active evidence layer contains 332 tone-bearing ESG records and 2{,}074 T2 rows.
    \item The schema supports simultaneous storage of text, aspect, ESG pillar, tone, sentiment, reasoning, and provenance.
    \item Ontology mapping covers all 52 tracked aspects in the thesis-facing subset.
  \end{itemize}
\end{frame}

\begin{frame}{Tone Distribution}
  \begin{figure}
    \centering
    \includegraphics[width=0.86\linewidth]{tone_distribution.png}
  \end{figure}
\end{frame}

\begin{frame}{ESG Distribution by Tone}
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{esg_by_tone.png}
  \end{figure}
\end{frame}

\begin{frame}{Aspect-by-Tone Structure}
  \begin{figure}
    \centering
    \includegraphics[width=0.92\linewidth]{aspect_by_tone_heatmap.png}
  \end{figure}
\end{frame}

\begin{frame}{Prompt-Level Extraction Results}
  \small
  \begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}X c c c}
    \toprule
    Prompt & Parse success & Avg. records & Missing tone \\
    \midrule
    \texttt{data.md} & 100.0\% & 3.00 & 100.0\% \\
    \texttt{tone\_cot\_en} & 100.0\% & 6.25 & 0.0\% \\
    \texttt{tone\_cot\_id} & 100.0\% & 4.07 & 0.3\% \\
    \texttt{tone\_few\_shot\_en} & 100.0\% & 0.00 & 0.0\% \\
    \texttt{tone\_few\_shot\_id} & 100.0\% & 1.00 & 0.0\% \\
    \texttt{tone\_zero\_shot\_en} & 100.0\% & 3.93 & 0.0\% \\
    \texttt{tone\_zero\_shot\_id} & 100.0\% & 2.62 & 0.0\% \\
    \bottomrule
  \end{tabularx}
  \vspace{0.5em}
  \begin{itemize}
    \item Parse validity is insufficient as a sole metric.
    \item Tone-aware chain-of-thought prompting is the strongest thesis-facing family.
  \end{itemize}
\end{frame}

\begin{frame}{RQ2: Tone vs. ClimateBERT}
  \begin{itemize}
    \item Tone commitment versus ClimateBERT-style commitment was evaluated over 332 records.
    \item The saved comparison reports 83.7\% agreement and Cohen's kappa of 0.645.
    \item The overlap is strong enough to support construct relevance, but not full label equivalence.
    \item ClimateBERT captures climate-topic or climate-commitment relevance; the tone taxonomy captures disclosure maturity.
  \end{itemize}
\end{frame}

\begin{frame}{Tone and ClimateBERT Cross-Distribution}
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{climatebert_label_by_tone.png}
  \end{figure}
\end{frame}

\begin{frame}{RQ3: Failure-Mode Diagnostics}
  \small
  \begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}X c >{\raggedright\arraybackslash}X}
    \toprule
    Failure mode & Count & Interpretation \\
    \midrule
    Missing tone & 61 & Core output field omitted despite otherwise parseable extraction \\
    Schema drift & 20 & Values placed in the wrong field or schema semantics shifted \\
    Hedged or modal language & 10 & Commitment-action boundary blurred by future-oriented phrasing \\
    Regulatory or Indonesian domain terms & 3 & Domain-specific wording weakens cue consistency \\
    Table or numeric layout & 3 & Tabular formatting disrupts semantic extraction \\
    Passive voice & 3 & Outcome versus action distinction becomes unstable \\
    Bilingual or code-switched & 1 & Mixed language complicates interpretation \\
    \bottomrule
  \end{tabularx}
\end{frame}

\begin{frame}{Failure-Mode Pareto}
  \begin{figure}
    \centering
    \includegraphics[width=0.92\linewidth]{failure_mode_pareto.png}
  \end{figure}
\end{frame}

\begin{frame}{Failure-Mode Composition}
  \begin{figure}
    \centering
    \includegraphics[width=0.8\linewidth]{failure_mode_pie.png}
  \end{figure}
\end{frame}

\begin{frame}{RQ4: Model Stability Trade-Off}
  \small
  \begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}X c c c}
    \toprule
    Model & Parse success & Avg. records & Short reading \\
    \midrule
    \texttt{trinity-large-preview} & 100.0\% & 3.02 & Best stable thesis-facing baseline \\
    \texttt{gpt-oss-120b} & 100.0\% & 3.00 & Parseable but unusable for tone \\
    \texttt{trinity-large-thinking} & 89.9\% & 12.52 & High yield, weaker formal stability \\
    \texttt{minimax-m2.5} & 56.6\% & 4.94 & High-volume use, weak parse reliability \\
    \texttt{gpt-oss-20b} & 95.9\% & 1.13 & Stable but low yield \\
    \bottomrule
  \end{tabularx}
  \vspace{0.5em}
  The decisive factor is schema-following behavior, not nominal model scale.
\end{frame}

\begin{frame}{Model Trade-Off Scatter}
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{model_tradeoff_scatter.png}
  \end{figure}
\end{frame}

\begin{frame}{Prompt Strategy Comparison}
  \begin{figure}
    \centering
    \includegraphics[width=0.9\linewidth]{prompt_strategy_comparison.png}
  \end{figure}
\end{frame}

\begin{frame}{Explainability-Oriented Graphs}
  \begin{columns}[T]
    \begin{column}{0.5\linewidth}
      \begin{figure}
        \centering
        \includegraphics[width=\linewidth]{information_density_by_tone.png}
      \end{figure}
    \end{column}
    \begin{column}{0.5\linewidth}
      \begin{figure}
        \centering
        \includegraphics[width=\linewidth]{soft_language_ratio_by_tone.png}
      \end{figure}
    \end{column}
  \end{columns}
  \begin{itemize}
    \item These charts help explain why commitment-heavy and soft-language segments create boundary failures.
  \end{itemize}
\end{frame}

\section{Discussion}

\begin{frame}{Discussion Synthesis}
  \begin{itemize}
    \item The thesis shows that ESG disclosure analysis becomes more informative when tone is modeled as a separate field from generic sentiment.
    \item The dominant evidence pattern is commitment-heavy environmental disclosure rather than outcome-heavy reporting.
    \item The strongest configuration is a tone-aware prompt paired with a schema-obedient model.
    \item Ontology coverage is comparatively robust; the main bottleneck is tone stability.
  \end{itemize}
\end{frame}

\begin{frame}{Research Question Resolution Summary}
  \small
  \begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}p{0.22\linewidth} >{\raggedright\arraybackslash}X >{\raggedright\arraybackslash}p{0.2\linewidth}}
    \toprule
    Research question & Core evidence & Status \\
    \midrule
    RQ1 & OCR-complete subset, structured records, ontology mapping & Answered positively \\
    RQ2 & 83.7\% agreement, kappa 0.645, meaningful divergence & Answered positively with qualification \\
    RQ3 & Missing tone, schema drift, ambiguity-rich failures & Answered diagnostically \\
    RQ4 & Stored artifacts, prompt and model trade-offs, rerunnable outputs & Answered positively with stability caveat \\
    \bottomrule
  \end{tabularx}
\end{frame}

\begin{frame}{Commitment-Outcome Screening Gap}
  \begin{figure}
    \centering
    \includegraphics[width=0.88\linewidth]{greenwashing_gap_scatter.png}
  \end{figure}
\end{frame}

\begin{frame}{Tone Share Ratio}
  \begin{figure}
    \centering
    \includegraphics[width=0.88\linewidth]{commitment_outcome_ratio.png}
  \end{figure}
\end{frame}

\begin{frame}{Limitations}
  \begin{itemize}
    \item The evaluation layer is still partly weakly supervised and not yet a complete expert-coded gold benchmark.
    \item The active evidence subset is domain-concentrated and environmentally skewed.
    \item Prompt and model sensitivity remain material; backend substitution is not safe by default.
    \item Greenwashing-style ratios are heuristic screening aids, not final adjudicative scores.
  \end{itemize}
\end{frame}

\begin{frame}{Future Work}
  \begin{itemize}
    \item Expand pilot review into a stratified expert benchmark with inter-annotator agreement.
    \item Tighten tone-specific prompting and schema validation with targeted rerun logic.
    \item Add OCR quality baselines so upstream noise can be separated from downstream extraction failure.
    \item Complete one-to-one ClimateBERT benchmarking over the full extracted record layer.
    \item Extend the framework toward analyst-facing review tools and graph-based retrieval workflows.
  \end{itemize}
\end{frame}

\section{Appendix and Reproducibility}

\begin{frame}{Operational User Workflow}
  \begin{itemize}
    \item Bulk OCR accepts uploaded or server-side PDFs and stores OCR-expanded artifacts under \texttt{data/thesis\_dataset/}.
    \item LLM Processing loads one OCR-expanded document, allows page-range selection, and sends batches to one of three provider families.
    \item Structured ESG records are stored in \texttt{results/esg\_records.json}.
    \item ClimateBERT or local comparison models operate downstream as the T1 comparison layer.
  \end{itemize}
\end{frame}

\begin{frame}{Appendix Workflow Figure}
  \begin{figure}
    \centering
    \includegraphics[width=0.88\linewidth]{03_01_overview.png}
  \end{figure}
  \begin{itemize}
    \item The appendix adds procedural detail on page-range processing, provider choice, and downstream comparison artifacts.
  \end{itemize}
\end{frame}

\begin{frame}{Repository JSON Artifact Families}
  \begin{itemize}
    \item \texttt{ocr\_result.json}: page-level OCR outputs and image metadata.
    \item \texttt{results/esg\_records.json}: structured T3 extraction runs and records.
    \item \texttt{results/t1\_results.jsonl} and \texttt{results/t2\_results.jsonl}: resumable benchmark layers.
    \item \texttt{results/revision\_analysis/ontology.json}: ontology paths and mapped ESG concepts.
    \item Dashboard and workflow JSON files support narrative reporting, transfer summaries, and Streamlit page relationships.
  \end{itemize}
\end{frame}

\begin{frame}{Reproducibility Strengths}
  \begin{itemize}
    \item The revision workflow indexes 1{,}220 stored result artifacts and 184 background jobs.
    \item Prompt templates, logs, JSONL files, visualizations, and chapter-ready outputs are persisted on disk.
    \item The strongest reproducibility claim is workflow and artifact persistence.
    \item Exact third-party LLM semantic outputs may still vary across time, providers, and model updates.
  \end{itemize}
\end{frame}

\section{Conclusion}

\begin{frame}{Closing Takeaways}
  \begin{itemize}
    \item The thesis demonstrates a viable end-to-end framework for converting Indonesian sustainability reports into auditable ESG evidence.
    \item The most important substantive insight is that commitment-heavy disclosure dominates the current extracted layer.
    \item The most important technical insight is that prompt design and schema obedience determine practical extraction quality.
    \item The framework is already useful for structured analysis and diagnostics, but broader benchmarking still requires stronger expert reference data.
  \end{itemize}
\end{frame}

\begin{frame}{Thank You}
  \centering
  Questions and discussion
\end{frame}

\end{document}
"""


def main() -> None:
    BEAMER_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_beamer_tex(), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
