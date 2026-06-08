## Implementation Details

### Experimental Objective and Tested Methods

The purpose of the Chapter 4 experiments is to evaluate whether the implemented ESG pipeline can transform sustainability-report PDFs into structured, auditable ESG disclosure records, classify those records into ESG pillar, aspect, sentiment, and disclosure tone, compare tone outputs against ClimateBERT-style labels, and expose failure modes that matter for thesis validity. In practice, the experiments do not test one isolated model. They test a full repository workflow composed of OCR ingestion, LLM-based structured extraction, benchmark labeling, ontology alignment, and diagnostic dashboards.

The main method under evaluation is the repository’s staged ESG analysis framework. The first stage is OCR and page extraction, which converts PDF files into page-level markdown and OCR JSON. The second stage is T3 LLM extraction, which generates structured ESG records stored in results/esg_records.json. The third stage is the T1 comparison layer, where extracted record texts are compared against ClimateBERT-style classification outputs or their local proxy equivalents. The fourth stage is the T2 ABSA-style layer, which includes rule-based logic, classical machine learning, and a lightweight hybrid contextual model. The final layer aggregates outputs into ontology coverage tables, failure-mode summaries, agreement scores, and dashboard artifacts.

Several comparison approaches are already implemented in the codebase. code/rule_based.py provides a lexicon-driven baseline with explicit aspect, polarity, and tone triggers. code/classical_ml.py provides a classical TF-IDF plus logistic-regression baseline. code/hybrid_model.py provides a contextual multilingual hybrid representation that fuses sentence embeddings, section context, ontology vectors, and a document-level vector. In parallel, the LLM extraction layer compares prompt and model variants rather than relying on a single fixed prompt. This is important because the thesis problem is not only classification performance but also schema stability, field completion, and practical utility of extracted records.

The implemented prompt inventory includes seven primary prompt templates used in the thesis-facing stability analysis: data.md, tone_chain_of_thought_english.md, tone_chain_of_thought_indonesian.md, tone_few_shot_english.md, tone_few_shot_indonesian.md, tone_zero_shot_english.md, and tone_zero_shot_indonesian.md. These operationalize three prompting strategies: zero-shot, few-shot, and chain-of-thought, in both English and Indonesian. At the backend level, the code supports OpenRouter-hosted models, LM Studio or other OpenAI-compatible local endpoints, and Ollama-style local inference. The active results summarized in the thesis dashboard show that the most important model comparison for the current evidence layer is between arcee-ai/trinity-large-preview:free and openai/gpt-oss-120b:free, while additional live reprocess runs include arcee-ai/trinity-large-thinking:free, minimax/minimax-m2.5:free, and openai/gpt-oss-20b:free.

This design follows directly from Chapter 3. The methodology argued that a mixed and modular evaluation strategy is more appropriate than a single-model setup because ESG reports are bilingual, structurally inconsistent, and prone to OCR and schema noise. The Chapter 4 implementation therefore tests both final output quality and engineering reliability.

### Configuration, Infrastructure, and Reproducibility

The implementation is centered on a Python and Streamlit research workspace. The main system surface is a multi-page Streamlit application under pages/, supported by reusable logic in code/. Source data is stored under data/, derived artifacts under results/, prompt templates under prompt/, and documentation under documentation/. This structure is part of the experiment design because each stage writes stable intermediate artifacts that can be audited or reused later.

For OCR-expanded data, each processed document in data/thesis_dataset/ contains ocr_result.json, page markdown files, and extracted images. For extraction outputs, pages/llm_processing.py writes structured run objects to results/esg_records.json and background job state to results/background_llm_jobs/. For benchmark runs, pages/ground_truth.py writes resumable JSONL outputs to results/t1_results.jsonl and results/t2_results.jsonl. For thesis reporting, summary tables and figures are exported to results/revision_analysis/ and results/thesis_workflow_dashboard/.

The main feature-extraction and model settings are as follows. The rule-based model uses curated lexical triggers for aspect, polarity, and tone. The classical model uses word and character TF-IDF vectors with logistic regression and one-vs-rest classification for multi-label aspects. The hybrid model uses distilbert-base-multilingual-cased when available, with a lightweight hierarchical encoder and a fused prediction head. In code/hybrid_model.py, the encoder weights are frozen by default for fast CPU-friendly operation, and the architecture uses a small multi-head attention block for section interaction. This is appropriate for the current thesis environment because the repository is designed to be executable on local research hardware and interactive dashboards, not only on high-end training servers.

