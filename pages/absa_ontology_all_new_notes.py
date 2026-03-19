import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.classical_ml import Featureizer
from code.deep_model import SimpleDLModel
from code.explainability import compare_explain
from code.hybrid_model import run_hierarchical_hybrid
from code.lexicons import ASPECT_LEX, CANON_PATHS
from code.rule_based import collect_aspects, polarity_basic, tone_basic
from code.utils import detect_lang, Sentence
import pandas as pd
import torch
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="ABSA Ontology Modules", layout="wide")
st.title("ABSA Ontology Modules")

text_input = st.text_area("Enter text to process with modules:")


if text_input:
    st.header("Rule-Based Model Demo")
    aspects = collect_aspects(text_input)
    polarity = polarity_basic(text_input)
    tone = tone_basic(text_input)
    st.write(f"Aspects: {aspects}")
    st.write(f"Polarity: {polarity}")
    st.write(f"Tone: {tone}")


    # Classical ML
    st.header("Classical ML Pipeline Demo")
    from code.classical_ml import run_classical_ml
    out_csv, out_df, fig, coef_sent, coef_aspect = run_classical_ml(text_input)
    st.write("Classical ML Output DataFrame:")
    st.dataframe(out_df)
    st.write("Sentiment Coefficients:")
    st.dataframe(coef_sent)
    st.write("Aspect Coefficients:")
    st.dataframe(coef_aspect)

    # Deep Model
    st.header("Deep Model (mBERT) Demo")
    run_deep = st.checkbox("Run Deep Model (mBERT) Demo (may download models / use GPU)", value=False)
    if run_deep:
        from code.deep_model import run_deep_learning
        out_csv, out_df, fig, interp_df = run_deep_learning(text_input)
        st.write("Deep Model Output DataFrame:")
        st.dataframe(out_df)
        st.write("Interpretability (Top Tokens):")
        st.dataframe(interp_df)
    else:
        st.info("Deep model skipped. Enable the checkbox to run the mBERT demo (may download models and take longer).")

    # Hybrid Model
    st.header("Hybrid Model (Hierarchical + MTL) Demo")
    from code.hybrid_model import run_hierarchical_hybrid
    _, df, fig1, _, _, metrics = run_hierarchical_hybrid(text_input)
    st.write("Output DataFrame:")
    st.dataframe(df)
    st.write("Metrics:", metrics)

    # Explainability Comparison
    st.header("Explainability Dashboard")
    from code.explainability import compare_explain
    df, fig, scatter = compare_explain()
    st.write("Comparison DataFrame:")
    st.dataframe(df)
    if fig:
        st.pyplot(fig)
    if scatter is not None:
        st.plotly_chart(scatter)

    # Save results to JSON
    save_json = st.checkbox("Save input and module outputs to JSON file", value=False)
    if save_json:
        out = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input_text": text_input,
            "rule_based": {
                "aspects": aspects if 'aspects' in locals() else None,
                "polarity": polarity if 'polarity' in locals() else None,
                "tone": tone if 'tone' in locals() else None,
            },
            "classical_ml": {
                "out_csv": out_csv if 'out_csv' in locals() else None,
                "out_df": out_df if 'out_df' in locals() else None,
                "coef_sent": coef_sent if 'coef_sent' in locals() else None,
                "coef_aspect": coef_aspect if 'coef_aspect' in locals() else None,
            },
            "deep_model": {
                "ran": bool(run_deep) if 'run_deep' in locals() else False,
                "out_df": out_df if 'out_df' in locals() else None,
                "interpretability": interp_df if 'interp_df' in locals() else None,
            },
            "hybrid_model": {
                "out_df": df if 'df' in locals() else None,
                "metrics": metrics if 'metrics' in locals() else None,
            },
            "explainability": {
                "compare_df": df if 'df' in locals() else None,
            }
        }

        # helper to convert common non-JSON types into JSON-serializable values
        import numpy as np
        import matplotlib
        import plotly
        def _serialize(obj):
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient="records")
            if isinstance(obj, pd.Series):
                return obj.to_dict()
            if isinstance(obj, (list, tuple)):
                return [_serialize(o) for o in obj]
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            if isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            if isinstance(obj, torch.Tensor):
                try:
                    return obj.cpu().detach().numpy().tolist()
                except Exception:
                    return str(obj)
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, matplotlib.figure.Figure):
                return "<matplotlib.figure.Figure>"
            try:
                import plotly.graph_objs as go
                if isinstance(obj, go.Figure):
                    return obj.to_dict()
            except Exception:
                pass
            if hasattr(obj, "to_dict") and not isinstance(obj, type):
                try:
                    return obj.to_dict()
                except Exception:
                    pass
            return str(obj)

        def make_json_safe(value):
            if isinstance(value, dict):
                return {k: make_json_safe(v) for k, v in value.items()}
            if isinstance(value, list):
                return [make_json_safe(v) for v in value]
            return _serialize(value)

        safe_out = make_json_safe(out)

        # ensure results directory
        base_dir = Path(__file__).resolve().parents[1]  # .../benchmarks
        results_dir = base_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # append to a single absa_results.json file (keep as a list of records)
        fname = results_dir / "absa_results.json"
        all_results = []
        if fname.exists():
            try:
                with fname.open("r", encoding="utf-8") as f:
                    existing = json.load(f)
                if isinstance(existing, list):
                    all_results = existing
                elif isinstance(existing, dict):
                    all_results = [existing]
            except Exception:
                # corrupted or empty file -> start fresh
                all_results = []

        all_results.append(safe_out)

        # write back (overwrite with appended list)
        with fname.open("w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        st.success(f"Appended results to {fname}")
        # offer download of the single appended record
        json_str = json.dumps(safe_out, ensure_ascii=False, indent=2)
        st.download_button("Download this record (JSON)", json_str,
                           file_name=f"absa_result_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
                           mime="application/json")

