https://app.jenni.ai/editor/TtVIBiLoGUiGSd8ZAEat

Feasibility of Chatbot for Indonesian ESG ABSA in This Benchmark

6. Methodology

This section presents the design choices, repositories of components, and evaluation protocol used to construct an Indonesian-language chatbot grounded on top of the existing ESG ABSA artifacts. The methodology is decomposed into (i) the repository inventory that the chatbot inherits, (ii) three candidate architectures with a worked-out comparison, (iii) Indonesian-language handling layer, (iv) a four-axis evaluation framework, and (v) the integration and release plan inside the present benchmark.

6.1 Existing Infrastructure to Reuse

The chatbot is constructed strictly as a thin conversational layer over already-tested repository modules. This deliberately preserves the "grounding-first" principle of Mishra et al. (Mishra et al., 2024), who position Deep Search DocQA as an integration of computer-vision-based PDF ingestion, NLP retrieval, and LLM generation; the analogue in this benchmark is the OCR ingestion pipeline (pages/Bulk_OCR.py), the LLM-driven statement parser (pages/llm_processing.py), and the canonical record store results/esg_records.json. Reusing these artifacts means that any chatbot response that points to a specific ESG ABSA record resolves to a paragraph, page coordinate, and OCR provenance that can be independently traced back to the source PDF, which is exactly the citation integrity guarantee that Wallat et al. (Wallat et al., 2025) argue is necessary but not sufficient for ESG-grade deployment.

Four separable layers of the existing benchmark are exposed as chatbot "skills":





Ingestion and extraction layer. The OCR and LLM processing pages produce normalized ESG statements; these flow into results/esg_records.json. This mirrors the document-conversion → information-retrieval → generation pipeline of Deep Search DocQA, in which PDF parsing or OCR, layout analysis, table extraction, and reading-order assembly precede any LLM-level question answering (Mishra et al., 2024). Treating esg_records.json as the chatbot's retrieval corpus keeps the chatbot aligned with the repository's reproducibility contract.



Validation and audit layer. Three pages act as auditor modules: pages/2_1_LLM_Error_Parse_Audit.py quantifies structural failures in the parsed records, pages/2_2_LLM_Statement_Page_Verifier.py checks that each statement references a valid PDF page coordinate, and pages/1_3_Ground_Truth_Metrics.py reports precision/recall/F1 against expert-labeled instances for each ABSA element. These three pages already implement the kind of detect-and-correct loop that Gupta et al. (al., 2025) recommend for financial-service chatbots under regulatory compliance (catching parse failures, content–document mismatches, and metric deviations before anything reaches the user).



Ontology and graph layer. pages/1_6_Ontology_Path_Viewer.py exposes the ESG ontology as a graph traversal surface, and pages/1_13_Semantic_Graph_Exporter.py provides serialized exports. This is functionally identical to the "ontology → dialogue manager" pattern of Altinok (Altinok, 2018), who showed that banking and finance chatbots can keep conversation state both as a knowledge base (nodes = products, services, named entities) and as a routing/disambiguation layer. Re-exporting the ontology through a chatbot query planner yields the workflow-guided hybrid in 6.2 without needing to redesign the ontology itself.



Job and model orchestration layer. code/llm_background_worker.py and the model catalog/monitoring pages give the chatbot a place to register background tasks, model versions, and inference logs. Hu et al. (Hu et al., 2025) warn that long-form financial outputs cannot be evaluated with BLEU/ROUGE alone, so ensuring that every chatbot inference is captured together with model version and prompt version is a prerequisite for the EMS-style evaluation in 6.4.

The four layers together yield a "data → audit → ontology → chat" readiness test that the chatbot inherits all of its grounding from artifacts already passing existing benchmark gates, rather than generating fresh answers from parametric memory alone.

6.2 Chatbot Architecture Options

Three candidate architectures are evaluated against the repository, ordered from least to most decoupled:





