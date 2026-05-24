"""Task definitions and UI helpers for ESG sustainability report task app."""

from __future__ import annotations

from typing import Dict, List

BADGES = [
    "NLP / ABSA",
    "Topic Modeling",
    "Sentiment Analysis",
    "Greenwashing Detection",
    "Indonesian ESG / OJK",
]

PHASES = [
    {
        "id": "phase_1",
        "title": "Phase 1 - Data Preparation",
        "tasks": [1, 2],
    },
    {
        "id": "phase_2",
        "title": "Phase 2 - Lexical and Sentiment Analysis",
        "tasks": [3, 4],
    },
    {
        "id": "phase_3",
        "title": "Phase 3 - Similarity and Clustering",
        "tasks": [5, 6, 7],
    },
    {
        "id": "phase_4",
        "title": "Phase 4 - Topic and Cluster Interpretation",
        "tasks": [8, 9],
    },
    {
        "id": "phase_5",
        "title": "Phase 5 - Temporal and Entity Analysis",
        "tasks": [10, 11],
    },
    {
        "id": "phase_6",
        "title": "Phase 6 - Predictive Modeling",
        "tasks": [12, 13],
    },
    {
        "id": "phase_7",
        "title": "Phase 7 - Synthesis",
        "tasks": [14],
    },
]

