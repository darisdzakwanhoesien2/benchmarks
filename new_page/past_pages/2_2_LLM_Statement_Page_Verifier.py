from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
from html import escape
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from _page_runtime_controls import apply_page_runtime_controls


st.set_page_config(page_title="LLM Statement Page Verifier", layout="wide")
apply_page_runtime_controls(__file__)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
VIS_DIR = RESULTS_DIR / "visualizations"
DATASET_DIR = ROOT / "data" / "thesis_dataset"
T3_PATH = RESULTS_DIR / "esg_records.json"
TONE_FLAT_PATH = VIS_DIR / "tone_records_flat.csv"
COMPILED_VERIFICATION_PATH = RESULTS_DIR / "revision_analysis" / "llm_statement_page_verifier_compiled.csv"

STOPWORDS = {
    "about",
    "after",
    "also",
    "among",
    "and",
    "are",
    "because",
    "been",
    "being",
    "can",
    "company",
    "dalam",
    "dan",
    "dengan",
    "for",
    "from",
    "has",
    "have",
    "into",
    "its",
    "kami",
    "kepada",
    "our",
    "that",
    "the",
    "their",
    "this",
    "through",
    "untuk",
    "was",
    "were",
    "will",
    "with",
    "yang",
}


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def normalize_text(value: str) -> str:
    value = re.sub(r"[^0-9a-zA-ZÀ-ÿ]+", " ", clean(value).lower())
    return re.sub(r"\s+", " ", value).strip()


def tokens(value: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[0-9a-zA-ZÀ-ÿ]+", normalize_text(value))
        if len(token) >= 4 and token not in STOPWORDS
    ]


@st.cache_data(show_spinner=False)
def load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []
    if isinstance(obj, list):
        return [row for row in obj if isinstance(row, dict)]
    if isinstance(obj, dict):
        return [obj]
    return []


