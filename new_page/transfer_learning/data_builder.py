from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from schemas import AbsaExample, iter_llm_records


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_from_esg_records(esg_records_path: Path) -> List[AbsaExample]:
    payload = read_json(esg_records_path)
    if not isinstance(payload, list):
        raise ValueError("esg_records.json must be a list of jobs")
    return list(iter_llm_records(payload))


def summarize(examples: List[AbsaExample]) -> Dict[str, Any]:
    aspect_counts = Counter(x.aspect for x in examples)
    sent_counts = Counter(x.sentiment for x in examples)
    tone_counts = Counter(x.tone for x in examples)
    esg_counts = Counter(x.esg for x in examples if x.esg)
    return {
        "n": len(examples),
        "unique_aspects": len(aspect_counts),
        "top_aspects": aspect_counts.most_common(20),
        "sentiments": sent_counts,
        "tones": tone_counts,
        "esg": esg_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build transfer learning dataset for ESG ABSA (Indonesian).")
    parser.add_argument("--esg-records", type=str, required=True, help="Path to results/esg_records.json")
    parser.add_argument("--out", type=str, required=True, help="Output dataset path (.jsonl)")
    parser.add_argument("--summary-out", type=str, default="", help="Optional summary json output path")
    args = parser.parse_args()

    esg_records_path = Path(args.esg_records)
    out_path = Path(args.out)
    summary_out = Path(args.summary_out) if args.summary_out else None

    examples = build_from_esg_records(esg_records_path)
    write_jsonl(out_path, (x.to_json() for x in examples))

    summary = summarize(examples)
    if summary_out:
        summary_out.parent.mkdir(parents=True, exist_ok=True)
        summary_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {len(examples)} rows to {out_path}")
    print(f"Unique aspects: {summary['unique_aspects']}")
    print(f"Sentiments: {dict(summary['sentiments'])}")
    print(f"Tones: {dict(summary['tones'])}")


if __name__ == "__main__":
    main()
