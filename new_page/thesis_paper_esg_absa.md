# Toward an Executable ESG Aspect-Based Sentiment Analysis Framework for Indonesian Sustainability Reports

**A thesis-style research paper draft based on the current ESG Streamlit evidence pipeline**

Author: Daris Dzakwan Hoesien  
Program: ESG / Sustainable Finance / Applied AI Research  
Draft version: 0.1  
Date: 2026-05-22  

## Abstract

Sustainability reports contain dense qualitative and quantitative disclosures about environmental, social, and governance (ESG) activities, yet much of this information remains difficult to compare across firms, years, languages, and disclosure styles. This thesis proposes an executable ESG Aspect-Based Sentiment Analysis (ABSA) framework for transforming Indonesian sustainability reports into structured evidence records. The framework combines OCR processing, large language model (LLM) extraction, ESG aspect classification, tone labeling, ClimateBERT-based comparison, ontology mapping, and interactive Streamlit dashboards. Unlike document-level ESG scoring, the proposed approach operates at the record level, preserving source provenance, prompt/model metadata, ESG pillar labels, aspect labels, tone labels, and validation outputs.

The current implementation processes sustainability-report text into a 332-record structured ESG evidence table, supported by 2,074 T2 rows, 23 OCR documents, 40 tracked artifacts, model-stability outputs, prompt-stability outputs, ontology coverage summaries, and ClimateBERT agreement metrics. Initial validation shows 83.7% ClimateBERT proxy agreement and Cohen's kappa of 0.645, indicating moderate alignment between ESG tone labels and climate-focused labels while also confirming that ESG tone and climate commitment are not identical constructs. The thesis contributes an executable research pipeline, a bilingual ESG ABSA schema, a reproducible artifact lineage, and an ontology-oriented path for extending Indonesian ESG vocabulary into RDF, OWL, and Neo4j graph formats.

Keywords: ESG, sustainability reports, aspect-based sentiment analysis, ABSA, ClimateBERT, ontology, knowledge graph, Indonesian ESG, LLM extraction, Streamlit dashboard

## Table Of Contents

1. Introduction  
2. Related Work  
3. Methodology  
4. Experimental Setup And Results  
5. Discussion  
6. Conclusion  
7. References  
8. Appendix: Executable Artifacts And Streamlit Pages  

---

# 1. Introduction

## 1.1 Motivation

ESG disclosure is increasingly used by investors, regulators, researchers, and companies to evaluate sustainability performance. However, sustainability reports are long, heterogeneous, and often written in a mixture of formal reporting language, promotional narrative, tables, operational claims, and forward-looking commitments. For Indonesian-listed companies, this problem is amplified by bilingual disclosure patterns, local ESG vocabulary, company-specific terminology, and uneven report formatting.

Traditional document-level ESG analysis is insufficient for this setting because a single report may contain multiple ESG aspects with different tones. One paragraph may describe an environmental commitment, another may report a completed social program, and another may mention governance compliance without measurable outcomes. Therefore, this thesis treats ESG disclosure as a record-level ABSA problem: each extracted statement is classified by aspect, ESG pillar, sentiment, tone, and provenance.

The motivation follows the structure of the reference thesis on behaviour-aware multimodal summarization: raw data must be converted into aligned, inspectable, and evaluable computational artifacts. In the ESG setting, the raw input is a sustainability-report corpus rather than video, and the aligned signals are OCR text, extracted ESG records, LLM metadata, ClimateBERT labels, human annotations, ontology mappings, and dashboard visualizations.

## 1.2 Problem Statement

The central problem is how to design a reproducible ESG ABSA pipeline that transforms sustainability-report PDFs into structured, validated, and thesis-ready evidence records.

This requires solving six linked challenges:

1. Converting heterogeneous PDF reports into usable text while preserving document/page provenance.
2. Extracting ESG statements from report text using configurable LLM prompts and providers.
3. Assigning aspect, ESG pillar, sentiment, and tone labels to extracted records.
4. Comparing ESG tone labels with climate-specific model outputs such as ClimateBERT.
5. Auditing failures, schema drift, missing fields, and OCR-related loss.
6. Connecting every artifact to research questions, chapter claims, and reproducible dashboards.

## 1.3 Research Questions

**RQ1. PDF-to-structured ESG transformation**  
How can sustainability-report PDFs be transformed into structured ESG evidence records while preserving provenance?

