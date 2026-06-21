"""Quick script to read coin_image_index key patterns with subjects."""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

KEY_PATH = Path(__file__).parent / "serviceAccountKey.json.json"
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(credentials.Certificate(str(KEY_PATH)))
db = firestore.client()

docs = list(db.collection("coin_image_index").stream())
print(f"Total docs in coin_image_index: {len(docs)}")

# Show 6+ part keys (subject-specific like year_mint_subject_program_side)
long_keys = [d for d in docs if len(d.id.split("_")) >= 5]
print(f"\n5+ part keys: {len(long_keys)}")
print("(These have subjects — state, president, woman)")
for doc in long_keys[:20]:
    print(f"\n  Doc ID: {doc.id}")
    d = doc.to_dict()
    for k, v in sorted(d.items()):
        if k in ("obverse", "reverse") and isinstance(v, dict):
            url = v.get("public_url", "")[:80]
            attr = v.get("attribution", "")[:40]
            print(f"    {k}: public_url={url}")
            print(f"    {k}: attribution={attr}")
        else:
            print(f"    {k}: {str(v)[:80]}")

# Also look for any AWQ or state-quarter subject keys
print("\n\n=== Looking for state-quarter, women subject keys ===")
subject_keys = [d for d in docs if any(
    x in d.id for x in ["new-jersey", "california", "angelou", "women", "maya"]
)]
for doc in subject_keys[:5]:
    print(f"  {doc.id}")
    d = doc.to_dict()
    for k, v in sorted(d.items()):
        if isinstance(v, dict):
            print(f"    {k}: {list(v.keys())}")
        else:
            print(f"    {k}: {str(v)[:80]}")
