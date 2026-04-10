import asyncio
import os
from typing import Any, List, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv
from anthropic import Anthropic
import mcp.types as types

# Load environment variables
load_dotenv()

# Anthropic context limit is 200k tokens; tool results can dwarf the rest of the conversation.
TOOL_RESULT_CHAR_BUDGET = int(os.getenv("ANTHROPIC_TOOL_RESULT_MAX_CHARS", "120000"))


class SSE_MCP_Client:
    """
    Client for connecting to an MCP server using SSE.
    """
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None

    async def connect_to_server(self, server_url: str):
        """Connects to an MCP server via SSE."""
        try:
            sse_transport = await self.exit_stack.enter_async_context(sse_client(server_url))
            sse_recv, sse_sent = sse_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(sse_recv, sse_sent))
            if self.session:
                await self.session.initialize()
                print(f"Connected to MCP server at {server_url}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    async def get_tools(self) -> List[types.Tool]:
        """Retrieves available tools from the server."""
        if not self.session:
            print("Session not initialized. Cannot retrieve tools.")
            return []
        response = await self.session.list_tools()
        print("Available tools:", [tool.name for tool in response.tools])
        return response.tools

    async def cleanup(self):
        """Closes the connection and cleans up resources."""
        await self.exit_stack.aclose()


def reformat_tools_for_anthropic(tools: List[types.Tool]):
    """
    Reformats the tool descriptions for Anthropic compatibility.
    """
    return [{
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    } for tool in tools]


def _content_blocks_to_api(blocks: List[Any]) -> List[dict]:
    """Serialize Anthropic content blocks for the messages API."""
    return [b.model_dump() if hasattr(b, "model_dump") else b for b in blocks]


def _extract_text_for_display(blocks: List[Any]) -> str:
    """Collect assistant text blocks (tool_use blocks have no .text)."""
    texts = []
    for b in blocks:
        if getattr(b, "type", None) == "text":
            texts.append(b.text)
    return "\n".join(texts).strip()


def _tool_use_blocks(blocks: List[Any]) -> List[Any]:
    return [b for b in blocks if getattr(b, "type", None) == "tool_use"]


def _mcp_tool_result_str(result: Any) -> str:
    parts = []
    for item in result.content:
        t = getattr(item, "text", None)
        if t is not None:
            parts.append(t)
        else:
            parts.append(str(item))
    return "\n".join(parts)


def _truncate_for_context_window(text: str) -> str:
    if len(text) <= TOOL_RESULT_CHAR_BUDGET:
        return text
    return (
        text[:TOOL_RESULT_CHAR_BUDGET]
        + "\n\n[Tool output truncated for model context limit. "
        "Fetch fewer emails, use fetch_newsletters with fewer hours, or read one message_id at a time.]"
    )


async def main():
    client = SSE_MCP_Client()
    chat = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model_name = os.getenv("ANTHROPIC_MODEL_NAME", "claude-sonnet-4-20250514")
    print(f"Using model: {model_name}")

    try:
        await client.connect_to_server("http://localhost:5553/sse")
        tools = await client.get_tools()
        formatted_tools = reformat_tools_for_anthropic(tools)

        messages: List[dict] = []
        user_message = input("Input: ")

        chat_prompt = (
            "You are a helpful assistant, you have the ability to call tools to achieve user requests.\n\n"
            "User request: " + user_message + "\n\n"
        )
        messages.append({"role": "user", "content": chat_prompt})

        while True:
            if not user_message:
                continue

            while True:
                llm_response = chat.messages.create(
                    model=model_name,
                    max_tokens=2048,
                    messages=messages,
                    tools=formatted_tools,
                    temperature=0.1,
                )
                messages.append({
                    "role": "assistant",
                    "content": _content_blocks_to_api(llm_response.content),
                })

                tools_used = _tool_use_blocks(llm_response.content)
                visible = _extract_text_for_display(llm_response.content)
                if visible:
                    print(f"LLM Response: {visible}")
                if tools_used:
                    print(f"LLM: calling tools: {', '.join(t.name for t in tools_used)}")

                if not tools_used:
                    break

                tool_results = []
                for tb in tools_used:
                    tool_response = await client.session.call_tool(tb.name, tb.input)
                    tool_result_text = _truncate_for_context_window(
                        _mcp_tool_result_str(tool_response)
                    )
                    preview = tool_result_text[:2000]
                    if len(tool_result_text) > 2000:
                        preview += f"\n... ({len(tool_result_text)} chars total)"
                    print(f"Tool {tb.name} response:\n{preview}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tb.id,
                        "content": tool_result_text,
                    })
                messages.append({"role": "user", "content": tool_results})

            user_message = input("Input: ")
            messages.append({"role": "user", "content": user_message})

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
