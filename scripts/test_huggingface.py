import joblib
from huggingface_hub import hf_hub_download

REPO_ID = "matheusrp41/insightcare-intent-classifier"


def main() -> None:
    model_path = hf_hub_download(repo_id=REPO_ID, filename="intent_classifier.joblib")

    model = joblib.load(model_path)

    examples = [
        "Quero cancelar meu plano.",
        "Gostei muito do atendimento.",
        "Preciso reclamar de uma cobrança.",
    ]

    predictions = model.predict(examples)

    for text, prediction in zip(examples, predictions):
        print(f"Texto: {text}")
        print(f"Intenção: {prediction}")
        print("-" * 40)

    print("Modelo carregado do Hugging Face com sucesso!")


if __name__ == "__main__":
    main()
