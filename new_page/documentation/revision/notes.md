To improve **Aspect 3 — Outlining of the Theme**, which is currently assessed at a **2/5** due to severe structural and logical shortcomings, you must move from a "templated" draft to a cohesive, logically progressing narrative.

Here is an elaboration on how to improve this aspect and pointers for the further analysis required.

### **1. Eliminating Structural Redundancy (The Most Urgent Fix)**
The primary reason for the low score is the **repetitive boilerplate text** used across Chapters III, IV, and V. Under the grading rubric, a 2/5 indicates "shortcomings in the logical structure which make it difficult for the reader to understand the applied methods".
*   **Action:** Collapse the six methodology subsections (3.1–3.6). Currently, every subsection repeats the same "mixed-method research logic" and "332 records" paragraph. 
*   **Logic:** State your overarching research design (mixed methods, exploratory design) **once** at the beginning of Chapter III. Each subsequent section must contain **only content unique to that phase** of the research.

### **2. Replacing Scaffolding with Technical Depth**
A professional thesis layout (Grade 5) requires "appropriate emphasis on key issues". Your current draft uses internal planning labels as body text, which signals the work is unfinished.
*   **Data Collection (Section 3.3):** Instead of repeating the research positioning, describe your **actual data**: the specific companies, the OJK portal used, the number of pages processed, and the specific OCR tools employed.
*   **Model Design (Section 3.4):** Transition from a template to technical specifics. Detail the **transformer backbones** (e.g., XLM-Roberta vs. mBERT), the fine-tuning strategy, and how your ontology paths are encoded.
*   **Discussion (Chapter V):** Remove the 1:1 restatements. Use this chapter to synthesize findings across sections rather than repeating the results summary four times.

### **3. Pointers for Deeper Analysis (Required for Aspects 5 & 6)**
To support a better outline, the content within that structure needs more analytical rigor. The following pointers address the "missing" elements identified in the feedback:

*   **Quantify OCR Quality:** You cannot claim an "OCR-to-record pipeline" (Contribution 1) without measuring **Character Error Rate (CER)** or **Word Error Rate (WER)**. Analyze how OCR noise specifically contributed to the "61 missing tone" records.
*   **Cross-Template Stability Analysis:** You have used seven prompt templates. Your analysis should move beyond counting runs to **quantifying variance**. Show which template (e.g., Chain-of-Thought vs. Few-Shot) produced the highest JSON parse success rate and the lowest "schema drift".
*   **Statistical Validation of Tone Labels:** The current comparison to ClimateBERT is purely descriptive (counting co-occurrences). To reach a Master's level evaluation (Aspect 6), compute **Cohen’s kappa** or percentage agreement between your LLM-assigned tones and the ClimateBERT-predicted labels.
*   **The "Greenwashing Index" Computation:** You defined this as a commitment-to-outcome ratio. To justify your theme, you must **actually compute and visualize this index** at the company level using your extracted 332 records. For example, plot BeFa vs. VKTR to show who has a higher "rhetoric-to-results" imbalance.

### **4. Refinement of Language and Layout**
*   **Tense Consistency:** Ensure Chapter III (Methodology) and Chapter IV (Results) use the **past tense** to describe completed work. Currently, they mix future-tense planning ("will be designed") with present reporting, creating a "project plan" feel rather than a final thesis.
*   **Table of Contents (ToC) Clean-up:** Your ToC currently lists over 80 subsections, many of which are placeholders like "subsection Purpose" or "Rationale". Consolidate these into 15–20 meaningful, content-driven headings to improve the "logical structure" required for a Grade 3 or higher.

To improve **Aspect 4 — Introduction and state of the art** from its current estimate of **3/5** to a **5/5**, you must shift the focus from a "wide but shallow" narrative to a technically grounded justification of your engineering choices. A score of 3 indicates the issues are "comprehensible," but a 5 requires that your chosen methods be "justified in relation to the state of the art" through empirical evidence and prior research.

The following elaboration details why the current draft is limited and provides a checklist for the deeper analysis required.

