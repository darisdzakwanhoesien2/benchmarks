from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

SPACE_URL = os.getenv("HF_CLIMATEBERT_SPACE")

client = Client(SPACE_URL)


def predict_all_models(text: str):

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    result = client.predict(
        text=text,
        api_name="/predict_all_models"
    )

    return result