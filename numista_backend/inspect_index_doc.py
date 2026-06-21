"""
inspect_index_doc.py
Print the raw Firestore structure of AWQ coin_image_index documents
to verify the field structure matches what CoinImageService expects.
"""
import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import google.auth
from google.cloud import firestore

creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')
idx = db.collection('coin_image_index')

check_keys = [
    '2022_nina-otero-warren_american-women-quarters_reverse',
    '2022_nina-otero-warren_american-women-quarters_obverse',
    '2022_american-women-quarters_obverse',
    '2024_celia-cruz_american-women-quarters_reverse',
    # Compare against a known-working old entry
    '1999_new-jersey_50-state-quarters_reverse',
    '2010_arizona_america-the-beautiful_reverse',
]

for key in check_keys:
    doc = idx.document(key).get()
    print(f"\n{'='*60}")
    print(f"KEY: {key}")
    print(f"EXISTS: {doc.exists}")
    if doc.exists:
        data = doc.to_dict()
        for field, val in data.items():
            if isinstance(val, dict):
                print(f"  FIELD '{field}' (dict):")
                for k2, v2 in val.items():
                    v_str = str(v2)[:80]
                    print(f"    '{k2}': {v_str}")
            else:
                print(f"  FIELD '{field}': {str(val)[:80]}")