The experiment results also reflect the available compute environment. The active pipeline supports cloud LLM calls through OpenRouter and local model execution through LM Studio-compatible backends and downloaded Hugging Face-style models. ClimateBERT comparison in the current saved outputs mostly uses local downloaded models such as distilroberta-base-climate-commitment and related classification checkpoints, while the repository notes that a full one-to-one remote ClimateBERT benchmark is still future work. This constraint affects how results are interpreted: current ClimateBERT tables are meaningful as proxy validation, but not yet as a final external benchmark.

Reproducibility is one of the strongest implementation features of the codebase. The thesis dashboard report lists 1,220 result artifacts, 184 LLM background jobs, and persistent saved graph attachments. The repository explicitly states that visualizations can be regenerated by rerunning scripts such as code/visualize_tone_climatebert.py, while Streamlit pages such as 6_1_Chapter_4_Implementation_Results.py and 6_6_Chapter_4_Results_Visualizer.py provide live views over the same stored artifacts. The experiments are therefore reproducible in an engineering sense even where some semantic baselines remain incomplete.

## Evaluation Metrics

### Primary Metrics

The thesis uses several primary evaluation metrics because no single metric captures the full quality of this pipeline.

For RQ1, the main metric is OCR processing completion, measured as the number of documents successfully processed and the number of pages covered by the OCR-expanded corpus. In the current dashboard snapshot, 23 out of 23 OCR-tracked documents are marked done, covering approximately 5,512 pages. This metric is suitable because the first requirement of the system is operational: the pipeline must convert PDFs into usable intermediate artifacts before any downstream ESG analysis can occur.

For T3 extraction quality, the primary metrics are JSON parse success rate, average records per run, field completion rate, missing-tone rate, and schema-drift rate. JSON parse success rate measures whether a model and prompt combination produces structurally valid outputs. Average records per run measures extraction yield. Field completion rate measures how often the expected schema is actually filled. Missing-tone rate measures how often tone is omitted, which is critical because tone is the main thesis contribution. Schema-drift rate captures malformed or repurposed fields, such as tone values appearing in sentiment slots.

For classification and comparison tasks, percent agreement and Cohen’s kappa are used. Agreement captures raw overlap between the repository’s tone labels and ClimateBERT-style commitment labels, while Cohen’s kappa adjusts for chance agreement. In the saved summary, the comparison tone_commitment_vs_climate_commitment_label covers 332 records and yields 83.7% agreement with Cohen’s kappa of 0.645. Higher values indicate stronger alignment, but kappa is preferred over raw agreement alone because the commitment class is relatively frequent.

For representation and ontology quality, ontology coverage is used. This metric tracks whether extracted aspects can be mapped to ontology paths. In the current RQ4 summary, 52 aspects are tracked and all 52 are mapped to ontology paths. This does not prove perfect semantic correctness, but it measures whether the ontology layer is operational and comprehensive enough for downstream interpretation.

For company-level interpretive risk, the greenwashing index is used as a task-specific ratio between commitment and outcome records at document level. Higher values indicate a stronger imbalance toward promises relative to reported outcomes. The metric is useful because it translates the tone taxonomy into an interpretable governance and disclosure-risk signal, but it remains heuristic and is not yet externally validated.

### Secondary and Complementary Metrics

Basic metrics alone are insufficient because this pipeline is not a single-label classification benchmark. Additional metrics are needed to evaluate reliability, interpretability, and usefulness.

First, prompt stability metrics are used to assess how sensitive the extraction layer is to prompt formulation. These include prompt-level parse success, average records, missing-tone rate, schema-drift rate, and field completion. Second, model stability metrics assess whether apparent quality gains are robust across model families. Third, failure-mode counts are used to identify specific structural or linguistic conditions under which the system breaks down, including bilingual or code-switched text, modal or hedged language, passive constructions, regulatory Indonesian terms, table-heavy layouts, and explicit missing-tone cases.

Fourth, denominator audits are used to interpret results correctly. The file results/revision_analysis/chapter4_tone_denominator_audit.csv distinguishes corpus extraction coverage from tone-table denominators. For example, 5,444 units are used for total extracted-record coverage, but 4,853 units are used for tone distribution and agreement because 591 cases are excluded from those denominators and treated as missing-tone quality issues. This is methodologically important because agreement should not be inflated or distorted by invalid or absent tone outputs.

