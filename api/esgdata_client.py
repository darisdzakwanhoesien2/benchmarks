from gradio_client import Client
from dotenv import load_dotenv

from ._space_url import resolve_space_url

load_dotenv()


def _get_space_url(space_url: str | None = None) -> str:
    """Return the resolved Gradio Space URL for ESG data."""

    return resolve_space_url(
        space_url=space_url,
        env_var="HF_ESGDATA_SPACE",
    )


def _get_client(space_url: str | None = None) -> Client:
    return Client(_get_space_url(space_url))


# 1. preprocess
def preprocess(input_path, output_path="processed.csv", space_url: str | None = None):

    client = _get_client(space_url)

    return client.predict(
        input_path=input_path,
        output_path=output_path,
        api_name="/preprocess_and_save"
    )


# 2. training
def run_training(space_url: str | None = None):

    client = _get_client(space_url)

    return client.predict(
        api_name="/run_training"
    )


# 3. evaluation
def run_evaluation(space_url: str | None = None):

    client = _get_client(space_url)

    return client.predict(
        api_name="/run_evaluation"
    )


# 4. advanced evaluation
def run_advanced_evaluation(space_url: str | None = None):

    client = _get_client(space_url)

    return client.predict(
        api_name="/run_advanced_evaluation"
    )


# 5. xai
def run_xai(model_path, text, space_url: str | None = None):

    client = _get_client(space_url)

    return client.predict(
        model_path=model_path,
        text1=text,
        api_name="/run_xai_analysis"
    )


# 6. compare
def analyze_and_compare(text1, text2):

    return client.predict(
        text1=text1,
        text2=text2,
        api_name="/analyze_and_compare"
    )