from gmail_api import initialize_gmail_service, trash_email, untrash_email_in_batch

service = initialize_gmail_service()

emails_to_trash = ['19b21d7c231a760d', '19b21a7faeff8779', '19b1fe92a11d1612']

for email_id in emails_to_trash:
    try:
        trash_email(service, 'me', email_id)
        print(f"Email with ID: {email_id} has been moved to Trash.")
    except Exception as e:
        print(f"Failed to trash email with ID: {email_id}. Error: {e}")

for email_id in emails_to_trash:
    try:
        untrash_email_in_batch(service, 'me', [email_id])
        print(f"Email with ID: {email_id} has been restored from Trash.")
    except Exception as e:
        print(f"Failed to untrash email with ID: {email_id}. Error: {e}")