Fifth, lexical trigger counts serve as a lightweight explainability metric. They show how often action, commitment, outcome, hedge, passive, regulatory, and table-layout triggers co-occur with predicted tones. These metrics do not replace semantic evaluation, but they help explain why certain prompts or models tend to overpredict commitment or underdetect outcome language.

Taken together, these metrics provide a more complete evaluation frame. OCR metrics measure operational readiness. Parse and completion metrics measure extraction usability. Agreement metrics measure construct overlap. Ontology coverage measures semantic mapping readiness. Stability metrics measure robustness. Failure modes measure weakness concentration. Greenwashing ratios and lexical triggers provide task-specific interpretation beyond generic accuracy.

## Experimental Results

### RQ1 and RQ2: PDF-to-Structured ESG Evidence and Tone-Aware Schema

The first result is that the ingestion and extraction pipeline is operational at meaningful corpus scale. The OCR processing summary lists 23 processed documents, all marked as done, covering approximately 5,512 pages. The largest processed reports include Bank Neo Commerce Annual and Sustainable Report Tahun 2024.pdf with 694 pages, vktr_ar_sr_2024.pdf with 548 pages, and alfamart_sustainability_2025.pdf with 510 pages. This demonstrates that the pipeline is not restricted to short pilot inputs and can process large real-world corporate reports.

The second result is that the extraction layer produces a usable structured evidence set. The thesis dashboard report records 332 tone-bearing ESG records and 2,074 T2 rows. Among the 332 extracted records, the most common tone is commitment with 115 records, and the most common ESG pillar is environmental with 179 records. Governance contributes 121 records, while the social pillar appears only 4 times in the summary used by the thesis planning notes. This indicates that the schema is already expressive enough to separate tone from polarity and from ESG pillar, but it also reveals imbalance in the active sample.

Prompt-level extraction behavior is shown in Table 4.1.

*Caption: Prompt-level extraction performance*

{2.5pt}
{1.15}

>{}p{0.40}
    *{6}{>{}p{0.075}}

**Prompt**

**Runs**

& 16 & 1.000 & 6.25 & 0.0000 & 0.0037 & 0.3744

& 15 & 1.000 & 4.07 & 0.0028 & 0.0028 & 0.3315

& 15 & 1.000 & 0.00 & 0.0000 & 0.0000 & 0.0000

& 14 & 1.000 & 1.00 & 0.0000 & 0.0000 & 0.0714

& 14 & 1.000 & 3.93 & 0.0000 & 0.0000 & 0.3571

& 16 & 1.000 & 2.63 & 0.0000 & 0.0000 & 0.1250

These results show that parse success alone is not an adequate quality metric. Every prompt listed above reaches 100% parse success, yet their practical usefulness differs sharply. tone_chain_of_thought_english.md yields the highest average record count. In other words, a prompt can be syntactically valid and still be unsuitable for the core thesis task.

The denominator audit clarifies the scale of the tone-quality problem. Of 5,444 extracted units in the relevant coverage view, 591 are excluded from tone distribution and agreement because they represent missing-tone cases. This is a meaningful failure rate, not a negligible noise band. It supports the claim that tone extraction is the most fragile part of the schema and justifies treating missing-tone behavior as an explicit Chapter 4 result rather than a minor implementation bug.

Overall, RQ1 and RQ2 show that the repository can reliably transform PDFs into structured ESG artifacts and that the tone-aware schema is operational. However, they also show that extraction quality depends heavily on prompt design and that formal evaluation must go beyond raw parse success.

### RQ3 and RQ4: ClimateBERT Comparison, Diagnostics, and Failure Modes

The most important quantitative comparison result is the alignment between disclosure tone and ClimateBERT-style commitment labels. Table 4.2 summarizes the main agreement result.

*Caption: Prompt-level extraction performance*

{2.5pt}
{1.15}

>{}p{0.43}
    *{5}{>{}p{0.10}}

**Prompt**

**Runs**

& N & Percent Agreement & Cohen’s Kappa & Tone Commitment Rate & Climate Commitment Label Rate

& 332 & 0.8373 & 0.6451 & 0.3464 & 0.3645

This is a strong but not perfect alignment. The result suggests that the repository’s tone taxonomy captures a signal that overlaps substantially with climate-commitment detection, but the two constructs are not identical. This is theoretically useful because it supports the claim that tone adds a maturity or disclosure-function layer beyond climate-topic recognition.

