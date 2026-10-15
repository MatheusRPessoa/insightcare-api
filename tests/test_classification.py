from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient


def test_classify_interaction(
    client: TestClient,
    create_interaction,
) -> None:
    interaction = create_interaction(
        transcript="Quero cancelar meu plano de saúde."
    )

    response = client.post(
        f"/api/v1/interactions/{interaction['id']}/classify"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["interaction_id"] == interaction["id"]
    assert data["intent"] == "cancelamento"
    assert 0 <= data["confidence"] <= 1
    assert data["model"] == "tfidf-logistic-regression"


def test_classify_nonexistent_interaction(
    client: TestClient,
) -> None:
    response = client.post(
        f"/api/v1/interactions/{uuid4()}/classify"
    )

    assert response.status_code == 404


def test_classify_model_unavailable(
    client: TestClient,
    create_interaction,
) -> None:
    interaction = create_interaction()

    with patch(
        "app.services.ml_classifier.load_classifier",
        side_effect=FileNotFoundError,
    ):
        response = client.post(
            f"/api/v1/interactions/{interaction['id']}/classify"
        )


    assert response.status_code == 503
