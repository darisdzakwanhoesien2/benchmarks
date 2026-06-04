# Chapter 4: Experiments

## 4.1. Implementation Details

This chapter presents the experimental implementation of the ESG ABSA pipeline described in Chapter 3. Whereas the previous chapter focused on methodological design, data architecture, and benchmark logic, the present chapter documents how the executable research workspace was instantiated in the current repository, what artifacts were produced, how the experiments were organized, and what empirical evidence can already be extracted from the existing implementation state.

The experiments were implemented as an executable multi-stage pipeline built in Python and exposed through a Streamlit multi-page application. This design was chosen for two reasons. First, the project is not limited to a single model-training script. It requires repeated movement between OCR inspection, structured extraction, validation, comparison, and thesis-facing interpretation. Second, Streamlit provides a practical environment for turning intermediate experiment artifacts into inspectable dashboards, making it possible to audit run-level behavior rather than only final summary tables.

At the system level, the implementation consists of five major operational layers:

1. source-document and OCR processing;
2. LLM-based ESG extraction;
3. T1 and T2 comparison layers for ClimateBERT and ABSA-style outputs;
4. ground-truth and revision-analysis tooling;
5. thesis-facing dashboards, visualizations, and semantic exports.

The OCR stage is centered around the PDF-to-text workflow represented by `pages/Bulk_OCR.py` and supporting audit interfaces. The role of this stage is to ingest sustainability-report PDFs, preserve document-level traceability, and create page-aware markdown outputs that can be used in downstream extraction. This stage is important because the experiments do not operate directly on raw PDFs. They operate on OCR-transformed page or batch text, which becomes the effective input corpus for the structured extraction process.

The extraction stage is centered around `pages/llm_processing.py`. This component acts as the main T3 layer of the pipeline. It receives OCR-derived text units, a chosen prompt template, and a selected model/provider configuration, then generates structured ESG records. In the current implementation, each run is treated as a discrete experiment object with associated metadata such as target document, prompt file, model identifier, status, and parsed output. The central record store for this stage is `results/esg_records.json`, which holds both successful and unsuccessful run information. This implementation detail matters because the thesis does not reduce experimentation to successful runs only. Failed runs, empty runs, and malformed outputs are preserved for audit.

The repository documentation for `2_0_LLM_Processing_Result_Visualizer.py` shows that the system already materializes three linked result layers:

- T1 model-level predictions in `results/predictions.json`,
- T2 ABSA outputs in `results/absa_results.json`,
- T3 structured ESG extraction outputs in `results/esg_records.json`.

This design makes the experiment environment richer than a single end-task classifier. T1 captures climate-model or model-level signals, T2 captures rule-based, classical, or hybrid ABSA-style behavior, and T3 captures LLM-mediated structured extraction. The existence of these three layers makes it possible to compare results across modeling paradigms and to identify where structured extraction diverges from simpler classification or climate-focused prediction.

At the interface level, the project is implemented as a multi-page Streamlit application. The documentation across `1_0_Revision_Analytics.md`, `0_9_Tone_ClimateBERT_Visualization.md`, `1_7_Research_Questions_Dashboard.md`, and related pages indicates that the current experimental dashboards cover the following functions:

- inspection of extracted records and run quality;
- prompt-stability analysis;
- ClimateBERT proxy comparison;
- greenwashing-index inspection;
- ontology coverage analysis;
- annotation coverage and disagreement review;
- and thesis-facing evidence synthesis.

This dashboard-oriented implementation is an important experimental detail because it means the experiments are not only computed; they are rendered in a form that supports qualitative verification, error tracing, and chapter integration.

The project also uses a hybrid execution model for LLM access. The methodology notes in `documentation/general.md` and related thesis planning files describe the system as combining cloud and local model access, specifically through OpenRouter-style remote APIs and LM Studio or comparable local-model execution. This is important in experimental terms because some results reflect provider behavior as well as prompt design. In the current project state, model variability is therefore an experimental variable rather than incidental infrastructure noise.

The file structure of the implementation also supports reproducibility. The current chapter is grounded in the repository’s persistent separation between:

- `data/` for corpus and OCR assets,
- `results/` for generated artifacts and summaries,
- `pages/` for experimental interfaces,
- `documentation/` for page-level and workflow documentation,
- and visualization folders for static experiment outputs.

This organization matters because it allows each result discussed in the experiments chapter to be linked back to a file, a dashboard, or a run artifact.

The implementation state documented in the current repository already includes a non-trivial evidence base. According to the thesis-facing summary in `thesis_paper_esg_absa.md` and the dashboard output catalog, the current experimental environment contains:

- 23 OCR documents,
- 332 structured ESG tone records,
- 2,074 T2 rows,
- approximately 40 tracked workflow artifacts,
- prompt-stability summaries,
- model-stability summaries,
- ontology coverage outputs,
- ClimateBERT comparison outputs,
- and silver-label plus ground-truth review files.

These quantities show that the implementation has moved beyond proof-of-concept UI scaffolding into a working experimental system with reusable outputs. At the same time, the chapter must be careful not to overstate what this means. The current implementation is strong on artifact generation, comparison workflows, and diagnostic visibility, but weaker on complete expert-labeled evaluation and fully matched model-vs-model benchmarking.

The repository also preserves image-based experiment outputs for thesis use. The saved dashboard output catalog in `documentation/streamlit_pages/1_7_Research_Questions_Dashboard_outputs.md` documents figures such as:

- `tone_distribution.png`,
- `esg_by_tone.png`,
- `climatebert_label_by_tone.png`,
- `aspect_by_tone_heatmap.png`,
- `climatebert_remote_top_scores.png`,
- and multiple dashboard screenshots linking research questions to evidence.

These outputs are important because the experiments are not only numerical. They are also visual and interpretive. In a thesis environment, these static figures serve as stable experiment artifacts that can be cited even when the live dashboard continues to evolve.

In implementation terms, the experiments in this chapter should therefore be understood as pipeline experiments rather than benchmark-only experiments. They test:

- whether OCR and extraction stages produce usable evidence,
- whether different prompts and models behave consistently,
- whether the resulting records align with ClimateBERT-style signals,
- whether current outputs can support provisional ground-truth workflows,
- and whether the full system is auditable enough to support a thesis contribution.

That framing is important because it clarifies the meaning of the results reported below. The chapter is not presenting a single fully supervised benchmark result. It is presenting the experimental state of an executable ESG ABSA research workspace built around structured ESG evidence records.

## 4.2. Evaluation Metrics

The evaluation metrics used in this chapter follow the layered metrics philosophy established in Chapter 3. Because the current implementation spans OCR, structured extraction, comparison modeling, proxy validation, and partial human annotation, the experiments cannot be summarized by one score alone. Instead, this chapter reports several complementary metric families, each tied to a specific component of the implementation.

The first metric family concerns extraction productivity and data yield. At the current implementation stage, basic but important output metrics include:

- number of OCR-processed source documents,
- number of structured ESG records,
- number of T2 rows,
- number of prompt templates represented in the extracted outputs,
- number of source targets,
- and number of tracked artifact outputs.

These counts are not superficial bookkeeping. They define the scale and maturity of the current experiment environment. For example, the presence of 332 structured ESG records is significant because it determines what kinds of descriptive analysis, prompt comparisons, and proxy validation claims are possible at the present stage.

The second metric family concerns structured extraction reliability. The revision-analytics documentation identifies the core metrics used for this purpose:

- JSON parse success rate,
- average records per run,
- missing tone rate,
- schema drift rate,
- field completion rate,
- empty-output rate,
- and counts of failed or unresolved runs.

These metrics are especially important for LLM-mediated extraction, where a model may generate text that appears reasonable but is not structurally reliable enough for automated analysis. In this thesis, an experiment is not counted as fully successful merely because the model returned text. It must produce parseable and meaningfully populated record fields. This makes parse success and field completion central metrics of experimental quality.

The third metric family concerns label comparison and agreement. The most visible example is the ClimateBERT proxy comparison, which the current dashboard reports using:

- percent agreement,
- Cohen’s kappa,
- comparison heatmaps,
- and discordant-case inspection.

The implementation summary currently reports ClimateBERT proxy agreement of `0.837` and Cohen’s kappa of `0.645`. These values are meaningful because they indicate that the LLM-derived tone taxonomy is neither random nor trivially identical to ClimateBERT-style labels. However, these metrics must be interpreted as proxy alignment metrics rather than definitive external-validation scores because the current remote ClimateBERT sample is limited.

The fourth metric family concerns formal evaluation against ground truth, where available. The dedicated metrics page (`1_3_Ground_Truth_Metrics.md`) defines the intended evaluation metrics for tone, ESG pillar, and aspect:

- accuracy,
- weighted precision,
- weighted recall,
- weighted F1,
- Cohen’s kappa,
- confusion matrices,
- and disagreement tables.

At the current implementation stage, these metrics are partially ready but depend on the availability of filled human labels. This means the metrics framework is fully defined in the system, but not yet fully populated for all rows. This is an important experimental fact: the evaluation design exists and is implemented, but the benchmark is still maturing.

