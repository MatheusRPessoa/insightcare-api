
import argparse

import httpx

API_URL = "http://localhost:8000/api/v1"

DEMO_INTERACTIONS = [
    {
        "channel": "CHAT",
        "transcript": (
            "Já solicitei autorização para minha cirurgia três vezes "
            "e ninguém resolveu. Vou registrar uma reclamação na ANS "
            "se não tiver uma resposta."
        ),
    },
    {
        "channel": "PHONE",
        "transcript": (
            "Meu tratamento foi negado novamente. Estou reunindo "
            "documentos para entrar com um processo judicial contra "
            "a operadora."
        ),
    },
    {
        "channel": "EMAIL",
        "transcript": (
            "Quero cancelar meu plano de saúde porque estou muito "
            "insatisfeito com a qualidade do atendimento."
        ),
    },
    {
        "channel": "CHAT",
        "transcript": (
            "Recebi uma cobrança duplicada na mensalidade deste mês "
            "e preciso que o valor seja corrigido."
        ),
    },
    {
        "channel": "PHONE",
        "transcript": (
            "Estou esperando retorno há vários dias. O atendimento "
            "está demorando muito e ninguém me explica o motivo."
        ),
    },
    {
        "channel": "CHAT",
        "transcript": (
            "Gostaria de saber se meu plano oferece cobertura "
            "para consultas com nutricionista."
        ),
    },
    {
        "channel": "EMAIL",
        "transcript": (
            "Preciso de informações sobre os horários de atendimento "
            "e os hospitais disponíveis na minha região."
        ),
    },
    {
        "channel": "CHAT",
        "transcript": (
            "Fui muito bem atendido pela equipe. O problema foi "
            "resolvido rapidamente e estou satisfeito com o serviço."
        ),
    },
    {
        "channel": "PHONE",
        "transcript": (
            "Não estou conseguindo acessar o aplicativo do plano. "
            "Como faço para recuperar minha senha?"
        ),
    },
    {
        "channel": "EMAIL",
        "transcript": (
            "Gostaria de solicitar a segunda via do boleto "
            "da mensalidade deste mês."
        ),
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Executar análises reais no Amazon Bedrock",
    )
    args = parser.parse_args()

    with httpx.Client(timeout=120.0) as client:
        for index, payload in enumerate(DEMO_INTERACTIONS, start=1):
            response = client.post(
                f"{API_URL}/interactions",
                json=payload,
            )
            response.raise_for_status()

            interaction = response.json()
            interaction_id = interaction["id"]

            print(
                f"[{index}/10] Atendimento criado: "
                f"{interaction['protocol']}"
            )

            if not args.analyze:
                continue

            try:
                analysis_response = client.post(
                    f"{API_URL}/interactions/"
                    f"{interaction_id}/analyze",
                )
                analysis_response.raise_for_status()

                analysis = analysis_response.json()

                print(
                    f"  Intenção: {analysis['intent']}"
                    f" | Risco: {analysis['risk_level']}"
                    f" | Sentimento: {analysis['sentiment']}"
                )

            except httpx.HTTPError as exc:
                print(f"  Falha na análise: {exc}")

    print("\nSeed finalizado!")


if __name__ == "__main__":
    main()