### **1. Elaboration of Current Grading (Reasoning)**
The primary reason for the 3/5 grade is that the literature review is heavily skewed toward **ESG theory** (governance, accounting, finance) at the expense of **NLP methodology**.
*   **The Granularity Gap:** While you cite the importance of ABSA, you do not discuss concrete benchmark datasets like **SemEval ABSA, FinancialPhraseBank, or MAMS**. This makes your task formulation feel isolated from the broader NLP research community.
*   **The "Black Box" of Performance:** You mention models like ClimateBERT and FinBERT, but you do not compare their reported **F1 scores** on standard benchmarks. Without these numbers, your decision to use "ClimateBERT + LLMs" is a narrative preference rather than an engineering decision grounded in the state of the art.
*   **Surface-Level Cross-Lingual Review:** You cite Šmíd & Král (2025) as a survey but fail to extract the critical empirical finding: the **performance gap** between monolingual and cross-lingual ABSA, especially for low-resource pairs like Indonesian/English.

### **2. Pointers for "More Analysis" to Reach 5/5**
To achieve the "comprehensive, in-depth" requirement of the rubric, incorporate the following analytical layers:

#### **A. Technical Benchmarking Table (Essential Analysis)**
Create a "Model vs. Performance" table in Chapter II. This table should serve as the empirical foundation for your methodology.
*   **Columns:** Model Name, Training Corpus (e.g., general vs. financial), Benchmark Dataset, Reported Metric (Accuracy/F1), and Relevance to your task.
*   **Comparison:** Contrast **FinBERT’s** performance on the FinancialPhraseBank with **ClimateBERT’s** performance on climate disclosures. This justifies why you need a multi-model pipeline rather than a single "one-size-fits-all" model.

#### **B. Cross-Lingual Transfer Degradation Analysis**
Move beyond noting that reports are bilingual. Analyze the **transfer learning challenges** specific to Indonesian corporate text.
*   **Indonesian-Specific NLP:** Investigate state-of-the-art models for Indonesian (e.g., **IndoBERT**) and analyze whether they outperform multilingual models (mBERT, XLM-R) in ABSA tasks.
*   **Gap Analysis:** Specifically discuss "lexical drift" between OJK regulatory Indonesian and international GRI English. Cite how current cross-lingual techniques (alignment-based vs. translation-based) address this.

#### **C. Critical Evaluation of LLM Stability**
The state of the art in LLM extraction acknowledges **output instability**.
*   **State-of-the-Art Mitigation:** Research and analyze how other studies have used **Chain-of-Thought (CoT)** or **Self-Consistency** techniques to stabilize structured JSON outputs in financial domains. This justifies your choice to test seven different prompt templates.

#### **D. OCR Error Propagation Analysis**
Your Gap 4 identifies OCR neglect. To make this "in-depth," you need to cite prior research on **"error-aware NLP."**
*   **Analysis Pointers:** Discuss how character error rates (CER) impact tokenization and subsequent sentiment classification in bilingual documents. This transforms "OCR is hard" into a technically justified research gap.

### **3. Checklist for Structural Improvements**
*   [ ] **Delete non-NLP padding:** Reduce the excessive summaries of general sustainability reporting trends (e.g., Srivastava & Anand 2023) if they do not lead directly to a specific NLP requirement.
*   [ ] **Justify the Tone Taxonomy:** Don't just propose the "Commitment/Action/Outcome" triad; justify it by citing its roots in **Legitimacy Theory** and **Signaling Theory**, explaining why binary "positive/negative" sentiment is an engineering failure for greenwashing detection.
*   [ ] **Connect XAI to Stakeholders:** When discussing SHAP and LIME, specifically state why these are "regulator-friendly." How does a SHAP plot satisfy an auditor’s need for "traceability" compared to an attention map?

By anchoring your choices in **quantitative comparisons** and **low-resource language challenges**, you will move from a comprehensible introduction (3/5) to one that justifies the methodology against the global state of the art (5/5).

To improve **Aspect 5 — Achievement of Aims** from its current estimated grade of **2/5**, you must address the significant gap between the **six substantial contributions** promised in your research table and the actual depth of the implementation. A score of 2 indicates that aims were not fully achieved due to minor shortcomings or, more critically, **insufficient proof or documentation** regarding their achievement.

Below are strategies to improve this aspect and specific pointers for the deeper analysis required to bridge the credibility gap.

### **1. Aligning Contributions with Technical Evidence**
The primary reason for the low score is the "credibility problem" created by claiming sophisticated outputs (like an ontology-based ABSA layer) that remain largely conceptual in the current draft.
*   **Narrow the Scope:** If you cannot extend the implementation, reframe the thesis as a **proof-of-concept** or prototype. Focus your claims on the three genuine strengths: the bilingual Indonesian ESG framing, the proposed commitment/action/outcome tone taxonomy, and the pipeline prototype.
*   **Extension Option:** If you maintain the current contribution claims, you must provide the missing evaluation data for each. For example, Contribution 4 (Ontology-based ABSA) requires evidence that a machine-readable ontology was actually built and used to guide classification, rather than just being discussed in the literature review.

