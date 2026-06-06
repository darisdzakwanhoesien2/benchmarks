# Chapter 4: Experiments and Results

## 4.1 System Implementation and Experimental Setup

This chapter reports the implementation state and empirical outputs of the ESG ABSA pipeline described in Chapter 3. The experiments are organized as a multi-stage research system rather than a single classifier benchmark. The implementation is built in Python and exposed through a Streamlit multi-page application so that OCR outputs, extraction runs, comparison labels, diagnostics, and thesis-facing figures can be inspected together.

At the system level, the implementation has five linked layers: source document ingestion and OCR, structured ESG extraction, T1 and T2 comparison outputs, review and revision tooling, and visualization or reporting dashboards. This architecture reflects the thesis claim that ESG disclosure analysis requires a full document-to-record workflow rather than only a final classifier.

The repository is organized to support that workflow. `data/` contains source and OCR-derived assets, `pages/` contains interactive Streamlit pages, `code/` contains analytical modules, `prompt/` stores extraction prompts, and `results/` stores persistent outputs and summaries. The central experiment artifact for this chapter is `results/esg_records.json`.

The current extraction state contains 110 successful ESG extraction runs and 332 structured ESG records generated across 7 prompt templates and 2 model backends. The current implementation also reports 23 OCR documents, 2,074 T2 rows, multiple workflow artifacts, static charts, prompt-stability summaries, and model-stability summaries. These outputs show that the pipeline has moved beyond interface scaffolding into a functioning experimental workspace.

The current experimental setup should still be interpreted carefully. It is strong in artifact generation, cross-layer visibility, and exploratory comparison. It is weaker in fully matched, one-to-one supervised benchmarking because the complete expert-labeled ground truth is not yet available.

## 4.2 Evaluation Metrics

The evaluation strategy is layered because the system itself is layered. No single metric can summarize OCR quality, extraction stability, semantic plausibility, and benchmark readiness at once. This chapter therefore uses several complementary metric families.

The first family is productivity and yield. These include the number of OCR-processed documents, the number of structured ESG records, the number of T2 rows, the number of prompt templates represented, and the number of tracked artifacts. These counts define the present scale of the workspace and therefore constrain what kinds of claims are possible.

The second family is structured extraction reliability. Important metrics here include parse success, record count per run, field completion, missing-tone rate, schema drift, and empty-output frequency. These are central because an LLM output is not analytically useful merely because it looks plausible in prose; it must also be structurally reliable enough for downstream analysis.

The third family is semantic comparison and agreement. The main example is the ClimateBERT proxy comparison, summarized through agreement percentages, kappa values, co-occurrence tables, and disagreement inspection. These metrics do not serve as a direct replacement for expert labels, but they do provide construct-level evidence.

The fourth family is human-evaluation readiness. The repository already defines accuracy, precision, recall, F1, kappa, confusion matrices, and disagreement tables for later use once human labels become more complete. At the current stage, this framework is implemented, but only partially populated.

The fifth family is interpretive analytics. This includes ontology coverage and the greenwashing-oriented rhetoric-to-results heuristic:

```text
greenwashing_index = (commitment + 0.5) / (outcome + 0.5)
```

This index is used in the project as a screening signal, not as a validated greenwashing verdict.

## 4.3 Main Experimental Results

At the highest level, the current experiment environment contains 23 OCR-processed documents, 332 structured ESG records, 2,074 T2 rows, 110 successful runs, and a stable set of dashboard artifacts. These outputs already support a meaningful experimental discussion because they show that the system can transform long-form disclosure documents into structured, auditable evidence.

The overall tone distribution is:

- `commitment`: 115
- `missing`: 61
- `action`: 58
- `outcome`: 50
- `none`: 48

The ESG pillar distribution is also uneven:

- `E`: 179
- `G`: 121
- `none`: 27
- `S`: 4
- `missing`: 1

These counts immediately show three things. First, the extraction pipeline yields enough records to support descriptive analysis. Second, commitment-oriented language dominates the current corpus. Third, the social pillar is severely underrepresented, which must be treated as both a substantive and methodological limitation.

### 4.3.1 RQ1 and RQ2: From PDF to Structured ESG Records

RQ1 concerns whether sustainability-report PDFs can be transformed into structured ESG evidence. The current implementation answers this positively at a feasibility level. The OCR layer already processes 23 documents into page-aware text artifacts that can be consumed by downstream extraction. The existence of 332 structured records shows that the document-to-record transformation is operational, not only theoretical.

RQ2 asks whether ESG statements can be represented using a record-level schema including aspect, ESG pillar, sentiment, and tone. The current extraction results also answer this positively, though not perfectly. The system already generates records with these fields and persists them into a reusable JSON store. However, the 61 missing-tone rows show that schema completion remains incomplete.

Prompt distribution across successful runs further confirms that the results do not come from a single hand-tuned prompt. The current run counts include `data.md` with 20 runs, `tone_zero_shot_indonesian` with 16, `tone_chain_of_thought_english` with 16, `tone_chain_of_thought_indonesian` with 15, `tone_few_shot_english` with 15, `tone_zero_shot_english` with 14, and `tone_few_shot_indonesian` with 14. This diversity makes the extraction layer experimentally informative, even when outputs are unstable.

