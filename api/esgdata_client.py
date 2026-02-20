from gradio_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(os.getenv("HF_ESGDATA_SPACE"))


# 1. preprocess
def preprocess(input_path, output_path="processed.csv"):

    return client.predict(
        input_path=input_path,
        output_path=output_path,
        api_name="/preprocess_and_save"
    )


# 2. training
def run_training():

    return client.predict(
        api_name="/run_training"
    )


# 3. evaluation
def run_evaluation():

    return client.predict(
        api_name="/run_evaluation"
    )


# 4. advanced evaluation
def run_advanced_evaluation():

    return client.predict(
        api_name="/run_advanced_evaluation"
    )


# 5. xai
def run_xai(model_path, text):

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