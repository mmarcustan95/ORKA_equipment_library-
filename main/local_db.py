import sqlite3
import json
from typing import List
from .models import ValidationEntry

class LocalDatabase:
    def __init__(self, db_path="orka_test_library.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
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

    def get_entries(self) -> List[ValidationEntry]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM entries")
            rows = cursor.fetchall()
            
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
                    attachments=row["attachments"] if "attachments" in row.keys() and row["attachments"] else "",

                    keywords=json.loads(row["keywords"])
                ))
            return entries

    def create_entry(self, entry: ValidationEntry):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO entries (id, project_name, equipment_system, validation_phase, 
                                   intended_outcome, obstacle, resolution, date_logged, attachments, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


    def delete_entry(self, entry_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        return True

# Singleton instance for testing
test_db = LocalDatabase()

