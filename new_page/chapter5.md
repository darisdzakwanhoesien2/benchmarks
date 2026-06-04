# Chapter 5: Discussion

## 5.1. Comparison with Existing Methods

The results presented in Chapter 4 show that the current ESG ABSA system should not be interpreted as a narrow classifier alone. It is better understood as an executable research workspace that combines document processing, structured extraction, tone-aware categorization, comparison modeling, ontology alignment, and reproducibility-oriented audit tooling. For that reason, the most appropriate discussion strategy is not simply to ask whether the current system is “better” than one baseline on one metric. Instead, it is necessary to compare the system with several alternative approaches that solve adjacent parts of the ESG disclosure problem but do not address the full research scope of this thesis.

Four comparison points are especially important:

1. manual ESG scoring and manual reading workflows;
2. pure LLM classification or extraction without audit scaffolding;
3. ClimateBERT-only or climate-domain-only approaches;
4. rule-based ESG taxonomies and deterministic lexicon systems.

Each of these alternatives captures part of the problem. None of them fully addresses the combined challenges of bilingual ESG disclosure extraction, tone-aware interpretation, provenance preservation, benchmark construction, and thesis-grade reproducibility. The present system should therefore be interpreted as an integration-oriented contribution rather than a single-task replacement model.

### 5.1.1. Manual ESG Scoring and Manual Review

Manual ESG assessment remains the most interpretable and context-sensitive alternative. Human reviewers can read long disclosures carefully, recognize nuance, distinguish between rhetorical commitment and measurable outcome, and resolve ambiguities that automated systems may misclassify. In a high-stakes context such as regulatory review or investment due diligence, manual assessment is often treated as the gold standard precisely because it allows contextual interpretation and explicit justification.

However, manual review does not scale well. Sustainability reports are long, heterogeneous, and often repetitive. Cross-document comparison becomes costly, and reproducibility is difficult when multiple reviewers infer categories from long narrative passages without a standardized record schema. Manual review is also weak in terms of structured artifact generation. A human reader may reach a good judgment, but unless that judgment is captured in a formal record-level format with provenance and label definitions, it becomes difficult to reuse the assessment in downstream analytics, dashboards, or graph representations.

The current system adds three important capabilities relative to manual-only review. First, it transforms PDF disclosures into record-level evidence units that can be compared systematically across documents and runs. Second, it distinguishes tone categories such as commitment, action, and outcome in a way that can be operationalized quantitatively. Third, it preserves audit trails through files, dashboards, and metadata. In other words, the system does not replace human judgment; it restructures the evidence so that human judgment can be applied more efficiently and more reproducibly.

From this perspective, the thesis contribution is not to claim that automation is always more accurate than humans. Rather, it shows that structured automation can reduce the cost of evidence discovery, expose hidden distributional patterns, and create a foundation for human-in-the-loop validation. This is especially valuable in ESG disclosure analysis, where interpretive scale and documentation quality are as important as raw classification performance.

### 5.1.2. Pure LLM Classification or Extraction

The second comparison point is pure LLM extraction without the layered controls implemented in this thesis. A direct prompt-to-output workflow is attractive because it is fast, flexible, and capable of capturing nuanced language patterns without supervised training. In practice, many contemporary applied NLP systems rely heavily on this paradigm: provide a prompt, obtain a structured-looking response, and treat the resulting JSON or table as the final analytical output.

The results in this repository show why that approach is insufficient for the current research problem if used in isolation. LLM outputs are highly sensitive to prompt formulation, context size, provider behavior, and parsing assumptions. A pure LLM workflow can therefore produce apparently coherent results while hiding structural fragility. Empty outputs, malformed JSON, field drift, prompt-specific label variation, and run failures may disappear from view if the system only reports records that parse successfully.

The present thesis adds methodological controls precisely in response to that problem. Instead of treating LLM output as self-justifying, it introduces:

- run-level logging,
- parse-audit tooling,
- prompt-stability summaries,
- model-stability summaries,
- disagreement review,
- and benchmark-construction scaffolding.

