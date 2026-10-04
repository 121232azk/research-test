#!/usr/bin/env python3
"""
Send slide deck via Gmail API.

This tool sends a PowerPoint or Google Slides presentation via Gmail API with OAuth2 authentication.
"""

import json
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

class GmailSlideDeckError(Exception):
    """Custom exception for Gmail slide deck sending errors."""
    pass

class GmailSlideDeckSender:
    def __init__(self):
        # Load credentials and configuration
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', './credentials.json')
        self.token_file = os.getenv('TOKEN_FILE', './token.json')
        self.recipients = os.getenv('SLIDE_DECK_RECIPIENTS', '').split(',')
        self.recipients = [email.strip() for email in self.recipients if email.strip()]

        # Email configuration
        self.sender_name = os.getenv('SLIDE_DECK_SENDER_NAME', 'AI Insights Team')
        self.sender_email = os.getenv('SLIDE_DECK_SENDER_EMAIL')
        if not self.sender_email:
            raise GmailSlideDeckError("SLIDE_DECK_SENDER_EMAIL not found in environment")

        self.subject_template = os.getenv('SLIDE_DECK_SUBJECT_TEMPLATE',
                                         'Trading News Analysis: {{topic}} - {{date}}')

        # Initialize Gmail service
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """
        Get or create Gmail API service with OAuth2 authentication.

        Returns:
            Gmail API service object

        Raises:
            GmailSlideDeckError: If authentication fails
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
                raise GmailSlideDeckError(
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
                raise GmailSlideDeckError(f"OAuth2 authentication failed: {str(e)}")

        try:
            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds, static_discovery=False)
            return service
        except Exception as e:
            raise GmailSlideDeckError(f"Failed to create Gmail service: {str(e)}")

    def create_message(self, to: str, subject: str, slide_deck_path: str) -> Dict[str, str]:
        """
        Create email message with slide deck attachment.

        Args:
            to: Recipient email address
            subject: Email subject
            slide_deck_path: Path to slide deck file

        Returns:
            Dictionary with raw message and headers

        Raises:
            GmailSlideDeckError: If message creation fails
        """
        try:
            # Read slide deck file
            with open(slide_deck_path, 'rb') as f:
                slide_deck_data = f.read()

            # Encode slide deck in base64
            slide_deck_b64 = base64.urlsafe_b64encode(slide_deck_data).decode('utf-8')

            # Create message headers
            message_headers = [
                f'From: {self.sender_name} <{self.sender_email}>',
                f'To: {to}',
                f'Subject: {subject}',
                'MIME-Version: 1.0',
                'Content-Type: multipart/mixed; boundary="boundary123"'
            ]

            # Create message parts
            message_parts = [
                '--boundary123\n',
                'Content-Type: text/plain; charset=UTF-8\n\n',
                f'Please find attached the trading news analysis slide deck: {subject}\n',
                '\n--boundary123\n',
                'Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation\n',
                'Content-Disposition: attachment; filename="trading_news_analysis.pptx"\n',
                'Content-Transfer-Encoding: base64\n\n',
                f'{slide_deck_b64}\n',
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

        except Exception as e:
            raise GmailSlideDeckError(f"Failed to create email message: {str(e)}")

    def send_slide_deck(self, slide_deck_path: str, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send slide deck to recipients via Gmail.

        Args:
            slide_deck_path: Path to slide deck file
            recipients: List of recipients (uses config if None)

        Returns:
            Dictionary with send results and statistics

        Raises:
            GmailSlideDeckError: If sending fails
        """
        # Use provided recipients or config
        target_recipients = recipients or self.recipients

        if not target_recipients:
            raise GmailSlideDeckError("No recipients specified")

        # Generate subject
        topic = os.path.basename(slide_deck_path)
        subject = self.subject_template.replace('{{topic}}', topic)
        subject = subject.replace('{{date}}', datetime.now().strftime('%B %d, %Y'))

        # Send to each recipient
        results = {
            'slide_deck': topic,
            'sender': self.sender_email,
            'recipients': [],
            'successful_sends':  Keynote
            'failed_sends': 0,
            'errors': [],
            'send_timestamp': datetime.now().isoformat(),
            'subject': subject
        }

        for recipient in target_recipients:
            try:
                print(f"Sending slide deck to: {recipient}")

                # Create message
                message = self.create_message(recipient, subject, slide_deck_path)

                # Send message
                sent_message = self.service.users().messages().send(
                    userId='me',
                    body={'raw': message['raw']}
                ).execute()

                results['recipients'].append({
                    'email': recipient,
                    'message_id': sent_message.get('id'),
                    'thread_id': sent_message.get('threadId'),
                    'status': 'sent',
                    'sent_at': datetime.now().isoformat()
                })

                results['successful_sends'] += 1

            except HttpError as e:
                error_details = e.content.decode('utf-8')
                error_info = {
                    'email': recipient,
                    'error': f"Gmail API HTTP error: {str(e)}\nDetails: {error_details}",
                    'status': 'failed'
                }

                results['recipients'].append(error_info)
                results['failed_sends'] += 1
                results['errors'].append(error_info)

                print(f"Failed to send to {recipient}: {str(e)}")
            except Exception as e:
                error_info = {
                    'email': recipient,
                    'error': f"Failed to send email: {str(e)}",
                    'status': 'failed'
                }

                results['recipients'].append(error_info)
                results['failed_sends'] += 1
                results['errors'].append(error_info)

                print(f"Failed to send to {recipient}: {str(e)}")

        return results

    def create_draft(self, to: str, subject: str, slide_deck_path: str) -> Dict[str, Any]:
        """
        Create email draft with slide deck attachment.

        Args:
            to: Recipient email address
            subject: Email subject
            slide_deck_path: Path to slide deck file

        Returns:
            Dictionary with draft ID and status

        Raises:
            GmailSlideDeckError: If draft creation fails
        """
        try:
            # Create message
            message = self.create_message(to, subject, slide_deck_path)

            # Create draft
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': message['raw']}}
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
            raise GmailSlideDeckError(f"Gmail API HTTP error: {str(e)}\nDetails: {error_details}")
        except Exception as e:
            raise GmailSlideDeckError(f"Failed to create draft: {str(e)}")

