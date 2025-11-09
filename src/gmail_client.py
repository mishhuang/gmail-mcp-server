"""Gmail API client for interacting with Gmail services."""

import base64
import re
from typing import Optional, List, Dict, Any, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from .auth import build_gmail_service


def validate_email(email: str) -> bool:
    """
    Validate email address format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid email format, False otherwise
        
    Raises:
        ValueError: If email format is invalid
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not isinstance(email, str):
        raise ValueError(f"Invalid email: empty or not a string")
    
    if not re.match(pattern, email.strip()):
        raise ValueError(f"Invalid email format: {email}")
    
    return True


def encode_message(message: MIMEText) -> str:
    """
    Base64 URL-safe encode a MIME message for Gmail API.
    
    Args:
        message: MIME message object
        
    Returns:
        str: Base64 URL-safe encoded message string
    """
    raw_message = message.as_bytes()
    encoded = base64.urlsafe_b64encode(raw_message).decode('utf-8')
    return encoded


def create_message(
    to: str,
    subject: str,
    body: str,
    is_html: bool = False,
    from_email: Optional[str] = None
) -> Dict[str, str]:
    """
    Create a MIME email message.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        is_html: Whether body is HTML (default: False for plain text)
        from_email: Sender email (optional, defaults to authenticated user)
        
    Returns:
        Dict with 'raw' key containing base64url-encoded message
        
    Raises:
        ValueError: If recipient email is invalid
    """
    # Validate recipient email
    validate_email(to)
    
    # Create message
    if is_html:
        message = MIMEMultipart('alternative')
        text_part = MIMEText(body, 'html')
        message.attach(text_part)
    else:
        message = MIMEText(body, 'plain')
    
    message['to'] = to
    message['subject'] = subject
    
    if from_email:
        validate_email(from_email)
        message['from'] = from_email
    
    # Encode and return
    encoded = encode_message(message)
    return {'raw': encoded}


def create_reply_message(
    original_message: Dict[str, Any],
    body: str,
    is_html: bool = False
) -> Dict[str, str]:
    """
    Create a reply message with proper threading headers.
    
    Args:
        original_message: Original message dict from Gmail API
        body: Reply body content
        is_html: Whether body is HTML (default: False)
        
    Returns:
        Dict with 'raw' and 'threadId' for sending via Gmail API
        
    Raises:
        ValueError: If original message is missing required headers
    """
    # Extract headers from original message
    headers = {h['name'].lower(): h['value'] 
               for h in original_message.get('payload', {}).get('headers', [])}
    
    original_from = headers.get('from', '')
    original_subject = headers.get('subject', '')
    original_message_id = headers.get('message-id', '')
    thread_id = original_message.get('threadId', '')
    
    if not original_from:
        raise ValueError("Original message missing 'From' header")
    
    # Extract email from "Name <email@domain.com>" format
    email_match = re.search(r'<(.+?)>', original_from)
    reply_to = email_match.group(1) if email_match else original_from
    
    # Validate recipient
    validate_email(reply_to)
    
    # Prepend "Re: " to subject if not already present
    reply_subject = original_subject
    if not reply_subject.lower().startswith('re:'):
        reply_subject = f"Re: {original_subject}"
    
    # Create reply message
    if is_html:
        message = MIMEMultipart('alternative')
        text_part = MIMEText(body, 'html')
        message.attach(text_part)
    else:
        message = MIMEText(body, 'plain')
    
    message['to'] = reply_to
    message['subject'] = reply_subject
    
    # Set threading headers
    if original_message_id:
        message['In-Reply-To'] = original_message_id
        message['References'] = original_message_id
    
    # Encode message
    encoded = encode_message(message)
    
    return {
        'raw': encoded,
        'threadId': thread_id
    }


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
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Send an email message via Gmail.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML (default: False for plain text)
        
        Returns:
            Optional[Dict[str, Any]]: Sent message details including message ID,
                                     or None if sending fails
        
        Raises:
            ValueError: If recipient email is invalid
            RuntimeError: If client not authenticated
        """
        if not self.service:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
        
        try:
            # Create message
            message = create_message(to=to, subject=subject, body=body, is_html=is_html)
            
            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return sent_message
            
        except HttpError as e:
            print(f"Gmail API error sending message: {e}")
            return None
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def reply_to_email(
        self,
        message_id: str,
        body: str,
        is_html: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Reply to an existing email message.
        
        Args:
            message_id: ID of the message to reply to
            body: Reply body content
            is_html: Whether body is HTML (default: False)
        
        Returns:
            Optional[Dict[str, Any]]: Sent reply details including message ID,
                                     or None if reply fails
        
        Raises:
            RuntimeError: If client not authenticated
            ValueError: If original message cannot be found or is invalid
        """
        if not self.service:
            raise RuntimeError("Client not authenticated. Call authenticate() first.")
        
        try:
            # Fetch original message
            original = self.get_message(message_id)
            if not original:
                raise ValueError(f"Could not fetch original message: {message_id}")
            
            # Create reply message
            reply_message = create_reply_message(
                original_message=original,
                body=body,
                is_html=is_html
            )
            
            # Send reply via Gmail API
            sent_reply = self.service.users().messages().send(
                userId='me',
                body=reply_message
            ).execute()
            
            return sent_reply
            
        except HttpError as e:
            print(f"Gmail API error sending reply: {e}")
            return None
        except ValueError:
            raise
        except Exception as e:
            print(f"Error sending reply: {e}")
            return None
    
    # Placeholder methods for future implementation
    
    def list_labels(self) -> Optional[List[Dict[str, Any]]]:
        """
        List all labels in the user's mailbox.
        
        Returns:
            Optional[List[Dict[str, Any]]]: List of label objects, or None if error occurs.
            
        Note:
            This is a placeholder. Full implementation coming soon.
        """
        raise NotImplementedError("list_labels will be implemented in future updates")

