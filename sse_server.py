"""
Gmail MCP Server
A FastMCP server for Gmail integration using the Gmail API.
"""

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


# Additional tools will be added here as the project grows
# Examples: list_emails, send_email, search_emails, etc.


# Start MCP server with SSE transport
if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} on port {SSE_PORT}...")
    print(f"Connect to: http://localhost:{SSE_PORT}/sse")
    mcp.run(transport="sse")