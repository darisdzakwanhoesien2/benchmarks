from api.climatebert_client import ClimateBERTClient

api = ClimateBERTClient()

result = api.predict(
    text="The company will reduce emissions by 50% by 2030.",
    model_key="netzero-reduction"
)

print(result)