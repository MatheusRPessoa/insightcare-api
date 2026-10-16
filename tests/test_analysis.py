from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.schemas.analysis import AnalysisResult


def test_analyze_interaction(
    client: TestClient,
    create_interaction,
) -> None:
    interaction = create_interaction(
        transcript=(
            "Quero cancelar meu plano porque o atendimento não resolveu meu problema."
        )
    )

    mocked_ml = {
        "intent": "cancelamento",
        "confidence": 0.9411,
        "model": "tfidf-logistic-regression",
    }

    mocked_llm = AnalysisResult(
        summary="Beneficiário manifesta intenção de cancelamento.",
        sentiment="NEGATIVE",
        risk_level="MEDIUM",
        detected_signals=["intencao_cancelamento"],
        evidence=["Quero cancelar meu plano"],
        recommended_action=("Encaminhar para a equipe de relacionamento."),
    )

    with (
        patch(
            "app.api.routes.interactions.MLClassifierService.classify",
            return_value=mocked_ml,
        ),
        patch(
            "app.api.routes.interactions.BedrockAnalysisService.analyze",
            return_value=mocked_llm,
        ),
    ):
        response = client.post(f"/api/v1/interactions/{interaction['id']}/analyze")

    assert response.status_code == 200, response.text

    saved_response = client.get(f"/api/v1/interactions/{interaction['id']}/analysis")

    assert saved_response.status_code == 200
    assert saved_response.json()["intent"] == "cancelamento"
    assert saved_response.json()["risk_level"] == "MEDIUM"

    interaction_response = client.get(f"/api/v1/interactions/{interaction['id']}")

    assert interaction_response.status_code == 200
    assert interaction_response.json()["status"] == "ANALYZED"

    result = response.json()

    assert result["interaction_id"] == interaction["id"]
    assert result["intent"] == "cancelamento"
    assert result["confidence"] == 0.9411
    assert result["sentiment"] == "NEGATIVE"
    assert result["risk_level"] == "MEDIUM"
    assert result["evidence"] == ["Quero cancelar meu plano"]
    assert result["generative_model"]


def test_analyze_nonexistent_interaction(
    client: TestClient,
) -> None:
    response = client.post(f"/api/v1/interactions/{uuid4()}/analyze")

    assert response.status_code == 404
