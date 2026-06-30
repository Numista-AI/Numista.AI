import sys
import os
from pathlib import Path

# Setup module path
sys.path.append(str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import firebase_admin
from firebase_admin import credentials, firestore

def main():
    key_path = Path(__file__).parent.parent / "serviceAccountKey.json.json"
    
    try:
        firebase_admin.get_app()
    except ValueError:
        if key_path.exists():
            firebase_admin.initialize_app(credentials.Certificate(str(key_path)))
        else:
            print("Error: serviceAccountKey.json.json not found.")
            return

    db = firestore.client()
    
    print("📥 Fetching latest scraper report from Firestore...")
    reports_ref = db.collection("scraper_reports")
    query = reports_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    docs = list(query.stream())
    
    if not docs:
        print("No scraper reports found in Firestore.")
        return
        
    data = docs[0].to_dict()
    report_content = data.get("report_content", "")
    
    output_path = Path(__file__).parent.parent / "latest_scraper_report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("=========================================================")
    print(f"✅ Success! Report saved to: {output_path.name}")
    print("=========================================================")
    print("Summary:")
    print(f"  - Timestamp: {data.get('datetime_utc')}")
    print(f"  - Gaps Filled: {data.get('processed_coins')} Coins / {data.get('processed_errors')} Errors")
    print("=========================================================")
    print("\n👉 Double-click 'latest_scraper_report.md' in VS Code to read it,")
    print("   and press 'Ctrl+K, V' to view the formatted Markdown preview!")

if __name__ == "__main__":
    main()
