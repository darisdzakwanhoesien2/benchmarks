import streamlit as st
from pathlib import Path
import importlib.util
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
PAGES_DIR = Path(__file__).resolve().parent
if str(PAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PAGES_DIR))

# Force `utils` to resolve to the local package even if Streamlit cached a
# third-party module with the same name.
utils_init = ROOT_DIR / "utils" / "__init__.py"
loaded_utils = sys.modules.get("utils")
if (
    loaded_utils is None
    or not hasattr(loaded_utils, "__path__")
    or str(ROOT_DIR / "utils") not in [str(Path(p).resolve()) for p in getattr(loaded_utils, "__path__", [])]
):
    spec = importlib.util.spec_from_file_location(
        "utils",
        utils_init,
        submodule_search_locations=[str(ROOT_DIR / "utils")],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["utils"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)

from _page_explanations import add_page_explanation, add_section_explanation
import pandas as pd

from utils.climatebert_batch import batch_process_csv
from utils.climatebert_groundtruth_storage import load_results


CSV = "data/ground_truth/absa_mapping.csv"

st.title("ClimateBERT Batch Processor (Linux)")
add_page_explanation(__file__)

df = pd.read_csv(CSV)

total = len(df)

results = load_results()

processed = len(set(x["index"] for x in results if "index" in x))

st.metric("Total", total)
st.metric("Processed", processed)
st.metric("Remaining", total - processed)

progress = st.progress(processed / total if total else 0)

status = st.empty()


def update(current, total):

    progress.progress(current / total)
    status.text(f"{current}/{total}")


batch_size = st.number_input("Batch size", 1, 1000, 10)

if st.button("Run Linux Batch"):

    new, proc, total = batch_process_csv(
        CSV,
        batch_size,
        update
    )

    st.success(f"{new} processed")

    st.rerun()

# import streamlit as st
# import pandas as pd

# from utils.climatebert_batch import batch_process_csv
# from utils.climatebert_groundtruth_storage_windows import load_results


# st.title("ClimateBERT Batch Processor")

# CSV = "data/ground_truth_windows/absa_mapping.csv"

# df = pd.read_csv(CSV)

# total = len(df)

# results = load_results()

# processed = len(set(r["index"] for r in results if "index" in r))

# remaining = total - processed

# st.metric("Total", total)
# st.metric("Processed", processed)
# st.metric("Remaining", remaining)

# progress = st.progress(processed / total if total else 0)

# status = st.empty()


# def update(current, total):

#     progress.progress(current / total)

#     status.text(f"{current}/{total}")


# batch = st.number_input("Batch size", 1, 1000, 10)

# if st.button("Run Batch"):

#     new, proc, tot = batch_process_csv(

#         CSV,
#         batch_size=batch,
#         progress_callback=update

#     )

#     st.success(f"{new} processed")

#     st.rerun()
