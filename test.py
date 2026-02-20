from gradio_client import Client

client = Client("darisdzakwanhoesien/absa-ontology")

result = client.predict(
    # text="The company improved sustainability and reduced emissions.",
    text="Convenience in daily banking also means that we need to be easily accessible to clients. Once clients have been in touch with us, our Net Promoter Scores, which show their willingness to recommend the bank, are high. Personal & Business Banking started out at low levels and we are slowly seeing improvements in our scores. We have almost doubled our pool of Help with Banking advisers to support clients who have trouble using banking services. Another way to improve\nthe customer experience is generative AI.",
    api_name="/_run_classical"
)

print(result)
