import json
import math
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
NOTES_PATH = APP_DIR / "notes.md"
SOURCES_PATH = DATA_DIR / "data_sources.json"


st.set_page_config(
    page_title="ESG ABSA Research Dashboard",
    page_icon="📘",
    layout="wide",
)


def _read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _load_sources_config() -> dict:
    if not SOURCES_PATH.exists():
        return {}
    try:
        return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


@st.cache_data(show_spinner=False)
def load_datasets() -> tuple[dict, list[str]]:
    config = _load_sources_config()
    datasets = {}
    logs = []

    real_keys = [
        "tone_records_flat",
        "t2_flat_outputs",
        "climatebert_proxy_agreement_summary",
        "model_stability_summary",
        "prompt_stability_summary",
        "ontology_coverage",
    ]

    for key in real_keys:
        rel = config.get(key)
        df = pd.DataFrame()
        if rel:
            p = ROOT_DIR / rel
            if p.exists():
                df = _read_csv(p)
                logs.append(f"Loaded real dataset for `{key}` from `{p}`")
            else:
                logs.append(f"Missing real dataset for `{key}` expected at `{p}`")
        else:
            logs.append(f"No configured path for `{key}` in data_sources.json")

        if df.empty:
            sample_name = f"sample_{key}.csv"
            sample_path = DATA_DIR / sample_name
            if sample_path.exists():
                df = _read_csv(sample_path)
                logs.append(f"Loaded fallback sample for `{key}` from `{sample_path}`")
            else:
                logs.append(f"No fallback sample found for `{key}`")

        datasets[key] = df

    return datasets, logs


def metric_int(value) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return "N/A"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def split_sentences(text: str) -> list[str]:
    if not text or not isinstance(text, str):
        return []
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [p.strip() for p in parts if p.strip()]


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r"[a-zA-Z0-9']+", text.lower())


