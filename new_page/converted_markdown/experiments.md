# Chapter 4 Experiments

## 4.1 Experimental Scope and Protocol

### 4.1.1 Experimental Objective and Tested Methods

The purpose of the Chapter 4 experiments is to evaluate whether the implemented ESG pipeline can transform sustainability-report PDFs into structured, auditable ESG disclosure records, classify those records into ESG pillar, aspect, sentiment, and disclosure tone, compare tone outputs against ClimateBERT-style labels, and expose failure modes that matter for thesis validity. In practice, the experiments do not test one isolated model. They test a full repository workflow composed of OCR ingestion, LLM-based structured extraction, benchmark labeling, ontology alignment, and diagnostic dashboards.

The main method under evaluation is the repository’s staged ESG analysis framework. The first stage is OCR and page extraction, which converts PDF files into page-level markdown and OCR JSON. The second stage is T3 LLM extraction, which generates structured ESG records stored in results/esg_records.json. The third stage is the T1 comparison layer, where extracted record texts are compared against ClimateBERT-style classification outputs or their local proxy equivalents. The fourth stage is the T2 ABSA-style layer, which includes rule-based logic, classical machine learning, and a lightweight hybrid contextual model. The final layer aggregates outputs into ontology coverage tables, failure-mode summaries, agreement scores, and dashboard artifacts.

Several comparison approaches are already implemented in the codebase. code/rule_based.py provides a lexicon-driven baseline with explicit aspect, polarity, and tone triggers. code/classical_ml.py provides a classical TF-IDF plus logistic-regression baseline. code/hybrid_model.py provides a contextual multilingual hybrid representation that fuses sentence embeddings, section context, ontology vectors, and a document-level vector. In parallel, the LLM extraction layer compares prompt and model variants rather than relying on a single fixed prompt. This is important because the thesis problem is not only classification performance but also schema stability, field completion, and practical utility of extracted records.

The implemented prompt inventory includes seven primary prompt templates used in the thesis-facing stability analysis: data.md, tone_chain_of_thought_english.md, tone_chain_of_thought_indonesian.md, tone_few_shot_english.md, tone_few_shot_indonesian.md, tone_zero_shot_english.md, and tone_zero_shot_indonesian.md. These operationalize three prompting strategies: zero-shot, few-shot, and chain-of-thought, in both English and Indonesian. At the backend level, the code supports OpenRouter-hosted models, LM Studio or other OpenAI-compatible local endpoints, and Ollama-style local inference. The active results summarized in the thesis dashboard show that the most important model comparison for the current evidence layer is between arcee-ai/trinity-large-preview:free and openai/gpt-oss-120b:free, while additional live reprocess runs include arcee-ai/trinity-large-thinking:free, minimax/minimax-m2.5:free, and openai/gpt-oss-20b:free.

This design follows directly from Chapter 3. The methodology argued that a mixed and modular evaluation strategy is more appropriate than a single-model setup because ESG reports are bilingual, structurally inconsistent, and prone to OCR and schema noise. The Chapter 4 implementation therefore tests both final output quality and engineering reliability.

### 4.1.2 Configuration, Infrastructure, and Reproducibility

The implementation is centered on a Python and Streamlit research workspace. The main system surface is a multi-page Streamlit application under pages/, supported by reusable logic in code/. Source data is stored under data/, derived artifacts under results/, prompt templates under prompt/, and documentation under documentation/. This structure is part of the experiment design because each stage writes stable intermediate artifacts that can be audited or reused later.

For OCR-expanded data, each processed document in data/thesis_dataset/ contains ocr_result.json, page markdown files, and extracted images. For extraction outputs, pages/llm_processing.py writes structured run objects to results/esg_records.json and background job state to results/background_llm_jobs/. For benchmark runs, pages/ground_truth.py writes resumable JSONL outputs to results/t1_results.jsonl and results/t2_results.jsonl. For thesis reporting, summary tables and figures are exported to results/revision_analysis/ and results/thesis_workflow_dashboard/.

