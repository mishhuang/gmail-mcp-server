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


def test_digest_no_newsletters(client, mock_client_module):
    """Returns 404 when no newsletters found in time range."""
    with patch("api_server.fetch_newsletters_func") as mock_fetch:
        mock_fetch.return_value = {
            "total_emails": 0,
            "newsletters_by_sender": {},
            "date_range": "2026-04-30 to 2026-05-01",
            "hours_back": 24,
        }
        response = client.post("/newsletters/digest", json={"hours_back": 24})
    assert response.status_code == 404


def test_digest_missing_api_key(client, mock_client_module):
    """Returns 503 when ANTHROPIC_API_KEY is not set."""
    with patch("api_server.fetch_newsletters_func") as mock_fetch:
        mock_fetch.return_value = {
            "total_emails": 1,
            "newsletters_by_sender": {"a@b.com": [{"subject": "S", "content": "C", "date": "D", "id": "1"}]},
            "date_range": "2026-04-30 to 2026-05-01",
            "hours_back": 24,
        }
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            response = client.post("/newsletters/digest", json={"hours_back": 24})
    assert response.status_code == 503


def test_write_endpoints_blocked_when_disabled(client, mock_client_module):
    """All write endpoints return 403 when ALLOW_WRITE is false."""
    with patch("api_server.ALLOW_WRITE", False):
        assert client.put("/emails/abc/read").status_code == 403
        assert client.put("/emails/abc/unread").status_code == 403
        assert client.post("/emails/abc/archive").status_code == 403
        assert client.post("/emails/abc/delete").status_code == 403


def test_mark_read(client, mock_client_module):
    mock_client_module.mark_as_read.return_value = {"id": "abc"}
    with patch("api_server.ALLOW_WRITE", True):
        response = client.put("/emails/abc/read")
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_mark_unread(client, mock_client_module):
    mock_client_module.mark_as_unread.return_value = {"id": "abc"}
    with patch("api_server.ALLOW_WRITE", True):
        response = client.put("/emails/abc/unread")
    assert response.status_code == 200


def test_archive(client, mock_client_module):
    mock_client_module.archive_email.return_value = {"id": "abc"}
    with patch("api_server.ALLOW_WRITE", True):
        response = client.post("/emails/abc/archive")
    assert response.status_code == 200


def test_delete(client, mock_client_module):
    mock_client_module.delete_email.return_value = {"id": "abc"}
    with patch("api_server.ALLOW_WRITE", True):
        response = client.post("/emails/abc/delete")
    assert response.status_code == 200