Option A — Direct ABSA-context chatbot (baseline). Selected ESG ABSA records (filtered by company, year, aspect, ESG pillar, or sentiment polarity) are inserted directly into the prompt as context, and a single LLM generates a response. This is the cheapest architecture because it does not require a retrieval index and is trivially deterministic per record selection. However, as flagged by Sharma and Bhattarai (Sharma & Bhattarai, 2026), retrieval-less generation is most vulnerable to hallucination when prompts are partially misleading or when the model's pre-training memory contradicts the injected context, and Garg et al. (Garg et al., 2025) demonstrate measurable hallucination reductions when the same architecture is augmented with at least a vector retrieval stage. Option A is included in this study primarily as a control because the repository's 1_3_Ground_Truth_Metrics.py page produces the kind of clean, structured JSON that Option A can consume verbatim.



Option B — Retrieval-Augmented Generation chatbot. ESG ABSA records are chunked at the statement level, embedded using a multilingual sentence encoder, indexed in FAISS, and queried by cosine similarity to the user question; the top-k chunks and their page coordinates are passed to a generator alongside the user query, with an instruction to "answer only from the context and cite each claim." This is functionally the same architecture validated by Garg et al. (Garg et al., 2025) (FAISS + cited generation) and by Daerobby et al. (Daerobby et al., 2026) in Indonesian—the latter achieved perfect Recall@3 of 1.000, MRR of 0.756, and NDCG@3 of 0.864 over 100 PMB questions using FAISS + LangChain, and Mistral Devstral produced the best generation profile (BERTScore 0.755, ROUGE-1 0.604, METEOR 0.427). The Indonesian RAG chatbot of Abdurrazzaq et al. (Abdurrazzaq et al., 2025) extends the architecture by combining dense embeddings (jina-embeddings-v3), BM25 lexical re-ranking, and a Logistic Regression domain filter; they report that an FAISS L2 + BM25 hybrid reranker achieved Top-30 accuracy of 0.699, while the domain filter worked well for synthetic queries but misclassified natural queries. This negative finding on domain-filter robustness is preserved as a warning in our workflow-guided hybrid below.



Option C — Workflow-guided hybrid chatbot. A lightweight intent router first classifies the user query into one of several families — aspect query, sentiment trend, ontology/path query, company summary, comparative query, or out-of-scope — and dispatches accordingly. ASPECT and SENTIMENT queries use Option B with a high overlap-band retriever; ONTOLOGY queries leverage the ontology graph exports via pages/1_13_Semantic_Graph_Exporter.py; COMPARATIVE queries invoke an aggregation module that pulls multi-record results into spot tables; OUT-OF-SCOPE queries return a refusal with a one-line justification and a pointer to the closest in-scope items. The architecture is justified by Altinok (Altinok, 2018), who argues that domain ontologies can simultaneously serve as knowledge base and as a state-tracking layer for ambiguous named-entity reference; by Mishra et al. (Ding et al., 2025) for EulerESG, which combines "dual-channel retrieval and LLM-driven disclosure analysis" with "an interactive dashboard and chatbot for exploration, benchmarking, and explanation" achieving up to 0.95 average accuracy on standard-aligned metric tables; and by Ibrahim et al. (Ibrahim et al., 2025), whose Indonesian public-service chatbot study recommends a "hybrid retrieval-generation design" because rule-based systems cannot handle informal expressions, multi-intent queries, and policy-specific terminology.

The expected Pareto tradeoff between the three options, distilled from the cited literature, is summarized below. Option B consistently outperforms Option A on faithfulness and citation quality because post-rationalization (up to 57% in Wallat et al. (Wallat et al., 2025)) is structurally limited by evidence injection; Option C further reduces cross-document aggregation errors documented by Boloș et al. (Boloș et al., 2024) (e.g., three-year GHG trajectories) and the "lack of citation support about 50% of the time" phenomenon of Gao et al. (Gao et al., 2023), at the cost of higher engineering complexity. Option C is the chosen architecture for the primary chatbot document (pages/2_7_Chatbot_ESG_ABSA.py), with Options A and B retained as ablation baselines.

6.3 Indonesian Language Handling

