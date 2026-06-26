import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (assuming default credentials or initialized app)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

EMAIL = 'jseaman1204@gmail.com'
AI_SOURCES = {'Binder Scan', 'PDF Invoice', 'Binder Checklist', 'document_ai'}

def run_migration():
    print(f"Starting migration for user: {EMAIL}")
    coins_ref = db.collection('users').document(EMAIL).collection('coins')
    
    # We will scan all coins for this user because we are backfilling missing fields
    docs = list(coins_ref.stream())
    print(f"Found {len(docs)} total coins for {EMAIL}.")
    
    batch = db.batch()
    updated_count = 0
    total_committed = 0
    
    for doc in docs:
        d = doc.to_dict()
        source = d.get('source', '')
        conf_val = d.get('confidence_score')
        conf = float(conf_val) if conf_val is not None else 1.0
        
        # Check if it's an AI modality
        is_ai = source in AI_SOURCES or conf < 0.95
        if not is_ai:
            continue
            
        status = d.get('grade_review_status')
        reviews = d.get('grade_reviews', [])
        is_reviewed = any(
            (isinstance(r, dict) and r.get('reviewer') == EMAIL) or (isinstance(r, str) and r == EMAIL)
            for r in reviews
        )
        
        # If it was never explicitly marked reviewed, or confirmed, or flagged, and it has no reviews:
        if status not in ['confirmed', 'flagged_for_admin_review'] and not is_reviewed:
            # We explicitly write it as pending
            if status != 'pending':
                batch.update(doc.reference, {'grade_review_status': 'pending'})
                updated_count += 1
                
                if updated_count == 400:
                    batch.commit()
                    total_committed += updated_count
                    print(f"Committed batch of {updated_count}. Total so far: {total_committed}")
                    batch = db.batch()
                    updated_count = 0
                    
    if updated_count > 0:
        batch.commit()
        total_committed += updated_count
        print(f"Committed final batch of {updated_count}. Total updated: {total_committed}")
        
    print(f"Migration complete. Total updated documents: {total_committed}")

if __name__ == '__main__':
    run_migration()
