import json
import os


OUTPUT_PATH = "data/ground_truth/climatebert_parsed.json"


def save_climatebert_results(new_results: list):

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    if os.path.exists(OUTPUT_PATH):

        with open(OUTPUT_PATH, "r") as f:
            existing = json.load(f)

    else:
        existing = []

    existing.extend(new_results)

    with open(OUTPUT_PATH, "w") as f:

        json.dump(existing, f, indent=2)

    print(f"Saved {len(new_results)} results")

# import json
# import os
# from datetime import datetime


# OUTPUT_PATH = "data/ground_truth/climatebert_parsed.json"


# def save_results(results: list):

#     os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

#     # Load existing if exists
#     if os.path.exists(OUTPUT_PATH):

#         with open(OUTPUT_PATH, "r") as f:
#             existing = json.load(f)

#     else:
#         existing = []

#     existing.extend(results)

#     with open(OUTPUT_PATH, "w") as f:

#         json.dump(existing, f, indent=2)

#     print(f"Saved {len(results)} results to {OUTPUT_PATH}")


# # Example usage
# if __name__ == "__main__":

#     example = [
#         {
#             "timestamp": datetime.utcnow().isoformat(),
#             "index": 0,
#             "text": "Example text",
#             "models": {
#                 "climate-sentiment": {
#                     "status": "success",
#                     "label": "opportunity",
#                     "confidence": 0.95
#                 }
#             }
#         }
#     ]

#     save_results(example)