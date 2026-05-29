from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
DOC_PATH = ROOT_DIR / "documentation_fact_checking.md"
REV_DIR = ROOT_DIR / "results" / "revision_analysis"


st.set_page_config(page_title="Fact-Checking Research Plan", page_icon="✅", layout="wide")


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _top(rows: list[dict], key: str, n: int = 8) -> list[tuple[str, int]]:
    ctr = Counter()
    for row in rows:
        v = (row.get(key) or "").strip()
        ctr[v if v else "<BLANK>"] += 1
    return ctr.most_common(n)


def _table(items: list[tuple[str, int]], c1: str, c2: str = "count") -> str:
    if not items:
        return "No data available."
    lines = [f"| {c1} | {c2} |", "|---|---:|"]
    for k, v in items:
        lines.append(f"| {k} | {v:,} |")
    return "\n".join(lines)


@st.cache_data(show_spinner=False)
def load_data() -> dict:
    pilot = _load_csv(REV_DIR / "pilot_ground_truth_annotations.csv")
    verifier = _load_csv(REV_DIR / "llm_statement_page_verifier_compiled.csv")
    failure = _load_csv(REV_DIR / "failure_modes.csv")
    prompt_stability = _load_csv(REV_DIR / "prompt_stability_summary.csv")
    model_stability = _load_csv(REV_DIR / "model_stability_summary.csv")
    ocr_summary = _load_csv(REV_DIR / "ocr_processing_summary.csv")

    return {
        "pilot": pilot,
        "verifier": verifier,
        "failure": failure,
        "prompt_stability": prompt_stability,
        "model_stability": model_stability,
        "ocr_summary": ocr_summary,
    }


def render_dataset_evidence(data: dict) -> None:
    pilot = data["pilot"]
    verifier = data["verifier"]
    failure = data["failure"]
    prompt_stability = data["prompt_stability"]
    model_stability = data["model_stability"]
    ocr_summary = data["ocr_summary"]

    st.subheader("Existing Dataset Evidence")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pilot labeled rows", f"{len(pilot):,}")
    c2.metric("Verifier rows", f"{len(verifier):,}")
    c3.metric("Failure rows", f"{len(failure):,}")
    c4.metric("OCR docs tracked", f"{len(ocr_summary):,}")

    exact = sum(1 for r in verifier if (r.get("best_status") or "").strip().lower() == "exact")
    likely = sum(1 for r in verifier if (r.get("best_status") or "").strip().lower() == "likely")
    possible = sum(1 for r in verifier if (r.get("best_status") or "").strip().lower() == "possible")

    s1, s2, s3 = st.columns(3)
    s1.metric("Verifier exact", f"{exact:,}")
    s2.metric("Verifier likely", f"{likely:,}")
    s3.metric("Verifier possible", f"{possible:,}")

    st.markdown("**Distribution snapshots for fact-checking readiness**")
    a, b = st.columns(2)
    with a:
        st.markdown(_table(_top(pilot, "ground_truth_esg"), "ground_truth_esg"))
        st.markdown(_table(_top(pilot, "ground_truth_tone"), "ground_truth_tone"))
        st.markdown(_table(_top(pilot, "sentiment"), "sentiment"))
    with b:
        st.markdown(_table(_top(verifier, "best_status"), "verifier_best_status"))
        st.markdown(_table(_top(failure, "failure_modes"), "failure_modes"))
        st.markdown(_table(_top(verifier, "prompt"), "verifier_prompt"))

    st.markdown("**Operational stability context**")
    o1, o2 = st.columns(2)
    o1.metric("Prompt stability configs", f"{len(prompt_stability):,}")
    o2.metric("Model stability configs", f"{len(model_stability):,}")