The saved tone-by-ClimateBERT crosstab provides a more detailed view:

{|c|c|c|c|c|c|}

**Tone** & **Ambiguous Actions** & **Brown Projects** & **Misinformation** & **no** & **yes**

commitment & 12 & 860 & 6 & 61 & 54

action & 25 & 1391 & 37 & 56 & 2

outcome & 12 & 926 & 35 & 44 & 6

missing & 16 & 1710 & 82 & 78 & 31

Although the label space is broader than a single climate-commitment binary, the table shows that commitment records cluster differently from action and outcome records. In the thesis planning notes, commitment is most strongly associated with climate-commitment, climate-d, and environmental-claims, while action and outcome disperse more across governance and other label families. This pattern supports the idea that commitment language dominates environmental claim-making even when a record does not yet describe measurable outcome.

RQ4 shifts from success to weakness detection. The failure-mode count table is shown below.

{|c|c|c|}

**Failure Mode** & **Tone Predicted** & **Count**

missing_tone & missing & 61

schema_drift & missing & 19

hedged_or_modal_language & missing & 9

regulatory_or_indonesian_domain_terms & missing & 3

table_or_numeric_layout & missing & 3

passive_voice & missing & 2

bilingual_or_code_switched & action & 1

hedged_or_modal_language & action & 1

passive_voice & action & 1

schema_drift & action & 1

The dominant weakness is clear: 61 missing-tone cases. Beyond that, schema drift and hedged language are the next most important failure patterns. This means that the pipeline is more vulnerable to discursive ambiguity and formatting irregularity than to simple parser breakdown. The problem is therefore partly linguistic, not only technical.

Ontology coverage provides a positive counterweight. The current ontology table shows 52 aspects tracked and 52 mapped to ontology paths. The highest-frequency mapped aspects are climate-detection with 79 records, governance with 66, missing with 60, and none with 23. Below these, domain-specific concepts such as roadmap karbon, pelatihan antikorupsi, komitmen net zero, and implementasi eco-mechanized mining are mapped to structured paths anchored to GRI-, governance-, or climate-oriented categories. This indicates that the ontology layer is currently stronger in coverage than the tone layer is in stability.

These findings reveal an important contradiction. The system is semantically organized enough to map diverse ESG aspects to ontology paths, yet it is still fragile when asked to consistently distinguish commitment, action, and outcome in noisy or governance-heavy contexts. That contradiction becomes one of the central interpretive findings of the chapter.

### RQ5 and RQ6: Reproducibility, Visualization, and Stability

The repository performs strongly on reproducibility as an engineering system. The saved thesis dashboard report indexes 1,220 result artifacts and 184 LLM background jobs. Five static figures are already exported for thesis reuse: tone_distribution.png, esg_by_tone.png, aspect_by_tone_heatmap.png, climatebert_label_by_tone.png, and climatebert_remote_top_scores.png. In addition, the Chapter 4 Streamlit pages render live views over the same result tables, allowing the written thesis chapter and the interactive dashboard to remain aligned.

This reproducibility evidence matters because it shows that the research output is not dependent on one temporary notebook state. The file structure preserves both intermediate and summarized evidence. The pipeline can therefore be re-run, inspected, and extended without rebuilding the thesis reporting layer from scratch.

The strongest stability results appear in the model- and prompt-level summaries. Table 4.3 shows the current model comparison.

*Caption: Model-level extraction performance*

{2.5pt}
{1.15}

>{}p{0.43}
    *{5}{>{}p{0.10}}

**Model**

**Runs**

& 90 & 1.0000 & 3.02 & 0.0005 & 0.0011

& 20 & 1.0000 & 3.00 & 1.0000 & 0.4250

& 89 & 0.8989 & 12.52 & 0.0000 & 0.0000

& 776 & 0.5657 & 4.94 & 0.0005 & 0.0026

& 145 & 0.9586 & 1.13 & 0.0000 & 0.0000

The most important comparison for the thesis-facing stable subset is between arcee-ai/trinity-large-preview:free and openai/gpt-oss-120b:free. Both achieved perfect parse success in the summarized slice, but gpt-oss-120b exhibited a 100% missing-tone rate and a 42.5% schema-drift rate in the corresponding prompt-model grouping. This is a strong warning against treating model size or brand reputation as a proxy for task suitability. In this workflow, schema obedience and tone completion matter more than raw generative capability.

