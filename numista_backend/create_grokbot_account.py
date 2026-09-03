#!/usr/bin/env python3
"""
create_grokbot_account.py
=========================
Creates a Firebase Auth user and Firestore user document for the Grok Bot
testing account: grokbot@numista.ai

Tier: sovereign (unlimited deepdives/invoice scans)

Usage:
  python create_grokbot_account.py           # Dry-run: prints what WOULD be created
  python create_grokbot_account.py --commit  # Creates Auth user + Firestore doc
"""

import argparse
import os
import sys
import secrets
import string
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore, auth

# Force UTF-8 output on Windows to avoid cp1252 emoji errors
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
SA_KEY_PATH = os.path.join(SCRIPT_DIR, "serviceAccountKey.json")
if not os.path.exists(SA_KEY_PATH):
    SA_KEY_PATH = os.path.join(SCRIPT_DIR, "serviceAccountKey.json.json")

PROJECT_ID  = "studio-9101802118-8c9a8"

BOT_EMAIL       = "grokbot@numista.ai"
BOT_DISPLAY_NAME = "Grok Bot (Testing)"
BOT_TIER        = "sovereign"

# ─── INIT ─────────────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    if os.path.exists(SA_KEY_PATH):
        cred = credentials.Certificate(SA_KEY_PATH)
        firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
    else:
        firebase_admin.initialize_app(options={"projectId": PROJECT_ID})

db = firestore.client()


def generate_password(length: int = 20) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def run(commit: bool = False):
    now_iso = datetime.now(timezone.utc).isoformat()
    password = generate_password()

    print("=" * 60)
    print(f"  GROK BOT ACCOUNT CREATION — MODE: {'LIVE' if commit else 'DRY RUN'}")
    print("=" * 60)
    print(f"  Email        : {BOT_EMAIL}")
    print(f"  Display Name : {BOT_DISPLAY_NAME}")
    print(f"  Tier         : {BOT_TIER}")
    if commit:
        print(f"  Password     : {password}")
    else:
        print(f"  Password     : (will be generated on --commit)")
    print()

    # ── Step 1: Check if Auth user already exists ─────────────────────────────
    existing_uid = None
    try:
        existing_user = auth.get_user_by_email(BOT_EMAIL)
        existing_uid  = existing_user.uid
        print(f"[AUTH] User already exists in Firebase Auth — UID: {existing_uid}")
    except auth.UserNotFoundError:
        print(f"[AUTH] No existing Firebase Auth user found for {BOT_EMAIL}.")

    # ── Step 2: Check if Firestore doc already exists ─────────────────────────
    doc_ref  = db.collection("users").document(BOT_EMAIL)
    doc_snap = doc_ref.get()
    if doc_snap.exists:
        print(f"[FIRESTORE] Document already exists: users/{BOT_EMAIL}")
        print(f"  Existing data: {doc_snap.to_dict()}")

    print()

    if not commit:
        print("[DRY RUN] No changes made. Run with --commit to create the account.")
        return

    # ── Step 3: Create or fetch Auth user ────────────────────────────────────
    if existing_uid:
        uid = existing_uid
        print(f"[AUTH] Reusing existing UID: {uid}")
    else:
        try:
            new_user = auth.create_user(
                email        = BOT_EMAIL,
                password     = password,
                display_name = BOT_DISPLAY_NAME,
                email_verified = True,
            )
            uid = new_user.uid
            print(f"[AUTH] ✅ Created Firebase Auth user — UID: {uid}")
        except Exception as e:
            print(f"[AUTH] ❌ Failed to create Auth user: {e}")
            sys.exit(1)

    # ── Step 4: Write Firestore user document ─────────────────────────────────
    user_doc = {
        "email"              : BOT_EMAIL,
        "uid"                : uid,
        "display_name"       : BOT_DISPLAY_NAME,
        "tier"               : BOT_TIER,
        "stripe_tier"        : BOT_TIER,
        "is_ai_qc_account"   : True,
        "is_bot_account"     : True,
        "beta_tester"        : False,
        "created_at"         : now_iso,
        "updated_at"         : now_iso,
        "notes"              : "Grok Bot testing account — sovereign tier, internal use only",
    }

    try:
        doc_ref.set(user_doc, merge=True)
        print(f"[FIRESTORE] ✅ User document written: users/{BOT_EMAIL}")
    except Exception as e:
        print(f"[FIRESTORE] ❌ Failed to write Firestore document: {e}")
        sys.exit(1)

    # ── Step 5: Also write by UID (secondary lookup) ──────────────────────────
    try:
        db.collection("users").document(uid).set(user_doc, merge=True)
        print(f"[FIRESTORE] ✅ UID-keyed document written: users/{uid}")
    except Exception as e:
        print(f"[FIRESTORE] ⚠️  Could not write UID-keyed document: {e}")

    print()
    print("=" * 60)
    print("  ACCOUNT CREATION COMPLETE")
    print("=" * 60)
    print(f"  Email   : {BOT_EMAIL}")
    print(f"  UID     : {uid}")
    print(f"  Tier    : {BOT_TIER}")
    print(f"  Password: {password}")
    print()
    print("  ⚠️  Save this password — it cannot be recovered later.")
    print("     You can reset it anytime via the Firebase Console.")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Grok Bot testing account.")
    parser.add_argument("--commit", action="store_true",
                        help="Actually create the account (default is dry-run).")
    args = parser.parse_args()
    run(commit=args.commit)