### **2. Pointers for Missing Analysis (The "Proof of Achievement")**
To move toward a Grade 4 or 5, you must provide quantitative proof for every claimed contribution.

*   **Quantify OCR Fidelity (Contribution 1):** You cannot claim a "fully integrated pipeline" without measuring its primary bottleneck. Compute the **Character Error Rate (CER)** and **Word Error Rate (WER)** across a sample of your Indonesian and English pages to document how text noise affects extraction.
*   **Statistical Prompt Comparison (Contribution 2):** You have implemented seven templates, but the comparison is currently superficial. Add a results table showing **F1 scores, JSON parse success rates, and schema drift rates** per template to scientifically justify which prompting strategy (e.g., Chain-of-Thought vs. Few-Shot) is most robust.
*   **Pilot Human Validation (Contribution 3):** A "validated tone taxonomy" requires human-in-the-loop proof. Perform a pilot annotation on a small subset of the 332 records and compute **inter-annotator agreement (Cohen’s kappa)** to prove the taxonomy is reliable and not just an LLM hallucination.
*   **Expanded Semantic Validation (Contribution 5):** The current ClimateBERT comparison uses only **three remote validation inputs**, which constitutes a "proof-of-concept" rather than a framework. You must run ClimateBERT over a significant portion of your 332 records and compute statistical concordance to validate that your LLM-assigned "commitment" tones align with independent climate-commitment labels.
*   **Calculate the Greenwashing Index:** You defined the greenwashing index as a **commitment-to-outcome ratio** but never actually computed it. To achieve your aims, you must visualize this index at the company level (e.g., comparing the "rhetoric-to-results" ratio of BeFa vs. PTBA) using your extracted data.

### **3. Technical Analysis for Explainability**
Contribution 6 promises explainability, but the current text only discusses "lexical triggers".
*   **Quantitative Feature Importance:** To support your claim, you should implement and visualize **SHAP or LIME values**. This analysis would show which specific words (e.g., "target," "achieved," "will") the model actually relied on to distinguish a "commitment" from an "outcome".
*   **Ontology Path Traversal:** If claiming an ontology-based layer, provide a visualization showing the **reasoning chain** from a raw sentence to a specific GRI/SASB node.

### **4. Addressing Weaknesses in the Results (RQ4)**
A high-scoring thesis (Grade 5) requires swifter performance and "fresh viewpoints".
*   **Analyze Failure Modes:** Use the **61 missing tone records** and instances of **schema drift** (where commitment was categorized as sentiment) as primary data for a **diagnostics framework**. 
*   **Actionable Feedback:** Explain *why* these failures occurred—for example, analyzing if specific Indonesian regulatory lexicons caused the "missing tone" errors—to inform future model refinement.

To improve **Aspect 6 — Author's Evaluation of Results** from an estimated **2/5** to a higher grade, you must move beyond a purely descriptive summary of your data and provide a rigorous, justified analysis tied to your research aims. A score of 2 indicates that your current assessment is "superficial or inadequately justified".

Here is how to improve this aspect and specific pointers for the deeper analysis required.

### **1. Implementing Quantitative Performance Metrics**
The most critical missing element is a standard set of technical metrics. To reach a Grade 3 or 4, you must describe exactly how results were obtained and provide properly justified evaluations.
*   **Per-Template Performance Table:** Instead of just listing run counts, create a table showing:
    *   **JSON Parse Success Rate:** Percentage of runs that produced valid, machine-readable records.
    *   **Field Completion Rate:** How often optional fields like `evidence_span` were populated.
    *   **Missing Tone Rate:** Quantify the "61 missing tones" as a percentage of the 332 records (18.4%) and show which templates (e.g., zero-shot vs. few-shot) were more prone to this failure.
*   **Schema Drift Quantification:** You identified that 18 records had "commitment" written into the sentiment field. Analyze if this "schema drift" is concentrated in a specific LLM (Model A vs. Model B) or a specific language (Indonesian vs. English).

