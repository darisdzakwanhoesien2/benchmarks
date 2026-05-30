from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
DOC_PATH = ROOT_DIR / "documentation_chatbot.md"
REV_DIR = ROOT_DIR / "results" / "revision_analysis"


st.set_page_config(page_title="Chatbot Research Plan", page_icon="💬", layout="wide")


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
        val = (row.get(key) or "").strip()
        ctr[val if val else "<BLANK>"] += 1
    return ctr.most_common(n)


def _table(items: list[tuple[str, int]], key_name: str, count_name: str = "count") -> str:
    if not items:
        return "No data available."
    lines = [f"| {key_name} | {count_name} |", "|---|---:|"]
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
    ontology = _load_csv(REV_DIR / "ontology_coverage.csv")

    return {
        "pilot": pilot,
        "verifier": verifier,
        "failure": failure,
        "prompt_stability": prompt_stability,
        "model_stability": model_stability,
        "ontology": ontology,
    }


def render_dataset_evidence(data: dict) -> None:
    pilot = data["pilot"]
    verifier = data["verifier"]
    failure = data["failure"]
    prompt_stability = data["prompt_stability"]
    model_stability = data["model_stability"]
    ontology = data["ontology"]

    st.subheader("Existing Dataset Evidence")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pilot labeled rows", f"{len(pilot):,}")
    c2.metric("Verifier rows", f"{len(verifier):,}")
    c3.metric("Failure rows", f"{len(failure):,}")
    c4.metric("Ontology aspects", f"{len(ontology):,}")

    s1, s2, s3 = st.columns(3)
    exact = sum(1 for r in verifier if (r.get("best_status") or "").strip().lower() == "exact")
    s1.metric("Verifier exact matches", f"{exact:,}")
    s2.metric("Prompt configs", f"{len(prompt_stability):,}")
    s3.metric("Model configs", f"{len(model_stability):,}")

    st.markdown("**Ground-truth and verifier distribution snapshots**")
    a, b = st.columns(2)
    with a:
        st.markdown(_table(_top(pilot, "ground_truth_esg"), "ground_truth_esg"))
        st.markdown(_table(_top(pilot, "ground_truth_tone"), "ground_truth_tone"))
        st.markdown(_table(_top(pilot, "sentiment"), "sentiment"))
    with b:
        st.markdown(_table(_top(verifier, "best_status"), "verifier_best_status"))
        st.markdown(_table(_top(failure, "failure_modes"), "failure_modes"))
        st.markdown(_table(_top(pilot, "company"), "company"))


