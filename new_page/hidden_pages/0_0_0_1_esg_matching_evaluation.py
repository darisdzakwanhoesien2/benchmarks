import os
import re
import json
import pathlib
import difflib
from typing import List, Dict, Any, Tuple

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# 📁 CONFIG
# ============================================================

ESG_FILE = (
    "/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/"
    "esg_project/benchmarks/new_page/results/esg_records.json"
)

RESULTS_FILE = (
    "/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/"
    "esg_project/benchmarks/new_page/results/t1_results.jsonl"
)

MAPPING_PATH = pathlib.Path(ESG_FILE).parent / "data" / "mapping.json"

# ============================================================
# 🔧 LOADERS
# ============================================================

def safe_load_json(path: str) -> List[Dict[str, Any]]:
    if not pathlib.Path(path).exists():
        return []

    text = pathlib.Path(path).read_text(encoding="utf-8")

    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except Exception:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
    return []


def load_jsonl_results(path: str) -> List[Dict[str, Any]]:
    if not pathlib.Path(path).exists():
        return []

    entries = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return entries


def load_mapping(path: pathlib.Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        # normalize keys to lowercase for tolerant lookup
        return {k.strip().lower(): v for k, v in data.items()}
    except Exception:
        return {}


# ============================================================
# 🧠 NORMALIZATION
# ============================================================

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"\.\.\.+", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = " ".join(s.split())
    return s.strip()


# ============================================================
# 🔍 MATCHING ENGINE
# ============================================================

def similarity_score(a: str, b: str) -> float:
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def find_match_with_score(norm: str, results_map: Dict[str, Any]) -> Tuple[Any, float]:
    if not norm:
        return None, 0.0

    if norm in results_map:
        return results_map[norm], 1.0

    best_match = None
    best_score = 0.0

    for k, v in results_map.items():

        if norm in k or k in norm:
            return v, 0.95

        score = similarity_score(norm, k)
        if score > best_score:
            best_score = score
            best_match = v

    if best_score > 0.6:
        return best_match, best_score

    keys = list(results_map.keys())
    m = difflib.get_close_matches(norm, keys, n=1, cutoff=0.75)
    if m:
        return results_map[m[0]], 0.7

    return None, best_score


# ============================================================
# 📊 RECORD PROCESSING
# ============================================================

def extract_records(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    records = []

    for item in data:
        if isinstance(item.get("records"), list):
            records.extend(item["records"])
            continue

        if all(k in item for k in ("text", "aspect")):
            records.append(item)

    return records


def normalize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "text": rec.get("text", ""),
        "aspect": rec.get("aspect", ""),
        "labels": ", ".join(rec.get("labels", [])),
        "esg": rec.get("esg", ""),
        "sentiment": rec.get("sentiment", ""),
        "sentiment_score": rec.get("sentiment_score", 0),
        "reasoning": rec.get("reasoning", ""),
        "_raw": rec,
    }


# ============================================================
# 🧪 PREDICTION PARSER
# ============================================================

def parse_prediction(pred_str: str):
    if not pred_str:
        return None, None

    match = re.search(r"(LABEL_\d+):\s*([0-9.]+)", pred_str)
    if match:
        return match.group(1), float(match.group(2))

    return None, None


# ============================================================
# 🚀 MAIN APP
# ============================================================

def main():
    st.set_page_config(layout="wide")
    st.title("🌍 ESG Matching & Evaluation Dashboard")

    # Load data
    data = safe_load_json(ESG_FILE)
    records = extract_records(data)

    if not records:
        st.warning("No ESG records found")
        return

    df = pd.DataFrame([normalize_record(r) for r in records])

    # Load results
    results_entries = load_jsonl_results(RESULTS_FILE)

    results_map = {}
    for e in results_entries:
        txt = e.get("text") or e.get("result", {}).get("text", "")
        if txt:
            results_map[normalize_text(txt)] = e

    # Matching
    df["normalized_text"] = df["text"].apply(normalize_text)

    matches = df["normalized_text"].apply(
        lambda x: find_match_with_score(x, results_map)
    )

    df["matched_result"] = matches.apply(lambda x: x[0])
    df["match_score"] = matches.apply(lambda x: x[1])

    # Extract predictions
    def extract_pred(r):
        if not isinstance(r, dict):
            return "", ""
        res = r.get("result", {})
        return res.get("model", ""), res.get("prediction", "")

    df[["matched_model", "matched_prediction"]] = df["matched_result"].apply(
        lambda x: pd.Series(extract_pred(x))
    )

    df[["pred_label", "pred_score"]] = df["matched_prediction"].apply(
        lambda x: pd.Series(parse_prediction(x))
    )

    label_mapping = load_mapping(MAPPING_PATH)

    # ========================================================
    # 📊 SIDEBAR FILTERS
    # ========================================================

    st.sidebar.header("Filters")

    esg = st.sidebar.selectbox("ESG", ["", "E", "S", "G", "N"])
    sentiment = st.sidebar.selectbox("Sentiment", ["", "positive", "neutral", "negative", "commitment"])
    search = st.sidebar.text_input("Search text")
    match_filter = st.sidebar.selectbox("Match", ["", "matched", "unmatched"])

    filtered = df.copy()

    if esg:
        filtered = filtered[filtered["esg"] == esg]

    if sentiment:
        filtered = filtered[filtered["sentiment"] == sentiment]

    if search:
        filtered = filtered[filtered["text"].str.contains(search, case=False, na=False)]

    if match_filter == "matched":
        filtered = filtered[filtered["matched_result"].notnull()]
    elif match_filter == "unmatched":
        filtered = filtered[filtered["matched_result"].isnull()]

    st.sidebar.markdown(f"**Records:** {len(filtered)}")

    # ========================================================
    # 📈 ANALYTICS
    # ========================================================

    st.subheader("📈 Analytics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", len(df))
    col2.metric("Matched", df["matched_result"].notnull().sum())
    col3.metric("Avg Score", round(df["match_score"].mean(), 2))

    # ========================================================
    # 📊 MATCHED VISUALIZATION
    # ========================================================

    st.subheader("📊 Matched Data Insights")

    matched_df = df[df["matched_result"].notnull()].copy()

    if not matched_df.empty:

        st.markdown("### 📈 Match Score Distribution")
        fig1, ax1 = plt.subplots()
        sns.histplot(matched_df["match_score"], bins=20, kde=True, ax=ax1)
        st.pyplot(fig1)

        st.markdown("### 🏷️ Prediction Label Distribution")
        fig2, ax2 = plt.subplots()
        matched_df["pred_label"].value_counts().plot(kind="bar", ax=ax2)
        st.pyplot(fig2)

        st.markdown("### 🔥 ESG vs Prediction Heatmap")
        # map esg and pred_label into grouped categories using mapping.json
        def map_to_group(val):
            if val is None:
                return "other"
            key = str(val).strip().lower()
            return label_mapping.get(key, key)

        matched_df["esg_group"] = matched_df["esg"].apply(map_to_group)
        matched_df["pred_group"] = matched_df["pred_label"].apply(map_to_group)

        pivot = pd.crosstab(matched_df["esg_group"], matched_df["pred_group"])
        fig3, ax3 = plt.subplots(figsize=(6, max(2, len(pivot) * 0.5)))
        sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax3)
        ax3.set_xlabel("pred_group")
        ax3.set_ylabel("esg_group")
        st.pyplot(fig3)

        # ========================================================
        # 📋 Heatmap table + CSV download (added)
        # ========================================================
        st.markdown("### 📋 Heatmap — underlying counts")
        heatmap_table = pivot.reset_index().rename_axis(None, axis=1)
        st.dataframe(heatmap_table, use_container_width=True)

        csv_bytes = heatmap_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download heatmap table CSV",
            data=csv_bytes,
            file_name="esg_pred_heatmap.csv",
            mime="text/csv",
        )

        st.markdown("### 🎯 Confidence by Label")
        fig4, ax4 = plt.subplots()
        sns.boxplot(data=matched_df, x="pred_label", y="pred_score", ax=ax4)
        st.pyplot(fig4)

        st.markdown("### ⚠️ Low Confidence Matches")
        low_conf = matched_df.sort_values("pred_score").head(10)
        st.dataframe(low_conf[["text", "match_score", "pred_label", "pred_score"]])

        # ========================================================
        # 📋 MATCHED TABLE
        # ========================================================
        st.markdown("### 📋 Matched Records Table")
        matched_table = (
            matched_df[
                [
                    "aspect",
                    "esg",
                    "sentiment",
                    "match_score",
                    "matched_model",
                    "pred_label",
                    "pred_score",
                    "text",
                ]
            ]
            .reset_index()
            .rename(columns={"index": "orig_index"})
        )

        st.dataframe(matched_table, use_container_width=True)

        # CSV download
        csv = matched_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download matched CSV",
            data=csv,
            file_name="matched_records.csv",
            mime="text/csv",
        )

        # Inspect selected rows
        sel = st.multiselect(
            "Select rows (orig_index) to inspect", options=matched_table["orig_index"].tolist()
        )
        if sel:
            for i in sel:
                if i in matched_df.index:
                    rec = matched_df.loc[i]
                    st.markdown(f"#### Record {i}")
                    st.write("**Text**")
                    st.write(rec["text"])
                    st.write("**Match score**", rec["match_score"])
                    st.write("**Predicted label / score**", rec["pred_label"], rec["pred_score"])
                    st.write("**Matched JSON**")
                    st.json(rec["matched_result"])

    # ========================================================
    # 📋 TABLE
    # ========================================================

    st.subheader("📋 Records")

    if filtered.empty:
        st.warning("No data after filtering")
        return

    st.dataframe(
        filtered[[
            "aspect", "esg", "sentiment",
            "match_score", "pred_label",
            "pred_score", "text"
        ]],
        use_container_width=True
    )

    # ========================================================
    # 🔍 DETAIL VIEW
    # ========================================================

    idx = st.selectbox("Select record", filtered.index)
    rec = filtered.loc[idx]

    st.subheader("🔍 Detail")

    st.write("**Text**", rec["text"])
    st.write("**Aspect**", rec["aspect"])
    st.write("**ESG**", rec["esg"])
    st.write("**Sentiment**", rec["sentiment"], rec["sentiment_score"])
    st.write("**Reasoning**", rec["reasoning"])

    st.write("### 🤖 Model Output")
    if rec["matched_result"]:
        st.json(rec["matched_result"])
    else:
        st.warning("No match found")

    # ========================================================
    # 🧪 DEBUG TOOL
    # ========================================================

    st.subheader("🧪 Matching Debug Tool")

    user_input = st.text_area("Test matching manually")

    if user_input:
        norm = normalize_text(user_input)
        match, score = find_match_with_score(norm, results_map)

        st.write("Normalized:", norm)
        st.write("Score:", score)

        if match:
            st.json(match)
        else:
            st.warning("No match")


