import pandas as pd
import os

from utils.parse_climatebert_results import parse_climatebert_results


ABSA_PATH = "data/ground_truth/absa_mapping.csv"
OUTPUT_PATH = "data/ground_truth/climatebert_absa_combined.csv"


def merge():

    if not os.path.exists(ABSA_PATH):
        raise FileNotFoundError(ABSA_PATH)

    absa_df = pd.read_csv(ABSA_PATH)

    absa_df["text"] = (
        absa_df["sentence_norm"]
        .astype(str)
        .str.strip()
    )

    climate_df = parse_climatebert_results()

    climate_df["text"] = (
        climate_df["text"]
        .astype(str)
        .str.strip()
    )

    combined = pd.merge(
        absa_df,
        climate_df,
        on="text",
        how="left"
    )

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    combined.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("Saved →", OUTPUT_PATH)

    print("Final columns:")
    print(combined.columns.tolist())

    return combined


if __name__ == "__main__":

    merge()

# import pandas as pd
# from utils.parse_climatebert_results import parse_climatebert


# ABSA_PATH = "data/ground_truth/absa_mapping.csv"
# OUTPUT_PATH = "data/ground_truth/climatebert_absa_combined.csv"


# def merge_climatebert_absa():

#     climate_df = parse_climatebert()

#     absa_df = pd.read_csv(ABSA_PATH)

#     # normalize text
#     absa_df["text"] = absa_df["sentence_norm"].astype(str).str.strip()
#     climate_df["text"] = climate_df["text"].astype(str).str.strip()

#     combined = pd.merge(
#         absa_df,
#         climate_df,
#         on="text",
#         how="left"
#     )

#     combined.to_csv(OUTPUT_PATH, index=False)

#     print("Saved combined dataset →", OUTPUT_PATH)

#     return combined


# if __name__ == "__main__":

#     df = merge_climatebert_absa()

#     print(df.columns.tolist())

# import json
# import pandas as pd


# CLIMATEBERT_PATH = "data/ground_truth/climatebert_parsed.json"
# ABSA_PATH = "data/ground_truth/absa_mapping.csv"

# OUTPUT_PATH = "data/ground_truth/climatebert_absa_combined.csv"


# def flatten_climatebert():

#     with open(CLIMATEBERT_PATH, "r") as f:
#         data = json.load(f)

#     rows = []

#     for item in data:

#         base = {
#             "index": item["index"],
#             "text": item["text"],
#             "timestamp": item["timestamp"]
#         }

#         for model, result in item["models"].items():

#             base[f"{model}_status"] = result.get("status")
#             base[f"{model}_label"] = result.get("label")
#             base[f"{model}_confidence"] = result.get("confidence")

#         rows.append(base)

#     return pd.DataFrame(rows)


# def merge_with_absa():

#     climate_df = flatten_climatebert()

#     absa_df = pd.read_csv(ABSA_PATH)

#     absa_df = absa_df.rename(columns={
#         "sentence_norm": "text"
#     })

#     combined = pd.merge(
#         absa_df,
#         climate_df,
#         on="text",
#         how="left"
#     )

#     combined.to_csv(OUTPUT_PATH, index=False)

#     print(f"Saved combined dataset → {OUTPUT_PATH}")

#     return combined


# if __name__ == "__main__":

#     df = merge_with_absa()

#     print(df.head())