@st.cache_data(show_spinner=False)
def flatten_t3(path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run_idx, run in enumerate(load_json(path)):
        records = run.get("records") if isinstance(run.get("records"), list) else []
        target = clean(run.get("target"))
        document = target.split("/")[0] if "/" in target else target
        for record_idx, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            labels = record.get("labels", [])
            labels_text = " | ".join(clean(v) for v in labels) if isinstance(labels, list) else clean(labels)
            statement = clean(record.get("text"))
            rows.append(
                {
                    "record_key": f"{run_idx}:{record_idx}",
                    "run_idx": run_idx,
                    "record_idx": record_idx,
                    "timestamp": clean(run.get("timestamp")),
                    "model": clean(run.get("model")),
                    "target": target,
                    "document": document,
                    "prompt": clean(run.get("prompt")),
                    "statement": statement,
                    "statement_len": len(statement),
                    "aspect": clean(record.get("aspect")),
                    "labels": labels_text,
                    "esg": clean(record.get("esg")).upper(),
                    "tone": clean(record.get("tone")).lower(),
                    "sentiment": clean(record.get("sentiment")).lower(),
                    "reasoning": clean(record.get("reasoning")),
                }
            )
    if rows:
        return pd.DataFrame(rows)
    if TONE_FLAT_PATH.exists():
        try:
            flat = pd.read_csv(TONE_FLAT_PATH).fillna("")
        except Exception:
            return pd.DataFrame(rows)
        for idx, record in flat.iterrows():
            target = clean(record.get("target"))
            document = target.split("/")[0] if "/" in target else clean(record.get("target_doc")) or target
            statement = clean(record.get("text"))
            rows.append(
                {
                    "record_key": f"flat:{idx}",
                    "run_idx": record.get("run_idx", ""),
                    "record_idx": record.get("record_idx", idx),
                    "timestamp": clean(record.get("timestamp")),
                    "model": clean(record.get("model")),
                    "target": target,
                    "document": document,
                    "prompt": clean(record.get("prompt")),
                    "statement": statement,
                    "statement_len": len(statement),
                    "aspect": clean(record.get("aspect")),
                    "labels": clean(record.get("labels")),
                    "esg": clean(record.get("esg")).upper(),
                    "tone": clean(record.get("tone")).lower(),
                    "sentiment": clean(record.get("sentiment")).lower(),
                    "reasoning": clean(record.get("reasoning")),
                }
            )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def list_documents(dataset_dir: Path) -> list[str]:
    if not dataset_dir.exists():
        return []
    return sorted(path.name for path in dataset_dir.iterdir() if (path / "pages").exists())


@st.cache_data(show_spinner=False)
def load_document_pages(dataset_dir: Path, document: str) -> pd.DataFrame:
    pages_dir = dataset_dir / document / "pages"
    if not pages_dir.exists():
        return pd.DataFrame(columns=["document", "page", "page_number", "path", "text", "norm_text"])
    rows: list[dict[str, Any]] = []
    for page_path in sorted(pages_dir.glob("*.md")):
        text = page_path.read_text(encoding="utf-8", errors="ignore")
        number_match = re.search(r"(\d+)", page_path.stem)
        rows.append(
            {
                "document": document,
                "page": page_path.name,
                "page_number": int(number_match.group(1)) if number_match else None,
                "path": str(page_path),
                "text": text,
                "norm_text": normalize_text(text),
            }
        )
    return pd.DataFrame(rows)


def values(df: pd.DataFrame, col: str) -> list[str]:
    if df.empty or col not in df.columns:
        return []
    return sorted(v for v in df[col].map(clean).unique() if v)


def apply_multiselect(df: pd.DataFrame, col: str, label: str, key: str) -> pd.DataFrame:
    options = values(df, col)
    selected = st.sidebar.multiselect(label, options, key=key)
    if not selected:
        return df
    return df[df[col].map(clean).isin(selected)]


def best_snippet(page_text: str, statement: str, radius: int = 420) -> str:
    page_norm = normalize_text(page_text)
    statement_norm = normalize_text(statement)
    if statement_norm and statement_norm in page_norm:
        idx = page_norm.find(statement_norm)
        return page_norm[max(0, idx - radius) : idx + len(statement_norm) + radius]

    statement_terms = set(tokens(statement))
    paragraphs = [p.strip() for p in re.split(r"\n{2,}|(?<=[.!?])\s+", page_text) if p.strip()]
    if not paragraphs:
        return clean(page_text)[: radius * 2]

    best_para = ""
    best_score = -1
    for paragraph in paragraphs:
        para_terms = set(tokens(paragraph))
        score = len(statement_terms & para_terms)
        if score > best_score:
            best_para = paragraph
            best_score = score
    return best_para[: radius * 2]


def page_match_score(statement: str, page_text: str) -> dict[str, Any]:
    statement_norm = normalize_text(statement)
    page_norm = normalize_text(page_text)
    if not statement_norm or not page_norm:
        return {
            "status": "not found",
            "exact": False,
            "token_coverage": 0.0,
            "sequence_ratio": 0.0,
            "score": 0.0,
            "matched_terms": "",
            "snippet": "",
        }

    exact = statement_norm in page_norm
    statement_terms = set(tokens(statement))
    page_terms = set(tokens(page_text))
    matched_terms = sorted(statement_terms & page_terms)
    token_coverage = len(matched_terms) / len(statement_terms) if statement_terms else 0.0

    snippet = best_snippet(page_text, statement)
    sequence_ratio = SequenceMatcher(None, statement_norm[:800], normalize_text(snippet)[:1200]).ratio()
    score = 1.0 if exact else round((token_coverage * 0.8) + (sequence_ratio * 0.2), 4)

    if exact:
        status = "exact"
    elif score >= 0.78:
        status = "likely"
    elif score >= 0.48:
        status = "possible"
    else:
        status = "not found"

    return {
        "status": status,
        "exact": exact,
        "token_coverage": round(token_coverage, 4),
        "sequence_ratio": round(sequence_ratio, 4),
        "score": score,
        "matched_terms": ", ".join(matched_terms[:40]),
        "snippet": snippet,
    }


def verify_statement(statement: str, pages_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, page in pages_df.iterrows():
        match = page_match_score(statement, clean(page.get("text")))
        rows.append(
            {
                "document": clean(page.get("document")),
                "page": clean(page.get("page")),
                "page_number": page.get("page_number"),
                "path": clean(page.get("path")),
                **match,
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    status_rank = {"exact": 0, "likely": 1, "possible": 2, "not found": 3}
    out["status_rank"] = out["status"].map(status_rank).fillna(9)
    return out.sort_values(["status_rank", "score", "token_coverage"], ascending=[True, False, False])


def compile_best_statement_matches(records: pd.DataFrame, dataset_dir: Path, all_documents: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    pages_cache: dict[str, pd.DataFrame] = {}
    for _, record in records.iterrows():
        document = clean(record.get("document"))
        if document not in all_documents:
            rows.append(
                {
                    **record.to_dict(),
                    "best_status": "missing_document",
                    "best_page": "",
                    "best_page_number": None,
                    "best_score": 0.0,
                    "best_token_coverage": 0.0,
                    "best_sequence_ratio": 0.0,
                    "best_matched_terms": "",
                    "best_page_path": "",
                    "best_snippet": "",
                }
            )
            continue
        if document not in pages_cache:
            pages_cache[document] = load_document_pages(dataset_dir, document)
        matches = verify_statement(clean(record.get("statement")), pages_cache[document])
        if matches.empty:
            best = {}
        else:
            best = matches.iloc[0].to_dict()
        rows.append(
            {
                **record.to_dict(),
                "best_status": clean(best.get("status")) or "not found",
                "best_page": clean(best.get("page")),
                "best_page_number": best.get("page_number"),
                "best_score": best.get("score", 0.0),
                "best_token_coverage": best.get("token_coverage", 0.0),
                "best_sequence_ratio": best.get("sequence_ratio", 0.0),
                "best_matched_terms": clean(best.get("matched_terms")),
                "best_page_path": clean(best.get("path")),
                "best_snippet": clean(best.get("snippet")),
            }
        )
    return pd.DataFrame(rows)


def highlight_terms(text: str, terms_text: str) -> str:
    output = escape(clean(text))
    terms = [term for term in terms_text.split(", ") if len(term) >= 4][:20]
    for term in sorted(set(terms), key=len, reverse=True):
        output = re.sub(
            rf"(?i)\b({re.escape(term)})\b",
            r"<mark>\1</mark>",
            output,
        )
    return output.replace("\n", "<br>")


st.title("LLM Statement Page Verifier")
st.caption(
    "Map parsed LLM ESG statements back to OCR markdown pages and check whether each extracted statement is actually present in the source pages."
)

records_df = flatten_t3(T3_PATH)
documents = list_documents(DATASET_DIR)

with st.sidebar:
    st.header("Source files")
    st.caption(f"LLM records: `{T3_PATH}`")
    if not T3_PATH.exists() and TONE_FLAT_PATH.exists():
        st.caption(f"Fallback flat records: `{TONE_FLAT_PATH}`")
    st.caption(f"OCR pages: `{DATASET_DIR}`")
    if st.button("Refresh files", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.header("Record filters")
    filtered = records_df.copy()
    for col, label in [
        ("document", "Document"),
        ("target", "Target batch"),
        ("model", "Model"),
        ("prompt", "Prompt"),
        ("esg", "ESG"),
        ("tone", "Tone"),
        ("sentiment", "Sentiment"),
        ("aspect", "Aspect"),
    ]:
        filtered = apply_multiselect(filtered, col, label, f"verify_{col}")

    search = st.text_input("Search extracted statement", "")
    if search.strip() and not filtered.empty:
        needle = normalize_text(search)
        filtered = filtered[
            filtered["statement"].map(lambda value: needle in normalize_text(value))
            | filtered["reasoning"].map(lambda value: needle in normalize_text(value))
        ]

    st.header("Verification")
    search_scope = st.radio(
        "Search OCR pages",
        ["Target document", "All documents"],
        help="Target document is faster and usually correct because the LLM target stores the OCR folder name.",
    )
    top_n = st.slider("Show top page matches", min_value=3, max_value=25, value=10, step=1)

metric_cols = st.columns(4)
metric_cols[0].metric("Extracted records", f"{len(records_df):,}")
metric_cols[1].metric("Filtered records", f"{len(filtered):,}")
metric_cols[2].metric("OCR documents", f"{len(documents):,}")
metric_cols[3].metric("Records with target doc", f"{records_df['document'].isin(documents).sum():,}" if not records_df.empty else "0")

with st.expander("Compiled statement-page verification dataset", expanded=COMPILED_VERIFICATION_PATH.exists()):
    st.caption(f"Compiled CSV: `{COMPILED_VERIFICATION_PATH}`")
    compile_limit = st.number_input(
        "Compile row limit",
        min_value=50,
        max_value=max(int(len(filtered)), 50),
        value=min(int(len(filtered)), 500) if len(filtered) else 50,
        step=50,
        help="Use a limit while testing. Set to the filtered row count to compile all visible records.",
    )
    compile_scope = st.radio("Compile scope", ["Filtered records", "All records"], horizontal=True)
    compile_source = filtered if compile_scope == "Filtered records" else records_df
    if st.button("Compile best page matches CSV", type="primary", use_container_width=True):
        to_compile = compile_source.head(int(compile_limit)).copy()
        with st.spinner(f"Compiling best page matches for {len(to_compile):,} statements..."):
            compiled = compile_best_statement_matches(to_compile, DATASET_DIR, documents)
            COMPILED_VERIFICATION_PATH.parent.mkdir(parents=True, exist_ok=True)
            compiled.to_csv(COMPILED_VERIFICATION_PATH, index=False)
        st.success(f"Saved {len(compiled):,} compiled verification rows.")
        st.rerun()
    if COMPILED_VERIFICATION_PATH.exists():
        compiled_existing = pd.read_csv(COMPILED_VERIFICATION_PATH).fillna("")
        c1, c2, c3 = st.columns(3)
        c1.metric("Compiled rows", f"{len(compiled_existing):,}")
        c2.metric("Exact / likely", f"{int(compiled_existing.get('best_status', pd.Series(dtype=str)).astype(str).isin(['exact', 'likely']).sum()):,}")
        c3.metric("Not found", f"{int(compiled_existing.get('best_status', pd.Series(dtype=str)).astype(str).eq('not found').sum()):,}")
        st.dataframe(compiled_existing.head(200), use_container_width=True, hide_index=True, height=300)
        st.download_button(
            "Download compiled verifier CSV",
            compiled_existing.to_csv(index=False).encode("utf-8"),
            "llm_statement_page_verifier_compiled.csv",
            "text/csv",
            use_container_width=True,
        )

if records_df.empty:
    st.warning("No parsed LLM ESG records were found.")
    st.stop()

if filtered.empty:
    st.info("No records match the current filters.")
    st.stop()

record_options = {
    f"{row.record_key} | {row.document} | {row.esg or '-'} | {row.tone or '-'} | {row.statement[:120]}": row.record_key
    for row in filtered.itertuples()
}
selected_label = st.selectbox("Choose an extracted statement", list(record_options.keys()))
selected_key = record_options[selected_label]
selected = filtered[filtered["record_key"].eq(selected_key)].iloc[0]

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Extracted LLM statement")
    st.write(selected["statement"])
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "document": selected["document"],
                    "target": selected["target"],
                    "model": selected["model"],
                    "prompt": selected["prompt"],
                    "ESG": selected["esg"],
                    "tone": selected["tone"],
                    "sentiment": selected["sentiment"],
                    "aspect": selected["aspect"],
                }
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
with right:
    st.subheader("LLM reasoning")
    st.write(selected["reasoning"] or "No reasoning saved for this record.")

if search_scope == "Target document":
    docs_to_search = [selected["document"]] if selected["document"] in documents else []
else:
    docs_to_search = documents

if not docs_to_search:
    st.error(f"No OCR markdown pages found for `{selected['document']}`.")
    st.stop()

with st.spinner("Searching OCR page text for this statement..."):
    pages_df = pd.concat(
        [load_document_pages(DATASET_DIR, doc) for doc in docs_to_search],
        ignore_index=True,
    )
    matches_df = verify_statement(selected["statement"], pages_df)

if matches_df.empty:
    st.warning("No OCR pages were available to scan.")
    st.stop()

best = matches_df.iloc[0]
status_color = {
    "exact": "green",
    "likely": "blue",
    "possible": "orange",
    "not found": "red",
}.get(best["status"], "gray")

result_cols = st.columns(4)
result_cols[0].metric("Best status", str(best["status"]).upper())
result_cols[1].metric("Best page", clean(best["page"]))
result_cols[2].metric("Match score", f"{float(best['score']):.2f}")
result_cols[3].metric("Token coverage", f"{float(best['token_coverage']) * 100:.1f}%")

if best["status"] == "not found":
    st.error("The selected statement was not found with enough textual overlap in the scanned OCR pages.")
else:
    st.success(f"Best source evidence is a {best['status']} match in `{best['document']}/{best['page']}`.")

st.subheader("Top matching pages")
visible_matches = matches_df.drop(columns=["status_rank"]).head(int(top_n))
st.dataframe(
    visible_matches[
        [
            "status",
            "document",
            "page",
            "score",
            "token_coverage",
            "sequence_ratio",
            "matched_terms",
            "path",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Best page evidence snippet")
st.caption("Highlighted words are overlapping terms between the extracted statement and OCR page text.")
st.markdown(
    f"""
    <div style="border-left: 5px solid {status_color}; padding: 1rem; background: #f8fafc; line-height: 1.65;">
      {highlight_terms(clean(best["snippet"]), clean(best["matched_terms"]))}
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Open full OCR page text"):
    page_text = pages_df[pages_df["path"].eq(best["path"])]["text"]
    st.text_area("OCR markdown page", value=page_text.iloc[0] if not page_text.empty else "", height=420)

with st.expander("Export verification results"):
    st.download_button(
        "Download page match CSV",
        visible_matches.to_csv(index=False).encode("utf-8"),
        file_name=f"llm_statement_page_verification_{selected_key.replace(':', '_')}.csv",
        mime="text/csv",
    )
