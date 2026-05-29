from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path
from urllib import parse, request

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
DOC_PATH = ROOT_DIR / "documentation_fine_tuning.md"
REV_DIR = ROOT_DIR / "results" / "revision_analysis"
API_BASE = "https://sustainable-framework-api.darisdzakwanhoesien.site"


st.set_page_config(page_title="Fine-Tuning Research Plan", page_icon="🧪", layout="wide")


def _load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _count_top(rows: list[dict], key: str, top_n: int = 8) -> list[tuple[str, int]]:
    ctr = Counter()
    for row in rows:
        value = (row.get(key) or "").strip()
        ctr[value if value else "<BLANK>"] += 1
    return ctr.most_common(top_n)


def _to_markdown_table(items: list[tuple[str, int]], col1: str, col2: str = "count") -> str:
    if not items:
        return "No data available."
    lines = [f"| {col1} | {col2} |", "|---|---:|"]
    for k, v in items:
        lines.append(f"| {k} | {v:,} |")
    return "\n".join(lines)


def _yn(v: str, yes: str = "yes", no: str = "no") -> str:
    s = (v or "").strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return yes
    return no


def _map_sentiment(v: str) -> str:
    s = (v or "").strip().lower()
    if s in {"positive", "negative", "neutral"}:
        return s
    return "neutral"


def _map_social_keyword(esg: str) -> str:
    s = (esg or "").strip().lower()
    return "yes" if "s" in s and s not in {"", "none"} else "no"


def _extract_prediction_label(payload: dict) -> str:
    for key in ["label", "prediction", "predicted_label", "class", "result"]:
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _safe_get(payload: dict, key: str) -> str:
    val = payload.get(key, "")
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def _call_climatebert_logic(params: dict, api_key: str = "", timeout: int = 30) -> dict:
    q = parse.urlencode(params)
    url = f"{API_BASE}/api/v1/climatebert-logic/classify?{q}"
    req = request.Request(url)
    if api_key.strip():
        req.add_header("x-api-key", api_key.strip())
    with request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)


@st.cache_data(show_spinner=False)
def load_evidence() -> dict:
    pilot = _load_csv(REV_DIR / "pilot_ground_truth_annotations.csv")
    silver = _load_csv(REV_DIR / "silver_tone_ground_truth.csv")
    verifier = _load_csv(REV_DIR / "llm_statement_page_verifier_compiled.csv")
    climatebert = _load_csv(REV_DIR / "climatebert_output.csv")
    model_stability = _load_csv(REV_DIR / "model_stability_summary.csv")
    prompt_stability = _load_csv(REV_DIR / "prompt_stability_summary.csv")

    return {
        "pilot": pilot,
        "silver": silver,
        "verifier": verifier,
        "climatebert": climatebert,
        "model_stability": model_stability,
        "prompt_stability": prompt_stability,
    }


def render_dataset_evidence(evd: dict) -> None:
    pilot = evd["pilot"]
    silver = evd["silver"]
    verifier = evd["verifier"]
    climatebert = evd["climatebert"]
    model_stability = evd["model_stability"]
    prompt_stability = evd["prompt_stability"]

    st.subheader("Existing Dataset Evidence")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pilot labeled rows", f"{len(pilot):,}")
    c2.metric("Silver rows", f"{len(silver):,}")
    c3.metric("Verifier rows", f"{len(verifier):,}")
    c4.metric("ClimateBERT rows", f"{len(climatebert):,}")

    st.markdown("**Label distribution snapshots (pilot labels)**")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown(_to_markdown_table(_count_top(pilot, "ground_truth_esg"), "ground_truth_esg"))
        st.markdown(_to_markdown_table(_count_top(pilot, "ground_truth_tone"), "ground_truth_tone"))
    with t2:
        st.markdown(_to_markdown_table(_count_top(pilot, "sentiment"), "sentiment"))
        st.markdown(_to_markdown_table(_count_top(pilot, "ground_truth_aspect"), "ground_truth_aspect"))

    st.markdown("**Stability context from existing runs**")
    s1, s2, s3 = st.columns(3)
    s1.metric("Models in stability summary", f"{len(model_stability):,}")
    s2.metric("Prompts in stability summary", f"{len(prompt_stability):,}")
    s3.metric("Companies in pilot labels", f"{len(set((r.get('company') or '').strip() for r in pilot if (r.get('company') or '').strip())):,}")

    with st.expander("Top prompts and models in current labeled corpus"):
        p1, p2 = st.columns(2)
        p1.markdown(_to_markdown_table(_count_top(pilot, "prompt"), "prompt"))
        p2.markdown(_to_markdown_table(_count_top(pilot, "model"), "model"))