Prompt-level stability shows a similar pattern. Chain-of-thought prompts, especially in English, produce the highest average records per run, while data.md produces formally parseable but functionally unusable tone outputs. Few-shot prompts appear inconsistent: the English few-shot prompt yields no average extracted records in the current summary, while the Indonesian few-shot prompt yields very low completion. This suggests that examples alone do not guarantee better extraction. In this repository, explicit tone framing and schema-constrained instruction style appear more important.

These results reveal a practical trade-off. Some settings maximize extraction volume, while others maximize structural cleanliness. The best-performing configuration for this thesis is therefore not the one with the highest nominal complexity, but the one that balances parse success, tone completion, and manageable drift. This is exactly the type of engineering validity condition the chapter needs to report.

### Explainability Outputs

The explainability layer helps show why the pipeline behaves as it does. At implementation level, code/rule_based.py uses explicit lexical triggers for commitment, action, and outcome, while code/classical_ml.py provides TF-IDF coefficient tables and local explanations. The lexicon file contains signals such as berkomitmen, commitment, will, menargetkan, target, aim to, and dedicated to for commitment-oriented language, and telah, achieved, has been, and successfully for outcome-oriented language.

The lexical trigger count summary confirms that these categories shape predictions in practice. Commitment triggers co-occurred 53 times with commitment predictions, compared with 30 action and 36 missing cases. Outcome triggers co-occurred 18 times with outcome predictions, but also 19 times with missing predictions and 17 times with commitment predictions. This helps explain why boundary cases remain difficult: many disclosure segments contain future-oriented and achieved language at the same time, especially in mixed narrative-reporting sections.

Ontology-path evidence is also interpretable. Environmental and climate-oriented examples include roadmap karbon, komitmen net zero, kerja sama energi bersih, and teknologi ramah lingkungan. Governance examples include pelatihan antikorupsi, kebijakan konflik kepentingan, and sertifikasi smap. These mappings show that the system can convert raw disclosure terms into structured thematic paths that are suitable for later chapter interpretation.

Representative records help illustrate the difference between commitment, action, and outcome:
1.

Commitment example: “As a pioneer among industrial estate developers in Indonesia, BeFa is at the forefront of creating a green and eco-friendly industrial zone...” This record is labeled commitment, carries environmental claims, and receives a strong local climate-commitment prediction.

Outcome example: “Keberhasilan pembangunan fasilitas perakitan kendaraan listrik di Magelang menjadi tonggak penting...” This record is labeled outcome with positive sentiment because it describes a realized infrastructure milestone.

Action example: “Pada tanggal 10 Oktober 2023, Perusahaan dan MB menandatangani perjanjian kerja sama...” This record is labeled action because it describes a concrete agreement, but not yet a completed performance outcome.

These examples show that the tone taxonomy is meaningful in practice. The main challenge is not whether the categories are interpretable, but whether the extraction layer can assign them consistently across different prompts, models, and disclosure styles.

## Validation of Reference Data and Pseudo-Ground Truth

The current evaluation target is not a full expert-labeled benchmark. It is a layered reference system built from extracted records, ClimateBERT-style comparison labels, weak lexical suggestions, and pilot human annotation files. This reference layer therefore has to be evaluated in its own right.

The strongest available comparison source is the ClimateBERT proxy agreement table over 332 records. It provides broad coverage and acceptable agreement, but it remains a proxy because the repository itself notes that a full one-to-one external ClimateBERT benchmark is still incomplete. The pilot human annotation layer is represented by files such as pilot_ground_truth_seed.csv and pilot_ground_truth_annotations.csv. The dashboard report currently records 70 pilot labels, which is useful for review and disagreement analysis but not enough to serve as a definitive gold standard.

Qualitatively, the reference layer is partially trustworthy but still noisy. Many pilot rows are marked needs_review, which is appropriate and should be reported transparently. Several examples show disagreement between predicted tone and suggested tone. For instance, some governance or agreement-signing records are predicted as action but receive commitment-oriented heuristic suggestions because the text includes modal or forward-looking language. This is not merely annotation error; it reflects the conceptual difficulty of distinguishing action from commitment in governance-heavy sustainability language.