This changes the epistemic status of the LLM output. The output is no longer simply accepted as a prediction. It becomes an inspectable artifact whose structural reliability can be measured and whose failures can be categorized.

This is one of the most important differences between the current system and a pure LLM baseline. The repository already shows that the system can identify missing tones, schema drift, empty prompt outputs, and recoverable failures. A pure extraction workflow would likely report only the 332 structured records and understate the instability behind them. The current system instead makes that instability part of the research evidence.

Therefore, compared with pure LLM extraction, the thesis contribution is not only semantic flexibility. It is methodological discipline. The system treats generation quality, parse reliability, and prompt sensitivity as experimental variables rather than hidden implementation noise. This makes the results less superficially clean, but more scientifically defensible.

### 5.1.3. ClimateBERT-Only Approaches

The third comparison point is ClimateBERT-only or climate-domain-only NLP. ClimateBERT-like models are valuable because they are specialized for climate-related language and often perform well on climate disclosure or net-zero related tasks. They provide a meaningful external signal for whether extracted text is climate-relevant, commitment-oriented, or semantically aligned with climate discourse.

However, the current results also clarify the limits of a ClimateBERT-only approach. The ESG disclosure problem addressed by this thesis is broader than climate classification. The dataset includes environmental, governance, and highly sparse social disclosures; it also distinguishes among commitment, action, and outcome as disclosure postures rather than simply asking whether text is climate-related.

This difference matters because tone and climate relevance are not identical constructs. A statement can be climate-related but not necessarily a commitment. A governance statement may be highly relevant to ESG disclosure quality while being outside the conceptual comfort zone of a climate-domain model. The current proxy agreement figures, `0.837` agreement and `0.645` kappa, are therefore best interpreted as positive but partial evidence. They show that the thesis taxonomy overlaps meaningfully with climate-domain semantics, but they also confirm that the two labeling systems should not be collapsed into one another.

The present system adds value beyond ClimateBERT-only approaches in three ways. First, it extends analysis beyond climate-specific text into a broader ESG record schema. Second, it incorporates tone categories that are more directly suited to greenwashing-oriented interpretation. Third, it exposes disagreement between taxonomies as an analytical resource rather than treating disagreement as a failure by default.

This last point is especially important. In the current project, divergence between ESG tone labels and ClimateBERT-style labels is not automatically an error. It can indicate a genuine construct mismatch, for example where governance disclosures do not fit environmental commitment language well. That makes the system useful not only for prediction, but for theoretical interpretation of what different labeling schemes are actually measuring.

### 5.1.4. Rule-Based ESG Taxonomies and Lexicon Systems

The fourth comparison point is deterministic rule-based or lexicon-based ESG analysis. Such systems are attractive because they are transparent, cheap to run, and straightforward to explain. A rule-based ESG taxonomy can map known keywords or phrases to pillars, aspects, or regulatory themes with minimal infrastructural complexity.

The limitations of such systems are especially apparent in the current thesis context. Bilingual ESG disclosure language is highly variable, often implicit, and strongly shaped by document genre. The same commitment may be expressed through explicit targets, narrative aspiration, passive formulations, or blended Indonesian-English phrasing. Deterministic systems struggle under these conditions because they rely on stable lexical cues and have difficulty distinguishing surface similarity from functional meaning.

That does not make rule-based systems useless. On the contrary, the methodology in Chapter 3 already showed why rule-like logic remains valuable for schema normalization, aspect scaffolding, and explainability. But the current results suggest that deterministic taxonomies are not sufficient as stand-alone solutions. They are better used as one layer within a hybrid system than as the sole analytical engine.

The present system improves on rule-only approaches by combining flexibility and structure. LLM extraction captures semantically rich ESG statements that a fixed lexicon may miss, while the surrounding dashboards and ontology layers preserve enough structure for interpretation. This hybrid logic is especially important for record-level tone classification, where disclosure meaning depends on whether a statement expresses intention, implementation, or realized result rather than only whether it contains a familiar ESG keyword.

### 5.1.5. What the Current System Adds

