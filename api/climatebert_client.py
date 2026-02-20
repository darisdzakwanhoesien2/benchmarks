import os
from dotenv import load_dotenv
from gradio_client import Client
from tqdm import tqdm

load_dotenv()

class ClimateBERTClient:

    def __init__(self):

        self.space_url = os.getenv(
            "HF_SPACE_URL",
            "https://darisdzakwanhoesien-climatebert-multi-model-demo-docker.hf.space/"
        )

        self.client = Client(self.space_url)

        self.available_models = [
            "econbert",
            "controversy-classification",
            "controversy-bert",
            "netzero-reduction",
            "transition-physical",
            "renewable",
            "climate-detector",
            "climate-commitment",
            "climate-tcfd",
            "climate-s",
            "climate-specificity",
            "climate-sentiment",
            "environmental-claims",
            "climate-f",
            "climate-d-s",
            "climate-d"
        ]

    def predict(self, text, model_key):

        result = self.client.predict(
            model_key=model_key,
            text=text,
            api_name="/predict"
        )

        return {
            "model": model_key,
            "text": text,
            "prediction": result
        }

    def batch_predict(self, texts, model_key):

        results = []

        for text in tqdm(texts):
            results.append(
                self.predict(text, model_key)
            )

        return results

# import os
# from typing import List, Dict
# from dotenv import load_dotenv
# from gradio_client import Client
# from tqdm import tqdm


# load_dotenv()


# class ClimateBERTClient:

#     def __init__(self, space_url: str = None):

#         self.space_url = space_url or os.getenv(
#             "HF_SPACE_URL",
#             "https://darisdzakwanhoesien-climatebert-multi-model-demo-docker.hf.space/"
#         )

#         self.client = Client(self.space_url)

#         self.available_models = [
#             "econbert",
#             "controversy-classification",
#             "controversy-bert",
#             "netzero-reduction",
#             "transition-physical",
#             "renewable",
#             "climate-detector",
#             "climate-commitment",
#             "climate-tcfd",
#             "climate-s",
#             "climate-specificity",
#             "climate-sentiment",
#             "environmental-claims",
#             "climate-f",
#             "climate-d-s",
#             "climate-d"
#         ]

#     def predict(self, text: str, model_key: str = "econbert") -> Dict:

#         if not text:
#             raise ValueError("Text cannot be empty")

#         if model_key not in self.available_models:
#             raise ValueError(f"Invalid model_key: {model_key}")

#         result = self.client.predict(
#             model_key=model_key,
#             text=text,
#             api_name="/predict"
#         )

#         return {
#             "text": text,
#             "model": model_key,
#             "prediction": result
#         }

#     def batch_predict(
#         self,
#         texts: List[str],
#         model_key: str = "econbert"
#     ) -> List[Dict]:

#         results = []

#         for text in tqdm(texts, desc="Running inference"):
#             result = self.predict(text, model_key)
#             results.append(result)

#         return results