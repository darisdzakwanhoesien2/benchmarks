B2. Scientific and Methodological Rigor

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
