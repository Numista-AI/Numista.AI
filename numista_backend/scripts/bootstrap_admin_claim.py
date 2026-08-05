"""
bootstrap_admin_claim.py
-------------------------
Admin utility script to set custom user claim `admin: True` on a target Firebase Auth account.
Run this script locally using the service account credentials.

Usage:
  python bootstrap_admin_claim.py --email admin@numista.ai
"""

import os
import sys
import argparse
import firebase_admin
from firebase_admin import credentials, auth

PROJECT_ID = "studio-9101802118-8c9a8"

def init_firebase():
    if not firebase_admin._apps:
        sa_path = os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json")
        if not os.path.exists(sa_path):
            sa_path = os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json.json")
        if os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={'projectId': PROJECT_ID})

def set_admin_claim(email: str):
    init_firebase()
    try:
        user = auth.get_user_by_email(email)
        existing_claims = user.custom_claims or {}
        existing_claims['admin'] = True
        auth.set_custom_user_claims(user.uid, existing_claims)
        print(f"✅ Successfully granted custom claim 'admin: True' to user: {email} (UID: {user.uid})")
    except auth.UserNotFoundError:
        print(f"❌ User with email '{email}' not found in Firebase Auth.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error setting custom claims: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set custom claim 'admin: True' for a Firebase Auth user.")
    parser.add_argument("--email", required=True, help="Firebase Auth user email to promote to Admin")
    args = parser.parse_args()
    set_admin_claim(args.email)
