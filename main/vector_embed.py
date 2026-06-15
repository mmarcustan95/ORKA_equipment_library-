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

from .local_db import ValidationEntry
from google import genai
from google.genai import types

# Initialise the Gemini client once at module level.
# Reads the API key from the GEMINI_API_KEY environment variable automatically.
client = genai.Client()


class VectorEmbedder:
    """
    Converts a ValidationEntry into a 768-dimension semantic embedding vector.

    The entry's text fields are concatenated into a single labelled string
    and sent to the Gemini embedding model. The resulting vector numerically
    represents the meaning of the entry and can be compared against other
    vectors using cosine similarity for semantic search.
    """

    def __init__(self, validation_entry: ValidationEntry):
        """
        Parameters
        ----------
        validation_entry : ValidationEntry
            The database entry to be embedded.
        """
        self.validation_entry = validation_entry

    def prepare_text(self) -> str:
        """
        Serialise the entry's key fields into a single labelled text string.

        Each field is formatted as "field name:value" and joined with spaces.
        Including field labels (not just values) gives the embedding model
        structural context, improving retrieval accuracy.

        Optional fields that are None default to 'NA' to avoid serialisation errors.
        The keywords list is joined into a comma-separated string.

        Returns
        -------
        str
            A single string representing the full content of the entry,
            ready to be passed to the embedding model.
        """
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

    def embed(self) -> list:
        """
        Generate a 768-dimensional embedding vector for this entry.

        Calls the Gemini embedding model with the prepared text and returns
        the raw float vector. This vector should be stored alongside the entry
        in the database to enable fast similarity search during RAG retrieval.

        Returns
        -------
        list[float]
            A list of 768 floats representing the semantic content of the entry.
        """
        embedding_vector = client.models.embed_content(
            contents=self.prepare_text(),
            model="gemini-embedding-001",
            # Request exactly 768 dimensions (model default is 1536)
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        return embedding_vector.embeddings[0].values
