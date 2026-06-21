"""
models.py
---------
Defines the core data model for the ORKA Equipment Knowledge Library.

A ValidationEntry represents a single "lesson learned" record — capturing the
equipment involved, what went wrong during validation, and how it was resolved.
This model is used by the API layer (app.py), the database layer (local_db.py),
and the AI embedding layer (vector_embed.py).
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional
from uuid import uuid4, UUID


class ValidationEntry(BaseModel):
    """
    Represents one equipment validation lesson learned entry.

    Fields
    ------
    id              : Auto-generated unique identifier (UUID). Never needs to be set manually.
    project_name    : Name of the pharmaceutical/biotech project (e.g. "ACME Pharma Suite 3").
    equipment_system: The equipment or system being validated (e.g. "HVAC", "WFI Loop").
    model_number    : Optional equipment model/tag number (e.g. "AHU-2200X").
    validation_phase: IQ / OQ / PQ phase in which the issue occurred.
    consultant      : Name of the validation consultant responsible for the entry.
    intended_outcome: What the validation test was supposed to achieve.
    obstacle        : The problem or deviation that was encountered.
    resolution      : How the issue was resolved, including any corrective actions taken.
    date_logged     : Date the lesson learned was recorded.
    attachments     : Optional file path or URL pointing to supporting documents.
    keywords        : List of tags for search and categorisation (e.g. ["HVAC", "PID", "ISO 7"]).
    """

    # Auto-generates a unique UUID if no id is provided on creation
    id: UUID = Field(default_factory=uuid4)
    project_name: str
    equipment_system: str
    model_number: Optional[str] = None
    validation_phase: str
    consultant: str
    intended_outcome: str
    obstacle: str
    resolution: str
    date_logged: date
    attachments: Optional[str] = ""
    keywords: List[str] = []

    class Config:
        # Allows Pydantic to read data from ORM/database row objects as well as plain dicts
        from_attributes = True

class ChatRequest(BaseModel):
    """
    Represents a chat request for the ORKA Equipment Knowledge Library.

    Fields
    ------
    query: The user's question or prompt to the AI chat system.
    context_entries: Optional list of ValidationEntry objects to provide context for the AI response.
    """

    query: str

class ChatSources(BaseModel):
    """
    Represents the sources used to generate a chat response.

    Fields
    ------
    source_id: The unique identifier of the source entry.
    source_text: The text content of the source entry.
    """

    source_id: str
    equipment_system: str
    phase: str
    source_type: str  # "entry" or "document"

class ChatResponse(BaseModel):
    """
    Represents a chat response from the ORKA Equipment Knowledge Library.

    Fields
    ------
    answer: The AI-generated answer to the user's query.
    sources: list of ValidationEntry objects that were used to generate the answer.
    """

    answer: str
    sources: List[ChatSources]