**RQ2. ESG ABSA schema**  
How can ESG disclosures be represented using aspect, ESG pillar, sentiment, and tone labels at the record level?

**RQ3. Tone versus ClimateBERT**  
How do ESG tone labels compare with ClimateBERT-style climate labels, and what does this reveal about construct validity?

**RQ4. Diagnostics and ontology gaps**  
What failure modes, schema-drift patterns, OCR issues, and unmapped aspects appear in the extraction pipeline?

**RQ5. Reproducibility and artifact lineage**  
How can LLM-based ESG extraction be made reproducible through job configs, logs, output files, dashboards, and graph exports?

**RQ6. Model and prompt stability**  
How stable are the ESG extraction outputs across prompts, models, and providers?

## 1.4 Objectives And Contributions

The thesis has six objectives:

1. Build a reproducible OCR-to-ESG extraction pipeline.
2. Design a record-level ESG ABSA schema for sustainability disclosures.
3. Compare tone labels with ClimateBERT-style climate labels.
4. Create diagnostics for parsing failures, schema drift, OCR loss, and missing labels.
5. Map aspects to ESG ontology paths and identify Indonesian ESG vocabulary extensions.
6. Provide Streamlit dashboards and semantic exports for thesis evidence, RDF, OWL, and Neo4j.

The expected contributions are:

- An executable ESG ABSA pipeline for sustainability reports.
- A bilingual and record-level ESG annotation schema.
- A thesis evidence layer linking raw reports, LLM outputs, validation tables, graphs, and chapter claims.
- A reproducibility workflow for LLM prompt/model comparison.
- A semantic graph export path for ESG evidence and ontology extension.
- A discussion of why ESG disclosure tone and climate commitment labels are related but not interchangeable.

## 1.5 Thesis Structure

Chapter 1 introduces the motivation, problem statement, research questions, objectives, and contributions. Chapter 2 reviews ABSA, ESG NLP, ClimateBERT, LLM extraction, agreement metrics, and ontology-based ESG representation. Chapter 3 explains the methodology, including OCR, LLM extraction, ABSA labeling, ClimateBERT comparison, ontology mapping, and dashboard integration. Chapter 4 presents implementation results and live artifact summaries. Chapter 5 discusses interpretation, limitations, construct validity, and Indonesian ESG vocabulary extension. Chapter 6 concludes the thesis and proposes future research directions.

## 1.6 Author Contribution And Use Of AI

The system uses LLMs as computational tools for extraction, prompting, summarization, code assistance, and dashboard generation. The author remains responsible for research design, annotation decisions, validation interpretation, thesis claims, and final academic judgment. AI-generated outputs are treated as artifacts that require inspection, source verification, and human review.

---

# 2. Related Work

## 2.1 Aspect-Based Sentiment Analysis

Aspect-Based Sentiment Analysis (ABSA) is a fine-grained sentiment analysis task that moves beyond document-level or sentence-level polarity by identifying the specific aspect or target being discussed and the sentiment expressed toward it. Survey work describes ABSA as a family of tasks involving aspect extraction, aspect category detection, opinion extraction, and sentiment classification (Zhang et al., 2022).

For ESG reporting, ABSA is useful because a single sustainability report can contain multiple aspects with different tones. For example, a report may contain a positive commitment to renewable energy, a neutral governance compliance statement, and a negative risk disclosure about emissions. A document-level score would hide these distinctions.

## 2.2 ESG And Climate-Related NLP

ClimateBERT is a pretrained language model for climate-related text and is frequently used as a domain-specific model for climate disclosure classification and climate-related NLP tasks (Webersinke et al., 2021). In this thesis, ClimateBERT is used not as a replacement for ESG ABSA, but as a baseline and comparison model. This distinction matters because a climate-specific model can detect climate relevance or climate commitment, while the ESG ABSA schema also includes governance, social, generic ESG, and non-climate aspects.

## 2.3 LLM-Based Structured Extraction

LLMs are useful for extracting structured records from long sustainability disclosures, but they introduce risks: schema drift, missing fields, prompt sensitivity, provider differences, and JSON parse failures. Therefore, the pipeline treats every LLM output as an auditable run artifact. Each record should preserve the model, prompt, timestamp, target document, source text, parsed fields, and parse status.

## 2.4 Ground Truth, Pseudo-Ground Truth, And Human Annotation

