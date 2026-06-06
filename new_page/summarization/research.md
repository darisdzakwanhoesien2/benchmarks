https://app.jenni.ai/editor/H4tDFHjObi69hudoF2S6
Multimodal Summarization in ESG Sustainable Report, News and Social Media Sources

Summarization

Based on your development of the Summarization Track (summarization/app.py), which emphasizes lightweight algorithmic baselines for processing ESG outputs, here is the defined thesis structure for Daris Dzakwan.

Chapter 1: Introduction

1.1. Motivation

The volume of ESG-related documentation is expanding at an unmanageable rate, often exceeding the processing capacity of human analysts (Parikh & Penfield, 2024). While Large Language Models offer advanced summarization, they are computationally intensive and prone to "hallucinations" that can compromise the factual integrity required for financial auditing (Raman et al., 2025; Shamshad, 2026). There is a significant research opportunity to evaluate whether "lightweight" extractive methods—such as TextRank and frequency-based algorithms—can provide a reliable, cost-effective baseline for summarizing corporate sustainability claims without external model dependencies (Moro et al., 2023; Raman et al., 2025).

1.2. Research Questions and Goals





RQ1: How do traditional graph-based and frequency-based extractive summarization techniques perform compared to neural models in the specific context of ESG disclosures? (Raman et al., 2025)



RQ2: Can existing outputs from prior tracks (e.g., esg_records.json or revision analysis) serve as high-quality inputs for standalone summarization tasks?



Goal: To develop a research dashboard for evaluating the feasibility of unsupervised summarization utilities in a resource-constrained sustainability context.

1.3. Objectives and Contributions





Dashboard Implementation: Creation of a standalone Streamlit dashboard (summarization/app.py) for visualizing and benchmarking various summarization strategies.



Algorithmic Baselines: Development of "zero-shot" utilities—including Lead-3, Frequency-based, and TextRank-like algorithms—that require no training data (Basu et al., 2025; Raman et al., 2025).



Evaluation Framework: Implementing a ROUGE-style scoring system to measure the lexical overlap between generated summaries and reference sustainability content (He et al., 2021; Wu et al., 2024).

1.4. Thesis Structure

Outlines the transition from complex LLM-led analysis to efficient, explainable summarization baselines for ESG report auditing.



Chapter 2: Related Works

This chapter explores the divide between extractive and abstractive summarization. While neural models like BART and Pegasus offer fluency, extractive methods preserve the exact wording of corporate disclosures, which is often preferred for factual accountability in ESG reporting (Dharrao et al., 2024; Shamshad, 2026).

State-of-the-Art Table: ESG & Extractive Summarization







Algorithm/Model



Type



Context



Key Metric/Finding



Source





SusGen-GPT



Abstractive



Sustainability Reports



Uses ROUGE and BERTScore to ensure expert-level similarity.



(Wu et al., 2024)





Entity-Boosted TextRank



Extractive



News/Business



Achieved 2x the n-gram overlap of BART-based models in some splits.



(Raman et al., 2025)





Carburacy



Neural/Tuned



Eco-Sustainable Regime



Balances summarization accuracy with carbon-aware compute costs.



(Moro et al., 2023)





TextRank



Graph-based



Covid-19 CSR Reports



Uses cosine similarity matrices to identify central "themes" in text.



(Basu et al., 2025)





Hybrid TF-IDF/TextRank



Extractive



Technical Docs



Overcomes "contextual blindness" through dual-format outputs.



(Shamshad, 2026)





CTRL-sum



Abstractive



News Summarization



High fluency but requires significant GPU resources and fine-tuning.



(Raman et al., 2025)





EXABSUM



Hybrid



General MDS



Uses re-ranking and keyphrase extraction to improve informativeness.



(Merrouni et al., 2023)



Chapter 3: Methodology

3.1. Overview of the Methodology

We implement a "model-independent" summarization framework designed for high-stakes auditing. The methodology focuses on extractive techniques that rank sentences based on their structural and lexical centrality within the ESG document (Basu et al., 2025; Mohamed & Oussalah, 2019).

3.2. Data Sources

3.2.1. Dataset Characteristics

The dashboard utilizes summarization/data/data_sources.json to configure input paths. These sources include structured records from previous tracks, such as extracted ESG indicators and revision analysis results (Ding et al., 2025).

3.2.2. Rationale

Summarizing the outputs of specialized ESG analysis (rather than raw reports) allows the dashboard to focus on the most "information-dense" segments of the disclosure, reducing noise (Bronzini et al., 2024).

3.2.3. Data Accessibility and Ethical Considerations

Focuses on "privacy-preserving" client-side execution, ensuring that sensitive corporate data does not need to be transmitted to external APIs for processing (Shamshad, 2026).

3.3. Preprocessing & Algorithm Pipeline





Lead-N Baseline: Selecting the first n sentences as a baseline, a common standard for news-style reporting (Dharrao et al., 2024).



Frequency-based Scoring: Weighting sentences by the frequency of key sustainability terms (e.g., "emissions," "carbon," "diversity").



TextRank Utility: Building a graph where vertices are sentences and edges represent cosine similarity, then applying a PageRank-derived algorithm to rank them (Basu et al., 2025; Shamshad, 2026).



Chapter 4: EXPERIMENTS

4.1. Implementation Details

The standalone dashboard is built using Streamlit. It leverages a custom ROUGE utility to compute scores locally, providing immediate feedback on summarization quality across different datasets.

4.2. Evaluation Metrics





ROUGE-N: Measuring n-gram recall (ROUGE-1 and ROUGE-2) between generated summaries and human-written references (He et al., 2021; Ma et al., 2022).



ROUGE-L: Evaluating the longest common subsequence to capture structural similarity (Dharrao et al., 2024; He et al., 2021).



Efficiency Metrics: Tracking compute time and memory footprint to highlight the benefits of unsupervised methods over neural sequences (Raman et al., 2025).

4.3. Experimental Results

4.3.1. Comparison with State-Of-The-Art

Performance of the "zero-shot" TextRank utility is benchmarked against established neural baselines like T5 and Pegasus, emphasizing the trade-off between fluency and cost (Dharrao et al., 2024; Raman et al., 2025).

4.3.2. Ground Truth Generation

Discussion on using expert-written ESG executive summaries as the "gold standard" for calculating ROUGE scores (Wu et al., 2024).

4.3.3. Ablation Studies

Evaluating how the exclusion of specific preprocessing steps (e.g., stopword removal or entity boosting) affects the ROUGE performance in single-document vs. multi-document contexts (Dharrao et al., 2024; Raman et al., 2025).



5. DISCUSSION

This section explores whether "factual integrity" in ESG is better served by extractive baselines that avoid the hallucination risks of abstractive LLMs (Raman et al., 2025; Shamshad, 2026). We also discuss the scalability of using simple algorithmic utilities for large-scale longitudinal report analysis (Parikh & Penfield, 2024).



6. CONCLUSION

The summarization track demonstrates that lightweight, unsupervised methods are viable and efficient for sustainability auditing. By grounding summaries in verified records and using ROUGE-based evaluation, the system provides a robust tool for navigating information-dense ESG landscapes without high computational costs (Moro et al., 2023; Raman et al., 2025).



7. REFERENCES

(Citations include (Wu et al., 2024), (Raman et al., 2025), (Shamshad, 2026), (Moro et al., 2023), (Basu et al., 2025), (Dharrao et al., 2024), (He et al., 2021), (Ma et al., 2022), (Merrouni et al., 2023), (Parikh & Penfield, 2024), (Ding et al., 2025), (Bronzini et al., 2024), (Mohamed & Oussalah, 2019))
