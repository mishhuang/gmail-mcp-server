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

# Import key classes for easier access
from .gmail_client import GmailClient
from .exceptions import (
    GmailMCPError,
    AuthenticationError,
    GmailAPIError,
    ValidationError,
    RateLimitError,
)

__all__ = [
    "GmailClient",
    "GmailMCPError",
    "AuthenticationError",
    "GmailAPIError",
    "ValidationError",
    "RateLimitError",
]

