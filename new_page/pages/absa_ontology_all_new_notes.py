import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from code.classical_ml import Featureizer
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path: import compare_explain
    sys.path.insert(0, ROOT)t run_hierarchical_hybrid
from code.lexicons import ASPECT_LEX, CANON_PATHS
from api.climatebert_client import ClimateBERTClienty_basic, tone_basic
from pathlib import Pathetect_lang, Sentence
from datetime import datetime
import jsony as np
import torch
st.title("🔎 Multi-Model Prediction")
import matplotlib
api = ClimateBERTClient()time
from pathlib import Path
models = api.available_models if hasattr(api, "available_models") else []
selected_models = st.multiselect("Select model(s)", models)

# ── Input source ──────────────────────────────────────────────────────────────
OCR_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "ocr_output"
input_mode = st.radio("Input source", ["Manual text", "OCR output file"], horizontal=True)
texts_to_process: list[dict] = []

if input_mode == "Manual text":def _serialize(obj):
    text = st.text_area("Enter text", height=150)
    if text.strip():        return obj.to_dict(orient="records")
        texts_to_process = [{"label": "manual_input", "text": text.strip()}]s):
else:
    doc_folders = sorted(j, (list, tuple)):
        [d for d in OCR_OUTPUT_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,    if isinstance(obj, dict):
    ) if OCR_OUTPUT_DIR.exists() else []   return {k: _serialize(v) for k, v in obj.items()}

    if not doc_folders:()
        st.warning(f"No document folders found in `{OCR_OUTPUT_DIR}`")
    else:
        doc_names = [d.name for d in doc_folders]:
        selected_doc = st.selectbox("Select document", doc_names)        return bool(obj)
        pages_dir = OCR_OUTPUT_DIR / selected_doc / "pages"torch.Tensor):
        page_files = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []
            return obj.cpu().detach().numpy().tolist()
        except Exception:
            return str(obj)            st.warning(f"No `.md` page files found in `{pages_dir}`")
    if isinstance(obj, Path):
        return str(obj)            page_names = [p.name for p in page_files]
    if isinstance(obj, datetime): = st.radio(
        return obj.isoformat()s"], horizontal=True            st.warning(f"No `.md` page files found in `{pages_dir}`")
    if isinstance(obj, matplotlib.figure.Figure):
        return "<matplotlib.figure.Figure>"
    try:                chosen_pages = page_files
        import plotly.graph_objs as go
        if isinstance(obj, go.Figure):_names[0]])                "Page selection", ["All pages", "Select specific pages"], horizontal=True
            return obj.to_dict()   chosen_pages = [pages_dir / n for n in chosen_names]
    except Exception:
        pass== "All pages":
    if hasattr(obj, "to_dict") and not isinstance(obj, type):view ({len(chosen_pages)} page(s) selected)"):                chosen_pages = page_files
        try:   for pf in chosen_pages[:5]:
            return obj.to_dict()e_names[0]])
        except Exception: + ("…" if pf.stat().st_size > 500 else ""))hosen_pages = [pages_dir / n for n in chosen_names]
            pass                    if len(chosen_pages) > 5:
    return str(obj)"… and {len(chosen_pages) - 5} more page(s)")

