from __future__ import annotations

import hashlib
import json
import re
import shutil
import struct
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "results" / "image_outputs_archive"
ARCHIVE_IMAGE_DIR = OUTPUT_ROOT / "images"
JSON_PATH = OUTPUT_ROOT / "image_outputs_explanations.json"
MARKDOWN_PATH = OUTPUT_ROOT / "image_outputs_explanations.md"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

SOURCE_ROOTS = [
    ROOT / "results",
    ROOT / "new_page" / "results",
    ROOT / "new_page" / "pages",
    ROOT / "new_page" / "error",
]

EXCLUDED_PARTS = {
    ("results", "image_outputs_archive"),
}


EXPLANATION_RULES = {
    "aspect_by_tone_heatmap": {
        "title": "Aspect by Tone Heatmap",
        "category": "ESG ABSA distribution",
        "rq_links": ["RQ2", "RQ4", "RQ6"],
        "explanation": (
            "Shows how extracted ESG aspects are distributed across tone categories. "
            "Use it to detect which aspects are dominated by commitment, action, outcome, "
            "or other tone classes, and to identify sparse aspect-tone cells."
        ),
        "thesis_use": (
            "Supports categorization validity, diagnostics for imbalance, and stability "
            "discussion across aspect/tone subgroups."
        ),
    },
    "climatebert_label_by_tone": {
        "title": "ClimateBERT Label by Tone",
        "category": "ClimateBERT alignment",
        "rq_links": ["RQ3", "RQ6"],
        "explanation": (
            "Compares ClimateBERT-style labels against the thesis tone categories. "
            "Use it to inspect whether climate labels concentrate in specific tone classes."
        ),
        "thesis_use": (
            "Supports the ClimateBERT-versus-tone comparison and highlights where label "
            "spaces may align or diverge."
        ),
    },
    "climatebert_remote_top_scores": {
        "title": "ClimateBERT Remote Top Scores",
        "category": "ClimateBERT scoring",
        "rq_links": ["RQ3", "RQ5"],
        "explanation": (
            "Summarizes top remote ClimateBERT scores. It is useful as a sanity check, "
            "but should be treated as limited evidence unless the scored rows cover the full dataset."
        ),
        "thesis_use": (
            "Supports preliminary model-output inspection and reproducibility documentation, "
            "not final model comparison by itself."
        ),
    },
    "esg_by_tone": {
        "title": "ESG Pillar by Tone",
        "category": "ESG ABSA distribution",
        "rq_links": ["RQ2", "RQ4", "RQ6"],
        "explanation": (
            "Shows how Environmental, Social, and Governance categories distribute across "
            "tone classes. This helps reveal pillar imbalance and tone asymmetry."
        ),
        "thesis_use": (
            "Supports claims about ESG pillar coverage and warns where Social or other "
            "cells are too sparse for strong conclusions."
        ),
    },
    "tone_distribution": {
        "title": "Tone Distribution",
        "category": "ESG ABSA distribution",
        "rq_links": ["RQ2", "RQ6"],
        "explanation": (
            "Displays the overall distribution of extracted tone labels. Use it as a "
            "baseline view of class balance before subgroup or model comparisons."
        ),
        "thesis_use": (
            "Supports tone-category framing and sample-size reasoning for class balance."
        ),
    },
    "cm_sentiment_absa": {
        "title": "ABSA Sentiment Confusion Matrix",
        "category": "Evaluation metric",
        "rq_links": ["RQ2", "RQ4"],
        "explanation": (
            "Confusion matrix for ABSA sentiment predictions. It shows which sentiment "
            "classes are correctly predicted and which are confused."
        ),
        "thesis_use": (
            "Supports model evaluation, error analysis, and diagnostics for sentiment labels."
        ),
    },
    "cm_sentiment_ensemble": {
        "title": "Ensemble Sentiment Confusion Matrix",
        "category": "Evaluation metric",
        "rq_links": ["RQ4", "RQ6"],
        "explanation": (
            "Confusion matrix for an ensemble sentiment output. Compare it with the ABSA "
            "matrix to see whether ensembling changes errors or improves stability."
        ),
        "thesis_use": (
            "Supports ensemble/stability discussion and error comparison across strategies."
        ),
    },
    "screenshot": {
        "title": "Dashboard Screenshot",
        "category": "Interface evidence",
        "rq_links": ["RQ5"],
        "explanation": (
            "Screenshot captured from dashboard or error-review work. Use it as interface "
            "or debugging evidence, not as a quantitative analysis result."
        ),
        "thesis_use": (
            "Supports reproducibility, dashboard documentation, and audit-trail notes."
        ),
    },
}


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "image"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def png_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with path.open("rb") as f:
            header = f.read(24)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            width, height = struct.unpack(">II", header[16:24])
            return width, height
    except Exception:
        pass
    return None, None


