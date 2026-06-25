B2. Scientific and Methodological Rigor

Use the actual thesis structure before evaluating rigor.

For this thesis, the main rigor-bearing chapters are:

- `implementation.md` for research design, data, preprocessing, feature logic, framework design, and reference construction;
- `experiments.md` for evaluation setup, metrics, comparisons, and diagnostic evidence;
- `discussion.md` for limitations, validity, and interpretation;
- `summary.md` for whether final claims stay within the evidence boundary.

Do not penalize the thesis merely for lacking a conventional train/validation/test benchmark if the work is actually an executable pipeline study with weak labels, pilot annotations, and comparative diagnostics. Instead, assess whether the thesis states that boundary honestly and avoids benchmark-style overclaims.

Evaluate:

suitability of the research design;
appropriateness of datasets and sampling;
representativeness of the selected sustainability reports or documents;
clarity of inclusion and exclusion criteria;
annotation procedure and ground-truth construction;
annotator expertise;
inter-annotator agreement;
treatment of label imbalance;
data leakage risks;
reproducibility of preprocessing;
separation of development and evaluation data;
baseline selection;
ablation studies;
hyperparameter selection;
evaluation metric selection;
statistical significance or uncertainty analysis;
error analysis;
qualitative analysis;
robustness checks;
external validity;
internal validity;
construct validity;
reproducibility;
limitations and threats to validity.

For machine-learning and NLP experiments, specifically check:

whether the train, validation, and test procedure is reproducible;
whether preprocessing was fitted using training data only;
whether test data influenced model or prompt selection;
whether prompts were changed after inspecting test outputs;
whether repeated LLM runs were handled consistently;
whether randomness, seeds, model versions, dates, and decoding settings are reported;
whether comparisons use the same datasets and evaluation conditions;
whether class-level results are provided when macro-level metrics could conceal poor performance;
whether numerical improvements are calculated correctly;
whether “significant” is used only when supported statistically;
whether qualitative examples are representative rather than selectively chosen.

Thesis-specific rigor checks:

- whether the reported four research questions are actually the ones being evaluated later;
- whether the OCR-expanded corpus, active thesis subset, and pilot-annotation subset are clearly separated;
- whether inclusion and exclusion criteria are explicit for documents, pages, and extracted records;
- whether prompt engineering changes are treated as development decisions, comparative experiments, or both;
- whether claims of reproducibility are supported by real prompt files, run metadata, model identifiers, timestamps, and artifact paths;
- whether ClimateBERT comparison is framed as external semantic comparison rather than full ground truth;
- whether missing-tone cases, schema drift, and heuristic greenwashing scores are discussed as limitations rather than hidden;
- whether the absence of full inter-annotator agreement and stratified expert gold data is acknowledged wherever validation claims are made.
