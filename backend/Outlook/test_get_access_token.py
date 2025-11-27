from Microsoft_API import get_access_token
import os
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv('MICROSOFT_CLIENT_ID')
APP_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')

scopes = ['User.Read', 'Mail.ReadWrite', 'Mail.Send']

try:
    access_token = get_access_token(app_id = APP_ID, client_secret = APP_SECRET, scopes = scopes)
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    print(headers)
except Exception as e:
    print (f"Error: {e}")