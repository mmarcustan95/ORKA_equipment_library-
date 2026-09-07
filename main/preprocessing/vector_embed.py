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
