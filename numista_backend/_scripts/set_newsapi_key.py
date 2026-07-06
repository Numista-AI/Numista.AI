# MANDATORY: Before changing this model ID, you MUST read the latest deprecation schedule in: C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules
"""
set_newsapi_key.py
─────────────────────────────────────────────────────────────────────────────
One-time utility: stores your NewsAPI.org API key in Firestore so the backend
/api/mint_news endpoint can use it.

Usage:
  python set_newsapi_key.py YOUR_NEWSAPI_KEY_HERE

Get a free key (500 requests/day dev plan):
  https://newsapi.org/register

Firestore path: config/newsapi  →  { "api_key": "..." }
"""
import sys
import os
from google.cloud import firestore
import google.auth

def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Usage: python set_newsapi_key.py YOUR_NEWSAPI_KEY")
        print("Get a free key at: https://newsapi.org/register")
        sys.exit(1)

    api_key = sys.argv[1].strip()

    # Load credentials from GOOGLE_APPLICATION_CREDENTIALS
    os.environ.setdefault(
        "GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json.json"
    )
    credentials, _ = google.auth.default()
    db = firestore.Client(
        credentials=credentials, project="studio-9101802118-8c9a8"
    )

    doc_ref = db.collection("config").document("newsapi")
    doc_ref.set({"api_key": api_key}, merge=True)
    print(f"✅  NewsAPI key stored in Firestore config/newsapi")
    print(f"    Key prefix: {api_key[:8]}{'*' * (len(api_key) - 8)}")
    print()
    print("The /api/mint_news backend endpoint will now use NewsAPI.org.")
    print("For Cloud Run production: set NEWSAPI_KEY as an env var instead.")

if __name__ == "__main__":
    main()
