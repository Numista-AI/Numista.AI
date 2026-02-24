import requests
import sqlite3
import json
import os
import time
from datetime import datetime
import getpass

# Constants
API_URL = "https://api.numista.com/api/v3"
MONTHLY_LIMIT = 2000
WARNING_LIMIT = 1500
USAGE_FILE = "api_usage.json"

script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(script_dir, "..", "database", "numista_coins.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coins (
            id INTEGER PRIMARY KEY,
            title TEXT,
            issuer TEXT,
            value TEXT,
            composition TEXT,
            mintage INTEGER,
            also_known_as TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    return conn

def check_rate_limit():
    current_month = datetime.now().strftime("%Y-%m")
    usage = {}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)
            
    month_usage = usage.get(current_month, 0)
    
    if month_usage >= MONTHLY_LIMIT:
        print(f"\n[CRITICAL] You have reached your monthly Numista API limit of {MONTHLY_LIMIT} requests. Stopping.")
        return False
    elif month_usage >= WARNING_LIMIT:
        print(f"\n[WARNING] You have used {month_usage}/{MONTHLY_LIMIT} Numista API requests this month. Proceeding...")
        
    return True

def increment_rate_limit():
    current_month = datetime.now().strftime("%Y-%m")
    usage = {}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)
            
    usage[current_month] = usage.get(current_month, 0) + 1
    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)

def fetch_coins(api_key, category):
    headers = {
        "Numista-API-Key": api_key
    }
    
    page = 1
    total_coins = 0
    conn = init_db()
    cursor = conn.cursor()
    
    print(f"\nFetching coins for category/query: {category}")
    
    # Numista API uses pagination. The 'q' parameter searches everywhere.
    # To prevent grabbing all 10,000+ US coins, we will strictly filter 
    # the results by looking at the 'value.text' field.
    
    valid_values = []
    if category == "dollar":
        valid_values = ["1 Dollar", "$1", "One Dollar"]
    elif category == "half dollar":
        valid_values = ["50 Cents", "Half Dollar", "1/2 Dollar"]
    elif category == "quarter":
        valid_values = ["25 Cents", "Quarter Dollar", "1/4 Dollar"]
        
    while True:
        if not check_rate_limit():
            break
            
        params = {
            "q": category,
            "issuer": "united-states",
            "page": page,
            "count": 50
        }
        
        url = f"{API_URL}/types"
        response = requests.get(url, headers=headers, params=params)
        increment_rate_limit()
        
        if response.status_code != 200:
            print(f"Error fetched: {response.status_code}")
            print(response.text)
            break
            
        data = response.json()
        items = data.get("types", [])
        
        if not items:
            break
            
        saved_on_page = 0
        for item in items:
            # Strictly filter the coins to only the exact denomination we want
            value_text = item.get("value", {}).get("text", "")
            
            # Use lower case to do a soft match since Numista formats can vary slightly
            is_valid = any(v.lower() in value_text.lower() for v in valid_values)
            if not is_valid and value_text != "":
                 # Skip coins that clearly don't match the required denomination
                 continue
                 
            item_id = item.get("id")
            title = item.get("title", "")
            issuer = item.get("issuer", {}).get("name", "United States")
            
            composition = item.get("composition", {}).get("text", "")
            mintage = 0 # Available via /types/{id}/issues normally but takes 1 API call per coin
            other_names = item.get("reference", "")
            
            cursor.execute('''
                INSERT OR REPLACE INTO coins (id, title, issuer, value, composition, mintage, also_known_as, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item_id, title, issuer, value_text, composition, mintage, str(other_names), category))
            
            saved_on_page += 1
            total_coins += 1
            
        conn.commit()
        
        print(f"Page {page} complete. Saved {saved_on_page}/{len(items)} items matching our strict filter. Total saved for {category}: {total_coins}")
        page += 1
        time.sleep(1) # Delay
        
    conn.close()
    print(f"Finished. Total coins strictly saved for {category}: {total_coins}")

def main():
    print("Numista API Fetcher")
    db_path_absolute = os.path.abspath(DB_PATH)
    print(f"Database will be saved to: {db_path_absolute}")
    
    api_key = getpass.getpass("Enter your Numista API Key: ")
    if not api_key:
        print("API Key is required.")
        return
        
    categories = ["$1", "50 Cents", "25 Cents"]
    # We might need to refine the queries for accurate Numista searches
    # For US, usually "dollar", "half dollar", "quarter"
    search_queries = ["dollar", "half dollar", "quarter"]
    
    for query in search_queries:
        if not check_rate_limit():
            break
        fetch_coins(api_key, query)
        
    print("\nFetch execution completed.")

if __name__ == "__main__":
    main()