The reference thesis uses LLM-generated pseudo-ground truth to address dataset scarcity. This ESG thesis adopts a related but more explicitly separated structure:

- LLM outputs are treated as machine-generated extraction artifacts.
- Proxy labels can be derived from existing fields.
- Human annotations are collected separately.
- Silver labels are used as intermediate validation targets.
- Metrics are computed only when the truth and prediction columns are clearly defined.

This separation prevents pseudo-ground truth from being mistaken for final human-labeled truth.

## 2.5 Agreement Metrics

Percent agreement is intuitive but does not adjust for chance agreement. Cohen's kappa is commonly used for nominal labels when comparing two raters or two labeling sources, because it adjusts for expected chance agreement (McHugh, 2012). In this thesis, agreement metrics are used to compare ClimateBERT-style labels, proxy labels, and human/silver labels. However, kappa should be interpreted carefully when label distributions are imbalanced.

## 2.6 Ontologies And Knowledge Graphs

Ontology mapping enables ESG records to become more than flat tables. Aspects can be connected to ESG pillars, GRI/SASB-like paths, local Indonesian vocabulary, company entities, report sources, and evidence statements. This supports semantic querying, RDF/OWL export, Neo4j import, GraphRAG retrieval, and explainable ESG evidence navigation.

## 2.7 Research Gap

Existing ABSA work provides strong methods for aspect and sentiment modeling, while climate-specific language models provide specialized climate-disclosure signals. However, there remains a practical gap in executable ESG thesis systems that combine:

- PDF OCR ingestion.
- LLM-based ESG statement extraction.
- Record-level ABSA labels.
- ClimateBERT comparison.
- Human and silver annotation workflows.
- Ontology mapping.
- Prompt/model stability analysis.
- Graph export.
- Chapter-ready dashboards.

This thesis addresses that gap by designing an integrated, reproducible, and thesis-facing ESG ABSA pipeline.

---

# 3. Methodology

## 3.1 Methodological Overview

The proposed framework follows a staged pipeline:

1. Source PDF collection.
2. OCR conversion and page-level auditing.
3. LLM-based ESG statement extraction.
4. ABSA field normalization.
5. ClimateBERT comparison.
6. Ground-truth annotation and metrics.
7. Ontology mapping and graph export.
8. Dashboard and thesis chapter integration.

The methodology is executable: each stage has Streamlit pages, backing files, figures, and audit tables.

## 3.2 Data Sources

The system uses Indonesian sustainability reports and generated pipeline artifacts. Current tracked evidence includes:

- 23 OCR documents.
- 332 structured ESG tone records.
- 2,074 T2 rows.
- 40 tracked artifacts in the workflow dashboard.
- Prompt-stability and model-stability summary tables.
- Ontology coverage tables.
- ClimateBERT comparison outputs.
- Ground-truth and silver-label annotation tables.

Key files include:

- `results/thesis_workflow_dashboard/tone_records_flat.csv`
- `results/thesis_workflow_dashboard/tone_esg_crosstab.csv`
- `results/thesis_workflow_dashboard/tone_climatebert_label_crosstab.csv`
- `results/thesis_workflow_dashboard/model_stability_summary.csv`
- `results/thesis_workflow_dashboard/prompt_stability_summary.csv`
- `results/thesis_workflow_dashboard/ontology_coverage.csv`
- `results/revision_analysis/silver_tone_ground_truth.csv`
- `results/semantic_exports/esg_thesis_graph.ttl`
- `results/semantic_exports/esg_thesis_ontology.owl`
- `results/semantic_exports/neo4j_nodes.csv`
- `results/semantic_exports/neo4j_relationships.csv`

## 3.3 OCR Processing

PDF sustainability reports are converted into page-level text using the OCR workflow. The OCR stage produces source text that can be sampled, audited, and linked to extracted records. OCR quality is treated as a methodological risk because missing text, table loss, and page segmentation errors can affect every downstream label.

Relevant pages:

- `pages/Bulk_OCR.py`
- `pages/1_2_OCR_Quality_Workbench.py`
- `pages/2_4_PDF_Page_Processing_Audit.py`

## 3.4 LLM ESG Record Extraction

LLM prompts extract ESG statements from OCR text. Each run is associated with a target document, prompt template, provider, model, timestamp, and output record. The pipeline supports repeated runs and background execution so that long extraction tasks can continue even if the Streamlit page is not actively open.

