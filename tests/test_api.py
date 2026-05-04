import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


def _make_summary(msg_id="abc123"):
    return {
        "id": msg_id,
        "subject": "Test Subject",
        "from": "sender@example.com",
        "date": "Thu, 01 May 2026 10:00:00 +0000",
        "snippet": "Preview text...",
    }


def _make_detail(msg_id="abc123"):
    return {
        "id": msg_id,
        "thread_id": "thread1",
        "subject": "Test Subject",
        "from": "sender@example.com",
        "to": "me@gmail.com",
        "date": "Thu, 01 May 2026 10:00:00 +0000",
        "snippet": "Preview text...",
        "plain_body": "Email body",
        "html_body": "<p>Email body</p>",
        "labels": ["INBOX"],
    }


@pytest.fixture
def mock_client_module():
    """Patch _gmail_client at module level before each test."""
    with patch("api_server._gmail_client") as mock_gc:
        mock_gc.service = MagicMock()
        yield mock_gc


@pytest.fixture
def client(mock_client_module):
    from api_server import app
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_emails(client, mock_client_module):
    mock_client_module.get_email_summaries.return_value = [_make_summary()]
    response = client.get("/emails")
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert data["emails"][0]["id"] == "abc123"


def test_list_emails_with_query(client, mock_client_module):
    mock_client_module.get_email_summaries.return_value = []
    response = client.get("/emails?q=is:unread&max_results=5")
    assert response.status_code == 200
    mock_client_module.get_email_summaries.assert_called_once_with(
        query="is:unread", max_results=5
    )


def test_read_email(client, mock_client_module):
    mock_client_module.get_parsed_email.return_value = _make_detail()
    response = client.get("/emails/abc123")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "abc123"
    assert "plain_body" in data


def test_read_email_not_found(client, mock_client_module):
    mock_client_module.get_parsed_email.return_value = None
    response = client.get("/emails/nonexistent")
    assert response.status_code == 404


def test_list_newsletters(client, mock_client_module):
    mock_client_module.get_email_summaries.return_value = [_make_summary("nl1")]
    response = client.get("/newsletters")
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert data["total"] == 1
