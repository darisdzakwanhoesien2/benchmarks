import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterable

import numpy as np
import pandas as pd
from difflib import SequenceMatcher
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
from sklearn.preprocessing import MultiLabelBinarizer
import matplotlib.pyplot as plt
import seaborn as sns

# Optional: parsing helper from workspace (not required, but available)
# [`parse_document`](code/utils.py)
try:
    from code.utils import parse_document
except Exception:
    try:
        # When running as a script from code/ directory, the local module is importable as `utils`
        from utils import parse_document  # type: ignore
    except Exception:
        # Fallback: simple pass-through parser (returns whole text as one item)
        def parse_document(text):
            return [text]


DATA_DIR = Path("data/new_data")
OUTPUT_CSV = Path("results") / "aligned_dataset.csv"
CM_DIR = Path("results") / "confusion_matrices"


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)


def safe_get_absa_df(absa_json: Any) -> pd.DataFrame:
    """
    Try to extract a DataFrame from known ABSA JSON shapes.
    Looks for keys like 'classical_ml' -> 'out_df' or top-level 'out_df'.
    """
    if isinstance(absa_json, dict):
        # common packaging: { "classical_ml": { "out_df": [...] } }
        if "classical_ml" in absa_json and isinstance(absa_json["classical_ml"], dict):
            out = absa_json["classical_ml"].get("out_df") or absa_json["classical_ml"].get("out_df", [])
            return pd.DataFrame(out)
        # direct out_df
        if "out_df" in absa_json:
            return pd.DataFrame(absa_json["out_df"])
    if isinstance(absa_json, list) and absa_json:
        # try to find first element containing classical_ml/out_df
        for item in absa_json:
            if isinstance(item, dict) and "classical_ml" in item:
                return safe_get_absa_df(item)
            if isinstance(item, dict) and "out_df" in item:
                return pd.DataFrame(item["out_df"])
    # fallback: try to convert whatever to dataframe
    try:
        return pd.DataFrame(absa_json)
    except Exception:
        return pd.DataFrame()


