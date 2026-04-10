"""
Gmail MCP Server
A FastMCP server for Gmail integration using the Gmail API.
"""

import json
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from src.config import (
    SERVER_NAME,
    SSE_PORT,
    ALLOW_WRITE,
    READ_EMAIL_HTML_MAX_CHARS,
    READ_EMAIL_PLAIN_MAX_CHARS,
    truncate_for_tool,
)
from src.gmail_client import GmailClient
from src.newsletter import fetch_newsletters as fetch_newsletters_func, get_sender_name
from src.validation import validate_hours_back
from src.exceptions import ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize MCP server with port configuration
mcp = FastMCP(SERVER_NAME, port=SSE_PORT)

# Initialize Gmail client (will be used by tools)
gmail_client = GmailClient()

WRITE_DISABLED_MSG = "Write operations are disabled. Set ALLOW_WRITE=true in .env to enable."


def _write_gate(confirm: bool, action: str, description: str) -> str | None:
    """Return a JSON error/warning string if the write should not proceed, or None to continue."""
    if not ALLOW_WRITE:
        return json.dumps({"error": WRITE_DISABLED_MSG})
    if not confirm:
        return json.dumps({
            "warning": description,
            "action": action,
            "requires_confirmation": True,
        })
    return None


#### Tools ####

@mcp.tool()
def test_connection() -> str:
    """
    Test that the MCP server is running.
    
    Returns:
        str: Success message confirming server is operational.
    """
    return "Gmail MCP Server is running!"


@mcp.tool()
def test_gmail_auth() -> str:
    """
    Test Gmail API authentication.
    
    Returns:
        str: Success message if authentication works, error message otherwise.
    """
    try:
        if gmail_client.authenticate():
            profile = gmail_client.get_profile()
            if profile:
                email = profile.get('emailAddress', 'Unknown')
                total_messages = profile.get('messagesTotal', 0)
                return f"Successfully authenticated! Email: {email}, Total messages: {total_messages}"
            else:
                return "Authentication succeeded but failed to retrieve profile."
        else:
            return "Authentication failed. Check credentials.json file."
    except Exception as e:
        return f"Error during authentication: {str(e)}"


@mcp.tool()
def list_emails(query: str = "", max_results: int = 10) -> str:
    """
    List emails from Gmail inbox.
    
    Args:
        query: Gmail search query (e.g., "from:sender@example.com", "is:unread", "after:2024/11/01")
        max_results: Maximum number of emails to return (default: 10)
    
    Returns:
        str: JSON string with array of email summaries containing id, subject, from, date, and snippet
    
    Examples:
        - list_emails() - Get 10 most recent emails
        - list_emails(query="is:unread") - Get unread emails
        - list_emails(query="from:example@gmail.com", max_results=5) - Get 5 emails from sender
    """
    try:
        # Ensure authenticated
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        # Get email summaries
        summaries = gmail_client.get_email_summaries(query=query, max_results=max_results)
        
        if not summaries:
            return json.dumps({
                "message": "No emails found matching the query",
                "query": query,
                "count": 0
            })
        
        return json.dumps({
            "count": len(summaries),
            "query": query,
            "emails": summaries
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to list emails: {str(e)}"
        })


@mcp.tool()
def read_email(message_id: str) -> str:
    """
    Read full email content by message ID.
    
    Args:
        message_id: Gmail message ID (obtained from list_emails)
    
    Returns:
        str: JSON string with full email details including subject, from, to, date, plain_body, and html_body
    
    Example:
        - read_email(message_id="18f2a3b4c5d6e7f8") - Read full email content
    """
    try:
        # Ensure authenticated
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        # Get parsed email
        email_data = gmail_client.get_parsed_email(message_id)
        
        if not email_data:
            return json.dumps({
                "error": f"Email not found with ID: {message_id}"
            })

        email_data["plain_body"] = truncate_for_tool(
            email_data.get("plain_body") or "",
            READ_EMAIL_PLAIN_MAX_CHARS,
            "plain_body",
        )
        email_data["html_body"] = truncate_for_tool(
            email_data.get("html_body") or "",
            READ_EMAIL_HTML_MAX_CHARS,
            "html_body",
        )

        return json.dumps(email_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to read email: {str(e)}"
        })


