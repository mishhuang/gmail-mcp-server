#!/usr/bin/env python3
"""
Standalone Gmail OAuth 2.0 Authentication Script

Run this script to authenticate with Gmail API and save credentials.
This only needs to be run once before using the MCP server.

Usage:
    python authenticate.py
    
The script will:
1. Check for existing credentials
2. Open your browser for Google authorization
3. Save the token for future use
4. Verify the authentication worked
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.auth import (
    get_gmail_credentials,
    build_gmail_service,
    verify_authentication,
)
from src.config import (
    CREDENTIALS_FILE,
    TOKEN_FILE,
    GMAIL_SCOPES,
    OAUTH_PORT
)


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print(" " * 15 + "Gmail MCP Server - Authentication")
    print("="*70)


def print_instructions():
    """Print pre-authentication instructions."""
    print("\n📋 Before you begin:")
    print("   1. Make sure credentials.json is in this directory")
    print("   2. The file should be downloaded from Google Cloud Console")
    print("   3. Your browser will open for authorization")
    print("   4. You'll need to sign in with your Google account")
    print("\n📂 Files:")
    print(f"   Credentials: {CREDENTIALS_FILE}")
    print(f"   Token (will be created): {TOKEN_FILE}")
    print(f"\n🔌 OAuth Port: {OAUTH_PORT}")
    print(f"\n🔐 Requesting access to these Gmail scopes:")
    for scope in GMAIL_SCOPES:
        scope_name = scope.split('/')[-1]
        print(f"   • {scope_name}")


def check_credentials_file() -> bool:
    """
    Check if credentials.json exists.
    
    Returns:
        bool: True if file exists, False otherwise.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print("\n" + "⚠️ " * 25)
        print("\n❌ ERROR: credentials.json not found!\n")
        print("Please follow these steps to get your credentials:\n")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project (or select existing one)")
        print("3. Enable the Gmail API:")
        print("   • Go to 'APIs & Services' > 'Library'")
        print("   • Search for 'Gmail API' and click 'Enable'")
        print("4. Create OAuth 2.0 credentials:")
        print("   • Go to 'APIs & Services' > 'Credentials'")
        print("   • Click 'Create Credentials' > 'OAuth client ID'")
        print("   • Choose 'Desktop app' as application type")
        print("   • Give it a name (e.g., 'Gmail MCP Server')")
        print("5. Download the credentials:")
        print("   • Click the download button (⬇️) next to your OAuth client")
        print("   • Save the file as 'credentials.json'")
        print(f"6. Place credentials.json in: {Path.cwd()}")
        print("\n" + "⚠️ " * 25 + "\n")
        return False
    
    print(f"✓ Found credentials file: {CREDENTIALS_FILE}")
    return True


def check_existing_token() -> bool:
    """
    Check if token.json already exists.
    
    Returns:
        bool: True if token exists and is valid, False otherwise.
    """
    if not os.path.exists(TOKEN_FILE):
        print(f"ℹ️  No existing token found at: {TOKEN_FILE}")
        return False
    
    print(f"✓ Found existing token: {TOKEN_FILE}")
    print("   Checking if it's still valid...")
    
    # Try to verify existing token
    if verify_authentication():
        print("\n✅ Existing authentication is still valid!")
        print("   No need to re-authenticate.")
        return True
    else:
        print("\n⚠️  Existing token is invalid or expired.")
        print("   Will start new authentication flow...")
        return False


def main():
    """Main authentication flow."""
    print_header()
    print_instructions()
    
    print("\n" + "-"*70)
    print("Starting authentication process...")
    print("-"*70 + "\n")
    
    # Check for credentials file
    if not check_credentials_file():
        sys.exit(1)
    
    # Check for existing valid token
    if check_existing_token():
        print("\n" + "="*70)
        print("✅ Authentication already complete!")
        print("="*70)
        print("\nYou can now run the MCP server:")
        print("  python sse_server.py\n")
        sys.exit(0)
    
    # Proceed with authentication
    print("\nPress Enter to start the authentication flow...")
    print("(or Ctrl+C to cancel)")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Authentication cancelled by user.")
        sys.exit(1)
    
    try:
        # Start OAuth flow
        creds = get_gmail_credentials(interactive=True)
        
        if not creds:
            print("\n❌ Failed to obtain credentials.")
            sys.exit(1)
        
        print("\n" + "-"*70)
        print("Verifying authentication...")
        print("-"*70 + "\n")
        
        # Verify it works
        service = build_gmail_service(interactive=False)
        if service:
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')
            total_messages = profile.get('messagesTotal', 0)
            
            print("\n" + "="*70)
            print("✅ SUCCESS! Gmail authentication complete!")
            print("="*70)
            print(f"\n📧 Authenticated as: {email}")
            print(f"📬 Total messages in account: {total_messages:,}")
            print(f"\n💾 Token saved to: {TOKEN_FILE}")
            print("\n🚀 You can now run the MCP server:")
            print("     python sse_server.py")
            print("\n   Or test with the client:")
            print("     python sse_client.py")
            print("\n" + "="*70 + "\n")
        else:
            print("\n⚠️  Authentication completed but could not verify Gmail access.")
            print("    You may need to enable the Gmail API in Google Cloud Console.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Authentication cancelled by user.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure credentials.json is valid")
        print("  • Check that Gmail API is enabled in Google Cloud Console")
        print(f"  • Verify port {OAUTH_PORT} is not in use")
        print("  • Try deleting token.json and running again")
        sys.exit(1)


if __name__ == "__main__":
    main()

