Social Network Analysis



Based on your development of the Social Network Analysis track (social_network_analysis/app.py), which focuses on adapting graph-based methodologies to identify relational structures within ESG corpora, here is the defined thesis structure for Daris Dzakwan.

Chapter 1: Introduction

1.1. Motivation

The fragmented nature of ESG reporting makes it difficult to understand the systemic relationships between corporate entities, sustainability aspects, and regulatory frameworks (He et al., 2026). While traditional NLP can extract individual metrics, it often fails to capture the "web of influence" and thematic intersections—such as how climate risk relates to executive remuneration or supply chain ethics (Angioni et al., 2024; Ferjančič et al., 2024). By leveraging Social Network Analysis and Knowledge Graph representations, researchers can move beyond isolated data points to visualize the structural dependencies and co-occurrence patterns that define a company's sustainability narrative (Bronzini et al., 2024; He et al., 2026).

1.2. Research Questions and Goals





RQ1: How can co-entity and co-aspect networks derived from OCR corpus sections reveal hidden thematic clusters in corporate sustainability reports? (Shin & Lee, 2026)



RQ2: To what extent do graph-level centrality metrics provide an objective summary of a company's ESG focus compared to standard frequency-based analysis? (Shin & Lee, 2026)



Goal: To adapt graph-based knowledge discovery frameworks to ESG reports, enabling the identification of association trends and high-centrality sustainability concepts (Rawal et al., 2025).

1.3. Objectives and Contributions





Network Construction: Implementation of an automated pipeline (social_network_analysis/app.py) that builds co-entity networks using networkx and text heuristics.



Graph-level Summarization: Developing utilities to generate categorical summaries and "atlas-style" focus maps for large-scale ESG datasets (He et al., 2026; Rawal et al., 2025).



Relational Reasoning: Demonstrating that graph representations can align partially overlapping standards by anchoring concepts within a shared semantic network (He et al., 2026).

1.4. Thesis Structure

Outlines the methodology for transforming unstructured OCR text into structured entity-association graphs, followed by a quantitative analysis of network topology.



Chapter 2: Related Works

This chapter investigates the application of Knowledge Graphs and SNA in financial auditing. Recent research highlights that graph-based representations offer a versatile approach to illustrating structured information through nodes (concepts) and edges (relationships), providing insights that go beyond simple text extraction (Bronzini et al., 2024; Repke & Krestel, 2021).

State-of-the-Art Table: ESG Graph & Network Analysis







Framework/Model



Method



Primary Focus



Key Performance/Metric



Source





KG4ESG



KG Atlas



Multi-standard Alignment



Organizes 337 papers into Data→KG and KG→App paradigms.



(He, Zhou, Wang, Yu, Xiao, Li, (71477), et al., 2026; He, Zhou, Wang, Yu, Xiao, Li, Xu, et al., 2026)





ESGSenticNet



Neurosymbolic Graph



Concept Identification



Uses graph label propagation to categorize ESG phrases.



(Ong et al., 2025)





Glitter or Gold



Bipartite Graphs



Action Analysis



Statistical analysis of 500+ topics reveals regional disclosure patterns.



(Bronzini et al., 2024)





CONCOR Analysis



Centrality Analysis



CEO Messages



Identified "Sustainable" and "Society" as the most central nodes.



(Shin & Lee, 2026)





Entity Association



Co-occurrence Networks



Knowledge Discovery



Domain-independent pipeline for association mining and scoring.



(Rawal et al., 2025)





E2CNN



Neural KG Extraction



Financial Relations



Mitigates "overlap triple" problems in complex financial sentences.



(Li et al., 2025)



Chapter 3: Methodology

3.1. Overview of the Methodology

We propose an "Entity Association Mining" framework that treats ESG report sections as sources of relational data. The methodology utilizes simple text heuristics to identify co-occurrences between entities (e.g., organizations) and aspects (e.g., carbon neutral targets), building a representative graph of corporate commitments (Bronzini et al., 2024; Rawal et al., 2025).

3.2. Data Sources

3.2.1. Dataset Characteristics

The study processes unstructured text from the OCR corpus sections. This involves multi-modal data where visual structure and layout flow are preserved to ensure accurate relation extraction (He et al., 2026; Yan et al., 2025).

3.2.2. Rationale

Graph-based exploration is necessary because it allows users to navigate large document sets without prior knowledge of the data, which is essential for investigative work in audits or legal discovery (Repke & Krestel, 2021).

3.2.3. Data Accessibility and Ethical Considerations

Focuses on the use of public disclosures while addressing the "semantic overlap" problem, where the same entity may appear in multiple relations within a single sentence (Li et al., 2025).

3.3. Preprocessing & Network Pipeline





OCR-to-Graph Parsing: Transforming sections of results/esg_records.json into triples (subject-predicate-object) or co-occurrence pairs (Bronzini et al., 2024; Li et al., 2025).



Heuristic Extraction: Utilizing task_data.py definitions to identify relevant ESG pillars and entities through keyword-based association (Rawal et al., 2025).



Graph Construction: Employing networkx to build the topology and ui.py for rendering interactive network visualizations.



Chapter 4: EXPERIMENTS

4.1. Implementation Details

The experimental dashboard (app.py) allows for the dynamic generation of networks from different report subsections. It calculates graph-level properties such as degree centrality and cluster density to summarize the corpus (Rawal et al., 2025; Shin & Lee, 2026).

4.2. Evaluation Metrics





Centrality Measures: Identifying "hubs" of sustainability information using betweenness and eigenvector centrality (Shin & Lee, 2026).



Network Coherence: Evaluating how well the graph clusters related ESG themes compared to standard taxonomies like the GRI (He et al., 2026; Ong et al., 2025).



Information Density: Ratio of extracted entities and relationships per document section (Li et al., 2025).

4.3. Experimental Results

4.3.1. Comparison with State-Of-The-Art

Evaluating whether the heuristic-based network construction matches the performance of more complex neural relation extraction models like E2CNN (Li et al., 2025).

4.3.2. Ground Truth Generation

Using the ESG-RFM as a gold standard to validate the alignment of extracted network clusters with major ESG frameworks (He, Zhou, Wang, Yu, Xiao, Li, (71477), et al., 2026; He, Zhou, Wang, Yu, Xiao, Li, Xu, et al., 2026).

4.3.3. Ablation Studies

Comparing "co-entity" networks (focusing on organizations) vs. "co-aspect" networks (focusing on ESG topics) to see which provides more actionable audit signals (Bronzini et al., 2024; Shin & Lee, 2026).



5. DISCUSSION

This section explores the benefits of graph-based summaries for detecting "ESG-washing" (Lagasio, 2024). We discuss whether the centrality of certain concepts (e.g., "growth" vs. "environment") reveals a discrepancy between a company's portrayed sustainability practices and its actual operational focus (Lagasio, 2024; Shin & Lee, 2026).



6. CONCLUSION

The SNA track demonstrates that graph analysis is a powerful tool for navigating the information-dense ESG landscape. By transforming unstructured text into relational networks, we provide stakeholders with an intuitive, structural view of corporate sustainability narratives that traditional NLP methods often overlook (Bronzini et al., 2024; Repke & Krestel, 2021).



7. REFERENCES

(Citations include (Bronzini et al., 2024), (He et al., 2026), (He et al., 2026), (Ong et al., 2025), (Shin & Lee, 2026), (Rawal et al., 2025), (Repke & Krestel, 2021), (Li et al., 2025), (Lagasio, 2024), (Yan et al., 2025), (Ferjančič et al., 2024), (Angioni et al., 2024))
