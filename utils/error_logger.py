import os
from datetime import datetime


ERROR_FILE = "data/climatebert_errors.log"


def log_error(error, text=None):

    os.makedirs("data", exist_ok=True)

    with open(ERROR_FILE, "a") as f:

        f.write("\n")
        f.write("="*50 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")

        if text:
            f.write(f"Input Text: {text}\n")

        f.write(f"Error: {str(error)}\n")