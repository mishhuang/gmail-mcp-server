# Gmail MCP Server

A powerful Model Context Protocol (MCP) server that provides Gmail integration for AI assistants like Claude. Built with FastMCP and the Gmail API, this server enables reading, sending, managing emails, and aggregating newsletters.

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

### Configure Claude Desktop

Add this to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "python",
      "args": [
        "/absolute/path/to/gmail-mcp-server/sse_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/gmail-mcp-server"
      }
    }
  }
}
```

Replace `/absolute/path/to/gmail-mcp-server` with your actual project path.

## Available Tools

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

#### `send_email`
Send a new email.

```python
send_email(
    to: str,                  # Recipient email
    subject: str,             # Email subject
    body: str,                # Email body
    is_html: bool = False     # HTML format
)
```

**Examples:**
- `send_email(to="friend@example.com", subject="Hello", body="Hi there!")`
- `send_email(to="colleague@work.com", subject="Report", body="<h1>Q4 Report</h1>", is_html=True)`

#### `reply_to_email`
Reply to an existing email with proper threading.

```python
reply_to_email(
    message_id: str,          # ID of email to reply to
    body: str,                # Reply content
    is_html: bool = False
)
```

**Example:**
- `reply_to_email(message_id="18f2a3b4c5d6e7f8", body="Thanks for the update!")`

### 🗂️ Email Management

#### `mark_email_read`
Mark an email as read.

```python
mark_email_read(message_id: str)
```

#### `mark_email_unread`
Mark an email as unread.

```python
mark_email_unread(message_id: str)
```

#### `archive_email`
Archive an email (remove from inbox).

```python
archive_email(message_id: str)
```

#### `delete_email`
Move an email to trash (30-day retention).

```python
delete_email(message_id: str)
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
```

## Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# OAuth Settings
OAUTH_PORT=8080                    # Port for OAuth callback

# MCP Server Settings
SSE_PORT=5553                      # MCP server port

# Anthropic API (for client testing)
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL_NAME=claude-sonnet-4-20250514
```

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
        print(f"Error: {e}")
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
        logger.info(f"your_new_tool called with param={param}")
        
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({"error": "Authentication failed"})
        
        result = gmail_client.your_new_method(param)
        return json.dumps({"success": True, "data": result})
        
    except Exception as e:
        logger.error(f"Error in your_new_tool: {e}")
        return json.dumps({"error": str(e)})
```

3. **Test it:**

```bash
python sse_server.py  # Start server
python sse_client.py  # Test with client
```

### Testing

Run the test suite:

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

## Security Considerations

⚠️ **Important Security Notes:**

- Never commit `credentials.json` or `token.json` to version control (they're in `.gitignore`)
- Treat these files like passwords
- OAuth tokens are stored locally only
- Tokens auto-refresh, limiting exposure time
- Scopes limit what the app can access
- Delete `token.json` if compromised and re-authenticate

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Follow existing code style (PEP 8)
5. Add docstrings to all functions
6. Update README.md if needed
7. Submit a pull request

## License

[Add your license here]

## Support

- 🐛 [Report Bugs](https://github.com/mishhuang/gmail-mcp-server/issues)
- 💬 [Discussions](https://github.com/mishhuang/gmail-mcp-server/discussions)
- 📧 Email: [your-email]

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)

---

**Built with ❤️ using FastMCP and Gmail API**

