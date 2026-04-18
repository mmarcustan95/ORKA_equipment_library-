import sqlite3

db_path = 'orka_test_library.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(entries);")
columns = cursor.fetchall()
print("Table structure (entries):")
for col in columns:
    print(col)

cursor.execute("SELECT * FROM entries LIMIT 3;")
rows = cursor.fetchall()
print("\nSample Data:")
for row in rows:
    print(row)

conn.close()
