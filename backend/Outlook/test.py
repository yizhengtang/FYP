import msal
import os
from dotenv import load_dotenv

load_dotenv()

app_id = os.getenv('MICROSOFT_CLIENT_ID')
client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')

client = msal.ConfidentialClientApplication(
        client_id = app_id,
        client_credential = client_secret,
        authority = 'https://login.microsoftonline.com/common')

result = None

accounts = client.get_accounts()
if accounts:
    print("Pick the account you want to use to proceed:")
    for a in accounts:
        print(a["username"])
    # Assuming the end user chose this one
    chosen = accounts[0]
    # Now let's try to find a token in cache for this account
    result = client.acquire_token_silent(["User.Read"], account=chosen)

if not result:
    # So no suitable token exists in cache. Let's get a new one from Azure AD.
    result = client.acquire_token_(scopes=["User.Read"])
if "access_token" in result:
    print(result["access_token"])  # Yay!
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug