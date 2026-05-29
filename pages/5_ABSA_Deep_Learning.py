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

from api.absa_client import run_deep
from utils.dataframe import hf_to_df
from utils.visualization import render_plot


st.title("ABSA Deep Learning")
add_page_explanation(__file__)

space_url = st.text_input(
    "Hugging Face Space URL (optional)",
    value="",
    help="If set, this will override the default HF Space URL / environment variable.",
)

text = st.text_area("Enter ESG Text")

epochs = st.slider("Epochs", 1, 10, 1)


if st.button("Run Deep Learning ABSA"):

    result = run_deep(text, epochs, space_url=space_url or None)

    csv = result[0]
    predictions = hf_to_df(result[1])
    plot = result[2]
    tokens = hf_to_df(result[3])

    st.dataframe(predictions)

    render_plot(plot)

    st.subheader("Token Interpretability")
    add_section_explanation("Token Interpretability")
    st.dataframe(tokens)

    st.download_button(
        "Download CSV",
        open(csv, "rb"),
        file_name="absa_deep.csv"
    )
