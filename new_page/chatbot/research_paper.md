https://app.jenni.ai/editor/Yu0IdLXboyf19BGgBXnr
Chatbot


Based on your development of the Chatbot Track (chatbot/app.py) and the focus on Aspect-Based Sentiment Analysis, here is the refined thesis structure for this research area, Daris Dzakwan.

Chapter 1: Introduction

1.1. Motivation

The complexity of ESG reporting often obscures objective performance behind "greenwashed" rhetoric, making it difficult for stakeholders to extract actionable insights (Ong et al., 2025). While traditional NLP tools can extract broad sentiments, there is a critical need for Aspect-Based Sentiment Analysis that links specific sustainability aspects to concrete corporate actions (Ong et al., 2025). Interactive chatbots provide a feasible medium for non-expert stakeholders to navigate these dense reports and explore longitudinal evidence through a conversational interface (Mishra et al., 2024; Tran et al., 2025).

1.2. Research Questions and Goals





RQ1: How can a grounded chatbot framework improve the transparency of ESG aspect-action analysis for stakeholders?



RQ2: To what extent does grounding a conversational agent in "Revision Analysis" datasets mitigate the risk of hallucinatory or misleading ESG claims?



Goal: To evaluate the feasibility of a chatbot layer that turns structured ABSA evidence and revision history into an interactive research plan.

1.3. Objectives and Contributions





System Development: Implementation of a Streamlit-based grounded research assistant (chatbot/app.py) capable of parsing documentation_chatbot.md.



Evidence Grounding: Integrating a RAG pipeline that utilizes results/revision_analysis/ to provide factual, version-controlled evidence for chatbot responses.



Methodological Framework: Proposing a hierarchical multi-agent or RAG-based approach for high-stakes ESG auditing (Bronzini et al., 2024; Zhao et al., 2026).

1.4. Thesis Structure

Outlines the progression from feasibility study and ABSA dataset analysis to the deployment of the grounded chatbot interface.



Chapter 2: Related Works

This chapter explores the intersection of Large Language Models, Retrieval-Augmented Generation, and ESG sentiment analysis. Current research emphasizes "Aspect-Action Analysis" to ensure that ESG insights are grounded in verifiable corporate behaviors rather than vague rhetoric (Ong et al., 2025a, 2025b).

State-of-the-Art Table: ESG Chatbots & ABSA







System/Model



Method



Primary Focus



Key Performance/Insight



Source





A3CG Framework



Aspect-Action Analysis



Anti-Greenwashing



Improves robustness by linking aspects to verifiable actions.



(Ong et al., 2025)





Deep Search DocQA



RAG + Computer Vision



ESG QA Assistant



Explores 10,000+ reports; focuses on "eloquent" response generation.



(Mishra et al., 2024)





ESGAgent



Multi-Agent RAG



Professional Auditing



84.15% accuracy on atomic QA; outperforms closed-source LLMs.



(Zhao et al., 2026)





EulerESG



Dual-channel Retrieval



SASB Framework Alignment



Achieved up to 0.95 average accuracy in standard-aligned extraction.



(Ding et al., 2025)





Client Adviser Framework



NLU Talking Points



Sustainable Investing



Achieved F1-score > 0.8 in identifying relevant talking points.



(Yi et al., 2025)





RAG-based ESG-QA



LLM + RAG



Management Support



Specifically addresses data standardization for SMEs.



(Tran et al., 2025)



Chapter 3: Methodology

3.1. Overview of the Methodology

The methodology follows a "Grounded Research Plan" design, where a chatbot serves as a reasoning layer over structured ABSA evidence. We utilize the Retrieval-Augmented Generation paradigm to ensure every conversational output is linked to a specific citation in the revision_analysis dataset (Bronzini et al., 2024; Tran et al., 2025).

3.2. Data Sources

3.2.1. Dataset Characteristics

The primary data includes documentation_chatbot.md (for plan structure) and the results/revision_analysis/ directory, which contains granular evidence of how corporate claims have evolved over reporting cycles.

3.2.2. Rationale

Focusing on "Revision Analysis" allows the chatbot to present a longitudinal view of a company's ESG commitments, identifying where claims have been modified or retracted—a key indicator of greenwashing risk (Ong et al., 2025).

3.2.3. Data Accessibility and Ethical Considerations

Ensures the chatbot maintains transparency by providing "verifiable references" for every claim, a feature critical for professional report generation (Zhao et al., 2026).

3.3. Preprocessing Pipeline & System Details





Document-to-Plan Conversion: Automated transformation of documentation_chatbot.md into an indexed knowledge base for the Streamlit app.



Evidence Filtering: Extracting "compact evidence" from JSON-based revision results to reduce context window noise.



ABSA Layer: Mapping sentiment results to specific ESG categories (e.g., carbon emissions vs. labor practices) to enable aspect-specific querying (Yi et al., 2025).



Chapter 4: EXPERIMENTS

4.1. Implementation Details

The prototype is built using Streamlit (chatbot/app.py). It utilizes a "feasibility study" configuration, focusing on research-plan presentation rather than real-time production inference.

4.2. Evaluation Metrics





Grounding Fidelity: Measuring the accuracy of the chatbot in referencing results/revision_analysis/ without hallucinations (Ding et al., 2025).



Aspect Identification F1: Evaluating the model's ability to correctly categorize user queries into ESG aspects (similar to the >0.8 F1 achieved in bank advisory tests (Yi et al., 2025)).



Response Eloquence: Qualitative assessment of the assistant’s ability to formulate coherent sustainability narratives (Mishra et al., 2024).

4.3. Experimental Results

4.3.1. Comparison with State-Of-The-Art

Performance comparison against general-purpose LLMs and specialized agents like ESGAgent, particularly in handling multi-step auditing workflows (Zhao et al., 2026).

4.3.2. Ground Truth Generation

Discussion on using the A3CG dataset approach to create gold-standard aspect-action pairs for validating the chatbot’s reasoning (Ong et al., 2025).

4.3.3. Ablation Studies

Testing the impact of the "Revision Analysis" grounding—evaluating how much the absence of longitudinal data increases the chatbot’s susceptibility to greenwashed claims.



5. DISCUSSION

This section addresses the feasibility of deploying conversational layers over complex ABSA evidence. It explores the "Glitter vs. Gold" dilemma—whether the chatbot effectively distinguishes between genuine corporate social responsibility initiatives and mere rhetorical disclosure (Bronzini et al., 2024).



6. CONCLUSION

The study concludes that a grounded chatbot layer significantly enhances the accessibility of ESG ABSA evidence. By utilizing a revision-analysis grounding, the system provides a more transparent and robust tool for sustainability auditing compared to text-only sentiment models (Ong et al., 2025; Zhao et al., 2026).



7. REFERENCES

(Citations include (Ong et al., 2025), (Ong et al., 2025), (Mishra et al., 2024), (Zhao et al., 2026), (Ding et al., 2025), (Yi et al., 2025), (Tran et al., 2025), (Bronzini et al., 2024))
