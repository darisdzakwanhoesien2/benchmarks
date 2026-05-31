# Expanded Literature → Gaps → RQs → Objectives → Methods → Evidence → Interpretation → Discussion → Conclusion (Mermaid)

This diagram is meant to be “thesis-structure complete”:

- It explicitly shows **research gap**, **research questions**, **objectives**, **literature review topics**, **methodology**, **results interpretation**, **discussion**, **conclusion**.
- It integrates **specific cited papers** (based on what is already present in `pages/thesis_draft/thesis_draft.csv` and the explicit references in `thesis_paper_esg_absa.md`).
- It anchors key claims to **repo evidence artifacts** so Chapter 4/5 statements remain auditable.

```mermaid
flowchart TD
  %% =====================================================================
  %% Thesis Topic
  %% =====================================================================
  T0["Thesis: Executable ESG ABSA framework<br/>for Indonesian sustainability reports"]:::node

  %% =====================================================================
  %% Research Gap
  %% =====================================================================
  subgraph GAP[Research Gap]
    G1["G1: ESG reports are heterogeneous<br/>bilingual, narrative+tables, non-standardized"]
    G2["G2: Document-level ESG scoring/sentiment is too coarse<br/>hides mixed tone across aspects"]
    G3["G3: LLM extraction is powerful but unstable<br/>schema drift, parse failures, prompt/model sensitivity"]
    G4["G4: Climate-only baselines (e.g., ClimateBERT)<br/>do not cover full ESG ABSA constructs"]
    G5["G5: Limited Indonesian ESG ABSA datasets<br/>need auditable pseudo/silver labeling workflows"]
  end

  %% =====================================================================
  %% Research Questions (RQs)  (matches the thesis draft structure)
  %% =====================================================================
  subgraph RQ[Research Questions]
    RQ1["RQ1: PDF→structured ESG transformation<br/>with provenance"]
    RQ2["RQ2: Record-level ESG ABSA schema<br/>(aspect / pillar / tone / sentiment)"]
    RQ3["RQ3: Tone vs ClimateBERT-style labels<br/>construct agreement"]
    RQ4["RQ4: Failure modes + schema drift + OCR loss<br/>+ ontology gaps"]
    RQ5["RQ5: Reproducibility & artifact lineage<br/>for LLM extraction"]
    RQ6["RQ6: Model & prompt stability<br/>across providers/models"]
  end

  %% =====================================================================
  %% Objectives
  %% =====================================================================
  subgraph OBJ[Research Objectives]
    O1["O1: Build OCR→records pipeline"]
    O2["O2: Define record-level ESG ABSA schema"]
    O3["O3: Add baselines + agreement metrics"]
    O4["O4: Add diagnostics + ontology coverage"]
    O5["O5: Ensure reproducibility via artifacts"]
    O6["O6: Deliver dashboards + semantic exports"]
  end

  %% =====================================================================
  %% Literature Review Topics (with integrated papers)
  %% =====================================================================
  subgraph LIT[Literature Review Topics]
    L1["ABSA foundations: tasks, models, trends"]:::topic
    L2["ABSA benchmarks & datasets (SemEval etc.)"]:::topic
    L3["ESG disclosure + integrated reporting context"]:::topic
    L4["Climate disclosure NLP baseline (ClimateBERT)"]:::topic
    L5["Greenwashing: concepts, taxonomy, detection"]:::topic
    L6["Validation: agreement metrics (κ etc.)"]:::topic
  end

  %% Papers (present in pages/thesis_draft/thesis_draft.csv)
  P_ABSA_SURVEY["Brauwers & Frasincar (2021)<br/>ABSA survey<br/>DOI: 10.1145/3503044"]:::paper
  P_ABSA_DATASETS["Chebolu et al. (2022)<br/>ABSA datasets review<br/>DOI: 10.18653/v1/2023.ijcnlp-main.41"]:::paper
  P_SEMEVAL14["Pontiki et al. (2014)<br/>SemEval-2014 ABSA<br/>DOI: 10.3115/v1/s14-2004"]:::paper
  P_SEMEVAL16["Pontiki et al. (2016)<br/>SemEval-2016 ABSA<br/>DOI: 10.18653/v1/s16-1002"]:::paper
  P_ABSA_QUADS["Zhang et al. (2024)<br/>ABSA quadruple extraction survey<br/>DOI: 10.1007/s10462-023-10633-x"]:::paper

  P_IR_ID["Adhariani & Sciulli (2020)<br/>Integrated reporting (Indonesia)<br/>DOI: 10.1108/ara-02-2019-0045"]:::paper
  P_ESG_VARIATION["Yu & Luu (2021)<br/>ESG disclosure variations<br/>DOI: 10.1016/j.irfa.2021.101731"]:::paper

  P_CLIMATEBERT["Webersinke et al. (2021)<br/>ClimateBERT baseline<br/>DOI: 10.2139/ssrn.4229146"]:::paper

  P_GREENWASH_TAX["Yang et al. (2020)<br/>Greenwashing taxonomy (SLR)<br/>DOI: 10.3846/jbem.2020.13225"]:::paper
  P_GREENWASH_LLM["Greenwashing detection w/ LMs (2023)<br/>arXiv:2311.01469"]:::paper

  P_AGREE_SURVEY["Artstein & Poesio (2008)<br/>Inter-coder agreement survey<br/>DOI: 10.1162/coli.07-034-r2"]:::paper
  P_AGREE_TUTOR["Hallgren (2012)<br/>IRR tutorial (κ etc.)<br/>DOI: 10.20982/tqmp.08.1.p023"]:::paper
  P_KAPPA["McHugh (2012)<br/>Kappa statistic overview<br/>(cited in thesis_paper_esg_absa.md)"]:::paper

  %% Topic-to-paper edges
  L1 --> P_ABSA_SURVEY
  L1 --> P_ABSA_QUADS
  L2 --> P_SEMEVAL14
  L2 --> P_SEMEVAL16
  L2 --> P_ABSA_DATASETS
  L3 --> P_IR_ID
  L3 --> P_ESG_VARIATION
  L4 --> P_CLIMATEBERT
  L5 --> P_GREENWASH_TAX
  L5 --> P_GREENWASH_LLM
  L6 --> P_AGREE_SURVEY
  L6 --> P_AGREE_TUTOR
  L6 --> P_KAPPA

  %% =====================================================================
  %% Methodology (Executable pipeline)
  %% =====================================================================
  subgraph METH[Methodology (Executable Pipeline)]
    M1["Data: sustainability-report PDFs<br/>(Indonesia; bilingual; varied layouts)"]
    M2["OCR: PDF→text with provenance"]
    M3["LLM extraction: text→structured records<br/>(store raw+parsed; detect schema drift)"]
    M4["ABSA labeling: aspect / ESG pillar / tone / sentiment<br/>(record-level)"]
    M5["Baseline comparison: ClimateBERT-style label<br/>(climate commitment/relevance)"]
    M6["Validation: agreement tables + error analysis<br/>(κ interpretation cautions)"]
    M7["Diagnostics: parse success, missing fields, failure modes"]
    M8["Ontology mapping: mapped vs unmapped aspects<br/>(vocabulary extension)"]
    M9["Outputs: dashboards + semantic graph exports<br/>(RDF/OWL/Neo4j)"]
  end

  %% =====================================================================
  %% Results & Interpretation (explicitly tied to artifacts)
  %% =====================================================================
  subgraph RES[Results & Interpretation]
    R1["Result: compact evidence snapshot<br/>(n=332 structured records)"]
    R2["Result: flattened intermediate outputs<br/>(n=2,074 T2 rows)"]
    R3["Result: proxy construct agreement vs ClimateBERT label<br/>agreement=0.837; κ=0.645 (n=332)"]
    R4["Result: OCR corpus processed<br/>(23 documents)"]
    R5["Interpretation: moderate alignment, non-identical constructs<br/>ESG tone ≠ climate commitment"]
  end

  %% =====================================================================
  %% Discussion / Limitations / Future Work
  %% =====================================================================
  subgraph DISC[Discussion]
    D1["Construct validity: what agreement means<br/>tone label vs climate label"]
    D2["Limitations: κ affected by label imbalance<br/>report prevalence + baselines"]
    D3["Next: human/silver labels → formal F1 + per-class errors"]
    D4["Next: expand corpus + multilingual robustness"]
    D5["Next: ontology extension for Indonesian ESG terms"]
  end

  %% =====================================================================
  %% Contributions
  %% =====================================================================
  subgraph CONTRIB[Research Contributions]
    C1["Executable OCR→records→ABSA evidence pipeline"]
    C2["Record-level ESG ABSA schema + evidence dashboards"]
    C3["Baseline framing: ClimateBERT as comparison, not replacement"]
    C4["Diagnostics suite: failure modes + stability summaries"]
    C5["Ontology mapping + semantic export path"]
  end

  %% =====================================================================
  %% Conclusion
  %% =====================================================================
  CONC["Conclusion: ESG ABSA can be made executable & auditable<br/>via record-level evidence + stability/diagnostics + ontology bridge"]:::node

  %% =====================================================================
  %% Artifact anchors (repo resources)
  %% =====================================================================
  subgraph ART[Backing Artifacts (Repo Paths)]
    A_TONE["`results/thesis_workflow_dashboard/tone_records_flat.csv`"]:::artifact
    A_T2["`results/thesis_workflow_dashboard/t2_flat_outputs.csv`"]:::artifact
    A_AGR["`results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv`"]:::artifact
    A_OCR["`results/thesis_workflow_dashboard/ocr_processing_summary.csv`"]:::artifact
    A_LIT["`pages/thesis_draft/thesis_draft.csv`"]:::artifact
    A_THR["`thesis_paper_esg_absa.md`"]:::artifact
  end

  %% =====================================================================
  %% High-level flow
  %% =====================================================================
  T0 --> GAP --> RQ --> OBJ
  OBJ --> METH --> RES --> DISC --> CONTRIB --> CONC
  LIT --> METH

  %% RQ to method mapping
  RQ1 --> M2
  RQ1 --> M3
  RQ2 --> M4
  RQ3 --> M5
  RQ3 --> M6
  RQ4 --> M7
  RQ4 --> M8
  RQ5 --> M9
  RQ6 --> M3

  %% Evidence anchoring
  R1 --> A_TONE
  R2 --> A_T2
  R3 --> A_AGR
  R4 --> A_OCR
  LIT --> A_LIT
  T0 --> A_THR

  classDef topic fill:#eef2ff,stroke:#3b82f6,stroke-width:1px,color:#111;
  classDef paper fill:#fff7ed,stroke:#f97316,stroke-width:1px,color:#111;
  classDef artifact fill:#f6f8fa,stroke:#333,stroke-width:1px,color:#111;
  classDef node fill:#ecfeff,stroke:#06b6d4,stroke-width:1px,color:#111;
```

