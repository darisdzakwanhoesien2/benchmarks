# Documentation: Feasibility of Multimodal Fact-Checking for Indonesian ESG ABSA

## 1. Research Gap

The current repository already provides ESG ABSA extraction from sustainability reports, OCR pipelines, ontology mapping, diagnostics, and thesis dashboards. However, a dedicated **fact-checking layer** across internal disclosure and external evidence is still missing, especially for Indonesian multimodal ESG contexts.

Main gaps are:

1. Current workflow focuses on extracting and classifying internal company disclosures, not verifying whether claims are supported or contradicted by external evidence.
2. Existing validation is mostly schema/label quality oriented (parse success, agreement metrics), not claim-level factual consistency testing.
3. External sources (news, social media, documentary/video transcripts, images) are not yet integrated into a unified evidence-retrieval and claim-verification pipeline.
4. Multimodal evidence reasoning (text + image + video) is not operationalized for ESG claim verification in Indonesian language settings.
5. There is no benchmark protocol for contradiction, support, or unverifiable classification of ESG claims.

## 2. Research Questions

1. Can ESG claims extracted from internal sustainability reports be automatically fact-checked against external Indonesian multimodal evidence?
2. Which evidence type contributes most to verification quality: news text, social media text, documentary transcripts, images, or combined multimodal signals?
3. How well can a verification system classify each claim as `supported`, `contradicted`, or `insufficient_evidence`?
4. Does multimodal evidence aggregation improve fact-checking reliability over text-only verification?
5. What are the main failure modes in Indonesian ESG fact-checking (entity mismatch, temporal mismatch, sentiment-claim confusion, visual ambiguity, source credibility noise)?

## 3. Research Objectives

1. Build a reproducible fact-checking pipeline for Indonesian ESG ABSA claims.
2. Integrate internal claim extraction with external evidence retrieval across text, image, and video sources.
3. Design a multimodal verification framework that outputs support/contradict/insufficient verdicts with evidence provenance.
4. Evaluate verification performance with claim-level and evidence-level metrics.
5. Integrate fact-checking outputs into existing dashboards and chapter-level thesis evidence.

## 4. Research Contribution

This study can contribute:

1. A practical Indonesian ESG multimodal fact-checking architecture built on top of existing ABSA infrastructure.
2. A claim-centric benchmark linking internal disclosure claims to external evidence trails.
3. A reproducible protocol for multimodal ESG verification with provenance and uncertainty handling.
4. An expanded ESG reliability framework beyond sentiment/tone classification toward disclosure truthfulness assessment.
5. Reusable datasets/artifacts for future ESG misinformation and greenwashing-risk analysis.

## 5. Literature Review (Focused)

Relevant literature streams:

1. **Automated fact-checking and claim verification**: retrieval + stance/verdict classification pipelines.
2. **Natural language inference (NLI) for verification**: textual entailment/contradiction methods for claim-evidence reasoning.
3. **Multimodal fact-checking**: combining text, image, and video cues for consistency analysis.
4. **ESG and greenwashing analysis**: reliability of voluntary disclosures and external accountability signals.
5. **Source reliability and trust modeling**: handling noisy social media and heterogeneous evidence credibility.
6. **Low-resource/multilingual verification**: Indonesian language challenges in entity linking, code-switching, and domain vocabulary.

For this repository, literature should support a critical principle: fact-checking outputs must be traceable to explicit evidence and timestamps, not only generated verdict text.

## 6. Methodology

### 6.1 Existing Infrastructure to Reuse

Existing components that can be leveraged:

1. Internal disclosure extraction
   - `pages/Bulk_OCR.py`
   - `pages/llm_processing.py`
   - `results/esg_records.json`
2. Verification and provenance support
   - `pages/2_2_LLM_Statement_Page_Verifier.py`
   - `pages/2_1_LLM_Error_Parse_Audit.py`
3. ABSA/ontology layer
   - `pages/1_6_Ontology_Path_Viewer.py`
   - `code/lexicons.py`
4. Workflow and chapter integration
   - `pages/1_7_Research_Questions_Dashboard.py`
   - Chapter pages under `pages/6_x_*.py`

### 6.2 Data Scope and Claim Unit

1. Internal claim source:
   - statements extracted from sustainability reports via existing ABSA pipeline.
