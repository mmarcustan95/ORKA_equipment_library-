"""
local_db.py
-----------
Database abstraction layer for the ORKA Equipment Knowledge Library.

Supports two backends transparently:
  - SQLite  : used locally for development (default, no config needed).
  - PostgreSQL: used in production when the DATABASE_URL environment variable is set.

All CRUD operations (Create, Read, Update, Delete) on ValidationEntry records live here.
The rest of the application interacts with the database only through the `test_db` singleton
exported at the bottom of this file.
"""

import sqlite3
import json
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from .models import ValidationEntry

load_dotenv(Path(__file__).resolve().parent / ".env")

# Attempt to import the PostgreSQL driver. If it's not installed the app
# falls back to SQLite automatically — no configuration needed for local dev.
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class LocalDatabase:
    """
    Handles all database interactions for ValidationEntry records.

    On instantiation it automatically:
      1. Detects whether to use SQLite or PostgreSQL.
      2. Creates the 'entries' table if it doesn't already exist.
      3. Runs a lightweight migration to add any missing columns (e.g. model_number).
    """

    def __init__(self, db_path="orka_test_library.db"):
        """
        Initialise the database connection settings and ensure the schema is ready.

        Parameters
        ----------
        db_path : str
            Path to the SQLite file used in local development.
            Ignored when DATABASE_URL is set (PostgreSQL mode).
        """
        # If DATABASE_URL is set in the environment, PostgreSQL is used instead of SQLite
        self.db_url = os.getenv("DATABASE_URL")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """
        Open and return a new database connection.

        Returns a psycopg2 connection for PostgreSQL or a sqlite3 connection
        for local development, depending on whether DATABASE_URL is set.
        Callers are responsible for closing the connection after use.
        """
        if self.db_url:
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_path)

    def _init_db(self):
        """
        Create the 'entries' table if it doesn't exist, and apply any outstanding migrations.

        Called once on startup. The CREATE TABLE statement is safe to run repeatedly
        because of the IF NOT EXISTS clause. The migration block checks for the
        model_number column and adds it if missing — this handles databases created
        before that field was introduced.
        """
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                # SQL syntax for table creation is compatible with both SQLite and PostgreSQL
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id TEXT PRIMARY KEY,
                        project_name TEXT,
                        equipment_system TEXT,
                        model_number TEXT,
                        validation_phase TEXT,
                        consultant TEXT,
                        intended_outcome TEXT,
                        obstacle TEXT,
                        resolution TEXT,
                        date_logged TEXT,
                        attachments TEXT,
                        keywords TEXT,
                        embedding TEXT
                    )
                """)

                for col, definition in [("model_number", "TEXT"), ("embedding", "TEXT")]:
                    try:
                        cur.execute(f"SELECT {col} FROM entries LIMIT 1")
                    except:
                        if self.db_url:
                            conn.rollback()
                            cur = conn.cursor()
                        cur.execute(f"ALTER TABLE entries ADD COLUMN {col} {definition}")
        finally:
            conn.close()

    def get_entries(self) -> List[ValidationEntry]:
        """
        Fetch all ValidationEntry records from the database.

        Returns
        -------
        List[ValidationEntry]
            Every entry currently stored, as a list of Pydantic model instances.
            Returns an empty list if the table has no rows.
        """
        conn = self._get_connection()
        try:
            if self.db_url:
                # RealDictCursor makes PostgreSQL rows behave like dicts (column name access)
                cur = conn.cursor(cursor_factory=RealDictCursor) # type: ignore
            else:
                # sqlite3.Row also enables column-name access on SQLite rows
                conn.row_factory = sqlite3.Row # type: ignore
                cur = conn.cursor()

            cur.execute("SELECT * FROM entries")
            rows = cur.fetchall()

            entries = []
            for row in rows:
                entries.append(ValidationEntry(
                    id=row["id"], # type: ignore
                    project_name=row["project_name"], # type: ignore
                    equipment_system=row["equipment_system"], # type: ignore
                    # model_number may be absent in older DB rows, default to empty string
                    model_number=row["model_number"] if "model_number" in row.keys() and row["model_number"] else "",   # type: ignore
                    validation_phase=row["validation_phase"], # type: ignore
                    consultant=row["consultant"] if row["consultant"] else "", # type: ignore
                    intended_outcome=row["intended_outcome"], # type: ignore
                    obstacle=row["obstacle"], # type: ignore
                    resolution=row["resolution"], # type: ignore
                    date_logged=row["date_logged"], # type: ignore
                    attachments=row["attachments"] if row["attachments"] else "", # type: ignore
                    # keywords is stored as a JSON string in the DB; deserialise it back to a list
                    keywords=json.loads(row["keywords"]) if isinstance(row["keywords"], str) else row["keywords"] # type: ignore
                ))
            return entries
        finally:
            conn.close()

    def create_entry(self, entry: ValidationEntry):
        """
        Insert a new ValidationEntry record into the database.

        Parameters
        ----------
        entry : ValidationEntry
            The fully populated entry to save. The id field is auto-generated
            by the model if not provided.

        Returns
        -------
        ValidationEntry
            The same entry object that was passed in (unchanged).
        """
        conn = self._get_connection()
        # SQLite uses ? as the parameter placeholder; PostgreSQL uses %s
        placeholder = "%s" if self.db_url else "?"
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(f"""
                    INSERT INTO entries (id, project_name, equipment_system, model_number, validation_phase, consultant,
                                       intended_outcome, obstacle, resolution, date_logged, attachments, keywords)
                    VALUES ({','.join([placeholder]*12)})
                """, (
                    str(entry.id),
                    entry.project_name,
                    entry.equipment_system,
                    entry.model_number,
                    entry.validation_phase,
                    entry.consultant,
                    entry.intended_outcome,
                    entry.obstacle,
                    entry.resolution,
                    entry.date_logged.isoformat(),  # Store date as ISO string (YYYY-MM-DD)
                    entry.attachments,
                    json.dumps(entry.keywords)      # Serialise keyword list to JSON string
                ))
            return entry
        finally:
            conn.close()

    def delete_entry(self, entry_id: str):
        """
        Permanently delete a ValidationEntry by its ID.

        Parameters
        ----------
        entry_id : str
            The UUID string of the entry to remove.

        Returns
        -------
        bool
            True if the operation completed without error.
        """
        conn = self._get_connection()
        placeholder = "%s" if self.db_url else "?"
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM entries WHERE id = {placeholder}", (entry_id,))
            return True
        finally:
            conn.close()

    def update_embedding(self, entry_id: str, embedding: list) -> None:
        """Persist a pre-computed embedding vector for an existing entry."""
        conn = self._get_connection()
        placeholder = "%s" if self.db_url else "?"
        # pgvector accepts a Python list directly; SQLite stores it as a JSON string
        value = embedding if self.db_url else json.dumps(embedding)
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(
                    f"UPDATE entries SET embedding = {placeholder} WHERE id = {placeholder}",
                    (value, entry_id),
                )
        finally:
            conn.close()

    def update_entry(self, entry_id: str, entry: ValidationEntry):
        """
        Overwrite all fields of an existing entry (full replace, not partial patch).

        Parameters
        ----------
        entry_id : str
            The UUID string identifying which row to update.
        entry : ValidationEntry
            The new field values. The id inside the entry object is ignored;
            the row is matched by entry_id.

        Returns
        -------
        ValidationEntry
            The updated entry object (unchanged from what was passed in).
        """
        conn = self._get_connection()
        placeholder = "%s" if self.db_url else "?"
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(f"""
                    UPDATE entries SET
                        project_name = {placeholder},
                        equipment_system = {placeholder},
                        model_number = {placeholder},
                        validation_phase = {placeholder},
                        consultant = {placeholder},
                        intended_outcome = {placeholder},
                        obstacle = {placeholder},
                        resolution = {placeholder},
                        date_logged = {placeholder},
                        attachments = {placeholder},
                        keywords = {placeholder}
                    WHERE id = {placeholder}
                """, (
                    entry.project_name,
                    entry.equipment_system,
                    entry.model_number,
                    entry.validation_phase,
                    entry.consultant,
                    entry.intended_outcome,
                    entry.obstacle,
                    entry.resolution,
                    entry.date_logged.isoformat(),
                    entry.attachments,
                    json.dumps(entry.keywords),
                    entry_id  # WHERE clause — must be last in the tuple
                ))
            return entry
        finally:
            conn.close()
    def insert_document_chunk(self, filename: str, file_type: str, content_chunk: str,
                               chunk_index: int, equipment_tag: str, embedding: list,
                               uploaded_by: str) -> None:
        """Insert a single document chunk with its embedding into the documents table."""
        if not self.db_url:
            raise RuntimeError("insert_document_chunk requires a PostgreSQL/Supabase connection.")

        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO documents
                        (filename, file_type, content_chunk, chunk_index, equipment_tag, embedding, uploaded_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (filename, file_type, content_chunk, chunk_index, equipment_tag, embedding, uploaded_by))
        finally:
            conn.close()

    def search_documents(self, queryvector, top_k=12):
        """Search document chunks by vector similarity. Requires Supabase (pgvector) — not supported on SQLite."""
        if not self.db_url:
            raise RuntimeError("search_documents requires a PostgreSQL/Supabase connection. Set DATABASE_URL in your environment.")

        conn = self._get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)  # type: ignore
            cur.execute("""
                SELECT id, filename, file_type, content_chunk, chunk_index, equipment_tag
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (queryvector, top_k))
            return cur.fetchall()
        finally:
            conn.close()

    def search_entries(self, queryvector, top_k=12):
        """Search entries by vector similarity. Requires Supabase (pgvector) — not supported on SQLite."""
        if not self.db_url:
            raise RuntimeError("search_entries requires a PostgreSQL/Supabase connection. Set DATABASE_URL in your environment.")

        conn = self._get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)  # type: ignore
            cur.execute("""
                SELECT id, equipment_system, validation_phase, obstacle, resolution
                FROM entries
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (queryvector, top_k))
            return cur.fetchall()
        finally:
            conn.close()


# Singleton database instance shared across the whole application.
# Import this object (not the class) in other modules.
test_db = LocalDatabase() # type: ignore
