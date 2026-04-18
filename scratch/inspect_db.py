import sqlite3
import os

db_path = 'orka_test_library.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"Tables in database: {[t[0] for t in tables]}")

for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Table '{table_name}' has {count} entries.")

db_size = os.path.getsize(db_path)
print(f"Database size: {db_size} bytes")

conn.close()
