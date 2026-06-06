# Chapter 3 Methodology Page-by-Page Checklist Template

Use this checklist when analyzing or building the methodology chapter of another thesis, dissertation, or long research paper. The goal is not to copy the topic, but to copy the **structural function** of each page.

---

# Section 3.1: Overview of the Methodology

**Expected length:** 2-3 pages
**Purpose:** Introduce the whole methodological design before technical details.

## Page 1 Checklist: Introduce the Core Research Strategy

Use this page to establish the main methodological idea.

Checklist:

* [ ] State the overall research objective of the methodology chapter.
* [ ] Introduce the main pipeline, framework, or research design.
* [ ] Explain whether the method uses one framework, multiple frameworks, or a comparison strategy.
* [ ] Identify the main inputs and outputs of the system.
* [ ] Explain why the chosen methodological direction is suitable for the research problem.
* [ ] Briefly contrast the proposed approach with traditional or simpler approaches.
* [ ] Connect the methodology to the research questions or thesis aim.
* [ ] Avoid deep technical details; keep this page as a high-level introduction.

General writing pattern:

> This page should answer:
> **What is the main methodological strategy of the study?**

---

## Page 2 Checklist: Provide the System Architecture

Use this page to visually explain the whole methodology.

Checklist:

* [ ] Include a system architecture diagram, pipeline diagram, or workflow figure.
* [ ] Show the major components of the method.
* [ ] Show how data moves from input to output.
* [ ] Label each major stage clearly.
* [ ] Explain the role of each component in the diagram.
* [ ] Briefly describe how the stages connect to one another.
* [ ] Use the figure as the visual anchor for the rest of the chapter.
* [ ] Refer to this figure when explaining later sections.

General writing pattern:

> This page should answer:
> **How does the whole system work from beginning to end?**

---

## Page 3 Checklist: Define Design Principles or Methodological Assumptions

Use this page to explain the principles guiding the method.

Checklist:

* [ ] List the main design principles of the methodology.
* [ ] Explain why each principle matters.
* [ ] Connect each principle to a technical decision later in the chapter.
* [ ] Define important methodological assumptions.
* [ ] Explain what the system prioritizes, such as interpretability, accuracy, efficiency, scalability, robustness, temporal consistency, or domain relevance.
* [ ] Prepare the reader for the detailed pipeline sections that follow.

General writing pattern:

> This page should answer:
> **What principles guide the design of the methodology?**

---

# Section 3.2: Data Sources

**Expected length:** 2-3 pages
**Purpose:** Justify the dataset, data source, or research material.

## Page 4 Checklist: Introduce the Dataset or Data Source

Use this page to define the main data used in the study.

Checklist:

* [ ] Name the dataset, corpus, documents, interviews, videos, reports, or source materials.
* [ ] Explain what the dataset contains.
* [ ] State the size of the dataset.
* [ ] Explain why this dataset is suitable for the research problem.
* [ ] Describe the domain, context, or population represented by the data.
* [ ] Connect the dataset to the research questions.
* [ ] Mention whether the dataset is public, private, collected, scraped, annotated, or generated.

General writing pattern:

> This page should answer:
> **What data is used, and why is it appropriate?**

---

## Page 5 Checklist: Describe Technical Data Characteristics and Sampling

Use this page to explain the technical properties and selection strategy.

Checklist:

* [ ] Describe the data format.
* [ ] Describe the number of samples, files, records, pages, clips, documents, or observations.
* [ ] Explain the relevant technical characteristics.
* [ ] Explain any sampling strategy.
* [ ] Justify why a subset is used, if applicable.
* [ ] Explain inclusion and exclusion criteria.
* [ ] Discuss class balance, demographic balance, domain balance, or temporal coverage if relevant.
* [ ] Explain computational constraints that influenced the data selection.

General writing pattern:

> This page should answer:
> **What are the technical properties of the data, and how was the final sample selected?**

---

## Page 6 Checklist: Discuss Ethics, Bias, and Data Limitations

Use this page to show responsible handling of data.

Checklist:

* [ ] Discuss consent, privacy, anonymity, or licensing.
* [ ] Explain whether the data contains sensitive information.
* [ ] Discuss possible demographic, cultural, linguistic, or domain bias.
* [ ] Explain how bias is mitigated or acknowledged.
* [ ] Mention data quality issues.
* [ ] Mention limitations of the dataset.
* [ ] Explain how these limitations affect generalizability.
* [ ] Connect ethical considerations to the research design.

