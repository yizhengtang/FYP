import marimo as mo
from pathlib import Path
from gmail_api import send_email_with_attachment, initialize_gmail_service

service = initialize_gmail_service()

to_address = "yzhengtang4@gmail.com"
subject = "Test Email with Attachment"
body = "This is a test email sent from the Gmail API with an attachment."
attachment_dir = Path('./attachments')
attachment_files = list(attachment_dir.glob('*'))

try:
    send_email_with_attachment(service, to_address, subject, body, body_type='plain', attachment_paths=attachment_files)
    print("Email sent successfully with attachments.")
except Exception as e:
    print(f"Failed to send email: {e}")