def normalize_col_candidates(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in df.columns:
        low = c.lower()
        for cand in candidates:
            if cand.lower() == low:
                return c
    return None


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_absa_rows_by_text(text: str, absa_df: pd.DataFrame, substr_threshold: float = 0.01, fuzzy_threshold: float = 0.75) -> pd.DataFrame:
    """
    1) Prefer direct substring match: absa sentence contained in ground-truth sentence.
    2) Fallback: fuzzy match sentence pairs by ratio.
    """
    if absa_df.empty:
        return absa_df

    # find candidate text column
    text_col = normalize_col_candidates(absa_df, ["Sentence_Text", "sentence_text", "text", "Sentence", "SentenceText"])
    if text_col is None:
        # try first string column
        text_cols = [c for c in absa_df.columns if absa_df[c].dtype == object]
        if not text_cols:
            return pd.DataFrame()
        text_col = text_cols[0]

    # substring matches (exact containment)
    mask = absa_df[text_col].apply(lambda s: isinstance(s, str) and (s.strip() and s.strip() in text))
    matched = absa_df[mask]
    if not matched.empty:
        return matched

    # fuzzy fallback
    scores = absa_df[text_col].fillna("").astype(str).apply(lambda s: fuzzy_ratio(s, text))
    best = scores[scores >= fuzzy_threshold]
    if not best.empty:
        return absa_df.loc[best.index]
    return pd.DataFrame()


def extract_absa_sentiment(matched_df: pd.DataFrame) -> str:
    if matched_df.empty:
        return "none"
    # possible column names
    sent_col = normalize_col_candidates(matched_df, ["Sentiment_Pred", "sentiment_pred", "sentiment", "Sentiment"])
    if sent_col is None:
        # try common lower-case
        for c in matched_df.columns:
            if "sent" in c.lower():
                sent_col = c
                break
    if sent_col is None:
        return "none"
    mode = matched_df[sent_col].mode()
    if mode.empty:
        return "none"
    return str(mode.iloc[0])


def extract_absa_aspect(matched_df: pd.DataFrame) -> List[str]:
    """
    Extract aspect(s) from matched ABSA rows. Return list (possibly empty).
    """
    if matched_df.empty:
        return []
    # possible aspect column names
    aspect_col = normalize_col_candidates(matched_df, ["Aspect", "aspect", "aspect_pred", "Aspect_Pred", "Category", "category"])
    if aspect_col is None:
        # try any column mentioning 'aspect' or 'label'
        for c in matched_df.columns:
            if "aspect" in c.lower() or "label" in c.lower() or "cat" in c.lower():
                aspect_col = c
                break
    if aspect_col is None:
        return []
    vals = matched_df[aspect_col].dropna().astype(str).tolist()
    # split if stored as comma-separated
    out = []
    for v in vals:
        parts = [p.strip() for p in v.split(",") if p.strip()]
        out.extend(parts if parts else [v])
    # deduplicate while preserving order
    seen = set()
    dedup = []
    for x in out:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
    return dedup


def majority_vote(candidates: Iterable[Any]) -> Any:
    """
    Simple majority vote over candidates. Handles lists by flattening.
    Returns most common item or 'none' if no candidate.
    """
    flat = []
    for c in candidates:
        if c is None:
            continue
        if isinstance(c, list):
            flat.extend([str(x) for x in c if x not in (None, "", "none")])
        else:
            if str(c) not in ("", "none"):
                flat.append(str(c))
    if not flat:
        return "none"
    vals, counts = np.unique(flat, return_counts=True)
    idx = counts.argmax()
    return vals[idx]


def build_benchmark_map(benchmark_json: Any) -> Dict[str, Any]:
    """
    Build model -> prediction map from benchmark list.
    Expected shape: list of { "model": "...", "result": {...} }
    """
    out = {}
    if isinstance(benchmark_json, dict):
        # maybe already a map
        return benchmark_json
    if isinstance(benchmark_json, list):
        for item in benchmark_json:
            if not isinstance(item, dict):
                continue
            model = item.get("model") or item.get("name") or item.get("model_name")
            # try to extract usable prediction content
            result = item.get("result") or item.get("prediction") or item.get("pred") or item.get("output")
            # normalize simple JSON structures to strings/lists
            if isinstance(result, dict):
                # flatten if simple keys
                # examples: {"prediction": "yes"} or {"labels": ["a","b"]}
                if "prediction" in result and isinstance(result["prediction"], (str, list)):
                    result = result["prediction"]
                elif "labels" in result:
                    result = result["labels"]
                elif "label" in result:
                    result = result["label"]
            if model:
                out[str(model)] = result
    return out


def save_confusion_matrix(y_true, y_pred, labels=None, fname: Path = None, title: str = None):
    if fname is None:
        return
    # ensure labels is a proper sequence; avoid `labels or ...` which fails for numpy arrays
    if labels is None:
        labels = np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))
    else:
        labels = np.asarray(labels)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.ylabel("True")
    plt.xlabel("Predicted")
    if title:
        plt.title(title)
    fname.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(fname, dpi=200)
    plt.close()


