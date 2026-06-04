# Chapter 6: Conclusion

## 6.1. Contribution Summary

This thesis set out to design an executable ESG aspect-based sentiment analysis framework for Indonesian sustainability reporting. Rather than treating ESG text analysis as a narrow sentence-classification task, the study approached it as an end-to-end research workspace that transforms raw corporate disclosure documents into structured, auditable, and thesis-ready ESG evidence records. Across Chapters 3, 4, and 5, the central argument has been that useful ESG NLP for Indonesian disclosure contexts requires more than a model. It requires a reproducible pipeline that integrates OCR, structured extraction, record-level schema design, comparison modeling, annotation workflows, ontology alignment, and diagnostic transparency.

The first contribution of the thesis is the creation of an executable document-to-record pipeline. The current repository demonstrates that PDF sustainability reports can be transformed into page-aware textual artifacts and then into structured ESG records while preserving source provenance. This is a meaningful contribution because ESG reporting analysis often begins from static PDF files, not pre-cleaned corpora. By making document transformation itself part of the research workflow, the thesis contributes an auditable infrastructure for future ESG NLP work.

The second contribution is the introduction of a record-level ESG ABSA schema that distinguishes not only aspect and ESG pillar, but also disclosure tone. This is conceptually important. Traditional sentiment analysis is not sufficient for sustainability reporting because positive sentiment does not reveal whether a company is making a commitment, describing an implementation action, or reporting an achieved outcome. The thesis therefore extends the analytical vocabulary of ESG ABSA by operationalizing commitment, action, and outcome as disclosure postures.

The third contribution is the integration of an external ClimateBERT comparison layer into the broader ESG extraction environment. The thesis does not claim that ClimateBERT and the ESG tone taxonomy are interchangeable. Instead, it demonstrates that their alignment and divergence can be used to study construct validity. The current implementation already reports meaningful proxy agreement, including `0.837` ClimateBERT proxy agreement and `0.645` Cohen’s kappa, which supports the view that the tone taxonomy is capturing semantically relevant climate-adjacent signals while still measuring something broader than climate classification alone.

The fourth contribution is the development of a benchmark-construction and validation environment rather than a one-shot extraction script. The system includes silver-label workflows, annotation coverage views, disagreement tables, review queues, and metrics pages prepared for formal evaluation. This matters because one of the main barriers in ESG ABSA is not just model design, but the lack of domain-appropriate labeled corpora. The thesis contributes infrastructure for building that benchmark progressively and transparently.

The fifth contribution is the integration of ontology-aware and semantic-export capabilities into the ESG ABSA workflow. The extracted records are not treated as flat isolated rows only; they can be linked to ontology paths, coverage summaries, and graph-export targets such as RDF, OWL, and Neo4j-style formats. This makes the system relevant not only for classification, but also for explainable ESG evidence organization and future knowledge-graph applications.

The sixth contribution is the explicit treatment of reproducibility as a first-class research objective. The system preserves prompt/model metadata, run artifacts, static figures, dashboards, and documentation, making the project more than a prototype UI. It becomes an executable research workspace in which outputs can be inspected, challenged, extended, and reused. In the context of LLM-mediated ESG extraction, this is particularly important because prompt sensitivity, parse fragility, and provider variability can otherwise remain hidden.

Taken together, these contributions show that the thesis is not merely an application of existing NLP models to ESG text. It is the design of an integrated, auditable, tone-aware ESG disclosure analysis environment tailored to the realities of Indonesian sustainability reporting.

### 6.1.1. Answers to the Research Questions

The thesis can now answer each research question at the level justified by the current evidence.

For RQ1, the answer is yes: sustainability-report PDFs can be transformed into structured ESG evidence records while preserving provenance. The current pipeline already processes source reports into OCR artifacts and structured ESG records, with the present implementation yielding `23` OCR documents and `332` structured ESG tone records. This demonstrates feasibility, although further OCR-quality quantification is still required.

For RQ2, the answer is also yes: ESG statements can be represented using a record-level schema that includes aspect, ESG pillar, sentiment, and tone. The current extracted corpus shows that this schema is operational and analytically useful. In particular, the distinction between commitment, action, and outcome produces interpretable disclosure patterns that would be invisible in sentiment-only analysis.

For RQ3, the answer is that ESG tone results and ClimateBERT-style labels are related but not identical. The current proxy alignment figures and the observed overlap between commitment tone and climate-commitment labels support the view that the tone taxonomy has meaningful external semantic grounding. However, the partial mismatch between the two also confirms that the thesis is measuring broader disclosure posture rather than only climate topicality.

For RQ4, the answer is yes: disagreement, missing labels, and schema fragility reveal important weaknesses in the extraction pipeline and in the current taxonomy fit. The presence of `61` missing-tone records, especially around governance-like disclosures, shows that the system is capable of surfacing its own limitations. This is analytically valuable because it turns failure into evidence for refinement.

For RQ5, the answer is yes: documentation and visualization practices can materially improve the auditability of ESG ABSA experiments. The current system already includes Streamlit pages, revision-analysis outputs, metric pages, prompt-stability summaries, static visualizations, and Mermaid-based documentation. These artifacts make the research process inspectable and reproducible in a way that a single model notebook would not.

For RQ6, the answer is that model and prompt choice clearly affect structured extraction stability, but the current evidence supports a cautious rather than definitive conclusion. The system already measures prompt sensitivity, schema drift, and model-level differences, but some cross-model comparisons remain confounded because not all models processed the same documents under the same prompt conditions. The research question is therefore partially answered in methodological terms, but still requires more controlled matched experiments for strong causal comparison.

