# Chapter 2 Related Works

## 2.1 Corporate Sustainability Reporting and the Greenwashing Challenge

### 2.1.1 The Technical Complexity of ESG Disclosures

Sustainability reports are inherently difficult to process because they are typically semi-structured PDF documents containing a mix of qualitative narratives, quantitative tables, and visual imagery. Technically, the challenge begins with **high-fidelity data extraction**; many reports utilize complex layouts that require robust OCR and parsing pipelines to ensure that textual data is not lost or corrupted during the ingestion phase  . Research indicates that data gaps in reporting often stem from these extraction failures rather than a lack of information, making the preprocessing pipeline (as seen in **Section 3.3**) a critical precursor to greenwashing detection  [@jacob_beck_9548a833].

### 2.1.2 NLP Frameworks for Greenwashing Detection

Recent literature has moved toward a **multi-dimensional textual framework** to identify greenwashing. This involves analyzing specific technical features:

- **Thematic and Sentiment Features:** Studies have shown that greenwashing is often characterized by a high frequency of "positive-sentiment" words paired with a lack of concrete, thematic "action" words  [@xiaojia_wang_02351a60]. High-risk reports typically exhibit a "sentimental mask," where optimistic language is used to hide a lack of specific environmental targets  [@xiaojia_wang_02351a60].
- **"Cheap Talk" and Cherry-Picking:** Advanced models like **ClimateBERT** have been used to identify "cheap talk"—vague, non-committal disclosures—and "cherry-picking," where firms only report on positive climate-related risks while omitting material negative ones  [@julia_bingler_268445e3]. Technically, this is achieved by comparing a firm's disclosure patterns against industry-wide benchmarks or historical data to find significant deviations  [@julia_bingler_268445e3].

### 2.1.3 Aspect-Action Analysis and Semantic Inconsistency

A significant technical advancement in this field is **Aspect-Action Analysis**. This method goes beyond simple sentiment analysis by extracting specific "aspects" (e.g., carbon emissions reduction) and linking them to "actions" (e.g., "invested \$50M in carbon capture")  [@keane_ong_369a0b63]. Greenwashing is technically identified when there is a **semantic inconsistency** or a cross-category generalization—such as when a company makes broad environmental claims based on a single, minor action  [@keane_ong_369a0b63]. This requires models with high "cross-category generalization" capabilities to detect if a company's "green" claims in one sector are being used to offset "brown" activities in another  [@keane_ong_369a0b63].

### 2.1.4 Monitoring Systems and Empirical Testing

Newer systems, such as **DeepGreen**, utilize Large Language Models to create monitoring systems designed for empirical testing  [@chong_xu_bff21576]. These systems are technically designed to:

1. **Extract structured evidence** from unstructured reports to verify if specific ESG metrics (like Scope 1 or 2 emissions) are reported with sufficient detail  [@chong_xu_bff21576].
1. **Compare internal reporting with external news**, using LLMs to check for discrepancies between what a company says in its ESG report and what is reported in the media
1. **Score "Greenwashing Tendency"** by applying weighted metrics to the extracted data, identifying when a firm’s rhetoric significantly outpaces its data-backed performance  [@chong_xu_bff21576].

### 2.1.5 Technical Limitations: The "Soft Language" Problem

A major hurdle remains the "soft" nature of ESG language. LLMs must be sensitive enough to distinguish between **substantive disclosures** and **boilerplate language** that satisfies regulatory checklists without providing material insight  [@frederik_maibaum_b8629037]. This provides the technical justification for **Section 3.4.4**, as standard machine learning baselines often fail to capture the subtle linguistic nuances that separate genuine commitment from strategic ambiguity

### 2.1.6 Table: State-of-the-Art in NLP-Driven ESG and Greenwashing Analysis

Below is a comprehensive table of state-of-the-art research relevant to Chapter 2.1, focusing on the technical and NLP methodologies used to address greenwashing and ESG extraction. This synthesis highlights how current frameworks transition from simple keyword counting toward complex, intent-aware architectures that verify sustainability claims against verifiable operational evidence  [@keane_ong_0a5de439]. On top of that, there next table focus on the technical nuances of goal alignment, model sensitivity, and sector-specific extraction, complementing the previous literature by addressing the "soft language" and benchmarking challenges in ESG.

