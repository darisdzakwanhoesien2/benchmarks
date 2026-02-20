import re
from datetime import datetime


def parse_climatebert_markdown(md_text: str):
    """
    Parse ClimateBERT markdown output into structured JSON
    """

    models = {}

    current_model = None

    lines = md_text.split("\n")

    for line in lines:

        line = line.strip()

        # detect model header
        if line.startswith("### "):

            current_model = line.replace("### ", "").strip()

            models[current_model] = {
                "status": "unknown",
                "label": None,
                "confidence": None,
                "error": None
            }

            continue

        if current_model is None:
            continue

        # detect error
        if "❌ Error:" in line:

            models[current_model]["status"] = "error"

            models[current_model]["error"] = line.replace("❌ Error:", "").strip()

            continue

        # detect prediction
        match = re.match(r"•\s*(.+):\s*([0-9.]+)", line)

        if match:

            label = match.group(1)
            confidence = float(match.group(2))

            models[current_model]["status"] = "success"
            models[current_model]["label"] = label
            models[current_model]["confidence"] = confidence

            continue

    return {
        "timestamp": datetime.now().isoformat(),
        "models": models
    }


def flatten_climatebert(parsed_json):
    """
    Convert parsed JSON into flat table format
    """

    rows = []

    for model, data in parsed_json["models"].items():

        rows.append({
            "model": model,
            "status": data["status"],
            "label": data["label"],
            "confidence": data["confidence"],
            "error": data["error"]
        })

    return rows