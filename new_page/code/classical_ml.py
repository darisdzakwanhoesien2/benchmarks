# -*- coding: utf-8 -*-
"""
core/classical_ml.py
Classical ML pipeline for ESG ABSA:
 - TF-IDF (word + char) featureizer
 - One-vs-Rest logistic regression for multi-label aspects
 - Logistic regression (or Dummy fallback) for sentiment & tone
 - Local (per-sentence) and global coefficient explanation helpers
"""

from typing import Tuple, List
import os
import tempfile

import numpy as np
import pandas as pd
from scipy.sparse import hstack, issparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier

from .utils import parse_document, safe_plot
from .lexicons import *
from .rule_based import polarity_basic, tone_basic
from .app_state import app_state


# -------------------------
# Featureizer
# -------------------------
class Featureizer:
    """
    Combined TF-IDF featureizer (word n-grams + char n-grams).
    Usage:
        f = Featureizer().fit(df_train)
        Xtr = f.transform(df_train)
        feat_names = f.feature_names()
    """
    def __init__(self, max_word=3000, max_char=2000):
        self.word_vec = TfidfVectorizer(ngram_range=(1, 2), max_features=max_word, sublinear_tf=True)
        self.char_vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), max_features=max_char, sublinear_tf=True)
        self._fitted = False

    def fit(self, df: pd.DataFrame):
        texts = df["Sentence_Text"].astype(str).tolist()
        self.word_vec.fit(texts)
        self.char_vec.fit(texts)
        self._fitted = True
        return self

    def transform(self, df: pd.DataFrame):
        if not self._fitted:
            raise RuntimeError("Featureizer must be fitted before transform()")
        texts = df["Sentence_Text"].astype(str).tolist()
        W = self.word_vec.transform(texts)
        C = self.char_vec.transform(texts)
        return hstack([W, C], format="csr")

    def feature_names(self) -> np.ndarray:
        """Return numpy array of combined feature names (word + prefixed char)."""
        if not self._fitted:
            raise RuntimeError("Featureizer must be fitted before calling feature_names()")
        w = list(self.word_vec.get_feature_names_out())
        c = ["<char>_" + x for x in self.char_vec.get_feature_names_out()]
        return np.array(w + c)


# -------------------------
# Small helpers
# -------------------------
def _safe_fit_classifier(clf, X, y):
    """
    Fit classifier with fallback when y has a single unique value.
    Returns fitted classifier.
    """
    if len(np.unique(y)) < 2:
        # fallback to dummy classifier that always predicts the majority
        dummy = DummyClassifier(strategy="most_frequent")
        dummy.fit(X, y)
        return dummy
    else:
        clf.fit(X, y)
        return clf


def coef_table_binary_safe(clf, feat_names, label_type="Sentiment", topk=8) -> pd.DataFrame:
    """
    Build a DataFrame of top positive/negative coefficients for a binary/multiclass linear classifier.
    Compatible with DummyClassifier (which does not have coef_).
    """
    if hasattr(clf, "coef_"):
        coefs = clf.coef_
        classes = list(getattr(clf, "classes_", []))
        # for binary with sklearn returning shape (n_classes,) sometimes handled
        if coefs.ndim == 1:
            # If only one class, avoid creating a fake negative class
            if len(classes) == 1:
                # Only one class present, cannot compute meaningful coefficients
                return pd.DataFrame([], columns=["Task","Class","Direction","Rank","Feature","Coefficient"])
            coefs = np.vstack([-coefs, coefs])
            classes = [f"Not-{classes[0]}", classes[0]]
    else:
        # DummyClassifier or other without coef_ -> produce empty table
        return pd.DataFrame([], columns=["Task","Class","Direction","Rank","Feature","Coefficient"])

    rows = []
    for ci, cname in enumerate(classes):
        # Defensive: skip if ci is out of bounds for coefs
        if ci >= coefs.shape[0]:
            continue
        coef = coefs[ci]
        pos_idx = np.argsort(coef)[-topk:][::-1]
        neg_idx = np.argsort(coef)[:topk]
        for rank, fi in enumerate(pos_idx, 1):
            rows.append([label_type, cname, "Positive", rank, feat_names[fi], float(coef[fi])])
        for rank, fi in enumerate(neg_idx, 1):
            rows.append([label_type, cname, "Negative", rank, feat_names[fi], float(coef[fi])])
    return pd.DataFrame(rows, columns=["Task","Class","Direction","Rank","Feature","Coefficient"])


