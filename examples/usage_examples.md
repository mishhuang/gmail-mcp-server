# Gmail MCP Server - Usage Examples

Complete examples for using the Gmail MCP Server with Claude.

## Table of Contents

- [Installation & Setup](#installation--setup)
- [Authentication](#authentication)
- [Email Reading](#email-reading)
- [Email Sending](#email-sending)
- [Email Management](#email-management)
- [Newsletter Aggregation](#newsletter-aggregation)
- [Common Workflows](#common-workflows)

## Installation & Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/mishhuang/gmail-mcp-server.git
cd gmail-mcp-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials as `credentials.json`
6. Place `credentials.json` in the project root

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_key_here
```

## Authentication

### Initial Authentication

```bash
# Run authentication script
python authenticate.py
```

**Expected Output:**

```
============================================================
🔐 Starting OAuth 2.0 Authentication
============================================================

📋 Requested Gmail API Scopes:
   • Read emails
   • Send emails
   • Compose emails
   • Modify emails

🌐 Opening browser for authentication...
   If browser doesn't open, copy the URL from below.

✅ Authentication completed successfully!
✓ Credentials saved to: token.json

🎉 Authentication Successful!
   Gmail API is ready to use.
✅ Successfully authenticated as: your.email@gmail.com
```

### Verify Authentication

```bash
python -c "from src.auth import verify_authentication; verify_authentication()"
```

## Email Reading

### List Recent Emails

**Tool:** `list_emails`

```python
# List 10 most recent emails
list_emails(max_results=10)
```

**Expected Output:**

```json
{
  "status": "success",
  "count": 10,
  "emails": [
    {
      "id": "18c4f3a2b5d6e7f8",
      "subject": "Weekly Newsletter",
      "from": "newsletter@example.com",
      "date": "2024-11-14 10:30:00",
      "snippet": "This week's top stories..."
    }
    // ... 9 more emails
  ]
}
```

### Search for Specific Emails

**Tool:** `search_emails`

```python
# Search for unread emails from a specific sender
search_emails(
    sender="boss@company.com",
    after_date="2024/11/01",
    max_results=20
)

# Search with Gmail query syntax
list_emails(
    query="from:github.com is:unread",
    max_results=15
)
```

**Expected Output:**

```json
{
  "status": "success",
  "query": "from:boss@company.com after:2024/11/01",
  "count": 5,
  "emails": [
    {
      "id": "abc123def456",
      "subject": "Q4 Review",
      "from": "boss@company.com",
      "date": "2024-11-13 14:00:00",
      "snippet": "Let's schedule a meeting..."
    }
  ]
}
```

### Read Full Email Content

**Tool:** `read_email`

```python
# Read email by ID
read_email(message_id="18c4f3a2b5d6e7f8")
```

**Expected Output:**

```json
{
  "status": "success",
  "email": {
    "id": "18c4f3a2b5d6e7f8",
    "subject": "Project Update",
    "from": "colleague@company.com",
    "to": "you@company.com",
    "date": "2024-11-14 09:15:00",
    "plain_body": "Hi,\n\nHere's the latest update...",
    "html_body": "<html><body><p>Hi,</p>...",
    "snippet": "Here's the latest update on the project..."
  }
}
```

## Email Sending

### Send New Email

**Tool:** `send_email`

```python
# Send plain text email
send_email(
    to="recipient@example.com",
    subject="Meeting Follow-up",
    body="Thanks for meeting today. Here are the action items we discussed...",
    is_html=False
)

# Send HTML email
send_email(
    to="team@company.com",
    subject="Weekly Report",
    body="""
    <html>
      <body>
        <h1>Weekly Report</h1>
        <p>Here are this week's highlights:</p>
        <ul>
          <li>Completed feature X</li>
          <li>Fixed bug Y</li>
        </ul>
      </body>
    </html>
    """,
    is_html=True
)
```

**Expected Output:**

```json
{
  "status": "success",
  "message": "Email sent successfully",
  "message_id": "xyz789abc123",
  "to": "recipient@example.com",
  "subject": "Meeting Follow-up"
}
```

### Reply to Email

**Tool:** `reply_to_email`

```python
# Reply to an email
reply_to_email(
    message_id="18c4f3a2b5d6e7f8",
    body="Thanks for reaching out! I'll get back to you by tomorrow.",
    is_html=False
)
```

**Expected Output:**

```json
{
  "status": "success",
  "message": "Reply sent successfully",
  "message_id": "def456ghi789",
  "original_subject": "Question about project",
  "reply_subject": "Re: Question about project"
}
```

## Email Management

### Mark as Read/Unread

**Tools:** `mark_email_read`, `mark_email_unread`

```python
# Mark email as read
mark_email_read(message_id="18c4f3a2b5d6e7f8")

# Mark email as unread
mark_email_unread(message_id="18c4f3a2b5d6e7f8")
```

**Expected Output:**

```json
{
  "status": "success",
  "action": "marked_read",
  "message_id": "18c4f3a2b5d6e7f8"
}
```

### Archive Email

**Tool:** `archive_email`

```python
# Archive email (remove from inbox)
archive_email(message_id="18c4f3a2b5d6e7f8")
```

**Expected Output:**

```json
{
  "status": "success",
  "action": "archived",
  "message_id": "18c4f3a2b5d6e7f8",
  "message": "Email archived successfully"
}
```

### Delete Email

**Tool:** `delete_email`

```python
# Move email to trash
delete_email(message_id="18c4f3a2b5d6e7f8")
```

**Expected Output:**

```json
{
  "status": "success",
  "action": "deleted",
  "message_id": "18c4f3a2b5d6e7f8",
  "message": "Email moved to trash"
}
```

## Newsletter Aggregation

### Fetch Newsletters

**Tool:** `fetch_newsletters`

```python
# Fetch newsletters from last 36 hours (default)
fetch_newsletters()

# Fetch newsletters from last 24 hours
fetch_newsletters(hours_back=24)

# Fetch from specific senders
fetch_newsletters(
    hours_back=48,
    sender_emails="newsletter1@example.com,newsletter2@example.com"
)
```

**Expected Output:**

```json
{
  "status": "success",
  "date_range": "2024-11-12 to 2024-11-14",
  "hours_back": 36,
  "total_emails": 8,
  "newsletters_by_sender": {
    "hello@bensbites.beehiiv.com": [
      {
        "id": "abc123",
        "subject": "Ben's Bites #234",
        "date": "2024-11-14 08:00:00",
        "sender_name": "Ben's Bites",
        "content": "🔥 OpenAI releases new model...\n\n📰 Top Stories:\n..."
      }
    ],
    "newsletter@theneurondaily.com": [
      {
        "id": "def456",
        "subject": "The Neuron Daily - Nov 14",
        "date": "2024-11-14 07:30:00",
        "sender_name": "The Neuron",
        "content": "Good morning! Here's what's new in AI...\n..."
      }
    ]
  }
}
```

## Common Workflows

### Daily Newsletter Digest

**Scenario:** Every morning, aggregate AI newsletters from the past day and have Claude summarize them.

```python
# Step 1: Fetch newsletters
newsletters = fetch_newsletters(hours_back=24)

# Step 2: Ask Claude to summarize (automatically done via MCP)
# "Can you summarize today's AI newsletters for me?"
```

**Claude's Response:**

```markdown
# Daily AI Newsletter Summary - Nov 14, 2024

## 🔥 Top Stories

1. **OpenAI Model Release** (Ben's Bites)
   - New GPT model with improved reasoning
   - 40% faster inference
   - Launch: next week

2. **Google AI Updates** (The Neuron)
   - Gemini 2.0 preview available
   - Enhanced multimodal capabilities
   
... (continues with organized summary)
```

### Inbox Cleanup

**Scenario:** Find and archive all read promotional emails older than 7 days.

```python
# Step 1: Search for emails
emails = list_emails(
    query="is:read category:promotions older_than:7d",
    max_results=100
)

# Step 2: Archive each email
# (Claude can iterate through and archive them)
for email in emails:
    archive_email(message_id=email['id'])
```

### Auto-Reply to Meeting Requests

**Scenario:** Find meeting requests and send polite replies.

```python
# Step 1: Search for meeting requests
emails = list_emails(
    query="subject:(meeting OR schedule) is:unread",
    max_results=10
)

# Step 2: For each email, send appropriate reply
# Claude analyzes each email and decides on response
for email in emails:
    email_content = read_email(message_id=email['id'])
    # Claude generates contextual reply
    reply_to_email(
        message_id=email['id'],
        body="Thank you for reaching out! I'd be happy to meet..."
    )
    mark_email_read(message_id=email['id'])
```

### Weekly Email Summary Report

**Scenario:** Generate a weekly summary of important emails.

```python
# Fetch all emails from the past week
emails = list_emails(
    query="after:2024/11/07 -category:promotions -category:social",
    max_results=50
)

# Claude analyzes and creates summary report:
# - Most important emails
# - Action items
# - Follow-ups needed
# - Statistics (emails received, by category, etc.)
```

### Newsletter Research Compilation

**Scenario:** Research a specific topic across multiple newsletters.

```python
# Step 1: Fetch recent newsletters
newsletters = fetch_newsletters(hours_back=168)  # Last week

# Step 2: Ask Claude to extract specific information
# "From these newsletters, compile all mentions of 'multimodal AI' 
#  with summaries and links"
```

## Tips & Best Practices

### Efficient API Usage

1. **Use specific queries** to reduce API calls:
   ```python
   # Good: Specific query
   list_emails(query="from:sender@example.com after:2024/11/01", max_results=10)
   
   # Avoid: Fetching everything then filtering
   list_emails(max_results=1000)  # Too broad
   ```

2. **Batch operations** when possible:
   ```python
   # Get email IDs first, then process
   emails = list_emails(query="is:read older_than:7d", max_results=50)
   for email in emails:
       archive_email(message_id=email['id'])
   ```

3. **Newsletter timing**: Run once per day (morning) for best results
   ```python
   # Optimal: Daily at 9 AM
   fetch_newsletters(hours_back=30)  # Slight overlap to catch stragglers
   ```

### Error Handling

The server automatically handles common errors:

- **Rate limits**: Automatic retry with exponential backoff
- **Invalid message IDs**: Clear error messages
- **Authentication issues**: Prompts for re-authentication
- **Network errors**: Retries transient failures

### Gmail Search Syntax

Powerful queries for `list_emails`:

```python
# Unread emails from last week
"is:unread newer_than:7d"

# Important emails not in spam
"is:important -in:spam"

# Emails with attachments
"has:attachment"

# Emails in specific date range
"after:2024/11/01 before:2024/11/14"

# Multiple conditions
"from:boss@company.com has:attachment is:unread"

# Exclude categories
"-category:promotions -category:social"
```

## Troubleshooting

### "Authentication failed"

```bash
# Re-run authentication
python authenticate.py
```

### "Message ID not found"

- Message may have been deleted
- Verify message ID is correct
- Check if you have access to the email

### "Rate limit exceeded"

- Wait a few seconds and retry
- Server automatically handles rate limits
- Consider reducing `max_results` in queries

### Newsletter not appearing

- Check sender email address is correct
- Verify time range (increase `hours_back`)
- Email might be in spam or other folder

## Support

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/mishhuang/gmail-mcp-server/issues)
- 💬 [Discussions](https://github.com/mishhuang/gmail-mcp-server/discussions)