if __name__ == "__main__":
    main()

# import os
# import re
# import json
# import pathlib
# import difflib
# from typing import List, Dict, Any, Tuple

# import pandas as pd
# import streamlit as st

# # ============================================================
# # 📁 CONFIG
# # ============================================================

# ESG_FILE = (
#     "/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/"
#     "esg_project/benchmarks/new_page/results/esg_records.json"
# )

# # new: path to JSONL results (change if needed)
# RESULTS_FILE = (
#     "/Users/darisdzakwanhoesien/Documents/project_documentation/codebase/"
#     "esg_project/benchmarks/new_page/results/t1_results.jsonl"
# )

# # ============================================================
# # 🔧 LOADERS
# # ============================================================

# def safe_load_json(path: str) -> List[Dict[str, Any]]:
#     if not pathlib.Path(path).exists():
#         return []

#     text = pathlib.Path(path).read_text(encoding="utf-8")

#     try:
#         data = json.loads(text)
#         return data if isinstance(data, list) else [data]
#     except Exception:
#         start = text.find("[")
#         end = text.rfind("]") + 1
#         if start != -1 and end != -1:
#             try:
#                 return json.loads(text[start:end])
#             except Exception:
#                 pass
#     return []


# def load_jsonl_results(path: str) -> List[Dict[str, Any]]:
#     if not pathlib.Path(path).exists():
#         return []

