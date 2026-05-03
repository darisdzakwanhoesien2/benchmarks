import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
from api.climatebert_client import ClimateBERTClient
from pathlib import Path
from datetime import datetime
import json

st.title("🔎 Multi-Model Prediction")
add_page_explanation(__file__)

api = ClimateBERTClient()

# allow selecting multiple models
models = api.available_models if hasattr(api, "available_models") else []
selected_models = st.multiselect("Select model(s)", models)

text = st.text_area("Enter text", height=150)

# option to save results
save_results = st.checkbox("Save results to JSON (append to results/predictions.json)", value=True)

if st.button("Predict"):
    if not text.strip():
        st.warning("Enter text first")
    elif not selected_models:
        st.warning("Select at least one model")
    else:
        results = []
        for model_key in selected_models:
            with st.spinner(f"Running inference with {model_key}..."):
                try:
                    res = api.predict(text=text, model_key=model_key)
                except Exception as e:
                    res = {"error": str(e)}
                record = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "model": model_key,
                    "text": text,
                    "result": res,
                }
                results.append(record)

        st.success("Prediction(s) complete")
        # show aggregated results
        st.json(results)

        if save_results:
            results_dir = Path(__file__).resolve().parents[1] / "results"
            results_dir.mkdir(parents=True, exist_ok=True)
            fname = results_dir / "predictions.json"

            all_records = []
            if fname.exists():
                try:
                    with fname.open("r", encoding="utf-8") as f:
                        existing = json.load(f)
                    if isinstance(existing, list):
                        all_records = existing
                    elif isinstance(existing, dict):
                        all_records = [existing]
                except Exception:
                    all_records = []

            # ensure JSON-serializable; fallback to str for non-serializable parts
            def _safe(obj):
                try:
                    json.dumps(obj)
                    return obj
                except TypeError:
                    return str(obj)

            safe_results = []
            for r in results:
                safe_r = {
                    k: (_safe(v) if k != "result" else (_safe(v) if isinstance(v, (dict, list)) else str(v)))
                    for k, v in r.items()
                }
                safe_results.append(safe_r)

            all_records.extend(safe_results)
            with fname.open("w", encoding="utf-8") as f:
                json.dump(all_records, f, ensure_ascii=False, indent=2)

            st.success(f"Appended {len(safe_results)} record(s) to {fname}")
            st.download_button(
                "Download appended records (JSON)",
                json.dumps(safe_results, ensure_ascii=False, indent=2),
                file_name=f"predictions_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
                mime="application/json",
            )