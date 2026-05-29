from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://sustainable-framework-api.darisdzakwanhoesien.site"


def yn(v: str, yes: str = "yes", no: str = "no") -> str:
    s = (v or "").strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return yes
    return no


def map_netzero(row: dict) -> str:
    # Ground truth has no explicit net-zero granularity in current file.
    # Keep conservative default unless you add a mapped column.
    return "none"


def map_specificity(row: dict) -> str:
    # Optional hook if you later add a specificity field.
    return "non"


def map_tcfd(row: dict) -> str:
    # Optional hook if you later add TCFD tagging.
    return "none"


def map_sentiment(v: str) -> str:
    s = (v or "").strip().lower()
    if s in {"positive", "negative", "neutral"}:
        return s
    return "neutral"


def map_social(esg: str) -> str:
    s = (esg or "").strip().lower()
    return "yes" if "s" in s and s not in {"", "none"} else "no"


def call_classify(params: dict, api_key: str | None = None, timeout: int = 30) -> dict:
    q = urllib.parse.urlencode(params)
    url = f"{API_BASE}/api/v1/climatebert-logic/classify?{q}"
    req = urllib.request.Request(url)
    if api_key:
        req.add_header("x-api-key", api_key)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Call climatebert logic classify using ground truth rows")
    parser.add_argument("--input", default="results/revision_analysis/pilot_ground_truth_annotations.csv")
    parser.add_argument("--output", default="results/fine_tuning/climatebert_logic_from_ground_truth.csv")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.1)
    parser.add_argument("--api-key", default="")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.limit > 0:
        rows = rows[: args.limit]

    out_fields = [
        "record_id",
        "company",
        "ground_truth_aspect",
        "ground_truth_esg",
        "ground_truth_tone",
        "sentiment",
        "api_params",
        "api_response",
        "api_error",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()

        for row in rows:
            params = {
                "climate_detector": yn(row.get("has_climate_d", "false"), yes="yes", no="no"),
                "climate_commitment": yn(row.get("has_climate_commitment", "false"), yes="yes", no="no"),
                "environmental_claims": yn(row.get("has_environmental_claims", "false"), yes="yes", no="no"),
                "netzero_reduction": map_netzero(row),
                "climate_specificity": map_specificity(row),
                "climate_tcfd": map_tcfd(row),
                "climate_sentiment": map_sentiment(row.get("sentiment", "")),
                "social_keyword": map_social(row.get("ground_truth_esg", "")),
            }

            api_resp = ""
            api_err = ""
            try:
                payload = call_classify(params, api_key=args.api_key or None)
                api_resp = json.dumps(payload, ensure_ascii=False)
            except Exception as e:
                api_err = str(e)

            writer.writerow(
                {
                    "record_id": row.get("record_id", ""),
                    "company": row.get("company", ""),
                    "ground_truth_aspect": row.get("ground_truth_aspect", ""),
                    "ground_truth_esg": row.get("ground_truth_esg", ""),
                    "ground_truth_tone": row.get("ground_truth_tone", ""),
                    "sentiment": row.get("sentiment", ""),
                    "api_params": json.dumps(params, ensure_ascii=False),
                    "api_response": api_resp,
                    "api_error": api_err,
                }
            )
            if args.sleep > 0:
                time.sleep(args.sleep)

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
