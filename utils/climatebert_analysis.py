import pandas as pd
import json


GROUND_TRUTH_FILE = "data/ground_truth/absa_mapping.csv"
PARSED_FILE = "data/ground_truth/climatebert_parsed.json"


def load_ground_truth():
    df = pd.read_csv(GROUND_TRUTH_FILE)

    df = df.rename(columns={
        "sentence_norm": "text",
        "majority_sentiment": "true_sentiment"
    })

    return df[["text", "true_sentiment"]]


def load_predictions():

    with open(PARSED_FILE, "r") as f:
        data = json.load(f)

    rows = []

    for entry in data:

        text = entry["text"]

        for model, result in entry["models"].items():

            rows.append({

                "text": text,
                "model": model,
                "predicted_label": result.get("label"),
                "confidence": result.get("confidence"),
                "status": result.get("status")

            })

    return pd.DataFrame(rows)


def merge_ground_truth():

    gt = load_ground_truth()
    pred = load_predictions()

    df = pred.merge(gt, on="text", how="left")

    return df


def compute_model_metrics(df):

    results = []

    models = df["model"].unique()

    for model in models:

        subset = df[df.model == model]

        valid = subset[subset.status == "success"]

        total = len(subset)
        success = len(valid)

        coverage = success / total if total else 0

        correct = (valid.predicted_label == valid.true_sentiment).sum()

        accuracy = correct / success if success else 0

        avg_conf = valid.confidence.mean() if success else 0

        results.append({

            "model": model,
            "total": total,
            "successful": success,
            "coverage": coverage,
            "accuracy": accuracy,
            "avg_confidence": avg_conf

        })

    return pd.DataFrame(results)


def confidence_distribution(df):

    return df[df.status == "success"][["model", "confidence"]]


def model_error_analysis(df):

    return df[df.status == "error"]