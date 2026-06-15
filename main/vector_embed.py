# 768 dimension embeddings for each entry in the dataset
from .local_db import ValidationEntry
from google import genai
from google.genai import types

client = genai.Client()

class VectorEmbedder:
    def __init__(self, validation_entry: ValidationEntry):
        self.validation_entry = validation_entry

    def prepare_text(self):
        # Combine relevant fields into a single text string for embedding
        fields = {
            'project name':self.validation_entry.project_name,
            'equipment system':self.validation_entry.equipment_system,
            'model number':self.validation_entry.model_number or 'NA',
            'validation phase':self.validation_entry.validation_phase,
            'consultant':self.validation_entry.consultant,
            'intended outcome':self.validation_entry.intended_outcome,
            'obstacle':self.validation_entry.obstacle,
            'resolution':self.validation_entry.resolution,
            'date logged':self.validation_entry.date_logged.isoformat(),
            'keywords': ', '.join(self.validation_entry.keywords)
        }
        return " ".join([f"{key}:{value}" for key, value in fields.items()])

    def embed(self):
        
        embedding_vector = client.models.embed_content(
            contents=self.prepare_text(), 
            model="gemini-embedding-001",
            config=types.EmbedContentConfig(output_dimensionality=768)
            )
        return embedding_vector.embeddings[0].values