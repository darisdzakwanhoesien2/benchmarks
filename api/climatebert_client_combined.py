from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

def _get_space_url(space_url: str | None = None) -> str:
    """Resolve the Gradio Space URL to use.

    Priority:
      1) explicit argument
      2) HF_CLIMATEBERT_SPACE env var
      3) raise informative error
    """

    if space_url and space_url.strip():
        return space_url

    env_url = os.getenv("HF_CLIMATEBERT_SPACE")
    if env_url and env_url.strip():
        return env_url

    raise EnvironmentError(
        "Environment variable HF_CLIMATEBERT_SPACE is not set. "
        "Please provide a Gradio Space URL or set the env var."
    )


def predict_all_models(text: str, space_url: str | None = None):

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    client = Client(_get_space_url(space_url))

    result = client.predict(
        text=text,
        api_name="/predict_all_models"
    )

    return result