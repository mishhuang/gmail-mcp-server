"""Gmail API client for interacting with Gmail services."""

import base64
from typing import Optional, List, Dict, Any, Tuple
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import Resource

from .auth import build_gmail_service


def decode_base64_data(data: str) -> str:
    """
    Decode base64url-encoded email content.
    
    Args:
        data: Base64url-encoded string from Gmail API
        
    Returns:
        str: Decoded UTF-8 string
    """
    try:
        # Gmail uses base64url encoding (RFC 4648)
        decoded_bytes = base64.urlsafe_b64decode(data)
        return decoded_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error decoding base64 data: {e}")
        return ""


def get_email_body(payload: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extract plain text and HTML body from email payload.
    
    Args:
        payload: Message payload from Gmail API
        
    Returns:
        Tuple[str, str]: (plain_text_body, html_body)
    """
    plain_body = ""
    html_body = ""
    
    def extract_parts(part: Dict[str, Any]):
        """Recursively extract body parts."""
        nonlocal plain_body, html_body
        
        mime_type = part.get('mimeType', '')
        
        if mime_type == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                plain_body = decode_base64_data(data)
        elif mime_type == 'text/html':
            data = part.get('body', {}).get('data', '')
            if data:
                html_body = decode_base64_data(data)
        elif mime_type.startswith('multipart/'):
            # Recursively process multipart messages
            for subpart in part.get('parts', []):
                extract_parts(subpart)
    
    # Check if message has parts
    if 'parts' in payload:
        for part in payload['parts']:
            extract_parts(part)
    else:
        # Single-part message
        data = payload.get('body', {}).get('data', '')
        if data:
            mime_type = payload.get('mimeType', '')
            decoded = decode_base64_data(data)
            if mime_type == 'text/html':
                html_body = decoded
            else:
                plain_body = decoded
    
    return plain_body, html_body


def parse_email_content(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse email message and extract key information.
    
    Args:
        message: Full message object from Gmail API
        
    Returns:
        Dict with parsed email data including:
        - id: Message ID
        - thread_id: Thread ID
        - subject: Email subject
        - from: Sender email and name
        - to: Recipient(s)
        - date: Date string
        - snippet: Preview text
        - plain_body: Plain text body
        - html_body: HTML body
        - labels: Message labels
    """
    headers = {h['name'].lower(): h['value'] 
               for h in message.get('payload', {}).get('headers', [])}
    
    payload = message.get('payload', {})
    plain_body, html_body = get_email_body(payload)
    
    return {
        'id': message.get('id'),
        'thread_id': message.get('threadId'),
        'subject': headers.get('subject', '(No Subject)'),
        'from': headers.get('from', ''),
        'to': headers.get('to', ''),
        'date': headers.get('date', ''),
        'snippet': message.get('snippet', ''),
        'plain_body': plain_body,
        'html_body': html_body,
        'labels': message.get('labelIds', [])
    }


def format_email_summary(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a compact email summary for list views.
    
    Args:
        message: Message object from Gmail API
        
    Returns:
        Dict with summary fields:
        - id: Message ID
        - subject: Email subject
        - from: Sender
        - date: Date string
        - snippet: Preview text
    """
    headers = {h['name'].lower(): h['value'] 
               for h in message.get('payload', {}).get('headers', [])}
    
    return {
        'id': message.get('id'),
        'subject': headers.get('subject', '(No Subject)'),
        'from': headers.get('from', ''),
        'date': headers.get('date', ''),
        'snippet': message.get('snippet', '')
    }


class GmailClient:
    """
    Client for interacting with Gmail API.
    
    This class provides methods for common Gmail operations such as:
    - Reading emails
    - Sending emails
    - Managing labels
    - Searching messages
    """
    
    def __init__(self):
        """Initialize the Gmail client."""
        self.service: Optional[Resource] = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            bool: True if authentication successful, False otherwise.
        """
        try:
            self.service = build_gmail_service()
            return self.service is not None
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get the user's Gmail profile information.
        
        Returns:
            Optional[Dict[str, Any]]: Profile information including email address,
                                     message count, etc., or None if error occurs.
        """
        if not self.service:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def list_messages(
        self, 
        query: str = "", 
        max_results: int = 10,
        label_ids: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        List messages from the user's mailbox.
        
        Args:
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            max_results: Maximum number of messages to return
            label_ids: List of label IDs to filter by (e.g., ['INBOX', 'UNREAD'])
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of message objects, or None if error occurs.
        """
        if not self.service:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
        
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results,
            }
            
            if query:
                params['q'] = query
            
            if label_ids:
                params['labelIds'] = label_ids
            
            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            print(f"Error listing messages: {e}")
            return None
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific message by ID.
        
        Args:
            message_id: The ID of the message to retrieve
        
        Returns:
            Optional[Dict[str, Any]]: Message object with full details, or None if error occurs.
        """
        if not self.service:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            print(f"Error getting message {message_id}: {e}")
            return None
    
    def get_email_summaries(
        self, 
        query: str = "", 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get formatted email summaries for list view.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of emails to return
            
        Returns:
            List[Dict[str, Any]]: List of formatted email summaries
        """
        if not self.service:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
        
        try:
            # Get message IDs
            message_refs = self.list_messages(query=query, max_results=max_results)
            if not message_refs:
                return []
            
            # Fetch full message details for each
            summaries = []
            for ref in message_refs:
                message = self.get_message(ref['id'])
                if message:
                    summary = format_email_summary(message)
                    summaries.append(summary)
            
            return summaries
        except Exception as e:
            print(f"Error getting email summaries: {e}")
            return []
    
    def get_parsed_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a fully parsed email with extracted content.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Optional[Dict[str, Any]]: Parsed email data or None if error
        """
        message = self.get_message(message_id)
        if not message:
            return None
        
        return parse_email_content(message)
    
    def search_emails_from_sender(
        self,
        sender: str,
        after_date: str = "",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for emails from a specific sender.
        
        Args:
            sender: Email address to search for
            after_date: Date in YYYY/MM/DD format (optional)
            max_results: Maximum number of emails to return
            
        Returns:
            List[Dict[str, Any]]: List of email summaries
        """
        # Build query
        query = f"from:{sender}"
        if after_date:
            query += f" after:{after_date}"
        
        return self.get_email_summaries(query=query, max_results=max_results)
    
    # Placeholder methods for future implementation
    
    def send_message(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email message.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
        
        Returns:
            bool: True if sent successfully, False otherwise.
            
        Note:
            This is a placeholder. Full implementation coming soon.
        """
        raise NotImplementedError("send_message will be implemented in future updates")
    
    def list_labels(self) -> Optional[List[Dict[str, Any]]]:
        """
        List all labels in the user's mailbox.
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of label objects, or None if error occurs.
            
        Note:
            This is a placeholder. Full implementation coming soon.
        """
        raise NotImplementedError("list_labels will be implemented in future updates")

