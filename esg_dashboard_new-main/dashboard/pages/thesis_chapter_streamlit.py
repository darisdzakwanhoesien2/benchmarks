from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import pandas as pd
import streamlit as st

from utils.data_loader import format_display_value


PAGES_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = PAGES_DIR.parent
RESULTS_DIR = DASHBOARD_DIR / "results"
REV_DIR = RESULTS_DIR / "revision_analysis"

DOCX_PATH = DASHBOARD_DIR / "pages" / "Thesis_Complete_Narrative.docx"
PDF_PATH = DASHBOARD_DIR / "pages" / "thesis_draft_1.pdf"


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return pd.DataFrame()


def _safe_metric(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def data_bundle() -> dict[str, pd.DataFrame]:
    """
    Loads any thesis artifacts that exist under `dashboard/results/revision_analysis/`.
    Returns a dict with stable keys so pages can render even when artifacts are missing.
    """
    return {
        "model_stability": _load_csv(REV_DIR / "model_stability_summary.csv"),
        "prompt_stability": _load_csv(REV_DIR / "prompt_stability_summary.csv"),
        "agreement": _load_csv(REV_DIR / "climatebert_proxy_agreement_summary.csv"),
        "ontology": _load_csv(REV_DIR / "ontology_coverage.csv"),
        "inventory": _load_csv(REV_DIR / "artifact_inventory.csv"),
        "citations": _load_csv(REV_DIR / "citation_table.csv"),
    }


def evidence_metrics(bundle: dict[str, pd.DataFrame]) -> dict[str, Any]:
    agreement = bundle.get("agreement", pd.DataFrame())
    ontology = bundle.get("ontology", pd.DataFrame())
    inventory = bundle.get("inventory", pd.DataFrame())

    percent_agreement = 0.0
    kappa = 0.0
    if not agreement.empty:
        for col in ["percent_agreement", "agreement", "pct_agreement"]:
            if col in agreement.columns:
                percent_agreement = _safe_metric(agreement.iloc[0].get(col), 0.0)
                if percent_agreement > 1.0:
                    percent_agreement = percent_agreement / 100.0
                break
        for col in ["kappa", "cohen_kappa"]:
            if col in agreement.columns:
                kappa = _safe_metric(agreement.iloc[0].get(col), 0.0)
                break

    ontology_mapped = 0
    ontology_total = 0
    if not ontology.empty:
        mapped_col = next((c for c in ["mapped", "mapped_count", "mapped_rows"] if c in ontology.columns), None)
        total_col = next((c for c in ["total", "total_count", "total_rows"] if c in ontology.columns), None)
        if mapped_col:
            ontology_mapped = int(pd.to_numeric(ontology[mapped_col], errors="coerce").fillna(0).sum())
        if total_col:
            ontology_total = int(pd.to_numeric(ontology[total_col], errors="coerce").fillna(0).sum())
        if not ontology_total and "status" in ontology.columns:
            ontology_total = int(len(ontology))
            ontology_mapped = int((ontology["status"].astype(str).str.lower() == "mapped").sum())

    artifacts = int(len(inventory)) if inventory is not None and not inventory.empty else 0

    return {
        "percent_agreement": percent_agreement,
        "kappa": kappa,
        "ontology_mapped": ontology_mapped,
        "ontology_total": ontology_total,
        "artifacts": artifacts,
    }


def metric_row(bundle: dict[str, pd.DataFrame]) -> None:
    m = evidence_metrics(bundle)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Agreement", f"{m['percent_agreement']:.1%}" if m["percent_agreement"] else "n/a")
    c2.metric("Kappa", f"{m['kappa']:.3f}" if m["kappa"] else "n/a")
    c3.metric("Ontology mapped", f"{m['ontology_mapped']:,}")
    c4.metric("Artifacts", f"{m['artifacts']:,}")


def citation_table(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df = bundle.get("citations", pd.DataFrame())
    if df is None or df.empty:
        return pd.DataFrame(columns=["citation", "artifact", "note"])
    return df


def _simple_bar(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty or x not in df.columns or y not in df.columns:
        st.info(f"Missing artifact for: {title}")
        return
    try:
        st.bar_chart(df.set_index(x)[y], height=280)
    except Exception:
        st.dataframe(df, use_container_width=True, hide_index=True)


def model_stability_chart(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("Missing `model_stability_summary.csv`.")
        return
    view = df.copy()
    if "model" in view.columns and "json_parse_success_rate" in view.columns:
        view["json_parse_success_rate"] = pd.to_numeric(view["json_parse_success_rate"], errors="coerce").fillna(0.0)
        view = view.sort_values("json_parse_success_rate", ascending=False).head(20)
        _simple_bar(view, "model", "json_parse_success_rate", "Model stability (parse success)")
    else:
        st.dataframe(view, use_container_width=True, hide_index=True, height=360)


def prompt_stability_chart(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("Missing `prompt_stability_summary.csv`.")
        return
    view = df.copy()
    if "prompt" in view.columns and "missing_tone_rate" in view.columns:
        view["missing_tone_rate"] = pd.to_numeric(view["missing_tone_rate"], errors="coerce").fillna(1.0)
        view = view.sort_values("missing_tone_rate", ascending=True).head(20)
        _simple_bar(view, "prompt", "missing_tone_rate", "Prompt stability (missing tone rate)")
    else:
        st.dataframe(view, use_container_width=True, hide_index=True, height=360)


def agreement_chart(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("Missing `climatebert_proxy_agreement_summary.csv`.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True, height=240)


def ontology_chart(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("Missing `ontology_coverage.csv`.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True, height=320)


def artifact_chart(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        st.info("Missing `artifact_inventory.csv`.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True, height=360)


def render_mermaid(code: str, height: int = 520) -> None:
    """
    Reuse the mermaid renderer from `_rq_thesis_content` when available; otherwise
    fall back to a plain code block so the page still works.
    """
    try:
        from _rq_thesis_content import render_mermaid as _render

        return _render(code, height=height)
    except Exception:
        st.code(code, language="text")


def thesis_spine_mermaid() -> str:
    return "\n".join(
        [
            "flowchart TD",
            '  RQ["Research Questions"] --> PIPE["Pipeline (OCR → LLM → ABSA)"]',
            '  PIPE --> ART["Artifacts (CSV/JSON)"]',
            '  ART --> CH4["Chapter 4 Results"]',
            '  ART --> CH5["Chapter 5 Discussion"]',
            '  ART --> CH6["Chapter 6 Conclusion"]',
            '  CH4 --> DASH["Dashboard pages"]',
            '  CH5 --> DASH',
            '  CH6 --> DASH',
        ]
    )


def rq_evidence_mermaid() -> str:
    return "\n".join(
        [
            "flowchart LR",
            '  RQ1["RQ1 Data + Corpus"] --> A1["OCR audit"]',
            '  RQ2["RQ2 ABSA labels"] --> A2["Tone/ESG charts"]',
            '  RQ3["RQ3 Climate construct"] --> A3["ClimateBERT comparison"]',
            '  RQ4["RQ4 Diagnostics"] --> A4["Failure + ontology gaps"]',
            '  RQ5["RQ5 Reproducibility"] --> A5["Artifacts + dashboard"]',
            '  RQ6["RQ6 Stability"] --> A6["Model/prompt stability"]',
        ]
    )


def pipeline_mermaid() -> str:
    return "\n".join(
        [
            "flowchart LR",
            '  PDF["PDF reports"] --> OCR["OCR/Text extraction"]',
            '  OCR --> LLM["LLM extraction"]',
            '  LLM --> JSON["Structured ESG JSON"]',
            '  JSON --> FLAT["Flatten records (CSV)"]',
            '  FLAT --> VALID["Validation + diagnostics"]',
            '  VALID --> FIG["Charts + tables"]',
        ]
    )


def validation_mermaid() -> str:
    return "\n".join(
        [
            "flowchart TD",
            '  SILVER["Silver annotation set"] --> AGREEMENT["Agreement metrics"]',
            '  OUTPUTS["Model outputs"] --> AGREEMENT',
            '  OUTPUTS --> ONTO["Ontology mapping coverage"]',
            '  OUTPUTS --> FAIL["Failure-mode audit"]',
            '  OUTPUTS --> STAB["Stability tables"]',
        ]
    )


def artifact_mermaid() -> str:
    return "\n".join(
        [
            "flowchart LR",
            '  INPUT["Inputs"] --> RUNS["Runs (configs/logs)"]',
            '  RUNS --> OUTPUT["Outputs (CSV/JSON)"]',
            '  OUTPUT --> PAGES["Streamlit pages"]',
            '  OUTPUT --> CHAPTERS["Thesis chapters"]',
        ]
    )


def _maybe_read_docx_outline(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame([{"section": "missing", "text": f"Missing DOCX: {path}"}])
    try:
        from zipfile import ZipFile
        from xml.etree import ElementTree as ET

        W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
        rows = []
        for para in root.findall(f".//{W_NS}p"):
            text = "".join(t.text or "" for t in para.findall(f".//{W_NS}t")).strip()
            if text:
                rows.append({"section": "docx", "text": text})
        return pd.DataFrame(rows[:400])
    except Exception as exc:
        return pd.DataFrame([{"section": "error", "text": f"Could not read DOCX: {exc}"}])


def chapter_outline() -> pd.DataFrame:
    return _maybe_read_docx_outline(DOCX_PATH)


def pdf_outline() -> pd.DataFrame:
    if not PDF_PATH.exists():
        return pd.DataFrame([{"page": 0, "text": f"Missing PDF: {PDF_PATH}"}])
    return pd.DataFrame([{"page": 0, "text": "PDF outline extraction not configured in this template."}])