def render_research_plan(data: dict) -> None:
    pilot = data["pilot"]
    verifier = data["verifier"]
    failure = data["failure"]
    prompt_stability = data["prompt_stability"]
    model_stability = data["model_stability"]
    ocr_summary = data["ocr_summary"]

    st.subheader("Research Plan for Multimodal Fact-Checking (Indonesian ESG ABSA)")

    st.markdown("### 1) Research Gap")
    st.markdown(
        """
- The current pipeline extracts and classifies internal ESG disclosures, but does not yet verify claim truthfulness against external evidence.
- Existing validation is strong for parse/label quality, yet limited for claim-level support/contradiction testing.
- External multimodal sources (news, social, video transcripts, images) are not unified in a retrieval + verdict workflow.
- There is no repository benchmark for `supported`, `contradicted`, and `insufficient_evidence` verdict quality.
"""
    )

    st.markdown("### 2) Research Questions")
    st.markdown(
        """
1. Can extracted ESG claims be automatically verified against external Indonesian multimodal evidence?
2. Which evidence type contributes most to verification quality (text, social, video transcript, image, or fusion)?
3. How reliably can the system classify claims as supported, contradicted, or insufficient evidence?
4. Does multimodal aggregation improve reliability over text-only verification?
5. What dominant failure modes appear (entity mismatch, temporal drift, sentiment-claim confusion, visual ambiguity, credibility noise)?
"""
    )

    st.markdown("### 3) Research Objectives")
    st.markdown(
        """
1. Build a reproducible fact-checking pipeline for Indonesian ESG ABSA claims.
2. Integrate internal claim extraction with external evidence retrieval across text, image, and video.
3. Produce support/contradict/insufficient verdicts with provenance.
4. Evaluate claim-level and evidence-level performance.
5. Integrate results into existing dashboard and thesis chapter workflows.
"""
    )

    st.markdown("### 4) Research Contributions")
    st.markdown(
        """
- A practical multimodal fact-checking architecture layered onto current ABSA infrastructure.
- A claim-centric benchmark connecting internal disclosures to external evidence trails.
- A reproducible protocol for provenance-aware ESG verification with uncertainty tagging.
- An expanded ESG analysis frame from sentiment/tone to disclosure reliability.
- Reusable artifacts for greenwashing and misinformation risk studies.
"""
    )

    st.markdown("### 5) Topic of Literature Review")
    st.markdown(
        """
- Automated fact-checking and claim-verification pipelines.
- NLI/entailment methods for support-vs-contradiction reasoning.
- Multimodal fact-checking approaches (text + image + video).
- ESG/greenwashing reliability and external accountability evidence.
- Source credibility modeling for heterogeneous/noisy media.
- Low-resource multilingual verification challenges in Indonesian contexts.
"""
    )

    st.markdown("### 6) Methodology")
    st.markdown(
        f"""
- **Existing internal evidence base:**
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` ({len(pilot):,} rows)
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv` ({len(verifier):,} rows)
  - `results/revision_analysis/failure_modes.csv` ({len(failure):,} rows)
  - `results/revision_analysis/ocr_processing_summary.csv` ({len(ocr_summary):,} rows)
- **Claim unit schema:** `claim_id`, `company`, `claim_text`, `claim_type`, `esg_pillar`, `aspect`, `time_reference`, `source_page_ref`.
- **Pipeline design:** claim extraction -> external retrieval -> relevance/date/entity filtering -> multimodal reasoning -> verdict + confidence + citation bundle.
- **Evaluation:** macro F1 over verdict classes, retrieval precision@k/recall@k, citation correctness, provenance completeness, multimodal ablation.
- **Robustness checks:** temporal drift, sector vocabulary shift, noisy-source stress tests, and human adjudication subset.
- **Operational controls:** calibrate with existing prompt/model stability baselines ({len(prompt_stability):,} prompts; {len(model_stability):,} models).
"""
    )

    st.markdown("### 7) Results Interpretation")
    st.markdown(
        """
- Judge improvements by claim-verification quality and citation fidelity, not narrative fluency.
- Separate verdict accuracy from evidence retrieval quality to locate bottlenecks.
- Analyze performance by claim type (commitment/action/outcome), ESG pillar, and company sector.
- Cross-check failures against known patterns (missing tone, schema drift, ambiguous wording) before concluding model weakness.
"""
    )

    st.markdown("### 8) Discussion")
    st.markdown(
        """
- This extends the system from extraction/classification into disclosure reliability assessment.
- Multimodal evidence can resolve contradictions text-only methods may miss.
- Entity/date mismatch and source noise can create false contradictions and must be controlled.
- Evidence trails improve transparency and auditability for ESG stakeholders.
"""
    )

    st.markdown("### 9) Conclusion")
    st.markdown(
        """
Multimodal fact-checking is feasible in this repository because extraction, provenance, and dashboard primitives already exist. The next milestone is external evidence ingestion plus rigorous verdict evaluation, yielding a reproducible fact-accountability layer for Indonesian ESG analysis.
"""
    )


def main() -> None:
    st.title("Fact-Checking Research Planner")
    st.caption("Built from documentation_fact_checking.md and existing revision-analysis datasets.")

    if DOC_PATH.exists():
        with st.expander("Reference: documentation_fact_checking.md"):
            st.code(DOC_PATH.read_text(encoding="utf-8"), language="markdown")
    else:
        st.warning("documentation_fact_checking.md not found.")

    data = load_data()
    render_dataset_evidence(data)
    st.divider()
    render_research_plan(data)


if __name__ == "__main__":
    main()
