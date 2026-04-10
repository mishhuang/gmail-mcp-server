"""
Gmail MCP Server - A Model Context Protocol server for Gmail integration.

This package provides a FastMCP server with tools for:
- Reading, sending, and managing emails
- Aggregating and organizing newsletters
- OAuth 2.0 authentication with Gmail API
- Comprehensive error handling and validation

Main modules:
- auth: OAuth 2.0 authentication
- gmail_client: Gmail API client wrapper
- newsletter: Newsletter aggregation utilities
- config: Configuration constants
- exceptions: Custom exception classes
- validation: Input validation utilities
"""

__version__ = "0.1.0"
__author__ = "Michelle Huang"


def __getattr__(name: str):
    """Lazy imports so that `import src` doesn't pull in Google libs immediately."""
    _lazy = {
        "GmailClient": ("gmail_client", "GmailClient"),
        "GmailMCPError": ("exceptions", "GmailMCPError"),
        "AuthenticationError": ("exceptions", "AuthenticationError"),
        "GmailAPIError": ("exceptions", "GmailAPIError"),
        "ValidationError": ("exceptions", "ValidationError"),
        "RateLimitError": ("exceptions", "RateLimitError"),
    }
    if name in _lazy:
        module_name, attr = _lazy[name]
        import importlib
        mod = importlib.import_module(f".{module_name}", __package__)
        return getattr(mod, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "GmailClient",
    "GmailMCPError",
    "AuthenticationError",
    "GmailAPIError",
    "ValidationError",
    "RateLimitError",
]
