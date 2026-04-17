import httpx
import msal
from main.config import config

def get_access_token():
    cid = str(config.CLIENT_ID)[:5] if config.CLIENT_ID else "None"
    tid = str(config.TENANT_ID)[:5] if config.TENANT_ID else "None"
    print(f"DEBUG: Using Client ID: {cid}... (Tenant: {tid}...)")
    
    if not config.CLIENT_ID or "your_client_id" in config.CLIENT_ID:
        raise Exception("CLIENT_ID is missing or still set to placeholder in .env!")

        
    app = msal.PublicClientApplication(
        config.CLIENT_ID,
        authority=config.AUTHORITY
    )
    
    # This will open a browser window for you to sign in
    result = app.acquire_token_interactive(scopes=config.SCOPE)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Could not authenticate: {result.get('error_description')}")

def list_sites(token):
    headers = {"Authorization": f"Bearer {token}"}
    # First, try to get the root site
    root_resp = httpx.get("https://graph.microsoft.com/v1.0/sites/root", headers=headers)
    if root_resp.status_code == 200:
        root = root_resp.json()
        print(f"\n--- Root Site ---\nName: {root['displayName']}\nID: {root['id']}\n")
    
    # Then try search
    response = httpx.get("https://graph.microsoft.com/v1.0/sites?search=*", headers=headers)
    sites = response.json().get("value", [])
    print("--- Other Available Sites ---")
    for site in sites:
        print(f"Name: {site['displayName']}\nID: {site['id']}\n")


def list_lists(token, site_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists", headers=headers)
    lists = response.json().get("value", [])
    print(f"\n--- Lists in Site {site_id} ---")
    for lst in lists:
        print(f"Name: {lst['displayName']}\nID: {lst['id']}\n")

if __name__ == "__main__":
    try:
        token = get_access_token()
        print("Successfully authenticated!")
        list_sites(token)
        
        # Once you see a Site ID you like, you can uncomment the line below 
        # and paste the Site ID to see its lists:
        # list_lists(token, "YOUR_SITE_ID_HERE")
        
    except Exception as e:
        print(f"Error: {e}")
