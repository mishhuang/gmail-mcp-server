"""Newsletter fetching and processing utilities for Gmail MCP Server."""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from googleapiclient.discovery import Resource

from .gmail_client import parse_email_content

logger = logging.getLogger(__name__)


# Default newsletter sender email addresses
NEWSLETTER_SENDERS = {
    'bens_bites': 'hello@bensbites.beehiiv.com',
    'the_neuron': 'newsletter@theneurondaily.com',
    'the_rundown': 'team@rundown.ai',
    'last_week_in_ai': 'hello@lastweekin.ai',
    'alpha_signal': 'newsletter@alphasignal.ai',
}


def calculate_date_filter(hours_back: int) -> str:
    """
    Calculate Gmail date filter for searching emails.
    
    Args:
        hours_back: Number of hours to look back from now
        
    Returns:
        str: Date in Gmail format (YYYY/MM/DD)
        
    Example:
        >>> calculate_date_filter(36)
        '2024/11/06'  # (if current date is 2024/11/07)
    """
    target_date = datetime.now() - timedelta(hours=hours_back)
    return target_date.strftime('%Y/%m/%d')


def extract_main_content(html: str) -> str:
    """
    Extract main content from HTML email, removing headers/footers/unsubscribe links.
    
    This function:
    - Removes script/style tags and metadata
    - Strips common newsletter footers (unsubscribe, social links)
    - Preserves important formatting (headings, lists)
    - Formats links as [text](url) for better readability
    
    Args:
        html: HTML content of email
        
    Returns:
        str: Cleaned main content with preserved structure
        
    Example:
        >>> html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        >>> extract_main_content(html)
        'Title\\n\\nContent'
    """
    if not html:
        return ""
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'head', 'footer', 'meta', 'link', 'noscript']):
            element.decompose()
        
        # Remove elements with unsubscribe/footer classes or IDs
        footer_patterns = ['footer', 'unsubscribe', 'social', 'share', 'preference']
        for pattern in footer_patterns:
            for element in soup.find_all(class_=re.compile(pattern, re.I)):
                element.decompose()
            for element in soup.find_all(id=re.compile(pattern, re.I)):
                element.decompose()
        
        # Convert links to readable format [text](url)
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href and text and not href.startswith('#'):
                link.replace_with(f"[{text}]({href})")
        
        # Add spacing around headings for better structure
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.insert_before('\n\n')
            tag.insert_after('\n')
        
        # Remove unsubscribe links and footers (common text patterns)
        unsubscribe_patterns = [
            'unsubscribe',
            'manage preferences',
            'update your preferences',
            'why did I get this',
            'sent to',
            'you received this email',
            'no longer want to receive',
            'email settings',
            'stop receiving',
        ]
        
        for element in soup.find_all(string=True):
            text_lower = element.lower() if isinstance(element, str) else ""
            if any(pattern in text_lower for pattern in unsubscribe_patterns):
                parent = element.parent
                if parent and len(text_lower) < 100:  # Only remove short unsubscribe snippets
                    parent.decompose()
        
        # Get text content with preserved structure
        text = soup.get_text(separator='\n', strip=True)
        
        return text
        
    except Exception as e:
        logger.error(f"Error extracting main content from HTML: {e}")
        return ""


def clean_email_content(html_content: str, plain_content: str) -> str:
    """
    Clean and format email content, preferring HTML but falling back to plain text.
    
    Args:
        html_content: HTML version of email body
        plain_content: Plain text version of email body
        
    Returns:
        str: Cleaned and formatted content
    """
    # Prefer HTML content for better structure
    if html_content:
        content = extract_main_content(html_content)
    else:
        content = plain_content
    
    if not content:
        return ""
    
    # Clean up excessive whitespace
    lines = content.split('\n')
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        line = line.strip()
        
        # Skip multiple consecutive empty lines
        if not line:
            if not prev_empty:
                cleaned_lines.append('')
                prev_empty = True
            continue
        
        prev_empty = False
        cleaned_lines.append(line)
    
    # Join and remove excessive spaces
    cleaned = '\n'.join(cleaned_lines)
    cleaned = re.sub(r' +', ' ', cleaned)
    
    # Limit to reasonable length (avoid massive emails)
    max_length = 50000  # ~50k characters
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "\n\n[Content truncated for length...]"
    
    return cleaned.strip()


def fetch_newsletters(
    service: Resource,
    hours_back: int = 36,
    senders: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Fetch newsletter emails from specified senders within the given time range.
    
    Args:
        service: Authenticated Gmail API service
        hours_back: How many hours back to search (default: 36)
        senders: List of sender email addresses (uses defaults if None)
        
    Returns:
        Dict with structure:
        {
            'date_range': str,
            'hours_back': int,
            'total_emails': int,
            'newsletters_by_sender': {
                'sender@example.com': [
                    {
                        'id': str,
                        'subject': str,
                        'date': str,
                        'content': str
                    }
                ]
            }
        }
    """
    # Use default senders if none provided
    if senders is None:
        senders = list(NEWSLETTER_SENDERS.values())
    
    # Calculate date filter
    date_filter = calculate_date_filter(hours_back)
    target_date = datetime.now() - timedelta(hours=hours_back)
    current_date = datetime.now()
    
    date_range = f"{target_date.strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}"
    
    newsletters_by_sender = {}
    total_emails = 0
    
    # Fetch emails for each sender
    for sender in senders:
        try:
            # Build query
            query = f"from:{sender} after:{date_filter}"
            
            # Search for messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10  # Reasonable limit per sender
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                continue
            
            sender_emails = []
            
            # Fetch and parse each message
            for msg_ref in messages:
                msg_id = msg_ref['id']
                
                # Get full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                
                # Parse email content
                parsed = parse_email_content(message)
                
                # Clean content
                cleaned_content = clean_email_content(
                    parsed.get('html_body', ''),
                    parsed.get('plain_body', '')
                )
                
                sender_emails.append({
                    'id': parsed['id'],
                    'subject': parsed['subject'],
                    'date': parsed['date'],
                    'content': cleaned_content
                })
                
                total_emails += 1
            
            if sender_emails:
                newsletters_by_sender[sender] = sender_emails
                
        except Exception as e:
            logger.error(f"Error fetching newsletters from {sender}: {e}")
            continue
    
    return {
        'date_range': date_range,
        'hours_back': hours_back,
        'total_emails': total_emails,
        'newsletters_by_sender': newsletters_by_sender
    }


def get_sender_name(email: str) -> str:
    """
    Get friendly name for a newsletter sender.
    
    Args:
        email: Sender email address
        
    Returns:
        str: Friendly name or email if not recognized
    """
    # Reverse lookup in NEWSLETTER_SENDERS
    for name, sender_email in NEWSLETTER_SENDERS.items():
        if sender_email == email:
            # Convert 'bens_bites' to "Ben's Bites"
            return name.replace('_', ' ').title().replace(' S ', "'s ")
    
    # Extract domain name as fallback
    if '@' in email:
        domain = email.split('@')[1].split('.')[0]
        return domain.title()
    
    return email