#     entries = []
#     for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
#         line = line.strip()
#         if not line:
#             continue
#         try:
#             entries.append(json.loads(line))
#         except Exception:
#             continue
#     return entries


# # ============================================================
# # 🧠 NORMALIZATION
# # ============================================================

# def normalize_text(s: str) -> str:
#     if not s:
#         return ""
#     s = s.lower()
#     # remove slashes and punctuation that vary between sources
#     for ch in ["/", "\\", "-", "—", "–", ":", ";", ",", "." , "\""]:
#         s = s.replace(ch, " ")
#     s = " ".join(s.split())
#     return s.strip()


# # ============================================================
# # 🔍 MATCHING ENGINE
# # ============================================================

# def similarity_score(a: str, b: str) -> float:
#     a_tokens = set(a.split())
#     b_tokens = set(b.split())
#     if not a_tokens or not b_tokens:
#         return 0.0
#     return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


# def find_match_with_score(norm: str, results_map: Dict[str, Any]) -> Tuple[Any, float]:
#     if not norm:
#         return None, 0.0

#     # exact
#     if norm in results_map:
#         return results_map[norm], 1.0

#     best_match = None
#     best_score = 0.0

#     for k, v in results_map.items():

#         # substring
#         if norm in k or k in norm:
#             return v, 0.95

