#!/usr/bin/env python3
"""
upgrade_beta_testers_to_estate.py

Upgrades Beta testers, Founders, Family, Influencers, and AI QC accounts in Firestore.
Keyed by root document `users/{user_email}` as well as user UID mappings.

Usage:
  python upgrade_beta_testers_to_estate.py --dry-run   (Default: logs planned updates without writing)
  python upgrade_beta_testers_to_estate.py --commit    (Applies updates to Firestore)
"""

import sys
import os
import argparse
from datetime import datetime, timezone
import openpyxl
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK if not initialized
def init_firestore():
    if not firebase_admin._apps:
        key_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred, {'projectId': 'studio-9101802118-8c9a8'})
        else:
            firebase_admin.initialize_app(options={'projectId': 'studio-9101802118-8c9a8'})
    return firestore.client()

# Hardcoded account classifications from master strategy and Account 10 AUG 26.xlsx
FOUNDER_AND_FAMILY = {
    'eric.seaman@yahoo.com',
    'seaman_duane@yahoo.com',
    'thetoadboy@yahoo.com',
    'eric@numista.ai',
    'jseaman1204@gmail.com',
}

INFLUENCERS = {
    'billie@greysheet.com',
}

AI_QC_EMAILS = {
    'beta@numista.ai',
    'qa_test_user_20260724@numista.ai',
    'qabrowser@numista.ai',
    'betauser01@numista.ai',
    'betauser069@numista.ai',
}

AI_QC_UIDS = {
    'HslBeUkLAsPdRr5SkW2fPV4BpOy1',
    'Ehdk3F27U2hhYKV8TRGpCiYWeCF2',
    'CQNL3b6ttnWMavtxRWE2WMmR2rU2',
    'NujQFhBAJSO22WWo20pG81FISX13',
    'YtUKSnx4CpPQNWssrAj4jKUp8L53',
    'GroxSUojlxUY3bTHBcTWvdIZwIA2',
    'cDly8k07tvSzMsJ6F50rgFCyubO2',
    'xC2IcqkTfxO2eX9NeJHzRD9Cj4d2',
    'drfMvgySeXbnDpOpwOa3m6Evhzt1',
    'aGKWSALD5YTGEeU0PPTE0o5GTim1',
    '1YTlzreKrQZNtyQjNw0md6cPGrw2',
}

EXCEL_PATH = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\10 AUG 26\Account 10 AUG 26.xlsx"

