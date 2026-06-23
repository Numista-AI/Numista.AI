import os
import sys
from google.cloud import firestore
import google.auth
from google.auth.exceptions import DefaultCredentialsError

# Force UTF-8 output so emoji/box-chars don't crash on Windows cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- CONFIGURATION ---
# Make sure this project ID is correct
PROJECT_ID = "studio-9101802118-8c9a8"

def check_firestore_connection():
    """
    Checks the connection to Firestore and permissions to write.
    """
    print("--- Starting Firestore Connection Debug ---")
    
    # 1. Check for local authentication
    try:
        print(f"Attempting to connect to Firestore project: {PROJECT_ID}")
        credentials, project = google.auth.default()
        print("✅ Google Auth: Credentials loaded successfully.")
        
        # Check if the credentials have a service account email
        if hasattr(credentials, 'service_account_email'):
            print(f"   - Authenticated as service account: {credentials.service_account_email}")
        else:
            # For user credentials from `gcloud auth application-default login`
            # The principal is not directly available in the object in a standard way.
            print("   - Authenticated with user credentials (from gcloud CLI or environment).")

    except DefaultCredentialsError:
        print("❌ Google Auth: Could not find default credentials.")
        print("   - Please run 'gcloud auth application-default login' in your terminal.")
        print("   - This will allow your local environment to authenticate with Google Cloud.")
        print("--- Debug Finished ---")
        return
    except Exception as e:
        print(f"❌ An unexpected error occurred during authentication: {e}")
        print("--- Debug Finished ---")
        return

    # 2. Try to write to Firestore
    try:
        db = firestore.Client(credentials=credentials, project=PROJECT_ID)
        print("✅ Firestore Client: Initialized successfully.")
        
        doc_ref = db.collection("debug_test").document("test_document")
        print("   - Attempting to write a test document to the 'debug_test' collection...")
        
        doc_ref.set({
            "message": "This is a test write from the debug script.",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        print("✅ Firestore Write: Successfully wrote a test document.")
        print("   - This confirms you have the correct permissions to write to Firestore.")
        
        # Clean up the test document
        doc_ref.delete()
        print("   - Cleaned up the test document.")

    except Exception as e:
        print(f"❌ Firestore Write: Failed to write a document.")
        print(f"   - Error: {e}")
        print("   - This could be due to:")
        print("     - Incorrect Firestore permissions for the authenticated user/service account.")
        print("     - The Firestore database not being created in your Google Cloud project.")
        print("     - Firestore Rules blocking the write (though your current rules are open).")

        print("--- Debug Finished ---")

if __name__ == "__main__":
    check_firestore_connection()