General writing pattern:

> This page should answer:
> **What ethical, bias, and limitation issues exist in the data?**

---

# Section 3.3: Preprocessing Pipeline

**Expected length:** 4-5 pages
**Purpose:** Explain how raw data becomes usable input.

## Page 7 Checklist: Explain First-Stage Data Extraction

Use this page to explain the first transformation from raw data.

Checklist:

* [ ] Describe how raw data is loaded or extracted.
* [ ] Explain the first preprocessing step.
* [ ] Define the unit of analysis, such as frame, sentence, paragraph, document, segment, record, or sample.
* [ ] Explain why this unit of analysis is suitable.
* [ ] Describe any downsampling, filtering, segmentation, or splitting.
* [ ] Justify efficiency decisions.
* [ ] Explain what output is produced by this step.

General writing pattern:

> This page should answer:
> **How is the raw data first converted into analyzable units?**

---

## Page 8 Checklist: Explain Data Standardization and Tooling

Use this page to describe tools and standard formats.

Checklist:

* [ ] Identify the tools, libraries, or software used.
* [ ] Explain why these tools were chosen.
* [ ] Describe the output format of each preprocessing stage.
* [ ] Standardize file format, resolution, sampling rate, encoding, schema, or structure.
* [ ] Explain storage conventions.
* [ ] Describe how processed files are organized.
* [ ] Mention reproducibility details such as version, configuration, or command logic if important.

General writing pattern:

> This page should answer:
> **What tools and formats are used to standardize the data?**

---

## Page 9 Checklist: Convert Data into a Secondary Modality or Representation

Use this page when the study converts one form of data into another.

Checklist:

* [ ] Explain conversion from one modality or format to another.
* [ ] Example conversions: audio to text, PDF to text, image to features, video to frames, reports to structured tables.
* [ ] Identify the model or tool used for conversion.
* [ ] Explain why the tool is suitable.
* [ ] Describe post-processing after conversion.
* [ ] Explain how errors are handled.
* [ ] Include a figure if the conversion pipeline is complex.

General writing pattern:

> This page should answer:
> **How is the raw source transformed into another usable representation?**

---

## Page 10 Checklist: Explain Alignment or Synchronization

Use this page if the method combines multiple data sources, modalities, or time steps.

Checklist:

* [ ] Explain how different data sources are aligned.
* [ ] Define the alignment unit, such as timestamp, sentence, paragraph, page, entity, ID, or segment.
* [ ] Explain the alignment algorithm, matching rule, or mapping process.
* [ ] Justify the expected precision or tolerance.
* [ ] Compare with alternative alignment methods if relevant.
* [ ] Include an alignment diagram if useful.
* [ ] Explain how alignment errors are detected.

General writing pattern:

> This page should answer:
> **How are different inputs connected or synchronized?**

---

## Page 11 Checklist: Verify Preprocessing Quality

Use this page to explain validation of the preprocessing pipeline.

Checklist:

* [ ] Describe quality checks after preprocessing.
* [ ] Define acceptable tolerance or error thresholds.
* [ ] Explain how missing, noisy, or failed cases are handled.
* [ ] Mention manual inspection if used.
* [ ] Mention automated validation if used.
* [ ] Explain how preprocessing quality affects later modeling.
* [ ] Summarize the final preprocessed dataset.

General writing pattern:

> This page should answer:
> **How do we know the preprocessed data is reliable enough for analysis?**

---

# Section 3.4: Feature Extraction or Representation Learning

**Expected length:** 10-16 pages
**Purpose:** Explain how meaningful features or embeddings are produced.

## Page 12 Checklist: Introduce Feature Extraction Strategy

Use this page to introduce the logic of feature extraction.

Checklist:

* [ ] Explain what types of features are extracted.
* [ ] Group features by modality, source, component, or analytical role.
* [ ] Explain the difference between handcrafted features and learned representations if relevant.
* [ ] Connect each feature group to the research objective.
* [ ] Explain how features will later be used by the model or framework.
* [ ] Provide a transition from preprocessing to modeling.

General writing pattern:

> This page should answer:
> **What features are extracted, and why are they needed?**

---

## Page 13 Checklist: Explain First Feature Group

Use this page for the first major feature category.

Checklist:

