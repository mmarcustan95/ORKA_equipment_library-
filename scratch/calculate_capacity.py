import sqlite3
import os

db_path = 'orka_test_library.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM entries")
rows = cursor.fetchall()

total_size_bytes = 0
for row in rows:
    # Estimate size by summing the length of all elements converted to string
    row_size = sum(len(str(item)) if item is not None else 0 for item in row)
    total_size_bytes += row_size

num_entries = len(rows)
avg_entry_size = total_size_bytes / num_entries if num_entries > 0 else 0

print(f"Number of entries: {num_entries}")
print(f"Total content size: {total_size_bytes} bytes")
print(f"Average entry size: {avg_entry_size:.2f} bytes")

# 8GB in bytes
eight_gb = 8 * 1024 * 1024 * 1024
if avg_entry_size > 0:
    estimated_capacity = eight_gb / avg_entry_size
    print(f"Estimated entries in 8GB: {estimated_capacity:,.0f}")
else:
    print("No entries found to calculate average.")

conn.close()