Because the repository targets Indonesian disclosures and Indonesian-speaking stakeholders, four language-specific adaptations are layered onto the chatbot:





Query normalization. User queries are normalized for spelling variants, compound-word splits common in Indonesian ESG reports ("emisi GRK", "gas rumah kaca"), and code-switching with English ESG terms ("emission reduction plan", "governance risk"). This is necessary because IndoBERT-style models, while robust, are sensitive to lemma variation, and the Indonesian Instagram-environment dataset of Octovianto et al. (Octovianto et al., 2025) showed that domain-tuned IndoBERT-large-p2 only reached 72.44% F1 on in-the-wild environmental text, indicating that realistic ESG text carries informal and Anglicized surface forms that must be pre-normalized.



ESG-vocabulary alignment. A controlled Indonesian ESG lexicon (environmental: emisi, limbah, energi, air, keanekaragaman hayati; social: karyawan, pelatihan, K3, komunitas, HAM; governance: direksi, komite audit, transparansi, remunerasi, RUPS) is mapped to the ontology aspect labels used in the repository, so a question like "aspek sosial apa yang paling banyak dibahas dalam laporan ini" routes to the social-pillar node rather than producing a free-form answer. This lexicon-bridging role is justified by the fact that Indonesian ABSA pipelines (Alifi et al. (Alifi et al., 2023); Setiowati et al. (Setiowati et al., 2020)) only reach ~90% accuracy when trained on Indonesian stock and hotel-review text, so the chatbot must enforce vocabulary alignment rather than relying on open-ended LLM generation for aspect routing.



Bilingual evidence quotes. When the source record contains a long Indonesian-language passage, the chatbot preserves the original Indonesian quote alongside the Indonesian-generated summary. This is consistent with the faithfulness-plus-interpretability posture advocated by Ong et al. (Ong et al., 2024) for corporate sustainability analysis, and it preserves the auditor's ability to verify the quote against the original PDF without translation loss.



Clarification prompts. Ambiguous user intent ("bagaimana prospek ESG perusahaan ini?") triggers a clarification slot ("Apakah Anda ingin melihat ringkasan pilar E, S, atau G, atau semua pilar?"). The need for this guard is reinforced by Fauzan (Fauzan, 2025), who found that Indonesian speakers do analyze chatbot outputs at the aspect level (Bard received the most positive sentiment; DeepSeek/ChatGPT were most criticized on performance and bias), and by Ibrahim et al. (Ibrahim et al., 2025), who note that LLM chatbots tend to increase inaccuracy on multi-intent, policy-specific, and informal queries without explicit routing.

The language handler is intentionally lightweight: heavy vocabulary expansion is delegated to the Indonesian resources catalog — IndoNLU (Wilie et al., 2020), IndoLEM/IndoBERT (Koto et al., 2020), IndoNLG (Cahyawijaya et al., 2021), and NusaCrowd (Cahyawijaya et al., 2023) — using the pretrained tokenizers of IndoBART/IndoGPT where the generator is an Indonesian-specialized model, and falling back to a multilingual encoder (mE5 / BGE multilingual variants) when the generator is a multilingual generalist.

6.4 Evaluation Framework

A four-axis protocol is adopted, modeled on the framework of Gupta et al. (al., 2025) for financial chatbots (cognitive and conversational intelligence, user experience, operational efficiency, and ethical and regulatory compliance) but rescaled to the specific requirements of Indonesian ESG ABSA. Each axis is anchored on a set of concrete metrics that have published baselines in cited literature.





Axis 1 — Response quality. Relevance, factuality, completeness, and clarity are measured on a fixed test set of stratified Indonesian ESG ABSA queries (e.g., aspect lookup, sentiment trend, ontology path, comparative cross-company). Metrics adopt those used in published Indonesian RAG systems: BERTScore, ROUGE-1, ROUGE-L, and METEOR, all of which were computed by Daerobby et al. (Daerobby et al., 2026) and are therefore directly benchmark-comparable. To address the EMS-critique of Hu et al. (Hu et al., 2025) — that long-form financial answers need extraction-aware scoring — each test response is also decomposed into atomic claim-extraction units and scored against a reference answer derived from stored ESG records. The reference answer is constructed by replaying the same query in SQL/SPARQL against the repository ground-truth, ensuring that "ground truth" is auditable rather than crowdsourced.



