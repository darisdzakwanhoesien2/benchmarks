import pandas as pd
from api.climatebert_client import ClimateBERTClient


api = ClimateBERTClient()

df = pd.read_csv("data.csv")

results = api.batch_predict(
    texts=df["text"].tolist(),
    model_key="climate-sentiment"
)

df["prediction"] = [r["prediction"] for r in results]

df.to_csv("results.csv", index=False)

print("Saved results.csv")