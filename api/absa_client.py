from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(os.getenv("HF_ABSA_SPACE"))


def run_rule(text):
    return client.predict(
        text=text,
        api_name="/_run_rule"
    )

def run_classical(text):

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    return client.predict(
        text=text,
        api_name="/_run_classical"
    )

# def run_classical(text):
#     return client.predict(
#         text=text,
#         api_name="/_run_classical"
#     )


def run_classical_alt(text):
    return client.predict(
        text=text,
        api_name="/_run_classical_1"
    )


def run_deep(text, epochs=1):
    return client.predict(
        text=text,
        epochs=epochs,
        api_name="/_run_deep"
    )


def run_deep_alt(text, epochs=1):
    return client.predict(
        text=text,
        epochs=epochs,
        api_name="/_run_deep_1"
    )


def run_hybrid(text):
    return client.predict(
        text=text,
        api_name="/_run_hybrid"
    )
