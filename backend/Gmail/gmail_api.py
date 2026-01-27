import os
import base64

#Email mime modules for creating and formatting email messages in Python. Provide classes for handling different parts of an email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from Google_API import create_gmail_service

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

#This function will send an email with attachments.
def send_email_with_attachment(service, to, subject, body, body_type='plain', attachment_paths=None):
    #First create the email, by creating a MIMEMultipart object to represent the email message that is about to send.
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject

    #Validates the body_type input, ensures that it is either plain or HTML.
    if body_type.lower() not in ['plain', 'html']:
        raise ValueError("body_type must be either 'plain' or 'html'")
    
    #Attach the email body to the message object using MIMEText, along by specifying the body type.
    message.attach(MIMEText(body, body_type.lower()))

    #This block will check for the attachment paths provided.
    if attachment_paths:
        #Iterate through each attachment path to attach files to the email.
        for attachment_path in attachment_paths:
            #For each attachment found, first check if the file exists.
            if os.path.exists(attachment_path):
                #Extract the filename.
                filename = os.path.basename(attachment_path)

                #Open the file in binary read mode (rb) to read it's content.
                with open(attachment_path, 'rb') as attachment_file:
                    #Creates a MIME part with type application/octet-stream, which is a generic binary file type.
                    part = MIMEBase('application', 'octet-stream')
                    #Reads the entire file and set it as the payload.
                    part.set_payload(attachment_file.read())

                #NExt step is to encode the payload using Base64 encoding.
                #This ensures the data remains safe during email transmission.
                encoders.encode_base64(part)

                #THen add a header to the attachment part to indicate it's an attachment with the filename.   
                part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
                
                #After everything attach the part to the main message object.
                message.attach(part)

            else:
                raise FileNotFoundError(f"Attachment file '{attachment_path}' not found.")

    #First encode the entire message as a url save base64 string.        
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    #Use the Gmail API to send the email message.
    sent_message = service.users().messages().send(
        userId='me',
        body={'raw': raw_message}
    ).execute()

    return sent_message

#This download function will download attachments from a specific email message.
def download_attachments(service, user_id, message_id, download_dir):
    #Fetch the full email message using the provided message ID.
    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
    payload = message.get('payload', {})
    parts = payload.get('parts', [])

    #Ensure the download directory exists, if not create it.
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    #Iterate through the parts of the email to find attachments.
    for part in parts:
        filename = part.get('filename')
        body = part.get('body', {})
        attachment_id = body.get('attachmentId')

        #If an attachment is found (filename and attachment ID exist)
        if filename and attachment_id:
            #Use the Gmail API to fetch the attachment data using the attachment ID.
            attachment = service.users().messages().attachments().get(
                userId=user_id,
                messageId=message_id,
                id=attachment_id
            ).execute()

            #Decode the Base64 encoded attachment data.
            file_data = base64.urlsafe_b64decode(attachment.get('data', '').encode('UTF-8'))

            #Define the full path to save the attachment.
            file_path = os.path.join(download_dir, filename)

            #Write the decoded data to a file in binary mode.
            with open(file_path, 'wb') as f:
                f.write(file_data)

            print(f"Attachment '{filename}' downloaded to '{file_path}'")
            
#This download all function will download attachments from all emails in a thread.
def download_attachments_all(service, user_id, message_id, download_dir):
    thread = service.users().threads().get(userId=user_id, id=message_id).execute()
    messages = thread.get('messages', [])
    for msg in messages:
        download_attachments(service, user_id, msg['id'], download_dir)
    gmail_service = service.users().messages()
    return gmail_service
        
#This function will try to look for individual emails.
def search_emails(service, query, user_id='me', max_results=5):
    messages = []
    next_page_token = None

    #THis while loop will continue fetching email messages until the maximum results is reached or no more messages left.
    while True:
        result = service.users().messages().list(
            userId=user_id,
            q=query,
            pageToken=next_page_token,
            maxResults=min(500, max_results - len(messages)) if max_results else 500
        ).execute()

        messages.extend(result.get('messages', []))
        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(messages) >= max_results):
            break

    return messages[:max_results] if max_results else messages

