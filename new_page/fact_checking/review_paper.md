# Review Paper: Automated and Multimodal Fact-Checking for Indonesian ESG Claim Verification

Date: 2026-05-30

## Abstract

Automated fact-checking (AFC) has matured into a modular pipeline that typically includes claim identification/normalization, evidence retrieval, claim–evidence reasoning, and verdict generation with provenance. Recent benchmarks (e.g., FEVER) operationalize evidence-based verification in large-scale settings, while newer datasets and shared tasks extend AFC to real-world claims, multilingual scenarios, and multimodal evidence (image, video, audio). Despite this progress, applying AFC to sustainability reporting—especially Indonesian ESG disclosures—raises additional challenges: claim vagueness and hedging, strong dependence on temporal context, entity ambiguity (subsidiaries/brand names), and the need for credibility-aware evidence ranking across heterogeneous sources. This review synthesizes key datasets, methods, evaluation protocols, and open challenges across textual and multimodal fact-checking, and then maps these findings into a concrete research agenda for a provenance-first Indonesian ESG claim verification system. The paper emphasizes (i) separating retrieval quality from reasoning quality, (ii) treating “insufficient evidence” as distinct from “false,” and (iii) measuring citation fidelity as a first-class metric to ensure auditability.

## Keywords

automated fact-checking; claim verification; evidence retrieval; natural language inference; multimodal verification; credibility modeling; ESG; Indonesia; provenance; citation fidelity

---

## 1. Introduction

