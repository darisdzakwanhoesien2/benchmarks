https://app.jenni.ai/editor/0qbGy9xgvDBJXIGKpKbX
Topic Modelling in ESG Sustainable Report, News and Social Media Sources


Topic Modelling

This section utilizes Latent Dirichlet Allocation to identify thematic clusters within sustainability disclosures, providing a latent semantic perspective on reporting trends over time (Hoesien, 2026, p. 22; Mohamed & Oussalah, 2019, p. 1372). Furthermore, the optimal number of topics is determined by evaluating coherence scores and K-values, ensuring the resulting thematic taxonomy accurately reflects the strategic priorities of the disclosing companies (Park et al., 2025, p. 12). 

Based on the development of your Topic Modelling Track (topic_modelling/app.py), which focuses on adapting frameworks from other domains into the ESG reporting landscape using keyword heuristics, here is the defined thesis structure for Daris Dzakwan.

Chapter 1: Introduction

1.1. Motivation

The heterogeneous nature of ESG reports, which combine dense technical data with high-level corporate narratives, makes it difficult to extract consistent thematic signals across different industries (Bronzini et al., 2024). Traditional topic modelling techniques often fail to capture the specific regulatory and ethical nuances inherent in sustainability disclosures, leading to "thematic noise" (Yan et al., 2025). There is a critical need to investigate how topic-modelling frameworks—originally developed for general text corpora—can be adapted and refined using domain-specific keyword heuristics to estimate ESG pillar signals with higher precision (Birti et al., 2025; Mehra et al., 2022).

1.2. Research Questions and Goals





RQ1: How can domain-specific keyword heuristics be used to improve the detection of ESG pillar signals in an unstructured corpus?



RQ2: To what extent is a topic-modelling framework adapted from another domain feasible for identifying cross-category ESG trends? (Ong et al., 2025)



Goal: To develop a task-framework dashboard that scans the data/thesis_dataset/ and provides categorical summaries of ESG themes.

1.3. Objectives and Contributions





Framework Adaptation: Implementing a task-based framework (task_data.py) that maps general topic-modelling logic to ESG-specific pillars.



Interactive Corpus Scanning: Developing a Streamlit-based explorer (topic_modelling/app.py) for dataset-wide corpus analysis and pillar signal estimation.



Heuristic Mapping: Establishing a utility-driven approach using keyword heuristics to categorize corpus properties without the need for exhaustive manual labeling (Birti et al., 2025).

1.4. Thesis Structure

Outlines the progression from corpus-wide signal detection to the adaptation of task-specific UI components for thematic research.



Chapter 2: Related Works

This chapter explores the intersection of unsupervised learning and corporate sustainability. Research indicates that while "glittery" corporate language can obscure specific actions, aspect-based topic models and keyword-informed heuristics can uncover the "gold" of genuine ESG disclosures (Bronzini et al., 2024; Ong et al., 2025).

State-of-the-Art Table: ESG Topic Modelling & Pillar Analysis







Framework/Model



Method



Pillar Focus



Key Performance/Insight



Source





A3CG Framework



Aspect-Action Analysis



E, S, G



Cross-category generalization improves theme robustness.



(Ong et al., 2025a, 2025b)





ESG-BERT



Domain Adaptation



Environment, Social



Optimized for specific ESG classification tasks vs. general BERT.



(Mehra et al., 2022)





EulerESG



SASB Alignment



Governance, Social



Uses standardized keywords to map reports to industry metrics.



(Ding et al., 2025)





Pharos-ESG



Hierarchical Labeling



Multimodal



Better theme alignment through layout-aware document parsing.



(Yan et al., 2025)





Nature-Disclosure



BERT-based



Nature/Environment



Identifies niche "nature-related" topics often missed by general models.



(Schimanski et al., 2024)





ESG Activity Detection



Taxonomic Mapping



EU ESG Taxonomy



Keyword-logic optimized for identifying specific "green" activities.



(Birti et al., 2025)



Chapter 3: Methodology

3.1. Overview of the Methodology

We propose a "Task-Framework" approach that adapts traditional LDA or BERTopic-like logic into the ESG domain. The methodology uses keyword heuristics to provide "soft labels" for the data/thesis_dataset/, allowing for an unsupervised estimation of pillar-specific signals (Birti et al., 2025; Mehra et al., 2022).

3.2. Data Sources

3.2.1. Dataset Characteristics

The primary source is the data/thesis_dataset/, a multi-industry corpus of corporate reports. It is supplemented by phase definitions found in topic_modelling/task_data.py.

3.2.2. Rationale

Utilizing a dataset-wide corpus scan is necessary to identify emerging sustainability trends that may not be captured by static regulatory checklists (Schimanski et al., 2024).

3.2.3. Data Accessibility and Ethical Considerations

Ensures the framework is adaptable to various disclosure systems, addressing the challenge of "framework proliferation" in global ESG reporting (Ding et al., 2025).

3.3. Preprocessing & Corpus Pipeline





Corpus Scan Heuristics: Utilizing keyword lists derived from SASB and GRI standards to estimate pillar signals (e.g., "emissions" for Environmental, "labor" for Social) (Ding et al., 2025; Mehra et al., 2022).



Run-Phase Definitions: Categorizing topics through sequential phases (defined in task_data.py) to observe thematic shifts.



Task-Rendering Logic: Using ui.py to provide a shared interface for visualizing categorical summaries and corpus properties.



Chapter 4: EXPERIMENTS

4.1. Implementation Details

The experimental prototype is implemented in topic_modelling/app.py. It provides a dashboard for scanning the corpus and visualizing keyword-pillar correlations.

4.2. Evaluation Metrics





Pillar Signal Strength: Measuring the density of keyword-informed signals across the dataset.



Thematic Coherence: Qualitative and quantitative assessment of how well the "adapted" framework clusters similar corporate actions (Ong et al., 2025).



Framework Robustness: Evaluating the consistency of topic assignments across different reporting sectors (e.g., energy vs. finance) (Ong et al., 2025).

4.3. Experimental Results

4.3.1. Comparison with State-Of-The-Art

Performance comparison of the heuristic-based approach against dedicated ESG classification models like ESG-BERT and the A3CG framework (Mehra et al., 2022; Ong et al., 2025).

4.3.2. Ground Truth Generation

Discussion on using taxonomies (such as the EU ESG Taxonomy) as the "gold standard" for validating keyword heuristics (Birti et al., 2025).

4.3.3. Ablation Studies

Evaluating the impact of different keyword sets on pillar estimation accuracy—specifically comparing general sustainability keywords vs. industry-specific technical terms (Schimanski et al., 2024).



5. DISCUSSION

This section addresses the feasibility of adapting out-of-domain frameworks. It discusses whether keyword heuristics are sufficient to overcome "greenwashing" noise or if deeper semantic logic (like Aspect-Action analysis) is required for high-stakes auditing (Bronzini et al., 2024; Ong et al., 2025).



6. CONCLUSION

The topic-modelling track demonstrates that an adapted task-based framework can effectively map unstructured ESG corpora to meaningful pillars. By leveraging keyword heuristics, the system provides a scalable first-pass audit for stakeholders navigating complex sustainability landscapes (Birti et al., 2025; Ding et al., 2025).



7. REFERENCES

(Citations include (Bronzini et al., 2024), (Ong et al., 2025), (Ong et al., 2025), (Mehra et al., 2022), (Ding et al., 2025), (Yan et al., 2025), (Schimanski et al., 2024), (Birti et al., 2025))- (Ong et al., 2025, p. 22) ESGSenticNet: A Neurosymbolic Knowledge Base for Corporate Sustainability Analysis.
