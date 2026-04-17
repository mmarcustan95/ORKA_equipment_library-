import sqlite3
import json
import os
from typing import List
from .models import ValidationEntry

# Try to import psycopg2 for PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

class LocalDatabase:
    def __init__(self, db_path="orka_test_library.db"):
        self.db_url = os.getenv("DATABASE_URL")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        if self.db_url:
            # Use PostgreSQL
            return psycopg2.connect(self.db_url)
        else:
            # Use SQLite
            return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.cursor()
                # SQL syntax for Table creation is the same for both
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id TEXT PRIMARY KEY,
                        project_name TEXT,
                        equipment_system TEXT,
                        validation_phase TEXT,
                        intended_outcome TEXT,
                        obstacle TEXT,
                        resolution TEXT,
                        date_logged TEXT,
                        attachments TEXT,
                        keywords TEXT
                    )
                """)
        finally:
            conn.close()

    def get_entries(self) -> List[ValidationEntry]:
        conn = self._get_connection()
        try:
            if self.db_url:
                cur = conn.cursor(cursor_factory=RealDictCursor)
            else:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
            
            cur.execute("SELECT * FROM entries")
            rows = cur.fetchall()
            
            entries = []
            for row in rows:
                entries.append(ValidationEntry(
                    id=row["id"],
                    project_name=row["project_name"],
                    equipment_system=row["equipment_system"],
                    validation_phase=row["validation_phase"],
                    intended_outcome=row["intended_outcome"],
                    obstacle=row["obstacle"],
                    resolution=row["resolution"],
                    date_logged=row["date_logged"],
                    attachments=row["attachments"] if row["attachments"] else "",
                    keywords=json.loads(row["keywords"]) if isinstance(row["keywords"], str) else row["keywords"]
                ))
            return entries
        finally:
            conn.close()

    def create_entry(self, entry: ValidationEntry):
        conn = self._get_connection()
        placeholder = "%s" if self.db_url else "?"
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(f"""
                    INSERT INTO entries (id, project_name, equipment_system, validation_phase, 
                                       intended_outcome, obstacle, resolution, date_logged, attachments, keywords)
                    VALUES ({','.join([placeholder]*10)})
                """, (
                    str(entry.id),
                    entry.project_name,
                    entry.equipment_system,
                    entry.validation_phase,
                    entry.intended_outcome,
                    entry.obstacle,
                    entry.resolution,
                    entry.date_logged.isoformat(),
                    entry.attachments,
                    json.dumps(entry.keywords)
                ))
            return entry
        finally:
            conn.close()

    def delete_entry(self, entry_id: str):
        conn = self._get_connection()
        placeholder = "%s" if self.db_url else "?"
        try:
            with conn:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM entries WHERE id = {placeholder}", (entry_id,))
            return True
        finally:
            conn.close()

# Singleton instance
test_db = LocalDatabase()

