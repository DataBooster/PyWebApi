# Sourced:
# https://github.com/microsoft/PowerBI-Developer-Samples/blob/master/Python/Embed%20for%20your%20customers/powerbiembedding/aadservice.py
#
import msal
from pbi_config import config

def get_accesstoken():
    '''Returns AAD token using MSAL'''

    response = None
    try:
        if config['AUTHENTICATION_MODE'].lower() == 'masteruser':
            
            # Create a public client to authorize the app with the AAD app
            clientapp = msal.PublicClientApplication(config['CLIENT_ID'], authority=config['AUTHORITY'])
            accounts = clientapp.get_accounts(username=config['POWER_BI_USER'])
            if accounts:
                
                # Retrieve Access token from cache if available
                response = clientapp.acquire_token_silent(config['SCOPE'], account=accounts[0])
            if not response:
                # Make a client call if Access token is not available in cache
                response = clientapp.acquire_token_by_username_password(config['POWER_BI_USER'], config['POWER_BI_PASS'], scopes=config['SCOPE'])     

        elif config['AUTHENTICATION_MODE'].lower() == 'serviceprincipal':
            authority = config['AUTHORITY'].replace('organizations', config['TENANT_ID'])
            clientapp = msal.ConfidentialClientApplication(config['CLIENT_ID'], client_credential=config['CLIENT_SECRET'], authority=authority)
            
            # Retrieve Access token from cache if available
            response = clientapp.acquire_token_silent(scopes=config['SCOPE'], account=None)
            if not response:
                
                # Make a client call if Access token is not available in cache
                response = clientapp.acquire_token_for_client(scopes=config['SCOPE'])
        try:
            return response['access_token']
        except KeyError:
            raise Exception(response['error_description'])

    except Exception as ex:
        raise Exception('Error retrieving Access token\n' + str(ex))