TASKS: Dict[int, Dict[str, object]] = {
    1: {
        "title": "Text Preprocessing of Sustainability Report Sections",
        "subtitle": "Tokenization, normalization, and domain-specific cleaning",
        "summary": "Build a bilingual preprocessing pipeline for ESG report text sections.",
        "steps": [
            "Cleaning: remove HTML tags, footnotes, table artifacts, page numbers.",
            "Normalization: lowercase and expand ESG abbreviations (GHG, CSR).",
            "Stop words: merge EN + ID stop words and add ESG domain stop list.",
            "Lemmatization: spaCy for English; IndoNLU/PySastrawi for Indonesian.",
            "Segmentation: split into E / S / G pillar-level units.",
            "Metadata tagging: company, sector, year, pillar, OJK listing tier.",
        ],
        "outputs": [
            "Cleaned corpus DataFrame",
            "Token lists per section",
            "Metadata-annotated text units",
        ],
        "notes": [
            "Detect language per sentence (langdetect) before routing to lemmatizer.",
        ],
    },
    2: {
        "title": "Initial Data Exploration and Distribution Analysis",
        "subtitle": "Understand corpus structure across companies, sectors, years, and ESG pillars",
        "summary": "Profile coverage and imbalance before downstream modeling.",
        "steps": [
            "Compute report count by year and sector.",
            "Compare average word counts by ESG pillar.",
            "Measure OJK tier distribution in the corpus.",
            "Build company x year coverage matrix for longitudinal gaps.",
            "Flag underrepresented sectors and sparse company histories.",
        ],
        "outputs": [
            "Grouped bar chart (reports per year x sector)",
            "Box plot (word count by pillar)",
            "Donut chart (OJK tier share)",
            "Coverage heatmap (company x year)",
        ],
        "notes": [
            "Flag companies with only one report year; they are unsuitable for Task 10.",
        ],
    },
    3: {
        "title": "ESG Word Frequency, N-Gram Analysis, and Sentiment Categorization",
        "subtitle": "Term frequency patterns across sentiment categories with word cloud visualization",
        "summary": "Aggregate sentiment metrics, bin records, and extract lexical patterns.",
        "steps": [
            "Aggregate afinn, bing, nrc, LLM-extracted, and ClimateBERT sentiment scores.",
            "Assign five sentiment bins from strongly negative to strongly positive.",
            "Extract top unigrams and bigrams per sentiment bin.",
            "Compare E vs S vs G lexical trends across bins.",
        ],
        "outputs": [
            "Word clouds by sentiment bin",
            "Top-20 unigram and bigram charts",
            "Pillar-level n-gram comparisons",
        ],
        "notes": [
            "Lexical greenwashing indicator: positive language dominated by vague commitments without hard metrics.",
        ],
    },
    4: {
        "title": "Cross-Category Analysis by Sector, ESG Pillar, and Company Size",
        "subtitle": "Identify linguistic patterns across organizational and reporting dimensions",
        "summary": "Repeat Task 3 analyses under metadata and reporting slices.",
        "steps": [
            "Group by IDX sector, company size, OJK tier, and ownership type.",
            "Group by ESG pillar, report year, GRI alignment, assurance level.",
            "Measure sentiment and lexical differences between groups.",
            "Answer hypothesis-driven questions on hedging/compliance tone.",
        ],
        "outputs": [
            "Group-wise lexical frequency tables",
            "Sentiment gap analysis by sector/pillar",
            "Hypothesis test summary notes",
        ],
        "notes": [
            "Track whether post-mandate years show sentiment tone shifts.",
        ],
    },
    5: {
        "title": "Metadata-Based Report Similarity Calculation",
        "subtitle": "Similarity using company characteristics and reporting metadata",
        "summary": "Create a non-text baseline similarity matrix using mixed-type metadata.",
        "steps": [
            "Encode categorical metadata features and normalize numeric features.",
            "Compute cosine or Gower distance between company-year observations.",
            "Convert distances into pairwise similarity matrix.",
            "Persist matrix for clustering in Task 7.",
        ],
        "outputs": [
            "Feature-encoded metadata table",
            "Pairwise metadata distance/similarity matrix",
        ],
        "notes": [
            "Gower is preferred for mixed categorical and continuous features.",
        ],
    },
    6: {
        "title": "Text-Based Report Similarity Calculation",
        "subtitle": "TF-IDF, semantic embeddings, and Doc2Vec for content-level similarity",
        "summary": "Compute three complementary text similarity views for boilerplate and drift checks.",
        "steps": [
            "TF-IDF cosine similarity for sparse lexical overlap.",
            "SBERT multilingual semantic similarity for bilingual meaning alignment.",
            "Doc2Vec embeddings for document-level trajectory analysis.",
            "Compare method agreement and retrieve high-similarity pairs.",
        ],
        "outputs": [
            "TF-IDF similarity matrix",
            "SBERT similarity matrix",
            "Doc2Vec similarity matrix",
        ],
        "notes": [
            "Stable high similarity across years can indicate narrative recycling.",
        ],
    },
    7: {
        "title": "Report Clustering Using Metadata and Text Similarities",
        "subtitle": "K-Means, DBSCAN, and Agglomerative Clustering with comparative analysis",
        "summary": "Cluster each similarity space and compare divergence between metadata and text structures.",
        "steps": [
            "Run K-Means with elbow and silhouette diagnostics.",
            "Run DBSCAN to identify dense groups and outliers.",
            "Run Agglomerative clustering and inspect dendrogram structure.",
            "Compare metadata clusters vs text clusters using Rand Index/NMI.",
        ],
        "outputs": [
            "Cluster assignments per method",
            "Outlier list (DBSCAN noise)",
            "Cluster divergence metrics (RI, NMI)",
        ],
        "notes": [
            "Large metadata-text divergence can be used as greenwashing signal candidates.",
        ],
    },
    8: {
        "title": "Cluster Analysis: Sentiment, Keywords, and Topic Modeling per Cluster",
        "subtitle": "LDA and BERTopic within each cluster; map to your 46 ESG aspect clusters",
        "summary": "Interpret clusters using sentiment profiles, topics, and ESG taxonomy mapping.",
        "steps": [
            "Compute cluster-level sentiment aggregates across metrics.",
            "Extract top unigram/bigram terms per cluster.",
            "Fit LDA with coherence-based topic count selection.",
            "Run BERTopic and map topics to 46 predefined ESG aspects.",
        ],
        "outputs": [
            "Cluster sentiment profile table",
            "Topic definitions (LDA + BERTopic)",
            "Topic-to-ESG-aspect mapping",
        ],
        "notes": [
            "Topic mapping quality can serve as external validation for both methods.",
        ],
    },
    9: {
        "title": "Correlation Between Company Features and Sentiment Scores",
        "subtitle": "Statistical associations between organizational characteristics and ESG tone",
        "summary": "Quantify which structural factors correlate with ESG sentiment behavior.",
        "steps": [
            "Build feature x sentiment variable matrix.",
            "Apply Pearson for continuous-continuous relationships.",
            "Apply Spearman for ordinal features like OJK tier.",
            "Apply eta-squared for categorical-continuous effects.",
        ],
        "outputs": [
            "Correlation and effect-size tables",
            "Seaborn heatmap and distribution plots",
        ],
        "notes": [
            "Use company-level stratification to avoid pseudo-replication bias.",
        ],
    },
    10: {
        "title": "ESG Topic Evolution Over Time and Across Companies",
        "subtitle": "Dynamic LDA and BERTopic time-based analysis; longitudinal greenwashing tracking",
        "summary": "Track topic and sentiment evolution over time using 2020 mandate as policy breakpoint.",
        "steps": [
            "Fit Dynamic LDA by year to observe topic emergence/persistence.",
            "Fit BERTopic with timestamps to analyze semantic drift.",
            "Compute rolling sentiment trends and Mann-Kendall tests.",
            "Run pre/post POJK 51/2017 effective-2020 comparison.",
        ],
        "outputs": [
            "Topic-over-time trajectories",
            "Company and sector trend charts",
            "Pre/post mandate change summary",
        ],
        "notes": [
            "Temporal greenwashing signal: sentiment inflation without metric expansion.",
        ],
    },
    11: {
        "title": "Named Entity Recognition for ESG Content and Commitment Analysis",
        "subtitle": "Identify regulatory bodies, certifications, targets, and co-occurrence networks",
        "summary": "Extract ESG entities, context polarity, and co-occurrence network structure.",
        "steps": [
            "Define ESG entity schema: ORG, CERT, POLICY, METRIC, DATE.",
            "Run NER with spaCy/GLiNER plus custom entity ruler patterns.",
            "Measure sentiment context per entity mention.",
            "Build co-occurrence network within sliding windows.",
        ],
        "outputs": [
            "Entity frequency and context table",
            "Entity co-occurrence graph",
            "Sector/pillar/entity distribution analysis",
        ],
        "notes": [
            "Entity mentions only in positive context may indicate impression management.",
        ],
    },
    12: {
        "title": "ESG Sentiment Prediction from Metadata, Text, and Combined Features",
        "subtitle": "Traditional ML + deep learning across three feature configurations",
        "summary": "Benchmark sentiment prediction performance across metadata-only, text-only, and fused features.",
        "steps": [
            "Train metadata-only models: LR, RF, XGBoost, TabNet.",
            "Train text-only models: embedding-based classifiers and IndoBERT/BERT variants.",
            "Train combined models: early-fusion MLP and late-fusion ensembles.",
            "Run ablations and compare accuracy, F1-macro, confusion matrices.",
        ],
        "outputs": [
            "Model leaderboard by feature set",
            "Confusion matrices by model",
            "Ablation summary of feature contribution",
        ],
        "notes": [
            "Use IndoBERT for Bahasa-heavy sections as baseline for text pipeline.",
        ],
    },
    13: {
        "title": "Advanced LLM Techniques for Greenwashing-Aware Sentiment Analysis",
        "subtitle": "Transformer models, nuance handling, and comparison with your ABSA pipeline",
        "summary": "Evaluate advanced models and build credibility-adjusted sentiment signals.",
        "steps": [
            "Benchmark RoBERTa, ClimateBERT, GPT/Claude prompted ABSA, IndoBERT fine-tuning.",
            "Implement hedging and temporal vagueness detectors.",
            "Design credibility-adjusted sentiment score combining positivity and verifiability cues.",
            "Evaluate against gold annotations using kappa, F1-macro, calibration.",
        ],
        "outputs": [
            "Model agreement and performance comparison",
            "Nuance-detection metrics (hedging/vagueness)",
            "Credibility-adjusted sentiment scoring framework",
        ],
        "notes": [
            "ClimateBERT mismatch with Indonesian discourse is a core research contribution.",
        ],
    },
    14: {
        "title": "Literature Review, Pipeline Evaluation, and Future Directions",
        "subtitle": "Contextualize findings, compare methods, address limitations",
        "summary": "Synthesize methodological and empirical findings into thesis-grade conclusions.",
        "steps": [
            "Position results in ABSA/greenwashing/NLP literature.",
            "Critically assess pipeline limits: imbalance, bilingual complexity, label subjectivity.",
            "Frame Indonesian regulatory implications (OJK, BI, PROPER).",
            "Propose next steps: ASEAN expansion, metric-grounded validation, local ESG lexicon.",
        ],
        "outputs": [
            "Structured synthesis narrative",
            "Limitations and mitigation table",
            "Future research roadmap",
        ],
        "notes": [
            "Tie claims to evidence from Tasks 1-13 and external references.",
        ],
    },
}


def get_tasks_for_phase(task_ids: List[int]) -> List[Dict[str, object]]:
    """Return full task objects for a phase definition."""
    return [{"id": task_id, **TASKS[task_id]} for task_id in task_ids]