def render_research_plan(evd: dict) -> None:
    st.subheader("Research Plan for Fine-Tuning (Indonesian ESG ABSA)")

    st.markdown("### 1) Research Gap")
    st.markdown(
        """
- Current repository pipelines (rule-based, classical ML, hybrid/deep, and LLM extraction) are active, but there is no standardized supervised fine-tuning benchmark for Indonesian ESG ABSA.
- Existing pilot labels are substantial but not yet operationalized into a strict document-level train/validation/test corpus.
- Existing evaluation emphasizes parse reliability and workflow stability, while controlled parameter-update strategies are not yet the center of evaluation.
- There is no consolidated in-project comparison between full fine-tuning and parameter-efficient fine-tuning (PEFT).
"""
    )

    st.markdown("### 2) Research Questions")
    st.markdown(
        """
1. Can supervised fine-tuning improve Indonesian ESG ABSA performance over current baseline methods in this repository?
2. Which strategy is more suitable in this pipeline: full fine-tuning or PEFT (adapter/LoRA style)?
3. How stable are fine-tuned models across ESG pillars, aspect groups, tone subtypes, and company sectors?
4. What minimum data scale and label-quality threshold are needed to produce reliable gains?
"""
    )

    st.markdown("### 3) Research Objectives")
    st.markdown(
        """
1. Build a reproducible fine-tuning workflow integrated with current project artifacts.
2. Construct a standardized labeled Indonesian ESG ABSA dataset from existing annotation/extraction outputs.
3. Fine-tune one or more pretrained encoders for aspect and sentiment tasks.
4. Compare fine-tuned models against existing baselines.
5. Deliver thesis-ready evidence on gains, limitations, and deployment tradeoffs.
"""
    )

    st.markdown("### 4) Research Contributions")
    st.markdown(
        """
- A practical fine-tuning blueprint for Indonesian ESG ABSA inside an operational thesis system.
- Empirical evidence on in-domain supervised adaptation for ESG aspect-sentiment quality.
- A reproducible evaluation package with aggregate, subgroup, and error-taxonomy diagnostics.
- Engineering tradeoff analysis across accuracy, compute cost, and maintainability.
- Reusable artifacts for future Indonesian ESG NLP benchmarking.
"""
    )

    st.markdown("### 5) Topic of Literature")
    st.markdown(
        """
- Pretraining and supervised fine-tuning in task-specific NLP.
- ABSA in specialized domains (finance/sustainability reports).
- Low-resource fine-tuning behavior (class imbalance, label noise, overfitting control).
- Parameter-efficient fine-tuning (adapters, LoRA, low-rank updates).
- Evaluation rigor beyond top-line F1 (subgroup robustness, calibration, error profiling).
"""
    )

    st.markdown("### 6) Methodology")
    st.markdown(
        f"""
- **Data sources (existing):**
  - `results/revision_analysis/pilot_ground_truth_annotations.csv` ({len(evd['pilot']):,} rows)
  - `results/revision_analysis/silver_tone_ground_truth.csv` ({len(evd['silver']):,} rows)
  - `results/revision_analysis/llm_statement_page_verifier_compiled.csv` ({len(evd['verifier']):,} rows)
  - `results/revision_analysis/climatebert_output.csv` ({len(evd['climatebert']):,} rows)
- **Dataset preparation:** label harmonization (aspect/esg/sentiment/tone), deduplication, noise filtering, and document/company-level split.
- **Training strategies:** full fine-tuning vs PEFT; optional multi-task setup (aspect + sentiment + auxiliary ESG/tone).
- **Evaluation protocol:** macro/weighted F1, precision/recall, accuracy, Cohen’s kappa, confusion matrices.
- **Robustness checks:** repeated seeds, class-weight ablation, subgroup diagnostics by ESG pillar, aspect frequency, tone, and company sector.
- **Codebase integration:** training/eval module in `code/`; outputs in `results/fine_tuning/`; dashboard page under `pages/`.
"""
    )

    st.markdown("### 7) Results Interpretation Plan")
    st.markdown(
        """
- Interpret gains relative to baseline families (rule/classical/hybrid/deep) rather than absolute metric values only.
- Separate aggregate improvements from subgroup behavior to detect hidden instability.
- Attribute errors by category: ambiguous Indonesian phrasing, code-switching, boilerplate disclosures, ontology mismatch.
- Use stability summaries (model/prompt) to contextualize whether gains are robust or configuration-sensitive.
"""
    )

    st.markdown("### 8) Discussion")
    st.markdown(
        """
- Fine-tuning is operationally feasible now because the project already has labeled rows, verifier outputs, and metric infrastructure.
- Label quality and coverage are likely stronger constraints than architecture choice.
- Full fine-tuning may maximize accuracy but PEFT may provide better cost/reproducibility tradeoffs.
- Strong claims should require repeated-run and subgroup evidence, not single-run top-line scores.
"""
    )

    st.markdown("### 9) Conclusion")
    st.markdown(
        """
A fine-tuning research track is feasible and timely in this repository. The next milestone is a clean, leakage-controlled master dataset and controlled comparisons of full fine-tuning vs PEFT against established baselines, with thesis-grade subgroup and stability diagnostics.
"""
    )


