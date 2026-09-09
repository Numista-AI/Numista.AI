#!/usr/bin/env python3
"""
fix_26rj_phase2.py
==================
Performs Phase 2 remediation for the 2026 Uncirculated Coin Set (26RJ):

Fix 1: Patch `coin_set_index/uncirculated-coin-set-2026`
- Reads document from collection `coin_set_index`, doc ID `uncirculated-coin-set-2026`
- Identifies entries in `coins` array where denomination == 'set' (packaging cards)
- Moves those entries into a new field `cards` (as a list)
- Removes those entries from `coins` array so only the 20 actual coins remain
- Updates `coin_count` to 20
- Uses merge=True to preserve all other fields

Fix 2: Patch Eric's parent document
- Collection path: `users/eric.seaman@yahoo.com/coins`
- Document ID: `71e2d4ae92bc4312a4198a3a0cc21fcb`
- Updates fields:
    * `image_url_obverse` -> canonical 26RJ obverse packaging card (26rj_c.jpg)
    * `image_url_reverse` -> canonical 26RJ reverse packaging card (26rj_e.jpg)
    * `Retailer Item No.` -> '26RJ'
    * `product_code`      -> '26RJ'
- Safety check: Confirms current `image_url_obverse` contains 'marine-corps' before updating
- Uses merge=True to preserve all other fields

Project:
    studio-9101802118-8c9a8

Usage:
    python fix_26rj_phase2.py             # Dry-run preview (default)
    python fix_26rj_phase2.py --dry-run   # Explicit dry-run
    python fix_26rj_phase2.py --execute   # Firestore update with merge=True
"""

import argparse
from datetime import datetime, timezone
import io
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
elif sys.stdout and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
elif sys.stderr and hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)

import google.auth
from google.cloud import firestore
from google.oauth2 import service_account

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ID = "studio-9101802118-8c9a8"

# Fix 1 constants
FIX1_COLLECTION = "coin_set_index"
FIX1_DOC_ID = "uncirculated-coin-set-2026"
EXPECTED_COIN_COUNT = 20

# Fix 2 constants
FIX2_USER = "eric.seaman@yahoo.com"
FIX2_DOC_ID = "71e2d4ae92bc4312a4198a3a0cc21fcb"
OBVERSE_REPLACEMENT_URL = (
    "https://storage.googleapis.com/numista-reference-library/reference_library/"
    "user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_c.jpg"
)
REVERSE_REPLACEMENT_URL = (
    "https://storage.googleapis.com/numista-reference-library/reference_library/"
    "user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg"
)
RETAILER_ITEM_NO = "26RJ"
PRODUCT_CODE = "26RJ"
SAFETY_URL_FRAGMENT = "marine-corps"


# ─────────────────────────────────────────────────────────────────────────────
# FIRESTORE CLIENT INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def get_firestore_client(project_id: str = PROJECT_ID) -> firestore.Client:
    """
    Initializes and returns a Google Cloud Firestore client.
    Checks GOOGLE_APPLICATION_CREDENTIALS, local serviceAccountKey files,
    and falls back to Application Default Credentials (ADC).
    """
    env_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_creds and os.path.exists(env_creds):
        creds = service_account.Credentials.from_service_account_file(env_creds)
        return firestore.Client(project=project_id, credentials=creds)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    workspace_dir = os.path.abspath(os.path.join(backend_dir, ".."))
    candidate_keys = [
        os.path.join(backend_dir, "serviceAccountKey.json"),
        os.path.join(backend_dir, "serviceAccountKey.json.json"),
        os.path.join(script_dir, "serviceAccountKey.json"),
        os.path.join(script_dir, "serviceAccountKey.json.json"),
        os.path.join(workspace_dir, "serviceAccountKey.json"),
        os.path.join(workspace_dir, "serviceAccountKey.json.json"),
        os.path.join(os.getcwd(), "serviceAccountKey.json"),
        os.path.join(os.getcwd(), "serviceAccountKey.json.json"),
    ]

    for key_path in candidate_keys:
        if os.path.exists(key_path):
            creds = service_account.Credentials.from_service_account_file(key_path)
            return firestore.Client(project=project_id, credentials=creds)

    creds, _ = google.auth.default()
    return firestore.Client(project=project_id, credentials=creds)