### **2. Moving from Counting to Statistical Validation**
Your current ClimateBERT "validation" is merely a count of co-occurrences (e.g., 91 co-occurrences between commitment and climate-commitment).
*   **Compute Agreement Statistics:** Calculate **Cohen’s kappa** or simple percentage agreement between your LLM-assigned tones and ClimateBERT’s labels. This provides a "properly justified" evaluation required for higher grades.
*   **Analyze Discordant Cases:** Investigate the "missing tone" records that co-occur with `climate-commitment` (22 cases) and `environmental-claims` (21 cases). Explain why the model recognized the *topic* but failed to assign a *tone*, providing actionable feedback for future model refinement.

### **3. Computing and Visualizing the "Greenwashing Index"**
You conceptually defined the greenwashing index as a **commitment-to-outcome ratio** but never calculated it.
*   **Action:** Generate a visualization (e.g., a bar chart) comparing the "Rhetoric vs. Results" ratio for the different companies in your dataset (e.g., BeFa vs. VKTR). 
*   **Analysis:** A higher ratio suggests a potential "warning signal" for regulators or investors, which directly addresses the significance of your results to the organization and the field.

### **4. Enhancing the Discussion (Chapter V)**
A Grade 5 requires discussing the "general significance to modern engineering or science". Currently, your discussion chapter repeats the same summary text four times.
*   **Synthesize with Theory:** Use your results to test the theories mentioned in your literature review. For example, does the dominance of "commitment" tone (115 vs. 50 outcomes) provide empirical evidence for **Legitimacy Theory** (firms signaling responsibility without performance)?
*   **Identify Stakeholder Gaps:** Discuss why the **social pillar (S)** is severely underrepresented (only 4 records). Is this a failure of the extraction prompts, the source documents, or does it reflect a corporate prioritization of environmental/governance audiences over social stakeholders?

### **5. Summary Checklist for Deeper Analysis**
*   **Quantify OCR Quality:** You cannot claim a "PDF-to-structured-ESG" pipeline without measuring the Character Error Rate (CER) or Word Error Rate (WER) to see how text noise affected the extraction.
*   **Template Sensitivity Analysis:** Formally compare whether **Chain-of-Thought** templates significantly reduced "interpretive uncertainty" or improved "reasoning" compared to **Zero-Shot** variants.
*   **Ontology Path Coverage:** Measure what percentage of extracted records successfully mapped to your proposed GRI/SASB/TCFD ontology nodes.

To improve **Aspect 9 — Language** from its current estimate of **2/5** to a **5/5**, you must transform the document from a "detailed project plan" into a finished scientific work. A grade of 2 indicates "minor shortcomings such as poor legibility... and clumsy sentences". In your case, this is primarily driven by **structural redundancy** and **internal scaffolding** that remains in the text.

Below is an elaboration on how to improve this aspect, followed by pointers for deeper linguistic analysis.

### **1. Eliminating Editorial Scaffolding (The 2/5 to 5/5 Path)**
The most urgent language fix is removing the planning notes that currently act as body text.
*   **Action:** Delete all internal headings such as "subsection Purpose", "Research Positioning", "Operational Design", and "Expected Output". These should be converted into flowing prose or removed entirely.
*   **Eliminate Boilerplate Repetition:** Currently, Chapters III, IV, and V repeat the same paragraph regarding "mixed-method research logic" and the "332 records" distribution. Under the rubric, this qualifies as "undue use of repetition".
*   **Tense Correction:** The methodology and results chapters currently mix future-tense planning ("will be designed") with present-tense reporting. You must convert all descriptions of completed work to the **past tense** (e.g., "The pipeline was designed...").

### **2. Pointers for Deeper Linguistic Analysis**
To move beyond a descriptive report, you should analyze the **language patterns** found in your 332 extracted records. This fulfills the requirement for "in-depth" technical justification in related aspects.

*   **Lexical Trigger Analysis (Quantification):** You mention "lexical triggers" for tone (e.g., "will" for commitment vs. "achieved" for outcome). 
    *   **New Analysis:** Create a table quantifying the frequency of these triggers. For example, how many of your 115 "commitment" records relied on **modal verbs** (*akan, will, intends*) versus how many "outcome" records used **past-participle markers** (*telah, achieved, completed*)?
*   **Analyze "Interpretive Uncertainty":** The feedback notes that "a neutral sentence may still be an important commitment".
    *   **New Analysis:** Perform a **Failure Mode Analysis** on the 61 "missing tone" records. Categorize whether these failures occurred because the language was too **hedged** (vague), used **passive voice**, or suffered from **Indonesian/English lexical drift** where specific regulatory terms were not recognized.