def run_upgrade(commit=False):
    db = init_firestore()
    now_iso = datetime.now(timezone.utc).isoformat()
    expires_24mo_iso = "2028-08-10T00:00:00Z"

    print("=" * 80)
    print(f" NUMISTA.AI BETA TESTER UPGRADE SCRIPT — MODE: {'LIVE COMMIT' if commit else 'DRY RUN'}")
    print("=" * 80)

    # 1. Parse Excel file if present
    excel_accounts = []
    if os.path.exists(EXCEL_PATH):
        try:
            wb = openpyxl.load_workbook(EXCEL_PATH)
            ws = wb.active
            for row in list(ws.iter_rows(values_only=True))[1:]:
                if not any(row):
                    continue
                identifier = str(row[0] or '').strip().lower()
                uid = str(row[4] or '').strip()
                action = str(row[5] or '').strip()
                offer_beta = str(row[6] or '').strip()
                excel_accounts.append({
                    'identifier': identifier,
                    'uid': uid,
                    'action': action,
                    'offer_beta': offer_beta,
                })
            print(f"[+] Loaded {len(excel_accounts)} account records from Excel.")
        except Exception as e:
            print(f"[!] Warning reading Excel: {e}")
    else:
        print(f"[!] Excel file not found at {EXCEL_PATH}. Proceeding with Firestore scanning.")

    # 2. Fetch all user documents from Firestore root collection `users`
    print("[+] Fetching existing `users` documents from Firestore...")
    users_snap = db.collection('users').get()
    print(f"[+] Found {len(users_snap)} user documents in Firestore.")

    stats = {
        'founders_family': 0,
        'influencers': 0,
        'ai_qc': 0,
        'real_beta_testers': 0,
        'other': 0,
    }

    real_beta_emails = set()

    for doc in users_snap:
        user_key = doc.id.lower().strip()
        data = doc.to_dict() or {}
        email = (data.get('email') or user_key).lower().strip()
        uid = data.get('uid') or data.get('user_id') or doc.id

        is_founder = email in FOUNDER_AND_FAMILY or user_key in FOUNDER_AND_FAMILY
        is_influencer = email in INFLUENCERS or user_key in INFLUENCERS
        is_ai_qc = email in AI_QC_EMAILS or uid in AI_QC_UIDS or 'anonymous' in user_key or 'qc' in user_key

        payload = {}
        category = ""

        if is_founder:
            category = "Founder / Family (Lifetime Super User)"
            payload = {
                'stripe_tier': 'family_estate',
                'tier': 'family_estate',
                'is_lifetime_family_estate': True,
                'beta_tester': True,
                'updated_at': now_iso,
            }
            stats['founders_family'] += 1

        elif is_influencer:
            category = "Influencer / Partner (Lifetime Super User)"
            payload = {
                'stripe_tier': 'family_estate',
                'tier': 'family_estate',
                'is_lifetime_family_estate': True,
                'beta_tester': True,
                'updated_at': now_iso,
            }
            stats['influencers'] += 1

        elif is_ai_qc:
            category = "AI QC / Internal Testing Account (Bypasses 50 Cap)"
            payload = {
                'stripe_tier': 'family_estate',
                'tier': 'family_estate',
                'is_ai_qc_account': True,
                'beta_tester': True,
                'updated_at': now_iso,
            }
            stats['ai_qc'] += 1

        else:
            # Real Beta Tester
            category = "Real Beta Tester (24-Month Upgrade)"
            payload = {
                'stripe_tier': 'family_estate',
                'tier': 'family_estate',
                'beta_tester': True,
                'beta_access_expires': expires_24mo_iso,
                'updated_at': now_iso,
            }
            stats['real_beta_testers'] += 1
            real_beta_emails.add(email)

        print(f" - [{category}] Target: {doc.id} ({email}) -> {payload}")

        if commit and payload:
            # Merge payload to root user document
            db.collection('users').document(doc.id).set(payload, merge=True)
            # Also write status to subscription/status subdocument for legacy backwards compatibility
            db.collection('users').document(doc.id).collection('subscription').document('status').set(payload, merge=True)

    active_beta_count = len(real_beta_emails)
    status_payload = {
        'active_beta_count': active_beta_count,
        'max_beta_limit': 50,
        'updated_at': now_iso,
    }

    print("\n" + "=" * 80)
    print(" SUMMARY OF ACCOUNT ENTITLEMENT UPDATES")
    print("=" * 80)
    print(f" Founders & Family (Lifetime Super User): {stats['founders_family']}")
    print(f" Influencers & Partners (Lifetime Super User): {stats['influencers']}")
    print(f" AI QC / Internal Test Accounts:           {stats['ai_qc']}")
    print(f" Real Beta Testers (24-Month Upgrade):     {stats['real_beta_testers']}")
    print(f" Total Real Beta Count towards 50 Limit:    {active_beta_count} / 50")
    print("=" * 80)

    if commit:
        db.collection('config').document('beta_status').set(status_payload, merge=True)
        print("[+] Firestore `config/beta_status` updated successfully.")
        print("[+] LIVE COMMIT COMPLETE! All entitlements upgraded.")
    else:
        print("[*] DRY RUN COMPLETE. No changes were written to Firestore. Pass --commit to write changes.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Upgrade Beta Testers to Family Estate tier.")
    parser.add_argument('--commit', action='store_true', help="Commit changes to Firestore.")
    args = parser.parse_args()
    run_upgrade(commit=args.commit)