# ─────────────────────────────────────────────────────────────────────────────
# INSPECTION & REMEDIATION LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def inspect_fix1(db: firestore.Client) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Inspects coin_set_index/uncirculated-coin-set-2026.
    Returns: (needs_update, update_payload, report_info)
    """
    doc_ref = db.collection(FIX1_COLLECTION).document(FIX1_DOC_ID)
    doc_snap = doc_ref.get()

    info: Dict[str, Any] = {
        "doc_path": f"{FIX1_COLLECTION}/{FIX1_DOC_ID}",
        "exists": doc_snap.exists,
        "current_coin_count": None,
        "current_coins_len": 0,
        "current_cards_len": 0,
        "set_entries_found": 0,
        "status": "UNKNOWN",
        "doc_ref": doc_ref,
    }

    if not doc_snap.exists:
        info["status"] = "NOT_FOUND"
        return False, None, info

    data = doc_snap.to_dict() or {}
    coins: List[Dict[str, Any]] = data.get("coins") or []
    cards: List[Dict[str, Any]] = data.get("cards") or []
    coin_count = data.get("coin_count")

    info["current_coin_count"] = coin_count
    info["current_coins_len"] = len(coins)
    info["current_cards_len"] = len(cards)

    # Separate packaging cards from coins
    card_entries = [c for c in coins if str(c.get("denomination", "")).strip().lower() == "set"]
    coin_entries = [c for c in coins if str(c.get("denomination", "")).strip().lower() != "set"]

    info["set_entries_found"] = len(card_entries)
    info["remaining_coins_len"] = len(coin_entries)
    info["card_names"] = [c.get("name") or c.get("label") or "Card" for c in card_entries]

    if len(card_entries) > 0:
        # Move packaging cards to cards list, keeping any existing cards
        new_cards = list(cards) if cards else []
        for card in card_entries:
            if card not in new_cards:
                new_cards.append(card)

        payload = {
            "coins": coin_entries,
            "cards": new_cards,
            "coin_count": EXPECTED_COIN_COUNT,
        }
        info["new_cards_len"] = len(new_cards)
        info["status"] = "NEEDS_UPDATE"
        return True, payload, info

    # If no 'set' entries in coins: check if already patched
    if len(coins) == EXPECTED_COIN_COUNT and coin_count == EXPECTED_COIN_COUNT and len(cards) > 0:
        info["status"] = "ALREADY_PATCHED"
        return False, None, info

    # If coins count is 20 but coin_count field differs
    if len(coins) == EXPECTED_COIN_COUNT and coin_count != EXPECTED_COIN_COUNT:
        payload = {"coin_count": EXPECTED_COIN_COUNT}
        info["status"] = "NEEDS_COIN_COUNT_UPDATE"
        return True, payload, info

    info["status"] = "NO_CHANGE_NEEDED"
    return False, None, info


def inspect_fix2(db: firestore.Client) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Inspects users/eric.seaman@yahoo.com/coins/71e2d4ae92bc4312a4198a3a0cc21fcb.
    Returns: (needs_update, update_payload, report_info)
    """
    collection_path = f"users/{FIX2_USER}/coins"
    doc_ref = db.collection("users").document(FIX2_USER).collection("coins").document(FIX2_DOC_ID)
    doc_snap = doc_ref.get()

    info: Dict[str, Any] = {
        "doc_path": f"{collection_path}/{FIX2_DOC_ID}",
        "exists": doc_snap.exists,
        "current_obverse": None,
        "current_reverse": None,
        "current_retailer": None,
        "current_prod_code": None,
        "safety_check_passed": False,
        "status": "UNKNOWN",
        "doc_ref": doc_ref,
    }

    if not doc_snap.exists:
        info["status"] = "NOT_FOUND"
        return False, None, info

    data = doc_snap.to_dict() or {}
    current_obverse = str(data.get("image_url_obverse") or "")
    current_reverse = str(data.get("image_url_reverse") or "")
    current_retailer = str(data.get("Retailer Item No.") or "")
    current_prod_code = str(data.get("product_code") or "")

    info["current_obverse"] = current_obverse
    info["current_reverse"] = current_reverse
    info["current_retailer"] = current_retailer
    info["current_prod_code"] = current_prod_code

    # Safety check: confirm current image_url_obverse contains 'marine-corps'
    has_marine_corps = SAFETY_URL_FRAGMENT.lower() in current_obverse.lower()
    info["safety_check_passed"] = has_marine_corps

    if has_marine_corps:
        info["status"] = "NEEDS_UPDATE"
        payload = {
            "image_url_obverse": OBVERSE_REPLACEMENT_URL,
            "image_url_reverse": REVERSE_REPLACEMENT_URL,
            "Retailer Item No.": RETAILER_ITEM_NO,
            "product_code": PRODUCT_CODE,
        }
        return True, payload, info

    # Check if already patched
    if (
        current_obverse == OBVERSE_REPLACEMENT_URL
        and current_reverse == REVERSE_REPLACEMENT_URL
        and current_retailer == RETAILER_ITEM_NO
        and current_prod_code == PRODUCT_CODE
    ):
        info["status"] = "ALREADY_PATCHED"
        return False, None, info

    # Current URL doesn't have marine-corps and doesn't match target URL
    info["status"] = "SAFETY_REFUSAL"
    return False, None, info


