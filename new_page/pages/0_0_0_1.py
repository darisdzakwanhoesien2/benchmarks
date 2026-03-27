import json
import pathlib
from typing import List, Dict, Any

import pandas as pd
import streamlit as st

ESG_FILE = (
    "/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/"
    "esg_project/benchmarks/new_page/results/esg_records.json"
)


def safe_load_json(path: str) -> List[Dict[str, Any]]:
    text = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return [data]
    except Exception:
        # fallback: extract first [...] block
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
    return []


def extract_records(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for item in data:
        # prefer explicit "records" lists
        if isinstance(item.get("records"), list) and item["records"]:
            records.extend(item["records"])
            continue
        # try parsing raw_output if present and looks like JSON
        raw = item.get("raw_output") or item.get("raw")
        if raw and isinstance(raw, str) and raw.strip():
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    for r in parsed:
                        if isinstance(r, dict):
                            records.append(r)
            except Exception:
                # ignore non-json raw_output
                pass
        # if item itself looks like a record
        if all(k in item for k in ("text", "aspect")):
            records.append(item)
    return records


def normalize(rec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "text": rec.get("text", "")[:1000],
        "aspect": rec.get("aspect", "") or rec.get("aspect"),
        "labels": ", ".join(rec.get("labels", [])) if isinstance(rec.get("labels"), list) else rec.get("labels", ""),
        "esg": rec.get("esg", "") or rec.get("ESG", ""),
        "sentiment": rec.get("sentiment", ""),
        "sentiment_score": rec.get("sentiment_score", 0),
        "reasoning": rec.get("reasoning", ""),
        "_raw": rec,
    }


def main():
    st.set_page_config(page_title="ESG Records viewer", layout="wide")
    st.title("ESG Records — viewer")

    data = safe_load_json(ESG_FILE)
    records = extract_records(data)
    if not records:
        st.warning(f"No records found in {ESG_FILE}")
        st.stop()

    df = pd.DataFrame([normalize(r) for r in records])

    # Sidebar filters
    st.sidebar.header("Filters")
    esg_options = [""] + sorted(df["esg"].dropna().unique().tolist())
    esg = st.sidebar.selectbox("ESG", esg_options, index=0)
    sentiment_options = [""] + sorted(df["sentiment"].dropna().unique().tolist())
    sentiment = st.sidebar.selectbox("Sentiment", sentiment_options, index=0)
    label_search = st.sidebar.text_input("Label contains (comma separated)")
    aspect_search = st.sidebar.text_input("Aspect contains")
    text_search = st.sidebar.text_input("Full-text search")

    filtered = df.copy()
    if esg:
        filtered = filtered[filtered["esg"].astype(str).str.lower() == esg.lower()]
    if sentiment:
        filtered = filtered[filtered["sentiment"].astype(str).str.lower() == sentiment.lower()]
    if label_search:
        for token in [t.strip().lower() for t in label_search.split(",") if t.strip()]:
            filtered = filtered[filtered["labels"].str.lower().str.contains(token, na=False)]
    if aspect_search:
        filtered = filtered[filtered["aspect"].astype(str).str.lower().str.contains(aspect_search.lower(), na=False)]
    if text_search:
        filtered = filtered[filtered["text"].astype(str).str.lower().str.contains(text_search.lower(), na=False)]

    st.sidebar.markdown(f"Results: **{len(filtered)}**")

    # Table and selection
    st.subheader("Records")

    # avoid errors when filters return no rows
    if filtered.empty:
        st.warning("No records match the current filters.")
        st.stop()

    index_options = list(filtered.index)
    selected_idx = st.selectbox(
        "Select record index",
        options=index_options,
        format_func=lambda i: f"{i} — {str(filtered.at[i, 'aspect'] or '')[:40]}",
    )

    st.dataframe(
        filtered[["aspect", "esg", "sentiment", "sentiment_score", "labels", "text"]].rename(
            columns={"text": "text_preview"}
        ),
        use_container_width=True,
    )

    # Detail view
    st.subheader("Detail")
    rec = filtered.at[selected_idx, "_raw"]
    st.markdown("**Text**")
    st.write(rec.get("text", ""))
    st.markdown("**Aspect**")
    st.write(rec.get("aspect", ""))
    st.markdown("**Labels**")
    st.write(rec.get("labels", []))
    st.markdown("**ESG**")
    st.write(rec.get("esg", ""))
    st.markdown("**Sentiment / score**")
    st.write(f"{rec.get('sentiment', '')} — {rec.get('sentiment_score', '')}")
    st.markdown("**Reasoning**")
    st.write(rec.get("reasoning", ""))

    # Quick action: show JSON for copy
    st.subheader("Raw JSON")
    st.json(rec)


if __name__ == "__main__":
    main()