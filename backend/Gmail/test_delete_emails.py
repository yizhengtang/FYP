from gmail_api import initialize_gmail_service, trash_email, untrash_email_in_batch, empty_trash

service = initialize_gmail_service()

emails_to_trash = ['19bf267376d43593']

for email_id in emails_to_trash:
    try:
        trash_email(service, 'me', email_id)
        print
        print(f"Email with ID: {email_id} has been moved to Trash.")
    except Exception as e:
        print(f"Failed to trash email with ID: {email_id}. Error: {e}")

try:
    empty_trash_response = empty_trash(service)
    print(f"Emptied trash. Total messages deleted: {empty_trash_response}")

except Exception as e:
    print(f"Failed to empty Trash. Error: {e}")