def make_json_safe(value):
    if isinstance(value, dict):{pf.name}", "text": pf.read_text(encoding="utf-8").strip()}n chosen_pages[:5]:
        return {k: make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [make_json_safe(v) for v in value]
    return _serialize(value)
# ── Save option ───────────────────────────────────────────────────────────────
def append_record_absa(record: dict, fname: Path) -> None:ults to JSON (append to results/predictions.json)", value=True)
    """Append one JSON-safe record to fname immediately (atomic write)."""
    existing: list = []k immediately ───────────────────────_pages
    if fname.exists():
        try:ing list → append new record → write back atomically."""
            with fname.open("r", encoding="utf-8") as f:    existing: list = []
                loaded = json.load(f)─────
            existing = loaded if isinstance(loaded, list) else [loaded]value=False)
        except Exception:            with fname.open("r", encoding="utf-8") as f:
            existing = []
 = loaded if isinstance(loaded, list) else [loaded]if texts_to_process:
    existing.append(make_json_safe(record))
    tmp = fname.with_suffix(".tmp")            existing = []
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    tmp.replace(fname)  # atomic replace
bj)
# ── Input source ──────────────────────────────────────────────────────────────            return obj
input_mode = st.radio("Input source", ["Manual text", "OCR output file"], horizontal=True):
texts_to_process: list[dict] = []

if input_mode == "Manual text":    safe_record = {
    text_input = st.text_area("Enter text to process with modules:", height=150)k != "result" else (_safe(v) if isinstance(v, (dict, list)) else str(v)))            st.divider()
    if text_input.strip():
        texts_to_process = [{"label": "manual_input", "text": text_input.strip()}]    }
else:
    doc_folders = sorted(l Demo")
        [d for d in OCR_OUTPUT_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,put)
    ) if OCR_OUTPUT_DIR.exists() else []ii=False, indent=2)
         st.write(f"Aspects: {aspects}")
    if not doc_folders:
        st.warning(f"No document folders found in `{OCR_OUTPUT_DIR}`")
    else:# ── Run ───────────────────────────────────────────────────────────────────────
        doc_names = [d.name for d in doc_folders]
        selected_doc = st.selectbox("Select document", doc_names)
        pages_dir = OCR_OUTPUT_DIR / selected_doc / "pages"ct at least one page.")ort run_classical_ml
        page_files = sorted(pages_dir.glob("*.md")) if pages_dir.exists() else []t_input)
")
        if not page_files:
            st.warning(f"No `.md` page files found in `{pages_dir}`")parents[1] / "results"
        else:rue, exist_ok=True)            st.dataframe(coef_sent)
            page_names = [p.name for p in page_files]son"pect Coefficients:")
            selection_mode = st.radio(
                "Page selection", ["All pages", "Select specific pages"], horizontal=True        all_results = []
            )─────────────────────────────────
            if selection_mode == "All pages":us line
                chosen_pages = page_files_process) * len(selected_models)None
            else:
                chosen_names = st.multiselect("Select page(s)", page_names, default=[page_names[0]])
                chosen_pages = [pages_dir / n for n in chosen_names]
 _, interp_df = run_deep_learning(text_input)
                status.info(f"⏳ [{step + 1}/{total}] `{item['label']}` — `{model_key}`")
er(f"📄 Preview ({len(chosen_pages)} page(s) selected)"):
                try:for pf in chosen_pages[:5]:
                    res = api.predict(text=item["text"], model_key=model_key)
                    outcome = "✅ ok"encoding="utf-8")[:500] + ("…" if pf.stat().st_size > 500 else ""))
                except Exception as e:
                    res = {"error": str(e)}n(f"… and {len(chosen_pages) - 5} more page(s)")
                    outcome = f"⚠️ error: {e}"
                texts_to_process = [
                record = {": f"{selected_doc}/{pf.name}", "text": pf.read_text(encoding="utf-8").strip()}
                    "timestamp": datetime.utcnow().isoformat() + "Z",for pf in chosen_pages
                    "model": model_key,(encoding="utf-8").strip()
                    "source": item["label"],
                    "text": item["text"],
                    "result": res,─────────────────────────────────────────────
                }run_deep = st.checkbox("Run Deep Model (mBERT) Demo (may download models / use GPU)", value=False)
                all_results.append(record)e each result immediately to results/absa_results.json", value=True)

                # ── Save immediately after each successful prediction ──────────────────────────────────────────────────
                if save_results:
                    try:xts_to_process:
                        append_record(record, fname)        st.warning("No text to process. Enter text or select at least one page.")
                        save_status = f" — 💾 saved to `{fname.name}`"
                    except Exception as save_err:] / "results"
                        save_status = f" — ❌ save failed: {save_err}"
                else:        fname = results_dir / "absa_results.json"
                    save_status = ""
0)
                st.write(f"**{item['label']}** × `{model_key}` → {outcome}{save_status}")

                step += 1
                progress.progress(step / total)
dx, item in enumerate(texts_to_process):












        )            mime="application/json",            file_name=f"predictions_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",            json.dumps(all_results, ensure_ascii=False, indent=2),            "⬇️ Download these results (JSON)",        st.download_button(        # ── Download all results from this run ────────────────────────────────        st.json(all_results)        st.success(f"✅ {len(all_results)} prediction(s) complete")        status.empty()        progress.empty()            text_input = item["text"]
            label      = item["label"]

            status.info(f"⏳ [{idx + 1}/{total}] Processing `{label}`…")
            st.divider()
            st.subheader(f"📄 `{label}`")

            # ── Rule-Based ────────────────────────────────────────────────────
            st.header("Rule-Based Model Demo")
            try:
                aspects  = collect_aspects(text_input)
                polarity = polarity_basic(text_input)
                tone     = tone_basic(text_input)
                st.write(f"Aspects: {aspects}")
                st.write(f"Polarity: {polarity}")
            except Exception as e:.write(f"Tone: {tone}")
                st.error(f"Rule-based error: {e}"): aspects, "polarity": polarity, "tone": tone}
                st.dataframe(out_df)n_classical_ml(text_input)
                st.dataframe(coef_sent)                from code.classical_ml import run_classical_ml            # ── Classical ML ──────────────────────────────────────────────────   "explainability": {
            except Exception as e:                           "coef_sent": coef_sent, "coef_aspect": coef_aspect}ame(coef_aspect)
                st.error(f"Classical ML error: {e}")out_csv": out_csv, "out_df": out_df,
                cml_out = {"error": str(e)}

            # ── Deep Model ────────────────────────────────────────────────────total)
            st.header("Deep Model (mBERT) Demo")
            deep_out = {"ran": run_deep}
            if run_deep: document(s)")
                try:
                    from code.deep_model import run_deep_learning───────────────
                    _, deep_out_df, _, interp_df = run_deep_learning(text_input)
                    st.dataframe(deep_out_df)
                    st.dataframe(interp_df)
                    deep_out.update({"out_df": deep_out_df, "interpretability": interp_df})
                except Exception as e:
                    st.error(f"Deep model error: {e}")ct(orient="records")
                    deep_out["error"] = str(e)
            else:rn obj.to_dict()
                st.info("Deep model skipped.")
e(o) for o in obj]
            # ── Hybrid Model ──────────────────────────────────────────────────):
            st.header("Hybrid Model Demo")(v) for k, v in obj.items()}
            try:np.ndarray):
                _, hybrid_df, _, _, _, metrics = run_hierarchical_hybrid(text_input)
                st.dataframe(hybrid_df)eger, np.floating)):
                st.write("Metrics:", metrics)
                hybrid_out = {"out_df": hybrid_df, "metrics": metrics}
            except Exception as e:return bool(obj)
                st.error(f"Hybrid model error: {e}")
                hybrid_out = {"error": str(e)}
ach().numpy().tolist()
            # ── Explainability ────────────────────────────────────────────────ion:
            st.header("Explainability Dashboard")return str(obj)
            try:
                expl_df, expl_fig, expl_scatter = compare_explain()rn str(obj)
                st.dataframe(expl_df):
                if expl_fig:mat()
                    st.pyplot(expl_fig)e(obj, matplotlib.figure.Figure):
                if expl_scatter is not None:tplotlib.figure.Figure>"
                    st.plotly_chart(expl_scatter)            try:
                expl_out = {"compare_df": expl_df}h_objs as go
            except Exception as e:igure):
                st.error(f"Explainability error: {e}")
                expl_out = {"error": str(e)}

            # ── Build & save record immediately ───────────────────────────────") and not isinstance(obj, type):
            record = {                try:
                "timestamp":      datetime.utcnow().isoformat() + "Z",
                "source":         label,                except Exception:
                "input_text":     text_input,ass
                "rule_based":     rb_out,
                "classical_ml":   cml_out,
                "deep_model":     deep_out,
                "hybrid_model":   hybrid_out,
                "explainability": expl_out,                return {k: make_json_safe(v) for k, v in value.items()}
            }(value, list):
son_safe(v) for v in value]
            safe_record = make_json_safe(record)serialize(value)
            all_safe_records.append(safe_record)
 r in all_records]
            if save_json:
                try:
                    append_record_absa(record, fname)e__).resolve().parents[1]
                    st.success(f"💾 `{label}` saved to `{fname.name}`")            results_dir = base_dir / "results"
                except Exception as save_err:e, exist_ok=True)
                    st.error(f"❌ Save failed for `{label}`: {save_err}")

            progress.progress((idx + 1) / total)            existing = []

        # ── Final summary ─────────────────────────────────────────────────────                try:
        progress.empty()
        status.empty()ded = json.load(f)
        st.success(f"✅ Processed {len(all_safe_records)} document(s)")ance(loaded, list) else [loaded]

        st.download_button(
            "⬇️ Download all results (JSON)",
            json.dumps(all_safe_records, ensure_ascii=False, indent=2),   existing.extend(safe_records)
            file_name=f"absa_results_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",            with fname.open("w", encoding="utf-8") as f:
            mime="application/json",                json.dump(existing, f, ensure_ascii=False, indent=2)



        )
            st.success(f"Appended {len(safe_records)} record(s) to `{fname}`")

        # ── Download ──────────────────────────────────────────────────────────
        st.download_button(
            "⬇️ Download these results (JSON)",
            json.dumps(safe_records, ensure_ascii=False, indent=2),
            file_name=f"absa_results_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
            mime="application/json",
        )