#         score = similarity_score(norm, k)
#         if score > best_score:
#             best_score = score
#             best_match = v

#     if best_score > 0.6:
#         return best_match, best_score

#     # fallback fuzzy
#     keys = list(results_map.keys())
#     m = difflib.get_close_matches(norm, keys, n=1, cutoff=0.75)
#     if m:
#         return results_map[m[0]], 0.7

#     return None, best_score


# # ============================================================
# # 📊 RECORD PROCESSING
# # ============================================================

# def extract_records(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     records = []

#     for item in data:
#         if isinstance(item.get("records"), list):
#             records.extend(item["records"])
#             continue

#         if all(k in item for k in ("text", "aspect")):
#             records.append(item)

#     return records


# def normalize_record(rec: Dict[str, Any]) -> Dict[str, Any]:
#     return {
#         "text": rec.get("text", ""),
#         "aspect": rec.get("aspect", ""),
#         "labels": ", ".join(rec.get("labels", [])),
#         "esg": rec.get("esg", ""),
#         "sentiment": rec.get("sentiment", ""),
#         "sentiment_score": rec.get("sentiment_score", 0),
#         "reasoning": rec.get("reasoning", ""),
#         "_raw": rec,
#     }


# # ============================================================
# # 🧪 PREDICTION PARSER
# # ============================================================

# def parse_prediction(pred_str: str):
#     if not pred_str:
#         return None, None

#     match = re.search(r"(LABEL_\d+):\s*([0-9.]+)", pred_str)
#     if match:
#         return match.group(1), float(match.group(2))

#     return None, None


# # ============================================================
# # 🚀 MAIN APP
# # ============================================================

# def main():
#     st.set_page_config(layout="wide")
#     st.title("🌍 ESG Matching & Evaluation Dashboard")

#     # Load data
#     data = safe_load_json(ESG_FILE)
#     records = extract_records(data)

#     if not records:
#         st.warning("No ESG records found")
#         return

#     df = pd.DataFrame([normalize_record(r) for r in records])

#     # Load results
#     results_entries = load_jsonl_results(RESULTS_FILE)

#     results_map = {}
#     for e in results_entries:
#         txt = e.get("text") or e.get("result", {}).get("text", "")
#         if txt:
#             results_map[normalize_text(txt)] = e

#     # Matching
#     df["normalized_text"] = df["text"].apply(normalize_text)

#     matches = df["normalized_text"].apply(
#         lambda x: find_match_with_score(x, results_map)
#     )

#     df["matched_result"] = matches.apply(lambda x: x[0])
#     df["match_score"] = matches.apply(lambda x: x[1])

