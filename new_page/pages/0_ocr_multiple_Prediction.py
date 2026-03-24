import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.climatebert_client import ClimateBERTClient
from pathlib import Path
from datetime import datetime
import json

st.title("🔎 Multi-Model Prediction")

api = ClimateBERTClient()

# allow selecting multiple models
models = api.available_models if hasattr(api, "available_models") else []
selected_models = st.multiselect("Select model(s)", models)

# ── Input source ──────────────────────────────────────────────────────────────
OCR_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "thesis_dataset"

input_mode = st.radio("Input source", ["Manual text", "OCR output file"], horizontal=True)

texts_to_process: list[dict] = []   # list of {"label": str, "text": str}

if input_mode == "Manual text":
    text = st.text_area("Enter text", height=150)
    if text.strip():
        texts_to_process = [{"label": "manual_input", "text": text.strip()}]

else:
    # ── Discover documents (sub-folders of ocr_output) ───────────────────────
    doc_folders = sorted(
        [d for d in OCR_OUTPUT_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    ) if OCR_OUTPUT_DIR.exists() else []

    if not doc_folders:
        st.warning(f"No document folders found in `{OCR_OUTPUT_DIR}`")
    else:
        doc_names = [d.name for d in doc_folders]
        selected_doc = st.selectbox("Select document", doc_names)
        pages_dir = OCR_OUTPUT_DIR / selected_doc / "pages"

        page_files = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []

        if not page_files:
            st.warning(f"No `.md` page files found in `{pages_dir}`")
        else:
            page_names = [p.name for p in page_files]

            selection_mode = st.radio(
                "Page selection", ["All pages", "Select specific pages"], horizontal=True
            )

            if selection_mode == "All pages":
                chosen_pages = page_files
            else:
                chosen_names = st.multiselect("Select page(s)", page_names, default=[page_names[0]])
                chosen_pages = [pages_dir / n for n in chosen_names]

            # Preview selected pages
            if chosen_pages:
                with st.expander(f"📄 Preview ({len(chosen_pages)} page(s) selected)"):
                    for pf in chosen_pages[:5]:   # limit preview to first 5
                        st.markdown(f"**{pf.name}**")
                        st.text(pf.read_text(encoding="utf-8")[:500] + ("…" if pf.stat().st_size > 500 else ""))
                    if len(chosen_pages) > 5:
                        st.caption(f"… and {len(chosen_pages) - 5} more page(s)")

                texts_to_process = [
                    {"label": f"{selected_doc}/{pf.name}", "text": pf.read_text(encoding="utf-8").strip()}
                    for pf in chosen_pages
                    if pf.read_text(encoding="utf-8").strip()
                ]

# ── Save option ───────────────────────────────────────────────────────────────
save_results = st.checkbox("Save results to JSON (append to results/predictions.json)", value=True)

# ── Run ───────────────────────────────────────────────────────────────────────
if st.button("Predict"):
    if not texts_to_process:
        st.warning("No text to process. Enter text or select at least one page.")
    elif not selected_models:
        st.warning("Select at least one model.")
    else:
        all_results = []
        progress = st.progress(0)
        total = len(texts_to_process) * len(selected_models)
        step = 0

        for item in texts_to_process:
            for model_key in selected_models:
                with st.spinner(f"[{item['label']}] Running {model_key}…"):
                    try:
                        res = api.predict(text=item["text"], model_key=model_key)
                    except Exception as e:
                        res = {"error": str(e)}

                    record = {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "model": model_key,
                        "source": item["label"],
                        "text": item["text"],
                        "result": res,
                    }
                    all_results.append(record)
                step += 1
                progress.progress(step / total)

        progress.empty()
        st.success(f"✅ {len(all_results)} prediction(s) complete")
        st.json(all_results)

        # ── Persist ───────────────────────────────────────────────────────────
        if save_results:
            results_dir = Path(__file__).resolve().parents[1] / "results"
            results_dir.mkdir(parents=True, exist_ok=True)
            fname = results_dir / "predictions.json"

            existing_records: list = []
            if fname.exists():
                try:
                    with fname.open("r", encoding="utf-8") as f:
                        loaded = json.load(f)
                    existing_records = loaded if isinstance(loaded, list) else [loaded]
                except Exception:
                    existing_records = []

            def _safe(obj):
                try:
                    json.dumps(obj)
                    return obj
                except TypeError:
                    return str(obj)

            safe_results = [
                {k: (_safe(v) if k != "result" else (_safe(v) if isinstance(v, (dict, list)) else str(v)))
                 for k, v in r.items()}
                for r in all_results
            ]

            existing_records.extend(safe_results)
            with fname.open("w", encoding="utf-8") as f:
                json.dump(existing_records, f, ensure_ascii=False, indent=2)

            st.success(f"Appended {len(safe_results)} record(s) to `{fname}`")
            st.download_button(
                "⬇️ Download these results (JSON)",
                json.dumps(safe_results, ensure_ascii=False, indent=2),
                file_name=f"predictions_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
                mime="application/json",
            )