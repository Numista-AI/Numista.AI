"""
Numista.AI -- 13 AUG Read-Only Production Account Audit Validator
Audits users/eric.seaman@yahoo.com in strict READ-ONLY mode.
Calculates SHA-256 deep hash of canonical fields to guarantee zero net mutation.
"""
import os
import sys
import json
import time
import hashlib
import google.auth
from google.cloud import firestore

TARGET_EMAIL = "eric.seaman@yahoo.com"
CANONICAL_HASH_FIELDS = [
    "coin_id", "title", "country", "denomination", "year", "mint_mark",
    "is_foreign", "program_series", "theme_subject", "variety_error",
    "estimated_value", "greysheet_value", "melt_value", "purchase_cost"
]

def get_firestore_db():
    sa_path = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json"
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
    try:
        creds, _ = google.auth.default()
        return firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
    except Exception as e:
        print(f"[ERROR] Firestore connection failed: {e}")
        return None

def compute_account_sha256(db, email=TARGET_EMAIL):
    coins_ref = db.collection("users").document(email).collection("coins")
    docs = list(coins_ref.stream())
    
    doc_payloads = []
    for d in sorted(docs, key=lambda x: x.id):
        data = d.to_dict() or {}
        # Construct deterministic canonical representation
        canon = {}
        for k in CANONICAL_HASH_FIELDS:
            val = data.get(k)
            # Normalize types
            if isinstance(val, bool):
                canon[k] = val
            elif isinstance(val, (int, float)):
                canon[k] = round(float(val), 4)
            else:
                canon[k] = str(val or "").strip()
        canon["_id"] = d.id
        doc_payloads.append(canon)

    raw_json = json.dumps(doc_payloads, sort_keys=True)
    digest = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
    return digest, len(docs), doc_payloads

def audit_account_readonly(email=TARGET_EMAIL):
    print(f"=== [READ-ONLY AUDIT] Validating Account: {email} ===")
    db = get_firestore_db()
    if not db:
        return {"status": "ERROR", "message": "Failed to connect to Firestore"}

    digest, count, payloads = compute_account_sha256(db, email)
    print(f"Audited {count} records for {email}.")
    print(f"SHA-256 Digest: {digest}")

    contract_issues = []
    for p in payloads:
        cid = p["_id"]
        country = p.get("country", "")
        is_foreign = p.get("is_foreign")
        mint_mark = p.get("mint_mark", "")
        
        # Rule 1: Country vs is_foreign
        if country and country != "United States" and is_foreign is not True:
            contract_issues.append({
                "id": cid,
                "rule": "FOREIGN_COUNTRY_FLAG_MISMATCH",
                "detail": f"Country '{country}' has is_foreign={is_foreign}"
            })
            
        # Rule 2: Mint mark sanitization
        if mint_mark.lower() in ["(none)", "none", "null", "n/a"]:
            contract_issues.append({
                "id": cid,
                "rule": "UNSANITIZED_MINT_MARK",
                "detail": f"Mint mark carries raw unsanitized string '{mint_mark}'"
            })

    result = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "account": email,
        "record_count": count,
        "sha256_digest": digest,
        "contract_issues_count": len(contract_issues),
        "contract_issues": contract_issues
    }

    report_path = os.path.join(os.path.dirname(__file__), "aug13_audit_validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"[AUDIT COMPLETE] {len(contract_issues)} contract issues flagged. Baseline count: {count}")
    return result

if __name__ == "__main__":
    audit_account_readonly()