Across these four alternatives, the main value added by the thesis system can be summarized as follows:

- It scales beyond manual reading while preserving room for human validation.
- It is more disciplined than pure LLM extraction because it measures structural failure and prompt sensitivity.
- It is broader than ClimateBERT-only pipelines because it covers non-climate ESG disclosures and explicit tone categories.
- It is more flexible than rule-only taxonomies because it can capture semantically varied, bilingual, and context-dependent disclosure language.

The system therefore contributes not merely a classifier, but an integrated evidence-construction environment built around structured ESG evidence records. This is important because the ESG disclosure problem is not only a prediction problem. It is also a provenance problem, a benchmark problem, and an interpretability problem. The current implementation addresses all four more directly than the comparison methods above.

## 5.2. Interpretation of Key Findings

The experimental results reported in Chapter 4 are meaningful not simply because they produce structured outputs, but because the structure of those outputs reveals patterns about Indonesian ESG disclosure itself and about the behavior of the extraction pipeline. Three findings are especially important for interpretation:

1. the dominance of commitment tone in the current corpus;
2. the substantial alignment between commitment tone and ClimateBERT-style climate-commitment labels;
3. the concentration of missing tone and schema-fragile records in governance-oriented disclosures.

These findings should be interpreted carefully. They do not yet justify broad population-level claims about all Indonesian sustainability reporting. However, they do provide plausible, theory-relevant signals about disclosure posture, model behavior, and where current taxonomies fit or fail.

### 5.2.1. Commitment Tone Dominance

One of the clearest current findings is that commitment appears as the dominant disclosure posture in the extracted record set. The planning notes already frame this in numeric terms as `115` commitment records out of `332` structured records, making commitment the largest tone class in the current dataset.

This pattern is important because it suggests that many ESG disclosures in the current corpus are framed prospectively rather than evidentially. In other words, companies often present what they intend to do, plan to support, or aim to improve, rather than emphasizing already realized outcomes. This does not automatically imply strategic misrepresentation or greenwashing. A commitment statement may be entirely legitimate, especially in sustainability transitions that depend on long-term targets and staged implementation. However, a commitment-dominant corpus does indicate that future-facing rhetoric is structurally central to the reporting style represented in the current dataset.

This interpretation also helps explain why tone is analytically useful beyond generic sentiment. A commitment statement may be positive in emotional or evaluative wording, but its substantive meaning differs from an outcome statement that reports realized change. The commitment dominance therefore supports the thesis argument that ESG disclosure analysis should distinguish posture from polarity. Sentiment alone cannot capture the difference between “we intend to reduce emissions” and “we reduced emissions by 20 percent.”

From a system perspective, the dominance of commitment tone also has methodological implications. It means the corpus is imbalanced by disclosure posture, which affects evaluation, prompt behavior, and comparison metrics. A model that performs reasonably well on commitment-heavy data may still fail on outcome or governance-specific cases. Therefore, commitment dominance is both a substantive result and a source of evaluation caution.

### 5.2.2. Alignment with Climate-Commitment Labels

The second major finding concerns the substantial overlap between commitment tone and ClimateBERT-style climate-commitment labels. The planning materials explicitly cite `91` co-occurrences between commitment tone and climate-commitment. This is one of the most encouraging results in the current system because it suggests that the thesis taxonomy is not arbitrarily assigning commitment labels. Instead, it appears to be tracking a meaningful subset of climate-oriented forward-looking disclosure language.

This alignment is important for two reasons. First, it provides a form of construct support. The ESG tone taxonomy and ClimateBERT-style labels are not identical, yet their overlap implies that the tone system is capturing recognizable climate-disclosure semantics. Second, it shows that record-level tone analysis can complement rather than replace domain-specific climate classification. The two views are related, but they illuminate different aspects of the same disclosure evidence.

At the same time, the alignment should not be oversimplified. ClimateBERT-style labels focus on climate-oriented meaning, whereas the thesis tone taxonomy is broader and includes governance and generalized ESG rhetoric. Therefore, strong overlap for commitment does not imply that the whole ESG tone system is validated externally. It means that one important part of the taxonomy behaves plausibly under external comparison.

