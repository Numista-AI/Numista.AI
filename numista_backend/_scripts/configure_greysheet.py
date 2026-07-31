import sys
import os
import getpass
from google.cloud import firestore
import google.auth

def main():
    print("=" * 60)
    print("Greysheet API Credentials Setup")
    print("=" * 60)
    print("This script will securely write your production Greysheet credentials")
    print("to the Firestore config/greysheet document.")
    print("")

    # Prompt securely using getpass
    api_key = getpass.getpass("Enter GREYSHEET_API_KEY (typing hidden): ").strip()
    if not api_key:
        print("Error: API Key cannot be empty.")
        sys.exit(1)

    api_token = getpass.getpass("Enter GREYSHEET_API_TOKEN (typing hidden): ").strip()
    if not api_token:
        print("Error: API Token cannot be empty.")
        sys.exit(1)

    PROJECT_ID = "studio-9101802118-8c9a8"
    print(f"\nConnecting to Firestore project '{PROJECT_ID}'...")

    try:
        # Initialize Firestore Client
        db = firestore.Client(project=PROJECT_ID)
        
        doc_ref = db.collection("config").document("greysheet")
        
        # Write keys
        doc_ref.set({
            "apiKey": api_key,
            "apiToken": api_token
        }, merge=True)
        
        # Verify (masked)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            if data.get("apiKey") and data.get("apiToken"):
                print("\n[SUCCESS] Credentials successfully written to Firestore!")
                print(f"  - Document: config/greysheet")
                print("  - apiKey:   [set]")
                print("  - apiToken: [set]")
            else:
                print("\n[ERROR] Document config/greysheet could not be verified after write.")
                sys.exit(1)
            
    except Exception:
        print("\n[ERROR] Failed to write credentials. Check your GCP credentials and Firestore access.")
        sys.exit(1)

if __name__ == "__main__":
    main()