def render_research_plan(data: dict) -> None:
    pilot = data["pilot"]
    verifier = data["verifier"]
    failure = data["failure"]
    prompt_stability = data["prompt_stability"]
    model_stability = data["model_stability"]
    ontology = data["ontology"]

    st.subheader("Research Plan for Indonesian ESG ABSA Chatbot")

    st.info(
        "This page renders a repo-grounded research plan. For a thesis-style write-up, see "
        "`documentation_chatbot.md` (feasibility) and `documentation_chatbot_research.md` (full track)."
    )

    st.markdown("### 1) Research Gap")
    st.markdown(
        """
- Existing ESG ABSA workflows are dashboard-oriented and not conversational for Indonesian-language query tasks.
- Structured outputs exist, but they are not yet systematically transformed into citation-grounded chatbot responses.
- Evidence traceability exists in artifacts and verifier outputs, but not consistently exposed in real-time chat answers.
- There is no formal chatbot benchmark in this repository for factuality, grounding, ABSA consistency, and safety.
"""
    )

    st.markdown("### 2) Research Questions")
    st.markdown(
        """
1. Can a grounded chatbot answer Indonesian ESG ABSA queries accurately using existing project artifacts?
2. Which architecture is strongest in this codebase: direct prompting, RAG, or workflow-guided hybrid routing?
3. How reliably can the chatbot preserve aspect, ESG pillar, sentiment, and tone semantics in conversation?
4. What dominant failure modes appear in Indonesian ESG chatbot outputs, and what controls mitigate them?
"""
    )

    st.markdown("### 3) Research Objectives")
    st.markdown(
        """
1. Build a reproducible chatbot layer over existing ESG ABSA outputs.
2. Support Indonesian queries over company disclosures, aspects, sentiment/tone, and ontology links.
3. Require source-grounded responses with explicit evidence references.
4. Evaluate chatbot quality with task-specific metrics and failure-mode analysis.
5. Integrate chatbot findings into thesis dashboard/chapter reporting.
"""
    )

    st.markdown("### 4) Research Contributions")
    st.markdown(
        """
- A practical, evidence-grounded Indonesian ESG ABSA chatbot architecture.
- A method to translate structured ABSA artifacts into conversational insights with citations.
- A reproducible chatbot evaluation framework emphasizing faithfulness and ABSA alignment.
- A failure-mode taxonomy for ESG conversational analytics.
- Reusable artifacts for future ESG decision-support interfaces.
"""
    )

    st.markdown("### 5) Topic of Literature Review")
    st.markdown(
        """
- Task-oriented and retrieval-augmented chatbots for domain QA.
- Hallucination control, faithfulness, and citation-grounding in conversational AI.
- Financial/ESG assistant design with interpretability and auditability constraints.
- Multilingual chatbot methods for Indonesian and code-switched inputs.
- Evaluation frameworks for relevance, factuality, consistency, and trust.
"""
    )

    st.markdown("### 6) Methodology")
    st.markdown(
        f"""
- **Existing dataset foundation:**
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` ({len(pilot):,} rows)
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv` ({len(verifier):,} rows)
  - `results/revision_analysis/failure_modes.csv` ({len(failure):,} rows)
  - `results/revision_analysis/ontology_coverage.csv` ({len(ontology):,} rows)
- **Architecture experiments:**
  - direct prompt-over-records,
  - RAG with statement/page retrieval,
  - hybrid intent-routing to specialized handlers (aspect/tone/company/ontology).
- **Language pipeline:** Indonesian query normalization, bilingual term mapping, ambiguity clarification prompts.
- **Evaluation protocol:** relevance, factuality, completeness, ABSA-consistency, citation-presence/correctness, repeated-query consistency.
- **Operational diagnostics:** use existing prompt/model stability summaries ({len(prompt_stability):,} prompts; {len(model_stability):,} models) and failure patterns to stress-test robustness.
- **Integration artifacts:** store chatbot logs/eval under `results/chatbot/`; surface metrics in Streamlit and chapter dashboards.
"""
    )

    st.markdown("### 7) Results Interpretation")
    st.markdown(
        """
- Interpret chatbot gains by grounded-answer quality, not fluency alone.
- Compare architectures on citation correctness and ABSA semantic alignment.
- Separate aggregate quality from subgroup behavior by company, ESG pillar, and tone.
- Map error patterns to known failure modes (e.g., missing tone, schema drift, ambiguous phrasing).
"""
    )

    st.markdown("### 8) Discussion")
    st.markdown(
        """
- Chatbot interaction can improve accessibility of complex ESG ABSA findings for non-technical users.
- Strong grounding controls are required so fluent responses do not mask factual errors.
- Retrieval depth and verification checks increase reliability but may add latency and complexity.
- Upstream OCR/extraction quality remains a primary constraint on chatbot answer quality.
"""
    )

    st.markdown("### 9) Conclusion")
    st.markdown(
        """
An Indonesian ESG ABSA chatbot is feasible with the current repository assets. The core requirement is a grounding-first architecture plus rigorous evaluation so chat responses remain auditable, semantically consistent, and thesis-grade.
"""
    )

    st.markdown("### 10) Where to Continue in This Repo")
    st.markdown(
        """
- Full research write-up: `documentation_chatbot_research.md`
- Feasibility notes: `documentation_chatbot.md`
- Add implementation artifacts under: `results/chatbot/` (recommended)
"""
    )


def main() -> None:
    st.title("Chatbot Research Planner")
    st.caption("Built from documentation_chatbot.md and existing revision-analysis datasets.")

    if DOC_PATH.exists():
        with st.expander("Reference: documentation_chatbot.md"):
            st.code(DOC_PATH.read_text(encoding="utf-8"), language="markdown")
    else:
        st.warning("documentation_chatbot.md not found.")

    data = load_data()
    render_dataset_evidence(data)
    st.divider()
    render_research_plan(data)


if __name__ == "__main__":
    main()
