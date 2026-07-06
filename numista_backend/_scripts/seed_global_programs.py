# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
Seed all programs from master_coin_programs.json to global_programs in Firestore.
Skips programs that are already there (won't overwrite existing data).
"""
import json
import re
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = r'c:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

with open('master_coin_programs.json', 'r') as f:
    programs = json.load(f)

# Skip these non-programs
SKIP = {
    "Littleton's Illustrated Guide to Mint Marks on Regular-Issue U.S. Coins",
    "2026 U.S. Circulating Coins",
}

def make_doc_id(name):
    """Convert program name to a clean Firestore document ID."""
    clean = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return clean

existing = {d.id for d in db.collection('global_programs').stream()}
print(f"Already in Firestore: {len(existing)} programs")

added = 0
skipped = 0
for p in programs:
    name = p['name']
    if name in SKIP:
        continue

    doc_id = make_doc_id(name)
    if doc_id in existing:
        print(f"  SKIP (exists): {name}")
        skipped += 1
        continue

    # Normalize varieties: ensure each variety is a dict
    coins = p.get('coins', [])
    normalized_coins = []
    for coin in coins:
        varieties = coin.get('varieties', [])
        normalized_varieties = []
        for v in varieties:
            if isinstance(v, dict):
                normalized_varieties.append(v)
            elif isinstance(v, str):
                normalized_varieties.append({'id': v, 'label': v})
            else:
                normalized_varieties.append({'id': str(v), 'label': str(v)})
        coin_copy = dict(coin)
        coin_copy['varieties'] = normalized_varieties
        normalized_coins.append(coin_copy)

    doc = {
        'name': name,
        'category': p.get('category', 'Other'),
        'years': p.get('years', ''),
        'mint_mark_locations': p.get('mint_mark_locations', ''),
        'mint_mark_type': p.get('mint_mark_type', ''),
        'mint_mark_description': p.get('mint_mark_description', ''),
        'coins': normalized_coins,
        'last_synced': firestore.SERVER_TIMESTAMP,
    }

    db.collection('global_programs').document(doc_id).set(doc)
    print(f"  ADDED: {name} ({len(normalized_coins)} coins) -> {doc_id}")

    added += 1

print(f"\nDone. Added: {added}, Skipped (already existed): {skipped}")