Fact-checking is central to combating misinformation and improving accountability in public discourse. In ESG disclosure analysis, the stakes are practical: companies can make broad or selectively framed claims (e.g., “reduced emissions,” “improved community outcomes”) that are difficult for stakeholders to verify without explicit evidence trails. Traditional NLP analyses of sustainability reports frequently focus on readability, sentiment, and boilerplate signals to detect potential greenwashing, but these signals do not directly establish whether a disclosure is supported by external evidence (e.g., regulator announcements, credible news, or third-party assessments) (e.g., tone/readability framing in sustainability reporting studies such as the multi-dimensional textual framework for detecting greenwashing) (Springer Discover Sustainability paper: https://link.springer.com/article/10.1007/s43621-026-02890-x).

Automated fact-checking (AFC) systems aim to (1) identify check-worthy claims, (2) retrieve relevant evidence, and (3) determine whether that evidence supports, contradicts, or is insufficient to judge the claim. Comprehensive AFC surveys highlight the modular pipeline design and the broad set of challenges (e.g., evidence retrieval, reasoning, and the limits of available supervision) (Guo et al., “A Survey on Automated Fact-Checking,” TACL 2022: https://transacl.org/index.php/tacl/article/view/3509). In parallel, large-scale benchmarks have been introduced for evidence-based claim verification, such as FEVER (Thorne et al., 2018: https://aclanthology.org/N18-1074.pdf) and LIAR (Wang, 2017: https://aclanthology.org/P17-2067/), as well as multi-domain datasets such as MultiFC (2019: https://arxiv.org/abs/1909.03242).

More recently, the evidence landscape has become multimodal and multilingual: social media and web claims often combine text with images, videos, and audio. This has motivated multimodal verification datasets and methods, including VERITE (a bias-aware image–text verification benchmark: https://arxiv.org/abs/2304.14133 and Springer version: https://link.springer.com/article/10.1007/s13735-023-00312-6), multimodal end-to-end datasets such as MOCHEG (https://arxiv.org/abs/2205.12487), and multimodal systems such as MAFT (textualization-based multimodal fact-checking; AAAI: https://ojs.aaai.org/index.php/AAAI/article/view/35354).

This review targets two goals:

1. Provide a structured synthesis of AFC methods and benchmarks (textual and multimodal).
2. Translate that synthesis into a research plan for Indonesian ESG claim verification, emphasizing provenance, temporal control, and credibility-aware evidence selection.

---

## 2. Problem Formulation and Terminology

### 2.1 Claim Types and Verifiability

In applied settings (including ESG), not all “claims” are equally verifiable. A useful distinction is:

- **Outcome claims** (measurable past/present outcomes; most falsifiable): e.g., “We reduced CO₂ emissions by 20% in 2023.”
- **Action claims** (actions taken; often verifiable via announcements or audits): e.g., “We installed solar panels at Plant X.”
- **Commitment claims** (future intent; weakly falsifiable): e.g., “We aim to reach net-zero by 2050.”

This distinction matters for label design and evaluation. A commitment claim may be judged “unsupported” simply because it is aspirational, not because it is false. Therefore, claim verification pipelines need explicit treatment of verifiability and time alignment.

### 2.2 Evidence-Based Verdict Labels

Many evidence-based fact-checking tasks use labels aligned with:

- **Supported / Entailed**
- **Refuted / Contradicted**
- **Not enough information / Insufficient evidence**

FEVER formalized this tri-label scheme at scale for Wikipedia evidence (Thorne et al., 2018: https://aclanthology.org/N18-1074.pdf). Multimodal end-to-end datasets also adopt similar tri-label verdicts with a retrieval stage (e.g., MOCHEG: https://arxiv.org/abs/2205.12487).

### 2.3 Provenance and Citation Fidelity

For ESG accountability, a verdict without an evidence trail is low utility. Two provenance dimensions should be separated:

1. **Internal provenance**: where in the report the claim originated (document id + page reference + extracted snippet).
2. **External provenance**: URLs, dates, and excerpts of evidence used to verify the claim.

Citation fidelity is the requirement that cited evidence actually supports the verdict (and is not unrelated or temporally mismatched). Surveys emphasize the need for traceable evidence rather than fluent explanations (Guo et al., 2022: https://transacl.org/index.php/tacl/article/view/3509).

---

## 3. Taxonomy of Automated Fact-Checking Pipelines

Most AFC systems can be organized into a modular pipeline, which is also reflected in shared task designs such as CLEF CheckThat! (e.g., overview papers for CheckThat! 2019/2020/2025: https://arxiv.org/abs/2109.15118, https://arxiv.org/abs/2007.07997, https://arxiv.org/abs/2503.14828).

### 3.1 Claim Detection and Checkworthiness

The first stage identifies what should be checked: not every sentence is check-worthy. Shared tasks explicitly include checkworthiness estimation as a separate subtask (CheckThat! 2019 overview: https://arxiv.org/abs/2109.15118; CheckThat! 2020 overview: https://arxiv.org/abs/2007.07997).

Common modeling approaches include transformer encoders for checkworthiness classification and ranking, often leveraging debate/speech/social content structures. For ESG, claim detection is harder because reporting language can be long-form, templated, and hedged.

### 3.2 Evidence Retrieval and Ranking

Evidence retrieval typically uses a combination of:

- document retrieval (BM25, dense retrieval)
- passage/sentence retrieval
- reranking (cross-encoders)

In FEVER-like settings, retrieval is performed over a fixed corpus (e.g., Wikipedia). In real-world settings (web), retrieval is open-domain and requires careful time and source constraints.

### 3.3 Claim–Evidence Reasoning

Reasoning is often framed as:

- **NLI / textual entailment** between claim and evidence
- multi-sentence reasoning (aggregating evidence sentences)
- graph-based reasoning for multi-hop evidence chains

FEVER’s shared-task systems are examples of multi-sentence entailment for claim verification (e.g., UKP-Athene approach: referenced metadata exists via research indexes; FEVER paper and task reports discuss entailment-based methods and pipeline designs) (Thorne et al., 2018: https://aclanthology.org/N18-1074.pdf).

### 3.4 Explanation and Reporting

Real-world fact-checking demands human-readable outputs:

- verdict + confidence
- cited evidence excerpts
- rationale statement constrained to the cited evidence

Multimodal datasets such as MOCHEG explicitly include explanation generation alongside evidence retrieval and verdict prediction (MOCHEG: https://arxiv.org/abs/2205.12487).

---

## 4. Key Datasets and Benchmarks

### 4.1 Textual Claim Verification

**FEVER (2018)**: a large-scale dataset for evidence-based claim verification with a tri-label scheme and evidence annotation over Wikipedia (Thorne et al., 2018: https://aclanthology.org/N18-1074.pdf).

**LIAR (2017)**: a benchmark dataset for fake news detection based on PolitiFact statements with multi-class truthfulness labels (Wang, 2017: https://aclanthology.org/P17-2067/).

**MultiFC (2019)**: a real-world multi-domain dataset for evidence-based fact checking of claims (MultiFC arXiv: https://arxiv.org/abs/1909.03242).

**SciFact (2020)**: a dataset for verifying scientific claims using evidence from research abstracts with labels and rationales (Wadden et al., 2020; arXiv: https://arxiv.org/abs/2004.14974; ACL Anthology PDF: https://aclanthology.org/2020.emnlp-main.609.pdf).

These datasets differ in evidence source (Wikipedia vs web vs scientific abstracts), supervision type (rationales or not), and the extent to which they model open-domain retrieval.

### 4.2 Shared Tasks: CheckThat!

The CLEF CheckThat! lab provides a pipeline framing across tasks including checkworthiness, retrieving previously fact-checked claims, evidence retrieval, and claim verification (e.g., CheckThat! 2020 overview: https://arxiv.org/abs/2007.07997; CheckThat! 2019 overview: https://arxiv.org/abs/2109.15118). These tasks are useful for multilingual evaluation and for benchmarking systems as components rather than only end-to-end.

### 4.3 Multimodal Fact-Checking and Verification

The multimodal setting spans at least two related problems:

1. **Image–text consistency / out-of-context detection**: verify whether an image and accompanying text match.
2. **End-to-end multimodal fact-checking with web evidence**: retrieve evidence from mixed media and predict a veracity label.

Representative resources include:

- **VERITE (2023)**: an image–text verification benchmark designed to reduce unimodal bias and include modality balancing (arXiv: https://arxiv.org/abs/2304.14133; Springer version: https://link.springer.com/article/10.1007/s13735-023-00312-6).
- **MOCHEG (2022)**: end-to-end multimodal fact-checking + explanation generation with evidence retrieval from web sources (arXiv: https://arxiv.org/abs/2205.12487).
- **FACTIFY3M (2023)**: multimodal fact verification benchmark with explainability via 5W QA pairs (arXiv: https://arxiv.org/abs/2306.05523).
- **MAFT (AAAI)**: a multimodal automated fact-checking approach based on textualizing non-text modalities (images/video/audio) for downstream reasoning (AAAI page: https://ojs.aaai.org/index.php/AAAI/article/view/35354).

Recent multimodal multilingual resources (e.g., M4FC, MMM-Fact, AVerImaTeC) suggest the field is moving toward web-realistic settings and time-aware evaluation splits; these are useful directions for Indonesian ESG use-cases but must be evaluated for domain fit (arXiv entries: https://arxiv.org/abs/2510.23508, https://arxiv.org/abs/2510.25120, https://arxiv.org/abs/2505.17978).

---

## 5. Methods: Evidence Retrieval, Reasoning, and Multimodal Fusion

### 5.1 Retrieval in Closed vs Open Settings

Closed-corpus retrieval (e.g., FEVER’s Wikipedia) simplifies evaluation but can hide real-world issues like missing evidence and temporal leakage. Open-web retrieval improves realism but introduces:

- credibility variability
- duplicates and near-duplicates
- changing content over time
- language diversity and OCR errors in PDFs/images

Datasets that explicitly include web evidence and temporal constraints (e.g., web-based verification datasets such as AVeriTeC and AVerImaTeC) highlight the need for controlling leakage and ensuring evidence sufficiency checks (e.g., AVeriTeC paper entry: https://huggingface.co/papers/2305.13117; AVerImaTeC arXiv: https://arxiv.org/abs/2505.17978).

### 5.2 Claim–Evidence Reasoning: From NLI to LLMs

The dominant paradigm for claim verification is to treat the problem as NLI-style classification with retrieved evidence. This can be:

- single-sentence entailment
- multi-sentence aggregation (e.g., concatenation + classifier, hierarchical models)
- graph-based evidence reasoning

Large language models (LLMs) can act as flexible reasoners and summarizers, but they introduce risk of hallucinated rationales if not constrained to quoted evidence. Surveys emphasize that AFC systems must be evaluated on evidence grounding rather than narrative quality (Guo et al., 2022: https://transacl.org/index.php/tacl/article/view/3509).

### 5.3 Multimodal Fusion Strategies

Common strategies include:

1. **Early fusion**: joint multimodal encoders learn a shared representation for claim + image/video frames + text evidence.
2. **Late fusion / ensemble**: separate unimodal judgments combined via learned weighting.
3. **Textualization**: convert images/video/audio into textual descriptions (captions/OCR/transcripts), then apply text-based verification (e.g., MAFT: https://ojs.aaai.org/index.php/AAAI/article/view/35354).

Textualization is attractive for ESG because much “visual” evidence is actually textual in images (tables/figures in PDFs) and can be handled via OCR + structured extraction.

### 5.4 Credibility Modeling and Evidence Weighting

In open-domain settings, evidence credibility matters: social posts may provide early signals but also propagate misinformation. A practical approach is to incorporate:

- domain reputation and source-type priors (regulator vs blog vs social)
- cross-source corroboration (multiple independent sources)
- recency and temporal alignment constraints

These are especially important for ESG, where different actors (company press releases, regulators, NGOs, media) have different incentives.

---

## 6. Evaluation Protocols and Metrics

### 6.1 Layered Evaluation (Recommended)

A recurring lesson from AFC research is to avoid attributing failure to the “verifier” when retrieval is the bottleneck. Therefore, evaluate:

1. **Retrieval quality** (evidence relevance): precision@k, recall@k, MRR.
2. **Verdict quality**: macro-F1/accuracy over supported/refuted/NEI.
3. **Citation fidelity**: whether evidence truly supports the verdict (human adjudication subset).
4. **Calibration**: reliability diagrams / ECE for confidence scores (important for audit prioritization).

Shared tasks (e.g., CheckThat!) encourage this decomposition by evaluating multiple pipeline components (CheckThat! 2020 overview: https://arxiv.org/abs/2007.07997).

### 6.2 Preventing Temporal Leakage

Time-based splitting is crucial in web settings. Several modern datasets emphasize temporal constraints and splits to better mirror deployment conditions (e.g., M4FC description mentions temporal splits and leakage prevention approaches; arXiv: https://arxiv.org/abs/2510.23508).

For ESG, temporal leakage is a major risk because a claim about “2022 performance” may be verified using evidence published later (e.g., retrospective reports).

---

## 7. Open Challenges and Research Gaps

This section consolidates the most important gaps for Indonesian ESG multimodal fact-checking:

1. **Claim definition and normalization remain under-specified**, especially in long-form documents (surveys note the lack of a universally accepted claim definition in practical pipelines) (see survey discussions such as MDPI “Using NLP for Fact Checking: A Survey”: https://www.mdpi.com/2411-9660/5/3/42).
2. **Evidence sufficiency is not guaranteed** in open-web retrieval. Systems must robustly output NEI when evidence is missing or ambiguous, rather than “guess.”
3. **Entity resolution is a primary failure mode** (subsidiaries, brand names, spelling variants; Indonesian/English mixing). This is likely to dominate ESG verification errors without explicit disambiguation.
4. **Temporal alignment is essential**: many apparent contradictions are simply different time windows.
5. **Multimodal bias and shortcut learning**: multimodal benchmarks show unimodal biases and the need for careful dataset design (VERITE: https://arxiv.org/abs/2304.14133).
6. **Citation fidelity remains weakly measured**: many systems optimize verdict accuracy without ensuring cited evidence justifies the verdict.
7. **ESG domain mismatch**: general fact-checking datasets may not reflect the language and evidence types in sustainability reporting (tables, audits, regulator filings).

---

## 8. Implications for Indonesian ESG Fact-Checking

### 8.1 Evidence Sources and Credibility

For Indonesian ESG, evidence sources should be prioritized by credibility and data stability:

1. Regulators / stock exchange announcements (high credibility)
2. Audited sustainability/annual reports and third-party assurance statements
3. Credible news outlets and NGO reports
4. Social media (low-to-variable credibility; use only with strong controls)

### 8.2 Multimodality in ESG

Unlike social-media misinformation where images may be misleading out-of-context, ESG multimodality often arises from:

- scanned tables/figures
- photos of projects or facilities
- PDFs with embedded images containing text

Therefore, an ESG multimodal pipeline benefits from “textualization” approaches:

- OCR for tables/figures
- structured extraction of numeric metrics
- linking metrics to claim units (e.g., emissions reduction)

This aligns with multimodal textualization system ideas (MAFT: https://ojs.aaai.org/index.php/AAAI/article/view/35354), but must be adapted for ESG-specific measurement units and reporting templates.

### 8.3 Greenwashing vs Fact-Checking

Greenwashing detection research often uses readability/sentiment/boilerplate indicators, which are useful signals but do not directly establish factual support. A combined approach is recommended:

- Use textual indicators to prioritize suspicious narratives (greenwashing risk)
- Use fact-checking to produce evidence-grounded verdicts about specific claims

This separation prevents conflating rhetorical style with factual accuracy.

---

## 9. Recommended Research Agenda for This Repository

This agenda is designed to be implementable and evaluable, aligning with the repo’s provenance-first style.

### 9.1 Canonical Claim Schema (Artifact-First)

Create a stable `claims.csv` containing at minimum:

- `claim_id`, `company`, `claim_text`, `claim_type`, `esg_pillar`, `aspect`, `time_reference`
- `internal_provenance` (document + page reference + snippet)

### 9.2 External Evidence Indexing (Credibility-First)

Start with a small, high-credibility evidence pool to prevent early-stage noise:

- regulator announcements, exchange filings, audited reports
- a curated list of news/NGO domains

Store evidence items in `evidence.csv` with:

- URL, domain, publish date, extracted text/transcript/OCR text
- derived entity mentions + time references

### 9.3 Retrieval + Hard Filters

For each claim:

- retrieve top-k evidence
- apply entity disambiguation filters
- apply time-window filters (claim time_reference ± tolerance)
- apply source credibility weights

### 9.4 Reasoning Baselines and Ablations

Baseline progression:

1. **Text-only verifier** (claim + evidence excerpts → tri-label verdict)
2. **Multimodal textualization** for ESG visuals (OCR/caption to text)
3. **Ablations**:
   - without credibility weighting
   - without time filtering
   - without entity normalization

### 9.5 Evaluation and Human Adjudication

Build a small adjudicated set for:

- evidence relevance
- verdict correctness
- citation fidelity

Compute macro-F1 and provide error analysis by:

- claim type (commitment/action/outcome)
- ESG pillar (E/S/G)
- evidence source type (regulator/news/NGO/social)

---

## 10. Conclusion

Automated fact-checking has evolved from closed-corpus textual entailment into web-realistic, multilingual, and increasingly multimodal verification. Surveys and shared tasks emphasize a modular pipeline: claim identification, evidence retrieval, reasoning, and transparent reporting. Multimodal benchmarks demonstrate both new capabilities (image/video evidence) and new risks (bias, shortcut learning, and evidence insufficiency). For Indonesian ESG disclosures, the most urgent methodological requirements are provenance-first claim units, time-aware and credibility-aware evidence retrieval, and explicit measurement of citation fidelity. The research agenda proposed here operationalizes these principles into an implementable and evaluable plan suitable for transforming ESG disclosure analysis from narrative characterization to evidence-grounded accountability.

---

## References (links)

- Guo, Z., et al. (2022). *A Survey on Automated Fact-Checking.* TACL. https://transacl.org/index.php/tacl/article/view/3509
- Thorne, J., Vlachos, A., Christodoulopoulos, C., & Mittal, A. (2018). *FEVER: a large-scale dataset for Fact Extraction and VERification.* NAACL. https://aclanthology.org/N18-1074.pdf
- Wang, W. Y. (2017). *“Liar, Liar Pants on Fire”: A New Benchmark Dataset for Fake News Detection.* ACL. https://aclanthology.org/P17-2067/
- Auge, D., et al. (2019). *MultiFC: A Real-World Multi-Domain Dataset for Evidence-Based Fact Checking of Claims.* arXiv. https://arxiv.org/abs/1909.03242
- Wadden, D., et al. (2020). *Fact or Fiction: Verifying Scientific Claims.* arXiv. https://arxiv.org/abs/2004.14974 (ACL PDF: https://aclanthology.org/2020.emnlp-main.609.pdf)
- Barrón-Cedeño, A., et al. (2021). *Overview of the CLEF-2019 CheckThat!: Automatic Identification and Verification of Claims.* arXiv. https://arxiv.org/abs/2109.15118
- Barrón-Cedeño, A., et al. (2020). *Overview of CheckThat! 2020: Automatic Identification and Verification of Claims in Social Media.* arXiv. https://arxiv.org/abs/2007.07997
- Nakov, P., et al. (2025). *The CLEF-2025 CheckThat! Lab: Subjectivity, Fact-Checking, Claim Normalization, and Retrieval.* arXiv. https://arxiv.org/abs/2503.14828
- Hessel, J., et al. (2023). *VERITE: A Robust Benchmark for Multimodal Misinformation Detection Accounting for Unimodal Bias.* arXiv. https://arxiv.org/abs/2304.14133 (Springer: https://link.springer.com/article/10.1007/s13735-023-00312-6)
- Jiang, Y., et al. (2022). *End-to-End Multimodal Fact-Checking and Explanation Generation: A Challenging Dataset and Models (MOCHEG).* arXiv. https://arxiv.org/abs/2205.12487
- Aman Chadha, et al. (2023). *FACTIFY3M: A Benchmark for Multimodal Fact Verification with Explainability through 5W Question-Answering.* arXiv. https://arxiv.org/abs/2306.05523
- Kakizaki, R., et al. (2025). *MAFT: Multimodal Automated Fact-Checking via Textualization.* AAAI. https://ojs.aaai.org/index.php/AAAI/article/view/35354
- Ciftci, M., et al. (2021). *Using NLP for Fact Checking: A Survey.* Designs (MDPI). https://www.mdpi.com/2411-9660/5/3/42
- (ESG framing example) *A multi-dimensional textual framework for detecting greenwashing in sustainability reporting.* Springer Discover Sustainability. https://link.springer.com/article/10.1007/s43621-026-02890-x