def align_and_evaluate(
    gt_path: Path = DATA_DIR / "data.json",
    absa_path: Path = DATA_DIR / "data_initial_absa.json",
    benchmark_path: Path = DATA_DIR / "data_benchmark.json",
    save_csv: bool = True,
    save_confusion: bool = True,
    fuzzy_threshold: float = 0.75,
    substr_threshold: float = 0.01,
) -> Dict[str, Any]:
    """
    Align the three sources and evaluate.

    Returns dict:
      {
        "df": pandas.DataFrame,
        "metrics": { ... },
        "confusion_matrices": [Path, ...]
      }
    """
    gt = load_json(gt_path)
    absa = load_json(absa_path)
    benchmark = load_json(benchmark_path)

    absa_df = safe_get_absa_df(absa)
    benchmark_map = build_benchmark_map(benchmark)

    rows = []
    # store mapping from aligned row index -> matched ABSA rows indices for inspection
    absa_matches_map = {}

    for i, item in enumerate(gt):
        text = item.get("text") or item.get("sentence") or item.get("raw") or ""
        true_labels = item.get("labels") or item.get("true_labels") or []
        if isinstance(true_labels, str):
            true_labels = [x.strip() for x in true_labels.split(",") if x.strip()]
        true_esg = item.get("esg") or item.get("true_esg") or item.get("esg_label") or None
        true_sentiment = item.get("sentiment") or item.get("true_sentiment") or None

        matched = match_absa_rows_by_text(text, absa_df, substr_threshold=substr_threshold, fuzzy_threshold=fuzzy_threshold)
        # record matched ABSA indices (for debug / inspection in UI)
        absa_matches_map[i] = matched.index.tolist() if not matched.empty else []

        absa_sent = extract_absa_sentiment(matched)
        absa_aspects = extract_absa_aspect(matched)

        bench_sent = "none"
        bench_label = []
        for k, v in benchmark_map.items():
            if v is None:
                continue
            if "sent" in k.lower():
                bench_sent = v if isinstance(v, str) else str(v)
            if any(x in k.lower() for x in ("label", "aspect", "class", "topic", "esg")):
                if isinstance(v, list):
                    bench_label.extend([str(x) for x in v])
                elif isinstance(v, str):
                    bench_label.extend([x.strip() for x in v.split(",") if x.strip()])
                else:
                    bench_label.append(str(v))
            if not bench_label and isinstance(v, (list, str)):
                if isinstance(v, str) and len(v.split()) <= 4:
                    bench_label.append(v.strip())
                if isinstance(v, list) and all(isinstance(x, str) for x in v):
                    bench_label.extend(v)

        final_label_pred = majority_vote([absa_aspects, bench_label])
        final_sentiment_pred = majority_vote([absa_sent, bench_sent])

        row = {
            "text": text,
            "true_labels": true_labels,
            "true_esg": true_esg,
            "true_sentiment": true_sentiment,
            "absa_sentiment": absa_sent,
            "absa_aspects": absa_aspects,
            "bench_label": bench_label,
            "bench_sent": bench_sent,
            "final_label_pred": final_label_pred,
            "final_sentiment_pred": final_sentiment_pred,
        }

        for k, v in benchmark_map.items():
            row[f"bench_{k}"] = v

        rows.append(row)

    df = pd.DataFrame(rows)

    metrics: Dict[str, Any] = {}
    cm_paths: List[Path] = []

    # Sentiment evaluation
    if df["true_sentiment"].notna().any():
        y_true = df["true_sentiment"].fillna("none")
        y_pred_absa = df["absa_sentiment"].fillna("none")
        y_pred_final = df["final_sentiment_pred"].fillna("none")

        rep_absa = classification_report(y_true, y_pred_absa, output_dict=True, zero_division=0)
        rep_final = classification_report(y_true, y_pred_final, output_dict=True, zero_division=0)
        metrics["sentiment_absa"] = rep_absa
        metrics["sentiment_ensemble"] = rep_final

        # save confusion matrices
        if save_confusion:
            CM_DIR.mkdir(parents=True, exist_ok=True)
            p1 = CM_DIR / "cm_sentiment_absa.png"
            p2 = CM_DIR / "cm_sentiment_ensemble.png"
            save_confusion_matrix(y_true.values, y_pred_absa.values,
                                  labels=np.unique(np.concatenate([y_true.values, y_pred_absa.values])),
                                  fname=p1, title="ABSA Sentiment CM")
            save_confusion_matrix(y_true.values, y_pred_final.values,
                                  labels=np.unique(np.concatenate([y_true.values, y_pred_final.values])),
                                  fname=p2, title="Ensemble Sentiment CM")
            cm_paths.extend([p1, p2])

    # Multi-label aspect evaluation
    if "true_labels" in df.columns and df["true_labels"].apply(bool).any():
        mlb = MultiLabelBinarizer(sparse_output=False)
        true_list = df["true_labels"].apply(lambda x: x if isinstance(x, list) else ([] if x is None else [x]))
        pred_list = df["final_label_pred"].apply(lambda x: [x] if (isinstance(x, str) and x not in ("none", "")) else ([] if x in ("none", None, "") else (x if isinstance(x, list) else [str(x)])))
        try:
            Y_true = mlb.fit_transform(true_list)
            Y_pred = mlb.transform(pred_list)
            f1_macro = f1_score(Y_true, Y_pred, average="macro", zero_division=0)
            f1_micro = f1_score(Y_true, Y_pred, average="micro", zero_division=0)
            metrics["aspects_f1_macro"] = float(f1_macro)
            metrics["aspects_f1_micro"] = float(f1_micro)
        except Exception as e:
            metrics["aspects_error"] = str(e)

    # ESG placeholder
    if "true_esg" in df.columns and df["true_esg"].notna().any():
        acc = accuracy_score(df["true_esg"].fillna("none"), df["true_esg"].fillna("none"))
        metrics["esg_placeholder_acc"] = float(acc)

    # save csv
    if save_csv:
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf8")

    result = {
        "df": df,
        "metrics": metrics,
        "confusion_matrices": [str(p) for p in cm_paths],
        "absa_matches_map": absa_matches_map,
        "output_csv": str(OUTPUT_CSV) if save_csv else None,
    }

    return result


if __name__ == "__main__":
    res = align_and_evaluate()
    # print a compact summary
    print("Metrics:", res.get("metrics", {}))