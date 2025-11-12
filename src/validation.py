"""Input validation utilities for Gmail MCP Server."""

import re
from datetime import datetime
from typing import Optional

from .exceptions import ValidationError


def validate_email(email: str) -> bool:
    """
    Validate email address format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid email format
        
    Raises:
        ValidationError: If email format is invalid
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        ValidationError
    """
    if not email or not isinstance(email, str):
        raise ValidationError("Email must be a non-empty string")
    
    email = email.strip()
    
    # RFC 5322 simplified regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    
    return True


def validate_message_id(message_id: str) -> bool:
    """
    Validate Gmail message ID format.
    
    Gmail message IDs are hexadecimal strings.
    
    Args:
        message_id: Gmail message ID to validate
        
    Returns:
        bool: True if valid message ID format
        
    Raises:
        ValidationError: If message ID format is invalid
    """
    if not message_id or not isinstance(message_id, str):
        raise ValidationError("Message ID must be a non-empty string")
    
    message_id = message_id.strip()
    
    # Gmail message IDs are typically alphanumeric
    if not re.match(r'^[a-zA-Z0-9]+$', message_id):
        raise ValidationError(f"Invalid message ID format: {message_id}")
    
    # Reasonable length check (Gmail IDs are typically 16-20 chars)
    if len(message_id) < 10 or len(message_id) > 30:
        raise ValidationError(f"Message ID has invalid length: {message_id}")
    
    return True


def validate_date_string(date_str: str, format: str = "%Y/%m/%d") -> bool:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        format: Expected date format (default: YYYY/MM/DD)
        
    Returns:
        bool: True if valid date format
        
    Raises:
        ValidationError: If date format is invalid
        
    Example:
        >>> validate_date_string("2024/11/07")
        True
        >>> validate_date_string("11-07-2024")
        ValidationError
    """
    if not date_str or not isinstance(date_str, str):
        raise ValidationError("Date must be a non-empty string")
    
    try:
        datetime.strptime(date_str.strip(), format)
        return True
    except ValueError:
        raise ValidationError(f"Invalid date format: {date_str}. Expected format: {format}")


def sanitize_query(query: str, max_length: int = 500) -> str:
    """
    Sanitize Gmail search query string.
    
    Args:
        query: Gmail search query to sanitize
        max_length: Maximum allowed query length
        
    Returns:
        str: Sanitized query string
        
    Raises:
        ValidationError: If query is invalid
    """
    if not isinstance(query, str):
        raise ValidationError("Query must be a string")
    
    # Strip whitespace
    query = query.strip()
    
    # Check length
    if len(query) > max_length:
        raise ValidationError(f"Query too long: {len(query)} chars (max: {max_length})")
    
    # Gmail queries can contain special operators, so we're permissive
    # Just remove any potentially dangerous characters
    # Allow: alphanumeric, spaces, @, ., -, _, :, /, quotes, parentheses
    sanitized = re.sub(r'[^a-zA-Z0-9\s@.\-_:/\'"(){}[\]]', '', query)
    
    return sanitized


def validate_hours_back(hours: int) -> bool:
    """
    Validate hours_back parameter for time-based queries.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If hours is invalid
    """
    if not isinstance(hours, int):
        raise ValidationError(f"Hours must be an integer, got {type(hours).__name__}")
    
    if hours <= 0:
        raise ValidationError(f"Hours must be positive, got {hours}")
    
    # Reasonable upper limit (1 year = ~8760 hours)
    if hours > 8760:
        raise ValidationError(f"Hours too large: {hours} (max: 8760)")
    
    return True


def validate_max_results(max_results: int) -> bool:
    """
    Validate max_results parameter.
    
    Args:
        max_results: Maximum number of results
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If max_results is invalid
    """
    if not isinstance(max_results, int):
        raise ValidationError(f"max_results must be an integer, got {type(max_results).__name__}")
    
    if max_results <= 0:
        raise ValidationError(f"max_results must be positive, got {max_results}")
    
    # Gmail API limit
    if max_results > 500:
        raise ValidationError(f"max_results too large: {max_results} (max: 500)")
    
    return True


def validate_subject(subject: str, max_length: int = 998) -> bool:
    """
    Validate email subject line.
    
    Args:
        subject: Email subject to validate
        max_length: Maximum subject length (RFC 5322 recommendation)
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If subject is invalid
    """
    if not isinstance(subject, str):
        raise ValidationError("Subject must be a string")
    
    if len(subject) > max_length:
        raise ValidationError(f"Subject too long: {len(subject)} chars (max: {max_length})")
    
    return True


def validate_body(body: str, max_length: int = 5000000) -> bool:
    """
    Validate email body content.
    
    Args:
        body: Email body to validate
        max_length: Maximum body length (~5MB for Gmail)
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If body is invalid
    """
    if not isinstance(body, str):
        raise ValidationError("Body must be a string")
    
    if not body.strip():
        raise ValidationError("Body cannot be empty")
    
    if len(body) > max_length:
        raise ValidationError(f"Body too long: {len(body)} chars (max: {max_length})")
    
    return True