Relevant pages:

- `pages/llm_processing.py`
- `pages/2_3_LLM_Background_Run_Monitor.py`
- `pages/2_0_LLM_Processing_Result_Visualizer.py`
- `pages/2_1_LLM_Error_Parse_Audit.py`

## 3.5 ESG ABSA Schema

Each extracted record is normalized into ABSA fields:

- `text`: source disclosure statement.
- `aspect`: ESG issue or topic.
- `esg`: ESG pillar, including multi-label possibilities such as E-S, E-G, S-G, or E-S-G.
- `tone`: commitment, action, outcome, missing, none, or other.
- `sentiment`: positive, negative, neutral, or related sentiment class.
- `labels`: supporting model labels such as climate-related or governance indicators.
- `reasoning`: explanation attached to the extracted record.
- `target_doc`: source document identifier.
- `prompt`: prompt template used.
- `model`: LLM model used.

The schema is intentionally record-level because ESG tone depends on the specific claim, not only on the document.

## 3.6 ClimateBERT Comparison

ClimateBERT outputs are used as a climate-specific comparison layer. The thesis does not assume that ClimateBERT labels and ESG tone labels should be identical. Instead, disagreement is analytically useful because it shows where a climate-oriented classifier detects climate relevance while the ESG ABSA schema captures disclosure tone.

Current dashboard metrics:

- ClimateBERT proxy agreement: 0.837.
- Cohen's kappa: 0.645.

These values suggest meaningful agreement, but also enough divergence to justify a construct-validity discussion.

Relevant pages:

- `pages/1_4_ClimateBERT_Record_Batch.py`
- `pages/0_9_Tone_ClimateBERT_Visualization.py`
- `pages/6_2_Chapter_5_Discussion.py`

## 3.7 Ground-Truth Annotation

Ground-truth annotation is handled separately from automatic extraction. The workbench supports tone, ESG pillar, and aspect labels. The system also supports review queues, unannotated-row filtering, and silver-label comparison.

Relevant pages:

- `pages/ground_truth.py`
- `pages/1_1_Ground_Truth_Workbench.py`
- `pages/1_3_Ground_Truth_Metrics.py`
- `pages/1_8_Ground_Truth_Output_Visualizer.py`
- `pages/1_12_Ground_Truth_Step_By_Step_Visualizer.py`

## 3.8 Ontology Mapping And Semantic Graph Export

Aspect labels are mapped to ontology paths when possible. Unmapped aspects are not treated only as errors; they are also candidates for Indonesian ESG vocabulary extension. Semantic exports convert records into RDF, OWL, and Neo4j graph formats.

Relevant pages:

- `pages/1_6_Ontology_Path_Viewer.py`
- `pages/1_13_Semantic_Graph_Exporter.py`

## 3.9 Dashboard And Chapter Integration

The Streamlit app is part of the research method. It allows the thesis to remain synchronized with live results. Chapter pages integrate graphs, backing tables, dashboard counters, and interpretation boxes.

Relevant pages:

- `pages/3_0_Thesis_Action_Plan.py`
- `pages/5_Thesis_Systematic_Workflow_dashboard.py`
- `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`
- `pages/6_1_Chapter_4_Implementation_Results.py`
- `pages/6_2_Chapter_5_Discussion.py`
- `pages/6_3_Chapter_6_Conclusion.py`
- `pages/6_4_ch4-6.py`

---

# 4. Experimental Setup And Results

## 4.1 Implementation Environment

The system is implemented as a Streamlit application with supporting Python scripts, CSV/JSON artifacts, visualizations, and semantic export files. LLM jobs can be run interactively or in the background. Dashboard pages read from the results folders and regenerate thesis-facing figures.

## 4.2 Current Dataset Snapshot

The current dashboard snapshot contains:

| Artifact group | Current value |
|---|---:|
| Research questions tracked | 6 |
| Structured tone records | 332 |
| T2 rows | 2,074 |
| OCR documents | 23 |
| Tracked artifacts | 40 |
| ClimateBERT proxy agreement | 0.837 |
| ClimateBERT Cohen's kappa | 0.645 |

Additional full-pipeline status from the action plan should be reported when regenerated:

| Status item | Thesis meaning |
|---|---|
| ClimateBERT real records | Completeness of local/real ClimateBERT predictions |
| Tone labels | Completeness of tone annotation |
| ESG labels | Completeness of ESG-pillar annotation |
| Aspect labels | Completeness of aspect annotation |
| OCR pages sampled | OCR-quality validation coverage |
| Models tested | LLM model-comparison coverage |

## 4.3 RQ1 Results: PDF-To-Structured ESG Transformation

The pipeline currently demonstrates that PDF sustainability reports can be transformed into structured ESG evidence records. OCR documents are processed into text, LLM prompts extract records, and the resulting evidence table preserves prompt, model, timestamp, target document, and record index.

Primary artifact:

- `results/thesis_workflow_dashboard/tone_records_flat.csv`

Main interpretation:

The output supports document-to-record transformation, but page-level OCR sampling remains necessary for stronger claims about OCR quality and extraction completeness.

## 4.4 RQ2 Results: ESG ABSA Schema

The ESG ABSA schema captures aspect, ESG pillar, sentiment, and tone. Current figures include:

- Tone distribution.
- ESG by tone.
- Aspect by tone heatmap.
- Ground-truth tone comparison.
- T2 rule versus hybrid tone outputs.

Important graph attachments:

- `results/docx_graph_attachments/docx_full_tone_distribution.png`
- `results/docx_graph_attachments/docx_full_esg_by_tone.png`
- `results/docx_graph_attachments/docx_full_aspect_by_tone_heatmap.png`
- `results/docx_graph_attachments/docx_ground_truth_tone_comparison.png`

Main interpretation:

ABSA is appropriate because ESG disclosure meaning changes at the aspect level. A single report can contain commitments, actions, outcomes, missing labels, and neutral disclosures across different ESG aspects.

## 4.5 RQ3 Results: Tone Versus ClimateBERT

The current ClimateBERT comparison shows:

- Percent agreement: 83.7%.
- Cohen's kappa: 0.645.

This indicates substantial but incomplete alignment. ClimateBERT is useful as a climate-focused baseline, but it does not replace ESG ABSA because ESG tone includes broader disclosure categories and non-climate aspects.

Important graph attachments:

- `results/docx_graph_attachments/docx_climatebert_baseline.png`
- `results/thesis_workflow_dashboard/climatebert_label_by_tone.png`
- `results/thesis_workflow_dashboard/climatebert_remote_top_scores.png`

Main interpretation:

The disagreement between tone and ClimateBERT labels is not only an error signal. It is also evidence that ESG tone and climate commitment are related but distinct constructs.

## 4.6 RQ4 Results: Diagnostics And Ontology Gaps

The system tracks diagnostic categories such as:

- Missing tone labels.
- Schema drift.
- JSON parse failures.
- OCR text loss.
- Bilingual code-switching.
- Ontology unmapped aspects.

Important artifacts:

- `results/thesis_workflow_dashboard/failure_mode_counts.csv`
- `results/thesis_workflow_dashboard/ontology_coverage.csv`
- `results/docx_graph_attachments/docx_ontology_mapped_vs_unmapped.png`
- `results/docx_graph_attachments/docx_ontology_extension_candidates.png`

Main interpretation:

Diagnostics transform pipeline weaknesses into research evidence. Unmapped aspects can reveal local ESG vocabulary that is not fully covered by imported ontology paths.

## 4.7 RQ5 Results: Reproducibility And Artifact Lineage

The pipeline supports reproducibility through:

- Background job folders.
- Config files.
- Status files.
- Event logs.
- Prompt names.
- Model names.
- Timestamped records.
- Graph attachments.
- Backing tables.
- Streamlit chapter pages.

Important pages:

- `pages/2_3_LLM_Background_Run_Monitor.py`
- `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py`
- `pages/6_4_ch4-6.py`

Main interpretation:

Reproducibility is operationalized through artifact lineage. A thesis claim should point to a graph, a backing table, a source artifact, and a Streamlit page.

## 4.8 RQ6 Results: Model And Prompt Stability

Current model-stability summary includes two visible model configurations:

| Model | Runs | JSON parse success | Average records | Missing-tone rate |
|---|---:|---:|---:|---:|
| `arcee-ai/trinity-large-preview:free` | 90 | 1.000 | 3.022 | 0.000463 |
| `openai/gpt-oss-120b:free` | 20 | 1.000 | 3.000 | 1.000000 |

