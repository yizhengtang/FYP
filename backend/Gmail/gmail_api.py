import os
import base64

#Email mime modules for creating and formatting email messages in Python. Provide classes for handling different parts of an email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from Google_apis import create_gmail_service

def initialize_gmail_service(api_name = 'gmail', api_version = 'v1', scopes = ['https://mail.google.com/']):
    service = create_gmail_service(api_name, api_version, scopes)
    return service

#Helper function to extract the body from email payload (data structure in email messages that contains the actual content of the email) (body text, headers, attachments ...)
def extract_body(payload):

    #Default body: no text body is found
    body = '<Text body not available>'

    #Checks if parts or body exists in the payload
    #Gmail API structures email content in parts, especially for multipart emails (HTML + plain text)
    #Sometimes it can have nested parts, Base64 encoded content.
    #Multipart emails are the most common format used today, in this loop it will iterate through the parts to find the plain text version of the email body.
    if 'parts' in payload:
        for part in payload['parts']:
            
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                        break

            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break

    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return body

#Function to get email messages from Gmail API service, user_id represents the user account.
#This function WILL ONLY fetch email_id and email thread ID.
def get_email_messages(service, user_id='me', label_ids = None, folder_name = 'INBOX', max_results=5):
    #Create a list to store email messages.
    messages = []
    #Use for pagination
    next_page_token = None

    #Checks if the provided folder name exists.
    if folder_name:
        #Get all the user's gmail labels into a variable call label_results.
        label_results = service.users().labels().list(userId=user_id).execute()
        #Then from the label results, extract the labels into a list called labels.
        labels = label_results.get('labels', [])

        #Here I created a folder_label_id variable that uses a list comprehension to find the label ID that matches the provided folder name with case insensitivity.
        folder_label_id = next((label['id'] for label in labels if label['name'].lower() == folder_name.lower()), None)
        if folder_label_id:
            if label_ids:
                label_ids.append(folder_label_id)
            else:
                label_ids = [folder_label_id]
        else:
            raise ValueError(f'Folder name "{folder_name}" not found.')

    #This while loop will continue fetching email messages until maximum results is reached or no more messages left.    
    while True:

        #Messages list method to retrieve email messages from the user's inbox.
        #Can fetch up to 500 messages per API call, so I limit the max results to 500.
        #Store the result of the API call in a variable call result.  
        result = service.users().messages().list(
            userId=user_id,
            labelIds=label_ids,
            pageToken=next_page_token,
            maxResults=min(500, max_results - len(messages)) if max_results else 500
        ).execute()

        #After the API call, extend the messages list with the retrieved messages from the result.
        #Then update the next_page_token to get the next set of messages in the next iteration.
        messages.extend(result.get('messages', []))
        next_page_token = result.get('nextPageToken')
        
        #Here is an if statement to break the loop if (1. No next page token 2. Reached the maximum number of messages specified)
        if not next_page_token or (max_results and len(messages) >= max_results):
            break
    
    #After the loop ends, return the messages list, slicing it to the specified max results.
    #This ensures we return the exact number of messages requested even if we retrieve more due to the batching process.
    return messages[:max_results] if max_results else messages   

#This function will retrieve the full details of a specific email.
#Takes in message_id as a parmeter to identify the email to fetch.
def get_email_message_details(service, message_id, user_id='me'):
    #Use the Gmail API to get the full details of a specific email message using its unique message ID.
    #Using the provided message_id and format 'full' to get all details of the email.
    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()

    #From the response, extract the payload from the message and retrieve the headers.
    #Headers contain improtant metadata such as subject, sender, recipient, date.
    payload = message['payload']
    headers = payload.get('headers', [])

    #Here use list comprehension to find the header with teh name "subject" and extracct it's value.
    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), None)
    if not subject:
        subject = message.get('subject', 'No subject')

    #Extract all otther metadata with similar approach here.
    sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown sender')
    recipient = next((header['value'] for header in headers if header['name'].lower() == 'to'), 'Unknown recipient(s)')
    snippet = message.get('snippet', 'No snippet available')
    thread_id = message.get('threadId', message_id)
    has_attachments = any(part.get('filename') for part in payload.get('parts', []) if part.get('filename'))
    date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'No date available')
    star = message.get('labelIds', []).count('STARRED') > 0
    label = ' , '.join(message.get('labelIds', []))

    #Using the extract_body function to get the body content from the email payload.
    body = extract_body(payload)

    email_details = {
        'id': message_id,
        'subject': subject,
        'from': sender,
        'to': recipient,
        'snippet': snippet,
        'thread_id': thread_id,
        'body': body,
        'has_attachments': has_attachments,
        'date': date,
        'starred': star,
        'label': label
    }
    return email_details 

def send_email_with_attachment(service, to, subject, body, body_type='plain', attachment_paths=None):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject

    if body_type.lower() not in ['plain', 'html']:
        raise ValueError("body_type must be either 'plain' or 'html'")
    
    message.attach(MIMEText(body, body_type.lower()))

    if attachment_paths:
        for attachment_path in attachment_paths:
            if os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)

                with open(attachment_path, 'rb') as attachment_file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment_file.read())

                encoders.encode_base64(part)

                part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
                
                message.attach(part)

            else:
                raise FileNotFoundError(f"Attachment file '{attachment_path}' not found.")
            
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
