"""
set_owner_entitlements.py
=========================
ITEM B1 — Set estate entitlement flags on a user's profile document.

Sets three flags on users/{uid} (the Firebase Auth uid, NEVER email):
  is_lifetime_family_estate: true
  is_ai_qc_account:          true
  beta_tester:               true

These flags are blocked from client writes by firestore.rules (profile
update rule, v2.1 B-ADD-1). Only Admin SDK may set them.

Usage
-----
  # Dry-run (preview — no writes):
  python numista_backend/scripts/set_owner_entitlements.py --uid <firebase_uid> --dry-run

  # Execute:
  python numista_backend/scripts/set_owner_entitlements.py --uid <firebase_uid>

  # Find the uid for an email address first:
  firebase auth:export --format=json | python -c \
    "import json,sys; [print(u['localId']) for u in json.load(sys.stdin)['users'] \
     if u.get('email')=='eric.seaman@yahoo.com']"

Output
------
  set_owner_entitlements_<timestamp>.log
  COMPLETE line: flags written / already-set / errors

Exit codes
----------
  0 — success (or dry-run preview)
  1 — errors encountered
"""

import argparse
import datetime
import logging
import os
import sys

_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
_log_file = f"set_owner_entitlements_{_ts}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger("set_owner_entitlements")

# Flags to set — all must be admin-only server writes.
TARGET_FLAGS = {
    "is_lifetime_family_estate": True,
    "is_ai_qc_account": True,
    "beta_tester": True,
}


def get_firestore_client():
    import firebase_admin
    from firebase_admin import credentials, firestore as admin_firestore

    key_candidates = [
        os.path.join(os.path.dirname(__file__), "..", "serviceAccountKey.json"),
        os.path.join(os.path.dirname(__file__), "..", "..", "serviceAccountKey.json"),
        "serviceAccountKey.json",
    ]
    key_file = None
    for candidate in key_candidates:
        if os.path.exists(candidate):
            key_file = os.path.abspath(candidate)
            break

    if not firebase_admin._apps:
        if key_file:
            cred = credentials.Certificate(key_file)
            firebase_admin.initialize_app(cred)
            log.info(f"Initialized Firebase Admin SDK from: {key_file}")
        else:
            firebase_admin.initialize_app()
            log.info("Initialized Firebase Admin SDK via Application Default Credentials")

    return admin_firestore.client()


def run(uid: str, dry_run: bool = False) -> dict:
    """
    Set entitlement flags on users/{uid}.
    Skips any flag already set to the correct value.
    Never uses email path — uid is the Firebase Auth opaque hash.
    """
    db = get_firestore_client()
    mode = "DRY-RUN" if dry_run else "EXECUTE"
    log.info(f"=== set_owner_entitlements [{mode}] uid={uid} ===")

    profile_ref = db.collection("users").document(uid)
    profile_snap = profile_ref.get()

    if not profile_snap.exists:
        log.warning(f"Document users/{uid} does not exist — will create on set.")

    existing = profile_snap.to_dict() or {} if profile_snap.exists else {}

    to_write = {}
    already_set = []
    for flag, value in TARGET_FLAGS.items():
        if existing.get(flag) == value:
            already_set.append(flag)
            log.info(f"  SKIP (already set): {flag} = {value}")
        else:
            to_write[flag] = value
            log.info(f"  WILL SET: {flag} = {value}  (current: {existing.get(flag, 'MISSING')})")

    errors = 0
    if to_write and not dry_run:
        try:
            from google.cloud import firestore
            profile_ref.set(to_write, merge=True)
            log.info(f"  Wrote {len(to_write)} flag(s) to users/{uid}")
        except Exception as exc:
            log.error(f"  ERROR writing to users/{uid}: {exc}")
            errors += 1

    result = dict(
        uid=uid,
        written=len(to_write) if not dry_run else 0,
        already_set=len(already_set),
        would_write=len(to_write) if dry_run else 0,
        errors=errors,
        dry_run=dry_run,
    )

    log.info("=" * 60)
    log.info(f"SET_OWNER_ENTITLEMENTS {'[DRY-RUN]' if dry_run else 'COMPLETE'}:")
    log.info(f"  uid           : {uid}")
    log.info(f"  Written       : {result['written']}")
    log.info(f"  Would-write   : {result['would_write']} (dry-run only)")
    log.info(f"  Already set   : {result['already_set']}")
    log.info(f"  Errors        : {errors}")
    log.info("=" * 60)
    log.info(f"Log: {os.path.abspath(_log_file)}")
    if not dry_run and errors == 0:
        log.info(f"VERIFY: python numista_backend/scripts/verify_entitlements.py --uid {uid}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set estate entitlement flags on users/{uid} (Admin SDK only)"
    )
    parser.add_argument("--uid", required=True, help="Firebase Auth uid (opaque hash, not email)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    result = run(uid=args.uid, dry_run=args.dry_run)
    sys.exit(0 if result["errors"] == 0 else 1)