@mcp.tool()
def search_emails(sender: str, after_date: str = "", max_results: int = 10) -> str:
    """
    Search for emails from a specific sender, optionally after a certain date.
    
    Args:
        sender: Email address to search for (e.g., "user@example.com")
        after_date: Date in YYYY/MM/DD format (optional, e.g., "2024/11/01")
        max_results: Maximum number of emails to return (default: 10)
    
    Returns:
        str: JSON string with filtered list of emails from the specified sender
    
    Examples:
        - search_emails(sender="boss@company.com") - Get emails from sender
        - search_emails(sender="boss@company.com", after_date="2024/11/01") - Get recent emails from sender
    """
    try:
        # Ensure authenticated
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        # Validate sender email format (basic check)
        if '@' not in sender:
            return json.dumps({
                "error": f"Invalid email address format: {sender}"
            })
        
        # Search emails
        results = gmail_client.search_emails_from_sender(
            sender=sender,
            after_date=after_date,
            max_results=max_results
        )
        
        if not results:
            date_str = f" after {after_date}" if after_date else ""
            return json.dumps({
                "message": f"No emails found from {sender}{date_str}",
                "sender": sender,
                "after_date": after_date,
                "count": 0
            })
        
        return json.dumps({
            "count": len(results),
            "sender": sender,
            "after_date": after_date,
            "emails": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to search emails: {str(e)}"
        })


@mcp.tool()
def send_email(to: str, subject: str, body: str, is_html: bool = False, confirm: bool = False) -> str:
    """
    Send an email via Gmail. Requires ALLOW_WRITE=true in .env.
    First call returns a confirmation prompt; call again with confirm=true to send.
    
    Args:
        to: Recipient email address (e.g., "recipient@example.com")
        subject: Email subject line
        body: Email body content
        is_html: Whether body is HTML format (default: False for plain text)
        confirm: Set to true to confirm and execute the send
    
    Returns:
        str: JSON string with confirmation and message ID
    
    Examples:
        - send_email(to="friend@example.com", subject="Hello", body="Hi there!", confirm=true)
    """
    gate = _write_gate(confirm, "send_email", f'About to send email to {to} with subject "{subject}". Call again with confirm=true to proceed.')
    if gate:
        return gate

    try:
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        result = gmail_client.send_email(
            to=to,
            subject=subject,
            body=body,
            is_html=is_html
        )
        
        if not result:
            return json.dumps({
                "error": "Failed to send email. Check recipient address and try again."
            })
        
        return json.dumps({
            "success": True,
            "message": "Email sent successfully",
            "message_id": result.get('id'),
            "thread_id": result.get('threadId'),
            "to": to,
            "subject": subject
        }, indent=2)
        
    except ValueError as e:
        return json.dumps({
            "error": f"Invalid input: {str(e)}"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to send email: {str(e)}"
        })


@mcp.tool()
def reply_to_email(message_id: str, body: str, is_html: bool = False, confirm: bool = False) -> str:
    """
    Reply to an existing email message. Requires ALLOW_WRITE=true in .env.
    First call returns a confirmation prompt; call again with confirm=true to send.
    
    Args:
        message_id: ID of the email to reply to (obtained from list_emails or read_email)
        body: Reply message content
        is_html: Whether body is HTML format (default: False for plain text)
        confirm: Set to true to confirm and execute the reply
    
    Returns:
        str: JSON string with confirmation and reply message ID
    
    Examples:
        - reply_to_email(message_id="18f2a3b4c5d6e7f8", body="Thanks!", confirm=true)
    
    Notes:
        - Automatically adds "Re: " to subject if not already present
        - Sets proper In-Reply-To and References headers for threading
        - Replies to the original sender
    """
    gate = _write_gate(confirm, "reply_to_email", f"About to reply to message {message_id}. Call again with confirm=true to proceed.")
    if gate:
        return gate

    try:
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        result = gmail_client.reply_to_email(
            message_id=message_id,
            body=body,
            is_html=is_html
        )
        
        if not result:
            return json.dumps({
                "error": f"Failed to send reply. Check message ID: {message_id}"
            })
        
        return json.dumps({
            "success": True,
            "message": "Reply sent successfully",
            "message_id": result.get('id'),
            "thread_id": result.get('threadId'),
            "in_reply_to": message_id
        }, indent=2)
        
    except ValueError as e:
        return json.dumps({
            "error": f"Invalid input: {str(e)}"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to send reply: {str(e)}"
        })


