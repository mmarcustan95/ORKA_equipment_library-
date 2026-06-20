"""
vector_embed.py
---------------
Generates semantic vector embeddings for ValidationEntry records using the
Google Gemini embedding model.

Embeddings are 768-dimensional float vectors that capture the semantic meaning
of an entry's text fields. They are the foundation of the RAG (Retrieval-Augmented
Generation) pipeline: once stored, they allow the AI to find the most relevant
past validation lessons for a given natural-language query.

Requires:
  - GEMINI_API_KEY set in the environment (loaded via .env in local dev).
  - google-genai package installed.

Typical usage:
    embedder = VectorEmbedder(entry)
    vector = embedder.embed()   # returns a list of 768 floats
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from .models import ValidationEntry
from google import genai
from google.genai import types

load_dotenv(Path(__file__).resolve().parent / ".env")

_EMBED_MODEL = "gemini-embedding-001"
_EMBED_DIMS = 768
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Set GEMINI_API_KEY in main/.env or your environment.")
        _client = genai.Client(api_key=api_key)
    return _client


def embed_text(text: str) -> list[float]:
    """Embed an arbitrary string — used to embed chat query strings for similarity search."""
    result = _get_client().models.embed_content(
        contents=text,
        model=_EMBED_MODEL,
        config=types.EmbedContentConfig(output_dimensionality=_EMBED_DIMS),
    )
    return result.embeddings[0].values


class VectorEmbedder:
    """Converts a ValidationEntry into a 768-dimension semantic embedding vector."""

    def __init__(self, validation_entry: ValidationEntry):
        self.validation_entry = validation_entry

    def prepare_text(self) -> str:
        """Serialise the entry's key fields into a single labelled string for embedding."""
        fields = {
            'project name':     self.validation_entry.project_name,
            'equipment system': self.validation_entry.equipment_system,
            'model number':     self.validation_entry.model_number or 'NA',
            'validation phase': self.validation_entry.validation_phase,
            'consultant':       self.validation_entry.consultant,
            'intended outcome': self.validation_entry.intended_outcome,
            'obstacle':         self.validation_entry.obstacle,
            'resolution':       self.validation_entry.resolution,
            'date logged':      self.validation_entry.date_logged.isoformat(),
            'keywords':         ', '.join(self.validation_entry.keywords)
        }
        return " ".join([f"{key}:{value}" for key, value in fields.items()])

    def embed(self) -> list[float]:
        """Generate a 768-dimensional embedding vector for this entry."""
        return embed_text(self.prepare_text())