*Table: caption*

*Table: caption*

## 2.2 Evolution of NLP in Sustainability Analysis

The methodology for analyzing corporate sustainability has undergone a significant transformation, evolving from simple keyword counting to sophisticated semantic understanding. This progression reflects the increasing complexity of ESG disclosures and the need for tools that can detect nuanced linguistic patterns like greenwashing.

### 2.2.1 Dictionary-Based and Statistical Foundations

Early NLP applications in sustainability relied heavily on **dictionary-based techniques** and **lexicons**. These methods used predefined lists of "green" or "socially responsible" keywords to quantify the volume of ESG communication  [@frederik_maibaum_b8629037]. While foundational, research has shown that dictionaries exhibit a large variation in quality and fail to capture the context in which words are used  [@frederik_maibaum_b8629037]. For instance, a dictionary might flag the word "carbon" as a positive environmental indicator, even if the text discusses a "failure to reduce carbon emissions"  [@julia_bingler_268445e3]. Subsequent statistical methods, such as **Latent Dirichlet Allocation** for topic modeling, offered improved performance over dictionaries by identifying latent themes across reports, yet they remained limited by their inability to handle complex semantic relationships  [@frederik_maibaum_b8629037].

### 2.2.2 The Transformer Revolution and Contextual Embeddings

The introduction of the **Transformer architecture** and models like **BERT** marked a paradigm shift. Unlike previous word embedding techniques (e.g., Word2Vec) that assigned a single vector to a word regardless of context, Transformers use attention mechanisms to derive context-dependent meanings  [@frederik_maibaum_b8629037]. This capability is crucial for ESG analysis, where the same term can have vastly different implications depending on the surrounding text  [@natraj_raman_009776f2]. Studies demonstrate that fine-tuned Transformer models significantly outperform classical machine learning baselines in classifying material ESG risks and identifying sustainability trends in corporate earnings calls  .

### 2.2.3 Domain-Specific Specialization: The Rise of ClimateBERT

As the limitations of general-purpose language models became apparent, the field shifted toward **domain-specific fine-tuning**. A prominent example is **ClimateBERT**, a model pretrained on millions of climate-related sentences from corporate reports and news  .

- **Precision in "Cheap Talk" Detection:** ClimateBERT has proven highly effective at identifying "cheap talk"—vague, non-committal climate disclosures that satisfy regulatory requirements without committing to material action  [@julia_bingler_268445e3].
- **Enhanced Performance:** By training on domain-specific corpora, these models achieve much higher accuracy in detecting climate-related risks compared to general models like BERT-base  .This specialization has extended to specific sub-domains, with researchers developing distinct models for the "E," "S," and "G" components to capture the unique linguistic styles of each pillar  [@tobias_schimanski_4e192ec5].

### 2.2.4 Large Language Models and Generative Extraction

The current frontier in the evolution of ESG NLP is the adoption of **Large Language Models** such as GPT-4 and Llama. These models represent a move from simple text classification to **structured semantic extraction**  [@seyed_alireza_mousavian_anaraki_b56a1c0f].

- **One-Shot and Few-Shot Capabilities:** Recent evaluations show that LLMs, when paired with well-designed prompts, can surpass earlier fine-tuned models in extracting structured data from unstructured reports  [@frederik_maibaum_b8629037].
- **Multi-Dimensional Analysis:** LLMs enable more complex tasks, such as **Aspect-Action Analysis**, which links specific environmental aspects to concrete corporate actions to identify inconsistencies  [@keane_ong_369a0b63].
- **Expansion to Nature and Biodiversity:** New datasets and models are now emerging to tackle "nature-related" disclosures, moving beyond carbon-centric analysis to evaluate how companies report on biodiversity and ecosystem services  [@tobias_schimanski_3549ff9f].

