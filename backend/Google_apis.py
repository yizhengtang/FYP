import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#First function: Create a gmail service, takes in four parameters.
#Handles the creation of service objects for different Google APIs.

#client_secret_file: Path to the client secret file, contains credentials for the google application.
#api_name: Name of the Google API to connect to (e.g., 'gmail').
#api_version: Version of the API to use (e.g., 'v1').
#scopes: Define the level of access the application is requesting.

def create_gmail_service(client_secret_file, api_name, api_version, *scopes, prefix =''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERCE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    #Creates token file that stores unique token for Gmail API services.
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token_files'
    token_file = f'token_{API_SERCE_NAME}_{API_VERSION}{prefix}.json'

    #Check if the token file directory exists.
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    #Look for existing token, if nto found then create a new one by going through the OUAth flow.
    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES) 

    #This statement checks if the credentials are valid, it can be either expired or mising. If expired, it automatically refreshes one, if missingm it goes through the OAuth flow.    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERCE_NAME, API_VERSION, credentials=creds)
        print(f'{API_SERCE_NAME} service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create servicw instance for {API_SERCE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None