*   **Cross-Lingual Comparison:** Analyze if "schema drift" (e.g., writing commitment into the sentiment field) happened more frequently in **Indonesian vs. English** text. This would provide "scientifically significant results" regarding how LLMs handle low-resource regulatory Indonesian.
*   **Sentence Complexity Study:** The rubric suggests breaking long compound sentences. 
    *   **New Analysis:** Use a tool to calculate the **Readability Index** (like Flesch-Kincaid) for sentences where the model failed to assign a tone. Determine if sentence length or complexity is a primary driver of model extraction errors (Gap 3).

### **3. Language Refinement Checklist**
*   [ ] **Standardize Terminology:** Ensure terms like "Tone," "Sentiment," and "Aspect" are used consistently according to your defined taxonomy.
*   [ ] **Audit for "Future Work" Contradictions:** Ensure that tasks listed in the "Future Work" section (like running ClimateBERT over all records) are not also described as completed in the methodology.
*   [ ] **Bilingual Consistency:** Verify that Indonesian terms in your JSON records (e.g., *komitmen esg*) are consistently mapped to their English equivalents in your discussion.

By removing the "template" feel and replacing it with a **quantitative evaluation of the linguistic features** that drove your model's decisions, you satisfy both the "Language" and "Author's Evaluation" criteria for a higher grade.

To improve **Aspect 10 — Layout** from a **2/3** to an **impeccable 3/3**, you must transition the document from a "nested planning template" into a professional academic manuscript. A score of 2 indicates "minor shortcomings in the layout that sometimes impede the total presentation," which in your case is primarily due to **structural bloat** and **visible scaffolding**.

The following steps detail how to fix the layout and provide pointers for the deeper analysis required to justify your technical claims.

### **1. Urgent Layout Improvements (The Path to 3/3)**

*   **Restructure the Table of Contents (ToC):** The current ToC is considered "unusable" because it lists over **80 numbered sub-items** as top-level headings. You must hide sub-headings like "subsection Purpose," "Rationale," and "Expected Output" from the ToC, showing only major sections (e.g., III, III-A).
*   **Remove Structural Placeholders:** Headings such as "Research Positioning," "Operational Design," and "subsection-Specific Report" appear as labels inside the body text. Under the grading rubric, these "structural meta-tags" impede reading flow and must be deleted or converted into standard flowing prose.
*   **Optimize Figure Captions and Consistency:** To reach Grade 3, captions must be **consistent with the language of the thesis** and provide clear explanations of the images. Ensure that figures like the `aspect_by_tone_heatmap` and `tone_distribution` include descriptive titles in the text that explain the significance of the data, such as the **dominance of commitment tone (115 records)** over outcomes.
*   **Clean Up the Bibliography:** Ensure the references section follows a strict **IEEE two-column style** without the planning notes currently visible in the draft.

### **2. Pointers for More Analysis (Layout-Related Technical Depth)**

To achieve higher grades in **Aspect 5 (Aims)** and **Aspect 6 (Evaluation)**, you need to analyze how the **physical layout of reports** impacted your model's performance.

*   **Analyze Layout-Induced Extraction Errors:** You identified **61 missing tone records** and instances of **schema drift**. Perform an analysis to see if these errors correlate with specific layout features, such as **text inside tables** versus standard narrative blocks.
*   **Quantify OCR Alignment Quality:** You claim a "page-aware" and "layout-aware" pipeline but have not measured its accuracy. Analyze the **Word Error Rate (WER)** specifically for pages with complex layouts (side-by-side bilingual columns or infographics) to document how document structure affects signal fidelity.
*   **Evaluate Cross-Lingual Layout Logic:** Since Indonesian reports often use **bilingual side-by-side layouts**, analyze whether your OCR-to-markdown process correctly separated the two languages or if "code-switching" errors occurred because the model read across column boundaries.
*   **Visual Validation of Ontology Paths:** To support your "Contribution 6" on explainability, provide a **layout-based visualization** showing the "reasoning chain" from a specific paragraph in a PDF to a node in your GRI/SASB ontology. This proves the "provenance" you claim is actually functional.

### **3. Critical Summary for Revision**
The strongest parts of your thesis are the **problem identification** and the **novel tri-tiered tone taxonomy**. However, the document currently looks like a **"detailed project plan annotated with results"** rather than a finished thesis. By collapsing the redundant structural labels and quantifying how the **complex PDF layouts** hindered your data extraction, you move from a borderline 21/42 score toward a scientifically significant master’s level work.

