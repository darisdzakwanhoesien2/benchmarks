# Chapter 1 Introduction

## 1.1 Motivation

Environmental, Social, and Governance disclosure has transitioned from a niche voluntary practice to a critical requirement for investors, regulators, and researchers seeking to evaluate corporate sustainability performance  [@hans_bonde_christensen_45b44695]. However, the current landscape of sustainability reporting is characterized by extreme heterogeneity. Reports vary significantly in format and extent due to a lack of global standardization, often blending concrete performance data with vague, forward-looking narratives  [@habiba_al_shaer_c2f5394b].

In the Indonesian context, these challenges are further compounded. Listed companies often produce bilingual reports with varying degrees of transparency, and empirical evidence suggests that the readability of Indonesian sustainability reports remains low  [@desi_adhariani_543335d6]. This lack of clarity often obscures specific sustainability issues, creating a gap between disclosed intentions and actual corporate conduct  [@marsdenia_010e13e7].

Traditional document-level analysis—which assigns a single score or sentiment to an entire report—is increasingly viewed as insufficient. ESG content is inherently multifaceted; a single page might contain an environmental commitment, a social program update, and a generic governance compliance statement  [@keane_ong_0a5de439]. This complexity allows for "greenwashing," where companies use "soft language" to mask a lack of measurable outcomes  [@keane_ong_8fec4760]. To address this, this research argues that ESG disclosures must be treated as a record-level **Aspect-Based Sentiment Analysis** problem. By treating every individual statement as a discrete record classified by aspect, pillar, sentiment, and provenance, we can transform raw PDF corpora into aligned, inspectable, and evaluable computational artifacts.

## 1.2 Problem Statement

The central research problem is the absence of a reproducible and validated pipeline for transforming heterogeneous sustainability-report PDFs into structured, record-level evidence. Current manual review processes are unscalable, while standard automated tools often fail to capture the semantic nuance required for ESG analysis.

This research addresses six critical technical challenges:

1. **Extraction Provenance:** Maintaining a clear link between extracted text and its original page/document location in heterogeneous PDFs.
1. **Prompt Configuration:** Designing Large Language Model prompts that can reliably extract multi-faceted ESG statements across different providers.
1. **Granular Labeling:** Assigning precise aspect, pillar, and tone labels at the record level rather than the document level.
1. **Construct Validity:** Identifying the divergence between general sentiment/tone and domain-specific climate labels (e.g., ClimateBERT).
1. **Quality Auditing:** Systematically identifying failures in OCR, schema drift, and missing data fields.
1. **Evidence Visualization:** Converting large-scale extraction results into interactive dashboards and semantic graphs for research verification.

## 1.3 Research Questions

The study is guided by the following research questions:

- **RQ1. ESG ABSA Schema:** How can ESG disclosures be effectively represented using a record-level schema that integrates aspect, ESG pillar, sentiment, and tone?
- **RQ2. Tone vs. Climate-Specific Models:** How do LLM-generated tone labels compare with specialized outputs from models like ClimateBERT, and what does this reveal about the validity of automated ESG assessments?
- **RQ3. Pipeline Diagnostics:** What specific failure modes, such as OCR-related data loss or ontology gaps, characterize the automated extraction of ESG records?
- **RQ4. Stability and Reproducibility:** To what extent do ESG extraction outputs remain stable across varying prompts, LLM models, and service providers?

## 1.4 Objectives and Contributions

### 1.4.1 Research Objectives:

1. **To Build a Reproducible OCR-to-ESG Extraction Pipeline:** Develop a system that converts raw PDF reports into usable text while preserving page-level provenance for auditability.
1. **To Design a Record-Level ESG ABSA Schema:** Establish a technical framework for classifying extracted statements based on granular ESG pillars and sentiment dimensions.
1. **To Evaluate Model Divergence:** Conduct a comparative analysis between general LLM tone labels and specialized ClimateBERT climate labels to assess construct validity.
1. **To Create a Diagnostic Framework:** Implement automated audits for parsing failures, schema drift, and missing labels within the extraction pipeline.
1. **To Develop a Semantic Evidence Layer:** Map extracted aspects to a formal ESG ontology and provide interactive dashboards for real-time data exploration and evidence verification.

### 1.4.2 Expected Contributions:

- **Technical Framework:** An executable, modular pipeline for automated ESG record extraction from sustainability reports.
- **Annotation Schema:** A bilingual, record-level ESG schema tailored for the Indonesian reporting context.
- **Evidence Layer:** A linked data structure connecting raw reports to LLM metadata, human annotations, and validation tables.
- **Methodological Insights:** A comprehensive stability analysis of LLM prompts and a critical discussion on why general sentiment and climate-specific commitment labels are non-interchangeable.

## 1.5 Thesis Structure

- **Chapter 1:** Outlines the motivation, problem statement, and technical objectives of the study.
- **Chapter 2:** Examines the evolution of NLP in sustainability, the challenge of greenwashing, and the current state-of-the-art in LLM-based extraction.
- **Chapter 3:** Details the OCR-to-ABSA pipeline, including prompt engineering strategies and the validation framework using ClimateBERT and human annotation.
- **Chapter 4:** Presents implementation details, evaluation metrics, and ablation studies regarding model stability.
- **Chapter 5:** Evaluates the ESG ABSA schema, analyzes failure modes, and discusses the implications of model divergence for future ESG research.
- **Chapter 6:** Summarizes the findings and suggests future directions for automated sustainability analysis.