Axis 2 — ABSA consistency. For every answer that asserts an aspect, opinion, polarity, ESG pillar, or sentiment tone, the chatbot's claim is checked against the corresponding esg_records.json entry. The axis uses conventional ABSA metrics (exact-match precision, recall, F1, and accuracy) for aspect term, aspect category, opinion term, and sentiment polarity (Zhang et al., 2022), evaluated at the response level rather than at the corpus level. The repository's existing ABSA baselines provide target ceilings: aspect extraction F1 in the range 0.79–0.95 (Alifi et al., 2023; Ekawati & Khodra, 2017; Jazuli et al., 2024), sentiment classification F1 in the range 0.64–0.97 (Ekawati & Khodra, 2017; Jazuli et al., 2024), and IndoBERT-large-p2 ESG-environment F1 of 72.44% (Octovianto et al., 2025). These ceilings are not strict pass/fail thresholds but are documented as design constraints to avoid overpromising model fidelity.



Axis 3 — Evidence grounding. Citation presence rate (fraction of claims that carry an in-response source pointer), citation correctness (fraction of pointers that resolve to the correct PDF page), and citation faithfulness — borrowing the post-rationalization definition of Wallat et al. (Wallat et al., 2025), where up to 57% of citations can be unfaithful in state-of-the-art systems — are computed by comparing each citation against an automatically-extracted claim map of the cited page. The ALCE framework (Gao et al., 2023) (fluency, correctness, citation quality) provides the macro template, and ALiiCE (Xu et al., 2024) provides the positional fine-grained view (recall/precision/variance of citation position within sentences) for cases where the response is a single paragraph. For multi-source aggregation responses (e.g., a multi-year carbon trend), citation aggregation correctness is measured against a manually constructed "ideal citation set."



Axis 4 — Robustness and safety. Repeated-query consistency (same query paraphrased in three ways should yield consistent claims and identical citations), adversarial/ambiguous query behavior (politeness injections, irrelevant follow-ups, currency/unit typos), and out-of-scope detection (questions unrelated to ESG ABSA should trigger a refusal) are tested on a held-out robustness set. The Indonesian-RAG medical chatbot of Abdurrazzaq et al. (Abdurrazzaq et al., 2025) is a relevant negative precedent: their Logistic Regression domain filter "works well on synthetic data but results in misclassification of natural queries," so a hybrid of NL intent classification and embedding-based out-of-scope rejection is adopted. The robustness axis also records latency per response and per-token cost, because production deployment in this repository currently runs on consumer hardware, similar to the Indonesian legal chatbot of Suharyadi and Saputra (Suharyadi & Saputra, 2025), which achieved 12–20 s response times on consumer hardware without cloud reliance.

A human-in-the-loop rating panel of three Indonesian-speaking reviewers is added on top of these automated metrics. The decision to include human review is motivated by Nurhidayati and Sugiarto (H & Sugiarto, 2025), who show that ROUGE-L, BERTScore, and LLM-as-Judge systematically overestimate semantic quality compared to human raters on Indonesian cultural content; human review is therefore necessary to avoid self-confirming metric drift.

6.5 Integration Plan in This Repository

The chatbot is added as a self-contained module that does not modify any existing repository component:





Code module. code/chatbot_esg_absa.py defines the public API: query(text: str) -> ChatResponse, where ChatResponse contains the generated answer, structured citations as a list of (record_id, page, snippet), and a self-reported confidence flag generated by the same verifier used in 2_2_LLM_Statement_Page_Verifier.py. Internally the module wires together the retriever, the workflow router, the Indonesian handler, and the audit hooks.



