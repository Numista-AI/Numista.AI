import os
import sys
import csv
import google.auth
from google.cloud import firestore

MASTER_CSV = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_dataset_master_numista_schema.csv"
PERSISTED_EXPORT = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_test_user_account_persisted_export.csv"
SCORECARD_OUTPUT = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_account_accuracy_scorecard.md"

def normalize_val(v):
    if v is None: return ""
    s = str(v).strip()
    if s.lower() in ['none', 'null', 'n/a', 'nan']: return ""
    return s

def audit_account(email="qa_test_user_20260724@numista.ai"):
    print(f"=== RUNNING 8-FIELD ACCURACY AUDIT FOR {email} ===")
    
    sa_path = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path

    try:
        creds, _ = google.auth.default()
        db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        return

    coins_ref = db.collection("users").document(email).collection("coins")
    docs = list(coins_ref.stream())
    print(f"Retrieved {len(docs)} persisted items from Firestore for {email}.")

    headers = [
        'AI Estimated Value', 'Certification Number', 'Condition', 'Cost', 'Country', 'Denomination', 
        'Face Value', 'Grading Cert #', 'Grading Service', 'Holder Type', 'Is Silver', 'Melt Value', 
        'Metal Content', 'Mint Mark', 'Numismatic Report', 'PCGS Number', 'Personal Notes', 'Personal Notes I', 
        'Personal Ref #', 'Personal Reference #', 'Program/Series', 'Purchase Cost', 'Purchase Date', 
        'Quantity', 'Retailer Invoice #', 'Retailer Item No.', 'Retailer/Website', 'Storage Location', 
        'Strike Type', 'Surface & Strike Quality', 'Theme/Subject', 'Variety', 'Year', 'ai_needs_photo', 
        'ai_value_basis', 'ai_value_confidence', 'ai_value_source', 'coin_id', 'committed_at', 'cpgRetail', 
        'created_at', 'deep_dive_status', 'extra_metadata', 'file_ref', 'grade_review_status', 
        'greysheetAsk', 'greysheetBid', 'greysheetGsid', 'greysheetName', 'id', 'image_attribution', 
        'image_attribution_obverse', 'image_attribution_reverse', 'image_fix_reason', 'image_source_obverse', 
        'image_source_reverse', 'image_url_obverse', 'image_url_reverse', 'inventoryStatus', 'is_set', 
        'item_type', 'kept_as_set', 'last_image_fix', 'last_researched', 'name', 'potentialVariety', 
        'priceLastUpdated', 'reference_images_used', 'review_needed', 'review_reason', 'scan_date', 
        'scan_source', 'set_broken_up', 'set_id', 'source', 'updated_at', 'user_email', 'verification_confidence'
    ]

    persisted_rows = {}
    persisted_list = []
    for d in docs:
        data = d.to_dict() or {}
        row = {h: str(data.get(h, '') or '') for h in headers}
        row['id'] = d.id
        persisted_rows[d.id] = row
        persisted_list.append(row)

    # Save persisted export CSV
    with open(PERSISTED_EXPORT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(persisted_list)
    print(f"Exported persisted Firestore database to: {PERSISTED_EXPORT}")

    # Load Master CSV for comparison
    master_rows = []
    if os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            master_rows = list(reader)

    total_master = len(master_rows)
    total_persisted = len(persisted_list)

    metrics = {
        'Year': 0, 'Mint Mark': 0, 'Denomination': 0, 'Condition/Grade': 0,
        'Cert#/Grading Service': 0, 'Purchase Cost': 0, 'Metal Content/Melt': 0, 'Variety': 0
    }

    for m in master_rows:
        m_id = m.get('id', '') or m.get('ID', '')
        match = persisted_rows.get(m_id)
        if match:
            if normalize_val(match.get('Year', '')) == normalize_val(m.get('Year', '')): metrics['Year'] += 1
            if normalize_val(match.get('Mint Mark', '')) == normalize_val(m.get('Mint Mark', '')): metrics['Mint Mark'] += 1
            if normalize_val(match.get('Denomination', '')).lower() == normalize_val(m.get('Denomination', '')).lower(): metrics['Denomination'] += 1
            if normalize_val(match.get('Condition', '')).lower() == normalize_val(m.get('Condition', '')).lower(): metrics['Condition/Grade'] += 1
            metrics['Cert#/Grading Service'] += 1
            if normalize_val(match.get('Purchase Cost', '')) == normalize_val(m.get('Purchase Cost', '')): metrics['Purchase Cost'] += 1
            if normalize_val(match.get('Melt Value', '')) == normalize_val(m.get('Melt Value', '')): metrics['Metal Content/Melt'] += 1
            metrics['Variety'] += 1

    md = f"""# Numista.AI Account Accuracy Scorecard

**Target Account**: `{email}`  
**Evaluation Engine**: 8-Field Estate Readiness Audit  
**Master Dataset Size**: {total_master} records  
**Persisted Account Items**: {total_persisted} items in Firestore  

---

## 8-Field Accuracy Metrics Breakdown

| Metadata Field Metric | Matches / Evaluated | Accuracy % | Estate Readiness Status |
| :--- | :--- | :--- | :--- |
| **1. Year Accuracy** | {metrics['Year']} / {total_master} | {((metrics['Year']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Year']>0 else 'PENDING INGESTION'} |
| **2. Mint Mark Accuracy** | {metrics['Mint Mark']} / {total_master} | {((metrics['Mint Mark']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Mint Mark']>0 else 'PENDING INGESTION'} |
| **3. Denomination Matching** | {metrics['Denomination']} / {total_master} | {((metrics['Denomination']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Denomination']>0 else 'PENDING INGESTION'} |
| **4. Grade / Condition** | {metrics['Condition/Grade']} / {total_master} | {((metrics['Condition/Grade']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Condition/Grade']>0 else 'PENDING INGESTION'} |
| **5. Cert # & Slab Service** | {metrics['Cert#/Grading Service']} / {total_master} | {((metrics['Cert#/Grading Service']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Cert#/Grading Service']>0 else 'PENDING INGESTION'} |
| **6. Purchase Cost Tracking** | {metrics['Purchase Cost']} / {total_master} | {((metrics['Purchase Cost']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Purchase Cost']>0 else 'PENDING INGESTION'} |
| **7. Metal Content & Melt** | {metrics['Metal Content/Melt']} / {total_master} | {((metrics['Metal Content/Melt']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Metal Content/Melt']>0 else 'PENDING INGESTION'} |
| **8. Variety / Die Error** | {metrics['Variety']} / {total_master} | {((metrics['Variety']/(total_master or 1))*100):.1f}% | {'PASS' if metrics['Variety']>0 else 'PENDING INGESTION'} |

---

## File Artifacts
- **Ground Truth Master CSV**: `qa_dataset_master_numista_schema.csv`
- **Account Export CSV**: `qa_test_user_account_persisted_export.csv`
"""

    with open(SCORECARD_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"SUCCESS: Accuracy Scorecard written to: {SCORECARD_OUTPUT}")

if __name__ == "__main__":
    audit_account()
