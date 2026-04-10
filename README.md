# Gmail MCP Server

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

A powerful Model Context Protocol (MCP) server that provides Gmail integration for AI assistants like Claude. Built with FastMCP and the Gmail API, this server enables reading, sending, managing emails, and aggregating newsletters.

## Quick Start

```bash
# Clone and install
git clone https://github.com/mishhuang/gmail-mcp-server.git
cd gmail-mcp-server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Authenticate
python authenticate.py

# Start server
python sse_server.py
```

## Features

🔐 **Complete OAuth 2.0 Authentication**
- Browser-based OAuth flow with automatic token refresh
- Secure credential storage with token.json
- Standalone authentication script for easy setup

📧 **Email Operations**
- **Read**: List, search, and read full email content
- **Write**: Send emails and reply to threads with proper threading
- **Manage**: Mark as read/unread, archive, delete
- **Search**: Advanced Gmail search queries with filters

📰 **Newsletter Aggregation**
- Fetch and organize newsletters from multiple senders
- Pre-configured for popular AI/tech newsletters
- HTML content cleaning and formatting
- Ready for LLM summarization

🛠️ **Robust Error Handling**
- Custom exception classes for different error types
- Comprehensive input validation
- Logging for debugging
- User-friendly error messages

## Disclaimer

This project is provided as-is for personal and educational use. Email operations (sending, deleting, archiving) are irreversible or difficult to undo. The author is not responsible for any unintended emails sent, data loss, or other consequences. The server starts in **read-only mode** by default — write operations must be explicitly enabled. Always test with a non-critical email account first.

## Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **Google Cloud Project** with Gmail API enabled
- **OAuth 2.0 credentials** (Desktop app) from Google Cloud Console
- **Anthropic API key** (optional, for testing with the included client)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mishhuang/gmail-mcp-server.git
cd gmail-mcp-server
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Credentials

#### Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to **"APIs & Services"** > **"Library"**
   - Search for **"Gmail API"**
   - Click **"Enable"**

#### Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** > **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - Choose **"External"** user type
   - Fill in required fields (app name, user support email)
   - Add your email as a test user
   - Save and continue through the steps
4. Back at Create OAuth client ID:
   - Choose **"Desktop app"** as application type
   - Give it a name (e.g., "Gmail MCP Server")
   - Click **"Create"**
5. Download the credentials:
   - Click the **download button (⬇️)** next to your OAuth client
   - Save as `credentials.json` in the project root

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key (optional, for client testing)
# ANTHROPIC_API_KEY=your_api_key_here
```

### 6. Authenticate with Gmail

Run the standalone authentication script:

```bash
python authenticate.py
```

This will:
- Check for `credentials.json`
- Open your browser for Google authorization
- Save the token to `token.json`
- Verify authentication worked

**Important:** You only need to run this once. The token will be saved and automatically refreshed.

## Usage

### Starting the MCP Server

```bash
python sse_server.py
```

The server will start on `http://localhost:5553/sse`

### Configure an MCP Client

