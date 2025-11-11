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

