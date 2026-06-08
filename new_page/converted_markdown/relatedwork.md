## Corporate Sustainability Reporting and the Greenwashing Challenge

### The Technical Complexity of ESG Disclosures

Sustainability reports are inherently difficult to process because they are typically semi-structured PDF documents containing a mix of qualitative narratives, quantitative tables, and visual imagery. Technically, the challenge begins with **high-fidelity data extraction**; many reports utilize complex layouts that require robust OCR and parsing pipelines to ensure that textual data is not lost or corrupted during the ingestion phase  . Research indicates that data gaps in reporting often stem from these extraction failures rather than a lack of information, making the preprocessing pipeline (as seen in **Section 3.3**) a critical precursor to greenwashing detection  .

### NLP Frameworks for Greenwashing Detection

Recent literature has moved toward a **multi-dimensional textual framework** to identify greenwashing. This involves analyzing specific technical features:
-

**Thematic and Sentiment Features:** Studies have shown that greenwashing is often characterized by a high frequency of "positive-sentiment" words paired with a lack of concrete, thematic "action" words  . High-risk reports typically exhibit a "sentimental mask," where optimistic language is used to hide a lack of specific environmental targets  .

**"Cheap Talk" and Cherry-Picking:** Advanced models like **ClimateBERT** have been used to identify "cheap talk"—vague, non-committal disclosures—and "cherry-picking," where firms only report on positive climate-related risks while omitting material negative ones  . Technically, this is achieved by comparing a firm's disclosure patterns against industry-wide benchmarks or historical data to find significant deviations  .

### Aspect-Action Analysis and Semantic Inconsistency

A significant technical advancement in this field is **Aspect-Action Analysis**. This method goes beyond simple sentiment analysis by extracting specific "aspects" (e.g., carbon emissions reduction) and linking them to "actions" (e.g., "invested \$50M in carbon capture")  . Greenwashing is technically identified when there is a **semantic inconsistency** or a cross-category generalization—such as when a company makes broad environmental claims based on a single, minor action  . This requires models with high "cross-category generalization" capabilities to detect if a company's "green" claims in one sector are being used to offset "brown" activities in another  .

### Monitoring Systems and Empirical Testing

Newer systems, such as **DeepGreen**, utilize Large Language Models to create monitoring systems designed for empirical testing  . These systems are technically designed to:
1.

**Extract structured evidence** from unstructured reports to verify if specific ESG metrics (like Scope 1 or 2 emissions) are reported with sufficient detail  .

**Compare internal reporting with external news**, using LLMs to check for discrepancies between what a company says in its ESG report and what is reported in the media

**Score "Greenwashing Tendency"** by applying weighted metrics to the extracted data, identifying when a firm’s rhetoric significantly outpaces its data-backed performance  .

### Technical Limitations: The "Soft Language" Problem

A major hurdle remains the "soft" nature of ESG language. LLMs must be sensitive enough to distinguish between **substantive disclosures** and **boilerplate language** that satisfies regulatory checklists without providing material insight  . This provides the technical justification for **Section 3.4.4**, as standard machine learning baselines often fail to capture the subtle linguistic nuances that separate genuine commitment from strategic ambiguity

### Table: State-of-the-Art in NLP-Driven ESG and Greenwashing Analysis

Below is a comprehensive table of state-of-the-art research relevant to Chapter 2.1, focusing on the technical and NLP methodologies used to address greenwashing and ESG extraction. This synthesis highlights how current frameworks transition from simple keyword counting toward complex, intent-aware architectures that verify sustainability claims against verifiable operational evidence  . On top of that, there next table focus on the technical nuances of goal alignment, model sensitivity, and sector-specific extraction, complementing the previous literature by addressing the "soft language" and benchmarking challenges in ESG.

*Caption: caption*

