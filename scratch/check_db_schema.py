import sqlite3
import os

db_path = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"
print("DB Path exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get table schema
cur.execute("PRAGMA table_info(definitive_reference);")
columns = cur.fetchall()
print("\n--- Columns in definitive_reference ---")
for col in columns:
    print(col)

# Get row count
cur.execute("SELECT COUNT(*) FROM definitive_reference;")
count = cur.fetchone()[0]
print("\nRow count:", count)

# Sample records
cur.execute("SELECT * FROM definitive_reference LIMIT 3;")
rows = cur.fetchall()
print("\n--- Sample records ---")
for row in rows:
    print(row)

# Check distinct categories
cur.execute("SELECT category, COUNT(*) FROM definitive_reference GROUP BY category;")
cats = cur.fetchall()
print("\n--- Categories ---")
for cat in cats:
    print(cat)

conn.close()
