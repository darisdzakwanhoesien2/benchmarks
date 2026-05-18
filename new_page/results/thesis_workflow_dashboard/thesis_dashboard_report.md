# Thesis Systematic Workflow Dashboard Report

- Results root: `/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks/new_page/results`
- Saved output root: `/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/esg_project/benchmarks/new_page/results/thesis_workflow_dashboard`
- Tone records: 332
- T2 rows: 2,074
- Pilot labels: 70
- Result artifacts: 40

## Saved Graph Attachments

- `tone_distribution.png`: `results/thesis_workflow_dashboard/tone_distribution.png`
- `esg_by_tone.png`: `results/thesis_workflow_dashboard/esg_by_tone.png`
- `aspect_by_tone_heatmap.png`: `results/thesis_workflow_dashboard/aspect_by_tone_heatmap.png`
- `climatebert_label_by_tone.png`: `results/thesis_workflow_dashboard/climatebert_label_by_tone.png`
- `climatebert_remote_top_scores.png`: `results/thesis_workflow_dashboard/climatebert_remote_top_scores.png`

## RQ1 PDF-to-structured ESG evidence

**RQ1 results.** 23/23 OCR documents are marked done, covering about 5,512 pages. The artifact inventory and background job tables show whether PDF-to-record processing is reproducible outside the visible browser session.

**RQ1 graph.** OCR processing status and largest documents by page count

**RQ1 interpretation analysis.** This supports the ingestion layer of the thesis: sustainability reports can be converted into auditable intermediate artifacts before ABSA or ClimateBERT comparison begins.

**RQ1 baseline needed.** Needed baseline: document-level OCR completeness from a trusted extractor such as PyMuPDF/pdfplumber, page-count parity against the original PDFs, and a small manually checked sample of page text quality.

**RQ1 discussion.** The current evidence is operational rather than semantic. It proves that the pipeline can process large reports, but the thesis should still report OCR error categories such as scanned pages, table loss, missing Indonesian characters, and duplicated headers.

**RQ1 conclusion.** RQ1 is implementation-ready; the next validation gap is a page/text quality baseline, not another dashboard.

## RQ2 Aspect, ESG pillar, sentiment, and tone schema

**RQ2 results.** The flat tone table contains 332 extracted records. The most common tone is commitment (115); the most common ESG pillar is e (179). T2 contains 2,074 parsed hybrid prediction rows.

**RQ2 graph.** Tone distribution, ESG pillar distribution, tone x ESG heatmap, and T2 hybrid outputs

**RQ2 interpretation analysis.** The generated schema separates topic, ESG pillar, sentiment polarity, and disclosure tone, which is useful because ESG text can be positive in sentiment while still being only a promise or commitment.

**RQ2 baseline needed.** Needed baseline: a human-coded annotation set for aspect, ESG pillar, sentiment, and tone; inter-annotator agreement; and a simple keyword/rule baseline for commitment/action/outcome labels.

**RQ2 discussion.** The current schema is broad enough for thesis experiments, but the human label loop should decide where 'commitment' ends and 'action' begins, especially for Indonesian modal verbs and sustainability boilerplate.

**RQ2 conclusion.** RQ2 has usable model outputs and a pilot seed, but formal claims need human validation and agreement statistics.

## RQ3 Tone vs ClimateBERT/proxy labels

**RQ3 results.** The agreement table covers 332 records. Tone commitment vs climate-commitment proxy agreement is 83.7%, with Cohen kappa 0.645. Tone commitment rate is 34.6%; climate commitment label rate is 36.4%.

**RQ3 graph.** Tone x ClimateBERT/proxy label crosstab and ClimateBERT agreement metrics

**RQ3 interpretation analysis.** The relatively high agreement suggests that disclosure tone and climate label signals overlap, but they are not identical constructs. That distinction is valuable for the thesis because ClimateBERT-style labels identify climate content while tone labels describe claim maturity.

**RQ3 baseline needed.** Needed baseline: the original ClimateBERT classifier outputs on the same records, a majority-class baseline, a keyword climate-commitment baseline, and a confusion matrix against manually reviewed climate/tone labels.

**RQ3 discussion.** The key thesis discussion is construct validity. A climate-commitment label can coexist with commitment tone, action tone, or outcome tone; disagreement cases should be inspected as evidence of why ABSA tone adds value beyond climate-topic classification.

**RQ3 conclusion.** RQ3 already has publishable-shaped evidence, but it needs an explicit baseline table and disagreement examples before being treated as final experimental evidence.

## RQ4 Diagnostics and extraction weaknesses

**RQ4 results.** The failure-mode table contains 10 mode-tone rows. Ontology coverage tracks 52 aspects, with 6 mapped to ontology paths.

**RQ4 graph.** Failure-mode counts and ontology coverage by aspect

**RQ4 interpretation analysis.** Diagnostics expose where the pipeline is weak: bilingual/code-switched text, hedged claims, missing tone fields, ontology gaps, and schema drift.

**RQ4 baseline needed.** Needed baseline: an error taxonomy coded on a fixed sample, expected failure rates for a rule-only extractor, and an ontology gold map for the most frequent ESG aspects.

**RQ4 discussion.** This section should turn model failure into thesis contribution: every recurring failure mode can become either a schema refinement, a prompt revision, or a human-review rule.

**RQ4 conclusion.** RQ4 is strong as an audit chapter if the dashboard examples are paired with manually inspected representative errors.

## RQ5 Reproducibility, documentation, and visualization

**RQ5 results.** The dashboard currently indexes 40 result artifacts, 1 LLM background jobs, and 0 ground-truth background jobs.

**RQ5 graph.** Artifact inventory, background job status, and exported dashboard report files

**RQ5 interpretation analysis.** The workflow is no longer only an interactive Streamlit view; it now has saved report artifacts that can be attached to the thesis workflow page and regenerated as results change.

**RQ5 baseline needed.** Needed baseline: a manifest of expected output files for each pipeline stage, checksums or timestamps, and a reproduce-from-clean-run checklist.

**RQ5 discussion.** Reproducibility depends on stable file paths, cached API/model metadata, and background execution logs. The report should distinguish generated evidence from manually edited thesis interpretation.

**RQ5 conclusion.** RQ5 is supported by the saved dashboard output and workflow integration; the remaining work is formal run provenance.

## RQ6 Cross-model and cross-prompt stability

**RQ6 results.** Model stability covers 2 models and prompt stability covers 7 prompts. The currently strongest parse-success model is arcee-ai/trinity-large-preview:free; the highest missing-tone prompt is data.md.

**RQ6 graph.** Model parse success, schema drift, prompt field completion, and missing-tone rate

**RQ6 interpretation analysis.** The stability results show that output validity is not only a model-quality problem; prompt format and field requirements strongly affect whether the pipeline produces thesis-usable records.

**RQ6 baseline needed.** Needed baseline: deterministic rule extraction, repeated runs with fixed seeds/temperature, a smaller local model baseline, and per-field agreement rates across prompts.

**RQ6 discussion.** The thesis can frame stability as an engineering and research validity condition. A high-performing model is not enough if it drifts schema or omits tone under a different prompt.

**RQ6 conclusion.** RQ6 has the clearest dashboard evidence for model/prompt comparison; it should be extended with repeated-run confidence intervals and field-level agreement.
