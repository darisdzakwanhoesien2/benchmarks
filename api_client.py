from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

HF_SPACE = os.getenv("HF_SPACE")

client = Client(HF_SPACE)


def predict_esg(text: str):
    return client.predict(
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