Current prompt-stability output contains seven prompt templates. The summary shows that prompt design strongly affects missing-tone rate and field completion rate.

Important artifacts:

- `results/thesis_workflow_dashboard/model_stability_summary.csv`
- `results/thesis_workflow_dashboard/prompt_stability_summary.csv`
- `results/docx_graph_attachments/docx_model_parse_success.png`
- `results/docx_graph_attachments/docx_prompt_missing_tone_rate.png`

Main interpretation:

Model and prompt stability must be reported because LLM extraction quality is not fixed. A prompt may parse successfully while still producing incomplete fields.

## 4.9 Benchmarking Plan

The thesis should benchmark against four categories:

1. **ClimateBERT baseline**: compare ESG tone labels with climate-specific predictions.
2. **Human annotation agreement**: compare model or silver labels against manually reviewed annotations.
3. **Repeated LLM runs**: measure stability across repeated prompts, models, and providers.
4. **Ontology extension**: compare mapped versus unmapped aspects and justify local vocabulary additions.

Benchmark artifacts:

- `human_agreement_summary.csv`
- `model_prompt_repeated_run_ci.csv`
- `climatebert_baseline_comparison.csv`
- `indonesian_esg_ontology_extension.csv`

---

# 5. Discussion

## 5.1 ESG Tone Is Not The Same As Climate Commitment

The ClimateBERT agreement results show useful alignment, but the constructs differ. ESG tone describes how a disclosure is framed: commitment, action, outcome, missing, none, or other. ClimateBERT-style labels identify climate relevance or climate-related categories. A governance action, social outcome, or general ESG commitment may be important in the ABSA schema but not central to a climate-specific model.

## 5.2 Commitment Dominance And Reporting Style

Sustainability reports often emphasize commitments and aspirational language. This can inflate commitment-like labels relative to measurable outcome labels. Therefore, the thesis should distinguish between what a company promises, what it does, and what it reports as achieved.

## 5.3 Schema Drift As A Diagnostic Signal

Schema drift occurs when LLM outputs do not match the expected fields or label structure. This is a technical problem, but it is also an empirical signal about prompt reliability. If one prompt produces complete ABSA fields and another produces missing tone labels, the difference should be included in the stability analysis.

## 5.4 Indonesian ESG Vocabulary Extension

Unmapped aspects should not be dismissed as noise. Some may represent local ESG concepts, regulatory language, or Indonesian reporting conventions that are underrepresented in global ontologies. This supports a thesis contribution: extending ESG ABSA ontology coverage for Indonesian sustainability reports.

## 5.5 Reliability And Validity

Reliability is addressed through repeated runs, parse-success rates, missing-field rates, annotation coverage, and agreement metrics. Validity is addressed by comparing labels against ClimateBERT, human annotations, ontology mappings, and source-page verification.

## 5.6 Limitations

Current limitations include:

- OCR quality sampling is not yet complete.
- Some figures may use smaller structured tables while action-plan counters show larger annotation-status totals.
- LLM outputs can be sensitive to prompt wording and model provider.
- Human annotation may require more than one annotator for stronger reliability claims.
- ClimateBERT is climate-specific and should not be treated as a full ESG baseline.
- Ontology mapping may underrepresent local Indonesian ESG vocabulary.

## 5.7 Implications

The framework demonstrates that ESG reporting analysis can become an executable research system. Instead of separating code, charts, annotation, and writing, the thesis links all of them through Streamlit pages, backing tables, and graph attachments. This makes the research easier to audit, reproduce, revise, and defend.

---

# 6. Conclusion

This thesis proposes an executable ESG ABSA framework for transforming Indonesian sustainability reports into structured, validated, and graph-ready evidence. The system combines OCR, LLM extraction, ABSA labeling, ClimateBERT comparison, human annotation, ontology mapping, and Streamlit-based thesis integration.

The main conclusion is that ESG disclosure analysis benefits from record-level modeling. Document-level ESG scoring is too coarse to capture differences between commitments, actions, outcomes, missing disclosures, and governance or social statements. The current pipeline shows that extracted records can be validated, visualized, mapped to research questions, and exported into semantic graph formats.

Future work should focus on:

1. Completing OCR quality sampling.
2. Expanding human annotation and inter-annotator agreement.
3. Running repeated LLM benchmarks across more providers.
4. Strengthening ClimateBERT comparison with real local model outputs.
5. Extending the ontology with Indonesian ESG vocabulary.
6. Developing Neo4j and GraphRAG interfaces for evidence-grounded ESG question answering.
7. Adding temporal and company-level ESG trend analysis.