* [ ] Define the feature group.
* [ ] Explain what signal, behavior, pattern, or information it captures.
* [ ] Identify the tool, model, or formula used.
* [ ] Provide an equation if the feature is mathematically computed.
* [ ] Explain the output dimension, format, or score.
* [ ] Justify why this feature is relevant.
* [ ] Explain limitations of the feature.

General writing pattern:

> This page should answer:
> **How is the first major feature group computed?**

---

## Page 14 Checklist: Explain Thresholding, Change Detection, or Event Detection

Use this page when the method detects important changes or events.

Checklist:

* [ ] Define what counts as a meaningful change or event.
* [ ] Explain the thresholding method.
* [ ] Provide equations if thresholds are adaptive or statistical.
* [ ] Explain how false positives are reduced.
* [ ] Include a graph or example if helpful.
* [ ] Explain how detected events are stored.
* [ ] Connect detected events to later scoring or modeling.

General writing pattern:

> This page should answer:
> **How does the method decide that something important has happened?**

---

## Page 15 Checklist: Explain Windowing or Local Context Logic

Use this page if nearby context matters.

Checklist:

* [ ] Define the window size.
* [ ] Explain why this window size is chosen.
* [ ] Explain what is captured inside the window.
* [ ] Discuss whether the window is temporal, textual, spatial, semantic, or document-based.
* [ ] Explain how overlapping windows are handled.
* [ ] Explain how window-level results are aggregated.
* [ ] Connect local context to later feature fusion or scoring.

General writing pattern:

> This page should answer:
> **How does the method capture local context around important units?**

---

## Page 16 Checklist: Explain Semantic or Deep Representation Features

Use this page for embedding-based or model-based representations.

Checklist:

* [ ] Introduce the embedding model or representation model.
* [ ] Explain what semantic information it captures.
* [ ] Describe the model architecture briefly.
* [ ] Explain input and output format.
* [ ] Provide the embedding dimension if relevant.
* [ ] Justify why this model is chosen over alternatives.
* [ ] Explain how embeddings are stored or passed to the next stage.

General writing pattern:

> This page should answer:
> **How does the method represent deeper semantic meaning?**

---

## Page 17 Checklist: Provide Mathematical Justification for the Representation

Use this page to formalize the representation method.

Checklist:

* [ ] Provide the loss function, embedding equation, scoring formula, or transformation equation.
* [ ] Explain each variable.
* [ ] Explain what the equation optimizes or measures.
* [ ] Connect the equation to the research objective.
* [ ] Compare briefly with alternative models if useful.
* [ ] Explain why the selected representation is appropriate.

General writing pattern:

> This page should answer:
> **What is the mathematical logic behind the selected representation?**

---

## Page 18 Checklist: Explain Feature Enhancement or Feature Combination

Use this page when raw features are enriched with additional signals.

Checklist:

* [ ] Explain how base features are modified or enhanced.
* [ ] Describe which additional indicators are added.
* [ ] Explain whether features are concatenated, weighted, normalized, or fused.
* [ ] Explain why enhancement improves the representation.
* [ ] Mention dimensionality changes if relevant.
* [ ] Explain how enhanced features are used later.

General writing pattern:

> This page should answer:
> **How are basic features improved before modeling?**

---

## Page 19 Checklist: Introduce Second Modality or Second Feature Group

Use this page to transition to another feature type.

Checklist:

* [ ] Introduce the second feature group.
* [ ] Explain what kind of information this group captures.
* [ ] Identify tools, algorithms, or models used.
* [ ] Explain why this feature group complements the previous one.
* [ ] Define the input and output.
* [ ] Explain preprocessing requirements specific to this feature group.

General writing pattern:

> This page should answer:
> **What additional information is captured by the second feature group?**

---

## Page 20 Checklist: Formalize the Second Feature Group

Use this page to provide the technical formulation.

Checklist:

* [ ] Provide equations or algorithmic logic.
* [ ] Explain how the feature is calculated.
* [ ] Define important variables.
* [ ] Explain the interpretation of the resulting values.
* [ ] Discuss noise, reliability, or sensitivity.
* [ ] Justify the method against alternatives.

General writing pattern:

> This page should answer:
> **How is the second feature group technically computed?**

---

## Page 21 Checklist: Add Supporting Feature Measures

Use this page for additional complementary indicators.

Checklist:

