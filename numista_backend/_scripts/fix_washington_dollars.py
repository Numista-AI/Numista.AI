# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account
import os

PROJECT_ID = "studio-9101802118-8c9a8"

# Connect to Firebase
print("Connecting to Firestore...")
key_path = "serviceAccountKey.json.json"
if os.path.exists(key_path):
    print("Found explicit service account key.")
    cred = service_account.Credentials.from_service_account_file(key_path)
    db = firestore.Client(credentials=cred, project=PROJECT_ID)
else:
    print("Using Application Default Credentials.")
    # Assuming google-auth will handle it automatically
    import google.auth
    cred, _ = google.auth.default()
    db = firestore.Client(credentials=cred, project=PROJECT_ID)

print("Connected. Scanning all user collections...")

# Get all users
users_ref = db.collection("users")
users = users_ref.stream()

total_fixed = 0

for user_doc in users:
    email = user_doc.id
    print(f"Checking user: {email}")
    
    coins_ref = db.collection(f"users/{email}/coins")
    coins = coins_ref.stream()
    
    batch = db.batch()
    batch_count = 0
    
    for coin_doc in coins:
        data = coin_doc.to_dict()
        needs_update = False
        
        theme = str(data.get('Theme/Subject', '')).strip().lower()
        denom = str(data.get('Denomination', '')).strip().lower()
        prog = str(data.get('Program/Series', '')).strip().lower()
        
        # Rule 1: Washington Theme + Denom 1/Dollar + Presidential Prog
        if 'washington' in theme and denom in ['1', '$1', 'dollar', 'one dollar'] and 'presidential' in prog:
            if data.get('Program/Series') != 'Presidential $1 Coin' or data.get('Denomination') != 'Dollar':
                data['Program/Series'] = 'Presidential $1 Coin'
                data['Denomination'] = 'Dollar'
                needs_update = True
                
        # Rule 2: Denom 1/Dollar + Quarter Prog
        elif denom in ['1', '$1', 'dollar', 'one dollar'] and 'quarter' in prog:
             if 'washington' in theme or 'washington' in prog:
                 data['Program/Series'] = 'Presidential $1 Coin'
                 needs_update = True

        if needs_update:
            print(f"  Fixing coin {coin_doc.id} ({data.get('Year')} {data.get('Denomination')})")
            batch.update(coin_doc.reference, {'Program/Series': data['Program/Series'], 'Denomination': data['Denomination']})
            batch_count += 1
            total_fixed += 1
            
            if batch_count >= 400:
                print("  Committing batch...")
                batch.commit()
                batch = db.batch()
                batch_count = 0
                
    if batch_count > 0:
        print("  Committing final batch for user...")
        batch.commit()

print(f"\nDone! Fixed {total_fixed} coins across all users.")