## Important: integrating “each cited paper” into the DOCX

Right now, `pages/thesis_draft/toward_an_executable_esg_aspect_based_sentiment_analysis_framework_for_indonesian_sustainability_reports.docx` uses Word placeholder cites (`CITATION <key>`), but those keys are not backed by the `.bib` files in `pages/thesis_draft/`.

Minimum viable integration step:

- Pick one authoritative bibliography file (recommended later: a new consolidated `pages/thesis_draft/final_references.bib`).
- Ensure every paper you actually cite has a matching BibTeX entry key.
- Replace the `CITATION <key>` placeholders with real citations (Zotero Word plugin or Pandoc workflow).

## Resources and citations used (from this repo)

### Repo resources (data / evidence artifacts)

- `pages/thesis_draft/thesis_draft.csv` (literature inventory used to populate “paper nodes”)
- `thesis_paper_esg_absa.md` (explicit reference list + thesis-structure/RQ framing)
- `results/thesis_workflow_dashboard/tone_records_flat.csv` (n=332 structured records backing the “compact evidence snapshot”)
- `results/thesis_workflow_dashboard/t2_flat_outputs.csv` (n=2,074 flattened T2 rows backing the “intermediate outputs”)
- `results/thesis_workflow_dashboard/climatebert_proxy_agreement_summary.csv` (agreement=0.837; κ=0.645; n=332 backing the “proxy construct agreement” node)
- `results/thesis_workflow_dashboard/ocr_processing_summary.csv` (23 OCR documents backing the “OCR corpus processed” node)