The server exposes an SSE endpoint at `http://localhost:5553/sse`. Point any
MCP-compatible client at that URL. For example, in Claude Desktop:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gmail": {
      "url": "http://localhost:5553/sse"
    }
  }
}
```

> **Note:** Start the server (`python sse_server.py`) before launching the client.

## Available Tools

### 🔧 Diagnostics

#### `test_connection`
Verify the MCP server is running.

#### `test_gmail_auth`
Test Gmail API authentication and display the connected email address.

### 📬 Email Reading

#### `list_emails`
List emails from your inbox with optional filtering.

```python
list_emails(
    query: str = "",           # Gmail search query
    max_results: int = 10      # Max number of emails (1-500)
)
```

**Examples:**
- `list_emails()` - Get 10 most recent emails
- `list_emails(query="is:unread")` - Get unread emails
- `list_emails(query="from:boss@company.com", max_results=5)`

#### `read_email`
Read full email content including body.

```python
read_email(
    message_id: str           # Gmail message ID from list_emails
)
```

**Example:**
- `read_email(message_id="18f2a3b4c5d6e7f8")`

#### `search_emails`
Search for emails from a specific sender.

```python
search_emails(
    sender: str,              # Email address
    after_date: str = "",     # Date in YYYY/MM/DD format
    max_results: int = 10
)
```

**Examples:**
- `search_emails(sender="newsletter@example.com")`
- `search_emails(sender="boss@company.com", after_date="2024/11/01")`

### ✉️ Email Sending

> All write tools require `ALLOW_WRITE=true` in `.env` and a two-step confirmation (see [Configuration](#configuration)).

#### `send_email`
Send a new email.

```python
send_email(
    to: str,                  # Recipient email
    subject: str,             # Email subject
    body: str,                # Email body
    is_html: bool = False,    # HTML format
    confirm: bool = False     # Must be true to execute
)
```

**Examples:**
- `send_email(to="friend@example.com", subject="Hello", body="Hi there!", confirm=true)`

#### `reply_to_email`
Reply to an existing email with proper threading.

```python
reply_to_email(
    message_id: str,          # ID of email to reply to
    body: str,                # Reply content
    is_html: bool = False,
    confirm: bool = False     # Must be true to execute
)
```

**Example:**
- `reply_to_email(message_id="18f2a3b4c5d6e7f8", body="Thanks!", confirm=true)`

### 🗂️ Email Management

#### `mark_email_read`
Mark an email as read.

```python
mark_email_read(message_id: str, confirm: bool = False)
```

#### `mark_email_unread`
Mark an email as unread.

```python
mark_email_unread(message_id: str, confirm: bool = False)
```

#### `archive_email`
Archive an email thread (removes the entire conversation from inbox, keeps in All Mail).

```python
archive_email(message_id: str, confirm: bool = False)
```

#### `delete_email`
Trash an email thread (moves the entire conversation to trash, recoverable for ~30 days).

```python
delete_email(message_id: str, confirm: bool = False)
```

### 📰 Newsletter Aggregation

#### `fetch_newsletters`
Fetch and organize newsletter emails for summarization.

```python
fetch_newsletters(
    hours_back: int = 36,           # Hours to look back
    sender_emails: str = ""         # Comma-separated custom senders
)
```

**Default Newsletters:**
- Ben's Bites
- The Neuron
- The Rundown AI
- Last Week in AI
- Alpha Signal

**Examples:**
- `fetch_newsletters()` - Get default newsletters from past 36 hours
- `fetch_newsletters(hours_back=24)` - Last 24 hours
- `fetch_newsletters(sender_emails="custom@newsletter.com")`

**Usage Workflow:**
1. Call `fetch_newsletters()` to get organized newsletter content
2. Pass the JSON output to Claude with a prompt like:
   ```
   "Please summarize the key points from these AI newsletters, 
   organized by topic. Highlight any breaking news or major 
   announcements."
   ```
3. Claude will generate a structured summary

**Customizing Newsletter Sources:**

Edit `src/newsletter.py` to add your own newsletter senders:

```python
NEWSLETTER_SENDERS = {
    'your_newsletter': 'newsletter@example.com',
    # ... add more
}

NEWSLETTER_DISPLAY_NAMES = {
    'your_newsletter': 'Your Newsletter',
    # ... add more
}
```

## Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# OAuth Settings
OAUTH_PORT=8080                    # Port for OAuth callback

# MCP Server Settings
SSE_PORT=5553                      # MCP server port

# Write mode — server is read-only by default
# Set to true to enable send, reply, delete, archive, and mark read/unread
ALLOW_WRITE=false

# Anthropic API (for client testing)
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL_NAME=claude-sonnet-4-5-20250929
```

**Write mode:** When `ALLOW_WRITE=true`, write tools still require a two-step confirmation. The first call returns a warning describing the action; calling again with `confirm=true` executes it. This prevents LLMs from accidentally firing off emails or deletes in a single turn.

### Gmail API Scopes

The server requests these Gmail API scopes (configured in `src/config.py`):

- `gmail.readonly` - Read emails and settings
- `gmail.send` - Send emails
- `gmail.compose` - Create and send drafts
- `gmail.modify` - Modify labels and read/unread status

**Note:** If you change scopes, delete `token.json` and re-authenticate.

## Gmail API Quotas

Gmail API has usage quotas to prevent abuse:

- **Per-user rate limit:** 250 quota units/second
- **Daily quota:** 1 billion units
- **Most operations:** 5-10 quota units each

**Common Operation Costs:**
- `users.getProfile`: 1 unit
- `users.messages.list`: 5 units
- `users.messages.get`: 5 units
- `users.messages.send`: 100 units
- `users.messages.modify`: 5 units