{1.2}
{}{|p{1.8cm}|X|X|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Xu et al.**   & **DeepGreen System**: LLM-driven monitoring for empirical testing of greenwashing. & Corporate ESG reports and external news articles. & Text & Developed a monitoring system to cross-verify internal reports with external media for discrepancies. & Potential focus on regional reporting standards may limit global generalization.

**Bingler et al.**   & **ClimateBERT**: Transformer-based model fine-tuned on climate-related data. & Large-scale corporate climate risk disclosures. & Text & Identified "cheap talk" and "cherry-picking" in risk disclosures by detecting vague, non-committal language. & Primarily focused on climate/risk; may overlook social (S) and governance (G) specific greenwashing.

**Ong et al.**   & **Aspect-Action Analysis**: Cross-category generalization for robust ESG analysis. & ESG reports categorized by specific environmental actions. & Text & Links specific "aspects" to concrete "actions" to identify inconsistencies between rhetoric and investment. & Requires high-quality labeled data for different action categories to maintain accuracy.

**Wang et al.**   & **Thematic & Sentiment Analysis**: Predicting greenwashing degrees via linguistic features. & Corporate ESG reports. & Text (Sentiment/ Theme) & Quantified how high positive sentiment correlates with a lack of specific, data-backed environmental themes. & Purely linguistic focus may miss technical data discrepancies (e.g., mismatched emission numbers).

**Bronzini et al.**   & **LLM-Structured Extraction**: Deriving structured insights from sustainability reports. & Diverse set of corporate sustainability reports. & Text & Semi-structured & Demonstrated the superiority of LLMs in extracting structured data from unstructured narrative text. & High computational cost and "hallucination" risks in extracting specific numerical metrics.

**Beck et al.**   & **Benchmark Dataset**: GHG emission extraction and data gap analysis. & Global dataset of PDF reports for Greenhouse Gas monitoring. & Text & PDF Metadata & Created a specialized benchmark for extracting Scope 1, 2, and 3 emissions to address reporting data gaps. & Focus is narrow, not covering broader qualitative greenwashing narratives.

**Schimanski et al.**   & **Nature-Related Analysis**: Datasets and models for biodiversity and nature disclosures. & Nature-related corporate disclosures. & Text & Expanded the scope of NLP moving beyond simple climate metrics. & Nature-related reporting is still in its infancy, leading to sparse and inconsistent ground-truth data.

*Caption: caption*

{1.2}
{}{|p{1.8cm}|X|X|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Kılınç et al.**   & **Multi-dimensional Textual Framework**: Specifically designed for greenwashing detection. & Multi-sector corporate sustainability reports. & Textual narratives & Developed a framework that integrates linguistic indicators of deception with sustainability metrics. & Framework performance is highly dependent on the quality of the underlying sentiment and thematic lexicons.

**Schimanski et al.**   & **ClimateBERT-NetZero**: Specialized model for detecting and assessing Net Zero targets. & Corporate Net Zero pledge documents and reports. & Text (Targets/ Claims) & Created a pipeline to distinguish between "vague" commitments and "verifiable" reduction targets, essential for flagging target-based greenwashing. & Difficulty in handling "future-looking" statements that lack immediate material evidence.

**Maibaum et al.**   & **Tool Selection Framework**: Systematic classification of sustainability information. & Standardized corporate reporting datasets. & Text & Established a decision-matrix for choosing between classical NLP and Deep Learning based on data complexity. & Identifies that traditional tools often fail at capturing the semantic nuance required for complex ESG themes.

**Chung & Latifi**   & **ESG Domain-Specific Evaluation**: Benchmarking domain-specific LLMs against traditional ML. & ESG-specific text classification benchmarks. & Text & Demonstrated that domain-pretraining (e.g., ESG-BERT) significantly outperforms general models in identifying material ESG risks. & Domain-specific models can exhibit high sensitivity to the specific training corpus, leading to potential bias.

**Yu et al.**   & **climateBUG**: Data-driven framework for analyzing bank reporting through a climate lens. & Financial sector climate risk reports. & Text & Financial Data & Developed a sector-specific lens for climate reporting, highlighting the "transparency gap" in banking disclosures. & Sector-specific focus (banking) may not directly transfer to heavy-industry or retail ESG reporting.

**Hajikhani & Cole**   & **Sensitivity and Bias Review**: Critical analysis of LLMs in specialized AI domains. & General and specialized LLM outputs. & Textual outputs & Highlighted the risks of "hallucination" and bias when LLMs are used for specialized tasks like ESG auditing. & Focuses on the "path toward specialized AI" rather than providing a standalone extraction tool.

## Evolution of NLP in Sustainability Analysis

The methodology for analyzing corporate sustainability has undergone a significant transformation, evolving from simple keyword counting to sophisticated semantic understanding. This progression reflects the increasing complexity of ESG disclosures and the need for tools that can detect nuanced linguistic patterns like greenwashing.

### Dictionary-Based and Statistical Foundations

Early NLP applications in sustainability relied heavily on **dictionary-based techniques** and **lexicons**. These methods used predefined lists of "green" or "socially responsible" keywords to quantify the volume of ESG communication  . While foundational, research has shown that dictionaries exhibit a large variation in quality and fail to capture the context in which words are used  . For instance, a dictionary might flag the word "carbon" as a positive environmental indicator, even if the text discusses a "failure to reduce carbon emissions"  . Subsequent statistical methods, such as **Latent Dirichlet Allocation** for topic modeling, offered improved performance over dictionaries by identifying latent themes across reports, yet they remained limited by their inability to handle complex semantic relationships  .

### The Transformer Revolution and Contextual Embeddings

The introduction of the **Transformer architecture** and models like **BERT** marked a paradigm shift. Unlike previous word embedding techniques (e.g., Word2Vec) that assigned a single vector to a word regardless of context, Transformers use attention mechanisms to derive context-dependent meanings  . This capability is crucial for ESG analysis, where the same term can have vastly different implications depending on the surrounding text  . Studies demonstrate that fine-tuned Transformer models significantly outperform classical machine learning baselines in classifying material ESG risks and identifying sustainability trends in corporate earnings calls  .

### Domain-Specific Specialization: The Rise of ClimateBERT

As the limitations of general-purpose language models became apparent, the field shifted toward **domain-specific fine-tuning**. A prominent example is **ClimateBERT**, a model pretrained on millions of climate-related sentences from corporate reports and news  .
-

**Precision in "Cheap Talk" Detection:** ClimateBERT has proven highly effective at identifying "cheap talk"—vague, non-committal climate disclosures that satisfy regulatory requirements without committing to material action  .

**Enhanced Performance:** By training on domain-specific corpora, these models achieve much higher accuracy in detecting climate-related risks compared to general models like BERT-base  .This specialization has extended to specific sub-domains, with researchers developing distinct models for the "E," "S," and "G" components to capture the unique linguistic styles of each pillar  .

### Large Language Models and Generative Extraction

The current frontier in the evolution of ESG NLP is the adoption of **Large Language Models** such as GPT-4 and Llama. These models represent a move from simple text classification to **structured semantic extraction**  .
-

**One-Shot and Few-Shot Capabilities:** Recent evaluations show that LLMs, when paired with well-designed prompts, can surpass earlier fine-tuned models in extracting structured data from unstructured reports  .

**Multi-Dimensional Analysis:** LLMs enable more complex tasks, such as **Aspect-Action Analysis**, which links specific environmental aspects to concrete corporate actions to identify inconsistencies  .

**Expansion to Nature and Biodiversity:** New datasets and models are now emerging to tackle "nature-related" disclosures, moving beyond carbon-centric analysis to evaluate how companies report on biodiversity and ecosystem services  .

### Table: State-of-the-Art in the Evolution of NLP for Sustainability

The table below summarizes the key milestones in the technical evolution of NLP within sustainability analysis, tracking the shift from lexicon-based systems to domain-specific Transformers and eventually to generative Large Language Models, also the table introduced specialized frameworks and models that represent the transition from general climate classification to more granular, sector-specific, and target-oriented analysis

*Caption: caption*

{1.2}
{}{|p{1.8cm}|p{3.5cm}|p{3cm}|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Maibaum et al.**   & **Tool Selection Framework**: Comparing Dictionaries, BERT, and LLMs. & Standardized corporate reporting datasets. & Text & Established a decision-matrix showing that while dictionaries provide transparency, Transformers are required for semantic nuance. & Does not propose a new architecture, but rather a methodology for tool selection.

**Raman et al.**   & **Distant Supervision**: Neural Language Models for trend mapping. & Corporate earnings call transcripts and ESG news. & Text & One of the first applications of neural embeddings to map long-term ESG trends via distant supervision. & Reliance on weak labels (distant supervision) can introduce noise into trend analysis.

**Bingler et al.**   & **ClimateBERT**: Domain-specific pre-training. & 1.6M paragraphs of climate-related disclosures. & Text & Proven that general-purpose models fail to detect "cheap talk" and that domain-pretraining is essential for climate precision. & Narrow focus on climate-related text; less effective for social or governance specificities.

**Schimanski et al.**   & **BERT-Based Measurement**: Quantifying multi-dimensional ESG communication. & Large-scale sustainability reports across multiple industries. & Text & Bridged the gap between manual content analysis and automated measurement using contextual embeddings. & The model is a "black box" compared to dictionary methods, making it harder for auditors to interpret specific flags.

**Chung & Latifi**   & **Domain-Specific LLM Evaluation**: Benchmarking ESG-specific LLMs. & Specialized ESG text classification benchmarks. & Text & Quantified the performance leap when using models pre-trained specifically on financial and ESG corpora. & Primarily addresses classification tasks rather than complex structured data extraction.

**Bronzini et al.**   & **Generative Extraction**: Transition from classification to structured insights via LLMs. & 100+ high-complexity corporate sustainability reports. & Text & Semi-structured data & Demonstrated that LLMs (e.g., GPT-4) can derive structured tables and insights that previously required manual entry. & High computational cost and the inherent risk of numerical "hallucinations" in extracted data.

**Anaraki et al.**   & **Systematic Review**: Mapping the research agenda for LLMs in sustainability. & Literature corpus on LLM applications in ESG. & Meta-analysis & Provided a comprehensive taxonomy of how LLMs are currently being used to automate regulatory reporting (GRI/SASB). & As a review paper, it does not provide an empirical benchmark for specific extraction tasks.

{1.2}
{}{|p{1.8cm}|p{3.5cm}|p{3cm}|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Ong et al.**   & **Aspect-Action Analysis**: Cross-category generalization for robust analysis. & ESG reports with labeled environmental actions. & Text & Developed a technical logic to link broad environmental claims ("Aspects") to verifiable investments ("Actions") to detect narrative inconsistencies  . & High performance dependency on the availability of explicit action-oriented language in reports.

**Schimanski et al.**   & **Nature-Related NLP**: Domain-specific datasets/models for biodiversity. & TNFD-aligned corporate nature disclosures. & Text & Technically expanded the evolution of ESG NLP from carbon-centric to nature/biodiversity-centric  . & Biodiversity reporting is currently sparse, leading to "small data" challenges for model training.

**Billert & Conrad**   & **Nano-ESG Extraction**: Information extraction from external news. & Large corpus of corporate news articles. & Text & Shifted from "Internal-Only" to "External-Monitoring" by extracting ESG performance indicators from media to verify company claims  . & News data is significantly noisier than formal reports, requiring complex cleaning and deduplication pipelines.

**Schimanski et al.**   & **ClimateBERT-NetZero**: Specialized target assessment pipeline. & Net Zero pledge documents and corporate targets. & Text (Targets/ Claims) & Introduced a methodology to technically differentiate between "vague" pledges and "verifiable" science-based targets  . & Struggles to validate future-looking claims that lack current-year material evidence or milestones.

**Wang et al.**   & **Multi-Feature Prediction**: Sentiment and thematic feature integration. & Standard corporate ESG reports. & Text & Quantified the "Greenwashing Degree" by using the disparity between positive sentiment and specific thematic density as a technical predictor  . & Focused on linguistic features; may miss numerical discrepancies found in financial tables.

**Yu et al.**   & **climateBUG**: Sector-specific framework for financial institutions. & Bank-specific climate risk and TCFD reports. & Text & Metadata & Developed a data-driven framework specifically for the banking sector to identify "transparency gaps" in carbon-intensive lending  . & The banking-specific ontology lacks generalization to other sectors like heavy manufacturing or retail.

## Large Language Models for Structured ESG Extraction

The shift toward Large Language Models represents a fundamental technical pivot from **text classification**—where models simply categorize a paragraph as "Environmental"—to **structured information extraction**, where models extract specific, actionable data points into predefined schemas  .

### From Classification to Schema-Based Extraction

Traditional NLP models typically perform sequence classification, providing a high-level label for a text block. In contrast, LLMs enable the derivation of structured insights, such as transforming unstructured narrative text into JSON or tabular formats that include specific metrics like Scope 1 emissions, target years, and baseline comparisons  . This capability is critical for automating the assessment of sustainability reports, which are often composed of semi-structured data that varies significantly between companies  . Research by **Bronzini et al.** demonstrates that LLMs like GPT-4 can derive these structured tables with a level of precision that previously required manual auditing, though the risk of numerical "hallucinations" remains a technical hurdle  .

### Prompt Engineering and In-Context Learning

A key technical advantage of LLMs in the ESG domain is their ability to perform tasks via **In-Context Learning**, which includes zero-shot and few-shot prompting strategies  . This eliminates the need for the extensive, task-specific fine-tuning required by earlier models like BERT  .
-

**Zero-Shot Extraction:** LLMs can extract ESG data based solely on a natural language description of the schema (aligning with **Section 3.4.1 Schema Layer**)  .

**Few-Shot Prompting:** Providing a few expert-labeled examples (e.g., how to identify a "Science-Based Target") within the prompt significantly improves model performance on complex, "soft" language tasks  .

**Chain-of-Thought:** Encouraging the model to "reason" through an extraction—such as explaining *why* a specific sentence constitutes a carbon reduction action—helps mitigate errors in judgment and improves the interpretability of the results  .

### Aspect-Action Linkage and Semantic Mapping

For greenwashing detection, simple keyword matching is insufficient. LLMs excel at **Aspect-Action Analysis**, a technical logic where the model identifies an environmental "aspect" (e.g., water conservation) and attempts to link it to a verifiable "action" (e.g., \$10M investment in desalination plants)  . Technically, this involves complex semantic mapping where the LLM evaluates the strength of the connection between a claim and the evidence provided. If a model identifies a high frequency of "aspects" without corresponding "actions," it can flag the report for potential greenwashing based on narrative inconsistency  .

### Domain-Specific vs. General LLMs

While general LLMs like GPT-4 show high performance, the evolution of the field has led to **domain-specific pre-trained models** (e.g., ESG-BERT or specialized Llama variants). Studies comparing these models indicate that domain-specific pre-training on financial and corporate corpora allows the model to better understand the "jargon" of sustainability reporting, leading to higher accuracy in identifying material risks  . However, general-purpose LLMs often retain a lead in "reasoning" tasks and complex instruction following, which justifies the **Comparative Model Logic** found in **Section 3.4.5**  .

### Technical Risks: Hallucinations and Grounding

A critical limitation of LLMs in ESG extraction is their sensitivity to input phrasing and their tendency to generate plausible-sounding but factually incorrect data—commonly known as **hallucinations**  . In the context of sustainability, a hallucinated emission figure or target date could lead to incorrect regulatory filings. This technical risk necessitates the use of **External Validators** (like ClimateBERT, as seen in  **Section 3.4.3**) and **Human-in-the-Loop** workflows to verify the extracted "silver labels" before they are accepted as ground truth  .

*Caption: caption*

{1.2}
{}{|p{1.8cm}|p{3.5cm}|p{3.5cm}|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Bronzini et al.**   & **Structured Parsing**: Using LLMs to derive JSON/tabular insights from text. & 100+ high-complexity corporate sustainability reports. & Text & Semi-structured data & Demonstrated that LLMs can automate the conversion of qualitative narratives into structured ESG metrics. & High risk of numerical "hallucinations" and significant computational costs per report.

**Anaraki et al.**   & **Systematic LLM Review**: Mapping the technical landscape of LLM applications in ESG. & Comprehensive corpus of LLM-ESG literature. & Meta-analysis & Provided a taxonomy of LLM tasks in sustainability, including regulatory reporting and audit automation. & Does not provide a specific empirical benchmark or new architecture.

**Hajikhani & Cole**   & **Sensitivity Analysis**: Evaluating model bias and sensitivity in specialized AI. & Multi-domain LLM outputs (general and specialized). & Text & Highlighted the critical need for "Self-Refinement" and specialized prompts to mitigate bias in LLM outputs. & Focuses on the "path toward specialized AI" rather than a standalone ESG extraction tool.

**Chung & Latifi**   & **Benchmarking ESG-LLMs**: Comparing domain-specific LLMs against general models. & ESG-specific text classification and extraction benchmarks. & Text & Quantified the performance gap, showing that ESG-pre-trained LLMs significantly reduce false-positive greenwashing flags. & Domain-specific models can inherit biases from their specific training corpus.

**Xu et al.**   & **DeepGreen System**: LLM-driven monitoring for empirical greenwashing testing. & Corporate ESG reports and external news articles. & Text & Created a cross-verification pipeline using LLMs to check report validity against external evidence. & Regional data focus (e.g., China) may affect generalizability to global reporting standards.

**Ong et al.**   & **Aspect-Action Analysis**: Linking sustainability "Aspects" to concrete "Actions." & ESG reports with labeled environmental investments. & Text & Developed a semantic logic to detect greenwashing when claims are not backed by verifiable data. & Highly dependent on the presence of explicit, action-oriented language within the reports.

**Beck et al.**   & **GHG Benchmark**: Structured extraction of Greenhouse Gas emissions. & Global dataset of PDF sustainability reports. & Text & PDF Metadata & Established a technical benchmark for extracting precise Scope 1, 2, and 3 emission figures from unstructured text. & Focused exclusively on GHG metrics, omitting broader qualitative ESG themes.

*Caption: caption*

{1.2}
{}{|p{1.8cm}|p{3.5cm}|p{2.5cm}|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Schimanski et al.**   & **ClimateBERT-NetZero**: Targeted assessment of reduction pledges. & Corporate Net Zero commitment documents. & Text (Targets/ Pledges) & Developed a pipeline to extract and assess "Net Zero" targets, distinguishing between vague pledges and verifiable, science-based reduction goals  . & Often struggles to validate purely forward-looking statements that lack current-year material evidence.

**Bingler et al.**   & **Domain-Specific Risk Extraction**: Identifying "cherry-picking" in disclosures. & TCFD-aligned climate risk reports. & Text & Technically identified "cheap talk" by extracting non-committal language and comparing it against material climate risks  . & Narrowly focused on climate-related risks; less effective for social (S) or governance (G) extraction.

**Schimanski et al.**   & **Nature-Related Models**: Extracting biodiversity and ecosystem metrics. & TNFD-aligned corporate nature disclosures. & Text (Nature/ Biodiversity) & Expanded the extraction paradigm to nature-related disclosures, providing a framework for monitoring biodiversity impact  . & Nature-related reporting is still emerging, leading to sparse and inconsistent ground-truth data for model training.

**Billert & Conrad**   & **Nano-ESG Extraction**: Event-based extraction from news media. & Large-scale corpus of corporate news articles. & Text & Shifted from internal reports to "outside-in" monitoring by extracting ESG-relevant events from news to verify internal claims  . & News data is significantly noisier than formal reports, requiring complex deduplication and filtering.

**Yu et al.**   & **climateBUG Framework**: Sector-specific extraction for financial institutions. & Bank-specific climate risk and TCFD reports. & Text & Metadata & Developed a data-driven framework specifically for the banking sector to identify "transparency gaps" in carbon-intensive lending  . & The sector-specific ontology (banking) may not directly transfer to heavy-industry or manufacturing sectors.

**Kılınç et al.**   & **Multi-dimensional Framework**: Deception detection in textual reporting. & Diverse corporate sustainability reports. & Textual Narratives & technically linked linguistic "deception" cues (e.g., strategic ambiguity) to specific sustainability extraction categories  . & High performance dependency on the quality and breadth of the underlying sentiment and thematic lexicons.

**Wang et al.**   & **Sentiment-Thematic Integration**: Predicting greenwashing degree via feature disparity. & Standardized corporate ESG reports. & Text & Quantified how high positive sentiment correlates with a lack of specific, data-backed thematic actions, creating a predictive score for greenwashing  . & Focused primarily on linguistic features; may miss numerical discrepancies found in financial tables.

## Data Gaps and Benchmark Design

The creation of a robust methodology for sustainability analysis is fundamentally constrained by the quality and structure of available data. This section examines the technical "data gaps" identified in current literature and the evolving standards for benchmark design in the ESG domain.

### Identifying Technical Data Gaps in Sustainability

Despite the increasing volume of reports, significant gaps prevent automated systems from achieving high accuracy.
-

**Extraction and Parsing Failures:** A primary technical gap is the failure of automated pipelines to ingest complex, semi-structured PDF layouts  . Research by **Beck et al.** highlights that data gaps in sustainability reporting—particularly regarding greenhouse gas emissions—are often caused by the technical difficulty of extracting data from multi-column tables and non-standardized units within unstructured narratives  .

**The Scope 3 Reporting Gap:** While Scope 1 and 2 emissions are increasingly reported with consistency, Scope 3 reporting remains sparse and technically inconsistent across industries, making it the most difficult metric to benchmark accurately  .

**"Sentimental Masks" and Omissions:** Data gaps are not always accidental; they can be strategic. Literature identifies "cherry-picking" (reporting only positive metrics) as a practice that creates artificial gaps in a firm’s environmental risk profile  . This requires benchmarks that can identify not just what is present, but what has been omitted  .

### The Role of Benchmark Datasets in ESG NLP

A technical benchmark provides a standardized "ground truth" to evaluate model performance. The field is currently shifting from general classification datasets to **specialized extraction benchmarks**:
-

**Target-Specific Benchmarking:** Newer benchmarks, such as **ClimateBERT-NetZero**, are designed specifically to evaluate a model's ability to distinguish between vague corporate pledges and verifiable, science-based reduction targets  .

**Nature and Biodiversity:** As the focus expands beyond carbon, specialized datasets are emerging for nature-related disclosures, addressing the "small data" challenge where high-quality labeled examples of biodiversity impact are scarce  .

**News-Based External Validation:** Benchmarks like the **ESG-FTSE corpus** utilize external news articles to provide an "outside-in" perspective, allowing researchers to check for discrepancies between internal corporate reports and external media narratives  .

### Technical Requirements for Benchmark Design

According to recent studies, a defensible ESG benchmark must satisfy three core technical requirements:
1.

**Granular Unit of Analysis:** Benchmarks must transition from report-level summaries to **paragraph-level extractions** to capture the specific context of claims  .

**Gold Standard Ground Truth:** While "Silver Labels" (generated via weak supervision or LLMs) are useful for initial seeding, a high-fidelity benchmark requires an expert-led **Human Annotation Workflow** to verify the semantic nuances of sustainability language  .

**Cross-Category Generalization:** A robust benchmark should test a model's performance across diverse industry sectors (e.g., banking vs. heavy industry) and ESG categories to ensure the methodology is not overfitted to a single domain  .

### Table: State-of-the-Art in ESG Benchmark Design

For **Section 2.4: Data Gaps and Benchmark Design**, the following table identifies the most recent state-of-the-art benchmarks and datasets designed to address the "expert-scarcity" and "data-fragmentation" problems in sustainability reporting. These works provide the technical foundation for the **Benchmark and Ground Truth Design (Section 3.6)**, and also highlights additional state-of-the-art research focusing on the specific technical gaps identified in corporate reporting and the datasets developed to mitigate them. These works provide the scholarly justification to focus on **Coverage, Stratification, and Resumability (Section 3.6.4)**.

*Caption: State-of-the-art ESG benchmarks and dataset design patterns supporting the benchmark and ground-truth construction in Section 3.6.*

{1.2}
{}{|p{1.8cm}|X|X|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Beck et al.**  & **LLM-powered extraction with human review**: a multi-stage validation pipeline. & 139 sustainability reports from company websites. & Text & PDF metadata & Created a gold-standard dataset for GHG emissions to validate automated extraction. & Primarily focused on numerical emission metrics; lacks qualitative greenwashing narrative analysis.

**Sun et al.**  & **ESG-Bench**: QA-based benchmarking for long-context understanding. & Human-annotated QA pairs grounded in real-world reports. & Text & Developed a benchmark for hallucination mitigation in compliance-critical ESG settings. & Complex QA design may limit direct reuse for simpler extraction tasks.

**Maibaum et al.**  & **Validity and quality assessment**: comparison of four NLP techniques. & 75,000 manually labelled sentences from 10-K reports. & Text & Established large-scale ground truth showing that dictionaries fail to capture semantic context. & Focuses on 10-K filings, which differ from dedicated ESG or sustainability reports.

**George & Saji**  & **ESGBench**: explainable question-answering framework. & Domain-grounded questions across multiple ESG themes. & Text & evidence chains & Created a benchmark requiring supporting evidence for answers, improving traceability. & Does not specifically address deceptive or greenwashed evidence.

**Schimanski et al.**  & **Multi-domain pretraining**: specialised E, S, and G classifiers. & 13.8M text blocks; three specialised 2k datasets. & Text & Provided targeted datasets for training models that explain variation in ESG ratings. & Final classification datasets are small compared with the pretraining corpus.

**Schimanski et al.**  & **Target assessment pipeline**: differentiating pledge types. & Corporate net-zero and reduction-target documents. & Text (targets/ pledges) & Created a benchmark for distinguishing vague pledges from verifiable science-based goals. & Evaluation is restricted to climate targets, omitting social and governance commitments.

**Pavlova et al.**  & **ESG-FTSE Corpus**: news-based relevance labelling. & News articles and press releases indexed by the FTSE. & Text & Established a corpus for outside-in verification against public sentiment and media evidence. & News data is noisy and requires filtering before matching report-level claims.

**Schimanski et al.**  & **Nature-related discovery**: transitioning beyond carbon. & TNFD-aligned nature and biodiversity disclosures. & Text & Developed benchmark resources for nature-related disclosures and biodiversity reporting gaps. & Biodiversity reporting standards are still evolving, creating inconsistent ground-truth labels.

*Caption: caption*

{1.2}
{}{|p{1.8cm}|X|X|p{1.8cm}|X|X|}

Authors & Method / Approach & Datasets & Modalities Involved & Key Contributions & Limitations

**Bingler et al.**   & **Cherry-Picking Analysis**: Identifying selective reporting in climate disclosures. & 1.6M paragraphs from TCFD-aligned reports. & Text & Technically mapped the gap between "climate-relevant" and "climate-material" disclosures, proving that companies selectively report positive news  . & Does not provide a mechanism for automated cross-source validation against external physical risk data.

**Yu et al.**   & **climateBUG Framework**: Sector-specific transparency gap analysis. & Bank-specific climate and TCFD reports. & Text & Financial Data & Identified the "transparency gap" in the financial sector, providing a dataset specifically for carbon-intensive lending disclosures  . & The benchmark is highly tailored to the banking ontology and may not apply to non-financial corporations.

**Kılınç et al.**   & **Deception-Oriented Dataset**: Focused on linguistic indicators of greenwashing. & Multi-sector corporate sustainability reports. & Textual Narratives & Established a dataset to test for "strategic ambiguity" and "vagueness," which are often omitted from standard NLP benchmarks  . & Performance is limited by the subjective nature of what constitutes "ambiguity" in different regulatory jurisdictions.

**Billert & Conrad**   & **Nano-ESG Corpus**: External event-based extraction. & News articles covering corporate environmental/social events. & Text & Addressed the "internal-only" data gap by creating a corpus that allows models to verify report claims against public events  . & Challenges arise in temporal alignment—matching a news event date to the specific reporting cycle of a firm.

**Wang et al.**   & **Sentiment-Thematic Disparity**: Predicting greenwashing degree. & Diverse corporate ESG reports. & Text & Technically quantified the gap between high-sentiment "marketing" language and low-density "action" themes  . & The model predicts a "degree" of greenwashing but cannot pinpoint specific false statements for auditing purposes.

**Ong et al.**   & **Aspect-Action Generalization**: Cross-category robustness testing. & ESG reports with labeled aspects and actions. & Text & Developed a benchmark to test how well models generalize "action-detection" across different ESG pillars (E vs. S vs. G)  . & Requires highly complex, multi-layered annotations which are difficult to scale for large datasets.