* [ ] Introduce secondary or supporting features.
* [ ] Explain what each supporting feature measures.
* [ ] Provide equations if necessary.
* [ ] Explain why these features add useful context.
* [ ] Mention whether they are used directly, normalized, or combined.
* [ ] Explain how they improve robustness.

General writing pattern:

> This page should answer:
> **What supporting signals are added to strengthen the analysis?**

---

## Page 22 Checklist: Visualize Extracted Features

Use this page to show examples of extracted features.

Checklist:

* [ ] Include a figure, graph, plot, or example output.
* [ ] Show how the extracted features look in practice.
* [ ] Explain what the reader should observe in the figure.
* [ ] Link visual patterns to methodological claims.
* [ ] Use the figure to confirm that the extraction process is meaningful.
* [ ] Avoid using the figure as decoration; interpret it clearly.

General writing pattern:

> This page should answer:
> **What do the extracted features look like in real examples?**

---

## Page 23 Checklist: Introduce Contextual Representation Model

Use this page for advanced representation learning.

Checklist:

* [ ] Introduce the contextual model.
* [ ] Explain whether it is supervised, self-supervised, pretrained, fine-tuned, or frozen.
* [ ] Explain what type of context the model captures.
* [ ] Explain why contextual representation is needed beyond handcrafted features.
* [ ] Describe the model's training or pretraining logic briefly.
* [ ] Explain how the contextual features support the final task.

General writing pattern:

> This page should answer:
> **Why is a contextual representation model needed?**

---

## Page 24 Checklist: Formalize Contextual Embeddings and Transition to Next Modality

Use this page to close one modality and move to another.

Checklist:

* [ ] Provide the equation or notation for contextual embeddings.
* [ ] Explain the shape or dimension of the embedding.
* [ ] Explain how frame-level, token-level, sentence-level, or segment-level embeddings are produced.
* [ ] Explain how these embeddings are aggregated.
* [ ] Summarize the completed feature group.
* [ ] Transition clearly to the next feature group.

General writing pattern:

> This page should answer:
> **How is the contextual representation produced and passed forward?**

---

## Page 25 Checklist: Explain Lexical or Surface-Level Features

Use this page for interpretable text, metadata, or structured features.

Checklist:

* [ ] Introduce interpretable feature extraction.
* [ ] Explain why surface-level features are useful.
* [ ] Provide formula or scoring logic if relevant.
* [ ] Explain cleaning steps specific to this feature type.
* [ ] Explain how noise is removed.
* [ ] Explain how features are ranked or selected.
* [ ] Connect these features to interpretability.

General writing pattern:

> This page should answer:
> **What simple but interpretable features are extracted?**

---

## Page 26 Checklist: Explain Sentiment, Tone, Polarity, or Classification Features

Use this page for affective, categorical, or label-based features.

Checklist:

* [ ] Define the classification target.
* [ ] Explain the model, lexicon, classifier, or rule set used.
* [ ] Explain how contextual modifiers are handled.
* [ ] Explain how negation, intensifiers, ambiguity, or domain-specific language are handled.
* [ ] Explain the output labels or scores.
* [ ] Discuss possible classification errors.
* [ ] Explain how the labels are used later.

General writing pattern:

> This page should answer:
> **How are categorical or affective features detected?**

---

## Page 27 Checklist: Explain Entity, Concept, or Information Extraction

Use this page for named entities, aspects, topics, events, or concepts.

Checklist:

* [ ] Define what entities or concepts are extracted.
* [ ] Explain the extraction tool or model.
* [ ] Explain the label schema.
* [ ] Explain how extracted concepts are cleaned or filtered.
* [ ] Explain how entities connect to the research task.
* [ ] Introduce any contextual embedding model used afterward.

General writing pattern:

> This page should answer:
> **What key concepts or entities are extracted from the data?**

---

## Page 28 Checklist: Provide Architecture Diagram for Representation Model

Use this page to visually explain a complex model.

Checklist:

* [ ] Include an architecture diagram.
* [ ] Show the input, encoder, intermediate layers, and output.
* [ ] Explain each component of the architecture.
* [ ] Explain why this architecture fits the data.
* [ ] Link the diagram to the previous feature extraction discussion.
* [ ] Prepare the reader for the final embedding formulation.

General writing pattern:

> This page should answer:
> **How is the representation model architecturally organized?**

---