This is still a valuable result because it shows that the thesis pipeline is not disconnected from the state of the art. It is anchored to an externally meaningful semantic signal while preserving its own broader interpretive framework.

### 5.2.3. Missing Tone and Governance Fragility

The third major finding concerns the concentration of missing tone and schema-fragile cases in governance-like text. The Chapter 4 notes already identify `61` missing tone records and highlight governance disclosures as an area where the tone taxonomy fits less cleanly. This is one of the most revealing results in the project because it exposes the limits of transferring an environmental or climate-oriented tone logic into broader corporate disclosure language.

Governance text often differs stylistically from environmental disclosure. It may be procedural, legalistic, risk-oriented, or structurally descriptive rather than aspirational or outcome-centered. Statements about boards, risk management, dividend recognition, control systems, or compliance procedures may not naturally fit the commitment-action-outcome framing. As a result, the model may either assign missing tone, force an ill-fitting category, or produce structurally unstable outputs.

This finding matters for both theory and system design. Substantively, it suggests that not all ESG pillars behave the same way under a unified tone taxonomy. Methodologically, it shows where the taxonomy needs refinement and where benchmark design must pay attention to category fit rather than only model accuracy. A missing tone in governance text may reflect a model failure, but it may also reflect a conceptual tension between the tone schema and the linguistic style of governance reporting.

This is precisely the kind of result that justifies the thesis’s broader methodological framing. A narrower pipeline might have simply discarded those rows. The present system surfaces them as evidence, making it possible to discuss whether the taxonomy itself should be adapted for governance-heavy corpora.

### 5.2.4. Overall Interpretation

Taken together, these three findings suggest that the current ESG ABSA system is capturing a real but uneven disclosure structure. It performs most coherently where future-oriented environmental or climate-adjacent rhetoric is prominent. It becomes more fragile when reporting language shifts toward governance procedure, descriptive finance language, or schema-atypical text.

This unevenness should not be read only as a weakness. It is also a substantive insight into disclosure heterogeneity. The system reveals that tone-aware ESG analysis is both feasible and non-uniform: some discourse types align naturally with the taxonomy, while others expose where the taxonomy and the models require further development.

## 5.3. Theoretical Implications

The findings of this thesis can be connected to several theoretical perspectives that help explain why the observed patterns matter beyond system implementation. Four frameworks are especially useful here:

1. legitimacy theory;
2. stakeholder theory;
3. ABSA theory and fine-grained sentiment analysis;
4. greenwashing-oriented disclosure theory.

These frameworks do not merely decorate the technical results. They help explain why the dominance of commitment language, the unevenness across ESG pillars, and the distinction between tone and sentiment are theoretically meaningful.

### 5.3.1. Legitimacy Theory

Legitimacy theory suggests that organizations disclose social and environmental information partly to maintain, restore, or enhance their perceived legitimacy in the eyes of external audiences. From this perspective, the dominance of commitment-oriented disclosure in the current corpus is consistent with a legitimacy-seeking communication style. Companies may emphasize intentions, pledges, and directional aspirations because these forms of language are effective for signaling alignment with expected sustainability norms, even when outcome evidence is less developed or more difficult to measure.

The present results do not prove illegitimacy or manipulation. However, they do show that the discourse structure of the current ESG record set is strongly future-facing. This supports a legitimacy-theory interpretation in which disclosure functions partly as a signaling mechanism. The tone taxonomy makes this visible in a way that generic sentiment analysis would not. A positive sentiment score cannot distinguish between an organization claiming that it plans to act and an organization reporting that it has already delivered measurable outcomes.

This is one of the most important theoretical contributions of the thesis. By separating commitment from outcome, the system operationalizes a distinction that legitimacy theory implies but does not automatically quantify.

### 5.3.2. Stakeholder Theory