See: [Gmail API Usage Limits](https://developers.google.com/gmail/api/reference/quota)

## Troubleshooting

### Authentication Errors

**"Credentials file not found"**
- Ensure `credentials.json` is in the project root
- Verify you downloaded OAuth 2.0 credentials (Desktop app), not API key

**"Authentication failed"**
- Delete `token.json` and run `python authenticate.py` again
- Verify Gmail API is enabled in Google Cloud Console
- Check OAuth consent screen is configured
- Ensure your email is added as a test user

**"Token refresh failed"**
- Refresh tokens expire if unused for 6 months
- Delete `token.json` and re-authenticate
- Check if OAuth client was deleted in Cloud Console

### Port Conflicts

**"Port already in use"**
- Change `OAUTH_PORT` in `.env` to a different port (e.g., 8081)
- Update authorized redirect URIs in Google Cloud Console
- Check what's using the port: `lsof -i :8080`

### API Errors

**"Quota exceeded"**
- You've hit the daily API limit
- Wait until quota resets (midnight Pacific Time)
- Reduce the number of API calls

**"Permission denied (403)"**
- Required scope not granted
- Delete `token.json` and re-authenticate
- Check Gmail API is enabled

**"Not found (404)"**
- Message ID doesn't exist or was deleted
- Verify the message ID is correct

### Server Issues

**Server won't start**
- Check port 5553 is available: `lsof -i :5553`
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check for Python errors in terminal output

**Tools not working**
- Ensure authenticated: run `python authenticate.py`
- Check `token.json` exists
- Verify credentials.json is valid JSON

## Development

### Project Structure

```
gmail-mcp-server/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── auth.py               # OAuth 2.0 authentication
│   ├── config.py             # Configuration constants
│   ├── gmail_client.py       # Gmail API client wrapper
│   ├── newsletter.py         # Newsletter aggregation
│   ├── exceptions.py         # Custom exception classes
│   └── validation.py         # Input validation utilities
├── sse_server.py             # Main MCP server with tools
├── sse_client.py             # Example client for testing
├── authenticate.py           # Standalone auth script
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment config
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Adding New Tools

1. **Implement in `src/gmail_client.py`:**

```python
def your_new_method(self, param: str) -> Optional[Dict]:
    """Your method docstring."""
    if not self.service:
        raise RuntimeError("Not authenticated")
    
    try:
        result = self.service.users().someOperation(...).execute()
        return result
    except HttpError as e:
        logger.error("Gmail API error: %s", e)
        return None
```

2. **Add tool in `sse_server.py`:**

```python
@mcp.tool()
def your_new_tool(param: str) -> str:
    """
    Your tool description.
    
    Args:
        param: Parameter description
    
    Returns:
        str: JSON string with results
    """
    try:
        logger.info("your_new_tool called with param=%s", param)
        
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({"error": "Authentication failed"})
        
        result = gmail_client.your_new_method(param)
        return json.dumps({"success": True, "data": result})
        
    except Exception as e:
        logger.error("Error in your_new_tool: %s", e)
        return json.dumps({"error": str(e)})
```

3. **Test it:**

```bash
python sse_server.py  # Start server
python sse_client.py  # Test with client
```

### Testing

Verify authentication works:

```bash
python -c "from src.auth import verify_authentication; verify_authentication()"
```

Test individual components:

```bash
# Test validation
python -c "from src.validation import validate_email; validate_email('test@example.com')"

# Test newsletter fetching
python -c "from src.newsletter import calculate_date_filter; print(calculate_date_filter(36))"
```

## Performance & Best Practices

### Optimization Tips

1. **Newsletter Aggregation:**
   - Run once daily (morning) to aggregate last 24-36 hours
   - Process newsletters in batches during off-peak hours
   - Use specific sender filters to reduce API calls

2. **Email Reading:**
   - Use `max_results` parameter to limit fetches
   - Apply specific search queries to narrow results
   - Request only needed fields when possible

3. **Rate Limiting:**
   - Errors are logged for troubleshooting
   - Consider spacing out large batch operations

4. **Authentication:**
   - Tokens are cached and automatically refreshed
   - Re-authentication only needed if token.json is deleted
   - No manual intervention required for token expiry

### Example Workflow

**Daily Newsletter Digest:**
```python
# Run this once per morning
newsletters = fetch_newsletters(hours_back=36)
# Send to Claude for summarization
# Typically uses ~50-100 API units
```

**Email Management:**
```python
# Efficient inbox cleanup
emails = list_emails(query="is:unread older_than:7d", max_results=50)
# Process and archive in batches
```

## Security Considerations

⚠️ **Important Security Notes:**

- Never commit `credentials.json` or `token.json` to version control (they're in `.gitignore`)
- Treat these files like passwords
- OAuth tokens are stored locally only
- Tokens auto-refresh, limiting exposure time
- Scopes limit what the app can access
- Delete `token.json` if compromised and re-authenticate

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)

---

**Built with ❤️ using FastMCP and Gmail API**