The fifth metric family concerns prompt and model stability. The `1_0_Revision_Analytics` page directly computes or displays:

- prompt-level parse success,
- prompt-level record count,
- prompt-level missing tone rate,
- prompt-level schema drift rate,
- prompt-level field completion,
- and model-level stability summaries.

These metrics are critical because the experiments explicitly study whether different prompt strategies produce meaningfully different structured outputs. A system that produces good results only under a narrow prompt configuration is less robust than a system whose outputs remain stable across prompt families. Therefore, prompt stability is treated as a first-class evaluation dimension rather than a side note.

The sixth metric family concerns ontology and explainability coverage. The system already tracks ontology-related outputs such as ontology coverage tables and mapped/unmapped aspect summaries. These metrics do not directly measure predictive accuracy, but they are still part of experimental evaluation because the thesis claims not only that records can be extracted, but that they can be organized into interpretable ESG concept structures. High ontology coverage supports this claim; low coverage identifies areas where ontology extension is needed.

The seventh metric family concerns greenwashing-oriented interpretive analysis. The revision analytics page defines a rhetoric-to-results indicator using:

```text
greenwashing_index = (commitment + 0.5) / (outcome + 0.5)
```

This metric is used as a screening heuristic rather than a validated classification score. Its presence in the experiments chapter is still justified because one of the thesis contributions is to show that tone-aware record extraction can support downstream interpretive analytics. However, the chapter must be explicit that this index is exploratory and not yet externally validated.

Finally, evaluation in this chapter also includes artifact-level and dashboard-level evidence. The project preserves static screenshots and visualizations that summarize:

- record distributions,
- research-question coverage,
- sample-size adequacy,
- ClimateBERT comparison views,
- and current limitations.

These are not substitutes for formal metrics, but they are still part of the experimental evidence because they show what the current implementation can already render, audit, and explain.

Overall, the evaluation metrics of this chapter can be grouped into three broad purposes:

1. productivity metrics, which show that the system generates analyzable artifacts;
2. reliability metrics, which show whether the generated artifacts are structurally and semantically stable;
3. validation metrics, which show how far the outputs align with external comparison models or human annotation workflows.

This layered metric design is appropriate for the current stage of the project because the system is both an extraction engine and a benchmark-construction platform.

## 4.3. Experimental Results

The current implementation already produces a substantial experimental evidence base, even though the full expert-labeled benchmark is not yet complete. The results presented in this section should therefore be read as implementation-grounded experimental findings rather than as the final settled performance of a mature supervised benchmark. They demonstrate what the pipeline currently achieves, where it is stable, where it is weak, and what kinds of claims are justified at the present state of the repository.

At the highest level, the experimental environment currently contains:

- 23 OCR-processed documents,
- 332 structured ESG tone records,
- 2,074 T2 rows,
- six currently visible source/company targets in the thesis-facing dashboard outputs,
- multiple prompt-stability and model-stability summaries,
- and a growing set of validation, ontology, and dashboard artifacts.

These outputs already support several meaningful conclusions. First, the pipeline can transform source PDF disclosures into structured, auditable ESG records at non-trivial scale. Second, the generated records are rich enough to support downstream analyses such as tone distribution, ESG-pillar distribution, ClimateBERT-style comparison, and greenwashing-oriented heuristics. Third, the system is sufficiently instrumented to reveal instability and failure modes rather than hiding them.

The dashboard output catalog provides especially useful evidence for this experimental state. The saved overview images already summarize the current results environment in terms of:

- total structured record count,
- source-document count,
- prompt coverage,
- current validation gaps,
- sample-size interpretation,
- and benchmark positioning.

This means the implementation has reached the point where the experiments chapter can report both data outputs and the system’s readiness boundaries.

The experimental results can be grouped into four main themes:

- implementation yield and pipeline productivity,
- tone and ClimateBERT comparison behavior,
- benchmark and ground-truth readiness,
- and prompt/model sensitivity.

### 4.3.1. Comparison with State-Of-The-Art

The current system should be compared with state-of-the-art work carefully because its strengths and weaknesses differ from conventional benchmark papers. The repository’s benchmark-positioning materials, especially the research-questions dashboard outputs and the sample-size reasoning notes, suggest that the system is already comparable to existing work in terms of pipeline scope and artifact richness, but not yet directly comparable in terms of fully supervised metric reporting at the scale of established benchmark datasets.

Compared with traditional ABSA studies, the present system offers a broader end-to-end workflow. Conventional ABSA baselines often assume pre-cleaned text and pre-labeled training data. By contrast, this thesis begins from raw PDF disclosure documents, passes through OCR, LLM extraction, proxy validation, ontology alignment, and dashboard synthesis, and preserves intermediate artifacts. In this sense, the implementation advances beyond narrow sentence-classification pipelines by treating record construction and provenance preservation as part of the experimental contribution.