def render_climatebert_api_validation(evd: dict) -> None:
    st.subheader("ClimateBERT Logic API Validation")
    st.caption("Run `/api/v1/climatebert-logic/classify` on sampled ground-truth rows and compare API output to existing labels.")

    pilot = evd["pilot"]
    if not pilot:
        st.warning("Pilot ground-truth data is unavailable.")
        return

    c1, c2, c3 = st.columns(3)
    sample_size = c1.number_input("Sample size", min_value=1, max_value=min(1000, len(pilot)), value=min(100, len(pilot)), step=1)
    sample_seed = c2.number_input("Random seed", min_value=0, max_value=999999, value=42, step=1)
    company_filter = c3.text_input("Company contains (optional)", value="")

    api_key = st.text_input("x-api-key (optional)", value="", type="password")
    run_clicked = st.button("Run ClimateBERT Logic API")

    if not run_clicked:
        return

    filtered = pilot
    if company_filter.strip():
        needle = company_filter.strip().lower()
        filtered = [r for r in pilot if needle in (r.get("company") or "").lower()]

    if not filtered:
        st.error("No rows match the selected company filter.")
        return

    rng = random.Random(int(sample_seed))
    n = min(int(sample_size), len(filtered))
    sampled = rng.sample(filtered, n) if n < len(filtered) else filtered[:]

    rows = []
    matches_climate_detector = 0
    matches_climate_commitment = 0
    matches_environmental_claims = 0
    matches_sentiment = 0
    api_success = 0

    with st.spinner(f"Calling API for {n} rows..."):
        for row in sampled:
            params = {
                "climate_detector": _yn(row.get("has_climate_d", "false"), yes="yes", no="no"),
                "climate_commitment": _yn(row.get("has_climate_commitment", "false"), yes="yes", no="no"),
                "environmental_claims": _yn(row.get("has_environmental_claims", "false"), yes="yes", no="no"),
                "netzero_reduction": "none",
                "climate_specificity": "non",
                "climate_tcfd": "none",
                "climate_sentiment": _map_sentiment(row.get("sentiment", "")),
                "social_keyword": _map_social_keyword(row.get("ground_truth_esg", "")),
            }

            api_error = ""
            payload = {}
            predicted_label = ""
            try:
                payload = _call_climatebert_logic(params, api_key=api_key)
                predicted_label = _extract_prediction_label(payload)
                api_success += 1
            except Exception as e:
                api_error = str(e)

            api_cd = _safe_get(payload, "climate_detector").lower()
            api_cc = _safe_get(payload, "climate_commitment").lower()
            api_ec = _safe_get(payload, "environmental_claims").lower()
            api_sent = _safe_get(payload, "climate_sentiment").lower()

            gt_cd = params["climate_detector"].lower()
            gt_cc = params["climate_commitment"].lower()
            gt_ec = params["environmental_claims"].lower()
            gt_sent = params["climate_sentiment"].lower()

            cd_match = api_cd == gt_cd if api_cd else False
            cc_match = api_cc == gt_cc if api_cc else False
            ec_match = api_ec == gt_ec if api_ec else False
            sent_match = api_sent == gt_sent if api_sent else False

            matches_climate_detector += int(cd_match)
            matches_climate_commitment += int(cc_match)
            matches_environmental_claims += int(ec_match)
            matches_sentiment += int(sent_match)

            rows.append(
                {
                    "record_id": row.get("record_id", ""),
                    "company": row.get("company", ""),
                    "ground_truth_tone": row.get("ground_truth_tone", ""),
                    "ground_truth_sentiment": row.get("sentiment", ""),
                    "api_predicted_label": predicted_label,
                    "gt_climate_detector": gt_cd,
                    "api_climate_detector": api_cd,
                    "match_climate_detector": cd_match,
                    "gt_climate_commitment": gt_cc,
                    "api_climate_commitment": api_cc,
                    "match_climate_commitment": cc_match,
                    "gt_environmental_claims": gt_ec,
                    "api_environmental_claims": api_ec,
                    "match_environmental_claims": ec_match,
                    "gt_climate_sentiment": gt_sent,
                    "api_climate_sentiment": api_sent,
                    "match_climate_sentiment": sent_match,
                    "api_error": api_error,
                }
            )

    denom = max(n, 1)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("API success", f"{api_success}/{n}")
    m2.metric("Match climate_detector", f"{(matches_climate_detector/denom)*100:.1f}%")
    m3.metric("Match climate_commitment", f"{(matches_climate_commitment/denom)*100:.1f}%")
    m4.metric("Match environmental_claims", f"{(matches_environmental_claims/denom)*100:.1f}%")
    m5.metric("Match climate_sentiment", f"{(matches_sentiment/denom)*100:.1f}%")

    st.dataframe(rows, use_container_width=True)

    out_path = ROOT_DIR / "results" / "fine_tuning" / "climatebert_api_validation_latest.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    st.caption(f"Saved latest validation output to `{out_path}`")


def main() -> None:
    st.title("Fine-Tuning Research Planner")
    st.caption("Built from documentation_fine_tuning.md and existing revision-analysis datasets.")

    if DOC_PATH.exists():
        with st.expander("Reference: documentation_fine_tuning.md"):
            st.code(DOC_PATH.read_text(encoding="utf-8"), language="markdown")
    else:
        st.warning("documentation_fine_tuning.md not found.")

    evidence = load_evidence()
    render_dataset_evidence(evidence)
    st.divider()
    render_climatebert_api_validation(evidence)
    st.divider()
    render_research_plan(evidence)


if __name__ == "__main__":
    main()