The main feature-extraction and model settings are as follows. The rule-based model uses curated lexical triggers for aspect, polarity, and tone. The classical model uses word and character TF-IDF vectors with logistic regression and one-vs-rest classification for multi-label aspects. The hybrid model uses distilbert-base-multilingual-cased when available, with a lightweight hierarchical encoder and a fused prediction head. In code/hybrid_model.py, the encoder weights are frozen by default for fast CPU-friendly operation, and the architecture uses a small multi-head attention block for section interaction. This is appropriate for the current thesis environment because the repository is designed to be executable on local research hardware and interactive dashboards, not only on high-end training servers.

The experiment results also reflect the available compute environment. The active pipeline supports cloud LLM calls through OpenRouter and local model execution through LM Studio-compatible backends and downloaded Hugging Face-style models. ClimateBERT comparison in the current saved outputs mostly uses local downloaded models such as distilroberta-base-climate-commitment and related classification checkpoints, while the repository notes that a full one-to-one remote ClimateBERT benchmark is still future work. This constraint affects how results are interpreted: current ClimateBERT tables are meaningful as proxy validation, but not yet as a final external benchmark.

Reproducibility is one of the strongest implementation features of the codebase. The thesis dashboard report lists 1,220 result artifacts, 184 LLM background jobs, and persistent saved graph attachments. The repository explicitly states that visualizations can be regenerated by rerunning scripts such as code/visualize_tone_climatebert.py, while Streamlit pages such as 6_1_Chapter_4_Implementation_Results.py and 6_6_Chapter_4_Results_Visualizer.py provide live views over the same stored artifacts. The experiments are therefore reproducible in an engineering sense even where some semantic baselines remain incomplete.

### 4.1.3 Evaluation Boundaries and Comparison Conditions

Not all Chapter 4 results use the same denominator or the same evidence layer, so each comparison must be interpreted against its own subset. OCR completion refers to the tracked processed-document layer. Tone distributions and agreement tables refer to the active extracted-record layer after additional validity filtering. Pilot annotation observations refer to a smaller review-oriented subset. For that reason, the chapter avoids treating every reported number as if it came from one unified benchmark corpus.

Comparison fairness is strongest when the same extracted text unit is preserved across later stages. This is the case for the main tone-versus-ClimateBERT comparison workflow, where record-level text and record identifiers are preserved for downstream comparison. By contrast, prompt and model comparisons should be interpreted as controlled configuration comparisons only when the same data slice and the same acceptance rules are held constant. Where those conditions are not perfectly fixed, the thesis treats the results as diagnostic evidence rather than as definitive head-to-head benchmark rankings.

## 4.2 Evaluation Metrics

### 4.2.1 Primary Metrics

The thesis uses several primary evaluation metrics because no single metric captures the full quality of this pipeline.

For RQ1, the main metric is OCR processing completion, measured as the number of documents successfully processed and the number of pages covered by the OCR-expanded corpus. In the current dashboard snapshot, 23 out of 23 OCR-tracked documents are marked done, covering approximately 5,512 pages. This metric is suitable because the first requirement of the system is operational: the pipeline must convert PDFs into usable intermediate artifacts before any downstream ESG analysis can occur.

For T3 extraction quality, the primary metrics are JSON parse success rate, average records per run, field completion rate, missing-tone rate, and schema-drift rate. JSON parse success rate measures whether a model and prompt combination produces structurally valid outputs. Average records per run measures extraction yield. Field completion rate measures how often the expected schema is actually filled. Missing-tone rate measures how often tone is omitted, which is critical because tone is the main thesis contribution. Schema-drift rate captures malformed or repurposed fields, such as tone values appearing in sentiment slots.

For classification and comparison tasks, percent agreement and Cohen’s kappa are used. Agreement captures raw overlap between the repository’s tone labels and ClimateBERT-style commitment labels, while Cohen’s kappa adjusts for chance agreement. In the saved summary, the comparison tone_commitment_vs_climate_commitment_label covers 332 records and yields 83.7% agreement with Cohen’s kappa of 0.645. Higher values indicate stronger alignment, but kappa is preferred over raw agreement alone because the commitment class is relatively frequent.

For representation and ontology quality, ontology coverage is used. This metric tracks whether extracted aspects can be mapped to ontology paths. In the current RQ4 summary, 52 aspects are tracked and all 52 are mapped to ontology paths. This does not prove perfect semantic correctness, but it measures whether the ontology layer is operational and comprehensive enough for downstream interpretation.