def run_fixes(execute: bool = False) -> int:
    """
    Executes inspection and remediation for Fix 1 and Fix 2.
    Returns: 0 for success, non-zero on error.
    """
    mode_str = "EXECUTE" if execute else "DRY-RUN"
    print("=" * 80)
    print(f"Numista.AI - Fix 26RJ Phase 2 Remediation ({mode_str} MODE)")
    print(f"Firestore Project: {PROJECT_ID}")
    print(f"Timestamp (UTC):   {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    try:
        db = get_firestore_client(PROJECT_ID)
    except Exception as e:
        print(f"[FATAL] Could not initialize Firestore client: {e}")
        return 1

    # ─────────────────────────────────────────────────────────────────────────
    # FIX 1 INSPECTION
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "-" * 80)
    print("FIX 1: Patch `coin_set_index/uncirculated-coin-set-2026`")
    print("-" * 80)

    fix1_needs_update, fix1_payload, fix1_info = inspect_fix1(db)

    print(f"Document Path:       {fix1_info['doc_path']}")
    print(f"Document Exists:     {fix1_info['exists']}")
    if not fix1_info["exists"]:
        print("  [ERROR] Document does not exist in Firestore!")
    else:
        print(f"Current coin_count:  {fix1_info['current_coin_count']}")
        print(f"Current coins count: {fix1_info['current_coins_len']}")
        print(f"Current cards count: {fix1_info['current_cards_len']}")
        print(f"Packaging cards in coins (denomination == 'set'): {fix1_info['set_entries_found']}")
        if fix1_info.get("card_names"):
            for name in fix1_info["card_names"]:
                print(f"  - Card: {name}")

        if fix1_info["status"] == "NEEDS_UPDATE":
            print(f"\n[ACTION REQUIRED] Found {fix1_info['set_entries_found']} packaging card(s) in `coins` array.")
            print("Proposed Mutations (merge=True):")
            print(f"  * Move {fix1_info['set_entries_found']} card(s) into new field `cards` (total cards: {fix1_info.get('new_cards_len', 2)})")
            print(f"  * Remove cards from `coins` array -> {fix1_info['remaining_coins_len']} actual coins remaining")
            print(f"  * Update `coin_count`: {fix1_info['current_coin_count']} -> {EXPECTED_COIN_COUNT}")
        elif fix1_info["status"] == "ALREADY_PATCHED":
            print("\n[VERIFIED] Document is ALREADY PATCHED:")
            print(f"  * `coin_count` is {fix1_info['current_coin_count']} (expected: 20)")
            print(f"  * `coins` array has {fix1_info['current_coins_len']} actual coins (0 'set' entries)")
            print(f"  * `cards` field exists with {fix1_info['current_cards_len']} packaging card(s)")
            print("  No further modifications needed.")
        elif fix1_info["status"] == "NEEDS_COIN_COUNT_UPDATE":
            print(f"\n[ACTION REQUIRED] `coins` has 20 coins, but `coin_count` is {fix1_info['current_coin_count']}.")
            print(f"Proposed Mutation: `coin_count` -> {EXPECTED_COIN_COUNT}")
        else:
            print(f"\n[INFO] Status: {fix1_info['status']}. No action required.")

    # ─────────────────────────────────────────────────────────────────────────
    # FIX 2 INSPECTION
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "-" * 80)
    print("FIX 2: Patch Eric's Parent Document (`71e2d4ae92bc4312a4198a3a0cc21fcb`)")
    print("-" * 80)

    fix2_needs_update, fix2_payload, fix2_info = inspect_fix2(db)

    print(f"Document Path:       {fix2_info['doc_path']}")
    print(f"Document Exists:     {fix2_info['exists']}")
    if not fix2_info["exists"]:
        print("  [ERROR] Document does not exist in Firestore!")
    else:
        print(f"Current image_url_obverse: {fix2_info['current_obverse']}")
        print(f"Current image_url_reverse: {fix2_info['current_reverse']}")
        print(f"Current Retailer Item No.: {fix2_info['current_retailer'] or '(None)'}")
        print(f"Current product_code:      {fix2_info['current_prod_code'] or '(None)'}")
        print(f"Safety Check (contains '{SAFETY_URL_FRAGMENT}'): {fix2_info['safety_check_passed']}")

        if fix2_info["status"] == "NEEDS_UPDATE":
            print("\n[SAFETY CHECK PASSED] Current obverse URL contains 'marine-corps'. Eligible for fix.")
            print("Proposed Mutations (merge=True):")
            print(f"  * `image_url_obverse` -> {OBVERSE_REPLACEMENT_URL}")
            print(f"  * `image_url_reverse` -> {REVERSE_REPLACEMENT_URL}")
            print(f"  * `Retailer Item No.` -> {RETAILER_ITEM_NO}")
            print(f"  * `product_code`      -> {PRODUCT_CODE}")
        elif fix2_info["status"] == "ALREADY_PATCHED":
            print("\n[VERIFIED] Document is ALREADY PATCHED:")
            print(f"  * `image_url_obverse` is set to canonical 26RJ packaging (does NOT contain 'marine-corps')")
            print(f"  * `image_url_reverse` is set to canonical 26RJ reverse")
            print(f"  * `Retailer Item No.` is '{fix2_info['current_retailer']}'")
            print(f"  * `product_code` is '{fix2_info['current_prod_code']}'")
            print("  No further modifications needed.")
        elif fix2_info["status"] == "SAFETY_REFUSAL":
            print(
                f"\n[SAFETY REFUSAL] Current obverse URL does not contain '{SAFETY_URL_FRAGMENT}' "
                f"and does not match target URL. Skipping update to avoid accidental overwrite."
            )
        else:
            print(f"\n[INFO] Status: {fix2_info['status']}. No action required.")

    # ─────────────────────────────────────────────────────────────────────────
    # SUMMARY & EXECUTION
    # ─────────────────────────────────────────────────────────────────────────
    updates_to_perform = (1 if fix1_needs_update else 0) + (1 if fix2_needs_update else 0)

    print("\n" + "=" * 80)
    print(f"Plan Summary: {updates_to_perform} document(s) queued for update.")
    print("=" * 80)

    if not execute:
        print("\n[DRY-RUN COMPLETE] No writes were committed to Firestore.")
        print("To commit these changes, re-run with: python fix_26rj_phase2.py --execute")
        return 0

    if updates_to_perform == 0:
        print("\n[INFO] No documents require updates. All targets are already clean or refused by safety gates.")
        return 0

    print(f"\nCommitting {updates_to_perform} update(s) to Firestore with merge=True...")

    # Execute Fix 1
    if fix1_needs_update and fix1_payload:
        try:
            fix1_info["doc_ref"].set(fix1_payload, merge=True)
            print(f"  [SUCCESS] Updated {fix1_info['doc_path']}")
            print(f"            Coins count: {len(fix1_payload.get('coins', []))}, coin_count: {fix1_payload.get('coin_count')}")
            print(f"            Cards count: {len(fix1_payload.get('cards', []))}")
        except Exception as e:
            print(f"  [ERROR] Failed to update Fix 1 document: {e}")
            return 1

    # Execute Fix 2
    if fix2_needs_update and fix2_payload:
        try:
            fix2_info["doc_ref"].set(fix2_payload, merge=True)
            print(f"  [SUCCESS] Updated {fix2_info['doc_path']}")
            print(f"            image_url_obverse: {fix2_payload['image_url_obverse']}")
            print(f"            image_url_reverse: {fix2_payload['image_url_reverse']}")
            print(f"            Retailer Item No.: {fix2_payload['Retailer Item No.']}")
            print(f"            product_code:      {fix2_payload['product_code']}")
        except Exception as e:
            print(f"  [ERROR] Failed to update Fix 2 document: {e}")
            return 1

    print("\n" + "=" * 80)
    print("Execution complete. All requested mutations have been committed.")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Fix 26RJ Phase 2 remediation: Patch coin_set_index packaging cards and Eric's parent document."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--execute",
        action="store_true",
        help="Commit updates to Firestore (merge=True).",
    )
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate changes without writing (default).",
    )

    args = parser.parse_args()
    is_execute = bool(args.execute)
    exit_code = run_fixes(execute=is_execute)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
