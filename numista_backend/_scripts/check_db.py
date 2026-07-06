# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
import google.auth

# Use default credentials
cred, default_project = google.auth.default()
db = firestore.Client(credentials=cred, project="studio-9101802118-8c9a8")

paths_to_check = [
    "users/eric@numista.ai/coins",
    "users/eric.seaman@v3tees.com/coins",
    "coins"
]

for path in paths_to_check:
    print(f"Checking path: {path}")
    docs = db.collection(path).limit(5).stream()
    count = 0
    for doc in docs:
        count += 1
        print(f" - Found doc: {doc.id} => {doc.to_dict().get('Year')} {doc.to_dict().get('Denomination')}")
    print(f"Total found in {path} (limited to 5): {count}\n")