### 4.3.2 RQ3: ClimateBERT Comparison and Proxy Validation

The most important comparative result is the partial alignment between LLM-derived tone labels and ClimateBERT-style labels. The project summary reports 83.7% proxy agreement and Cohen’s kappa of 0.645. These values indicate meaningful overlap, but not identity, between the two labeling schemes.

The most important co-occurrence pattern is `commitment` with `climate-commitment`, which appears 91 times. Additional alignment appears between `commitment` and `climate-d` at 57 cases, and between `commitment` and `environmental-claims` at 48 cases. This matters because it suggests that commitment records are not arbitrary artifacts of prompting. Many of them also register as climate-relevant under an external domain-oriented label family.

At the same time, the comparison layer reveals important disagreement and ambiguity. The project notes show missing-tone co-occurrence with `climate-commitment` 22 times and with `environmental-claims` 21 times. These cases likely represent false negatives, schema failures, or taxonomy-fit problems rather than simple absence of meaning.

### 4.3.3 RQ4: Diagnostics and Extraction Weaknesses

RQ4 concerns whether the pipeline can reveal its own weaknesses. The current answer is clearly yes. The most visible weakness is the 61 missing-tone records, which amount to a substantial proportion of the extracted corpus. In addition, the sentiment field contains schema drift, including 18 records where `commitment` appears in the sentiment position. This shows that extraction quality must be judged structurally as well as semantically.

Another important diagnostic result is the underrepresentation of social disclosures, with only four `S` records. This may reflect corpus selection, prompt behavior, ontology gaps, or a real imbalance in the sampled disclosure environment. At the present stage, the thesis cannot isolate these causes confidently, but it can surface them as a priority for refinement.

Governance-oriented text also appears to be more difficult for the current tone taxonomy. The current discussion artifacts repeatedly note that governance disclosures are spread across action, commitment, outcome, none, and missing categories. This pattern suggests that procedural or compliance-oriented language does not map cleanly onto an environmental-performance-style tone schema.

### 4.3.4 RQ5 and RQ6: Documentation, Visualization, and Stability

RQ5 asks whether documentation and visualization materially improve auditability. The answer is yes. The implementation already produces a stable set of thesis-ready visual artifacts, including `tone_distribution.png`, `esg_by_tone.png`, `climatebert_label_by_tone.png`, `aspect_by_tone_heatmap.png`, and `climatebert_remote_top_scores.png`. These figures make it possible to discuss extraction outcomes even when the live dashboard evolves.

The interactive dashboard also supports filtering by tone, ESG pillar, prompt, and source document. This matters because the thesis contribution is not only predictive output; it is also the ability to inspect why outputs look the way they do.

RQ6 concerns prompt and model stability. The current project summary indicates that model stability covers multiple models and prompt stability covers seven prompt templates. At the present stage, the strongest practical conclusion is cautious: prompt and model choice clearly affect parse success, field completion, and missing-tone frequency, but not all model comparisons are yet fully matched on identical inputs. Therefore, stability is already measurable, but not yet fully controlled.

## 4.4 Comparison with State-of-the-Art

The system should be compared with state-of-the-art work carefully. It is stronger than many narrower ABSA or climate-classification pipelines in terms of workflow scope, provenance preservation, and dashboard-based explainability. It is weaker than established supervised benchmarks in terms of final label-validated performance reporting.

Relative to traditional ABSA pipelines, the present system begins from raw PDFs rather than pre-cleaned text and preserves the entire transformation chain from OCR to structured records. Relative to ClimateBERT-only approaches, it models a broader ESG taxonomy and explicitly distinguishes commitment, action, and outcome. Relative to pure LLM extraction, it preserves parse diagnostics, run metadata, and revision artifacts rather than reporting successful outputs only.

The current ClimateBERT proxy agreement of 0.837 and kappa of 0.645 suggest that the system is not disconnected from domain-specific state-of-the-art climate semantics. However, the thesis contribution should still be framed primarily as an executable, auditable ESG ABSA framework rather than a final large-scale benchmark winner.

## 4.5 Ground-Truth Readiness and Explainability Outputs

One of the most important results of the current experiment stage is that the system already supports benchmark construction. It contains silver-label tables, review queues, disagreement views, metrics pages, and human-editable fields that can evolve into a stronger evaluation dataset.

The implementation also provides explainability signals. Rule-based and dashboard artifacts highlight common lexical patterns associated with tone categories, such as forward-looking markers for commitment, implementation verbs for action, and achieved-result language for outcome. Ontology-aware outputs further support interpretation by linking extracted records to structured ESG concepts rather than leaving them as isolated free text.

Taken together, the Chapter 4 results show that the current pipeline is experimentally productive, diagnostically transparent, and already capable of generating meaningful ESG disclosure evidence. Its main weakness is not lack of output, but incomplete validation depth. That boundary is what motivates the discussion and future work in the next chapters.
