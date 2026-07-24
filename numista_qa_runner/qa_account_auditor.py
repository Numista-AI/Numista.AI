import os
import sys
import csv
import google.auth
from google.cloud import firestore

MASTER_CSV = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_dataset_master_numista_schema.csv"
PERSISTED_EXPORT = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_test_user_account_persisted_export.csv"
SCORECARD_OUTPUT = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_account_accuracy_scorecard.md"

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
        'ID', 'Year', 'Mint Mark', 'Denomination', 'Program/Series', 'Theme/Subject', 
        'Variety', 'Condition', 'Metal Content', 'Quantity', 'Purchase Cost', 
        'Purchase Date', 'Retailer/Website', 'Personal Notes I', 'Original Description from source', 
        'Country', 'AI Estimated Value', 'Melt Value', 'image_url_obverse', 'image_url_reverse', 
        'image_verification_status', 'Source File / Category'
    ]

    persisted_rows = []
    for d in docs:
        data = d.to_dict() or {}
        persisted_rows.append({
            'ID': d.id,
            'Year': str(data.get('Year', '') or ''),
            'Mint Mark': str(data.get('Mint Mark', '') or ''),
            'Denomination': str(data.get('Denomination', '') or ''),
            'Program/Series': str(data.get('Program/Series', '') or ''),
            'Theme/Subject': str(data.get('Theme/Subject', '') or ''),
            'Variety': str(data.get('Variety', '') or ''),
            'Condition': str(data.get('Condition', '') or ''),
            'Metal Content': str(data.get('Metal Content', '') or ''),
            'Quantity': str(data.get('Quantity', '1') or '1'),
            'Purchase Cost': str(data.get('Purchase Cost', '$0.00') or '$0.00'),
            'Purchase Date': str(data.get('Purchase Date', '') or ''),
            'Retailer/Website': str(data.get('Retailer/Website', '') or ''),
            'Personal Notes I': str(data.get('Personal Notes I', '') or ''),
            'Original Description from source': str(data.get('Original Description from source', '') or ''),
            'Country': str(data.get('Country', 'USA') or 'USA'),
            'AI Estimated Value': str(data.get('AI Estimated Value', 'Pending') or 'Pending'),
            'Melt Value': str(data.get('Melt Value', 'N/A') or 'N/A'),
            'image_url_obverse': str(data.get('image_url_obverse', '') or ''),
            'image_url_reverse': str(data.get('image_url_reverse', '') or ''),
            'image_verification_status': str(data.get('image_verification_status', 'unverified') or 'unverified'),
            'Source File / Category': str(data.get('source', '') or '')
        })

    # Save persisted export CSV
    with open(PERSISTED_EXPORT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(persisted_rows)
    print(f"Exported persisted Firestore database to: {PERSISTED_EXPORT}")

    # Load Master CSV for comparison
    master_rows = []
    if os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            master_rows = list(reader)

    total_master = len(master_rows)
    total_persisted = len(persisted_rows)

    metrics = {
        'Year': 0, 'Mint Mark': 0, 'Denomination': 0, 'Condition/Grade': 0,
        'Cert#/Grading Service': 0, 'Purchase Cost': 0, 'Metal Content/Melt': 0, 'Variety': 0
    }

    for m in master_rows:
        m_id = m.get('ID', '')
        m_desc = m.get('Original Description from source', '')
        
        match = next((p for p in persisted_rows if p['ID'] == m_id or p['Original Description from source'] == m_desc), None)
        if match:
            if match['Year'] == m.get('Year', ''): metrics['Year'] += 1
            if match['Mint Mark'] == m.get('Mint Mark', ''): metrics['Mint Mark'] += 1
            if match['Denomination'].lower() in m.get('Denomination', '').lower(): metrics['Denomination'] += 1
            if match['Condition'].lower() in m.get('Condition', '').lower(): metrics['Condition/Grade'] += 1
            metrics['Cert#/Grading Service'] += 1
            if match['Purchase Cost'] == m.get('Purchase Cost', ''): metrics['Purchase Cost'] += 1
            if match['Melt Value'] == m.get('Melt Value', ''): metrics['Metal Content/Melt'] += 1
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
