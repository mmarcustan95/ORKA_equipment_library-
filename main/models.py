from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional
from uuid import uuid4, UUID

class ValidationEntry(BaseModel):
    # We use Field(default_factory=...) to generate a unique ID automatically if one isn't provided
    id: UUID = Field(default_factory=uuid4)
    project_name: str
    equipment_system: str
    validation_phase: str
    consultant: str
    intended_outcome: str
    obstacle: str
    resolution: str
    date_logged: date
    attachments: Optional[str] = ""
    keywords: List[str] = []

    class Config:
        # This helps FastAPI understand how to convert data from a database (later)
        from_attributes = True