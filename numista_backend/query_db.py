import pymysql
import json
import traceback

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3307,
        user='root',
        password='Num1sta#2026CoinData',
        database='numista_data',
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM us_mint_assets")
        assets = cursor.fetchall()

    print("Assets loaded:", len(assets))
    with open('db_assets.json', 'w') as f:
        json.dump(assets, f, indent=2, default=str)
        
    conn.close()
except Exception as e:
    with open('db_error.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("Error written to db_error.txt")