### 2.2.5 Table: State-of-the-Art in the Evolution of NLP for Sustainability

The table below summarizes the key milestones in the technical evolution of NLP within sustainability analysis, tracking the shift from lexicon-based systems to domain-specific Transformers and eventually to generative Large Language Models, also the table introduced specialized frameworks and models that represent the transition from general climate classification to more granular, sector-specific, and target-oriented analysis

*Table: caption*

## 2.3 Large Language Models for Structured ESG Extraction

The shift toward Large Language Models represents a fundamental technical pivot from **text classification**—where models simply categorize a paragraph as "Environmental"—to **structured information extraction**, where models extract specific, actionable data points into predefined schemas  .

### 2.3.1 From Classification to Schema-Based Extraction

Traditional NLP models typically perform sequence classification, providing a high-level label for a text block. In contrast, LLMs enable the derivation of structured insights, such as transforming unstructured narrative text into JSON or tabular formats that include specific metrics like Scope 1 emissions, target years, and baseline comparisons  [@marco_bronzini_bf94d949]. This capability is critical for automating the assessment of sustainability reports, which are often composed of semi-structured data that varies significantly between companies  . Research by **Bronzini et al.** demonstrates that LLMs like GPT-4 can derive these structured tables with a level of precision that previously required manual auditing, though the risk of numerical "hallucinations" remains a technical hurdle  [@marco_bronzini_bf94d949].

### 2.3.2 Prompt Engineering and In-Context Learning

A key technical advantage of LLMs in the ESG domain is their ability to perform tasks via **In-Context Learning**, which includes zero-shot and few-shot prompting strategies  [@frederik_maibaum_b8629037]. This eliminates the need for the extensive, task-specific fine-tuning required by earlier models like BERT  .

- **Zero-Shot Extraction:** LLMs can extract ESG data based solely on a natural language description of the schema (aligning with **Section 3.4.1 Schema Layer**)  [@marco_bronzini_bf94d949].
- **Few-Shot Prompting:** Providing a few expert-labeled examples (e.g., how to identify a "Science-Based Target") within the prompt significantly improves model performance on complex, "soft" language tasks  .
- **Chain-of-Thought:** Encouraging the model to "reason" through an extraction—such as explaining *why* a specific sentence constitutes a carbon reduction action—helps mitigate errors in judgment and improves the interpretability of the results  [@arash_hajikhani_cbb2528f].

### 2.3.3 Aspect-Action Linkage and Semantic Mapping

For greenwashing detection, simple keyword matching is insufficient. LLMs excel at **Aspect-Action Analysis**, a technical logic where the model identifies an environmental "aspect" (e.g., water conservation) and attempts to link it to a verifiable "action" (e.g., \$10M investment in desalination plants)  [@keane_ong_369a0b63]. Technically, this involves complex semantic mapping where the LLM evaluates the strength of the connection between a claim and the evidence provided. If a model identifies a high frequency of "aspects" without corresponding "actions," it can flag the report for potential greenwashing based on narrative inconsistency  .

### 2.3.4 Domain-Specific vs. General LLMs

While general LLMs like GPT-4 show high performance, the evolution of the field has led to **domain-specific pre-trained models** (e.g., ESG-BERT or specialized Llama variants). Studies comparing these models indicate that domain-specific pre-training on financial and corporate corpora allows the model to better understand the "jargon" of sustainability reporting, leading to higher accuracy in identifying material risks  . However, general-purpose LLMs often retain a lead in "reasoning" tasks and complex instruction following, which justifies the **Comparative Model Logic** found in **Section 3.4.5**  .

### 2.3.5 Technical Risks: Hallucinations and Grounding

A critical limitation of LLMs in ESG extraction is their sensitivity to input phrasing and their tendency to generate plausible-sounding but factually incorrect data—commonly known as **hallucinations**  [@arash_hajikhani_cbb2528f]. In the context of sustainability, a hallucinated emission figure or target date could lead to incorrect regulatory filings. This technical risk necessitates the use of **External Validators** (like ClimateBERT, as seen in  **Section 3.4.3**) and **Human-in-the-Loop** workflows to verify the extracted "silver labels" before they are accepted as ground truth  .

