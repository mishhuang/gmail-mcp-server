"""Configuration management for Gmail MCP Server."""

import os
from pathlib import Path
from typing import List

# Base directory
BASE_DIR = Path(__file__).parent.parent

# OAuth 2.0 credentials and token files
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# Gmail API scopes
# If modifying these scopes, delete the token.json file
GMAIL_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

# OAuth callback configuration
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "8080"))
OAUTH_REDIRECT_URI = f"http://localhost:{OAUTH_PORT}/"

# Server configuration
SERVER_NAME = "gmail-mcp-server"
SSE_PORT = int(os.getenv("SSE_PORT", "5553"))

# Newsletter configuration
DEFAULT_NEWSLETTER_HOURS = 36
# Keep newsletter tool responses small enough for LLM context (many senders × many messages).
NEWSLETTER_MAX_RESULTS_PER_SENDER = 5
NEWSLETTER_MAX_BODY_CHARS = 5000

# read_email returns can be huge (HTML newsletters); cap before JSON to avoid 200k+ token prompts.
READ_EMAIL_PLAIN_MAX_CHARS = 32000
READ_EMAIL_HTML_MAX_CHARS = 16000


def truncate_for_tool(text: str, max_chars: int, field_name: str = "content") -> str:
    """Shorten a string for MCP tool JSON so clients stay within model context limits."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return (
        text[:max_chars]
        + f"\n\n... [{field_name} truncated; original length {len(text)} characters]"
    )

