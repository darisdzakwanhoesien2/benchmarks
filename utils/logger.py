import json
import os

HISTORY_FILE = "data/history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(entry):
    history = load_history()
    history.append(entry)

    os.makedirs("data", exist_ok=True)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# import json
# import os
# from datetime import datetime

# HISTORY_FILE = "data/history.json"


# def load_history():
#     if not os.path.exists(HISTORY_FILE):
#         return []

#     with open(HISTORY_FILE, "r") as f:
#         return json.load(f)


# def save_history(entry):
#     history = load_history()
#     history.append(entry)

#     os.makedirs("data", exist_ok=True)

#     with open(HISTORY_FILE, "w") as f:
#         json.dump(history, f, indent=2)