import sqlite3

db_path = r"c:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get distinct years and their counts
cur.execute("SELECT year, COUNT(*) FROM definitive_reference WHERE year != '' GROUP BY year ORDER BY year LIMIT 50;")
years = cur.fetchall()
print("--- Distinct Years (First 50) ---")
for y in years:
    print(y)

# Look for Fugio cent
cur.execute("SELECT year, denomination, variety, series, doc_id FROM definitive_reference WHERE variety LIKE '%Fugio%' OR note LIKE '%Fugio%';")
fugio = cur.fetchall()
print("\n--- Fugio Cent Reference ---")
for f in fugio:
    print(f)

# Look for earliest year
cur.execute("SELECT MIN(CAST(year AS INTEGER)), MAX(CAST(year AS INTEGER)) FROM definitive_reference WHERE year != '';")
min_max = cur.fetchone()
print("\nMin/Max year casting as integer:", min_max)

conn.close()