def coef_table_aspect(clf_ovr, feat_names, topk=6) -> pd.DataFrame:
    """
    For OneVsRestClassifier of aspects: iterate over estimators and extract top features.
    If estimator missing coef_ (e.g., Dummy), skip gracefully.
    """
    rows = []
    classes = list(clf_ovr.classes_) if hasattr(clf_ovr, "classes_") else []
    estimators = getattr(clf_ovr, "estimators_", [])
    for cname, est in zip(classes, estimators):
        if not hasattr(est, "coef_"):
            continue
        coef = est.coef_.ravel()
        pos_idx = np.argsort(coef)[-topk:][::-1]
        neg_idx = np.argsort(coef)[:topk]
        for rank, fi in enumerate(pos_idx, 1):
            rows.append(["Aspect", cname, "Positive", rank, feat_names[fi], float(coef[fi])])
        for rank, fi in enumerate(neg_idx, 1):
            rows.append(["Aspect", cname, "Negative", rank, feat_names[fi], float(coef[fi])])
    return pd.DataFrame(rows, columns=["Task","Class","Direction","Rank","Feature","Coefficient"])


def local_explain(x_row, feat_names, clf, pred_label=None, topk=5):
    """
    Local (per-sample) explanation by multiplying feature values by linear coefficients.
    x_row must be a 1xN sparse matrix (csr) from Featureizer.transform.
    """
    # Ensure x_row is 1xN sparse matrix
    if not hasattr(x_row, "toarray") and not issparse(x_row):
        # try converting list -> array
        x_arr = np.asarray(x_row).ravel()
    else:
        x_arr = x_row.toarray().ravel()

    if hasattr(clf, "coef_"):
        coefs = clf.coef_
        classes = list(getattr(clf, "classes_", []))
        if coefs.ndim == 1:
            coef = coefs
        else:
            if pred_label is not None and pred_label in classes:
                coef = coefs[classes.index(pred_label)]
            else:
                coef = np.mean(coefs, axis=0)
    else:
        # Dummy fallback -> no informative coefficients
        return []

    contrib = x_arr * coef
    nz = np.where(x_arr != 0)[0]
    if nz.size == 0:
        return []
    idx_sorted = nz[np.argsort(np.abs(contrib[nz]))[::-1][:topk]]
    return [{"feature": feat_names[i], "contribution": float(contrib[i])} for i in idx_sorted]


# -------------------------
# Main runner
# -------------------------
def build_ml_df(raw: str) -> pd.DataFrame:
    """Create a dataframe with weak labels from parsed sentences."""
    sents = parse_document(raw)
    rows = []
    for s in sents:
        asp = [a for a in ASPECT_LEX.keys() if any_match(ASPECT_LEX[a], s.text)]
        rows.append({
            "Sentence_ID": s.idx,
            "Sentence_Text": s.text,
            "Section": s.section,
            "Section_Type": s.section_type,
            "Language": s.lang,
            "Aspect_Weak": ", ".join(asp) if asp else "General",
            "Sentiment_Weak": polarity_basic(s.text),
            "Tone_Weak": tone_basic(s.text)
        })
    return pd.DataFrame(rows)


