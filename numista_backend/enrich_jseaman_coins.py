# -*- coding: utf-8 -*-
"""
enrich_jseaman_coins.py
-----------------------
Enriches jseaman_unresolved_coins.csv with missing information from:
1. Firestore user collections (users/jseaman1204@gmail.com/coins and users/jseaman1204@gmail.com/currency)
2. PCGS Public API (when a cert number is present)
3. Standard references from SQLite database (numista_coins.db)
"""

import csv
import os
import sys
import json
import urllib.request
import urllib.parse
import sqlite3
from google.oauth2 import service_account
from google.cloud import firestore

# Configure output encoding for terminal
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Configuration ───────────────────────────────────────────────────────────
PROJECT_ID       = "studio-9101802118-8c9a8"
CREDENTIALS_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
DB_FILE          = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\database\numista_coins.db"
INPUT_CSV        = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\data\jseaman_unresolved_coins.csv"
OUTPUT_CSV       = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\data\jseaman_unresolved_coins_enriched.csv"
USER_EMAIL       = "jseaman1204@gmail.com"

# PCGS API
PCGS_TOKEN = "H7yYuwz6oDnLmtz0M-8iaYFEdE9okmmZjL0u_EpOdVgYPOZUKHhaOjdJlPiXy-TTk_lOAzOsRzdm97n2hP3N5LpagAmjIX9xObLNmE3VBefWJU9dtNkU3QH4m1WFIHEiIzVbFUgdZplfWEKfThe3w0FGclodfBim0Vu0SPplpgrzprFzeqkF2Q7Q_zZsHGvXJ4sThOS_7VADHbn1ocRmqhFYb7rglbZ8vMb_wlAyiZjM9Yc7J-5e2A_OW-quh1WdziPtXT3Zxfg7mXOaA7NXDDmnzPkzYNPkKQElLpcY5W27AMDw"
PCGS_BASE  = "https://api.pcgs.com/publicapi"

