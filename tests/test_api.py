import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import here so patching happens before module-level init
    with patch("api_server._gmail_client") as mock_gc:
        mock_gc.service = MagicMock()
        from api_server import app
        return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
