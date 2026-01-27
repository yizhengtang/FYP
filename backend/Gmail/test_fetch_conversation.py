from gmail_api import initialize_gmail_service, search_emails, get_email_conversations

service = initialize_gmail_service()

message_id = '19a3528511363e9e'
message_conversations = get_email_conversations(service, message_id)

print(f"\nFetching conversations for email ID: {message_id}\n")
for conversation in message_conversations:
    print(f"Conversation ID: {conversation['id']}")
    print(f"sender: {conversation['from']}")
    print(f"recipient: {conversation['to']}")
    print(f"subject: {conversation['subject']}")
    print(f"body: {conversation['body']}")
    print(f"date: {conversation['date']}")
    print("-" * 80)