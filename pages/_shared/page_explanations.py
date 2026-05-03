from pathlib import Path

import streamlit as st


def add_page_explanation(file_path):
    """Render a short user-facing guide for a Streamlit page."""
    name = Path(file_path).name
    lower = name.lower()

    if "single_prediction" in lower:
        data_used = (
            "One ESG text passage entered in the text box and the selected "
            "ClimateBERT model endpoint."
        )
        steps = [
            "Select the model you want to inspect.",
            "Paste one sentence or paragraph from an ESG report.",
            "Run inference and review the returned label, score, and raw JSON response.",
        ]
    elif "multiple_prediction" in lower or "multi" in lower:
        data_used = (
            "One ESG text passage entered manually, one or more selected model "
            "endpoints, and optionally the saved JSON history in results/predictions.json."
        )
        steps = [
            "Choose the models to compare.",
            "Submit the same text to each model.",
            "Compare the predictions side by side and optionally export or append the results.",
        ]
    elif "batch_prediction" in lower:
        data_used = "An uploaded CSV file with a text column plus the selected ClimateBERT model."
        steps = [
            "Upload the CSV input file.",
            "Preview the rows that will be processed.",
            "Run batch inference and download the CSV with added prediction columns.",
        ]
    elif "batch_groundtruth" in lower:
        data_used = (
            "The ground-truth ABSA mapping CSV under data/ground_truth or "
            "data/ground_truth_windows, depending on the page."
        )
        steps = [
            "Load the labeled sentence dataset.",
            "Process only rows that still need ClimateBERT outputs.",
            "Persist raw and parsed model results so downstream dashboards can evaluate them.",
        ]
    elif "metric_analysis" in lower:
        data_used = (
            "Two uploaded CSV files: a ground-truth file and a prediction file. "
            "Both must include sentence, aspect_category, sentiment, and tone columns."
        )
        steps = [
            "Upload the two files.",
            "Normalize column names and validate required fields.",
            "Align rows by sentence, then compute classification metrics for aspect, sentiment, and tone.",
        ]
    elif "metrics_comparison" in lower or "metrics_visualization" in lower:
        data_used = (
            "Stored metric JSON or paired ground-truth/baseline CSV files, plus category "
            "mapping JSON files where label normalization is needed."
        )
        steps = [
            "Load the saved evaluation inputs.",
            "Normalize labels so comparable categories share the same names.",
            "Report precision, recall, F1, confusion matrices, and per-class error counts.",
        ]
    elif "scrambled" in lower:
        data_used = "A baseline ABSA mapping CSV that is intentionally shuffled or randomized."
        steps = [
            "Load the baseline mapping data.",
            "Scramble values to create a weak reference baseline.",
            "Use the output as a sanity check against real ABSA mapping models.",
        ]
    elif "absa" in lower and ("ontology" in lower or "model_comparison" in lower or "test_models" in lower):
        data_used = (
            "User-entered ESG text processed through rule-based, classical ML, deep learning, "
            "or hybrid ABSA modules."
        )
        steps = [
            "Enter ESG report text or a target sentence.",
            "Run the selected ABSA module or compare multiple modules.",
            "Inspect extracted aspects, sentiment, tone, explanations, coefficients, metrics, and downloadable outputs.",
        ]
    elif "absa_rule" in lower or "rule_based" in lower:
        data_used = "User-entered ESG text evaluated with the ontology/rule-based ABSA pipeline."
        steps = [
            "Paste ESG text.",
            "Match words and phrases against the aspect, sentiment, and tone ontology rules.",
            "Review the extracted labels, visualization, rule explanations, and CSV export.",
        ]
    elif "absa_classical" in lower or "classical" in lower:
        data_used = "User-entered ESG text evaluated with the classical machine-learning ABSA pipeline."
        steps = [
            "Paste ESG text.",
            "Run the trained classical model pipeline.",
            "Review predictions, feature coefficients, visual summaries, and CSV export.",
        ]
    elif "deep_learning" in lower or "deep_model" in lower:
        data_used = "User-entered ESG text evaluated with a deep-learning ABSA model such as mBERT."
        steps = [
            "Paste ESG text and initialize the model if required.",
            "Run token-level or sentence-level prediction.",
            "Inspect model outputs, token interpretability, and downloadable results.",
        ]
    elif "commitment_distribution" in lower:
        data_used = "Parsed ClimateBERT commitment-model outputs joined with available ground-truth labels."
        steps = [
            "Select a model or comparison view.",
            "Review predicted label counts and confidence distributions.",
            "Compare true and predicted labels, inspect confusion matrices, and export filtered results.",
        ]
    elif "climatebert" in lower:
        data_used = (
            "Saved ClimateBERT prediction outputs, parsed model responses, confidence scores, "
            "and ground-truth labels where available."
        )
        steps = [
            "Load the combined ClimateBERT result table.",
            "Summarize coverage, confidence, labels, and model-level accuracy.",
            "Drill into predictions, errors, confusion matrices, and exportable result tables.",
        ]
    elif "distribution document" in lower:
        data_used = (
            "A selected or uploaded ESG CSV with filename, sentiment, and tone columns, "
            "normalized with sentiment and tone ontologies."
        )
        steps = [
            "Choose or upload the document-level dataset.",
            "Aggregate sentiment and tone counts by file.",
            "Review per-document distributions, overall composition, summary statistics, and correlations.",
        ]
    elif "sankey" in lower or "tone_distribution" in lower or "data_new_distribution" in lower:
        data_used = (
            "An ESG sentence CSV containing aspect_category, sentiment, and tone columns, "
            "plus ontology JSON files for normalized labels."
        )
        steps = [
            "Load the configured or uploaded dataset.",
            "Normalize aspects, sentiments, and tones against the ontology files.",
            "Explore filtered distributions, Sankey flows, heatmaps, balancing rules, and downloadable tables.",
        ]
    elif "data distribution" in lower:
        data_used = (
            "A selected or uploaded ESG CSV together with aspect, sentiment, and tone ontology JSON files."
        )
        steps = [
            "Load the dataset from config/dataset.json or an uploaded CSV.",
            "Normalize raw labels into ontology categories.",
            "Compare raw and normalized distributions and export category summaries.",
        ]
    elif "dashboard" in lower or "aspects" in lower:
        data_used = (
            "Parsed ESG extraction outputs from configured CSV files, including source markdown, "
            "cleaned markdown, model names, pages, extracted sentences, aspects, sentiment, and tone."
        )
        steps = [
            "Select or load the parsed ESG dataset.",
            "Flatten model JSON responses into sentence-level rows.",
            "Filter, compare models, verify source grounding, inspect raw JSON, and audit aspect clusters.",
        ]
    elif "aspect_clusters" in lower:
        data_used = "The generated data/aspect_cluster.json file and its aspect member counts."
        steps = [
            "Load the cluster JSON file.",
            "Summarize clusters and member frequencies.",
            "Drill into one cluster and download the cluster membership table when needed.",
        ]
    elif "parse_documentation" in lower:
        data_used = "The JSON array embedded inside documentation.md."
        steps = [
            "Read documentation.md.",
            "Extract the first JSON array from the markdown text.",
            "Parse it into a dataframe for easier inspection.",
        ]
    else:
        data_used = (
            "The page-specific ESG, ABSA, or ClimateBERT inputs loaded by this script, "
            "usually from an uploaded CSV, configured dataset, JSON artifact, or typed text."
        )
        steps = [
            "Load or enter the input data.",
            "Apply the page's model, mapping, normalization, or evaluation logic.",
            "Inspect the tables, charts, diagnostics, and exports produced by the workflow.",
        ]

    st.markdown(
        f"""
**What this page is for:** This page is part of the ESG benchmarking workflow. It explains, tests, visualizes, or evaluates model outputs so the results are easier to audit instead of being treated as a black box.

**Data used:** {data_used}

**Step-by-step workflow:**
1. {steps[0]}
2. {steps[1]}
3. {steps[2]}

**How to read the output:** Use the tables for row-level evidence, the charts for distribution patterns, and the download buttons when you need to carry the processed results into another analysis step.
"""
    )


