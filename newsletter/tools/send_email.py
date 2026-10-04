#!/usr/bin/env python3
"""
Send newsletter via Gmail API.

This tool sends formatted HTML newsletters using Gmail API with OAuth2 authentication.
Supports both direct sending and draft creation workflows.
"""

import json
import os
import base64
import pickle
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

class GmailAPIError(Exception):
    """Custom exception for Gmail API errors."""
    pass

class GmailEmailTool:
    def __init__(self):
        # Load credentials and configuration
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', './credentials.json')
        self.token_file = os.getenv('TOKEN_FILE', './token.json')
        self.recipients = os.getenv('NEWSLETTER_RECIPIENTS', '').split(',')
        self.recipients = [email.strip() for email in self.recipients if email.strip()]

        # Email configuration
        self.sender_name = os.getenv('NEWSLETTER_SENDER_NAME', 'Newsletter Sender')
        self.sender_email = os.getenv('NEWSLETTER_SENDER_EMAIL')
        if not self.sender_email:
            raise GmailAPIError("NEWSLETTER_SENDER_EMAIL not found in environment")

        self.subject_template = os.getenv('NEWSLETTER_SUBJECT_TEMPLATE',
                                         'AI Newsletter: {{topic}} - {{date}}')
        self.include_html_alternative = os.getenv('INCLUDE_HTML_ALTERNATIVE', 'true').lower() == 'true'

        # Initialize Gmail service
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """
        Get or create Gmail API service with OAuth2 authentication.

        Returns:
            Gmail API service object

        Raises:
            GmailAPIError: If authentication fails
        """
        creds = None

        # Check if token file exists and is valid
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_info(
                    json.load(open(self.token_file, 'r', encoding='utf-8')),
                    scopes=GMAIL_SCOPES
                )
            except Exception as e:
                print(f"Warning: Could not load existing credentials: {str(e)}")
                creds = None

        # If no valid credentials, run OAuth2 flow
        if not creds or not creds.valid:
            if not os.path.exists(self.credentials_file):
                raise GmailAPIError(
                    f"Credentials file not found: {self.credentials_file}. "
                    "Please set up Google OAuth2 credentials first."
                )

            try:
                # Create OAuth2 flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    GMAIL_SCOPES
                )

                # Run local server for OAuth2
                creds = flow.run_local_server(
                    port=8080,
                    authorization_prompt_message=(
                        "Please authenticate your Gmail account "
                        "in the browser that opened."
                    )
                )

                # Save credentials for future use
                os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
                with open(self.token_file, 'w', encoding='utf-8') as token:
                    token.write(json.dumps(creds.to_json()))

                print("Authentication successful! Credentials saved.")

            except Exception as e:
                raise GmailAPIError(f"OAuth2 authentication failed: {str(e)}")

        try:
            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds, static_discovery=False)
            return service
        except Exception as e:
            raise GmailAPIError(f"Failed to create Gmail service: {str(e)}")

    def create_message(self, to: str, subject: str, html_content: str,
                      text_content: Optional[str] = None) -> Dict[str, str]:
        """
        Create email message.

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text alternative (optional)

        Returns:
            Dictionary with raw message and headers

        Raises:
            GmailAPIError: If message creation fails
        """
        # Create message headers
        message_headers = [
            f'From: {self.sender_name} <{self.sender_email}>',
            f'To: {to}',
            f'Subject: {subject}',
            'MIME-Version: 1.0',
            'Content-Type: multipart/alternative; boundary="boundary123"'
        ]

        # Create message parts
        message_parts = [
            '--boundary123\n',
            'Content-Type: text/plain; charset=UTF-8\n\n',
            f'{text_content or self._create_text_alternative(html_content)}\n',
            '\n--boundary123\n',
            'Content-Type: text/html; charset=UTF-8\n\n',
            f'{html_content}\n',
            '\n--boundary123--\n'
        ]

        # Combine headers and parts
        message = '\n'.join(message_headers + message_parts)

        # Encode message in base64
        raw_message = base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8')

        return {
            'raw': raw_message,
            'to': to,
            'subject': subject,
            'headers': message_headers
        }

    def _create_text_alternative(self, html_content: str) -> str:
        """
        Create plain text alternative from HTML content.

        Args:
            html_content: HTML content

        Returns:
            Plain text version
        """
        # Basic HTML to text conversion
        text = re.sub(r'<[^>]+>', '', html_content)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        return text.strip()

    def send_message(self, to: str, subject: str, html_content: str,
                    text_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email via Gmail API.

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text alternative (optional)

        Returns:
            Dictionary with message ID and status

        Raises:
            GmailAPIError: If sending fails
        """
        try:
            # Create message
            message = self.create_message(to, subject, html_content, text_content)

            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            return {
                'success': True,
                'message_id': sent_message.get('id'),
                'thread_id': sent_message.get('threadId'),
                'to': to,
                'subject': subject,
                'sent_at': datetime.now().isoformat(),
                'raw_message': message
            }

        except HttpError as e:
            error_details = e.content.decode('utf-8')
            raise GmailAPIError(f"Gmail API HTTP error: {str(e)}\nDetails: {error_details}")
        except Exception as e:
            raise GmailAPIError(f"Failed to send email: {str(e)}")

    def send_newsletter(self, newsletter_data: Dict[str, Any],
                       recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send newsletter to recipients.

        Args:
            newsletter_data: Newsletter data with HTML content and metadata
            recipients: List of recipients (uses config if None)

        Returns:
            Dictionary with send results and statistics
        """
        # Use provided recipients or config
        target_recipients = recipients or self.recipients

        if not target_recipients:
            raise GmailAPIError("No recipients specified")

        # Get newsletter content and metadata
        html_content = newsletter_data.get('html_content', '')
        metadata = newsletter_data.get('metadata', {})

        # Generate subject
        topic = metadata.get('topic', 'Newsletter')
        subject = self.subject_template.replace('{{topic}}', topic)
        subject = subject.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))

        # Create text alternative if needed
        text_content = None
        if self.include_html_alternative:
            text_content = self._create_text_alternative(html_content)

        # Send to each recipient
        results = {
            'newsletter_topic': topic,
            'sender': self.sender_email,
            'recipients': [],
            'successful_sends': 0,
            'failed_sends': 0,
            'errors': [],
            'send_timestamp': datetime.now().isoformat(),
            'subject': subject
        }

        for recipient in target_recipients:
            try:
                print(f"Sending newsletter to: {recipient}")

                result = self.send_message(recipient, subject, html_content, text_content)

                results['recipients'].append({
                    'email': recipient,
                    'message_id': result.get('message_id'),
                    'thread_id': result.get('thread_id'),
                    'status': 'sent',
                    'sent_at': result.get('sent_at')
                })

                results['successful_sends'] += 1

            except GmailAPIError as e:
                error_info = {
                    'email': recipient,
                    'error': str(e),
                    'status': 'failed'
                }

                results['recipients'].append(error_info)
                results['failed_sends'] += 1
                results['errors'].append(error_info)

                print(f"Failed to send to {recipient}: {str(e)}")

        return results

    def create_draft(self, to: str, subject: str, html_content: str,
                    text_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Create email draft instead of sending directly.

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text alternative (optional)

        Returns:
            Dictionary with draft ID and status
        """
        try:
            # Create message
            message = self.create_message(to, subject, html_content, text_content)

            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()

            return {
                'success': True,
                'draft_id': draft.get('id'),
                'thread_id': draft.get('threadId'),
                'to': to,
                'subject': subject,
                'created_at': datetime.now().isoformat(),
                'raw_message': message
            }

        except HttpError as e:
            error_details = e.content.decode('utf-8')
            raise GmailAPIError(f"Gmail API HTTP error: {str(e)}\nDetails: {error_details}")
        except Exception as e:
            raise GmailAPIError(f"Failed to create draft: {str(e)}")

def main():
    """CLI interface for the Gmail tool."""
    if len(sys.argv) < 2:
        print("Usage: python send_email.py <html_file> [recipients_file] [draft_mode]")
        print("Example: python send_email.py newsletter.html recipients.txt")
        print("         python send_email.py newsletter.html recipients.txt draft")
        return

    html_file = sys.argv[1]
    recipients_file = sys.argv[2] if len(sys.argv) > 2 else None
    draft_mode = len(sys.argv) > 3 and sys.argv[3].lower() == 'draft'

    try:
        # Load HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Load recipients from file if provided
        recipients = []
        if recipients_file and os.path.exists(recipients_file):
            with open(recipients_file, 'r', encoding='utf-8') as f:
                for line in f:
                    email = line.strip()
                    if email and '@' in email:
                        recipients.append(email)

        # Create email tool
        email_tool = GmailEmailTool()

        # Create metadata
        metadata = {
            'topic': os.getenv('NEWSLETTER_TOPIC', 'AI Trends Newsletter'),
            'generated_at': datetime.now().isoformat(),
            'source_file': html_file
        }

        newsletter_data = {
            'html_content': html_content,
            'metadata': metadata
        }

        # Send or draft
        if draft_mode:
            print("Creating draft instead of sending...")

            if len(sys.argv) < 3:
                print("Error: Recipient required for draft mode")
                return 1

            recipient = sys.argv[3] if len(sys.argv) > 3 else recipients[0] if recipients else None

            if not recipient:
                print("Error: No recipient specified")
                return 1

            result = email_tool.create_draft(
                to=recipient,
                subject=f"Newsletter Draft: {metadata['topic']}",
                html_content=html_content
            )

            print(f"Draft created successfully!")
            print(f"Draft ID: {result.get('draft_id')}")
            print(f"Thread ID: {result.get('thread_id')}")

        else:
            print("Sending newsletter...")

            results = email_tool.send_newsletter(newsletter_data, recipients)

            print(f"\n=== Send Results ===")
            print(f"Topic: {results['newsletter_topic']}")
            print(f"Sender: {results['sender']}")
            print(f"Subject: {results['subject']}")
            print(f"Successful sends: {results['successful_sends']}")
            print(f"Failed sends: {results['failed_sends']}")

            if results['errors']:
                print(f"\n=== Errors ===")
                for error in results['errors']:
                    print(f"{error['email']}: {error['error']}")

    except GmailAPIError as e:
        print(f"Gmail API Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    import re
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    exit(main())