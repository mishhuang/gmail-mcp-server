"""
Authentication module for Gmail API using OAuth 2.0.

This module handles the complete OAuth 2.0 flow for Gmail API access:
- Browser-based authentication using Google's OAuth flow
- Automatic token refresh when credentials expire
- Persistent credential storage in token.json
- Support for multiple Gmail API scopes
"""

from typing import Optional
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from .config import CREDENTIALS_FILE, TOKEN_FILE, GMAIL_SCOPES, OAUTH_PORT


def load_credentials_file() -> dict:
    """
    Load OAuth client credentials from credentials.json file.
    
    Returns:
        dict: OAuth client configuration dictionary.
        
    Raises:
        FileNotFoundError: If credentials.json doesn't exist.
        json.JSONDecodeError: If credentials.json is invalid JSON.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"\n❌ Credentials file not found at: {CREDENTIALS_FILE}\n\n"
            "Please follow these steps:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create a project or select an existing one\n"
            "3. Enable the Gmail API\n"
            "4. Create OAuth 2.0 credentials (Desktop app)\n"
            "5. Download the credentials JSON file\n"
            "6. Save it as 'credentials.json' in the project root\n"
        )
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in credentials file: {CREDENTIALS_FILE}",
            e.doc,
            e.pos
        )


def load_token() -> Optional[Credentials]:
    """
    Load existing OAuth token from token.json file.
    
    Returns:
        Optional[Credentials]: Loaded credentials if file exists, None otherwise.
    """
    if not os.path.exists(TOKEN_FILE):
        return None
    
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), GMAIL_SCOPES)
        return creds
    except Exception as e:
        print(f"⚠️  Warning: Could not load token file: {e}")
        print(f"   Token file will be recreated.")
        return None


def save_token(creds: Credentials) -> None:
    """
    Save OAuth credentials to token.json file.
    
    Args:
        creds: Google OAuth2 credentials to save.
    """
    try:
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"✓ Credentials saved to: {TOKEN_FILE}")
    except Exception as e:
        print(f"⚠️  Warning: Could not save token: {e}")


def refresh_credentials(creds: Credentials) -> Credentials:
    """
    Refresh expired OAuth credentials.
    
    Args:
        creds: Expired credentials with refresh token.
        
    Returns:
        Credentials: Refreshed credentials.
        
    Raises:
        Exception: If refresh fails.
    """
    try:
        print("🔄 Refreshing expired credentials...")
        creds.refresh(Request())
        print("✓ Credentials refreshed successfully")
        return creds
    except Exception as e:
        raise Exception(f"Failed to refresh credentials: {e}")


def initiate_oauth_flow() -> Credentials:
    """
    Initiate browser-based OAuth 2.0 flow.
    
    This will:
    1. Start a local server on the specified port
    2. Open the user's browser for authorization
    3. Wait for the authorization callback
    4. Return the authorized credentials
    
    Returns:
        Credentials: Authorized credentials from OAuth flow.
        
    Raises:
        FileNotFoundError: If credentials.json doesn't exist.
        Exception: If OAuth flow fails.
    """
    # Ensure credentials file exists
    load_credentials_file()
    
    print("\n" + "="*60)
    print("🔐 Starting OAuth 2.0 Authentication")
    print("="*60)
    print(f"\n📋 Requested Gmail API Scopes:")
    for scope in GMAIL_SCOPES:
        scope_name = scope.split('/')[-1]
        print(f"   • {scope_name}")
    print(f"\n🌐 Opening browser for authentication...")
    print(f"   If browser doesn't open, copy the URL from below.\n")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), 
            GMAIL_SCOPES
        )
        
        # Run local server on configured port
        creds = flow.run_local_server(
            port=OAUTH_PORT,
            open_browser=True,
            success_message="✓ Authentication successful! You can close this window."
        )
        
        print("\n✅ Authentication completed successfully!")
        return creds
        
    except Exception as e:
        raise Exception(f"OAuth flow failed: {e}")


def get_gmail_credentials(interactive: bool = True) -> Optional[Credentials]:
    """
    Retrieve valid Gmail API credentials using OAuth 2.0 flow.
    
    This function implements the complete OAuth flow:
    1. Check for existing token.json
    2. Validate credentials (check expiration)
    3. Refresh if expired (and refresh token available)
    4. Initiate new OAuth flow if needed
    5. Save credentials for future use
    
    Args:
        interactive: If True, will prompt user for authorization when needed.
                    If False, returns None if valid credentials don't exist.
    
    Returns:
        Optional[Credentials]: Valid Gmail API credentials, or None if unavailable.
        
    Raises:
        FileNotFoundError: If credentials.json is missing.
        Exception: If authentication fails.
    """
    creds: Optional[Credentials] = None
    
    # Try to load existing token
    creds = load_token()
    
    # Check if credentials are valid
    if creds and creds.valid:
        return creds
    
    # Try to refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds = refresh_credentials(creds)
            save_token(creds)
            return creds
        except Exception as e:
            print(f"⚠️  Could not refresh credentials: {e}")
            print(f"   Will start new OAuth flow...")
            creds = None
    
    # Need new credentials
    if not interactive:
        return None
    
    # Initiate OAuth flow
    creds = initiate_oauth_flow()
    save_token(creds)
    
    return creds


def build_gmail_service(interactive: bool = True) -> Optional[Resource]:
    """
    Build and return an authenticated Gmail API service instance.
    
    This is the main entry point for getting a Gmail service object.
    It handles the complete authentication flow automatically.
    
    Args:
        interactive: If True, will prompt user for auth if needed.
                    If False, returns None if credentials aren't available.
    
    Returns:
        Optional[Resource]: Authenticated Gmail API service instance,
                           or None if authentication fails.
        
    Example:
        >>> service = build_gmail_service()
        >>> if service:
        >>>     results = service.users().messages().list(userId='me').execute()
        >>>     print(f"Found {len(results.get('messages', []))} messages")
    
    Raises:
        FileNotFoundError: If credentials.json is missing.
        HttpError: If Gmail API request fails.
    """
    try:
        creds = get_gmail_credentials(interactive=interactive)
        if not creds:
            return None
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Verify service works by making a simple API call
        try:
            service.users().getProfile(userId='me').execute()
        except HttpError as e:
            print(f"⚠️  Gmail API verification failed: {e}")
            return None
        
        return service
        
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f"❌ Error building Gmail service: {e}")
        return None


def verify_authentication() -> bool:
    """
    Verify that Gmail authentication is working.
    
    Returns:
        bool: True if authentication successful, False otherwise.
    """
    try:
        service = build_gmail_service(interactive=False)
        if not service:
            return False
        
        # Try to get user profile
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'Unknown')
        
        print(f"✅ Successfully authenticated as: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Authentication verification failed: {e}")
        return False