To improve the estimated grades for Aspects 1, 2, 7, and 8, you must move from a "prototype" stage to a completed research system with validated, technically grounded outputs. The current assessments identify a gap between your ambitious contributions and the evidence provided in the draft.

The following sections elaborate on how to improve each aspect and the specific analysis required to achieve the highest possible grades.

### **Aspect 1: Scope of Thesis**
*   **Estimated Grade: 2 / 3 points**
*   **Reasoning:** The thesis correctly identifies several complex themes (ESG, ABSA, bilingual Indonesian/English, and document engineering), but the scope promises (such as an ontology-based layer and external validation framework) currently exceed the actual delivery.
*   **How to Reach 3/3:** You must demonstrate that these themes are not just discussed but fully integrated into a functional pipeline.
*   **Pointers for More Analysis:**
    *   **Ontology Integration:** Provide proof of a machine-readable ontology (e.g., in OWL or RDF format) that was actually used to guide aspect classification, rather than just referencing existing frameworks.
    *   **Bilingual Signal Alignment:** Quantify the consistency of your model's outputs across the two languages. For example, show that the model assigns the same "commitment" tone to a specific Indonesian sentence and its English translation.

### **Aspect 2: Challenge**
*   **Estimated Grade: 2 / 3 points**
*   **Reasoning:** While the topic is implementationally demanding, the current depth of implementation is considered "shallow" because it relies on standard LLM prompting without fine-tuning or rigorous quantitative modeling of the "phenomena".
*   **How to Reach 3/3:** You must engage more deeply with the basic theory of the theme (e.g., Signaling or Legitimacy theory) and apply it in a demanding quantitative evaluation.
*   **Pointers for More Analysis:**
    *   **Model Benchmarking:** Instead of only using LLMs, compare your results against a domain-adapted baseline like **IndoBERT** or a fine-tuned **XLM-Roberta** to justify your choice of methods against the state of the art.
    *   **Complexity Metrics:** Analyze how your pipeline handles "hard" cases, such as sentences with multiple conflicting ESG aspects or complex regulatory Indonesian phrasing.

### **Aspect 7: Significance of Results**
*   **Estimated Grade: 2 / 5 points**
*   **Reasoning:** The setting is novel, but since you admit the "greenwashing index" is unvalidated and lacks ground truth, the significance of the results is currently "smaller than expected" for a Master's level.
*   **How to Reach 4/5 or 5/5:** Discuss the results' significance to a specific organization (like OJK or an investment firm) and prove they introduce a "remarkable improvement".
*   **Pointers for More Analysis:**
    *   **Actual Calculation of the Greenwashing Index:** You defined the index as a **commitment-to-outcome ratio** but never calculated it. Compute and visualize this ratio for specific companies (e.g., BeFa vs. PTBA) to show how it functions as a risk screening tool.
    *   **External Validation Case Study:** Compare your pipeline's findings against external data, such as actual carbon emission trends or third-party ESG controversy scores, to prove that your "greenwashing flags" have real-world predictive value.

### **Aspect 8: Initiative**
*   **Estimated Grade: 2 / 3 points**
*   **Reasoning:** Developing a working Streamlit dashboard shows initiative, but the "pervasive copy-paste structure" throughout the methodology and results chapters suggests a lack of independent self-review.
*   **How to Reach 3/3:** Demonstrate active and independent work by thoroughly revising the structure to eliminate redundant templates.
*   **Pointers for More Analysis:**
    *   **Deep Failure Mode Analysis (RQ4):** Don't just note that 61 records are "missing tones." Conduct a rigorous, independent investigation into *why* they failed. Categorize these failures by sentence length, language, or specific GRI/SASB topic.
    *   **Ablation Study of Prompts:** Independently design an experiment to isolate which part of your **seven prompt templates** (e.g., few-shot examples vs. chain-of-thought instructions) actually provides the most stability.

### **Summary of Analysis Required to Improve Grades**
| Aspect | Required Analysis Pointer | Target Grade |
| :--- | :--- | :--- |
| **1. Scope** | Build and document a **bilingual machine-readable ontology**. | 3 / 3 |
| **2. Challenge** | Implement a **transformer-based baseline** (e.g., IndoBERT) for comparison. | 3 / 3 |
| **7. Significance** | Compute the **Greenwashing Index** and plot it at the company level. | 4 / 5+ |
| **8. Initiative** | Conduct a **linguistic failure-mode analysis** on the 61 missing records. | 3 / 3 |