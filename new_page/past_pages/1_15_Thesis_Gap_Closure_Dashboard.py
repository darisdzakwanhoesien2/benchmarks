from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from statistics import mean

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="Thesis Gap Closure Dashboard", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "results" / "revision_analysis"


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _bootstrap_ci(values: list[float], n_boot: int = 2000, alpha: float = 0.05) -> tuple[float, float, float]:
    if not values:
        return 0.0, 0.0, 0.0
    import random

    rng = random.Random(42)
    boots = []
    n = len(values)
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        boots.append(mean(sample))
    boots.sort()
    lo = boots[int((alpha / 2) * len(boots))]
    hi = boots[int((1 - alpha / 2) * len(boots)) - 1]
    return mean(values), lo, hi


ID_HINTS = {
    "dan",
    "yang",
    "dengan",
    "untuk",
    "pada",
    "tahun",
    "emisi",
    "limbah",
    "konsumsi",
    "energi",
    "lingkungan",
    "perusahaan",
    "penurunan",
    "dibandingkan",
}
EN_HINTS = {
    "and",
    "with",
    "for",
    "in",
    "year",
    "emission",
    "waste",
    "energy",
    "company",
    "environment",
    "decrease",
    "increase",
}


def _suspect_language(text: str) -> tuple[str, float, int, int]:
    tokens = re.findall(r"[a-zA-Z']+", (text or "").lower())
    if not tokens:
        return "unknown", 0.0, 0, 0
    id_hits = sum(1 for t in tokens if t in ID_HINTS)
    en_hits = sum(1 for t in tokens if t in EN_HINTS)
    total_hits = id_hits + en_hits
    if total_hits == 0:
        return "unknown", 0.0, id_hits, en_hits
    if id_hits > en_hits:
        return "id", id_hits / total_hits, id_hits, en_hits
    if en_hits > id_hits:
        return "en", en_hits / total_hits, id_hits, en_hits
    return "mixed", 0.5, id_hits, en_hits


pilot = _read_csv(REV / "pilot_ground_truth_annotations.csv")
verifier = _read_csv(REV / "llm_statement_page_verifier_compiled.csv")
failure = _read_csv(REV / "failure_modes.csv")
ontology = _read_csv(REV / "ontology_coverage_full.csv")
greenwashing = _read_csv(REV / "greenwashing_index_by_company.csv")
prompt_stability = _read_csv(REV / "prompt_stability_summary.csv")
model_stability = _read_csv(REV / "model_stability_summary.csv")


st.title("Thesis Gap Closure Dashboard")
st.caption("Implements the strategic improvements from improvement_001.md using current revision-analysis artifacts.")

tabs = st.tabs(
    [
        "Baseline Hierarchy",
        "Significance Layer",
        "Error Taxonomy",
        "Greenwashing Validation",
        "Ontology Contribution",
        "Bilingual + Temporal",
        "Threats to Validity",
        "Ablation Plan",
    ]
)

with tabs[0]:
    st.subheader("1) Experimental Baseline Hierarchy")
    baseline_rows = [
        {"method": "VADER", "purpose": "generic sentiment baseline", "status": "planned baseline"},
        {"method": "FinBERT", "purpose": "financial-domain baseline", "status": "planned baseline"},
        {"method": "ClimateBERT", "purpose": "climate-domain baseline", "status": "partially implemented"},
        {"method": "LLM ABSA", "purpose": "current proposed core", "status": "implemented"},
        {"method": "LLM + Ontology", "purpose": "enhanced proposed core", "status": "implemented"},
    ]
    st.dataframe(pd.DataFrame(baseline_rows), use_container_width=True, hide_index=True)
    st.info(
        "Current repo already supports LLM ABSA and ontology-enhanced pipelines. "
        "This table formalizes the benchmark order for Chapter 4/5 comparisons."
    )

with tabs[1]:
    st.subheader("2) Significance and Confidence Layer")
    st.markdown("Bootstrap 95% CI is computed over verifier exact-match indicator and per-prompt stability rates.")

    exact_values = [1.0 if (r.get("best_status") or "").strip().lower() == "exact" else 0.0 for r in verifier]
    exact_mean, exact_lo, exact_hi = _bootstrap_ci(exact_values)

    c1, c2, c3 = st.columns(3)
    c1.metric("Verifier rows", f"{len(verifier):,}")
    c2.metric("Exact-match rate", f"{exact_mean*100:.2f}%")
    c3.metric("95% CI", f"[{exact_lo*100:.2f}%, {exact_hi*100:.2f}%]")

    per_prompt = []
    for r in prompt_stability:
        per_prompt.append(
            {
                "prompt": r.get("prompt", ""),
                "json_parse_success_rate": _to_float(r.get("json_parse_success_rate", "0")),
                "field_completion_rate": _to_float(r.get("field_completion_rate", "0")),
                "missing_tone_rate": _to_float(r.get("missing_tone_rate", "0")),
            }
        )
    st.dataframe(pd.DataFrame(per_prompt), use_container_width=True, hide_index=True)