#     # Extract predictions
#     def extract_pred(r):
#         if not isinstance(r, dict):
#             return "", ""
#         res = r.get("result", {})
#         return res.get("model", ""), res.get("prediction", "")

#     df[["matched_model", "matched_prediction"]] = df["matched_result"].apply(
#         lambda x: pd.Series(extract_pred(x))
#     )

#     df[["pred_label", "pred_score"]] = df["matched_prediction"].apply(
#         lambda x: pd.Series(parse_prediction(x))
#     )

#     # ========================================================
#     # 📊 SIDEBAR
#     # ========================================================

#     st.sidebar.header("Filters")

#     esg = st.sidebar.selectbox("ESG", ["", "E", "S", "G", "N"])
#     sentiment = st.sidebar.selectbox("Sentiment", ["", "positive", "neutral", "negative", "commitment"])
#     search = st.sidebar.text_input("Search text")
#     match_filter = st.sidebar.selectbox("Match", ["", "matched", "unmatched"])

#     filtered = df.copy()

#     if esg:
#         filtered = filtered[filtered["esg"] == esg]

#     if sentiment:
#         filtered = filtered[filtered["sentiment"] == sentiment]

#     if search:
#         filtered = filtered[filtered["text"].str.contains(search, case=False, na=False)]

#     if match_filter == "matched":
#         filtered = filtered[filtered["matched_result"].notnull()]
#     elif match_filter == "unmatched":
#         filtered = filtered[filtered["matched_result"].isnull()]

#     st.sidebar.markdown(f"**Records:** {len(filtered)}")

#     # ========================================================
#     # 📈 ANALYTICS
#     # ========================================================

#     st.subheader("📈 Analytics")

#     col1, col2, col3 = st.columns(3)
#     col1.metric("Total", len(df))
#     col2.metric("Matched", df["matched_result"].notnull().sum())
#     col3.metric("Avg Score", round(df["match_score"].mean(), 2))

#     # ========================================================
#     # 📋 TABLE
#     # ========================================================

#     st.subheader("📋 Records")

#     if filtered.empty:
#         st.warning("No data after filtering")
#         return

#     st.dataframe(
#         filtered[[
#             "aspect", "esg", "sentiment",
#             "match_score", "pred_label",
#             "pred_score", "text"
#         ]],
#         use_container_width=True
#     )

#     # ========================================================
#     # 🔍 DETAIL VIEW
#     # ========================================================

#     idx = st.selectbox("Select record", filtered.index)

#     rec = filtered.loc[idx]

#     st.subheader("🔍 Detail")

#     st.write("**Text**", rec["text"])
#     st.write("**Aspect**", rec["aspect"])
#     st.write("**ESG**", rec["esg"])
#     st.write("**Sentiment**", rec["sentiment"], rec["sentiment_score"])
#     st.write("**Reasoning**", rec["reasoning"])

#     st.write("### 🤖 Model Output")
#     if rec["matched_result"]:
#         st.json(rec["matched_result"])
#     else:
#         st.warning("No match found")

#     # ========================================================
#     # 🧪 DEBUG TOOL
#     # ========================================================

#     st.subheader("🧪 Matching Debug Tool")

#     user_input = st.text_area("Test matching manually")

#     if user_input:
#         norm = normalize_text(user_input)
#         match, score = find_match_with_score(norm, results_map)

#         st.write("Normalized:", norm)
#         st.write("Score:", score)

#         if match:
#             st.json(match)
#         else:
#             st.warning("No match")


# if __name__ == "__main__":
#     main()

# import json
# import pathlib
# from typing import List, Dict, Any
# import difflib

# import pandas as pd
# import streamlit as st




# def safe_load_json(path: str) -> List[Dict[str, Any]]:
#     text = pathlib.Path(path).read_text(encoding="utf-8")
#     try:
#         data = json.loads(text)
#         if isinstance(data, list):
#             return data
#         return [data]
#     except Exception:
#         # fallback: extract first [...] block
#         start = text.find("[")
#         end = text.rfind("]") + 1
#         if start != -1 and end != -1:
#             try:
#                 return json.loads(text[start:end])
#             except Exception:
#                 pass
#     return []