Artifact directory. results/chatbot/ is created to host four artifact families per release: (i) query logs (queries.jsonl), (ii) raw responses (responses.jsonl), (iii) grounding checks (grounding_report.jsonl with per-citation pass/fail and rationale), and (iv) failure-mode tables (failure_modes.csv) categorizing each incorrect response into one of the taxonomy slots introduced in Section 7 (cross-document aggregation, unsupported inference, ambiguous phrasing, ontology misalignment, out-of-scope, etc.).



Streamlit page. pages/2_7_Chatbot_ESG_ABSA.py (or whatever index slot is next available) hosts the interactive chatbot interface with a side-by-side evidence panel showing the cited records and the corresponding page coordinates, mirroring the EulerESG "interactive dashboard and chatbot for exploration, benchmarking, and explanation" pattern (Ding et al., 2025). The page also exposes the evaluation leaderboard so that each architecture variant can be compared side-by-side using the four-axis scoring from 6.4.



Documentation and chapter hooks. The chatbot README links back to the research-question dashboard and to sections of the thesis discussion, so that any chatbot finding (e.g., a high rate of cross-document aggregation errors, or a measurable ABSA consensus gap) can be referenced from the discussion chapter without re-running experiments. This pattern of artifact-to-chapter traceability follows Mishra et al. (Mishra et al., 2024), whose DocQA pipeline is explicitly reproducible from the DS4SD platform, and Zhu et al. (Zhu et al., 2025), who demonstrate that AI-generated ESG scores remain auditable against human expert ratings when scored indicators and reports are kept side by side.

Integration is staged in three phases: (i) Phase 1 ships Option A as a smoke test against 1_3_Ground_Truth_Metrics.py outputs, proving that the chatbot text generation layer is functioning end-to-end; (ii) Phase 2 ships Option B with a small FAISS index over esg_records.json and reports retrieval Recall@k/MRR/NDCG@k numbers that are directly comparable with Daerobby et al. (Daerobby et al., 2026)'s Indonesian RAG baselines (Recall@3 = 1.000, MRR = 0.756, NDCG@3 = 0.864); (iii) Phase 3 ships Option C, full Option B + ontology router + Indonesian handler, and runs the four-axis evaluation to produce the final scores reported in Section 7. The staged rollout is preferred over a single big-bang release so that failure modes introduced by the retrieval layer (e.g., the ABSA recall ceiling observed in (Ekawati & Khodra, 2017)'s 0.793 aspect F1) can be distinguished from failure modes introduced by the language layer, in line with the modular evaluation discipline of Malin et al. (Malin et al., 2025) and the architectural lesson of Garg et al. (Garg et al., 2025) that domain-aware RAG gains must be measured component-by-component.

Section-by-Section Checklist for "Feasibility of Chatbot for Indonesian ESG ABSA in This Benchmark"

Below are structured completion checklists for each section. Use them as a write-and-tick audit layer to ensure every component of the proposal is present, grounded, and aligned with the existing benchmark repository.



Checklist 1 — Section 1: Research Gap





State the Indonesian ESG disclosure landscape with at least one source describing the regulatory backdrop (POJK 51/2017, sustainability-report mandates, SDGs 2030 commitments).



Identify the absence of an Indonesian-language ESG ABSA artifact layer (no IndoESG-aspect-term roster, no Indonesian ESG ABSA benchmark corpus).



Identify the absence of a faithfulness/citation protocol for ESG ABSA grounded answers (cite Wallat et al. (Wallat et al., 2025), ALCE (Gao et al., 2023), Zhang et al. (Zhang et al., 2024)).



Identify the gap between English-language ESG chatbots (EulerESG (Ding et al., 2025), Deep Search DocQA (Mishra et al., 2024), ESG-RAG (Tran et al., 2025)) and Indonesian-language deployment.



Identify the gap between Indonesian RAG chatbot research (Daerobby et al. (Daerobby et al., 2026), Tohir et al. (Tohir et al., 2024), Abdurrazzaq et al. (Abdurrazzaq et al., 2025)) and ESG-specific content.



