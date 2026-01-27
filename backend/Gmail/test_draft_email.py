from pathlib import Path
from gmail_api import initialize_gmail_service, create_draft_email, list_draft_email_messages, get_draft_email_details

service = initialize_gmail_service()

to_address = "yzhengtang4@gmail.com"
subject = "Test Draft Email"
body = "This is a test draft email created using the Gmail API."
attachment_dir = Path('./attachments')
attachment_files = list(attachment_dir.glob('*'))

draft_email_response = create_draft_email(
    service,
    to_address,
    subject,
    body,
    body_type='plain',
    attachment_paths=attachment_files
)
print(f"Draft email created with ID: {draft_email_response['id']}")