# # new: normalize text for matching
# def normalize_text(s: str) -> str:
#     if not s:
#         return ""
#     s = s.lower()
#     # remove slashes and punctuation that vary between sources
#     for ch in ["/", "\\", "-", "—", "–", ":", ";", ",", "." , "\""]:
#         s = s.replace(ch, " ")
#     s = " ".join(s.split())
#     return s.strip()


# # new: load JSONL results file into a list / map keyed by normalized text
# def load_jsonl_results(path: str) -> List[Dict[str, Any]]:
#     path_obj = pathlib.Path(path)
#     if not path_obj.exists():
#         return []
#     entries: List[Dict[str, Any]] = []
#     for raw in path_obj.read_text(encoding="utf-8").splitlines():
#         raw = raw.strip()
#         if not raw or raw.startswith("//"):
#             continue
#         try:
#             obj = json.loads(raw)
#             entries.append(obj)
#         except Exception:
#             # some files include extraneous text; try to extract {...}
#             start = raw.find("{")
#             end = raw.rfind("}") + 1
#             if start != -1 and end != -1:
#                 try:
#                     entries.append(json.loads(raw[start:end]))
#                 except Exception:
#                     continue
#     return entries


# def extract_records(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     records: List[Dict[str, Any]] = []
#     for item in data:
#         # prefer explicit "records" lists
#         if isinstance(item.get("records"), list) and item["records"]:
#             records.extend(item["records"])
#             continue
#         # try parsing raw_output if present and looks like JSON
#         raw = item.get("raw_output") or item.get("raw")
#         if raw and isinstance(raw, str) and raw.strip():
#             try:
#                 parsed = json.loads(raw)
#                 if isinstance(parsed, list):
#                     for r in parsed:
#                         if isinstance(r, dict):
#                             records.append(r)
#             except Exception:
#                 # ignore non-json raw_output
#                 pass
#         # if item itself looks like a record
#         if all(k in item for k in ("text", "aspect")):
#             records.append(item)
#     return records


# def normalize(rec: Dict[str, Any]) -> Dict[str, Any]:
#     return {
#         "text": rec.get("text", "")[:1000],
#         "aspect": rec.get("aspect", "") or rec.get("aspect"),
#         "labels": ", ".join(rec.get("labels", [])) if isinstance(rec.get("labels"), list) else rec.get("labels", ""),
#         "esg": rec.get("esg", "") or rec.get("ESG", ""),
#         "sentiment": rec.get("sentiment", ""),
#         "sentiment_score": rec.get("sentiment_score", 0),
#         "reasoning": rec.get("reasoning", ""),
#         "_raw": rec,
#     }


# def main():
#     st.set_page_config(page_title="ESG Records viewer", layout="wide")
#     st.title("ESG Records — viewer")

#     data = safe_load_json(ESG_FILE)
#     records = extract_records(data)
#     if not records:
#         st.warning(f"No records found in {ESG_FILE}")
#         st.stop()

#     df = pd.DataFrame([normalize(r) for r in records])

#     # load JSONL results and build map by normalized text
#     results_entries = load_jsonl_results(RESULTS_FILE)
#     results_map: Dict[str, Dict[str, Any]] = {}
#     for e in results_entries:
#         text_val = e.get("text") or e.get("result", {}).get("text") or e.get("label") or ""
#         if text_val:
#             results_map[normalize_text(str(text_val))] = e

#     # attach normalized text and attempt to match (exact then fuzzy)
#     df["normalized_text"] = df["text"].astype(str).apply(normalize_text)

#     def find_match(norm: str) -> Any:
#         if not norm:
#             return None
#         if norm in results_map:
#             return results_map[norm]
#         # fuzzy fallback
#         keys = list(results_map.keys())
#         if not keys:
#             return None
#         m = difflib.get_close_matches(norm, keys, n=1, cutoff=0.8)
#         if m:
#             return results_map[m[0]]
#         return None

