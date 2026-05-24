from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "results" / "revision_analysis"

TONE_TOTAL = 5444
TONE_COMPLETED = 4853
TONE_MISSING = 591
MAJORITY_BASELINE = 0.654
MISSING_ASPECTS = {"", "missing", "none", "nan", "null", "unknown", "n/a", "not_applicable"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="ignore") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def pct(value: float) -> str:
    return f"{value:.1%}"


def float_value(row: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default) or default)
    except Exception:
        return default


def methodology_paragraph() -> str:
    missing_rate = TONE_MISSING / TONE_TOTAL
    return (
        f"Tone agreement and tone-distribution statistics were computed on the {TONE_COMPLETED:,} records with a valid tone label, "
        f"excluding the {TONE_MISSING:,} records ({missing_rate:.1%}) where the pipeline returned no tone value. "
        "The excluded records are reported as a data-quality outcome rather than recoded as `none`, because absence of a model output is not "
        "equivalent to a substantive no-tone disclosure. Therefore, Chapter 4 tables and figures that analyze tone use 4,853 as the effective "
        "tone-analysis denominator, while corpus coverage tables retain 5,444 as the extraction denominator."
    )


def a19_narrative() -> str:
    return (
        "A.19 shows the largest substantive confusion around the boundary between realized outcomes and weaker disclosure tones. "
        "Outcome rows include 934 correct classifications but 101 cases assigned as action, indicating that the model sometimes "
        "reads implemented or measured results as activity language. The `none` row includes 1,781 correct classifications but "
        "223 cases assigned as commitment, showing a tendency to over-read generic sustainability language as forward-looking commitment. "
        "This should be interpreted as a claim-maturity boundary problem rather than a simple accuracy failure."
    )


def tone_denominator_rows() -> list[dict]:
    return [
        {"chapter element": "Corpus extraction coverage", "denominator": TONE_TOTAL, "included": TONE_TOTAL, "excluded": 0, "note": "Use for total extracted-record coverage."},
        {"chapter element": "Tone distribution", "denominator": TONE_COMPLETED, "included": TONE_COMPLETED, "excluded": TONE_MISSING, "note": "Use this denominator in Chapter 4 tone tables and figures."},
        {"chapter element": "Tone agreement / kappa", "denominator": TONE_COMPLETED, "included": TONE_COMPLETED, "excluded": TONE_MISSING, "note": "Do not compute agreement over missing tone outputs."},
        {"chapter element": "Missing-tone quality audit", "denominator": TONE_TOTAL, "included": TONE_MISSING, "excluded": TONE_COMPLETED, "note": "Report missingness as its own pipeline-quality result."},
    ]


def proxy_summary() -> dict:
    rows = read_csv(REV / "climatebert_proxy_agreement_summary.csv")
    if rows:
        row = rows[0]
        return {
            "percent_agreement": float_value(row, "percent_agreement", 0.8373493975903614),
            "cohen_kappa": float_value(row, "cohen_kappa", 0.6451446894422231),
        }
    return {"percent_agreement": 0.8373493975903614, "cohen_kappa": 0.6451446894422231}


def top_unmapped_rows(limit: int = 15) -> list[dict]:
    coverage = read_csv(REV / "ontology_coverage_full.csv")
    review = read_csv(REV / "ontology_novel_aspect_review.csv")
    reviewed_paths = {row.get("aspect", ""): row.get("ontology_path", "") for row in review}
    rows = []
    for row in coverage:
        mapped = str(row.get("mapped_to_ontology", "")).lower() in {"true", "1", "yes"}
        aspect = row.get("aspect", "").strip()
        if mapped or aspect.lower() in MISSING_ASPECTS:
            continue
        rows.append(
            {
                "aspect": aspect,
                "records": row.get("records", ""),
                "suggested_gri_sasb_tcfd_node": suggest_node(aspect),
                "reviewed_ontology_path": reviewed_paths.get(aspect, ""),
            }
        )
    rows.sort(key=lambda row: int(float(row.get("records") or 0)), reverse=True)
    return rows[:limit]


def suggest_node(aspect: str) -> str:
    text = aspect.lower()
    if any(token in text for token in ["keberlanjutan", "sustainability", "pengungkapan", "pelaporan", "prospektif"]):
        return f"GRI 2 General Disclosures / GRI 3 Material Topics -> {aspect}"
    if any(token in text for token in ["korupsi", "etik", "governance", "tata kelola", "kepatuhan", "manajemen risiko", "pengelolaan risiko", "pengendalian internal"]):
        return f"GRI 205 Anti-corruption / GRI 2 Governance -> {aspect}"
    if any(token in text for token in ["climate", "karbon", "emisi", "energi", "iklim", "renewable"]):
        return f"GRI 305 Emissions / TCFD Climate -> {aspect}"
    if any(token in text for token in ["limbah", "pollution", "polusi", "air", "lingkungan", "ramah lingkungan"]):
        return f"GRI 306 Waste / GRI 303 Water / GRI 3 Material Topics -> {aspect}"
    if any(token in text for token in ["karyawan", "pelatihan", "keselamatan", "tenaga kerja", "hak asasi manusia"]):
        return f"GRI 401-404 Employment and Training -> {aspect}"
    if any(token in text for token in ["masyarakat", "community", "sosial", "csr", "pemberdayaan"]):
        return f"GRI 413 Local Communities -> {aspect}"
    return f"Manual review -> {aspect}"