#This function will return the entire thread for emails that matches the query string.
def search_email_conversations(service, query, user_id='me', max_results=5):
    threads = []
    next_page_token = None

    while True:
        result = service.users().threads().list(
            userId=user_id,
            q=query,
            pageToken=next_page_token,
            maxResults=min(500, max_results - len(threads)) if max_results else 500
        ).execute()

        threads.extend(result.get('threads', []))
        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(threads) >= max_results):
            break

    return threads[:max_results] if max_results else threads

#This function will create a new label.
def create_label(service, name, label_list_visibility='labelShow', message_list_visibility='show'):
    label = {
        'name': name,
        #LabelListVisibility controls whether the label is shown in the label list in the web app, messageListVisibility controls whether the label is showing in an email message.
        'labelListVisibility': label_list_visibility,
        'messageListVisibility': message_list_visibility
    }
    created_label = service.users().labels().create(userId='me', body=label).execute()
    return created_label

#This function will list all labels.
def list_labels(service, user_id='me'):
    results = service.users().labels().list(userId=user_id).execute()
    labels = results.get('labels', [])
    return labels

#Thius function will get details for a specific label by ID.
def get_label_details(service, label_id, user_id='me'):
    label = service.users().labels().get(userId=user_id, id=label_id).execute()
    return label

#This function will modify an existing label.
def modify_labels(service, label_id, **updates):
    label = service.users().labels().get(userId='me', id=label_id).execute()
    for key, value in updates.items():
        label[key] = value
    updated_label = service.users().labels().update(userId='me', id=label_id, body=label).execute()
    return updated_label

#Tjis function will delete a label by ID.
def delete_label(service, label_id, user_id='me'):
    service.users().labels().delete(userId=user_id, id=label_id).execute()
    return f'Label with ID {label_id} deleted successfully.'

#Helper function to map label ID using given label name.
def map_label_name_to_id(service, label_name, user_id='me'):
    labels = list_labels(service, user_id)
    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']
    return None

#This function will add/delete labels from a specific email message.
def modify_email_labels(service, user_id, message_id, add_labels = None, remove_labels = None):
    #this function will process labels in batches to avoid exceeding API limits.
    def batch_labels(labels, batch_size = 100):
        return [labels[i:i + batch_size] for i in range(0, len(labels), batch_size)]
    if add_labels:
        for batch in batch_labels(add_labels):
            service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={'addLabelIds': batch}
            ).execute()

    if remove_labels:
        for batch in batch_labels(remove_labels):
            service.users().messages().modify(
                userId=user_id,
                id=message_id,
                body={'removeLabelIds': batch}
            ).execute()

    return f'Labels modified for message ID {message_id}.'

#This function will trash a specific email.
def trash_email(service, user_id, message_id):
    service.users().messages().trash(userId=user_id, id=message_id).execute()
    return f'Message ID {message_id} moved to trash.'

#This function allows trashing multiple emails by batch.
def trash_email_in_batch(service, user_id, message_ids):
    batch = service.new_batch_http_request()
    for message_id in message_ids:
        batch.add(service.users().messages().trash(userId=user_id, id=message_id))
    batch.execute()
    return f'Trashed {len(message_ids)} messages.'

#This function will untrash a specific email.
def untrash_email(service, user_id, message_id):
    service.users().messages().untrash(userId=user_id, id=message_id).execute()
    return f'Message ID {message_id} untrashed.'

#This function will untrash multiple emails by batch.
def untrash_email_in_batch(service, user_id, message_ids):
    batch = service.new_batch_http_request()
    for message_id in message_ids:
        batch.add(service.users().messages().untrash(userId=user_id, id=message_id))
    batch.execute()

    return f'Untrashed {len(message_ids)} messages.'

