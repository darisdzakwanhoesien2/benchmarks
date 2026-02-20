import json
import os


PARSED_FILE = "data/climatebert_parsed.json"


def save_parsed_result(parsed):

    os.makedirs("data", exist_ok=True)

    if os.path.exists(PARSED_FILE):

        with open(PARSED_FILE, "r") as f:
            data = json.load(f)

    else:
        data = []

    data.append(parsed)

    with open(PARSED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_parsed_results():

    if not os.path.exists(PARSED_FILE):
        return []

    with open(PARSED_FILE, "r") as f:
        return json.load(f)