def call_pcgs_api(path, params=None):
    url = PCGS_BASE + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    
    headers = {
        'Authorization': f'Bearer {PCGS_TOKEN}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'NumistaAI/1.0 (eric@numista.ai)',
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                return json.loads(r.read())
    except Exception as e:
        print(f"      [PCGS API Error] {e}")
    return None

def is_empty(val) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s == "" or s.lower() in ("none", "nan", "n/a")

def get_first_non_empty(d, keys, default=""):
    for k in keys:
        v = d.get(k)
        if not is_empty(v):
            return str(v).strip()
    return default

def main():
    print("=" * 70)
    print("NUMISTA.AI -- COIN DATA ENRICHMENT FOR JSEAMAN1204")
    print("=" * 70)
    
    # 1. Check paths
    if not os.path.exists(CREDENTIALS_FILE):
        sys.exit(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
    if not os.path.exists(INPUT_CSV):
        sys.exit(f"ERROR: Input CSV file not found: {INPUT_CSV}")
        
    # Authenticate Firestore
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    
    # Load input unresolved list
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
        
    print(f"Loaded {len(rows)} unresolved coins from CSV.")
    
    # Add extra enrichment columns if not present
    enriched_fields = [
        "id", "Year", "Mint Mark", "Denomination", "Condition", 
        "Theme/Subject", "Country", "Variety", "PCGS Number",
        "Source Collection", "Grading Service", "Cert Number", "Program/Series",
        "Enrichment Status"
    ]
    
    enriched_rows = []
    enriched_count = 0
    pcgs_count = 0
    not_found_count = 0
    
    # Iterate and enrich
    for idx, row in enumerate(rows, 1):
        doc_id = row.get("id")
        if is_empty(doc_id):
            print(f"[{idx}] Warning: Empty ID, skipping.")
            continue
            
        print(f"[{idx}/{len(rows)}] Processing ID: {doc_id} ...")
        
        # Initialize enriched entry
        entry = {
            "id": doc_id,
            "Year": row.get("Year", ""),
            "Mint Mark": row.get("Mint Mark", ""),
            "Denomination": row.get("Denomination", ""),
            "Condition": row.get("Condition", ""),
            "Theme/Subject": row.get("Theme/Subject", ""),
            "Country": row.get("Country", ""),
            "Variety": row.get("Variety", ""),
            "PCGS Number": row.get("PCGS Number", ""),
            "Source Collection": "Not Found",
            "Grading Service": "",
            "Cert Number": "",
            "Program/Series": "",
            "Enrichment Status": "No Match in Firestore"
        }
        
        # 2. Query Firestore 'coins'
        coin_ref = db.collection("users").document(USER_EMAIL).collection("coins").document(doc_id)
        coin_doc = coin_ref.get()
        
        data = None
        source_col = ""
        
        if coin_doc.exists:
            data = coin_doc.to_dict()
            source_col = "coins"
        else:
            # Try 'currency' subcollection
            curr_ref = db.collection("users").document(USER_EMAIL).collection("currency").document(doc_id)
            curr_doc = curr_ref.get()
            if curr_doc.exists:
                data = curr_doc.to_dict()
                source_col = "currency"
                
        if data:
            entry["Source Collection"] = source_col
            entry["Enrichment Status"] = "Enriched from Firestore"
            enriched_count += 1
            
            # Read fields from Firestore to populate missing/empty columns
            for csv_key, firestore_keys in [
                ("Year", ["Year", "year", "coin_year", "Date", "date"]),
                ("Mint Mark", ["Mint Mark", "mint_mark", "mintMark", "Mint", "mint"]),
                ("Denomination", ["Denomination", "denomination", "Denom", "denom"]),
                ("Condition", ["Condition", "condition", "grade", "Grade"]),
                ("Theme/Subject", ["Theme/Subject", "theme", "subject", "Theme", "Subject", "Description", "description"]),
                ("Country", ["Country", "country"]),
                ("Variety", ["Variety", "variety"]),
                ("PCGS Number", ["PCGS Number", "PCGSNo", "pcgs_number", "greysheetGsid"]),
                ("Grading Service", ["Grading Service", "grading_service", "gradingService"]),
                ("Cert Number", ["Cert Number", "cert_number", "certNumber", "PCGS Cert #", "NGC Cert #", "Cert #"]),
                ("Program/Series", ["Program/Series", "program", "series", "Program", "Series", "coin_type", "type", "Type"])
            ]:
                if is_empty(entry.get(csv_key)):
                    val = get_first_non_empty(data, firestore_keys)
                    if val:
                        entry[csv_key] = val
                        
            # If variety/subject describes a set/collection, let's flag that
            prog = entry.get("Program/Series") or ""
            theme = entry.get("Theme/Subject") or ""
            denom = entry.get("Denomination") or ""
            
            # 3. Hit PCGS API if PCGS Cert number is available
            grading_svc = entry.get("Grading Service") or ""
            cert_no = entry.get("Cert Number") or ""
            
            if grading_svc.upper() == "PCGS" and cert_no:
                print(f"    -> PCGS Cert {cert_no} detected. Calling PCGS API...")
                pcgs_data = call_pcgs_api("/coindetail/GetCoinFactsByCertNumber", {"certno": cert_no})
                if pcgs_data:
                    pcgs_count += 1
                    entry["Enrichment Status"] = "Enriched from Firestore + PCGS API"
                    
                    # Overwrite/fill details from official PCGS certificate details
                    # PCGS returns detailed coin properties in the API response
                    # Struct usually has: 'Year', 'MintMark', 'Denomination', 'PCGSNo', 'Grade', 'Variety', 'SeriesName'
                    coin_details = pcgs_data.get("CoinFacts") or pcgs_data
                    if coin_details:
                        pcgs_year = coin_details.get("Year") or coin_details.get("CoinYear")
                        pcgs_mint = coin_details.get("MintMark")
                        pcgs_denom = coin_details.get("Denomination")
                        pcgs_num = coin_details.get("PCGSNo")
                        pcgs_series = coin_details.get("SeriesName")
                        pcgs_variety = coin_details.get("Variety")
                        pcgs_desc = coin_details.get("Description") or coin_details.get("CoinDescription")
                        
                        if pcgs_year: entry["Year"] = str(pcgs_year)
                        if pcgs_mint: entry["Mint Mark"] = str(pcgs_mint)
                        if pcgs_denom: entry["Denomination"] = str(pcgs_denom)
                        if pcgs_num: entry["PCGS Number"] = str(pcgs_num)
                        if pcgs_series: entry["Program/Series"] = str(pcgs_series)
                        if pcgs_variety: entry["Variety"] = str(pcgs_variety)
                        if pcgs_desc: entry["Theme/Subject"] = str(pcgs_desc)
                        
            # If denomination is still empty and it's a Proof Set / Mint Set, let's auto-fill
            if is_empty(entry.get("Denomination")):
                combined = (prog + " " + theme + " " + denom).lower()
                if "proof set" in combined or "mint set" in combined:
                    # Parse count
                    if "10 coins" in combined or "10-coin" in combined:
                        entry["Denomination"] = "10-Coin Proof Set"
                    elif "5 coins" in combined or "5-coin" in combined:
                        entry["Denomination"] = "5-Coin Proof Set"
                    elif "14 coins" in combined or "14-coin" in combined:
                        entry["Denomination"] = "14-Coin Proof Set"
                    else:
                        entry["Denomination"] = "Proof/Mint Set"
                        
            print(f"    Result: {entry['Denomination']} | {entry['Year']} | {entry['Theme/Subject']} | {entry['Enrichment Status']}")
        else:
            print(f"    -> Document not found in Firestore.")
            not_found_count += 1
            
        enriched_rows.append(entry)
        
    # Write enriched CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=enriched_fields)
        writer.writeheader()
        writer.writerows(enriched_rows)
        
    print("\n" + "=" * 70)
    print("  DATA ENRICHMENT SUMMARY")
    print("=" * 70)
    print(f"  Total CSV rows processed       : {len(rows)}")
    print(f"  Enriched from Firestore        : {enriched_count}")
    print(f"  Enriched from PCGS API         : {pcgs_count}")
    print(f"  Not found in Firestore         : {not_found_count}")
    print(f"  Saved enriched CSV to          : {OUTPUT_CSV}")
    print("=" * 70)

if __name__ == "__main__":
    main()