Stakeholder theory provides a second useful lens. It suggests that disclosure content reflects the information demands of key stakeholder groups, including investors, regulators, civil society actors, and governance monitors. The current project notes frame the pillar distribution as strongly concentrated in environmental and governance categories, with very sparse social representation. This pattern suggests that the current corpus may be more responsive to stakeholder pressures around environmental performance and governance assurance than to social-impact detail.

Such a pattern is plausible in a disclosure environment where climate, emissions, governance processes, and formal risk language receive more institutional attention than diffuse or harder-to-standardize social issues. If so, the current ESG ABSA results do more than describe model output; they reveal how disclosure salience may be shaped by stakeholder demand structures.

This interpretation also explains why governance text creates challenges for tone classification. Governance disclosure often serves assurance and compliance functions rather than public aspiration or impact narration. It is therefore plausible that stakeholder-oriented governance language diverges from the narrative forms that the commitment-action-outcome taxonomy handles most naturally.

### 5.3.3. ABSA Theory and the Tone-Sentiment Distinction

A third implication concerns ABSA itself. Traditional sentiment analysis often treats polarity as the primary explanatory variable: positive, negative, or neutral sentiment toward an aspect. The current thesis shows why that is insufficient for ESG disclosure. The difference between commitment, action, and outcome demonstrates that aspect and polarity do not exhaust the meaning structure of corporate sustainability statements.

This is theoretically significant because it extends ABSA from evaluative sentiment toward disclosure posture. In other words, the thesis suggests that for ESG reporting, one must often ask not only “what aspect is being discussed?” and “is the statement positive or negative?” but also “what kind of claim is being made?” The tone dimension captures whether a statement reports intention, implementation, or realized effect. This moves the analytical unit closer to how disclosure is used in governance, sustainability assessment, and rhetorical signaling.

The current results therefore support an expansionist view of ABSA in ESG contexts. Fine-grained analysis should include disclosure posture as a first-class variable alongside aspect and sentiment. This is especially important in domains where organizations may communicate strategically rather than descriptively.

### 5.3.4. Greenwashing Theory

The fourth implication concerns greenwashing-oriented interpretation. Greenwashing theory is concerned with mismatches between sustainability rhetoric and demonstrable practice. The current system does not claim to solve greenwashing detection conclusively. However, the commitment-to-outcome imbalance and the greenwashing-oriented index implemented in the revision analytics page show that tone-aware extraction can operationalize one dimension of rhetorical asymmetry.

This matters theoretically because many discussions of greenwashing remain qualitative or case-specific. The present thesis suggests a pathway toward a more structured computational indicator: if disclosure records can be categorized by posture, then one can begin to quantify whether a document or company relies disproportionately on future-facing claims relative to achieved results.

The current implementation does not yet validate this index against external controversy data or regulatory outcomes. Therefore, the discussion must remain careful. Still, the theoretical implication is important: tone-aware ABSA creates a bridge between disclosure language analysis and greenwashing-oriented risk heuristics. This is a meaningful step beyond sentiment-only ESG NLP.

### 5.3.5. Integrated Theoretical Reading

Taken together, these frameworks suggest that the current findings are not isolated technical curiosities. They point toward a larger interpretation:

- commitment-heavy ESG disclosure can be read as a legitimacy signal,
- pillar imbalances reflect stakeholder-driven disclosure priorities,
- tone-aware ABSA extends sentiment theory toward disclosure posture,
- and commitment-outcome asymmetry creates a computationally tractable entry point into greenwashing research.

This integrated reading strengthens the thesis contribution because it shows that the system’s categories are not arbitrary engineering choices. They correspond to meaningful theoretical distinctions in sustainability communication.

## 5.4. Limitations

The results of this thesis are promising, but they remain subject to several important limitations. These limitations do not invalidate the contribution. Rather, they define the scope within which the findings should be interpreted and indicate where further work is required before stronger empirical claims can be made.

### 5.4.1. No Full Expert-Labeled Ground Truth

The most important limitation is that the current corpus does not yet contain a complete expert-labeled benchmark. The 332 structured ESG records are useful for exploratory analysis, proxy validation, and benchmark construction, but they do not yet constitute a fully human-validated evaluation dataset. As a result, many current findings are best interpreted as implementation-grounded or proxy-grounded rather than final supervised performance claims.

