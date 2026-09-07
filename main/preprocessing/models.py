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
    id: UUID = Field(default_factory = uuid4)
    project_name: str
    equipment_system: str
    model_number: Optional[str] = None
    validation_phase: str
    consultant: str
    intended_outcome: str
    obstacle: str
    resolution: str | None = None
    date_logged: str
    attachments: Optional[str] = ""
    keywords: list[str] = []

class ChatRequest(BaseModel):
    req: str

class ChatSources(BaseModel):

    """ 
    Represents the model used to generate a source
    
    Fields
    ---
    src_id: UUID of the source info
    equipment_system: system name
    source type: type of source quoted, entry/documents
    phase: validation phase
    """
    src_id: str
    equipment_system: str
    source_type: str
    phase: str

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