@mcp.tool()
def fetch_newsletters(hours_back: int = 36, sender_emails: str = "") -> str:
    """
    Fetch and organize newsletter emails from the past N hours.
    
    This tool aggregates emails from AI/tech newsletters for easy summarization.
    Default newsletters include: Ben's Bites, The Neuron, The Rundown AI, 
    Last Week in AI, and Alpha Signal.
    
    Args:
        hours_back: How many hours back to search (default: 36)
        sender_emails: Comma-separated email addresses to override defaults (optional)
                      Example: "sender1@example.com,sender2@example.com"
    
    Returns:
        str: JSON string with structure:
        {
            "date_range": "YYYY-MM-DD to YYYY-MM-DD",
            "hours_back": int,
            "total_emails": int,
            "newsletters_by_sender": {
                "sender@example.com": [
                    {
                        "id": "message_id",
                        "subject": "subject line",
                        "date": "date string",
                        "content": "cleaned email content"
                    }
                ]
            }
        }
    
    Examples:
        - fetch_newsletters() - Get default newsletters from past 36 hours
        - fetch_newsletters(hours_back=24) - Get newsletters from past 24 hours
        - fetch_newsletters(sender_emails="custom@newsletter.com") - Custom sender
    
    Usage Tips:
        - Use the returned content with an LLM to generate daily summaries
        - Adjust hours_back to match your reading schedule (24h, 48h, etc.)
        - Content is pre-cleaned with headers/footers removed
    """
    try:
        # Ensure authenticated
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })

        # MCP / LLM clients may pass hours_back as str or float; newsletter code needs int.
        if isinstance(hours_back, bool):
            return json.dumps({"error": "hours_back must be an integer"})
        try:
            if isinstance(hours_back, float):
                if not hours_back.is_integer():
                    return json.dumps({"error": "hours_back must be a whole number"})
                hours_back = int(hours_back)
            elif isinstance(hours_back, str):
                hours_back = int(hours_back.strip())
            elif not isinstance(hours_back, int):
                return json.dumps({
                    "error": f"hours_back must be an integer, got {type(hours_back).__name__}"
                })
            validate_hours_back(hours_back)
        except ValueError:
            return json.dumps({"error": "hours_back must be a valid whole number"})
        except ValidationError as e:
            return json.dumps({"error": str(e)})
        
        # Parse custom senders if provided
        custom_senders = None
        if sender_emails.strip():
            custom_senders = [s.strip() for s in sender_emails.split(',') if s.strip()]
        
        # Fetch newsletters
        result = fetch_newsletters_func(
            service=gmail_client.service,
            hours_back=hours_back,
            senders=custom_senders
        )
        
        if result['total_emails'] == 0:
            return json.dumps({
                "message": f"No newsletters found in the past {hours_back} hours",
                "date_range": result['date_range'],
                "hours_back": hours_back,
                "total_emails": 0
            })
        
        # Add friendly names for senders
        newsletters_with_names = {}
        for sender, emails in result['newsletters_by_sender'].items():
            friendly_name = get_sender_name(sender)
            newsletters_with_names[f"{friendly_name} ({sender})"] = emails
        
        result['newsletters_by_sender'] = newsletters_with_names
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch newsletters: {str(e)}"
        })


@mcp.tool()
def mark_email_read(message_id: str, confirm: bool = False) -> str:
    """
    Mark an email as read. Requires ALLOW_WRITE=true in .env.
    First call returns a confirmation prompt; call again with confirm=true to execute.
    
    Args:
        message_id: Gmail message ID (obtained from list_emails or read_email)
        confirm: Set to true to confirm and execute the action
    
    Returns:
        str: JSON string with success confirmation
    
    Example:
        - mark_email_read(message_id="18f2a3b4c5d6e7f8", confirm=true)
    """
    gate = _write_gate(confirm, "mark_email_read", f"About to mark message {message_id} as read. Call again with confirm=true to proceed.")
    if gate:
        return gate

    try:
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        result = gmail_client.mark_as_read(message_id)
        
        if not result:
            return json.dumps({
                "error": f"Failed to mark email as read. Check message ID: {message_id}"
            })
        
        return json.dumps({
            "success": True,
            "message": "Email marked as read",
            "message_id": message_id,
            "action": "mark_read"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to mark email as read: {str(e)}"
        })


