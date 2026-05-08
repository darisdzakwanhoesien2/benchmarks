from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

HF_SPACE = (os.getenv("HF_SPACE") or "darisdzakwanhoesien/esg_scoring_sme").strip()


def get_client() -> Client:
    if not HF_SPACE:
        raise ValueError("HF_SPACE is empty. Set HF_SPACE or provide a default Hugging Face Space.")
    return Client(HF_SPACE)


def predict_esg(text: str):
    return get_client().predict(
        text=text,
        api_name="/predict"
    )


# from gradio_client import Client
# import os
# from dotenv import load_dotenv

# load_dotenv()

# HF_SPACE = "darisdzakwanhoesien/esg_scoring_sme"

# client = Client(HF_SPACE)


# def predict_esg(text: str):
#     """
#     Call HuggingFace Space ESG model
#     """

#     result = client.predict(
#         text=text,
#         api_name="/predict"
#     )

#     return result
