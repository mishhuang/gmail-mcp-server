"""Custom exception classes for Gmail MCP Server."""


class GmailMCPError(Exception):
    """Base exception for Gmail MCP Server."""
    pass


class AuthenticationError(GmailMCPError):
    """
    Raised when OAuth authentication fails.
    
    Examples:
        - Missing credentials.json
        - Token refresh failure
        - Invalid OAuth scopes
    """
    pass


class GmailAPIError(GmailMCPError):
    """
    Raised when Gmail API returns an error.
    
    Examples:
        - API quota exceeded
        - Permission denied
        - Resource not found
        - Invalid request
    """
    
    def __init__(self, message: str, status_code: int = None, details: str = None):
        """
        Initialize GmailAPIError.
        
        Args:
            message: Error message
            status_code: HTTP status code from API
            details: Additional error details
        """
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationError(GmailMCPError):
    """
    Raised when input validation fails.
    
    Examples:
        - Invalid email format
        - Invalid message ID
        - Invalid date format
        - Out of range values
    """
    pass


class RateLimitError(GmailAPIError):
    """
    Raised when Gmail API rate limit is exceeded.
    
    This is a specific type of GmailAPIError that indicates
    the application should retry after a delay.
    """
    
    def __init__(self, message: str = "Gmail API rate limit exceeded", retry_after: int = None):
        """
        Initialize RateLimitError.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (if provided by API)
        """
        self.retry_after = retry_after
        super().__init__(message, status_code=429)