For company-level interpretive risk, the greenwashing index is used as a task-specific ratio between commitment and outcome records at document level. Higher values indicate a stronger imbalance toward promises relative to reported outcomes. The metric is useful because it translates the tone taxonomy into an interpretable governance and disclosure-risk signal, but it remains heuristic and is not yet externally validated.

### 4.2.2 Secondary and Complementary Metrics

Basic metrics alone are insufficient because this pipeline is not a single-label classification benchmark. Additional metrics are needed to evaluate reliability, interpretability, and usefulness.

First, prompt stability metrics are used to assess how sensitive the extraction layer is to prompt formulation. These include prompt-level parse success, average records, missing-tone rate, schema-drift rate, and field completion. Second, model stability metrics assess whether apparent quality gains are robust across model families. Third, failure-mode counts are used to identify specific structural or linguistic conditions under which the system breaks down, including bilingual or code-switched text, modal or hedged language, passive constructions, regulatory Indonesian terms, table-heavy layouts, and explicit missing-tone cases.

Fourth, denominator audits are used to interpret results correctly. The file results/revision_analysis/chapter4_tone_denominator_audit.csv distinguishes corpus extraction coverage from tone-table denominators. For example, 5,444 units are used for total extracted-record coverage, but 4,853 units are used for tone distribution and agreement because 591 cases are excluded from those denominators and treated as missing-tone quality issues. This is methodologically important because agreement should not be inflated or distorted by invalid or absent tone outputs.

Fifth, lexical trigger counts serve as a lightweight explainability metric. They show how often action, commitment, outcome, hedge, passive, regulatory, and table-layout triggers co-occur with predicted tones. These metrics do not replace semantic evaluation, but they help explain why certain prompts or models tend to overpredict commitment or underdetect outcome language.

Taken together, these metrics provide a more complete evaluation frame. OCR metrics measure operational readiness. Parse and completion metrics measure extraction usability. Agreement metrics measure construct overlap. Ontology coverage measures semantic mapping readiness. Stability metrics measure robustness. Failure modes measure weakness concentration. Greenwashing ratios and lexical triggers provide task-specific interpretation beyond generic accuracy.

## 4.3 Experimental Results

### 4.3.1 RQ1: ESG ABSA Schema

RQ1 asks how ESG disclosures can be represented effectively through a record-level schema that integrates aspect, ESG pillar, sentiment, and tone. The Chapter 4 results show that the proposed schema is operational and expressive enough to support that goal in the current thesis-facing subset.

The first result relevant to RQ1 is that the ingestion and extraction pipeline is operational at meaningful corpus scale. The OCR processing summary lists 23 processed documents, all marked as done, covering approximately 5,512 pages. The largest processed reports include Bank Neo Commerce Annual and Sustainable Report Tahun 2024.pdf with 694 pages, vktr_ar_sr_2024.pdf with 548 pages, and alfamart_sustainability_2025.pdf with 510 pages. This demonstrates that the schema is not being tested only on short pilot inputs, but on long, structurally varied corporate reports.

The second result is that the extraction layer produces a usable structured evidence set. The thesis dashboard report records 332 tone-bearing ESG records and 2,074 T2 rows. Among the 332 extracted records, the most common tone is commitment with 115 records, and the most common ESG pillar is environmental with 179 records. Governance contributes 121 records, while the social pillar appears only 4 times in the summary used by the thesis planning notes. This indicates that the schema is already expressive enough to separate tone from polarity and from ESG pillar, but it also reveals imbalance in the active sample.

Figure 4.1 and Figure 4.2 should be inserted here because they make the basic record composition visually transparent before the chapter moves into agreement and failure analysis.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/tone_distribution}
\end{center}
\caption{Tone distribution across the active extracted-record layer. This figure supports RQ2 by showing that commitment is the dominant disclosure tone in the current thesis-facing subset.}
\alt{Bar chart showing the distribution of extracted records across tone categories, with commitment as the dominant class.}
\label{fig:tone_distribution}
\end{figure}

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/esg_by_tone}
\end{center}
\caption{ESG pillar distribution by tone. This figure shows that environmental and governance disclosures dominate the active evidence layer and helps explain why social-pillar findings remain comparatively weak.}
\alt{Stacked bar chart showing ESG pillar counts within each tone category, with environmental and governance records dominating the distribution.}
\label{fig:esg_by_tone}
\end{figure}

