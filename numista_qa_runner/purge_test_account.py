import os
import sys
import google.auth
from google.cloud import firestore

def purge_qa_account(email="qa_test_user_20260724@numista.ai"):
    print(f"=== PURGING TEST ACCOUNT: {email} ===")
    
    sa_path = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json"
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path
        
    try:
        creds, _ = google.auth.default()
        db = firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")
    except Exception as e:
        print(f"Error authenticating with Firestore: {e}")
        return False

    user_ref = db.collection("users").document(email)
    coins_ref = user_ref.collection("coins")
    
    deleted_count = 0
    docs = list(coins_ref.limit(500).stream())
    
    while len(docs) > 0:
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
            deleted_count += 1
        batch.commit()
        print(f"Purged batch of {len(docs)} records...")
        docs = list(coins_ref.limit(500).stream())
        
    print(f"SUCCESS: Account {email} fully purged. Total records deleted: {deleted_count}")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "qa_test_user_20260724@numista.ai"
    purge_qa_account(target)
