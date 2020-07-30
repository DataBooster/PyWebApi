# Sourced:
# https://github.com/microsoft/PowerBI-Developer-Samples/blob/master/Python/Embed%20for%20your%20customers/powerbiembedding/config.py
#
config = {
     # Can be set to 'MasterUser' or 'ServicePrincipal'
    "AUTHENTICATION_MODE": "masteruser",

    # Id of the Azure tenant in which AAD app and Power BI report is hosted.
    # Required only for ServicePrincipal authentication mode.
    "TENANT_ID": "",
    
    # Client Id (Application Id) of the AAD app
    "CLIENT_ID": "",
    
    # Client Secret (App Secret) of the AAD app.
    # Required only for ServicePrincipal authentication mode.
    "CLIENT_SECRET": "",
    
    # Scope of AAD app.
    # Use the below configuration to use all the permissions provided in the
    # AAD app through Azure portal.
    "SCOPE": ["https://analysis.windows.net/powerbi/api/.default"],
    
    # URL used for initiating authorization request
    "AUTHORITY": "https://login.microsoftonline.com/organizations",
    
    # Master user email address.
    # Required only for MasterUser authentication mode.
    "POWER_BI_USER": "",
    
    # Master user email password.
    # Required only for MasterUser authentication mode.
    "POWER_BI_PASS": ""
    }