Prompt-level extraction behavior is shown in Table 4.1.

*Table 4.1: Prompt-level extraction performance across the thesis-facing subset. Recommended columns: prompt template, runs, parse success rate, average records, field completion rate, missing-tone rate, and schema-drift rate.*

These results show that parse success alone is not an adequate quality metric. Every prompt listed above reaches 100% parse success, yet their practical usefulness differs sharply. tone_chain_of_thought_english.md yields the highest average record count. In other words, a prompt can be syntactically valid and still be unsuitable for the core thesis task.

The denominator audit clarifies the scale of the tone-quality problem. Of 5,444 extracted units in the relevant coverage view, 591 are excluded from tone distribution and agreement because they represent missing-tone cases. This is a meaningful failure rate, not a negligible noise band. It supports the claim that tone extraction is the most fragile part of the schema and justifies treating missing-tone behavior as an explicit Chapter 4 result rather than a minor implementation bug.

Figure 4.3 should be inserted after Table 4.1 because it complements the aggregate tone distribution with aspect-level structure.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/aspect_by_tone_heatmap}
\end{center}
\caption{Aspect-by-tone heatmap for the active extracted-record layer. This figure supports RQ2 by showing which aspects are concentrated in commitment, action, or outcome language rather than only reporting overall counts.}
\alt{Heatmap showing how extracted ESG aspects are distributed across commitment, action, outcome, and other tone categories.}
\label{fig:aspect_by_tone_heatmap}
\end{figure}

The ontology layer strengthens the schema interpretation further. The current ontology table shows 52 aspects tracked and 52 mapped to ontology paths. This does not prove perfect semantic correctness, but it shows that the record-level schema is not only syntactically structured; it is also semantically linkable to a broader ESG concept layer. In practical terms, the schema supports page-linked extraction, multi-field labeling, and ontology-aligned interpretation in a single evidence structure.

Overall, RQ1 is answered positively within the current thesis scope. ESG disclosures can be represented through a record-level schema that integrates aspect, ESG pillar, sentiment, and tone, and that schema remains usable at realistic report scale. The main qualification is that class balance is uneven and tone completion remains more fragile than aspect or ontology coverage.

### 4.3.2 RQ2: Tone vs. Climate-Specific Models

RQ2 asks how LLM-generated tone labels compare with specialized outputs from models like ClimateBERT, and what that comparison reveals about the validity of automated ESG assessment. The most important quantitative result for this question is the alignment between disclosure tone and ClimateBERT-style commitment labels. Table 4.2 summarizes the main agreement result.

*Table 4.2: Tone-commitment versus ClimateBERT-style commitment comparison. Recommended columns: compared labels, number of records, percent agreement, Cohen's kappa, denominator note, and interpretation boundary.*

This is a strong but not perfect alignment. The result suggests that the repository’s tone taxonomy captures a signal that overlaps substantially with climate-commitment detection, but the two constructs are not identical. This is theoretically useful because it supports the claim that tone adds a maturity or disclosure-function layer beyond climate-topic recognition.

Figure 4.4 should be inserted with Table 4.2 because the crosstab structure is easier to interpret visually than in prose alone.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/climatebert_label_by_tone}
\end{center}
\caption{Cross-distribution of LLM tone labels and ClimateBERT-style labels. This figure supports RQ3 by showing where commitment aligns strongly and where action or outcome labels diverge from climate-topic categorization.}
\alt{Stacked chart comparing tone categories against ClimateBERT-style labels to show areas of overlap and divergence.}
\label{fig:climatebert_label_by_tone}
\end{figure}

The saved tone-by-ClimateBERT crosstab provides a more detailed view:

Although the label space is broader than a single climate-commitment binary, the table shows that commitment records cluster differently from action and outcome records. In the thesis planning notes, commitment is most strongly associated with climate-commitment, climate-d, and environmental-claims, while action and outcome disperse more across governance and other label families. This pattern supports the idea that commitment language dominates environmental claim-making even when a record does not yet describe measurable outcome.

