"""Authentication module for Gmail API using OAuth 2.0."""

from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource
import os.path

from .config import CREDENTIALS_FILE, TOKEN_FILE, GMAIL_SCOPES


def get_gmail_credentials() -> Optional[Credentials]:
    """
    Retrieve Gmail API credentials using OAuth 2.0 flow.
    
    Returns:
        Optional[Credentials]: Valid Gmail API credentials, or None if authentication fails.
        
    Notes:
        - If token.json exists, it will be used and refreshed if expired
        - If token.json doesn't exist, a new OAuth flow will be initiated
        - The credentials file (credentials.json) must exist in the project root
    """
    creds: Optional[Credentials] = None
    
    # Load existing credentials from token file if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), GMAIL_SCOPES)
    
    # If no valid credentials are available, trigger OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired credentials
            creds.refresh(Request())
        else:
            # Start new OAuth flow
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file not found at {CREDENTIALS_FILE}. "
                    "Please download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def build_gmail_service() -> Optional[Resource]:
    """
    Build and return a Gmail API service instance.
    
    Returns:
        Optional[Resource]: Gmail API service instance, or None if authentication fails.
        
    Example:
        >>> service = build_gmail_service()
        >>> if service:
        >>>     results = service.users().messages().list(userId='me').execute()
    """
    try:
        creds = get_gmail_credentials()
        if not creds:
            return None
        
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None

