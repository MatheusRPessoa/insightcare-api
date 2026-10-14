
from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import session_local
from app.main import app
from app.models.interaction import Interaction


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def created_interactions() -> Generator[list[UUID], None, None]:
    interaction_ids: list[UUID] = []

    yield interaction_ids

    if not interaction_ids:
        return

    with session_local() as session:
        session.execute(
            delete(Interaction).where(
                Interaction.id.in_(interaction_ids)
            )
        )
        session.commit()


@pytest.fixture
def create_interaction(client, created_interactions):
    def _create(
        channel: str = "CHAT",
        transcript: str = (
            "Solicitei autorização para meu exame "
            "e ainda não recebi uma resposta."
        ),
    ) -> dict:
        response = client.post(
            "/api/v1/interactions",
            json={
                "channel": channel,
                "transcript": transcript,
            },
        )

        assert response.status_code == 201, response.text

        interaction = response.json()

        created_interactions.append(UUID(interaction["id"]))

        return interaction

    return _create