def summarize_lead(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    return " ".join(sentences[:max_sentences])


def summarize_frequency(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ""
    tokens = tokenize(text)
    if not tokens:
        return summarize_lead(text, max_sentences=max_sentences)
    freqs = Counter(tokens)
    scores = []
    for idx, sent in enumerate(sentences):
        sent_tokens = tokenize(sent)
        if not sent_tokens:
            continue
        score = sum(freqs[t] for t in sent_tokens) / (len(sent_tokens) + 1e-9)
        scores.append((idx, score))
    if not scores:
        return summarize_lead(text, max_sentences=max_sentences)
    top_idx = [i for i, _ in sorted(scores, key=lambda x: x[1], reverse=True)[:max_sentences]]
    top_idx.sort()
    return " ".join(sentences[i] for i in top_idx)


def _sentence_similarity(a: str, b: str) -> float:
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta or not tb:
        return 0.0
    inter = len(ta.intersection(tb))
    denom = math.sqrt(len(ta) * len(tb))
    if denom == 0:
        return 0.0
    return inter / denom


def summarize_textrank_like(text: str, max_sentences: int = 3, iters: int = 20, d: float = 0.85) -> str:
    sentences = split_sentences(text)
    n = len(sentences)
    if n == 0:
        return ""
    if n <= max_sentences:
        return " ".join(sentences)

    sim = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                sim[i][j] = _sentence_similarity(sentences[i], sentences[j])

    scores = [1.0] * n
    for _ in range(iters):
        new_scores = [1 - d] * n
        for i in range(n):
            s = 0.0
            for j in range(n):
                if i == j:
                    continue
                row_sum = sum(sim[j])
                if row_sum > 0:
                    s += (sim[j][i] / row_sum) * scores[j]
            new_scores[i] += d * s
        scores = new_scores

    top_idx = sorted(range(n), key=lambda i: scores[i], reverse=True)[:max_sentences]
    top_idx.sort()
    return " ".join(sentences[i] for i in top_idx)


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def rouge_n(pred: str, ref: str, n: int) -> dict:
    pt = tokenize(pred)
    rt = tokenize(ref)
    p_ngrams = _ngrams(pt, n)
    r_ngrams = _ngrams(rt, n)
    if not p_ngrams or not r_ngrams:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    pc = Counter(p_ngrams)
    rc = Counter(r_ngrams)
    overlap = sum(min(pc[g], rc[g]) for g in rc)
    precision = overlap / len(p_ngrams)
    recall = overlap / len(r_ngrams)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def _lcs_length(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    dp = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        prev = 0
        for j in range(1, len(b) + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = tmp
    return dp[-1]


def rouge_l(pred: str, ref: str) -> dict:
    pt = tokenize(pred)
    rt = tokenize(ref)
    if not pt or not rt:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    lcs = _lcs_length(pt, rt)
    precision = lcs / len(pt)
    recall = lcs / len(rt)
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def render_automatic_summarization_analysis(datasets: dict) -> None:
    st.subheader("Automatic Summarization Analysis")
    st.caption("Compare built-in extractive summarizers and optionally evaluate with ROUGE metrics.")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    source_options = ["Manual input", "From tone_records_flat grouped text"]
    source_choice = st.radio("Input Source", source_options, horizontal=True)

    text_input = ""
    if source_choice == "Manual input":
        text_input = st.text_area(
            "Input Document Text",
            height=220,
            placeholder="Paste a report section, page text, or paragraph to summarize.",
        )
    else:
        if tone_df.empty:
            st.warning("tone_records_flat is empty. Use Manual input.")
            return
        group_col = find_column(tone_df, ["source_doc", "source", "company", "target_doc"])
        text_col = find_column(tone_df, ["text", "statement", "reasoning"])
        if not group_col or not text_col:
            st.warning("Required columns not found for grouped summarization (`source_doc/company` and `text/statement/reasoning`).")
            return
        options = sorted(tone_df[group_col].dropna().astype(str).unique().tolist())
        if not options:
            st.warning("No valid grouping values in dataset.")
            return
        selected = st.selectbox("Select Group", options)
        subset = tone_df[tone_df[group_col].astype(str) == selected]
        text_input = " ".join(subset[text_col].dropna().astype(str).tolist())
        st.caption(f"Built input from {len(subset):,} rows in `{selected}`")

    max_sentences = st.slider("Summary Length (sentences)", min_value=1, max_value=10, value=3, step=1)
    if not text_input.strip():
        st.info("Provide input text to generate summaries.")
        return

    lead_summary = summarize_lead(text_input, max_sentences=max_sentences)
    freq_summary = summarize_frequency(text_input, max_sentences=max_sentences)
    rank_summary = summarize_textrank_like(text_input, max_sentences=max_sentences)

    c1, c2, c3 = st.columns(3)
    c1.markdown("#### Lead Baseline")
    c1.write(lead_summary if lead_summary else "No summary generated.")
    c2.markdown("#### Frequency")
    c2.write(freq_summary if freq_summary else "No summary generated.")
    c3.markdown("#### TextRank-like")
    c3.write(rank_summary if rank_summary else "No summary generated.")

    st.markdown("### ROUGE Evaluation (Optional)")
    ref = st.text_area("Reference (Gold) Summary", height=140, placeholder="Paste a reference summary to compute ROUGE-1/2/L.")
    if ref.strip():
        rows = []
        systems = {
            "Lead": lead_summary,
            "Frequency": freq_summary,
            "TextRank-like": rank_summary,
        }
        for name, pred in systems.items():
            r1 = rouge_n(pred, ref, 1)
            r2 = rouge_n(pred, ref, 2)
            rl = rouge_l(pred, ref)
            rows.append(
                {
                    "system": name,
                    "rouge1_f1": round(r1["f1"], 4),
                    "rouge2_f1": round(r2["f1"], 4),
                    "rougel_f1": round(rl["f1"], 4),
                    "rouge1_recall": round(r1["recall"], 4),
                    "rouge2_recall": round(r2["recall"], 4),
                    "rougel_recall": round(rl["recall"], 4),
                }
            )
        scores_df = pd.DataFrame(rows).sort_values(by=["rouge2_f1", "rougel_f1"], ascending=False)
        st.dataframe(scores_df, use_container_width=True)


def render_overview(datasets: dict) -> None:
    st.subheader("Overview")

    tone_df = datasets.get("tone_records_flat", pd.DataFrame())
    t2_df = datasets.get("t2_flat_outputs", pd.DataFrame())
    climate_df = datasets.get("climatebert_proxy_agreement_summary", pd.DataFrame())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Structured ESG Records", metric_int(len(tone_df)))
    col2.metric("T2 Rows", metric_int(len(t2_df)))

    agreement_val = "N/A"
    kappa_val = "N/A"
    if not climate_df.empty:
        agreement_col = find_column(climate_df, ["agreement", "proxy_agreement", "agreement_rate", "value"])
        kappa_col = find_column(climate_df, ["kappa", "cohen_kappa", "cohens_kappa"])
        if agreement_col:
            try:
                agreement_val = f"{float(climate_df[agreement_col].dropna().iloc[0]):.3f}"
            except Exception:
                pass
        if kappa_col:
            try:
                kappa_val = f"{float(climate_df[kappa_col].dropna().iloc[0]):.3f}"
            except Exception:
                pass

    col3.metric("ClimateBERT Agreement", agreement_val)
    col4.metric("Cohen's Kappa", kappa_val)

    st.markdown("### Tone Distribution")
    if not tone_df.empty:
        tone_col = find_column(tone_df, ["tone", "label_tone"])
        if tone_col:
            dist = tone_df[tone_col].fillna("Unknown").value_counts().rename_axis("tone").reset_index(name="count")
            st.bar_chart(dist.set_index("tone"))
        else:
            st.info("No `tone` column found in tone records.")
    else:
        st.info("No tone records available.")


def render_record_explorer(datasets: dict) -> None:
    st.subheader("Record Explorer")
    tone_df = datasets.get("tone_records_flat", pd.DataFrame())

    if tone_df.empty:
        st.warning("No tone record data available.")
        return

    aspect_col = find_column(tone_df, ["aspect"])
    esg_col = find_column(tone_df, ["esg", "esg_pillar"])
    tone_col = find_column(tone_df, ["tone"])

    f1, f2, f3 = st.columns(3)

    filtered = tone_df.copy()

    if aspect_col:
        aspects = ["All"] + sorted(filtered[aspect_col].dropna().astype(str).unique().tolist())
        aspect_choice = f1.selectbox("Aspect", aspects)
        if aspect_choice != "All":
            filtered = filtered[filtered[aspect_col].astype(str) == aspect_choice]

    if esg_col:
        esgs = ["All"] + sorted(filtered[esg_col].dropna().astype(str).unique().tolist())
        esg_choice = f2.selectbox("ESG Pillar", esgs)
        if esg_choice != "All":
            filtered = filtered[filtered[esg_col].astype(str) == esg_choice]

    if tone_col:
        tones = ["All"] + sorted(filtered[tone_col].dropna().astype(str).unique().tolist())
        tone_choice = f3.selectbox("Tone", tones)
        if tone_choice != "All":
            filtered = filtered[filtered[tone_col].astype(str) == tone_choice]

    st.caption(f"Showing {len(filtered):,} rows")
    st.dataframe(filtered, use_container_width=True, height=420)


def render_stability(datasets: dict) -> None:
    st.subheader("Stability Analysis")

    model_df = datasets.get("model_stability_summary", pd.DataFrame())
    prompt_df = datasets.get("prompt_stability_summary", pd.DataFrame())

    left, right = st.columns(2)

    with left:
        st.markdown("#### Model Stability")
        if model_df.empty:
            st.info("No model stability summary available.")
        else:
            st.dataframe(model_df, use_container_width=True)
            model_col = find_column(model_df, ["model", "model_name"])
            success_col = find_column(model_df, ["parse_success_rate", "success_rate"])
            if model_col and success_col:
                chart_df = model_df[[model_col, success_col]].dropna().set_index(model_col)
                st.bar_chart(chart_df)

    with right:
        st.markdown("#### Prompt Stability")
        if prompt_df.empty:
            st.info("No prompt stability summary available.")
        else:
            st.dataframe(prompt_df, use_container_width=True)
            prompt_col = find_column(prompt_df, ["prompt_name", "prompt"])
            success_col = find_column(prompt_df, ["parse_success_rate", "success_rate"])
            if prompt_col and success_col:
                chart_df = prompt_df[[prompt_col, success_col]].dropna().set_index(prompt_col)
                st.bar_chart(chart_df)


def render_ontology(datasets: dict) -> None:
    st.subheader("Ontology Coverage")

    ont_df = datasets.get("ontology_coverage", pd.DataFrame())
    if ont_df.empty:
        st.info("No ontology coverage data available.")
        return

    st.dataframe(ont_df, use_container_width=True)

    status_col = find_column(ont_df, ["status", "mapping_status", "label"])
    count_col = find_column(ont_df, ["count", "records", "value"])

    if status_col and count_col:
        chart_df = ont_df[[status_col, count_col]].dropna().set_index(status_col)
        st.bar_chart(chart_df)


def render_research_notes() -> None:
    st.subheader("Research Framing")
    if NOTES_PATH.exists():
        st.markdown(NOTES_PATH.read_text(encoding="utf-8"))
    else:
        st.warning("`summarization/notes.md` not found.")


def main() -> None:
    st.title("ESG ABSA Summarization Workspace")
    st.caption("Streamlit dashboard for ESG evidence summarization, stability checks, and research framing.")

    datasets, logs = load_datasets()

    with st.expander("Data Loading Log", expanded=False):
        for line in logs:
            st.write(f"- {line}")

    tabs = st.tabs([
        "Overview",
        "Auto Summarization",
        "Record Explorer",
        "Stability",
        "Ontology",
        "Research Notes",
    ])

    with tabs[0]:
        render_overview(datasets)
    with tabs[1]:
        render_automatic_summarization_analysis(datasets)
    with tabs[2]:
        render_record_explorer(datasets)
    with tabs[3]:
        render_stability(datasets)
    with tabs[4]:
        render_ontology(datasets)
    with tabs[5]:
        render_research_notes()


if __name__ == "__main__":
    main()
