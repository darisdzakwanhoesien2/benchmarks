from gradio_client import Client
from dotenv import load_dotenv

from ._space_url import resolve_space_url

load_dotenv()


def _get_client(space_url: str | None = None) -> Client:
    """Return a gradio_client.Client using the ABSA Space URL."""

    space = resolve_space_url(
        space_url=space_url,
        env_var="HF_ABSA_SPACE",
    )
    return Client(space)


def run_rule(text: str, space_url: str | None = None):
    return _get_client(space_url).predict(
        text=text,
        api_name="/_run_rule"
    )

def run_classical(text: str, space_url: str | None = None):

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    return _get_client(space_url).predict(
        text=text,
        api_name="/_run_classical"
    )

# def run_classical(text: str, space_url: str | None = None):
#     return _get_client(space_url).predict(
#         text=text,
#         api_name="/_run_classical"
#     )


def run_classical_alt(text: str, space_url: str | None = None):
    return _get_client(space_url).predict(
        text=text,
        api_name="/_run_classical_1"
    )


def run_deep(text: str, epochs=1, space_url: str | None = None):
    return _get_client(space_url).predict(
        text=text,
        epochs=epochs,
        api_name="/_run_deep"
    )


def run_deep_alt(text: str, epochs=1, space_url: str | None = None):
    return _get_client(space_url).predict(
        text=text,
        epochs=epochs,
        api_name="/_run_deep_1"
    )


def run_hybrid(text: str, space_url: str | None = None):
    return _get_client(space_url).predict(
        text=text,
        api_name="/_run_hybrid"
    )
