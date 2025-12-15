#This script contains the function to generate user access token to connect to Microsoft Graph API using OAuth2 authentication.
import os
import webbrowser
import msal

MS_GRAPH_BASE_ENDPOINT = 'https://graph.microsoft.com/v1.0/'

#This function will handle the authentication process and return an access token for the Microsoft Graph API
def get_access_token(app_id, client_secret, scopes):
    #ConfidentialClientApplication is used here since it is a web app where client secrets can be securely stored in.
    client = msal.ConfidentialClientApplication(
        client_id = app_id,
        client_credential = client_secret,
        authority = 'https://login.microsoftonline.com/common'
    )

    #Check if there is a refresh token stored.
    refresh_token = None
    if os.path.exists('refresh_token.txt'):
        with open ('refresh_token.txt', 'r') as file:
            refresh_token = file.read().strip()

    if refresh_token:
        #If refresh token exists, try to acquire a new token using the refresh token
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes = scopes)
    else:
        #Perform authorization flow if no refresh token found
        auth_request_url = client.get_authorization_request_url(scopes)
        webbrowser.open(auth_request_url)
        authorization_code = input('Enter the authorization code: ')

        if not authorization_code:
            raise ValueError("Authorization code is empty")
        
        token_response = client.acquire_token_by_authorization_code(code = authorization_code, scopes = scopes)

    if 'access_token' in token_response:
        if 'refresh_token' in token_response:
            with open('refresh_token.txt', 'w') as file:
                file.write(token_response['refresh_token'])
            
        return token_response['access_token']
    else:
        raise Exception("Failed to acquire access token: " + str(token_response))
    


    