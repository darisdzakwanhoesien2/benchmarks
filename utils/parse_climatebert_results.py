import json
import pandas as pd
import os

INPUT_PATH = "data/ground_truth/climatebert_parsed.json"


def parse_climatebert_results():

    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(INPUT_PATH)

    with open(INPUT_PATH, "r") as f:
        raw = json.load(f)

    rows = []

    for item in raw:

        row = {}

        row["index"] = item.get("index")
        row["text"] = str(item.get("text", "")).strip()
        row["timestamp"] = item.get("timestamp")

        models = item.get("models", {})

        for model_name, model_data in models.items():

            row[f"{model_name}_status"] = model_data.get("status")
            row[f"{model_name}_label"] = model_data.get("label")
            row[f"{model_name}_confidence"] = model_data.get("confidence")

        rows.append(row)

    df = pd.DataFrame(rows)

    print("Parsed columns:")
    print(df.columns.tolist())

    return df


if __name__ == "__main__":

    df = parse_climatebert_results()

    print(df.head())

# import json
# import pandas as pd


# INPUT_PATH = "data/ground_truth/climatebert_parsed.json"


# def parse_climatebert():

#     with open(INPUT_PATH, "r") as f:
#         raw = json.load(f)

#     rows = []

#     for item in raw:

#         base = {
#             "index": item.get("index"),
#             "text": item.get("text", "").strip(),
#             "timestamp": item.get("timestamp")
#         }

#         models = item.get("models", {})

#         for model_name, result in models.items():

#             base[f"{model_name}_status"] = result.get("status")
#             base[f"{model_name}_label"] = result.get("label")
#             base[f"{model_name}_confidence"] = result.get("confidence")

#         rows.append(base)

#     df = pd.DataFrame(rows)

#     return df


# if __name__ == "__main__":

#     df = parse_climatebert()

#     print(df.head())