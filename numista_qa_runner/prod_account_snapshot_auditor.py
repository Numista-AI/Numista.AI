"""
Numista.AI -- Real Production Account Snapshot Auditor
Performs a read-only health audit on real user collection Firestore documents (e.g. jseaman1204@gmail.com).
Detects real-world data gaps, missing images, $0 valuation surprises, and checklist mismatches
BEFORE the user logs in. Robust against real-world price ranges and string formatting.
"""
import os
import re
import json
import time
import google.auth
from google.cloud import firestore

TARGET_EMAIL = "jseaman1204@gmail.com"
REPORT_PATH = os.path.join(os.path.dirname(__file__), "prod_account_audit_report.json")

def parse_safe_float(val):
    """Safely extracts numeric float from strings like '$35.00', '$35 - $50', or None."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.lower() in ["none", "null", "n/a", "nan", ""]:
        return 0.0
    
    # Handle range strings like '$35 - $50' -> take first number
    matches = re.findall(r"\d+(?:\.\d+)?", s.replace(",", ""))
    if matches:
        try:
            return float(matches[0])
        except ValueError:
            return 0.0
    return 0.0

def get_firestore_db():
    sa_path = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json"
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
    try:
        creds, _ = google.auth.default()
        return firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        return None

def audit_production_account(email=TARGET_EMAIL):
    print(f"=== RUNNING REAL PRODUCTION ACCOUNT HEALTH AUDIT FOR {email} ===")
    db = get_firestore_db()
    if not db:
        return {"status": "SKIPPED", "reason": "No Firestore credentials"}

    coins_ref = db.collection("users").document(email).collection("coins")
    docs = list(coins_ref.stream())
    print(f"Fetched {len(docs)} real collection records for {email}.")

    anomalies = []
    missing_images = 0
    zero_value_items = 0
    missing_melt_values = 0

    for d in docs:
        data = d.to_dict() or {}
        doc_id = d.id
        name = data.get("name") or f"{data.get('Year', '')} {data.get('Denomination', '')}"
        
        # Check 1: Missing images
        obv = data.get("imageUrlObverse") or data.get("image_url_obverse")
        rev = data.get("imageUrlReverse") or data.get("image_url_reverse")
        if not obv and not rev:
            missing_images += 1
            anomalies.append({
                "type": "MISSING_IMAGE",
                "id": doc_id,
                "name": name,
                "detail": "Neither obverse nor reverse image URL present"
            })

        # Check 2: Zero valuation on standalone items
        raw_val = data.get("AI Estimated Value") or data.get("cpgRetail") or data.get("Purchase Cost")
        est_val = parse_safe_float(raw_val)
        is_set_child = bool(data.get("parent_set_id") and not data.get("set_broken_up"))
        if est_val == 0.0 and not is_set_child:
            zero_value_items += 1
            anomalies.append({
                "type": "ZERO_VALUATION_SURPRISE",
                "id": doc_id,
                "name": name,
                "detail": "Standalone collection item carrying $0.00 valuation"
            })

        # Check 3: Precious metal missing melt
        metal = (data.get("Metal Content") or "").lower()
        melt = parse_safe_float(data.get("Melt Value"))
        if any(m in metal for m in ["silver", "gold", "platinum"]) and melt == 0.0:
            missing_melt_values += 1
            anomalies.append({
                "type": "MISSING_MELT_VALUE",
                "id": doc_id,
                "name": name,
                "detail": f"Precious metal coin ({metal}) has $0.00 melt value"
            })

    report = {
        "audited_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target_account": email,
        "total_records_audited": len(docs),
        "metrics": {
            "missing_images_count": missing_images,
            "zero_value_items_count": zero_value_items,
            "missing_melt_count": missing_melt_values,
            "total_anomalies_flagged": len(anomalies)
        },
        "anomalies": anomalies[:25] # Top 25 actionable items
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"SUCCESS: Production account audit complete for {email}. Found {len(anomalies)} real-world items needing review.")
    return report

if __name__ == "__main__":
    audit_production_account()