def run_classical_ml(raw_text: str) -> Tuple[str, pd.DataFrame, object, pd.DataFrame, pd.DataFrame]:
    """
    Run classical ML pipeline:
     - Build dataset
     - Fit TF-IDF Featureizer
     - Train OneVsRestClassifier (LogReg) for aspects
     - Train LogisticRegression for sentiment and tone (or Dummy fallback)
     - Return CSV path, validation dataframe, matplotlib figure, coef_sent, coef_aspect
    """
    df = build_ml_df(raw_text)
    if len(df) < 2:
        empty = pd.DataFrame()
        fig = safe_plot(lambda ax: (ax.text(0.5, 0.5, "Not enough data", ha="center"), ax.axis("off")), "Classical ML")
        app_state["classical"] = None
        return None, empty, fig, empty, empty

    # Train / validation split
    tr, va = train_test_split(df, test_size=0.4, random_state=42)
    feat = Featureizer().fit(tr)
    Xtr = feat.transform(tr)
    Xva = feat.transform(va)
    feat_names = feat.feature_names()

    # Multi-label aspects
    y_aspect = [a.split(", ") if isinstance(a, str) and a else ["General"] for a in tr["Aspect_Weak"]]
    mlb = MultiLabelBinarizer().fit(y_aspect)
    Ytr = mlb.transform(y_aspect)

    # Fit classifiers with safe fallback
    clfA = OneVsRestClassifier(LogisticRegression(max_iter=500, solver="liblinear"))
    try:
        clfA.fit(Xtr, Ytr)
    except Exception:
        # If something fails, fit dummy per-class classifier via OneVsRest with DummyClassifier
        estimators = [DummyClassifier(strategy="most_frequent").fit(Xtr, Ytr[:, i]) for i in range(Ytr.shape[1])]
        # Create a simple object to mimic estimators_ and classes_
        class SimpleOVR:
            pass
        clfA = SimpleOVR()
        clfA.classes_ = mlb.classes_
        clfA.estimators_ = estimators

    # Sentiment & Tone (single-label)
    y_sent = tr["Sentiment_Weak"].values
    y_tone = tr["Tone_Weak"].values
    clfS = _safe_fit_classifier(LogisticRegression(max_iter=500, solver="liblinear"), Xtr, y_sent)
    clfT = _safe_fit_classifier(LogisticRegression(max_iter=500, solver="liblinear"), Xtr, y_tone)

    # Predictions on validation
    # Aspects (OneVsRest or fallback)
    try:
        Pa = clfA.predict(Xva)
        predsA = mlb.inverse_transform(Pa)
    except Exception:
        # fallback: predict empty aspect list
        predsA = [("General",) for _ in range(Xva.shape[0])]

    sentP = clfS.predict(Xva)
    toneP = clfT.predict(Xva)

    out = va.copy().reset_index(drop=True)
    out["Aspect_Pred"] = [", ".join(list(a)) for a in predsA]
    out["Sentiment_Pred"] = sentP
    out["Tone_Pred"] = toneP
    out["Ontology_Path"] = [
        "; ".join([CANON_PATHS.get(a, "General → Misc") for a in (a_list if isinstance(a_list, (list, tuple)) else [a_list])])
        for a_list in predsA
    ]

    # Coefficient tables
    coef_sent = coef_table_binary_safe(clfS, feat_names, "Sentiment")
    coef_aspect = coef_table_aspect(clfA, feat_names)

    def _plot(ax):
        if out.empty:
            ax.text(0.5, 0.5, "No data", ha="center")
            ax.axis("off")
            return
        out["Sentiment_Pred"].value_counts().plot(kind="bar", ax=ax)
        ax.set_ylabel("Count")

    fig = safe_plot(_plot, "Classical ML: Sentiment Predictions (val)")

    out_csv = os.path.join(tempfile.gettempdir(), "esg_classical_ml_outputs.csv")
    out.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # persist artifacts
    app_state["classical"] = {
        "df_train": tr.reset_index(drop=True),
        "df_val": out,
        "feat": feat,
        "feat_names": feat_names,
        "clfS": clfS,
        "clfA": clfA,
        "clfT": clfT,
        "coef_sent": coef_sent,
        "coef_aspect": coef_aspect,
        "mlb": mlb,
        "csv": out_csv
    }

    return out_csv, out, fig, coef_sent, coef_aspect


# -------------------------
# Explain helper
# -------------------------
def explain_classical_sentence(sentence_text: str):
    """
    Provide prediction + local + global explanations for a single sentence.
    Requires that run_classical_ml has been executed at least once (app_state['classical'] set).
    """
    state = app_state.get("classical")
    if not state:
        return {"error": "Classical model not run yet."}

    feat = state["feat"]
    clfS = state["clfS"]
    feat_names = state["feat_names"]

    X = feat.transform(pd.DataFrame([{"Sentence_Text": sentence_text}]))
    try:
        pred = clfS.predict(X)[0]
    except Exception as e:
        pred = None

    local = local_explain(X, feat_names, clfS, pred_label=pred, topk=6)
    # Global top features for sentiment (state['coef_sent'] is a DataFrame)
    top_glob = state.get("coef_sent", pd.DataFrame()).nlargest(8, "Coefficient") if isinstance(state.get("coef_sent"), pd.DataFrame) and not state.get("coef_sent").empty else pd.DataFrame()

    return {"prediction": pred, "local_features": local, "global_top": top_glob}