## Page 29 Checklist: Finalize Feature Encoding

Use this page to present the final representation used by the framework.

Checklist:

* [ ] Provide the final encoding equation.
* [ ] Explain the final feature vector or embedding.
* [ ] State the dimensionality if relevant.
* [ ] Explain whether features are sentence-level, document-level, segment-level, or sample-level.
* [ ] Explain how all extracted features are prepared for the next framework stage.
* [ ] Summarize the feature extraction section.

General writing pattern:

> This page should answer:
> **What final representation is passed into the proposed method?**

---

# Section 3.5: Proposed Framework or Model

**Expected length:** 10-12 pages
**Purpose:** Explain how the method uses extracted features to produce final outputs.

## Page 30 Checklist: Introduce the Proposed Frameworks

Use this page to introduce the main modeling or reasoning stage.

Checklist:

* [ ] State the purpose of the framework.
* [ ] Explain how the framework uses the extracted features.
* [ ] Identify whether there is one method, two methods, or several compared methods.
* [ ] Explain the difference between baseline and proposed method if applicable.
* [ ] Explain the main advantage of each framework.
* [ ] Transition from feature extraction to output generation.

General writing pattern:

> This page should answer:
> **How are the extracted features used to solve the research task?**

---

## Page 31 Checklist: Explain the First Framework Architecture

Use this page for the first proposed method.

Checklist:

* [ ] Name the first framework.
* [ ] Explain its main idea.
* [ ] Include a framework diagram.
* [ ] Explain the input, processing steps, and output.
* [ ] Explain why this framework is useful.
* [ ] Emphasize interpretability, simplicity, efficiency, or domain logic if relevant.

General writing pattern:

> This page should answer:
> **How does the first framework work at a high level?**

---

## Page 32 Checklist: Explain Alignment, Weighting, and Evidence Scoring

Use this page for scoring or decision logic.

Checklist:

* [ ] Explain how different cues or features are aligned.
* [ ] Define scoring windows or matching rules.
* [ ] Explain confidence weighting.
* [ ] Provide evidence scoring formula.
* [ ] Explain how multiple signals contribute to one score.
* [ ] Explain how the score affects the final output.

General writing pattern:

> This page should answer:
> **How does the framework combine evidence from multiple sources?**

---

## Page 33 Checklist: Explain Thresholding, Ranking, and Selection

Use this page for decision-making logic.

Checklist:

* [ ] Define the threshold criterion.
* [ ] Explain how candidates are ranked.
* [ ] Provide ranking formula or algorithm.
* [ ] Explain how selected items are chosen.
* [ ] Explain sentence, segment, document, or sample weighting.
* [ ] Explain how weak candidates are removed.

General writing pattern:

> This page should answer:
> **How does the framework decide what is important enough to select?**

---

## Page 34 Checklist: Explain Normalization, Diversity, and Final Assembly

Use this page for final output construction.

Checklist:

* [ ] Explain score normalization.
* [ ] Explain how redundancy is reduced.
* [ ] Explain how diversity is preserved.
* [ ] Explain how selected items are assembled into final output.
* [ ] Explain ordering logic.
* [ ] Explain length constraints.
* [ ] Provide final output formula if relevant.

General writing pattern:

> This page should answer:
> **How are selected items converted into a coherent final output?**

---

## Page 35 Checklist: Provide Full Algorithm or Pseudocode

Use this page to consolidate the first framework.

Checklist:

* [ ] Provide pseudocode for the full method.
* [ ] Show input and output clearly.
* [ ] List the main processing steps in order.
* [ ] Include loops, scoring, ranking, and selection steps.
* [ ] Make the algorithm reproducible.
* [ ] Explain the algorithm after presenting it.
* [ ] Ensure the pseudocode matches the earlier equations.

General writing pattern:

> This page should answer:
> **What is the complete step-by-step algorithm?**

---

## Page 36 Checklist: Introduce the Second Framework

Use this page if the thesis compares or proposes a second method.

Checklist:

* [ ] Name the second framework.
* [ ] Explain why a second framework is needed.
* [ ] Include an architecture diagram.
* [ ] Explain the main components.
* [ ] Explain how it differs from the first framework.
* [ ] Explain its expected strengths.
* [ ] Prepare the reader for mathematical formulation.

General writing pattern:

> This page should answer:
> **What is the second framework, and why is it introduced?**