Cite Indonesian ABSA baselines (Ekawati & Khodra (Ekawati & Khodra, 2017), Jazuli et al. (Jazuli et al., 2024), Alifi et al. (Alifi et al., 2023), Octovianto et al. (Octovianto et al., 2025)) as scaffolding but highlight the lack of ESG-domain tuning.



Provide at least one quantitative anchor (e.g., F1 numbers, dataset size) for each gap claim.



Conclude the gap explicitly: "No Indonesian ESG ABSA chatbot with grounded citations currently exists, and the existing pieces have not been jointly composed."



Checklist 2 — Section 2: Research Questions





Write RQ1 on construction: a clear question about whether a chatbot grounded on the existing Indonesian ESG ABSA artifact layer is technically feasible to build.



Write RQ2 on architecture comparison: a question comparing direct-context, RAG, and workflow-guided hybrid chatbots.



Write RQ3 on Indonesian-language handling: a question on how Indonesian normalization, vocabulary alignment, bilingual quote preservation, and clarification prompts affect output quality.



Write RQ4 on evaluation: a question on whether a four-axis protocol (response quality, ABSA consistency, evidence grounding, robustness/safety) yields reproducible scoring for Indonesian ESG answers.



Write RQ5 on integration: a question on whether the chatbot can be deployed in the existing benchmark repository as a self-contained, non-destructive module.



Confirm each RQ is answerable from the artifact layer (i.e., questions should reference data and pages that exist in code/ and pages/).



Number the questions; cross-reference each RQ with at least one objective in Section 3.



Checklist 3 — Section 3: Research Objectives





Objective 1 — Implement three chatbot architecture variants (A/B/C) on top of results/esg_records.json.



Objective 2 — Build an Indonesian language handler (normalizer, ESG lexicon alignment, bilingual quote exporter, clarification prompts).



Objective 3 — Establish a four-axis evaluation framework with concrete metrics (BERTScore, ROUGE-1, ROUGE-L, METEOR (Daerobby et al., 2026); ABSA precision/recall/F1/accuracy (Zhang et al., 2022); ALCE-style citation metrics (Gao et al., 2023); robustness + latency).



Objective 4 — Run a comparative ablation covering Option A, Option B, and Option C.



Objective 5 — Integrate chatbot, evaluation artifacts, and dashboards into the repository as a strict superset (no modifications to existing ingestion/extration pipelines).



Objective 6 — Subject the chatbot to a human-in-the-loop review panel (three Indonesian-speaking reviewers), referencing the metric overestimation issue highlighted by Nurhidayati & Sugiarto (H & Sugiarto, 2025).



Each objective is phrased with a measurable verb (build, implement, measure, integrate, evaluate, audit).



Checklist 4 — Section 4: Research Contribution





Articulate a theoretical contribution: a reproducible protocol for grounding Indonesian ESG chatbots in an ABSA artifact layer (cite Ong et al. (Ong et al., 2024) on explainable NLP for sustainability analysis).



Articulate a practical contribution: deliver code/chatbot_esg_absa.py, the Streamlit page (pages/2_7_Chatbot_ESG_ABSA.py), and the artifact directory results/chatbot/.



Articulate an empirical contribution: an Indonesian ESG ABSA chatbot evaluation leaderboard across four axes and three architectures.



Articulate a resource contribution: an Indonesian ESG ABSA vocabulary lexicon, an evaluation test set, and the failure-mode taxonomy.



Position the contribution against the English ESG chatbot family (Ding et al., 2025; Mishra et al., 2023; Tran et al., 2025) and the Indonesian RAG chatbot family (Abdurrazzaq et al., 2025; Daerobby et al., 2026; Tohir et al., 2024) — make the intersection explicit.



State what is out of scope (e.g., updated rating predictions, trading decisions, real-time ESG news ingestion).



Ensure the contribution does not duplicate Indonesian NLP resources (IndoNLU (Wilie et al., 2020), IndoLEM/IndoBERT (Koto et al., 2020), IndoNLG (Cahyawijaya et al., 2021), NusaCrowd (Cahyawijaya et al., 2023)) but composes them.



