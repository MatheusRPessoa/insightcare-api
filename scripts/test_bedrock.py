from app.core.aws import get_bedrock_client
from app.core.config import settings


def main() -> None:
    client = get_bedrock_client()

    response = client.converse(
        modelId=settings.bedrock_model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "Responda em português e em uma frase: "
                            "qual é a finalidade de analisar "
                            "atendimentos com IA?"
                        )
                    }
                ],
            }
        ],
        inferenceConfig={
            "maxTokens": 150,
            "temperature": 0.1,
        },
    )

    content = response["output"]["message"]["content"]

    for block in content:
        if "text" in block:
            print(block["text"])

    usage = response.get("usage", {})

    print("\nTokens de entrada:", usage.get("inputTokens"))
    print("Tokens de saída:", usage.get("outputTokens"))


if __name__ == "__main__":
    main()
