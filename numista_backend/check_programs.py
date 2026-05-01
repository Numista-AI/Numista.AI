"""Remove duplicate programs that were double-seeded with different doc IDs."""
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# These are the NEWER duplicates added by seed_global_programs.py.
# The OLDER doc IDs (fifty_state_quarters, america_the_beautiful_quarters, etc.) are kept.
DUPLICATES_TO_DELETE = [
    '50_state_quarters',                          # dupe of fifty_state_quarters
    'america_the_beautiful_quarters_national_parks',  # dupe of america_the_beautiful_quarters
    'american_innovation_1_coin_program',          # dupe of american_innovation_dollars
    'd_c_u_s_territories_quarters',               # dupe of dc_territories_quarters
]

for doc_id in DUPLICATES_TO_DELETE:
    db.collection('global_programs').document(doc_id).delete()
    print(f"Deleted: {doc_id}")

print("Done. Duplicates removed.")
