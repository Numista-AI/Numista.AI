# -*- coding: utf-8 -*-
"""
test_greysheet_cache.py
-----------------------
Verifies that the persistent Firestore cache for Greysheet is working.
Makes two consecutive calls to fetch pricing for a GSID:
- Call 1: Fetches from Greysheet API and writes to Firestore.
- Call 2: Fetches directly from Firestore (Cache Hit).
"""

import os
import sys
import logging
from google.oauth2 import service_account
from google.cloud import firestore

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Configure logging to see the service logs
logging.basicConfig(level=logging.INFO)

PROJECT_ID       = "studio-9101802118-8c9a8"
CREDENTIALS_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"

def main():
    print("=" * 70)
    print("  VERIFYING GREYSHEET PERSISTENT CACHE")
    print("=" * 70)
    
    # 1. Initialize DB and Service
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    
    sys.path.append(r"C:\Users\ericd\Documents\MyVertexProject\numista_backend")
    from services.greysheet_service import GreysheetService
    
    service = GreysheetService(db=db)
    
    # Use a dummy GSID for testing
    test_gsid = 73577
    
    # Clean previous test cache if any
    try:
        db.collection("greysheet_cache").document(f"pricing_{test_gsid}").delete()
        print("Cleared previous test cache document.")
    except Exception:
        pass
        
    print("\n--- CALL 1: Fetching pricing (should hit API and write to Cache) ---")
    # We call get_pricing. Since 999999 is a test ID, it might return empty list from API,
    # but the service should still attempt to write to Firestore cache to prevent API load on future calls.
    pricing1 = service.get_pricing(test_gsid)
    print(f"Call 1 completed. Result length: {len(pricing1)}")
    
    print("\n--- CALL 2: Fetching pricing again (should be a Cache Hit from Firestore) ---")
    # Reset in-memory cache to force it to look at Firestore
    service._pricing_cache = {}
    
    pricing2 = service.get_pricing(test_gsid)
    print(f"Call 2 completed. Result length: {len(pricing2)}")
    
    print("\nVerification finished.")
    print("=" * 70)

if __name__ == "__main__":
    main()
