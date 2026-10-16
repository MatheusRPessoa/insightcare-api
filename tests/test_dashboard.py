from fastapi.testclient import TestClient


def test_dashboard_summary_structure(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["total_interactions"], int)
    assert isinstance(data["analyzed_interactions"], int)
    assert isinstance(data["pending_interactions"], int)

    assert set(data["risk_distribution"]) == {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert set(data["sentiment_distribution"]) == {
        "POSITIVE",
        "NEUTRAL",
        "NEGATIVE",
    }

    assert isinstance(data["intent_distribution"], dict)


def test_dashboard_summary_counts(
    client: TestClient,
    create_interaction,
) -> None:
    before_response = client.get("/api/v1/dashboard/summary")
    assert before_response.status_code == 200

    before = before_response.json()

    create_interaction(
        transcript=(
            "Preciso verificar o andamento da minha solicitação de atendimento."
        )
    )

    after_response = client.get("/api/v1/dashboard/summary")
    assert after_response.status_code == 200

    after = after_response.json()

    assert after["total_interactions"] == before["total_interactions"] + 1

    assert after["pending_interactions"] == before["pending_interactions"] + 1
