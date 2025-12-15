#This script handles the creation of Gmail service objects using OAuth2 authentication.
import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#This script will use the variables defined for the client credentials from the .env file. SO here we load them.
load_dotenv()

#First function: Create a gmail service, takes in four parameters.
#Handles the creation of service objects for different Google APIs.

#api_name: Name of the Google API to connect to (e.g., 'gmail').
#api_version: Version of the API to use (e.g., 'v1').
#scopes: Define the level of access the application is requesting.
def create_gmail_service(api_name, api_version, *scopes, prefix =''):
    API_SERCE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    #Here I build the client configuration using environment variables.
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
            "redirect_uris": os.getenv("GOOGLE_REDIRECT_URI")
        }
    }

    #Validate that environment variables are loaded
    if not client_config["web"]["client_id"]:
        raise ValueError("GOOGLE_CLIENT_ID not found in environment variables.")
    
    if not client_config["web"]["client_secret"]:
        raise ValueError("GOOGLE_CLIENT_SECRET not found in environment variables.")
    

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
        #This function reads the token file and parses the JSON content to create a Credentials object.
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES) 

    #This statement checks if the credentials are valid, it can be either expired or mising. If expired, it automatically refreshes one, if missingm it goes through the OAuth flow.    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            #Try block to attempt to refresh the token using the refresh function
            #Except block to ensure that it will re-authenticate if the refresh fails
            try:
                print("User's credentials have expired. Attempting to refresh user credentials.")
                #What happens here is that it sends a HTTP Post request to the token URI with the refresh token to get a new access token.
                creds.refresh(Request())
            except Exception:
                print("Refresh user credentials failed. Re-running OAuth flow.")
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')
        else:
            #This is a helper class from Google's library that simplifies the OAuth 2.0 authorization flow for web apps.
            #Basically it creates a flow object that contains: WHere to send the user to authorize, what permission to request (scopes).
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

            #Starts a local web server (8080) to receive the OAuth callback
            #Make sure it always ask for consent and offline access to get refresh tokens.
            creds = flow.run_local_server(port=8080, access_type='offline', prompt='consent')

        #Save the token.
        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    #After all is done, build the service object.
    try:
        #Build() fetches all the API discovery documents from Google API
        #Creates dynamic service objects that has methosds matching to the API structure.
        service = build(API_SERCE_NAME, API_VERSION, credentials=creds)
        print(f'{API_SERCE_NAME} service created successfully')
        #After the service object is created, it will return a resource object with all the methods (all available endpoints with their parameters) for interacting with the service.
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create servicw instance for {API_SERCE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None