### Literature citations (as represented in the diagram)

The following literature items were explicitly integrated as “paper nodes” in the Mermaid diagram. These are drawn from `pages/thesis_draft/thesis_draft.csv` and (for McHugh) the reference list in `thesis_paper_esg_absa.md`.

- Brauwers, G., & Frasincar, F. (2021). *A Survey on Aspect-Based Sentiment Classification*. ACM Computing Surveys. DOI: `10.1145/3503044`
- Chebolu, S. U. S., Dernoncourt, F., Lipka, N., & Solorio, T. (2022). *A Review of Datasets for Aspect-based Sentiment Analysis*. IJCNLP. DOI: `10.18653/v1/2023.ijcnlp-main.41`
- Pontiki, M., et al. (2014). *SemEval-2014 Task 4: Aspect Based Sentiment Analysis*. SemEval. DOI: `10.3115/v1/s14-2004`
- Pontiki, M., et al. (2016). *SemEval-2016 Task 5: Aspect Based Sentiment Analysis*. SemEval. DOI: `10.18653/v1/s16-1002`
- Zhang, H., Cheah, Y.-N., Alyasiri, O. M., & An, J. (2024). *Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey*. Artificial Intelligence Review. DOI: `10.1007/s10462-023-10633-x`
- Adhariani, D., & Sciulli, N. (2020). *The future of integrated reporting in an emerging market: an analysis of the disclosure conformity level*. DOI: `10.1108/ara-02-2019-0045`
- Yu, E. P.-y., & Luu, B. V. (2021). *International variations in ESG disclosure – Do cross-listed companies care more?* International Review of Financial Analysis. DOI: `10.1016/j.irfa.2021.101731`
- Webersinke, N., Kraus, M., Bingler, J. A., & Leippold, M. (2021). *ClimateBert: A Pretrained Language Model for Climate-Related Text*. SSRN. DOI: `10.2139/ssrn.4229146`
- Yang, Z., Nguyen, T., Nguyen, H.-N., Nguyen, T. T. N., & Cao, T. T. H. (2020). *GREENWASHING BEHAVIOURS: CAUSES, TAXONOMY AND CONSEQUENCES BASED ON A SYSTEMATIC LITERATURE REVIEW*. DOI: `10.3846/jbem.2020.13225`
- “Leveraging Language Models to Detect Greenwashing” (2023). arXiv: `2311.01469`
- Artstein, R., & Poesio, M. (2008). *Survey Article: Inter-Coder Agreement for Computational Linguistics*. DOI: `10.1162/coli.07-034-r2`
- Hallgren, K. A. (2012). *Computing Inter-Rater Reliability for Observational Data: An Overview and Tutorial*. DOI: `10.20982/tqmp.08.1.p023`
- McHugh, M. L. (2012). *Interrater reliability: The kappa statistic*. Biochemia Medica. (Referenced in `thesis_paper_esg_absa.md`)