The comparison therefore supports a qualified validity claim. Tone labels and ClimateBERT-style labels are strongly related at commitment level, which suggests that the tone taxonomy is not arbitrary. At the same time, the two systems answer different analytical questions. ClimateBERT-style outputs focus on climate-topic or climate-commitment relevance, whereas the tone schema asks whether a disclosure is a promise, an action, or an achieved outcome. The result is therefore best interpreted as partial construct alignment rather than label equivalence.

Overall, RQ2 is answered positively but with a clear boundary. LLM-generated tone labels overlap meaningfully with specialized climate-oriented outputs, especially for commitment language, but they should not be treated as interchangeable with climate-topic classification. The comparison supports the validity of the tone taxonomy as an additional analytical layer rather than as a replacement for specialized climate models.

### 4.3.3 RQ3: Pipeline Diagnostics

RQ3 asks what specific failure modes characterize the automated extraction of ESG records, including OCR-related data loss, schema problems, and ontology gaps. This is the research question where the Chapter 4 evidence is most explicitly diagnostic rather than comparative.

The failure-mode count table is shown below.

*Table 4.3: Failure-mode count table. Recommended columns: failure mode, count, share of reviewed failures, likely cause, and representative example.*

The dominant weakness is clear: 61 missing-tone cases. Beyond that, schema drift and hedged language are the next most important failure patterns. This means that the pipeline is more vulnerable to discursive ambiguity and formatting irregularity than to simple parser breakdown. The problem is therefore partly linguistic, not only technical.

Two additional graphs support the failure-analysis argument directly by separating absolute frequency from composition.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/failure_mode_pareto}
\end{center}
\caption{Failure-mode Pareto chart. This figure shows which small number of failure categories account for most observed extraction weakness in the current thesis-facing subset.}
\alt{Pareto chart showing failure categories ranked by count with a cumulative-percentage line highlighting the dominant sources of extraction weakness.}
\label{fig:failure_mode_pareto}
\end{figure}

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/failure_mode_pie}
\end{center}
\caption{Failure-mode composition. This figure shows the relative share of missing tone, schema drift, language ambiguity, layout-related issues, and other recorded failure categories.}
\alt{Pie chart showing the proportional composition of recorded failure categories such as missing tone, schema drift, and language ambiguity.}
\label{fig:failure_mode_pie}
\end{figure}

Ontology coverage provides a positive counterweight. The current ontology table shows 52 aspects tracked and 52 mapped to ontology paths. The highest-frequency mapped aspects are climate-detection with 79 records, governance with 66, missing with 60, and none with 23. Below these, domain-specific concepts such as roadmap karbon, pelatihan antikorupsi, komitmen net zero, and implementasi eco-mechanized mining are mapped to structured paths anchored to GRI-, governance-, or climate-oriented categories. This indicates that the ontology layer is currently stronger in coverage than the tone layer is in stability.

The denominator audit reinforces the diagnostic reading of these results. Of 5,444 extracted units in the relevant coverage view, 591 are excluded from tone distribution and agreement because they represent missing-tone cases. This is not a trivial cleanup issue. It shows that the extraction pipeline can remain operational while still failing on the central tone field often enough to distort downstream interpretation if those cases are ignored.

These findings reveal an important contradiction. The system is semantically organized enough to map diverse ESG aspects to ontology paths, yet it is still fragile when asked to consistently distinguish commitment, action, and outcome in noisy or governance-heavy contexts. That contradiction becomes one of the central interpretive findings of the chapter.

Overall, RQ3 is answered directly by the diagnostic evidence. The most important failure modes are missing tone, schema drift, hedged or modal language, and layout- or terminology-related ambiguity. OCR processing is operational at document level, but the central downstream weakness remains tone stability rather than ontology coverage.

### 4.3.4 RQ4: Stability and Reproducibility

RQ4 asks to what extent ESG extraction outputs remain stable across varying prompts, LLM models, and service providers. This question is answered through prompt-level stability summaries, model-level summaries, stored workflow artifacts, and the reproducibility structure of the repository.

