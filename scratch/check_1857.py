import sqlite3

db_path = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM definitive_reference WHERE year = '1857';")
rows = [dict(r) for r in cur.fetchall()]
for r in rows:
    print(dict(r))

conn.close()