#     df["matched_result"] = df["normalized_text"].apply(find_match)
#     # expose common prediction fields for display
#     def extract_pred(r):
#         if not isinstance(r, dict):
#             return {"matched_model": "", "matched_prediction": ""}
#         res = r.get("result") or r.get("result", {})
#         model = res.get("model") or r.get("model") or ""
#         pred = res.get("prediction") or r.get("prediction") or ""
#         return {"matched_model": model, "matched_prediction": pred}

#     preds = df["matched_result"].apply(extract_pred).apply(pd.Series)
#     df = pd.concat([df, preds], axis=1)

#     # Sidebar filters
#     st.sidebar.header("Filters")
#     esg_options = [""] + sorted(df["esg"].dropna().unique().tolist())
#     esg = st.sidebar.selectbox("ESG", esg_options, index=0)
#     sentiment_options = [""] + sorted(df["sentiment"].dropna().unique().tolist())
#     sentiment = st.sidebar.selectbox("Sentiment", sentiment_options, index=0)
#     label_search = st.sidebar.text_input("Label contains (comma separated)")
#     aspect_search = st.sidebar.text_input("Aspect contains")
#     text_search = st.sidebar.text_input("Full-text search")
#     match_filter = st.sidebar.selectbox("Has match in results", ["", "matched", "unmatched"], index=0)

#     filtered = df.copy()
#     if esg:
#         filtered = filtered[filtered["esg"].astype(str).str.lower() == esg.lower()]
#     if sentiment:
#         filtered = filtered[filtered["sentiment"].astype(str).str.lower() == sentiment.lower()]
#     if label_search:
#         for token in [t.strip().lower() for t in label_search.split(",") if t.strip()]:
#             filtered = filtered[filtered["labels"].str.lower().str.contains(token, na=False)]
#     if aspect_search:
#         filtered = filtered[filtered["aspect"].astype(str).str.lower().str.contains(aspect_search.lower(), na=False)]
#     if text_search:
#         filtered = filtered[filtered["text"].astype(str).str.lower().str.contains(text_search.lower(), na=False)]
#     if match_filter == "matched":
#         filtered = filtered[filtered["matched_result"].notnull()]
#     elif match_filter == "unmatched":
#         filtered = filtered[filtered["matched_result"].isnull()]

#     st.sidebar.markdown(f"Results: **{len(filtered)}**")

#     # Table and selection
#     st.subheader("Records")

#     # avoid errors when filters return no rows
#     if filtered.empty:
#         st.warning("No records match the current filters.")
#         st.stop()

#     index_options = list(filtered.index)
#     selected_idx = st.selectbox(
#         "Select record index",
#         options=index_options,
#         format_func=lambda i: f"{i} — {str(filtered.at[i, 'aspect'] or '')[:40]}",
#     )

#     st.dataframe(
#         filtered[["aspect", "esg", "sentiment", "sentiment_score", "labels", "matched_model", "matched_prediction", "text"]]
#         .rename(columns={"text": "text_preview"}),
#         use_container_width=True,
#     )

#     # Detail view
#     st.subheader("Detail")
#     rec = filtered.at[selected_idx, "_raw"]
#     st.markdown("**Text**")
#     st.write(rec.get("text", ""))
#     st.markdown("**Aspect**")
#     st.write(rec.get("aspect", ""))
#     st.markdown("**Labels**")
#     st.write(rec.get("labels", []))
#     st.markdown("**ESG**")
#     st.write(rec.get("esg", ""))
#     st.markdown("**Sentiment / score**")
#     st.write(f"{rec.get('sentiment', '')} — {rec.get('sentiment_score', '')}")
#     st.markdown("**Reasoning**")
#     st.write(rec.get("reasoning", ""))

#     # show matched result if any
#     st.markdown("**Matched external result**")
#     matched = filtered.at[selected_idx, "matched_result"]
#     if matched:
#         st.json(matched)
#     else:
#         st.write("No matching JSONL result found for this record.")

#     # Quick action: show JSON for copy
#     st.subheader("Raw JSON")
#     st.json(rec)


# if __name__ == "__main__":
#     main()