This limitation affects how metrics should be discussed. Accuracy, precision, recall, F1, and kappa are fully meaningful only when the underlying reference labels are sufficiently complete and representative. The current system is well prepared for such evaluation, but the benchmark itself is still under construction.

### 5.4.2. Weak Labels and Limited ClimateBERT Coverage

The second major limitation concerns weak supervision and partial external validation. The current project already uses silver labels and ClimateBERT proxy comparison productively, but these remain intermediate evidence sources rather than definitive truth. In particular, the repository notes explicitly indicate that the current real ClimateBERT remote sample is small and cannot stand in for a one-to-one benchmark over the full record set.

This means that the reported ClimateBERT proxy agreement and kappa values should be read as construct-support evidence, not as final external-validation scores. The same caution applies to silver labels: they are useful for scaffolding and review prioritization, but they cannot fully replace expert annotation.

### 5.4.3. OCR Quality Is Not Yet Fully Quantified

The third limitation is that OCR quality, although recognized as important throughout the methodology, has not yet been quantified comprehensively with formal CER/WER reporting across representative page types. Because OCR is the first transformation stage in the pipeline, this matters a great deal. If OCR quality is uneven, then some downstream extraction failures may reflect source distortion rather than model weakness.

The current repository already contains the tools needed to address this problem, especially through OCR-quality workbench pages and page-processing audits. However, until a representative sample is manually corrected and measured, OCR remains an acknowledged but only partially quantified source of uncertainty.

### 5.4.4. Prompt Sensitivity and Cross-Model Confounds

The fourth limitation concerns the instability inherent in LLM-based structured extraction. The project already improves on naive LLM use by measuring prompt-stability and model-stability artifacts, but this does not eliminate the underlying problem. Different prompt templates yield different record distributions, different field completion patterns, and different rates of missing tone or schema drift.

In addition, the current cross-model comparison is not yet perfectly controlled. Some of the repository’s benchmark notes explicitly caution that models did not always process the same documents under the same prompt conditions. This means some model-comparison findings are suggestive rather than causal. The system is strong enough to reveal this confound, but not yet strong enough to eliminate it retroactively.

### 5.4.5. Greenwashing Index Is Heuristic

The fifth limitation concerns the greenwashing-oriented rhetoric-to-results index. The current implementation provides an analytically interesting screening measure, but it has not yet been validated against external outcomes such as controversy datasets, regulatory findings, or independent ESG quality indicators. Therefore, it should not be interpreted as a proven greenwashing detector.

Its current value lies in hypothesis generation and comparative screening. It helps identify cases where commitment language appears to dominate outcome language, but it cannot by itself determine whether a company is misleading stakeholders.

### 5.4.6. Ontology Scope and Social-Pillar Sparsity

The sixth limitation concerns ontology scope and dataset coverage. The current ontology and aspect mapping infrastructure already supports useful interpretation, but it may not yet capture the full range of Indonesian-specific ESG disclosure language. This is especially relevant for social disclosures, which appear severely underrepresented in the current extracted record set.

Sparse social coverage has two effects. Substantively, it weakens any broad conclusions about S-pillar discourse. Methodologically, it makes it harder to know whether the sparsity reflects real disclosure patterns, extraction bias, ontology gaps, or a combination of all three.

### 5.4.7. Overall Limitation Boundary

Taken together, these limitations define a clear boundary for the thesis claims. The current system is strong as:

- an executable ESG ABSA prototype,
- a record-level disclosure analysis framework,
- a benchmark-construction environment,
- and a reproducibility-oriented audit platform.

It is weaker as:

- a finalized supervised benchmark,
- a definitive cross-model comparison study,
- a fully validated greenwashing detector,
- and a complete representation of all ESG pillar variation.

This boundary should not be treated as a failure. It is the realistic condition of a complex research system that has progressed far enough to expose its own weaknesses in a structured way. That self-diagnostic capability is itself part of the contribution.
