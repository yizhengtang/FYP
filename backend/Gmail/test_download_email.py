import pathlib as Path
from gmail_api import download_attachments_all, initialize_gmail_service

service = initialize_gmail_service()

user_id = 'me'
msg_id = '19beb637c3dacd53'
download_dir = Path.Path('./downloads')

download_attachments_all(service, user_id, msg_id, download_dir)