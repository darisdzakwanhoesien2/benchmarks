import streamlit as st
import sys, os
import json
from pathlib import Path
from datetime import datetime
import matplotlib
from code.classical_ml import Featureizer
from code.hybrid_model import run_hierarchical_hybrid
from code.lexicons import ASPECT_LEX, CANON_PATHS
from code.rule_based import collect_aspects, polarity_basic, tone_basic
from code.explainability import compare_explain
from api.climatebert_client import ClimateBERTClient

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── ClimateBERT ───────────────────────────────────────────────────────────────
# DO NOT instantiate client at import time (can block / timeout). Initialise lazily.
api = None
models = []

use_climatebert = st.checkbox("Use ClimateBERT (T1) — connect (optional)", value=False)
if use_climatebert:
    try:
        with st.spinner("Connecting to ClimateBERT…"):
            api = ClimateBERTClient()
            models = api.available_models if hasattr(api, "available_models") else []
            st.success(f"ClimateBERT: {len(models)} model(s) available")
    except Exception as e:
        api = None
        st.warning(f"ClimateBERT unavailable: {e}")

selected_models = st.multiselect("Select model(s)", models)

# ── Input source ──────────────────────────────────────────────────────────────
OCR_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "ocr_output"
input_mode = st.radio("Input source", ["Manual text", "OCR output file"], horizontal=True)
texts_to_process: list[dict] = []

if input_mode == "Manual text":
    text_input = st.text_area("Enter text to process with modules:", height=150)
    if text_input.strip():
        texts_to_process = [{"label": "manual_input", "text": text_input.strip()}]
else:
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

            st.subheader(f"📄 Preview ({len(chosen_pages)} page(s) selected)")
            for pf in chosen_pages[:5]:
                st.markdown(f"**{pf.name}**")
                content = pf.read_text(encoding="utf-8")
                st.text(content[:400] + ("…" if len(content) > 400 else ""))
            if len(chosen_pages) > 5:
                st.caption(f"… and {len(chosen_pages) - 5} more page(s)")

            texts_to_process = [
                {"label": f"{selected_doc}/{pf.name}", "text": pf.read_text(encoding="utf-8").strip()}
                for pf in chosen_pages
            ]

# ── Save option ───────────────────────────────────────────────────────────────
def _serialize(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_serialize(o) for o in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, np.bool_):
            return bool(obj)
    except ImportError:
        pass
    try:
        import torch
        if isinstance(obj, torch.Tensor):
            return obj.cpu().detach().numpy().tolist()
    except ImportError:
        pass
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
    return _serialize(value)

def append_record_absa(record: dict, fname: Path) -> None:
    """Append one JSON-safe record to fname immediately (atomic write)."""
    existing: list = []
    if fname.exists():
        try:
            with fname.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
            existing = loaded if isinstance(loaded, list) else [loaded]
        except Exception:
            existing = []
    existing.append(make_json_safe(record))
    tmp = fname.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    tmp.replace(fname)  # atomic replace

# ── Run ───────────────────────────────────────────────────────────────────────
save_json = st.checkbox("Save results to JSON (append to results/absa_results.json)", value=True)
results_dir = Path(__file__).resolve().parents[1] / "results"
results_dir.mkdir(parents=True, exist_ok=True)
fname = results_dir / "absa_results.json"