with tabs[2]:
    st.subheader("3) Formal Error Taxonomy")
    freq = Counter((r.get("failure_modes") or "").strip().lower() for r in failure)
    tax_rows = [{"error_type": k if k else "<blank>", "count": v} for k, v in freq.most_common(20)]
    st.dataframe(pd.DataFrame(tax_rows), use_container_width=True, hide_index=True)

    st.markdown("Canonical categories for thesis write-up:")
    canonical = [
        {"category": "OCR Error", "signal": "table_or_numeric_layout, parsing artifacts"},
        {"category": "Translation / Bilingual", "signal": "bilingual_or_code_switched, domain term drift"},
        {"category": "Ontology Error", "signal": "unmapped or weakly mapped aspect"},
        {"category": "Tone Error", "signal": "missing_tone, commitment/action/outcome confusion"},
        {"category": "Prompt Error", "signal": "schema_drift, unstable extraction fields"},
        {"category": "ClimateBERT Error", "signal": "climate detection mismatch"},
    ]
    st.dataframe(pd.DataFrame(canonical), use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("4) Greenwashing Validation Layer")
    st.markdown("Current artifact coverage:")
    st.metric("Greenwashing rows", f"{len(greenwashing):,}")
    st.markdown(
        """
**Metric logic used in this artifact**

- `commitment_share`:
  - proportion of rows for a company tagged as `commitment`.
  - practical form: `commitment / records`.
- `outcome_share`:
  - proportion of rows tagged as `outcome`.
  - practical form: `outcome / records`.
- `greenwashing_index`:
  - proxy index intended to reflect imbalance between promise-heavy (`commitment`) and realized-result (`outcome`) language.
  - higher values imply commitment-heavy disclosure relative to outcome evidence.
  - the exact smoothing/scaling formula is not stored in this CSV, so treat it as a **derived proxy** and keep formula provenance explicit in thesis text.
"""
    )

    gw_df = pd.DataFrame(greenwashing)
    if not gw_df.empty:
        gw_df["commitment_share_recalc"] = gw_df.apply(
            lambda r: (_to_float(r.get("commitment", 0)) / _to_float(r.get("records", 1), 1.0))
            if _to_float(r.get("records", 0), 0.0) > 0
            else 0.0,
            axis=1,
        )
        gw_df["outcome_share_recalc"] = gw_df.apply(
            lambda r: (_to_float(r.get("outcome", 0)) / _to_float(r.get("records", 1), 1.0))
            if _to_float(r.get("records", 0), 0.0) > 0
            else 0.0,
            axis=1,
        )
        gw_df["commitment_outcome_ratio_proxy"] = gw_df.apply(
            lambda r: (_to_float(r["commitment_share_recalc"]) / max(_to_float(r["outcome_share_recalc"]), 1e-6)),
            axis=1,
        )
        st.dataframe(gw_df, use_container_width=True, hide_index=True)

        st.markdown("### Company-level metric view")
        companies = sorted(gw_df["company"].astype(str).unique().tolist())
        selected_company = st.selectbox("Select company", companies, index=0, key="gw_company_select")
        row_df = gw_df[gw_df["company"].astype(str).eq(str(selected_company))].copy()
        if row_df.empty:
            st.info("No row found for selected company.")
        else:
            row = row_df.iloc[0]
            viz_rows = [
                {"metric": "greenwashing_index", "value": _to_float(row.get("greenwashing_index", 0.0))},
                {"metric": "commitment_share", "value": _to_float(row.get("commitment_share", 0.0))},
                {"metric": "outcome_share", "value": _to_float(row.get("outcome_share", 0.0))},
                {"metric": "commitment_share_recalc", "value": _to_float(row.get("commitment_share_recalc", 0.0))},
                {"metric": "outcome_share_recalc", "value": _to_float(row.get("outcome_share_recalc", 0.0))},
                {"metric": "commitment_outcome_ratio_proxy", "value": _to_float(row.get("commitment_outcome_ratio_proxy", 0.0))},
            ]
            viz_df = pd.DataFrame(viz_rows)

            c1, c2 = st.columns([1.2, 2.2])
            with c1:
                st.dataframe(viz_df, use_container_width=True, hide_index=True, height=280)
            with c2:
                chart = (
                    alt.Chart(viz_df)
                    .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
                    .encode(
                        x=alt.X("value:Q", title="Value"),
                        y=alt.Y("metric:N", sort="-x", title=None),
                        tooltip=[alt.Tooltip("metric:N"), alt.Tooltip("value:Q", format=".6f")],
                        color=alt.value("#6c5ce7"),
                    )
                    .properties(height=280)
                )
                st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No greenwashing rows available.")

    st.warning(
        "Gap remains: this is an index/proxy artifact. Add expert-labeled greenwashing cases and agreement tests "
        "(human vs system) to claim validated greenwashing detection."
    )

with tabs[4]:
    st.subheader("5) Ontology Contribution Analysis")
    mapped_counter = Counter((r.get("mapped_to_ontology") or "").strip().lower() for r in ontology)
    st.metric("Ontology coverage rows", f"{len(ontology):,}")
    st.metric("Mapped=true rows", f"{mapped_counter.get('true', 0):,}")

    examples = []
    for r in ontology[:30]:
        examples.append(
            {
                "aspect": r.get("aspect", ""),
                "suggested_path": r.get("suggested_path", ""),
                "records": r.get("records", ""),
            }
        )
    st.markdown("Sample contribution rows (quick view):")
    st.dataframe(pd.DataFrame(examples), use_container_width=True, hide_index=True)

    st.markdown("Editable ontology contribution table (working sheet):")
    edit_cols = ["aspect", "suggested_path", "records", "mapped_to_ontology"]
    editable_df = pd.DataFrame(ontology)[edit_cols] if ontology else pd.DataFrame(columns=edit_cols)
    edited_df = st.data_editor(
        editable_df,
        use_container_width=True,
        num_rows="dynamic",
        key="ontology_edit_table",
    )
    st.download_button(
        "Download edited ontology table (CSV)",
        edited_df.to_csv(index=False).encode("utf-8"),
        file_name="ontology_contribution_edited.csv",
        mime="text/csv",
    )

    st.markdown("Full ontology coverage table (all rows):")
    full_df = pd.DataFrame(ontology)
    st.dataframe(full_df, use_container_width=True, hide_index=True)
    st.info("Use these rows to document Indonesian ESG vocabulary/path contributions as a distinct thesis novelty section.")

with tabs[5]:
    st.subheader("6) Bilingual + Temporal Analysis")
    lang_counter = Counter((r.get("language") or "").strip().lower() or "<blank>" for r in pilot)
    st.markdown("Language distribution in pilot annotations:")
    st.dataframe(
        pd.DataFrame([{"language": k, "count": v} for k, v in lang_counter.most_common()]),
        use_container_width=True,
        hide_index=True,
    )

    blank_rows = [r for r in pilot if not (r.get("language") or "").strip()]
    st.metric("Rows with language=<blank>", f"{len(blank_rows):,}")
    st.caption("Below is a heuristic suspicion pass over `<blank>` rows. This is not a replacement for human validation.")
    suspect_preview = []
    for r in blank_rows[:500]:
        pred_lang, conf, id_hits, en_hits = _suspect_language(r.get("text", ""))
        suspect_preview.append(
            {
                "record_id": r.get("record_id", ""),
                "company": r.get("company", ""),
                "predicted_language": pred_lang,
                "confidence": round(conf, 3),
                "id_hits": id_hits,
                "en_hits": en_hits,
                "text_preview": (r.get("text", "") or "").replace("\n", " ")[:180],
            }
        )
    suspect_df = pd.DataFrame(suspect_preview)
    st.dataframe(suspect_df, use_container_width=True, hide_index=True)
    if not suspect_df.empty:
        st.download_button(
            "Download suspected language labels (sample)",
            suspect_df.to_csv(index=False).encode("utf-8"),
            file_name="language_blank_suspected_sample.csv",
            mime="text/csv",
        )

    year_counter = Counter()
    for r in pilot:
        company = (r.get("company") or "").lower()
        for y in ["2023", "2024", "2025", "2026"]:
            if y in company:
                year_counter[y] += 1
    st.markdown("Year signal inferred from company/document naming:")
    st.dataframe(
        pd.DataFrame([{"year": k, "count": v} for k, v in sorted(year_counter.items())]),
        use_container_width=True,
        hide_index=True,
    )
    st.warning("Temporal analysis is currently weakly proxied by naming. Add explicit report-year metadata for rigorous trend claims.")

with tabs[6]:
    st.subheader("7) Threats to Validity (Structured)")
    threats = [
        {"type": "Internal validity", "risk": "Prompt/model sensitivity may shift outputs across runs.", "mitigation": "Use prompt/model stability summaries and repeated-run tests."},
        {"type": "Construct validity", "risk": "Tone may not equal ESG quality or truthfulness.", "mitigation": "Add fact-checking and greenwashing expert labels."},
        {"type": "External validity", "risk": "Dataset concentrated on selected Indonesian reports.", "mitigation": "Expand sectors/years and cross-corpus evaluation."},
        {"type": "Conclusion validity", "risk": "Limited adjudicated labels can inflate uncertainty.", "mitigation": "Increase labeled sample and report confidence intervals."},
    ]
    st.dataframe(pd.DataFrame(threats), use_container_width=True, hide_index=True)

with tabs[7]:
    st.subheader("8) Ablation Study Plan")
    st.markdown("Comprehensive execution plan")
    ablation = [
        {
            "phase": "A0",
            "configuration": "LLM only",
            "what_to_run": "Use current extraction outputs without ontology remapping or tone constraints.",
            "deliverables": "Base prediction table, macro/weighted F1, coverage.",
            "acceptance": "Reproducible baseline with fixed split and seed.",
        },
        {
            "phase": "A1",
            "configuration": "LLM + ontology",
            "what_to_run": "Apply ontology path normalization and remap aspects before scoring.",
            "deliverables": "A0 + mapped/unmapped stats + per-aspect delta.",
            "acceptance": "Coverage improves or unmapped rate decreases with no large F1 collapse.",
        },
        {
            "phase": "A2",
            "configuration": "LLM + ontology + tone",
            "what_to_run": "Include tone constraints and tone-consistency checks in post-processing.",
            "deliverables": "A1 + tone consistency matrix + commitment/outcome/action stability.",
            "acceptance": "Missing-tone and schema-drift rates decrease with stable ABSA scores.",
        },
        {
            "phase": "A3",
            "configuration": "Full pipeline (+ verifier + diagnostics)",
            "what_to_run": "Add statement-page verification and failure-mode diagnostics.",
            "deliverables": "A2 + verifier exact/likely/possible + failure taxonomy report.",
            "acceptance": "Grounding quality and reliability evidence are thesis-ready.",
        },
        {
            "phase": "A4",
            "configuration": "External baseline comparison",
            "what_to_run": "Compare A3 against VADER/FinBERT/ClimateBERT where applicable.",
            "deliverables": "Comparative table + confidence intervals + significance test results.",
            "acceptance": "Proposed pipeline shows statistically defensible gains on target tasks.",
        },
    ]
    st.dataframe(pd.DataFrame(ablation), use_container_width=True, hide_index=True)

    st.markdown("Execution checklist")
    checklist = [
        {"step": 1, "task": "Freeze dataset split by company/document", "why": "Prevents leakage and keeps ablation fair."},
        {"step": 2, "task": "Lock metrics schema (macro-F1, weighted-F1, coverage, exact-rate, missing-tone)", "why": "Ensures apples-to-apples comparisons."},
        {"step": 3, "task": "Run A0-A4 with >=3 seeds each", "why": "Quantifies run variance and stability."},
        {"step": 4, "task": "Compute bootstrap CI and paired significance tests (e.g., McNemar where valid)", "why": "Supports conclusion validity."},
        {"step": 5, "task": "Produce subgroup breakdowns (ESG pillar, aspect frequency, company, language)", "why": "Avoids hidden regressions in aggregate-only reporting."},
        {"step": 6, "task": "Attach failure-mode deltas between phases", "why": "Shows which module fixes which error category."},
        {"step": 7, "task": "Write chapter-ready interpretation template per phase", "why": "Accelerates thesis writing with reproducible evidence blocks."},
    ]
    st.dataframe(pd.DataFrame(checklist), use_container_width=True, hide_index=True)

    st.markdown(
        "Minimum reporting bundle per phase: `predictions.csv`, `metrics.json/csv`, `confusion_matrix.csv`, "
        "`subgroup_metrics.csv`, and `failure_mode_counts.csv`."
    )