---

## Page 37 Checklist: Define Formal Notation and Model Configuration

Use this page to set up the model mathematically.

Checklist:

* [ ] Define input notation.
* [ ] Define output notation.
* [ ] Define modality-specific or component-specific variables.
* [ ] Explain model depth, layers, hidden size, heads, or configuration.
* [ ] Explain how each input enters the model.
* [ ] Clarify assumptions before equations become complex.

General writing pattern:

> This page should answer:
> **What notation and configuration are used by the model?**

---

## Page 38 Checklist: Explain Encoding for First and Second Inputs

Use this page for model encoder details.

Checklist:

* [ ] Explain how the first input type is encoded.
* [ ] Provide equations if needed.
* [ ] Explain how the second input type is encoded.
* [ ] Provide equations if needed.
* [ ] Include an encoder architecture figure if useful.
* [ ] Explain how encoded representations are passed forward.

General writing pattern:

> This page should answer:
> **How are the main inputs encoded into model representations?**

---

## Page 39 Checklist: Explain Encoding for Third Input and Start Fusion

Use this page to complete encoding and introduce fusion.

Checklist:

* [ ] Explain how the third input type is encoded.
* [ ] Provide equations if relevant.
* [ ] Explain how all encoded inputs are prepared for fusion.
* [ ] Introduce attention, fusion, aggregation, voting, ensemble, or graph integration.
* [ ] Explain why fusion is necessary.
* [ ] Transition to the main fusion mechanism.

General writing pattern:

> This page should answer:
> **How are all input representations prepared for integration?**

---

## Page 40 Checklist: Explain Fusion, Attention, or Decision Mechanism

Use this page for the technical heart of the model.

Checklist:

* [ ] Define the unified context representation.
* [ ] Explain attention, fusion, aggregation, or decision logic.
* [ ] Provide equations.
* [ ] Explain each term in the equations.
* [ ] Explain how the model produces intermediate outputs.
* [ ] Explain how final predictions or generated outputs are formed.

General writing pattern:

> This page should answer:
> **How does the model combine information and generate decisions?**

---

## Page 41 Checklist: Explain Inference and Output Mapping

Use this page to explain how model outputs become real outputs.

Checklist:

* [ ] Explain the inference process.
* [ ] Define start/end tokens, stopping rules, thresholds, or decision criteria if relevant.
* [ ] Explain how abstract model outputs are mapped back to real data.
* [ ] Explain similarity matching or retrieval logic if used.
* [ ] Explain ordering, filtering, or post-processing.
* [ ] Explain final output generation.

General writing pattern:

> This page should answer:
> **How does the trained or designed model produce the final usable output?**

---

# Section 3.6: Ground Truth, Pseudo-Ground Truth, or Evaluation Reference

**Expected length:** 2-3 pages
**Purpose:** Explain how reference labels, summaries, annotations, or validation targets are created.

## Page 42 Checklist: Explain the Ground-Truth Problem

Use this page to explain why reference data is needed.

Checklist:

* [ ] Explain whether true ground truth exists.
* [ ] Explain why existing labels or references are insufficient.
* [ ] Describe the challenge of annotation, scarcity, subjectivity, cost, or domain mismatch.
* [ ] Explain what kind of reference output is needed.
* [ ] Connect this reference output to training or evaluation.
* [ ] Reuse earlier preprocessing outputs if relevant.

General writing pattern:

> This page should answer:
> **Why is a special ground-truth or reference construction process needed?**

---

## Page 43 Checklist: Explain Pseudo-Labeling, Annotation, or Reference Generation

Use this page to explain how labels or reference outputs are created.

Checklist:

* [ ] Identify the method used to generate labels or references.
* [ ] Explain whether humans, rules, models, LLMs, heuristics, or external datasets are used.
* [ ] Explain prompt design if LLMs are used.
* [ ] Explain annotation guidelines if humans are used.
* [ ] Explain labeling rules if heuristics are used.
* [ ] Use multiple models, annotators, or validation passes if possible.
* [ ] Explain how consistency is checked.

General writing pattern:

> This page should answer:
> **How are reference outputs created?**

---

## Page 44 Checklist: Explain Mapping, Validation, and Constraints

Use this page to finalize ground-truth construction.

Checklist:

