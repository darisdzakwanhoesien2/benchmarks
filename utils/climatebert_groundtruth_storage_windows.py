import json
import os
import tempfile
import shutil

BASE_DIR = "data/ground_truth_windows"

RESULTS_FILE = f"{BASE_DIR}/climatebert_results.json"
PARSED_FILE = f"{BASE_DIR}/climatebert_parsed.json"


def _ensure_dir():
    os.makedirs(BASE_DIR, exist_ok=True)


def _atomic_write(path, data):

    _ensure_dir()

    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        dir=BASE_DIR
    ) as tmp:

        json.dump(data, tmp, indent=2)
        tmp_path = tmp.name

    shutil.move(tmp_path, path)


def load_results():

    _ensure_dir()

    if not os.path.exists(RESULTS_FILE):
        return []

    with open(RESULTS_FILE) as f:
        return json.load(f)


def save_result(entry):

    data = load_results()
    data.append(entry)

    _atomic_write(RESULTS_FILE, data)


def load_parsed():

    _ensure_dir()

    if not os.path.exists(PARSED_FILE):
        return []

    with open(PARSED_FILE) as f:
        return json.load(f)


def save_parsed(entry):

    data = load_parsed()
    data.append(entry)

    _atomic_write(PARSED_FILE, data)

# import json
# import os
# import tempfile
# import shutil

# BASE_DIR = "data/ground_truth_windows"

# RESULTS_FILE = f"{BASE_DIR}/climatebert_results.json"
# PARSED_FILE = f"{BASE_DIR}/climatebert_parsed.json"


# def _ensure_dir():
#     os.makedirs(BASE_DIR, exist_ok=True)


# def _atomic_write(path, data):

#     _ensure_dir()

#     with tempfile.NamedTemporaryFile(
#         "w",
#         delete=False,
#         dir=BASE_DIR
#     ) as tmp:

#         json.dump(data, tmp, indent=2)
#         tmp_path = tmp.name

#     shutil.move(tmp_path, path)


# def load_results():

#     _ensure_dir()

#     if not os.path.exists(RESULTS_FILE):
#         return []

#     with open(RESULTS_FILE) as f:
#         return json.load(f)


# def save_result(entry):

#     data = load_results()
#     data.append(entry)

#     _atomic_write(RESULTS_FILE, data)


# def load_parsed():

#     _ensure_dir()

#     if not os.path.exists(PARSED_FILE):
#         return []

#     with open(PARSED_FILE) as f:
#         return json.load(f)


# def save_parsed(entry):

#     data = load_parsed()
#     data.append(entry)

#     _atomic_write(PARSED_FILE, data)
# import json
# import os
# import tempfile
# import shutil

# BASE_DIR = "data/ground_truth_windows"

# RESULTS_FILE = f"{BASE_DIR}/climatebert_results.json"
# PARSED_FILE = f"{BASE_DIR}/climatebert_parsed.json"


# def _ensure_dir():
#     os.makedirs(BASE_DIR, exist_ok=True)


# def _atomic_write(filepath, data):

#     _ensure_dir()

#     with tempfile.NamedTemporaryFile(
#         "w",
#         delete=False,
#         dir=BASE_DIR
#     ) as tmp:

#         json.dump(data, tmp, indent=2)

#         temp_path = tmp.name

#     shutil.move(temp_path, filepath)


# def load_results():

#     _ensure_dir()

#     if not os.path.exists(RESULTS_FILE):
#         return []

#     with open(RESULTS_FILE, "r") as f:
#         return json.load(f)


# def save_result(entry):

#     data = load_results()

#     data.append(entry)

#     _atomic_write(RESULTS_FILE, data)


# def load_parsed():

#     _ensure_dir()

#     if not os.path.exists(PARSED_FILE):
#         return []

#     with open(PARSED_FILE, "r") as f:
#         return json.load(f)


# def save_parsed(entry):

#     data = load_parsed()

#     data.append(entry)

#     _atomic_write(PARSED_FILE, data)