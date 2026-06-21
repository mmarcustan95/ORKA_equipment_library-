"""
ingest_document.py
------------------
PDF ingestion pipeline for the ORKA Equipment Knowledge Library.

Extracts text from an uploaded PDF, splits it into overlapping chunks,
generates a Gemini embedding for each chunk, and stores them in the
Supabase documents table for retrieval by the /chat endpoint.

Chunk strategy: ~2000 characters per chunk with 200-character overlap.
This approximates the 500-token / 50-token-overlap target from the plan
without requiring a separate tokeniser dependency.
"""

import io
import logging
import pdfplumber
from docx import Document as DocxDocument
from pptx import Presentation
from .vector_embed import embed_text
from .local_db import test_db

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2000   # characters (~500 tokens)
CHUNK_OVERLAP = 200  # characters (~50 tokens)

SUPPORTED_TYPES = {".pdf", ".docx", ".pptx"}


def extract_text_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF. Returns empty string for scanned PDFs."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_docx(file_bytes: bytes) -> str:
    """Extract text from a Word document paragraph by paragraph."""
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_pptx(file_bytes: bytes) -> str:
    """Extract text from a PowerPoint file slide by slide."""
    prs = Presentation(io.BytesIO(file_bytes))
    text_parts = []
    for slide_num, slide in enumerate(prs.slides, 1):
        slide_texts = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                slide_texts.append(shape.text.strip())
        if slide_texts:
            text_parts.append(f"[Slide {slide_num}]\n" + "\n".join(slide_texts))
    return "\n\n".join(text_parts)


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Route to the correct extractor based on file extension."""
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_text_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_docx(file_bytes)
    elif ext == "pptx":
        return extract_text_pptx(file_bytes)
    raise ValueError(f"Unsupported file type: .{ext}")


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks of ~2000 characters with 200-character overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def ingest_document(filename: str, file_bytes: bytes, equipment_tag: str, uploaded_by: str) -> dict:
    """
    Full ingestion pipeline for a PDF, Word document, or PowerPoint file.

    Extracts text, chunks it, embeds each chunk, and stores all chunks
    in the documents table. Returns a summary of the result.
    """
    ext = "." + filename.lower().rsplit(".", 1)[-1]
    if ext not in SUPPORTED_TYPES:
        return {"filename": filename, "status": "skipped", "reason": f"Unsupported file type: {ext}", "chunks": 0}

    text = extract_text(filename, file_bytes)

    if not text.strip():
        logger.warning("No extractable text found in %s.", filename)
        return {"filename": filename, "status": "skipped", "reason": "No extractable text — scanned or image-only file?", "chunks": 0}

    chunks = chunk_text(text)
    stored = 0
    failed = 0

    for i, chunk in enumerate(chunks):
        try:
            embedding = embed_text(chunk)
            test_db.insert_document_chunk(
                filename=filename,
                file_type=ext.lstrip("."),
                content_chunk=chunk,
                chunk_index=i,
                equipment_tag=equipment_tag,
                embedding=embedding,
                uploaded_by=uploaded_by,
            )
            stored += 1
        except Exception as e:
            logger.warning("Failed to store chunk %d of %s: %s", i, filename, e)
            failed += 1

    logger.info("Ingested %s: %d chunks stored, %d failed.", filename, stored, failed)
    return {"filename": filename, "status": "complete", "chunks_stored": stored, "chunks_failed": failed}