Overall, the combined findings demonstrate that automated tone-aware ESG disclosure analysis is feasible, useful, and methodologically rich, but still dependent on continued benchmark maturation and validation work before it can support stronger generalized claims.

## 6.2. Practical Implications

The practical implications of this thesis differ by stakeholder group. The system is designed not only as an academic exercise, but as a usable analytical environment for several audiences involved in ESG reporting, assessment, and oversight.

For ESG analysts, the main implication is efficiency with traceability. The pipeline reduces the burden of manually scanning long sustainability reports by extracting structured evidence records and surfacing patterns such as commitment dominance, missing outcomes, ontology coverage gaps, and governance-fragile rows. This does not eliminate the need for expert judgment, but it substantially improves evidence discovery and prioritization. Analysts can move more quickly from long-form reports to auditable candidate claims and can focus their manual effort on the most ambiguous or high-risk records.

For sustainability report authors and corporate reporting teams, the system provides a new form of feedback on disclosure quality. A tone-aware analysis can reveal whether a report is overly dominated by forward-looking commitments and under-supported by evidence of implemented action or measurable outcome. In practice, this could help authors improve the balance of their reporting by making the rhetorical structure of disclosures more visible. It could also help internal ESG teams identify sections where governance language is too procedural or too vague to map cleanly onto a structured evidence framework.

For regulators and standard-setting bodies, the thesis suggests a pathway toward scalable pre-screening of corporate sustainability narratives. A system like this could support review workflows under OJK-like or exchange-linked reporting environments by flagging:

- commitment-heavy sections with limited outcome evidence,
- disclosures with high schema ambiguity,
- governance sections that resist current tone categorization,
- and areas where claimed sustainability language is hard to align with structured ontology concepts.

The practical value here is not autonomous regulatory judgment. It is triage support. The system can help direct attention to potentially important sections before full expert review.

For investors and financial users of ESG disclosures, the system offers a structured supplement to traditional ESG ratings. Most external ratings compress broad disclosure environments into abstract scores. By contrast, a tone-aware record-level pipeline can expose how a company frames its sustainability narrative, whether it emphasizes target-setting over achieved outcomes, and whether governance statements are mostly descriptive rather than substantive. This does not replace financial analysis or validated ESG ratings, but it can enrich them by adding a disclosure-structure lens.

More broadly, the thesis demonstrates that ESG NLP systems become more practically useful when they are designed as evidence workspaces rather than opaque classifiers. The combination of extraction, dashboards, review queues, and documentation increases the chance that the outputs can be trusted, challenged, and improved in real-world use.

## 6.3. Future Work

Although the current thesis demonstrates a working and meaningful ESG ABSA framework, several important next steps remain. These future directions are not marginal extensions; they are the most direct path toward strengthening the empirical and practical value of the system.

The first priority is the creation of a larger expert-labeled ground truth with explicit inter-annotator agreement. This is the most important next step because it will allow the system to move from exploratory and proxy evaluation toward fully defensible supervised benchmarking. A stronger annotation campaign should include stratified coverage across tone classes, ESG pillars, prompts, languages, and source documents. It should also record reviewer disagreement, adjudication decisions, and coverage metadata so that performance metrics can be interpreted rigorously.

The second priority is comprehensive OCR quality evaluation. The current methodology already recognizes OCR as a foundational risk, but the empirical layer remains incomplete until representative page samples are corrected and scored using metrics such as character error rate, word error rate, and table-extraction quality. This work would allow later experiments to separate model failure from source-text degradation more precisely.

The third priority is the validation of the greenwashing-oriented rhetoric-to-results index. At present, the index is a useful heuristic, but it remains interpretive. Future work should compare the index with external benchmarks such as controversy datasets, enforcement actions, third-party ESG controversy signals, or known high-profile mismatch cases. This would clarify whether commitment-to-outcome imbalance is only a descriptive signal or also a predictive one.

The fourth priority is ontology expansion, especially for Indonesian-specific ESG disclosure language and underrepresented social topics. The current ontology infrastructure is useful, but it remains incomplete. Future work should enlarge the lexicon and path structure to cover more locally meaningful governance and social disclosure concepts, Indonesian regulatory phrasing, and sector-specific sustainability terminology. This would improve both interpretability and extraction fit.

The fifth priority is multilingual and domain-adapted model development. The current system already operates in a bilingual setting, but it relies heavily on prompt-based general-purpose or domain-adjacent models. A future stage could include fine-tuning multilingual transformers or compact LLMs on Indonesian-English ESG corpora, especially once higher-quality annotated data are available. This would make it possible to compare prompt-based extraction with more formal supervised or instruction-tuned alternatives.

The sixth priority is complete one-to-one ClimateBERT evaluation over the full extracted record set. At present, the ClimateBERT comparison is informative but only partially realized. Running ClimateBERT or compatible climate-domain classifiers across all current ESG records would make the external comparison more rigorous and would allow more precise analysis of where the tone taxonomy converges with or diverges from climate-domain semantics.

Beyond these six priorities, several additional future directions are also implied by the current repository. The semantic graph exports could be extended into knowledge-graph-driven retrieval systems. The prompt-stability framework could be expanded into ensemble or verifier-based extraction strategies. The governance-specific failure cases could motivate a revised or pillar-specific tone taxonomy. And the thesis-facing dashboard ecosystem could be adapted into a reusable research platform for broader ESG disclosure auditing beyond the current sample.

The overall future-work agenda therefore follows a clear logic: preserve the current executable workspace, strengthen the benchmark, tighten the validation layers, extend the ontology, and move from prototype-scale evidence to more rigorous comparative evaluation. If those steps are completed, the current system could evolve from a strong master’s thesis framework into a broader reusable research platform for ESG disclosure analytics in multilingual and emerging-market contexts.