The repository performs strongly on reproducibility as an engineering system. The saved thesis dashboard report indexes 1,220 result artifacts and 184 LLM background jobs. Five static figures are already exported for thesis reuse: tone_distribution.png, esg_by_tone.png, aspect_by_tone_heatmap.png, climatebert_label_by_tone.png, and climatebert_remote_top_scores.png. In addition, the Chapter 4 Streamlit pages render live views over the same result tables, allowing the written thesis chapter and the interactive dashboard to remain aligned.

This reproducibility evidence matters because it shows that the research output is not dependent on one temporary notebook state. The file structure preserves both intermediate and summarized evidence. The pipeline can therefore be re-run, inspected, and extended without rebuilding the thesis reporting layer from scratch. At the same time, this should not be confused with a claim that all third-party LLM outputs are exactly repeatable across time. The thesis claims reproducible workflow structure and artifact persistence more strongly than deterministic output identity.

The strongest stability results appear in the model- and prompt-level summaries. Table 4.3 shows the current model comparison.

*Table 4.4: Model-level extraction performance. Recommended columns: model, runs, parse success rate, average records, missing-tone rate, schema-drift rate, and short interpretation.*

The most important comparison for the thesis-facing stable subset is between arcee-ai/trinity-large-preview:free and openai/gpt-oss-120b:free. Both achieved perfect parse success in the summarized slice, but gpt-oss-120b exhibited a 100% missing-tone rate and a 42.5% schema-drift rate in the corresponding prompt-model grouping. This is a strong warning against treating model size or brand reputation as a proxy for task suitability. In this workflow, schema obedience and tone completion matter more than raw generative capability.

Figure 4.7 complements Table 4.4 because it makes the trade-off between formal stability and usable extraction output easier to read.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/model_tradeoff_scatter}
\end{center}
\caption{Model trade-off scatter plot with parse success on the x-axis and average extracted records on the y-axis. This figure helps separate models that are formally stable from those that are practically useful.}
\alt{Scatter plot comparing models by parse success and average extracted records, showing the trade-off between formal stability and practical extraction yield.}
\label{fig:model_tradeoff_scatter}
\end{figure}

Prompt-level stability shows a similar pattern. Chain-of-thought prompts, especially in English, produce the highest average records per run, while data.md produces formally parseable but functionally unusable tone outputs. Few-shot prompts appear inconsistent: the English few-shot prompt yields no average extracted records in the current summary, while the Indonesian few-shot prompt yields very low completion. This suggests that examples alone do not guarantee better extraction. In this repository, explicit tone framing and schema-constrained instruction style appear more important.

Figure 4.8 should be read together with the prompt-level results table because prompt-family trends are central to the argument that prompt design matters more than nominal prompting style labels.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/prompt_strategy_comparison}
\end{center}
\caption{Prompt-strategy comparison across average records, parse success, and field completion. The figure shows that chain-of-thought and tone-specific framing matter more than generic prompt validity alone.}
\alt{Three-panel comparison chart showing prompt templates across average extracted records, parse success, and field completion.}
\label{fig:prompt_strategy_comparison}
\end{figure}

These results reveal a practical trade-off. Some settings maximize extraction volume, while others maximize structural cleanliness. The best-performing configuration for this thesis is therefore not the one with the highest nominal complexity, but the one that balances parse success, tone completion, and manageable drift. This is exactly the type of engineering validity condition the chapter needs to report.

Overall, RQ4 is answered with an important qualification. The workflow is reproducible and stable in an engineering sense because prompts, outputs, logs, and derived artifacts are stored persistently, and because the same evaluation views can be regenerated. However, semantic output stability is not uniform across prompts, models, or providers. Stability depends strongly on prompt design and schema-following behavior, so the thesis can claim reproducible workflow structure more confidently than universally stable model behavior.

## 4.4 Explainability Outputs

The explainability layer helps show why the pipeline behaves as it does. At implementation level, code/rule_based.py uses explicit lexical triggers for commitment, action, and outcome, while code/classical_ml.py provides TF-IDF coefficient tables and local explanations. The lexicon file contains signals such as berkomitmen, commitment, will, menargetkan, target, aim to, and dedicated to for commitment-oriented language, and telah, achieved, has been, and successfully for outcome-oriented language.