def main():
    """CLI interface for the slide deck sending tool."""
    if len(sys.argv) < 2:
        print("Usage: python send_slide_deck.py <slide_deck_file> [recipients_file] [draft_mode]")
        print("Example: python send_slide_deck.py slide_deck.pptx recipients.txt")
        print("         python send_slide_deck.py slide_deck.pptx recipients.txt draft")
        return

    slide_deck_file = sys.argv[1]
    recipients_file = sys.argv[2] if len(sys.argv) > 2 else None
    draft_mode = len(sys.argv) > 3 and sys.argv[3].lower() == 'draft'

    try:
        # Check if slide deck file exists
        if not os.path.exists(slide_deck_file):
            raise GmailSlideDeckError(f"Slide deck file not found: {slide_deck_file}")

        # Load recipients optional = recipients_file:
            with open(recipients_file, 'r', encoding='utf-8') as f:
                for line in f:
                    email = line.strip()
                    if email and '@' in email:
                        recipients.append(email)

        # Create email tool
        email_tool = GmailSlideDeckSender()

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
                subject=f"Trading News Analysis: {os.path.basename(slide_deck_file)}",
                slide_deck_path=slide_deck_file
            )

            print(f"Draft created successfully!")
            print(f"Draft ID: {result.get('draft_id')}")
            print(f"Thread ID: {result.get('thread_id')}")

        else:
            print("Sending slide deck...")

            results Mounted as DefinedRemotePart by *mount*, not a filesystem path. Cannot read.

        except GmailSlideDeckError as e:
            print(f"Gmail API Error: {str(e)}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return 1

        return 0

if __name__ == "__main__":
    import sys
    exit(main())