def image_paths() -> list[Path]:
    paths: list[Path] = []
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            rel_parts = path.relative_to(ROOT).parts
            if any(rel_parts[: len(parts)] == parts for parts in EXCLUDED_PARTS):
                continue
            paths.append(path)
    return sorted(set(paths))


def rule_for(path: Path) -> dict:
    stem = slugify(path.stem)
    for key, rule in EXPLANATION_RULES.items():
        if key in stem:
            return rule
    return {
        "title": path.stem,
        "category": "Image output",
        "rq_links": [],
        "explanation": (
            "Generated image output discovered in the benchmark workspace. Review the "
            "source path and surrounding analysis page before using it as thesis evidence."
        ),
        "thesis_use": "Use only after confirming its source analysis and data lineage.",
    }


def build_manifest() -> dict:
    ARCHIVE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for index, source in enumerate(image_paths(), start=1):
        rule = rule_for(source)
        rel_source = source.relative_to(ROOT)
        archive_name = f"{index:03d}_{slugify(source.stem)}{source.suffix.lower()}"
        archive_path = ARCHIVE_IMAGE_DIR / archive_name
        shutil.copy2(source, archive_path)
        width, height = png_dimensions(source)
        records.append({
            "id": f"img_{index:03d}",
            "title": rule["title"],
            "category": rule["category"],
            "research_question_links": rule["rq_links"],
            "source_path": str(rel_source),
            "archived_path": str(archive_path.relative_to(ROOT)),
            "file_name": source.name,
            "extension": source.suffix.lower(),
            "size_bytes": source.stat().st_size,
            "width": width,
            "height": height,
            "sha256": file_sha256(source),
            "explanation": rule["explanation"],
            "thesis_use": rule["thesis_use"],
        })

    categories = {}
    for record in records:
        categories[record["category"]] = categories.get(record["category"], 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_root": str(ROOT),
        "scope_note": (
            "Archived generated image outputs from results/, new_page/results/, "
            "new_page/pages/, and new_page/error/. Raw extracted PDF page images under "
            "new_page/data/thesis_dataset are intentionally excluded."
        ),
        "image_count": len(records),
        "category_counts": categories,
        "images": records,
    }


def write_markdown(manifest: dict) -> None:
    lines = [
        "# Image Outputs and Explanations",
        "",
        f"Generated at: `{manifest['generated_at']}`",
        "",
        manifest["scope_note"],
        "",
        f"Archived image count: **{manifest['image_count']}**",
        "",
        "## Category Summary",
        "",
    ]
    for category, count in sorted(manifest["category_counts"].items()):
        lines.append(f"- **{category}:** {count}")

    lines.extend(["", "## Image Inventory", ""])
    for record in manifest["images"]:
        rq = ", ".join(record["research_question_links"]) or "Not directly linked"
        lines.extend([
            f"### {record['id']} - {record['title']}",
            "",
            f"![{record['title']}](images/{Path(record['archived_path']).name})",
            "",
            f"- **Category:** {record['category']}",
            f"- **RQ links:** {rq}",
            f"- **Source:** `{record['source_path']}`",
            f"- **Archive:** `{record['archived_path']}`",
            f"- **Dimensions:** {record['width'] or 'unknown'} x {record['height'] or 'unknown'}",
            f"- **Explanation:** {record['explanation']}",
            f"- **Thesis use:** {record['thesis_use']}",
            "",
        ])

    MARKDOWN_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    manifest = build_manifest()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_markdown(manifest)
    print(f"Archived {manifest['image_count']} image outputs")
    print(JSON_PATH)
    print(MARKDOWN_PATH)


if __name__ == "__main__":
    main()
