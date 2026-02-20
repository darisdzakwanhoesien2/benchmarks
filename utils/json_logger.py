import json
import os
from datetime import datetime


RESULT_FILE = "data/climatebert_results.json"


def save_result(text, result):

    os.makedirs("data", exist_ok=True)

    entry = {

        "timestamp": datetime.now().isoformat(),
        "text": text,
        "result": result

    }

    if os.path.exists(RESULT_FILE):

        with open(RESULT_FILE, "r") as f:
            data = json.load(f)

    else:

        data = []

    data.append(entry)

    with open(RESULT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_results():

    if not os.path.exists(RESULT_FILE):
        return []

    with open(RESULT_FILE, "r") as f:
        return json.load(f)