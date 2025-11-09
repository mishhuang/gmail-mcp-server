"""
Gmail MCP Server
A FastMCP server for Gmail integration using the Gmail API.
"""

import json
from typing import Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from src.config import SERVER_NAME, SSE_PORT
from src.gmail_client import GmailClient

# Load environment variables
load_dotenv()

# Initialize MCP server with port configuration
mcp = FastMCP(SERVER_NAME, port=SSE_PORT)

# Initialize Gmail client (will be used by tools)
gmail_client = GmailClient()


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


# Start MCP server with SSE transport
if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} on port {SSE_PORT}...")
    print(f"Connect to: http://localhost:{SSE_PORT}/sse")
    mcp.run(transport="sse")