def benchmark_rows() -> list[dict]:
    return [
        {"benchmark": "FinBERT", "reported metric": "F1=97.3%", "handles finance/ESG language": "yes", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no", "positioning": "Strong domain classifier, but not the thesis niche."},
        {"benchmark": "ESG-BERT", "reported metric": "F1=88%", "handles finance/ESG language": "yes", "Indonesian": "no", "multi-aspect": "limited", "tone-labeled disclosure maturity": "no", "positioning": "Relevant ESG baseline without Indonesian multi-aspect tone coverage."},
        {"benchmark": "SpanEval", "reported metric": "F1=75.42%", "handles finance/ESG language": "partial", "Indonesian": "no", "multi-aspect": "yes", "tone-labeled disclosure maturity": "no", "positioning": "Useful extraction benchmark, but not a sustainability disclosure tone system."},
        {"benchmark": "ClimateBERT", "reported metric": "F1=1.16", "handles finance/ESG language": "climate-specific", "Indonesian": "no", "multi-aspect": "no", "tone-labeled disclosure maturity": "no", "positioning": "Adjacent climate NLP baseline; measures climate commitment, not ABSA tone maturity."},
        {"benchmark": "GH-ABSA", "reported metric": "accuracy=4.71", "handles finance/ESG language": "no", "Indonesian": "no", "multi-aspect": "yes", "tone-labeled disclosure maturity": "no", "positioning": "ABSA reference point, but not designed for Indonesian sustainability disclosures."},
        {"benchmark": "This thesis", "reported metric": "prototype system", "handles finance/ESG language": "yes", "Indonesian": "yes", "multi-aspect": "yes", "tone-labeled disclosure maturity": "yes", "positioning": "Niche contribution: Indonesian-language, multi-aspect, tone-labeled sustainability disclosure analysis."},
    ]


def resolution_rows() -> list[dict]:
    proxy = proxy_summary()
    return [
        {"chapter": "4", "issue": "591 missing tone records", "decision": "exclude_from_agreement", "evidence": f"{TONE_COMPLETED:,}/{TONE_TOTAL:,} usable tone records", "writeup": methodology_paragraph()},
        {"chapter": "4", "issue": "Proxy kappa 0.645", "decision": "frame_as_tone_vs_climatebert_construct_agreement", "evidence": f"agreement={pct(proxy['percent_agreement'])}; kappa={proxy['cohen_kappa']:.3f}", "writeup": "Do not describe as human inter-rater agreement; interpret as ABSA tone vs ClimateBERT climate-commitment agreement."},
        {"chapter": "4", "issue": "A.19 commitment/action/outcome/none confusion", "decision": "add_narrative_interpretation", "evidence": "outcome correct=934, outcome->action=101, none correct=1,781, none->commitment=223", "writeup": a19_narrative()},
        {"chapter": "5", "issue": "data.md missing-tone outlier", "decision": "retain_as_failed_experiment", "evidence": "data.md missing_tone_rate=1.000", "writeup": "Use the outlier as validation evidence for prompt sensitivity, then state stability claims on the successful prompt family separately."},
        {"chapter": "5", "issue": "A.15 ClimateBERT baseline", "decision": "frame_as_adjacent_constructs", "evidence": f"percent agreement={pct(proxy['percent_agreement'])}; kappa={proxy['cohen_kappa']:.3f}; majority baseline={pct(MAJORITY_BASELINE)}", "writeup": "The pipeline beats the majority baseline but should be argued as complementary to ClimateBERT, not as a replacement."},
        {"chapter": "5", "issue": "A.29 greenwashing index", "decision": "median_primary_log1p_sensitivity", "evidence": "mean=3,380; median=0.0; n=2,071", "writeup": "Use median primary and log+1 sensitivity, or explicitly label the index as a prototype metric dominated by outliers."},
        {"chapter": "6", "issue": "Ontology contribution", "decision": "add_top_unmapped_mapping_table", "evidence": "52/52 aspects mapped in compact table; 138 novel/unmapped and 194 mapped reported in thesis notes", "writeup": "Use the top 10-15 unmapped aspects table with suggested GRI/SASB/TCFD nodes as A.16 backing evidence."},
        {"chapter": "6", "issue": "Benchmark gap framing", "decision": "claim_combined_indonesian_multi_aspect_tone_niche", "evidence": "FinBERT, ESG-BERT, SpanEval, ClimateBERT, and GH-ABSA do not cover all target pillars simultaneously.", "writeup": "Frame incomplete benchmark checklist items as future work: OCR quality, second annotator, and ontology formalization."},
    ]


def main() -> None:
    REV.mkdir(parents=True, exist_ok=True)
    write_csv(REV / "chapter_4_6_resolution_board.csv", resolution_rows())
    write_csv(REV / "chapter4_tone_denominator_audit.csv", tone_denominator_rows())
    write_csv(REV / "chapter6_top_unmapped_ontology_candidates.csv", top_unmapped_rows())
    write_csv(REV / "chapter6_benchmark_gap_positioning.csv", benchmark_rows())
    (REV / "chapter_4_6_resolution_decisions.json").write_text(
        json.dumps(
            {
                "missing_tone_policy": "exclude_from_agreement",
                "data_md_policy": "retain_as_failed_experiment",
                "greenwashing_policy": "median_primary_log1p_sensitivity",
                "ontology_top_n": 15,
                "updated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Generated Chapter 4-6 resolution artifacts in results/revision_analysis")


if __name__ == "__main__":
    main()