#This function permanently deletes an email.
def delete_email(service, user_id, message_id):
    service.users().messages().delete(userId=user_id, id=message_id).execute()
    return f'Message ID {message_id} deleted successfully.'

def empty_trash(service):
    page_token = None
    total_deleted = 0

    while True:
        response = service.users().messages().list(
            userId= 'me',
            q='in:trash',
            pageToken=page_token,
            maxResults=500
        ).execute()

        messages = response.get('messages', [])
        if not messages:
            break

        batch = service.new_batch_http_request()
        for message in messages:
            batch.add(service.users().messages().delete(userId='me', id=message['id']))
        batch.execute()

        total_deleted += len(messages)

        page_token = response.get('nextPageToken')
        if not page_token:
            break
    return total_deleted

#This function will create a draft email message.
#The function is pretty much like the send email function, but instead of sending the email, it saves it as a draft.
#Create draft is done by using the drafts.create method from the Gmail API.
def create_draft_email(service, to, subject, body, body_type='plain', attachment_paths=None):
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

    draft = service.users().drafts().create(
        userId='me',
        body={'message': {'raw': raw_message}}
    ).execute()

    return draft
    
#This function will list all draft email messages.
#Use while loop to fetch the draft emails in the draft folder using the drafts list method.
#Breaks when mac results is reached or nextpagetoken returns none.
def list_draft_email_messages(service, user_id='me', max_results=5):
    drafts = []
    next_page_token = None

    while True:
        result = service.users().drafts().list(
            userId=user_id,
            pageToken=next_page_token,
            maxResults=min(500, max_results - len(drafts)) if max_results else 500
        ).execute()

        drafts.extend(result.get('drafts', []))
        next_page_token = result.get('nextPageToken')

        if not next_page_token or (max_results and len(drafts) >= max_results):
            break

    return drafts[:max_results] if max_results else drafts

#This function will get the detail of a specific draft email by ID.
#Also pretty much same as the get email message details function, but instead this uses the drafts.get method to get the draft email details.
#Return the draft details in a dictionary format.
def get_draft_email_details(service, draft_id, format='full'):
    draft_detail = service.users().drafts().get(userId='me', id=draft_id, format=format).execute()
    draft_id = draft_detail['id']
    draft_message = draft_detail['message']
    draft_payload = draft_message['payload']
    headers = draft_payload.get('headers', [])
    subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), None)
    if not subject:
        subject = draft_message.get('subject', 'No subject')
    sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown sender')
    recipient = next((header['value'] for header in headers if header['name'].lower() == 'to'), 'Unknown recipient(s)')
    snippet = draft_message.get('snippet', 'No snippet available')
    thread_id = draft_message.get('threadId', draft_id)
    has_attachments = any(part.get('filename') for part in draft_payload.get('parts', []) if part.get('filename'))
    date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'No date available')
    star = draft_message.get('labelIds', []).count('STARRED') > 0
    label = ' , '.join(draft_message.get('labelIds', []))

    body = '<Text body not available>'
    if 'parts' in draft_payload:
        for part in draft_payload['parts']:
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8')
                        break
            elif part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break

    draft_details = {
        'subject': subject,
        'from': sender,
        'to': recipient,
        'body': body,
        'snippet': snippet,
        'has_attachments': has_attachments,
        'date': date,
        'starred': star,
        'label': label
    }
    return draft_details

#This function will send a draft email by ID.
#This is also similar to the send email function, but instead this uses the drafts.send method for sending a draft message.
def send_draft_email(service, draft_id):
    draft = service.users().drafts().send(userId='me', body={'id': draft_id}).execute()
    return draft

#This function deletes a draft email by ID.
#Similar to delete email function, but instead it uses the drafts.delete method to delete a draft email.
def delete_draft_email(service, draft_id):
    service.users().drafts().delete(userId='me', id=draft_id).execute()
    return f'Draft ID {draft_id} deleted successfully.'