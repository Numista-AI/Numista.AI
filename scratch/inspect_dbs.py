import sqlite3

def inspect_db(db_path):
    print(f"=== Inspecting {db_path} ===")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)
    for table in tables:
        cur.execute(f"PRAGMA table_info({table});")
        columns = cur.fetchall()
        print(f"\nTable: {table}")
        for col in columns:
            print(f"  Column: {col[1]} ({col[2]})")
        
        # Print row count
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        row_count = cur.fetchone()[0]
        print(f"  Total Rows: {row_count}")
    conn.close()

if __name__ == "__main__":
    import os
    inspect_db("c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db")
    inspect_db("c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista.db")
