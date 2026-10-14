
from uuid import UUID, uuid4

from fastapi.testclient import TestClient


def test_create_interaction(create_interaction) -> None:
    interaction = create_interaction()

    assert UUID(interaction["id"])
    assert interaction["channel"] == "CHAT"
    assert interaction["status"] == "PENDING"
    assert interaction["protocol"]
    assert interaction["created_at"]
    assert interaction["updated_at"]


def test_list_interactions(
    client: TestClient,
    create_interaction,
) -> None:
    interaction = create_interaction()

    response = client.get("/api/v1/interactions")

    assert response.status_code == 200
    assert any(
        item["id"] == interaction["id"]
        for item in response.json()
    )


def test_get_interaction(
    client: TestClient,
    create_interaction,
) -> None:
    interaction = create_interaction()

    response = client.get(
        f"/api/v1/interactions/{interaction['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == interaction["id"]


def test_get_nonexistent_interaction(
    client: TestClient,
) -> None:
    interaction_id = uuid4()

    response = client.get(
        f"/api/v1/interactions/{interaction_id}"
    )

    assert response.status_code == 404


def test_delete_interaction(
    client: TestClient,
    create_interaction,
) -> None:
    interaction = create_interaction()

    response = client.delete(
        f"/api/v1/interactions/{interaction['id']}"
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/interactions/{interaction['id']}"
    )

    assert get_response.status_code == 404


def test_reject_short_transcript(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/interactions",
        json={
            "channel": "CHAT",
            "transcript": "Oi",
        },
    )

    assert response.status_code == 422


def test_reject_invalid_channel(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/interactions",
        json={
            "channel": "WHATSAPP",
            "transcript": "Preciso de ajuda para autorizar um exame.",
        },
    )

    assert response.status_code == 422


def test_generate_unique_protocols(
    create_interaction,
) -> None:
    first = create_interaction()
    second = create_interaction()

    assert first["protocol"]
    assert second["protocol"]
    assert first["protocol"] != second["protocol"]
