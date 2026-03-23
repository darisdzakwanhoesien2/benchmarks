import streamlit as st
import pandas as pd
from pathlib import Path
import io
import sys
import os
import importlib
import json

# Ensure both repo root and code/ are on sys.path so imports work in different run contexts
PROJECT_DIR = Path(__file__).parents[1].resolve()        # .../benchmarks/code
REPO_ROOT = PROJECT_DIR.parents[1].resolve()            # .../benchmarks
for p in (str(REPO_ROOT), str(PROJECT_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Import aligner robustly
try:
    # prefer package-style if available
    from code.data_alignment import align_and_evaluate
    from code.data_alignment import DATA_DIR, OUTPUT_CSV
except Exception:
    try:
        from data_alignment import align_and_evaluate
        from data_alignment import DATA_DIR, OUTPUT_CSV
    except Exception:
        # fallback: load module by path
        mod_path = PROJECT_DIR / "data_alignment.py"
        spec = importlib.util.spec_from_file_location("data_alignment", str(mod_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        align_and_evaluate = mod.align_and_evaluate
        DATA_DIR = getattr(mod, "DATA_DIR", Path("data/new_data"))
        OUTPUT_CSV = getattr(mod, "OUTPUT_CSV", Path("results/aligned_dataset.csv"))

st.set_page_config(page_title="ESG Alignment / Evaluation", layout="wide")
st.title("ESG Alignment & Evaluation (interactive)")

# settings persistence
SETTINGS_PATH = Path(__file__).parents[1] / "settings.json"

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text(encoding="utf8"))
        except Exception:
            return {}
    return {}

def save_settings(cfg: dict):
    try:
        SETTINGS_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf8")
    except Exception as e:
        st.sidebar.error(f"Failed to save settings: {e}")

# load saved settings (if any) to prefill sidebar defaults
_saved = load_settings()

st.sidebar.header("Inputs")
# defaults updated to new_page/results
base_results = Path(__file__).parents[1] / "results"
default_gt = _saved.get("gt_file", str(base_results / "esg_records.json"))
default_absa = _saved.get("absa_file", str(base_results / "absa_results.json"))
default_bench = _saved.get("bench_file", str(base_results / "predictions.json"))

gt_file = st.sidebar.text_input("GT JSON path", default_gt)
absa_file = st.sidebar.text_input("ABSA JSON path", default_absa)
bench_file = st.sidebar.text_input("Benchmark JSON path", default_bench)

st.sidebar.markdown("### Matching thresholds")
fuzzy_threshold = st.sidebar.slider("Fuzzy match threshold", 0.0, 1.0, float(_saved.get("fuzzy_threshold", 0.75)), 0.01)
substr_threshold = st.sidebar.slider("Substring min length fraction (unused currently)", 0.0, 1.0, float(_saved.get("substr_threshold", 0.01)), 0.01)

save_confusion = st.sidebar.checkbox("Save confusion matrices", value=_saved.get("save_confusion", True))
save_csv = st.sidebar.checkbox("Save CSV", value=_saved.get("save_csv", True))

st.sidebar.markdown("### Advanced")
show_absa_matches = st.sidebar.checkbox("Show ABSA matched sentences for a selected row", value=_saved.get("show_absa_matches", True))

if st.sidebar.button("Run pipeline"):
    with st.spinner("Running alignment & evaluation..."):
        try:
            res = align_and_evaluate(
                gt_path=Path(gt_file),
                absa_path=Path(absa_file),
                benchmark_path=Path(bench_file),
                save_csv=save_csv,
                save_confusion=save_confusion,
                fuzzy_threshold=float(fuzzy_threshold),
                substr_threshold=float(substr_threshold),
            )
            st.success("Pipeline finished")

            df = res["df"]
            metrics = res.get("metrics", {})
            cms = res.get("confusion_matrices", [])
            absa_matches_map = res.get("absa_matches_map", {})

            st.subheader("Metrics")
            st.json(metrics)

            st.subheader("Aligned dataset (first 200 rows)")
            st.dataframe(df.head(200))

            if res.get("output_csv"):
                with open(res["output_csv"], "r", encoding="utf8") as fh:
                    csv_bytes = fh.read()
                st.download_button("Download aligned CSV", csv_bytes, file_name=Path(res["output_csv"]).name, mime="text/csv")

            st.subheader("Confusion matrices")
            if cms:
                for p in cms:
                    if Path(p).exists():
                        st.image(str(p), use_column_width=True)
            else:
                st.info("No confusion matrices were generated.")

            if show_absa_matches and len(df) > 0:
                st.subheader("Inspect ABSA matches")
                idx = st.number_input("Select aligned row index", min_value=0, max_value=max(0, len(df)-1), value=0)
                st.write("Text:", df.iloc[int(idx)]["text"])
                matched_indices = absa_matches_map.get(int(idx), [])
                if matched_indices:
                    st.write(f"Matched ABSA row indices: {matched_indices}")
                    # try to show ABSA rows from absa file
                    try:
                        import json
                        absa_json = json.load(open(absa_file, "r", encoding="utf8"))
                        # extract out_df
                        from data_alignment import safe_get_absa_df  # module local import
                        absa_df = safe_get_absa_df(absa_json)
                        st.write("Matched ABSA rows:")
                        st.table(absa_df.loc[matched_indices].reset_index(drop=True))
                    except Exception as e:
                        st.error(f"Could not load ABSA file for inspection: {e}")
                else:
                    st.write("No ABSA matches for this row.")

        except Exception as e:
            st.error(f"Pipeline failed: {e}")

# add Save / Load settings controls
if st.sidebar.button("Save sidebar settings"):
    cfg = {
        "gt_file": gt_file,
        "absa_file": absa_file,
        "bench_file": bench_file,
        "fuzzy_threshold": float(fuzzy_threshold),
        "substr_threshold": float(substr_threshold),
        "save_confusion": bool(save_confusion),
        "save_csv": bool(save_csv),
        "show_absa_matches": bool(show_absa_matches),
    }
    save_settings(cfg)
    st.sidebar.success("Settings saved to new_page/settings.json")

if st.sidebar.button("Clear saved settings"):
    try:
        if SETTINGS_PATH.exists():
            SETTINGS_PATH.unlink()
        st.sidebar.success("Saved settings cleared")
    except Exception as e:
        st.sidebar.error(f"Failed to clear settings: {e}")