The lexical trigger count summary confirms that these categories shape predictions in practice. Commitment triggers co-occurred 53 times with commitment predictions, compared with 30 action and 36 missing cases. Outcome triggers co-occurred 18 times with outcome predictions, but also 19 times with missing predictions and 17 times with commitment predictions. This helps explain why boundary cases remain difficult: many disclosure segments contain future-oriented and achieved language at the same time, especially in mixed narrative-reporting sections.

Two additional figures fit especially well in this subsection because they extend the explainability argument without requiring a new evaluation protocol.

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/information_density_by_tone}
\end{center}
\caption{Information-density by tone. This figure shows whether commitment, action, outcome, and none records differ systematically in word count and therefore in extraction complexity.}
\alt{Boxplot comparing record word counts across commitment, action, outcome, and none tone categories.}
\label{fig:information_density_by_tone}
\end{figure}

\begin{figure}[ht]
\begin{center}
  \includegraphics*[width=\textwidth]{results/visualizations/soft_language_ratio_by_tone}
\end{center}
\caption{Soft-language ratio by tone. This figure shows whether commitment records contain a higher proportion of soft or future-oriented verbs than action and outcome records, thereby giving a linguistic explanation for some tone-boundary failures.}
\alt{Boxplot comparing the ratio of soft or future-oriented verbs across commitment, action, and outcome tone categories.}
\label{fig:soft_language_ratio_by_tone}
\end{figure}

Ontology-path evidence is also interpretable. Environmental and climate-oriented examples include roadmap karbon, komitmen net zero, kerja sama energi bersih, and teknologi ramah lingkungan. Governance examples include pelatihan antikorupsi, kebijakan konflik kepentingan, and sertifikasi smap. These mappings show that the system can convert raw disclosure terms into structured thematic paths that are suitable for later chapter interpretation.

Representative records help illustrate the difference between commitment, action, and outcome:

1. Commitment example: “As a pioneer among industrial estate developers in Indonesia, BeFa is at the forefront of creating a green and eco-friendly industrial zone...” This record is labeled commitment, carries environmental claims, and receives a strong local climate-commitment prediction.
1. Outcome example: “Keberhasilan pembangunan fasilitas perakitan kendaraan listrik di Magelang menjadi tonggak penting...” This record is labeled outcome with positive sentiment because it describes a realized infrastructure milestone.
1. Action example: “Pada tanggal 10 Oktober 2023, Perusahaan dan MB menandatangani perjanjian kerja sama...” This record is labeled action because it describes a concrete agreement, but not yet a completed performance outcome.

These examples show that the tone taxonomy is meaningful in practice. The main challenge is not whether the categories are interpretable, but whether the extraction layer can assign them consistently across different prompts, models, and disclosure styles.

## 4.5 Validation of Reference Data and Pilot Reference Layer

The current evaluation target is not a full expert-labeled benchmark. It is a layered reference system built from extracted records, ClimateBERT-style comparison labels, weak lexical suggestions, and pilot human annotation files. This reference layer therefore has to be evaluated in its own right.

The strongest available comparison source is the ClimateBERT proxy agreement table over 332 records. It provides broad coverage and acceptable agreement, but it remains a proxy because the repository itself notes that a full one-to-one external ClimateBERT benchmark is still incomplete. The pilot human annotation layer is represented by files such as pilot_ground_truth_seed.csv and pilot_ground_truth_annotations.csv. The dashboard report currently records 70 pilot labels, which is useful for review and disagreement analysis but not enough to serve as a definitive gold standard.

Qualitatively, the reference layer is partially trustworthy but still noisy. Many pilot rows are marked needs_review, which is appropriate and should be reported transparently. Several examples show disagreement between predicted tone and suggested tone. For instance, some governance or agreement-signing records are predicted as action but receive commitment-oriented heuristic suggestions because the text includes modal or forward-looking language. This is not merely annotation error; it reflects the conceptual difficulty of distinguishing action from commitment in governance-heavy sustainability language.

The repository also preserves invalid or weak reference cases rather than silently filtering them. Missing-tone and schema-drift rows remain visible in the review files. This is methodologically sound because it prevents the evaluation set from becoming artificially clean. At the same time, it means that the current reference layer should be described as a pilot reference framework rather than a finalized benchmark corpus.

Overall, the selected reference system is reliable enough for exploratory evaluation, disagreement analysis, and chapter-level empirical claims about patterns and failure modes. It is not yet reliable enough for definitive benchmark claims about absolute model superiority.

