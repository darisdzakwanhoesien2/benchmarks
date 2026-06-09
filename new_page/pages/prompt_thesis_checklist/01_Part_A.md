Part A: Thesis-Wide Consistency and Contradiction Audit

Review the complete thesis for contradictions and inconsistencies involving:

thesis title and actual scope;
abstract and main thesis content;
introduction and conclusion;
research problem, objectives, and research questions;
terminology and abbreviations;
dataset names, dataset sizes, languages, companies, reports, pages, samples, and annotation counts;
model names, architectures, configurations, and versions;
baseline, proposed, hybrid, rule-based, classical machine-learning, and deep-learning systems;
training, validation, testing, and external evaluation splits;
preprocessing and experimental procedures;
hyperparameters and implementation descriptions;
evaluation metrics;
numerical values in text, tables, figures, appendices, and conclusions;
percentages, averages, totals, differences, and claimed improvements;
reported best-performing methods;
statistical claims and their supporting analyses;
limitations discussed in different chapters;
claimed contributions and evidence supporting them;
tense usage, particularly proposed work described as completed work;
references to tables, figures, equations, sections, appendices, and algorithms;
repeated passages that express different facts;
claims that become stronger between the results, discussion, abstract, and conclusion without additional evidence.

For every detected inconsistency, report:

Location A
Statement or value A
Location B
Statement or value B
Type of inconsistency
Why the two statements conflict
Which statement appears better supported
Recommended correction
Severity: Critical, Major, Moderate, or Minor
Confidence: High, Medium, or Low

Also determine whether apparently different numbers may legitimately represent different:

datasets;
subsets;
experimental stages;
folds;
averaging methods;
metrics;
model variants;
annotation rounds;
language subsets;
document-processing stages.

Do not classify values as contradictory before considering these possibilities.