*Table: caption*

*Table: caption*

## 2.4 Data Gaps and Benchmark Design

The creation of a robust methodology for sustainability analysis is fundamentally constrained by the quality and structure of available data. This section examines the technical "data gaps" identified in current literature and the evolving standards for benchmark design in the ESG domain.

### 2.4.1 Identifying Technical Data Gaps in Sustainability

Despite the increasing volume of reports, significant gaps prevent automated systems from achieving high accuracy.

- **Extraction and Parsing Failures:** A primary technical gap is the failure of automated pipelines to ingest complex, semi-structured PDF layouts  . Research by **Beck et al.** highlights that data gaps in sustainability reporting—particularly regarding greenhouse gas emissions—are often caused by the technical difficulty of extracting data from multi-column tables and non-standardized units within unstructured narratives  [@jacob_beck_9548a833].
- **The Scope 3 Reporting Gap:** While Scope 1 and 2 emissions are increasingly reported with consistency, Scope 3 reporting remains sparse and technically inconsistent across industries, making it the most difficult metric to benchmark accurately  [@jacob_beck_9548a833].
- **"Sentimental Masks" and Omissions:** Data gaps are not always accidental; they can be strategic. Literature identifies "cherry-picking" (reporting only positive metrics) as a practice that creates artificial gaps in a firm’s environmental risk profile  . This requires benchmarks that can identify not just what is present, but what has been omitted  [@julia_bingler_268445e3].

### 2.4.2 The Role of Benchmark Datasets in ESG NLP

A technical benchmark provides a standardized "ground truth" to evaluate model performance. The field is currently shifting from general classification datasets to **specialized extraction benchmarks**:

- **Target-Specific Benchmarking:** Newer benchmarks, such as **ClimateBERT-NetZero**, are designed specifically to evaluate a model's ability to distinguish between vague corporate pledges and verifiable, science-based reduction targets  [@tobias_schimanski_241ada20].
- **Nature and Biodiversity:** As the focus expands beyond carbon, specialized datasets are emerging for nature-related disclosures, addressing the "small data" challenge where high-quality labeled examples of biodiversity impact are scarce  [@tobias_schimanski_3549ff9f].
- **News-Based External Validation:** Benchmarks like the **ESG-FTSE corpus** utilize external news articles to provide an "outside-in" perspective, allowing researchers to check for discrepancies between internal corporate reports and external media narratives  .

### 2.4.3 Technical Requirements for Benchmark Design

According to recent studies, a defensible ESG benchmark must satisfy three core technical requirements:

1. **Granular Unit of Analysis:** Benchmarks must transition from report-level summaries to **paragraph-level extractions** to capture the specific context of claims  [@jacob_beck_9548a833].
1. **Gold Standard Ground Truth:** While "Silver Labels" (generated via weak supervision or LLMs) are useful for initial seeding, a high-fidelity benchmark requires an expert-led **Human Annotation Workflow** to verify the semantic nuances of sustainability language  .
1. **Cross-Category Generalization:** A robust benchmark should test a model's performance across diverse industry sectors (e.g., banking vs. heavy industry) and ESG categories to ensure the methodology is not overfitted to a single domain  .

### 2.4.4 Table: State-of-the-Art in ESG Benchmark Design

For **Section 2.4: Data Gaps and Benchmark Design**, the following table identifies the most recent state-of-the-art benchmarks and datasets designed to address the "expert-scarcity" and "data-fragmentation" problems in sustainability reporting. These works provide the technical foundation for the **Benchmark and Ground Truth Design (Section 3.6)**, and also highlights additional state-of-the-art research focusing on the specific technical gaps identified in corporate reporting and the datasets developed to mitigate them. These works provide the scholarly justification to focus on **Coverage, Stratification, and Resumability (Section 3.6.4)**.

*Table: State-of-the-art ESG benchmarks and dataset design patterns supporting the benchmark and ground-truth construction in Section 3.6*

*Table: caption*
