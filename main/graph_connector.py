import httpx
import msal
from typing import List, Dict, Any
from .config import config
from .models import ValidationEntry

class GraphConnector:
    def __init__(self):
        self.app = msal.ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=config.AUTHORITY,
            client_credential=config.CLIENT_SECRET,
        )

    def _get_access_token(self) -> str:
        """Retrieve a fresh access token from Microsoft Entra ID."""
        result = self.app.acquire_token_for_client(scopes=config.SCOPE)
        if "access_token" in result:
            return result["access_token"]
        else:
            raise Exception(f"Failed to authenticate with Microsoft: {result.get('error_description')}")

    def get_entries(self) -> List[ValidationEntry]:
        """Fetch all items from the SharePoint List."""
        token = self._get_access_token()
        url = f"https://graph.microsoft.com/v1.0/sites/{config.SHAREPOINT_SITE_ID}/lists/{config.SHAREPOINT_LIST_ID}/items?expand=fields"
        
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        
        items = response.json().get("value", [])
        entries = []
        for item in items:
            fields = item.get("fields", {})
            # Map SharePoint columns back to our Pydantic model
            entries.append(ValidationEntry(
                id=fields.get("id", item.get("id")), # Use SP item ID if our field is missing
                project_name=fields.get("ProjectName", ""),
                equipment_system=fields.get("SystemEquipment", ""),
                validation_phase=fields.get("ValidationPhase", ""),
                intended_outcome=fields.get("IntendedOutcome", ""),
                obstacle=fields.get("ObstacleEncountered", ""),
                resolution=fields.get("ResolutionLearning", ""),
                date_logged=fields.get("DateLogged"),
                consultant=fields.get("Consultant", ""),
                keywords=fields.get("Keywords", "").split(", ") if fields.get("Keywords") else []
            ))
        return entries

    def create_entry(self, entry: ValidationEntry) -> Dict[str, Any]:
        """Create a new item in the SharePoint List."""
        token = self._get_access_token()
        url = f"https://graph.microsoft.com/v1.0/sites/{config.SHAREPOINT_SITE_ID}/lists/{config.SHAREPOINT_LIST_ID}/items"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Prepare the data for SharePoint (Internal column names are used here)
        payload = {
            "fields": {
                "Title": entry.project_name, # Usually 'Title' is the mandatory first column
                "ProjectName": entry.project_name,
                "SystemEquipment": entry.equipment_system,
                "ValidationPhase": entry.validation_phase,
                "IntendedOutcome": entry.intended_outcome,
                "ObstacleEncountered": entry.obstacle,
                "ResolutionLearning": entry.resolution,
                "DateLogged": entry.date_logged.isoformat(),
                "Consultant": entry.consultant,
                "Keywords": ", ".join(entry.keywords)
            }
        }
        
        response = httpx.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

# Singleton instance
connector = GraphConnector()