* [ ] Explain how generated labels or references are mapped back to the original data.
* [ ] Explain validation rules.
* [ ] Explain chronological, structural, semantic, or logical consistency checks.
* [ ] Explain length, coverage, confidence, or quality constraints.
* [ ] Explain how invalid outputs are removed or corrected.
* [ ] Summarize the final reference dataset.
* [ ] Mention limitations of pseudo-ground truth.

General writing pattern:

> This page should answer:
> **How are generated references validated and made usable for evaluation?**

---

# Condensed One-Line Checklist Version

Use this faster version when reviewing another paper.

| Page Function             | Checklist Question                                        |
| ------------------------- | --------------------------------------------------------- |
| Method overview           | Does the paper explain the main methodological strategy?  |
| Architecture              | Does it show the full system or workflow diagram?         |
| Design principles         | Does it explain the principles guiding the method?        |
| Dataset introduction      | Does it justify the dataset or data source?               |
| Data characteristics      | Does it describe size, format, sampling, and constraints? |
| Ethics and bias           | Does it discuss ethical issues, bias, and limitations?    |
| First preprocessing       | Does it explain how raw data becomes analyzable units?    |
| Standardization           | Does it explain tools, formats, and storage?              |
| Conversion                | Does it explain conversion into another representation?   |
| Alignment                 | Does it explain synchronization or mapping?               |
| Verification              | Does it validate preprocessing quality?                   |
| Feature strategy          | Does it introduce all extracted feature groups?           |
| Feature group 1           | Does it explain the first major feature group?            |
| Event detection           | Does it define thresholds or important changes?           |
| Windowing                 | Does it explain local context handling?                   |
| Deep representation       | Does it explain embeddings or semantic representation?    |
| Mathematical basis        | Does it formalize the representation?                     |
| Feature enhancement       | Does it explain feature fusion or enrichment?             |
| Feature group 2           | Does it introduce another modality or feature group?      |
| Feature formalization     | Does it compute that feature technically?                 |
| Supporting features       | Does it add secondary measures?                           |
| Feature visualization     | Does it show extracted features visually?                 |
| Contextual model          | Does it explain advanced representation learning?         |
| Embedding output          | Does it define final contextual embeddings?               |
| Lexical features          | Does it explain interpretable features?                   |
| Classification features   | Does it explain sentiment, tone, or label extraction?     |
| Entity/concept extraction | Does it extract entities, aspects, or concepts?           |
| Model architecture        | Does it show architecture for representation?             |
| Final encoding            | Does it define the final feature vector?                  |
| Framework intro           | Does it explain how features solve the task?              |
| Framework 1               | Does it explain the first method?                         |
| Evidence scoring          | Does it combine evidence from sources?                    |
| Ranking                   | Does it rank or select important units?                   |
| Output assembly           | Does it normalize, diversify, and assemble output?        |
| Algorithm                 | Does it provide full pseudocode?                          |
| Framework 2               | Does it introduce the second method?                      |
| Notation                  | Does it define formal input/output notation?              |
| Encoding                  | Does it explain encoder logic?                            |
| Fusion                    | Does it explain how representations are combined?         |
| Decision/generation       | Does it explain output generation?                        |
| Inference                 | Does it map model output back to real data?               |
| Ground-truth issue        | Does it explain why reference labels are needed?          |
| Reference generation      | Does it explain annotation or pseudo-labeling?            |
| Validation                | Does it validate and constrain the final references?      |

---

# How to Use This Checklist for Another Paper

When reading another paper, do not expect the exact same topics. Instead, check the **function** of each part.

For example:

* If the original paper has "frame extraction," another paper may have "PDF parsing" or "survey response cleaning."
* If the original paper has "audio feature extraction," another paper may have "financial indicator extraction."
* If the original paper has "CLIP embeddings," another paper may have "BERT embeddings," "graph embeddings," or "topic vectors."
* If the original paper has "video segment mapping," another paper may have "evidence sentence mapping," "document retrieval mapping," or "label-to-source mapping."

The reusable idea is:

> Each page should perform one clear methodological job.

A strong methodology chapter usually contains these jobs:

1. Introduce the methodological design.
2. Show the system architecture.
3. Justify the data.
4. Prepare the raw data.
5. Extract features or representations.
6. Explain the proposed framework.
7. Formalize the method with equations or algorithms.
8. Explain inference or output generation.
9. Explain ground truth or pseudo-ground truth.
10. Validate that the output is reliable.
