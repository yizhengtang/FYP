from gmail_api import initialize_gmail_service, get_email_message_details, search_emails, search_email_conversations

service = initialize_gmail_service()

query = 'security'
emails = search_emails(service, query, max_results=5)

print(f"\nFetching details for {len(emails)} emails matching query: '{query}'\n")
for email in emails:
    details = get_email_message_details(service, email['id'])

    print(f"Email ID: {details['id']}")
    print(f"Thread ID: {details['thread_id']}")
    print(f"From: {details['from']}")
    print(f"To: {details['to']}")
    print(f"Subject: {details['subject']}")
    print(f"Body: {details['body']}")
    print(f"Date: {details['date']}")
    print(f"Snippet: {details['snippet']}")
    print(f"Starred: {details['starred']}")
    print(f"Has Attachments: {details['has_attachments']}")
    print(f"Labels: {details['label']}")
    print("-" * 80)