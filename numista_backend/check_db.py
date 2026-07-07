import google.auth
from google.cloud import firestore

PROJECT_ID = "studio-9101802118-8c9a8"
credentials, _ = google.auth.default()
db = firestore.Client(credentials=credentials, project=PROJECT_ID)

kb_count = len(list(db.collection('brain_knowledge_base').stream()))
sug_count = len(list(db.collection('brain_suggestions').stream()))

print(f"Knowledge Base: {kb_count} docs")
print(f"Suggestions: {sug_count} docs")
