import os, google.auth
from google.cloud import firestore
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './serviceAccountKey.json.json'
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# Try all email variations for aunt
emails_to_try = [
    "JSeaman1204@gmail.com",
    "jseaman1204@gmail.com",
    "Jseaman1204@gmail.com",
    "JSEAMAN1204@gmail.com",
]
for email in emails_to_try:
    coins = list(db.collection('users').document(email).collection('coins').limit(5).stream())
    print(f"  {email}: {len(coins)} coins")

# Also check review_queue for any JSeaman entries
print("\nChecking review_queue for JSeaman...")
rq = list(db.collection('users').document("JSeaman1204@gmail.com").collection('review_queue').limit(5).stream())
print(f"  review_queue: {len(rq)} items")

# Check staging_area
print("Checking staging_area...")
staging = list(db.collection('staging_area').where('user_email', '==', 'JSeaman1204@gmail.com').limit(3).stream())
print(f"  staging_area: {len(staging)} items")
