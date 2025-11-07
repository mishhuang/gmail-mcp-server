from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool
from dotenv import load_dotenv

load_dotenv()

# Initialize MCP server
mcp = FastMCP("SimpleMCPServer")

#### Write Tools here ####



async def list_tools() -> List[Tool]:
    """List the tools available to the LLM."""
    return [
        Tool( 
            # You will list your tools here as you write them
        ),
    ]

# Start MCP server with SSE transport
if __name__ == "__main__":
    mcp.run(transport="sse")