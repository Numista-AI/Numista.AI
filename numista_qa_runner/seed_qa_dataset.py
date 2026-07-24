import os
import csv
import google.auth
from google.cloud import firestore

MASTER_CSV = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_dataset_master_numista_schema.csv"

def seed_qa_account(email="qa_test_user_20260724@numista.ai"):
    print(f"=== INGESTING DATASET ITEMS INTO FIRESTORE FOR {email} ===")
    sa_path = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path

    try:
        creds, _ = google.auth.default()
        db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        return False

    if not os.path.exists(MASTER_CSV):
        print(f"Master CSV not found at: {MASTER_CSV}")
        return False

    with open(MASTER_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    print(f"Loaded {len(records)} records from ground-truth master CSV.")

    user_ref = db.collection("users").document(email)
    coins_ref = user_ref.collection("coins")

    batch = db.batch()
    count = 0
    batch_count = 0
    for r in records:
        count += 1
        doc_id = r.get('id') or r.get('ID') or f'NUM-{count:05d}'
        doc_ref = coins_ref.document(doc_id)
        batch.set(doc_ref, r, merge=True)
        batch_count += 1
        
        if batch_count >= 400:
            batch.commit()
            print(f"Committed batch of {count} / {len(records)} records...")
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
        print(f"Committed final batch. Total: {count} records.")

    print(f"SUCCESS: Ingested all {count} items into Firestore under users/{email}/coins!")
    return True

if __name__ == "__main__":
    seed_qa_account()
