# -*- coding: utf-8 -*-
"""
nightly_data_audit.py
---------------------
Performs nightly data integrity and image audits across all user collections
in Firestore and writes a summary report directly into the 'weekly_audits' 
collection so it is visible to admins and user portals.
"""

import os
import sys
from datetime import datetime, timezone
from google.oauth2 import service_account
from google.cloud import firestore

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Configuration ───────────────────────────────────────────────────────────
PROJECT_ID       = "studio-9101802118-8c9a8"
CREDENTIALS_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
TARGET_USERS     = ["eric@numista.ai", "jseaman1204@gmail.com"]

def is_empty(val) -> bool:
    if val is None:
        return True
    s = str(val).strip()
    return s == "" or s.lower() in ("none", "nan", "n/a")

def get_val(d, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v is not None and str(v).strip() not in ("", "None", "nan"):
            return str(v).strip()
    return default

def main():
    print("=" * 70)
    print("  NUMISTA.AI -- NIGHTLY SYSTEM DATA AUDIT RUN")
    print("=" * 70)
    
    if not os.path.exists(CREDENTIALS_FILE):
        sys.exit(f"ERROR: Credentials file not found: {CREDENTIALS_FILE}")
        
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    
    summary_findings = []
    total_coins_scanned = 0
    total_currency_scanned = 0
    flagged_count = 0
    
    for email in TARGET_USERS:
        print(f"\nScanning collections for {email}...")
        
        # 1. Audit Coins
        coins_ref = db.collection("users").document(email).collection("coins")
        coin_docs = list(coins_ref.stream())
        total_coins_scanned += len(coin_docs)
        print(f"  - Coins in collection: {len(coin_docs)}")
        
        for doc in coin_docs:
            d = doc.to_dict() or {}
            doc_id = doc.id
            
            # Read properties
            year = get_val(d, "Year", "year", "coin_year", "date", "Date")
            denom = get_val(d, "Denomination", "denomination", "face_value")
            program = get_val(d, "Program/Series", "program", "series")
            obv = d.get("image_url_obverse", "").strip()
            rev = d.get("image_url_reverse", "").strip()
            
            reasons = []
            
            # Checks
            if is_empty(obv) and is_empty(rev):
                reasons.append("Missing both images")
            elif is_empty(obv):
                reasons.append("Missing obverse image")
            elif is_empty(rev):
                reasons.append("Missing reverse image")
                
            if is_empty(denom):
                reasons.append("Missing Denomination")
            if is_empty(year):
                reasons.append("Missing Year")
                
            # Check year mismatches in URL path (if any)
            if not is_empty(year) and len(year) == 4 and year.isdigit():
                for img_url, label in [(obv, "Obverse"), (rev, "Reverse")]:
                    if img_url and year not in img_url:
                        # Extract year from URL if present
                        import re
                        years_in_url = re.findall(r'/(\d{4})[-_]', img_url)
                        if years_in_url and years_in_url[0] != year:
                            reasons.append(f"{label}: Year mismatch (coin is {year} but URL contains {years_in_url[0]})")
                            
            if reasons:
                flagged_count += 1
                summary_findings.append({
                    "id": doc_id,
                    "user_email": email,
                    "type": "coin",
                    "name": f"{year} {denom} - {program}" if not is_empty(year) else f"Unknown Coin (ID: {doc_id})",
                    "issues": reasons,
                    "checked_at": datetime.now(timezone.utc).isoformat()
                })
                
        # 2. Audit Currency
        curr_ref = db.collection("users").document(email).collection("currency")
        curr_docs = list(curr_ref.stream())
        total_currency_scanned += len(curr_docs)
        print(f"  - Currency in collection: {len(curr_docs)}")
        
        for doc in curr_docs:
            d = doc.to_dict() or {}
            doc_id = doc.id
            
            year = get_val(d, "Year", "year", "Date", "date")
            denom = get_val(d, "Denomination", "denomination")
            obv = d.get("image_url_obverse", "").strip()
            
            reasons = []
            if is_empty(obv):
                reasons.append("Missing obverse banknote image")
            if is_empty(denom):
                reasons.append("Missing Denomination")
                
            if reasons:
                flagged_count += 1
                summary_findings.append({
                    "id": doc_id,
                    "user_email": email,
                    "type": "currency",
                    "name": f"{year} {denom} Note" if not is_empty(year) else f"Unknown Banknote (ID: {doc_id})",
                    "issues": reasons,
                    "checked_at": datetime.now(timezone.utc).isoformat()
                })
                
    # 3. Save Summary to Firestore 'weekly_audits'
    report_id = f"audit_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    report_ref = db.collection("weekly_audits").document(report_id)
    
    report_data = {
        "report_id": report_id,
        "run_date": datetime.now(timezone.utc).isoformat(),
        "total_coins_scanned": total_coins_scanned,
        "total_currency_scanned": total_currency_scanned,
        "flagged_items_count": flagged_count,
        "flagged_items": summary_findings[:100],  # cap list of items in main doc for size
        "status": "COMPLETED"
    }
    
    try:
        report_ref.set(report_data)
        print(f"\n[OK] Audit summary saved successfully to Firestore: weekly_audits/{report_id}")
    except Exception as e:
        print(f"\n[ERROR] Failed to save audit summary: {e}")
        
    print("\n" + "=" * 70)
    print("  NIGHTLY AUDIT SUMMARY")
    print("=" * 70)
    print(f"  Total Coins Scanned            : {total_coins_scanned}")
    print(f"  Total Currency Scanned         : {total_currency_scanned}")
    print(f"  Flagged Items with Issues      : {flagged_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
