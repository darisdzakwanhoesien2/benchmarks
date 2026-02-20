import json
import os
import tempfile
import shutil

RESULTS_FILE = "data/ground_truth/climatebert_results.json"
PARSED_FILE = "data/ground_truth/climatebert_parsed.json"


def _ensure_dir():
    os.makedirs("data/ground_truth", exist_ok=True)


def _atomic_write(filepath, data):

    _ensure_dir()

    with tempfile.NamedTemporaryFile("w", delete=False, dir="data/ground_truth") as tmp:

        json.dump(data, tmp, indent=2)

        tmp_path = tmp.name

    shutil.move(tmp_path, filepath)


def load_results():

    _ensure_dir()

    if not os.path.exists(RESULTS_FILE):
        return []

    with open(RESULTS_FILE, "r") as f:
        return json.load(f)


def save_result(entry):

    data = load_results()

    data.append(entry)

    _atomic_write(RESULTS_FILE, data)


def load_parsed():

    _ensure_dir()

    if not os.path.exists(PARSED_FILE):
        return []

    with open(PARSED_FILE, "r") as f:
        return json.load(f)


def save_parsed(entry):

    data = load_parsed()

    data.append(entry)

    _atomic_write(PARSED_FILE, data)

# import json
# import os

# RESULTS_FILE = "data/ground_truth/climatebert_results.json"
# PARSED_FILE = "data/ground_truth/climatebert_parsed.json"


# def _ensure_dir():
#     os.makedirs("data/ground_truth", exist_ok=True)


# def load_results():

#     _ensure_dir()

#     if not os.path.exists(RESULTS_FILE):
#         return []

#     with open(RESULTS_FILE, "r") as f:
#         return json.load(f)


# def save_result(entry):

#     data = load_results()

#     data.append(entry)

#     with open(RESULTS_FILE, "w") as f:
#         json.dump(data, f, indent=2)


# def load_parsed():

#     _ensure_dir()

#     if not os.path.exists(PARSED_FILE):
#         return []

#     with open(PARSED_FILE, "r") as f:
#         return json.load(f)


# def save_parsed(entry):

#     data = load_parsed()

#     data.append(entry)

#     with open(PARSED_FILE, "w") as f:
#         json.dump(data, f, indent=2)