@mcp.tool()
def mark_email_unread(message_id: str, confirm: bool = False) -> str:
    """
    Mark an email as unread. Requires ALLOW_WRITE=true in .env.
    First call returns a confirmation prompt; call again with confirm=true to execute.
    
    Args:
        message_id: Gmail message ID (obtained from list_emails or read_email)
        confirm: Set to true to confirm and execute the action
    
    Returns:
        str: JSON string with success confirmation
    
    Example:
        - mark_email_unread(message_id="18f2a3b4c5d6e7f8", confirm=true)
    """
    gate = _write_gate(confirm, "mark_email_unread", f"About to mark message {message_id} as unread. Call again with confirm=true to proceed.")
    if gate:
        return gate

    try:
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        result = gmail_client.mark_as_unread(message_id)
        
        if not result:
            return json.dumps({
                "error": f"Failed to mark email as unread. Check message ID: {message_id}"
            })
        
        return json.dumps({
            "success": True,
            "message": "Email marked as unread",
            "message_id": message_id,
            "action": "mark_unread"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to mark email as unread: {str(e)}"
        })


@mcp.tool()
def archive_email(message_id: str, confirm: bool = False) -> str:
    """
    Archive an email thread by removing it from the inbox. Requires ALLOW_WRITE=true in .env.
    First call returns a confirmation prompt; call again with confirm=true to execute.
    
    Note: Archiving removes the conversation from your inbox but keeps it in "All Mail".
    
    Args:
        message_id: Gmail message ID (obtained from list_emails or read_email)
        confirm: Set to true to confirm and execute the archive
    
    Returns:
        str: JSON string with success confirmation
    
    Example:
        - archive_email(message_id="18f2a3b4c5d6e7f8", confirm=true)
    """
    gate = _write_gate(confirm, "archive_email", f"About to archive thread for message {message_id} (removes from inbox, keeps in All Mail). Call again with confirm=true to proceed.")
    if gate:
        return gate

    try:
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        result = gmail_client.archive_email(message_id)
        
        if not result:
            return json.dumps({
                "error": f"Failed to archive email. Check message ID: {message_id}"
            })
        
        return json.dumps({
            "success": True,
            "message": "Email archived (removed from inbox)",
            "message_id": message_id,
            "action": "archive"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to archive email: {str(e)}"
        })


@mcp.tool()
def delete_email(message_id: str, confirm: bool = False) -> str:
    """
    Move mail to trash (recoverable ~30 days). Requires ALLOW_WRITE=true in .env.
    First call returns a confirmation prompt; call again with confirm=true to execute.
    If the message is part of a thread, the entire conversation is trashed.
    
    Args:
        message_id: Gmail message ID (obtained from list_emails or read_email)
        confirm: Set to true to confirm and execute the delete
    
    Returns:
        str: JSON string with success confirmation
    
    Example:
        - delete_email(message_id="18f2a3b4c5d6e7f8", confirm=true)
    """
    gate = _write_gate(confirm, "delete_email", f"About to trash thread for message {message_id} (recoverable ~30 days). Call again with confirm=true to proceed.")
    if gate:
        return gate

    try:
        if not gmail_client.service:
            if not gmail_client.authenticate():
                return json.dumps({
                    "error": "Authentication failed. Please run: python authenticate.py"
                })
        
        result = gmail_client.delete_email(message_id)
        
        if not result:
            return json.dumps({
                "error": f"Failed to delete email. Check message ID: {message_id}"
            })
        
        return json.dumps({
            "success": True,
            "message": "Moved to trash (whole thread if this message was in a conversation; recoverable ~30 days)",
            "message_id": message_id,
            "action": "delete"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to delete email: {str(e)}"
        })


# Start MCP server with SSE transport
if __name__ == "__main__":
    mode = "READ-WRITE" if ALLOW_WRITE else "READ-ONLY"
    print(f"Starting {SERVER_NAME} on port {SSE_PORT}...")
    print(f"Mode: {mode}")
    print(f"Connect to: http://localhost:{SSE_PORT}/sse")
    mcp.run(transport="sse")