if texts_to_process:
    st.divider()
    run_deep = st.checkbox("Run Deep Model (mBERT) Demo (may download models / use GPU)", value=False)
    all_safe_records = []
    total = len(texts_to_process) * len(selected_models)
    step = 0
    progress = st.progress(0)
    status = st.empty()

    for text_input in texts_to_process:
        label = text_input["label"]
        status.info(f"⏳ Processing `{label}`…")
        st.divider()
        st.subheader(f"📄 `{label}`")

        # ── Rule-Based ────────────────────────────────────────────────────────
        st.header("Rule-Based Model Demo")
        try:
            aspects = collect_aspects(text_input)
            polarity = polarity_basic(text_input)
            tone = tone_basic(text_input)
            st.write(f"Aspects: {aspects}")
            st.write(f"Polarity: {polarity}")
            st.write(f"Tone: {tone}")
            rb_out = {"aspects": aspects, "polarity": polarity, "tone": tone}
        except Exception as e:
            st.error(f"Rule-based error: {e}")
            rb_out = {"error": str(e)}

        # ── Classical ML ──────────────────────────────────────────────────────
        st.header("Classical ML Demo")
        try:
            from code.classical_ml import run_classical_ml
            out_csv, out_df, fig, coef_sent, coef_aspect = run_classical_ml(text_input)
            st.dataframe(out_df, use_container_width=True)
            st.dataframe(coef_sent, use_container_width=True)
            st.dataframe(coef_aspect, use_container_width=True)
            cml_out = {"out_csv": out_csv, "out_df": out_df, "coef_sent": coef_sent, "coef_aspect": coef_aspect}
        except Exception as e:
            st.error(f"Classical ML error: {e}")
            cml_out = {"error": str(e)}

        # ── Deep Model ────────────────────────────────────────────────────────
        st.header("Deep Model (mBERT) Demo")
        deep_out = {"ran": run_deep}
        if run_deep:
            try:
                from code.deep_model import run_deep_learning
                _, deep_out_df, _, interp_df = run_deep_learning(text_input)
                st.dataframe(deep_out_df)
                st.dataframe(interp_df)
                deep_out.update({"out_df": deep_out_df, "interpretability": interp_df})
            except Exception as e:
                st.error(f"Deep model error: {e}")
                deep_out["error"] = str(e)
        else:
            st.info("Deep model skipped.")

        # ── Hybrid Model ──────────────────────────────────────────────────────
        st.header("Hybrid Model Demo")
        try:
            _, hybrid_df, _, _, _, metrics = run_hierarchical_hybrid(text_input)
            st.dataframe(hybrid_df)
            st.write("Metrics:", metrics)
            hybrid_out = {"out_df": hybrid_df, "metrics": metrics}
        except Exception as e:
            st.error(f"Hybrid model error: {e}")
            hybrid_out = {"error": str(e)}

        # ── Explainability ────────────────────────────────────────────────────
        st.header("Explainability Dashboard")
        try:
            expl_df, expl_fig, expl_scatter = compare_explain()
            st.dataframe(expl_df)
            if expl_fig:
                st.pyplot(expl_fig)
            if expl_scatter is not None:
                st.plotly_chart(expl_scatter)
            expl_out = {"compare_df": expl_df}
        except Exception as e:
            st.error(f"Explainability error: {e}")
            expl_out = {"error": str(e)}

        # ── Build & save record immediately ───────────────────────────────────
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": label,
            "input_text": text_input,
            "rule_based": rb_out,
            "classical_ml": cml_out,
            "deep_model": deep_out,
            "hybrid_model": hybrid_out,
            "explainability": expl_out,
        }
        safe_record = make_json_safe(record)
        all_safe_records.append(safe_record)

        if save_json:
            try:
                append_record_absa(record, fname)
                st.success(f"💾 `{label}` saved to `{fname.name}`")
            except Exception as save_err:
                st.error(f"❌ Save failed for `{label}`: {save_err}")

        step += 1
        progress.progress(step / total)

    # ── Final summary ─────────────────────────────────────────────────────────
    progress.empty()
    status.empty()
    st.success(f"✅ Processed {len(all_safe_records)} document(s)")

    # ── Download ──────────────────────────────────────────────────────────────
    st.download_button(
        "⬇️ Download these results (JSON)",
        json.dumps(all_safe_records, ensure_ascii=False, indent=2),
        file_name=f"absa_results_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json",
        mime="application/json",
    )

    if save_json:
        st.success(f"Appended {len(all_safe_records)} record(s) to `{fname}`")