The broader contribution is methodological: the thesis is not only a written argument but also an executable evidence environment.

---

# 7. References

McHugh, M. L. (2012). Interrater reliability: The kappa statistic. *Biochemia Medica*, 22(3), 276-282. https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/

Webersinke, N., Kraus, M., Bingler, J. A., & Leippold, M. (2021). ClimateBERT: A pretrained language model for climate-related text. *arXiv*. https://arxiv.org/abs/2110.12010

Zhang, W., Li, X., Deng, Y., Bing, L., & Lam, W. (2022). A survey on aspect-based sentiment analysis: Tasks, methods, and challenges. *arXiv*. https://arxiv.org/abs/2203.01054

Islam, M. M. (2025). *Towards Behaviour-Aware Multimodal Video Summarization: Integrating Visual, Audio, and Textual Cues for Human-Centric Content Analysis* [Master's thesis, University of Oulu]. Local reference file: `research_references/nbnfioulu-202506124422.pdf`

---

# 8. Appendix: Executable Artifacts And Streamlit Pages

## A. Core Streamlit Pages

| Page | Thesis role |
|---|---|
| `pages/3_0_Thesis_Action_Plan.py` | Live task execution, status counters, migration, annotation, prompt matrix |
| `pages/6_4_ch4-6.py` | Graph attachments, backing tables, chapter mapping, benchmark checklist |
| `pages/6_0_Thesis_Draft_Chapter_Integration_Mermaid.py` | Thesis spine, RQ evidence, validation loop, artifact lineage |
| `pages/6_1_Chapter_4_Implementation_Results.py` | Live Chapter 4 implementation and results |
| `pages/6_2_Chapter_5_Discussion.py` | Live Chapter 5 interpretation and limitations |
| `pages/6_3_Chapter_6_Conclusion.py` | Live Chapter 6 conclusions and future work |
| `pages/1_13_Semantic_Graph_Exporter.py` | RDF, OWL, Neo4j export |

## B. Core Result Tables

| Artifact | Use |
|---|---|
| `results/thesis_workflow_dashboard/tone_records_flat.csv` | Main structured ESG ABSA record table |
| `results/thesis_workflow_dashboard/tone_esg_crosstab.csv` | ESG pillar by tone |
| `results/thesis_workflow_dashboard/tone_climatebert_label_crosstab.csv` | Tone by ClimateBERT-style label |
| `results/thesis_workflow_dashboard/model_stability_summary.csv` | Model-level stability |
| `results/thesis_workflow_dashboard/prompt_stability_summary.csv` | Prompt-level stability |
| `results/thesis_workflow_dashboard/ontology_coverage.csv` | Mapped and unmapped aspects |
| `results/revision_analysis/silver_tone_ground_truth.csv` | Silver-label ground truth scaffold |

## C. Core Graph Attachments

| Attachment | Use |
|---|---|
| `results/docx_graph_attachments/docx_full_tone_distribution.png` | Chapter 4 RQ2 tone distribution |
| `results/docx_graph_attachments/docx_full_esg_by_tone.png` | Chapter 4 RQ2 ESG by tone |
| `results/docx_graph_attachments/docx_full_aspect_by_tone_heatmap.png` | Chapter 4 RQ2 aspect by tone |
| `results/docx_graph_attachments/docx_climatebert_baseline.png` | Chapter 4/5 RQ3 ClimateBERT baseline |
| `results/docx_graph_attachments/docx_model_parse_success.png` | Chapter 6 RQ6 model stability |
| `results/docx_graph_attachments/docx_ontology_mapped_vs_unmapped.png` | Chapter 5/6 ontology coverage |
| `results/docx_graph_attachments/aspect_cooccurrence_edges.png` | Aspect relationship analysis |
| `results/docx_graph_attachments/aspect_network_centrality.png` | Aspect centrality analysis |

## D. Recommended Figure/Table Format

Every graph section should include:

1. Chapter and RQ label.
2. Graph path.
3. Original table path.
4. Redirect/open page button.
5. Original graph attachment.
6. Original/backing table.
7. Interpretation box.
8. Limitation or next-action box.

This format keeps the paper, dashboard, graph, and data table connected.
