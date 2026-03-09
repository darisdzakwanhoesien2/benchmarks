# -*- coding: utf-8 -*-
"""
core/explainability.py
Cross-model explainability and visualization layer for ESG ABSA.
Integrates outputs from rule-based, classical, deep, and hybrid models
to produce comparative dashboards and interpretable summaries.
"""

import numpy as np
import pandas as pd

from .app_state import app_state
from .utils import safe_plot
from .deep_model import plot_attention_plotly
from .hybrid_model import plot_ontology_scatter


# -------------------------
# Helper: safe retrieve
# -------------------------
def _get_df_safe(key: str) -> pd.DataFrame:
    state = app_state.get(key)
    if not state:
        return pd.DataFrame()
    if isinstance(state, dict):
        return state.get("df", pd.DataFrame())
    return pd.DataFrame()


# -------------------------
# Model comparison summary
# -------------------------
def compare_explain():
    """
    Combine predictions from rule-based, classical, deep, and hybrid models
    to highlight overlaps and divergences across sentiment/tone/aspect levels.
    Returns: comparison DataFrame, matplotlib fig, and optional plotly scatter.
    """
    df_rule = _get_df_safe("rule")
    df_class = _get_df_safe("classical")
    df_deep = _get_df_safe("deep")
    df_hyb = _get_df_safe("hybrid")

    # unify columns
    if df_rule.empty and df_class.empty and df_deep.empty and df_hyb.empty:
        fig = safe_plot(lambda ax: (ax.text(0.5, 0.5, "No data yet", ha="center"), ax.axis("off")), "Explainability")
        return pd.DataFrame(), fig, None

    dfs = []
    for name, df in [("Rule-based", df_rule), ("Classical", df_class),
                     ("Deep", df_deep), ("Hybrid", df_hyb)]:
        if df is None or df.empty:
            continue
        # unify into columns: Sentence_Text, Sentiment, Tone
        if "Sentiment_Pred" in df.columns:
            sent_col = "Sentiment_Pred"
        elif "RQ2_Sentiment" in df.columns:
            sent_col = "RQ2_Sentiment"
        elif "RQ1_Baseline_Sentiment" in df.columns:
            sent_col = "RQ1_Baseline_Sentiment"
        else:
            sent_col = None
        if "Tone_Pred" in df.columns:
            tone_col = "Tone_Pred"
        elif "RQ2_Tone" in df.columns:
            tone_col = "RQ2_Tone"
        else:
            tone_col = None
        base = pd.DataFrame({
            "Sentence_Text": df["Sentence_Text"] if "Sentence_Text" in df.columns else df.iloc[:, 0],
            "Sentiment": df[sent_col] if sent_col else "Neutral",
            "Tone": df[tone_col] if tone_col else "Unknown",
        })
        base["Model"] = name
        dfs.append(base)

    merged = pd.concat(dfs, ignore_index=True)

    # Compute disagreement count (sentence level)
    grp = merged.groupby("Sentence_Text")["Sentiment"].nunique().reset_index(name="Sentiment_Disagreement")
    avg_disagreement = grp["Sentiment_Disagreement"].mean() if not grp.empty else 0.0

    # Visualization
    def plot_disagreement(ax):
        if merged.empty:
            ax.text(0.5, 0.5, "No models to compare", ha="center")
            ax.axis("off")
            return
        (merged.groupby(["Model", "Sentiment"]).size()
               .unstack(fill_value=0)
               .plot(kind="bar", stacked=True, ax=ax))
        ax.set_ylabel("Sentence Count")
        ax.set_title(f"Cross-model Sentiment Comparison (Disagreement: {avg_disagreement:.2f})")

    fig = safe_plot(plot_disagreement, "Model Sentiment Comparison")

    # optional hybrid scatter
    hybrid_state = app_state.get("hybrid")
    plotly_scatter = None
    if hybrid_state:
        try:
            plotly_scatter = plot_ontology_scatter(hybrid_state)
        except Exception:
            plotly_scatter = None

    return merged, fig, plotly_scatter


# -------------------------
# Explainability fusion
# -------------------------
def explain_sentence_across_models(sentence_text: str):
    """
    Compare the same sentence across all available models and produce a consolidated explanation dict.
    Returns: dict with keys: 'sentence', 'rule', 'classical', 'deep', 'hybrid'
    """
    explanations = {"sentence": sentence_text}

    # Rule-based
    try:
        from .rule_based import explain_rule_based_sentence
        explanations["rule"] = explain_rule_based_sentence(sentence_text)
    except Exception:
        explanations["rule"] = ["(unavailable)"]

    # Classical ML
    try:
        from .classical_ml import explain_classical_sentence
        explanations["classical"] = explain_classical_sentence(sentence_text)
    except Exception:
        explanations["classical"] = {"error": "unavailable"}

    # Deep
    try:
        from .deep_model import explain_deep_sentence
        deep_expl = explain_deep_sentence(sentence_text)
        if isinstance(deep_expl, dict) and "tokens" in deep_expl:
            fig = plot_attention_plotly(deep_expl["tokens"], deep_expl["weights"], title="Deep Attention")
            explanations["deep"] = {"tokens": deep_expl["tokens"], "weights": deep_expl["weights"], "plot": fig}
        else:
            explanations["deep"] = deep_expl
    except Exception as e:
        explanations["deep"] = {"error": str(e)}

    # Hybrid
    try:
        from .hybrid_model import explain_hybrid_sentence
        explanations["hybrid"] = explain_hybrid_sentence(sentence_text)
    except Exception:
        explanations["hybrid"] = {"error": "unavailable"}

    return explanations


# -------------------------
# Visualization of consistency
# -------------------------
def plot_consistency_summary():
    """
    Build a simple consistency heatmap across model pairs.
    """
    dfs = {
        "Rule-based": _get_df_safe("rule"),
        "Classical": _get_df_safe("classical"),
        "Deep": _get_df_safe("deep"),
        "Hybrid": _get_df_safe("hybrid")
    }
    # extract sentiment vectors
    sentiment_matrix = {}
    for k, df in dfs.items():
        if df.empty:
            continue
        sent_col = next((c for c in df.columns if "Sentiment" in c), None)
        if sent_col:
            sentiment_matrix[k] = df[sent_col].reset_index(drop=True)
    if not sentiment_matrix:
        fig = safe_plot(lambda ax: (ax.text(0.5, 0.5, "No data", ha="center"), ax.axis("off")), "Consistency")
        return fig

    # compute pairwise agreements
    models = list(sentiment_matrix.keys())
    n = len(models)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i, j] = 1.0
            else:
                si = sentiment_matrix[models[i]]
                sj = sentiment_matrix[models[j]]
                m = min(len(si), len(sj))
                if m == 0:
                    mat[i, j] = 0.0
                else:
                    mat[i, j] = (si[:m] == sj[:m]).mean()

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(mat, cmap="Blues")
    ax.set_xticks(range(n))
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.set_yticks(range(n))
    ax.set_yticklabels(models)
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center", color="black", fontsize=8)
    plt.title("Sentiment Consistency Matrix")
    plt.tight_layout()
    return fig