The repository also preserves invalid or weak reference cases rather than silently filtering them. Missing-tone and schema-drift rows remain visible in the review files. This is methodologically sound because it prevents the evaluation set from becoming artificially clean. At the same time, it means that the current reference layer should be described as a pilot pseudo-ground-truth framework rather than a finalized benchmark corpus.

Overall, the selected reference system is reliable enough for exploratory evaluation, disagreement analysis, and chapter-level empirical claims about patterns and failure modes. It is not yet reliable enough for definitive benchmark claims about absolute model superiority.

## Comparative Component Analysis and Ablation-Like Findings

The repository does not yet contain a full controlled ablation study in the strict machine-learning sense, where one component at a time is removed under a fixed benchmark and identical evaluation set. However, the existing results do support an ablation-like comparative analysis across prompts, models, and representational choices. This section therefore addresses the checklist requirement cautiously and explicitly.

The first ablation-like finding concerns the prompt layer. If prompt framing is treated as a removable component, then tone-specific chain-of-thought prompting is the most important component for usable T3 extraction. Replacing it with the generic data.md prompt preserves JSON parse success but causes catastrophic tone failure. This indicates that explicit tone instruction is more important than generic extraction framing for the thesis task.

The second finding concerns model choice. If model family is treated as a removable or swappable component, then not all large language models are equivalent. arcee-ai/trinity-large-preview:free produces stable parse and tone behavior in the thesis-facing subset, whereas openai/gpt-oss-120b:free shows unacceptable tone omission and schema drift in the summarized grouping. This means the pipeline depends more strongly on schema-following behavior than on raw model scale.

The third finding concerns representation type. The repository’s architecture suggests three feature regimes: handcrafted lexical features, sparse learned features, and contextual fused features. The rule-based model offers maximum interpretability and is useful for explainability and error diagnosis, but it is brittle under ambiguity. The classical TF-IDF model offers reproducible statistical baselines and coefficient-level explanations, but it is limited by sparse surface-form dependence. The hybrid contextual model is designed to capture sentence meaning, section context, and ontology information together, making it the most conceptually complete architecture. The current Chapter 4 evidence, however, is stronger for prompt/model stability than for full benchmark comparison among these three ABSA components, because the saved thesis dashboard focuses on pipeline evidence rather than controlled classifier benchmarking.

The fourth finding concerns ontology integration. The ontology layer appears robust in coverage, which implies that aspect-to-path mapping is not currently the most fragile component. If any component is most responsible for pipeline weakness, it is the tone-label production step rather than the ontology layer.

These component comparisons lead to a clear synthesis. The most important component of the implemented system is the prompt-and-schema design of the extraction layer, followed by the choice of model backend that can reliably honor that schema. Contextual and ontology-aware representations remain important for interpretability and future benchmarking, but the present evidence shows that extraction stability is the prerequisite for all later gains.

## Chapter Synthesis

The main findings of Chapter 4 are fivefold.

First, the pipeline successfully operationalizes PDF-to-structured ESG extraction over a nontrivial document set: 23 processed reports and roughly 5,512 OCR-covered pages. Second, the extraction layer produces a meaningful evidence store with 332 tone-bearing records and 2,074 T2 rows, confirming that the proposed schema is practically usable. Third, tone commitment aligns strongly with ClimateBERT-style commitment labels, with 83.7% agreement and Cohen’s kappa of 0.645, which supports the construct relevance of the tone taxonomy. Fourth, the major weakness of the system is not parser failure but tone instability, especially missing-tone cases and schema drift under certain prompt settings. Fifth, the most important determinant of usable output is the interaction between prompt design and model compliance, not simply model scale.

The best overall thesis-facing configuration in the current saved evidence is the one represented by arcee-ai/trinity-large-preview:free with tone-focused prompts, because it combines high parse success with low missing-tone and low schema-drift rates. The most important system component is the tone-aware extraction prompt design. The main trade-off is between broad extraction flexibility and schema reliability: settings that appear generically capable do not necessarily produce thesis-usable structured outputs.

These findings connect directly back to Chapter 3. The methodology emphasized modularity, provenance, bilingual robustness, and interpretability. Chapter 4 shows that these design choices were justified. The system works best when it preserves traceable intermediate artifacts, separates tone from sentiment, and treats disagreement as information rather than noise. These results also prepare the next chapter: the discussion can now interpret commitment dominance, governance-related tone failures, model disagreement, and ontology coverage as substantive findings rather than mere implementation artifacts.
