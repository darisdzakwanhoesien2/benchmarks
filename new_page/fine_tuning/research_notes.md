
Fine-tuning



Based on your development of the Fine-tuning Track, which utilizes logic from domain-specific models like ClimateBERT, here is the defined thesis structure for this research area, Daris Dzakwan.

Chapter 1: Introduction

1.1. Motivation

General-purpose language models often struggle with the specialized lexicon of sustainability reporting, where terms like "nature" can have varying meanings depending on the financial or environmental context (Schimanski et al., 2024). While standard BERT and FinBERT provide a foundation, they frequently underperform on niche tasks such as climate-related financial risk detection (Garrido‐Merchán et al., 2023). Consequently, there is a growing need to investigate the feasibility of domain-specific fine-tuning—leveraging models like ClimateBERT that have been pre-trained on millions of climate-related paragraphs—to enhance the accuracy of ESG disclosures (He et al., 2025; Yu et al., 2023).

1.2. Research Questions and Goals





RQ1: How does the performance of domain-adapted models (e.g., ClimateBERT) compare to general-purpose LLMs in classifying complex ESG and climate-risk disclosures?



RQ2: Is it feasible to deploy a fine-tuning pipeline for small-to-medium datasets to achieve professional-grade classification metrics?



Goal: To establish a utility-driven framework for normalizing ESG data and evaluating the feasibility of fine-tuned domain models for sustainability tasks.

1.3. Objectives and Contributions





Pipeline Normalization: Development of call_climatebert_logic.py to standardize the input/output logic for climate-specific transformer models.



Feasibility Assessment: Implementation of a research-plan application (fine_tuning/app.py) to visualize the impact of fine-tuning on classification accuracy.



Domain Adaptation: Demonstrating that transfer learning on specialized corpora (like ClimaText) significantly improves F1 scores over baseline models (Garrido‐Merchán et al., 2023; Vivek et al., 2024).

1.4. Thesis Structure

Outlines the methodology for adapting transformer-based architectures to the ESG domain, followed by comparative experimental analysis.



Chapter 2: Related Works

This chapter reviews the evolution of transformer models in the corporate sustainability field. Research indicates that while generative LLMs excel at dialogue, BERT-like models remain superior for complex understanding tasks such as topic extraction and impact classification (Ong et al., 2024).

State-of-the-Art Table: ESG & Climate Fine-tuning







Model/Framework



Base Architecture



Domain Focus



Key Finding/Metric



Source





ClimateBERT



DistilRoBERTa



Climate Risk



Pre-trained on 1.6M climate paragraphs; outperforms BERT in risk detection.



(Garrido‐Merchán et al., 2023; He et al., 2025)





ESG-BERT



BERT



General ESG



Achieved higher accuracy than original BERT for environment-specific tasks.



(Mehra et al., 2022)





climateBUG-LM



BERT-family



Bank Reporting



Best performance achieved through temporal validation and domain adaptation.



(Yu et al., 2023)





EnvLlama 2



Llama 2



ESG Classification



12.3% F1-score improvement over FinBERT-ESG via fine-tuning.



(Chung & Latifi, 2024)





SDG Prospector



LLM-based



SDG Alignment



Leveraged LLMs to identify specific Sustainable Development Goal paragraphs.



(Bronzini et al., 2024)





ClimaText Model



ClimateBERT



Financial Reports



Outperforms state-of-the-art transformers on the ClimaText database.



(Vivek et al., 2024)



Chapter 3: Methodology

3.1. Overview of the Methodology

We propose a fine-tuning feasibility framework that tests the adaptation of pre-trained climate models to specific reporting datasets. The approach focuses on "transfer learning," where a model like ClimateBERT—already optimized for contextual word relationships in climate text—is further refined for specific corporate disclosures (Garrido‐Merchán et al., 2023; Vivek et al., 2024).

3.2. Data Sources

3.2.1. Dataset Characteristics

The methodology utilizes evidence sources documented in fine_tuning/README.md, including industry-specific report statements and climate-related corpora similar to the ClimaText database (Garrido‐Merchán et al., 2023).

3.2.2. Rationale

Fine-tuning on domain-specific corpora is essential because general models lack the "domain relevance" needed to accurately predict future ESG events based on past reporting data (Yu et al., 2023).

3.2.3. Data Accessibility and Ethical Considerations

Data collection focuses on 10-K filings, Wikipedia, and web-based climate claims to ensure a diverse and transparent training set (Vivek et al., 2024).

3.3. Preprocessing & Logic Pipeline





Normalization Logic: Utilizing fine_tuning/call_climatebert_logic.py to normalize report text, ensuring compatibility with the DistilRoBERTa architecture.



BERT-like Encoding: Implementing deep learning-based attention architectures to exploit semantic understanding of text embeddings (Ong et al., 2024).



Task Normalization: Mapping raw text to classification labels for (T1) topic extraction and (T2) impact classification (Ong et al., 2024).



Chapter 4: EXPERIMENTS

4.1. Implementation Details

The experimental environment is hosted on a Streamlit-based research-plan app (fine_tuning/app.py). It facilitates the comparative testing of normalized logic across different model backbones.

4.2. Evaluation Metrics





Standard NLP Metrics: Accuracy, Precision, Recall, and F1-score (Chung & Latifi, 2024).



Domain Gain: Measuring the percentage improvement (e.g., the 7.37% gain noted in Qlora studies) over classical machine learning models (Chung & Latifi, 2024).



Training Efficiency: Assessing the feasibility of training on limited-resource environments (Yu et al., 2023).

4.3. Experimental Results

4.3.1. Comparison with State-Of-The-Art

Performance comparison of the fine-tuned pipeline against baselines such as standard BERT, FinBERT-ESG, and zero-shot generative LLMs (Chung & Latifi, 2024; Yu et al., 2023).

4.3.2. Ground Truth Generation

Discussion of the "gold standard" dataset creation, involving independent assessment by annotators to ensure high data quality for large-scale extraction (Beck et al., 2025).

4.3.3. Ablation Studies

Evaluation of the "domain adaptation" effect—comparing the performance of the model with and without the domain-specific logic implemented in call_climatebert_logic.py.



5. DISCUSSION

This section explores the limitations of general-purpose LLMs in reasoning tasks and the necessity of domain-specific pre-training (like the 1.6M paragraph corpus used for ClimateBERT) for high-stakes financial auditing (He et al., 2025; Ong et al., 2024).



6. CONCLUSION

The fine-tuning track demonstrates that specialized transformer-based models are critical for reliable ESG classification. By integrating normalized domain logic, stakeholders can achieve significant performance gains over generic machine learning techniques (Chung & Latifi, 2024; Garrido‐Merchán et al., 2023).



7. REFERENCES

(Citations include (He et al., 2025), (Beck et al., 2025), (Ong et al., 2024), (Bronzini et al., 2024), (Chung & Latifi, 2024), (Garrido‐Merchán et al., 2023), (Garrido‐Merchán et al., 2023), (Mehra et al., 2022), (Yu et al., 2023), (Schimanski et al., 2024), (Vivek et al., 2024))

