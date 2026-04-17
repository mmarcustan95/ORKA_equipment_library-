import os
from dotenv import load_dotenv

# Load environment variables from .env file
print(f"DEBUG: Looking for .env in {os.getcwd()}")
if os.path.exists(".env"):
    print("DEBUG: Found .env file!")
else:
    print("DEBUG: .env file NOT FOUND in current directory!")

load_dotenv()

class Config:
    # These must be the EXACT names of the variables in your .env file
    CLIENT_ID = os.getenv("CLIENT_ID")
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    
    SHAREPOINT_SITE_ID = os.getenv("SHAREPOINT_SITE_ID")
    SHAREPOINT_LIST_ID = os.getenv("SHAREPOINT_LIST_ID")
    
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/docs/oauth2-redirect")
    
    # Authority URL for Microsoft Entra ID
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPE = ["https://graph.microsoft.com/.default"]

config = Config()
