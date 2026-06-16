# Thesis Defense & Testing Questions

This document contains a list of questions designed to test your thesis work: **"Toward an Executable ESG Aspect-Based Sentiment Analysis Framework for Indonesian Sustainability Reports."**

---

### **1. Thesis Title and Core Objectives**
*   **What is the full title of your thesis?**
    *   *Expected:* "Toward an Executable ESG Aspect-Based Sentiment Analysis Framework for Indonesian Sustainability Reports."
*   **What are the primary research questions (RQs) your thesis addresses?**
    *   *Answer:* Your work covers ESG evidence transformation (RQ1), representation of pillars/tone (RQ2), comparison with ClimateBERT (RQ3), and diagnostic instability (RQ4).
*   **Why is "Tone" a central contribution of your work compared to standard sentiment analysis?**
    *   *Expected:* Standard sentiment (positive/negative) misses the maturity of the disclosure. Your framework distinguishes between *Commitment* (promises), *Action* (active processes), and *Outcome* (verified results).

### **2. Dataset and Data Sourcing**
*   **Cite the name of the dataset or where it was sourced from.**
    *   *Expected:* A corpus of Indonesian sustainability and annual report PDFs (initially 193 files) stored in `data/thesis_pdf/`.
*   **Explain three technical attributes of this dataset.**
    *   *Answer:* 1) **Bilingual/Code-switched:** Contains both Indonesian and English text. 2) **High Volume:** The active subset covers ~5,512 pages across 23 reports. 3) **Unstructured:** Includes mixed narratives, tables, and regulatory boilerplate.
*   **How did you handle the transition from raw PDF to machine-readable evidence?**
    *   *Answer:* Using an OCR-based expansion pipeline that creates page-level Markdown and JSON metadata to preserve provenance.

### **3. Architecture and Methodology**
*   **Explain the "Executable" nature of your framework.**
    *   *Answer:* It is implemented as a functional Python/Streamlit repository where every stage (OCR, extraction, audit) produces versioned artifacts and can be re-run for validation.
*   **How does your architecture ensure "Provenance" for the extracted ESG records?**
    *   *Answer:* Each extracted record is linked back to its specific source page in the original PDF, allowing for manual auditing via the Streamlit dashboard.
*   **Describe the three main layers of your system architecture.**
    *   *Answer:* 1) **OCR Layer** (Ingestion), 2) **Extraction Layer** (LLM-based record generation), 3) **Analysis Layer** (Ontology alignment and diagnostic stability).

### **4. Sentimental and Tone Aspect**
*   **How was the "sentimental aspect" taken into account while deploying the architecture?**
    *   *Answer:* Beyond polarity, you used a multi-layered ABSA (Aspect-Based Sentiment Analysis) approach. This includes rule-based lexicons, classical ML (TF-IDF + Logistic Regression), and a hybrid contextual model.
*   **What specific tones does your framework classify, and which was the most dominant in your results?**
    *   *Answer:* Commitment, Action, and Outcome. *Commitment* was the dominant tone (115 out of 332 records).
*   **How did you validate your tone labels against external benchmarks?**
    *   *Answer:* By comparing them with ClimateBERT-style commitment labels, achieving 83.7% agreement and a Cohen’s kappa of 0.645.

### **5. Ethics and Bias**
*   **How were Ethics taken into consideration while building the architecture?**
    *   *Answer:* Since the data is corporate (public reports), the focus was on **evidential integrity**. By maintaining provenance links, you prevent "hallucinated" or decontextualized ESG claims, ensuring the model's output can always be verified against the source text.
*   **What are some inherent biases present in your dataset?**
    *   *Answer:* 1) **Sector Bias:** Some industries report more than others. 2) **Pillar Imbalance:** Environmental and Governance data is much more prevalent than Social data in the current snapshot.

### **6. Limitations and Failure Modes**
*   **Briefly explain 3 limitations of your work.**
    *   *Answer:* 1) **Prompt Sensitivity:** Extraction quality varies significantly depending on the prompt design (e.g., CoT vs. Zero-shot). 2) **Schema Drift:** Some LLMs fail to strictly follow the JSON schema, leading to missing fields. 3) **Proxy-Based Validation:** The ClimateBERT comparison is a proxy rather than a full one-to-one external benchmark.
*   **What is "Schema Drift" and why is it a problem for your framework?**
    *   *Answer:* It occurs when the LLM outputs malformed JSON or repurposes fields (e.g., putting tone values in sentiment slots), which breaks the automated analysis pipeline.

### **7. Analytical Metrics**
*   **What is the "Greenwashing Index" you proposed, and how is it calculated?**
    *   *Answer:* It is a heuristic ratio between *Commitment* records and *Outcome* records at the document level.
*   **Why did you use Cohen's Kappa instead of just raw accuracy for your comparison results?**
    *   *Answer:* Because the *Commitment* class is very frequent; Kappa adjusts for the agreement that could happen by pure chance.