def add_section_explanation(heading):
    """Render a concise explanation below a section heading."""
    text = str(heading).lower()

    if "upload" in text or "load" in text or "data" in text:
        explanation = (
            "This step defines the input dataset for the analysis. Check that the expected "
            "columns are present before interpreting any charts or metrics below."
        )
    elif "alignment" in text:
        explanation = (
            "This step matches prediction rows to ground-truth rows, usually by sentence, "
            "so later metrics compare the same evidence rather than unrelated records."
        )
    elif "metric" in text or "evaluation" in text or "accuracy" in text or "leaderboard" in text:
        explanation = (
            "This section turns the aligned labels into evaluation scores. Use it to compare "
            "model quality, coverage, and error patterns across aspect, sentiment, and tone outputs."
        )
    elif "overview" in text or "summary" in text:
        explanation = (
            "This section gives the high-level shape of the loaded results before drilling into "
            "individual rows, models, or categories."
        )
    elif "distribution" in text or "composition" in text:
        explanation = (
            "This section counts how often each label appears. It is useful for spotting class "
            "imbalance, dominant ESG themes, and categories that may need more examples."
        )
    elif "confidence" in text:
        explanation = (
            "This section shows how certain the model was about its predictions. Low-confidence "
            "or widely spread scores are good candidates for manual review."
        )
    elif "confusion" in text:
        explanation = (
            "This table compares true labels with predicted labels. Off-diagonal cells show where "
            "the model is confusing one category for another."
        )
    elif "prediction" in text or "model" in text:
        explanation = (
            "This section exposes the model outputs directly so predictions can be audited against "
            "the original sentence and compared across model variants."
        )
    elif "explorer" in text or "raw" in text or "json" in text or "table" in text:
        explanation = (
            "This section is for row-level inspection. Use it when you need to verify exactly what "
            "was loaded, parsed, filtered, or exported."
        )
    elif "markdown" in text or "source" in text or "grounding" in text:
        explanation = (
            "This section links extracted ESG sentences back to the source text. It helps separate "
            "grounded extraction from possible hallucination or parsing drift."
        )
    elif "sankey" in text or "waterfall" in text or "heatmap" in text or "correlation" in text:
        explanation = (
            "This visualization shows relationships between labels, such as aspect to sentiment "
            "to tone. Use it to understand flows, concentrations, and unusual combinations."
        )
    elif "aspect" in text or "cluster" in text:
        explanation = (
            "This section organizes ESG aspects into raw labels or normalized clusters so similar "
            "topics can be compared more consistently."
        )
    elif "sentiment" in text or "tone" in text:
        explanation = (
            "This section focuses on the attitude or communication style attached to ESG statements, "
            "then compares those labels across documents, aspects, or models."
        )
    elif "coefficient" in text or "interpretability" in text or "explain" in text:
        explanation = (
            "This section explains which tokens, rules, or learned features influenced the output, "
            "making the prediction easier to review and challenge."
        )
    elif "export" in text or "download" in text:
        explanation = (
            "This step packages the current processed results so they can be reused in reporting, "
            "manual annotation, or follow-up benchmarking."
        )
    else:
        explanation = (
            "This section is one step in the page workflow. Read it together with the page overview, "
            "then use the displayed evidence to validate the model or dataset behavior."
        )

    st.markdown(f"_{explanation}_")
