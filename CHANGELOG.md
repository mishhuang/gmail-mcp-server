# Changelog

All notable changes to the Gmail MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-12

### Added

#### Authentication & Setup
- Complete OAuth 2.0 authentication system with browser-based flow
- Automatic token refresh when credentials expire
- Standalone `authenticate.py` script for easy setup
- Token persistence in `token.json` with automatic management
- Support for multiple Gmail API scopes (readonly, send, compose, modify)

#### Email Reading Features
- `list_emails()` tool - List emails with Gmail search queries
- `read_email()` tool - Read full email content (plain text and HTML)
- `search_emails()` tool - Search emails by sender and date
- Email parsing with multipart MIME support
- Base64url decoding for email content
- Header extraction (subject, from, to, date, etc.)

#### Email Sending Features
- `send_email()` tool - Send new emails (plain text or HTML)
- `reply_to_email()` tool - Reply to emails with proper threading
- MIME message creation for both plain text and HTML
- Automatic "Re:" prefix for replies
- In-Reply-To and References headers for email threading
- Email address validation with regex

#### Email Management Features
- `mark_email_read()` tool - Mark emails as read
- `mark_email_unread()` tool - Mark emails as unread
- `archive_email()` tool - Archive emails (remove from inbox)
- `delete_email()` tool - Move emails to trash (30-day retention)
- Label modification support (add/remove labels)
- Batch email operations helper

#### Newsletter Aggregation
- `fetch_newsletters()` tool - Aggregate newsletters for summarization
- Pre-configured support for 5 popular AI/tech newsletters:
  - Ben's Bites
  - The Neuron
  - The Rundown AI
  - Last Week in AI
  - Alpha Signal
- HTML content cleaning (removes headers, footers, unsubscribe links)
- BeautifulSoup-based content extraction
- Configurable time range (hours back)
- Custom sender list support
- Organized output ready for LLM summarization

#### Error Handling & Validation
- Custom exception classes:
  - `GmailMCPError` (base exception)
  - `AuthenticationError` (OAuth failures)
  - `GmailAPIError` (API errors with status codes)
  - `ValidationError` (input validation)
  - `RateLimitError` (quota exceeded)
- Comprehensive input validation:
  - Email format validation
  - Message ID format validation
  - Date format validation
  - Query sanitization
  - Parameter range checking
- Python logging configuration
- User-friendly error messages

#### Developer Experience
- Modular architecture with clean separation of concerns:
  - `src/auth.py` - Authentication logic
  - `src/gmail_client.py` - Gmail API wrapper
  - `src/newsletter.py` - Newsletter utilities
  - `src/config.py` - Configuration
  - `src/exceptions.py` - Exception classes
  - `src/validation.py` - Validation utilities
- FastMCP server with SSE transport
- Example MCP client (`sse_client.py`) for testing
- Environment variable configuration via `.env`
- Comprehensive docstrings (Google style)
- Type hints throughout

#### Documentation
- Complete README.md with:
  - Installation instructions
  - Google Cloud setup guide
  - All tool documentation with examples
  - Configuration guide
  - Troubleshooting section
  - Gmail API quota information
- Environment variable examples (`.env.example`)
- Code comments explaining design decisions

### Technical Details

#### Dependencies
- FastMCP for MCP server framework
- Google Auth libraries for OAuth 2.0
- Google API Python Client for Gmail API
- BeautifulSoup4 for HTML parsing
- Anthropic SDK for client testing
- Python 3.8+ required

#### Configuration
- Configurable OAuth port (default: 8080)
- Configurable MCP server port (default: 5553)
- Customizable Gmail API scopes
- Newsletter time range (default: 36 hours)

#### Security
- OAuth 2.0 with refresh tokens
- Local credential storage only
- No hardcoded secrets
- Files properly gitignored
- Scoped API permissions

## [Unreleased]

### Planned Features

#### Email Management
- Star/unstar emails
- Add/remove custom labels
- Create new labels
- Move emails between folders
- Batch archive/delete operations
- Email draft creation and management

#### Advanced Search
- Complex Gmail search query builder
- Search by attachment type
- Search by date range with calendar picker
- Search by size/has attachment filters
- Save and reuse search queries

#### Attachments
- Download email attachments
- Send emails with attachments
- Attachment type detection
- Size limit validation
- Virus scanning integration

#### Scheduling & Automation
- Schedule email sending
- Recurring email tasks
- Auto-archive based on rules
- Smart inbox categorization
- Email digest scheduling

#### Calendar Integration
- Create calendar events from emails
- Add meetings mentioned in emails
- RSVP to calendar invites
- Check availability

#### Analytics & Insights
- Email volume analytics
- Response time tracking
- Most frequent senders
- Email categorization
- Thread statistics

#### Performance
- Caching layer for frequently accessed emails
- Rate limit handling with exponential backoff
- Batch API operations
- Connection pooling
- Async operations where applicable

#### Testing
- Comprehensive unit tests
- Integration tests with mock Gmail API
- End-to-end testing suite
- Performance benchmarks

#### Developer Tools
- OpenAPI/Swagger documentation
- GraphQL interface option
- Webhook support
- CLI tool for testing
- Docker container
- Kubernetes deployment templates

## Version History

### [0.1.0] - 2024-11-12
- Initial release
- Core email operations (read, send, manage)
- Newsletter aggregation
- OAuth 2.0 authentication
- Error handling and validation

---

## Notes

### Breaking Changes
None yet (initial release)

### Deprecations
None yet

### Migration Guide
Not applicable (initial release)

### Contributors
- Initial development and implementation

---

For more details on each release, see the [GitHub Releases](https://github.com/mishhuang/gmail-mcp-server/releases) page.