2. External evidence source:
   - news articles,
   - social media posts,
   - documentary/video transcripts,
   - image evidence (charts, infographics, photos where relevant).
3. Standard claim schema:
   - `claim_id`,
   - `company`,
   - `claim_text`,
   - `claim_type` (commitment/action/outcome),
   - `esg_pillar`,
   - `aspect`,
   - `time_reference`,
   - `source_page_ref`.

### 6.3 Multimodal Fact-Checking Pipeline

1. **Claim extraction and normalization**
   - extract candidate factual claims from internal ABSA records.
2. **Evidence retrieval**
   - text retrieval for news/social posts,
   - transcript retrieval for video/documentary,
   - image retrieval and OCR/caption extraction for visual evidence.
3. **Evidence ranking and filtering**
   - relevance scoring,
   - date filtering,
   - entity disambiguation,
   - source credibility weighting.
4. **Verification reasoning**
   - text-NLI style support/contradict checks,
   - multimodal fusion for text+image+video evidence,
   - uncertainty tagging for ambiguous evidence.
5. **Verdict generation**
   - `supported`, `contradicted`, `insufficient_evidence`,
   - confidence score,
   - cited evidence bundle.

### 6.4 Evaluation Framework

1. Claim-level metrics:
   - accuracy/F1 for verdict classification,
   - macro F1 across `supported/contradicted/insufficient`.
2. Evidence-level metrics:
   - precision@k / recall@k retrieval relevance,
   - citation correctness,
   - provenance completeness.
3. Multimodality ablation:
   - text-only vs text+image vs text+video vs full multimodal.
4. Robustness checks:
   - temporal drift,
   - sector-specific vocabulary,
   - noisy social-media evidence.
5. Human adjudication subset:
   - expert/manual check on sampled claims to calibrate automated verdicts.

### 6.5 Integration Plan in This Repository

1. Add fact-checking module(s), e.g.:
   - `code/fact_checking_esg.py` (claim + verdict pipeline),
   - optional `code/multimodal_evidence_retriever.py`.
2. Save outputs under `results/fact_checking/`:
   - claims table,
   - retrieved evidence table,
   - verdict table,
   - ablation/evaluation reports.
3. Add Streamlit page (e.g., `pages/2_9_Fact_Checking_ESG_ABSA.py`) with:
   - claim list,
   - verdict summary,
   - evidence cards (text/image/video),
   - contradiction dashboard.
4. Connect outputs to research-question and chapter pages.

## 7. Expected Results

With current repository maturity, expected outcomes are:

1. Internal ESG claims can be mapped to external evidence with usable retrieval quality.
2. Multimodal verification improves contradiction detection for claims where text-only signals are incomplete.
3. Action/outcome claims are generally easier to verify than broad commitment claims.
4. Social media evidence increases coverage but may reduce reliability without credibility weighting.
5. Fact-checking outputs expose high-risk claim clusters useful for greenwashing-oriented analysis.

## 8. Discussion

Key discussion points:

1. **Value extension**: the system evolves from extraction/classification into disclosure reliability assessment.
2. **Multimodal benefit**: image/video evidence can resolve cases that text alone cannot.
3. **Method risk**: weak entity resolution, date mismatch, and source noise can produce false contradictions.
4. **Governance implication**: verified evidence trails improve transparency for ESG stakeholders.
5. **Research implication**: combining ABSA + multimodal fact-checking provides stronger empirical grounding for thesis claims.

## 9. Conclusion

Multimodal fact-checking for Indonesian ESG ABSA is feasible in this repository because core prerequisites already exist: internal claim extraction, provenance utilities, ontology structure, and dashboard integration. The main implementation requirement is adding external evidence ingestion, multimodal retrieval, and verdict evaluation. The expected contribution is a reproducible claim-verification layer that strengthens ESG disclosure analysis beyond sentiment/tone into factual accountability.

---

## Suggested Next Implementation Steps

1. Define a canonical claim schema derived from `results/esg_records.json`.
2. Implement external evidence ingestion connectors (news, social media, documentary transcripts, images).
3. Build `results/fact_checking/` with retrieval/verdict/evaluation artifacts.
4. Add Streamlit fact-checking dashboard with claim-level evidence audit and multimodal ablation views.
