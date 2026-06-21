import os, sys
os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', './serviceAccountKey.json.json')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Use google.cloud.firestore admin SDK to test if currency collection is readable
import google.auth
from google.cloud import firestore
creds, _ = google.auth.default()
db = firestore.Client(credentials=creds, project='studio-9101802118-8c9a8')

# Try to list documents in currency collection
col = db.collection('users').document('jseaman1204@gmail.com').collection('currency')
docs = list(col.limit(3).stream())
print(f'currency collection readable: {len(docs)} docs (using admin creds)')

# Check if there are any collections under the user document
user_ref = db.document('users/jseaman1204@gmail.com')
print('\nSub-collections under AJ user doc:')
for coll in user_ref.collections():
    print(f'  - {coll.id}')
