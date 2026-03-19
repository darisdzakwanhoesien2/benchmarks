import streamlit as st
import pandas as pd
from pathlib import Path
import io
import sys
import os
import importlib

# Ensure both repo root and code/ are on sys.path so imports work in different run contexts
PROJECT_DIR = Path(__file__).parent.resolve()        # .../benchmarks/code
REPO_ROOT = PROJECT_DIR.parent.resolve()            # .../benchmarks
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

st.sidebar.header("Inputs")
gt_file = st.sidebar.text_input("GT JSON path", str(DATA_DIR / "data.json"))
absa_file = st.sidebar.text_input("ABSA JSON path", str(DATA_DIR / "data_initial_absa.json"))
bench_file = st.sidebar.text_input("Benchmark JSON path", str(DATA_DIR / "data_benchmark.json"))

st.sidebar.markdown("### Matching thresholds")
fuzzy_threshold = st.sidebar.slider("Fuzzy match threshold", 0.0, 1.0, 0.75, 0.01)
substr_threshold = st.sidebar.slider("Substring min length fraction (unused currently)", 0.0, 1.0, 0.01, 0.01)

save_confusion = st.sidebar.checkbox("Save confusion matrices", value=True)
save_csv = st.sidebar.checkbox("Save CSV", value=True)

st.sidebar.markdown("### Advanced")
show_absa_matches = st.sidebar.checkbox("Show ABSA matched sentences for a selected row", value=True)

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