Compared with climate-domain transformer work such as ClimateBERT-style studies, the current system also differs in target definition. ClimateBERT and similar models are optimized for climate-related or net-zero-oriented semantic detection. The current ESG ABSA framework, however, is broader: it includes environmental, governance, and sparse social disclosures, and it distinguishes tone categories such as commitment, action, and outcome rather than focusing exclusively on topical climate detection. The state-of-the-art comparison is therefore not a pure like-for-like accuracy comparison. It is a construct-level comparison between a climate-focused external signal and a broader ESG disclosure taxonomy.

The current implementation already yields meaningful proxy alignment with ClimateBERT-style labels. The existing dashboard summary reports:

- ClimateBERT proxy agreement of `0.837`,
- Cohen’s kappa of `0.645`.

These values suggest moderate-to-strong semantic alignment without conceptual identity. This is a useful result in state-of-the-art terms because it indicates that the thesis taxonomy is capturing climate-relevant meaning while also preserving distinctions that a climate-specific classifier alone would not model.

At the same time, the system does not yet meet the strongest comparability standards of established supervised benchmarks. The repository’s benchmark screenshots and reasoning notes make this explicit: the current project supports descriptive and feasibility-level claims, but full precision/recall/F1 comparison against large labeled datasets requires more expert annotation. Therefore, the present system is best positioned as:

- stronger than simple descriptive ESG dashboards because it provides record-level structured extraction and auditability;
- broader than ClimateBERT-only approaches because it includes governance, ontology mapping, and tone-aware outputs;
- more explainable than pure black-box LLM extraction because it preserves prompt, run, and audit artifacts;
- but not yet a full state-of-the-art supervised benchmark competitor in the narrow sense of large-scale label-validated F1 comparison.

The dashboard benchmark visualizations explicitly frame this boundary. They place the thesis alongside FinBERT-, ESG-BERT-, ClimateBERT-, and cross-lingual ABSA-style references, while acknowledging that the current contribution is strongest as a reproducible prototype and benchmark-construction framework. This is an honest and methodologically appropriate comparison.

In practical terms, the current system adds three state-of-the-art-relevant capabilities that many narrower baselines lack:

1. document-to-record provenance from PDF to extracted evidence;
2. explicit tone modeling beyond generic sentiment;
3. integrated diagnostic dashboards for prompt stability, schema drift, and validation readiness.

These contributions are meaningful even before the benchmark is fully mature because they expand what can be experimentally studied in ESG disclosure analysis.

### 4.3.2. Ground Truth Generation

Ground-truth generation is one of the most important experimental outputs of the current system because it transforms the project from a pure extraction prototype into an evaluation-capable environment. The repository documentation makes clear that the system already contains the necessary components for benchmark generation, even though full human labeling is still incomplete.

The current ground-truth workflow relies on three progressively stronger label layers:

1. raw model output labels such as `tone_pred`,
2. silver-label scaffolding in files such as `silver_tone_ground_truth.csv`,
3. human-editable and eventually human-validated fields such as `ground_truth_tone`, `ground_truth_esg`, and `ground_truth_aspect`.

This staged structure is experimentally valuable because it allows validation work to begin before the final benchmark is complete. The `1_8_Ground_Truth_Output_Visualizer` page shows how the current system already supports:

- predicted-tone distribution inspection,
- silver-versus-human comparison,
- annotation coverage tracking,
- disagreement review,
- review queues,
- and exportable audit subsets.

In experimental terms, this means the project already generates not just predictions but evaluable benchmark candidates.

The current implementation also reveals that benchmark readiness is uneven. Some records can already be compared against silver labels, while others still await human review or schema repair. This is not a weakness of the chapter; it is one of its findings. The system is successfully surfacing which parts of the extracted corpus are ready for formal evaluation and which parts remain provisional.

The coverage views described in the documentation are particularly important. They show annotation coverage across:

- company or source,
- prompt,
- model,
- language,
- ESG pillar,
- and predicted tone.

This means ground-truth generation is not treated as a flat label-filling exercise. It is treated as a stratified experimental design problem. A strong evaluation set should not overrepresent one prompt, one language, or one tone class. The current tooling therefore makes it possible to prioritize annotation work where it matters most.

The agreement workflow is also already partially operational. According to the ground-truth visualizer design, the system can compare predicted tones against either:

- human tone labels when present,
- or silver labels when human labels are absent and the proxy option is enabled.