## 4.6 Comparative Component Analysis

The repository does not yet contain a full controlled ablation study in the strict machine-learning sense, where one component at a time is removed under a fixed benchmark and identical evaluation set. However, the existing results do support a comparative component analysis across prompts, models, and representational choices. This section therefore addresses the checklist requirement cautiously and explicitly.

The first comparative finding concerns the prompt layer. If prompt framing is treated as a removable component, then tone-specific chain-of-thought prompting is the most important component for usable T3 extraction. Replacing it with the generic data.md prompt preserves JSON parse success but causes catastrophic tone failure. This indicates that explicit tone instruction is more important than generic extraction framing for the thesis task.

The second finding concerns model choice. If model family is treated as a removable or swappable component, then not all large language models are equivalent. arcee-ai/trinity-large-preview:free produces stable parse and tone behavior in the thesis-facing subset, whereas openai/gpt-oss-120b:free shows unacceptable tone omission and schema drift in the summarized grouping. This means the pipeline depends more strongly on schema-following behavior than on raw model scale.

The third finding concerns representation type. The repository’s architecture suggests three feature regimes: handcrafted lexical features, sparse learned features, and contextual fused features. The rule-based model offers maximum interpretability and is useful for explainability and error diagnosis, but it is brittle under ambiguity. The classical TF-IDF model offers reproducible statistical baselines and coefficient-level explanations, but it is limited by sparse surface-form dependence. The hybrid contextual model is designed to capture sentence meaning, section context, and ontology information together, making it the most conceptually complete architecture. The current Chapter 4 evidence, however, is stronger for prompt/model stability than for full benchmark comparison among these three ABSA components, because the saved thesis dashboard focuses on pipeline evidence rather than controlled classifier benchmarking.

The fourth finding concerns ontology integration. The ontology layer appears robust in coverage, which implies that aspect-to-path mapping is not currently the most fragile component. If any component is most responsible for pipeline weakness, it is the tone-label production step rather than the ontology layer.

These component comparisons lead to a clear synthesis. The most important component of the implemented system is the prompt-and-schema design of the extraction layer, followed by the choice of model backend that can reliably honor that schema. Contextual and ontology-aware representations remain important for interpretability and future benchmarking, but the present evidence shows that extraction stability is the prerequisite for all later gains.

Figure 4.11 should be added as a final integrative visual if the Sankey export is generated from the visualizer, because it would summarize how the most frequent aspects distribute across commitment, action, and outcome in one compact view.

## 4.7 Chapter Synthesis

The main findings of Chapter 4 are fivefold.

First, the pipeline successfully operationalizes PDF-to-structured ESG extraction over a nontrivial document set: 23 processed reports and roughly 5,512 OCR-covered pages. Second, the extraction layer produces a meaningful evidence store with 332 tone-bearing records and 2,074 T2 rows, confirming that the proposed schema is practically usable. Third, tone commitment aligns strongly with ClimateBERT-style commitment labels, with 83.7% agreement and Cohen’s kappa of 0.645, which supports the construct relevance of the tone taxonomy without collapsing it into climate-topic classification. Fourth, the major weakness of the system is not parser failure but tone instability, especially missing-tone cases and schema drift under certain prompt settings. Fifth, the most important determinant of usable output is the interaction between prompt design and model compliance, not simply model scale.

The best overall thesis-facing configuration in the current saved evidence is the one represented by arcee-ai/trinity-large-preview:free with tone-focused prompts, because it combines high parse success with low missing-tone and low schema-drift rates. The most important system component is the tone-aware extraction prompt design. The main trade-off is between broad extraction flexibility and schema reliability: settings that appear generically capable do not necessarily produce thesis-usable structured outputs.

These findings connect directly back to Chapter 3. The methodology emphasized modularity, provenance, bilingual robustness, and interpretability. Chapter 4 shows that these design choices were justified. The system works best when it preserves traceable intermediate artifacts, separates tone from sentiment, and treats disagreement as information rather than noise. These results also prepare the next chapter: the discussion can now interpret commitment dominance, governance-related tone failures, model disagreement, and ontology coverage as substantive findings rather than mere implementation artifacts.
