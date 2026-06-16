# Thesis Defense & Testing Questions
https://notebooklm.google.com/notebook/e837ec26-003e-444b-9c84-44c3caaa21bf
This document contains a comprehensive list of questions designed to test your thesis work: **"Toward an Executable ESG Aspect-Based Sentiment Analysis Framework for Indonesian Sustainability Reports."**

---

## **Part 1: Core Objectives and Dataset**

### **1. Thesis Title and Core Objectives**
*   **What is the full title of your thesis?**
*   **What are the primary research questions (RQs) your thesis addresses?**
*   **Why is "Tone" a central contribution of your work compared to standard sentiment analysis?**

### **2. Dataset and Data Sourcing**
*   **Cite the name of the dataset or where it was sourced from.**
*   **Explain three technical attributes of this dataset.**
*   **How did you handle the transition from raw PDF to machine-readable evidence?**
*   **Why did you limit the active experimental subset to 23 reports (5,512 pages)?**
    *   *Answer:* Due to practical constraints such as OCR completion time, background job stability, and the need for manual audit/annotation capacity.

---

## **Part 2: Methodology and Architecture**

### **3. System Architecture and Preprocessing**
*   **Describe the four main layers of your system architecture.**
*   **Why did you choose the "Page" as your primary unit of analysis?**
*   **What specific artifacts are produced during the OCR expansion stage?**

### **4. Feature Engineering and ML Models**
*   **Your framework uses a "Hybrid Contextual Model." Explain its architecture.**
*   **How does the Rule-Based model differ from the Classical ML model in your work?**
*   **What is "Ontology Alignment" in the context of your framework?**
*   **Explain the HierarchicalEncoder's role in the Hybrid Model.**
    *   *Answer:* It captures cross-section attention, allowing the model to interpret a sentence not just locally, but within the context of the report's broader section (e.g., "Governance" vs. "Environment").

---

## **Part 3: LLM Extraction and Performance**

### **5. Prompting Strategy**
*   **You tested multiple prompting strategies. Which one yielded the best results?**
*   **Why did you include both Indonesian and English prompts in your experiments?**
*   **What is the difference in performance between `tone_chain_of_thought_english.md` and the Indonesian version?**
    *   *Answer:* The English version generally achieved higher record yields (Avg. 6.25 vs 4.07), likely due to the model's stronger instruction-following capabilities in English.

### **6. Model Comparison and Stability**
*   **Compare the performance of `arcee-ai/trinity-large-preview` vs `openai/gpt-oss-120b`.**
*   **What metrics did you use to evaluate "Extraction Quality" beyond simple accuracy?**
*   **Why did `minimax/minimax-m2.5` have a high volume of runs but low parse reliability (56.6%)?**
    *   *Answer:* It represents "live usage" noise; its lower reliability highlights why choosing a stable model like `trinity-large-preview` was necessary for the final thesis findings.

---

## **Part 4: Results, Diagnostics, and Ethics**

### **7. Findings and Comparison**
*   **How did you validate your tone labels against ClimateBERT?**
*   **What was the dominant ESG pillar in your extracted evidence?**
*   **Why were "Social" disclosures significantly underrepresented in your results?**
    *   *Answer:* Likely due to corporate reporting priorities (which favor Environmental and Governance disclosures) and potential gaps in the initial Social-pillar lexicons.

### **8. Failure Modes and Diagnostics**
*   **What is the most frequent failure mode in your pipeline?**
*   **How do "Hedged or Modal Language" (e.g., "will", "intend") affect your model's accuracy?**
*   **Explain the "Passive Voice" failure mode.**
    *   *Answer:* Passive constructions often hide the "actor" or the specific "action," making it difficult for the model to distinguish between a currently active process and an achieved outcome.

---

## **Part 5: Analytical Metrics and Future Work**

### **9. Specialized Metrics**
*   **What is the "Greenwashing Index" you proposed?**
*   **How does the "Denominator Audit" help in interpreting your results?**

### **10. Conclusion and Future Directions**
*   **If you had more time, how would you improve the "Social" pillar coverage?**
*   **What is your final verdict on the feasibility of automated ESG tone analysis for Indonesian reports?**

---

## **Part 6: Advanced Technical & Domain Questions**

### **11. Bilingualism and Code-Switching**
*   **How does "Code-Switching" (mixing Indonesian and English) impact the extraction accuracy?**
    *   *Answer:* It increases the risk of "schema drift" or "missing tone" if the model's triggers are only optimized for one language. Your hybrid model mitigates this by using `distilbert-base-multilingual-cased`.
*   **Did you observe any specific Indonesian regulatory terms that the LLM struggled with?**
    *   *Answer:* Yes, terms like "roadmap karbon" or specific OJK-mandated governance phrasing sometimes produce "Unknown" tones in the rule-based layer.

### **12. Ontology and Regulatory Alignment**
*   **How does your ontology map to global standards like GRI (Global Reporting Initiative)?**
    *   *Answer:* The ontology is anchored to GRI-related categories, mapping specific Indonesian aspects (like "pelatihan antikorupsi") to canonical ESG concepts.
*   **You tracked 52 aspects. Are these exhaustive for the Indonesian market?**
    *   *Answer:* No, they represent the "active experimental subset." A full commercial deployment would require a broader ontology covering all OJK-mandated disclosure fields.

### **13. Scalability and Real-World Impact**
*   **How would a financial regulator (like OJK) benefit from your "Provenance" feature?**
    *   *Answer:* It allows them to verify automated "green" claims instantly by clicking a link that shows the exact page in the report where the claim originated, preventing "black-box" conclusions.
*   **Your framework uses Streamlit for the UI. Is this suitable for large-scale enterprise use?**
    *   *Answer:* Streamlit is excellent for **research and auditing (the "audit surface")**, but the backend background workers (running through `status.json` and `control.json`) are what provide the true scalability for batch processing.

### **14. Theoretical and Counter-Arguments**
*   **Why not just use a single large LLM (like GPT-4) for everything instead of your complex pipeline?**
    *   *Answer:* 1) **Traceability:** A single LLM call is a black box; your pipeline preserves every intermediate step. 2) **Sensitivity:** As shown with `gpt-oss-120b`, even "large" models can fail on tone classification despite being fluent. 3) **Cost/Speed:** Your hybrid approach allows for faster local analysis where high-end LLMs aren't needed.
*   **Is "Tone" just a proxy for "Commitment"?**
    *   *Answer:* No. Tone also captures **Action** and **Outcome**. While commitment is a large part of it, the ability to identify *achieved* results (Outcome) is the most critical feature for detecting greenwashing.