This staged logic is experimentally appropriate. It preserves continuity between early-phase review and later formal evaluation. However, the chapter must emphasize that final thesis claims should rely on human-labeled rows rather than silver labels alone.

The ground-truth generation results also expose key limitations in the current corpus. The project notes and revision documentation identify:

- missing tone rows,
- schema drift rows,
- disagreement rows,
- and incomplete human coverage.

These are not merely defects. They are part of the benchmark-generation evidence because they show the real work required to transform extracted outputs into a defensible evaluation corpus.

In summary, the current implementation demonstrates that:

- the system can generate benchmark candidates at record level,
- the benchmark workflow is already integrated with filtering, coverage, and audit views,
- silver-label scaffolding supports early-phase evaluation,
- human-label infrastructure is present but not yet complete,
- and the resulting ground-truth layer is already useful for identifying where the extraction pipeline is strong or fragile.

This is a meaningful experimental result because it shows that the thesis system is not only producing outputs; it is producing the conditions for its own future formal evaluation.

### 4.3.3. Ablation Studies

In the current project state, ablation is best understood as controlled comparison across prompts, models, and validation layers rather than as a classical neural-architecture ablation. The system does not yet present a fully trained supervised model with removable internal components. Instead, the ablation logic arises from the fact that the extraction pipeline can be varied systematically by:

- prompt family,
- model family,
- validation source,
- and output filtering logic.

This is still a valid ablation strategy because the thesis aims to understand which pipeline choices materially affect the quality and structure of the resulting ESG records.

The clearest current ablation dimension is prompt strategy. The revision analytics documentation explicitly states that the system computes prompt-level metrics such as:

- JSON parse success,
- average records per run,
- missing tone rate,
- schema drift rate,
- and field completion rate.

This effectively creates an ablation study over prompt design. The project’s thesis-planning notes identify seven prompt templates spanning variants such as:

- `data.md`,
- `tone_zero_shot_indonesian`,
- `tone_zero_shot_english`,
- `tone_few_shot_english`,
- `tone_few_shot_indonesian`,
- `tone_chain_of_thought_english`,
- `tone_chain_of_thought_indonesian`.

These prompt families operationalize different extraction assumptions. Comparing them is equivalent to ablating the role of in-context examples, language choice, and reasoning scaffolds. If one prompt family yields higher parse success but also higher missing-tone rates, that is an important experimental result about tradeoffs in structured generation.

The second ablation dimension is model choice. The thesis planning notes describe a comparison between at least two model contexts, including `arcee-ai/trinity-large-preview` and `openai/gpt-oss-120b`, with the current data showing a strong imbalance between them. This means the current cross-model ablation is informative but confounded. The experimental conclusion is not that one model is definitively better; rather, the conclusion is that the system has already exposed the need for matched document-prompt reruns before a fair model comparison can be claimed.

This is still a useful ablation result. It reveals that:

- model comparison is possible in the system design,
- current evidence is insufficient for a clean causal claim,
- and future experiments must hold document and prompt conditions constant.

The third ablation dimension concerns validation source. The current implementation allows comparison between:

- raw extracted outputs,
- ClimateBERT-style proxy alignment,
- silver-label agreement,
- and human-label agreement where available.

This creates a de facto validation ablation. It shows how the perceived quality of the system changes depending on whether one evaluates it through proxy climate alignment, provisional silver labels, or stricter human annotation. This is experimentally useful because it prevents the false impression that any one validation source tells the whole story.

The fourth ablation dimension concerns pipeline visibility itself. Because the repository preserves run-quality tables, empty outputs, failure categories, and raw-output signals, the project can compare:

- results using only parsed records,
- versus results using all run outcomes including failed and empty runs.

This is an important experimental ablation because it reveals how much of the apparent success of a system depends on excluding difficult cases. A methodology that only reports successful parsed rows would overestimate reliability.

The current ablation evidence therefore supports several conclusions.

First, prompt design materially influences extraction structure and output quality. This validates the thesis decision to treat prompts as experimental variables.

Second, model comparison remains methodologically promising but currently undercontrolled. The current data reveal the confound clearly, which is itself a useful experimental finding.

Third, evaluation conclusions are sensitive to the validation layer used. Proxy agreement, silver-label agreement, and human-label agreement should not be conflated.

Fourth, the system’s auditability allows ablation not only over outputs, but over what counts as an output in the first place. This is a major advantage over many simpler pipelines.

Overall, the ablation studies in the present chapter should be interpreted as pipeline-component ablations rather than architecture-neuron ablations. They are fully appropriate for an LLM-mediated, artifact-centered ESG extraction framework, and they directly support the thesis goal of identifying robust, reproducible, and auditable extraction practices.