Checklist 5 — Section 5: Literature Review

5.1 Task-Oriented and Retrieval-Augmented Chatbots





Cover RAG paradigm — at least Garg et al. (Garg et al., 2025), Siriwardhana et al. (Siriwardhana et al., 2023), Sharma & Bhattarai (Sharma & Bhattarai, 2026).



Cover ontology-based dialog management — Altinok (Altinok, 2018).



Connect each cited work to the chatbot construction step referencing it (e.g., FAISS → Option B; ontology → Option C).

5.2 Conversational AI Faithfulness and Citation Grounding





Revisit the "correctness ≠ faithfulness" finding of Wallat et al. (Wallat et al., 2025) (up to 57% unfaithful citations).



Cover the ALCE framework (Gao et al. (Gao et al., 2023)).



Cover comparative metric analyses (Zhang et al. (Zhang et al., 2024); Malin et al. (Malin et al., 2025)).



Connect faithfulness protocol to ESG requirement for verifiable artifacts.

5.3 Financial/ESG NLP Assistants and Disclosure Analytics





Cite Deep Search DocQA (Mishra et al., 2024), Lim (Lim, 2024), EulerESG (Ding et al., 2025), ESG Accountability (Mishra et al., 2023), ESG-RAG (Tran et al., 2025).



Cite Boloș et al. (Boloș et al., 2024), Ong et al. (Ong et al., 2024), Zhu et al. (Zhu et al., 2025).



Cite Indonesian-specific tangents (Prathama et al., 2025; Wiputra, 2026).



Note that none of the cited systems are Indonesian-language ESG ABSA-aware grounded chatbots.

5.4 Multilingual and Indonesian-Language Chatbot Design





Cite Ibrahim et al. (Ibrahim et al., 2025) (GPT-4, PaLM-2, IndoGPT comparison).



Cite Tohir et al. (Tohir et al., 2024) (RAG on 30 Juz Qur'an Indonesian corpus).



Cite Abdurrazzaq et al. (Abdurrazzaq et al., 2025) (medical Indonesian RAG, FAISS + BM25, LR domain filter caveat).



Cite Daerobby et al. (Daerobby et al., 2026) (Indonesian RAG baselines: Recall@3 1.000, MRR 0.756, NDCG@3 0.864, BERTScore 0.755).



Cite Nurhidayati & Sugiarto (H & Sugiarto, 2025) (memory injection + automated-overestimation warning).



Cite Fauzan (Fauzan, 2025) (zero-shot ABSA on AI chatbots).



Cite Indonesian NLP resources (Cahyawijaya et al., 2021, 2023; Koto et al., 2020; Wilie et al., 2020).



Cite Indonesian ABSA studies (Alifi et al., 2023; Ekawati & Khodra, 2017; Jazuli et al., 2024; Setiowati et al., 2020; Suchrady & Purwarianti, 2023) and Indonesian ESG sentiment dataset (Octovianto et al., 2025).

5.5 Evaluation Frameworks for ABSA and Chatbot Quality





ABSA metrics taxonomy — Zhang et al. (Zhang et al., 2022); Hua et al. (Hua et al., 2024); Zhang et al. (Zhang et al., 2024).



Chatbot evaluation frameworks — Gupta et al. (al., 2025) (4-axis financial chatbot).



Long-form evaluation — Hu et al. (Hu et al., 2025).



Citation granularity — Xu et al. (Xu et al., 2024).



Financial RAG — Li et al. (Li et al., 2024).



ESG-AI transparency — Lim (Lim, 2024).

5.6 Synthesis and Position





Identify three recurring gaps:.



State the intersection the proposed work occupies.



Map the contribution to four-axis the evaluation framework.



Checklist 6 — Section 6: Methodology

6.1 Existing Infrastructure to Reuse





Ingestion layer: pages/Bulk_OCR.py, pages/llm_processing.py → results/esg_records.json.



Validation layer: pages/2_1_LLM_Error_Parse_Audit.py, pages/2_2_LLM_Statement_Page_Verifier.py, pages/1_3_Ground_Truth_Metrics.py.



Ontology layer: pages/1_6_Ontology_Path_Viewer.py, pages/1_13_Semantic_Graph_Exporter.py.



Orchestration layer: code/llm_background_worker.py, model catalog pages.



Connection to the Deep Search DocQA-style ingestion-retrieval-generation pipeline (Mishra et al., 2023).

6.2 Chatbot Architecture Options





Option A (direct ABSA-context chatbot, no retriever).



Option B (RAG: chunked record store + FAISS + multilingual embeddings + cited generation).



Option C (workflow-guided hybrid router).



Architecture diagram with arrows from existing repository files.



Expected Pareto tradeoff table.



Justification page for Option C as the primary architecture (pages/2_7_Chatbot_ESG_ABSA.py).

6.3 Indonesian Language Handling





Query normalization (spelling, compound-word split, code-switch handling).



ESG-vocabulary lexicon (E/S/G pillars).



Bilingual evidence quotes preservation.



Clarification prompts for ambiguous intent (cite Fauzan (Fauzan, 2025); Ibrahim et al. (Ibrahim et al., 2025)).



Decision policy: when to use IndoBART/IndoGPT vs multilingual generalist (mE5/BGE).

6.4 Evaluation Framework





Axis 1 — BERTScore, ROUGE-1, ROUGE-L, METEOR; claim-extraction scoring inspired by Hu et al. (Hu et al., 2025).



Axis 2 — precision/recall/F1/accuracy at the response level (Zhang et al., 2022); documented ceilings (Alifi et al., 2023; Ekawati & Khodra, 2017; Jazuli et al., 2024; Octovianto et al., 2025).



Axis 3 — citation presence rate, citation correctness, citation faithfulness (Gao et al., 2023; Wallat et al., 2025; Xu et al., 2024).



Axis 4 (Robustness/safety) — repeated-query consistency, adversarial queries, out-of-scope rejection, latency/cost.



Human-in-the-loop review (3 Indonesian reviewers) — motivated by Nurhidayati & Sugiarto (H & Sugiarto, 2025).



Test set construction methodology (stratified, reproducible, queryable).



Reference answer generation methodology (SQL/SPARQL replay against esg_records.json).

6.5 Integration Plan





code/chatbot_esg_absa.py API: query(text) -> ChatResponse.



results/chatbot/ directory with four artifact families: query logs, raw responses, grounding reports, failure-mode tables.



pages/2_7_Chatbot_ESG_ABSA.py Streamlit page with side-by-side evidence panel.



Three-phase staged rollout: Phase 1, Phase 2, Phase 3 (Option C + evaluation).



Cross-link from chatbot page to thesis discussion chapter.



Checklist 7 — Document-Level Quality Gates





Every cited claim has an inline [id#excerpt] citation.



Every citation points to a real <WORK ID=N> in the source index.



No citations use alphanumeric doc_id strings.



No fabricated statistics, percentages, or author-year references.



All Indonesian-language methodological decisions are explicitly justified (cite Indonesian ABSA baselines (Alifi et al., 2023; Ekawati & Khodra, 2017; Jazuli et al., 2024) and Indonesian RAG baselines (Abdurrazzaq et al., 2025; Daerobby et al., 2026; Tohir et al., 2024)).



Each architecture option (A/B/C) maps to a specific retrieval protocol (none, dense, hybrid + router).



Each evaluation axis (1–4) has at least one concrete metric with a published baseline for comparison.



Repository code/files referenced (pages/*, code/*) actually exist in the benchmark.



Reviewed by all three Indonesian-speaking human reviewers before final submission.



Tables, headings, and LaTeX/math notation match the rest of the thesis formatting (GitHub-flavored markdown, single $ delimiters, headings with ##).



If you want, I can convert any of these checklists into a *.yaml or * todo-list file inside results/chatbot/ so they automatically travel alongside your chatbot artifacts.
